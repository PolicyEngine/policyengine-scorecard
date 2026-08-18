# KFF Medicaid scorecard lane progress

## State

In progress. The KFF source population is adapted into 57 truthful-vintage moments rows. Network access remains prohibited for this lane.

## Done

- Read the lane brief and established the required descriptive register, certified-bundle constraint, single-period 2024 scope, simulation memory discipline, and sanity anchors.
- Attempted the GitNexus exploration workflow; GitNexus resources and query tools are not exposed in this workspace, so repository files and tests will be used directly.
- Created the implementation and validation plan.
- Read the complete KFF provenance and staged table, plus the existing moments and campaign contracts.
- Added the KFF source registry, descriptive construct annotations, and adapter: 52 state-indicator percentage rows (US + 50 states + DC) and five 2022 flagship-brief rows. The selected rendered column has no NSD cells; the adapter retains any NSD selected cell as an explicitly suppressed row.

## Next

- Extend the moments builder for multiple PE payloads, deterministic primary/alternative variants, truthful-period references, row metadata, and null-safe suppression handling; add tests.
- Validate baseline and 100%-take-up computation on a uniformly sampled 5,000-household dataset, using one managed simulation per process.
- Run full-file baseline and reform passes separately, stage aggregate diagnostics/results, wire moments, and run offline checks.
