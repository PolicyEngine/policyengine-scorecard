"""Baseline moments: join external tracker claims with our counterparts.

Additive sibling of build_comparison.py for the claim class Max named
baseline moments: current-law statistics published by external modelers
(average tariff rates today; average tax rate tables tomorrow), each
compared against our computation with the construct difference stated.

Join key: (program, metric, subgroup, geography, period). Status logic:
  comparable        external and PE rows share the same variant
  concept_mismatch  a PE row exists for the period but under a different
                    construct variant (the delta is still shown, annotated)
  not_computed      no PE row for the period
Every external row appears; the misses stay on the page.
Output: app/public/data/moments.json.
"""

import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXTERNALS = ROOT / "data" / "externals"
SOURCES = ("yale-tariff-tracker", "tpc-tariffs")


def load_annotations():
    entries = []
    for source in SOURCES:
        path = ROOT / "sources" / source / "annotations.json"
        entries.extend(json.loads(path.read_text()))
    return entries


def main():
    pe_payload = json.loads(
        (ROOT / "data" / "pe" / "tariff_counterparts.json").read_text()
    )
    pe_rows = {
        (r["program"], r["metric"], r["subgroup"], r["geography"], r["period"]): r
        for r in pe_payload["rows"]
    }
    annotations = load_annotations()
    source_annotation_ids = {}
    for entry in annotations:
        source_annotation_ids.setdefault(entry["applies"]["source"], []).append(
            entry["id"]
        )

    rows = []
    for source in SOURCES:
        meta = json.loads((ROOT / "sources" / source / "source.json").read_text())
        for ext in json.loads((EXTERNALS / f"{source}.json").read_text()):
            key = (
                ext["program"],
                ext["metric"],
                ext["subgroup"],
                ext["geography"],
                ext["period"],
            )
            pe = pe_rows.get(key)
            if pe is None:
                status, pe_value, pe_variant = "not_computed", None, None
            elif pe["variant"] == ext["variant"]:
                status, pe_value, pe_variant = "comparable", pe["value"], pe["variant"]
            else:
                status, pe_value, pe_variant = (
                    "concept_mismatch",
                    pe["value"],
                    pe["variant"],
                )
            rows.append(
                {
                    **{
                        k: ext[k]
                        for k in (
                            "source",
                            "program",
                            "metric",
                            "subgroup",
                            "variant",
                            "geography",
                            "unit_concept",
                            "period",
                        )
                    },
                    "claim_class": meta.get("claim_class", "baseline_moment"),
                    "external_value": ext["value"],
                    "pe_value": pe_value,
                    "pe_variant": pe_variant,
                    "delta": None if pe_value is None else pe_value - ext["value"],
                    "status": status,
                    "annotation_ids": source_annotation_ids.get(source, []),
                }
            )

    statuses = {}
    for row in rows:
        statuses[row["status"]] = statuses.get(row["status"], 0) + 1
    payload = {
        "built": date.today().isoformat(),
        "claim_class": "baseline_moment",
        "pe_provenance": pe_payload["provenance"],
        "sources": SOURCES,
        "summary": {"rows": len(rows), "by_status": statuses},
        "annotations": annotations,
        "rows": rows,
    }
    out = ROOT / "app" / "public" / "data" / "moments.json"
    out.write_text(json.dumps(payload, indent=1) + "\n")
    print(f"{out}: {len(rows)} rows {statuses}")


if __name__ == "__main__":
    main()
