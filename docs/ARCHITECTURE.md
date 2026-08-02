# Scorecard architecture: the N-source template

The scorecard is a template for a full agentic loop: for every external score
or analysis PolicyEngine can plausibly run, put each published number next to
its PolicyEngine counterpart, classify every material difference, and turn the
classification into a fix — a PolicyEngine issue/PR when the gap is ours, an
upstream report when an open-source external model is wrong, or a documented
concept annotation when the numbers measure different things.

Instance 1 (Urban's State of the Safety Net) exercises every stage; this
document is the contract that makes instance N cheap.

## The loop

```
┌─ sources/<id>/ ─────────────┐
│ source.json   registry      │   1. fetch & pin the external data
│ raw/          as published  │
│ adapter.py    → tidy rows   │   2. one schema for every source
│ annotations.json            │   3. concept deltas, traceable
└─────────────┬───────────────┘
              ▼
 pipeline/compute_counterparts.py   4. PE metrics on the certified artifact
              ▼                        (counts only; constructions logged)
 pipeline/build_comparison.py       5. join, derive rates/deltas, attach
              ▼                        annotations, assign status
 data/comparison.json ──► app/      6. the scorecard — misses stay visible
              ▼
 diagnosis stage (agents)           7. classify material deltas, draft fixes
              ▼
 PE issues/PRs · upstream reports · new annotations · new targets
              └──────────► re-run the loop
```

## The tidy row schema (adapter contract)

Every adapter emits rows of exactly this shape; nothing downstream knows
anything source-specific except the counterpart mapping:

```json
{
  "source": "urban-sotsn",
  "program": "snap",
  "metric": "participation_rate",
  "subgroup": "age_0thr17",
  "variant": null,
  "geography": "CA",
  "unit_concept": "persons",
  "period": "2023 average month",
  "value": 0.542,
  "status": "ok | suppressed",
  "source_column": "provenance pointer into raw/"
}
```

Conventions: counts in raw units (adapter undoes source scaling), rates as
fractions, `subgroup` slugs shared across sources where concepts genuinely
match (age bands, race, disability), `variant` for source-side methodological
forks (e.g. TANF with/without solely-state-funded programs).

## The PE side

`compute_counterparts.py` emits **weighted counts only** — every rate, gap,
and delta is derived in `build_comparison.py`, so arithmetic has one home.
Rules (binding):

- Load through `policyengine.py` (`pe.us.managed_microsimulation()`), never a
  bare country-package Microsimulation — the certified artifact and the
  package default are different worlds.
- microdf auto-weighting only; subgroup/state cuts by boolean-array indexing
  of MicroSeries; cross-entity moves via `map_to`.
- Counterfactual runs (e.g. full participation) set inputs before any
  calculate, at the variable's own definition period (monthly variables get
  all 12 months), and verify the toggle took effect — the run log records
  post-set means.
- Every variable used gets its engine metadata (label, entity, period,
  documentation) recorded in `pe_meta.json`, so concept annotations cite the
  engine rather than memory.

## What may never become a target

Two standing rulings (Max, 2026-08-02), enforced in
`scorecard_db/relationships.py::never_calibrate`:

1. **Survey-derived statistics — poverty rates above all — are permanent
   calibration holdouts.** Populace exists to fix the survey's issues
   through imputation, computed taxes and benefits, and calibration to
   administrative systems; consuming a survey-derived statistic launders
   survey error back in and destroys the validation signal. Release gates
   may fail a certification on a held-out regression (doctrine point 3);
   fitting the statistic is categorically different and prohibited.
2. **Deviations from official poverty metrics are never inherently
   problematic.** A model that corrects benefit underreporting should, all
   else equal, sit below survey-based rates; divergence is expected by
   construction. Scorecard and diagnosis language must treat official
   numbers as comparators, not truth — direction and composition anomalies
   are investigation flags, not "misses".

## Status taxonomy + annotation traceability

Statuses: `comparable`, `constructed`, `concept_mismatch`, `pe_gap`,
`not_computed`, `suppressed` (see README table). Two invariants:

1. **Misses stay on the page.** Gap rows render alongside hits; the coverage
   spine makes the gray structurally inseparable from the teal.
2. **No fabricated mechanisms.** Every annotation carries a `basis` that is
   one of: a section of a checked-in assessment document, engine metadata
   recorded at runtime in `pe_meta.json`, a GitHub issue, or a measured
   diagnostic in this repo's data. If a claim about how either model works
   can't cite one of those, it doesn't ship.

## The diagnosis stage

Input: comparison rows with status `comparable`/`constructed` beyond
tolerance (the app's Divergences tab is the human view of the same queue).

Each divergence gets classified as exactly one of:

| class | meaning | fix artifact |
|---|---|---|
| `pe_gap` | our eligibility encoding, data, target surface, or take-up seeding is wrong/missing | PE issue + PR sketch (parameter/variable/target) |
| `external_model_issue` | the external model's construction looks wrong | open-source external → upstream issue/PR; closed-source (ATTIS) → comparison memo |
| `concept_mismatch` | the numbers measure different things | new/updated annotation in `annotations.json` |
| `data_vintage` | period or data-year difference explains the delta | annotation; optionally a matched-year re-run |

Operating rules for the agent stage:

- Frame prompts as defensive audits of our own model first ("what would make
  our number wrong?") before touching the external's methodology.
- Grind work (per-divergence investigation across engine code, parameters,
  admin sources) is dispatched to worker agents; the main loop only
  adjudicates classifications and owns anything that becomes an outward
  artifact (issue text, upstream report).
- A classification must name its evidence: the engine file/parameter, the
  admin series, or the assessment section it rests on. Unevidenced
  classifications stay open.
- Every classified divergence lands back in the dataset (a `diagnosis` field
  on the row) so the app can show it — the queue and its resolutions are the
  same page.

## Adding source N

1. `sources/<id>/`: fetch raw data, write `source.json`, write the adapter to
   the tidy schema, seed `annotations.json` with known concept deltas.
2. Extend the counterpart mapping in `build_comparison.py` (or, when a source
   needs new PE metrics, add emission blocks to `compute_counterparts.py`).
3. Run the pipeline; the app picks up new sources from the data with no UI
   work beyond labels.
4. Run the diagnosis stage on the new divergence queue.

### Designed-for future sources (not yet built)

| source | comparison unit | adapter shape | notes |
|---|---|---|---|
| TAXSIM (NBER) | record-level tax liability | run policyengine-taxsim on shared records; rows = aggregate match rates + named mismatch clusters | open source → upstream PRs possible; policyengine-taxsim already exists |
| FNS official SNAP state participation rates | state × year rates | direct table adapter | the natural held-out validation for SNAP (FNS state rates are not consumed by calibration) |
| SNAP QC | caseload composition | distributional rows (shares by hh type/income band) | needs a composition metric family |
| ASPE welfare indicators | TANF/SSI recipiency rates | direct table adapter | TRIM3-based — same family as Urban's TANF seed source |
| Census SPM reports | poverty rates by state/group | direct table adapter | anchors the poverty side independently of Urban |
| CBO / JCT scores | reform deltas (revenue/outlay) | per-provision adapter; needs a "reform" dimension added to the schema (`reform` column, null for baseline sources) | compares deltas, not levels |
| EUROMOD / UKMOD | UK/EU program aggregates | same schema, `country` column promoted from constant to key | requires policyengine.py UK managed sims |

Schema evolution implied: `country` and `reform` columns (constant today),
and a `composition` metric family for QC-style shares. Nothing else changes.

## Repo conventions

- Private-first; flip public only deliberately.
- `data/` artifacts are committed — the scorecard is a provenance artifact,
  and CI can re-derive them.
- App: bun + vite + react + `@policyengine/ui-kit` tokens; sentence case;
  counts/rates formatted centrally.
