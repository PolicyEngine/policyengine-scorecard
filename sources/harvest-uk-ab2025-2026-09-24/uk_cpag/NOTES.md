# uk_cpag — Child Poverty Action Group, Autumn Budget 2025 harvest (2026-09-24)

Source `cpag`. Engine `ukmod_b1.13` for the poverty and cost figures ("The results presented here are
based on UKMOD version B1.13", submission footnote 2 / briefing footnote 1); `ukmod_b1.11` for the
Scottish Child Payment modelling in the Scotland release; `arithmetic` for the benefit-cap worked
examples ("Author’s calculations from benefit and local housing allowance rates"); `administrative_data`
/ `survey_microdata` for the DWP and HBAI figures CPAG restates.

## Access recipe

- cpag.org.uk `robots.txt`: Drupal defaults (only /admin, /search etc. disallowed). Four pages and two
  PDFs fetched directly, HTTP 200. The page text is padded with the site's full navigation; the notes
  scripts read from the second occurrence of the headline to "Post type". PDFs text-extracted with pypdf
  (one sentence in the submission spans the p.3/p.4 page break; the row quotes the p.4 fragment).
- The 13 Oct page's Table 1 (seven local rental areas) is HTML text, not an image (the seed said image),
  and is staged in full.

## Coverage tally (seed bullets → rows)

- 13 Oct benefit-cap release — 2 bullets → 15 rows: Table 1 (Inner London £3, Guildford £82, Brighton
  and Hove £89, Oxford £118, Harlow £144, Northampton £170, Cardiff £210); 95 % of England and Wales
  (2025) vs 60 % (2023); 124,000 households / nearly 300,000 children / 28,000 in 2013 (restated DWP);
  69 % single parents (restated); removal: 300,000 depth and £300m. NOT staged: cap thresholds £423.46
  / £486.98 a week (policy parameters, not outcomes); the London couple case study (£573 a month after
  rent — testimony, not analysis); the "£44 in 2023" figure is not on this page (staged from the PDFs).
- 17 Oct Budget submission — 4 bullets → 15 rows (landing page manifested; all rows from the PDF):
  4.5m (restated HBAI) and 4.7m by the end of the parliament; 350,000 instantly, 150,000 prevented,
  700,000 depth, £2bn today rising to £3bn, 109 a day; 124,000 capped (restated, printed "124, 000"),
  £3 / £44, 300,000 depth, £300m; school costs £1,000 / £2,300.
- 19 Nov pre-Budget briefing — 3 bullets + restated → 18 rows: 4.5m / 4.7m; 350,000 / 700,000 / £2bn;
  109 a day; 124,000; £3 / £44; 95 % / 60 %; 300,000 / £300m; both policies 400,000 / nearly a million /
  £2.5bn; 3.1m vs 2.2m deep poverty (restated HBAI).
- 26 Nov UK release — 1 bullet → 1 row (59 % working families, restated DWP); "most have three
  children" has no number.
- 26 Nov Scotland release — 1 bullet → 10 rows: >£150m freed (restated SFC), £155m mitigation cost
  (restated), £34m FAI (restated), SCP £40: 15,000 / one-to-two pp / £190m (own, UKMOD B1.11, 2025/26
  prices), £37.50: 10,000 (own), FAI £35: £121m / −1pp (restated) — the seven SCP rows are keyed to
  `ab2025_option__scottish_child_payment_increase` with the £40 / £37.50 / £35 variant in reform_hint.
- "The Cost of a Child in 2025" (Loughborough CRSP for CPAG, 23 Oct) — 3 seed bullets NOT staged:
  producer slug `loughborough_crsp` belongs to the uk_thinktank_misc lane, and it is a Minimum Income
  Standard budget exercise, not microsimulation; outside this family's brief.

## Corrections to the seed inventory

- Seed: the 13 Oct "Table 1 of local rental areas … is an image and was not transcribed" — it is text
  on the fetched page and is staged (7 rows).
- Seed puts "£3 a week (down from £44 in 2023)" under 13 Oct; the £44 appears only in the 17 Oct and
  19 Nov PDFs ("down from £44 a week in 2023"). Staged from those.
- The 13 Oct page says "95% of England and Wales"; the PDFs say "95 per cent of the country" —
  geography carried as "England and Wales" on all three with the PDF wording noted in measure_type.

## Baselines and periods

- "instantly" / "today" rows: period 2026 (FY 2025-26, the scoring year), `baseline_policy: null`
  (current law at the scoring date), `conditions.horizon` immediate.
- "by the end of this parliament" / "over this parliament" rows (4.7m baseline level, 150,000
  prevented entries, £3bn): period 2030 (FY 2029-30), `baseline_policy: end_of_parliament_pre_ab2025`.
- The £300m benefit-cap cost carries no year on any CPAG page; staged at the scoring year with a
  `year_note`.

## Attribution decisions

- own (43): every UKMOD figure, the benefit-cap worked examples and area shares, the school-cost
  research, the SCP modelling.
- restated (16): DWP benefit-cap and two-child statistics, HBAI levels (4.5m, 3.1m, 2.2m), SFC /
  Scottish Government (£150m, £155m) and Fraser of Allander (£34m, £121m, −1pp).
- Package rows (both policies) keyed on the two-child option with `conditions.package_second_key`
  naming the benefit-cap key.
- The cost-per-child-lifted comparison CPAG makes in prose ("most cost-effective") has no printed
  cost-per-child figure in these documents, so no `cost_per_child_lifted_out_of_poverty` row was
  needed; the proposal name is reserved for the ingest's drop rule.

## Proposals (proposed_metric / proposed_unit) with the producer's definition

- `household_post_rent_income` (gbp_per_week): Table 1 "Weekly post-rent income" — "the cap leaves an
  Inner London lone parent with three children renting a private sector, three-bedroom home, with £3 to
  live on after she’s paid her rent" (single-household worked examples, mode-3 material).
- `affected_share` (share): "capped in 95% of England and Wales, compared to 60% in 2023"; "69% of
  capped households are single parents"; "59% of families affected by the two-child limit have at least
  one working parent".
- `affected_count` (children): "nearly 300,000 children are affected by the cap".
- `poverty_depth_reduction_count` (children): "reduce the depth of poverty for 300,000 children";
  "reducing the depth of poverty for a further 700,000 children"; "nearly a million more".
- `poverty_entries_per_day` (children): "an estimated 109 children are pushed into poverty every day by
  the policy".
- `minimum_cost_of_education` (gbp): "the minimum cost of education parents in the UK must meet is now
  over £1,000 a year for a child at primary school and nearly £2,300 a year for a child at secondary
  school".
- `devolved_budget_saving` (gbp): "frees up over £150 million in the 2026/27 Scottish budget".
- No proposed_unit is used.

## Registry gaps (resolved 2026-09-24)

- Scottish Child Payment increases (£40 / £37.50 / £35 a week) were unkeyed in the first pass; the key
  `ab2025_option__scottish_child_payment_increase` (all variants) was registered the same day and the
  seven rows now carry it, variant in reform_hint. No `measure_scope: unkeyed` rows remain.
- The £155m mitigation cost is staged as `benefit_cost` (a devolved programme level) and the £34m FAI
  knock-on as `benefit_cost_change` keyed to the announced two-child measure.

## Manifest (primaries fetched 2026-09-24, sha256 + bytes)

- 2025-10-13 · html · direct · `5f9f00276fb3d3dd…` · 153,320 bytes · Benefit cap leaving families with as little as £3 after rent (press release)  
  https://cpag.org.uk/news/benefit-cap-leaving-families-little-ps3-after-rent
- 2025-10-17 · html · direct · `b8666fc907bc088a…` · 149,779 bytes · CPAG's 2025 Budget Submission (landing page)  
  https://cpag.org.uk/news/cpags-2025-budget-submission
- 2025-10-17 · pdf · direct · `931aca965c1f536a…` · 265,469 bytes · CPAG's 2025 Budget Submission (PDF, 7 pp.)  
  https://cpag.org.uk/sites/default/files/2025-10/Budget_25_submission_final.pdf
- 2025-11-19 · pdf · direct · `2e99aaf539a2378c…` · 225,232 bytes · CPAG's 2025 pre-Budget briefing (PDF, 5 pp., November 2025)  
  https://cpag.org.uk/sites/default/files/2025-11/CPAG_pre-Budget_briefing_25.pdf
- 2025-11-26 · html · direct · `853a7ca3cfef4b55…` · 150,805 bytes · Abolition of two-child limit 'transformational for children' (press release)  
  https://cpag.org.uk/news/abolition-two-child-limit-transformational-children
- 2025-11-26 · html · direct · `2ac78b92ae981fe7…` · 151,530 bytes · Scotland's child poverty campaigners hail two-child limit abolition (CPAG in Scotland / End Child Poverty press release)  
  https://cpag.org.uk/news/scotlands-child-poverty-campaigners-hail-two-child-limit-abolition

## Row tally by publication and measure key

- 2025-10-13: 15 rows
- 2025-10-17: 15 rows
- 2025-11-19: 18 rows
- 2025-11-26: 11 rows

- measure_key `None`: 33
- measure_key `ab2025__uc_child_element_remove_two_child_limit`: 2
- measure_key `ab2025_option__remove_the_benefit_cap`: 6
- measure_key `ab2025_option__scottish_child_payment_increase`: 7
- measure_key `ab2025_option__scrap_two_child_limit`: 11

## Attribution and class counts

- attribution: own 43, restated 16
- benchmark_class: administrative_fact 13, different_model 46
- source_model: administrative_data 7, arithmetic 17, not_stated 3, obr_efo_forecast 2, survey_microdata 4, ukmod_b1.11 5, ukmod_b1.13 21
- baseline_policy: None 55, end_of_parliament_pre_ab2025 4
- value_kind: central 1, point 51, range_high 4, range_low 3; time_basis: annual 9, fiscal_year 44, point_in_time 6; parse_confidence: high 45, medium 14

## Registered metrics and units used

- metric: benefit_cost 1, benefit_cost_change 1, caseload 4, poverty_count 6, poverty_count_change 6, poverty_rate_change 3, revenue_change 9
- unit_concept: children 21, families 1, gbp 14, gbp_per_week 11, households 3, percentage_points 3, share 6

## Distinct values on every conditions axis

- `basis` (1): static
- `denominator` (2): capped households | families affected by the two-child limit
- `engine_note` (1): UKMOD B1.13 per the 17 Oct submission (the page itself does not name the model)
- `fiscal_event` (1): autumn_budget_2025
- `funding_note` (1): £155m (the earmarked two-child mitigation money) funds a payment of £37.50
- `fy` (5): 2012-13 | 2023-24 | 2025-26 | 2026-27 | 2029-30
- `geography` (11): Brighton and Hove | Cardiff | England and Wales | GB | Guildford | Harlow | Inner London | Northampton | Oxford | Scotland | UK
- `horizon` (4): end_of_parliament | immediate | immediate ('instantly') | immediate ('today')
- `household` (1): lone parent with three children renting a private-sector three-bedroom home
- `housing_costs` (1): ahc
- `measure_type` (6): children pushed into poverty per day by the two-child limit (current-policy flow, continuing until 2035) | prevented_entries_over_parliament | share of local rental areas in which the example household is capped | share of local rental areas in which the example household is capped ('the country') | worked example: weekly entitlement after housing costs for a capped household | worked example: weekly income after rent for a capped household
- `method` (1): Author’s calculations from benefit and local housing allowance rates
- `model_version` (1): B1.11
- `origin` (12): CPAG, The minimum cost of education in the UK, 2025 | DWP | DWP HBAI 2023/24 (record high) | DWP benefit cap statistics | DWP benefit cap statistics (households capped to May 2025) | DWP two-child limit statistics | DWP, Benefit cap: number of households capped to May 2025 | Fraser of Allander Institute analysis | Fraser of Allander Institute modelling | Scottish Fiscal Commission / Scottish Government | Scottish Fiscal Commission forecasts | latest poverty statistics (HBAI)
- `package` (1): scrap_two_child_limit + remove_the_benefit_cap
- `package_second_key` (1): ab2025_option__remove_the_benefit_cap
- `poverty_line` (2): deep poverty (producer's definition not stated on the page) | relative_60_median
- `prices` (1): 2025/26
- `program` (3): Scottish two-child limit mitigation payments | benefit_cap | discretionary housing payments (benefit-cap interaction) and widened Scottish Child Payment eligibility
- `scenario` (1): without further action
- `sign_convention` (8): positive = additional Scottish spending required | positive = children lifted out of poverty | positive = children prevented from being drawn into poverty over the parliament | positive = children whose depth of poverty is reduced | positive = cost to the Exchequer | positive = cost to the Scottish budget | positive = money freed up in the Scottish budget | positive = rise in the child poverty rate
- `subgroup` (5): a child at primary school | a child at secondary school | children | families with at least one working parent | single parents
- `year_note` (1): no year stated; staged at the scoring year
