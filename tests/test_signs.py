"""Issue #198: every exported row states its published value's sign against
PolicyEngine's — same, opposite, magnitude or unknown — from a declared
rule, and carries the value in that orientation."""

import glob
import json
from collections import Counter
from pathlib import Path

import pytest

from scorecard_db import signs

REPO = Path(__file__).resolve().parent.parent


def _row(metric, convention=None, *, country="UK", source="x", annotations=(), **cond):
    conditions = dict(cond)
    if convention is not None:
        conditions["sign_convention"] = convention
    return {
        "metric": metric,
        "conditions": conditions,
        "country": country,
        "source": source,
        "latest": {"annotations": list(annotations)},
    }


@pytest.mark.parametrize(
    ("row", "relation"),
    [
        # exchequer conventions, verbatim from the feed
        (_row("revenue_change", "positive_gain_to_exchequer"), "same"),
        (
            _row(
                "revenue_change",
                "positive = yield to the Exchequer (reduces borrowing); negative = "
                "cost to the Exchequer (no legend printed in the document)",
            ),
            "same",
        ),
        (
            _row(
                "revenue_change",
                "Note (verbatim): A positive sign implies an increase in borrowing.",
            ),
            "opposite",
        ),
        (
            _row(
                "revenue_change",
                "Note (verbatim): This table uses the convention that a negative "
                "figure means a reduction in PSNB.",
            ),
            "opposite",
        ),
        (
            _row(
                "revenue_change",
                "Note (verbatim): Here we present higher taxes as positive numbers, "
                "in contrast to the tables elsewhere in this chapter.",
            ),
            "same",
        ),
        (_row("revenue_change", "positive = reduction in public spending"), "same"),
        (
            _row(
                "revenue_change",
                "as worded: 'reduces the static yield' (positive = reduction in yield)",
            ),
            "unknown",
        ),
        # households, poverty, bills
        (
            _row("average_household_income_change", "positive = gain to households"),
            "same",
        ),
        (
            _row(
                "average_household_income_change",
                "positive = loss to households (printed as a loss)",
            ),
            "opposite",
        ),
        (
            _row(
                "poverty_count_change",
                "positive = more people in poverty under the reform",
            ),
            "same",
        ),
        (
            _row("poverty_count_change", "positive = children lifted out of poverty"),
            "opposite",
        ),
        (
            _row(
                "poverty_count_change",
                "positive = children in poverty because of the two-child limit "
                "(= lifted out by its removal)",
            ),
            "unknown",
        ),
        (_row("energy_bill_change", "positive = saving"), "opposite"),
        (_row("energy_bill_change", "positive = higher council tax bill"), "same"),
        # levels, and changes with no stated convention
        (_row("poverty_rate"), "same"),
        (_row("revenue_change", country="US"), "same"),
        (_row("revenue_change"), "unknown"),
    ],
)
def test_declared_conventions(row, relation):
    assert signs.classify(row)[0] == relation


def test_an_unsigned_magnitude_is_magnitude():
    # the issue's example: HMRC "Change personal allowance by 1%"
    row = _row(
        "revenue_change",
        "magnitude_with_direction_in_label",
        change_direction="unsigned",
    )
    assert signs.classify(row) == ("magnitude", "magnitude_in_label")
    assert signs.external_value_pe_sign(1e9, "magnitude") is None


def test_a_result_oriented_to_its_claim_is_same_whatever_the_text():
    row = _row(
        "revenue_change",
        "positive = increase in borrowing",
        annotations=[
            "claim sign: positive = cost / increase in borrowing; PE oriented to it"
        ],
    )
    assert signs.classify(row) == ("same", "result_oriented_to_claim")


def test_external_value_pe_sign():
    assert signs.external_value_pe_sign(2.0, "same") == 2.0
    assert signs.external_value_pe_sign(2.0, "opposite") == -2.0
    assert signs.external_value_pe_sign(2.0, "unknown") is None
    assert signs.external_value_pe_sign(None, "same") is None


def _feed_rows():
    rows = list(json.loads((REPO / "data" / "populations.json").read_text())["rows"])
    for path in sorted(glob.glob(str(REPO / "data" / "populations-pmd" / "*.json"))):
        d = json.loads(Path(path).read_text())
        rows += [
            {
                **d["common"],
                **r,
                "conditions": {**d["common_conditions"], **r["conditions"]},
            }
            for r in d["rows"]
        ]
    return rows


def test_every_exported_row_carries_a_declared_sign():
    rows = _feed_rows()
    feed = json.loads((REPO / "data" / "populations.json").read_text())
    counts = Counter(r["sign_relative_to_pe"] for r in rows)
    assert counts == feed["summary"]["by_sign_relative_to_pe"]
    for r in rows:
        relation = r["sign_relative_to_pe"]
        assert relation in signs.RELATIONS
        # a new free-text convention must be classified deliberately
        assert not r["sign_basis"].endswith(":unrecognised"), r["conditions"]
        assert r["external_value_pe_sign"] == signs.external_value_pe_sign(
            r["external_value"], relation
        )
