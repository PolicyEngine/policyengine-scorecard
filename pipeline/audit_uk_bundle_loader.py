"""Hash installed 6.x loader evidence without importing or running the engine."""

from __future__ import annotations

import argparse
import hashlib
import json
from importlib.metadata import distribution, version
from pathlib import Path

from pipeline import uk_bundle

SOURCES = {
    "policyengine": [
        "core/tax_benefit_model_version.py",
        "tax_benefit_models/uk/model.py",
        "tax_benefit_models/common/model_version.py",
        "provenance/manifest.py",
        "provenance/dataset_materialization.py",
    ],
    "policyengine_uk": [
        "simulation.py",
        "data/economic_assumptions.py",
        "data/dataset_schema.py",
        "utils/scenario.py",
        "utils/parameters.py",
        "scenarios/uc_reform.py",
        "parameters/gov/hmrc/cgt/basic_rate.yaml",
        "parameters/gov/hmrc/cgt/higher_rate.yaml",
        "parameters/gov/hmrc/cgt/additional_rate.yaml",
        "parameters/gov/hmrc/fuel_duty/lpg.yaml",
        "parameters/gov/hmrc/fuel_duty/natural_gas.yaml",
        "parameters/gov/hmrc/tobacco_duty/rates/cigarette_specific.yaml",
        "parameters/gov/hmrc/alcohol_duty/rates/beer.yaml",
    ],
}


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def audit(key):
    pin = uk_bundle.load_bundle(key)
    identities = uk_bundle.bundle_identity(key)
    for package, expected in identities["engine_versions"].items():
        if version(package) != expected:
            raise ValueError(f"installed {package} differs from bundle pin")
    site = Path(distribution("policyengine").locate_file(""))
    manifest_path = site / "policyengine/data/bundle/manifest.json"
    packaged = json.loads(manifest_path.read_text())
    release = packaged["data_releases"]["uk"]
    certification = release["certification"]
    if (
        certification["certified_for_model_version"]
        != identities["engine_versions"]["policyengine-uk"]
        or release["certified_data_artifact"]["sha256"] != pin["sha256"]
        or certification["data_build_id"] != pin["data_build_id"]
    ):
        raise ValueError("packaged certification differs from selected bundle")
    sources = {
        f"{package}/{relative}": sha256(site / package / relative)
        for package, files in SOURCES.items()
        for relative in files
    }
    references = {}
    for name in sources:
        lines = (site / name).read_text().splitlines()
        references[name] = [
            {"line": i, "text": line.strip()}
            for i, line in enumerate(lines, 1)
            if any(
                marker in line
                for marker in (
                    "def managed_microsimulation",
                    "def materialize_dataset",
                    "def _reuse_or_download",
                    "def release_bundle",
                    "runtime_dataset_source",
                    "def from_reform",
                    "def convert_to_fiscal",
                    "fiscal_year_blend",
                    "preserve_calendar_dates",
                    "end_year: int",
                    'mode="r"',
                    "def build_from_single",
                    "def build_from_multi",
                    'sim.set_input("uc_LCWRA',
                    "universal_credit_july_2025_reform.simulation_modifier",
                    "not scenario.applied_before",
                    "def get_data_release_manifest",
                    "return bundled_certification",
                )
            )
        ]
    kind = "models" if pin["repo_type"] == "model" else "datasets"
    cache_directory = f"{kind}--{pin['repo_id'].replace('/', '--')}"
    return {
        "schema_version": 2,
        "inspection": "Engine-free installed-source inspection; no provider, credentials, network or simulation.",
        "development_bundle": bool(pin.get("development_bundle")),
        "policyengine_version": pin["managed_loader_version"],
        "certified_identity": {
            **{
                field: pin[field]
                for field in (
                    "repo_id",
                    "repo_type",
                    "revision",
                    "artifact",
                    "sha256",
                    "size_bytes",
                    "data_year",
                    "resolved_hf_commit",
                )
            },
            "model_version": identities["engine_versions"]["policyengine-uk"],
            "core_version": identities["engine_versions"]["policyengine-core"],
            "dataset_uri": release["default_dataset_uri"],
            "data_build_id": pin["data_build_id"],
        },
        "bundled_certification": certification,
        "packaged_bundle_manifest_sha256": sha256(manifest_path),
        "source_files_sha256": sources,
        "source_references": references,
        "release_manifest_revision": pin["release_manifest_revision"],
        "registration_provenance_hashes": pin.get("provenance_hashes", {}),
        "minimal_hf_cache_allowlist": {
            "repo_cache_directory": cache_directory,
            "required_ref": {
                "path": f"refs/{pin['revision']}",
                "contents": pin["resolved_hf_commit"],
            },
            "required_snapshot_file": {
                "path": f"snapshots/{pin['resolved_hf_commit']}/{pin['artifact']}"
            },
            "exclude": [
                "tokens",
                "credentials",
                "refs/main",
                "other revisions",
                "other artifacts",
            ],
        },
        "offline_loader_behavior": {
            "materialization": "Reuse hash-verified ./data/<artifact>; requests downloads bypass HF offline flags on a missing or mismatched file.",
            "release_metadata": "requests.get bypasses HF offline flags; socket blocking forces packaged certification fallback.",
            "fallback": "Must retain packaged certified_for_model_version matching the runtime; unverified fallback is refused.",
            "runtime_dataset_source": "The source.path returned by materialize_dataset is recorded by build_runtime_dataset_provenance and must resolve to the pre/post hashed file.",
            "read_only_h5": "Single-year and multi-year constructors use HDFStore(mode='r'); no writable dataset copy is required.",
            "projection": "managed_microsimulation passes the original stored-year dataset to the engine; no projected year-file re-anchoring.",
        },
        **identities,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    document = audit(args.bundle)
    output = (
        args.output
        or uk_bundle.ROOT / uk_bundle.load_bundle(args.bundle)["offline_audit"]
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n")
    print(f"{output}: {sha256(output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
