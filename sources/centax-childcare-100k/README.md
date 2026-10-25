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
| PolicyEngine, published dashboard (static, history) | −0.434 | −0.505 |
| PolicyEngine, dashboard PR #8 on the fixed draw (uncertified, not attached) | −1.009 | −1.215 |

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

CenTax's two behavioural margins are on the page without a PolicyEngine
value; this lane's counterpart is static.

## Why PolicyEngine is below CenTax

The central static rows carry a `pe_gap` diagnosis linked to
[microcosm#1126](https://github.com/PolicyEngine/microcosm/issues/1126).
Measured on the certified pair: families receiving the extended hours use a
weighted mean of 15.3 of the 30 weekly hours (`maximum_extended_childcare_hours_usage`);
#1126 puts DfE's mean at about 28.5 and identifies the draw as the main
reason PolicyEngine's free-hours spending is low. With every family at the
full 30 hours, the same reform costs £1.40bn in 2027-28 and £1.72bn in
2029-30 on this pair (a diagnostic run, never attached). Smaller factors on
our side, recorded on each result: the engine switches universal and
targeted hours off once a family qualifies for the extended hours
([policyengine-uk#1930](https://github.com/PolicyEngine/policyengine-uk/issues/1930),
changed after the pin by [policyengine-uk#2177](https://github.com/PolicyEngine/policyengine-uk/pull/2177)),
and no child under 1 receives hours.

The published dashboard figure ran on the 2 October Microcosm release that
#1126 examines, with the same draw. The fix merged in microcosm on 16
October 2026 (microcosm#1299). The certified pair was built on 19 June 2026,
before it, so the row shows the miss until a certified Microcosm release
with the fixed draw lands. That is intended. When it does and becomes a
certified replay variant, run the compute script with `--variant <id>` in
that variant's environment. Its artifact goes beside this one in
`results/uk/childcare_100k/`, and ingest keeps every certified artifact's
run: the newest becomes the latest, and this pair's run and the published
figure stay in the history. Ingest refuses an artifact whose package,
release-bundle or dataset identity differs from its variant record.

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
