"""Reproduce the Scottish Budget-response rows without refetching the primary."""

import gzip
import io
import json
from pathlib import Path


FAMILY = Path(__file__).resolve().parent
PUBLICATION = {
    "title": "UK Budget delivers real cut to Scotland’s funding",
    "url": "https://www.gov.scot/news/uk-budget-delivers-real-cut-to-scotlands-funding/",
    "date": "2026-10-28",
    "publisher": "Scottish Government",
    "primary_sha256": "f3d0183e470f711b6821e4956e108c5d17210a392e6a6e471eccf297c807a6ac",
    "access": "direct",
}

# Reading order: the opening paragraph, then paragraph 2 from left to right.
# Positive values retain the printed magnitudes; the conditions say "reduction".
FIGURES = [
    {
        "component": "Resource and capital budgets",
        "value_raw": "£650 million",
        "value": 650_000_000,
        "unit_concept": "gbp",
        "normalization": "£ million × 1e6 -> GBP; positive magnitude of the reported reduction",
        "quote": "around £650 million in 2027-28",
        "locator": "Opening body paragraph, sentence beginning 'The UK Budget delivers' (HTML line 347)",
        "source_column": "Total real-terms reduction",
        "precision": "around",
    },
    {
        "component": "Resource Block Grant",
        "value_raw": "1.3%",
        "value": 1.3,
        "unit_concept": "percent",
        "normalization": "percent as printed; positive magnitude of the reported reduction",
        "quote": "reduce by 1.3%",
        "locator": "Body paragraph 2, first sentence, resource block grant percentage (HTML line 348)",
        "source_column": "Resource real-terms percentage reduction",
        "precision": "as printed",
    },
    {
        "component": "Resource Block Grant",
        "value_raw": "£550 million",
        "value": 550_000_000,
        "unit_concept": "gbp",
        "normalization": "£ million × 1e6 -> GBP; positive magnitude of the reported reduction",
        "quote": "around £550 million",
        "locator": "Body paragraph 2, first sentence, cash equivalent of resource reduction (HTML line 348)",
        "source_column": "Resource real-terms reduction, cash equivalent",
        "precision": "around",
    },
    {
        "component": "Capital budget",
        "value_raw": "1.5%",
        "value": 1.5,
        "unit_concept": "percent",
        "normalization": "percent as printed; positive magnitude of the reported reduction",
        "quote": "a 1.5% real terms reduction",
        "locator": "Body paragraph 2, second sentence, capital percentage (HTML line 348)",
        "source_column": "Capital real-terms percentage reduction",
        "precision": "as printed",
    },
    {
        "component": "Capital budget",
        "value_raw": "£100 million",
        "value": 100_000_000,
        "unit_concept": "gbp",
        "normalization": "£ million × 1e6 -> GBP; positive magnitude of the reported reduction",
        "quote": "around £100 million",
        "locator": "Body paragraph 2, second sentence, cash equivalent of capital reduction (HTML line 348)",
        "source_column": "Capital real-terms reduction, cash equivalent",
        "precision": "around",
    },
]


def rows():
    for figure in FIGURES:
        yield {
            "source": "scottish_government",
            "source_model": "arithmetic",
            "proposed_metric": "block_grant_effect",
            "unit_concept": figure["unit_concept"],
            "value": figure["value"],
            "value_raw": figure["value_raw"],
            "normalization": figure["normalization"],
            "value_kind": "point",
            "period": 2028,
            "time_basis": "fiscal_year",
            "conditions": {
                "fiscal_event": "autumn_budget_2026",
                "fy": "2027-28",
                "geography": "Scotland",
                "basis": "forecast",
                "component": figure["component"],
                "price_basis": "real terms; base year not specified",
                "comparison_basis": "reported funding reduction; comparator not specified in the primary",
                "sign_convention": "positive = magnitude of reduction in Scottish Government funding",
                "precision": figure["precision"],
            },
            "reform_hint": None,
            "measure_key": None,
            "attribution": "own",
            "benchmark_class": "different_model",
            "baseline_policy": None,
            "publication": {**PUBLICATION, "locator": figure["locator"]},
            "source_table": None,
            "source_column": figure["source_column"],
            "quote": figure["quote"],
            "note": (
                "Scottish Government's reported real-terms funding projection, not an isolated "
                "costing of AB2026 decisions. The article does not name an original estimator, "
                "a comparison baseline or a price base year. No measure key or proposed measure "
                "key is assigned. Positive printed magnitudes are retained, with the reduction "
                "direction recorded in conditions. This is not a cash-terms Barnett consequential."
            ),
            "parse_confidence": "high",
            "status": "ok",
        }


def main():
    claims = list(rows())
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb", mtime=0, filename="") as fh:
        for row in claims:
            fh.write((json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n").encode())
    destination = FAMILY / "claims_staged.jsonl.gz"
    destination.write_bytes(buf.getvalue())
    print(f"{destination.name}: {len(claims)} rows")


if __name__ == "__main__":
    main()
