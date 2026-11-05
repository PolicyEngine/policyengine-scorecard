# uk_hmt_tables: HM Treasury Budget 2026 Tables 6.1, 6.2 and 6.4

Staged 2026-10-29 by `pipeline/stage_ab2026_hmt_tables.py`, which is vendored, so the staging re-runs byte for byte. Source slug `hm_treasury`, source_model `hmt_costing_obr_certified`.

On 4 November 2026 the stager took review A's fixes T-1 to T-9. The workbooks weren't re-fetched in that session, so its output was produced by running the stager on the two workbooks' cells rebuilt in memory from the 29 October rows (every row's locator names its cell), the five section fills and Table 6.2's total row (cells E14:J14, as review A read them). Under the 29 October stager, that rebuild reproduces the 29 October claims file byte for byte. The rebuild script is on the staging branch (`harvest-staging/ab2026/tables-reconstruction/`); a run of the stager on the pinned workbooks should give this file's sha256.

- **Rows:** 768.
  - Table 6.1: 98 measure lines and 3 total rows, each across 6 fiscal years (606 rows).
  - Table 6.2: 9 lines and its total row, each across 6 fiscal years (60 rows). The total's 6 rows come last in the file, after Table 6.4's, so the rows staged before it keep their positions.
  - Table 6.4: 17 lines across 6 fiscal years (102 rows).
- **Primaries:** 2 workbooks.

## Access recipe

The two XLSX attachments of [Supporting documents for Budget 2026](https://www.gov.uk/government/publications/supporting-documents-for-budget-2026), listed through the gov.uk content API (`/api/content/government/publications/supporting-documents-for-budget-2026`).

- **First download:** 2026-10-28, `curl -sSL` with a browser User-Agent.
- **Second download:** 2026-10-29. Both hash to the pinned sha256, which the stager checks before writing anything.
- **Reading:** openpyxl with cached values (`data_only=True`), so every value is the number HM Treasury stored, not a recomputed formula.

## What is staged

- **Table 6.1:** every cell of every measure line, 2026-27 to 2031-32.
  - Fields: `metric: revenue_change`, `unit_concept: gbp`, value = cell × 1e6. Since 3 November, the three total rows take `decisions_effect_on_borrowing` (README rule 10), with no value or sign changed.
  - Conditions carry the line (`table_line`), the Tax/Spend head (`head`) and the line's headings (`heading`).
  - `heading` is "section > sub-heading". The workbook shades its five top-level section headings (cells B5, B27, B43, B58 and B82, fill FFFFCCCC), as the red book shades them, and each sub-heading belongs to the last section above it. So lines 12–19 read "Breathing space for families and businesses > Breathing space for businesses".
  - Column D of both sheets, headed "Fiscal Head check (hide)", is a hidden check column the red book doesn't print (15 lines read "SUBTOTAL", line 30 has "Tax" on a Spend line and line 44 "RAME" on a Tax line). It isn't staged (review A, T-3); `head` is the printed Tax/Spend head.
  - Titles are staged with whitespace normalised: sixteen titles carry tabs, trailing spaces or no-break spaces in the workbook, collapsed to single spaces. Lines 45 and 47 print footnote marker 4 as a superscript run glued to the title; the stager strips it (review A, T-5).
  - The three total rows carry the package keys `ab2026__package_total_policy_decisions`, `…_total_tax_policy_decisions` and `…_total_spending_policy_decisions`.
  - The lines don't sum exactly to the totals: by up to £10m a year for the grand total and up to £15m for the Tax and Spend totals (the Spend total in 2029-30). Footnote 1 says totals may not sum due to rounding, and the rows are staged as printed.
  - The totals' note quotes footnotes 1 and 2. Footnote 2 sets their scope: it excludes the PWLB debt relief and the landlord registration fee ("no net increase to borrowing"), and "AME and tax costings with an impact of less than +-£10 million in every year".
- **Table 6.2:** financial transactions, `proposed_metric: financial_transaction_cash_impact` (cash impact on the public sector, not borrowing).
  - Each line carries the measure key of the Table 6.1 measure it belongs to.
  - Line 4 (Sovereign AI) has no Table 6.1 line and so has its own registered key.
  - Line 6, "Reprioritise financial transactions budgets to fund the new equity loan scheme", has `measure_key: null` and the proposed key `ab2026__your_first_home_ft_reprioritisation` (scope: Table 6.2 line 6; no Table 6.1 line), as Table 6.1 line 34's reprioritisation has its own line (review A, T-1). Line 5 is the scheme itself (its cells sum to −4,700, the red book's "£4.7 billion", para 5.5) and keeps `ab2026__your_first_home_equity_loan`. Both lines are whole rows, so they mustn't share a key: marking both as parts of the scheme would net it to an inflow.
  - The total row, "Total cash impacts of financial transactions" (cells E14:J14: −230, −1,160, −2,290, −2,795, −3,675, −3,850), is staged as 6 `row_type: total` rows with `measure_key: null` and the proposed key `ab2026__package_total_financial_transactions` (scope: exactly Table 6.2 lines 1–9), with footnote 1's rounding note (review A, T-2).
- **Table 6.4:** recostings at Budget 2026 of measures announced earlier.
  - Each row carries **that event's** registry key, with `conditions.recosting_of`:
    - lines 1–14: `autumn_budget_2025` (`data/uk/ab2025_measures.json`);
    - lines 15–16: `autumn_budget_2024`;
    - line 17: `spring_budget_2024` (`data/uk/events/*_measures.json`).
  - The cells are £ million. The table's units header prints "(£)", and its footnotes give no unit, but every value cell carries the number format `\+#,##0"m"` (I9 = 7130 displays as "+7,130m"), so the rows are `parse_confidence: high` (review A, T-6). The sheet is read by name ("Rounded Table 6.4"), not as the workbook's active sheet.
  - Footnote 2 (cell F25) sets the table's scope: "Measures that interact with new measures announced at this Budget, for example on savings income tax changes, as well as measures that extend an existing policy such as personal tax threshold measures have not been included." (review A, T-6).

## Conventions (load-bearing)

- **Sign.** The tables print no legend. `conditions.sign_convention` on every Table 6.1 and 6.4 row reads "positive = yield to the Exchequer (reduces borrowing); negative = cost to the Exchequer". The convention is observed from the rows themselves: the bank surcharge rise is positive, the Household Energy Payment negative. The AB2025 Table 4.1 harvest uses the same convention. Values are NOT re-signed.
- **Table 6.2's sign.** Every Table 6.2 row reads "positive = improves the public sector's cash position (cash inflow or lower outflow); negative = worsens it". The National Wealth Fund's investment is negative; line 6's positives are a lower outflow (budgets reprioritised away from other financial transactions), not an inflow (review A, T-9).
- **scoring_method `final`.** Table 6.1 is the certified post-behavioural total. The static and behavioural legs are in the policy costings document (family `uk_hmt_costings`).
- **period** is the FY end year (2026-27 → 2027), with `conditions.fy` holding the label.
- **geography** is "UK" on every row: these are Exchequer impacts. A measure's own scope (for example England only for the Household Energy Payment) is in its title, verbatim in `reform_hint`, and in the registry.
- **quote** is the line's title and the cell, as printed (Open Government Licence).

## For tranche 2

- Table 6.2's proposed `financial_transaction_cash_impact` and the registered `cash_requirement_change`, which `uk_obr_tables` uses for paragraph 3.20's £1.9bn rise in the Government's financing requirement from the National Wealth Fund and British Business Bank transactions, both measure the cash effect of the same transactions: one as a cash impact, one as the financing requirement. The ingest settles the metric.
- Table 6.3 of the red book prints Table 6.1 lines 45 and 46 again (`uk_hmt_redbook` rows staged from it); tranche 2 dedupes identical HM Treasury figures across the two families.

## Not staged

- Table 6.1's footnote 2 names two measures with "no net increase to borrowing" that the table excludes: debt relief for councils in severe financial distress through the PWLB, and a landlord registration fee for the private rented sector. They have no figures, so there's nothing to stage. The registry doesn't list them.
