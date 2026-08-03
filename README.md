# PolicyEngine scorecard

Comparing PolicyEngine/Populace estimates against every external score or
analysis the model can plausibly run — as a filterable, honest scorecard.
Every external number appears alongside its PolicyEngine counterpart with
the delta and any concept-mismatch annotation; the misses stay on the page.
The register is descriptive: in model-vs-model comparison there is no right
answer, so divergence is decomposition material, never a verdict (issue #9).

**Sources so far** (42,270 claims in data/scorecard.db): Urban Institute's
[State of the Safety Net](https://apps.urban.org/features/state-safety-net/)
(30,004 claims — nine programs × eligibility/participation × US + states +
subgroups + the SPM full-participation counterfactual, with 7,912 PE
counterparts), plus the 2026-08-02 US harvest: JCT, CBO, TPC, Tax
Foundation, PWBM, Budget Lab, and CPSP (12,266 reform-score, baseline, and
poverty claims — cataloged, counterparts queued). UK sources land through
the same pipeline and appear in the app automatically once ingested.

## How it works

```
sources/<source-id>/       registry entry, raw data, adapter, annotations
scorecard_db/              THE source of truth: models + ingest modules
                           writing data/scorecard.db (claims × PE results
                           × diagnoses × lanes; `comparisons` view)
pipeline/
  compute_counterparts.py  PE metrics on the certified Populace artifact
                           (policyengine.py managed_microsimulation, Build P)
  build_comparison.py      platform join → data/comparison.json (Urban grid)
  export_db.py             scorecard.db → data/export/: index.json (sources
                           index + the four home tiles) and per-source row
                           slices consumed by the app
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

Export the database into the app's feeds (stdlib only — no venv needed):

```bash
python3 pipeline/export_db.py
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
