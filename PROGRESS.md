# OBR costings lane progress

Updated: 2026-08-17

## State

Follow-up 2 is in progress from clean branch `obr-costings-mode2` at requested
HEAD `7222976`. The six clean-context review findings are being fixed offline.
The existing 13 certified run artifacts will only be read through `--restage`;
no managed simulation will be constructed and the full 26-measure population
remains intentionally unrun.

## Done

- Read this progress record and the clean-context review before inspecting or
  changing the implementation.
- Verified the checkout was clean, on `obr-costings-mode2`, and exactly at
  `7222976e2cb38c8318f0ca085026bcf319d986f2`.
- Confirmed GitNexus graph tools are not exposed in this checkout, so the six
  findings are being traced directly through source, registry data, artifacts,
  and tests.
- Removed the aggregate sign-concordance register headline; the progress record
  retains only row-level values and descriptive bins.
- Fixed finding 1 for all future managed runs: the exact resolved
  `runtime_dataset_source` is SHA-256 checked against the release manifest
  immediately before each simulation is constructed and immediately after its
  aggregates are read. The simulation-reported path must also equal the path
  that was hashed, and any mismatch aborts before artifact emission.
- New artifacts record `dataset_sha256_before` and `dataset_sha256_after` for
  both baseline and reform simulations beside their bundle identities. The 13
  committed artifacts retain no invented hashes during `--restage`; their
  absence is accepted only because run id `campaign-20260816-obr-costings`
  predates the field's 2026-08-17 introduction. A fake-file mutation test
  exercises the before/after rejection.
- Started Follow-up 1 from clean branch `obr-costings-mode2` at `b6442fe` and
  read this progress record plus both compute/comparison modules end to end.
- Confirmed the orientation defect is confined to artifact/staging derivation:
  raw aggregates were intact, but the exchequer-gain reversal delta had been
  stored and compared as `pe_value` without the measure-facing sign flip.
- Confirmed GitNexus graph tools remain unavailable in this checkout and traced
  the staging-to-artifact comparison invariant directly in source.
- Centralized the staging identity in `orient_exchequer_effect`: tax uses
  `G = +(reform - baseline)`, spending uses `G = -(reform - baseline)`, and
  `pe_value` is `-G` for a certified-world reversal or `+G` for a forward
  construction. Unit tests cover both constructions and both channels.
- Preserved every artifact's raw baseline/reform aggregates and raw aggregate
  delta. Reversal heads now record `reversal_delta_exchequer_gain`; the forward
  diagnostic records `forward_delta_exchequer_gain`; artifact and staged
  `pe_value` are measure-oriented.
- Added `--restage`, which reads only the manifest-listed artifacts, validates
  their registry/run/head/raw-aggregate identities, re-derives all values, and
  writes staging and comparison outputs before any PolicyEngine import, cache
  preflight, or simulation path. The synthetic test proves a second restage is
  byte-for-byte idempotent.
- Ran `--restage` twice against the 13 existing artifacts. Each invocation
  produced 20 staged and 26 comparison rows and reported zero managed
  simulations; the second invocation left an identical diff hash.
- Replaced the false literal-direction annotation with: “Reversal leg on the
  certified world, re-oriented to the announced measure: measure Δ =
  −(reversal − baseline).” Static/behavioural, certified-world/announcement-
  baseline, calendar-year/fiscal-year, head-scope, and unexplained-remainder
  axes remain explicit.
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
  totals.
- Built `pipeline/compare_uk_obr_costings.py`. It produces head-level CSV and
  Markdown rows with signed PE/OBR ratios, descriptive bins, and named model,
  adjustment, baseline, timing, and head-scope axes; any remainder is labelled
  `unexplained`. For PMD measures with at least two computed mapped heads, it
  adds a comparison-only mapped-head sum that is explicitly not an external
  TOTAL claim. No score-like summary statistic is produced.
- Ran the requested smoke sample offline against certified build
  `populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z` (PolicyEngine 5.0.2,
  PolicyEngine UK 2.89.2, bundle `uk-5.0.2`). The run produced 13 per-run JSON
  artifacts (12 staged measure-years plus one diagnostic), 20 staged head/total
  rows, and 26 comparison rows including six comparison-only mapped-head
  totals.
- Traced all 20 non-null staged PE values to exactly one head in exactly one
  saved artifact and to the artifact's frozen source snapshot. The committed
  test also checks the full bundle id, engine version, run id, measure, year,
  raw aggregates, and diagnostic separation.
- Re-ran the comparison renderer from the staged file and source harvest. It
  wrote `results/uk/obr_costings/COMPARISON.csv` and `COMPARISON.md`; the
  artifact/source trace audit completed successfully.
- All 33 focused cases and all 200 repository tests pass in the certified
  venv. The sole warning is an upstream Pydantic deprecation emitted by
  policyengine-uk.

## Next

- Vendor the 215 exact matched harvest rows, make staged descriptors unique,
  and test both vendored and optional full-harvest joins.
- Replace unsupported row mechanisms with harvested/code-backed axes, correct
  the provisional HICBC welfare mapping, and add the employer-NIC incidence
  mechanism from installed source.
- Add and validate the per-year dividend-threshold computability overrides.
- Restage without simulations, regenerate comparisons, run focused and full
  tests, then write the final report.

## Registry counts

- `expressible`: 3
- `partial`: 18
- `not_expressible`: 5
- Total: 26

## Smoke results

Original certified run command (not rerun for Follow-up 1; the managed calls
were serial, with one baseline retained only as aggregates per year):

```text
/Users/maxghenis/scorecard-lanes/.venv-obr/bin/python \
  pipeline/compute_uk_obr_costings.py \
  --measures efo_march_2026__pa_and_hrt_freezes \
  efo_march_2026__additional_rate_threshold_reduction \
  spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp \
  spring_budget_2024__hicbc_threshold_and_taper \
  autumn_budget_2024__employer_nics_package \
  autumn_budget_2025__uc_child_element_remove_two_child_limit \
  --years 2026 2027 --limit 6 --pa-smoke-probe
```

Follow-up 1 restage command:

```text
/Users/maxghenis/scorecard-lanes/.venv-obr/bin/python \
  pipeline/compute_uk_obr_costings.py --restage
```

It read the 13 existing per-run artifacts, staged 20 rows, rendered 26
comparison rows, and constructed zero managed simulations.

The values below are GBP billions in the harvested
`positive_gain_to_exchequer` convention. “Mapped total” sums only the OBR heads
listed in the annotation; it is not an OBR TOTAL claim. Every row has
`benchmark_class = different_model`, uses PE calendar year Y as the proxy for
FY Y-(Y+1). Each reversal leg on the certified world is re-oriented to the
announced measure using
`measure Δ = −(reversal − baseline)`. The certified-world versus announcement-
baseline axis, head scope, and unexplained remainder remain explicit.

| Measure | FY | Scope | OBR £bn | PE £bn | PE/OBR | Bin | Measure-specific annotation |
|---|---:|---|---:|---:|---:|---|---|
| PA and HRT freezes | 2026-27 | OBR total | +34.010 | +47.681 | 1.402 | same_sign_ratio_1.25_to_2 | Table 3.17 bundled line; published indexed PA/HRT reversal |
| PA and HRT freezes | 2027-28 | OBR total | +38.475 | +53.452 | 1.389 | same_sign_ratio_1.25_to_2 | Table 3.17 bundled line; published indexed PA/HRT reversal |
| Additional-rate threshold reduction | 2026-27 | OBR total | +0.940 | +1.840 | 1.957 | same_sign_ratio_1.25_to_2 | Table 3.17 threshold reversal |
| Additional-rate threshold reduction | 2027-28 | OBR total | +0.970 | +1.933 | 1.993 | same_sign_ratio_1.25_to_2 | Table 3.17 threshold reversal |
| SB2024 Class 1 employee NICs cut | 2026-27 | Mapped total | -9.129 | -11.965 | 1.311 | same_sign_ratio_1.25_to_2 | Income tax + NICs + welfare-inside-cap only; partial head scope |
| SB2024 Class 1 employee NICs cut | 2027-28 | Mapped total | -9.244 | -12.247 | 1.325 | same_sign_ratio_1.25_to_2 | Income tax + NICs + welfare-inside-cap only; partial head scope |
| SB2024 HICBC threshold/taper | 2026-27 | Mapped total | -0.641 | -1.721 | 2.684 | same_sign_ratio_at_least_2 | Income tax + welfare-inside-cap; fixed PE claiming makes child-benefit delta zero |
| SB2024 HICBC threshold/taper | 2027-28 | Mapped total | -0.647 | -1.844 | 2.850 | same_sign_ratio_at_least_2 | Income tax + welfare-inside-cap; fixed PE claiming makes child-benefit delta zero |
| AB2024 employer NICs package | 2026-27 | Mapped total | +23.610 | +16.247 | 0.688 | same_sign_ratio_0.5_to_0.8 | Income tax + NICs only; no Employment Allowance/firm mechanics; other OBR heads excluded |
| AB2024 employer NICs package | 2027-28 | Mapped total | +24.027 | +16.422 | 0.683 | same_sign_ratio_0.5_to_0.8 | Income tax + NICs only; no Employment Allowance/firm mechanics; other OBR heads excluded |
| AB2025 remove UC two-child limit | 2026-27 | Welfare inside cap | -1.887 | -1.104 | 0.585 | same_sign_ratio_0.5_to_0.8 | UC inside-cap aggregate only; outside-cap OBR head excluded |
| AB2025 remove UC two-child limit | 2027-28 | Welfare inside cap | -2.101 | -1.182 | 0.563 | same_sign_ratio_0.5_to_0.8 | UC inside-cap aggregate only; outside-cap OBR head excluded |

The separate diagnostic changed the 2026 personal allowance from £12,570 to
£13,070. Baseline income tax was £421.891913bn and the static income-tax delta
was exactly -£4,475,428,181.94, or -£4.48bn rounded as required. This diagnostic
has its own artifact and is not staged against an OBR claim.

### Smoke performance

Follow-up 1 restaging took 1.5 seconds and constructed no simulation. The
unchanged original end-to-end run took 798.504 seconds (13m 18.5s). Its fifteen
managed sims accounted for 783.002 seconds: two reused baselines, twelve
measure-year reforms, and one diagnostic. Peak memory is sampled process RSS,
not an incremental allocation. Cleanup and `gc.collect()` ran after every
reform.

| Simulation | Year | Wall seconds | Peak RSS GiB |
|---|---:|---:|---:|
| Baseline | 2026 | 31.402 | 20.429 |
| Baseline | 2027 | 30.783 | 20.778 |
| PA and HRT freezes | 2026 | 53.083 | 31.756 |
| Additional-rate threshold reduction | 2026 | 54.371 | 25.717 |
| SB2024 Class 1 employee NICs cut | 2026 | 60.772 | 23.472 |
| SB2024 HICBC threshold/taper | 2026 | 66.139 | 19.039 |
| AB2024 employer NICs package | 2026 | 56.375 | 26.893 |
| AB2025 remove UC two-child limit | 2026 | 59.976 | 26.318 |
| PA +£500 diagnostic | 2026 | 54.618 | 29.788 |
| PA and HRT freezes | 2027 | 55.165 | 27.529 |
| Additional-rate threshold reduction | 2027 | 49.910 | 31.891 |
| SB2024 Class 1 employee NICs cut | 2027 | 51.499 | 32.823 |
| SB2024 HICBC threshold/taper | 2027 | 51.385 | 31.905 |
| AB2024 employer NICs package | 2027 | 53.868 | 27.373 |
| AB2025 remove UC two-child limit | 2027 | 53.656 | 32.888 |

Maximum sampled process RSS was 32.888 GiB.

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
- Only the requested six-measure/two-year sample ran. No PE value is claimed
  for the other registry entries, and the full population remains unverified.
- PMD includes allocations in years that precede the modeled policy-effective
  date for some descriptions. The pipeline preserves those source rows rather
  than suppressing them; why each OBR allocation appears there is unexplained.
- The smoke differences beyond the named model, behavioural/static,
  certified-world/announcement-baseline, timing, and head-scope axes are
  unexplained. No causal explanation is inferred from ratio magnitude.
- The first smoke attempt wrote no run artifact and stopped before simulation
  when PyTables found the certified HF-cache file read-only. The successful
  run used a SHA-verified, ignored writable mirror of those same cached bytes;
  no download was attempted. Portability of that mirror path outside this
  checkout was not tested.
