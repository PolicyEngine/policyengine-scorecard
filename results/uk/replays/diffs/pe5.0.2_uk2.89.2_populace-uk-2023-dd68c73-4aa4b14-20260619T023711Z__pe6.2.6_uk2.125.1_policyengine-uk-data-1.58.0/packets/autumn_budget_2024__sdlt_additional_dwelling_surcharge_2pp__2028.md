# Investigation packet: autumn_budget_2024 / autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Stamp Duty Land Tax (SDLT): Increase the Higher Rate of Additional Dwelling (HRAD) of SDLT by 2ppts from 3% to 5% from 31 October 2024
* Flags: numerical
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:11650:068acce8b0873200 | 2,259.3 | 2,427.2 | 168.0 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:11656:e5c5845a4df7a18b | — | — | — | — | — |
| source_row | obr_pmd_nov2025:11662:6d909ba62cdc4a9d | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22809:83691f2969d81ad0 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22815:1312cc7ca835f35b | — | — | — | — | — |
| measure_year | total | 2,259.3 | 2,427.2 | 168.0 | numerical | move_above_threshold |
| head | stamp_duty_land_tax | 2,259.3 | 2,427.2 | 168.0 | numerical | move_above_threshold |

## OBR source cells

| Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---:|---:|---:|
| obr_pmd_nov2025:11650:068acce8b0873200 (row 11650) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Stamp duty | 450.8 | 2,259.3 | 2,427.2 |
| obr_pmd_nov2025:11656:e5c5845a4df7a18b (row 11656) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Capital gains tax | -122.8 | — | — |
| obr_pmd_nov2025:11662:6d909ba62cdc4a9d (row 11662) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Inheritance tax | -77.4 | — | — |
| obr_pmd_nov2025:22809:83691f2969d81ad0 (row 22809) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | 21.0 | — | — |
| obr_pmd_nov2025:22815:1312cc7ca835f35b (row 22815) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | 9.1 | — | — |

## Executed worlds

* base: `results/uk/events/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2028.json` (sha256 `70e7150fa4a3f1eaad3603f32abfebc280f14c4aa93c9df190d6b0290af18f48`), forward_delta_on_certified_world; baseline dict `null`; reform dict `{"gov.hmrc.stamp_duty.residential.purchase.additional.rate[0].rate": {"2024-10-31.2035-12-31": 0.05}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[1].rate": {"2024-10-31.2035-12-31": 0.07}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[2].rate": {"2024-10-31.2035-12-31": 0.1}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[3].rate": {"2024-10-31.2035-12-31": 0.15}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[4].rate": {"2024-10-31.2035-12-31": 0.17}}`
* head: `results/uk/replays/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2028.json` (sha256 `789a3d2e467eca75c0793c0ceb7bdb30073e5f3a9aecedfa4d78eecf30c5fa9e`), forward_delta_on_certified_world; baseline dict `null`; reform dict `{"gov.hmrc.stamp_duty.residential.purchase.additional.rate[0].rate": {"2024-10-31.2035-12-31": 0.05}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[1].rate": {"2024-10-31.2035-12-31": 0.07}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[2].rate": {"2024-10-31.2035-12-31": 0.1}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[3].rate": {"2024-10-31.2035-12-31": 0.15}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[4].rate": {"2024-10-31.2035-12-31": 0.17}}`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --measures autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2028
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0 --measures autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
