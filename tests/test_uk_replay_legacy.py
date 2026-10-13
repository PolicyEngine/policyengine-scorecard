"""The event generalisation must preserve every committed AB2025 output byte."""

import hashlib
import json
from pathlib import Path

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
