# uk_obr_tables — OBR Economic and fiscal outlook November 2025 (chapter 3), uncertainty ratings, supplementary notes

Staged 2026-09-24. Source slug `obr_efo`. 927 rows; 6 primaries in `manifest.jsonl` (the landing page carries no
claims). Scripts (scratchpad): `parse_obr.py` machine-reads every table from the pypdf text layer (Tables 3.1-3.10,
Box 3.3 Table A, supplementary Tables 1.1/1.2/1.5 (HVCTS), 1.3 (eVED), 1.1/1.3/1.4/1.5 (non-labour)) and the
'Autumn Budget 2025' sheet of the ratings workbook (openpyxl); `stage_obr.py` builds the rows and adds the
hand-transcribed text claims and parameter tables. Every value is verbatim; nothing derived.

## Access recipe (all direct, browser User-Agent, `curl -sSL`; no Cloudflare challenge on 2026-09-24)

- EFO PDF https://obr.uk/docs/dlm_uploads/OBR_Economic_and_fiscal_outlook_November_2025.pdf (200, 1,703,111
  bytes, sha256 0b9265e18907c54e0144911b13b0af894a0f993b649e8bbdd976362159dc4b5e), 207 pages. Printed page = PDF
  page - 9 in chapter 3; locators cite printed pages: Table 3.1 p.58, paras 3.9-3.10 p.59, Box 3.1 pp.61-62,
  paras 3.13-3.17 pp.62-64, para 3.18 pp.64-65, Box 3.2 pp.65-66, paras 3.19-3.22 pp.66-67, paras 3.29-3.30 p.69,
  Table 3.3 p.70, Box 3.3 pp.70-72 (Table A p.71), Table 3.4 p.73, Table 3.5 p.74, Table 3.6 p.75, Table 3.7 p.76,
  Table 3.8 p.77, Table 3.9 p.78, Table 3.10 p.81, para 3.73 p.85, paras 3.79-3.81 pp.86-87.
- Supplementary forecast information (2 Apr 2026), via the `/download/` slugs with `-L` (302 to `/docs/dlm_uploads/`):
  HVCTS ...Supplementary-forecast-information-high-value-council-tax-surcharge-costing.pdf (126,847 bytes);
  eVED ...Supplementary-forecast-information-eVED-costing-1.pdf (153,939 bytes; the file was updated on 3 Sep 2026
  to add the new-sales row to Table 1.2 — the hash is of the updated file); non-labour income
  ...Supplementary-forecast-information-non-labour-components-of-incomes-tax-costing.pdf (129,389 bytes). 7 pages each.
- Uncertainty ratings database: https://obr.uk/download/policy-costings-uncertainty-ratings-database-march-2025/
  resolves to https://obr.uk/docs/dlm_uploads/Uncertainty_ratings_database_March_2026.xlsx (316,614 bytes); a
  "november-2025" slug returns 404. Sheet 'Autumn Budget 2025', rows 8-95 (88 Table 4.1 lines) and 97-103 (7
  fiscally neutral measures). Manifest date 2026-03-03 is the Spring Forecast 2026 day inferred from the file
  title "March 2026" (no upload date is shown) — the only inferred date in this family.
- The OBR Policy measures database (seed bullet "Tax-head split") was NOT fetched or staged: PR #56 owns it.

## Sign conventions (recorded per row, verbatim where printed)

- Table 3.1 and Table 3.10: "Note (verbatim): A positive sign implies an increase in borrowing."
- Tables 3.2-3.9 print no note; rows carry: "positive = increase in borrowing (no note printed on this table;
  chapter convention per the Table 3.1 note ... and the Box 3.3 Table A note 'Here we present higher taxes as
  positive numbers, in contrast to the tables elsewhere in this chapter')". Table 3.2 adds "(this table: positive =
  higher UC spending)".
- Box 3.3 Table A: "Note (verbatim): Here we present higher taxes as positive numbers, in contrast to the tables
  elsewhere in this chapter."
- HVCTS Table 1.5 and non-labour Tables 1.3/1.4/1.5: "Note (verbatim): This table uses the convention that a
  negative figure means a reduction in PSNB."; non-labour Table 1.1 static yields: "Note (verbatim): The static
  yield values in this table use the convention that a negative figure means a reduction in PSNB."
- eVED Table 1.3 prints no note and shows the yield positive (1.3 / 1.6 / 2.1); rows carry "positive = revenue
  yield (... inferred from para 1.19 'central revenue yield of £1.1 billion in 2028-29' matching the +1.1
  post-behavioural cell)" with `parse_confidence: medium`.
- Text claims carry the wording: "as worded (positive = cost / increase in borrowing)", "as worded (positive =
  yield / reduction in borrowing)", "as worded: 'reduce CPI inflation by' (positive = reduction ...)", etc.
  Values are never re-signed.

## What is staged (927 rows)

- Table 3.1 (168): all 28 lines x 6 FYs, `metric: revenue_change` (spending lines flagged
  `aggregation_level: package_total` / `measure_or_group`). measure_key on the single-measure lines (salary
  sacrifice, WDA, eVED, gambling, EOT, HVCTS, fuel duty) and `ab2025__package_total_policy_decisions` on the memo
  line "direct effect of decisions on HM Treasury's ... table 4.1" (sign reversed relative to HMT's total);
  null with a note on the grouped lines ("Freezes to personal tax thresholds" = two registry measures;
  "Increases to income tax rates on property, savings and dividends" = three).
- Table 3.2 (25): post-behavioural / static / take-up response (`revenue_change`, Great Britain basis, DWP PSM),
  "Number of families gaining (thousand)" (`metric: gainer_count`, unit families, x1e3) and "Average annual change
  in award for gaining families (£)" (`metric: average_annual_gain`, unit gbp, per gaining family).
- Table 3.3 (35) incl. the two memo lines (`scoring_method: memo`); Table 3.4 (35); Table 3.5 (45, component rows
  keyed to the dividend / savings / property measures, total rows null); Tables 3.6-3.9 (15 each).
- Box 3.3 Table A (57): existing changes (baseline = proposed with-indexation counterfactual, `measure_key: null`),
  November 2025 measures (income tax and employee NICs -> thresholds key; employer NICs -> secondary-threshold
  key; total null), Total. Box 3.3 text (19): £4,900 / £20,100 (`proposed_metric: counterfactual_threshold_gap`),
  £56bn / £12bn, ~£11bn / £0.9bn, -£0.4bn, £67bn / 1.8% of GDP / £13bn, £3.3bn vs March 2025, 5.2m / 4.8m /
  600,000 (`metric: taxpayer_count_change`, cumulative 2022-23 to 2030-31), 780,000 / 920,000 / 4,000 vs March 2025
  (`parse_confidence: medium`: "largely" attributable to the extensions), 15% -> 24%
  (`proposed_metric: taxpayer_share_higher_or_additional_rate`).
- Table 3.10 (65): 13 measures x 5 FYs, £m, with `conditions.uncertainty_rating` and `table_41_head`.
- Uncertainty ratings sheet (95): one row per measure, `proposed_metric: costing_uncertainty_rating`,
  `value_kind: categorical`, `value: 0` (null not allowed), `value_raw` = the Final rating text, the Data /
  Behavioural / Modelling / most-important sub-ratings in `conditions`, `period 2025`, `time_basis: point_in_time`.
  measure_key by Table 4.1 line via the registry (88 lines -> keys; 7 fiscally neutral rows null). 13 rows are
  "N/A" (DEL-only measures, not rated) and are staged so the sheet is complete; the ingest can drop them.
- Supplementary notes: HVCTS Tables 1.1 and 1.2 (30, `tax_base`, `proposed_unit: properties`, England, static vs
  post-behaviour), Table 1.3 key parameters (14, `behavioural_parameter`; band charges are policy design and are
  not staged), Table 1.5 costing (30), text percentages (11) and the 'high' rating (1); eVED Table 1.1 parameters
  (11; 8,450 / 5,870 miles as `tax_base`), Table 1.2 sales and stock (10, `tax_base`, `proposed_unit: cars`),
  Table 1.3 costing (15), text (14: 4.3% / 2.2%, 4% cap, 120,000 / 2.2%, 220,000, £150m / 7.1%, 3.2% / 1.6%, £60m /
  3.0%, £30m / 1.4%, £0.2bn / 12%, £7bn 2050-51) and the 'high' rating (1); non-labour Table 1.1 (30: tax bases and
  static yields), Tables 1.3 / 1.4 / 1.5 (35 + 15 + 35), text (11: one-third, 90% / 10%, 20%, 28% and the 14-45%
  range, 0.2ppt rents (`rent_level_effect`), -0.1ppt house prices (`house_price_level_effect`), 5%, 3.0%) and three
  ratings (dividends high, savings medium, property high).
- EFO text (59 = 54 paragraph rows + 5 Box 3.2 rows): paras 3.9-3.10 (`metric: decisions_effect_on_borrowing`, £ and % of GDP), 3.14 (potential output,
  range_high), 3.15 (real GDP), 3.17 (CPI x4), 3.18 (£6.9bn; WFP £1.6bn / £1.7bn, four-fifths eligible
  (`eligibility_rate`), £0.5bn recovered; PIP £3.9bn; UCHE £520m), Box 3.2 (AHE x3, 20,000-40,000), 3.19-3.20
  (£2.3bn / £3.0bn, £300m + 25,000 families, 450,000 restated), footnote 9 (£600m), 3.21 (£2.3bn average), 3.22
  (£0.4bn a year, £5.6bn), 3.30 (£8.3bn, £7.6bn, £0.2bn), 3.32 (76%, 50%), 3.33 (£2.1bn, £1.2bn, £0.3bn, £0.5bn,
  £0.1bn, £0.5bn), 3.36-3.38 (£255 worked example, 8,500 miles, 440,000 / 320,000, ECS £0.5bn, grant £0.3bn),
  3.40 (90%, £0.5bn, £0.1bn), 3.41 (£0.9bn), 3.45 (£2.4bn, £0.9bn), 3.73 (£120bn cumulative, proposed RPI
  baseline), 3.81 (£7bn, 0.15% of GDP, 2050-51).

## Coverage tally (seed "Office for Budget Responsibility" bullets)

Staged: Table 3.1 total package and personal-tax lines; Table 3.2 + paras 3.19-3.20; Table 3.3 + paras
3.29-3.30; Box 3.3 Table A, Chart B numbers and text; Table 3.4 + paras 3.31-3.32 (the parameters; the £4.7bn /
£2.6bn / £0.7bn / £1.6bn text figures duplicate table cells and are not re-staged as text); Table 3.5 + para 3.33;
non-labour supplementary note; Table 3.7 + paras 3.36-3.38; eVED supplementary note (incl. the 3 Sep 2026 update);
Table 3.8 + paras 3.39-3.40; Table 3.9 + paras 3.42-3.44; HVCTS supplementary note; fuel duty paras 3.45 and 3.73;
summer welfare reversals para 3.18 and the Table 3.1 lines; Box 3.2; student loans para 3.22; RO para 3.21;
economy effects paras 3.13-3.17 (the indirect effects £2.0bn / £5.2bn are the Table 3.1 "Indirect effects" line);
Table 3.10; uncertainty ratings sheet. Also staged although not in the seed: Table 3.6 (writing down allowances,
an AB2025 measure inside the 3.2-3.10 range) and the remaining Table 3.1 lines.

Not staged, with reasons:
- Para 3.79 (long-run rent effect of the property rate rise): qualitative, no number.
- OBR Policy measures database tax-head split: owned by PR #56.
- Duplicated text figures that equal a staged table cell (3.31 £4.7bn / £2.6bn; 3.37 £1.1bn / £1.9bn / £0.2bn;
  3.39 £1.1bn; 3.42 £0.4bn; 3.20 560,000 / £5,310; supplementary forestalling ±£0.3bn, -£0.2bn, +£0.3bn, -£0.1bn):
  the table cells are the staged rows.
- Policy design parameters (£0.03 / £0.015 per mile; HVCTS band charges £2,500-£7,500; 25% / 100% of the RO
  cost on bills from 2029-30; £2,370 ECS total for a car bought in 2025-26; "16 consecutive years"): kept in
  `reform_hint` / `note`, not values.
- OBR determinant tables (HVCTS Table 1.4 CPI and house price index; eVED Table 1.2 CPI, consumption, Bank rate;
  non-labour Table 1.2 growth determinants): forecast determinants, not scores or measure parameters.
- Non-numeric behavioural statements ("around one-third" for gambling and HVCTS, "around 90 per cent of cars
  fully electric" as an assumption): in `note` / `conditions.assumption`.
- Paras 3.46-3.48 (business rates £1.2bn average, Sizewell C, compliance £2.3bn): not in the seed; left for a
  later pass (chapter 3 text beyond the household measures).

## Distinct condition values

- geography: UK | England (HVCTS supplementary property counts, parameters) | Great Britain (Table 3.2, para 3.19
  rows, UCHE) | England and Wales (WFP / PIP para 3.18 rows)
- fy: 2021-22 | 2022-23 | 2023-24 | 2024-25 | 2025-26 | 2026-27 | 2027-28 | 2028-29 | 2029-30 | 2030-31 | 2050-51
  (ratings rows: period 2025, point_in_time; CPI peak: period 2026, point_in_time)
- basis: forecast | outturn (2021-22 share only)
- scoring_method: static | behavioural_effect | post_behavioural | final | memo (absent on ratings, counts and
  some text rows)
- sign_convention: 37 distinct strings — the four verbatim table notes, the chapter convention string, the eVED
  inferred string, and per-row "as worded: ..." strings for text claims
- component: 58 distinct (table sub-lines such as Pass-through, Other behaviours, Employers switching to
  ordinary contributions, Employees switching to RAS schemes, Dividends / Savings / Property, Forestalling,
  Reduction in taxable income, Tax-motivated incorporations, Rental and property prices, Evasion and
  non-compliance, Block grant adjustment, Price capitalisation, bunching, and supply impacts, Compliance, appeals
  and support scheme adjustments, Other tax heads impact; and text components)
- parameter: 57 distinct verbatim parameter descriptions (behavioural_parameter rows)
- table_row: 90 distinct printed labels; block: existing | nov2025 | total (Box 3.3 Table A)
- aggregation: average per year over the five years of the forecast | average over the next two years (2026-27
  and 2027-28) | average over the last two years of the forecast (2029-30 and 2030-31) | average per year from
  2027-28 (onwards) | average per year from 2028-29 | average per year over 2026-27, 2027-28 and 2028-29 | average
  per year 2025-26 to 2029-30 | average per year 2027-28 to 2030-31 | per year in the medium term | peak effect
- horizon: 2026-27 to 2030-31 | by 2029-30 | between 2022-23 and 2030-31 (cumulative) | 2010-11 to 2026-27
  (cumulative); comparison: vs March 2025 forecast (...) | with-inflation indexation minus frozen level |
  relative to the level had the two-child limit remained in place | relative to the stated policy of RPI uprating ...
- impact_channel: spending_measure | tax_measure; block_grant_adjustment: included (footnote 7) | excluded
  (footnote 7); measure_scope: England; table_41_head: Tax | Spend; uncertainty_rating: High | Very High | Very high
- ratings rows: data_uncertainty / behavioural_uncertainty / modelling_uncertainty in {Low, Medium-Low, Medium,
  Medium-High, High, Very high, N/A} (sheet spellings) plus lower-case text spellings from the supplementary
  notes; most_important_source: Behaviour | Data | Modelling | N/A; rating_axis: final; sheet_section: "Measures
  on Treasury's policy decisions table" | "Fiscally neutral measures²"; table_41_line: 1-88 | "not on Table 4.1
  (fiscally neutral measures)"; as_of: 2025-11-26 (...)
- policy_vintage: Spring Statement 2025 UC measures as amended in July 2025 | Spring Statement 2025 employment
  support programme; applied_to_forecast: no (...); price_basis: today's prices | real 2025 £; price_band_gbp_m:
  2.0 to 2.5 | 2.5 to 3.5 | 3.5 to 5.0 | Over 5 | Total estimated properties in scope; car_age: 0 | 15;
  share_of_static_yield: 7.1 | 3.0 | 1.4 | 12 per cent; subgroup: pensioners | average driver of a battery
  electric car driving 8,500 miles | taxpayers at either the higher or additional rate; per: gaining family;
  period_detail: second quarter of 2026 (peak); poverty_line: unstated (Government estimate); assumption (2).

## Proposals used

- proposed_metric: `costing_uncertainty_rating` (100), `tax_base` (58), `behavioural_parameter` (55),
  `household_tax_change` (1: the £255 worked example), `affected_count` (1: 25,000 additional claiming families),
  and four new spellings: `counterfactual_threshold_gap` (2: £4,900 / £20,100), `taxpayer_share_higher_or_additional_rate`
  (2: 15% / 24%), `rent_level_effect` (1: +0.2ppt), `house_price_level_effect` (1: -0.1ppt a year).
- proposed_unit: `rating_category` (100), `properties` (30), `cars` (14), `percent_of_gdp` (5 — the registered
  units are percent_of_real_gdp / percent_of_potential_gdp; these figures are shares of nominal GDP),
  `elasticity` (4), `miles_per_car_per_year` (3), `average_hours_equivalent` (3), `transactions_per_year` (2),
  `years` (1).
- baseline_policy `obr_pre_measures_autumn_budget_2025__policy_parameters` on 773 rows; null on the 100 rating
  rows and on the Box 3.3 / long-run rows whose baseline is a counterfactual world, where `proposed_baseline`
  reads "thresholds uprated in line with inflation (Box 3.3: 'Had the PA and HRT instead moved in line with
  inflation'); yield of all freezes since 2022-23, not the AB2025 pre-measures world" (57 rows) or "fuel duty
  rates uprated in line with RPI inflation since 2010-11 (stated policy)" (1 row).

## Attribution

926 rows `own` (OBR-certified costings, OBR judgements, OBR-scrutinised HMRC/DWP components); 1 row `restated`:
the 450,000 children "The Government estimates" figure in para 3.20 (source_model
`dwp_policy_simulation_model`). source_model: `hmt_costing_obr_certified` (425, certified costing tables),
`hmrc_personal_tax_model` (251, HMRC-modelled personal-tax tables and parameters), `obr_efo_forecast` (215,
OBR's own economy/fiscal judgements and ratings), `dwp_policy_simulation_model` (36, welfare tables/text).
benchmark_class `different_model` throughout. measure_key: 89 registry keys; 223 rows null (Table 3.1 aggregates
and grouped lines, Box 3.3 existing/total rows, Table 3.5 totals, Box 3.2 and para 3.14 package effects, fiscally
neutral ratings, and the "Increases to income tax rates on property, savings and dividends" / "Freezes to personal
tax thresholds" grouped lines, each noting the registry keys it sums).

## Discrepancies between primaries worth knowing (not errors in the seed)

- HVCTS bunching elasticities: HMT costings p.52 print "1.0 to 1.5"; the OBR supplementary note Table 1.3 prints
  "1.0 to 1.25". Both are staged in their own family with a cross-reference note.
- eVED mileage: HMT costings p.69 use 8,000 miles a year on average across electric and plug-in hybrid cars; EFO
  para 3.36 uses 8,500 miles for the average battery electric driver; the supplementary note models 8,450 (car
  age 0) to 5,870 (age 15). All staged as `tax_base` rows with notes.
- Personal tax thresholds: the EFO Table 3.3 post-behavioural line (-3.3 / -7.6 / -12.1) exceeds the HMT
  post-behavioural costing (+3,365 / +7,780 / +12,435 £m) because of the pass-through error found after the
  forecast closed (HMT footnote 1 p.41; OBR Table 3.3 note and memo lines, both staged).
