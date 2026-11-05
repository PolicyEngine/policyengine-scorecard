# uk_tpa: Tax Policy Associates, Autumn Budget 2026

In this family we stage Dan Neidle's "Budget 2026 – what it means" (taxpolicy.org.uk, 28 October 2026), the seven chart data files the article embeds, and the calculator screenshot its footnote 1 links. We use source slug `tax_policy_associates`, as in the AB2025 `uk_tpa` family.

We keep `stage.py` on branch `uk/ab2026-harvest-staging` at `harvest-staging/ab2026/lanes/thinktanks-a/uk_tpa/stage.py`. We commit only NOTES.md, `manifest.jsonl` and `claims_staged.jsonl.gz` to this branch, and the repository holds no primary bytes. The lane never committed its local primaries folder (`.ab2026-primaries/uk_tpa/`), so fetch each primary from its `manifest.jsonl` URL and check its sha256. `stage.py` reads `uk_hmt_tables` from its sibling directory, so run it from a checkout where the two families share a parent.

We wrote the rows into `stage.py` as data, and it rewrites `manifest.jsonl` and `claims_staged.jsonl.gz` byte for byte. `stage.py --verify` checks the primaries' hashes and finds every quote in its primary. It also reads every chart value back from its JSON path and re-derives each TPA group's Table 6.1 lines from `../uk_hmt_tables`; it reports 0 problems.

- Rows: 305 (own 244, restated 61).
- Primaries: 10 (the article, seven chart data files, one PNG, and the calculator page as a 0-row descriptor).

## Access recipe

We fetched every primary directly on 2026-10-29 between 16:17Z and 16:19Z, with `curl -sSL` and the browser User-Agent in the brief (HTTP 200). The lane saved the bytes under `.ab2026-primaries/uk_tpa/`, and we took nothing from a local copy.

- TPA stamps the article with `article:published_time` 2026-10-28T15:51Z and `article:modified_time` 2026-10-29T09:59Z, so it edited the article once after publication. We hashed the 16:17Z fetch.
- By 4 November readers had added five comments to the article: review B's fetch that day (217,180 bytes, sha256 `d95a0e8f8a0e6465…`) shows `article:modified_time` 2026-11-04T10:10:31Z, and the comments account for 15,211 of the 15,247 added bytes. In review B's 4 November fetch the 49 quotes and footnotes 1–15 read as on 29 October, and TPA had added no figure that the rows and these notes don't already cover. Because TPA changed neither the article's own text nor its figures, the coordinator ruled it not a second primary under README rule 7, and we keep citing the 29 October bytes in the rows. Like every HTML page in this harvest, the article embeds per-request content, so a later fetch's sha256 differs; check instead that the quotes still appear.
- TPA draws the charts as ECharts embeds. In each chart's `data-json` attribute TPA names a JSON file under `/wp-content/assets/`, and we take those files as the primaries, at the URLs TPA names (three end in a `?v=20261028-n` cache-buster). As in AB2025, we set `doc_type` to `flourish_json`, the nearest enum for a chart-data file.
- We take values from the data files, not from bar heights. Where TPA prints a data label on the chart (`label.formatter`), we keep the label in `conditions.chart_label`.
- To quote from a JSON file, we re-serialise the element with `json.dumps` and decode `£` to £ (the AB2025 `uk_tpa` precedent); the file itself may print the same element across several lines. In three of the chart files TPA writes £ as the JSON unicode escape `\u00a3`.
- TPA gives only four of the seven chart files an `aria.label.description`, and we stage the net totals from those four.
- TPA links the PNG (`child_benefit_budget_2026.png`) from footnote 1, as a calculator screenshot. TPA prints its values as text in the tooltip panel, and we read them off the image (`parse_confidence: medium`).
- TPA's "Download as PDF" button builds a PDF in the browser (`tpa-pdf-exporter-loader.js`), so TPA publishes no separate document there.

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
| `ab2026__package_total_tax_policy_decisions` | 40 |
| the 14 group keys below | 65 |
| `ab2026__writing_down_allowance_12pc_and_fya_50pc` | 15 |
| `ab2026__bank_surcharge_6pc_temporary` | 11 |
| `ab2026__hmrc_tax_gap_package` | 8 |
| `ab2026__pension_tax_allowance` | 2 |
| `ab2026__foreign_permanent_establishment_exemption_mandatory` | 5 |
| `ab2026__foreign_sovereign_investments_taxation` | 4 |
| `ab2026__electricity_vat_zero_rate_to_july_2027` | 2 |
| 14 other single measures (Table 6.1 lines 3, 5, 15, 26, 44, 46, 49, 56, 59, 60, 61, 62, 86, 96), one row each | 14 |
| `null` (context) | 139 |

We gave the 139 context rows no measure key:

- the earlier fiscal events in the two history charts (`conditions.policy_event`). We key the 2026 Budget series' 0.0 fills for 2024-25 and 2025-26, years Table 6.1 has no column for, to the series' key instead (rows 98, 99 and 130; review B, TPA finding 1);
- the other countries, the pre-Budget UK, and the after-Budget UK's bank levy and VAT components (which the surcharge leaves unchanged) in the bank chart;
- the fiscal-context levels in footnote 2;
- capital-allowance present values under pre-Budget regimes;
- the child benefit worked example.

## Attribution: how TPA's numbers divide

TPA builds no yield estimates of its own. It takes every £ yield in the article and its charts from HM Treasury's Table 6.1 costing (or the OBR's), and uses it in one of two ways:

- **TPA repeats it**, for example in a chart group that holds a single Table 6.1 line, or as "about £0.7bn" for the £695m total. We mark these rows `restated`, with `source_model: hmt_costing_obr_certified` (or `obr_efo_forecast` for the OBR's paragraph 3.17 averages) and `conditions.originator`. In every restated row's `note` we name whose figure it is ("Restates …"), and write "TPA names no source" where TPA cites none.
- **TPA re-expresses it**: it groups lines, sums them over years, deflates them to 2026-27 prices, or divides them by GDP. We mark these rows `own`, with `source_model: arithmetic` and a `conditions.derived_from` naming the HMT or OBR input, and in every note we say "arithmetic on HM Treasury's costings, not an independent estimate". We treat IFS's own aggregate of HMT costings the same way in the IFS family. At ingest we score all 186 of these `own` rows as TPA's claims, not restatements, or drop them on other grounds (see "Review fixes, 3 November 2026", finding 2).

We mark TPA's own calculations from statutory parameters `own`, with no `derived_from`:

- capital-allowance present values;
- the Pension Tax Allowance's 53% marginal rate;
- the notional investment bank's tax rates;
- the calculator outputs.

Under README rule 8 we treat a measure's own parameters as its design and stage no rows for them. We record the allowance's "£282 withdrawal band", "up to £94 a year" maximum and the "£93" it removes in the conditions of the 53% row.

## Conventions

- **Sign.** We set `positive = yield to the Exchequer` on every revenue row. TPA draws tax rises red and cuts green, which matches.
- **Units.**
  - We give £ figures in pounds (`£ billion × 1e9`).
  - We give charted % of GDP figures as percentages with `proposed_unit: percent_of_gdp`, the OBR lane's spelling, and set `conditions.denominator` to "nominal GDP".
  - We give present values as shares of cost.
  - We give marginal and effective rates in percent.
- **Period and price basis.** We give fiscal-year rows `fy`, with `period` the end year. We convert no price bases:
  - TPA gives the history chart in "2026 money";
  - TPA gives the by-measure chart and footnote 7 in "2026-27 prices";
  - TPA gives every other £ figure in cash.
- **Cumulative rows.** We put the six-year totals at `fy` 2031-32 (`value_kind: cumulative`, `horizon` "2026-27 to 2031-32 (cumulative)").
- **Present values and the bank chart.** The capital-allowance present values describe a regime, so we stage them `point_in_time` 2027, with the regime in `conditions.regime`. TPA draws the bank chart under "2027 rules" (`annual` 2027).
- **Rows with no stated year.** We put "about £1bn a year in the medium term", HM Treasury's 84% (row 9, staged at 2027-28 as we stage para 2.50 in uk_hmt_redbook) and similar figures at a stated year, with a `year_note` and `parse_confidence: medium`. We put the OBR's paragraph 3.17 averages that TPA quotes in footnote 8 (rows 29–30, "a year on average from 2028-29") at 2031-32, the forecast's final year, as we index the same sentences in the uk_obr_tables family. In footnote 15 TPA gives "£450m to £495m a year" as a range across 2028-29 to 2031-32. We stage it at the years in which HM Treasury shows those values on Table 6.1 line 68: £450m in 2029-30 and £495m in 2028-29.
- **Value kinds.** TPA states no ranges for its own estimates, so we stage "About two-fifths" as a `point`, like the family's other "about" figures.
- **Geography.** We give the calculator rows AB2025's code `UK_excl_scotland`, and name the bank chart's other countries.
- **Parts (README rule 9).** TPA prints the bank chart's "Corporate income taxes" for the after-Budget UK (row 278) as a part of the 33.7% total (row 268), so we mark it a `measure_component`. The OBR's £0.4bn (row 30) covers only Table 6.1 line 61's receipts head, so we mark it a `measure_component` of that line ("Tax head (receipts), annual average 2028-29 to 2031-32 (para 3.17)").

## How we found each TPA group's Table 6.1 lines

In footnote 6 TPA says "Our mapping of each row to a group is available on request", so TPA hasn't published the mapping. We inferred the lines below by matching TPA's printed values to Table 6.1 (`../uk_hmt_tables`), and `stage.py --verify` repeats the match:

- **By-year chart.** Every group reproduces TPA's value in all six years exactly. TPA's 11 groups partition the 53 Table 6.1 tax-head lines, which sum to £700m in 2027-28, as TPA says in footnote 5.
- **By-tax chart (2027-28 only).** Each group matches its 2027-28 value exactly. We assign the lines that are zero in 2027-28 from the by-year mapping and, for line 95, from the by-measure "Tariffs" bar. We couldn't determine one line: line 66 (the summer 2026 cut to 5% VAT on family days out). HM Treasury shows zero on it in 2027-28, and in its by-year chart TPA puts it in "Temporary VAT and fuel cuts". But in its by-tax chart TPA splits that group into electricity VAT and fuel, red diesel and HGV VED, and line 66 fits neither. TPA may count it in the by-tax "Other VAT" or "Other", so we leave it out of both scopes below. Leaving line 66 out changes no value.
- **By-measure chart (real terms).** We fitted deflators to its 19 single-measure bars (1.000, 0.9705, 0.9503, 0.9310, 0.9133, 0.8943 for 2026-27 to 2031-32), and they reproduce every bar to within £1m. That settles the multi-line bars. "Savings and property income tax rates +2ppts" takes lines 61 and 62 (3.981; adding line 11 would give 3.816). "Tariffs" includes line 95 (−1.594; without it −1.776), and "Other" takes the remainder.

We give a chart group that holds a single Table 6.1 line that line's registry key. On 29 October we gave the other groups `measure_key: null` and proposed the 14 keys below, and in tranche 2 we registered them.

## Group keys

| key | Table 6.1 lines | TPA's words | rows |
|---|---|---|--:|
| `ab2026__package_property_and_savings_income_rates` | 61, 62 | "The savings and property rise"; "Savings and property income tax rates +2ppts" (by-measure chart). Same spelling and scope as the uk_hmt_redbook family | 5 |
| `ab2026__package_tpa_savings_property_income_and_cash_isa` | 11, 61, 62 | "Savings and property income" (by-year), "Savings and property income tax" (by-tax). The group includes line 11, the cash ISA limit held at £20,000, which TPA doesn't mention | 7 |
| `ab2026__package_tpa_temporary_vat_and_fuel_cuts` | 2, 3, 18, 65, 66 | "Temporary VAT and fuel cuts" (by-year) | 6 |
| `ab2026__package_tpa_fuel_duty_red_diesel_and_hgv_ved` | 3, 18, 65 | "Fuel duty cut, red diesel and HGV VED (temporary)" (by-tax) | 1 |
| `ab2026__package_tpa_business_rates` | 12, 13, 14, 57, 76, 80 | "Business rates" (all three charts). Registry caveat (review B, TPA finding 5): on the by-tax bar, we place line 76, zero in 2027-28, by assumption; the values do not depend on it. | 8 |
| `ab2026__package_tpa_energy_and_environment` | 17, 69, 71, 90, 96 | "Energy and environment" (by-year) | 6 |
| `ab2026__package_tpa_other_income_tax` | 5, 15, 28, 52, 53, 86, 94 | "Other income tax" (by-year); "Income tax: mileage rates, Pension Tax Allowance and other" (by-tax). Registry caveat (review B, TPA finding 5): on the by-tax bar, we place lines 15 and 86, zero in 2027-28, by assumption; the values do not depend on them. | 7 |
| `ab2026__package_tpa_other_vat` | 36, 46, 51, 59, 88, 89 (the by-tax bar may also hold line 66, zero in 2027-28) | "Other VAT" (by-year, by-tax). Registry caveat (thinktanks-a review, finding 6): we place the by-tax lines that are zero in 2027-28 by assumption, and couldn't determine line 66; the values do not depend on it. | 7 |
| `ab2026__package_tpa_other_corporate_tax` | 49, 50, 54, 68, 97 | "Other corporate tax" (by-year, by-tax). Registry caveat (review B, TPA finding 5): on the by-tax bar, we place lines 49 and 50, zero in 2027-28, by assumption; the values do not depend on them. | 7 |
| `ab2026__package_tpa_other_by_year` | 10, 16, 19, 26, 44, 56, 60, 77, 78, 79, 93, 95, 98 | "Other" (by-year) | 6 |
| `ab2026__package_tpa_tariffs` | 10, 16, 77, 78, 95 | "Tariffs (incl. UK-India)" (by-tax, by-measure). Registry caveat (review B, TPA finding 5): on the by-tax bar, we place line 95, zero in 2027-28, by assumption (the by-measure bar settles it); the values do not depend on it. | 2 |
| `ab2026__package_tpa_cgt_founders_relief_and_badr` | 26, 60 | "CGT (Founders' Relief, BADR)" (by-tax) | 1 |
| `ab2026__package_tpa_other_by_tax_2027_28` | 17, 19, 44, 56, 69, 71, 79, 90, 93, 96, 98 (line 66 undetermined) | "Other" (by-tax). The non-zero 2027-28 lines are 19, 44, 56, 69, 79, 90 and 93; we take the zero lines from the by-year mapping. Registry caveat (thinktanks-a review, finding 6): we place the by-tax lines that are zero in 2027-28 by assumption, and couldn't determine line 66; the values do not depend on it. | 1 |
| `ab2026__package_tpa_other_by_measure` | 11, 17, 18, 19, 28, 36, 50, 51, 53, 65, 66, 69, 71, 79, 88, 89, 90, 93, 94, 97, 98 | "Other" (by-measure) | 1 |

We use the registered `ab2026__package_total_tax_policy_decisions` for TPA's rows for "today's Budget" and "the tax measures", the net totals, and the 2026 Budget series of the history charts, because TPA scopes them to all Table 6.1 tax lines. We also key the series' 0.0 cells for 2024-25 and 2025-26 (rows 98, 99 and 130) to it, though Table 6.1 has no column for those years. TPA gives two kinds of total:

- **Sums of the 53 tax lines** (`own`, `arithmetic`): footnote 5's £700m, the by-tax chart's "Net £0.7bn", footnote 7's £19.1bn and £21.0bn, and the by-measure chart's net. These differ from HM Treasury's printed totals by rounding only (£700m against £695m in 2027-28).
- **HM Treasury's printed totals** (`restated`): the by-year chart's "Net total" (TPA prints £-1.65bn for 2026-27, HMT's −£1,645m; the 53 lines sum to −£1,635m), the GDP chart's £ figures, footnote 5's £695m and the article's "about £0.7bn".

## Proposed metrics and units

We reuse one metric from the AB2025 README list: `effective_tax_rate` (the notional bank's tax as a % of profit).

We propose these new metrics, each with TPA's own words:

- **`capital_allowance_present_value` (share):** "the present value of the allowances as a percentage of the cost, discounting at 5% a year" (footnote 12).
- **`marginal_tax_rate` (percent):** "a 53% marginal rate for pensioners on about £13,000", and the calculator's marginal rate.
- **`marginal_take_home_pay` (gbp):** "Of the next £1,000, you keep £417" (calculator screenshot; a level at the margin under current rules, not a policy change).
- **`marginal_tax_amount` (gbp):** "Income tax £400", "NI £20" and "Child benefit charge £163" on the next £1,000 of salary (same screenshot).
- **`unaffected_share` (share):** "84% of income tax payers will be unaffected". We don't use `affected_share`, because TPA gives the unaffected share.
- **`tax_to_gdp_ratio` (`percent_of_gdp`):** "tax burden … 33% of GDP", "Tax take".
- **Context levels from footnote 2:** `public_sector_net_debt_change` (percentage points), `programme_cost` (gbp) and `debt_interest_cost` (gbp, the uk_thinktank_misc spelling).

- **`revenue_share_by_fiscal_event` (share):** "About two-fifths of that comes from Conservative Budgets", the share of the £123bn of extra tax in 2030-31 coming from a group of Budgets. We register `revenue_share` for a group's share of one measure's yield, so it doesn't fit here.

We use the registered metrics `revenue_change`, `caseload` and, for the totals of the Budget's tax measures, `decisions_effect_on_borrowing` (README rule 10, below). We propose no baseline on any row (`baseline_policy` is null throughout).

## Not staged, and why

- We left out policy parameters (README rule 8, "stage estimates, not design"):
  - the Pension Tax Allowance's "up to £94 a year" maximum and "£282 withdrawal band" (in the conditions of the 53% row);
  - "£93", the most tax the allowance removes (20% × (£13,036.40 − £12,570) = £93.28), the same quantity as the £94 maximum. We staged it on 29 October, dropped it on 3 November and kept it as `conditions.tax_removed` on the 53% row;
  - savings and property rates of 24%, 44% and 49%;
  - writing-down allowance rates of 18%, 14%, 12% and 6%, and first-year allowances of 40% and 50%;
  - the £1m annual investment allowance;
  - the full new State Pension of £13,036.40 (which we record in a condition) and the £1-for-£3 taper;
  - the 15% REIT rate in footnote 14;
  - the £60-80k child benefit band in footnote 1;
  - the 2.0% CPI assumption for 2032 (which we record in `conditions.deflator`).
- We left out duplicate phrasings in one primary: TPA's "a new 53% band, for £94" repeats the paragraph's own 53% and £94.
- We left out figures without a year or a measure:
  - "the UK's approximately £3,000bn GDP": an approximate OBR level with no year.
  - "over twice its pre-pandemic share of GDP": a ratio with no printed base.
- We left out the OBR's "High" uncertainty rating for the property costing, which TPA quotes in footnote 8; the rating names a category and belongs in the OBR family.
- We left out the calculator page's 69.5% marginal rate under Reform UK's £15,000 allowance, which falls out of scope as an opposition proposal, not the Budget's.
- We left out material that isn't TPA's:
  - In image-6.png TPA reproduces Red Book paragraph 2.54, HM Treasury's text, which gives only parameters.
  - Readers, not TPA, wrote the comments under the article, for example "the cost is £1.2bn" for Founders' Relief.
- We left out the further-reading thumbnails (image-2, investment_bank_tax_as_of_profit-1, taxable_capital_gains_…), which illustrate other articles.
- We manifest the calculator page (25 October, updated for the Budget) as a 0-row descriptor, as in AB2025:
  - TPA's calculator works out take-home pay, marginal and effective rates, and net-v-gross for employment and other income, current rules against Budget 2027/28;
  - TPA's worked examples on it (62% in the £100k taper, 67.3% and 73.3% with three children and student loans, 84.5% and 89.3% in Scotland, 2,000,000% at the childcare cliff) describe the tax system, not the Budget's measures;
  - TPA restates CenTax's £640m childcare costing there, which we stage in uk_centax.
  - The browser computes its on-screen outputs, and TPA prints none of them as text.
- We left out pre-Budget TPA articles that this one links, outside the assignment: "Banks say they're overtaxed. The TUC says they're undertaxed" (22 October, linked from the bank-tax paragraph), "Capital gains tax reform was right. Now it's dead." (6 October), the Cebr VAT-free shopping article (28 September) and "37 ways Andy Burnham could raise £4.7bn" (3 July). Each could seed a follow-up if the family should include pre-Budget options, as AB2025's did.

## Things in the primaries that look wrong or contradictory (reported, not fixed)

- **Pension Tax Allowance maximum:**
  - TPA says "up to £94 a year" and, a paragraph later, "£93".
  - In OOTLAR paragraph 1.4, which TPA cites, HM Treasury gives the rule: 20% of the full new State Pension minus the Personal Allowance. On TPA's own £13,036.40, that gives £93.28.
  - TPA's "£282 withdrawal band" equals three times £94; three times £93.28 gives £279.84.
- **Start year of the history total:** in the £123bn sentence TPA says tax changes "since 2021"; in footnote 3 it says measures "announced since March 2020".
- **OBR's property figure:** in footnote 8 TPA quotes the OBR (EFO paragraph 3.17) correctly. But the OBR's "£0.4 billion a year on average from 2028-29" for the property rise falls short of Table 6.1 line 61's average over 2028-29 to 2031-32 (£478m).
- **Rounding:** the bank chart's stacked components sum to within 0.1pp of the printed totals, for example the Netherlands at 43.7 against 43.8.

## Review fixes, 3 November 2026

In its review (`harvest-staging/ab2026/reviews/verify-thinktanks-a.md` on the staging branch), the thinktanks-a reviewer approved this family with fixes. We put each in an explicit block at the end of `stage.py`'s rows. We re-opened no primary, because the session's network policy refused taxpolicy.org.uk, and changed no printed value.

- Finding 1, the coordinator's call: we dropped row 16, "£93", as the allowance's design under rule 8, and set `conditions.tax_removed: "£93 (as printed)"` on row 17 (53%). The 306 rows became 305.
- Finding 2: we made no change, since we had already set `conditions.derived_from` on the group, deflated and %-of-GDP rows. At ingest we copy the field onto each of the 155 claims these 186 rows become, and drop the other 31 (30 as out of scope, 1 as a ratio). No code reads the field, so separating these claims from model estimates stays open.
- Finding 3: we made no change. We stage the 2027-28 total tax policy decisions on rows 3, 26, 27, 147, 169 and 237 (0-based before the drop) and the six-year total on rows 4, 28 and 265. At ingest, counting today's 305 rows from 0, we drop the restated rows 3, 26, 146 and 236, and score rows 25 and 168 (2027-28) and 4, 27 and 264 (six years) on `decisions_effect_on_borrowing`. We merge none of these five at ingest, so their duplication stays open.
- Finding 4: we now say, in the quote convention above, that we re-serialise JSON elements.
- Finding 5 (optional, applied): on row 1 ("About two-fifths") we use `proposed_metric: revenue_share_by_fiscal_event`, not the registered `revenue_share`.
- Finding 6: we added the registry caveat to the two by-tax scopes in the group-key table.
- The contract checker reports 305 rows, 0 problems, and when we re-run `stage.py` it reproduces both files byte for byte. COUNTS.json pins the gzip's sha256.

## README rule 10, 3 November 2026

Under README rule 10, in `stage.py` we move TPA's figures for all the Budget's tax measures from `revenue_change` to `decisions_effect_on_borrowing`. We move the 37 rows keyed to `ab2026__package_total_tax_policy_decisions`, in pounds or as a share of GDP. We also move the three 0.0 cells that TPA prints in its charts for years before Table 6.1 starts, which we now key the same way (40 rows in all). Counting from 0, the rows are 2–4, 25–28, 98–104, 130–135, 143–154, 168, 235–240 and 264. We keep `revenue_change` for single measures and groups of measures, and changed no value or sign.

## Review fixes, 4 November 2026

Two independent reviews of PR #231 at 4f424b9 approved this family with fixes, all low: review B (TPA findings 1–6) and review A (K-5, H-6(d) and H-6(e)). We put them in an explicit block after the rule 10 block in `stage.py` and changed no printed value. We give 4f424b9's indices.

- Finding 1, the first fix and the coordinator's call: we key rows 98, 99 and 130, the 2026 Budget series' 0.0 cells for 2024-25 and 2025-26, to `ab2026__package_total_tax_policy_decisions`. We wrote in their note "Table 6.1 has no column for this year; TPA's chart prints 0.0". The key now has 40 rows, and the context rows went from 142 to 139.
- Finding 2, NOTES only and the coordinator's call: in the access recipe we record the article's 4 November change (five reader comments), and don't treat it as a second primary.
- Finding 3, and review A's H-6(e): in each of the 21 restated rows 18–24, 26, 43–48 and 136–142 we name the originator in `note`, and on rows 18, 20, 22 and 142 we say "TPA names no source". We name the OBR's *Fiscal risks and sustainability*, July 2025, which footnote 2 links, as row 21's originator.
- Finding 4: we mark row 278 (corporate income taxes, 30.5%) as a `measure_component` of row 268's 33.7%.
- Finding 5: we added the by-tax caveat to the four further scopes (`…tpa_other_corporate_tax`, `…tpa_other_income_tax`, `…tpa_tariffs`, `…tpa_business_rates`), and moved the two existing caveats into the scope column.
- Finding 6, nits: on rows 299–304 we use `UK_excl_scotland` and record the tooltip's "Smoothed tapers" (`conditions.calculator_setting`). We gave row 9 a `year_note` and medium confidence, and staged row 1 as a `point`. We name the third paragraph after the Red Book excerpt in rows 10–12's locator, and recorded the chart notes, the £ escapes and the Reform UK rate. We also gave row 141 its printed `chart_label` (38.5%), which review B noted in its sample.
- Review A, K-5: we mark row 30 (the OBR's £0.4bn, line 61's receipts) as a `measure_component` with `component: "Tax head (receipts), annual average 2028-29 to 2031-32 (para 3.17)"`. We also applied the optional alignment and put rows 29 and 30 at 2031-32, as we do for the OBR family's paragraph 3.17 rows.
- The contract checker reports 305 rows, 0 problems, and when we re-run `stage.py` in a scratch directory it reproduces both files byte for byte.
