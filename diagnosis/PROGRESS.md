# Divergence diagnosis batch 1 progress

## State

Required context reads are complete on branch `diagnosis-batch-1`; queue-item evidence collection is next. The audit is restricted to static code reading and the supplied JSON data; no microsimulation runs will be made. The separate 2026 projection/full-participation adjudication is out of scope.

## Done

- Read the `gitnexus-debugging` workflow and began the two required methodology/mechanics documents.
- Confirmed the certified stack and the distinction between record-level take-up flags, formula eligibility, and soft calibration targets.
- Confirmed the worktree was clean before beginning.
- Finished `docs/replication-assessment.md` and `docs/mechanics-audit.md`, including the program formulas, current Build P target surface, and evidence-citation conventions.
- Read the shipped annotation registry and runtime-recorded variable/toggle metadata.
- Read `docs/RECONCILIATION.md` and `docs/SCHEMA_NOTES.md`; incorporated the independent bit-exact recomputation, the corrected monthly WIC gate, and the unit/construction safeguards.
- Confirmed `calibration_relationship` and `calibration_basis` are structural row fields in the rebuilt comparison and must govern whether a result is consumed, seeded, or held out.
- Attempted the required remote refresh; network access is disabled, but the locally tracked `origin/main` commit is already merged into this branch.

## Next

- Audit all ten queue items defensively, beginning with ways PolicyEngine could be wrong and then ways Urban/ATTIS could be wrong.
- Record each item's consumed/seeded/held-out relationship and avoid treating consumed-target agreement as validation.
- Write and validate `diagnoses.json` and `DIAGNOSES.md`, then commit the completed batch.
