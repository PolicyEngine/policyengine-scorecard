# Divergence diagnosis batch 1 progress

## State

Diagnosis batch 1 is complete within the task constraints on branch `diagnosis-batch-1`. Both deliverables passed independent review and final consistency checks. One requested evidence point remains explicitly blocked: the actual TY2023 ACTC claim count is not present in trustworthy local sources, network use is prohibited, and the apparent local 17,312,260 row is proven TY2022. The audit remained restricted to static code and supplied data; no microsimulation runs were made. The separate 2026 projection/full-participation adjudication remained out of scope.

## Done

- Read the `gitnexus-debugging` workflow and began the two required methodology/mechanics documents.
- Confirmed the certified stack and the distinction between record-level take-up flags, formula eligibility, and soft calibration targets.
- Confirmed the worktree was clean before beginning.
- Finished `docs/replication-assessment.md` and `docs/mechanics-audit.md`, including the program formulas, current Build P target surface, and evidence-citation conventions.
- Read the shipped annotation registry and runtime-recorded variable/toggle metadata.
- Read `docs/RECONCILIATION.md` and `docs/SCHEMA_NOTES.md`; incorporated the independent bit-exact recomputation, the corrected monthly WIC gate, and the unit/construction safeguards.
- Confirmed `calibration_relationship` and `calibration_basis` are structural row fields in the rebuilt comparison and must govern whether a result is consumed, seeded, or held out.
- Attempted the required remote refresh; network access is disabled, but the locally tracked `origin/main` commit is already merged into this branch.
- Audited queue items 1–10 defensively against certified engine code, Populace source stages and release diagnostics, Ledger administrative series, and the supplied scorecard JSON.
- Quantified the SNAP annual-person/average-month mismatch, TANF target and state-support failures, EITC/ACTC administrative anchors, SSI age-shape error, housing rate decomposition, both PE full-participation variants, Alaska SNAP saturation, and the held-out WIC age offsets.
- Confirmed that the Early Head Start valuation defect contributes exactly zero to the scorecard's SPM poverty result because the certified `spm_unit_benefits` list omits both Head Start variables.
- Rejected `17,312,260` as a TY2023 ACTC count: its underlying `22incd.csv` source is TY2022 despite a generated artifact's incorrect period label. No trustworthy local TY2023 count is available under the no-network constraint.
- Used the rebuilt comparison at local commit `c80b6c4` as the authoritative calibration-relationship layer because the merged working-tree copy predates those two structural fields; the ten queued values are unchanged.
- Wrote `diagnosis/diagnoses.json` with ten ordered records, complete deliverable keys, evidence-backed classifications, metric-specific calibration relationships, quantification, fix drafts, and open questions; validated its JSON syntax, IDs, keys, evidence presence, and split sum.
- Wrote `diagnosis/DIAGNOSES.md`, ordered by maintainer priority, with explicit PE remediation, Urban-facing requests, calibration interpretation, the WIC holdout exhibit, and audit limitations.
- Completed three independent read-only reviews. Removed a housing flag-mass calculation sourced outside the brief's permitted files, recomputed the housing split from one rounded-rate basis, softened unsupported SSI and Alaska causal bounds, reclassified the WIC age offset as a medium-confidence held-out PE gap, and made Build P-era Populace commit references explicit.
- Revalidated JSON syntax, IDs, exact keys, field types, classification/fix-draft mapping, split sum, citation residues, housing arithmetic, and whitespace; the post-fix independent delta review returned clean.

## Next

- No in-scope work remains.
- When a trustworthy TY2023 IRS SOI Historic Table 2 N11070 source becomes locally available, replace the explicit item 4 blocker and recheck its confidence; do not use the mislabeled `22incd.csv` value.
