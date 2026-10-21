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

## Runs

Each simulation runs on Modal: about 30 seconds for modern law and 50 seconds
for each alternate world, so an event's grid takes 15 to 35 minutes.

### Autumn Statement 2022, interim pair

36 experiment-years, nine experiments, FY 2024-25 to 2027-28
([FINDINGS](../../results/uk/experiments/exp-pe6.10.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_statement_2022/FINDINGS.md)).
No investigate-level anomaly. Every computed scaled ratio lies between 0.52
and 2.25:

| Experiment | 2024-25 PE / OBR mapped (£bn) | Scaled ratio, 2024-25 to 2027-28 |
|---|---|---|
| Reverse the 1.25pp NICs rise and the levy | −16.25 / −16.21 | 1.00, 0.90, 0.91, 0.92 |
| Keep the basic rate at 20% | +6.25 / +5.52 | 1.05, 0.95, 0.99, 1.00 |
| Additional-rate threshold £125,140 | +0.85 / +0.79 | 1.00, 1.10, 1.24, 1.24 |
| Dividend allowance £500 | +0.51 / +0.52 | 0.91, 0.52, 0.55, 0.52 |
| CGT annual exempt amount £3,000 | +0.83 / +0.28 | 2.25, 1.46, 1.44, 1.52 |
| Benefit cap uprating | −0.27 / −0.24 | 1.05, 1.21, 1.62, 1.68 |
| Employer secondary threshold freeze | +3.67 / +5.31 | 0.69 (later years superseded) |
| End the Growth Plan SDLT relief | 0 / +0.20 | 1.36, 0.88, 0.83 from 2025-26 |

The dividend allowance's later ratios near 0.5 and the CGT allowance's 2.25
in 2024-25 fit the OBR's cash timing (self-assessment receipts lag a year)
against PolicyEngine's liabilities. They are inside the bands and not
flagged.

All eight `construction_noop` notes are diagnosed
([diagnoses](../../data/uk/experiments/diagnoses.json)). One is a model
finding: **pe-uk 2.132.6 has no Growth Plan SDLT relief**, so its 2024-25
SDLT is the pre-relief schedule. That is already fixed in 2.141.8
(4044d6ccf): on 2.143.0 the same experiment is −£1.234bn in 2024-25 against the OBR's −£1.048bn.

**The dividend-band lead, confirmed by a run.** On 2.132.6 the
additional-rate-threshold reversal leaves dividend income untouched in
2024-25 and 2025-26, because 2.132.6's dividend additional threshold is
already £150,000. On 2.143.0 the same experiment is +£0.959bn in 2024-25
against +£0.853bn, the difference being the dividend band. Fixed in 2.139.4
(83de1ef1d).

**The population.** PolicyEngine's modern income tax base is 0.94 to 0.98
of the OBR's March 2026 forecast, and NICs 1.01 to 1.05. Capital gains tax is
1.69 in 2024-25, but that compares liabilities with cash receipts, which lag
disposals by about a year; against the OBR's 2025-26 cash forecast (£21.8bn)
the 2024-25 liability (£23.1bn) is 1.06.
