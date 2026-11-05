"""The AB2026 harvest row contract (#230), as one checkable function.

sources/harvest-uk-ab2026-2026-10-29/README.md states the contract: the AB2025
row contract with the AB2026 exceptions. tests/test_uk_ab2026_harvest.py
holds every pinned family to it, and a family being staged can be checked on
its own before COUNTS.json pins it:

    python pipeline/ab2026_harvest_contract.py sources/harvest-uk-ab2026-2026-10-29/uk_rf_ab2026
"""

import gzip
import json
import math
import re
import sys
import zlib
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UK = ROOT / "data" / "uk"
FISCAL_EVENT = "autumn_budget_2026"

REQUIRED = {
    "source",
    "source_model",
    "value",
    "value_raw",
    "normalization",
    "value_kind",
    "period",
    "time_basis",
    "conditions",
    "reform_hint",
    "measure_key",
    "attribution",
    "benchmark_class",
    "baseline_policy",
    "publication",
    "source_table",
    "source_column",
    "quote",
    "parse_confidence",
    "status",
}
OPTIONAL = {
    "metric",
    "proposed_metric",
    "unit_concept",
    "proposed_unit",
    "proposed_baseline",
    "note",
    "local_artifact",
}
ATTRIBUTION = {"own", "restated", "same_assumptions"}
BENCHMARK_CLASS = {"different_model", "administrative_fact", "same_assumptions"}
VALUE_KIND = {
    "point",
    "central",
    "range_low",
    "range_high",
    "approx_chart_reading",
    "cumulative",
    "categorical",
}
TIME_BASIS = {"fiscal_year", "annual", "point_in_time"}
CONFIDENCE = {"high", "medium", "low"}
# What a malformed row could still raise when the checks reach it, after
# type_problems has turned away each field of the wrong type: an integer with
# too many digits to print, or nesting too deep to print or encode. The
# checker reports these as problems (review A H-6(h); delta review D1-3;
# final review F3). _number turns away an integer too large for a float
# before any arithmetic, so no check overflows.
MALFORMED = (
    TypeError,
    AttributeError,
    KeyError,
    ValueError,
    RecursionError,
)
# README rule 6: HM Treasury and OBR material is under the Open Government
# Licence and quoted whole; every other producer's quote stays under 15 words.
OGL = {"hm_treasury", "obr_efo"}
# A slug of lower-case words joined by single underscores (review A H-6(f)).
PROPOSED_KEY = re.compile(r"ab2026(_option)?__[a-z0-9]+(_[a-z0-9]+)*")
BARE_PACKAGE = re.compile(r"ab2026__package")
SHA256 = re.compile(r"[0-9a-f]{64}")
# Rule 9: a component names its part on a part row; OBR workbook totals mark
# themselves `measure_total` (review A H-1).
COMPONENT_ROW_TYPES = {"measure_component", "measure_total"}
# conditions.geography is a closed code (review A H-6(d)); prose goes in
# conditions.geography_note.
GEOGRAPHY = {
    "UK",
    "GB",
    "England",
    "Wales",
    "Scotland",
    "Northern Ireland",
    "England and Wales",
    "UK_excl_scotland",
    "Scotland, Wales and Northern Ireland",
    "not stated",
    # countries a producer compares the UK with
    "France",
    "Germany",
    "Ireland",
    "Italy",
    "Netherlands",
    "Singapore",
    "Spain",
    "US",
}
# A `normalization` that documents a sign taken from the wording, not from a
# printed minus (review A H-2(3)).
WORDED_SIGN = re.compile(r"sign from the wording|carried negative|-> -\d|→ negative")
SCALES = (1, 1e3, 1e6, 1e9, 0.01, 100)
WORD_SCALE = (
    (re.compile(r"\b(bn|billion)\b|\dbn\b", re.I), 1e9),
    (re.compile(r"\b(m|million|mn)\b|\dm\b", re.I), 1e6),
    (re.compile(r"\b(k|thousand)\b|\dk\b", re.I), 1e3),
    (re.compile(r"%|per ?cent|percentage point|ppts?\b|pp\b", re.I), 0.01),
)
NUMBER = re.compile(r"(?<![\w.])[-−–]?(?:\d[\d,]*(?:\.\d+)?|\.\d+)(?:[eE][-+]?\d+)?")
# Number words: one to nineteen, and the tens
ONES = {
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
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
}
TENS = {
    "twenty": 20,
    "thirty": 30,
    "forty": 40,
    "fifty": 50,
    "sixty": 60,
    "seventy": 70,
    "eighty": 80,
    "ninety": 90,
}
# A multiplier after a number: a word ("2 million", "a thousand") or, after
# digits, a short form ("2m", "4bn")
LONG = {"hundred": 100, "thousand": 1e3, "million": 1e6, "billion": 1e9}
SHORT = {"bn": 1e9, "mn": 1e6, "m": 1e6, "k": 1e3}
MULTIPLIERS = LONG | SHORT
STEM = re.compile(r"(?:hundred|thousand|million|billion)(?:th|ths|s)")
# A string as tokens: digits, words, whitespace and single characters
TOKEN = re.compile(
    r"(?P<num>\d+(?:,\d+)*(?:\.\d+)?)|(?P<word>[^\W\d_]+)|(?P<space>\s+)|(?P<char>.)",
    re.S,
)
CURRENCY = "£$€"
DASHES = "-−–"
YEAR = re.compile(r"(?:19|20)\d\d")
GENERIC_RATIO = re.compile(r"\bN\s+in\s+M\b", re.I)
ARROW = re.compile(r"\s*(?:->|→)")


def _either(words):
    """A regex alternation of words, the longest first."""
    return "|".join(re.escape(w) for w in sorted(words, key=len, reverse=True))


_SEP = r"(?:\s+|\s*-\s*)"
# README rule 4. A locator that names Figure 1.A or 1.B ("Figure 1.A", "Fig.
# 1A", "Figures 1.A and 1.B") says where HM Treasury prints the number only
# if its first reference, up to its first comma or semicolon, takes one of
# the forms PRINTED reads and nothing more: a paragraph, table or box by its
# number, or a data label. The checker reads any other first reference as a
# bar reading, "Figure 1.A data label unavailable" included (delta review
# R2). A locator that says we read the number off a bar, chart or graph marks
# a bar reading wherever it says so, unless a negation comes just before
# ("not a bar reading", "isn't read off the chart").
FIGURE_1 = re.compile(r"\bfig(?:ure)?s?\.?\s*1\.?\s*[ab]\b", re.I)
_FIG = r"fig(?:ure)?s?\.?\s*1\.?\s*[ab](?:\s+and\s+1\.?\s*[ab])?"
_ID = r"\d+(?:\.[0-9a-z]+)*"
PRINTED = re.compile(
    rf"(?:paragraph|para|table|box)(?:s|es)?\.?\s+{_ID}(?:\s+(?:and|to)\s+{_ID})?"
    rf"|(?:{_FIG}\s+)?data\s+labels?"
    rf"(?:\s+(?:for|on)\s+(?:(?:decile|quintile)\s+\d+|{_FIG}))?",
    re.I,
)
BAR_READING = re.compile(
    r"\b(?:bar|chart|graph) readings?\b"
    r"|\bread (?:off|from) (?:the |a )?(?:bars?|charts?|graphs?|figures?)\b",
    re.I,
)
DENIED = re.compile(
    r"(?:\b(?:no|not|never|without)|n['’]t)\s+(?:(?:a|an|the|been)\s+)?\Z", re.I
)
# A worded fraction: "half", or a numerator and a denominator ("a third",
# "three-fifths", "another quarter").
NUMERATORS = {"a": 1, "an": 1, "another": 1} | {
    w: v for w, v in ONES.items() if v <= 10
}
DENOMINATORS = {
    "half": 2,
    "halves": 2,
    "third": 3,
    "thirds": 3,
    "quarter": 4,
    "quarters": 4,
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
FRACTION = re.compile(
    rf"\b(?:({_either(NUMERATORS)}){_SEP})?({_either(DENOMINATORS)})(?!\w|-\w)", re.I
)

# A run is the longest stretch of number tokens joined by single spaces or
# dashes: digits with one multiplier or none ("2 million", "2.5bn"), or
# number words ("twenty-five", "a hundred and five", "two hundred
# thousand"). The checker reads a run whole or not at all, so it never takes
# part of a number for the number (delta review R1: "twenty-one in a
# hundred" is 0.21, and "4-5" is no one number).
#
# A ratio is a run N, "in", "in every" or "out of", and a run M, joined all
# by spaces or all by hyphens ("1 in 4", "1-in-4", "one in every ten", "3
# out of 10", "1 in 2 million"). Its share is N/M, negative when a minus
# comes right before N, or after the spaces before M ("-1 in 4", "1 in -4"),
# and N and M count for nothing on their own (delta review D1-1). The
# checker reads no ratio after a currency sign ("£5 in 10 years") or in a
# name ("COVID-19 in 10"). It reads a year after a bare "in" ("5 in 2027",
# "5 in 2026-27") as a year, unless the normalization gives the ratio ("1 in
# 2000 -> 0.0005", or "N in M -> N/M" in any case). It reports any other
# ratio it can't read: a run it can't parse ("a thousand and one in a
# million", "1 in 2 thousand million"), a multiplier's ordinal or plural
# after M ("1 in 2 millionths"), an M joined to a word ("1 in 4-year-olds"),
# or separators it can't place ("1 in - 4", "1 in-4").


def _tokens(text):
    """A string's tokens, as (kind, text, start)."""
    return [(m.lastgroup, m.group(), m.start()) for m in TOKEN.finditer(text)]


def _kind(tokens, i):
    """The kind of token i, or None past either end."""
    return tokens[i][0] if 0 <= i < len(tokens) else None


def _word(tokens, i):
    """The lower-case word at token i, or None."""
    return tokens[i][1].lower() if _kind(tokens, i) == "word" else None


def _is(tokens, i, chars):
    """Whether token i is one of these characters."""
    return _kind(tokens, i) == "char" and tokens[i][1] in chars


def _number_at(tokens, i):
    """Whether token i is digits or a number word below a hundred."""
    w = _word(tokens, i)
    return _kind(tokens, i) == "num" or w in ONES or w in TENS


def _starts_run(tokens, i):
    """Whether a number starts at token i: digits, a number word, or "a" or
    "an" before a multiplier word ("a thousand", "a-million")."""
    if _number_at(tokens, i):
        return True
    return (
        _word(tokens, i) in ("a", "an")
        and (_kind(tokens, i + 1) == "space" or _is(tokens, i + 1, "-"))
        and _word(tokens, i + 2) in LONG
    )


def _continues(tokens, j, k):
    """Whether token k carries on the run whose last token is j."""
    w = _word(tokens, k)
    if _number_at(tokens, k) or w in LONG:
        return True
    if w in SHORT:
        return _kind(tokens, j) == "num"
    # "and" after a multiplier word, before more of the number ("a hundred
    # and five", and so "a thousand and 21", which the checker can't read)
    return (
        w == "and"
        and _word(tokens, j) in LONG
        and _kind(tokens, k + 1) == "space"
        and _number_at(tokens, k + 2)
    )


def _run_end(tokens, i):
    """The last token of the run that starts at token i."""
    j = i
    while True:
        if _kind(tokens, j) == "num" and _word(tokens, j + 1) in MULTIPLIERS:
            j += 1  # a multiplier written on to the digits ("2bn")
        elif (
            (_kind(tokens, j + 1) == "space" or _is(tokens, j + 1, DASHES))
            and j + 2 < len(tokens)
            and _continues(tokens, j, j + 2)
        ):
            j += 2
        else:
            return j


def _small(parts, k):
    """The number from one to ninety-nine that the words from k on start
    with ("eleven", "twenty", "twenty-five"), as (number, next word), or
    None."""
    w = parts[k] if k < len(parts) else None
    if w in TENS:
        unit = parts[k + 1] if k + 1 < len(parts) else None
        if unit in ONES and ONES[unit] < 10:
            return TENS[w] + ONES[unit], k + 2
        return TENS[w], k + 1
    if w in ONES:
        return ONES[w], k + 1
    return None


def _run_value(tokens, i, j):
    """The number the run from token i to token j prints, as (number,
    multiplier), or None if it doesn't read as one number: digits with one
    multiplier or none ("2.5bn", "2 million"), or words up to nine hundred
    and ninety-nine with one multiplier or none ("twenty-five", "a hundred
    and five", "two hundred thousand", "a million")."""
    parts = [t[1].lower() for t in tokens[i : j + 1] if t[0] in ("num", "word")]
    if tokens[i][0] == "num":
        n = float(parts[0].replace(",", ""))
        if not math.isfinite(n):
            return None
        if len(parts) == 1:
            return n, 1
        if len(parts) == 2 and parts[1] in MULTIPLIERS:
            return n, MULTIPLIERS[parts[1]]
        return None
    if parts[0] in ("a", "an"):
        n, k = 1, 1
    else:
        head = _small(parts, 0)
        if head is None:
            return None
        n, k = head
    if k < len(parts) and parts[k] == "hundred":
        n, k = n * 100, k + 1
        if k < len(parts) and parts[k] == "and":
            k += 1
            if _small(parts, k) is None:
                return None
        rest = _small(parts, k)
        if rest:
            n, k = n + rest[0], rest[1]
    if k + 1 == len(parts) and parts[k] in ("thousand", "million", "billion"):
        return n, LONG[parts[k]]
    if parts[0] in ("a", "an") and n == 1:
        return None  # "a" needs a multiplier
    return (n, 1) if k == len(parts) else None


def _glued_left(tokens, i):
    """Whether the token before i ties a run that starts at i into a name or
    a number: "Q1", "COVID-19", ".5"."""
    if _kind(tokens, i - 1) in ("num", "word") or _is(tokens, i - 1, "."):
        return True
    return _is(tokens, i - 1, DASHES) and _kind(tokens, i - 2) == "word"


def _joined_right(tokens, j):
    """The last token of a word or number joined to the run that ends at j
    ("4th", "4-year", "two-child", "4–5"), or None."""
    if _kind(tokens, j + 1) in ("num", "word"):
        return j + 1
    if _is(tokens, j + 1, DASHES) and _kind(tokens, j + 2) in ("num", "word"):
        return j + 2
    return None


def _spoiler(tokens, j):
    """The last token of what stops the checker reading a ratio's M, which
    ends at token j: a word or number joined to it ("1 in 4-year-olds"), or
    a multiplier's ordinal or plural after it ("1 in 2 millionths"); or
    None."""
    joined = _joined_right(tokens, j)
    if joined is not None:
        return joined
    if _kind(tokens, j + 1) == "space" and STEM.fullmatch(_word(tokens, j + 2) or ""):
        return j + 2
    return None


def _seps(tokens, p):
    """The spaces and dashes from token p on, as (text, next token)."""
    text = ""
    while _kind(tokens, p) == "space" or _is(tokens, p, DASHES):
        text += tokens[p][1]
        p += 1
    return text, p


def _sep_kind(sep):
    """A ratio separator's kind: "space" for whitespace, "hyphen" for one
    hyphen, or None for anything else ("", " - ", "–")."""
    if sep == "-":
        return "hyphen"
    return "space" if sep.isspace() else None


def _joint(tokens, p):
    """The ratio joint at token p, as (its words, the separators inside it,
    the next token), or None."""
    w = _word(tokens, p)
    if w == "in":
        sep, q = _seps(tokens, p + 1)
        if _word(tokens, q) == "every":
            return "in every", [sep], q + 1
        return "in", [], p + 1
    if w == "out":
        sep, q = _seps(tokens, p + 1)
        if _word(tokens, q) == "of":
            return "out of", [sep], q + 1
    return None


def _sign(tokens, i):
    """Whether a minus comes right before token i, after a space, a bracket
    or the start of the string, rather than after a word or a number (a name
    or a range)."""
    return _is(tokens, i - 1, DASHES) and _kind(tokens, i - 2) not in ("num", "word")


def _money(tokens, i):
    """Whether a currency sign comes before token i, perhaps across a minus
    or a space ("£5", "-£5", "£ 5")."""
    k = i - 1
    if _is(tokens, k, DASHES):
        k -= 1
    if _kind(tokens, k) == "space":
        k -= 1
    return _is(tokens, k, CURRENCY)


def _year(tokens, k, m):
    """Whether the run from token k to token m prints a year: "2027",
    "2026-27" or "2026-2027"."""
    if not (tokens[k][0] == "num" and YEAR.fullmatch(tokens[k][1])):
        return False
    return m == k or (
        m == k + 2
        and _is(tokens, k + 1, DASHES)
        and re.fullmatch(r"\d\d|(?:19|20)\d\d", tokens[m][1]) is not None
    )


def _gives_ratio(normalization, n, m):
    """Whether a normalization gives "n in m" as a ratio: the generic "N in M"
    or the printed ratio, followed by an arrow to the share."""
    printed = (
        rf"(?<![\w.]){re.escape(n)}(?:\s+|\s*-\s*)in(?:\s+|\s*-\s*){re.escape(m)}"
        r"(?!\w|\.\d)"
    )
    return bool(
        GENERIC_RATIO.search(normalization)
        or re.search(printed + ARROW.pattern, normalization, re.I)
    )


def _ratios(text, normalization=""):
    """The ratios a string prints, as ((start, end), share), and the text of
    each ratio it prints that the checker can't read."""
    tokens = _tokens(text)
    found, unread = [], []
    i = 0
    while i < len(tokens):
        if not _starts_run(tokens, i):
            i += 1
            continue
        j = _run_end(tokens, i)
        sep1, p = _seps(tokens, j + 1)
        joint = _joint(tokens, p)
        sep2, k = _seps(tokens, joint[2]) if joint else ("", p)
        if not (joint and k < len(tokens) and _starts_run(tokens, k)):
            i = j + 1
            continue
        words, inner = joint[0], joint[1]
        m = _run_end(tokens, k)
        n_text = text[tokens[i][2] : tokens[j][2] + len(tokens[j][1])]
        m_text = text[tokens[k][2] : tokens[m][2] + len(tokens[m][1])]
        if _money(tokens, i) or _glued_left(tokens, i):
            i = j + 1
            continue  # "£5 in 10 years", "COVID-19 in 10"
        m_sign = re.fullmatch(r"\s+[-−–]", sep2) is not None
        if (
            words == "in"
            and not m_sign
            and _year(tokens, k, m)
            and not _gives_ratio(normalization, n_text, m_text)
        ):
            i = j + 1
            continue  # "5 in 2027"
        n_sign = _sign(tokens, i)
        start = tokens[i - 1][2] if n_sign else tokens[i][2]
        end = tokens[m][2] + len(tokens[m][1])
        # one kind of separator throughout, so a hyphen is never a sign
        kinds = {_sep_kind(s) for s in (sep1, *inner, sep2[:-1] if m_sign else sep2)}
        a, b = _run_value(tokens, i, j), _run_value(tokens, k, m)
        spoiler = _spoiler(tokens, m)
        share = None
        if (
            len(kinds) == 1
            and None not in kinds
            and spoiler is None
            and a is not None
            and b is not None
            and b[0] * b[1]
        ):
            share = a[0] * a[1] / (b[0] * b[1])
        if share is not None and math.isfinite(share):
            found.append(((start, end), -share if n_sign != m_sign else share))
        else:
            last = tokens[m if spoiler is None else spoiler]
            unread.append(text[start : last[2] + len(last[1])])
        i = m + 1
    return found, unread


def _cut(text, spans):
    """The string with each span cut out."""
    for start, end in sorted(spans, reverse=True):
        text = f"{text[:start]} {text[end:]}"
    return text


def _words_alone(text):
    """The numbers a string prints in words, outside names and hyphenated
    words ("two-child"), each without its multiplier word, which value_raw's
    scale supplies; and the text of each one the checker can't read."""
    tokens = _tokens(text)
    out, unread = [], []
    i = 0
    while i < len(tokens):
        if tokens[i][0] == "num" or not _starts_run(tokens, i):
            i += 1
            continue
        j = _run_end(tokens, i)
        if not (_glued_left(tokens, i) or _joined_right(tokens, j) is not None):
            v = _run_value(tokens, i, j)
            if v is None:
                unread.append(text[tokens[i][2] : tokens[j][2] + len(tokens[j][1])])
            else:
                out.append(float(v[0]))
        i = j + 1
    return out, unread


def _read(text, normalization="", words=False):
    """What a string prints, as (exact, fractions, spans, unread). Exact
    numbers are its digits, signed, outside its ratios. Fractions are its
    ratios' shares ("1 in 4" -> 0.25) and its worded fractions ("a third"),
    which a stored share may round (delta review D1-1). Spans are its ratios'
    places, and unread lists each ratio or number in words that the checker
    can't read. With words, a string that prints none of these gives its
    number words ("four", "over a million")."""
    ratios, unread = _ratios(text, normalization)
    fractions = [share for _, share in ratios]
    spans = [span for span, _ in ratios]
    text = _cut(text, spans)
    for m in FRACTION.finditer(text):
        top, bottom = (g.lower() if g else g for g in m.groups())
        if top or bottom == "half":
            fractions.append(NUMERATORS[top or "a"] / DENOMINATORS[bottom])
    text = re.sub(r"([-−–])\s*[£$€]", r"\1", text)  # "-£1.7bn"
    exact = []
    for m in NUMBER.findall(text):
        t = m.replace(",", "").replace("−", "-").replace("–", "-")
        try:
            exact.append(float(t))
        except ValueError:
            pass
    if words and not (exact or fractions):
        exact, more = _words_alone(text)
        unread += more
    return exact, fractions, spans, unread


def _factors(normalization):
    """The multipliers a normalization states ("x 1,000,000", "/ 100", ...)."""
    out = []
    for op, num in re.findall(
        r"(?:^|\s)(x|×|\*|/|÷)\s*(\d[\d,]*(?:\.\d+)?(?:e[+-]?\d+)?)",
        normalization or "",
        re.I,
    ):
        try:
            f = float(num.replace(",", ""))
        except ValueError:
            continue
        if f and math.isfinite(f):
            out.append(1 / f if op in "/÷" else f)
    return out


def _scales(raw, normalization):
    """README rule contract, review A H-2(2): the scale comes from value_raw's
    word (bn, m, k, %), failing that from the normalization's stated factor,
    failing that from a fixed set."""
    for rx, scale in WORD_SCALE:
        if rx.search(raw):
            # a percentage is stored as a share or in percent units
            return {scale, 1.0} if scale == 0.01 else {scale}
    factors = _factors(normalization)
    if factors:
        return set(factors)
    return set(SCALES)


def _number(v):
    """A finite number. A bool isn't one, and neither is an integer too large
    for a float (final review F3)."""
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        return False
    try:
        return math.isfinite(v)
    except OverflowError:
        return False


def _text(v):
    """A string with more than whitespace in it."""
    return isinstance(v, str) and bool(v.strip())


# Floating-point error: a printed number at its scale and the stored value
# differ by at most four units in the last place (final review F2). Each
# staged value that matches a printed number, rather than a ratio or worded
# fraction, differs from it by at most one.
ULPS = 4


def _same(a, b):
    """A printed number at its scale, equal up to floating-point error."""
    if not (math.isfinite(a) and math.isfinite(b)):
        return False
    return abs(a - b) <= ULPS * math.ulp(max(abs(a), abs(b)))


def _rounded(a, b):
    """A stored share of a printed fraction, rounded ("a third" -> 0.3333)."""
    return math.isfinite(b) and math.isclose(a, b, rel_tol=1e-3)


def value_problems(r):
    """review A H-2: `value` is finite and is value_raw's number at its scale,
    with value_raw's sign unless the normalization documents a worded sign.
    Delta review D1-1: a printed number matches exactly, and only the share
    of a printed ratio or worded fraction, the fraction itself, may round. A
    `unit_concept: percent` row stores that share in percent units, 100 times
    the fraction. A non-categorical row that prints its number only in words
    gives those words. Delta review R1: a ratio, or a number in words, that
    the checker can't read is a problem."""
    v = r["value"]
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        return ["value is not a number"]
    if not _number(v):
        return ["value is not finite"]
    raw = r["value_raw"] if isinstance(r["value_raw"], str) else ""
    norm = r.get("normalization") or ""
    exact, fractions, spans, unread = _read(
        raw, norm, words=r["value_kind"] != "categorical"
    )
    if unread:
        return [f"value_raw {raw!r} prints {unread[0]!r}, which the checker can't read"]
    if not (exact or fractions):
        return []  # nothing printed to compare (a categorical label)
    # a ratio's multiplier ("1 in 2 million") scales the ratio, not the string
    rest = _cut(raw, spans)
    printed = [n * s for n in exact for s in _scales(rest, norm)]
    per = 100 if r.get("unit_concept") == "percent" else 1
    shares = [per * f for f in fractions]
    if not (
        any(_same(abs(v), abs(p)) for p in printed)
        or any(_rounded(abs(v), abs(f)) for f in shares)
    ):
        return [f"value {v!r} is not value_raw {raw!r} at a stated scale"]
    if (
        WORDED_SIGN.search(norm)
        or any(_same(v, p) for p in printed)
        or any(_rounded(v, f) for f in shares)
    ):
        return []
    return [f"value {v!r} has the opposite sign to value_raw {raw!r}"]


def _keys(path):
    return {m["measure_key"] for m in json.loads(path.read_text())["measures"]}


def registry_keys():
    """The AB2026 keys, and each earlier event's keys for Table 6.4
    recostings (README rule 2). AB2025 has two key spaces: the #136 port
    registry and the events inventory."""
    earlier = {
        p.name.removesuffix("_measures.json"): _keys(p)
        for p in (UK / "events").glob("*_measures.json")
    }
    earlier["autumn_budget_2025"] |= _keys(UK / "ab2025_measures.json")
    return _keys(UK / "ab2026_measures.json"), earlier


def enums():
    from scorecard_db.models import Metric, UnitConcept

    return {m.value for m in Metric}, {u.value for u in UnitConcept}


def read_rows(family_dir):
    with gzip.open(Path(family_dir) / "claims_staged.jsonl.gz", "rt") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def read_manifest(family_dir):
    text = (Path(family_dir) / "manifest.jsonl").read_text()
    return [json.loads(line) for line in text.splitlines() if line.strip()]


# A line of a JSON-lines file that isn't JSON keeps its place as UNREADABLE.
UNREADABLE = object()


def _json_lines(path, label):
    """A JSON-lines file's values, one per non-blank line, and a problem for
    each line that isn't JSON or for a file that can't be read, never an
    exception (final review F3). read_rows and read_manifest raise instead,
    for the generators and tests that read checked families."""
    try:
        if path.suffix == ".gz":
            with gzip.open(path, "rt", encoding="utf-8") as fh:
                text = fh.read()
        else:
            text = path.read_text(encoding="utf-8")
    except (OSError, EOFError, ValueError, zlib.error) as e:
        return [], [f"{path.name} cannot be read ({type(e).__name__})"]
    values, out = [], []
    for line in text.split("\n"):  # as read_rows splits a file's lines
        if not line.strip():
            continue
        try:
            values.append(json.loads(line))
        except (ValueError, RecursionError):
            out.append(f"{label} {len(values)}: is not JSON")
            values.append(UNREADABLE)
    return values, out


def proposed_keys(rows):
    """The proposed measure keys a family's rows name (README rule 2). A
    malformed row names none; row_problems reports it (delta review D1-3)."""
    return {
        r["conditions"]["proposed_measure_key"]
        for r in rows
        if isinstance(r, dict)
        and isinstance(r.get("conditions"), dict)
        and isinstance(r["conditions"].get("proposed_measure_key"), str)
        and r["conditions"]["proposed_measure_key"]
    }


# The AB2025 row contract's types (delta review R4): a string in each TEXT
# field, a string or null in each TEXT_OR_NULL field and PUBLICATION field,
# an integer in `period`, and an object of strings in `conditions`.
# value_problems checks `value`.
TEXT = {
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
}
TEXT_OR_NULL = {
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
}
PUBLICATION = (
    "title",
    "url",
    "date",
    "publisher",
    "primary_sha256",
    "locator",
    "access",
)


def type_problems(r):
    """Delta review R4: each field of r whose type the AB2025 row contract
    doesn't allow, as strings."""
    out = [
        f"{f} is not a string"
        for f in sorted(TEXT & set(r))
        if not isinstance(r[f], str)
    ]
    out += [
        f"{f} is not a string or null"
        for f in sorted(TEXT_OR_NULL & set(r))
        if not (r[f] is None or isinstance(r[f], str))
    ]
    period = r.get("period")
    if "period" in r and (isinstance(period, bool) or not isinstance(period, int)):
        out.append("period is not an integer")
    for f in ("conditions", "publication"):
        if f in r and not isinstance(r[f], dict):
            out.append(f"{f} is not an object")
    if isinstance(r.get("conditions"), dict):
        for k, v in r["conditions"].items():
            if not (isinstance(k, str) and isinstance(v, str)):
                out.append(f"condition {k!r} is not a string")
    if isinstance(r.get("publication"), dict):
        pub = r["publication"]
        out += [
            f"publication.{f} is not a string"
            for f in PUBLICATION
            if not (pub.get(f) is None or isinstance(pub[f], str))
        ]
    return out


def row_problems(r, keys, earlier, metrics, units):
    """Every way one staged row breaks the contract, as strings. A malformed
    row is reported, never raised (review A H-6(h))."""
    if not isinstance(r, dict):
        return ["row is not an object"]
    try:
        return _row_problems(r, keys, earlier, metrics, units)
    except MALFORMED as e:
        return [f"row is malformed ({type(e).__name__}: {e})"]


def _row_problems(r, keys, earlier, metrics, units):
    out = []
    fields = set(r)
    if not REQUIRED <= fields:
        return [f"missing fields {sorted(REQUIRED - fields)}"]
    if not fields <= REQUIRED | OPTIONAL:
        out.append(f"unknown fields {sorted(fields - REQUIRED - OPTIONAL)}")
    wrong = type_problems(r)
    if wrong:
        return out + wrong
    for field, allowed in (
        ("attribution", ATTRIBUTION),
        ("benchmark_class", BENCHMARK_CLASS),
        ("value_kind", VALUE_KIND),
        ("time_basis", TIME_BASIS),
        ("parse_confidence", CONFIDENCE),
    ):
        if r[field] not in allowed:
            out.append(f"{field} {r[field]!r} not in {sorted(allowed)}")
    if r["status"] != "ok":
        out.append("status is not ok")
    for field in ("value_raw", "quote"):
        if not r[field].strip():
            out.append(f"{field} is empty")
    out += value_problems(r)
    if bool(r.get("metric")) == bool(r.get("proposed_metric")):
        out.append("exactly one of metric and proposed_metric")
    if r.get("proposed_metric") in metrics:
        out.append(
            f"proposed_metric {r['proposed_metric']!r} is a registered Metric; use metric"
        )
    if bool(r.get("unit_concept")) == bool(r.get("proposed_unit")):
        out.append("exactly one of unit_concept and proposed_unit")
    if r.get("metric") and r["metric"] not in metrics:
        out.append(f"metric {r['metric']!r} is not a Metric; use proposed_metric")
    if r.get("unit_concept") and r["unit_concept"] not in units:
        out.append(f"unit_concept {r['unit_concept']!r} is not a UnitConcept")

    c = r["conditions"]
    if not c:
        return out + ["conditions is not a non-empty object"]
    if c.get("fiscal_event") != FISCAL_EVENT:
        out.append(f"conditions.fiscal_event is not {FISCAL_EVENT}")
    if "fy" in c:
        m = re.fullmatch(r"(\d{4})-(\d{2})", str(c["fy"]))
        if not m or (int(m.group(1)) + 1) % 100 != int(m.group(2)):
            out.append(f"conditions.fy {c['fy']!r} is not one fiscal year YYYY-YY")
        else:
            if r["period"] != int(m.group(1)) + 1:
                out.append(f"period {r['period']} is not the end year of {c['fy']}")
            if r["time_basis"] != "fiscal_year":
                out.append("an fy row has time_basis fiscal_year")
    elif r["time_basis"] == "fiscal_year" and not c.get("horizon"):
        out.append("a fiscal_year row has conditions.fy or conditions.horizon")
    if "geography" in c and c["geography"] not in GEOGRAPHY:
        out.append(
            f"conditions.geography {c['geography']!r} is not a code; put prose in geography_note"
        )
    if not (isinstance(r["period"], int) and 1945 <= r["period"] <= 2075):
        out.append(f"period {r['period']!r} is not a year")

    k = r["measure_key"]
    if "recosting_of" in c:
        if c.get("row_type") != "recosting":
            out.append("a recosting_of row has row_type recosting (review A H-6(b))")
        if k not in earlier.get(c["recosting_of"], ()):
            out.append(f"{k} is not a {c['recosting_of']} key")
    elif k is not None:
        if k not in keys:
            out.append(f"measure_key {k} is not in data/uk/ab2026_measures.json")
        if "proposed_measure_key" in c:
            out.append("a row with a measure_key carries no proposed_measure_key")
    elif c.get("proposed_measure_key"):
        pk = c["proposed_measure_key"]
        if not PROPOSED_KEY.fullmatch(pk) or BARE_PACKAGE.fullmatch(pk):
            out.append(f"proposed_measure_key {pk!r} is not ab2026[_option]__slug")
        if pk in keys:
            out.append(f"{pk} is registered; put it in measure_key")
    if c.get("row_type") == "measure_component" and not (
        c.get("component", "").strip() and (k or c.get("proposed_measure_key"))
    ):
        out.append("a measure_component row names its component and measure (rule 9)")
    if "component" in c and (
        not c["component"].strip() or c.get("row_type") not in COMPONENT_ROW_TYPES
    ):
        out.append("a component row has row_type measure_component (rule 9)")
    if r["attribution"] == "restated" and not (r.get("note") or "").strip():
        out.append("a restated row's note names whose figure it restates")

    pub = r["publication"]
    for field in ("title", "url", "date", "publisher", "primary_sha256"):
        if not pub.get(field):
            out.append(f"publication.{field} is empty")
    if pub.get("primary_sha256") and not SHA256.fullmatch(pub["primary_sha256"]):
        out.append("publication.primary_sha256 is not a sha256")
    if pub.get("date") and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", pub["date"]):
        out.append("publication.date is not YYYY-MM-DD")

    if r["value_raw"] not in r["quote"]:
        out.append("quote does not contain value_raw")
    if r["source"] not in OGL and len(r["quote"].split()) >= 15:
        out.append("quote has 15 or more words (README rule 6)")
    if r["attribution"] == "same_assumptions" and (
        r["benchmark_class"] != "same_assumptions"
        or r["source_model"] != "policyengine_uk"
    ):
        out.append("same_assumptions rows are PolicyEngine-computed")
    if (
        r["source"] == "hm_treasury"
        and "impact on households" in (pub.get("title") or "").lower()
        and (
            r["value_kind"] == "approx_chart_reading"
            or reads_a_bar(pub.get("locator") or "")
        )
    ):
        out.append("no HMT Impact on households bar readings (README rule 4)")
    return out


def reads_a_bar(locator):
    """README rule 4: whether a locator places the number on a bar of Figure
    1.A or 1.B, rather than naming where HM Treasury prints it."""
    if any(
        not DENIED.search(locator[: m.start()]) for m in BAR_READING.finditer(locator)
    ):
        return True
    if not FIGURE_1.search(locator):
        return False
    lead = " ".join(re.split(r"[,;]", locator, maxsplit=1)[0].split())
    return not PRINTED.fullmatch(lead)


def family_problems(family_dir):
    """Every contract breach in one family directory, as strings."""
    family_dir = Path(family_dir)
    missing = [
        n
        for n in ("NOTES.md", "manifest.jsonl", "claims_staged.jsonl.gz")
        if not (family_dir / n).exists()
    ]
    if missing:
        return [f"{family_dir.name}: missing {missing}"]
    manifest, out = _json_lines(family_dir / "manifest.jsonl", "manifest line")
    rows, unread = _json_lines(family_dir / "claims_staged.jsonl.gz", "row")
    out += unread
    try:
        notes = (family_dir / "NOTES.md").read_text(encoding="utf-8")
    except (OSError, ValueError) as e:
        notes = ""
        out.append(f"NOTES.md cannot be read ({type(e).__name__})")
    entries = [m for m in manifest if isinstance(m, dict)]
    if len(entries) < len([m for m in manifest if m is not UNREADABLE]):
        out.append("manifest has a line that is not an object")
    shas = [m["sha256"] for m in entries if isinstance(m.get("sha256"), str)]
    for j, m in enumerate(manifest):
        if not isinstance(m, dict):
            continue  # reported above, or by _json_lines
        # a problem names the line by its url, or by its place when the url
        # isn't text
        name = m["url"] if _text(m.get("url")) else f"line {j}"
        if not (isinstance(m.get("sha256"), str) and SHA256.fullmatch(m["sha256"])):
            out.append(f"manifest {name}: sha256 is not a sha256")
        if not all(_text(m.get(f)) for f in ("url", "title", "retrieved")):
            out.append(f"manifest {name}: needs url, title and retrieved as text")
    if len(set(shas)) != len(shas):
        out.append("manifest lists a primary twice")
    keys, earlier = registry_keys()
    metrics, units = enums()
    for i, r in enumerate(rows):
        if r is UNREADABLE:
            continue  # reported by _json_lines
        for p in row_problems(r, keys, earlier, metrics, units):
            out.append(f"row {i}: {p}")
        pub = r.get("publication") if isinstance(r, dict) else None
        sha = pub.get("primary_sha256") if isinstance(pub, dict) else None
        if not (isinstance(sha, str) and sha in shas):
            out.append(f"row {i}: primary_sha256 is not in manifest.jsonl")
    out += duplicate_problems(rows)
    for pk in sorted(proposed_keys(rows)):
        if not re.search(rf"(?<![a-z0-9_]){re.escape(pk)}(?![a-z0-9_])", notes):
            out.append(f"NOTES.md does not give the scope of {pk}")
    return out


def claim_identity(r):
    """The AB2025 ingest's claim identity (ExternalScore.claim_id's inputs):
    two rows that share it become one claim."""
    c = r["conditions"]
    return json.dumps(
        [
            r["source"],
            r["measure_key"] or c.get("proposed_measure_key"),
            r["reform_hint"],
            r["baseline_policy"],
            r.get("metric") or r.get("proposed_metric"),
            r.get("unit_concept") or r.get("proposed_unit"),
            r["period"],
            r["time_basis"],
            c,
            r["value_raw"],
            r["value_kind"],
            r["benchmark_class"],
        ],
        sort_keys=True,
        ensure_ascii=False,
    )


def duplicate_problems(rows):
    """review A H-3: the AB2025 ingest merges two printings of one claim and
    raises on three, so no more than two non-restated, non-categorical rows
    share a claim identity, and a pair agrees within 0.5%."""
    groups = defaultdict(list)
    for i, r in enumerate(rows):
        try:
            if r["attribution"] == "restated" or r["value_kind"] == "categorical":
                continue
            groups[claim_identity(r)].append(i)
        except MALFORMED:
            continue  # reported by row_problems
    out = []
    for idx in groups.values():
        if len(idx) > 2:
            out.append(f"rows {idx} share one claim identity (more than 2)")
        elif len(idx) == 2:
            a, b = (rows[i].get("value") for i in idx)
            if not (_number(a) and _number(b)):
                continue  # row_problems reports the value (D1-3, final review F3)
            if not math.isclose(a, b, rel_tol=0.005, abs_tol=1e-9):
                out.append(
                    f"rows {idx} share one claim identity but differ by over 0.5%"
                )
    return out


def main(argv):
    bad = 0
    for d in argv:
        problems = family_problems(d)
        gz = Path(d) / "claims_staged.jsonl.gz"
        rows = len(_json_lines(gz, "row")[0]) if gz.exists() else 0
        print(f"{d}: {rows} rows, {len(problems)} problems")
        for p in problems[:200]:
            print("  " + p)
        bad += bool(problems)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
