"""Issue #198: every exported row states its published value's sign against
PolicyEngine's — same, opposite, magnitude or unknown — from a declared
rule, and carries the value in that orientation."""

import glob
import gzip
import json
from collections import Counter
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

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
        # IFS's estimate of the Budget's tax change, which keeps revenue_change
        # (the Autumn Budget 2026 harvest's README rule 10)
        (
            _row("revenue_change", "positive = increase in net tax as a share of GDP"),
            "same",
        ),
        # borrowing conventions, verbatim from the Autumn Budget 2026 harvest,
        # whose totals of the Budget's decisions take this metric (its README
        # rule 10)
        (
            _row(
                "decisions_effect_on_borrowing",
                "Note (verbatim): A positive sign implies an increase in borrowing.",
            ),
            "same",
        ),
        (
            _row(
                "decisions_effect_on_borrowing",
                "positive = increase in PSNB; negative = reduction in PSNB",
            ),
            "same",
        ),
        (
            _row(
                "decisions_effect_on_borrowing",
                "as worded: positive = reduction in underspends / borrowing increase",
            ),
            "same",
        ),
        (
            _row("decisions_effect_on_borrowing", "positive = cost to the Exchequer"),
            "same",
        ),
        (
            _row(
                "decisions_effect_on_borrowing",
                "Note (verbatim): This table uses the convention that a negative "
                "sign implies a loss to the Exchequer (and is therefore an "
                "increase in PSNB).",
            ),
            "opposite",
        ),
        (
            _row(
                "decisions_effect_on_borrowing",
                "positive = yield to the Exchequer (reduces borrowing); negative = "
                "cost to the Exchequer",
            ),
            "opposite",
        ),
        (
            _row(
                "decisions_effect_on_borrowing",
                "positive = raises revenue (reduces borrowing), as RF plots Figure 10",
            ),
            "opposite",
        ),
        (
            _row(
                "decisions_effect_on_borrowing",
                "as worded: positive = borrowing reduction",
            ),
            "opposite",
        ),
        (
            _row(
                "decisions_effect_on_borrowing",
                "positive = increase in net tax as a share of GDP",
            ),
            "opposite",
        ),
        (
            _row(
                "decisions_effect_on_borrowing",
                "as worded: positive = additional investment income",
            ),
            "opposite",
        ),
        (
            _row(
                "decisions_effect_on_borrowing",
                "mixed: row 551 (negative = loss to Exchequer) plus row 555 "
                "(positive = increase in PSNB)",
            ),
            "unknown",
        ),
        (
            _row(
                "decisions_effect_on_borrowing", "absolute average, no directional sign"
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


def test_a_borrowing_total_without_one_direction_is_declared_unknown():
    # a total adding rows under two conventions, and an average of absolute
    # values, state why no sign applies rather than going unrecognised
    for convention in (
        "mixed: row 551 (negative = loss to Exchequer) plus row 555 "
        "(positive = increase in PSNB)",
        "absolute average, no directional sign",
    ):
        row = _row("decisions_effect_on_borrowing", convention)
        assert signs.classify(row) == ("unknown", "stated:borrowing:not_this_quantity")


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


# revenue_change counts a gain to the Exchequer as positive and
# decisions_effect_on_borrowing counts more borrowing as positive, so a
# convention that both phrase families read must read same for one metric
# and opposite for the other
_DEFINITE = sorted(
    {
        phrase
        for family in ("exchequer", "borrowing")
        for phrases in signs._PHRASES[family][1:]
        for phrase in phrases
    }
)
_FILLER = st.text(alphabet=" 0123456789;,()=-", max_size=12)


@settings(max_examples=200, deadline=None)
@given(phrase=st.sampled_from(_DEFINITE), before=_FILLER, after=_FILLER)
def test_one_phrase_reads_opposite_ways_for_revenue_and_borrowing(
    phrase, before, after
):
    text = before + phrase + after
    revenue = signs.classify(_row("revenue_change", text))[0]
    borrowing = signs.classify(_row("decisions_effect_on_borrowing", text))[0]
    if {revenue, borrowing} <= {"same", "opposite"}:
        assert revenue != borrowing, text


def test_published_conventions_read_opposite_ways_for_revenue_and_borrowing():
    texts = {r["conditions"].get("sign_convention") for r in _feed_rows()}
    for path in glob.glob(
        str(REPO / "sources" / "harvest-uk-*" / "*" / "claims_staged.jsonl.gz")
    ):
        with gzip.open(path, "rt") as f:
            texts |= {
                (json.loads(line).get("conditions") or {}).get("sign_convention")
                for line in f
            }
    texts.discard(None)
    read_by_both = 0
    for text in texts:
        revenue = signs.classify(_row("revenue_change", text))[0]
        borrowing = signs.classify(_row("decisions_effect_on_borrowing", text))[0]
        if {revenue, borrowing} <= {"same", "opposite"}:
            read_by_both += 1
            assert revenue != borrowing, text
    # 32 with the feed and the Autumn Budget 2026 harvest alone, 33 with
    # every harvest and the PMD feed
    assert read_by_both >= 30


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
