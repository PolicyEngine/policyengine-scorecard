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
# What a malformed row raises when the checks reach it: a field of the wrong
# type, a missing field, an integer with too many digits to print, or nesting
# too deep to print or encode. The checker reports these as problems (review A
# H-6(h); delta review D1-3; final review F3). _number turns away an integer
# too large for a float before any arithmetic, so no check overflows.
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
# "N in M" prints a ratio: the share N/M, never N or M on its own (delta
# review D1-1). "In" may take any case or hyphens ("1 IN 4", "1-in-4"), a
# minus on N carries to the share, and N and M may be number words ("one in
# ten"). A year after "in" ("£5 in 2027") is no denominator unless the
# normalization gives the ratio ("1 in 2000 -> 0.0005", "N in M -> N/M")
# (final review F1).
NUMBER_WORDS = {
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
    "twenty": 20,
    "thirty": 30,
    "forty": 40,
    "fifty": 50,
    "sixty": 60,
    "seventy": 70,
    "eighty": 80,
    "ninety": 90,
    "a hundred": 100,
    "one hundred": 100,
    "a thousand": 1000,
    "one thousand": 1000,
}
_OPERAND = r"\d[\d,]*(?:\.\d+)?|" + "|".join(
    re.escape(w).replace(r"\ ", " ").replace(" ", r"\s+")
    for w in sorted(NUMBER_WORDS, key=len, reverse=True)
)
RATIO = re.compile(
    rf"(?<![\w.])([-−–])?({_OPERAND})(?:\s+|\s*-\s*)in(?:\s+|\s*-\s*)({_OPERAND})"
    r"(?!\w|\.\d|-\w)",
    re.I,
)
YEAR = re.compile(r"(?:19|20)\d\d")
GENERIC_RATIO = re.compile(r"\bN\s+in\s+M\b")
ARROW = re.compile(r"\s*(?:->|→)")
# README rule 4: a locator's leading reference, up to its first comma or
# semicolon, says where HM Treasury prints the number: a data label when it
# names Figure 1.A or 1.B, else a paragraph, table, box or data label. A
# locator that names Figure 1.A or 1.B anywhere, in any of the spellings
# "Figure 1.A", "Fig. 1A" or "Figures 1.A and 1.B", needs such a reference,
# free of any negation ("no data labels", "data label missing", "isn't
# labelled"), and one that calls the number a bar or chart reading reads a
# bar whatever else it names (delta review D1; final review F4).
FIGURE_1 = re.compile(r"\bfig(?:ure)?s?\.?\s*1\.?\s*[ab]\b", re.I)
PRINTED_AT = re.compile(r"\b(?:paragraph|para|table|box)s?\b", re.I)
DATA_LABEL = re.compile(r"\bdata labels?\b", re.I)
NEGATION = re.compile(
    r"\b(?:no|not|none|never|without|missing|absent|lacks?|lacking|unlabell?ed)\b"
    r"|n['’]t\b",
    re.I,
)
BAR_READING = re.compile(
    r"\b(?:bar|chart|graph) readings?\b"
    r"|\bread (?:off|from) (?:the |a )?(?:bars?|charts?|graphs?|figures?)\b",
    re.I,
)
WORDS = {
    "half": 0.5,
    "a half": 0.5,
    "one half": 0.5,
    "a third": 1 / 3,
    "one third": 1 / 3,
    "two thirds": 2 / 3,
    "two-thirds": 2 / 3,
    "a quarter": 0.25,
    "one quarter": 0.25,
    "three quarters": 0.75,
    "three-quarters": 0.75,
    "two-fifths": 0.4,
    "two fifths": 0.4,
}


def _operand(text):
    """A ratio's number, from digits or number words ("1,000", "a hundred")."""
    word = re.sub(r"\s+", " ", text.lower())
    if word in NUMBER_WORDS:
        return float(NUMBER_WORDS[word])
    return float(text.replace(",", ""))


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
    """The ratios a string prints, as ((start, end), N/M), the share signed
    as N is."""
    out = []
    for m in RATIO.finditer(text):
        sign, n, d = m.groups()
        if YEAR.fullmatch(d) and not _gives_ratio(normalization, n, d):
            continue  # "£5 in 2027"
        a, b = _operand(n), _operand(d)
        if b and math.isfinite(a) and math.isfinite(b):
            out.append((m.span(), (-a if sign else a) / b))
    return out


def _numbers(text, normalization=""):
    """The numbers a string prints, as (exact, fractions). Exact numbers are
    its signed digits. Fractions are its ratios ("1 in 4" -> 0.25), whose two
    numbers count for nothing on their own, and its worded fractions ("a
    third"), which a stored share may round (delta review D1-1)."""
    text = re.sub(r"([-−–])\s*[£$€]", r"\1", text)  # "-£1.7bn"
    fractions = []
    for (start, end), share in reversed(_ratios(text, normalization)):
        fractions.append(share)
        text = f"{text[:start]} {text[end:]}"
    exact = []
    for m in NUMBER.findall(text):
        t = m.replace(",", "").replace("−", "-").replace("–", "-")
        try:
            exact.append(float(t))
        except ValueError:
            pass
    low = text.lower()
    fractions += [v for w, v in WORDS.items() if re.search(rf"\b{w}\b", low)]
    return exact, fractions


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
    of a printed ratio or worded fraction, the fraction itself, may round."""
    v = r["value"]
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        return ["value is not a number"]
    if not _number(v):
        return ["value is not finite"]
    raw = r["value_raw"] if isinstance(r["value_raw"], str) else ""
    norm = r.get("normalization") or ""
    exact, fractions = _numbers(raw, norm)
    if not (exact or fractions):
        return []  # nothing printed to compare (a categorical label)
    printed = [n * s for n in exact for s in _scales(raw, norm)]
    if not (
        any(_same(abs(v), abs(p)) for p in printed)
        or any(_rounded(abs(v), abs(f)) for f in fractions)
    ):
        return [f"value {v!r} is not value_raw {raw!r} at a stated scale"]
    if (
        WORDED_SIGN.search(norm)
        or any(_same(v, p) for p in printed)
        or any(_rounded(v, f) for f in fractions)
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
        if not (isinstance(r[field], str) and r[field].strip()):
            out.append(f"{field} is empty")
    if not all(isinstance(r[f], str) for f in ("value_raw", "quote")):
        return out
    if not isinstance(r["publication"], dict):
        return out + ["publication is not an object"]
    if r["measure_key"] is not None and not isinstance(r["measure_key"], str):
        return out + ["measure_key is not a string or null"]
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
    if not (isinstance(c, dict) and c):
        return out + ["conditions is not a non-empty object"]
    for k, v in c.items():
        if not (isinstance(k, str) and isinstance(v, str)):
            out.append(f"condition {k!r} is not a string")
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
    if BAR_READING.search(locator):
        return True
    if not FIGURE_1.search(locator):
        return False
    lead = re.split(r"[,;]", locator, maxsplit=1)[0]
    if NEGATION.search(lead):
        return True
    if FIGURE_1.search(lead):
        return not DATA_LABEL.search(lead)
    return not (PRINTED_AT.search(lead) or DATA_LABEL.search(lead))


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
