> **Filed 2026-10-06** (user-approved): P1 → PolicyEngine/policyengine-us#9919, P3 → #9920, P4 → #9921; M2 → PolicyEngine/microcosm#1116, M3 → #1117; M1 → comment on microcosm#944 (+ pointer on #646). P2 not filed (already fixed by policyengine-us#9577).

# Batch 2 upstream issue drafts (NOT POSTED)

Drafted 2026-10-06 from the batch-2 memos (`A.md`, `B.md`, `C.md`, `D.md`). Nothing below has been posted.
Do not file without Pavel's explicit go-ahead.

- Bundle: us-6.2.1 = policyengine-us 2.2.1 + `populace-us-2024-spm-20260915`.
- microcosm checkout: `/Users/pavelmakarchuk/microcosm` @ `581b569`.
- policyengine-us `main` checked at `6b80a8e447` (2026-10-06T17:07Z) for every engine claim.
- Raw extractions (statute HTML to text, `pdftotext -layout` output, SOI cells, engine/microcosm file copies, duplicate-search output):
  `/private/tmp/claude-501/-Users-pavelmakarchuk-policyengine-scorecard/f4a2f8d5-0a3a-4727-aebc-e3f8a13d165e/scratchpad/issue-evidence/`
  (`law/`, `forms/`, `soi/`, `main/`, `engine-2.2.1/`, `microcosm-581b569/`, `dupes/`).

## Status at a glance

| # | Target | Status | Duplicate / overlap |
|---|---|---|---|
| M1 | microcosm | **needs-changes**: post as a comment on microcosm#944 (same root cause, measured on wages), cross-link #646. Full issue text kept as fallback. | #944 (same root cause), #646, #981, #1044 |
| M2 | microcosm | **ready** | none; related #341, #348 |
| M3 | microcosm | **needs-changes**: 6 of 7 sections overlap open issues. File as a tracker that links them, or post per-section comments. Only A4 is new. | #505, #252, #586, #579, #253, #254, #958 |
| P1 | policyengine-us | **ready** | none; related #3686, #3707, #9633 |
| P2 | policyengine-us | **recommend not filing**: fixed by policyengine-us#9577 (merged 2026-10-03, released in 2.23.2) | #9577 |
| P3 | policyengine-us | **ready** (coordinate with open PR #9912) | none; related #9912, #9888 |
| P4 | policyengine-us | **ready** (statute and form support the claim; impact is attribution, not total tax) | none; related #7984 |

---

## M1 — microcosm: pooled ASEC income years in nominal own-year dollars vs 2024 SPM thresholds

**Target:** PolicyEngine/microcosm
**Recommendation:** microcosm#944 already reports the root cause (pooled prior-year ASEC dollars are not aged to the target year) for wages/FUTA, and asks whether that is intended. Post the body below as a **comment on #944** (it answers #944's question with the SPM consequence), and add a one-line pointer comment on #646. Use the title below only if the maintainers want a separate SPM-scoped issue.

**Title (fallback):** Pooled ASEC income years enter the US H5 in nominal own-year dollars, but SPM poverty tests them against 2024 thresholds

````markdown
Found by the policyengine-scorecard reform-validation diagnosis (batch 2), PolicyEngine/policyengine-scorecard#146. Memo: `diagnosis/batch2/C.md`, item C-1.
Related: #944 (same no-aging behavior, measured on wages), #646 (child-vs-total SPM anomaly), #981 (per-record donor aging), #1044 (default pool moved to income years 2023-2025).

## Summary

On the certified bundle us-6.2.1 (policyengine-us 2.2.1 + `populace-us-2024-spm-20260915`), records from ASEC income years 2022 and 2023 carry their own-year nominal dollars into the 2024 period, while the SPM calculator prices every unit at 2024 thresholds. The 2022-income records (34.1% of child weight) therefore meet a threshold about 13.7% above the one Census used for them; the 2023-income records meet one about 5.8% above.

First-order estimate (taxes and benefits not recomputed): testing each record against its own source-year threshold lowers the national 2024 SPM child rate from 15.83% to 13.24% (-2.6 pp) and the total rate from 13.06% to 11.48% (-1.6 pp). This is one component of the child excess in #646. The batch-2 decomposition of the +2.43 pp national child gap vs Census P60-287 is: populace weighting +3.1 pp, this item +2.6 pp, the policyengine-us partnership-income omission +1.3 pp, other resource differences -4.5 pp (all first order).

## What microcosm documents (@ 581b569)

> `docs/us-asec-source-pins.md:216-220`
> - **Money.** The pooled person tables carry nominal dollars of each income
>   year, as they did for 2022-2024; no base-build stage restates them by source
>   year. `target_aging` ages calibration targets, not survey records. The mean
>   income year of the default pool is 2024, the target year; for the old pool
>   it was 2023.

> `docs/us-spm-role-stage.md:143-144`
> ... each of the three Build P vintages (income years 2022-2024):

## What the engine does

The SPM threshold year is the simulation period for every unit, whatever its source year:

> `spm_calculator/policyengine_adapter.py:311-313` (spm-calculator 1.0.0, installed with policyengine-us 2.2.1)
> ```python
>     rows = [
>         bound._amounts(
>             int(period.start.year),
> ```

## Measurements on the certified H5

| Check | income year 2022 | 2023 | 2024 |
|---|---:|---:|---:|
| Share of child weight | 34.1% | 31.8% | 34.1% |
| Median of PE (market income + SS + SSI + UC) / Census `SPM_TOTVAL`, ASEC-channel units | 1.0000 | 0.9999 | 0.9999 |
| Child-weighted median of PE threshold / Census `SPM_POVTHRESHOLD` | 1.137 | 1.058 | 1.004 |
| Child-weighted median of PE geographic factor / Census `SPM_GEOADJ` | 0.997 | 0.997 | 1.000 |
| PE child SPM rate | 17.2% | 14.6% | 15.6% |
| Census `SPM_POOR` on the same weighted records | 15.4% | 17.5% | 16.6% |

- Wage inputs equal `WSAL_VAL` for 100% of ASEC-channel adults and 99.9% of PUF-clone adults.
- The geographic factors match Census, so the threshold gap is the year, not the county adjustment.
- Per state, the own-year-threshold effect is 0-5.5 pp (C.md, column `vint`).

## Why a pool centred on the target year still needs a fix

#1044 makes the default pool income years 2023-2025, whose mean is the target year. Each record is still tested against a threshold from a different year than its dollars: 2023 records against a higher one, 2025 records against a lower one. Poverty is a threshold test, so the two errors cancel only if the income density near the threshold is the same in both vintages. (Reasoning, not measured.)

## Options

1. Age pooled-year dollar inputs to the target year per record at build time, series by series (the per-record donor ager proposed in #981, applied to the ASEC pool). This is also the fix #944 asks about.
2. For the 3-year Census backtest rows (`us/state_spm_poverty_levels.json`), evaluate SPM status against each record's own source-year threshold. That matches how the Census flag on the H5 is built: `SPM_POOR == (SPM_RESOURCES < SPM_POVTHRESHOLD)` holds for 100% of units, with each source year's own thresholds.

## Acceptance test (external ground truth)

The H5 carries Census `SPM_POOR`, `SPM_RESOURCES`, `SPM_POVTHRESHOLD` and `source_year`, and PE and Census SPM units align exactly (0 of 59,900 PE units span more than one Census `SPM_ID`). After the fix, the by-source-year gap between PE's SPM status and Census `SPM_POOR` on ASEC-channel records should no longer depend on the source year, within a stated tolerance.

## Limits

First order: benefits and taxes are computed at 2024 law on nominal income and are not recomputed. Option 1 ages income with income-growth series, not SPM-threshold growth, so its effect will differ in size from the threshold counterfactual above.
````

---

## M2 — microcosm: registry spec fixes at policyengine-us 2.2.1 (D1, D2, D3, D5) + SE on state SPM rate rows (C-3)

**Target:** PolicyEngine/microcosm
**Title:** reform_validation registry: four state rows measure the wrong quantity at policyengine-us 2.2.1 (IA HF1020, MN WFC, ID CTC, CO CTC), and state SPM rate rows need a sampling SE

````markdown
Found by the policyengine-scorecard reform-validation diagnosis (batch 2), PolicyEngine/policyengine-scorecard#146. Memos: `diagnosis/batch2/D.md` (items D1, D2, D3, D5) and `diagnosis/batch2/C.md` (item C-3).

Values are on the certified bundle us-6.2.1 (policyengine-us 2.2.1 + `populace-us-2024-spm-20260915`). microcosm paths are relative to `packages/microcosm-build/src/microcosm/build/` @ 581b569; engine paths are relative to `policyengine_us/` 2.2.1. Each item is a construction defect in the registry spec: the row measures something other than its benchmark. None needs an engine change.

## 1. IA HF1020: the reform's bracket indices moved under policyengine-us 2.2.1 (`state.ia.hf1020`)

Registry: LSA -$17.7M (FY2026); PE -$1.84M (ratio 0.10).

> `us/state_reforms.json:176-185`
> ```json
>    "parameter_changes": {
>     "gov.states.ia.tax.income.credits.child_care.fraction[4].amount": {
>      "2025-01-01.2100-12-31": 0.5
>     },
>     "gov.states.ia.tax.income.credits.child_care.fraction[5].amount": {
>      "2025-01-01.2100-12-31": 0.5
>     },
>     "gov.states.ia.tax.income.credits.child_care.fraction[6].amount": {
>      "2025-01-01.2100-12-31": 0.5
>     }
> ```

- policyengine-us 1.764.6 (`parameters/gov/states/ia/tax/income/credits/child_care/fraction.yaml:22-50`) has seven brackets with thresholds -inf, 10,000, 20,000, 25,000, 35,000, 40,000, 90,000. Indices 4-6 were $35k-40k, $40k-90k and $90k+.
- policyengine-us 2.2.1 (same file, `:26-61`) inserts a 45,000 bracket (`:51-57`: 0.0 from 2006, 0.30 from 2021). Indices 4-6 are now $35k-40k, $40k-45k and $45k-90k. The $90k+ band moved to index 7 (amount 0.0) and the reform no longer changes it.

The bill covers the $90k+ band:

> Iowa LSA Fiscal Note, HF 1020 (Doc ID 1526230, April 22, 2025), p. 1, "Description":
> "House File 1020 reduces the number of net income thresholds for the Child and Dependent Care (CDC) Tax Credit from seven to four and allows any taxpayer with Iowa net income equal to or exceeding $25,000 to qualify for the refundable tax credit of up to 50.0% of the federal Child and Dependent Care Credit."

> Same, p. 2, "Assumptions":
> "1040 filers with an AGI of $90,000 or more will be able to access the State CDC Tax Credit due to the Bill and will realize an estimated decrease in tax liability beginning in TY 2025."

Effect (D.md, analytic on the 2025 baseline): the registry construction reproduces -$1.836M exactly. The bill-text construction (50% from $25k up, including $90k+) gives -$23.97M (1.35x the note), of which the $90k+ band is -$22.14M. Builds on 1.764.6 (old indexing) scored -$21.7M to -$27.6M.

**Fix.** Add `"gov.states.ia.tax.income.credits.child_care.fraction[7].amount": {"2025-01-01.2100-12-31": 0.5}`. Add a guard test that asserts, at the pinned engine, the thresholds the reform targets (25,000 / 35,000 / 40,000 / 45,000 / 90,000 at indices 3-7), so the next re-indexing fails loudly instead of rescoring a different bill.

Residual (open): PE keys the fraction on taxable income (`fraction.yaml:1`), while the note describes Iowa net income. PE's own 2025 baseline `ia_cdcc` is $19.4M; the note (p. 1, Background) reports IDR claims of "$11.0 million in FY 2024".

## 2. MN Working Family Credit row measures the pre-2023 `mn_wfc` (`state_mn_wfc`)

Registry: derived $191.5M (TY2024, `score_type: approximation`); PE $289.6M (1.51).

> `us/state_program_levels.json:110-113`
> ```json
>    "id": "state_mn_wfc",
>    "name": "Minnesota Working Family Credit",
>    "variable": "mn_wfc",
>    "period": 2024,
> ```

- `variables/gov/states/mn/tax/income/credits/mn_wfc.py:17-39` computes the credit from `p.wfc.pre_cwfc_legislation.*` parameters.
- The engine does not use `mn_wfc` in the 2023+ tax calculation: `parameters/gov/states/mn/tax/income/credits/refundable.yaml` lists `mn_wfc` only in its 2021 entry (`:3-6`); the 2023 and 2024 entries (`:8-16`) list `mn_child_and_working_families_credits`.

The official figure that isolates the non-child part:

> MN House Research, "Minnesota's Child Credit and Working Family Credit" (May 2026), p. 1:
> "For tax year (TY) 2024 returns filed in 2025, the combined cost of the child and working family credits was about $755.5 million. Of this amount, about 76 percent of credits before the phaseout were young child credits, 20 percent were working family credits, and 4 percent were credits for older children. About 240,100 returns with an older or younger child claimed about $665.9 million in credits, for an average credit of about $2,773. About 301,500 childless returns claimed about $89.6 million in credits, for an average credit of $297."

Effect (D.md): PE's pre-phaseout split is 23.5% WFC + older child, against House Research's 24%. A proportional split of PE's post-phaseout combined credit gives a WFC + older-child component of $238.5M (1.25x the derived benchmark), so the construction explains $51.1M of the $98.1M excess.

**Fix.** Retire `state_mn_wfc`, or re-measure it as PE's combined credit for units with no qualifying child against the childless subtotal ($89.6M on 301,500 returns). Keep `state_mn_cwfc` (1.14) as the primary MN row. Note: on this release that childless comparison is itself 1.85x (PE $165.5M on 453.0k units), so it would expose an open residual rather than close one.

Separate engine item (policyengine-us, not this repo): `variables/gov/states/mn/tax/income/credits/taxsim_mn_child_tax_credit_component.py:13-15` subtracts the same `mn_wfc` from the 2023+ combined credit.

## 3. Idaho CTC row sums the uncapped nonrefundable credit (`state_id_ctc`)

Registry: DFM $63.96M (CY2024); PE $96.66M (1.51).

- `variables/gov/states/id/tax/income/credits/id_ctc.py:12-19`: `eligible_children * p.amount`, with no liability cap.
- The cap applies only in `id_non_refundable_credits` (`variables/gov/states/id/tax/income/id_non_refundable_credits.py:15-24`). `id_ctc` is the only Idaho nonrefundable credit for 2018-2025 (`parameters/gov/states/id/tax/income/credits/non_refundable.yaml:17-20`).
- The row (`us/state_program_levels.json:609-622`) sets no `cap_variable`, so `_level_total` sums the uncapped amount (`us_runtime/reform_validation.py:984-1004`).

The benchmark is a foregone-revenue estimate for a nonrefundable credit:

> Idaho DFM, General Fund Revenue Book (January 2026), PDF p. 29, "Child Income Tax Credit: 63–3029L":
> "Description: The state provides a nonrefundable $205 individual income tax credit per qualifying child of the taxpayer."

> Same, PDF p. 20, table "Idaho Tax Preferences (Thousands)", Income Tax Credits (columns 2022-2028):
> "63-3029L Child Income Tax Credit $ 65,539 63,427 63,962 64,768 65,412 0 0"

> Same, PDF p. 17: "The estimates listed in the table in this section could be treated as upper bounds since they are computed by taking tax rates and applying them to existing sales and income figures."

Effect (D.md): capped at liability, PE is $73.24M (1.145x). Units with zero Idaho liability carry $22.3M of the uncapped amount. The construction explains $23.4M of the $32.7M excess (72%).

**Fix.** Set `"cap_variable": "id_income_tax_before_non_refundable_credits"` on the row (it has no `state` key, so `_level_total` reaches the capped branch at `reform_validation.py:997-1003`), or measure `id_non_refundable_credits`.

## 4. Colorado CTC: a TY2024-law total against a TY2023 actual (`state_co_ctc`)

Registry: CO DOR $89.16M (TY2023, 130,188 claims per the row); PE $200.9M (2.25), simulated at `"period": 2024` (`us/state_program_levels.json:70-80`).

Colorado changed the credit for TY2024:

> HB23-1112 (signed act), PDF p. 4, amending C.R.S. 39-22-129(3)(a):
> "(3) (a) Except as provided in subsection (4) of this section, for income tax years commencing on or after January 1, 2022, BUT BEFORE JANUARY 1,2024, a resident individual who claims a federal child tax credit for an eligible child on the individual's federal tax return is allowed a child tax credit in the amount set forth in subsection (3)(b) or (3)(c) of this"

> Same, PDF p. 5, new subsection (4.5)(a)(I):
> "(4.5) (a) (I) FOR INCOME TAX YEARS COMMENCING ON OR AFTER JANUARY 1, 2024, A RESIDENT INDIVIDUAL WHO FILES A SINGLE RETURN IS ALLOWED A CHILD TAX CREDIT AGAINST THE INCOME TAXES DUE UNDER THIS ARTICLE 22 FOR EACH ELIGIBLE CHILD OF THE TAXPAYER IN THE FOLLOWING AMOUNTS: (A) ONE THOUSAND TWO HUNDRED DOLLARS IF THE INDIVIDUAL'S FEDERAL ADJUSTED GROSS INCOME IS TWENTY-FIVE THOUSAND DOLLARS OR LESS;"

The engine switches regimes by year (`variables/gov/states/co/tax/income/credits/ctc/co_ctc.py:27-70`; `parameters/gov/states/co/tax/income/credits/ctc/ctc_matched_federal_credit.yaml`: `true` from 2022, `false` from 2024).

The row description (`us/state_program_levels.json:81`) says the gap "is entirely law-change vintage, proven by replication — running the pre-HB23-1112 TY2023 law (60/30/10% of federal CTC) on this same data reproduces the DOR actual to the dollar". That no longer holds: on this release the TY2023 rule on the same 2024 data gives $167.9M on 198.3k units (1.88x; D.md probe 3). The law change explains $33.0M of the $111.8M excess (about 30%).

**Fix.** Correct the description now. Then either score the row under TY2023 law or replace the benchmark with CO DOR TY2024 actuals when they are published. The residual is open (one candidate is the missing claim gate on flat child credits, #341).

## 5. State SPM rate rows: emit a sampling SE and an effective sample size (C-3)

`_person_rate` (`us_runtime/reform_validation.py:933-982`) returns a point estimate only, and the emitted row (`:1006-1034`) carries no uncertainty. On this release:

- the queued state child-rate rows rest on 26-149 effective child households (Kish), and the 10 largest households hold 11-48% of child weight;
- household-cluster linearized SEs of those rates are 3.7-7.1 pp, against Census rates of 5-18%;
- after the common national shift (+2.43 pp, child) is removed, 12 of the 14 high-side queued rows have |z| < 2 (exceptions: TN 2.14, FL 2.05).

**Proposal.** With every `statistic: "rate"` row, also emit the household-cluster linearized SE of the ratio estimator and the Kish effective number of households (for example `microcosm.standard_error` and `microcosm.effective_households`). Consumers can then flag on |z| instead of |ratio - 1|.
````

---

## M3 — microcosm: umbrella "tax-input coverage gaps surfaced by the reform-validation registry"

**Target:** PolicyEngine/microcosm
**Recommendation (needs-changes):** six of the seven sections overlap open microcosm issues (table below). Do not file a fresh umbrella that restates them as new. Either (a) file it as a **tracker** that links the existing issues and adds the us-6.2.1 numbers (the body below is written that way), or (b) post each section as a comment on its issue and open a new issue only for A4.

| Section | Existing issue | What is new here |
|---|---|---|
| A2 tips | #505 (open, carrier count -50.27% on Build N), #586 | within-occupation incidence (7.4% of waitstaff); FY2027 ratio 0.25 on us-6.2.1 |
| A3 car loan | #252 (open but stale: says the input is never imputed; the proxy now exists), #586, #981 | flow-vs-stock defect in the proxy |
| A4 non-itemizer giving | none (only #586 mentions the charitable line) | new |
| B1 Keogh | #579 (ALD stack under-fit), #445/#556 (closed, keogh carriers) | SOI Table 1.4 comparison, max $1,771/person |
| B2 SE health insurance | #579, #451 (closed) | right claimant count, half the amount, gap at AGI $200K+ |
| B5 education credits | #253 (open) | LLC structurally zero; coverage gate registers only tuition |
| B6 AMT / top tail | #958 (open, same top-tail compression), #254 (open, stale: says AMT 59% under; now 1.6x over) | AMT angle: 70 records, $1-2M band |

**Title:** Tax-input coverage gaps surfaced by the reform-validation registry on us-6.2.1 (tracker)

````markdown
Found by the policyengine-scorecard reform-validation diagnosis (batch 2), PolicyEngine/policyengine-scorecard#146. Memos: `diagnosis/batch2/A.md` (A2-A4) and `diagnosis/batch2/B.md` (B1, B2, B5, B6).

This tracker collects input-coverage gaps that the reform-validation registry shows on the certified bundle us-6.2.1 (policyengine-us 2.2.1 + `populace-us-2024-spm-20260915`). In every case the engine models the provision; the release's inputs cannot reach the benchmark. Each section links the existing issue where one exists and records only what is new. microcosm paths are relative to `packages/microcosm-build/src/microcosm/build/` @ 581b569.

### Benchmarks used below (extracted)

> JCX-35-25 (July 1, 2025), PDF p. 2, Chapter 2, $ millions, FY2025-2034:
> "1. No tax on tips (sunset 12/31/28) [5] ... tyba 12/31/24 --- -10,121 -7,664 -8,078 -5,262 -90 -98 -107 -117 -127 -31,664"
> "3. No tax on car loan interest ... iia 12/31/24 -1,932 -5,400 -8,070 -9,916 -5,313 --- --- --- --- --- -30,631"

> JCX-35-25, PDF p. 4, Chapter 4, Subchapter C:
> "4. Permanent and expanded reinstatement of partial deduction for charitable contributions of individuals who do not elect to itemize ... tyba 12/31/25 --- -1,543 -7,791 -8,149 ..."

> JCX-48-24, Table 1 "Tax Expenditure Estimates By Budget Function, Fiscal Years 2024 - 2028", Individuals, $ billions, 2024-2028:
> (PDF p. 33, Income Security) "Net exclusion of pension contributions and earnings: Plans covering partners and sole proprietors (sometimes referred to as "Keogh plans") ... 16.6 17.1 17.7 20.4 22.5"
> (PDF p. 32, Health) "Deduction for health insurance premiums and long-term care insurance premiums by the self-employed ... 8.4 9.3 11.9 13.4 14.0"

> IRS SOI Publication 1304, Table 1.4 "All Returns: Sources of Income, Adjustments, and Tax Items, by Size of Adjusted Gross Income, Tax Year 2023 (Filing Year 2024)" (`23in14ar.xls`), money in thousands of dollars, row "All returns, total":
> "Payments to a Keogh plan" (cols 115-116): 946,019 returns; 30,130,848
> "Self-employed health insurance deduction" (cols 117-118): 3,595,764 returns; 31,232,604
> "Alternative minimum tax" (cols 143-144): 150,167 returns; 2,752,164

> IRS SOI Publication 1304, Table 3.3 "All Returns: Tax Liability, Tax Credits, and Tax Payments, by Size of Adjusted Gross Income, Tax Year 2023 (Filing Year 2024)" (`23in33ar.xls`), row "All returns, total":
> "Tax credits > Nonrefundable credits > Nonrefundable education credit" (cols 8-9): 7,211,349 returns; 7,554,668
> "Tax credits > Total refundable credits > American opportunity credit" (cols 40-41): 5,821,688 returns; 5,090,364

PE values are calendar-2026 liability changes for OBBBA rows. The FY2027 JCT column is the like-for-like comparator for these provisions (FY2026 is a partial first year; A.md item A1).

---

### - [ ] A2. Tip income: incidence inside tipped occupations is too low (see #505, #586)

- Registry: PE -$1.93B vs JCT -$7.66B FY2027 (0.25) and -$10.12B FY2026 (0.19).
- H5 (2024, weighted): `tip_income` $34.3B on 2.97M recipients. Of 22.97M wage earners with a Treasury-listed occupation code, 1.72M (7.5%) have tips > 0. Waitstaff (Census 2018 occupation 4110, mapped to TTOC 102 in `us_runtime/sipp_tips.py:133-184`): 1.68M wage earners, 0.124M (7.4%) with tips. Bartenders: 18%.
- 2026 simulation: `tip_income_deduction` $16.9B on 1.54M tax units. At PE's revenue per deducted dollar (about 11.4%), JCT's FY2027 value needs about $67B of deductions, about 4x PE's.
- Mechanism (`us_runtime/sipp_tips.py`): annual tips are the December monthly SIPP amount x 12 (`:3-7`, `:334`); training is capped at 10,000 rows (`:114`, `:419-423`), and the code notes that "seed 0 materially under-samples positive tip rows in the 10,000-row cap" (`:117-119`). The occupation code "is a predictor, not a domain mask" (`:25`). The plausibility band checks only the all-person share with tips (`:127`), not incidence inside listed occupations.
- New relative to #505: #505 attributes the carrier deficit to the December-reference participation concept; the within-occupation incidence above is consistent with that explanation.
- Proposed: two-stage incidence/amount model conditional on a listed occupation; stratified donor sampling of positives; a gate on within-occupation incidence; the JCX-45-25 deduction line from #586 as a target.

### - [ ] A3. Qualified car-loan interest: the proxy uses one year of loan issuance as the stock (see #252, #586, #981)

- Registry: PE -$1.08B vs JCT -$8.07B FY2027 (0.13) and -$5.40B FY2026 (0.20).
- #252 says the input "is never imputed". That is stale: `us_runtime/scf_auto_loans.py:454-472` now sets qualifying interest = `auto_loan_interest` x min(1, 6,000,000 / weighted households with positive interest). The docstring (`:15-24`) calls 6M the number of qualifying loans "issued annually".
- The statute covers all post-2024 indebtedness, so the eligible stock grows each year:

> 26 U.S.C. 163(h)(4)(A) and (B)(i) (Cornell LII, current text): "In the case of taxable years beginning after December 31, 2024, and before January 1, 2029, for purposes of this subsection the term “personal interest” shall not include qualified passenger vehicle loan interest." ... "the term “qualified passenger vehicle loan interest” means any interest which is paid or accrued during the taxable year on indebtedness incurred by the taxpayer after December 31, 2024, for the purchase of, and that is secured by a first lien on, an applicable passenger vehicle for personal use."

- By TY2026 the stock holds about two annual vintages (less payoffs); the proxy holds one, and the engine uprates the input by CPI-U only (`policyengine_us/variables/.../qualified_passenger_vehicle_loan_interest.py:20`). First-order: a vintage-corrected input moves PE to about -$2.2B (0.27x FY2027). Most of the gap stays open: at PE's revenue per deducted dollar (about 10%), JCT's FY2027 value needs about $80B of deductions, more than all H5 auto-loan interest ($75.6B in 2026).
- Proposed: a vintage-stock share for the dataset's target year (sum over 2025+ vintages of 6M x survival), and an external household auto-debt benchmark for total `auto_loan_interest`. Update or close #252.

### - [ ] A4. Non-itemizer cash giving: donor incidence is about half of an external benchmark (new)

- Registry: PE -$3.52B vs JCT -$7.79B FY2027 (0.45).
- `charitable_cash_donations` comes from the `puf_tax_detail` stage, "IRS PUF 2015 (uprated)" (`us/spec/sources.yaml:110-111`, output list `:283`); the PUF field mapped to cash contributions is E19800 (`us_runtime/puf_aggregate_records.py:115`). Hypothesis, not verified against the PUF codebook: the field is observed only for itemizers, which would under-represent non-itemizer donors.
- H5: 23.9% of households and 19.1% of tax units have cash donations > 0 (25.5% of households give in any form); 4.8% at AGI $0-25K, 7.2% at AGI $25-50K.
- External benchmark:

> Lilly Family School of Philanthropy, news release (October 24, 2024), on its Philanthropy Panel Study (part of the PSID): "The share of Americans who give to charity declined from 50.9% in 2018 to 46.9% in 2020, following the onset of the pandemic."

- 2026 simulation: 18.3M of 147.5M non-itemizing tax units claim the deduction ($21.6B). At PE's revenue per deducted dollar (about 16%), JCT's FY2027 value needs about 40M claimants at PE's average amount, about 2.2x PE. A capped $1,000/$2,000 deduction scales mainly with donor count.
- Proposed: impute giving incidence and amount for all households from a source that observes non-itemizers (PSID PPS or CE cash contributions), or add a non-itemizer deduction target once an SOI series is sourced.

### - [ ] B1. Self-employed (Keogh/SEP/SIMPLE) pension contributions at about 3% of SOI (see #579)

- Registry: PE $0.21B vs JCT $16.6B (0.01). Note: JCT's line is a net exclusion of contributions and earnings, so a contribution-only repeal cannot reach it; the data gap is still the main factor.
- H5: `self_employed_pension_contributions_desired` $1.373B on 5.38M persons (1,654 records); among holders p50 $276, p99 $1,380, max $1,771. Engine ALD: $1.013B on 5.33M tax units. SOI: $30.13B on 946,019 returns (above), so PE dollars are 3.4% of SOI on 5.6x the claimants. At AGI $200K+, PE $0.23B vs SOI $24.3B.
- Mechanism (`us/spec/sources.yaml:524-530`, stage `retirement_contributions`): "Measured ASEC RETCB_VAL is allocated across self-employed pension, defined-contribution, and IRA pools ... QRF-imputes all five leaves onto the PUF half from the ASEC rows and PUF-imputed income." The PUF half does not carry tax-form Keogh amounts.
- Proposed: source the PUF half from the PUF Keogh-deduction field (verify the field ID in the codebook), or add SOI Table 1.4 "Payments to a Keogh plan" returns and amount as targets.

### - [ ] B2. Self-employed health insurance: right claimant count, half the amount (see #579)

- Registry: PE $2.38B vs JCT $8.4B (0.28).
- Engine ALD: $14.84B on 3.688M tax units (mean $4,024). SOI: $31.23B on 3,595,764 returns (mean $8,686). Count ratio 1.03, amount ratio 0.475.
- By AGI (SOI Table 1.4 col 118): below $200K, PE $12.59B vs SOI $14.51B (0.87); at $200K and above, PE $2.25B vs SOI $16.73B (0.13).
- Source (`us/spec/sources.yaml:2847-2927`, `attribute_self_employed_health_premiums`): the ASEC reported premium is copied onto Schedule-C persons outside ESI and outside a Medicare proxy.
- Proposed: test the CPS premium under-report, the Medicare-proxy exclusion and tax-unit premium assignment (not verified); add SOI Table 1.4 SEHI returns and amount by AGI as targets.

### - [ ] B5. Education credits at 10% of SOI: LLC structurally zero (see #253)

- Registry: PE $0.78B vs SOI $7.55B nonrefundable education credit (0.10).
- LLC: `is_eligible_for_lifetime_learning_credit.py:29-47` requires `attends_eligible_educational_institution_for_lifetime_learning_credit` and `has_lifetime_learning_credit_1098_t_or_exception` (bool inputs, so False when absent). Neither is in the H5, so `lifetime_learning_credit` = 0.
- AOTC: `qualified_tuition_expenses` $4.40B on 1.18M persons (426 records). Nonrefundable AOTC is at most 0.6 x $4.40B = $2.64B even without a liability limit. PE claimant units are about 11% of SOI's 7.2M nonrefundable-credit returns.
- The coverage gate registers only `qualified_tuition_expenses` for this row (`us_runtime/validation_input_coverage.py:122-126`), so the LLC zero passes the gate.
- Proposed: LLC factual inputs for a non-AOTC student population (graduate, part-time, non-degree); widen tuition to SOI scale; register both LLC flags in `US_VALIDATION_PROVISION_INPUT_LEAVES` (`:106`); add SOI Table 3.3 education-credit targets. #253's numbers are from f0af251; update it.

### - [ ] B6. AMT from 70 records: top-tail compression (see #958; #254 is stale)

- Registry: PE $4.39B vs SOI $2.75B (1.60). PE's AMT comes from 70 records; the top 10 hold 87% of AMT dollars.
- By AGI (PE 2024 filers vs SOI TY2023 Table 1.4 col 1 and cols 143-144): $1M-1.5M PE 94.1K payers / $1.30B vs SOI 16,889 / $0.26B; $1.5M-2M PE 75.0K / $1.35B vs SOI 18,284 / $0.32B; $5M-10M and $10M+ PE 0 vs SOI 6,264 / $0.18B and 4,164 / $0.26B.
- This is the same tail compression as #958 (too many returns at $1-2M, almost none above $5M), seen through AMT. #254 says AMT is 59% under; on us-6.2.1 it is 1.6x over, and the history moved $1.13B -> $4.39B across releases at a fixed engine for part of the path.
- Proposed: track under #958; comment on #254 that its sign changed.
````

---

## P1 — policyengine-us: SPM resources omit partnership/S-corp income but subtract the tax on it

**Target:** PolicyEngine/policyengine-us
**Title:** SPM resources leave out partnership/S-corp income (and other gross-income sources), while SPM taxes include the tax on them

````markdown
Found by the policyengine-scorecard reform-validation diagnosis (batch 2), PolicyEngine/policyengine-scorecard#146. Memo: `diagnosis/batch2/C.md`, item C-2.
Related: #3686 (closed, SPM resource components), #3707 (open, rename `spm_unit_net_income`), #9633 (merged; added `estate_income` to both `market_income` and `gov.household.market_income_sources`).

## Summary

`spm_unit_net_income` adds `spm_unit_market_income`, which adds person `market_income`. `market_income` does not include `partnership_s_corp_income`, `farm_rent_income`, `non_sch_d_capital_gains` or `ak_permanent_fund_dividend`, although all four are in `gov.irs.gross_income.sources`. `spm_unit_net_income` subtracts `spm_unit_taxes`, which includes federal income tax and self-employment tax computed on those sources. A family with partnership income therefore loses the tax on that income but never receives the income in SPM resources.

The household-level list `gov.household.market_income_sources` (used by `household_market_income`) does include `partnership_s_corp_income`, `farm_rent_income` and `ak_permanent_fund_dividend`, so the person and household market-income definitions disagree.

## Code (main @ 6b80a8e; policyengine-us 2.2.1 is identical except that `estate_income` was added by #9633)

Full component list, `policyengine_us/variables/household/income/person/general/market_income.py:13-30`:

```python
        COMPONENTS = [
            "employment_income",
            "self_employment_income",
            "sstb_self_employment_income",
            "pension_income",
            "dividend_income",
            "interest_income",
            "gi_cash_assistance",
            "capital_gains",
            "rental_income",
            "estate_income",
            "illicit_income",
            "farm_operations_income",
            "miscellaneous_income",
            "alimony_income",
            "strike_benefits",
            "retirement_distributions",
        ]
```

Full list, `policyengine_us/parameters/gov/irs/gross_income/sources.yaml:3-41` (comments omitted): `irs_employment_income`, `self_employment_income`, `sstb_self_employment_income`, `partnership_s_corp_income`, `farm_operations_income`, `farm_rent_income`, `other_net_gain_gross_income`, `capital_gains`, `non_sch_d_capital_gains`, `taxable_interest_income`, `rental_income`, `dividend_income`, `taxable_pension_income`, `debt_relief`, `estate_income`, `taxable_unemployment_compensation`, `taxable_social_security`, `illicit_income`, `taxable_retirement_distributions`, `taxable_roth_conversions`, `miscellaneous_income`, `ak_permanent_fund_dividend`, `taxable_alimony_income`, `salt_refund_income`.

Full list, `policyengine_us/parameters/gov/household/market_income_sources.yaml:3-29` (comments omitted): `employment_income`, `self_employment_income`, `sstb_self_employment_income`, `partnership_s_corp_income`, `gi_cash_assistance`, `farm_operations_income`, `farm_rent_income`, `capital_gains`, `interest_income`, `rental_income`, `dividend_income`, `pension_income`, `debt_relief`, `estate_income`, `illicit_income`, `retirement_distributions`, `miscellaneous_income`, `alimony_income`, `strike_benefits`, `ak_permanent_fund_dividend`.

The SPM chain:
- `variables/household/income/spm_unit/spm_unit_net_income.py:11-18`: `adds = ["spm_unit_market_income", "spm_unit_benefits", "acp", "ebb"]`, `subtracts = ["spm_unit_taxes", "spm_unit_spm_expenses"]`.
- `variables/household/income/spm_unit/spm_unit_market_income.py:11`: `adds = ["market_income"]`.
- `variables/household/income/spm_unit/spm_unit_taxes.py:11-18` (main; 2.2.1 has no `spm_unit_local_tax`): adds `spm_unit_payroll_tax`, `spm_unit_self_employment_tax`, `spm_unit_federal_tax`, `spm_unit_state_tax`, `spm_unit_local_tax`, `flat_tax`.
- `variables/household/expense/tax/spm_unit_federal_tax.py:11-12`: `sum_contained_tax_units("income_tax", spm_unit, period)`.
- `variables/gov/irs/tax/self_employment/taxable_self_employment_income.py:18-23`: SE tax sources include `partnership_self_employment_net_earnings`.
- `partnership_s_corp_income` adds `partnership_income` and `s_corp_income` (`variables/household/income/person/self_employment/partnership_s_corp_income.py:11`).

## Gross-income sources with no counterpart in SPM resources

Every other entry in `gov.irs.gross_income.sources` maps to a `market_income` component or to `spm_unit_benefits` (unemployment compensation, Social Security). These do not:

| Gross-income source | in `household_market_income`? | in `spm_unit_benefits`? | Suggested treatment |
|---|---|---|---|
| `partnership_s_corp_income` | yes | no | add to `market_income` |
| `farm_rent_income` | yes | no | add to `market_income` |
| `ak_permanent_fund_dividend` | yes | no | add (cash payment) |
| `non_sch_d_capital_gains` | no | no | review (capital gain distributions; `capital_gains` is already in `market_income`) |
| `debt_relief` | yes | no | review (not a cash receipt) |
| `other_net_gain_gross_income` | no | no | review |
| `taxable_roth_conversions` | no | no | leave out: its documentation says these amounts "do not represent cash retirement distributions available for spending" |
| `salt_refund_income` (main only) | no | no | review |

## Impact (certified bundle us-6.2.1: policyengine-us 2.2.1 + `populace-us-2024-spm-20260915`)

- First order (taxes not recomputed): adding positive `partnership_income + s_corp_income + farm_rent_income + non_sch_d_capital_gains` to SPM resources moves the 2024 national SPM child rate from 15.83% to 14.52% and the total rate from 13.06% to 12.18%. All of the change is in PUF-clone records (clone children 13.10% -> 10.87%; ASEC-channel children unchanged).
- Tennessee: -5.6 pp on the child rate, the largest single component of its 12.9 pp gap to Census.
- Example household (TN, PUF clone 1030751): `partnership_income` $287,010; federal income tax plus SE tax $51,891 against $11,408 of `market_income`; SPM resources -$17,378.

## Proposed change

Add `partnership_s_corp_income` and `farm_rent_income` to `market_income` (they are already in `gov.household.market_income_sources`), and decide the review rows above. Alternatively, have `market_income` read `gov.household.market_income_sources` so the two lists cannot drift again (#9633 had to edit both).

Consumers of `market_income` to check in the PR (code search on main): `variables/household/income/spm_unit/spm_unit_market_income.py:11`, `variables/household/marginal_tax_rate.py:104`, `variables/gov/states/mo/dss/ssp/mo_snc_countable_income.py:20`. (In 2.2.1 `variables/gov/hhs/ccdf/ccdf_income.py:10` also read it; that file is gone on main.) If a consumer must keep the narrower definition, add the sources to `spm_unit_market_income` only.

Test: a single adult whose only income is partnership income has `spm_unit_net_income` = that income minus `spm_unit_taxes` (an accounting identity of the variables above, not a premise of this issue). Today it is minus `spm_unit_taxes`.
````

---

## P2 — policyengine-us: `estate_tax_credit` returns the exclusion amount — RECOMMEND NOT FILING

**Reason:** already fixed upstream. policyengine-us#9577 "Compute the federal estate tax unified credit as tax on the applicable exclusion amount" merged 2026-10-03T11:56Z; CHANGELOG lists it under **2.23.2** (2026-10-03). Latest on PyPI today: 2.29.12. The scorecard bundle pins 2.2.1, so the defect is still in our bundle.

Verification of the fix (no filing needed):

> 26 U.S.C. 2010(a) (Cornell LII, current text): "A credit of the applicable credit amount shall be allowed to the estate of every decedent against the tax imposed by section 2001."

> 26 U.S.C. 2010(c)(1): "For purposes of this section, the applicable credit amount is the amount of the tentative tax which would be determined under section 2001(c) if the amount with respect to which such tentative tax is to be computed were equal to the applicable exclusion amount."

> 26 U.S.C. 2010(c)(2): "For purposes of this subsection, the applicable exclusion amount is the sum of— (A) the basic exclusion amount, and (B) in the case of a surviving spouse, the deceased spousal unused exclusion amount."

> 26 U.S.C. 2010(c)(3)(A): "For purposes of this subsection, the basic exclusion amount is $15,000,000."

> 26 U.S.C. 2001(c), top bracket: "Over $1,000,000 — $345,800, plus 40 percent of the excess of such amount over $1,000,000."

Tentative tax on $15,000,000 = 345,800 + 0.40 x 14,000,000 = **$5,945,800** (matches the Form 706 Rev. July 2026 line 9e value quoted in #9577). On the OBBBA revert value $6,790,000: $2,661,800.

- policyengine-us 2.2.1 `variables/gov/irs/credits/estate/estate_tax_credit.py:13-16` returns `p.base` ($15,000,000 for 2026, `parameters/gov/irs/credits/estate/base.yaml:61`), so estate tax is 0 below a taxable estate of $37,635,500.
- main `estate_tax_credit.py:23-33` returns `p.tax.estate.rate.calc(applicable_exclusion_amount)` with `applicable_exclusion_amount = p.credits.estate.base + deceased_spousal_unused_exclusion_amount`. This matches §2010(c)(1)-(2) as extracted.

**Action instead:** update the scorecard A6 annotation: "Engine credit defect fixed in policyengine-us 2.23.2 (#9577); the PE = 0 on us-6.2.1 is structural (no `taxable_estate_value` / `is_deceased` inputs in the H5) and remains after the engine upgrade."

---

## P3 — policyengine-us: casualty losses from declared disasters are zeroed

**Target:** PolicyEngine/policyengine-us
**Title:** Personal casualty losses are non-deductible from 2018 in PolicyEngine, but §165(h)(5) still allows losses attributable to federally (and, from 2026, State) declared disasters

````markdown
Found by the policyengine-scorecard reform-validation diagnosis (batch 2), PolicyEngine/policyengine-scorecard#146. Memo: `diagnosis/batch2/A.md`, item A5.
Related: #9912 (open; $100 per-casualty reduction; lists "declared-disaster attribution" and P.L. 119-108 qualified disaster losses as not modeled), #9888 (open; Montana, same note).

## What the engine does (main @ 6b80a8e = 2.2.1 for these files)

> `policyengine_us/parameters/gov/irs/deductions/itemized/casualty/active.yaml:8-11`
> ```yaml
>     # OBBB extends extends elimination of casualty expense deduction, with an exception for state declared disasters.
> values:
>   2013-01-01: true
>   2018-01-01: false
> ```

> `policyengine_us/variables/gov/irs/income/taxable_income/deductions/itemizing/casualty_loss_deduction.py:11-16`
> ```python
>     def formula(tax_unit, period, parameters):
>         loss = add(tax_unit, period, ["casualty_loss"])
>         p = parameters(period).gov.irs.deductions.itemized.casualty
>         positive_agi = tax_unit("positive_agi", period)
>         amount_over_floor = max_(0, loss - positive_agi * p.floor)
>         return p.active * amount_over_floor
> ```

`casualty_loss` (`variables/household/expense/tax/casualty_loss.py`) is one person input with no disaster attribution. From 2018 every personal casualty loss is therefore non-deductible. The parameter comment names the exception but no code implements it.

## What the statute says

> 26 U.S.C. 165(h)(5)(A) (Cornell LII, current text, under (h) "Treatment of casualty gains and losses", (5) "Limitation for taxable years beginning after 2017"):
> "In the case of an individual, except as provided in subparagraph (B), any personal casualty loss which (but for this paragraph) would be deductible in a taxable year beginning after December 31, 2017, shall be allowed as a deduction under subsection (a) only to the extent it is attributable to a Federally declared disaster (as defined in subsection (i)(5)) or a State declared disaster."

> 26 U.S.C. 165(i)(5)(A) (LII; "[2]" is LII's footnote marker): "The term “Federally [2] declared disaster” means any disaster subsequently determined by the President of the United States to warrant assistance by the Federal Government under the Robert T. Stafford Disaster Relief and Emergency Assistance Act."

The "State declared disaster" wording and the removal of the 2025 end date come from OBBBA:

> Pub. L. 119-21, § 70109 (139 Stat. 163-164), govinfo text:
> "(a) In General.--Section 165(h)(5) is amended-- (1) in subparagraph (A), by striking ``, and before January 1, 2026'', and (2) by striking ``2018 Through 2025'' in the heading and inserting ``Beginning After 2017''.
> (b) Extension to State Declared Disasters.-- (1) In general.--Subparagraph (A) of section 165(h)(5), as amended by subsection (a), is further amended by striking ``(i)(5))'' and inserting ``(i)(5)) or a State declared disaster''. ...
> (c) Effective Date.--The amendments made by this section shall apply to taxable years beginning after December 31, 2025."

So for TY2018-2025, losses attributable to a Federally declared disaster stay deductible; from TY2026, losses attributable to a State declared disaster are added (165(h)(5)(C) defines the term).

A later law also changes this area:

> 26 U.S.C. 165(h)(6)(A) (added by Pub. L. 119-108, § 2(a), Sept. 11, 2026): "If an individual has a qualified net disaster loss for any taxable year, the amount determined under paragraph (2)(A)(ii) shall be the sum of— (i) such qualified net disaster loss, and (ii) so much of the excess referred to in the matter preceding clause (i) of paragraph (2)(A) (reduced by the amount in clause (i) of this subparagraph) as exceeds 10 percent of the adjusted gross income of the individual."

> 26 U.S.C. 63(b)(8) (added by Pub. L. 119-108, § 2(c)): "so much of the deduction allowed by section 165(a) as is attributable to the qualified net disaster loss (as defined in section 165(h)(6)(B))."

> Pub. L. 119-108, § 2(d)(1) (note under 26 U.S.C. 63): "The amendments made by this section [amending this section and section 165 of this title] shall apply to taxable years beginning after December 31, 2024."

## Proposed change

1. Add a person input for the part of `casualty_loss` attributable to a declared disaster (Federally declared for 2018-2025; Federally or State declared from 2026). Apply `active = false` only to the remainder.
2. Optionally (or as a follow-up, as #9912 suggests): qualified disaster losses under 165(h)(6) ($500 reduction, no 10% floor) and the non-itemizer deduction under 63(b)(8), TY2025+.
3. Coordinate with #9912, which adds the $100 per-casualty reduction.

Tests (hand-computed from the text above: $100 reduction under 165(h)(1), as #9912 adds it, then the 10% floor under 165(h)(2); single casualty, no casualty gains):
- TY2026, itemizer, AGI $100,000, $20,000 loss not attributable to any declared disaster: 0.
- TY2026, same, loss attributable only to a State declared disaster (no Presidential declaration, so 165(h)(6) does not apply): (20,000 - 100) - 10,000 = 9,900.
- TY2025, the same State-declared-only loss: 0 (State declared disasters enter 165(h)(5)(A) from TY2026).
- Federally declared disaster cases: build from the Form 4684 instructions, because the qualified-disaster rules (165(h)(6) from TY2025; before that the provisions Pub. L. 119-108 § 2(d)(2) supersedes) change the $100/$500 reduction and the 10% floor.

## Impact and data note

- With the current certified dataset this change alone does not move baseline results: the input would default to 0. It matters for household calculations and for any dataset that carries the attribution.
- Context: JCX-48-24 Table 1 (PDF p. 32, Income Security) lists "Deduction for casualty and theft losses" for individuals at $0.1B in FY2024 and FY2025, so a post-2017 deduction exists in practice.
- In the scorecard's OBBBA row, the revert (`gov.irs.deductions.itemized.casualty.active: true`) gives back all losses, including disaster losses that are deductible in both worlds. PE is 2.27x JCT's FY2027 value ($0.29B vs $0.128B). That value rests on 33 PUF-derived tax units, one of which holds about half the weighted dollars, so the comparison is indicative only.
````

---

## P4 — policyengine-us: Ohio EITC applied before the credits that precede it by law

**Target:** PolicyEngine/policyengine-us
**Statute/form check:** both clearly support the claim (R.C. 5747.71 caps the EITC at tax "after deducting any other nonrefundable credits that precede" it in R.C. 5747.98; the 2021, 2022, 2023 and 2025 versions of 5747.98 all list the EITC after the retirement, senior, dependent care, displaced worker, exemption and joint filing credits, and through the 2023 version also after the campaign contribution credit; the 2024 Schedule of Credits puts it on line 13 after lines 2-12). **Ready.** Severity is low: in every case traced, total Ohio tax is unchanged; the defect is the attribution among credits.

**Title:** Ohio: `oh_eitc` is applied before the credits that R.C. 5747.98 and the Schedule of Credits place ahead of it

````markdown
Found by the policyengine-scorecard reform-validation diagnosis (batch 2), PolicyEngine/policyengine-scorecard#146. Memo: `diagnosis/batch2/D.md`, item D4.
Related: #7984 (merged; introduced ordered per-credit application).

## What the engine does (main @ 6b80a8e = 2.2.1 for these files)

> `policyengine_us/parameters/gov/states/oh/tax/income/credits/non_refundable.yaml:2-19`
> ```yaml
> values:
>   2021-01-01:
>     - oh_adoption_credit
>     - oh_eitc
>     - oh_cdcc
>     - oh_senior_citizen_credit
>     - oh_retirement_credit
>     - oh_non_public_school_credits
>     - oh_exemption_credit
>     - oh_joint_filing_credit
>   2023-01-01:
>     - oh_eitc
>     - oh_cdcc
>     - oh_senior_citizen_credit
>     - oh_retirement_credit
>     - oh_non_public_school_credits
>     - oh_exemption_credit
>     - oh_joint_filing_credit
> ```

`oh_eitc` (`variables/gov/states/oh/tax/income/credits/oh_eitc.py:19-30`) is capped by `applied_state_non_refundable_credit`, which subtracts only the credits listed before it (`variables/gov/states/tax/income/non_refundable_credit_cap.py:31-43`). With `oh_eitc` first, nothing precedes it. The joint filing credit base ("line 11") is liability minus the *applied* CDCC, senior, retirement and exemption credits (`variables/gov/states/oh/tax/income/credits/joint_filing_credit/oh_tax_before_joint_filing_credit.py:18-23`; `parameters/gov/states/oh/tax/income/credits/joint_filing/other_non_refundable_credits.yaml:3-7`), and those are already reduced by the EITC.

The existing test `tests/policy/baseline/gov/states/oh/tax/income/credits/oh_non_refundable_credit_order.yaml` ("Applied non-refundable credits follow filing order") encodes the EITC-first order (`oh_eitc: 80`, `oh_cdcc: 20` on $100 of liability), so it would need to change.

## What the law and form say

> R.C. 5747.71 (codes.ohio.gov; effective July 3, 2019):
> "There is hereby allowed a nonrefundable credit against a taxpayer's aggregate tax liability under section 5747.02 of the Revised Code for a taxpayer who is an "eligible individual" as defined in section 32 of the Internal Revenue Code. The credit shall equal thirty per cent of the federal credit allowed for the taxable year. The credit shall not exceed the aggregate amount of tax otherwise due under section 5747.02 of the Revised Code after deducting any other nonrefundable credits that precede the credit allowed under this section in the order prescribed by section 5747.98 of the Revised Code."

> R.C. 5747.98(A), version effective October 3, 2023 (H.B. 33), in force for TY2024, first eight items:
> "(A) To provide a uniform procedure for calculating a taxpayer's aggregate tax liability under section 5747.02 of the Revised Code, a taxpayer shall claim any credits to which the taxpayer is entitled in the following order:
> Either the retirement income credit under division (B) of section 5747.055 of the Revised Code or the lump sum retirement income credits under divisions (C), (D), and (E) of that section;
> Either the senior citizen credit under division (F) of section 5747.055 of the Revised Code or the lump sum distribution credit under division (G) of that section;
> The dependent care credit under section 5747.054 of the Revised Code;
> The credit for displaced workers who pay for job training under section 5747.27 of the Revised Code;
> The campaign contribution credit under section 5747.29 of the Revised Code;
> The twenty-dollar personal exemption credit under section 5747.022 of the Revised Code;
> The joint filing credit under division (G) of section 5747.05 of the Revised Code;
> The earned income credit under section 5747.71 of the Revised Code;"

The September 30, 2021, March 23, 2022 and September 30, 2025 versions list the same eight credits in the same order (the 2025 version drops the campaign contribution credit and cites division (E) for the joint filing credit). In the 2021 and 2022 versions the adoption credit (5747.37) comes after the nonchartered nonpublic school tuition credit, not first.

> 2024 Ohio Schedule of Credits (2024 Ohio IT 1040 bundle, PDF p. 7), Nonrefundable Credits [dot leaders removed]:
> " 1. Tax liability before credits (from Ohio IT 1040, line 8c)
>   2. Retirement income credit (include 1099-R forms)
>   3. Lump sum retirement credit (include a copy of the worksheet and 1099-R forms)
>   4. Senior citizen credit (must be 65 or older to claim this credit)
>   5. Lump sum distribution credit (include a copy of the worksheet and 1099-R forms).
>   6. Child care & dependent care credit (include a copy of the worksheet)
>   7. Displaced worker training credit (include a copy of the worksheet and all required documentation).
>   8. Campaign contribution credit for Ohio statewide office or General Assembly
>   9. Exemption credit
>  10. Total (add lines 2 through 9)
>  11. Tax less credits (line 1 minus line 10; if negative, enter zero).
>  12. Joint filing credit (see instructions for table). % times line 11, up to $650
>  13. Earned income credit"

> 2024 Ohio IT 1040 instructions (PDF p. 30), "Line 13 – Earned Income Credit": "Your nonrefundable Ohio earned income credit (EIC) equals 30% of your federal EIC (federal 1040 and 1040-SR, line 27). See R.C. 5747.71."

## Example (policyengine-us 2.2.1, TY2024, Ohio, married filing jointly, wages $30,000 + $6,000, children 4 and 2, child care $4,000)

Engine values: tax before nonrefundable credits $370.32; `oh_eitc_potential` $1,686.18; `oh_cdcc_potential` $170.00; `oh_exemption_credit_potential` $80.00; joint filing rate 15% (the rate the engine applies to this household).

| Line | Schedule of Credits order (hand computed) | Engine today |
|---|---:|---:|
| 1 Tax before credits | 370.32 | 370.32 |
| 6 CDCC | 170.00 | 0.00 |
| 9 Exemption credit | 80.00 | 0.00 |
| 11 Tax less credits | 120.32 | 370.32 (`oh_tax_before_joint_filing_credit`) |
| 12 Joint filing credit (15% of line 11) | 18.05 | 0.00 |
| 13 EITC (capped at 120.32 - 18.05) | 102.27 | 370.32 |
| Ohio income tax | 0.00 | 0.00 |

Reordering the parameter list to the statutory order reproduces the hand-computed column exactly.

## Impact

- Total Ohio income tax: unchanged in every case traced. The ordered aggregate (`oh_non_refundable_credits`) is still capped at liability, so the total of applied credits is min(sum, liability) in either order. (Reasoning plus three household checks; not proven for every input.)
- Changed: the applied amounts of `oh_eitc`, `oh_cdcc`, `oh_exemption_credit`, `oh_joint_filing_credit`, `oh_retirement_credit` and `oh_senior_citizen_credit`, and anything that reads them, including the `state_eitc` aggregates (`parameters/gov/states/household/state_eitcs.yaml` lists `oh_eitc`).
- Validation (certified bundle us-6.2.1): PE's 2024 `oh_eitc` total is $108.9M. Applying it after the preceding credits in the form order gives $95.9M (first order), so the ordering explains $13.0M of the gap to the scorecard's Ohio benchmark row ($59.3M, an ODT estimate the registry labels approximation; we did not re-extract that document).

## Proposed change

For `2021-01-01` and `2023-01-01`, reorder `gov.states.oh.tax.income.credits.non_refundable` to R.C. 5747.98: `oh_retirement_credit`, `oh_senior_citizen_credit`, `oh_cdcc`, `oh_exemption_credit`, `oh_joint_filing_credit`, `oh_eitc`, `oh_non_public_school_credits`, then `oh_adoption_credit` for 2021-2022. Update `oh_non_refundable_credit_order.yaml`, and add the household above as a test (expected values from the Schedule of Credits arithmetic).
````

---

## Duplicate-search results

All searches: `gh search issues --repo PolicyEngine/<repo> "<query>" --include-prs` (open and closed). Raw output in `issue-evidence/dupes/`.

**M1 (microcosm):** "nominal dollars ASEC pooled" (0), "SPM threshold source year" (0), "pooled income years" (#943, #853), "SPM child poverty" (#646, #1026, #1098, #348, #976, #925, #1070), "uprate pooled ASEC" (0), "income year deflate" (#1059), "nominal" (#668, #943, #958, ...), "source_year" (#1085, #720, #942, #744, #658, ...), "income year" (#296, **#944**, #719, #720, #943, #1044, ...), "vintage dollars" (#274), "SPM threshold" (#646, #893, #936, #1061, #976, #1044, #348, #925), "3-year average" (#348), "ASEC 2022" (#720, #296, #1085, #1039, #926, #1044, ...), "age to target year" (**#944**, #943, #204). Also read: #944 (open, "Pooled prior-year ASEC wages are not aged to the target year" — same root cause), #646, PR #1044, #981, PR #957 (forward static aging only).

**M2 (microcosm):** "HF1020" (#340, #319), "Iowa child care" (0), "bracket index reform" (0), "mn_wfc" (0), "Minnesota working family credit" (0), "Idaho child tax credit" (0), "cap_variable" (#348), "Colorado child tax credit" (0), "state_program_levels" (0), "state_reforms" (0), "standard error state rate" (0), "sampling error" (#292, #354), "effective sample size" (#285, #1088, #1075, #403, #458, ...), "reform validation registry" (#606, #629, #513, #977). No duplicate. Related: #341 (state credit take-up).

**M3 (microcosm):** "tip income" (**#505**, #361, #411, **#586**, #291, **#340**, #481, #465, #1029, ...), "tips imputation" (#395, #451), "SIPP tips" (#505, #481, ...), "car loan interest" (0), "auto loan" (**#252**, #49, #340, **#981**, #253, #324, #586, #361, #368, ...), "charitable" (#586, #1108, #298, #535, #327, #396, #186, ...), "non-itemizer" (#673, #511, #586, #299, #517, #357, #451), "Keogh" (#505, #769, **#579**, #556, #445, #446, ...), "self-employed pension" (#958, #964, #361, #279, #514, #451, #278, ...), "self-employed health insurance" (#38, #1071, #451, #514, #500, #26, #278, #279), "education credit" (**#253**, #340, #361, #251, #316, #247, ...), "lifetime learning" (#983), "AMT" (**#254**, #38, ...), "alternative minimum tax" (#254, #247), "top tail" (#725, #940, #567, #1102, #1112, #1006, **#958**, ...), "charitable cash donations", "E19800", "giving", "donations", "tipped occupation", "waitstaff", "SEHI", "health insurance premiums self-employed" (no new hits beyond the above).

**P1 (policyengine-us):** "market_income partnership" (0), "market income partnership S-corp" (0), "spm_unit_market_income" (#9633, #7696, #4833, #3706, #3686, #559), "market_income_sources" (0), "SPM net income partnership" (0), "market_income farm_rent_income" (0), "household_market_income market_income inconsistent" (0), "SPM resources S corporation" (0), "market_income missing" (0), "partnership income SPM" (#7462, #8747, #1053, #504, ...), "market income" (#9567, #9635, ...), "spm_unit_net_income" (#3707, #9694, #8089, #9493, #9633, ...), "partnership_s_corp_income" (#9910, #9909, #5272, #9793, #9804, #9805, #9306, #7461, ...). No duplicate.

**P2 (policyengine-us):** "estate tax credit", "unified credit", "estate_tax_credit", "tentative tax exclusion amount", "estate tax" -> **#9577 (merged 2026-10-03: the fix)**, #9633, #5399, #5171, #4660. Duplicate of a merged fix.

**P3 (policyengine-us):** "casualty loss" (**#9912**, **#9888**, #9614, #9625, #9693, #9695, ...), "casualty", "disaster loss", "federally declared disaster" (#9888, #9625, #7253, #7250, #6202), "qualified disaster" (#9912, #9888), "165(h)" (#9912, #9888, ...), "119-108" (#9912, #9637, ...), "net disaster loss" (#9888, #9625), "disaster attribution" (#9912), "State declared disaster" (#9912), "casualty active" (#9888, #9614, #9912). No issue for the disaster carve-out; #9912 and #9888 list it as not modeled.

**P4 (policyengine-us):** "Ohio EITC" (#9798, #9843, #4704, #8657, #8656, #7895, #7106), "Ohio earned income credit" (#4704, #1492, #7106, #2209), "Ohio nonrefundable credits order" (0), "Ohio credit order" (#7984), "Ohio joint filing credit" (#3527, #9890, #9876, #9797, #6879, #6880, #4348, #3671, ...), "5747.98" (0), "Ohio non-refundable" (#8657, #8656, #4704, #7106, #3760, #3241, #2665). No duplicate.

---

## Verification log

Each quote was re-read in the extracted file after drafting. "LII" = Cornell LII HTML converted to text with a local HTML-to-text script (`law/h2t.py`).

### Statutes and laws
| Quote | Source file (evidence dir) | Scope check |
|---|---|---|
| 26 U.S.C. 2010(a), (c)(1)-(3)(A) | `law/usc26_2010.txt` lines 141-167 (LII, sha256 `f5d7c56d…`) | under "(c) Applicable credit amount"; applies to estates of decedents |
| 26 U.S.C. 2001(c) top bracket | `law/usc26_2001.txt` lines 161-219 | under "(c) Rate schedule" |
| 26 U.S.C. 165(h)(5)(A), (i)(5)(A), (h)(6)(A) | `law/usc26_165.txt` lines 277-330, 361-365 (LII, sha256 `8b5a622a…`) | (h)(5) "Limitation for taxable years beginning after 2017", individuals; amendment notes lines 539-551, effective-date notes 669-677 |
| Pub. L. 119-21 § 70109 | `law/plaw119-21.htm` lines 5925-5971 (govinfo, sha256 `84000b07…`) | full section incl. (c) effective date |
| 26 U.S.C. 63(b)(8); Pub. L. 119-108 § 2(d)(1) | `law/usc26_63.txt` lines 140-173, 571-576 | (b) "Individuals who do not itemize"; note "Effective Date of 2026 Amendment" |
| 26 U.S.C. 163(h)(4)(A), (B)(i) | `law/usc26_163.txt` lines 609-619 (LII, sha256 `53ffe402…`) | (h)(4) "Special rules for taxable years 2025 through 2028 relating to qualified passenger vehicle loan interest" |
| R.C. 5747.71 | `law/orc_5747.71.txt` (codes.ohio.gov, effective July 3, 2019) | whole section |
| R.C. 5747.98(A),(B) | `law/orc_5747.98_2023-10-03.txt` (TY2024 version), `orc_5747.98.txt` (9-30-2025), `orc_5747.98_3-23-2022.txt`, `orc_5747.98_9-30-2021.txt` | list (A) order compared across all four versions; adoption credit position checked in 2021 and 2022 |

### Forms and documents (`pdftotext -layout`)
| Quote | File | Page |
|---|---|---|
| 2024 Ohio Schedule of Credits lines 1-13 | `forms/oh2024_bundle.txt` from `1040-bundle-original-fi.pdf` (tax.ohio.gov, sha256 `123ef745…`) | PDF p. 7 |
| 2024 IT 1040 instructions, Line 13 and Line 12 | `forms/oh2024_booklet.txt` from `it1040-booklet.pdf` (sha256 `e87bcf67…`) | PDF p. 30 (line 13), p. 29 (line 12) |
| Iowa LSA Fiscal Note HF 1020 | `forms/ia_hf1020_fn.txt` (legis.iowa.gov, sha256 `501dd13f…`) | p. 1 Description and Background; p. 2 Assumptions |
| MN House Research brief | `forms/mn_sschldwfc.txt` (house.mn.gov, sha256 `bdc01cb9…`) | p. 1 |
| Idaho DFM General Fund Revenue Book Jan 2026 | `forms/id_gfrb.txt` (sha256 `e01966ea…`) | PDF p. 29 (description), p. 20 (table), p. 17 (upper bounds) |
| CO HB23-1112 signed act | `forms/co_hb23_1112.pdf` (leg.colorado.gov, sha256 `3fe2772e…`) | PDF p. 4 ((3)(a)), p. 5 ((4.5)(a)(I)) |
| JCX-35-25 | `forms/jcx3525.txt` (jct.gov, sha256 `b33299c3…`) | PDF p. 2 (tips, car loan), p. 4 (non-itemizer charitable) |
| JCX-48-24 Table 1 | `soi/jcx4824.txt` (`~/Downloads/x-48-24.pdf`, sha256 `227fabbe…`) | PDF p. 33 Keogh (Income Security), p. 32 SEHI (Health), p. 32 casualty (Income Security) |
| SOI Table 1.4 TY2023 | `soi/t14_rows.txt` from `23in14ar.xls` (irs.gov, sha256 `b6c1f87f…`) | cols 1, 115-118, 143-144; rows "All returns, total" and $200K+ classes; $200K+ sums recomputed (Keogh 24,302,163; SEHI 16,726,766) |
| SOI Table 3.3 TY2023 | `soi/t33_rows.txt` from `23in33ar.xls` (irs.gov, sha256 `e749d3e9…`) | cols 8-9 (merged header "Nonrefundable credits"), 40-41 (merged header "Total refundable credits") |
| Lilly School PPS release | `forms/lilly_2024.txt` (sha256 `38977961…`) | dated October 24, 2024 |

### Engine lines re-read (policyengine-us 2.2.1 copies in `engine-2.2.1/`; main copies in `main/`)
- `market_income.py:13-30` (main, includes `estate_income`) and 2.2.1 `:13-29`; `gross_income/sources.yaml` main `:3-41`; `market_income_sources.yaml` main `:3-29`; `spm_unit_net_income.py:11-18`; `spm_unit_market_income.py:11`; `spm_unit_taxes.py` (main adds `spm_unit_local_tax`); `household/expense/tax/spm_unit_federal_tax.py:11-12`; `taxable_self_employment_income.py:18-23`; `spm_unit_benefits.py` (no `ak_permanent_fund_dividend`, main and 2.2.1); `taxable_roth_conversions.py:10-14`.
- `estate_tax_credit.py:13-16` (2.2.1) vs main `:23-33`; `estate/base.yaml:61`.
- `casualty/active.yaml:8-11`; `casualty_loss_deduction.py:11-16` (same on main).
- `oh/.../non_refundable.yaml:2-19` (same on main); `oh_eitc.py:19-30`; `non_refundable_credit_cap.py:31-43`; `oh_tax_before_joint_filing_credit.py:18-23`; `joint_filing/other_non_refundable_credits.yaml:3-7`; test `oh_non_refundable_credit_order.yaml:1-21`.
- `ia/.../child_care/fraction.yaml` 2.2.1 `:26-61` vs 1.764.6 `:22-50`; `mn_wfc.py:17-39`; `mn/.../refundable.yaml:3-16`; `id_ctc.py:12-19`; `id_non_refundable_credits.py:15-24`; `id/.../non_refundable.yaml:17-20`; `co_ctc.py:27-70`; `ctc_matched_federal_credit.yaml` values; `taxsim_mn_child_tax_credit_component.py:13-15`.
- `spm_calculator/policyengine_adapter.py:311-313` (period year used for thresholds).

### microcosm lines re-read (@ 581b569, copies in `microcosm-581b569/`)
- `docs/us-asec-source-pins.md:216-220`; `docs/us-spm-role-stage.md:143-144`.
- `us/state_reforms.json:176-185`; `us/state_program_levels.json:70-81, 110-121, 609-622`.
- `us_runtime/reform_validation.py:463-469, 933-982, 984-1004, 1006-1034`.
- `us_runtime/sipp_tips.py:3-7, 25, 114, 117-119, 127, 334, 419-423`; `us_runtime/scf_auto_loans.py:15-24, 454-472`; `us_runtime/validation_input_coverage.py:106, 122-126`; `us_runtime/puf_aggregate_records.py:115`; `us/spec/sources.yaml:110-111, 283, 524-530`.

### Computations run in this session
- P2: tentative tax on $15,000,000 = $5,945,800; on $6,790,000 = $2,661,800; zero-tax break-even under 2.2.1 = $37,635,500.
- P4: household runs on policyengine-us 2.2.1 (`issue-evidence/p4_household.py`, `p4_reorder.py`, output `P4_household_output.txt`); the statutory-order reform reproduced the hand-computed Schedule of Credits column (102.27 / 170.00 / 80.00 / 18.05) and left `oh_income_tax` unchanged in all three households.

### Not verified in this session
- All PE microdata measurements (rates, totals, record counts, per-state decompositions) are taken from the batch-2 memos; they are measurements on the certified bundle, not re-run here.
- M3 A4: whether PUF E19800 is populated only for itemizers (labeled as a hypothesis).
- M3 B1: the PUF Keogh-deduction field ID (left for the implementer to verify).
- P4: the Ohio TER benchmark ($59.3M) document was not re-extracted (memo D4 had a TLS error); the draft labels it as the registry's benchmark only.
- M2 item 2: the MN DOR $564M CTC figure used in the registry's derived benchmark was not re-verified (the draft does not rely on it).
- JCX-35-25 effective-date column for tips reads "tyba 12/31/24" in the PDF; memo A quoted "yba 12/31/24" from the staged harvest. The draft uses the PDF text.
