"""The Autumn Budget 2026 ingest (#230, tranche 2).

Every one of the 5,952 staged rows becomes a claim or a tallied drop. These
tests pin the ingest's invariants:

1. read = ingested + dropped, per family and in total, against COUNTS.json
   and ingest_uk_ab2026_expected.json, with a written reason for each drop;
2. the AB2026 registry lists every claim's key, or for a Table 6.4 recosting
   the earlier event's does, and each claim takes that registry's verdict;
3. one claim per claim identity, and each HM Treasury figure counted once;
4. each claim's sign reads as signs.py reads it, pinned for every staged
   (metric, convention) pair and every pair the ingest's metric calls make;
5. the same claims from the same rows, run after run and in any row order;
6. AB2025's ingest and counterparts give the same output here as on
   origin/main.

Hypothesis checks the accounting on samples of the harvest, the order
independence, the twin rule and the share-of-GDP rule.
"""

import copy
import gzip
import json
import os
import random
import shutil
import sqlite3
import subprocess
import sys
from collections import Counter
from pathlib import Path

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from scorecard_db import ScorecardDB, signs
from scorecard_db import ingest_uk_ab2026 as I
from scorecard_db.models import Metric

ROOT = Path(__file__).resolve().parent.parent
COUNTS = json.loads((I.HARVEST / "COUNTS.json").read_text())
EARLIER = {
    p.name.removesuffix("_measures.json"): {
        m["measure_key"] for m in json.loads(p.read_text())["measures"]
    }
    for p in (ROOT / "data" / "uk" / "events").glob("*_measures.json")
}
EARLIER.setdefault("autumn_budget_2025", set()).update(
    m["measure_key"]
    for m in json.loads((ROOT / "data/uk/ab2025_measures.json").read_text())["measures"]
)


def _raw(family):
    path = I.HARVEST / family / "claims_staged.jsonl.gz"
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        return [json.loads(line) for line in fh]


RAW = {fam: _raw(fam) for fam in I.FAMILIES}


@pytest.fixture(scope="module")
def staged():
    return I.stage()


def _numbered(sample=None):
    return {
        fam: [
            (i, r) for i, r in enumerate(rows) if sample is None or (fam, i) in sample
        ]
        for fam, rows in RAW.items()
    }


def _rows(scores):
    return sorted(json.dumps(ScorecardDB.score_row(s), default=str) for s in scores)


# --- 1. the accounting -------------------------------------------------------


def test_every_staged_row_is_ingested_or_tallied(staged):
    scores, acct = staged
    exp = I.expected()
    assert acct["read"] == exp["read"] == COUNTS["_totals"]["rows"] == 5952
    assert acct["ingested"] == len(scores) == exp["ingested"]
    assert acct["ingested"] + acct["dropped"] == acct["read"]
    assert set(acct["by_family"]) == {k for k in COUNTS if not k.startswith("_")}
    for fam, v in acct["by_family"].items():
        assert v["read"] == COUNTS[fam]["rows"], fam
        assert v["ingested"] + v["dropped"] == v["read"], fam
    I.check_accounting(acct)


def test_every_drop_states_a_reason(staged):
    _, acct = staged
    for key, entry in acct["drops"].items():
        assert entry["rows"] > 0, key
        assert len(entry["reason"]) > 80, key
    assert sum(e["rows"] for e in acct["drops"].values()) == acct["dropped"]


def test_restated_rows_are_tallied_not_carried(staged):
    _, acct = staged
    assert (
        acct["drops"]["restated_official_figure"]["rows"]
        == COUNTS["_totals"]["restated"]
        == 450
    )


def test_every_staged_metric_name_is_decided():
    """Every metric name on a row that reaches a metric decision is adopted
    or dropped, never both; restated and categorical rows drop first."""
    for fam, rows in RAW.items():
        for r in rows:
            if r["attribution"] == "restated" or r.get("value_kind") == "categorical":
                continue
            name = r.get("metric") or r.get("proposed_metric")
            assert (name in I.DISPOSITIONS) != (name in I._DROP_BY_NAME), (fam, name)


def test_accounting_drift_raises(staged):
    _, acct = staged
    bad = json.loads(json.dumps(acct))
    bad["ingested"] -= 1
    bad["dropped"] += 1
    with pytest.raises(ValueError, match="accounting drifted"):
        I.check_accounting(bad)


def test_an_undecided_metric_raises(monkeypatch):
    row = copy.deepcopy(RAW["uk_tpa"][0])
    row["attribution"] = "own"
    row["metric"] = None
    row["proposed_metric"] = "a_metric_nobody_decided"
    with pytest.raises(ValueError, match="no disposition"):
        I.stage({"uk_tpa": [(10_000, row)]})


def test_a_moved_row_call_raises(monkeypatch):
    monkeypatch.setitem(
        I.ROW_DROPS, ("uk_obr_tables", 0), ("not this value", "no_registered_metric")
    )
    with pytest.raises(ValueError, match="no longer matches"):
        I._check_row_calls("uk_obr_tables", RAW["uk_obr_tables"])


# --- 2. keys and verdicts ----------------------------------------------------


def test_every_claim_key_is_registered_with_its_verdict(staged):
    scores, _ = staged
    for s in scores:
        c = s.conditions
        assert "proposed_measure_key" not in c
        key = c.get("measure_key")
        if key is None:
            continue
        if "recosting_of" in c:
            assert key in EARLIER[c["recosting_of"]], key
            if s.metric not in I.AB25.MACRO_METRICS:
                assert "pe_expressibility" not in c, key
            continue
        assert key in I.REGISTRY, key
        if s.metric in I.AB25.MACRO_METRICS:
            assert c["pe_expressibility"] == "not_expressible"
        else:
            assert c["pe_expressibility"] == I.REGISTRY[key]["computability"], key


def test_every_claim_names_its_producer_measure_and_event(staged):
    scores, _ = staged
    for s in scores:
        assert s.source in I.ALL_SOURCES
        assert s.conditions["fiscal_event"] == "autumn_budget_2026"
        assert s.publication["registry"] == I.REGISTRY_MARK
        geography = s.conditions.get("geography")
        assert s.publication["publish_without_result"] is (
            geography is None or geography in I.UK_GEOGRAPHIES
        ), geography


# --- 3. one claim per identity, each HM Treasury figure once -----------------


def test_claim_ids_are_unique(staged):
    scores, _ = staged
    ids = [s.claim_id() for s in scores]
    assert len(ids) == len(set(ids))


def test_each_hm_treasury_figure_is_counted_once(staged):
    """HM Treasury repeats 408 Table 6.1 cells in the costings and 24 in the
    red book; the ingest keeps each Table 6.1 claim and records its twins on
    it."""
    scores, acct = staged
    assert acct["drops"]["hmt_figure_staged_twice"]["rows"] == 432
    assert (
        acct["by_family"]["uk_hmt_costings"]["drops"]["hmt_figure_staged_twice"] == 408
    )
    assert acct["by_family"]["uk_hmt_redbook"]["drops"]["hmt_figure_staged_twice"] == 24
    printed = [s for s in scores if "also_printed_in" in s.publication]
    assert sum(len(s.publication["also_printed_in"]) for s in printed) == 432
    for s in printed:
        assert s.publication["family"] == "uk_hmt_tables"
        assert {
            t["family"] for t in s.publication["also_printed_in"]
        } <= I._TWIN_FAMILIES
    by_locator = {
        s.publication.get("locator"): s
        for s in scores
        if s.publication["family"] == "uk_hmt_tables"
    }
    for (fam, i), (t, reason) in I.REVIEWED_TWINS.items():
        assert len(reason) > 80
        kept = by_locator[RAW["uk_hmt_tables"][t]["publication"]["locator"]]
        assert RAW[fam][i]["publication"]["locator"] in {
            p["locator"] for p in kept.publication["also_printed_in"]
        }, (fam, i)


# Each reviewed red book row, the Table 6.1 row it repeats and both printings,
# read from the documents apart from I.REVIEWED_TWINS:
# red book row -> (table row, red book print, table cell, table value, table year)
REVIEWED_PINS = {
    6: (0, "£2.6 billion", "-2625", -2_625_000_000, 2027),
    179: (0, "£2.6 billion", "-2625", -2_625_000_000, 2027),
    11: (109, "£10 million", "-10", -10_000_000, 2028),
    236: (109, "£10 million", "-10", -10_000_000, 2028),
    220: (49, "£5 million", "-5", -5_000_000, 2028),
    270: (49, "£5 million", "-5", -5_000_000, 2028),
    263: (252, "£500 million", "-500", -500_000_000, 2027),
    271: (252, "£500 million", "-500", -500_000_000, 2027),
    272: (252, "£500 million", "-500", -500_000_000, 2027),
}


def test_each_reviewed_twin_repeats_the_cell_we_read():
    assert set(I.REVIEWED_TWINS) == {("uk_hmt_redbook", i) for i in REVIEWED_PINS}
    for i, (t, printed, cell, value, year) in REVIEWED_PINS.items():
        assert I.REVIEWED_TWINS[("uk_hmt_redbook", i)][0] == t, i
        assert RAW["uk_hmt_redbook"][i]["value_raw"] == printed, i
        table = RAW["uk_hmt_tables"][t]
        assert (table["value_raw"], table["value"], table["period"]) == (
            cell,
            value,
            year,
        ), i


# A costings or red book claim within 5% of a Table 6.1 or 6.2 claim on the
# same key and metric, once both read in PolicyEngine's orientation, that the
# reviewed twin table doesn't hold: (family, locator, period) -> why it stays
# a claim. A horizon difference (a multi-year total against one year) never
# comes within 5%, so none needs listing here.
NOT_TWINS: dict[tuple[str, str, int], str] = {}


def _pe_signed(s):
    relation, _ = signs.classify(
        {"metric": s.metric.value, "conditions": s.conditions, "country": "UK"}
    )
    return signs.external_value_pe_sign(s.value, relation)


def test_no_costings_or_red_book_claim_repeats_a_table_figure(staged):
    """A scan independent of _twin_key: it reads signs through signs.classify,
    allows rounding to 5% and ignores the period, so a repetition with
    another sign, rounding or year shows up unless the reviewed twin table
    drops it or NOT_TWINS gives a reason."""
    scores, _ = staged
    tables = [
        s
        for s in scores
        if s.publication["family"] == "uk_hmt_tables"
        and s.conditions.get("table") in ("6.1", "6.2")
    ]
    hits = set()
    for s in scores:
        if (
            s.publication["family"] not in I._TWIN_FAMILIES
            or s.conditions.get("component")
            or s.conditions.get("row_type") == "measure_component"
        ):
            continue
        v = _pe_signed(s)
        if not v:
            continue
        for t in tables:
            if t.metric != s.metric or t.conditions.get(
                "measure_key"
            ) != s.conditions.get("measure_key"):
                continue
            w = _pe_signed(t)
            if w and abs(v - w) <= 0.05 * abs(w):
                hits.add(
                    (s.publication["family"], s.publication.get("locator"), s.period)
                )
    assert hits <= set(NOT_TWINS), sorted(hits - set(NOT_TWINS))
    assert all(len(why) > 40 for why in NOT_TWINS.values())


# --- the metric calls ----------------------------------------------------------


def test_table_6_2_and_the_obr_financing_requirement_share_one_metric(staged):
    scores, _ = staged
    t62 = [s for s in scores if s.conditions.get("table") == "6.2"]
    assert len(t62) == 60
    assert {s.metric for s in t62} == {Metric.CASH_REQUIREMENT_CHANGE}
    obr = [
        s
        for s in scores
        if s.source == "obr_efo"
        and s.conditions.get("value_verbatim") == "£1.9 billion"
        and s.conditions.get("measure_key")
        == "ab2026__package_national_wealth_fund_and_british_business_bank"
    ]
    assert [s.metric for s in obr] == [Metric.CASH_REQUIREMENT_CHANGE]


def test_the_continued_fuel_duty_freeze_stays_on_borrowing(staged):
    """The OBR states the option's effect on public sector net borrowing, so
    its claim keeps that metric and takes the macro verdict (rule 10, #55)."""
    scores, _ = staged
    freeze = [
        s
        for s in scores
        if s.conditions.get("measure_key")
        == "ab2026_option__fuel_duty_continued_freeze"
    ]
    # RF derives its figure from the OBR's forecasts, so only the OBR's stays
    [obr] = freeze
    assert obr.source == "obr_efo"
    assert obr.metric == Metric.DECISIONS_EFFECT_ON_BORROWING
    assert "staged_metric" not in obr.conditions
    assert obr.conditions["pe_expressibility"] == "not_expressible"
    assert obr.conditions["pe_missing"] == I.AB25.MACRO_MISSING
    assert obr.conditions["action_link"] == I.AB25.MACRO_LINK


def test_ifs_keeps_the_one_off_payment_and_tallies_the_partial_year_support():
    """IFS averages January 2027's Household Energy Payment across households in
    England, and the whole payment falls in one fiscal year. Its other three
    averages cover part of a year."""
    rows = RAW["uk_ifs_ab2026"]
    scores, acct = I.stage({"uk_ifs_ab2026": [(i, rows[i]) for i in (43, 44, 45, 46)]})
    [claim] = scores
    assert claim.metric == Metric.AVERAGE_HOUSEHOLD_INCOME_CHANGE
    assert claim.unit_concept.value == "gbp_per_household"
    assert (claim.value, claim.period) == (80, 2027)
    c = claim.conditions
    assert c["measure_key"] == "ab2026__household_energy_payment_100_bands_a_to_d"
    assert c["staged_metric"] == "average_household_support"
    assert (c["geography"], c["payment_date"], c["price_basis"], c["horizon"]) == (
        "England",
        "January 2027",
        "2026-27 prices",
        "October 2026 to June 2027",
    )
    assert acct["drops"]["partial_year_household_support"]["rows"] == 3


def test_a_row_metric_on_another_row_raises(monkeypatch):
    """A re-staged family can't move a metric call onto another row."""
    monkeypatch.setitem(
        I.ROW_METRICS,
        ("uk_ifs_ab2026", 45),
        (
            "average_household_support",
            "£80",
            Metric.AVERAGE_HOUSEHOLD_INCOME_CHANGE,
            "x",
        ),
    )
    with pytest.raises(ValueError, match="ROW_METRICS uk_ifs_ab2026 row 45"):
        I.stage()


def test_the_obr_receipts_total_lands_on_revenue_and_its_restatement_drops(staged):
    obr, rf = RAW["uk_obr_tables"], RAW["uk_rf_ab2026"]
    assert {obr[i]["metric"] for i in range(2190, 2196)} == {"revenue_change"}
    assert {rf[i]["attribution"] for i in range(385, 391)} == {"restated"}
    scores, _ = staged
    totals = [
        s
        for s in scores
        if s.source == "obr_efo"
        and s.conditions.get("value_verbatim")
        in {obr[i]["value_raw"] for i in range(2190, 2196)}
        and s.conditions.get("component") == obr[2190]["conditions"].get("component")
    ]
    assert len(totals) == 6
    assert {s.metric for s in totals} == {Metric.REVENUE_CHANGE}
    restatement = {rf[i]["value_raw"] for i in range(385, 391)}
    assert not [
        s
        for s in scores
        if s.source == "resolution_foundation"
        and s.conditions["value_verbatim"] in restatement
    ]


def test_ifs_shares_of_gdp_take_percent_of_gdp():
    ifs = RAW["uk_ifs_ab2026"]
    gdp = [
        r
        for r in ifs
        if r.get("unit_concept") == "percent"
        and str(r["conditions"].get("denominator", "")).lower() == "gdp"
    ]
    assert len(gdp) == 33
    assert {I.unit_label(r) for r in gdp} == {"percent_of_gdp"}
    own = [r for r in gdp if r["attribution"] == "own"]
    assert len(own) == 1 and own[0]["value_raw"] == "0.2"
    assert I.AB25._UNIT_DROPS["percent_of_gdp"] == "macro_fiscal_or_out_of_scope"


# --- 4. signs -------------------------------------------------------------------

STAGED_READINGS = {
    (p["metric"], p["sign_convention"]): p["relation"]
    for p in json.loads((ROOT / "tests/fixtures/ab2026_sign_readings.json").read_text())
}
INGEST_READINGS = {
    (p["metric"], p["sign_convention"]): p["relation"]
    for p in json.loads(
        (ROOT / "tests/fixtures/ab2026_ingest_sign_readings.json").read_text()
    )
}


def test_every_claim_sign_reads_as_reviewed(staged):
    """A claim on its staged metric reads as the harvest fixture pins; a
    claim on a metric the ingest decided reads as the ingest fixture pins
    (reviewed 5 November 2026). A new pair fails until someone reviews it."""
    scores, _ = staged
    seen = set()
    for s in scores:
        if s.metric.value not in signs.ORIENTATION:
            continue
        pair = (s.metric.value, s.conditions.get("sign_convention"))
        fixture = (
            INGEST_READINGS if "staged_metric" in s.conditions else STAGED_READINGS
        )
        assert pair in fixture, pair
        relation, _ = signs.classify(
            {"metric": s.metric.value, "conditions": s.conditions, "country": "UK"}
        )
        assert relation == fixture[pair], pair
        if "staged_metric" in s.conditions:
            seen.add(pair)
    assert seen == set(INGEST_READINGS)


def test_only_unsigned_claims_lack_a_direction(staged):
    """Every oriented claim reads same or opposite, or states why no sign
    applies."""
    scores, _ = staged
    bases = Counter()
    for s in scores:
        if s.metric.value not in signs.ORIENTATION:
            continue
        relation, basis = signs.classify(
            {"metric": s.metric.value, "conditions": s.conditions, "country": "UK"}
        )
        if relation == "unknown":
            bases[basis] += 1
    assert set(bases) <= {
        "stated:exchequer:not_this_quantity",
        "stated:borrowing:not_this_quantity",
    }


# --- 5. determinism ---------------------------------------------------------


def test_the_stage_is_deterministic(staged):
    again, acct = I.stage()
    assert _rows(staged[0]) == _rows(again)
    assert I.summarise(acct) == I.summarise(staged[1])


@settings(max_examples=25, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(seed=st.integers(min_value=0, max_value=2**32 - 1))
def test_row_order_never_changes_the_claims_or_the_tally(seed):
    rng = random.Random(seed)
    numbered = _numbered()
    for fam in numbered:
        rng.shuffle(numbered[fam])
    scores, acct = I.stage(numbered)
    base_scores, base_acct = BASE
    # whole serialized claims, publication and twin printings included, so a
    # row order can't change which printing a claim cites
    assert _rows(scores) == BASE_ROWS
    assert I.summarise(acct) == I.summarise(base_acct)


BASE = I.stage()
BASE_ROWS = _rows(BASE[0])


@settings(max_examples=40, deadline=None, suppress_health_check=[HealthCheck.too_slow])
@given(
    seed=st.integers(min_value=0, max_value=2**32 - 1),
    share=st.floats(min_value=0.0, max_value=1.0),
)
def test_any_sample_of_the_harvest_closes_its_accounting(seed, share):
    """read = ingested + dropped holds for every sample of rows, by family
    and by reason, and no sample makes the ingest raise."""
    rng = random.Random(seed)
    sample = {
        (fam, i)
        for fam, rows in RAW.items()
        for i in range(len(rows))
        if rng.random() < share
    }
    scores, acct = I.stage(_numbered(sample))
    assert acct["read"] == len(sample)
    assert acct["ingested"] == len(scores)
    assert acct["ingested"] + acct["dropped"] == acct["read"]
    assert sum(e["rows"] for e in acct["drops"].values()) == acct["dropped"]
    for fam, v in acct["by_family"].items():
        assert v["ingested"] + v["dropped"] == v["read"]
        assert v["read"] == sum(1 for f, _ in sample if f == fam)
    base_ids = {s.claim_id() for s in BASE[0]}
    assert {s.claim_id() for s in scores} <= base_ids | {
        # a sample can keep a twin whose Table 6.1 row it left out
        s.claim_id()
        for s in scores
        if s.publication["family"] in I._TWIN_FAMILIES
    }


T61 = [
    (i, r)
    for i, r in enumerate(RAW["uk_hmt_tables"])
    if r["conditions"].get("table") == "6.1"
    and r["conditions"].get("row_type") == "measure"
]


@settings(max_examples=60, deadline=None)
@given(
    pick=st.integers(min_value=0, max_value=len(T61) - 1),
    family=st.sampled_from(sorted(I._TWIN_FAMILIES)),
    nudge=st.one_of(st.just(0.0), st.floats(min_value=1.0, max_value=1e9)),
)
def test_a_copy_of_a_table_6_1_cell_is_a_twin_only_at_the_same_value(
    pick, family, nudge
):
    i, row = T61[pick]
    twin = copy.deepcopy(row)
    # a costings row prints the cell under its own conditions; a copy with
    # the table row's conditions and another value would be one claim
    # printed twice, which merge_republications refuses
    twin["conditions"]["costing_leg_heading"] = "Exchequer impact (£m)"
    twin["value"] = row["value"] + nudge
    scores, acct = I.stage({"uk_hmt_tables": [(i, row)], family: [(99_999, twin)]})
    if nudge == 0.0:
        assert acct["drops"]["hmt_figure_staged_twice"]["rows"] == 1
        assert len(scores) == 1
        assert scores[0].publication["also_printed_in"][0]["family"] == family
    else:
        assert "hmt_figure_staged_twice" not in acct["drops"]
    assert acct["read"] == acct["ingested"] + acct["dropped"] == 2


@given(
    unit=st.sampled_from(["percent", "share", "gbp", "percentage_points", None]),
    denominator=st.sampled_from(["GDP", "gdp", " GDP ", "Gdp", "GNI", "", None]),
)
def test_only_a_percent_of_gdp_moves_unit(unit, denominator):
    row = {"unit_concept": unit, "proposed_unit": None, "conditions": {}}
    if denominator is not None:
        row["conditions"]["denominator"] = denominator
    moved = I.unit_label(row)
    is_gdp = unit == "percent" and (denominator or "").strip().lower() == "gdp"
    assert moved == ("percent_of_gdp" if is_gdp else unit)


# --- the database --------------------------------------------------------------


def test_round_trip_lanes_and_verdicts(tmp_path):
    db_path = tmp_path / "t.db"
    ScorecardDB(db_path).close()
    feed = tmp_path / "lanes.json"  # a copy: never the committed feed
    shutil.copy(ROOT / "data" / "lanes.json", feed)
    summary = I.ingest(db_path, feed)
    I.ingest(db_path, feed)  # idempotent
    verdicts = I.ingest_verdicts(db_path)
    conn = sqlite3.connect(db_path)
    n = conn.execute(
        "SELECT COUNT(*) FROM external_scores"
        " WHERE json_extract(publication, '$.registry') = ?",
        (I.REGISTRY_MARK,),
    ).fetchone()[0]
    assert n == summary["claims"] == I.expected()["ingested"]
    gaps = conn.execute(
        "SELECT COUNT(*) FROM external_scores"
        " WHERE json_extract(conditions, '$.pe_expressibility') = 'not_expressible'"
    ).fetchone()[0]
    assert verdicts == {"pe_gap_results": gaps, "pe_gap_diagnoses": gaps}
    lanes = dict(
        conn.execute("SELECT lane, stage FROM lanes WHERE lane LIKE 'uk-ab2026-%'")
    )
    assert lanes == {lane: "ingested" for lane in I.LANES}
    conn.close()
    fed = {lane["id"]: lane for lane in json.loads(feed.read_text())["lanes"]}
    for lane in I.LANES:
        assert fed[lane]["country"] == "UK"


# --- 6. AB2025 unchanged -------------------------------------------------------

_AB2025_DUMP = r"""
import json, shutil, sqlite3, sys, tempfile
from pathlib import Path
from scorecard_db import ScorecardDB
from scorecard_db import ingest_uk_ab2025 as A
out = Path(sys.argv[1])
tmp = Path(tempfile.mkdtemp())
db = tmp / "t.db"; ScorecardDB(db).close()
feed = tmp / "lanes.json"; shutil.copy(A.REPO / "data" / "lanes.json", feed)
A.ingest(db, feed); A.ingest_verdicts(db)
conn = sqlite3.connect(db)
def dump(sql):
    return sorted(json.dumps(list(r), default=str) for r in conn.execute(sql))
tables = {
    "claims": dump("SELECT claim_id, source, metric, period, value, conditions, publication, baseline_key FROM external_scores"),
    "results": dump("SELECT claim_id, status, engine_version, pe_construction, annotations FROM pe_results"),
    "diagnoses": dump("SELECT * FROM diagnoses"),
    "lanes": dump("SELECT lane, stage, detail FROM lanes"),
}
# AB2025's tranche 3: the stager's output over these claims, its
# counterparts attached as build_db attaches them, and the lanes after
from scorecard_db import ingest_campaign
from pipeline import stage_uk_ab2025 as T
rows, tally, unanswered = T.stage(db)
tables["staging"] = [json.dumps(r, sort_keys=True) for r in rows]
tables["staging_tally"] = json.dumps(tally, sort_keys=True)
tables["staging_unanswered"] = [json.dumps(r, sort_keys=True) for r in unanswered]
ingest_campaign.ingest(db, A.STAGED_COUNTERPARTS)
A.advance_lanes(db, feed)
tables["counterparts"] = dump("SELECT claim_id, computed_value, status, baseline_key, annotations FROM pe_results WHERE status != 'pe_gap'")
tables["lanes_after"] = dump("SELECT lane, stage, detail FROM lanes")
out.write_text(json.dumps(tables))
"""


def _ab2025_dump(tree: Path, out: Path):
    subprocess.run(
        [sys.executable, "-c", _AB2025_DUMP, str(out)],
        cwd=tree,
        env={**os.environ, "PYTHONPATH": str(tree)},
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(out.read_text())


def _main_ref():
    for ref in ("origin/main", "main"):
        ok = subprocess.run(
            ["git", "rev-parse", "--verify", "--quiet", ref],
            cwd=ROOT,
            capture_output=True,
        )
        if ok.returncode == 0:
            return ref
    return None


def test_ab2025_ingest_matches_main(tmp_path):
    """AB2025's claims, pe_gap results, diagnoses and lanes come out byte
    for byte as on main, and so do tranche 3's staging, attached
    counterparts and advanced lanes. CI fetches origin/main, so there a
    missing ref fails; a local checkout without one skips."""
    if _main_ref() is None:
        if os.environ.get("GITHUB_ACTIONS"):
            pytest.fail("CI must fetch origin/main for the AB2025 differential")
        pytest.skip("no main ref in this checkout")
    main = tmp_path / "main"
    main.mkdir()
    archive = subprocess.run(
        [
            "git",
            "archive",
            _main_ref(),
            "scorecard_db",
            "be",
            "nz",
            "data/uk",
            "data/lanes.json",
            "sources/harvest-uk-ab2025-2026-09-24",
            "pipeline",
            "results/uk/ab2025",
            "results/uk/staged_ab2025",
        ],
        cwd=ROOT,
        capture_output=True,
        check=True,
    ).stdout
    subprocess.run(["tar", "-x", "-C", str(main)], input=archive, check=True)
    theirs = _ab2025_dump(main, tmp_path / "main.json")
    ours = _ab2025_dump(ROOT, tmp_path / "ours.json")
    assert set(ours) == set(theirs)
    for table in ours:
        assert ours[table] == theirs[table], table


# --- value preservation ---------------------------------------------------------


def _staged_unit(row):
    unit = row.get("unit_concept") or row.get("proposed_unit")
    denominator = str((row.get("conditions") or {}).get("denominator", ""))
    if unit == "percent" and denominator.strip().lower() == "gdp":
        return "percent_of_gdp"
    return {"dwellings": "properties"}.get(unit, unit)


# The one row whose stored unit the ingest overrides, apart from I.ROW_UNITS:
# (family, locator, printed value) -> unit
STORED_UNITS = {("uk_ifs_ab2026", "slide 4", "£80"): "gbp_per_household"}


def _keeps_conditions(row, score):
    """Every staged condition reaches the claim, as itself or, where the ingest
    canonicalises its value, beside its verbatim text."""
    for key, value in (row.get("conditions") or {}).items():
        if value not in (
            score.conditions.get(key),
            score.conditions.get(f"{key}_verbatim"),
        ):
            if key != "program" or "program" not in score.conditions:
                return False
    return True


def test_every_claim_preserves_its_staged_row(staged):
    """Read each family's claims file directly, find the row behind each
    claim by its printed place and printed value, and require the claim to
    keep the producer's value, unit, conditions and provenance.
    Sign rule: the ingest stores the value as staged, in the producer's own
    orientation, and signs.py reads the orientation at comparison."""
    index = {}
    for fam, rows in RAW.items():
        for r in rows:
            loc = (r.get("publication") or {}).get("locator")
            index.setdefault(
                (fam, loc, r.get("source_column") or "", str(r["value_raw"])), []
            ).append(r)
    scores, _ = staged
    for s in scores:
        fam = s.publication["family"]
        stored_unit = STORED_UNITS.get(
            (fam, s.publication.get("locator"), s.conditions["value_verbatim"])
        )
        found = index.get(
            (
                fam,
                s.publication.get("locator"),
                s.source_column,
                s.conditions["value_verbatim"],
            )
        )
        assert found, (fam, s.publication.get("locator"))
        assert any(
            float(r["value"]) == s.value
            and (stored_unit or _staged_unit(r)) == s.unit_concept.value
            and (r.get("value_kind") or s.unit_concept.value) == s.value_kind
            and s.conditions.get("estimate_kind")
            == (r.get("value_kind") if r.get("value_kind") != "point" else None)
            and int(r["period"]) == s.period
            and r["time_basis"] == s.time_basis.value
            and r.get("quote") == s.publication.get("quote")
            and r.get("source_table") == s.publication.get("table")
            and r["attribution"] == s.publication.get("attribution")
            and _keeps_conditions(r, s)
            for r in found
        ), (fam, s.publication.get("locator"), s.value)


# --- guards the mutation runs found untested ----------------------------------


def test_each_ab2026_disposition_lands_on_its_metric(staged):
    """Every AB2026 adoption emits claims on its assigned metric."""
    scores, _ = staged
    pins = {
        "financial_transaction_cash_impact": Metric.CASH_REQUIREMENT_CHANGE,
        "unaffected_share": Metric.SHARE_NO_CHANGE,
    }
    assert set(pins) == set(I.DISPOSITIONS_AB2026)
    for name, metric in pins.items():
        got = {s.metric for s in scores if s.conditions.get("staged_metric") == name}
        assert got == {metric}, name


def test_ingest_checks_the_accounting_before_writing(tmp_path, monkeypatch):
    db_path = tmp_path / "t.db"
    ScorecardDB(db_path).close()
    monkeypatch.setattr(I, "expected", lambda: {"read": -1})
    with pytest.raises(ValueError, match="accounting drifted"):
        I.ingest(db_path, tmp_path / "lanes.json")
    conn = sqlite3.connect(db_path)
    assert conn.execute("SELECT COUNT(*) FROM external_scores").fetchone()[0] == 0


def test_verdict_rows_refuses_a_claim_the_registry_contradicts(tmp_path):
    db_path = tmp_path / "t.db"
    ScorecardDB(db_path).close()
    feed = tmp_path / "lanes.json"
    shutil.copy(ROOT / "data" / "lanes.json", feed)
    I.ingest(db_path, feed)
    key = next(
        k
        for k, m in I.REGISTRY.items()
        if m["computability"] == "partial"
        and k
        in {
            s.conditions.get("measure_key")
            for s in BASE[0]
            if s.metric not in I.AB25.MACRO_METRICS
        }
    )
    conn = sqlite3.connect(db_path)
    conn.execute(
        "UPDATE external_scores SET conditions = json_set(conditions,"
        " '$.pe_expressibility', 'not_expressible')"
        " WHERE json_extract(conditions, '$.measure_key') = ?",
        (key,),
    )
    conn.commit()
    conn.close()
    db = ScorecardDB(db_path)
    with pytest.raises(ValueError, match="in the registry"):
        I.verdict_rows(db)
    db.close()


@pytest.mark.parametrize(
    "mark", [{"component": "rate rise"}, {"row_type": "measure_component"}]
)
def test_a_part_of_a_measure_is_never_a_twin_of_the_whole(mark):
    """Rule 9: a component that equals its line's cell stays a claim."""
    i, row = T61[0]
    part = copy.deepcopy(row)
    part["conditions"].update(mark)
    part["conditions"]["costing_leg_heading"] = "Exchequer impact (£m)"
    scores, acct = I.stage(
        {"uk_hmt_tables": [(i, row)], "uk_hmt_costings": [(99_999, part)]}
    )
    assert "hmt_figure_staged_twice" not in acct["drops"]
    assert len(scores) == 2


def test_a_reviewed_twin_that_is_a_component_raises(monkeypatch):
    rows = copy.deepcopy(RAW["uk_hmt_redbook"])
    rows[6]["conditions"]["row_type"] = "measure_component"
    with pytest.raises(ValueError, match="REVIEWED_TWINS"):
        I._check_row_calls("uk_hmt_redbook", rows)


def _point_twin(monkeypatch, row, table_row):
    key = ("uk_hmt_redbook", row)
    monkeypatch.setitem(I.REVIEWED_TWINS, key, (table_row, I.REVIEWED_TWINS[key][1]))


def test_a_reviewed_twin_on_another_key_raises(monkeypatch):
    red_book = RAW["uk_hmt_redbook"][11]
    other = next(
        i
        for i, r in enumerate(RAW["uk_hmt_tables"])
        if abs(r["value"]) == abs(red_book["value"])
        and r["period"] == red_book["period"]
        and r.get("measure_key") != red_book.get("measure_key")
    )
    _point_twin(monkeypatch, 11, other)
    with pytest.raises(ValueError, match="no longer matches"):
        I._check_row_calls("uk_hmt_redbook", RAW["uk_hmt_redbook"])


def test_a_reviewed_twin_of_a_zero_cell_raises(monkeypatch):
    """Row 11 shares row 108's key and takes its year, so only the magnitude
    differs."""
    assert RAW["uk_hmt_tables"][108]["value"] == 0
    rows = copy.deepcopy(RAW["uk_hmt_redbook"])
    rows[11]["period"] = RAW["uk_hmt_tables"][108]["period"]
    _point_twin(monkeypatch, 11, 108)
    with pytest.raises(ValueError, match="no longer matches"):
        I._check_row_calls("uk_hmt_redbook", rows)


def test_a_reviewed_twin_of_another_year_raises(monkeypatch):
    rows = copy.deepcopy(RAW["uk_hmt_redbook"])
    rows[11]["period"] += 1
    with pytest.raises(ValueError, match="no longer matches"):
        I._check_row_calls("uk_hmt_redbook", rows)


def test_ukraine_s_explanation_grants_another_row_no_year_exception(monkeypatch):
    rows = copy.deepcopy(RAW["uk_hmt_redbook"])
    rows[11]["period"] += 1
    monkeypatch.setitem(I.REVIEWED_TWINS, ("uk_hmt_redbook", 11), (109, I._UKRAINE))
    with pytest.raises(ValueError, match="no longer matches"):
        I._check_row_calls("uk_hmt_redbook", rows)


@pytest.mark.parametrize("period", [2025, 2028, 2031])
def test_a_ukraine_row_in_any_other_year_raises(period):
    """We stage 2026, the announcement year, on these rows, and the table's cell
    for 2026-27 has period 2027, the only other year that matches."""
    rows = copy.deepcopy(RAW["uk_hmt_redbook"])
    rows[263]["period"] = period
    with pytest.raises(ValueError, match="no longer matches"):
        I._check_row_calls("uk_hmt_redbook", rows)


def test_a_ukraine_row_keeps_its_table_cell_for_the_year_exception(monkeypatch):
    """The year exception names table row 252, so another cell on the same key
    and of the same magnitude in another year raises."""
    table = copy.deepcopy(RAW["uk_hmt_tables"])
    table.append({**table[252], "period": 2030})
    monkeypatch.setattr(I, "_load", lambda family: table)
    _point_twin(monkeypatch, 263, len(table) - 1)
    with pytest.raises(ValueError, match="no longer matches"):
        I._check_row_calls("uk_hmt_redbook", RAW["uk_hmt_redbook"])


@pytest.mark.parametrize(
    "raw",
    ["in 2026-27, £2.6 billion", "£2.6bn", "2,600 million", "around £2.6 billion"],
)
def test_a_reviewed_twin_printed_in_another_form_raises(raw):
    rows = copy.deepcopy(RAW["uk_hmt_redbook"])
    rows[6]["value_raw"] = raw
    with pytest.raises(ValueError, match="no printed amount"):
        I._check_row_calls("uk_hmt_redbook", rows)


def test_a_reviewed_twin_whose_value_leaves_its_print_raises():
    """A row can't widen its own tolerance by storing another value."""
    rows = copy.deepcopy(RAW["uk_hmt_redbook"])
    rows[6]["value"] = 2.675e9
    with pytest.raises(ValueError, match="printed amount"):
        I._check_row_calls("uk_hmt_redbook", rows)


def test_a_reviewed_twin_printed_as_zero_raises():
    rows = copy.deepcopy(RAW["uk_hmt_redbook"])
    rows[6].update(value=0, value_raw="£0 million")
    with pytest.raises(ValueError, match="no longer matches"):
        I._check_row_calls("uk_hmt_redbook", rows)


def test_a_reviewed_twin_outside_the_printed_rounding_raises(monkeypatch):
    rows = copy.deepcopy(RAW["uk_hmt_redbook"])
    rows[6].update(value=2.7e9, value_raw="£2.7 billion")
    with pytest.raises(ValueError, match="no longer matches"):
        I._check_row_calls("uk_hmt_redbook", rows)


@given(st.integers(1, 99_999), st.integers(0, 3), st.booleans())
def test_the_printed_unit_follows_the_last_printed_digit(digits, places, billions):
    number = digits / 10**places
    word, scale = ("billion", 1e9) if billions else ("million", 1e6)
    raw = f"£{number:,.{places}f} {word}"
    unit = I._printed_unit({"value": number * scale, "value_raw": raw})
    assert unit == pytest.approx(scale / 10**places)


def test_the_stage_checks_its_row_calls(monkeypatch):
    monkeypatch.setitem(
        I.ROW_DROPS, ("uk_obr_tables", 0), ("not this value", "no_registered_metric")
    )
    with pytest.raises(ValueError, match="no longer matches"):
        I.stage()


def test_a_recosting_takes_no_registry_verdict():
    key = next(k for k, m in I.REGISTRY.items() if m["computability"] == "partial")
    cond = {"recosting_of": "autumn_budget_2025"}
    I._verdict_conditions({"measure_key": key}, cond, Metric.REVENUE_CHANGE)
    assert cond["measure_key"] == key
    assert "pe_expressibility" not in cond


@pytest.mark.parametrize("attached", [False, True])
@pytest.mark.parametrize(
    "field",
    ["access", "date", "locator", "primary_sha256", "publisher", "title", "url"],
)
def test_row_order_never_decides_a_printing_that_differs_in_one_field(field, attached):
    """We choose the same primary printing after changing any harvested
    publication field and reversing the rows."""
    i, row = T61[0]
    assert field in row["publication"]
    a, b = copy.deepcopy(row), copy.deepcopy(row)
    a["publication"][field] = "a"
    b["publication"][field] = "b"
    twin = copy.deepcopy(row)
    twin["conditions"]["costing_leg_heading"] = "Exchequer impact (£m)"
    twin["publication"]["locator"] = "costings"

    def kept(first, second):
        families = {"uk_hmt_tables": [(i, first), (i + 10_000, second)]}
        if attached:
            families["uk_hmt_costings"] = [(1, twin)]
        [claim], _ = I.stage(families)
        return claim.publication

    forward, backward = kept(a, b), kept(b, a)
    assert forward[field] == backward[field] == "b"
    if attached:
        assert forward["also_printed_in"] == backward["also_printed_in"]
        assert len(forward["also_printed_in"]) == 1


def test_a_printing_s_twins_never_move_the_tie_breaker():
    """We omit ``also_printed_in`` from the tie-breaker because we attach a
    costings repetition to the table printing we encounter last."""
    i, row = T61[0]
    a, b = copy.deepcopy(row), copy.deepcopy(row)
    a["publication"]["url"] = "https://example.org/a"
    b["publication"]["url"] = "https://example.org/b"
    twin = copy.deepcopy(row)
    twin["conditions"]["costing_leg_heading"] = "Exchequer impact (£m)"
    twin["publication"]["locator"] = "costings"
    for first, second in ((a, b), (b, a)):
        [kept], _ = I.stage(
            {
                "uk_hmt_tables": [(i, first), (i + 10_000, second)],
                "uk_hmt_costings": [(1, twin)],
            }
        )
        assert kept.publication["url"] == "https://example.org/b"
        assert [t["locator"] for t in kept.publication["also_printed_in"]] == [
            "costings"
        ]


def test_a_merged_printing_keeps_its_twins():
    """Two printings of one Table 6.1 claim merge; a costings repetition
    attached to the printing the merge drops moves to the one it keeps."""
    i, row = T61[0]
    a, b = copy.deepcopy(row), copy.deepcopy(row)
    a["publication"]["locator"] = "z"  # sorts above b, so the merge keeps a
    b["publication"]["locator"] = "a"
    twin = copy.deepcopy(row)
    twin["conditions"]["costing_leg_heading"] = "Exchequer impact (£m)"
    twin["publication"]["locator"] = "costings"
    scores, acct = I.stage(
        {"uk_hmt_tables": [(i, a), (i + 10_000, b)], "uk_hmt_costings": [(1, twin)]}
    )
    assert acct["drops"]["republished_twin_merged"]["rows"] == 1
    assert acct["drops"]["hmt_figure_staged_twice"]["rows"] == 1
    [kept] = scores
    assert kept.publication["locator"] == "z"
    assert [t["locator"] for t in kept.publication["also_printed_in"]] == ["costings"]


@pytest.mark.parametrize(
    "family, row, reading",
    [
        # phrases on rows the ingest drops before any claim forms
        ("uk_obr_tables", 2738, ("opposite", "stated:exchequer:opposite")),
        ("uk_ifs_ab2026", 53, ("opposite", "stated:household_gain:opposite")),
        ("uk_thinktank_misc", 9, ("same", "stated:household_gain:same")),
        ("uk_obr_tables", 2742, ("same", "stated:higher_output:same")),
        (
            "uk_obr_tables",
            2658,
            ("unknown", "stated:higher_inflation:not_this_quantity"),
        ),
    ],
)
def test_sign_phrases_on_dropped_rows_read_as_reviewed(family, row, reading):
    r = RAW[family][row]
    metric = r.get("metric") or r.get("proposed_metric")
    got = signs.classify(
        {"metric": metric, "conditions": r["conditions"], "country": "UK"}
    )
    assert got == reading
