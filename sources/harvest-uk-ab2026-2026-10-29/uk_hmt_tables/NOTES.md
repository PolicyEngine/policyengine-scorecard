# uk_hmt_tables: HM Treasury Budget 2026 Tables 6.1, 6.2 and 6.4

Staged 2026-10-29 by `pipeline/stage_ab2026_hmt_tables.py`, which is vendored, so the staging re-runs byte for byte. Source slug `hm_treasury`, source_model `hmt_costing_obr_certified`.

- **Rows:** 762.
  - Table 6.1: 98 measure lines and 3 total rows, each across 6 fiscal years (606 rows).
  - Table 6.2: 9 lines across 6 fiscal years (54 rows).
  - Table 6.4: 17 lines across 6 fiscal years (102 rows).
- **Primaries:** 2 workbooks.

## Access recipe

The two XLSX attachments of [Supporting documents for Budget 2026](https://www.gov.uk/government/publications/supporting-documents-for-budget-2026), listed through the gov.uk content API (`/api/content/government/publications/supporting-documents-for-budget-2026`).

- **First download:** 2026-10-28, `curl -sSL` with a browser User-Agent.
- **Second download:** 2026-10-29. Both hash to the pinned sha256, which the stager checks before writing anything.
- **Reading:** openpyxl with cached values (`data_only=True`), so every value is the number HM Treasury stored, not a recomputed formula.

## What is staged

- **Table 6.1:** every cell of every measure line, 2026-27 to 2031-32.
  - Fields: `metric: revenue_change`, `unit_concept: gbp`, value = cell × 1e6.
  - Conditions carry the line (`table_line`), the Tax/Spend head (`head`), the fiscal head where printed (`fiscal_head`: RDEL, TDEL, RAME, SUBTOTAL, Tax, Tax/TME, …), and the run of headings above the line (`heading`).
  - The table marks no hierarchy beyond adjacency. Two headings with no line between them are recorded as "A > B".
  - The three total rows carry the package keys `ab2026__package_total_policy_decisions`, `…_total_tax_policy_decisions` and `…_total_spending_policy_decisions`.
  - The lines don't sum exactly to the totals (by £5m to £10m a year). Footnote 1 says totals may not sum due to rounding, and the rows are staged as printed.
- **Table 6.2:** financial transactions, `proposed_metric: financial_transaction_cash_impact` (cash impact on the public sector, not borrowing).
  - Each line carries the measure key of the Table 6.1 measure it belongs to.
  - The exception is line 4 (Sovereign AI), which has no Table 6.1 line and so has its own key.
- **Table 6.4:** recostings at Budget 2026 of measures announced earlier.
  - Each row carries **that event's** registry key, with `conditions.recosting_of`:
    - lines 1–14: `autumn_budget_2025` (`data/uk/ab2025_measures.json`);
    - lines 15–16: `autumn_budget_2024`;
    - line 17: `spring_budget_2024` (`data/uk/events/*_measures.json`).
  - `parse_confidence: medium`: the table's units header prints "(£)", but its magnitudes and footnotes match Table 6.1's £ million, which these rows assume.

## Conventions (load-bearing)

- **Sign.** The tables print no legend. `conditions.sign_convention` on every Table 6.1 and 6.4 row reads "positive = yield to the Exchequer (reduces borrowing); negative = cost to the Exchequer". The convention is observed from the rows themselves: the bank surcharge rise is positive, the Household Energy Payment negative. The AB2025 Table 4.1 harvest uses the same convention. Values are NOT re-signed.
- **scoring_method `final`.** Table 6.1 is the certified post-behavioural total. The static and behavioural legs are in the policy costings document (family `uk_hmt_costings`).
- **period** is the FY end year (2026-27 → 2027), with `conditions.fy` holding the label.
- **geography** is "UK" on every row: these are Exchequer impacts. A measure's own scope (for example England only for the Household Energy Payment) is in its title, verbatim in `reform_hint`, and in the registry.
- **quote** is the line's title and the cell, as printed (Open Government Licence).

## Not staged

- Table 6.1's footnote 2 names two measures with "no net increase to borrowing" that the table excludes: debt relief for councils in severe financial distress through the PWLB, and a landlord registration fee for the private rented sector. They have no figures, so there's nothing to stage. The registry doesn't list them.
