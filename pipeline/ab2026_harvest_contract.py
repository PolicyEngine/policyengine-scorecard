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


def _numbers(text):
    """The signed numbers printed in a string, as floats."""
    out = []
    text = re.sub(r"([-−–])\s*[£$€]", r"\1", text)  # "-£1.7bn"
    for m in NUMBER.findall(text):
        t = m.replace(",", "").replace("−", "-").replace("–", "-")
        try:
            out.append(float(t))
        except ValueError:
            pass
    for a, b in re.findall(r"(\d[\d,]*(?:\.\d+)?)\s+in\s+(\d[\d,]*(?:\.\d+)?)", text):
        b = float(b.replace(",", ""))
        if b:
            out.append(float(a.replace(",", "")) / b)
    low = text.lower()
    out += [v for w, v in WORDS.items() if re.search(rf"\b{w}\b", low)]
    return out


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
        if f:
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


def value_problems(r):
    """review A H-2: `value` is finite and is value_raw's number at its scale,
    with value_raw's sign unless the normalization documents a worded sign."""
    v = r["value"]
    if not isinstance(v, (int, float)) or isinstance(v, bool):
        return ["value is not a number"]
    if not math.isfinite(v):
        return ["value is not finite"]
    raw = r["value_raw"] if isinstance(r["value_raw"], str) else ""
    numbers = _numbers(raw)
    if not numbers:
        return []  # nothing printed to compare (a categorical label)
    norm = r.get("normalization") or ""
    scales = _scales(raw, norm)
    worded = bool(WORDED_SIGN.search(norm))

    def close(a, b):
        # stored shares round printed fractions ("a third" -> 0.3333)
        return math.isclose(a, b, rel_tol=1e-3, abs_tol=1e-9)

    magnitude = [(n, s) for n in numbers for s in scales if close(abs(v), abs(n) * s)]
    if not magnitude:
        return [f"value {v!r} is not value_raw {raw!r} at a stated scale"]
    if worded or any(close(v, n * s) for n, s in magnitude):
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


def proposed_keys(rows):
    """The proposed measure keys a family's rows name (README rule 2)."""
    return {
        r["conditions"]["proposed_measure_key"]
        for r in rows
        if isinstance(r.get("conditions"), dict)
        and r["conditions"].get("proposed_measure_key")
    }


def row_problems(r, keys, earlier, metrics, units):
    """Every way one staged row breaks the contract, as strings. A malformed
    row is reported, never raised (review A H-6(h))."""
    if not isinstance(r, dict):
        return ["row is not an object"]
    try:
        return _row_problems(r, keys, earlier, metrics, units)
    except (TypeError, AttributeError, KeyError, ValueError) as e:
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
        and "impact on households" in pub.get("title", "").lower()
        and (
            r["value_kind"] == "approx_chart_reading"
            or re.search(r"figure 1\.[ab]\b", pub.get("locator") or "", re.I)
        )
    ):
        out.append("no HMT Impact on households bar readings (README rule 4)")
    return out


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
    out = []
    manifest = read_manifest(family_dir)
    shas = [m.get("sha256", "") for m in manifest]
    for m in manifest:
        if not SHA256.fullmatch(m.get("sha256", "")):
            out.append(f"manifest {m.get('url')}: sha256 is not a sha256")
        if not (m.get("url") and m.get("title") and m.get("retrieved")):
            out.append(f"manifest {m.get('url')}: needs url, title and retrieved")
    if len(set(shas)) != len(shas):
        out.append("manifest lists a primary twice")
    keys, earlier = registry_keys()
    metrics, units = enums()
    rows = read_rows(family_dir)
    for i, r in enumerate(rows):
        for p in row_problems(r, keys, earlier, metrics, units):
            out.append(f"row {i}: {p}")
        pub = r.get("publication") if isinstance(r, dict) else None
        sha = pub.get("primary_sha256") if isinstance(pub, dict) else None
        if sha not in set(shas):
            out.append(f"row {i}: primary_sha256 is not in manifest.jsonl")
    out += duplicate_problems(rows)
    notes = (family_dir / "NOTES.md").read_text()
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
        except (TypeError, KeyError, AttributeError):
            continue  # reported by row_problems
    out = []
    for idx in groups.values():
        if len(idx) > 2:
            out.append(f"rows {idx} share one claim identity (more than 2)")
        elif len(idx) == 2:
            a, b = (rows[i]["value"] for i in idx)
            if not math.isclose(a, b, rel_tol=0.005, abs_tol=1e-9):
                out.append(
                    f"rows {idx} share one claim identity but differ by over 0.5%"
                )
    return out


def main(argv):
    bad = 0
    for d in argv:
        problems = family_problems(d)
        rows = len(read_rows(d)) if (Path(d) / "claims_staged.jsonl.gz").exists() else 0
        print(f"{d}: {rows} rows, {len(problems)} problems")
        for p in problems[:200]:
            print("  " + p)
        bad += bool(problems)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
