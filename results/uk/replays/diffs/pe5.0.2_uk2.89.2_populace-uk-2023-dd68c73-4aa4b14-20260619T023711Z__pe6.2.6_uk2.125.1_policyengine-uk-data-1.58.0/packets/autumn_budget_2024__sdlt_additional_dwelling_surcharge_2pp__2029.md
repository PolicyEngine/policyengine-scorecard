# Investigation packet: autumn_budget_2024 / autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp / CY2029

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Stamp Duty Land Tax (SDLT): Increase the Higher Rate of Additional Dwelling (HRAD) of SDLT by 2ppts from 3% to 5% from 31 October 2024
* Flags: numerical
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:11651:9a7327566a66890c | 2,336.4 | 2,510.1 | 173.7 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:11657:7fa7efce401257e4 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:11663:7a186012776764b9 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22810:b94a793fb1d3c286 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22816:4ee584ef8c6c1052 | — | — | — | — | — |
| measure_year | total | 2,336.4 | 2,510.1 | 173.7 | numerical | move_above_threshold |
| head | stamp_duty_land_tax | 2,336.4 | 2,510.1 | 173.7 | numerical | move_above_threshold |

## OBR source cells

| Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---:|---:|---:|
| obr_pmd_nov2025:11651:9a7327566a66890c (row 11651) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Stamp duty | 490.3 | 2,336.4 | 2,510.1 |
| obr_pmd_nov2025:11657:7fa7efce401257e4 (row 11657) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Capital gains tax | -129.2 | — | — |
| obr_pmd_nov2025:11663:7a186012776764b9 (row 11663) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Inheritance tax | -84.7 | — | — |
| obr_pmd_nov2025:22810:b94a793fb1d3c286 (row 22810) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Scottish BGA (current) | 22.8 | — | — |
| obr_pmd_nov2025:22816:4ee584ef8c6c1052 (row 22816) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | PSCE in RDEL | 9.9 | — | — |

## Executed worlds

* base: `results/uk/events/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2029.json` (sha256 `f5da4dceb4590b02226a96759ce615b1282a0707a2349616f676394d17b5ca31`), forward_delta_on_certified_world; baseline dict `null`; reform dict `{"gov.hmrc.stamp_duty.residential.purchase.additional.rate[0].rate": {"2024-10-31.2035-12-31": 0.05}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[1].rate": {"2024-10-31.2035-12-31": 0.07}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[2].rate": {"2024-10-31.2035-12-31": 0.1}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[3].rate": {"2024-10-31.2035-12-31": 0.15}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[4].rate": {"2024-10-31.2035-12-31": 0.17}}`
* head: `results/uk/replays/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2029.json` (sha256 `f7a8720d649c722f589f7c39bb63e0fb0825cb6d27ac1eaef505f7599fa93547`), forward_delta_on_certified_world; baseline dict `null`; reform dict `{"gov.hmrc.stamp_duty.residential.purchase.additional.rate[0].rate": {"2024-10-31.2035-12-31": 0.05}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[1].rate": {"2024-10-31.2035-12-31": 0.07}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[2].rate": {"2024-10-31.2035-12-31": 0.1}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[3].rate": {"2024-10-31.2035-12-31": 0.15}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[4].rate": {"2024-10-31.2035-12-31": 0.17}}`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --measures autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2029
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0 --measures autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2029
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
