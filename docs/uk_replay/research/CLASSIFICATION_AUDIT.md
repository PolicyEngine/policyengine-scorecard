# Targeted classification audit, 9 October 2026

The final inventory uses 2.125.1. The patch follow-up below supersedes the earlier
Class 2/4 source findings; the initial audit and its 37 amendments remain recorded.

This continuation reviews the surviving verifier disputes and material inventory rows,
against the installed **policyengine-uk 2.125.0** source. It is a targeted audit, not a
claim that every one of the 3,796 classifications was independently reproduced. No
simulations were run. The 37 complete amended records are in
`data/uk/events/classifications/review_corrections.json`; the parent build integrates
them by `row_id`, so this JSON file is deliberately not another classification JSONL.
Paths beginning `variables/`, `parameters/` or `data/economic_assumptions.py` below
are relative to the installed `policyengine_uk/` package; the complete source path
read was the installed wheel's `policyengine_uk/` tree. The durable
[selected source snapshot](../evidence/classification_sources.json) preserves
the cited code and hashes, so this audit does not depend on scratch paths.

All pound totals here use `base_rows.jsonl::gross_gbp_m`: the sum of absolute values
over the original scoring fiscal years, in £ million. They are neither one-year
costings nor an event's net fiscal impact.

## Material changes

| Change from recovered batches | Rows | Gross £bn |
|---|---:|---:|
| Expressible → partial | 10 | 43.680 |
| Out → partial | 6 | 16.509 |
| Out → not expressible | 12 | 88.744 |
| Not expressible → partial | 2 | 6.025 |
| Expressible → out | 3 | 8.095 |
| Not expressible → out | 2 | 1.000 |

Two further amendments correct explanatory text or an outside-scope reason. These
figures describe the proposed corrections before integration; the final event
summary is authoritative for programme totals.

## Structural gaps hidden by an existing parameter

**Age-related personal allowances.** `policyengine_uk/variables/gov/hmrc/income_tax/allowances/personal_allowance.py`
reads one common `PA.amount`, `PA.maximum_ANI` and `PA.reduction_rate`; it reads no age
or birth date. [HMRC's historical allowance table](https://www.gov.uk/government/publications/rates-and-allowances-income-tax/income-tax-rates-and-allowances-current-and-past)
shows separate older-person allowances and a different income taper through 2015-16.
Consequently the allowance changes at `autumn_2012:tax:010`,
`budget_2013:tax:039`, `budget_2014:tax:001` and `autumn_2014:tax:001` are partial,
as are their three classified benefit-response siblings. This is a missing statutory
structure, in addition to the separate date-key gaps. The June 2010, Budget 2011 and
Budget 2012 allowance rows already acknowledge it.

**Winter Fuel Payment.**
`policyengine_uk/variables/gov/dwp/winter_fuel_allowance.py::on_mtb` checks Pension
Credit, Income Support, income-related ESA and income-based JSA, but omits UC and tax
credits. The [2024 regulations](https://www.legislation.gov.uk/uksi/2024/869/body/2024-09-16)
and [SSAC's letter on them](https://assets.publishing.service.gov.uk/media/6709199430536cb927483050/ssac-letter-to-sswp-social-fund-wfp-regs-2024.pdf)
include these passports. `autumn_budget_2024:spending:044` (£8.521bn) is therefore
partial. The same formula's 2025 income passport uses a household `any` test and one
household payment, with strict `<` at the threshold. It cannot allocate payment and
recovery separately for pensioners with different incomes in one household.
`autumn_budget_2025:spending:110` (£10.192bn) is partial. The
[Budget 2025 policy costing](https://assets.publishing.service.gov.uk/media/6926e0849c1eda2cdf034098/Budget_2025_policy_costings_-_revised.pdf)
describes an individual recovery and the complete benefit passport list; the engine
instead books the net effect as household eligibility.

**Entrepreneurs' Relief lifetime limit.**
`policyengine_uk/variables/gov/hmrc/capital_gains_tax/capital_gains_badr.py` explicitly
documents treating the current year's gains as if no lifetime limit had been used
before. `capital_gains_tax.py` caps these annual gains directly at
`gov.hmrc.cgt.badr.lifetime_limit`; there is no prior-usage input in that calculation.
Thus `budget_2020:tax:041` (£5.261bn), which changes the lifetime limit itself, is
partial. This does not automatically downgrade every CGT rate change.

## Household heads and scope judgements

**CJRS is included as employee-linked wage support, with a named gap.** Three grant
rows and six direct Income Tax/NIC payroll rows move to in/not expressible. The
[15 April 2020 Treasury Direction](https://www.gov.uk/government/publications/treasury-direction-made-under-sections-71-and-76-of-the-coronavirus-act-2020/treasury-direction-made-under-sections-71-and-76-of-the-coronavirus-act-2020)
paras 2.2 and 8.1 link reimbursement to the pay and associated employer NIC/pension
costs of specified employees. This is an explicit scope judgement: the grant is paid
to employers and includes a composite employer-cost leg, but its per-employee wage
support is household relevant. It is not treated like an unrestricted business grant.
The source search found no CJRS/furlough/reference-pay policy machinery in the
2.125.0 variable or parameter trees; `policyengine_uk/variables/input/employment_income.py`
has earnings and behavioural additions, not a furlough scheme. An annual income
override would not construct this policy or a no-support employment counterfactual.
The separate BGA/DEL and purely indirect consumption-tax rows remain outside scope.

**Employer NICs and salary sacrifice have actual income-tax channels.**
`policyengine_uk/variables/contrib/policyengine/employer_ni/employer_ni_fixed_employer_cost_change.py`
compares employer rates, thresholds and pension exemptions with the baseline and
changes pay at a fixed employer cost. `variables/input/employment_income.py` includes
this addition. Its incidence parameter,
`parameters/gov/contrib/policyengine/employer_ni/employee_incidence.yaml`, defaults to
1. Therefore AS2022's levy reversal and employer-threshold freeze, and AB2025's
employer-threshold freeze, have partial household income-tax constructions. They do
not reproduce an OBR gradual incidence path or unincorporated employers' profits
channel.

`variables/gov/hmrc/national_insurance/salary_sacrifice_broad_base_haircut.py` applies
the broad earnings haircut whenever the pension cap is finite. Its
`parameters/gov/contrib/behavioral_responses/salary_sacrifice_broad_base_haircut_rate.yaml`
defaults to 0.0016. The AB2025 income-tax head is partial; the NICs sibling's statement
that all behavioural responses are off by default was incorrect and is amended.

**The AS2023 employee-NIC income-tax head is partial, not incorporation-only.**
The [AS2023 policy costing, p9](https://assets.publishing.service.gov.uk/media/655d0a83544aea000dfb321d/Autumn_Statement_2023_Policy_Costings_-_Final.pdf)
identifies employment, hours and incorporation responses. The optional earnings
response exists in
`variables/gov/simulation/labour_supply_response/employment_income_behavioral_response.py`,
using `gov.simulation.labour_supply_responses`; the income and substitution
elasticities default to zero in their YAML files. This supports a partial verdict,
consistent with SB2024's sibling, with extensive-margin entry and incorporation
still absent. The verifier's proposed `not` verdict incorrectly inferred that the
whole income-tax head was incorporation. For the three older CGT-to-income-tax
rows, scope is harmonised to in/not: the detailed OBR decomposition is unknown and
no income-to-gains or incorporation construction has been identified.

**Loan-book accounts remain outside scope.** The verifier proposed including the
£27.425bn Spring 2022 student-loan spending reform as partial. This is rejected under
the rubric's explicit loan-book/RAB/outlay exclusion; the graduate repayment-rule
siblings remain in scope. SR2020's £50m student-loan spending row, AB2025's £5.946bn
student-loan spending row and its £2.099bn accrued-interest row are harmonised to
out. `variables/gov/hmrc/student_loans/student_loan_repayment.py` computes a year's
cash repayment from income, plan and optional outstanding balance, not a lifetime
loan valuation. [OBR's accounting explanation](https://obr.uk/box/accounting-treatment-and-policy-developments-affecting-student-loans/)
and [its Spring 2022 reform box](https://obr.uk/box/the-fiscal-impact-of-student-loans-reforms/)
distinguish projected cash repayments from the transfer/write-off and interest
accounts. A cash-flow proxy must never be labelled this accrual costing.

**General tariffs are consistently outside the household statutory base.** Two
recent rows had been included solely on a consumer-price pass-through argument;
other tariff rows were outside. Harmonise the two to out, while labelling the
household component unknown. [HMRC's integrated tariff description](https://www.gov.uk/government/publications/the-uks-integrated-tariff-schedule/the-uks-integrated-tariff-schedule)
distinguishes importers and production inputs from consumers affected by price
changes. Broad price incidence does not by itself widen every business tax into this
inventory. A separately specified household import/pass-through model could change
that boundary; no customs/import-content policy machinery was found in the inspected
engine trees. The supplier-funded Warm Home Discount levy similarly retains the
rubric's outside supplier-levy classification, with the rebate spending row inside.

## Projection levers are machinery, not historical readiness

`variables/input/consumption/property/council_tax.py` is an input with no liability
formula. `data/economic_assumptions.py::uprate_council_tax` multiplies that input by
regional growth series. This is a partial level proxy applied during data projection;
it does not supply local authority bands, referendum decisions, empty-home premiums
or pre-2013 Council Tax Benefit rules. Existing council-tax partial classifications
are retained on that limited basis.

The same file's `uprate_rent` reads
`gov.economic_assumptions.yoy_growth.obr.social_rent` for every non-private-rented
tenure, but hard-skips years before 2022. The three Summer 2015 social-rent rows are
harmonised to partial because this lever exists today. A 2016-19 replay as shipped is
blocked by the guard, historical indices and provider/geography detail. The
[government's social-rent reduction guidance](https://www.gov.uk/guidance/welfare-reform-and-work-act-2016-social-rent-reduction)
defines an English registered-provider policy; a UK-wide index cannot implement its
full scope. Public landlords' receipts are also a distinct comparator concept.

One stale rubric fact was checked and rejected: Class 2 NICs is **not** input-only in
2.125.0. `variables/gov/hmrc/national_insurance/class_2/ni_class_2.py` has a flat-rate,
small-profits-threshold formula. Class 3 remains an input in
`class_3/ni_class_3.py`. The survivors already distinguish the Class 2 approximation
from contribution-record and voluntary-payment gaps; no blanket Class 2 upgrade is
applied.

JSA/ESA require a qualification to the earlier research shorthand. In 2.125.0,
`variables/gov/dwp/jsa_income.py` and `esa_income.py` screen reported awards through
capital eligibility and subtract tariff income. `jsa_contrib.py` and
`esa_contrib.py` still add reported awards. These are bounded capital screens and
reported-amount calculations, not full JSA/ESA entitlement, contribution-history or
work-capability/component rules. No recovered expressible classification directly
cites a JSA/ESA variable. Existing partial/not verdicts for their wider reforms are
retained.

UC amount parameters also need the correct initialization order.
`simulation.py` runs `scenarios/uc_reform.py::add_universal_credit_reform` after
loading data and before ordinary post-load parameter changes. That modifier stores
`uc_LCWRA_element` as an input for 2026-29, allocating new claimants by seeded shares
and protecting existing claimants' combined award. Changing `rebalancing.active`
or `elements.disabled.amount` after those inputs are created does not remove them.
An older-event baseline must use the appropriate parameters before data load, and
may require explicit restoration/removal of cached element inputs. SS2025's
standard-allowance rate construction remains machinery-expressible through
`standard_allowance.amount`, but an executable reversal must establish the correct
historical health-element baseline and modifier state as well. The modifier also
does not read `rebalancing.standard_allowance_uplift`; the explicit standard amounts
are read by `standard_allowance/uc_standard_allowance.py`.

`universal_credit/would_claim_uc.py` is a dataset take-up input, and
`universal_credit/universal_credit.py` is defined for that input. Tax-credit
`is_CTC_eligible.py` and `is_WTC_eligible.py` depend on reported receipt. Thus the
existing UC/CTC/WTC amount levers are conditional on claimant and migration inputs;
they are not a cohort rollout rule. `uc_individual_child_element.py` reads the
child-count limit and a birth-date grandfathering flag, supporting removal of the
limit. `uc_limited_capability_for_WRA.py` returns `is_disabled_for_benefits`, so
work-capability descriptor changes and precise LCW/LCWRA cohort assignment are
separate gaps. This is why the WCA reform rows remain not expressible and the 2025
health-element cohort changes remain partial.

## Interpretation and verification

`expressible` denotes existing machinery for the household leg, not a complete
vintage-law baseline, calibrated historical population, certified bundle or matched
fiscal aggregate. In particular, the fuel-duty formula
`variables/gov/hmrc/fuel_duty/fuel_duty.py` is labelled cars only and consumes household
fuel inputs; the VAT formula `variables/gov/hmrc/vat.py` uses household full/reduced
rate consumption and a coverage scalar; private-school VAT in
`variables/contrib/labour/private_school_vat.py` uses pupil counts, mean fees and an
imputed VAT basis. These levers are retained as expressible machinery with explicit
base/concept limitations. They do not recover non-household OBR bases.
For private schools the verdict means the household rate-only leg can be represented
on that imputed base. Boarding fees, school-specific fees, recoverable input VAT and
pass-through responses are not separately observed in this formula, and their
coverage in the imputed mean is unknown. It is not a claim that the full source
row's base or all schools' fiscal VAT accounts are represented; track 1's partial
assessment at its certified construction standard remains usable.

Track 1's 2.89.2 certified-bundle result (0 expressible, 13 partial, 163 not
expressible, 145 outside across five registries) uses a stricter construction and
artifact standard. This inventory's 2.125.0 machinery counts do not supersede that
result or imply any new certified replay. Validation checks row identities, allowed
scope/classes and resolution of cited paths and variables. It does not validate a
reform's quantitative outcome; no such outcome was computed here.

The builder's `validate` function checked all **37 corrected records** against the
2.125.0 parameter/variable index and their original PMD rows: **0 errors**.

## Final PyPI patch follow-up: 2.125.1

The final version check found a substantive Class 2/4 patch. The review read the
wheel `/tmp/uk-replay-scope/latest_patch.whl`, and the updated installed source,
without importing the country package or running a simulation. The durable source
record is [the patch source manifest](../evidence/patch_sources.json). Seventeen
complete follow-up records are in
`data/uk/events/classifications/patch_corrections.json`: all 11 Class 2-area rows,
the Spring 2022 Class 2-to-UC effect, and five Class 4/date collateral notes.

`policyengine_uk/utils/class_2.py::class_2_liable` now uses the lower profits
threshold from 2022-23, representing the compulsory cash liability exclusion for
the treated-as-paid band. The formula tests profits strictly above this threshold;
the earlier SPT test applies before 2022. The new
`parameters/gov/hmrc/national_insurance/class_2/lower_profits_threshold.yaml` has
£11,908 at 2022-04-06 and £12,570 at 2023-04-06, while
`lower_profits_threshold_applies.yaml` switches the rule on at 2022-04-06. The
updated `flat_rate.yaml` includes £3.45/week at 2023-04-06 and ends compulsory cash
payments at 2024-04-06. The threshold switch remains on after abolition so that
restoring a flat rate reconstructs the right pre-abolition profit condition.

`variables/gov/hmrc/national_insurance/class_2/ni_class_2.py` reads
`ni_class_4_profits` and uses `class_2_contribution_weeks`, which counts 52 or 53
contribution weeks, assuming a full year of self-employment. The shared profit base
is documented in `class_4/ni_class_4_profits.py`; the formula deducts its modelled
capital allowances, trading allowance and carried losses, while trade-interest and
certain royalty deductions remain unmodelled.

The resulting **one classification upgrade** is
`autumn_statement_2023:tax:010`, compulsory Class 2 abolition: partial → expressible,
**£1.804737006bn gross**. Its earlier missing treated-as-paid band and counterfactual
weekly-rate reasons are now false. The reversal restores the compulsory rate and
`gov.hmrc.national_insurance.class_4.annual_maximum.includes_class_2` so that
`class_4/ni_class_4.py` and `ni_class_4_maximum.py` restore the pre-abolition annual
maximum treatment as well. Unchanged voluntary contributions are not a missing leg
of abolishing compulsory liability. This is a machinery verdict; full-year
self-employment and historical population requirements still apply.

The other 10 Class 2-area verdicts are retained. The SPT/LEL freezes still need
contribution-credit and voluntary-payment channels, even though the treated-as-paid
cash band is now represented. The Class 2/3 voluntary rate freezes and overseas
eligibility changes still lack voluntary-payment/contribution-record machinery.
The 2018 delayed bill remains partial because the PMD does not specify all its
provisions; the benefit consequence still needs contribution histories. The Spring
2022 cash-liability reform remains expressible, now using the explicit lower-profit
switch/threshold instead of artificially moving SPT. The 2016 compulsory abolition
remains expressible with the annual-maximum caveat named.

The UC MIF NI formula,
`variables/gov/dwp/universal_credit/income/income_floor/uc_minimum_income_floor_national_insurance.py`,
uses the same Class 2 helper and week count on notional floor income. Actual UC NI
deductions still add Class 1 employee, Class 2 and Class 4, excluding voluntary
Class 3, in `income/uc_national_insurance_on_earnings.py`. These fixes update the
Spring 2022 UC consequence's construction note, not its class.

The patch also corrects Class 4 date claims. `class_4/rates/main.yaml` and
`additional.yaml` carry the post-repeal annual 2022-23 blended rates 9.73%/2.73%,
returning to 9%/2% on 2023-04-06. A vintage-faithful AB2021 world must instead set
10.25%/3.25% for 2022-23. The combined current-law Class 4 main-rate cut is dated
2024-04-06 at 6%, and `thresholds/lower_profits_limit.yaml` has £12,570 from
2023-04-06. A current-law marginal reversal of AS2023's one-point cut can use 7%; an
AS2023-vintage pair instead needs 9% → 8%, excluding SB2024's later two-point cut.
Class 1 employee rates remain monthly, and the separate Class 1 additional-rate
YAML's late-reversion historical gap is not fixed by this patch.

All **17 follow-up records** passed the builder's existing row/path/variable
validation against the **2.125.1 index: 0 errors**. No quantitative result was
computed. Final event summaries incorporate this one upgrade and supersede any
earlier 2.125.0 count snapshot.
