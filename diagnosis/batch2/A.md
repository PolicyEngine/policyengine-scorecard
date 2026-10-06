# Cluster A — JCT OBBBA provision scores (JCX-35-25)

Batch 2 diagnosis, 16 queue claims. PE values: certified bundle us-6.2.1
(policyengine-us 2.2.1 + `populace-us-2024-spm-20260915`). All file:line
references were read in this session. Scratch computations:
`/private/tmp/claude-501/-Users-pavelmakarchuk-policyengine-taxsim/f4a2f8d5-0a3a-4727-aebc-e3f8a13d165e/scratchpad/batch2-A/`.

## Bottom line

| # | Claims | Finding | Class | Confidence | Fix |
|---|---|---|---|---|---|
| A1 | 7 FY2026 claims: charitable floor 5.53x, CDCC 3.79x, mortgage 2.50x, non-itemizer charitable 2.28x, SALT 1.96x, AMT 1.85x, CTC 1.84x | The registry compares one **calendar-2026 liability** with JCT's **FY2026 receipts**. For these TY2026-onset provisions, FY2026 holds only 19–56% of the FY2027 value. Against FY2027, the same PE values give 1.05, 1.29, 1.32, 0.45, 0.78, 1.03 and 1.03. | `construction_issue` | High | construction_fix + annotation |
| A2 | Tips FY2026 0.19x, FY2027 0.25x | Tip income is in the H5, but only 7.5% of wage earners in Treasury-listed occupations have tips (waitstaff: 7.4%). The SIPP QRF draw under-imputes tip incidence. Fiscal-year timing does not explain the gap: FY2027 still gives 0.25x. | `pe_gap` (data) | Medium | pe_issue (microcosm) |
| A3 | Car-loan interest FY2026 0.20x, FY2027 0.13x | The qualified-interest input is a proxy: auto-loan interest x (6M qualifying loans per year / 36.9M borrowing households) = 16% share. The statute covers all debt incurred after 12/31/2024, so by TY2026 the stock holds about two annual vintages. The proxy uses one. | `pe_gap` (data proxy), residual open | Medium (direction), low (size) | pe_issue (microcosm) |
| A4 | Non-itemizer charitable FY2027 0.45x | Cash donations come from the TY2015 PUF (Schedule A field E19800). Only 23.9% of H5 households give cash (25.5% give in any form). The PSID Philanthropy Panel Study reports a 46.9% giving share for 2020. The capped deduction scales with the donor count. | `pe_gap` (data) | Medium | pe_issue (microcosm) |
| A5 | Casualty loss FY2026 3.37x, FY2027 2.27x | (1) The engine sets the casualty deduction to zero from 2018 on, but §165(h)(5)(A) keeps losses from federally or State declared disasters. The revert therefore adds back disaster losses that JCT keeps deductible on both sides. (2) Only 33 tax units carry `casualty_loss`; one record holds 52% of weighted dollars. The value moved 0 → 0.43B → 0.29B across builds. | `pe_gap` (engine + sparse data) | Medium | pe_issue (policyengine-us) + annotation |
| A6 | Estate and gift exemption FY2026 and FY2027, PE = 0 | The H5 has no `taxable_estate_value` or `is_deceased` column, so `estate_tax` = 0 in both worlds. Separately, `estate_tax_credit` returns the exclusion amount ($15M) where §2010(c)(1) requires the tentative tax on it ($5.95M), so PE would understate the tax even with estate data. | `pe_gap` (data coverage + engine) | High | annotation + pe_issue (policyengine-us) |

## How the registry scores OBBBA rows (read this session)

- **Revert patches.** `microcosm/packages/microcosm-build/src/microcosm/build/us/obbba_reforms.json`
  encodes each provision as a counterfactual patch for the period
  `2026-01-01.2026-12-31` only. Examples: rows 13 and 15 set
  `gov.irs.deductions.tip_income.cap` and
  `gov.irs.deductions.auto_loan_interest.cap` to 0. Row 9 sets
  `gov.irs.deductions.itemized.casualty.active` to `true`. Row 6 sets
  `gov.irs.credits.estate.base` to 6,790,000 and measures `estate_tax`.
- **Stacking.** `reform_validation.py:787-839` (`stacked_obbba_effects`, microcosm@581b569)
  merges all reverts into a pre-OBBBA world (line 818). It then enacts the
  provisions one at a time in config order (line 828), and records
  `cur_total − prev_total` (line 837). The stack runs per
  (measure, period) group, so the estate row is its own group on `estate_tax`.
  The raw file confirms the chain: each OBBBA row's `baseline_total` equals the
  previous row's `reform_total`. For example, SALT 2,571.44B → 2,633.42B, then
  tips 2,633.42B → 2,631.49B. The order follows JCX-35-25 (Ch.1 lines 1–11 and 20,
  Ch.2 lines 1–3, Ch.4.A line 5, Ch.4.C lines 4–5). JCT provisions that PE does
  not model sit between these lines in JCT's stack. Their interactions are
  second order and are not quantified here.
- **Sign.** The `effect_direction` is `baseline_minus_reform` (JCT
  enactment sign). All 16 PE values have JCT's sign, except the estate
  value, which is 0.
- **Period.** Every OBBBA row has `period: 2026`. The scorecard ingest
  (`scorecard_db/ingest_reform_validation.py:838-860, 916-921`) attaches the
  **same CY2026 value** to the FY2026 claim and to the FY2027 claim. The
  construction string names this approximation: `cy2026_for_fy2026` and
  `cy2026_for_fy2027`. The producer's own comment
  (`reform_validation.py:101-104`) says: "FY2026 is a partial ramp year for
  provisions effective 1/1/2026, so it understates the annual effect", and it
  calls FY2027 "the fairer like-for-like against calendar-year microcosm
  liability".

## JCX-35-25 values and effective dates

Source: `sources/harvest-2026-08-02/jct/claims_staged.jsonl`, the `JCX-35-25`
rows. These rows were parsed with `pdftotext -layout` and checksum-validated
against the printed 2025–34 totals (`NOTES.md` in the same folder). Values are
in $M, FY, and copied verbatim from the staged `value_verbatim` and
`effective_verbatim` fields. I could not re-extract the PDF footnote and legend
page in this session (the PDF is not on this machine). The footnote claims in
the registry descriptions, such as the tips line bundling §45B, stay
unverified here.

| Line (verbatim label) | Effective | FY2025 | FY2026 | FY2027 | FY2028 | FY26/FY27 |
|---|---|---:|---:|---:|---:|---:|
| Ch.1 4. Extension and enhancement of increased child tax credit [1] | tyba 12/31/25 | — | -48,769 | -87,599 | -90,174 | 0.557 |
| Ch.1 6. Extension and enhancement of increased estate and gift tax exemption amounts | dda & gma 12/31/25 | -50 | -3,672 | -20,276 | -22,353 | 0.181 |
| Ch.1 7. Extension of increased alternative minimum tax exemption amounts, … | tyba 12/31/25 | — | -76,835 | -137,508 | -139,699 | 0.559 |
| Ch.1 8. Extension of limitation on deduction for qualified residence interest [1] | tyba 12/31/25 | — | 1,639 | 3,110 | 3,535 | 0.527 |
| Ch.1 9. Extension and modification of limitation on casualty loss deduction [1] | tyba 12/31/25 | — | 86 | 128 | 137 | 0.672 |
| Ch.1 20. Limitation on individual deductions for certain State and local taxes [1] | yba 12/31/24 | -5,070 | 31,617 | 79,250 | 80,000 | 0.399 |
| Ch.2 1. No tax on tips (sunset 12/31/28) [5] | yba 12/31/24 | — | -10,121 | -7,664 | -8,078 | 1.321 |
| Ch.2 3. No tax on car loan interest | iia 12/31/24 | -1,932 | -5,400 | -8,070 | -9,916 | 0.669 |
| Ch.4 5. Enhancement of child and dependent care tax credit [1] | tyba 12/31/25 | — | -409 | -1,197 | -1,189 | 0.342 |
| Ch.4 4. Permanent and expanded reinstatement of partial deduction for charitable contributions of individuals who do not elect to itemize | tyba 12/31/25 | — | -1,543 | -7,791 | -8,149 | 0.198 |
| Ch.4 5. 0.5 percent floor on deduction of contributions made by individuals | tyba 12/31/25 | — | 1,346 | 7,083 | 7,212 | 0.190 |

"—" means the staged rows have no FY2025 cell for that line. The JCT
abbreviations are the standard legend codes: tyba = taxable years beginning
after, yba = years beginning after, iia = interest incurred after, and
dda & gma = decedents dying and gifts made after. I did not re-extract the
legend in this session.

---

## A1 — CY2026 liability compared with FY2026 receipts (7 claims)

**Claims:** `ecb717a9acc4a1b38078` (floor), `0b9f7c2b76e0753b5f75` (CDCC),
`8c39fd4f728cdc2a89f9` (mortgage), `1cb8833f070d370af65f` (non-itemizer,
FY2026), `a822378f6be2661eb525` (SALT), `3dd3cd4f14af2d46bd66` (AMT),
`01304f138bf44f724ef0` (CTC).

**Class:** `construction_issue`. **Confidence:** high.

**Finding.** Each PE value is one TY2026 static liability change. Federal
FY2026 runs from Oct 1, 2025 to Sep 30, 2026, so it ends before any TY2026
return is filed. For provisions whose first tax year is 2026, FY2026 can only
hold the part of the effect that flows through 2026 withholding and estimated
payments. Settlement at filing falls in FY2027. JCT's own numbers show the
size of this ramp. The FY2026/FY2027 ratio is 0.190 (floor), 0.198
(non-itemizer), 0.342 (CDCC), 0.527 (mortgage), 0.557 (CTC) and 0.559 (AMT).
The two lowest FY2026 shares (the 0.5% floor and the non-itemizer
deduction) belong to deductions that are claimed at filing. This agrees
with the withholding explanation. The PE/FY2026 ratio is equal to (PE/FY2027) ÷
(FY2026/FY2027), and the second factor explains it completely:

| Provision | PE (CY2026) | PE/FY2026 | PE/FY2027 |
|---|---:|---:|---:|
| 0.5% charitable floor | +7.44B | 5.53 | **1.05** |
| CDCC enhancement | −1.55B | 3.79 | **1.29** |
| Mortgage-interest limit | +4.09B | 2.50 | **1.32** |
| Non-itemizer charitable | −3.52B | 2.28 | **0.45** (see A4) |
| SALT limit | +61.98B | 1.96 | **0.78** |
| AMT | −142.09B | 1.85 | **1.03** |
| CTC | −89.81B | 1.84 | **1.03** |

SALT has a second timing issue. The line is effective "yba 12/31/24". So
FY2026 nets the TY2025 settlement loss (the $10K → $40K cap increase against
present law, FY2025 = −5,070M) against the first TY2026 gains (no cap → $40K
cap). PE simulates only TY2026.

**Release history** (`data/populations.json`, `results`). The FY2026 ratio is
above 1.5 in every build that has a nonzero value. Floor: 7.15–7.44B
stacked (9.43B isolated). CTC: −85.6 to −91.2B. AMT: −101.5 to −147.7B. SALT:
57.4–64.0B. A constant offset across builds that differ a lot in data is the
signature of a construction difference, not a data difference.

**What timing cannot explain.** FY2027 is not exactly TY2026 either. It holds
the TY2026 settlement plus about three quarters of TY2027 withholding. FY2027
therefore approximates one year of effect at late-2026/2027 levels, about one
year of growth above CY2026 (JCT FY2028/FY2027 is 0.99–1.14 for these lines).
Also, JCT's conventional estimates include micro-behavioral responses, and PE
is static. Neither factor can produce a 1.8–5.5x gap. Against FY2027, the ratios are
0.78–1.32, except the non-itemizer deduction (0.45, see A4).

**Fix (construction_fix).** In `scorecard_db/ingest_reform_validation.py:856-921`,
stop treating the CY2026 value as a like-for-like counterpart of an FY2026
claim when the JCX effective column says that TY2026 is the first affected
year ("tyba 12/31/25"). Two options:
1. Attach the FY2026 result with status `concept_mismatch` and a timing
   annotation, and keep FY2027 as the headline comparison.
2. Construct a PE fiscal-year value. This needs a withholding share per
   provision that we do not have, so option 1 is preferred.

For "yba 12/31/24" and "iia 12/31/24" lines (SALT, tips, car loan, overtime),
FY2026 also contains TY2025. Annotate these FY2026 claims the same way.

**Annotation text (FY2026 claims):** "JCX-35-25 reports fiscal-year receipts.
This provision first applies to taxable years beginning after 12/31/2025, so
FY2026 (Oct 2025–Sep 2026) holds only the withholding-year part of the TY2026
effect; JCT's own FY2026 value is {x}% of its FY2027 value. PolicyEngine
reports one full calendar-2026 liability change. Compare with the FY2027
claim."

---

## A2 — No tax on tips (2 claims)

**Claims:** `73ef6ebfd109b05e4d60` (FY2026, 0.19x), `f227bd9991831f737066`
(FY2027, 0.25x). **Class:** `pe_gap` (data). **Confidence:** medium.

**Construction is correct.** Row 13 sets `tip_income.cap` to 0 for 2026.
Timing makes the gap larger, not smaller: the line is "yba 12/31/24", so FY2026
(−10,121M) holds the TY2025 settlement and is larger than FY2027 (−7,664M).
FY2027 is the cleaner comparator, and it gives 0.25x. The staged FY2030–34
values (−90M to −127M) remain after the deduction sunsets. This agrees with
the registry note that the line also holds a small §45B component of about
$0.1B a year, which is negligible here.

**Engine.** `tip_income_deduction.py:12-27` applies the deduction to
`tip_income` x `tip_income_deduction_occupation_requirement_met`, caps it at
$25,000 and phases it out. The occupation test
(`tip_income_deduction_occupation_requirement_met.py:19-28`) is
`treasury_tipped_occupation_code > 0` and not SSTB. SSN rules apply through
`defined_for` (`tip_income_deduction_ssn_requirement_met.py`). The engine
models the provision fully.

**Data (H5, 2024 weighted, computed this session).**
- `tip_income`: $34.3B total, 2.97M recipients. Of this, $9.25B (1.26M
  recipients) is in non-listed occupations, which the engine excludes.
- Wage earners with a listed TTOC: 22.97M. Of these, only **1.72M (7.5%)**
  have tips > 0.
- Waitstaff (Census 2018 occupation 4110, "Waiters and waitresses" in the
  IPUMS OCC2018 list, mapped to TTOC 102 at `sipp_tips.py:133-184`): 1.68M wage
  earners, of whom **0.124M (7.4%)** have tips, $0.82B in total. Bartenders
  (4040 → 101): 0.54M wage earners, 0.097M (18%) with tips.
- Waitstaff is the main tipped occupation, so a 7% incidence is not plausible
  on its face. This is a domain expectation, not an extracted statistic. The
  internal pattern is also inconsistent: bartenders show 18% and waitstaff
  7.4%.
- The occupation mask is broad, not narrow. The crosswalk also maps, for
  example, Census 9620 ("Laborers and freight, stock, and material movers,
  hand") to TTOC 809 and 3602 ("Personal care aides") to TTOC 501. So the low
  deduction comes from tip incidence, not from the occupation test.

**Mechanism (microcosm `us_runtime/sipp_tips.py`).** The imputation is a QRF
draw. The donor is all December SIPP 2023 person records. Annual tips are the
December monthly amount x 12 (lines 3-7, 324-330). Training is capped at
10,000 rows (line 114, 419-421). The comment at lines 115-119 says that "seed 0
materially under-samples positive tip rows in the 10,000-row cap", so the
positive tail of the target is thin. The occupation flag is "a predictor, not a
domain mask" (lines 23-26). The signal gate only checks that 0.1%–3% of all
persons have tips (line 127). It does not check incidence inside tipped
occupations. The H5 has 0.87% of persons with tips, close to the reference
eCPS value of 0.79% (line 123). This build reproduces the legacy method, which
had the same low incidence.

**Size check (2026 simulation, this session, `pe.us.managed_microsimulation()`
on us-6.2.1).**
- `tip_income` is $39.3B, of which $28.3B passes the occupation test.
- `tip_income_deduction` is $16.9B, claimed by 1.54M tax units.
- PE's −1.93B is therefore about 11.4% per deducted dollar. At that rate,
  JCT's −7.66B (FY2027) needs about $67B of deductions, about 4x PE's
  deductions. This is consistent with an incidence shortfall of that size.
- I did not find an official total of reported tips (W-2 box 7 or Form 4137)
  that I could extract this session, so the size of the shortfall stays
  open.

**Fix draft (pe_issue → PolicyEngine/microcosm).** Title: "SIPP tip imputation:
only 7% of CPS waitstaff receive tips." Body: show the incidence table above,
then propose these changes:
1. Model incidence and amount in two stages, conditional on a listed occupation.
2. Sample donor positives in strata, not inside a uniform 10K cap.
3. Add a gate on within-occupation incidence, for example at least 50% for
   TTOC 101–104.
4. Add a calibration target on total qualified tips once an IRS tip-reporting
   total is sourced.

---

## A3 — No tax on car loan interest (2 claims)

**Claims:** `17ba03f21f372df6c315` (FY2026, 0.20x), `cf49ed4913b68459b9b0`
(FY2027, 0.13x). **Class:** `pe_gap` (data proxy). The residual cause is
`open`. **Confidence:** medium on the direction, low on the size.

**Construction is correct.** Row 15 sets `auto_loan_interest.cap` to 0.
`auto_loan_interest_deduction.py:16-36` caps interest at $10,000 and applies
the $200-per-$1,000 phase-out. The deduction is in both deduction lists
(`deductions_if_not_itemizing.yaml:11-18`).

**Statute.** 26 U.S.C. §163(h)(4), extracted from LII this session: qualified
interest is "any interest which is paid or accrued during the taxable year on
indebtedness incurred by the taxpayer after December 31, 2024, for the
purchase of … an applicable passenger vehicle for personal use", for
"taxable years beginning after December 31, 2024, and before January 1, 2029".

**Data.** `qualified_passenger_vehicle_loan_interest` is not observed. It is
derived in microcosm `us_runtime/scf_auto_loans.py:454-472` as
`auto_loan_interest × min(1, 6,000,000 / weighted households with positive
interest)`. The rationale (lines 16-24) is "roughly six million qualifying
loans are issued annually (16m new light-vehicle sales × 60% financed × 60%
final assembly in the United States)". In the H5 (2024), this share gives
$12.16B of qualifying interest, which is 17.2% of $70.59B total auto-loan
interest, spread over 36.9M households.

**The defect.** Six million is an annual **flow** of new loans. The statute
covers all debt incurred after 12/31/2024, so the TY2026 **stock** holds the
2025 and 2026 vintages, less payoffs. That is close to 2x by TY2026 and about
3x by TY2027–28. JCT's own path rises the same way: −1,932 / −5,400 / −8,070 /
−9,916M for FY2025–28, then −5,313M in the sunset year. The proxy has no year
dimension, and PE uprates the input only by CPI-U
(`qualified_passenger_vehicle_loan_interest.py:20`). A vintage-corrected input
would move PE to about −2.2B (0.27x FY2027). Most of the gap would remain.

**Open residual.** The 2026 simulation (this session) gives
$13.03B of qualified interest, $75.6B of all auto-loan interest, and a
$10.82B `auto_loan_interest_deduction` spread over 43.3M tax units. The
household amount is split over tax units by person share
(`policyengine_core/commons/formulas.py:189-194`), so it is not double
counted. PE's −1.08B is about 10% per deducted dollar. At that rate, JCT's
−8.07B needs about $80B of deductions. That is more than all auto-loan
interest in the H5 ($75.6B in 2026). Possible causes
are a small auto-loan interest pool in the H5 (SCF 2022, original financed
amounts x rate), JCT behavioral responses (shifts toward financed qualifying
purchases), and larger new-vehicle loan balances than the average loan. None
of these was measured this session.

**Fix draft (pe_issue → PolicyEngine/microcosm).** Title: "Qualified car-loan
interest proxy uses one year of loan issuance as the TY2026 loan stock."
Proposed changes:
1. Replace the flow share with a vintage-stock share for the dataset's target
   year: the sum over vintages since 2025 of 6M x survival. Or let the engine
   apply a year-indexed qualifying share.
2. Benchmark total `auto_loan_interest` against an external household
   auto-debt series before scaling.

---

## A4 — Non-itemizer charitable deduction, FY2027 (1 claim)

**Claim:** `85abfca7dfcd7c68d978` (0.45x). Its FY2026 twin is in A1, where
timing turns the 0.45x into an apparent 2.28x. **Class:** `pe_gap` (data).
**Confidence:** medium.

**Construction and engine are correct.** Row 17 sets
`charity.non_itemizers_amount` to 0 for 2026. The engine
(`charitable_deduction_for_non_itemizers.py:13-17`) gives
`min(amount[filing_status], charitable_cash_donations)`, with $1,000, or
$2,000 for joint returns, from 2026 (`non_itemizers_amount.yaml:22-55`). It is
in `deductions_if_not_itemizing.yaml:11-18`. FY2027 is the right comparator
("tyba 12/31/25").

**Data.**
- `charitable_cash_donations` comes from the TY2015 PUF. The PUF tax-detail
  stage (`source_stages.json` stage `puf_tax_detail`, "IRS PUF 2015
  (uprated)") maps E19800 to cash contributions
  (`puf_aggregate_records.py:115`). Hypothesis: before the 2020 CARES Act
  deduction, non-itemizers had no charitable deduction (the engine comment at
  `non_itemizers_amount.yaml:30-32` dates the $300 cap to CARES Act §2204).
  If so, a TY2015 return donor observes giving only for Schedule A filers. The
  measured incidence pattern agrees with this. I did not extract the PUF
  codebook entry for E19800 in this session.
- H5 result: 23.9% of households, and 19.1% of tax units, have cash donations
  > 0. Incidence falls to 4.8% for AGI $0–25K and to 7.2% for AGI $25–50K.
- Benchmark: the Lilly Family School of Philanthropy (24 Oct 2024, PPS within
  the PSID) reports: "The share of Americans who give to charity declined from
  50.9% in 2018 to 46.9% in 2020". The H5 donor incidence is about half of
  this benchmark. The PPS measure counts all forms of giving, and the H5 share
  for any donation is 25.5%.
- 2026 simulation (this session): 147.5M of 165.4M tax units do not
  itemize. Only 18.3M of them (12.4%) have cash donations. All 18.3M claim the
  deduction, a total of $21.6B (average $1,184).
- PE's −3.52B is about 16% per deducted dollar. At that rate, JCT's −7.79B
  needs about $48B of deductions, or about 40M claimants at PE's average
  amount. That is about 2.2x PE's claimant count.
- A capped $1,000/$2,000 deduction scales mainly with the number of donors, so
  the donor-incidence shortfall explains the 0.45x ratio in size.

**Fix draft (pe_issue → PolicyEngine/microcosm).** Title: "Cash charitable
giving is imputed from TY2015 Schedule A, so non-itemizer donors are missing."
Proposed changes:
1. Impute giving incidence and amount for all households from a source that
   observes non-itemizers (PSID Philanthropy Panel Study, or CE Survey cash
   contributions).
2. Or add a calibration target from SOI TY2021 Form 1040 line 12b (the
   $300/$600 non-itemizer deduction): return count and amount. Source this
   series first.

---

## A5 — Casualty loss limitation (2 claims)

**Claims:** `2b90f7cd21917bcf9730` (FY2026, 3.37x), `03d90cf1164672f10599`
(FY2027, 2.27x). **Class:** `pe_gap` (engine encoding + sparse data).
**Confidence:** medium.

**Engine.**
- `casualty/active.yaml:8-11` is `true` from 2013 and `false` from 2018, with
  the comment "OBBB extends extends elimination of casualty expense deduction,
  with an exception for state declared disasters".
- `casualty_loss_deduction.py:12-16` returns `p.active × max(0, loss −
  10% AGI)`. So in the OBBBA baseline every personal casualty loss is
  non-deductible, and no disaster-attributable input exists.
- §165(h)(5)(A), extracted from LII this session: a personal casualty loss in
  a taxable year after 2017 "shall be allowed as a deduction … only to the
  extent it is attributable to a Federally declared disaster … or a State
  declared disaster". The Pub. L. 119-21 note applies the amendments to
  "taxable years beginning after December 31, 2025".
- Effect: the registry revert (row 9) gives back **all** losses, including
  disaster losses that remain deductible under OBBBA. JCT's line scores only
  the non-disaster part, net of the new State-declared carve-out. PE's sign
  is right, but its size is too large by the disaster share. The H5 has no
  disaster flag, so this share cannot be quantified.

**Data.**
- `casualty_loss` = PUF E20500 (`source_stages.json:82`).
- The H5 has 33 tax units with a positive amount, and $1.50B weighted. One
  record (weight 1,186; $654,564) holds about 52% of the weighted dollars.
- 2026 simulation (this session): losses are $1.72B, and the amount above the
  10% AGI floor is $1.14B on 32 records. The top 5 records hold 99.99% of the
  amount above the floor. The top record alone (weight 1,206; $590,917 above
  the floor) holds 62%.
- History: 0 / 0 / 0 (l0-refit, buildi, buildj) → 0.43B (buildo) → 0.29B
  (spm-20260915), and 0.66B in f0af251.
- A provision this small (JCT $86–128M) is below the resolution of the data.
- Open question: is E20500 a pre-floor or a post-floor amount? If it is
  post-floor, the engine applies the 10% floor a second time. That would
  lower PE, so it is not the cause of the PE excess.

**Fix draft.**
1. pe_issue (PolicyEngine/policyengine-us). Title: "Casualty loss deduction
   is zero from 2018 on, but §165(h)(5) keeps disaster losses." Add a person
   input `casualty_loss_attributable_to_declared_disaster`. Apply
   `active=false` only to the remainder. Cite §165(h)(5)(A).
2. Annotation: "PE's value rests on 33 PUF-derived records, and one record
   carries about half of the weighted losses. Treat the comparison as
   indicative only."

---

## A6 — Estate and gift tax exemption (2 claims)

**Claims:** `71c9d1d62387ef6b688d` (FY2026, −3.672B), `3244357bc57dbb8f68a4`
(FY2027, −20.276B), PE = 0. **Class:** `pe_gap` (data coverage + engine).
**Confidence:** high.

**Construction.** Row 6 reverts `gov.irs.credits.estate.base` to 6,790,000
and measures `estate_tax` in its own stack group. The raw row has
`baseline_total` 0.0 and `reform_total` 0.0. The value was 0 in all six
releases.

**Data.**
- `estate_tax.py:12-15` = max(0, `estate_tax_before_credits` −
  `estate_tax_credit`). `estate_tax_before_credits` applies the §2001(c)
  schedule to `taxable_estate_value` (`estate_tax_before_credits.py:12-15`),
  and `estate_tax_credit` is `defined_for = "is_deceased"`.
- The H5 has neither `taxable_estate_value` nor `is_deceased`. I scanned all
  seven entity tables; the only "estate" columns are `estate_income` and
  `real_estate_taxes`.
- Result: `estate_tax` is 0 for everybody in both worlds.
- Timing adds to this: the line is "dda & gma 12/31/25", and FY2026 is only
  18% of FY2027. This agrees with estate returns being filed after death. The gift-tax
  part is also not modeled. But no timing correction can turn 0 into a
  non-zero value.

**Engine defect (separate from data).**
- `estate_tax_credit.py:13-16` returns `p.base`, the basic exclusion amount
  ($15,000,000 for 2026, `estate/base.yaml:61`).
- §2010(c)(1), extracted from LII this session: "the applicable credit amount
  is the amount of the tentative tax which would be determined under section
  2001(c) if the amount with respect to which such tentative tax is to be
  computed were equal to the applicable exclusion amount."
- With the engine's own §2001(c) schedule (`tax/estate/rate.yaml`), the
  tentative tax on $15M is $5,945,800. On the revert value of $6.79M it is
  $2,661,800.
- Because the credit is $15M and not $5.95M, PE's estate tax is 0 for any
  taxable estate below about $37.6M. PE would therefore understate the
  provision even with estate microdata.

**Fix draft.**
1. Annotation (registry): "Household survey microdata contain no decedent
   estates. The release carries no `taxable_estate_value` or `is_deceased`
   input, so PolicyEngine cannot score estate- or gift-tax provisions on this
   dataset. The 0 is structural, not an estimate." Change the status from
   `constructed` to a not-modelable or `pe_gap` status, so that the 0 does not
   read as a model estimate.
2. pe_issue (PolicyEngine/policyengine-us). Title: "estate_tax_credit
   returns the exclusion amount instead of the tentative tax on it
   (§2010(c)(1))." Change the credit to `rate.calc(applicable exclusion
   amount)`, and add the DSUE amount for surviving spouses (§2010(c)(2)(B)).
   Test: a decedent with a $20M taxable estate in 2026 owes 0.4 x $5M = $2.0M.
   The current engine gives 0.

## Concept check: what JCT-vs-PE differences can and cannot explain

- **Fiscal year vs calendar year.** This explains A1 completely (7 claims).
  It explains part of A5 (×1.49). It makes A2 and A3 look **worse** on
  FY2027, not better.
- **Present-law baseline.** The microcosm stack starts from the merged
  pre-OBBBA reverts, which is the same reference world as JCX-35-25 (present
  law). This is not a source of divergence.
- **Behavioral and conventional responses.** JCT includes micro-behavioral
  responses, and PE is static. These are plausible as part of the A3 residual.
  They are unlikely to explain A2 or A4. In A4, the measured input incidence
  is about half of an external benchmark. In A2, it is not plausible on
  internal evidence (7.4% of waitstaff).
- **Bundled scope.** The tips line has about $0.1B a year that remains after
  the sunset (§45B, per the registry note). The mortgage line includes
  mortgage-insurance premiums (per the registry note; not re-verified). Both
  are small compared with the gaps above.
