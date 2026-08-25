"""The DISTINCT ledger only ever contains checkable assertions.

`DISTINCT` is a plain frozenset of `"source:value"` strings, so nothing
stops it naming a source that has no registered vocabulary. A pair like
that reads as if a distinction had been checked when there is nothing on
the other side to check against — and, because the pair is just a
string, every test asserting it exists still passes.

That defect was caught by review on #92 (ONS quintiles claimed distinct
from HBAI, which registers no quantile vocabulary at all) and it recurred
on the pensions branch (DWP age bands claimed distinct from LPC, whose
vocabulary lives on another branch). Two occurrences is a class, so it
gets a guard rather than a third correction.
"""

import re
from pathlib import Path

import pytest

from scorecard_db.uk_aliases import DISTINCT, known

ROOT = Path(__file__).resolve().parent.parent
SOURCE = (ROOT / "scorecard_db" / "uk_aliases.py").read_text()


def _registered_sources():
    """Every source with at least one registered value, read from the
    registry itself rather than a hardcoded list."""
    sources = set()
    for axis_call in re.finditer(
        r'_(?:identity|alias)\(\s*\n?\s*"([a-z_0-9]+)"', SOURCE
    ):
        sources.add(axis_call.group(1))
    for pair in re.findall(r"for _src in \(([^)]*)\)", SOURCE):
        sources.update(re.findall(r'"([a-z_0-9]+)"', pair))
    return sources


def test_every_distinct_pair_names_two_registered_sources():
    """An assertion against a source nobody registered is not a
    distinction — it is a sentence."""
    registered = _registered_sources()
    dangling = sorted(
        {
            side.split(":", 1)[0]
            for pair in DISTINCT
            for side in pair
            if ":" in side and side.split(":", 1)[0] not in registered
        }
    )
    assert not dangling, (
        f"DISTINCT names sources with no registered vocabulary: {dangling}. "
        "Either register them, or defer the pair with a comment saying which "
        "branch or issue brings the other side — do not assert against "
        "nothing."
    )


def test_every_distinct_value_exists_on_its_own_side():
    """The stricter form: not just the source, the VALUE. A pair naming
    `ukmod:q9` would be equally unfalsifiable."""
    missing = []
    for pair in DISTINCT:
        for side in pair:
            if ":" not in side:
                continue
            src, value = side.split(":", 1)
            axes = (
                "program",
                "subgroup",
                "geography",
                "income_group",
                "quantile",
                "unit",
                "benefit",
                "earnings_band",
                "age_band",
                "region",
                "income_concept",
                "statistic",
                "rate_scope",
                "poverty_line",
                "housing_costs",
                "sector",
            )
            if not any(value in known(src, axis) for axis in axes):
                missing.append(side)
    assert not missing, (
        f"DISTINCT names values that are not registered anywhere: "
        f"{sorted(set(missing))}"
    )


def test_the_guard_is_not_passing_trivially():
    """A guard that would pass on an empty set is not a guard. The
    long-standing base pairs must be present, so the checks above are
    actually checking something."""
    assert ("dwp_takeup:benefit_units", "ukmod:families") in DISTINCT
    assert (
        "dwp_takeup:housing_benefit_pensioners",
        "ukmod:housing_benefit",
    ) in DISTINCT
    assert len(DISTINCT) >= 4
