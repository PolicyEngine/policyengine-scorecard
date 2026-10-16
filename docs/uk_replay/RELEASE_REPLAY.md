# Replaying the event corpus on every certified release

Status: design contract for workstream W6 of the Autumn Budget 2026 CI plan,
11 October 2026. It extends the track 1 replay ([RECIPE.md](RECIPE.md),
[YEARS.md](YEARS.md)) from one hard-pinned world to any number of
**certified replay variants**, and turns each variant's run into a receipt
that release qualification (W4, policyengine.py) can consume before a
model/data pair is promoted.

The registries remain frozen. An explicit construction revision may be
selected from `data/uk/events/construction_revisions.json` by metadata in
the installed engine; its SHA-256 is bound in the run manifest and
premises, and the comparison and release diff identify it. The AB2024 CGT
revision follows W6's methodology choice under cos d1344 (Max, 15 October
2026): use the reading supported by the law and land on independent review.
Other failed premises remain revision candidates. See
[CONSTRUCTION_REVISIONS.md](CONSTRUCTION_REVISIONS.md) for the decision,
statutory citation and recorded limits.

## Why the existing runner cannot rerun

Read in code at `61c13e38`:

* `pipeline/uk_engine_registry.py` refuses any engine except `2.89.2`.
* `compute_uk_ab2025.preflight()` and `compute_uk_obr_costings.assert_engine_matches_bundle()`
  read `data/uk/certified_bundle.json`, whose only compatible model is
  `policyengine-uk ==2.89.2`, and require the installed engine to equal it.
* `modal_uk_event.py` hardcodes `ENGINE_PINS` (`policyengine 5.0.2`,
  core `3.27.1`, UK `2.89.2`), the populace Hugging Face cache layout and
  the audited HF commit.
* `compute_uk_event.validate_years` allows CY2023–2030 for every run.
* `compare_uk_event.review_diagnosis` attaches ten 2.89.2 findings to every
  row with `"engine_version": "2.89.2"` whatever engine produced the row;
  `construction_note` states 2.89.2 facts (the £3.15 Class 2 rate, "the pin
  still has the 3% surcharge scale") unconditionally.
* `diagnose_uk_event_models.investigate` refuses any engine but 2.89.2.

The newest certified pair is policyengine.py **6.2.6** (PR #555 and its
version bump `481940ec`): `policyengine-uk 2.125.1`, `policyengine-core
3.33.0`, data `policyengine-uk-data-1.58.0`, default dataset
`enhanced_frs_2024_25` (SHA-256 `5ba399ea…60b6`, 128,369,110 bytes,
`hf://policyengine/policyengine-uk-data-private/enhanced_frs_2024_25.h5@1.58.0`).

Measured on that pair on 11 October with the installed wheels (one managed
simulation, offline, no token):

* The HDF5's `time_period` table holds `["2024"]`; the managed simulation's
  `dataset.years` is `[2024, …, 2030]` (`extend_single_year_dataset`,
  `end_year=2030`, in `policyengine_uk/data/economic_assumptions.py`).
* **Calculating 2023 does not raise.** `income_tax` for 2023 sums to £0.0bn,
  against £275.5bn in 2024: the simulation has no 2023 inputs and returns
  defaults. Year support therefore has to be enforced from the data; a
  successful calculation proves nothing.
* `pe.uk.managed_microsimulation()` materialises the default dataset at
  `./data/<file>` relative to the working directory (policyengine.py
  `provenance/dataset_materialization.py`, `DEFAULT_DATA_DIR = Path("./data")`),
  reusing a file whose SHA-256 matches and otherwise downloading over HTTPS.
  The 5.0.2 HF-cache mirror path does not apply.
* With no Hugging Face token the release-manifest fetch fails and the
  wrapper uses its packaged certification (`compatibility_basis
  "legacy_compatible_model_package"`, `certified_for_model_version
  "2.125.1"`). With a token, `certify_data_release_compatibility` derives a
  certification from the remote release manifest instead, which changes
  `release_bundle` fields. The 5.0.2 audit recorded the same split
  (`OFFLINE_BUNDLE_AUDIT.json`, `release_bundle_field_changes_if_remote_manifest_is_available`).
* Peak resident memory for the baseline load plus five annual aggregates was
  2.3GB; the whole probe took 10.6s.

## Certified replay variants

`data/uk/replay_variants.json` lists every variant the corpus may run on.
`data/uk/certified_bundle.json` is unchanged and remains the legacy
variant's identity: AB2025, the OBR-costing runner and every existing
receipt keep reading it byte-for-byte.

```json
{
 "schema_version": 1,
 "default_variant": "<legacy variant_id>",
 "variants": [ <variant record>, ... ]
}
```

A variant record:

| Field | Meaning |
|---|---|
| `variant_id` | `pe<wrapper>_uk<model>_<certified_data_build_id>`, recomputed from `identity`; when another identity already holds that slug (same versions, other wheels or numerical environment) the id adds `--<first 10 hex of identity_sha256>`. |
| `identity` | Everything that determines execution. Its canonical-JSON SHA-256 is `identity_sha256`. `data_years`, `layout`, `status` and `executor` are outside it on purpose: they describe or file a run and do not change a computed byte. `data_years` is checked instead: on a non-legacy variant every simulation compares the record's `data_years` with its dataset's whole `dataset.years` set and stops if they differ, and staging recomputes the supported years from the record. |
| `identity.packages` | For `policyengine`, `policyengine-uk`, `policyengine-core`: exact `version`, and `record_sha256`: the SHA-256 of the distribution's own `RECORD` entries, sorted, excluding installer bookkeeping (`INSTALLER`, `REQUESTED`, `RECORD`, `direct_url.json`, `uv_cache.json`), bytecode, and the console-script wrappers the installer generates outside site-packages (their shebang names the environment's interpreter). Every listed file is checked on disk against its recorded hash when the identity is read, so the digest binds the wheel's installed contents, and pip and uv installs of one wheel agree. Optional `wheel_sha256`: the wheel's digest as published on PyPI, recorded at certification; the receiver verifies each downloaded wheel against it, and the runner, which never sees a wheel, checks only its format. |
| `identity.packaged_bundle_manifest_sha256` | SHA-256 of `policyengine/data/bundle/manifest.json` as installed. |
| `identity.release_bundle` | The exact `pe.uk.uk_latest.release_bundle` dict expected at runtime under **packaged (offline) certification**. |
| `identity.dataset` | `repo_id`, `repo_type`, `revision`, `path`, `sha256`, `size_bytes`; `release_bundle.default_dataset_uri` must name the same file. |
| `identity.materialization` | `hf_cache_mirror` (policyengine 5.x: the existing HF-cache plus `data/uk/policyengine-local` mirror) or `policyengine_data_dir` (6.x: a verified copy at `<runtime dir>/data/<path>`). |
| `identity.python` | Interpreter minor version, e.g. `3.12`. |
| `identity.requirements_sha256` | The SHA-256 of the requirements freeze below: the numerical environment (numpy, pandas, h5py and the rest) is part of the identity, because it can move numbers. |
| `requirements` | `{path, sha256}`: the exact freeze installed for this variant. Legacy: `docs/uk_replay/requirements.txt`. Others: `docs/uk_replay/requirements/<variant_id>.txt`. |
| `data_years` | Calendar years the population supports: from the dataset's first `time_period` through the engine's extension end, as observed in `simulation.dataset.years`. |
| `data_years_evidence` | The observed `time_period`, `dataset.years` and the engine file/line that sets the extension end. |
| `certification` | Where the pairing is certified: `source` (e.g. `policyengine.py 6.2.6 packaged manifest`), `compatibility_basis`, `certified_for_model_version`, `data_build_id`. |
| `status` | `certified` (a released policyengine.py bundle), `candidate` (a W4 qualification request), or `retired`. Only a certified variant runs, and the default must be certified; a qualification run, which replays its own candidate record, passes `--allow-uncertified`. |
| `qualification_request_sha256` | For candidates, the request the variant was built from. |
| `executor` | `local` (GitHub runner or workstation) and/or `modal`. The populace 1.3GB dataset needs Modal's 32GiB; the 128MB enhanced FRS runs on a 16GB runner. |

### What "validated exactly" means

Before any simulation the runner checks all of the following and refuses on
the first failure. The numbering groups them by subject; the code runs record
consistency, the installed environment, certification isolation, dataset
materialisation, bytecode isolation, the engine import and its origins, then
the release-bundle comparison (`compute_uk_event.variant_preflight`; the
legacy variant's `preflight` runs the same checks around its original
managed-release preflight).

1. **Record consistency (engine-free).** `variant_id` and `identity_sha256`
   recompute; `release_bundle.model_version == packages["policyengine-uk"].version`;
   `release_bundle.policyengine_version == packages["policyengine"].version`;
   `certification.certified_for_model_version == packages["policyengine-uk"].version`;
   `release_bundle.certified_data_artifact_sha256 == dataset.sha256`;
   `release_bundle.certified_data_build_id == certification.data_build_id`;
   `release_bundle.default_dataset_uri` names `dataset.repo_id`, `path` and
   `revision`; the requirements file hashes to `requirements.sha256` and pins
   exactly the three package versions. For the legacy variant, additionally
   `certified_bundle.json`'s `revision`, `sha256`, `size_bytes`, `repo_id`
   and `compatible_model_packages` agree with the record.
2. **Installed environment.** Installed versions of the three packages equal
   the record; every installed file matches its `RECORD` hash and the
   normalised `RECORD` hashes to `record_sha256`; nothing sits in the three
   packages' directories that the package's own `RECORD` does not list:
   policyengine-core loads every file in a parameter directory and every
   module in a variable directory, recursing into subdirectories
   (`__pycache__` included) and following symlinked ones, so an unlisted
   file, any symlink, and anything but `*.pyc` inside a `__pycache__` are
   refused, and another distribution's `RECORD` does not count; every
   `*.pth` startup file beside the packages belongs to a distribution pinned
   in the requirements freeze or is the virtual environment's own
   `_virtualenv.pth`; every distribution pinned in the requirements freeze
   is installed at its pinned version (extra distributions, such as the
   receipt tools, are allowed); the installed packaged manifest hashes to
   `packaged_bundle_manifest_sha256`; the interpreter minor version matches.
   The legacy variant is checked the same way.

   What this does not bind: the files of pinned distributions other than the
   three packages are checked by version, not by hash, and an extra
   distribution's importable modules are not inspected. The check catches a
   drifted or mixed environment; it is not a defence against someone who
   can edit the environment at will.
3. **What is imported.** Before the engine is imported, bytecode caching is
   turned off and `sys.pycache_prefix` points at an empty directory, so
   Python compiles every engine module from the verified sources and never
   reads a `__pycache__` beside them; spawned year workers inherit both
   settings. After import, each package's `__file__` must be its verified
   distribution's own `__init__.py`, not a same-named tree earlier on
   `sys.path`; each year worker checks this too.
4. **Certification path.** Before importing the engine the runner removes
   `HUGGING_FACE_TOKEN`, `HF_TOKEN` and `HUGGINGFACE_HUB_TOKEN` and the
   `NO_PROXY` exceptions from the environment, forces Hugging Face offline
   mode, and points the HTTP(S) proxy variables at a closed local port.
   policyengine.py 6.x fetches the data release manifest with `requests`
   (`provenance/manifest.py`, `get_data_release_manifest`), which ignores
   `HF_HUB_OFFLINE` but reads those proxy variables, so the fetch fails at
   once for a private or a public data repository, and
   `certify_data_release_compatibility` falls back to the wrapper's packaged
   certification. Then
   `dict(pe.uk.uk_latest.release_bundle) == identity.release_bundle`, exactly.
   The legacy variant runs under the same isolation and the same exact
   comparison, in addition to its original check against
   `data/uk/certified_bundle.json`.
5. **Dataset bytes.** The materialised file hashes to `dataset.sha256` and
   has `size_bytes`, before construction and after the last aggregate
   (existing `run_managed_simulation` checks), and the simulation's reported
   runtime dataset source is that file.
6. **Year support.** Requested years must lie in `data_years`, and inside
   every simulation `year in simulation.dataset.years` or the run stops; on a
   non-legacy variant a dataset that does not state its years, or states a
   year set other than the record's `data_years`, stops the run too (the
   legacy check skips both, as it always has). Registry years outside `data_years` are not
   requested by default; they are reported as unsupported (below).

A model/data combination is **incompatible** when no certified variant
records it. There is no flag that relaxes a check: running a newer engine
means adding a variant whose certification names it.

## Unsupported years

Each event registry's `calendar_years` is the construction's window; a
variant runs `calendar_years ∩ data_years`. The rest are **unsupported on the
variant**, with a reason (`before_data_year` or `after_extension_end`).
`RUN_MANIFEST.json` records `supported_years`, `unsupported_years` and
`full_supported_grid_complete`; `full_event_complete` keeps its meaning
(every registry year). Staging does not take those fields on trust: it loads
the manifest's `variant_id` from the variants document, requires the
manifest's identity digest, `data_years`, `supported_years` and
`unsupported_years` to be the ones that record gives, and requires every
artifact's variant fields to match (a legacy manifest and its artifacts carry
none). `--resume` reads receipts only for supported years and refuses any
receipt that names an unsupported one. Staging marks a source row whose year is unsupported
as `status: "unsupported_on_variant"` with no numerical counterpart, kept in
the row universe and counted separately from `not_computed`. On
`pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0`, CY2023 is unsupported, so
Spring Budget 2023, Autumn Statement 2023 and Spring Budget 2024 lose their
FY2023–24 counterparts; that loss is shown, never hidden.

## Result namespaces

* Legacy results stay where they are, in `results/uk/events/<event>/`.
* Every other variant writes to `results/uk/replays/<variant_id>/`:
  `<event>/` (the same files as a legacy event directory), `SUMMARY.md`,
  `SUPPORT.json`, `CORPUS.json` (a qualification run's corpus version and
  events, written before any event runs), `CONSTRUCTION_PREMISES.json`,
  `MODEL_DIAGNOSTICS.json`,
  `REQUEST.json` (the re-serialised qualification request the run answers),
  `INSTALL.json` (whether installation used the certified requirements,
  certified constraints or free resolution), and finally
  `NAMESPACE_MANIFEST.json` and `REPLAY_RECEIPT.json`.
* `data/uk/replay_variants.json` is the index: each record's `result_root`
  names its namespace (legacy: `results/uk/events`) and its `status`. A
  candidate's record and results live on the `replay-state` branch under
  `requests/<request_id>/results/` until it is certified.
* A namespace with `REPLAY_RECEIPT.json` is **sealed**:
  `NAMESPACE_MANIFEST.json` lists the SHA-256 of every file under it (and of
  its release diff), the receipt binds that manifest's digest, the runner
  refuses to write there (compute, staging, comparison and the summary all
  check), and CI fails if any sealed byte changes. `verify-sealed` derives
  the expected namespaces from the variants index: every record with
  `layout: "replay_namespace"` whose `result_root` exists must have both
  sealing files. Deleting a receipt or manifest therefore fails the check.
* Each corpus qualification creates a detached checkout of the runner's `HEAD`
  under `<work>/checkout`. It deletes the candidate's namespace and selected
  diff directory inside that checkout, computes every event there without
  `--resume`, seals there, then copies the namespace and diff to the request's
  `results/` directory. The previous attempt's `results/` directory is removed
  before copying. Every pipeline subprocess uses that fresh checkout as its
  working directory and module root, keeping artifact paths repository-relative.
  The runner's committed namespaces are only read, including the diff's base.
  Re-qualifying an exactly certified pair compares the fresh run against its
  own committed run when `compare_to` is `latest_certified`; this doubles as
  a determinism check.
* Release differences live in `results/uk/replays/diffs/<base>__<head>/`.

## Version-scoped diagnoses

Every diagnosis and construction note carries the engine version it was
established on. The legacy diagnoses also describe the legacy data bundle,
so a comparison row attaches them as current only on the legacy run. On
every certified variant, including one using 2.89.2 with another bundle, the
row carries `prior_diagnoses` with `established_on` and `status:
"not_reverified"`. Re-verification of measured model candidates is separate:
`diagnose_uk_event_models.py` reruns each case's predicate and records
`persists`, `resolved` or `inconclusive`. Re-verified records keep historical
interpretation and policy citations under `established`, naming that
observation's engine, and describe the new predicate observation separately.
The legacy event outputs remain byte-identical.

For the 6.2.6 variant, use the candidate environment named in
[RECIPE.md](RECIPE.md) to reproduce a status, selecting a case if needed:

```bash
env -u HUGGING_FACE_TOKEN -u HF_TOKEN -u HUGGINGFACE_HUB_TOKEN \
  PYTHONPATH=. .venv-candidate/bin/python pipeline/diagnose_uk_event_models.py \
  --reverify results/uk/events/MODEL_DIAGNOSTICS.json \
  --expect-engine 2.125.1 --case cgt_main_rate_commencement
```

Variant summaries reject diagnostic records from another engine and count
measured issue candidates as current only when the re-verified status is
`persists`. A variant record without a status is shown as not re-verified.

## Construction premises

A namespace's premises and its `SUMMARY.md` cover the same events
(`uk_replay_variants.namespace_events`). A qualification run records its
corpus in `CORPUS.json` (corpus version and events) before replaying any
event, and that record decides. Without one (the legacy namespace, or a
namespace holding no run), they cover the events it holds results for (an
event directory with `RUN_MANIFEST.json`), or every registered replay event
when it holds none. A namespace whose bytes a seal or a release diff binds (a
diff records each side's premises digest) therefore keeps them when a later
event is registered, even if every event of its run failed. A qualification
run writes its summary last, after the re-verified diagnostics, which the
summary renders.

`pipeline/audit_uk_event_premises.py` records, for each executable measure,
year and parameter path the construction touches, on a given engine:
current-law value at the annual lookup (1 January of the year), the raw
value at 30 April, the intended baseline-world and reform-world values, and
these checks:

| Check | Fails when |
|---|---|
| `forward_delta_changes_current_law` | A forward delta equals current law in every in-force supported year (inert by construction). |
| `reversal_differs_from_current_law` | A reversal modifier equals current law in every in-force supported year. |
| `authored_construction_reproduces` | Re-authoring with this engine's parameters differs from the frozen modifier or reform delta. |
| `annual_value_matches_30_april_sample` | An in-force touched path carries `fiscal_year_blend` or `preserve_calendar_dates` metadata that the installed converter reads. This historical key checks metadata, not value equality. |

The annualisation check retains its historical name to keep legacy receipt
bytes unchanged. Converter support is detected from executable metadata
lookups in its parsed AST; a mention in a docstring does not count. A path
can carry an annualisation flag while its annual and 30 April values are
equal in a year with no rate change. Numerical evidence remains in the
separate `current_law` and `raw_30_april` fields. The latter reads the
`baseline` clone, which `process_parameters` adds as a child of the parameter
tree before uprating and backdating run over the whole tree, so it is
uprated and backdated; only the fiscal-year conversion of `.gov` skips it
(`policyengine_uk/tax_benefit_system.py:102-108` in 2.89.2; `109-115` in
2.125.1). It is therefore the uprated, backdated value sampled on 30 April
before fiscal-year conversion. Installed-engine tests
compare the CGT values directly and regenerate the corresponding committed
premises; the engine-free suite reports an explicit skip for those checks.

`baseline_world` and `reform_world` are the intended processed period-Y
values: the construction's value at 1 January Y when its annual override
contains that date, otherwise the current-law annual value. The premises
audit and executor use one shared function to compute them. These fields
describe the construction's intent; a parameter-only annual lookup does
not prove a simulation executed it. This distinction matters when a reform
is written to the statutory timeline and annualised again.

For every replay, immediately after constructing each world's simulation
and before any aggregate is calculated, the executor reads period Y from that
simulation's own processed parameter tree for every path touched by either
world. It records both the intended and processed values, per path and
world, in the measure-year artifact; agreement means relative difference
within `1e-9`, or both values absent. It reads the tree the engine actually
built, so it checks both the
annual-lookup and statutory-reprocessing routes without predicting either
from a version string. Legacy-layout runs omit the field and retain their
artifact bytes.

In policyengine-uk 2.130.1, a construction-time reform's `start.stop`
interval is written onto the statutory timeline before processing
(`utils/dated_reforms.py`, `read_reform_dict`, and
`tax_benefit_system.py`, `_rebuild`). A 1 January Y interval on a
`fiscal_year_blend` path therefore also changes part of period Y−1. The
AB2024 CGT revision uses complete fiscal-year intervals on that route;
the annual-lookup route uses intervals containing 1 January of the intended
year. The executed processed-value check remains mandatory in either case.

A failed check is a **construction revision candidate**, reported in the
release diff's construction flags and summarised in
`docs/uk_replay/CONSTRUCTION_REVISIONS.md`. A selected revision is recorded
there with its d1344 basis and exceptions; it never edits a frozen registry.

Observed on 2.125.1 on 11 October (parameter tree only):

* `gov.contrib.labour.private_school_vat` is still 0 in every year, so the
  AB2024 VAT forward delta still changes current law.
* The SDLT additional-dwelling scale is still 3/5/8/13/15%, so the AB2024
  forward 2pp delta still applies.
* CGT `basic_rate` at the 2024 annual lookup is 0.1346. In 2.125.1,
  `parameters/gov/hmrc/cgt/basic_rate.yaml` dates the 18% rate from
  2024-10-30 and sets `metadata.fiscal_year_blend: true`, and
  `utils/parameters.convert_to_fiscal_year_parameters` day-weights such
  parameters over 6 April–5 April (`fiscal_year_average`) instead of
  sampling 30 April: 0.10 × 207/365 + 0.18 × 158/365 = 0.1346. The AB2024
  note assumes 2.89.2's raw 2025-04-06 date and 30 April sampling. The
  frozen reversal, first selected in January 2025, leaves the blended 2024
  increase in both worlds on this engine's annual-lookup route. The selected
  construction revision instead holds the pre-announcement 10%/20% through
  FY2024–25, activating FY2024–25 on blend engines. FY2023–24 is unchanged.
* The UC childcare cap path (2024 £1,014.63 for one child) and the benefit
  CPI path feed the SB2023 and SS2025 frozen counterfactuals, which were
  derived from 2.89.2's values.
* The Class 2 flat rate for 2023 is £3.45, so the "pin uses £3.15" note is a
  2.89.2 fact only.

## Release differences

`pipeline/diff_uk_event_runs.py --base <variant or root> --head <variant or root>`
compares two complete namespaces, engine-free, after re-verifying each side's
staging and comparison receipts against that side's receipt-bound registry
snapshot. The current event registry does not replace a historical snapshot.
Every inventoried artifact is checked by the staging and comparison validators,
including artifacts that supply no numeric source counterpart. Each run
manifest's execution identity, registry and artifact inventory, supported and
unsupported years, and measure-year grids must agree with the verified staging
rows and tally. Inertness comes from the staging manifest named and verified by
comparison provenance. Inconsistent receipts are refused before a diff is
written. Two namespace files are checked when present:

* `NAMESPACE_MANIFEST.json`: the events whose run manifests it lists must be
  exactly the events that load, so a sealed namespace with an event listed but
  missing, or present but unlisted, is refused (the diff compares the event
  sets and does not re-hash the listed digests);
* `CONSTRUCTION_PREMISES.json`: its engine (policyengine, policyengine-uk and
  policyengine-core versions) must be the run's, and each event's premise
  record must name the registry digest that event verified against.

Keys:

* source row: `(event, source_row_id)`;
* measure-year total: `(event, measure_key, year)`;
* PE head: `(event, measure_key, year, variable)` from artifact `head_effects`.

Flags are descriptive; none is a pass or a failure. A flag names a move to
investigate, and the existing signed PE/OBR bins are reported unchanged as
bin transitions.

| Flag | Raised when |
|---|---|
| `numerical` | Both sides numeric and `abs(head − base) > max(£1,000,000, 0.01 × max(abs(head), abs(base)))`. Strictly greater. |
| `structural` | Sign reversal or a zero crossing (zero means `abs(x) ≤ £0.50`, accounting roundoff); artifact schema or orientation changed; non-finite value. Regardless of size. |
| `coverage` | A counterpart, artifact pair or source row present on one side only, in a year both sides support. The shared-support requirement also applies to rows outside household scope or without an expressible counterpart. An event replayed on one side only flags every one of its source rows `event_on_base_only` or `event_on_head_only`, whatever the year. |
| `mapping` | A row's `head_variables`, an artifact's `head_channels` or `head_definitions`, or the registry SHA-256 differs. Registry changes flag the event's affected records with both digests. |
| `support` | A year supported on one side only. Source rows that cannot carry a counterpart do not receive this flag. |
| `inertness` | `inert_construction` on one side only, or identical worlds in an in-force year on one side only. |
| `construction` | Executed `baseline_world`/`reform_world` reform dicts differ, a premise check's result differs, or a measure has premise records on one side only (`premises_on_base_only`/`premises_on_head_only`; the other side's checks cannot be compared). A changed current-law value of a touched parameter is recorded as context on the row, not flagged: it is what a model release is expected to change. When neither side has premises, `DIFF.md` says so: premise checks were not compared. |

Identity changes (wrapper, engine, core, data build, dataset digest) are
recorded once per diff; they explain moves and are not flags on rows.

Outputs: `DIFF.json` (canonical, sorted), `DIFF.md`, and one issue packet per
flagged `(event, measure, year)` under `packets/`. A packet holds the source
cells (table, column, row number, source-row id, OBR value) and measure details
from each registry with base/head attribution, both execution
identities, registry and artifact digests, the executed reform dicts, the
affected heads with base/head values, focused rerun commands for each
variant using that side's verified registry path and variant selection, the
statutory sources each registry already cites with side attribution, and empty
`minimal_case` and `statutory_evidence` sections for the investigating lane.
Removed measures retain their base title, source cells and citations.
Packets are evidence for the coordinating session, which files upstream
issues; this pipeline files none.

Diff invariants are checked with deterministic cases and Hypothesis properties
in `tests/test_uk_event_diff.py`: identical sides raise no flags; swapping sides
preserves each record's flag set and mirrors its values; every source row in
either side appears once at source-row level; every flagged record appears in
exactly one packet, including support-only records; numerical moves flag only
strictly above the stated threshold; coverage and support do not overlap; and,
for events on both sides, coverage requires a year both sides support.

## Qualification requests and receipts

See [QUALIFICATION_INTERFACE.md](QUALIFICATION_INTERFACE.md) for the request
W4 sends before promotion and the receipt returned.

### The receiver

`.github/workflows/uk-replay.yml` receives `repository_dispatch` events of
type `uk-replay-qualification-request` (and manual requests). An incoming
request uses an `enqueue` job to write it to the persistent queue on the
`replay-state` branch (`pipeline/uk_replay_queue.py`), then dispatches a drain
run. Incoming runs have distinct concurrency groups; drain runs share
`uk-replay-drain`, so only one prepare/run/record sequence executes at a time.
GitHub's default concurrency queue can replace an older pending run; the
request remains in `replay-state` for a later drain.
([GitHub concurrency documentation](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency))

The `prepare` job selects the oldest eligible request, marks it running and
hands only `REQUEST.json` to the run job. The separate `run` job has
`contents: read` and checks out with `persist-credentials: false`. Its first
step after that fetches the dataset with `fetch-dataset`, checks its size and
SHA-256, and records the fetch outcome, before any candidate code is
installed. That one step holds the data token: the organisation secret
`PE_UK_PRIVATE_HF_READ_TOKEN` (read-only, policyengine-uk-data-private only),
passed as `HUGGING_FACE_TOKEN`, and only in `workflow_dispatch` and
`repository_dispatch` runs; the schedule only dispatches a drain, and the
workflow has no pull-request trigger. A fetch rejection is passed to the run
without installing candidate code.

Candidate code then runs as an unprivileged account inside a systemd sandbox
(`.github/scripts/uk_replay_sandbox.sh`), never as the runner user. The
runner user has passwordless sudo, owns the workspace and the runner's
command files (`$GITHUB_ENV`, `$GITHUB_PATH`), and owns the runner processes
that keep the job's secrets in memory for the whole job and pass the Actions
runtime token to later steps. Later steps run as that user and search its
`PATH`, which on the hosted image includes world-writable directories under
`/opt`; a separate account alone could plant a program there for a later
step to run. So the candidate runs as a transient systemd service
(`systemd-run --uid`): the whole filesystem is read-only except the
account's home (`ProtectSystem=strict`), the runner's home is inaccessible,
`/tmp` is private, setuid programs such as sudo cannot gain privileges
(`NoNewPrivileges`), other users' processes are invisible
(`ProtectProc=invisible`), and kernel tunables, modules, logs, the clock,
namespaces and capabilities are locked down. `/dev/shm` and `/dev/mqueue`
stay shared with the host (systemd binds them under `PrivateDevices`), so
Python multiprocessing works; nothing later in the job runs from them. The
account has no sudoers entry, no supplementary group (so no docker socket)
and no cron or at jobs. `setup` checks from inside the sandbox that sudo
fails, that the account has no group beyond its own, and that nothing is
writable among every directory on the runner's `PATH` and its parents, the
tool cache, `/opt`, `/usr`, `/etc`, the workspace, the command files and the
docker socket; otherwise the job fails. The account works in its own copy of
the repository and of `input/` (the request, the verified dataset and the
fetch outcome), with an environment built from nothing. It runs
`.github/scripts/uk_replay_drain.sh` for that one request. When the
service's main process ends, systemd kills everything left in it; `collect`
then checks that no process of the account survives, and the account streams
its `output/` out with `tar`, which the runner user unpacks as itself; links
stay links and special files stay special files, for the guard to refuse.
The upload needs both `collect` and the guard to succeed. CI's `receiver
sandbox` job runs `setup`, `run` and `collect` on the runner image on every
pull request, with no secrets and a stub drain that does what a real run
needs inside the sandbox (creates a uv environment and installs from PyPI,
adds a git worktree of the copy, runs a multiprocessing pool) and leaves a
process behind.

Scorecard is public, so the dataset and anything household-level stay on the
runner. No job saves or restores a cache (setup-uv's default cache is off on
every use, and nothing uses `actions/cache`), so no cache links a candidate
to the jobs that can write. The only artifacts are the request and the run's
`output/` directory. `.github/scripts/uk_replay_output_guard.py` (standard
library, run with the runner's own Python) is an allowlist: every entry must
be a regular file ending `.json`, `.jsonl`, `.csv`, `.md` or `.txt` whose
bytes parse as that format (UTF-8 text, no NUL bytes), at most 10 MB each and
100 MB in all; tables are allowed only as `COMPARISON.csv` and
`STAGED.jsonl`, the names the pipeline writes. The committed sealed namespace
for 6.2.6 is 30 MB, its largest file 3.3 MB. The run job uploads only if the
guard passes. The `record` job, where no candidate code has run, applies the
guard again (`.github/scripts/uk_replay_recheck.sh`) before committing
anything to the public `replay-state` branch, and drops a refused output, so
the attempt is recorded as `failed`.

What this protects, and what it does not. A request names its candidate by
version and wheel SHA-256, and only a caller with write access to this
repository can send one (`repository_dispatch` and `workflow_dispatch` both
require it); requests are meant for PolicyEngine's own releases, from W4. A
new candidate's dependencies resolve within the newest certified freeze
where they can. The candidate and its dependencies are trusted with the
dataset: they compute on it, and the guard stops an honest run from
publishing a dataset copy, a binary, or a `.csv` or `.jsonl` table under
any other name. It does not read what a parsable file says: a
household-level table written as `COMPARISON.csv`, or as JSON or Markdown,
would pass. Code in the candidate's dependency closure cannot reach the data
token, the runtime token, the write jobs' credentials or a cache, and cannot
alter the guard or what the recorder checks. A deliberately malicious
candidate could still encode data in aggregates that parse, and could forge a
schema-valid receipt for its own request, since the receipt and seal are
produced beside it. Neither is in scope. Each needs malicious code in the
candidate's environment: a malicious PolicyEngine release, a commit reached
through the wrapper's `PolicyEngine/policyengine.py` git source (which can
name a fork's commit), or a malicious third-party dependency pulled in when
installation falls back to free resolution.

CI's `replay engine` job is weaker: the variant's engine runs as the runner
user, so code in a certified freeze could reach the token held by the fetch
step's runner process. That job runs only on pushes to main, with committed,
certified freezes. `pipeline/uk_replay_qualify.py run-request` then:

1. Validate the request (`schema_invalid`).
2. Check the dataset file supplied by the control job against the request
   (`data_access_failed`, `artifact_hash_mismatch`).
3. Build the candidate environment: download the model and core wheels
   without dependencies, check their SHA-256 against the request, then
   install them, the wrapper (its PyPI wheel or its public commit) and the
   receipt tools. A requested wheel missing from PyPI is an
   `artifact_hash_mismatch` rejection. Re-qualifying a certified pair installs
   that pair's exact requirements freeze; a new candidate first uses the
   newest certified freeze as constraints and falls back to free resolution
   if that installation fails. `INSTALL.json` records `exact_requirements`,
   `certified_constraints` or `free_resolution`, the reference variant and
   the environment file's digest; the namespace seal binds this provenance.
4. Probe inside that environment: the installed identity, the release
   bundle under packaged certification (`release_bundle_mismatch`), the
   certification naming this model and this dataset (`incompatible_pair`),
   and the simulation's data years (`no_supported_years`). If the
   environment reproduces a committed variant exactly, the run uses that
   record; otherwise it builds a candidate record whose requirements are the
   environment's normalised freeze.
5. Run the corpus in the fresh checkout: every event's compute (allowing the
   candidate record), staging (using the work variants document), comparison,
   the summary, the construction premises, the re-verified diagnostics.
6. Diff against the runner checkout's committed `compare_to` namespace
   (default: the newest certified variant with committed results, preferring
   the matching certified variant itself for an exact re-qualification). The
   base is verified against the runner's committed variants document and the
   candidate against the work document that adds its record.
7. Seal the namespace (`NAMESPACE_MANIFEST.json`, then
   `REPLAY_RECEIPT.json`) and copy it, the diff and the requirements to
   `replay-state:requests/<request_id>/results/`.

The qualifier writes a result file containing `status` and `receipt_sha256`;
the drain handles a non-zero qualifier exit and leaves run logs visible in
Actions. The separate `record` job, with `contents: write` and `actions: write`,
reads that result file, validates the uploaded output and commits the receipt
first. The terminal `STATUS.json` follows in a later commit naming the receipt's
digest and the pushed receipt commit. Missing or invalid run output yields a
minimal `failed` receipt.

An in-force measure-year whose declared heads come out identical in the two
worlds is inert. If the run's `CONSTRUCTION_PREMISES.json` gives any
parameter different 1 January values in the two worlds that year, the
intended change did not show in the declared heads: the construction did not
reach the engine, it does not bind on this population, or it moves only
variables outside those heads. The receipt then
records an integrity failure `construction_inert` (with `event`,
`measure_key`, `year`, and the parameter and both worlds' values in
`detail`), and its status is `failed`. Equal premises values do not prove a
pair should be inert (a freeze can carry earlier years' rates forward), so
such a pair leaves the grid incomplete and is listed in
`inert_measure_years`. Whether either blocks promotion is W4's qualification
policy.

A processed parameter value that differs from its intended value is an
integrity failure. The values are read before aggregation; whether a
mismatch refuses the measure-year is decided once both worlds are computed
(`compute_uk_event.processed_value_failures`). It refuses when the mismatch
is in the certified current law, when the measure is in force that year
(from its `commences_fy`), or when the two worlds' totals differ (gov_tax,
gov_spending, household net income or any declared head). The executor then
refuses to write the measure-year artifact; qualification records
`processed_value_mismatch` with `event`, `measure_key` and `year`, plus
`world`, `path`, `intended` and `processed` as JSON in the receipt schema's
`detail` field, and returns a failed receipt. This check does not depend on
a nonzero fiscal-head result: an in-force construction routed to a different
annual value fails even when its population effect happens to be zero.

The one accepted mismatch is in an announcement world, never the certified
current law, in a year before the measure commences whose two worlds come
out identical: it moved none of those totals. A `commences_fy` that is not a
complete `YYYY-YY` label for consecutive years is an error, not a deferral. The artifact
is written and lists each such mismatch under `processed_value_notes`, with
the same fields and `"accepted": "not_in_force_identical_worlds"`. In
policyengine-uk 2.130.1, a construction-time change starting on a
parameter's first stated date is rebuilt without its prior law, so a
reversal's value also appears in earlier years. AB2025's high-value council
tax surcharge shows this in 2025 to 2027, where its formula returns zero
before 2028.

A step that fails before the candidate's identity is known yields a `failed`
receipt with no execution block. If no event outputs exist, `corpus` is null.
An exception while building, sealing or copying the receipt's results yields
a minimal `failed` receipt with `receipt_step_failed` and the error's first
line. A request still `running` seven hours after its last update (a cancelled
or crashed job) is eligible for retry; at most three `running` history entries
are allowed. The next stale attempt records a minimal `failed` receipt with
`attempt_limit_exceeded` and terminal status instead of running again.

The recording job dispatches another drain run while pending requests remain;
`workflow_dispatch` can create a run using `GITHUB_TOKEN`.
([GitHub workflow-trigger documentation](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow))
A scheduled run every three hours also drains the queue. This schedule only
processes recorded requests; undispatched release discovery is separate work
in PR #165. Concurrent enqueues retry with backoff and, on a rebase conflict,
abort, check out the latest state branch and enqueue the request again.
Exhausting retries reports an error.

At most one drain run executes, with at most two simulation workers, so this
workflow never runs more than two simulations at once. These runs use GitHub
runners; manual replays on the shared Mac also respect the host reservation
(`python3 ~/reviews/fleet-ops/tools/reservation.py allowed w6-replay`), which
holds heavy local work back from 29 October to 2 November.

### Replay in CI

`ci.yml` runs two kinds of replay check on every pull request and push:

* Engine-free, in the main job: every committed namespace with event run
  manifests (legacy and each variant) is re-staged and re-compared from its
  artifacts, every committed release diff is re-rendered with `--check`, and
  every present namespace indexed as `replay_namespace` must have a receipt
  and manifest matching its bytes. The no-drift gate uses
  `git status --porcelain`, so newly generated untracked files fail too.
* `replay engine`, for the two certified variants in its CI matrix: installs
  each variant's exact
  freeze, checks the installed environment against the record, runs every
  event's construction guards, regenerates the committed construction
  premises byte for byte. Non-legacy variants also regenerate the re-verified
  diagnostics and, on pushes to main with the `PE_UK_PRIVATE_HF_READ_TOKEN`
  secret and a committed sealed namespace, replay one real measure-year on
  the certified dataset and compare its artifact with the committed bytes.
  The token is in one step that fetches the dataset into the Hugging Face
  cache; the variant's engine runs in the next step, without it, in a job
  with `contents: read`, no persisted checkout credential and no cache.
  Pull requests never receive the token: their run emits a notice that
  nothing was replayed. The legacy leg skips diagnostics and this
  determinism step. Without the secret, or without a committed sealed
  namespace, the step emits a notice stating that nothing was replayed.

## Invariants

Each has deterministic boundary cases and Hypothesis properties in
`tests/`:

* **Exact variant validation.** For any record and environment differing from
  it in one field, validation refuses; for the matching pair it accepts.
* **Support honesty.** No artifact exists for a year outside the variant's
  `data_years`; every registry source row appears exactly once in staging,
  with unsupported years as `unsupported_on_variant`.
* **Replay determinism.** For the same complete execution fingerprint
  (variant identity, registry bytes, measure, year), numerical artifact bytes
  are identical; timings stay in `RUN_LOG.json`.
* **Legacy preservation.** Legacy staging, comparison and summary outputs
  regenerate byte-identically from the committed artifacts
  (`tests/test_uk_replay_legacy.py` reruns all five events and compares
  bytes), and no committed legacy artifact, manifest or receipt carries a
  variant field.
* **Diff flags.** `diff(a, a)` has no row flags. Flag sets are symmetric under
  swapping sides (with signs reversed). No numerical flag at or below the
  threshold; one strictly above it. Row order and file order do not change
  output bytes.
* **Sealed namespaces.** Every byte under a sealed namespace matches its
  receipt.
