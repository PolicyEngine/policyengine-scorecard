# Replaying the event corpus on every certified release

Status: design contract for workstream W6 of the Autumn Budget 2026 CI plan,
11 October 2026. It extends the track 1 replay ([RECIPE.md](RECIPE.md),
[YEARS.md](YEARS.md)) from one hard-pinned world to any number of
**certified replay variants**, and turns each variant's run into a receipt
that release qualification (W4, policyengine.py) can consume before a
model/data pair is promoted.

The registries remain frozen. An explicit construction revision may be
selected from `data/uk/events/construction_revisions.json` or
`construction_revisions_enacted.json` by metadata or current-law values in
the installed engine; the SHA-256 of the file holding it is bound in the run
manifest and premises, and the comparison and release diff identify it. The
revisions follow W6's methodology choice under cos d1344 (Max, 15 October
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

The pair examined in the initial 11 October audit was policyengine.py
**6.2.6** (PR #555 and its version bump `481940ec`): `policyengine-uk 2.125.1`, `policyengine-core
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
| `executor` | `local` (GitHub runner or workstation) and/or `modal`. The populace 1.3GB dataset needs Modal's 32GiB; the 128MB enhanced FRS runs on a 16GB runner, and the 322MB Microcosm UK 2024-25 runs there with one year worker (see "Memory and year workers"). |

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

### Certified pairs (lane runs only)

A lane can need a policyengine.py release's certified bundle before this
pipeline qualifies it as a variant: `uk-childcare-100k` (issue #228) runs on
policyengine.py 6.11.0's Microcosm pair. `data/uk/certified_pairs.json`
(kind `uk_certified_pairs`, `pipeline/uk_certified_pairs.py`) records each
such bundle in the variant record's shape less the fields that file a
replay: `pair_id` (`pair-<variant slug>`) in place of `variant_id`, status
`certified_pair`, and no `layout` or `result_root`
(`uk_certified_pairs.FIELDS` is the whole field set).

- **The checks are the variant's.** `uk_replay_variants.validate_identity`
  is check 1 for both kinds; `validate_record` adds only the variant's
  status, layout, result root and legacy checks. A pair's preflight then
  runs checks 2 to 6 through the same code: `verify_installed`, then
  `compute_uk_event.materialized_preflight`, the second half of
  `variant_preflight`.
- **No event replay runs on a pair.** The event runner resolves only
  `replay_variants.json`; a lane resolves either kind with
  `uk_certified_pairs.get_record`, and its ingest reads both files.
- **A pair stays when a variant arrives.** A variant this pipeline later
  qualifies for the same bundle has its own requirements file, so its own
  identity and id. The pair remains the identity the lane's runs on it were
  checked against.
- Experiment populations (`docs/uk_replay/POLICY_EXPERIMENTS.md`) are a
  third kind: their results are never ingested, while a lane's runs on a
  pair are.

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
  the expected namespaces from the variants index: a record with
  `layout: "replay_namespace"` must have both sealing files when its
  namespace holds an event `RUN_MANIFEST.json`, a `CORPUS.json`, a receipt or
  a namespace manifest (`uk_replay_qualify`, `must_be_sealed`). A namespace
  holding only premises, diagnostics or a summary stays unsealed. Deleting a
  receipt or manifest therefore fails the check.
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

### Committed certified results

Each certified qualification reaches main through a results pull request
([below](#the-results-pull-request)), which adds its paragraph here from the
receipt's counts; reviewers add any interpretation. The newest certified
variant is the last `certified` record in `data/uk/replay_variants.json`.

`results/uk/replays/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/` holds
the receiver's qualification of policyengine.py 6.4.1: request `b1f9a93d…`,
receipt SHA-256 `3b420b5e…`, `replay-state` commit `484eaa7`. Its release
diff against the legacy variant is committed beside it. All six corpus events
have complete supported grids and no inert measure-years.
It was the newest certified variant until 6.5.0; the 6.2.6 audit above
remains historical evidence.

The run predates the processed-value readback and the AB2024 CGT construction
revision (#186). Its AB2024 Capital Gains Tax row for period 2024 (FY2024–25)
therefore executes the frozen reversal on policyengine-uk 2.130.1's statutory
reprocessing route, and carries that route's rate blend. The registry's
30 October 2024 start (which the artifacts record) is executed as the window
1 January 2025 to 31 December 2035 (`compute_uk_event.annual_reform`).
Reprocessed with `fiscal_year_blend`, that window also covers 95 of
FY2024–25's 365 days. By the day-weighting rule, the reversal world's
FY2024–25 rates are basic 0.1138 against an intended 0.1346, and higher and
additional 0.2069 against 0.2173. The frozen construction intends identical
worlds in period 2024, yet the row records +£0.575bn. That figure comes from
the route; it is not a PolicyEngine costing of the FY2024–25 increase.

Periods 2025 to 2029 (FY2025–26 to FY2029–30) fall wholly inside the window,
so their reversal rates are the intended 0.10 and 0.20. A rerun with #186
executes the revision and refuses any processed mismatch in an in-force year.

The real replay of this variant (`uk-replay-determinism.yml`, on pushes to
main) recomputes one artifact with the current code, which also writes the
processed-value evidence fields. A committed artifact from before that check
is compared with exactly those fields removed, and the step says so in a
notice; every other byte must match (`pipeline/uk_replay_determinism.py`).

`results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/` holds
the qualification of policyengine.py 6.5.0: request `d83eaf59…`, receipt
SHA-256 `a7a67c26…`, `replay-state` commit `19a9ccd`. It ran with #186, so
every artifact carries its processed values and the AB2024 CGT revision
`ab2024_cgt_fiscal_year_blend.v1` is selected. Integrity is complete with no
failures, and all six events have complete supported grids and no inert
measure-years. Its release diff is against 6.4.1, the newest certified
variant with committed results at the time. That diff flags eight rows, all
of them AB2024 CGT main rates. Period 2024 moves from +£0.575bn to +£0.956bn,
the blended FY2024–25 increase, with processed rates equal to intended in
both worlds. Periods 2025 to 2029 carry only the construction flag, and their
values are unchanged. No other row in any event moved. AB2025's high-value
council tax surcharge artifacts for 2025 to 2027 record
`processed_value_notes` (policyengine-uk#2435); their totals are zero. The
real replay of this variant compares whole bytes.

`results/uk/replays/pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1/` holds
the qualification of policyengine.py 6.9.0: request `705e2b7a…`, receipt
SHA-256 `e9883083…`, `replay-state` commit `755ceb7`. Integrity is complete
with no failures, and all six events have complete supported grids and no
inert measure-years. Its release diff is against
`pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`, the newest certified
variant with committed results at the time. That diff flags no rows. The
results pull request wrote this paragraph from the receipt's counts.

`results/uk/replays/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/`
holds the qualification of policyengine.py 6.11.0: request `55070155…`,
receipt SHA-256 `48ac3847…`, `replay-state` commit `5c4e38a`. Integrity is
complete with no failures, and all six events have complete supported grids
and no inert measure-years. Its release diff is against
`pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1`, the newest certified
variant with committed results at the time. That diff flags 394 rows; its
flag counts are numerical 393 and structural 4, and every other flag count
is zero. The results pull request wrote this paragraph from the receipt's
counts.

`results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/`
holds the qualification of policyengine.py 6.11.1: request `62397224…`,
receipt SHA-256 `e0fbc787…`, `replay-state` commit `0a9075d`. Integrity is
complete with no failures, and all six events have complete supported grids
and no inert measure-years. Its release diff is against
`pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71`,
the newest certified variant with committed results at the time. That diff
flags 356 rows; its flag counts are construction 22, numerical 350 and
structural 20, and every other flag count is zero. The results pull request
wrote this paragraph from the receipt's counts.

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

`DIFF.json` also records, per side, `grids`: each event's grid as that side's
verified staging recorded it (`diff_uk_event_runs.staging_grid`: supported
years from the run manifest, `full_supported_grid_complete`, and the inert,
missing and unsupported measure-years), for variant runs only. A
qualification receipt copies the base side's into `diff.base_events`.

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
`uk-replay-drain`, so only one discovery/prepare/run/record sequence executes
at a time.
GitHub's default concurrency queue can replace an older pending run; the
request remains in `replay-state` for a later drain.
([GitHub concurrency documentation](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency))

An empty-request `workflow_dispatch` drain first runs `discover`, then
`discover_enqueue`, before `prepare`. The schedule's `tick` job only dispatches
that empty drain: it does not check out code or hold the dataset token. Neither
discovery nor dataset fetching runs on a schedule tick or a pull request.

| Job | Authority and inputs |
|---|---|
| `tick` | `actions: write`; dispatches an empty drain, without a dataset token. |
| `enqueue` | `contents: write`, `actions: write`; records a received request and dispatches a drain; runs only trusted control code. |
| `discover` | `contents: read`, checkout credentials disabled; reads PyPI and wheel ZIP/JSON bytes, with one token step reading only the private data release manifest. It installs, imports and executes no release or candidate code. |
| `discover_enqueue` | `contents: write`; validates public discovery metadata and writes `replay-state`; no dataset token or release/candidate code. |
| `prepare` | `contents: write`; selects a queued request and marks it running. |
| `run` | `contents: read`, checkout credentials disabled; one trusted token step fetches the dataset, then candidate code runs in the sandbox below. |
| `record` | `contents: write`, `actions: write`; rechecks public output, records the receipt, dispatches the results workflow for a complete request and dispatches the next drain; no release/candidate code. |

For the 6.4.1 and 6.5.0 wheels, a successful packaged-certification
`release_bundle` is a pure function of the packaged manifest. The loader reads
`data_releases[country]` (`policyengine/provenance/manifest.py:321–335` in
both wheels); local overlays cannot shadow the default or certified dataset
(`:300–317`). Offline certification selects the bundled certification for the
pinned model (`:395–422`); a fingerprint mismatch can raise, rather than
produce a different successful bundle. Bundle construction fills those
manifest fields (`policyengine/tax_benefit_models/common/model_version.py:126–158`
in 6.4.1, `:127–164` in 6.5.0), and the property projects the exact dictionary
(`policyengine/core/tax_benefit_model_version.py:137–210` in 6.4.1,
`:148–222` in 6.5.0). In particular, `policyengine_version` comes from that
manifest (`:156` and `:168` respectively), not an imported wrapper.
Discovery mirrors that projection and checks it against the exact W4 6.4.1
and 6.5.0 request fixtures in `tests/fixtures/uk_replay/discovery/`. The
receiver still compares the request with the installed release's actual
runtime bundle: a future release that changes this projection is rejected
if they differ.

`pipeline/uk_replay_discover.py` considers stable, non-yanked PyPI releases
whose wheel upload is at least six hours old, oldest first. The grace period
allows W4's normal dispatch and publication metadata to arrive before
catch-up. A version must be strictly newer than both the newest certified
variant and the newest version named by a recorded `released_bundle` request
in any status (`queued`, `running`, `complete`, `failed` or `rejected`).
Only `released_bundle` requests count, for this floor and for deduplication.
A pre-promotion `candidate` request names the version the candidate will be
released as but pins the candidate's wheels, while `push.yaml` rebuilds the
released wheel, so a missed release dispatch is still caught and the
released bytes replayed. A requested version raises the floor only while
PyPI lists it and only if it is a plain final release (no epoch, local, pre,
post or dev segment). A yanked release is still listed, so it still counts.
A version PyPI no longer lists (removed or quarantined) stops counting, and
the releases it superseded can then be discovered if they pass every other
check. A stored request naming a version never published cannot stop
discovery, yet still counts against duplicating itself. Requests are stored
under their content digest, so a wrong request is recovered by removing it
from `replay-state`, never by editing it in place. For example, once 6.5.0
was certified (or requested as a released bundle), discovery no longer
considered 6.4.2, 6.4.3 or 6.5.0 itself. A certified version suppresses older
releases whatever PyPI lists; a requested one does so only while PyPI lists
it. Each drain builds at most three requests and examines at most 30
releases.

Before building a request, discovery reads the selected wheel's static PyPI
integrity provenance JSON and requires an attestation bundle whose publisher
has each of these fields with exactly these case-sensitive values (a field
PyPI adds later is ignored, so it cannot permanently skip a genuine release):
`kind: "GitHub"`,
`repository: "PolicyEngine/policyengine.py"`, `workflow: "push.yaml"`, and
`environment: "pypi"`. The
[6.5.0 wheel provenance](https://pypi.org/integrity/policyengine/6.5.0/policyengine-6.5.0-py3-none-any.whl/provenance)
is the checked example of those exact field names and values. Discovery runs
nothing from this response. A 404 (PyPI: "file has no provenance"), another
publisher and an unreadable provenance response are permanent skips,
evidenced by the response bytes' SHA-256. Any other HTTP status, including
403 (access "temporarily disabled by the PyPI administrators") and 406, and
any network failure, leaves the release eligible next time
([PyPI integrity API](https://docs.pypi.org/api/integrity/)).
A read stopped at the size cap also remains retryable, since it has no digest
of a complete response. Other contradictions in verified immutable artifacts
are also recorded as permanent skips, with the artifact digests that support
the decision.

Accepted requests record the provenance response's SHA-256 in
`requested_by.pypi_provenance_sha256`, so it is part of their request identity
and public discovery metadata; discovery also logs the digest. The vendored
[v1 request schema](schemas/qualification_request.v1.json) already permits
additional provenance fields inside `requested_by`; no schema change is
needed. Permanent skips record it as
`evidence_sha256.policyengine_provenance`.

Discovery derives public request fields from the wrapper wheel's packaged
manifest and PyPI metadata without installing or importing the wheel. Its
only token-holding step reads the private release manifest to bind its SHA-256
and the certified dataset's size; it downloads no dataset. Downloaded wheels
have a 64 MiB streaming-read cap; PyPI JSON responses have a 1 MiB cap.
The packaged manifest and METADATA ZIP members must each be at most 1 MiB,
with a compression ratio no greater than 100, before decompression. The
artifact passed to `discover_enqueue` contains only requests and permanent skip evidence,
checked by the receiver's output guard before upload. The write job guards
that artifact again and validates **every** request against the vendored
qualification schema before enqueueing any request. It refetches `replay-state`
and checks covered versions again on each write attempt, so a W4
`released_bundle` request that arrived before that attempt is not duplicated
(a `candidate` request deliberately does not cover the released version). A
dispatch arriving after discovery has pushed can still create a distinct
request; the six-hour grace period reduces that overlap but does not rule it
out. Failed discovery or discovery enqueueing
does not block `prepare`: existing queued requests still drain.

The `prepare` job selects the oldest eligible request, marks it running and
hands only `REQUEST.json` to the run job. The separate `run` job has
`contents: read` and checks out with `persist-credentials: false`. Its first
step after that fetches the dataset with `fetch-dataset`, checks its size and
SHA-256, and records the fetch outcome, before any candidate code is
installed. That step holds the data token: the organisation secret
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
process behind. `setup` also checks the offline form of the sandbox that the
real replay uses ([the real replay in the
sandbox](#the-real-replay-in-the-sandbox)).

Scorecard is public, so the dataset and anything household-level stay on the
runner. No job saves or restores a cache (setup-uv's default cache is off on
every use, and nothing uses `actions/cache`), so no cache links a candidate
to the jobs that can write. The only artifacts are public discovery metadata,
the selected request and the run's `output/` directory.
`.github/scripts/uk_replay_output_guard.py` (standard
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
version and wheel SHA-256. W4's explicit dispatch and manual request paths are
joined by discovery's automatic path: discovery trusts a release on PyPI only
when its wheel has trusted-publisher provenance naming
`PolicyEngine/policyengine.py`, workflow `push.yaml`, environment `pypi`, with
publisher kind exactly `GitHub`, as in the
[checked 6.5.0 response](https://pypi.org/integrity/policyengine/6.5.0/policyengine-6.5.0-py3-none-any.whl/provenance).
A PyPI upload without that provenance cannot create a discovery request.
These requests remain intended for PolicyEngine's own releases. A new
candidate's dependencies resolve within the newest certified freeze
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

The real replay in `uk-replay-determinism.yml` runs a certified variant's
code in this same sandbox, its replay offline. [The real replay in the
sandbox](#the-real-replay-in-the-sandbox) says how, and what a malicious
freeze could still do there.

In the qualification run's sandbox, the drain
(`.github/scripts/uk_replay_drain.sh`) runs
`pipeline/uk_replay_qualify.py run-request`, which goes through these steps:

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
dispatches an empty `workflow_dispatch`; that drain discovers missed releases
before selecting work. Concurrent enqueues retry with backoff and, on a
rebase conflict,
abort, check out the latest state branch and enqueue the request again.
Exhausting retries reports an error.

At most one drain run executes, with one or two simulation workers (see
"Memory and year workers"), so this workflow never runs more than two
simulations at once. These runs use GitHub runners; manual replays on the
shared Mac also respect the host reservation
(`python3 ~/reviews/fleet-ops/tools/reservation.py allowed w6-replay`), which
holds heavy local work back from 29 October to 2 November.

### Memory and year workers

`compute_uk_event` runs each event's years one after another in its own
process (one worker) or across two spawned year workers; each holds one live
simulation at a time. The run job is a
GitHub-hosted `ubuntu-latest` runner, which for a public repository has 4
CPUs and 16 GB of memory
([GitHub-hosted runners](https://docs.github.com/en/actions/reference/runners/github-hosted-runners)).
On 30 October 2026 `free -m` on that runner reported 15,983 MiB of memory and
3,071 MiB of swap, and `df` 83 GB free on `/`.
`run_request` runs two workers only when
`docs/uk_replay/evidence/replay_memory.json` records a two-worker peak for
the request's exact dataset (by SHA-256) and workload, and that peak plus a
2 GiB reserve fits in the runner's `MemTotal`, read from `/proc/meminfo`.
The workload is the candidate's identity as the request names it (the three
engine versions, the wheels' digests and the wrapper's source), its
installed numerical environment (the digest of the normalised freeze that
`probe` records in the variant's identity, so the choice is made after
`probe`), the corpus version, the scheduling event, and a digest of the
scorecard files that run that event besides the engine
(`MEMORY_WORKLOAD_FILES`: its registry, the construction revisions and the
compute modules); a change to any of them makes a measurement another
workload's. A peak counts only from a completed run of the whole of Autumn
Budget 2025, the corpus's event with the most measure-years (nine measures
over six years, each with a modified world) and the one two Microcosm workers
could not finish on policyengine-uk 2.132.6, in which both year workers were
spawned and the run manifest's full event
grid is complete. A slice leaves out years, worlds and the memory a worker
accumulates over them, so it does not count. Anything else means one
worker: a dataset or workload nobody has measured, an evidence file of
another format, a peak that is not a positive integer below 2^50 bytes, or
an unknown `MemTotal`. The
reserve is a margin for what lies outside the corpus's process tree (the
runner's services, the drain's control process, the page cache), not a
measurement.

The choice and its reason go in the receipt's `execution.runner`, after the
runner's name: for example `github-actions Linux X64; 1 simulation worker:
measured two-worker peak … plus 2.0 GiB reserve exceeds this runner's …`.
It is a string rather than a new key because policyengine.py validates every
receipt against its vendored copy of `replay_receipt.v1.json`
(`provenance/qualification.py`, `ReplayReceipt.from_document`), whose
`execution` object admits no other property.

The evidence comes from `pipeline/modal_uk_replay_memory.py`. It builds the
candidate environment with the qualifier's own `prepare`, runs `probe` and
then `compute_uk_event` exactly as `run_corpus` calls it, in a Modal
container with the runner's 4 CPUs and 32 GiB (so a run that would not fit on
the runner still finishes and is measured), and samples the summed resident
memory of `compute_uk_event` and its year workers every 0.2 s. Pages two
processes share count in both, so the figure bounds the tree from above. The
container's network is blocked while it runs, and only memory, timings and
lines matching `compute_uk_event`'s own progress and aggregate formats
exactly are printed or come back; any other line stays in the container.
Each measurement records the candidate's identity, the installed
environment's freeze digest from the container's own `probe`, the workload
digest (taken from the copy that is uploaded, and checked again in the
container) and the run manifest's coverage. `summarize` derives each dataset's peaks from
the measurements, and a test regenerates the committed file's summary from
its own measurements. The three one-worker measurements below were taken
before each phase's process peak started from the phase's own first sample,
so their phases record only the tree's peak (`"phase_peaks": "tree_only"`);
they inform, and do not schedule.

The committed measurements (Modal, 4 CPUs; the qualifier's own `prepare`
resolved each candidate within the 6.9.0 certified environment). The two
whole-event two-worker runs, on 23 October 2026, are the scheduling
evidence; the one-worker runs, on 22 October, are for reading:

| Slice of Autumn Budget 2025 | Dataset (release) | Workers | Peak summed RSS | Wall |
|---|---|---|---|---|
| all years and measures | Microcosm UK 2024-25 (6.10.0) | 2 | 19.2 GiB | 22 min |
| all years and measures | Microcosm UK 2024-25 (6.10.0) | 1 | 10.2 GiB | 46 min |
| 2029: baseline and the threshold-freeze world | Microcosm UK 2024-25 (6.10.0) | 1 | 8.5 GiB | 1.6 min |
| all years and measures | enhanced FRS 1.58.1 (6.9.0) | 2 | 9.1 GiB | 15 min |
| 2029: baseline and the threshold-freeze world | enhanced FRS 1.58.1 (6.9.0) | 1 | 3.8 GiB | 0.8 min |

Two earlier runs of the Microcosm two-worker slice, before the tool's last
revisions, measured 18.6 and 18.5 GiB. For the workloads measured,
Microcosm with 6.10.0's candidate runs one worker on a 16 GB runner (19.2 GiB
plus the reserve is far above it) and the enhanced FRS 1.58.1 with 6.9.0's
would run two (9.1 GiB plus the reserve fits). Any other candidate on either
dataset, 6.10.1's included, has no matching measurement and runs one. #224
changed `pipeline/uk_replay_variants.py`, a workload file, after these
measurements, so every request now runs one worker until a dataset is
measured again with this tool and `summarize`; that is the direction this
rule errs in. A worker's resident memory grows over its successive years: with one
worker on Microcosm it went from 8.9 GiB in 2025 to 10.2 GiB in 2030. In
policyengine.py 6.10.0's first two qualification attempts (requests
`47fe63f4…` and `dfc9d655…`), two workers finished AB2025's 2025 to 2028,
where the measured two-worker peak is 17.5 to 17.9 GiB, and the runner was
lost in 2029 and 2030, where it reaches 19.2 GiB; their 2029 and 2030
baselines took 60 to 67 s, against 29 to 40 s for the earlier years on the
runner and 28 to 31 s for the same baselines with one worker here. Summed
RSS counts shared pages twice, so the runner held somewhat less than these
figures when it failed.

The first attempts of 6.10.2 (`4d08f87c…`) and 6.11.0 (`ad44443d…`), on the
same policyengine-uk 2.132.6, policyengine-core 3.33.3 and Microcosm build,
lost their runners with two workers at the same AB2025 years. 6.11.0's second
attempt (`55070155…`, run 41079735503) ran the whole corpus with one worker
and completed in 97 minutes of simulation, inside the run job's 340. Its
`[memory]` lines match the measurement above:

| Event | Peak process tree | Lowest `MemAvailable` | Minutes |
|---|---|---|---|
| Autumn Budget 2024 | 9.3 GiB | 5.4 GiB | 20.5 |
| Autumn Statement 2023 | 9.1 GiB | 5.5 GiB | 14.1 |
| Spring Budget 2024 | 8.7 GiB | 5.9 GiB | 10.7 |
| Spring Statement 2025 | 8.5 GiB | 6.1 GiB | 9.1 |
| Spring Budget 2023 | 8.4 GiB | 6.2 GiB | 6.0 |
| Autumn Budget 2025 | 10.2 GiB | 4.5 GiB | 36.5 |

policyengine.py 6.11.1's first attempt (`25ae5bf3…`, run 40433159238) moved to
policyengine-uk 2.151.0 and a newer Microcosm build
(`…20261025T091414Z-a6299504`, whose file is 6% larger) and lost its runner
five minutes into Autumn Budget 2024 with two workers. Its measurements, also
in the evidence file, need more memory and time than 2.132.6's: two workers
peak at 27.3 GiB on Autumn Budget 2024, where one year worker alone reaches
15.5 GiB. This repository does not establish which change between
policyengine-uk 2.132.6 and 2.151.0 adds the memory.

Its second attempt (`d1e672fe…`, run 41143889866) ran the whole corpus with
one worker and completed in 190 minutes of simulation, inside the run job's
340. The table sets its `[memory]` lines beside the one-worker measurements:

| Event | Peak summed RSS on Modal | Peak process tree on the runner | Lowest `MemAvailable` | Minutes on Modal | Minutes on the runner |
|---|---|---|---|---:|---:|
| Autumn Budget 2024 | 15.5 GiB | 14.7 GiB | 0.1 GiB | 39 | 43.2 |
| Autumn Budget 2025 | 12.7 GiB | 12.7 GiB | 2.1 GiB | 73 | 68.4 |
| Autumn Statement 2023 | 11.9 GiB | 11.9 GiB | 2.8 GiB | 36 | 27.4 |
| Spring Statement 2025 | 11.4 GiB | 11.3 GiB | 3.4 GiB | 22 | 18.0 |
| Spring Budget 2024 | 11.4 GiB | 11.4 GiB | 3.3 GiB | 18 | 20.5 |
| Spring Budget 2023 | 10.9 GiB | 10.9 GiB | 3.8 GiB | 14 | 12.2 |

So Autumn Budget 2025 no longer has the corpus's largest peak on that release.
Autumn Budget 2024 filled the runner's memory. Swap held nothing before the
candidate started and 175 MiB after that event, and the run does not log swap
at the peak. One worker fits policyengine-uk 2.151.0 with only the swap to
spare, so a later release that needs more memory on this path can lose the
runner again.

The run job also logs the runner's memory, swap, CPUs and disk before the
candidate starts and its memory after it ends. Inside the sandbox,
`run_corpus` prints `free -m` before and after each event; while the event
runs it samples the process tree every second and prints each new whole GiB
it reaches with `MemAvailable`, and after the event the tree's peak and the
lowest `MemAvailable`. A runner lost to memory leaves those lines as the last
it streamed.

### The results pull request

A certified qualification reaches main through a pull request built by
`.github/workflows/uk-replay-results.yml`, never by a direct push. When the
`record` job writes terminal status `complete`, it dispatches that workflow
with the request id; a failed dispatch is a warning, and the workflow can be
run by hand with the same `request_id`. It has no `pull_request` trigger and
runs only the default branch's code.

| Job | Authority and inputs |
|---|---|
| `build` | `GITHUB_TOKEN` `contents: read`, checkout credentials not persisted, no secret. Assembles the commit and runs every check, with the PyPI packages the checks need, CI's own format check and suite among them. Outputs the verified tree, the main and `replay-state` commits it used, two check results and its report of CI's checks. |
| `propose` | On a fresh runner. `GITHUB_TOKEN` `contents: read`; actions pinned to commits; no uv and no installed package. Assembles the same commit again with git and the standard library (the builder under `python3 -I -S`, small helpers under `python3 -I`) on the commits `build` used: `replay-state` history, and main history no older than the workflow's own commit. It refuses unless its tree is `build`'s, then decides again against main's current tip, reading only the request it extracted and guarded. Only then is a short-lived token for the organisation's `policyengine` GitHub App minted, scoped to this repository with `contents: write` and `pull-requests: write`, to push that commit and open the pull request. |

Neither job holds a dataset token, and neither installs, imports or runs
release or candidate code; both read only committed public results from
`replay-state`. Two jobs, not two steps, because steps in one job share a
runner: whatever the checks' packages did there (a `$GITHUB_PATH` or
`$GITHUB_ENV` write, a planted program) would reach a later step that held
the token. Job 2 receives only job 1's outputs, as strings it validates, and
pushes only what this code builds from main's and `replay-state`'s history.
The tree comparison catches an honest build job whose commit diverges; the
`verify-sealed` and content-hash lines and the report of CI's checks in the
pull request body are the build job's word, checked only for shape. CI on the
pull request runs the regeneration, both database builds, the format check,
the suite and the drift checks again.

The App token, not `GITHUB_TOKEN`, writes because a pull request opened with
`GITHUB_TOKEN` starts no `pull_request` workflow
([GitHub documentation](https://docs.github.com/en/actions/concepts/security/github_token)),
while checks from a `workflow_dispatch` run do not count for a pull request
([GitHub documentation](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks)),
so its pull request would never carry checks. The App's push and pull request
start CI as any other pull request does.

The token has no `workflows` permission, which an App needs to edit files in
`.github/workflows`
([GitHub documentation](https://docs.github.com/en/apps/creating-github-apps/registering-a-github-app/choosing-permissions-for-a-github-app)).
The commit never touches `.github/`: CI's engine matrix is read from the
variant index (see "Replay in CI"), and `scope` refuses a commit that touches
anything outside the results and the four edits. So the token cannot push a
workflow that reads a secret. It can still push to any branch of this
repository, main included (main has no protection rule or ruleset), and the
scripts and pipeline code that secret-holding jobs run live outside
`.github/workflows`; without `workflows` it loses only the direct route.

`.github/scripts/uk_replay_results_pr.sh` and
`pipeline/uk_replay_results_pr.py` build the pull request as #188 (6.4.1) and
#190 (6.5.0) were built by hand, less the `ci.yml` matrix entry each added,
which CI now reads from the index:

1. **Eligibility.** `STATUS.json` is `complete`; the receipt validates and is
   the one `STATUS.json` names; `REQUEST.json` hashes to the request id; and
   `results/VARIANT.json` is `certified`, is the receipt's variant and was
   built from this request. A failed, rejected or candidate run, or a variant
   the index already holds, ends the run with a notice and no pull request. A
   certified variant whose policyengine version is older than the newest
   certified one is refused: appended, it would become `latest_certified`.
   That refusal is permanent for that request: the older release's results
   stay on `replay-state`.
   So is a variant id that could not name a branch and paths (anything but
   letters, digits, `.`, `_` and `-`, or a `..`). An exactly certified pair
   qualified again returns the committed record, so it ends with a notice
   too. That comparison is the variant: its id and its `identity_sha256`,
   which must be the digest of its identity, against a certified record on
   main. The rest of main's record (the note, and anything a later change
   to the index adds or reshapes) is not compared. A record that only
   shares its id with a committed one (two runs that finished before either
   merged) is refused, to be qualified again for an id of its own.
2. **Results, byte for byte.** The request directory passes the receiver's
   output guard again, and its receipt and results must be unchanged since
   the receipt commit. `requests/<request_id>/results/{results,docs}` is
   extracted with `git archive … | tar -x --strip-components=3`. It may hold
   only the variant's namespace, its release diff and its requirements
   freeze, none of which main may already hold; the namespace's receipt must
   be the request's, and its manifest and diff the ones the receipt binds.
   After the commit, every one of those files must have the blob
   `replay-state` holds. Nothing household-level is added: the namespace is
   aggregates, and nothing is uploaded.
3. **Edits.** `VARIANT.json` plus a `note` is appended to
   `data/uk/replay_variants.json` in canonical form
   (`compute_uk_event.canonical_bytes`). That is all CI needs to replay the
   variant: the `replay-engine` matrix is the index's certified variants
   (see "Replay in CI"), so no workflow changes. `NEWEST` in
   `tests/test_uk_replay_qualify.py` and
   `tests/test_uk_replay_determinism.py` moves to it, and `COMMITTED` in
   `tests/test_uk_replay_variants.py` gains it. A paragraph under "Committed
   certified results" states the receipt's integrity, grid and diff-flag
   counts. Each edit checks the text it replaces and fails if the file has
   another shape, and the commit may touch nothing else, `.github/`
   included.
4. **Checks.** `uk_replay_qualify verify-sealed` (the new namespace, then
   every one), CI's `.github/scripts/uk_replay_regenerate.sh`, and two
   `scorecard_db.build_db` runs, which must agree on the content hash and
   leave no tracked-file drift. A failure of any of these stops the run.
   Then CI's own checks on the same tree, as `ci.yml`'s `python` job runs
   them on every pull request: `uvx ruff format --check be nz scorecard_db
   tests pipeline`, the suite (`uv run --with pytest … pytest tests/ -q`,
   with `PYTHONPATH=.`), and its no-drift check, `git status --porcelain`
   after the suite. A test checks that these are `ci.yml`'s lines word for
   word. They run in the `build` job, which holds no write credential: the
   script refuses to start them if `GH_TOKEN` or `GITHUB_TOKEN` is set, and
   unsets the variables that name the step's command files
   (`$GITHUB_OUTPUT`, `$GITHUB_ENV`, `$GITHUB_PATH`, `$GITHUB_STATE`,
   `$GITHUB_STEP_SUMMARY`), so a test that writes one by name writes
   nowhere. That is hygiene, not a sandbox: a process that finds the files
   on the runner's disk can still write them, and `propose` takes every
   output of `build` as its word, checked for shape. Their output goes to
   the step log with workflow commands paused (`::stop-commands::`, by a
   token only the script holds), so a line the suite prints is not acted
   on as one, and what `build` outputs about the commit is read before they
   run. Their failure does not stop the run. The job reports each check's
   exit status, how many files, tests or paths failed (the node ids of
   pytest's last short test summary, the files ruff names, the paths
   `git status` lists) and the first 50 that are printable ASCII without a
   backtick, with no space at either end and at most 200 characters long,
   as one line of JSON (three full lists keep the body inside GitHub's
   65,536-character limit). On CI pytest prints whole messages over lines:
   the job reads a message line that itself starts with `FAILED` or `ERROR`
   as another node id, and one that is itself a summary header drops the
   ids before it. Only the list changes: a check's exit status, not its
   list, says whether it failed. `propose` refuses a report of any other
   shape, a count of a billion or more among them. Results pull requests
   #195, #204 and #206 opened ready and failed CI's `pytest` job; with these
   checks such a pull request opens as a draft that names the failures.
5. **Pull request.** In the `propose` job, steps 1 to 3 run again with the
   standard library, skipping only the JSON Schema and RFC 8785 checks
   `build` made. Only when the tree matches is the App token minted. The
   commit, authored and committed as `github-actions[bot]` (the receiver's
   bot identity) with a `Replay-Request:` trailer and pushed with the App's
   token, goes to `uk-replay-results/<variant_id>`, and a pull request
   against main follows; CI runs on it as on any pull request, without the
   dataset token. It is a draft when integrity is not `complete`, or when
   one of CI's checks in step 4 fails; its body then lists what failed,
   under "Validation in the results run", in a fenced block, with the
   count of any it could not list. Fix those on main and run the workflow
   again for the same request: it rebuilds the branch on the new main.
   The builder never marks a pull request ready; a person does, once CI
   passes.

Running the workflow again for the same request is safe. An identical tree
pushes nothing. A branch built on an older main is rebuilt and force-pushed,
with a lease on the commit it read, only when it holds exactly one commit,
authored and committed by the bot with this request's trailer; an added or
amended commit is a person's, and the run fails and leaves the branch alone.
A rebuild that pushes edits the open pull request's title and body. One that
is a draft (integrity not `complete`, or one of CI's checks failing) first
turns a ready pull request back into a draft (`gh pr ready --undo`), before
the push, so it is never ready on a commit whose checks failed; one that is
not leaves it as it is. A rerun on
an unchanged main pushes nothing, so it leaves the body as it was, even when
the earlier run's suite failed only by chance.
A rebuilt branch also carries main's commits since the branch was built.
GitHub does not document whether it counts that as editing a workflow when
one of those commits changed `.github/workflows`, even a change main later
reverted; if it refuses such a push
for want of `workflows`, the run fails with an error that says so and the
branch stays as it was. Close the pull request, delete its branch and run the
workflow again: a new branch holds only the bot's commit.
Two certified requests built from the same main conflict in the index and
the tests: after the first merges, run the workflow again for the
second, unless the second is the older release, which the version check then
refuses. Nothing merges automatically. The pull request lands on the normal
gates: CI and an independent review.

### Replay in CI

CI runs four kinds of replay check. `ci.yml` runs the first three on every
pull request and push, and `uk-replay-determinism.yml` runs the fourth on
pushes to main only:

* Engine-free, in the main job: every committed namespace with event run
  manifests (legacy and each variant) is re-staged and re-compared from its
  artifacts, every committed release diff is re-rendered with `--check`, and
  every present namespace indexed as `replay_namespace` must have a receipt
  and manifest matching its bytes. The no-drift gate uses
  `git status --porcelain`, so newly generated untracked files fail too.
* `replay engine`, one leg for each certified variant. The
  `certified replay variants` job lists the certified variants of
  `data/uk/replay_variants.json` in index order, and that list is the
  matrix (`.github/scripts/uk_replay_engine_matrix.py`: the standard library
  under the runner's own Python, in a job with `contents: read` that checks
  out only that script and the index). No workflow names a variant, so the
  index is the only list a new variant joins. The job fails, and with it
  every leg, rather than list fewer variants, when a record is not an
  object, an id is not plain (letters, digits, `.`, `_` and `-`, starting
  with a letter or digit, no `..`, at most 120 characters; CI puts ids in
  job names, environment variables, shell commands and paths, and two ids
  joined by `__` name a release diff's directory), a status is not `certified`,
  `candidate` or `retired`, an id repeats, nothing is certified, or the
  matrix would exceed GitHub's 256 jobs
  ([GitHub limits](https://docs.github.com/en/actions/reference/limits)).
  Each leg installs the variant's exact
  freeze, checks the installed environment against the record, runs every
  event's construction guards, regenerates the committed construction
  premises byte for byte. Non-legacy variants also regenerate the re-verified
  diagnostics. The legacy leg skips them. `ci.yml` names no dataset token,
  and a pull request's run emits a notice that nothing was replayed.
* `real replay sandbox`, with no secrets: the real replay's sandbox modes
  on the runner image, with a stand-in dataset and a stub engine
  ([below](#the-real-replay-in-the-sandbox)).
* `real replay`, in `uk-replay-determinism.yml`, on pushes to main only, one
  leg for each certified variant from the same listing. A non-legacy variant
  with a committed sealed namespace replays one real measure-year on the
  certified dataset and compares its artifact with the committed bytes. The
  `PE_UK_PRIVATE_HF_READ_TOKEN` secret is in one step, the first after the
  checkout, uv's setup and a read of the index, and before anything of the
  variant's is installed. It fetches the dataset into the Hugging Face hub
  cache by uv's absolute path in an emptied environment, with packages no
  newer than a fixed date and the token on stdin. The variant's install and
  replay then run as the unprivileged candidate account in the systemd
  sandbox, the replay offline
  ([below](#the-real-replay-in-the-sandbox)), and the runner's own Python
  compares the artifact that comes back. The job has `contents: read`, no
  persisted checkout credential and no cache. The legacy leg replays
  nothing. Without the secret, or without a committed sealed namespace, the
  fetch emits a notice stating that nothing was replayed.

#### The real replay in the sandbox

The real replay in `uk-replay-determinism.yml` runs a certified variant's
code as the receiver runs a candidate: as the unprivileged account in the
systemd sandbox that [the receiver](#the-receiver) describes
(`.github/scripts/uk_replay_sandbox.sh`). Its token step runs before any
variant code, which keeps such code from redirecting the fetch through
`$GITHUB_ENV`, `$GITHUB_PATH` or a planted file. The job then finds the
fetched dataset by size and SHA-256 (`find_dataset_bytes`, under the
runner's own Python) and runs `setup`. The variant's code runs in two
services after that:

* `install` builds the variant's exact freeze in the account's copy, with
  the network and without the dataset.
* `replay` checks that nothing of the account is running and has the account
  write the dataset into its copy from a pipe, inside an offline service,
  into an `input/` it makes afresh: a link left in the copy can send the
  bytes nowhere the sandbox cannot already write, and a pipe left there
  cannot stall the write. It then replays one measure-year from that file
  (`compute_uk_event --dataset-file`), offline. The service gets its own
  network namespace, whose only interface is loopback (`PrivateNetwork`),
  and may open only IPv4, IPv6 and netlink sockets
  (`RestrictAddressFamilies`; a `socketpair`, which multiprocessing may use,
  still works). Without Unix sockets it cannot reach systemd-resolved over
  D-Bus, which on the hosted image resolved a name for the candidate under
  `PrivateNetwork` alone, or any other host service. systemd enforces that
  on `socket(2)` only, so the service may make only native system calls
  (`SystemCallArchitectures=native`: the 32-bit x86 ABI's `socketcall` would
  pass the filter) and none of io_uring's, which can open a socket without
  `socket(2)`. `setup` checks from inside an offline service that loopback
  is the only interface, that an IPv4 socket opens and a Unix socket does
  not, and that `io_uring_setup` fails with `EPERM`.

Both print the variant's output, its stderr joined to its stdout, with the
runner's workflow commands stopped (`::stop-commands::` with a token
generated outside the sandbox). The runner reads stderr as a separate
stream, where a last line with no newline would reach it after the token.
They first remove the problem matcher that setup-uv registers for the rest
of the job (owner `python`), because matchers read plain lines, which
stopping commands does not stop. So that output cannot set a step output or
raise an annotation, through a workflow command or a matcher. `collect` then
checks that no process of the account survives and streams `output/` back;
an honest run leaves only the replayed artifact there. The runner's own
Python (`/usr/bin/python3 -E -s`, standard library only) compares it with
the committed artifact that the job names, and refuses anything but a
regular file (`pipeline/uk_replay_determinism.py`). Nothing is uploaded or
cached. The job has a 90-minute timeout.

So a compromised package among a certified freeze's pins cannot read the
token, short of a kernel exploit (below). The token is not in the sandbox's
environment, the runner's processes are invisible, sudo and setuid programs
cannot raise privileges, and the runner's home, workspace, command files and
every directory on its `PATH` are read-only or hidden. It cannot leave a
process behind; it can leave files in `/dev/shm` and `/dev/mqueue` and
System V IPC objects, which nothing later in the job reads. The freeze pins
versions, not file hashes (`docs/uk_replay/requirements/`), so this sandbox,
not the pins, is what keeps such a package from the token.

What such a package can still do:

* It reads the dataset, as the engine must, and its output goes to the
  workflow's public log, so it could print household-level data there.
* It controls the bytes it hands back, and its copy of the repository holds
  the committed artifact. So it can make the comparison pass: the check
  catches an honest engine whose output drifts, not a malicious one.
* During `install` it has the network, but not the dataset.
* It can fail the job, or hold it until the timeout.
* A kernel privilege escalation would defeat the sandbox, as it would any
  sandbox on that kernel; the `install` service, unlike `replay`, also runs
  without the system call filters.

The workflow runs only on pushes to main. CI's `replay engine` legs install
and run each variant on pull requests too, so `ci.yml` names no dataset
token: the runner receives a secret its job names even in a step that never
runs. CI's `real replay sandbox` job runs `setup`, `install`, `replay` and
`collect` on every pull request, with no secrets: a stand-in dataset, plus a
one-package freeze and a stub engine module in the account's copy. The
freeze installs from PyPI in the sandbox. The stub reports what it finds
offline, leaves a process behind, and forges workflow commands (on stdout,
and on stderr with no newline) and a traceback the matcher would read. The
runner's comparison must find exactly loopback, no connection out, no name
lookup and no D-Bus, the stand-in's SHA-256, a working process pool and the
arguments the job passed. The stub must have set no step output, while a
control step outside the fence sets one the same deprecated way. No step can
read the job's annotations, so the job does not check them.

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
* **Year workers.** Two workers exactly when the measured two-worker peak
  for the request's dataset and workload plus the reserve is at most the
  runner's memory; more memory never means fewer workers and a higher peak
  never means more; no such peak, or an invalid one, means one, and so does
  any change to the candidate's identity, its installed environment or the
  workload's files. Only a
  completed whole-event Autumn Budget 2025 run with both year workers
  spawned sets that peak, and it is the largest such run. The committed evidence is its own
  measurements summarized, and a process tree's total is its root's
  resident memory plus each child's total.
* **Engine matrix.** For any index the lister accepts, CI's engine matrix is
  exactly its certified ids in index order; one bad record refuses the whole
  matrix; the lister's plain-id rule is the results pull request's on any
  string; and no workflow names a variant.
