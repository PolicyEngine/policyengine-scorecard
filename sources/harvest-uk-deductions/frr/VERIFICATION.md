# FRR claim family — page verification (2026-08-14)

Re-harvest of the Fair Repayment Rate family from issue #21, rebuilt
from primary sources because the original `~/scorecard-harvest/
uk_deductions/` staging is machine-local and not vendored. Every figure
below was re-verified against the vendored PDFs / live page on
2026-08-14; the `quote` field on each staged row is verbatim.

## Sources vendored here

- `autumn_budget_2024.pdf` — HM Treasury, Autumn Budget 2024 print
  (2024-10-30). FRR passages: para 2.30 (p.47), para 4.111 (p.110),
  para 5.134 (p.142).
- `autumn_budget_2024_policy_costings.pdf` — AB2024 policy costings
  document. **Verified absence**: no FRR costing line (searched
  'Repayment'/'deduction' across all 93 pages) — consistent with issue
  #21's note that the FRR is a financial transaction with no PSNB
  impact; the only fiscal quantity is the PSNCR line in para 5.134.
  The absence is machine-checked, not prose-only:
  `tests/test_uk_deductions_ingest.py::test_frr_costing_absence_is_machine_checked`
  extracts the vendored costings PDF and asserts zero occurrences of
  the measure name (skips where pypdf is unavailable, e.g. bare CI).
- DWP press release 2025-04-30 (URL in the staged rows): effective
  date 30 April 2025, cap 25% -> 15% of the UC standard allowance.

## Figures

| claim | value | where |
|---|---|---|
| PSNCR increase, 2029-30 | +£385m | AB2024 para 5.134 |
| households better off | 1.2m | AB2024 5.134/2.30; DWP PR |
| average annual gain | £420 | AB2024 5.134/2.30; DWP PR |
| of which families with children | 700k | AB2024 2.30; DWP PR |

### Removed at gate (2026-08-19): the 2.8m deductions level

The 2026-08-14 staging carried a fifth row — 2.8m "households with
deductions (pre-FRR level)", keyed FY2025-26, held_out. Removed on the
#52 review round, three defects:

1. **The staged quote was a paraphrase.** The release's actual sentence
   (re-verified 2026-08-19 against the live page): "With as many as
   2.8 million households seeing deductions made to their Universal
   Credit award to pay off debt each month, the new rate is designed to
   ensure money is repaid where it is owed…" — the staged "2.8 million
   households currently experience deductions monthly" appears nowhere.
2. **The release states no measurement vintage**, so FY2025-26 /
   period 2026 / FISCAL_YEAR was an unsupported temporal identity; the
   reviewer traced the figure to DWP's administrative deductions
   statistics (the December 2023 to November 2024 publication —
   pre-FRR data).
3. **Boundary rule**: that administrative quantity is exactly the DWP
   quarterly deductions OUTTURN family relationships.py routes away
   from external scores ("deliberately not ingested"); a press-release
   republication does not make it independent.

Disposition: the figure belongs to the future Ledger lane, staged from
the DWP deductions statistics publication itself (exact cell + vintage
+ the consuming pe-uk parameter named), never from the press release.

## Hygiene rules carried from #21

- **PSNCR, never PSNB**: the £385m is a public-sector-net-cash-
  requirement effect. A PSNB comparison row would compare against a
  number that does not exist (PQ UIN 3751).
- **DWP quarterly deductions outturns route to calibration, not
  external_scores** — the Stat-Xplare deductions tables PE's parameters
  consume are consumed_as_target territory and are NOT staged here.
- The gainer counts/average gains have no stated fiscal year in the
  sources; they describe the steady state after the 30 April 2025
  start, staged here as FY 2025-26 with the effective date on the
  reform descriptor. Flag on comparison if PE's year convention
  differs.

## Not yet staged (rest of #21)

JRF protected-minimum floor (pre/post-FRR baselines), historical cap
costings (Budget 2018/2020), DWP/DfC screening counts, Policy in
Practice maximums, Citizens Advice costings — these need their own
page-verified pass against their primary PDFs.
