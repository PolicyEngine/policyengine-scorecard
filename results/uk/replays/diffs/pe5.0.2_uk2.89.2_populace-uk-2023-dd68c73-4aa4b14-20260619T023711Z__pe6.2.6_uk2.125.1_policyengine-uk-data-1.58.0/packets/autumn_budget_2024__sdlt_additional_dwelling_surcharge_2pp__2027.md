# Investigation packet: autumn_budget_2024 / autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Stamp Duty Land Tax (SDLT): Increase the Higher Rate of Additional Dwelling (HRAD) of SDLT by 2ppts from 3% to 5% from 31 October 2024
* Flags: numerical
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:11649:910077d14a180f90 | 2,182.6 | 2,344.8 | 162.2 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:11655:2e1dc1d269227e2f | — | — | — | — | — |
| source_row | obr_pmd_nov2025:11661:a5ce1ea1b223ab58 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22808:c8fe3aecef088bf1 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22814:3608d4c47b99f4c7 | — | — | — | — | — |
| measure_year | total | 2,182.6 | 2,344.8 | 162.2 | numerical | move_above_threshold |
| head | stamp_duty_land_tax | 2,182.6 | 2,344.8 | 162.2 | numerical | move_above_threshold |

## OBR source cells

| Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---:|---:|---:|
| obr_pmd_nov2025:11649:910077d14a180f90 (row 11649) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Stamp duty | 413.5 | 2,182.6 | 2,344.8 |
| obr_pmd_nov2025:11655:2e1dc1d269227e2f (row 11655) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Capital gains tax | -117.9 | — | — |
| obr_pmd_nov2025:11661:a5ce1ea1b223ab58 (row 11661) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Inheritance tax | -70.6 | — | — |
| obr_pmd_nov2025:22808:c8fe3aecef088bf1 (row 22808) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | 19.3 | — | — |
| obr_pmd_nov2025:22814:3608d4c47b99f4c7 (row 22814) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | 8.4 | — | — |

## Executed worlds

* base: `results/uk/events/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2027.json` (sha256 `b42db280325514c06105c5e2a0aa3fedb5f2fc24548778486ab4baf0ee418ecc`), forward_delta_on_certified_world; baseline dict `null`; reform dict `{"gov.hmrc.stamp_duty.residential.purchase.additional.rate[0].rate": {"2024-10-31.2035-12-31": 0.05}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[1].rate": {"2024-10-31.2035-12-31": 0.07}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[2].rate": {"2024-10-31.2035-12-31": 0.1}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[3].rate": {"2024-10-31.2035-12-31": 0.15}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[4].rate": {"2024-10-31.2035-12-31": 0.17}}`
* head: `results/uk/replays/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2027.json` (sha256 `b3d4b01015c7e700da922c20baae9834ab7eb0e11057962daba4257b4759eb20`), forward_delta_on_certified_world; baseline dict `null`; reform dict `{"gov.hmrc.stamp_duty.residential.purchase.additional.rate[0].rate": {"2024-10-31.2035-12-31": 0.05}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[1].rate": {"2024-10-31.2035-12-31": 0.07}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[2].rate": {"2024-10-31.2035-12-31": 0.1}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[3].rate": {"2024-10-31.2035-12-31": 0.15}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[4].rate": {"2024-10-31.2035-12-31": 0.17}}`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --measures autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2027
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0 --measures autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
