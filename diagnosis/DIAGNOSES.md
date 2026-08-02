# Divergence diagnoses: Urban SotSN and PolicyEngine Build P

## Executive conclusion

PolicyEngine maintainers should address housing first, then TANF, SNAP state saturation, SSI age composition, and child SPM poverty. These are not disagreements that can be dismissed as different model vintages:

1. Housing is entirely held out and combines an approximate 22% denominator-concept contribution with a 78% PE receipt/HAP contribution to the 23.29-point participation-rate gap. PE pays positive HAP to only 0.69 million units and computes $5.57 billion, versus roughly 4.6 million assisted households and more than $50 billion administratively.
2. TANF eligibility is held out, its participation rate comes from a seed rather than a caseload target, and its consumed national cash target still misses by 36.1%. The absence of a recipient/enrollment input leaves several states on applicant rules even under forced take-up.
3. Alaska SNAP is a calibration-machinery finding. Build P hits the FY2024 FNS Alaska household target within 0.021%, then reports 99.998% of eligible people participating. Eighteen jurisdictions finish at or above 99.9% because household-targeted SPM-unit receipt is mapped to every person and current saturation diagnostics use pre-calibration weights.
4. SSI's held-out payable denominator is 20.7% below Urban, while consumed recipient controls mask an age-shape failure: PE is 85% below Urban at ages 60-64 and 55% above Urban at ages 18-24.
5. PE's 2024 child SPM poverty rate is 16.97%, 3.57 points above the same-year Census P60-287 benchmark of 13.4%. Total SPM poverty is only 0.70 point above Census, which makes this a child-specific held-out PE gap.

Urban's EITC eligible universe also merits clarification: 18.45 million is 22% below the 23.69 million SOI claims total and below the 23-26 million TY2016 NTA/Treasury eligible-universe range. Refundable CTC is not yet a same-concept disagreement: PE's 17.66 million count is claims-shaped by a consumed SOI target, while Urban reports modeled eligibility.

WIC is the strongest control result. It has zero calibration targets and independent recomputation support; PE's national eligibility is within 0.8% of Urban and participation within 2.1 percentage points. The national match hides a 435,000 infant shortfall offset by 357,000 more children ages 1-4, and its participation gate is seeded from separate FNS CY2022 category rates.

## Classification summary

| Queue | Finding | Primary class | Confidence | Calibration relationship |
| ---: | --- | --- | --- | --- |
| 1 | National SNAP person rate | `concept_mismatch` | High | Eligibility held out; rate indirectly consumed through household targets |
| 2 | TANF eligibility, rate, and cash | `pe_gap` | High | Eligibility held out; rate seeded; cash target consumed and missed |
| 3 | EITC eligible tax units | `external_model_issue` | Medium | Forced-positive denominator held out; baseline claims consumed |
| 4 | Refundable CTC eligible/claim count | `concept_mismatch` | High | Count consumed and claims-shaped |
| 5 | SSI payable adults | `pe_gap` | Medium | Payable denominator held out; recipient rate consumed |
| 6 | Housing participation | `pe_gap` (78% PE / 22% concept) | High | Fully held out; zero targets |
| 7 | Full-participation poverty | `concept_mismatch` | High | Fully held out; zero poverty targets |
| 8 | Baseline child SPM poverty | `pe_gap` | High | Held out; same-year Census benchmark available |
| 9 | Alaska SNAP saturation | `pe_gap` | High | Eligibility held out; household-caseload quantity consumed |
| 10 | WIC control | `concept_mismatch` | High | Fully held out from calibration; claim gate separately seeded |

Consumed-target agreement is not validation. Conversely, disagreement on a consumed quantity identifies the calibration surface, grain bridge, or release gate rather than the underlying eligibility formula alone. Seeded quantities test what the seed plus downstream model produces, not an independent take-up estimate. Held-out quantities provide the cleanest validation.

## Priority 1: repair housing receipt and HAP delivery

PE defines housing eligibility broadly: current receipt or a renter through 80% of area median income. Urban uses households at or below 50% of area median income. PE therefore reports 25.386 million eligible SPM units versus Urban's 16.781 million households. That is a real concept difference, but it does not explain most of the participation-rate gap.

Urban's published eligible count and gap imply 4.358 million participating households. PE stores receipt/take-up flags for 2.681 million eligible units, then computes positive housing assistance for only 0.689 million. In other words, 1.992 million flagged units, or 74.3%, receive zero HAP. PE computes $5.571 billion, at most about 11% of the documented $50 billion-plus administrative benchmark.

A symmetric Shapley decomposition of the 23.29-point rate gap assigns 5.10 points (21.9%) to the denominator difference and 18.16 points (78.1%) to receipt/HAP. This is an arithmetic decomposition, not a causal model, but it establishes priority: matching Urban's denominator would leave most of the divergence.

The first PE issue should:

- ingest a pinned HUD Picture of Subsidized Households national/state household-count extract;
- keep the household-to-SPM-unit bridge explicit and validate it before using it as a calibration target;
- add a sourced total-HAP or assisted-housing expenditure control;
- emit receipt-flag mass, positive-HAP mass, total HAP, and mean positive HAP; and
- locate whether payment standard, gross rent, tenant payment, or geography makes 74.3% of flagged units zero.

For scorecard comparison, add a separate household, at-or-below-50%-AMI denominator. Do not narrow the engine's broader eligibility variable simply to match Urban. Evidence: certified PE-US 1.764.6 `is_eligible_for_housing_assistance.py:69-88`, `housing_assistance.py:4-18`, `hud_hap.py:4-18`; Populace `housing_inputs.py:1-20,491-520,974-1131`; `docs/replication-assessment.md:85,113,124`.

## Priority 2: restore TANF recipient state and caseload validation

PE's 8.496 million payable-under-forced people are 2.902 million, or 25.5%, below Urban. Baseline positive-benefit persons divided by the forced denominator yields 40.8%, 22.3 points above Urban's 18.5%. Neither is a clean independent take-up comparison: the denominator is held out, and Build P seeds the flag from ASPE's 21.9% TRIM3 rate, the same model family as ATTIS.

The engine does enumerate all 51 state/DC cash programs, so a missing aggregator is not the answer. The sharper PE failure is that `is_tanf_enrolled` is an input-only Boolean and Build P does not thread an ASEC public-assistance receipt anchor. It therefore defaults false. State formulas including Texas, Indiana, and Delaware continue to apply applicant rather than recipient/continuation branches even when the scorecard forces take-up.

The state pattern confirms that this is not a uniform vintage difference. Twenty-three state PE totals are below half Urban; Delaware, Indiana, and Texas are below 1% of Urban, while New York is 2.36 times Urban. The national FY2024 ACF basic-assistance target is consumed, yet Build P produces $4.973 billion against $7.788 billion, a $2.815 billion or 36.1% miss. California contributes $2.484 billion, or 88.3%, of the net national shortfall.

The PE issue should thread a documented receipt/enrollment input, expose payable-under-forced eligibility directly, add ACF average-month family and recipient validations, and gate severe state support failures. It should investigate California's target support and the Delaware/Indiana/Texas applicant-path collapse separately. Evidence: certified `tanf.py:3-80`, `is_tanf_enrolled.py:4-9`; Populace `take_up_contract.json:30-45`; `tools/build_us_target_parity_manifest.py:469-507`; Build P `calibration_diagnostics.json`.

One mechanics-audit sentence is stale: `docs/mechanics-audit.md:46` describes `is_tanf_enrolled` as defaulting to `receives_tanf`, but certified 1.764.6 contains only the input declaration. The certified code and Populace's explicit statement that no PAW anchor is threaded govern this diagnosis.

## Priority 3: make SNAP state saturation a release failure

Alaska's official input is not suspicious. The FY2024 FNS target is 31,319.25 average-month households, and final calibration produces 31,325.745, an error of 6.495 households or 0.0207%. Yet the scorecard maps 107,163.924 participants onto 107,166.399 eligible people: 99.99769% participation and a gap of 2.476 people. Urban reports 34.2% and roughly 57,000 unserved people.

This divergence occurs on a quantity labeled `consumed_as_target`, so it is a calibration-machinery finding. Populace derives a fill rate as target divided by weighted eligible units, clips it at one, and treats target-at-or-above-eligible weight as accepted saturation. The SNAP stage diagnostic uses pre-calibration design weights; final weight calibration can change the effective rate. Fifteen jurisdictions finish at exactly 100%, and Alaska, South Dakota, and Texas bring the count at or above 99.9% to 18.

Populace should make unexplained saturation release-blocking, emit final-weight state eligibility and caseload diagnostics, and add Alaska plus systemic-saturation tests. The scorecard also needs a grain-compatible person validation: FNS targets households, while the current statistic counts every member of a targeted SPM unit. Evidence: Populace `snap_state_take_up.py:186-211,307-380`; `source_stages.json:1806`; `pipeline/compute_counterparts.py:300-306`; Build P `us_snap_state_take_up.json` and `calibration_diagnostics.json`.

## Priority 4: expose SSI age composition beneath pooled controls

The held-out PE payable denominator is 9.993 million adults versus Urban's 12.602 million, a 2.609 million or 20.7% shortfall. The aggregate hides opposing age errors:

| Adult age | PE payable | Urban payable | PE difference |
| --- | ---: | ---: | ---: |
| 18-24 | 1.335M | 0.861M | +55.0% |
| 25-59 | 3.783M | 4.526M | -16.4% |
| 60-64 | 0.162M | 1.083M | -85.0% |
| 65+ | 4.713M | 6.132M | -23.1% |

PE approximately meets consumed recipient counts when adults are pooled into 18-64 and 65+, but inferred recipients shift by about 0.66 million out of ages 60-64 and 0.46 million into ages 18-24. The SIPP disability classifier trains on 577 positives and 8,769 negatives, applies a measured-disability-signal gate, and passes a global share check rather than a fine-age check. State-supplement-only recipients total 114,977, only 4.4% of the eligibility gap, so state supplements cannot explain the national difference alone.

Add component diagnostics for disability/ABD, resources, income, and immigration in the four scorecard age bands. Keep eligibility held out; use a detailed-age SSA series first as validation rather than forcing eligibility toward receipt. Evidence: Populace `ssi_take_up.py:164-210`, `ssi_disability_criteria.py:1-29,143-158,924-1043,1167-1205`; certified `is_ssi_eligible.py:4-18`, `uncapped_ssi.py:4-16`, `ssi_amount_if_eligible.py:15-70`.

## Priority 5: diagnose child SPM resources against Census

PE's 2024 child SPM poverty rate is 16.9689%, versus 13.8% in Urban's 2023 output. The year difference does not carry the diagnosis: Census P60-287 reports 13.4% for children in 2024, so PE misses a same-year held-out benchmark by 3.5689 points, or 26.6%. PE's total SPM rate is 13.6042% versus Census's 12.9%, only 0.7042 point high. The excess is therefore concentrated among children rather than reflecting a general poverty-level shift.

Promote the existing national P60-287 total and child rows from passive backtests to explicit release diagnostics. Decompose market income, benefits, taxes, medical expenses, work/child-care expenses, unit composition, and thresholds by child status. Keep poverty held out initially: locate the resource or threshold error before fitting the outcome. Evidence: Populace `state_spm_poverty_levels.json:1-32`, `reform_validation.py:597-623`; `data/pe/pe_metrics.json`; certified `spm_unit_is_in_spm_poverty.py:10-13`, `spm_unit_net_income.py:11-18`.

The Early Head Start valuation defect is not a candidate explanation. The scorecard uses `spm_unit_is_in_spm_poverty`, whose net-income benefit list omits both Head Start variables. Its contribution here is exactly $0, zero people, and zero percentage points. The $112.3 billion remains a separate fiscal/model-output defect.

## Correct the full-participation comparison before interpreting headroom

PE all-flags and Urban do not force the same programs. PE all-flags includes ACA, Medicaid, Medicare, and Head Start; Urban covers nine safety-net programs including ACTC, LIHEAP, and CCDF. PE lacks comprehensive national LIHEAP/CCDF and has no distinct ACTC take-up flag.

The supplied static runs show the consequence:

| Population | Baseline | PE all-flags | Relative change | PE Urban-six | Relative change | Urban |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Total | 13.604% | 12.910% | -5.103% | 12.262% | -9.863% | -33.6% |
| Children | 16.969% | 15.540% | -8.420% | 14.578% | -14.091% | -43.6% |

Urban-six lifts 4.563 million people and 1.834 million children, 2.202 million and 0.738 million more than all-flags. It still falls 10.828 million people and 2.540 million children short of Urban. The nonmonotonicity has a static engine path: the extra all-flags health gates can add Marketplace, Medicaid, and Medicare premiums to SPM medical expenses, reducing SPM net resources. Exact attribution still requires marginal runs, which this audit did not perform.

Publish all-flags and Urban-six separately and label both as nonreplications. Build an exact nine-program surface only after the missing national programs and an ACTC claim gate exist. Evidence: `pipeline/compute_counterparts.py:48-66,453-477,489-493`; certified `spm_unit_spm_expenses.py:11-20`, `spm_unit_health_insurance_premiums.py:16-22`; `docs/replication-assessment.md:17-22,31-32,108-116`.

## Annotate the national SNAP rate instead of treating it as a model contest

PE's 91.1% is an annual mapped-person statistic, while Urban's 57.5% uses an average-month administrative numerator. FNS reports 42.177 million average-month persons in FY2023 and 41.690 million in FY2024. Dividing those counts by PE's 66.364 million annual eligible pool yields 63.55% and 62.82%.

This unit/time substitution removes 27.55-28.29 percentage points, or 82-84% of the published 33.61-point rate difference. A residual 5.32-6.05 points remains. Urban's participant count inferred from its rounded gap is 1.92-2.41 million below FNS, and PE eligibility is 4.0% below Urban, so the residual needs a matched eligibility period and exact Urban numerator before attribution.

The rate row is structurally labeled consumed because Build P consumes the same administrative caseload class, but only at household grain. Household agreement is tautological; the divergent person statistic diagnoses the grain/time bridge. The annotation should state this and avoid a like-for-like presentation. Evidence: USDA FNS SNAP Monthly State Participation and Benefit Summary; Populace `build_us_target_parity_manifest.py:179-198`; `test_us_fiscal_targets.py:1130-1149`; `pipeline/compute_counterparts.py:300-306`.

## What we would tell Urban

### EITC: publish the eligibility funnel

Urban reports 18.445 million eligible EITC tax units. That is 5.247 million, or 22.2%, below the 23.692 million SOI claims count and 4.6-7.6 million below the brief's TY2016 NTA/Treasury eligible-universe range of 23-26 million. PE's held-out forced-positive universe is 26.939 million, 0.939 million above that range; its 23.686 million baseline claims are calibrated and therefore do not validate the denominator.

We would ask Urban to publish the ATTIS funnel from income-positive potential claims through investment-income, qualifying-child/age, valid-SSN, separate-filer, dependency, and filing rules. SOI claims can include erroneous claims and the years differ, so the claims count is not proof by itself. It does establish that 18.445 million needs reconciliation. Evidence: certified `eitc_eligible.py:11-27`, `eitc.py:13-31`; Build P `calibration_diagnostics.json`; Populace `take_up_contract.json:48-63`.

### Refundable CTC: compare eligibility with eligibility

PE reports 17.657 million positive refundable-CTC tax units and Urban 11.795 million. PE's count is within 0.20% of the clean TY2022 SOI Historic Table 2 ACTC claims total of 17.691 million, but calibration consumed that target and PE has no ACTC filing/take-up flag. This is claims-shaped agreement, not independent evidence that PE has 17.7 million statutorily eligible units.

We would ask Urban to document its filing and eligibility construction, but first PE must expose a forced-filing statutory ACTC eligibility metric. Until then, annotate the comparison as claims versus modeled eligibility.

The requested actual TY2023 ACTC count could not be named from trustworthy local evidence under the no-network constraint. Do not use 17,312,260: that row comes from `22incd.csv`, which both the importer and Ledger package identify as TY2022, despite an incorrect TY2023 label in one generated consumer-fact artifact. The clean locally pinned national figure is TY2022 Historic Table 2 N11070 = 17,691,450. Pin the actual TY2023 Historic Table 2 N11070 value before publication.

### WIC: preserve the holdout, but show the age offsets

WIC has zero calibration targets. Independent implementations agree bit-exactly after the monthly-gate fix. PE eligibility is 9.367 million versus Urban's 9.444 million, a 76,701 or 0.8% difference; participation is 51.4% versus 53.5%, a 2.1-point difference.

This is meaningful held-out validation, especially for eligibility. It is not wholly unseeded: PE's claim gate consumes separate FNS CY2022 category rates of 78.4% for infants and 46.0% for children. The national eligibility match also hides a 434,957 infant shortfall offset by 357,256 more children ages 1-4. Preserve WIC as a validation holdout or use a target rotation if future releases add WIC controls. Evidence: Populace `target_parity_manifest.json:680-689`, `source_stages.json:2250-2301`, `wic_claim.py:89-130,283-338`; `docs/RECONCILIATION.md:20-44`.

## Audit scope and limitations

- This audit used only supplied JSON, static engine/Populace/Ledger code, and existing release diagnostics. It ran no new microsimulation and used no network access.
- It covers the 2024 scorecard quantities only. It does not adjudicate the separate 2026 projection or full-participation gate work.
- The certified venv path named in the brief was absent after the harness restart. Engine citations use the local version-identical PE-US 1.764.6 snapshot at commit `92e6052d3e`.
- The branch's checked-out `data/comparison.json` predates the two calibration fields despite the resume note. The locally reachable rebuilt blob at `c80b6c4:data/comparison.json` supplies `calibration_relationship` and `calibration_basis`; all ten queued values match the branch copy.
- ATTIS is closed-source. The EITC finding therefore has medium rather than high confidence, and several program-level open questions require Urban documentation.

The complete per-item evidence, quantification, proposed issue or annotation text, and open questions are in `diagnosis/diagnoses.json`.
