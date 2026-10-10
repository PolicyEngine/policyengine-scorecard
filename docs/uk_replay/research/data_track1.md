# How one 2023 population is simulated in other years: what a single-population replay of older OBR events can and cannot say

Research worker, read-only. Context: policyengine-scorecard#156, track 2 scoping, written 2026-10-09.
Every claim below cites a file:line read in this task, or a computation run in this task (marked **computed**, with its output file). Facts I know but did not verify from a source here are marked **external, unverified**. Anything else is marked **unknown** or **inference**.

## Sources and versions actually read

| Source | Version | Path |
|---|---|---|
| policyengine.py | 393762b (2026-10-09), bundle 6.2.4 | `/tmp/uk-replay-scope/policyengine.py` |
| policyengine.py, the loader track 1 uses | 5.0.2 | `~/PolicyEngine/_worktrees/scorecard-replay-pilot/.venv-replay/lib/python3.12/site-packages/policyengine` |
| policyengine-uk (installed) | 2.124.0, with policyengine-core 3.32.29 | `/tmp/uk-replay-scope/venv/lib/python3.12/site-packages/policyengine_uk` |
| policyengine-uk (the certified bundle's declared pin) | 2.89.2, with policyengine-core 3.27.1 | `…/scorecard-replay-pilot/.venv-replay/lib/python3.12/site-packages/policyengine_uk` |
| policyengine-uk-data | 0dc9ef2 | `/tmp/uk-replay-scope/policyengine-uk-data` |
| populace-uk release (cached, not downloaded) | revision `populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z` | `~/.cache/huggingface/hub/datasets--policyengine--populace-uk-private/snapshots/a75a9a83…/releases/populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/{release_manifest.json,calibration_diagnostics.json}`; artifact blob `…/blobs/f17306cc…` (sha matches `data/uk/certified_bundle.json:7`) |
| scorecard | main at 99f1cc1 (this worktree) | `~/PolicyEngine/_worktrees/scorecard-replay-inventory` |
| track 1 | **`origin/replay/pilot` does not exist** (`git fetch origin replay/pilot` → "couldn't find remote ref"). Track 1's work is uncommitted in the local worktree `~/PolicyEngine/_worktrees/scorecard-replay-pilot` (branch `replay/pilot` at 99f1cc1 + untracked files). I read those files without changing them. | |

Computations run (all read-only; the outputs are in `/tmp/uk-replay-scope/agents/`):
- `data_track1_probe.py` → `data_track1_probe_2.124.0.json` and `data_track1_probe_2.89.2.json`. This is a synthetic 1-household `UKSingleYearDataset` with `fiscal_year=2023`, calculated for 2012, 2017, 2022, 2023, 2024, 2026, 2030 and 2031 under both engine pins. It uses no survey data.
- `data_track1_receipt.py` → `data_track1_receipt.json`. These are weighted counts of reported benefit receipt in the certified artifact, read field by field with h5py.
- `data_track1_param_dates.py` → `data_track1_param_dates_{2.124.0,2.89.2}.json`. This gives the earliest dated value of each parameter leaf in the raw YAML. The parser is approximate: it reads `values:` and `brackets:` forms only.

---

## 1. What happens when the 2023 dataset is simulated for a year Y ≠ 2023

### 1a. The load path (evidenced)

1. **policyengine.py, current version (393762b).** `pe.uk.managed_microsimulation()` materialises the bundle dataset (`src/policyengine/tax_benefit_models/uk/model.py:418-422`). If the file has the single-year layout, it wraps it as `UKSingleYearDataset` (`model.py:424-433`) and calls `policyengine_uk.Microsimulation(dataset=…)` (`model.py:434`). There is no year argument and no year guard on this path (`model.py:397-443`).
   - **policyengine 5.0.2**, which track 1 uses, does the same: it wraps a single-year file as `UKSingleYearDataset` and calls `Microsimulation` (pilot venv `policyengine/tax_benefit_models/uk/model.py:313-325`).
2. **The artifact uses the single-year layout.** **Computed:** its top-level HDF5 keys are `benunit, household, person, time_period`, and `time_period` is `['2023']`. This matches the layout check in `policyengine_uk/data/dataset_schema.py:24-41`. Track 1 got the same value (`docs/uk_replay/YEARS.md:14-16`, pilot worktree).
3. **policyengine-uk's `Simulation.__init__`** sends a `UKSingleYearDataset` to `build_from_single_year_dataset` (`simulation.py:180-181`). That method calls `extend_single_year_dataset(dataset, parameters)` (`simulation.py:505-517`).
4. **`extend_single_year_dataset`** (`data/economic_assumptions.py:53-70` in 2.124.0; `:35-52` in 2.89.2):
   - `start_year = int(dataset.time_period)`, i.e. 2023.
   - `end_year` defaults to 2030.
   - It copies the same records into every year from 2023 to 2030 and then calls `apply_uprating`.
   - It never creates a year before `start_year`.
5. **`apply_uprating`** skips the first year and uprates each later year from the year before it (`economic_assumptions.py:86-93`).
6. **`build_from_multi_year_dataset`** builds the entities from the first year only. It then calls `set_input(variable, year, …)` for every year in 2023–2030 (`simulation.py:533-549`).

### 1b. Which inputs are uprated, by what, from where (evidenced)

For each consecutive year (2024 from 2023, and so on): `value_t = value_{t-1} × (1 + g_t)`. Here `g_t` is a **single national scalar per index per year**: `parameters.get_child(index)(year)` (`economic_assumptions.py:107-116`). The variable-to-index map is `data/uprating_indices.yaml`:

| Index | Variables | Lines (2.124.0) |
|---|---|---|
| OBR average earnings | Employment income and pension contributions | 30-36 |
| OBR CPI | Every `*_reported` benefit, `state_pension`, and consumption categories | 37-80 |
| OBR per-capita GDP | Dividends, savings, property income, wealth, capital gains | 89-124 |
| OBR per-capita mixed income | Self-employment income | 125-126 |
| Private-pension index | Private pension income | 127-128 |
| **ONS population** | **`household_weight`** | 129-130 (2.89.2: 84-85) |

Custom rules:
- **Council tax** follows OBR council-tax growth by nation (`economic_assumptions.py:135-161`).
- **Rent** follows ONS private-rent or OBR social-rent growth. The code logs "not supported for years before 2022" and skips uprating for those years (`:164-196`; the guard is at `:177-181`).
- **Student-loan plans** are re-labelled by cohort (`:199-332`).

Where the growth series come from (`parameters/gov/economic_assumptions/yoy_growth.yaml:1-16` in 2.124.0, and `:1-7` in 2.89.2, which is identical): outturn for 2009–2024, the **OBR March 2026 EFO** for 2025–2030, and long-run assumptions for 2031–2073. For example, average earnings are 0.051 in 2024 (`yoy_growth.yaml:135`) and population growth is 0.0107 in 2024 (`yoy_growth.yaml:823`).

**Computed** (both engine pins give identical results): the probe household's weight goes from 1000 (2023) to 1010.70 (2024) and 1021.85 (2026). Its employment income goes from 30000 to 31530 (2024). Both match the indices above.

### 1c. Weights (evidenced and computed)

- Weights are **not re-solved per year**. `household_weight` is multiplied by the national ONS population growth for every household alike (`uprating_indices.yaml:129-130`).
- Person and benefit-unit weights are the household weight. In policyengine.py they are copied from the household (`uk/datasets.py:204-254`).
- The certified artifact stores only `household_weight`. **Computed:** the household table's columns include `household_weight` and nothing else weight-like. The person and benunit tables have no weight column.

### 1d. Demographics are not aged (evidenced and computed)

- `age` does not appear in `uprating_indices.yaml` (lines 28-130), and the extension copies the same records (`economic_assumptions.py:61-64`).
- **Computed:** the probe person's age is 35.0 in every year from 2023 to 2031.
- The student-loan code *assumes* ages move with the year (`base_year_age = age - (year - _FRS_BASE_YEAR)`, `economic_assumptions.py:243`), but nothing actually changes `age`.
- Household composition, tenure and region are therefore fixed at 2023 for every year.

### 1e. Years after 2030 (evidenced and computed)

There are no stored inputs after 2030. Instead, policyengine-core either:
- uprates the latest earlier input by the variable's own `uprating` parameter (core 3.32.29 `simulations/simulation.py:1145-1197`), or
- carries the latest input forward (`:1198-1236`; UK enables this at `tax_benefit_system.py:69`).

**Computed (2031):** weight ×1.0043 and employment income ×1.033 relative to 2030. Rent is flat (carried over).

### 1f. Years before 2023: no inputs exist, so core returns defaults silently (evidenced and computed)

This is the central finding.

- **Core 3.32.29.** Uprating can only start from an *earlier* stored input (`simulation.py:1128-1153`). Carry-over only uses inputs starting no later than the requested period (`:1221-1231`). If the only stored periods are *later*, it `return holder.default_array()` (`:1237-1247`: "A later input does not carry backwards").
- **Core 3.27.1** (the bundle's pin) does the same: `if last_known_period.start > period.start: return holder.default_array()` (pilot venv `policyengine_core/simulations/simulation.py:862-864`).
- **Defaults.** `household_weight.default_value = 1` (`variables/household/demographic/household_weight.py:11`). `age.default_value = 40` (`variables/input/demographic.py:15`). `would_claim_uc.default_value = True` (`variables/gov/dwp/universal_credit/would_claim_uc.py:16`). Income inputs have no default, so they are 0 (as computed).
- **Computed, identical on 2.89.2/3.27.1 and 2.124.0/3.32.29.** For 2017 and 2022:

  | Variable | Value |
  |---|---|
  | `household_weight` | 1.0 |
  | `employment_income` | 0 |
  | `age` | 40 |
  | `rent` | 0 |
  | `would_claim_uc` | True |
  | `income_tax` | 0 |

  stderr was empty: **no error and no warning.** On the real artifact, a weight of 1 on each of 535,080 household rows (computed row count) means pre-2023 totals are unweighted sums of near-empty records.

### 1g. Years before 2015: parameters are missing, so formulas fail (evidenced and computed)

- `process_parameters` runs `backdate_parameters(parameters, "2015-01-01")` and then `convert_to_fiscal_year_parameters` (`tax_benefit_system.py:113-115`).
- **Backdating** fills in each parameter's *earliest recorded value* from 2015-01-01 up to its first date (`utils/parameters.py:11-25`). It does nothing before 2015.
- **Fiscal-year conversion** covers only `range(2015, 2041)`. It sets each calendar-year period to the value on 30 April of that year, so period Y means FY Y–(Y+1) (`utils/parameters.py:102-119`).
- A formula's `parameters(period)` reads `period.start` (core `periods/helpers.py:57-58`). A parameter returns `None` before its first value (core `parameters/parameter.py:223-227`).
- So for Y < 2015:
  - Converted parameters do not exist.
  - Lookups read 1 January Y, i.e. the value in force in FY (Y−1)–Y. That is a one-year shift against the Y→FY Y–(Y+1) convention.
  - Any parameter whose history starts in 2015 or later is missing.
- **Computed:** for 2012, `employment_income` and `income_tax` raise `ParameterNotFoundError: gov.simulation.labour_supply_responses[income_elasticity] … not found in the 2012-01-01 tax and benefit system`, on both pins.
- **Computed (approximate):** of 1,405 parameter leaves in 2.124.0, **858 have a first value on or after 2015-01-01** (416 on or after 2020). For 2.89.2 the figures are 662 of 936 (275 on or after 2020).
- Core income tax and NICs start in 2015:
  - Personal allowance first value 2015-04-06 (`parameters/gov/hmrc/income_tax/allowances/personal_allowance/amount.yaml:2-3`).
  - Basic rate 2015-04-01 and higher-rate threshold 2015-04-05 (`income_tax/rates/uk.yaml:11-12, 42-43`).
  - Class 1 employee main rate 2015-04-01 (`national_insurance/class_1/rates/employee/main.yaml:2-3`) and primary threshold 2015-04-06 (`…/thresholds/primary_threshold.yaml:10-11`).
  - 2.89.2 has the same personal-allowance history.

---

## 2. Which years can be simulated at all (errors, warnings, guards)

| Path | Supported | Guard behaviour | Evidence |
|---|---|---|---|
| policyengine-uk, single-year dataset (2023) | 2023–2030 with stored inputs. 2031+ by core uprating or carry-over. | **Y < 2023: silent defaults.** Y < 2015: `ParameterNotFoundError` on many formulas. No year guard. | §1f, §1g; `simulation.py:505-517`; probe JSONs |
| policyengine.py `managed_microsimulation` | Same as above | No year argument or guard | `uk/model.py:397-443` |
| policyengine.py `PolicyEngineUKDataset` / `create_datasets` | Default years `[2026…2030]` | `data_year > year` raises "data can only be projected forward". `sim.dataset[year]` for a missing year raises `ValueError("No dataset found for year …")`. | `uk/datasets.py:101-105, 268, 300`; `dataset_schema.py:216-220` |
| scorecard `compute_uk_obr_costings.py` | `YEAR_MIN=2024`, `YEAR_MAX=2030` | Years outside that range raise `RegistryError`. Engine version must equal the bundle's declared engine and the `==2.89.2` pin. | `pipeline/compute_uk_obr_costings.py:48-49, 754-763, 843-875` |
| track 1 `compute_uk_event.py` | 2023–2030 | Raises "certified single-population replay supports 2023 through 2030 only" | pilot `pipeline/compute_uk_event.py:308-322` |

**The bundle changes under current policyengine.py (evidenced).** In the 6.2.4 bundle, the UK default dataset is **`enhanced_frs_2024_25`** (policyengine-uk-data 1.56.16), declaring **policyengine-uk 2.102.3** (`src/policyengine/data/bundle/manifest.json:94-101`). `populace_uk_2023` is reachable only as a by-name `dataset_overlays` entry (`manifest.json:258-265`; merge logic at `provenance/manifest.py:275-315`).
- **Computed:** the cached `enhanced_frs_2024_25.h5` (two HF snapshots) has `time_period` b'2024'.
- So on the current policyengine.py, the default window starts in 2024.
- policyengine 5.0.2 defaults to `populace_uk_2023` on 2.89.2 (pilot venv `policyengine/data/bundle/manifest.json:34-36, 80-87`).
- **Inference:** the scorecard's call `pe.uk.managed_microsimulation()` passes no dataset (`compute_uk_obr_costings.py:1026-1030`). Together with its engine checks (`:861-874`), that means a run on current policyengine.py would either use a different population or fail the pin check. I did not execute this.

## 3. Per-year calibrated weights and targets

**The certified bundle has none (evidenced and computed).**
- The release has three artifacts: microdata, `calibration_diagnostics.json`, and `populace_uk_2023_calibration.npz` (`release_manifest.json:2-24`).
- The `.npz` SHA (`fb2fc115…`) equals `target_surface.sha256` in the diagnostics (`calibration_diagnostics.json:160-162`). That is the 149-target surface, not a set of per-year weights.
- Calibration settings are `"year": 2023` and `calibrated_households: 535080` (`calibration_diagnostics.json:147-153`).
- **Computed:** all 149 targets have `period: 2023`. Sources are **ONS 142, SLC 6, OBR 1**. The OBR target is `obr/private_school_students`.
- The ONS targets are mostly regional age bands (12 regions × 9 bands), household types, tenure (England) and land values. There are no HMRC or DWP caseload targets.
- The build is "FRS 2023-24 base plus WAS/LCFS/ETB/SPI/derived imputations and a 20x OA clone pool" (`release_manifest.json:39`). The target registry version is `policyengine-uk-data-dd68c73` (`calibration_diagnostics.json:156-158`).

**policyengine-uk-data at 0dc9ef2 (evidenced).**
- **One release:** `CURRENT_FRS_RELEASE = frs_2024_25`, survey_year 2024, base_year 2024, calibration_year 2025 (`datasets/frs_release.py:53-68`).
- **One calibration year.** Weights are solved at `time_period=frs_release.calibration_year` (`datasets/create_datasets.py:276-283, 303-310`). The default weight key is `str(calibration_year)` (`utils/calibrate.py:19-20, 245-246`). The calibrated data is then down-rated to the base year and saved (`create_datasets.py:327-358`).
- **No per-year weight files for 2024–2030 are written.** I searched `range(20xx` and found only target-side year loops (`targets/sources/ons_demographics.py:53` uses `range(2022, 2030)`; `obr.py:668-682`).
- **OBR targets** come from the **March 2026 EFO** receipts and expenditure tables, FY 2024-25 to 2030-31, mapped to calendar 2024–2030 (`targets/sources/obr.py:1-10, 28-38`).
- **How far back it can go:**
  - Its own uprating table covers **2020–2034** only, and raises `UpratingYearOutOfRangeError` outside that range (`utils/uprating.py:5-6, 36-55, 251-271`).
  - Its household-weight index is hard-coded at 1.0 for 2020 and 2021 (`:17-33`).
  - `create_frs(year=…)` contains some handling for older FRS vintages ("2018 FRS uses blanks…", `if year < 2021`; `datasets/frs.py:1236-1252`) and refuses a year that does not match its folder (`:760-790`).
  - Whether older FRS raw files (2010–2019) are available to PolicyEngine is **unknown**.
  - **Computed:** a legacy-format `enhanced_frs_2022_23.h5` (period `2022` only) sits in the local HF cache (`models--policyengine--policyengine-uk-data-private/snapshots/47bbb58d…`). Its provenance and engine compatibility are **unknown**.

## 4. Track 1's findings so far (uncommitted, pilot worktree)

- **Supported window is CY 2023–2030.** Track 1 says this is "a projection of one population… it does not establish a population or forecast matched to each historical event" (`docs/uk_replay/YEARS.md:3-8`). It sets end-2030 from `extend_single_year_dataset` and start-2023 from the file's `time_period` (`YEARS.md:14-16, 25-38`).
- **2022 and 2031 are rejected.** "Historical events beginning before 2023–24 require track 2's historical rules and per-year populations" (`YEARS.md:36-38`; `RECIPE.md:117-133`).
- **The axes are named but not repaired:** `population_vintage` and `baseline_vintage` (`RECIPE.md:145-153`).
- **Registries (computed):**
  - Spring Budget 2023 has `calendar_years` 2023–2027. Its 170 source rows for **FY 2022-23 are "accounted but not simulated"** (`data/uk/events/spring_budget_2023_measures.json`, `years_note`).
  - The other four events (AS2023, SB2024, AB2024, SS2025) start in 2023 or 2024.
- **Track 1 has no findings on scoring years before FY 2022-23** (e.g. Autumn Budget 2017). Nothing was attempted there.
- Its model investigations are 2024–2030 encoding gaps (`MODEL_INVESTIGATIONS.md`), for example the missing Carer's Allowance earnings test and the CGT commencement date.

---

## 5. Failure modes of using the single 2023 population for older scoring years

**Overall verdict (evidenced).** As the code stands, **no scoring year before 2023 can be computed from this population at all.**
- 2015–2022 return silent defaults: weight 1, zero incomes (§1f).
- Before 2015, many formulas raise errors (§1g).
- So any 2011–2022 number from this bundle on the standard path is an artefact, not an estimate.

The modes below apply only if track 2 *re-stamps or back-casts* the 2023 records to year Y. That is mechanically possible because `time_period` is just a label:
- `UKSingleYearDataset(…, fiscal_year=Y)` (`dataset_schema.py:61-69`).
- policyengine.py treats `data_year=None` data as observed for its year (`uk/datasets.py:56-65`; `uk/model.py:291-307`).

**(a) Income distribution and demographics of the wrong year.**
- *Evidenced:* only scalar national growth factors move incomes (`economic_assumptions.py:109-116`). Ages, household composition, tenure, regional mix and the 2023 calibration are fixed (§1c, §1d). The weights solve only 2023 ONS/SLC targets (§3).
- *Evidenced:* the PE growth series do not reach back far enough to back-cast all incomes. **Computed** first dates:
  - per-capita GDP 2021 (dividends, savings, property income)
  - mixed income 2021 (self-employment)
  - population 2021
  - house prices and mortgage interest 2021
  - rent 2022
  - council tax 2023
  - CPI, RPI and earnings 2009
- *Evidenced:* the indices are built from the first year at 1.0 (`create_economic_assumption_indices.py:38-47`) and then backdated to 2015. So the per-capita GDP, mixed-income and population indices are flat for 2015–2021. uk-data's own back-caster stops at 2020 (`uprating.py:48-55`).
- *Inference:* severity grows with distance from 2023:
  - 2021–2022: small, with indices available.
  - 2017–2020: only CPI and earnings are available, so capital incomes and self-employment have no index.
  - 2011–2016: the same, plus a 7–12-year demographic gap.

**(b) Rules missing before 2015, or backdated.**
- *Evidenced:* there are no fiscal-year values before 2015, and core IT/NIC parameters start in 2015-04 (§1g). **2011–2014 is not computable without encoding the history.**
- *Evidenced:* for 2015–2016 and later, backdating imports *later* law back to 2015-01-01. Examples:
  - `dividend_allowance` first value 2016-04-06 at £5,000, citing Finance Act 2016 (`dividend_allowance.yaml:2-7`). Backdated, it applies in FY 2015-16.
  - `benefit_cap` first values 2016-11-07 (`benefit_cap.yaml:9,17,28,36`). Backdated, they apply from 2015.
  - Dividend rates of 7.5%, 32.5% and 38.1% from 2015-04-01 (`dividends.yaml:10-11, 40, 72`).
  - The personal allowance jumps from 10,600 (2015-04-06) to 11,500 (2017-04-06) with no 2016 entry (`amount.yaml:3-4`).
- *External, unverified:* the FY 2016-17 personal allowance was £11,000, and dividend taxation before April 2016 used a different regime.
- *Computed:* 416 of 1,405 leaves start in 2020 or later. In 2017–2019, those leaves carry later law.

**(c) Programmes that are absent or shrunk in the 2023 population.**
- *Evidenced:* CTC, WTC, IS and HB are claimed only if the family **reported receipt in the data** (or under a `claims_all_entitled_benefits` override):
  - `would_claim_CTC.py:11-14`, `would_claim_WTC.py:11-14`, `would_claim_IS.py:11-14`, `housing_benefit/would_claim_housing_benefit.py:11-14`
  - CTC is `defined_for = "would_claim_CTC"` (`child_tax_credit.py:10`).
- *Computed:* weighted reported receipt in the certified 2023 artifact, in benefit units:

  | Benefit | Benefit units |
  |---|---|
  | UC | 2.94m (£33.5bn) |
  | CTC | 0.62m |
  | WTC | 0.29m |
  | HB | 1.92m |
  | IS | 0.30m |
  | JSA-IR | 0.035m |
  | ESA-IR | 0.57m |
  | Pension Credit | 1.24m |

  The population totals 28.84m households and 68.44m people.
- *Evidenced:* the model's own UC roll-out parameter runs from 0 (2010) through 0.2 (2018-01), 0.58 (2020-01) and 0.8 (2022-01) to 1.0 (2023-07) (`parameters/gov/dwp/universal_credit/rollout_rate.yaml:12-38`).
- *Computed:* **no `.py` file in policyengine-uk 2.124.0 references it**. A grep for "rollout" outside `.pyc` matches only three parameter description files.
- *Inference:* in a re-stamped 2011–2020 world:
  - The legacy and tax-credit caseload would be the 2023 residual.
  - Families on UC in 2023 would get UC in years when the model's own parameter says it barely existed.
  - Measures on tax credits, legacy benefits, or the UC/legacy split would be scored on the wrong base.
  - The size of the gap from historical caseloads is **unknown**: no historical caseload source was read.
- *Evidenced but limited:* "active" end-date switches exist only for closures (tax credits `active.yaml:2-4`, IS `active.yaml:2-4`). Nothing models the pre-2023 caseload.

**(d) The OBR's vintage forecast versus the uprating path.**
- *Evidenced:* growth is outturn through 2024 plus the March 2026 EFO (`yoy_growth.yaml:1-7`). uk-data's OBR targets are the March 2026 EFO for 2024–2030 (`obr.py:7-9, 28-38`). The bundle's own targets are 2023 ONS/SLC (§3).
- *Evidenced:* parameter histories record **outturn law**, including later events. For example, personal-allowance values to 2030 cite the OBR EFO of November 2025 (`amount.yaml:3-14`).
- *Inference:* an older event's costing (e.g. AB2017, FY 2017-18 onward) used that event's EFO forecast and pre-measure baseline. A replay would grow incomes along realised 2017–2024 outturn and score against law that already contains every later measure. Both axes are unsized. Track 1 tags them as `population_vintage` and `baseline_vintage` without sizing them (`RECIPE.md:145-153`).

### Summary by period (each statement traces to the evidence above)

| Scoring years | Standard path | If re-stamped or back-cast |
|---|---|---|
| **2011–2016** | Not computable: silent defaults plus `ParameterNotFoundError` before 2015 | Rules missing before FY 2015-16, later law imported into 2015-16, no capital-income or population index, and UC/legacy caseload inverted. **Misleading.** |
| **2017–2020** | Not computable (silent defaults) | Rules mostly present, but 416 leaves backdated. Earnings and CPI indices exist; others do not. UC roll-out 20–58% by the model's own parameter versus the 2023 caseload. **Misleading for benefit measures; tax-rate and threshold measures carry (a) and (d) unsized.** |
| **2021–2022** | Not computable (silent defaults); track 1 rejects 2022 | Indices exist (rent from 2022). uk-data's back-caster covers 2020+. A cached legacy 2022 dataset exists (unknown status). Roll-out 0.66–0.94. **Best candidate for a labelled answer**, still tagged (a)–(d). |

## Unknowns

- Whether older FRS raw files or other per-year PE populations (2010–2021) exist and are usable.
- The provenance and compatibility of the cached `enhanced_frs_2022_23.h5`.
- The historical caseloads and EFO vintages against which to size (c) and (d).
- Whether the `.npz` holds anything beyond the target surface. I matched its SHA but did not open it.
