"""Tests for the OBR divergence decomposition (#59).

Fixture provenance: tests/fixtures/obr_costings_comparison_20260817.csv
is a verbatim copy of
origin/obr-costings-mode2:results/uk/obr_costings/COMPARISON.csv
(PR #56) taken 2026-08-17, committed so the decomposition arithmetic is
executable before that PR merges.
"""

import json
from pathlib import Path

import pytest

from pipeline.decompose_uk_obr_divergence import (
    ROOT,
    comparison_rows,
    decompose,
    load_registry,
    render_md,
)

FIXTURE = Path(__file__).parent / "fixtures" / "obr_costings_comparison_20260817.csv"
REGISTRY = ROOT / "data" / "uk" / "obr_divergence_axes.json"


@pytest.fixture(scope="module")
def records():
    return decompose(load_registry(REGISTRY), comparison_rows(FIXTURE))


def test_registry_validates():
    reg = load_registry(REGISTRY)
    assert len(reg["measures"]) == 6


def test_registry_rejects_sized_without_provenance(tmp_path):
    reg = json.loads(REGISTRY.read_text())
    comp = reg["measures"]["autumn_budget_2024__employer_nics_package"]["components"][0]
    comp.pop("provenance")
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps(reg))
    with pytest.raises(ValueError, match="no provenance"):
        load_registry(bad)


def test_registry_rejects_unsized_without_recipe(tmp_path):
    reg = json.loads(REGISTRY.read_text())
    for m in reg["measures"].values():
        for c in m["components"]:
            if c["status"] == "unsized":
                c.pop("recipe")
                bad = tmp_path / "bad.json"
                bad.write_text(json.dumps(reg))
                with pytest.raises(ValueError, match="no recipe"):
                    load_registry(bad)
                return
    pytest.fail("no unsized component found")


def test_every_registry_measure_decomposes_per_fixture_fy(records):
    keys = {(r["measure_key"], r["fy"]) for r in records}
    assert ("efo_march_2026__pa_and_hrt_freezes", "2026-27") in keys
    assert ("autumn_budget_2024__employer_nics_package", "2027-28") in keys
    assert len(records) == 12  # 6 measures x 2 FYs in the fixture


def test_arithmetic_identity(records):
    for r in records:
        total = sum(c["value_gbp"] for c in r["sized_components"]) + r["residual_gbp"]
        assert total == pytest.approx(r["gap_gbp"], abs=1e-6), r["measure_key"]
        assert r["gap_gbp"] == pytest.approx(
            r["pe_value_gbp"] - r["obr_value_gbp"], abs=1e-6
        )


def test_partial_decompositions_never_present_as_explained(records):
    for r in records:
        if r["unsized_components"]:
            assert r["decomposition_status"] == "partial"
            assert r["residual_label"] == "residual_plus_unsized"
            assert "explained_share" not in r


def test_employer_nics_sized_components(records):
    r = next(
        r
        for r in records
        if r["measure_key"] == "autumn_budget_2024__employer_nics_package"
        and r["fy"] == "2026-27"
    )
    by_name = {c["name"]: c for c in r["sized_components"]}
    # OBR 8 May 2025 supplementary release, Tables 1.3+1.4 / 1.5
    assert by_name["employment_allowance_missing_construction"]["value_gbp"] == 4.581e9
    assert by_name["behavioural_adjustment"]["value_gbp"] == 0.723e9
    # gap = 16.247bn - 23.610bn; the residual exposes the like-for-like
    # static shortfall the registry's residual recipe attributes
    assert r["gap_gbp"] == pytest.approx(-7.363e9, abs=2e6)
    assert r["residual_gbp"] == pytest.approx(-7.363e9 - 5.304e9, abs=2e6)


def test_hicbc_welfare_head_component_matches_comparison(records):
    r = next(
        r
        for r in records
        if r["measure_key"] == "spring_budget_2024__hicbc_threshold_and_taper"
        and r["fy"] == "2027-28"
    )
    by_name = {c["name"]: c for c in r["sized_components"]}
    assert by_name["welfare_head_missing"]["value_gbp"] == 0.426e9


def test_missing_row_kind_errors():
    reg = load_registry(REGISTRY)
    rows = [
        r
        for r in comparison_rows(FIXTURE)
        if r["measure_key"] != "efo_march_2026__pa_and_hrt_freezes"
    ]
    with pytest.raises(ValueError, match="pa_and_hrt_freezes"):
        decompose(reg, rows)


def test_markdown_renders_all_rows(records):
    md = render_md(records)
    assert "residual_plus_unsized" in md
    assert md.count("| unsized |") == sum(len(r["unsized_components"]) for r in records)
