# RESUME — diagnosis batch 1 (second run after harness restart)

Read and execute `diagnosis/BRIEF.md` in this worktree. A prior run started:
commit 0090270 created `diagnosis/PROGRESS.md` (context reads begun, no
audits completed, no diagnoses written). Do NOT restart from zero — trust
PROGRESS.md's Done list, finish the context reads, then audit the ten queue
items and deliver `diagnosis/diagnoses.json` + `diagnosis/DIAGNOSES.md` per
the brief's deliverable contract. Commit per coherent step on this branch
(`diagnosis-batch-1`). No pushes.

New context since the brief was written (the worktree now contains it —
`origin/main` was merged in):

1. `docs/RECONCILIATION.md` + `docs/SCHEMA_NOTES.md`: a parallel session
   independently built the same comparison; the two agreed bit-exactly on
   every shared construction after two bugs were found and patched. Queue
   item context: the WIC monthly-gate trap is now documented and fixed in
   `pipeline/compute_counterparts.py::build_sim` — your item 10's
   "confirm zero WIC targets" stands, and the out-of-sample WIC agreement now
   has independent-recompute backing.
2. `calibration_relationship` is now structural on every row of
   `data/comparison.json`: `consumed_as_target | seed_source | held_out`
   with a `calibration_basis` string. Use it: for each diagnosis, state
   whether the divergence (or agreement) is on a consumed, seeded, or
   held-out quantity — consumed-target agreement is a tautology, and a
   divergence ON a consumed target (e.g. queue item 9, Alaska SNAP) is a
   calibration-machinery finding, not a model-eligibility finding.
3. Do NOT work on the 2026 projection column or the interchange's 2026
   fullpart gate question — that adjudication runs in a separate lane.
4. `data/comparison.json` was rebuilt since the brief; row shapes gained
   `calibration_relationship`, `calibration_basis`, `pe_value_2026`.
   The ten queue items and all their numbers are unchanged.
