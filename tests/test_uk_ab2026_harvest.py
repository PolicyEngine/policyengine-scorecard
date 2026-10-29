"""The Autumn Budget 2026 harvest (#230): vendored data, checked as data.

sources/harvest-uk-ab2026-2026-10-29/ stages every producer's AB2026 claims
before the tranche-2 ingest exists. These tests hold each staged row to the
row contract in that directory's README.md (the AB2025 contract with the
AB2026 exceptions): field names, closed enums, the FY-end-year period rule,
the fiscal_event slug, measure keys that exist in the AB2026 registry or, for
a Table 6.4 recosting, in the earlier event's registry, sha256-shaped
manifests, and per-family pins that the ingest's exact accounting will read.
"""

import gzip
import json
import re
from pathlib import Path

import pytest

from pipeline import ab2026_measure_keys as K
from pipeline.harvest_counts import counts

ROOT = Path(__file__).resolve().parent.parent
HARVEST = ROOT / "sources" / "harvest-uk-ab2026-2026-10-29"
UK = ROOT / "data" / "uk"


def _keys(path):
    return {m["measure_key"] for m in json.loads(path.read_text())["measures"]}


KEYS = _keys(UK / "ab2026_measures.json")
# A Table 6.4 recosting carries the earlier event's key (README rule 2).
# AB2025 has two key spaces: the #136 port registry and the events inventory.
EARLIER = {
    p.name.removesuffix("_measures.json"): _keys(p)
    for p in (UK / "events").glob("*_measures.json")
}
EARLIER["autumn_budget_2025"] |= _keys(UK / "ab2025_measures.json")

COUNTS = json.loads((HARVEST / "COUNTS.json").read_text())
FAMILIES = sorted(k for k in COUNTS if not k.startswith("_"))

REQUIRED = {
    "source",
    "source_model",
    "value",
    "value_raw",
    "normalization",
    "value_kind",
    "period",
    "time_basis",
    "conditions",
    "reform_hint",
    "measure_key",
    "attribution",
    "benchmark_class",
    "baseline_policy",
    "publication",
    "source_table",
    "source_column",
    "quote",
    "parse_confidence",
    "status",
}
OPTIONAL = {
    "metric",
    "proposed_metric",
    "unit_concept",
    "proposed_unit",
    "proposed_baseline",
    "note",
    "local_artifact",
}
ATTRIBUTION = {"own", "restated", "same_assumptions"}
BENCHMARK_CLASS = {"different_model", "administrative_fact", "same_assumptions"}
VALUE_KIND = {
    "point",
    "central",
    "range_low",
    "range_high",
    "approx_chart_reading",
    "cumulative",
    "categorical",
}
TIME_BASIS = {"fiscal_year", "annual", "point_in_time"}
CONFIDENCE = {"high", "medium", "low"}
# README rule 6: quotes from producers outside the Open Government Licence
# stay under 15 words.
OGL = {"hm_treasury", "obr_efo", "hmrc", "dwp", "ons", "scottish_fiscal_commission"}

from scorecard_db.models import Metric, UnitConcept  # noqa: E402

METRICS = {m.value for m in Metric}
UNITS = {u.value for u in UnitConcept}


def families():
    return sorted(
        p.name
        for p in HARVEST.iterdir()
        if p.is_dir() and (p / "claims_staged.jsonl.gz").exists()
    )


def rows(family):
    with gzip.open(HARVEST / family / "claims_staged.jsonl.gz", "rt") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def manifest(family):
    return [
        json.loads(line)
        for line in (HARVEST / family / "manifest.jsonl").read_text().splitlines()
        if line.strip()
    ]


def test_every_pinned_family_is_present_and_complete():
    assert set(FAMILIES) == set(families()), set(FAMILIES) ^ set(families())
    for fam in families():
        for name in ("NOTES.md", "manifest.jsonl", "claims_staged.jsonl.gz"):
            assert (HARVEST / fam / name).exists(), (fam, name)


def test_counts_json_is_what_harvest_counts_computes():
    """Rows, primaries, sources and the claims digest per family, plus the
    totals: one function writes COUNTS.json and this re-derives it, so a
    silent edit to a vendored row or a family added without its pin fails."""
    assert counts(HARVEST, COUNTS["_totals"]["pinned_on"]) == COUNTS


@pytest.mark.parametrize("family", FAMILIES)
def test_rows_follow_the_contract(family):
    for i, r in enumerate(rows(family)):
        where = (family, i)
        keys = set(r)
        assert REQUIRED <= keys, (where, REQUIRED - keys)
        assert keys <= REQUIRED | OPTIONAL, (where, keys - REQUIRED - OPTIONAL)
        assert r["status"] == "ok", where
        assert r["attribution"] in ATTRIBUTION, where
        assert r["benchmark_class"] in BENCHMARK_CLASS, where
        assert r["value_kind"] in VALUE_KIND, where
        assert r["time_basis"] in TIME_BASIS, where
        assert r["parse_confidence"] in CONFIDENCE, where
        assert isinstance(r["value"], (int, float)) and not isinstance(
            r["value"], bool
        ), where
        assert isinstance(r["value_raw"], str) and r["value_raw"].strip(), where
        assert isinstance(r["quote"], str) and r["quote"].strip(), where
        assert bool(r.get("metric")) != bool(r.get("proposed_metric")), where
        assert bool(r.get("unit_concept")) != bool(r.get("proposed_unit")), where
        if r.get("metric"):
            assert r["metric"] in METRICS, (where, r["metric"])
        if r.get("unit_concept"):
            assert r["unit_concept"] in UNITS, (where, r["unit_concept"])
        c = r["conditions"]
        assert isinstance(c, dict) and c, where
        for k, v in c.items():
            assert isinstance(k, str) and isinstance(v, str), (where, k, v)
        assert c["fiscal_event"] == "autumn_budget_2026", where
        if "fy" in c:
            m = re.fullmatch(r"(\d{4})-(\d{2})", c["fy"])
            assert m, (where, c["fy"])
            assert r["period"] == int(m.group(1)) + 1, (where, c["fy"], r["period"])
            assert r["time_basis"] == "fiscal_year", where
        assert isinstance(r["period"], int) and 1945 <= r["period"] <= 2075, where
        pub = r["publication"]
        for k in ("title", "url", "date", "publisher", "primary_sha256"):
            assert pub.get(k), (where, k)
        assert re.fullmatch(r"[0-9a-f]{64}", pub["primary_sha256"]), where
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", pub["date"]), where


@pytest.mark.parametrize("family", FAMILIES)
def test_measure_keys_exist_where_the_row_says_they_live(family):
    """README rule 2: an AB2026 key, an earlier event's key on a recosting,
    or null with a proposed key and nothing else."""
    for i, r in enumerate(rows(family)):
        where, c, k = (family, i), r["conditions"], r["measure_key"]
        if "recosting_of" in c:
            assert k in EARLIER[c["recosting_of"]], (where, c["recosting_of"], k)
        elif k is not None:
            assert k in KEYS, (where, k)
            assert "proposed_measure_key" not in c, where
        else:
            pk = c.get("proposed_measure_key")
            if pk:
                assert re.fullmatch(r"ab2026(_option)?__[a-z0-9_]+", pk), (where, pk)
                assert pk not in KEYS, (where, "use measure_key", pk)


@pytest.mark.parametrize("family", FAMILIES)
def test_every_row_cites_a_manifest_primary(family):
    shas = {m["sha256"] for m in manifest(family)}
    for m in manifest(family):
        assert re.fullmatch(r"[0-9a-f]{64}", m["sha256"]), (family, m.get("url"))
        assert m.get("url") and m.get("title") and m.get("retrieved"), (family, m)
    assert len(shas) == len(manifest(family)), family
    for i, r in enumerate(rows(family)):
        assert r["publication"]["primary_sha256"] in shas, (family, i)


@pytest.mark.parametrize("family", FAMILIES)
def test_quotes_outside_the_ogl_stay_short(family):
    for i, r in enumerate(rows(family)):
        if r["source"] not in OGL:
            assert len(r["quote"].split()) < 15, (family, i, r["quote"])


def test_same_assumptions_rows_are_policyengine_computed():
    for fam in families():
        for r in rows(fam):
            if r["attribution"] == "same_assumptions":
                assert r["benchmark_class"] == "same_assumptions", fam
                assert r["source_model"] == "policyengine_uk", fam


def test_no_hmt_decile_bar_readings_were_staged():
    """README rule 4 (AB2025 rule 9, #61)."""
    for fam in families():
        for r in rows(fam):
            if r["source"] == "hm_treasury":
                assert "Impact on households" not in r["publication"]["title"] or (
                    r["value_kind"] != "approx_chart_reading"
                ), (fam, r["quote"][:80])


def test_the_key_listing_is_derived_from_the_registry():
    text = (HARVEST / "REGISTRY_KEYS.md").read_text()
    listed = set(re.findall(r"^\| `([a-z0-9_]+)` \|", text, flags=re.M))
    assert listed == KEYS, listed ^ KEYS


# --- uk_hmt_tables: the stager's output against the tables' own structure ---

HMT = "uk_hmt_tables"


def _hmt(table):
    return [r for r in rows(HMT) if r["conditions"]["table"] == table]


def test_table_61_stages_every_line_and_total_for_six_years():
    t61 = _hmt("6.1")
    years = sorted({r["conditions"]["fy"] for r in t61})
    assert years == [f"{y}-{(y + 1) % 100:02d}" for y in range(2026, 2032)]
    measures = [r for r in t61 if r["conditions"]["row_type"] == "measure"]
    assert sorted({int(r["conditions"]["table_line"]) for r in measures}) == list(
        range(1, 99)
    )
    assert len(measures) == 98 * 6
    totals = [r for r in t61 if r["conditions"]["row_type"] == "total"]
    assert {r["measure_key"] for r in totals} == {
        K.package_key(s)
        for s in (
            "package_total_policy_decisions",
            "package_total_tax_policy_decisions",
            "package_total_spending_policy_decisions",
        )
    }
    assert len(totals) == 3 * 6


def test_table_61_rows_carry_the_written_out_key_for_their_line():
    for r in _hmt("6.1"):
        c = r["conditions"]
        if c["row_type"] == "measure":
            assert r["measure_key"] == K.key(int(c["table_line"])), c["table_line"]


def test_every_hmt_cell_is_a_multiple_of_5m():
    for r in rows(HMT):
        assert r["value"] % 5e6 == 0, (r["conditions"]["table"], r["value_raw"])


def test_table_61_lines_sum_to_the_printed_totals_within_rounding():
    """Footnote 1: totals may not sum due to rounding. Every staged cell is a
    multiple of £5m, so if HM Treasury rounds each line to the nearest £5m, 98
    lines drift at most 98 × £2.5m from the exact total; the observed gaps are
    £5m to £10m. Tax plus spend equals the grand total within the same rule."""
    t61 = _hmt("6.1")
    for fy in {r["conditions"]["fy"] for r in t61}:
        year = [r for r in t61 if r["conditions"]["fy"] == fy]
        total = {
            r["measure_key"]: r["value"]
            for r in year
            if r["conditions"]["row_type"] == "total"
        }
        by_head = {"Tax": 0.0, "Spend": 0.0}
        for r in year:
            if r["conditions"]["row_type"] == "measure":
                by_head[r["conditions"]["head"]] += r["value"]
        tax = total[K.package_key("package_total_tax_policy_decisions")]
        spend = total[K.package_key("package_total_spending_policy_decisions")]
        grand = total[K.package_key("package_total_policy_decisions")]
        assert abs(by_head["Tax"] - tax) <= 98 * 2.5e6, fy
        assert abs(by_head["Spend"] - spend) <= 98 * 2.5e6, fy
        assert abs(tax + spend - grand) <= 3 * 2.5e6, fy


def test_table_64_recostings_name_their_event():
    t64 = _hmt("6.4")
    assert len(t64) == 17 * 6
    for r in t64:
        c = r["conditions"]
        event, key = K.TABLE_64[int(c["table_line"])]
        assert c["recosting_of"] == event
        assert r["measure_key"] == key
        assert c["row_type"] == "recosting"


def test_table_62_rows_are_financial_transactions_not_revenue():
    t62 = _hmt("6.2")
    assert len(t62) == 9 * 6
    for r in t62:
        assert r["proposed_metric"] == "financial_transaction_cash_impact"
        assert "metric" not in r
        assert (
            r["measure_key"]
            == K.PREFIX + K.TABLE_62[int(r["conditions"]["table_line"])]
        )
