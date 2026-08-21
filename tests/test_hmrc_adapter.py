"""HMRC personal tax externals: the ready-reckoner sign convention.

CI never runs sources/, so the adapter's own inline checks are invisible here.
These read the committed extract instead.

The defect these guard: HMRC ready-reckoner rows are magnitudes with the
direction carried only in English prose, so a cost row and a yield row are both
positive. A PE counterpart computed as (reform - baseline) returns the cost with
the opposite sign and reads as a 100% divergence -- or matches under any abs()
comparison. The convention has to be on the row, machine-readable.
"""

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
EXTERNAL = ROOT / "data" / "externals" / "hmrc-personal-tax.json"

SIGN_CONVENTION = "magnitude_with_direction_in_label"
DIRECTIONS = {"cost", "yield", "stated_change"}
CHANGE_DIRECTIONS = {"increase", "decrease", "unsigned"}
CONVENTION_KEYS = {"sign_convention", "direction", "change_direction"}


def load():
    if not EXTERNAL.exists():
        pytest.skip(f"{EXTERNAL} not built")
    return json.loads(EXTERNAL.read_text())


def reckoner(rows):
    return [r for r in rows if r["metric"] == "revenue_effect"]


def test_row_count_pinned():
    rows = load()
    assert len(rows) == 1213
    assert len(reckoner(rows)) == 225


def test_every_reckoner_row_carries_a_classified_convention():
    rows = reckoner(load())
    assert rows
    for row in rows:
        assert row["sign_convention"] == SIGN_CONVENTION, row["subgroup"]
        assert row["direction"] in DIRECTIONS, row["subgroup"]
        assert row["change_direction"] in CHANGE_DIRECTIONS, row["subgroup"]


def test_direction_matches_the_verbatim_label():
    """Direction is read off the label, never guessed from the value's sign."""
    for row in reckoner(load()):
        label = row["subgroup"]
        lowered = label.lower()
        if lowered.endswith("(cost)"):
            assert row["direction"] == "cost", label
        elif lowered.endswith("(yield)"):
            assert row["direction"] == "yield", label
        else:
            # No marker in the label -> no direction may be invented for it.
            assert row["direction"] == "stated_change", label
        if label.startswith(("Increase ", "Raise ")):
            assert row["change_direction"] == "increase", label
        elif label.startswith(("Decrease ", "Cut ")):
            assert row["change_direction"] == "decrease", label
        else:
            assert row["change_direction"] == "unsigned", label


def test_additional_rate_cost_and_yield_are_both_positive_but_distinguishable():
    """The exact ambiguity that motivated this: same sign, opposite meaning."""
    rows = reckoner(load())
    yield_row = next(
        r
        for r in rows
        if r["subgroup"] == "Increase additional rate by 1p (yield)"
        and r["period"] == "2026-27"
    )
    cost_row = next(
        r
        for r in rows
        if r["subgroup"] == "Decrease additional rate by 1p (cost)"
        and r["period"] == "2026-27"
    )
    # Values are HMRC's, unflipped: both positive, which is the trap.
    assert yield_row["value"] == 145_000_000
    assert cost_row["value"] == 175_000_000
    assert yield_row["value"] > 0 and cost_row["value"] > 0
    # Sign alone cannot separate them; the direction field must.
    assert yield_row["direction"] == "yield"
    assert cost_row["direction"] == "cost"
    assert yield_row["direction"] != cost_row["direction"]
    assert yield_row["change_direction"] == "increase"
    assert cost_row["change_direction"] == "decrease"


def test_unmarked_increase_rows_are_not_called_yields():
    """HMRC publishes revenue-losing 'Increase ...' rows; no direction invented."""
    rows = reckoner(load())
    label = "Increase lower Capital Gains Tax rate by 10 percentage points"
    cgt = next(r for r in rows if r["subgroup"] == label and r["period"] == "2026-27")
    assert cgt["value"] == -130_000_000  # genuine negative, preserved
    assert cgt["direction"] == "stated_change"
    assert cgt["change_direction"] == "increase"


def test_plain_change_rows_state_no_direction():
    rows = reckoner(load())
    basic = next(
        r
        for r in rows
        if r["subgroup"] == "Change basic rate by 1p" and r["period"] == "2026-27"
    )
    assert basic["value"] == 6_900_000_000
    assert basic["direction"] == "stated_change"
    assert basic["change_direction"] == "unsigned"


def test_levels_rows_are_untouched():
    rows = load()
    levels = [r for r in rows if r["metric"] != "revenue_effect"]
    assert len(levels) == 988
    for row in levels:
        assert not (CONVENTION_KEYS & set(row)), row["metric"]
    total = next(
        r
        for r in levels
        if r["metric"] == "taxpayer_count"
        and r["subgroup"] == "total"
        and r["period"] == "2026-27"
    )
    assert total["value"] == 40_800_000


def test_annotation_states_the_convention_as_a_comparison_constraint():
    path = ROOT / "sources" / "hmrc-personal-tax" / "annotations.json"
    annotations = json.loads(path.read_text())["annotations"]
    applicable = [
        a for a in annotations if "revenue_effect" in (a["applies_to"]["metrics"] or [])
    ]
    text = " ".join(a["text"] for a in applicable)
    assert SIGN_CONVENTION in text
    assert "direction" in text
