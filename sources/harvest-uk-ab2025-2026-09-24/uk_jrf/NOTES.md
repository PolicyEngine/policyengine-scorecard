# uk_jrf — Joseph Rowntree Foundation, Autumn Budget 2025 harvest (2026-09-24)

Source `jrf`. Six quantified JRF pieces from 25 Sep 2025 to 3 Mar 2026 plus the 26 Nov commentary
(manifested, zero claims). Engine: the IPPR Tax-Benefit Model (`source_model: landman_ttm`, version in
`conditions.model_version`: v02_85 on 25/30 Sep, 02_90 on 27 Jan, v02_92 on 3 Mar, not stated on 27 Nov);
Savanta survey rows carry `source_model: survey` and `benchmark_class: administrative_fact`; OBR/HMT/DWP
figures JRF repeats are `attribution: restated` with the originating engine as `source_model`.

## Access recipe

- jrf.org.uk `robots.txt`: `User-agent: * / Crawl-delay: 20`. The seven pages were fetched once each,
  spaced 21 s apart, with a browser User-Agent, all HTTP 200, no Wayback fallback needed. Text extracted
  with the harvest's `html2txt.py` (script/style/nav/header/footer dropped). Figures 1–6 (25 Sep),
  1–2 (30 Sep) and 1–3 (27 Nov, 27 Jan) are images; every number staged is stated in the page text.
- Every `quote` was machine-checked against the extracted page text (whitespace-collapsed).

## Already in sources/harvest-uk-2026-08-02 (not re-staged here)

`sources/harvest-uk-2026-08-02/uk_ukmod_jrf/` already carries JRF's **UK Poverty 2026** data workbook
(sheets OT1, GT1, DDT1, OG1, FAST2, A1T1; xlsx sha256 3c694c57…), the UK Poverty 2026 landing page
(sha256 48abe893…) and **A Minimum Income Standard for the UK in 2025** Table 2 (sha256 1097b577…).
None of that material is touched; the 27 Jan 2026 piece staged here ("This isn't what change feels like")
is a different publication from UK Poverty 2026 (same release day).

## Coverage tally (seed bullets → rows)

- 25 Sep "A decade of falling incomes?" — 5 seed bullets → 35 rows. Baseline (£42,830; −£550/−1.3 %;
  −£570; previous parliament −0.5 %; OBR RHDI +2.9 % restated), drivers (housing −£770; tax +£630 /
  +£310 tertile 1 / +£850 tertile 3; social security +£120 / +£270 / −£150 / −£240), distribution
  (tertile 1 −£1,110/−6.2 % over the decade and −£470/−2.7 % this parliament; tertiles 2–3 −1.1 %/−1.3 %;
  pensioner −0.6 %/−£170; 35–64 −£870/−1.9 %; under-35 −£930/−2.7 %; couples/lone parents −£1,500,
  −2.8 %/−5.6 %), tax options (CGT package >£13bn; NICs on investment income >£10bn, keyed to
  `ab2025_option__nics_on_investment_income`), May-2025 hardship survey (7m / 4.5m / 4m). NOT staged: "real wages in 2029 less than
  6 % above 2007" (JRF's reading of ONS, no exact value); "around half this loss occurring during this
  parliament" (not a number).
- 30 Sep "Two policies" — 4 bullets → 17 rows, everything in the seed (−£750/−1.3 %, −£780/−3.0 %;
  −£510, 32 %, +£320/+1.2 %, 2.1m children, 500,000 out, 1m depth, £3.6bn; 300,000 and £2.8bn alone;
  £3,514 per child; £380m floor; 141,000 capped children).
- 19 Nov "Put cost of living at heart of Budget" — 3 bullets → 9 rows (7.1m, 60 %, 1 in 4, 83 %, 69 %,
  46 %; >£3,500; 300,000; further 200,000).
- 26 Nov "Chancellor makes right choice" — commentary, no numbers, 0 rows (manifested).
- 27 Nov "Scrapping two-child limit eases burden" — 4 bullets → 16 rows (0.4pp and £150 restated;
  400,000 projection; £3.0bn restated; 2.0m children; 1.1pp; tertile −£140/−0.8 %, −£300/−0.9 %,
  −£2,230/−2.9 %; top third +£1,570/+2.1 % 2019–24; mean −£850/−2.0 %). NOT staged: "OBR RHDI adjusted
  … broadly flat" (no number).
- 27 Jan 2026 "This isn't what change feels like" — 3 bullets → 50 rows (400,000; 22.3 → 21.2 → 21.0;
  half a million families restated OBR; working-age 20.4 / 19.8 / −0.06; child 31.6 / 28.7 / −0.05 per
  year; 29.8 % and 28.6 % HBAI comparators restated; >4m children; pensioners 16.7 → 15.9; upside 21.0;
  80 %-employment scenario 20.4 vs 21; 32,000 fewer disability recipients; Table 1 central inputs 7 × 4;
  productivity 1.3 %/0.7 %). NOT staged: Tables 2–3 (upside/downside inputs — in the page text, second
  pass); the DWP HBAI "over 4 million" is the JRF projection row (kept once).
- 3 Mar 2026 "Living standards challenge still acute" — 1 bullet → 7 rows (£42,470 / £43,080 / £42,500;
  +£40 / +0.1 %; −£580; Chancellor's £1,000 restated).

## Corrections to the seed inventory / registry

- Seed (27 Jan) reads "upside scenario overall 21.0%/20.4%": the primary gives 21.0 % for the upside
  scenario and 20.4 % for a separate "80 % of working-age adults working" scenario (vs 21 % central);
  staged as two scenarios.
- Seed (27 Nov) attributes the model as "IPPR TBM (inferred)": confirmed not named on the page;
  `conditions.model_version` says so and the rows keep `source_model: landman_ttm`.
- baselines.py describes `jrf_pre_ab2025_projection_path` as "incomes projected November to November";
  the 25 Sep and 30 Sep primaries project to **September** of each year (2025 Q3 prices); November is
  the 27 Nov post-Budget path. The label is used as instructed for the pre-Budget rows; the docstring
  needs the month corrected before ingest.

## Baselines

- `jrf_pre_ab2025_projection_path` on every 25 Sep / 30 Sep projection and option row (46 rows).
- Post-Budget paths are unregistered and go in `proposed_baseline` (strings listed below): the 27 Nov
  November-to-November path on the OBR November 2025 forecast, the 27 Jan April-to-April path on the
  OBR November 2025 EFO central scenario, the 3 Mar path on the OBR Spring Forecast 2026, and the
  27 Nov "if the policy was retained" counterfactual for the 1.1pp row.
- Levels at the scoring date, restated OBR/HMT figures and HBAI comparators carry `baseline_policy: null`.

## Attribution decisions

- own: all IPPR-TBM projections and option scores, the Savanta survey counts, the £2.8bn / £3.6bn /
  £380m take-up-calibrated costs, the 2.0m affected-children projection, the £3,514 per-child arithmetic.
- restated (36 rows): OBR RHDI +2.9 % and the Chancellor's £1,000; the 0.4pp inflation effect and the
  £150 energy-bill figure; the £3.0bn two-child cost (OBR-certified; JRF's own is £2.8bn); OBR's
  "half a million families"; the HBAI 29.8 % / 28.6 % comparators; Table 1 central inputs (OBR/DWP).
- Package rows (two-child limit + protected minimum floor) are keyed on the two-child limit with
  `conditions.package` and `conditions.package_second_key` naming the floor key; the floor-alone rows
  and the "further 200,000" incremental row are keyed on the floor.

## Proposals (proposed_metric / proposed_unit) with the producer's definition

- `income_component_change` (gbp): change in a component of household disposable income over the
  window — "housing costs … reducing disposable incomes by £770 per year for the average household in
  September 2029"; "tax paid on those earnings is expected to increase by around £630 per year";
  "average income from social security will increase by £120 per year".
- `affected_count` (households / children / families): "over 7 million low-income households went
  without essentials"; "2.1 million children would be benefiting"; "the 2.0 million children that would
  have been hit by the limit"; "141,000 children in families impacted by the two-child limit who are also
  currently benefit capped"; OBR's "half a million families that will immediately benefit".
- `affected_share` (share): survey shares — "60% of low-income households went without essentials",
  "1 in 4 of all households", "83%", "69%", "46%".
- `benefit_loss_per_child` (gbp): "current losses of £3,514 per year for each third and subsequent
  children born after April 2017"; "losses of over £3,500 per year".
- `poverty_depth_reduction_count` (children): "reduce the depth of poverty by a further 1 million".
- `living_standards_decline_offset_share` (percent): "offset the average decline in living standards
  by a third (32%)".
- `real_income_growth_difference` (percentage_points): "disposable income after housing costs 1.1
  percentage points higher over this parliament than if the policy was retained".
- `household_bill_change` (gbp_per_household): "policies to lower energy bills by £150 per year".
- `projection_input_assumption` (percent): Table 1 "Input parameters for central scenario" and the
  productivity assumptions ("medium-run annual productivity growth at 1.3%").
- No proposed_unit is used in this family.

## Registry gaps (resolved 2026-09-24)

- NICs on all investment income (dividends, rents, savings) was unkeyed in the first pass; the key
  `ab2025_option__nics_on_investment_income` was registered the same day and the row (25 Sep, >£10bn,
  2029/30) now carries it. No `measure_scope: unkeyed` rows remain in this family.

## Manifest (primaries fetched 2026-09-24, sha256 + bytes)

- 2025-09-25 · html · direct · `87c3faed8f3ad436…` · 121,154 bytes · A decade of falling incomes? JRF's pre-budget assessment of living standards (Tims, Belfield, Matejic)  
  https://www.jrf.org.uk/cost-of-living/a-decade-of-falling-incomes-jrfs-pre-budget-assessment-of-living-standards
- 2025-09-30 · html · direct · `10a7de1f2ad373c4…` · 84,531 bytes · Two policies to boost family living standards and reduce child poverty (Schmuecker, Tims)  
  https://www.jrf.org.uk/child-poverty/two-policies-to-boost-family-living-standards-and-reduce-child-poverty
- 2025-11-19 · html · direct · `83597fc206bd1059…` · 74,100 bytes · Put cost of living at heart of Budget for growth and fairness (Tims, Belfield, Percival)  
  https://www.jrf.org.uk/cost-of-living/put-cost-of-living-at-heart-of-budget-for-growth-and-fairness
- 2025-11-26 · html · direct · `b7ca549128cfa67a…` · 64,390 bytes · Chancellor makes right choice on two-child limit at Budget, but families left with mountain still to climb (Alfie Stirling)  
  https://www.jrf.org.uk/news/jrf-responds-to-autumn-budget-2025
- 2025-11-27 · html · direct · `d94429c8dbd128cc…` · 83,043 bytes · Scrapping two-child limit eases burden on families, but living standards still bleak (Tims, Matejic, Belfield, Wenham, Aref-Adib)  
  https://www.jrf.org.uk/cost-of-living/scrapping-two-child-limit-eases-burden-on-families-but-living-standards-still-bleak
- 2026-01-27 · html · direct · `f7b0dc9eb337e74a…` · 116,805 bytes · This isn't what change feels like (Belfield, Matejic, Tims, Wenham)  
  https://www.jrf.org.uk/social-security/this-isnt-what-change-feels-like
- 2026-03-03 · html · direct · `6246db3bc33a79b3…` · 69,183 bytes · Living standards challenge still acute as average annual incomes set to grow by only GBP 40 over course of parliament (Chris Belfield)  
  https://www.jrf.org.uk/news/living-standards-challenge-still-acute-as-average-annual-incomes-set-to-grow-by-only-ps40-over

## Row tally by publication and measure key

- 2025-09-25: 35 rows
- 2025-09-30: 17 rows
- 2025-11-19: 9 rows
- 2025-11-27: 16 rows
- 2026-01-27: 50 rows
- 2026-03-03: 7 rows

- measure_key `None`: 113
- measure_key `ab2025__renewables_obligation_exchequer_funded_75pct`: 2
- measure_key `ab2025__uc_child_element_remove_two_child_limit`: 4
- measure_key `ab2025_option__cgt_equalise_with_income_tax_plus_investment_allowance`: 1
- measure_key `ab2025_option__nics_on_investment_income`: 1
- measure_key `ab2025_option__scrap_two_child_limit`: 11
- measure_key `ab2025_option__uc_protected_minimum_floor_deductions_capped_at_15pct`: 2

## Attribution and class counts

- attribution: own 98, restated 36
- benchmark_class: administrative_fact 12, different_model 122
- source_model: administrative_data 1, arithmetic 4, hmt_costing_obr_certified 2, landman_ttm 84, obr_efo_forecast 32, survey 9, survey_microdata 2
- baseline_policy: None 88, jrf_pre_ab2025_projection_path 46
- value_kind: central 3, point 126, range_low 5; time_basis: annual 25, fiscal_year 21, point_in_time 88; parse_confidence: high 121, medium 13

## Registered metrics and units used

- metric: average_household_income_change 21, caseload 1, cpi_inflation_effect 1, income_statistic 4, poverty_count 1, poverty_count_change 6, poverty_rate 14, poverty_rate_change 2, real_income_growth 21, revenue_change 6
- unit_concept: children 11, families 1, gbp 41, gbp_per_household 1, households 4, percent 66, percentage_points 4, persons 1, share 5

## Distinct values on every conditions axis

- `attribution_note` (2): JRF attributes the fall primarily to the removal of the two-child limit; the figure is the projected total change, not an isolated measure delta | JRF: primarily because of the removal of the two-child limit; the figure is the year-on-year projected change
- `basis` (2): post_behavioural | static
- `comparison_window` (15): 2019-09 to 2029-09 | 2019-11 to 2024-11 | 2024-04 to 2029-04 | 2024-09 to 2029-09 | 2024-11 to 2029-11 | 2025-04 to 2026-04 | 2025-09 to 2029-09 | 2026-04 to 2029-04 | 2026-04 to 2029-04, per year | average throughout the 2010s | over the parliament | over this parliament (November 2024 to November 2029) | previous 5-year parliament (to 2024) | start of parliament to end of parliament (September 2024 to September 2029) | three years before the pandemic
- `component` (3): housing_costs | social_security | tax_on_earnings
- `data` (2): FRS 2021-24 | FRS 2023/24
- `data_scope` (2): Savanta panel survey for JRF, households in the bottom 40% of incomes, May 2025 wave | Savanta survey for JRF, 17 October - 7 November 2025, at least 4,000 households in the bottom 40% of incomes
- `denominator` (4): all UK households | all low-income households (bottom 40%) | low-income households (bottom 40%) | low-income households with 3 or more children
- `fiscal_event` (1): autumn_budget_2025
- `floor_parameter` (1): deductions resulting from the benefit cap capped at 15% of the basic rate of entitlement
- `fy` (3): 2025-26 | 2026-27 | 2029-30
- `geography` (1): UK
- `hardship_measure` (4): skipped meals or gone hungry | took out a loan to cover the cost of essentials | went into arrears on bills | went without essentials
- `horizon` (2): end of the decade | end_of_parliament
- `housing_costs` (1): ahc
- `income_concept` (3): mean household disposable income after housing costs, real (CPI deflator), household level | real household disposable income per head (OBR national-accounts measure) | real household disposable income per head (OBR national-accounts measure), as quoted by the Chancellor
- `income_group` (4): all | tertile_1 | tertile_2 | tertile_3
- `input_basis` (1): employment and unemployment refer to the financial year (2026 = 2026/27); all other values are for the second quarter of that year
- `macro_path` (5): OBR March 2025 adjusted by Bank of England August 2025 MPR | OBR November 2025 EFO outturn and forecast (central scenario) with DWP caseload projections | OBR November 2025 EFO with DWP caseload projections | OBR November 2025 forecast | OBR Spring Forecast 2026
- `measure_type` (12): change_over_parliament_with_reform | children benefiting | children that would have been hit by the two-child limit | current loss per child under the two-child limit | difference from central scenario | families benefiting immediately | historical_comparison | historical_outturn | incremental effect of the floor on top of two-child-limit removal | interaction_two_child_limit_and_benefit_cap | level | rounded restatement of the central 21.0%
- `model_runs` (1): average of 5 model runs
- `model_version` (4): 02_90 | not stated on the page (IPPR TBM inferred from the pieces either side) | v02_85 | v02_92
- `origin` (2): JRF earlier work (Earwaker et al 2025, Spring Statement piece), not fresh modelling | restates JRF's own 30 Sep 2025 modelling
- `package` (2): energy bill and rail fare measures | scrap_two_child_limit + uc_protected_minimum_floor (deductions from the benefit cap and debt capped)
- `package_second_key` (2): ab2025_option__scrap_two_child_limit | ab2025_option__uc_protected_minimum_floor_deductions_capped_at_15pct
- `parameter` (8): Bank rate | Employment (16–64) | Inflation | Mortgage interest growth | Private rent growth | Real earnings growth | Unemployment (16–64) | medium-run annual productivity growth
- `policy_note` (1): thresholds frozen in cash terms until April 2028 (pre-Budget path)
- `poverty_line` (1): relative_60_median
- `prices` (2): 2025 Q3 | 2025/26
- `program` (2): universal_credit_child_element | working-age disability benefits
- `projection_month` (3): April | November | September
- `reference_month` (5): 2024-04 | 2025-04 | 2025-09 | 2026-04 | 2029-04
- `reference_period` (3): last 30 days | last 6 months | past 6 months to May 2025
- `scenario` (10): 80% working-age employment ambition | central | downside | obr_march_2025_forecast | obr_spring_forecast_2026 | outturn | post_budget_projection | post_spring_forecast_2026_projection | pre_budget_baseline | upside
- `scenario_family` (1): post_budget_projection
- `scenario_note` (2): 'Even if the economy performs substantially better than expected, with the Government hitting their ambition for 80% of working-age adults to be working' | medium-run productivity growth 1.3% (vs 1.0% central), higher employment, lower disability-benefit onflow
- `scotland_treatment` (2): cost and poverty estimates count the removal of the two-child limit in Scotland as part of the effect (note 2) | living-standards projection already accounts for the announced removal of the two-child limit in Scotland (note 2)
- `sign_convention` (16): positive = adds to household disposable income | positive = children lifted out of poverty | positive = children whose depth of poverty is reduced | positive = cost to the Exchequer | positive = fall in the number of children in poverty | positive = fewer children in poverty | positive = gain to households | positive = growth | positive = higher disposable income growth than the counterfactual | positive = higher inflation | positive = more recipients than central | positive = more tax paid by households | positive = reduction in household energy bills | positive = rise in the poverty rate | positive = share of the projected decline offset | positive = yield to the Exchequer
- `statistic` (2): average | mean
- `subgroup` (14): all households | all people | children | children in families impacted by the two-child limit who are also currently benefit capped | couples with children | households headed by someone aged 35-64 | households headed by someone under 35 | lone parents | low-income families | pension-age households (head 65+) | pensioner households (head 65+) | pensioners | third and subsequent children born after April 2017 | working-age adults
- `subgroup_basis` (2): FRS default family-type decomposition | age of the main FRS respondent (head); mixed households dropped
- `take_up` (1): UC take-up calibrated to published counts of children impacted by the two-child limit and held constant across scenarios (note 3)
- `tertile_basis` (2): tertiles set at person level on equivalised household income after housing costs; averages at household level | thirds of income (JRF: person-level tertiles of equivalised AHC income, averages at household level)

## proposed_baseline strings in use (to register before ingest, rule 7)

- JRF post-Budget projection path with the two-child limit retained ("than if the policy was retained"), November 2024 to November 2029
- JRF post-Budget projection path: Autumn Budget 2025 policy on the OBR November 2025 forecast, household disposable income after housing costs projected November 2024 to November 2029 ("the average (mean) household will be £850 (2.0%) per year worse off in November 2029 than in 2024")
- JRF post-Budget projection: current policy after Autumn Budget 2025 on the OBR November 2025 EFO central scenario ("Our central scenario uses projections made at the Autumn Budget by the Office for Budget Responsibility (OBR). These projections predict how the economy will develop over the next few years based on current Government policy"), incomes projected to April of each year
- JRF post-Spring-Forecast-2026 projection path: current policy on the latest OBR forecasts ("The modelling uses the most up to date forecasts from the Office for Budget Responsibility (OBR) on key economic indicators such as CPI inflation and average weekly earnings"), incomes to April of each year, 2025/26 prices
