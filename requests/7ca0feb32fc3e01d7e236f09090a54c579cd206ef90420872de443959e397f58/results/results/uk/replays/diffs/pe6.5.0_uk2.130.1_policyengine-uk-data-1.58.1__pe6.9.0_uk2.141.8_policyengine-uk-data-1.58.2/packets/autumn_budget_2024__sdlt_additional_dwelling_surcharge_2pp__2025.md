# Investigation packet: autumn_budget_2024 / autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp / CY2025

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Stamp Duty Land Tax (SDLT): Increase the Higher Rate of Additional Dwelling (HRAD) of SDLT by 2ppts from 3% to 5% from 31 October 2024
* Flags: numerical, structural, inertness, construction
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.9.0_uk2.141.8_policyengine-uk-data-1.58.2`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:11647:b269082735adb83b | 2,182.3 | — | — | inertness | inert_on_head_only |
| source_row | obr_pmd_nov2025:11653:f9403f5df25abb27 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:11659:58ae63699eb03986 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22806:de888a245348bcc1 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22812:2180748e886ef44d | — | — | — | — | — |
| measure_year | total | 2,182.3 | 0.0 | -2,182.3 | numerical, structural, inertness, construction | move_above_threshold; zero_crossing; inert_on_head_only; premise_check_changed (forward_delta_changes_current_law) |
| head | stamp_duty_land_tax | 2,182.3 | 0.0 | -2,182.3 | numerical, structural | move_above_threshold; zero_crossing |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:11647:b269082735adb83b (row 11647) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Stamp duty | 208.3 | 2,182.3 | — |
| base | obr_pmd_nov2025:11653:f9403f5df25abb27 (row 11653) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Capital gains tax | -92.2 | — | — |
| base | obr_pmd_nov2025:11659:58ae63699eb03986 (row 11659) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Inheritance tax | -39.1 | — | — |
| base | obr_pmd_nov2025:22806:de888a245348bcc1 (row 22806) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Scottish BGA (current) | 9.7 | — | — |
| base | obr_pmd_nov2025:22812:2180748e886ef44d (row 22812) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | PSCE in RDEL | 4.2 | — | — |
| head | obr_pmd_nov2025:11647:b269082735adb83b (row 11647) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Stamp duty | 208.3 | 2,182.3 | — |
| head | obr_pmd_nov2025:11653:f9403f5df25abb27 (row 11653) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Capital gains tax | -92.2 | — | — |
| head | obr_pmd_nov2025:11659:58ae63699eb03986 (row 11659) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Inheritance tax | -39.1 | — | — |
| head | obr_pmd_nov2025:22806:de888a245348bcc1 (row 22806) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Scottish BGA (current) | 9.7 | — | — |
| head | obr_pmd_nov2025:22812:2180748e886ef44d (row 22812) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | PSCE in RDEL | 4.2 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2025.json` (sha256 `c8319ed95b7fbb9d76fe13c26b16de6bc2734b4378b7219af1eaf4c55d3012e1`), forward_delta_on_certified_world; baseline dict `null`; reform dict `{"gov.hmrc.stamp_duty.residential.purchase.additional.rate[0].rate": {"2024-10-31.2035-12-31": 0.05}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[1].rate": {"2024-10-31.2035-12-31": 0.07}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[2].rate": {"2024-10-31.2035-12-31": 0.1}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[3].rate": {"2024-10-31.2035-12-31": 0.15}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[4].rate": {"2024-10-31.2035-12-31": 0.17}}`
* head: `results/uk/replays/pe6.9.0_uk2.141.8_policyengine-uk-data-1.58.2/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2025.json` (sha256 `0e6bb7001d2bd8d7f33da891fc9e4484f6e545b6cdc411f1393008fdc21a763d`), forward_delta_on_certified_world; baseline dict `null`; reform dict `{"gov.hmrc.stamp_duty.residential.purchase.additional.rate[0].rate": {"2024-10-31.2035-12-31": 0.05}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[1].rate": {"2024-10-31.2035-12-31": 0.07}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[2].rate": {"2024-10-31.2035-12-31": 0.1}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[3].rate": {"2024-10-31.2035-12-31": 0.15}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[4].rate": {"2024-10-31.2035-12-31": 0.17}}`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2025
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.9.0_uk2.141.8_policyengine-uk-data-1.58.2 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.141.8_policyengine-uk-data-1.58.2/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2025
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
