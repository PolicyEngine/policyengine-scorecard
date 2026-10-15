# Historical event registry adapter

Status: proposed design for phase 0, 11 October 2026. This slice changes no
registry builder, runner or numerical artifact. The policy-world choice and
annualisation bridge remain pending under the [policy-world
proposal](POLICY_WORLD_CONTRACT.md) and cos d1344.

The adapter should retain every original source row and fiscal year, then
select an explicitly certified event population through the
[event-vintage selector](EVENT_VINTAGE_SELECTOR.md) and
[population manifest](POPULATION_MANIFEST.md). A missing population, forecast
source, policy-world decision or annualisation bridge permits source accounting
only. It must not select the modern default population to fill the gap.

## Code read and current limits

The current-worktree code was read at
`61c13e38cfe4676756a7857e4fc6f67eac33cd0c`:

| Path and lines | Observed behavior |
|---|---|
| [pipeline/build_uk_event_registry.py:105–155](https://github.com/PolicyEngine/policyengine-scorecard/blob/61c13e38cfe4676756a7857e4fc6f67eac33cd0c/pipeline/build_uk_event_registry.py#L105-L155) | Verifies the compressed and uncompressed PMD snapshot hashes; selects every matching event cell; retains its original FY, head, amount, table and column; identifies it by snapshot position and source-line digest. |
| [pipeline/build_uk_event_registry.py:171–229](https://github.com/PolicyEngine/policyengine-scorecard/blob/61c13e38cfe4676756a7857e4fc6f67eac33cd0c/pipeline/build_uk_event_registry.py#L171-L229) | Checks that each source-row identity occurs once after classification and that row counts, net GBP and absolute GBP reconcile, including within every FY. |
| [pipeline/build_uk_event_registry.py:743–749](https://github.com/PolicyEngine/policyengine-scorecard/blob/61c13e38cfe4676756a7857e4fc6f67eac33cd0c/pipeline/build_uk_event_registry.py#L743-L749) | Groups all event rows but clips `calendar_years` to FY start years 2023–2030. This clips execution, not the source-row accounting. |
| [pipeline/build_uk_event_registry.py:822–882](https://github.com/PolicyEngine/policyengine-scorecard/blob/61c13e38cfe4676756a7857e4fc6f67eac33cd0c/pipeline/build_uk_event_registry.py#L822-L882) | Adds every classified source row to its measure and records the clipped execution years, an FY-start-year proxy note, the fixed certified bundle and the complete accounting. |
| [pipeline/compute_uk_event.py:461–474](https://github.com/PolicyEngine/policyengine-scorecard/blob/61c13e38cfe4676756a7857e4fc6f67eac33cd0c/pipeline/compute_uk_event.py#L461-L474) | Requires a nonempty registry `calendar_years`, rejects any requested year before 2023 or after 2030, and rejects years outside the registry's window. |

The variant interface was read with
`git show origin/w6/replay-variants:docs/uk_replay/RELEASE_REPLAY.md`, with that
remote-tracking ref resolving locally to
`eec87f42719cc73f41774ac940f67f5e55a67dba`. This is a separate branch's
interface, not an interface implemented on this worktree's checkpoint.

At that commit,
[compute_uk_event.validate_variant_years](https://github.com/PolicyEngine/policyengine-scorecard/blob/eec87f42719cc73f41774ac940f67f5e55a67dba/pipeline/compute_uk_event.py#L561-L590)
partitions registry years using the selected variant's `data_years` and refuses
explicit requests outside them. The legacy path still uses the 2023–2030
restriction
([lines 695–704](https://github.com/PolicyEngine/policyengine-scorecard/blob/eec87f42719cc73f41774ac940f67f5e55a67dba/pipeline/compute_uk_event.py#L695-L704)).
[uk_replay_variants.supported_years](https://github.com/PolicyEngine/policyengine-scorecard/blob/eec87f42719cc73f41774ac940f67f5e55a67dba/pipeline/uk_replay_variants.py#L833-L847)
records `before_data_year` or `after_extension_end` for unsupported years;
[manifest_fields](https://github.com/PolicyEngine/policyengine-scorecard/blob/eec87f42719cc73f41774ac940f67f5e55a67dba/pipeline/uk_replay_variants.py#L878-L893)
records the supported grid separately. Staging retains an otherwise executable
source row without a counterpart as `unsupported_on_variant`
([stage_uk_event.py:401–419](https://github.com/PolicyEngine/policyengine-scorecard/blob/eec87f42719cc73f41774ac940f67f5e55a67dba/pipeline/stage_uk_event.py#L401-L419)).
These mechanisms supply the accounting and support reporting to extend; the
new selector and population-manifest join described below remains proposed.

## Original years stay in the accounting

The union of `costing_gbp_m` keys for each event in
[data/uk/events/inventory.jsonl](https://github.com/PolicyEngine/policyengine-scorecard/blob/61c13e38cfe4676756a7857e4fc6f67eac33cd0c/data/uk/events/inventory.jsonl)
was read without loading an engine:

| Event | Required scoring FYs | FYs currently excluded from execution |
|---|---|---|
| Spring Statement 2022 | 2021–22 through 2026–27 | 2021–22, 2022–23 |
| Autumn Statement 2022 | 2022–23 through 2027–28 | 2022–23 |
| Autumn Budget 2021 | 2021–22 through 2026–27 | 2021–22, 2022–23 |

The builder should derive its full source-year grid before selecting a variant.
Its source accounting must continue to reconcile every original cell, including
zeros, heads outside household scope and unsupported years. The selector's
`scoring_fys` must equal the inventory's FY union. A construction's missing
household legs or part-year effects remain named gaps on the original source
FY; they do not authorise dropping a row or moving a costing to another year.

The existing November 2025 PMD snapshot is the accounting/comparison source.
The event locks identify the separately dated forecast inputs for population
construction. The adapter must retain both identities: a later consolidated
PMD observation is not evidence that its workbook existed at the event date.
Archive capture classification and missing files come from the committed
locks; an unavailable lock entry supplies no calibration value.

## Proposed selection interface

Add explicit selector and manifest-plan inputs to the builder and runner in a
later slice. An event's manifest plan should name one resolved population
manifest per `costing_fy`, the selected variant's `variant_id` and
`identity_sha256`, and the hashes of the selector and manifests. These are
proposed inputs, not existing command-line flags. The ordinary historical
selection requires one certified variant whose data support covers all of the
event's scoring FYs.

Before importing an engine, selection should perform these checks:

1. Validate the selector and all manifests against their versioned schemas;
   recompute their commitments and every referenced lock digest using the
   collector's canonical receipt convention. Require the selected event and
   full scoring-FY list to match the inventory, and the event date to agree
   with the selector. Retain unavailable-source reasons from the locks.
2. Require a `status: "certified"` manifest for each scoring FY. All nine
   identity fields must be resolved. Each manifest's `event_slug` and
   `costing_fy` must match its position in the plan. Its
   `forecast_release_identity.selector_sha256` and `source_lock_sha256` must
   bind the selected forecast and locks; it must not substitute another EFO
   release or later forecast revision without a separately labelled selector.
3. Require `historical_survey_release.release_id` to occur in
   `admissible_survey_releases`, and its publication date to agree with the
   selector. Independently verify the licensed source receipt named by
   `historical_survey_release.source_receipt_sha256`. A vintage-faithful Spring
   Statement 2022 or Autumn Budget 2021
   build uses the selected FRS 2019–20 release. FRS 2020–21, first published
   after Spring Statement 2022, is admissible for Autumn Statement 2022 only
   among these three events; see
   [PLAN.md](PLAN.md#phases-and-effort) and
   [POPULATIONS_AND_VINTAGES.md](POPULATIONS_AND_VINTAGES.md). A later-survey
   reconstruction needs a separately labelled retrospective selector.
4. Require consistent resolved `policy_world`, historical survey and forecast
   release identities across the plan. `policy_world.contract_sha256` must
   bind the approved contract. For the published end-state option, evaluate
   the documented pre-measure counterfactual on that same population and
   weights. For the pre-measures option, require the documented level-bridge
   receipt. A `pending` contract or bridge blocks numerical execution.
5. Join the manifests to the explicitly named certified replay variant by
   `population_artifact_digest == identity.dataset.sha256`, and verify the
   certification and engine provenance described below. Version numbers or
   overlapping years alone do not establish a matched population.
6. Require the selector's full `scoring_fys` to be covered by the manifests'
   `data_years`; require each manifest's declared coverage to equal its
   certification receipt's `data_years`, in chronological order. Convert each
   FY to the runner's required input periods only through the resolved
   `annualisation_bridge`; require every resulting calendar year in the
   variant's integer `data_years`. A mismatch stops the historical run with
   an explicit reason and leaves all source rows available for accounting.

Manifest `data_years` contains FY strings; the replay-variant record's
`data_years` contains integer calendar years. They must not be compared
directly. The current FY-start-year proxy would require calendar 2021–2026
for Spring Statement 2022 and Autumn Budget 2021, and 2022–2027 for Autumn
Statement 2022. Those ranges describe the current proxy's mapping, not an
approved historical bridge. A bridge requiring two calendar periods for a
single fiscal year must check both periods. Its receipt must explain policy
commencement, annual parameter processing and the cash/liability distinction;
it cannot claim part-year coverage merely because an annual result exists.

An explicit partial-support comparison may use the variant branch's support
partition, but must list every unsupported FY and retain its source rows. It
cannot certify full historical-event coverage. Do not fall back to the default
variant, advance a year until it is supported, or replace a missing forecast
target with an outturn or later vintage. A modern-population sensitivity run
is a separately identified question under [PLAN.md](PLAN.md#where-a-single-population-gives-a-usable-labelled-answer).

## Certification binds the engine actually run

The variant branch already checks the model and wrapper versions against its
release bundle, certification against the model version and data build, and
the certified dataset digest against `identity.dataset.sha256`
([uk_replay_variants.py:303–342](https://github.com/PolicyEngine/policyengine-scorecard/blob/eec87f42719cc73f41774ac940f67f5e55a67dba/pipeline/uk_replay_variants.py#L303-L342)).
Its
[variant_preflight](https://github.com/PolicyEngine/policyengine-scorecard/blob/eec87f42719cc73f41774ac940f67f5e55a67dba/pipeline/compute_uk_event.py#L336-L366)
verifies the installed environment, isolates certification, materialises
verified dataset bytes and checks the managed release bundle. Its managed
simulation path checks the exact runtime file, dataset-year membership and
the dataset hash before and after aggregation
([compute_uk_obr_costings.py:1044–1106](https://github.com/PolicyEngine/policyengine-scorecard/blob/eec87f42719cc73f41774ac940f67f5e55a67dba/pipeline/compute_uk_obr_costings.py#L1044-L1106)).
These gates should remain in the historical runner.

The population manifest additionally requires an exact `engine_commit`.
The existing variant record checks model version rather than this commit.
A historical certification receipt therefore needs upstream provenance
binding that commit to the certified wheel or installed-content identity;
inferring a commit from a version string is insufficient. Require:

```text
manifest.engine_commit = certification_receipt.engine_commit
manifest.population_artifact_digest = certification_receipt.population_artifact_digest
manifest.population_artifact_digest = variant.identity.dataset.sha256
manifest.data_years = certification_receipt.data_years
requested FYs are covered by manifest.data_years
certified engine provenance matches the variant's verified installed engine
```

Each artifact, progress receipt and run manifest should bind the selector,
population manifests, approved bridge and policy-world contract in addition
to the existing registry, variant and dataset digests. Resume must refuse a
receipt from a different manifest or engine even if its measure and year
match. Staging should recompute the join and support grid from committed
inputs, then preserve the full source-row universe. Comparison should expose
these identities and retain descriptive timing, cash/liability, geography,
head-scope and omitted-behaviour axes. Held-out OBR measure deltas remain
comparison values, never per-measure calibration targets; the target boundary
in [docs/ARCHITECTURE.md](../ARCHITECTURE.md#what-may-never-become-a-target)
continues to apply.

## Work still required

The selector/manifest join, historical execution window and commit-bound
certification are designs, not implemented runner features. No historical
population artifact, admissible survey microdata or new certification was
obtained or inspected in this adapter slice. No population was built and no
microsimulation ran. Historical rule coverage, exact period behavior on a
future selected engine and certification of that engine/population pairing
remain unverified. Source-lock retrieval and release-byte classification are
recorded by the collector and its receipts, not asserted by this document.
