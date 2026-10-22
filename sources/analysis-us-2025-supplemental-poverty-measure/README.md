# 2025 Supplemental Poverty Measure post: comparables record

A backfill under the pre-publish comparables gate (docs/COMPARABLES.md): the post was published on
18 September 2026, before the gate existed.

- **Published figures** (pinned in `analysis.json`, 90 estimates): the post's calculations are in
  `PolicyEngine/spm-threshold-paper` PR #8, which the post links, pinned at its head
  `4b8df66` (`analysis/asec-2026-anchored-thresholds/`): `anchored_results.json` (2025 rates at
  2024 thresholds grown by CPI-U, the threshold effect, tenure, and the recomputed published
  rates), `anchored_results_chained.json` (the C-CPI-U column), `waterfall_data.json` (the
  2024-to-2025 change at anchored thresholds, the post's "fell 0.7 points"),
  `state_age_results.json` (finer ages) and `by_state.csv` (the state tile map). The post's 2024
  rates on the earlier population controls (footnote 2: 12.93, 13.35, 12.16, 14.95; and 14.50 for
  under 6) are pinned to `analysis/prediction-grade-2025/results/raw_aging.json` on the same
  repository's master (`22d8b7a`; the same bytes were committed on 17 September in `a79c03a`). The
  post does not link that file. These are recomputations from the Census public-use files with
  Census's own SPM variables; no PolicyEngine microsimulation model is involved. The page was read
  from policyengine-app-v2 main at `24550022d`
  (`app/src/data/posts/articles/2025-supplemental-poverty-measure.md`, last changed in `a326e0e`).
  Every figure the post prints was checked against the file it is pinned to, including all 51
  state tiles and the waterfall chart's data.
- **Not pinned**: the post's 2024 rates for under 4 (14.95†), 6 to 17 (12.84†) and 75 and over
  (16.49†), and its † change column. No results file in the repository carries them. Census's own
  figures that the post reports (P60-290 rates, Table 17 state averages) are not PolicyEngine
  estimates.
- **What the search found** (2026-10-21, every US producer): Census's working paper
  SEHSD-WP2026-22, released with P60-290, anchors the 2024 thresholds two ways. Its CPI-U table
  (A.4) is the post's own counterfactual, and is staged and compared: 12.4 percent for all people
  against the post's 12.31, and a 0.7-point fall from 2024 against the post's 0.69. Its headline
  FCSUti-anchored tables (A.2, A.3) are staged as a concept mismatch, because the FCSUti index rose
  3.44 percent against CPI-U's 2.63. CBPP's blog of 16 September restates the FCSUti figures and
  is logged as found but not staged: its page returns a Cloudflare challenge. Columbia CPSP's 2025
  databook anchors in 2025 and prints no figure on the post's quantities.
- **The gaps**: every compared claim is within the 25 percent threshold. The largest are the
  2024-to-2025 changes for people 65 and over (−0.44 against −0.5, −12 percent) and for children
  and 18 to 64 year olds (about +9 percent). Census prints its rates and differences to one
  decimal, and the post's change starts from Census's 2024 rates as printed (13.0, 13.5, 12.2,
  15.1).
- **Not on the producer list**: the Census Bureau was the one producer with a comparable, found by
  open search. A US poverty analysis will usually meet its anchored-threshold papers, so it is a
  candidate for `data/comparables/producers.json` with a `why`.
