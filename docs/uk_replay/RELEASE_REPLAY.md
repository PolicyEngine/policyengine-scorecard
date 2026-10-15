# Replaying the event corpus on every certified release

Status: design contract for workstream W6 of the Autumn Budget 2026 CI plan,
11 October 2026. It extends the track 1 replay ([RECIPE.md](RECIPE.md),
[YEARS.md](YEARS.md)) from one hard-pinned world to any number of
**certified replay variants**, and turns each variant's run into a receipt
that release qualification (W4, policyengine.py) can consume before a
model/data pair is promoted.

Nothing here changes a registered construction. A variant reruns the same
frozen registries; where a construction's premise no longer holds on a
variant, that is reported as a construction revision for review, never
silently repaired. Methodology changes (counterfactual intent, annualisation
semantics, acceptance policy) wait on cos d1344.

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
  `SUPPORT.json`, `CONSTRUCTION_PREMISES.json`, `MODEL_DIAGNOSTICS.json`,
  `REQUEST.json` (the qualification request the run answers), and finally
  `NAMESPACE_MANIFEST.json` and `REPLAY_RECEIPT.json`.
* `data/uk/replay_variants.json` is the index: each record's `result_root`
  names its namespace (legacy: `results/uk/events`) and its `status`. A
  candidate's record and results live on the `replay-state` branch under
  `requests/<request_id>/results/` until it is certified.
* A namespace with `REPLAY_RECEIPT.json` is **sealed**: the runner refuses
  to write there (compute, staging, comparison and the summary all check).
  A rerun of a sealed variant writes to an explicit separate output
  directory, and its bytes against the sealed run are a determinism check.
  The receiver (`pipeline/uk_replay_qualify.py`, which arrives with the
  receiver change, PR #163) writes the seal itself:
  `NAMESPACE_MANIFEST.json` lists the SHA-256 of every file under the
  namespace (and of its release diff) and the receipt binds that manifest's
  digest. The same change adds the CI job that fails when a sealed byte
  changes and replays one real measure-year; until it lands, neither exists.
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

`pipeline/audit_uk_event_premises.py` records, for each executable measure,
year and parameter path the construction touches, on a given engine:
current-law value at the annual lookup (1 January of the year), the raw
value at 30 April, the executed baseline-world and reform-world values, and
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

A failed check is a **construction revision candidate**, reported in the
release diff's construction flags and summarised in
`docs/uk_replay/CONSTRUCTION_REVISIONS.md` with a proposed revision. Running
a revised construction is a methodology change and waits on d1344.

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
  reversal, first selected in January 2025, leaves the blended 2024 increase
  in both worlds, so CY2024 shows no effect although current law has one.
* The UC childcare cap path (2024 £1,014.63 for one child) and the benefit
  CPI path feed the SB2023 and SS2025 frozen counterfactuals, which were
  derived from 2.89.2's values.
* The Class 2 flat rate for 2023 is £3.45, so the "pin uses £3.15" note is a
  2.89.2 fact only.

## Release differences

`pipeline/diff_uk_event_runs.py --base <variant or root> --head <variant or root>`
compares two complete namespaces, engine-free, after re-verifying each side's
staging and comparison receipts. Keys:

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
| `coverage` | A counterpart, artifact pair or source row present on one side only, in a year both sides support. |
| `mapping` | A row's `head_variables`, an artifact's `head_channels` or `head_definitions`, or the registry SHA-256 differs. |
| `support` | A year supported on one side only. |
| `inertness` | `inert_construction` on one side only, or identical worlds in an in-force year on one side only. |
| `construction` | Executed `baseline_world`/`reform_world` reform dicts differ, or a premise check's result differs. A changed current-law value of a touched parameter is recorded as context on the row, not flagged: it is what a model release is expected to change. |

Identity changes (wrapper, engine, core, data build, dataset digest) are
recorded once per diff; they explain moves and are not flags on rows.

Outputs: `DIFF.json` (canonical, sorted), `DIFF.md`, and one issue packet per
flagged `(event, measure, year)` under `packets/`. A packet holds the source
cells (table, column, row number, source-row id, OBR value), both execution
identities, registry and artifact digests, the executed reform dicts, the
affected heads with base/head values, focused rerun commands for each
variant, the statutory sources the registry already cites, and empty
`minimal_case` and `statutory_evidence` sections for the investigating lane.
Packets are evidence for the coordinating session, which files upstream
issues; this pipeline files none.

## Qualification requests and receipts

See [QUALIFICATION_INTERFACE.md](QUALIFICATION_INTERFACE.md) for the request
W4 sends before promotion, the receipt returned, and the persistent queue.

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
