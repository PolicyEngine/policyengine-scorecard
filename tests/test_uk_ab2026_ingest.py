"""The Autumn Budget 2026 ingest (#230, tranche 2).

Every one of the 5,959 staged rows becomes a claim or a tallied drop. These
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
import functools
import gzip
import json
import math
import os
import random
import re
import shutil
import sqlite3
import subprocess
import sys
from collections import Counter
from pathlib import Path
from types import SimpleNamespace

import pytest
from hypothesis import HealthCheck, example, given, settings
from hypothesis import strategies as st

from scorecard_db import ScorecardDB, signs
from scorecard_db import ingest_uk_ab2026 as I
from scorecard_db.models import Metric, ReformRef, TimeBasis, UnitConcept
from scorecard_db.uk_aliases import canon, known

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
    assert acct["read"] == exp["read"] == COUNTS["_totals"]["rows"] == 5959
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


def test_the_restated_fuel_freeze_reason_names_both_obr_figures():
    assert I.DROPS_AB2026["restated_obr_forecast"] == (
        "Resolution Foundation computes the cost of continuing the fuel duty "
        "freeze from two OBR forecasts, the constant-duty-rate receipts less "
        "the central receipts. We keep the OBR's own figures: its effect on "
        "borrowing in 2029-30 (paragraph 3.43) and its average cut in receipts "
        "from 2027-28 to 2031-32 (paragraph 4.30)."
    )


def test_the_new_obr_rows_become_one_claim_and_six_macro_drops():
    numbered = {"uk_obr_tables": list(enumerate(RAW["uk_obr_tables"][2800:], 2800))}
    scores, acct = I.stage(numbered)
    assert (acct["read"], acct["ingested"], acct["dropped"]) == (7, 1, 6)
    assert {key: value["rows"] for key, value in acct["drops"].items()} == {
        "macro_fiscal_or_out_of_scope": 6
    }
    claim = scores[0]
    assert claim.metric == Metric.REVENUE_CHANGE
    assert (
        claim.conditions["measure_key"] == "ab2026_option__fuel_duty_continued_freeze"
    )
    assert claim.value == 4_000_000_000
    assert claim.conditions["aggregation"] == "annual average 2027-28 to 2031-32"
    assert claim.reform.baseline == LATEST_POLICY_WORLD
    old, old_acct = I.stage({"uk_obr_tables": [(2688, RAW["uk_obr_tables"][2688])]})
    assert old == []
    assert set(old_acct["drops"]) == set(acct["drops"])


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


def test_a_moved_time_basis_call_raises(monkeypatch):
    monkeypatch.setitem(
        I.ROW_TIME_BASES,
        ("uk_hmt_redbook", 0),
        ("annual", "not this value", "point_in_time", "x" * 41),
    )
    with pytest.raises(ValueError, match="no longer matches"):
        I._check_row_calls("uk_hmt_redbook", RAW["uk_hmt_redbook"])


def test_each_restaged_row_takes_the_time_basis_we_store():
    """Review of #256, M3: we stage HM Treasury's £50 off the annual price
    cap, and its count of households that the government pays from January
    2027, on the time basis of the printing we keep."""
    assert len(I.ROW_TIME_BASES) == 3
    for (family, i), (staged, printed, stored, why) in I.ROW_TIME_BASES.items():
        assert (RAW[family][i]["time_basis"], RAW[family][i]["value_raw"]) == (
            staged,
            printed,
        )
        assert _staged_alone(family, i).time_basis.value == stored, (family, i)
        assert len(why) > 40


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
    printed = [
        s
        for s in scores
        if s.publication["family"] == "uk_hmt_tables"
        and "also_printed_in" in s.publication
    ]
    assert sum(len(s.publication["also_printed_in"]) for s in printed) == 432
    for s in printed:
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


# --- figures a producer prints more than once ----------------------------------

# Each repeated printing, the printing whose claim we keep, and the value_raw
# of both, which we list here apart from I.REPEATED_PRINTINGS:
# (family, repeat row) -> (kept row, repeat's printing, kept printing). We
# give the kept row as (family, row) where its family differs.
REPEATED_PINS = {
    ("uk_centax", 25): (1, "£640 million", "£640 million"),
    ("uk_centax", 62): (82, "58%", "57.52%"),
    ("uk_centax", 64): (67, "9%", "8.75%"),
    ("uk_centax", 65): (66, "less than 0.5%", "0.40%"),
    ("uk_centax", 107): (21, "£19.7 billion", "£19.7 billion"),
    ("uk_centax", 108): (58, "£14 billion", "£14 billion"),
    ("uk_hmt_costings", 191): (("uk_hmt_redbook", 273), "+0m", "+0m"),
    ("uk_hmt_costings", 192): (("uk_hmt_redbook", 274), "+10m", "+10m"),
    ("uk_hmt_costings", 193): (("uk_hmt_redbook", 275), "+55m", "+55m"),
    ("uk_hmt_costings", 194): (("uk_hmt_redbook", 276), "+140m", "+140m"),
    ("uk_hmt_costings", 195): (("uk_hmt_redbook", 277), "+160m", "+160m"),
    ("uk_hmt_costings", 196): (("uk_hmt_redbook", 278), "+150m", "+150m"),
    ("uk_hmt_costings", 197): (("uk_hmt_redbook", 279), "+0m", "+0m"),
    ("uk_hmt_costings", 198): (("uk_hmt_redbook", 280), "+0m", "+0m"),
    ("uk_hmt_costings", 199): (("uk_hmt_redbook", 281), "-85m", "-85m"),
    ("uk_hmt_costings", 200): (("uk_hmt_redbook", 282), "+70m", "+70m"),
    ("uk_hmt_costings", 201): (("uk_hmt_redbook", 283), "+25m", "+25m"),
    ("uk_hmt_costings", 202): (("uk_hmt_redbook", 284), "+25m", "+25m"),
    ("uk_hmt_costings", 203): (("uk_hmt_redbook", 285), "+0m", "+0m"),
    ("uk_hmt_costings", 204): (("uk_hmt_redbook", 286), "+0m", "+0m"),
    ("uk_hmt_costings", 205): (("uk_hmt_redbook", 287), "+0m", "+0m"),
    ("uk_hmt_costings", 206): (("uk_hmt_redbook", 288), "+1,355m", "+1,355m"),
    ("uk_hmt_costings", 207): (("uk_hmt_redbook", 289), "+1,605m", "+1,605m"),
    ("uk_hmt_costings", 208): (("uk_hmt_redbook", 290), "+1,815m", "+1,815m"),
    ("uk_hmt_costings", 209): (("uk_hmt_redbook", 291), "+0m", "+0m"),
    ("uk_hmt_costings", 210): (("uk_hmt_redbook", 292), "+0m", "+0m"),
    ("uk_hmt_costings", 211): (("uk_hmt_redbook", 293), "+0m", "+0m"),
    ("uk_hmt_costings", 212): (("uk_hmt_redbook", 294), "+165m", "+165m"),
    ("uk_hmt_costings", 213): (("uk_hmt_redbook", 295), "+5m", "+5m"),
    ("uk_hmt_costings", 214): (("uk_hmt_redbook", 296), "+5m", "+5m"),
    ("uk_hmt_costings", 215): (("uk_hmt_redbook", 297), "+0m", "+0m"),
    ("uk_hmt_costings", 216): (("uk_hmt_redbook", 298), "+0m", "+0m"),
    ("uk_hmt_costings", 217): (("uk_hmt_redbook", 299), "+0m", "+0m"),
    ("uk_hmt_costings", 218): (("uk_hmt_redbook", 300), "+20m", "+20m"),
    ("uk_hmt_costings", 219): (("uk_hmt_redbook", 301), "+65m", "+65m"),
    ("uk_hmt_costings", 220): (("uk_hmt_redbook", 302), "+55m", "+55m"),
    ("uk_hmt_costings", 221): (("uk_hmt_redbook", 303), "+0m", "+0m"),
    ("uk_hmt_costings", 222): (("uk_hmt_redbook", 304), "+0m", "+0m"),
    ("uk_hmt_costings", 223): (("uk_hmt_redbook", 305), "+0m", "+0m"),
    ("uk_hmt_costings", 224): (("uk_hmt_redbook", 306), "+50m", "+50m"),
    ("uk_hmt_costings", 225): (("uk_hmt_redbook", 307), "+255m", "+255m"),
    ("uk_hmt_costings", 226): (("uk_hmt_redbook", 308), "+320m", "+320m"),
    ("uk_hmt_costings", 227): (("uk_hmt_redbook", 309), "+65m", "+65m"),
    ("uk_hmt_costings", 228): (("uk_hmt_redbook", 310), "+120m", "+120m"),
    ("uk_hmt_costings", 229): (("uk_hmt_redbook", 311), "+0m", "+0m"),
    ("uk_hmt_costings", 230): (("uk_hmt_redbook", 312), "+75m", "+75m"),
    ("uk_hmt_costings", 231): (("uk_hmt_redbook", 313), "+250m", "+250m"),
    ("uk_hmt_costings", 232): (("uk_hmt_redbook", 314), "+575m", "+575m"),
    ("uk_hmt_costings", 235): (("uk_hmt_redbook", 315), "+50m", "+50m"),
    ("uk_hmt_costings", 236): (("uk_hmt_redbook", 316), "+205m", "+205m"),
    ("uk_hmt_costings", 237): (("uk_hmt_redbook", 317), "+310m", "+310m"),
    ("uk_hmt_costings", 238): (("uk_hmt_redbook", 318), "+260m", "+260m"),
    ("uk_hmt_costings", 239): (("uk_hmt_redbook", 319), "+270m", "+270m"),
    ("uk_hmt_costings", 240): (("uk_hmt_redbook", 320), "+415m", "+415m"),
    ("uk_hmt_costings", 241): (("uk_hmt_redbook", 321), "+0m", "+0m"),
    ("uk_hmt_costings", 242): (("uk_hmt_redbook", 322), "-15m", "-15m"),
    ("uk_hmt_costings", 243): (("uk_hmt_redbook", 323), "-40m", "-40m"),
    ("uk_hmt_costings", 244): (("uk_hmt_redbook", 324), "+5m", "+5m"),
    ("uk_hmt_costings", 245): (("uk_hmt_redbook", 325), "+0m", "+0m"),
    ("uk_hmt_costings", 246): (("uk_hmt_redbook", 326), "+0m", "+0m"),
    ("uk_hmt_costings", 247): (("uk_hmt_redbook", 327), "-5m", "-5m"),
    ("uk_hmt_costings", 248): (("uk_hmt_redbook", 328), "-30m", "-30m"),
    ("uk_hmt_costings", 249): (("uk_hmt_redbook", 329), "+0m", "+0m"),
    ("uk_hmt_costings", 250): (("uk_hmt_redbook", 330), "+0m", "+0m"),
    ("uk_hmt_costings", 251): (("uk_hmt_redbook", 331), "+0m", "+0m"),
    ("uk_hmt_costings", 252): (("uk_hmt_redbook", 332), "+0m", "+0m"),
    ("uk_hmt_redbook", 5): (188, "around £50", "£50"),
    ("uk_hmt_redbook", 180): (7, "20 million", "up to 20 million"),
    ("uk_hmt_redbook", 181): (354, "£2.3 billion", "+2,250m"),
    ("uk_hmt_redbook", 189): (7, "20 million", "up to 20 million"),
    ("uk_hmt_redbook", 190): (188, "£50", "£50"),
    ("uk_hmt_redbook", 194): (9, "£30", "around £30"),
    ("uk_hmt_redbook", 197): (188, "£50", "£50"),
    ("uk_hmt_redbook", 201): (9, "£30", "around £30"),
    ("uk_hmt_redbook", 202): (187, "35 million", "35 million"),
    ("uk_hmt_redbook", 256): (14, "70,000", "70,000"),
    ("uk_hmt_redbook", 265): (176, "£50 million", "£50 million"),
    ("uk_hmt_redbook", 268): (258, "£15 million", "£15 million"),
    ("uk_hmt_redbook", 362): (400, "£33,500", "33,500"),
    ("uk_hmt_redbook", 423): (422, "£166", "£166"),
    ("uk_ifs_ab2026", 97): (91, "80%", "80%"),
    ("uk_obr_tables", 2520): (2501, "£12 billion", "11,681"),
    ("uk_obr_tables", 2526): (2171, "£5.5 billion", "5500"),
    ("uk_obr_tables", 2531): (1183, "£1 billion", "951"),
    ("uk_obr_tables", 2540): (2352, "5.8", "-5,848"),
    ("uk_obr_tables", 2541): (2353, "3.9", "-3,877"),
    ("uk_obr_tables", 2542): (2354, "3.5", "-3,458"),
    ("uk_obr_tables", 2543): (2355, "1.7", "-1,699"),
    ("uk_obr_tables", 2544): (2356, "1.6", "-1,578"),
    ("uk_obr_tables", 2545): (2357, "-4.2", "4,161"),
    ("uk_obr_tables", 2552): (2514, "-1.3", "-1,308"),
    ("uk_obr_tables", 2553): (2515, "3.5", "3,483"),
    ("uk_obr_tables", 2554): (2516, "1.7", "1,702"),
    ("uk_obr_tables", 2555): (2517, "1.4", "1,424"),
    ("uk_obr_tables", 2556): (2518, "1.4", "1,442"),
    ("uk_obr_tables", 2557): (2519, "2.4", "2,412"),
    ("uk_obr_tables", 2558): (2496, "7.6", "-7,597"),
    ("uk_obr_tables", 2559): (2497, "3.5", "-3,532"),
    ("uk_obr_tables", 2560): (2498, "0.4", "-380"),
    ("uk_obr_tables", 2561): (2499, "-4.1", "4,061"),
    ("uk_obr_tables", 2562): (2500, "-5.0", "4,983"),
    ("uk_obr_tables", 2563): (2501, "-11.7", "11,681"),
    ("uk_obr_tables", 2564): (6, "2.6", "-2627"),
    ("uk_obr_tables", 2565): (7, "0.0", "0"),
    ("uk_obr_tables", 2566): (8, "0.0", "0"),
    ("uk_obr_tables", 2567): (9, "0.0", "0"),
    ("uk_obr_tables", 2568): (10, "0.0", "0"),
    ("uk_obr_tables", 2569): (11, "0.0", "0"),
    ("uk_obr_tables", 2576): (2184, "0.0", "0"),
    ("uk_obr_tables", 2577): (2185, "1.1", "-1058"),
    ("uk_obr_tables", 2578): (2186, "1.1", "-1113"),
    ("uk_obr_tables", 2579): (2187, "1.1", "-1132"),
    ("uk_obr_tables", 2580): (2188, "1.2", "-1151"),
    ("uk_obr_tables", 2581): (2189, "1.2", "-1169"),
    ("uk_obr_tables", 2630): (2502, "7.6", "-7,597"),
    ("uk_obr_tables", 2631): (2503, "2.5", "-2,475"),
    ("uk_obr_tables", 2632): (2504, "-0.7", "732"),
    ("uk_obr_tables", 2633): (2505, "-5.2", "5,192"),
    ("uk_obr_tables", 2634): (2506, "-6.1", "6,134"),
    ("uk_obr_tables", 2635): (2507, "-7.3", "7,349"),
    ("uk_obr_tables", 2636): (2508, "0.0", "0"),
    ("uk_obr_tables", 2637): (2509, "1.1", "-1,058"),
    ("uk_obr_tables", 2638): (2510, "1.1", "-1,113"),
    ("uk_obr_tables", 2639): (2511, "1.1", "-1,132"),
    ("uk_obr_tables", 2640): (2512, "1.2", "-1,151"),
    ("uk_obr_tables", 2641): (2513, "-4.3", "4,331"),
    ("uk_obr_tables", 2655): (2570, "£5 billion", "5.4"),
    ("uk_obr_tables", 2667): (1167, "£0.7 billion", "688"),
    ("uk_obr_tables", 2672): (1005, "£0.8 billion", "802"),
    ("uk_obr_tables", 2673): (1347, "£0.3 billion", "253"),
    ("uk_obr_tables", 2674): (537, "£0.3 billion", "-261"),
    ("uk_obr_tables", 2680): (18, "£0.7 billion", "-734"),
    ("uk_obr_tables", 2681): (19, "£0.3 billion", "-296"),
    ("uk_obr_tables", 2712): (943, "-164", "164"),
    ("uk_obr_tables", 2713): (944, "-318", "318"),
    ("uk_obr_tables", 2714): (945, "-270", "270"),
    ("uk_obr_tables", 2715): (946, "-250", "250"),
    ("uk_obr_tables", 2716): (947, "-264", "264"),
    ("uk_rf_ab2026", 28): (74, "under £145", "£145"),
    ("uk_rf_ab2026", 29): (76, "over £130", "£130"),
    ("uk_rf_ab2026", 41): (49, "3 per cent", "3.0 per cent"),
    ("uk_rf_ab2026", 48): (130, "just over half", "52 per cent"),
    ("uk_rf_ab2026", 54): (34, "£4.4 billion", "£4.4 billion"),
    ("uk_rf_ab2026", 58): (383, "over a million", "1572152"),
    ("uk_rf_ab2026", 59): (379, "91 per cent", "0.90648359700588743"),
    ("uk_rf_ab2026", 60): (765, "2.6 percentage points", "-2.6014506816864014"),
    ("uk_rf_ab2026", 61): (56, "£158", "£158"),
    ("uk_rf_ab2026", 63): (57, "£144", "£144"),
    ("uk_rf_ab2026", 77): (382, "76 per cent", "0.76228673788146883"),
    ("uk_rf_ab2026", 93): (47, "£3.7 billion", "£3.7 billion"),
    ("uk_rf_ab2026", 127): (34, "£4.4 billion", "£4.4 billion"),
    ("uk_rf_ab2026", 133): (4, "around one-in-eight", "around one-in-eight"),
    ("uk_rf_ab2026", 137): (383, "over a million", "1572152"),
    ("uk_rf_ab2026", 138): (379, "91 per cent", "0.90648359700588743"),
    ("uk_rf_ab2026", 147): (433, "-£2.0bn", "-2.003759382381924"),
    ("uk_rf_ab2026", 148): (434, "-£0.7bn", "-0.66114480370056317"),
    ("uk_rf_ab2026", 149): (435, "+£1.5bn", "1.4700235532486525"),
    ("uk_rf_ab2026", 150): (436, "+£1.9bn", "1.8860311488670831"),
    ("uk_rf_ab2026", 151): (437, "+£2.7bn", "2.6523035758874194"),
    ("uk_rf_ab2026", 153): (12, "around £20 billion", "around £20 billion"),
    ("uk_rf_ab2026", 177): (13, "£2 billion", "£2 billion"),
    ("uk_rf_ab2026", 198): (633, "1.8 per cent", "1.835872215777723E-2"),
    ("uk_rf_ab2026", 200): (631, "5.0 per cent", "5.0346160874108259E-2"),
    ("uk_rf_ab2026", 205): (765, "2.6 percentage points", "-2.6014506816864014"),
    ("uk_rf_ab2026", 208): (763, "+0.8ppts", "0.83668380975723267"),
    ("uk_rf_ab2026", 209): (764, "-0.4ppts", "-0.41938871145248413"),
    ("uk_tpa", 2): (104, "about £6bn", "5.9"),
    ("uk_tpa", 4): (27, "£19bn", "£19.1bn"),
    ("uk_tpa", 8): (6, "about £1bn", "£1.1bn"),
    ("uk_tpa", 168): (25, "£0.7bn", "£700m"),
    ("uk_tpa", 176): (166, "-0.49", "-0.49"),
    ("uk_tpa", 194): (163, "-0.29", "-0.29"),
    ("uk_tpa", 206): (158, "0.38", "0.38"),
    ("uk_tpa", 212): (160, "0.155", "0.155"),
    ("uk_tpa", 224): (157, "0.63", "0.63"),
    ("uk_tpa", 264): (27, "£19.1bn", "£19.1bn"),
}


def _kept_row(family, k):
    return k if isinstance(k, tuple) else (family, k)


def test_each_repeated_printing_pairs_the_rows_we_read():
    assert set(I.REPEATED_PRINTINGS) == set(REPEATED_PINS)
    for (family, i), (k, repeat, kept) in REPEATED_PINS.items():
        assert I.REPEATED_PRINTINGS[(family, i)][0] == k, (family, i)
        assert len(I.REPEATED_PRINTINGS[(family, i)][1]) > 40, (family, i)
        kept_family, kept_row = _kept_row(family, k)
        assert RAW[family][i]["value_raw"] == repeat, (family, i)
        assert RAW[kept_family][kept_row]["value_raw"] == kept, (family, i)


@pytest.mark.parametrize("entry", sorted(REPEATED_PINS))
def test_a_repeated_printing_merges_into_the_printing_we_keep(entry):
    family, i = entry
    k, repeat, kept = REPEATED_PINS[entry]
    kept_family, kept_row = _kept_row(family, k)
    families = {family: [(i, RAW[family][i])]}
    families.setdefault(kept_family, []).append((kept_row, RAW[kept_family][kept_row]))
    [claim], acct = I.stage(families)
    assert (acct["read"], acct["ingested"], acct["dropped"]) == (2, 1, 1)
    assert acct["drops"]["figure_printed_again"]["rows"] == 1
    assert acct["by_family"][family]["drops"]["figure_printed_again"] == 1
    assert claim.publication["family"] == kept_family
    assert claim.conditions["value_verbatim"] == kept
    assert (
        claim.publication["locator"]
        == RAW[kept_family][kept_row]["publication"]["locator"]
    )
    row = RAW[family][i]
    assert claim.publication["also_printed_in"] == [
        {
            "family": family,
            "table": row.get("source_table"),
            "locator": row["publication"].get("locator"),
            "source_column": row.get("source_column") or None,
            "value_verbatim": repeat,
        }
    ]


def test_each_repeated_printing_leaves_one_claim(staged):
    """The full ingest drops each repeat once, in the repeat's family, and
    lists it on the claim it keeps. On HM Treasury's table claims it lists only
    their costings and red book twins, so we leave those claims out."""
    scores, acct = staged
    assert acct["drops"]["figure_printed_again"]["rows"] == len(REPEATED_PINS) == 176
    for family, n in Counter(f for f, _ in REPEATED_PINS).items():
        assert acct["by_family"][family]["drops"]["figure_printed_again"] == n
    listed = [
        (s.publication["family"], t["family"], t["value_verbatim"])
        for s in scores
        if s.publication["family"] != "uk_hmt_tables"
        for t in s.publication.get("also_printed_in", [])
    ]
    assert sorted(listed) == sorted(
        (_kept_row(family, k)[0], family, repeat)
        for (family, _), (k, repeat, _) in REPEATED_PINS.items()
    )


# Two claims that we pair in the scan below but keep apart: (family,
# locator, period, printed value) of each, sorted -> why both stay claims.
_HMT_PACKAGE = (
    "HM Treasury costs two different measures of one package at the same amount "
    "in this year, and we stage both under one reform key."
)
_OBR_TAX_GAP_ZERO = (
    "The OBR prints zero in this year for two different parts of the "
    "government's package of measures to close the tax gap."
)
NOT_REPEATS: dict[tuple, str] = {
    (
        ("uk_centax", "p. 22, section 3.3", 2030, "4%"),
        ("uk_centax", "p. 22, section 3.3", 2030, "4%"),
    ): (
        "CenTax estimates that the bottom 50% would pay 4% of the additional "
        "revenue from taxing each of two kinds of income more: savings, and "
        "other non-dividend investment income."
    ),
    **dict.fromkeys(
        [
            (
                ("uk_hmt_costings", "p.33 (Exchequer impact (£m))", 2027, "+0m"),
                ("uk_hmt_costings", "p.34 (Exchequer impact (£m))", 2027, "+0m"),
            ),
            (
                ("uk_hmt_costings", "p.33 (Exchequer impact (£m))", 2029, "+0m"),
                ("uk_hmt_costings", "p.34 (Exchequer impact (£m))", 2029, "+0m"),
            ),
            (
                ("uk_hmt_costings", "p.54 (Exchequer impact (£m))", 2027, "+0m"),
                ("uk_hmt_costings", "p.55 (Exchequer impact (£m))", 2027, "+0m"),
            ),
            (
                ("uk_hmt_costings", "p.54 (Exchequer impact (£m))", 2027, "+0m"),
                ("uk_hmt_costings", "p.58 (Exchequer impact (£m))", 2027, "+0m"),
            ),
            (
                ("uk_hmt_costings", "p.54 (Exchequer impact (£m))", 2031, "+40m"),
                ("uk_hmt_costings", "p.55 (Exchequer impact (£m))", 2031, "+40m"),
            ),
            (
                ("uk_hmt_costings", "p.55 (Exchequer impact (£m))", 2027, "+0m"),
                ("uk_hmt_costings", "p.58 (Exchequer impact (£m))", 2027, "+0m"),
            ),
            (
                ("uk_hmt_costings", "p.55 (Exchequer impact (£m))", 2029, "+0m"),
                ("uk_hmt_costings", "p.58 (Exchequer impact (£m))", 2029, "+0m"),
            ),
            (
                ("uk_hmt_costings", "p.56 (Exchequer impact (£m))", 2027, "-5m"),
                ("uk_hmt_costings", "p.57 (Exchequer impact (£m))", 2027, "-5m"),
            ),
            (
                ("uk_hmt_costings", "p.67 (Exchequer impact (£m))", 2027, "+0m"),
                ("uk_hmt_costings", "p.68 (Exchequer impact (£m))", 2027, "+0m"),
            ),
            (
                ("uk_hmt_costings", "p.92 (Exchequer impact (£m))", 2027, "+0m"),
                ("uk_hmt_costings", "p.93 (Exchequer impact (£m))", 2027, "+0m"),
            ),
            (
                ("uk_hmt_costings", "p.92 (Exchequer impact (£m))", 2028, "-2m"),
                ("uk_hmt_costings", "p.93 (Exchequer impact (£m))", 2028, "-2m"),
            ),
            (
                ("uk_hmt_costings", "p.92 (Exchequer impact (£m))", 2031, "+0m"),
                ("uk_hmt_costings", "p.93 (Exchequer impact (£m))", 2031, "+0m"),
            ),
            (
                ("uk_hmt_costings", "p.92 (Exchequer impact (£m))", 2032, "+0m"),
                ("uk_hmt_costings", "p.93 (Exchequer impact (£m))", 2032, "+0m"),
            ),
        ],
        _HMT_PACKAGE,
    ),
    **dict.fromkeys(
        [
            (
                (
                    "uk_obr_tables",
                    "Table 3.1 (p.61), Timely payment for self-assessment, 2026-27",
                    2027,
                    "0.0",
                ),
                (
                    "uk_obr_tables",
                    "sheet '1.1'; Table 1.1; measure 45; Receipts / Alcohol duty; 2026-27; cell I204",
                    2027,
                    "0",
                ),
            ),
            (
                (
                    "uk_obr_tables",
                    "Table 3.1 (p.61), Timely payment for self-assessment, 2026-27",
                    2027,
                    "0.0",
                ),
                (
                    "uk_obr_tables",
                    "sheet '1.1'; Table 1.1; measure 45; Receipts / Capital gains tax; 2026-27; cell I198",
                    2027,
                    "0",
                ),
            ),
            (
                (
                    "uk_obr_tables",
                    "Table 3.1 (p.61), Timely payment for self-assessment, 2026-27",
                    2027,
                    "0.0",
                ),
                (
                    "uk_obr_tables",
                    "sheet '1.1'; Table 1.1; measure 45; Receipts / Vehicle excise duty; 2026-27; cell I206",
                    2027,
                    "0",
                ),
            ),
            (
                (
                    "uk_obr_tables",
                    "Table 3.1 (p.61), Timely payment for self-assessment, 2027-28",
                    2028,
                    "0.0",
                ),
                (
                    "uk_obr_tables",
                    "Table 3.3 (p.72), Direct recovery of debt, 2027-28",
                    2028,
                    "0",
                ),
            ),
            (
                (
                    "uk_obr_tables",
                    "Table 3.1 (p.61), Timely payment for self-assessment, 2027-28",
                    2028,
                    "0.0",
                ),
                (
                    "uk_obr_tables",
                    "sheet '1.1'; Table 1.1; measure 45; Receipts / Capital gains tax; 2027-28; cell J198",
                    2028,
                    "0",
                ),
            ),
            (
                (
                    "uk_obr_tables",
                    "Table 3.1 (p.61), Timely payment for self-assessment, 2028-29",
                    2029,
                    "0.0",
                ),
                (
                    "uk_obr_tables",
                    "sheet '1.1'; Table 1.1; measure 45; Current AME / Scottish BGA (current); 2028-29; cell K208",
                    2029,
                    "0",
                ),
            ),
            (
                (
                    "uk_obr_tables",
                    "Table 3.3 (p.72), Direct recovery of debt, 2027-28",
                    2028,
                    "0",
                ),
                (
                    "uk_obr_tables",
                    "sheet '1.1'; Table 1.1; measure 45; Receipts / Capital gains tax; 2027-28; cell J198",
                    2028,
                    "0",
                ),
            ),
        ],
        _OBR_TAX_GAP_ZERO,
    ),
    (
        ("uk_obr_tables", "para 3.13 (p.65)", 2032, "£0.4 billion"),
        (
            "uk_obr_tables",
            "sheet '1.1'; Table 1.1; measure 45; Receipts / Onshore CT; 2031-32; cell N201",
            2032,
            "445",
        ),
    ): (
        "In paragraph 3.13 the OBR costs the changes to HMRC's compliance "
        "workforce, one part of the tax-gap package, at £0.4 billion in 2031-32. "
        "In Table 1.1 it prints the whole package's onshore corporation tax, 445 "
        "(£ million)."
    ),
    (
        (
            "uk_obr_tables",
            "Table 3.3 (p.72), Property income tax rate increase, 2027-28",
            2028,
            "-2",
        ),
        (
            "uk_obr_tables",
            "sheet '1.1'; Table 1.1; measure 61; Receipts / Onshore CT; 2027-28; cell J298",
            2028,
            "2",
        ),
    ): (
        "Under the property income measure's tax head in Table 3.3, the OBR sums "
        "the measure's receipts. In 2027-28 it prints zero on the measure's income "
        "tax line in Table 1.1, so the sum equals the onshore corporation tax "
        "line, 2 (£ million)."
    ),
    (
        ("uk_tpa", "footnote 5", 2028, "£700m"),
        (
            "uk_tpa",
            "series[7] 'Healey Oct 2026 Budget', data[3] (2027-28)",
            2028,
            "0.7",
        ),
    ): (
        "In footnote 5 Tax Policy Associates sums HM Treasury's 2027-28 tax "
        "costings to £700m in cash. On its chart of tax rises by fiscal event it "
        "plots the OBR's costings in 2026 money, and puts that year's total at "
        "£0.7bn too."
    ),
}

_PRINTED = re.compile(r"(\d[\d,]*)(?:\.(\d+))?(?:[eE]([+-]?\d+))?")


def _last_digit(s):
    """Return the place of a printing's last digit in claim units, which we
    compute apart from I._printed_place. For a printing without digits, or a
    value of zero, we return 0."""
    m = _PRINTED.search(s.conditions.get("value_verbatim") or "")
    if not m or not s.value:
        return 0.0
    number = float(m[1].replace(",", "") + "." + (m[2] or "0")) * 10 ** int(m[3] or 0)
    if not number:
        return 0.0
    return 10.0 ** (int(m[3] or 0) - len(m[2] or "")) * abs(s.value) / number


def _oriented(s):
    relation, _ = signs.classify(
        {
            "metric": s.metric.value,
            "conditions": s.conditions,
            "country": "UK",
            "source": s.source,
        }
    )
    if relation in (signs.SAME, signs.OPPOSITE):
        return signs.external_value_pe_sign(s.value, relation)
    return abs(s.value)


def _one_table(a, b):
    """Whether the producer prints both claims in one table. We read two lines
    of one table as two figures."""
    pa, pb = a.publication, b.publication
    return (
        pa["family"] == pb["family"]
        and pa.get("table") is not None
        and pa.get("table") == pb.get("table")
    )


def _differ_in_scope(a, b):
    """Whether two claims cover different places, housing cost bases, income
    groups or averaging windows. We compare geography and housing costs where
    both claims state them, read a claim without an income group as covering
    everyone, and read one without an aggregation as a single year's figure."""
    ca, cb = a.conditions, b.conditions
    if any(
        k in ca and k in cb and ca[k] != cb[k] for k in ("geography", "housing_costs")
    ):
        return True
    return (ca.get("income_group", "all"), ca.get("aggregation")) != (
        cb.get("income_group", "all"),
        cb.get("aggregation"),
    )


def test_no_claim_repeats_another_printing_of_its_figure(staged):
    """We pair the ingest's claims by a rule we wrote apart from
    I.REPEATED_PRINTINGS. We treat two claims as one figure that the producer
    prints twice when they share a source, reform, metric, unit, year, time
    basis and window, and their values, zeros included, agree to half the
    coarser printing's last digit. We also require that the producer cost part
    of a measure in both, or the whole measure in both. We skip two lines of
    one table and two claims that differ in scope, and for each other pair
    that the ingest keeps, we give our reason in NOT_REPEATS."""
    scores, _ = staged
    groups: dict[tuple, list] = {}
    for s in scores:
        key = (
            s.source,
            s.reform.key(),
            s.metric,
            s.unit_concept,
            s.period,
            s.time_basis,
            s.period_start,
            s.period_end,
            s.conditions.get("row_type") == "measure_component",
        )
        groups.setdefault(key, []).append(s)
    hits = set()
    for group in groups.values():
        for x, a in enumerate(group):
            for b in group[x + 1 :]:
                if a.value is None or b.value is None:
                    continue
                if _one_table(a, b) or _differ_in_scope(a, b):
                    continue
                if (
                    abs(_oriented(a) - _oriented(b))
                    > max(_last_digit(a), _last_digit(b)) / 2 + 1e-9
                ):
                    continue
                hits.add(
                    tuple(
                        sorted(
                            (
                                s.publication["family"],
                                str(s.publication.get("locator")),
                                s.period,
                                s.conditions.get("value_verbatim"),
                            )
                            for s in (a, b)
                        )
                    )
                )
    assert hits == set(NOT_REPEATS), (
        sorted(hits - set(NOT_REPEATS)),
        sorted(set(NOT_REPEATS) - hits),
    )
    assert all(len(why) > 40 for why in NOT_REPEATS.values())


def test_the_merge_never_leaves_a_same_claim_twin(monkeypatch):
    """RF prints row 60's figure again on row 205. Without row 60's entry, the
    ingest would merge row 205 into row 765 and keep row 60, whose claim
    shares row 205's id, so it raises."""
    monkeypatch.delitem(I.REPEATED_PRINTINGS, ("uk_rf_ab2026", 60))
    rows = [(i, RAW["uk_rf_ab2026"][i]) for i in (60, 205, 765)]
    with pytest.raises(ValueError, match="shares its id with a repeat we dropped"):
        I.stage({"uk_rf_ab2026": rows})


def test_a_repeat_that_shares_its_kept_claim_s_id_merges():
    """Review of #256, L3: if we staged row 25 with row 1's conditions, the
    two claims would share an id. The ingest merges row 25 into row 1 and
    keeps that one claim, so the twin guard lets it through."""
    rows = {i: copy.deepcopy(RAW["uk_centax"][i]) for i in (1, 25)}
    rows[25]["conditions"] = copy.deepcopy(rows[1]["conditions"])
    [claim], acct = I.stage({"uk_centax": sorted(rows.items())})
    assert acct["drops"]["figure_printed_again"]["rows"] == 1
    assert claim.publication["locator"] == rows[1]["publication"]["locator"]


def test_a_full_ingest_raises_when_a_printing_goes_missing(monkeypatch):
    monkeypatch.setitem(I.REPEATED_PRINTINGS, ("uk_tpa", 999_999), (27, "x" * 41))
    with pytest.raises(ValueError, match="uk_tpa row 999999 or its kept row 27"):
        I.stage()


@functools.cache
def _staged_alone(family, i):
    [s], _ = I.stage({family: [(i, RAW[family][i])]})
    return s


def _claim(family, i):
    return copy.deepcopy(_staged_alone(family, i))


# RF's fuel freeze path for 2027-28, which RF rounds on its chart's label and
# gives in full in its workbook.
FREEZE_LABEL = ("uk_rf_ab2026", 147)
FREEZE_CELL = ("uk_rf_ab2026", 433)


def _printing(s, printed, value):
    s = copy.deepcopy(s)
    s.conditions["value_verbatim"] = printed
    s.value = float(value)
    return s


@settings(max_examples=300, deadline=None)
@given(
    cell=st.integers(-9_999_999, 9_999_999).filter(bool),
    label=st.integers(-99, 99).filter(bool),
)
@example(cell=100_000, label=1)
@example(cell=150_000, label=1)
@example(cell=150_001, label=1)
@example(cell=-100_000, label=1)
def test_a_rounded_printing_agrees_only_to_half_its_last_digit(cell, label):
    """We print the cell in £bn to six places (cell / 10**6) and the label to
    one (label / 10). The ingest accepts the pair exactly when they differ by
    at most £50 million. In the first example we print £0.1 billion in both
    places, so only the precision check stops us keeping the label. In the
    second, the two values differ by exactly £50 million, and in the third by
    £1,000 more. In the fourth, they match in size and differ in sign."""
    label_claim, cell_claim = _claim(*FREEZE_LABEL), _claim(*FREEZE_CELL)
    kept = _printing(cell_claim, f"{cell / 10**6:.6f}", cell * 1_000)
    repeat = _printing(label_claim, f"£{abs(label) / 10:.1f}bn", label * 100_000_000)
    agree = abs(cell * 1_000 - label * 100_000_000) <= 50_000_000
    if agree:
        I._check_printing("uk_rf_ab2026", 147, repeat, kept)
    else:
        with pytest.raises(ValueError, match="no longer matches"):
            I._check_printing("uk_rf_ab2026", 147, repeat, kept)
    # we never keep the coarser printing
    with pytest.raises(ValueError, match="no longer matches"):
        I._check_printing("uk_rf_ab2026", 147, kept, repeat)


@pytest.mark.parametrize(
    "change",
    [
        lambda s: setattr(s, "source", "another_producer"),
        lambda s: setattr(s, "reform", ReformRef("policy_ref", {"policy": "another"})),
        lambda s: setattr(s, "metric", Metric.POVERTY_RATE_CHANGE),
        lambda s: setattr(s, "unit_concept", UnitConcept.PERSONS),
        lambda s: setattr(s, "period", s.period + 1),
        lambda s: setattr(s, "time_basis", TimeBasis.POINT_IN_TIME),
        lambda s: setattr(s, "period_start", s.period - 1),
        lambda s: setattr(s, "period_end", s.period + 1),
        lambda s: s.conditions.update(row_type="measure_component"),
        lambda s: s.conditions.update(estimate_kind="range_high"),
        lambda s: s.conditions.update(estimate_kind="cumulative"),
    ],
    ids=[
        "source",
        "reform",
        "metric",
        "unit",
        "year",
        "time_basis",
        "window_start",
        "window_end",
        "part_of_a_measure",
        "kept_bound",
        "estimate_kind",
    ],
)
def test_a_printing_of_another_figure_raises(change):
    """We change one field of the workbook's claim for RF's 2027-28 fuel
    freeze path, which RF also labels on its chart. After each change we read
    the claim as another figure, so the ingest raises."""
    repeat, kept = _claim(*FREEZE_LABEL), _claim(*FREEZE_CELL)
    I._check_printing("uk_rf_ab2026", 147, repeat, kept)
    change(kept)
    with pytest.raises(ValueError, match="no longer matches"):
        I._check_printing("uk_rf_ab2026", 147, repeat, kept)


@pytest.mark.parametrize(
    "key",
    [
        "geography",
        "income_group",
        "unit_population",
        "subgroup",
        "denominator",
        "statistic",
        "housing_costs",
        "component",
        "aggregation",
        "horizon",
        "price_basis",
    ],
)
def test_a_printing_in_another_scope_raises(key):
    """We give one scope key of the workbook's claim for RF's fuel freeze path a
    wording that we don't list in ``_SAME_SCOPE``, so the ingest raises. We name
    the keys here, apart from ``_SCOPE``, so that dropping one from ``_SCOPE``
    fails a test."""
    repeat, kept = _claim(*FREEZE_LABEL), _claim(*FREEZE_CELL)
    I._check_printing("uk_rf_ab2026", 147, repeat, kept)
    kept.conditions[key] = "a wording we don't list"
    with pytest.raises(ValueError, match="no longer matches"):
        I._check_printing("uk_rf_ab2026", 147, repeat, kept)


def test_we_list_only_the_wordings_that_repeats_use():
    """We list in ``_SAME_SCOPE`` each pair of wordings on which a repeat and
    the claim we keep differ, and no others, so a stale pair can't let another
    figure through."""
    used = set()
    for (family, i), (k, _) in I.REPEATED_PRINTINGS.items():
        repeat, kept = _claim(family, i), _claim(*_kept_row(family, k))
        first, second = (
            {key: s.conditions.get(key, I._UNSTATED.get(key)) for key in I._SCOPE}
            for s in (repeat, kept)
        )
        used |= {
            (key, first[key], second[key])
            for key in I._SCOPE
            if first[key] != second[key]
        }
    assert used == I._SAME_SCOPE


# Each bound a producer prints, the point value we keep for it, and a
# printing of that point outside the bound: (family, bound row, point row) ->
# (printed, value)
OUTSIDE_THE_BOUND = {
    ("uk_rf_ab2026", 28, 74): ("£146", 146),  # under £145
    ("uk_rf_ab2026", 29, 76): ("£129", 129),  # over £130
    ("uk_rf_ab2026", 48, 130): ("49 per cent", 0.49),  # just over half
    ("uk_rf_ab2026", 58, 383): ("999000", 999_000),  # over a million
    ("uk_centax", 65, 66): ("0.60%", 0.006),  # less than 0.5%
}


@pytest.mark.parametrize("entry", sorted(OUTSIDE_THE_BOUND))
def test_a_bound_merges_only_into_a_point_value_within_it(entry):
    """Review of #256, M2: we keep the point value, and the ingest raises if
    it lies more than half its last digit past the bound."""
    family, i, k = entry
    bound, point = _claim(family, i), _claim(family, k)
    assert bound.conditions["estimate_kind"] in ("range_low", "range_high")
    assert point.conditions.get("estimate_kind") not in ("range_low", "range_high")
    I._check_printing(family, i, bound, point)
    with pytest.raises(ValueError, match="no longer matches"):
        I._check_printing(family, i, bound, _printing(point, *OUTSIDE_THE_BOUND[entry]))


@pytest.mark.parametrize(
    "entry, inside, outside",
    [
        (
            ("uk_rf_ab2026", 48, 130),
            ("over 52.4 per cent", 0.524),
            ("over 52.6 per cent", 0.526),
        ),
        (("uk_rf_ab2026", 28, 74), ("under £144.6", 144.6), ("under £144.4", 144.4)),
    ],
)
def test_a_point_value_agrees_with_a_bound_its_rounding_could_meet(
    entry, inside, outside
):
    """RF prints 52 per cent, which stands for any share from 51.5 to 52.5
    per cent, so it agrees with a bound of over 52.4 per cent but not with
    one of over 52.6 per cent. In the same way £145 agrees with a bound of
    under £144.6 but not with one of under £144.4."""
    family, i, k = entry
    bound, point = _claim(family, i), _claim(family, k)
    I._check_printing(family, i, _printing(bound, *inside), point)
    with pytest.raises(ValueError, match="no longer matches"):
        I._check_printing(family, i, _printing(bound, *outside), point)


@pytest.mark.parametrize(
    "entry, bound_printing, point_printing",
    [
        (("uk_rf_ab2026", 48, 130), ("over 3.5 per cent", 0.035), ("3 per cent", 0.03)),
        (("uk_centax", 65, 66), ("less than 4.5%", 0.045), ("5%", 0.05)),
    ],
)
def test_a_point_half_its_last_digit_past_a_bound_agrees(
    entry, bound_printing, point_printing
):
    """A producer could print 3 per cent for any share up to 3.5 per cent, so
    that printing agrees with a bound of over 3.5 per cent. In the same way, 5%
    agrees with a bound of less than 4.5%. In binary floating point, 0.03 + 0.005
    falls short of 0.035 and 0.05 - 0.005 exceeds 0.045, so the ingest allows a
    few units in the last place here too."""
    family, i, k = entry
    bound = _printing(_claim(family, i), *bound_printing)
    point = _printing(_claim(family, k), *point_printing)
    I._check_printing(family, i, bound, point)


def test_a_bound_and_a_point_of_opposite_signs_raise():
    """RF bounds a typical household's gain under £145 and gives £145 in
    another printing. If RF printed the second as a loss, we could no longer
    read the bound against it."""
    bound, point = _claim("uk_rf_ab2026", 28), _claim("uk_rf_ab2026", 74)
    I._check_printing("uk_rf_ab2026", 28, bound, point)
    point.conditions["sign_convention"] = "positive = loss to households"
    point.value = -point.value
    point.conditions["value_verbatim"] = "-£145"
    with pytest.raises(ValueError, match="no longer matches"):
        I._check_printing("uk_rf_ab2026", 28, bound, point)


def test_two_bounds_merge_only_in_the_same_direction():
    """HM Treasury counts up to 20 million households in two printings, and we
    merge one into the other. If it printed at least 20 million in one of them,
    the two would bound the count from opposite sides, so the ingest raises."""
    repeat, kept = _claim("uk_hmt_redbook", 180), _claim("uk_hmt_redbook", 7)
    assert {s.conditions["estimate_kind"] for s in (repeat, kept)} == {"range_high"}
    I._check_printing("uk_hmt_redbook", 180, repeat, kept)
    kept.conditions["estimate_kind"] = "range_low"
    with pytest.raises(ValueError, match="no longer matches"):
        I._check_printing("uk_hmt_redbook", 180, repeat, kept)


def test_a_share_half_a_point_from_its_rounding_agrees():
    """Review of #256, L2: 58% and 57.5% differ by exactly half of 58%'s
    last digit. In binary floating point, 0.58 - 0.575 =
    0.0050000000000000044, so the ingest allows a few units in the last place
    of each value."""
    repeat, kept = _claim("uk_centax", 62), _claim("uk_centax", 82)
    assert repeat.conditions["value_verbatim"] == "58%"
    I._check_printing("uk_centax", 62, repeat, _printing(kept, "57.5%", 0.575))
    with pytest.raises(ValueError, match="no longer matches"):
        I._check_printing("uk_centax", 62, repeat, _printing(kept, "57.4%", 0.574))


def test_a_printing_of_the_opposite_sign_raises():
    """The OBR prints Founders' Relief's 2029-30 effect as a £0.3 billion cut
    in receipts in paragraph 3.18 and as -261 in Table 1.1, where it prints a
    loss to the Exchequer as negative. If the OBR printed +261 there, a gain,
    the two printings would agree in size and differ in direction."""
    repeat, kept = _claim("uk_obr_tables", 2674), _claim("uk_obr_tables", 537)
    assert kept.conditions["value_verbatim"] == "-261"
    I._check_printing("uk_obr_tables", 2674, repeat, kept)
    kept.value = -kept.value
    kept.conditions["value_verbatim"] = "261"
    with pytest.raises(ValueError, match="no longer matches"):
        I._check_printing("uk_obr_tables", 2674, repeat, kept)


@pytest.mark.parametrize("marks", [(True, False), (False, True), (True, True)])
def test_a_printing_with_its_direction_in_its_label_agrees_in_size(marks):
    """We flip the sign of the workbook's claim for RF's fuel freeze path, so
    the ingest raises. Then we mark one printing or both as giving its direction
    in its label, as ``signs.classify`` reads it. The ingest can't orient that
    printing, so it compares the two magnitudes and accepts the pair."""
    repeat, kept = _claim(*FREEZE_LABEL), _claim(*FREEZE_CELL)
    kept.value = -kept.value
    with pytest.raises(ValueError, match="no longer matches"):
        I._check_printing("uk_rf_ab2026", 147, repeat, kept)
    for s, mark in zip((repeat, kept), marks):
        if mark:
            s.conditions["sign_convention"] = signs.MAGNITUDE_CONVENTION
    I._check_printing("uk_rf_ab2026", 147, repeat, kept)


_AFFIXES = st.sampled_from([("", ""), ("£", ""), ("£", " billion"), ("", "%")])


@settings(max_examples=500, deadline=None)
@given(
    whole=st.integers(1, 999_999),
    places=st.integers(0, 6),
    data=st.data(),
    power=st.integers(-6, 12),
    commas=st.booleans(),
    affixes=_AFFIXES,
)
def test_the_last_printed_digit_sets_the_place(
    whole, places, data, power, commas, affixes
):
    fraction = data.draw(st.integers(0, 10**places - 1))
    digits = f"{whole:,}" if commas else str(whole)
    printed = digits + (f".{fraction:0{places}d}" if places else "")
    number = whole + fraction / 10**places
    s = SimpleNamespace(
        conditions={"value_verbatim": affixes[0] + printed + affixes[1]},
        value=-number * 10.0**power,
    )
    assert math.isclose(I._printed_place(s), 10.0 ** (power - places), rel_tol=1e-9), (
        printed
    )


@settings(max_examples=200, deadline=None)
@given(
    mantissa=st.integers(1, 9_999_999),
    exponent=st.integers(-4, 4),
    power=st.integers(-3, 9),
)
def test_a_workbook_exponent_moves_the_place(mantissa, exponent, power):
    """RF writes '1.835872215777723E-2' in its workbook, with the last digit
    at 10**-17."""
    text = f"{mantissa / 10**6:.6f}E{exponent}"
    s = SimpleNamespace(
        conditions={"value_verbatim": text},
        value=mantissa / 10**6 * 10.0**exponent * 10.0**power,
    )
    assert math.isclose(
        I._printed_place(s), 10.0 ** (power + exponent - 6), rel_tol=1e-9
    ), text


@settings(max_examples=200, deadline=None)
@given(
    number=st.integers(1, 999_999),
    factor=st.integers(2, 9),
    power=st.integers(-6, 12),
)
def test_a_value_off_its_printing_by_more_than_a_power_of_ten_raises(
    number, factor, power
):
    s = SimpleNamespace(
        conditions={"value_verbatim": f"£{number}"},
        value=number * factor * 10.0**power,
    )
    with pytest.raises(ValueError, match="doesn't match printed"):
        I._printed_place(s)


@pytest.mark.parametrize(
    "printed, value",
    [("over a million", 1_000_000.0), ("£0", 0.0), ("0.0", 0.0), ("£5", 0.0)],
)
def test_a_printing_without_digits_or_of_zero_has_no_place(printed, value):
    assert (
        I._printed_place(
            SimpleNamespace(conditions={"value_verbatim": printed}, value=value)
        )
        == 0.0
    )


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


def test_the_fuel_freeze_keeps_the_obrs_borrowing_and_receipts_figures(staged):
    """Keep both OBR quantities and apply #55's macro verdict to borrowing."""
    scores, _ = staged
    freeze = [
        s
        for s in scores
        if s.conditions.get("measure_key")
        == "ab2026_option__fuel_duty_continued_freeze"
    ]
    # RF derives its figures from the OBR's forecasts; keep both OBR estimates.
    assert len(freeze) == 2
    assert {s.source for s in freeze} == {"obr_efo"}
    by_metric = {s.metric: s for s in freeze}
    assert set(by_metric) == {
        Metric.DECISIONS_EFFECT_ON_BORROWING,
        Metric.REVENUE_CHANGE,
    }
    receipts = by_metric[Metric.REVENUE_CHANGE]
    assert (receipts.value, receipts.period) == (4_000_000_000, 2032)
    assert receipts.conditions["aggregation"] == "annual average 2027-28 to 2031-32"
    obr = by_metric[Metric.DECISIONS_EFFECT_ON_BORROWING]
    assert "staged_metric" not in obr.conditions
    assert obr.conditions["pe_expressibility"] == "not_expressible"
    assert obr.conditions["pe_missing"] == I.AB25.MACRO_MISSING
    assert obr.conditions["action_link"] == I.AB25.MACRO_LINK


LATEST_POLICY_WORLD = {
    "policy": "obr_october_2026_budget_forecast",
    "counterfactual": "policy_parameters",
}


def test_the_freeze_claims_score_against_the_obrs_latest_policy_world(staged):
    """Review of #255, M1: both OBR costings of a continued freeze take the
    registered latest-policy world, and every other OBR claim keeps its own."""
    scores, _ = staged
    obr = [s for s in scores if s.source == "obr_efo"]
    latest = [s for s in obr if s.reform.baseline == LATEST_POLICY_WORLD]
    assert sorted(s.publication["locator"] for s in latest) == [
        "para 3.43 (p.76)",
        "para 4.30 (p.96)",
    ]
    assert {s.conditions["measure_key"] for s in latest} == {
        "ab2026_option__fuel_duty_continued_freeze"
    }
    assert {s.conditions["baseline_policy"] for s in latest} == {
        "obr_october_2026_budget_forecast"
    }
    # we merge 57 of the pre-measures world's 2,702 claims into other
    # printings of their figures (REPEATED_PRINTINGS), so 2,645 remain
    assert Counter((s.reform.baseline or {}).get("policy") for s in obr) == {
        "obr_pre_measures_autumn_budget_2026": 2645,
        "obr_october_2026_budget_forecast": 2,
        "obr_fuel_duty_rpi_uprated_since_2010_11": 1,
        None: 7,
    }


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
    # the ingest keeps a repeat whose kept printing we left out of the sample
    repeats = {_staged_alone(*row).claim_id() for row in I.REPEATED_PRINTINGS}
    assert {s.claim_id() for s in scores} <= base_ids | repeats | {
        # and a twin whose Table 6.1 row we left out
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


# The conditions `_score`, `_verdict_conditions` and `with_baseline_condition`
# write beside the staged ones.
INGEST_CONDITIONS = {
    "action_link",
    "baseline_policy",
    "benchmark_class",
    "counterfactual",
    "country",
    "estimate_kind",
    "measure_key",
    "pe_expressibility",
    "pe_missing",
    "reform_hint",
    "staged_metric",
    "value_verbatim",
}


def _keeps_conditions(row, score):
    """Require each staged condition on the claim as staged. For a condition the
    ingest canonicalises, require the registered name and the staged text beside
    any name that differs. For a program we haven't registered, require the staged
    text alone. Refuse any condition neither the row nor the ingest supplies."""
    staged = row.get("conditions") or {}
    for key, value in staged.items():
        stored = score.conditions.get(key)
        verbatim = score.conditions.get(f"{key}_verbatim")
        if key == "program" and value not in known(row["source"], key):
            kept = stored is None and verbatim == value
        elif key == "program" or key in I.AB25._CANONICALISED:
            name = canon(row["source"], key, value)
            kept = stored == name and verbatim == (None if name == value else value)
        else:
            kept = stored == value
        if not kept:
            return False
    verbatim = {
        f"{key}_verbatim"
        for key in staged
        if key == "program" or key in I.AB25._CANONICALISED
    }
    allowed = set(staged) | verbatim | INGEST_CONDITIONS
    if "scoring_method" in score.conditions and "scoring_method" not in staged:
        if (
            row.get("proposed_metric") != "exchequer_impact_static"
            or score.conditions["scoring_method"] != "static"
        ):
            return False
        allowed.add("scoring_method")
    return set(score.conditions) <= allowed


_CHILDCARE = "free childcare entitlement (claimed and received some)"


@pytest.mark.parametrize(
    "row, stored",
    [
        (
            {"source": "centax", "conditions": {"program": _CHILDCARE}},
            {"program": "winter_fuel_payment"},
        ),
        (
            {"source": "centax", "conditions": {"program": _CHILDCARE}},
            {"program": "winter_fuel_payment", "program_verbatim": _CHILDCARE},
        ),
        (
            {"source": "centax", "conditions": {"program": _CHILDCARE}},
            {},
        ),
        (
            {"source": "ukmod", "conditions": {"program": "winter_fuel_allowance"}},
            {"program": "winter_fuel_payment"},
        ),
        (
            {"source": "ukmod", "conditions": {"program": "winter_fuel_allowance"}},
            {"program": "fuel", "program_verbatim": "winter_fuel_allowance"},
        ),
        (
            {"source": "centax", "conditions": {"basis": "forecast"}},
            {"basis": "outturn", "basis_verbatim": "forecast"},
        ),
        (
            {"source": "centax", "conditions": {"housing_costs": "BHC"}},
            {"housing_costs": "AHC", "housing_costs_verbatim": "BHC"},
        ),
        (
            {"source": "centax", "conditions": {"geography": "England"}},
            {"geography": "UK", "geography_verbatim": "England"},
        ),
        (
            {"source": "obr", "conditions": {"geography": "NI"}},
            {"geography": "Northern Ireland"},
        ),
        (
            {"source": "centax", "conditions": {"basis": "forecast"}},
            {"basis": "forecast", "housing_costs": "AHC"},
        ),
        (
            {"source": "centax", "conditions": {"basis": "forecast"}},
            {"basis": "forecast", "basis_verbatim": "forecast"},
        ),
        (
            {"source": "centax", "conditions": {"basis": "forecast"}},
            {"basis": "forecast", "geography_verbatim": "England"},
        ),
        (
            {
                "source": "centax",
                "proposed_metric": "exchequer_impact_static",
                "conditions": {},
            },
            {"scoring_method": "post_behavioural"},
        ),
    ],
)
def test_preservation_rejects_a_lost_or_invented_condition(row, stored):
    assert not _keeps_conditions(row, SimpleNamespace(conditions=stored))


@pytest.mark.parametrize(
    "row, stored",
    [
        (
            {"source": "centax", "conditions": {"program": _CHILDCARE}},
            {"program_verbatim": _CHILDCARE},
        ),
        (
            {"source": "ukmod", "conditions": {"program": "winter_fuel_allowance"}},
            {
                "program": "winter_fuel_payment",
                "program_verbatim": "winter_fuel_allowance",
            },
        ),
        (
            {"source": "centax", "conditions": {"basis": "forecast"}},
            {"basis": "forecast"},
        ),
        (
            {"source": "centax", "conditions": {"geography": "England"}},
            {"geography": "England"},
        ),
        (
            {"source": "obr", "conditions": {"geography": "NI"}},
            {"geography": "Northern Ireland", "geography_verbatim": "NI"},
        ),
        (
            {"source": "centax", "conditions": {"basis": "forecast"}},
            {"basis": "forecast", "country": "UK", "value_verbatim": "£1"},
        ),
    ],
)
def test_preservation_accepts_what_the_ingest_keeps(row, stored):
    assert _keeps_conditions(row, SimpleNamespace(conditions=stored))


@pytest.mark.parametrize(
    "name, verbatim",
    [("childcare", _CHILDCARE), (_CHILDCARE, None)],
)
def test_a_registered_program_keeps_its_text_beside_a_new_name(
    monkeypatch, name, verbatim
):
    """No staged program takes this path, so we register CenTax row 100's text."""
    registered = canon

    def canonical(source, axis, value):
        return name if axis == "program" else registered(source, axis, value)

    monkeypatch.setattr(I, "known", lambda source, axis: {_CHILDCARE})
    monkeypatch.setattr(I, "canon", canonical)
    row = RAW["uk_centax"][100]
    assert row["conditions"]["program"] == _CHILDCARE
    score = I._score(row, "uk_centax", row["source"], Metric.AFFECTED_SHARE)
    assert score.conditions["program"] == name
    assert score.conditions.get("program_verbatim") == verbatim


def test_a_centax_row_cannot_gain_an_unstaged_scoring_method():
    row = RAW["uk_centax"][100]
    assert "scoring_method" not in (row.get("conditions") or {})
    score = I._score(row, "uk_centax", row["source"], Metric.AFFECTED_SHARE)
    score.conditions["scoring_method"] = "static"
    assert not _keeps_conditions(row, score)


@pytest.mark.parametrize("method", [None, "post_behavioural"])
def test_a_static_exchequer_row_gains_its_scoring_method(method):
    """We staged no row under `exchequer_impact_static`, so we set it on an
    HM Treasury costings row and preserve any staged scoring method."""
    row = copy.deepcopy(
        next(
            r
            for r in RAW["uk_hmt_costings"]
            if "scoring_method" not in (r.get("conditions") or {})
        )
    )
    row["proposed_metric"] = "exchequer_impact_static"
    if method is not None:
        row.setdefault("conditions", {})["scoring_method"] = method
    score = I._score(row, "uk_hmt_costings", row["source"], Metric.REVENUE_CHANGE)
    assert score.conditions["scoring_method"] == (method or "static")
    assert _keeps_conditions(row, score)


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
    """We give red book row 11 table row 108's year; their keys already match,
    so only the ingest's magnitude check can raise."""
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
    """We grant the year exception for table row 252 alone and reject another
    row with the same key, magnitude and year."""
    table = copy.deepcopy(RAW["uk_hmt_tables"])
    table.append(copy.deepcopy(table[252]))
    monkeypatch.setattr(I, "_load", lambda family: table)
    _point_twin(monkeypatch, 263, len(table) - 1)
    with pytest.raises(ValueError, match="no longer matches"):
        I._check_row_calls("uk_hmt_redbook", RAW["uk_hmt_redbook"])


@pytest.mark.parametrize(
    "raw",
    [
        "in 2026-27, £2.6 billion",
        "£2.6bn",
        "2,600 million",
        "around £2.6 billion",
        "£2, million",
        "£2,6 billion",
        "£26,00 million",
        "£2600, million",
        "£1,2345 million",
        "£0,123 million",
        "£01 million",
        "£1234,567 million",
    ],
)
def test_a_reviewed_twin_printed_in_another_form_raises(raw):
    rows = copy.deepcopy(RAW["uk_hmt_redbook"])
    rows[6]["value_raw"] = raw
    with pytest.raises(ValueError, match="no printed amount"):
        I._check_row_calls("uk_hmt_redbook", rows)


@given(st.integers(0, 10**12), st.sampled_from(["million", "billion"]))
def test_a_printed_amount_reads_with_or_without_thousands_commas(number, unit):
    for digits in (str(number), f"{number:,}"):
        printed = I._PRINTED_AMOUNT.fullmatch(f"£{digits} {unit}")
        assert printed and int(printed[1].replace(",", "")) == number


@given(st.integers(1, 10**12), st.integers(0, 13))
def test_a_printed_amount_takes_commas_only_at_thousands(number, at):
    digits = str(number)
    comma = f"{digits[:at]},{digits[at:]}"
    assert (I._PRINTED_AMOUNT.fullmatch(f"£{comma} million") is not None) == (
        comma == f"{number:,}"
    )


@given(st.integers(1, 10**12))
def test_a_printed_amount_takes_no_leading_zero(number):
    assert I._PRINTED_AMOUNT.fullmatch(f"£0{number} million") is None
    assert I._PRINTED_AMOUNT.fullmatch(f"£0{number:,} million") is None


def test_a_reviewed_twin_whose_value_leaves_its_print_raises():
    """We cannot widen the ingest's tolerance by storing a value that differs
    from the printed amount."""
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


def test_a_four_place_decimal_prints_a_hundred_thousand_pound_unit():
    assert (
        I._printed_unit({"value": 1_234_500_000, "value_raw": "£1.2345 billion"})
        == 100_000
    )


@given(st.integers(1, 99_999), st.integers(0, 6), st.booleans())
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
