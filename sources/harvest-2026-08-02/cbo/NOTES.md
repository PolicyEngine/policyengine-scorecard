# CBO harvest notes (2026-08-02)

## Coverage

- **Latest baseline = February 2026** ("The Budget and Economic Outlook: 2026
  to 2036", publication 61882). Confirmed current via Wayback snapshot of
  cbo.gov/data/budget-economic-data (2026-07-18 capture): the only newer
  artifacts are a June 2026 refresh of 51142 Spending Projections and of the
  highway trust fund file — no full summer baseline as of that capture.
- 20 documents manifested (13 baseline XLSX, 7 cost-estimate/supplemental
  PDFs). 931 claims staged (929 from six baseline workbooks + 2 from the
  P.L. 119-21 SNAP supplemental).
- claims builder: `build_claims.py` (rerunnable; coordinate-based extraction,
  duplicate-identity guard aligned with models.py claim_id fields).

## Access route (important for re-harvest)

cbo.gov is behind **DataDome** bot protection — direct curl AND WebFetch get
403 challenge pages regardless of UA honesty. No bypass attempted. Routes
used instead, in order:
1. **Local copies** in ~/Downloads (Max's manual downloads for the Feb 2026
   PE calibration update) — 7 workbooks, byte-hashed here.
2. **Wayback Machine** (`web.archive.org/web/<ts>id_/<url>`) — 6 workbooks +
   7 PDFs. CDX API is flaky (504s, slow wildcards); exact timestamps work
   best. macOS has no `timeout` command — use `curl --max-time`.
3. **Save Page Now**: anonymous SPN returned HTTP 520 for all four attempts —
   not usable tonight.

## Best baseline-spreadsheet finds (exact tabs/rows, Feb 2026 vintage)

- **SNAP — 51312-2026-02-snap.xlsx**, sheet `SNAP_02-2026`, years in r8
  (D..): r13 "Estimated Budget Authority", **r15 "Estimated Outlays"**,
  r19 "Total Benefits — Budget Authority", r29 "Average Monthly Participation
  (Millions of People)", r30 "Average Monthly Benefit per Participant".
  ⚠️ **Unit-label bug in the workbook**: r11 says "Billions of dollars" but
  values are unambiguously **millions** (r15 FY2026 = 100053; 51118 Table
  3-2 unadj shows the same FY2026 SNAP outlays as 100.053 [billions];
  also r29×r30×12 ≈ r19). Claims staged as millions with the conversion
  recorded per row.
- **SSI — 51313-2026-02-ssi.xlsx**, sheet `SSI_02-2026`: **r13 "Total
  Estimated Outlays"**, r14 payment-date-shift adjustment, r15 adjusted
  total, r19/r20/r21 benefits by group (aged / blind+disabled adults /
  children), r24 "…Demonstration Projects, and Other", r30 avg monthly
  benefit, r31 avg monthly beneficiaries (thousands), r36 maximum monthly
  benefit (individual). Billions. PE's calibration recipe (verified in
  policyengine-us `parameters/calibration/gov/cbo/ssi.yaml`) = r13 − r24;
  Feb 2026 values match that yaml exactly (e.g. 2026: 66.5 − 0.9 = 65.6).
- **Medicaid — 51301-2026-02-medicaid.xlsx**, sheet `Medicaid_02-2026`
  (years D8:O8 = FY2025 actual..2036): r13 "Estimated Outlays" (federal,
  billions), r34-r38 federal benefit payments by eligibility group,
  r42-r46 average monthly enrollment by group (millions), r47 total,
  r51 "Total Enrolled Within a Fiscal Year", r54-r58 average federal
  spending per enrollee (dollars).
- **EITC/CTC — no dedicated program workbook exists.** The outlay effects
  line is **51118 Table 3-2 (and "Table 3-2, unadj") row "Earned income,
  child, and other tax credits"** (composite; footnote d). Staged with
  program=eitc_ctc_other_credits — the EITC-vs-CTC split is NOT published
  in the Feb 2026 supplemental workbooks.
- **Revenues — 51118 Table 1-1** rows 12-17 (individual income taxes,
  payroll taxes, corporate, customs, other, total; billions, FY, r9 years);
  **51138 sheet "3.Individual Income Tax Details"** (CALENDAR years r9;
  actuals 2022-2023, projections to 2036): AGI components r12-r22, taxable
  income r32, deductions r27-r30 (r30 "additional deductions" = the OBBBA
  senior/tips/overtime/auto-loan bundle, footnote e), tax before credits
  r48, credits r62, tax after credits r63, NIIT r64, liability r65,
  returns r69, itemizers r70.
- Also staged: CHIP (51296 r15/r20/r22), TANF (51314 r15, millions), UI
  (51316 r15/r19/r25/r26, millions), OASI/DI/SS + PTC + child nutrition +
  family-support rows from 51118 Table 3-2 unadj (+ timing-adjusted
  variants for the shift-affected rows from Table 3-2).

## Vocabulary notes for ingestion

- `metric` used where the closed vocabulary fits: benefit_cost, enrollment,
  participant_count, revenue_change (per task directive, revenue rows =
  revenue_change with conditions.concept="baseline_level" — semantically a
  level score of the null reform; consider a `revenue_level` metric).
- `proposed_metric` (no enum fit; each recorded instead of `metric`):
  income_aggregate, deduction_aggregate, tax_liability,
  tax_credits_applied, return_count, average_monthly_benefit,
  average_weekly_benefit, maximum_monthly_benefit, first_payment_count.
- `calibration_relationship=consumed_as_target` ONLY where policyengine-us
  demonstrably consumes the series (files in
  `parameters/calibration/gov/cbo/`: snap, ssi, social_security,
  unemployment_compensation, income_tax, payroll_taxes, income_by_source ←
  51138 sheet 3 rows 12-22; mapping per the max-productivity:cbo-baseline
  skill). Everything else held_out. Re-derive at ingest via
  relationships.effective_relationship.
- Two staged rows carry `reform_hint` (P.L. 119-21 §10101) instead of a
  reform dict — the TFP-cap reform is expressible as a PE parametric reform
  at ingest time.

## Pointers (verbatim numbers NOT staged — period-range or low-confidence fit)

From **61367-SNAP.pdf** (all "relative to CBO's January 2025 baseline"):
- §10102 work requirements: −2.4 million SNAP participants in an average
  month over 2025-2034 (components: ~800k ABAWDs through 64; ~300k adults
  with children 14+; ~1M waiver-loss; ±300k veterans/homeless/foster-care
  vs American Indian net −300k). Multi-year-average ⇒ no single `period`.
- §10103 SUA: benefit −~$100/month for ~3% of households, 2026-2034 avg.
- §10104 internet expenses: −~$10/month for ~65% of households.
- §10105 state cost share: −$41B direct spending 2028-2034 (~$35B from
  state benefit payments; ~300k people lose/reduce benefits in an average
  month 2028-2034; child nutrition −96k children, −$170M).
- **61537**: H.R. 1 Senate-passed = −$0.4T deficits vs budget-enforcement
  baseline; +$3.4T vs Jan 2025 current-law baseline; interactions ≈ +$90B
  outlays, −$20B revenues, +$110B deficits (2025-2034 totals).
- **HSGAC-and-Judiciary-Reconciliation.pdf** (May 5 2026): at-a-glance
  table is by-FY in millions — immigration-fee reconciliation, mostly not
  PE-modelable; parse if Scorecard wants it.
- **61536 / Arrington-Guthrie letter / 61505 / 61367-Distributional**: table
  extraction not attempted tonight (time); all are OBBBA-era analyses with
  by-title or decile tables worth a second parsing pass. The distributional
  letter's decile tables are prime PE-comparable material.

## Blockers / gaps

- **Not retrieved** (no Wayback capture; SPN 520; live site DataDome'd):
  51308 Social Security workbook, 51293 child nutrition, 60523 premium tax
  credit workbook, **51142-2026-06 Spending Projections (June 2026 refresh
  — newest program-outlay artifact)**, and the enacted-law estimate PDF for
  publication **61570** ("Estimated Budgetary Effects of Public Law
  119-21", July 21 2025) plus the Oct 2025 Medicaid supplemental
  (PL-119-21-Medicaid _0.pdf; Wayback returned an HTML stub). SS totals are
  covered via 51118 Table 3-2 OASI/DI rows. Next session: retry SPN, or a
  real-browser session on cbo.gov, or ask Max to click-download the five.
- 51142-2026-02 (account-level spending) and 51135 (economic projections)
  and 53724 (tax parameters) are manifested but not claim-staged: 51142's
  "Payment where credit exceeds liability" Treasury accounts are the only
  published EITC-vs-CTC-ish outlay split — good follow-up target.
- cost-estimates INDEX page (cbo.gov/cost-estimates) has no usable recent
  Wayback capture (June-Aug 2026 CDX empty/504) — PDF discovery tonight was
  via CDX directory scans of /system/files/2025-06..2026-07, so recent
  2026 estimates beyond the two May 2026 finds are under-sampled.
