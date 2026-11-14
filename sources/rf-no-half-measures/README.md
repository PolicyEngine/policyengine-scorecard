# Resolution Foundation: No half measures

Clegg and Judge, *No half measures: Setting child poverty on a downward
course at the Autumn Budget* (Resolution Foundation Spotlight, 30 October
2025). The source also vendors the annex of the *Living Standards Outlook
2024*, which the spotlight cites for its projection method (footnote 4).
Lane `uk-two-child-limit-poverty`.

## Why this source mints no claims

These figures were already claims in the Autumn Budget 2025 harvest
(`sources/harvest-uk-ab2025-2026-09-24/uk_rf_ab2025`, registry `uk_ab2025`).
That harvest kept no raw files and no adapter, so this source supplies
them. The ingest matches each adapter row to exactly one harvest claim, by
measure, metric, period, value and publication URL, and attaches the
certified-pair result to that claim. Minting the claims again here would
create duplicates.

## Rows

| Row | Value | Page |
|---|---|---|
| Scrap the limit in full, 2029-30 | 480,000 fewer children in poverty | 3 |
| Cost of scrapping it, 2029-30 | £3.5 billion | 3 |
| Scrapping it "today" (2025-26) | 330,000 fewer children | 1 |
| The "further" fall by 2029-30 | 150,000 (that is, 480,000 less 330,000) | 1 |
| A three-child limit, 2029-30 | 350,000 fewer | 9, endnote 8 |
| A two-thirds element for third and later children, 2029-30 | 340,000 fewer | 9, endnote 8 |
| No limit for families in work, 2029-30 | 330,000 fewer | 9, endnote 8 |

PolicyEngine cannot run the last two options. The engine has no
per-rank child element and no in-work exemption: the registry marks them
`partial`. Those two claims therefore get no result.

## The concepts, from the documents

- **The measure** is relative child poverty after housing costs in the UK.
  Neither the spotlight nor the annex says whether a policy scenario's line
  comes from that scenario's own median.
- **Children** are dependent children: the annex reweights "the numbers of
  dependent children of each age".
- **Take-up** of Universal Credit is fixed at 80%, unchanged "between years
  (or scenarios)" (annex).
- **The counterfactual** is RF's current-policy projection: OBR March 2025
  earnings and Bank of England August 2025 CPI. Policy changes apply from
  April 2026, and Scotland's mitigation of the limit is excluded.

Run `python sources/rf-no-half-measures/adapter.py` (standard library
only). `tests/test_uk_two_child_limit_poverty.py` re-extracts every page
with `pdftotext` and compares it with the vendored extract, where poppler
is installed.
