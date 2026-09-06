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


## Instance 2: baseline moments — average tariff rates (Yale, TPC)

The scorecard's second claim class, `baseline_moment`: current-law
statistics published by external modelers, captured with the same
honesty machinery as reform scores. First population: average US
tariff rates —

- **Yale Budget Lab tariff-rate-tracker** (`weighted_etr`): effective
  statutory rates × fixed 2024 import weights, vintage pinned at the
  2026-06-09 publication (commit 39d394d).
- **TPC Tracking Trump Tariffs**: average statutory rate × fixed 2025
  weights, ex-AD/CVD, Datawrapper datasets version-pinned (aO4iG v44,
  MC81F v43 incl. by-authority types).
- **Our side**: the ex-post collections rate (Σ calculated duty /
  Σ customs value, monthly) from the Microcosm import-entry margins
  (exact-reconciled; microcosm #620) — today a `concept_mismatch`
  counterpart by design, with the fixed-base-vs-contemporaneous gap
  annotated; same-construct replications (our rates under each
  tracker's own definition) are the staged next counterparts, and
  by-authority decomposition arrives with the full-schedule rate
  generator (P5 charter).

Pipeline (additive; does not touch the Instance-1 build):

```bash
python sources/yale-tariff-tracker/adapter.py
python sources/tpc-tariffs/adapter.py
python pipeline/compute_tariff_counterparts.py   # parquet if present, else the committed extract
python pipeline/build_moments.py                 # -> app/public/data/moments.json
```

## Reproducing

Python side (requires the policyengine.py-managed environment; heavy —
respect the machine-wide sim lock):

```bash
python sources/urban-sotsn/adapter.py
simlock -- .venv-pe/bin/python pipeline/compute_counterparts.py
python pipeline/build_comparison.py
```

UK side (#40; adapters are stdlib-only except ukmod-stats, which needs
pypdf; the compute stage needs the managed policyengine-uk environment
and the certified populace-uk bundle):

```bash
python sources/dwp-takeup/adapter.py          # + hbai-poverty, hmrc-personal-tax,
python sources/obr-welfare/adapter.py         #   ukmod-stats
simlock -- .venv-pe/bin/python pipeline/compute_uk_counterparts.py 2025
```

The single positional argument is the policy year (default 2025); both the
baseline and fullpart runs always execute, and the script aborts rather than
writing output if any take-up-validated benefit fails to move under the
fullpart overrides — the movement check is per benefit, so one benefit
responding never blesses another's unchanged caseload.

App:

```bash
cd app && bun install && bun dev
```

## Deployment

The application is connected to the `policyengine-scorecard` Vercel project
through Vercel's native GitHub integration. Vercel builds from `app/` while
including the repository-level data used by the application's `prebuild`
script. Pull request branches receive preview deployments, and commits on
`main` create production deployments. The deployed application is served at
`/scorecard/`.

## Architecture for N sources

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — the registry/adapter
contract and the divergence-diagnosis stage that classifies each material
delta as PE gap, external-model issue, concept mismatch, or data vintage,
and drafts the fix.
