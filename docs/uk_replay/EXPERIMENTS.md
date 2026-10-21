# Policy experiment findings

Running log of the policy experiments on the modern population
([design](POLICY_EXPERIMENTS.md)). **These are policy experiments on the
modern population: not replays, and not PolicyEngine's costing of any past
event.** Each entry names the event, the population, what broke, the
diagnosis and the issue or PR it became.

## Populations

| Population | Model | Data | Status |
|---|---|---|---|
| `exp-pe6.10.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71` | policyengine-uk 2.132.6, policyengine.py 6.10.0 | Microcosm UK 2024-25 national cut `20261019T083323Z-6cba5d71` (the interim pair, policyengine.py#685) | probing |

## Leads from authoring the constructions

Read in the pe-uk 2.132.6 parameter files while writing the specs, before any
run. Each was checked against pe-uk main; neither is filed, because both are
already fixed there.

| Lead | 2.132.6 | Fixed on main | Experiments it touches |
|---|---|---|---|
| Dividend bands keep the £37,500 higher-rate and £150,000 additional-rate thresholds until April 2026, while the main bands are £37,700 and £125,140 | `rates/dividends.yaml` | 83de1ef1d "Correct historical dividend income tax band thresholds", first in 2.139.4 | `as2022_additional_rate_threshold_125140`, `ab2021_dividend_rates_plus_1_25pp` |
| Residential SDLT has no Growth Plan relief (£250,000 nil-rate band, £425,000 first-time buyers' threshold, 23 September 2022 to 31 March 2025) | `stamp_duty/residential/purchase/main/*` | 4044d6ccf "Fix recent residential SDLT purchase schedules and inclusive first-buyer caps" | `as2022_sdlt_nil_rate_bands_2024` (expected `construction_noop` on 2.132.6) |

## Runs

None yet.
