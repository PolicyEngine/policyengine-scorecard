"""Qualify a candidate model/data pair by replaying the event corpus on it.

A qualification request (docs/uk_replay/QUALIFICATION_INTERFACE.md) names a
candidate exactly. This module turns it into a candidate replay variant, or a
rejection with a code; runs the supported corpus on it; diffs the run against
a base variant; and seals the namespace with an artifact-bound receipt.

Steps, each a subcommand so the receiver workflow can run them in the right
environment:

* ``plan``: validate the request and print the install commands for its
  exact wheels (control environment; needs rfc8785 and jsonschema).
* ``probe``: inside the candidate environment, after installation, verify
  the installed identity against the request, materialise the dataset and
  read the release bundle, certification and data years.
* ``corpus``: inside the candidate environment, run compute, staging and
  comparison for every event, then premises, diagnostics and the diff.
* ``receipt``: build, validate and seal the receipt; write
  NAMESPACE_MANIFEST.json and REPLAY_RECEIPT.json.

Nothing here decides whether a candidate is good: the receipt reports
integrity and descriptive diff flags; the promotion policy is release
qualification's.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline import uk_replay_variants as variants  # noqa: E402

EVENTS = (
    "autumn_budget_2024",
    "autumn_statement_2023",
    "spring_budget_2024",
    "spring_statement_2025",
    "spring_budget_2023",
)
CORPUS_VERSION = "uk-fiscal-event-replay/1"
REJECTION_CODES = (
    "schema_invalid",
    "artifact_hash_mismatch",
    "release_bundle_mismatch",
    "incompatible_pair",
    "data_access_failed",
    "no_supported_years",
)
MANIFEST_NAME = "NAMESPACE_MANIFEST.json"
POLICYENGINE_GIT = "https://github.com/PolicyEngine/policyengine.py"
# Run in the candidate environment beside the engine, never resolved freely.
RUNTIME_TOOLS = ("pytest", "hypothesis", "rfc8785==0.1.4", "jsonschema")


class Rejected(Exception):
    """The request cannot be qualified; the receipt carries the code."""

    def __init__(self, code: str, detail: str):
        if code not in REJECTION_CODES:
            raise ValueError(f"unknown rejection code {code}")
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, indent=1, sort_keys=True, allow_nan=False) + "\n"
    ).encode()


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


# --- the request ------------------------------------------------------------------


def request_id(request: dict) -> str:
    """Validate against the v1 schema; schema failures are rejections."""
    from pipeline import uk_replay_interface as interface

    try:
        return interface.validate_request(request)
    except Exception as exc:  # noqa: BLE001 - jsonschema's errors, digest errors
        raise Rejected("schema_invalid", str(exc).splitlines()[0]) from exc


def download_plan(request: dict, venv: Path, wheels: Path) -> list[list[str]]:
    """Create the candidate environment and download the pinned wheels,
    without dependencies, for ``verify_wheels`` to check."""
    candidate = request["candidate"]
    python = str(venv / "bin" / "python")
    pinned = [
        f"policyengine-uk=={candidate['policyengine_uk']['version']}",
        f"policyengine-core=={candidate['policyengine_core']['version']}",
    ]
    if "pypi" in candidate["policyengine"]["source"]:
        pinned.append(f"policyengine=={candidate['policyengine']['version']}")
    return [
        ["uv", "venv", "--python", "3.12", str(venv)],
        ["uv", "pip", "install", "--python", python, "pip"],
        [
            python,
            "-m",
            "pip",
            "download",
            "--no-deps",
            "--only-binary",
            ":all:",
            "-d",
            str(wheels),
            *pinned,
        ],
    ]


def requested_versions(request: dict) -> dict[str, str]:
    candidate = request["candidate"]
    return {
        "policyengine": candidate["policyengine"]["version"],
        "policyengine-uk": candidate["policyengine_uk"]["version"],
        "policyengine-core": candidate["policyengine_core"]["version"],
    }


def matching_certified(request: dict, document: dict) -> dict | None:
    """A committed certified variant of exactly this pair, if any: same
    versions, packaged manifest and dataset, and the same wheel digests where
    both record them."""
    candidate = request["candidate"]
    wheels = {
        "policyengine-uk": candidate["policyengine_uk"]["wheel_sha256"],
        "policyengine-core": candidate["policyengine_core"]["wheel_sha256"],
    }
    if "pypi" in candidate["policyengine"]["source"]:
        wheels["policyengine"] = candidate["policyengine"]["source"]["pypi"][
            "wheel_sha256"
        ]
    for record in document["variants"]:
        identity = record["identity"]
        versions = {n: p["version"] for n, p in identity["packages"].items()}
        if (
            record["status"] == "certified"
            and versions == requested_versions(request)
            and identity["packaged_bundle_manifest_sha256"]
            == candidate["policyengine"]["packaged_bundle_manifest_sha256"]
            and identity["dataset"]["sha256"] == candidate["data"]["sha256"]
            and all(
                identity["packages"][name].get("wheel_sha256", digest) == digest
                for name, digest in wheels.items()
            )
        ):
            return record
    return None


def latest_certified(document: dict) -> dict:
    """The newest certified variant: the file is append-only, newest last."""
    return [r for r in document["variants"] if r["status"] == "certified"][-1]


def environment_lines(record: dict, *, root: Path = ROOT) -> list[str]:
    """A variant's exact pins without the three engine packages."""
    pins = variants.requirements_pins(
        (root / record["requirements"]["path"]).read_text()
    )
    return [
        f"{name}=={version}"
        for name, version in sorted(pins.items())
        if name not in variants.PACKAGES
    ]


def install_command(
    request: dict,
    venv: Path,
    wheels: Path,
    *,
    environment: Path | None = None,
    exact: bool = False,
) -> list[str]:
    """Install the verified local wheels, the wrapper from its public commit
    when it is not a PyPI wheel, and the receipt tools. Re-qualifying a
    certified pair installs that pair's exact numerical environment (``-r``);
    a new candidate resolves within the newest certified one (``-c``). The
    installed RECORD digests then bind the installed contents."""
    source = request["candidate"]["policyengine"]["source"]
    command = [
        "uv",
        "pip",
        "install",
        "--python",
        str(venv / "bin" / "python"),
        *sorted(str(path) for path in wheels.glob("*.whl")),
    ]
    if "git" in source:
        command.append(
            f"policyengine @ git+{POLICYENGINE_GIT}@{source['git']['commit']}"
        )
    if environment is not None:
        command += ["-r" if exact else "-c", str(environment)]
    return command + list(RUNTIME_TOOLS)


def prepare(
    request: dict, venv: Path, wheels: Path, *, root: Path = ROOT
) -> dict[str, str]:
    """Build the candidate environment from exactly the requested wheels."""
    wheels.mkdir(parents=True, exist_ok=True)
    for command in download_plan(request, venv, wheels):
        run(command)
    digests = verify_wheels(request, wheels)
    document = variants.load_document(root / "data" / "uk" / "replay_variants.json")
    match = matching_certified(request, document)
    environment = wheels.parent / f"{wheels.name}-environment.txt"
    environment.write_text(
        "\n".join(environment_lines(match or latest_certified(document), root=root))
        + "\n"
    )
    try:
        run(
            install_command(
                request, venv, wheels, environment=environment, exact=bool(match)
            )
        )
    except subprocess.CalledProcessError:
        if match is not None:
            raise
        # The candidate's own requirements conflict with the newest certified
        # environment: resolve freely; the recorded freeze shows what moved.
        run(install_command(request, venv, wheels))
    return digests


def verify_wheels(request: dict, wheels: Path) -> dict[str, str]:
    """Each downloaded wheel's SHA-256 against the request."""
    candidate = request["candidate"]
    expected = {
        "policyengine_uk": candidate["policyengine_uk"],
        "policyengine_core": candidate["policyengine_core"],
    }
    if "pypi" in candidate["policyengine"]["source"]:
        expected["policyengine"] = {
            "version": candidate["policyengine"]["version"],
            "wheel_sha256": candidate["policyengine"]["source"]["pypi"]["wheel_sha256"],
        }
    found = {}
    for path in sorted(wheels.glob("*.whl")):
        name, version = path.name.split("-")[:2]
        found[name.lower()] = (version, variants.sha256_file(path))
    out = {}
    for name, want in expected.items():
        version, digest = found.get(name, (None, None))
        if version != want["version"] or digest != want["wheel_sha256"]:
            raise Rejected(
                "artifact_hash_mismatch",
                f"{name} wheel {version} sha256 {digest} is not the requested "
                f"{want['version']} {want['wheel_sha256']}",
            )
        out[name] = digest
    return out


# --- probing the installed candidate ---------------------------------------------------


def probe(
    request: dict, runtime_root: Path, *, dataset_file: Path | None = None
) -> dict:
    """Run inside the candidate environment. Engine-dependent."""
    import importlib.metadata

    candidate = request["candidate"]
    installed = variants.installed_identity()
    want = {
        "policyengine": candidate["policyengine"]["version"],
        "policyengine-uk": candidate["policyengine_uk"]["version"],
        "policyengine-core": candidate["policyengine_core"]["version"],
    }
    have = {name: row["version"] for name, row in installed["packages"].items()}
    if have != want:
        raise Rejected("artifact_hash_mismatch", f"installed {have}, requested {want}")
    if (
        installed["packaged_bundle_manifest_sha256"]
        != candidate["policyengine"]["packaged_bundle_manifest_sha256"]
    ):
        raise Rejected(
            "artifact_hash_mismatch",
            "installed packaged bundle manifest differs from the request",
        )
    variants.isolate_certification_environment()
    data = candidate["data"]
    dataset_identity = {
        key: data[key]
        for key in ("repo_id", "repo_type", "revision", "path", "sha256", "size_bytes")
    }
    record_stub = {
        "variant_id": "probe",
        "identity": {
            "dataset": dataset_identity,
            "materialization": "policyengine_data_dir",
        },
    }
    try:
        dataset = variants.materialize_dataset(
            record_stub, runtime_root, source=dataset_file
        )
    except variants.VariantError as exc:
        raise Rejected("data_access_failed", str(exc)) from exc
    os.chdir(runtime_root)
    import policyengine as pe

    bundle = dict(pe.uk.uk_latest.release_bundle)
    if bundle != candidate["expected_release_bundle"]:
        differences = sorted(
            key
            for key in set(bundle) | set(candidate["expected_release_bundle"])
            if bundle.get(key) != candidate["expected_release_bundle"].get(key)
        )
        raise Rejected("release_bundle_mismatch", f"fields differ: {differences}")
    certification = pe.uk.uk_latest.data_certification
    certified_for = getattr(certification, "certified_for_model_version", None)
    if certified_for != want["policyengine-uk"]:
        raise Rejected(
            "incompatible_pair",
            f"the packaged certification names policyengine-uk {certified_for}",
        )
    if (
        bundle.get("certified_data_artifact_sha256") != data["sha256"]
        or bundle.get("certified_data_build_id") != data["build_id"]
        or bundle.get("default_dataset_uri") != variants.hf_uri(dataset_identity)
    ):
        raise Rejected(
            "incompatible_pair", "the dataset is not the bundle's certified artifact"
        )
    simulation = pe.uk.managed_microsimulation()
    years = sorted(int(year) for year in simulation.dataset.years)
    del simulation
    return {
        "installed": installed,
        "release_bundle": bundle,
        "certification": {
            "source": (
                f"policyengine.py {want['policyengine']} packaged bundle manifest "
                f"(qualification request; {json.dumps(candidate['policyengine']['source'], sort_keys=True)})"
            ),
            "compatibility_basis": bundle.get("compatibility_basis"),
            "certified_for_model_version": certified_for,
            "data_build_id": bundle.get("certified_data_build_id"),
        },
        "dataset": dataset_identity,
        "dataset_path": str(dataset),
        "data_years": years,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "freeze": subprocess.run(
            ["uv", "pip", "freeze", "--python", sys.executable],
            check=True,
            capture_output=True,
            text=True,
        ).stdout,
        "versions": {name: importlib.metadata.version(name) for name in want},
    }


def candidate_record(
    request: dict, probed: dict, *, root: Path = ROOT, wheel_sha256: dict | None = None
) -> dict:
    """The variant this request runs as.

    A committed variant whose identity the installed environment reproduces
    exactly (packages, manifest, bundle, dataset and every pinned
    distribution) is returned unchanged. Otherwise a candidate record is
    built, with its normalised freeze written as its requirements."""
    installed = probed["installed"]
    document = variants.load_document(root / "data" / "uk" / "replay_variants.json")

    def engine(packages: dict) -> dict:
        return {
            name: {"version": row["version"], "record_sha256": row["record_sha256"]}
            for name, row in packages.items()
        }

    for record in document["variants"]:
        identity = record["identity"]
        pins = variants.requirements_pins(
            (root / record["requirements"]["path"]).read_text()
        )
        if (
            engine(identity["packages"]) == engine(installed["packages"])
            and identity["release_bundle"] == probed["release_bundle"]
            and identity["dataset"] == probed["dataset"]
            and not variants.identity_mismatches(record, installed)
            and not variants.environment_mismatches(pins, installed)
        ):
            return record
    packages = {}
    for name in variants.PACKAGES:
        packages[name] = dict(installed["packages"][name])
        key = name.replace("-", "_")
        if wheel_sha256 and key in wheel_sha256:
            packages[name]["wheel_sha256"] = wheel_sha256[key]
    freeze = variants.normalized_freeze(
        probed["freeze"], {n: p["version"] for n, p in installed["packages"].items()}
    )
    identity = {
        "packages": packages,
        "packaged_bundle_manifest_sha256": installed["packaged_bundle_manifest_sha256"],
        "release_bundle": probed["release_bundle"],
        "dataset": probed["dataset"],
        "materialization": "policyengine_data_dir",
        "python": installed["python"],
        "requirements_sha256": sha256_bytes(freeze.encode()),
    }
    taken = {
        variants.variant_slug(r["identity"]): r["identity_sha256"]
        for r in document["variants"]
    }
    variant_id = variants.variant_id_for(identity, taken)
    requirements = root / "docs" / "uk_replay" / "requirements" / f"{variant_id}.txt"
    if requirements.exists() and requirements.read_text() != freeze:
        raise RuntimeError(f"{requirements} already holds another environment")
    requirements.parent.mkdir(parents=True, exist_ok=True)
    requirements.write_text(freeze)
    years = probed["data_years"]
    record = {
        "variant_id": variant_id,
        "identity_sha256": variants.identity_sha256(identity),
        "identity": identity,
        "status": "candidate" if request["kind"] == "candidate" else "certified",
        "layout": "replay_namespace",
        "result_root": f"{variants.REPLAY_RESULT_ROOT}/{variant_id}",
        "requirements": {
            "path": str(requirements.relative_to(root)),
            "sha256": variants.sha256_file(requirements),
        },
        "data_years": list(range(years[0], years[-1] + 1)),
        "data_years_evidence": {
            "simulation_dataset_years": years,
            "source": "Measured by pipeline/uk_replay_qualify.py probe in the candidate environment.",
        },
        "certification": probed["certification"],
        "executor": ["local"],
        "qualification_request_sha256": request_id(request),
    }
    variants.validate_record(record, root=root)
    registry_years = set()
    for event in EVENTS:
        registry = json.loads(
            (root / f"data/uk/events/{event}_measures.json").read_bytes()
        )
        registry_years |= set(registry["calendar_years"])
    if not variants.supported_years(record, registry_years)[0]:
        raise Rejected("no_supported_years", f"data years {years} meet no event year")
    return record


# --- the corpus ------------------------------------------------------------------------


def run(command: list[str], *, cwd: Path = ROOT) -> None:
    print("+", " ".join(command), flush=True)
    subprocess.run(
        command, check=True, cwd=cwd, env={**os.environ, "PYTHONPATH": str(ROOT)}
    )


def run_corpus(
    record: dict,
    variants_file: Path,
    *,
    workers: int = 2,
    dataset_file: Path | None = None,
    events: tuple[str, ...] = EVENTS,
) -> list[dict]:
    """Compute, stage and compare every event; returns integrity failures."""
    python = sys.executable
    namespace = variants.namespace_root(record)
    failures = []
    for event in events:
        output = namespace / event
        try:
            command = [
                python,
                "-m",
                "pipeline.compute_uk_event",
                "--event",
                event,
                "--variant",
                record["variant_id"],
                "--variants-file",
                str(variants_file),
                "--workers",
                str(workers),
                "--output-dir",
                str(output),
            ]
            if dataset_file is not None:
                command += ["--dataset-file", str(dataset_file)]
            if (output / "RUN_MANIFEST.json").exists() or any(
                output.glob("RUN_PROGRESS_*.json")
            ):
                command.append("--resume")
            run(command)
            run(
                [
                    python,
                    "pipeline/stage_uk_event.py",
                    "--event",
                    event,
                    "--artifact-dir",
                    str(output),
                ]
            )
            run(
                [
                    python,
                    "pipeline/compare_uk_event.py",
                    "--event",
                    event,
                    "--staged",
                    str(output / "STAGED.jsonl"),
                    "--output-dir",
                    str(output),
                ]
            )
        except subprocess.CalledProcessError as exc:
            failures.append(
                {"code": "event_run_failed", "detail": str(exc), "event": event}
            )
    run(
        [
            python,
            "pipeline/compare_uk_event.py",
            "--summary",
            "--events-root",
            str(namespace),
        ]
    )
    engine = record["identity"]["packages"]["policyengine-uk"]["version"]
    run(
        [
            python,
            "-m",
            "pipeline.audit_uk_event_premises",
            "--all",
            "--expect-engine",
            engine,
            "--output",
            str(namespace / "CONSTRUCTION_PREMISES.json"),
        ]
    )
    run(
        [
            python,
            "pipeline/diagnose_uk_event_models.py",
            "--reverify",
            str(ROOT / "results/uk/events/MODEL_DIAGNOSTICS.json"),
            "--expect-engine",
            engine,
            "--output",
            str(namespace / "MODEL_DIAGNOSTICS.json"),
        ]
    )
    support = {}
    for event in events:
        manifest_path = namespace / event / "RUN_MANIFEST.json"
        if manifest_path.exists():
            manifest = json.loads(manifest_path.read_bytes())
            support[event] = {
                "supported_years": manifest["supported_years"],
                "unsupported_years": manifest["unsupported_years"],
            }
    (namespace / "SUPPORT.json").write_bytes(canonical_bytes(support))
    return failures


# --- receipts and sealing ------------------------------------------------------------


def namespace_files(namespace: Path) -> dict[str, str]:
    return {
        str(path.relative_to(namespace)): variants.sha256_file(path)
        for path in sorted(namespace.rglob("*"))
        if path.is_file() and path.name not in (MANIFEST_NAME, variants.RECEIPT_NAME)
    }


def event_results(record: dict, events=EVENTS) -> tuple[dict, list[dict]]:
    namespace = variants.namespace_root(record)
    out, failures = {}, []
    for event in events:
        directory = namespace / event
        try:
            manifest_bytes = (directory / "RUN_MANIFEST.json").read_bytes()
            staging_bytes = (directory / "STAGING_MANIFEST.json").read_bytes()
            provenance_bytes = (directory / "COMPARISON_PROVENANCE.json").read_bytes()
        except FileNotFoundError as exc:
            failures.append(
                {"code": "event_outputs_missing", "detail": str(exc), "event": event}
            )
            continue
        manifest, staging = json.loads(manifest_bytes), json.loads(staging_bytes)
        out[event] = {
            "registry_sha256": manifest["registry_sha256"],
            "supported_years": manifest["supported_years"],
            "unsupported_years": manifest["unsupported_years"],
            "run_manifest_sha256": sha256_bytes(manifest_bytes),
            "staging_manifest_sha256": sha256_bytes(staging_bytes),
            "comparison_provenance_sha256": sha256_bytes(provenance_bytes),
            "artifacts": len(manifest["artifacts"]),
            "full_supported_grid_complete": bool(
                staging.get("full_supported_grid_complete")
            ),
            "inert_measure_years": staging.get("inert_measure_years", []),
        }
    return out, failures


def diff_summary(diff_dir: Path) -> dict:
    payload = (diff_dir / "DIFF.json").read_bytes()
    diff = json.loads(payload)
    return {
        "base_variant_id": diff["base"]["identity"]["variant_id"],
        "diff_sha256": sha256_bytes(payload),
        "flag_counts": diff["flag_counts"],
        "flagged_rows": [
            {
                "event": row["event"],
                "measure_key": row["measure_key"],
                "year": row["year"],
                "level": row["level"],
                "key": row["key"],
                "flags": row["flags"],
                "base_gbp": row["base_gbp"],
                "head_gbp": row["head_gbp"],
            }
            for row in diff["rows"]
            if row["flags"]
        ],
    }


def build_receipt(
    request: dict,
    *,
    record: dict | None,
    rejection: Rejected | None = None,
    failures: list[dict] | None = None,
    diff_dir: Path | None = None,
    results_path: str,
    ref: str = "replay-state",
    runner: str = "local",
) -> dict:
    from pipeline import uk_replay_interface as interface

    try:
        rid = interface.request_id(request)
    except Exception:  # noqa: BLE001 - an unparseable request still gets a receipt
        rid = interface.jcs_sha256(request)
    failures = list(failures or [])
    receipt = {
        "schema": interface.RECEIPT_SCHEMA_ID,
        "request_id": rid,
        "status": "rejected" if rejection else "complete",
        "rejection": {"code": rejection.code, "detail": rejection.detail}
        if rejection
        else None,
        "variant_id": record["variant_id"] if record else None,
        "variant_identity_sha256": record["identity_sha256"] if record else None,
        "execution": None,
        "corpus": None,
        "integrity": {"status": "not_run", "failures": []},
        "diff": None,
        "results": {
            "repository": "PolicyEngine/policyengine-scorecard",
            "ref": ref,
            "path": results_path,
        },
    }
    if record is None and rejection is None:
        # A step failed before the candidate's identity was established.
        receipt["status"] = "failed"
        receipt["integrity"] = {"status": "failed", "failures": failures}
    if record is not None and rejection is None:
        identity = record["identity"]
        receipt["execution"] = {
            "packages": identity["packages"],
            "packaged_bundle_manifest_sha256": identity[
                "packaged_bundle_manifest_sha256"
            ],
            "release_bundle": identity["release_bundle"],
            "dataset_sha256": identity["dataset"]["sha256"],
            "requirements_sha256": record["requirements"]["sha256"],
            "python": platform.python_version(),
            "platform": platform.platform(),
            "runner": runner,
        }
        events, missing = event_results(record)
        failures += missing
        receipt["corpus"] = {"corpus_version": CORPUS_VERSION, "events": events}
        complete = events and all(
            e["full_supported_grid_complete"] for e in events.values()
        )
        receipt["integrity"] = {
            "status": "failed"
            if failures
            else "complete"
            if complete
            else "incomplete",
            "failures": failures,
        }
        if failures:
            receipt["status"] = "failed"
        if diff_dir is not None and (diff_dir / "DIFF.json").exists():
            receipt["diff"] = diff_summary(diff_dir)
    return receipt


def seal(namespace: Path, receipt: dict, *, diff_dir: Path | None = None) -> dict:
    """Bind every namespace file (and the diff) and write the sealed receipt."""
    from pipeline import uk_replay_interface as interface

    manifest = {
        "schema_version": 1,
        "files": namespace_files(namespace),
        "diff_files": {
            str(path.relative_to(diff_dir)): variants.sha256_file(path)
            for path in sorted(diff_dir.rglob("*"))
            if path.is_file()
        }
        if diff_dir is not None and diff_dir.is_dir()
        else {},
    }
    payload = canonical_bytes(manifest)
    (namespace / MANIFEST_NAME).write_bytes(payload)
    receipt = dict(receipt)
    receipt["results"] = {
        **receipt["results"],
        "manifest_sha256": sha256_bytes(payload),
    }
    sealed = interface.seal_receipt(receipt)
    interface.validate(sealed, interface.RECEIPT_SCHEMA_ID)
    (namespace / variants.RECEIPT_NAME).write_bytes(canonical_bytes(sealed))
    return sealed


def verify_sealed(namespace: Path, *, diff_dir: Path | None = None) -> list[str]:
    """Problems with a sealed namespace; empty when every byte matches."""
    from pipeline import uk_replay_interface as interface

    problems = []
    receipt_path = namespace / variants.RECEIPT_NAME
    manifest_path = namespace / MANIFEST_NAME
    if not receipt_path.is_file() or not manifest_path.is_file():
        return [f"{namespace}: not sealed"]
    receipt = json.loads(receipt_path.read_bytes())
    try:
        interface.validate(receipt, interface.RECEIPT_SCHEMA_ID)
    except Exception as exc:  # noqa: BLE001
        problems.append(f"{receipt_path}: {exc}")
    manifest_bytes = manifest_path.read_bytes()
    if receipt.get("results", {}).get("manifest_sha256") != sha256_bytes(
        manifest_bytes
    ):
        problems.append(f"{manifest_path}: digest differs from the receipt")
    manifest = json.loads(manifest_bytes)
    actual = namespace_files(namespace)
    if actual != manifest["files"]:
        changed = sorted(
            set(actual.items()) ^ set(manifest["files"].items()),
            key=lambda item: item[0],
        )
        problems.append(
            f"{namespace}: files differ from the seal: {[c[0] for c in changed][:10]}"
        )
    if diff_dir is not None and manifest.get("diff_files"):
        actual_diff = {
            str(path.relative_to(diff_dir)): variants.sha256_file(path)
            for path in sorted(diff_dir.rglob("*"))
            if path.is_file()
        }
        if actual_diff != manifest["diff_files"]:
            problems.append(f"{diff_dir}: files differ from the seal")
    return problems


# --- one request, end to end ---------------------------------------------------------

PROBE_REJECTED = 3


def fetch_dataset(request: dict) -> Path:
    """Download the requested artifact into the Hugging Face cache with the
    receiver's token; probe later finds it there by digest."""
    from huggingface_hub import hf_hub_download

    data = request["candidate"]["data"]
    token = os.environ.get("HUGGING_FACE_TOKEN") or os.environ.get("HF_TOKEN")
    try:
        path = Path(
            hf_hub_download(
                repo_id=data["repo_id"],
                repo_type=data["repo_type"],
                filename=data["path"],
                revision=data["revision"],
                token=token or None,
            )
        )
    except Exception as exc:  # noqa: BLE001 - authentication, absence, network
        raise Rejected(
            "data_access_failed", f"{type(exc).__name__}: {exc}".splitlines()[0]
        ) from exc
    if (
        path.stat().st_size != data["size_bytes"]
        or variants.sha256_file(path) != data["sha256"]
    ):
        raise Rejected(
            "artifact_hash_mismatch", f"{data['path']} bytes differ from the request"
        )
    return path


def base_namespace(request: dict, record: dict, document: dict) -> Path | None:
    """The namespace to diff against: compare_to, or the newest certified
    variant other than this one whose results are present."""
    wanted = request.get("compare_to", "latest_certified")
    candidates = (
        [r for r in document["variants"] if r["variant_id"] == wanted]
        if wanted != "latest_certified"
        else [
            r
            for r in reversed(document["variants"])
            if r["status"] == "certified" and r["variant_id"] != record["variant_id"]
        ]
    )
    for candidate in candidates:
        root = variants.namespace_root(candidate)
        if any(root.glob("*/COMPARISON.json")):
            return root
    return None


def run_request(request: dict, state_dir: Path, work: Path, *, runner: str) -> dict:
    """Qualify one request and write its receipt and results to the state
    checkout. Every outcome, including a rejection, produces a receipt."""
    import shutil

    from pipeline import uk_replay_interface as interface

    try:
        rid = request_id(request)
    except Rejected:
        rid = interface.jcs_sha256(request)
    destination = state_dir / "requests" / rid
    results_path = f"requests/{rid}/results/"
    work.mkdir(parents=True, exist_ok=True)
    venv, wheels = work / "venv", work / "wheels"
    variants_file = work / "variants.json"
    record = rejection = diff_dir = None
    failures: list[dict] = []
    try:
        request_id(request)
        fetch_dataset(request)
        digests = prepare(request, venv, wheels)
        (work / "wheels.json").write_bytes(canonical_bytes(digests))
        python = str(venv / "bin" / "python")
        (work / "request.json").write_bytes(canonical_bytes(request))
        probe_run = subprocess.run(
            [
                python,
                "-m",
                "pipeline.uk_replay_qualify",
                "probe",
                "--request",
                str(work / "request.json"),
                "--runtime-root",
                str(work / "runtime"),
                "--wheel-digests",
                str(work / "wheels.json"),
                "--variants-file",
                str(variants_file),
                "--rejection-file",
                str(work / "rejection.json"),
            ],
            cwd=ROOT,
            env={**os.environ, "PYTHONPATH": str(ROOT)},
            capture_output=True,
            text=True,
        )
        if probe_run.returncode == PROBE_REJECTED:
            refused = json.loads((work / "rejection.json").read_bytes())
            raise Rejected(refused["code"], refused["detail"])
        if probe_run.returncode != 0:
            raise subprocess.CalledProcessError(
                probe_run.returncode, "probe", probe_run.stdout, probe_run.stderr
            )
        variant_id = probe_run.stdout.strip().splitlines()[-1]
        record = variants.get_variant(variant_id, path=variants_file)
        run(
            [
                python,
                "-m",
                "pipeline.uk_replay_qualify",
                "corpus",
                "--variant",
                variant_id,
                "--variants-file",
                str(variants_file),
                "--failures",
                str(work / "failures.json"),
            ]
        )
        failures = json.loads((work / "failures.json").read_bytes())
        document = variants.load_document(variants_file)
        base = base_namespace(request, record, document)
        if base is not None:
            base_id = (
                json.loads(next(base.glob("*/RUN_MANIFEST.json")).read_bytes()).get(
                    "variant_id"
                )
                or variants.get_variant(path=variants_file)["variant_id"]
            )
            diff_dir = (
                ROOT
                / variants.REPLAY_RESULT_ROOT
                / "diffs"
                / f"{base_id}__{variant_id}"
            )
            run(
                [
                    python,
                    "-m",
                    "pipeline.diff_uk_event_runs",
                    "--base",
                    str(base),
                    "--head",
                    str(variants.namespace_root(record)),
                    "--output-dir",
                    str(diff_dir),
                ]
            )
    except Rejected as exc:
        rejection = exc
    except subprocess.CalledProcessError as exc:
        failures.append(
            {
                "code": "qualification_step_failed",
                "detail": f"{exc.cmd}: exit {exc.returncode}",
            }
        )
    except Exception as exc:  # noqa: BLE001 - a crash must still produce a receipt
        failures.append(
            {
                "code": "unexpected_error",
                "detail": f"{type(exc).__name__}: {exc}".splitlines()[0][:500],
            }
        )
    receipt = build_receipt(
        request,
        record=None if rejection else record,
        rejection=rejection,
        failures=failures,
        diff_dir=diff_dir,
        results_path=results_path,
        runner=runner,
    )
    if record is not None and rejection is None:
        namespace = variants.namespace_root(record)
        sealed = seal(namespace, receipt, diff_dir=diff_dir)
        target = destination / "results"
        shutil.copytree(namespace, target / record["result_root"], dirs_exist_ok=True)
        if diff_dir is not None and diff_dir.is_dir():
            shutil.copytree(
                diff_dir,
                target / diff_dir.relative_to(ROOT),
                dirs_exist_ok=True,
            )
        requirements = ROOT / record["requirements"]["path"]
        (target / record["requirements"]["path"]).parent.mkdir(
            parents=True, exist_ok=True
        )
        shutil.copy2(requirements, target / record["requirements"]["path"])
        (target / "VARIANT.json").write_bytes(canonical_bytes(record))
    else:
        sealed = interface.seal_receipt(receipt)
        interface.validate(sealed, interface.RECEIPT_SCHEMA_ID)
    destination.mkdir(parents=True, exist_ok=True)
    (destination / variants.RECEIPT_NAME).write_bytes(canonical_bytes(sealed))
    return sealed


# --- the command line ------------------------------------------------------------------


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("validate")
    validate.add_argument("--request", type=Path, required=True)
    prep = commands.add_parser("prepare")
    prep.add_argument("--request", type=Path, required=True)
    prep.add_argument("--venv", type=Path, required=True)
    prep.add_argument("--wheels", type=Path, required=True)
    prep.add_argument("--output", type=Path, required=True)
    probe_parser = commands.add_parser("probe")
    probe_parser.add_argument("--request", type=Path, required=True)
    probe_parser.add_argument("--runtime-root", type=Path, required=True)
    probe_parser.add_argument("--dataset-file", type=Path)
    probe_parser.add_argument("--wheel-digests", type=Path)
    probe_parser.add_argument("--variants-file", type=Path, required=True)
    probe_parser.add_argument("--rejection-file", type=Path)
    request_parser = commands.add_parser("run-request")
    request_parser.add_argument("--request", type=Path, required=True)
    request_parser.add_argument("--state-dir", type=Path, required=True)
    request_parser.add_argument("--work", type=Path, required=True)
    request_parser.add_argument(
        "--runner", default=os.environ.get("REPLAY_RUNNER", "local")
    )
    corpus = commands.add_parser("corpus")
    corpus.add_argument("--variant", required=True)
    corpus.add_argument("--variants-file", type=Path, required=True)
    corpus.add_argument("--workers", type=int, choices=(1, 2), default=2)
    corpus.add_argument("--dataset-file", type=Path)
    corpus.add_argument("--failures", type=Path, required=True)
    receipt = commands.add_parser("receipt")
    receipt.add_argument("--request", type=Path, required=True)
    receipt.add_argument("--variant")
    receipt.add_argument("--variants-file", type=Path)
    receipt.add_argument("--rejection")
    receipt.add_argument("--failures", type=Path)
    receipt.add_argument("--diff-dir", type=Path)
    receipt.add_argument("--results-path", required=True)
    receipt.add_argument("--ref", default="replay-state")
    receipt.add_argument("--runner", default=os.environ.get("REPLAY_RUNNER", "local"))
    receipt.add_argument("--output", type=Path)
    check = commands.add_parser("verify-sealed")
    check.add_argument("namespaces", nargs="*", type=Path)
    args = parser.parse_args(argv)

    if args.command == "validate":
        print(request_id(_load(args.request)))
        return 0
    if args.command == "prepare":
        digests = prepare(
            _load(args.request), args.venv.resolve(), args.wheels.resolve()
        )
        args.output.write_bytes(canonical_bytes(digests))
        return 0
    if args.command == "probe":
        request = _load(args.request)
        digests = _load(args.wheel_digests) if args.wheel_digests else None
        try:
            probed = probe(
                request, args.runtime_root.resolve(), dataset_file=args.dataset_file
            )
            os.chdir(ROOT)
            record = candidate_record(request, probed, wheel_sha256=digests)
        except Rejected as exc:
            if args.rejection_file is None:
                raise
            args.rejection_file.write_bytes(
                canonical_bytes({"code": exc.code, "detail": exc.detail})
            )
            return PROBE_REJECTED
        document = variants.load_document()
        document["variants"] = [
            v for v in document["variants"] if v["variant_id"] != record["variant_id"]
        ] + [record]
        args.variants_file.write_bytes(canonical_bytes(document))
        print(record["variant_id"])
        return 0
    if args.command == "run-request":
        receipt = run_request(
            _load(args.request), args.state_dir, args.work.resolve(), runner=args.runner
        )
        print(f"{receipt['status']} {receipt['receipt_sha256']}")
        return 0
    if args.command == "corpus":
        record = variants.get_variant(args.variant, path=args.variants_file.resolve())
        failures = run_corpus(
            record,
            args.variants_file.resolve(),
            workers=args.workers,
            dataset_file=args.dataset_file,
        )
        args.failures.write_bytes(canonical_bytes(failures))
        return 0
    if args.command == "receipt":
        request = _load(args.request)
        record = (
            variants.get_variant(args.variant, path=args.variants_file.resolve())
            if args.variant
            else None
        )
        rejection = None
        if args.rejection:
            code, _, detail = args.rejection.partition(":")
            rejection = Rejected(code.strip(), detail.strip() or code.strip())
        failures = (
            _load(args.failures) if args.failures and args.failures.exists() else []
        )
        built = build_receipt(
            request,
            record=record,
            rejection=rejection,
            failures=failures,
            diff_dir=args.diff_dir,
            results_path=args.results_path,
            ref=args.ref,
            runner=args.runner,
        )
        if record is not None and rejection is None:
            sealed = seal(
                variants.namespace_root(record), built, diff_dir=args.diff_dir
            )
        else:
            from pipeline import uk_replay_interface as interface

            sealed = interface.seal_receipt(built)
            interface.validate(sealed, interface.RECEIPT_SCHEMA_ID)
            if args.output:
                args.output.write_bytes(canonical_bytes(sealed))
        print(sealed["receipt_sha256"])
        return 0
    if args.command == "verify-sealed":
        namespaces = args.namespaces or sorted(
            path.parent
            for path in (ROOT / variants.REPLAY_RESULT_ROOT).glob(
                f"*/{variants.RECEIPT_NAME}"
            )
        )
        problems = []
        for namespace in namespaces:
            receipt = json.loads((namespace / variants.RECEIPT_NAME).read_bytes())
            diff = None
            if receipt.get("diff"):
                diff = (
                    ROOT
                    / variants.REPLAY_RESULT_ROOT
                    / "diffs"
                    / f"{receipt['diff']['base_variant_id']}__{receipt['variant_id']}"
                )
            problems += verify_sealed(namespace, diff_dir=diff)
        for problem in problems:
            print(problem)
        print(f"{len(namespaces)} sealed namespace(s) checked")
        return 1 if problems else 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
