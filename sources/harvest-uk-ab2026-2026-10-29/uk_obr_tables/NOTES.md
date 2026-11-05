# uk_obr_tables — October 2026 Economic and fiscal outlook

We keep `stage.py` on branch `uk/ab2026-harvest-staging` at `harvest-staging/ab2026/lanes/obr-tables/uk_obr_tables/stage.py`. We commit only NOTES.md, `manifest.jsonl` and `claims_staged.jsonl.gz` to this branch, and the repository holds no primary bytes. Fetch each primary from its `manifest.jsonl` URL (or, while obr.uk refuses non-browser clients, use the coordinator's local copies) and check its sha256.

We staged this family on 2026-10-29, reworked it on 3 November 2026 under the OBR review, and again on 4 November under reviews A and B (see "Review fixes" at the end). We use source `obr_efo`. We stage **2,800 rows (2,891 before the 3 November review, 2,797 at 4f424b9), 4 primaries (rows cite 3 of them), 98 individual registered measures plus the registered total-policy package.** We write all outputs inside this family. `stage.py` embeds all reviewed rows as metadata templates and cell data. A rerun needs only the Python standard library, and reproduces the gzip without primary files or network access.

## Access recipe and primaries

The lane tried each resolved URL in the supplied OBR `PROVENANCE.md` once, with `curl -sSL` and the exact Safari User-Agent the assignment requested. The OBR's server returned **403** for the EFO landing page at 2026-10-29T15:51:17Z, and for the resolved URLs of the chapter-2 workbook and detailed-table ZIP at 15:51:18Z. The lane attempted no bypass. We used the supplied local policy and aggregate workbook members and PDF, and record `access: "local copy"` on every row and manifest entry.

The coordinator supplied the local copies. The lane kept exact byte copies, failed-response headers and bodies, and fetch timestamps in its local primaries folder, which it never committed. It read the workbooks with openpyxl `data_only=True` and the PDF with `pdftotext -layout`, and verified all three primaries with `shasum -a 256`. Both workbook member hashes match the browser-download provenance from 28 October, including the ZIP's recorded Last-Modified of Wed, 28 Oct 2026 14:05:59 GMT.

We give the resolved ZIP URL as the publication URL for both members, with the member name in each row's note and the manifest. Nobody supplied the ZIP container itself locally, and we don't present it as read. PROVENANCE gives no PDF attachment URL, and the blocked landing page kept us from discovering it. So in the PDF's manifest entry and rows we use the EFO landing URL and name the supplied local PDF file. The OBR prints October 2026 on the cover and imprint; we take the publication date 2026-10-28 from the EFO-page date recorded in PROVENANCE.

**The OBR corrected the PDF after the lane read it (README rule 7).** On 30 October 2026 GOV.UK replaced the attachment (change history 2026-10-30T14:21:10Z) with a corrected version (sha256 `555e0c26…`, 1,771,863 bytes), and the OBR's download link (`obr.uk/download/economic-and-fiscal-outlook-october-2026/`) redirects to it. The OBR added a correction slip at physical p.4. In paragraph 3.19's first bullet it now dates the abolition of carbon price support April 2028, where the 28 October text said April 2027. Review B found every other staged PDF quote unchanged in it. Its physical page equals the printed page + 4, against printed + 3 in the 28 October file. We list it in the manifest as a fourth primary, and every PDF row cites the 28 October version (`9e0e9c34…`), which the lane read.

| Primary file | Rows | Bytes | SHA-256 |
|---|---:|---:|---|
| efo-october-2026-detailed-forecast-tables-policy.xlsx | 2,520 | 106,602 | `cdcc2a06b100241bf3010bd159a4e5d43daef2348a3850797b1e88a308fd45fd` |
| economic-and-fiscal-outlook-october-2026-web-accessible.pdf (28 October) | 267 | 1,754,344 | `9e0e9c340e35e603066f3124a614fcd68feadb3d5d10d1f76fb536e150e6225e` |
| efo-october-2026-detailed-forecast-tables-aggregates.xlsx | 13 | 218,000 | `3ffa3f1e63667b2ae9fb9626dc1da881673227d43aeeb52f8c3db168a5c75d6b` |
| economic-and-fiscal-outlook-october-2026-web-accessible.pdf, corrected 30 October 2026 | 0 | 1,771,863 | `555e0c266a5c2a9a5fdeaee9a36425c6bf3b899fde456160945b5323f610c3f4` |

## Coverage

- Policy workbook Table 1.1: we stage **2,520** cells, every numeric row series (420) across all six fiscal years, 2026-27 through 2031-32. They comprise 2,112 numbered-measure component/total cells, 48 fiscally neutral cells, 30 non-scorecard cells and 330 summary cells.
- EFO chapter 3: we stage **225** rows (316 before the 3 November review):
  - Table 3.1, 114 rows. The OBR repeats the table's "Direct effect" rows as "Spending measures" and "Tax measures" rows, so we dropped the repeats.
  - Table 3.3, 35 costings plus 7 categorical uncertainty ratings.
  - Policy and behavioural prose and Box 3.1, 69 rows. On 4 November we restored paragraph 3.20's financing requirement and added Box 3.1's two measure counts.
  - We treat Table 3.2's 47 funding cells as design (rule 8) and don't stage them.
- Headline fiscal context: we stage **55** rows: 13 workbook cells (PSNB cash six years; ex-BoE PSND/GDP seven years) and 42 PDF cells (Table 7.1 headroom 13; Annex A Table A.9 PSNB, PSNFL and ex-BoE PSND 29). For the current-budget and PSNFL rules we include current pre-measures, post-measures and the printed memo excluding fuel-duty rises, and we include the welfare-cap margin. Where the PDF and aggregate workbook give the same forecast, we stage it once.

## Conventions

- **Values and precision.** We take policy workbook values at their displayed integer £million formats (`0`, `#,##0`; eight exact General-format zeros) and multiply them by 1e6. We don't claim unprinted cached decimal precision. We round decimals half away from zero, and stage `0` for a stored negative fraction that displays zero. A LibreOffice PDF rendering independently confirmed these display conventions. We take aggregate workbook values at their displayed one-decimal precision. We multiply PDF £billion values by 1e9 and £million by 1e6, and stage no ratios, sums or inferred annual paths.
- **Signs.** The OBR prints in the policy workbook “This table uses the convention that a negative sign implies a loss to the Exchequer (and is therefore an increase in PSNB).” Under PDF Tables 3.1/3.3 it prints “A positive sign implies an increase in borrowing.” We keep both. On the workbook's indirect-effect rows, whose signs conflict with that workbook legend, we say so. In prose rows we keep positive magnitudes for costs, yields or behavioural erosion as the OBR words them, and state the meaning in per-row conditions. We record headroom as positive for a margin and negative for a breach.
- **Period.** We use the FY end year, with the printed `fy`. For quarterly CPI peaks we use calendar-year `point_in_time` and quarter detail without `fy`. We stage an annual average or recurring prose amount once, at the terminal forecast FY, with its interval in `aggregation`, rather than manufacture six yearly values. We treat staffing figures as design (rule 8) and keep them in `conditions.staffing`, not in rows. We put Box 3.1's undated share and counts at the publication-year anchor, 2026. We keep end-March timing for debt stocks and end-March-centred GDP denominators.
- **Central.** We stage ordinary policy tables and prose as `point` estimates of the single final forecast. We mark aggregate forecasts `central`, for the OBR central forecast, and observed 2025-26 outturns `point`. We infer no statistical confidence interval. For “High” ratings we use categorical `value: 0`, the precedent's schema placeholder, not a numerical score. The Health Foundation's range endpoints span alternative reform options, not uncertainty about one policy.
- **Attribution.** We mark 2,777 rows `own` and 23 `restated` (2,821 and 70 before we dropped Table 3.2's 47 rows on 3 November).
  - We follow the AB2025 `own` convention for OBR-certified and HMRC- or DWP-scrutinised costings, and use `obr_efo_forecast` for the OBR's fiscal judgments.
  - We mark twelve workbook fuel cells and two PDF fiscal fuel costings restated `hmt_costing_uncertified`: in EFO p.59 footnote 1 the OBR says the final Government costing arrived after certification.
  - We name ONS on six latest ONS outturn aggregate cells, the Health Foundation on two social-care options, and the Government/DBT impact assessment on one FTA effect.
  - We keep the OBR's CPI judgments as its own estimates. We use `administrative_fact` for ONS facts and `different_model` for modelled estimates.
- **Scope.** All 98 numbered workbook titles match registry titles once we normalise whitespace and footnotes. We key fiscal-head components to their full measure, with component conditions; never sum totals and components as independent estimates. We use the registered total-policy package only for workbook row 552 and the PDF's explicit HMT-policy-table memo. For all other groupings we use the package keys we proposed and registered in tranche 2, and for context levels null with no key. Since 4 November, by the coordinator's call on review A's H-6(b), we stage paragraph 3.28's salary-sacrifice revision as a context row with a null key, not as an AB2026 intervention. The AB2025 OBR family stages no headline fiscal aggregates. The live `Metric` enum supplies `fiscal_headroom`, and cross-family proposals supply the closest aggregate names.
- **Quotes and order.** We quote full numeric or rating cells, or full OGL prose sentences, keeping the printed number. We normalise PDF whitespace and line wraps, and leave footnote superscripts out of sentence text. We read in policy workbook row/column order, then PDF page/position, then aggregate workbook table/row/column. In the 28 October file that rows cite, the physical page equals the printed page + 3 (+ 4 in the 30 October correction).

## Coverage by measure_key, including null

We use 128 keys on 2,742 rows, 1,951 of them `row_type: measure_component`. Of those rows, we key 535 (374 of them `measure_component`) to the 29 keys we proposed and registered in tranche 2. We stage 58 rows as context: 42 fiscal aggregates, 13 headroom rows, Box 3.1's two measure counts and paragraph 3.28's salary-sacrifice revision. Across the family we mark 1,951 rows `measure_component` and 649 `measure_total`, and give 200 no row type. We key the uncertainty ratings to their measures.

| measure_key | Rows |
|---|---:|
| `ab2026__advance_corporation_tax_abolished` | 12 |
| `ab2026__alcohol_duty_small_producer_relief` | 12 |
| `ab2026__artificial_intelligence_package` | 18 |
| `ab2026__badr_lifetime_limit_500000` | 43 |
| `ab2026__bank_surcharge_6pc_temporary` | 21 |
| `ab2026__benefits_in_kind_payrolling_delay` | 36 |
| `ab2026__benefits_removed_hospitalised_serious_offenders` | 18 |
| `ab2026__british_business_bank_backing_innovation` | 18 |
| `ab2026__british_industrial_competitiveness_scheme` | 25 |
| `ab2026__bus_fare_cap_2_england_outside_london_2027` | 18 |
| `ab2026__business_rates_ev_charging_relief` | 48 |
| `ab2026__business_rates_pubs_relief_35pc` | 48 |
| `ab2026__business_rates_retention_mayoral_authorities` | 31 |
| `ab2026__business_rates_rhl_transitional_support` | 48 |
| `ab2026__business_rates_sbrr_rhl_thresholds_raised` | 48 |
| `ab2026__business_rates_vape_shops_and_agcs_reliefs_removed` | 48 |
| `ab2026__business_tariff_suspensions` | 12 |
| `ab2026__cambridge_development_corporation` | 12 |
| `ab2026__carbon_price_support_removed` | 18 |
| `ab2026__carers_allowance_earnings_taper` | 18 |
| `ab2026__cash_isa_limit_held_at_20000` | 12 |
| `ab2026__civil_service_admin_budgets_cut_20pc` | 12 |
| `ab2026__civil_service_ai_fund` | 12 |
| `ab2026__climate_change_levy_rates_2028` | 12 |
| `ab2026__company_car_tax_rates_2030_31` | 36 |
| `ab2026__defence_admin_savings_reinvested` | 12 |
| `ab2026__defence_investment_plan_capital_reallocation` | 18 |
| `ab2026__defence_investment_plan_further_savings` | 18 |
| `ab2026__distributions_framework_modernised` | 19 |
| `ab2026__dwp_fraud_and_error_prevention` | 31 |
| `ab2026__early_years_books_access` | 12 |
| `ab2026__electricity_generator_levy_55pc` | 12 |
| `ab2026__electricity_vat_zero_rate_to_july_2027` | 20 |
| `ab2026__emi2_option_limit_120000` | 48 |
| `ab2026__ets_energy_from_waste_delay` | 12 |
| `ab2026__ev_charging_public_chargers` | 12 |
| `ab2026__first_time_buyer_isa` | 12 |
| `ab2026__food_and_heating_oil_tariff_suspensions` | 12 |
| `ab2026__foreign_permanent_establishment_exemption_mandatory` | 12 |
| `ab2026__foreign_sovereign_investments_taxation` | 61 |
| `ab2026__founders_relief_cgt` | 37 |
| `ab2026__franchised_higher_education_registration` | 18 |
| `ab2026__free_bus_travel_children_august_2026` | 12 |
| `ab2026__fuel_duty_5p_cut_extended_and_rpi_rise_deferred` | 15 |
| `ab2026__further_priorities_nhs_and_vawg` | 24 |
| `ab2026__gas_distribution_revenue_recognition_spread` | 12 |
| `ab2026__good_growth_funds` | 18 |
| `ab2026__growth_guarantee_scheme_expansion` | 21 |
| `ab2026__hgv_ved_1_for_12_months` | 12 |
| `ab2026__high_needs_local_authority_spending` | 18 |
| `ab2026__hmrc_tax_gap_package` | 105 |
| `ab2026__household_energy_payment_100_bands_a_to_d` | 18 |
| `ab2026__hvcts_deferrals_discounts_exemptions` | 42 |
| `ab2026__infected_blood_compensation_additional_report` | 12 |
| `ab2026__investment_for_growth` | 24 |
| `ab2026__landfill_communities_fund_credit_cap` | 24 |
| `ab2026__leeds_city_fund` | 24 |
| `ab2026__lifetime_isa_withdrawal_charge_20pc_above_cap` | 12 |
| `ab2026__local_apprenticeship_services` | 12 |
| `ab2026__low_value_imports_customs_relief_removed` | 60 |
| `ab2026__machine_games_duty_higher_stake_25pc` | 18 |
| `ab2026__mileage_allowance_payments_55p` | 36 |
| `ab2026__misogyny_prevention_programmes` | 12 |
| `ab2026__national_wealth_fund_capital` | 18 |
| `ab2026__online_marketplace_liability_uk_businesses` | 18 |
| `ab2026__package_total_policy_decisions` | 12 |
| `ab2026__parental_allowance_fathers_partners_adopters` | 12 |
| `ab2026__pension_death_benefits_two_year_rule_removed` | 30 |
| `ab2026__pension_tax_allowance` | 54 |
| `ab2026__private_hire_operators_vat_full_fare` | 12 |
| `ab2026__property_income_rates_plus_2pp` | 44 |
| `ab2026__rd_relief_claim_notification_form_removed` | 18 |
| `ab2026__red_diesel_duty_cut` | 12 |
| `ab2026__regional_growth_investments` | 18 |
| `ab2026__rough_sleeping_investment` | 24 |
| `ab2026__rough_sleeping_reprioritised_mhclg_budgets` | 18 |
| `ab2026__savings_income_rates_plus_2pp` | 20 |
| `ab2026__securities_transfer_tax` | 12 |
| `ab2026__social_and_affordable_homes_programme` | 12 |
| `ab2026__steel_tariff_and_quotas` | 18 |
| `ab2026__strategic_authorities_capacity_funding` | 12 |
| `ab2026__student_loan_interest_cap_6pc_plan_2_and_3` | 18 |
| `ab2026__supported_housing_licensing` | 12 |
| `ab2026__trading_allowance_3000` | 36 |
| `ab2026__uc_surplus_earnings_threshold_2500_extended` | 12 |
| `ab2026__uk_export_finance_defence_capacity` | 13 |
| `ab2026__uk_india_ceta_and_double_contributions_convention` | 19 |
| `ab2026__ukraine_winter_air_defence` | 18 |
| `ab2026__union_learning_fund` | 12 |
| `ab2026__us_llc_double_taxation_relief` | 12 |
| `ab2026__vat_5pc_family_days_out_summer_2026` | 12 |
| `ab2026__vat_medical_deputies_staffing` | 12 |
| `ab2026__vat_reverse_charge_overseas_services_restricted` | 12 |
| `ab2026__vat_zero_rate_donated_medicines` | 12 |
| `ab2026__vat_zero_rate_land_for_social_housing` | 12 |
| `ab2026__waste_crime_landfill_tax_clearances` | 18 |
| `ab2026__writing_down_allowance_12pc_and_fya_50pc` | 43 |
| `ab2026__your_first_home_equity_loan` | 19 |
| `ab2026__youth_guarantee_and_apprenticeships_spring_2026` | 18 |
| the 29 keys we proposed (below) | 535 |
| `null` (context) | 58 |

## Keys we proposed, with the producer's scopes

We gave all of these rows `measure_key: null` and proposed these keys, and in tranche 2 we registered them and moved them into `measure_key`. We name them under README rule 2 as harmonised on 3 November (review finding 9). A single measure takes `ab2026__<slug>`, and a scope package's slug names the scope and drops `obr`. The exception is the OBR's own residual groups, which keep it (4 November, review B finding 15). Where the OBR publishes only a named residual group, we leave its line decomposition unresolved and attach no guessed membership or registry key.

| Key | Rows | Scope |
|---|---:|---|
| `ab2026__departmental_spending_growth_2031_32` | 13 | No Table 6.1 lines. “Departmental spending: Grow day-to-day spending by 0.7% in real terms in 2031-32, matching 0.7% average annual real terms growth from 2029-30 to 2030-31”. PDF describes the same baseline change as a £5.5bn reduction in the 2031-32 pre-measures RDEL assumption. (Was `ab2026__package_obr_departmental_spending_growth_2031_32`.) |
| `ab2026__package_carbon_price_support_and_cfd_levies` | 2 | Table 6.1 lines 70 and 71: row 2673's £0.4bn covers their receipts (`measure_component`, excluding the backdated AME support of footnote 9), and row 2677's £0.5bn their totals. The CfD-levy funding sits in line 70: its "Environmental levies" receipts (−480 / −63 / −130 / −408 / −450) give the only environmental-levies effect of any decision (review B finding 7). Footnote 9's £0.8bn of backdated BICS and Supercharger support counts as line 70's current AME in 2027-28, and we key it to line 70 as a component. The 28 October PDF dated CPS abolition April 2027; the OBR's 30 October correction moved it to April 2028, matching line 71. (Was `ab2026__package_obr_carbon_price_support_and_cfd_levies`.) |
| `ab2026__package_civil_service_transformation_programme` | 1 | The OBR's “civil service transformation programme ... reduce resource spending”. Table 6.1 lines 63 and 64 probably make up the programme, but the OBR names no lines, and lines 63 and 64's totals average £0.56bn from 2028-29 against its £0.5bn (review B finding 14). (Was `ab2026__package_obr_civil_service_transformation_programme`.) |
| `ab2026__package_compliance_measures_announced` | 1 | No Table 6.1 line list. Box 3.1 (p.66): "Of the compliance measures announced in this Budget". The OBR does not list them; they probably cover Table 6.1 line 45's items and line 46, but the OBR doesn't say so, so we take the scope from its words. |
| `ab2026__package_corporation_and_bank_tax_changes` | 7 | OBR “Changes to corporation and bank taxation”; paragraph 3.16 explicitly discusses line 58 WDA/FYA, line 55 bank surcharge, and line 54 overseas sovereign immunity. The OBR publishes no complete Table 6.1 line decomposition or fiscal-head allocation, and we leave it unresolved and infer no further membership. (Was `ab2026__package_obr_corporation_and_bank_tax_changes`.) |
| `ab2026__package_defence_investment_plan` | 1 | OBR “funding for the defence investment plan” / “the defence investment plan, which increases departmental resource spending (RDEL)”; related to Table 6.1 Defence Investment Plan entries, but the OBR publishes no complete line decomposition, and we infer no membership of lines 40–43. (Was `ab2026__package_obr_defence_investment_plan`.) Shared with the red book's Defence Investment Plan row. Row 2522's £1.8bn a year gives the package's RDEL part (`measure_component`, review A's K-2): it matches gross RDEL (line 40's averages £1,766m), not the lines' net effect. |
| `ab2026__package_dividend_and_capital_gains_tax_changes` | 6 | Table 6.1 lines 26, 49 and 60: OBR “Changes to dividend and capital gains taxation”. (Was `ab2026__package_obr_dividend_and_capital_gains_tax_changes`.) |
| `ab2026__package_fuel_duty_and_electricity_vat` | 11 | The receipts of Table 6.1 lines 2 and 3 only (the OBR groups receipts in Table 3.1's tax groups, review B finding 3); OBR “Fuel duty freeze and VAT off domestic energy bills”. Excludes household council-tax rebate line 1. (Was `ab2026__package_obr_fuel_duty_and_electricity_vat`.) |
| `ab2026__package_fuel_duty_freezes_since_2010_11` | 1 | OBR cumulative 2010-11 to 2027-28 fuel duty freezes and 5p cut relative to stated RPI uprating; includes Table 6.1 line 3 and earlier freezes since 2010-11. Not the cost of the AB2026 measure alone. (Was `ab2026__package_obr_historical_fuel_duty_freezes_and_5p_cut`.) RF's `ab2026_option__fuel_duty_rpi_uprating_since_2011` looks at the same pair of paths from the other side (RPI uprating since January 2011 against the freezes); the two keys stay separate, and each family's NOTES names the other (review A's K-6). |
| `ab2026__package_government_decisions_since_march_2026` | 340 | Table 6.1 lines 1–98, plus the three fiscally neutral measures (PWLB debt relief, Scottish APD devolution, landlord registration fee) and the two non-scorecard policies listed above. OBR “Total effect of Government decisions”, with direct, indirect, receipt, expenditure and fiscal-head projections distinguished in conditions. Includes indirect effects where stated; not the HMT scorecard-only package. (Was `ab2026__package_obr_government_decisions_since_march_2026`.) Shared with the red book's Table 1.3 "Total effect of policy decisions" and RF's restatement. **Parts and wholes (rule 9, 4 November):** we mark the totals (workbook row 549 and Table 3.1's total) `measure_total` with no `component`, and every part `measure_component`, with `component` the label its primary prints: the workbook's direct and indirect effects, its total of receipts measures ("Total effects of receipts measures", which keeps `revenue_change`) and its 288 lines by head ("Receipts: <line>" or "<fiscal head>: <line>"), Table 3.1's direct and indirect effects, and paragraphs 3.2 and 3.5. Never sum a part with the total. The workbook's total of expenditure measures moved to the spending-decisions key and paragraph 3.4's tax line to the tax-decisions key (review B finding 6). |
| `ab2026__package_national_wealth_fund_and_british_business_bank` | 5 | Table 6.1 lines 29 and 30 together, plus their associated financial transactions in Table 6.2; OBR “funding available for the National Wealth Fund and the British Business Bank ... to invest in financial assets”. Paragraph 3.20's effects: we stage the financing requirement (`cash_requirement_change`, restored 4 November), the net debt effect (£3.4bn) and the borrowing effect (£0.5bn) as wholes, and the gross debt (£3.9bn) and the additional income (£0.6bn) as their parts (`measure_component`). (Was `ab2026__package_obr_national_wealth_fund_and_british_business_bank`.) |
| `ab2026__package_non_scorecard_decisions` | 12 | No Table 6.1 lines. “Direct effect of non-scorecard decisions”: exactly the departmental spending assumption and public-pension valuation changes above. (Was `ab2026__package_obr_non_scorecard_decisions`.) |
| `ab2026__package_obr_other_ame_spending_decisions` | 6 | OBR Table 3.1 “Other AME spending decisions”; excludes net unfunded pensions valuation, and is net of the council tax rebate shown on its own line (−£2.6bn in 2026-27): in Table 6.2 the OBR prints "Other spending decisions" at 0.4 in 2026-27, the rebate's 2.6 plus this group's −2.2 (review B finding 9). (Was `ab2026__package_other_ame_spending_decisions` until 4 November, review B finding 15.) The OBR gives no full Table 6.1 line decomposition in the PDF. (Was `ab2026__package_obr_other_ame_spending_decisions`.) |
| `ab2026__package_obr_other_departmental_spending_changes` | 7 | The OBR's Table 3.1 group: departmental spending changes excluding the pensions valuation, including the DEL funding for line 1's council tax rebate (the group, 5.4 / 1.2 / 1.5 / −0.1 / −0.2 / −6.0, equals the workbook's DEL total less the pensions valuation's DEL, which includes line 1's −2,627; review B finding 9). It includes defence, capital spending and the £5.5bn 2031-32 pre-measures RDEL reduction, which has no Table 6.1 line. (Was `ab2026__package_other_departmental_spending_changes` until 4 November, review B finding 15.) The OBR gives no full Table 6.1 line decomposition in the PDF. (Was `ab2026__package_obr_other_departmental_spending_changes`.) |
| `ab2026__package_obr_other_hmrc_compliance_and_debt` | 1 | OBR paragraph 3.13 residual “Other measures”: direct debt recovery, e-invoicing, debt collection agencies (components of Table 6.1 line 45), and online marketplace liability (line 46). (Was `ab2026__package_obr_other_hmrc_compliance_and_debt` until 3 November, and `ab2026__package_other_hmrc_compliance_and_debt` until 4 November.) |
| `ab2026__package_obr_other_tax_measures` | 6 | OBR Table 3.1 “Other tax measures”; residual of Table 6.1 tax measures after tax administration/compliance/debt, corporation/bank, savings/property, dividend/CGT and fuel/electricity VAT groups. PDF does not enumerate a full line-number decomposition. (Was `ab2026__package_obr_other_tax_measures` until 3 November, and `ab2026__package_other_tax_measures` until 4 November.) |
| `ab2026__package_planned_capital_spending_reductions` | 1 | OBR “Reductions in planned capital spending” / “changes to departmental capital spending”; PDF does not enumerate the exact Table 6.1 lines. (Was `ab2026__package_obr_planned_capital_spending_reductions`.) |
| `ab2026__package_property_and_savings_income_rates_receipts` | 7 | The receipts of Table 6.1 lines 61 and 62: Table 3.1's “Changes to savings and property income tax rates”. (Was `ab2026__package_obr_savings_and_property_income_tax_rates`.) **Receipts only (3 November):** The OBR prints 0.1 in 2027-28 and 0.9 in 2029-30 in Table 3.1, against lines 61 and 62's totals of 160 and 954 (£m), but in line with their receipts (in Table 3.3 it gives line 61's as 2, 543 and 400 from 2027-28). So we don't use `ab2026__package_property_and_savings_income_rates`, which covers exactly lines 61 and 62. |
| `ab2026__package_spending_decisions_since_march_2026` | 13 | OBR “Direct effect of spending measures” / “Spending measures”: expenditure-side effects of decisions since March, including unfunded public service pensions valuation and the £5.5bn 2031-32 RDEL assumption reduction. We don't use the HMT total-spending package here. Table 6.1 lines 1–98 can affect expenditure fiscal heads; the OBR publishes no complete narrower line decomposition, and we leave it unresolved. (Was `ab2026__package_obr_spending_decisions_since_march`.) Since 4 November it also holds the workbook's total of expenditure measures (I520:N520), Table 3.1's direct effect of spending measures reversed (review B finding 6). |
| `ab2026__package_tax_administration_compliance_and_debt_collection_receipts` | 6 | The receipts of Table 6.1 lines 45 and 46: OBR “Tax administration, compliance and debt collection measures”. The group (−0.1 / −0.5 / −0.6 / −2.4 / −2.9 / −3.6) equals lines 45 and 46's receipts (107 / 455 / 567 / 2,411 / 2,881 / 3,630) in all six years; their totals (8 / 262 / 434 / 2,248 / 2,733 / 3,423) round differently in every year (review B finding 3). Never key it to line 45 alone. (Was `ab2026__package_obr_tax_administration_compliance_and_debt`, then `ab2026__package_tax_administration_compliance_and_debt_collection` until 4 November.) Shared with RF's restatement. |
| `ab2026__package_tax_decisions_since_march_2026` | 6 | OBR Table 3.1 "Direct effect of tax measures": the direct effect of tax decisions since March 2026, as the OBR classifies them. Shared with RF's restatement of the same row. It equals −1 × the workbook's total of receipts measures, so the OBR groups receipts here. Before 3 November these rows sat under the total package with `component: tax measures (OBR classification)`. Since 4 November it also holds paragraph 3.4's "reducing borrowing by an average of £6 billion over the final four years", the mean of this line from 2028-29 (review B finding 6). |
| `ab2026__package_temporary_business_rates_reliefs_receipts` | 1 | The receipts of Table 6.1 lines 12, 13 and 14 (paragraph 3.19's "net cost of around £0.5 billion in 2028-29" covers their receipts, 536, against totals of 663; review B finding 3 and review A's K-7(g)): “package of temporary business rates measures” including real-terms freeze for certain sectors, pubs/live-music reliefs, small-business thresholds and extension of transitional support, partly offset by transitional relief supplement. (Was `ab2026__package_obr_temporary_business_rates_reliefs`, then `ab2026__package_temporary_business_rates_reliefs` until 4 November.) |
| `ab2026__private_landlord_register_fee_65` | 18 | No Table 6.1 lines. “Landlord registration fee”; receipts, current DEL and total. (Was `ab2026__package_obr_landlord_registration_fee`.) The costings family's spelling for the same measure. |
| `ab2026__public_sector_pensions_2024_valuations` | 27 | No Table 6.1 lines. “Public Sector Pensions: Net impact of the 2024 valuations”; departmental reductions, net public service pension payments and their net total. PDF calls this “Net impact of unfunded pensions valuation”. (Was `ab2026__package_obr_public_sector_pensions_2024_valuations`.) |
| `ab2026__pwlb_debt_relief_councils_severe_distress` | 12 | No Table 6.1 lines. “Provide Public Works Loan Board (PWLB) debt relief for councils in severe financial distress”; capital AME and total. (Was `ab2026__package_obr_pwlb_distress_debt_relief`.) The costings family's spelling for the same measure. |
| `ab2026__scottish_air_passenger_duty_devolution` | 18 | No Table 6.1 lines. “Devolving Air Passenger Duty to the Scottish Government in April 2027”; Scottish BGA, self-financed expenditure and total. (Was `ab2026__package_obr_scottish_air_passenger_duty_devolution`.) |
| `ab2026__state_pension_triple_lock_adjustment` | 2 | No Table 6.1 line: OBR paragraph 3.49 adjusted state pension triple lock expected April 2030, retaining CPI/2.5 percent floor but linking catch-up to 2029-30 earnings ratio. Paragraph 3.51's two figures (rows 2743–2744) come from the OBR's simulation over 1990–2025, not from a medium-term costing of the policy. (Was `ab2026__package_obr_adjusted_state_pension_triple_lock`.) The red book's spelling for the same measure. |
| `ab2026_option__fuel_duty_continued_freeze` | 1 | No Table 6.1 line as an announced measure: OBR paragraph 3.43 counterfactual “if fuel duty were to remain frozen until 2029-30”, extending line 3 beyond July 2027. (Was `ab2026_option__obr_fuel_duty_frozen_until_2029_30`.) Shared with RF, whose series for the OBR's constant-duty-rate alternative prints the same £4.3bn in 2029-30. |
| `ab2026_option__health_foundation_social_care_reforms` | 2 | No Table 6.1 line: Health Foundation illustrative future social care reforms cited by OBR paragraph 3.41, from limited home-care reform to wider schemes including residential care; costs additional to current spending in 2035-36 per footnote 13. The OBR cites the Health Foundation's estimates as illustrations, and HM Treasury prints no social care line in Table 6.1. (Was `ab2026_option__obr_health_foundation_social_care_reforms`.) |


## Metric, unit and baseline proposals

We use no unregistered enum literals. The live models register `fiscal_headroom`, even though the older README calls it a proposal.

| proposed_metric | Rows | Scope |
|---|---:|---|
| `measure_count` | 2 | Box 3.1: the 15 measures expected to reduce the tax gap, and the four of them that target the small business tax gap (context counts, as the uk_thinktank_misc and uk_ifs_ab2026 families stage measure counts; review B finding 11). |
| `cash_receipts_change` | 1 | Self-assessment overlapping transition payments, £17bn in 2029-30; assumed extraordinary accruals adjustment excludes the temporary cash effect from PSNB. |
| `fiscal_balance_change` | 6 | Table 3.1's memo line, the total effect of Government decisions on the current budget deficit (README rule 10, 3 November). |
| `tax_gap_share_of_compliance_yield` | 1 | Box 3.1: the share of this Budget's compliance measures' yield the OBR expects to reduce the tax gap ("a third"). |
| `costing_uncertainty_rating` | 7 | Table 3.3 High final ratings; categorical placeholder zero. |
| `psnb_share_of_gdp` | 7 | PSNB as percent of nominal GDP. |
| `psnd_share_of_gdp` | 7 | Ex-Bank-of-England PSND as percent of nominal GDP; reuses AB2025 cross-family spelling. |
| `psnfl_share_of_gdp` | 7 | PSNFL as percent of nominal GDP; reuses AB2025 cross-family spelling. |
| `public_sector_net_borrowing` | 7 | Annual PSNB cash level in GBP. |
| `public_sector_net_debt` | 7 | End-March PSND stock explicitly excluding Bank of England, GBP. |
| `public_sector_net_debt_change` | 3 | Marginal stock debt effects of NWF/BBB investment and Your First Home lending, paragraphs 3.20/3.22. |
| `public_sector_net_financial_liabilities` | 7 | End-March PSNFL stock, GBP. |

We propose these units: `percent_of_gdp` (28 rows, nominal GDP denominator, including one prose package effect and fiscal shares/headroom); `rating_category` (7 High uncertainty ratings); `measures` (Box 3.1's 2 counts).

Beyond `revenue_change`, we use these registered metrics: `decisions_effect_on_borrowing` (91 rows, README rule 10), `fiscal_headroom` (13), `cpi_inflation_effect` (6), `benefit_cost_change` (2, paragraph 3.51's simulations), `cash_requirement_change` (1, paragraph 3.20's financing requirement) and `gdp_level_effect` (1).

**At ingest.** In `uk_hmt_tables` we stage HM Treasury's Table 6.2 cash impacts of the same NWF and BBB financial transactions on the proposed `financial_transaction_cash_impact`, and here we stage paragraph 3.20's £1.9bn (row 2684) on the registered `cash_requirement_change`. At ingest we put Table 6.2's 60 rows on `cash_requirement_change` too, so both producers' figures share one metric.

We leave every `baseline_policy` null, and give effect estimates the explicit unregistered baseline proposals below. We propose no baseline for rating, funding-level and aggregate context rows.

| proposed_baseline, verbatim | Rows |
|---|---:|
| OBR pre-measures Autumn Budget 2026 policy parameters | 2,730 |
| Fuel duty policy reflected in OBR October 2026 economy forecast, confirmed before the final Budget parameters | 1 |
| Current social care spending (Health Foundation 2024 scenarios, additional spending in 2035-36) | 2 |
| Fuel duty rates increase in line with RPI inflation: stated policy since 2010-11 | 1 |
| Current triple lock uprating applied to historical outturn 1990–2025 | 1 |
| Earnings uprating applied to historical outturn 1990–2025 | 1 |

## Not staged and unreachable material

- **Design (rule 8), which we dropped on 3 November after review finding 1: 57 rows (58 until we restored paragraph 3.20's financing requirement on 4 November).**
  - Table 3.2's 47 funding cells: HMRC and DWP baseline, Budget 2025, Budget 2026 additional and total compliance, debt and fraud-and-error funding ("the funding provision", Source: HM Treasury). The OBR prints no yield in the table, and its Budget 2026 lines differ from the scored costs. Its DWP line prints −16, 188, 178, 188, 210, 214, while the workbook's line-47 departmental spending prints 218, −194, −184, −195, −217, −221.
  - Six staffing inputs: the 2,000, 200 and 150 DWP staff (para 3.12); the 5,500 and 670 HMRC staff and the "23 per cent increase" (para 3.13). We now keep them in `conditions.staffing` on the £0.5bn and £0.4bn yield rows.
  - Guarantee capacity, a contingent liability: UK Export Finance's £40bn and the Growth Guarantee Scheme's £7bn (para 3.21).
  - A lending allocation: Your First Home's £0.7bn and £1bn of loans (para 3.22). We stage paragraph 3.22's effect on debt (£0.7bn in the first year).
- **The rule for lending and financing (4 November, the coordinator's call on review B's finding 5; README rule 8).** In the harvest we stage HM Treasury's Tables 6.1, 6.2 and 6.4 and the OBR's policy workbook whole, as the decisions' costings. Elsewhere we treat an amount a scheme will lend or spend as design (rule 8), and an effect on borrowing, debt or the financing requirement as an estimate. So we keep paragraph 3.22's loan volumes dropped and its effect on debt staged. We had dropped paragraph 3.20's "£1.9 billion a year" increase in the Government's financing requirement on 3 November as a financing allocation, and we restored it as a fiscal-aggregate estimate (`cash_requirement_change`). In EFO paragraphs 6.19–6.20 the OBR says the CGNCR "forms the basis of" the DMO's remit, so we treat the requirement as the aggregate and the remit as the design.
- **Repeats, which we dropped on 3 November (review finding 5, the coordinator's call): 37 rows.** As in the AB2025 OBR family, we stage the table cells. We dropped text that repeats a Table 3.1 cell (paras 3.2, 3.3, 3.4, 3.11, 3.13, 3.16, 3.17 and 3.19: 19 rows) or earlier text (paras 3.11, 3.12, 3.13 and 3.16: 6 rows). We also dropped Table 3.1's "Spending measures" and "Tax measures" rows, which repeat its "Direct effect of spending measures" and "Direct effect of tax measures" rows (12 rows).

- **Chapters 1, 2 and 4–6 and paragraph 7.20 (4 November, review B finding 4; the coordinator's call: not staged).** In most of these chapters the OBR repeats Table 3.1 and the workbook's lines by head (Tables 4.5–4.7, 5.4, 5.6 and 6.2 among them). The OBR gives these new estimates there, which we didn't stage; tranche 2 may add any of them as components:
  - Tables 4.2 (p.87, indirect effects on receipts), 5.2 (p.108, indirect effects on spending) and 5.8 (p.128, "Effects of Government decisions" on debt interest, −0.9 / 1.2 / 1.0 / 0.7 / 0.4 / 0.3). They form parts of the decisions' total effect, which we stage whole in rows 2490–2495 and 2534–2539 (4f424b9 order).
  - Tables 4.3 to 4.7's indirect rows by tax and their PAYE / self-assessment split, including Table 4.4's self-assessment income tax by measure (e.g. "Timely payment for self assessment" 3.5 / 6.5 in 2029-30 / 2030-31). They split, by tax or by cash timing, lines we already stage.
  - Paragraph 4.30: a continued fuel duty freeze "would reduce receipts, on average, by £4 billion a year between 2027-28 and 2031-32". The OBR gives here the receipts average of the option whose effect on borrowing we stage in row 2740.
  - Table 6.3 (p.141, "Effects of policy on financial transactions", −0.1 / 0.8 / 2.1 / −12.4 / 3.9 / 4.0): the OBR's whole-package effect on financial transactions. We don't stage it yet. We stage HM Treasury's Table 6.2 total in `uk_hmt_tables`.
  - Paragraph 7.20's decomposition of the changes in the fiscal-target margins.
- In Annex A the OBR gives no policy-costing narrative beyond introduction A.1. Its current receipts, spending and economy forecast Tables A.1–A.8/A.11–A.12 fall outside the policy family's scope. The aggregate lane owns the headline fiscal aggregates in A.9.
- The OBR prints no numeric Pension Tax Allowance or Carer’s Allowance taper claim in chapter 3 or Annex A. A whole-PDF search finds no PTA phrase, and Carer’s Allowance appears only in a generic welfare footnote, not a taper costing. We cover these measures with workbook rows.
- The OBR prints no data labels for the policy values in Charts 3.1–3.4 and Box 3.1 Charts A/B, and we read no bars or paths. We don't count tick labels and dates as claims. In Box 3.1's tax-gap context the OBR restates HMRC and several Budgets' historical compliance yields, which we didn't stage. We stage its three AB2026 figures. One gives the estimate "a third of the yield" (review finding 10; we completed the sentence on 4 November). The other two count measures: 15 measures expected to reduce the tax gap, and four that target the small business tax gap (review B finding 11).
- We didn't separately stage policy design parameters (tax rates/thresholds, dates, litres/pence) that give no costing or behavioural estimate.
- In paragraphs 3.29–3.36 the OBR monitors older employment, housing and childcare policies and costs no AB2026 Table 6.1 measure there, so we invented no new AB2026 measure key for them. In paragraph 3.28 the OBR revises its Autumn Budget 2025 costing of salary sacrifice by +£0.4bn. Since 4 November we stage that as a context row with a null key (review A's H-6(b), the coordinator's call). A revision isn't a level, so it doesn't share a key with Table 6.4's recosted level.
- In paragraph 3.48 the OBR gives FRS long-run pension and debt scenarios as current-policy or earlier-publication context, outside the requested headline medium-term aggregate scope. In paragraph 3.52 the OBR dates the adjusted-triple-lock debt effects 2075-76, which would map to period 2076. The checker caps periods at 2075, so we staged neither the 25pp nor the 10pp long-run debt effect, rather than misdate them.
- The text lane owns no further primary access attempts; in the root manifest and NOTES we record the direct/local recipe and the unreachable EFO landing page.

- The OBR gives no static/post-behavioural split, rating matrix or recosting table in the policy workbook, and labels no fiscal-head rows as static or behavioural. We don't count contents or navigation cells as further claims.
- The supplied chapter-2 charts workbook and the other economy, receipts, expenditure and debt-interest workbooks fall outside the policy/headline scope. The chapter-2 fresh URL returned 403, and we didn't use it. We staged no economy-wide GDP/CPI paths, only explicit policy CPI/GDP effects.
- We couldn't reach the EFO landing page, resolved detailed-tables ZIP or chapter-2 workbook URLs (403), and couldn't discover the PDF attachment URL. We presumed no missing online content, new attachments or separate latest ratings database available, and substituted none of them. We include the seven printed PDF ratings.


## Contradictions and limitations retained

- On workbook row 549 “Total effect of Government decisions” the OBR displays **-8,905 / -50 / 1,322 / 5,484 / 6,425 / 14,093 £m**, while in PDF Table 3.1 it prints **6.3 / 7.0 / 2.1 / -2.6 / -3.5 / -9.3 £bn**. The gap exceeds a sign flip or rounding difference. Workbook direct row 551 follows its negative-loss legend, and indirect row 555 has the same signs as the PDF borrowing effects. The OBR appears to mix conventions in the workbook's total. We leave both sources unchanged and call out the inconsistency in row notes.
- The OBR and HMT round differently: the OBR gives the Household Energy Payment as -2,627 £m here, and HMT gives -2,625 £m in Table 6.1. Rounded components need not sum to the separately rounded totals.
- In the 28 October text of paragraph 3.19 the OBR dated carbon-price-support abolition April 2027, and in its 30 October correction moved it to April 2028, matching line 71. For its combined CPS/CfD scope (lines 70 and 71) we use our own package key, not the CPS key.
- In paragraph 3.16 the OBR dates the first-year-allowance increase April 2027, while HMT dates line 58 1 January 2027. The reviewer judged the dates a difference of description, not scope, so we key the WDA/FYA row to line 58.
- In paragraph 3.21 the OBR gives a £7bn Growth Guarantee expansion, while HMT's line 75 gives £6.5bn of additional SME lending. The £7bn and £6.5bn measure different quantities of the same measure (guarantee capacity against lending supported). We key the borrowing rows to line 75 and don't stage the £7bn.
- In Table 3.3 and paragraph 3.24 the OBR calls the reform Company Share Option Plan (CSOP), while HMT's line 28 says Enterprise Management Incentives 2 (EMI2). The workbook's line 28 total (−26 / −33 / −47 / −144 / −142) matches Table 3.3, so after review we re-keyed it to line 28 as its tax head.
- The OBR's "increase borrowing by £5 billion in 2026-27" in paragraph 3.11 rounds Table 3.1's "Other departmental spending changes" (5.4). That group includes the DEL funding for the council tax rebate, and in Table 3.1 the OBR nets the rebate out of its "Other AME spending decisions" group instead (review B finding 9). So don't add the rebate row (2.6), the departmental group and the AME group together in 2026-27.
- The OBR's tax aggregates differ from HMT's in fiscal head and classification: for 2031-32 the OBR gives -£7.5bn against HMT's +£6.970bn. We use no total-tax registry key.
- In paragraph 3.2 the OBR rounds the 2031-32 borrowing reduction to £12bn, and it prints -11.7bn in Table 3.1. We keep both.
- In paragraph 3.41 the OBR speaks of social-care options, while in footnote 13 it calls the cited amounts “extra costs of healthcare”. We report them as printed, with no correction.
- The Health Foundation's range spans different reform options, not statistical uncertainty about one fixed policy.
- Nothing in the EFO shows that the whole-scheme UKEF exports in paragraph 3.21 match the defence-export capacity in HMT line 44. The OBR's India-UK FTA GDP claim leaves out the Double Contributions Convention component in HMT line 77. We key the UKEF borrowing row, which matches line 44, to that line, and stage the India FTA GDP row as a component of line 77.

## Validation

- On 4 November, the contract checker reported 2,800 rows and 0 problems, and when we re-ran `stage.py` in a scratch directory it reproduced the gzip byte for byte. We re-opened no primary in this session. The coordinator read the new quotes (Box 3.1's sentences) from its local copy of the 28 October PDF, and review B supplied the corrected PDF's hash and change history.
- On 3 November, the contract checker reported 2,797 rows, 0 problems, and when we re-ran `stage.py` it reproduced the gzip byte for byte (COUNTS.json pins its sha256). We re-opened no primary: the session's network policy refused obr.uk, and this lane's primaries come from the coordinator's local copies. We only relabelled, re-keyed or dropped rows, and changed no printed value.
- On 29 October, the lane ran the full-family checker, a deterministic gzip digest and 40 seeded random row checks, plus ten aggregate checks. Independent auditors verified all 2,520 workbook cells and all 316 chapter-3 rows. We deleted the lane's REPORT.md, the only report file any family included, under review finding 7.

## Review fixes, 3 November 2026

In its review (`harvest-staging/ab2026/reviews/verify-obr.md` on the staging branch, verdict REWORK), the OBR reviewer found the numbers sound and the keying, typing and design rows systematic. We applied every fix in `review_fixes()` in `stage.py`, with the coordinator's calls on findings 5, 6, 9 and 10:

1. **Design rows (rule 8):** we dropped 58 rows (see "Not staged") and moved the staffing figures into the yield rows' conditions.
2. **Components (rule 9):** we re-keyed 37 rows to their measure.
   - Direct recovery of debt, e-invoicing mandation, timely payment for self assessment and HMRC's compliance workforce became line 45 components, and verification assurance officers line 47's.
   - The India FTA GDP effect became line 77's, and Table 3.3's CSOP reform line 28's tax head.
   - UKEF's borrowing effect went to line 44, moved to 2030-31 because line 44 shows 0 in 2031-32. The Growth Guarantee Scheme's borrowing effects went to line 75, and the WDA and FYA yield to line 58.
   - We dropped rows 2693 and 2747 under finding 5, so their re-keys fell away. We retired nine proposed keys with these re-keys, and the WDA/FYA one too.
3. **Row types:** we marked Table 3.3's tax-head rows for lines 54, 61 and 46, the three behavioural-erosion rows and paragraph 3.12's welfare saving `row_type: measure_component`, and the bank surcharge's erosion row `cumulative`.
4. **Sign conventions:** on the workbook's indirect-effect rows we say they follow PSNB, and on its total rows that they mix two conventions.
5. **Repeats:** we dropped 37 rows (the coordinator's call; see "Not staged").
6. **Field fixes:** we gave row 2774 `decisions_effect_on_borrowing` with `component: gross additional investment income`. We keyed row 2828 to `ab2025__salary_sacrifice_pension_nics_cap_2000` with `recosting_of: autumn_budget_2025`, which the contract accepted. (We overrode that on 4 November: row 2734 in the 4f424b9 order is now a context row with a null key; see the end.)
7. **Files and paths:** we deleted REPORT.md, removed local machine paths from the manifest notes and these notes, and say in the PDF's manifest note that only this lane recorded its origin and hash.
8. **NOTES.md:** we regenerated the tallies, keys and the not-staged list from the rows.
9. **Key names:** we renamed keys under rule 2, as the key table above records. The Table 3.1 savings and property grouping covers receipts only, so we gave it its own key rather than the lines 61 and 62 package.
10. **Box 3.1:** we staged "a third of the yield" from the review's quotation, at medium confidence, under `ab2026__package_compliance_measures_announced`.

We give row indices above in the 29 October order. 2,797 rows: 2,891 − 58 − 37 + 1.

## README rule 10, 3 and 4 November 2026

The IFS reviewer of d5e323dc (finding 3) found this family's totals of the Budget's decisions on `revenue_change`. `rule10()` in `stage.py` applies README rule 10 after `review_fixes()`. It moves 81 rows, the OBR's stated effects of the Budget's decisions on PSNB, to `decisions_effect_on_borrowing`:

- Table 3.1 (42 rows): the total, direct and indirect effects of Government decisions, and the direct effects of tax and of spending measures. It also holds the two memo lines that split the direct effect between decisions on and off HM Treasury's policy decisions table.
- The policy workbook's Table 1.1 (36 rows): the total, direct and indirect effects of Government decisions, the direct effects of scorecard and of non-scorecard decisions, and the total of expenditure measures.
- Chapter 3's text (3 rows): paragraph 3.3's spending policies, paragraph 3.4's tax policy changes and paragraph 3.5's fall in departmental underspends, a part of the indirect effects.

The OBR sums its receipts heads, from air passenger duty to visa fees, into the workbook's total of receipts measures (6 rows, cells I490:N490, rows 2190–2195 counting from 0). We keep that total on `revenue_change`, the receipts line that `models.py` keeps apart from PSNB (delta review of 8b7b23db, finding 1). In Table 3.1 the OBR gives the same figures, in £ billion with the opposite sign, as the direct effect of tax measures, and we move those rows to `decisions_effect_on_borrowing`.

We now propose `fiscal_balance_change` for Table 3.1's memo on the current budget deficit (6 rows), and add to its sign convention that a positive value on this line increases that deficit. We keep `revenue_change` for the workbook's 288 lines by tax and spending head, Table 3.1's groups of measures, Table 3.3's costings and the prose costings of measures. In paragraphs 3.20, 3.21 and 3.43 the OBR gives four policies' effects on borrowing, and we had already put their seven rows on `decisions_effect_on_borrowing`. We changed no value or printed sign.

Counting from 0 in the 3 November order, we moved rows 2352–2357, 2490–2519, 2521, 2527, 2533–2563 and 2630–2641 (81 rows) and gave the memo rows 2642–2647 the proposed `fiscal_balance_change`. The contract checker reports 2,797 rows, 0 problems, and when we re-run `stage.py` it reproduces the gzip byte for byte.

`scorecard_db/signs.py` now reads the workbook's legend on both metrics: on `revenue_change` it runs the way PolicyEngine's sign does, and on `decisions_effect_on_borrowing` the other way. It reads the six workbook total rows whose sign convention starts "mixed:", and paragraph 3.6's two absolute averages, as having no single sign.

Review B also noted that we had put rows 2520, 2648 and 2649 (paragraphs 3.2 and 3.6) on `decisions_effect_on_borrowing`. So 91 rows in the family use that metric: the 81 that rule 10 moved, the seven of paragraphs 3.20, 3.21 and 3.43, and these three.

**Text that restates a Table 3.1 group (4 November, review B finding 12, option (a)).** Where the OBR's text restates a Table 3.1 group or measure as an effect on borrowing, we give it that row's metric. Table 3.1's "A positive sign implies an increase in borrowing" sets a sign convention; it doesn't state that a group gives the decisions' effect on PSNB. So we keep `revenue_change` for paragraph 3.11's "increase borrowing by £5 billion in 2026-27" (Table 3.1's "Other departmental spending changes", rounded), as for that group's rows.

## Reviews A and B, 4 November 2026

Review B (issue comments 6635496734 to 6635499259 on #231) approved this family with fixes, and review A's key harmonisation (6635870934) touched its rows. `review_fixes_nov4()` in `stage.py` applies them after `rule10()`, with indices in the 4f424b9 order, and we changed no printed value. Rows: 2,797 + 1 restored + 2 added = 2,800.

1. **The corrected PDF (finding 1):** we added a fourth manifest line and give the corrected date in row 2673's `reform_hint` and note; we keep the rows on the 28 October file.
2. **Parts and wholes on the total-decisions key (finding 2, review A's K-1 and H-1):**
   - We mark the totals `measure_total`, with no `component`.
   - We mark as `measure_component` the workbook's direct and indirect effects, its total of receipts measures and its 288 lines by head, Table 3.1's direct and indirect effects, and paragraphs 3.2 and 3.5, each labelled as its primary prints it.
   - We mark the workbook's scorecard and non-scorecard rows `measure_total` on their own keys, and give Table 3.1's total, indirect and current budget memo rows `source_model: obr_efo_forecast`.
3. **Receipts-only figures (finding 3, review A's K-5 and K-7(g)):** we mark paragraph 3.17's £0.4bn and paragraph 3.19's electricity VAT figures as receipts components of their lines. We gave the tax administration and temporary business rates groupings `_receipts` keys, and stage Table 3.3's online marketplace rows as line 46's whole costing.
4. **Chapters 1, 2 and 4–6 and paragraph 7.20 (finding 4):** we didn't stage them, and list each with its reason (the coordinator's call).
5. **Paragraph 3.20's financing requirement (finding 5):** we restored it on `cash_requirement_change`, under the rule for lending and financing above.
6. **Splits on the split keys (finding 6):** we stage the workbook's total of expenditure measures and paragraph 3.4's tax line as whole rows on the spending- and tax-decisions keys.
7. **Lines 70 and 71 (finding 7):** we give the carbon price package's scope, and key footnote 9's £0.8bn to line 70 as its current AME.
8. **More parts (finding 8):** we mark as components paragraph 3.20's gross debt and additional income, paragraph 3.12's two pension heads and paragraph 3.19's AME to local authorities (now `revenue_change`, as worded). We also mark as components Table 3.3's four rating rows that name a part (H-1).
9. **Two spending scopes (finding 9):** we restated them.
10. **Box 3.1 (finding 10):** we stage the whole sentence, from the coordinator's reading of the 28 October PDF.
11. **Box 3.1's counts (finding 11):** we staged them.
12. **Paragraph 3.11 (finding 12):** we took option (a), above.
13. **Averaging intervals (finding 13):** row 2529 averages from 2027-28; the OBR doesn't state row 2522's interval.
14. **Civil service programme (finding 14):** we call its membership probable, not established.
15. **The OBR's residual groups (finding 15):** they keep `obr` in their keys.
16. **Stale and run-together text (finding 16):** we corrected the row notes and these NOTES, and `review_fixes_nov4()` inserts the missing spaces in every field but quotes, values and locators.

Under review A's K-2 we make row 2522 the defence investment plan's RDEL part, with the sign convention "positive = cost to the Exchequer (higher RDEL spending)". Under K-6 we keep RF's RPI-uprating option apart from this family's fuel duty freezes key. Under K-7(d) we give paragraph 3.51's two simulations conventions that `signs.py` reads. Under H-6(b), the coordinator's call, we make paragraph 3.28's revision a context row with a null key and no `recosting_of`.
