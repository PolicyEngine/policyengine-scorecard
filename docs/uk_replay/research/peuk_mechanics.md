# PolicyEngine UK 2.124.0: can it represent 2010–2022 law? (track 2 of policyengine-scorecard#156)

Scope: read-only audit of the installed source at
`/tmp/uk-replay-scope/venv/lib/python3.12/site-packages/policyengine_uk` (2.124.0, abbreviated `UK/`)
and `.../policyengine_core` (3.32.29, abbreviated `CORE/`). Every claim below cites a file:line read in
this task, or a probe run in this task. Parameter paths `parameters/...` are relative to `UK/`.

Evidence types:
- **source**: file:line read this session.
- **raw-param dump**: `/tmp/uk-replay-scope/agents/peuk_work/raw_params.json`, built by loading `UK/parameters` with
  `policyengine_core.parameters.ParameterNode` and no processing (script `peuk_work/rawparams.py`). "earliest" means
  the oldest date key in the YAML.
- **probe**: `peuk_work/probe.py` loads the fully processed `policyengine_uk.system` and queries parameters and
  household simulations. Output is in `peuk_work/probe.log` and `probe_out.json`, and the run took 720 s. A second probe,
  `peuk_work/probe2.py` (output `probe2.log`), is reported in the appendix.
- **unknown**: not established from the code.

Statements about what the law was (for example "the benefit cap was £26,000 in 2015") come from the task brief or
general knowledge, not from the code, and are marked *(external)*. They need checking against legislation before
anyone relies on them.

---

## Bottom line

1. **No year before 2015 could be simulated in the three probes run here** (narrower than a general claim; see HISTORICAL_RULES.md for the qualified statement). A household simulation for 2010, 2012 or 2014 raises
   `ParameterNotFoundError` on every headline output: income tax, NI, Child Benefit, net income, tax credits and UC
   (probe `sim_2010`, `sim_2012`, `sim_2014`). The first failure is
   `gov.simulation.labour_supply_responses.income_elasticity`. Its earliest key is 2020-01-01
   (`parameters/gov/simulation/labour_supply_responses/income_elasticity.yaml:3`), backdating fills it only to
   2015-01-01, and every earnings-dependent calculation reads it via `employment_income`
   (`UK/variables/input/employment_income.py:13-19`) and `income_elasticity_lsr` (`.../labour_supply_response/income_elasticity_lsr.py:12-13`).
   Behind that come the personal allowance, the NI rates and thresholds, the CTC elements, the IS, JSA and HB amounts,
   the DLA, PIP, AA and CA rates, the Pension Credit guarantee and the UC amounts, all of which first appear in 2015 or later.
2. **2015 and 2016 run without error but are silently wrong in many places.** `backdate_parameters` copies each
   parameter's first value back to 2015-01-01. Some YAML files also key post-reform law at a 2005, 2010 or 2015 date.
   Probe-observed cases: in 2015 the benefit cap is the post-November-2016 £13,400 single (outside London) amount; the
   dividend allowance is £5,000; the CGT higher rate is 20%; the CGT annual exempt amount is the 2018 figure, £11,700;
   the SDLT first-time-buyer relief and the 3% surcharge both apply; and the Personal Savings Allowance is £1,000 back
   to 2010. In 2016 the personal allowance is £10,600 (simulated income tax is identical in 2015 and 2016). For
   periods 2015–2017 the default `tax_band` formula classes higher-rate taxpayers as BASIC (see 2(d) item 9). A
   2015 household with no reported legacy award gets UC rather than tax credits (appendix, probe 2).
3. **Datasets only project forward.** `extend_single_year_dataset` copies the base year to each later year up to 2030
   (`UK/data/economic_assumptions.py:53-70`). Core never carries an input backwards and returns default zeros for a
   period before every stored input (`CORE/simulations/simulation.py:1220-1247`).
4. **Legacy benefits are anchored to reported receipt, not simulated from law.** WTC, CTC and working-age HB require
   a reported award (`is_WTC_eligible.py:44-49`, `is_CTC_eligible.py:12-21`, `housing_benefit_eligible.py:48-50,64`).
   JSA and ESA pass the reported amount through (`jsa_contrib.py:11`, `esa_contrib.py:11`, `jsa_income.py:30-31`,
   `esa_income.py:25-26`). Nothing in the code allocates people between UC and legacy benefits by year:
   `rollout_rate` exists but no formula reads it.
5. **Several 2010–2022 instruments are absent.** These are IHT, APD, IPT, the Employment Allowance,
   contracted-out NI rebates, age-related personal allowances, the 50p rate as a dated parameter, the pre-2016 dividend
   tax credit, the slab SDLT system, the social-sector size criteria ("bedroom tax"), the pre-2013 national CTB, the
   2013 benefit-cap levels and council tax freeze grants. Alcohol duty, tobacco duty and VED have `formula_2024` only,
   so they return 0 before 2024.

---

## Part 2: engine mechanics before the base year

(Part 2 comes first because Part 1 relies on it.)

### 2(a) How a parameter is read for 2012 versus 2016

**Pipeline.** `CountryTaxBenefitSystem.process_parameters` (`UK/tax_benefit_system.py:86-116`) runs the steps in
this order:
1. The add_* builders (lines 100-106).
2. A baseline clone (109).
3. `propagate_parameter_metadata` (112).
4. `uprate_parameters` (113).
5. `backdate_parameters(self.parameters, "2015-01-01")` (114).
6. `self.parameters.gov = convert_to_fiscal_year_parameters(self.parameters.gov)` (115). Only the `gov` subtree is
   converted. `household.*` parameters are backdated but keep calendar dates.

**Uprating only extends forward.** Core `uprate_parameter` starts from the latest value and appends entries dated
after it (`CORE/parameters/operations/uprate_parameters.py:339-374`). Nothing is filled backwards.

**`backdate_parameters`** (`UK/utils/parameters.py:11-25`). For each `Parameter`, `earliest = param.values_list[-1]`
(line 16). If `first_instant (2015-01-01) < earliest_instant` (line 19), it writes `earliest_value` over a day-period
from 2015-01-01 that runs up to the day before the earliest key (lines 20-24). A parameter whose earliest key is on or
before 2015-01-01 is unchanged. Nothing before 2015-01-01 is ever filled.

**`convert_to_fiscal_year_parameters`** (`UK/utils/parameters.py:78-120`):
- `YEARS = list(range(2015, 2041))` (line 103).
- It skips parameters marked `preserve_calendar_dates` (106-107).
- For each year it takes the day-weighted fiscal-year average when `fiscal_year_blend` is set (111), otherwise
  `param(f"{year}-04-30")` (112-113).
- It then writes `param.update(period=f"{year}")` (115-119). A bare year is a calendar-year period, so 1 January to
  31 December of each year from 2015 to 2040 takes the 30 April value.
- Years before 2015 are not touched.

Only six YAMLs set `fiscal_year_blend: true`: the three fuel-duty rates and the three CGT rates (grep of `parameters/`).

**How formulas read parameters.** A formula receives the root parameter tree (`CORE/simulations/simulation.py:1528,1545`)
and calls `parameters(period)`. A `Period` resolves to `period.start` (`CORE/periods/helpers.py:58-59`, through
`CORE/parameters/at_instant_like.py:30-42`, where a `Period` is a tuple subclass), so a YEAR period for 2012 reads instant **2012-01-01**.
`Parameter._get_at_instant` returns the first value whose key is on or before the instant, and **`None` if there is
none** (`CORE/parameters/parameter.py:223-227`).

**What a `None` does:**
- On a plain parameter, `ParameterNodeAtInstant` leaves the child out (`CORE/parameters/parameter_node_at_instant.py:36-39`).
  Attribute access then raises `ParameterNotFoundError` (lines 45-49). This is loud.
- In a scale, a bracket whose `rate` or `threshold` is missing is dropped without warning
  (`CORE/parameters/parameter_scale.py:172`). If every bracket is dropped, `calc` raises
  `TypeError: object of type 'int' has no len()` (probe `uk_rates_2012_calc_50000`, and `uk_rates_2012_nbrackets → 0`).
  A partially populated scale silently loses brackets.

**Worked cases (probe, processed parameters):**

| query | parameter earliest key 2015-04-06 or later (e.g. personal allowance 2015-04-06, CTC child element 2016-04-06) | parameter with a 2010-or-earlier key |
|---|---|---|
| 2012 (reads 2012-01-01) | `None`, so `ParameterNotFoundError`. PA@2012 → None; `node_access_PA_2012` raises. | Raw value in force on 1 January 2012, i.e. the **previous fiscal year's** value for April-keyed parameters. WTC basic element@2014 → 1920 but @2014-12-31 → 1940. VAT@2011 → **0.175**, although the YAML switches to 0.2 on 2011-01-04 (`parameters/gov/hmrc/vat/standard_rate.yaml`, values 2010-01-01 0.175, 2011-01-04 0.2). Fuel duty@2011 → 0.5895, the January 2011 value. |
| a parameter first keyed in April of year Y < 2015, queried for Y | — | `None` for year Y, because the query date 1 January precedes the April key. Fuel duty petrol/diesel@2010 → None (earliest 2010-04-01, `petrol_and_diesel.yaml:9`). `tax_credits`@2012 raises on `working_tax_credit.min_hours.couple_with_children` (earliest 2012-04-06, `min_hours/couple_with_children.yaml:3`). |
| 2016 (reads 2016-01-01) | The calendar-2016 value is the 2016-04-30 sample, i.e. the FY2016-17 value. If the parameter begins after 2016-04-30 (benefit cap, 2016-11-07), the backdated first value is returned: benefit cap single outside London@2016 → **13,400**. | Real FY value: PA@2016 → 10,600, but the YAML has no 2016-04-06 key (`personal_allowance/amount.yaml:3`: 2015-04-06 10600, then 2017-04-06 11500). The £11,000 PA for 2016-17 *(external)* is missing. |

The mechanics for **monthly variables** differ. `fuel_duty` is MONTH-defined (`UK/variables/gov/hmrc/fuel_duty/fuel_duty.py:7`).
From 2015 every month of calendar year Y carries the FY-Y value, because conversion writes the whole calendar year. So
January to March read the following fiscal year. Before 2015, monthly reads see the raw dated history.

### 2(b) Projecting a dataset to another year

- `Simulation.build_from_file` / `build_from_single_year_dataset` / `build_from_dataset` call
  `extend_single_year_dataset` (`UK/simulation.py:354-357, 498-500, 512-514`).
- `extend_single_year_dataset(dataset, params, end_year=2030)` (`UK/data/economic_assumptions.py:53-70`) copies the
  base year to every year from `start_year` to 2030 (lines 60-64), then calls `apply_uprating`.
- `apply_uprating` skips the first (base) year and uprates each later year from the year before (lines 86-93). **There
  is no backward path.**
- `apply_single_year_uprating` (98-132) multiplies the previous year's column by `1 + yoy_growth(year)` for each
  index in `UK/data/uprating_indices.yaml` (lines 107-116). It then applies council tax growth by country (135-161),
  rent growth (164-196) and the student-loan cohort logic (199-332).
- **Index mapping** (`uprating_indices.yaml`):
  - `obr.average_earnings` → employment income and pension contributions (30-36).
  - `obr.consumer_price_index` → reported benefits, consumption categories and `state_pension` (37-80).
  - `obr.per_capita.gdp` → capital gains, dividends, savings interest, property income, wealth (89-124).
  - `obr.per_capita.mixed_income` → self-employment income (125-126).
  - `obr.private_pension_index` → private pension income (127-128).
  - `ons.population` → `household_weight` (129-130).
  - `obr.mortgage_interest` (85-88) and the fuel proxies (81-84).
- **How far back each growth series goes** (raw-param dump):
  - `obr.consumer_price_index`, `obr.average_earnings`, `obr.rpi`: from 2009-01-01 (`yoy_growth.yaml:41,120,200`).
  - `obr.per_capita.gdp`, `per_capita.mixed_income`, `mortgage_interest`, `house_prices`, `non_labour_income`, `road_fuel_volume`: from 2021-01-01.
  - `ons.population`: 2021-01-01.
  - `ons.household_interest_income`: 2020-01-01.
  - `obr.rent`, `obr.social_rent`, `ons.private_rental_prices.*`, `obr.cpih`, `consumer_price_index_ahc`: 2022-01-01.
  - `obr.council_tax.{england,scotland,wales}`: 2023-01-01.
  - `finance_ni.domestic_rates`: 2020-01-01.
  - The derived `private_pension_index` is built for 2020–2034 only (`UK/parameters/gov/contrib/create_private_pension_uprating.py:6,14-15`).
- `uprate_rent` logs "Rent uprating is not supported for years before 2022" and **leaves rent unchanged** for
  year < 2022 (`economic_assumptions.py:177-181`).
- **Index parameters** (`gov.economic_assumptions.indices.*`) are built by `create_economic_assumption_indices`
  (`UK/parameters/gov/economic_assumptions/create_economic_assumption_indices.py:22-61`). Each starts at 1.0 in its
  series' first year (38-39) and runs to 2039 (41). After backdating, a 2021-based index reads 1.0 for every year from
  2015 to 2021 (probe: `indices.obr.per_capita.gdp`@2015, @2016, @2017 → 1.0) and `None` before 2015.
  `indices.obr.consumer_price_index`@2010 → 1.035, so the CPI index exists back to 2009.
- **Variable-level `uprating` attributes.** 43 variables use the CPI index, 32 GDP per capita, 5 earnings, and so on
  (grep of `uprating = ` in `UK/variables`). Core applies them only from an **earlier** stored input to a later period
  (`CORE/simulations/simulation.py:1146-1197`). The comment at line 1220 reads "A later input does not carry
  backwards". For a period before every stored input, core returns `holder.default_array()`, usually 0, without
  caching it (1237-1247).
- **Data observation (not a mechanism).** `obr.rpi` and `obr.average_earnings` carry identical values for every year
  from 2009 to 2021 (`yoy_growth.yaml:41-53` and `:120-132`). Two different statistics should not match for 13 years,
  so the RPI history probably needs checking against source.

### 2(c) Explicit year limits found

| limit | where |
|---|---|
| Backdate floor 2015-01-01 | `UK/tax_benefit_system.py:114` |
| Fiscal-year conversion 2015–2040 | `UK/utils/parameters.py:103` |
| Dataset extension to 2030 | `UK/data/economic_assumptions.py:56,61` |
| Rent uprating disabled before 2022 | `UK/data/economic_assumptions.py:177-181` |
| FRS base year constant 2023 | `UK/data/economic_assumptions.py:11` |
| Economic-assumption indices built to 2039 | `create_economic_assumption_indices.py:41` |
| Lagged CPI from 2010; lagged earnings from 2022 | `lag_cpi.py:15`; `lag_average_earnings.py:15-17` |
| Triple-lock series from 2011 | `UK/parameters/gov/dwp/state_pension/triple_lock/create_triple_lock.py:50` |
| Private pension index 2020–2034 | `create_private_pension_uprating.py:6` |
| `Simulation.default_input_period = default_calculation_period = 2025` | `UK/simulation.py:105-106` |
| Structural reforms evaluated at the 2025 default input period | `UK/simulation.py:201-204` |
| Undated reform values applied with `year:2000:100` | `UK/simulation.py:294` |
| `programs.yaml` self-declared `verified_start_year` | CTR 2013 (`programs.yaml:526`); income tax and NI 2019 (`:17,:29`); UC 2019 (`:195`); most benefits and taxes 2022 (e.g. `:207,:219,:231,:334`); alcohol, tobacco and VED 2024–2026 (`:98-99,:111-112,:124-125`) |

No code asserts or raises on the simulation year. The years fail or drift through the parameter-date mechanics instead.

### 2(d) Does a pre-2015 year produce silent anachronisms?

**Before 2015, mostly it fails loudly rather than silently** (Bottom line, item 1). Silent paths still exist:

1. **Dropped scale brackets.** A bracket with a `None` component is dropped (`CORE/parameters/parameter_scale.py:172`).
2. **Dated formulas.** A variable with only `formula_2024` has no formula before 2024 (`CORE/variables/variable.py:741-745`).
   `_run_formula` then returns `None` (`CORE/simulations/simulation.py:1458-1460`), and the default value 0 is used
   (1126, 1249-1251). This applies to:
   - every alcohol duty (`UK/variables/gov/hmrc/alcohol_duty/*_duty.py:13`);
   - `tobacco_duty` (`tobacco_duty.py:13`);
   - `car_vehicle_excise_duty` (`UK/variables/gov/dft/vehicle_excise_duty/car_vehicle_excise_duty.py:14`).
   `state_pension_reported` has only `formula_2022` (`UK/variables/gov/dwp/state_pension_reported.py:11-12`).
3. **Inputs before the data year.** Inputs requested before the first dataset year come back as zeros
   (`CORE/simulations/simulation.py:1237-1247`).
4. **1 January sampling.** Before 2015, parameters are read on 1 January, which returns the previous fiscal year's
   rates (e.g. VAT@2011 = 17.5%; WTC basic element@2014 = 1920).

**From 2015 onwards the anachronisms are silent:**

5. **Backdating** to 2015-01-01 of every parameter first keyed after 2015 (`UK/utils/parameters.py:19-24`). Cases:
   - Benefit cap: first key 2016-11-07 (`parameters/gov/dwp/benefit_cap.yaml:9`), so 2015 and 2016 → 13,400.
   - Dividend allowance: 2016-04-06 → 2015 gets 5,000.
   - CGT annual exempt amount: 2018-01-01 → 2015–2017 get 11,700.
   - UC work allowances: 2016-04-11.
   - CTC child element, family element and income thresholds: 2016-04-06.
   - SDLT first-time-buyer relief: 2018-03-15 (`first/max.yaml:3`); 2015 → max 500,000.
   - SDLT 3% surcharge: 2016-09-15 (`additional/min.yaml:3`).
   - HB non-dependant deductions: 2018-06-18.
   - Scottish income tax schedule: 2017-04-06 (`scotland/rates.yaml:5`). It applies to Scottish residents in every
     year (`pays_scottish_income_tax.py:10-13`; `earned_income_tax.py:18-21`).
   - LTT: 2018-04-01. `ltt_liable` is simply `country == WALES` (`UK/variables/gov/wra/ltt_liable.py:13-15`), and
     `sdlt_liable` is England or Northern Ireland only (`UK/variables/gov/hmrc/sdlt_liable.py:12-18`). So 2015–2017
     Welsh purchases are taxed under 2018 LTT.
   - LSR elasticities (2020).
6. **Post-reform law keyed at early dates in the YAML.** These are not backdating artefacts: the YAML itself puts the
   values there.
   - PSA £1,000 / £500 / £0 from 2005-04-01 (`personal_savings_allowance/basic.yaml:3`).
   - Savings starter rate allowance £5,000 from 2010-04-01 (`savings_starter_rate/allowance.yaml:3`), applied as a 0%
     band (`savings_starter_rate_income.py:23-49`).
   - CGT 10% / 20% from 2015-01-01 (`cgt/basic_rate.yaml:3`, `cgt/higher_rate.yaml:3`).
   - Dividend rates 7.5% / 32.5% / 38.1% from 2015-04-01 (`rates/dividends.yaml:11`).
   The law these values contradict is *(external)*: the PSA started in 2016; the starting rate was 10% on about
   £2,880 before 2015; CGT was 18/28 until April 2016; dividends were taxed at 10/32.5/37.5 with a tax credit until April 2016.
7. **Missing history keys.** No PA key for 2016-04-06, so 2016 = 10,600 (probe; `sim_2016` income tax 3,880 equals
   `sim_2015`).
8. **NI 2022–2023.** The HSCL is encoded as NI rate changes with no fiscal-year blend, so FY2022 reads 13.25% for the
   whole year. The employee additional rate stays at 3.25% until 2024-04-04 (probe `...employee.additional@2023 → 0.0325`),
   while the main rate reverts on 2022-11-06 (`class_1/rates/employee/main.yaml` raw keys: 2022-04-06 0.1325,
   2022-11-06 0.12).
9. **Dated formulas keyed mid-year take effect a year late.** `get_formula` compares `period.start` (1 January) with
   the formula's start date (`CORE/variables/variable.py:729-743`). `tax_band.formula_2017_04_06` therefore first
   applies to period 2018, and `formula_2018_06_01` first applies to 2019 (`tax_band.py:38,56`). For 2015–2017 the
   default `tax_band.formula` runs (`tax_band.py:25-36`). It sets `higher = allowances + thresholds[-2]` and
   `add = allowances + thresholds[-1]` (lines 30-31). The UK scale has four brackets with thresholds
   `[0, 32000, 150000, 10000000]` (probe `uk_rates_2016_thresholds`), so `thresholds[-2]` is the 150,000
   additional-rate threshold and `thresholds[-1]` is a 10m placeholder. A higher-rate taxpayer is therefore classed
   BASIC and gets the £1,000 PSA. In probe 2 (appendix), `investor_2015` and `investor_2016` have ANI of £73k,
   `savings_allowance` 1000 and savings tax 800 = (3,000 − 1,000) × 40%. The higher-rate PSA is £500 (`higher.yaml`,
   raw value 500).

---

## Part 1: scheme-by-scheme

Legend: **A** = formula present, parameter history from 2010 or earlier; **B(yyyy)** = formula present, parameters
start in yyyy; **C** = formula absent; **U** = unknown.
"Date logic" lists explicit year branches in the formulas. Counts of parameter starts come from
`peuk_work/scheme_summary.py` over the raw-param dump.

### Tax credits (WTC, CTC)

- **Variables:** `working_tax_credit`, `child_tax_credit`, `tax_credits`, `*_pre_minimum`, `wtc_entitlement`,
  `ctc_entitlement`, `WTC_*_element`, `CTC_*_element`, `tax_credits_reduction`, `tax_credits_applicable_income`,
  `is_WTC_eligible`, `is_CTC_eligible`, `would_claim_WTC/CTC` (all in `UK/variables/gov/dwp/`).
- **Formulas:** present. `tax_credits.py:12-21` sums WTC and CTC pre-minimum, applies the £26 minimum and the
  `active` switch. The taper is `max(0, income − threshold) × rate`, with a CTC-only threshold
  (`tax_credits_reduction.py:16-23`). The income definition is current-year (`tax_credits_applicable_income.py:24-44`).
  CTC is limited to two children via `limit.child_count` (`CTC_child_element.py`).
- **Date logic:** none in the formulas. Dates come only from parameters.
- **Award mechanics:** WTC needs `working_tax_credit_reported > 0` (`is_WTC_eligible.py:44-49`). CTC needs
  `child_tax_credit_reported > 0` and not `would_claim_uc` (`is_CTC_eligible.py:12-21`). There are no parameters for
  prior-year income, the in-year rise or fall disregards, or finalisation: `means_test` holds only `income_reduction_rate`,
  `income_threshold`, `income_threshold_CTC_only` and `non_earned_disregard` (raw-param dump).
- **Parameters:**
  - From 2010 or earlier: WTC elements from 2002-08-01 (`working_tax_credit/elements/basic.yaml:3`); taper 37%, then
    39% (2008), then 41% (2011-04-06) (`income_reduction_rate.yaml:3`); `min_hours.old_age` 60 from 2011; childcare
    coverage 70/80/70%; `active` from 2003-04-06, false from 2025-04-06; `child_count` inf → 2 from 2017-04-06 (`child_count.yaml:3`).
  - From 2015 or later: CTC `child_element`, `family_element` and `severe_dis_child_element` (2016-04-06);
    `dis_child_element` (2015-04-06); `income_threshold` and `income_threshold_CTC_only` (2016-04-06).
  - From 2012: `min_hours.couple_with_children` (2012-04-06).
  - Overall: 23 of 32 start by 2010, 1 in 2010–14, 8 from 2015.
- **Rating:** WTC elements A; CTC and thresholds **B(2016)**, backdated into 2015. Pre-2015 runs fail. Caseload is
  reported-anchored.

### JSA (income-based and contribution-based)

- **Variables:** `jsa`, `jsa_income`, `jsa_contrib`, `jsa_income_eligible`, `jsa_income_tariff_income`.
- **Formulas:**
  - `jsa_contrib` adds `jsa_contrib_reported` (`jsa_contrib.py:11`). There is no entitlement formula.
  - `jsa_income` is the reported award less capital tariff income, gated on `JSA.income.active` (`jsa_income.py:4-13,27-31`).
    Its documentation says "This is not a full entitlement model" (`jsa_income.py:20-23`).
- **Parameters:** personal amounts, capital limit and disregards from 2015-04-01; `income.active` from 1996-10-07,
  false from 2026-04-01; `takeup` from 2009.
- **Rating:** pass-through, **B(2015)**. Pre-2015 fails on the capital-test parameters.

### ESA (income-related, contributory, WRAG/support component)

- **Variables:** `esa`, `esa_income`, `esa_contrib`.
- **Formulas:**
  - `esa_contrib` adds `esa_contrib_reported` (`esa_contrib.py:11`).
  - `esa_income` is the reported award less tariff income (`esa_income.py:4-10,24-26`), "not a full entitlement model" (`:13-16`).
- **Not found:** no WRAG or support-component parameters were found in `gov.dwp.ESA` (raw-param dump lists eligibility,
  amounts, capital and disregards only).
- **Rating:** pass-through, **B(2015)**. The WRAG and support component is **C**.

### Income Support

- **Variables:** `income_support`, `income_support_entitlement`, `income_support_applicable_amount`,
  `income_support_applicable_income`, `income_support_eligible`, `would_claim_IS`.
- **Formula:** a simulated entitlement: applicable amount less income, times eligibility
  (`income_support_entitlement.py`). The personal allowance is selected by age and family type, plus premiums
  (`income_support_applicable_amount.py`). It is gated on `income_support.active` (`income_support.py:13-15`).
- **Parameters:** amounts from 2015-04-01 (`amounts/amount_over_25.yaml:3`), uprated by `gov.benefit_uprating_cpi`
  (`amounts/amount_16_24.yaml:8`); capital from 2010-01-01; lone-parent child-age limit 5 from 2012-05-21; `active`
  from 1988-04-11, false from 2026-04-01.
- **Data observation:** IS `amount_16_24` = 58.9 at 2015-04-01, while JSA `amount_18_24` = 57.9 for 2015–2019 and 58.9
  from 2020 (raw-param dump). The IS 2015 value looks like a later year's rate keyed at 2015.
- **Rating:** **B(2015)**.

### Housing Benefit (LHA, size criteria, non-dependant deductions) and Council Tax Benefit/Reduction

- **HB formula:** `housing_benefit_entitlement.py:39-69`. Eligible rent is the LHA cap for LHA cases, otherwise rent
  less meals (line 53). Then it subtracts non-dependant deductions and the taper on income above the applicable amount.
- **HB eligibility:** pension age, or a continuing award (reported HB and not claiming UC)
  (`housing_benefit_eligible.py:48-50,64`). A new working-age claim is not possible.
- **Social-sector size criteria ("bedroom tax"):** absent. Social renters' eligible rent is rent less meals (line 53).
  UC is the same: social rent is uncapped (`uc_housing_costs_element.py:21-27`). A grep for "B13", "social sector",
  "under-occupation" and "spare room" in the `dwp` variables and parameters returned nothing. → **C**.
- **HB parameters:**
  - `allowances.*` and `withdrawal_rate` from 2015-04-01.
  - LHA `maximum.*` from 2014-04-01; `percentile` 0.3 from 2015-01-01; `freeze` from 2015-01-01.
  - Non-dependant deduction amounts from 2018-06-18, so they are backdated (2018 values in 2015–2017); age threshold from 2019-04-01.
  - Meals deductions from 2008; capital rules from 2006; `universal_credit_passport` from 2006.
  - Overall: 34 of 87 by 2010, 8 in 2010–14, 45 from 2015.
- **CTB / CTR:**
  - `council_tax_benefit` (`UK/variables/gov/dwp/council_tax_benefit.py:7-...`) is built on the post-2013 CTR schemes
    (references SI 2012/2885, WSI 2013/3029, lines 31-35).
  - The `council_tax_reduction*` variables are under `UK/variables/gov/local_authorities/council_tax_reduction/`.
    Their parameters for England, Scotland and Wales all start 2013-04-01 (21 of 21).
  - `programs.yaml:526` gives verified_start_year 2013 and notes first-pass support for Scotland, Wales and England
    *pensioner* schemes.
  - The pre-April-2013 national CTB has no parameters. → **C**.
- **Ratings:** HB **B(2015)**, reported-anchored for working-age claims. CTR **B(2013)**. CTB **C**.

### State Pension (basic, additional, new), triple lock, Pension Credit

- **`basic_state_pension`:** reported receipt in the data year × (rate for the period ÷ rate for the data year), for
  type BASIC (`basic_state_pension.py:15-58`; data year at 18-22).
- **`additional_state_pension`:** the reported amount above the flat-rate ceiling, scaled by the ratio of flat rates
  (`additional_state_pension.py:53-80`). It is not uprated by CPI, and SERPS/S2P accrual is not modelled.
- **`new_state_pension`:** `new_state_pension.py:19-21` follows the same data-year pattern.
- **`state_pension_type`:** BASIC if the person reached SPA before the nSP activation date, which is the first True of
  `new_state_pension.active` (2016-01-01) (`state_pension_type.py:28-50`). For years before 2016 this yields BASIC for
  everyone at SPA. This is the only scheme with an explicit pre/post-2016 switch.
- **State Pension parameters:**
  - BSP `amount` from 2002-01-01 (`basic_state_pension/amount.yaml:3`); probe @2010 97.65, @2012 107.45.
  - nSP from 2016-01-01.
  - SPA timetable from 1995 (174 brackets).
  - Triple lock built from 2011 (`create_triple_lock.py:50`); `outturn` 2011 = 0.046 (`triple_lock/outturn.yaml:6`);
    probe triple_lock@2011 0.046, @2012 0.052.
- **Pension Credit:**
  - Formulas present (`UK/variables/gov/dwp/pension_credit/...`).
  - `minimum_guarantee` and savings-credit `threshold` start 2015-04-06 (`minimum_guarantee.yaml:4`, `threshold.yaml:4`),
    so pre-2015 is `None`.
  - Savings-credit rates from 2002; capital from 2003; savings-credit `cutoff_year` 2016.
- **Ratings:** BSP **A** (reported-anchored); nSP **B(2016)**, correct start; ASP present but crude; Pension Credit **B(2015)**.

### Benefit cap

- **Variables:** `benefit_cap`, `benefit_cap_reduction`, `is_benefit_cap_exempt*`.
- **Parameters:** all four start 2016-11-07 (`parameters/gov/dwp/benefit_cap.yaml:9`).
- **Effect:** probe @2015 → 13,400; @2014 → None. The 2013–2016 cap levels (£26,000 / £18,200) *(external)* are not
  encoded.
- **Rating:** **B(2016)**, backdated into 2015.

### Child Benefit and HICBC

- **Child Benefit:** amounts from 2007-04-09, including the 2011–2014 freeze keys (`child_benefit/amount/eldest.yaml:3`;
  probe @2010 20.0, @2012 20.3). Rating **A**.
- **HICBC:** `CB_HITC` (`charges/child_benefit_hitc.py:14-21`). Its `phase_out_start` and `phase_out_end` begin
  2015-06-05 (`CB_HITC/phase_out_start.yaml:3`), so pre-2015 is `None`. HICBC started 7 January 2013 *(external)*.
  Rating **B(2015)**.

### DLA, PIP, AA, Carer's Allowance, Winter Fuel Payment, cost-of-living payments, energy support

- **DLA, PIP and AA** read *input* categories (`pip_dl.py:12-20`, `attendance_allowance.py:11-21`) and pay rates
  that start 2015-04-01 (`dla/self_care/higher.yaml:3`, `pip/daily_living/enhanced.yaml:3`, `attendance_allowance/higher.yaml:3`).
  The DLA→PIP migration is not modelled; recipients come from data categories. Rating **B(2015)**.
- **Carer's Allowance:** rate from 2015-04-01; qualifying benefits from 1992. `carers_allowance_pre_overlap.py:22`
  branches on `period.start.year >= 2025` for Carer Support Payment. Rating **B(2015)**.
- **Winter Fuel Payment:** amounts £200 / £300 from 2000-01-01 (`winter_fuel_payment/amount/higher.yaml:2`). The
  formula branches on `period.start.year >= 2024` for the age test (`winter_fuel_allowance.py:19-25`). Means-testing
  (`require_benefits`) applies from 2024, and the income test from 2025. Rating **A**. Pre-2011 amounts *(external)*
  were not checked.
- **Cost-of-living payments:** `cost_of_living_support_payment.py:11-33`. Amounts from 2022-01-01: means-tested 650,
  then 900 (2023), then 0 (2024). Rating **B(2022)**, correct start.
- **Energy Price Guarantee:**
  - `epg_subsidy` sums `monthly_epg_subsidy` over the twelve months of the *calendar* year (`epg_subsidy.py:12-17`).
  - EPG parameters keep calendar dates: 2022-10-01 2,500, 2023-07-01 3,000; `energy_price_guarantee_in_effect` until 2024-04-01.
  - The energy bills rebate council-tax £150 and the EBSS monthly credits are in 2022–23 parameters.
  - Rating **B(2022)**.

### Universal Credit and managed migration

- **Formulas:** present (`UK/variables/gov/dwp/universal_credit/*`).
- **Parameters:**
  - Means-test parameters from 2013-04-29, e.g. the 65% taper (`means_test/reduction_rate.yaml:3`).
  - Some standard-allowance keys from 2015-04-01 (`standard_allowance/amount.yaml:5`).
  - Work allowances from 2016-04-11, so the pre-2016 work-allowance schedule is missing and backdated.
  - Child element from 2018-04-09.
- **UC versus legacy:**
  - `would_claim_uc` has **no formula**: it is a dataset input with default True (`would_claim_uc.py:14-16`).
  - `is_uc_eligible` checks age, capital and the Pension Credit route only, with no year or rollout test (`is_uc_eligible.py:27-49`).
  - `gov.dwp.universal_credit.rollout_rate` exists (`rollout_rate.yaml:13`; 0 until 2017, 0.25 in 2018, 0.85 in 2022
    per probe) but **no `.py` file references it** (grep of `UK/` returned nothing).
  - Legacy exclusivity runs through reported receipt and `would_claim_uc` (`is_CTC_eligible.py:12-14`;
    `housing_benefit_eligible.py:48-50`).
  - In a situation simulation, UC is therefore computed in any year whose UC parameters exist (2015+), and legacy tax
    credits are 0 unless a reported award is supplied (probe `sim_2015`: tax_credits 0.0; see appendix probe 2).
- **Rating:** **B(2013/2015/2016)**. The rollout is **C**: not implemented in formulas.

### Income tax

- **Personal allowance:** `personal_allowance.py:15-26`. The taper (£100k, 50%) has keys from 2009-07-21
  (`maximum_ANI.yaml:4`), but `amount` starts 2015-04-06 (`amount.yaml:3`) and has no 2016 key. **B(2015)**, with a
  known 2016 gap.
- **Age-related allowances:** no parameter or variable found (raw-param search for age_related, age_allowance and
  blind returned only a TV-licence parameter; no `age_allowance` variable in `income_tax/allowances/`). **C**.
- **Bands and rates:** `rates/uk.yaml` keys begin 2015-04-01 / 2015-04-05 (`uk.yaml:12,20`). The additional rate is
  0.45 from 2015. The 50p rate (2010–2013) is **not representable** as a dated parameter, because nothing predates 2015.
  **B(2015)**.
- **Scottish rates:** `rates/scotland/rates.yaml` from 2017-04-06 (`:5`). They apply by residence in every year
  (`earned_income_tax.py:18-21`, `pays_scottish_income_tax.py:10-13`), so they are backdated into 2015–2016.
  `tax_band` has dated formulas `formula_2017_04_06` and `formula_2018_06_01` (`tax_band.py:38,56`). **B(2017)**.
- **Starting rate for savings:** see 2(d) item 6. The rate is implemented as 0% only; the pre-2015 10% rate is not
  representable. **B(2010)**, wrong structure before 2015.
- **Personal Savings Allowance:** keyed from 2005-04-01, so it appears in 2010–2015. **Anachronistic.**
- **Dividends:** the allowance starts 2016-04-06, and rates are keyed from 2015-04-01 with post-2016 values
  (`dividends.yaml:11`). `dividend_income_tax.py:15-37` and `taxed_dividend_income.py:15-24` contain no notional tax
  credit or gross-up. The pre-2016 regime is **C**.
- **Married couple's allowance:** `married_couples_allowance` is an input with no formula
  (`married_couples_allowance.py:4-9`). The deduction rate is 10% from 2010-01-01 (`deduction_rate.yaml:12`). **A**,
  but only if the input is supplied.
- **Marriage Allowance:** `marriage_allowance.py:27-52`; `max` from 2016-04-01, backdated to 2015 (matching the 2015
  start *(external)*). **B(2016)**, effectively 2015.
- **Pensions:** annual allowance from 2015-04-01 (`annual_allowance/default.yaml:3`); `gov.hmrc.pensions` from 2004.
  **B(2015)**.
- **Rent-a-room:** `sublet_income` is an input (`UK/variables/input/sublet_income.py`) that no `gov` formula references
  (grep returned nothing). **C**.
- **Trading and property allowances:** 0 from 2005, 1,000 from 2017-04-06 (`trading_allowance.yaml:3`). **A**.

### National Insurance

- **Class 1:** rates from 2015-04-01 and thresholds (LEL, PT, ST, UEL) from 2015-04-06 (`class_1/rates/employee/main.yaml:3`,
  `class_1/thresholds/primary_threshold.yaml:11`). **B(2015)**.
- **Contracted-out rebates:** a case-insensitive grep for `contracted.out` in `variables/` and `parameters/` found
  nothing. **C**.
- **Class 2:** from 2015. **B(2015)**.
- **Class 3:** `ni_class_3` is an input with no formula (`class_3/ni_class_3.py:4-11`). **C** as a rule.
- **Class 4:** from 2015; `annual_maximum.includes_class_2` from 2003. **B(2015)**.
- **Employment Allowance:** grep found nothing. **C**.
- **Health and Social Care Levy:** no separate variable. It is encoded as NI rate changes (main 0.1325 for
  2022-04-06..2022-11-06; employer 0.1505) and dividend-rate changes from 2022-04-01. The fiscal-year sampling issue and
  the additional-rate inconsistency are in 2(d) item 8. **B(2022)**.

### CGT, IHT, SDLT, LBTT, LTT

- **CGT:**
  - `capital_gains_tax.py:45-...` uses the UK band thresholds.
  - Rates from 2015-01-01 at 10% / 20%, blended across the fiscal year; residential 18% / 28%; carried interest; BADR
    10% from 2015 with lifetime limit £10m → £1m on 2020-03-11.
  - The annual exempt amount starts 2018-01-01 (`annual_exempt_amount.yaml:3`).
  - Rating **B(2015/2018)**. 2015 rates are anachronistic (see 2(d)).
- **IHT:** no variable or parameter. A case-insensitive grep of `variables/` and `parameters/` for `inheritance` and
  `nil.rate.band` matched nothing, and a substring search of raw parameter names for `iht` and `inherit` matched
  nothing. **C**.
- **SDLT:**
  - `sdlt_on_residential_property_transactions.py:13-38` uses `scale.calc`, which is marginal (slice) for every year.
    There is no slab logic.
  - The `main.subsequent` scale has keys from 2003-07-10, including the 7% band from 2012-07-17 to 2015-02-12
    (`subsequent.yaml:37,40`). Read as slices, though, pre-reform keys give slice tax, not slab tax.
  - The switch is keyed 2015-02-12, not 4 December 2014 *(external)*.
  - Surcharge and first-time-buyer relief are backdated (see 2(d)).
  - Rating **B(2003)** with the wrong pre-December-2014 structure. The slab system is **C**.
- **LBTT:** from 2015-04-01 (33 parameters), consistent with the April 2015 start *(external)*. **B(2015)**.
- **LTT:** from 2018-04-01, backdated to 2015, and liable whenever the household is in Wales (`ltt_liable.py:13-15`).
  **B(2018)**, wrong for 2015–2017.

### VAT, fuel duty, alcohol and tobacco duties, VED, APD, IPT, council tax

- **VAT:** modelled from consumption: `vat = (full_rate_consumption × standard_rate + reduced_rate_consumption ×
  reduced_rate) / microdata_vat_coverage` (`UK/variables/gov/hmrc/vat.py:11-19`). Coverage is 0.38 from 2010-01-01.
  The standard rate has its full history to 2011-01-04 at 0.2. Rating **A**, subject to the 1 January sampling before
  2015 (VAT@2011 = 17.5%).
- **Fuel duty:** `fuel_duty.py:11-23` (MONTH). Petrol and diesel from 2010-04-01 (`petrol_and_diesel.yaml:9`), with
  the history 57.19p → 58.19p → 58.95p → 57.95p, then 52.95p from 2022-03-23. Rural relief from 2012-03-01; LPG and
  natural gas from 2021. Rating **A** for petrol and diesel from April 2010.
- **Alcohol and tobacco duties:** `formula_2024` only, with parameters from 2023-08-01 and 2023-11-22. Rating **B(2023)**;
  the formula is effectively absent before 2024.
- **VED:** `formula_2024` only (`car_vehicle_excise_duty.py:14`). **C** before 2024.
- **APD and IPT:** a grep for `air.passenger` and `insurance.premium` in `variables/` and `parameters/` found nothing. **C**.
- **Council tax:**
  - `council_tax` is an input (`UK/variables/input/consumption/property/council_tax.py:4`), as is `council_tax_band`
    (`UK/variables/input/council_tax_band.py`).
  - Projection uses OBR council-tax growth from 2023 (`economic_assumptions.py:135-161`; `yoy_growth.obr.council_tax.*`
    earliest 2023-01-01).
  - There are no council-tax-freeze-grant parameters; the only council-tax parameter subtree is
    `gov.hmrc.council_tax.high_value_surcharge`, from 2028.
  - Rating: liability is an input; the freeze is **C**.

---

## Summary table

| scheme / area | key variables | formula present? | parameter history start (raw) | behaviour in 2010–2014 | 2015–2016 behaviour | gap and effort note |
|---|---|---|---|---|---|---|
| Labour-supply responses (blocks everything) | `employment_income` → `income_elasticity_lsr` | yes | 2020-01-01 | **raises** | backdated, 0 | Add `0000-01-01: 0` keys to the LSR parameters, or backdate further. Trivial, but it only unmasks the next missing parameter. |
| Personal allowance and taper | `personal_allowance` | yes | amount 2015-04-06; taper 2009-07-21 | raises | 2016 = 10,600 (no 2016 key) | Add 2010–2016 PA keys. Small. |
| Age-related allowances | — | **no** | — | — | — | New variables and parameters (PAA / income limit / MCA age test). Medium. |
| Bands and rates (incl. 50p) | `earned_income_tax`, `rates.uk` scale | yes | 2015-04-01/05 | raises (empty scale TypeError) | OK in 2015 | Add 2010–2014 band keys, including the 0.5 additional rate. Small. |
| Scottish rates | `pays_scottish_income_tax`, `rates.scotland` | yes | 2017-04-06 | raises | 2017 schedule applied in 2015–16 | Year-gate Scottish liability (from 2017; SRIT 2016). Small to medium. |
| Savings starter rate / PSA | `savings_starter_rate_income`, `savings_allowance`, `tax_band` | yes | 2010-04-01 / 2005-04-01 | starter rate 0% on £5,000; PSA applied | PSA applied in 2015; pre-2018 `tax_band` classes higher-rate payers as BASIC (PSA £1,000) | Add a 10% starter rate, correct the PSA start, fix `tax_band.formula` indexing. Small to medium. |
| Dividends | `dividend_income_tax`, `taxed_dividend_income` | partial | allowance 2016-04-06; rates 2015-04-01 | raises | 2016 regime in 2015 | Add the pre-2016 tax-credit / gross-up regime. Medium. |
| Married couple's / Marriage Allowance | `married_couples_allowance*`, `marriage_allowance` | MCA input; MA yes | 2010 / 2016-04-01 | MCA OK if input; MA raises | MA backdated (matches 2015 start *(external)*) | MCA amount and age eligibility as a rule. Medium. |
| Pension relief / annual allowance | `pension_annual_allowance` | yes | 2015-04-01 | raises | OK | Add AA 2010–2014 keys (£255k / £50k / £40k *(external)*). Small. |
| Rent-a-room | `sublet_income` (unused) | **no** | — | — | — | New relief. Small. |
| NI Class 1/2/4 | `ni_class_1_*`, `ni_class_2`, `ni_class_4*` | yes | 2015-04-01/06 | raises | OK; 2022 HSCL not blended; 2023 additional rate 3.25% | Add 2010–2014 keys; blend 2022; fix the additional-rate dates. Small. |
| Contracted-out rebate / Employment Allowance | — | **no** | — | — | — | New mechanics; data lacks contracting-out status *(unknown)*. Medium to large. |
| Class 3 | `ni_class_3` | input only | — | — | — | Out of scope for fiscal replay. |
| CGT | `capital_gains_tax` | yes | rates 2015-01-01; AEA 2018-01-01 | raises | 10/20 in 2015 (18/28 law *(external)*); AEA 11,700 | Add 2010–2017 keys (18/28, AEA). Small. |
| IHT | — | **no** | — | — | — | New tax and estate data. Large. |
| SDLT | `sdlt_on_*`, `stamp_duty_land_tax` | yes | 2003-07-10 | slice calc on slab-era rates (wrong) | first-time-buyer relief and 3% surcharge backdated into 2015 | Add a slab formula before 2014-12-04; date the surcharge and FTB relief. Medium. |
| LBTT / LTT | `lbtt_*`, `ltt_*`, `*_liable` | yes | 2015-04-01 / 2018-04-01 | raises | LTT applied in Wales 2015–17 | Year-gate `*_liable`. Small. |
| VAT | `vat` | yes | 1973 | Jan-1 sampling (2011 = 17.5%) | OK | Fiscal-year conversion before 2015. Small (engine). |
| Fuel duty | `fuel_duty` | yes | 2010-04-01 | 2010 raises; Jan-1 sampling | OK (blended) | Add a 2010-01-01 key. Trivial. |
| Alcohol / tobacco duty | `*_duty` (`formula_2024`) | 2024+ only | 2023-08 / 2023-11 | 0 silently | 0 silently | Old duty regimes and rates. Medium. |
| VED | `car_vehicle_excise_duty` (`formula_2024`) | 2024+ only | 2024-04-01 (scales) | 0 silently | 0 silently | Pre-2017 VED bands. Medium. |
| APD / IPT | — | **no** | — | — | — | New taxes, no household data *(unknown)*. Large. |
| Council tax and freeze grants | `council_tax` (input) | input | growth 2023+ | input as given | input | Backcast liabilities; freeze grants not representable. Medium. |
| WTC | `working_tax_credit`, `WTC_*` | yes | elements 2002 | raises (min_hours 2012-04-06; DLA 2015) | reported-anchored | Data must carry reported WTC for the year. Large (data). |
| CTC (incl. two-child limit) | `child_tax_credit`, `CTC_*` | yes | elements 2016-04-06; limit 0001 / 2017 | raises | 2016 values in 2015 | Add CTC 2010–2015 keys; add income-rise disregards. Medium. |
| Tax-credit award mechanics | `tax_credits_applicable_income` | current-year only | — | — | — | Prior-year income and disregards absent. Medium. |
| JSA / ESA | `jsa_*`, `esa_*` | pass-through of reported | 2015-04-01 | raises | pass-through | Entitlement models absent (WRAG/support absent). Large. |
| Income Support | `income_support*` | yes | amounts 2015-04-01 | raises | amounts look like later rates | Add 2010–2015 rates. Small to medium. |
| Housing Benefit / LHA | `housing_benefit*`, `LHA_*` | yes | allowances 2015; LHA max 2014; non-dep 2018 | raises | non-dep 2018 values in 2015–17 | Add keys; new working-age claims are impossible by design. Medium. |
| Bedroom tax | — | **no** | — | — | — | New rule (14% / 25%). Small to medium, needs bedrooms data *(unknown)*. |
| CTB (pre-2013) / CTR | `council_tax_benefit`, `council_tax_reduction*` | CTR yes | 2013-04-01 | 2010–2012 raise or absent | OK | National CTB for 2010–2012 absent. Medium. |
| Basic / additional / new SP | `basic_state_pension`, `additional_state_pension`, `new_state_pension`, `state_pension_type` | yes | BSP 2002; nSP 2016; triple lock 2011 | BSP OK; type → BASIC | OK | Reported-anchored; ASP scaled by flat-rate ratio, not accrual. Medium. |
| Pension Credit | `pension_credit*` | yes | guarantee 2015-04-06 | raises | OK | Add 2010–2014 guarantee and threshold keys. Small. |
| Benefit cap | `benefit_cap*` | yes | 2016-11-07 | raises | **£13,400 cap in 2015–16** | Add 2013-04-15 £26k / £18.2k keys *(external)*. Small. |
| Child Benefit | `child_benefit*` | yes | 2007-04-09 | OK (Jan-1 sampling) | OK | — |
| HICBC | `CB_HITC` | yes | 2015-06-05 | raises | OK | Add 2013-01-07 keys. Trivial. |
| DLA / PIP / AA / CA | `dla*`, `pip*`, `attendance_allowance`, `carers_allowance` | yes (input categories) | 2015-04-01 | raises | OK | Add 2010–2014 rates. The PIP rollout comes from data. Small. |
| Winter Fuel Payment | `winter_fuel_allowance` | yes, year branch ≥2024 | 2000-01-01 | OK | OK | — |
| Cost-of-living payments / EPG / EBSS | `cost_of_living_support_payment`, `epg_subsidy`, `energy_bills_*` | yes | 2022 | n/a | n/a | EPG sums calendar months, not fiscal. Small. |
| UC and managed migration | `universal_credit*`, `would_claim_uc` | yes; rollout no | 2013-04-29 / 2015 / 2016 | raises | UC computed whenever legacy is not reported | `rollout_rate` unused; UC/legacy allocation comes only from data. Large. |
| Dataset back-projection | `extend_single_year_dataset` | forward only | indices: CPI/AWE 2009; GDP etc. 2021; rents 2022 | inputs → 0 | n/a | Needs period-specific datasets (FRS 2010–) or back-casting code. Large. |

---

## Appendix: probe outputs

From `peuk_work/probe.log`, situation: one adult aged 40 earning £30,000 and one child aged 5.
- `sim_2010`, `sim_2012` and `sim_2014`: every output raised `ParameterNotFoundError`. Income tax, NI, Child Benefit
  and net income failed on `labour_supply_responses[income_elasticity]`. The PA failed on `personal_allowance[amount]`.
  Tax credits failed on `min_hours[couple_with_children]` (2010, 2012) and `dla.self_care[higher]` (2014). UC failed on
  `means_test.capital[sources]` (2010, 2012) and `carers_allowance[rate]` (2014).
- `sim_2015`: income tax 3,880.0; NI 2,632.80; Child Benefit 1,076.40; tax credits 0; UC 0; net income 24,416.55.
- `sim_2016`: identical to 2015, including income tax 3,880.0 from a PA of 10,600.
- `sim_2019`: income tax 3,500.0.

From `peuk_work/probe2.log` (428 s), situation simulations with no reported benefits:
- `lone_parent_2015` and `lone_parent_2016` (identical): a lone parent aged 30 earning £8,000 with children aged 4
  and 7. `universal_credit` 7,815.44; `child_tax_credit` 0; `working_tax_credit` 0; `tax_credits` 5,560 (the
  pre-minimum sum, before the reported-receipt gate in `ctc_entitlement` / `wtc_entitlement`); `income_support` 0;
  `benefit_cap_reduction` 0; `child_benefit` 1,788.80. In 2015 the model pays UC, not tax credits, to a family with no
  reported legacy award.
- `investor_2015` and `investor_2016` (identical): age 50; employment £60,000, dividends £10,000, savings interest
  £3,000, gains £50,000. `dividend_income_tax` 1,625 = (10,000 − 5,000 allowance) × 32.5%; `savings_allowance` 1,000;
  `savings_income_tax` 800; `capital_gains_tax` 7,660 = (50,000 − 11,700) × 20%; `personal_allowance` 10,600;
  `income_tax` 15,785. These show the 2016-or-later dividend regime, the 20% CGT rate and the 2018 AEA applied in 2015,
  and the PSA band misclassification from 2(d) item 9.
