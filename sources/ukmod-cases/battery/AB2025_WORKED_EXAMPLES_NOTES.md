# Autumn Budget 2025 worked examples as a mode-3 case battery (tranche 4 of #136)

`ab2025_worked_examples.json` turns the single-household worked examples that producers published
around the Autumn Budget 2025 into CaseSpecs under `SCHEMA.md` (inputs and expected focus only). It
was drafted on 2026-09-25 from the harvest `sources/harvest-uk-ab2025-2026-09-24/`: every row of
family `uk_cases_commercial` (121 rows, 16 producers) and the specimen-household rows of the other
families, selected as rows whose `conditions` carry `household_type`, `household` or
`employment_income`, or whose `proposed_metric` is one of `household_tax_change`,
`take_home_pay_change`, `take_home_pay`, `household_income_tax_bill`, `household_post_rent_income`,
`pension_pot_projection` (141 rows after dropping population shares, energy-bill averages and the
Minimum Income Standard rows, which are not single-household tax-benefit quantities). The per-family
`NOTES.md` supplied each example's assumptions. Scripts: the scratchpad `build_battery.py` (writes
the JSON) and `check_battery.py` (the machine check reproduced below).

Result: **46 cases from 14 producers**, evaluated in 2025 (14), 2026 (1), 2028 (11), 2029 (16),
2030 (3) and 2031 (1); 18 are current-law levels and 28 carry a registered baseline world.

## Rules applied

- One case per distinct specimen household a producer used. Rows that share a household across
  measures, years or output variables (an income tax bill and the same person's extra tax; an
  employee figure and the employer figure beside it; a five-year table) collapse into one case, and
  every value the producer printed for it is quoted in the rationale as text. No expected value is
  a field.
- Several years for the same inputs: the first year is written and the rationale says so. Where the
  inputs differ by year (InvestEngine's interest grows each year; CPS states the 2030-31 salary) one
  case per year is written. Where the same household is evaluated in a different registered world
  (AJ Bell's Sally under current rules in 2025-26 and under the NI cap in 2029-30) both are written,
  following the existing battery's two-child-limit pairs.
- `policy_year` is the tax year the producer evaluated: 2025 for 2025-26 examples, 2028 for the
  first year of the extended freeze, 2029 for the salary-sacrifice cap, and so on. Rationales of the
  2025 cases note that the thresholds they turn on are frozen at the same nominal values in 2026-27.
- `baseline` is set only when the example compares against the pre-Budget position, and names the
  registered descriptor exactly as `scorecard_db/baselines.py` carries it (per-measure worlds carry
  both `policy` and `measure`, because `baseline_key` hashes the whole descriptor). Worlds used:
  `pre_ab2025__personal_tax_thresholds_freeze_to_2031` (6 cases),
  `pre_ab2025__salary_sacrifice_pension_nics_cap_2000` (15),
  `pre_ab2025__savings_rates_plus_2pp_and_starter_limit_held` (3), `pre_ab2025` (1) and
  `pre_ab2025__uc_standard_allowance_and_health_element_rebalancing` (3). **The last is registered in
  `baselines.py` (provenance: executed by the tranche-3 run) but was not among the worlds listed in
  the tranche-4 brief**; it is the world the CPS out-of-work and both RF Universal Credit examples
  compare against, so it is used and flagged in each rationale. Strip the `baseline` from
  `uk-ab2025-cps-uc-single-standard-allowance-2030`, `uk-ab2025-rf-table1-single-unemployed-north-east`
  and `uk-ab2025-rf-uc-couple-two-children-uprating-2026` if the ruling is that it may not be named.
- Employer National Insurance is not a battery variable, so employer-side figures (Deloitte, RSM,
  Fidelity, Royal London, Moore Kingston Smith, PPI, RF) are recorded in the rationale only; the
  employee-side NI is what the case pins.
- Identical households published by two producers are merged into one case, named for the primary
  producer, with the other producer's publication and printed values in the rationale (see
  "Cross-producer merges"). The count of distinct households below is per producer, before merging.
- Unstated inputs are filled with a stated assumption in the rationale (see "Assumptions"), never
  silently. Examples whose inputs cannot be expressed in the closed vocabulary, or whose household
  is not specified in pounds, are skipped and listed below with the reason.

## Distinct households per producer, and cases written

- AJ Bell: 15 distinct households (the eight salaries of the Which? income-tax table, GBP 15,000 to
  GBP 50,270; Sally on GBP 55,000 with a 10% contribution; three "today" incomes for the freeze,
  GBP 15,000 / 45,000 / 47,000; three 35-year-olds for the pension "hole", GBP 50,000 / 75,000 /
  100,000). 14 cases: the eight earners (the GBP 35,000 earner also carries Tom Selby's 31 Oct
  GBP 4,486 / 4,710 figures), Sally with and without salary sacrifice in 2025-26 and under the cap
  in 2029-30, and the three freeze earners. Skipped: the three pension-hole projections.
- EY (via BBC News): 3 households (Fatima, Deborah, Neal and Tara); 3 cases.
- Hargreaves Lansdown: 3 households (GBP 45,000 at 5% for the rumoured cap; GBP 51,000 for the
  freeze; a 22-year-old on GBP 25,000 with two employer-contribution variants); 1 case (the
  GBP 51,000 freeze earner); the GBP 45,000 household is merged into the Royal London case; the
  pension-pot projection is skipped.
- Quilter: 2 households (GBP 40,000 and GBP 44,000 today); 2 cases.
- Deloitte: 1 household (GBP 50,000 at 10%); 1 case.
- RSM: 3 households (Employees A, B, C); 3 cases.
- Fidelity: 4 households (GBP 40,000 at 5%; GBP 40,000 at 10%; GBP 110,000 sacrificing GBP 10,000;
  GBP 120,000 sacrificing GBP 20,000); 3 cases; the GBP 40,000 at 5% household is merged into RSM
  Employee A.
- Moore Kingston Smith: 2 households (GBP 50,000 and GBP 100,000 at 5%); 2 cases.
- Royal London: 1 household (GBP 45,000 at 5%); 1 case (with Hargreaves Lansdown merged in).
- Blick Rothenberg: 2 households (GBP 60,000 at 5%, merged into RSM Employee B; a higher-rate saver
  with GBP 8,000 at 4.5% and "no personal savings allowance", skipped); 0 own cases.
- Pensions Policy Institute: 4 input sets (the median earner projected close to GBP 43,000 at 5%
  and 10%; the GBP 50,270 upper-earnings-limit earner at 5% and 10%); 4 cases.
- InvestEngine (via MoneyWeek): 1 scenario household over five years; 3 cases (years 3-5, where the
  interest exceeds the personal savings allowance); years 1-2 are zero in both worlds and are noted
  in the rationales rather than written.
- Centre for Policy Studies: 4 households (the GBP 50,000 worker in 2025-26; the same worker on the
  stated GBP 56,269 in 2030-31; the full-new-State-Pension pensioner; the single over-25 on the UC
  standard allowance only); 4 cases; the pensioner's 2030-31 point and the "quadruple lock" variant
  are recorded in the rationale, not written (nominal pension not printed; option not registered).
- CPAG: 1 household (workless lone parent, three children, private three-bedroom rent) across seven
  areas; 2 cases (Inner London, Cardiff); five areas skipped (BRMA registry).
- Resolution Foundation: 10 Table 1 specimen families plus the "couple with two children on
  Universal Credit" uprating example and the GBP 3,000 salary-sacrifice example; 3 cases (the
  unemployed single adult in the North East; the capped single parent with four children in London;
  the UC couple); the GBP 3,000 example is merged into RSM Employee B; 8 Table 1 families skipped.
- Producers with rows in scope but no case: Aegon, Which? (own rows), IG, Rathbones, Evelyn
  Partners, IFS, Fabian Society, HMRC (TIINs), HM Treasury (factsheet), OBR, Tax Policy Associates,
  Trussell / WPI - reasons below.

## Skipped, by reason

Counted as examples (a household or a printed worked figure), not rows.

- Input concept absent from the closed vocabulary (13 examples):
  - property income - Fabian Society's one-property landlord (GBP 1,400/month rent, taxable profit
    half of gross, +2pp = GBP 170 a year);
  - council tax band - IFS band G / band H doubling (+GBP 3,800 / +GBP 4,560), Tax Policy
    Associates' band G "around GBP 4,000", HM Treasury's average band D GBP 2,280; council tax
    itself is also not a `FOCUS_VARIABLES` entry (only `council_tax_reduction` is);
  - Broad Rental Market Area not in `BRMA_REGION` - CPAG's Guildford, Brighton and Hove, Oxford,
    Harlow and Northampton rows (5);
  - employer pension contributions and multi-decade pension-pot projections - AJ Bell's three
    35-year-olds (GBP 22,060 / over GBP 37,000 / nearly GBP 50,000 holes by 65) and Hargreaves
    Lansdown's 22-year-old (GBP 226,000 vs GBP 283,000 at retirement);
  - mileage and vehicle - the OBR / Which? electric-car driver at 8,500 miles (GBP 255);
  - flat-rate expense reliefs - HMRC's homeworking-relief removal (GBP 62 / GBP 124);
  - winter fuel payment - HMRC's PAYE customer with a GBP 200 payment (GBP 17 / GBP 33 a month
    deductions): no income or age stated, the printed figure is a monthly PAYE coding deduction, and
    `winter_fuel_payment` is not a `FOCUS_VARIABLES` entry.
- Household not specified in pounds (income is a projection or a descriptive label the producer
  did not print) (26 examples):
  - Rathbones' four 2022 salaries (GBP 35,000 / 50,000 / 80,000 / 100,000) grown on an unpublished
    OBR wage path, cumulative since 2022 and scoring the pre-Budget freeze-to-2030 option;
  - RF Table 1's other eight families (full-time NLW, low-to-median, median-to-high, high-paid,
    "average private pension income" incomes in 2028-29 are RF projections; their energy and
    transport components are outside the vocabulary in any case);
  - RF's rate-band examples (basic-rate employee GBP 140 / GBP 220 / GBP 73, higher-rate GBP 280 /
    GBP 660 / GBP 222, additional-rate GBP 440, average or basic-rate pensioner GBP 160 / GBP 52,
    typical worker on GBP 35,000 "around GBP 1,400" against a no-freeze-since-2021 world that is not
    registered, median-employee tax-wedge and self-employed comparisons, the GBP 2.5 million
    home-owner, the GBP 40,000 pensioner break-even);
  - IFS's full-time minimum-wage worker (GBP 137 / GBP 759; the 2029-30 NLW is an IFS projection),
    hours-at-minimum-wage (31 / 18 hours), UC marginal retention (45p / 32p), and the basic /
    higher / additional-rate taxpayer plateaus (GBP 220 / 600 / 390; the exact per-earnings Flourish
    series is staged in `uk_ifs_ab2025` and could seed further cases);
  - CPS's pensioner in 2030-31 (only real levels printed) and the quadruple-lock variant (option).
- Not a single-household quantity (26 examples): IG's ninth and top decile averages; Which?'s
  personal-savings-allowance balance thresholds (GBP 22,728 / 11,364); the Aegon and PPI cap
  maxima (GBP 160 / 300); InvestEngine's ISA-saver counts; Evelyn Partners' restated OBR yields
  (12); Which?'s restated OBR / government examples (GBP 5,310 x 560,000 families, GBP 900 NLW);
  Trussell's restated GBP 900 NLW figure.
- Producer assumes away the statute (1): Blick Rothenberg's cash-ISA example computes GBP 144 with
  "no personal savings allowance", which the engines cannot be asked to ignore.

## Assumptions made (all stated in the case rationale)

Global conventions, applied wherever the example is silent:

- Region `SOUTH_EAST` for "rUK rates (not stated otherwise)" (39 cases); stated places map to their
  ITL-1 region (north London -> `LONDON`, Sheffield and Bradford -> `YORKSHIRE`, Cardiff -> `WALES`,
  RF's North East and London as printed).
- Adult age 40 when unstated for an earner (35 for a lone parent, 30 for a single UC claimant "over
  25", 70 for a pensioner, 45 for the CPS worker five years on); stated ages are used (Deborah 63,
  Neal and Tara 58).
- Tenure owner-occupier with a mortgage and no rent for pure tax cases (immaterial to income tax and
  National Insurance); owner-occupier outright where the producer says so (mortgage paid off; "standard
  allowance only", i.e. no housing element).
- Freeze examples: the producer grew the stated income with inflation (AJ Bell, EY, Quilter) or
  stated it for 2027-28 (Hargreaves Lansdown); the case holds the stated nominal income and writes
  the first year of the extension (2028), so it pins the per-year mechanism, not the printed
  cumulative. Hargreaves Lansdown's counterfactual is wage-indexed thresholds, whereas the registered
  world follows the pre-Budget CPI path.

Case-specific:

- `uk-ab2025-aj-bell-sally-net-pay-2025`: the contribution is written without `salary_sacrifice`,
  which the connector maps to its engine's non-sacrifice concept. AJ Bell's printed employee NI
  (GBP 3,394) equals 8% of (55,000 - 12,570) with no 2% band above the upper earnings limit; the
  case is expected to surface that as an oracle-side difference.
- `uk-ab2025-ey-fatima-25000-lone-parent-london`: one child aged 8 (the piece says only "single
  mum"); council rent GBP 150/week = 7,800.
- `uk-ab2025-ey-deborah-20000-sheffield`: the adult son is a separate benefit unit aged 30 with no
  income (neither is stated).
- `uk-ab2025-ey-neal-tara-couple-100000-bradford`: the combined "about GBP 100,000" is split
  GBP 50,000 each.
- `uk-ab2025-ppi-median-43000-ss-*`: PPI's "close to GBP 43,000 in 2029" is written as exactly
  GBP 43,000.
- `uk-ab2025-investengine-cash-isa-year*`: employment income GBP 30,000, chosen so the saver is a
  basic-rate taxpayer with non-savings income above the starting-rate-for-savings band, as
  InvestEngine's "basic-rate taxpayer" with a GBP 1,000 allowance implies; ISA holdings are not an
  input (ISA interest is outside the tax base).
- `uk-ab2025-cps-pensioner-full-nsp-2025`: the full new State Pension is written at its 2025-26
  rate, GBP 230.25/week = 11,973 (CPS names the pension, not the amount).
- `uk-ab2025-cpag-benefit-cap-lone-parent-*`: rent set at the three-bedroom LHA rate the table
  implies (Inner London GBP 485/week = 25,220; Cardiff GBP 215/week = 11,180; CPAG computes from
  LHA rates but does not print them); parent 35, children 12, 9, 5; no earnings. The compared
  outputs are invariant to the exact rent once the cap binds; CPAG's post-rent income is not a
  battery variable.
- `uk-ab2025-rf-table1-single-unemployed-north-east`: age 30; social rent GBP 100/week = 5,200.
- `uk-ab2025-rf-table1-capped-lone-parent-four-children-london`: private rent GBP 350/week =
  18,200 in the `Outer London` BRMA, high enough that the family is capped even with only two child
  elements (RF says only "subject to the benefit cap"); parent 35, children 12, 9, 6, 3 (the two
  youngest post-April-2017 births); no earnings.
- `uk-ab2025-rf-uc-couple-two-children-uprating-2026`: adults 35 and 33, children 8 and 5, no
  earnings, social rent GBP 120/week = 6,240, region `SOUTH_EAST`.

## Cross-producer merges (one case, all producers cited in its rationale)

- `uk-ab2025-rsm-employee-a-40000-ss-5pct` also carries Fidelity's GBP 40,000 at 5% (no extra NI).
- `uk-ab2025-rsm-employee-b-60000-ss-5pct` also carries Blick Rothenberg's GBP 60,000 at 5%
  (GBP 20 / GBP 150) and the Resolution Foundation's GBP 3,000-sacrifice example (GBP 150 employer,
  GBP 20 employee above the higher-rate threshold, no income named).
- `uk-ab2025-royal-london-45000-ss-5pct` also carries Hargreaves Lansdown's GBP 45,000 at 5% for
  the rumoured cap (GBP 30 / GBP 34 against Royal London's "approximately GBP 20" / GBP 37.50): the
  oracle run adjudicates between the two printed answers.
- `uk-ab2025-aj-bell-earner-35000` carries both the Which? table row and Tom Selby's 31 Oct piece.

## Machine check (scratchpad `check_battery.py`, run 2026-09-25 against `scorecard_db/case_diffs.py`)

```
load_battery: OK, 46 cases, schema=sources/ukmod-cases/SCHEMA.md schema_version=1
case_id clashes with cases.json: none
regions used: {'LONDON': 3, 'NORTH_EAST': 1, 'SOUTH_EAST': 39, 'WALES': 1, 'YORKSHIRE': 2} -> all in VALID_REGIONS['UK']: True
BRMAs used: {'Inner London': 1, 'Cardiff': 1, 'Outer London': 1} -> all in BRMA_REGION and in their region: True
person keys used: {'age': 62, 'employee_pension_contributions': 17, 'employment_income': 40, 'hours_worked_per_week': 1, 'salary_sacrifice': 16, 'savings_income': 3, 'state_pension': 1} -> subset of PERSON_KEYS: True
household keys used: {'benefit_units': 46, 'brma': 3, 'people': 46, 'region': 46, 'rent': 46, 'tenure': 46} -> subset of HOUSEHOLD_KEYS: True
tenures used: {'owned_mortgage': 37, 'rented_social': 3, 'owned_outright': 3, 'rented_private': 3} -> subset of VALID_TENURES: True
expected_focus used: {'benefit_cap': 3, 'child_benefit': 5, 'income_tax': 40, 'national_insurance': 28, 'pension_credit': 1, 'universal_credit': 7} -> subset of FOCUS_VARIABLES['UK']: True
FOCUS_VARIABLES['UK'] not exercised by this battery: ['carers_allowance', 'council_tax_reduction', 'housing_benefit', 'scottish_child_payment']
policy years: {2025: 14, 2026: 1, 2028: 11, 2029: 16, 2030: 3, 2031: 1}
baseline worlds: {'current_law (no baseline)': 18, 'pre_ab2025__salary_sacrifice_pension_nics_cap_2000': 15, 'pre_ab2025__personal_tax_thresholds_freeze_to_2031': 6, 'pre_ab2025__savings_rates_plus_2pp_and_starter_limit_held': 3, 'pre_ab2025__uc_standard_allowance_and_health_element_rebalancing': 3, 'pre_ab2025': 1}
case keys used: ['baseline', 'case_id', 'country', 'description', 'expected_focus', 'household', 'policy_year', 'rationale'] -> subset of CASE_KEYS: True
PROBLEMS: none
```

`load_battery` exercises every validator in `case_diffs.py` (unknown keys, ages, finite amounts,
benefit-unit assignment, tenure/rent consistency, region registry, BRMA registry and region match,
focus registry, baseline registration via `baselines.py`, duplicate ids). The four unexercised focus
variables are a property of the source material - no producer published a carer, council tax
reduction, Housing Benefit or Scottish Child Payment worked example - not a gap in the battery's
construction; this file is not the coverage battery, `cases.json` is (`tests/test_case_schema.py`
loads only `cases.json`).

## Vocabulary the schema lacks that several examples needed

- Property (rental) income as a person key - the Fabian Society landlord, and RF's Figure 14
  marginal rates across income sources.
- Council tax band (and council tax liability as a focus variable) - IFS, Tax Policy Associates, HM
  Treasury and RF's mansion-tax examples (four producers).
- More BRMAs in `BRMA_REGION` - five of CPAG's seven areas (Guildford, Brighton and Hove, Oxford,
  Harlow, Northampton).
- Employer pension contributions, distinct from the employee's, and a way to say a contribution is
  the auto-enrolment minimum - AJ Bell, Hargreaves Lansdown and PPI describe contributions as
  "5% personal + 3% employer"; the pot projections would also need a growth assumption, which is
  outside a tax-benefit case in any event.
- Winter Fuel Payment as a focus variable - the HMRC TIIN example and RF Table 1's pensioners.
- Energy and transport consumption (bills, fuel, mileage, rail) - RF Table 1's energy and transport
  components and the OBR / Which? EV example; not tax-benefit inputs.
- Income projections: many examples state an income "today" or in 2022 and let it grow on an OBR
  wage or CPI path; the battery can only hold a nominal amount per policy year, so such examples
  are written for one year with the stated amount (flagged), or skipped when no amount is printed.

## Points for review

- The three cases in the UC rebalancing world (registered but not in the brief's list) - keep or
  strip the baseline.
- `policy_year` 2025 on 14 cases follows the brief ("the tax year the example is evaluated in");
  the existing battery re-pinned its 2025-26 examples to 2026 for the live-calculator oracles. These
  cases are not calculator work-list entries, so nothing breaks, but the convention differs.
- The assumed incomes on the InvestEngine cases and the assumed rents on the CPAG and RF cases are
  the assumptions with the most leverage; each rationale says what they were chosen to achieve.
