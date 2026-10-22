# The Burnham plan vs the triple lock: comparables record

A backfill under the pre-publish comparables gate (docs/COMPARABLES.md). The dashboard was listed
on policyengine.org on 16 October 2026, before the gate existed. The search ran on 21 October 2026
against every UK producer.

## What is pinned

`analysis.json` holds 45 estimates, read from `dashboard/public/data/results.json` in
`PolicyEngine/uk-triple-lock` at `5a6acc5`, the commit the 20 October production deployment builds
from. The file is byte-identical to `data/results.json` and has not changed since 15 October
(SHA-256 `e35c1fac…`). The estimates are:

- the expected gross and net saving for every year from 2031-32 to 2039-40 (£11.14bn gross and
  £7.86bn net in 2039-40);
- the lowest and highest of the reweightings the Summary tab charts;
- the OBR central-path, OBR-wedge and ±0.5-point earnings scenarios;
- the plan replayed from April 2012 and from April 2017;
- the share of households with less income;
- pensioner absolute poverty on the central path.

## What the search found

35 claims are staged:

- **DWP:** £15bn (cash) and £11bn (2025-26 prices) for 2039-40, and Chart 1's pensioner relative
  poverty for 2034-35 and 2039-40, read from the chart's vector file.
- **IFS:** around £4bn in 2034-35; £4bn to £20bn for 2039-40; and £9bn lower spending in 2026-27
  had the new rule run since 2011.
- **Resolution Foundation:**
  - £24bn if the 2030s repeat the decade after 2016;
  - its reconstruction of the government's figure (restated);
  - £5bn after five years and £15bn after ten;
  - the pension 5.9% lower had the rule run since 2012.
- **Centre for British Progress:** the post's £3bn and £14.3bn, and the calculator's mean savings
  before and after income tax for each year.
- **OBR:** the triple-lock wedge of 0.56 and 0.6 points.

AJ Bell's £600 and £490 a year is logged as found but not staged, because only press coverage
carries it. The search log lists figures left unstaged because they score the triple lock against
an earnings link: the OBR's £15.5bn, the IFS's £16bn, and RF's £9bn net (with the OBR's £12.6bn it
reports).

## Gaps over the threshold

**DWP.** The dashboard's UK figure is 26% below DWP's £15bn, and its Great Britain figure 28% below.
The gap is `pending` on `uk-triple-lock#13`, which says its cause is not established, so the
analysis may not be promoted until that issue is closed and the cause written. The annotation
gives a partial account:

- The survey's basic and new State Pension bill is about 14 to 16% below DWP's in every year DWP
  publishes. DWP's figure includes payments abroad, so the like-for-like shortfall is about 10 to
  16%.
- On any path the saving is a fixed share of the basic and new State Pension bill. The engine
  enforces this, and the paired Microcosm run confirms it: a bill 10.1% larger, a saving £1.12bn
  larger, the share unchanged.
- That leaves about 14 to 19% (the Microcosm run gives 20%), inside the threshold. The remainder
  could come from DWP's unpublished path, its population projection or its rounding, and none can
  be checked.

This is an accounting decomposition, not the matched full-run counterfactual `uk-triple-lock#13`
asks for, which is why the gap stays pending.

**IFS range.** IFS's £4bn to £20bn for 2039-40 is compared as a range with the expected gross saving,
£11.14bn, which lies inside it. The comparison reads IFS's figures as cash, as it does IFS's £4bn
for 2034-35; IFS does not say.

**CBP calculator.** The dashboard is 25% below the calculator in 2039-40, 37% below in 2032-33 and
59% below in 2031-32. CBP's own methodology documents why:

- Its spending base is about 27% larger: more pensioners, including those abroad, each priced at the
  full rate.
- Its price and earnings paths are its own, not the OBR's.

## Not compared, by design

These claims are recorded beside their nearest estimate with a concept-mismatch annotation:

- DWP's real-terms table (`prices: real`);
- DWP's relative poverty (the dashboard prints absolute levels only);
- RF's decade replay, its reconstruction, and its £5bn and £15bn (staged, unlike RF's other
  earnings-link figures, because The Telegraph reported them as the plan's saving; they score an
  earnings link, recorded as their own world);
- CBP's net figures, which are after income tax only.

Two have a nearby figure that cannot be pinned:

- The "middle 80% of paths" card, £3.9bn to £18.9bn, is the like-for-like spread for IFS's range.
  The page shows it, but the results file does not store it.
- Relative pensioner poverty, 13.8%, is well above DWP's chart (about 9% in 2039-40). The results
  file stores it, but the page does not show it. The record claims no cause for that difference.

The OBR wedge and RF's 5.9% wait on proposed metrics (`uprating_premium_over_earnings`,
`benefit_rate_change_pct`) before the dashboard's 0.55 points and 6.3% can be pinned.

## Primaries

Primaries were fetched on 21 October 2026 and hashed in `manifest.jsonl`. IFS and OBR pages were
read from Wayback Machine captures, because both sites return HTTP 403 to automated fetches.
