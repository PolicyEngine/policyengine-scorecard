# KFF Medicaid scorecard lane progress

## State

In progress. Full certified 2024 baseline and take-up-reform extracts have been computed in separate processes, passed the national anchors and identities, and have been aggregated into diagnostics, moments counterparts, and campaign staging. Network access remains prohibited for this lane.

## Done

- Read the lane brief and established the required descriptive register, certified-bundle constraint, single-period 2024 scope, simulation memory discipline, and sanity anchors.
- Attempted the GitNexus exploration workflow; GitNexus resources and query tools are not exposed in this workspace, so repository files and tests will be used directly.
- Created the implementation and validation plan.
- Read the complete KFF provenance and staged table, plus the existing moments and campaign contracts.
- Added the KFF source registry, descriptive construct annotations, and adapter: 52 state-indicator percentage rows (US + 50 states + DC) and five 2022 flagship-brief rows. The selected rendered column has no NSD cells; the adapter retains any NSD selected cell as an explicitly suppressed row.
- Extended campaign ingest with a strict `policyengine_us_inputs` ReformRef exhibit route, preserving state geography, baseline values, deltas, and canonical reform identity. Focused plus existing campaign/database tests pass (62 tests).
- Added memory-disciplined sample, one-simulation extraction, and aggregate-output pipelines. The deterministic sample selects 5,000 of 57,240 households (seed 20260818), rescales `household_weight` by 11.448, retains 14,254 people and every referenced group entity, and runs baseline/reform in separate processes.
- Sample validation: 75.282M eligible, 69.039M enrolled, +6.243M enrollment; eligible-minus-enrolled identity gap 0.000000004 persons. The bridge is 3.552M reported-uninsured and 2.691M other-coverage. The fixed-baseline-denominator spending construction produces +$115.558B. These are sample checks, not published estimates.
- Confirmed the fiscal mechanic: a standalone take-up override re-normalizes fixed state Medicaid spending. The reform extractor supplies the baseline state-allocation denominator, reproducing policyengine-us's intended baseline-branch cost semantics without retaining two simulations. This execution choice is explicit in every staged reform row.
- Confirmed installed policyengine-us 1.764.6 has no module `__version__` attribute; the pipeline uses `importlib.metadata.version("policyengine-us")`, asserts it equals `sim.policyengine_bundle["model_version"]`, and records bundle `us-5.0.2` plus the full certified Build P id.
- Added a bounded-memory eligibility execution: each configured native Medicaid category pathway is materialized separately and its dependency cache is cleared before the final native `is_medicaid_eligible` formula runs. On the required sample, all 14,254 person rows are exactly identical to the ordinary native calculation across every extracted column.
- Completed the full certified baseline: 77.325M eligible, 72.336M enrolled, and $880.019B in Medicaid spending. Both population anchors differ from the lane anchors by less than 0.1%.
- Completed the separate full reform process with the annual take-up input forced true. Policy-invariant baseline eligibility and the baseline state-allocation denominator are supplied from the baseline extract; enrollment and Medicaid spending are recomputed independently.
- Full reform results: +4.989M enrollment and +$71.527B Medicaid spending. The marginal-enrollment bridge is 2.792M reported-uninsured and 2.196M other-coverage; the enrollment and bridge identities hold to floating-point precision.
- Built 214 PE moment counterparts, 208 campaign rows, and US/state diagnostic CSVs. The 2024 reported-uninsured counterpart is 34.921M eligible among 80.932M uninsured (43.15%); the modeled-uninsured alternative is 2.785M among 48.796M (5.71%).
- Added strict sample/full provenance gates and explicit bridge-scope annotations to the aggregate builder. The real builder-to-JSONL-to-database test covers reform identity, state shape, identities, provenance, and idempotency.
- Ingested the full staging file into `data/scorecard.db` offline: 208 exhibits, 52 geographies, no deferred rows, all under canonical ReformRef key `849973669b6526d6`. A second temporary-database ingest returned the same 208-row result.
- Extended the additive moments pipeline for multiple counterpart payloads, deterministic primary/alternative variants, null-safe suppression, period-specific annotations, and dated reference counterparts. The regenerated 603-row payload contains 52 KFF `concept_mismatch` rows for 2024 and five truthful `not_computed` 2022 rows with separately dated 2024 PE references.

## Next

- Run the complete offline test, formatting, and application-data checks; write the uncommitted PR body and final report with the three largest state differences and exact commit list.
