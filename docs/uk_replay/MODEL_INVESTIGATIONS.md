# Measured UK replay model investigation candidates

These small reproductions inspect policyengine-uk 2.89.2. They identify specific encoding or parameter concerns, independently of the national OBR differences. Their national effect is unsized; no issue has been filed. These are model investigation candidates, not ten sized explanations of national differences.

An [integrated execution receipt](../../results/uk/events/MODEL_DIAGNOSTICS_VERIFICATION.json) binds the [preserved fresh output](../../results/uk/events/diagnostics/integrated_run_20261009.json) to these observations. The Class 4 primary citation was added afterward; the receipt distinguishes that metadata addition from engine results.

## carers_allowance_earnings_test_absent

Class: `pe_gap`. Variables: `carers_allowance`.

The formula uses care hours or reported receipt and no earnings test. The AB2024 earnings-limit increase cannot be represented by this formula. This is an encoding gap, not a sized explanation of the national costing.

Evidence: `variables/gov/dwp/carers_allowance.py`; source SHA-256 `92657ce086a44f8fc7c1991167b23c9e088e53a5ae32163d4f46fb5ebda7db5a`. Full source and measured observations are retained in `results/uk/events/MODEL_DIAGNOSTICS.json`.

```bash
PYTHONPATH=. .venv-replay/bin/python pipeline/diagnose_uk_event_models.py --case carers_allowance_earnings_test_absent
```

Observed:

```json
{
 "annual_carers_allowance_gbp": [
  4331.080078125,
  4331.080078125
 ],
 "annual_earnings_gbp": [
  0,
  100000
 ],
 "care_hours_weekly": [
  35,
  35
 ],
 "earnings_limit_parameter_names": [
  "min_hours",
  "rate"
 ]
}
```

## cgt_main_rate_commencement

Class: `pe_gap`. Variables: `capital_gains_tax`.

The harvested AB2024 title specifies 30 October 2024, while the raw main-rate schedule starts 6 April 2025. CountryTaxBenefitSystem annualizes government policy from the 30 April snapshot. The first higher processed year, 2025, is inferred from that conversion rule and the recorded April 2025 values. This records a missing part-year 2024 commencement, not an additional delay to 2026. The parameter description also warns that it is under active development. The national timing contribution remains unsized.

Evidence: `parameters/gov/hmrc/cgt/basic_rate.yaml`; source SHA-256 `0a1896eb3f2007ca95811765e8eabcf526af7831897a5d105d8b18c6c9fe58ed`. Full source and measured observations are retained in `results/uk/events/MODEL_DIAGNOSTICS.json`.

```bash
PYTHONPATH=. .venv-replay/bin/python pipeline/diagnose_uk_event_models.py --case cgt_main_rate_commencement
```

Observed:

```json
{
 "2024-10-29": {
  "additional": 0.2,
  "basic": 0.1,
  "higher": 0.2
 },
 "2024-10-30": {
  "additional": 0.2,
  "basic": 0.1,
  "higher": 0.2
 },
 "2025-04-06": {
  "additional": 0.24,
  "basic": 0.18,
  "higher": 0.24
 }
}
```

## sdlt_additional_home_hike_absent

Class: `pe_gap`. Variables: `sdlt_on_residential_property_transactions`, `stamp_duty_land_tax`.

The source title raises HRAD from 3% to 5% on 31 October 2024. The pinned additional-home scale still has rates 3/5/8/13/15% at these dates. A forward +2pp construction models this missing announced change; it is not a reversal already present in certified law.

Evidence: `parameters/gov/hmrc/stamp_duty/residential/purchase/additional/rate.yaml`; source SHA-256 `0467640e77930ae05b3f923d8ed85eb37f634200e225a49766ec971785c48fb6`. Full source and measured observations are retained in `results/uk/events/MODEL_DIAGNOSTICS.json`.

```bash
PYTHONPATH=. .venv-replay/bin/python pipeline/diagnose_uk_event_models.py --case sdlt_additional_home_hike_absent
```

Observed:

```json
{
 "2024-10-30": [
  0.03,
  0.05,
  0.08,
  0.13,
  0.15
 ],
 "2024-10-31": [
  0.03,
  0.05,
  0.08,
  0.13,
  0.15
 ],
 "2025-04-06": [
  0.03,
  0.05,
  0.08,
  0.13,
  0.15
 ],
 "2026-06-01": [
  0.03,
  0.05,
  0.08,
  0.13,
  0.15
 ]
}
```

## private_school_vat_current_law_lever_zero

Class: `pe_gap`. Variables: `private_school_vat`.

The harvested AB2024 title applies 20% VAT to private-school education and boarding from January 2025. The pinned private-school VAT lever remains zero. The replay therefore executes a forward 20% construction; its imputed fees, attendance and omitted input-VAT recovery remain separate unsized scope limitations.

Evidence: `parameters/gov/contrib/labour/private_school_vat.yaml`; source SHA-256 `d108161e9d328757f935e0149c27fb06ead467d2e16f359a4b79ff65b8c26633`. Full source and measured observations are retained in `results/uk/events/MODEL_DIAGNOSTICS.json`.

```bash
PYTHONPATH=. .venv-replay/bin/python pipeline/diagnose_uk_event_models.py --case private_school_vat_current_law_lever_zero
```

Observed:

```json
{
 "2025-01-01": 0,
 "2025-06-01": 0,
 "2026-06-01": 0
}
```

## dividend_band_threshold_lag

Class: `pe_gap`. Variables: `dividend_income_tax`, `income_tax`.

The existing mode-2 registry records the dividend thresholds lagging the main bands until April 2026. Their effect on a specific NICs costing's Income Tax interaction is unsized, so the national gap remains open.

Evidence: `parameters/gov/hmrc/income_tax/rates/dividends.yaml`; source SHA-256 `d3bcbc7fec39442b8313401c9c84f9fe7d704abf070e9a91a4d01478b54f8244`. Full source and measured observations are retained in `results/uk/events/MODEL_DIAGNOSTICS.json`.

```bash
PYTHONPATH=. .venv-replay/bin/python pipeline/diagnose_uk_event_models.py --case dividend_band_threshold_lag
```

Observed:

```json
{
 "2024-06-01": {
  "dividend_additional_threshold": 150000,
  "dividend_higher_threshold": 37500,
  "uk_additional_threshold": 125140,
  "uk_higher_threshold": 37700
 },
 "2025-06-01": {
  "dividend_additional_threshold": 150000,
  "dividend_higher_threshold": 37500,
  "uk_additional_threshold": 125140,
  "uk_higher_threshold": 37700
 },
 "2026-06-01": {
  "dividend_additional_threshold": 125140,
  "dividend_higher_threshold": 37700,
  "uk_additional_threshold": 125140,
  "uk_higher_threshold": 37700
 }
}
```

## class4_threshold_indexation_from_2027

Class: `pe_gap`. Variables: `ni_class_4`.

The existing AB2025 baseline integrity assessment states the prior-law Class 4 freeze runs to April 2028 while the pin resumes uprating in April 2027. This changes the marginal tax base in 2027; no fraction of a replay gap is attributed without a paired run.

Evidence: `parameters/gov/hmrc/national_insurance/class_4/thresholds/lower_profits_limit.yaml`; source SHA-256 `22412335d15673fd57fe56d9a9989675c02cc3ed64fce33ca3b57f6906d90dd5`. Full source and measured observations are retained in `results/uk/events/MODEL_DIAGNOSTICS.json`.

Primary rule (checked 2026-10-09): The Class 4 Lower Profits Limit of £12,570 and Upper Profits Limit of £50,270 were frozen until April 2028. [Autumn Statement 2022 tax section](https://www.gov.uk/government/publications/autumn-statement-2022-documents/autumn-statement-2022-html).

```bash
PYTHONPATH=. .venv-replay/bin/python pipeline/diagnose_uk_event_models.py --case class4_threshold_indexation_from_2027
```

Observed:

```json
{
 "2026-06-01": {
  "lower_profits_limit": 12570,
  "upper_profits_limit": 50270
 },
 "2027-06-01": {
  "lower_profits_limit": 12821.380164235901,
  "upper_profits_limit": 51275.32067272385
 },
 "2028-06-01": {
  "lower_profits_limit": 13077.795560896562,
  "upper_profits_limit": 52300.77826939301
 }
}
```

## uc_lcwra_protection_stops_at_2030

Class: `investigation`. Variables: `uc_LCWRA_element`.

The default Simulation constructor executes a deterministic UC modifier. It protects seeded existing claimants for 2026–2029, so inspecting uc_LCWRA_element alone would incorrectly claim all claimants are halved. The modifier loops over range(2026,2030), leaving CY2030 outside that protection override. The synthetic observation isolates the cutoff; continued-protection policy scope requires review before calling it an encoding defect.

Evidence: `scenarios/uc_reform.py`; source SHA-256 `5f139b8af2579099d1842c86ad5c4de8fc1984d6adb77ed9ce25dbfebd4e9eec`. Full source and measured observations are retained in `results/uk/events/MODEL_DIAGNOSTICS.json`.

```bash
PYTHONPATH=. .venv-replay/bin/python pipeline/diagnose_uk_event_models.py --case uc_lcwra_protection_stops_at_2030
```

Observed:

```json
{
 "annual_synthetic_lcwra_element": {
  "2029": [
   5447.29150390625
  ],
  "2030": [
   2830.311279296875
  ]
 },
 "formula_source": "    def formula(benunit, period, parameters):\n        p = parameters(period).gov.dwp.universal_credit.elements.disabled\n        limited_capability = benunit.members(\"uc_limited_capability_for_WRA\", period)\n        person_amounts = limited_capability * p.amount\n        return benunit.sum(person_amounts) * MONTHS_IN_YEAR\n",
 "monthly_disabled_element": {
  "2025-06-01": 423.27,
  "2026-06-01": 217.26,
  "2030-06-01": 235.85927653841142
 }
}
```

## employer_nics_state_pension_age_exemption

Class: `pe_gap`. Variables: `ni_liable`, `ni_class_1_employer`, `ni_class_1_employee`.

The employer formula uses the same ni_liable age mask as employee contributions. For otherwise identical £50,000 earnings, employer NICs falls to zero at age 70. HMRC states employer contributions continue after State Pension age. This is an employer-liability encoding concern; its national contribution to the NICs replay difference remains unsized.

Evidence: `variables/gov/hmrc/national_insurance/class_1/ni_class_1_employer.py`; source SHA-256 `1327631826a869fbaa5f236ad7089e7dea6254c0d9502e2a10d344e308478008`. Full source and measured observations are retained in `results/uk/events/MODEL_DIAGNOSTICS.json`.

Primary rule (checked 2026-10-09): Employers continue paying National Insurance after employees reach State Pension age. [HMRC guidance](https://www.gov.uk/employee-reaches-state-pension-age).

```bash
PYTHONPATH=. .venv-replay/bin/python pipeline/diagnose_uk_event_models.py --case employer_nics_state_pension_age_exemption
```

Observed:

```json
{
 "ni_class_1_employee": [
  2994.4033203125,
  0.0
 ],
 "ni_class_1_employer": [
  6751.2001953125,
  0.0
 ],
 "ni_liable": [
  true,
  false
 ]
}
```

## pension_taper_omits_employer_contributions

Class: `pe_gap`. Variables: `adjusted_net_income`, `pension_annual_allowance`.

The pension taper uses adjusted_net_income, which excludes employer pension contributions, and omits the separate threshold-income gate. With £240,000 salary and £50,000 employer contributions it returns the full £60,000 allowance. HMRC's adjusted-income rule gives £290,000 and a £45,000 allowance for this controlled case. The national contribution to pension or Income Tax costing differences remains unsized.

Evidence: `variables/gov/hmrc/income_tax/allowances/pension_annual_allowance.py`; source SHA-256 `086e8e8b7da2d5c8693e9f6ce5cb67d6535fbac9b9c619adbe3bab872bad78c2`. Full source and measured observations are retained in `results/uk/events/MODEL_DIAGNOSTICS.json`.

Primary rule (checked 2026-10-09): Threshold income must exceed £200,000, and adjusted income adds employer pension contributions; the taper starts above £260,000. [HMRC guidance](https://www.gov.uk/guidance/pension-schemes-work-out-your-tapered-annual-allowance).

```bash
PYTHONPATH=. .venv-replay/bin/python pipeline/diagnose_uk_event_models.py --case pension_taper_omits_employer_contributions
```

Observed:

```json
{
 "adjusted_net_income": [
  240000.0
 ],
 "pension_annual_allowance": [
  60000.0
 ]
}
```

## annual_allowance_charge_single_marginal_rate

Class: `pe_gap`. Variables: `personal_pension_contributions_tax`.

The annual-allowance charge applies one marginal rate at taxed_income to the entire excess. Controlled intermediate inputs of £30,000 taxed income and £20,000 excess produce £4,000. HMRC's band-crossing rule gives £6,460 (£7,700 at 20% and £12,300 at 40%). Intermediate overrides isolate this formula rather than claim a complete household contribution history. The national contribution remains unsized.

Evidence: `variables/gov/hmrc/pensions/private_pension_contributions_tax.py`; source SHA-256 `eb27b9fc08eb6a6db2d12ea6b7b3e41e620687caa723bb5f9cb0f93661cfdae3`. Full source and measured observations are retained in `results/uk/events/MODEL_DIAGNOSTICS.json`.

Primary rule (checked 2026-10-09): The annual-allowance charge uses the rates that apply if the excess is added to taxable income, including bands crossed by that excess. [HMRC guidance](https://www.gov.uk/hmrc-internal-manuals/pensions-tax-manual/ptm056110).

```bash
PYTHONPATH=. .venv-replay/bin/python pipeline/diagnose_uk_event_models.py --case annual_allowance_charge_single_marginal_rate
```

Observed:

```json
{
 "personal_pension_contributions_tax": [
  4000.0
 ]
}
```
