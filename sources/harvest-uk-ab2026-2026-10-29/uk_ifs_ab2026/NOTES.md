# uk_ifs_ab2026 — Institute for Fiscal Studies, Autumn Budget 2026

**Working files.** `stage.py`, which writes `claims_staged.jsonl.gz` and is the file meant wherever these notes say `stage.py`, lives on branch `uk/ab2026-harvest-staging` at `harvest-staging/ab2026/lanes/ifs/uk_ifs_ab2026/stage.py`; this branch carries only NOTES.md, `manifest.jsonl` and `claims_staged.jsonl.gz`. `stage.py` embeds every row, so it rebuilds the gzip with no network and no primary file. `.ab2026-primaries/uk_ifs_ab2026/` is the harvest's local primaries folder, which no commit carries: the repository holds no primary bytes. Fetch each deck from its `manifest.jsonl` URL, and each Flourish embed from the embed URL in its manifest note, and check its sha256. The two browser-text primaries are each page's `<main>` text as saved on 29 October; ifs.org.uk refuses curl and its HTML embeds per-request tokens, so only the saved texts match those two hashes.

**144 rows from 13 primaries.** `source: ifs`. The manifest lists 14 primaries: four current briefing decks, the superseded TW_0 deck (no rows), two IFS pages read as browser text, and the public data of seven Flourish visualisations. The first lane staged 106 rows from the decks on 29 October. On 3 November the harvest applied the IFS addendum (`briefs/ifs-addendum.md` on the staging branch). Its sections 3 and 4 cut the deck rows to 87, through an explicit block that follows the deck rows in `stage.py`. Its sections 1 and 2 then appended 57 rows in a second JSON block: 11 from the two pages and 46 from the seven visualisations. Attribution: 48 `own`, 96 `restated`. No primary mentions PolicyEngine. From "Family conventions" on, the sections keep the first lane's record of 29 October; where they differ from the sections above them, the sections above win.

## Review A fixes, 4 November 2026

Review A (PR #231, issue comment 6635870934) asked for three changes to this family. They sit in a block before `main()` in `stage.py`; its indices are 0-based, as review A cites them. The coordinator read Adam's deck (slide 2) and Wernham's (slide 3) for K-7(a) and K-7(e); this session re-opened no primary. No printed value, sign or year changed.

- **H-6(a):** rows 39 and 40 (`cpi_inflation_rate`) and 47 and 48 (`affected_share`) carry the registered metric in `metric`, with `proposed_metric` null.
- **K-7(a):** row 78 (£1.1bn, lines 61 and 62) keeps 2031-32 ("Biggest revenue-raisers in 2031–32") and adds `conditions.discrepancy`: "IFS prints £1.1bn for 2031-32, where Table 6.1 gives lines 61 and 62 a combined £1,045m."
- **K-7(e):** row 42 (£5bn): slide 3 gives it as the cost of the three measures "over next nine months", and Table 6.1 line 2 costs the whole VAT cut from 1 October 2026, so the re-key to lines 1–3 stands (£5,040m over 2026-27 and 2027-28). Its note says so, and it is `cumulative` with the time basis of RF's two-year totals: period 2028 (the final fiscal year), `fiscal_year`, no `fy`, and `conditions.horizon` naming both years.

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

Rows 0 to 86 come from the decks, by deck, slide and position. Rows 87 to 143 follow in read order: the initial response, the opening remarks, then the seven visualisations in the order above, each by data row and then series.

| measure_key | Rows | of which components (rule 9) | of which from sections 1 and 2 |
|---|--:|--:|--:|
| `null`, context (no proposed key) | 116 | 0 | 52 |
| `null` with a proposed key | 7 | 0 | 3 |
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

## Proposed measure keys

Four proposed keys name seven rows. README rule 2 sets their spelling, and each takes the producer's printed scope (rule 3).

- `ab2026__package_property_and_savings_income_rates` (1 row): exactly Table 6.1 lines 61 and 62, Adam slide 2's "Increased income tax on savings & property income", £1.1bn in 2031–32 (lines 61 and 62 print 455 + 590 = 1,045). Slide 2's list opens "Biggest revenue-raisers in 2031–32", so the year stands, and the row's `conditions.discrepancy` records the £55m gap (review A, K-7(a)).
- `ab2026__gas_standing_charge_moved_to_unit_rates` (3 rows): no Table 6.1 line. Wernham slide 8's "Shifting gas standing charge onto unit price": "This charge will be scrapped, but per-unit price will be increased to absorb this". The spelling is the RF family's.
- `ab2026__package_ifs_new_giveaways` (2 rows, from the initial response): IFS's new giveaways, which push up borrowing by £8 billion this year and £4 billion next. The page names no OBR line and doesn't say the giveaways cover every Government decision since March, so the rows don't take the key the OBR, HM Treasury red book and RF families share for those decisions. To the nearest billion they match the OBR's direct effects of Government decisions in EFO Table 3.1, 7.6 in 2026-27 and 3.5 in 2027-28 (uk_obr_tables). We infer from that match that IFS restates the OBR, so both rows have medium confidence. Neither the total effect including indirect effects (6.3 and 7.0) nor Table 6.1's total of policy decisions (7,595 and 2,475 £m, uk_hmt_tables) matches both years.
- `ab2026__package_ifs_announced_tax_changes` (1 row, from Flourish 30726047): the tax change that Budget 2026 announced, at the forecast horizon, as a share of GDP as forecast at the event. The chart's footer credits IFS calculations from the OBR's October 2026 EFO, policy measures database and historical official forecasts database. The chart lists no Table 6.1 line and names no OBR grouping, and one rounded figure cannot tie it to the scope of `ab2026__package_total_tax_policy_decisions` or of the OBR's tax decisions since March, so the row proposes a key in IFS's own terms.

## Keys the addendum changed (rules 3 and 9)

| Rows (first lane, 0-based) | Was | Now | Why |
|---|---|---|---|
| 45, 46, 52 (£5bn, £140, 35%) | proposed `ab2026__package_ifs_cost_of_living_support` | `ab2026__package_household_energy_vat_and_fuel_duty` | IFS's three measures are the energy payment, the whole electricity VAT cut and the fuel duty cut, exactly lines 1, 2 and 3 (README rule 3, corrected). Lines 1+2+3 print 5,040 over 2026-27 and 2027-28, IFS's £5bn. Since 4 November the £5bn row (0-based row 42) is `cumulative`, period 2028, `fiscal_year`, with the two years in `horizon`, as RF dates its two-year totals, and its note no longer says the scope differs from lines 1–3 (review A, K-7(e)). |
| 48 (£36) | proposed `ab2026__package_ifs_electricity_vat_oct_2026_june_2027` | `ab2026__electricity_vat_zero_rate_to_july_2027` | Line 2 costs the whole cut, 1 October 2026 to 1 July 2027, including the weeks before the Budget. |
| 89 (£1.8bn) | proposed `ab2026__package_ifs_self_assessment_payment_timing` | `ab2026__hmrc_tax_gap_package`, component | Table 6.3 row 3, "More timely payment" for Self Assessment, +1,815m in 2031–32: a part of line 45. |
| 92 (£1bn) | proposed `ab2026__package_ifs_hmrc_compliance_staff_and_debt_collection` | `ab2026__hmrc_tax_gap_package`, component | Table 6.3 rows 7 (debt management, +575m) and 8 (compliance officers, +415m), 990 in 2031–32: a part of line 45. |
| 91 (£1.1bn) | proposed `ab2026__package_ifs_savings_and_property_income_tax` | proposed `ab2026__package_property_and_savings_income_rates` | The name README rule 2 gives exactly lines 61 and 62. |
| 55–57 | proposed `ab2026__package_ifs_gas_standing_charge_reallocation` | proposed `ab2026__gas_standing_charge_moved_to_unit_rates` | A measure with no Table 6.1 line is `ab2026__<slug>`; the RF family's spelling. |
| 61 (£1.2bn per year) | proposed `ab2026__package_ifs_defence_investment_plan_funding` | dropped | See below. |

**Defence Investment Plan funding.** The addendum asked whether IFS's "£1.2bn per year gap in Defence Investment Plan funding" is an estimate (keep, as context) or not. The first lane's own note calls it the government's DIP funding announcement, restated: the Budget "filled" the gap. That makes it a spending allocation, which rule 8 excludes, so it is dropped rather than kept as context. It is close to, but not exactly, Table 6.1 line 41 (capital reallocation to fully fund the DIP: +1,100, +1,135, +1,180 in 2029-30 to 2031-32), so it is not keyed there either.


## Rows from addendum sections 1 and 2

### The two pages (11 rows)

The rows cite each page's saved `<main>` text by line.

The initial response (rows 87 to 91):

- Line 16: £13 billion and £15 billion, `fiscal_headroom` in 2029–30 before and after the Budget's policy decisions (`policy_scenario` pre-measures and post-measures). They restate the OBR, which the sentence names. The OBR family stages £12.5 billion and £14.5 billion against the target "Current budget to be in surplus by 2029-30" (uk_obr_tables); the rows keep the page's rounded figures.
- Line 18: £8 billion and £4 billion, `decisions_effect_on_borrowing` in 2026-27 and 2027-28 (this year and next at the 28 October Budget), under the proposed key above. We infer the OBR attribution from the rounded match to Table 3.1, so both rows have medium confidence.
- Line 28: 80%, `affected_share` 0.8. IFS's estimate of the share of households in England that receive the £100 payment, keyed to `ab2026__household_energy_payment_100_bands_a_to_d`; `reform_hint` keeps the £100.

The opening remarks (rows 92 to 97; the saved text holds the whole speech on line 6):

- 98: proposed metric `measure_count` in proposed unit `measures`, `measure_key` null, no proposed key. A count of the Budget's measures, staged as the AB2025 and AB2026 uk_thinktank_misc families stage such counts (`own`, `different_model`). Table 6.1 numbers its lines 1 to 98 (`data/uk/ab2026_measures.json`).
- £17 billion: proposed metric `spending_pressure`, IFS's estimate of the top-up that avoiding real-terms cuts could need. The page prints its year as "2030-21", a typo, most likely for 2030–31. The row keeps "2030-21" in the quote and `conditions.horizon`, sets no `fy`, takes 2026 as a publication-year marker, and has medium confidence.
- £11 billion: `spending_pressure` for defence plans, on top of the £17 billion. The page prints no year; Boileau slide 4 prints £11 billion more defence spending in 2030–31 (row 55). Medium confidence and a 2026 marker.
- 25% and 40%: proposed metric `reserve_allocated_share`, the shares of the capital and day-to-day reserves already spent, restated `administrative_fact`. Neither the remarks nor Boileau slide 11, which prints the same two shares, names a source, so all four rows infer the restated attribution and have medium confidence.
- 80%: `affected_share` 0.8 of households, for the £100 payment through council tax bands A-D, keyed to `ab2026__household_energy_payment_100_bands_a_to_d`.

### The seven visualisations (46 rows)

`.ab2026-primaries/uk_ifs_ab2026/browser/data-items.json` lists the seven data items in the collection's key charts, each with its Flourish id and lead sentence. The rows read each chart's data cells from its public embed (see "Access recipe and primary inventory"). Following the addendum, they stage the October 2026 forecast values, and the March 2026 values where a chart compares the two, as restated OBR figures unless IFS computed them; IFS's own calculations are `own`. Outturns stay unstaged unless a lead states one as its finding.

| Flourish id | Rows | Metric and unit | What the rows hold | Attribution |
|---|--:|---|---|---|
| 30734907 | 5 | `real_household_disposable_income_index` (proposed), `index` (proposed) | the 2020s forecast path, years 6 to 10 of the decade, read as 2026 to 2030; the lead's finding is the year-10 value | `own`: IFS builds the decade index from OBR and ONS data, and the addendum classes this chart as own |
| 30726471 | 11 | `current_budget_deficit` (proposed), `gbp` | the October 2026 forecast for 2026-27 to 2031-32 and the March 2026 forecast for 2026-27 to 2030-31 | `restated` OBR |
| 30726788 | 2 | `fiscal_headroom`, `share` | headroom at the March 2026 and October 2026 forecasts, as fractions of GDP | `restated` OBR |
| 30726917 | 11 | `real_gdp_index` (proposed), `index` (proposed) | the March 2026 forecast for 2026-27 to 2030-31 and the October 2026 forecast for 2026-27 to 2031-32, with 2025-26 = 100 | `restated` OBR; the addendum classes this chart as restated |
| 30726939 | 1 | `real_income_growth`, `percent` | 0.4% a year over the 2024-2029 parliament | `own`: the footer credits IFS calculations |
| 30726047 | 1 | `revenue_change`, `percent` | Budget 2026's tax change at the forecast horizon, 0.2% of GDP, with the proposed key above | `own`: the footer credits IFS calculations |
| 30727239 | 15 | `taxpayer_count`, `persons` | the three forecast series (the freeze at the March and October 2026 forecasts, and CPI uprating at the October forecast), 2026-27 to 2030-31 | `restated` OBR: the footer cites the OBR EFO, October 2026 |

Only the tax-change row carries a key. The other 45 hold forecast levels or IFS indicators, not the effect of one measure, so they have `measure_key` null and no proposed key.

### Conventions for these rows

- **Quotes and locators.** Each Flourish row quotes "row, series: value", and its locator names the visualisation, the data row and the series. `value_raw` is the cell as the embed serves it, at full precision, whatever the chart displays.
- **Units.** The deficit chart's y-axis title is "£ billion", so its cells scale by 1e9 to GBP. The taxpayer chart's cells are thousands: the lead's 10.8 million is the 2030-31 October freeze cell, 10800, and the chart's number format sets a constant of 1000. They scale by 1,000 to persons. The headroom cells are fractions of GDP, staged as served in unit `share`; the chart's number format sets a constant of 100, one decimal place and a % suffix. Index levels keep proposed unit `index`, not the registered `index_0_1`. The parliament and tax-change cells are percentages: the number format adds a % suffix, and the tax column's name says "% of GDP".
- **Periods.** Fiscal-year rows take the end year and `conditions.fy`. The decade chart labels its rows "Year of decade" 0 to 10; the rows read years 6 to 10 of the 2020s as calendar 2026 to 2030, which the chart does not print, so they have medium confidence. The headroom and tax-change cells are fiscal-event snapshots (`point_in_time`, period 2026). The parliament average takes the parliament's end year, 2029, and keeps 2024-2029 in `conditions.horizon`. Text rows with no printed year take 2026 as a disclosed publication-year marker and import no year from the decks.
- **Vintages.** `conditions.forecast_vintage` follows the series or row label, March 2026 or October 2026. The decade chart's footer names the OBR's October 2026 EFO, and the parliament chart's lead names OBR forecasts, so those rows read October 2026.
- **Signs.** As served. A negative deficit cell is a surplus; the chart shades the area below zero "Current budget surplus".
- **Sources.** Restated OBR rows carry `source_model: obr_efo_forecast` and `benchmark_class: different_model`; IFS's own calculations carry `arithmetic`. The two reserve shares are `administrative_fact`, as in the Boileau rows.

## Not staged (rules 8 and 9)

### Deck rows the addendum dropped

The addendum dropped 19 of the first lane's 106 rows, all under rule 8:

| Category | Rows | Examples (deck, slide) |
|---|--:|---|
| Measure parameters: rates, payment amounts, thresholds, a fare cap | 10 | £100 Household Energy Payment (Wernham 3); 5p fuel duty cut (Wernham 3); 0% VAT on electricity (Wernham 3, Adam 5); £2 bus fare cap (Wernham 15); Founders' Relief 10% rate, 24% comparator and £10m limit (Adam 3); RHL rateable values £12,000 and £21,000 (Adam 4) |
| Government targets | 3 | defence at 3% of GDP by 2030 (Boileau 4, repeated on 8); the DIP's earlier 2.7% in 2029–30 (Boileau 4) |
| Inputs of IFS's own spending scenarios | 2 | defence held at 2.7% of GDP, or at 3% by 2030–31 (Boileau 7 and 9); the scenarios' computed growth rates stay |
| Financing and allocations | 2 | ~£1bn a year of NWF and BBB financing for defence (Boileau 5); the £1.2bn a year of DIP funding (Boileau 4) |
| The base a measure moves | 2 | the £108 average gas standing charge and its 13% share of a typical gas bill (Wernham 8), as the red book dropped its £108 |

Each dropped parameter that names a measure stays in the kept rows' `reform_hint`. The 25% capital and 40% day-to-day reserve shares (Boileau 11) stay: the addendum lists them as estimates. The bond spread and debt-ownership context rows (Stockton 7) are not design and stay as context.

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

The pages' other numbers are not figures to stage: publication dates, titles and target dates (2030, 2035); horizons ("next five years", and "next three years", which row 95 keeps in `conditions.horizon`); the fiscal rule's year, 2029–30, which the headroom rows carry as `fy`; "2030-21", which row 93 keeps; the name of the "10 year plan"; the G7; the count of "two big problems"; and "one-off". The remarks' "almost halved" prints no number, and no row turns it into one.

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

Outside the data cells, the headroom chart draws a reference line labelled with the 2010s average headroom, 0.9% of GDP: a historical average, which no row stages. The lead sentences in `data-items.json` belong to no manifested primary. Each estimate a lead states repeats a staged cell (0.4% a year is row 127, around 0.2% of GDP is row 128, 10.8 million is row 142), and their other numbers are dates. Axis titles define index bases, and apart from the labelled 0.9% line, no tick or guide adds an estimate. No row reads a value off an image, a bar, a line or a tick.

## Unreached

We couldn't fetch two of the sources the addendum names, and two others held nothing to stage:

- **The seven IFS data-item pages.** ifs.org.uk refuses curl, and the addendum rules out any other route, so each manifest line names its data item's URL and hashes the chart's public Flourish embed instead. The rows do not use the "Download data" link that each chart's footer template names.
- **The explainer and the fiscal devolution comment.** The browser read of 29 October found only an embedded video in the first and only design parameters in the second, so neither has a manifest line or rows.
- **The briefing event page** (https://ifs.org.uk/events/autumn-budget-2026-ifs-analysis) refused the first lane's curl with a Cloudflare challenge (see below); no primary holds it.

## Verification (3 November 2026)

- **Checker:** `PYTHONPATH=. python pipeline/ab2026_harvest_contract.py sources/harvest-uk-ab2026-2026-10-29/uk_ifs_ab2026` reports 144 rows, 0 problems.
- **Determinism:** two runs of `stage.py` write the same gzip, sha256 `40331bc6beb36fc78d2e10731730c4c8a15942d4419bd840d0cebc95988e6125`. The 87-row file before sections 1 and 2 had `2e8b2dc5a85bb66fb11431f5c20565a40b2cf546e7edaabedd3a6c56ddb68d49`. COUNTS.json pins the new hash.
- **The 87 deck rows:** the new gzip's first 87 serialised lines match the 87-row file byte for byte (3,247 leaf fields, 0 differences), and manifest lines 1 to 5 match theirs.
- **Every new row:** a script re-opened all 57 rows at their locators: the saved text's line, or the embed's data row and series, decoding the embed afresh with every number kept as served text. It checked the primary's sha256 against the row and the manifest, the quote against the line or cell, `value_raw` against the cell, and the value, sign, unit, period and forecast vintage. All 57 pass. Nine planted errors (value, sign, period, `fy`, series, unit, vintage, quote and hash) each made it fail.
- **Cell accounting:** the same decoder lists every non-null cell in the seven embeds: 302, of which the rows stage 46.
- **Flourish bytes:** fetches on 29 October and 3 November returned byte-identical embeds.
- **Tests:** `PYTHONPATH=. python -m pytest -n 4 --noconftest tests/test_ab2026_harvest_contract.py tests/test_uk_ab2026_harvest.py`: 52 passed. `--noconftest` skips the conftest's build of the derived database, which neither file uses.
- **Generated files:** `pipeline/ab2026_proposed_keys.py` and `pipeline/harvest_counts.py --pinned-on 2026-10-29` regenerate PROPOSED_KEYS.md and COUNTS.json, and both `--check` runs pass.
- **After the review:** commit f4c7c94a's fixes and README rule 10's move of row 76 changed no value, sign or year. COUNTS.json pins the gzip's current sha256, and `stage.py` still writes it byte for byte.

The scripts and their outputs sit in the ignored `.ab2026-primaries/uk_ifs_ab2026/a3/`.

## Access recipe and primary inventory

### Decks (first lane, 29 October)

Fresh fetches began **2026-10-29 15:43:43 UTC**, using exactly:

```sh
curl -sSL -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15" URL
```

The fetch also saved response headers and HTTP status and imposed a 50-second
timeout. Bytes are under `.ab2026-primaries/uk_ifs_ab2026/`, outside the vendored
family. SHA256s were checked with `shasum -a 256`. PDFs were read with
`pdftotext -layout` and rendered for visual checks of labels and embedded images.
None of the PDF annotations links to a chart-data download.

Stockton's fresh file is byte-for-byte identical to assigned `stockton.pdf`,
confirming it is **Weathering-the-fiscal-storm-IS.pdf**. The other three current
decks also match their supplied local copies. TW_0 returned HTTP 403; the
supplied local PDF was copied to `TW_0-local.pdf` and hashed. All rows from the
cost-of-living presentation cite TW_1, not the superseded version. Full TW_0/TW_1
changes are documented below; no numerical claim changed.

### Browser text (the initial response and the opening remarks)

On 29 October, between 16:56Z and 16:58Z, the harvest read the two pages in the Claude desktop app's built-in browser, as an ordinary page visit with no challenge solved. It fetched each page's HTML in-page with `fetch(location.href)` and hashed it. Two fetches of the initial response gave the same length, 257,037 bytes, with different hashes: the HTML embeds per-request tokens. So the primary is the text of each page's `<main>` element, and each manifest note records the HTML's byte count and one fetch's hash. Both pages print publication on 28 October 2026; the remarks are Helen Miller's opening remarks at the 29 October briefing.

### Flourish public data (the seven visualisations)

```sh
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
curl -sSL --max-time 50 -A "$UA" https://public.flourish.studio/visualisation/ID/   # names the embed URL
curl -sSL --max-time 50 -A "$UA" https://flo.uri.sh/visualisation/ID/embed          # the hashed primary
```

Both answered HTTP 200 for all seven ids on 3 November. Each embed is an HTML page whose inline script assigns `_Flourish_data`, `_Flourish_data_column_names` and `_Flourish_settings` as JSON; a JSON decoder reads them from the assignment onward. `_Flourish_data_timestamps` holds a JavaScript `new Date(...)`, which needs its own parse. Each manifest note gives the data item's URL, the public page's bytes and hash, the embed URL, the fetch time, the Flourish version, the data's last update and the lead sentence from `data-items.json`.

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

The first lane's record of the HTML pages that returned a Cloudflare challenge (HTTP 403) to its curl at 15:43:43 UTC; "Browser text" above and "Unreached" give what has become of each:

- https://ifs.org.uk/articles/autumn-budget-2026-initial-response
- https://ifs.org.uk/articles/autumn-budget-2026-explained
- https://ifs.org.uk/collections/autumn-budget-2026
- https://ifs.org.uk/events/autumn-budget-2026-ifs-analysis

No assigned local HTML copies exist. No attempt was made to bypass the blocks.
Challenge pages are retained only as fetch evidence in the ignored primaries
directory; they are not IFS publications and are not manifested. No rows are
staged from them. The explainer's existence/content cannot be confirmed from its
challenge response. The blocked collection and event pages prevent discovering
additional AB2026 items or linked xlsx/csv downloads. No data file was identified
inside the reachable PDFs; this is an access limit, not a finding that IFS posted
no data. No Wayback, alternative domain or other bypass was attempted.

## Proposed metrics and units

The table lists every proposed metric in the 144 rows.

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

The proposed units are `index` (16 rows, the two index charts) and `measures` (the measure count); no row proposes a baseline. The first lane's rows proposed `affected_share` and `cpi_inflation_rate`, which the Metric registry carries; since 4 November (review A's H-6(a)) those four rows (Wernham slides 2 and 5) carry them in `metric`, and the new rows use the registered `affected_share` too. The new rows also use the registered metrics `taxpayer_count` (15), `fiscal_headroom` (4), `decisions_effect_on_borrowing` (2), `real_income_growth` (1) and `revenue_change` (1).

## Family conventions

- Fiscal years use their end year and `conditions.fy`. Calendar years,
  cross-fiscal-year nine-month support, and publication-date snapshots have
  no `fy`; full horizons and missing dates are disclosed. Unspecified-year
  Founders' Relief annual figures use annual 2026 publication markers and
  medium confidence, not an inferred implementation year.
- Monetary magnitudes and signs are verbatim. £bn and £m are normalised to
  GBP. Percentage forecasts and rates stay percent; recipient shares divide
  by 100. Fiscal cells say percent of GDP or revenues as printed, rather
  than inventing a real-GDP unit. 134 basis points is 1.34 percentage points.
  The fuel-duty parameter keeps proposed unit `pence_per_litre`.
- Real/cash and price bases stay as published. Nine-month household support
  is not annualised. A printed positive magnitude followed by “decrease”
  remains positive, with the direction recorded in conditions.
- All figures are `point`: no producer scenario is substituted for a central
  OBR estimate and no confidence band is invented. “Central” would mean a
  producer-labelled central forecast; the staged figures contain no such label.
- `arithmetic` is used for IFS calculations where the deck does not name
  TAXBEN. Official costings/forecasts are `restated`, with original source
  named in notes where supplied or inferable; administrative policy parameters
  are distinguished from IFS estimates. IFS does not cite PolicyEngine here.
- Current-law/default baseline is null. No new baseline world is inferred.
  Every condition value is a string. Quotes are under 15 words, contain the
  exact value_raw, and refer to printed text, a data label or a numeric cell.

## Stockton fiscal deck

39 rows: 38 printed numeric cells in slide 7's **Fiscal traffic lights** image
table, plus slide 8's “roughly 1 in 4 revisions” risk annotation. Text extraction
misses the entire image table; all cells were transcribed from the rendered
slide and independently audited. The table spans FY2026-27, 2027-28, 2029-30 and
2031-32; missing intermediate years were not invented. Net worth is explicitly
inverted and the signs were not reversed. The debt-interest denominator is
revenues, while debt ownership is a share of total debt.

The table prints no source citation. OBR attribution for the 36 forecast cells
is inferred from the surrounding OBR forecast slides, not presented as an
explicit citation; these rows have medium confidence and disclose the inference.
Debt-ownership's administrative origin likewise has no named original provider
or observation date. The 134bp spread is an IFS market comparison with other
G7 economies whose source/weighting/date are unspecified. The latter two use a
2026 in-year snapshot. The 1-in-4 risk uses historical forecast revisions since
2010 excluding 2020-21; “Spring” is interpreted as Spring 2027 and disclosed.
All fiscal rows have null measure_key and no proposed measure.

Not staged: slides 3–6 forecast/borrowing bars, diamonds and lines, and slide 8's
forecast/outturn lines, because they have no numeric data labels. Axis ticks,
chart origins and dates are not outcome rows. Slides 1–6 were visually checked
for hidden printed numbers. No headroom or tax/GDP number is printed there.

## Wernham cost-of-living deck

Tom Wernham component: 21 rows from the revised 17-slide Cost of living measures deck, cover dated 29 October 2026. Source slug `ifs`; own household-price calculations use `arithmetic` (the deck does not name TAXBEN), OBR forecasts use `obr_efo_forecast`, EDF's energy-price forecast uses `edf_energy_price_forecast`, and announced statutory parameters use `administrative_data` with restated attribution and administrative_fact benchmark. No chart bars were read for values.

Access/version evidence:

- TW_1 freshly fetched directly at 2026-10-29 15:43:43Z using the assigned Safari user agent. SHA256 `6ed174b22b4d22a34c8bbd450194fb2b4181a9d566b137913bee52ca49a0299b`, 222191 bytes. This hash is identical to the coordinator's local copy of the TW_1 PDF.
- TW_0 fresh URL returned HTTP403, so the assigned local file was copied to `.ab2026-primaries/uk_ifs_ab2026/TW_0-local.pdf`, hashed, and extracted using `pdftotext -layout`. SHA256 `abb63d9c4ecd21c3c9173077c5e92d8015c7cc30aebd12be159185d7d157f12a`, 231180 bytes; manifest access must be `local copy`. No bypass was attempted.
- Text diff: TW_0 has18 pages, TW_1 has17. TW_0 p4 already includes the80%/91% eligibility annotations; TW_1 p4 omits these. TW_0 p5 has those eligibility annotations overlapping the VAT/fuel commentary. TW_1 p5 relocates eligibility to the lower chart and VAT/fuel commentary to the upper chart. TW_0 p6 is another copy of the unannotated support chart and was removed. TW_0 p7–18 correspond to TW_1 p6–17. No printed numerical claim changes. All staged rows cite TW_1; TW_0 contributes zero rows but is manifested as the changed primary required by rule7.

Coverage by measure_key: null14; `ab2026__household_energy_payment_100_bands_a_to_d`4; `ab2026__fuel_duty_5p_cut_extended_and_rpi_rise_deferred`2; `ab2026__bus_fare_cap_2_england_outside_london_2027`1. Within null: 6 unscored context rows; the remaining8 use proposed measure keys below. Rows per primary: TW_1=21, TW_0=0.

Proposed measure scopes: the first lane's three Wernham proposals were re-keyed on 3 November (see "Keys the addendum changed" above). The cost-of-living package is exactly lines 1, 2 and 3, because line 2 costs the whole VAT cut including the weeks before the Budget; the full-period VAT row is line 2; the gas standing-charge rows use `ab2026__gas_standing_charge_moved_to_unit_rates`.

Proposed metrics and units:

- `cpi_inflation_rate`: printed OBR3.8% and1.9% CPI forecast levels for Q12027, not inflation effects from measures.
- `average_energy_bill_change`: existing AB2025 proposal; EDF£470 annual energy-price increase from January2027.
- `benefit_payment_amount`: £100 per eligible household one-off payment, rather than the average gain across all households.
- `fuel_duty_rate_cut`, proposed_unit `pence_per_litre`: printed5p extension; no negative sign is inserted. Per-litre basis follows the named policy, though the slide prints only5p.
- `statutory_tax_rate`:0% electricity VAT during October2026–June2027, not an effective tax rate.
- `average_household_support`: nine-month cash support, including indirect tax reductions; no conversion to annual gains or household income changes. Printed£140 headline and £24/£36/£80 all-household chart labels.
- `affected_share`: existing AB2025 proposal, payment receipt by80% of all England households and91% of the poorest30%; normalized to0.8 and0.91 shares. Household ranking is by spending, not income decile.
- `share_of_energy_price_increase_offset`: the printed "around35%" of forecast price increases covered by the three measures; normalized to0.35 share, no ratio derived from bars.
- `energy_standing_charge`: current annual gas standing charge£108; context.
- `energy_standing_charge_share`: current13% of a typical gas bill; normalized to0.13 share, context.
- `fare_cap`: £2 single bus fare cap, a restated policy parameter. Exact2027 timing and England-outside-London scope follow registered Table6.1 line4; the slide itself gives only "£2 cap on bus fares", and the row explicitly says this.

Conventions: GBP amounts stay as printed in cash or2026-27 prices as specified; the £5bn aggregate is multiplied by1e9. Shares divide printed percentages by100, while CPI percentages and the printed1% income decrease remain percentages. Positive cost is cost to the Exchequer; positive household support is a gain. The printed1% decrease in real household disposable income is not re-signed; its direction is explicit in sign_convention. October2026–June2027 figures use annual time_basis, end-period marker2027 and horizon strings, with no fiscal-year condition because the nine months cross fiscal years. The1% RHDI decrease spansFY2024-25 toFY2026-27 and usesFY2026-27/end2027. No row is described as central: all figures are printed point estimates/parameters. For gas reform, year2026 is explicitly only a publication marker because no implementation year is printed. Baseline remains null; unsupported counterfactual definitions were not invented.

Not staged:

- Spending-decile bars in pp4–6, energy-price bars/percentiles pp7/16/17, carbon implicit-tax bars p9, and real-income decade/forecast lines pp11/14 have no data labels (apart from the separately staged£24/£36/£80 all-household labels and1% annotation). Visual inspection found no further printed values, embedded raster tables, or hidden numeric labels.
- Slide5 repeats p4's £140/£24/£36/£80 chart values; only its new80%/91% annotations are additional rows. Repeated£100 legend descriptions are not extra rows.
- Richest30% "lose a similar amount" is not an exact printed cash number; no negative£13 was inferred.
-30% subgroup labels,5–15 bus-travel age eligibility, dates, axis ticks, years and0% chart origins are conditions/context, not separate scored estimates.
- Other temporary announcements on p15 (food tariffs, family-days-out VAT, free bus travel) have no printed cost/effect values, apart from the£2 bus fare parameter staged.
- Gas-standing-charge reform's average "no give-away" and "does not change overall costs" are qualitative; no numerical zero was invented. Its future electricity counterpart has no printed effect.
- No data download was identified within the PDF; the collection/event fetches were blocked as documented above.

Potential contradictions/limits: the package's modelled full electricity-VAT period includes already-announced relief, despite being discussed beside Budget measures. This is why the package and full-period electricity rows have proposed scopes. The printed£140 headline is rounded; do not derive a different total from a plotted stack. Gas reform has unspecified implementation year and geography. The positive1% magnitude is explicitly a decrease. No numerical difference was detected between TW_0 and TW_1.

Component spot check: deterministic random sample seed230,10 of21 rows, reopened directly from TW_1 PDF text; labels and direction were also checked against rendered pp4,5,7,8,14. One-based component rows1,6,7,8,10,11,14,15,18,19: p2 3.8% CPI inQ12027; p3 0% VAT October2026–June2027; p3 £5bn positive Exchequer cost across nine months; p4 £140 nine-month household support; p4 £36 VAT label; p4 £80 payment label (all in2026-27 prices); p7 around35% offset→0.35; p8 current£108 annual gas charge; p8 40% worse off→0.4 losing share; p8 poorest30% gain£13 per year, date unspecified/publication marker2026. All values found verbatim. The21 component rows pass row_problems with0 problems using UV_CACHE_DIR=/tmp/ab2026-ifs-uv-cache (default uv cache is outside the sandbox).


## Bee Boileau public services deck

Primary: *Spending on public services: the Achilles’ heel?*, 29 October 2026,
https://ifs.org.uk/system/files/2026-10/Spending-on-public-services-the-Achilles-heel-BB.pdf.
Fresh direct fetch 2026-10-29 15:43:43Z with the required Safari User-Agent;
157,838 bytes, sha256 `7403ecc0641b23f5ffc0cb28f67435dbd1b8df6b124874ffae7ae7f75e357aa6`.
The coordinator's assigned local copy and fresh copy are byte-identical. Read with
`pdftotext -layout`; visually inspected all 13 slides and the slide 7/9 data labels.
No raster-only numeric table was missed.

Coverage: 28 rows, all `measure_key: null` (one has the proposed package below).
By slide: 3:1, 4:4, 5:1, 7:6, 8:1, 9:10, 10:3, 11:2.
The figures are 21 own arithmetic calculations/scenario assumptions and 7 restated
announced policy/target/reserve figures. No exact registered AB2026 measure is assigned.

The first lane's one proposed key here, for the £1.2bn a year of DIP funding, went with that row, which the addendum dropped as an allocation (see "Keys the addendum changed" above). The rule 8 drops also removed slide 4's and 8's targets, slide 5's financing and the two scenario inputs on slides 7 and 9, so the deck now has 21 rows.

Metric proposals reuse `spending_pressure`, `forecast_spending_change` and
`real_spending_growth` from AB2025. The historical one-percentage-point revision uses `real_spending_growth_revision`. New `reserve_allocated_share` means the
percentage of the specified day-to-day/capital reserve already allocated over
its printed multi-year window. No new unit or baseline proposal.

`arithmetic` is the IFS's own scenario/growth calculation, or an announced target
restated without a named model; the £1.2bn funding amount is marked restated with
`hmt_costing_obr_certified`. Restated rows name their government/DIP origin in
`note`; two announced reserve allocation shares are `administrative_fact`, with
medium confidence, since the slide names no source for them.
Real growth remains percent, growth revisions are percentage points, cash
amounts are GBP, and signs are as printed. Positive pressure means additional
spending required; negative growth is a real cut. There are no central-value
rows: IFS's scenarios are point estimates, never substituted for OBR forecasts.

The 2027–28 to 2030–31 chart rates are average annual real growth over the whole
interval: `growth_period` preserves that interval, and the row's fiscal period
is its terminal year, 2031. The reserve shares likewise retain their complete
allocation windows, ending 2028–29 and 2029–30 respectively. The published £1.2bn
and ~£1bn annual flows have no fiscal year: they carry a 2026 publication-date
snapshot, `time_basis: point_in_time`, `reference_date`, and medium confidence;
the rows do not claim these are 2026 annual outlays. The historical average
1-percentage-point growth revision since 2010 uses the same dated-snapshot
convention. Slide 4 states a calendar-2030 defence target, so that row has no fy;
slide 9 explicitly says 2030–31 and is recorded as fiscal. The difference in date
labels is preserved, not resolved by the harvest.

Not staged: slide 3's unlabelled growth bars and axis ticks; all dates, document
address numbers and slide enumeration; qualitative/unquantified claims; the
second occurrence of the identical 3%-of-GDP scenario annotation within slide 9.
Slide 7 and slide 9 repeated printed labels are retained at their separate
locators, and slide 9's two health bars are separate scenario observations.
The £1bn financing flow is explicitly investment/financing, not military
purchases, matching the slide's caution. The deck identifies no downloadable
data file or distributional chart. No public-services primary was unreached.

Validation: `row_problems` from the AB2026 checker, with registered keys and enums,
reported **28 rows, 0 row problems**. Full-family validation is recorded below. A full visual pass found no contradictory value.
The calendar/fiscal defence target wording and unspecified flow years above are
material limitations.

Deterministic random spot-check (seed 230, 1-based indices within the Boileau component):

| Row | Locator | Printed value | Normalized unit/value | Period check |
|---|---|---|---|---|
| 1 | slide 3 | £8 billion | GBP 8,000,000,000 | FY2030–31 |
| 6 | slide 5 | ~£1bn per year | GBP 1,000,000,000 | no year printed; dated snapshot, medium |
| 10 | slide 7 | 1.7% | percent 1.7 | average 2027–28 to2030–31 |
| 14 | slide 9 | 0.9% | percent 0.9 | average 2027–28 to2030–31 |
| 16 | slide 9 | £9 billion | GBP 9,000,000,000 | interval ends FY2030–31 |
| 18 | slide 9 | 2.7% | percent 2.7 | yellow health bar, average interval |
| 22 | slide 9 | -0.9% | percent -0.9 | green other-departments bar, average interval |
| 23 | slide 9 | -2.1% | percent -2.1 | yellow other-departments bar, average interval |
| 24 | slide 10 | £28 billion | GBP 28,000,000,000 | FY2030–31 |
| 25 | slide 10 | 1 percentage point | percentage_points 1 | historic since2010, dated snapshot |

For every sampled row the primary PDF was reopened with `pdftotext -f/-l` and the
number/string, sign, unit and context checked; slide 7/9 labels were also viewed
at full-page resolution. All printed value strings matched. No bar reading or
arithmetic derived by the harvest was used.


## Stuart Adam: Tax measures

18 rows from one six-slide PDF. Direct fetch with the required browser User-Agent,
2026-10-29 15:43:43Z; 133,005 bytes;
sha256 `6792dc448f40d34f174b6a3c839863b5c969a7334263f5d6b539be62a0428bb8`.
The fetched bytes match the assignment's local copy. Text read with
`pdftotext -layout`; all six slides rendered and visually read as a safeguard
against raster text. Slides 2–6 have no embedded raster images and all printed
numbers are in the text extraction. No distributional chart or data download
is linked inside this deck.

Rows by registered key: `ab2026__package_total_tax_policy_decisions` 1;
`ab2026__writing_down_allowance_12pc_and_fya_50pc` 1;
`ab2026__distributions_framework_modernised` 1;
`ab2026__badr_lifetime_limit_500000` 1;
`ab2026__founders_relief_cgt` 6;
`ab2026__business_rates_sbrr_rhl_thresholds_raised` 3;
`ab2026__electricity_vat_zero_rate_to_july_2027` 1; null 4.
Since 3 November, the £7bn net tax rise, Table 6.1's total of tax policy decisions, takes `decisions_effect_on_borrowing` (README rule 10).
### Proposed measure scopes

Superseded on 3 November (see "Keys the addendum changed" above): the self-assessment timing and the compliance-staff and debt-collection figures are line 45 components, matched to Table 6.3's items by value, and the savings and property income figure uses `ab2026__package_property_and_savings_income_rates`. Rule 8 dropped this deck's six parameter rows (the Founders' Relief rate, comparator and limit, the RHL rateable values and the 0% VAT rate), so it now has 12 rows.

### Conventions and metric proposals

All monetary figures preserve printed signs. Revenue-raising amounts are
positive yields; the Founders' Relief £0.3bn is a positive cost, explicitly
labelled as such. Amounts expressed in £bn/£m are multiplied by 1e9/1e6.
Tax rates remain percent. All quoted excerpts have fewer than 15 words and
contain their exact `value_raw`.

The HMT-certified Budget costings are `restated` with
`source_model: hmt_costing_obr_certified`; rates and eligibility parameters
are `restated` announced-government design with `administrative_data`.
The deck does not cite a source for its beneficiary count or gain calculations;
these are presented as IFS `own`, `arithmetic`. Its maximum business-rate
saving is also IFS arithmetic. `point` is used for printed single estimates;
the £12,000–£21,000 benefiting-property range uses range endpoints. No
uncertainty range is inferred. There are no rows labelled `central` in this deck.

- Reused `tax_threshold_level` (GBP): the £10m cap on qualifying Founders'
  Relief gains and the lower/upper rateable-value bounds identifying RHL
  properties benefiting from higher relief thresholds.
- Proposed `statutory_tax_rate` (percent): the statutory 10% Founders' Relief rate,
  its current 24% standard-rate comparator, and the temporary 0% electricity
  VAT rate. These are statutory parameters, not effective marginal rates.
- Proposed `taxpayer_gain` (GBP): the printed maximum £1.4m gain per
  Founders' Relief beneficiary, with the maximum recorded in conditions.
- Proposed `business_rates_bill_change` (GBP): maximum annual bill saving
  to an RHL property from the higher relief thresholds, £7,146 in 2027-28;
  positive means a gain to the business.

Fiscal-year impacts use their end year. The BADR £0.3bn bullet omits the
year; 2031–32 is inherited from the preceding slide's final-year comparison
and its adjacent Founders' Relief bullet. That row has medium parse confidence
and explains the inheritance. The annual count of 600 beneficiaries and
average £500,000 gain have no year printed; they use an annual 2026
publication-year marker, with explicit `period_assignment` and `horizon`
conditions and medium confidence. This marker does not claim the relief operated in 2026.
Unspecified-year parameters and the maximum £1.4m gain use point-in-time
2026 as announcements, with no fiscal-year condition. No baseline proposal.

### Omissions and source issues

- No effective marginal rates, distributions or unlabelled charts occur in
  this deck. No amounts are inferred from qualitative bullets.
- Dates and durations are descriptive scope rather than numerical impact
  rows: the bank surcharge's 15-month period; two years of business-rate
  discounts; the 2029 revaluation; April 2028 income-tax revenue devolution.
  The devolution slide prints no quantified spending or revenue amount.
- The title slide prints “28 October 2026”, despite the assignment describing
  the 29 October briefing and PDF metadata showing creation/modification on
  29 October. Publication date follows the printed cover (2026-10-28); the
  contradictory date evidence is preserved here, not silently corrected.
- IFS's £1.1bn combined savings/property yield is retained verbatim. The
  corresponding Table 6.1 line-61/62 final-year amounts are £455m and £590m,
  totalling £1.045bn. Different rounding/aggregation could explain the
  displayed £1.1bn; no correction or derivation is staged.
- The £1bn HMRC compliance/debt-collection figure is narrower than line 45's
  full £3.160bn. It is not treated as a contradictory costing of the full package.

### Verification

The 18 individual rows pass `row_problems` from the harvest contract with
zero problems. All 18 short quotes were matched against whitespace-normalised
`pdftotext -layout` output and visually checked on the rendered slides.
Random spot-check seed 230 selected the following ten local rows. Each was
reopened at its slide and checked for exact value, sign, unit and period:

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

The required command, with its uv cache confined to the ignored family primaries
directory, completed successfully:

```sh
UV_CACHE_DIR=.ab2026-primaries/uk_ifs_ab2026/uv-cache PYTHONPATH=. uv run -q python pipeline/ab2026_harvest_contract.py sources/harvest-uk-ab2026-2026-10-29/uk_ifs_ab2026
```

```text
sources/harvest-uk-ab2026-2026-10-29/uk_ifs_ab2026: 106 rows, 0 problems
```

Re-running `stage.py` produced the same gzip SHA256 before and after:
`4f0c9cd197d970486608ea093bf3822ae1d92fa56ebc4a2ac1fae3086430b1cb`.
68 text-row value_raw strings were also matched at their exact PDF slide
locators. Sixty-five quotes match the whitespace-normalised extraction directly;
three Boileau chart annotations interleave with other columns in pdftotext and
were confirmed against rendered slides 7 and 9. All 38 embedded fiscal-table
cells were independently checked visually. All quotes have fewer than 15 words
and contain value_raw.

The final family random sample uses seed 230, ten of 106 rows, one-based gzip
indices. Each primary was reopened at the locator and its number, sign, unit and
period checked. All ten passed; unspecified dates are disclosed markers, not
confirmed implementation dates.

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

Registered-key scope review covered every non-null row:

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

Wernham's full-period VAT *impact* uses a proposal because it includes prior
relief; Adam's zero-rate *parameter* is directly stated for the measure and is
not a costing of the full period. All broader or unidentified packages use null
measure_key with proposals. Source issues are preserved: Adam's cover date,
savings/property rounding, Boileau's calendar/fiscal target wording and undated
flows, Wernham's undated gas reform, and Stockton's uncited attribution. None
was silently corrected.

