"""The event generalisation must preserve every committed AB2025 output byte."""

import hashlib
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


def test_ab2025_committed_outputs_are_byte_identical_to_before_refactor():
    original = json.loads(
        (ROOT / "tests/fixtures/uk_replay_ab2025_hashes.json").read_text()
    )
    actual = {
        path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
        for path in original
    }
    assert actual == original


def test_ab2025_dry_run_matches_before_refactor(monkeypatch, capsys):
    from pipeline import compute_uk_ab2025

    def unavailable():
        raise ImportError("engine-free legacy construction snapshot")

    monkeypatch.setattr(compute_uk_ab2025, "engine_resolver", unavailable)
    assert compute_uk_ab2025.main(["--dry-run"]) == 0
    assert (
        capsys.readouterr().out
        == (ROOT / "tests/fixtures/uk_replay_ab2025_dry_run.txt").read_text()
    )


LEGACY_EVENTS = (
    "autumn_budget_2024",
    "autumn_statement_2023",
    "spring_budget_2024",
    "spring_statement_2025",
    "spring_budget_2023",
)


@pytest.mark.parametrize("event", LEGACY_EVENTS)
def test_committed_legacy_staging_and_comparison_regenerate_byte_for_byte(
    event, tmp_path
):
    """The variant work must not move a legacy byte: staging and comparison,
    rerun from the committed artifacts, reproduce the committed files."""
    from pipeline import compare_uk_event as compare
    from pipeline import compute_uk_event as compute
    from pipeline import compute_uk_obr_costings as fiscal
    from pipeline import stage_uk_event as stage

    registry_path, artifact_dir = compute.event_paths(event)
    payload = registry_path.read_bytes()
    manifest = json.loads((artifact_dir / "RUN_MANIFEST.json").read_bytes())
    assert "variant_id" not in manifest and "unsupported_years" not in manifest
    rows, tally = stage.stage_event(
        json.loads(payload),
        manifest,
        artifact_dir=artifact_dir,
        registry_sha256=hashlib.sha256(payload).hexdigest(),
    )
    staged = b"".join(
        (json.dumps(row, sort_keys=True, allow_nan=False) + "\n").encode()
        for row in rows
    )
    assert staged == (artifact_dir / "STAGED.jsonl").read_bytes()
    staging_manifest = compute.canonical_bytes(
        {
            **tally,
            "event": event,
            "staged_path": fiscal.relative_to_root(artifact_dir / "STAGED.jsonl"),
            "staged_sha256": hashlib.sha256(staged).hexdigest(),
        }
    )
    assert staging_manifest == (artifact_dir / "STAGING_MANIFEST.json").read_bytes()
    compare.write_comparison(
        event, staged_path=artifact_dir / "STAGED.jsonl", output_dir=tmp_path
    )
    written = sorted(path.name for path in tmp_path.iterdir())
    assert written == [
        "COMPARISON.csv",
        "COMPARISON.json",
        "COMPARISON.md",
        "COMPARISON_PROVENANCE.json",
    ]
    for name in written:
        assert (tmp_path / name).read_bytes() == (artifact_dir / name).read_bytes()


def test_committed_legacy_summary_regenerates_byte_for_byte(monkeypatch):
    from pipeline import compare_uk_event as compare

    written = {}
    monkeypatch.setattr(
        compare, "atomic_write_bytes", lambda path, data: written.update({path: data})
    )
    root = ROOT / "results" / "uk" / "events"
    compare.write_summary(root)
    assert list(written) == [root / "SUMMARY.md"]
    assert written[root / "SUMMARY.md"] == (root / "SUMMARY.md").read_bytes()


def test_legacy_artifacts_and_manifests_carry_no_variant_fields():
    """Every committed legacy artifact, manifest and progress receipt keeps
    its pre-variant shape."""
    root = ROOT / "results" / "uk" / "events"
    checked = 0
    for event in LEGACY_EVENTS:
        for path in sorted((root / event).glob("*.json")):
            if path.name.startswith("COMPARISON"):
                continue
            document = json.loads(path.read_bytes())
            assert isinstance(document, dict)
            leaked = [
                key
                for key in document
                if "variant" in key or "supported" in key or key == "data_years"
            ]
            assert not leaked, (path.name, leaked)
            checked += 1
    assert checked > 100
