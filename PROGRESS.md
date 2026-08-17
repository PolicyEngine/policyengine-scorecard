# OBR costings lane progress

Updated: 2026-08-16

## State

In progress. The 26-measure registry, offline compute/staging pipeline,
descriptive comparison renderer, and focused test module are built. Registry
paths, aggregate variables, and harvested row identities validate without
constructing a managed simulation. The bounded smoke run remains.

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
  eighteen named PMD measures. Every non-null reform path resolves through
  `CountryTaxBenefitSystem().parameters`, every mapped variable exists, and
  every mapped head resolves to exactly one harvested row per available FY
  once verbatim measure identity is included.
- Built `pipeline/compute_uk_obr_costings.py`. It runs year-major, retains only
  aggregate floats between simulations, uses the required plain reform dict,
  records complete baseline/reform bundle metadata and raw aggregates, and
  freezes the exact matched OBR identity/value into every run artifact before
  deriving staged rows.
- Hardened the certified path: normal execution assigns all HF offline flags,
  requires a local-only cache hit, and verifies the cached 1.2 GB artifact's
  SHA-256 against the release manifest before constructing any simulation.
  The verified build id is
  `populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`.
- The first smoke invocation stopped before constructing a simulation because
  PyTables requests read/write access while the sandbox exposes the certified
  HF cache read-only. No run artifact was written. The pipeline now copies the
  same SHA-256-verified bytes to an ignored workspace-local mirror, verifies
  that copy again, and points the managed API's supported local-mirror resolver
  at it; the certified manifest URI and bundle identity remain unchanged.
- Ran `--dry-run --limit 3 --years 2026` after the final registry audit; it
  validated all 26 entries and 215 mapped head-years, constructed no managed
  simulation, and wrote no output. An earlier run with a pre-existing
  `HF_HUB_OFFLINE=0` confirmed the program overrides it to offline. A separate
  local-only cache preflight verified SHA-256
  `f17306ccb2aad7ff0130be3589b560afb2e2a12a943570911cd0c77f07934833`
  in 0.524 seconds.
- Expanded the AB2025 scope after a second code/harvest audit: dividend,
  property, and savings rates; the salary-sacrifice cap; Winter Fuel Payment;
  and the non-expressible UC standard/health protection now sit alongside the
  threshold and two-child measures. The audit also made PMD pre-effective rows
  visible, added HICBC's fixed-claiming child-benefit spending counterpart, and
  tightened partial classifications for broad welfare/head scope.
- Added focused tests for registry schema/counts, installed-engine path and
  variable resolution, the exact NICs aggregate, tax/spending signs, forced
  offline mode, exact source conditions and artifact provenance, ambiguous
  source resolution, finite JSON, null-reform selection, bundle identity, and
  an output-free offline CLI dry run. Comparison tests also cover every ratio
  boundary, artifact-backed source resolution, and explicit mapped-head-only
  totals. All 26 focused cases and all 193 repository tests pass in the
  certified venv; the only warning is an upstream Pydantic deprecation from
  policyengine-uk.
- Built `pipeline/compare_uk_obr_costings.py`. It produces head-level CSV and
  Markdown rows with signed PE/OBR ratios, descriptive bins, and named model,
  adjustment, baseline, timing, and head-scope axes; any remainder is labelled
  `unexplained`. For PMD measures with at least two computed mapped heads, it
  adds a comparison-only mapped-head sum that is explicitly not an external
  TOTAL claim. No score-like summary statistic is produced.

## Next

- Run only the requested bounded offline smoke sample, then record measured
  wall time, peak memory, results, uncertainties, and unverified items here.

## Registry counts

- `expressible`: 3
- `partial`: 18
- `not_expressible`: 5
- Total: 26

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
  income-tax, NICs, or welfare head). The registry covers the named threshold
  and two-child items plus six additional measures whose relevant mechanics
  were directly checked. It is not asserted to exhaust all 39 descriptions.
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
- The exact pre-policy salary-sacrifice cap is infinity, which cannot be stored
  in standards-compliant JSON. The partial reversal uses a finite `1e100` cap
  and zeroes the fixed 0.16% broad-base haircut; installed formulas show this
  is uncapped for modeled contributions, but it is not claimed as a literal
  infinity-valued reform.
- The HICBC welfare counterpart uses gross `child_benefit` with fixed
  `would_claim_child_benefit`; its static delta should be zero. The OBR welfare
  head includes claiming effects, so the absent PE claiming response is named.
