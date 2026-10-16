# Release diff: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1` → `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`

Movements of the event replay between two certified releases. Flags are investigation prompts, not verdicts; ratio bins are descriptive.

A numerical flag means the move exceeds max(£1m, 1% of the larger magnitude). Structural, coverage, mapping, support, inertness and construction flags are raised regardless of size. A year supported on one side only is a support flag, not coverage.

## Executions

| Field | Base | Head |
|---|---|---|
| certified_dataset_sha256 | `056e80fd8e9151d78f432a25cde863340baee81304c6216a37fb575ce8563784` | `056e80fd8e9151d78f432a25cde863340baee81304c6216a37fb575ce8563784` |
| data_bundle | `policyengine-uk-data-1.58.1` | `policyengine-uk-data-1.58.1` |
| policyengine_core_version | `3.33.0` | `3.33.0` |
| policyengine_uk_version | `2.130.1` | `2.130.1` |
| policyengine_version | `6.4.1` | `6.5.0` |
| variant_id | `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1` | `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1` |

Construction premises compared: base `59504b1dce718a92b441f71e254fad225c4f50030407d0ad8e2711b8e78a6296`, head `cb587ba5f065d00e191bf3c51883bf07a9c101b59b5a6419c1a3760c3170857e`.

## Flags by event

| Event | Supported years (base → head) | numerical | structural | coverage | mapping | support | inertness | construction |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| autumn_budget_2024 | 2024–2029 → 2024–2029 | 3 | 0 | 0 | 0 | 0 | 0 | 6 |
| autumn_budget_2025 | 2025–2030 → 2025–2030 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| autumn_statement_2023 | 2024–2028 → 2024–2028 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| spring_budget_2023 | 2024–2027 → 2024–2027 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| spring_budget_2024 | 2024–2028 → 2024–2028 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| spring_statement_2025 | 2024–2029 → 2024–2029 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| **all** | | 3 | 0 | 0 | 0 | 0 | 0 | 6 |

## Flagged movements

Showing 8 of 8 rows with a flag other than support, rows without a numerical change first, then by absolute change. £m, positive = gain to the Exchequer.

| Event | Measure | CY | Level | Key | Base | Head | Change | Flags |
|---|---|---:|---|---|---:|---:|---:|---|
| autumn_budget_2024 | capital_gains_main_rates_and_reliefs | 2024 | source_row | obr_pmd_nov2025:11682:73295721bdfdb9e8 | 575.0 | 956.3 | 381.3 | numerical |
| autumn_budget_2024 | capital_gains_main_rates_and_reliefs | 2024 | measure_year | total | 575.0 | 956.3 | 381.3 | numerical, construction |
| autumn_budget_2024 | capital_gains_main_rates_and_reliefs | 2024 | head | capital_gains_tax | 575.0 | 956.3 | 381.3 | numerical |
| autumn_budget_2024 | capital_gains_main_rates_and_reliefs | 2025 | measure_year | total | 2,321.6 | 2,321.6 | 0.0 | construction |
| autumn_budget_2024 | capital_gains_main_rates_and_reliefs | 2026 | measure_year | total | 2,397.9 | 2,397.9 | 0.0 | construction |
| autumn_budget_2024 | capital_gains_main_rates_and_reliefs | 2027 | measure_year | total | 2,484.7 | 2,484.7 | 0.0 | construction |
| autumn_budget_2024 | capital_gains_main_rates_and_reliefs | 2028 | measure_year | total | 2,572.4 | 2,572.4 | 0.0 | construction |
| autumn_budget_2024 | capital_gains_main_rates_and_reliefs | 2029 | measure_year | total | 2,660.3 | 2,660.3 | 0.0 | construction |

## Years supported on one side only

Each has a packet; the population of one release cannot supply the year.

| Event | CY | Level | Rows |
|---|---:|---|---:|
| none | | | |

## PE/OBR ratio-bin transitions (source rows on both sides)

### autumn_budget_2024

| Base bin | Head bin | Rows |
|---|---|---:|
| both_zero | both_zero | 2 |
| not_available | not_available | 1100 |
| obr_zero | obr_zero | 1 |
| opposite_sign | opposite_sign | 2 |
| same_sign_ratio_0.8_to_1.25 | same_sign_ratio_0.8_to_1.25 | 6 |
| same_sign_ratio_1.25_to_2 | same_sign_ratio_1.25_to_2 | 5 |
| same_sign_ratio_at_least_2 | same_sign_ratio_at_least_2 | 13 |
| same_sign_ratio_below_0.5 | same_sign_ratio_below_0.5 | 5 |

### autumn_budget_2025

| Base bin | Head bin | Rows |
|---|---|---:|
| both_zero | both_zero | 28 |
| not_available | not_available | 1422 |
| obr_zero | obr_zero | 1 |
| opposite_sign | opposite_sign | 1 |
| pe_zero | pe_zero | 19 |
| same_sign_ratio_0.5_to_0.8 | same_sign_ratio_0.5_to_0.8 | 10 |
| same_sign_ratio_0.8_to_1.25 | same_sign_ratio_0.8_to_1.25 | 16 |
| same_sign_ratio_1.25_to_2 | same_sign_ratio_1.25_to_2 | 8 |
| same_sign_ratio_at_least_2 | same_sign_ratio_at_least_2 | 6 |
| same_sign_ratio_below_0.5 | same_sign_ratio_below_0.5 | 1 |

### autumn_statement_2023

| Base bin | Head bin | Rows |
|---|---|---:|
| both_zero | both_zero | 2 |
| not_available | not_available | 1066 |
| pe_zero | pe_zero | 13 |
| same_sign_ratio_0.8_to_1.25 | same_sign_ratio_0.8_to_1.25 | 7 |
| same_sign_ratio_1.25_to_2 | same_sign_ratio_1.25_to_2 | 17 |
| same_sign_ratio_at_least_2 | same_sign_ratio_at_least_2 | 11 |

### spring_budget_2023

| Base bin | Head bin | Rows |
|---|---|---:|
| not_available | not_available | 1008 |
| pe_zero | pe_zero | 4 |
| same_sign_ratio_at_least_2 | same_sign_ratio_at_least_2 | 8 |

### spring_budget_2024

| Base bin | Head bin | Rows |
|---|---|---:|
| both_zero | both_zero | 2 |
| not_available | not_available | 776 |
| pe_zero | pe_zero | 8 |
| same_sign_ratio_0.5_to_0.8 | same_sign_ratio_0.5_to_0.8 | 4 |
| same_sign_ratio_0.8_to_1.25 | same_sign_ratio_0.8_to_1.25 | 11 |
| same_sign_ratio_1.25_to_2 | same_sign_ratio_1.25_to_2 | 4 |
| same_sign_ratio_at_least_2 | same_sign_ratio_at_least_2 | 11 |

### spring_statement_2025

| Base bin | Head bin | Rows |
|---|---|---:|
| both_zero | both_zero | 4 |
| not_available | not_available | 486 |
| same_sign_ratio_0.5_to_0.8 | same_sign_ratio_0.5_to_0.8 | 3 |
| same_sign_ratio_0.8_to_1.25 | same_sign_ratio_0.8_to_1.25 | 2 |
| same_sign_ratio_below_0.5 | same_sign_ratio_below_0.5 | 3 |

## Investigation packets

* [autumn_budget_2024__capital_gains_main_rates_and_reliefs__2024](packets/autumn_budget_2024__capital_gains_main_rates_and_reliefs__2024.md)
* [autumn_budget_2024__capital_gains_main_rates_and_reliefs__2025](packets/autumn_budget_2024__capital_gains_main_rates_and_reliefs__2025.md)
* [autumn_budget_2024__capital_gains_main_rates_and_reliefs__2026](packets/autumn_budget_2024__capital_gains_main_rates_and_reliefs__2026.md)
* [autumn_budget_2024__capital_gains_main_rates_and_reliefs__2027](packets/autumn_budget_2024__capital_gains_main_rates_and_reliefs__2027.md)
* [autumn_budget_2024__capital_gains_main_rates_and_reliefs__2028](packets/autumn_budget_2024__capital_gains_main_rates_and_reliefs__2028.md)
* [autumn_budget_2024__capital_gains_main_rates_and_reliefs__2029](packets/autumn_budget_2024__capital_gains_main_rates_and_reliefs__2029.md)
