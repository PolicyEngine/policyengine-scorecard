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
- DWP press release 2025-04-30 (URL in the staged rows): effective
  date 30 April 2025, cap 25% -> 15% of the UC standard allowance.

## Figures

| claim | value | where |
|---|---|---|
| PSNCR increase, 2029-30 | +£385m | AB2024 para 5.134 |
| households better off | 1.2m | AB2024 5.134/2.30; DWP PR |
| average annual gain | £420 | AB2024 5.134/2.30; DWP PR |
| of which families with children | 700k | AB2024 2.30; DWP PR |
| households with deductions (pre-FRR level) | 2.8m | DWP PR |

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
