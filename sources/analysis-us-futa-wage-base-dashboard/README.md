# FUTA taxable wage base dashboard: comparables record

A backfill under the pre-publish comparables gate (docs/COMPARABLES.md). The dashboard was
published on 17 September 2026, before the gate existed. This is its first search, run on
21 October 2026 across every US producer.

## Published figures

The estimates are pinned in `analysis.json`. They cover FUTA revenue from raising the taxable
wage base from $7,000 to $43,000 in 2026 and indexing it to the CPI-U, at the unchanged 0.6%
net rate. They count the FUTA line only, for calendar years 2026 to 2035. Every figure comes
from `PolicyEngine/futa-wage-base-dashboard` at `72e3137`, the commit Vercel serves in
production.

- **Two series per year.** Each year is pinned in both of the dashboard's series:
  - The adjusted series the page leads with removes FUTA-exempt employers and applies one
    wage base per employer. It is pinned from `analysis/futa_wage_base_estimates.csv`, which
    the page's CSV download reproduces byte for byte.
  - The unadjusted model output is pinned from `frontend/lib/results.json`, the file the page
    reads.
- **Ten-year totals.** The page's totals, $251.1 billion adjusted and $317.4 billion
  unadjusted, are sums the page computes from the annual figures (`frontend/lib/data.ts`).
  No file prints them, so each is pinned as that sum over the pinned file, and its
  `derivation` condition says so.
- **Other figures.** The current-law FUTA revenue for the same years is pinned, along with
  the fiscal-year figures for FY2024 and FY2025 in both series.

## What the search found

No producer has scored the dashboard's policy, a base near $43,000 at the 0.6% rate. The
nearest precedent is Kletzer and Rosen (Hamilton Project, 2006). They put a $45,000 base at
the then-current 0.8% net rate at $8.7 billion, with no year stated. It is logged under
`academic` and not staged.

**Staged:**

- **The Budget Lab at Yale** (November 2025, for the Niskanen Center) scores bases of $8,000
  to $14,000 for calendar 2026-35, net of an income-tax offset of about 25%. Its $14,000 rows
  under each indexing rule are staged, with its decade baseline ("about $64B").
- **CBO's budget options** raise the base to $40,000, index it to wages and cut the net rate
  to 0.167%. CBO counts the state unemployment taxes that follow. Staged:
  - the December 2018 option for FY2026 to FY2028, with its ten-year total;
  - the December 2016 option for FY2026, with its ten-year total.
- **CBO's January 2025 baseline** gives FUTA revenue for FY2025 to FY2035.

**Logged, not staged:**

- Treasury's own estimate of the FY2017 budget's $40,000 proposal ($46.3 billion over
  2017-26) and CBO's estimate of the same proposal. Both are estimated after the budget's
  permanent FUTA surtax, a baseline `scorecard_db/baselines.py` does not register (harvest
  rule 7). Their primaries are hashed in `manifest.jsonl`. The `open_search` entry records
  Treasury's hold and the `cbo` entry records CBO's.
- The Searchlight Institute's "north of $250 billion" (8 October 2026), which restates this
  dashboard.

## The comparison

One claim is compared: CBO's January 2025 projection of FY2025 FUTA revenue, $8.461 billion.
The dashboard's unadjusted fiscal-year figure for FY2025 is $8.493 billion, which puts the gap
at +0.4%. The comparison is `constructed`, and its annotation states what differs:

- The dashboard builds its fiscal-year figure from calendar-year liability to sit beside gross
  collections.
- CBO's series matches collections net of refunds.
- CBO's figure is a projection.
- The adjusted fiscal-year figure is 13.7% below CBO.

The other claims have no like-for-like counterpart:

- The Budget Lab's $14,000 rows score a different policy. Each year sits beside the
  dashboard's adjusted estimate for that year, and each budget window beside its adjusted
  ten-year total, labelled `concept_mismatch`.
- CBO's options score a different policy, on fiscal years.
- CBO's FY2026-FY2035 baseline projections are fiscal-year collections. For those years the
  dashboard publishes only calendar-year liability without surcharges.
- The Budget Lab's baseline is a decade total.

No gap is over the threshold.

## Registry note

The apps.json description still gives "$317 billion over ten years", the unadjusted total.
Since PR #6 (17 September 2026), the page has led with the adjusted $251.1 billion.

## Primaries

The primaries are hashed in `manifest.jsonl`. cbo.gov blocks scripted fetches, so its files
came from Wayback Machine captures, recorded as the `wayback_snapshot` on each line. The Budget
Lab PDF has no text layer, so its rows were read from a 300 dpi render.
