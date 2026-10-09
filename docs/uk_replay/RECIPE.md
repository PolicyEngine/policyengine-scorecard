# Replaying an OBR fiscal event on the certified bundle

Each event lane builds its registry, runs the executable household legs, stages
every source row, and writes descriptive comparisons. The input is the OBR
Policy measures database harvested in `~/scorecard-harvest/uk_obr/`, frozen as
the gzip snapshot named in `sources/uk_replay/source.json`. The source manifest
pins both compressed and uncompressed SHA-256 values. A registry build refuses
different bytes.

Read `docs/AI_GUIDANCE.md` and `docs/ARCHITECTURE.md` first. Work on the assigned
event branch. The replay must not change calibration targets to fit the OBR,
update the certified pin, infer a behavioural adjustment from a raw difference,
or classify an unexplained gap as an engine defect without evidence.

## Classifying measures

Group the exact source titles within the chosen `conditions.fiscal_event`.
Keep each source head and FY as its own `source_rows` entry, including zero
cells. The source-row id includes the snapshot position and the source line's
digest. The original `reform_hint`, `tax_head` or spending head, FY, table,
column, metric and gain-to-Exchequer value remain attached.

Assign every source row exactly one of these classes:

| Class | Required record |
|---|---|
| `expressible` | Resolved parameter construction, a `pe_reform_delta`, a `pe_baseline_modifier`, or a package; a dated policy schedule; and explicit source-head mappings with tax/spending channels. |
| `partial` | An executable household leg, the exact omitted legs in `missing_legs`, and the resulting scope limits. Unmapped source heads remain uncomputed. |
| `not_expressible` | A `pe_gap` that names the missing tax base, entitlement, history, data input or counterfactual world. Record a search over both the pinned engine's full parameter tree and variable list; a search result alone does not demonstrate a mechanism. |
| `out_of_household_scope` | A business, departmental, local-government, financing or other non-household account, with the scope reason. Corporation tax, bank levy and business rates belong here. |

A measure can have source rows outside household scope while its household
heads are expressible or partial. Source-row classes determine the accounting;
the measure's summary class must not silently override them. A tax that exists
in the engine is not enough to express a measure: the targeted population and
the event's counterfactual also need to be established.
Measure counts use each measure's single summary class; row counts and £ use
each source row's class. Outside-scope £ can therefore include business or
departmental heads belonging to a partial household measure.

The current executor accepts parameter dictionaries. An input-changing
construction needs an executor extension, including variable-period input
setting before calculation and a measured check that the toggle took effect;
documenting an input idea alone does not make it executable.

For `not_expressible`, distinguish an evidenced missing mechanism from a
`construction_pending` decision in `gap_kind`. The latter means that this
lane has not established an executable construction; it does not establish
that the engine lacks the underlying liability model.

Title keywords need token boundaries: ISA/ISAs, VAT and NIC/NICs must not
match disability, private, innovation or technical. Likewise, immigration
is not UC migration. The registry tests cover these cases and generated
embedded acronyms. Scope lookup strips only outer head-label whitespace;
the source label itself remains unchanged for accounting and provenance.

Read ambiguous spending heads in the context of the source title. Autumn
Budget 2024's SEND-deficit reduction is local-authority finance funded by
additional DEL, recorded only under `Other AME (current)`, so it is outside
household scope. That does not make every Other AME payment outside scope.
Spring Statement 2025's capital-investment package uses `PSGI in CDEL` and
`Scottish AME (capital) `, both public-budget accounts; the trailing space
does not create a household counterpart.

Autumn Budget 2024 examples:

* Employer NICs: reverse the rate increase and secondary-threshold reduction
  on the certified world. The Employment Allowance increase and eligibility
  expansion require firm information that the household model does not
  represent, so the package is `partial`.
* Carer's Allowance earnings-limit increase is `not_expressible`: the pinned
  `carers_allowance` formula tests care hours or reported receipt and never
  tests earnings. Its parameter node has the rate and minimum care hours, but
  no earnings limit. The diagnostic script demonstrates the missing test
  using two carers with identical care hours and different earnings.
* CGT main-rate increases can be a `partial` reversal from 2025 onward. The
  raw parameter change is dated April 2025 rather than the announced October 2024;
  BADR and Investors' Relief histories remain omitted. The pin labels these
  rate parameters as under active development, which must travel into the
  construction's caveat. The April-snapshot conversion implies that the
  April 2025 rate applies throughout annual 2025: the first higher processed
  year is 2025, rather than 2026.
* SDLT's additional-home 2pp increase requires a forward delta: the pinned
  additional-home scale still has its old rates, so reversing certified law
  would score the wrong world. The event's source head includes other stamp
  taxes; retain that scope limitation.
* Removing private schools' business-rates charitable relief is
  `out_of_household_scope`. The private-school VAT leg is `partial`: execute
  the dedicated `gov.contrib.labour.private_school_vat` lever at 20% from
  January 2025 on imputed attendance and average fees. Input-VAT recovery,
  school spending responses, boarding detail and attendance or fee behaviour
  remain absent; a generic VAT rate is not a substitute for this construction.
* Abolishing the non-dom regime needs residence and foreign-income history;
  a main income-tax rate change cannot stand in for that package.

## Construction patterns

`reversal_on_certified_world` is used when a measure is already present in the
pinned current law. For the Autumn Budget 2024 employer NICs package, the
mode-2 construction restores
`gov.hmrc.national_insurance.class_1.rates.employer` to 0.138 and
`gov.hmrc.national_insurance.class_1.thresholds.secondary_threshold` to £175
per week from calendar 2025. £175/week corresponds to the pre-announcement
£9,100/year threshold; the pin's £96/week corresponds to £4,992/year and is a
recorded approximation to the announced £5,000/year threshold. Date windows
are explicit, and years before commencement retain their real zero effects.

Winter Fuel Payment illustrates a partial certified-world reversal. In
`policyengine_uk/variables/gov/dwp/winter_fuel_allowance.py`, eligibility is
qualifying-benefit receipt OR `require_benefits=false` OR an income passport.
From 2025 the passport admits England/Wales households with any state-pension-age
member whose `total_income` is below £35,000; Northern Ireland has no passport
and this variable excludes Scotland. Setting `require_benefits=false` therefore
restores eligibility only for the remaining non-passported households, a
narrower future-year effect than the original benefit-only restriction costed
by OBR. This is `partial` and tags `baseline_vintage`. The registry's
"recovery" shorthand refers to this eligibility rule; the engine does not
implement it as a separate HMRC recovery charge. Do not assume its residual
national effect is zero.

For a reversal, the executed alternate world is the reversal. Preserve its
literal delta against the certified world, and score the announced measure as
its negative:

```text
literal = gain_to_exchequer(reversal - certified)
announced_effect = -literal
```

The saved `totals.baseline` and `totals.reform` are in announcement order:
pre-measure world, then certified current law. The literal reversal delta is
kept separately in `literal_reform_minus_baseline` and
`literal_reversal_minus_certified_gbp`.

A forward `pe_reform_delta` applies an announced change absent from the
certified world. A `delta_on_modified_baseline` executes an explicit
`pe_baseline_modifier` and `pe_reform_delta` for mixed worlds. A package
composes registered legs, checking that overlapping paths specify the same
values. Its source rows still occur once: components do not get duplicate
claims or contribute a synthetic OBR total.

Positive effects mean gains to the Exchequer. A tax head uses
`reform - baseline`; a spending head uses its negative. Record each head's
variables and fiscal channel explicitly. The measure total is the sum of its
declared head effects; it is not automatically the complete published Budget
costing. Employer NICs also changes wages at the pinned incidence setting,
so the Income Tax channel can move. That is a construction scope difference,
not proof that OBR omitted wage incidence.

For employer NICs, `gov.contrib.policyengine.employer_ni.employee_incidence=1`
assigns the full wage adjustment to employees holding employer cost fixed.
Thus "static" here retains this pinned rule; it does not mean fixed wages.
The existing `employee_incidence_and_base` recipe in
`obr_divergence_axes.json` distinguishes this whole PE wage channel from the
PE–OBR incidence difference. OBR's database notes report direct measure
costings and exclude separately reported indirect macroeconomic effects.
Tag the construction and `head_scope` difference without attributing an
unsized percentage of the gap to it.

The [source-head audit](../../results/uk/events/SOURCE_HEAD_AUDIT.md) checked
the original workbook's titles, tax heads, FY columns and units. Its real
FY 2026–27 cells illustrate why a head comparison is not a package total:

| Package / head | Workbook cell | OBR £m |
|---|---|---:|
| CGT main rates and reliefs / Capital gains tax | BI2401 | 95.778978 |
| Same CGT package / Income tax | BI2403 | 1,262.326238 |
| Same CGT package / Stamp duty | BI2402 | -65.673195 |
| SDLT additional-home surcharge / Stamp duty | BI2395 | 334.228735 |
| Employer NICs package / Income tax | BI2398 | -312.921791 |

All cells are GBP millions, converted once to GBP. The £95.8m CGT cell is a
genuine tax-head costing; its package also has separate Income Tax and Stamp
Duty effects. The PE CGT leg pools gain types and leaves those source heads
uncomputed. The SDLT leg omits the source package's CGT/IHT interactions,
corporate purchasers and transactions response. These are explicit partial
scope limits, not evidence that the large raw ratios are engine defects.

## Years and worlds

The bundle is one `populace_uk_2023.h5` population, compatible with
`policyengine-uk ==2.89.2` and `policyengine-core ==3.27.1`. Use the managed
loader version `policyengine ==5.0.2` recorded in the existing mode-2 artifacts;
the later loader's bundle registry can select a different dataset. Its identity and size are fixed in
`data/uk/certified_bundle.json`. It is not a collection of independently
certified historical or future populations.

Use the start year Y of a source FY Y–(Y+1) as the population-input year.
Keep source FYs before 2023–24 in the registry accounting, but leave them
uncomputed on this track. Do not infer support from successful parameter
lookup alone. Read the managed loader, dataset time periods, income and
weight uprating, and the engine's parameter and formula histories; retain
those findings in [YEARS.md](YEARS.md). A future-year simulation projects
the certified 2023 records using the pinned engine's later targets and rules.
The pinned `policyengine_uk/data/economic_assumptions.py` extends a single-year
dataset from its base year through 2030, retaining the same population and
applying the indices in `uprating_indices.yaml`. The legacy managed-loader
conversion uses the HDF5's first time period, then invokes that extension.
`build_from_multi_year_dataset` loads each extended year's inputs explicitly.
The pin's `parameters/gov/economic_assumptions/yoy_growth.yaml` uses outturn
through 2024 and March 2026 OBR forecast growth for 2025–2030. The usable
projection window for this 2023 bundle is therefore CY 2023–2030; earlier and
later years are outside this track's supported data window. These projected
years remain subject to the population-vintage limitation.

It does not reproduce the event-vintage OBR world. Each registry's
`calendar_years` is the permitted execution window; compute rejects requests
outside that window.

Use every supported costing year, even if the first year's effect is zero.
Government policy parameters undergo the pinned engine's fiscal conversion:
after uprating and backdating, `convert_to_fiscal_year_parameters` samples
each parameter at 30 April of Y and applies that value across annual period
Y. Parameter reforms undergo the same processing. Thus the model combines
calendar-year population inputs with an April policy snapshot. Inspect the
processed tax-benefit system or simulation; raw YAML date schedules alone
do not establish the executed policy.

Annual modelling can miss part-year commencement: Autumn Statement 2023's
January 2024 NICs cut falls in FY 2023–24 while the processed April 2023
snapshot remains unchanged. In processed 2024, the employee NICs rate is
8% throughout the annual period, reflecting the later April 2024 cut.
Keep the source FY and the calendar proxy visible and tag the timing axis.
Do not silently move the source claim to a different year.

## Axis tagging and explained share

Every source comparison row tags `population_vintage`: OBR used the forecast
available at that event; the certified 2023 population is calibrated to later
targets and then uprated. This axis is named, not repaired in track 1.
`baseline_vintage` separately names certified-world versus announcement-policy
baseline differences. The other standard tags are `behavioural_adjustment`
(static versus behavioural), `cy_proxies_fy`, and `head_scope`. Partial legs
also carry `construction_scope`. Definitions and evidence pointers live in
`data/uk/obr_divergence_axes.json`; the six existing mode-2 component records
are preserved.

The comparison reports signed PE/OBR bins: both zero, OBR zero, PE zero,
opposite sign, or same-sign ratios below 0.5, 0.5–0.8, 0.8–1.25, 1.25–2,
and at least 2. These are descriptions, not success criteria.

Axis-tagged coverage is the count or absolute gap amount carrying relevant
tags. Explained share needs evidence-backed, additive, sized components that
cover every relevant axis. The event pipeline withholds it while any relevant
axis is unsized, any component masks the gap, components overlap, the gap is
zero, or the implied share lies outside [0, 1]. Component status `sized` means
a verbatim primary-source cell; arithmetic over quoted cells is `derived` and
must retain its formula. A computed component retains its executor's
derivation and provenance. Without a complete decomposition the remainder is
`residual_plus_unsized`, which is an investigation queue, not an engine-error
estimate.

## Accounting and verification

Test these identities across the event and within every FY:

```text
multiset(source-row ids in) = multiset(source-row ids classified), once each
rows in = rows classified
net GBP in = net GBP classified
absolute GBP in = absolute GBP classified
```

The builder uses `Decimal` from the original source value strings to avoid
cancellation concealing a dropped cell. Each class's measure count, source-row
count, net GBP and absolute GBP are retained. Across all heads and costing
years, those amounts are accounting quantities, not an annual Budget total.

Staging verifies raw head aggregates, literal reversal orientation, head
sums, registry identity and certified digest against the compute manifest.
Comparison verifies the complete staged source-row universe, source values,
the staging manifest, artifact digests and head effects again. Deterministic
numerical artifacts contain no timestamps, elapsed seconds or process memory;
those operational facts belong in `RUN_LOG.json`. Repeat one real
(measure, year) run and compare SHA-256 values. Existing AB2025 registry,
dry-run and staging outputs must remain byte-identical after shared-code edits.

Run the engine-free tests and the pinned integration checks:

```bash
.venv-replay/bin/python -m pytest tests/test_uk_event_registry.py tests/test_uk_event_compute.py tests/test_uk_event_comparison.py tests/test_uk_replay_legacy.py
PYTHONPATH=. .venv-replay/bin/python pipeline/build_uk_event_registry.py --event autumn_budget_2024 --check
```

The properties include row/GBP conservation, ratio scale and sign invariance,
reversal sign involution, head sums, residual accounting and deterministic
serialization. The legacy AB2025 regression tests remain part of the check.

## Commands and compute budget

Build a Python 3.12 uv environment in the assigned workspace and install the
managed runner with these exact compatibility pins:

```bash
UV_CACHE_DIR=.venv-uv-cache uv venv --python 3.12 .venv-replay
UV_CACHE_DIR=.venv-uv-cache uv pip install --python .venv-replay/bin/python 'policyengine==5.0.2' 'policyengine-uk==2.89.2' 'policyengine-core==3.27.1' pytest hypothesis pyyaml
```

Force `HF_HUB_OFFLINE=1`,
`HF_DATASETS_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1` before importing the engine.
The scripts also force those settings. They resolve the managed release from
the installed loader's bundled UK manifest, then find the pinned HDF5 in the
local `datasets--policyengine--populace-uk-private` Hugging Face cache and
hash it before and after simulations. No matching digest means no run.
The loader's separate release-metadata request does not obey those offline
flags; the Modal adapter blocks runtime network so it uses the audited
packaged certification fallback.
Use a writable uv cache within the workspace if the default cache is outside
the sandbox.

For one event:

```bash
PYTHONPATH=. .venv-replay/bin/python pipeline/build_uk_event_registry.py --event autumn_budget_2024
PYTHONPATH=. .venv-replay/bin/python pipeline/compute_uk_event.py --event autumn_budget_2024 --dry-run
PYTHONPATH=. .venv-replay/bin/python pipeline/compute_uk_event.py --event autumn_budget_2024 --workers 1
PYTHONPATH=. .venv-replay/bin/python pipeline/stage_uk_event.py --event autumn_budget_2024
PYTHONPATH=. .venv-replay/bin/python pipeline/compare_uk_event.py --event autumn_budget_2024 --summary
```

Use `--measures <measure_key> --years <Y>` for a minimal reproducer or a
determinism check, with a separate output directory so the canonical event
receipts stay intact. For example:

```bash
PYTHONPATH=. .venv-replay/bin/python pipeline/compute_uk_event.py --event autumn_budget_2024 --measures autumn_budget_2024__private_school_vat_20pct --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/autumn_budget_2024/private_school_vat_2026
```

Compare the new artifact's SHA-256 with the same measure-year file in the
event directory. Per-year progress receipts bind each completed artifact's
SHA after it is written. `--resume` can retain those verified pairs even if an
interrupted run did not finish `RUN_MANIFEST.json`; it ignores unreceipted
files. Their registry and certified-dataset identities must still match.
A focused rerun without `--resume` uses an explicit separate output directory
and recomputes the requested pairs. When a default-directory manifest already
exists, focused selection requires `--resume` or an explicit output directory;
`--resume` retains other SHA-bound completed pairs. Run no more than two simulations
concurrently on the shared Mac, counting national and synthetic diagnostic
runs together. Start with `--workers 1` on the shared host; use `--workers 2`
only when the host has capacity and no other lane is simulating. Each worker
holds one live managed simulation and reuses one certified baseline
extraction per year across measures. Keep independently launched event
processes within that same global two-simulation cap. Follow the requested event order: Autumn Budget 2024,
Autumn Statement 2023, Spring Budget 2024, Spring Statement 2025, then Spring
Budget 2023.

Expected run time is proportional to supported years times changed worlds,
plus one baseline per year. Historical mode-2 runs recorded a 36.99s median
baseline and a 68.03s median alternate (60.73–260.95s range). The historical
Autumn Budget 2024 NICs 2026 baseline took 65.60s at 4.34GiB, and its alternate
took 64.65s at 10.63GiB, recorded in the
[mode-2 artifact](../../results/uk/obr_costings/autumn_budget_2024__employer_nics_package_2026.json).
The medians summarize the checked-in mode-2 artifacts' `performance` fields,
deduplicating five baseline records and using 94 alternate records. Six
baselines plus thirty alternates suggest roughly
40 minutes on a quiet host, excluding preflight overhead; this is a historical
planning estimate. The current shared host took about twenty minutes for
preflight alone, and the replay moved to Modal after the local two-worker
launch required retrying with one worker. The first Modal private-school VAT
2026 replay recorded a 70.739s certified baseline, a 124.811s alternate,
208.145s in the generic CLI, and 212.351s across the remote worker. Those are
one measure-year's observations, not a full-event ETA. Actual full-event
wall time remains pending. Exact observed baseline and measure seconds are
saved in each event's `RUN_LOG.json`; use those measured timings for the next
lane. Registry accounting, staging
and comparison are engine-free; the builder validates parameters and variables
against the pinned engine.

This replay now uses the isolated UK Modal adapter after its offline
preflight and first numerical check completed. The inspected [Modal runner in
PR #53](https://github.com/PolicyEngine/policyengine-scorecard/pull/53), at
head `50b426055049cb42105200c268ca9ea46075f544`, is open and US-specific:
its [backfill driver](https://github.com/PolicyEngine/policyengine-scorecard/blob/50b426055049cb42105200c268ca9ea46075f544/tools/reform_validation/backfill.py)
hardcodes the populace-us repository and 2024 period and loads a
`USSingleYearDataset`; the [Modal app](https://github.com/PolicyEngine/policyengine-scorecard/blob/50b426055049cb42105200c268ca9ea46075f544/tools/reform_validation/modal_backfill_app.py)
installs the US engine from its manifest, and the [workflow](https://github.com/PolicyEngine/policyengine-scorecard/blob/50b426055049cb42105200c268ca9ea46075f544/.github/workflows/reform-validation-backfill.yml)
selects US releases. Its
hash verification protects that US artifact, but it has no UK event/bundle
interface, pinned UK environment or Hugging Face offline setup, and it fetches
remote metadata and data. The isolated `pipeline/modal_uk_event.py` adapter
uses the unchanged UK replay CLI instead. Its actual preflight verified the
complete pinned environment, exact certified build and digest, and packaged
certification with runtime network blocked. Its first nonzero private-school
VAT 2026 artifact is byte-identical to the local artifact, SHA-256
`48666307c1ff045f07b39510c1dc22ab46cbd4d814320c34572d69e0a55ea931`.
Its second fresh remote repeat produced the same bytes. See
[the determinism evidence](DETERMINISM.md) for the saved receipts and the
scope of that check. Both repeats bind the original uploaded registry;
subsequent classification corrections change artifact metadata hashes and
require new receipts. A focused result does not establish full event
completion; that requires the full thirty-pair manifest.

The adapter needs a separate control environment because its
serialized function must use the remote SDK interpreter's Python 3.12 minor
version. The local compute and control environments use Python 3.12.14;
the remote uv venv pins Python 3.12.13, available as a Linux x86_64 GNU
download in uv's catalog. `UV_CACHE_DIR=.venv-uv-cache uv python list 3.12 --all-versions --all-platforms
--all-arches --only-downloads --show-urls --offline` records that distinction;
the [standalone Python download](https://releases.astral.sh/github/python-build-standalone/releases/download/20260414/cpython-3.12.13%2B20260414-x86_64-unknown-linux-gnu-install_only_stripped.tar.gz)
is explicit. The wrapper's runtime receipt records the actual patch and
platform. The actual Linux 3.12.13 VAT artifact matched the local macOS
3.12.14 artifact byte-for-byte. This establishes the observed measure-year,
not a blanket guarantee for every platform or measure. The remote venv
installs the complete checked-in `requirements.txt` freeze; the model,
numerical dependencies and certified data pins are unchanged.
Its one container has two
CPUs, 32GiB memory, a 10,800-second timeout, one input and one replay worker.
Only allowlisted source files, the certified H5 and its single HF revision
ref are mounted. Runtime network is blocked, Hugging Face offline mode is
forced, no credentials are forwarded, and the existing managed loader's
release identity and pre/post simulation hash gates remain binding. See
[the offline cache audit](OFFLINE_BUNDLE_AUDIT.md) for the packaged
certification fallback.

Inspect the input plan and then run preflight without simulation:

```bash
UV_CACHE_DIR=.venv-uv-cache uv venv --python 3.12.14 .venv-replay-checks/modal-control
UV_CACHE_DIR=.venv-uv-cache uv pip install --python .venv-replay-checks/modal-control/bin/python 'modal==1.3.2'
python3 -m pipeline.modal_uk_event --event autumn_budget_2024 --plan
.venv-replay-checks/modal-control/bin/python -m pipeline.modal_uk_event --event autumn_budget_2024 --preflight-only --output-dir .venv-replay-checks/modal/ab24/preflight --download-root .venv-replay-checks/modal-downloads/preflight --execute
```

After validating that preflight receipt, recompute one real measure-year
twice in separate directories. Compare the numerical artifact bytes, while
keeping observational `RUN_LOG.json` and `MODAL_RECEIPT.json` outside that
determinism comparison:

```bash
.venv-replay-checks/modal-control/bin/python -m pipeline.modal_uk_event --event autumn_budget_2024 --measures autumn_budget_2024__private_school_vat_20pct --years 2026 --output-dir .venv-replay-checks/modal/ab24/vat2026_repeat_a --download-root .venv-replay-checks/modal-downloads/repeat_a --execute
.venv-replay-checks/modal-control/bin/python -m pipeline.modal_uk_event --event autumn_budget_2024 --measures autumn_budget_2024__private_school_vat_20pct --years 2026 --output-dir .venv-replay-checks/modal/ab24/vat2026_repeat_b --download-root .venv-replay-checks/modal-downloads/repeat_b --execute
```

Compare the same measure-year with local artifacts as a separate platform
provenance check; retain any differences for investigation. After those
checks, a full event uses canonical paths inside the remote workspace:

```bash
.venv-replay-checks/modal-control/bin/python -m pipeline.modal_uk_event --event autumn_budget_2024 --download-root .venv-replay-checks/modal-downloads/full_ab24 --execute
```

The download prefix receives the returned ROOT-relative paths, so this
command writes locally under
`.venv-replay-checks/modal-downloads/full_ab24/results/uk/events/autumn_budget_2024/`
and preserves canonical path strings in receipts. The wrapper never writes
local canonical results. Validate downloaded input identities, artifact
hashes and staging invariants, then adopt the returned relative files
atomically only after the local event run has stopped. Keep raw receipts
for provenance. Each Modal invocation uses one replay worker. Count every
active invocation and local simulation toward the overall maximum of two;
separate invocations do not share a global concurrency gate. A full event
plus one focused repeat uses both slots. Remote wall time is recorded
separately in `MODAL_RECEIPT.json`; use the completed event's observed timings
when planning the next lane.

Each event writes deterministic numerical artifacts, `RUN_MANIFEST.json`,
`STAGED.jsonl`, `STAGING_MANIFEST.json`, `COMPARISON.csv`, `COMPARISON.json`,
`COMPARISON.md` and `COMPARISON_PROVENANCE.json` under
`results/uk/events/<slug>/`. Staging and comparison report the complete
executable measure-year grid, completed pair count and missing pairs; a
partial selection does not establish a completed event replay. `--summary`
checks comparison output hashes against their provenance, current registry
and axes hashes, staging receipts and numerical artifacts before aggregation.
Stale receipts stop summary generation. It writes
`results/uk/events/SUMMARY.md` by tax head and measure type and lists the
largest unexplained rows with variables and minimal replay commands. Registry-only
events stay visible with numerical replay marked incomplete. Add
engine-issue diagnoses only with runtime metadata, a checked-in assessment,
an existing issue, or a measured diagnostic. Leave issue filing to the main
session.

These event staging files are standalone comparison receipts. They preserve
the source-row inventory and do not attach counterparts to the app's
`external_scores` through `ingest_campaign`. That future integration requires
ingested claim ids and registered descriptors for the executed worlds; this
track's registry and artifact identities remain available for that work.

`pipeline/diagnose_uk_event_models.py` records small pinned reproductions of
specific model investigation candidates. It uses a two-person synthetic
Carer's Allowance example and direct parameter/formula inspection; it does
not run a national population simulation or claim to size a national gap.
Run it with `--output results/uk/events/MODEL_DIAGNOSTICS.json`, or use
`--case <diagnostic_id>` to print one candidate's evidence. Distinguish those
measured encoding findings from the largest raw unexplained national gaps.
The Carer's Allowance and UC cases each use a small synthetic simulation;
respect the same two-simulation concurrency limit when running them. Other
`--case` selections inspect only parameters and formula metadata.
`--from-json results/uk/events/MODEL_DIAGNOSTICS.json --report docs/uk_replay/MODEL_INVESTIGATIONS.md`
renders a report from saved observations without any engine calculation.
