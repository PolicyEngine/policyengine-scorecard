# Demos — Autumn Budget 2025 harvest (source `demos`)

Staged 2026-09-24 from the primary documents. **15 claims** in `claims_staged.jsonl.gz`, **1 documents** in `manifest.jsonl`. Row contract, enums and rules: `../README.md`; measure keys: `../REGISTRY_KEYS.md`. Every `value` is verbatim (normalised to the unit as recorded in `normalization`); nothing is derived.

## Access recipe

"Solving the Tax Puzzle" (Dan Goss, 96 pages) fetched directly (`curl`, HTTP 200; PDF CreationDate 2025-09-25, cover
"September 2025"); pypdf text. `source_model: arithmetic` (Demos's own static arithmetic for the two property
proposals and the package aggregation; the other components are CenTax/IPPR estimates restated).

### Documents (manifest.jsonl)

- 2025-09-25 · Solving the Tax Puzzle (Dan Goss, September 2025) · `pdf` · access `direct` · 6,438,635 bytes · sha256 `f5718c04f54dbdb8…` · **15 rows** — date = PDF CreationDate (25 Sep 2025); cover says September 2025  
  <https://demos.co.uk/wp-content/uploads/2025/09/Solving-the-tax-puzzle_report_2025_Sept.pdf>

## Coverage tally (seed bullets → claims staged → not staged)

Seed: `scores-3-other-shops.md` § Demos (10 bullets incl. polling).

Staged (15 rows):
- Package £21.3bn (own upper-bound aggregation), £5.1bn NICs on income from wealth, £1.7bn properties → 3.
- Proposal 1 NICs on rental income: £3.2bn 2026/27, £3.6bn 2029/30, 47% from the top 10%, 5% from the bottom half →
  4 rows, **restated (CenTax)**. INVENTORY CORRECTION: the seed listed the £3.2bn as Demos's own static estimate; p.10
  ("The revenue figures for NICs on rental income, for partnership contributions, and for CGT are based on previously
  published estimtes made by the expert team at CenTax") and p.36 ("Source: CenTax analysis") attribute it to CenTax.
- Proposal 2 partnership contributions £1.9bn → 1 (restated CenTax; note the p.13 "static" vs p.46 "dynamic" label
  inconsistency — CenTax's £1.9bn is post-behavioural).
- Proposals 3–5 CGT: £11.2bn static 2019/20; £11.3bn dynamic 2026/27; exit tax £3.8bn; death uplift £0.7bn → 4
  (restated CenTax 2024).
- Proposal 6 proportional property tax £1.5bn; Proposal 7 council tax premium "over £200 million" → 2 (own).
- Proposal 8 gambling £3.2bn → 1 (restated IPPR).

Not staged (with reason):
- Opinium polling (net support +48pp / +42pp / 65% vs 9% / 46% vs 19%) — public-attitude statistics, not scorecard
  claims.
- "gambling's fiscal costs £1.4–7.2bn/yr" — cited estimate (footnote 7), context only.
- Restated fiscal-gap figures (£6.6bn / £16bn / >£20bn, Sky/IFS-derived).
- No modelling of the announced measures and no distributional analysis of the package.

### Row counts

- by `source`: demos 15
- by `attribution`: own 5, restated 10
- by `benchmark_class`: different_model 15
- by `source_model`: arithmetic 15
- by `value_kind`: point 13, range_high 1, range_low 1
- by `parse_confidence`: high 15
- by `measure_key`:
  - `ab2025_option__nics_on_rental_income` 4
  - `null` 3
  - `ab2025_option__cgt_equalise_with_income_tax_plus_investment_allowance` 2
  - `ab2025_option__cgt_end_uplift_on_death` 1
  - `ab2025_option__cgt_exit_tax_on_emigration` 1
  - `ab2025_option__gambling_duties_consolidated_or_raised` 1
  - `ab2025_option__nics_on_partnership_income` 1
  - `ab2025_option__proportional_property_tax_on_values_over_2m` 1
  - `ab2025_option__second_homes_200pct_premium_for_non_uk_residents` 1

## Metrics, units and baselines used

- `revenue_change` (registered) throughout; `conditions.basis` static / post_behavioural as labelled by Demos;
  `conditions.originator` names CenTax/IPPR on restated rows. Producer definition (p.29): "Based on static estimates,
  this package would collectively raise around £21.3 billion in 2026/27. This includes £5.1 billion from NICs on
  income from wealth, £11.3 billion from CGT (including the new exit tax), £1.7 billion on properties (£1.5 billion
  from the new property tax and £0.2 billion from council tax) and £3.2 billion from gambling duties." Footnote 14:
  "This should be considered an upper bound, as behavioural responses will reduce revenues."
- `proposed_metric: revenue_share` (`share`) for the 47% / 5% incidence of rental NICs.
- `period`: 2026-27 for the package and static 2026/27 rows; 2019-20 for the CenTax static 2019/20 CGT rows; 2029-30
  for the £3.6bn.
- `measure_key`: `ab2025_option__nics_on_rental_income`; `ab2025_option__nics_on_partnership_income`;
  `ab2025_option__cgt_equalise_with_income_tax_plus_investment_allowance`; `ab2025_option__cgt_exit_tax_on_emigration`;
  `ab2025_option__cgt_end_uplift_on_death`; `ab2025_option__proportional_property_tax_on_values_over_2m`;
  `ab2025_option__second_homes_200pct_premium_for_non_uk_residents`; `ab2025_option__gambling_duties_consolidated_or_raised`;
  package aggregates `null` + `reform_hint`.
- Baselines: all `baseline_policy: null`.

### As staged

- registered `metric`: `revenue_change` 13
- `proposed_metric`: `revenue_share` 2
- registered `unit_concept`: `gbp` 13, `share` 2
- `proposed_unit`: none
- `baseline_policy`: None 15 (null = current law at the scoring date)
- `proposed_baseline`: none

## Distinct values per `conditions` axis

- `basis` (2 distinct): static (13); post_behavioural (2)
- `component` (2 distinct): NICs on income from wealth (rental income £3.2bn + partnership contributions £1.9bn) (1); properties (proportional property tax £1.5bn + council tax premium £0.2bn) (1)
- `fiscal_event` (1 distinct): autumn_budget_2025 (15)
- `fy` (3 distinct): 2026-27 (11); 2019-20 (3); 2029-30 (1)
- `geography` (1 distinct): UK (15)
- `income_group` (2 distinct): bottom_50pct (1); decile_10 (1)
- `measure_type` (1 distinct): upper bound ('behavioural responses will reduce revenues'); CGT and partnership components are dynamic (1)
- `originator` (3 distinct): CenTax (previously published estimates; p.10: 'The revenue figures for NICs on rental income, for partnership contributions, and for CGT are based on previously published estimtes made by the expert team at CenTax') (5); CenTax: Advani, Lonsdale and Summers (2024), Reforming Capital Gains Tax (4); IPPR (p.10: 'The figure for raising gambling duties is based on estimates from the Institute for Public Policy Research (IPPR)') (1)
- `scenario` (2 distinct): with equalised CGT rates and an investment allowance (2); with exit tax and removal of the death uplift (1)
- `sign_convention` (1 distinct): positive = yield to the Exchequer (13)

## Attribution decisions

- `own` / `different_model`: £21.3bn, £5.1bn, £1.7bn (Demos aggregation), £1.5bn property tax, >£200m council tax
  premium (Demos analysis per p.10).
- `restated`: rental NICs (CenTax), partnership contributions (CenTax), CGT trio (CenTax 2024), gambling (IPPR) — 10
  rows, each with `conditions.originator` naming the originator; dropped at ingest (#86).
