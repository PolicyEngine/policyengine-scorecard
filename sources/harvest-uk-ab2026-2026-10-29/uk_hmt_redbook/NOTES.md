# uk_hmt_redbook: Autumn Budget 2026 red book, Impact on households and Pension Tax Allowance explainer

We keep `stage.py`, which writes this family's two data files, on branch `uk/ab2026-harvest-staging` at `harvest-staging/ab2026/lanes/hmt-redbook/uk_hmt_redbook/stage.py`. We commit only NOTES.md, `manifest.jsonl` and `claims_staged.jsonl.gz` to this branch, and the repository holds no primary bytes. The lane kept its local primaries in `.ab2026-primaries/uk_hmt_redbook/` and never committed them, so fetch each primary from its `manifest.jsonl` URL and check its sha256.

We use source `hm_treasury`. We stage **425 rows from 3 cited primaries (6 hashed versions), on 50 measure keys, 21 of which we proposed and tranche 2 registered.** We embedded every row and manifest line in `stage.py` as data. `python3 stage.py` rewrites `claims_staged.jsonl.gz` and `manifest.jsonl` byte for byte with the standard library alone. We vendor no primary bytes.

Our first staging (29 October, morning) produced 1,699 rows and 250 proposed keys. In this rework we apply README rules 8 and 9. We keep estimates of effects and drop design (parameters, allocations, financing, contingent liabilities), and we key each printed part of one Table 6.1 measure to that measure. After review A at 4f424b9 (4 November) we dropped 7 more (see "Review A fixes"). We account for all 1,274 dropped rows in the section "Not staged (rules 8 and 9)".

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

For every fresh fetch the lane ran:

```sh
curl -sSL -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15" URL -o PATH
shasum -a 256 PATH
```

Every fresh fetch returned HTTP 200, the lane saved the files under `.ab2026-primaries/uk_hmt_redbook/`, and no page refused access. We label the two historical copies `local copy` in the manifest. We keep them for the changed-primary comparison (README rule 7), not as blocked-fetch fallbacks.

- **Red book.** The lane fetched a fresh PDF about 2026-10-29T15:41Z, and `19b337ac…` matches the supplied 29 October download. It ran `pdftotext -layout` and `diff -u` against the supplied 28 October version `bed70546…` and found one change: HM Treasury cut the words "and potential for ULEV SalSac reforms" from paragraph 6.207's heading, which rewrapped the lines. **HM Treasury changed no printed number.** Every red-book row cites the current version. The printed page equals the PDF page minus six.
- **HTML discovery.** The publication content API `https://www.gov.uk/api/content/government/publications/budget-2026-document` (hash `4568690c1ca115ff4a7aa5aa116bcdb39cebee39d8af4490b8dc3ad544b3ec6d`) names the HTML attachment, which we fetched as a cross-check (hash `33ee5a00b6383104f83790719c0a67e396cfb52e7ea93986b76ab15a19fdaaec`). We staged no rows from either and take the PDF as the primary.
- **Impact on households.** The lane fetched a fresh PDF at 2026-10-29T15:41:44Z, identical to the supplied 29 October copy, and read it with `pdftotext -layout`. Its printed pages equal PDF pages.
- **Pension Tax Allowance explainer.** The lane fetched fresh content API JSON at 2026-10-29T15:41:44Z, matching the supplied 28 October response, and our rows quote its decoded `details.body`. **The supplied 29 October response differs.** In it HM Treasury gives a 353-character introduction without the counts, worked cases or FAQ of the 19,727-character full body. Both show publication date 28 October. No row cites the abbreviated version.
- **Pension Tax Allowance explainer, republished (README rule 7).** Review A fetched the content API on 4 November and got `83f8c894…` (24,356 bytes, `updated_at` 2026-10-29T15:55:28Z, a 19,206-character body). So HM Treasury republished the explainer about 14 minutes after the lane's fetch. All twelve explainer rows' quotes and values appear verbatim in it. HM Treasury fixed "part-time wok" and no longer repeats an FAQ question, but left "£13.319". We keep the rows citing `cc3ec22e…`, the version we read them from.

## Coverage

We order rows by document: red book (printed page, then position), Impact on households, Pension Tax Allowance explainer.

- **Red book (357 rows):**
  - 160 fiscal aggregates that HM Treasury restates from the OBR, ONS and IMF, with two shares of HM Treasury's own arithmetic (Box 1.C footnotes 54 and 56): Chapter 1 text, Chart 1.6's six data labels, Tables 1.2 and 1.3;
  - 84 cells of Table 6.3, in which HM Treasury breaks Table 6.1 line 45 into eleven items, with its subtotal, the line 46 memo and the subtotal including memo;
  - 28 costs, yields and savings: Table 6.1 measures where the red book prints the line's own Exchequer impact, printed parts of those lines, and saving estimates with their own scopes;
  - 85 effects on people and businesses: counts affected; gains, losses and bill changes; GDP, earnings, price and jobs effects; Barnett consequentials.
- **Impact on households (56 rows):** the distributional and context statements of paragraphs 1.7, 1.9, 1.10 (first bullet), 2.4, 2.5 and 2.10, and the 50 cells of Table 2.C.
- **Pension Tax Allowance explainer (12 rows):** three pensioner counts and nine worked-case outcomes.

Rows by measure key:

| measure_key | rows | of which components (rule 9) |
|---|---:|---:|
| the 21 keys we proposed (below) | 66 | 18 |
| `null`, context (no key) | 189 | 0 |
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

We give the 189 context rows no key (README rule 2). They comprise 135 fiscal aggregates about no measure (133 restated, plus HM Treasury's own two Box 1.C shares) and 54 Impact on households rows (Table 2.C and the context statements of paragraphs 1.10, 2.4, 2.5 and 2.10). We key the other 24 Table 1.3 rows, the OBR's effect of policy decisions, and Chart 1.6's "Effect of policy" to `ab2026__package_government_decisions_since_march_2026`.

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

We mark 257 rows `own` and 168 `restated` (OBR, ONS, IMF, DWP, DBT, the British Business Bank, the National Wealth Fund).

## Conventions

- **Values as printed.** We copy the printed string to `value_raw` and scale it to the unit in `value` (£ million × 1e6, £ billion × 1e9; percent stays percent; words such as "three-quarters" become fractions with unit `share`). We keep the printed qualifier on bounds: "over" and "more than" give `range_low`, "up to" gives `range_high`, and "around" gives `point`.
- **Sign.** We never re-sign values. In `conditions.sign_convention` we state each row's direction in the phrasing `scorecard_db/signs.py` reads:
  - Exchequer costs: "positive = cost to the Exchequer (as printed; not re-signed)";
  - savings: "positive = saving to the Exchequer";
  - yields, including Table 6.3: "positive = yield to the Exchequer (reduces borrowing)";
  - Table 1.3: "positive = increase in PSNB", the opposite of Table 6.1's yield convention. Its two memo lines give the change in the current budget deficit: "positive = increase in current budget deficit" (README rule 10, since 3 November);
  - Table 1.2: deficits and debt positive, surpluses negative, as printed;
  - Chart 1.6's three bridge steps (rows 21, 22 and 24 at 4f424b9): "positive = reduction in current budget deficit (increase in stability rule headroom)". HM Treasury prints these steps with the opposite sign to Table 1.3's memo: Chart 1.6's "Effect of policy" +2.0 shows Table 1.3's policy memo −2.0 in 2029-30;
  - Box 1.C: on each row we say what it measures and which way it runs (review A's RB-12), for example "positive = fall in borrowing (… as worded: fell by)" and "as printed; positive = current budget deficit (% of GDP)";
  - Barnett consequentials: "positive = increase in devolved government funding";
  - gains to a person or business: "positive = gain to the <payer> (…, as printed)", and row 185's CPI effect "positive = reduction in CPI inflation (as worded: reduce inflation by)" (RB-17).
- **Periods.**
  - We give fiscal-year figures `conditions.fy`, end-year `period` and `time_basis: fiscal_year`.
  - For a multi-year total, or an average over the forecast, we keep the whole horizon in `conditions.horizon`, put the row at its final fiscal year and never annualise it. We read "over the forecast" as 2026-27 to 2031-32, as HM Treasury dates it in paragraphs 1.20 and 1.40.
  - Where HM Treasury prints a figure more than once, we keep a row for each printing (as in AB2025) and give the repeats one dating, the most specific mention's (review A's RB-15). Where more than two printings would share one claim identity, we keep only two (RB-2).
  - We put an undated figure ("by the late 2030s", "this winter") at the publication year 2026, with the printed horizon in conditions and, where the year matters, `parse_confidence: medium`.
- **Geography.** We take it from the harvest's closed list (`UK`, `GB`, `England`, `Wales`, `Scotland`, `Northern Ireland`, `England and Wales`, `Scotland, Wales and Northern Ireland`), and put any detail in `conditions.geography_note` or `note`. We record the Ofgem price cap and BICS as `GB`.
- **Prices.** HM Treasury prints every money figure in cash, and we stage it so; on Table 1.3's rows we set `price_basis: current prices`. We convert no basis. (Our first staging tagged the £595 million administration saving `real terms`. But in paragraph 2.14 HM Treasury applies "real terms" to the Spending Review's 16% cut, and the £595 million equals Table 6.1 line 63's cash +595.)
- **"Central".** HM Treasury prints single estimates, and we mark the printed figure `point`. We infer no scenario on any row. On the one OBR scenario row (borrowing £12 billion lower if energy prices follow a lower path) we set `conditions.scenario`.
- **Rule 9 components.** We key a printed part of one Table 6.1 measure to the line, name the part in `conditions.component` and set `conditions.row_type: measure_component`. We never sum components with the line's total. In this family we stage 102:
  - the 66 Table 6.3 item cells and the 160,000 employees (line 45);
  - the £3 billion and £1.7 billion parts of line 41's £4.7 billion;
  - the four food-tariff consumer savings (line 10). The June-and-November range contains the November-only one, so never add the two;
  - the India agreement's UK, Scotland, Wales and Northern Ireland GDP effects (line 77). HM Treasury's UK figure covers the trade deal alone, without the Double Contributions Convention;
  - paragraph 3.22's six figures for line 14's real-terms freeze and SSB extension;
  - the British Business Bank's 40,000 jobs (line 29's capacity half, as in Policy Costings p.34);
  - under the keys we proposed, the Tax and Spending parts of the OBR's policy effect, the three devolved Barnett consequentials and three parts of the regulatory administrative savings.
- **We use `component` for a part only.** Where our first staging used `component` for a Chapter 6 paragraph title on a whole-measure row, we now use `paragraph_heading`, and in the pension worked cases `quantity`. On 3 November we moved Chart 1.6's six headroom-bridge data labels, which the rework had left under `component`, to `chart_bar`.
- **Attribution.** We mark OBR forecasts `restated` with source model `obr_efo_forecast`. We mark ONS, IMF, DWP, DBT and British Business Bank figures `restated` and name the original in their notes. We mark HM Treasury's own costings, counts and worked cases `own`.

### Which spending figures stay (rule 8 exception)

We treat a spending figure as a measure's design unless the red book presents it as the measure's Exchequer impact. We keep the figure when it equals the printed Table 6.1 line (from `uk_hmt_tables`), within the red book's rounding. It may match as a total over the years the red book states or, for a per-year amount, as the line's per-year amount (review A's RB-20(b): the early-years books rows pass only the second form). We keep tax costs and yields, savings estimates and Table 6.3 regardless.

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

## Keys we proposed (21)

We proposed each key below, and tranche 2 registered it and moved it into `measure_key`. We give each key the whole scope of its rows, as Table 6.1 lines or "no Table 6.1 line", with the red book's words.

- `ab2026__package_government_decisions_since_march_2026` (25 rows): the OBR's "Total effect of policy decisions" on PSNB in Table 1.3, with its Tax and Spending parts (components) and the memo effect on the current budget deficit, 2026-27 to 2031-32. It also covers Chart 1.6's "Effect of policy" on stability rule headroom in 2029-30 (+2.0: the memo's −2.0 seen as headroom; proposed `fiscal_balance_change`). We scope the key across Table 6.1 lines 1–98 and the OBR's indirect effects. In Table 1.3 footnote 1 HM Treasury says the OBR's EFO Table 3.1 explains the "Differences between the direct impacts of the policy measures as set out in Table 6.1 of the Budget, and how the OBR incorporate these into their forecast". We don't use `ab2026__package_total_policy_decisions` here.
- `ab2026__package_hmrc_tax_gap_and_online_marketplace` (7 rows): exactly Table 6.1 lines 45 and 46. It covers Table 6.3's "Subtotal including memo" (six years) and footnote 73's "£2.3 billion from this Budget". In Table 6.3 HM Treasury prints +2,250m for lines 45 and 46 in 2029-30, against +1,980m for line 45 alone.
- `ab2026__package_parliament_tax_gap_measures` (1 row): lines 45 and 46 plus the tax-gap measures of Autumn Budget 2024, Spring Statement 2025 and Budget 2025 (footnote 73). Paragraph 2.46: "the total due to be raised from measures to close the tax gap announced during this Parliament to over £12 billion in 2029-30".
- `ab2026__package_property_and_savings_income_rates` (2 rows): exactly Table 6.1 lines 61 and 62. Paragraph 2.50: "84% of income tax payers will be unaffected by these changes"; "Around half of the revenue raised from this change is expected to come from the top 10% of households".
- `ab2026__package_breathing_space_for_households` (1 row): paragraph 3.2's "Government action at this Budget to provide breathing space for households", which the OBR expects to reduce CPI inflation by 0.1 percentage points in 2027. We scope the key across Table 6.1 lines, though the red book lists none for this figure.
  - The row fits three scopes, and we keep it on this key (the coordinator's call on review A's RB-17). #247 registers the key with a `partial` verdict and leaves the three readings open (`KEY_DECISIONS.md`), and at ingest we drop the row as a restatement of the OBR's figure.
  - In Box 3.A HM Treasury's "breathing space for households" covers lines 1 and 2 (the Household Energy Payment and the VAT cut). In the OBR family we key the OBR's own CPI effect to lines 2 and 3 (`ab2026__package_fuel_duty_and_electricity_vat`). In Table 6.1 HM Treasury groups lines 1–11 under "Breathing space for families".
  - HM Treasury repeats the 0.1 percentage points in paragraph 1.38, which we don't stage.
- `ab2026__energy_debt_circuit_breaker` (3 rows): no Table 6.1 line. Paragraph 3.8: "a new debt strategy to address this and act as a circuit breaker on energy debt … via reforms to prevent debt building up and a one-off targeted debt relief scheme for eligible households".
- `ab2026__package_parliament_fuel_duty_decisions` (3 rows): Table 6.1 line 3 plus the fuel duty decisions of earlier events in this Parliament. Paragraph 3.13: "the government's decisions on fuel duty across this Parliament … compared with plans under the previous government". In footnote 98 HM Treasury takes as baseline the 5p cut reversed in April 2025 and annual RPI uprating.
- `ab2026__minimum_wage_uprating_april_2027` (2 rows): no Table 6.1 line (a regulation). Paragraph 3.18: "raising the National Living Wage and National Minimum Wages" from 1 April 2027.
- `ab2026__package_business_rates_rhl_sbrr_and_transitional_support` (2 rows): Table 6.1 lines 13 and 14, the three bullets of paragraph 3.22 (SBRR thresholds; the real-terms freeze; the SSB extension), to which paragraph 3.23's "As a result of this package" refers. The red book doesn't say whether paragraph 3.21's pubs relief (line 12) also counts.
- `ab2026__package_pubs_relief_35pc_total` (1 row): the whole 35% business rates relief for pubs, social clubs and live music venues in England. It adds the 15% announced in January 2026 (paragraph 6.189; no AB2026 Table 6.1 line) to Table 6.1 line 12's further 20ppt. Paragraph 3.21: "Taken together, this relief is a tax cut worth an average of over £3,000 per pub next year." We don't use line 12's key, since line 12 covers only the 20ppt (rule 3; review A's RB-3).
- `ab2026__package_regulation_tariff_and_sandbox_business_savings` (1 row): the executive summary's "almost £800 million per year through further cuts to the administrative burdens of regulation, extending suspensions on tariffs, and introducing new cross-economy powers so firms can safely test new technologies faster". We scope the key across Table 6.1 line 16 (business tariff suspensions) and measures that have no Table 6.1 line.
- `ab2026__regulatory_administrative_savings` (5 rows): no Table 6.1 line. It covers the Chapter 6 decision "Regulatory administrative savings" (paragraph 6.36) and paragraph 4.52's "up to an estimated £640 million per annum of new gross administrative savings for business". We stage its £290 million, £116 million and £105 million parts as components.
- `ab2026__rolls_royce_gas_turbine_programme` (1 row): HM Treasury names no Table 6.1 line. Paragraph 4.80: "co-investment in a joint, 10-year, £2.5‑billion programme for next-generation gas turbine technologies for civil and defence aerospace"; in paragraph 4.83 HM Treasury says it "has not been contracted".
- `ab2026__package_defence_investment_plan` (1 row): the Defence Investment Plan published in June 2026, which no single line covers; HM Treasury puts its savings and funding in lines 40–42. Paragraph 5.34: "The Defence Investment Plan will create approximately 60,000 new jobs by 2029‑30 compared with 2023‑24." In the OBR family we stage the row on this key (paragraph 3.3's £1.8 billion a year) as the plan's RDEL funding part, a component (review A's K-2).
- `ab2026__package_dwp_fraud_and_error_measures` (1 row): the "new measures" of paragraph 5.17, "expected to save an additional £1.4 billion over the forecast" (2026-27 to 2031-32). The red book doesn't list them.
  - HM Treasury makes paragraphs 6.19–6.22 line 47's own package (its footnote 4; Policy Costings pp.54–58, which we key as line 47 components in `uk_hmt_costings`).
  - But the £1.4 billion reconciles with no printed basis for line 47. HM Treasury prints +600m on Table 6.1 line 47 over the forecast, and +940m with Table 6.2 line 9's +340m, and the costings sum to +570m. So we keep the figure off line 47's key (rule 3; review A's RB-8).
- `ab2026__package_welfare_fraud_and_error_savings_in_forecast` (1 row): this Budget's new fraud and error measures plus those already in the forecast. Paragraph 5.17: "bringing total savings from fraud and error to over £20 billion over the forecast". HM Treasury doesn't say which earlier measures count. We proposed the key as `ab2026__package_parliament_welfare_fraud_and_error_savings`; review A suggested dropping "parliament" from the name, and tranche 2 renamed it when it registered the key.
- `ab2026__package_barnett_consequentials` (4 rows): the Barnett consequentials of "decisions confirmed at Budget", 2026-27 to 2029-30, excluding the technical reduction from lower employer pension contributions (paragraph 4.150).
  - We scope the key across Table 6.1's England spending lines, and HM Treasury prints no line of its own for it.
  - We mark the three-government £1.3 billion `row_type: total`, and the Scottish, Welsh and Northern Ireland figures as components, one per government. In `uk_devolved_govts` we type the Welsh Government's own figures as Welsh Government components of this key.
  - On all four rows we say "positive = increase in devolved government funding" (review A's K-7(b)).
- `ab2026__mod_counter_fraud_strategy` (1 row): no Table 6.1 line. Paragraph 5.32: "a new Counter Fraud Strategy in November, with investment in fraud and error analytics and closer working with the Public Sector Fraud Authority set to deliver £250 million of benefits".
- `ab2026__state_pension_triple_lock_adjustment` (2 rows): no Table 6.1 line (its savings fall after the forecast). Paragraph 5.23: "adjusting the Triple Lock from April 2030 so that the State Pension rises each year by the highest of 2.5%, inflation, or the amount required to maintain its value relative to earnings as reached in April 2029"; DWP made the estimate (footnote 61).
- `ab2026__package_hmt_distributional_budget_2026` (1 row): HM Treasury's own grouping, the Budget 2026 policies it models in Impact on households (paragraph 1.4). It covers Table 6.1 lines 2, 3, 4, 5, 8, 11, 15, 26, 39, 49, 52, 59, 60, 61, 62, 72 and 95, plus the private landlord registration fee, which has no line. "Decisions announced at Budget 2026 (including those pre-announced where funding is allocated at Budget 2026)". HM Treasury leaves out line 1, the Household Energy Payment.
- `ab2026__package_hmt_distributional_since_ab2024` (1 row): HM Treasury's own grouping, the modelled policies and public service settlements "announced from Autumn Budget 2024 onwards up to and including Budget 2026" (paragraph 1.8). It covers the lines above plus earlier events' measures, which Table 6.1 doesn't list.

The coordinator set shared spellings, and no kept row has the scope of `ab2026__gas_standing_charge_moved_to_unit_rates`, `ab2026__pwlb_debt_relief_councils_severe_distress`, `ab2026__private_landlord_register_fee_65`, `ab2026__british_business_bank_defence_commitments_accelerated` or `ab2026__package_household_energy_payment_and_electricity_vat`. We dropped the rows on those subjects as design:
- the £108 current gas standing charge and the end-2027 delivery date (parameters);
- the £500 million and £200 million of PWLB debt relief (allocations to two councils, which Table 6.1's footnote 2 excludes as adding nothing to borrowing);
- the £65 fee (a parameter);
- the "up to £5 billion" NWF and BBB defence commitment (an investment total).

No red-book figure covers exactly lines 1 and 2, or exactly lines 1, 2 and 3 (`ab2026__package_household_energy_vat_and_fuel_duty`).

## Quantity and baseline proposals

- **Proposed metrics:**
  - fiscal aggregates (restated): `government_borrowing`, `government_borrowing_change`, `government_debt`, `government_net_worth`, `fiscal_balance`, `fiscal_balance_change` (also Chart 1.6's three bridge steps, which change the stability rule's headroom, i.e. the 2029-30 current budget), `debt_interest_change`, `fiscal_consolidation_share`; `block_grant_effect` (AB2025 list);
  - household and business effects:
    - `household_tax_change` (AB2025 list; worked cases);
    - `average_cumulative_gain` (multi-year savings);
    - `aggregate_household_saving` (AB2025 spelling; consumer savings);
    - `bill_change_percent` (business electricity bills);
    - `gross_earnings_change` (AB2025 spelling);
    - `business_cost_saving` (administrative savings to business; replaces `operating_cost_change`, which the enum defines as an official operating-cost line);
    - `housing_supply_change` (the 20,000 additional homes);
    - `jobs_created_or_supported` (the NWF's 100,000, the BBB's 40,000, Rolls-Royce's 3,300 and the DIP's 60,000; we don't use `affected_count`, which counts individuals affected, for jobs; review A's RB-9);
  - shares with exact meanings: `unaffected_share` (the share printed as unaffected), `share_with_zero_liability` (half of RHL properties paying no rates), `share_in_non_gaining_deciles`, `share_in_net_recipient_deciles`, `income_mobility_share`, `share_in_top_half_of_expenditure` (Impact on households context).
- **Proposed units:** `businesses` (15 rows), `dwellings` (1).
- **Proposed baselines:** `hmt_no_budget_2026_modelled_policies` (paragraph 1.6, "a counterfactual in which the modelled policies were not introduced") and `hmt_no_policy_changes_from_ab2024_through_ab2026` (paragraph 1.8, "a counterfactual in which the modelled policies and spending settlements were not introduced"), one row each. We set `baseline_policy: null` on the other rows.

## Not staged (rules 8 and 9)

In the rework we dropped 1,267 of the first staging's 1,699 rows, and with review A's fixes we dropped 7 more (4 November), so we don't stage 1,274 rows. We retired the first staging's proposed keys that named only dropped rows. We can't check how many there were, because neither branch's history includes the first staging, so we give no number.

| Category | Rows | Examples (locator) |
|---|---:|---|
| A. Measure parameters: rates, thresholds, payment amounts, dates, durations; worked-example inputs | 829 | 817 former `policy_parameter` rows, e.g. "£13.21" per hour (para 3.18), "£2,500" surplus earnings threshold (Impact on households para 1.4), "£13,319" withdrawal threshold (explainer FAQ). Also the £100 Household Energy Payment amount (4 rows, e.g. para 2.48); the £108 current gas standing charge (para 3.9); the £2,000 rise in the full new State Pension over the Parliament (para 5.23); six worked-case inputs, e.g. Tom's "£10,300" income. |
| B. Spending allocations: programme funding, capitalisations, investment totals, spending levels | 221 | 166 programme amounts that match no Table 6.1 line's printed impact (table above), e.g. "£120 million" for the AI Security Institute (para 4.130), "£30 million" for Cardiff Parkway (para 4.157), "£1.5 billion" for the Social and Affordable Homes Programme (para 5.4); 46 investment totals, e.g. NWF "£15.4 billion" (para 4.44), Your First Home "£4.7 billion" (para 5.5); public sector net investment (Table 1.2, 6); departmental spending levels (2); £200 million of private AI model credits (para 4.132). |
| C. Financing: DMO remit, gilts, Treasury bills, NS&I, cash requirements, financial transactions | 177 | DMO net financing requirement "£258.6 billion" (Annex A.8); Table A.1 gilt sales by maturity; CGNCR "£144.1 billion" (para 1.47); Table 1.4 financial transactions by programme, e.g. Student Loans "15.9" (55 rows); Sovereign AI "£60 million" (para 4.135). |
| D. Contingent liabilities | 14 | Table 1.5, e.g. Department for Energy Security and Net Zero "1.2-1.7"; Total reasonable worst case "4-4.5". |
| E. Programme inputs, scope counts and targets | 25 | "670" HMRC compliance officers to recruit (paras 2.42, 6.151); tariffs on "over 100" food products (para 3.17); "around 10,000" homes the Social and Affordable Homes Programme funds (para 6.114); the 25% administrative-burden target worth "£5.6 billion" (para 4.51); "over 90% of England's population will have a devolution agreement in place" (para 4.68), a coverage count that includes existing agreements (review A's RB-7, dropped 4 November). |
| F. Effects of policies outside this Budget | 3 | "more than 100" businesses using the Global Talent funder pathway since Budget 2025 (para 4.112); "over £5 billion" of services exports from the Switzerland and South Korea deals (para 4.124); "over £2 billion of net progress secured" against the administrative-burden target (para 4.51), progress before this Budget (footnote 137 cites a July 2026 annex; para 4.52 counts this Budget's £640 million separately; RB-7). |
| G. Repeats beyond two of one claim | 4 | The Household Energy Payment's "£2.6 billion" in para 3.5 and Box 3.A, and "up to 20 million households" in para 3.3 and Box 3.A. Kept: the £2.6 billion of the executive summary and para 2.48, and the 20 million of the executive summary and paras 2.48 and 3.5 (review A's RB-2; see Review A fixes). |
| H. The rework brief's drop list | 1 | Impact on households para 1.10's "over four times as much in public spending than they pay in tax" (`spending_to_tax_ratio`, which the brief's item 1 names for removal; RB-13). Row 365's 60% beside it stays as a printed value. |

Under rule 9 we moved 74 kept rows from proposed keys to a Table 6.1 line's key:
- the 66 Table 6.3 item cells and the 160,000 employees (from proposed keys such as `ab2026__package_tax_gap_timely_payment`; now line 45 components);
- four food-tariff savings (now line 10 components);
- the £3 billion and £1.7 billion DIP parts (now line 41 components);
- the Your First Home count (now line 37).

We keep one row off a line's key: the £1.4 billion of DWP fraud savings, which reconciles with no printed basis for line 47 (rule 3; see its package key, `ab2026__package_dwp_fraud_and_error_measures`).

### Other material not staged

- **Tables 6.1, 6.2 and 6.4:** we stage these in `uk_hmt_tables`. HM Treasury prints Table 6.3 as a separate breakdown, and we stage it here.
- **No Impact on households bar readings** (README rule 4). HM Treasury prints no data labels on Figures 1.A–1.E, and we stage Chart 1.6's six data labels.
- **Words without numbers:** we don't turn "hundreds of pounds a month" or "thousands of jobs" into numbers.
- **Footnote 73's earlier-event yields** (£6.5 billion, over £1 billion, £2.4 billion): HM Treasury gives them for other fiscal events' measures, and we stage only this Budget's £2.3 billion and the £12 billion total.
- **Background:** we don't stage macro forecasts that score no measure (GDP growth, inflation, employment, Table 1.1), departmental efficiency histories, Annex B budgets or Annex C charts.
- **The abbreviated 29 October explainer:** HM Treasury gives no quantitative content in it.
- **Other figures not staged (review A's RB-20(c)):**
  - paragraph 5.17's Motability saving "over £1 billion over the next five years" (no Table 6.1 line);
  - paragraph 3.7's £150 from Budget 2025 (an earlier event's measure);
  - paragraph 4.36's reprioritisation savings (spending allocations);
  - paragraph 4.42's National Wealth Fund and British Business Bank outcomes to date (effects before this Budget);
  - paragraph 6.9's £150 million (an allocation).
- **Paragraph 1.38:** HM Treasury repeats the OBR's 0.1 percentage point CPI effect there; in row 185 we stage paragraph 3.2's.

## Judgement calls for the coordinator

- **We dropped `spending_to_tax_ratio` (review A's RB-13).** In the 3 November finish we kept paragraph 1.10's "over four times" as a distributional statement. Review A read the rework brief's item 1 as a named removal list whose only exception is a Table 6.1 cost or yield. Neither primary prints another spending-to-tax ratio, so the list can only mean this row, and HM Treasury frames paragraph 1.10 as "context beyond the impact of recent government policy decisions". We dropped the row (category H). We keep the 60% row beside it, Table 2.C and the other Impact on households context rows as printed values.
- **Mislabelled shares beyond the 84%.** We stage the 84% as `unaffected_share`, never 16%. BADR's "three-quarters … will still receive relief on their entire gain" gives the unaffected share too. "half of all RHL properties … will not pay business rates at all" includes properties already paying none (`share_with_zero_liability`). Impact on households' 20%, 60%, 59% and approximately 20% don't give affected shares (proposals above). The registry defines `share_no_change` as a household-income measure, so for the 84% of income tax payers we follow the brief's `unaffected_share`.
- **Registered metrics replace AB2025-era proposals.** For the four "around £50 off the annual Ofgem price cap" rows and the three energy-debt "£30" rows we now use the registered `energy_bill_change` (unit `gbp_per_household`), which the enum mints for HM Treasury bill figures. For the India agreement's GDP effects we use `gdp_level_effect` in GBP (the AB2025 IPPR precedent).
- **We dropped financial transactions and public sector net investment as financing and spending levels.** In Table 1.4 HM Treasury prints forecast levels of lending by programme, not Budget effects. The OBR produces public sector net investment as an aggregate, but the brief lists `public_investment_share` for removal.
- **We keep jobs and induced homes, and drop delivery targets.** We stage the estimated jobs (NWF 100,000; BBB 40,000; Rolls-Royce 3,300; DIP 60,000; proposed `jobs_created_or_supported` since review A) and Your First Home's "estimated 20,000 new homes" as estimated effects. We treat the 10,000 homes the Social and Affordable Homes Programme funds (in line 35's title), robotic procedures rising to 500,000, 2,000 learners and the infrastructure pipeline's 650,000 workforce requirement as delivery targets of allocations.
- **We now mark the BBB's 40,000 jobs `restated`.** In footnote 135 HM Treasury cites the British Business Bank's press release. We mark the NWF's 100,000 `restated` too (footnote 134 cites the National Wealth Fund's own statement).

## Printed problems and differences

- **Spending figures that differ from Table 6.1:**
  - Social and Affordable Homes Programme: £1.5 billion (paras 5.4, 6.114) against line 35's -1,750 over 2027-28 to 2030-31.
  - Early years books: "£5 million a year for three years from 2027-28" (paras 3.20, 6.122) against line 9's -5 in 2026-27, 2027-28 and 2028-29. The amounts agree; the years don't.
  - Local apprenticeship services £100 million (line 22: -120);
  - Good Growth Funds £285 million in 2027-28 (line 20: -340);
  - Strategic Authorities £150 million (line 25: -180);
  - Union Learning Fund £15 million a year (line 73: -20 a year);
  - Sovereign AI £60 million (Table 6.2 line 4: -45 a year).
  - DWP fraud and error: "an additional £1.4 billion over the forecast" (para 5.17) against line 47's +600m in total (+940m with Table 6.2 line 9; the Policy Costings' +570m).
- **Regulatory savings target:** HM Treasury prints "£5.6 million" in paragraph 6.36 and "£5.6 billion" in paragraph 4.51. It gives different printed scopes to the executive summary's "almost £800 million per year" and paragraph 4.52's "up to … £640 million per annum", and we keep both.
- **Repeated amounts that disagree (not staged after rule 8):**
  - local AI partnerships £30 million (para 4.135) and £15 million (para 6.101);
  - Leeds College of Building £28 million (para 4.71) and £15 million (para 6.53);
  - business tariff suspensions on 269 goods (para 3.28), 350 goods (para 4.147) and 361 extensions plus 72 new suspensions (line 16's title).
- **Pubs relief:** HM Treasury writes the extra relief as "20%" in the text and as "20ppts" in Table 6.1.
- **Table 1.3:** HM Treasury labels the new forecast "November 2026 forecast" in an October Budget. In Chart 1.6 it prints 14.5 where the text says £15 billion. Its "Debt is lower at the end of the forecast" fits public sector net financial liabilities (83.2% to 81.7%), while public sector net debt goes from 95.5% to 95.6%.
- **Paragraphs 6.225 and 6.226:** HM Treasury repeats the Machine Games Duty measure. In Annex A footnote 181 it points to A.17 for green gilts, which A.19 covers.
- **Pension Tax Allowance explainer:** in the FAQ HM Treasury prints "£13.319" for £13,319. It prints both £13,036.40 and the rounded £13,037, and "up to £94" beside Steph's £93.28. In the 28 October version's FAQ it repeats a question and prints "part-time wok". In the version it republished on 29 October (`83f8c894…`) it fixes both and still prints "£13.319".

## Verification

- **Checker.** `PYTHONPATH=. uv run -q python pipeline/ab2026_harvest_contract.py sources/harvest-uk-ab2026-2026-10-29/uk_hmt_redbook` reports 425 rows, 0 problems (4 November, after review A's fixes, with the coordinator's tightened checks).
- **Determinism.** Two runs of `stage.py` write the same `claims_staged.jsonl.gz` and an unchanged `manifest.jsonl`. COUNTS.json pins the gzip's sha256.
- **Spot check (the rework's, 29 October; row numbers are the rework's, which held at 4f424b9).** The rework drew 30 rows with `random.Random(20261029).sample(range(432), 30)` (0-based row numbers) and re-opened each at its locator in the hashed primaries. It extracted red-book and Impact on households pages with `pdftotext -layout -f N -l N`, and read table cells against the printed row and column. All 30 match on value, sign, unit and period.

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

The rework stopped before its report, so on 3 November we checked each instruction of `briefs/rework-hmt-redbook.md` (on the staging branch) against the rows:

- **Removed metrics.** No `policy_parameter` row remained. Of the nine allocation and financing metrics, only `spending_to_tax_ratio` remained, on one row (paragraph 1.10's "over four times"). We kept it then as a distributional statement printed in Impact on households, which item 3 of the brief keeps, not the fiscal aggregate the drop list targets. See the judgement calls above.
- **Rule 9 and the "Also fix" section.** We stage the 84% row as `unaffected_share`, as printed. We key no row to `ab2026__package_tax_gap_timely_payment`, and key line 45's items to line 45 as components. We name no measure without a Table 6.1 line as a package. No kept row has the scope of the coordinator's shared spellings (see "Keys we proposed").
- **`component`.** Six rows still used `component` for a chart bar, and we moved them to `chart_bar`.
- **Stale files.** We found no REPORT.md or spot-check files left in the family.
- **Keys.** The coordinator harmonised keys across families on 3 November; `stage.py`'s `KEY_MAP` lists each rename, and the keys we proposed (above) give the final spellings.
- **Checker:** 0 problems. **Determinism:** when we re-ran `stage.py` it reproduced the gzip and manifest byte for byte.
- **Spot check: not repeated.** The brief asked for 15 random rows re-opened at their locators. The 3 November session's network policy refused gov.uk and assets.publishing.service.gov.uk (HTTP 403 at the proxy), so we fetched no primary and re-opened no row. The 30-row check above is the rework's own; nobody independent has checked this rework yet.

## Key harmonisation, 3 November 2026

The coordinator gave each scope one key across families (tranche 1, task 3.4), and renamed these keys in this family:

- `ab2026__package_obr_forecast_policy_effects` → `ab2026__package_government_decisions_since_march_2026`
- `ab2026__package_budget_barnett_consequentials` → `ab2026__package_barnett_consequentials`
- `ab2026__defence_investment_plan` → `ab2026__package_defence_investment_plan`

The OBR prints the same figures in its Table 3.1 "Total effect of Government decisions" as HM Treasury does in Table 1.3's "Total effect of policy decisions" (2.1 in 2028-29 in both). So the red book's restatement shares the OBR family's key. We name the Barnett key for the scope the Welsh Government's figures share (£450 million here, £448m there). The Defence Investment Plan crosses Table 6.1 lines 40–42, so we key it as a package, shared with the OBR's DIP funding row. We keep Table 1.3's Tax and Spending parts as components of the total, as staged.

## README rule 10, 3 November 2026

We had already put Table 1.3's total effect of policy decisions and its tax and spending parts (18 rows) on `decisions_effect_on_borrowing`, and proposed `fiscal_balance_change` for its two memo lines on the current budget deficit (11 rows). The memo rows' sign convention named PSNB, so `stage.py` now states which way the current budget deficit moves on rows 138–142 (underlying forecast differences) and 161–166 (policy decisions). We changed no value or sign. The contract checker reports 432 rows, 0 problems, and when we re-run `stage.py` it reproduces the gzip byte for byte.

## Review A fixes, 4 November 2026

Review A (issue comment 6635870934 on #231, at 4f424b9) approved this family with fixes. `stage.py` applies each as an explicit, commented step after the rows, indexed by 4f424b9's row numbers, and drops rows only at the end. We give 4f424b9's row numbers in this section too, as in the review. Dropping seven rows moves every later row up to seven places earlier in the staged file (row 365 here becomes row 359 there). We re-opened no primary for this round; every new quote and value comes from the review or the row. The coordinator then finished RB-18 and RB-19 from two pinned primaries (below). 432 rows → 425; `own` 263 → 257, `restated` 169 → 168; 6 hashed primaries.

- **RB-1:** we put paragraph 5.17's two totals "over the forecast" (rows 265 and 266) at 2031-32 with the forecast's horizon. We marked row 265 `cumulative`, kept `range_low` on row 266 and marked row 267 `point_in_time`.
- **RB-2:** we dropped rows 191 and 200 (the £2.6 billion's third and fourth printings) and dated row 179 2026-27. Under the same rule we dropped rows 188 and 201, which repeat "up to 20 million" in paragraph 3.3 and Box 3.A. Once RB-11 put rows 180 and 201 in England, four rows shared one claim identity, and the coordinator's new duplicate-claim check, H-3, rejects more than two.
- **RB-3:** we moved row 226 to `ab2026__package_pubs_relief_35pc_total`.
- **RB-4:** for Chart 1.6's bridge steps (rows 21, 22, 24) we propose `fiscal_balance_change` with the stability rule's sign, and key row 24 to the government-decisions key. On all six rows we name the stability rule, and on rows 20, 23 and 25 their forecast vintage and policy scenario.
- **RB-5:** we made row 246 a line 29 component (retiring its proposed key), rows 232–237 line 14 components and row 254 a line 77 component.
- **RB-6:** in rows 219–220's component we say it contains rows 217–218.
- **RB-7:** we dropped rows 247 and 252 (the coordinator's call), with their one-row keys `ab2026__package_parliament_regulatory_burden_reduction` and `ab2026__english_devolution_agreements`, and list them under categories F and E.
- **RB-8:** we rewrote the DWP fraud key's scope and row 265's note, and marked rows 265–266 `hmt_published_estimate_method_unspecified`.
- **RB-9:** we propose `jobs_created_or_supported` for rows 245, 246, 253 and 268, mark row 245 `restated`, and mark rows 253 and 268 `hmt_published_estimate_method_unspecified`.
- **RB-10:** we dated rows 11 and 240 2027-28 ("per year from 2027-28"), and marked rows 6 and 11 `hmt_costing_obr_certified`.
- **RB-11:** we corrected the geography on rows 5, 8, 9, 14, 180, 190, 196–199, 201–205, 258, 269 and 275, and write "Great Britain" as `GB` throughout (the harvest's closed list).
- **RB-12:** we fixed rows 30–39's sign conventions, and marked rows 30, 31, 34, 35, 36 and 38 as ONS outturns (`administrative_data`, `administrative_fact`).
- **RB-13:** we dropped row 366 (category H).
- **RB-14:** we record the republished explainer as a 0-row primary (manifest line 6).
- **RB-15:** we gave repeats one dating (rows 9, 10, 14, 196, 205, 248–251, 271, 273), and moved rows 0, 19, 215 and 244 to the multi-year convention.
- **RB-16:** we set rows 143–166's `reform_hint` to "Total effect of policy decisions".
- **RB-17:** we gave rows 185, 216, 226 and 237 conventions `signs.py` reads. Row 185 keeps its key, with the three scopes in its bullet, and we stage row 182 as 0.84 `share`.
- **RB-18:**
  - We mark rows 33 and 37 as HM Treasury's own arithmetic.
  - Rows 6, 7, 8, 10, 11, 12 and 14 take their repeats' source models. Row 5's and row 9's repeats already used `arithmetic`, and row 13 has no repeat and keeps its label.
  - We stage row 222 as a worked example (`arithmetic`, with its subgroup), and row 183 as `decile_10`.
  - We dated row 184 2027-28, at medium confidence, `hmt_published_estimate_method_unspecified`. We removed `presentation` from row 168, and marked row 267 `hmt_published_estimate_method_unspecified`.
  - In row 194's note we give footnote 84's "fuel stressed" definition, which the coordinator read from the red book (19b337ac…).
- **RB-19:** rows 15, 29, 41 and 42 now quote only their sentence, and rows 103, 104 and 167 drop their leading paragraph numbers. We corrected the locators of rows 172, 190, 227, 248 and 249. Rows 365 and 368 quote their whole sentences, which the coordinator read from Impact on households (36cd5afb…). Row 365's sentence includes the lead-in that dates para 1.10's bullets to 2028-29 (we dropped row 366).
- **RB-20:** (a) We removed the unverifiable "234 proposed keys" figure. (b) Our spending test now reads "the per-year amount equals the line's", which rows 224 and 276 pass, so we keep them. (c) We list five more figures under "Other material not staged".
- **RB-21:** we matched this lane folder's gzip and NOTES to #231's, and set `metric: null` explicitly on the 40 proposed-metric rows. We left Table 6.3's duplication of Table 6.1 lines 45 and 46 (`uk_hmt_tables`) to tranche 2. At ingest we drop rows 339–350, which repeat those lines, as twins of `uk_hmt_tables` rows 264–275, and record each under the kept claim's `publication.also_printed_in`.
- **K-7(b):** we made row 258 the Barnett `total`, and gave rows 258–261 the sign convention.
- **K-7(c):** row 222 already proposes `gross_earnings_change`, the AB2025 spelling, so we made no change.
