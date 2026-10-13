# NIESR — Autumn Budget 2025 harvest (source `niesr`)

Staged 2026-09-24 from the primary documents. **27 claims** in `claims_staged.jsonl.gz`, **8 documents** in `manifest.jsonl`. Row contract, enums and rules: `../README.md`; measure keys: `../REGISTRY_KEYS.md`. Every `value` is verbatim (normalised to the unit as recorded in `normalization`); nothing is derived.

## Access recipe

All eight NIESR pages/PDFs were fetched directly with `curl` and a browser User-Agent (HTTP 200, no blocks); text
extracted with pypdf (PDFs) and BeautifulSoup (HTML). NIESR blog pages carry `article:published_time` meta tags
(used for `date`); the two Outlook PDFs print no date, so `date` is the PDF CreationDate (2025-11-03 and 2026-02-02)
and the manifest note says so.

Only the **household/static** rows are staged here (HBAI quantile regression; arithmetic on OBR data). Every NiGEM
macro scenario, forecast and fiscal-impulse number is **deferred to `uk_macro_calls` (tranche 4)** — the source
documents are manifested so the tally is complete, with zero rows.

### Documents (manifest.jsonl)

- 2025-11-26 · 2025 Autumn Budget Reaction: A High-Tax, High-Debt Steady State · `html` · access `direct` · 143,424 bytes · sha256 `70a9ee6200c94923…` · **7 rows**  
  <https://niesr.ac.uk/blog/2025-autumn-budget-reaction>
- 2025-11-10 · The Distributional Impacts of Tax Rises · `html` · access `direct` · 166,560 bytes · sha256 `7364bd05b45a13e8…` · **1 rows**  
  <https://niesr.ac.uk/blog/distributional-impacts-tax-rises>
- 2025-11-24 · Four Key Questions Ahead of the Autumn Budget · `html` · access `direct` · 131,323 bytes · sha256 `fd1412c9d23dd69e…` · **1 rows**  
  <https://niesr.ac.uk/blog/four-key-questions-ahead-autumn-budget>
- 2025-10-20 · Tax Options for the Chancellor · `html` · access `direct` · 168,558 bytes · sha256 `21bfdba97b8ce6b1…` · **0 rows** — NiGEM macro scenarios only: deferred to uk_macro_calls (tranche 4); manifested, no rows  
  <https://niesr.ac.uk/blog/tax-options-chancellor>
- 2025-11-28 · What is the Stance of Fiscal Policy after Wednesday's Budget? · `html` · access `direct` · 108,460 bytes · sha256 `13d801406c1b12d9…` · **0 rows** — Fiscal Impact Measure (macro): deferred to uk_macro_calls (tranche 4); manifested, no rows  
  <https://niesr.ac.uk/blog/what-stance-fiscal-policy-after-wednesdays-budget>
- 2025-12-15 · Where Did the Fiscal Black Hole Go? · `html` · access `direct` · 173,137 bytes · sha256 `99d67583835d3738…` · **0 rows** — NiGEM-vs-OBR forecast decomposition: deferred to uk_macro_calls (tranche 4); manifested, no rows  
  <https://niesr.ac.uk/blog/where-did-fiscal-black-hole-go>
- 2025-11-03 · UK Economic Outlook, Autumn 2025: Stability First · `pdf` · access `direct` · 1,555,228 bytes · sha256 `391956de6fd8ec35…` · **18 rows** — date = PDF CreationDate (2025-11-03); the PDF prints no publication date; forecast completed 27 Oct 2025  
  <https://niesr.ac.uk/wp-content/uploads/2025/11/Economic-Outlook-Autumn-2025.pdf>
- 2026-02-02 · UK Economic Outlook, Winter 2026: Normality Under Strain · `pdf` · access `direct` · 2,807,212 bytes · sha256 `c9f35cd3095b28df…` · **0 rows** — date = PDF CreationDate; NiGEM forecast rows deferred to uk_macro_calls (tranche 4); manifested, no rows  
  <https://niesr.ac.uk/wp-content/uploads/2026/02/UK-Economic-Outlook-Winter-2026.pdf>

## Coverage tally (seed bullets → claims staged → not staged)

Seed: `SEED_INVENTORY/scores-3-other-shops.md` § NIESR (14 bullets + restated list).

Staged (27 rows):
- Box D Figure D4 (Autumn 2025 Outlook) and its restatement in "The Distributional Impacts of Tax Rises" (10 Nov):
  second-decile equivalised AHC income "about two per cent lower than the baseline in the long run" → 2 rows
  (`pct_change_after_tax_income`, source_model `hbai_quantile_regression`). Decile 1 and decile 9 paths are
  chart-only (Figure D4 has no data labels) → not staged.
- Budget-day reaction Figure 5 ("The freezing of income tax thresholds until 2030 will hit the bottom half of the
  income distribution hardest"): the values are printed in the text (decile 1 −2.5%, decile 2 "nearly 5 per cent",
  decile 3 3.75%, deciles 4–7 3.5%) → 7 rows with `value_kind: approx_chart_reading` as instructed and
  `source_model: unstated` (no source line under the chart, no "our model" statement; consistent with the HBAI
  quantile-regression approach). Deciles 8–10 are not printed → not staged.
- Box C Table C1 "Benchmarks for a prudent fiscal buffer" (8 methods × £bn and % of GDP) → 16 rows
  (`proposed_metric: fiscal_headroom`, source_model `arithmetic`; the debt-at-risk rows record the quantile-regression
  estimation in `conditions.estimation`), plus the "60th percentile" coverage of the £9.9bn buffer → 1 row, plus the
  24 Nov blog's "around £24 billion" restatement of the same Box C result → 1 row.

Deferred to `uk_macro_calls` (tranche 4) — NiGEM / macro, listed here with the printed figures:
- "Tax Options for the Chancellor" (20 Oct): £30bn via income tax (real GDP "lower by approximately 0.05 per cent"
  first year), VAT ("falls by 0.87 per cent in the first year"), corporation tax ("approximately 0.15 per cent").
- Autumn 2025 Outlook Box D Figures D1/D3 (GDP impacts of £50bn scenarios; chart-only) and Box C's pre-measures
  current budget deficit of £38.2bn in 2029-30 (NiGEM forecast).
- "Four Key Questions" (24 Nov): removing VAT on domestic energy "would reduce headline inflation by 0.17 percentage
  points in the first year"; 50bp of Bank Rate cuts in 2026; a 10bp gilt-yield rise raising debt interest by £3bn.
- Budget reaction (26 Nov): trend growth 1.25% vs OBR 1.5%; average GDP growth 1.0% since 2019; headroom £22bn = 0.6%
  of GDP (NIESR arithmetic on OBR figures); "£8bn short of NIESR's pre-Budget recommendation of £30bn".
- "What is the Stance of Fiscal Policy" (28 Nov): Fiscal Impact Measure, "fiscal drag of close to 0.4 percentage
  points on GDP growth" by 2027 (annual values chart-only).
- "Where Did the Fiscal Black Hole Go?" (15 Dec) and Winter 2026 Outlook Box C: £48bn predicted shortfall, ~£15bn
  employment/participation, £6.4bn real spending erosion, £2.5bn income composition, nominal GDP +£40bn, 330,000
  more in work, −38.2 → OBR +4.2 waterfall; Winter 2026 own headroom (current budget deficit £0.5bn in 2029-30,
  PSNFL headroom £33.1bn, PSNFL 83.7% of GDP 2027-28, PSND 99.1% 2028-29).

Restated (not staged; OBR/HMT/DWP figures repeated by NIESR): £22bn headroom; 59% probability; productivity −0.3pp
costing £16bn; £24.1bn tightening by 2030-31; ~600,000 families gaining ~£5,300 from two-child-limit removal; >£7bn
welfare reversals; energy measures −0.3pp CPI 2026; EV VED +0.1pp CPI 2028; gilt issuance £303.7bn; debt 83.7%→83.0%;
£9.9bn March headroom; DMO £309.1bn; the 10 Nov blog's "about £7 billion per year" fiscal drag (source not stated).

Not quantified by NIESR (nothing to stage): costings of individual Budget measures; two-child limit beyond government
figures; household worked examples; regional breakdowns.

### Row counts

- by `source`: niesr 27
- by `attribution`: own 27
- by `benchmark_class`: different_model 27
- by `source_model`: arithmetic 18, hbai_quantile_regression 2, unstated 7
- by `value_kind`: approx_chart_reading 7, point 20
- by `parse_confidence`: high 17, medium 10
- by `measure_key`:
  - `null` 18
  - `ab2025__personal_tax_thresholds_freeze_to_2031` 7
  - `ab2025_option__niesr_30bn_tax_rise_scenarios` 2

## Metrics, units and baselines used

- `pct_change_after_tax_income` (registered) for the decile income changes; the income concept rides in
  `conditions.income_concept` ("equivalised household disposable income, after housing costs (AHC)" for Box D;
  "real household disposable income" for Figure 5). Producer definition (Box D, p.37): "We focus on equivalised
  after housing cost (AHC) household incomes, which accounts for the variation in both household composition and
  housing expenses across households".
- `proposed_metric: fiscal_headroom` (already in the README's cross-family proposal list) with `unit_concept: gbp`
  and `proposed_unit: percent_of_gdp`. Producer definition (Box C, p.29): "The fiscal buffer is the margin between
  the OBR’s central forecast for meeting the fiscal rule and the point at which the rule would be breached."
- `proposed_metric: debt_outcome_percentile_covered` with `proposed_unit: percentile` for the single "60th
  percentile" row (Box C, p.31-32).
- Baselines: all rows `baseline_policy: null` (current law / NiGEM baseline as the producer's counterfactual); the
  Box D counterfactual is the NiGEM baseline "with no tax rises" (recorded in `conditions.measure_type`).
- `period`: Box D "long run" rows carry the calibration year 2029-30 (`period: 2030`) with `conditions.horizon:
  "long run"`; Figure 5 rows carry 2030-31 (`period: 2031`, horizon implied by "until 2030"/"to 2031").

### As staged

- registered `metric`: `pct_change_after_tax_income` 9
- `proposed_metric`: `debt_outcome_percentile_covered` 1, `fiscal_headroom` 17
- registered `unit_concept`: `gbp` 9, `percent` 9
- `proposed_unit`: `percent_of_gdp` 8, `percentile` 1
- `baseline_policy`: None 27 (null = current law at the scoring date)
- `proposed_baseline`: none

## Distinct values per `conditions` axis

- `concept` (6 distinct): 1 sigma (4); 2 sigma (4); 75% probability of meeting rule (3); 95% probability of meeting rule (2); Mean (2010-2025) (2); Median (2010-2025) (2)
- `estimation` (1 distinct): quantile regressions on UK data 1989-2025 (IMF-style debt-at-risk) (5)
- `fiscal_event` (1 distinct): autumn_budget_2025 (27)
- `fy` (2 distinct): 2029-30 (20); 2030-31 (7)
- `geography` (1 distinct): UK (27)
- `headroom` (1 distinct): £9.9 billion (OBR March 2025) (1)
- `horizon` (2 distinct): freeze to 2030-31 (implied) (7); long run (2)
- `housing_costs` (1 distinct): ahc (2)
- `income_concept` (2 distinct): real household disposable income (7); equivalised household disposable income, after housing costs (AHC) (2)
- `income_group` (7 distinct): decile_2 (3); decile_1 (1); decile_3 (1); decile_4 (1); decile_5 (1); decile_6 (1); decile_7 (1)
- `measure_type` (2 distinct): fiscal buffer against the stability rule (current budget) (16); cumulative effect vs NiGEM baseline (1)
- `method` (4 distinct): Debt-at-risk (6); Historical (4); OBR forecast errors (4); OBR forecast errors (without GFC/COVID) (4)
- `price_basis` (1 distinct): today's prices (16)
- `scenario` (2 distinct): flat-rate income tax increase (Box D scenario) (1); whichever tax is raised (labour income, VAT or corporation tax) (1)
- `sign_convention` (1 distinct): positive = gain to households (9)

## Attribution decisions

- All 27 rows are `attribution: own` / `benchmark_class: different_model` (NIESR's own quantile regression or
  arithmetic on OBR data). The 24 Nov "£24 billion" row is NIESR restating its own Box C number, so it stays `own`.
- Restated OBR/HMT figures were not staged (listed above) because none of them is a household/static row of NIESR's.
- Figure 5 provenance is unstated: `source_model: "unstated"`, `parse_confidence: medium`, the caveat is in `note`.
