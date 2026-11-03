# uk_tpa: Tax Policy Associates, Autumn Budget 2026

Dan Neidle's "Budget 2026 – what it means" (taxpolicy.org.uk, 28 October 2026), the seven chart data files the article embeds, and the calculator screenshot its footnote 1 links. Source slug `tax_policy_associates`, as in the AB2025 `uk_tpa` family.

**Working files.** `stage.py`, the file meant wherever these notes say `stage.py`, lives on branch `uk/ab2026-harvest-staging` at `harvest-staging/ab2026/lanes/thinktanks-a/uk_tpa/stage.py`; this branch carries only NOTES.md, `manifest.jsonl` and `claims_staged.jsonl.gz`. The lane's local primaries folder (`.ab2026-primaries/uk_tpa/`) was never committed: the repository carries no primary bytes, so fetch each primary from its `manifest.jsonl` URL and check its sha256. `stage.py` reads `uk_hmt_tables` from its sibling directory, so run it from a checkout where the family sits beside that one.

`stage.py` holds the rows as data and rewrites `manifest.jsonl` and `claims_staged.jsonl.gz` byte for byte. `stage.py --verify` checks the primaries' hashes, finds every quote in its primary, reads every chart value back from its JSON path, and re-derives each TPA group's Table 6.1 lines from `../uk_hmt_tables` (result: 0 problems).

- **Rows:** 305 (own 244, restated 61).
- **Primaries:** 10 (the article, seven chart data files, one PNG, and the calculator page as a 0-row descriptor).

## Access recipe

Every primary was fetched directly on 2026-10-29 between 16:17Z and 16:19Z, with `curl -sSL` and the browser User-Agent in the brief (HTTP 200). The bytes are under `.ab2026-primaries/uk_tpa/`; nothing came from a local copy.

- **The article** carries `article:published_time` 2026-10-28T15:51Z and `article:modified_time` 2026-10-29T09:59Z, so TPA edited it once after publication. The copy hashed here is the 16:17Z fetch.
- **The charts** are ECharts embeds. Each chart's `data-json` attribute names a JSON file under `/wp-content/assets/`, and those files are the primaries, URLs as named (three carry a `?v=20261028-n` cache-buster). As in AB2025, `doc_type` is `flourish_json`, the nearest enum for a chart-data file.
- **Values come from the data files, not from bar heights.** Where the chart prints a data label (`label.formatter`), the label is kept in `conditions.chart_label`. Each chart file also has an `aria.label.description` sentence, and the net totals are staged from it.
- **Quotes** from a JSON file are the element re-serialised with `json.dumps`, with `£` decoded to £ (the AB2025 `uk_tpa` precedent); the file itself may print the same element across several lines with `\u00a3` escapes.
- **The PNG** (`child_benefit_budget_2026.png`, linked from footnote 1) is a calculator screenshot. Its values are printed text in the tooltip panel, read off the image (`parse_confidence: medium`).
- **The "Download as PDF" button** builds a PDF in the browser (`tpa-pdf-exporter-loader.js`). It is not a separate document.

## Rows by primary

| primary | sha256 | rows |
|---|---|--:|
| Budget 2026 – what it means (HTML) | `9d8031655aa08411…` | 49 |
| budget_tax_rises_by_event.json | `62d64a909445ce61…` | 63 |
| tax_take_by_government.json | `b13087894131a927…` | 31 |
| budget_2026_tax_gdp_impact.json | `a96c8f8f29b1e0e7…` | 12 |
| budget_2026_chart_by_tax_2027_28.json | `dcf10b6e82b0848a…` | 14 |
| budget_2026_chart_by_year_v2.json | `db22d5e01bb59ba7…` | 72 |
| budget_2026_chart_by_measure_total_real.json | `7355f24b6b8a620c…` | 24 |
| bank-tax-compare-uk-budget-2026.json | `7a8454d612b6e46b…` | 34 |
| child_benefit_budget_2026.png | `e69c25ad27fbd19b…` | 6 |
| The UK tax calculator (HTML, descriptor) | `69a72c68640f3b2f…` | 0 |

## Rows by measure key

| measure_key | rows |
|---|--:|
| `null` (65 with a proposed key, 142 context) | 207 |
| `ab2026__package_total_tax_policy_decisions` | 37 |
| `ab2026__writing_down_allowance_12pc_and_fya_50pc` | 15 |
| `ab2026__bank_surcharge_6pc_temporary` | 11 |
| `ab2026__hmrc_tax_gap_package` | 8 |
| `ab2026__pension_tax_allowance` | 2 |
| `ab2026__foreign_permanent_establishment_exemption_mandatory` | 5 |
| `ab2026__foreign_sovereign_investments_taxation` | 4 |
| `ab2026__electricity_vat_zero_rate_to_july_2027` | 2 |
| 14 other single measures (Table 6.1 lines 3, 5, 15, 26, 44, 46, 49, 56, 59, 60, 61, 62, 86, 96), one row each | 14 |

The 142 context rows have no measure key and no proposal:

- the earlier fiscal events in the two history charts (`conditions.policy_event`), and the 2026 Budget series' 0.0 fills for 2024-25 and 2025-26, years before Table 6.1 starts;
- the other countries, the pre-Budget UK, and the after-Budget UK's bank levy and VAT components (which the surcharge leaves unchanged) in the bank chart;
- the fiscal-context levels in footnote 2;
- capital-allowance present values under pre-Budget regimes;
- the child benefit worked example.

## Attribution: how TPA's numbers divide

TPA builds no yield estimates of its own. Every £ yield in the article and its charts is HM Treasury's Table 6.1 costing (or the OBR's), and TPA uses it in one of two ways:

- **Repeats it,** for example a chart group that is exactly one Table 6.1 line, or "about £0.7bn" for the £695m total. These rows are `restated`, with `source_model: hmt_costing_obr_certified` (or `obr_efo_forecast` for the OBR's paragraph 3.17 averages) and `conditions.originator`.
- **Re-expresses it.** TPA groups lines, sums them over years, deflates them to 2026-27 prices, or divides them by GDP. These rows are `own`, with `source_model: arithmetic` and a `conditions.derived_from` naming the HMT or OBR input, and every note says "arithmetic on HM Treasury's costings, not an independent estimate". This matches the IFS lane's treatment of IFS's own aggregate of HMT costings. The ingest can separate these rows on `derived_from` if it treats them as restatements.

TPA's own calculations from statutory parameters are `own` with no `derived_from`:

- capital-allowance present values;
- the Pension Tax Allowance's 53% marginal rate;
- the notional investment bank's tax rates;
- the calculator outputs.

Under README rule 8, a measure's own parameters are its design, not rows. The allowance's "£282 withdrawal band", "up to £94 a year" maximum and the "£93" it removes therefore sit in the conditions of the 53% row.

## Conventions

- **Sign:** `positive = yield to the Exchequer` on every revenue row. The charts draw tax rises red and cuts green, which matches.
- **Units:**
  - £ figures are in pounds (`£ billion × 1e9`).
  - Charted % of GDP figures are percentages with `proposed_unit: percent_of_gdp`, the OBR lane's spelling. `conditions.denominator` says "nominal GDP".
  - Present values are shares of cost.
  - Marginal and effective rates are percent.
- **Period and price basis:** fiscal-year rows carry `fy`, with `period` the end year. Price bases are not converted:
  - the history chart is in "2026 money";
  - the by-measure chart and footnote 7 are in "2026-27 prices";
  - every other £ figure is cash.
- **Cumulative rows:** the six-year totals sit at `fy` 2031-32 (`value_kind: cumulative`, `horizon` "2026-27 to 2031-32 (cumulative)").
- **Present values and the bank chart:** the capital-allowance present values are properties of a regime, so they are `point_in_time` 2027, with the regime in `conditions.regime`. The bank chart is under "2027 rules" (`annual` 2027).
- **Rows with no stated year:** "about £1bn a year in the medium term" and similar figures sit at a stated year, with a `year_note` and `parse_confidence: medium`. Footnote 15's "£450m to £495m a year" (a range across 2028-29 to 2031-32) is staged at the years Table 6.1 line 68 shows those values: £450m in 2029-30 and £495m in 2028-29.
- **"Central":** TPA states no ranges for its own estimates. The one `central` row is "About two-fifths".

## How each TPA group's Table 6.1 lines were found

TPA's footnote 6 says "Our mapping of each row to a group is available on request", so the mapping isn't published. The lines below were inferred by matching TPA's printed values to Table 6.1 (`../uk_hmt_tables`). `stage.py --verify` repeats the match:

- **By-year chart:** every group reproduces TPA's value in all six years exactly. Its 11 groups partition the 53 Table 6.1 tax-head lines, which sum to £700m in 2027-28, as footnote 5 says.
- **By-tax chart (2027-28 only):** each group matches its 2027-28 value exactly. Lines that are zero in 2027-28 are assigned by the by-year mapping and, for line 95, by the by-measure "Tariffs" bar. One line stays undetermined: line 66 (the summer 2026 cut to 5% VAT on family days out). It is zero in 2027-28, the by-year chart puts it in "Temporary VAT and fuel cuts", and the by-tax chart splits that group into electricity VAT and fuel, red diesel and HGV VED, neither of which it fits. It may sit in the by-tax "Other VAT" or "Other", and it is left out of both scopes below. The values are unaffected.
- **By-measure chart (real terms):** deflators fitted to its 19 single-measure bars (1.000, 0.9705, 0.9503, 0.9310, 0.9133, 0.8943 for 2026-27 to 2031-32) reproduce every bar to within £1m. That settles the multi-line bars: "Savings and property income tax rates +2ppts" is lines 61 and 62 (3.981; adding line 11 would give 3.816), "Tariffs" includes line 95 (−1.594; without it −1.776), and "Other" is the remainder.

A chart group that is exactly one Table 6.1 line carries that line's registry key. Other groups carry a proposed key.

## Proposed measure keys (all `measure_key: null`)

| proposed key | Table 6.1 lines | TPA's words | rows |
|---|---|---|--:|
| `ab2026__package_property_and_savings_income_rates` | 61, 62 | "The savings and property rise"; "Savings and property income tax rates +2ppts" (by-measure chart). Same spelling and scope as the uk_hmt_redbook family | 5 |
| `ab2026__package_tpa_savings_property_income_and_cash_isa` | 11, 61, 62 | "Savings and property income" (by-year), "Savings and property income tax" (by-tax). The group includes line 11, the cash ISA limit held at £20,000, which TPA doesn't mention | 7 |
| `ab2026__package_tpa_temporary_vat_and_fuel_cuts` | 2, 3, 18, 65, 66 | "Temporary VAT and fuel cuts" (by-year) | 6 |
| `ab2026__package_tpa_fuel_duty_red_diesel_and_hgv_ved` | 3, 18, 65 | "Fuel duty cut, red diesel and HGV VED (temporary)" (by-tax) | 1 |
| `ab2026__package_tpa_business_rates` | 12, 13, 14, 57, 76, 80 | "Business rates" (all three charts) | 8 |
| `ab2026__package_tpa_energy_and_environment` | 17, 69, 71, 90, 96 | "Energy and environment" (by-year) | 6 |
| `ab2026__package_tpa_other_income_tax` | 5, 15, 28, 52, 53, 86, 94 | "Other income tax" (by-year); "Income tax: mileage rates, Pension Tax Allowance and other" (by-tax) | 7 |
| `ab2026__package_tpa_other_vat` | 36, 46, 51, 59, 88, 89 (the by-tax bar may also hold line 66, zero in 2027-28) | "Other VAT" (by-year, by-tax) | 7 Registry caveat (thinktanks-a review, finding 6): the by-tax lines that are zero in 2027-28 are placed by assumption and line 66 is undetermined; the values do not depend on it. |
| `ab2026__package_tpa_other_corporate_tax` | 49, 50, 54, 68, 97 | "Other corporate tax" (by-year, by-tax) | 7 |
| `ab2026__package_tpa_other_by_year` | 10, 16, 19, 26, 44, 56, 60, 77, 78, 79, 93, 95, 98 | "Other" (by-year) | 6 |
| `ab2026__package_tpa_tariffs` | 10, 16, 77, 78, 95 | "Tariffs (incl. UK-India)" (by-tax, by-measure) | 2 |
| `ab2026__package_tpa_cgt_founders_relief_and_badr` | 26, 60 | "CGT (Founders' Relief, BADR)" (by-tax) | 1 |
| `ab2026__package_tpa_other_by_tax_2027_28` | 17, 19, 44, 56, 69, 71, 79, 90, 93, 96, 98 (line 66 undetermined) | "Other" (by-tax). The non-zero 2027-28 lines are 19, 44, 56, 69, 79, 90 and 93; the zero lines come from the by-year mapping | 1 Registry caveat (thinktanks-a review, finding 6): the by-tax lines that are zero in 2027-28 are placed by assumption and line 66 is undetermined; the values do not depend on it. |
| `ab2026__package_tpa_other_by_measure` | 11, 17, 18, 19, 28, 36, 50, 51, 53, 65, 66, 69, 71, 79, 88, 89, 90, 93, 94, 97, 98 | "Other" (by-measure) | 1 |

`ab2026__package_total_tax_policy_decisions` is registered. It carries TPA's rows for "today's Budget" and "the tax measures", the net totals, and the 2026 Budget series of the history charts from 2026-27, because their scope is all Table 6.1 tax lines. The totals come in two kinds:

- **Sums of the 53 tax lines** (`own`, `arithmetic`): footnote 5's £700m, the by-tax chart's "Net £0.7bn", footnote 7's £19.1bn and £21.0bn, and the by-measure chart's net. These differ from HM Treasury's printed totals by rounding only (£700m against £695m in 2027-28).
- **HM Treasury's printed totals** (`restated`): the by-year chart's "Net total" (it prints £-1.65bn for 2026-27, HMT's −£1,645m; the 53 lines sum to −£1,635m), the GDP chart's £ figures, footnote 5's £695m and the article's "about £0.7bn".

## Proposed metrics and units

Reused from the AB2025 README list: `effective_tax_rate` (the notional bank's tax as a % of profit).

New proposals, each with TPA's own words:

- **`capital_allowance_present_value` (share):** "the present value of the allowances as a percentage of the cost, discounting at 5% a year" (footnote 12).
- **`marginal_tax_rate` (percent):** "a 53% marginal rate for pensioners on about £13,000", and the calculator's marginal rate.
- **`marginal_take_home_pay` (gbp):** "Of the next £1,000, you keep £417" (calculator screenshot; a level at the margin under current rules, not a policy change).
- **`marginal_tax_amount` (gbp):** "Income tax £400", "NI £20" and "Child benefit charge £163" on the next £1,000 of salary (same screenshot).
- **`unaffected_share` (share):** "84% of income tax payers will be unaffected". This is not `affected_share`: the value is the unaffected share.
- **`tax_to_gdp_ratio` (`percent_of_gdp`):** "tax burden … 33% of GDP", "Tax take".
- **Context levels from footnote 2:** `public_sector_net_debt_change` (percentage points), `programme_cost` (gbp) and `debt_interest_cost` (gbp, the uk_thinktank_misc spelling).

- **`revenue_share_by_fiscal_event` (share):** "About two-fifths of that comes from Conservative Budgets", the share of the £123bn of extra tax in 2030-31 coming from a group of Budgets. The registered `revenue_share` is a group's share of one measure's yield, so it does not fit.

The family uses the registered Metrics `revenue_change`, `caseload` and, for the totals of the Budget's tax measures, `decisions_effect_on_borrowing` (README rule 10, below). No row proposes a baseline (`baseline_policy` is null throughout).

## Not staged, and why

- **Policy parameters** (README rule 8, "stage estimates, not design"):
  - the Pension Tax Allowance's "up to £94 a year" maximum and "£282 withdrawal band" (in the conditions of the 53% row);
  - "£93", the most tax the allowance removes (20% × (£13,036.40 − £12,570) = £93.28), the same quantity as the £94 maximum: staged on 29 October, dropped on 3 November and kept as `conditions.tax_removed` on the 53% row;
  - savings and property rates of 24%, 44% and 49%;
  - writing-down allowance rates of 18%, 14%, 12% and 6%, and first-year allowances of 40% and 50%;
  - the £1m annual investment allowance;
  - the full new State Pension of £13,036.40 (carried in a condition) and the £1-for-£3 taper;
  - the 15% REIT rate in footnote 14;
  - the £60-80k child benefit band in footnote 1;
  - the 2.0% CPI assumption for 2032 (carried in `conditions.deflator`).
- **Duplicate phrasings** in one primary: "a new 53% band, for £94" repeats the paragraph's own 53% and £94.
- **Figures without a year or a measure:**
  - "the UK's approximately £3,000bn GDP": an approximate OBR level with no year.
  - "over twice its pre-pandemic share of GDP": a ratio with no printed base.
- **Not numeric:** the OBR's "High" uncertainty rating for the property costing (footnote 8) is categorical. It belongs to the OBR family.
- **Not TPA's:**
  - image-6.png reproduces Red Book paragraph 2.54, HM Treasury's text, which holds only parameters.
  - Reader comments under the article, for example "the cost is £1.2bn" for Founders' Relief, are not TPA's.
- **Further-reading thumbnails** (image-2, investment_bank_tax_as_of_profit-1, taxable_capital_gains_…) illustrate other articles.
- **The calculator page** (25 October, updated for the Budget) is a 0-row descriptor, as in AB2025:
  - it calculates take-home pay, marginal and effective rates, and net-v-gross for employment and other income, current rules against Budget 2027/28;
  - its worked examples (62% in the £100k taper, 67.3% and 73.3% with three children and student loans, 84.5% and 89.3% in Scotland, 2,000,000% at the childcare cliff) describe the tax system, not the Budget's measures;
  - it restates CenTax's £640m childcare costing, which is staged in uk_centax.
  - Its on-screen outputs are computed in the browser and are not printed text.
- **Pre-Budget TPA articles linked from this one, outside the assignment:** "Banks say they're overtaxed. The TUC says they're undertaxed" (22 October, linked from the bank-tax paragraph), "Capital gains tax reform was right. Now it's dead." (6 October), the Cebr VAT-free shopping article (28 September) and "37 ways Andy Burnham could raise £4.7bn" (3 July). They are candidates for a follow-up if the family is to include pre-Budget options, as AB2025's did.

## Things in the primaries that look wrong or contradictory (reported, not fixed)

- **Pension Tax Allowance maximum:**
  - The article says "up to £94 a year" and, a paragraph later, "£93".
  - OOTLAR paragraph 1.4, which TPA cites, gives the rule: 20% of the full new State Pension minus the Personal Allowance. On TPA's own £13,036.40, that is £93.28.
  - The "£282 withdrawal band" is three times £94; three times £93.28 is £279.84.
- **Start year of the history total:** the £123bn sentence says tax changes "since 2021"; footnote 3 says measures "announced since March 2020".
- **OBR's property figure:** footnote 8 quotes the OBR (EFO paragraph 3.17) correctly, but the OBR's "£0.4 billion a year on average from 2028-29" for the property rise sits below Table 6.1 line 61's average over 2028-29 to 2031-32 (£478m).
- **Rounding:** the bank chart's stacked components sum within 0.1pp of the printed totals, for example the Netherlands at 43.7 against 43.8.

## Review fixes, 3 November 2026

The thinktanks-a review (`harvest-staging/ab2026/reviews/verify-thinktanks-a.md` on the staging branch) approved this family with fixes. Each sits in an explicit block at the end of `stage.py`'s rows. No primary was re-opened (the session's network policy refused taxpolicy.org.uk); no printed value changed.

- **Finding 1 (the coordinator's call):** row 16, "£93", is the allowance's design under rule 8 and is dropped; row 17 (53%) carries `conditions.tax_removed: "£93 (as printed)"`. 306 rows become 305.
- **Finding 2:** no change. The group, deflated and %-of-GDP rows carry `conditions.derived_from`; tranche 2 separates them from model estimates on it.
- **Finding 3:** no change. The 2027-28 total tax policy decisions appear in several rows (3, 26, 27, 147, 169 and 237, 0-based before the drop) and the six-year total in rows 4, 28 and 265; tranche 2 should deduplicate them.
- **Finding 4:** the quote convention above now says JSON elements are re-serialised.
- **Finding 5 (optional, applied):** row 1 ("About two-fifths") uses `proposed_metric: revenue_share_by_fiscal_event`, not the registered `revenue_share`.
- **Finding 6:** the two by-tax scopes carry the registry caveat in the proposed-key table.
- **Verification:** the contract checker reports 305 rows, 0 problems, and a re-run of `stage.py` reproduces both files byte for byte. COUNTS.json pins the gzip's sha256.

## README rule 10, 3 November 2026

Under README rule 10, `stage.py` moves TPA's figures for all the Budget's tax measures from `revenue_change` to `decisions_effect_on_borrowing`: the 37 rows keyed to `ab2026__package_total_tax_policy_decisions`, in pounds or as a share of GDP, and the three unkeyed 0.0 cells that TPA's charts print for years before Table 6.1 starts. Counting from 0, the rows are 2–4, 25–28, 98–104, 130–135, 143–154, 168, 235–240 and 264. Single measures and groups of measures keep `revenue_change`. No value or sign changed.
