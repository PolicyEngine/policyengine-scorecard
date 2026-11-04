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
from collections import Counter
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
from scorecard_db import signs

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
    # README rule 10: the totals take the borrowing metric, the lines keep
    # revenue_change
    assert {r["metric"] for r in totals} == {"decisions_effect_on_borrowing"}
    assert {r["metric"] for r in measures} == {"revenue_change"}


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


# --- README rule 10: stated effects of the Budget's decisions on PSNB --------

BORROWING = "decisions_effect_on_borrowing"

# keys that name only a stated effect of the Budget's decisions on PSNB or one
# of its splits
TOTAL_KEYS = {
    K.package_key(s)
    for s in (
        "package_total_policy_decisions",
        "package_total_tax_policy_decisions",
        "package_total_spending_policy_decisions",
        "package_tax_decisions_since_march_2026",
        "package_spending_decisions_since_march_2026",
        "package_non_scorecard_decisions",
    )
} | {"ab2026_option__tax_decisions_with_continued_fuel_duty_freeze"}
# the OBR's total, which also keys its Table 1.1 lines by head and its total
# of receipts measures
GOVERNMENT_DECISIONS = K.package_key("package_government_decisions_since_march_2026")
RECEIPTS_TOTAL = "Total effects of receipts measures (£ millions)"
IFS_TAX_CHANGE = K.package_key("package_ifs_announced_tax_changes")


def _key(r):
    return r.get("measure_key") or r["conditions"].get("proposed_measure_key")


def _label(r):
    c = r["conditions"]
    return c.get("table_row") or c.get("aggregate") or r.get("reform_hint") or ""


def test_rows_keyed_to_a_total_take_the_borrowing_metric():
    keyed = [(fam, r) for fam in FAMILIES for r in rows(fam) if _key(r) in TOTAL_KEYS]
    assert {_key(r) for _, r in keyed} == TOTAL_KEYS
    for fam, r in keyed:
        assert r["metric"] == BORROWING, (fam, _key(r), r["value_raw"])


def test_a_totals_lines_by_head_keep_revenue_change():
    """The OBR keys its Table 1.1 lines by tax and spending head, and the
    total of its receipts heads, to the total they add up to. Those rows keep
    revenue_change; every other row on that key gives the total, its direct
    or indirect effects or a part of them, and takes the borrowing metric or,
    for the current budget deficit, proposes fiscal_balance_change."""
    on_key = [
        r for fam in FAMILIES for r in rows(fam) if _key(r) == GOVERNMENT_DECISIONS
    ]
    by_head = [
        r
        for r in on_key
        if r.get("metric") == "revenue_change" and _label(r) != RECEIPTS_TOTAL
    ]
    assert len(by_head) == 288
    for r in by_head:
        assert r["source_table"].startswith("Table 1.1: Breakdown of policy decisions")
        assert not re.search(r"\b(total|effects? of)\b", _label(r), re.I), _label(r)
    for r in on_key:
        if r.get("metric") != "revenue_change":
            assert (
                r.get("metric") == BORROWING
                or r.get("proposed_metric") == "fiscal_balance_change"
            ), _label(r)


def test_receipts_totals_and_tax_change_estimates_keep_revenue_change():
    """README rule 10 (delta review of 8b7b23db, findings 1 and 2): a receipts
    total or a tax-change estimate keeps revenue_change unless its evidence
    establishes PSNB scope. The OBR workbook's total of receipts measures sums
    its receipts heads, and nothing in IFS's chart ties its estimate of the
    Budget's tax change at the forecast horizon to PSNB."""
    receipts = [r for r in rows("uk_obr_tables") if _label(r) == RECEIPTS_TOTAL]
    tax_change = [r for r in rows("uk_ifs_ab2026") if _key(r) == IFS_TAX_CHANGE]
    assert (len(receipts), len(tax_change)) == (6, 1)
    assert {r["metric"] for r in receipts + tax_change} == {"revenue_change"}


def test_a_measure_takes_the_borrowing_metric_only_where_its_producer_says_so():
    """README rule 10's exception: the OBR's paragraphs 3.20, 3.21 and 3.43
    give four policies' effects on borrowing, and IFS gives the Budget's new
    giveaways' effect on it."""
    outside = Counter(
        (fam, r["source_table"] if fam == "uk_obr_tables" else _key(r))
        for fam in FAMILIES
        for r in rows(fam)
        if r.get("metric") == BORROWING
        and _key(r) not in TOTAL_KEYS | {GOVERNMENT_DECISIONS, None}
    )
    assert outside == {
        ("uk_obr_tables", "para 3.20"): 2,
        ("uk_obr_tables", "para 3.21"): 4,
        ("uk_obr_tables", "para 3.43"): 1,
        ("uk_ifs_ab2026", "ab2026__package_ifs_new_giveaways"): 2,
    }


def test_the_current_budget_memos_name_that_deficit():
    memos = [
        (fam, r)
        for fam in FAMILIES
        for r in rows(fam)
        if re.search(r"memo:.*current budget deficit", _label(r), re.I)
    ]
    assert sorted(Counter(fam for fam, _ in memos).items()) == [
        ("uk_hmt_redbook", 11),
        ("uk_obr_tables", 6),
    ]
    for fam, r in memos:
        assert r.get("metric") is None, fam
        assert r["proposed_metric"] == "fiscal_balance_change", fam
        assert "current budget deficit" in r["conditions"]["sign_convention"], fam


def test_every_borrowing_row_says_which_way_it_runs():
    """signs.py reads each row's sign_convention as same or opposite, or as a
    stated reason no sign applies (a total that adds rows under two
    conventions, or an average of absolute values), never as unrecognised."""
    for fam in FAMILIES:
        for r in rows(fam):
            if r.get("metric") != BORROWING:
                continue
            relation, basis = signs.classify(
                {"metric": BORROWING, "conditions": r["conditions"], "country": "UK"}
            )
            assert relation in ("same", "opposite") or basis.endswith(
                ":not_this_quantity"
            ), (fam, r["conditions"].get("sign_convention"))
