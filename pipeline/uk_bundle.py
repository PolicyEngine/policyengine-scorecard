"""Offline UK replay bundle selection and receipt identity.

The legacy pin is read without rewriting it. ``load_bundle`` supplies its
historically audited runtime fields; serialization should use ``bundle_document``
when preserving legacy receipts. Development indexes may be selected explicitly
with UK_BUNDLE_INDEX, without adding a development bundle to the production index.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BUNDLE = "populace-uk-2023__pe-uk-2.89.2"
INDEX = Path("data/uk/certified_bundles/index.json")


def _key(key):
    if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_.-]*", key):
        raise ValueError("invalid UK bundle key")
    return key


def bundle_index_path(*, root=ROOT):
    path = Path(os.environ.get("UK_BUNDLE_INDEX", INDEX))
    return path if path.is_absolute() else Path(root) / path


def bundle_pin_path(key=DEFAULT_BUNDLE, *, root=ROOT):
    _key(key)
    path = bundle_index_path(root=root)
    # Older engine-free test roots contain only the historical pin.
    if (
        not path.exists()
        and key == DEFAULT_BUNDLE
        and not os.environ.get("UK_BUNDLE_INDEX")
    ):
        return Path(root) / "data/uk/certified_bundle.json"
    index = json.loads(path.read_text())
    if (
        index.get("schema_version") != 1
        or index.get("default_bundle") != DEFAULT_BUNDLE
    ):
        raise ValueError("invalid UK bundle index")
    try:
        pin = Path(index["bundles"][key])
    except KeyError as error:
        raise ValueError(f"unregistered UK bundle: {key}") from error
    return pin if pin.is_absolute() else Path(root) / pin


def bundle_document(key=DEFAULT_BUNDLE, *, root=ROOT):
    pin = json.loads(bundle_pin_path(key, root=root).read_text())
    if pin.get("bundle_key", key) != key:
        raise ValueError("bundle pin key differs from index")
    return pin


def load_bundle(key=DEFAULT_BUNDLE, *, root=ROOT):
    pin = bundle_document(key, root=root)
    if key == DEFAULT_BUNDLE:
        defaults = {
            "repo_type": "dataset",
            "release_tag": pin["revision"],
            "resolved_hf_commit": "a75a9a831d6b07aaffbd09713f2a1124f5c0f08f",
            "release_manifest_revision": pin["revision"],
            "data_year": 2023,
            "supported_calendar_years": [2023, 2030],
            "compatible_core_packages": [
                {"name": "policyengine-core", "specifier": "==3.27.1"}
            ],
            "managed_loader_version": "5.0.2",
            "requirements_freeze": "docs/uk_replay/requirements.txt",
            "offline_audit": "docs/uk_replay/OFFLINE_BUNDLE_AUDIT.json",
            "data_build_id": pin["revision"],
        }
        # The resolved commit is recorded by the existing offline audit, not
        # inferred from a moving remote branch.
        audit = Path(root) / defaults["offline_audit"]
        if audit.exists():
            document = json.loads(audit.read_text())
            commit = document.get("certified_identity", {}).get("resolved_hf_commit")
            if commit:
                defaults["resolved_hf_commit"] = commit
        for field, value in defaults.items():
            pin.setdefault(field, value)
    required = (
        "repo_type",
        "release_tag",
        "resolved_hf_commit",
        "release_manifest_revision",
        "data_year",
        "supported_calendar_years",
        "compatible_core_packages",
        "managed_loader_version",
        "requirements_freeze",
        "offline_audit",
    )
    missing = [name for name in required if name not in pin]
    if missing:
        raise ValueError(f"bundle pin missing fields: {missing}")
    pin["bundle_key"] = key
    pin.setdefault("resolved_commit", pin["resolved_hf_commit"])
    pin.setdefault("data_build_id", pin["revision"])
    if pin["repo_type"] not in ("model", "dataset"):
        raise ValueError("invalid bundle repo_type")
    bundle_window(pin)
    return pin


def bundle_window(pin_or_key=DEFAULT_BUNDLE, *, root=ROOT):
    pin = (
        load_bundle(pin_or_key, root=root)
        if isinstance(pin_or_key, str)
        else pin_or_key
    )
    years = pin["supported_calendar_years"]
    if len(years) != 2 or any(type(year) is not int for year in years):
        raise ValueError("bundle year window must contain two integer endpoints")
    start, end = years
    if start != pin["data_year"] or start > end:
        raise ValueError("bundle window must begin at its stored data year")
    return start, end


def registry_path(event, key=DEFAULT_BUNDLE, *, root=ROOT):
    _key(event)
    _key(key)
    directory = Path(root) / "data/uk/events"
    if key != DEFAULT_BUNDLE:
        directory /= f"bundles/{key}"
    return directory / f"{event}_measures.json"


def results_root(key=DEFAULT_BUNDLE, *, root=ROOT):
    _key(key)
    directory = Path(root) / "results/uk/events"
    return directory if key == DEFAULT_BUNDLE else directory / "bundles" / key


def event_output_dir(event, key=DEFAULT_BUNDLE, *, root=ROOT):
    _key(event)
    return results_root(key, root=root) / event


def _exact_pin(pin, field, package):
    entries = [entry["specifier"] for entry in pin[field] if entry["name"] == package]
    if len(entries) != 1 or not entries[0].startswith("==") or "*" in entries[0]:
        raise ValueError(f"bundle needs one exact {package} pin")
    return entries[0][2:]


def bundle_identity(key=DEFAULT_BUNDLE, *, root=ROOT):
    pin = load_bundle(key, root=root)
    return {
        "bundle_key": key,
        "bundle_pin_sha256": hashlib.sha256(
            bundle_pin_path(key, root=root).read_bytes()
        ).hexdigest(),
        "certified_dataset_sha256": pin["sha256"],
        "engine_versions": {
            "policyengine": pin["managed_loader_version"],
            "policyengine-uk": _exact_pin(
                pin, "compatible_model_packages", "policyengine-uk"
            ),
            "policyengine-core": _exact_pin(
                pin, "compatible_core_packages", "policyengine-core"
            ),
        },
        "supported_calendar_years": list(bundle_window(pin)),
    }


def validate_bundle_identity(document, key=DEFAULT_BUNDLE, *, root=ROOT):
    identity = bundle_identity(key, root=root)
    for field, expected in identity.items():
        if field not in document:
            if key != DEFAULT_BUNDLE:
                raise ValueError(f"missing bundle identity field: {field}")
        elif (
            field == "certified_dataset_sha256"
            and key == DEFAULT_BUNDLE
            and "bundle_key" not in document
        ):
            continue  # Existing stages separately validate their legacy digest.
        elif document[field] != expected:
            raise ValueError(f"bundle identity mismatch: {field}")
    return identity


def validate_runtime_bundle(document, key=DEFAULT_BUNDLE, *, root=ROOT):
    identity = validate_bundle_identity(document, key, root=root)
    pin = load_bundle(key, root=root)
    expected = {
        "engine_version": identity["engine_versions"]["policyengine-uk"],
        "policyengine_core_version": identity["engine_versions"]["policyengine-core"],
        "policyengine_version": identity["engine_versions"]["policyengine"],
        "data_bundle": pin["data_build_id"],
        "dataset_sha256_before": pin["sha256"],
        "dataset_sha256_after": pin["sha256"],
    }
    for field, value in expected.items():
        if field in document and document[field] != value:
            raise ValueError(f"runtime bundle mismatch: {field}")
    return identity


def validate_bundle_path(path, key=DEFAULT_BUNDLE, *, kind, root=ROOT):
    _key(key)
    canonical = Path(root) / (
        "data/uk/events" if kind == "registry" else "results/uk/events"
    )
    if kind not in ("registry", "results"):
        raise ValueError("invalid bundle path kind")
    try:
        relative = Path(path).resolve().relative_to(canonical.resolve())
    except ValueError:
        return Path(path)  # Explicit development or determinism-check directory.
    parts = relative.parts
    actual = parts[1] if len(parts) > 1 and parts[0] == "bundles" else DEFAULT_BUNDLE
    if actual != key:
        raise ValueError("path belongs to another bundle")
    return Path(path)


def validate_registry_bundle(registry, key=DEFAULT_BUNDLE, *, root=ROOT):
    validate_bundle_identity(registry, key, root=root)
    expected = bundle_document(key, root=root)
    if registry.get("bundle") != expected:
        raise ValueError("registry bundle pin differs from selected bundle")
    start, end = bundle_window(key, root=root)
    if any(not start <= year <= end for year in registry["calendar_years"]):
        raise ValueError("registry year outside bundle window")
    return expected
