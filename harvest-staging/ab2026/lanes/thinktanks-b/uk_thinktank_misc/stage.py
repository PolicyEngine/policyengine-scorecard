"""Reproduce this family's claims and manifest from the embedded primary readings.

Only Python's standard library is required. Primaries are hashed, not vendored.
"""

import gzip
import io
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
DOCUMENTS = {
    "cps": {
        "url": "https://cps.org.uk/media/post/2026/a-dangerous-continuation-of-labours-tax-and-spend-fantasy-cps-verdict-on-the-budget/",
        "title": "'A dangerous continuation of Labour's tax-and-spend fantasy' - CPS verdict on the Budget",
        "publisher": "Centre for Policy Studies",
        "sha256": "2c832e011866eb9f63f20597e7bf43bc01d44b6b1b5be43eee866ad6fc5ecd24",
        "bytes": 70197,
        "fetch_time": "2026-10-29T15:22:34Z",
    },
    "ifg": {
        "url": "https://www.instituteforgovernment.org.uk/comment/john-healeys-underwhelming-budget",
        "title": "John Healey’s underwhelming budget punts big decisions into 2027",
        "publisher": "Institute for Government",
        "sha256": "ecf19f14b4f808846fb8230b28a3244b0b65812484735842f9ab537a50195c69",
        "bytes": 153352,
        "fetch_time": "2026-10-29T15:22:31Z",
    },
    "age_uk": {
        "url": "https://www.ageuk.org.uk/latest-press/age-uk-response-to-the-budget/",
        "title": "Age UK's Response to the Chancellor's Autumn Budget",
        "publisher": "Age UK",
        "sha256": "3035a8bbbb0f023dc24e805b430052163aa0dbfce3c975a6e0a0568983db6bf0",
        "bytes": 105862,
        "fetch_time": "2026-10-29T15:22:31Z",
    },
    "lwi": {
        "url": "https://learningandwork.org.uk/responding-to-autumn-budget-2026/",
        "title": "Responding to Autumn Budget 2026",
        "publisher": "Learning and Work Institute",
        "sha256": "c7fe077a0d9f4784aa4c91c906bcefa087cc9a4ece8b28026d24347c2a8b5dcf",
        "bytes": 122809,
        "fetch_time": "2026-10-29T15:22:31Z",
    },
    "citizens_advice": {
        "url": "https://www.citizensadvice.org.uk/about-us/media-centre/press-releases/citizens-advice-responds-to-chancellors-budget/",
        "title": "Citizens Advice responds to Chancellor's Budget",
        "publisher": "Citizens Advice",
        "sha256": "6a10336a67fc058512a4ccd9d0e80a27470fee8ba5775690fb1fcba39db67385",
        "bytes": 22671,
        "fetch_time": "2026-10-29T15:23:24Z",
    },
    "trussell": {
        "url": "https://www.trussell.org.uk/news-and-research/news/our-response-to-the-autumn-budget-2026",
        "title": "Our response to the Autumn Budget 2026",
        "publisher": "Trussell",
        "sha256": "6cd2162d1382f03e937a382a39bd38c497a83d357bd969d2c85598740d17a95e",
        "bytes": 171343,
        "fetch_time": "2026-10-29T15:23:24Z",
    },
}


def row(document, source, source_model, value_raw, value, quote, locator, *,
        metric=None, proposed_metric=None, unit="gbp", proposed_unit=None,
        normalization="as printed", value_kind="point", period=2026,
        time_basis="point_in_time", conditions=None, reform_hint=None,
        measure_key=None, attribution="own", benchmark_class="different_model",
        note=None, parse_confidence="high"):
    doc = DOCUMENTS[document]
    return {
        "source": source,
        "source_model": source_model,
        "metric": metric,
        "proposed_metric": proposed_metric,
        "unit_concept": unit,
        "proposed_unit": proposed_unit,
        "value": value,
        "value_raw": value_raw,
        "normalization": normalization,
        "value_kind": value_kind,
        "period": period,
        "time_basis": time_basis,
        "conditions": {"fiscal_event": "autumn_budget_2026", **(conditions or {})},
        "reform_hint": reform_hint,
        "measure_key": measure_key,
        "attribution": attribution,
        "benchmark_class": benchmark_class,
        "baseline_policy": None,
        "publication": {
            "title": doc["title"], "url": doc["url"], "date": "2026-10-28",
            "publisher": doc["publisher"], "primary_sha256": doc["sha256"],
            "locator": locator, "access": "direct",
        },
        "source_table": None,
        "source_column": None,
        "quote": quote,
        "note": note,
        "parse_confidence": parse_confidence,
        "status": "ok",
    }


# Reading order: document order above; then top to bottom within each document.
# Quotes are contiguous excerpts of the primary's own text, each under 15 words.
ROWS = [
    row("cps", "cps", "administrative_data", "£3 trillion", 3_000_000_000_000,
        "Britain’s national debt now tops £3 trillion",
        "Liam Halligan statement, paragraph beginning ‘Britain’s national debt’",
        proposed_metric="public_debt_level", value_kind="range_low",
        normalization="£ trillion × 1e12; 'tops' is a strict lower-bound qualifier",
        conditions={"geography": "UK", "basis": "outturn", "horizon": "now, at publication",
                    "sign_convention": "positive = stock of national debt",
                    "originator": "UK official public finance statistics (not explicitly cited)"},
        attribution="restated", benchmark_class="administrative_fact",
        note="Context stock, not a Budget policy effect. The page does not name the original official release or debt definition; no more specific series or observation date is inferred."),
    row("cps", "cps", "administrative_data", "£61 billion", 61_000_000_000,
        "£61 billion spent on debt interest payments alone over the last six months",
        "Liam Halligan statement, paragraph beginning ‘Britain’s national debt’, debt-interest clause",
        proposed_metric="debt_interest_cost", normalization="£ billion × 1e9",
        conditions={"geography": "UK", "basis": "outturn", "horizon": "over the last six months",
                    "sign_convention": "positive = debt interest paid",
                    "originator": "UK official public finance statistics (not explicitly cited)"},
        attribution="restated", benchmark_class="administrative_fact",
        note="Six-month context total, not an annual amount or a Budget policy effect. No fiscal year or exact six-month endpoints are printed; period anchors the statement at publication."),
    row("cps", "cps", "obr_efo_forecast", "£15 billion", 15_000_000_000,
        "fiscal ‘headroom’ buffer down to £15 billion",
        "Liam Halligan statement, final paragraph beginning ‘And by eroding’",
        proposed_metric="fiscal_headroom", normalization="£ billion × 1e9",
        conditions={"geography": "UK", "basis": "forecast", "horizon": "fiscal-rule target year not stated",
                    "sign_convention": "positive = headroom against the fiscal rule",
                    "originator": "OBR fiscal forecast (not explicitly cited)"},
        attribution="restated",
        note="Post-Budget fiscal-rule headroom context. The primary does not print the target fiscal year, so none is supplied; point-in-time period is publication year."),
    row("cps", "cps", "unstated", "£3.1 billion", 3_100_000_000,
        "Labour is increasing debt by £3.1 billion each year",
        "Daniel Herring statement, paragraph beginning ‘By channelling investment into Public Financial Institutions’",
        proposed_metric="public_debt_change", normalization="£ billion × 1e9",
        conditions={"geography": "UK", "basis": "forecast", "horizon": "each year; no start or end year specified",
                    "sign_convention": "positive = increase in public debt",
                    # thinktanks-b review finding 1: context, not a proposal.
                    "measure_type": "debt increase from channelling investment into Public Financial Institutions (PuFins), as asserted by CPS"},
        reform_hint=None,
        note="CPS's own asserted annual debt effect of the government's whole Public Financial Institutions channel, tied to a CPS paper from the week before the Budget; it names no Budget decision, Table 6.1 or 6.2 line or year, so it is context with no measure or proposed key. Method and components are not supplied in this primary. Point-in-time period anchors the annual-rate assertion at publication, without inventing a fiscal or calendar scoring year.",
        parse_confidence="medium"),
    row("ifg", "institute_for_government", "arithmetic", "almost 100", 100,
        "the scorecard stretching to almost 100 policies",
        "Opening body paragraph beginning ‘We were promised’",
        proposed_metric="measure_count", unit=None, proposed_unit="measures",
        normalization="printed threshold 100 measures; 'almost' retained as an upper-bound qualifier",
        value_kind="range_high",
        conditions={"geography": "UK", "measure_type": "number of policies on the Budget scorecard",
                    "horizon": "scorecard as published on 28 October 2026"},
        note="Context count about the Budget document, not a scored package effect. The exact count is not inferred from ‘almost’; 100 is the printed upper threshold."),
    # thinktanks-b review finding 6: the measure IfG counted is a `subgroup`
    # of this context count, not a rule 9 `component`.
    row("ifg", "institute_for_government", "arithmetic", "one", 1,
        "Only one tax measure",
        "‘A budget of many measures but a mostly unchanged fiscal picture’, first paragraph",
        proposed_metric="measure_count", unit=None, proposed_unit="measures",
        normalization="printed word 'one' → 1 measure",
        conditions={"geography": "UK", "measure_type": "tax measures costing or saving more than £1bn in the last forecast year",
                    "subgroup": "a change to capital allowances", "horizon": "last year of the forecast; year not printed"},
        note="IfG's tally of measures exceeding the printed £1bn threshold, not a £1bn costing. Document-level context count; no policy-effect package is inferred."),
    row("ifg", "institute_for_government", "obr_efo_forecast", "56%", 56,
        "a 56% chance, based on past forecast errors",
        "‘A budget of many measures but a mostly unchanged fiscal picture’, second paragraph, current-rule probability",
        proposed_metric="fiscal_rule_probability", unit="percent", period=2030,
        time_basis="fiscal_year",
        conditions={"geography": "UK", "basis": "forecast", "fy": "2029-30",
                    "forecast_vintage": "Autumn Budget 2026", "fiscal_rule": "current budget surplus in 2029/30",
                    "originator": "OBR forecast-error-based fiscal-rule probability"},
        attribution="restated",
        note="Restatement of OBR forecast probability, not a modelled effect of a particular measure."),
    row("ifg", "institute_for_government", "obr_efo_forecast", "59%", 59,
        "down from 59% at the last budget",
        "‘A budget of many measures but a mostly unchanged fiscal picture’, second paragraph, previous-budget comparator",
        proposed_metric="fiscal_rule_probability", unit="percent", period=2030,
        time_basis="fiscal_year",
        conditions={"geography": "UK", "basis": "forecast", "fy": "2029-30",
                    "forecast_vintage": "last budget, as described by IfG", "fiscal_rule": "current budget surplus in 2029/30",
                    "originator": "OBR forecast-error-based fiscal-rule probability"},
        attribution="restated",
        note="The previous-budget comparator is retained as printed; no probability change is derived."),
    row("ifg", "institute_for_government", "unstated", "80%", 80,
        "around 80% will receive the £100 rebate this winter",
        "‘Energy support for households prioritised breadth over targeting’, first paragraph, rebate-coverage sentence",
        proposed_metric="affected_share", unit="percent",
        conditions={"denominator": "all households, as phrased by IfG; geography unspecified",
                    "measure_type": "households receiving the £100 council tax rebate",
                    "horizon": "this winter, as described on 28 October 2026", "precision": "around"},
        reform_hint="a £100 council tax rebate to households in bands A-D",
        measure_key="ab2026__household_energy_payment_100_bands_a_to_d",
        note="IfG does not cite an external source or method for this approximate coverage share; treated as its own unattributed estimate with method unstated. Geography of the household denominator is not printed, so none is inferred. The numerator is specifically the £100 council-tax rebate for bands A-D, identifying Table 6.1 line 1. No fiscal year is printed.",
        parse_confidence="medium"),
    row("ifg", "institute_for_government", "obr_efo_forecast", "2%", 2,
        "only 2% higher in 2030 than before the pandemic",
        "‘Energy support for households prioritised breadth over targeting’, first paragraph, final sentence",
        metric="real_income_growth", unit="percent", period=2030, time_basis="annual",
        conditions={"geography": "UK", "basis": "forecast", "measure_type": "real household disposable incomes",
                    "comparison_period": "before the pandemic", "horizon": "2030 relative to before the pandemic",
                    "price_basis": "real", "sign_convention": "positive = higher real household disposable incomes",
                    "originator": "OBR, explicitly named by IfG"},
        attribution="restated",
        note="Cumulative growth over the producer's comparison window, not annual growth of 2% or a Budget policy effect. The primary does not identify a specific pre-pandemic year.",
        value_kind="cumulative"),
    row("lwi", "learning_and_work_institute", "administrative_data", "one million", 1_000_000,
        "one million young people not in education, employment or training",
        "Stephen Evans response, main quotation, sentence beginning ‘But stability risks turning into stagnation’",
        proposed_metric="affected_count", unit="persons",
        normalization="printed words 'one million' → 1,000,000 persons",
        conditions={"geography": "UK", "basis": "outturn", "subgroup": "young people not in education, employment or training",
                    "horizon": "current labour market, at publication", "originator": "official labour-market statistics (not explicitly cited)"},
        attribution="restated", benchmark_class="administrative_fact",
        note="Rounded labour-market context level, not a Budget effect. No precise age range, reference quarter or original release is identified; the count is treated as a restated official NEET level."),
    row("citizens_advice", "citizens_advice", "unstated", "£60", 60,
        "adding £60 a month to already inflated bills",
        "Dame Clare Moriarty response, second quoted paragraph beginning ‘With energy prices expected to soar’",
        proposed_metric="average_energy_bill_change", unit="gbp_per_month",
        normalization="£60 a month as printed → 60 GBP per month",
        conditions={"basis": "forecast", "horizon": "another difficult winter, as described on 28 October 2026",
                    "sign_convention": "positive = increase in household energy bills"},
        note="Unattributed forecast in Citizens Advice's own response, treated as its own estimate with method unstated. Context energy-price increase, not the effect of a Budget measure. Geography, precise winter dates, price basis and calculation method are not printed; none is inferred.",
        parse_confidence="medium"),
    row("trussell", "trussell", "unstated", "over half", 0.5,
        "over half of private renters on low incomes",
        "Helen Barnard response, second quoted paragraph beginning ‘We know from our research’",
        proposed_metric="affected_share", unit="share", value_kind="range_low",
        normalization="printed 'half' → 0.5 share; 'over' retained as a strict lower-bound qualifier",
        conditions={"geography": "UK", "basis": "outturn", "horizon": "in the last 12 months",
                    "denominator": "private renters on low incomes in receipt of Local Housing Allowance",
                    "measure_type": "ran out of food and could not afford more", "subgroup": "low-income private renters receiving LHA"},
        benchmark_class="administrative_fact",
        note="Trussell explicitly attributes this finding to its own research, but does not identify its method, research dates or an exact percentage. Source model is unstated. Retrospective food-insecurity observation, not a modelled effect of freezing LHA.",
        parse_confidence="medium"),
]


# thinktanks-b review finding 5: Trussell's row and primary move to the
# AB2026 family uk_trussell_wpi (source trussell_wpi), as AB2025 staged
# Trussell's Budget responses; its stage.py there carries the row unchanged
# except the source slug.
ROWS = [r for r in ROWS if r["source"] != "trussell"]
del DOCUMENTS["trussell"]


def main():
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb", mtime=0, filename="") as gz:
        for claim in ROWS:
            gz.write((json.dumps(claim, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8"))
    (HERE / "claims_staged.jsonl.gz").write_bytes(buf.getvalue())
    manifest = []
    for doc in DOCUMENTS.values():
        manifest.append({
            **{key: doc[key] for key in ("url", "title", "publisher", "sha256", "bytes")},
            "date": "2026-10-28", "doc_type": "html", "access": "direct", "retrieved": "2026-10-29",
            "note": f"Fetched HTML fresh with prescribed curl browser User-Agent; HTTP 200; fetch completed {doc['fetch_time']}. Hash is of fetched HTML bytes. No assignment local copy or earlier version was supplied.",
        })
    (HERE / "manifest.jsonl").write_text(
        "".join(json.dumps(doc, sort_keys=True, ensure_ascii=False) + "\n" for doc in manifest),
        encoding="utf-8",
    )
    print(f"Wrote {len(ROWS)} rows and {len(manifest)} primaries to {HERE}")


if __name__ == "__main__":
    main()
