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
