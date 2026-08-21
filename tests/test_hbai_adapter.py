"""Series-completeness tests for the HBAI poverty external.

These assert shape, not headline values: the adapter's own inline checks pin
hand-picked cells from the FYE 2025 publication text, and two whole-series
losses passed all thirteen of them.

  - a DWP series-break annotation sitting in column A *next to live data*
    ("Admin-linked benefits data from 2021/22" / "See Note 1") made the row
    loop treat 2021/22 and 2022/23 as prose, dropping both years from every
    summary table (8 sheets x 2 years x 4 measure columns = 64 rows);
  - a stray space in one period header ('20/21- 22/23') failed the period
    regex in the four pensioner regional tables, dropping that whole column
    (4 tables x 13 geographies x 2 variants = 104 rows).

Neither was visible from a spot check, so the tests below look at spans and
cross-table agreement instead.
"""

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
EXTERNAL = ROOT / "data" / "externals" / "hbai-poverty.json"

pytestmark = pytest.mark.skipif(
    not EXTERNAL.exists(), reason="hbai-poverty external not built on this branch"
)

# Pinned to the FYE 2025 vintage. A new vintage moves this deliberately; an
# accidental parse regression moves it by surprise, which is the point.
EXPECTED_ROWS = 13056

GB_YEARS = [f"{y}/{(y + 1) % 100:02d}" for y in range(1994, 2002)]  # 1994/95-2001/02
UK_YEARS = [f"{y}/{(y + 1) % 100:02d}" for y in range(2002, 2025)]  # 2002/03-2024/25

REGIONS = {
    "England",
    "North East",
    "North West",
    "Yorkshire and the Humber",
    "East Midlands",
    "West Midlands",
    "East",
    "London",
    "South East",
    "South West",
    "Wales",
    "Scotland",
    "Northern Ireland",
}

SUBGROUPS = {"total", "children", "working_age", "pensioners"}


@pytest.fixture(scope="module")
def rows():
    return json.loads(EXTERNAL.read_text())


def test_row_count_pinned(rows):
    assert len(rows) == EXPECTED_ROWS


def test_rows_are_unique(rows):
    keys = [
        (
            r["metric"],
            r["subgroup"],
            r["variant"],
            r["geography"],
            r["period"],
        )
        for r in rows
    ]
    assert len(set(keys)) == len(keys)


def test_single_year_series_span_is_unbroken(rows):
    """Every UK/GB series covers 1994/95-2024/25 with no missing year.

    Regression for the series-break annotation defect: before the fix the
    UK series jumped 2020/21 -> 2023/24.
    """
    series = {}
    for r in rows:
        if r["geography"] in ("GB", "UK"):
            key = (r["metric"], r["subgroup"], r["variant"])
            series.setdefault(key, {}).setdefault(r["geography"], []).append(
                r["period"]
            )

    # 2 poverty lines x 2 kinds x 4 subgroups x 2 housing-cost variants
    assert len(series) == 32
    for key, by_geo in series.items():
        assert sorted(by_geo["GB"]) == GB_YEARS, key
        assert sorted(by_geo["UK"]) == UK_YEARS, key


def test_series_break_years_present(rows):
    """The two years the column-A annotation used to swallow."""
    for period in ("2021/22", "2022/23"):
        got = [r for r in rows if r["period"] == period and r["geography"] == "UK"]
        assert len(got) == 32, period
        assert all(r["value"] is not None for r in got), period


def test_change_rows_are_not_emitted(rows):
    """DWP's 'Change' rows are year-on-year deltas, not levels.

    Loosening the row filter to rescue the annotated years must not let the
    delta row in: every UK/GB period stays a bare single year.
    """
    bad = [
        r["period"]
        for r in rows
        if r["geography"] in ("GB", "UK")
        and not re.fullmatch(r"\d{4}/\d{2}", r["period"])
    ]
    assert not bad


def test_regional_periods_identical_across_age_groups(rows):
    """All four age groups publish the same 3-year periods.

    Regression for the stray-space defect: the pensioner tables carried 28
    periods where the other age groups carried 29.
    """
    by_key = {}
    for r in rows:
        if r["geography"] in ("GB", "UK"):
            continue
        key = (r["metric"], r["subgroup"], r["variant"], r["geography"])
        by_key.setdefault(key, set()).add(r["period"])

    period_sets = {frozenset(v) for v in by_key.values()}
    assert len(period_sets) == 1, {
        k: len(v) for k, v in sorted(by_key.items(), key=lambda kv: len(kv[1]))
    }

    periods = sorted(period_sets.pop())
    assert periods[0] == "1994/95-1996/97"
    assert periods[-1] == "2022/23-2024/25"
    assert len(periods) == 29
    # rolling, so consecutive periods start one year apart with no gap
    starts = [int(p[:4]) for p in periods]
    assert starts == list(range(starts[0], starts[0] + len(starts)))
    # the period the pensioner tables used to lose
    assert "2020/21-2022/23" in periods


def test_every_regional_table_covers_every_geography(rows):
    by_key = {}
    for r in rows:
        if r["geography"] in ("GB", "UK"):
            continue
        key = (r["metric"], r["subgroup"], r["variant"])
        by_key.setdefault(key, set()).add(r["geography"])
    assert len(by_key) == 32
    for key, geos in by_key.items():
        assert geos == REGIONS, key


def test_schema_fields_and_domains(rows):
    for r in rows:
        assert r["source"] == "hbai-poverty"
        assert r["country"] == "UK"
        assert r["program"] == "hbai_low_income"
        assert r["subgroup"] in SUBGROUPS
        assert r["variant"] in ("bhc", "ahc")
        assert r["metric"] in {
            f"{line}_low_income_{kind}"
            for line in ("relative", "absolute")
            for kind in ("rate", "count")
        }
        assert r["status"] in ("ok", "suppressed")
        assert (r["value"] is None) == (r["status"] == "suppressed")
        if r["metric"].endswith("_rate") and r["value"] is not None:
            assert 0 < r["value"] < 1


# --- office:value precision (#44 follow-up, fixed 2026-08-19) --------------
# The adapter reads the ODS office:value attribute — the UNROUNDED value the
# workbook stores — keeping the display text only as a consistency check.

_ADAPTER = ROOT / "sources" / "hbai-poverty" / "adapter.py"


@pytest.fixture(scope="module")
def adapter():
    import importlib.util

    spec = importlib.util.spec_from_file_location("hbai_adapter", _ADAPTER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_parse_value_prefers_office_value(adapter):
    cell = adapter.Cell("16", num=(15.911572126383566, "float"))
    value, status = adapter.parse_value(cell, "rate")
    assert status == "ok"
    assert value == pytest.approx(0.15911572126383566)
    # a count cell displayed in millions keeps its unrounded millions
    cell = adapter.Cell("10.9", num=(10.859363, "float"))
    value, _ = adapter.parse_value(cell, "count")
    assert value == pytest.approx(10_859_363.0)


def test_percentage_typed_cells_align_to_display_scale(adapter):
    # ODS percentage cells store the FRACTION; the sheet displays the
    # percent-scale number — parse must not divide twice.
    cell = adapter.Cell("16", num=(0.15911572126383566, "percentage"))
    value, _ = adapter.parse_value(cell, "rate")
    assert value == pytest.approx(0.15911572126383566)


def test_display_must_be_the_rounded_rendering(adapter):
    # text "16" cannot belong to a stored 17.2 — a mispaired cell aborts
    cell = adapter.Cell("16", num=(17.2, "float"))
    with pytest.raises(ValueError, match="rounded rendering"):
        adapter.parse_value(cell, "rate")
    # ...but 16.4 rounds to 16 at the text's own precision: accepted
    cell = adapter.Cell("16", num=(16.4, "float"))
    value, _ = adapter.parse_value(cell, "rate")
    assert value == pytest.approx(0.164)


def test_text_only_cells_still_parse(adapter):
    # suppression markers and label cells never carry num
    assert adapter.parse_value(adapter.Cell("[x]"), "rate") == (None, "suppressed")
    assert adapter.parse_value(adapter.Cell(""), "rate") == (None, "empty")
    # a bare string (no office:value captured) falls back to the text
    value, _ = adapter.parse_value(adapter.Cell("16"), "rate")
    assert value == pytest.approx(0.16)


def test_emitted_rates_carry_full_precision(rows):
    """The emitted external is unrounded: in the FYE 2025 vintage zero of
    the 6,528 rate values sit at exactly two decimals; a regression to
    display-text parsing puts ALL of them there. Threshold well under
    both: a future vintage may legitimately land a handful of exact
    values, a text-parse regression cannot stay under it."""
    rates = [
        r["value"]
        for r in rows
        if r["metric"].endswith("_rate") and r["value"] is not None
    ]
    exactly_2dp = sum(1 for v in rates if v == round(v, 2))
    assert len(rates) > 6000
    assert exactly_2dp < len(rates) * 0.01, f"{exactly_2dp}/{len(rates)}"


@pytest.mark.skipif(
    not (ROOT / "sources" / "hbai-poverty" / "raw").exists(),
    reason="vendored raw ODS files not present",
)
def test_vendored_workbook_carries_unrounded_values(adapter):
    """One real cell from the vendored summary workbook: sheet 1_2a
    displays '75.9' over a stored 75.875 (the probe that motivated the
    fix). read_sheets must surface the stored value."""
    sheets = adapter.read_sheets(
        ROOT / "sources" / "hbai-poverty" / "raw" / adapter.SUMMARY_FILE, {"1_2a"}
    )
    nums = [
        cell.num[0]
        for row in sheets["1_2a"]
        for cell in row
        if cell.num is not None and cell.num[1] == "float"
    ]
    assert 75.875 in nums
