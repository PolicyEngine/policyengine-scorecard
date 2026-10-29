"""The Autumn Budget 2026 harvest (#230): vendored data, checked as data.

sources/harvest-uk-ab2026-2026-10-29/ stages every producer's AB2026 claims
before the tranche-2 ingest exists. These tests hold each staged row to the
row contract in that directory's README.md (the AB2025 contract with the
AB2026 exceptions): field names, closed enums, the FY-end-year period rule,
the fiscal_event slug, measure keys that exist in the AB2026 registry or, for
a Table 6.4 recosting, in the earlier event's registry, sha256-shaped
manifests, and per-family pins that the ingest's exact accounting will read.
"""

import json
import re
from pathlib import Path

import pytest

from pipeline import ab2026_measure_keys as K
from pipeline.ab2026_harvest_contract import (
    family_problems,
    read_manifest,
    read_rows,
    registry_keys,
)
from pipeline.ab2026_proposed_keys import render
from pipeline.harvest_counts import counts

ROOT = Path(__file__).resolve().parent.parent
HARVEST = ROOT / "sources" / "harvest-uk-ab2026-2026-10-29"
KEYS, _ = registry_keys()

COUNTS = json.loads((HARVEST / "COUNTS.json").read_text())
FAMILIES = sorted(k for k in COUNTS if not k.startswith("_"))


def families():
    return sorted(
        p.name
        for p in HARVEST.iterdir()
        if p.is_dir() and (p / "claims_staged.jsonl.gz").exists()
    )


def rows(family):
    return read_rows(HARVEST / family)


def manifest(family):
    return read_manifest(HARVEST / family)


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
    """pipeline/ab2026_harvest_contract.py: field names, closed enums, the
    FY-end-year period, the fiscal_event slug, keys where the row says they
    live (README rule 2), a manifest primary for every row, short quotes
    outside the OGL (rule 6) that contain the value as printed, components
    that name their part and measure (rule 9), a NOTES.md scope for every
    proposed key, PolicyEngine-computed same_assumptions rows and no Impact
    on households bar readings (rule 4)."""
    assert family_problems(HARVEST / family) == []


def test_the_proposed_key_listing_is_derived_from_the_families():
    """PROPOSED_KEYS.md lists every proposed_measure_key a staged row names,
    once, with its rows, families and producers: tranche 2 registers or folds
    each one, so a key added without the listing moving fails."""
    assert (HARVEST / "PROPOSED_KEYS.md").read_text() == render(HARVEST)


def test_the_key_listing_is_derived_from_the_registry():
    text = (HARVEST / "REGISTRY_KEYS.md").read_text()
    listed = set(re.findall(r"^\| `([a-z0-9_]+)` \|", text, flags=re.MULTILINE))
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
