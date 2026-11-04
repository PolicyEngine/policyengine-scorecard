"""Reproduce the devolved governments' AB2026 harvest without refetching a page.

The Welsh Government's written statement (rows 0-13) and, since
3 November 2026, the Scottish Government's news release (rows 14-18), which
the thinktanks-b review (finding 7) moved here from uk_fai_sfc so that both
devolved governments sit in one family.
"""

import gzip
import io
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SHA256 = "87490552c36d8ffd5787db18127704e467d93599e5708627adb6da7dcfe17c7c"
URL = "https://www.gov.wales/written-statement-welsh-government-response-uk-autumn-budget-2026"
TITLE = "Written Statement: Welsh Government response to the UK Autumn Budget 2026"
# Review finding 3: the key names the scope (Barnett consequentials of the
# Budget's decisions), not the nation, so that HM Treasury's own figures for
# the same scope (uk_hmt_redbook) share it. The nation is in `geography`.
PROPOSED_PACKAGE = "ab2026__package_barnett_consequentials"
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
    "Welsh Government's reported changes to its block grant from UK Government "
    "decisions at the Budget, by resource and capital, as printed in Table 1, "
    "excluding employer pension contribution savings. Wales's part of the "
    "proposed package of the Budget's Barnett consequentials."
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
            {**change, "row_type": "total", "horizon": "2026-27 to 2029-30 (Table 1)"},
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
                # Review finding 2: Resource and Capital are parts of the
                # Total; the Totals carry row_type "total" and no component.
                ({**change, "row_type": "total", "fy": fy} if component == "Total"
                 else {**change, "component": component,
                       "row_type": "measure_component", "fy": fy}),
                int(fy[:4]) + 1,
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
            # Context rows: `budget`, not `component` (rule 9 reserves
            # `component` for parts of a measure; review finding 6's reasoning).
            {"budget": component, "fy": fy, "basis": "forecast",
             "price_basis": "real terms; price year not stated",
             "sign_convention": "positive = magnitude of reported real-terms funding reduction",
             "qualifier": qualifier,
             "comparison": "settlement level; comparison year not expressly stated"},
            int(fy[:4]) + 1, unit_concept="percent",
            # Review finding 4: a real-terms change in the whole settlement is
            # not a policy's effect on the grant (AB2025's block_grant_effect).
            proposed_metric="devolved_funding_real_terms_change",
            normalization="percent as printed; lower denotes reduction, magnitude retained",
            value_kind="range_high" if component == "Capital" else "point",
            reform_hint=None,
            note=("Context: real-terms change in the full Welsh settlement, not the isolated "
                  "effect of the Budget's additional funding. No measure or proposed measure "
                  "key. Next financial year means 2027-28 given publication on 28 October "
                  "2026. Price year and comparison year are not specified; neither is invented."),
        ))
    return result


# ---------------------------------------------------------------------------
# Scottish Government, moved from uk_fai_sfc on 3 November 2026 (review
# finding 7). Rows and manifest line unchanged except the metric (finding 4)
# and `component` renamed `budget` on these context rows.

SCOT_MANIFEST = {
    "url": "https://www.gov.scot/news/uk-budget-delivers-real-cut-to-scotlands-funding/",
    "title": "UK Budget delivers real cut to Scotland’s funding",
    "date": "2026-10-28",
    "publisher": "Scottish Government",
    "sha256": "f3d0183e470f711b6821e4956e108c5d17210a392e6a6e471eccf297c807a6ac",
    "bytes": 27662,
    "doc_type": "html",
    "access": "direct",
    "retrieved": "2026-10-29",
    "note": "Fresh exact prescribed browser-UA curl fetched HTTP 200 at 2026-10-29T15:22:47Z. SHA256 covers the fetched HTML bytes. Visible publication timestamp is 28 October 2026 15:45. JSON-LD dateModified is 2026-10-29T08:22:59Z, while dc.date.modified repeats 2026-10-28 15:45; no earlier copy was supplied, so a numerical change cannot be established. Five rows, read from opening body paragraphs 1–2. First staged in the uk_fai_sfc lane on 29 October; moved to uk_devolved_govts on 3 November 2026."
}


SCOT_PUBLICATION = {
    "title": "UK Budget delivers real cut to Scotland’s funding",
    "url": "https://www.gov.scot/news/uk-budget-delivers-real-cut-to-scotlands-funding/",
    "date": "2026-10-28",
    "publisher": "Scottish Government",
    "primary_sha256": "f3d0183e470f711b6821e4956e108c5d17210a392e6a6e471eccf297c807a6ac",
    "access": "direct",
}

# Scottish Government. Reading order: the opening paragraph, then paragraph 2 from left to right.
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


def scottish_rows():
    for figure in FIGURES:
        yield {
            "source": "scottish_government",
            "source_model": "arithmetic",
            "proposed_metric": "devolved_funding_real_terms_change",  # review finding 4
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
                "budget": figure["component"],  # a context row: `budget`, not `component`
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
            "publication": {**SCOT_PUBLICATION, "locator": figure["locator"]},
            "source_table": None,
            "source_column": None,  # review B, finding 2: no printed column label
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


# === review B fixes, 4 November 2026 ======================================
# Review B (PR #231, issue comment 6635498758), uk_devolved_govts findings 1
# and 2, with the coordinator's Barnett call (brief section 3.3): the shared
# key's scope is the red book's (the consequentials of the Budget's decisions
# for the three devolved governments), so every Welsh row on it is a part,
# named "Welsh Government" (rule 9: "a part can be ... a nation"). Red book
# row 258 is the key's total. No primary was re-opened; no value changes.

def review_fixes(result):
    welsh = result[:14]
    for r in welsh[:12]:
        c = r["conditions"]
        assert c["proposed_measure_key"] == PROPOSED_PACKAGE, r
        if c["row_type"] == "total":  # the £448m and the four Table 1 Totals
            assert "component" not in c, r
            c["component"] = "Welsh Government"
        else:  # Table 1's Resource and Capital cells
            c["component"] = "Welsh Government: " + c["component"]
        c["row_type"] = "measure_component"
    # Finding 1: the £448m is the total over 2026-27 to 2029-30, indexed to
    # the final year (period 2030), so it names that fiscal year.
    assert welsh[0]["value_raw"] == "£448m" and welsh[0]["period"] == 2030
    welsh[0]["conditions"]["fy"] = "2029-30"
    # Finding 2: row 13's quote is the paragraph's third sentence, and the
    # "next financial year" sentence of the shared note belongs to row 12.
    r13 = welsh[13]
    assert r13["value_raw"] == "almost 10%"
    r13["publication"]["locator"] = "Second paragraph after Table 1, third sentence"
    r13["note"] = r13["note"].replace(
        " Next financial year means 2027-28 given publication on 28 October 2026.", "")
    return result


def main():
    (HERE / "manifest.jsonl").write_text(
        "".join(json.dumps(m, sort_keys=True, ensure_ascii=False) + "\n" for m in (MANIFEST, SCOT_MANIFEST)),
        encoding="utf-8",
    )
    claims = review_fixes(rows()) + list(scottish_rows())
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb", mtime=0, filename="") as fh:
        for item in claims:
            fh.write((json.dumps(item, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8"))
    (HERE / "claims_staged.jsonl.gz").write_bytes(buf.getvalue())
    print(f"{HERE.name}: {len(claims)} rows")


if __name__ == "__main__":
    main()
