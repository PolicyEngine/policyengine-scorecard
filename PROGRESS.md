# KFF Medicaid scorecard lane progress

## State

In progress. The KFF source population and campaign schema are implemented, and the full baseline/reform computation path has been validated on the required deterministic 5,000-household sample. Network access remains prohibited for this lane.

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

## Next

- Extend the moments builder for multiple PE payloads, deterministic primary/alternative variants, truthful-period references, row metadata, and null-safe suppression handling; add tests.
- Run full-file baseline and reform passes separately, stage aggregate diagnostics/results, wire moments, and run offline checks.
