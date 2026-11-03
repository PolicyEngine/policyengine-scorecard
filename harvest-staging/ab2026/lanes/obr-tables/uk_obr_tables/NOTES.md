# uk_obr_tables — October 2026 Economic and fiscal outlook

Staged 2026-10-29. Source `obr_efo`. **2,891 rows, 3 primaries, 98 individual registered measures plus the registered total-policy package.** All outputs are confined to this family. `stage.py` embeds all reviewed rows as metadata templates and cell data; rerunning needs only the Python standard library and reproduces the gzip without primary files or network access.

## Access recipe and primaries

Each resolved URL in the supplied OBR `PROVENANCE.md` was attempted once using `curl -sSL` and the exact Safari User-Agent requested in the assignment. The EFO landing page returned **403** at 2026-10-29T15:51:17Z; the chapter-2 workbook and detailed-table ZIP resolved URLs returned **403** at 15:51:18Z. No bypass was attempted. We used the supplied local policy and aggregate workbook members and PDF; every row and manifest entry records `access: "local copy"`.

Local source directory: `/Users/maxghenis/reviews/scorecard-ab2026-harvest/local-primaries/obr/`. Exact byte copies, failed-response headers/bodies and fetch timestamps are retained under ignored `.ab2026-primaries/uk_obr_tables/`. Workbooks were read with openpyxl `data_only=True`; the PDF with `pdftotext -layout`. `shasum -a 256` verified all three primaries. Both workbook member hashes match the browser-download provenance from 28 October, including the ZIP's recorded Last-Modified of Wed, 28 Oct 2026 14:05:59 GMT.

The resolved ZIP URL is the publication URL for both members, with the member name in each row's note and the manifest. The ZIP container itself was not supplied locally and is not represented as if it had been read. The PDF attachment URL is absent from PROVENANCE; the blocked landing page prevented discovering it. Its manifest and rows therefore use the EFO landing URL and identify the supplied local PDF filename. The cover/imprint say October 2026; publication date 2026-10-28 follows the EFO-page date recorded in PROVENANCE. No replacement version could be compared after the refusals, and no changed-primary claim is made.

| Primary file | Rows | Bytes | SHA-256 |
|---|---:|---:|---|
| efo-october-2026-detailed-forecast-tables-policy.xlsx | 2,520 | 106,602 | `cdcc2a06b100241bf3010bd159a4e5d43daef2348a3850797b1e88a308fd45fd` |
| economic-and-fiscal-outlook-october-2026-web-accessible.pdf | 358 | 1,754,344 | `9e0e9c340e35e603066f3124a614fcd68feadb3d5d10d1f76fb536e150e6225e` |
| efo-october-2026-detailed-forecast-tables-aggregates.xlsx | 13 | 218,000 | `3ffa3f1e63667b2ae9fb9626dc1da881673227d43aeeb52f8c3db168a5c75d6b` |

## Coverage

- Policy workbook Table 1.1: **2,520** cells, every numeric row series (420) across all six fiscal years, 2026-27 through 2031-32. This includes 2,112 numbered-measure component/total cells, 48 fiscally neutral cells, 30 non-scorecard cells and 330 summary cells.
- EFO chapter 3: **316** rows: Table 3.1 126; Table 3.2 47 numeric funding cells; Table 3.3 35 costings plus 7 categorical uncertainty ratings; policy/behavioural prose 101.
- Headline fiscal context: **55** rows: 13 workbook cells (PSNB cash six years; ex-BoE PSND/GDP seven years) and 42 PDF cells (Table 7.1 headroom 13; Annex A Table A.9 PSNB, PSNFL and ex-BoE PSND 29). The current-budget and PSNFL rules include current pre-measures, post-measures and the printed memo excluding fuel-duty rises; welfare-cap margin is included. Forecast duplicates between the PDF and aggregate workbook are represented once.

## Conventions

- **Values and precision:** policy workbook values use their displayed integer £million formats (`0`, `#,##0`; eight exact General-format zeros), multiplied by 1e6. Unprinted cached decimal precision is not a claim. Decimal rounding is half away from zero; a stored negative fraction that displays zero is `0`. A LibreOffice PDF rendering independently confirmed these display conventions. Aggregate workbook values use displayed one-decimal precision. PDF £billion values multiply by 1e9 and £million by 1e6; no ratios, sums or inferred annual paths are staged.
- **Signs:** policy workbook prints “This table uses the convention that a negative sign implies a loss to the Exchequer (and is therefore an increase in PSNB).” PDF Tables 3.1/3.3 print “A positive sign implies an increase in borrowing.” Both are retained. The indirect-effect workbook row's conflict with that workbook legend is explicitly noted in those rows. Prose uses positive magnitudes for costs, yields or behavioural erosion exactly as worded; per-row conditions state the meaning. Funding amounts are positive cost provision, except the printed negative change. Headroom is positive margin, negative breach.
- **Period:** FY end year, with the printed `fy`; quarterly CPI peaks use calendar-year `point_in_time` and quarter detail without `fy`. An annual average or recurring prose amount appears once at the terminal forecast FY, with its interval in `aggregation`, rather than manufacturing six yearly values. The 5,500 previously announced HMRC recruits have no separately printed delivery year and are an announcement input at point-in-time 2026; the separate 670 figure retains its printed 2029-30 horizon. Debt stocks preserve end-March timing and end-March-centred GDP denominators.
- **Central:** ordinary policy tables/prose are `point` estimates of the single final forecast; aggregate forecasts are `central`, meaning the OBR central forecast, and observed 2025-26 outturns are `point`. No statistical confidence interval is inferred. “High” ratings use categorical `value: 0` as the precedent's schema placeholder, not a numerical score. Health Foundation range endpoints span alternative reform options, not uncertainty for one policy.
- **Attribution:** 2,821 `own`, 70 `restated`. OBR-certified/HMRC/DWP-scrutinised costings follow the AB2025 `own` convention; OBR fiscal judgments use `obr_efo_forecast`. Twelve workbook fuel cells and two PDF fiscal fuel costings are restated `hmt_costing_uncertified`: EFO p.59 footnote 1 says the final Government costing arrived after certification. Table 3.2's 47 funding cells name HM Treasury as original source; six latest ONS outturn aggregate cells name ONS. Two social-care options name Health Foundation; one FTA effect names the Government/DBT impact assessment. OBR's CPI judgments remain its own estimates. Funding/ONS facts use `administrative_fact`; modeled estimates use `different_model`.
- **Scope:** all 98 numbered workbook titles match registry titles after whitespace/footnote normalization. Fiscal-head components retain their full measure's key, with component conditions; totals and components must not be summed as independent estimates. Only workbook row552 and the PDF's explicit HMT-policy-table memo use the registered total-policy package. All other groupings use null plus a proposed key. Context levels use null without a proposed measure. The lone prior-policy salary-sacrifice recosting stays null as assigned; it is not recast as an AB2026 intervention. The AB2025 OBR family actually contains no headline fiscal aggregates; the live `Metric` enum supplies `fiscal_headroom`, and cross-family proposals supply the closest aggregate names.
- **Quotes/order:** full numeric/rating cells or full OGL prose sentences, preserving the printed number; PDF whitespace/line wraps normalized, footnote superscripts excluded from sentence text. Reading order is policy workbook row/column, PDF page/position, then aggregate workbook table/row/column. PDF printed page + 3 is the physical PDF page.

## Coverage by measure_key, including null

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
| `ab2026__british_industrial_competitiveness_scheme` | 24 |
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
| `ab2026__dwp_fraud_and_error_prevention` | 34 |
| `ab2026__early_years_books_access` | 12 |
| `ab2026__electricity_generator_levy_55pc` | 12 |
| `ab2026__electricity_vat_zero_rate_to_july_2027` | 20 |
| `ab2026__emi2_option_limit_120000` | 42 |
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
| `ab2026__growth_guarantee_scheme_expansion` | 18 |
| `ab2026__hgv_ved_1_for_12_months` | 12 |
| `ab2026__high_needs_local_authority_spending` | 18 |
| `ab2026__hmrc_tax_gap_package` | 84 |
| `ab2026__household_energy_payment_100_bands_a_to_d` | 20 |
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
| `ab2026__uk_export_finance_defence_capacity` | 12 |
| `ab2026__uk_india_ceta_and_double_contributions_convention` | 18 |
| `ab2026__ukraine_winter_air_defence` | 18 |
| `ab2026__union_learning_fund` | 12 |
| `ab2026__us_llc_double_taxation_relief` | 12 |
| `ab2026__vat_5pc_family_days_out_summer_2026` | 12 |
| `ab2026__vat_medical_deputies_staffing` | 12 |
| `ab2026__vat_reverse_charge_overseas_services_restricted` | 12 |
| `ab2026__vat_zero_rate_donated_medicines` | 12 |
| `ab2026__vat_zero_rate_land_for_social_housing` | 12 |
| `ab2026__waste_crime_landfill_tax_clearances` | 18 |
| `ab2026__writing_down_allowance_12pc_and_fya_50pc` | 42 |
| `ab2026__your_first_home_equity_loan` | 21 |
| `ab2026__youth_guarantee_and_apprenticeships_spring_2026` | 18 |
| `null` | 711 |

## Proposed measure keys and exact producer scopes

All of these rows have `measure_key: null`. Known Table 6.1 components are stated below. Where OBR publishes only a named residual group, its complete line decomposition is explicitly unresolved; no guessed membership or existing registry key is attached. Those proposals need reconciliation before registration.

| Proposed key | Rows | Scope |
|---|---:|---|
| `ab2026__package_obr_additional_uk_export_finance_guarantees` | 2 | No exact Table6.1 scope certified: OBR paragraph3.21 £40bn additional UK Export Finance guarantees for British exports2027-28to2030-31. Related line44 is specifically defence exports fromJune2026, whereas OBR text describes exports generically. |
| `ab2026__package_obr_adjusted_state_pension_triple_lock` | 2 | No Table6.1 line: OBR paragraph3.49 adjusted state pension triple lock expected April2030, retaining CPI/2.5percent floor but linking catch-up to2029-30 earnings ratio. Figures3.51 are historical simulations1990–2025, not the medium-term policy costing. |
| `ab2026__package_obr_carbon_price_support_and_cfd_levies` | 3 | Table 6.1 line 71 plus funding for Low Carbon Contracts Company to reduce CfD levies (no separately identifiable line in Table 6.1); related support for BICS/Supercharger includes line 70. OBR paragraph 3.19 combines these measures and dates CPS abolition April 2027, while HMT line 71 says April 2028. |
| `ab2026__package_obr_civil_service_transformation_programme` | 1 | Table 6.1 lines 63 and 64 net programme: “civil service transformation programme ... reduce resource spending”. |
| `ab2026__package_obr_company_share_option_plan_reform` | 6 | OBR Table 3.3 “Company Share Option Plan scheme reform” and paragraph 3.24 CSOP individual option limit and EMI interaction. No exact Table 6.1 line: line 28 instead calls its measure “Enterprise Management Incentives 2 (EMI2)”. |
| `ab2026__package_obr_corporation_and_bank_tax_changes` | 8 | OBR “Changes to corporation and bank taxation”; paragraph3.16 explicitly discusses line58 WDA/FYA, line55 bank surcharge, and line54 overseas sovereign immunity. Complete Table6.1 line decomposition and fiscal-head allocation are not published; unresolved, no inferred additional membership. |
| `ab2026__package_obr_defence_investment_plan` | 2 | OBR “funding for the defence investment plan” / “the defence investment plan, which increases departmental resource spending (RDEL)”; related to Table6.1 Defence Investment Plan entries, but complete line decomposition is not published and is unresolved. No inferred40–43 membership. |
| `ab2026__package_obr_departmental_spending_growth_2031_32` | 14 | No Table 6.1 lines. “Departmental spending: Grow day-to-day spending by 0.7% in real terms in 2031-32, matching 0.7% average annual real terms growth from 2029-30 to 2030-31”. PDF describes the same baseline change as a £5.5bn reduction in the 2031-32 pre-measures RDEL assumption. |
| `ab2026__package_obr_direct_recovery_of_debt` | 6 | Component of Table 6.1 line 45: “Direct recovery of debt” in Table 3.3. |
| `ab2026__package_obr_dividend_and_capital_gains_tax_changes` | 6 | Table 6.1 lines 26,49 and 60: OBR “Changes to dividend and capital gains taxation”. |
| `ab2026__package_obr_e_invoicing_mandation` | 6 | Component of Table 6.1 line 45: “E-invoicing mandation” in Table 3.3. |
| `ab2026__package_obr_fuel_duty_and_electricity_vat` | 12 | Table 6.1 lines 2 and 3 only; OBR “Fuel duty freeze and VAT off domestic energy bills”. Excludes household council-tax rebate line 1. |
| `ab2026__package_obr_government_decisions_since_march_2026` | 365 | Table 6.1 lines 1–98, plus the three fiscally neutral measures (PWLB debt relief, Scottish APD devolution, landlord registration fee) and the two non-scorecard policies listed above. OBR “Total effect of Government decisions”, with direct, indirect, receipt, expenditure and fiscal-head projections distinguished in conditions. Includes indirect effects where stated; not the HMT scorecard-only package. |
| `ab2026__package_obr_growth_guarantee_scheme_7bn` | 4 | OBR paragraph 3.21 “£7 billion expansion of the Growth Guarantee Scheme”; related to Table 6.1 line 75, whose title says £6.5bn. Scope/amount discrepancy prevents exact registry-key match. |
| `ab2026__package_obr_historical_fuel_duty_freezes_and_5p_cut` | 1 | OBR cumulative 2010-11 to 2027-28 fuel duty freezes and 5p cut relative to stated RPI uprating; includes Table6.1 line3 and earlier freezes since2010-11. Not the cost of the AB2026 measure alone. |
| `ab2026__package_obr_hmrc_compliance_workforce` | 4 | Component of Table 6.1 line 45: acceleration of 5,500 compliance officers and an additional 670 staff, called “Changes to HMRC’s compliance workforce”. |
| `ab2026__package_obr_india_uk_free_trade_agreement` | 1 | Table6.1 line77 FTA component only: India-UK Free Trade Agreement GDP effect; excludes Double Contributions Convention also named in the registered line77 package. |
| `ab2026__package_obr_landlord_registration_fee` | 18 | No Table 6.1 lines. “Landlord registration fee”; receipts, current DEL and total. |
| `ab2026__package_obr_national_wealth_fund_and_british_business_bank` | 5 | Table 6.1 lines 29 and 30 together, plus their associated financial transactions in Table 6.2; OBR “funding available for the National Wealth Fund and the British Business Bank ... to invest in financial assets”. |
| `ab2026__package_obr_non_scorecard_decisions` | 12 | No Table 6.1 lines. “Direct effect of non-scorecard decisions”: exactly the departmental spending assumption and public-pension valuation changes above. |
| `ab2026__package_obr_other_ame_spending_decisions` | 6 | OBR Table 3.1 “Other AME spending decisions”; excludes net unfunded pensions valuation. Producer does not supply a full Table 6.1 line-number decomposition in PDF. |
| `ab2026__package_obr_other_departmental_spending_changes` | 9 | OBR Table 3.1 “Other departmental spending changes”, excluding council tax rebate line 1; includes defence, capital spending and the £5.5bn 2031-32 pre-measures RDEL reduction, which has no Table 6.1 line. Producer does not supply a full line-number decomposition in PDF. |
| `ab2026__package_obr_other_hmrc_compliance_and_debt` | 1 | OBR paragraph 3.13 residual “Other measures”: direct debt recovery, e-invoicing, debt collection agencies (components of Table 6.1 line 45), and online marketplace liability (line 46). |
| `ab2026__package_obr_other_tax_measures` | 9 | OBR Table 3.1 “Other tax measures”; residual of Table 6.1 tax measures after tax administration/compliance/debt, corporation/bank, savings/property, dividend/CGT and fuel/electricity VAT groups. PDF does not enumerate a full line-number decomposition. |
| `ab2026__package_obr_planned_capital_spending_reductions` | 2 | OBR “Reductions in planned capital spending” / “changes to departmental capital spending”; PDF does not enumerate the exact Table 6.1 lines. |
| `ab2026__package_obr_public_sector_pensions_2024_valuations` | 28 | No Table 6.1 lines. “Public Sector Pensions: Net impact of the 2024 valuations”; departmental reductions, net public service pension payments and their net total. PDF calls this “Net impact of unfunded pensions valuation”. |
| `ab2026__package_obr_pwlb_distress_debt_relief` | 12 | No Table 6.1 lines. “Provide Public Works Loan Board (PWLB) debt relief for councils in severe financial distress”; capital AME and total. |
| `ab2026__package_obr_savings_and_property_income_tax_rates` | 8 | Table 6.1 lines 61 and 62 only: “Changes to savings and property income tax rates”. |
| `ab2026__package_obr_scottish_air_passenger_duty_devolution` | 18 | No Table 6.1 lines. “Devolving Air Passenger Duty to the Scottish Government in April 2027”; Scottish BGA, self-financed expenditure and total. |
| `ab2026__package_obr_spending_decisions_since_march` | 14 | OBR “Direct effect of spending measures” / “Spending measures”: expenditure-side effects of decisions since March, including unfunded public service pensions valuation and the £5.5bn 2031-32 RDEL assumption reduction. This is not the HMT total-spending package. Table 6.1 lines 1–98 can affect expenditure fiscal heads; a complete narrower line decomposition is not published and remains unresolved. |
| `ab2026__package_obr_tax_administration_compliance_and_debt` | 14 | OBR “Tax administration, compliance and debt collection measures”, including Table6.1 line45 (HMRC tax-gap package) and line46 (online marketplace liability), with funding/receipt interactions. PDF group yield (£3.6bn2031-32) differs from standalone line45 (£3.160bn) and must not be attached to line45 alone. |
| `ab2026__package_obr_temporary_business_rates_reliefs` | 1 | Table 6.1 lines 12,13,14: “package of temporary business rates measures” including real-terms freeze for certain sectors, pubs/live-music reliefs, small-business thresholds and extension of transitional support, partly offset by transitional relief supplement. |
| `ab2026__package_obr_timely_payment_self_assessment` | 9 | Component of Table 6.1 line 45 “HMRC: Measures to close the tax gap”, called “Timely payment for self-assessment” by OBR; includes part reversal of AB2025 PAYE coding-out. |
| `ab2026__package_obr_verification_assurance_officers` | 6 | Component of Table 6.1 line 47: “Verification assurance officers” in Table 3.3. |
| `ab2026__package_obr_wda_and_first_year_allowance_as_printed` | 2 | Table6.1 line58-related WDA/FYA policy as described by OBR paragraph3.16: WDA14to12percent and FYA40to50percent from April2027; HMT line58 instead dates FYA increase1January2027. Exact timing mismatch prevents direct key assignment. |
| `ab2026_option__obr_fuel_duty_frozen_until_2029_30` | 1 | No Table6.1 line as an announced measure: OBR paragraph3.43 counterfactual “if fuel duty were to remain frozen until 2029-30”, extending line3 beyond July2027. |
| `ab2026_option__obr_health_foundation_social_care_reforms` | 2 | No Table6.1 line: Health Foundation illustrative future social care reforms cited by OBR paragraph3.41, from limited home-care reform to wider schemes including residential care; costs additional to current spending in2035-36 per footnote13. This is not a settled AB2026 policy. |

## Metric, unit and baseline proposals

No unregistered enum literals are used. `fiscal_headroom` is registered in the live models even though the older README calls it a proposal.

| proposed_metric | Rows | Scope |
|---|---:|---|
| `cash_receipts_change` | 1 | Self-assessment overlapping transition payments, £17bn in 2029-30; assumed extraordinary accruals adjustment excludes the temporary cash effect from PSNB. |
| `compliance_funding` | 35 | Annual baseline, earlier-Budget and total HMRC compliance/debt and DWP fraud/error funding, Table 3.2; GBP funding level, not net yield. |
| `costing_uncertainty_rating` | 7 | Table 3.3 High final ratings; categorical placeholder zero. |
| `psnb_share_of_gdp` | 7 | PSNB as percent of nominal GDP. |
| `psnd_share_of_gdp` | 7 | Ex-Bank-of-England PSND as percent of nominal GDP; reuses AB2025 cross-family spelling. |
| `psnfl_share_of_gdp` | 7 | PSNFL as percent of nominal GDP; reuses AB2025 cross-family spelling. |
| `public_sector_net_borrowing` | 7 | Annual PSNB cash level in GBP. |
| `public_sector_net_debt` | 7 | End-March PSND stock explicitly excluding Bank of England, GBP. |
| `public_sector_net_debt_change` | 3 | Marginal stock debt effects of NWF/BBB investment and Your First Home lending, paragraphs 3.20/3.22. |
| `public_sector_net_financial_liabilities` | 7 | End-March PSNFL stock, GBP. |
| `tax_base` | 8 | Printed staffing and guarantee-capacity inputs, paragraphs 3.12/3.13/3.21, in jobs, percent or GBP. |

Proposed units: `percent_of_gdp` (28 rows, nominal GDP denominator, including one prose package effect and fiscal shares/headroom); `rating_category` (7 High uncertainty ratings).

Every `baseline_policy` is null; effect estimates use the following explicit unregistered baseline proposals. Rating, funding-level and aggregate context rows have no proposed baseline.

| proposed_baseline, verbatim | Rows |
|---|---:|
| OBR pre-measures Autumn Budget 2026 policy parameters | 2776 |
| Fuel duty policy reflected in OBR October 2026 economy forecast, confirmed before the final Budget parameters | 1 |
| Current social care spending (Health Foundation2024 scenarios, additional spending in2035-36) | 2 |
| Fuel duty rates increase in line with RPI inflation: stated policy since 2010-11 | 1 |
| Current triple lock uprating applied to historical outturn1990–2025 | 1 |
| Earnings uprating applied to historical outturn1990–2025 | 1 |

## Not staged and unreachable material

- AnnexA has no policy-costing narrative beyond introductionA.1; current receipts/spending/economy forecast TablesA.1–A.8/A.11–A.12 are outside the policy-family scope. Headline fiscal aggregates inA.9 are owned by aggregate lane.
- No printed numeric Pension Tax Allowance or Carer’s Allowance taper claim appears in chapter3 or AnnexA. Whole-PDF search finds no PTA phrase; Carer’s Allowance appears only in a generic welfare footnote, not taper costing. These measures are covered by workbook rows.
- Charts3.1–3.4 and Box3.1 ChartsA/B contain no printed data labels for the policy values; no bars or paths read. Tick labels and dates are not claims. Box3.1 tax-gap context restates HMRC and several-Budget historical compliance yields; omitted to match assigned current policy tables scope.
- Policy design parameters (tax rates/thresholds, dates, litres/pence) without costing or behavioural-estimate content were not separately staged.
- Older-policy employment/housing/childcare monitoring examples in3.29–3.36 do not cost an AB2026 Table6.1 measure; no new AB2026 measure key invented. Paragraph3.28’s salary-sacrifice recosting amount is retained null-key as explicitly permitted for non-Table6.1 lines.
- Paragraph3.48 FRS long-run pension/debt scenarios are current-policy/earlier-publication context, outside requested headline medium-term aggregate scope. Paragraph3.52 adjusted-triple-lock debt effects are explicitly2075-76=>2076; checker caps periods at2075, so neither25pp nor10pp long-run debt effect was staged or misdated.
- Table3.2 Budget2025 additional DWP funding2031-32 is printed dash, not a number. Omitted rather than inventing zero.
- No additional primary access attempts owned by text lane; root records direct/local recipe and unreachable EFO landing page in manifest/NOTES.

- The policy workbook contains no static/post-behavioural split or rating matrix, and no recosting table. Fiscal-head rows are not labeled as static or behavioural. Contents/navigation cells are not additional claims.
- The supplied chapter-2 charts workbook and the other economy, receipts, expenditure and debt-interest workbooks are outside the policy/headline scope. The chapter-2 fresh URL was 403; it was not used. No economy-wide GDP/CPI paths were staged; only explicit policy CPI/GDP effects.
- The EFO landing page, resolved detailed-tables ZIP and chapter-2 workbook URLs were unreached (403). The PDF attachment URL could not be discovered. No missing online content, new attachments or separate latest ratings database was presumed available or silently substituted. The seven printed PDF ratings are included.


## Contradictions and limitations retained

- Workbook row549 “Total effect of Government decisions” displays **-8,905 / -50 / 1,322 / 5,484 / 6,425 / 14,093 £m**, while PDF Table 3.1 prints **6.3 / 7.0 / 2.1 / -2.6 / -3.5 / -9.3 £bn**. This exceeds a sign flip or rounding difference. Workbook direct row551 follows its negative-loss legend; indirect row555 has the same signs as the PDF borrowing effects. The workbook appears to mix conventions in its total. Both sources remain unchanged; row notes call out the inconsistency.
- Workbook/HMT precision differs: Household Energy Payment is -2,627 £m here versus -2,625 £m in HMT Table 6.1. Rounded components need not sum to the separately rounded totals.
- Paragraph3.19 dates carbon-price-support abolition April2027; HMT line71 says April2028. Its combined CPS/CfD/BICS/Supercharger scope uses a proposal, not CPS key.
- Paragraph3.16 dates first-year-allowance increase April2027; HMT line58 dates1January2027. WDA/FYA claims use as-printed proposal.
- Paragraph3.21 says£7bn Growth Guarantee expansion; HMT line75 says£6.5bn additional SME lending. Separate proposed scope.
- Table3.3/paragraph3.24 call reform Company Share Option Plan (CSOP); HMT line28 says Enterprise Management Incentives2 (EMI2). Not equated.
- Paragraph3.11 says departmental spending+£5bn2026-27; Table3.1 “Other departmental spending changes”+£5.4bn and separate rebate+£2.6bn. Preserved without inventing reconciliation.
- OBR tax aggregates include fiscal-head/classification differences from HMT:2031-32 OBR -£7.5bn against HMT+£6.970bn. No total-tax registry key used.
- Paragraph3.2 prose rounds2031-32 borrowing reduction to£12bn; Table3.1 prints-11.7bn. Both preserved.
- Paragraph3.41 says social-care options; footnote13 calls cited amounts “extra costs of healthcare”. Reported as printed, no correction.
- Health Foundation range is across different reform options, not statistical uncertainty about one fixed policy.
- Whole-Scheme UKEF exports in paragraph3.21 are not proven identical to defence-export capacity in HMT line44. India-UK FTA GDP claim does not include Double Contributions Convention component in HMT line77. Both use proposals.

## Validation

See `REPORT.md` for the executed full-family checker, deterministic gzip digest and 40 seeded random final-row checks, plus ten supplementary aggregate checks. Independent audits also verified all 2,520 workbook cells (coverage, display, normalization, period and 98 title lineages) and all 316 chapter-3 rows (including all 215 table cells). Four apparent quote mismatches were page continuations or footnote removal, re-opened and confirmed. No primary number was corrected to reconcile a discrepancy.

No COUNTS, registry, shared README, tests or other family was edited. Git state was not mutated, and no commit, push or PR was made, following the assignment-specific instruction. Global count/pinning tests are intentionally left for the coordinator that merges this unpinned family; the standalone family contract is the required check here.

