# DWP: removing the two-child limit, impact on low income

DWP's Budget 2025 note, *Removing the two-child limit on Universal Credit:
Impact on low income poverty levels in the United Kingdom* (26 November
2025, figures corrected 27 November), as GOV.UK's content API serves it.
Lane `uk-two-child-limit-poverty`; ingest
`scorecard_db/ingest_uk_two_child_limit_poverty.py`.

## What the rows are

- Tables 1-4: the change, against a baseline that keeps the limit, in the
  number and the percentage of people in low income, FYE 2027 to FYE 2031,
  for children, working-age adults and individuals: 120 cells.
  - Table 1: relative low income, after housing costs.
  - Table 2: relative low income, before housing costs.
  - Table 3: absolute low income, after housing costs.
  - Table 4: absolute low income, before housing costs.
- The FYE 2026 figure in the text and footnote 2: 300,000 fewer children
  in relative low income after housing costs "if the two-child limit did
  not exist".
- Children in households whose income rises, FYE 2030: 2 million (2.0
  million in Table A5 of DWP's Child Poverty Strategy note), and Table A5's
  0.6 million of them in deep material poverty.

## The concepts, from the documents

| Question | Answer | Where it is stated |
|---|---|---|
| Relative line | 60% of the median "in that year". The note does not say whether the policy scenario's line comes from that scenario's own median or from the baseline's. | HBAI FYE 2024 methodology, which the note cites |
| Absolute line | 60% of the FYE 2011 median, uprated by CPI variants. The note predates HBAI's March 2026 move to an FYE 2025 reference year. | HBAI FYE 2024 methodology |
| Housing costs | Both bases: BHC and AHC | the note's tables |
| Children | HBAI dependent children: under 16, or 16 to 19 in full-time non-advanced education and living with parents | HBAI FYE 2024 glossary |
| Period | FYE N runs April N-1 to March N. `period` = N; PolicyEngine engine period = N-1 | the column headers |
| Model | DWP's Policy Simulation Model, static, on FRS FYE 2022-2024 pooled, consistent with the OBR's November 2025 forecasts | the note's Methodology |
| Rounding | Numbers to the nearest 50,000; rates to the nearest 0.1 percentage point | the note's Methodology |

## Two quirks the adapter records

- **Table 2's header cell.** It reads "Change in relative low income AHC"
  under a title that says before housing costs. The title governs: the
  values differ from Table 1's, and Table A2 of the strategy note has a BHC
  header.
- **One cell published twice.** Table 2 gives individuals in FYE 2031 as
  -0.6 percentage points, and Table A2 of the strategy note gives -0.5. The
  Budget note's value is the claim; the claim's `note` condition records
  the other.

## Not staged

- Footnote 2's "around 100 children a day" and footnote 3's "additional
  150,000 children": both are arithmetic on the staged figures.
- The attached constituency spreadsheet: administrative counts, not a
  reform score.

DWP's April 2025 two-child limit statistics are not a claim either; they
are administrative fact. The lane uses them only as a measured comparison
for the children whom the with-limit world leaves without a child element.

Run `python sources/dwp-two-child-limit-poverty/adapter.py` (standard
library only).
