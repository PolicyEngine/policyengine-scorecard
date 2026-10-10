"""Register the installed loader's certified UK bundle from cached bytes only.

No package constraint is relaxed and no Hugging Face request is made. An
installed loader's packaged bundle manifest supplies the recertified model/core
pins. A cached producer manifest supplies artifact size when the packaged
manifest omits it. Development registration requires an explicit development
index and never changes the production index.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import re
from pathlib import Path

from pipeline.uk_bundle import DEFAULT_BUNDLE, INDEX, ROOT, _key


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _stored_year(path):
    import h5py

    with h5py.File(path, "r") as data:
        values = data["time_period/table"][()]["values"]
    years = {
        int(value.decode() if isinstance(value, bytes) else value) for value in values
    }
    if len(years) != 1:
        raise ValueError("certified artifact must store exactly one data year")
    return years.pop()


def _extension_end(path):
    # Inspect code rather than importing a simulation or inferring support from
    # a parameter lookup.
    source = Path(path).read_text()
    match = re.search(
        r"def extend_single_year_dataset\([^)]*end_year:\s*int\s*=\s*(\d+)",
        source,
        re.DOTALL,
    )
    if not match:
        raise ValueError("cannot verify the installed dataset extension end")
    return int(match.group(1))


def inspect_installed_bundle(
    key, *, requirements_freeze, offline_audit, cache_root=None, development=False
):
    _key(key)
    distribution = importlib.metadata.distribution("policyengine")
    manifest_path = Path(
        distribution.locate_file("policyengine/data/bundle/manifest.json")
    )
    manifest = json.loads(manifest_path.read_text())
    country = manifest["data_releases"]["uk"]
    certification = country["certification"]
    basis = certification.get("compatibility_basis", "")
    if not basis or "unverified" in basis.lower():
        raise ValueError("packaged UK bundle lacks a verified compatibility claim")
    build_id = country.get("build_id")
    if not build_id or certification.get("data_build_id") != build_id:
        raise ValueError("packaged certification data build identity differs")
    versions = {}
    for name in ("policyengine", "policyengine-uk", "policyengine-core"):
        declared = manifest["packages"][name]["version"]
        installed = importlib.metadata.version(name)
        if installed != declared:
            raise ValueError(
                f"installed {name} {installed} differs from packaged pin {declared}"
            )
        versions[name] = installed
    if (
        country["model_package"]["version"] != versions["policyengine-uk"]
        or certification["certified_for_model_version"] != versions["policyengine-uk"]
    ):
        raise ValueError("packaged UK model certification differs from installed model")
    if country["policyengine_version"] != versions["policyengine"]:
        raise ValueError("packaged UK managed loader version differs")
    dataset_name = country["default_dataset"]
    declaration = country["datasets"][dataset_name]
    certified = country["certified_data_artifact"]
    if certified.get("build_id") != build_id:
        raise ValueError("packaged artifact data build identity differs")
    if (
        declaration["sha256"] != certified["sha256"]
        or certified["dataset"] != dataset_name
    ):
        raise ValueError("packaged artifact declarations disagree")
    package = country["data_package"]
    repo_type = declaration.get("repo_type", package["repo_type"])
    if repo_type not in ("model", "dataset"):
        raise ValueError("packaged artifact repo_type is invalid")
    repo_id = declaration.get("repo_id", package["repo_id"])
    release_tag = declaration["revision"]
    uri = f"hf://{repo_id}/{declaration['path']}@{release_tag}"
    if certified.get("uri") != uri or country.get("default_dataset_uri") != uri:
        raise ValueError(
            "packaged certified/default dataset URI differs from artifact identity"
        )
    cache = Path(
        cache_root
        or os.environ.get("HF_HUB_CACHE", Path.home() / ".cache/huggingface/hub")
    )
    repo = (
        cache
        / f"{'models' if repo_type == 'model' else 'datasets'}--{repo_id.replace('/', '--')}"
    )
    ref = repo / "refs" / release_tag
    commit = ref.read_text().strip() if ref.exists() else release_tag
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("cached release tag does not resolve to a commit")
    artifact = repo / "snapshots" / commit / declaration["path"]
    if not artifact.is_file():
        raise ValueError(
            "certified artifact is not cached; registration never downloads"
        )
    digest = sha256_file(artifact)
    size = artifact.stat().st_size
    if digest != declaration["sha256"]:
        raise ValueError("cached artifact digest differs from packaged manifest")
    # Older packaged manifests do not carry size. Only use a cached matching
    # producer declaration, not an unrelated moving root release manifest.
    release_paths = [
        repo
        / "snapshots"
        / package["release_manifest_revision"]
        / package["release_manifest_path"],
        repo / "snapshots" / commit / package["release_manifest_path"],
        repo / "snapshots" / commit / "release_manifest.json",
    ]
    producer_manifest = None
    producer_path = None
    for path in release_paths:
        if not path.is_file():
            continue
        candidate = json.loads(path.read_text())
        candidate_artifact = candidate.get("artifacts", {}).get(dataset_name, {})
        if candidate_artifact.get("sha256") == digest:
            producer_manifest, producer_path = candidate, path
            break
    declared_size = declaration.get("size_bytes", certified.get("size_bytes"))
    if declared_size is None and producer_manifest is not None:
        declared_size = producer_manifest["artifacts"][dataset_name].get("size_bytes")
    if declared_size is None or size != declared_size:
        raise ValueError("cached artifact size absent from or differs from manifest")
    for value in (declaration.get("size_bytes"), certified.get("size_bytes")):
        if value is not None and value != size:
            raise ValueError("packaged artifact size declarations disagree")
    model_distribution = importlib.metadata.distribution("policyengine-uk")
    extension_path = Path(
        model_distribution.locate_file("policyengine_uk/data/economic_assumptions.py")
    )
    start, end = _stored_year(artifact), _extension_end(extension_path)
    if start > end:
        raise ValueError("stored data year exceeds engine extension window")
    return {
        "schema_version": 2,
        "bundle_key": key,
        "registry_rule": "Offline byte-exact certified UK replay identity; the installed managed loader's packaged manifest certifies the exact model/core environment.",
        "repo_id": repo_id,
        "repo_type": repo_type,
        "revision": release_tag,
        "release_tag": release_tag,
        "resolved_hf_commit": commit,
        "resolved_commit": commit,
        "release_manifest_revision": package["release_manifest_revision"],
        "release_manifest_path": package["release_manifest_path"],
        "cached_artifact_manifest_revision": producer_path.relative_to(
            repo / "snapshots"
        ).parts[0]
        if producer_path
        else None,
        "artifact": declaration["path"],
        "sha256": digest,
        "size_bytes": size,
        "data_build_id": country["build_id"],
        "data_year": start,
        "supported_calendar_years": [start, end],
        "compatible_model_packages": [
            {"name": "policyengine-uk", "specifier": f"=={versions['policyengine-uk']}"}
        ],
        "compatible_core_packages": [
            {
                "name": "policyengine-core",
                "specifier": f"=={versions['policyengine-core']}",
            }
        ],
        "managed_loader_version": versions["policyengine"],
        "requirements_freeze": str(requirements_freeze),
        "offline_audit": str(offline_audit),
        "certification": certification,
        "producer_declared_model_packages": producer_manifest.get(
            "compatible_model_packages", []
        )
        if producer_manifest
        else [],
        "producer_declared_core_packages": producer_manifest.get(
            "compatible_core_packages", []
        )
        if producer_manifest
        else [],
        "development_bundle": bool(development),
        "provenance": "Read from the installed release's packaged policyengine/data/bundle/manifest.json; independently verified the already-cached HF artifact, its producer-declared size, stored data year and installed engine extension function. No network request or simulation.",
        "provenance_hashes": {
            "packaged_bundle_manifest_sha256": sha256_file(manifest_path),
            "cached_artifact_manifest_sha256": sha256_file(producer_path)
            if producer_path
            else None,
            "engine_extension_source_sha256": sha256_file(extension_path),
        },
        "compatibility_authority": "Packaged loader certification and packages pins; producer build pins describe the original build, not this recertified environment.",
        "why_this_bundle": "Development adapter checks only; never event results."
        if development
        else "Registered separately so older certified results remain available for descriptive comparison.",
        "engine_constraint_note": "Exact model and core constraints come from this installed managed-loader release. Computing at other engine versions requires another certified bundle registration; see #126.",
    }


def write_registration(pin, pin_path, index_path, *, root=ROOT):
    pin_path, index_path = Path(pin_path), Path(index_path)
    if pin["bundle_key"] == DEFAULT_BUNDLE:
        raise ValueError("the historical default pin must not be replaced")
    if (
        pin.get("development_bundle")
        and index_path.resolve() == (Path(root) / INDEX).resolve()
    ):
        raise ValueError("development bundles cannot enter the production index")
    if pin.get("development_bundle"):
        try:
            development_path = pin_path.resolve().relative_to(Path(root).resolve())
        except ValueError:
            development_path = None
        if development_path is not None and development_path.parts[0] == "data":
            raise ValueError(
                "development pins belong in ignored paths or test fixtures"
            )
    index = (
        json.loads(index_path.read_text())
        if index_path.exists()
        else {
            "schema_version": 1,
            "default_bundle": DEFAULT_BUNDLE,
            "bundles": {DEFAULT_BUNDLE: "data/uk/certified_bundle.json"},
        }
    )
    if index.get("default_bundle") != DEFAULT_BUNDLE:
        raise ValueError("registration must preserve the historical default")
    try:
        relative = str(pin_path.resolve().relative_to(Path(root).resolve()))
    except ValueError:
        relative = str(pin_path.resolve())
    existing_path = index["bundles"].get(pin["bundle_key"])
    if existing_path is not None and existing_path != relative:
        raise ValueError("bundle key is already registered to another pin")
    index["bundles"][pin["bundle_key"]] = relative
    pin_bytes = (
        json.dumps(pin, indent=1, sort_keys=True, allow_nan=False) + "\n"
    ).encode()
    if pin_path.exists() and pin_path.read_bytes() != pin_bytes:
        raise ValueError("refusing to replace an existing bundle pin")
    pin_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.parent.mkdir(parents=True, exist_ok=True)
    pin_path.write_bytes(pin_bytes)
    index_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--key", required=True)
    parser.add_argument("--requirements-freeze", required=True)
    parser.add_argument("--offline-audit", required=True)
    parser.add_argument("--pin", type=Path)
    parser.add_argument("--index", type=Path, default=ROOT / INDEX)
    parser.add_argument("--cache-root", type=Path)
    parser.add_argument("--development", action="store_true")
    args = parser.parse_args(argv)
    pin = inspect_installed_bundle(
        args.key,
        requirements_freeze=args.requirements_freeze,
        offline_audit=args.offline_audit,
        cache_root=args.cache_root,
        development=args.development,
    )
    pin_path = args.pin or ROOT / "data/uk/certified_bundles" / f"{args.key}.json"
    write_registration(pin, pin_path, args.index)
    print(
        json.dumps(
            {
                "bundle_key": args.key,
                "pin": str(pin_path),
                "sha256": pin["sha256"],
                "data_year": pin["data_year"],
                "supported_calendar_years": pin["supported_calendar_years"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
