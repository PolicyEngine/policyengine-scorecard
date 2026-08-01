# PolicyEngine scorecard

A template for comparing PolicyEngine/Populace estimates against every
external score or analysis the model can plausibly run — as a filterable,
honest scorecard. Every external number appears alongside its PolicyEngine
counterpart with the delta and any concept-mismatch annotation; the misses
stay on the page.

**Instance 1: Urban Institute's [State of the Safety
Net](https://apps.urban.org/features/state-safety-net/)** — nine programs
(SNAP, SSI, TANF, WIC, CCDF, housing, LIHEAP, EITC, refundable CTC) ×
eligibility/participation metrics × US + 50 states + DC + demographic
subgroups, plus the SPM poverty full-participation counterfactual.

## How it works

```
sources/<source-id>/
  source.json       registry entry: what the source is, method, period
  raw/              the source's own published data, as fetched
  adapter.py        raw → tidy external rows (one schema for all sources)
  annotations.json  concept-mismatch annotations; every one traces to
                    docs/, engine metadata, or a measured diagnostic
pipeline/
  compute_counterparts.py  PE metrics on the certified Populace artifact
                           (policyengine.py managed_microsimulation, Build P)
  build_comparison.py      join + derive rates/deltas → data/comparison.json
app/                       the scorecard UI (bun + vite + react + ui-kit)
docs/                      replication assessment + engine mechanics audit
```

Tidy row schema: `{source, program, metric, subgroup, variant, geography,
unit_concept, period, value}`. The PE side emits weighted counts only;
every rate and delta is derived in one place (`build_comparison.py`).

Status taxonomy — honesty made structural:

| status | meaning |
|---|---|
| `comparable` | PE measures the same concept |
| `constructed` | PE approximates the concept via a documented construction |
| `concept_mismatch` | PE value exists but measures a different concept |
| `pe_gap` | the model/artifact cannot produce this today |
| `not_computed` | producible but not yet in the pipeline |
| `suppressed` | the source suppressed the cell |

## Reproducing

Python side (requires the policyengine.py-managed environment; heavy —
respect the machine-wide sim lock):

```bash
python sources/urban-sotsn/adapter.py
simlock -- .venv-pe/bin/python pipeline/compute_counterparts.py
python pipeline/build_comparison.py
```

App:

```bash
cd app && bun install && bun dev
```

## Architecture for N sources

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — the registry/adapter
contract and the divergence-diagnosis stage that classifies each material
delta as PE gap, external-model issue, concept mismatch, or data vintage,
and drafts the fix.
