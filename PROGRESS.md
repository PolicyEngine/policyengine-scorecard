# OBR costings lane progress

Updated: 2026-08-17

## State

Follow-up 5 is in progress on branch `obr-costings-mode2` from
`22718bfb1e257b51f294eec1d33a6ac83f2049e3`. The round-4 review has been read
in full. Work is now tracing and hardening restage as a byte-bound replay; no
managed simulation will be constructed.

## Done

- Started Follow-up 5 by reading the complete round-4 review before inspecting
  or changing implementation code.
- Verified the checkout was clean, on `obr-costings-mode2`, and exactly at
  `22718bfb1e257b51f294eec1d33a6ac83f2049e3`.
- Read the GitNexus debugging workflow. Its graph tools are not exposed in this
  session, so source, manifest, artifact, and test paths will be traced
  directly.
- Fixed round-4 findings 2 and 4: restage resolves every manifest, registry,
  claims, artifact-directory, artifact, staged, and comparison path before
  referenced-input parsing; rejects absolute recorded paths, containment
  escapes, and canonical role collisions; and uses exclusive temporary writes.
- Fixed round-4 finding 5: manifests record an explicit `staged` boolean and
  restage rejects `staged: false` immediately as a non-replayable `--no-stage`
  run. The committed replay manifest now records `staged: true`.
- Path/containment/no-stage verification passes 12 targeted replay cases, and
  Python compilation plus `git diff --check` pass.
- Started Follow-up 4 by reading the complete round-3 review before inspecting
  or changing implementation code.
- Verified the checkout was clean, on `obr-costings-mode2`, and exactly at
  `59fa323309abb827aba1afa8da737aed51b85694`.
- Read the GitNexus debugging and CLI workflows. The repository has no local
  GitNexus index, so an offline index refresh is the next diagnostic step.
- The offline GitNexus analysis parsed the repository but sandbox policy
  blocked its registry write; direct source/test tracing completed instead.
- Fixed round-3 finding 1: restage now hashes the current claims bytes before
  parsing or reconstructing any row, rejects every mismatch with expected and
  actual hashes plus a new-run instruction, and has no drift bypass.
- Fixed round-3 finding 2: artifact rederivation locates current claims by the
  frozen six-key descriptor first, distinguishes missing from ambiguous rows,
  recursively names all drift, and tests all 35 observed frozen leaf fields.
- Claim-provenance regressions pass: 38 passed, 48 deselected.
- Fixed round-3 finding 3: lag years are derived independently for each
  dividend/main threshold pair, and a one-path catch-up fake reports only that
  path's 2024–2025 overrides as unnecessary. All three dividend tests pass.
- Fixed round-3 finding 4: every relative recorded path is resolved and must
  remain beneath the artifact root; an existing outside claims file reached
  through `..` is rejected. All three restage tests pass.
- Exact default `--dry-run` validated 26 measures and 215 source head-years and
  reported that no managed microsimulation was constructed.
- Exact `--restage` read 13 artifacts including one diagnostic, wrote 20 staged
  and 26 comparison rows, and reported zero managed simulations.
- Staged JSONL, comparison CSV, and comparison Markdown SHA-256 values were
  byte-identical before and after restage: `45faa64a`, `3f8fe4c1`, and
  `8c291b6b`, respectively.
- Final verification passes all 88 focused OBR tests and all 255 repository
  tests. The sole warning is the upstream PolicyEngine-UK Pydantic deprecation.
- A final independent audit found that comparison rendering reopened the claims
  path after its SHA gate. Restage now rechecks the SHA before any output write
  and renders comparison rows only from the verified in-memory claims.
- Artifact claims-hash mismatches now name expected and actual hashes and
  instruct a new compute run. Three targeted restage/comparison tests pass,
  including a mutation injected during artifactless-row reconstruction.
- Post-audit verification repeated the exact 26-measure dry run, 13-artifact
  restage, three byte-identity checks, 88 focused tests, and 255 full-suite
  tests with the same results and sole upstream warning.
- Started Follow-up 3 by reading this progress record and the complete round-2
  review before inspecting or changing the implementation.
- Verified the checkout was clean, on `obr-costings-mode2`, and exactly at
  `52c9f952f6ca87263d81e69bbaa3ef21310628fb`.
- Confirmed GitNexus graph tools are still not exposed in this checkout, so
  the eight findings will be traced directly through source, registry data,
  artifacts, and tests.
- Fixed round-2 finding 7 in this register: the Follow-up 2 report was removed
  from the branch in `8c1d858` and kept outside the repository; it is not a
  committed current-tree file (`PROGRESS.md:396`).
- Fixed round-2 finding 1: production-path tests now prove
  `run_managed_simulation` rejects a dataset mutated during `calculate`, writes
  no artifact, and aborts an already-mismatched file before construction; SHA
  errors name expected and actual hashes
  (`pipeline/compute_uk_obr_costings.py:584`,
  `tests/test_obr_costings_registry.py:488`).
- Fixed round-2 finding 6: new artifacts always require dataset hashes, while
  restage admits missing hashes only for the 13 exact paths recorded in
  `legacy_artifacts_without_dataset_hashes`; old-looking caller run ids grant
  no exception (`pipeline/compute_uk_obr_costings.py:886`,
  `results/uk/obr_costings/RUN_MANIFEST.json:17`,
  `tests/test_obr_costings_registry.py:611`).
- Fixed round-2 finding 3: the default claims input is the repo-vendored,
  byte-identical 621-row operational slice covering every registry measure and
  source period; default all-26 `--dry-run` passes, and the manifest records
  only its repo-relative path and SHA-256
  (`pipeline/compute_uk_obr_costings.py:38`,
  `results/uk/obr_costings/RUN_MANIFEST.json:103`).
- Fixed round-2 finding 2: every artifact now carries the claims SHA and a
  complete 17-field frozen source snapshot; restage recursively rejects every
  differing dotted field without replacement. Follow-up 4 then made the
  claims-file hash immutable during every restage
  (`pipeline/compute_uk_obr_costings.py:260`,
  `pipeline/compare_uk_obr_costings.py:212`,
  `tests/test_obr_costings_registry.py:1333`).
- Fixed round-2 finding 5: dividend-lag overrides now apply only to threshold
  paths whose schedules overlap the installed 2024–2025 lag, leaving the two
  genuinely affected measures (`data/uk/obr_measure_reforms.yaml:585`,
  `tests/test_obr_costings_registry.py:267`).
- Fixed round-2 finding 8: `start_fy` now means the first nonzero harvested
  costing year, all 26 values are validated against the complete vendored
  slice, and 11 incorrect entries are corrected
  (`data/uk/obr_measure_reforms.yaml:4`,
  `pipeline/compute_uk_obr_costings.py:423`).
- Fixed round-2 finding 4: restage reconstructs selected null-reform rows from
  persisted run facts, permits empty artifact inventories, and validates exact
  source-backed `(measure, year)` coverage; the all-26 round-trip proves 21
  artifact-backed and 5 reconstructed measure keys twice byte-identically
  (`pipeline/compute_uk_obr_costings.py:1710`,
  `tests/test_obr_costings_registry.py:1435`).
- Final exact default `--dry-run` validated all 26 measures and 215 mapped
  head-years from the 621-row vendor; final `--restage` read 13 artifacts,
  wrote 20 staged and 26 comparison rows, and reported zero managed sims.
- The staged JSONL, comparison CSV, and comparison Markdown are byte-identical
  to their `52c9f95` versions; only required artifact/manifest provenance
  metadata changed. Final verification passes 51 focused OBR tests and all
  218 repository tests, with only the upstream PolicyEngine-UK Pydantic warning.
- Read this progress record and the clean-context review before inspecting or
  changing the implementation.
- Verified the checkout was clean, on `obr-costings-mode2`, and exactly at
  `7222976e2cb38c8318f0ca085026bcf319d986f2`.
- Confirmed GitNexus graph tools are not exposed in this checkout, so the six
  findings are being traced directly through source, registry data, artifacts,
  and tests.
- Fixed finding 5 by removing the aggregate sign-concordance register headline;
  the progress record and tests retain row-level values and descriptive bins.
- Fixed finding 1 for all future managed runs: the exact resolved
  `runtime_dataset_source` is SHA-256 checked against the release manifest
  immediately before each simulation is constructed and immediately after its
  aggregates are read. The simulation-reported path must also equal the path
  that was hashed, and any mismatch aborts before artifact emission.
- Follow-up 2 introduced `dataset_sha256_before` and
  `dataset_sha256_after` for new simulations. Follow-up 3 replaced its former
  run-id date exception with the exact 13-path manifest allowlist.
- Fixed finding 2 by extending every staged `external_claim_match` to the
  complete six-key identity: `source`, adopted `metric`, `period`, verbatim
  `source_table`, verbatim `reform_hint`, and the full `conditions` mapping.
  The comparison resolver now uses only those descriptor keys.
- Follow-up 2 first vendored the 215 mapped head-year lines. Follow-up 3
  expanded that predecessor into the complete 621-row registry-measure slice,
  preserving source order and exact source bytes.
- The future UK ingestor work in #33/#48 must accept `source_table` and
  `reform_hint` as supported match keys. This lane does not modify
  `scorecard_db/`.
- Fixed finding 3 by replacing blanket OBR mechanism labels with row-level
  harvested facts: verbatim `source_model`, verbatim `basis`, and
  `behavioural_adjustment = unstated in harvest`. PE annotations retain only
  code-backed construction, timing, head-scope, and unexplained-remainder
  statements.
- Documented the employer-NIC incidence mechanism from installed code:
  `employee_incidence` is 1 and
  `employer_ni_fixed_employer_cost_change` adjusts wages while employer cost is
  fixed. The affected rows cite both package-relative source paths and explain
  the non-zero PE Income-tax head.
- Fixed finding 4 by marking `child_benefit` as a PROVISIONAL PE mapping for
  the harvested “Welfare inside cap” head. The row is explicit that the harvest
  identifies neither a programme nor mechanism, while fixed PE
  `would_claim_child_benefit` makes the static PE delta zero.
- Restaging refreshed the 12 non-diagnostic artifacts' matched claim snapshots
  with harvested `source_model` and current registry notes. Legacy dataset hash
  fields remain absent; no hash was invented and no simulation ran.
- Follow-up 2 added year-keyed dividend `computability_overrides`; Follow-up 3
  narrowed them to the two threshold schedules that actually overlap 2024–25.
- The engine-sensitive test reads the installed main/dividend higher and
  additional thresholds. On pe-uk 2.89.2 it observes 37,700/125,140 versus
  37,500/150,000 in 2024–2025, equality from 2026, and requires override years
  to equal that lag set exactly. A future engine correction therefore makes
  the stale override test fail until the registry is updated.
- Ran the final artifact-only `--restage`: 13 existing artifacts (one
  diagnostic), 20 staged rows, 26 comparison rows, and zero managed
  simulations. A clean worktree afterward confirms byte-idempotent outputs.
- Independently compared all 26 pre/post comparison row identities, OBR/PE
  values, signed ratios, and bins; they are unchanged. Only descriptors,
  sourced axes, and annotations changed.
- Follow-up 2 verification passed 44 focused OBR cases and all 211 repository
  tests. Its only warning was the upstream PolicyEngine-UK Pydantic deprecation.
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
- Replaced the false literal-direction annotation with the code-backed reversal
  identity: `measure Δ = −(reversal − baseline)`.
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

- Bind manifests and artifacts to registry bytes and freeze every
  output-driving registry field, retaining the exact legacy-artifact path.
- Add ordinal claim identity and mutation-specific frozen-field diagnostics,
  run exact dry-run/restage byte-identity checks without simulations, then run
  focused and full suites.

- Clean-context review can now re-check all eight resolved round-2 findings.
- The future UK ingestor in #33/#48 must add the two new descriptor match keys
  before these rows are attached to the campaign database.
- Remove the 2024–2025 dividend overrides when an installed PE-UK release fixes
  policyengine-uk#1822; the version/date-sensitive test will flag that change.
- Run the full selected population only after the review gate; it remains
  outside this no-simulation follow-up.

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
`measure Δ = −(reversal − baseline)`. Harvested source model, basis, unstated
behavioural adjustment, head scope, and unexplained remainder remain explicit.

| Measure | FY | Scope | OBR £bn | PE £bn | PE/OBR | Bin | OBR source_model / basis / behavioural_adjustment | Measure-specific annotation |
|---|---:|---|---:|---:|---:|---|---|---|
| PA and HRT freezes | 2026-27 | OBR total | +34.010 | +47.681 | 1.402 | same_sign_ratio_1.25_to_2 | obr_efo_forecast / unstated / unstated in harvest | Table 3.17 bundled line; published indexed PA/HRT reversal |
| PA and HRT freezes | 2027-28 | OBR total | +38.475 | +53.452 | 1.389 | same_sign_ratio_1.25_to_2 | obr_efo_forecast / unstated / unstated in harvest | Table 3.17 bundled line; published indexed PA/HRT reversal |
| Additional-rate threshold reduction | 2026-27 | OBR total | +0.940 | +1.840 | 1.957 | same_sign_ratio_1.25_to_2 | obr_efo_forecast / unstated / unstated in harvest | Table 3.17 threshold reversal |
| Additional-rate threshold reduction | 2027-28 | OBR total | +0.970 | +1.933 | 1.993 | same_sign_ratio_1.25_to_2 | obr_efo_forecast / unstated / unstated in harvest | Table 3.17 threshold reversal |
| SB2024 Class 1 employee NICs cut | 2026-27 | Mapped total | -9.129 | -11.965 | 1.311 | same_sign_ratio_1.25_to_2 | hmt_scorecard_obr_database / forecast / unstated in harvest | Income tax + NICs + welfare-inside-cap only; partial head scope |
| SB2024 Class 1 employee NICs cut | 2027-28 | Mapped total | -9.244 | -12.247 | 1.325 | same_sign_ratio_1.25_to_2 | hmt_scorecard_obr_database / forecast / unstated in harvest | Income tax + NICs + welfare-inside-cap only; partial head scope |
| SB2024 HICBC threshold/taper | 2026-27 | Mapped total | -0.641 | -1.721 | 2.684 | same_sign_ratio_at_least_2 | hmt_scorecard_obr_database / forecast / unstated in harvest | PROVISIONAL child_benefit mapping; harvest names no programme/mechanism; fixed PE claiming makes its delta zero |
| SB2024 HICBC threshold/taper | 2027-28 | Mapped total | -0.647 | -1.844 | 2.850 | same_sign_ratio_at_least_2 | hmt_scorecard_obr_database / forecast / unstated in harvest | PROVISIONAL child_benefit mapping; harvest names no programme/mechanism; fixed PE claiming makes its delta zero |
| AB2024 employer NICs package | 2026-27 | Mapped total | +23.610 | +16.247 | 0.688 | same_sign_ratio_0.5_to_0.8 | hmt_scorecard_obr_database / forecast / unstated in harvest | Income tax + NICs only; employee incidence 1 and fixed-employer-cost wage adjustment; other heads excluded |
| AB2024 employer NICs package | 2027-28 | Mapped total | +24.027 | +16.422 | 0.683 | same_sign_ratio_0.5_to_0.8 | hmt_scorecard_obr_database / forecast / unstated in harvest | Income tax + NICs only; employee incidence 1 and fixed-employer-cost wage adjustment; other heads excluded |
| AB2025 remove UC two-child limit | 2026-27 | Welfare inside cap | -1.887 | -1.104 | 0.585 | same_sign_ratio_0.5_to_0.8 | hmt_scorecard_obr_database / forecast / unstated in harvest | UC inside-cap aggregate only; outside-cap OBR head excluded |
| AB2025 remove UC two-child limit | 2027-28 | Welfare inside cap | -2.101 | -1.182 | 0.563 | same_sign_ratio_0.5_to_0.8 | hmt_scorecard_obr_database / forecast / unstated in harvest | UC inside-cap aggregate only; outside-cap OBR head excluded |

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
- PMD `source + metric + period + conditions` alone is not unique. Staged
  descriptors now also carry the harvested `source_table` and verbatim
  `reform_hint`; this six-key identity resolves each mapped row exactly once.
  The future UK ingestor in #33/#48 must support those two match keys before
  campaign-database attachment.
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
- PE-UK 2.89.2 keeps dividend higher/additional band thresholds at
  £37,500/£150,000 in 2024–2025 while the main bands are £37,700/£125,140. The
  two registry reforms whose dividend-threshold schedules overlap those years
  carry year-specific `partial` overrides; policyengine-uk#1822 tracks the lag.
- The exact pre-policy salary-sacrifice cap is infinity, which cannot be stored
  in standards-compliant JSON. The partial reversal uses a finite `1e100` cap
  and zeroes the fixed 0.16% broad-base haircut; installed formulas show this
  is uncapped for modeled contributions, but it is not claimed as a literal
  infinity-valued reform.
- `child_benefit` is only a PROVISIONAL PE mapping for HICBC's harvested
  “Welfare inside cap” head; the harvest identifies neither a programme nor a
  mechanism. Fixed `would_claim_child_benefit` makes the PE static delta zero.
- Only the requested six-measure/two-year sample ran. No PE value is claimed
  for the other registry entries, and the full population remains unverified.
- PMD includes allocations in years that precede the modeled policy-effective
  date for some descriptions. The pipeline preserves those source rows rather
  than suppressing them; why each OBR allocation appears there is unexplained.
- The smoke differences beyond harvested source model/basis, PE construction,
  timing, and head scope are unexplained. No causal explanation is inferred
  from ratio magnitude.
- The first smoke attempt wrote no run artifact and stopped before simulation
  when PyTables found the certified HF-cache file read-only. The successful
  run used a SHA-verified, ignored writable mirror of those same cached bytes;
  no download was attempted. Portability of that mirror path outside this
  checkout was not tested.
- The Follow-up 2 report was kept outside this repository after the designated
  parent output path proved unwritable; commit `8c1d858` removed the temporary
  in-repository copy.
