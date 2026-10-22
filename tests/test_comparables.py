"""The comparables gate (docs/COMPARABLES.md).

Invariants, each tested below:

- Completeness: every committed sources/analysis-* directory passes the
  validator, and the committed index is exactly what the directories build
  (twice, identically).
- The gate: a compared claim fails exactly when its gap exceeds the threshold
  or its sign disagrees, unless an annotation explains it, for values of either
  sign and orientation (Hypothesis); an explained gap always passes.
- No evasion: no relabelling of a like-for-like claim (its basis, programme,
  time basis, period, metric, value kind, status or annotation) gets an
  unexplained gap past the gate without the validator saying so.
- Search integrity: a search's kind and date must fit the record (no search
  after today, before the producer list, a later-kind search on its first day,
  or a prepublish search after publication); a pending gap only on what a
  post-publication search found; the latest search compared the results files
  the estimates are read from now.
- The gap rule: zero for equal values, invariant to rescaling both values,
  orientation-consistent, sign-free only for unsigned levels, over every
  allowed threshold when signs disagree, monotone in the threshold, and over
  any threshold when a nonzero estimate meets a published zero. A range is
  over only when the estimate lies outside it by more than the threshold.
- Harvest rule 1: a printed value parses back to the staged value at the
  scale it states, in every printed form (Hypothesis); the quote prints it as
  a whole number with its sign.
- Coverage: a search that skips any listed producer, or calls an applicable
  producer not_applicable, fails; Max's 2026-10-21 producer list is pinned.
- The database: every analysis claim is held out; the claims ingested are
  exactly the records' claims the database can hold; each compared claim, and
  each claim beside its nearest estimate, has the analysis's figure as its
  result with the record's status.
- Differential: the app-v2 block and the index cite the same search; the
  freshness rule agrees with the shared cases newsletters checks too.
"""

from __future__ import annotations

import copy
import datetime as dt
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
FRESH_CASES = REPO / "tests" / "fixtures" / "comparables_fresh_cases.json"
PRODUCERS = cmp.load_producers()
POLICY = cmp.load_policy()
THRESHOLD = POLICY["gap_threshold"]
WINDOW = POLICY["promotion_window_days"]

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


def shift(date: str, days: int) -> str:
    return (dt.date.fromisoformat(date) + dt.timedelta(days=days)).isoformat()


# --- a minimal synthetic record ------------------------------------------------

SHA = "a" * 64
COMMIT = "b" * 40
PIN = f"PolicyEngine/test@{COMMIT}:{SHA}"
SEARCH_DATE = "2026-10-21"
EXCHEQUER = "positive = yield to the Exchequer"


def _producers(found_by: str, keys: list[str]) -> list[dict]:
    out = []
    for p in cmp.required_producers(PRODUCERS, "UK", SEARCH_DATE):
        entry = {
            "producer": p["slug"],
            "result": "none_found",
            "queries": [f"{p['slug']} test query"],
            "checked": [],
            "claims": [],
        }
        if p["slug"] == found_by:
            entry.update(result="found", claims=list(keys))
        if not cmp.applies(p, "uk_wide"):
            entry.update(result="not_applicable", queries=[])
        out.append(entry)
    return out


def synthetic(
    pe_value: float, ext_value: float, *, annotate: bool = False
) -> cmp.AnalysisRecord:
    """One UK analysis, one estimate, one compared claim; every producer
    logged none_found except the one that found the claim."""
    claim_key = "ext_cost_fy2027"
    identity = {"fy": "2027-28", "basis": "static", "program": "test_programme"}
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
                "conditions": {**identity, "sign_convention": EXCHEQUER},
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
    printed = ("-" if ext_value < 0 else "") + repr(abs(ext_value))
    claim = {
        "key": claim_key,
        "source": "ifs",
        "found_by": "ifs",
        "found_on": SEARCH_DATE,
        "source_model": "ifs_taxben",
        "metric": "revenue_change",
        "unit_concept": "gbp",
        "value": ext_value,
        "value_raw": printed,
        "normalization": "as printed",
        "value_kind": "point",
        "period": 2028,
        "time_basis": "fiscal_year",
        "conditions": {**identity, "sign_convention": EXCHEQUER},
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
        "quote": f"Cost {printed}",
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
                    "results_pins": [PIN],
                    "producers": _producers("ifs", [claim_key]),
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


def mutate(fn, base=None):
    record = base or synthetic(-100.0, -105.0)
    assert errors_of(record) == []
    fn(record)
    return errors_of(record)


def claim0(record) -> dict:
    return record.claims[0]


def note(nid, keys, status, explains=False, **extra):
    return {
        "id": nid,
        "claims": keys,
        "status": status,
        "explains_gap": explains,
        "cause": "a cause long enough to count as one",
        "basis": [
            {"kind": "issue", "ref": "https://github.com/PolicyEngine/test/issues/9"}
        ],
        **extra,
    }


def post_publication(record, kind="reharvest", later="2026-10-22"):
    """The synthetic record, published on its search day, then searched again."""
    first = copy.deepcopy(record.search_log["searches"][0])
    for p in first["producers"]:
        if p["producer"] == "ifs":
            p.update(result="none_found", claims=[])
    record.analysis["published"] = SEARCH_DATE
    later_search = record.search_log["searches"][0]
    later_search.update(date=later, kind=kind)
    record.search_log["searches"] = [first, later_search]
    claim0(record)["found_on"] = later
    return record


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
    assert index["promotion_window_days"] == WINDOW


def test_the_index_publishes_the_entry_rules_the_validator_applies():
    rules = json.loads(cmp.INDEX_PATH.read_text())["entry_rules"]
    assert set(rules["analysis_tags"]) == cmp.ANALYSIS_TAGS
    assert set(rules["no_estimate_tags"]) == cmp.NO_ESTIMATE_TAGS
    assert rules["country_tags"] == list(cmp.COUNTRY_TAGS)
    assert rules["default_country"] == cmp.DEFAULT_COUNTRY
    assert rules["search_kinds"] == list(cmp.SEARCH_KINDS)


def test_the_index_is_strict_json():
    with pytest.raises(ValueError):
        cmp.render_index({"x": float("nan")})
    json.loads(cmp.INDEX_PATH.read_text(), parse_constant=lambda c: pytest.fail(c))


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


def test_a_producer_cannot_be_added_in_the_future(tmp_path):
    data = json.loads(cmp.PRODUCERS_PATH.read_text())
    data["countries"]["UK"][0]["added"] = "2099-01-01"
    path = tmp_path / "producers.json"
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="no later than today"):
        cmp.load_producers(path)


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
    unexplained = [e for e in errors_of(record) if "no annotation explains it" in e]
    # three central years, and the two scenario ranges
    assert len(unexplained) == 7
    assert any("centax_static_central_fy2027 is -45.8%" in e for e in unexplained)


def test_childcare_figures_are_what_the_published_files_imply():
    rows = {r["key"]: r for r in cmp.evaluate(childcare(), POLICY)}
    assert rows["centax_static_central_fy2027"]["gap"] == pytest.approx(
        0.434 / 0.80 - 1
    )
    assert rows["centax_static_central_fy2029"]["gap"] == pytest.approx(
        0.505 / 0.98 - 1
    )
    assert rows["centax_static_central_fy2028"]["gap"] == pytest.approx(
        0.484 / 0.88 - 1
    )
    # the scenario range is over by its nearer bound, the low-cost scenario
    assert rows["centax_static_low_cost_fy2027"]["group_gap"] == pytest.approx(
        0.434 / 0.58 - 1
    )
    # compared across two worlds, so constructed rather than comparable
    assert rows["centax_static_central_fy2027"]["status"] == "constructed"
    # net of behaviour beside the dashboard's net figure, labelled a mismatch
    assert (
        rows["centax_net_central_fy2027"]["nearest"]
        == "both_schemes_dynamic_central_fy2027"
    )
    assert rows["centax_net_central_fy2027"]["status"] == "concept_mismatch"
    assert rows["centax_net_central_fy2027"]["nearest_gap"] == pytest.approx(
        -0.479 / -0.520 - 1
    )
    # CBP's net gain against the dashboard's net cost: compared, signs disagree
    assert (
        rows["cbp_net_table3_fy2027"]["estimate"]
        == "both_schemes_dynamic_central_fy2027"
    )
    assert rows["cbp_net_table3_fy2027"]["sign_disagrees"]
    assert rows["cbp_net_table3_fy2027"]["over"]


# --- the gate as a property -------------------------------------------------------------

money = st.floats(min_value=1e3, max_value=1e12, allow_nan=False, allow_infinity=False)


def _signed_record(pe: float, ext: float, annotate=False):
    """A synthetic record whose external value is printed with its own sign."""
    record = synthetic(pe, ext, annotate=annotate)
    return record


@settings(max_examples=200, deadline=None)
@given(pe=money, ext=money, pe_negative=st.booleans(), ext_negative=st.booleans())
def test_gate_fails_exactly_when_an_unexplained_gap_exceeds_the_threshold(
    pe, ext, pe_negative, ext_negative
):
    pe = float(round(pe)) * (-1 if pe_negative else 1)
    ext = float(round(ext)) * (-1 if ext_negative else 1)
    gap = pe / ext - 1
    assume(abs(abs(gap) - THRESHOLD) > 1e-9)  # stay off the boundary
    errors = errors_of(_signed_record(pe, ext))
    gate_errors = [e for e in errors if "no annotation explains it" in e]
    assert [e for e in errors if e not in gate_errors] == []
    should_fail = abs(gap) > THRESHOLD or (pe > 0) != (ext > 0)
    assert bool(gate_errors) == should_fail


@settings(max_examples=60, deadline=None)
@given(pe=money, ext=money, flip=st.booleans())
def test_an_explained_gap_always_passes(pe, ext, flip):
    ext = float(round(ext)) * (-1 if flip else 1)
    assert errors_of(synthetic(-float(round(pe)), ext, annotate=True)) == []


def test_an_annotation_that_does_not_explain_the_gap_fails():
    record = synthetic(-100.0, -300.0, annotate=True)
    record.annotations[0]["explains_gap"] = False
    assert any("explains_gap: true" in e for e in errors_of(record))


# --- no evasion: relabelling a like-for-like claim never hides its gap ---------------


def _evade(fn):
    """An unexplained 200% gap on a like-for-like claim, relabelled by ``fn``:
    the validator must still say something."""
    record = synthetic(-300.0, -100.0)
    assert any("no annotation explains it" in e for e in errors_of(record))
    fn(record)
    return errors_of(record)


EVASIONS = {
    "null metric": lambda r: claim0(r).update(
        metric=None,
        proposed_metric="cost",
        compare_to=None,
        pe_missing="a different metric entirely",
    ),
    "uncompared with a one-line reason": lambda r: claim0(r).update(
        compare_to=None, pe_missing="a different concept, says the stager"
    ),
    "time basis annual": lambda r: claim0(r).update(time_basis="annual"),
    "period moved, fy kept": lambda r: claim0(r).update(period=2031),
    "basis relabelled to net": lambda r: claim0(r)["conditions"].update(
        basis="post_behavioural"
    ),
    "programme relabelled": lambda r: claim0(r)["conditions"].update(
        program="another_programme"
    ),
    "chart reading at a different value": lambda r: claim0(r).update(
        value_kind="approx_chart_reading",
        value=-299.0,
        note="read off the chart by eye",
    ),
    "NaN value": lambda r: claim0(r).update(value=float("nan")),
    "unsigned magnitude": lambda r: claim0(r)["conditions"].update(
        change_direction="unsigned"
    ),
    "two-sided convention": lambda r: claim0(r)["conditions"].update(
        sign_convention="positive = reduction in borrowing; negative = increase in borrowing"
    ),
    "cumulative": lambda r: claim0(r).update(value_kind="cumulative"),
    "relabelled concept mismatch": lambda r: r.annotations.append(
        note("x", ["ext_cost_fy2027"], "concept_mismatch", explains=True)
    ),
    "same quantity set aside as a mismatch": lambda r: (
        claim0(r).update(
            compare_to=None,
            pe_missing="said to be a different concept",
            nearest_estimate="pe_cost_fy2027",
        ),
        r.annotations.append(note("x", ["ext_cost_fy2027"], "concept_mismatch")),
    ),
    "placeholder basis": lambda r: r.annotations.append(
        {
            **note("x", ["ext_cost_fy2027"], "comparable", explains=True),
            "basis": [{"kind": "document", "ref": "#"}],
        }
    ),
    "a directory as basis": lambda r: r.annotations.append(
        {
            **note("x", ["ext_cost_fy2027"], "comparable", explains=True),
            "basis": [{"kind": "document", "ref": "sources"}],
        }
    ),
    "a bare host as basis": lambda r: r.annotations.append(
        {
            **note("x", ["ext_cost_fy2027"], "comparable", explains=True),
            "basis": [{"kind": "document", "ref": "https://example.com"}],
        }
    ),
    "pending before publication": lambda r: r.annotations.append(
        note(
            "x",
            ["ext_cost_fy2027"],
            "pending",
            tracking_issue="https://github.com/PolicyEngine/test/issues/9",
        )
    ),
    "same-day reharvest": lambda r: (
        post_publication(r, later=SEARCH_DATE),
        r.annotations.append(
            note(
                "x",
                ["ext_cost_fy2027"],
                "pending",
                tracking_issue="https://github.com/PolicyEngine/test/issues/9",
            )
        ),
    ),
    "future-dated reharvest": lambda r: (
        post_publication(r, later="2099-12-31"),
        r.annotations.append(
            note(
                "x",
                ["ext_cost_fy2027"],
                "pending",
                tracking_issue="https://github.com/PolicyEngine/test/issues/9",
            )
        ),
    ),
    "reharvest with no publication date": lambda r: (
        post_publication(r),
        r.analysis.update(published=None),
        r.annotations.append(
            note(
                "x",
                ["ext_cost_fy2027"],
                "pending",
                tracking_issue="https://github.com/PolicyEngine/test/issues/9",
            )
        ),
    ),
    "logged under open_search": lambda r: (
        claim0(r).update(found_by="open_search"),
        r.search_log["searches"][0].update(
            producers=_producers("open_search", ["ext_cost_fy2027"])
        ),
    ),
    "scale word disagrees": lambda r: claim0(r).update(
        value_raw="-100bn", quote="Cost -100bn"
    ),
}


@pytest.mark.parametrize("name", sorted(EVASIONS))
def test_no_relabelling_hides_an_unexplained_gap(name):
    errors = _evade(EVASIONS[name])
    assert errors, f"{name} let an unexplained gap through"


# --- search integrity -----------------------------------------------------------------


def test_a_search_cannot_be_dated_after_today():
    errors = mutate(lambda r: r.search_log["searches"][0].update(date="2099-01-01"))
    assert any("after today" in e for e in errors)


def test_a_search_cannot_predate_the_producer_list():
    def f(r):
        r.search_log["searches"][0].update(date="2026-10-01", producers=[])
        claim0(r)["found_on"] = "2026-10-01"
        claim0(r)["publication"]["date"] = "2026-09-01"

    errors = mutate(f)
    assert any("before the UK producer list" in e for e in errors)


def test_a_prepublish_search_comes_before_publication():
    errors = mutate(lambda r: r.analysis.update(published="2026-10-20"))
    assert any(
        "a prepublish search is dated on or before publication" in e for e in errors
    )


def test_a_backfill_needs_and_follows_publication():
    def f(r):
        r.search_log["searches"][0]["kind"] = "backfill"

    assert any("needs analysis.json published" in e for e in mutate(f))

    def g(r):
        r.search_log["searches"][0]["kind"] = "backfill"
        r.analysis["published"] = "2026-10-22"

    errors = mutate(g)
    assert any("after publication" in e or "no later than today" in e for e in errors)


def test_only_the_first_search_is_prepublish_or_backfill():
    def f(r):
        post_publication(r, kind="reharvest")
        r.search_log["searches"][1]["kind"] = "backfill"

    assert any("only the first search is backfill" in e for e in mutate(f))


def test_a_reharvest_find_may_wait_on_its_issue():
    record = post_publication(synthetic(-100.0, -300.0))
    assert any("no annotation explains it" in e for e in errors_of(record))
    record.annotations.append(
        note(
            "new-find",
            ["ext_cost_fy2027"],
            "pending",
            tracking_issue="https://github.com/PolicyEngine/test/issues/3",
        )
    )
    assert errors_of(record) == []
    entry = cmp.index_entry(record, POLICY)
    assert entry["pending"] == 1
    assert entry["tracking_issues"] == ["https://github.com/PolicyEngine/test/issues/3"]
    report = cmp.report(record, "2026-10-22", POLICY)
    assert report["new_claims"] == ["ext_cost_fy2027"]
    assert report["over_threshold"][0]["tracking_issue"].endswith("/3")


def test_a_backfill_find_may_wait_on_its_issue():
    def f(r):
        r.analysis["published"] = "2026-10-12"
        r.search_log["searches"][0]["kind"] = "backfill"

    record = synthetic(-100.0, -300.0)
    f(record)
    record.annotations.append(
        note(
            "x",
            ["ext_cost_fy2027"],
            "pending",
            tracking_issue="https://github.com/PolicyEngine/test/issues/4",
        )
    )
    assert errors_of(record) == []


def test_a_new_results_file_needs_a_new_search():
    def f(r):
        r.analysis["pe_estimates"][0]["provenance"]["commit"] = "c" * 40

    errors = mutate(f)
    assert any("a new results file needs a new search" in e for e in errors)


def test_a_superseded_estimate_stays_as_history():
    record = synthetic(-100.0, -105.0)
    old = copy.deepcopy(record.analysis["pe_estimates"][0])
    old.update(superseded_on="2026-10-21")
    new = record.analysis["pe_estimates"][0]
    new["provenance"]["commit"] = "c" * 40
    record.analysis["superseded_estimates"] = [old]
    record.search_log["searches"][0]["results_pins"] = [
        f"PolicyEngine/test@{'c' * 40}:{SHA}"
    ]
    assert errors_of(record) == []


def test_the_first_search_is_never_a_later_kind():
    for kind in cmp.LATER_KINDS:
        errors = mutate(lambda r, k=kind: r.search_log["searches"][0].update(kind=k))
        assert any("prepublish or backfill" in e for e in errors), kind


# --- each other rule fails a record that breaks it ---------------------------------


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
    errors = mutate(lambda r: _search(r)[0].update(result="not_applicable", queries=[]))
    assert any("applies to 'uk_wide'" in e for e in errors)


def test_a_search_with_nothing_run_fails():
    errors = mutate(lambda r: _search(r)[0].update(queries=[], checked=[]))
    assert any("no query run" in e for e in errors)


def test_queries_are_a_list_of_strings():
    errors = mutate(lambda r: _search(r)[0].update(queries="x"))
    assert any("lists of strings" in e for e in errors)


def test_found_not_staged_says_what_and_where():
    errors = mutate(lambda r: _search(r)[0].update(result="found_not_staged", note=""))
    assert any("lists the pages it was seen on" in e for e in errors)
    assert any("says what was found" in e for e in errors)


def test_a_claim_no_search_found_fails():
    def f(r):
        for p in _search(r):
            if p["producer"] == "ifs":
                p.update(claims=[], result="none_found")

    assert any("no search entry lists this claim" in e for e in mutate(f))


def test_a_listed_producer_finds_only_its_own_claims():
    errors = mutate(lambda r: claim0(r).update(source="resolution_foundation"))
    assert any("logged under resolution_foundation's own entry" in e for e in errors)


@pytest.mark.parametrize("source", ["policyengine", "academic", "open_search"])
def test_a_source_names_a_real_producer(source):
    errors = mutate(lambda r: claim0(r).update(source=source))
    assert any("names the producer that published the figure" in e for e in errors)


def test_an_unused_primary_fails():
    def f(r):
        extra = dict(
            r.manifest[0], sha256="d" * 64, url="https://example.org/other.pdf"
        )
        r.manifest.append(extra)

    assert any("cited by no claim" in e for e in mutate(f))


def test_a_value_that_is_not_what_was_printed_fails():
    errors = mutate(lambda r: claim0(r).update(value=-999.0))
    assert any("is not value_raw" in e for e in errors)


def test_a_quote_without_the_value_fails():
    errors = mutate(lambda r: claim0(r).update(quote="no number here"))
    assert any("quote does not print the value" in e for e in errors)


def test_a_quote_must_print_the_whole_number_with_its_sign():
    assert not cmp.quote_contains("Cost 10.07", "0.07")
    assert not cmp.quote_contains("Cost -800m", "800m")
    assert cmp.quote_contains("Cost -800m and more", "-800m")
    assert cmp.quote_contains("Abolish Cliff 0.070 0.077 0.091", "0.077")


def test_an_unhashed_primary_fails():
    errors = mutate(lambda r: claim0(r)["publication"].update(primary_sha256="c" * 64))
    assert any("not in manifest.jsonl" in e for e in errors)


def test_a_publication_date_is_real_and_not_after_its_finding():
    assert any(
        "real YYYY-MM-DD" in e
        for e in mutate(lambda r: claim0(r)["publication"].update(date="2026-02-31"))
    )
    assert any(
        "after it was found" in e
        for e in mutate(lambda r: claim0(r)["publication"].update(date="2026-10-30"))
    )


def test_a_different_world_needs_a_reason():
    def f(r):
        r.analysis["worlds"]["other"] = {
            "policy": "uk_other",
            "description": "another world here",
        }
        claim0(r)["world"] = "other"

    assert any("compare across worlds only with" in e for e in mutate(f))


def test_a_cross_world_comparison_is_not_plainly_comparable():
    def f(r):
        r.analysis["worlds"]["other"] = {
            "policy": "uk_other",
            "description": "another world here",
        }
        claim0(r)["world"] = "other"
        claim0(r)["compare_to"]["across_worlds"] = {
            "reason": "the quantities are the same in both worlds, as measured",
            "basis": [
                {
                    "kind": "issue",
                    "ref": "https://github.com/PolicyEngine/test/issues/2",
                }
            ],
        }
        r.annotations.append(
            note("x", ["ext_cost_fy2027"], "comparable", explains=True)
        )

    assert any("constructed, not comparable" in e for e in mutate(f))


def test_baselines_must_agree():
    errors = mutate(lambda r: claim0(r).update(baseline_policy="current_policy"))
    assert any("scored against baseline current_policy" in e for e in errors)


def test_a_world_baseline_is_registered():
    errors = mutate(
        lambda r: r.analysis["worlds"]["test_reform"].update(baseline="not_a_world")
    )
    assert any("is not registered" in e for e in errors)


def test_an_unregistered_claim_baseline_fails():
    errors = mutate(
        lambda r: claim0(r).update(baseline_policy="not_a_registered_world")
    )
    assert any("is not registered" in e for e in errors)


def test_a_restated_figure_is_not_compared():
    errors = mutate(lambda r: claim0(r).update(attribution="restated"))
    assert any("only a producer's own estimate is compared" in e for e in errors)


def test_an_administrative_level_belongs_to_a_producer_source():
    errors = mutate(
        lambda r: claim0(r).update(
            benchmark_class="administrative_fact", world="baseline"
        )
    )
    assert any("calibration material" in e for e in errors)


def test_a_compared_claim_names_no_nearest_estimate():
    errors = mutate(lambda r: claim0(r).update(nearest_estimate="pe_cost_fy2027"))
    assert any("a compared claim has no nearest_estimate" in e for e in errors)


def test_a_nearest_estimate_must_be_near():
    def f(r):
        claim0(r).update(
            compare_to=None,
            pe_missing="a different period entirely",
            period=2031,
            nearest_estimate="pe_cost_fy2027",
        )
        claim0(r)["conditions"].pop("fy")

    assert any("is not near this claim" in e for e in mutate(f))


def test_a_claim_beside_its_nearest_estimate_needs_a_cited_mismatch():
    def name_it(r):
        claim0(r).update(
            compare_to=None,
            pe_missing="the producer's figure is net of behaviour",
            nearest_estimate="pe_cost_fy2027",
        )
        claim0(r)["conditions"]["basis"] = "post_behavioural"

    assert any("must say why" in e for e in mutate(name_it))

    def annotate(r):
        name_it(r)
        r.annotations.append(
            note("net-vs-static", ["ext_cost_fy2027"], "concept_mismatch")
        )

    assert mutate(annotate) == []


def test_a_range_needs_both_bounds_and_is_judged_as_a_range():
    def lone(r):
        claim0(r).update(value_kind="range_low")
        claim0(r)["conditions"]["range_group"] = "g"

    assert any(
        "needs exactly one range_low and one range_high" in e for e in mutate(lone)
    )

    def pair(pe, low, high):
        record = synthetic(pe, low)
        c = claim0(record)
        c.update(value_kind="range_low")
        c["conditions"]["range_group"] = "g"
        other = copy.deepcopy(c)
        printed = ("-" if high < 0 else "") + repr(abs(high))
        other.update(
            key="ext_cost_high_fy2027",
            value_kind="range_high",
            value=high,
            value_raw=printed,
            quote=f"Cost {printed}",
        )
        record.claims.append(other)
        for p in _search(record):
            if p["producer"] == "ifs":
                p["claims"].append(other["key"])
        return record

    inside = pair(-150.0, -100.0, -200.0)
    assert errors_of(inside) == []
    assert not any(r["over"] for r in cmp.evaluate(inside, POLICY))
    outside = pair(-300.0, -100.0, -200.0)
    rows = cmp.evaluate(outside, POLICY)
    assert all(r["over"] for r in rows)
    assert rows[0]["group_gap"] == pytest.approx(300 / 200 - 1)


def test_an_issue_basis_is_a_github_issue():
    def f(r):
        r.annotations.append(
            {
                **note("x", ["ext_cost_fy2027"], "comparable", explains=True),
                "basis": [{"kind": "issue", "ref": "https://example.org/ticket/1"}],
            }
        )

    assert any("GitHub issue or pull URL" in e for e in mutate(f))


def test_a_basis_may_be_a_file_in_this_repository():
    assert (
        cmp._check_basis(
            {"kind": "document", "ref": "docs/COMPARABLES.md#the-gap"}, "t"
        )
        == []
    )
    assert cmp._check_basis({"kind": "document", "ref": "docs"}, "t") != []
    assert cmp._check_basis({"kind": "document", "ref": "../../etc/passwd"}, "t") != []


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
    row["sign"] = True
    assert any("integer 1 or -1" in e for e in cmp.check_value(row, "t", signed=True))


def test_duplicate_json_keys_fail(tmp_path):
    directory = tmp_path / "analysis-uk-dup"
    directory.mkdir()
    for name in cmp.FILES:
        (directory / name).write_text("[]" if name.endswith(".json") else "")
    (directory / "analysis.json").write_text('{"a": 1, "a": 2}')
    record = cmp.load_analysis(directory)
    assert any("duplicate key" in e for e in record.load_errors)


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


@given(pe=nonzero, ext=nonzero, t=st.floats(0.001, 0.999))
def test_a_sign_disagreement_is_over_every_allowed_threshold(pe, ext, t):
    assume((pe > 0) != (ext > 0))
    assert cmp.sign_disagrees(pe, ext)
    assert cmp.over_threshold(cmp.relative_gap(pe, ext, signs.SAME), t)


@given(pe=nonzero, ext=nonzero, t1=st.floats(0.01, 0.99), t2=st.floats(0.01, 0.99))
def test_over_threshold_is_monotone_in_the_threshold(pe, ext, t1, t2):
    gap = cmp.relative_gap(pe, ext, signs.SAME)
    lo, hi = sorted((t1, t2))
    assert cmp.over_threshold(gap, hi) <= cmp.over_threshold(gap, lo)


def test_a_published_zero():
    assert cmp.relative_gap(0.0, 0.0, signs.SAME) == 0
    assert math.isinf(cmp.relative_gap(5.0, 0.0, signs.SAME))
    assert cmp.over_threshold(cmp.relative_gap(5.0, 0.0, signs.SAME), 0.99)


def test_no_rule_no_gap():
    assert cmp.relative_gap(1.0, 1.0, signs.UNKNOWN) is None
    assert not cmp.over_threshold(None, 0.25)


@pytest.mark.parametrize(
    "convention",
    [
        "positive = reduction in borrowing; negative = increase in borrowing",
        "negative = cost to the Exchequer",
        "positive = yield forgone",
        "",
    ],
)
def test_ambiguous_conventions_do_not_orient(convention):
    claim = {
        "metric": "revenue_change",
        "conditions": {"sign_convention": convention},
        "source": "x",
    }
    assert cmp.orientation(claim, "UK")[0] == signs.UNKNOWN


@pytest.mark.parametrize(
    "metric, convention, relation",
    [
        (
            "benefit_cost_change",
            "positive = increase in federal revenue",
            signs.UNKNOWN,
        ),
        ("benefit_cost_change", "positive = increase in tax receipts", signs.UNKNOWN),
        ("benefit_cost_change", "positive = higher government expenditure", signs.SAME),
        ("revenue_change", "positive = higher government revenue", signs.SAME),
        ("revenue_change", "positive = increase in borrowing", signs.OPPOSITE),
        ("avg_tax_change_usd", "positive = increase in tax credits", signs.UNKNOWN),
        ("avg_tax_change_usd", "positive = tax increase", signs.SAME),
    ],
)
def test_conventions_orient_only_when_they_say_one_thing(metric, convention, relation):
    claim = {
        "metric": metric,
        "conditions": {"sign_convention": convention},
        "source": "x",
    }
    assert cmp.orientation(claim, "US")[0] == relation


def test_a_us_change_with_no_convention_does_not_orient():
    claim = {"metric": "revenue_change", "conditions": {}, "source": "cbo"}
    assert cmp.orientation(claim, "US")[0] == signs.UNKNOWN


def test_the_policy_keeps_the_threshold_below_one(tmp_path):
    for bad in (1, 1.5, 0, True):
        path = tmp_path / "policy.json"
        path.write_text(json.dumps(dict(POLICY, gap_threshold=bad)))
        with pytest.raises(ValueError, match="between 0 and 1"):
            cmp.load_policy(path)


@pytest.mark.parametrize("days", [0, 91, 7.5, True, "7"])
def test_the_policy_rejects_a_bad_window(tmp_path, days):
    path = tmp_path / "policy.json"
    path.write_text(json.dumps(dict(POLICY, promotion_window_days=days)))
    with pytest.raises(ValueError, match="promotion_window_days"):
        cmp.load_policy(path)


# --- harvest rule 1 ------------------------------------------------------------------------

UNITS = {"m": "GBP m x 1e6 -> GBP", "bn": "GBP bn x 1e9 -> GBP", "": "as printed"}


@given(
    cents=st.integers(min_value=0, max_value=10**9),
    prefix=st.sampled_from(["", "£"]),
    unit=st.sampled_from(sorted(UNITS)),
    negative=st.booleans(),
    minus=st.sampled_from(["-", "−", "‒", "－"]),
    grouped=st.booleans(),
)
def test_printed_values_parse_back(cents, prefix, unit, negative, minus, grouped):
    number = cents / 100
    digits = f"{number:,.2f}" if grouped else f"{number:.2f}"
    raw = f"{minus if negative else ''}{prefix}{digits}{unit}"
    expected = -number if negative and number else number
    assert cmp.parse_printed(raw) == pytest.approx(expected)
    row = {
        "value": expected * cmp.NORMALIZATIONS[UNITS[unit]][0],
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
        ("£(0.4)bn", -0.4),
        ("(£0.4bn)", -0.4),
        ("−£1.2 billion", -1.2),
        ("2.1 per cent", 2.1),
        ("13,360", 13360),
        ("+140m", 140),
        ("post-tax £0.8bn", 0.8),
        ("minus £3m", -3),
    ],
)
def test_printed_forms(raw, value):
    assert cmp.parse_printed(raw) == value


@pytest.mark.parametrize(
    "raw, normalization",
    [
        ("£800m", "GBP bn x 1e9 -> GBP"),
        ("2.1%", "GBP bn x 1e9 -> GBP"),
        ("£0.8bn", "as printed"),
    ],
)
def test_a_printed_scale_must_match_the_normalization(raw, normalization):
    value = cmp.parse_printed(raw) * cmp.NORMALIZATIONS[normalization][0]
    errors = cmp.check_value(
        {"value": value, "value_raw": raw, "normalization": normalization}, "t"
    )
    assert any("states the scale" in e for e in errors)


def test_a_printed_range_is_two_claims():
    with pytest.raises(ValueError, match="2 numbers"):
        cmp.parse_printed("£1.2bn to £1.5bn")


# --- the app-v2 record ------------------------------------------------------------------------


@pytest.mark.parametrize("directory", cmp.analysis_dirs(), ids=lambda d: d.name)
def test_app_record_and_index_cite_the_same_search(directory):
    record = cmp.load_analysis(directory)
    block = cmp.app_record(record)
    entry = json.loads(cmp.INDEX_PATH.read_text())["analyses"][directory.name]
    search = next(
        s
        for s in entry["searches"]
        if s["date"] == block["searchDate"] and s["kind"] == block["searchKind"]
    )
    assert block["scorecardSource"] == directory.name
    assert block["producersSearched"] == search["producers_searched"]
    assert block["found"] == search["found"]
    assert block["searchLog"] == entry["search_log"]


@pytest.mark.parametrize("directory", cmp.analysis_dirs(), ids=lambda d: d.name)
def test_index_comparisons_are_every_staged_estimate(directory):
    record = cmp.load_analysis(directory)
    entry = json.loads(cmp.INDEX_PATH.read_text())["analyses"][directory.name]
    rows = {r["key"]: r for r in cmp.evaluate(record, POLICY)}
    assert [c["claim"] for c in entry["comparisons"]] == [
        c["key"] for c in record.claims
    ]
    assert entry["current_pins"] == cmp.current_pins(record.analysis)
    for c in entry["comparisons"]:
        row = rows[c["claim"]]
        assert c["estimate"] == row["estimate"]
        if row["gap"] is not None and not math.isinf(row["gap"]):
            assert c["gap"] == pytest.approx(row["gap"], abs=5e-5)
        assert (c["pe_value"] is None) == (row["estimate"] is None)
        assert c["nearest_estimate"] == row["nearest"]
        assert (c["nearest_pe_value"] is None) == (row["nearest"] is None)
        if row["over"]:
            assert c["cause"], f"{c['claim']} is over the threshold with no cause"


def test_scaffold_lists_every_producer(tmp_path):
    directory = cmp.scaffold("uk", "app", "new-dashboard", SEARCH_DATE, root=tmp_path)
    log = json.loads((directory / "search_log.json").read_text())
    logged = [p["producer"] for p in log["searches"][0]["producers"]]
    assert logged == [
        p["slug"] for p in cmp.required_producers(PRODUCERS, "UK", SEARCH_DATE)
    ]
    assert directory.name == "analysis-uk-new-dashboard"


def test_scaffold_refuses_a_country_with_no_list(tmp_path):
    with pytest.raises(SystemExit, match="no producer list for NG"):
        cmp.scaffold("ng", "app", "x", SEARCH_DATE, root=tmp_path)


def test_post_slug_is_the_websites():
    assert cmp.post_slug("UK_Two_Child-limit.md") == "uk-two-child-limit"
    assert cmp.post_slug("a.b.md") == "a"


def test_no_estimate_is_only_for_posts_that_are_not_analyses():
    assert cmp.may_declare_no_estimate("post", ["us", "giving"])
    assert not cmp.may_declare_no_estimate("post", ["uk", "autumn-budget", "featured"])
    assert not cmp.may_declare_no_estimate("post", ["us", "giving", "policy"])
    assert not cmp.may_declare_no_estimate("app", ["us", "giving"])


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
        {
            "slug": "unlisted",
            "countryId": "us",
            "date": "2026-10-03",
            "tags": ["us", "policy"],
        },
    ]
    posts = [
        {"filename": "Some_Post.md", "date": "2026-10-02", "tags": ["us", "policy"]},
        {
            "filename": "budget-costing.md",
            "date": "2026-10-04",
            "tags": ["uk", "autumn-budget"],
        },
        {
            "filename": "event.md",
            "date": "2026-10-03",
            "tags": ["uk", "event"],
            "comparables": {"status": "no_estimate", "reason": "x"},
        },
        {"filename": "untagged.md", "date": "2026-10-05", "tags": ["technical"]},
    ]
    rows = cmp.due(apps, posts, "2026-10-21", 183, root=tmp_path)
    assert [(r["kind"], r["source"]) for r in rows] == [
        ("post", "analysis-us-some-post"),
        ("app", "analysis-us-unlisted"),
        ("post", "analysis-uk-budget-costing"),
        ("post", "analysis-us-untagged"),
        ("app", "analysis-uk-a"),
    ]


def test_due_refuses_two_entries_sharing_a_record(tmp_path):
    apps = [
        {
            "slug": "x",
            "countryId": "uk",
            "date": "2026-10-12",
            "displayWithResearch": True,
            "tags": ["uk", "policy"],
        }
    ]
    posts = [{"filename": "x.md", "date": "2026-10-13", "tags": ["uk", "policy"]}]
    with pytest.raises(ValueError, match="would share the record analysis-uk-x"):
        cmp.due(apps, posts, "2026-10-21", 183, root=tmp_path)


# --- promotion: a fresh search before a push ----------------------------------------


def _entry(search_dates, pending=(), pins_match=True):
    return {
        "current_pins": [PIN],
        "searches": [
            {
                "date": d,
                "kind": "reharvest",
                "results_pins": [PIN] if pins_match else ["x"],
            }
            for d in search_dates
        ],
        "comparisons": [
            {"claim": f"c{i}", "status": "pending", "found_on": found}
            for i, found in enumerate(pending)
        ],
    }


days_st = st.integers(min_value=-400, max_value=400)
PUSH = "2026-11-02"


@given(offsets=st.lists(days_st, min_size=1, max_size=6), window=st.integers(1, 60))
def test_fresh_exactly_when_a_search_falls_in_the_window(offsets, window):
    dates = sorted(shift(PUSH, o) for o in offsets)
    in_window = any(-window <= o <= 0 for o in offsets)
    assert (cmp.fresh(_entry(dates), PUSH, window) == []) == in_window


@given(
    offsets=st.lists(days_st, min_size=1, max_size=6),
    w1=st.integers(1, 60),
    w2=st.integers(1, 60),
)
def test_a_wider_window_is_never_stricter(offsets, w1, w2):
    dates = sorted(shift(PUSH, o) for o in offsets)
    narrow, wide = sorted((w1, w2))
    if cmp.fresh(_entry(dates), PUSH, narrow) == []:
        assert cmp.fresh(_entry(dates), PUSH, wide) == []


@given(found=days_st)
def test_a_pending_gap_blocks_a_push_only_once_found(found):
    reasons = cmp.fresh(_entry([PUSH], pending=[shift(PUSH, found)]), PUSH, WINDOW)
    assert bool(reasons) == (found <= 0)


def test_a_search_against_old_results_is_not_fresh():
    reasons = cmp.fresh(_entry([PUSH], pins_match=False), PUSH, WINDOW)
    assert reasons and "compared the results the page reads now" in reasons[0]


def test_a_search_after_the_push_does_not_count():
    assert cmp.fresh(_entry([shift(PUSH, 1)]), PUSH, WINDOW) != []


def test_the_childcare_record_is_fresh_only_within_its_window():
    entry = json.loads(cmp.INDEX_PATH.read_text())["analyses"][CHILDCARE.name]
    assert cmp.fresh(entry, "2026-10-21", WINDOW) == []
    assert cmp.fresh(entry, shift("2026-10-21", WINDOW), WINDOW) == []
    late = cmp.fresh(entry, shift("2026-10-21", WINDOW + 1), WINDOW)
    assert late and "run a prepromotion search" in late[0]


def _fresh_cases() -> list[dict]:
    """The cases PolicyEngine/newsletters' fresh is checked against too."""
    cases = []
    for window in (3, 7):
        for search in (-9, -8, -7, -3, 0, 1):
            for pins_match in (True, False):
                for pending in (None, -2, 0, 2):
                    entry = _entry(
                        [shift(PUSH, search)],
                        pending=() if pending is None else [shift(PUSH, pending)],
                        pins_match=pins_match,
                    )
                    cases.append(
                        {
                            "entry": entry,
                            "on": PUSH,
                            "window": window,
                            "fresh": cmp.fresh(entry, PUSH, window) == [],
                        }
                    )
    return cases


def test_the_shared_fresh_cases_are_current():
    assert json.loads(FRESH_CASES.read_text()) == _fresh_cases()


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


def test_db_holds_exactly_the_records_claims(db):
    expected = {}
    for directory in cmp.analysis_dirs():
        record = cmp.load_analysis(directory)
        claims = {c["key"]: c for c in record.claims}
        for row in cmp.evaluate(record, POLICY):
            c = claims[row["key"]]
            if (
                c["attribution"] == "restated"
                or c.get("metric") is None
                or c.get("unit_concept") is None
            ):
                continue
            expected[(record.analysis["id"], row["key"])] = (row, c)
    seen = set()
    for r in _analysis_claims(db):
        cond = json.loads(r["conditions"])
        key = (cond["analysis"], cond["analysis_claim"])
        seen.add(key)
        row, claim = expected[key]
        results = db.execute(
            "SELECT status, computed_value FROM pe_results WHERE claim_id = ?",
            (r["claim_id"],),
        ).fetchall()
        history = 1 + sum(
            1
            for e in cmp.load_analysis(
                cmp.SOURCES / f"analysis-{key[0].replace('/', '-')}"
            ).analysis.get("superseded_estimates", [])
            if e["key"] in (row["estimate"], row["nearest"])
        )
        if row["estimate"] or row["nearest"]:
            assert len(results) == history
            want = row["status"]
            if want == "pending":
                want = "comparable"
            assert {res["status"] for res in results} == {want} or want == "comparable"
        else:
            assert results == []
            assert cond["pe_missing"]
    assert seen == set(expected)


def test_childcare_result_is_the_published_figure(db):
    row = db.execute(
        "SELECT r.computed_value, r.run_id, r.status, s.value FROM external_scores s JOIN pe_results r"
        " ON r.claim_id = s.claim_id WHERE json_extract(s.conditions, '$.analysis_claim') = ?",
        ("centax_static_central_fy2027",),
    ).fetchone()
    assert row["computed_value"] == -434e6
    assert row["value"] == -800e6
    assert row["status"] == "constructed"
    assert row["run_id"] == "analysis:uk/childcare-100k-threshold@f25f0db"
