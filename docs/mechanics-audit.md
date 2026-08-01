# Defensive mechanics audit: PolicyEngine US take-up and calibration

Audit date: 2026-08-01. Scope: mechanics needed to compare PolicyEngine's 2024 US microdata with the Urban Institute's ATTIS-based *State of the Safety Net* results. This is a correctness audit, not an estimate of take-up.

## Executive findings

1. The running engine does **not** match the premise that there are 13 take-up flags and no WIC flag. PolicyEngine US 1.779.4 exposes 14 `takes_up_*` variables: 13 program flags plus `takes_up_dc_ptc`; `takes_up_wic_if_eligible` is one of them. Every flag is a bare input with `default_value = True` and no formula. (`EVIDENCE:evidence/engine_take_up_probe.txt:1-23`)
2. The exact pinned HDF5 stores only 11 of those 14 flags. It omits the current WIC, CHIP, and Basic Health Program flags. An omitted input therefore resolves to the engine's `True` default, unless supplied separately at runtime. (`EVIDENCE:evidence/pinned_artifact_probe.txt:24-56`; `EVIDENCE:evidence/engine_take_up_probe.txt:8-23`)
3. In the pinned artifact, only ACA PTC and housing have nonconstant stored take-up flags: 13.3491% of tax-unit rows and 18.7569% of SPM-unit rows, respectively. The other nine stored program flags are `True` on every row. These are **unweighted shares of entity records**, not participation rates among eligible people. (`EVIDENCE:evidence/pinned_artifact_probe.txt:24-36`)
4. Calibration is reweighting, not a second stochastic participation model. The cached release optimized 4,408 aggregate targets over 75,112 household weights with a capped relative-error objective; its targets are soft and were not all met exactly. Thus “pinned by calibration” below means approximately constrained as an aggregate numerator, never an exact individual take-up probability or exact recipient/eligible ratio. (`CACHE:calibration_diagnostics.json:3-49`; `EVIDENCE:evidence/pinned_diagnostics_summary.txt:1-10`)
5. The June 19 artifact was built with PolicyEngine US 1.729.0/core 3.26.11, whereas the running engine is 1.779.4/core 3.30.2 and current Populace `origin/main` is commit `8828dee`. Current build code is therefore evidence of the **current procedure**, not proof of the historical procedure that made the pinned artifact. That historical Populace source revision is **UNKNOWN** because the cached release manifest does not identify it. (`EVIDENCE:evidence/source_identity.txt:1-17`)

## Scope, versions, and citation convention

The installed `policyengine-us` distribution is editable: its `.pth` file points to `/Users/maxghenis/PolicyEngine/policyengine-us`, so `PEUS:` citations below resolve under `/Users/maxghenis/PolicyEngine/policyengine-us/policyengine_us/`. `PEUS729:` means the immutable PolicyEngine US git blob at commit `cc505a49493f8395b17c0ad79ea269bdbf23bb0c`, whose `pyproject.toml` identifies version 1.729.0. `CORE:` resolves under `/Users/maxghenis/PolicyEngine/policyengine-us/.venv/lib/python3.14/site-packages/policyengine_core/`. (`EVIDENCE:evidence/source_identity.txt:3-10`; `PEUS729:pyproject.toml:1-4`)

`POP@8828dee:` means the immutable blob read with `git -C /Users/maxghenis/PolicyEngine/populace show 8828dee:<path>`; it never denotes the `pr524` working tree. `CACHE:` means the exact cached release directory `/Users/maxghenis/.cache/huggingface/hub/datasets--policyengine--populace-us/snapshots/be80a14f5ac24d726d2dddb7da78c55570515aa3/releases/populace-us-2024-c86a631-6e1bcd0271a5-20260619T002242Z/`. `BUNDLE:` means `/Users/maxghenis/PolicyEngine/policyengine.py/src/policyengine/data/bundle/manifest.json`. (`EVIDENCE:evidence/source_identity.txt:1-3,11-25`)

Binary HDF5 claims cite the committed, reproducible probe output (`EVIDENCE:evidence/pinned_artifact_probe.txt`) and its script (`scripts/probe_pinned_artifact.py`). Diagnostic summaries cite `EVIDENCE:evidence/pinned_diagnostics_summary.txt`; exact target names remain those serialized in the cached JSON. A statement labeled **UNKNOWN** was not established from the available local evidence.

## A. Engine take-up mechanics

### A.0 Shared semantics

`defined_for = condition_name` is implemented by calculating the condition on the formula's output entity, then returning the variable's default where it is false—zero for the numeric benefits discussed here. When a person-level condition is requested by a group entity, the default person-to-group projection is a sum; the condition is therefore true when at least one group member is true. (`CORE:simulations/simulation.py:614-650,800-811,872-873`)

The flag definitions themselves contain no random seed or formula. An exhaustive scan of 5,651 engine variable files found no `random(...)`/RNG call and no take-up-parameter lookup; 5,536 parameter files contained no take-up filename or key. PolicyEngine Core also rejects formula randomness and directs authors to seed random input data outside formulas. (`EVIDENCE:evidence/engine_take_up_probe.txt:24-32`; `CORE:variables/formula_randomness.py:1-20,151-168`; `CORE:variables/variable.py:322-329`)

### A.1 Program-by-program trace

#### SNAP

- `snap` is an SPM-unit monthly variable that adds `snap_if_takes_up`; the whole formula is `defined_for = "takes_up_snap_if_eligible"`. The flag is an SPM-unit annual input defaulting to `True`. (`PEUS:variables/gov/usda/snap/snap.py:4-19`; `PEUS:variables/gov/usda/snap/takes_up_snap_if_eligible.py:4-9`)
- The benefit is formula-computed, not reported passthrough: `snap_if_takes_up` combines normal allotment, emergency allotment, and `dc_snap_temporary_local_benefit`; normal allotment is gated by `is_snap_eligible`. `is_snap_eligible` is an SPM-unit monthly eligibility variable. (`PEUS:variables/gov/usda/snap/snap_if_takes_up.py:4-31`; `PEUS:variables/gov/usda/snap/snap_normal_allotment.py:4-23`; `PEUS:variables/gov/usda/snap/eligibility/is_snap_eligible.py:4-36`)
- `receives_snap` is a separate reported SPM-unit input; it is not the dollar returned by `snap`. (`PEUS:variables/gov/usda/snap/receives_snap.py:4-8`; `PEUS:variables/gov/usda/snap/snap.py:4-19`)

#### SSI

- `ssi` is a person monthly variable and is `defined_for = "takes_up_ssi_if_eligible"`; the person annual flag defaults to `True`. (`PEUS:variables/gov/ssa/ssi/ssi.py:4-13`; `PEUS:variables/gov/ssa/ssi/takes_up_ssi_if_eligible.py:4-9`)
- Eligibility is person-level `is_ssi_eligible`; it gates `uncapped_ssi`. The final amount is formula-computed from the applicable federal benefit rate, countable income, and caps/floors, rather than copied from the reported `receives_ssi` Boolean. (`PEUS:variables/gov/ssa/ssi/is_ssi_eligible.py:4-18`; `PEUS:variables/gov/ssa/ssi/ssi_amount_if_eligible.py:7-70`; `PEUS:variables/gov/ssa/ssi/uncapped_ssi.py:4-16`; `PEUS:variables/gov/ssa/ssi/ssi_if_takes_up.py:16-39`; `PEUS:variables/gov/ssa/ssi/receives_ssi.py:4-8`)

#### TANF cash

- `tanf` is an SPM-unit annual variable and is `defined_for = "takes_up_tanf_if_eligible"`; the SPM-unit annual flag defaults to `True`. (`PEUS:variables/gov/hhs/tanf/cash/tanf.py:4-15`; `PEUS:variables/gov/hhs/tanf/cash/takes_up_tanf_if_eligible.py:4-9`)
- There is no single federal eligibility variable at this aggregation point. `tanf_if_takes_up` enumerates and sums state program outputs; those outputs implement state rules (for example Alabama and California). Consequently, the exact eligibility variable is state-dependent. (`PEUS:variables/gov/hhs/tanf/cash/tanf_if_takes_up.py:3-77`; `PEUS:variables/gov/states/al/dhs/tanf/al_tanf.py:4-16`; `PEUS:variables/gov/states/ca/cdss/tanf/cash/ca_tanf.py:4-28`)
- The amount is state-rule-computed, not a survey-dollar passthrough. `is_tanf_enrolled` defaults to the `receives_tanf` input and can enter continuation rules—as Texas's income test illustrates—but `tanf` does not simply return a reported benefit value. (`PEUS:variables/gov/hhs/tanf/cash/eligibility/is_tanf_enrolled.py:4-16`; `PEUS:variables/gov/states/tx/tanf/eligibility/tx_tanf_income_eligible.py:14-40`; `PEUS:variables/gov/states/tx/tanf/tx_tanf.py:4-25`; `PEUS:variables/gov/states/tx/tanf/tx_regular_tanf.py:4-26`; `PEUS:variables/gov/states/tx/tanf/ottanf/tx_ottanf.py:4-19`)

#### WIC

- Contrary to the stated premise, current 1.779.4 has `takes_up_wic_if_eligible`, a person monthly input defaulting to `True`. `wic` is person monthly and its formula is `defined_for` that flag. (`PEUS:variables/gov/usda/wic/takes_up_wic_if_eligible.py:4-9`; `PEUS:variables/gov/usda/wic/wic.py:4-19`; `EVIDENCE:evidence/engine_take_up_probe.txt:8-23`)
- Within that gate, `wic_if_takes_up` is `defined_for = "is_wic_eligible"` and returns base package value plus the conditional cash-value-benefit replacement adjustment `replaces_included_value * (current_cvb - included_cvb)`. `is_wic_eligible` is person monthly and computes categorical, income, and nutritional-risk conditions. (`PEUS:variables/gov/usda/wic/wic_if_takes_up.py:4-33`; `PEUS:variables/gov/usda/wic/is_wic_eligible.py:4-23`)
- Package value comes from an administrative average-cost parameter, not a reported benefit. `receives_wic` is a separate bare reported-enrollment input and is not referenced by the current benefit path; nutritional risk itself defaults to `True`. (`PEUS:parameters/gov/usda/wic/value.yaml:1-13,45-92`; `PEUS:variables/gov/usda/wic/receives_wic.py:4-8`; `PEUS:variables/gov/usda/wic/is_wic_at_nutritional_risk.py:4-11`; `PEUS:variables/gov/usda/wic/wic.py:4-19`)
- No engine WIC take-up-rate parameter, random draw, or formula seed was found. Absent a dataset value, the WIC flag is therefore `True`; the engine itself does not probabilistically choose participants. (`EVIDENCE:evidence/engine_take_up_probe.txt:8-32`)
- The build-time engine was different. Version 1.729.0's WIC path did not use `takes_up_wic_if_eligible`; its `wic` formula was eligibility-gated and multiplied the person-month input `would_claim_wic`, which also defaulted to `True`. Thus both the historical and current engine paths are identifiable, but they read different input names. (`PEUS729:pyproject.toml:1-4`; `PEUS729:policyengine_us/variables/gov/usda/wic/wic.py:4-31`; `PEUS729:policyengine_us/variables/gov/usda/wic/would_claim_wic.py:4-9`)

#### EITC

- `eitc` is a tax-unit annual variable `defined_for = "eitc_eligible"`. Its formula explicitly multiplies the computed credit by `takes_up_eitc` and a locally constructed filer Boolean: `tax_unit_is_required_to_file OR would_file_taxes_voluntarily OR would_file_if_eligible_for_refundable_credit`. The annual tax-unit flag defaults to `True`. (`PEUS:variables/gov/irs/credits/earned_income/eitc.py:4-31`; `PEUS:variables/gov/irs/credits/earned_income/takes_up_eitc.py:4-9`)
- `eitc_eligible` is tax-unit annual and combines demographic, investment-income, identification, and separate-filer rules. The benefit is formula-computed rather than passed through from survey dollars. (`PEUS:variables/gov/irs/credits/earned_income/eligibility/eitc_eligible.py:4-27`; `PEUS:variables/gov/irs/credits/earned_income/eitc.py:4-31`)

#### Refundable CTC / ACTC

- There is no refundable-CTC take-up flag in the runtime 14-flag inventory. `refundable_ctc` is a tax-unit annual formula that computes refundable amounts from phase-in, tax-limit, and maximum components; it does not multiply a participation flag. (`EVIDENCE:evidence/engine_take_up_probe.txt:8-23`; `PEUS:variables/gov/irs/credits/ctc/refundable/refundable_ctc.py:4-38`)
- Total `ctc` is `defined_for = "filer_meets_ctc_identification_requirements"`, a tax-unit rule derived from member identification requirements. Refundable CTC is included in the IRS refundable-credit list. This is formula computation, not a reported-benefit passthrough. (`PEUS:variables/gov/irs/credits/ctc/ctc.py:4-17`; `PEUS:variables/gov/irs/credits/ctc/maximum/individual/filer_meets_ctc_identification_requirements.py:4-16`; `PEUS:parameters/gov/irs/credits/refundable.yaml:1-26`)

#### Medicaid

- `medicaid` is person annual and adds `medicaid_cost`; cost is `defined_for = "medicaid_enrolled"`. Enrollment is itself `defined_for = "is_medicaid_eligible"` and returns `takes_up_medicaid_if_eligible`; that person annual flag defaults to `True`. (`PEUS:variables/gov/hhs/medicaid/medicaid.py:4-11`; `PEUS:variables/gov/hhs/medicaid/medicaid_cost.py:4-12`; `PEUS:variables/gov/hhs/medicaid/medicaid_enrolled.py:4-11`; `PEUS:variables/gov/hhs/medicaid/takes_up_medicaid_if_eligible.py:4-9`)
- `is_medicaid_eligible` is person annual and aggregates state/category eligibility paths. The dollar value is an administrative imputation: in dataset simulations, state spending is allocated using an SLCSP cost index and a weighted enrolled-person denominator; a single-household simulation instead uses administrative enrollment times the state-average index for its denominator. It is not a person-level benefit passthrough or a raw uniform per-capita survey value. (`PEUS:variables/gov/hhs/medicaid/eligibility/is_medicaid_eligible.py:4-54`; `PEUS:variables/gov/hhs/medicaid/costs/medicaid_cost_if_enrolled.py:4-22`; `PEUS:variables/gov/hhs/medicaid/costs/medicaid_slcsp_state_denominator.py:7-32`)
- `receives_medicaid` is a separate coverage input and does not supply `medicaid` dollars. (`PEUS:variables/gov/hhs/medicaid/receives_medicaid.py:4-17`; `PEUS:variables/gov/hhs/medicaid/medicaid.py:4-11`)

#### CHIP

- `chip` is person annual and `defined_for = "chip_enrolled"`; enrollment is `defined_for = "is_chip_eligible"` and returns the person annual `takes_up_chip_if_eligible` flag, which defaults to `True`. (`PEUS:variables/gov/hhs/chip/chip.py:4-18`; `PEUS:variables/gov/hhs/chip/chip_enrolled.py:4-11`; `PEUS:variables/gov/hhs/chip/is_chip_eligible.py:4-12`; `PEUS:variables/gov/hhs/chip/takes_up_chip_if_eligible.py:4-9`)
- The benefit is an imputed state per-capita value derived from separate-CHIP spending and administrative enrollment, not reported person-level dollars. (`PEUS:variables/gov/hhs/chip/per_capita_chip.py:4-28`)

#### ACA premium tax credit

- Gross `aca_ptc` is a tax-unit annual formula, but its `defined_for` condition is person-level `is_aca_ptc_eligible`; the core person-to-tax-unit projection makes the gate true when any member is eligible. For 2018 onward, gross PTC is the positive difference between SLCSP and required MAGI contribution, multiplied by tax-filer status. (`PEUS:variables/gov/aca/ptc/aca_ptc.py:4-28`; `PEUS:variables/gov/aca/eligibility/is_aca_ptc_eligible.py:4-23`; `CORE:simulations/simulation.py:614-650`)
- Take-up enters at annual `assigned_aca_ptc`, which multiplies gross `aca_ptc` by tax-unit annual `takes_up_aca_if_eligible`; the latter defaults to `True`. The monthly `premium_tax_credit` variable adds `assigned_aca_ptc`. (`PEUS:variables/gov/aca/ptc/assigned_aca_ptc.py:4-15`; `PEUS:variables/gov/aca/takes_up_aca_if_eligible.py:4-9`; `PEUS:variables/gov/aca/ptc/premium_tax_credit.py:4-11`)
- This is formula-computed PTC. `has_marketplace_health_coverage` is a separate person-level formula derived from the bare person-level interview-coverage input; neither is the returned PTC amount. (`PEUS:variables/household/expense/health/has_marketplace_health_coverage.py:4-19`; `PEUS:variables/household/expense/health/has_marketplace_health_coverage_at_interview.py:4-8`; `PEUS:variables/gov/aca/ptc/aca_ptc.py:4-28`)

#### Housing assistance

- `housing_assistance` is an SPM-unit annual formula `defined_for = "is_eligible_for_housing_assistance"`; it returns rule-computed `hud_hap * takes_up_housing_assistance_if_eligible`. The annual SPM-unit flag defaults to `True`. (`PEUS:variables/gov/hud/housing_assistance.py:4-18`; `PEUS:variables/gov/hud/takes_up_housing_assistance_if_eligible.py:4-9`)
- Eligibility is receipt **or** modeled renter/income eligibility. `hud_hap` applies maximum-subsidy and tenant-payment rules; `hud_max_subsidy` applies the PHA payment standard, and `hud_gross_rent` adds `pre_subsidy_rent` and utility allowance. The input `pre_subsidy_rent` is therefore an input to a computed HAP, not a `housing_assistance` dollar passthrough. (`PEUS:variables/gov/hud/is_eligible_for_housing_assistance.py:69-88`; `PEUS:variables/gov/hud/hud_hap.py:4-18`; `PEUS:variables/gov/hud/hud_max_subsidy.py:4-16`; `PEUS:variables/gov/hud/hud_gross_rent.py:4-13`; `PEUS:variables/household/expense/housing/pre_subsidy_rent.py:4-9`)
- `receives_housing_assistance` is a separate SPM-unit receipt input used in eligibility. (`PEUS:variables/gov/hud/receives_housing_assistance.py:4-9`; `PEUS:variables/gov/hud/is_eligible_for_housing_assistance.py:69-88`)

#### Free and reduced-price school meals

- Neither benefit has a take-up flag in the runtime inventory. `free_school_meals` and `reduced_price_school_meals` are SPM-unit annual formulas gated by the corresponding value of computed `school_meal_tier`. (`EVIDENCE:evidence/engine_take_up_probe.txt:8-23`; `PEUS:variables/gov/usda/school_meals/free_school_meals.py:4-15`; `PEUS:variables/gov/usda/school_meals/reduced_price_school_meals.py:4-15`)
- `school_meal_tier` uses income/FPG, categorical eligibility, and universal-state rules. Dollars are reimbursement net subsidy times school days and K–12 child count; `is_in_k12_school` assumes all ages 5–17 attend. No reported-enrollment input enters this benefit path. (`PEUS:variables/gov/usda/school_meals/school_meal_tier.py:4-38`; `PEUS:variables/gov/usda/school_meals/school_meal_net_subsidy.py:4-22`; `PEUS:variables/household/demographic/person/is_in_k12_school.py:4-17`)

#### Head Start and Early Head Start

- Both are person annual formula variables, each `defined_for` its own person-level eligibility and each multiplying its own person annual default-`True` take-up flag. (`PEUS:variables/gov/hhs/head_start/head_start.py:4-22`; `PEUS:variables/gov/hhs/head_start/early_head_start.py:4-22`; `PEUS:variables/gov/hhs/head_start/takes_up_head_start_if_eligible.py:4-9`; `PEUS:variables/gov/hhs/head_start/takes_up_early_head_start_if_eligible.py:4-9`)
- Eligibility variables are `is_head_start_eligible` and `is_early_head_start_eligible`. Benefit values are administrative state spending divided by enrollment and applied to qualifying people, rather than survey-reported benefits. (`PEUS:variables/gov/hhs/head_start/is_head_start_eligible.py:4-22`; `PEUS:variables/gov/hhs/head_start/is_early_head_start_eligible.py:4-24`; `PEUS:variables/gov/hhs/head_start/head_start.py:4-22`; `PEUS:variables/gov/hhs/head_start/early_head_start.py:4-22`)

#### Basic Health Program

- `basic_health_program` is a tax-unit annual variable `defined_for = "basic_health_program_tax_unit_enrolled"`. That tax-unit enrollment is true when any member's person-level `basic_health_program_enrolled` is true; person enrollment is `defined_for = "is_basic_health_program_eligible"` and returns the person annual default-`True` flag. (`PEUS:variables/gov/hhs/basic_health_program/basic_health_program.py:4-12`; `PEUS:variables/gov/hhs/basic_health_program/basic_health_program_tax_unit_enrolled.py:4-11`; `PEUS:variables/gov/hhs/basic_health_program/basic_health_program_enrolled.py:4-11`; `PEUS:variables/gov/hhs/basic_health_program/takes_up_basic_health_program_if_eligible.py:4-9`)
- Eligibility is person-level `is_basic_health_program_eligible`. The base/pre-2026 tax-unit benefit formula returns zero; the 2026 formula is a payment proxy based on adjusted reference premium, household contribution, reconciliation factor, and federal payment rate. Thus the requested 2024 artifact has no positive BHP dollar benefit from this formula. (`PEUS:variables/gov/hhs/basic_health_program/is_basic_health_program_eligible.py:4-8,28-77`; `PEUS:variables/gov/hhs/basic_health_program/basic_health_program.py:25-49`)

### A.2 LIHEAP and CCDF are not absent

The engine contains CCDF/child-care subsidies: `child_care_subsidies` aggregates state program outputs named in a parameter list, and the generic SPM-unit subsidy uses modeled eligibility. It also contains a bare `is_enrolled_in_ccdf` input. Exact take-up treatment is state-specific and was not exhaustively classified here: **UNKNOWN**. (`PEUS:variables/gov/hhs/ccdf/child_care_subsidies.py:4-11`; `PEUS:parameters/gov/hhs/ccdf/child_care_subsidy_programs.yaml:1-49`; `PEUS:variables/gov/hhs/ccdf/spm_unit_ccdf_subsidy.py:4-19`; `PEUS:variables/gov/hhs/ccdf/is_enrolled_in_ccdf.py:4-8`)

The engine also contains LIHEAP/energy-assistance implementations for DC, Illinois, Massachusetts, and Texas CEAP, plus Riverside County eligibility. A single nationwide `liheap` output and comprehensive national coverage are **UNKNOWN**. (`PEUS:variables/gov/states/dc/doee/liheap/dc_liheap_payment.py:4-18,38-55`; `PEUS:variables/gov/states/il/dceo/liheap/il_liheap.py:4-13`; `PEUS:variables/gov/states/ma/doer/liheap/payment/ma_liheap.py:4-18,39-46`; `PEUS:variables/gov/states/tx/tdhca/ceap/tx_ceap.py:4-16,19-46`; `PEUS:variables/gov/local/ca/riv/liheap/ca_riv_liheap_eligible.py:4-18`)

## B. What the pinned artifact stores

### B.1 Identity and layout

The exact reference named by `DEFAULT_DATASET` is cached. Its reference resolves to snapshot `18c16…`, its HDF5 blob SHA-256 is `f0af2519…`, and that hash matches the exact release manifest in cached snapshot `be80a14…`. The file contains PyTables entity tables `family`, `household`, `marital_unit`, `person`, `spm_unit`, and `tax_unit`, with 79,365; 75,112; 124,087; 160,858; 76,665; and 87,519 rows respectively. (`EVIDENCE:evidence/pinned_artifact_probe.txt:1-23`)

### B.2 Stored take-up flags

All percentages below are **unweighted shares of raw entity-table records**, not weighted shares and not shares among eligible records. (`EVIDENCE:evidence/pinned_artifact_probe.txt:24-36`)

| Entity table | Stored flag | True / rows | Unweighted True share |
|---|---|---:|---:|
| `person` | `takes_up_early_head_start_if_eligible` | 160,858 / 160,858 | 100% |
| `person` | `takes_up_head_start_if_eligible` | 160,858 / 160,858 | 100% |
| `person` | `takes_up_medicaid_if_eligible` | 160,858 / 160,858 | 100% |
| `person` | `takes_up_medicare_if_eligible` | 160,858 / 160,858 | 100% |
| `person` | `takes_up_ssi_if_eligible` | 160,858 / 160,858 | 100% |
| `spm_unit` | `takes_up_housing_assistance_if_eligible` | 14,380 / 76,665 | 18.7569294985% |
| `spm_unit` | `takes_up_snap_if_eligible` | 76,665 / 76,665 | 100% |
| `spm_unit` | `takes_up_tanf_if_eligible` | 76,665 / 76,665 | 100% |
| `tax_unit` | `takes_up_aca_if_eligible` | 11,683 / 87,519 | 13.3491013380% |
| `tax_unit` | `takes_up_dc_ptc` | 87,519 / 87,519 | 100% |
| `tax_unit` | `takes_up_eitc` | 87,519 / 87,519 | 100% |

Source for every row: `EVIDENCE:evidence/pinned_artifact_probe.txt:24-36`.

The HDF5 does **not** store `takes_up_wic_if_eligible`, `takes_up_chip_if_eligible`, or `takes_up_basic_health_program_if_eligible`; in the current engine all three therefore fall back to `True`. This is a silent 100%-of-eligible **flag gate** in a current-engine run of this artifact, subject to eligibility, other formula conditions, and any zero-valued formula. (`EVIDENCE:evidence/pinned_artifact_probe.txt:51-56`; `EVIDENCE:evidence/engine_take_up_probe.txt:11-12,23`)

### B.3 WIC, housing, rent, Medicaid, and CHIP fields

The person table stores `WICYN`, `receives_wic`, `is_wic_at_nutritional_risk`, and legacy `would_claim_wic`. `WICYN` has raw values `{0: 125135, 1: 1348, 2: 34375}`; `receives_wic` is true on 1,348 of 160,858 rows, while both risk and legacy `would_claim_wic` are true on every row. Build-time 1.729.0 multiplied that stored all-`True` legacy column; current 1.779.4 ignores it and instead reads the absent/default-`True` renamed flag. Both paths therefore pass the take-up gate for every eligible person, although by different input names. (`EVIDENCE:evidence/pinned_artifact_probe.txt:37-41,54`; `PEUS729:policyengine_us/variables/gov/usda/wic/wic.py:18-31`; `PEUS:variables/gov/usda/wic/wic.py:4-19`; `PEUS:variables/gov/usda/wic/wic_if_takes_up.py:4-33`)

The person table stores `pre_subsidy_rent` (5,722 nonzero rows); the SPM-unit table stores `receives_housing_assistance` (2,305 true rows) plus the take-up flag noted above. No entity table stores an exact `housing_assistance` or `rent` dollar column, and no entity table stores an exact `medicaid` or `chip` dollar column. These absences are consistent with engine-side computed/imputed benefits, but do not by themselves prove every build-stage transformation. (`EVIDENCE:evidence/pinned_artifact_probe.txt:42-56`)

The complete stored-column inventory is in Appendix 1. (`EVIDENCE:evidence/pinned_artifact_probe.txt:57-386`)

## C. Current Populace build: take-up seeding

### C.0 Version boundary

This section describes current `origin/main` at `8828dee`, not the unknown historical Populace revision that built the June artifact. The current contract says it was generated against PolicyEngine US 1.752.2; the audited runtime is 1.779.4 and the pinned artifact was built with 1.729.0. (`POP@8828dee:packages/populace-build/src/populace/build/us/take_up_contract.json:1-15`; `EVIDENCE:evidence/source_identity.txt:1-17`)

### C.1 Contract and rates

The contract declares an engine-asserted set of 13 flags. All 13 have engine class `data_seeded`, which the contract defines as a bare input leaf—not a claim that Populace actually writes the column. Its separate `populace_treatment` field and dedicated-stage ownership determine the current build action. (`POP@8828dee:packages/populace-build/src/populace/build/us/take_up_contract.json:1-15,17-204`)

| Flag | Current contract/build action | Contract source or note | Citation |
|---|---|---|---|
| SNAP | `out_of_scope` for generic seeder; dedicated stage seeds a 0.82 national prior and recalibrates by state household counts | USDA FNS participation rate | `POP@8828dee:packages/populace-build/src/populace/build/us/take_up_contract.json:19-27`; `POP@8828dee:packages/populace-build/src/populace/build/us/source_stages.json:1950-2036` |
| TANF | `seed`; stable hash-based Bernoulli draw at 0.219 | HHS ASPE 2022 | `POP@8828dee:packages/populace-build/src/populace/build/us/take_up_contract.json:30-45` |
| EITC | `seed`; stable hash-based Bernoulli draw by children: 0=0.65, 1=0.86, 2=0.85, 3+=0.82 | IRS National Taxpayer Advocate; 3+ correction explicitly recorded | `POP@8828dee:packages/populace-build/src/populace/build/us/take_up_contract.json:48-63` |
| Medicaid | `count_calibrated`; dedicated stage, no scalar rate | reported coverage anchor plus CMS/model eligibility and count facts | `POP@8828dee:packages/populace-build/src/populace/build/us/take_up_contract.json:66-82`; `POP@8828dee:packages/populace-build/src/populace/build/us_runtime/medicaid_take_up.py:1-56,136-195,214-239,253-340` |
| CHIP | `rate_unsourced`; left unseeded/default `True` | standalone current rate unavailable; concept split unresolved | `POP@8828dee:packages/populace-build/src/populace/build/us/take_up_contract.json:85-94` |
| BHP | `rate_unsourced`; left unseeded/default `True` | no source | `POP@8828dee:packages/populace-build/src/populace/build/us/take_up_contract.json:97-106` |
| Medicare | `out_of_scope` for generic seeder; dedicated measured-input stage | ASEC `MCARE == 1`, no scalar rate | `POP@8828dee:packages/populace-build/src/populace/build/us/take_up_contract.json:109-118`; `POP@8828dee:packages/populace-build/src/populace/build/us_runtime/medicare_take_up.py:1-8,131-155,172-229` |
| SSI | `count_calibrated`; dedicated age-band prior stage, no flag count-matching | `SSI_VAL` anchors and SSA December 2024 federal-payment-recipient facts; ordinary weight calibration later targets the same counts | `POP@8828dee:packages/populace-build/src/populace/build/us/take_up_contract.json:121-145`; `POP@8828dee:packages/populace-build/src/populace/build/us_runtime/ssi_take_up.py:1-26,482-511,550-698,1097-1136` |
| DC PTC | `rate_unsourced`; left unseeded/default `True` | published claim count is not a participation rate | `POP@8828dee:packages/populace-build/src/populace/build/us/take_up_contract.json:148-157` |
| Head Start | `out_of_scope` for generic seeder; dedicated measured-proxy stage | SIPP donor proxy, no scalar rate | `POP@8828dee:packages/populace-build/src/populace/build/us/take_up_contract.json:160-169`; `POP@8828dee:packages/populace-build/src/populace/build/us_runtime/sipp_head_start.py:1-24,88-109,614-619` |
| Early Head Start | `rate_unsourced`; left unseeded/default `True` | individual-level source unavailable | `POP@8828dee:packages/populace-build/src/populace/build/us/take_up_contract.json:172-181` |
| Housing | `out_of_scope` for generic seeder; dedicated measured/imputed-receipt stage | exact receipt anchor, no scalar rate | `POP@8828dee:packages/populace-build/src/populace/build/us/take_up_contract.json:184-193`; `POP@8828dee:packages/populace-build/src/populace/build/us/source_stages.json:2400-2530` |
| ACA | `out_of_scope` for generic seeder; dedicated anchored rate/count stage | contract metadata 0.672; operational builder derives a clipped CMS APTC/eligible-weight rate | `POP@8828dee:packages/populace-build/src/populace/build/us/take_up_contract.json:196-204`; `POP@8828dee:tools/build_us_fiscal_refresh_release.py:2494-2516`; `POP@8828dee:packages/populace-build/src/populace/build/us/source_stages.json:2680-2785` |

The generic seeder's stated scope is TANF and EITC. It generates stable BLAKE2-based uniform draws from source identity, approximates EITC child count as the number of tax-unit members under 19, and assigns a flag when `draw < rate`. The draw covers **all** SPM units for TANF and all tax units for EITC, not only formula-eligible units; PolicyEngine's eligibility and filer logic gates benefits later. On assembled frames the seeder fills missing values; its legacy unassembled-frame path also replaces a missing **or constant** column. (`POP@8828dee:packages/populace-build/src/populace/build/us_runtime/take_up.py:1-38,112-159,200-239,242-294,307-394`)

SNAP, Medicaid, SSI, Medicare, Head Start, housing, and ACA have dedicated current stages rather than merely the generic scalar seeder. SNAP forces reported recipients true, then chooses a nonreporter threshold that targets a weighted all-SPM-unit flag share of 0.82 **in expectation**, unless reporter mass already meets or exceeds the target; a state household-count stage subsequently recalibrates assignments. Medicaid anchors coverage and excludes CHIP from that flag; SSI derives age-band priors without count-matching flags; Medicare maps measured `MCARE == 1`; Head Start uses a SIPP donor proxy; and housing uses measured/imputed receipt without adding random nonreporters. (`POP@8828dee:packages/populace-build/src/populace/build/us_runtime/snap_take_up.py:1-35,95-122,218-230,251-300`; `POP@8828dee:packages/populace-build/src/populace/build/us_runtime/snap_state_take_up.py:1-47,115-170,340-395`; `POP@8828dee:packages/populace-build/src/populace/build/us_runtime/medicaid_take_up.py:1-56,253-340`; `POP@8828dee:packages/populace-build/src/populace/build/us_runtime/ssi_take_up.py:1-26,1097-1136`; `POP@8828dee:packages/populace-build/src/populace/build/us_runtime/medicare_take_up.py:1-8,131-155`; `POP@8828dee:packages/populace-build/src/populace/build/us/source_stages.json:1357-1486,1988-2036,2400-2530,2680-2785`)

The ACA contract's 0.672 is metadata, not the operational draw rate. The current builder derives a clipped state prior from CMS APTC targets divided by weighted eligible units; the dedicated stage anchors reported **subsidized** marketplace coverage and then calibrates assignment to CMS counts, with optional IRS PTC count/amount controls. (`POP@8828dee:packages/populace-build/src/populace/build/us/take_up_contract.json:196-204`; `POP@8828dee:tools/build_us_fiscal_refresh_release.py:2494-2516`; `POP@8828dee:packages/populace-build/src/populace/build/us/source_stages.json:2712-2748`)

The checked-in scalar inputs are SNAP 0.82, TANF 0.219, and the EITC child-bin probabilities. Ledger-fed compiled count specifications drive the dedicated SNAP-state, Medicaid, SSI-prior/weight-target, and ACA stages. Medicare, Head Start, and housing instead use measured or imputed source mappings rather than administrative-rate seeds. (`POP@8828dee:packages/populace-build/src/populace/build/us/take_up_contract.json:19-204`; `POP@8828dee:packages/populace-build/src/populace/build/us/source_stages.json:1357-1486,1950-2036,2400-2530,2680-2785`; `POP@8828dee:packages/populace-build/src/populace/build/us_runtime/medicaid_take_up.py:136-195`; `POP@8828dee:packages/populace-build/src/populace/build/us_runtime/ssi_take_up.py:482-511`)

Current WIC creates a contract drift: the current engine exposes 14 flags including WIC, but the current Populace contract enumerates 13 and omits WIC. Therefore a current build with exactly this 1.779.4 engine should fail the exact-set gate before release; whether/when Populace will add WIC is **UNKNOWN**. (`EVIDENCE:evidence/engine_take_up_probe.txt:8-23`; `POP@8828dee:packages/populace-build/src/populace/build/us/take_up_contract.json:19-204`; `POP@8828dee:packages/populace-build/src/populace/build/us_runtime/take_up_contract.py:284-348`)

### C.2 Release gate and diagnostics

The adapter discovers engine variables whose names begin with `takes_up` (or the seed-name patterns). The contract gate validates entry structure/provenance; asserts exact equality of engine-discovered and contract-declared flag sets; compares entity, value type, default, and engine class; and rejects logically inconsistent engine-class/treatment pairs. It does **not** generally prove that every dedicated stage emitted a nondefault column. Preflight invokes the contract gate, and tests cover missing, extra, metadata-drift, and treatment-inconsistency cases. (`POP@8828dee:packages/populace-frame/src/populace/frame/adapters/policyengine_us.py:246-263`; `POP@8828dee:packages/populace-build/src/populace/build/us_runtime/take_up_contract.py:123-267,284-397`; `POP@8828dee:tools/build_us_fiscal_refresh_release.py:7490-7500`; `POP@8828dee:packages/populace-build/tests/test_us_take_up_contract.py:30-35,120-137,166-222`)

`us_take_up_participation.json` includes one metadata row per **contract entry**. Materialized generic `seed` rows carry the **weighted** flag-true count, weighted all-entity universe, weighted share, and administrative rate; materialized `count_calibrated` rows carry the same weighted all-entity share, explicitly including off-domain propensities. Other rows principally record treatment/default status and follow-up. For an `out_of_scope` row, the generic diagnostic sets `ships_at_engine_default = false` from the treatment label without inspecting the live column, so it is not proof that the dedicated stage ran. Eligibility-restricted surfaces live in dedicated artifacts, so these generic shares are not automatically recipient/eligible “effective take-up” rates. (`POP@8828dee:packages/populace-build/src/populace/build/us_runtime/take_up.py:481-598`)

The release writer persists dedicated Medicaid and SNAP-state artifacts, notes that SSI was written earlier, and separately rejects a count-calibrated flag that reaches export at engine default. Medicaid's final-weight diagnostics contain national/state enrollment-to-eligibility ratios; SSI's delivered artifact is release-final; SNAP-state diagnostics explicitly use pre-calibration design weights and are not final-weight effective-rate results. (`POP@8828dee:tools/build_us_fiscal_refresh_release.py:3073-3112,9366-9402,10155-10203`; `POP@8828dee:packages/populace-build/src/populace/build/us_runtime/medicaid_take_up.py:343-441`; `POP@8828dee:packages/populace-build/src/populace/build/us_runtime/ssi_take_up.py:1185-1194,1351-1356`; `POP@8828dee:packages/populace-build/src/populace/build/us_runtime/snap_state_take_up.py:320-400`)

## D. Calibration targets touching programs

### D.0 Do not substitute the managed bundle

The separately installed `policyengine.py` 4.18.8 bundle points to a July 1 `sparse-l0...` build made with PolicyEngine US 1.752.2, not the June 19 artifact pinned by the audited engine. Its diagnostics therefore are not used to report June achieved errors. (`BUNDLE:2-7,99-184,225-231`; `EVIDENCE:evidence/source_identity.txt:18-25`)

### D.1 Current `origin/main` target surface

Ledger-backed rows generally keep the Ledger source-record ID and gain `@period` when materialized; derived CHIP names are synthesized by replacing `total_medicaid_chip_enrollment` with `total_chip_enrollment`. The active registry maps SOI counts/amounts, SSA/USDA/HHS dollar facts, and enrollment indicators into calibration expressions; the builder compiles that registry and passes the resulting surface to the solver. (`POP@8828dee:packages/populace-calibrate/src/populace/calibrate/target.py:126-138`; `POP@8828dee:packages/populace-build/src/populace/build/us_runtime/fiscal_targets.py:115-150,201-233,416-550,1124-1133`; `POP@8828dee:tools/build_us_fiscal_refresh_release.py:4010-4034,7531-7566,9291-9305`)

| Program | Current target surface | Exact representative surface names | Evidence / Ledger family |
|---|---|---|---|
| SNAP | Benefit dollars, national/state; average-monthly participating-household counts, national/state. Person counts are deliberately excluded. | `usda_snap.fy2024.national_benefits.national_total.total_benefits@2024`; `usda_snap.fy2024.state_benefits.wro.ca.total_benefits@2024`; `usda_snap.fy2024.national_average_monthly_households.national_total.average_monthly_households@2024`; `usda_snap.fy2024.state_average_monthly_households.nero.ny.average_monthly_households@2024` | `POP@8828dee:packages/populace-build/tests/test_us_fiscal_targets.py:769-809,1155-1228`; `POP@8828dee:packages/populace-build/src/populace/build/us/target_parity_feed_families.json:80-85` |
| SSI | National/state payment dollars; state recipient counts; national recipient counts by under-18, 18–64, and 65+ age bands. The all-age row is excluded. | `ssa_supplement.cy2024.oasdi_ssi_payments.ssi_payments.payment_amount@2024`; `ssa_supplement.cy2024.ssi_payments.by_area_category.alabama_total.payment_amount@2024`; `ssa_supplement.cy2024.ssi_recipients.by_area_category.alabama_total.recipient_count@2024`; `ssa_ssi_monthly.month2024_12.ssi_federal_payment_recipients.by_age.under_18.recipient_count@2024` | `POP@8828dee:packages/populace-build/tests/test_us_fiscal_targets.py:1313-1465,1559-1639,4344-4412`; `POP@8828dee:packages/populace-build/src/populace/build/us/target_parity_feed_families.json:76-79` |
| TANF cash | Cash-assistance dollars, national/available states. Family and recipient caseload counts are reviewed exclusions because no receipt indicator is wired. | `hhs_acf_tanf.fy2024.cash_assistance.us.basic_assistance_excluding_relative_foster_care_and_adoption_guardianship.all_funds@2024`; `hhs_acf_tanf.fy2024.cash_assistance.ca.basic_assistance_excluding_relative_foster_care_and_adoption_guardianship.all_funds@2024` | `POP@8828dee:packages/populace-build/tests/test_us_fiscal_targets.py:617-663`; `POP@8828dee:packages/populace-build/src/populace/build/us/target_parity_manifest.json:488-511`; `POP@8828dee:packages/populace-build/src/populace/build/us/target_parity_feed_families.json:55-57` |
| WIC | No current target; this is a **known reviewed exclusion** because the pinned feed has no WIC fact. | No surface name | `POP@8828dee:packages/populace-build/src/populace/build/us/target_parity_manifest.json:680-689` |
| EITC | SOI claim counts and dollars, national/state, plus child-count/AGI decompositions where compiled. | `irs_soi.ty2024.filing_season_week47.eitc_all_returns.earned_income_credit.total_earned_income_credit_returns@2024`; `irs_soi.ty2024.filing_season_week47.eitc_all_returns.earned_income_credit.total_earned_income_credit_amount@2024`; `irs_soi.ty2024.table_2_5.eitc_by_agi_children.no_qualifying_children.25k_to_30k.eitc_total@2024`; `irs_soi.ty2024.state_2022.us.eitc_three_or_more_children_returns.three_or_more_qualifying_children.return_count@2024` | `POP@8828dee:packages/populace-build/src/populace/build/us_runtime/fiscal_targets.py:115-150,201-233`; `POP@8828dee:packages/populace-build/tests/test_us_fiscal_targets.py:2281-2390,4175-4210`; `POP@8828dee:packages/populace-build/src/populace/build/us/target_parity_feed_families.json:58-70` |
| CTC / refundable CTC (ACTC) | SOI claim counts and dollars, national/state. | `irs_soi.ty2022.historic_table_2.us.all.ctc_claims@2024`; `irs_soi.ty2022.historic_table_2.us.all.ctc_amount@2024`; `irs_soi.ty2022.historic_table_2.us.all.actc_claims@2024`; `irs_soi.ty2022.historic_table_2.us.all.actc_amount@2024` | `POP@8828dee:packages/populace-build/src/populace/build/us_runtime/fiscal_targets.py:115-150,201-233`; `POP@8828dee:packages/populace-build/tests/test_us_fiscal_targets.py:2235-2278`; `POP@8828dee:packages/populace-build/src/populace/build/us/target_parity_feed_families.json:58-70` |
| Medicaid | Enrollment counts, national/state. Spending is validation-only, not a calibration row. | `cms_medicaid.month2024_12.state_enrollment.us.total_medicaid_enrollment@2024`; `cms_medicaid.month2024_12.state_enrollment.tx.total_medicaid_enrollment@2024` | `POP@8828dee:packages/populace-build/src/populace/build/us_runtime/fiscal_targets.py:431-443,468-517`; `POP@8828dee:packages/populace-build/src/populace/build/us/take_up_contract.json:73-78`; `POP@8828dee:packages/populace-build/tests/test_us_fiscal_targets.py:812-830,966-1152`; `POP@8828dee:packages/populace-build/src/populace/build/us/target_parity_feed_families.json:47-48` |
| CHIP | Standalone and combined Medicaid+CHIP enrollment counts, including derived combined-minus-Medicaid targets where suitable. | `cms_medicaid.month2024_12.state_enrollment.us.total_chip_enrollment@2024`; `cms_medicaid.month2024_12.state_enrollment.us.total_medicaid_chip_enrollment@2024` | `POP@8828dee:packages/populace-build/src/populace/build/us_runtime/fiscal_targets.py:498-517,1036-1165`; `POP@8828dee:packages/populace-build/tests/test_us_fiscal_targets.py:966-1152`; `POP@8828dee:packages/populace-build/src/populace/build/us/target_parity_feed_families.json:47-48` |
| ACA / PTC | Marketplace, APTC-recipient, and bronze-plan counts; SOI PTC-return counts and PTC dollars. Marketplace counts use interview coverage; APTC-recipient/PTC-return rows use computed `assigned_aca_ptc` expressions. | `cms_aca.oep2024.state_marketplace.ca.marketplace_enrollment@2024`; `cms_aca.oep2024.state_marketplace.ca.aptc_recipients@2024`; `cms_aca.oep2024.state_metal.ca.bronze_aptc_consumers@2024`; `irs_soi.ty2022.historic_table_2.us.all.premium_tax_credit_returns@2024`; `irs_soi.ty2022.historic_table_2.us.all.premium_tax_credit_amount@2024` | `POP@8828dee:packages/populace-build/src/populace/build/us_runtime/fiscal_targets.py:468-497`; `POP@8828dee:packages/populace-build/tests/test_us_fiscal_targets.py:2079-2232`; `POP@8828dee:packages/populace-build/src/populace/build/us/target_parity_feed_families.json:47-48,58-70` |
| Housing | No current target; this is a **known reviewed exclusion** because the pinned feed has no HUD fact. | No surface name | `POP@8828dee:packages/populace-build/src/populace/build/us/target_parity_manifest.json:513-521` |
| LIHEAP | National recipient-household count through an indicator on `spm_unit_energy_subsidy`; dollars are deferred. | `hhs_acf_liheap.fy2024.national_profile.state_programs.households_served@2024` | `POP@8828dee:packages/populace-build/src/populace/build/us_runtime/fiscal_targets.py:540-550`; `POP@8828dee:packages/populace-build/tests/test_us_fiscal_targets.py:1779-1804`; `POP@8828dee:packages/populace-build/src/populace/build/us/target_parity_feed_families.json:54` |

The source-family manifest identifies CMS ACA/Medicaid, HHS ACF LIHEAP/TANF, IRS SOI, SSA, and USDA SNAP Ledger packages; those are the administrative fact families behind the mappings above. (`POP@8828dee:packages/populace-build/src/populace/build/us/target_parity_feed_families.json:47-85`; `POP@8828dee:packages/populace-build/src/populace/build/us/target_parity_manifest.json:440-522,634-689`)

### D.2 Exact June artifact: cached diagnostics and achieved errors

The exact `calibration_diagnostics.json` is cached and hash-verified. It records 4,408 targets, 75,112 household-weight records, final objective loss 0.0432632, and 88.1806% of targets within 10% relative error. Its `post_export_target_audit` field is `false`; the achieved errors below are the serialized solver/target-frame diagnostics, not an independent recomputation from the shipped HDF5. (`EVIDENCE:evidence/pinned_diagnostics_summary.txt:1-10,95`; `CACHE:release_manifest.json:49-54`; `CACHE:calibration_diagnostics.json:290222`)

Family-wide results expose state misses that a national-only table would hide. Ranges below are minimum-to-maximum relative errors across **nonzero** targets. (`EVIDENCE:evidence/pinned_diagnostics_summary.txt:12-57`)

| Pinned target family | Targets (nonzero) | Nonzero targets within ±10% | Achieved relative-error range |
|---|---:|---:|---:|
| ACA marketplace enrollment | 51 (51) | 49 / 51 | −30.8338% to +110.1490% |
| ACA APTC recipients | 51 (51) | 48 / 51 | −30.5057% to +1.1418% |
| Medicaid + CHIP enrollment | 52 (51) | 50 / 51 | −10.0787% to +5.5024% |
| Medicaid enrollment | 52 (51) | 45 / 51 | −11.5837% to +13.5795% |
| TANF dollars | 30 (30) | 19 / 30 | −93.6451% to +1,765.9163% |
| ACA PTC returns and dollars | 104 (104) | 92 / 104 | −1.9873% to +202.3581% |
| EITC | 521 (521) | 475 / 521 | −45.2455% to +50.4996% |
| CTC | 104 (104) | 86 / 104 | −22.8831% to +22.8163% |
| Refundable CTC / ACTC | 104 (104) | 100 / 104 | −13.0873% to +26.6293% |
| SSI dollars | 1 (1) | 1 / 1 | −0.024182% |
| SNAP dollars | 52 (52) | 47 / 52 | −6.4077% to +61.7776% |

Source for every family row: `EVIDENCE:evidence/pinned_diagnostics_summary.txt:12-57`. The two excluded zero targets are Rhode Island Medicaid and Medicaid+CHIP: each target is 0 and each final estimate is 239,443.018. An ordinary percentage error is undefined for a zero denominator, so the JSON's numeric `relative_error` field for these two rows must not be interpreted as a fractional percentage. (`EVIDENCE:evidence/pinned_diagnostics_summary.txt:20-29`)

The table reports national program targets exactly as serialized. Relative error is `(final_estimate / target) - 1`; it is not an error in an effective take-up ratio. (`CACHE:calibration_diagnostics.json:12-28`; `EVIDENCE:evidence/pinned_diagnostics_summary.txt:59-80`)

| Exact target name | Unit | Achieved relative error |
|---|---:|---:|
| `cms_medicaid.month2024_12.state_enrollment.us.total_medicaid_chip_enrollment@2024` | count | −0.996513% |
| `cms_medicaid.month2024_12.state_enrollment.us.total_medicaid_enrollment@2024` | count | +2.183543% |
| `hhs_acf_tanf.fy2024.cash_assistance.us.basic_assistance_excluding_relative_foster_care_and_adoption_guardianship.all_funds@2024` | USD | +0.241683% |
| `irs_soi.ty2022.historic_table_2.us.all.premium_tax_credit_returns@2024` | count | +7.856794% |
| `irs_soi.ty2022.historic_table_2.us.all.premium_tax_credit_amount@2024` | USD | +6.697868% |
| `irs_soi.ty2022.historic_table_2.us.all.eitc_claims@2024` | count | −0.005483% |
| `irs_soi.ty2022.historic_table_2.us.all.eitc_amount@2024` | USD | +0.950000% |
| `irs_soi.ty2022.historic_table_2.us.all.ctc_claims@2024` | count | −3.848545% |
| `irs_soi.ty2022.historic_table_2.us.all.ctc_amount@2024` | USD | +3.930812% |
| `irs_soi.ty2022.historic_table_2.us.all.actc_claims@2024` | count | −0.674172% |
| `irs_soi.ty2022.historic_table_2.us.all.actc_amount@2024` | USD | +0.029654% |
| `ssa_supplement.cy2024.oasdi_ssi_payments.ssi_payments.payment_amount@2024` | USD | −0.024182% |
| `usda_snap.fy2024.national_benefits.national_total.total_benefits@2024` | USD | +0.041282% |

Source for every row: `EVIDENCE:evidence/pinned_diagnostics_summary.txt:59-80`.

The additional national EITC decomposition rows achieved the following errors. (`EVIDENCE:evidence/pinned_diagnostics_summary.txt:66-74`)

| Exact target name | Unit | Achieved relative error |
|---|---:|---:|
| `irs_soi.ty2024.state_2022.us.eitc_three_or_more_children_returns.three_or_more_qualifying_children.return_count@2024` | count | −0.319464% |
| `irs_soi.ty2022.table_2_5.eitc_by_agi_children.no_qualifying_children.total.eitc_returns@2024` | count | −2.282344% |
| `irs_soi.ty2022.table_2_5.eitc_by_agi_children.no_qualifying_children.total.eitc_total@2024` | USD | −0.762718% |
| `irs_soi.ty2022.table_2_5.eitc_by_agi_children.one_qualifying_child.total.eitc_returns@2024` | count | −1.099936% |
| `irs_soi.ty2022.table_2_5.eitc_by_agi_children.one_qualifying_child.total.eitc_total@2024` | USD | −0.336155% |
| `irs_soi.ty2022.table_2_5.eitc_by_agi_children.two_qualifying_children.total.eitc_returns@2024` | count | −2.248162% |
| `irs_soi.ty2022.table_2_5.eitc_by_agi_children.two_qualifying_children.total.eitc_total@2024` | USD | −0.919128% |
| `irs_soi.ty2022.table_2_5.eitc_by_agi_children.three_or_more_qualifying_children.total.eitc_returns@2024` | count | −0.600422% |
| `irs_soi.ty2022.table_2_5.eitc_by_agi_children.three_or_more_qualifying_children.total.eitc_total@2024` | USD | −0.043360% |

Source for every EITC decomposition row: `EVIDENCE:evidence/pinned_diagnostics_summary.txt:66-74`.

The pinned surface comprises 51 state marketplace-enrollment counts, 51 state APTC-recipient counts, 52 Medicaid+CHIP counts, 52 Medicaid counts, 30 TANF dollar targets, 104 PTC targets (52 count/52 dollars), 521 EITC targets (261 count/260 dollars), 104 CTC targets, 104 ACTC targets, one SSI dollar target, and 52 SNAP dollar targets. (`EVIDENCE:evidence/pinned_diagnostics_summary.txt:12-57`)

No pinned target name/semantic role matches WIC, housing/HUD, school meals, Head Start, Early Head Start, BHP, LIHEAP, child care/CCDF, SNAP participation counts, TANF caseload counts, SSI recipient counts, Medicaid dollars, or standalone CHIP enrollment. (`EVIDENCE:evidence/pinned_diagnostics_summary.txt:81-94`)

### D.3 Counts versus dollars

Calibration does target participation **counts**; it is not dollars-only. In the pinned release the count targets touch ACA marketplace/APTC participation, PTC-return counts, EITC/CTC/ACTC claims, Medicaid enrollment, and combined Medicaid+CHIP enrollment. SNAP, TANF, and SSI have dollars only in that release, while WIC and housing have neither. (`EVIDENCE:evidence/pinned_diagnostics_summary.txt:12-94`)

A count target approximately constrains the weighted numerator represented by its particular materialized expression. It does not independently constrain the weighted eligible denominator, does not set record-level flags, and—because the optimization is soft—does not guarantee the count exactly. The target/matrix code materializes per-record vectors and the solver changes weights; it does not mutate program inputs. This distinction is required before describing a calibration target as “pinning take-up.” (`CACHE:calibration_diagnostics.json:12-49`; `POP@8828dee:packages/populace-calibrate/src/populace/calibrate/target.py:1-18,37-65,187-229`; `POP@8828dee:packages/populace-calibrate/src/populace/calibrate/matrix.py:48-65,161-183`; `POP@8828dee:packages/populace-calibrate/src/populace/calibrate/solve.py:1306-1361`)

## E. Synthesis: how effective take-up emerges

An official PolicyEngine definition of “effective take-up rate” is **UNKNOWN**. This audit therefore distinguishes (i) the weighted **take-up-flag pass share among formula-eligible units** from (ii) the weighted **positive-benefit recipient share among formula-eligible units**. A missing/default-`True` or all-`True` flag proves a 100% flag-gate pass among eligibles; it does not always prove a 100% positive-benefit share because other conditions or zero-valued formulas can intervene. EITC separately applies a filer condition, and the 2024 BHP formula is zero. (`PEUS:variables/gov/irs/credits/earned_income/eitc.py:11-31`; `PEUS:variables/gov/hhs/basic_health_program/basic_health_program.py:4-12,25-49`; `EVIDENCE:evidence/engine_take_up_probe.txt:8-23`)

The causal chain is: (1) the dataset supplies a Boolean take-up input, or the engine supplies its `True` default; (2) eligibility, claim/filer, and benefit formulas apply that input; (3) calibration changes household weights to reduce aggregate count/dollar errors. Reweighting changes weighted composition but does not rewrite the stored flags. (`CORE:simulations/simulation.py:800-811,872-873`; `POP@8828dee:packages/populace-calibrate/src/populace/calibrate/matrix.py:48-65,161-183`; `EVIDENCE:evidence/pinned_artifact_probe.txt:24-56`)

Two version layers must remain separate. The stored inputs can be evaluated under current 1.779.4 formulas, but the cached B/C target results were generated by build-time 1.729.0. Whether a fresh 1.779.4 recalculation with the shipped weights still achieves those serialized errors is **UNKNOWN**; the cached diagnostics are not post-export audited. (`EVIDENCE:evidence/source_identity.txt:3-17`; `EVIDENCE:evidence/pinned_diagnostics_summary.txt:95`)

The requested labels below are nonexclusive: **(a)** direct data seeding; **(b)** a participation-count numerator approximately constrained by historical calibration; **(c)** a dollar aggregate constrained, which does **not** identify a take-up rate; **(d)** an all-eligible flag gate because the flag is absent/default `True`, stored all `True`, or no participation flag exists. Because the historical Populace source revision is absent, direct-seeding provenance for the two nontrivial stored flags is **UNKNOWN**, even though their stored surfaces are observable. (`EVIDENCE:evidence/source_identity.txt:11-17`; `EVIDENCE:evidence/pinned_artifact_probe.txt:24-56`)

| Program | Pinned-artifact classification | Defensive interpretation |
|---|---|---|
| SNAP | (c) + (d); (a) UNKNOWN | Stored flag is all `True`; cached calibration has benefit dollars only, so no participation count or effective rate is targeted. (`EVIDENCE:evidence/pinned_artifact_probe.txt:31-32`; `EVIDENCE:evidence/pinned_diagnostics_summary.txt:54-57,80,90`) |
| SSI | (c) + (d); (a) UNKNOWN | Stored flag is all `True`; only national payment dollars are targeted, not recipient counts. (`EVIDENCE:evidence/pinned_artifact_probe.txt:28-29`; `EVIDENCE:evidence/pinned_diagnostics_summary.txt:50-53,79,92`) |
| TANF cash | (c) + (d); (a) UNKNOWN | Stored flag is all `True`; 30 cash-dollar targets exist, but no caseload count. (`EVIDENCE:evidence/pinned_artifact_probe.txt:32-33`; `EVIDENCE:evidence/pinned_diagnostics_summary.txt:30-33,61,91`) |
| WIC | (d); (a) UNKNOWN | Build-time 1.729.0 read stored `would_claim_wic`, which is all `True`; current 1.779.4 reads the missing/default-`True` renamed flag. Neither `receives_wic` nor a WIC calibration target controls the benefit gate. (`EVIDENCE:evidence/pinned_artifact_probe.txt:37-41,54`; `EVIDENCE:evidence/pinned_diagnostics_summary.txt:82`; `PEUS729:policyengine_us/variables/gov/usda/wic/wic.py:18-31`; `PEUS:variables/gov/usda/wic/wic.py:4-19`) |
| EITC | (b) + (c) + (d); (a) UNKNOWN | Stored flag is all `True`; claim counts and dollars are targeted. Counts constrain positive claims, but they neither create a sub-100% flag gate nor identify the eligible denominator; the separate filer condition can still yield zero. (`EVIDENCE:evidence/pinned_artifact_probe.txt:35-36`; `EVIDENCE:evidence/pinned_diagnostics_summary.txt:38-41,64-74`; `PEUS:variables/gov/irs/credits/earned_income/eitc.py:11-31`) |
| Refundable CTC / ACTC | (b) + (c) + (d) | No take-up flag exists; claim counts and dollars are targeted, while formula rules determine positive credit. (`PEUS:variables/gov/irs/credits/ctc/refundable/refundable_ctc.py:4-38`; `EVIDENCE:evidence/pinned_diagnostics_summary.txt:46-49,77-78`) |
| Medicaid | (b) + (d); (a) UNKNOWN | Stored flag is all `True`; Medicaid enrollment counts are targeted. That establishes an all-eligible flag gate, not an exact positive-benefit recipient/eligible rate. There is no pinned Medicaid dollar calibration target. (`EVIDENCE:evidence/pinned_artifact_probe.txt:26-27`; `EVIDENCE:evidence/pinned_diagnostics_summary.txt:20-29,59,93`; `PEUS:variables/gov/hhs/medicaid/costs/medicaid_cost_if_enrolled.py:4-22`) |
| CHIP | indirect (b) + (d); (a) UNKNOWN | Current flag is absent/default `True`; the historical surface has combined Medicaid+CHIP counts but no standalone CHIP target, so CHIP is only indirectly present in a combined numerator. (`EVIDENCE:evidence/pinned_artifact_probe.txt:51-56`; `EVIDENCE:evidence/pinned_diagnostics_summary.txt:20-24,59,94`) |
| ACA PTC | stored nontrivial surface; (a) provenance UNKNOWN; (b) + (c) | The stored tax-unit flag is true on 13.3491% of **all** tax-unit rows. Marketplace coverage counts target a different reported-coverage expression; APTC-recipient/PTC-return counts and PTC dollars touch computed PTC. The historical algorithm producing the flag is UNKNOWN. (`EVIDENCE:evidence/pinned_artifact_probe.txt:33-34`; `EVIDENCE:evidence/pinned_diagnostics_summary.txt:12-19,34-37,62-63`; `EVIDENCE:evidence/source_identity.txt:11-17`) |
| Housing assistance | stored nontrivial surface; (a) provenance UNKNOWN | The flag is true on 18.7569% of **all** SPM-unit rows, but there is no housing target. The historical algorithm producing it is UNKNOWN. (`EVIDENCE:evidence/pinned_artifact_probe.txt:29-30`; `EVIDENCE:evidence/pinned_diagnostics_summary.txt:83`; `EVIDENCE:evidence/source_identity.txt:11-17`) |
| Free/reduced school meals | (d) | No take-up flag or pinned target; tier/K–12 assumptions determine modeled benefit. (`EVIDENCE:evidence/engine_take_up_probe.txt:8-23`; `EVIDENCE:evidence/pinned_diagnostics_summary.txt:84`; `PEUS:variables/gov/usda/school_meals/school_meal_tier.py:4-38`) |
| Head Start | (d); (a) UNKNOWN | Stored flag is all `True` and no target exists; every formula-eligible person passes the take-up flag gate. (`EVIDENCE:evidence/pinned_artifact_probe.txt:25-26`; `EVIDENCE:evidence/pinned_diagnostics_summary.txt:85`) |
| Early Head Start | (d); (a) UNKNOWN | Stored flag is all `True` and no target exists; every formula-eligible person passes the take-up flag gate. (`EVIDENCE:evidence/pinned_artifact_probe.txt:24-25`; `EVIDENCE:evidence/pinned_diagnostics_summary.txt:86`) |
| Basic Health Program | (d); (a) UNKNOWN | Current flag is absent/default `True`, no target exists, and the 2024 benefit formula is zero; flag-gate pass and positive-benefit receipt therefore sharply differ. (`EVIDENCE:evidence/pinned_artifact_probe.txt:51-56`; `EVIDENCE:evidence/pinned_diagnostics_summary.txt:87`; `PEUS:variables/gov/hhs/basic_health_program/basic_health_program.py:4-12,25-49`) |

Current `origin/main` is materially different: it materializes nondefault take-up input surfaces for SNAP, TANF, EITC, Medicaid, Medicare, SSI, Head Start, housing, and ACA through a mix of hash draws, count-derived stages, measured mappings, and donor/imputation stages. Current calibration also adds SNAP household counts and SSI recipient counts and supports standalone CHIP counts. These are current-pipeline mechanics, not proof of the pinned June build's history. (`POP@8828dee:packages/populace-build/src/populace/build/us/take_up_contract.json:19-204`; `POP@8828dee:packages/populace-build/tests/test_us_fiscal_targets.py:1155-1228,1313-1465`; `POP@8828dee:packages/populace-build/src/populace/build/us_runtime/fiscal_targets.py:1036-1165`)

The safe external description is therefore: **PolicyEngine effective take-up is an emergent property of microdata take-up inputs, formula eligibility/claim rules, and calibrated household weights. Some aggregate recipient counts are calibration targets, but calibration neither supplies missing flags nor, by itself, identifies an exact recipient/eligible take-up rate.** (`EVIDENCE:evidence/pinned_artifact_probe.txt:24-56`; `CACHE:calibration_diagnostics.json:3-49`; `POP@8828dee:packages/populace-calibrate/src/populace/calibrate/matrix.py:48-65,161-183`)

## Appendix 1. Full stored-column inventory

The names below preserve HDF5 file order exactly. (`EVIDENCE:evidence/pinned_artifact_probe.txt:57-386`)

### `family` — 79365 rows, 2 columns

```text
family_id
family_is_puf_clone
```

### `household` — 75112 rows, 44 columns

```text
household_id
state_fips
cbsa
household_type
household_income_bracket
household_total_income
GTCO
H_TENURE
tenure_type
block_geoid
county_fips
congressional_district_geoid
tract_geoid
household_is_puf_clone
scf_net_worth
auto_loan_balance
auto_loan_interest
scf_bank_account_assets
scf_stock_assets
scf_bond_assets
scf_household_vehicles_value
scf_certificates_of_deposit
scf_savings_bonds
scf_retirement_assets
scf_cash_value_life_insurance
scf_other_managed_assets
scf_other_financial_assets
scf_primary_residence_value
scf_other_residential_real_estate
scf_nonresidential_real_estate_equity
scf_business_equity
scf_other_nonfinancial_assets
scf_mortgage_debt
scf_other_residential_debt
scf_other_lines_of_credit
scf_credit_card_debt
scf_vehicle_installment_debt
scf_student_loan_debt
scf_other_installment_debt
scf_other_debt
net_worth
household_vehicles_owned
household_vehicles_value
household_weight
```

### `marital_unit` — 124087 rows, 1 columns

```text
marital_unit_id
```

### `person` — 160858 rows, 249 columns

```text
age
sex
hispanic
education
class_of_worker
work_status
hours_worked
employment_income
self_employment_income
taxable_interest_income
dividend_income
rental_income
social_security
taxable_pension_income
unemployment_compensation
total_person_income
public_assistance
has_medicare
has_medicaid
person_number
family_relationship
marital_status
weight
march_supplement_weight
A_AGE
A_EXPRRP
A_FTPT
A_HRS1
A_HSCOL
A_LINENO
A_MARITL
A_SPOUSE
CHSP_VAL
CSP_VAL
DIS_SC1
DIS_SC2
DIS_VAL1
DIS_VAL2
DST_SC1
DST_SC1_YNG
DST_SC2
DST_SC2_YNG
DST_VAL1
DST_VAL1_YNG
DST_VAL2
DST_VAL2_YNG
ED_VAL
FIN_VAL
LKWEEKS
NOW_CAID
NOW_CHAMPVA
NOW_GRP
NOW_GRPFTYP
NOW_HIPAID
NOW_IHSFLG
NOW_MIL
NOW_MRK
NOW_NONM
NOW_OTHMT
NOW_OWNGRP
NOW_VACARE
OI_OFF
OI_VAL
PEDISDRS
PEDISEAR
PEDISEYE
PEDISOUT
PEDISPHY
PEDISREM
PEIOOCC
PEPAR1
PEPAR2
PERIDNUM
PF_SEQ
PHIP_VAL
PH_SEQ
PMED_VAL
POCCU2
POTC_VAL
P_SEQ
RESNSS1
RESNSS2
RETCB_VAL
SEMP_VAL
SPM_CAPHOUSESUB
SPM_CAPWKCCXPNS
SPM_CHILDCAREXPNS
SPM_ENGVAL
SPM_ID
SRVS_VAL
VET_VAL
WC_VAL
WICYN
WKSWORK
WSAL_VAL
person_tax_unit_id
tax_unit_role_input
is_related_to_head_or_spouse
person_spm_unit_id
person_family_id
person_marital_unit_id
_half
new_tax_unit_id
alimony_expense
alimony_income
business_is_sstb
non_sch_d_capital_gains
casualty_loss
charitable_cash_donations
charitable_non_cash_donations
educator_expense
estate_income
farm_income
farm_rent_income
investment_income_elected_form_4952
taxable_ira_distributions
long_term_capital_gains
long_term_capital_gains_on_collectibles
non_qualified_dividend_income
partnership_se_income
miscellaneous_income
qualified_bdc_income
qualified_dividend_income
qualified_reit_and_ptp_income
qualified_tuition_expenses
real_estate_taxes
salt_refund_income
short_term_capital_gains
sstb_self_employment_income_before_lsr
sstb_self_employment_income_would_be_qualified
sstb_unadjusted_basis_qualified_property
sstb_w2_wages_from_qualified_business
student_loan_interest
tax_exempt_interest_income
unadjusted_basis_qualified_property
unreimbursed_business_employee_expenses
w2_wages_from_qualified_business
tax_exempt_pension_income
child_support_received
child_support_expense
disability_benefits
has_esi
has_marketplace_health_coverage
receives_wic
health_insurance_premiums_without_medicare_part_b
over_the_counter_health_expenses
other_medical_expenses
is_disabled
cps_race
is_female
is_hispanic
is_household_head
is_separated
is_unmarried_partner_of_household_head
own_children_in_household
count_under_18
count_under_6
social_security_retirement
social_security_disability
social_security_survivors
social_security_dependents
educational_assistance
financial_assistance
survivor_benefits
veterans_benefits
workers_compensation
hours_worked_last_week
weeks_worked
detailed_occupation_recode
weeks_unemployed
is_blind
is_surviving_spouse
is_full_time_college_student
has_marketplace_health_coverage_at_interview
has_non_marketplace_direct_purchase_health_coverage_at_interview
has_medicaid_health_coverage_at_interview
has_other_means_tested_health_coverage_at_interview
has_tricare_health_coverage_at_interview
has_champva_health_coverage_at_interview
has_va_health_coverage_at_interview
has_indian_health_service_coverage_at_interview
has_never_worked
is_military
is_computer_scientist
is_farmer_fisher
is_executive_administrative_professional
self_employed_pension_contributions_desired
traditional_401k_contributions_desired
roth_401k_contributions_desired
traditional_ira_contributions_desired
roth_ira_contributions_desired
treasury_tipped_occupation_code
is_tipped_occupation
keogh_distributions
tax_exempt_ira_distributions
taxable_401k_distributions
taxable_403b_distributions
taxable_sep_distributions
employment_income_before_lsr
self_employment_income_before_lsr
long_term_capital_gains_before_response
farm_operations_income
taxable_private_pension_income
tax_exempt_private_pension_income
_orig_household_id
person_household_id
person_id
person_is_puf_clone
bank_account_assets
stock_assets
bond_assets
tip_income
hourly_wage
is_paid_hourly
is_union_member_or_covered
fsla_overtime_premium
employer_sponsored_insurance_premiums
self_employment_income_last_year
previous_year_income_available
home_mortgage_interest
investment_interest_expense
pre_subsidy_rent
is_pursuing_credential_for_american_opportunity_credit
attends_eligible_educational_institution_for_american_opportunity_credit
is_enrolled_at_least_half_time_for_american_opportunity_credit
has_american_opportunity_credit_1098_t_or_exception
has_american_opportunity_credit_institution_ein
estate_income_would_be_qualified
farm_operations_income_would_be_qualified
farm_rent_income_would_be_qualified
has_valid_ssn
immigration_status_str
is_wic_at_nutritional_risk
partnership_s_corp_income_would_be_qualified
rental_income_would_be_qualified
self_employment_income_would_be_qualified
ssn_card_type
takes_up_early_head_start_if_eligible
takes_up_head_start_if_eligible
takes_up_medicaid_if_eligible
takes_up_medicare_if_eligible
takes_up_ssi_if_eligible
taxpayer_id_type
weekly_hours_worked_before_lsr
would_claim_wic
other_health_insurance_premiums
is_pregnant
partnership_income
s_corp_income
```

### `spm_unit` — 76665 rows, 9 columns

```text
spm_unit_id
spm_unit_is_puf_clone
spm_unit_pre_subsidy_childcare_expenses
spm_unit_energy_subsidy
receives_housing_assistance
spm_unit_tenure_type
takes_up_housing_assistance_if_eligible
takes_up_snap_if_eligible
takes_up_tanf_if_eligible
```

### `tax_unit` — 87519 rows, 18 columns

```text
tax_unit_id
filing_status_input
tax_unit_is_puf_clone
domestic_production_ald
health_savings_account_ald
self_employed_pension_contribution_ald
unrecaptured_section_1250_gain
second_home_mortgage_balance
second_home_mortgage_origination_year
first_home_mortgage_balance
first_home_mortgage_origination_year
second_home_mortgage_interest
first_home_mortgage_interest
selected_marketplace_plan_benchmark_ratio
takes_up_aca_if_eligible
takes_up_dc_ptc
takes_up_eitc
would_file_taxes_voluntarily
```
