"""Tests for the OBR divergence decomposition (#59).

Fixture provenance: tests/fixtures/obr_costings_comparison_20260817.csv
is a verbatim copy of
origin/obr-costings-mode2:results/uk/obr_costings/COMPARISON.csv
(PR #56) taken 2026-08-17, committed so the decomposition arithmetic is
executable before that PR merges.

The identity residual = gap - sum(valued) holds by construction and is
deliberately NOT tested as if it were evidence: the tests here exercise
the diagnostics that can actually fail — direction classification,
masking (divergence-understated) flags, |residual| > |gap|, and the
registry's quoted-vs-derived contract — plus a hand-computed regression
for the employer-NICs row (the case the review worked by hand).
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


# --- registry contract ------------------------------------------------------


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


def test_registry_rejects_sized_with_derivation(tmp_path):
    """A number produced by arithmetic must be status derived, never
    sized: sized means quoted verbatim from the source."""
    reg = json.loads(REGISTRY.read_text())
    comp = reg["measures"]["autumn_budget_2024__employer_nics_package"]["components"][0]
    assert comp["status"] == "sized"
    comp["derivation"] = "a - b"
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps(reg))
    with pytest.raises(ValueError, match="must be 'derived'"):
        load_registry(bad)


def test_registry_rejects_derived_without_derivation(tmp_path):
    reg = json.loads(REGISTRY.read_text())
    comps = reg["measures"]["autumn_budget_2024__employer_nics_package"]["components"]
    derived = next(c for c in comps if c["status"] == "derived")
    derived.pop("derivation")
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps(reg))
    with pytest.raises(ValueError, match="no derivation"):
        load_registry(bad)


def test_behavioural_component_is_derived_not_sized():
    """The Table-1.5-minus-PMD subtraction is arithmetic on quoted
    numbers, so it must carry the derived label and its formula."""
    reg = load_registry(REGISTRY)
    comps = reg["measures"]["autumn_budget_2024__employer_nics_package"]["components"]
    beh = next(c for c in comps if c["name"] == "behavioural_adjustment")
    assert beh["status"] == "derived"
    assert "24,333m - 23,610m" in beh["derivation"]


# --- decomposition records --------------------------------------------------


def test_every_registry_measure_decomposes_per_fixture_fy(records):
    keys = {(r["measure_key"], r["fy"]) for r in records}
    assert ("efo_march_2026__pa_and_hrt_freezes", "2026-27") in keys
    assert ("autumn_budget_2024__employer_nics_package", "2027-28") in keys
    assert len(records) == 12  # 6 measures x 2 FYs in the fixture


def test_partial_decompositions_never_present_as_explained(records):
    for r in records:
        if r["unsized_components"]:
            assert r["decomposition_status"] == "partial"
            assert r["residual_label"] == "residual_plus_unsized"
            assert "explained_share" not in r


def test_masking_components_never_yield_explained_share(records):
    for r in records:
        if r["divergence_understated"]:
            assert "explained_share" not in r
            assert "like_for_like_gap_gbp" in r


# --- direction / masking diagnostics (synthetic, can fail) ------------------


def _one_measure_registry(value_gbp):
    return {
        "measures": {
            "m": {
                "comparison_row_kind": "total",
                "components": [
                    {
                        "name": "c",
                        "axis": "head_scope",
                        "status": "sized",
                        "values_gbp": {"2026-27": value_gbp},
                        "provenance": "test",
                    }
                ],
            }
        }
    }


def _one_row(obr, pe):
    return [
        {
            "measure_key": "m",
            "row_kind": "total",
            "fy": "2026-27",
            "obr_value_gbp": str(obr),
            "pe_value_gbp": str(pe),
        }
    ]


def test_component_opposing_the_gap_is_classified_masking_not_explaining():
    """gap = -2bn, component = +1bn: the axis hides part of a -3bn
    like-for-like disagreement. The old artifact presented this as a
    decomposition step; it must now flag divergence_understated and
    never emit explained_share."""
    rec = decompose(_one_measure_registry(1e9), _one_row(obr=5e9, pe=3e9))[0]
    comp = rec["valued_components"][0]
    assert comp["direction"] == "masks_gap"
    assert rec["divergence_understated"] is True
    assert rec["like_for_like_gap_gbp"] == pytest.approx(-3e9)
    assert rec["residual_gbp"] == pytest.approx(-3e9)
    assert rec["residual_exceeds_gap"] is True
    assert "explained_share" not in rec


def test_component_exceeding_the_gap_never_claims_explained():
    """Same-sign component larger than the gap: residual flips sign and
    exceeds nothing, but explained_share must not exceed sanity — the
    share is emitted (complete, no masking) and reflects overshoot."""
    rec = decompose(_one_measure_registry(3e9), _one_row(obr=3e9, pe=5e9))[0]
    assert rec["valued_components"][0]["direction"] == "explains_gap"
    assert rec["residual_gbp"] == pytest.approx(-1e9)
    assert rec["explained_share"] == pytest.approx(1.5)  # overshoot is visible


def test_same_direction_component_explains(records=None):
    rec = decompose(_one_measure_registry(1e9), _one_row(obr=3e9, pe=5e9))[0]
    assert rec["valued_components"][0]["direction"] == "explains_gap"
    assert rec["divergence_understated"] is False
    assert rec["residual_exceeds_gap"] is False
    assert rec["explained_share"] == pytest.approx(0.5)


def test_residual_exceeding_gap_is_flagged(records):
    flagged = {
        (r["measure_key"], r["fy"]) for r in records if r["residual_exceeds_gap"]
    }
    assert ("autumn_budget_2024__employer_nics_package", "2026-27") in flagged


# --- employer NICs regression: the review's hand-worked row -----------------


def test_employer_nics_row_matches_the_hand_computation(records):
    """Pin the arithmetic DTrim99 worked by hand in the PR #67 review:
    gap = 16,246,687,341 - 23,610,420,262 = -7.364bn; valued components
    +4,581m (EA construction) + 723m (behavioural, derived) = +5.304bn,
    BOTH masking; residual -12.668bn exceeds the gap; the like-for-like
    disagreement is wider than the observed gap and the record says so."""
    r = next(
        r
        for r in records
        if r["measure_key"] == "autumn_budget_2024__employer_nics_package"
        and r["fy"] == "2026-27"
    )
    assert r["gap_gbp"] == pytest.approx(-7.3637e9, abs=2e6)
    by_name = {c["name"]: c for c in r["valued_components"]}
    ea = by_name["employment_allowance_missing_construction"]
    beh = by_name["behavioural_adjustment"]
    assert ea["value_gbp"] == 4.581e9 and ea["direction"] == "masks_gap"
    assert beh["value_gbp"] == 0.723e9 and beh["direction"] == "masks_gap"
    assert beh["status"] == "derived" and "derivation" in beh
    assert r["residual_gbp"] == pytest.approx(-7.3637e9 - 5.304e9, abs=2e6)
    assert r["residual_exceeds_gap"] is True
    assert r["divergence_understated"] is True
    assert r["like_for_like_gap_gbp"] == pytest.approx(-12.668e9, abs=2e6)
    assert "explained_share" not in r
    # the dominant driver has a named component with a sizing recipe
    assert any(
        c["name"] == "employee_incidence_and_base" for c in r["unsized_components"]
    )


def test_hicbc_welfare_head_component_is_masking(records):
    """HICBC 2027-28: gap is negative (PE below OBR on the mapped total)
    while the missing welfare head contributes +426m — masking, so the
    record must carry the widened like-for-like gap, not treat the head
    fix as progress."""
    r = next(
        r
        for r in records
        if r["measure_key"] == "spring_budget_2024__hicbc_threshold_and_taper"
        and r["fy"] == "2027-28"
    )
    comp = next(
        c for c in r["valued_components"] if c["name"] == "welfare_head_missing"
    )
    assert comp["value_gbp"] == 0.426e9
    assert comp["direction"] == "masks_gap"
    assert r["divergence_understated"] is True


# --- plumbing ---------------------------------------------------------------


def test_missing_row_kind_errors():
    reg = load_registry(REGISTRY)
    rows = [
        r
        for r in comparison_rows(FIXTURE)
        if r["measure_key"] != "efo_march_2026__pa_and_hrt_freezes"
    ]
    with pytest.raises(ValueError, match="pa_and_hrt_freezes"):
        decompose(reg, rows)


def test_markdown_states_understatement(records):
    md = render_md(records)
    assert "residual_plus_unsized" in md
    assert "divergence understated; like-for-like gap" in md
    assert "masks_gap" in md
    assert md.count("| unsized |") == sum(len(r["unsized_components"]) for r in records)
