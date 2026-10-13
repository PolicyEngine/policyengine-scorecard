# Batch 2, cluster D: state credit costs (admin actuals and fiscal notes)

Nine claims, seven items. Three divergences are mostly the registry's own
construction: a reform keyed to bracket indices that moved (IA HF1020), a
repealed-law variable (MN WFC), and an uncapped nonrefundable credit (ID CTC).
The flat refundable child credits (CA YCTC, CO FAC, MD CTC) are an
entitlement-versus-claims concept gap: the engine pays every eligible unit,
including units that are not required to file, while the benchmarks count
claims. Colorado CTC is only partly the TY2023-versus-TY2024 law change the
registry row claims; on this release most of the gap survives a TY2023-law
replication and stays open. Ohio has a real engine ordering defect, but it
explains only a quarter of the gap. Illinois stays open: its benchmark is an
ex-ante first-year estimate.

PE values are the certified bundle us-6.2.1 (policyengine-us 2.2.1 +
`populace-us-2024-spm-20260915`), read from
`sources/populace-reform-validation/raw/populace-us-2024-spm-20260915.json`.
All decompositions below are from three managed baseline simulations run this
session, one at a time (`pe.us.managed_microsimulation()`, bundle `us-6.2.1`;
scripts and JSON in the session scratchpad `batch2-D/probe_d{,2,3}.py` and
`.json`). The probes reproduce every registry level to the dollar (for example
`ca_yctc` $621,910,016, `co_ctc` $200,915,440, `mn_wfc` $289,644,384, `id_ctc`
$96,658,528, `oh_eitc` $108,913,696) and the IA registry delta exactly
($1,835,913). Engine paths are relative to
`.venv-pe/lib/python3.12/site-packages/policyengine_us/`; microcosm paths are
relative to `packages/microcosm-build/src/microcosm/build/` at 581b569.

Method caution for other clusters: `sim.calculate("state_fips", period,
map_to="tax_unit")` is wrong for 44.0% of weighted tax units.
policyengine-core maps household to person by the mean and person to tax unit
by the sum (`policyengine_core/simulations/simulation.py:696-717`), so any tax
unit that is not the whole household gets a scaled FIPS. Probes 1-2 used it for
state masks; probe 3 re-derived every masked number from members' person-level
FIPS, and only probe-3 values for masked statistics are used below.

## Common mechanics (read this session)

- Every level row is a plain weighted baseline total of one variable at
  period 2024: `us/state_program_levels.json` (variable fields at lines 21, 73,
  112, 334, 500, 556, 598, 612) feeds `us_runtime/reform_validation.py:984-1004`
  (`_level_total`), which caps a credit at liability only when the row sets
  `cap_variable` (lines 465-469, 997-1001). No state row sets it; only four SOI
  rows do (`us/soi_baseline_levels.json:48,62,76,90`).
- Take-up and filing gates. The federal EITC is multiplied by `takes_up_eitc`
  and a filer test (`variables/gov/irs/credits/earned_income/eitc.py:14,25-31`),
  and state EITCs built with the shared helper inherit both gates
  (`tools/state_eitc_helpers.py:128-139`). The release H5 tax-unit table carries
  `takes_up_eitc` and `would_file_taxes_voluntarily`, but not
  `would_file_if_eligible_for_refundable_credit`, whose default is True
  (`variables/gov/irs/would_file_if_eligible_for_refundable_credit.py:17`).
  The CA YCTC, CO CTC, CO FAC, MD CTC, ID CTC and MN combined credit formulas
  read no take-up or filer variable (files cited per item). The seeded EITC
  take-up share among EITC-eligible units is 74.8% nationally (CA 70.9%,
  CO 75.1%, MD 72.6%, IL 76.5%, OH 76.9%, MN 71.1%, ID 69.8%, IA 70.1%).

---

## D1. IA HF1020: the reform's bracket indices moved under the engine (construction_issue, high)

Claim `e3eb837aef9d9269a700`: LSA fiscal note −$17.7M FY2026; PE −$1.84M (0.10).

**Finding.** The registry reform sets
`gov.states.ia.tax.income.credits.child_care.fraction[4..6].amount = 0.5`
(`us/state_reforms.json:177-185`). In policyengine-us 1.764.6 the schedule had
seven brackets and indices 4, 5, 6 were $35k-40k, $40k-90k and $90k+
(`.venv-pe501/lib/python3.12/site-packages/policyengine_us/parameters/gov/states/ia/tax/income/credits/child_care/fraction.yaml`
in this repo). In 2.2.1 a
$45k bracket was inserted (`parameters/gov/states/ia/tax/income/credits/child_care/fraction.yaml:47-61`:
40k 0.30, 45k 0.0→0.30 from 2021, 90k 0.0), so the same indices now mean
$35k-40k, $40k-45k, $45k-90k. The reform silently stopped covering the $90k+
band. The bill covers it:

> "House File 1020 reduces the number of net income thresholds for the Child and
> Dependent Care (CDC) Tax Credit from seven to four and allows any taxpayer with
> Iowa net income equal to or exceeding $25,000 to qualify for the refundable tax
> credit of up to 50.0% of the federal Child and Dependent Care Credit."
> — Iowa LSA Fiscal Note HF 1020 (Doc ID 1526230, April 22, 2025), p.1, Description

> "1040 filers with an AGI of $90,000 or more will be able to access the State CDC
> Tax Credit due to the Bill and will realize an estimated decrease in tax
> liability beginning in TY 2025." — same, p.2, Assumptions

**Quantification (analytic on the 2025 baseline; `ia_cdcc` is refundable,
`parameters/gov/states/ia/tax/income/credits/refundable.yaml`, and the formula is
`cdcc_potential × fraction(ia_taxable_income_consolidated)`,
`variables/gov/states/ia/tax/income/credits/ia_cdcc.py:28-37`):**

| construction | Δ revenue | units gaining |
|---|---:|---:|
| registry (35k-90k → 50%) | −$1.836M (reproduces the registry row exactly) | |
| bill text (≥ $25k → 50%, incl. $90k+) | −$23.97M | 48.8k |
| of which the $90k+ band | −$22.14M | 40.8k |

The results history confirms it: buildi/j/o (engine 1.764.6, old indexing)
scored −$21.7M/−$22.7M/−$27.6M; spm-20260915 (2.2.1) scored −$1.84M. With the
bill-text construction the ratio is 1.35, and PE has fewer gaining units than
the note's 78,000 but a larger average ($491 vs $228). The residual is open: PE's own 2025
baseline `ia_cdcc` is $19.4M, while the note's background reports IDR claims of
"$11.0 million in FY 2024", and PE keys the fraction on taxable income while the
note describes net income. Nonresidents are 5.2% of the note's decreases and are
outside PE.

**Fix (construction_fix, microcosm `us/state_reforms.json`).** Add
`fraction[7].amount: 0.5` (2025-01-01.2100-12-31), and add a guard test that
asserts the bracket thresholds a bracket-index reform targets
(35,000/40,000/45,000/90,000 here) at the pinned engine, so a future
re-indexing fails loudly instead of rescoring a different bill.

---

## D2. MN Working Family Credit: the row measures a repealed-law variable (construction_issue, high; residual open)

Claim `901232245430396bdea5`: derived $191.5M (TY2024); PE $289.6M (1.51).

**Finding.** The row measures `mn_wfc` (`us/state_program_levels.json:112`).
That variable computes the pre-2023 WFC schedule from
`p.wfc.pre_cwfc_legislation.*` (`variables/gov/states/mn/tax/income/credits/mn_wfc.py:16-42`;
phase-in rates up to 12.5% on earnings up to $21,170, with 2022 values carried
forward). It is not part of the 2024 tax calculation: the 2023 and 2024
refundable lists contain `mn_child_and_working_families_credits`, not `mn_wfc`
(`parameters/gov/states/mn/tax/income/credits/refundable.yaml:8-14`). The 2024
law is the combined credit, with the WFC at 4% of earnings
(`parameters/.../cwfc/wfc/phase_in.yaml`, 2024 threshold $9,220).

> "taxpayers add together the two credits, and the combined amount is phased
> down based on income." … "Of this amount, about 76 percent of credits before
> the phaseout were young child credits, 20 percent were working family credits,
> and 4 percent were credits for older children." … "About 301,500 childless
> returns claimed about $89.6 million in credits, for an average credit of $297."
> — MN House Research, Minnesota's Child Credit and Working Family Credit (May 2026), p.1

**Quantification (probe, current-law combined credit):** PE's pre-phaseout
WFC+older-child share is 23.5% ($292.2M of $1,245.3M), against House Research's
24% (20% + 4%), so the engine's split is right. A proportional allocation of
the post-phaseout combined credit gives a WFC+older-child component of $238.5M
(ratio 1.25 against the derived $191.5M; the $564M DOR CTC figure that the
derivation subtracts was not re-verified this session). Construction therefore
explains $51.1M of the $98.1M excess. The rest sits in childless units: PE pays
$165.5M to 453.0k units with no qualifying child against the official $89.6M on
301.5k childless returns (1.85; avg $365 vs $297). Of PE's childless amount,
$66.1M goes to 179.3k units with a head aged 19-24 (Minnesota's own expansion
beyond the federal age floor) and $101.6M to 287.9k units aged 25-64; only
$20.5M goes to units not required to file. With-children units are close:
$694.0M on 274.1k units against $665.9M on 240.1k returns (1.04). The combined
credit reads no take-up flag
(`variables/gov/states/mn/tax/income/credits/mn_child_and_working_families_credits.py:65,87`);
gating it by the seeded `takes_up_eitc` would lower the combined total only
from $859.5M to $825.6M. The combined row (`state_mn_cwfc`) is 1.14 and is not
in this queue. The childless excess is not explained this session (open).

**Spillover (engine).** `variables/gov/states/mn/tax/income/credits/taxsim_mn_child_tax_credit_component.py:13-15`
subtracts the same legacy `mn_wfc` from the 2023+ combined credit, so the
TAXSIM-style CTC component is wrong for TY2023+. The policyengine-taxsim
emulator reads the legacy variable too: `policyengine_taxsim/config/variable_mappings.yaml:681`
(MN state EITC output = `mn_wfc`) and
`policyengine_taxsim/core/state_output_resolver.py:54,268-279` (v39 EITC and
the MN state CTC component). Outside this cluster's scope; worth a check.

**Fix (construction_fix).** Retire `state_mn_wfc` or re-measure it. Preferred:
replace it with the official childless-returns subtotal ($89.6M, 301,500
returns) against PE's combined credit for units with no qualifying child. Keep
`state_mn_cwfc` as the primary MN row. Separately, a small PE issue: end
`mn_wfc` at 2022 (or make it the 2023+ WFC component) and fix the TAXSIM
component.

---

## D3. Idaho CTC: the row sums the uncapped nonrefundable credit (construction_issue, high)

Claim `bd2894a6bf3d1e1eda0d`: DFM $63.96M (CY2024); PE $96.66M (1.51).

**Finding.** `id_ctc` is $205 × CTC-qualifying children with no liability cap
(`variables/gov/states/id/tax/income/credits/id_ctc.py:12-19`). The cap is
applied only in `id_non_refundable_credits`
(`variables/gov/states/id/tax/income/id_non_refundable_credits.py:15-24`),
and `id_ctc` is the only Idaho nonrefundable credit in 2024
(`parameters/gov/states/id/tax/income/credits/non_refundable.yaml:17-20`). The
benchmark is a foregone-revenue figure for a nonrefundable credit:

> "The state provides a nonrefundable $205 individual income tax credit per
> qualifying child of the taxpayer." — Idaho DFM General Fund Revenue Book,
> Jan 2026, Tax Preferences history, 63–3029L; table row (thousands, 2022-2028):
> "63-3029L Child Income Tax Credit $ 65,539 63,427 63,962 64,768 65,412 0 0" (p.21)

**Quantification.** Capped at liability, PE is $73.24M (ratio 1.145). The
58.6k units with zero Idaho liability carry $22.3M of the uncapped amount.
Construction explains $23.4M of the $32.7M excess (72%). The 1.145 residual is
small and not attributed. DFM describes its preference figures as estimates
that are "likely to be upper bounds" (p.18), so if anything the true used
amount is below $64M. The row rests on 357 sample records.

**Fix (construction_fix).** Measure `id_non_refundable_credits` for this row,
or set `cap_variable: id_income_tax_before_non_refundable_credits`.

---

## D4. Ohio EITC: the engine applies the EITC before the credits that precede it by law (open; pe_gap share about a quarter)

Claim `4bac6a16f6267328daf0`: OH TER $59.3M (FY2025, TY2024 proxy); PE $108.9M (1.84).

**Finding.** `oh_eitc` is the applied amount, capped at the liability that
remains at its turn (`variables/gov/states/oh/tax/income/credits/oh_eitc.py:19-30`;
`variables/gov/states/tax/income/non_refundable_credit_cap.py:31-43,46-63`), so
the row is already liability-limited. But the engine's 2023+ order puts
`oh_eitc` first (`parameters/gov/states/oh/tax/income/credits/non_refundable.yaml:12-19`),
while the statute and the 2024 form put it thirteenth:

> "The credit shall not exceed the aggregate amount of tax otherwise due under
> section 5747.02 of the Revised Code after deducting any other nonrefundable
> credits that precede the credit allowed under this section in the order
> prescribed by section 5747.98 of the Revised Code." — R.C. 5747.71 (effective July 3, 2019)

> 2024 Ohio Schedule of Credits, Nonrefundable Credits: "2. Retirement income
> credit" … "4. Senior citizen credit" … "6. Child care & dependent care credit"
> … "9. Exemption credit" … "11. Tax less credits (line 1 minus line 10 …)" …
> "12. Joint filing credit (see instructions for table). % times line 11, up to
> $650" … "13. Earned income credit"

**Quantification (probe 3).** The uncapped 30% match is $695.0M; Ohio
liability before nonrefundable credits on EITC-potential units is $145.3M, and
571.9k potential units have no liability. Applying the EITC after the preceding
credits' potentials in the form's order gives $95.9M (1.62), against the
engine's $108.9M. Step by step: CDCC −$5.4M, exemption credit −$4.1M, joint
filing credit −$3.4M (retirement, senior and lump-sum credits do not bind). The
ordering defect therefore explains $13.0M of the $49.6M excess (26%). The rest
is open. The benchmark is an ODT estimate that the registry labels
"approximation"; the TER PDF could not be re-extracted this session (TLS
error), so its basis is taken from the row. PE's EITC path is already gated by
the seeded EITC take-up (Ohio 76.9%). The row rests on 93 sample records.

**Fix (pe_issue).** Reorder `gov.states.oh.tax.income.credits.non_refundable`
for 2023+ to the R.C. 5747.98 / Schedule of Credits order (retirement,
senior, lump-sum, CDCC, exemption, joint filing, then EITC, then the school
credits), with a household test where the CDCC, exemption and joint filing
credits use up a small liability before the EITC. Check that the joint filing
credit is computed on line 11 (tax after lines 2-9). Annotate the row that the
residual 1.62 is unexplained.

---

## D5. Colorado CTC: law vintage explains only part of the gap on this release (open; construction share about 30%)

Claim `03d666ddda6fe83bd6f4`: CO DOR $89.16M (TY2023, 130,188 claims per the row); PE $200.9M (2.25).

**Finding.** The row simulates period 2024
(`us/state_program_levels.json:71-73`), but Colorado changed the credit for
TY2024. Through TY2023 it was a percentage of the federal CTC for filers who
claimed the federal CTC; from TY2024 it is a flat amount per child under 6 with
no federal-claim requirement:

> "(3)(a) … for income tax years commencing on or after January 1, 2022, BUT
> BEFORE JANUARY 1, 2024, a resident individual who claims a federal child tax
> credit for an eligible child on the individual's federal tax return is allowed
> a child tax credit" … "(4.5)(a)(I) FOR INCOME TAX YEARS COMMENCING ON OR AFTER
> JANUARY 1, 2024, A RESIDENT INDIVIDUAL WHO FILES A SINGLE RETURN IS ALLOWED A
> CHILD TAX CREDIT … (A) ONE THOUSAND TWO HUNDRED DOLLARS IF THE INDIVIDUAL'S
> FEDERAL ADJUSTED GROSS INCOME IS TWENTY-FIVE THOUSAND DOLLARS OR LESS;"
> — HB23-1112 (signed), amending C.R.S. 39-22-129, pp.4-5

The engine encodes both regimes
(`variables/gov/states/co/tax/income/credits/ctc/co_ctc.py:27-45` and `46-70`;
`parameters/gov/states/co/tax/income/credits/ctc/ctc_matched_federal_credit.yaml`:
true 2022, false 2024; `amount/single.yaml` and `amount/joint.yaml` match the
quoted $1,200/$600/$200 tiers). Comparing a TY2024-law total to a TY2023 actual
is a construction issue in its own right.

**Quantification (probe 3).** Re-running the TY2023 rule on the same 2024 data
(AGI-tier rate × the Colorado federal-CTC replica for under-6 children, ACTC
per-child cap $1,600) gives $167.9M on 198.3k units (avg $847), against
$89.16M on 130,188 claims (avg $685): ratio 1.88. Using the engine's
`co_federal_ctc` as is gives $179.1M (2.01). The law change is therefore worth
only 200.9 → 167.9, $33.0M of the $111.8M excess (30%; 22% in log terms); unit count (1.52) and
per-unit amount (1.24) both stay high under TY2023 law. Under TY2024 law,
$18.2M goes to 20.7k zero-earning units and $81.6M to units not required to
file. The row's description asserts that TY2023 law "reproduces the DOR actual
to the dollar" (2026-07 audit, l0-refit release, TY2024-law total then
$116.3M). That does not hold on this release: the TY2024-law level rose to
$183.5M at buildi and $200.9M now, so the data builds since l0-refit carry many
more Colorado young-child units with sizable credits. The residual is not
attributed this session (candidates: no claim gate, as in D6; Colorado
low-income young-child composition in the data). The row rests on 100 sample
records.

**Fix (construction_fix + annotation).** Do not compare a TY2024-law total to a
TY2023 actual: replace the benchmark with CO DOR TY2024 actuals when published,
or score the row under TY2023 law. Correct the row description now: the
"entirely law-change vintage" claim is refuted on spm-20260915 (TY2023 law on
the same data is still 1.88).

---

## D6. Flat refundable child credits: entitlement for every eligible unit versus claims (concept_mismatch, medium)

Claims `9eda40b94ca5ce924e04` (CA YCTC, 1.51), `a4ac9f4bd35f476eee27` (CO FAC,
1.76), `e598532e06e1a4b95e8f` (MD CTC, 1.74).

**Shared mechanism.** None of these formulas reads a take-up or filer
variable: `variables/gov/states/ca/tax/income/credits/young_child/ca_yctc.py:34-59`
(eligibility from `ca_eitc > 0` or the loss path; `ca_eitc_eligible.py:36-40`
has no earnings, filer or take-up test),
`variables/gov/states/co/tax/income/credits/family_affordability/co_family_affordability_credit.py:15-27`,
`variables/gov/states/md/tax/income/credits/ctc/md_ctc.py:18-49` and
`md_ctc_eligible.py:36-38`. The benchmarks are claims (FTB, MD DBM) or a claims
model with an explicit utilization rate (CO). For a flat per-child amount every
unclaimed eligible unit passes its full amount into the gap. The registry's own
open issue for this class is microcosm#341 (read this session; its numbers are
from the l0-refit release).

**CA YCTC** (FTB TY2023 $413M on 398,059 returns, as quoted in the registry
row; the FTB report itself returned HTTP 403 this session). Vintage: TY2023 parameters on
the same data give $595.7M (−4.2%; `parameters/gov/states/ca/tax/income/credits/young_child/amount.yaml`
$1,117 → $1,154, `phase_out/start.yaml` $25,775 → $26,626). After vintage the
ratio is 1.44. Per-unit amounts nearly agree (TY2023-law avg $1,093 vs FTB
$1,037, +5.4%); the excess is unit count (545.1k vs 398,059, 1.37). The
zero-earnings loss path is small ($31.0M, 26.9k units). 64.8% of PE dollars
($403.3M, 354.3k units) go to units not required to file a federal return.
Applying the engine's own `takes_up_eitc` flag would remove only 6.3%
($583.0M): 93% of YCTC-positive units carry the flag True, although the CA
seeded EITC take-up among all eligible units is 70.9%. The implied claim rate
is 0.73. If every required-to-file unit claimed, non-required units would need
a 58% claim rate to match FTB. No published YCTC take-up rate was verified this
session (FTB pages return 403), so the residual is not split further, and a
data over-count of low-income young-child units is not excluded.

**CO FAC** (benchmark $654M, the fiscal note's 75%-utilization TY2024 level).

> "there were 370,333 tax returns remitted for tax year 2019 that would have
> qualified for the tax credit … If all of these returns had claimed the credit
> in 2019, the total credit amount would have been about $900 million." …
> "It assumes 75 percent utilization for the credit in tax year 2024 … If 100
> percent of eligible taxpayers claim the credit, the credit in the bill would be
> estimated to reduce state revenue by about $880 million annually."
> — HB24-1311 Final Fiscal Note (August 5, 2024), p.4, State Revenue

Against the like-for-like 100% figure, PE is 1.31 ($1,151.5M). The engine rule
matches the note's summary (p.2: $3,200 under 6, $2,400 ages 6-16, 6.875% per
$5,000 above $15,000 single / $25,000 joint; parameters under
`parameters/gov/states/co/tax/income/credits/family_affordability/`). PE has
fewer units than the note's base (314.0k vs 370,333) but more dollars per unit
($3,667 vs about $2,380 at $880M). PE's high-amount units are concentrated
among units not required to file: $446.9M on 89.0k units (avg $5,020);
zero-earning units take $105.2M. The note's 100% figure is built only from
returns filed for 2019, so eligible families that did not file are outside it,
while PE includes them. Against $880M, the 100%-utilization adjustment covers
53% of the log gap (654 → 880); the rest is not attributed. Release history is volatile ($1,020M, $1,246M, $1,396M, $1,359M,
$1,151M), so the residual is also data-sensitive.

**MD CTC** (DBM FY2024 $13.8M; no claim counts). The engine applies the TY2023
law ($500 per child under 6 or disabled under 17, AGI ≤ $15,000;
`parameters/gov/states/md/tax/income/credits/ctc/agi_cap.yaml`,
`age_threshold/main.yaml`) unchanged in 2024, so there is no law vintage. PE
pays $24.08M on 37.0k units for 48.2k children (no disabled 6-16 children in
the data). 53.6% of dollars ($12.9M) go to units not required to file; zero-AGI
units take $2.36M. The benchmark implies about 27,600 children claimed (0.57 of
PE). The DBM report describes itself as a "statement of the estimated amount"
(reporting-law section), and its basis could not be confirmed this session.
The row swung $11.4M → $22.2M → $24.6M → $18.2M → $24.1M across releases, and
only 13 sample records carry a positive `md_ctc` in this release, so the level
is dominated by sampling noise; this item's MD part is low confidence. (For
scale: CA YCTC rests on 90 records, CO CTC on 100, CO FAC on 225 tax units.)

**Fix (annotation now; pe_issue for the mechanism).** Annotate each row:
PE is full entitlement including units that are not required to file; quote
the like-for-like CO figure ($880M at 100% utilization, 2019 filer base).
For the engine/data, extend microcosm#341: give state flat child credits a
claim gate (reuse the federal claim/filing flags or seed a state-credit
take-up), and calibrate it on the state counts that exist (FTB YCTC returns,
CO DOR claims, MN childless returns).

---

## D7. Illinois CTC: the benchmark is an ex-ante first-year estimate (open)

Claim `e053f2018d75bd10cecc`: GOMB $50M (TY2024, approximation); PE $79.4M (1.59).

**Finding.** `il_ctc` is 20% of `il_eitc` for units with a qualifying child
under 12 (`variables/gov/states/il/tax/income/credits/il_ctc.py:13-23`;
`parameters/gov/states/il/tax/income/credits/ctc/rate.yaml` 0.2 for 2024), and
`il_eitc` already carries the EITC take-up and filer gates
(`il_eitc.py:41-50` → `tools/state_eitc_helpers.py:128-139`), so this credit is
not in the D6 class. PE: $79.4M on 432.6k units (avg $184), 15.1% of PE's IL
EITC ($525.6M). PE's IL EITC is itself 1.20 of the TY2023 actual ($437.4M,
registry row `state_il_eitc`); scaling to that actual gives $66.1M, still 1.32
of $50M. The registry labels the benchmark an approximation with "no official
actuals"; the GOMB budget book could not be extracted this session (file over
the fetch limit), so its basis is unverified. The same $50M appears before
enactment as a forecast: "In its first year, the program is expected to cost
the state $50 million" (Capitol News Illinois, June 13, 2024). PE's IL CTC
rests on 154 sample records. No classification is evidenced.

**Fix (annotation).** Mark the benchmark as a pre-enactment estimate and
replace it with IDOR TY2024 claims when they are published.
