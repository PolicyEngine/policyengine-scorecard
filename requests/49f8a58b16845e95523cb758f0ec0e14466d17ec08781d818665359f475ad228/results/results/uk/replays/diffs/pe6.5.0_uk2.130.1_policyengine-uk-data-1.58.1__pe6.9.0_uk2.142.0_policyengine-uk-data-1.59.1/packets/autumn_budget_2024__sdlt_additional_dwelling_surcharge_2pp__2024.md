# Investigation packet: autumn_budget_2024 / autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp / CY2024

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Stamp Duty Land Tax (SDLT): Increase the Higher Rate of Additional Dwelling (HRAD) of SDLT by 2ppts from 3% to 5% from 31 October 2024
* Flags: construction
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.9.0_uk2.142.0_policyengine-uk-data-1.59.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:11646:015f43cbab8a5a02 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:11652:27a50b13291133b1 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:11658:7bd2fb01df3101cc | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22805:100fbff6a9179adc | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22811:21d31fd21a96d516 | — | — | — | — | — |
| measure_year | total | 0.0 | 0.0 | 0.0 | construction | premise_check_changed (forward_delta_changes_current_law) |
| head | stamp_duty_land_tax | 0.0 | 0.0 | 0.0 | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:11646:015f43cbab8a5a02 (row 11646) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Stamp duty | 134.3 | — | — |
| base | obr_pmd_nov2025:11652:27a50b13291133b1 (row 11652) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Capital gains tax | -22.1 | — | — |
| base | obr_pmd_nov2025:11658:7bd2fb01df3101cc (row 11658) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Inheritance tax | -7.0 | — | — |
| base | obr_pmd_nov2025:22805:100fbff6a9179adc (row 22805) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Scottish BGA (current) | 6.2 | — | — |
| base | obr_pmd_nov2025:22811:21d31fd21a96d516 (row 22811) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | PSCE in RDEL | 2.7 | — | — |
| head | obr_pmd_nov2025:11646:015f43cbab8a5a02 (row 11646) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Stamp duty | 134.3 | — | — |
| head | obr_pmd_nov2025:11652:27a50b13291133b1 (row 11652) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Capital gains tax | -22.1 | — | — |
| head | obr_pmd_nov2025:11658:7bd2fb01df3101cc (row 11658) | Tax Measures (Policy measures database) / 2024-25 | 2024-25 | Inheritance tax | -7.0 | — | — |
| head | obr_pmd_nov2025:22805:100fbff6a9179adc (row 22805) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Scottish BGA (current) | 6.2 | — | — |
| head | obr_pmd_nov2025:22811:21d31fd21a96d516 (row 22811) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | PSCE in RDEL | 2.7 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2024.json` (sha256 `ca0d572e5625f32ef8ace2492e059fca2065861c05c67aa7e8b9f2a638b31da3`), forward_delta_on_certified_world; baseline dict `null`; reform dict `{"gov.hmrc.stamp_duty.residential.purchase.additional.rate[0].rate": {"2024-10-31.2035-12-31": 0.05}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[1].rate": {"2024-10-31.2035-12-31": 0.07}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[2].rate": {"2024-10-31.2035-12-31": 0.1}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[3].rate": {"2024-10-31.2035-12-31": 0.15}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[4].rate": {"2024-10-31.2035-12-31": 0.17}}`
* head: `results/uk/replays/pe6.9.0_uk2.142.0_policyengine-uk-data-1.59.1/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2024.json` (sha256 `55aa4289e61ba71efa43e43f0047319f865710edee76a7be1bc76ad156fedbab`), forward_delta_on_certified_world; baseline dict `null`; reform dict `{"gov.hmrc.stamp_duty.residential.purchase.additional.rate[0].rate": {"2024-10-31.2035-12-31": 0.05}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[1].rate": {"2024-10-31.2035-12-31": 0.07}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[2].rate": {"2024-10-31.2035-12-31": 0.1}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[3].rate": {"2024-10-31.2035-12-31": 0.15}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[4].rate": {"2024-10-31.2035-12-31": 0.17}}`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp --years 2024 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2024
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.9.0_uk2.142.0_policyengine-uk-data-1.59.1 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp --years 2024 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.142.0_policyengine-uk-data-1.59.1/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2024
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
