# Investigation packet: autumn_budget_2024 / autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp / CY2025

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Stamp Duty Land Tax (SDLT): Increase the Higher Rate of Additional Dwelling (HRAD) of SDLT by 2ppts from 3% to 5% from 31 October 2024
* Flags: numerical
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:11647:b269082735adb83b | 2,039.0 | 2,190.5 | 151.5 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:11653:f9403f5df25abb27 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:11659:58ae63699eb03986 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22806:de888a245348bcc1 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22812:2180748e886ef44d | — | — | — | — | — |
| measure_year | total | 2,039.0 | 2,190.5 | 151.5 | numerical | move_above_threshold |
| head | stamp_duty_land_tax | 2,039.0 | 2,190.5 | 151.5 | numerical | move_above_threshold |

## OBR source cells

| Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---:|---:|---:|
| obr_pmd_nov2025:11647:b269082735adb83b (row 11647) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Stamp duty | 208.3 | 2,039.0 | 2,190.5 |
| obr_pmd_nov2025:11653:f9403f5df25abb27 (row 11653) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Capital gains tax | -92.2 | — | — |
| obr_pmd_nov2025:11659:58ae63699eb03986 (row 11659) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Inheritance tax | -39.1 | — | — |
| obr_pmd_nov2025:22806:de888a245348bcc1 (row 22806) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Scottish BGA (current) | 9.7 | — | — |
| obr_pmd_nov2025:22812:2180748e886ef44d (row 22812) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | PSCE in RDEL | 4.2 | — | — |

## Executed worlds

* base: `results/uk/events/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2025.json` (sha256 `42577f2444a415c58a9e906f9c810bf6876884466bd8c91584d478889d4f5301`), forward_delta_on_certified_world; baseline dict `null`; reform dict `{"gov.hmrc.stamp_duty.residential.purchase.additional.rate[0].rate": {"2024-10-31.2035-12-31": 0.05}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[1].rate": {"2024-10-31.2035-12-31": 0.07}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[2].rate": {"2024-10-31.2035-12-31": 0.1}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[3].rate": {"2024-10-31.2035-12-31": 0.15}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[4].rate": {"2024-10-31.2035-12-31": 0.17}}`
* head: `results/uk/replays/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2025.json` (sha256 `e5af4a516dd512e6ef71dc7ace88f04cc2cb57d7a437a6cfbf193a29b093f885`), forward_delta_on_certified_world; baseline dict `null`; reform dict `{"gov.hmrc.stamp_duty.residential.purchase.additional.rate[0].rate": {"2024-10-31.2035-12-31": 0.05}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[1].rate": {"2024-10-31.2035-12-31": 0.07}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[2].rate": {"2024-10-31.2035-12-31": 0.1}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[3].rate": {"2024-10-31.2035-12-31": 0.15}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[4].rate": {"2024-10-31.2035-12-31": 0.17}}`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --measures autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2025
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0 --measures autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2025
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
