"""The pre-publish comparables gate (docs/COMPARABLES.md).

Invariants, each tested below:

- Completeness: every committed sources/analysis-* directory passes the
  validator, and the committed index is exactly what the directories build
  (twice, identically).
- The gate: a compared claim whose gap exceeds the threshold fails unless an
  annotation explains it, for any PolicyEngine and external values; within the
  threshold it passes with no annotation (Hypothesis).
- The gap rule: zero for equal values, invariant to rescaling both values,
  orientation-consistent (an opposite-signed convention equals the same value
  negated), sign-free for magnitudes, monotone in the threshold, and over any
  threshold when a nonzero estimate meets a published zero.
- Harvest rule 1: a printed value parses back to the staged value, in every
  printed form (Hypothesis), and a re-signed or mis-scaled value fails.
- Coverage: a search that skips any listed producer, or calls an applicable
  producer not_applicable, fails; Max's 2026-10-21 producer list is pinned.
- The database: every analysis claim is held out, every compared claim has
  exactly one result whose status the record decides, and every uncompared
  claim says why.
- Differential: the app-v2 record and the index agree on the search they cite.
"""

from __future__ import annotations

import copy
import json
import math
import sqlite3
from pathlib import Path

import pytest
from hypothesis import assume, given, settings, strategies as st

from scorecard_db import comparables as cmp
from scorecard_db import signs

REPO = Path(__file__).resolve().parent.parent
COMMITTED_DB = REPO / "data" / "scorecard.db"
CHILDCARE = cmp.SOURCES / "analysis-uk-childcare-100k-threshold"
PRODUCERS = cmp.load_producers()
POLICY = cmp.load_policy()
THRESHOLD = POLICY["gap_threshold"]

# Max's list of 2026-10-21. Additions are fine; removing one of these fails.
MAX_LIST = {
    "UK": {
        "obr",
        "hm_treasury",
        "ifs",
        "resolution_foundation",
        "centax",
        "centre_for_british_progress",
        "ippr",
        "fabian_society",
        "niesr",
        "ukmod",
        "lse_case",
        "jrf",
        "landman_economics",
        "tax_policy_associates",
        "academic",
    },
    "US": {
        "cbo",
        "jct",
        "tpc",
        "pwbm",
        "budget_lab",
        "tax_foundation",
        "urban",
        "cbpp",
        "itep",
        "state_fiscal_note",
        "academic",
    },
}


# --- a minimal synthetic record ------------------------------------------------

SHA = "a" * 64
COMMIT = "b" * 40
SEARCH_DATE = "2026-10-21"


def synthetic(
    pe_value: float, ext_value: float, *, annotate: bool = False
) -> cmp.AnalysisRecord:
    """One UK analysis, one estimate, one compared claim; every producer
    logged none_found except the one that found the claim."""
    claim_key = "ext_cost_fy2027"
    producers = []
    for p in cmp.required_producers(PRODUCERS, "UK", SEARCH_DATE):
        entry = {
            "producer": p["slug"],
            "result": "none_found",
            "queries": [f"{p['slug']} test query"],
            "checked": [],
            "claims": [],
        }
        if p["slug"] == "ifs":
            entry.update(result="found", claims=[claim_key])
        if not cmp.applies(p, "uk_wide"):
            entry.update(result="not_applicable", queries=[])
        producers.append(entry)
    analysis = {
        "schema": cmp.ANALYSIS_SCHEMA,
        "id": "uk/test-analysis",
        "country": "UK",
        "registry": {"kind": "app", "slug": "test-analysis", "country_id": "uk"},
        "title": "A test analysis",
        "url": "https://policyengine.org/uk/test-analysis",
        "published": None,
        "owner": {"author": "max-ghenis"},
        "scope": "uk_wide",
        "subject": "The cost of a test reform",
        "search_terms": ["test reform cost"],
        "worlds": {
            "test_reform": {
                "policy": "uk_test_reform",
                "description": "A test reform world",
            }
        },
        "pe_estimates": [
            {
                "key": "pe_cost_fy2027",
                "label": "Cost, 2027-28",
                "world": "test_reform",
                "metric": "revenue_change",
                "unit_concept": "gbp",
                "period": 2028,
                "time_basis": "fiscal_year",
                "value": pe_value,
                "value_raw": repr(abs(pe_value)) if pe_value else "0",
                "normalization": "as printed",
                "sign": -1 if pe_value < 0 else 1,
                "sign_basis": "printed as a positive cost; revenue_change is positive = yield",
                "conditions": {"sign_convention": "positive = yield to the Exchequer"},
                "provenance": {
                    "repo": "PolicyEngine/test",
                    "commit": COMMIT,
                    "path": "results.json",
                    "sha256": SHA,
                    "field": "cost",
                    "computed_at": "2026-10-20",
                    "engine": {"policyengine": "6.2.1"},
                    "dataset": "test-dataset",
                },
            }
        ],
    }
    raw = repr(abs(ext_value))
    claim = {
        "key": claim_key,
        "source": "ifs",
        "found_by": "ifs",
        "found_on": SEARCH_DATE,
        "source_model": "ifs_taxben",
        "metric": "revenue_change",
        "unit_concept": "gbp",
        "value": ext_value,
        "value_raw": ("-" if ext_value < 0 else "") + raw,
        "normalization": "as printed",
        "value_kind": "point",
        "period": 2028,
        "time_basis": "fiscal_year",
        "conditions": {"sign_convention": "positive = yield to the Exchequer"},
        "world": "test_reform",
        "reform_hint": "the test reform",
        "attribution": "own",
        "benchmark_class": "different_model",
        "baseline_policy": None,
        "publication": {
            "title": "A test report",
            "url": "https://example.org/report.pdf",
            "date": "2026-10-01",
            "publisher": "IFS",
            "primary_sha256": SHA,
            "locator": "Table 1",
            "access": "direct",
        },
        "source_table": "Table 1",
        "source_column": "Cost",
        "quote": f"Cost {('-' if ext_value < 0 else '') + raw}",
        "parse_confidence": "high",
        "status": "ok",
        "compare_to": {"pe_estimate": "pe_cost_fy2027"},
    }
    annotations = []
    if annotate:
        annotations.append(
            {
                "id": "test-cause",
                "claims": [claim_key],
                "status": "comparable",
                "explains_gap": True,
                "cause": "A documented difference in the test populations explains it.",
                "basis": [
                    {
                        "kind": "issue",
                        "ref": "https://github.com/PolicyEngine/test/issues/1",
                    }
                ],
            }
        )
    return cmp.AnalysisRecord(
        directory=Path("/nonexistent/analysis-uk-test-analysis"),
        analysis=analysis,
        search_log={
            "schema": cmp.SEARCH_SCHEMA,
            "searches": [
                {
                    "date": SEARCH_DATE,
                    "kind": "prepublish",
                    "by": "test",
                    "producers": producers,
                }
            ],
        },
        manifest=[
            {
                "url": "https://example.org/report.pdf",
                "title": "A test report",
                "date": "2026-10-01",
                "publisher": "IFS",
                "sha256": SHA,
                "retrieved": SEARCH_DATE,
                "access": "direct",
            }
        ],
        claims=[claim],
        annotations=annotations,
    )


def errors_of(record) -> list[str]:
    return cmp.validate(record, PRODUCERS, POLICY)


def childcare() -> cmp.AnalysisRecord:
    return cmp.load_analysis(CHILDCARE)


# --- completeness of what is committed ---------------------------------------------


@pytest.mark.parametrize("directory", cmp.analysis_dirs(), ids=lambda d: d.name)
def test_every_committed_record_passes_the_gate(directory):
    assert errors_of(cmp.load_analysis(directory)) == []


def test_committed_index_is_what_the_records_build():
    assert cmp.INDEX_PATH.read_text() == cmp.render_index(cmp.build_index())


def test_index_build_is_deterministic():
    assert cmp.render_index(cmp.build_index()) == cmp.render_index(cmp.build_index())


def test_index_lists_every_record_and_only_records():
    index = json.loads(cmp.INDEX_PATH.read_text())
    assert sorted(index["analyses"]) == [d.name for d in cmp.analysis_dirs()]
    assert index["gap_threshold"] == THRESHOLD


def test_max_producer_list_is_kept():
    for country, required in MAX_LIST.items():
        listed = {p["slug"] for p in PRODUCERS["countries"][country]}
        assert required <= listed, required - listed


def test_every_producer_is_complete():
    for country, producers in PRODUCERS["countries"].items():
        for p in producers:
            assert (
                p["name"] and p["kind"] and p["search_hints"] and p["where_to_look"]
            ), p["slug"]
            if p["slug"] not in MAX_LIST[country] and p["slug"] != "open_search":
                assert p.get("why"), (
                    f"{p['slug']} was added beyond Max's list without a reason"
                )


def test_state_fiscal_note_sources_belong_to_state_fiscal_note():
    assert (
        cmp.producer_for_source(PRODUCERS, "US", "ca_fiscal_note")
        == "state_fiscal_note"
    )
    assert cmp.producer_for_source(PRODUCERS, "UK", "obr_efo") == "obr"
    assert cmp.producer_for_source(PRODUCERS, "UK", "unlisted_tank") is None


# --- the motivating case -------------------------------------------------------------


def test_childcare_gap_fails_the_gate_without_its_explanation():
    record = childcare()
    record.annotations = [
        n for n in record.annotations if n["id"] != "hours-draw-microcosm-1126"
    ]
    errors = errors_of(record)
    unexplained = [e for e in errors if "no annotation explains it" in e]
    assert len(unexplained) == 6
    assert any("centax_static_central_fy2027 is -45.8%" in e for e in unexplained)


def test_childcare_central_gap_is_what_the_published_figures_imply():
    rows = {r["key"]: r for r in cmp.evaluate(childcare(), POLICY)}
    assert rows["centax_static_central_fy2027"]["gap"] == pytest.approx(
        0.434 / 0.80 - 1
    )
    assert rows["centax_static_central_fy2029"]["gap"] == pytest.approx(
        0.505 / 0.98 - 1
    )
    # compared across two worlds, so constructed rather than comparable
    assert rows["centax_static_central_fy2027"]["status"] == "constructed"
    assert rows["centax_net_central_fy2027"]["estimate"] is None
    # net of behaviour: beside the static figure, labelled a concept mismatch
    assert rows["centax_net_central_fy2027"]["nearest"] == "thirty_hours_static_fy2027"
    assert rows["centax_net_central_fy2027"]["status"] == "concept_mismatch"
    assert rows["cbp_net_table2_fy2029"]["nearest"] == "both_schemes_static_fy2029"


# --- the gate as a property -------------------------------------------------------------

money = st.floats(min_value=1e3, max_value=1e12, allow_nan=False, allow_infinity=False)


@settings(max_examples=150, deadline=None)
@given(pe=money, ext=money)
def test_gate_fails_exactly_when_an_unexplained_gap_exceeds_the_threshold(pe, ext):
    pe, ext = float(round(pe)), float(round(ext))
    gap = pe / ext - 1
    assume(abs(abs(gap) - THRESHOLD) > 1e-9)  # stay off the boundary
    errors = errors_of(synthetic(-pe, -ext))
    gate_errors = [e for e in errors if "no annotation explains it" in e]
    assert [e for e in errors if e not in gate_errors] == []
    assert bool(gate_errors) == (abs(gap) > THRESHOLD)


@settings(max_examples=60, deadline=None)
@given(pe=money, ext=money)
def test_an_explained_gap_always_passes(pe, ext):
    assert (
        errors_of(synthetic(-float(round(pe)), -float(round(ext)), annotate=True)) == []
    )


def test_an_annotation_that_does_not_explain_the_gap_fails():
    record = synthetic(-100.0, -300.0, annotate=True)
    record.annotations[0]["explains_gap"] = False
    assert any("explains_gap: true" in e for e in errors_of(record))


# --- the gap rule ----------------------------------------------------------------------

nonzero = st.floats(min_value=-1e12, max_value=1e12, allow_nan=False).filter(
    lambda x: abs(x) > 1e-3
)


@given(x=nonzero)
def test_gap_is_zero_for_equal_values(x):
    assert cmp.relative_gap(x, x, signs.SAME) == 0


@given(pe=nonzero, ext=nonzero, k=st.floats(min_value=1e-3, max_value=1e3))
def test_gap_is_invariant_to_rescaling_both_values(pe, ext, k):
    a = cmp.relative_gap(pe, ext, signs.SAME)
    b = cmp.relative_gap(pe * k, ext * k, signs.SAME)
    assert math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-9)


@given(pe=nonzero, ext=nonzero)
def test_opposite_convention_is_the_value_negated(pe, ext):
    assert cmp.relative_gap(pe, -ext, signs.OPPOSITE) == cmp.relative_gap(
        pe, ext, signs.SAME
    )


@given(pe=nonzero, ext=nonzero)
def test_magnitudes_ignore_sign(pe, ext):
    assert cmp.relative_gap(pe, ext, signs.MAGNITUDE) == cmp.relative_gap(
        abs(pe), abs(ext), signs.SAME
    )


@given(pe=nonzero, ext=nonzero)
def test_opposite_signs_are_always_over_any_threshold_below_one(pe, ext):
    assume((pe > 0) != (ext > 0))
    assert cmp.relative_gap(pe, ext, signs.SAME) < -1
    assert cmp.over_threshold(cmp.relative_gap(pe, ext, signs.SAME), 0.999)


@given(pe=nonzero, ext=nonzero, t1=st.floats(0.01, 5), t2=st.floats(0.01, 5))
def test_over_threshold_is_monotone_in_the_threshold(pe, ext, t1, t2):
    gap = cmp.relative_gap(pe, ext, signs.SAME)
    lo, hi = sorted((t1, t2))
    assert cmp.over_threshold(gap, hi) <= cmp.over_threshold(gap, lo)


def test_a_published_zero():
    assert cmp.relative_gap(0.0, 0.0, signs.SAME) == 0
    assert math.isinf(cmp.relative_gap(5.0, 0.0, signs.SAME))
    assert cmp.over_threshold(cmp.relative_gap(5.0, 0.0, signs.SAME), 100)


def test_no_rule_no_gap():
    assert cmp.relative_gap(1.0, 1.0, signs.UNKNOWN) is None
    assert not cmp.over_threshold(None, 0.25)


# --- harvest rule 1 ------------------------------------------------------------------------

UNITS = {"m": "GBP m x 1e6 -> GBP", "bn": "GBP bn x 1e9 -> GBP", "": "as printed"}


@given(
    cents=st.integers(min_value=0, max_value=10**9),
    prefix=st.sampled_from(["", "£"]),
    unit=st.sampled_from(sorted(UNITS)),
    negative=st.booleans(),
    minus=st.sampled_from(["-", "−"]),
    grouped=st.booleans(),
)
def test_printed_values_parse_back(cents, prefix, unit, negative, minus, grouped):
    number = cents / 100
    digits = f"{number:,.2f}" if grouped else f"{number:.2f}"
    raw = f"{minus if negative else ''}{prefix}{digits}{unit}"
    expected = -number if negative and number else number
    assert cmp.parse_printed(raw) == pytest.approx(expected)
    row = {
        "value": expected * cmp.NORMALIZATIONS[UNITS[unit]],
        "value_raw": raw,
        "normalization": UNITS[unit],
    }
    assert cmp.check_value(row, "t") == []
    row["value"] = row["value"] * 1.01 + 1
    assert cmp.check_value(row, "t") != []


@pytest.mark.parametrize(
    "raw, value",
    [
        ("(0.4)", -0.4),
        ("−£1.2 billion", -1.2),
        ("2.1 per cent", 2.1),
        ("13,360", 13360),
        ("+140m", 140),
    ],
)
def test_printed_forms(raw, value):
    assert cmp.parse_printed(raw) == value


def test_a_printed_range_is_two_claims():
    with pytest.raises(ValueError, match="2 numbers"):
        cmp.parse_printed("£1.2bn to £1.5bn")


def test_a_staged_claim_is_never_re_signed():
    assert cmp.check_value(
        {"value": 1, "value_raw": "1", "normalization": "as printed", "sign": -1}, "t"
    )


def test_an_estimate_may_be_re_signed_with_a_reason():
    row = {
        "value": -434e6,
        "value_raw": "0.434",
        "normalization": "GBP bn x 1e9 -> GBP",
        "sign": -1,
    }
    assert any("sign_basis" in e for e in cmp.check_value(row, "t", signed=True))
    row["sign_basis"] = "printed as a positive cost"
    assert cmp.check_value(row, "t", signed=True) == []


# --- each rule fails a record that breaks it -------------------------------------------------


def mutate(fn):
    record = synthetic(-100.0, -105.0)
    assert errors_of(record) == []
    fn(record)
    return errors_of(record)


def _search(record):
    return record.search_log["searches"][0]["producers"]


def test_a_skipped_producer_fails():
    errors = mutate(lambda r: _search(r).pop(0))
    assert any("producers not searched: ['obr']" in e for e in errors)


def test_an_unlisted_producer_fails():
    errors = mutate(
        lambda r: _search(r).append(
            {
                "producer": "made_up",
                "result": "none_found",
                "queries": ["q"],
                "claims": [],
            }
        )
    )
    assert any("not on the UK list" in e for e in errors)


def test_not_applicable_needs_the_scope_to_exclude_the_producer():
    def f(r):
        _search(r)[0].update(result="not_applicable", queries=[])

    assert any("applies to 'uk_wide'" in e for e in mutate(f))


def test_a_search_with_nothing_run_fails():
    def f(r):
        _search(r)[0].update(queries=[], checked=[])

    assert any("no query run" in e for e in mutate(f))


def test_found_not_staged_says_what_and_where():
    def f(r):
        _search(r)[0].update(result="found_not_staged", note="")

    errors = mutate(f)
    assert any("lists the pages it was seen on" in e for e in errors)
    assert any("says what was found" in e for e in errors)


def test_a_claim_no_search_found_fails():
    def f(r):
        for p in _search(r):
            p.update(claims=[], result="none_found") if p["producer"] == "ifs" else None

    assert any("no search entry lists this claim" in e for e in mutate(f))


def test_a_listed_producer_finds_only_its_own_claims():
    errors = mutate(lambda r: r.claims[0].update(source="resolution_foundation"))
    assert any("is not ifs's" in e for e in errors)


def test_a_value_that_is_not_what_was_printed_fails():
    errors = mutate(lambda r: r.claims[0].update(value=-999.0))
    assert any("is not value_raw" in e for e in errors)


def test_a_quote_without_the_value_fails():
    errors = mutate(lambda r: r.claims[0].update(quote="no number here"))
    assert any("quote does not contain" in e for e in errors)


def test_an_unhashed_primary_fails():
    errors = mutate(
        lambda r: r.claims[0]["publication"].update(primary_sha256="c" * 64)
    )
    assert any("not in manifest.jsonl" in e for e in errors)


def test_a_different_world_needs_a_reason():
    def f(r):
        r.analysis["worlds"]["other"] = {
            "policy": "uk_other",
            "description": "another world here",
        }
        r.claims[0]["world"] = "other"

    assert any("compare across worlds only with" in e for e in mutate(f))


def test_a_different_quantity_is_not_compared():
    errors = mutate(lambda r: r.claims[0].update(period=2029))
    assert any("period 2029 differs" in e for e in errors)


def test_an_unreadable_sign_convention_fails():
    errors = mutate(
        lambda r: r.claims[0]["conditions"].update(
            sign_convention="negative = cost to the Exchequer"
        )
    )
    assert any("does not orient the value" in e for e in errors)


def test_an_uncompared_claim_says_why():
    errors = mutate(lambda r: r.claims[0].update(compare_to=None))
    assert any("pe_missing must say why" in e for e in errors)


def test_a_claim_on_a_published_quantity_cannot_be_waved_off():
    def f(r):
        r.claims[0].update(
            compare_to=None, pe_missing="a different concept, says the stager"
        )

    errors = mutate(f)
    assert any("matches pe_cost_fy2027 on metric, unit, period" in e for e in errors)


def test_a_waved_off_claim_needs_a_cited_mismatch():
    def name_it(r):
        r.claims[0].update(
            compare_to=None,
            pe_missing="the producer's figure is net of behaviour",
            nearest_estimate="pe_cost_fy2027",
        )

    assert any("must say why" in e for e in mutate(name_it))

    def annotate(r):
        name_it(r)
        r.annotations.append(
            {
                "id": "net-vs-static",
                "claims": [r.claims[0]["key"]],
                "status": "concept_mismatch",
                "explains_gap": False,
                "cause": "the producer's figure is net of behavioural responses",
                "basis": [
                    {"kind": "document", "ref": "https://example.org/report.pdf#page=3"}
                ],
            }
        )

    assert mutate(annotate) == []

    def comparable_status(r):
        annotate(r)
        r.annotations[0]["status"] = "comparable"

    assert any("must say why" in e for e in mutate(comparable_status))


def test_nearest_estimate_must_match():
    def f(r):
        r.claims[0].update(
            compare_to=None,
            pe_missing="a different period entirely",
            period=2031,
            nearest_estimate="pe_cost_fy2027",
        )

    assert any("does not match this claim" in e for e in mutate(f))


def test_a_restated_figure_is_not_compared():
    errors = mutate(lambda r: r.claims[0].update(attribution="restated"))
    assert any("only a producer's own estimate is compared" in e for e in errors)


def test_an_unregistered_baseline_fails():
    errors = mutate(
        lambda r: r.claims[0].update(baseline_policy="not_a_registered_world")
    )
    assert any("is not registered" in e for e in errors)


def test_an_administrative_level_belongs_to_a_producer_source():
    def f(r):
        r.claims[0].update(benchmark_class="administrative_fact", world="baseline")

    assert any("calibration material" in e for e in mutate(f))


def test_an_annotation_without_a_basis_fails():
    def f(r):
        r.annotations.append(
            {
                "id": "x",
                "claims": [r.claims[0]["key"]],
                "status": "comparable",
                "explains_gap": True,
                "cause": "a cause long enough to count",
                "basis": [],
            }
        )

    assert any("no fabricated mechanisms" in e for e in mutate(f))


def test_an_issue_basis_is_a_github_issue():
    def f(r):
        r.annotations.append(
            {
                "id": "x",
                "claims": [r.claims[0]["key"]],
                "status": "comparable",
                "explains_gap": True,
                "cause": "a cause long enough to count",
                "basis": [{"kind": "issue", "ref": "https://example.org/ticket/1"}],
            }
        )

    assert any("GitHub issue or pull URL" in e for e in mutate(f))


def test_pending_is_only_for_what_a_reharvest_found():
    def f(r):
        r.annotations.append(
            {
                "id": "x",
                "claims": [r.claims[0]["key"]],
                "status": "pending",
                "explains_gap": False,
                "cause": "found after publication; being explained",
                "basis": [
                    {
                        "kind": "issue",
                        "ref": "https://github.com/PolicyEngine/test/issues/2",
                    }
                ],
                "tracking_issue": "https://github.com/PolicyEngine/test/issues/2",
            }
        )

    assert any("explained before the analysis is recorded" in e for e in mutate(f))


def test_a_reharvest_find_may_wait_on_its_issue():
    record = synthetic(-100.0, -300.0)
    first = copy.deepcopy(record.search_log["searches"][0])
    for p in first["producers"]:
        if p["producer"] == "ifs":
            p.update(result="none_found", claims=[])
    later = record.search_log["searches"][0]
    later.update(date="2026-11-02", kind="reharvest")
    record.search_log["searches"] = [first, later]
    record.claims[0]["found_on"] = "2026-11-02"
    assert any("no annotation explains it" in e for e in errors_of(record))
    record.annotations.append(
        {
            "id": "new-find",
            "claims": [record.claims[0]["key"]],
            "status": "pending",
            "explains_gap": False,
            "cause": "found by the weekly re-harvest; the owner is explaining it",
            "basis": [
                {
                    "kind": "issue",
                    "ref": "https://github.com/PolicyEngine/test/issues/3",
                }
            ],
            "tracking_issue": "https://github.com/PolicyEngine/test/issues/3",
        }
    )
    assert errors_of(record) == []
    entry = cmp.index_entry(record, POLICY)
    assert entry["pending"] == 1
    assert entry["tracking_issues"] == ["https://github.com/PolicyEngine/test/issues/3"]
    report = cmp.report(record, "2026-11-01", POLICY)
    assert report["new_claims"] == ["ext_cost_fy2027"]
    assert report["over_threshold"][0]["tracking_issue"].endswith("/3")


def test_the_first_search_is_never_a_reharvest():
    errors = mutate(lambda r: r.search_log["searches"][0].update(kind="reharvest"))
    assert any("prepublish or backfill" in e for e in errors)


# --- the app-v2 record ------------------------------------------------------------------------


@pytest.mark.parametrize("directory", cmp.analysis_dirs(), ids=lambda d: d.name)
def test_app_record_and_index_cite_the_same_search(directory):
    record = cmp.load_analysis(directory)
    block = cmp.app_record(record)
    entry = json.loads(cmp.INDEX_PATH.read_text())["analyses"][directory.name]
    search = next(s for s in entry["searches"] if s["date"] == block["searchDate"])
    assert block["scorecardSource"] == directory.name
    assert block["producersSearched"] == search["producers_searched"]
    assert block["found"] == search["found"]
    assert block["searchKind"] == search["kind"]
    assert block["searchLog"] == entry["search_log"]


def test_scaffold_lists_every_producer(tmp_path):
    directory = cmp.scaffold("uk", "app", "new-dashboard", SEARCH_DATE, root=tmp_path)
    log = json.loads((directory / "search_log.json").read_text())
    logged = [p["producer"] for p in log["searches"][0]["producers"]]
    assert logged == [
        p["slug"] for p in cmp.required_producers(PRODUCERS, "UK", SEARCH_DATE)
    ]
    assert directory.name == "analysis-uk-new-dashboard"


def test_due_lists_recent_estimates_only(tmp_path):
    apps = [
        {
            "slug": "a",
            "countryId": "uk",
            "date": "2026-10-12 12:00:00",
            "displayWithResearch": True,
            "tags": ["uk", "policy"],
        },
        {
            "slug": "old",
            "countryId": "uk",
            "date": "2026-01-01",
            "displayWithResearch": True,
            "tags": ["uk", "policy"],
        },
        {
            "slug": "tool",
            "countryId": "us",
            "date": "2026-10-01",
            "displayWithResearch": True,
            "tags": ["us"],
        },
        {"slug": "unlisted", "countryId": "us", "tags": ["us", "policy"]},
    ]
    posts = [
        {"filename": "Some_Post.md", "date": "2026-10-02", "tags": ["us", "policy"]},
        {
            "filename": "event.md",
            "date": "2026-10-03",
            "tags": ["uk", "event"],
            "comparables": {"status": "no_estimate", "reason": "x"},
        },
    ]
    rows = cmp.due(apps, posts, "2026-10-21", 183, root=tmp_path)
    assert [(r["kind"], r["source"]) for r in rows] == [
        ("post", "analysis-us-some-post"),
        ("app", "analysis-uk-a"),
    ]


# --- the database ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def db():
    if not COMMITTED_DB.exists():
        pytest.skip("scorecard.db not built")
    conn = sqlite3.connect(COMMITTED_DB)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


def _analysis_claims(db):
    return db.execute(
        "SELECT * FROM external_scores WHERE json_extract(publication, '$.registry') = ?",
        ("analysis_comparables",),
    ).fetchall()


def test_every_analysis_claim_is_held_out(db):
    rows = _analysis_claims(db)
    assert rows
    assert {r["calibration_relationship"] for r in rows} == {"held_out"}


def test_db_matches_the_records(db):
    expected = {}
    for directory in cmp.analysis_dirs():
        record = cmp.load_analysis(directory)
        for row in cmp.evaluate(record, POLICY):
            expected[(record.analysis["id"], row["key"])] = row
    rows = _analysis_claims(db)
    seen = set()
    for r in rows:
        cond = json.loads(r["conditions"])
        key = (cond["analysis"], cond["analysis_claim"])
        seen.add(key)
        results = db.execute(
            "SELECT status, computed_value FROM pe_results WHERE claim_id = ?",
            (r["claim_id"],),
        ).fetchall()
        if expected[key]["estimate"]:
            assert len(results) == 1
            want = expected[key]["status"]
            assert results[0]["status"] == ("comparable" if want == "pending" else want)
        elif expected[key]["nearest"]:
            # beside its nearest estimate, labelled with the stated mismatch
            assert len(results) == 1
            assert results[0]["status"] == expected[key]["status"]
            assert results[0]["status"] in cmp.MISMATCH_STATUSES
            assert cond["pe_missing"]
        else:
            assert results == []
            assert cond["pe_missing"]
    staged = {k for k, row in expected.items()}
    assert seen <= staged


def test_childcare_result_is_the_published_figure(db):
    row = db.execute(
        "SELECT r.computed_value, r.run_id, s.value FROM external_scores s JOIN pe_results r"
        " ON r.claim_id = s.claim_id WHERE json_extract(s.conditions, '$.analysis_claim') = ?",
        ("centax_static_central_fy2027",),
    ).fetchone()
    assert row["computed_value"] == -434e6
    assert row["value"] == -800e6
    assert row["run_id"] == "analysis:uk/childcare-100k-threshold@f25f0db"


@pytest.mark.parametrize("directory", cmp.analysis_dirs(), ids=lambda d: d.name)
def test_index_comparisons_are_every_staged_estimate(directory):
    record = cmp.load_analysis(directory)
    entry = json.loads(cmp.INDEX_PATH.read_text())["analyses"][directory.name]
    rows = {r["key"]: r for r in cmp.evaluate(record, POLICY)}
    assert [c["claim"] for c in entry["comparisons"]] == [
        c["key"] for c in record.claims
    ]
    for c in entry["comparisons"]:
        row = rows[c["claim"]]
        assert c["estimate"] == row["estimate"]
        if row["gap"] is not None and not math.isinf(row["gap"]):
            assert c["gap"] == pytest.approx(row["gap"], abs=5e-5)
        assert (c["pe_value"] is None) == (row["estimate"] is None)
        assert c["nearest_estimate"] == row["nearest"]
        assert (c["nearest_pe_value"] is None) == (row["nearest"] is None)
        assert (c["pe_missing"] is None) == (row["estimate"] is not None)
        if row["over"]:
            assert c["cause"], f"{c['claim']} is over the threshold with no cause"


# --- promotion: a fresh search before a push ----------------------------------------

WINDOW = POLICY["promotion_window_days"]


def _entry(search_dates, pending=()):
    return {
        "searches": [{"date": d, "kind": "reharvest"} for d in search_dates],
        "comparisons": [
            {"claim": f"c{i}", "status": "pending", "found_on": found}
            for i, found in enumerate(pending)
        ],
    }


days_st = st.integers(min_value=-400, max_value=400)


def _shift(days):
    import datetime as dt

    return (dt.date(2026, 11, 2) + dt.timedelta(days=days)).isoformat()


@given(offsets=st.lists(days_st, min_size=1, max_size=6), window=st.integers(1, 60))
def test_fresh_exactly_when_a_search_falls_in_the_window(offsets, window):
    on = _shift(0)
    dates = sorted(_shift(o) for o in offsets)
    in_window = any(-window <= o <= 0 for o in offsets)
    assert (cmp.fresh(_entry(dates), on, window) == []) == in_window


@given(
    offsets=st.lists(days_st, min_size=1, max_size=6),
    w1=st.integers(1, 60),
    w2=st.integers(1, 60),
)
def test_a_wider_window_is_never_stricter(offsets, w1, w2):
    on = _shift(0)
    dates = sorted(_shift(o) for o in offsets)
    narrow, wide = sorted((w1, w2))
    if cmp.fresh(_entry(dates), on, narrow) == []:
        assert cmp.fresh(_entry(dates), on, wide) == []


@given(found=days_st)
def test_a_pending_gap_blocks_a_push_only_once_found(found):
    on = _shift(0)
    reasons = cmp.fresh(_entry([on], pending=[_shift(found)]), on, WINDOW)
    assert bool(reasons) == (found <= 0)


def test_a_search_after_the_push_does_not_count():
    assert cmp.fresh(_entry([_shift(1)]), _shift(0), WINDOW) != []


def test_the_childcare_record_was_fresh_on_its_search_day_only_for_the_window():
    entry = json.loads(cmp.INDEX_PATH.read_text())["analyses"][CHILDCARE.name]
    assert cmp.fresh(entry, "2026-10-21", WINDOW) == []
    assert cmp.fresh(entry, f"2026-10-{21 + WINDOW:02d}", WINDOW) == []
    late = cmp.fresh(entry, f"2026-10-{22 + WINDOW:02d}", WINDOW)
    assert late and "run a prepromotion search" in late[0]


def test_the_index_carries_the_window_and_when_each_claim_was_found():
    index = json.loads(cmp.INDEX_PATH.read_text())
    assert index["promotion_window_days"] == WINDOW
    for entry in index["analyses"].values():
        assert all("found_on" in c for c in entry["comparisons"])


def test_a_prepromotion_search_is_never_the_first():
    errors = mutate(lambda r: r.search_log["searches"][0].update(kind="prepromotion"))
    assert any("prepublish or backfill" in e for e in errors)


def test_a_prepromotion_find_may_wait_on_its_issue_but_blocks_the_push():
    record = synthetic(-100.0, -300.0)
    first = copy.deepcopy(record.search_log["searches"][0])
    for p in first["producers"]:
        if p["producer"] == "ifs":
            p.update(result="none_found", claims=[])
    later = record.search_log["searches"][0]
    later.update(date="2026-11-02", kind="prepromotion")
    record.search_log["searches"] = [first, later]
    record.claims[0]["found_on"] = "2026-11-02"
    record.annotations.append(
        {
            "id": "found-before-a-push",
            "claims": [record.claims[0]["key"]],
            "status": "pending",
            "explains_gap": False,
            "cause": "found by the search before the newsletter; the owner is explaining it",
            "basis": [
                {
                    "kind": "issue",
                    "ref": "https://github.com/PolicyEngine/test/issues/4",
                }
            ],
            "tracking_issue": "https://github.com/PolicyEngine/test/issues/4",
        }
    )
    assert errors_of(record) == []
    entry = cmp.index_entry(record, POLICY)
    reasons = cmp.fresh(entry, "2026-11-03", WINDOW)
    assert len(reasons) == 1 and "pending" in reasons[0]


def test_the_policy_rejects_a_bad_window(tmp_path):
    bad = dict(POLICY, promotion_window_days=0)
    path = tmp_path / "policy.json"
    path.write_text(json.dumps(bad))
    with pytest.raises(ValueError, match="promotion_window_days"):
        cmp.load_policy(path)
