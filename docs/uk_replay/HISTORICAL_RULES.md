# Historical rules for the UK fiscal-event replay

The main rules dependency is restoring complete historical systems, rather
than adding an event's parameter changes. The installed PolicyEngine UK
**2.125.1** has substantial dated history, but its processing fills missing
history only back to **2015** and annualises government parameters only for
**2015–2040**. Several retired schemes survive as formulas, while others
survive as reported amounts. RuleSpec UK offers some useful structural
references but does not supply a 2010–2022 parameter history.

This is a source audit on the evening of 9 October 2026 (New York time), with
**no simulations**. The earlier
[mechanics notes](research/peuk_mechanics.md) and
[RuleSpec notes](research/rulespec_uk.md) concern UK 2.124.0 and were used as
leads. The base audit read installed 2.125.0 files; the final audit checked
the installed **2.125.1** patch against its wheel and compared all 109
preserved base-file hashes. The RuleSpec UK pin remains
`1c1101cba14ac683a49df41d58d34cb66c4d9290`.

The [source evidence](evidence/historical_rules_sources.json) preserves the
2.125.0 base files, their SHA-256 hashes, the national RuleSpec rules and
absence searches. The [2.125.1 patch receipt](evidence/historical_rules_patch_2.125.1.json)
preserves the latest read NIC source/YAML and identifies unchanged base
files. Four of the 109 preserved base files changed; additional patch files
are labelled newly read. The [audit script](research/audit_historical_sources.py)
records the base source audit without importing the model; reproduce that
receipt against the pinned 2.125.0 source, then apply the separately pinned
patch receipt. The complete
[raw parameter-date index](../../data/uk/events/pe_uk_parameter_dates_2.125.1.json.gz)
records every leaf's YAML dates. `UK/` below means the installed
`policyengine_uk/` package; `RS/` means the pinned `rulespec-uk/` checkout.
These paths are also the keys in the preserved evidence.

## What a date key does and does not establish

`UK/tax_benefit_system.py::process_parameters` uprates, then calls
`backdate_parameters(..., "2015-01-01")`, then
`convert_to_fiscal_year_parameters(self.parameters.gov)`. In
`UK/utils/parameters.py`, backdating copies a leaf's first available value
into the gap from 2015 to that first date. It does not reconstruct the
intervening law. Annual conversion samples 30 April of each year from 2015
to 2040, except for leaves marked `fiscal_year_blend`, which use a weighted
average over 6 April–5 April, or `preserve_calendar_dates`, which retain
their dates. [H1](#h1)

Consequently, a later first key can become an earlier apparent value. For
example, the benefit-cap file begins on `2016-11-07`, the CGT annual exempt
amount on `2018-01-01`, and SDLT first-buyer relief on `2018-03-15`: each can
be filled back to 2015 by this mechanism. The files do not encode the
earlier regime merely because the processed tree can return a value.
Likewise, pre-2015 date keys are not subject to the package's fiscal-year
conversion. VAT switches from 17.5% to 20% on `2011-01-04`; a bare January
date and a fiscal-year costing period are different queries. These are
static implications of the read code, not claims from a replay run.
[H1](#h1), [H7](#h7), [H12](#h12), [H13](#h13)

The table reports **raw keys present**, not certified years. A value can
remain in force without an annual key, and a key can itself be incomplete
or misdated. For example, the personal-allowance file goes directly from
`2015-04-06` to `2017-04-06`; checking the intervening year against a
historical statutory source remains required. Supporting machinery also
matters: `employment_income` reads the income-elasticity labour-supply
response, whose parameter first key is 2020 and is filled only to 2015.
Extending that common floor is a prerequisite, not a repair to the policy
history. [H1](#h1), [H2](#h2)

## Coverage by policy area

Effort is an **engineering estimate**, in lane-days for researched rules,
implementation and focused historical examples. It excludes population
builds, vintage-target ingestion, event-by-event certification and new
microdata acquisition. Ranges are planning allowances, not measured tasks;
shared work is deliberately grouped. Remaining historical law is to be
verified against archived legislation and Budget documents before coding.

| Area | Raw history available for the replay years | Main gaps and implications | Estimated rules effort |
|---|---|---|---|
| Common time handling | Government FY conversion 2015–2040; backdate floor 2015; income-elasticity first key 2020 | Extend the time framework to 2010, audit missing leaves rather than fill with later law, and certify mid-year changes. [H1](#h1) | 4–7 shared days |
| Income tax: allowance, bands, regional schedules | Personal allowance and UK scale start April 2015; allowance taper 2009; Scotland scale 2017 | No 2010–2014 allowance/band history; allowance has no 2016 key; Scottish residence formula has no commencement condition. Age-related allowances were not found. [H2](#h2) | 6–10 days |
| Income tax: savings, dividends, marriage/pension reliefs | Savings starter allowance keyed 2010; PSA keyed 2005; dividend rates 2015 and allowance 2016; marriage transfer maximum 2016 | Pre-2016 dividend tax-credit/gross-up calculation is absent from the read liability/base formulas. Early PSA and savings-start keys need historical verification. Married Couple's Allowance is an input, not computed eligibility/amount. Pension allowance history also needs completing. [H2](#h2) | 6–10 days, sharing the income-tax audit |
| NIC Class 1 employee | Main/additional rates 2015; thresholds 2015 | Add 2010–2014 rules; additional rate is 3.25% from April 2022 until April 2024 in the raw file, while main rate changes in November 2022. Annualisation needs checking. Contracted-out machinery was not found. [H3](#h3) | 4–7 days for Class 1/2/4 history; 5–10 additional for contracting-out machinery and data interface |
| NIC Class 1 employer | Employer rate and secondary threshold 2015 | Add earlier values and historical employer exceptions. Employment Allowance machinery was not found. A household earnings formula alone does not establish the firm-level allowance base. [H3](#h3) | Included in NIC history; firm-level machinery remains a separate scoped task |
| NIC Class 2 | Flat rate and small-profits threshold 2015; lower-profits-threshold switch 2015/2022; threshold values 2022/2023; award formula is present | 2.125.1 uses Class 4 relevant profits, contribution-week counts and the higher liability threshold for 2022–2023. Earlier rates/thresholds remain missing. Full-year self-employment is assumed, and voluntary Class 2 is explicitly excluded. [H3](#h3), [H3P](#h3p) | Included in NIC history |
| NIC Class 3 | `ni_class_3` exists only as an input | No contribution-rate/entitlement calculation to replay. Voluntary contributions require a distinct behavioural/data treatment if admitted to household scope. [H3](#h3) | 3–5 days for a rule surface; behavioural/data scope unknown |
| NIC Class 4 | Rates/profits thresholds 2015; annual-maximum interaction starts 2003; latest YAML includes 9.73%/2.73% and £11,908 lower limit for 2022 | 2.125.1 repairs the encoded 2022 rates/limits and later transitions. Earlier 2010–2014 values remain missing; validate the annual maximum with Classes 1/2 and historical profit inputs. [H3](#h3), [H3P](#h3p) | Included in NIC history |
| Tax credits, WTC and CTC | WTC element history starts 2002; child element and income thresholds 2016; disabled-child element 2015; couple-with-children hours key 2012 | Formulas remain, but reported receipt gates eligibility. Complete CTC and threshold history, pre-2012 hours rules and prior-year-income/disregard mechanics; year-specific legacy recipients are indispensable. [H4](#h4) | 8–14 days, plus population work |
| Legacy benefits: Income Support | Award/applicable-amount formulas exist; personal amounts/disregards 2015; capital 2010; lone-parent child-age limit 2012 | Complete earlier amounts and eligibility transitions; first amount keys need historical source validation. [H5](#h5) | 3–6 days |
| Legacy benefits: income-based/contributory JSA and ESA | Main amount/capital parameters mostly 2015 | Contributory awards pass through reported values; income-related awards apply a capital screen to reported amounts. Full award/NI-contribution entitlement and ESA components are not implemented in these formulas. [H5](#h5) | 15–25 days for entitlement machinery, then population inputs |
| Universal Credit | Taper/capital keys 2013; standard allowance 2015; work allowances 2016; child element 2018 | Complete early allowances/elements. `would_claim_uc` is an input, default True; no variable formula reads `rollout_rate`. Recipiency/migration must be reconstructed per year. Social-rent formula has no size-criteria reduction. [H6](#h6) | 8–14 days, plus migration/population work |
| Child Benefit and HICBC | Child Benefit amount history 2007; HICBC thresholds June 2015 | Child Benefit amounts reach 2010; complete the HICBC start/early threshold history and confirm annual timing. [H7](#h7) | 1–3 days |
| State Pension, including pre-2016 | Basic rate 2002; new-pension activation 2016; triple-lock raw series 2011; **current** age timetable keyed 1995 | Basic/additional/new formulas exist, but scale reported data-year receipt. Additional pension is the reported excess over the relevant flat-rate ceiling, scaled with the flat-rate ratio; there is no earnings/NI-record accrual calculation in it. The age YAML explicitly omits earlier timetable versions: restore pre-event age law for its future scoring years. [H8](#h8) | 5–10 days for uprating/cohort/vintage-age replay; full accrual reconstruction unknown pending lifetime-record inputs |
| Pension Credit | Guarantee and savings-credit thresholds 2015; some capital/savings rules 2002–2003; child/disability additions 2018–2019 | Add 2010–2014 guarantees/thresholds and verify introduction dates of later additions; guard against backdating them. [H9](#h9) | 3–6 days |
| Housing Benefit and LHA | Core allowances/withdrawal key 2015; LHA maximum 2014 and percentile/freeze 2015; non-dependant rates 2018 | Working-age eligibility requires continuing reported HB and no UC claim. Historical open-claim rules, early LHA/local rates, deductions and social-sector size criteria require work. Current eligible-rent formula does not apply the size reduction. [H10](#h10) | 7–12 days, plus local-rate and population ingestion |
| Council tax, Council Tax Benefit and Council Tax Reduction | Council-tax liability is a data input; national CTR parameters 2013; local schemes have separate files | The `council_tax_benefit` name wraps post-2013 CTR logic; no separate pre-2013 national CTB system was established. Household liability and local scheme histories need year-specific data. Freeze-grant machinery was not found. [H11](#h11) | 8–15 days for CTB/basic CTR; comprehensive local histories unknown |
| VAT | Standard rate 1973–2011; reduced-rate keys 1994–1997 | Tax calculation exists, but year interpretation before 2015 and historical consumption/category coverage need auditing. This is household incidence; wider OBR revenue channels stay outside the model boundary. [H12](#h12) | 1–3 days shared with fuel timing |
| Fuel duty | Petrol/diesel April 2010 onward; rural relief 2012; LPG/natural-gas 2021 | Petrol/diesel keys reach June 2010; earlier-year queries and smaller fuel classes need completing. Formula is monthly, so match scoring FY timing explicitly. [H12](#h12) | Included in VAT/fuel timing |
| Alcohol and tobacco duties; VED | Current alcohol/tobacco parameters begin 2023; the read duties and car VED have `formula_2024` | Historical schedules/formulas need encoding. APD/IPT machinery was not found. Dated formulas do not establish pre-2024 coverage. [H12](#h12) | 8–15 days for alcohol/tobacco/vehicle histories; APD/IPT separate scope |
| CGT | Main/property/carried-interest/BADR rates 2015; annual exempt amount 2018 | Add 2010–2017 history and check transitions against statutory sources; backdating the later exemption is not historical coverage. Household gains composition/realisation remains a population constraint. [H13](#h13) | 3–6 days |
| IHT | No parameter or variable found by the recorded inheritance/IHT/nil-rate-band search | Tax machinery and an estate/death/transfer input model would be new work. Coverage of those inputs is unknown. [H13](#h13) | 10–20 days for bounded tax machinery; estate-data feasibility first |
| SDLT | Main residential scale has keys from 2003; additional-property rule 2016; first-buyer relief 2018 | Purchase formula always applies marginal scales; no earlier slab calculation appears. Correct historical regime switches and relief commencement, then supply transaction amounts/dates. [H13](#h13) | 3–6 days |
| LBTT | Residential/non-residential/rent scale keys 2015; surcharge 2016 | Geography-only liability condition has no date test. Verify start, first-buyer relief and surcharge histories rather than rely on filled values. [H14](#h14) | 1–3 days |
| LTT | Scale keys 2018 | Geography-only liability and England/NI-only SDLT liability mean the read routing does not switch Wales from SDLT to LTT by date. Add dated territorial routing and verify scale changes. [H14](#h14) | 1–3 days |
| Disability/carer benefits and benefit cap | DLA/PIP/AA/Carer's Allowance core rates 2015; benefit cap November 2016 | Add older rates and earlier cap regime. Disability categories and programme migration come from population inputs, not an entitlement assessment reconstructed here. [H7](#h7), raw date index | 3–6 days for historical amounts; migration work separate |

These ranges are not additive project estimates: income/NIC framework work,
time handling and shared benefit machinery overlap. [PLAN.md](PLAN.md)
combines them with population, vintage and certification dependencies.

The latest Class 2 machinery is more detailed than the base audit's formula.
`utils/class_2.py` counts Sundays in the 6 April–5 April contribution year
instead of multiplying by a constant 52, so a full-year liability can use
52 or 53 weeks. It applies profits **at or above** the small-profits
threshold before 2022 and profits **above** the lower-profits threshold
from 2022, leaving the intermediate treated-as-paid band with no payable
amount. The new YAML sets the lower threshold to £11,908 for 2022 and
£12,570 for 2023, and the compulsory weekly rate to zero from
`2024-04-06`. The award is still for full-year self-employment; the read
code does not model voluntary contributions. [H3P](#h3p)

The same liability/week helper supplies notional Class 2 in the UC minimum
income-floor NI deduction. Class 4's annual-maximum formula uses the
relevant-profit base and actual Class 2 deductions, while retaining a
separate **53-week** flat-rate allowance in its statutory step calculation.
The latest Class 4 YAML has a single 2022 annual main/additional rate of
9.73%/2.73%, followed by 9%/2% in 2023 and 6%/2% from 2024. These source
changes improve the 2015 onward rule surface; they do not establish a
historical population or certify the earlier years. [H3P](#h3p)

## Retired schemes: present formulas versus missing machinery

* **WTC/CTC survive.** `working_tax_credit.py` and `child_tax_credit.py`
  calculate awards, but `is_WTC_eligible.py` requires a positive reported
  WTC amount and `is_CTC_eligible.py` requires reported CTC and the legacy/UC
  choice. `tax_credits_applicable_income.py` sums current-period income; it
  does not implement a prior-tax-year income comparison or income-rise/fall
  disregard. A historical receipt population can support bounded award
  changes; a today's-recipient population cannot establish the old caseload.
  [H4](#h4)
* **Income Support survives as an entitlement formula.** It subtracts
  applicable income from applicable amount and applies eligibility. In
  contrast, `jsa_contrib.py` and `esa_contrib.py` sum reported awards, while
  `jsa_income.py` and `esa_income.py` explicitly document that they are not
  full entitlement models. Historical JSA/ESA rate/component measures need
  new award machinery or a clearly labelled reported-award construction.
  [H5](#h5)
* **Pre-2016 State Pension has formulas.** It is incorrect to call the
  entire retired system absent: BASIC/NEW routing, basic amounts and an
  additional-pension component exist. The missing mechanism is accrual from
  lifetime contribution/earnings history, including the detailed additional
  pension calculation; the implemented amount scales reported receipt.
  `state_pension_reported.py` also begins its conversion formula in 2022,
  so historical builds must explicitly supply the appropriate reported
  input rather than assume the current conversion applies. [H8](#h8)
* **Pre-2013 Council Tax Benefit is the clearest missing retired benefit
  system in this audit.** The current variable's statutory references and
  calculation concern CTR, and the national CTR parameter histories start
  in 2013. A pre-2013 award cannot be certified from the variable name.
  [H11](#h11)

The State Pension age table is an especially important distinction between
historical outturn law and event-vintage law. Its YAML comment says the
1995-keyed timetable reflects current text, including the 2011 and 2014
amendments, and that earlier versions are not separately encoded. Even if
that current table gives the right status on a realised past date, it does
not represent a pre-amendment event baseline projected into future costing
years. Vintage timetable versions must therefore be supplied for age-change
measures. The payroll interface also needs the same vintage choice:
`ni_liable.py` gates primary Class 1/Class 2 on the annual State Pension age
flag. [H8](#h8), [H3](#h3)

Whether historical source microdata contain every needed legacy claimant,
contribution, pension accrual and local housing input is **unknown from
this rules audit**. [POPULATIONS_AND_VINTAGES.md](POPULATIONS_AND_VINTAGES.md)
defines the data investigation. Package `verified_start_year` metadata and
raw YAML dates are useful signals; neither is evidence of an independently
certified historical system. [H1](#h1)

## What RuleSpec UK can supply

The audit parsed the national `RS/uk/**/*.yaml` modules, excluding tests
and ProgramSpecs. There are **1,491 rules**: **1,474 with one version**,
**11 with no version** (relation rules) and **6 with two versions**. The
two-version cases are Class 3 NIC, company-size thresholds and GDPR caps;
none is a 2010–2022 tax-benefit history. Of **600 parameter rules**, **250**
start at the sentinel `0001-01-01`. These counts are reproducible from the
`rulespec_national_rules` section of the preserved evidence, including the
file path of every rule.

`effective_from` labels a rule version; it does not prove that the module
contains historical values. The personal allowance module
`RS/uk/statutes/ukpga/2007/3/35.yaml` sets `12570` at the sentinel date.
Dividend rates in `.../8.yaml` are a single 2024-dated version containing
10.75%, 35.75% and 39.35%; the unchanged UK dividend scale instead dates the
10.75% basic rate to 2026. The benefit-cap module
`RS/uk/regulations/uksi/2013/376/80A.yaml` dates its single current limit
table to 2013, whereas UK's cap file changes to that table in 2023. These
source conflicts require legislation checks; copying RuleSpec dates would
not resolve the earlier histories. [R1](#r1)

| RuleSpec area/file | Dated content checked | Contribution to the missing historical system |
|---|---|---|
| Income tax: `uk/statutes/ukpga/2007/3/{35,8,55B}.yaml` | Allowance sentinel; dividend rates single 2024 version; explicit 2015–2016 marriage-transfer amount and 2016 onward percentage/rounding rules | Marriage transfer is a narrow earlier-value/structural reference. No allowance/band/dividend history for 2010–2022. [R1](#r1), [R2](#r2) |
| NIC: `uk/statutes/ukpga/1992/4/{8,15}.yaml` | Single 2% additional-rate versions from 2011 | Narrow earlier keys than UK's raw 2015 start; cannot supply thresholds/main rates or a complete 2022 exception. [R2](#r2) |
| Tax credits: `uk/regulations/uksi/2002/{2005/schedule/2,2007/7}.yaml`, `uksi/2024/247/3.yaml` | Element tables dated 2024 | No full tax-credit award/income pipeline was established; does not fill PE's early CTC/threshold gaps. [R3](#r3) |
| Income Support/JSA/ESA: `uksi/1987/1967/53.yaml`, `uksi/1996/207/116.yaml`, `uksi/2008/794/118.yaml`; ESA composed pipeline | Capital tariffs dated 1988/1996/2008; ESA applicable-amount pipeline for 2026–2027 | Useful formula references for components; no annual historical amount/entitlement chain. [R3](#r3) |
| UC: `uksi/2013/376/24A.yaml`; `policies/universal_credit_composed_award_pipeline.yaml` | Two-child-limit module has `rules: []` and is deferred; composed pipeline expressly excludes it and is for 2026–2027 | Current UC structure is a reading aid, not the migrating 2013–2025 system. [R4](#r4) |
| State Pension: `uk/policies/govuk/state-pension.yaml` | Basic-pension qualifying-year formula dated 2010; new-pension qualifying-year formula dated 2016; imported weekly rates from 2026 instruments | Could guide an explicit qualifying-years interface. No historical rate history or additional-pension accrual module found. [R5](#r5) |
| Pension Credit/HB/CTR, CB/HICBC and disability areas | National rule/version inventory records the module paths and each `effective_from`; individual rules largely single-version | No 2010–2022 annual history was established. The earlier notes contain a broader module map; importing these areas requires an independent historical audit. **Unknown** whether fuller historical source text exists outside this checkout. [source evidence](evidence/historical_rules_sources.json) |
| VAT/fuel duty, CGT, LBTT/LTT | National inventory has single-version modules; checked LBTT 2015 and LTT 2022/2024 rate tables | Existing PE date histories are generally richer. The checked tables do not reconstruct earlier regime changes. [R6](#r6) |
| IHT, SDLT, retired national CTB | No supplying module was established in the audited national inventory | Treat as unsupplied, not as an assumed future rules-engine capability. [source evidence](evidence/historical_rules_sources.json) |

RuleSpec could therefore reduce research effort on particular clauses or
provide independent formula examples. It is **not an automatic historical
rules provider** for this programme. An adapter, verified historical
versions and tests against the relevant law would still be needed.
Historical validation and a production import path into PE were not
demonstrated by this audit.

## Evidence paths

Each list below identifies the read files preserved in
[historical_rules_sources.json](evidence/historical_rules_sources.json),
with newer NIC files in the [patch receipt](evidence/historical_rules_patch_2.125.1.json).
Parameter groups not copied in full are covered by the complete raw date
index linked above. Absence claims are bounded to the audited source tree;
the evidence records search patterns and every hit.

### H1

`UK/tax_benefit_system.py`; `UK/utils/parameters.py`; `UK/programs.yaml`;
`UK/variables/input/employment_income.py`;
`UK/variables/gov/simulation/labour_supply_response/income_elasticity_lsr.py`;
`UK/parameters/gov/simulation/labour_supply_responses/income_elasticity.yaml`.

### H2

`UK/parameters/gov/hmrc/income_tax/allowances/personal_allowance/{amount,maximum_ANI}.yaml`;
`.../allowances/personal_savings_allowance/basic.yaml`;
`.../allowances/dividend_allowance.yaml`; `.../allowances/marriage_allowance/max.yaml`;
`.../rates/{uk,dividends}.yaml`; `.../rates/scotland/rates.yaml`;
`.../rates/savings_starter_rate/allowance.yaml`;
`UK/variables/gov/hmrc/income_tax/{earned_income_tax,liability/dividend_income_tax,bases/taxed_dividend_income,allowances/married_couples_allowance,bracketized_liability/tax_band}.py`;
`UK/variables/gov/hmrc/regional/pays_scottish_income_tax.py`;
`uk_absence_searches.queries.age_related_allowances` in the evidence.

### H3

`UK/parameters/gov/hmrc/national_insurance/class_1/rates/{employee/main,employee/additional,employer}.yaml`;
`.../class_1/thresholds/primary_threshold.yaml`; `.../class_2/flat_rate.yaml`;
`.../class_4/rates/{main,additional}.yaml`;
`UK/variables/gov/hmrc/national_insurance/class_3/ni_class_3.py`;
`.../class_2/ni_class_2.py`; `.../class_1/{ni_class_1_employee,ni_class_1_employer,ni_liable}.py`;
`.../class_4/ni_class_4.py`;
raw date index for other NIC thresholds;
`uk_absence_searches.queries.{contracted_out_nics,employment_allowance}`.

### H3P

The 2.125.1 patch receipt preserves
`UK/variables/gov/hmrc/national_insurance/class_2/ni_class_2.py`;
`UK/utils/class_2.py`;
`UK/parameters/gov/hmrc/national_insurance/class_2/{flat_rate,small_profits_threshold,lower_profits_threshold,lower_profits_threshold_applies}.yaml`;
`.../class_4/rates/{main,additional}.yaml`;
`.../class_4/thresholds/{lower_profits_limit,upper_profits_limit}.yaml`;
`UK/variables/gov/hmrc/national_insurance/class_4/ni_class_4_maximum.py`;
`UK/variables/gov/dwp/universal_credit/income/income_floor/uc_minimum_income_floor_national_insurance.py`.
The release [wheel receipt](../../data/uk/events/patch_release_receipt.json)
pins the PyPI download and complete changed-file list.

### H4

`UK/variables/gov/dwp/{is_WTC_eligible,is_CTC_eligible,working_tax_credit,child_tax_credit,tax_credits_applicable_income}.py`;
`UK/parameters/gov/dwp/tax_credits/working_tax_credit/{elements/basic,min_hours/couple_with_children}.yaml`;
`.../child_tax_credit/elements/child_element.yaml`; `.../means_test/income_threshold.yaml`;
raw date index for the remaining elements/thresholds.

### H5

`UK/variables/gov/dwp/{jsa_contrib,jsa_income,esa_contrib,esa_income,income_support_entitlement,income_support_applicable_amount}.py`;
`UK/parameters/gov/dwp/{JSA,ESA}/income/amount_over_25.yaml`;
`.../income_support/amounts/amount_16_24.yaml`;
`.../income_support/eligibility/lone_parent_youngest_child_age_limit.yaml`;
raw date index for capital and other amount rules.

### H6

`UK/variables/gov/dwp/universal_credit/{would_claim_uc,is_uc_eligible,housing_costs_element/uc_housing_costs_element}.py`;
`UK/parameters/gov/dwp/universal_credit/{standard_allowance/amount,means_test/work_allowance,rollout_rate}.yaml`;
`uc_rollout_formula_search` and raw date index in the evidence.

### H7

`UK/parameters/gov/hmrc/child_benefit/amount/eldest.yaml`;
`UK/parameters/gov/hmrc/income_tax/charges/CB_HITC/phase_out_start.yaml`;
`UK/parameters/gov/dwp/benefit_cap.yaml`; raw date index for disability/carer amount files.
`UK/variables/gov/dwp/{pip/pip_dl,dla/dla_sc,attendance_allowance,carers_allowance_pre_overlap}.py`.

### H8

`UK/variables/gov/dwp/{basic_state_pension,additional_state_pension,new_state_pension,state_pension_type,state_pension_reported}.py`;
`UK/parameters/gov/dwp/state_pension/{basic_state_pension/amount,new_state_pension/active}.yaml`;
`UK/variables/gov/dwp/state_pension_age.py`; `UK/utils/state_pension_age.py`;
`UK/parameters/gov/dwp/state_pension/age/{age_by_birth_date,day_by_birth_date,male/age,male/born_before}.yaml`;
raw date index for the age timetable and triple-lock series.

### H9

`UK/parameters/gov/dwp/pension_credit/{guarantee_credit/minimum_guarantee,savings_credit/threshold}.yaml`;
raw date index for additions, capital and savings-credit rules.

### H10

`UK/variables/gov/dwp/housing_benefit/housing_benefit_eligible.py`;
`.../housing_benefit/entitlement/housing_benefit_entitlement.py`;
`UK/parameters/gov/dwp/{housing_benefit/means_test/withdrawal_rate,LHA/maximum/A}.yaml`;
raw date index for HB allowances/non-dependant rates and LHA;
`uk_absence_searches.queries.social_sector_size_criteria`.

### H11

`UK/variables/gov/dwp/council_tax_benefit.py`;
`UK/variables/input/consumption/property/council_tax.py`;
`UK/parameters/gov/local_authorities/england/council_tax_reduction/pensioners/means_test/withdrawal_rate.yaml`;
`.../{scotland,wales}/council_tax_reduction/means_test/withdrawal_rate.yaml`;
raw date index for local-authority schemes and the council-tax subtree.

### H12

`UK/variables/gov/hmrc/{vat,fuel_duty/fuel_duty,alcohol_duty/beer_duty,tobacco_duty/tobacco_duty}.py`;
`UK/variables/gov/dft/vehicle_excise_duty/car_vehicle_excise_duty.py`;
`UK/parameters/gov/hmrc/{vat/standard_rate,fuel_duty/petrol_and_diesel}.yaml`;
raw date index for other duty parameters; `uk_absence_searches.queries.apd_and_ipt`.

### H13

`UK/parameters/gov/hmrc/cgt/{basic_rate,higher_rate,annual_exempt_amount}.yaml`;
`UK/variables/gov/hmrc/sdlt_on_residential_property_transactions.py`;
`UK/parameters/gov/hmrc/stamp_duty/residential/purchase/{main/subsequent,main/first/max,additional/min}.yaml`;
`uk_absence_searches.queries.inheritance_tax`.

### H14

`UK/variables/gov/{hmrc/sdlt_liable,revenue_scotland/lbtt_liable,wra/ltt_liable}.py`;
`UK/parameters/gov/revenue_scotland/lbtt/residential/rate.yaml`;
`UK/parameters/gov/wra/land_transaction_tax/residential/primary.yaml`;
raw date index for the remaining scales/surcharges.

### R1

`RS/uk/statutes/ukpga/2007/3/{35,8}.yaml`;
`RS/uk/regulations/uksi/2013/376/80A.yaml`, compared with the UK files in H2/H7.

### R2

`RS/uk/statutes/ukpga/2007/3/55B.yaml`;
`RS/uk/statutes/ukpga/1992/4/{8,15}.yaml`.

### R3

`RS/uk/regulations/uksi/2002/2005/schedule/2.yaml`;
`RS/uk/regulations/uksi/2002/2007/7.yaml`; `RS/uk/regulations/uksi/2024/247/3.yaml`;
`RS/uk/regulations/uksi/{1987/1967/53,1996/207/116,2008/794/118}.yaml`;
`RS/uk/policies/esa_income_related_applicable_amount_pipeline.yaml`.

### R4

`RS/uk/regulations/uksi/2013/376/24A.yaml`;
`RS/uk/policies/universal_credit_composed_award_pipeline.yaml`.

### R5

`RS/uk/policies/govuk/state-pension.yaml`;
`rulespec_absence_searches.queries.additional_state_pension`.

### R6

`RS/uk/statutes/asp/2013/11/24.yaml`;
`RS/uk/statutes/anaw/2017/1/24.yaml`;
`rulespec_national_rules` for the remaining rate histories and module paths.
