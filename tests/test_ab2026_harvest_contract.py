"""The AB2026 harvest contract checker (#230), tested on rows built to break it.

tests/test_uk_ab2026_harvest.py holds every staged family to
pipeline/ab2026_harvest_contract.py. These tests hold the checker itself to
the README: each rule, broken on an otherwise valid row, gives a problem, and
the period and quote-length rules hold for every input.
"""

import copy
import gzip
import io
import json
import math
import shutil
import tempfile
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from pipeline.ab2026_harvest_contract import (
    OGL,
    ONES,
    TENS,
    duplicate_problems,
    enums,
    family_problems,
    proposed_keys,
    read_rows,
    reads_a_bar,
    registry_keys,
    row_problems,
)

ROOT = Path(__file__).resolve().parent.parent
FAMILY = ROOT / "sources" / "harvest-uk-ab2026-2026-10-29" / "uk_hmt_tables"
KEYS, EARLIER = registry_keys()
METRICS, UNITS = enums()
BASE = next(
    r
    for r in read_rows(FAMILY)
    if r["measure_key"] and "recosting_of" not in r["conditions"]
)
REGISTERED = BASE["measure_key"]


def problems(row):
    return row_problems(row, KEYS, EARLIER, METRICS, UNITS)


def mutated(**changes):
    """BASE with dotted-path changes; a value of ... deletes the field."""
    row = copy.deepcopy(BASE)
    for path, value in changes.items():
        *parents, leaf = path.split("__")
        target = row
        for p in parents:
            target = target[p]
        if value is ...:
            del target[leaf]
        else:
            target[leaf] = value
    return row


def test_a_staged_row_has_no_problems():
    assert problems(BASE) == []


@pytest.mark.parametrize(
    ("changes", "expected"),
    [
        ({"quote": ...}, "missing fields"),
        ({"invented": "x"}, "unknown fields"),
        ({"attribution": "guess"}, "attribution"),
        ({"status": "draft"}, "status is not ok"),
        ({"value": "1"}, "value is not a number"),
        ({"value": True}, "value is not a number"),
        ({"proposed_metric": "x"}, "exactly one of metric"),
        ({"metric": "not_a_metric"}, "is not a Metric"),
        ({"conditions__fiscal_event": "autumn_budget_2025"}, "fiscal_event"),
        ({"conditions__geography": 1}, "is not a string"),
        ({"conditions__fy": "2026/27"}, "is not one fiscal year YYYY-YY"),
        ({"conditions__fy": "2026-29"}, "is not one fiscal year YYYY-YY"),
        ({"period": 2026}, "is not the end year"),
        ({"time_basis": "annual"}, "time_basis fiscal_year"),
        ({"measure_key": "ab2026__not_a_measure"}, "is not in data/uk"),
        (
            {"conditions__proposed_measure_key": "ab2026__package_x"},
            "carries no proposed_measure_key",
        ),
        (
            {"measure_key": None, "conditions__proposed_measure_key": "package_x"},
            "is not ab2026",
        ),
        (
            {"measure_key": None, "conditions__proposed_measure_key": REGISTERED},
            "is registered",
        ),
        (
            {"conditions__recosting_of": "autumn_budget_2025"},
            "is not a autumn_budget_2025 key",
        ),
        ({"conditions__row_type": "measure_component"}, "rule 9"),
        (
            {
                "measure_key": None,
                "conditions__row_type": "measure_component",
                "conditions__component": "Scotland",
            },
            "rule 9",
        ),
        ({"value_raw": "-2,625"}, "quote does not contain value_raw"),
        ({"publication__primary_sha256": "abc"}, "is not a sha256"),
        ({"publication__date": "28 October 2026"}, "is not YYYY-MM-DD"),
        ({"publication__url": ""}, "publication.url is empty"),
        ({"attribution": "same_assumptions"}, "PolicyEngine-computed"),
        # review A H-1: a component is a part (rule 9)
        ({"conditions__component": "Receipts: VAT"}, "a component row has row_type"),
        (
            {"conditions__component": " ", "conditions__row_type": "measure_component"},
            "names its component and measure",
        ),
        # review A H-2: value against value_raw
        ({"value": float("nan")}, "value is not finite"),
        ({"value": float("inf")}, "value is not finite"),
        ({"value": -2625}, "at a stated scale"),
        ({"value": 2625000000}, "opposite sign"),
        # review A H-6
        (
            {"metric": ..., "proposed_metric": "affected_share"},
            "is a registered Metric",
        ),
        ({"conditions__recosting_of": "autumn_budget_2025"}, "row_type recosting"),
        ({"conditions__fy": ...}, "conditions.fy or conditions.horizon"),
        ({"conditions__geography": "England for count; UK funding"}, "is not a code"),
        ({"attribution": "restated", "note": ""}, "names whose figure"),
        (
            {"measure_key": None, "conditions__proposed_measure_key": "ab2026___x"},
            "is not ab2026",
        ),
        (
            {
                "measure_key": None,
                "conditions__proposed_measure_key": "ab2026__package_",
            },
            "is not ab2026",
        ),
        (
            {
                "measure_key": None,
                "conditions__proposed_measure_key": "ab2026__package",
            },
            "is not ab2026",
        ),
        ({"measure_key": ["ab2026__x"]}, "measure_key is not a string"),
        ({"publication": None}, "publication is not an object"),
        ({"value_raw": None}, "value_raw is empty"),
        # delta review D1-1: a printed £m cell is that many millions exactly
        ({"value": -2626312500}, "at a stated scale"),
        ({"value": -2625100000}, "at a stated scale"),
        # delta review D1: each arm the dedicated tests didn't reach
        (
            {"conditions__component": " ", "conditions__row_type": "measure_total"},
            "a component row has row_type",
        ),
        ({"conditions__component": 1}, "row is malformed"),
        (
            {"measure_key": None, "conditions__proposed_measure_key": ["ab2026__x"]},
            "row is malformed",
        ),
        # final review F2: £1 or £2 off a £m cell is no floating-point error
        ({"value": -2625000001}, "at a stated scale"),
        ({"value": -2625000002}, "at a stated scale"),
        ({"value": -2624999999.5}, "at a stated scale"),
        # final review F3: an integer too large for a float
        ({"value": 10**400}, "value is not finite"),
        ({"value": -(10**400)}, "value is not finite"),
    ],
)
def test_each_rule_broken_on_a_valid_row_is_a_problem(changes, expected):
    found = problems(mutated(**changes))
    assert any(expected in p for p in found), found


def test_value_raw_scale_words_set_the_scale():
    """review A H-2: "£15 billion" is 1.5e10, never 1.5e7; "N in M" is N/M."""
    bn = mutated(value_raw="£15 billion", quote="£15 billion", value=1.5e10)
    wrong = mutated(value_raw="£15 billion", quote="£15 billion", value=1.5e7)
    share = mutated(
        value_raw="1 in 4", quote="1 in 4", value=0.25, normalization="N in M -> N/M"
    )
    worded = mutated(
        value_raw="£2bn",
        quote="cut of £2bn",
        value=-2e9,
        normalization="£bn x 1e9; sign from the wording (cut)",
    )
    assert problems(bn) == []
    assert any("at a stated scale" in p for p in problems(wrong))
    assert problems(share) == []
    assert problems(worded) == []


def _share(raw, value, normalization="N in M -> N/M"):
    return mutated(value_raw=raw, quote=raw, value=value, normalization=normalization)


@pytest.mark.parametrize("wrong", [0.01, 0.04, 1, 4, 25])
def test_a_ratio_is_its_share_not_its_numbers(wrong):
    """Delta review D1-1: IFS's "1 in 4" (its row 38) is the share 0.25.
    Neither number on its own, at any scale, is."""
    assert problems(_share("1 in 4", 0.25)) == []
    assert any("at a stated scale" in p for p in problems(_share("1 in 4", wrong)))


def test_a_worded_fraction_is_its_share():
    """Delta review D1: "a third" is 1/3, which a stored share may round to
    0.3333 (OBR row 2662), and nothing else. A row whose fraction went
    unparsed would compare nothing and pass whatever its value."""
    note = "'a third' -> 0.3333 share"
    assert problems(_share("a third", 0.3333, note)) == []
    assert any("at a stated scale" in p for p in problems(_share("a third", 0.5, note)))
    assert any("opposite sign" in p for p in problems(_share("a third", -0.3333, note)))


def test_a_year_after_in_is_no_denominator():
    """A year after "in" prints a year: "5 in 2027" gives 5 (here £5m) and
    2027, not the ratio 5/2027."""
    assert problems(mutated(value_raw="5 in 2027", quote="5 in 2027", value=5e6)) == []


def test_a_year_after_in_is_a_denominator_when_the_normalization_says_so():
    """Final review F1: "1 in 2000" stored as the share 0.0005 passes only
    when its normalization gives the ratio, as "1 in 2,000" always does."""
    stated = "1 in 2000 -> 0.0005"
    assert problems(_share("1 in 2000", 0.0005)) == []
    assert problems(_share("1 in 2000", 0.0005, stated)) == []
    assert problems(_share("1 in 2,000", 0.0005, "share as printed")) == []
    found = problems(_share("1 in 2000", 0.0005, "£ million x 1,000,000"))
    assert any("at a stated scale" in p for p in found), found
    for wrong in (1, 2000):
        found = problems(_share("1 in 2000", wrong, stated))
        assert any("at a stated scale" in p for p in found), (wrong, found)


@pytest.mark.parametrize(
    ("raw", "share", "normalization"),
    [
        ("1 IN 4", 0.25, "N in M -> N/M"),
        ("1 In 4", 0.25, "N in M -> N/M"),
        ("1-in-4", 0.25, "N in M -> N/M"),
        ("-1 in 4", -0.25, "N in M -> N/M"),
        ("−1 in 4", -0.25, "N in M -> N/M"),
        ("one in ten", 0.1, "one in ten -> 0.1"),
        ("fewer than one in ten", 0.1, "one in ten -> 0.1"),
        ("about three in ten", 0.3, "three in ten -> 0.3"),
        ("Eight in Ten", 0.8, "eight in ten -> 0.8"),
        ("one in four", 0.25, "one in four -> 0.25"),
        ("one in a hundred", 0.01, "one in a hundred -> 0.01"),
        ("1 in 2000", 0.0005, "1 in 2000 -> 0.0005"),
    ],
)
def test_a_ratio_in_any_form_is_its_signed_share(raw, share, normalization):
    """Final review F1: "in" in any case or hyphenated, a minus on N, and
    number words (CenTax's "one in ten", rows 16, 93 and 95). The share
    passes; the share with the other sign, N, M and N/M as a percentage
    don't. Before F1, a worded ratio printed no number, so any value passed."""
    assert problems(_share(raw, share, normalization)) == []
    flipped = problems(_share(raw, -share, normalization))
    assert any("opposite sign" in p for p in flipped), flipped
    for wrong in (1, 3, 4, 8, 10, 100, 2000, 100 * share, 0.5):
        if not math.isclose(abs(wrong), abs(share), rel_tol=1e-3):
            found = problems(_share(raw, wrong, normalization))
            assert any(
                "at a stated scale" in p or "opposite sign" in p for p in found
            ), (raw, wrong, found)


@settings(max_examples=200, deadline=None)
@given(
    n=st.integers(1, 50),
    extra=st.integers(1, 1000),
    form=st.sampled_from(["{n} in {m:,}", "{n} IN {m:,}", "{n}-in-{m}", "{n} In {m}"]),
    minus=st.sampled_from(["", "-", "−"]),
)
def test_a_ratio_passes_only_at_its_share(n, extra, form, minus):
    """Delta review D1-1 and final review F1, for every "N in M" in any case
    and with any minus: N/M, signed as N is, passes, and N, M, N% and M% fail
    unless they round to N/M."""
    m = n + extra
    raw = minus + form.format(n=n, m=m)
    share = (-1 if minus else 1) * n / m
    assert problems(_share(raw, share)) == []
    assert any("opposite sign" in p for p in problems(_share(raw, -share)))
    for wrong in (n, m, n / 100, m / 100, 100 * n / m):
        if not math.isclose(wrong, n / m, rel_tol=1e-3):
            found = problems(_share(raw, wrong))
            assert any(
                "at a stated scale" in p or "opposite sign" in p for p in found
            ), (raw, wrong)


SAY = {v: w for w, v in (ONES | TENS).items()}


def _say(n, a=False, hyphen=True, joined=True):
    """n, from 1 to 999, in words as a producer might print it: "a" or "one"
    hundred, "twenty-five" or "twenty five", "and" after the hundreds or not."""
    if n >= 100:
        head, rest = divmod(n, 100)
        out = ("a" if a and head == 1 else SAY[head]) + " hundred"
        if rest:
            out += " and " if joined else " "
            out += _say(rest, a, hyphen, joined)
        return out
    if n in SAY:
        return SAY[n]
    tens, unit = divmod(n, 10)
    return SAY[10 * tens] + ("-" if hyphen else " ") + SAY[unit]


STYLES = st.tuples(st.booleans(), st.booleans(), st.booleans())


@settings(max_examples=300, deadline=None)
@given(
    n=st.integers(1, 999),
    m=st.integers(1, 999),
    styles=STYLES,
    joint=st.sampled_from(["in", "IN", "in every", "In Every", "out of", "OUT OF"]),
    multiplier=st.sampled_from(
        [("", 1), (" thousand", 1e3), (" million", 1e6), (" billion", 1e9)]
    ),
    wrong=st.floats(0.001, 1000),
)
def test_a_worded_ratio_passes_only_at_its_share(
    n, m, styles, joint, multiplier, wrong
):
    """Final review F1: number words up to the hundreds give a ratio as
    numerals do, after "in", "in every" or "out of" and with a multiplier on
    M. The share passes, and so does nothing else, N and M included."""
    word, factor = multiplier
    raw = f"{_say(n, *styles)} {joint} {_say(m, *styles)}{word}"
    share = n / (m * factor)
    assert problems(_share(raw, share, "share as printed")) == [], raw
    for bad in (wrong, n, m, m * factor, n / m):
        if not math.isclose(bad, share, rel_tol=1e-3):
            found = problems(_share(raw, bad, "share as printed"))
            assert any("at a stated scale" in p for p in found), (raw, bad)


@pytest.mark.parametrize(
    ("raw", "share", "wrongs"),
    [
        ("1 in 2 million", 5e-7, (0.5, 1, 2, 2e6)),
        ("1 in 2m", 5e-7, (0.5, 2, 2e6)),
        ("1 in 2.5 million", 4e-7, (0.4, 2.5, 2.5e6)),
        ("1 in 4bn", 2.5e-10, (0.25, 4, 4e9)),
        ("one in a million", 1e-6, (1, 1e6)),
        ("one in a thousand", 1e-3, (1, 1e3)),
        ("one in ten thousand", 1e-4, (0.1, 10, 1e4)),
        ("one in two hundred", 5e-3, (0.5, 2, 200)),
        ("1 in 2 hundred", 5e-3, (0.5, 2, 200)),
        ("one in a hundred thousand", 1e-5, (0.01, 100, 1e5)),
        ("one in twenty-five", 0.04, (0.05, 0.2, 1, 25)),
        ("one in a hundred and twenty", 1 / 120, (0.01, 0.05, 120)),
        ("3 out of 10", 0.3, (3, 10, 30)),
        ("3-out-of-10", 0.3, (3, 10)),
        ("three out of ten", 0.3, (3, 10)),
        ("1 in every 4", 0.25, (1, 4, 25)),
        ("one in every five", 0.2, (1, 5)),
        ("1 in every 2000", 0.0005, (1, 2000)),
        ("1 out of 2000", 0.0005, (1, 2000)),
        ("1 in 2000 million", 5e-10, (0.0005, 2000, 2e9)),
    ],
)
def test_a_ratio_with_a_multiplier_or_another_joint_is_its_share(raw, share, wrongs):
    """A multiplier on M scales M, so "1 in 2 million" is 5e-7, never 0.5.
    Number words run to the hundreds, and "in every" and "out of" print a
    ratio as "in" does. A year after "in every" or "out of", or before a
    multiplier, is a denominator. The share passes; N, M, and the share
    without the multiplier don't."""
    assert problems(_share(raw, share, "share as printed")) == []
    for wrong in wrongs:
        found = problems(_share(raw, wrong, "share as printed"))
        assert any("at a stated scale" in p for p in found), (raw, wrong, found)


@pytest.mark.parametrize(
    ("raw", "value", "share"),
    [
        ("£5 in 10 years", 5, 0.5),
        ("-£5 in 10", -5, -0.5),
        ("$3 in 4", 3, 0.75),
        ("1 in 2 millionths", 1, 0.5),
        ("1 in 2 million-strong", 2e6, 0.5),
        ("1 in 2 thousand million", 2e6, 0.5),
    ],
)
def test_a_number_after_a_currency_sign_or_before_an_unread_multiplier_is_no_ratio(
    raw, value, share
):
    """A number after a currency sign starts no ratio, and a ratio whose
    multiplier won't read is none: each number counts at its scale, and the
    ratio's share without its multiplier fails."""
    assert problems(_share(raw, value, "as printed")) == []
    found = problems(_share(raw, share, "as printed"))
    assert any("at a stated scale" in p for p in found), (raw, found)


def test_a_ratio_s_multiplier_scales_only_the_ratio():
    """ "million" in "1 in 2 million" scales M, not the string's other
    numbers: at the stated factor of 1, the 3 in "3 (1 in 2 million)" is 3."""
    note = "count as printed x 1"
    assert problems(_share("3 (1 in 2 million)", 3, note)) == []
    found = problems(_share("3 (1 in 2 million)", 3e6, note))
    assert any("at a stated scale" in p for p in found), found


@pytest.mark.parametrize(
    ("raw", "share", "wrongs"),
    [
        ("a fifth", 0.2, (5, 0.5, 20)),
        ("less than a fifth", 0.2, (5, 20)),
        ("about three-fifths", 0.6, (3, 5, 0.35, 60)),
        ("three fifths", 0.6, (3, 5)),
        ("another quarter", 0.25, (4, 0.75, 25)),
        ("around one-tenth", 0.1, (1, 10)),
        ("seven eighths", 0.875, (7, 8, 0.78)),
        ("an eighth", 0.125, (8, 0.18)),
        ("two-thirds", 2 / 3, (2, 3, 0.23)),
        ("three quarters", 0.75, (3, 4, 0.34)),
        ("half", 0.5, (2, 50)),
        ("a half", 0.5, (2,)),
    ],
)
def test_a_worded_fraction_in_any_form_is_its_share(raw, share, wrongs):
    """A worded fraction is a numerator ("a", "an", "another", or one to
    ten) and a denominator from a half to a tenth, with a space or a hyphen
    between them, or "half" alone. The share passes; its two numbers, and 100
    times the share on a row not in percent units, don't."""
    assert problems(_share(raw, share, "share as printed")) == []
    for wrong in wrongs:
        found = problems(_share(raw, wrong, "share as printed"))
        assert any("at a stated scale" in p for p in found), (raw, wrong, found)


@pytest.mark.parametrize("raw", ["a third-party", "the third year", "per quarter"])
def test_an_ordinal_or_a_compound_is_no_fraction(raw):
    """ "third" in "a third-party" or "the third year", and "quarter" without
    a numerator, print no fraction, so the row compares nothing."""
    assert problems(_share(raw, 7, "as printed")) == []


@pytest.mark.parametrize(
    ("raw", "share"), [("around one-tenth", 0.1), ("1 in 4", 0.25), ("a third", 1 / 3)]
)
def test_a_percent_row_stores_its_share_in_percent_units(raw, share):
    """Resolution Foundation's "around one-tenth" (row 114) is 10 on its
    `unit_concept: percent` row. A percent row stores 100 times the share,
    and every other row the share itself."""

    def row(value, unit):
        return mutated(
            value_raw=raw,
            quote=raw,
            value=value,
            normalization="as printed",
            unit_concept=unit,
        )

    assert problems(row(100 * share, "percent")) == []
    assert problems(row(share, "share")) == []
    for value, unit in ((share, "percent"), (100 * share, "share")):
        found = problems(row(value, unit))
        assert any("at a stated scale" in p for p in found), (raw, value, unit)


@pytest.mark.parametrize(
    ("raw", "value", "wrongs"),
    [
        ("four", 4, (5, 40)),
        ("one", 1, (2,)),
        ("twenty-five", 25, (20, 5)),
        ("a hundred and five", 105, (100, 5)),
        ("one million", 1e6, (1, 2e6)),
        ("over a million", 1e6, (1, 1e3)),
        ("a hundred thousand", 1e5, (100, 1e3)),
    ],
)
def test_a_number_printed_only_in_words_is_that_number(raw, value, wrongs):
    """A row that prints its number only in words (OBR's "four", row 2664)
    gives those words, at value_raw's scale ("over a million" is 1e6). Before,
    it compared nothing and passed whatever its value."""
    assert problems(_share(raw, value, "printed in words")) == []
    for wrong in wrongs:
        found = problems(_share(raw, wrong, "printed in words"))
        assert any("at a stated scale" in p for p in found), (raw, wrong, found)


@settings(max_examples=300, deadline=None)
@given(n=st.integers(1, 999), styles=STYLES, off=st.integers(1, 50))
def test_any_number_in_words_reads_as_that_number(n, styles, off):
    """Every number from one to nine hundred and ninety-nine, in any of the
    ways _say prints it, reads back as itself, and n + off doesn't."""
    raw = _say(n, *styles)
    assert problems(_share(raw, n, "printed in words")) == [], raw
    found = problems(_share(raw, n + off, "printed in words"))
    assert any("at a stated scale" in p for p in found), (raw, n + off)


@pytest.mark.parametrize("raw", ["two-child limit", "one-off", "four"])
def test_number_words_in_a_compound_or_on_a_categorical_row_compare_nothing(raw):
    """A number word inside a hyphenated word ("two-child") prints no number,
    and a categorical row's words are its label, never its value."""
    if raw != "four":
        assert problems(_share(raw, 7, "as printed")) == []
    label = mutated(
        value_raw=raw,
        quote=raw,
        value=7,
        normalization="rating as printed",
        value_kind="categorical",
    )
    assert problems(label) == []


@settings(max_examples=300, deadline=None)
@given(tenths=st.integers(-99_999, 99_999), how=st.integers(0, 2))
def test_a_printed_percentage_is_its_share_to_floating_point_error(tenths, how):
    """Final review F2: a share computed from a printed percentage in any
    usual way passes, and any value 1e-12 or more away fails."""
    raw = f"{tenths / 10}%"
    share = (tenths / 10 / 100, tenths / 1000, float(raw[:-1]) * 0.01)[how]
    note = "per cent / 100 -> share"
    assert problems(_share(raw, share, note)) == []
    moved = share + (1e-12 if share >= 0 else -1e-12)
    assert any("at a stated scale" in p for p in problems(_share(raw, moved, note)))


@settings(max_examples=200, deadline=None)
@given(cell=st.integers(-9999, 9999), off=st.integers(1, 10**8), up=st.booleans())
def test_a_money_cell_passes_only_at_its_exact_value(cell, off, up):
    """Delta review D1-1 and final review F2: a cell printed in £ million is
    that many millions, to floating-point error (four units in the last
    place). £1 off any cell under £10bn fails: the 0.1% rounding allowance
    covers a share of a printed fraction, nothing else."""
    raw = str(cell)
    quote = f"Line 1 | 2026-27: {raw}"
    exact = mutated(value_raw=raw, quote=quote, value=cell * 1e6)
    moved = mutated(
        value_raw=raw, quote=quote, value=cell * 1e6 + (off if up else -off)
    )
    assert problems(exact) == []
    assert any(
        "at a stated scale" in p or "opposite sign" in p for p in problems(moved)
    )


def test_malformed_rows_are_reported_not_raised():
    """review A H-6(h)."""
    for row in (
        mutated(conditions=["fy"]),
        mutated(publication=None),
        mutated(measure_key=["x"]),
        mutated(quote=None),
        "not a row",
    ):
        assert problems(row), row


def test_rule_4_holds_whatever_the_title_case():
    row = mutated(
        publication__title="Budget 2026: IMPACT ON HOUSEHOLDS",
        value_kind="approx_chart_reading",
    )
    assert any("rule 4" in p for p in problems(row))


@pytest.mark.parametrize(
    ("locator", "bar_reading"),
    [
        ("Figure 1.A, decile 3 bar", True),
        ("p.5, Figure 1.B, top bar", True),
        ("paragraph 1.7, p.8; discussion of Figure 1.A", False),
        ("paragraph 1.7; discussion of Figure 1.A", False),
        ("Figure 1.A data label, decile 3", False),
        ("Table 2.C, decile 3", False),
        ("Table 2.C, p.16, decile 1, column 1 adult", False),
        ("paragraph 2.4, p.14; source Table 2.B, p.13", False),
        # final review F4: a secondary or negated reference names nothing
        ("Figure 1.A, decile 3 bar; no data labels", True),
        ("Figure 1.A, decile 3 bar; see paragraph 1.7", True),
        ("Figure 1.A decile 3 bar, paragraph 1.7", True),
        ("Figure 1.A decile 3 bar beside paragraph 1.7", True),
        ("Figure 1.A (no data labels), decile 3", True),
        ("no data label; paragraph 1.7, Figure 1.A", True),
        ("paragraph 1.7; bar reading from Figure 1.A", True),
        ("Figure 1.B; data label", True),
        ("data label for decile 3, Figure 1.A", False),
        # the figure in other spellings, and negations in other words
        ("Figures 1.A and 1.B, decile 3 bars", True),
        ("Fig. 1.A, decile 3 bar", True),
        ("Figure 1A, decile 3 bar", True),
        ("fig 1b; top bar", True),
        ("Figure 1.A data label missing, decile 3", True),
        ("Figure 1.A data label isn't printed", True),
        ("Figure 1.A data label absent", True),
        ("Figure 1.B lacks a data label", True),
        ("Fig. 1A data label, decile 3", False),
        ("Figures 1.A and 1.B data labels", False),
        ("Figure 1 below; paragraph 1.7", False),
        ("Table 2.C; config 1a", False),
    ],
)
def test_rule_4_reads_where_the_locator_places_the_number(locator, bar_reading):
    """README rule 4: a locator that places the number on Figure 1.A's or
    1.B's bars marks a bar reading; one whose leading reference names the
    paragraph, table or data label printing it doesn't (delta review D1:
    red book row 357's 20% sits in paragraph 1.7; final review F4)."""
    row = mutated(
        publication__title="Budget 2026: Impact on households",
        publication__locator=locator,
    )
    assert any("rule 4" in p for p in problems(row)) == bar_reading


@pytest.mark.parametrize(
    "negated",
    [
        "no data labels",
        "not a data label",
        "none of its data labels",
        "never a data label",
        "without data labels",
        "data label missing",
        "data label absent",
        "lacks a data label",
        "lacking data labels",
        "unlabelled data label",
        "data label: unlabeled bars",
        "data label isn't printed",
        "data label isn’t printed",
    ],
)
def test_rule_4_reads_a_negated_data_label_as_a_bar_reading(negated):
    """Final review F4: a leading reference that negates its data label, in
    any of these words, places the number on a bar."""
    assert reads_a_bar(f"Figure 1.A {negated}")
    assert not reads_a_bar("Figure 1.A data label")


# Leading references that say where HM Treasury prints a number, and ones
# that don't; and the parts of a locator that name Figure 1.A or 1.B.
PRINTING = [
    "paragraph 1.7",
    "Table 2.C",
    "Box 1.A",
    "Figure 1.A data label",
    "Fig. 1B data labels",
    "data label",
]
NOT_PRINTING = [
    "Figure 1.B",
    "Figures 1.A and 1.B",
    "Figure 1.A, decile 3 bar",
    "p.8",
    "no data labels",
    "data label missing",
    "Figure 1.A data label isn't shown",
]
NAMES_FIGURE = {
    "Figure 1.A data label",
    "Fig. 1B data labels",
    "Figure 1.B",
    "Figures 1.A and 1.B",
    "Figure 1.A, decile 3 bar",
    "Figure 1.A data label isn't shown",
    "discussion of Figure 1.A",
    "fig 1a",
}


@settings(max_examples=300, deadline=None)
@given(
    lead=st.sampled_from(PRINTING + NOT_PRINTING),
    rest=st.lists(
        st.sampled_from(
            [
                "p.8",
                "see paragraph 1.7",
                "no data labels",
                "discussion of Figure 1.A",
                "fig 1a",
                "decile 3",
                "data label",
                "Table 2.C",
            ]
        ),
        max_size=3,
    ),
)
def test_rule_4_follows_the_leading_reference(lead, rest):
    """Final review F4: where a locator names Figure 1.A or 1.B, in any
    spelling, only its leading reference, positively naming a paragraph,
    table, box or data label, places the number where HM Treasury prints it;
    anything later in the locator places nothing."""
    locator = "; ".join([lead, *rest])
    names_figure = any(part in NAMES_FIGURE for part in [lead, *rest])
    assert reads_a_bar(locator) == (names_figure and lead not in PRINTING)


def test_a_component_with_its_measure_or_a_proposed_key_is_valid():
    """README rule 9: a part of one measure keeps that measure's key; a part
    of a measure with no Table 6.1 line keeps that measure's proposed key."""
    keyed = mutated(
        conditions__row_type="measure_component", conditions__component="Wales"
    )
    proposed = mutated(
        measure_key=None,
        conditions__row_type="measure_component",
        conditions__component="Capital AME",
        conditions__proposed_measure_key="ab2026__package_fiscally_neutral_x",
    )
    assert problems(keyed) == []
    assert problems(proposed) == []


@settings(max_examples=200, deadline=None)
@given(start=st.integers(1945, 2073), offset=st.integers(-3, 3))
def test_an_fy_row_is_valid_only_at_the_fy_end_year(start, offset):
    fy = f"{start}-{(start + 1) % 100:02d}"
    row = mutated(conditions__fy=fy, period=start + 1 + offset)
    end_year_problem = any("is not the end year" in p for p in problems(row))
    assert end_year_problem == (offset != 0)


@settings(max_examples=200, deadline=None)
@given(
    words=st.integers(1, 40),
    source=st.sampled_from(["ifs", "resolution_foundation", *sorted(OGL)]),
)
def test_only_ogl_quotes_may_run_to_15_words(words, source):
    """README rule 6: under 15 words outside the Open Government Licence."""
    row = mutated(source=source, quote=" ".join(["-2625"] * words))
    long_quote = any("15 or more words" in p for p in problems(row))
    assert long_quote == (source not in OGL and words >= 15)


def _write(fam, rows):
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb", mtime=0, filename="") as gz:
        for r in rows:
            gz.write((json.dumps(r, sort_keys=True) + "\n").encode())
    (fam / "claims_staged.jsonl.gz").write_bytes(buf.getvalue())


def _family_with_a_proposed_key(
    tmp_path, notes_extra, key="ab2026__package_test_scope"
):
    fam = tmp_path / "uk_test_family"
    shutil.copytree(FAMILY, fam)
    rows = read_rows(fam)
    i = rows.index(BASE)
    rows[i]["measure_key"] = None
    rows[i]["conditions"]["proposed_measure_key"] = key
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb", mtime=0, filename="") as gz:
        for r in rows:
            gz.write((json.dumps(r, sort_keys=True) + "\n").encode())
    (fam / "claims_staged.jsonl.gz").write_bytes(buf.getvalue())
    with (fam / "NOTES.md").open("a") as fh:
        fh.write(notes_extra)
    return fam


def test_a_family_scopes_every_proposed_key_it_uses_in_its_notes(tmp_path):
    unscoped = _family_with_a_proposed_key(tmp_path / "a", "")
    scoped = _family_with_a_proposed_key(
        tmp_path / "b", "\n- `ab2026__package_test_scope`: Table 6.1 line 1.\n"
    )
    assert family_problems(unscoped) == [
        "NOTES.md does not give the scope of ab2026__package_test_scope"
    ]
    assert family_problems(scoped) == []


def test_a_scope_for_a_longer_key_does_not_scope_its_prefix(tmp_path):
    """review A H-6(g): NOTES scopes a key as a whole token."""
    fam = _family_with_a_proposed_key(
        tmp_path,
        "\n- `ab2026__package_test_scope_wider`: Table 6.1 lines 1-2.\n",
        key="ab2026__package_test_scope",
    )
    assert family_problems(fam) == [
        "NOTES.md does not give the scope of ab2026__package_test_scope"
    ]


def _family_with_copies(tmp_path, n, factor=1.0):
    fam = tmp_path / "uk_test_family"
    shutil.copytree(FAMILY, fam)
    rows = read_rows(fam)
    i = rows.index(BASE)
    extra = copy.deepcopy(BASE)
    extra["value"] = BASE["value"] * factor
    rows[i + 1 : i + 1] = [copy.deepcopy(extra) for _ in range(n)]
    _write(fam, rows)
    return fam


def test_three_printings_of_one_claim_are_a_problem(tmp_path):
    """review A H-3: the AB2025 ingest merges two rows that share a claim
    identity and raises on three (red book rows 179, 191 and 200)."""
    assert family_problems(_family_with_copies(tmp_path / "a", 1)) == []
    triple = family_problems(_family_with_copies(tmp_path / "b", 2))
    assert len(triple) == 1 and "more than 2" in triple[0], triple


def test_a_pair_that_disagrees_is_a_problem(tmp_path):
    # a value off by 1% (value_raw unchanged) is also a value_raw mismatch
    found = family_problems(_family_with_copies(tmp_path, 1, factor=1.01))
    assert any("differ by over 0.5%" in p for p in found), found


def _family(tmp_path):
    fam = tmp_path / "uk_test_family"
    shutil.copytree(FAMILY, fam)
    return fam


def _rewrite_manifest(fam, edit):
    lines = [
        json.loads(x) for x in (fam / "manifest.jsonl").read_text().splitlines() if x
    ]
    lines = edit(lines)
    (fam / "manifest.jsonl").write_text("".join(json.dumps(m) + "\n" for m in lines))


@pytest.mark.parametrize(
    ("edit", "expected"),
    [
        (lambda m: [{**m[0], "sha256": "abc"}, *m[1:]], "sha256 is not a sha256"),
        (lambda m: [{**m[0], "retrieved": ""}, *m[1:]], "needs url, title"),
        # a field that isn't text, and a problem that names its line when the
        # url isn't text
        (lambda m: [{**m[0], "title": 5}, *m[1:]], "needs url, title"),
        (lambda m: [{**m[0], "retrieved": "  "}, *m[1:]], "needs url, title"),
        (
            lambda m: [{**m[0], "url": ["x"]}, *m[1:]],
            "manifest line 0: needs url, title and retrieved as text",
        ),
        (
            lambda m: [*m[:1], {**m[1], "url": 7, "sha256": "abc"}, *m[2:]],
            "manifest line 1: sha256 is not a sha256",
        ),
        (lambda m: [*m, m[0]], "lists a primary twice"),
        (lambda m: m[1:], "primary_sha256 is not in manifest.jsonl"),
        (lambda m: [*m, "not an object"], "a line that is not an object"),
    ],
)
def test_each_manifest_rule_broken_is_a_problem(tmp_path, edit, expected):
    """review A H-7: the manifest checks, reached by a test."""
    fam = _family(tmp_path)
    _rewrite_manifest(fam, edit)
    found = family_problems(fam)
    assert any(expected in p for p in found), found[:5]


def test_a_family_missing_a_file_is_a_problem(tmp_path):
    fam = _family(tmp_path)
    (fam / "NOTES.md").unlink()
    assert family_problems(fam) == ["uk_test_family: missing ['NOTES.md']"]


@pytest.mark.parametrize(
    ("extra", "expected"),
    [
        # a copy of the base row whose value is a string: the pair check
        # compares the two values
        ([{**BASE, "value": "-2625000000"}], "value is not a number"),
        (["not a row", None], "row is not an object"),
        (
            [mutated(measure_key=None, conditions__proposed_measure_key=["ab2026__x"])],
            "row is malformed",
        ),
        (
            [mutated(publication__primary_sha256=["abc"])],
            "primary_sha256 is not in manifest.jsonl",
        ),
        # final review F3: a copy of the base row without its value, and one
        # whose value is an integer too large for a float, pair with it
        ([{k: v for k, v in BASE.items() if k != "value"}], "missing fields"),
        ([{**BASE, "value": 10**400}], "value is not finite"),
    ],
)
def test_a_family_reports_malformed_rows_without_raising(tmp_path, extra, expected):
    """Delta review D1-3 and final review F3: family_problems reports a
    malformed row as row_problems does. The pair check, the proposed-key
    scope check and the manifest lookup skip a value, key or hash they can't
    compare."""
    fam = _family(tmp_path)
    _write(fam, read_rows(fam) + extra)
    found = family_problems(fam)
    assert any(expected in p for p in found), found[:5]


def test_a_family_reports_unreadable_lines_and_files(tmp_path):
    """Final review F3: a line that isn't JSON, or a file that can't be read,
    is a problem, never an exception."""
    fam = _family(tmp_path)
    gz = fam / "claims_staged.jsonl.gz"
    text = gzip.decompress(gz.read_bytes()).decode()
    gz.write_bytes(gzip.compress((text + "{not json\n").encode(), mtime=0))
    (fam / "manifest.jsonl").write_text((fam / "manifest.jsonl").read_text() + "[1,\n")
    found = family_problems(fam)
    assert [p for p in found if p.startswith("row 768")] == ["row 768: is not JSON"]
    assert [p for p in found if p.startswith("manifest")] == [
        "manifest line 2: is not JSON"
    ]
    gz.write_bytes(b"not gzip")
    found = family_problems(fam)
    assert "claims_staged.jsonl.gz cannot be read (BadGzipFile)" in found, found[:5]


def test_a_field_nested_too_deep_to_print_is_a_problem():
    """Final review F3: a field nested too deep to print, or to encode as a
    claim identity, is a problem, never an exception."""
    deep = []
    for _ in range(100_000):
        deep = [deep]
    found = problems(mutated(period=deep))
    assert [p for p in found if p.startswith("row is malformed (RecursionError")]
    nested = mutated(conditions__geography_note=deep)
    assert duplicate_problems([nested, nested]) == []


# Any JSON value, with the integers JSON allows but a float can't hold.
JSON = st.recursive(
    st.none()
    | st.booleans()
    | st.integers()
    | st.floats()
    | st.text(max_size=12)
    | st.sampled_from([10**400, -(10**400), "1 in 4", "-2,625", ""]),
    lambda inner: (
        st.lists(inner, max_size=3)
        | st.dictionaries(st.text(max_size=8), inner, max_size=3)
    ),
    max_leaves=8,
)
FIELDS = sorted(
    [*BASE]
    + [f"conditions__{k}" for k in BASE["conditions"]]
    + [f"publication__{k}" for k in BASE["publication"]]
)


def _changed(changes):
    """BASE with each field set to a value, or deleted (...), nested fields
    first, so a later change to their parent can't strand them."""
    row = copy.deepcopy(BASE)
    for path in sorted(changes, key=lambda p: -p.count("__")):
        *parents, leaf = path.split("__")
        target = row
        for p in parents:
            target = target[p]
        if changes[path] is ...:
            target.pop(leaf, None)
        else:
            target[leaf] = changes[path]
    return row


@settings(max_examples=400, deadline=None)
@given(
    changes=st.dictionaries(
        st.sampled_from(FIELDS), JSON | st.just(...), min_size=1, max_size=4
    )
)
def test_any_malformed_row_gives_problems_never_an_exception(changes):
    """Final review F3, for every input: row_problems, the pair check and the
    proposed-key scan return strings for a row with any field changed to any
    JSON value or deleted, alone and next to copies of itself and BASE."""
    row = _changed(changes)
    found = problems(row)
    assert isinstance(found, list) and all(isinstance(p, str) for p in found)
    pairs = duplicate_problems([BASE, row]) + duplicate_problems([row, row])
    assert all(isinstance(p, str) for p in pairs)
    assert isinstance(proposed_keys([row, BASE]), set)


@settings(max_examples=200, deadline=None)
@given(row=JSON)
def test_any_json_value_as_a_row_gives_problems_never_an_exception(row):
    found = problems(row)
    assert found and all(isinstance(p, str) for p in found)
    assert all(isinstance(p, str) for p in duplicate_problems([row, row, BASE]))
    assert isinstance(proposed_keys([row]), set)


@settings(max_examples=60, deadline=None)
@given(lines=st.lists(JSON.map(json.dumps) | st.text(max_size=30), max_size=4))
def test_any_family_file_gives_problems_never_an_exception(lines):
    """Final review F3: family_problems reads any line, JSON or not."""
    with tempfile.TemporaryDirectory() as d:
        fam = Path(d) / "uk_fuzz"
        fam.mkdir()
        (fam / "NOTES.md").write_text("Fuzzed family.\n")
        shutil.copy(FAMILY / "manifest.jsonl", fam / "manifest.jsonl")
        body = "".join(
            line.replace("\n", " ").replace("\r", " ") + "\n"
            for line in [json.dumps(BASE), *lines]
        )
        (fam / "claims_staged.jsonl.gz").write_bytes(
            gzip.compress(body.encode(), mtime=0)
        )
        found = family_problems(fam)
    assert all(isinstance(p, str) for p in found)
