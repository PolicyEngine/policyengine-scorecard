# lpc-minimum-wage raw artifacts

Fetched 2026-08-24 from GOV.UK, via the content API attachment list for
`/government/publications/low-pay-commission-report-2025` (first
published 2026-02-02). Both are the report's own data annexes — the
numbers behind its figures, not a re-typing of them.

| file | source URL | sha256 |
|---|---|---|
| lpc_2025_main_report_data.xlsx | https://assets.publishing.service.gov.uk/media/6980987cf0e5cf1ed2612de7/2025_Main_Report_Data.xlsx | bd0c10dc42bc04d5af09792731464b9549f971a3ff36f9c2ddf0ee69281f08ee |
| lpc_2025_coverage_by_la_region_nation.xlsx | https://assets.publishing.service.gov.uk/media/6980901f3915f712365800dc/2025_Coverage_tables_by_LA_region_nation.xlsx | 2cab42281f0b8094ab1a9077016cf21b91e1069da1fe7dd07f7bb771e108498d |

## What is read

- `lpc_2025_main_report_data.xlsx` has **193 sheets**, one per published
  figure. Three are read:
  - `5.2` — bite and coverage of the adult rate, UK, 1999-2025
  - `6.7 right` — bite by age band, UK, 2013-2025
  - the rest are surveyed and not read; the adapter tallies that rather
    than implying it consumed the workbook.
- `lpc_2025_coverage_by_la_region_nation.xlsx` has 4 sheets; the
  `Region and nation` table is read.

## What was surveyed and deliberately NOT kept

- **The `Local authority` coverage table.** Local-authority geography is
  finer than any UK geography this repo registers, and PolicyEngine-UK's
  certified world cannot resolve it either. Opening an LA vocabulary for
  one table would create identities nothing else can join to. The table
  is a declared drop with a tallied row count, not an omission.
- **The report PDF.** The data annexes carry the numbers; the PDF is
  commentary, and this lane does not digitize prose.
- **190 of the 193 main-annex sheets.** They are the other figures of the
  report — earnings distributions, employment effects, international
  comparisons — each of which is its own population decision rather than
  something to sweep in because the file was already open.

## Why the 2025 report

It is the current edition. LPC publishes annually, so a later harvest
bumps the edition explicitly; the year is part of every claim's identity
(the ASHE April reference year), so a silent edition change would move
the observations under the claims.
