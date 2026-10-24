# Dashboard export of certified event replays

The UK Autumn Budget dashboard
([PolicyEngine/uk-autumn-budget-dashboard-2026](https://github.com/PolicyEngine/uk-autumn-budget-dashboard-2026))
can show past fiscal events beside the current Budget. It runs every figure
through its own publication pipeline, on its own certified model and data
pair. So what it takes from a replay is how each measure was built, not the
replay's numbers. `pipeline/export_uk_events_dashboard.py` writes that, one
file per event, from a certified replay namespace:

```bash
PYTHONPATH=. uv run --with numpy python pipeline/export_uk_events_dashboard.py \
    [--variant <variant_id>] [--events <slug> ...]
```

The output is `results/uk/dashboard_export/<variant_id>/<event>.json`,
plus `EXPORT_MANIFEST.json` with the digest of each file. Without `--variant`
the newest certified replay namespace is used. The committed export is for
`pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1`, covering the six events in its
corpus: 25 computed measures out of 426.

## What each file holds

- **Identity.** The event, its registry path and digest, and the variant:
  packages, dataset, data years, and the digests of the receipt, namespace
  manifest, run manifest and `COMPARISON.csv`. The supported and unsupported
  years come from the run manifest.
- **Every registry measure.** Each one carries its classification, its gap
  kind when it is not expressible, and the registry's reason for anything
  without a counterpart: missing legs, the out-of-scope reason, or the
  `pe_gap`. A measure whose class is computable but which has nothing to
  execute by design takes `compute_uk_ab2025.not_computable`'s reason.
- **The construction of each computed measure.** This is what the
  importer needs:
  - `kind`: either `reversal_on_certified_world` or
    `forward_delta_on_certified_world`;
  - each world's engine entry point and the parameter dictionary the replay
    submitted, merged across years (two years that disagree on a window are
    refused);
  - the construction revision, if one ran, and the `null_executed_as_no_limit`
    sentinels;
  - `executor_route`: `uc_health_element_refresh` when the construction
    changes `UC_HEALTH_ELEMENT_PARAMETER`, because
    `compute_uk_event.uc_health_scenario` refreshes Universal Credit's seeded
    cohort after the parameter change. An importer has to reproduce that route,
    not only the dictionary.
  - the declared fiscal heads.
- **Per year.** `measure_total_gbp`, the head effects, and the processed
  parameter values the engine reported (intended and processed, for each
  world), with the artifact path and digest. These are the replay's numbers
  on the replay's pair. The dashboard uses them only for the differential
  check described below.
- **The OBR side of every source row.** Each row carries the OBR value as an
  exact decimal, its class and `COMPARISON.csv` status. It also carries the
  replay's own counterpart, gap and ratio from `COMPARISON.csv`, named
  `replay_*` (including `replay_ratio_bin`) so that nothing reads them as the
  dashboard's figures.
- **Accounting.** The registry's source-inventory accounting, recomputed from
  the rows with arithmetic that refuses to round. It must equal the
  registry's recorded accounting exactly. It gives each class's measures,
  rows, net and absolute GBP, and exact shares (`"p/q"`) of the absolute GBP
  and of the measures. It also gives the rows by comparison status: of
  everything the OBR costed, how much has a computed counterpart.

Nothing household-level is read or written. The artifacts are national
aggregates, and the OBR rows are published costings.

## What the numbers mean

Each computed measure is costed on the replay's certified model and data. The
rest of the law is held at what that engine treats as current law, so these
are not the estimates made at the time of the event:

- **A reversal** undoes the measure in its baseline world, and its reform
  world is current law.
- **A forward delta** runs current law as its baseline world and adds the
  measure in its reform world.
- **Totals.** `measure_total_gbp` is the sum of the declared heads' effects.
  A positive value is a gain to the Exchequer.
- **Years.** Replay year Y is calendar year Y, the proxy for fiscal year
  Y-(Y+1).

So a measure later changed by another event is costed at the margin of
today's law. Two cases in the committed export:

- **Autumn Budget 2024 winter fuel means test.** It is costed with Autumn
  Budget 2025's £35,000 income test still in place.
- **The two 2p Class 1 employee NICs cuts.** The cuts in the Autumn Statement
  2023 and the Spring Budget 2024 each reverse 8% to 10% on the certified
  world, so they give the same totals. Each event's construction note says so.

## Checks before anything is written

The export reads only what the seal covers:

1. The variant record must validate, and its recomputed identity digest must
   match `REPLAY_RECEIPT.json`. The receipt and its integrity status must both
   be complete. It names the digest of `NAMESPACE_MANIFEST.json`, which names
   the digest of every file read: run manifests, provenance, `COMPARISON.csv`
   and artifacts. The corpus and namespace manifest must name the same event
   inventory; missing event files are refused.
2. Each run manifest's registry digest must equal the committed registry file,
   and so must `COMPARISON_PROVENANCE.json`'s.
3. Every artifact must belong to this event and variant, and to a measure the
   registry computes. Artifact measure/year pairs must be unique and equal
   the registry's supported-year grid. Data years must match the sealed run.
   Every `COMPARISON.csv` row must be a registry source row with the same OBR
   value; a measure without computation cannot own constructed rows.
4. Each computed measure's submitted worlds must equal the registry's
   construction under `compute_uk_event.annual_reform`, after applying any
   recorded construction revision and its specified window transformation.
   Revision evidence must match the revision registry. Each computed measure
   must also agree with its artifacts on the construction kind, entry points,
   sentinels and heads.

A legacy namespace (no processed-parameter evidence) and an uncertified
variant are refused.

## Invariants

`tests/test_export_uk_events_dashboard.py` checks these for every committed
export:

- **Regeneration.** The export regenerates byte for byte, and the manifest
  names each file by its digest.
- **Coverage.** Every registry measure appears once. It is computed exactly
  when the registry computes it, with one year per supported year. A measure
  that is not computed has a reason.
- **Construction direction.** A reversal submits a baseline-world dictionary
  and runs current law as its reform world. A forward delta does the opposite.
- **Totals.** Each year's total is the sum of its head effects.
- **Accounting.**
  - Classes partition the source rows, so their absolute and measure shares
    each sum to exactly 1.
  - Statuses partition the rows too.
  - The constructed rows' absolute GBP is no more than the computable
    classes'.
- **Closed shape.** The document has no field beyond the schema's.

Hypothesis properties cover the exact decimal text, shares of any partition,
sums that never round, and merging years in any order. The accounting is also
checked against an independent Fraction implementation over generated
registries. Tampered copies of a sealed namespace (an artifact,
`COMPARISON.csv`, the namespace manifest, the registry) are refused.

## How the dashboard uses it

The importer writes each computed measure into the dashboard's registry under
its event:

- **Reversal.** The baseline world's dictionary becomes the entry's
  `baseline_parameter_changes`, with no reform changes.
- **Forward delta.** The dictionary becomes its `parameter_changes`.

These dictionaries are the replay's literal submissions. Their timing meaning
therefore depends on the engine and entry point recorded in the export. An
importer must adapt that route to its engine and must not pass the exported
dictionaries through `compute_uk_event.annual_reform` again. That function
maps a window's start to the first 1 January on or after it: for example,
annualising CGT's exported `2024-04-06.2036-04-05` window again produces
`2025-01-01.2036-12-31`, shifting its first year from 2024 to 2025. After
adapting the route, read back each parameter for each supported year and
compare it with that world's exported `processed_parameter_values` intended
value. The per-year intended values are the timing comparison target.

The dashboard's own pipeline then produces the full table set on the
dashboard's pair. Measures without a construction stay listed as not modelled,
with their class and reason. The page links to
[policyengine-scorecard.vercel.app](https://policyengine-scorecard.vercel.app)
for the replay itself rather than repeating it.

The dashboard pair differs from this variant's: as of 24 October 2026 it is
policyengine 6.10.2 with policyengine-uk 2.132.6 and the Microcosm UK 2024-25
build. A national figure from the dashboard can therefore differ from
`measure_total_gbp` because of the pair, not the construction. Until a
replay is certified on the dashboard's pair, the differential check works at
the parameter level. In the world where the dictionary is submitted, the
dashboard's processed value for each parameter must equal the intended value
recorded here. In the current-law world, a different value is pair drift: the
check reports it rather than hiding it. Once a replay on the dashboard's pair
exists, export it with `--variant`; the national totals can then be compared
within a stated tolerance.
