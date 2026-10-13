# Batch 2 / cluster B: JCT tax expenditures and IRS SOI income-tax aggregates

Scope: 6 claims on `populace-us-2024-spm-20260915` (bundle us-6.2.1 = policyengine-us 2.2.1).
All computations were run this session with `.venv-pe/bin/python` (one simulation at a
time) and with direct reads of `data/populace_us_2024.h5`. Scratch scripts and outputs are in
`/private/tmp/claude-501/-Users-pavelmakarchuk-policyengine-scorecard/f4a2f8d5-0a3a-4727-aebc-e3f8a13d165e/scratchpad/batch2-B/`
(`h5_totals.py`, `sim_b.py`, `sim_amt.py`, `sim_te.py`, `sim_agi.py`, `*_out.json`).

External documents extracted mechanically this session:

- **JCX-48-24** (`~/Downloads/x-48-24.pdf`, sha256 `227fabbe…8fff`), `pdftotext -layout` → `jcx4824.txt`.
- **IRS SOI Pub 1304 TY2023 Table 1.4** (`~/Downloads/23in14ar.xls`, sha256 `b6c1f87f…96af`), read with `xlrd`, row "All returns, total" and AGI classes.
- **IRS SOI Pub 1304 TY2023 Table 3.3** (`https://www.irs.gov/pub/irs-soi/23in33ar.xls`, downloaded this session, sha256 `e749d3e9…4c04`).
- **26 U.S.C. 408A and 219** (Cornell LII HTML, downloaded this session).

## Summary

| # | claim_id(s) | item | class | conf. | fix |
|---|---|---|---|---|---|
| 1 | `4c1e51a09563b19229d8` | SE pension (Keogh) TE, ratio 0.01 | `pe_gap` (split: concept 0.25) | high | pe_issue (microcosm) |
| 2 | `0bd035cc14714f0a289a` | SE health insurance TE, ratio 0.28 | `pe_gap` | high | pe_issue (microcosm) |
| 3 | `000c6065155be0232de2` | HSA TE, ratio 0.26 | `concept_mismatch` | high | annotation |
| 4 | `db63c233d9e3d2e33f86` | Traditional IRA TE, ratio 0.20 | `concept_mismatch` | medium | annotation (+ microcosm note) |
| 5 | `788712a4db74edbd1398` | SOI nonrefundable education credits, ratio 0.10 | `pe_gap` | high | pe_issue (microcosm) |
| 6 | `705dc2ffcbb72e8915a0` | SOI AMT, ratio 1.60 | `pe_gap` (top-tail weights) | medium | pe_issue (microcosm) + annotation |
| 7 | `788712a4db74edbd1398`, `705dc2ffcbb72e8915a0` | scorecard labels SOI rows `consumed_as_target` | `construction_issue` (label only) | high | construction_fix |

## How the producer computes these rows (question 1)

**JCT rows are not simulated. They are the calibration's own in-sample estimates.**

- Each registry row has `"in_sample": true`, `baseline_total: null`, `reform_total: null`
  (`sources/populace-reform-validation/raw/populace-us-2024-spm-20260915.json`).
- `microcosm/packages/microcosm-build/src/microcosm/build/us_runtime/reform_validation.py:862-863`:
  `if spec.in_sample and spec.id in estimates: effect = float(estimates[spec.id])`; the JCT figure is
  the calibration target (`:870-871`).
- `microcosm/tools/probe_us_post_export.py:2261-2280` (`_validation`) feeds the estimates from the
  build's `calibration_diagnostics.json` via `calibration_result_from_diagnostics` (`:896-915`),
  which reads each target's `final_estimate`.
- `calib_spm.json` (the release's diagnostics) matches the registry to the cent:

| target | target | initial_estimate | final_estimate | rel. error |
|---|---:|---:|---:|---:|
| self_employed_pension_contribution_deduction | 16.6e9 | 0.214e9 | 0.2069e9 | −0.988 |
| traditional_ira_deduction | 16.0e9 | 4.118e9 | 3.1334e9 | −0.804 |
| health_savings_account_deduction | 12.2e9 | 2.244e9 | 3.1248e9 | −0.744 |
| self_employed_health_insurance_deduction | 8.4e9 | 2.363e9 | 2.3791e9 | −0.717 |

- The target pairing is correct: each target neutralizes the matching engine variable
  (`microcosm/.../us/fiscal_target_references.json:204, 221, 256, 274` →
  `self_employed_health_insurance_ald`, `health_savings_account_ald`,
  `self_employed_pension_contribution_ald`, `traditional_ira_contributions`).
- **The calibration missed its own targets because the inputs cannot support them.** The initial
  estimates were already 1–28% of target (SE pension 1.3%, HSA 18%, IRA 26%, SEHI 28%), and the fit
  runs with `max_weight_ratio: 5.0` (`calib_spm.json` → `options`). Reweighting cannot lift the SE pension
  estimate 80x, and it can lift the others only by moving many other targets.
  For IRA, the fit moved the estimate *away* from target (4.12 → 3.13B) because other targets dominate.
- Re-simulation check (this session, `sim_te.py`: managed simulation on `data/populace_us_2024.h5` at 2.2.1,
  `income_tax` under `neutralize_variable(X)` minus baseline): SE pension $206,887,009; traditional IRA
  $3,133,821,110; HSA $3,126,553,667; SEHI $2,380,337,324. All four agree with the calibration
  `final_estimate` within 0.06%. The in-sample shortcut therefore reports what the released data gives;
  it is **not** a construction defect.

**SOI rows are simulated baseline levels.** `reform_validation.py:984-1001` (`_level_total`);
education uses `min(education_tax_credits, income_tax_before_credits)` per tax unit
(`soi_baseline_levels.json` `cap_variable`). Both rows are `"in_sample": false`, and the
release's 5,659 targets include **no** AMT, education-credit, IRA-payment, Keogh, SEHI or HSA
SOI target (searched `calib_spm.json` target names this session).

**Period labels.** The ledger IDs say `cy2024`, but the values are JCX-48-24 Table 1, whose title is
"Tax Expenditure Estimates By Budget Function, Fiscal Years 2024 - 2028" (FY2024 Individuals
column). FY2024 vs CY2024 differs by a few percent (for example SEHI 8.4 FY24 vs 9.3 FY25), which
is immaterial against ratios of 0.01–0.28. Not classified separately.

---

## 1. Self-employed pension contributions (Keogh) — `pe_gap`, split concept_mismatch 0.25

**Finding.** PE's self-employed pension input is about 3% of the SOI amount, and no record holds a
realistic contribution. A residual is concept: JCT's line is a net exclusion of contributions *and
earnings*.

Evidence:

- Engine: `self_employed_pension_contribution_ald_person.py:13-16` = `min(max(0, total_self_employment_income), self_employed_pension_contributions)`;
  `self_employed_pension_contributions.py:16-19` = `min(desired, limit)`; `self_employed_pension_contributions_desired.py:4-12` is a pure input.
- H5 (`h5_totals.py`): `self_employed_pension_contributions_desired` total **$1.373B**, 5.38M persons,
  1,654 records; unweighted quantiles among holders p50 $276, p99 $1,380, **max $1,771**.
  By support channel: PUF half $0.71B, ASEC half $0.66B.
- Engine ALD (`sim_b.py`): `self_employed_pension_contribution_ald` **$1.013B**, 5.33M tax units, mean $190.
- SOI TY2023 Table 1.4, "Payments to a Keogh plan", All returns: **946,019 returns, $30,130,848 thousand**.
  PE dollars = 3.4% of SOI; PE holders = 5.6x SOI returns.
- AGI profile (`sim_agi.py` vs SOI col 116): at $200K+ AGI, PE $0.23B vs SOI $24.3B (81% of SOI's Keogh
  dollars sit at $200K+).
- Source construction: `microcosm/.../us/spec/sources.yaml:458-530` (stage `retirement_contributions`) —
  notes at `:524-530`: "Measured ASEC RETCB_VAL is allocated across self-employed pension, defined-contribution,
  and IRA pools … QRF-imputes all five leaves onto the PUF half from the ASEC rows". The PUF half
  therefore does not carry tax-form Keogh amounts.
- JCT concept (JCX-48-24 Table 1, Income Security, verbatim):
  > Net exclusion of pension contributions and earnings:
  > Plans covering partners and sole proprietors (sometimes referred to as "Keogh plans") … 16.6
  
  Measurement text (JCX-48-24 pp. 3–4, Part I):
  > The tax expenditure for "net exclusion of pension contributions and earnings" is computed as the income taxes forgone on current tax-excluded pension contributions and earnings less the income taxes paid on current pension distributions
- microcosm already flags the concept (`fiscal_target_references.json:255` `concept_note`, ledger#118).

Quantification: the input factor alone is 1.013/30.13 = 0.034; the observed ratio is 0.0125. In log
terms the input explains ~77% of the gap; the residual 0.37 is marginal-rate mix plus the earnings
component that a contribution-only neutralization cannot reach.

**Fix draft (pe_issue, microcosm).** Title: "Self-employed pension contributions are ~3% of SOI Keogh
payments (max $1,771/person)". Body: the `retirement_contributions` stage allocates ASEC RETCB_VAL and
QRF-imputes it onto the PUF half, so the PUF's own Keogh/SEP/SIMPLE deduction amounts never reach
`self_employed_pension_contributions_desired`. Released H5: $1.37B on 5.4M persons vs SOI TY2023
Table 1.4 $30.13B on 946K returns. Proposed: (a) source the PUF half from the PUF Keogh-deduction
field (verify the field ID against the PUF codebook), or (b) add SOI Table 1.4 "Payments to a Keogh
plan" returns and amount as calibration targets; (c) keep the JCT row as a broad-fit anchor only,
because the JCT line includes inside build-up.

## 2. Self-employed health insurance — `pe_gap`

**Finding.** The concept matches; PE has the right number of claimants but about half the SOI amount,
and a lower revenue per deduction dollar.

- JCT concept (JCX-48-24 Table 1, Health, verbatim):
  > Deduction for health insurance premiums and long-term care insurance premiums by the self-employed … 8.4
- Engine: `self_employed_health_insurance_ald_person.py:13-16` = `min(SE earnings, self_employed_health_insurance_premiums)`;
  `self_employed_health_insurance_premiums.py:11-12` (`defined_for = "is_self_employed"`, `adds = ["health_insurance_premiums"]`).
- H5: `health_insurance_premiums` is populated only for `is_self_employed` persons: **$18.35B**, 3.74M persons.
- Engine ALD (`sim_b.py`): **$14.840B**, 3.688M tax units, mean $4,024.
- SOI TY2023 Table 1.4, "Self-employed health insurance deduction": **3,595,764 returns, $31,232,604 thousand**.
  Count ratio 1.03; amount ratio **0.475**; mean per return $8,686 vs PE $4,024.
- Revenue per deduction dollar: PE 2.379/14.84 = 16.0%; JCT implied 8.4/31.23 = 26.9% (TY2023 base as proxy). 0.475 × 0.60 ≈ 0.28 = the observed ratio.
- AGI profile (`sim_agi.py` vs SOI Table 1.4 col 118 by AGI class): below $200K AGI, PE $12.59B vs SOI
  $14.51B (0.87); at $200K and above, PE **$2.25B vs SOI $16.73B (0.13)**. The shortfall is almost entirely
  in high-AGI claimants, which explains both the amount factor and the low revenue per dollar.
- Source construction: `sources.yaml:2847-2927` (`attribute_self_employed_health_premiums`) copies the
  ASEC PHIP_VAL-based reported premium onto Schedule-C persons outside ESI and outside a Medicare proxy
  (age 65+ or SSDI). The stage notes already cite the SOI anchor (`:2926-2927`, ledger#105) but the
  release carries no SOI target for it.

**Fix draft (pe_issue, microcosm).** Title: "SE health insurance deduction is 48% of SOI TY2023 at the
right claimant count". Body: counts match SOI (3.69M vs 3.60M) but the per-claimant premium is half
($4,024 vs $8,686) and the claimants sit at lower marginal rates. Candidates to test (not verified):
CPS premium under-report; the Medicare-proxy exclusion (65+ / SSDI persons); tax-unit premiums assigned
to one person. Add SOI Table 1.4 SEHI returns and amount as calibration targets.

## 3. Health savings accounts — `concept_mismatch`

**Finding.** JCT's HSA line includes employer contributions made through cafeteria plans; PE neutralizes
only the individual above-the-line deduction. PE's deduction input is *above* SOI, so data is not the
cause of the low ratio.

- JCT (JCX-48-24 Table 1, Health, and footnote 14, verbatim):
  > Health savings accounts [14] … 12.2
  >
  > [14] Estimate includes employer contributions made through cafeteria plans to health savings accounts, which are also included in other line items on this table.
- Engine: `health_savings_account_ald.py:4-11` — a pure TaxUnit input with no formula. Payroll/employer
  contributions are a separate person input, `health_savings_account_payroll_contributions`
  (`household/expense/health/health_savings_account_contributions.py:4-12`), which the H5 does not carry.
- H5 / engine: `health_savings_account_ald` **$11.463B**, 2.001M tax units, mean $5,728.
- SOI TY2023 Table 1.4, "Health savings account deduction": **2,012,002 returns, $6,334,546 thousand**.
  Count ratio 0.99; amount ratio **1.81** (over, not under).
- PE revenue per deduction dollar 3.125/11.46 = 27%. AGI profile (`sim_agi.py` vs SOI col 110): at $200K+
  AGI, PE $7.17B vs SOI $2.80B, so PE's deduction is, if anything, too large and too high in the brackets.

**Fix draft (annotation).** "JCT's HSA tax expenditure includes employer contributions made through
cafeteria plans (JCX-48-24 Table 1 fn 14). PolicyEngine's row repeals only the individual HSA deduction
(`health_savings_account_ald`), so a ratio well below 1 is expected. PolicyEngine's HSA deduction input
($11.5B) is 1.8x SOI TY2023's $6.3B, so the deduction itself is not under-covered." Secondary note for
microcosm: the PUF-sourced HSA deduction is 1.8x SOI; consider an SOI Table 1.4 HSA target.

## 4. Traditional IRA — `concept_mismatch` (medium)

**Finding.** PE's deduction dollars match SOI, and PE's deduction sits at *higher* AGI than SOI's. A
deduction-only repeal cannot approach JCT's $16.0B; the JCT line values more than the deduction.

- Engine: `parameters/gov/irs/ald/deductions.yaml:15, 31, 46, 61` list `traditional_ira_contributions`
  itself as the ALD; `traditional_ira_contributions.py:19-22` = `desired * ira_contribution_scale`.
  No §219(g) active-participant reduction exists in the engine (grep for `219#g` / `active_participant`
  found nothing). §219(g)(1), verbatim (Cornell LII): "If … an individual or the individual's spouse is
  an active participant, each of the dollar limitations contained in subsections (b)(1)(A) and (c)(1)(A)
  … shall be reduced (but not below zero)".
- Engine (`sim_b.py`): `traditional_ira_contributions` **$14.730B**; 47.49M tax units (54.5M persons), mean
  $310 per tax unit. H5 unweighted quantiles among holders: p50 $180, p99 $2,244.
- SOI TY2023 Table 1.4, "IRA payments": **2,503,934 returns, $13,771,289 thousand**. Amount ratio 1.07;
  holder ratio **19x**; mean $5,500 vs $310.
- AGI profile (`sim_agi.py` vs SOI col 124): at $200K+ AGI, PE $5.24B vs SOI $2.10B; below $50K, PE $1.29B
  vs SOI $2.90B. PE's deduction is skewed to higher brackets (consistent with no §219(g) phase-out), so the
  PE-side data issues push PE's revenue loss **up**, not down. PE revenue per deduction dollar = 21%.
- JCT concept: JCX-48-24 Table 1 lists, under "Individual retirement arrangements:", "Traditional IRAs …
  16.0" and "Roth IRAs … 14.9". The document has no IRA method text. The Roth line shows the IRA lines
  are not deduction-only: 26 U.S.C. 408A(c)(1), verbatim: "No deduction shall be allowed under section 219
  for a contribution to a Roth IRA", and 408A(d)(1): "Any qualified distribution from a Roth IRA shall not
  be includible in gross income." A $14.9B Roth figure with no deduction can only come from the earnings
  side. This is an inference from the document's own figures; microcosm's `concept_note` at
  `fiscal_target_references.json:273` states the same, citing ledger#118. Confidence is medium because
  JCT's IRA method is not stated verbatim in JCX-48-24.

**Fix draft (annotation).** "JCT's Traditional-IRA line (JCX-48-24 Table 1) values the IRA regime, not
only the contribution deduction (the parallel Roth line is $14.9B, and §408A(c)(1) allows no deduction for
Roth contributions). PolicyEngine repeals only the deduction. PolicyEngine's deduction base ($14.7B)
matches SOI TY2023 IRA payments ($13.8B)." **Secondary microcosm/engine note (not the cause of the low
ratio):** traditional IRA contributions reach 47.5M tax units at a $310 mean vs SOI 2.5M returns at
$5,500, and policyengine-us 2.2.1 has no §219(g) active-participant phase-out; both skew PE's deduction
toward high AGI.

## 5. Nonrefundable education credits (SOI) — `pe_gap`

**Finding.** The Lifetime Learning Credit is a structural zero, and the AOTC student pool is 1.18M
persons with $4.4B of expenses. That input cannot produce $7.55B of nonrefundable credit.

- Engine: `education_tax_credits.py:13-16` = nonrefundable AOTC + LLC.
  `is_eligible_for_lifetime_learning_credit.py:29-47` requires
  `attends_eligible_educational_institution_for_lifetime_learning_credit` and (since
  `requires_1098_t_or_exception.yaml` = true from 2016) `has_lifetime_learning_credit_1098_t_or_exception`.
  Both are bool inputs with no `default_value` (so False) and are **absent from the H5**.
- Engine (`sim_b.py`): `lifetime_learning_credit` = 0 (0 eligible records); `education_tax_credits` =
  nonrefundable AOTC = **$0.780B**, 0.785M tax units; total AOTC $1.727B (0.894M units), refundable $0.691B.
- H5: `qualified_tuition_expenses` **$4.401B**, 1.18M persons, 426 records; all five AOTC flags are true on
  exactly those 426 records (`sources.yaml:441-456`, `derive_education_inputs`, notes: sets "all five
  affirmative AOTC inputs on that mask").
- Ceiling: AOTC is 100% of the first $2,000 and 25% of the next $2,000 (`american_opportunity_credit/amount.yaml`),
  so AOTC ≤ expenses; 40% is refundable (`refundability.yaml`). Nonrefundable AOTC ≤ 0.6 × $4.40B = $2.64B
  even with no tax-liability limit. Setting the LLC flags on the same mask would add nothing, because
  `lifetime_learning_credit_potential.py:19-23` excludes AOTC-eligible students.
- SOI TY2023 Table 3.3: "Nonrefundable education credit" **7,211,349 returns, $7,554,668 thousand**;
  "American opportunity credit" (refundable section) 5,821,688 returns, $5,090,364 thousand.
  JCX-48-24 Table 3 (2024 law/income), "Education Credits": 9,894 thousand returns, $14,796 million.
  PE claimant units are ~11% of SOI's nonrefundable returns.
- History (`data/populations.json`): f0af251 (1.729.0) $4.557B → l0-refit/buildi/buildj $0 → buildo $0.798B
  → spm $0.780B. The zeros are the structural zero microcosm#253 describes
  (`us_runtime/validation_input_coverage.py:12-15`). The LLC gate already existed at 1.764.6 (uv-cache copy
  `lifetime_learning_credit_potential.py:17-23`), so buildo also had LLC = 0. The f0af251 value was not
  re-derived (1.729.0 is not installed).
- The coverage gate registers only `qualified_tuition_expenses` for this row
  (`validation_input_coverage.py:122-125`), so the LLC zero passes the gate.

**Fix draft (pe_issue, microcosm).** Title: "Education credits at 10% of SOI: LLC structurally zero,
AOTC pool 1.18M students". Body: (1) produce LLC factual inputs and an LLC-expense population that is
not AOTC-eligible (graduate, part-time, non-degree); (2) widen qualified tuition expenses to SOI scale
(7.2M nonrefundable-credit returns, 5.8M AOTC returns in TY2023); (3) register
`attends_eligible_educational_institution_for_lifetime_learning_credit` and
`has_lifetime_learning_credit_1098_t_or_exception` in `US_VALIDATION_PROVISION_INPUT_LEAVES` (`validation_input_coverage.py:106`); (4) add SOI Table 3.3
education-credit returns/amount targets.

## 6. Alternative minimum tax (SOI) — `pe_gap` (top-tail weights), medium

**Finding.** PE's AMT comes from 70 records. The excess sits in the $1–2M AGI band, where PE has about 3x
SOI's returns, while PE has almost no returns above $5M. The total is volatile across releases.

- Engine (`sim_b.py`, `sim_amt.py`): AMT **$4.394B**, 241K weighted payers from **70 records** (SOI 150,167
  returns). The top 10 records hold **87%** of AMT dollars; weights 6.5K–25.8K each, AGI $0.9–2.9M.
- AMT payers: QDCG = 71% of AGI. This fits the post-TCJA pattern where the exemption phases out and the
  ordinary slice is taxed at 26/28% (`amt_tax_including_cg.py:15-35`, `alternative_minimum_tax.py:21-43`).
- AGI classes, PE 2024 filers vs SOI TY2023 Table 1.4 returns (col 1) and AMT (cols 143–144):

| AGI | PE filers | SOI returns | PE AMT payers / $ | SOI AMT returns / $ |
|---|---:|---:|---:|---:|
| $200K–500K | 13.69M | 10.96M | 0 / $0 | 29,331 / $0.354B |
| $500K–1M | 2.35M | 1.78M | 41.0K / $0.551B | 22,929 / $0.471B |
| $1M–1.5M | 1.20M | 368,931 | 94.1K / $1.302B | 16,889 / $0.262B |
| $1.5M–2M | 326K | 147,290 | 75.0K / $1.351B | 18,284 / $0.323B |
| $2M–5M | 209K | 203,230 | 29.5K / $1.184B | 27,153 / $0.578B |
| $5M–10M | 12K | 49,262 | 0 / $0 | 6,264 / $0.185B |
| $10M+ | ~0 (3 records) | 30,382 | 0 / $0 | 4,164 / $0.259B |

  Total AGI at $1M+: PE $2.61T vs SOI $2.54T. The aggregate is matched by compressing the top tail into $1–2M.
- Calibration diagnostics show the same band failing: `irs_soi.ty2022.historic_table_2.us.1m_plus.taxable_interest_returns`
  target 838,400, final 1,387,000 (+65%); `…1m_plus.taxable_interest_amount` target $160.3B, final $97.6B (−39%).
  No other AGI-class target exists for $1M+ returns.
- 1–2M band: weighted 1.53M filers, median record weight 0.008, max 31,876 — a few heavy records carry the band.
- History (`data/populations.json`): $1.13B (f0af251) → $1.70B → $2.77B (buildi) → $2.56B (buildj) → $4.25B (buildo) →
  $4.39B (spm). buildj → buildo is +66% at a fixed engine (1.764.6), so the drift is data/weights.
- Period: PE 2024 vs SOI TY2023 (minor against a 1.6x ratio).

**Fix draft (pe_issue, microcosm).** Title: "Top-tail compression: 3x SOI returns at $1–2M AGI, ~0 above
$10M; AMT 1.6x SOI from 70 records". Body: add SOI Table 1.4 AGI-class return counts and AGI amounts for
the $500K+ classes as targets; check why the Forbes-backed top tail (`sources.yaml:157` `forbes_top_tail_enabled: true`)
ends with ~zero weight; optionally add SOI AMT returns/amount. **Annotation:** "AMT is a top-tail statistic;
PolicyEngine's estimate rests on 70 records and has moved from $1.1B to $4.4B across releases."

## 7. SOI rows labeled `consumed_as_target` — `construction_issue` (label only)

`scorecard_db/ingest_reform_validation.py:723-725` labels every `"IRS SOI actual"` row `consumed_as_target`,
based on the docstring claim at `:54-56` ("IRS SOI totals are on the certified target surface"). The release
has no AMT or TY2023 Table 3.3 targets (no `alternative_minimum`/`education` names among 5,659 targets), and
the registry rows are `"in_sample": false`. This mislabels the AMT and education claims as calibrated (the same
rule applies to the other 7 SOI rows; outside this cluster). PE values are unaffected.

**Fix draft (construction_fix).** Derive `calibration_relationship` for SOI rows from the release's
`calibration_diagnostics.json` target names (or the row's `in_sample` flag), not from the category.


> **Applied in this PR (2026-10-06):** item 7's label fix — `scorecard_db/ingest_reform_validation.py` `SOI_HELD_OUT` relabels the AMT and education-credit SOI rows `held_out`. Item 7 is therefore not in `B.json` (one diagnosis per claim; those claims keep items 5 and 6).
