# Policy experiment findings

Running log of the policy experiments on the modern population
([design](POLICY_EXPERIMENTS.md)). **These are policy experiments on the
modern population: not replays, and not PolicyEngine's costing of any past
event.** Each entry names the event, the population, what broke, the
diagnosis and the issue or PR it became.

## Populations

| Population | Model | Data | Status |
|---|---|---|---|
| `exp-pe6.10.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71` | policyengine-uk 2.132.6, policyengine.py 6.10.0 | Microcosm UK 2024-25 national cut `20261019T083323Z-6cba5d71` (the interim pair, policyengine.py#685) | certified pair; probed (data years 2024-2032) |
| `exp-pe6.10.0_uk2.143.0_on_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71` | policyengine-uk 2.143.0 (released 21 October), policyengine.py 6.10.0 | the same cut | model swap; probed |

The pre-Budget pair (María's cut on policyengine-uk 2.141.x) is added when it
is published. Against the model swap on the interim cut, it separates data
from model: the two then share a model family but not data.

## Leads from authoring the constructions

Read in the pe-uk 2.132.6 parameter files while writing the specs, before any
run. Each was checked against pe-uk main; neither is filed, because both are
already fixed there.

| Lead | 2.132.6 | Fixed on main | Experiments it touches |
|---|---|---|---|
| Dividend bands keep the £37,500 higher-rate and £150,000 additional-rate thresholds until April 2026, while the main bands are £37,700 and £125,140 | `rates/dividends.yaml` | 83de1ef1d "Correct historical dividend income tax band thresholds", first in 2.139.4 | `as2022_additional_rate_threshold_125140`, `ab2021_dividend_rates_plus_1_25pp` |
| Residential SDLT has no Growth Plan relief (£250,000 nil-rate band, £425,000 first-time buyers' threshold, 23 September 2022 to 31 March 2025) | `stamp_duty/residential/purchase/main/*` | 4044d6ccf "Fix recent residential SDLT purchase schedules and inclusive first-buyer caps" | `as2022_sdlt_nil_rate_bands_2024` (expected `construction_noop` on 2.132.6) |

## What broke

| Finding | Status | Experiment that caught it |
|---|---|---|
| **Setting the statutory Marriage Allowance rate switches on the CPS expanded Marriage Allowance reform.** The reform keeps the 10% rate and extends it to higher- and additional-rate taxpayers, so "remove the allowance" ran as "extend it": income tax fell £0.23bn where it should rise. A synthetic-couple reproduction on 2.143.0, with the rate set to 0: the basic-rate couple's allowance is unchanged, and the higher-rate couple gains £1,260 of allowance and £504 less tax. Present on main. | **filed: [PolicyEngine/policyengine-uk#2551](https://github.com/PolicyEngine/policyengine-uk/issues/2551)**, handed to the UK hub | `as2013_marriage_allowance` (`sign_mismatch`) |
| pe-uk 2.132.6's dividend bands keep £37,500 and £150,000 until April 2026 | fixed upstream in 2.139.4 (83de1ef1d); the model swap adds +£0.11bn to the additional-rate-threshold experiment in 2024-25 and 2025-26, and the dividend leg of the allowance freezes starts from £37,500 instead of £37,700 | `as2022_additional_rate_threshold_125140` (model change), `b2018_personal_allowance_12500_hrt_50000` and `sb2021_personal_allowance_hrt_freeze` (`modern_law_differs` on 2.132.6) |
| pe-uk 2.132.6 has no Growth Plan SDLT relief (23 September 2022 to 31 March 2025) | fixed upstream in 2.141.8 (4044d6ccf); the 2024-25 experiment goes from 0 (2.132.6) to −£1.234bn (2.143.0) against the OBR's −£1.048bn | `as2022_sdlt_nil_rate_bands_2024` (`construction_noop`, then model change) |
| pe-uk 2.132.6's additional-dwellings SDLT scale lacks Autumn Budget 2024's further 2pp (from 31 October 2024), so the surcharge reversal removes 1pp, not 3pp | fixed upstream in 2.141.8 (4044d6ccf, the same commit as the Growth Plan relief); caught by the first review, now flagged `modern_law_differs` | `as2015_sdlt_additional_dwellings_surcharge` |
| pe-uk 2.132.6 charges every home buyer's whole stock of other residential property as one additional-dwelling purchase at the higher rates, so its modern-law SDLT (£15.0bn in 2025-26) is overstated; its £0.94bn for the surcharge is a 1pp removal on that base, so not a comparison with the OBR | fixed upstream in 2.134.1 (52030637b, #2238). From then the purchase price is a dataset input: the interim cut lacks it, so on 2.143.0 SDLT is £8.1bn and the surcharge reversal is `inert`. Microcosm imputes it from #1308, so the pre-Budget cut carries it | `as2015_sdlt_additional_dwellings_surcharge` (model change, then `inert` on the swap) |

**A model swap is valid only where the data carries the newer model's
inputs.** Three variables the 2.132.6 model computed became dataset inputs by
2.143.0, and the interim cut carries none of them: the additional-dwelling and
non-residential purchase prices, and salary sacrifice returned to income. On
the swap each is nil for every record (`model_swap_input_gaps` on the
population record). The pre-Budget pair has no such gap for the first two.

The 2.132.6 currency gaps confirm the brief's point: the interim pair's model
is about 630 commits behind main, and only the newest model catches current
bugs. Every anomaly on the interim pair was therefore checked against
2.143.0 before anything was filed.

## Diagnosed, not bugs

| Flag | Diagnosis |
|---|---|
| Budget 2017's Class 4 rise, `magnitude_outside_3x` (5.48 and 3.17) | The OBR's costing is net of the self-employed incorporating: its NICs yield falls from £570m to £475m while income tax goes from −£60m to −£420m and corporation tax rises to +£340m. A static run has no such response. PolicyEngine's NICs leg alone is 1.27 times the OBR's NICs row scaled to the modern base. |
| Budget 2016's trading and property allowances, `magnitude_outside_3x` (0.20) | Without gross receipts, pe-uk relieves only profits within the £1,000 allowance and takes larger profits as already netting the better of expenses and the allowance. Neither data line (Microcosm UK 2024-25 or policyengine-uk-data's enhanced FRS 2024-25) carries `self_employment_gross_receipts`, so the partial relief the OBR costed has nothing to act on. *Data note for María:* an imputed gross-receipts column would let this leg move. |
| Budget 2012's 45p additional rate, `magnitude_outside_10x` (39.5) | The OBR's −£110m is net of a taxable-income response that offsets almost all of the static cost; a static run has none. Restoring 50% costs £6.3bn statically on the modern population. The flag is the screen working as designed on a measure costed behaviourally. |
| Eight `construction_noop` notes in Autumn Statement 2022 | The employer threshold freeze is superseded by Autumn Budget 2024's £5,000. The Growth Plan SDLT relief ended in March 2025. Ending that relief changes nothing until 2025-26. On 2.132.6 only, the relief is missing altogether (above). |

## Clean

These experiments returned the OBR's sign. Where magnitudes are checked,
their scaled ratios fall inside the bands.

| Event | Experiment | Scaled ratio by year (PE / OBR × scale) |
|---|---|---|
| Autumn Statement 2022 | reverse the 1.25pp NICs rise and the levy | 1.00, 0.90, 0.91, 0.92 |
| | keep the basic rate at 20% | 1.05, 0.95, 0.99, 1.00 |
| | additional-rate threshold £125,140 | 1.00, 1.10, 1.24, 1.24 (2.143.0: 1.13, 1.24, 1.22, 1.22; 2.132.6 has no dividend leg until April 2026) |
| | dividend allowance £500 | 0.91, 0.52, 0.55, 0.52 (OBR cash lags a year) |
| | CGT allowance £3,000 | 2.25, 1.46, 1.44, 1.52 (OBR cash lags a year) |
| | benefit cap uprating | 1.05, 1.21, 1.62, 1.68 |
| | employer threshold freeze (2024-25) | 0.69 |
| | end the Growth Plan SDLT relief | 1.36, 0.88, 0.83 |
| Autumn Budget 2021 | Health and Social Care Levy | 1.00, 0.90, 0.91 |
| | dividend rates +1.25pp | 1.16, 0.99, 0.92 |
| | UC taper 55% and £500 work allowance | 0.98, 0.88, 0.84 |
| | double lock 2022-23 | 1.09, 1.08, 1.05 |
| | fuel duty freeze 2022-23 | 0.55, 0.54 |
| Spring Statement 2022 | basic rate 19% | 1.14, 1.04, 1.09 |
| | basic rate 19%, welfare row | 1.40, 1.15, 1.21 |
| | primary threshold and LPL alignment (sign only) | 0.42, 0.32, 0.31 (outturn CPI and the modern 8% rate against 13.25% then) |
| | the same, welfare row (sign only) | 0.39, 0.26, 0.25 |
| Spring Budget 2021 | allowance and threshold freeze (sign only) | 3.82, 3.18 (outturn inflation far above the March 2021 forecast) |
| | fuel duty freeze 2021-22 | 0.48, 0.47 |
| Spending Review 2020 | pension credit guarantee uprating | 0.76, 0.72 |
| Budget 2020 | fuel duty freeze 2020-21 | 0.71 |
| Budget 2018 | £12,500 allowance and £50,000 threshold a year early | 1.39, 1.46 (2.143.0: 1.42, 1.49) |
| | UC £1,000 work allowance increase | 0.58, 0.56 |
| | fuel duty freeze 2019-20 | 0.62, 0.61 |
| Autumn Budget 2017 | first-time buyers' SDLT relief | 1.31, 1.19 |
| | fuel duty freeze 2018-19 | 0.66, 0.65 |
| Autumn Statement 2016 | fuel duty freeze 2017-18 | 0.61, 0.60 |
| Budget 2016 | fuel duty freeze 2016 | 0.64, 0.63 |
| Budget 2015 | personal savings allowance | 0.43, 0.45 |
| Summer Budget 2015 | two-child limit (sign only) | 0.90, 0.94 |
| | working-age benefit freeze (scaled amounts) | 0.68, 0.65 |
| | 30-hour childcare entitlement (ages 3 and 4) | 1.38, 1.40 |
| Autumn Statement 2012 | Universal Credit at 1% (scaled amounts) | 0.51, 0.50 |
| | child benefit at 1% (scaled amounts) | 0.51, 0.49 |
| Autumn Statement 2010 | high-income child benefit charge | 0.58, 0.61 |
| Budget 2010 | VAT at 20% | 1.31, 1.31 |
| | child benefit three-year freeze | 0.91, 0.86 |

The fuel-duty ratios near 0.5–0.7 are expected: pe-uk's fuel duty is
household car fuel only, while the OBR's base includes business and haulage
fuel. Events before 2021 compare with their last costing year, carried
forward (`carried_from_fy`).

**Mirrors.** The Health and Social Care Levy (AB2021) and its reversal
(AS2022) return exact negatives in every year and head group, from separate
Modal containers, and so do Spring Statement 2022's 19% basic rate and
Autumn Statement 2022's 20%. Determinism and the symmetry of the reform route
both hold.

**The population.** PolicyEngine's modern income tax base is 0.94 to 0.98
of the OBR's March 2026 forecast, and NICs 1.01 to 1.05. Capital gains tax is
1.69 in 2024-25, but that compares liabilities with cash receipts, which lag
disposals by about a year; against the OBR's 2025-26 cash forecast (£21.8bn)
the 2024-25 liability (£23.1bn) is 1.06.

## Corrections from the first review

An Opus 5.5 review of the harness at `bb445279` found four constructions
wrong on their own premises. Each is corrected, and its event rerun on both
populations:

- **The additional-dwellings surcharge removed 1pp, not 3pp, on 2.132.6.**
  The counterfactual (2/4/7/12/14%) was written against modern law with
  Autumn Budget 2024's further 2pp, which 2.132.6 lacks (3/5/8/13/15%). Its
  earlier "0.96, clean" compared a 1pp removal with the OBR's 3pp. Specs now
  state the current law they assume (`assumes_modern`), and an engine whose
  processed value differs gets `modern_law_differs`.
- **Spring Statement 2022's primary threshold.** No law ever set an
  unaligned threshold after 2022-23, so its path without the alignment has
  more than one defensible reading: CPI uprating to April 2025, then
  Autumn Statement 2022's hold ("maintain thresholds at 2023-24 levels until
  April 2028") from April 2026; one uprating in April 2023, then the hold;
  or no uprating after 2022-23. The construction had the second. It now has
  the first (£11,607, then £11,804), as the file's Spring Budget 2021
  counterfactual indexes the allowance through 2025-26. The yield depends on
  that reading and on outturn inflation since the event, so both
  experiments are now sign only.
- **Budget 2018's work allowance** removed the April 2019 uprating with the
  £1,000 measure. Without the measure the allowances would have been £203
  and £419 a month (the 2018 levels uprated by 2.4%), not £198 and £409.
- **The 30-hour childcare entitlement** zeroed only the age-3 bracket; it now
  zeroes the age-4 bracket too.

## Harness fixes the runs forced

- **Fuel duty in cash.** The 2022 5p cut was a cash cut, so a removed
  freeze's counterfactual is 57.95p × (1 + RPI) − 5p, not 52.95p × (1 + RPI).
  Autumn Budget 2021 was rerun on the corrected spec.
- **The mapped share by head.** Offsetting mapped heads (an incorporation
  response's NICs gain against its income tax loss) hid Budget 2017's flag
  from the magnitude check. The share now counts each head's absolute value.
- **Mirrors by shared head group.** Mirrors map different head groups (AS2022's
  reversal also maps Universal Credit), so they compare only the groups both
  map.
- **Current law the construction assumes** (above): `modern_law_differs`.
  A test compares the two engines' current law on every parameter a
  construction sets, in every year it sets it: 248 parameter-years, of which
  the engines differ on 21. Each of the 21 is either declared in
  `assumes_modern` (16) or set outright whatever the engine's law (5: Budget
  2017's zero first-time-buyer limit and Autumn Statement 2022's 2024-25
  pre-relief schedule).
- **Integrity of the committed results** (from the review). `findings` refuses
  a run on another spec; `adopt` checks every download before copying any; a
  test regenerates every committed `FINDINGS` and `SUMMARY` file byte for
  byte; no output path may enter a replay root of any checkout.

## Runs

Each simulation runs on Modal: about 30 seconds for modern law and 50 seconds
for each alternate world. Per-event detail is in each event's `FINDINGS.md`
under `results/uk/experiments/<population>/<event>/`, and each population's
`SUMMARY.md` collects the anomaly counts, mirrors, population check and (for
the model swap) every model change against the certified pair.
