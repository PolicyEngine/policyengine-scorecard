# Public First — Autumn Budget 2025 harvest (source `public_first`)

Staged 2026-09-24 from the primary documents. **12 claims** in `claims_staged.jsonl.gz`, **1 documents** in `manifest.jsonl`. Row contract, enums and rules: `../README.md`; measure keys: `../REGISTRY_KEYS.md`. Every `value` is verbatim (normalised to the unit as recorded in `normalization`); nothing is derived.

## Access recipe

Single blog post (Scott Corfe, dated 18/11/2025 on the page) fetched directly (`curl`, HTTP 200); BeautifulSoup text.
`source_model: survey_microdata` (Family Resources Survey 2023-24 secondary analysis: "a sample of close to 12,000
households across England, including about 500 band G and H residents").

### Documents (manifest.jsonl)

- 2025-11-18 · A Band G and H Council Tax raid could be the next “Granny Tax” · `html` · access `direct` · 33,941 bytes · sha256 `65d5a29e08ea1a74…` · **12 rows** — dated 18/11/2025 on the page; author Scott Corfe  
  <https://www.publicfirst.co.uk/a-band-g-and-h-council-tax-raid-could-be-the-next-granny-tax>

## Coverage tally (seed bullets → claims staged → not staged)

Seed: `scores-3-other-shops.md` § Public First (2 bullets).

Staged (12 rows):
- "over £4.2 billion per annum by the end of the decade, according to the IFS" → 1 row, **restated (IFS)**.
  INVENTORY CORRECTION: the seed attributed the £4.2bn to Public First's own FRS analysis; the page attributes it to
  the IFS.
- FRS tabulations (administrative_fact): G/H = about 4% of properties; 41% pensioner households vs <30% England-wide;
  median AHC income £62,400 vs £32,500; roughly a quarter in the bottom half; median council tax £3,500 (2023-24);
  council tax 5.1% of disposable income; 6.4% pay over 10% → 9 rows.
- Doubling scenario: 18% (~160,000 households) would pay 10%+ of disposable income → 2 rows (`different_model`).

Not staged: the "asset rich but cash poor" framing and political-risk discussion (no values); no modelling of the
enacted HVCTS by Public First.

### Row counts

- by `source`: public_first 12
- by `attribution`: own 11, restated 1
- by `benchmark_class`: administrative_fact 9, different_model 3
- by `source_model`: survey_microdata 12
- by `value_kind`: point 10, range_high 1, range_low 1
- by `parse_confidence`: high 12
- by `measure_key`:
  - `ab2025_option__council_tax_double_bands_g_and_h_england` 6
  - `null` 6

## Metrics, units and baselines used

- `revenue_change` for the restated £4.2bn (`value_kind: range_low`, "over £4.2 billion").
- `proposed_metric: affected_share` (`share`; `conditions.denominator` names the base — all properties in England,
  band G/H households, all households in England) and `affected_count` (`households`) for the 160,000.
- `income_statistic` (registered; `gbp`; `conditions.statistic: median`, `income_concept: household income after
  housing costs`) for £62,400 / £32,500. Producer definition: "the median household income (after housing costs) for
  band G and H residents is £62,400 per year. This is close to double the England-wide median of £32,500."
- `average_tax_amount` (registered; `statistic: median`, `tax: council tax`) for £3,500; `average_tax_rate`
  (registered; `percent`) for 5.1% ("As a share of disposable income, Council Tax for bands G and H stands at 5.1%").
- `period`: FRS levels 2023-24 (`period: 2024`); the restated IFS yield "by the end of the decade" → 2029-30.
- `measure_key`: `ab2025_option__council_tax_double_bands_g_and_h_england` on the option rows; levels `null`.
- Baselines: all `baseline_policy: null`.

### As staged

- registered `metric`: `average_tax_amount` 1, `average_tax_rate` 1, `income_statistic` 2, `revenue_change` 1
- `proposed_metric`: `affected_count` 1, `affected_share` 6
- registered `unit_concept`: `gbp` 4, `households` 1, `percent` 1, `share` 6
- `proposed_unit`: none
- `baseline_policy`: None 12 (null = current law at the scoring date)
- `proposed_baseline`: none

## Distinct values per `conditions` axis

- `basis` (1 distinct): static (3)
- `council_tax_band` (1 distinct): G and H (9)
- `data` (1 distinct): Family Resources Survey 2023-24 (close to 12,000 households in England, about 500 in bands G and H) (11)
- `denominator` (3 distinct): households in Council Tax bands G and H (4); all households in England (1); all properties in England (1)
- `fiscal_event` (1 distinct): autumn_budget_2025 (12)
- `fy` (2 distinct): 2023-24 (11); 2029-30 (1)
- `geography` (1 distinct): England (12)
- `horizon` (1 distinct): by the end of the decade (1)
- `housing_costs` (1 distinct): ahc (2)
- `income_concept` (2 distinct): household income after housing costs (2); disposable income (1)
- `originator` (1 distinct): IFS (1)
- `scenario` (2 distinct): bills doubled (2); current bills (1)
- `sign_convention` (1 distinct): positive = yield to the Exchequer (1)
- `statistic` (2 distinct): median (3); not stated (share of disposable income) (1)
- `subgroup` (5 distinct): council tax at 10% or more of disposable income (2); pensioner households (2); all households (1); council tax over 10% of disposable income (1); in the bottom half of the AHC national income distribution (1)
- `tax` (1 distinct): council tax (2)

## Attribution decisions

- `own` / `administrative_fact` for the FRS tabulations (levels and shares of the current population).
- `own` / `different_model` for the doubling-scenario shares/count (18%, ~160,000).
- `restated` for the IFS £4.2bn.
