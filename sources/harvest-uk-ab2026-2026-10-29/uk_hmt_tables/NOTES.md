# uk_hmt_tables: HM Treasury Budget 2026 Tables 6.1, 6.2 and 6.4

We staged this family on 2026-10-29 with the vendored `pipeline/stage_ab2026_hmt_tables.py`, so the staging re-runs byte for byte. We use source slug `hm_treasury` and source_model `hmt_costing_obr_certified`.

On 4 November 2026 we applied review A's fixes T-1 to T-9 to the stager. We didn't re-fetch the workbooks in that session, so we rebuilt the two workbooks' cells in memory and ran the stager on them. We rebuilt them from the 29 October rows (we name each row's cell in its locator), the five section fills and Table 6.2's total row (cells E14:J14, as review A read them). Under the 29 October stager, that rebuild reproduces the 29 October claims file byte for byte. We keep the rebuild script on the staging branch (`harvest-staging/ab2026/tables-reconstruction/`); a run of the stager on the pinned workbooks should give this file's sha256.

- Rows: 768.
  - Table 6.1: 98 measure lines and 3 total rows, each across 6 fiscal years (606 rows).
  - Table 6.2: 9 lines and its total row, each across 6 fiscal years (60 rows). We put the total's 6 rows last in the file, after Table 6.4's, so the rows we staged before it keep their positions.
  - Table 6.4: 17 lines across 6 fiscal years (102 rows).
- Primaries: 2 workbooks.

## Access recipe

HM Treasury attaches the two XLSX files to [Supporting documents for Budget 2026](https://www.gov.uk/government/publications/supporting-documents-for-budget-2026), and we listed them through the gov.uk content API (`/api/content/government/publications/supporting-documents-for-budget-2026`).

- We first downloaded them on 2026-10-28, with `curl -sSL` and a browser User-Agent.
- We downloaded them again on 2026-10-29. Both downloads hash to the pinned sha256, which the stager checks before it writes anything.
- We read them with openpyxl's cached values (`data_only=True`), so we stage the number HM Treasury stored, not a recomputed formula.

## What we staged

- Table 6.1: every cell of every measure line, 2026-27 to 2031-32.
  - We record `metric: revenue_change`, `unit_concept: gbp` and value = cell × 1e6. Since 3 November, under README rule 10, we give the three total rows `decisions_effect_on_borrowing` instead, with no value or sign changed.
  - We record the line in `table_line`, the Tax/Spend head in `head` and the line's headings in `heading`.
  - We write `heading` as "section > sub-heading". HM Treasury shades its five top-level section headings in the workbook (cells B5, B27, B43, B58 and B82, fill FFFFCCCC), as it does in the red book, and each sub-heading falls under the last section above it. So we write lines 12–19 as "Breathing space for families and businesses > Breathing space for businesses".
  - HM Treasury hides a check column, headed "Fiscal Head check (hide)", in column D of both sheets, and doesn't print it in the red book. In that column HM Treasury enters "SUBTOTAL" on 15 lines, "Tax" on line 30, a Spend line, and "RAME" on line 44, a Tax line. We left the column out after review A's T-3, and take `head` from the printed Tax/Spend head.
  - We normalise whitespace in titles: in sixteen titles HM Treasury typed tabs, trailing spaces or no-break spaces, and we collapse them to single spaces. On lines 45 and 47 HM Treasury prints footnote marker 4 as a superscript run glued to the title, and since review A's T-5 the stager strips it.
  - We key the three total rows to the package keys `ab2026__package_total_policy_decisions`, `…_total_tax_policy_decisions` and `…_total_spending_policy_decisions`.
  - The lines don't sum to the totals: they miss by up to £10m a year for the grand total and up to £15m for the Tax and Spend totals (the Spend total in 2029-30). In footnote 1 HM Treasury says totals may not sum due to rounding, and we staged the rows as printed.
  - We quote footnotes 1 and 2 in the totals' note. In footnote 2, HM Treasury sets their scope: it excludes the PWLB debt relief and the landlord registration fee ("no net increase to borrowing"), and "AME and tax costings with an impact of less than +-£10 million in every year".
- Table 6.2: financial transactions, which we stage with `proposed_metric: financial_transaction_cash_impact` (cash impact on the public sector, not borrowing).
  - We give each line the measure key of the Table 6.1 measure it belongs to.
  - HM Treasury prints no Table 6.1 line for line 4 (Sovereign AI), so we gave it its own registered key.
  - On line 6 HM Treasury prints "Reprioritise financial transactions budgets to fund the new equity loan scheme". We key it to `ab2026__your_first_home_ft_reprioritisation` (scope: Table 6.2 line 6; no Table 6.1 line), as Table 6.1 line 34's reprioritisation has its own line (review A, T-1). On 4 November we gave it `measure_key: null` and this key as a proposal, and in tranche 2 we registered it. HM Treasury puts the scheme itself on line 5 (its cells sum to −4,700, the red book's "£4.7 billion", para 5.5), and we keep `ab2026__your_first_home_equity_loan` on it. We stage both lines as whole rows, so they mustn't share a key: if we marked both as parts of the scheme, we would net it to an inflow.
  - We stage the total row, "Total cash impacts of financial transactions" (cells E14:J14: −230, −1,160, −2,290, −2,795, −3,675, −3,850), as 6 `row_type: total` rows. We key them to `ab2026__package_total_financial_transactions` (scope: exactly Table 6.2 lines 1–9), which we proposed on 4 November and registered in tranche 2, and give them footnote 1's rounding note (review A, T-2).
- Table 6.4: HM Treasury's recostings at Budget 2026 of measures announced earlier.
  - We key each row to **that event's** registry key, with `conditions.recosting_of`:
    - lines 1–14: `autumn_budget_2025` (`data/uk/ab2025_measures.json`);
    - lines 15–16: `autumn_budget_2024`;
    - line 17: `spring_budget_2024` (`data/uk/events/*_measures.json`).
  - HM Treasury reports the cells in £ million. It prints "(£)" in the units header and gives no unit in the footnotes, but formats every value cell as `\+#,##0"m"` (I9 = 7130 displays as "+7,130m"). We therefore give the rows `parse_confidence: high` (review A, T-6). We read the sheet by name ("Rounded Table 6.4"), not as the workbook's active sheet.
  - In footnote 2 (cell F25), HM Treasury sets the table's scope: "Measures that interact with new measures announced at this Budget, for example on savings income tax changes, as well as measures that extend an existing policy such as personal tax threshold measures have not been included." (review A, T-6).

## Conventions the rows depend on

- **Sign.** HM Treasury prints no legend for the tables. On every Table 6.1 and 6.4 row we set `conditions.sign_convention` to "positive = yield to the Exchequer (reduces borrowing); negative = cost to the Exchequer". We read the convention from the rows themselves: HM Treasury prints the bank surcharge rise as positive and the Household Energy Payment as negative. We use the same convention in the AB2025 Table 4.1 harvest. We didn't re-sign any value.
- **Table 6.2's sign.** On every Table 6.2 row we set "positive = improves the public sector's cash position (cash inflow or lower outflow); negative = worsens it". HM Treasury prints the National Wealth Fund's investment as negative, and on line 6 HM Treasury's positives record a lower outflow (budgets reprioritised away from other financial transactions), not an inflow (review A, T-9).
- **scoring_method `final`.** HM Treasury prints the certified post-behavioural total in Table 6.1, and the static and behavioural legs in the policy costings document (family `uk_hmt_costings`).
- **period.** We use the FY end year (2026-27 → 2027) and put the label in `conditions.fy`.
- **geography.** We set "UK" on every row, since HM Treasury reports Exchequer impacts. HM Treasury gives a measure's own scope (for example England only for the Household Energy Payment) in its title, which we copy verbatim into `reform_hint`, and we record it in the registry.
- **quote.** We quote the line's title and the cell, as HM Treasury prints them (Open Government Licence).

## At ingest

- We stage Table 6.2 on the proposed `financial_transaction_cash_impact`, and at ingest we put its 60 rows on the registered `cash_requirement_change`, the PSNCR metric. In `uk_obr_tables` we stage paragraph 3.20's £1.9bn rise in the Government's financing requirement from the National Wealth Fund and British Business Bank transactions (row 2684) on the same metric.
- In Table 6.3 of the red book, HM Treasury prints Table 6.1 lines 45 and 46 again, and we staged `uk_hmt_redbook` rows 339–350 from it. At ingest we drop those 12 rows as twins of this family's rows 264–275 and record each under the kept claim's `publication.also_printed_in`.

## Not staged

- In Table 6.1's footnote 2, HM Treasury names two measures with "no net increase to borrowing" that it leaves out of the table. It names debt relief for councils in severe financial distress through the PWLB, and a landlord registration fee for the private rented sector. HM Treasury gives no figures for them, so we had nothing to stage, and our registry doesn't list them.
