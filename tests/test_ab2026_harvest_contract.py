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
from itertools import product
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from pipeline.ab2026_harvest_contract import (
    OGL,
    duplicate_problems,
    enums,
    family_problems,
    proposed_keys,
    read_rows,
    reads_a_bar,
    registry_keys,
    row_problems,
    type_problems,
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
        ({"measure_key": ["ab2026__x"]}, "measure_key is not a string or null"),
        ({"publication": None}, "publication is not an object"),
        ({"value_raw": None}, "value_raw is not a string"),
        # delta review D1-1: a printed £m cell is that many millions exactly
        ({"value": -2626312500}, "at a stated scale"),
        ({"value": -2625100000}, "at a stated scale"),
        # delta review D1: each arm the dedicated tests didn't reach
        (
            {"conditions__component": " ", "conditions__row_type": "measure_total"},
            "a component row has row_type",
        ),
        ({"conditions__component": 1}, "condition 'component' is not a string"),
        (
            {"measure_key": None, "conditions__proposed_measure_key": ["ab2026__x"]},
            "condition 'proposed_measure_key' is not a string",
        ),
        # final review F2: £1 or £2 off a £m cell is no floating-point error
        ({"value": -2625000001}, "at a stated scale"),
        ({"value": -2625000002}, "at a stated scale"),
        ({"value": -2624999999.5}, "at a stated scale"),
        # final review F3: an integer too large for a float
        ({"value": 10**400}, "value is not finite"),
        ({"value": -(10**400)}, "value is not finite"),
        # delta review R4: a field of a type the AB2025 row contract doesn't
        # allow
        ({"source_model": []}, "source_model is not a string"),
        ({"reform_hint": []}, "reform_hint is not a string or null"),
        ({"baseline_policy": []}, "baseline_policy is not a string or null"),
        ({"source_table": []}, "source_table is not a string or null"),
        ({"source_column": []}, "source_column is not a string or null"),
        ({"attribution": ["own"]}, "attribution is not a string"),
        ({"period": "2027"}, "period is not an integer"),
        ({"period": True}, "period is not an integer"),
        ({"publication__locator": 7}, "publication.locator is not a string"),
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


def _cant_read(raw, normalization="as printed"):
    """The checker reports raw as unreadable at every value we try."""
    values = (0, 0.25, 0.5, 1, 4, 5, 19, 25, 2e6, 1e-6, -1, -0.25)
    return all(
        any("can't read" in p for p in problems(_share(raw, v, normalization)))
        for v in values
    )


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


@pytest.mark.parametrize(
    "raw",
    [
        "5 in 2027",
        "40,000 in 2030",
        "two million in 2030",
        "1-in-2030",
        "5 in -2027",
        "5 in −2027",
        "5 in +2027",
        "5 in 2010",
        "5 in 2099",
        "5 in 2026-27",
        "5 in 2026–27",
        "5 in 2026-2027",
    ],
)
def test_a_year_after_in_is_a_problem(raw):
    """The checker reads no ratio with a year from 2010 to 2099 after a bare
    "in", and can't read "5 in 2026-27": we narrow value_raw to the number the
    row stores."""
    assert _cant_read(raw)


@pytest.mark.parametrize(
    ("raw", "quotient"),
    [
        ("5 in 2027", 5 / 2027),
        ("40,000 in 2030", 40_000 / 2030),
        ("two million in 2030", 2e6 / 2030),
        ("1-in-2030", 1 / 2030),
    ],
)
def test_a_year_gives_no_quotient(raw, quotient):
    """A year after "in" counts no denominator, so its quotient is no value."""
    found = problems(_share(raw, quotient, "as printed"))
    assert any("can't read" in p for p in found), (raw, found)


@pytest.mark.parametrize(
    ("raw", "share"),
    [
        ("1 in 2000", 1 / 2000),
        ("1 in 2009", 1 / 2009),
        ("1 in 2100", 1 / 2100),
        ("1 in 2,030", 1 / 2030),
        ("one in every 2027", 1 / 2027),
        ("1 out of 2027", 1 / 2027),
        ("1 in 2030 million", 1 / 2.03e9),
    ],
)
def test_a_denominator_no_year_could_print_stays_a_ratio(raw, share):
    """A number outside 2010 to 2099, a comma, a multiplier, "every" or "out of"
    marks a denominator: the share passes, and the numbers alone fail."""
    assert problems(_share(raw, share, "as printed")) == []
    for alone in (1, 1 / share):
        found = problems(_share(raw, alone, "as printed"))
        assert any("at a stated scale" in p for p in found), (raw, alone, found)


@pytest.mark.parametrize(
    "normalization",
    [
        "as printed",
        "N in M -> N/M",
        "1 in 2000 -> 0.0005",
        "£ million x 1,000,000",
        "/ 100",
    ],
)
def test_a_ratio_reads_the_same_under_any_normalization(normalization):
    """A ratio's share takes no factor from the normalization: "1 in 2000"
    passes at 0.0005 and fails at 1, at 2000 and at the share at that factor."""
    assert problems(_share("1 in 2000", 0.0005, normalization)) == []
    for wrong in (1, 2000, 500, 0.05):
        found = problems(_share("1 in 2000", wrong, normalization))
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


# Number words as a producer prints them, written out here apart from the
# checker's own lists (delta review R1).
SAY = dict(
    enumerate(
        "zero one two three four five six seven eight nine ten eleven twelve"
        " thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
    )
) | {
    20: "twenty",
    30: "thirty",
    40: "forty",
    50: "fifty",
    60: "sixty",
    70: "seventy",
    80: "eighty",
    90: "ninety",
}


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
JOINTS = [
    "in",
    "IN",
    "in every",
    "In Every",
    "out of",
    "OUT OF",
    "out of every",
    "Out Of Every",
]


@settings(max_examples=300, deadline=None)
@given(
    n=st.integers(1, 999),
    m=st.integers(1, 999),
    styles=STYLES,
    joint=st.sampled_from(JOINTS),
    multiplier=st.sampled_from(
        [("", 1), (" thousand", 1e3), (" million", 1e6), (" billion", 1e9)]
    ),
    wrong=st.floats(0.001, 1000),
)
def test_a_worded_ratio_passes_only_at_its_share(
    n, m, styles, joint, multiplier, wrong
):
    """Final review F1: number words up to the hundreds give a ratio as
    numerals do, after "in", "in every", "out of" or "out of every" and with
    a multiplier on M. The share passes, and so does nothing else, N and M
    included."""
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
        ("one out of every five", 0.2, (1, 5)),
        ("1 out of every 4", 0.25, (1, 4, 25)),
        ("1-out-of-every-4", 0.25, (1, 4)),
        (".5 in 4", 0.125, (0.5, 4)),
        ("1e3 in 4", 250, (1000, 4)),
        ("1 in .5", 2, (1, 0.5)),
        ("1 in +4", 0.25, (1, 4)),
        ("+1 in 4", 0.25, (1, 4)),
    ],
)
def test_a_ratio_with_a_multiplier_or_another_joint_is_its_share(raw, share, wrongs):
    """A multiplier on M scales M, so "1 in 2 million" is 5e-7, never 0.5.
    Number words run to the hundreds, and "in every", "out of" and "out of
    every" print a ratio as "in" does. The share passes; N, M, and the share
    without the multiplier don't."""
    assert problems(_share(raw, share, "share as printed")) == []
    for wrong in wrongs:
        found = problems(_share(raw, wrong, "share as printed"))
        assert any("at a stated scale" in p for p in found), (raw, wrong, found)


@pytest.mark.parametrize(
    "raw",
    [
        "£5 in 10 years",
        "£ 5 in 10 years",
        "£5 in 10",
        "-£5 in 10",
        "£-5 in 10",
        "$3 in 4",
        "COVID-19 in 10",
        "Q1 in 4",
        "£5 in 2027",
    ],
)
def test_a_ratio_with_a_currency_sign_or_in_a_name_is_a_problem(raw):
    """A ratio takes no currency sign, and "COVID-19 in 10" names something,
    so the checker reads neither the numbers nor a share at any value."""
    assert _cant_read(raw)


@pytest.mark.parametrize(
    ("raw", "share", "wrongs"),
    [
        ("twenty-one in a hundred", 0.21, (0.01, 1, 21, 100)),
        ("twenty one in a hundred", 0.21, (0.01, 21, 100)),
        ("one in twenty-five", 0.04, (42, 0.2, 1, 25)),
    ],
)
def test_a_compound_number_reads_whole(raw, share, wrongs):
    """Delta review R1: the checker reads "twenty-one" as 21, never as its
    last word, so "twenty-one in a hundred" passes at 0.21 and at nothing
    else."""
    assert problems(_share(raw, share, "share as printed")) == []
    for wrong in wrongs:
        found = problems(_share(raw, wrong, "share as printed"))
        assert any("at a stated scale" in p for p in found), (raw, wrong, found)


@pytest.mark.parametrize(
    ("raw", "share"),
    [
        ("1 in -4", -0.25),
        ("-1 in -4", 0.25),
        ("1 in −4", -0.25),
        ("one in -four", -0.25),
        ("-1-in-4", -0.25),
    ],
)
def test_a_minus_on_either_number_signs_the_share(raw, share):
    """Delta review R1: a minus after the spaces before M signs the share as
    a minus before N does, so "1 in -4" passes at -0.25 and fails at 0.25."""
    assert problems(_share(raw, share)) == []
    flipped = problems(_share(raw, -share))
    assert any("opposite sign" in p for p in flipped), (raw, flipped)


# Strings that print no one number the checker can read. Each would give a
# wrong value or none if the checker read part of it.
CANT_READ = [
    # operands (delta review D1)
    "one in zero",
    "1 in 0",
    "1 in 1e999",
    "1e999 in 4",
    "1 in 1e308bn",
    "1e999",
    "1e999 and a half",
    "four million per cent",
    "zero million",
    "hundred",
    "million",
    # ranges on either side of a ratio (delta review D2)
    "4 - 5 in 10",
    "4—5 in 10",
    "1 in 4 - 5",
    "1 in 4—5",
    "1 in 4 to 5",
    "1 to 4 in 5",
    # numbers in words we don't list (delta reviews D3 and D4)
    "twenty-one fifths",
    "four million; five thousand",
    "one thousandth",
    "a millionth",
    "- four",
    # a ratio with more after it (cloud review A1, A3)
    "2 million in 5 years",
    "5bn in 10 years",
    "200,000 in five years",
    "one in a hundred and one in ten",
    "2025, 1 in 4",
    "a one-in-a-million chance",
    # separators (cloud review A5)
    "1 in-every 4",
    "1-in every-4",
    "1 out-of 4",
    "one in four m",
    # commas, signs and characters that print no number
    "1,2",
    "1,23",
    "1234,567",
    "12,34,567",
    "4.",
    "--4",
    "٣",
    "４",
    "4\u200b",
    "",
    "   ",
    # ranges the checker can't place
    "4 -5",
    "4- 5",
    "four-five",
    "4% to 5",
    "4bn-5",
    "1 to 2 to 3",
    # brackets
    "(25%)",
    "4 (five",
    "4 (five) (six)",
    "one third (about 33%)",
    "a thousand and one in a million",
    "a thousand and 21 in 100",
    "one in a thousand and one in a million",
    "twenty eleven in a hundred",
    "1 in 2 thousand million",
    "1 in 2 millionths",
    "1 in 2 thousands",
    "1 in 2 million-strong",
    "1 in 4-year-olds",
    "1 in 4th",
    "1 in 4–5",
    "4-5 in 10",
    "4–5 in 10",
    "1 in - 4",
    "1 - in 4",
    "1in 4",
    "1 in4",
    "1 in-4",
    "1-in 4",
    "1 in 0",
    # numerators and denominators past the list
    "eleven fifths",
    "twelve thirds",
    "one eleventh",
    # a range that runs downward in value and in size
    "2025-26",
    "5-4",
    "5 to 4",
    "4bn-5m",
    "1.5bn to 200m",
    "a half to a third",
    # a range with a word on its first number alone
    "4k to 5000",
    "1m-2000000",
    # a range that runs downward from a positive number (cloud review A-L2)
    "2 to -3",
    "4--5",
    "4 - -5",
    # a range from a fraction to a percentage, which could read either way
    "a third to 40%",
    "half to 40%",
    "a third to half a per cent",
    # a range that joins a percentage to a multiplier
    "4% to 2 million",
    "2 million to 4%",
    "4%-5bn",
    "0.1 percentage points to 2.5bn",
    # brackets that don't restate a share as a percentage
    "4 (five)",
    "4 (2025)",
    "£5bn (2027)",
    "one third (50%)",
    "1 in 4 (26%)",
    "25% (1 in 3)",
    "-1 in 4 (25%)",
    "half a million (50%)",
    "a third (33)",
    "a third (1 in 3)",
    "25% (25%)",
    "25% (0.25)",
    "0% (0%)",
    "1 in 4 (25-26%)",
    "25-26% (1 in 4)",
    "3 (1 in 2 million)",
    "1 in 3 (33.9%)",
    # a hyphen-joined ratio takes no minus on M, and a slash joins nothing
    "1-in--4",
    "4/5",
]


@pytest.mark.parametrize("raw", CANT_READ)
def test_a_string_the_checker_cant_read_is_a_problem(raw):
    """Delta reviews R1 and D1 to D4, and cloud review A1 to A5: a string that
    prints no one number in a form the checker knows gives a problem at any
    value, and the problem says so and asks us to narrow value_raw."""
    assert _cant_read(raw), raw
    found = problems(_share(raw, 1, "as printed"))
    assert any("narrow it to the number" in p for p in found), found


MULTIPLIER = st.sampled_from(
    [("", 1), (" thousand", 1e3), (" million", 1e6), (" billion", 1e9)]
    + [("bn", 1e9), ("m", 1e6), ("k", 1e3)]
)


def _operand(x, word, styles, multiplier):
    """x in words or digits, with a multiplier; a short multiplier ("bn")
    only after digits."""
    text, factor = multiplier
    if word and not text.startswith(" "):
        text, factor = "", 1
    return (_say(x, *styles) if word else str(x)) + text, factor


@settings(max_examples=500, deadline=None)
@given(
    n=st.integers(1, 999),
    m=st.integers(1, 999),
    words=st.tuples(st.booleans(), st.booleans()),
    styles=STYLES,
    multipliers=st.tuples(MULTIPLIER, MULTIPLIER),
    signs=st.tuples(st.sampled_from(["", "-", "−"]), st.sampled_from(["", "-", "−"])),
    joint=st.sampled_from(JOINTS),
    hyphens=st.booleans(),
)
def test_any_ratio_reads_whole_and_signed(
    n, m, words, styles, multipliers, signs, joint, hyphens
):
    """Delta review R1, for every ratio of numbers up to 999, in words or
    digits, with a multiplier or none on each number, a minus or none on N,
    and a minus or none on M when spaces join the ratio, joined all by spaces
    or all by hyphens: the signed share passes, and its opposite, N, M and the
    share without its multipliers fail."""
    top, f_top = _operand(n, words[0], styles, multipliers[0])
    bottom, f_bottom = _operand(m, words[1], styles, multipliers[1])
    sign_m = "" if hyphens else signs[1]
    if hyphens:
        raw = f"{signs[0]}{top}-{joint.replace(' ', '-')}-{bottom}"
    else:
        raw = f"{signs[0]}{top} {joint} {sign_m}{bottom}"
    share = (n * f_top) / (m * f_bottom) * (-1 if signs[0] else 1)
    share *= -1 if sign_m else 1
    assert problems(_share(raw, share, "share as printed")) == [], raw
    flipped = problems(_share(raw, -share, "share as printed"))
    assert any("opposite sign" in p for p in flipped), (raw, flipped)
    for bad in (n, m, n * f_top, m * f_bottom, n / m):
        if not math.isclose(bad, abs(share), rel_tol=1e-3):
            found = problems(_share(raw, bad, "share as printed"))
            assert any(
                "at a stated scale" in p or "opposite sign" in p for p in found
            ), (raw, bad, found)


@settings(max_examples=400, deadline=None)
@given(
    n=st.sampled_from(
        ["21", "twenty-one", "twenty one", "five", "105", "one hundred and five"]
    ),
    m=st.sampled_from(
        ["100", "a hundred", "twenty-five", "2 million", "a thousand", "4bn"]
    ),
    joint=st.sampled_from(["in", "in every", "out of"]),
    spoiler=st.sampled_from(
        ["one ", "3 ", "two million ", "a thousand and "]
        + [" thousand thousand", " millionths", "-year-olds", " 7"]
    ),
    value=st.floats(-1e12, 1e12, allow_nan=False),
)
def test_a_ratio_whose_number_runs_on_is_a_problem_at_any_value(
    n, m, joint, spoiler, value
):
    """Delta review R1, for ratios whose N or M runs on into more of a number
    ("one 21 in 100", "1 in 4 7") or into a word ("1 in 2 millionths", "1 in
    4-year-olds"): the checker reports each at any value, rather than read
    part of it."""
    if spoiler.endswith(" "):
        raw = f"{spoiler}{n} {joint} {m}"
    else:
        raw = f"{n} {joint} {m}{spoiler}"
    found = problems(_share(raw, value, "share as printed"))
    assert any("can't read" in p for p in found), (raw, found)


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


# Each numerator and denominator the README lists, written out here apart from
# the checker's tables.
NUMERATOR_WORDS = {
    "a": 1,
    "an": 1,
    "another": 1,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
}
DENOMINATOR_WORDS = {
    "half": 2,
    "halves": 2,
    "third": 3,
    "thirds": 3,
    "quarter": 4,
    "quarters": 4,
    "fourth": 4,
    "fourths": 4,
    "fifth": 5,
    "fifths": 5,
    "sixth": 6,
    "sixths": 6,
    "seventh": 7,
    "sevenths": 7,
    "eighth": 8,
    "eighths": 8,
    "ninth": 9,
    "ninths": 9,
    "tenth": 10,
    "tenths": 10,
}


def test_every_worded_fraction_reads_as_its_share():
    """Every numerator over every denominator, with a space or a hyphen, passes
    at its share and fails at twice that."""
    for top, n in NUMERATOR_WORDS.items():
        for bottom, m in DENOMINATOR_WORDS.items():
            for joint in " -":
                raw = f"{top}{joint}{bottom}"
                assert problems(_share(raw, n / m, "as printed")) == [], raw
                found = problems(_share(raw, 2 * n / m, "as printed"))
                assert any("at a stated scale" in p for p in found), (raw, found)


@pytest.mark.parametrize(
    ("raw", "near", "far"),
    [
        ("a third", 0.3331, 0.331),
        ("two-thirds", 0.667, 0.663),
        ("1 in 3", 0.3331, 0.331),
        ("a third", 0.3334, 0.3337),
        ("half a million", 500_400, 503_000),
        ("half a million", 500_400, 500_600),
        ("a third of a million", 333_100, 331_000),
        ("two and a half", 2.502, 2.51),
    ],
)
def test_a_rounded_number_passes_within_a_tenth_of_a_percent(raw, near, far):
    """A stored value may differ from a share, a fraction of a multiplier or a
    whole number with a fraction by 0.1%, and no further."""
    assert problems(_share(raw, near, "as printed")) == [], (raw, near)
    found = problems(_share(raw, far, "as printed"))
    assert any("at a stated scale" in p for p in found), (raw, far, found)


@pytest.mark.parametrize("minus", ["", "-"])
@pytest.mark.parametrize(
    ("raw", "value"),
    [
        ("half", 0.5),
        ("a third", 1 / 3),
        ("1 in 3", 1 / 3),
        ("half a million", 5e5),
        ("a third of a million", 1e6 / 3),
        ("half a per cent", 0.005),
        ("half a per cent", 0.5),
        ("two and a half", 2.5),
        ("two and a half million", 2.5e6),
        ("two and a half per cent", 0.025),
        ("two and a half per cent", 2.5),
    ],
)
def test_a_rounded_number_stops_at_a_tenth_of_a_percent(raw, value, minus):
    """Each kind of number that may round, with either sign, passes 0.09% from
    its value and fails 0.105% from it, on either side."""
    sign = -1 if minus else 1
    for off in (0.0009, -0.0009):
        stored = sign * value * (1 + off)
        assert problems(_share(minus + raw, stored, "as printed")) == [], (raw, off)
    for off in (0.00105, -0.00105):
        stored = sign * value * (1 + off)
        found = problems(_share(minus + raw, stored, "as printed"))
        assert any("at a stated scale" in p for p in found), (raw, off, found)


@pytest.mark.parametrize(
    "raw",
    [
        "a third-party",
        "the third year",
        "per quarter",
        "third",
        "quarter",
        "2 and half",
    ],
)
def test_an_ordinal_or_a_compound_is_a_problem(raw):
    """ "third" in "a third-party" or "the third year", and "quarter" without
    a numerator, print no fraction the checker can read."""
    assert _cant_read(raw)


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


def test_a_percent_row_scales_only_a_share():
    """A percent row stores a share in percent units. "Two and a half" prints a
    number, so it stays 2.5 there."""
    row = mutated(
        value_raw="two and a half",
        quote="two and a half",
        value=2.5,
        normalization="as printed",
        unit_concept="percent",
    )
    assert problems(row) == []
    row["value"] = 250
    assert any("at a stated scale" in p for p in problems(row))


@pytest.mark.parametrize(
    "raw",
    [
        "half per cent",
        "one half percent",
        "half a per cent",
        "half of one per cent",
        "a half percentage point",
    ],
)
def test_a_fraction_of_a_percentage_keeps_its_value_on_a_percent_row(raw):
    """A fraction of a percentage prints its own unit, so "half per cent" stays
    0.5 on a `unit_concept: percent` row, where "half" alone would read as 50."""
    row = mutated(
        value_raw=raw,
        quote=raw,
        value=0.5,
        normalization="as printed",
        unit_concept="percent",
    )
    assert problems(row) == []
    row["value"] = 50
    assert any("at a stated scale" in p for p in problems(row))


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


@pytest.mark.parametrize(
    "raw", ["a thousand and one", "twenty eleven", "one thousand two hundred"]
)
def test_a_number_in_words_the_checker_cant_read_is_a_problem(raw):
    """Delta review R1: words alone that make no one number the checker
    reads ("twenty eleven"), or one it doesn't ("one thousand two hundred"),
    give a problem, rather than count their parts."""
    for value in (1, 20, 1000, 1001, 1200):
        found = problems(_share(raw, value, "printed in words"))
        assert any("can't read" in p for p in found), (raw, found)


@pytest.mark.parametrize("raw", ["two-child limit", "one-off"])
def test_a_number_word_inside_a_compound_is_a_problem(raw):
    """A number word inside a hyphenated word ("two-child") prints no number."""
    assert _cant_read(raw)


def _label(raw, value):
    return mutated(
        value_raw=raw,
        quote=raw,
        value=value,
        normalization="rating as printed",
        value_kind="categorical",
    )


@pytest.mark.parametrize("raw", ["High", "four", "two-child limit", "one-off"])
def test_a_categorical_row_prints_a_label_and_compares_nothing(raw):
    """A categorical row's words name its label, whatever its value."""
    assert problems(_label(raw, 7)) == []


@pytest.mark.parametrize("raw", ["Tier 2", "3", "1 in 4", "٣"])
def test_a_categorical_row_that_prints_a_digit_is_a_problem(raw):
    """A number on a categorical row would compare nothing, so the checker
    takes no digits there."""
    found = problems(_label(raw, 7))
    assert any("prints a number" in p for p in found), (raw, found)


@pytest.mark.parametrize(
    ("raw", "passes", "fails"),
    [
        # a minus on a number in words
        ("-four", (-4,), (4,)),
        ("−four", (-4,), (4,)),
        ("+four", (4,), (-4,)),
        ("-three-fifths", (-0.6,), (0.6,)),
        ("-half", (-0.5,), (0.5,)),
        ("-1 in 4", (-0.25,), (0.25,)),
        # a whole number and a fraction
        ("two and a half", (2.5,), (0.5, 2, 250)),
        ("2 and a third", (7 / 3, 2.3333), (1 / 3, 2)),
        ("-two and a half", (-2.5,), (2.5,)),
        ("one and a half million", (1.5e6,), (0.5, 1.5, 5e5)),
        ("2 and a half bn", (2.5e9,), (2.5, 2.5e6)),
        ("two and a half m", (2.5e6,), (2.5, 2.5e9)),
        ("two and a half per cent", (0.025, 2.5), (0.5, 2)),
        ("twenty-one and a half", (21.5,), (0.5, 1)),
        # a fraction of a multiplier
        ("half a million", (5e5,), (0.5, 1e6)),
        ("half a hundred", (50,), (0.5, 100)),
        ("a quarter of a million", (2.5e5,), (0.25, 1e6)),
        ("three quarters of a billion", (7.5e8,), (0.75, 1e9)),
        ("half a percentage point", (0.005, 0.5), (1, 2)),
        ("a third of a million", (333_333,), (1 / 3, 1e6)),
        ("half of one million", (5e5,), (0.5, 1e6)),
        ("half million", (5e5,), (0.5, 1e6)),
        ("a half million", (5e5,), (0.5, 1e6)),
        # a fraction of a percentage, with or without "a" or "of"
        ("half per cent", (0.005, 0.5), (0.05, 5, 50)),
        ("half percent", (0.005, 0.5), (0.05, 5, 50)),
        ("half%", (0.005, 0.5), (0.05, 5, 50)),
        ("one half percent", (0.005, 0.5), (0.05, 5, 50)),
        ("a half percentage point", (0.005, 0.5), (0.05, 5, 50)),
        ("half a per cent", (0.005, 0.5), (0.05, 5, 50)),
        ("half a percent", (0.005, 0.5), (0.05, 5, 50)),
        ("half of a per cent", (0.005, 0.5), (0.05, 5, 50)),
        ("half of one per cent", (0.005, 0.5), (0.05, 5, 50)),
        ("a quarter of a percentage point", (0.0025, 0.25), (1, 0.025)),
        ("three-quarters per cent", (0.0075, 0.75), (75, 0.075)),
        ("-half per cent", (-0.005, -0.5), (0.005, 0.5)),
        # a whole number up to the hundreds and a fraction
        ("one hundred and a half", (100.5,), (0.5, 100, 1.5, 150)),
        ("a hundred and five and a half", (105.5,), (0.5, 105, 5.5)),
        ("nine hundred and ninety-nine and a half", (999.5,), (0.5, 990)),
        ("two hundred and a half million", (200.5e6,), (200.5, 0.5, 2e8)),
        ("one hundred and a half per cent", (1.005, 100.5), (0.5, 100)),
        ("-one hundred and a half", (-100.5,), (100.5,)),
        # a range: the first number takes the second's word
        ("£4-5 million", (4e6, 5e6), (4, 5, 4e3)),
        ("4-5%", (0.04, 0.05, 4, 5), (40,)),
        ("4–5bn", (4e9, 5e9), (4, 5)),
        ("4 to 5bn", (4e9, 5e9), (4, 5)),
        ("4m to 5bn", (4e6, 5e9), (4e9, 5e6)),
        ("4 - 5%", (0.04, 0.05), (45,)),
        ("4—5%", (0.04, 0.05), (45,)),
        ("four to five", (4, 5), (45, 0.8)),
        ("four to five million", (4e6, 5e6), (4, 5)),
        ("a third to a half", (1 / 3, 0.5), (0.1,)),
        ("a third to half a million", (333_333, 5e5), (1 / 3, 0.5)),
        ("-4 to -5", (-4, -5), (4, 5)),
        ("-5 to -4", (-5, -4), (5, 4)),
        ("200m to 1.5bn", (2e8, 1.5e9), (200, 1.5)),
        # a second number in brackets restates the first
        ("one third (33%)", (1 / 3, 0.33, 33), (0.5, 3)),
        ("1 in 4 (25%)", (0.25, 25), (1, 4)),
        ("25% (1 in 4)", (0.25, 25), (1, 4)),
        ("half (50%)", (0.5, 50), (2,)),
        ("-1 in 4 (-25%)", (-0.25, -25), (0.25, 25)),
        ("1 in 8 (13%)", (0.125, 0.13, 13), (1, 8)),
        ("1 in 8 (12%)", (0.125, 0.12, 12), (1, 8)),
        # words that print a zero
        ("nil", (0,), (1,)),
        ("nothing", (0,), (1,)),
        ("none", (0,), (1,)),
        ("no change", (0,), (1,)),
        ("no impact", (0,), (1,)),
        ("no overall impact", (0,), (1,)),
        ("zero", (0,), (1,)),
        ("zero in five", (0,), (5, 0.2)),
        # words around a number
        ("about £2bn a year", (2e9,), (2,)),
        ("4 per cent of GDP", (0.04, 4), (40,)),
        ("less than a 0.1 percentage point", (0.001, 0.1), (1,)),
        ("over a million", (1e6,), (1,)),
        # each spelling of a percentage and of a short multiplier
        ("4 %", (0.04, 4), (40,)),
        ("4 percent", (0.04, 4), (40,)),
        ("4 ppts", (0.04, 4), (40,)),
        ("+4ppt", (0.04, 4), (40,)),
        ("4pp", (0.04, 4), (40,)),
        ("2 m", (2e6,), (2,)),
        ("2mn", (2e6,), (2,)),
        ("2k", (2e3,), (2,)),
        ("2tn", (2e12,), (2,)),
        ("£3 trillion", (3e12,), (3,)),
        ("2-million", (2e6,), (2,)),
        ("2 hundred", (200,), (2,)),
        # signs and currency in any order
        ("-£1.7bn", (-1.7e9,), (1.7e9,)),
        ("£-1.7bn", (-1.7e9,), (1.7e9,)),
        ("+$2m", (2e6,), (-2e6,)),
        ("£5", (5,), (6, 5e3, 5e6, 5e9, 0.05, 500)),
        ("4", (4,), (0.04, 400, 4e3, 4e6, 4e9)),
        ("$5", (5,), (6,)),
        ("€5", (5,), (6,)),
        ("-$5", (-5,), (5,)),
        ("-€2m", (-2e6,), (2e6,)),
        ("$-5", (-5,), (5,)),
        ("€-2m", (-2e6,), (2e6,)),
        ("−2", (-2,), (2,)),
        ("–2", (-2,), (2,)),
        ("1E-05", (1e-5,), (1,)),
        ("1,234.5", (1234.5,), (1.2345,)),
        # a range may fall only if neither number is positive
        ("0 to -3", (0, -3), (3,)),
    ],
)
def test_each_form_reads_at_its_values_and_no_others(raw, passes, fails):
    """Each listed string passes at the listed accepted values and rejects the
    listed invalid values."""
    for value in passes:
        assert problems(_share(raw, value, "as printed")) == [], (raw, value)
    for value in fails:
        found = problems(_share(raw, value, "as printed"))
        assert any("at a stated scale" in p or "opposite sign" in p for p in found), (
            raw,
            value,
            found,
        )


@pytest.mark.parametrize(
    ("raw", "whole"),
    [("two and a half", 2.5), ("2 and a half", 2.5), ("one hundred and a half", 100.5)],
)
def test_a_whole_number_with_a_fraction_takes_the_normalization_s_factor(raw, whole):
    """With no word of its own, a whole number with a fraction takes the factor,
    within 0.1%, and fails at 1."""
    note = "£ million x 1,000,000"
    scaled = whole * 1e6
    assert problems(_share(raw, scaled, note)) == []
    assert problems(_share(raw, scaled * 1.0009, note)) == []
    for value in (whole, scaled * 1.00105, whole * 1e9):
        found = problems(_share(raw, value, note))
        assert any("at a stated scale" in p for p in found), (raw, value, found)


@pytest.mark.parametrize("dash", ["-", "−", "–", "—", "‐", "‑", "‒", "―", " - "])
def test_a_dash_is_zero_only_where_the_normalization_says_it_prints_nil(dash):
    """A table may print a dash for nil or for "not available", so the checker
    reads one only if the normalization records nil, and then only as zero."""
    for note in (
        "dash for nil",
        "dashes for nil",
        "dash means nil",
        "dash = nil",
        "nil = dash",
        "nil as dash",
        "the table prints NIL as a dash",
        "prints a dash for nil",
        "print nil as a dash",
        "the dash means nil",
        "dashes mean nil",
        "dash  for  nil",
        "the producer prints a dash for nil",
        "source prints nil as a dash",
        "the workbook prints dashes for nil",
        "£ million x 1e6; dash for nil",
        "as printed, dash for nil",
        "as printed. dash for nil",
        "as printed (dash for nil)",
    ):
        assert problems(_share(dash, 0, note)) == [], (dash, note)
        for value in (1, -1, 0.5, 1e6):
            found = problems(_share(dash, value, note))
            assert any("at a stated scale" in p for p in found), (dash, value, found)
    for note in (
        "as printed",
        "dash for not available",
        "dash means not available, not nil",
        "dash means missing, not nil",
        "dash does not mean nil",
        "not available; nil is printed as 0",
        "no dash for nil",
        "not a dash for nil",
        "never prints nil as a dash",
        "nil-rate band",
        "nil",
        "vanilla",
    ):
        assert _cant_read(dash, note), (dash, note)


def test_every_number_up_to_999_reads_in_every_style():
    """Exhaustively: each number from 0 to 999, however `_say` prints it, passes
    alone and rejects itself plus one. Its ratios pass at their shares and reject a
    different share."""

    def rejects(raw, value):
        found = problems(_share(raw, value, "as printed"))
        return any("at a stated scale" in p for p in found)

    for n in range(1000):
        for raw in {_say(n, *style) for style in product([False, True], repeat=3)}:
            assert problems(_share(raw, n, "printed in words")) == [], raw
            found = problems(_share(raw, n + 1, "printed in words"))
            assert any("at a stated scale" in p for p in found), raw
            ratio = f"{raw} in a thousand"
            assert problems(_share(ratio, n / 1000, "as printed")) == [], raw
            assert rejects(ratio, 1.01 * (n or 1) / 1000), raw
            if n:
                ratio = f"one in {raw}"
                assert problems(_share(ratio, 1 / n, "as printed")) == [], raw
                assert rejects(ratio, 1.01 / n), raw


# Numbers in the forms the README lists, each with its value and with no sign,
# written out here apart from the checker's tables. Ranges, brackets and the words
# for zero have tests of their own.
READABLE = [
    ("5", 5),
    ("1,234", 1234),
    ("2.5", 2.5),
    (".5", 0.5),
    ("£5", 5),
    ("2m", 2e6),
    ("2.5bn", 2.5e9),
    ("£2 billion", 2e9),
    ("4%", 0.04),
    ("4 per cent", 0.04),
    ("0.1 percentage points", 0.001),
    ("four", 4),
    ("twenty-five", 25),
    ("a hundred and five", 105),
    ("one million", 1e6),
    ("a million", 1e6),
    ("half", 0.5),
    ("a third", 1 / 3),
    ("three-fifths", 0.6),
    ("half a million", 5e5),
    ("half per cent", 0.005),
    ("two and a half", 2.5),
    ("one hundred and a half", 100.5),
    ("1 in 4", 0.25),
    ("one-in-eight", 0.125),
    ("3 out of 10", 0.3),
    ("one in every five", 0.2),
]
SPOILED = st.sampled_from(READABLE).map(lambda pair: pair[0])
AFTER = [
    " years",
    " people",
    " or more",
    "th",
    "-year-olds",
    ", 2025",
    "; 2025",
    ".",
    "/yr",
    " per household",
    " banana",
    " in",
    " and",
    " (",
    ")",
    "%%",
]
BEFORE = ["the ", "year ", "£5 ", "and ", "Q", "x", "COVID-", "(", "), ", "per ", "9 "]


@settings(max_examples=500, deadline=None)
@given(
    number=SPOILED,
    before=st.sampled_from(["", *BEFORE]),
    after=st.sampled_from(["", *AFTER]),
    value=st.floats(-1e12, 1e12, allow_nan=False),
)
def test_a_readable_number_with_more_around_it_is_a_problem_at_any_value(
    number, before, after, value
):
    """Each of READABLE's numbers, with words or characters around it that the
    README doesn't list, gives a problem at any value, so the checker never reads
    part of a string."""
    if before or after:
        found = problems(_share(f"{before}{number}{after}", value, "as printed"))
        assert any("can't read" in p for p in found), (before, number, after, found)


@settings(max_examples=300, deadline=None)
@given(number=SPOILED, value=st.floats(-1e12, 1e12, allow_nan=False))
def test_a_word_inside_a_readable_number_is_a_problem_at_any_value(number, value):
    """A word at any space inside one of READABLE's numbers gives a problem."""
    for i, ch in enumerate(number):
        if ch == " ":
            spoiled = f"{number[:i]} banana{number[i:]}"
            found = problems(_share(spoiled, value, "as printed"))
            assert any("can't read" in p for p in found), (spoiled, found)


@settings(max_examples=300, deadline=None)
@given(
    pair=st.sampled_from(READABLE),
    qualifier=st.sampled_from(
        ["about", "almost", "Approx.", "approximately", "around", "at least"]
        + ["at most", "fewer than", "just over", "just under", "less than"]
        + ["more than", "nearly", "over", "roughly", "some", "under", "up to"]
    ),
    tail=st.sampled_from(["", " a year", " of GDP"]),
    case=st.sampled_from([str, str.upper, str.title]),
    gap=st.sampled_from([" ", "  ", "\u00a0", "\t"]),
    off=st.sampled_from([1.5, 2, 0.5, 7]),
)
def test_a_number_reads_the_same_with_any_qualifier_case_or_spacing(
    pair, qualifier, tail, case, gap, off
):
    """A qualifier before a number, "a year" or "of GDP" after it, its case and
    its spacing change nothing: it passes at its value and fails elsewhere."""
    number, value = pair
    raw = case(f"{qualifier} {number}{tail}").replace(" ", gap)
    assert problems(_share(raw, value, "as printed")) == [], raw
    found = problems(_share(raw, value * off, "as printed"))
    assert any("at a stated scale" in p for p in found), (raw, found)


@settings(max_examples=300, deadline=None)
@given(pair=st.sampled_from(READABLE), minus=st.sampled_from(["-", "−", "–"]))
def test_a_minus_flips_a_number_in_any_form(pair, minus):
    """A minus before a number gives its opposite: the negative passes, the
    positive doesn't, and the unsigned number mirrors both."""
    number, value = pair
    raw = minus + number
    assert problems(_share(raw, -value, "as printed")) == [], raw
    flipped = problems(_share(raw, value, "as printed"))
    assert any("opposite sign" in p for p in flipped), (raw, flipped)
    assert problems(_share(number, value, "as printed")) == [], number
    mirror = problems(_share(number, -value, "as printed"))
    assert any("opposite sign" in p for p in mirror), (number, mirror)


@settings(max_examples=300, deadline=None)
@given(
    n=st.integers(1, 9999),
    word=st.sampled_from(
        [
            (" thousand", 1e3),
            (" million", 1e6),
            (" billion", 1e9),
            (" trillion", 1e12),
            ("k", 1e3),
            ("m", 1e6),
            ("mn", 1e6),
            ("bn", 1e9),
            ("tn", 1e12),
        ]
    ),
    other=st.sampled_from([1, 1e3, 1e6, 1e9, 1e12, 0.01, 100]),
    normalization=st.sampled_from(["as printed", "£ x 1,000,000", "/ 100"]),
)
def test_a_number_s_own_multiplier_sets_its_scale_under_any_normalization(
    n, word, other, normalization
):
    """A multiplier scales its own number, and no normalization overrides it."""
    text, factor = word
    raw = f"{n}{text}"
    assert problems(_share(raw, n * factor, normalization)) == [], raw
    if other != factor:
        found = problems(_share(raw, n * other, normalization))
        assert any("at a stated scale" in p for p in found), (raw, other, found)


@pytest.mark.parametrize("normalization", ["as printed", "£ x 1,000,000", "/ 100"])
@pytest.mark.parametrize(
    ("raw", "value", "number"),
    [
        ("one million", 1e6, 1),
        ("two million", 2e6, 2),
        ("a thousand", 1e3, 1),
        ("three hundred thousand", 3e5, 300),
        ("five billion", 5e9, 5),
        ("half a million", 5e5, 0.5),
        ("one and a half million", 1.5e6, 1.5),
    ],
)
def test_a_worded_multiplier_sets_its_scale_under_any_normalization(
    raw, value, number, normalization
):
    """A multiplier in words scales its number as a short one does, so "one
    million" under "/ 100" passes at a million and fails at 0.01."""
    assert problems(_share(raw, value, normalization)) == [], raw
    for scale in (1, 0.01, 1e6):
        if number * scale != value:
            found = problems(_share(raw, number * scale, normalization))
            assert any("at a stated scale" in p for p in found), (raw, scale, found)


@settings(max_examples=200, deadline=None)
@given(n=st.integers(1, 9999))
def test_digits_alone_take_the_normalization_s_factor_failing_that_one(n):
    """Digits with no word of their own take the normalization's factor, failing
    that 1, and nothing else: "4" as printed never passes at 4,000,000,000."""
    raw = str(n)
    assert problems(_share(raw, n, "as printed")) == []
    for scale in (7, 1e3, 1e6, 1e9, 0.01, 100):
        found = problems(_share(raw, n * scale, "as printed"))
        assert any("at a stated scale" in p for p in found), (raw, scale, found)
    stated = "£ million x 1,000,000"
    assert problems(_share(raw, n * 1e6, stated)) == []
    for scale in (1, 1e3, 1e9, 0.01, 100):
        found = problems(_share(raw, n * scale, stated))
        assert any("at a stated scale" in p for p in found), (raw, scale, found)


@pytest.mark.parametrize(
    ("note", "passes", "fails"),
    [
        ("£ million x 1e6", (4e6,), (4, 40, 4e9)),
        ("£ million X 1E6", (4e6,), (4, 40, 4e9)),
        ("£ million x 10^6", (4e6,), (4, 40, 4e9)),
        ("£ million x 10**6", (4e6,), (4, 40, 4e9)),
        ("£ million x 10 ^ 6", (4e6,), (4, 40, 4e9)),
        ("£ million × 1,000,000", (4e6,), (4, 4e3)),
        ("£ million (x 1e6)", (4e6,), (4,)),
        ("£ million [x 1e6]", (4e6,), (4,)),
        ("(x 1e6), sign as printed", (4e6,), (4,)),
        ("£ million x 1,000,000, sign as printed", (4e6,), (4,)),
        ("£ million x 1e6: sign as printed", (4e6,), (4,)),
        ("£ million x 1e6.", (4e6,), (4,)),
        ("£ x 1,000,000 monthly", (4e6,), (4,)),
        ("thousands * 1000", (4e3,), (4, 4e6)),
        ("÷ 100", (0.04,), (4, 400)),
        ("percent / 100", (0.04,), (4, 400)),
        ("x .5", (2,), (4, 8)),
        ("x 1,000,000 / 100", (4e4,), (4, 4e6, 0.04)),
        ("x 1,000,000 ÷ 100 * 2", (8e4,), (4, 4e6, 4e4, 0.04)),
        # two statements, so two readings; a semicolon ends a run of operations
        ("x 1e6; percent / 100", (4e6, 0.04), (4, 4e4)),
        ("x 1e6; / 100", (4e6, 0.04), (4, 4e4)),
        # no factor here
        ("x-axis", (4,), (40,)),
        ("see box 5", (4,), (20,)),
        ("printed as a fall ('lower' / 'fall' / 'drop')", (4,), (40,)),
        ("4x", (4,), (40,)),
    ],
)
def test_a_bare_number_takes_each_whole_factor_the_normalization_states(
    note, passes, fails
):
    """Sol R2 and R7: the checker reads a factor's whole operand, and composes
    operations in a row, so "4" under "x 10^6" never passes at 40."""
    for value in passes:
        assert problems(_share("4", value, note)) == [], (note, value)
    for value in fails:
        found = problems(_share("4", value, note))
        assert any("at a stated scale" in p for p in found), (note, value, found)


@pytest.mark.parametrize(
    "note",
    [
        "x 1 million",
        "x 2 bn",
        "x 1 000 000",
        "x 10^",
        "x 5^2",
        "x 5**2",
        "x 1,00",
        "x 0",
        "/ 0",
        "x 1e999",
        "x 10^999",
        "x 1e6a",
        "x 100%",
        "x 1e6->GBP",
        "x 1,000,000 / 100 million",
        "x 1,000,000 / 10^",
    ],
)
def test_a_factor_the_checker_cant_read_whole_is_a_problem_at_any_value(note):
    """Sol R2: a numeric prefix doesn't count as the factor, and the checker never
    falls back to 1 past a factor it can't read."""
    for value in (4, 40, 4e6, 0.04, 0):
        found = problems(_share("4", value, note))
        assert any("a factor in normalization" in p for p in found), (note, value)


@pytest.mark.parametrize(
    ("raw", "value", "wrong"),
    [("four", 4, 40), ("twenty-five", 25, 250), ("a hundred and five", 105, 1050)],
)
def test_words_alone_take_the_normalization_s_factor_failing_that_one(
    raw, value, wrong
):
    """Number words with no multiplier take the normalization's factor, failing
    that 1, as digits do."""
    assert problems(_share(raw, value, "as printed")) == []
    for bad in (wrong, value * 1e3, value * 1e6, value * 0.01, value * 100):
        found = problems(_share(raw, bad, "as printed"))
        assert any("at a stated scale" in p for p in found), (raw, bad, found)
    assert problems(_share(raw, value * 1e6, "measures x 1,000,000")) == []
    found = problems(_share(raw, value, "measures x 1,000,000"))
    assert any("at a stated scale" in p for p in found), (raw, found)


@settings(max_examples=500, deadline=None)
@given(
    text=st.lists(
        st.sampled_from(
            ["1", "4", "2.5", "1,000", "1e3", "1e999", ".5", "£", "$", "-", "−", "–"]
            + ["—", "+", "%", "(", ")", "in", "every", "out", "of", "to", "and", "a"]
            + ["an", "half", "third", "quarters", "one", "four", "twenty", "hundred"]
            + ["thousand", "million", "bn", "m", "k", "per", "cent", "percentage"]
            + ["point", "about", "over", "year", "gdp", "nil", "no", "change", ","]
            + [" ", "  ", "\u00a0", "\u200b", "٣", "th", "s"]
        ),
        max_size=8,
    ).map("".join),
    value=st.floats(-1e12, 1e12, allow_nan=False),
)
def test_any_string_of_number_parts_gives_a_verdict_never_an_exception(text, value):
    """The checker reads any arrangement of these parts whole or reports it,
    and never raises."""
    found = problems(_share(text, value, "as printed"))
    assert isinstance(found, list) and all(isinstance(p, str) for p in found)


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


@pytest.mark.parametrize("sign", [1, -1])
@pytest.mark.parametrize("toward_zero", [False, True])
def test_a_printed_number_matches_to_four_units_in_the_last_place(sign, toward_zero):
    """Delta review R3: a value one to four units in the last place from
    £1.7bn, on either side and with either sign, passes, and one five units
    off fails."""
    raw = "-£1.7bn" if sign < 0 else "£1.7bn"
    exact = (-1.7 if sign < 0 else 1.7) * 1e9
    target = 0.0 if toward_zero else math.copysign(math.inf, exact)
    value = exact
    for units in range(1, 6):
        value = math.nextafter(value, target)
        row = mutated(value_raw=raw, quote=raw, value=value, normalization="£bn x 1e9")
        found = problems(row)
        if units <= 4:
            assert found == [], (units, value, found)
        else:
            assert any("at a stated scale" in p for p in found), (units, value, found)


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
    found = [p for p in problems(row) if "rule 4" in p]
    assert found
    # the problem says what the locator should start with (cloud review A6)
    assert all("paragraph, table, box or data label" in p for p in found)


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
        # delta review R2: the first reference takes one of a closed list of
        # forms, so a qualifier there, even "(not missing)", reads as a bar;
        # and a negation right before a bar-reading phrase cancels it
        ("Figure 1.A data label unavailable, decile 3", True),
        ("Figure 1.A data label (not missing), decile 3", True),
        ("paragraph 1.7 approximately; Figure 1.A", True),
        ("paragraph 1.7; not a bar reading from Figure 1.A", False),
        ("paragraph 1.7; isn't read off Figure 1.A", False),
        ("paragraph 1.7; never a chart reading, Figure 1.A", False),
        ("paragraph 1.7; a bar reading from Figure 1.A", True),
        ("paragraph 1.7; read off Figure 1.A", True),
        ("paragraph 1.7; not a bar reading but read off the chart, Figure 1.A", True),
        ("paragraphs 1.7 and 1.8; Figure 1.A", False),
        ("data labels on Figure 1.B", False),
        ("Box 1.A; Figure 1.A", False),
        ("  paragraph 1.7 ; Figure 1.A", False),
        # delta review D5: any spacing, hyphen or case in a bar-reading phrase
        ("paragraph 1.7; bar-reading from Figure 1.A", True),
        ("paragraph 1.7; BAR  READING from Figure 1.A", True),
        ("paragraph 1.7; read  off the chart from Figure 1.A", True),
        ("paragraph 1.7; chart–reading of Figure 1.A", True),
        ("paragraph 1.7; bars read by eye, Figure 1.A", True),
        ("paragraph 1.7; reading from the chart, Figure 1.A", True),
        ("paragraph 1.7; estimated from the figure", True),
        ("paragraph 1.7; estimated from Figure 1.A", True),
        ("paragraph 1.7; not a bar-reading from Figure 1.A", False),
        # a word between the negation and the phrase, or a comma, ends the
        # negation (delta review D5)
        ("paragraph 1.7; not only a bar reading", True),
        ("paragraph 1.7; no, a bar reading", True),
        # the figure with a hyphen or a dash in its name
        ("Figure 1-A, decile 3 bar", True),
        ("Figure 1–B, decile 3 bar", True),
        # cloud review A6: forms that name where HM Treasury prints the number
        ("Table 2.C and Figure 1.A", False),
        ("paragraph 1.7 and Figure 1.A", False),
        ("paragraphs 1.7–1.8; Figure 1.A", False),
        ("paragraphs 1.7-1.8; Figure 1.A", False),
        ("paragraphs 1.7 to 1.8; Figure 1.A", False),
        ("Figure 1.A: data label for decile 3", False),
        ("Figure 1.A data label decile 3", False),
        ("Figure 1.A, data label decile 3", True),
        # Sol N2: a double negation affirms, so one negation alone cancels
        ("paragraph 1.7; not without a bar reading from Figure 1.A", True),
        ("paragraph 1.7; never without reading off the chart", True),
        ("paragraph 1.7; isn't not a chart reading", True),
        ("paragraph 1.7; no never a graph", True),
        ("paragraph 1.7; without a bar reading from Figure 1.A", False),
        ("paragraph 1.7; never reading off the chart", False),
        ("paragraph 1.7; no, not a bar reading", False),
        # Sol N3 and cloud review M2: how we say we took a number off a picture,
        # and the same with a negation before the verb
        ("paragraph 1.7; read off of the chart in Figure 1.A", True),
        ("paragraph 1.7; not read off of the chart in Figure 1.A", False),
        ("paragraph 1.7; read directly off the chart", True),
        ("paragraph 1.7; not read directly off the chart", False),
        ("paragraph 1.7; read off this chart (Figure 1.A)", True),
        ("paragraph 1.7; never read off this chart (Figure 1.A)", False),
        ("paragraph 1.7; read from that bar", True),
        ("paragraph 1.7; not read from that bar", False),
        ("paragraph 1.7; we read it off the bar in Figure 1.A", True),
        ("paragraph 1.7; we did not read it off the bar", False),
        ("paragraph 1.7; we estimated it from the bar", True),
        ("paragraph 1.7; we haven't estimated it from the bar", False),
        ("paragraph 1.7; read off the decile 3 bar of Figure 1.A", True),
        ("paragraph 1.7; not read off the decile 3 bar of Figure 1.A", False),
        ("paragraph 1.7; reading of the decile 3 bar, Figure 1.A", True),
        ("paragraph 1.7; not a reading of the decile 3 bar, Figure 1.A", False),
        ("paragraph 1.7; taken from the chart in Figure 1.A", True),
        ("paragraph 1.7; not taken from the chart, Figure 1.A", False),
        ("paragraph 1.7; took it from the chart", True),
        ("paragraph 1.7; measured from the bar", True),
        ("paragraph 1.7; not measured from the bar", False),
        ("decile 3: we read it off the chart", True),
        ("paragraph 1.7; reads from the chart", True),
        ("paragraph 1.7; never reads from the chart", False),
        ("paragraph 1.7; reads off the chart", True),
        ("paragraph 1.7; readings from the graph", True),
        ("paragraph 1.7; read the number off the bar", True),
        ("paragraph 1.7; estimated from Figure 1.A", True),
        ("paragraph 1.7; isn't estimated from Figure 1.A", False),
        ("paragraph 1.7; read off of Figure 1.A", True),
        ("paragraph 1.7; isn't read off of Figure 1.A", False),
        ("paragraph 1.7; not a bar reading from the figure", False),
        ("paragraph 1.7; not a bar reading from the figures", False),
        ("paragraph 1.7; not a bar reading off the figure", False),
        ("paragraph 1.7; not a bar reading off of the figure", False),
        ("paragraph 1.7; reading of Figure 1.A", True),
        ("paragraph 1.7; not a reading of Figure 1.A", False),
        ("paragraph 1.7; no readings of the chart", False),
        ("paragraph 1.7; no readings from the graph", False),
        ("paragraph 1.7; not an estimate from the chart", False),
        ("paragraph 1.7; never took it from the chart", False),
        ("paragraph 1.7; not read the decile 3 off the bar", False),
        ("paragraph 1.7; not read off the top decile 3 bar", False),
        ("paragraph 1.7; off of Figure 1.A", True),
        # any other bar, chart or graph, and any number from a figure, whatever
        # the verb; a negation before a verb we don't list cancels nothing
        ("paragraph 1.7; decile 3 bar", True),
        ("Table 2.C; the chart shows it", True),
        ("paragraph 1.7; graph", True),
        ("paragraph 1.7; eyeballed from Figure 1.A", True),
        ("paragraph 1.7; interpolated from the chart", True),
        ("paragraph 1.7; not interpolated from the chart", True),
        ("paragraph 1.7; from Figure 1.A", True),
        ("paragraph 1.7; off Figure 1.A", True),
        ("paragraph 1.7; no bar", False),
        ("paragraph 1.7; without a chart", False),
        ("paragraph 1.7; not the graph", False),
        ("paragraph 1.7; no bars", False),
        # words that only look like one, and readings of something else
        ("paragraph 1.7; Barnett formula", False),
        ("paragraph 1.7; Charter for Budget Responsibility", False),
        ("Table 2.C; read with paragraph 1.7", False),
        ("paragraph 1.7; taken from Table 2.C", False),
        ("paragraph 1.7; read from the text", False),
        ("paragraph 1.7; discussion of Figure 1.A", False),
        # Sol N6: any dash in a printed place, as in the figure's name
        ("Figure 1-A data label", False),
        ("Figure 1–A data label", False),
        ("Figure 1—B data label", False),
        ("Figure 1‑A data label", False),
        ("Figure 1‐A data label", False),
        ("Figure 1‒A data label", False),
        ("Figure 1―A data label", False),
        ("Figures 1-A and 1-B data labels", False),
        ("Figure 1.A data-label", False),
        ("paragraphs 1.7—1.8; Figure 1.A", False),
        ("paragraphs 1.7−1.8; Figure 1.A", False),
        ("paragraphs 1.7 — 1.8; Figure 1.A", False),
        ("Figure 1-A data label unavailable", True),
        # cloud review A-L1: each arm of the negation and the printed forms
        ("paragraph 1.7; graph reading, Figure 1.A", True),
        ("paragraph 1.7; without a graph reading, Figure 1.A", False),
        ("paragraph 1.7; it has not been read off the chart, Figure 1.A", False),
        ("paragraph 1.7; isn’t read off the chart, Figure 1.A", False),
        ("para 1.7; Figure 1.A", False),
        ("para. 1.7; Figure 1.A", False),
        ("Boxes 1.1 and 1.2; Figure 1.A", False),
        ("Figure 1.B data label on quintile 2", False),
        # each dash, in a phrase and in a figure's name
        ("paragraph 1.7; not a bar–reading from Figure 1.A", False),
        ("Figure 1–B, decile 3", True),
        ("Figure 1‐A, decile 3", True),
        ("Figure 1‑A, decile 3", True),
        # plural figures, each kind of picture, and any spacing
        ("paragraph 1.7; not read off figures 1.A and 1.B", False),
        ("paragraph 1.7; from figures 1.A and 1.B", True),
        ("paragraph 1.7; graphs", True),
        ("paragraph 1.7; charts", True),
        ("paragraph 1.7; not  a  bar  reading from Figure 1.A", False),
        # the figure in any spelling, and the number read on, in or using it
        ("paragraph 1.7; read off Fig. 1.A", True),
        ("paragraph 1.7; estimated from Fig 1A", True),
        ("paragraph 1.7; read off Figs. 1.A and 1.B", True),
        ("paragraph 1.7; taken from Fig. 1.B, decile 3", True),
        ("paragraph 1.7; eyeballed off Fig. 1.A", True),
        ("paragraph 1.7; reading of Fig. 1.A", True),
        ("paragraph 1.7; bar reading from Fig. 1.A", True),
        ("paragraph 1.7; read on Figure 1.A", True),
        ("paragraph 1.7; read in Figure 1.A", True),
        ("paragraph 1.7; estimated using Figure 1.A", True),
        ("paragraph 1.7; measured on Figure 1.A", True),
        ("paragraph 1.7; not read off Fig. 1.A", False),
        ("paragraph 1.7; not read on Figure 1.A", False),
        ("paragraph 1.7; not estimated using Figure 1.A", False),
        ("paragraph 1.7; read in the text", False),
        ("paragraph 1.7; read on page 8", False),
        ("paragraph 1.7; figure in the text", False),
        ("paragraph 1.7; configured using the table", False),
        # a second negation anywhere earlier in the clause undoes the first, and
        # one in an earlier clause doesn't
        ("paragraph 1.7; not possible without reading off the chart", True),
        ("paragraph 1.7; cannot be had without reading off the chart", True),
        ("paragraph 1.7; can't be had without reading off the chart", True),
        ("paragraph 1.7; no, not a bar reading", False),
        ("paragraph 1.7; no rounding; not a bar reading", False),
        ("paragraph 1.7: no rounding: not a bar reading", False),
        ("paragraph 1.7 (no rounding) not a bar reading", False),
        ("paragraph 1.7; cannot read off the chart", False),
        # Sol R1: an abbreviated figure counts as a figure
        ("paragraph 1.7; taken from Fig. 1.A", True),
        ("paragraph 1.7; taken from Figs. 1.A and 1.B", True),
        ("paragraph 1.7; estimated using fig 1.A", True),
        ("paragraph 1.7; not taken from Fig. 1.A", False),
        ("Fig. 1.A data label", False),
        # Sol R8: the rarer ways to say we read a number off a picture
        ("paragraph 1.7; estimated from the plot", True),
        ("paragraph 1.7; estimated from the diagram", True),
        ("paragraph 1.7; taken from the visual", True),
        ("paragraph 1.7; visual estimate of Figure 1.A", True),
        ("paragraph 1.7; estimate of Figure 1.A", True),
        ("paragraph 1.7; Figure 1.A read by eye", True),
        ("paragraph 1.7; read by eye", True),
        ("paragraph 1.7; by eye", True),
        ("paragraph 1.7; estimated from the plots", True),
        ("paragraph 1.7; estimated from the diagrams", True),
        ("paragraph 1.7; taken from the visuals", True),
        ("paragraph 1.7; column 3 of Figure 1.A", True),
        ("paragraph 1.7; columns 3-4 of Figure 1.A", True),
        ("paragraph 1.7; the column on Fig. 1.A", True),
        ("paragraph 1.7; the third column in Fig. 1.A", True),
        ("paragraph 1.7; not estimated from the plot", False),
        ("paragraph 1.7; no diagram", False),
        ("paragraph 1.7; no visual estimate of Figure 1.A", False),
        ("paragraph 1.7; not read by eye", False),
        ("paragraph 1.7; Figure 1.A not read by eye", False),
        ("paragraph 1.7; no column of Figure 1.A", False),
        # a column of a table prints its number
        ("Table 2.1, column 3", False),
        ("paragraph 1.7; column 3 of Table 2.1", False),
        ("paragraph 1.7; subcolumn of Figure 1.A", False),
        ("paragraph 1.7; nearby eye", False),
        ("paragraph 1.7; by eyewitnesses", False),
        ("paragraph 1.7; Table 2.1 column 3", False),
        # Sol R7: a negation in capitals reads the same
        ("paragraph 1.7; NOT a bar reading", False),
        ("paragraph 1.7; NEVER read off the chart", False),
        ("paragraph 1.7; DIDN'T read it off the chart", False),
        ("paragraph 1.7; NOT WITHOUT a bar reading", True),
        ("paragraph 1.7; NOT possible WITHOUT reading off the chart", True),
        # the cloud review of 3c65fd7a: Figure 1(a) names Figure 1.A
        ("Figure 1(a), decile 3", True),
        ("Figure 1 (a), decile 3", True),
        ("Fig. 1(b)", True),
        ("paragraph 1.7; Figure 1(a)", False),
        # plurals count
        ("paragraph 1.7; the decile bars", True),
        # a word that holds a negation isn't one, and a bracket ends a clause
        ("paragraph 1.7; casino not a bar reading", False),
        ("paragraph 1.7; note not a bar reading", False),
        ("paragraph 1.7; no rounding (not a bar reading)", False),
        # each earlier negation counts
        ("paragraph 1.7; without doubt not a bar reading", True),
        ("paragraph 1.7; didn’t say not a bar reading", True),
        # any phrase that stands decides, and a verb starts at a word's start
        ("paragraph 1.7; a bar reading but not a chart reading", True),
        ("paragraph 1.7; spread from no chart", False),
    ],
)
def test_rule_4_reads_where_the_locator_places_the_number(locator, bar_reading):
    """README rule 4: a locator that places the number on Figure 1.A's or
    1.B's bars marks a bar reading; one whose first reference names the
    paragraph, table or data label printing it doesn't (delta review D1:
    red book row 357's 20% sits in paragraph 1.7; final review F4; delta
    review R2)."""
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
    """Final review F4 and delta review R2: a first reference with any word
    after its data label, a negation included, places the number on a bar."""
    assert reads_a_bar(f"Figure 1.A {negated}")
    assert not reads_a_bar("Figure 1.A data label")


# Leading references that say where HM Treasury prints a number, and ones
# that don't; and the parts of a locator that name Figure 1.A or 1.B.
PRINTING = [
    "paragraph 1.7",
    "paragraphs 1.7 and 1.8",
    "Table 2.C",
    "Table 2.C and Figure 1.A",
    "Box 1.A",
    "Figure 1.A data label",
    "Fig. 1B data labels",
    "data label",
    "data label for decile 3",
    "data labels for Figure 1.B",
]
NOT_PRINTING = [
    "Figure 1.B",
    "Figures 1.A and 1.B",
    "Figure 1.A, decile 3 bar",
    "p.8",
    "no data labels",
    "data label missing",
    "Figure 1.A data label isn't shown",
    "Figure 1.A data label unavailable",
    "Figure 1.A data label (not missing)",
    "paragraph 1.7 approximately",
]
NAMES_FIGURE = {
    "Figure 1.A data label",
    "Fig. 1B data labels",
    "data labels for Figure 1.B",
    "Figure 1.B",
    "Figures 1.A and 1.B",
    "Figure 1.A, decile 3 bar",
    "Figure 1.A data label isn't shown",
    "Figure 1.A data label unavailable",
    "Figure 1.A data label (not missing)",
    "Table 2.C and Figure 1.A",
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
                "not a bar reading",
                "never read off the chart",
                "isn't a chart reading",
            ]
        ),
        max_size=3,
    ),
    affirm=st.booleans(),
)
def test_rule_4_follows_the_leading_reference(lead, rest, affirm):
    """Final review F4 and delta review R2: where a locator names Figure 1.A
    or 1.B, in any spelling, only a first reference in one of the forms
    PRINTING lists places the number where HM Treasury prints it, and
    anything later in the locator places nothing. A bar-reading phrase
    anywhere marks a bar reading, unless a negation comes right before it."""
    locator = "; ".join([lead, *rest, *(["a bar reading"] if affirm else [])])
    names_figure = any(part in NAMES_FIGURE for part in [lead, *rest])
    assert reads_a_bar(locator) == (affirm or (names_figure and lead not in PRINTING))


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
            "condition 'proposed_measure_key' is not a string",
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
    assert problems(mutated(period=deep)) == ["period is not an integer"]
    locator = mutated(publication__locator=deep)
    assert problems(locator) == ["publication.locator is not a string"]
    assert problems(mutated(invented=deep)) == ["unknown fields ['invented']"]
    nested = mutated(conditions__geography_note=deep)
    assert problems(nested) == ["condition 'geography_note' is not a string"]
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


# The AB2025 row contract's types, from its README, written out here apart
# from the checker's own lists (delta review R4): each field with the types
# it allows.
STRING_FIELDS = [
    "source",
    "source_model",
    "value_raw",
    "normalization",
    "value_kind",
    "time_basis",
    "attribution",
    "benchmark_class",
    "quote",
    "parse_confidence",
    "status",
]
NULLABLE_FIELDS = [
    "reform_hint",
    "measure_key",
    "baseline_policy",
    "source_table",
    "source_column",
    "metric",
    "proposed_metric",
    "unit_concept",
    "proposed_unit",
    "proposed_baseline",
    "note",
    "local_artifact",
]
PUBLICATION_FIELDS = [
    "title",
    "url",
    "date",
    "publisher",
    "primary_sha256",
    "locator",
    "access",
]
TYPED = (
    [(f, (str,)) for f in STRING_FIELDS]
    + [(f, (str, type(None))) for f in NULLABLE_FIELDS]
    + [(f"publication__{f}", (str, type(None))) for f in PUBLICATION_FIELDS]
    + [(f"conditions__{k}", (str,)) for k in BASE["conditions"]]
    + [("period", (int,)), ("value", (int, float))]
    + [("conditions", (dict,)), ("publication", (dict,))]
)


def _named(path):
    """How a problem names a field: "quote", "publication.url" or "condition
    'fy'"."""
    if path.startswith("publication__"):
        return "publication." + path.split("__")[1]
    if path.startswith("conditions__"):
        return f"condition {path.split('__')[1]!r}"
    return path


@pytest.mark.parametrize("field", NULLABLE_FIELDS)
def test_a_nullable_field_takes_null_or_a_string(field):
    """Delta review R4: null or a string passes in each field the contract
    lets us leave empty."""
    assert type_problems(mutated(**{field: None})) == []
    assert type_problems(mutated(**{field: "x"})) == []


@pytest.mark.parametrize("field", STRING_FIELDS)
def test_a_string_field_takes_no_null(field):
    """Delta review R4: null fails in each field that needs a string."""
    assert type_problems(mutated(**{field: None})) == [f"{field} is not a string"]


@settings(max_examples=500, deadline=None)
@given(data=st.data(), typed=st.sampled_from(TYPED))
def test_a_field_of_a_type_the_contract_doesnt_allow_is_a_problem(data, typed):
    """Delta review R4, for every field the AB2025 row contract types: any
    JSON value of another type gives a problem that names the field."""
    path, allowed = typed
    value = data.draw(
        JSON.filter(lambda v: isinstance(v, bool) or not isinstance(v, allowed))
    )
    found = problems(_changed({path: value}))
    assert any(p.startswith(f"{_named(path)} is not") for p in found), (
        path,
        value,
        found,
    )


@settings(max_examples=400, deadline=None)
@given(
    changes=st.dictionaries(
        st.sampled_from(FIELDS), JSON | st.just(...), min_size=1, max_size=4
    )
)
def test_changing_or_deleting_fields_never_raises(changes):
    """Final review F3, for every input: changing or deleting fields does not
    make row validation, duplicate checking or proposed-key discovery raise
    an exception, for a row alone or next to copies of itself and BASE."""
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


@pytest.mark.parametrize("dash", "-−–—‐‑‒―")
def test_rule_4_reads_each_dash_as_a_space(dash):
    """The checker reads a phrase and its negation through any dash."""
    assert reads_a_bar(f"paragraph 1.7; read by{dash}eye")
    assert not reads_a_bar(f"paragraph 1.7; not{dash}a bar reading")
