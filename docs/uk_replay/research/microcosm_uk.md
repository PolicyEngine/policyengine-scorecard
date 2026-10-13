# Microcosm UK: what population can be built, by year (scorecard#156, track 2)

Scope: PolicyEngine/microcosm @ `7f23594` and PolicyEngine/chronicle @ `1ee7dfe`. I read both clones at `/tmp/uk-replay-scope/{microcosm,chronicle}` and the GitHub issues listed in §5 (read-only `gh`). All paths below are relative to those clones. M = `/tmp/uk-replay-scope/microcosm`, C = `/tmp/uk-replay-scope/chronicle`, UKR = `M/packages/microcosm-build/src/microcosm/build/uk_runtime`, UKP = `M/packages/microcosm-build/src/microcosm/build/uk`.

Evidence labels used throughout:

- **[code]**: implemented in code or a checked-in resource I read.
- **[receipt]**: a committed machine output, such as a fixture or a signed-differences file.
- **[computed]**: I computed it in this task over checked-in files. The script is `/tmp/uk-replay-scope/agents/_chron_scan.py`, with output in `_chron_scan.out` beside it.
- **[deduced]**: follows from code I read, but I did not execute it.
- **[planned]**: documented in an issue or doc as intended, not shipped.
- **unknown**: I could not establish it.

I did not run a UK build. The licensed FRS data and the Chronicle consumer artifact are not in the clones.

---

## Bottom line

1. **Microcosm builds one UK year, and it is hard-pinned.** The base is FRS 2024-25 (survey/base year 2024), calibrated to calendar 2025. One checked-in release object drives the whole build [code: `UKP/frs_release.json:6-11`; `UKP/spec/vintages.yaml:1-16`; `UKP/spec/bundle.yaml:4-5`]. No other FRS year is pinned. Re-basing means re-pinning the release object, 21 raw-tab hashes, parity instruments, the take-up contract and the gate receipts. Changelog `M/changelog.d/723-uk-frs-2024-25-retarget.changed.md` records that surface for the 2023-24 → 2024-25 move.
2. **The certified bundle the scorecard runs on was not built by today's microcosm code.** `populace-uk-2023` came from `PolicyEngine/policyengine-uk-data@dd68c73` plus `populace@4aa4b14`. It is FRS 2023-24 based and fits 149 targets, all at period 2023 [receipt: `M/packages/microcosm-data/tests/fixtures/uk_june_2023/populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/{release_manifest,build_manifest,calibration_diagnostics}.json`].
3. **There is no backcasting.** The only projection operator, `static_aging`, refuses years at or before the base year [code: `M/packages/microcosm-calibrate/src/microcosm/calibrate/static_aging.py:348-349`]. It also has no UK reader [doc: `M/docs/static-aging.md:16`]. The planned UK reader runs forward to 2050-51 only [planned: microcosm#1075].
4. **Targets come from one pinned Chronicle feed, and target compilation fails closed at the calibration year.** The feed is chronicle `825406f`, 344,402 rows. Every one of 1,231 national references must compile at the calibration year or the build stops [code: `UKR/full_targets.py:134-152`]. The feed's UK coverage is overwhelmingly 2023–2026 publications [computed]. A committed receipt shows only 919 of 1,231 references compile at period 2023 [receipt: `UKP/ledger_compile_parity_production_2023_signed_differences.json`]. Calibration years 2010–2024 are therefore blocked on facts, not on solver machinery.
5. **The schema can hold a forecast vintage, but no vintage is stored for any replay event, and the consumer cannot select by publication date.**
   - Chronicle facts carry `source.vintage`, a `source_release_key` hashed over the vintage, and `assertion: source_projection` [code: `C/docs/schemas/consumer_fact.v4.schema.json:13,20,269-270,394-399`; `C/chronicle/consumer_contract.py:90-108`].
   - The only OBR forecast vintage in Chronicle is the EFO of March 2026 [computed; `C/packages/obr/efo_*_march_2026/source_package.yaml`]. That is after Autumn Budget 2025, so it falls outside every replay event.
   - Microcosm resolves facts by *period* ("latest not after"), and its series key folds publication vintages together. Its selector vocabulary has no `vintage` or `source_release_key` key [code: `M/packages/microcosm-build/src/microcosm/build/ledger_targets.py:3217-3239, 3271-3290, 3717-3769`].

---

## 1. UK build surface in microcosm today

### 1.1 UK-specific modules [code]

- **`UKP/`** is the pure-data country package. It holds:
  - `spec/{bundle,catalogs,geography,sources,spine,vintages}.yaml`, registered in `UKP/country_package.json:4-34`;
  - `frs_release.json`, the FRS release pin;
  - `chronicle_feed.json`, the Chronicle pin;
  - `target_references.json`, 1,231 national references [computed];
  - `local_target_references.json`;
  - `gates.json`, 64 gates: 6 preflight, 28 transferred, 4 assembled, 26 terminal [computed];
  - `take_up_contract.json`;
  - vendored fact resources and the parity and signed-difference receipts.
- **`UKR/`** holds about 120 Python modules: spine stages (`spine_build.py`, `frs_*.py`, `spi_*.py`, `was_*.py`, `lcfs_consumption.py`, `etb_vat.py`, `cgt_*.py` and others), targets (`ledger_targets.py`, `full_targets.py`, `hmrc_uprating.py`), the graph (`graph_build.py`, `graph_population.py`, `graph_targets.py`, `graph_calibration.py`, `graph_terminal.py`, `graph_national.py`), the driver (`full_build_cli.py`) and certification (`full_certification.py`, `release_certification.py`).
- **Shared packages**:
  - `microcosm-calibrate` holds the solver, `solve.py`, and `static_aging.py`.
  - `microcosm-data` holds the dataset registry, release contract and publish tooling.
  - `microcosm-graph` holds graph execution.
  - `microcosm-build/.../ledger_targets.py` is the shared Chronicle-to-target compiler.
- **Entry points**:
  - `tools/build_uk_full.py` (`microcosm-build-uk`), with `--release-role national|dense`;
  - `tools/build_uk_frs_spine.py`, a shim;
  - `tools/certify_uk_release_cut.py`;
  - `tools/assemble_uk_release_dir.py` and `tools/assemble_uk_dense_release_dir.py`.

  The docs are `M/docs/uk-full-build-graph.md:1-5, 57-59` and `M/README.md:81-93`.

### 1.2 Base year and survey pins [code]

`UKP/frs_release.json:5-11` pins:

| Field | Value |
|---|---|
| `name` | `frs_2024_25` |
| `survey_year` | 2024 |
| `base_year` | 2024 |
| `calibration_year` | 2025 |
| `time_period` | `"2024"` |
| `vintage` | `2024_25` |
| UKDS study number | SN 9563 |

The zip is acquired from `policyengine/policyengine-uk-data-private@a2039519…`.

The loader is a single cached object (`lru_cache(maxsize=1)`). It validates `survey_year <= base_year < calibration_year` and `time_period == base_year` [`UKR/frs_release.py:49-50, 112-121`]. The country adapter refuses raw-source pins that differ from the canonical FRS stage, and a target period that differs from `calibration_year` [`UKR/country_adapter.py:35-89`]. The tests assert these exact values [`M/packages/microcosm-build/tests/engine_free/uk/test_uk_frs_release.py:40-74`].

Donor and source vintages are each pinned once [`UKP/spec/sources.yaml`, stage headers]:

| Stage | Source and vintage | Location |
|---|---|---|
| `frs_spine` | FRS 2024-25, SN 9563 | 182-184 |
| `spi_income_band_donors` | SPI Public Use Tape 2022-23 plus HMRC ITL July 2026 Table 2.5 | 1280-1282 |
| `hmrc_spi_income_spine` | SPI PUT 2022-23 plus HMRC Personal Incomes Tables 3.6/3.7, 2023-24 | 1362-1364 |
| `was_wealth`, `was_lisa` | WAS round 8, SN 7215 (interviews April 2020 – March 2022) | 2058-2060, 2265-2267 |
| `nts_bus_travel` | NTS 2002-2024, SN 5340 | 2439-2441 |
| `lcfs_consumption` | LCFS 2023-24, SN 9468 | 2758-2760 |
| `etb_vat`, `etb_services` | ETB 1977-2024, SN 8856 | 3212-3214, 3271-3273 |
| CGT stages | HMRC CGT statistics 2026 (2024-25) plus Advani-Summers 2020 | 3904-4338 |
| `uc_deduction_attributes` | DWP UC deductions, March 2025 – February 2026 | 3857-3859 |
| `regional_property_uprating` | ONS HPI, December 2025 | 2406-2408 |

`UKP/frs_release.json:24` says the donor vintages are unchanged by the FRS 2024-25 retarget. Microcosm#1164 (open) proposes moving LCFS to 2024-25.

### 1.3 What a build emits [code/doc]

Each build emits one single-year H5 and one household weight vector. There are no per-year weights.

- **National role**:
  - `microcosm_uk_2024_25.h5`;
  - `build_record.json` (schema 1);
  - `national_target_registry.json` and `national_contract_registry.json`;
  - `rowwise_candidate_manifest.json` (schema 4);
  - calibration diagnostics and gate reports.

  Source: `M/docs/uk-full-build-graph.md:59`.
- **Dense and local roles**: `microcosm_uk_2024_25_local.h5` (or `_dense.h5`) with `.local_gates.json`, `.diagnostics.json`, `.targets.csv`, `candidate.json` and `build.json` [`M/docs/uk-full-build-graph.md:104-106`].
- **H5 contents**: `person`, `benunit`, `household` and a `time_period` table [`UKR/rowwise_dataset.py:80`]. The config's `time_period` defaults to the FRS `time_period`, which is `"2024"` [`UKR/graph_build.py:63-70`].
  - A maintainer comment on microcosm#823 (2026-09-18) says "the H5's own time period is 2025". I did not reconcile this with the code default. **unknown** which value shipped cuts carry.
- **Registry** [`M/packages/microcosm-data/src/microcosm/data/registry.py:101-150`]: three UK entries, all `UKSingleYearDataset`:
  - `("uk", 2023, default)` → `populace_uk_2023.h5`;
  - `("uk", 2025, "national")` → `microcosm_uk_2024_25.h5` via `latest-national.json`, registered off the default until first promotion;
  - `("uk", 2025, "dense")`.

  The UK repo-global `latest.json` "remains frozen on the June 2023 release" [`M/README.md:380-384`].
- **Annual tooling is US-only**:
  - `M/packages/microcosm-data/src/microcosm/data/annual_projections.py:1` ("explicit annual US dataset families");
  - `M/packages/microcosm-build/src/microcosm/build/us_annual_static_aging.py`.

### 1.4 How `populace-uk-2023` was built [receipt]

The source is the fixture copy of the release in `M/packages/microcosm-data/tests/fixtures/uk_june_2023/populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/`.

- **Construction** (from `release_manifest.json` `build.metadata.construction`): "FRS 2023-24 base plus WAS/LCFS/ETB/SPI/derived imputations and a 20x OA clone pool, calibrated on the 149-target UK national/region/country surface."
  - The builder is `populace`, at `populace_commit 4aa4b14`.
  - The data code is `uk_data_commit dd68c73`, which is `PolicyEngine/policyengine-uk-data` per `build_manifest.json` `code.repository`.
  - `policyengine-uk-data` runtime 1.56.1.
  - Built 2026-06-19.
  - Declared engine: `policyengine-uk ==2.89.2`, `policyengine-core ==3.27.1`.
- **Dataset** (`build_manifest.json`): 535,080 households, 1,315,880,118 bytes, sha256 `f17306cc…`.
- **Calibration** (`calibration_diagnostics.json`, `options.year = 2023`): all 149 targets are at period 2023. By source: 142 ONS, 6 SLC, 1 "obr" [computed]. The "obr" row is `obr/private_school_students`, which the 2023 parity receipt shows bound from ISC.
- **Gates**:
  - `exported_nonzero`;
  - `parity` against `enhanced_frs_2023_24_recalibrated`;
  - `release_surface`;
  - `target_fit` (max |relative error| 0.25);
  - `smoke`.
- **Manifest schema**: `release_manifest.json` is `schema_version: 1`. It has `artifacts{kind,path,repo_id,revision,sha256,size_bytes}`, `build{build_id,built_at,built_with_core_package,built_with_model_package,metadata}`, `compatible_{core,model}_packages`, `data_package`, `default_datasets` and `metadata.region_datasets`. The validators live in `M/packages/microcosm-data/src/microcosm/data/contract.py:1084-1291`.
- **The current code has no path to rebuild this bundle.** Rebuilding the FRS 2023-24 vintage in microcosm is microcosm#687 ("Legacy 2023-vintage build … (deferred)"; "No owner. Unscheduled") [planned]. The 2023 pins are "preserved in git history at the pre-#723 pins". The clone is shallow (1 commit), so I could not verify that.
- **Known quality issues**: microcosm#731 (open) scores `populace_uk_2023` at 2026 against admin benchmarks. Income tax is £419bn against OBR's ~£330bn, and Universal Credit £39.9bn against ~£80–86bn.

---

## 2. Per-year builds

### (a) A different FRS year as the base

**Not supported without a re-pin.** The FRS identity is one checked-in object, `UKP/frs_release.json`, and the loader caches exactly one [`UKR/frs_release.py:49-50`]. `sources.yaml` pins all 21 raw tabs by sha256 and size, and `country_adapter.validate_uk_country_source_projection` refuses any drift [`UKR/country_adapter.py:35-68`]. The tests hard-code 2024/2025 [`.../test_uk_frs_release.py:40-74`].

The retarget changelog lists what moved for one year change [`M/changelog.d/723-uk-frs-2024-25-retarget.changed.md`]:

- release object and raw-tab manifest;
- build period;
- take-up `build_year`;
- HMRC surface period mapping;
- eFRS parity reference;
- input coverage manifest;
- input-mass reference;
- gate baselines.

There are some per-year hooks:

- Stages declare a `YEAR_RULE` (`survey_year`/`calibration_year`) [`UKR/frs_disability.py:51`, `UKR/frs_education_grants.py:40-41`; closed microcosm#862].
- The take-up contract is date-keyed back to 2000/2012–2015 and picks "the latest value with year ≤ build year" [`UKP/take_up_contract.json:4` policy text, `build_year: 2024`].

**unknown**: whether the FRS ingest and stage code parse pre-2024-25 FRS codebooks. Variable names and table sets change across years. I did not audit stage column maps against older dictionaries. One test comment cites the FRS 2023-24 dictionary (SN 9367) [`M/packages/microcosm-build/tests/engine_free/uk/test_uk_frs_education.py:30-37`].

### (b) Projecting or backcasting a base-year population to another year

- **Forward reweighting exists, but has no UK reader.** `static_aging` reweights a base cross-section to later years by demographic cell and applies monetary factors [code: `static_aging.py:291-449`]. It raises `ValueError("Projection years must follow base year …")` for any year ≤ base [`static_aging.py:348-349`]. The only demographic reader is SSA's [`static_aging.py:581`]. The docs say "the package does not yet include a UK projection reader" [`M/docs/static-aging.md:16`].
- **Planned UK reader is forward only.** Microcosm#1075 (open, 2026-10-01) plans an ONS 2024-based NPP reader with weights-only projections to 2050-51. It maps no monetary series and is estimated at 2–3 agent-days. It does not cover earlier years [planned].
- **Input uprating from base to calibration year is delegated to policyengine-uk.** The H5 stores base-year inputs (`time_period "2024"`). Calibration measures are `simulation.calculate(variable, year)` at the calibration year [code: `UKR/measure_simulation.py:233`]. So the engine's own uprating carries 2024 inputs to 2025.
  - **unknown**: whether the policyengine-uk engine produces meaningful backward values when a 2024 dataset is simulated at 2010–2023. I did not read policyengine-uk.
- **Calibrating to an earlier year is not refused anywhere I found.** The pinned release refuses `calibration_year ≤ base_year` [`UKR/frs_release.py:115-119`]. The CLI's `--calibration-year` [`UKR/full_build_cli.py:437`, used at `:756-757` and `:1727`] has no ordering check:
  - `rowwise_cli.validate_cli_args` checks only `--source-year > 0` [`UKR/rowwise_cli.py:589-590`];
  - `full_targets` checks only positive [`UKR/full_targets.py:129-131`];
  - `UKFullBuildConfig.__post_init__` has no year check [`UKR/graph_build.py:89-135`].

  So `--calibration-year 2015` would reach target compilation. There it fails on missing facts (see (c)) [deduced].

### (c) Reweighting to year-Y targets

**The machinery exists; the facts and the contract do not, for any Y other than 2025.**

- Every packaged reference is restamped to `target_period = Y` [code: `UKR/ledger_targets.py:481-496`]. Facts are resolved by the reference's period policy: default `latest_not_after`, or `exact`/`source_window` [code: `.../build/ledger_targets.py:35-38, 225-226, 3071-3095`].
- Compilation fails closed at the calibration year. Any unsupported national or local reference at Y raises [`UKR/full_targets.py:134-152, 157-170`].
- **Validation periods** are national {2023, 2025} and local {2025}. They are skipped, not fatal, when facts are missing [`UKR/full_targets.py:60-64`].
- **Year-bound gates**:
  - `uk_ledger_compile_parity_production_2023`, `uk_ledger_compile_parity_incumbent_2025` and `uk_target_surface_local_default_2025` [`UKP/gates.json:31, 43` and the following entries];
  - `uk_cgt_projection_entrants`, which pins policyengine-uk OBR GDP-growth values for 2023–2030 with drift tolerance 0.0005 and horizon 2030 [`UKP/gates.json:1096`ff].
- **OBR calendar-year targets need two fiscal years.** The 23 OBR references use `calendar_year_window`, which needs fiscal-year facts for Y−1 (weight 3/12) and Y (9/12). It refuses a partial window [`.../build/ledger_targets.py:99-101, 2736-2767`].
- **Executed evidence for 2023.** At period 2023 the current feed compiles 919 of 1,231 references [receipt: `UKP/ledger_compile_parity_production_2023_signed_differences.json`, `compiled_count: 919`]. The receipt also shows 120 "calibration_drift" rows against the June-2023 fixture (ONS land values, SLC, ISC), so the June-2023 targets and today's 2023 compile differ.

**Years actually wired.** I found these in config, tests and CI:

- **Config**: 2025 only [`UKP/frs_release.json:8`, `UKP/spec/bundle.yaml:4-5`, `UKP/spec/vintages.yaml:10-16`].
- **Tests**: `calibration_year=2024` and `2026` appear only in unit tests with mocked compilers or config objects [`.../tests/engine_free/uk/test_uk_full_targets.py:89-112`; `test_uk_full_target_graph.py:14`; `.../tests/engine/uk/test_uk_full_graph_admission.py:104`].
- **CI**: `engine-uk` and `integration-uk` jobs run on synthetic fixtures (`--synthetic-fixture-dir`) and have no year matrix [`M/.github/workflows/test.yml:103-135`; `.../tests/integration/uk/test_uk_staging_integration.py:40,121`].

---

## 3. Calibration machinery, targets and Chronicle

### 3.1 Optimizer and loss [code]

The solver is `M/packages/microcosm-calibrate/src/microcosm/calibrate/solve.py:1-60`.

- **Loss**: fixed-scale weighted MAPE, `weighted_mean(|A w − b| / s)` with `s = max(|b|, 1)`.
- **Optimizer**: Adam over log-weights (the default), or proximal gradient.
- **Options**:
  - `mass` free or conserve;
  - `max_weight_ratio`, a hard per-record cap;
  - L0 hard-concrete gates with a record budget;
  - L1 and L2 penalties.

The UK national doctrine is `UKR/national_doctrine.py:33-40`:

| Setting | Value |
|---|---|
| Epochs | 1500 |
| Learning rate | 0.02 |
| `max_weight_ratio` | 10 |
| Seed | 0 |
| `target_loss_cap` | 10 |
| Mass | free |
| `l0_lambda` | 0 |
| Target weighting | `family_equal`, an equal objective share per target family (rationale at `:45-63`) |

### 3.2 Targets [code/computed]

`UKP/target_references.json` holds 1,231 national references. Its description says period is "the model and calibration year 2025, distinct from the FRS 2024-25 base period 2024".

- **Families**, by count:

  | Family | References |
  |---|---|
  | `hmrc_spi_region` | 360 |
  | `hmrc_spi` | 169 |
  | `ons_population` | 149 |
  | `dwp_universal_credit` | 118 |
  | `hmrc_cgt` | 105 |
  | `council_tax_stock` | 100 |
  | `dwp_state_pension` | 59 |
  | `hmrc_itl` | 33 |
  | `obr` | 23 |
  | Other DWP, ONS, SLC, DfT, DfE, Scottish Government and other families | the remainder |

- **Period policy**: 1,129 `latest_not_after`, 101 `source_window`, 1 `exact`.
- **Assertion policy**: 1,169 `observed_only`, 62 `allow_source_projection`. The latter are all OBR rows, HMRC ITL band projections, SLC borrower forecasts, Scottish Child Payment spending and DWP HB.
- **Fact uprating** (`uprating_index`) applies to 534 references. It uses HMRC ITL growth series and policyengine-uk parameters (`gov.economic_assumptions.indices.obr.*`, the state pension rate, the employer NIC rate), with DfT BUS0415 for bus fares [`UKR/hmrc_uprating.py:1-25, 46-50`; `UKR/ledger_targets.py:697-721`].
  - The policyengine-uk-parameter indices come from **the installed engine's** OBR series, not a vintage-specific one.

Selection runs in this order [`UKR/full_targets.py:171-191`; `M/docs/uk-full-build-graph.md:126`]:

1. Compile.
2. Apply reviewed measure exclusions, evaluated at `--review-date`.
3. Reconcile band edges.
4. Run the graph's `uk.full.target_selection` node.

### 3.3 Certification [code/doc]

- **Gates**: `UKP/gates.json` (64 gates).
- **Graph certification**: `uk.full.certification` writes unsigned `certification.json` [`M/docs/uk-full-build-graph.md:106-110`].
- **National cuts** are certified by `tools/certify_uk_release_cut.py`, signed with `MICROCOSM_UK_TERMINAL_GATE_SIGNING_KEY`, published `--no-latest`, then promoted to `latest-national.json` [`M/docs/uk-national-release-assembly-runbook-806.md:1-60, 190-215`].
- **unknown**: whether any 2025 national cut has been promoted. The registry entry is still off the default variant [`M/packages/microcosm-data/src/microcosm/data/registry.py:114-136`]. The HF repo is private and I did not query it.

### 3.4 How microcosm consumes Chronicle [code]

1. `UKP/chronicle_feed.json` pins `source_commit 825406f…`, `consumer_fact.v4`, 344,402 rows, and the facts and manifest sha256.
2. `UKR/chronicle_feed.py:90` (`load_uk_chronicle_feed`) loads the pin.
3. `.../build/ledger_artifact.py:192` (`load_ledger_consumer_artifact`, with hash checks) loads the artifact.
4. `UKR/full_targets.py:75` (`load_uk_full_target_inputs`) or the national variant takes over. Graph nodes call it at `UKR/graph_targets.py:229-232` and `UKR/graph_national.py:476`.
5. `UKR/ledger_targets.py:481` (`compile_uk_target_registry`) compiles the UK references.
6. `.../build/ledger_targets.py:594` (`compile_ledger_target_references`) produces a `TargetRegistry`.

A re-pin is one reviewed change. Both roles refuse an unpinned feed; national has a diagnostic override [`M/docs/uk-chronicle-feed-repin.md:1-66`]. The feed is built in Chronicle with `build-bundle --suite uk -> build-consumer-artifact` [`UKP/chronicle_feed.json`].

### 3.5 UK series Chronicle carries [computed]

Method: I parsed the `period` of every record set in every `C/packages/<publisher>/*/source_package.yaml` for 20 UK publishers (200 packages). No UK package uses `{year}` templating. This counts declared record-set periods only.

| Publisher | Packages | Period coverage (min..max over packages) and notes |
|---|---|---|
| OBR | 6 | `efo_{receipts,expenditure,aggregates,economy}_march_2026`: FY2024 outturn (`observation`) and FY2025–2030 forecasts (`source_projection`). `fuel_duty_receipts_by_vehicle_april_2024`: 2022–2028. `salary_sacrifice_costing_february_2026`: 2027–2030. **One EFO vintage only.** |
| HMRC | 23 | Mostly 2023–2026. ITL July 2026: 2023 outturn plus 2024–26 projections. SPI 2023-24. CGT 2026 release. Long series: CGT Table 1, 1987–2024; Child Benefit, 2003-08 to 2025-08; Tax-Free Childcare, 2017 onwards; property rental, 2020–24; hydrocarbon oils, 2020 onwards. |
| DWP | 43 | Stat-Xplore February 2023 – March 2026 for State Pension, Pension Credit, AA and UC; ESA from 2018-05; UC childcare from 2021-03; Spring 2026 expenditure tables FY2023–2030 (62 observation, 186 projection); WFP 2023–25; workplace pensions 2023–25 (the package name says 2009_to_2025, but periods ingested are 2023–25). |
| ONS | 44 | MYE mid-2023 and mid-2024; NPP 2024-based for 2024–29 (projection); Census 2021; families and households 2018–2025; land balance sheet 1995–2024; savings interest 2018–2025; consumer trends 2020 to 2026-Q1; ASHE 2024; PIPR 2023-01 to 2026-06. |
| Scottish Government | 11 | Band D 1996–2026; collection 1999–2025; council tax bands 2023–25; social security budget 2024–26; bus 2023–25. |
| Welsh Government | 8 | Council tax 2023–2026; bus and transport 2022–24. |
| NRS / NISRA / DfC NI / DfI NI / NITHC | 5 / 5 / 3 / 2 / 1 | Census 2022 (Scotland) and 2021 (NI); constituency population mid-2024; NI pensions and UC 2023 to 2026-05; NI bus 2019–24. |
| SLC | 6 | Borrower forecasts 2024–29 (projection); repayments FY2024; student support AY2013–2024. |
| VOA / MHCLG | 2 / 7 | VOA CTSOP 2025; council taxbase 2023–25; collection 2021–25; EHS 2023-24. |
| DfT / DESNZ / Ofgem / ORR / ISC / DfE | 10 / 15 / 2 / 4 / 2 / 1 | BUS01 2005–2025; NTS 2003–2025; road fuel 2005–2024; NEED 2023/2024; Ofgem cap 2024Q1–2026Q4; ORR support 2015–2024; ISC census 2023, 2024; DfE early education 2011-01 to 2026-01. |

Implication [deduced]: the families that dominate the surface have no Chronicle facts before 2023. These are ONS population, HMRC SPI, DWP UC/State Pension/Pension Credit and OBR. Under `latest_not_after`, a reference has nothing to resolve for those years, so calibration years before 2023 fail closed. The 2023 receipt (919 of 1,231) is the measured version of this.

---

## 4. Vintage: is a forecast as-at date recorded?

**Chronicle (schema): yes, by release identity; no explicit publication date** [code]:

- `consumer_fact.v4` requires the following:

  | Field | Location |
  |---|---|
  | `source_release_key` | `C/docs/schemas/consumer_fact.v4.schema.json:13, 74` |
  | `assertion ∈ {observation, source_projection}` | `:20, 394-399` |
  | `source.vintage` and `source.extracted_at` | `:269-270, 289-292` |
  | optional `period_coverage.basis` including `projection_horizon` | `:420-435` |

- `source_release_key` hashes source name, table, file, url, **vintage**, sha256, size and the R2 uri [`C/chronicle/consumer_contract.py:90-108`].
- The identity ADR includes `source_release_key` in `aggregate_fact_key`, so several publications of the same statistic coexist as distinct facts that share a `semantic_fact_key` [`C/docs/adr-chronicle-fact-identity-v2.md:65-78, 155-176, 206-221`].
- The README states that publisher projections are facts typed `source_projection` and that PolicyEngine-computed values never enter the store [`C/README.md:28-31, 51-58`].
- The vintage is a label, such as `efo_march_2026`. `extracted_at` is the extraction date (2026-08-06 for the March 2026 EFO), not the publication date [`C/packages/obr/efo_receipts_march_2026/source_package.yaml:21-22`]. I found no `published_at` or release-date field in the v4 schema.
- chronicle#160 (open): the assertion axis "cannot represent provisional (revisable) observations".

**Can "OBR forecast for FY Y as published at event E" be expressed?**

- **In Chronicle: yes** [deduced from schema plus an existing package]. One source package per EFO (as `efo_*_march_2026` does) gives facts with `assertion: source_projection`, `period {fiscal_year, Y}`, `source.vintage = efo_<event>` and a distinct `source_release_key`. Only the March 2026 EFO exists today [computed]. That is after Autumn Budget 2025, so **0 of the 2010–2025 replay events have their own OBR vintage in Chronicle**. chronicle#225 (open) records that OBR returns 403 to non-browser fetchers, which affects unattended backfill.
- **In a microcosm target reference: only by pinning per event, and with no as-at semantics** [code/deduced]:
  - The selector vocabulary is closed. It has `source_table`, `record_set_id`, `aggregate_fact_key`, `source_record_id`, `assertion`, `period_*` and others, but **no `vintage` or `source_release_key`**. An unknown key raises [`.../build/ledger_targets.py:3717-3769`].
  - A per-event reference could pin `source_table`. The OBR tables embed the vintage, for example `'EFO March 2026 detailed forecast tables: receipts'` [`C/packages/obr/efo_receipts_march_2026/source_package.yaml:17`].
  - Resolution is period-based: `latest_not_after` the target period [`:3071-3095, 3186-3214`]. The series-invariant key excludes `source_table` and vintage, and record-set ids are normalised to strip glued vintage years "or every vintage of one series looks like a different series" [`:3217-3239, 3242-3290`].
  - So if a second EFO vintage entered the feed, today's unpinned OBR references would match two facts at the same period and raise "matched multiple Ledger facts" [`:1786-1823`; deduced, not executed].
  - The contract is one packaged `target_references.json` restamped to a single target period [`UKR/ledger_targets.py:493-496`]. There is no per-event contract mechanism or "as of date" period policy (`ALLOWED_PERIOD_MATCH_POLICIES = {latest_not_after, exact, source_window}`, `:36-38`).
- **Engine-side vintage coupling.** Fact uprating reads policyengine-uk parameters [`UKR/hmrc_uprating.py:46-50`]. The release-blocking `uk_cgt_projection_entrants` gate pins the engine's OBR GDP-growth path to ±0.0005 [`UKP/gates.json:1096`ff]. Building with an engine whose OBR path differs would trip the gate [deduced]. A vintage-faithful replay therefore needs the build-time engine and the scoring-time engine decoupled, or both versioned per event.

---

## 5. Effort signals (issues, specs, TODOs)

**Microcosm issues** (read via `gh`):

- **#687** (open): "Legacy 2023-vintage build of the microcosm UK spine (deferred)". The scope is to pin FRS 2023-24 tabs and check parity against `enhanced_frs_2023_24@655dd07e…`. It is "Not on the August path. No owner. Unscheduled", to be closed at decommission if unclaimed.
- **#665** (open): master migration epic. Phase P2 is "Spine built in microcosm from raw **FRS 2024-25** sources (#723 retarget; 2023 build deferred to #687)". Workstream **F — Uprating / multi-year (#148)** is unchecked.
- **#148** (open): "Decide UK panel, public transfer…", including "Multi-year/panel UK data: policyengine-uk-data#345, #346, #158". It is a decision record, not an implementation.
- **#1075** (open): UK static aging reader (ONS 2024-based NPP), weights-only, **forward to 2050-51**, estimated at 2–3 agent-days plus 0.5–1 review day. No backcast.
- **#1076** (open): UK State Pension projection bundle (forward).
- **#723** (closed): the FRS 2024-25 retarget. Its changelog is the template for the cost of each re-pin.
- **#731** (open): scorecard of `populace_uk_2023` and `enhanced_frs_2024_25` against admin data at 2026.
- **#1164** (open): move LCFS to 2024-25.
- **#1095** (open): track uk-data defect fixes.

**Chronicle issues:**

- **#160** (open): no provisional or revision status on facts.
- **#225** (open): OBR blocks unattended fetch.

I found no microcosm or Chronicle issue about historical OBR EFO vintages or backcasting. The searches I ran on microcosm were "backcast", "historical", "vintage OBR", "forecast vintage", "replay", "OBR EFO", "multi-year uk" and "frs 2023-24". On Chronicle I searched "OBR", "EFO", "vintage", "historical uk" and "backfill".

---

## 6. Per-year table, 2010–2025

Column meanings:

- **Base FRS pinned in microcosm**: whether a raw FRS vintage for that year is pinned.
- **Build path**: whether the current code can produce a population calibrated to that year.
- **Chronicle targets**: what the pinned feed's UK packages cover at that period [computed, §3.5].
- **OBR forecast as-at event**: whether any EFO published at or near events in that year is in Chronicle.

| Year | Base FRS pinned in microcosm | Build path exists | Chronicle targets (outturn / forecast) | OBR forecast as-at event | Status |
|---|---|---|---|---|---|
| 2010 | No [`UKP/frs_release.json`, `spec/vintages.yaml`] | No. No backcast (`static_aging.py:348-349`), and compile fails closed (`full_targets.py:134-152`) | Outturn: only long series (HMRC CGT T1, Child Benefit, ONS land, DfT/NTS, DESNZ road fuel, Scottish Government council tax). No ONS population, SPI, DWP or OBR. Forecast: none | None | Needs work: FRS re-pin, new facts, per-year contract |
| 2011 | No | No | As 2010, plus DfE early education (2011-01 onwards). Forecast: none | None | Needs work |
| 2012 | No | No | As 2011. Forecast: none | None | Needs work |
| 2013 | No | No | Plus SLC student support (AY2013 onwards). Forecast: none | None | Needs work |
| 2014 | No | No | As 2013. Forecast: none | None | Needs work |
| 2015 | No | No | Plus ORR support (2015 onwards). Forecast: none | None | Needs work |
| 2016 | No | No | As 2015. Forecast: none | None | Needs work |
| 2017 | No | No | Plus HMRC Tax-Free Childcare (2017 onwards). Forecast: none | None | Needs work |
| 2018 | No | No | Plus ONS families and households, ONS savings interest, DWP ESA (2018-05 onwards). Forecast: none | None | Needs work |
| 2019 | No | No | Plus DfI NI bus. Forecast: none | None | Needs work |
| 2020 | No | No | Plus HMRC property rental, hydrocarbon oils, ONS consumer trends, ORR fares. Forecast: none | None | Needs work. Also unknown: FRS 2020-21 fieldwork quality, not assessed here |
| 2021 | No | No | Plus Census 2021, UC childcare (2021-03 onwards), CGT BADR, MHCLG collection. Forecast: none | None | Needs work |
| 2022 | No | No | Plus Scottish Census 2022, ONS small-area income FYE2023, DESNZ energy trends, OBR fuel duty by vehicle (April 2024 vintage), Welsh bus. Forecast: OBR fuel-duty-by-vehicle FY2023–28 (April 2024 vintage) only | None | Needs work |
| 2023 | No in the current code (2023-24 pins only in pre-#723 git history, per #687, unverified). The certified populace-uk-2023 used FRS 2023-24 via policyengine-uk-data@dd68c73 | **Certified artifact exists** (period 2023, 149 targets; `uk_june_2023` fixture). Not rebuildable by current microcosm (#687 deferred). With the current feed, only 919/1231 references compile at 2023 (receipt), so fail-closed | Outturn: ONS MYE 2023, SPI 2023-24, HMRC ITL 2023-24, DWP Stat-Xplore Feb 2023 onwards, DWP Spring 2026 FY2023, council taxbase 2023, NEED 2023, ISC 2023. OBR: no FY2022/FY2023 facts, so OBR calendar windows unsupported (deduced, `ledger_targets.py:2736-2767`) | None | **Certified** (populace_uk_2023, outside current microcosm). Re-deriving it in microcosm needs work |
| 2024 | **Yes, as the base**: FRS 2024-25 (survey/base year 2024, `frs_release.json:6-9`). But the build calibrates to 2025, not 2024 | No release path to calibrate to 2024. The `--calibration-year 2024` flag exists (`full_build_cli.py:437`), but OBR windows for 2024 need FY2023 facts, which are absent, so it fails closed (deduced) | Outturn: MYE 2024, OBR FY2024 outturn rows, HMRC ITL 2024-25 projection, DWP, NEED 2024, etc. Forecast: HMRC ITL and DWP 2024 projections | None (EFO March 2026 only) | Needs work (unbuilt; partial targets) |
| 2025 | Yes: FRS 2024-25 base, `calibration_year 2025` | **Yes.** `microcosm-build-uk --release-role national|dense` (`docs/uk-full-build-graph.md:7-59`). Needs licensed FRS, donors and the Chronicle artifact | Full wired surface: 1,231 national references. OBR window = FY2024 outturn plus FY2025 forecast from EFO **March 2026** | None for any 2025 event (Spring Statement or Autumn Budget 2025). EFO March 2026 postdates them | **Buildable today** for a "latest-outturn/latest-forecast" 2025 population. Certified-cut promotion: unknown. Not vintage-faithful to any 2025 event |

Notes on the table:

1. **"Certified".** Only `populace_uk_2023` is a certified UK release in the evidence I read (fixture plus `registry.py:101-111`). The `("uk", 2025, "national")` line has release machinery and a registry entry. Whether a cut was promoted is unknown.
2. **No year has OBR forecast targets as published at the event.** Chronicle holds one EFO (March 2026). A faithful replay needs a Chronicle source package per EFO (about 2 per year, 2010–2025) and a microcosm contract that pins each event's vintage. Microcosm's current resolution and selector semantics would otherwise either refuse the ambiguity or pick by period, not publication date (§4).
3. **What it would take for any 2010–2024 calibration year, in microcosm terms.** Each item is [deduced] from the code paths cited:
   - (i) re-pin an FRS vintage, or add a backcast operator, which does not exist;
   - (ii) add Chronicle UK facts for that period, including ONS MYE, HMRC SPI, DWP caseloads and OBR outturn;
   - (iii) either relax the fail-closed compile through reviewed exclusions, or author a per-year reference contract;
   - (iv) re-measure the year-bound gates: the 2023/2025 compile parity receipts and `uk_cgt_projection_entrants`.
