"""Regression tests for the UKMOD Country Report adapter (#47).

CI runs pytest but never `sources/`, so the adapter's own check block is
invisible to it — which is how a defect that shifted five of Table 4.7's
rows onto their neighbours' values shipped while all 12 spot-checks
printed OK. These tests put the table-level identities in CI's path.
"""

import importlib.util
import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
EXTERNAL = REPO / "data" / "externals" / "ukmod-stats.json"
ADAPTER = REPO / "sources" / "ukmod-stats" / "adapter.py"

pytestmark = pytest.mark.skipif(
    not EXTERNAL.exists(), reason="ukmod-stats adapter output not built"
)


def _adapter():
    spec = importlib.util.spec_from_file_location("ukmod_adapter", ADAPTER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def rows():
    return json.loads(EXTERNAL.read_text())


def test_row_count_pinned(rows):
    assert len(rows) == 1131


def test_structural_invariants_hold(rows):
    failures = [label for label, ok in _adapter().structural_invariants(rows) if not ok]
    assert not failures


def test_quintile_medians_match_the_report(rows):
    """Table 4.7 ground truth, read off the PDF by hand."""
    index = {
        (r["subgroup"], r["variant"], r["period"]): r["value"]
        for r in rows
        if r["metric"] == "quintile_median_income"
    }
    expected = {
        ("ukmod", "2023"): [1560, 2238, 2869, 3779, 5591],
        ("ukmod", "2024"): [1587, 2333, 3022, 4013, 5919],
        ("ukmod", "2030"): [1811, 2670, 3427, 4558, 6724],
        ("input_data", "2023"): [1352, 2157, 2818, 3682, 5510],
        ("hbai", "2023"): [1527, 2308, 2980, 3834, 5704],
    }
    for (variant, period), values in expected.items():
        got = [index[(q, variant, period)] for q in ("q1", "q2", "q3", "q4", "q5")]
        assert got == values, (variant, period, got)


def test_quintile_shares_match_the_report(rows):
    index = {
        (r["subgroup"], r["variant"], r["period"]): r["value"]
        for r in rows
        if r["metric"] == "quintile_income_share"
    }
    for variant, period, values in (
        ("ukmod", "2023", [0.08, 0.13, 0.17, 0.22, 0.40]),
        ("hbai", "2023", [0.08, 0.13, 0.17, 0.21, 0.41]),
        ("input_data", "2023", [0.07, 0.13, 0.17, 0.22, 0.42]),
    ):
        got = [
            round(index[(q, variant, period)], 4)
            for q in ("q1", "q2", "q3", "q4", "q5")
        ]
        assert got == values, (variant, period, got)


def test_money_rows_carry_a_money_unit(rows):
    """Expenditure counts pounds, whatever its instrument counts."""
    units = {r["unit_concept"] for r in rows if r["metric"] == "expenditure"}
    assert units == {"gbp_nominal"}


def test_caseload_units_are_counting_units(rows):
    units = {r["unit_concept"] for r in rows if r["metric"] == "caseload"}
    assert units <= {"families", "households", "children", "individuals"}


def test_no_value_is_absurdly_small(rows):
    """A row label captured as a value shows up as a tiny number.

    The original defect stored the literal row label '2' as quintile 2's
    2024 median income (£2/month).
    """
    suspects = [
        r
        for r in rows
        if r["metric"] in ("quintile_median_income", "mean_income", "median_income")
        and r["value"] is not None
        and r["value"] < 100
    ]
    assert not suspects
