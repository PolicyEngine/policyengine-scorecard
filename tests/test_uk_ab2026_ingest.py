"""The Autumn Budget 2026 ingest (#230, tranche 2).

Every one of the 5,952 staged rows becomes a claim or a tallied drop. These
tests pin the ingest's invariants:

1. read = ingested + dropped, per family and in total, against COUNTS.json
   and ingest_uk_ab2026_expected.json, with a written reason for each drop;
2. every claim's key sits in the AB2026 registry, or for a Table 6.4
   recosting in the earlier event's, and carries that registry's verdict;
3. one claim per claim identity, and each HM Treasury figure counted once;
4. each claim's sign reads as signs.py reads it, pinned for every staged
   (metric, convention) pair and every pair the ingest's metric calls make;
5. the same claims from the same rows, run after run and in any row order;
6. AB2025's ingest gives the same output here as on origin/main.

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
    """The costings repeat 408 Table 6.1 cells and the red book 24; the
    ingest keeps each Table 6.1 claim and records its twins on it."""
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


def test_the_continued_fuel_duty_freeze_has_one_metric(staged):
    scores, _ = staged
    freeze = [
        s
        for s in scores
        if s.conditions.get("measure_key")
        == "ab2026_option__fuel_duty_continued_freeze"
    ]
    # RF derives its figure from the OBR's forecasts, so only the OBR's stays
    assert {s.source for s in freeze} == {"obr_efo"}
    assert {s.metric for s in freeze} == {Metric.REVENUE_CHANGE}
    obr = [s for s in freeze if s.source == "obr_efo"]
    assert [s.conditions["staged_metric"] for s in obr] == [
        "decisions_effect_on_borrowing"
    ]


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
out.write_text(json.dumps({
    "claims": dump("SELECT claim_id, source, metric, period, value, conditions, publication, baseline_key FROM external_scores"),
    "results": dump("SELECT claim_id, status, engine_version, pe_construction, annotations FROM pe_results"),
    "diagnoses": dump("SELECT * FROM diagnoses"),
    "lanes": dump("SELECT lane, stage, detail FROM lanes"),
}))
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
    for byte as on main. CI fetches origin/main, so there a missing ref
    fails; a local checkout without one skips."""
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
        ],
        cwd=ROOT,
        capture_output=True,
        check=True,
    ).stdout
    subprocess.run(["tar", "-x", "-C", str(main)], input=archive, check=True)
    theirs = _ab2025_dump(main, tmp_path / "main.json")
    ours = _ab2025_dump(ROOT, tmp_path / "ours.json")
    for table in ("claims", "results", "diagnoses", "lanes"):
        assert ours[table] == theirs[table], table


# --- value preservation ---------------------------------------------------------


def _staged_unit(row):
    unit = row.get("unit_concept") or row.get("proposed_unit")
    denominator = str((row.get("conditions") or {}).get("denominator", ""))
    if unit == "percent" and denominator.strip().lower() == "gdp":
        return "percent_of_gdp"
    return {"dwellings": "properties"}.get(unit, unit)


def test_every_claim_preserves_its_staged_row(staged):
    """Read each family's claims file directly, find the row behind each
    claim by its printed place and printed value, and require the claim to
    keep the producer's value, unit, statistic, time window and provenance.
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
            and _staged_unit(r) == s.unit_concept.value
            and (r.get("value_kind") or s.unit_concept.value) == s.value_kind
            and int(r["period"]) == s.period
            and r["time_basis"] == s.time_basis.value
            and r.get("quote") == s.publication.get("quote")
            and r.get("source_table") == s.publication.get("table")
            and r["attribution"] == s.publication.get("attribution")
            for r in found
        ), (fam, s.publication.get("locator"), s.value)
