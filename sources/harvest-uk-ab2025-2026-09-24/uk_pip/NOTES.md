# uk_pip — Policy in Practice, Autumn Budget 2025 harvest (2026-09-24)

Source `policy_in_practice`, `source_model: administrative_data`, `benchmark_class:
administrative_fact` on every own row; `conditions.data_scope = "8 local authorities' UC records"`
verbatim on the sample rows, with the sample description in `conditions.sample`.

## Access recipe

- policyinpractice.co.uk `robots.txt` disallows only query-string variants and wp-admin. Both WordPress
  posts fetched directly, HTTP 200; the scenario table is HTML text (cells joined with " | " by the
  extractor, which is how the quotes read).

## Coverage tally (seed bullets → rows)

- 24 Nov "Benefit cap blocks support for 1 in 5 families" — 6 bullets → 23 rows: the scenario table in
  full (4 scenarios × 3 benefit-cap statuses + cost per child £95 / £99 / £76 / £101); 17 % of families
  and 30 % of children currently losing out; 3,100 children in the sample with no gain; 95 % of children
  gaining in full when the cap is raised; £3,500 a year and 400,000 families (restated DWP); £24bn
  unclaimed (own). NOT staged: the LIFT map (demo data), webinar and cookie text.
- 28 Nov "Budget 2025: What does it mean for low income households?" — 2 bullets → 13 rows: 450,000
  (restated); 17 % and "1 in 5" (own, restated from 24 Nov); £155m Scotland (restated); NLW 4.1 % /
  8.5 % / 6 %, State Pension 4.8 %, £150 energy, UC standard allowance +2.4pp, Help to Save 20 %
  (all restated policy parameters, staged for the tally); "over £2 billion" for "over 1 million people"
  (own). NOT staged: "Half of these families will get part … the other half won't get anything"
  (qualitative restatement of the table); the earned-income disregard (no number).

## Corrections to the seed inventory

- None of substance. The seed's "per week implied by context; unit not stated" for the £95 / £99 / £76
  / £101 figures is confirmed and carried as `conditions.unit_period`, parse_confidence medium.
- The 24 Nov post calls the event "Wednesday's Autumn Statement"; `fiscal_event` is
  `autumn_budget_2025` throughout (rule 6).

## Baselines

- All own rows are against current law at the scoring date (`baseline_policy: null`); the sample
  shares are static re-computations of entitlement on the LA records, not a projection.
- The restated 450,000 carries `end_of_parliament_pre_ab2025` like the other producers' restatements.

## Attribution decisions

- own (25): every sample share and cost-per-child cell, the 3,100 count, the £24bn / £2bn / 1m figures.
- restated (11): DWP £3,500 / 400,000, HMT 450,000, Scottish £155m, the April 2026 rates and the
  Help to Save take-up.
- Scenario keys: "Remove 2 Child Limit" → `ab2025_option__scrap_two_child_limit`; "Replace with 3
  Child Limit" → `ab2025_option__three_child_limit`; the "+ raise Benefit Cap" variants keep the
  two-child / three-child key with `conditions.package_second_key =
  ab2025_option__raise_the_benefit_cap_to_living_wage_equivalent` (£29,000 London, £26,000 outside).

## Proposals (proposed_metric / proposed_unit) with the producer's definition

- `affected_share` (share): table "Share of low income households that gain, fully or partially, for
  various policy change scenarios" rows "Already benefit capped / No financial gain", "Become benefit
  capped / Only gain partially", "Not benefit capped / Gain in full"; "17% of families are currently
  losing support due to the two child limit"; "30% of children are losing out"; "95% of children gaining
  in full"; "1 in 5 families won’t receive the full benefit".
- `cost_per_child_gaining` (gbp): table row "Cost per child who gains financially" — "When raising the
  Benefit Cap, the cost per child excludes the impact on households not currently impacted by the 2
  child limit".
- `affected_count` (children / families / persons): "3,100 children seeing no financial gain"; DWP
  "400,000 families"; "over 1 million people".
- `benefit_loss_per_child` (gbp): "£3,500 a year foregone per child".
- `minimum_wage_uprating_rate` (percent): "the main rate (for 21 and over) will rise by 4.1%, 18 to 20
  year olds will get an 8.5% pay rise, and there’s a 6% boost for 16 or 17 year olds".
- `household_bill_change` (gbp_per_household): "the average £150 stated by the Chancellor".
- `devolved_budget_saving` (gbp): "the Scottish Government saves £155m".
- No proposed_unit is used.

## Manifest (primaries fetched 2026-09-24, sha256 + bytes)

- 2025-11-24 · html · direct · `55ead16f68e907e6…` · 163,480 bytes · New analysis: Benefit cap blocks support for 1 in 5 families hit by two child limit (Rory Ewan)  
  https://policyinpractice.co.uk/blog/new-analysis-benefit-cap-blocks-support-for-1-in-5-families-hit-by-two-child-limit/
- 2025-11-28 · html · direct · `d5446689959a12fe…` · 170,072 bytes · Budget 2025: What does it mean for low income households? (Rebecca McDonald)  
  https://policyinpractice.co.uk/blog/budget-2025/

## Row tally by publication and measure key

- 2025-11-24: 23 rows
- 2025-11-28: 13 rows

- measure_key `None`: 12
- measure_key `ab2025__renewables_obligation_exchequer_funded_75pct`: 1
- measure_key `ab2025__supporting_savers_help_to_save_and_cash_isa_limit`: 1
- measure_key `ab2025__uc_child_element_remove_two_child_limit`: 3
- measure_key `ab2025__uc_standard_allowance_and_health_element_rebalancing`: 1
- measure_key `ab2025_option__scrap_two_child_limit`: 10
- measure_key `ab2025_option__three_child_limit`: 8

## Attribution and class counts

- attribution: own 25, restated 11
- benchmark_class: administrative_fact 33, different_model 3
- source_model: administrative_data 33, dwp_policy_simulation_model 1, hmt_costing_obr_certified 1, obr_efo_forecast 1
- baseline_policy: None 35, end_of_parliament_pre_ab2025 1
- value_kind: central 1, point 33, range_low 2; time_basis: annual 3, fiscal_year 32, point_in_time 1; parse_confidence: high 31, medium 5

## Registered metrics and units used

- metric: benefit_uprating_rate 2, participation_rate 1, poverty_count_change 1, unclaimed_benefit_amount 2
- unit_concept: children 2, families 1, gbp 8, gbp_per_household 1, percent 4, percentage_points 1, persons 1, share 18

## Distinct values on every conditions axis

- `cap_scope_note` (1): when raising the Benefit Cap, the cost per child excludes the impact on households not currently impacted by the 2 child limit
- `data_scope` (1): 8 local authorities' UC records
- `denominator` (5): UC families with children in the sample (49,000) | children in UC families in the sample | children in the sample's two-child-limit households | households currently held back by the two child limit in the sample | low income families with children (PiP's eight-LA sample)
- `fiscal_event` (1): autumn_budget_2025
- `fy` (3): 2025-26 | 2026-27 | 2029-30
- `geography` (3): Scotland | UK | UK (eight local authorities, county and district)
- `horizon` (1): end_of_parliament
- `measure_type` (10): amount foregone per child under the two child limit | children losing out under the two child limit | cost per child who gains financially | families affected by the two child limit | families currently losing support due to the two child limit | families who currently lose out under the two child limit | people helped to identify unclaimed benefits last year via PiP tools | real-terms uprating above September 2025 CPI (Universal Credit Act 2025) | sample count, not grossed | unclaimed benefits identified for clients' residents last year via PiP tools
- `origin` (7): Chancellor | DWP | Government | Government (April 2026 rates confirmed at the Budget) | HM Treasury / DWP Budget assessment | Policy in Practice 'Missing Out' 2025 | Scottish Government / SFC
- `package` (2): raise_the_benefit_cap_to_living_wage_equivalent (£29,000 London, £26,000 outside) + scrap_two_child_limit | raise_the_benefit_cap_to_living_wage_equivalent (£29,000 London, £26,000 outside) + three_child_limit
- `package_second_key` (1): ab2025_option__raise_the_benefit_cap_to_living_wage_equivalent
- `program` (4): help_to_save | state pension and Pension Credit (triple lock) | universal_credit_child_element | universal_credit_standard_allowance
- `sample` (1): 105,000 households on Universal Credit, of whom 49,000 have children; a subset of the lowest income Universal Credit households receiving locally administered benefits such as Council Tax Reduction
- `sign_convention` (3): positive = children lifted out of poverty | positive = reduction in household energy bills | positive = saving to the Scottish Government
- `statistic` (1): average
- `subgroup` (9): 16 or 17 year olds | 18 to 20 year olds | National Living Wage (21 and over) | already benefit capped: no financial gain | become benefit capped: only gain partially | children gaining in full | children in already-capped families seeing no financial gain | families that won't receive the full benefit of the change (already capped or newly capped) | not benefit capped: gain in full
- `unit_period` (1): not stated on the page (weekly implied by context)
