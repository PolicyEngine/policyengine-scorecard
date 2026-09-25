# Cebr — Autumn Budget 2025 harvest (source `cebr`)

Staged 2026-09-24 from the primary documents. **12 claims** in `claims_staged.jsonl.gz`, **2 documents** in `manifest.jsonl`. Row contract, enums and rules: `../README.md`; measure keys: `../REGISTRY_KEYS.md`. Every `value` is verbatim (normalised to the unit as recorded in `normalization`); nothing is derived.

## Access recipe

Briefing-note PDF (CreationDate 2025-11-26 17:16 GMT) and the reaction blog (`article:published_time` 2025-11-26 17:38
GMT) fetched directly (`curl`, browser User-Agent, HTTP 200); pypdf/BeautifulSoup text. `source_model: cebr_forecast`
(Cebr's own macro forecast applied to the frozen thresholds); the Asda Income Tracker rows use `arithmetic`.

### Documents (manifest.jsonl)

- 2025-11-26 · Cebr’s Reaction: The Autumn Budget 2025 · `html` · access `direct` · 58,728 bytes · sha256 `aba3825ab80fd19a…` · **1 rows** — article:published_time 2025-11-26T17:38 GMT  
  <https://cebr.com/blogs/cebrs-reaction-the-autumn-budget-2025/>
- 2025-11-26 · Cebr's Immediate Reaction: Autumn Budget Briefing, November 2025 · `pdf` · access `direct` · 325,459 bytes · sha256 `1bc5d08ff91e86d9…` · **11 rows** — PDF CreationDate 2025-11-26 17:16 GMT  
  <https://cebr.com/wp-content/uploads/2025/11/Cebr-Briefing-Note-Autumn-Budget-2025.pdf>

## Coverage tally (seed bullets → claims staged → not staged)

Seed: `scores-3-other-shops.md` § Cebr (3 bullets) and `scores-4-commercial.md` § Cebr (duplicate; staged here only).

Staged (12 rows):
- Threshold freeze yield "£4.9 billion in 2028/29, £10.5 billion in 2029/30, and £15.9 billion in 2030/31" → 3 rows;
  blog "£15.9 billion by 2031" → 1 row.
- Real value of thresholds eroded "by around 30% by the end of the new commitment period, relative to their initial
  freeze date" → 1 row (`proposed_metric: threshold_real_value_change`).
- Wage floors: real-terms pay rises 1.6% / 5.9% / 3.4% for NLW, NMW 18-20, NMW 16-17/apprentices → 3 rows
  (`real_income_growth`, `measure_key: null`, NLW rates in `reform_hint`); minimum wage 62.1% of the median
  (`minimum_wage_bite`) and the OECD average 52.2% (restated) → 2 rows.
- Asda Income Tracker discretionary income −£49 / −£45 per week for the lowest and second-lowest quintiles → 2 rows
  (context, `proposed_metric: discretionary_income_change`).

Not staged (with reason):
- Figure 1 (real personal allowance, 2021/22 prices) and Figure 2 (real wage floors) — chart-only.
- Restated: £26bn package; OBR 2025 growth 1.5%; salary sacrifice cap £60,000 → £2,000, OBR £4.7bn 2029/30 and
  £2.6bn 2030/31; 15 million under-savers; cash ISA £12,000; RGD 21% → 40% and GBD 25% from April 2027; productivity
  0.6% vs 2.1% pre-2008 (Cebr's growth-accounting statement, context only).
- No distributional, decile or household analysis by Cebr.

### Row counts

- by `source`: cebr 12
- by `attribution`: own 11, restated 1
- by `benchmark_class`: different_model 12
- by `source_model`: arithmetic 2, cebr_forecast 10
- by `value_kind`: point 12
- by `parse_confidence`: high 10, medium 2
- by `measure_key`:
  - `null` 7
  - `ab2025__personal_tax_thresholds_freeze_to_2031` 5

## Metrics, units and baselines used

- `revenue_change` (registered) with `conditions.basis: forecast` and `conditions.method` quoting the mechanism
  ("Cebr's own earnings-growth and CPI forecasts applied to the frozen thresholds"). Producer definition (p.3):
  "Cebr estimates that the freeze will raise an additional £4.9 billion in 2028/29, £10.5 billion in 2029/30, and
  £15.9 billion in 2030/31. These projections exceed the OBR’s forecasts, reflecting our expectation of stronger
  consumer price growth and, in turn, higher wage growth."
- `proposed_metric: threshold_real_value_change` (`percent`, value −30; horizon April 2021 to 2030/31).
- `real_income_growth` (registered, `percent`) for the wage-floor real pay rises; `minimum_wage_bite` (registered,
  `percent`) for 62.1% / 52.2%.
- `proposed_metric: discretionary_income_change` (`gbp_per_week`; `income_group` quintile_1 / quintile_2; horizon
  "from the pre-cost-of-living-crisis peak"; `parse_confidence: medium` because the peak date is not printed).
- `measure_key`: freeze rows `ab2025__personal_tax_thresholds_freeze_to_2031`; wage-floor and tracker rows `null`.
- Baselines: all `baseline_policy: null`.

### As staged

- registered `metric`: `minimum_wage_bite` 2, `real_income_growth` 3, `revenue_change` 4
- `proposed_metric`: `discretionary_income_change` 2, `threshold_real_value_change` 1
- registered `unit_concept`: `gbp` 4, `gbp_per_week` 2, `percent` 6
- `proposed_unit`: none
- `baseline_policy`: None 12 (null = current law at the scoring date)
- `proposed_baseline`: none

## Distinct values per `conditions` axis

- `basis` (1 distinct): forecast (8)
- `data` (1 distinct): Asda Income Tracker (Cebr) (2)
- `fiscal_event` (1 distinct): autumn_budget_2025 (12)
- `fy` (4 distinct): 2026-27 (3); 2030-31 (3); 2028-29 (1); 2029-30 (1)
- `geography` (2 distinct): UK (11); OECD average (1)
- `horizon` (2 distinct): from the pre-cost-of-living-crisis peak (2); April 2021 (initial freeze) to the end of the new commitment period (2030/31) (1)
- `income_concept` (1 distinct): real-terms hourly pay at the wage floor (3)
- `income_group` (2 distinct): quintile_1 (1); quintile_2 (1)
- `method` (1 distinct): Cebr's own earnings-growth and CPI forecasts applied to the frozen thresholds ('stronger consumer price growth and, in turn, higher wage growth') (3)
- `originator` (1 distinct): OECD (1)
- `price_basis` (2 distinct): real (Cebr CPI forecast) (3); real (CPI) (1)
- `rate` (3 distinct): £10.85 (1); £12.71 (1); £8.00 (1)
- `sign_convention` (2 distinct): positive = yield to the Exchequer (4); positive = gain to households (2)
- `statistic` (1 distinct): minimum wage as a percentage of the median wage (2)
- `subgroup` (3 distinct): National Living Wage (21 and over) (1); National Minimum Wage (16-17 and apprentices) (1); National Minimum Wage (18-20) (1)

## Attribution decisions

- `own` / `different_model` for the freeze yields, the 30% erosion, the real pay rises, the 62.1% bite and the Asda
  tracker figures (Cebr's own work).
- `restated` only for the OECD average 52.2% (comparator).
