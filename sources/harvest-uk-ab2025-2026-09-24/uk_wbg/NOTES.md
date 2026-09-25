# Women's Budget Group — Autumn Budget 2025 harvest (source `wbg`)

Staged 2026-09-24 from the primary documents. **7 claims** in `claims_staged.jsonl.gz`, **2 documents** in `manifest.jsonl`. Row contract, enums and rules: `../README.md`; measure keys: `../REGISTRY_KEYS.md`. Every `value` is verbatim (normalised to the unit as recorded in `normalization`); nothing is derived.

## Access recipe

The report PDF (`Budget-2025-Response-WBG-5.pdf`) and the publication page were fetched directly with `curl` and a
browser User-Agent (HTTP 200; the seed's 403/Cloudflare challenge did not recur, so no proxy was used). pypdf text.
The publication page carries the "Amendment – 9 December 2025" note (Figure 2 title/notes corrected from 2029/30 to
2030/31); the PDF's ModDate is 2025-12-09. `date` = 2025-12-04 (publication date) with the correction in the note.
`source_model` is `ukmod_b2025.08` per the report's footnotes ("UK WGB's estimations using UKMOD Public version
B2025.08, using FRS 2023/24 (UK_2023_a2)").

### Documents (manifest.jsonl)

- 2025-12-04 · ‘Cost of Living Budget’ 2025: What it Means for Women (publication page) · `html` · access `direct` · 88,223 bytes · sha256 `c9da2308256ead46…` · **0 rows** — carries the 9 December 2025 amendment note  
  <https://www.wbg.org.uk/publication/cost-of-living-budget-2025-what-it-means-for-women/>
- 2025-12-04 · ‘Cost of Living Budget’ 2025: What it Means for Women · `pdf` · access `direct` · 322,206 bytes · sha256 `ec6e39af1ab41268…` · **7 rows** — corrected 9 December 2025 (Figure 2 title/notes now say 2030/31); PDF ModDate 2025-12-09; fetched directly with a browser User-Agent (the seed reported a 403)  
  <https://www.wbg.org.uk/wp-content/uploads/2025/12/Budget-2025-Response-WBG-5.pdf>

## Coverage tally (seed bullets → claims staged → not staged)

Seed: `scores-3-other-shops.md` § Women's Budget Group (4 bullets).

Staged (7 rows):
- 63% of those newly paying tax under the freeze (vs a 1pp rate rise) are women → 1 row (`affected_share`,
  `conditions.subgroup: women`).
- Two-child limit: single-mother households +£735 in 2029/30 → 1 row; with the benefit cap also abolished £1,800 and a
  9% rise in disposable income → 2 rows (option key `ab2025_option__remove_the_benefit_cap`).
- LHA relink + two-child limit + benefit cap: child poverty 31% (2024/25) → 29.5% (2029/30), 660,000 children →
  3 rows, **restated** (footnote 26 = Resolution Foundation, "No half measures"; `source_model: landman_ttm`).

Not staged (with reason):
- Figure 1 (single-father households; other household types) and Figure 2 (change in household disposable income
  AHC in 2030/31 by household type under the freeze vs a 1pp rate rise) — chart-only, no printed values.
- Restated statistics: 450,000 children lifted out of poverty by 2029/30 (DWP); single mothers ~50% of two-child-limit
  households (HMRC); ~70% of capped households single parents (DWP); 52% of LHA-shortfall claimants single women (DWP
  EIA 2020); <1% of properties above £2m (HMT); 70% of Carer's Allowance recipients women; 60% of Motability customers
  women; £8bn freeze yield 2029/30 = "around 31% of the total revenue the OBR forecasts" (OBR); women 58% of income on
  rent vs 42% men — all government/OBR/other statistics, not WBG output.
- Gender split of losers from HVCTS, dividend/savings/property rises, salary-sacrifice cap: not quantified by WBG.

### Row counts

- by `source`: wbg 7
- by `attribution`: own 4, restated 3
- by `benchmark_class`: different_model 7
- by `source_model`: landman_ttm 3, ukmod_b2025.08 4
- by `value_kind`: point 7
- by `parse_confidence`: high 6, medium 1
- by `measure_key`:
  - `ab2025_option__relink_lha_to_30th_percentile_of_local_rents` 2
  - `ab2025_option__remove_the_benefit_cap` 2
  - `ab2025__personal_tax_thresholds_freeze_to_2031` 1
  - `ab2025__uc_child_element_remove_two_child_limit` 1
  - `null` 1

## Metrics, units and baselines used

- `proposed_metric: affected_share` (`share`) for the 63%; `conditions.unit_population` spells out the group ("people
  who pay income tax under the freeze but would not under a 1pp rise in all income tax rates"). Producer definition
  (p.16): "women are 63% of the people who will be paying taxes due to the freeze, but who would not have paid taxes if
  income tax rates had increased by one percentage point instead".
- `average_annual_gain` (registered; `gbp_per_household`, `conditions.statistic: mean`, `subgroup: single-mother
  households`) for £735 / £1,800; `pct_change_after_tax_income` (`percent`) for the 9%. Producer definition (p.10):
  "On average, single-mother households will see an increase in their annual income of £735 in 2029/30".
- `poverty_rate` (`share`) and `poverty_count_change` (`children_under_18`) for the restated RF rows.
- `period`: 63% row 2030-31 (`period: 2031`, medium confidence — the sentence has no year; Figure 2 under the same
  footnote is 2030/31); two-child-limit rows 2029-30.
- `measure_key`: `ab2025__personal_tax_thresholds_freeze_to_2031`; `ab2025__uc_child_element_remove_two_child_limit`;
  `ab2025_option__remove_the_benefit_cap`; `ab2025_option__relink_lha_to_30th_percentile_of_local_rents`.
- Baselines: all `baseline_policy: null`.

### As staged

- registered `metric`: `average_annual_gain` 2, `pct_change_after_tax_income` 1, `poverty_count_change` 1, `poverty_rate` 2
- `proposed_metric`: `affected_share` 1
- registered `unit_concept`: `children_under_18` 1, `gbp_per_household` 2, `percent` 1, `share` 3
- `proposed_unit`: none
- `baseline_policy`: None 7 (null = current law at the scoring date)
- `proposed_baseline`: none

## Distinct values per `conditions` axis

- `basis` (1 distinct): static (4)
- `data` (1 distinct): UKMOD Public version B2025.08, FRS 2023/24 (UK_2023_a2); 'The results and their interpretation are the WBG’s sole responsibility' (4)
- `fiscal_event` (1 distinct): autumn_budget_2025 (7)
- `fy` (3 distinct): 2029-30 (5); 2024-25 (1); 2030-31 (1)
- `geography` (1 distinct): UK (7)
- `income_concept` (1 distinct): household disposable income (1)
- `originator` (1 distinct): Resolution Foundation, 'No half measures' (footnote 26) (3)
- `poverty_line` (1 distinct): relative_60_median (3)
- `sign_convention` (1 distinct): positive = gain to households (3)
- `statistic` (1 distinct): mean (3)
- `subgroup` (2 distinct): single-mother households (3); women (1)
- `unit_population` (2 distinct): children (3); people who pay income tax under the freeze but would not under a 1pp rise in all income tax rates (1)

## Attribution decisions

- `own` / `different_model` (UKMOD B2025.08) for the 63%, £735, £1,800 and 9% rows.
- `restated` for the LHA/child-poverty rows (Resolution Foundation "No half measures", footnote 26) — the seed flagged
  "may be cited rather than WBG's own"; confirmed cited.
