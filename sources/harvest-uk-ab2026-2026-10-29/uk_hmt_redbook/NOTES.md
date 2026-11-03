# uk_hmt_redbook: Autumn Budget 2026 red book, Impact on households and Pension Tax Allowance explainer

**Working files.** `stage.py`, which writes this family's two data files and is the file meant wherever these notes say `stage.py`, lives on branch `uk/ab2026-harvest-staging` at `harvest-staging/ab2026/lanes/hmt-redbook/uk_hmt_redbook/stage.py`; this branch carries only NOTES.md, `manifest.jsonl` and `claims_staged.jsonl.gz`. `.ab2026-primaries/uk_hmt_redbook/` was the lane's local primaries folder and was never committed: the repository carries no primary bytes, so fetch each primary from its `manifest.jsonl` URL and check its sha256.

Source `hm_treasury`. **432 rows from 3 cited primaries (5 hashed versions), 23 proposed measure keys.** `stage.py` embeds every row and manifest line as data; `python3 stage.py` rewrites `claims_staged.jsonl.gz` and `manifest.jsonl` byte for byte with the standard library alone. No primary bytes are vendored.

The first staging (29 October, morning) produced 1,699 rows and 250 proposed keys. This rework applies README rules 8 and 9: it keeps estimates of effects, drops design (parameters, allocations, financing, contingent liabilities), and gives each printed part of one Table 6.1 measure that measure's key. The section "Not staged (rules 8 and 9)" accounts for all 1,267 dropped rows.

## Primaries

| Primary version | SHA256 | Bytes | Access | Rows |
|---|---|---:|---|---:|
| Budget 2026 (HC 726), 28 October version | `bed70546c026487e3141799968f6df08210c182b0695fed0e8adf7efd6697e03` | 4,657,025 | local copy | 0 |
| Budget 2026 (HC 726), current version | `19b337aced8fe47de1d6ee462dabf75155110d347c38123b6380d90f09e97b93` | 4,679,545 | direct | 363 |
| Impact on households: distributional analysis to accompany Budget 2026 | `36cd5afb4fceca2cecba0d065974ffe8280888e15ed852c129339439e539469c` | 197,606 | direct | 57 |
| Pension Tax Allowance Explainer (content API, full body) | `cc3ec22eb55f4c827c301bc67b06aa7482e4970ef7e1cec644bc382dac0dbb25` | 24,883 | govuk_api | 12 |
| Pension Tax Allowance Explainer (content API, 29 October abbreviated body) | `791d2573bafc67fcfd89567dab55c0239dd26febc9feec44d10f2be4ae21a9e4` | 9,816 | local copy | 0 |

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

## Coverage

Rows run in document order: red book (printed page, then position), Impact on households, Pension Tax Allowance explainer.

- **Red book (363 rows):**
  - 160 fiscal aggregates restated from the OBR, ONS and IMF: Chapter 1 text, Chart 1.6's six data labels, Tables 1.2 and 1.3;
  - 84 cells of Table 6.3, which breaks Table 6.1 line 45 into eleven items, with its subtotal, the line 46 memo and the subtotal including memo;
  - 30 costs, yields and savings: Table 6.1 measures where the red book prints the line's own Exchequer impact, printed parts of those lines, and saving estimates with their own scopes;
  - 89 effects on people and businesses: counts affected; gains, losses and bill changes; GDP, earnings, price and jobs effects; Barnett consequentials.
- **Impact on households (57 rows):** the distributional and context statements of paragraphs 1.7, 1.9, 1.10, 2.4, 2.5 and 2.10, and the 50 cells of Table 2.C.
- **Pension Tax Allowance explainer (12 rows):** three pensioner counts and nine worked-case outcomes.

Rows by measure key:

| measure_key | rows | of which components (rule 9) |
|---|---:|---:|
| `null` with a proposed key | 67 | 18 |
| `null`, context (no proposed key) | 191 | 0 |
| `ab2026__hmrc_tax_gap_package` | 73 | 67 |
| `ab2026__household_energy_payment_100_bands_a_to_d` | 12 | 0 |
| `ab2026__pension_tax_allowance` | 12 | 0 |
| `ab2026__british_industrial_competitiveness_scheme` | 8 | 0 |
| `ab2026__business_rates_rhl_transitional_support` | 6 | 0 |
| `ab2026__business_rates_sbrr_rhl_thresholds_raised` | 6 | 0 |
| `ab2026__online_marketplace_liability_uk_businesses` | 6 | 0 |
| `ab2026__electricity_vat_zero_rate_to_july_2027` | 5 | 0 |
| `ab2026__alcohol_duty_small_producer_relief` | 4 | 0 |
| `ab2026__food_and_heating_oil_tariff_suspensions` | 4 | 4 |
| `ab2026__mileage_allowance_payments_55p` | 4 | 0 |
| `ab2026__uk_india_ceta_and_double_contributions_convention` | 4 | 3 |
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
| `ab2026__business_rates_pubs_relief_35pc` | 1 | 0 |
| `ab2026__carbon_price_support_removed` | 1 | 0 |
| `ab2026__carers_allowance_earnings_taper` | 1 | 0 |
| `ab2026__hgv_ved_1_for_12_months` | 1 | 0 |
| `ab2026__national_wealth_fund_capital` | 1 | 0 |
| `ab2026__parental_allowance_fathers_partners_adopters` | 1 | 0 |

The 191 context rows carry no proposed key (README rule 2): 136 restated fiscal aggregates about no measure, and 55 Impact on households rows (Table 2.C and the context statements of paragraphs 1.10, 2.4, 2.5 and 2.10). The other 24 Table 1.3 rows, the OBR's effect of policy decisions, carry `ab2026__package_government_decisions_since_march_2026`.

Rows by metric:

| metric | rows |
|---|---:|
| `revenue_change` | 114 |
| `income_statistic` | 52 |
| `affected_count` | 38 |
| proposed `government_borrowing` | 28 |
| proposed `government_debt` | 25 |
| proposed `fiscal_balance` | 21 |
| proposed `government_borrowing_change` | 20 |
| `decisions_effect_on_borrowing` | 18 |
| `fiscal_headroom` | 17 |
| proposed `fiscal_balance_change` | 13 |
| proposed `government_net_worth` | 9 |
| `energy_bill_change` | 7 |
| proposed `business_cost_saving` | 7 |
| proposed `debt_interest_change` | 7 |
| proposed `household_tax_change` | 7 |
| proposed `average_cumulative_gain` | 5 |
| `affected_share` | 4 |
| `gdp_level_effect` | 4 |
| `tax_liability` | 4 |
| proposed `aggregate_household_saving` | 4 |
| proposed `bill_change_percent` | 4 |
| proposed `block_grant_effect` | 4 |
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
| proposed `spending_to_tax_ratio` | 1 |

Attribution: 263 rows `own`, 169 `restated` (OBR, ONS, IMF, DWP, DBT, the British Business Bank).

## Conventions

- **Values as printed.** `value_raw` is the printed string, and `value` scales it to the unit (£ million × 1e6, £ billion × 1e9; percent stays percent; words such as "three-quarters" become fractions with unit `share`). Bounds keep the printed qualifier: "over" and "more than" are `range_low`, "up to" is `range_high`, "around" is `point`.
- **Sign.** Values are never re-signed. `conditions.sign_convention` states each row's direction in the phrasing `scorecard_db/signs.py` reads:
  - Exchequer costs: "positive = cost to the Exchequer (as printed; not re-signed)";
  - savings: "positive = saving to the Exchequer";
  - yields, including Table 6.3: "positive = yield to the Exchequer (reduces borrowing)";
  - Table 1.3: "positive = increase in PSNB" (the opposite of Table 6.1's yield convention), except on its two memo lines, which give the change in the current budget deficit: "positive = increase in current budget deficit" (README rule 10, since 3 November);
  - Table 1.2: deficits and debt positive, surpluses negative, as printed.
- **Periods.** Fiscal-year figures carry `conditions.fy`, end-year `period` and `time_basis: fiscal_year`. A multi-year total keeps its whole horizon in `conditions.horizon`, sits at its final fiscal year and is never annualised. An undated figure ("by the late 2030s", "this winter") sits at the publication year 2026 with the printed horizon in conditions and, where the year matters, `parse_confidence: medium`.
- **Prices.** Every money figure is cash, as printed; Table 1.3's rows carry `price_basis: current prices`. No basis is converted. (The first staging tagged the £595 million administration saving `real terms`; paragraph 2.14's "real terms" belongs to the Spending Review's 16% cut, and the £595 million equals Table 6.1 line 63's cash +595.)
- **"Central".** HM Treasury prints single estimates; `point` means the printed figure. No row is an inferred scenario. The one OBR scenario row (borrowing £12 billion lower if energy prices follow a lower path) carries `conditions.scenario`.
- **Rule 9 components.** A printed part of one Table 6.1 measure carries the line's key, `conditions.component` naming the part and `conditions.row_type: measure_component`. Components are never summed with the line's total. This family has 94: the 66 Table 6.3 item cells and the 160,000 employees (line 45); the £3 billion and £1.7 billion parts of line 41's £4.7 billion; the two food-tariff consumer savings (line 10); the Scotland, Wales and Northern Ireland GDP effects of the India agreement (line 77); and, under proposed keys, the Tax and Spending parts of the OBR's policy effect, the three devolved Barnett consequentials and three parts of the regulatory administrative savings.
- **`component` means a part only.** Where the first staging used `component` for a Chapter 6 paragraph title on a whole-measure row, the condition is now `paragraph_heading`; in the pension worked cases it is `quantity`. Chart 1.6's six headroom-bridge data labels name their bar in `chart_bar` (changed on 3 November; the rework had left them under `component`).
- **Attribution.** OBR forecasts are `restated` with source model `obr_efo_forecast`; ONS, IMF, DWP, DBT and British Business Bank figures are `restated` and their notes name the original. HM Treasury's own costings, counts and worked cases are `own`.

### Which spending figures stay (rule 8 exception)

A spending figure is a measure's design unless the red book presents it as the measure's Exchequer impact. The test applied: the figure stays when it equals the printed Table 6.1 line (from `uk_hmt_tables`) for the years the red book states, within the red book's rounding. Tax costs and yields, savings estimates and Table 6.3 stay regardless.

| Table 6.1 line | Red book | Table 6.1 prints (£ million) | Rows |
|---|---|---|---|
| 1 Household Energy Payment | £2.6 billion | -2,625 in 2026-27 | kept (4) |
| 9 Early years books | £5 million a year | -5 a year (2026-27 to 2028-29) | kept (2); years differ, see anomalies |
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

## Proposed measure keys (23)

Each key below is the whole scope of its rows, stated as Table 6.1 lines or "no Table 6.1 line", with the red book's words.

- `ab2026__package_government_decisions_since_march_2026` (24 rows): the OBR's "Total effect of policy decisions" on PSNB in Table 1.3, with its Tax and Spending parts (components) and the memo effect on the current budget deficit, 2026-27 to 2031-32. Crosses Table 6.1 lines 1–98 and adds the OBR's indirect effects; Table 1.3 footnote 1 says the OBR's EFO Table 3.1 explains the "Differences between the direct impacts of the policy measures as set out in Table 6.1 of the Budget, and how the OBR incorporate these into their forecast". Not `ab2026__package_total_policy_decisions`.
- `ab2026__package_hmrc_tax_gap_and_online_marketplace` (7 rows): exactly Table 6.1 lines 45 and 46. Table 6.3's "Subtotal including memo" (six years) and footnote 73's "£2.3 billion from this Budget": Table 6.3 prints +2,250m for lines 45 and 46 in 2029-30, against +1,980m for line 45 alone.
- `ab2026__package_parliament_tax_gap_measures` (1 row): lines 45 and 46 plus the tax-gap measures of Autumn Budget 2024, Spring Statement 2025 and Budget 2025 (footnote 73). Paragraph 2.46: "the total due to be raised from measures to close the tax gap announced during this Parliament to over £12 billion in 2029-30".
- `ab2026__package_property_and_savings_income_rates` (2 rows): exactly Table 6.1 lines 61 and 62. Paragraph 2.50: "84% of income tax payers will be unaffected by these changes"; "Around half of the revenue raised from this change is expected to come from the top 10% of households".
- `ab2026__package_breathing_space_for_households` (1 row): paragraph 3.2's "Government action at this Budget to provide breathing space for households", which the OBR expects to reduce CPI inflation by 0.1 percentage points in 2027. Crosses Table 6.1 lines; the red book lists none for this figure. Table 6.1 groups lines 1–11 under "Breathing space for families", and Box 3.A's "breathing space for households" names line 2 (the VAT cut) and line 1 (the Household Energy Payment).
- `ab2026__energy_debt_circuit_breaker` (3 rows): no Table 6.1 line. Paragraph 3.8: "a new debt strategy to address this and act as a circuit breaker on energy debt … via reforms to prevent debt building up and a one-off targeted debt relief scheme for eligible households".
- `ab2026__package_parliament_fuel_duty_decisions` (3 rows): Table 6.1 line 3 plus the fuel duty decisions of earlier events in this Parliament. Paragraph 3.13: "the government's decisions on fuel duty across this Parliament … compared with plans under the previous government"; footnote 98's baseline is the 5p cut reversed in April 2025 and annual RPI uprating.
- `ab2026__minimum_wage_uprating_april_2027` (2 rows): no Table 6.1 line (a regulation). Paragraph 3.18: "raising the National Living Wage and National Minimum Wages" from 1 April 2027.
- `ab2026__package_business_rates_rhl_sbrr_and_transitional_support` (2 rows): Table 6.1 lines 13 and 14, the three bullets of paragraph 3.22 (SBRR thresholds; the real-terms freeze; the SSB extension), to which paragraph 3.23's "As a result of this package" refers. The red book does not say whether paragraph 3.21's pubs relief (line 12) also counts.
- `ab2026__package_regulation_tariff_and_sandbox_business_savings` (1 row): the executive summary's "almost £800 million per year through further cuts to the administrative burdens of regulation, extending suspensions on tariffs, and introducing new cross-economy powers so firms can safely test new technologies faster". Crosses Table 6.1 line 16 (business tariff suspensions) with measures that have no Table 6.1 line.
- `ab2026__regulatory_administrative_savings` (5 rows): no Table 6.1 line. Chapter 6 decision "Regulatory administrative savings" (paragraph 6.36) and paragraph 4.52's "up to an estimated £640 million per annum of new gross administrative savings for business"; its £290 million, £116 million and £105 million parts are components.
- `ab2026__package_parliament_regulatory_burden_reduction` (1 row): no Table 6.1 line. Paragraph 4.51: the 25% administrative-burden target, "with over £2 billion of net progress secured" across this Parliament.
- `ab2026__package_bbb_equity_community_lender_and_venture_debt` (1 row): paragraph 4.46's "three measures": £1.4 billion of commercial equity commitments, £165 million for community lenders and £450 million for a venture debt product, which the British Business Bank's additional £5 billion of capacity enables. The red book does not map them to lines; the BBB's capacity sits in Table 6.1 line 29 (Table 6.2 line 3) and the Growth Guarantee Scheme in line 75.
- `ab2026__rolls_royce_gas_turbine_programme` (1 row): no Table 6.1 line named. Paragraph 4.80: "co-investment in a joint, 10-year, £2.5‑billion programme for next-generation gas turbine technologies for civil and defence aerospace"; paragraph 4.83 says it "has not been contracted".
- `ab2026__package_defence_investment_plan` (1 row): the Defence Investment Plan published in June 2026, which no single line covers; lines 40–42 carry its savings and funding. Paragraph 5.34: "The Defence Investment Plan will create approximately 60,000 new jobs by 2029‑30 compared with 2023‑24."
- `ab2026__english_devolution_agreements` (1 row): no Table 6.1 line. Paragraphs 4.67–4.68: "the final stages of agreeing 10 new devolution agreements", after which "over 90% of England's population will have a devolution agreement in place" (the 90% includes existing agreements).
- `ab2026__package_dwp_fraud_and_error_measures` (1 row): Table 6.1 line 47 plus the DWP fraud and error decisions of paragraphs 6.19–6.22, which have no lines of their own. Paragraph 5.17: "new measures expected to save an additional £1.4 billion over the forecast". Line 47 alone prints +600m over 2026-27 to 2031-32 (and Table 6.2 line 9 +340m).
- `ab2026__package_parliament_welfare_fraud_and_error_savings` (1 row): line 47's measures plus the fraud and error measures of earlier events in this Parliament. Paragraph 5.17: "bringing total savings from fraud and error to over £20 billion over the forecast".
- `ab2026__package_barnett_consequentials` (4 rows): the Barnett consequentials of "decisions confirmed at Budget", 2026-27 to 2029-30, excluding the technical reduction from lower employer pension contributions (paragraph 4.150). Crosses Table 6.1's England spending lines; no line of its own. The Scottish, Welsh and Northern Ireland figures are components.
- `ab2026__mod_counter_fraud_strategy` (1 row): no Table 6.1 line. Paragraph 5.32: "a new Counter Fraud Strategy in November, with investment in fraud and error analytics and closer working with the Public Sector Fraud Authority set to deliver £250 million of benefits".
- `ab2026__state_pension_triple_lock_adjustment` (2 rows): no Table 6.1 line (its savings fall after the forecast). Paragraph 5.23: "adjusting the Triple Lock from April 2030 so that the State Pension rises each year by the highest of 2.5%, inflation, or the amount required to maintain its value relative to earnings as reached in April 2029"; DWP's estimate (footnote 61).
- `ab2026__package_hmt_distributional_budget_2026` (1 row): HM Treasury's own grouping, the Budget 2026 policies modelled in Impact on households (paragraph 1.4): Table 6.1 lines 2, 3, 4, 5, 8, 11, 15, 26, 39, 49, 52, 59, 60, 61, 62, 72 and 95, plus the private landlord registration fee, which has no line. "Decisions announced at Budget 2026 (including those pre-announced where funding is allocated at Budget 2026)". It excludes line 1, the Household Energy Payment.
- `ab2026__package_hmt_distributional_since_ab2024` (1 row): HM Treasury's own grouping, the modelled policies and public service settlements "announced from Autumn Budget 2024 onwards up to and including Budget 2026" (paragraph 1.8): the lines above plus earlier events' measures, which are not Table 6.1 lines.

The coordinator's shared spellings: no kept row has the scope of `ab2026__gas_standing_charge_moved_to_unit_rates`, `ab2026__pwlb_debt_relief_councils_severe_distress`, `ab2026__private_landlord_register_fee_65`, `ab2026__british_business_bank_defence_commitments_accelerated` or `ab2026__package_household_energy_payment_and_electricity_vat`. The dropped rows on those subjects were design: the £108 current gas standing charge and the end-2027 delivery date (parameters), the £500 million and £200 million of PWLB debt relief (allocations to two councils, which Table 6.1's footnote 2 excludes as adding nothing to borrowing), the £65 fee (a parameter), and the "up to £5 billion" NWF and BBB defence commitment (an investment total). No red-book figure covers exactly lines 1 and 2, or exactly lines 1, 2 and 3 (`ab2026__package_household_energy_vat_and_fuel_duty`).

## Quantity and baseline proposals

- **Proposed metrics:**
  - fiscal aggregates (restated): `government_borrowing`, `government_borrowing_change`, `government_debt`, `government_net_worth`, `fiscal_balance`, `fiscal_balance_change`, `debt_interest_change`, `fiscal_consolidation_share`; `block_grant_effect` (AB2025 list);
  - household and business effects: `household_tax_change` (AB2025 list; worked cases), `average_cumulative_gain` (multi-year savings), `aggregate_household_saving` (AB2025 spelling; consumer savings), `bill_change_percent` (business electricity bills), `gross_earnings_change` (AB2025 spelling), `business_cost_saving` (administrative savings to business; replaces `operating_cost_change`, which the enum defines as an official operating-cost line), `housing_supply_change` (the 20,000 additional homes);
  - shares with exact meanings: `unaffected_share` (the share printed as unaffected), `share_with_zero_liability` (half of RHL properties paying no rates), `share_in_non_gaining_deciles`, `share_in_net_recipient_deciles`, `spending_to_tax_ratio`, `income_mobility_share`, `share_in_top_half_of_expenditure` (Impact on households context).
- **Proposed units:** `businesses` (15 rows), `dwellings` (1), `ratio` (1).
- **Proposed baselines:** `hmt_no_budget_2026_modelled_policies` (paragraph 1.6, "a counterfactual in which the modelled policies were not introduced") and `hmt_no_policy_changes_from_ab2024_through_ab2026` (paragraph 1.8, "a counterfactual in which the modelled policies and spending settlements were not introduced"), one row each. Other rows have `baseline_policy: null`.

## Not staged (rules 8 and 9)

The rework dropped 1,267 of the first staging's 1,699 rows. 234 proposed keys named only dropped rows and are gone.

| Category | Rows | Examples (locator) |
|---|---:|---|
| A. Measure parameters: rates, thresholds, payment amounts, dates, durations; worked-example inputs | 829 | 817 former `policy_parameter` rows, e.g. "£13.21" per hour (para 3.18), "£2,500" surplus earnings threshold (Impact on households para 1.4), "£13,319" withdrawal threshold (explainer FAQ). Also the £100 Household Energy Payment amount (4 rows, e.g. para 2.48); the £108 current gas standing charge (para 3.9); the £2,000 rise in the full new State Pension over the Parliament (para 5.23); six worked-case inputs, e.g. Tom's "£10,300" income. |
| B. Spending allocations: programme funding, capitalisations, investment totals, spending levels | 221 | 166 programme amounts that are not a Table 6.1 line's printed impact (table above), e.g. "£120 million" for the AI Security Institute (para 4.130), "£30 million" for Cardiff Parkway (para 4.157), "£1.5 billion" for the Social and Affordable Homes Programme (para 5.4); 46 investment totals, e.g. NWF "£15.4 billion" (para 4.44), Your First Home "£4.7 billion" (para 5.5); public sector net investment (Table 1.2, 6); departmental spending levels (2); £200 million of private AI model credits (para 4.132). |
| C. Financing: DMO remit, gilts, Treasury bills, NS&I, cash requirements, financial transactions | 177 | DMO net financing requirement "£258.6 billion" (Annex A.8); Table A.1 gilt sales by maturity; CGNCR "£144.1 billion" (para 1.47); Table 1.4 financial transactions by programme, e.g. Student Loans "15.9" (55 rows); Sovereign AI "£60 million" (para 4.135). |
| D. Contingent liabilities | 14 | Table 1.5, e.g. Department for Energy Security and Net Zero "1.2-1.7"; Total reasonable worst case "4-4.5". |
| E. Programme inputs, scope counts and targets | 24 | "670" HMRC compliance officers to recruit (paras 2.42, 6.151); tariffs on "over 100" food products (para 3.17); "around 10,000" homes the Social and Affordable Homes Programme funds (para 6.114); the 25% administrative-burden target worth "£5.6 billion" (para 4.51). |
| F. Effects of policies outside this Budget | 2 | "more than 100" businesses using the Global Talent funder pathway since Budget 2025 (para 4.112); "over £5 billion" of services exports from the Switzerland and South Korea deals (para 4.124). |

Rule 9 moved 74 kept rows from proposed keys to a Table 6.1 line's key: the 66 Table 6.3 item cells and the 160,000 employees (proposed keys such as `ab2026__package_tax_gap_timely_payment`, now line 45 components); four food-tariff savings (now line 10 components); the £3 billion and £1.7 billion DIP parts (now line 41 components); and the Your First Home count (now line 37). One row moved the other way: the £1.4 billion of DWP fraud savings, whose scope is wider than line 47 (rule 3).

### Other material not staged

- **Tables 6.1, 6.2 and 6.4** belong to `uk_hmt_tables`. Table 6.3 is a separate printed breakdown and is staged here.
- **No Impact on households bar readings** (README rule 4). Figures 1.A–1.E print no data labels. Chart 1.6's six data labels are staged.
- **Words without numbers** ("hundreds of pounds a month", "thousands of jobs") are not turned into numbers.
- **Footnote 73's earlier-event yields** (£6.5 billion, over £1 billion, £2.4 billion) are other fiscal events' measures; only this Budget's £2.3 billion and the £12 billion total are staged.
- **Background macro forecasts** that score no measure (GDP growth, inflation, employment, Table 1.1), departmental efficiency histories, Annex B budgets and Annex C charts are not staged.
- **The abbreviated 29 October explainer** has no quantitative content.

## Judgement calls for the coordinator

- **`spending_to_tax_ratio` is kept, against the drop list.** Its only row is Impact on households paragraph 1.10's "households in the lowest income decile will receive over four times as much in public spending than they pay in tax": a distributional statement and one of the Impact on households printed values the brief keeps. The 60% row beside it stays too. Drop both if the drop list was meant literally.
- **Mislabelled shares beyond the 84%.** Besides the 84% (`unaffected_share`, never 16%), BADR's "three-quarters … will still receive relief on their entire gain" is the unaffected share too; "half of all RHL properties … will not pay business rates at all" includes properties already paying none (`share_with_zero_liability`); and Impact on households' 20%, 60%, 59% and approximately 20% are not affected shares (proposals above). The registered `share_no_change` is a household-income measure, so the 84% of income tax payers follows the brief's `unaffected_share`.
- **Registered metrics replace AB2025-era proposals.** The four "around £50 off the annual Ofgem price cap" rows and the three energy-debt "£30" rows now use the registered `energy_bill_change` (unit `gbp_per_household`), which the enum mints for HM Treasury bill figures; the India agreement's GDP effects use `gdp_level_effect` in GBP (the AB2025 IPPR precedent).
- **Financial transactions and public sector net investment are dropped as financing and spending levels.** Table 1.4 prints forecast levels of lending by programme, not Budget effects. Public sector net investment is an OBR aggregate, but the brief lists `public_investment_share` for removal.
- **Jobs and induced homes stay; delivery targets go.** Estimated jobs (NWF 100,000; BBB 40,000; Rolls-Royce 3,300; DIP 60,000) and Your First Home's "estimated 20,000 new homes" are estimated effects. The 10,000 homes the Social and Affordable Homes Programme funds (in line 35's title), robotic procedures rising to 500,000, 2,000 learners and the 650,000 workforce requirement of the infrastructure pipeline are delivery targets of allocations.
- **The BBB's 40,000 jobs is now `restated`.** Footnote 135 cites the British Business Bank's press release.

## Printed problems and differences

- **Spending figures that differ from Table 6.1:**
  - Social and Affordable Homes Programme: £1.5 billion (paras 5.4, 6.114) against line 35's -1,750 over 2027-28 to 2030-31.
  - Early years books: "£5 million a year for three years from 2027-28" (paras 3.20, 6.122) against line 9's -5 in 2026-27, 2027-28 and 2028-29. The amount agrees; the years do not.
  - Local apprenticeship services £100 million (line 22: -120); Good Growth Funds £285 million in 2027-28 (line 20: -340); Strategic Authorities £150 million (line 25: -180); Union Learning Fund £15 million a year (line 73: -20 a year); Sovereign AI £60 million (Table 6.2 line 4: -45 a year).
  - DWP fraud and error: "an additional £1.4 billion over the forecast" (para 5.17) against line 47's +600m in total.
- **Regulatory savings target:** paragraph 6.36 prints "£5.6 million"; paragraph 4.51 prints "£5.6 billion". The executive summary's "almost £800 million per year" and paragraph 4.52's "up to … £640 million per annum" have different printed scopes; both stay.
- **Repeated amounts that disagree (not staged after rule 8):** local AI partnerships £30 million (para 4.135) and £15 million (para 6.101); Leeds College of Building £28 million (para 4.71) and £15 million (para 6.53); business tariff suspensions on 269 goods (para 3.28), 350 goods (para 4.147) and 361 extensions plus 72 new suspensions (line 16's title).
- **Pubs relief:** the text prints an extra "20%"; Table 6.1 prints "20ppts".
- **Table 1.3** labels the new forecast "November 2026 forecast" in an October Budget. Chart 1.6 prints 14.5 where the text says £15 billion. "Debt is lower at the end of the forecast" fits public sector net financial liabilities (83.2% to 81.7%), while public sector net debt goes from 95.5% to 95.6%.
- **Paragraphs 6.225 and 6.226** repeat the Machine Games Duty measure. Annex A footnote 181 points to A.17 for green gilts, which A.19 covers.
- **Pension Tax Allowance explainer:** the FAQ prints "£13.319" for £13,319; the explainer prints both £13,036.40 and the rounded £13,037, and "up to £94" beside Steph's £93.28. The FAQ repeats a question and prints "part-time wok".

## Verification

- **Checker:** `PYTHONPATH=. uv run -q python pipeline/ab2026_harvest_contract.py sources/harvest-uk-ab2026-2026-10-29/uk_hmt_redbook` reports 432 rows, 0 problems.
- **Determinism:** two runs of `stage.py` write the same `claims_staged.jsonl.gz` and an unchanged `manifest.jsonl`. COUNTS.json pins the gzip's sha256.
- **Spot check (the rework's, 29 October):** 30 rows drawn with `random.Random(20261029).sample(range(432), 30)` (0-based row numbers), each re-opened at its locator in the hashed primaries: red-book and Impact on households pages extracted with `pdftotext -layout -f N -l N`; table cells read against the printed row and column. All 30 match on value, sign, unit and period.

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
