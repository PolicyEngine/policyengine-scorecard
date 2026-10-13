# uk_ukmod_ab2025 — UKMOD's own Autumn Budget 2025 brief (CeMPA WP 3/26)

Source slug `ukmod`; engine `ukmod_b2025.09` (the paper states UKMOD B2025.09 on FRS
2023-24; static, no behavioural response). One primary: CeMPA Working Paper 3/26,
Rejoice Frimpong, 18 February 2026 (`manifest.jsonl`; sha256 equals the
2026-08-02 harvest's copy in `sources/harvest-uk-2026-08-02/uk_ukmod_jrf/`).

## Why this family exists (2026-09-25)
The 2026-08-02 harvest staged this paper's Tables 1, 1.2, 2, 2.1, 2.4, 3a and 3b
(261 rows) in the `uk_ukmod_jrf` family, which no ingest reads; the AB2025 port's
tranche-2 note that UKMOD's Budget rows "were already in ukmod-stats" was wrong
(that source holds the Country Report only). The rows are re-staged here in the
AB2025 row contract, keyed to the registry's `ab2025__package_ukmod_wp3_26`, and
the second pass reads the tables the first pass left (deciles, winners/losers).

## Conversion from the 2026-08-02 rows
- period: the paper's year Y is FY Y/(Y+1); staged `period` = FY END year, `fy` = "Y-(Y+1)".
- scenario: `baseline` rows are LEVELS of the pre-Budget world (reform_hint and
  measure_key null; baseline_policy `ukmod_b2025_09_fixed_baseline_line`);
  `reform` rows are levels under the package; `reform_minus_baseline` rows are the
  paper's own printed changes. Nothing is derived here.
- income_concept AHC/BHC -> `housing_costs`; the fixed poverty line ->
  `poverty_line: fixed_at_baseline`; subgroups lower-cased.
- registered metrics keep their names (`gini_coefficient` -> `gini`); the rest are
  proposals the ingest dispositions: `expenditure_change` (benefit_cost_change),
  `net_fiscal_impact` (revenue_change with fiscal_measure), and drops for the
  revenue/expenditure LEVELS (macro aggregates), per-capita net impact, S80/S20
  and the Gini/S80 CHANGES (ratios or derived from staged levels).
- sign conventions are stated per fiscal metric on change rows.
- `quote` is the printed cell (value_raw); `publication.locator` the table.

## Title-year quirk
The WP title says "Autumn Budget Statement 2026"; the inner cover says "…2025".
The measures are the November 2025 Budget's, analysed over 2026-2030. Title kept
verbatim; noted on every row.

## Package composition
The paper names four components: personal income tax threshold freezes (fiscal
drag), Universal Credit two-child limit removal, Winter Fuel Allowance
restrictions, Pension Credit reductions. Three are registry measures (the
registry's `package_of`); "Pension Credit reductions" has no Table 4.1 line and
travels in the paper's own words (reform_hint). The earlier registry entry
"six measures … confirmed at harvest" was not confirmed and is replaced.

## Coverage tally (seed bullets -> staged)
13 seed bullets (scores-3-other-shops.md, "ISER / UKMOD (CeMPA WP 3/26)"):
package fiscal net effect and components (Table 1), by nation (Table 1.2),
poverty AHC/BHC fixed line (Table 2), by group (Table 2), by nation (2.1),
child poverty by nation (2.4), inequality (3a/3b) -> the 261 first-pass rows.
Second pass (deciles, winners/losers): see `SECOND_PASS.md` when present.
