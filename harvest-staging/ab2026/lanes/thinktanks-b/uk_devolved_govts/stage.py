"""Reproduce the Welsh Government AB2026 harvest without refetching a page."""

import gzip
import io
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SHA256 = "87490552c36d8ffd5787db18127704e467d93599e5708627adb6da7dcfe17c7c"
URL = "https://www.gov.wales/written-statement-welsh-government-response-uk-autumn-budget-2026"
TITLE = "Written Statement: Welsh Government response to the UK Autumn Budget 2026"
PROPOSED_PACKAGE = "ab2026__package_welsh_settlement_changes"
MANIFEST = {
    "url": URL,
    "title": TITLE,
    "date": "2026-10-28",
    "publisher": "Welsh Government",
    "sha256": SHA256,
    "bytes": 26908,
    "doc_type": "html",
    "access": "direct",
    "retrieved": "2026-10-29",
    "note": (
        "Fresh curl -sSL fetch with the assigned Safari User-Agent; HTTP 200, "
        "completed 2026-10-29T15:22:18Z (HTTP Date header). SHA256 is of the "
        "unaltered HTML bytes saved as .ab2026-primaries/uk_devolved_govts/"
        "welsh-response.html. Publication and last-updated dates both print "
        "28 October 2026. No assignment local copy was supplied."
    ),
}

# Printed table cells, in document reading order. N/A is deliberately not zero.
YEARS = ["2026-27", "2027-28", "2028-29", "2029-30"]
TABLE = [
    ("Resource", ["199", "165", "146", None]),
    ("Capital", ["-27", "-19", "2", "-18"]),
    ("Total", ["172", "146", "148", "-18"]),
]
SCOPE_NOTE = (
    "Welsh Government's reported settlement changes following the Budget, "
    "excluding employer pension contribution savings. The primary does not "
    "enumerate Table 6.1 lines, so this is a proposed package, not a claim "
    "that its scope equals all Table 6.1 spending decisions."
)


def row(raw, value, quote, locator, conditions, period, **overrides):
    result = {
        "source": "welsh_government",
        "source_model": "arithmetic",
        "proposed_metric": "block_grant_effect",
        "unit_concept": "gbp",
        "value_raw": raw,
        "value": value,
        "normalization": "£ million × 1e6 -> GBP; sign as printed",
        "value_kind": "point",
        "period": period,
        "time_basis": "fiscal_year",
        "conditions": {
            "fiscal_event": "autumn_budget_2026",
            "geography": "Wales",
            **conditions,
        },
        "reform_hint": "Changes to the Welsh Government Settlement following the UK Autumn Budget 2026",
        "measure_key": None,
        "attribution": "own",
        "benchmark_class": "different_model",
        "baseline_policy": None,
        "publication": {
            "title": TITLE,
            "url": URL,
            "date": "2026-10-28",
            "publisher": "Welsh Government",
            "primary_sha256": SHA256,
            "locator": locator,
            "access": "direct",
        },
        "source_table": None,
        "source_column": None,
        "quote": quote,
        "note": SCOPE_NOTE,
        "parse_confidence": "high",
        "status": "ok",
    }
    result.update(overrides)
    return result


def rows():
    change = {
        "proposed_measure_key": PROPOSED_PACKAGE,
        "mechanism": "Barnett consequentials / changes to Welsh settlement",
        "sign_convention": "positive = increase in Welsh Government funding",
        "price_basis": "cash; no real-terms adjustment stated for Table 1",
        "exclusion": "employer pension contribution savings",
    }
    result = [
        row(
            "£448m", 448000000,
            "an additional £448m of funding over the current spending review period.",
            "Paragraph immediately before Table 1, first sentence",
            {**change, "component": "Total", "horizon": "2026-27 to 2029-30 (Table 1)"},
            2030, value_kind="cumulative",
        )
    ]
    for component, cells in TABLE:
        for fy, raw in zip(YEARS, cells):
            if raw is None:
                continue
            result.append(row(
                raw, int(raw) * 1000000, raw,
                f"Table 1: Changes to the Welsh Government Settlement; {component} row; {fy} column (£m)",
                {**change, "component": component, "fy": fy}, int(fy[:4]) + 1,
                source_table="Table 1: Changes to the Welsh Government Settlement",
                source_column=fy,
            ))
    for raw, value, component, fy, quote, locator, qualifier in [
        ("0.5%", 0.5, "Resource", "2027-28",
         "0.5% lower in real terms next financial year.",
         "First paragraph after Table 1 and rounding footnote, final sentence", "as printed"),
        ("almost 10%", 10, "Capital", "2029-30",
         "capital funding will be almost 10% lower in real terms by 2029-30.",
         "Second paragraph after Table 1, second sentence", "almost; magnitude below 10%"),
    ]:
        result.append(row(
            raw, value, quote, locator,
            {"component": component, "fy": fy, "basis": "forecast",
             "price_basis": "real terms; price year not stated",
             "sign_convention": "positive = magnitude of reported real-terms funding reduction",
             "qualifier": qualifier,
             "comparison": "settlement level; comparison year not expressly stated"},
            int(fy[:4]) + 1, unit_concept="percent",
            normalization="percent as printed; lower denotes reduction, magnitude retained",
            value_kind="range_high" if component == "Capital" else "point",
            reform_hint=None,
            note=("Context: real-terms change in the full Welsh settlement, not the isolated "
                  "effect of the Budget's additional funding. No measure or proposed measure "
                  "key. Next financial year means 2027-28 given publication on 28 October "
                  "2026. Price year and comparison year are not specified; neither is invented."),
        ))
    return result


def main():
    (HERE / "manifest.jsonl").write_text(
        json.dumps(MANIFEST, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb", mtime=0, filename="") as fh:
        for item in rows():
            fh.write((json.dumps(item, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8"))
    (HERE / "claims_staged.jsonl.gz").write_bytes(buf.getvalue())
    print(f"{HERE.name}: {len(rows())} rows")


if __name__ == "__main__":
    main()
