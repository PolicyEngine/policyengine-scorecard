# OBR costings lane progress

Updated: 2026-08-16

## State

In progress. The external harvest, campaign precedent, ingest contract,
architecture, and existing comparison seam have been read. Engine and harvest
research is complete enough to build the registry without guessing parameter
paths or OBR row identities. The first 20-measure registry is built and
validated against the installed engine and harvested row identities.

## Done

- Confirmed the worktree was clean and based on `fd817b9`.
- Read the local lane brief and recorded its descriptive-comparison doctrine,
  certified-artifact traceability requirement, and offline-only constraint.
- Confirmed that GitNexus is not exposed for this checkout; source files will
  be inspected directly.
- Read `uk_obr/NOTES.md`: PMD values use the Treasury convention that a
  positive sign is a gain to the Exchequer; tax rows use `revenue_change`,
  while spending rows retain that same sign as proposed `exchequer_impact`.
- Read all 95 Table 3.17 rows and extracted the eight component line items and
  the non-independent subtotal/total lines.
- Read the named 2023–2025 PMD measures and retained their verbatim
  `reform_hint`, complete harvested head sets, fiscal windows, and condition
  vocabulary.
- Read the campaign staging precedent and `ingest_campaign.py`. The existing
  campaign ingestor deliberately rejects UK family `obr`; a future UK joiner
  is owned outside this lane.
- Confirmed `build_comparison.py` is Urban-specific, so the OBR lane will use a
  standalone descriptive comparison renderer.
- Verified the core PolicyEngine UK parameter paths and aggregate-variable
  entities against the installed 2.89.2 system rather than inferring names.
- Built `data/uk/obr_measure_reforms.yaml` with eight Table 3.17 components and
  twelve named PMD measures. Every non-null reform path resolves through
  `CountryTaxBenefitSystem().parameters`, every mapped variable exists, and
  every mapped head resolves to exactly one harvested row per available FY
  once verbatim measure identity is included.

## Next

- Build and validate the measure registry, then the compute/staging pipeline,
  comparison renderer, and tests in coherent committed steps.
- Run only the requested bounded offline smoke sample, then record measured
  wall time, peak memory, results, uncertainties, and unverified items here.

## Registry counts

- `expressible`: 8
- `partial`: 8
- `not_expressible`: 4
- Total: 20

## Smoke results

Not yet run.

## Uncertainties and offline limitations

- The private #54/#55 issue bodies and #48 PR body could not be read from the
  checkout. Vocabulary explicitly summarized in the lane brief (`gbp`, `fy`,
  and `basis`) will be followed without changing `scorecard_db/models.py`.
- Table 3.17 rows do not carry `fiscal_event`, `tax_head`, `costing_phase`, or
  `sign_convention`; their actual conditions are `geography`, `fy`, `basis`,
  `line_item`, and `note`. Staging must preserve that exact source shape.
- PMD `source + metric + period + conditions` is not unique because the
  verbatim measure description is top-level `reform_hint`. The prescribed
  descriptor will be emitted, but this lane's exact resolver must additionally
  require `obr_description == reform_hint` and `source_table`. Claim-ID or
  reform-aware UK attachment remains work for the future UK ingestor.
- PMD spending rows currently carry `proposed_metric: exchequer_impact`, not a
  `metric` field. This lane treats `exchequer_impact` as the adopted staging
  vocabulary summarized by the brief and preserves the raw condition keys.
- “AB2025 measures” is not a unique harvest subset (39 descriptions touch an
  income-tax, NICs, or welfare head). The registry scope will use the three
  measures unambiguously named by the brief: personal/equivalent-NI threshold
  extension, employer secondary-threshold extension, and two-child removal.
- The Table 3.17 PA/HRT reversal uses published Table 3.19 indexed levels.
  The requested £12,570→£13,070 PA smoke value is a separate engine-path
  diagnostic, not the full OBR counterfactual, and will be reported as such.
- PE-UK has no Employment Allowance or firm entity, so both AB2024 employer-NI
  entries omit the allowance increase and eligibility-test removal and are
  marked partial.
- The certified bundle freezes PA/HRT and the employer secondary threshold
  through 2030 but resumes uprating other equivalent NI thresholds earlier.
  The combined AB2025 threshold extension is therefore marked partial rather
  than assuming a policy world the loaded parameter schedules do not contain.
