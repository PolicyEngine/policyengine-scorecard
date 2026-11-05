# uk_ifs_ab2026 — Institute for Fiscal Studies, Autumn Budget 2026

We keep `stage.py`, which writes `claims_staged.jsonl.gz`, on branch `uk/ab2026-harvest-staging` at `harvest-staging/ab2026/lanes/ifs/uk_ifs_ab2026/stage.py`. We commit only NOTES.md, `manifest.jsonl` and `claims_staged.jsonl.gz` to this branch. We embedded every row in `stage.py`, so it rebuilds the gzip with no network and no primary file. The harvest keeps its local primaries in `.ab2026-primaries/uk_ifs_ab2026/`, which we never commit, so the repository holds no primary bytes. Fetch each deck from its `manifest.jsonl` URL, and each Flourish embed from the embed URL in its manifest note, and check its sha256. For the two browser-text primaries we took each page's `<main>` text as saved on 29 October. ifs.org.uk refuses curl and embeds per-request tokens in its HTML, so only the saved texts match those two hashes.

We stage **144 rows from 13 primaries**, with `source: ifs`. We list 14 primaries in the manifest: four current briefing decks, the superseded TW_0 deck (no rows), two IFS pages read as browser text, and the public data of seven Flourish visualisations.
- The first lane staged 106 rows from the decks on 29 October.
- On 3 November we applied the IFS addendum (`briefs/ifs-addendum.md` on the staging branch). Under its sections 3 and 4 we cut the deck rows to 87, through an explicit block that follows the deck rows in `stage.py`. Under its sections 1 and 2 we then appended 57 rows in a second JSON block: 11 from the two pages and 46 from the seven visualisations.

Attribution: 48 `own`, 96 `restated`. No primary mentions PolicyEngine. From "Family conventions" on, we keep the first lane's record of 29 October; where it differs from the sections above it, the sections above win.

## Review A fixes, 4 November 2026

Review A (PR #231, issue comment 6635870934) asked for three changes to this family. We put them in a block before `main()` in `stage.py`, with 0-based indices, as review A cites them. The coordinator read Adam's deck (slide 2) and Wernham's (slide 3) for K-7(a) and K-7(e); this session re-opened no primary. We changed no printed value, sign or year.

- H-6(a): we now record the registered metric in `metric` on rows 39 and 40 (`cpi_inflation_rate`) and 47 and 48 (`affected_share`), with `proposed_metric` null.
- K-7(a): we keep row 78 (£1.1bn, lines 61 and 62) at 2031-32 ("Biggest revenue-raisers in 2031–32") and add `conditions.discrepancy`: "IFS prints £1.1bn for 2031-32, where Table 6.1 gives lines 61 and 62 a combined £1,045m."
- K-7(e): row 42 (£5bn). On slide 3 IFS gives it as the cost of the three measures "over next nine months", and HM Treasury's Table 6.1 line 2 costs the whole VAT cut from 1 October 2026. So the re-key to lines 1–3 stands (£5,040m over 2026-27 and 2027-28), and the row's note says so. We mark it `cumulative`, with the time basis of RF's two-year totals: period 2028 (the final fiscal year), `fiscal_year`, no `fy`, and `conditions.horizon` naming both years.

## Coverage

| Primary | Access | Rows | own | restated |
|---|---|--:|--:|--:|
| Weathering the fiscal storm? (Isabel Stockton) | direct | 39 | 2 | 37 |
| Cost of living measures, TW_0 (superseded) | local copy | 0 | 0 | 0 |
| Cost of living measures, TW_1 (Tom Wernham) | direct | 15 | 11 | 4 |
| Spending on public services: the Achilles' heel? (Bee Boileau) | direct | 21 | 19 | 2 |
| Tax measures (Stuart Adam) | direct | 12 | 4 | 8 |
| Autumn Budget 2026: initial response | browser text | 5 | 1 | 4 |
| Collection page: opening remarks by Helen Miller | browser text | 6 | 4 | 2 |
| Flourish 30734907: real household disposable income by decade | Flourish public data | 5 | 5 | 0 |
| Flourish 30726471: current budget deficit, March and October 2026 forecasts | Flourish public data | 11 | 0 | 11 |
| Flourish 30726788: headroom as a share of GDP | Flourish public data | 2 | 0 | 2 |
| Flourish 30726917: real GDP over the forecast | Flourish public data | 11 | 0 | 11 |
| Flourish 30726939: real household disposable income growth by parliament | Flourish public data | 1 | 1 | 0 |
| Flourish 30726047: announced tax changes by fiscal event | Flourish public data | 1 | 1 | 0 |
| Flourish 30727239: higher and additional rate taxpayers | Flourish public data | 15 | 0 | 15 |
| **Total** | | **144** | **48** | **96** |

We take rows 0 to 86 from the decks, by deck, slide and position. Rows 87 to 143 follow in read order: the initial response, the opening remarks, then the seven visualisations in the order above, each by data row and then series.

| measure_key | Rows | of which components (rule 9) | of which from sections 1 and 2 |
|---|--:|--:|--:|
| `null`, context (no key) | 116 | 0 | 52 |
| the four keys we proposed (below) | 7 | 0 | 3 |
| `ab2026__household_energy_payment_100_bands_a_to_d` | 5 | 0 | 2 |
| `ab2026__founders_relief_cgt` | 4 | 0 | 0 |
| `ab2026__package_household_energy_vat_and_fuel_duty` | 3 | 0 | 0 |
| `ab2026__hmrc_tax_gap_package` | 2 | 2 | 0 |
| `ab2026__badr_lifetime_limit_500000` | 1 | 0 | 0 |
| `ab2026__business_rates_sbrr_rhl_thresholds_raised` | 1 | 0 | 0 |
| `ab2026__distributions_framework_modernised` | 1 | 0 | 0 |
| `ab2026__electricity_vat_zero_rate_to_july_2027` | 1 | 0 | 0 |
| `ab2026__fuel_duty_5p_cut_extended_and_rpi_rise_deferred` | 1 | 0 | 0 |
| `ab2026__package_total_tax_policy_decisions` | 1 | 0 | 0 |
| `ab2026__writing_down_allowance_12pc_and_fya_50pc` | 1 | 0 | 0 |

## Keys we proposed

We proposed four keys for seven rows, and in tranche 2 we registered them and moved them into `measure_key`. We spell them under README rule 2 and give each the producer's printed scope (rule 3).

- `ab2026__package_property_and_savings_income_rates` (1 row): exactly Table 6.1 lines 61 and 62. On Adam slide 2 IFS gives "Increased income tax on savings & property income" as £1.1bn in 2031–32 (lines 61 and 62 print 455 + 590 = 1,045). IFS opens slide 2's list "Biggest revenue-raisers in 2031–32", so the year stands, and we record the £55m gap in the row's `conditions.discrepancy` (review A, K-7(a)).
- `ab2026__gas_standing_charge_moved_to_unit_rates` (3 rows): no Table 6.1 line. Wernham slide 8's "Shifting gas standing charge onto unit price": "This charge will be scrapped, but per-unit price will be increased to absorb this". We take the RF family's spelling.
- `ab2026__package_ifs_new_giveaways` (2 rows, from the initial response): IFS's new giveaways, which push up borrowing by £8 billion this year and £4 billion next.
  - IFS names no OBR line and doesn't say the giveaways cover every Government decision since March. So we don't give the rows the key we share across the OBR, HM Treasury red book and RF families for those decisions.
  - To the nearest billion they match the OBR's direct effects of Government decisions in EFO Table 3.1, 7.6 in 2026-27 and 3.5 in 2027-28 (uk_obr_tables). We infer from that match that IFS restates the OBR, so we give both rows medium confidence.
  - Neither the total effect including indirect effects (6.3 and 7.0) nor Table 6.1's total of policy decisions (7,595 and 2,475 £m, uk_hmt_tables) matches both years.
- `ab2026__package_ifs_announced_tax_changes` (1 row, from Flourish 30726047): the tax change that Budget 2026 announced, at the forecast horizon, as a share of GDP as forecast at the event.
  - In the chart's footer IFS credits its own calculations from the OBR's October 2026 EFO, policy measures database and historical official forecasts database.
  - IFS lists no Table 6.1 line and names no OBR grouping, and one rounded figure can't tie the row to the scope of `ab2026__package_total_tax_policy_decisions` or of the OBR's tax decisions since March. So we propose a key in IFS's own terms.

## Keys the addendum changed (rules 3 and 9)

| Rows (first lane, 0-based) | Was | Now | Why |
|---|---|---|---|
| 45, 46, 52 (£5bn, £140, 35%) | proposed `ab2026__package_ifs_cost_of_living_support` | `ab2026__package_household_energy_vat_and_fuel_duty` | IFS's three measures comprise the energy payment, the whole electricity VAT cut and the fuel duty cut, exactly lines 1, 2 and 3 (README rule 3, corrected). Lines 1+2+3 print 5,040 over 2026-27 and 2027-28, IFS's £5bn. Since 4 November we mark the £5bn row (0-based row 42) `cumulative`, period 2028, `fiscal_year`, with the two years in `horizon`, as RF dates its two-year totals, and its note no longer says the scope differs from lines 1–3 (review A, K-7(e)). |
| 48 (£36) | proposed `ab2026__package_ifs_electricity_vat_oct_2026_june_2027` | `ab2026__electricity_vat_zero_rate_to_july_2027` | Line 2 costs the whole cut, 1 October 2026 to 1 July 2027, including the weeks before the Budget. |
| 89 (£1.8bn) | proposed `ab2026__package_ifs_self_assessment_payment_timing` | `ab2026__hmrc_tax_gap_package`, component | Table 6.3 row 3, "More timely payment" for Self Assessment, +1,815m in 2031–32: a part of line 45. |
| 92 (£1bn) | proposed `ab2026__package_ifs_hmrc_compliance_staff_and_debt_collection` | `ab2026__hmrc_tax_gap_package`, component | Table 6.3 rows 7 (debt management, +575m) and 8 (compliance officers, +415m), 990 in 2031–32: a part of line 45. |
| 91 (£1.1bn) | proposed `ab2026__package_ifs_savings_and_property_income_tax` | proposed `ab2026__package_property_and_savings_income_rates` | The name README rule 2 gives exactly lines 61 and 62. |
| 55–57 | proposed `ab2026__package_ifs_gas_standing_charge_reallocation` | proposed `ab2026__gas_standing_charge_moved_to_unit_rates` | We give a measure with no Table 6.1 line `ab2026__<slug>`; the RF family's spelling. |
| 61 (£1.2bn per year) | proposed `ab2026__package_ifs_defence_investment_plan_funding` | dropped | See below. |

**Defence Investment Plan funding.** The addendum asked whether IFS's "£1.2bn per year gap in Defence Investment Plan funding" gives an estimate (keep, as context) or not. In its own note the first lane calls it the government's DIP funding announcement, restated: the Budget "filled" the gap. That makes it a spending allocation, which rule 8 excludes, so we dropped it rather than keep it as context. It comes close to, but doesn't equal, Table 6.1 line 41 (capital reallocation to fully fund the DIP: +1,100, +1,135, +1,180 in 2029-30 to 2031-32), so we don't key it there either.


## Rows from addendum sections 1 and 2

### The two pages (11 rows)

We cite each page's saved `<main>` text by line.

The initial response (rows 87 to 91):

- Line 16: £13 billion and £15 billion, `fiscal_headroom` in 2029–30 before and after the Budget's policy decisions (`policy_scenario` pre-measures and post-measures). IFS restates the OBR, which the sentence names. In the OBR family we stage £12.5 billion and £14.5 billion against the target "Current budget to be in surplus by 2029-30" (uk_obr_tables); here we keep the page's rounded figures.
- Line 18: £8 billion and £4 billion, `decisions_effect_on_borrowing` in 2026-27 and 2027-28 (this year and next at the 28 October Budget), under `ab2026__package_ifs_new_giveaways` above. We infer the OBR attribution from the rounded match to Table 3.1, so we give both rows medium confidence.
- Line 28: 80%, `affected_share` 0.8: IFS's estimate of the share of households in England that receive the £100 payment. We key it to `ab2026__household_energy_payment_100_bands_a_to_d` and keep the £100 in `reform_hint`.

The opening remarks (rows 92 to 97; the saved text puts the whole speech on line 6):

- 98: proposed metric `measure_count` in proposed unit `measures`, `measure_key` null, no proposed key. Miller counts the Budget's measures, and we stage the count as we stage such counts in the AB2025 and AB2026 uk_thinktank_misc families (`own`, `different_model`). HM Treasury numbers Table 6.1's lines 1 to 98 (`data/uk/ab2026_measures.json`).
- £17 billion: proposed metric `spending_pressure`, IFS's estimate of the top-up that avoiding real-terms cuts could need. IFS prints its year as "2030-21", a typo, most likely for 2030–31. We keep "2030-21" in the quote and `conditions.horizon`, set no `fy`, use 2026 as a publication-year marker and give the row medium confidence.
- £11 billion: `spending_pressure` for defence plans, on top of the £17 billion. IFS prints no year on the page; on Boileau slide 4 it prints £11 billion more defence spending in 2030–31 (row 55). We give the row medium confidence and a 2026 marker.
- 25% and 40%: proposed metric `reserve_allocated_share`, the shares of the capital and day-to-day reserves already spent, restated `administrative_fact`. IFS names a source neither in the remarks nor on Boileau slide 11, which prints the same two shares. So in all four rows we infer the restated attribution and give medium confidence.
- 80%: `affected_share` 0.8 of households, for the £100 payment through council tax bands A-D, keyed to `ab2026__household_energy_payment_100_bands_a_to_d`.

### The seven visualisations (46 rows)

In `.ab2026-primaries/uk_ifs_ab2026/browser/data-items.json` we list the seven data items in the collection's key charts, each with its Flourish id and lead sentence. We read each chart's data cells from its public embed (see "Access recipe and primary inventory"). Following the addendum, we stage the October 2026 forecast values, and the March 2026 values where a chart compares the two. We mark them restated OBR figures unless IFS computed them, and mark IFS's own calculations `own`. We leave outturns unstaged unless a lead states one as its finding.

| Flourish id | Rows | Metric and unit | What we stage | Attribution |
|---|--:|---|---|---|
| 30734907 | 5 | `real_household_disposable_income_index` (proposed), `index` (proposed) | the 2020s forecast path, years 6 to 10 of the decade, read as 2026 to 2030; the lead's finding is the year-10 value | `own`: IFS builds the decade index from OBR and ONS data, and the addendum classes this chart as own |
| 30726471 | 11 | `current_budget_deficit` (proposed), `gbp` | the October 2026 forecast for 2026-27 to 2031-32 and the March 2026 forecast for 2026-27 to 2030-31 | `restated` OBR |
| 30726788 | 2 | `fiscal_headroom`, `share` | headroom at the March 2026 and October 2026 forecasts, as fractions of GDP | `restated` OBR |
| 30726917 | 11 | `real_gdp_index` (proposed), `index` (proposed) | the March 2026 forecast for 2026-27 to 2030-31 and the October 2026 forecast for 2026-27 to 2031-32, with 2025-26 = 100 | `restated` OBR; the addendum classes this chart as restated |
| 30726939 | 1 | `real_income_growth`, `percent` | 0.4% a year over the 2024-2029 parliament | `own`: the footer credits IFS calculations |
| 30726047 | 1 | `revenue_change`, `percent` | Budget 2026's tax change at the forecast horizon, 0.2% of GDP, with `ab2026__package_ifs_announced_tax_changes` above | `own`: the footer credits IFS calculations |
| 30727239 | 15 | `taxpayer_count`, `persons` | the three forecast series (the freeze at the March and October 2026 forecasts, and CPI uprating at the October forecast), 2026-27 to 2030-31 | `restated` OBR: the footer cites the OBR EFO, October 2026 |

We key only the tax-change row. The other 45 give forecast levels or IFS indicators, not the effect of one measure, so we give them `measure_key` null and no proposed key.

### Conventions for these rows

- **Quotes and locators.** We quote each Flourish row as "row, series: value", and name the visualisation, the data row and the series in its locator. We take `value_raw` as the cell the embed serves, at full precision, whatever the chart displays.
- **Units.**
  - IFS titles the deficit chart's y-axis "£ billion", so we scale its cells by 1e9 to GBP.
  - IFS gives the taxpayer chart's cells in thousands: the lead's 10.8 million equals the 2030-31 October freeze cell, 10800, and the chart's number format sets a constant of 1000. We scale them by 1,000 to persons.
  - IFS gives the headroom cells as fractions of GDP, which we stage as served in unit `share`; the chart's number format sets a constant of 100, one decimal place and a % suffix.
  - We keep index levels in the proposed unit `index`, not the registered `index_0_1`.
  - IFS gives the parliament and tax-change cells as percentages: the number format adds a % suffix, and the tax column's name says "% of GDP".
- **Periods.**
  - We give fiscal-year rows the end year and `conditions.fy`.
  - IFS labels the decade chart's rows "Year of decade" 0 to 10. We read years 6 to 10 of the 2020s as calendar 2026 to 2030, which IFS doesn't print, so we give those rows medium confidence.
  - We stage the headroom and tax-change cells as fiscal-event snapshots (`point_in_time`, period 2026).
  - We put the parliament average at the parliament's end year, 2029, and keep 2024-2029 in `conditions.horizon`.
  - For text rows with no printed year we use 2026 as a disclosed publication-year marker, and import no year from the decks.
- **Vintages.** We set `conditions.forecast_vintage` from the series or row label, March 2026 or October 2026. IFS names the OBR's October 2026 EFO in the decade chart's footer, and OBR forecasts in the parliament chart's lead, so we set those rows to October 2026.
- **Signs.** We stage cells as served. A negative deficit cell gives a surplus; IFS shades the area below zero "Current budget surplus".
- **Sources.** We give restated OBR rows `source_model: obr_efo_forecast` and `benchmark_class: different_model`, and IFS's own calculations `arithmetic`. We mark the two reserve shares `administrative_fact`, as in the Boileau rows.

## Not staged (rules 8 and 9)

### Deck rows the addendum dropped

Under the addendum we dropped 19 of the first lane's 106 rows, all under rule 8:

| Category | Rows | Examples (deck, slide) |
|---|--:|---|
| Measure parameters: rates, payment amounts, thresholds, a fare cap | 10 | £100 Household Energy Payment (Wernham 3); 5p fuel duty cut (Wernham 3); 0% VAT on electricity (Wernham 3, Adam 5); £2 bus fare cap (Wernham 15); Founders' Relief 10% rate, 24% comparator and £10m limit (Adam 3); RHL rateable values £12,000 and £21,000 (Adam 4) |
| Government targets | 3 | defence at 3% of GDP by 2030 (Boileau 4, repeated on 8); the DIP's earlier 2.7% in 2029–30 (Boileau 4) |
| Inputs of IFS's own spending scenarios | 2 | defence held at 2.7% of GDP, or at 3% by 2030–31 (Boileau 7 and 9); the scenarios' computed growth rates stay |
| Financing and allocations | 2 | ~£1bn a year of NWF and BBB financing for defence (Boileau 5); the £1.2bn a year of DIP funding (Boileau 4) |
| The base a measure moves | 2 | the £108 average gas standing charge and its 13% share of a typical gas bill (Wernham 8), as the red book dropped its £108 |

We keep each dropped parameter that names a measure in the kept rows' `reform_hint`. We keep the 25% capital and 40% day-to-day reserve shares (Boileau 11), because the addendum lists them as estimates. We keep the bond spread and debt-ownership context rows (Stockton 7) as context, since they aren't design.

### Figures on the two pages (11)

| Page | Figure | Times printed | Why the rows leave it out |
|---|---|--:|---|
| Initial response | 3% of GDP on defence by 2030 | 2 | a government target (rule 8) |
| Initial response | the £100 payment | 1 | a measure parameter (rule 8); row 91's `reform_hint` keeps it |
| Opening remarks | 3% of GDP on defence | 3 | a government target |
| Opening remarks | 3.5% by 2035 | 1 | a government target |
| Opening remarks | 2.7% of GDP from next year to 2029–30 | 1 | the government's defence spending plan, a target |
| Opening remarks | the £100 payment | 1 | a measure parameter; row 97's `reform_hint` keeps it |
| Opening remarks | property values 35 years out of date | 1 | it describes council tax valuations and estimates no Budget effect |
| Opening remarks | local areas to retain 100% of business rates | 1 | the design of a devolution plan (rule 8) |

We don't count the pages' other numbers as figures to stage:
- publication dates, titles and target dates (2030, 2035);
- horizons ("next five years", and "next three years", which we keep in row 95's `conditions.horizon`);
- the fiscal rule's year, 2029–30, which we record as `fy` on the headroom rows;
- "2030-21", which we keep in row 93;
- the name of the "10 year plan"; the G7; the count of "two big problems"; and "one-off".

Miller's "almost halved" prints no number, and we turn it into none.

### Data cells in the seven visualisations (256 of 302)

| Flourish id | Non-null cells | Staged | Excluded | The excluded cells |
|---|--:|--:|--:|---|
| 30734907 | 89 | 5 | 84 | the 1950s to 2010s paths (77, including seven base-100 cells); the 2020s series, years 0 to 5 (6, including its base-100 cell), which the chart does not mark as forecast; and the forecast series' year-5 cell (1), which repeats the 2020s series' year-5 value where the two lines meet |
| 30726471 | 13 | 11 | 2 | 2025-26 in both series, 47.4 each: a year that had ended before the October forecast, with one value for both series. The March series has no 2031-32 cell |
| 30726788 | 32 | 2 | 30 | headroom at the 30 earlier fiscal events, Jun 10 to Nov 25 |
| 30726917 | 13 | 11 | 2 | the 2025-26 base cells, 100 in both series. The March series has no 2031-32 cell |
| 30726939 | 12 | 1 | 11 | the 11 earlier parliaments, 1979-1983 to 2019-2024 |
| 30726047 | 85 | 1 | 84 | every earlier fiscal event, Budget 1971 to Spring Forecast 2026; one further data row is blank |
| 30727239 | 58 | 15 | 43 | the Current plans series, 1990-91 to 2025-26 (36); the two freeze series' 2025-26 cells (2), each 8510, the Current plans value for that year; and the CPI-uprating series for 2021-22 to 2025-26 (5), a counterfactual path for the years before the forecast years, whose 2021-22 cell equals Current plans' 4950 |
| **Total** | **302** | **46** | **256** | |

Outside the data cells, IFS draws a reference line on the headroom chart labelled with the 2010s average headroom, 0.9% of GDP: a historical average, which we don't stage. The lead sentences in `data-items.json` belong to no manifested primary. Each estimate a lead states repeats a staged cell (0.4% a year in row 127, around 0.2% of GDP in row 128, 10.8 million in row 142), and its other numbers give dates. IFS defines index bases in the axis titles, and apart from the labelled 0.9% line, adds no estimate in any tick or guide. We read no value off an image, a bar, a line or a tick.

## Unreached

We couldn't fetch two of the sources the addendum names, and two others gave us nothing to stage:

- **The seven IFS data-item pages.** ifs.org.uk refuses curl, and the addendum rules out any other route. So in each manifest line we name the data item's URL and hash the chart's public Flourish embed instead. We don't use the "Download data" link that each chart's footer template names.
- **The explainer and the fiscal devolution comment.** In the browser read of 29 October we found only an embedded video in the first and only design parameters in the second, so we gave neither a manifest line or rows.
- **The briefing event page** (https://ifs.org.uk/events/autumn-budget-2026-ifs-analysis). IFS's server refused the first lane's curl with a Cloudflare challenge (see below), and no primary holds it.

## Verification (3 November 2026)

- **Checker.** `PYTHONPATH=. python pipeline/ab2026_harvest_contract.py sources/harvest-uk-ab2026-2026-10-29/uk_ifs_ab2026` reports 144 rows, 0 problems.
- **Determinism.** Two runs of `stage.py` write the same gzip (sha256 `40331bc6beb36fc78d2e10731730c4c8a15942d4419bd840d0cebc95988e6125`), which COUNTS.json pins; the 87-row file before sections 1 and 2 hashed to `2e8b2dc5a85bb66fb11431f5c20565a40b2cf546e7edaabedd3a6c56ddb68d49`.
- **The 87 deck rows.** The new gzip's first 87 serialised lines match the 87-row file byte for byte (3,247 leaf fields, 0 differences), and manifest lines 1 to 5 match theirs.
- **Every new row.** We re-opened all 57 rows with a script at their locators: the saved text's line, or the embed's data row and series, decoding the embed afresh with every number kept as served text. The script checked the primary's sha256 against the row and the manifest, the quote against the line or cell, `value_raw` against the cell, and the value, sign, unit, period and forecast vintage. All 57 pass. We planted nine errors (value, sign, period, `fy`, series, unit, vintage, quote and hash), and each made it fail.
- **Cell accounting.** The same decoder lists every non-null cell in the seven embeds: 302, of which we stage 46.
- **Flourish bytes.** Our fetches on 29 October and 3 November returned byte-identical embeds.
- **Tests.** `PYTHONPATH=. python -m pytest -n 4 --noconftest tests/test_ab2026_harvest_contract.py tests/test_uk_ab2026_harvest.py`: 52 passed. `--noconftest` skips the conftest's build of the derived database, which neither file uses.
- **Generated files.** `pipeline/ab2026_proposed_keys.py` and `pipeline/harvest_counts.py --pinned-on 2026-10-29` regenerate PROPOSED_KEYS.md and COUNTS.json, and both `--check` runs pass.
- **After the review.** Commit f4c7c94a's fixes and README rule 10's move of row 76 changed no value, sign or year. COUNTS.json pins the gzip's current sha256, and `stage.py` still writes it byte for byte.

We keep the scripts and their outputs in the ignored `.ab2026-primaries/uk_ifs_ab2026/a3/`.

## Access recipe and primary inventory

### Decks (first lane, 29 October)

The first lane began fresh fetches at **2026-10-29 15:43:43 UTC**, with exactly:

```sh
curl -sSL -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15" URL
```

The lane also saved response headers and HTTP status, and set a 50-second
timeout. It saved the bytes under `.ab2026-primaries/uk_ifs_ab2026/`, outside the
vendored family, and checked SHA256s with `shasum -a 256`. It read the PDFs with
`pdftotext -layout` and rendered them for visual checks of labels and embedded
images. None of IFS's PDF annotations links to a chart-data download.

Stockton's fresh file matches the assigned `stockton.pdf` byte for byte,
which confirms it as **Weathering-the-fiscal-storm-IS.pdf**. The other three
current decks also match their supplied local copies. IFS's server returned HTTP
403 for TW_0, so the lane copied the supplied local PDF to `TW_0-local.pdf` and
hashed it. All rows from the cost-of-living presentation cite TW_1, not the
superseded version. We document the full TW_0/TW_1 changes below; IFS changed no
numerical claim.

### Browser text (the initial response and the opening remarks)

On 29 October, between 16:56Z and 16:58Z, we read the two pages in the Claude desktop app's built-in browser, as an ordinary page visit with no challenge solved. We fetched each page's HTML in-page with `fetch(location.href)` and hashed it. Two fetches of the initial response gave the same length, 257,037 bytes, with different hashes, because IFS embeds per-request tokens in the HTML. So we take the text of each page's `<main>` element as the primary, and record the HTML's byte count and one fetch's hash in each manifest note. IFS dates both pages 28 October 2026; the remarks give Helen Miller's opening remarks at the 29 October briefing.

### Flourish public data (the seven visualisations)

```sh
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
curl -sSL --max-time 50 -A "$UA" https://public.flourish.studio/visualisation/ID/   # names the embed URL
curl -sSL --max-time 50 -A "$UA" https://flo.uri.sh/visualisation/ID/embed          # the hashed primary
```

Both answered HTTP 200 for all seven ids on 3 November.
- Flourish serves each embed as an HTML page whose inline script assigns `_Flourish_data`, `_Flourish_data_column_names` and `_Flourish_settings` as JSON, and we read them with a JSON decoder from the assignment onward.
- Flourish stores `_Flourish_data_timestamps` as a JavaScript `new Date(...)`, which we parse separately.
- In each manifest note we give the data item's URL, the public page's bytes and hash, the embed URL, the fetch time, the Flourish version, the data's last update and the lead sentence from `data-items.json`.

### Inventory

| Primary | Access | Bytes | Rows | SHA256 |
|---|---|--:|--:|---|
| [Weathering the fiscal storm?](https://ifs.org.uk/system/files/2026-10/Weathering-the-fiscal-storm-IS.pdf) | direct | 318,348 | 39 | `fd09e707a4bc0a8e0a3de4a3fa902c8ccdc1e4c44ccdd0dee92866857aa4690b` |
| [Cost of living measures (TW_0, superseded)](https://ifs.org.uk/system/files/2026-10/Cost-of-living-measures-TW_0.pdf) | local copy | 231,180 | 0 | `abb63d9c4ecd21c3c9173077c5e92d8015c7cc30aebd12be159185d7d157f12a` |
| [Cost of living measures (TW_1, revised)](https://ifs.org.uk/system/files/2026-10/Cost-of-living-measures-TW_1.pdf) | direct | 222,191 | 15 | `6ed174b22b4d22a34c8bbd450194fb2b4181a9d566b137913bee52ca49a0299b` |
| [Spending on public services: the Achilles heel](https://ifs.org.uk/system/files/2026-10/Spending-on-public-services-the-Achilles-heel-BB.pdf) | direct | 157,838 | 21 | `7403ecc0641b23f5ffc0cb28f67435dbd1b8df6b124874ffae7ae7f75e357aa6` |
| [Tax measures](https://ifs.org.uk/system/files/2026-10/Tax-measures-SA.pdf) | direct | 133,005 | 12 | `6792dc448f40d34f174b6a3c839863b5c969a7334263f5d6b539be62a0428bb8` |
| [Autumn Budget 2026: initial response](https://ifs.org.uk/articles/autumn-budget-2026-initial-response) | browser text | 5,401 | 5 | `962f737e4dfb70416f76a7fc3104f9c4d6b04ef6566a58e0e55fd9db709136ff` |
| [Collection page: opening remarks by Helen Miller](https://ifs.org.uk/collections/autumn-budget-2026) | browser text | 12,403 | 6 | `5991ccec0e0ebb90952937f23400039a8386c047a4b44c9cd4391f535504723c` |
| [Flourish 30734907](https://flo.uri.sh/visualisation/30734907/embed) | Flourish public data | 912,453 | 5 | `99d8b19e36132340356adfcd9206cc26beb37484b3213cbfaa416dd39c9a8f9a` |
| [Flourish 30726471](https://flo.uri.sh/visualisation/30726471/embed) | Flourish public data | 909,632 | 11 | `db33c42dce0a78f12eef4c58497dbb9d2b3f0b3b304018fdf26f2052995f3618` |
| [Flourish 30726788](https://flo.uri.sh/visualisation/30726788/embed) | Flourish public data | 911,264 | 2 | `ce839de3a697429a34906b427d87f40ae9a9adccaf7b522a3b7d6d6bfb3bdf82` |
| [Flourish 30726917](https://flo.uri.sh/visualisation/30726917/embed) | Flourish public data | 909,037 | 11 | `a0a5eb60d2b40f76bbd78389bbb8ef3592ebee447e2746e6becc56c31fd60a5c` |
| [Flourish 30726939](https://flo.uri.sh/visualisation/30726939/embed) | Flourish public data | 909,837 | 1 | `96086a29b440505c6b4010e7844320b5d8179572c2f9d7585389b8a298a7d253` |
| [Flourish 30726047](https://flo.uri.sh/visualisation/30726047/embed) | Flourish public data | 920,130 | 1 | `3da8f416456fc61e99144bf23563bc553eefb8fa751251aa9e3cacc73af10c44` |
| [Flourish 30727239](https://flo.uri.sh/visualisation/30727239/embed) | Flourish public data | 912,450 | 15 | `b4303da3a3371585ab0c000a6f6419c07ae67391fd9c37efcdbc495a0f51ea6b` |

### HTML pages that refused curl

When the first lane ran curl at 15:43:43 UTC, these HTML pages answered with a Cloudflare challenge (HTTP 403). "Browser text" above and "Unreached" say what became of each:

- https://ifs.org.uk/articles/autumn-budget-2026-initial-response
- https://ifs.org.uk/articles/autumn-budget-2026-explained
- https://ifs.org.uk/collections/autumn-budget-2026
- https://ifs.org.uk/events/autumn-budget-2026-ifs-analysis

Nobody assigned local HTML copies, and the lane made no attempt to bypass the
blocks. We keep the challenge pages only as fetch evidence in the ignored
primaries directory; IFS didn't publish them, and we don't manifest them or stage
rows from them. We can't confirm the explainer's existence or content from its
challenge response. The blocked collection and event pages kept us from
discovering further AB2026 items or linked xlsx/csv downloads. We found no data
file inside the reachable PDFs; that reflects an access limit, not a finding that
IFS posted no data. We attempted no Wayback, alternative domain or other bypass.

## Proposed metrics and units

We list every proposed metric in the 144 rows.

| Proposed metric | Rows | Unit(s) | Where and what |
|---|--:|---|---|
| `average_energy_bill_change` | 1 | gbp | Wernham slide 2: EDF's forecast £470 rise in annual household energy prices |
| `average_household_support` | 4 | gbp | Wernham slide 4: nine-month cost-of-living support per household, £140 and the £24, £36 and £80 labels |
| `business_rates_bill_change` | 1 | gbp | Adam slide 4: the maximum annual bill saving, £7,146 in 2027-28 |
| `current_budget_deficit` | 15 | percent, gbp | Stockton slide 7, % of GDP (4); Flourish 30726471, £ (11) |
| `current_budget_deficit_revision_risk` | 1 | share | Stockton slide 8: roughly 1 in 4 revisions |
| `debt_interest_share_of_revenue` | 4 | percent | Stockton slide 7 |
| `debt_owned_by_non_residents_share` | 1 | percent | Stockton slide 7 |
| `gross_financing_requirement` | 4 | percent | Stockton slide 7 |
| `measure_count` | 1 | measures (proposed) | opening remarks: the Budget's 98 measures |
| `primary_deficit` | 4 | percent | Stockton slide 7 |
| `public_sector_net_borrowing` | 4 | percent | Stockton slide 7 |
| `public_sector_net_debt_ex_boe` | 4 | percent | Stockton slide 7 |
| `public_sector_net_debt_ex_boe_change` | 4 | percent | Stockton slide 7 |
| `public_sector_net_financial_liabilities_change` | 4 | percent | Stockton slide 7 |
| `public_sector_net_worth_inverted_change` | 4 | percent | Stockton slide 7 |
| `real_gdp_index` | 11 | index (proposed) | Flourish 30726917: real GDP, 2025-26 = 100 |
| `real_household_disposable_income_index` | 5 | index (proposed) | Flourish 30734907: real household disposable income, start of decade = 100 |
| `real_spending_growth` | 11 | percent | Boileau slides 7 and 9: average annual real-terms budget growth |
| `real_spending_growth_revision` | 1 | percentage_points | Boileau slide 10: the average revision to annual spending growth |
| `reserve_allocated_share` | 4 | percent | Boileau slide 11 (2) and the opening remarks (2): shares of the reserves already allocated |
| `share_of_energy_price_increase_offset` | 1 | share | Wernham slide 7: around 35% |
| `spending_pressure` | 9 | gbp | Boileau slides 3, 4, 7, 9 and 10 (7) and the opening remarks (2) |
| `taxpayer_gain` | 1 | gbp | Adam slide 3: the maximum Founders' Relief gain, £1.4m |
| `ten_year_bond_spread_other_g7` | 1 | percentage_points | Stockton slide 7: 134bp |

We propose the units `index` (16 rows, the two index charts) and `measures` (the measure count), and propose no baseline on any row. The first lane's rows proposed `affected_share` and `cpi_inflation_rate`, which the Metric registry lists. Since 4 November (review A's H-6(a)) we record them in `metric` on those four rows (Wernham slides 2 and 5), and use the registered `affected_share` in the new rows too. In the new rows we also use the registered metrics `taxpayer_count` (15), `fiscal_headroom` (4), `decisions_effect_on_borrowing` (2), `real_income_growth` (1) and `revenue_change` (1).

## Family conventions

- We give fiscal years their end year and `conditions.fy`. We give calendar
  years, cross-fiscal-year nine-month support and publication-date snapshots
  no `fy`, and disclose full horizons and missing dates. For Founders' Relief
  annual figures with no year, we use annual 2026 publication markers and
  medium confidence, not an inferred implementation year.
- We copy monetary magnitudes and signs verbatim and normalise £bn and £m to
  GBP. We keep percentage forecasts and rates in percent, and divide recipient
  shares by 100. We keep fiscal cells in percent of GDP or revenues as IFS
  prints them, rather than invent a real-GDP unit. We convert 134 basis points
  to 1.34 percentage points. We keep the proposed unit `pence_per_litre` for
  the fuel-duty parameter.
- We keep real/cash and price bases as IFS publishes them, and don't
  annualise nine-month household support. Where IFS prints a positive
  magnitude followed by “decrease”, we keep it positive and record the
  direction in conditions.
- We mark all figures `point`: we substitute no producer scenario for a
  central OBR estimate and invent no confidence band. We would use “Central”
  only for a forecast the producer labels central, and no staged figure has
  such a label.
- We use `arithmetic` for IFS calculations where the deck doesn't name
  TAXBEN. We mark official costings and forecasts `restated`, and name the
  original source in notes where IFS supplies it or we can infer it. We
  distinguish administrative policy parameters from IFS estimates. IFS doesn't
  cite PolicyEngine here.
- We leave the current-law/default baseline null and infer no new baseline
  world. We write every condition value as a string. We keep quotes under 15
  words; each contains the exact value_raw and comes from printed text, a data
  label or a numeric cell.

## Stockton fiscal deck

The first lane staged 39 rows: 38 printed numeric cells in slide 7's **Fiscal
traffic lights** image table, plus slide 8's “roughly 1 in 4 revisions” risk
annotation. Text extraction misses the whole image table, so the lane
transcribed every cell from the rendered slide and had it independently
audited. IFS's table spans FY2026-27, 2027-28, 2029-30 and 2031-32, and we
invented no missing intermediate years. IFS explicitly inverts net worth, and
we didn't reverse the signs. IFS divides debt interest by revenues, and gives
debt ownership as a share of total debt.

IFS cites no source in the table. We infer OBR attribution for the 36 forecast
cells from the surrounding OBR forecast slides rather than from an explicit
citation, so we give these rows medium confidence and disclose the inference.
IFS likewise names no original provider or observation date for debt
ownership. IFS gives the 134bp spread as a market comparison with other G7
economies, with unspecified source, weighting and date. We give these last two
a 2026 in-year snapshot. For the 1-in-4 risk IFS uses historical forecast
revisions since 2010, excluding 2020-21; we interpret “Spring” as Spring 2027
and disclose it. We give all fiscal rows a null measure_key and no proposed
measure.

The first lane didn't stage slides 3–6's forecast/borrowing bars, diamonds and
lines, or slide 8's forecast/outturn lines, because IFS prints no numeric data
labels on them. It staged no axis ticks, chart origins or dates as outcome rows,
and when it checked slides 1–6 by eye, it found no printed headroom or tax/GDP
number.

## Wernham cost-of-living deck

The first lane staged 21 Tom Wernham rows (15 after the 3 November addendum) from the revised 17-slide Cost of living measures deck, whose cover IFS dates 29 October 2026. We use source slug `ifs`. We use `arithmetic` for IFS's own household-price calculations (the deck doesn't name TAXBEN), `obr_efo_forecast` for OBR forecasts and `edf_energy_price_forecast` for EDF's energy-price forecast. The first lane gave announced statutory parameters `administrative_data`, restated attribution and an administrative_fact benchmark. The lane read no chart bars for values.

Access and version evidence:

- The lane freshly fetched TW_1 directly at 2026-10-29 15:43:43Z with the assigned Safari user agent: SHA256 `6ed174b22b4d22a34c8bbd450194fb2b4181a9d566b137913bee52ca49a0299b`, 222191 bytes. That hash matches the coordinator's local copy of the TW_1 PDF.
- IFS's server returned HTTP 403 for the fresh TW_0 URL. So the lane copied the assigned local file to `.ab2026-primaries/uk_ifs_ab2026/TW_0-local.pdf`, hashed it and extracted it with `pdftotext -layout`: SHA256 `abb63d9c4ecd21c3c9173077c5e92d8015c7cc30aebd12be159185d7d157f12a`, 231180 bytes. Its manifest access must read `local copy`. The lane attempted no bypass.
- Text diff:
  - IFS prints 18 pages in TW_0 and 17 in TW_1.
  - On TW_0 p4 IFS already includes the 80%/91% eligibility annotations, which TW_1 p4 omits.
  - On TW_0 p5 the eligibility annotations overlap the VAT/fuel commentary. On TW_1 p5 IFS moves eligibility to the lower chart and the VAT/fuel commentary to the upper chart.
  - IFS removed TW_0 p6, another copy of the unannotated support chart. TW_0 p7–18 correspond to TW_1 p6–17.
  - IFS changed no printed numerical claim. All staged rows cite TW_1. TW_0 gives zero rows, but we manifest it as the changed primary rule 7 requires.

The first lane gave 14 of its rows a null measure_key, 4 `ab2026__household_energy_payment_100_bands_a_to_d`, 2 `ab2026__fuel_duty_5p_cut_extended_and_rpi_rise_deferred` and 1 `ab2026__bus_fare_cap_2_england_outside_london_2027`. Of the null rows, it staged 6 as unscored context and gave 8 its proposed measure keys. It staged all 21 rows from TW_1 (TW_1=21, TW_0=0).

On 3 November we re-keyed the first lane's three Wernham proposals (see "Keys the addendum changed" above). The cost-of-living package covers exactly lines 1, 2 and 3, because line 2 costs the whole VAT cut, including the weeks before the Budget. We key the full-period VAT row to line 2, and the gas standing-charge rows to `ab2026__gas_standing_charge_moved_to_unit_rates`.

The first lane proposed these metrics and units. Under the 3 November addendum we dropped the rows on `benefit_payment_amount`, `fuel_duty_rate_cut`, `statutory_tax_rate`, `energy_standing_charge`, `energy_standing_charge_share` and `fare_cap` (rule 8).

- `cpi_inflation_rate`: IFS prints the OBR's 3.8% and 1.9% CPI forecast levels for Q1 2027, not inflation effects from measures.
- `average_energy_bill_change`: an existing AB2025 proposal; EDF's £470 annual energy-price increase from January 2027.
- `benefit_payment_amount`: the first lane proposed it for the £100 one-off payment per eligible household, not the average gain across all households.
- `fuel_duty_rate_cut`, proposed_unit `pence_per_litre`: IFS prints a 5p extension, and the first lane inserted no negative sign. It followed the named policy's per-litre basis, though IFS prints only 5p on the slide.
- `statutory_tax_rate`: the first lane proposed it for 0% electricity VAT during October 2026–June 2027, not an effective tax rate.
- `average_household_support`: nine-month cash support, including indirect tax reductions; we make no conversion to annual gains or household income changes. IFS prints the £140 headline and £24/£36/£80 all-household chart labels. At ingest we tally the £140, £24 and £36 as partial-year support. We score the £80 on `average_household_income_change`, because IFS averages January 2027's one-off Household Energy Payment across households in England and the whole payment falls in 2026-27.
- `affected_share`: an existing AB2025 proposal; payment receipt by 80% of all England households and 91% of the poorest 30%, normalised to 0.8 and 0.91 shares. IFS ranks households by spending, not income decile.
- `share_of_energy_price_increase_offset`: IFS's printed "around 35%" of forecast price increases covered by the three measures, normalised to a 0.35 share; we derive no ratio from bars.
- `energy_standing_charge`: the first lane staged the current annual gas standing charge of £108 on it as context.
- `energy_standing_charge_share`: the first lane staged the current 13% of a typical gas bill on it as context, normalised to a 0.13 share.
- `fare_cap`: the £2 single bus fare cap, a restated policy parameter. The first lane took the exact 2027 timing and England-outside-London scope from registered Table 6.1 line 4, and wrote in its row's note that IFS prints only "£2 cap on bus fares" on the slide.

Conventions:
- We keep GBP amounts as IFS prints them, in cash or 2026-27 prices as it specifies, and multiply the £5bn aggregate by 1e9.
- We divide printed percentages by 100 for shares, while keeping CPI percentages and the printed 1% income decrease as percentages.
- We record a positive cost as a cost to the Exchequer, and positive household support as a gain. We don't re-sign IFS's printed 1% decrease in real household disposable income, and state its direction in sign_convention.
- For October 2026–June 2027 figures we use the annual time_basis, end-period marker 2027 and horizon strings, and no fiscal-year condition, because the nine months cross fiscal years.
- IFS's 1% RHDI decrease spans FY2024-25 to FY2026-27, and we use FY2026-27/end 2027.
- We describe no row as central: IFS prints point estimates and parameters throughout.
- For the gas reform IFS prints no implementation year, so we use 2026 as a publication marker only.
- We leave the baseline null and invented no unsupported counterfactual definitions.

Not staged:

- IFS prints no data labels on the spending-decile bars in pp4–6, the energy-price bars/percentiles on pp7/16/17, the carbon implicit-tax bars on p9 or the real-income decade/forecast lines on pp11/14, apart from the separately staged £24/£36/£80 all-household labels and 1% annotation. The lane's visual inspection found no further printed values, embedded raster tables or hidden numeric labels.
- On slide 5 IFS repeats p4's £140/£24/£36/£80 chart values; we stage only its new 80%/91% annotations as further rows. We don't stage IFS's repeated £100 legend descriptions as extra rows.
- IFS says the richest 30% "lose a similar amount" without printing an exact cash number, and we inferred no negative £13.
- We treat the 30% subgroup labels, dates, axis ticks, years and 0% chart origins as conditions or context, not separate scored estimates. We stage no row with the 5–15 bus-travel age eligibility.
- IFS prints no cost or effect values for the other temporary announcements on p15 (food tariffs, family-days-out VAT, free bus travel), apart from the £2 bus fare parameter.
- IFS's "no give-away" and "does not change overall costs" for the gas-standing-charge reform are qualitative, and we invented no numerical zero. IFS prints no effect for its future electricity counterpart.
- The lane found no data download in the PDF, and IFS's server blocked the collection and event fetches, as documented above.

Potential contradictions and limits:
- IFS's modelled full electricity-VAT period for the package includes relief announced earlier, though IFS discusses it beside Budget measures, so the first lane gave the package and full-period electricity rows proposed scopes.
- IFS rounds the printed £140 headline; don't derive a different total from a plotted stack.
- IFS leaves the gas reform's implementation year and geography unspecified.
- IFS gives the positive 1% magnitude explicitly as a decrease.
- The lane detected no numerical difference between TW_0 and TW_1.

The lane drew a deterministic random sample, seed 230, of 10 of the 21 rows, and reopened each directly from the TW_1 PDF text. It also checked labels and direction against rendered pp4, 5, 7, 8 and 14. The one-based component rows 1, 6, 7, 8, 10, 11, 14, 15, 18 and 19 gave:
- p2 3.8% CPI in Q1 2027;
- p3 0% VAT October 2026–June 2027;
- p3 £5bn positive Exchequer cost across nine months;
- p4 £140 nine-month household support;
- p4 £36 VAT label;
- p4 £80 payment label (all in 2026-27 prices);
- p7 around 35% offset → 0.35;
- p8 current £108 annual gas charge;
- p8 40% worse off → 0.4 losing share;
- p8 poorest 30% gain £13 per year, date unspecified/publication marker 2026.

The lane found all values verbatim. The 21 component rows pass row_problems with 0 problems using UV_CACHE_DIR=/tmp/ab2026-ifs-uv-cache (the default uv cache lies outside the sandbox).


## Bee Boileau public services deck

Primary: *Spending on public services: the Achilles’ heel?*, 29 October 2026,
https://ifs.org.uk/system/files/2026-10/Spending-on-public-services-the-Achilles-heel-BB.pdf.
The lane fetched it fresh and directly at 2026-10-29 15:43:43Z with the required
Safari User-Agent: 157,838 bytes, sha256
`7403ecc0641b23f5ffc0cb28f67435dbd1b8df6b124874ffae7ae7f75e357aa6`. The
fresh copy matches the coordinator's assigned local copy byte for byte. The
lane read it with `pdftotext -layout` and visually inspected all 13 slides and
the slide 7/9 data labels. It missed no raster-only numeric table.

The first lane staged 28 rows (21 after the 3 November addendum), all
`measure_key: null` (one with the proposed package below). By slide: 3:1, 4:4, 5:1, 7:6, 8:1, 9:10, 10:3, 11:2.
IFS gives 21 own arithmetic calculations or scenario assumptions and 7 restated
announced policy, target or reserve figures. The first lane assigned no exact
registered AB2026 measure.

The first lane's one proposed key here, for the £1.2bn a year of DIP funding, went with that row, which we dropped under the addendum as an allocation (see "Keys the addendum changed" above). Our rule 8 drops also removed slide 4's and 8's targets, slide 5's financing and the two scenario inputs on slides 7 and 9, so the deck now gives 21 rows.

For metrics the first lane reused `spending_pressure`, `forecast_spending_change`
and `real_spending_growth` from AB2025, and used `real_spending_growth_revision`
for the historical one-percentage-point revision. It proposed the new
`reserve_allocated_share` for the percentage of the specified day-to-day or
capital reserve already allocated over its printed multi-year window, and
proposed no new unit or baseline. Under the 3 November addendum we kept 21 of
the deck's rows (rows 54–74). We stage them under the proposed metrics
`real_spending_growth` (11 rows), `spending_pressure` (7),
`reserve_allocated_share` (2) and `real_spending_growth_revision` (1), and none
under `forecast_spending_change`.

The first lane used `arithmetic` for IFS's own scenario and growth calculations,
or for an announced target IFS restates without naming a model. It marked the
£1.2bn funding amount restated, with `hmt_costing_obr_certified`, and in `note`
named each restated row's government/DIP origin. It marked the two announced
reserve allocation shares `administrative_fact`, with medium confidence, since
IFS names no source for them on the slide. It kept real growth in percent,
growth revisions in percentage points and cash amounts in GBP, with signs as
printed, and recorded additional spending required as positive pressure and a
real cut as negative growth. It staged no central-value rows: IFS gives its scenarios
as point estimates, and the lane never substituted them for OBR forecasts.

IFS gives the 2027–28 to 2030–31 chart rates as average annual real growth over
the whole interval. The first lane kept that interval in `growth_period` and
set the row's fiscal period to its terminal year, 2031. It likewise kept the
reserve shares' complete allocation windows, ending 2028–29 and 2029–30
respectively. IFS gives no fiscal year for the published £1.2bn and ~£1bn annual
flows, so the lane gave them a 2026 publication-date snapshot,
`time_basis: point_in_time`, `reference_date` and medium confidence, without
claiming them as 2026 annual outlays. It treated IFS's historical average
1-percentage-point growth revision since 2010 the same way. On slide 4 IFS
states a calendar-2030 defence target, so the first lane gave that row no fy; on
slide 9 IFS says 2030–31 explicitly, and the lane recorded that row as fiscal.
It kept the difference in date labels and didn't resolve it.

The first lane didn't stage slide 3's unlabelled growth bars and axis ticks;
all dates, document address numbers and slide enumeration; qualitative or
unquantified claims; or the second occurrence of the identical 3%-of-GDP
scenario annotation within slide 9. It kept slide 7's and slide 9's repeated
printed labels at their separate locators, and staged slide 9's two health bars
as separate scenario observations. IFS describes the £1bn financing flow
explicitly as investment or financing, not military purchases, and the lane
followed the slide's caution. IFS identifies no downloadable data file or
distributional chart in the deck, and the lane reached every public-services
primary.

`row_problems` from the AB2026 checker, with registered keys and
enums, reported **28 rows, 0 row problems**. We record full-family validation
below. In a full visual pass the lane found no contradictory value, and counted
the calendar/fiscal defence target wording and the unspecified flow years above
as material limitations.

The lane's deterministic random spot-check (seed 230, 1-based indices within the Boileau component):

| Row | Locator | Printed value | Normalized unit/value | Period check |
|---|---|---|---|---|
| 1 | slide 3 | £8 billion | GBP 8,000,000,000 | FY2030–31 |
| 6 | slide 5 | ~£1bn per year | GBP 1,000,000,000 | no year printed; dated snapshot, medium |
| 10 | slide 7 | 1.7% | percent 1.7 | average 2027–28 to 2030–31 |
| 14 | slide 9 | 0.9% | percent 0.9 | average 2027–28 to 2030–31 |
| 16 | slide 9 | £9 billion | GBP 9,000,000,000 | interval ends FY2030–31 |
| 18 | slide 9 | 2.7% | percent 2.7 | yellow health bar, average interval |
| 22 | slide 9 | -0.9% | percent -0.9 | green other-departments bar, average interval |
| 23 | slide 9 | -2.1% | percent -2.1 | yellow other-departments bar, average interval |
| 24 | slide 10 | £28 billion | GBP 28,000,000,000 | FY2030–31 |
| 25 | slide 10 | 1 percentage point | percentage_points 1 | historic since 2010, dated snapshot |

For every sampled row the lane reopened the primary PDF with `pdftotext -f/-l`
and checked the number or string, sign, unit and context; it also viewed slide
7/9 labels at full-page resolution. All printed value strings matched. The lane
used no bar reading and no arithmetic of its own.


## Stuart Adam: Tax measures

The first lane staged 18 rows (12 after the 3 November addendum) from one six-slide PDF. It fetched the PDF
directly with the required browser User-Agent at 2026-10-29 15:43:43Z: 133,005
bytes, sha256 `6792dc448f40d34f174b6a3c839863b5c969a7334263f5d6b539be62a0428bb8`.
The fetched bytes match the assignment's local copy. The lane read the text with
`pdftotext -layout`, and rendered and read all six slides as a safeguard against
raster text. IFS embeds no raster images on slides 2–6, and the lane's text extraction
captured every printed number. IFS links no distributional chart or data download
inside this deck.

The first lane keyed its 18 rows: `ab2026__package_total_tax_policy_decisions` 1;
`ab2026__writing_down_allowance_12pc_and_fya_50pc` 1;
`ab2026__distributions_framework_modernised` 1;
`ab2026__badr_lifetime_limit_500000` 1;
`ab2026__founders_relief_cgt` 6;
`ab2026__business_rates_sbrr_rhl_thresholds_raised` 3;
`ab2026__electricity_vat_zero_rate_to_july_2027` 1; null 4.
We now key the 12 rows we stage (rows 75–86) to `ab2026__founders_relief_cgt` 4;
`ab2026__hmrc_tax_gap_package` 2;
`ab2026__package_property_and_savings_income_rates` 1;
`ab2026__package_total_tax_policy_decisions` 1;
`ab2026__writing_down_allowance_12pc_and_fya_50pc` 1;
`ab2026__distributions_framework_modernised` 1;
`ab2026__badr_lifetime_limit_500000` 1; and
`ab2026__business_rates_sbrr_rhl_thresholds_raised` 1.
Since 3 November we put the £7bn net tax rise, Table 6.1's total of tax policy decisions, on `decisions_effect_on_borrowing` (README rule 10).

### Proposed measure scopes

We superseded these on 3 November (see "Keys the addendum changed" above). We stage the self-assessment timing and the compliance-staff and debt-collection figures as line 45 components, matched to Table 6.3's items by value, and the savings and property income figure on `ab2026__package_property_and_savings_income_rates`. Under rule 8 we dropped this deck's six parameter rows (the Founders' Relief rate, comparator and limit, the RHL rateable values and the 0% VAT rate), so it now gives 12 rows.

### Conventions and metric proposals

The first lane kept printed signs on all monetary figures. It staged
revenue-raising amounts as positive yields, and the Founders' Relief £0.3bn as a
positive cost, labelled as such. It multiplied amounts in £bn/£m by 1e9/1e6,
kept tax rates in percent, and kept every quoted excerpt under 15 words,
containing its exact `value_raw`. Under the 3 November addendum we kept 12 of
these rows (rows 75–86) with these signs, scalings and quotes, among them row
82's Founders' Relief £0.3bn as a positive cost, and dropped every tax-rate row
(rule 8).

The first lane marked the HMT-certified Budget costings `restated` with
`source_model: hmt_costing_obr_certified`, and rates and eligibility parameters
`restated` announced-government design with `administrative_data`. IFS cites no
source for its beneficiary count or gain calculations, so the lane presented
them, and IFS's maximum business-rate saving, as IFS `own`, `arithmetic`. It
used `point` for printed single estimates and range endpoints for the
£12,000–£21,000 benefiting-property range, inferred no uncertainty range, and
labelled no row in this deck `central`.

- Reused `tax_threshold_level` (GBP): the £10m cap on qualifying Founders'
  Relief gains, and the lower and upper rateable-value bounds of the RHL
  properties that benefit from higher relief thresholds.
- Proposed `statutory_tax_rate` (percent): the statutory 10% Founders' Relief
  rate, its current 24% standard-rate comparator, and the temporary 0%
  electricity VAT rate. IFS gives statutory parameters here, not effective
  marginal rates.
- Proposed `taxpayer_gain` (GBP): the printed maximum £1.4m gain per
  Founders' Relief beneficiary, with the maximum recorded in conditions.
- Proposed `business_rates_bill_change` (GBP): the maximum annual bill saving
  to an RHL property from the higher relief thresholds, £7,146 in 2027-28;
  positive for a gain to the business.

The first lane gave fiscal-year impacts their end year. IFS omits the year in
the BADR £0.3bn bullet, so the lane took 2031–32 from the preceding slide's
final-year comparison and the adjacent Founders' Relief bullet, and gave that
row medium parse confidence with the inheritance explained. IFS prints no year
for the annual count of 600 beneficiaries or the average £500,000 gain. The lane
used an annual 2026 publication-year marker for them, with explicit
`period_assignment` and `horizon` conditions and medium confidence; the marker
doesn't claim the relief operated in 2026. It staged parameters with no year,
and the maximum £1.4m gain, at point-in-time 2026 as announcements, with no
fiscal-year condition, and proposed no baseline.

### Omissions and source issues

- IFS prints no effective marginal rates, distributions or unlabelled charts in
  this deck, and we infer no amounts from qualitative bullets.
- We treat dates and durations as descriptive scope, not numerical impact
  rows: the bank surcharge's 15-month period; two years of business-rate
  discounts; the 2029 revaluation; April 2028 income-tax revenue devolution.
  IFS prints no quantified spending or revenue amount on the devolution slide.
- IFS prints “28 October 2026” on the title slide, though the assignment
  describes the 29 October briefing and the PDF metadata show creation and
  modification on 29 October. We follow the printed cover for the publication
  date (2026-10-28).
- We keep IFS's £1.1bn combined savings/property yield verbatim. Table 6.1
  gives lines 61 and 62 final-year amounts of £455m and £590m, totalling
  £1.045bn. Different rounding or aggregation could explain IFS's displayed
  £1.1bn; we stage no correction or derivation.
- IFS's £1bn HMRC compliance/debt-collection figure covers less than line 45's
  full £3.160bn, and we don't treat it as a contradictory costing of the full
  package.

### Verification

The 18 individual rows pass `row_problems` from the harvest contract with zero
problems. The lane matched all 18 short quotes against whitespace-normalised
`pdftotext -layout` output and checked them visually on the rendered slides.
Its random spot-check, seed 230, selected the following ten local rows. It
reopened each at its slide and checked the exact value, sign, unit and period:

| Local row | Slide | Printed value | Sign/basis | Period |
|--:|--:|---|---|---|
| 1 | 2 | £7bn | positive Exchequer yield, GBP | 2031-32 |
| 6 | 2 | £0.8bn | positive Exchequer yield, GBP | 2031-32 |
| 7 | 3 | £0.3bn | positive Exchequer yield, GBP | inherited 2031-32, disclosed |
| 8 | 3 | £0.3bn | positive Exchequer cost, GBP | explicit 2031-32 |
| 10 | 3 | 24% | standard statutory rate, percent | 2026 context marker |
| 11 | 3 | £10m | qualifying gains cap, GBP | 2026 announcement marker |
| 13 | 3 | £1.4m | maximum positive taxpayer gain, GBP | 2026 announcement marker |
| 14 | 3 | £500,000 | average positive beneficiary gain, GBP | annual, year unspecified; 2026 marker disclosed |
| 15 | 4 | £12,000 | lower rateable-value bound, GBP | 2027-28 |
| 16 | 4 | £21,000 | upper rateable-value bound, GBP | 2027-28 |


## First lane's family verification (29 October 2026, 106 rows)

The lane ran the required command, with its uv cache confined to the ignored
family primaries directory, and it completed successfully:

```sh
UV_CACHE_DIR=.ab2026-primaries/uk_ifs_ab2026/uv-cache PYTHONPATH=. uv run -q python pipeline/ab2026_harvest_contract.py sources/harvest-uk-ab2026-2026-10-29/uk_ifs_ab2026
```

```text
sources/harvest-uk-ab2026-2026-10-29/uk_ifs_ab2026: 106 rows, 0 problems
```

When the lane re-ran `stage.py`, it produced the same gzip SHA256 before and after:
`4f0c9cd197d970486608ea093bf3822ae1d92fa56ebc4a2ac1fae3086430b1cb`.
The lane also matched 68 text-row value_raw strings at their exact PDF slide
locators. Sixty-five quotes match the whitespace-normalised extraction directly.
In pdftotext three Boileau chart annotations interleave with other columns, so
the lane confirmed them against rendered slides 7 and 9. It checked all 38
embedded fiscal-table cells independently by eye. Every quote runs under 15
words and contains value_raw.

For the final family random sample the lane used seed 230, ten of 106 rows,
one-based gzip indices. It reopened each primary at the locator and checked the
number, sign, unit and period. All ten passed; we disclose unspecified dates as
markers, not confirmed implementation dates.

| Row | Primary / locator | Value and sign | Normalized unit | Period checked |
|--:|---|---|---|---|
| 3 | Stockton, slide 7, current budget deficit | -0.4, surplus direction | percent of GDP | FY2029-30 / 2030 |
| 21 | Stockton, slide 7, PSND ex BoE year-on-year change | 3.4, positive change | percent of GDP as printed | FY2026-27 / 2027 |
| 39 | Stockton, slide 8, forecast risk annotation | roughly 1 in 4 | share 0.25 | Spring 2027 inference disclosed |
| 56 | Wernham, slide 8, gas reform winners | 60%, better off | share 0.60 | implementation unspecified; 2026 publication marker |
| 69 | Boileau, slide 7, Health and Social Care | 2.7%, positive real growth | percent | annual average FY2027-28 to FY2030-31 / 2031 |
| 85 | Boileau, slide 10, historical top-ups | 1 percentage point increase | percentage_points 1 | historical since 2010; 2026 snapshot |
| 87 | Boileau, slide 11, day-to-day reserve | 40%, already allocated | percent | FY2027-28 to FY2028-29 / 2029 |
| 91 | Adam, slide 2, business investment allowances | £1.1bn, positive yield | GBP 1,100,000,000 | FY2031-32 / 2032 |
| 93 | Adam, slide 2, HMRC staffing/debt collection | £1bn, positive yield | GBP 1,000,000,000 | FY2031-32 / 2032 |
| 106 | Adam, slide 5, electricity VAT | 0%, statutory rate | percent 0 | announcement at publication in 2026; no fy |

The lane reviewed the registered-key scope of every non-null row:

| Registered key suffix (all prefixed ab2026__) | Table 6.1 line | Printed scope checked |
|---|--:|---|
| household_energy_payment_100_bands_a_to_d | 1 | one-off payment and all-household mean/receipt estimates |
| fuel_duty_5p_cut_extended_and_rpi_rise_deferred | 3 | 5p cut/freeze extension and its Jan-Jun average support |
| bus_fare_cap_2_england_outside_london_2027 | 4 | £2 fare parameter; registry timing/geography explicitly sourced in note |
| founders_relief_cgt | 26 | relief costing, design, beneficiary count and gains |
| distributions_framework_modernised | 49 | reclassification of capital gains as dividends |
| badr_lifetime_limit_500000 | 60 | further cut to BADR |
| business_rates_sbrr_rhl_thresholds_raised | 13 | benefiting rateable-value range and maximum saving from threshold increase |
| writing_down_allowance_12pc_and_fya_50pc | 58 | business investment allowances |
| electricity_vat_zero_rate_to_july_2027 | 2 | Adam statutory zero-rate parameter, no full-period gain/cost attached |
| package_total_tax_policy_decisions | total | net Budget tax rise in final forecast year |

The first lane gave Wernham's full-period VAT *impact* a proposal because it
includes earlier relief; since 3 November we key it to line 2. Adam states the
zero-rate *parameter* directly for the measure and doesn't cost the full period.
The first lane gave all broader or unidentified packages a null measure_key with
proposals. It left these as IFS printed them: Adam's cover date, the
savings/property rounding, Boileau's calendar/fiscal target wording and undated
flows, Wernham's undated gas reform, and Stockton's uncited attribution.
