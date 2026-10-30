# Recent OBR fiscal-event replays

These replays ran on certified variant `pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1`. PolicyEngine is policyengine-uk 2.130.1 with policyengine 6.9.0, on certified data build policyengine-uk-data-1.58.1: one survey population whose data years are 2024–2032, projected by the engine to calendar year Y. Reform dictionaries use explicit 1 January windows for annual lookups (compute_uk_event.annual_reform). Registry years outside the population's data years are reported as unsupported, not computed. A seeded registry does not establish a completed numerical replay. Available comparisons use one source head and fiscal year per row.

Numerical comparison outputs available: 6. Registry inventories available: 6.

| Event | Replay state | Measures | Source rows | Computed rows | Computed FYs |
|---|---|---:|---:|---:|---|
| [autumn_budget_2024](autumn_budget_2024/COMPARISON.md) | Registered construction replay complete | 74 | 1134 | 34 | 2024-25, 2025-26, 2026-27, 2027-28, 2028-29, 2029-30 |
| [autumn_budget_2025](autumn_budget_2025/COMPARISON.md) | Registered construction replay complete | 105 | 1512 | 90 | 2025-26, 2026-27, 2027-28, 2028-29, 2029-30, 2030-31 |
| [autumn_statement_2023](autumn_statement_2023/COMPARISON.md) | Registered construction replay complete on supported years; unsupported: 2023 | 77 | 1116 | 50 | 2024-25, 2025-26, 2026-27, 2027-28, 2028-29 |
| [spring_budget_2023](spring_budget_2023/COMPARISON.md) | Registered construction replay complete on supported years; unsupported: 2023 | 89 | 1020 | 12 | 2024-25, 2025-26, 2026-27, 2027-28 |
| [spring_budget_2024](spring_budget_2024/COMPARISON.md) | Registered construction replay complete on supported years; unsupported: 2023 | 49 | 816 | 40 | 2024-25, 2025-26, 2026-27, 2027-28, 2028-29 |
| [spring_statement_2025](spring_statement_2025/COMPARISON.md) | Registered construction replay complete | 32 | 498 | 12 | 2024-25, 2025-26, 2026-27, 2027-28, 2028-29, 2029-30 |

## Source inventory accounting

These amounts sum all source heads and costing years, including zero cells. They are inventory totals, not one-year event costings or numerical agreement statistics.

| Event / class | Measures | Source rows | Net OBR £bn | Absolute OBR £bn |
|---|---:|---:|---:|---:|
| autumn_budget_2024 / expressible | 0 | 0 | 0.000 | 0.000 |
| autumn_budget_2024 / partial | 5 | 60 | 148.279 | 152.288 |
| autumn_budget_2024 / not_expressible | 43 | 438 | 42.163 | 71.094 |
| autumn_budget_2024 / out_of_household_scope | 26 | 636 | -380.606 | 477.285 |
| autumn_budget_2025 / expressible | 1 | 6 | 1.398 | 1.398 |
| autumn_budget_2025 / partial | 8 | 138 | 19.726 | 73.212 |
| autumn_budget_2025 / not_expressible | 51 | 510 | -8.198 | 82.650 |
| autumn_budget_2025 / out_of_household_scope | 45 | 858 | 7.180 | 185.626 |
| autumn_statement_2023 / expressible | 0 | 0 | 0.000 | 0.000 |
| autumn_statement_2023 / partial | 4 | 84 | -55.217 | 65.982 |
| autumn_statement_2023 / not_expressible | 35 | 318 | 15.971 | 21.286 |
| autumn_statement_2023 / out_of_household_scope | 38 | 714 | -67.493 | 99.223 |
| spring_budget_2023 / expressible | 0 | 0 | 0.000 | 0.000 |
| spring_budget_2023 / partial | 2 | 18 | -2.014 | 2.014 |
| spring_budget_2023 / not_expressible | 39 | 324 | -22.202 | 40.640 |
| spring_budget_2023 / out_of_household_scope | 48 | 678 | -63.834 | 83.759 |
| spring_budget_2024 / expressible | 0 | 0 | 0.000 | 0.000 |
| spring_budget_2024 / partial | 3 | 48 | -51.930 | 58.201 |
| spring_budget_2024 / not_expressible | 26 | 276 | 9.152 | 28.291 |
| spring_budget_2024 / out_of_household_scope | 20 | 492 | -1.255 | 25.416 |
| spring_statement_2025 / expressible | 0 | 0 | 0.000 | 0.000 |
| spring_statement_2025 / partial | 2 | 18 | 2.365 | 13.031 |
| spring_statement_2025 / not_expressible | 17 | 156 | 13.906 | 22.174 |
| spring_statement_2025 / out_of_household_scope | 13 | 324 | -10.696 | 39.774 |

### Not-expressible gap split

construction_pending identifies unfinished replay constructions; model_or_data_gap identifies evidenced model or data limitations.

| Event / gap kind | Measures | Source rows | Net OBR £bn | Absolute OBR £bn |
|---|---:|---:|---:|---:|
| autumn_budget_2024 / construction_pending | 14 | 114 | -2.503 | 21.454 |
| autumn_budget_2024 / model_or_data_gap | 29 | 324 | 44.666 | 49.640 |
| autumn_budget_2025 / construction_pending | 36 | 366 | -18.921 | 66.119 |
| autumn_budget_2025 / model_or_data_gap | 15 | 144 | 10.723 | 16.531 |
| autumn_statement_2023 / construction_pending | 24 | 204 | 8.607 | 10.499 |
| autumn_statement_2023 / model_or_data_gap | 11 | 114 | 7.364 | 10.787 |
| spring_budget_2023 / construction_pending | 23 | 180 | -18.605 | 22.208 |
| spring_budget_2023 / model_or_data_gap | 16 | 144 | -3.597 | 18.432 |
| spring_budget_2024 / construction_pending | 17 | 192 | -4.211 | 14.828 |
| spring_budget_2024 / model_or_data_gap | 9 | 84 | 13.364 | 13.463 |
| spring_statement_2025 / construction_pending | 6 | 42 | 4.520 | 4.858 |
| spring_statement_2025 / model_or_data_gap | 11 | 114 | 9.386 | 17.316 |

## Agreement profile

| Tax head | Source-row ratio bins |
|---|---|
| Aggregates levy | not_available: 6 |
| Air passenger duty | not_available: 18 |
| Alcohol duty | not_available: 42 |
| Bank surcharge | not_available: 24 |
| Betting | not_available: 24 |
| Building safety levy | not_available: 6 |
| Business rates | not_available: 66 |
| CBAM | not_available: 18 |
| Capital gains tax | not_available: 162, obr_zero: 1, opposite_sign: 1, same_sign_ratio_at_least_2: 4 |
| Climate change levy | not_available: 30 |
| Company and other credits | not_available: 60 |
| Corporation tax (onshore) | not_available: 324 |
| Council Tax | not_available: 36 |
| Crime levy | not_available: 12 |
| Customs duty | not_available: 72 |
| Electricity generators levy | not_available: 12 |
| Emissions trading scheme | not_available: 12 |
| Energy bills subsidies | not_available: 24 |
| Energy profits levy | not_available: 12 |
| Environmental levies | not_available: 18 |
| Fuel Duty | not_available: 24 |
| Fuel duty | not_available: 6 |
| Gross operating surplus | not_available: 18 |
| High-value council tax surcharge | both_zero: 3, same_sign_ratio_0.8_to_1.25: 3 |
| Immigration health surcharge | not_available: 6 |
| Immigration skills charge | not_available: 6 |
| Income tax | both_zero: 17, not_available: 530, obr_zero: 1, opposite_sign: 2, pe_zero: 30, same_sign_ratio_0.5_to_0.8: 2, same_sign_ratio_0.8_to_1.25: 7, same_sign_ratio_1.25_to_2: 3, same_sign_ratio_at_least_2: 19, same_sign_ratio_below_0.5: 1 |
| Inheritance tax | not_available: 102 |
| Insurance premium tax | not_available: 6 |
| Interest and dividend receipts | not_available: 66 |
| International student levy | not_available: 6 |
| Landfill tax | not_available: 30 |
| Locally-financed capital expenditure | not_available: 36 |
| Locally-financed current expenditure | not_available: 162 |
| Multinational top-up tax | not_available: 6 |
| NICs | both_zero: 10, not_available: 223, pe_zero: 14, same_sign_ratio_0.5_to_0.8: 2, same_sign_ratio_0.8_to_1.25: 25, same_sign_ratio_1.25_to_2: 8 |
| Net public service pension payments | not_available: 24 |
| North sea taxes | not_available: 6 |
| Other AME (capital) | not_available: 12 |
| Other AME (current) | not_available: 96 |
| Other departmental expenditure (capital) | not_available: 36 |
| Other departmental expenditure (current) | not_available: 12 |
| Other tax | not_available: 18 |
| PSCE in RDEL | not_available: 1176 |
| PSGI in CDEL | not_available: 348 |
| Passport fees | not_available: 6 |
| Penalties | not_available: 24 |
| Plastic packaging tax | not_available: 6 |
| Public corporations capital expenditure | not_available: 12 |
| Scottish AME (capital)  | not_available: 12 |
| Scottish AME (current)  | not_available: 36 |
| Scottish BGA (capital) | not_available: 54 |
| Scottish BGA (current) | not_available: 816 |
| Soft drinks Levy | not_available: 12 |
| Stamp duty | not_available: 103, same_sign_ratio_at_least_2: 5 |
| Statutory gaming levy | not_available: 6 |
| Student loans | not_available: 42 |
| Tobacco duty | not_available: 54 |
| VAT | not_available: 175, same_sign_ratio_1.25_to_2: 5 |
| VAT refunds | not_available: 12 |
| Vaping duty | not_available: 24 |
| Vehicle excise duty | not_available: 36 |
| Visa fees | not_available: 12 |
| Welfare inside cap | both_zero: 8, not_available: 321, same_sign_ratio_0.5_to_0.8: 13, same_sign_ratio_0.8_to_1.25: 7, same_sign_ratio_1.25_to_2: 18, same_sign_ratio_at_least_2: 21, same_sign_ratio_below_0.5: 8 |
| Welfare outside cap | not_available: 132 |
| Welsh BGA (current) | not_available: 30 |

| Measure type | Source-row ratio bins |
|---|---|
| administration | not_available: 726 |
| business_tax | not_available: 642 |
| capital_gains_tax | not_available: 72, obr_zero: 1, opposite_sign: 1, same_sign_ratio_at_least_2: 4 |
| carers_allowance | not_available: 12 |
| child_benefit | not_available: 2, same_sign_ratio_0.5_to_0.8: 4, same_sign_ratio_0.8_to_1.25: 1, same_sign_ratio_at_least_2: 5 |
| council_tax | both_zero: 3, not_available: 30, same_sign_ratio_0.8_to_1.25: 3 |
| fuel_duty | not_available: 24 |
| housing_benefit | not_available: 7, same_sign_ratio_1.25_to_2: 5 |
| income_tax | both_zero: 24, not_available: 226, obr_zero: 1, opposite_sign: 1, pe_zero: 23, same_sign_ratio_0.5_to_0.8: 10, same_sign_ratio_0.8_to_1.25: 13, same_sign_ratio_1.25_to_2: 3, same_sign_ratio_at_least_2: 10, same_sign_ratio_below_0.5: 1 |
| indirect_tax | not_available: 246 |
| inheritance_tax | not_available: 96 |
| local_government_finance | not_available: 6 |
| national_insurance | both_zero: 6, not_available: 141, opposite_sign: 1, pe_zero: 21, same_sign_ratio_0.8_to_1.25: 22, same_sign_ratio_1.25_to_2: 16, same_sign_ratio_at_least_2: 21 |
| other | not_available: 1272 |
| savings | not_available: 54 |
| scope | not_available: 1476 |
| stamp_duty_land_tax | not_available: 25, same_sign_ratio_at_least_2: 5 |
| tax_benefit | both_zero: 1, not_available: 222, same_sign_ratio_1.25_to_2: 5 |
| transport | not_available: 246 |
| universal_credit | both_zero: 4, not_available: 38, same_sign_ratio_0.5_to_0.8: 3, same_sign_ratio_0.8_to_1.25: 2, same_sign_ratio_at_least_2: 4, same_sign_ratio_below_0.5: 3 |
| value_added_tax | not_available: 13, same_sign_ratio_1.25_to_2: 5 |
| welfare | not_available: 264 |
| winter_fuel_payment | not_available: 18, same_sign_ratio_0.8_to_1.25: 1, same_sign_ratio_below_0.5: 5 |

## Named axes and explained share

population_vintage tags every row: the fiscal event's OBR forecast differs from this release's later survey population. behavioural_adjustment, baseline_vintage, cy_proxies_fy and head_scope describe the other construction differences. construction_scope identifies partial measures. The pipeline does not adjust the population vintage.

Pinned employer-NIC incidence assigns the wage adjustment fully to employees while holding employer cost fixed. OBR's direct per-head costings exclude separately reported macroeconomic indirect effects. This construction/head_scope difference is named, but its contribution to the raw gaps remains unsized.

Axis-tagged coverage: 238 computed rows, £151.172bn of absolute raw gap. Explained share is available on 0 rows; relevant unsized axes withhold it on the rest. These are different quantities.

## Largest unexplained divergences

The queue below is ranked by absolute residual_plus_unsized, after any evidence-backed sized terms. It names variables and a minimal run selection for investigation. A raw gap with unsized vintage or behavioural terms does not establish a PolicyEngine model issue. Multiple years of one measure share a potential mechanism, so the queue selects one row per measure.

| Event / measure | FY / head | Residual £bn | Variables | Cause class | Evidence / diagnosis | Minimal replay |
|---|---|---:|---|---|---|---|
| autumn_budget_2024 / Employer National Insurance contributions: Increase rate by 1.2 ppts to 15%, cut the Secondary Threshold to £5,000 until 5 April 2028 and uprate with CPI thereafter, increase Employment Allowance to £10,500, remove the £100,000 Employment Allowance eligibility threshold | 2029-30 / Income tax | -7.963 | income_tax | Prior (2.89.2), not re-verified: Construction and head scope; wage incidence | employee_incidence=1 holds employer cost fixed relative to the certified simulation baseline. The lower employer-NIC reversal therefore raises wages, making the announced Income Tax effect about −£8bn to −£9bn, versus OBR's roughly −£0.1bn to −£0.3bn direct head costing. CY2026 also has a −£1.26bn employee-NIC channel. This is the pinned wage-incidence construction, with its contribution to the PE–OBR difference unsized. | `PYTHONPATH=. .venv-candidate/bin/python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1 --measures autumn_budget_2024__employer_nics_package --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/autumn_budget_2024/autumn_budget_2024__employer_nics_package_2029` |
| spring_budget_2023 / Annual Allowance (AA): increase to £60,000 and allow Pension Input Amount aggregation between open and closed public service pension schemes from April 2023 | 2027-28 / Income tax | -3.305 | income_tax | Prior (2.89.2), not re-verified: PE model issue; construction scope | pension_contributions_relief caps relief at the Annual Allowance while private_pension_contributions_tax.py also charges the excess; both enter Income Tax. The charge base includes employer contributions and no carry-forward is represented. policyengine-uk#2237. The separately measured omitted-employer-contributions taper and single-marginal-rate charge diagnostics both reduce the charge in their controlled cases: they push opposite to the observed excessive PE tax reduction and do not explain that excess. National contributions remain unsized. | `PYTHONPATH=. .venv-candidate/bin/python pipeline/compute_uk_event.py --event spring_budget_2023 --variant pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1 --measures spring_budget_2023__pension_annual_allowance_package --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/spring_budget_2023/spring_budget_2023__pension_annual_allowance_package_2027` |
| autumn_statement_2023 / National Insurance contributions (NICs): 2p cut to the main rate of Class 1 employee NICs from January 2024 | 2028-29 / NICs | -2.602 | ni_class_1_employee, ni_class_1_employer, ni_class_2, ni_class_4 | Prior (2.89.2), not re-verified: Data level and population vintage; behavioural adjustment | The certified employee-NIC base is about 15–20% above the OBR forecast: PE £51.7bn in CY2024 and £57.1bn in CY2026 versus £43.9bn and £47.6bn in the OBR March2024 forecast. This broadly follows the effect ratios. OBR's positive Income Tax cells also identify a labour-supply offset. The review's uk-data#537 observation is only about a 1.2% fit change and does not explain this base difference. AS2023 and SB2024 both execute the same certified 10%→8% world; AS2023's PE number is not an isolated 12%→10% costing. The employer-NIC pension-age exemption reduces that different tax base, so a closer employer match does not validate the employee base. | `PYTHONPATH=. .venv-candidate/bin/python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1 --measures autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/autumn_statement_2023/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p_2028` |
| autumn_budget_2024 / Capital Gains Tax: Increase the main rates of CGT to 18% and 24% from 30 October 2024, and the Business Asset Disposal Relief (BADR) and Investors' Relief (IR) rate to 14% from 6 April 2025 and to 18% from 6 April 2026 | 2027-28 / Capital gains tax | 2.561 | capital_gains_tax | Prior (2.89.2), not re-verified: Construction scope; behavioural adjustment and head scope | The gains input pools asset types. Reversing all pooled gains to 10%/20% also lowers residential gains that were already taxed at 18%/24% before AB2024, overstating the announced main-rate tax gain. The pinned gains elasticity is zero and the OBR package has separate Income Tax and Stamp Duty heads. Certified CGT is £23.4bn versus £18.7bn in the reversal world in CY2025; the review does not establish that this baseline level is an engine defect. | `PYTHONPATH=. .venv-candidate/bin/python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1 --measures autumn_budget_2024__capital_gains_main_rates_and_reliefs --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/autumn_budget_2024/autumn_budget_2024__capital_gains_main_rates_and_reliefs_2027` |
| spring_budget_2024 / National Insurance contributions (NICs): 2 percentage point cut to the main rate of Class 1 employee NICs from 6 April 2024 | 2028-29 / NICs | -2.354 | ni_class_1_employee, ni_class_1_employer, ni_class_2, ni_class_4 | Prior (2.89.2), not re-verified: Data level and population vintage; behavioural adjustment | The certified employee-NIC base is about 15–20% above the OBR forecast: PE £51.7bn in CY2024 and £57.1bn in CY2026 versus £43.9bn and £47.6bn in the OBR March2024 forecast. This broadly follows the effect ratios. OBR's positive Income Tax cells also identify a labour-supply offset. The review's uk-data#537 observation is only about a 1.2% fit change and does not explain this base difference. AS2023 and SB2024 both execute the same certified 10%→8% world; AS2023's PE number is not an isolated 12%→10% costing. The employer-NIC pension-age exemption reduces that different tax base, so a closer employer match does not validate the employee base. | `PYTHONPATH=. .venv-candidate/bin/python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1 --measures spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/spring_budget_2024/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp_2028` |
| autumn_budget_2024 / Stamp Duty Land Tax (SDLT): Increase the Higher Rate of Additional Dwelling (HRAD) of SDLT by 2ppts from 3% to 5% from 31 October 2024 | 2029-30 / Stamp duty | 2.010 | stamp_duty_land_tax | Prior (2.89.2), not re-verified: PE model/data issue; behavioural adjustment and head scope | additional_residential_property_purchased multiplies the household's whole other-property stock by property_purchased, the all-property purchase flag. The audited flagged stock is £94.7bn; 2pp of that is about £1.9bn, consistent with the large PE effect. policyengine-uk#2238. Transactions behaviour, corporate purchasers and other stamp-tax interactions remain separate unsized scope terms. | `PYTHONPATH=. .venv-candidate/bin/python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1 --measures autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2029` |
| spring_statement_2025 / Universal Credit Health Element: Maintain at 2025-26 rate until 2029-30, reduce rate by 50% for new claimants from April 2026 and maintain until 2029-30 | 2029-30 / Welfare inside cap | -1.756 | universal_credit | Open: relevant axes unsized | Open: relevant axes unsized | `PYTHONPATH=. .venv-candidate/bin/python pipeline/compute_uk_event.py --event spring_statement_2025 --variant pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1 --measures spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/spring_statement_2025/spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut_2029` |
| autumn_budget_2025 / Salary Sacrifice: Limit the value of salary sacrificed pension contributions that can receive employee and employer NICs relief to £2,000 per year from 6 April 2029 | 2030-31 / NICs | -1.402 | ni_class_1_employee, ni_class_1_employer, ni_class_4 | Open: relevant axes unsized | Open: relevant axes unsized | `PYTHONPATH=. .venv-candidate/bin/python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1 --measures ab2025__salary_sacrifice_pension_nics_cap_2000 --years 2030 --workers 1 --output-dir .venv-replay-checks/reproductions/autumn_budget_2025/ab2025__salary_sacrifice_pension_nics_cap_2000_2030` |
| autumn_budget_2024 / Winter Fuel Payments: Target payments at recipients of Pension Credit and certain other means-tested benefits from winter 2024-25 | 2029-30 / Welfare inside cap | -1.272 | winter_fuel_allowance | Prior (2.89.2), not re-verified: Baseline vintage | From 2025 the pinned £35,000 income passport is an alternative eligibility route, so require_benefits=False reaches only households still excluded after that later reversal. This explains the narrower future-year construction. PE excludes Scotland, which reduces spending and pushes opposite to the excessive PE restriction saving in FY2024–25; Pension Credit take-up and behaviour remain unsized. | `PYTHONPATH=. .venv-candidate/bin/python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1 --measures autumn_budget_2024__winter_fuel_means_test --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/autumn_budget_2024/autumn_budget_2024__winter_fuel_means_test_2029` |
| spring_budget_2024 / High Income Child Benefit Charge: increase income threshold to £60,000 and taper range to £60,000 to £80,000 from 6 April 2024 | 2028-29 / Income tax | -1.202 | income_tax | Prior (2.89.2), not re-verified: PE model issue, fixed on main after the certified pin | The pinned child_benefit and child_benefit_respective_amount formulas ignore child_benefit_opts_out: opted-out families can be charged HICBC and the reform cannot induce their claims. The review records the opts_out/remains_opted_out fix on main after 2.89.2; this certified replay retains the earlier formulas. Welfare's zero counterpart and the Income Tax excess therefore have a known model diagnosis. | `PYTHONPATH=. .venv-candidate/bin/python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1 --measures spring_budget_2024__hicbc_threshold_and_taper --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/spring_budget_2024/spring_budget_2024__hicbc_threshold_and_taper_2028` |
| autumn_budget_2025 / Personal Tax: Maintain the personal income tax and equivalent national insurance thresholds at current levels for a further three years until April 2031 | 2030-31 / Income tax | 0.950 | income_tax | Open: relevant axes unsized | Open: relevant axes unsized | `PYTHONPATH=. .venv-candidate/bin/python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1 --measures ab2025__personal_tax_thresholds_freeze_to_2031 --years 2030 --workers 1 --output-dir .venv-replay-checks/reproductions/autumn_budget_2025/ab2025__personal_tax_thresholds_freeze_to_2031_2030` |
| autumn_budget_2025 / Savings Income: Increase tax rates on savings income by 2ppts at the basic, higher and additional rate from 6 April 2027 and maintain the Starting Rate of Savings limit at £5000 from April 2026 to April 2031 | 2027-28 / Income tax | 0.941 | income_tax | Open: relevant axes unsized | Open: relevant axes unsized | `PYTHONPATH=. .venv-candidate/bin/python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1 --measures ab2025__savings_rates_plus_2pp_and_starter_limit_held --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/autumn_budget_2025/ab2025__savings_rates_plus_2pp_and_starter_limit_held_2027` |
| autumn_budget_2025 / Winter Fuel Payment: Target to pensioners with taxable income below or equal to £35,000 from Winter 2025 | 2027-28 / Income tax | -0.892 | income_tax | Open: relevant axes unsized | Open: relevant axes unsized | `PYTHONPATH=. .venv-candidate/bin/python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1 --measures ab2025__winter_fuel_payment_income_test_35000 --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/autumn_budget_2025/ab2025__winter_fuel_payment_income_test_35000_2027` |
| autumn_budget_2025 / Property Income: Introduce separate tax rates for property income at 22% for the property basic rate, 42% for the property higher rate and 47% for the property additional rate, from 6 April 2027 | 2027-28 / Income tax | 0.890 | income_tax | Open: relevant axes unsized | Open: relevant axes unsized | `PYTHONPATH=. .venv-candidate/bin/python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1 --measures ab2025__property_income_separate_rates --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/autumn_budget_2025/ab2025__property_income_separate_rates_2027` |
| autumn_budget_2025 / Universal Credit Child Element: Remove the two child limit from April 2026, taking 450,000 children out of poverty | 2027-28 / Welfare inside cap | -0.857 | universal_credit | Open: relevant axes unsized | Open: relevant axes unsized | `PYTHONPATH=. .venv-candidate/bin/python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1 --measures ab2025__uc_child_element_remove_two_child_limit --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/autumn_budget_2025/ab2025__uc_child_element_remove_two_child_limit_2027` |
| spring_statement_2025 / Universal Credit Standard Allowance: Increase above inflation for all claimants from April 2026, reaching CPI +5% from April 2029, with the standard allowance expected to be worth £106 per week in 2029-30 | 2029-30 / Welfare inside cap | 0.793 | universal_credit | Prior (2.89.2), not re-verified: PE model issue; index and baseline vintage; head scope | The 2026 counterfactual uses the legislated amount's September2025 CPI of 3.8%, removing the former 3.4% forecast-index mismatch. Later counterfactual years continue on the certified CPI path. Raising the counterfactual reduces the scored allowance cost, moving PE's cost magnitude further below OBR's; the earlier index mismatch pushed opposite to the observed cost shortfall. The pin hardcodes the 2026 allowance and then applies plain CPI; uc_standard_allowance never reads standard_allowance_uplift, whose 2027–2029 values are 3.1%, 4.0% and 4.8%. The Welfare outside cap source head remains uncomputed. The missing legislated 2027–2029 uplifts are policyengine-uk#2239. | `PYTHONPATH=. .venv-candidate/bin/python pipeline/compute_uk_event.py --event spring_statement_2025 --variant pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1 --measures spring_statement_2025__uc_standard_allowance_above_inflation --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/spring_statement_2025/spring_statement_2025__uc_standard_allowance_above_inflation_2029` |
| autumn_statement_2023 / Local Housing Allowance (LHA): set to the 30th percentile from April 2024 | 2025-26 / Welfare inside cap | -0.791 | housing_benefit, universal_credit | Open: relevant axes unsized | Open: relevant axes unsized | `PYTHONPATH=. .venv-candidate/bin/python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1 --measures autumn_statement_2023__lha_reset_to_30th_percentile --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2025` |
| autumn_budget_2025 / Dividend Income: Increase tax rates on dividend income by 2ppts at the ordinary and upper rate from 6 April 2026 | 2026-27 / Income tax | 0.591 | income_tax | Open: relevant axes unsized | Open: relevant axes unsized | `PYTHONPATH=. .venv-candidate/bin/python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1 --measures ab2025__dividend_rates_plus_2pp --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/autumn_budget_2025/ab2025__dividend_rates_plus_2pp_2026` |
| autumn_budget_2024 / VAT: Applying the standard rate (20%) to education and boarding services provided by private schools from 1 January 2025 | 2028-29 / VAT | 0.474 | private_school_vat | Open: relevant axes unsized | Open: relevant axes unsized | `PYTHONPATH=. .venv-candidate/bin/python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1 --measures autumn_budget_2024__private_school_vat_20pct --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/autumn_budget_2024/autumn_budget_2024__private_school_vat_20pct_2028` |
| spring_budget_2024 / National Insurance contributions (NICs): 2 percentage point cut to the main rate of Class 4 self-employed NICs from 6 April 2024 | 2028-29 / Income tax | -0.360 | income_tax | Open: relevant axes unsized | Open: relevant axes unsized | `PYTHONPATH=. .venv-candidate/bin/python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1 --measures spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/spring_budget_2024/spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp_2028` |
| autumn_statement_2023 / National Insurance contributions (NICs): abolish Class 2 self-employed NICs liability from April 2024 | 2028-29 / Income tax | -0.262 | income_tax | Prior (2.89.2), not re-verified: PE model issue; Class 2/Class 4 cap interaction | The FY2027–28 announced artifact records −£552.039m in ni_class_2 and −£786.808m in ni_class_4, alongside +£11.933m in Universal Credit. Later-year totals therefore include the pinned Class 4 cap interaction alongside direct Class 2 cash liability. A controlled 2027 calculation with £143,750 self-employment income and zero employee NICs reproduces a £1,849.49 Class 4 increase when Class 2 is restored. In ni_class_4_maximum, a strict branch comparison at a mathematically equal boundary is sensitive to floating-point subtraction of uprated thresholds. This points to a pinned cap-formula issue; the artifact quantifies the national Class 4 head, while a full household trace would be needed to attribute that entire head to the reproduced instability. | `PYTHONPATH=. .venv-candidate/bin/python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1 --measures autumn_statement_2023__class_2_self_employed_nics_abolition --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/autumn_statement_2023/autumn_statement_2023__class_2_self_employed_nics_abolition_2028` |
| autumn_statement_2023 / National Insurance contributions (NICs): 1p cut to the main rate of Class 4 self-employed NICs from April 2024 | 2028-29 / Income tax | -0.203 | income_tax | Open: relevant axes unsized | Open: relevant axes unsized | `PYTHONPATH=. .venv-candidate/bin/python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1 --measures autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/autumn_statement_2023/autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p_2028` |
| spring_budget_2023 / DWP: increase the maximum support available in Universal Credit for childcare costs | 2027-28 / Welfare inside cap | -0.179 | universal_credit | Open: relevant axes unsized | Open: relevant axes unsized | `PYTHONPATH=. .venv-candidate/bin/python pipeline/compute_uk_event.py --event spring_budget_2023 --variant pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1 --measures spring_budget_2023__uc_childcare_cap_increase --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/spring_budget_2023/spring_budget_2023__uc_childcare_cap_increase_2027` |
| autumn_budget_2025 / National Insurance: Maintain the secondary threshold for employer contributions at current level for a further three years until April 2031 | 2030-31 / NICs | -0.145 | ni_class_1_employee, ni_class_1_employer, ni_class_4 | Open: relevant axes unsized | Open: relevant axes unsized | `PYTHONPATH=. .venv-candidate/bin/python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1 --measures ab2025__employer_nics_secondary_threshold_freeze_to_2031 --years 2030 --workers 1 --output-dir .venv-replay-checks/reproductions/autumn_budget_2025/ab2025__employer_nics_secondary_threshold_freeze_to_2031_2030` |
| autumn_budget_2025 / High Value Council Tax Surcharge: Introduce a surcharge on owners of residential properties valued over £2m in England from 1 April 2028 | 2030-31 / High-value council tax surcharge | 0.030 | high_value_council_tax_surcharge | Open: relevant axes unsized | Open: relevant axes unsized | `PYTHONPATH=. .venv-candidate/bin/python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1 --measures ab2025__high_value_council_tax_surcharge --years 2030 --workers 1 --output-dir .venv-replay-checks/reproductions/autumn_budget_2025/ab2025__high_value_council_tax_surcharge_2030` |

Evidence-backed PolicyEngine issue candidates recorded: 5. No upstream issues were filed by this replay lane.

## Measured model investigation candidates

These are engine observations reproduced separately from the national costing. Their national contribution remains unsized. The list contains only observed candidates; it is not padded to ten.

| Candidate | Class (established) | Status on this engine | Variables | Evidence | Minimal reproducer |
|---|---|---|---|---|---|
| carers_allowance_earnings_test_absent | pe_gap | resolved (established on 2.89.2) | carers_allowance | variables/gov/dwp/carers_allowance.py (source SHA and measured values in MODEL_DIAGNOSTICS.json) | `PYTHONPATH=. .venv-candidate/bin/python pipeline/diagnose_uk_event_models.py --reverify results/uk/events/MODEL_DIAGNOSTICS.json --expect-engine 2.130.1 --case carers_allowance_earnings_test_absent` |
| cgt_main_rate_commencement | pe_gap | resolved (established on 2.89.2) | capital_gains_tax | parameters/gov/hmrc/cgt/basic_rate.yaml (source SHA and measured values in MODEL_DIAGNOSTICS.json) | `PYTHONPATH=. .venv-candidate/bin/python pipeline/diagnose_uk_event_models.py --reverify results/uk/events/MODEL_DIAGNOSTICS.json --expect-engine 2.130.1 --case cgt_main_rate_commencement` |
| sdlt_additional_home_hike_absent | pe_gap | persists (established on 2.89.2) | sdlt_on_residential_property_transactions, stamp_duty_land_tax | parameters/gov/hmrc/stamp_duty/residential/purchase/additional/rate.yaml (source SHA and measured values in MODEL_DIAGNOSTICS.json) | `PYTHONPATH=. .venv-candidate/bin/python pipeline/diagnose_uk_event_models.py --reverify results/uk/events/MODEL_DIAGNOSTICS.json --expect-engine 2.130.1 --case sdlt_additional_home_hike_absent` |
| private_school_vat_current_law_lever_zero | pe_gap | persists (established on 2.89.2) | private_school_vat | parameters/gov/contrib/labour/private_school_vat.yaml (source SHA and measured values in MODEL_DIAGNOSTICS.json) | `PYTHONPATH=. .venv-candidate/bin/python pipeline/diagnose_uk_event_models.py --reverify results/uk/events/MODEL_DIAGNOSTICS.json --expect-engine 2.130.1 --case private_school_vat_current_law_lever_zero` |
| dividend_band_threshold_lag | pe_gap | persists (established on 2.89.2) | dividend_income_tax, income_tax | parameters/gov/hmrc/income_tax/rates/dividends.yaml (source SHA and measured values in MODEL_DIAGNOSTICS.json) | `PYTHONPATH=. .venv-candidate/bin/python pipeline/diagnose_uk_event_models.py --reverify results/uk/events/MODEL_DIAGNOSTICS.json --expect-engine 2.130.1 --case dividend_band_threshold_lag` |
| class4_threshold_indexation_from_2027 | pe_gap | resolved (established on 2.89.2) | ni_class_4 | parameters/gov/hmrc/national_insurance/class_4/thresholds/lower_profits_limit.yaml (source SHA and measured values in MODEL_DIAGNOSTICS.json) | `PYTHONPATH=. .venv-candidate/bin/python pipeline/diagnose_uk_event_models.py --reverify results/uk/events/MODEL_DIAGNOSTICS.json --expect-engine 2.130.1 --case class4_threshold_indexation_from_2027` |
| uc_lcwra_protection_stops_at_2030 | investigation | persists (established on 2.89.2) | uc_LCWRA_element | scenarios/uc_reform.py (source SHA and measured values in MODEL_DIAGNOSTICS.json) | `PYTHONPATH=. .venv-candidate/bin/python pipeline/diagnose_uk_event_models.py --reverify results/uk/events/MODEL_DIAGNOSTICS.json --expect-engine 2.130.1 --case uc_lcwra_protection_stops_at_2030` |
| employer_nics_state_pension_age_exemption | pe_gap | resolved (established on 2.89.2) | ni_liable, ni_class_1_employer, ni_class_1_employee | variables/gov/hmrc/national_insurance/class_1/ni_class_1_employer.py (source SHA and measured values in MODEL_DIAGNOSTICS.json) | `PYTHONPATH=. .venv-candidate/bin/python pipeline/diagnose_uk_event_models.py --reverify results/uk/events/MODEL_DIAGNOSTICS.json --expect-engine 2.130.1 --case employer_nics_state_pension_age_exemption` |
| pension_taper_omits_employer_contributions | pe_gap | persists (established on 2.89.2) | adjusted_net_income, pension_annual_allowance | variables/gov/hmrc/income_tax/allowances/pension_annual_allowance.py (source SHA and measured values in MODEL_DIAGNOSTICS.json) | `PYTHONPATH=. .venv-candidate/bin/python pipeline/diagnose_uk_event_models.py --reverify results/uk/events/MODEL_DIAGNOSTICS.json --expect-engine 2.130.1 --case pension_taper_omits_employer_contributions` |
| annual_allowance_charge_single_marginal_rate | pe_gap | persists (established on 2.89.2) | personal_pension_contributions_tax | variables/gov/hmrc/pensions/private_pension_contributions_tax.py (source SHA and measured values in MODEL_DIAGNOSTICS.json) | `PYTHONPATH=. .venv-candidate/bin/python pipeline/diagnose_uk_event_models.py --reverify results/uk/events/MODEL_DIAGNOSTICS.json --expect-engine 2.130.1 --case annual_allowance_charge_single_marginal_rate` |
