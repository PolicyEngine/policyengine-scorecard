# KFF: eligibility for coverage among the remaining uninsured

Source adapter for KFF's eligibility-among-the-uninsured estimates (the KFF/Damico
eligibility simulation). Two populations, different vintages:

## 1. Flagship brief (national counts)

- **Title**: A Closer Look at the Remaining Uninsured Population Eligible for
  Medicaid and CHIP
- **URL**: https://www.kff.org/uninsured/a-closer-look-at-the-remaining-uninsured-population-eligible-for-medicaid-and-chip/
- **Published**: 2024-03-15. **Accessed**: 2026-08-18 (WebFetch, main session).
- **Vintage**: 2022 survey data (ACS), 2023 Medicaid eligibility levels.
  Pre-unwinding (continuous enrollment ended 2023-03-31); the brief itself notes
  unwinding disenrollment is expected to increase the uninsured.
- **Headline numbers** (nonelderly, uninsured AND eligible for Medicaid/CHIP):
  - Total: 6.4M = 25% of the 25.6M nonelderly uninsured (2022)
  - Adults 4.2M; children 2.2M (children's leg includes CHIP)
  - In expansion states: 5.2M
- **Universe**: nonelderly (0–64) uninsured; eligibility includes CHIP for
  children; MAGI pathways only (see methods below).

## 2. State Health Facts indicator (state shares, vintage-matched to Populace 2024)

- **Title**: Distribution of Eligibility for ACA Health Coverage Among the
  Remaining Uninsured
- **URL**: https://www.kff.org/health-reform/state-indicator/distribution-of-eligibility-for-aca-coverage-among-the-remaining-uninsured/
- **Accessed**: 2026-08-18 (WebFetch extraction of the rendered table — NOT the
  CSV download; see caution below).
- **Vintage**: 2024 ACS, 2025 Medicaid + premium tax credit eligibility levels
  (per the page's methods notes). Post-unwinding on both sides of any join with
  populace_us_2024.
- **Raw extraction**: `raw/state_indicator_2024acs_2025levels.md`.
- **⚠️ Column-label caution**: the extraction labeled the first column
  "Medicaid/Other Public (%)" — verify category semantics against KFF's own
  column headers before finalizing claim metric names (KFF's category set for
  this indicator historically: Medicaid eligible / Tax-credit eligible /
  in coverage gap / ineligible due to income or ESI offer / ineligible due to
  immigration status). NSD = below statistical-reliability minimum; NA (coverage
  gap) = expansion state. Shares are of each state's remaining uninsured
  (nonelderly universe).

## KFF methodology (verified from KFF's own methods boxes, 2026-08-18)

Static eligibility microsimulation (analyst: Anthony Damico). Current vintage:
ACS microdata (moved from CPS ASEC with the 2017 estimates); separate
Medicaid-vs-Marketplace health insurance units built per person (tax-unit
reconstruction ~99% match to IPUMS); ACA-definition MAGI vs state-reported
eligibility levels (KFF/Georgetown CCF 50-state survey); immigration status
imputed (current methods box: regression trained on the 2023 KFF/LA Times
Survey of Immigrants, 5 implicates, benchmarked to Pew state estimates; earlier
vintages: SIPP-based SHADAC/Van Hook model benchmarked to DHS); ESI offers
imputed from a CPS-ASEC regression. MAGI pathway only (no disability/non-MAGI
pathways; they argue SSI auto-linkage makes the residual small). Annual income
snapshot (they note monthly churn means annual flow exceeds the point-in-time
stock). No stated correction for survey Medicaid underreporting.

Methods sources:
- https://www.kff.org/medicaid/how-many-uninsured-are-in-the-coverage-gap-and-how-many-could-be-eligible-if-all-states-adopted-the-medicaid-expansion/ (current ACS-era methods box)
- https://files.kff.org/attachment/data-note-new-estimates-of-eligibility-for-aca-coverage-among-the-uninsured (2016 data note, CPS-era Methods box)

## Named construct differences vs PolicyEngine (annotate on every join; both directions, descriptive)

1. **Pathway breadth**: KFF = MAGI-only; PE `is_medicaid_eligible` includes
   SSI-linked, medically needy, optional senior/disabled categories → PE
   eligibility construct is broader.
2. **CHIP**: KFF's counts include CHIP children; Microcosm deliberately does not
   assign standalone CHIP take-up (M-CHIP concept split pending, microcosm#321)
   → condition PE counterparts on Medicaid-only or annotate.
3. **Coverage measurement**: KFF's uninsured retains survey Medicaid
   misreporters (no undercount correction stated); PE enrollment is
   anchor-and-fill calibrated to CMS Dec-2024 state counts with reported
   coverage as a floor.
4. **Data/imputations**: ACS vs CPS-ASEC-based Populace; immigration status —
   KFF regression + Pew benchmarks (5 implicates) vs Microcosm
   derive_immigration_status (CPS citizenship/entry-year/nativity + Pew anchors);
   ESI offer imputed by KFF, reported at interview in Populace.
5. **Vintage** (brief population only): 2022 ACS + 2023 levels vs single-period
   2024 artifact — join as vintage-mismatched; the state indicator population is
   the vintage-matched join.
