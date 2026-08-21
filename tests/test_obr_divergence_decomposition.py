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
    comp = next(
        c
        for c in reg["measures"]["spring_budget_2024__hicbc_threshold_and_taper"][
            "components"
        ]
        if c["status"] == "sized"
    )
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


def test_the_static_vs_pmd_term_is_a_joint_term_not_a_behavioural_one():
    """The Table-1.5-minus-PMD subtraction takes a FULL-MEASURE static
    total from a MAPPED-HEAD post-behavioural subtotal: the two sides
    differ in both scope and basis, so the difference cannot be
    attributed to the behavioural response. It is derived, and its axis
    says joint."""
    reg = load_registry(REGISTRY)
    comps = reg["measures"]["autumn_budget_2024__employer_nics_package"]["components"]
    joint = next(c for c in comps if c["name"] == "static_vs_post_behavioural_joint")
    assert joint["status"] == "derived"
    assert joint["axis"] == "joint_behavioural_and_scope"
    assert "24,333m - 23,610m" in joint["derivation"]
    assert "cannot be attributed to the behavioural response" in joint["derivation"]
    assert not any(c["name"] == "behavioural_adjustment" for c in comps)


def test_employment_allowance_is_derived_because_it_sums_two_cells():
    """It adds Table 1.3 and Table 1.4 — the source prints neither total,
    so `verbatim sized` claimed a quote that does not exist."""
    reg = load_registry(REGISTRY)
    comps = reg["measures"]["autumn_budget_2024__employer_nics_package"]["components"]
    ea = next(
        c for c in comps if c["name"] == "employment_allowance_missing_construction"
    )
    assert ea["status"] == "derived"
    assert "3,353m + " in ea["derivation"].replace("m + 1,228m", "m + ")
    assert ea["values_gbp"]["2026-27"] == 3353000000 + 1228000000


def test_residual_is_not_an_axis():
    """It was both a registry axis and the quantity the pipeline
    computes, so a component could be filed under the name of the thing
    it was meant to explain."""
    from pipeline.decompose_uk_obr_divergence import AXES

    assert "residual" not in AXES
    reg = load_registry(REGISTRY)
    for key, m in reg["measures"].items():
        for c in m["components"]:
            assert c["axis"] != "residual", f"{key}/{c['name']}"


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
            "year": "2026",
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
    """Same-sign component larger than the gap. explained_share must NOT
    be emitted: a "150% explained" gap is a residual of the opposite sign
    wearing an explanation's name. The overshoot stays visible in the
    residual and in an explicit withheld reason."""
    rec = decompose(_one_measure_registry(3e9), _one_row(obr=3e9, pe=5e9))[0]
    assert rec["valued_components"][0]["direction"] == "explains_gap"
    assert rec["residual_gbp"] == pytest.approx(-1e9)
    assert "explained_share" not in rec
    assert "outside [0, 1]" in rec["explained_share_withheld"]


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
    +4,581m (EA construction) + 723m (the static-vs-PMD joint term, now
    correctly named rather than called behavioural) = +5.304bn, BOTH
    masking; residual -12.668bn exceeds the gap; the like-for-like
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
    joint = by_name["static_vs_post_behavioural_joint"]
    assert ea["value_gbp"] == 4.581e9 and ea["direction"] == "masks_gap"
    assert ea["status"] == "derived" and "derivation" in ea
    assert joint["value_gbp"] == 0.723e9 and joint["direction"] == "masks_gap"
    assert joint["status"] == "derived" and "derivation" in joint
    # ...plus the cy_proxies_fy component, which the pipeline now
    # EXECUTES from the adjacent-CY comparison rows rather than leaving
    # as a recipe. Here it is a third MASKING term — small, but it
    # widens the like-for-like disagreement rather than explaining any
    # of the observed gap, which is exactly the kind of thing an
    # unexecuted recipe never tells you.
    cy = by_name["cy_proxies_fy"]
    assert cy["status"] == "computed"
    assert cy["direction"] == "masks_gap"
    assert "EQUAL ACCRUAL" in cy["derivation"]
    valued_sum = sum(c["value_gbp"] for c in r["valued_components"])
    assert r["residual_gbp"] == pytest.approx(r["gap_gbp"] - valued_sum, abs=1.0)
    assert r["residual_exceeds_gap"] is True
    assert r["divergence_understated"] is True
    # The like-for-like gap strips the masking terms: the hand-worked
    # -12.668bn plus the newly executed CY term (~-44m), because that
    # term masks too.
    assert r["like_for_like_gap_gbp"] == pytest.approx(
        -12.668e9 - cy["value_gbp"], abs=2e6
    )
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


# --- the four review blockers ----------------------------------------------


def test_the_focal_cy_recipes_are_executed_not_asserted(records):
    """Blocker 1: every PA/HRT and additional-rate component was unsized,
    the residuals equalled the entire gaps, and no record emitted an
    explained_share — while FY2026-27's CY component was already
    computable from the fixture's own adjacent runs under the PR's own
    3:1 recipe."""
    by_key = {(r["measure_key"], r["fy"]): r for r in records}

    pa = by_key[("efo_march_2026__pa_and_hrt_freezes", "2026-27")]
    cy = next(c for c in pa["valued_components"] if c["name"] == "cy_proxies_fy")
    assert cy["status"] == "computed"
    assert cy["value_gbp"] == pytest.approx(1.443e9, abs=2e6)
    # the residual is no longer the whole gap
    assert abs(pa["residual_gbp"]) < abs(pa["gap_gbp"])

    ar = by_key[("efo_march_2026__additional_rate_threshold_reduction", "2026-27")]
    cy = next(c for c in ar["valued_components"] if c["name"] == "cy_proxies_fy")
    assert cy["value_gbp"] == pytest.approx(23.5e6, abs=0.2e6)
    assert abs(ar["residual_gbp"]) < abs(ar["gap_gbp"])


def test_an_executed_component_states_its_assumption(records):
    for r in records:
        for c in r["valued_components"]:
            if c["status"] == "computed":
                assert "EQUAL ACCRUAL" in c["derivation"]
                assert "END year" in c["derivation"]  # the FY identity convention
                assert "EXECUTED by this pipeline" in c["provenance"]


def test_a_recipe_with_no_adjacent_run_stays_unsized(records):
    """FY2027-28 needs a CY2028 run the fixture does not have. Honest:
    the component stays unsized and says why, rather than inventing an
    extrapolation."""
    r = next(
        r
        for r in records
        if r["measure_key"] == "efo_march_2026__pa_and_hrt_freezes"
        and r["fy"] == "2027-28"
    )
    cy = next(c for c in r["unsized_components"] if c["name"] == "cy_proxies_fy")
    assert "NOT EXECUTED" in cy["recipe"]
    assert "no adjacent CY2028" in cy["recipe"]


def test_a_computed_component_may_not_hard_code_a_value(tmp_path):
    reg = json.loads(REGISTRY.read_text())
    comp = next(
        c
        for c in reg["measures"]["efo_march_2026__pa_and_hrt_freezes"]["components"]
        if c["status"] == "computed"
    )
    comp["values_gbp"] = {"2026-27": 1.0}
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps(reg))
    with pytest.raises(ValueError, match="would let it drift"):
        load_registry(bad)


def test_overlapping_components_withhold_explained_share():
    """Blocker 2: HICBC's welfare_head_missing is a sign-adjusted head
    difference that is the SAME channel as its unsized take-up axis.
    Two terms sharing a channel are not additive."""
    reg = load_registry(REGISTRY)
    comps = reg["measures"]["spring_budget_2024__hicbc_threshold_and_taper"][
        "components"
    ]
    head = next(c for c in comps if c["name"] == "welfare_head_missing")
    assert head["overlaps"] == ["behavioural_adjustment"]

    # both valued -> the overlap is recorded and the share withheld
    synthetic = {
        "measures": {
            "m": {
                "comparison_row_kind": "total",
                "components": [
                    {
                        "name": "a",
                        "axis": "head_scope",
                        "status": "sized",
                        "values_gbp": {"2026-27": 4e8},
                        "provenance": "t",
                        "overlaps": ["b"],
                    },
                    {
                        "name": "b",
                        "axis": "behavioural_adjustment",
                        "status": "sized",
                        "values_gbp": {"2026-27": 4e8},
                        "provenance": "t",
                        "overlaps": ["a"],
                    },
                ],
            }
        }
    }
    rec = decompose(synthetic, _one_row(obr=1e9, pe=1.8e9))[0]
    assert rec["overlapping_components"] == ["a~b", "b~a"]
    assert "explained_share" not in rec


def test_registry_rejects_an_overlap_naming_an_unknown_component(tmp_path):
    reg = json.loads(REGISTRY.read_text())
    reg["measures"]["spring_budget_2024__hicbc_threshold_and_taper"]["components"][0][
        "overlaps"
    ] = ["a_component_that_does_not_exist"]
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps(reg))
    with pytest.raises(ValueError, match="overlaps unknown component"):
        load_registry(bad)


def test_the_employer_nics_axis_no_longer_denies_obrs_pass_through():
    """Blocker 3: the registry claimed OBR has "no comparable
    pass-through", but the October 2024 EFO assumes 60% rising to 76%
    with the indirect effects reported separately — so a PE 1->0
    incidence pair sizes PE's WHOLE wage channel, not a PE-vs-OBR
    wedge."""
    reg = load_registry(REGISTRY)
    comps = reg["measures"]["autumn_budget_2024__employer_nics_package"]["components"]
    inc = next(c for c in comps if c["name"] == "employee_incidence_and_base")
    assert "no comparable first-year wage pass-through" not in inc["recipe"]
    assert "OBR DOES assume employer-NICs pass-through" in inc["recipe"]
    assert "60%" in inc["recipe"] and "76%" in inc["recipe"]
    assert "not a PE-vs-OBR wedge" in inc["recipe"]


def test_the_pa_hrt_baseline_recipe_is_not_redundant_and_names_a_world():
    """It substituted the March-2026 earnings determinants PE 2.89.2
    already uses — differencing a world against itself — and it conflated
    data uprating with threshold indexation. The counterfactual it needs
    is now a REGISTERED world."""
    from scorecard_db.baselines import BASELINES

    reg = load_registry(REGISTRY)
    comps = reg["measures"]["efo_march_2026__pa_and_hrt_freezes"]["components"]
    bv = next(c for c in comps if c["name"] == "baseline_vintage")
    assert "ALREADY uses" in bv["recipe"]
    assert "THRESHOLD indexation" in bv["recipe"]
    registered = {d["policy"] for d, *_ in BASELINES}
    assert "obr_announcement_baseline_efo_march_2026" in registered
    assert "obr_announcement_baseline_efo_march_2026" in bv["recipe"]


def test_the_tool_stands_alone_without_pr_56(tmp_path, capsys):
    """Blocker 4: a clean invocation FileNotFoundError'd on #56's output,
    which does not exist on this branch."""
    from pipeline.decompose_uk_obr_divergence import (
        FIXTURE_COMPARISON,
        LIVE_COMPARISON,
        choose_comparison,
        main,
    )

    assert not LIVE_COMPARISON.exists()  # #56 has not merged
    path, provenance = choose_comparison()
    assert path == FIXTURE_COMPARISON and provenance == "fixture"
    main(["--out", str(tmp_path)])
    out = capsys.readouterr().out
    assert "FROZEN FIXTURE" in out
    assert "snapshot, not live results" in out
    prov = json.loads((tmp_path / "PROVENANCE.json").read_text())
    assert prov["comparison_provenance"] == "fixture"


def test_the_lane_survives_a_fresh_build(tmp_path):
    """Nothing registered in build_db.py, so the artifact vanished on
    every CI rebuild."""
    import sqlite3

    from scorecard_db.db import ScorecardDB
    from scorecard_db.ingest_obr_divergence import LANE_ID, ingest

    db_path = tmp_path / "db.sqlite"
    ScorecardDB(db_path).close()
    ingest(db_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    lane = conn.execute("SELECT * FROM lanes WHERE lane = ?", (LANE_ID,)).fetchone()
    conn.close()
    assert lane is not None

    import inspect

    from scorecard_db import build_db

    assert "ingest_obr_divergence.ingest" in inspect.getsource(build_db)
