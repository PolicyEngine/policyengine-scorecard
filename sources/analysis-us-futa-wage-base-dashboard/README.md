# FUTA taxable wage base dashboard: comparables record

A backfill under the pre-publish comparables gate (docs/COMPARABLES.md). The dashboard was
published on 17 September 2026, before the gate existed; this is its first search, run on
21 October 2026 across every US producer.

- **Published figures** (pinned in `analysis.json`): FUTA revenue from raising the taxable wage
  base from $7,000 to $43,000 in 2026 and indexing it to the CPI-U, at the unchanged 0.6% net
  rate, FUTA line only, calendar 2026 to 2035. Each year is pinned twice: the adjusted series
  the page leads with (FUTA-exempt employers removed, one wage base per employer;
  `analysis/futa_wage_base_estimates.csv`, which the page's CSV download reproduces byte for
  byte) and the unadjusted model output (`frontend/lib/results.json`, the file the page reads).
  The current-law FUTA revenue for the same years and the fiscal-year validation figures for
  FY2024 and FY2025 are pinned too. Everything comes from `PolicyEngine/futa-wage-base-dashboard`
  at `72e3137`, the commit Vercel serves in production.
- **Ten-year totals.** The page's $251.1 billion (adjusted) and $317.4 billion (unadjusted) are
  sums the page computes from the annual figures (`frontend/lib/data.ts`, `TEN_YEAR_ADJUSTED` and
  `TEN_YEAR_TOTAL`). No results file prints them, so they are not pinned as estimates; the
  annual figures they sum are.
- **What the search found.**
  - Nobody else has scored the dashboard's policy, a $43,000 base at the 0.6% rate.
  - The Budget Lab at Yale (November 2025, for the Niskanen Center) scores bases of $8,000 to
    $14,000, net of an income-tax offset of about 25%. Its $14,000 rows and its decade baseline
    are staged.
  - CBO's December 2016 and December 2018 budget options raise the base to $40,000, cut the net
    rate to 0.167% and count the state unemployment taxes that follow. They are staged for
    2026 to 2028 and their ten-year totals.
  - CBO's January 2025 baseline gives FUTA revenue by fiscal year, FY2025 to FY2035.
  - Treasury's own estimate of the FY2017 budget's $40,000 proposal ($46.3 billion over
    2017-26) and CBO's estimate of it are logged but not staged. Both are estimated after the
    budget's permanent FUTA surtax, a baseline `scorecard_db/baselines.py` does not register
    (harvest rule 7).
  - The Searchlight Institute's "north of $250 billion" (8 October 2026) restates this
    dashboard.
- **The comparison.** One claim compares like for like: CBO's January 2025 projection of FY2025
  FUTA revenue, $8.461 billion, against the dashboard's fiscal-year model figure of $8.493
  billion, a gap of +0.4%. Every other claim scores a different policy. Each Budget Lab
  figure sits beside the dashboard's estimate for the same year, labelled `concept_mismatch`
  with its cause; no gap is over the threshold.
- **Registry note.** The apps.json description still gives "$317 billion over ten years", the
  unadjusted total. Since PR #6 (17 September 2026), the page leads with the adjusted $251.1
  billion.

The primaries are hashed in `manifest.jsonl`. cbo.gov blocks scripted fetches, so its files came
from Wayback Machine captures (the `wayback_snapshot` on each line). The Budget Lab PDF has no
text layer, and its rows were read from a 300 dpi render.
