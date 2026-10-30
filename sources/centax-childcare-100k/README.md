# CenTax: removing the £100,000 childcare limit (lane `uk-childcare-100k`)

CenTax's costing of removing the £100,000 adjusted-net-income limit on the
working-parent free childcare hours in England (Advani, Flew, Pepin-Hall and
Summers, [Removing the childcare cliff-edge](https://centax.org.uk/wp-content/uploads/2026/09/AdvaniFlewPepin-HallSummers2026_Removing-the-childcare-cliff-edge.pdf),
September 2026, Table 4.2), set against PolicyEngine's static cost of the
same reform on certified UK pairs. The lane also carries the
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
  people in English households: policyengine-uk restricts the three
  free-hours offers to England but applies Tax-Free Childcare across the
  UK. Ingest checks that no free-hours head moves outside England.

## The comparison (£bn, negative = cost to the Exchequer)

| | 2027-28 | 2029-30 |
|---|---:|---:|
| CenTax static cost, central | −0.80 | −0.98 |
| CenTax net fiscal cost, central | −0.52 | −0.64 |
| PolicyEngine, policyengine.py 6.11.0's certified pair (static) | −1.007 | −1.225 |
| PolicyEngine, 19 June certified pair (static, history) | −0.690 | −0.838 |
| PolicyEngine, published dashboard (static, history; on policyengine.org 12–21 October 2026) | −0.434 | −0.505 |
| PolicyEngine dashboard since PR #8 merged (1b83dd46, 24 October 2026; its own Vercel deployment, not policyengine.org; not attached) | −0.902 | −1.037 |

The latest result comes from the pair policyengine.py 6.11.0 certifies:
national cut `microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71` with
policyengine-uk 2.132.6 (`data/uk/certified_pairs.json`). The history keeps
the 19 June run on the default replay variant: populace-uk build
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

## Why PolicyEngine estimates a higher cost

On the latest pair, PolicyEngine's static cost exceeds CenTax's by 26% in
2027-28 and 25% in 2029-30. The central static rows carry a `pe_gap`
diagnosis linked to [microcosm#1338](https://github.com/PolicyEngine/microcosm/pull/1338).

| £bn of cost | 2027-28 | 2029-30 |
|---|---:|---:|
| Extended hours | 0.864 | 1.065 |
| Universal hours | 0.143 | 0.159 |
| Targeted hours | 0.000 | 0.000 |
| PolicyEngine total | 1.007 | 1.225 |
| CenTax static cost, central | 0.80 | 0.98 |

The universal change makes up 69% of the excess in 2027-28 and 65% in
2029-30, and this cut's take-up draws produce it. A family above £100,000 can
hold extended take-up true and universal take-up false.
It receives no universal hours under current law, though those hours have no
income limit, and receives them only once the reform makes it eligible for
the extended hours. Every pound of the universal change falls on such
children. microcosm#1338 (merged 23 October 2026, after this cut) nests the
universal draw under the extended one, so a family that claims the extended
hours also claims the universal hours.

The extended hours alone run 8% and 9% above CenTax. Two differences could
account for that remainder, and this run sizes neither:

- On this cut, copied high-income families inherit their hosts' take-up
  draws and children under 2 share the older children's take-up.
  microcosm#1338 changes both.
- The engine starts a working parent above £100,000 from no working-parent
  hours. CenTax nets off the hours that parents with live accounts already
  receive.

Usage no longer drives the gap. Families receiving the extended hours use a
weighted mean of 28.3 of the 30 weekly hours
(`maximum_extended_childcare_hours_usage`), against about 28.5 for DfE in
[microcosm#1126](https://github.com/PolicyEngine/microcosm/issues/1126).
With every family at the full 30 hours, the same reform costs £1.055bn in
2027-28 and £1.278bn in 2029-30 on this pair (a diagnostic run, never
attached). No child under 1 receives hours on this pair, because every age
is a whole number of years.

The 19 June pair ran about 14% below CenTax. Families on that pair drew a
weighted mean of 15.3 weekly hours, and #1126 identifies that draw as the
main reason PolicyEngine's free-hours spending ran low. At the full 30 hours
the same reform cost £1.40bn and £1.72bn on that pair. Its engine also
switched universal and targeted hours off once a family qualified for the
extended hours
([policyengine-uk#1930](https://github.com/PolicyEngine/policyengine-uk/issues/1930),
changed by [policyengine-uk#2177](https://github.com/PolicyEngine/policyengine-uk/pull/2177)).
The published dashboard figure ran on the 2 October Microcosm release that
#1126 examines, with the same draw. microcosm#1299 fixed the draw on 16
October 2026, and [policyengine.py#685](https://github.com/PolicyEngine/policyengine.py/pull/685)
(merged 21 October 2026) certified the latest pair with it.

policyengine.py 6.11.1 (27 October) certifies a later pair, national cut
`microcosm-uk-2024-25-national-20261025T091414Z-a6299504` with
policyengine-uk 2.151.0, built after microcosm#1338 merged. This lane has not
run it yet: [#232](https://github.com/PolicyEngine/policyengine-scorecard/issues/232).

To add a pair, run the compute script with `--variant <id>` in that
variant's environment. The run id defaults to
`childcare-100k-<variant>-<UTC start second>`. Ingest writes a full-use
figure only when both full-use worlds record it: the run set the input to 30
before anything read it, read it back at 30, and kept the main world's reform
and executed limits on 30 April of the year. Two runs of one variant
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
