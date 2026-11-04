# uk_hmt_redbook: Autumn Budget 2026 red book, Impact on households and Pension Tax Allowance explainer

**Working files.** `stage.py`, which writes this family's two data files and is the file meant wherever these notes say `stage.py`, lives on branch `uk/ab2026-harvest-staging` at `harvest-staging/ab2026/lanes/hmt-redbook/uk_hmt_redbook/stage.py`; this branch carries only NOTES.md, `manifest.jsonl` and `claims_staged.jsonl.gz`. `.ab2026-primaries/uk_hmt_redbook/` was the lane's local primaries folder and was never committed: the repository carries no primary bytes, so fetch each primary from its `manifest.jsonl` URL and check its sha256.

Source `hm_treasury`. **425 rows from 3 cited primaries (6 hashed versions), 21 proposed measure keys.** `stage.py` embeds every row and manifest line as data; `python3 stage.py` rewrites `claims_staged.jsonl.gz` and `manifest.jsonl` byte for byte with the standard library alone. No primary bytes are vendored.

The first staging (29 October, morning) produced 1,699 rows and 250 proposed keys. This rework applies README rules 8 and 9: it keeps estimates of effects, drops design (parameters, allocations, financing, contingent liabilities), and gives each printed part of one Table 6.1 measure that measure's key. Review A at 4f424b9 (4 November) dropped 7 more (see "Review A fixes"). The section "Not staged (rules 8 and 9)" accounts for all 1,274 dropped rows.

## Primaries

| Primary version | SHA256 | Bytes | Access | Rows |
|---|---|---:|---|---:|
| Budget 2026 (HC 726), 28 October version | `bed70546c026487e3141799968f6df08210c182b0695fed0e8adf7efd6697e03` | 4,657,025 | local copy | 0 |
| Budget 2026 (HC 726), current version | `19b337aced8fe47de1d6ee462dabf75155110d347c38123b6380d90f09e97b93` | 4,679,545 | direct | 357 |
| Impact on households: distributional analysis to accompany Budget 2026 | `36cd5afb4fceca2cecba0d065974ffe8280888e15ed852c129339439e539469c` | 197,606 | direct | 56 |
| Pension Tax Allowance Explainer (content API, full body) | `cc3ec22eb55f4c827c301bc67b06aa7482e4970ef7e1cec644bc382dac0dbb25` | 24,883 | govuk_api | 12 |
| Pension Tax Allowance Explainer (content API, 29 October abbreviated body) | `791d2573bafc67fcfd89567dab55c0239dd26febc9feec44d10f2be4ae21a9e4` | 9,816 | local copy | 0 |
| Pension Tax Allowance Explainer (content API, republished; `updated_at` 2026-10-29T15:55:28Z) | `83f8c894ce76a8e9ce80854f9b7287442d5f6b521a4eb260e5cfacae1c98909b` | 24,356 | govuk_api (review A, 4 November) | 0 |

## Access recipe

Every fresh fetch used:

```sh
curl -sSL -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15" URL -o PATH
shasum -a 256 PATH
```

All fresh fetches returned HTTP 200, and the files sit under `.ab2026-primaries/uk_hmt_redbook/`. No page refused access and none went unreached. The manifest labels the two historical copies `local copy`; they are kept for the changed-primary comparison (README rule 7), not as blocked-fetch fallbacks.

- **Red book:** fresh PDF fetched about 2026-10-29T15:41Z. `19b337ac…` matches the supplied 29 October download. `pdftotext -layout` and `diff -u` against the supplied 28 October version `bed70546…` find one change: paragraph 6.207's heading lost the words "and potential for ULEV SalSac reforms", with resulting line wrapping. **No printed number changed.** Every red-book row cites the current version. Printed page = PDF page minus six.
- **HTML discovery:** the publication content API `https://www.gov.uk/api/content/government/publications/budget-2026-document` (hash `4568690c1ca115ff4a7aa5aa116bcdb39cebee39d8af4490b8dc3ad544b3ec6d`) names the HTML attachment, fetched as a cross-check (hash `33ee5a00b6383104f83790719c0a67e396cfb52e7ea93986b76ab15a19fdaaec`). Neither supplies rows; the PDF is the primary.
- **Impact on households:** fresh PDF fetched 2026-10-29T15:41:44Z, identical to the supplied 29 October copy, read with `pdftotext -layout`. Printed pages equal PDF pages.
- **Pension Tax Allowance explainer:** fresh content API JSON fetched 2026-10-29T15:41:44Z, matching the supplied 28 October response. Rows quote its decoded `details.body`. **The supplied 29 October response differs:** its body is a 353-character introduction without the counts, worked cases or FAQ of the 19,727-character full body. Both carry publication date 28 October. No row cites the abbreviated version.
- **Pension Tax Allowance explainer, republished (README rule 7).** Review A fetched the content API on 4 November and got `83f8c894…` (24,356 bytes, `updated_at` 2026-10-29T15:55:28Z, a 19,206-character body): HM Treasury republished the explainer about 14 minutes after the lane's fetch. All twelve explainer rows' quotes and values are verbatim in it. It fixes "part-time wok" and no longer repeats an FAQ question; "£13.319" remains. The rows keep citing `cc3ec22e…`, the version they were read from.

## Coverage

Rows run in document order: red book (printed page, then position), Impact on households, Pension Tax Allowance explainer.

- **Red book (357 rows):**
  - 160 fiscal aggregates restated from the OBR, ONS and IMF, with two shares of HM Treasury's own arithmetic (Box 1.C footnotes 54 and 56): Chapter 1 text, Chart 1.6's six data labels, Tables 1.2 and 1.3;
  - 84 cells of Table 6.3, which breaks Table 6.1 line 45 into eleven items, with its subtotal, the line 46 memo and the subtotal including memo;
  - 28 costs, yields and savings: Table 6.1 measures where the red book prints the line's own Exchequer impact, printed parts of those lines, and saving estimates with their own scopes;
  - 85 effects on people and businesses: counts affected; gains, losses and bill changes; GDP, earnings, price and jobs effects; Barnett consequentials.
- **Impact on households (56 rows):** the distributional and context statements of paragraphs 1.7, 1.9, 1.10 (first bullet), 2.4, 2.5 and 2.10, and the 50 cells of Table 2.C.
- **Pension Tax Allowance explainer (12 rows):** three pensioner counts and nine worked-case outcomes.

Rows by measure key:

| measure_key | rows | of which components (rule 9) |
|---|---:|---:|
| `null` with a proposed key | 66 | 18 |
| `null`, context (no proposed key) | 189 | 0 |
| `ab2026__hmrc_tax_gap_package` | 73 | 67 |
| `ab2026__pension_tax_allowance` | 12 | 0 |
| `ab2026__british_industrial_competitiveness_scheme` | 8 | 0 |
| `ab2026__household_energy_payment_100_bands_a_to_d` | 8 | 0 |
| `ab2026__business_rates_rhl_transitional_support` | 6 | 6 |
| `ab2026__business_rates_sbrr_rhl_thresholds_raised` | 6 | 0 |
| `ab2026__online_marketplace_liability_uk_businesses` | 6 | 0 |
| `ab2026__electricity_vat_zero_rate_to_july_2027` | 5 | 0 |
| `ab2026__alcohol_duty_small_producer_relief` | 4 | 0 |
| `ab2026__food_and_heating_oil_tariff_suspensions` | 4 | 4 |
| `ab2026__mileage_allowance_payments_55p` | 4 | 0 |
| `ab2026__uk_india_ceta_and_double_contributions_convention` | 4 | 4 |
| `ab2026__your_first_home_equity_loan` | 4 | 0 |
| `ab2026__defence_investment_plan_capital_reallocation` | 3 | 2 |
| `ab2026__ukraine_winter_air_defence` | 3 | 0 |
| `ab2026__civil_service_admin_budgets_cut_20pc` | 2 | 0 |
| `ab2026__civil_service_ai_fund` | 2 | 0 |
| `ab2026__early_years_books_access` | 2 | 0 |
| `ab2026__ev_charging_public_chargers` | 2 | 0 |
| `ab2026__fuel_duty_5p_cut_extended_and_rpi_rise_deferred` | 2 | 0 |
| `ab2026__misogyny_prevention_programmes` | 2 | 0 |
| `ab2026__badr_lifetime_limit_500000` | 1 | 0 |
| `ab2026__benefits_removed_hospitalised_serious_offenders` | 1 | 0 |
| `ab2026__british_business_bank_backing_innovation` | 1 | 1 |
| `ab2026__carbon_price_support_removed` | 1 | 0 |
| `ab2026__carers_allowance_earnings_taper` | 1 | 0 |
| `ab2026__hgv_ved_1_for_12_months` | 1 | 0 |
| `ab2026__national_wealth_fund_capital` | 1 | 0 |
| `ab2026__parental_allowance_fathers_partners_adopters` | 1 | 0 |

The 189 context rows carry no proposed key (README rule 2): 135 fiscal aggregates about no measure (133 restated, and HM Treasury's own two Box 1.C shares), and 54 Impact on households rows (Table 2.C and the context statements of paragraphs 1.10, 2.4, 2.5 and 2.10). The other 24 Table 1.3 rows, the OBR's effect of policy decisions, and Chart 1.6's "Effect of policy" carry `ab2026__package_government_decisions_since_march_2026`.

Rows by metric:

| metric | rows |
|---|---:|
| `revenue_change` | 112 |
| `income_statistic` | 52 |
| `affected_count` | 32 |
| proposed `government_borrowing` | 28 |
| proposed `government_debt` | 25 |
| proposed `fiscal_balance` | 21 |
| proposed `government_borrowing_change` | 20 |
| `decisions_effect_on_borrowing` | 18 |
| proposed `fiscal_balance_change` | 16 |
| `fiscal_headroom` | 14 |
| proposed `government_net_worth` | 9 |
| `energy_bill_change` | 7 |
| proposed `debt_interest_change` | 7 |
| proposed `household_tax_change` | 7 |
| proposed `business_cost_saving` | 6 |
| proposed `average_cumulative_gain` | 5 |
| `gdp_level_effect` | 4 |
| `tax_liability` | 4 |
| proposed `aggregate_household_saving` | 4 |
| proposed `bill_change_percent` | 4 |
| proposed `block_grant_effect` | 4 |
| proposed `jobs_created_or_supported` | 4 |
| `affected_share` | 3 |
| `average_annual_gain` | 3 |
| `gainer_count` | 2 |
| proposed `fiscal_consolidation_share` | 2 |
| proposed `share_in_non_gaining_deciles` | 2 |
| proposed `unaffected_share` | 2 |
| `cpi_inflation_effect` | 1 |
| `revenue_share` | 1 |
| proposed `gross_earnings_change` | 1 |
| proposed `housing_supply_change` | 1 |
| proposed `income_mobility_share` | 1 |
| proposed `share_in_net_recipient_deciles` | 1 |
| proposed `share_in_top_half_of_expenditure` | 1 |
| proposed `share_with_zero_liability` | 1 |

Attribution: 257 rows `own`, 168 `restated` (OBR, ONS, IMF, DWP, DBT, the British Business Bank, the National Wealth Fund).

## Conventions

- **Values as printed.** `value_raw` is the printed string, and `value` scales it to the unit (£ million × 1e6, £ billion × 1e9; percent stays percent; words such as "three-quarters" become fractions with unit `share`). Bounds keep the printed qualifier: "over" and "more than" are `range_low`, "up to" is `range_high`, "around" is `point`.
- **Sign.** Values are never re-signed. `conditions.sign_convention` states each row's direction in the phrasing `scorecard_db/signs.py` reads:
  - Exchequer costs: "positive = cost to the Exchequer (as printed; not re-signed)";
  - savings: "positive = saving to the Exchequer";
  - yields, including Table 6.3: "positive = yield to the Exchequer (reduces borrowing)";
  - Table 1.3: "positive = increase in PSNB" (the opposite of Table 6.1's yield convention), except on its two memo lines, which give the change in the current budget deficit: "positive = increase in current budget deficit" (README rule 10, since 3 November);
  - Table 1.2: deficits and debt positive, surpluses negative, as printed;
  - Chart 1.6's three bridge steps (rows 21, 22 and 24 at 4f424b9): "positive = reduction in current budget deficit (increase in stability rule headroom)", the reverse of Table 1.3's memo, as printed (Chart 1.6's "Effect of policy" +2.0 is Table 1.3's policy memo −2.0 in 2029-30);
  - Box 1.C: each row says what it measures and which way it runs ("positive = fall in borrowing (… as worded: fell by)", "as printed; positive = current budget deficit (% of GDP)" and so on; review A's RB-12);
  - Barnett consequentials: "positive = increase in devolved government funding";
  - gains to a person or business: "positive = gain to the <payer> (…, as printed)", and row 185's CPI effect "positive = reduction in CPI inflation (as worded: reduce inflation by)" (RB-17).
- **Periods.** Fiscal-year figures carry `conditions.fy`, end-year `period` and `time_basis: fiscal_year`. A multi-year total, or an average over the forecast, keeps its whole horizon in `conditions.horizon`, sits at its final fiscal year and is never annualised; "over the forecast" means 2026-27 to 2031-32, as paragraphs 1.20 and 1.40 date it. A figure printed more than once keeps a row for each printing (AB2025 did the same), and the repeats share one dating, the most specific mention's (review A's RB-15); where more than two printings would share one claim identity, only two are kept (RB-2). An undated figure ("by the late 2030s", "this winter") sits at the publication year 2026 with the printed horizon in conditions and, where the year matters, `parse_confidence: medium`.
- **Geography** comes from the harvest's closed list (`UK`, `GB`, `England`, `Wales`, `Scotland`, `Northern Ireland`, `England and Wales`, `Scotland, Wales and Northern Ireland`); any detail goes in `conditions.geography_note` or `note`. The Ofgem price cap and BICS are `GB`.
- **Prices.** Every money figure is cash, as printed; Table 1.3's rows carry `price_basis: current prices`. No basis is converted. (The first staging tagged the £595 million administration saving `real terms`; paragraph 2.14's "real terms" belongs to the Spending Review's 16% cut, and the £595 million equals Table 6.1 line 63's cash +595.)
- **"Central".** HM Treasury prints single estimates; `point` means the printed figure. No row is an inferred scenario. The one OBR scenario row (borrowing £12 billion lower if energy prices follow a lower path) carries `conditions.scenario`.
- **Rule 9 components.** A printed part of one Table 6.1 measure carries the line's key, `conditions.component` naming the part and `conditions.row_type: measure_component`. Components are never summed with the line's total. This family has 102: the 66 Table 6.3 item cells and the 160,000 employees (line 45); the £3 billion and £1.7 billion parts of line 41's £4.7 billion; the four food-tariff consumer savings (line 10; the June-and-November range contains the November-only one, so never add the two); the India agreement's UK, Scotland, Wales and Northern Ireland GDP effects (line 77; the UK figure is the trade deal alone, without the Double Contributions Convention); paragraph 3.22's six figures for line 14's real-terms freeze and SSB extension; the British Business Bank's 40,000 jobs (line 29's capacity half, as Policy Costings p.34); and, under proposed keys, the Tax and Spending parts of the OBR's policy effect, the three devolved Barnett consequentials and three parts of the regulatory administrative savings.
- **`component` means a part only.** Where the first staging used `component` for a Chapter 6 paragraph title on a whole-measure row, the condition is now `paragraph_heading`; in the pension worked cases it is `quantity`. Chart 1.6's six headroom-bridge data labels name their bar in `chart_bar` (changed on 3 November; the rework had left them under `component`).
- **Attribution.** OBR forecasts are `restated` with source model `obr_efo_forecast`; ONS, IMF, DWP, DBT and British Business Bank figures are `restated` and their notes name the original. HM Treasury's own costings, counts and worked cases are `own`.

### Which spending figures stay (rule 8 exception)

A spending figure is a measure's design unless the red book presents it as the measure's Exchequer impact. The test applied: the figure stays when it equals the printed Table 6.1 line (from `uk_hmt_tables`), within the red book's rounding, as a total over the years the red book states or, for a per-year amount, as the line's per-year amount (review A's RB-20(b): the early-years books rows pass only the second form). Tax costs and yields, savings estimates and Table 6.3 stay regardless.

| Table 6.1 line | Red book | Table 6.1 prints (£ million) | Rows |
|---|---|---|---|
| 1 Household Energy Payment | £2.6 billion | -2,625 in 2026-27 | kept (2): the executive summary and para 2.48 (review A's RB-2 dropped Box 3.A's and para 3.5's repeats) |
| 9 Early years books | £5 million a year | -5 a year (2026-27 to 2028-29) | kept (2): the per-year amount equals the line's; the years differ, see anomalies |
| 19 Small Producer Relief | £10 million per year | -10 a year from 2027-28 | kept (2) |
| 32 EV charging | £100 million over two years | -50, -50 | kept (1) |
| 41 DIP capital reallocation | £4.7 billion, 2027-28 to 2029-30 | +2,135, +1,420, +1,100 = 4,655 | kept (1), with its £3 billion and £1.7 billion parts as components (2) |
| 43 Ukraine air defence | £500 million this winter | -500 in 2026-27 | kept (3) |
| 48 Hospitalised offenders | around £5 million in 2031-32 | +5 | kept (1) |
| 63 Administration budgets | £595 million in 2029-30 | +595 | kept (2) |
| 64 Civil Service AI fund | £50 million across 2027-28 and 2028-29 | -25, -25 | kept (2) |
| 71 Carbon Price Support | £235 million over five years | -165, -45, -15, -10 | kept (1) |
| 81 Misogyny prevention | £15 million | -5 a year for three years | kept (2) |
| 20 Good Growth Funds | £285 million in 2027-28 | -340 in 2027-28 | dropped |
| 22 Local apprenticeship services | £100 million over two years | -50, -70 | dropped |
| 25 Strategic Authorities capacity | £150 million in 2027-28 | -180 | dropped |
| 33 Rough sleeping | £432 million across 2027-28 and 2028-29 | -515, -580 | dropped |
| 35 Social and Affordable Homes | £1.5 billion | -250, -500, -500, -500 = -1,750 | dropped |
| 73 Union Learning Fund | £15 million a year | -20 a year | dropped |
| 23, 31, 74, 85 and others | programme amounts inside a line (AI Security Institute, Cardiff Parkway, UKRI clusters, NHS winter funding…) | line totals only | dropped |
| 37 Your First Home (Table 6.2 line 5) | £4.7 billion | -4,700 of financial transactions | dropped: a financial-transactions allocation |
| 6.2 line 4 Sovereign AI | £60 million from 2027-28 | -45 a year | dropped |

## Proposed measure keys (21)

Each key below is the whole scope of its rows, stated as Table 6.1 lines or "no Table 6.1 line", with the red book's words.

- `ab2026__package_government_decisions_since_march_2026` (25 rows): the OBR's "Total effect of policy decisions" on PSNB in Table 1.3, with its Tax and Spending parts (components) and the memo effect on the current budget deficit, 2026-27 to 2031-32, and Chart 1.6's "Effect of policy" on stability rule headroom in 2029-30 (+2.0: the memo's −2.0 seen as headroom; proposed `fiscal_balance_change`). Crosses Table 6.1 lines 1–98 and adds the OBR's indirect effects; Table 1.3 footnote 1 says the OBR's EFO Table 3.1 explains the "Differences between the direct impacts of the policy measures as set out in Table 6.1 of the Budget, and how the OBR incorporate these into their forecast". Not `ab2026__package_total_policy_decisions`.
- `ab2026__package_hmrc_tax_gap_and_online_marketplace` (7 rows): exactly Table 6.1 lines 45 and 46. Table 6.3's "Subtotal including memo" (six years) and footnote 73's "£2.3 billion from this Budget": Table 6.3 prints +2,250m for lines 45 and 46 in 2029-30, against +1,980m for line 45 alone.
- `ab2026__package_parliament_tax_gap_measures` (1 row): lines 45 and 46 plus the tax-gap measures of Autumn Budget 2024, Spring Statement 2025 and Budget 2025 (footnote 73). Paragraph 2.46: "the total due to be raised from measures to close the tax gap announced during this Parliament to over £12 billion in 2029-30".
- `ab2026__package_property_and_savings_income_rates` (2 rows): exactly Table 6.1 lines 61 and 62. Paragraph 2.50: "84% of income tax payers will be unaffected by these changes"; "Around half of the revenue raised from this change is expected to come from the top 10% of households".
- `ab2026__package_breathing_space_for_households` (1 row): paragraph 3.2's "Government action at this Budget to provide breathing space for households", which the OBR expects to reduce CPI inflation by 0.1 percentage points in 2027. Crosses Table 6.1 lines; the red book lists none for this figure. Three scopes are in play, and the row keeps this key until tranche 2 settles them (the coordinator's call on review A's RB-17): Box 3.A's "breathing space for households" is lines 1 and 2 (the Household Energy Payment and the VAT cut); the OBR family keys its own CPI effect to lines 2 and 3 (`ab2026__package_fuel_duty_and_electricity_vat`); and Table 6.1 groups lines 1–11 under "Breathing space for families". Paragraph 1.38 repeats the 0.1 percentage points and is not staged.
- `ab2026__energy_debt_circuit_breaker` (3 rows): no Table 6.1 line. Paragraph 3.8: "a new debt strategy to address this and act as a circuit breaker on energy debt … via reforms to prevent debt building up and a one-off targeted debt relief scheme for eligible households".
- `ab2026__package_parliament_fuel_duty_decisions` (3 rows): Table 6.1 line 3 plus the fuel duty decisions of earlier events in this Parliament. Paragraph 3.13: "the government's decisions on fuel duty across this Parliament … compared with plans under the previous government"; footnote 98's baseline is the 5p cut reversed in April 2025 and annual RPI uprating.
- `ab2026__minimum_wage_uprating_april_2027` (2 rows): no Table 6.1 line (a regulation). Paragraph 3.18: "raising the National Living Wage and National Minimum Wages" from 1 April 2027.
- `ab2026__package_business_rates_rhl_sbrr_and_transitional_support` (2 rows): Table 6.1 lines 13 and 14, the three bullets of paragraph 3.22 (SBRR thresholds; the real-terms freeze; the SSB extension), to which paragraph 3.23's "As a result of this package" refers. The red book does not say whether paragraph 3.21's pubs relief (line 12) also counts.
- `ab2026__package_pubs_relief_35pc_total` (1 row): the whole 35% business rates relief for pubs, social clubs and live music venues in England: the 15% announced in January 2026 (paragraph 6.189; no AB2026 Table 6.1 line) plus Table 6.1 line 12's further 20ppt. Paragraph 3.21: "Taken together, this relief is a tax cut worth an average of over £3,000 per pub next year." Not line 12's key, since line 12 is only the 20ppt (rule 3; review A's RB-3).
- `ab2026__package_regulation_tariff_and_sandbox_business_savings` (1 row): the executive summary's "almost £800 million per year through further cuts to the administrative burdens of regulation, extending suspensions on tariffs, and introducing new cross-economy powers so firms can safely test new technologies faster". Crosses Table 6.1 line 16 (business tariff suspensions) with measures that have no Table 6.1 line.
- `ab2026__regulatory_administrative_savings` (5 rows): no Table 6.1 line. Chapter 6 decision "Regulatory administrative savings" (paragraph 6.36) and paragraph 4.52's "up to an estimated £640 million per annum of new gross administrative savings for business"; its £290 million, £116 million and £105 million parts are components.
- `ab2026__rolls_royce_gas_turbine_programme` (1 row): no Table 6.1 line named. Paragraph 4.80: "co-investment in a joint, 10-year, £2.5‑billion programme for next-generation gas turbine technologies for civil and defence aerospace"; paragraph 4.83 says it "has not been contracted".
- `ab2026__package_defence_investment_plan` (1 row): the Defence Investment Plan published in June 2026, which no single line covers; lines 40–42 carry its savings and funding. Paragraph 5.34: "The Defence Investment Plan will create approximately 60,000 new jobs by 2029‑30 compared with 2023‑24." The OBR family's row on this key (paragraph 3.3's £1.8 billion a year) is the plan's RDEL funding part, a component (review A's K-2).
- `ab2026__package_dwp_fraud_and_error_measures` (1 row): the "new measures" of paragraph 5.17, "expected to save an additional £1.4 billion over the forecast" (2026-27 to 2031-32). The red book doesn't list them. Paragraphs 6.19–6.22 are line 47's own package (its footnote 4; Policy Costings pp.54–58, which `uk_hmt_costings` keys as line 47 components), but the £1.4 billion reconciles with no printed basis for line 47: the line prints +600m over the forecast, +940m with Table 6.2 line 9's +340m, and the costings sum to +570m. So the figure stays off line 47's key (rule 3; review A's RB-8).
- `ab2026__package_parliament_welfare_fraud_and_error_savings` (1 row): this Budget's new fraud and error measures plus those already in the forecast. Paragraph 5.17: "bringing total savings from fraud and error to over £20 billion over the forecast". It doesn't say which earlier measures count. (Review A suggested dropping "parliament" from the one-row key's name; tranche 2 can rename it when it registers the key.)
- `ab2026__package_barnett_consequentials` (4 rows): the Barnett consequentials of "decisions confirmed at Budget", 2026-27 to 2029-30, excluding the technical reduction from lower employer pension contributions (paragraph 4.150). Crosses Table 6.1's England spending lines; no line of its own. The three-government £1.3 billion is `row_type: total`, and the Scottish, Welsh and Northern Ireland figures are components, one per government; `uk_devolved_govts` types the Welsh Government's own figures as Welsh Government components of this key. All four rows say "positive = increase in devolved government funding" (review A's K-7(b)).
- `ab2026__mod_counter_fraud_strategy` (1 row): no Table 6.1 line. Paragraph 5.32: "a new Counter Fraud Strategy in November, with investment in fraud and error analytics and closer working with the Public Sector Fraud Authority set to deliver £250 million of benefits".
- `ab2026__state_pension_triple_lock_adjustment` (2 rows): no Table 6.1 line (its savings fall after the forecast). Paragraph 5.23: "adjusting the Triple Lock from April 2030 so that the State Pension rises each year by the highest of 2.5%, inflation, or the amount required to maintain its value relative to earnings as reached in April 2029"; DWP's estimate (footnote 61).
- `ab2026__package_hmt_distributional_budget_2026` (1 row): HM Treasury's own grouping, the Budget 2026 policies modelled in Impact on households (paragraph 1.4): Table 6.1 lines 2, 3, 4, 5, 8, 11, 15, 26, 39, 49, 52, 59, 60, 61, 62, 72 and 95, plus the private landlord registration fee, which has no line. "Decisions announced at Budget 2026 (including those pre-announced where funding is allocated at Budget 2026)". It excludes line 1, the Household Energy Payment.
- `ab2026__package_hmt_distributional_since_ab2024` (1 row): HM Treasury's own grouping, the modelled policies and public service settlements "announced from Autumn Budget 2024 onwards up to and including Budget 2026" (paragraph 1.8): the lines above plus earlier events' measures, which are not Table 6.1 lines.

The coordinator's shared spellings: no kept row has the scope of `ab2026__gas_standing_charge_moved_to_unit_rates`, `ab2026__pwlb_debt_relief_councils_severe_distress`, `ab2026__private_landlord_register_fee_65`, `ab2026__british_business_bank_defence_commitments_accelerated` or `ab2026__package_household_energy_payment_and_electricity_vat`. The dropped rows on those subjects were design: the £108 current gas standing charge and the end-2027 delivery date (parameters), the £500 million and £200 million of PWLB debt relief (allocations to two councils, which Table 6.1's footnote 2 excludes as adding nothing to borrowing), the £65 fee (a parameter), and the "up to £5 billion" NWF and BBB defence commitment (an investment total). No red-book figure covers exactly lines 1 and 2, or exactly lines 1, 2 and 3 (`ab2026__package_household_energy_vat_and_fuel_duty`).

## Quantity and baseline proposals

- **Proposed metrics:**
  - fiscal aggregates (restated): `government_borrowing`, `government_borrowing_change`, `government_debt`, `government_net_worth`, `fiscal_balance`, `fiscal_balance_change` (also Chart 1.6's three bridge steps, which change the stability rule's headroom, i.e. the 2029-30 current budget), `debt_interest_change`, `fiscal_consolidation_share`; `block_grant_effect` (AB2025 list);
  - household and business effects: `household_tax_change` (AB2025 list; worked cases), `average_cumulative_gain` (multi-year savings), `aggregate_household_saving` (AB2025 spelling; consumer savings), `bill_change_percent` (business electricity bills), `gross_earnings_change` (AB2025 spelling), `business_cost_saving` (administrative savings to business; replaces `operating_cost_change`, which the enum defines as an official operating-cost line), `housing_supply_change` (the 20,000 additional homes), `jobs_created_or_supported` (the NWF's 100,000, the BBB's 40,000, Rolls-Royce's 3,300 and the DIP's 60,000; `affected_count` counts individuals affected, so jobs are not it, review A's RB-9);
  - shares with exact meanings: `unaffected_share` (the share printed as unaffected), `share_with_zero_liability` (half of RHL properties paying no rates), `share_in_non_gaining_deciles`, `share_in_net_recipient_deciles`, `income_mobility_share`, `share_in_top_half_of_expenditure` (Impact on households context).
- **Proposed units:** `businesses` (15 rows), `dwellings` (1).
- **Proposed baselines:** `hmt_no_budget_2026_modelled_policies` (paragraph 1.6, "a counterfactual in which the modelled policies were not introduced") and `hmt_no_policy_changes_from_ab2024_through_ab2026` (paragraph 1.8, "a counterfactual in which the modelled policies and spending settlements were not introduced"), one row each. Other rows have `baseline_policy: null`.

## Not staged (rules 8 and 9)

The rework dropped 1,267 of the first staging's 1,699 rows, and review A's fixes dropped 7 more (4 November), so 1,274 rows are not staged. The first staging's proposed keys that named only dropped rows are gone; their number can't be checked, because the first staging is in neither branch's history, so it is not given.

| Category | Rows | Examples (locator) |
|---|---:|---|
| A. Measure parameters: rates, thresholds, payment amounts, dates, durations; worked-example inputs | 829 | 817 former `policy_parameter` rows, e.g. "£13.21" per hour (para 3.18), "£2,500" surplus earnings threshold (Impact on households para 1.4), "£13,319" withdrawal threshold (explainer FAQ). Also the £100 Household Energy Payment amount (4 rows, e.g. para 2.48); the £108 current gas standing charge (para 3.9); the £2,000 rise in the full new State Pension over the Parliament (para 5.23); six worked-case inputs, e.g. Tom's "£10,300" income. |
| B. Spending allocations: programme funding, capitalisations, investment totals, spending levels | 221 | 166 programme amounts that are not a Table 6.1 line's printed impact (table above), e.g. "£120 million" for the AI Security Institute (para 4.130), "£30 million" for Cardiff Parkway (para 4.157), "£1.5 billion" for the Social and Affordable Homes Programme (para 5.4); 46 investment totals, e.g. NWF "£15.4 billion" (para 4.44), Your First Home "£4.7 billion" (para 5.5); public sector net investment (Table 1.2, 6); departmental spending levels (2); £200 million of private AI model credits (para 4.132). |
| C. Financing: DMO remit, gilts, Treasury bills, NS&I, cash requirements, financial transactions | 177 | DMO net financing requirement "£258.6 billion" (Annex A.8); Table A.1 gilt sales by maturity; CGNCR "£144.1 billion" (para 1.47); Table 1.4 financial transactions by programme, e.g. Student Loans "15.9" (55 rows); Sovereign AI "£60 million" (para 4.135). |
| D. Contingent liabilities | 14 | Table 1.5, e.g. Department for Energy Security and Net Zero "1.2-1.7"; Total reasonable worst case "4-4.5". |
| E. Programme inputs, scope counts and targets | 25 | "670" HMRC compliance officers to recruit (paras 2.42, 6.151); tariffs on "over 100" food products (para 3.17); "around 10,000" homes the Social and Affordable Homes Programme funds (para 6.114); the 25% administrative-burden target worth "£5.6 billion" (para 4.51); "over 90% of England's population will have a devolution agreement in place" (para 4.68), a coverage count that includes existing agreements (review A's RB-7, dropped 4 November). |
| F. Effects of policies outside this Budget | 3 | "more than 100" businesses using the Global Talent funder pathway since Budget 2025 (para 4.112); "over £5 billion" of services exports from the Switzerland and South Korea deals (para 4.124); "over £2 billion of net progress secured" against the administrative-burden target (para 4.51), progress before this Budget (footnote 137 cites a July 2026 annex; para 4.52 counts this Budget's £640 million separately; RB-7). |
| G. Repeats beyond two of one claim | 4 | The Household Energy Payment's "£2.6 billion" in para 3.5 and Box 3.A, and "up to 20 million households" in para 3.3 and Box 3.A. Kept: the £2.6 billion of the executive summary and para 2.48, and the 20 million of the executive summary and paras 2.48 and 3.5 (review A's RB-2; see Review A fixes). |
| H. The rework brief's drop list | 1 | Impact on households para 1.10's "over four times as much in public spending than they pay in tax" (`spending_to_tax_ratio`, which the brief's item 1 names for removal; RB-13). Row 365's 60% beside it stays as a printed value. |

Rule 9 moved 74 kept rows from proposed keys to a Table 6.1 line's key: the 66 Table 6.3 item cells and the 160,000 employees (proposed keys such as `ab2026__package_tax_gap_timely_payment`, now line 45 components); four food-tariff savings (now line 10 components); the £3 billion and £1.7 billion DIP parts (now line 41 components); and the Your First Home count (now line 37). One row stays off a line's key: the £1.4 billion of DWP fraud savings, which reconciles with no printed basis for line 47 (rule 3; see its proposed key).

### Other material not staged

- **Tables 6.1, 6.2 and 6.4** belong to `uk_hmt_tables`. Table 6.3 is a separate printed breakdown and is staged here.
- **No Impact on households bar readings** (README rule 4). Figures 1.A–1.E print no data labels. Chart 1.6's six data labels are staged.
- **Words without numbers** ("hundreds of pounds a month", "thousands of jobs") are not turned into numbers.
- **Footnote 73's earlier-event yields** (£6.5 billion, over £1 billion, £2.4 billion) are other fiscal events' measures; only this Budget's £2.3 billion and the £12 billion total are staged.
- **Background macro forecasts** that score no measure (GDP growth, inflation, employment, Table 1.1), departmental efficiency histories, Annex B budgets and Annex C charts are not staged.
- **The abbreviated 29 October explainer** has no quantitative content.
- **Other figures not staged (review A's RB-20(c)):** paragraph 5.17's Motability saving "over £1 billion over the next five years" (no Table 6.1 line); paragraph 3.7's £150 from Budget 2025 (an earlier event's measure); paragraph 4.36's reprioritisation savings (spending allocations); paragraph 4.42's National Wealth Fund and British Business Bank outcomes to date (effects before this Budget); and paragraph 6.9's £150 million (an allocation).
- **Paragraph 1.38's** repeat of the OBR's 0.1 percentage point CPI effect (row 185 stages paragraph 3.2's).

## Judgement calls for the coordinator

- **`spending_to_tax_ratio` is dropped (review A's RB-13).** The 3 November finish kept paragraph 1.10's "over four times" as a distributional statement. Review A read the rework brief's item 1 as a named removal list whose only exception is a Table 6.1 cost or yield: neither primary prints another spending-to-tax ratio, so the list can only mean this row, and HM Treasury frames paragraph 1.10 as "context beyond the impact of recent government policy decisions". The row is dropped (category H). The 60% row beside it, Table 2.C and the other Impact on households context rows stay as printed values.
- **Mislabelled shares beyond the 84%.** Besides the 84% (`unaffected_share`, never 16%), BADR's "three-quarters … will still receive relief on their entire gain" is the unaffected share too; "half of all RHL properties … will not pay business rates at all" includes properties already paying none (`share_with_zero_liability`); and Impact on households' 20%, 60%, 59% and approximately 20% are not affected shares (proposals above). The registered `share_no_change` is a household-income measure, so the 84% of income tax payers follows the brief's `unaffected_share`.
- **Registered metrics replace AB2025-era proposals.** The four "around £50 off the annual Ofgem price cap" rows and the three energy-debt "£30" rows now use the registered `energy_bill_change` (unit `gbp_per_household`), which the enum mints for HM Treasury bill figures; the India agreement's GDP effects use `gdp_level_effect` in GBP (the AB2025 IPPR precedent).
- **Financial transactions and public sector net investment are dropped as financing and spending levels.** Table 1.4 prints forecast levels of lending by programme, not Budget effects. Public sector net investment is an OBR aggregate, but the brief lists `public_investment_share` for removal.
- **Jobs and induced homes stay; delivery targets go.** Estimated jobs (NWF 100,000; BBB 40,000; Rolls-Royce 3,300; DIP 60,000; proposed `jobs_created_or_supported` since review A) and Your First Home's "estimated 20,000 new homes" are estimated effects. The 10,000 homes the Social and Affordable Homes Programme funds (in line 35's title), robotic procedures rising to 500,000, 2,000 learners and the 650,000 workforce requirement of the infrastructure pipeline are delivery targets of allocations.
- **The BBB's 40,000 jobs is now `restated`.** Footnote 135 cites the British Business Bank's press release. The NWF's 100,000 is `restated` too (footnote 134 cites the National Wealth Fund's own statement).

## Printed problems and differences

- **Spending figures that differ from Table 6.1:**
  - Social and Affordable Homes Programme: £1.5 billion (paras 5.4, 6.114) against line 35's -1,750 over 2027-28 to 2030-31.
  - Early years books: "£5 million a year for three years from 2027-28" (paras 3.20, 6.122) against line 9's -5 in 2026-27, 2027-28 and 2028-29. The amount agrees; the years do not.
  - Local apprenticeship services £100 million (line 22: -120); Good Growth Funds £285 million in 2027-28 (line 20: -340); Strategic Authorities £150 million (line 25: -180); Union Learning Fund £15 million a year (line 73: -20 a year); Sovereign AI £60 million (Table 6.2 line 4: -45 a year).
  - DWP fraud and error: "an additional £1.4 billion over the forecast" (para 5.17) against line 47's +600m in total (+940m with Table 6.2 line 9; the Policy Costings' +570m).
- **Regulatory savings target:** paragraph 6.36 prints "£5.6 million"; paragraph 4.51 prints "£5.6 billion". The executive summary's "almost £800 million per year" and paragraph 4.52's "up to … £640 million per annum" have different printed scopes; both stay.
- **Repeated amounts that disagree (not staged after rule 8):** local AI partnerships £30 million (para 4.135) and £15 million (para 6.101); Leeds College of Building £28 million (para 4.71) and £15 million (para 6.53); business tariff suspensions on 269 goods (para 3.28), 350 goods (para 4.147) and 361 extensions plus 72 new suspensions (line 16's title).
- **Pubs relief:** the text prints an extra "20%"; Table 6.1 prints "20ppts".
- **Table 1.3** labels the new forecast "November 2026 forecast" in an October Budget. Chart 1.6 prints 14.5 where the text says £15 billion. "Debt is lower at the end of the forecast" fits public sector net financial liabilities (83.2% to 81.7%), while public sector net debt goes from 95.5% to 95.6%.
- **Paragraphs 6.225 and 6.226** repeat the Machine Games Duty measure. Annex A footnote 181 points to A.17 for green gilts, which A.19 covers.
- **Pension Tax Allowance explainer:** the FAQ prints "£13.319" for £13,319; the explainer prints both £13,036.40 and the rounded £13,037, and "up to £94" beside Steph's £93.28. The 28 October version's FAQ repeats a question and prints "part-time wok"; the version HM Treasury republished on 29 October (`83f8c894…`) fixes both and still prints "£13.319".

## Verification

- **Checker:** `PYTHONPATH=. uv run -q python pipeline/ab2026_harvest_contract.py sources/harvest-uk-ab2026-2026-10-29/uk_hmt_redbook` reports 425 rows, 0 problems (4 November, after review A's fixes, with the coordinator's tightened checks).
- **Determinism:** two runs of `stage.py` write the same `claims_staged.jsonl.gz` and an unchanged `manifest.jsonl`. COUNTS.json pins the gzip's sha256.
- **Spot check (the rework's, 29 October; row numbers are the rework's, which held at 4f424b9):** 30 rows drawn with `random.Random(20261029).sample(range(432), 30)` (0-based row numbers), each re-opened at its locator in the hashed primaries: red-book and Impact on households pages extracted with `pdftotext -layout -f N -l N`; table cells read against the printed row and column. All 30 match on value, sign, unit and period.

| Row | Locator | Printed | Staged value and unit | Period |
|---:|---|---|---|---|
| 44 | Table 1.2, Current budget deficit, 2027-28 | 0.5 | 0.5 percent of GDP | 2028, fy 2027-28 |
| 53 | Table 1.2, Public sector net borrowing, 2030-31 | 1.8 | 1.8 percent of GDP | 2031, fy 2030-31 |
| 68 | Table 1.2, Cyclically adjusted primary deficit, 2027-28 | -0.5 | -0.5 percent of GDP | 2028, fy 2027-28 |
| 75 | Table 1.2, PSNFL, 2028-29 | 83.8 | 83.8 percent of GDP | 2029, fy 2028-29 |
| 92 | Table 1.2, Public sector net worth, 2027-28 | 63.4 | 63.4 percent of GDP (inverted, as printed) | 2028, fy 2027-28 |
| 115 | Table 1.3, November 2026 forecast, 2029-30 | 73.8 | £73.8 billion PSNB | 2030, fy 2029-30 |
| 118 | Table 1.3, Difference, 2026-27 | 17.7 | £17.7 billion (positive = higher PSNB) | 2027, fy 2026-27 |
| 125 | Table 1.3, Underlying forecast differences, 2028-29 | 11.4 | £11.4 billion | 2029, fy 2028-29 |
| 130 | Table 1.3, Debt interest, 2028-29 | 12.0 | £12.0 billion | 2029, fy 2028-29 |
| 133 | Table 1.3, Other forecast changes, 2026-27 | -4.0 | -£4.0 billion | 2027, fy 2026-27 |
| 138 | Table 1.3, Memo: current budget deficit (underlying), 2026-27 | 0.6 | £0.6 billion | 2027, fy 2026-27 |
| 145 | Table 1.3, Total effect of policy decisions, 2028-29 | 2.1 | £2.1 billion (positive = higher PSNB) | 2029, fy 2028-29 |
| 178 | para 2.46 | over £12 billion | £12 billion, range_low, yield | 2030, fy 2029-30 |
| 185 | para 3.2 | 0.1 percentage points | 0.1 pp reduction in CPI | 2027, annual |
| 216 | para 3.16 | around £150 per year | £150 a year per EV driver | 2027, annual |
| 217 | para 3.17 | £120-185 million per annum | £120 million, range_low, consumer saving | 2026, publication year |
| 226 | para 3.21 | over £3,000 per pub | £3,000, range_low | 2028, fy 2027-28 |
| 234 | para 3.22 | 120,000 shops | 120,000 businesses | 2029, two years to 2028-29 |
| 235 | para 3.22 | £3,250 over the two years | £3,250, cumulative | 2029, two years to 2028-29 |
| 256 | para 4.146 | Wales's economy by £80 million | £80 million GDP, Wales component of line 77 | 2026, publication year |
| 273 | para 6.36 | up to £640 million | £640 million, range_high, saving to business | 2026, publication year |
| 299 | Table 6.3 row 4, 2028-29 | +0m | £0, line 45 component | 2029, fy 2028-29 |
| 327 | Table 6.3 row 9, 2026-27 | +0m | £0, line 45 component | 2027, fy 2026-27 |
| 337 | Table 6.3 row 10, 2030-31 | +0m | £0, line 45 component | 2031, fy 2030-31 |
| 350 | Table 6.3 subtotal, 2031-32 | +3,160m | £3,160 million yield, line 45 | 2032, fy 2031-32 |
| 354 | Table 6.3 memo, 2029-30 | +270m | £270 million yield, line 46 | 2030, fy 2029-30 |
| 356 | Table 6.3 memo, 2031-32 | +265m | £265 million yield, line 46 | 2032, fy 2031-32 |
| 369 | Impact on households para 2.10 | £33,500 | £33,500 gross household income, decile 3 | 2029, fy 2028-29 |
| 395 | Table 2.C, fifth decile, 1 adult | 30,400 | £30,400 | 2029, fy 2028-29 |
| 400 | Table 2.C, fourth decile, 1 adult | 26,300 | £26,300 | 2029, fy 2028-29 |

### Tranche 1 finish (3 November 2026)

The rework stopped before its report, so on 3 November each instruction of `briefs/rework-hmt-redbook.md` (on the staging branch) was checked against the rows:

- **Removed metrics.** No `policy_parameter` row remains, and of the nine allocation and financing metrics only `spending_to_tax_ratio` remains, on one row (paragraph 1.10's "over four times"). It stays: it is a distributional statement printed in Impact on households, which item 3 of the brief keeps, not the fiscal aggregate the drop list targets. See the judgement calls above.
- **Rule 9 and the "Also fix" section.** The 84% row is `unaffected_share` as printed. No row carries `ab2026__package_tax_gap_timely_payment`; line 45's items carry line 45's key as components. No measure without a Table 6.1 line is named as a package. No kept row has the scope of the coordinator's shared spellings (see "Proposed measure keys").
- **`component`.** Six rows still used `component` for a chart bar; they now use `chart_bar`.
- **Stale files.** The family had no REPORT.md or spot-check files left.
- **Keys** were harmonised across families on 3 November; `stage.py`'s `KEY_MAP` lists each rename, and the proposed keys above give the final spellings.
- **Checker:** 0 problems. **Determinism:** a re-run of `stage.py` reproduces the gzip and manifest byte for byte.
- **Spot check: not repeated.** The brief asked for 15 random rows re-opened at their locators. The 3 November session's network policy refused gov.uk and assets.publishing.service.gov.uk (HTTP 403 at the proxy), so no primary could be fetched, and no row was re-opened. The 30-row check above is the rework's own; nobody independent has checked this rework yet.

## Key harmonisation, 3 November 2026

The coordinator gave each scope one key across families (tranche 1, task 3.4). This family's renames:

- `ab2026__package_obr_forecast_policy_effects` → `ab2026__package_government_decisions_since_march_2026`
- `ab2026__package_budget_barnett_consequentials` → `ab2026__package_barnett_consequentials`
- `ab2026__defence_investment_plan` → `ab2026__package_defence_investment_plan`

The OBR's Table 3.1 "Total effect of Government decisions" prints the same figures as Table 1.3's "Total effect of policy decisions" (2.1 in 2028-29 in both), so the red book's restatement shares the OBR family's key. The Barnett key names the scope the Welsh Government's figures share (£450 million here, £448m there). The Defence Investment Plan crosses Table 6.1 lines 40–42, so it is a package, shared with the OBR's DIP funding row. Table 1.3's Tax and Spending parts stay components of the total, as staged.

## README rule 10, 3 November 2026

Table 1.3's total effect of policy decisions and its tax and spending parts (18 rows) already took `decisions_effect_on_borrowing`, and its two memo lines on the current budget deficit (11 rows) already proposed `fiscal_balance_change`. The memo rows' sign convention named PSNB, so `stage.py` now states which way the current budget deficit moves on rows 138–142 (underlying forecast differences) and 161–166 (policy decisions). No value or sign changed. The contract checker reports 432 rows, 0 problems, and a re-run of `stage.py` reproduces the gzip byte for byte.

## Review A fixes, 4 November 2026

Review A (issue comment 6635870934 on #231, at 4f424b9) approved this family with fixes. `stage.py` applies each as an explicit, commented step after the rows, indexed by 4f424b9's row numbers, and drops rows only at the end. No primary was re-opened for this round; every new quote and value comes from the review or the row. 432 rows → 425; `own` 263 → 257, `restated` 169 → 168; 6 hashed primaries.

- **RB-1:** paragraph 5.17's two totals "over the forecast" (rows 265 and 266) sit at 2031-32 with the forecast's horizon; row 265 is `cumulative`, row 266 keeps `range_low`; row 267 is `point_in_time`.
- **RB-2:** rows 191 and 200 dropped (the £2.6 billion's third and fourth printings); row 179 dated 2026-27. The same rule drops rows 188 and 201, which repeat "up to 20 million" in paragraph 3.3 and Box 3.A: once RB-11 put rows 180 and 201 in England, four rows shared one claim identity (the coordinator's new duplicate-claim check, H-3, rejects more than two).
- **RB-3:** row 226 moved to `ab2026__package_pubs_relief_35pc_total`.
- **RB-4:** Chart 1.6's bridge steps (rows 21, 22, 24) propose `fiscal_balance_change` with the stability rule's sign; row 24 carries the government-decisions key; all six rows name the stability rule, and rows 20, 23 and 25 their forecast vintage and policy scenario.
- **RB-5:** row 246 is a line 29 component (its proposed key is retired); rows 232–237 are line 14 components; row 254 is a line 77 component.
- **RB-6:** rows 219–220's component says it contains rows 217–218.
- **RB-7:** rows 247 and 252 dropped (the coordinator's call), with their one-row keys `ab2026__package_parliament_regulatory_burden_reduction` and `ab2026__english_devolution_agreements`; categories F and E list them.
- **RB-8:** the DWP fraud key's scope and row 265's note rewritten; rows 265–266 `hmt_published_estimate_method_unspecified`.
- **RB-9:** rows 245, 246, 253 and 268 propose `jobs_created_or_supported`; row 245 is `restated`; rows 253 and 268 `hmt_published_estimate_method_unspecified`.
- **RB-10:** rows 11 and 240 dated 2027-28 ("per year from 2027-28"); rows 6 and 11 `hmt_costing_obr_certified`.
- **RB-11:** geography corrected on rows 5, 8, 9, 14, 180, 190, 196–199, 201–205, 258, 269 and 275, and "Great Britain" written `GB` throughout (the harvest's closed list).
- **RB-12:** rows 30–39's sign conventions; rows 30, 31, 34, 35, 36 and 38 are ONS outturns (`administrative_data`, `administrative_fact`).
- **RB-13:** row 366 dropped (category H).
- **RB-14:** the republished explainer is a 0-row primary (manifest line 6).
- **RB-15:** repeats share a dating (rows 9, 10, 14, 196, 205, 248–251, 271, 273), and rows 0, 19, 215 and 244 take the multi-year convention.
- **RB-16:** rows 143–166's `reform_hint` is "Total effect of policy decisions".
- **RB-17:** rows 185, 216, 226 and 237 have conventions `signs.py` reads; row 185 keeps its key, with the three scopes in its bullet; row 182 is 0.84 `share`.
- **RB-18:** rows 33 and 37 are HM Treasury's own arithmetic; rows 6, 7, 8, 10, 11, 12 and 14 take their repeats' source models (row 5's and row 9's repeats are already `arithmetic`; row 13 has no repeat and keeps its label); row 222 is a worked example (`arithmetic`, with its subgroup); row 183 `decile_10`; row 184 dated 2027-28, medium confidence, `hmt_published_estimate_method_unspecified`; row 168 loses `presentation`; row 267 `hmt_published_estimate_method_unspecified`. **Not done:** row 194's note should give footnote 84's "fuel stressed" definition, which needs the primary.
- **RB-19:** rows 15, 29, 41 and 42 quote only their sentence; rows 103, 104 and 167 lose their leading paragraph numbers; locators of rows 172, 190, 227, 248 and 249 corrected. **Not done:** rows 365 and 368 still quote fragments, since the whole sentences need the primary (row 366 is dropped).
- **RB-20:** (a) the unverifiable "234 proposed keys" figure is removed; (b) the spending test reads "the per-year amount equals the line's", which rows 224 and 276 pass, so they stay; (c) five more figures listed under "Other material not staged".
- **RB-21:** this lane folder's gzip and NOTES now match #231's; the 40 proposed-metric rows set `metric: null` explicitly. Table 6.3's duplication of Table 6.1 lines 45 and 46 (`uk_hmt_tables`) is left to tranche 2's cross-family dedupe.
- **K-7(b):** row 258 is the Barnett `total`, and rows 258–261 carry the sign convention.
- **K-7(c):** row 222 already proposes `gross_earnings_change`, the AB2025 spelling; no change.
