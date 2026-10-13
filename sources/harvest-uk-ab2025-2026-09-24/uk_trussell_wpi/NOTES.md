# uk_trussell_wpi — Trussell / WPI Economics, Autumn Budget 2025 harvest (2026-09-24)

Source `trussell_wpi`, `source_model: wpi_hardship_model` for the severe-hardship projections
(proposed_metric `severe_hardship_count_change`, `conditions.poverty_measure = wpi_severe_hardship` so
these rows are never unified with HBAI poverty); `administrative_data` / `survey` for Trussell's
food-bank network and Hunger in the UK figures; `not_stated` for the LHA-freeze modelling whose source
the page does not give.

## Access recipe

- trussell.org.uk `robots.txt`: `User-Agent: * / Allow: /`. Both news pages fetched directly, HTTP
  200. The WPI technical report is on cms.trussell.org.uk (robots allow-all), 65 pages, pypdf text;
  Tables 24a–c (UK) and 25a–28a (nations) are on pp. 51–60, "Policy impacts in Year 5". The main Cost of
  Hunger and Hardship report and the 30 Apr 2025 press release were not fetched (not needed for any
  staged value; see the 470,000 note below).
- Every `quote` was machine-checked against the extracted text; the UK table rows quote the
  whitespace-collapsed table line (e.g. "Remove two child limit £3.3bn increase in social security spend
  -670,000 £3.1bn £1.1bn £1.4bn £540m £1.5bn").

## Coverage tally (seed bullets → rows)

- 26 Nov "Our response to lifting the two-child limit" — 1 bullet → 6 rows: 470,000 children (quote and
  background), 670,000 people, 7 % and 15 % decreases, £3.1bn per year.
- 11 Dec "Our response to the Autumn Budget and Child Poverty Strategy" — 3 bullets + restated → 17
  rows: 470,000 (own); 29 % of parcels (own network data); 141,000 (restated JRF); 500,000 and 1m
  (restated JRF, keyed to the floor option with `jrf_pre_ab2025_projection_path`); LHA freeze £700,
  50,000 / 60,000 / 80,000 / 30,000 (own, engine not stated, parse_confidence low, keyed to
  `ab2025_option__lha_freeze_maintained`); 14m and
  3.8m faced hunger (own survey); £900 NLW (restated); 30 % / 24 % working referrals and 41 % / 36 %
  homelessness (own network data). NOT staged: "Half (50%) of private renters receiving social security
  support for housing payments experienced food insecurity" (not in the seed; second pass), the £8m
  temporary-accommodation pilots and the Crisis and Resilience Fund (no Trussell number).
- WPI technical report (30 Apr 2025, the basis the seed traced the 26 Nov figures to) — 33 rows: Table
  24a UK "Remove two child limit and benefit cap" / "Remove two child limit" / "Remove benefit cap"
  (change in social security spend, reduction in people at risk of H&H, total benefits) and the
  Tables 25a–28a nation headline rows (people and total benefits) for the same three policies. These are
  pre-Budget OPTION scores keyed to `ab2025_option__scrap_two_child_limit` /
  `ab2025_option__remove_the_benefit_cap`; the 26 Nov / 11 Dec page rows are keyed to the announced
  measure. NOT staged: the other policies in Tables 24–28 (income maximisation, Scottish Child Payment
  extension, Essentials Guarantee, FSM, Real Living Wage, HSF, UC taper — outside the AB2025 measure
  set; second pass), the sub-columns (reduced public spending, employment, tax) and the wellbeing
  column, the cumulative 5-year tables.

## Corrections to the seed inventory

- The 470,000-children figure is not in the technical report (its tables are people, not children);
  it is staged from the Trussell pages only, with the technical report's −670,000 people row as the
  cross-check (Table 24a, Year 5). The seed's "projection year 2027" is WPI's Year 5 = 2026/27
  (`period 2027`, `conditions.fy 2026-27`, 2023/24 prices).
- Seed: "the April 2025 report says 'over £3 billion'" — the technical report Table 24a prints £3.1bn
  for total benefits of removing the two-child limit, matching the 26 Nov page.
- Seed reads "lift 670,000 people out of severe hardship"; the technical report column is "Reduction in
  the number of people at risk of H&H" and prints −670,000. Signs are carried as printed on each
  primary (positive on the Trussell pages, negative in the WPI tables) with the sign convention on the
  row; nothing is re-signed.

## Baselines

- WPI rows and the Trussell page rows carry `proposed_baseline` = the WPI projection world (string
  below); it is neither current law at the scoring date nor an end-of-parliament world.
- Restated JRF rows keep `jrf_pre_ab2025_projection_path`; the LHA rows and network/survey facts carry
  `baseline_policy: null`.

## Attribution decisions

- own (52): WPI-model figures on the Trussell pages and in the technical report, Trussell's network and
  survey statistics, the LHA rows (Trussell-published, engine unknown).
- restated (4): JRF's 141,000 / 500,000 / 1m and the Government's £900 NLW figure.
- Package rows ("Remove two child limit and benefit cap") keyed on the two-child option with
  `conditions.package_second_key = ab2025_option__remove_the_benefit_cap`.

## Proposals (proposed_metric / proposed_unit) with the producer's definition

- `severe_hardship_count_change` (persons / children / percent): "lift 670,000 people out of severe
  hardship, including 470,000 children by 2027. This represents a 7% decrease in the number of people
  and a 15% decrease in the number of children expected to face hunger and hardship"; WPI: "Reduction
  in the number of people at risk of H&H", where "A family is considered to face H&H if they are more
  than 25% below the Social Metrics Commission poverty line".
- `fiscal_and_economic_benefit` (gbp): "benefit the economy and public purse by around £3.1 billion per
  year through relieving pressure on public services, supporting people to find and sustain work, and by
  increasing tax revenue"; WPI column "Total benefits (public spending, economy, fiscal)". Not a policy
  cost.
- `affected_count` (persons / children): "More than 14 million people – including 3.8 million children –
  faced hunger in the UK last year"; JRF's "141,000 children".
- `affected_share` (share): "three in 10 (30%) people referred to food banks in 2024 were in working
  households"; "Forty-one percent … were currently homeless".
- `food_parcel_share` (share): "nearly three in 10 emergency food parcels (29%) were provided for
  families with three or more children".
- `average_annual_loss` (gbp): "private renters on housing benefits will be around £700 worse off per
  year by 2029".
- `take_home_pay_change` (gbp): "increases to Minimum Wage and the National Living Wage (worth around
  £900 a year)".
- `poverty_depth_reduction_count` (children): JRF's "reduced the depth of poverty for a further 1
  million".
- Registered `benefit_cost_change` carries WPI's "Total change in resources" ("£3.3bn increase in
  social security spend"); registered `poverty_count_change` carries the LHA rows with the producer's
  depth label in `conditions.poverty_line` (threshold not stated).

## Registry gaps (resolved 2026-09-24)

- The continued LHA freeze was unkeyed in the first pass; `ab2025_option__lha_freeze_maintained` (the
  counterfactual to `ab2025_option__relink_lha_to_30th_percentile_of_local_rents`) was registered the
  same day and the five LHA rows (£700; 50,000 / 60,000 / 80,000 / 30,000) now carry it, reform_hint
  "If LHA remains frozen over the course of this parliament". No `measure_scope: unkeyed` rows remain.

## Manifest (primaries fetched 2026-09-24, sha256 + bytes)

- 2025-04-30 · pdf · direct · `27a8cd140f58cc38…` · 1,012,998 bytes · The Cost of Hunger and Hardship: final technical report (WPI Economics for Trussell)  
  https://cms.trussell.org.uk/sites/default/files/2025-04/cost_of_hunger_and_hardship_final_technical_report.pdf
- 2025-11-26 · html · direct · `6f693a2d1cc677a9…` · 177,013 bytes · Our response to lifting the two-child limit (Helen Barnard, press release)  
  https://www.trussell.org.uk/news-and-research/news/our-response-to-lifting-the-two-child-limit
- 2025-12-11 · html · direct · `e943353a68cfb6a0…` · 195,840 bytes · Our response to the Autumn Budget and Child Poverty Strategy (Elizabeth Miller, analysis)  
  https://www.trussell.org.uk/news-and-research/news/our-response-to-the-autumn-budget-and-child-poverty-strategy

## Row tally by publication and measure key

- 2025-04-30: 33 rows
- 2025-11-26: 6 rows
- 2025-12-11: 17 rows

- measure_key `None`: 9
- measure_key `ab2025__uc_child_element_remove_two_child_limit`: 7
- measure_key `ab2025_option__lha_freeze_maintained`: 5
- measure_key `ab2025_option__remove_the_benefit_cap`: 11
- measure_key `ab2025_option__scrap_two_child_limit`: 22
- measure_key `ab2025_option__uc_protected_minimum_floor_deductions_capped_at_15pct`: 2

## Attribution and class counts

- attribution: own 52, restated 4
- benchmark_class: administrative_fact 9, different_model 47
- source_model: administrative_data 7, landman_ttm 2, not_stated 5, survey 2, wpi_hardship_model 40
- baseline_policy: None 54, jrf_pre_ab2025_projection_path 2
- value_kind: central 3, point 52, range_low 1; time_basis: annual 12, fiscal_year 41, point_in_time 3; parse_confidence: high 51, low 5

## Registered metrics and units used

- metric: benefit_cost_change 3, poverty_count_change 5
- unit_concept: children 8, gbp 21, percent 2, persons 20, share 5

## Distinct values on every conditions axis

- `data` (1): FRS 2022/23 base, projected to 2026/27
- `data_scope` (3): Trussell Hunger in the UK survey | Trussell food bank network referrals | Trussell food bank network, last year
- `denominator` (1): emergency food parcels
- `engine_note` (1): source of modelling not stated on the page
- `fiscal_event` (1): autumn_budget_2025
- `fy` (1): 2026-27
- `geography` (5): England | Northern Ireland | Scotland | UK | Wales
- `hardship_definition` (1): a family faces hunger and hardship if it is more than 25% below the Social Metrics Commission poverty line (WPI technical report, footnote 1)
- `hardship_measure` (1): faced hunger last year because they didn't have enough money for food
- `horizon` (4): Year 5 (2026/27) | by 2027 (WPI Year 5 = 2026/27) | by 2029 | end_of_parliament
- `housing_costs` (1): ahc
- `measure_type` (3): interaction_two_child_limit_and_benefit_cap | relative change | total benefits (public spending, economy, fiscal) - not a policy cost
- `origin` (3): Government | JRF (30 Sep 2025) | JRF (30 Sep 2025), IPPR tax-benefit model
- `package` (2): scrap_two_child_limit + remove_the_benefit_cap | uc_protected_minimum_floor + two-child limit removal
- `package_second_key` (2): ab2025__uc_child_element_remove_two_child_limit | ab2025_option__remove_the_benefit_cap
- `poverty_line` (4): deep poverty (producer's threshold not stated on the page) | poverty (producer's threshold not stated on the page) | relative_60_median | very deep poverty (producer's threshold not stated on the page)
- `poverty_measure` (1): wpi_severe_hardship
- `prices` (2): 2023/24 | 2023/24 (WPI convention)
- `program` (1): National Living Wage April 2026 increase
- `scenario` (1): LHA remains frozen over the course of the parliament
- `sign_convention` (14): negative = reduction in the number of people at risk of hunger and hardship (as printed) | positive = benefit to public spending, economy and fiscal position | positive = benefit to the economy and public purse | positive = children lifted out of poverty | positive = children lifted out of severe hardship | positive = children lifted out of severe hunger and hardship | positive = children whose depth of poverty is reduced | positive = increase in social security spend | positive = increase in the number expected to face hunger and hardship | positive = loss to households | positive = people lifted out of severe hardship | positive = pushed into deep poverty | positive = pushed into poverty | positive = pushed into very deep poverty
- `statistic` (1): average
- `subgroup` (9): all people | children | children in families impacted by the two-child limit who are also benefit capped | children of renters | families with three or more children | people referred to food banks who were currently homeless or had experienced homelessness in the previous year | people referred to food banks who were in working households | private renters receiving housing benefit / UC housing support | renters

## proposed_baseline strings in use (to register before ingest, rule 7)

- WPI Economics projection of hunger and hardship to 2026/27 (Year 5) from a 2022/23 FRS base under policy as of April 2025 ("headline estimates made for the 2022/23 year, year five policy impacts based on results from 2026/27"), 2023/24 prices
