# Policy experiments on the modern population

Max decided cos d1817 on 21 October 2026: run past UK fiscal events on the
newest Microcosm UK population as a bank of real policy reforms, to find where
PolicyEngine UK breaks. These runs are **policy experiments on the modern
population**. They are not replays, and they are not PolicyEngine's costing of
any past event. [PLAN.md](PLAN.md#where-a-single-population-gives-a-usable-labelled-answer)
named this question `modern_population_sensitivity` and listed what it is good
for: construction QA and spotting sign and unit errors.

Certified replays are unchanged. `compute_uk_event.refuse_unexecutable` still
refuses every historical registry, and a historical event replays only on a
certified event population ([HISTORICAL_ADAPTER.md](HISTORICAL_ADAPTER.md)).
Event-year populations for true replays stay possible later (d1817).

## What an experiment is

An experiment takes one measure from an event's source-accounting registry
and expresses it as a parameter change on **modern law**: the current law of
the engine being tested. It runs that change on the modern population in each
year both the population and the event's costing window cover, and compares
the result with the OBR's costing of the original measure.

Two constructions exist, matching the replay's orientation rules
(`compute_uk_obr_costings.orient_exchequer_effect`):

| Construction | Modern law | The alternate world | Announced effect |
|---|---|---|---|
| `reversal_on_modern_law` | still contains the measure | restores the pre-measure policy, keeping every later change | `-(alternate - modern)` |
| `forward_on_modern_law` | lacks the measure (later reversed, or never commenced) | applies the measure | `alternate - modern` |

Positive effects are gains to the Exchequer, as everywhere in the scorecard.
Each construction states its pre-measure values and their sources. When later
policy changed the same parameter, the counterfactual keeps the later change
and removes only this measure's (for example, scaling a later-uprated amount
by the measure's own uprating ratio).

Events with a source-accounting registry (Autumn Budget 2021, Spring
Statement 2022, Autumn Statement 2022) bind it. Older events have no
registry, and building one would need an event-vintage selector first, so
their specs bind the [inventory](INVENTORY.md) (`data/uk/events/inventory.jsonl`)
instead: `load_registry` groups the event's inventory rows into the same
shape, converting GBP millions to GBP through each value's decimal string.

An experiment can name the `years` it runs. A parameter the engine
day-weights over the fiscal year (`fiscal_year_blend`, such as fuel duty)
needs a window covering whole fiscal years, so its experiments stop where
modern law's own schedule changes within a year.

## Populations

| Pairing | What it runs | What it is for |
|---|---|---|
| `certified_pair` | a policyengine.py release's model on the data cut certified for it | the experiment population proper |
| `model_swap` | a newer policyengine-uk on the same data cut | the newest model before a data cut is built for it; against the certified pair on the same data, it separates model changes from data |

A model swap is valid only where the data carries the newer model's inputs.
A variable the older model computed and the newer one expects from the data
is nil on the swap; the record lists them in `model_swap_input_gaps`, found by
comparing the two models' source with the data cut's columns (for 2.143.0 on
the interim cut: the additional-dwelling and non-residential purchase prices
and salary sacrifice returned to income).

A model swap's record names the bundle's model in `model_swap_of`. Its
artifacts record the installed model as `engine_version` and the data's
model as `data_built_with_model_version`. policyengine.py runs it with a
warning: offline, a data release certified for another model is marked
unverified rather than refused (`provenance/manifest.py`,
`certify_data_release_compatibility`).

## Nothing can be mistaken for a replay

| Replay | Experiment |
|---|---|
| Registry `data/uk/events/<event>_measures.json` | Spec `data/uk/experiments/<event>.json`, kind `uk_modern_population_policy_experiments` |
| Variant index `data/uk/replay_variants.json` | Population records `data/uk/experiments/populations.json`, status `experiment_population`, ids prefixed `exp-` |
| Results `results/uk/events/`, `results/uk/replays/<variant>/` | Results `results/uk/experiments/<population>/<event>/` |
| `RUN_MANIFEST.json`, receipts, seals | `EXPERIMENT_MANIFEST.json`, `FINDINGS.json`, `FINDINGS.md` |
| Joins published scores via `scorecard_db` | Never ingested |

- **The registry is not edited.** The spec binds it by SHA-256 and reads its
  source rows for the OBR side; its `execution` block keeps refusing replays.
- **Every output carries the label.** Each artifact, manifest and findings
  file has `kind`, `label: modern_population_sensitivity`, `is_replay: false`
  and the sentence "Policy experiment on the modern population: not a replay
  or a costing of <event>."
- **Separate code path.** `pipeline/uk_policy_experiment.py` never writes
  under `results/uk/events`, `results/uk/replays` or the variant index; a test
  checks the containment for any output path. Tests also check that the
  scorecard database build, the replay namespace scan and the results-PR
  builder never read `results/uk/experiments`.
- **A population is not a variant.** An experiment population record has the
  variant's identity shape (packages, wheel and RECORD digests, the packaged
  bundle manifest, the dataset digest, the requirements freeze) so the
  replay's environment checks apply, but it is never added to the variant
  index and never sealed.

## Runs

The runner reuses the replay's managed simulation path
(`compute_uk_event.run_sim`): policyengine.py's managed microsimulation, the
dataset's SHA-256 before and after every simulation, the dataset's year set
checked against the population record, and each touched parameter read back
from the simulation's own processed tree.

For each year it computes modern law once, then each experiment's alternate
world. A simulation that raises is recorded as a `crash` for that
experiment-year; the run continues. Simulations run on Modal
(`pipeline/modal_uk_experiment.py`), with runtime network blocked, and take
the replay's two shared simulation slots, so experiments and replays together
never run more than two simulations at once.

## Anomalies

Each experiment-year is classified by `classify()`, a pure function of the
artifact, the OBR rows and the bases. Severity `investigate` must get a
diagnosis before anything is called a bug; `check` and `note` are listed.

| Code | Severity | Condition |
|---|---|---|
| `crash` | investigate | The alternate world raised. |
| `reform_not_applied` | investigate | A touched parameter's processed value differs from the construction's intent: the reform route did not reach the simulation. |
| `construction_noop` | note | Every touched parameter already equals modern law that year, so the experiment has nothing to move (the measure is superseded on modern law). |
| `inert` | investigate if the OBR's mapped costing is at least £20m, else check | A parameter changed but the summed effect is under £1m. |
| `sign_mismatch` | investigate | The OBR's mapped costing is at least £20m and PolicyEngine's effect has the opposite sign, at least £5m and 10% of the OBR's. |
| `magnitude_outside_10x` | investigate | Scaled ratio outside [1/10, 10]. |
| `magnitude_outside_3x` | check | Scaled ratio outside [1/3, 3] but inside [1/10, 10]. |
| `obr_zero_pe_moves` | note | The OBR's mapped costing is under £1m but PolicyEngine's effect is at least £100m (usually cash timing or a costing window). |
| `mirror_mismatch` | investigate | Two experiments declared as mirrors (the same parameter change, opposite constructions) do not return exact negatives. |
| `modern_law_differs` | investigate | A touched parameter's processed current-law value differs from the value the construction assumed. |

Magnitude flags apply only when the experiment's `magnitude_check` is
`scaled`, the expected value is at least £100m, and the mapped heads hold at
least half of the OBR's costing that year. That share is measured on each
head's absolute value, so mapped heads that offset each other (an
incorporation response's NICs gain against its income tax loss) still count
as mapped. Threshold freezes and other
measures whose value depends on the event's own inflation forecast are
`sign_only`: PLAN.md names them as the case a modern population misleads on.

## When an engine's current law is not the assumed one

A construction may state the current-law values its counterfactual is
written against (`assumes_modern`), for example the 5pp additional-dwellings
surcharge, or the £125,140 dividend additional-rate threshold. When an
engine's processed value differs, the experiment-year gets
`modern_law_differs` (investigate), whatever its other codes. The effect
measures that engine's current law, not the measure.

## Integrity of the committed results

`findings` refuses a run whose manifest names another spec or registry, so
a corrected construction always forces a rerun. `adopt` checks every
download's receipt, bytes and manifest, and that the manifests agree, before
it copies anything. A test regenerates every committed `FINDINGS` and
`SUMMARY` file from the committed artifacts and requires identical bytes.

## Scaling the OBR's costing

The OBR costed each measure against its own forecast at the event. The
modern population is calibrated to a later economy. For each mapped head
group, the experiment scales the OBR's costing by

```text
scale = PE baseline of the group in year Y / OBR event-vintage forecast of the head for FY Y
```

when the group's PolicyEngine variables cover the whole OBR head
(`pe_base_comparable`, for example `income_tax` and Income tax). Otherwise it
uses the OBR's own vintage factor,

```text
scale = OBR newest forecast for FY Y / OBR event-vintage forecast for FY Y
```

and a group with no forecast series is unscaled. The forecasts are rows of the
OBR's Historical official forecasts database (Spring 2026 edition), extracted
with their cell references into `data/uk/experiments/obr_head_forecasts.json`.
The event-vintage rows are checked against the March 2025 edition that the
event vintage locks name. The scaled ratio is
`PolicyEngine effect / Σ (OBR costing × scale)` over the mapped groups.

The scaling is a screen for bugs, not a comparison of vintages: it absorbs
nominal growth and base level, not differences in rates, thresholds or
behaviour between the event's world and modern law. That is why the bands are
wide and why each flag needs a diagnosis.

A group's scale is that of its whole head. The NICs base includes employer
contributions, so Autumn Budget 2024's employer changes raise the scale from
2025-26 for measures that touch only employees or the self-employed: Budget
2017's Class 4 rise scales by 1.13 in 2024-25 and 1.40 in 2025-26.

## Summary

`pipeline/uk_policy_experiment.py summary` writes
`results/uk/experiments/<population>/SUMMARY.{json,md}`. It covers every
event's findings, the anomaly counts by diagnosis state and the mirror
checks. Mirrors compare each head group of PolicyEngine variables that both
experiments map; a group only one of them maps is not compared. It also lists
each comparable head's modern base against the OBR's newest forecast of the
same head, which screens the population itself.

## Diagnoses and findings

`data/uk/experiments/diagnoses.json` records each diagnosis: the anomaly, its
status (`expected`, `construction_corrected`, `model_bug`, `data_issue`,
`engine_route`), the evidence (a minimised reproduction, preferably a
synthetic household) and the policyengine-uk or Microcosm issue it became.
`pipeline/uk_policy_experiment.py findings` writes `FINDINGS.json` and
`FINDINGS.md` per event; [EXPERIMENTS.md](EXPERIMENTS.md) is the running log
across events.

## Invariants

The tests state and check these for every input:

1. **Orientation.** A reversal and a forward construction of the same raw
   difference give exact negatives, and a spending channel negates a tax
   channel.
2. **Head sums.** An experiment's total is the sum of its head effects.
3. **OBR accounting.** The mapped and unmapped OBR values of an experiment-year
   sum to the registry's rows for that measure and fiscal year, in `Decimal`.
4. **Classification.** `classify` is pure; negating both PolicyEngine's effect
   and the OBR's costing leaves the codes unchanged; scaling both by a positive
   factor (above the floors) leaves them unchanged; a ratio further from 1 than
   a flagged one is also flagged; `crash` and `inert` exclude sign and
   magnitude codes.
5. **Containment.** No output path resolves into a replay root
   (`results/uk/events`, `results/uk/replays`) of this checkout or any other,
   and none resolves inside the repository outside
   `results/uk/experiments/<population>/<event>/` and `.venv-replay-checks/`.
6. **Mirrors.** Mirrored experiments return exact negatives (checked on real
   runs in the findings).
7. **Regeneration.** Every committed `FINDINGS` and `SUMMARY` file
   regenerates byte for byte from the committed artifacts.
8. **Declared current law.** Where a model swap and its certified pair differ
   on the current law of a parameter a construction sets, the construction
   declares the law it assumes (`assumes_modern`) or sets the parameter
   outright (a list in the test, each entry with its reason).
