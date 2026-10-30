# CenTax: removing the £100,000 childcare limit (lane `uk-childcare-100k`)

CenTax's costing of removing the £100,000 adjusted-net-income limit on the
working-parent free childcare hours in England (Advani, Flew, Pepin-Hall and
Summers, [Removing the childcare cliff-edge](https://centax.org.uk/wp-content/uploads/2026/09/AdvaniFlewPepin-HallSummers2026_Removing-the-childcare-cliff-edge.pdf),
September 2026, Table 4.2), set against PolicyEngine's static cost of the
same reform on the scorecard's certified UK pair. The lane also carries the
Centre for British Progress estimate the report reviews
([`../cbp-rates-and-wrongs/`](../cbp-rates-and-wrongs/)).

## What is here

| file | what it is |
|---|---|
| `raw/AdvaniFlewPepin-HallSummers2026_Removing-the-childcare-cliff-edge.pdf` | the report as published (sha256 in `source.json`) |
| `raw/pages_layout.txt` | `pdftotext -layout` of the twelve pages the rows and annotations cite; a test re-extracts them from the PDF |
| `adapter.py` | Table 4.2 → `data/externals/centax-childcare-100k.json` (36 cells), with a sum check, a cross-check against Table 4.3 and a check of the prose under the table |
| `annotations.json` | concept differences, each with its basis; the one that sets a row's status is marked |
| `pe/published_dashboard.json` | PolicyEngine's published figure for the same reform, kept as history |

The PolicyEngine side is `pipeline/compute_uk_childcare_100k.py`, which wrote
`results/uk/childcare_100k/<variant>.json`; the ingest is
`scorecard_db/ingest_uk_childcare_100k.py`.

## Years and scope

- CenTax names tax years by their later year: 2028 is 2027-28 and 2030 is
  2029-30 (editorial note, printed page 2). Claims key `period` on that
  later year, the repo's UK convention, and carry `fy`.
- The reform covers the free hours only. Tax-Free Childcare has its own
  £100,000 limit and is not part of it. The £500 Tax-Free Childcare
  addition in the report's Appendix D belongs to CBP's estimate.
- Both offers are England's. The counterparts sum each childcare head for
  people in English households: policyengine-uk 2.89.2 restricts the three
  free-hours offers to England but applies Tax-Free Childcare across the
  UK. Ingest checks that no free-hours head moves outside England.

## The comparison (£bn, negative = cost to the Exchequer)

| | 2027-28 | 2029-30 |
|---|---:|---:|
| CenTax static cost, central | −0.80 | −0.98 |
| CenTax net fiscal cost, central | −0.52 | −0.64 |
| PolicyEngine, certified pair (static) | −0.690 | −0.838 |
| PolicyEngine, published dashboard (static, history; on policyengine.org 12–21 October 2026) | −0.434 | −0.505 |
| PolicyEngine dashboard since PR #8 merged (1b83dd46, 24 October 2026; its own Vercel deployment, not policyengine.org; not attached) | −0.902 | −1.037 |

The certified pair is the default replay variant: populace-uk build
`populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z` with policyengine-uk
2.89.2 (`data/uk/certified_bundle.json`). Statuses:

- static against static: `comparable` (all three scenarios, which differ in
  CenTax's assumed bunching friction; PolicyEngine has one current-law
  distribution);
- CenTax's net cost, which adds the intensive and extensive behavioural
  gains: `concept_mismatch`;
- the published dashboard figure: `constructed` (the dashboard applied six
  local corrections to policyengine-uk 2.102.3), and older than the
  certified run, so it shows in the history rather than as the latest.
  policyengine.org served it from 12 October 2026 until it took the page
  down on 21 October while the dashboard's costing is revised
  (policyengine-app-v2 de2b07cf); the path redirects to /uk/research.
  Since [uk-childcare-100k-threshold#8](https://github.com/PolicyEngine/uk-childcare-100k-threshold/pull/8)
  merged on 24 October, the dashboard's own deployment serves £0.902bn and
  £1.037bn on Microcosm's 23 October release (a133f37a, policyengine-uk
  2.147.2), which is in no certified pair. The row records it and does not
  attach it; when policyengine.org serves the page again, its figure is a
  new published row.

CenTax's two behavioural margins are on the page without a PolicyEngine
value. Their `pe_missing` says why: this lane's counterparts are static
runs.

## Why PolicyEngine is below CenTax

The central static rows carry a `pe_gap` diagnosis linked to
[microcosm#1126](https://github.com/PolicyEngine/microcosm/issues/1126).
Measured on the certified pair: families receiving the extended hours use a
weighted mean of 15.3 of the 30 weekly hours (`maximum_extended_childcare_hours_usage`);
#1126 puts DfE's mean at about 28.5 and identifies the draw as the main
reason PolicyEngine's free-hours spending is low. With every family at the
full 30 hours, the same reform costs £1.40bn in 2027-28 and £1.72bn in
2029-30 on this pair (a diagnostic run, never attached). Ingest writes that
figure only when both full-use worlds record it: the input set to 30 before
any holder that reads it was filled, read back at 30, and the main world's
reform and executed limits on 30 April of the year. Smaller factors on
our side, recorded on each result: the engine switches universal and
targeted hours off once a family qualifies for the extended hours
([policyengine-uk#1930](https://github.com/PolicyEngine/policyengine-uk/issues/1930),
changed after the pin by [policyengine-uk#2177](https://github.com/PolicyEngine/policyengine-uk/pull/2177)),
and no child under 1 receives hours.

The published dashboard figure ran on the 2 October Microcosm release that
#1126 examines, with the same draw. The fix merged in microcosm on 16
October 2026 (microcosm#1299). The certified pair was built on 19 June 2026,
before it. [policyengine.py#685](https://github.com/PolicyEngine/policyengine.py/pull/685)
(merged 21 October 2026) certified a Microcosm pair with the fixed draw:
national cut `microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71` with
policyengine-uk 2.132.6, which policyengine.py 6.11.0 (25 October) still
pins. This repository has it only as an experiment population, not a replay
variant, so this lane has not run it yet:
[#228](https://github.com/PolicyEngine/policyengine-scorecard/issues/228).
Until it does, the latest result is the 19 June pair's and the row shows
that pair's miss.

To add a pair, run the compute script with `--variant <id>` in that
variant's environment. The run id defaults to
`childcare-100k-<variant>-<UTC start second>`. Two runs of one variant
started in the same second would share it, and ingest refuses two
artifacts with one run id. The artifact goes beside this one in
`results/uk/childcare_100k/`. Before ingest takes it, check each note whose
basis is the engine or a run at the new pin.
These are the entries with a `variants` list in both sources'
`annotations.json` and in `results/uk/childcare_100k/construction_annotations.json`.
Add the pair to the notes that still hold, and write replacements for those
that do not. Then add the pair's `verified_pairs` entry, which says why its
run is static, what is known about its hours draw, and the `pe_gap`
diagnosis, if one still applies. Ingest refuses an artifact on a pair with
no such entry. It attaches each note only to results on the pairs it names,
and it refuses an artifact whose package, release-bundle or dataset identity
differs from its variant record. It keeps every certified artifact's run.
Each claim's latest result is the newest run that computed the claim's
year; older runs and the published figure stay in the history. Run ids may
not start with `platform-grid-` in any letter case: the comparisons view
prefers those runs within a data bundle, and its `LIKE` ignores ASCII case.
Each `computed_at` must be a distinct UTC time, written as
`datetime.isoformat()` writes it, so that text order is time order.

## Never a calibration target

Both sources are held out (`relationships.uk_relationship`). A reform
estimate from another model is never a calibration target under the
2026-08-02 rulings. `never_calibrate()` is keyed on metric and covers the
poverty family, so `tests/test_uk_childcare_100k.py` checks the rule on the
built database for every source: any claim that scores a world other than
the baseline is held out.

## CenTax moments as calibration targets

Arun Advani suggested calibrating PolicyEngine to CenTax's moments. Under
the 2026-08-02 rulings that splits in two:

- **Never targets:** CenTax's model outputs. That covers every Table 4.2
  cell, including the bunching counts (projections for 2028 and 2030 from
  the bunching model), and estimator outputs such as the 2,610 excess
  parents bunching in 2022 (key findings, printed page 3: a comparison
  with a counterfactual density).
- **Possible targets, if published as administrative quantities:** genuine
  HMRC administrative counts, the quadrant the rulings allow (admin
  tax-benefit quantities). The report quotes some, rounded, in prose, such
  as about 11,000 parents in 2022 with a live childcare account for part of
  the year and an actual adjusted net income over £100,000 (printed page 42).
  A target needs CenTax (or HMRC) to publish such counts as administrative
  tabulations with a definition, a year and a population, not a rounded
  figure in a policy report.

Decided 25 October 2026: CenTax's administrative tabulations become
calibration targets in Microcosm, where that work happens; its model
outputs stay out. Nothing changes in this lane: both sources stay held out,
and no costing here is ever a target.

## Reproducing

```bash
python sources/centax-childcare-100k/adapter.py
python sources/cbp-rates-and-wrongs/adapter.py
# the counterpart: the certified environment (docs/uk_replay/requirements.txt)
# and the certified artifact in the Hugging Face cache, offline; the run
# copies it into a verified writable mirror under data/uk/policyengine-local/
# (about 1.3 GB, git-ignored) and hashes the file each simulation reads
PYTHONPATH=. .venv-pe289m/bin/python pipeline/compute_uk_childcare_100k.py
PYTHONPATH=. python -m scorecard_db.ingest_uk_childcare_100k data/scorecard.db
```
