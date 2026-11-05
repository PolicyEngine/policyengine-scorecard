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
# A percentage is stored as a share or in percent units.
PERCENT = (0.01, 1.0)

# README, "Row contract additions": the checker reads value_raw only when the
# whole string, in lower case with its spaces collapsed, matches a form below.
# It reports anything else, and we narrow value_raw to the number, which the
# quote still contains. So no part of a number, and no number among other words,
# passes as the row's value.
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
COUNTS = ONES | TENS | {"a": 1, "an": 1, "zero": 0}
# A multiplier after a number: a word, or after digits a short form
LARGE = {"thousand": 1e3, "million": 1e6, "billion": 1e9, "trillion": 1e12}
SHORT = {"bn": 1e9, "mn": 1e6, "m": 1e6, "k": 1e3, "tn": 1e12}
MULTIPLIERS = LARGE | SHORT | {"hundred": 100}
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
QUALIFIERS = {
    "about",
    "almost",
    "approx.",
    "approximately",
    "around",
    "at least",
    "at most",
    "fewer than",
    "just over",
    "just under",
    "less than",
    "more than",
    "nearly",
    "over",
    "roughly",
    "some",
    "under",
    "up to",
}
# Words after the number that leave it as it is
TAILS = {"a year", "of gdp"}
# Words that print a zero
ZERO = {"nil", "no change", "no impact", "no overall impact", "none", "nothing"}


def _either(words):
    """A regex alternation of words, the longest first."""
    return "|".join(re.escape(w) for w in sorted(words, key=len, reverse=True))


_SIGN = "[-+−–]"
_DIGITS = (
    r"(?:(?:[0-9]{1,3}(?:,[0-9]{3})+|[0-9]+)(?:\.[0-9]+)?|\.[0-9]+)(?:e[-+]?[0-9]+)?"
)
_LARGE = _either(LARGE)
_UNITS = _either(w for w, n in ONES.items() if n < 10)
_TEENS = _either(w for w, n in ONES.items() if n >= 10)
_BELOW_100 = rf"(?:(?:{_either(TENS)})(?:[ -](?:{_UNITS}))?|{_TEENS}|{_UNITS})"
_BELOW_1000 = (
    rf"(?:(?:{_UNITS}|an?)[ -]hundred(?:(?:[ -]and)?[ -]{_BELOW_100})?|{_BELOW_100})"
)
# Number words with one multiplier or none: "twenty-five", "a hundred and
# five", "two hundred thousand", "a million"
_WORDS = rf"(?:zero|{_BELOW_1000}(?:[ -](?:{_LARGE}))?|an?[ -](?:{_LARGE}))"
# After digits, one multiplier: "2.5bn", "2 m", "2 million", "2-million"
_TIMES = rf"(?: ?(?:{_either(SHORT)})|[ -]?(?:hundred|{_LARGE}))"
_PERCENT = r"(?: ?%| per ?cent| percentage points?| ?ppts?| ?pp)"
# Digits with an optional sign and currency sign: "-£1.7bn", "£-1.7bn", "+434m"
_FIGURE = (
    rf"(?P<lead>(?:{_SIGN}[£$€]?|[£$€]{_SIGN}?)?)(?P<digits>{_DIGITS})"
    rf"(?:(?P<times>{_TIMES})|(?P<percent>{_PERCENT}))?"
)
FIGURE = re.compile(_FIGURE)
WORDED = re.compile(
    rf"(?P<sign>{_SIGN})?(?P<words>{_WORDS})(?P<percent>{_PERCENT})?",
)
_PART = rf"(?:{_either(NUMERATORS)})[ -](?:{_either(DENOMINATORS)})"
# A worded fraction, perhaps of a multiplier: "half", "three-fifths", "half a
# million", "a quarter of a percentage point"
FRACTION = re.compile(
    rf"(?P<sign>{_SIGN})?(?P<fraction>half|{_PART})"
    rf"(?:(?: of)? an? (?:(?P<times>hundred|{_LARGE})"
    rf"|(?P<percent>per ?cent|percentage point)))?"
)
# A whole number and a fraction: "two and a half million", "2 and a third"
MIXED = re.compile(
    rf"(?P<sign>{_SIGN})?(?P<whole>{_DIGITS}|{_BELOW_100}) and (?P<fraction>{_PART})"
    rf"(?:[ -](?P<times>{_LARGE})|(?P<percent>{_PERCENT}))?"
)
_COUNT = rf"(?:{_DIGITS}{_TIMES}?|{_WORDS})"
# Two numbers joined all by spaces or all by hyphens. A sign comes before N or,
# with spaces, before M.
RATIO = re.compile(
    rf"(?P<sign_n>{_SIGN})?(?P<n>{_COUNT})"
    r"(?: (?:in(?: every)?|out of(?: every)?) "
    rf"(?P<sign_m>{_SIGN})?|-(?:in(?:-every)?|out-of(?:-every)?)-)"
    rf"(?P<m>{_COUNT})"
)
_FIGURE_END = _FIGURE.replace("?P<lead>", "?:").replace("?P<digits>", "?:")
_FIGURE_END = _FIGURE_END.replace("?P<times>", "?:").replace("?P<percent>", "?:")
DASHED = re.compile(rf"(?P<a>{_FIGURE_END})(?:[-–—]| [-–—] )(?P<b>{_FIGURE_END})")
WHOLE = re.compile(
    rf"(?:(?:{_either(QUALIFIERS)}) )?(?:an? (?=[-+−–£$€.0-9]))?"
    rf"(?P<body>.*?)(?: (?:{_either(TAILS)}))?"
)


def _signed(lead, number):
    """The number, negative if its lead holds a minus."""
    return -number if lead and set(lead) & set("-−–") else number


def _own(times, percent):
    """The scales a number's own word gives it, or None."""
    if percent:
        return PERCENT
    return (MULTIPLIERS[times.strip(" -")],) if times else None


def _in_words(words):
    """The number and the multiplier that WORDED's words print."""
    number, large = 0, 1
    for w in re.split("[ -]", words):
        if w in LARGE:
            large = LARGE[w]
        elif w == "hundred":
            number *= 100
        elif w != "and":
            number += COUNTS[w]
    return number, large


def _part(text):
    """The share that a worded fraction prints."""
    if text == "half":
        return 1 / 2
    top, bottom = re.split("[ -]", text)
    return NUMERATORS[top] / DENOMINATORS[bottom]


def _one_number(text):
    """One number, as (number, its own scales or None, its kind), or None. Its
    kind says how value_problems compares it: "digits" and "words" exactly,
    "rounded" and "share" within 0.1%, and "share" in percent units on a percent
    row."""
    m = FIGURE.fullmatch(text)
    if m:
        number = float(m["digits"].replace(",", ""))
        if not math.isfinite(number):
            return None
        own = _own(m["times"], m["percent"])
        return _signed(m["lead"], number), own, "digits"
    m = WORDED.fullmatch(text)
    if m:
        number, large = _in_words(m["words"])
        if m["percent"] and large != 1:
            return None
        own = _own(None, m["percent"]) or ((large,) if large != 1 else None)
        return _signed(m["sign"], float(number)), own, "words"
    m = FRACTION.fullmatch(text)
    if m:
        number = _signed(m["sign"], _part(m["fraction"]))
        own = _own(m["times"], m["percent"])
        return number, own, "rounded" if own else "share"
    m = MIXED.fullmatch(text)
    if m:
        whole = m["whole"]
        digits = whole[0] in "0123456789."
        count = float(whole.replace(",", "")) if digits else _in_words(whole)[0]
        if not math.isfinite(count):
            return None
        number = _signed(m["sign"], count + _part(m["fraction"]))
        return number, _own(m["times"], m["percent"]), "rounded"
    return None


def _count(text):
    """A ratio's N or M at its multiplier, or None if it isn't finite."""
    one = _one_number(text)
    if one is None:
        return None
    number, own, _ = one
    count = number * (own[0] if own else 1)
    return count if math.isfinite(count) else None


def _printed(text):
    """What one number, ratio or range prints, as a list of _one_number's tuples,
    or None."""
    one = _one_number(text)
    if one:
        return [one]
    m = RATIO.fullmatch(text)
    if m:
        top, bottom = _count(m["n"]), _count(m["m"])
        if top is None or not bottom:
            return None
        share = _signed(m["sign_n"], _signed(m["sign_m"], top / bottom))
        return [(share, None, "share")]
    m = DASHED.fullmatch(text) or re.fullmatch(r"(?P<a>.+) to (?P<b>.+)", text)
    if m:
        low, high = _one_number(m["a"]), _one_number(m["b"])
        if not (low and high) or (low[1] and not high[1]):
            return None
        # The first number takes the second's word: "£4-5 million"
        if high[1] and not low[1]:
            kind = "rounded" if low[2] == "share" else low[2]
            low = (low[0], high[1], kind)
        # A range joins like with like, and runs upward in value or in size, so
        # neither "4% to 2 million" nor "2025-26" is one
        if (low[1] == PERCENT) != (high[1] == PERCENT):
            return None
        a, b = (number * (own[0] if own else 1) for number, own, _ in (low, high))
        if a > b and abs(a) > abs(b):
            return None
        return [low, high]
    return None


def _restates(first, second):
    """Whether a ratio or worded fraction and a percentage, in either order, agree
    to the nearest percentage point: "one third (33%)", "25% (1 in 4)"."""
    if len(first) != 1 or len(second) != 1:
        return False
    if first[0][2] == "share":
        share, percent = first[0], second[0]
    else:
        share, percent = second[0], first[0]
    return (
        share[2] == "share"
        and percent[1] == PERCENT
        and abs(100 * share[0] - percent[0]) <= 0.5 + 1e-9
    )


def _read(raw):
    """What value_raw prints, as a list of _one_number's tuples, or None if
    it matches no form the checker reads."""
    text = " ".join(raw.lower().split())
    body = WHOLE.fullmatch(text)["body"]
    if body in ZERO:
        return [(0.0, (1,), "words")]
    both = re.fullmatch(r"(.+) \((.+)\)", body)
    if not both:
        return _printed(body)
    first, second = _printed(both[1]), _printed(both[2])
    return first + second if first and second and _restates(first, second) else None


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
    with value_raw's sign unless the normalization documents a worded sign. A
    number's own word sets its scale. Failing that, the normalization's factor
    does, failing that a fixed set for digits and 1 for number words. Delta
    review D1-1: a printed number matches exactly, and only a fraction or a
    ratio's share may round. A `unit_concept: percent` row stores a share in
    percent units, 100 times the fraction. A categorical row prints a label
    with no digits. Any other row matches a form the checker reads."""
    v = r["value"]
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        return ["value is not a number"]
    if not _number(v):
        return ["value is not finite"]
    raw = r["value_raw"] if isinstance(r["value_raw"], str) else ""
    if r["value_kind"] == "categorical":
        if re.search(r"\d", raw):
            return [f"categorical value_raw {raw!r} prints a number"]
        return []
    numbers = _read(raw)
    if numbers is None:
        return [
            f"the checker can't read value_raw {raw!r} as one number; "
            "narrow it to the number the row stores"
        ]
    factors = _factors(r.get("normalization") or "")
    per = 100 if r.get("unit_concept") == "percent" else 1
    exact, near = [], []
    for number, own, kind in numbers:
        if kind == "share":
            near.append(per * number)
        elif kind == "rounded":
            near += [number * s for s in own or (1,)]
        else:
            fallback = SCALES if kind == "digits" else (1,)
            exact += [number * s for s in own or factors or fallback]
    if not (
        any(_same(abs(v), abs(p)) for p in exact)
        or any(_rounded(abs(v), abs(f)) for f in near)
    ):
        return [f"value {v!r} is not value_raw {raw!r} at a stated scale"]
    if (
        WORDED_SIGN.search(r.get("normalization") or "")
        or any(_same(v, p) for p in exact)
        or any(_rounded(v, f) for f in near)
    ):
        return []
    return [f"value {v!r} has the opposite sign to value_raw {raw!r}"]


# README rule 4. A locator that names Figure 1.A or 1.B ("Figure 1.A", "Fig.
# 1A", "Figures 1.A and 1.B") says where HM Treasury prints the number only
# if its first reference, up to its first comma or semicolon, takes one of
# the forms PRINTED reads and nothing more: a paragraph, table or box by its
# number, or a data label. The checker reads any other first reference as a
# bar reading, "Figure 1.A data label unavailable" included. A locator that
# says we read the number off a bar, chart or graph marks a bar reading
# wherever it says so, unless a negation comes just before ("not a bar
# reading", "isn't read off the chart"). The checker looks for these phrases
# with hyphens and dashes as spaces and with runs of spaces collapsed.
FIGURE_1 = re.compile(r"\bfig(?:ure)?s?\.?\s*1\.?\s*[ab]\b", re.I)
_FIG = r"fig(?:ure)?s?\.?\s*1\.?\s*[ab](?:\s+and\s+1\.?\s*[ab])?"
_ID = r"\d+(?:\.[0-9a-z]+)*"
PRINTED = re.compile(
    rf"(?:paragraph|para|table|box)(?:s|es)?\.?\s+{_ID}"
    rf"(?:(?:\s+(?:and|to)\s+|\s*[-–]\s*){_ID})?(?:\s+and\s+{_FIG})?"
    rf"|(?:{_FIG}\s*:?\s+)?data\s+labels?"
    rf"(?:\s+(?:(?:for|on)\s+)?(?:decile|quintile)\s+\d+|\s+(?:for|on)\s+{_FIG})?",
    re.I,
)
_VISUAL = r"(?:the |a )?(?:bars?|charts?|graphs?|figures?)"
BAR_READING = re.compile(
    r"\b(?:bar|chart|graph)s? read(?:ing)?s?\b"
    rf"|\bread(?:s|ing|ings)? (?:off|from) {_VISUAL}\b"
    rf"|\bestimated from {_VISUAL}\b",
    re.I,
)
DENIED = re.compile(
    r"(?:\b(?:no|not|never|without)|n['’]t)\s+(?:(?:a|an|the|been)\s+)?\Z", re.I
)


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
        out.append(
            "no HMT Impact on households bar readings: start the locator with "
            "the paragraph, table, box or data label where HM Treasury prints "
            "the number (README rule 4)"
        )
    return out


def reads_a_bar(locator):
    """README rule 4: whether a locator places the number on a bar of Figure
    1.A or 1.B, rather than naming where HM Treasury prints it."""
    plain = " ".join(re.sub(r"[-−–—‐‑]", " ", locator).split())
    if any(not DENIED.search(plain[: m.start()]) for m in BAR_READING.finditer(plain)):
        return True
    if not FIGURE_1.search(plain):
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
