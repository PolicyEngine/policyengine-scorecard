# KFF Medicaid scorecard lane progress

## State

In progress. The worktree is on `us/kff-medicaid`; the pre-staged KFF source directory is present and intentionally unmodified so far. Network access is prohibited for this lane.

## Done

- Read the lane brief and established the required descriptive register, certified-bundle constraint, single-period 2024 scope, simulation memory discipline, and sanity anchors.
- Attempted the GitNexus exploration workflow; GitNexus resources and query tools are not exposed in this workspace, so repository files and tests will be used directly.
- Created the implementation and validation plan.

## Next

- Read the full KFF provenance and inspect the existing Yale/TPC moments adapters, campaign/populace reform staging, schemas, and tests.
- Add the KFF source adapter and tests.
- Validate baseline and 100%-take-up computation on a uniformly sampled 5,000-household dataset, using one managed simulation per process.
- Run full-file baseline and reform passes separately, stage aggregate diagnostics/results, wire moments, and run offline checks.
