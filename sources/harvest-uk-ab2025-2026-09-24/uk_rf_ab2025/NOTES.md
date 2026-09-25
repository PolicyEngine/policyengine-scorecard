# uk_rf_ab2025 — Resolution Foundation, Autumn Budget 2025 (staged 2026-09-24)

1,460 claims from 20 manifested primaries. `source: resolution_foundation`; `source_model:
landman_ttm` (the IPPR tax-benefit model behind every RF distribution/projection figure),
`rf_case_study_model` (Stairway Table 1 and the 2028-29 £73/£222/£52 freeze figures), `arithmetic`
for RF costings and OBR/HMT re-arrangements, plus the OBR/HMT/DWP engines on `restated` rows.
Period is the FY END year (`conditions.fy` carries the label). Seeds:
`SEED_INVENTORY/scores-2-rf-poverty.md` § Resolution Foundation.

## Access recipe per document

Every RF PDF and page fetched directly with a browser User-Agent (HTTP 200, no blocks). Image
tables (Call of duties Tables 1-2 and Box 2, Black holes Table 1, Stairway Table 1) were rendered
with pymupdf at 170 dpi and transcribed (`parse_confidence: medium`). Every RF chart is an Excel-style
VECTOR export, so Stairway Figures 13, 17, 18, 19, 20, 21, 22 and Call of duties Figure 8 were
digitised from the drawing paths (`digitise_rf.py`, output `digitised_figures.json` in the scratchpad):

- stacked bars = one filled-rect drawing per series (legend swatch colour → label read from the words
  right of each swatch); net change = white diamond quads; % change = dark polyline with circle markers;
- the y-axis is a least-squares line on the HORIZONTAL GRIDLINES matched to the tick labels. The tick-label
  text centres sit 1.7 pt above the gridlines; bar bases coincide with the zero gridline, so gridlines
  are the truth. Calibrating on label centres instead would shift every reading by ~£28 / 0.11 ppt
  (Fig 18), £37 / 0.15 ppt (Fig 20), £29 / 0.07 ppt (Fig 21), £27 / 0.016 ppt (Fig 13), £2.2 (Fig 17),
  £26 / 0.1 ppt (Fig 22), 1.1 ppt (Fig 19);
- resolution ~0.1 pt (≈ £2, ≈ 0.005 ppt). All such rows: `value_kind: approx_chart_reading`,
  `parse_confidence: medium`, method in `note`;
- anchor checks against printed text: Fig 19 vigintiles 1-2 gain 67.2/59.4 % (text: 64 % of the poorest
  decile), 19-20 lose 95.4/95.7 % (text 96 %); Fig 17 medians decile 1-2 £107/£122 and 9-10 £147/£145 (text
  £115 lowest quintile, £145 top), % line 0.59/0.62 vs 0.40/0.36 (text 0.6/0.4); Fig 18 richest-fifth
  PTA+HRT components average −£530 (text £540), mansion tax v19-20 −£32/−£75 (text £50); Fig 22
  decile-10 stack £1,460 (text £1,500), deciles 1-2 share 8.3/5.5 % (text 7 % poorest fifth);
  Fig 21 % line 0-17 +1.05, 35-44 −0.53, 55-64 −1.33, 65+ −1.32 vs text 1.0/−0.6/−1.4/−1.3 (label-centre
  calibration would give 0.98/−0.60/−1.40/−1.39: the printed values sit between the two calibrations).
  Discrepancy left open: Fig 22's share line reads 0.55 % at decile 10 where the text says 0.8 % for the
  richest tenth (row parse_confidence low).
- Fig 19 x labels are rotated text; categories assigned by bar order and verified on the render
  (All, vigintiles 1-20, Pensioner household, Working-age no kids, Working-age with kids).
- Figures 18/20 and Call of duties Fig 8 omit vigintile 1 ("We exclude the bottom 5 per cent").
- Legend circles/segments drawn inside the plot box (Figs 13, 22) were excluded; % values come from the
  polyline vertices, which agree with the circle centres elsewhere to 0.01 ppt.

## Already in sources/harvest-uk-2026-08-02/uk_resolution_foundation (NOT re-staged)

Stairway 12 rows (£3,570 per child element; £360 poorest fifth; £540 / £64 freeze; £50 / £5 mansion
tax; £160 UC-Health; 64 % / 51 % / 78 % / 96 % Figure 19 text shares; £1.9bn eVED); Catching up 8 rows
(the six April-2026 uprating rates, −10 % real UC, £800m 2026-27); Happy new tax year 9 rows (whole
publication left out of this pass); LSO 2026 28 rows (poverty rates 33 %→30 %, −420,000, 19.9/19.5/16.0 %,
1.2/4.7/0.2/5.8/1.8 % growth, 0.9 %/yr Unsung Britain, £2.4bn/£3.1bn, 510,000/£4,560, £330m/−£210m,
£99/£47, Figure 8 uprating path); LSO 2025 14 rows. Grep that family's `claims_staged.jsonl.gz` for any
value before adding a row.

## Coverage tally (seed bullets → staged)

- Call of duties (23 Sep; 18 bullets): Table 2 all 14 measures + 3 subtotals + total (18 rows); £140/£280;
  Fig 7 28 %/29 %; >£5bn fuel-duty freezes; Box 2 £1-2bn rental and £1bn self-employed NI; tax gap
  £5bn/£15bn; £20-40bn framing; U-turns >£6bn; Fig 8 digitised (57 rows). NOT staged: £22bn employer
  contribution exemption cost and ">70 % of partnership income to the top 1 %" (no year printed);
  £1bn AB2024 cancelled uprating (no year); 0.6-1.8 months life expectancy (not a fiscal/distribution
  metric); Table 1 marginal-rate schedule (rates, not scores); inflation "zero or negative" (qualitative).
- Splitting the bill (16 Oct; 6 bullets): all quantified values (15 rows); per-year costs given fy 2026-27
  with the assumption flagged (`conditions.basis`).
- Catching up (22 Oct; 3 bullets): 4 new rows (£61, 40 %, 4.8 %, £1.85bn typo-corrected at parse_confidence low).
- It's personal (27 Oct; 2 bullets): 10 rows (55 %, 27 %/17 %, £3,500, £8bn/£9bn/>£10bn, 29 %, 16 %, 42 %).
  NOT staged: 13 % productivity, 0.1 % GDP illustration, OECD 29→32 % (international context).
- No half measures (30 Oct; 9 bullets): 35 rows incl. Figure 3's five printed labels (order verified on the
  render: +29,000 / +48,000 / +10,000 / +26,000 / +63,000 for 2025-26 … 2029-30). NOT staged: Figure 3 bar
  levels (~300k→~480k, unlabelled), Figure 5 bars other than the "half a percentage point" text.
- Black holes (4 Nov; 9 bullets + PR): Table 1 (18 rows, duplicate of Call of duties Table 2 by design),
  fiscal scenario, consolidation arithmetic, energy package, nil-rate VAT, other tax options, pensioner
  switch rows (55 + 3 PR rows). NOT staged: £20bn/£15bn recommended headroom (a recommendation),
  Unemployment Insurance £0.6-1.4bn (restated IFS, already an IFS-lane item), SDLT "up to £2bn" (no year),
  2p on all rates "around £20bn" and non-residential SDLT (no registry key AND no year).
- 14 Nov PR: 3 rows (£7.5bn, £6bn, £9bn). 26 Nov PR: 29 rows. 27 Nov PR: 18 rows.
- Stairway (27 Nov; 25 bullets): text rows for Figures 11-17 and pp.15-33 (fiscal context, freezes,
  salary sacrifice, capital-income rates, tax wedge, mansion tax, EVs, energy, fuel duty, two-child limit,
  benefit cap, smaller welfare measures), Table 1 (40 rows), Figure 23 (19 printed parliament labels +
  3 text rows), Box 2 coverage (3), and the digitised Figures 13 (76), 17 (40), 18 (~260), 19 (72),
  20 (~280), 21 (105), 22 (80). NOT staged: Box 1 minimum-wage rates (the PDF text extract does not
  carry the exact wording; the seed bullet is unverified here), Figure 6/7/8/9/12 series (charts of
  OBR/HMT aggregates; headline text values staged instead), "£45-54bn RDEL increase", "2.7 % vs 1.7 %
  investment", Figure 11 component stacks (unlabelled).
- Top of the Charts (28 Nov; 4 bullets): 14 rows. NOT staged: the £5m Westminster vs £210,000 Sunderland
  comparison (no number for the tax paid).
- 5 Dec PR (4 bullets): 8 rows. LSO 2026 (5 bullets): 8 new rows (cumulative 6.4 %/4.7 %, three-fifths,
  RHDI 0.3 %/0.4 %, real wages 0.3 %, 0.5 %/1.8 % long-run growth). NOT staged: energy ~60 %/food ~40 %
  price context, 4 %/yr and 2.9 %/yr 1994-2004 growth.
- Happy new tax year 2026: fetched and hashed (manifest) but not claim-mined — out of this pass's scope;
  its Figure 1/3 vigintile bars could be digitised with the same recipe.

## Distinct condition values per axis

- fy: 2004-05, 2007-08, 2018-19, 2019-20, 2023-24, 2024-25, 2025-26, 2026-27 (86), 2027-28, 2028-29 (140),
  2029-30 (1,032), 2030-31 (112). Calendar rows (time_basis annual): Figure 23 parliaments, RHDI quarters.
- geography: UK (1,276), England (96: HVCTS, Figure 22 in-kind, council tax variants), GB (74: energy
  bills), UK_excl_scotland (14: tax-wedge and marginal-rate rows).
- income_group: vigintile_1..vigintile_20 (Figs 13/18/19/20 and CoD Fig 8; vigintile_1 only in Fig 19),
  decile_1..decile_10 (Figs 17/22, Table 1 pre-measures deciles, Black holes deciles 1-3, Stairway deciles
  6-10), quintile_1 / quintile_5, all, and `bottom_half` / `top_half` — the last two are RF's "poorest /
  richest half" and are OUTSIDE the README's decile/quintile/vigintile/tertile spellings (13 rows; the
  2026-08-02 family used free-text "bottom half"). Ingest ruling needed.
- income_axis: net equivalised household income vigintile, after housing costs (807); net equivalised
  household income decile, after housing costs (130); age group (105); household income decile,
  pre-measures basis (40, Table 1); equivalised household income decile/quintile, after housing costs.
- housing_costs: ahc (1,103). poverty_line: relative_60_median (36). unit_population: households (750),
  persons (household income per person) (109, Fig 21), children (34), pensioners, working-age families,
  below-/above-middle income non-pensioner families, poorer half of non-pensioner families.
- age_group: 0-17, 18-24, 25-34, 35-44, 45-54, 55-64, 65+.
- household_type: the ten Table 1 labels verbatim (incl. the producer's "the the South East"), the three
  Fig 19 family types, and worked-example labels (typical employee, higher earner, very high earner,
  average pensioner, basic-rate pensioner (no NI), Ofgem typical household, owner of a £2.5 million home …).
- component: 60 labels — the Fig 18/20/21 legend entries verbatim (eVED, Salary sacrifice,
  Property/Dividends/Savings tax, Mansion tax, Energy bill reduction, Scrap two-child limit, HRT freeze,
  PTA freeze, Winter Fuel Payment extension / cut, UC Health cut, Free School Meals expansion / FSM
  expansion, UC standard allowance boost / UC SA boost, Fuel duty, Consumption tax rises / cuts, Employer
  NI rise, Net change in income, % change in income), Fig 22 departments (DHSC, Education, Police,
  Justice, Local government, Transport, DWP), Table 1 columns, energy-package parts, fiscal components.
- scenario, comparison, horizon, statistic, subgroup, variant, scope, rule, program, threshold, basis,
  costing_basis, no_change_band (+/-£10 per year), group (Table 2 blocks), series (Net effect): free text
  verbatim, listed in the staged file.
- sign_convention: 46 "positive = …" sentences; losses printed as losses are carried NEGATIVE with the
  convention "positive = gain to households" (Figs 13/18/20/21, halves); Exchequer rows carry
  "positive = yield" or "positive = cost" as published.

## Proposals used (producer definition quoted)

- `household_income_change` (gbp): Table 1 "Change in annual income (in 2025-26 prices) as a result of the
  key measures announced since Autumn Budget 2024, for ten specimen families: 2028-29"; PR "A typical
  family will gain £234 in 2026-27".
- `household_tax_change` (gbp): "basic-rate employees will pay around £220 more tax and National Insurance".
- `average_energy_bill_change` (gbp): "savings worth £130 for the typical household in 2026-27".
- `median_energy_bill_saving`, `energy_bill_saving_quartile` (gbp), `median_energy_bill_saving_share_of_spending`
  (percent): Figure 17 "Median and interquartile (p25-p75) range of annual savings … and median savings as a
  proportion of total non-housing expenditure".
- `share_no_change` (share): Figure 19 "No change (+/-£10p.a.)".
- `in_kind_benefit_change` (gbp), `in_kind_benefit_share_of_income` (percent): Figure 22 "In-kind benefits
  in cash terms … and as share of income … from the Government’s plans compared to previous Government’s plans".
- `effective_tax_rate`, `effective_tax_rate_change`, `tax_wedge_gap_ratio`, `ni_share_of_tax_wedge`,
  `marginal_tax_rate`: "Total Income Tax and National Insurance as a proportion of labour cost".
- `affected_share`, `affected_count`, `share_of_affected_households`, `share_of_affected_properties`,
  `ownership_share`, `incidence_share`, `beneficiary_share`, `electricity_share_of_savings`,
  `energy_burden_share`, `bill_saving_share_of_spending`, `backloading_share`, `modelling_coverage_share`,
  `cuts_relative_to_austerity_average`, `real_value_recovery_share`, `threshold_real_rise_reversed_share`,
  `offset_share_of_long_run_fuel_duty_loss`, `income_growth_contribution_share`.
- `fiscal_headroom`, `fiscal_consolidation_requirement`, `forecast_borrowing_change`,
  `forecast_revenue_change`, `policy_change_vs_previous_government_plans`, `psnfl_share_of_gdp`,
  `tax_to_gdp_ratio`, `tax_gap`, `spending_pressure`, `real_spending_growth`, `real_spending_change_per_person`.
- `break_even_income` (gbp): "less costly than freezing thresholds for anyone with an income below £35,000".
- `threshold_real_value_change`, `threshold_salary`, `threshold_savings`, `benefit_rate_real_change`,
  `benefit_rate_change`, `cumulative_over_indexation`, `poverty_rate_headroom`,
  `cost_per_child_lifted_out_of_poverty`, `child_population`, `average_charge_per_vehicle`,
  `employer_cost_per_employee_change`, `energy_policy_cost_per_household`, `energy_tax_per_household`,
  `energy_policy_costs_total`, `council_tax_share_of_income`, `real_wage_growth`, `salary_sacrifice_share`.
- No proposed units.
- Baselines: `rf_permanent_measures_since_ab2024` (366 rows: Figs 18-19 and the bottom/top-half text);
  `rf_start_of_parliament_policy` (436: Figs 20-21, the 27 Nov PR halves, deciles 6-10, TOTC welfare);
  proposed_baseline (145): "RF 'current policy' projection at 30 Oct 2025: pre-Budget policy including the
  FSM extension and UC over-indexation, excluding the Scottish Government's two-child-limit mitigation; OBR
  March 2025 earnings, Bank of England August 2025 CPI, HBAI 2023-24 base" (No half measures);
  "RF case-study counterfactual: policy before the key measures announced since Autumn Budget 2024 (…),
  2028-29" (Table 1); "the previous Government's spending plans (Spring 2024) for day-to-day public
  services, England, 2028-29" (Figure 22); "RF projection without the Child Poverty Strategy policies
  (two-child limit repeal, Free School Meals expansion), OBR November 2025 economic assumptions" (5 Dec).

## Attribution decisions

- `restated` (82): HMT costings (£3.1bn two-child limit incl. NI block grant, £4.7bn/£2.6bn salary
  sacrifice, £430m/165,000 HVCTS, £89 per car, £2.4bn/£0.8bn fuel duty, £2.6bn energy, £150 government
  bill figure, the five smaller welfare measures, U-turn totals), OBR EFO aggregates (£26bn, Figure 11
  net path, £13bn freezes, tax/GDP, 0.8m/0.9m taxpayers, £3.0bn, £7bn/£120bn fuel duty, CPI effects
  0.13/0.4/0.5, PSNFL, headroom levels, RHDI paths, £16bn productivity), Government 450,000, DWP
  two-child-limit and benefit-cap statistics (`administrative_fact`), HMRC tax gap, CenTax £2bn, IFS £2.1bn,
  TPA >£1bn, Universal Credit Act costings (£1.85bn, 4.8 %), State Pension +£560.
- `own` everything else, including RF's arithmetic on OBR tables (£68bn/£70bn, £77bn/73 %, +£1bn/−£24bn,
  £5.5bn vs £21bn) — flagged `source_model: arithmetic`.
- The 26 Nov PR figures re-appear in Stairway and TOTC; each publication's own statement is staged
  (dedup is the ingest's job).

## Inventory corrections and discrepancies

- No half measures Figure 3: seed's label order "+48,000, +10,000, +26,000, +63,000, +29,000" is the PDF
  text order; the rendered chart places +29,000 first (2024-25→2025-26). Staged in chart order.
- Stairway Table 1: text (p.34) calls the three-child single parent a London family; the table says Wales.
  Staged as printed in the table, note on every Table 1 row.
- Stairway p.25 "2023-34" is the producer's typo for 2023-24 (kept in value_raw).
- 5 Dec PR "80,0000" typo → 80,000 (parse_confidence medium). Catching up "£1.85 million" → £1.85bn
  (parse_confidence low).
- Two Budgets' tax rise: 26 Nov PR and Stairway say £68bn; TOTC says £70bn a year in 2029-30. Both staged.
- 2024-25 child poverty nowcast: 31 % (No half measures, 30 Oct) vs 32 % (5 Dec PR) — vintage change, both staged.
- Figure 22 decile-10 share: chart 0.55 % vs text 0.8 % (see access recipe).
- Fig 21 printed percentages vs digitised (see access recipe); text rows and chart rows both staged.
- Seed's "Figure 18 … +£500 … −£1,000 to −£1,500 … +4 % … −2 %" approximations are replaced by exact
  digitised markers (+£491 at vigintile 2, −£1,145 at vigintile 20; +3.65 % / −0.69 %, with −1.18 % at 19).
- Seed's "Figure 20 … −£2,000 to −£2,500 top vigintile" → −£2,140 digitised.
- Seed's "Figure 13 … 1p rise −£2,500 to −£3,000 in vigintile 20" → −£2,515; freeze −£905 at vigintile 20.
- Black holes and Stairway shas match the 2026-08-02 manifest (downloaded there, not mined).
