# Certified replay years: uk-data 1.58.0 with policyengine-uk 2.125.1

Bundle key `uk-data-1.58.0__pe-uk-2.125.1`. The pin is `data/uk/certified_bundles/uk-data-1.58.0__pe-uk-2.125.1.json`. policyengine 6.2.6 certifies it, released from policyengine.py#555 at tag `6.2.6` (`481940ec`), with policyengine-uk 2.125.1 and policyengine-core 3.33.0.

The supported calendar-year window is **2024 through 2030**. Calendar year Y proxies OBR fiscal year Y–(Y+1). The 2.89.2 bundle's window was 2023–2030 (see [YEARS.md](YEARS.md)). On this population, FY2023–24 source cells stay in the accounting once, labelled `outside_bundle_window`, and are not computed. That affects Spring Budget 2023, Autumn Statement 2023 and Spring Budget 2024: nine measure-years that were computed on the 2.89.2 bundle.

## Population identity

- Artifact `enhanced_frs_2024_25.h5` in `policyengine/policyengine-uk-data-private` (an HF model repo), tag `1.58.0`, which resolves to commit `47bbb58d3f6467aa4a7059bc6110d2bdcf699b29`.
- SHA-256 `5ba399ea5ab9a6c7d4e9aaf6c623080beb34d9ad5f330f6244dbad72b8d960b6`, 128,369,110 bytes.
- `pandas.read_hdf(<cached H5>, "time_period")` returns `2024`.
- The publisher claim is at HF commit `fdeba38517bd86067f34c0a5d8ed8923efb3b10a`, file `releases/1.58.0/release_manifest.json`. Its `compatible_model_packages` include `policyengine-uk==2.125.1`, and its `compatible_core_packages` include `policyengine-core==3.33.0`. The artifact digest and size match the cached file. The main session fetched that manifest once, read-only, on 2026-10-10 to verify the claim. Registration itself is offline.

## Engine evidence (installed wheels in the 6.2.6 freeze, read 2026-10-10)

Line numbers refer to `site-packages` in an environment built from `docs/uk_replay/requirements-uk-data-1.58.0__pe-uk-2.125.1.txt`. The [offline loader audit](OFFLINE_BUNDLE_AUDIT_uk-data-1.58.0__pe-uk-2.125.1.json) binds the source hashes.

| File and lines | What it establishes |
| --- | --- |
| `policyengine_uk/data/economic_assumptions.py:53–61` | `extend_single_year_dataset` starts at `int(dataset.time_period)` (2024) and defaults `end_year` to 2030. It copies the input population into each year, then uprates it. |
| `policyengine_uk/simulation.py:505–517` | A single-year dataset goes through that extension before any year's inputs are loaded. |
| `policyengine_uk/simulation.py:142–150`, `232` | `reform=` becomes `Scenario.from_reform(...)`. Its modifier runs after data load unless the scenario sets `applied_before_data_load`. |
| `policyengine_uk/utils/scenario.py:111`, `178`, `189` | A dictionary reform calls `target.update(...)` on the processed parameter tree. It doesn't reload or fiscally reprocess, so an annual lookup still resolves at 1 January (`compute_uk_event.annual_reform`). |
| `policyengine_uk/utils/parameters.py:78–113` | Current law is processed by sampling 30 April for each annual period (`:113`). The exceptions are parameters with `fiscal_year_blend: true` (`:108`), which take a day-weighted 6 April–5 April blend, and `preserve_calendar_dates: true` (`:106`). The CGT basic, higher and additional rates and fuel-duty LPG/natural gas carry `fiscal_year_blend`; some tobacco and alcohol rates carry `preserve_calendar_dates`. |
| `policyengine_uk/simulation.py:192–194` before `232` | The default UC July 2025 modifier runs before the dictionary scenario, so the UC health construction still has to refresh the fixed inputs after its parameter update (`compute_uk_event.uc_health_scenario`). |
| `policyengine_uk/scenarios/uc_reform.py:70`, `95` | The health inputs are fixed for `range(2026, 2030)`, so 2030 is not covered. The registered Spring Statement 2025 horizon ends in 2029. |
| `policyengine_uk/variables/gov/dwp/universal_credit/standard_allowance/uc_standard_allowance.py` | At 2.125.1 the standard allowance is `amount × 12`. `rebalancing/standard_allowance_uplift` is not read (policyengine-uk#2239, fixed in #2242, which isn't in 2.125.1). |
| `policyengine/tax_benefit_models/uk/model.py:397` | `managed_microsimulation` materialises the certified dataset and forwards `reform=` / `scenario=` to `Microsimulation`. It passes the stored-year dataset, so a projected year is never treated as the data year (the policyengine.py#557 issue). |
| `policyengine/provenance/manifest.py:339`, `422` | With network blocked, the release-metadata request fails and the loader returns the packaged certification. |
| `policyengine_uk/data/dataset_schema.py:56`, `198` | The H5 is opened read-only (`HDFStore(mode="r")`), so no writable copy is needed. |

## Construction consequences on this bundle

The registry rebuild applies the rulings in the main session's construction decisions for #156. Briefly:
- every construction is byte-identical to 2.89.2 except where the engine requires otherwise;
- AB2024 CGT gets a data-driven `cgt_fiscal_year_blend_annual_reversal`, because processed CY2024 already blends in the 30 October 2024 increase;
- AS2023 Class 2 keeps its `small_profits_threshold = 12570` override unchanged. It is now dormant: at 2.125.1, `policyengine_uk/utils/class_2.py:44–49` tests profits strictly above the lower profits threshold whenever `lower_profits_threshold_applies` is true, which it is from 2022-04-06. Keeping it avoids a construction change with no numerical effect.

The registry's `construction_adjustments` lists each deviation, and ENGINE_COMPARISON reports it as `construction_change`.

## Dataset input contract (1.58.0 H5 columns)

- **Present:** benefit-unit `would_claim_child_benefit` and `child_benefit_opts_out` (so the HICBC opt-out, policyengine-uk#2140, acts on data); `pension_credit_reported_capital`; pooled person `capital_gains`; `property_purchased`, `main_residence_value`, `other_residential_property_value`, `non_residential_property_value`; `personal_pension_contributions`, `employer_pension_contributions`.
- **Absent:** `private_pension_wealth`, separate BADR, residential or carried-interest gains, benefit-unit reported capital, and `additional_residential_property_purchased`. Inputs added by later engine changes are therefore inert, at their defaults.
