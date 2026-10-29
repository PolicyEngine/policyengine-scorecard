"""The AB2026 harvest row contract (#230), as one checkable function.

sources/harvest-uk-ab2026-2026-10-29/README.md states the contract: the AB2025
row contract with the AB2026 exceptions. tests/test_uk_ab2026_harvest.py
holds every pinned family to it, and a family being staged can be checked on
its own before COUNTS.json pins it:

    python pipeline/ab2026_harvest_contract.py sources/harvest-uk-ab2026-2026-10-29/uk_rf_ab2026
"""

import gzip
import json
import re
import sys
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
PROPOSED_KEY = re.compile(r"ab2026(_option)?__[a-z0-9_]+")
SHA256 = re.compile(r"[0-9a-f]{64}")


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


def row_problems(r, keys, earlier, metrics, units):
    """Every way one staged row breaks the contract, as strings."""
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
    if not isinstance(r["value"], (int, float)) or isinstance(r["value"], bool):
        out.append("value is not a number")
    for field in ("value_raw", "quote"):
        if not (isinstance(r[field], str) and r[field].strip()):
            out.append(f"{field} is empty")
    if bool(r.get("metric")) == bool(r.get("proposed_metric")):
        out.append("exactly one of metric and proposed_metric")
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
        if not m:
            out.append(f"conditions.fy {c['fy']!r} is not YYYY-YY")
        else:
            if r["period"] != int(m.group(1)) + 1:
                out.append(f"period {r['period']} is not the end year of {c['fy']}")
            if r["time_basis"] != "fiscal_year":
                out.append("an fy row has time_basis fiscal_year")
    if not (isinstance(r["period"], int) and 1945 <= r["period"] <= 2075):
        out.append(f"period {r['period']!r} is not a year")

    k = r["measure_key"]
    if "recosting_of" in c:
        if k not in earlier.get(c["recosting_of"], ()):
            out.append(f"{k} is not a {c['recosting_of']} key")
    elif k is not None:
        if k not in keys:
            out.append(f"measure_key {k} is not in data/uk/ab2026_measures.json")
        if "proposed_measure_key" in c:
            out.append("a row with a measure_key carries no proposed_measure_key")
    elif c.get("proposed_measure_key"):
        pk = c["proposed_measure_key"]
        if not PROPOSED_KEY.fullmatch(pk):
            out.append(f"proposed_measure_key {pk!r} is not ab2026[_option]__slug")
        if pk in keys:
            out.append(f"{pk} is registered; put it in measure_key")

    pub = r["publication"]
    for field in ("title", "url", "date", "publisher", "primary_sha256"):
        if not pub.get(field):
            out.append(f"publication.{field} is empty")
    if pub.get("primary_sha256") and not SHA256.fullmatch(pub["primary_sha256"]):
        out.append("publication.primary_sha256 is not a sha256")
    if pub.get("date") and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", pub["date"]):
        out.append("publication.date is not YYYY-MM-DD")

    if r["source"] not in OGL and len(r["quote"].split()) >= 15:
        out.append("quote has 15 or more words (README rule 6)")
    if r["attribution"] == "same_assumptions" and (
        r["benchmark_class"] != "same_assumptions"
        or r["source_model"] != "policyengine_uk"
    ):
        out.append("same_assumptions rows are PolicyEngine-computed")
    if (
        r["source"] == "hm_treasury"
        and "Impact on households" in pub.get("title", "")
        and r["value_kind"] == "approx_chart_reading"
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
    for i, r in enumerate(read_rows(family_dir)):
        for p in row_problems(r, keys, earlier, metrics, units):
            out.append(f"row {i}: {p}")
        sha = (r.get("publication") or {}).get("primary_sha256")
        if sha not in set(shas):
            out.append(f"row {i}: primary_sha256 is not in manifest.jsonl")
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
