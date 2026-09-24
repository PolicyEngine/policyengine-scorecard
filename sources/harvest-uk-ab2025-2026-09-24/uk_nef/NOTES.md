# New Economics Foundation — Autumn Budget 2025 harvest (source `nef`)

Staged 2026-09-24 from the primary documents. **17 claims** in `claims_staged.jsonl.gz`, **4 documents** in `manifest.jsonl`. Row contract, enums and rules: `../README.md`; measure keys: `../REGISTRY_KEYS.md`. Every `value` is verbatim (normalised to the unit as recorded in `normalization`); nothing is derived.

## Access recipe

Four NEF pages fetched directly (`curl`, browser User-Agent, HTTP 200). NEF pages carry no `article:published_time`
meta; `date` is the date printed on the page (26 November 2025; 21 November 2025; 25 September 2025; 26 November 2025).
Text extracted with BeautifulSoup; the press-release "Notes" sections (method statements) are quoted in the rows.

### Documents (manifest.jsonl)

- 2025-09-25 · Breaking the bank? The case for and against central bank losses · `html` · access `direct` · 44,657 bytes · sha256 `5f168c59acda8212…` · **4 rows**  
  <https://neweconomics.org/2025/09/breaking-the-bank>
- 2025-11-26 · Budget tax rises to be overshadowed by Bank of England bond sales and losses · `html` · access `direct` · 39,833 bytes · sha256 `9a423eb2f0fcfef6…` · **5 rows**  
  <https://neweconomics.org/2025/11/budget-tax-rises-to-be-overshadowed-by-bank-of-england-bond-sales-and-losses>
- 2025-11-26 · Poorest households in coldest homes have lost two-thirds of support to reduce energy bills · `html` · access `direct` · 39,776 bytes · sha256 `a165aecc9483fa86…` · **6 rows**  
  <https://neweconomics.org/2025/11/poorest-households-in-coldest-homes-have-lost-two-thirds-of-support-to-reduce-energy-bills>
- 2025-11-21 · Time to be bold: how the budget could set the UK on a more hopeful course · `html` · access `direct` · 47,008 bytes · sha256 `14b795e6a8c4edf2…` · **2 rows**  
  <https://neweconomics.org/2025/11/time-to-be-bold-the-chancellor-must-use-budget-to-set-the-uk-on-a-more-hopeful-course>

## Coverage tally (seed bullets → claims staged → not staged)

Seed: `scores-3-other-shops.md` § New Economics Foundation (4 bullets).

Staged (17 rows):
- Energy bill package (26 Nov): households under £30,000 save "around £100"; over £80,000 "£143"; "£290" foregone
  ECO saving (ONS average, applied by NEF → restated); "two-thirds" of support lost; "£6.4bn of ECO support" replaced
  by "a £1.5bn fund" (government figures → restated) → 6 rows, `source_model: lcfs_serl_ehs_incidence` for the
  incidence rows.
- BoE APF indemnity (21 Nov): "around £18.8bn per year – although only £4.8bn of this would count towards the
  headroom" → 2 rows. "Breaking the bank?" (25 Sep): "nearly £80bn since 2022", "around £20bn a year until 2033",
  "lifetime loss close to £150bn", "save the Treasury up to £20bn a year" → 4 rows.
- Budget tax rises vs BoE losses (26 Nov): £78bn cumulative tax rises (sum of OBR scorecard → restated); £112bn BoE
  losses (own); £32bn/yr bond sales (OBR → restated); £26bn 2029/30 (OBR/HMT → restated); "up to 0.25 percentage
  points" on borrowing costs (BoE → restated) → 5 rows.

Not staged (with reason):
- "tiered reserves (unquantified here)" — no number; "£20bn a year cost would make it the tenth most expensive
  government department" — ranking, not a value.
- 21 Nov restated OBR long-run pressures (health +6.6% of GDP, pensions +2.7%) and health share of spending 14% →
  19% (IFS/Commons Library) — restated, not NEF's; not staged.
- CGT equalisation, RNRB abolition, dividend basic rate, property tax reform, National Energy Guarantee, triple lock:
  advocated without NEF revenue figures.

### Row counts

- by `source`: nef 17
- by `attribution`: own 10, restated 7
- by `benchmark_class`: different_model 17
- by `source_model`: arithmetic 13, lcfs_serl_ehs_incidence 4
- by `value_kind`: cumulative 4, point 11, range_high 2
- by `parse_confidence`: high 10, medium 7
- by `measure_key`:
  - `null` 6
  - `ab2025__renewables_obligation_exchequer_funded_75pct` 4
  - `ab2025_option__boe_apf_indemnity_or_reserves_remuneration_reform` 3
  - `ab2025__package_total_tax_policy_decisions` 2
  - `ab2025__warm_homes_plan_and_warm_home_discount_expansion` 2

## Metrics, units and baselines used

- `proposed_metric: household_energy_bill_change` (`gbp_per_household`, "positive = gain to households") for the
  £100 / £143 / £290 rows. Producer definition (Notes): "We take the Ofgem energy price cap breakdown Oct 2025-Dec
  2025 as our baseline and use that to estimate the median household energy bill across ten income bands using Smart
  Energy Research Lab (SERL) survey (2023) consumption data … Our bill savings estimates are therefore slightly lower
  than official government estimates." `conditions.income_group` carries the printed bands ("household income under
  £30,000", "household income over £80,000").
- `proposed_metric: support_lost_share` (`share`) for the "two-thirds" headline.
- `benefit_cost_change` / `benefit_cost` (registered) for the £6.4bn ECO cut and £1.5bn replacement fund.
- `revenue_change` (registered) for the £18.8bn / £4.8bn / £20bn APF saving rows and the £78bn / £26bn tax rows
  ("positive = saving to the Exchequer" / "positive = yield to the Exchequer").
- `proposed_metric: central_bank_loss_transfer` (`gbp`) for the BoE loss levels (£80bn since 2022, £20bn/yr, £150bn
  lifetime, £112bn 2025-26 to 2030-31); `proposed_metric: bond_sales` (`gbp`); `proposed_metric: gilt_yield_effect`
  (`percentage_points`).
- `period`: energy rows 2026-27 ("from April 2026"); APF rows carry the year stated or, where "per year" has no
  year, 2026-27 with `parse_confidence: medium` and the assumption in `note`; cumulative rows carry the end year
  (`value_kind: cumulative`).
- `measure_key`: energy rows `ab2025__renewables_obligation_exchequer_funded_75pct` (the RO cut is the bill saver; the
  ECO wind-down rows use `ab2025__warm_homes_plan_and_warm_home_discount_expansion`); APF rows
  `ab2025_option__boe_apf_indemnity_or_reserves_remuneration_reform`; package rows
  `ab2025__package_total_tax_policy_decisions`.
- Baselines: all `baseline_policy: null`.

### As staged

- registered `metric`: `benefit_cost` 1, `benefit_cost_change` 1, `revenue_change` 5
- `proposed_metric`: `bond_sales` 1, `central_bank_loss_transfer` 4, `gilt_yield_effect` 1, `household_energy_bill_change` 3, `support_lost_share` 1
- registered `unit_concept`: `gbp` 12, `gbp_per_household` 3, `percentage_points` 1, `share` 1
- `proposed_unit`: none
- `baseline_policy`: None 17 (null = current law at the scoring date)
- `proposed_baseline`: none

## Distinct values per `conditions` axis

- `basis` (2 distinct): static (4); forecast (3)
- `fiscal_event` (1 distinct): autumn_budget_2025 (17)
- `fy` (4 distinct): 2026-27 (8); 2025-26 (2); 2029-30 (2); 2030-31 (2)
- `geography` (3 distinct): UK (11); England (4); Great Britain (2)
- `horizon` (5 distinct): 2025-26 to 2030-31 (cumulative) (2); each year until 2033 (1); lifetime of the APF (1); per year until 2029-30 (1); since 2022 (cumulative) (1)
- `income_group` (2 distinct): household income under £30,000 (2); household income over £80,000 (1)
- `measure_type` (3 distinct): median household energy bill saving, 2026 bills (Ofgem cap Oct-Dec 2025 baseline, SERL 2023 consumption) (3); annual, forecast period (2); portion counting towards fiscal headroom (current budget rule) (1)
- `note` (1 distinct): NEF: 'Our bill savings estimates are therefore slightly lower than official government estimates' (3)
- `originator` (7 distinct): Bank of England (15-25 basis points, Monetary Policy Report August 2025) (1); HM Treasury / OBR (1); OBR (1); OBR (sum of scorecard tax measures) (1); ONS Household Energy Efficiency Statistical Release 2021 (average first-year ECO saving) (1); government (1); government (ECO scheme value) (1)
- `program` (4 distinct): BoE APF indemnity transfers (3); BoE losses from active QT sales (OBR APF assumptions) (1); Energy Company Obligation (ECO) (1); replacement fund for ECO (1)
- `scenario` (1 distinct): counterfactual: ECO-eligible household (EPC D-G, social security > £20/week excl. state pension) receiving ECO retrofit (1)
- `sign_convention` (6 distinct): positive = cost to the Exchequer (4); positive = gain to households (3); positive = saving to the Exchequer (3); positive = yield to the Exchequer (2); positive = support lost (1); positive = support removed (1)
- `subgroup` (1 distinct): poorest households in the coldest homes (ECO-eligible, EPC D-G) (1)

## Attribution decisions

- `own`: NEF incidence results (£100, £143, two-thirds) and NEF arithmetic on BoE/OBR APF data (£18.8bn, £4.8bn,
  £80bn, £20bn/yr, £150bn, £112bn, "up to £20bn a year").
- `restated`: £290 (ONS average first-year ECO saving, which NEF applies), £6.4bn ECO and £1.5bn fund (government),
  £78bn cumulative tax rises (sum of OBR figures), £32bn bond sales (OBR), £26bn (OBR/HMT), 0.25pp (Bank of England).
