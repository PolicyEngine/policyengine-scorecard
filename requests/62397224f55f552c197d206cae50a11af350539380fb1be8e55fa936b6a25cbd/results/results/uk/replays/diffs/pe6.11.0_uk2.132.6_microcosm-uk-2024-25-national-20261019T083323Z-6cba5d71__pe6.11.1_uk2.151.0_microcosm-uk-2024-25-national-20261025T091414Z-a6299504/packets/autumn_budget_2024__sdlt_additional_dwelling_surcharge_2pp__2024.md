# Investigation packet: autumn_budget_2024 / autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp / CY2024

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Stamp Duty Land Tax (SDLT): Increase the Higher Rate of Additional Dwelling (HRAD) of SDLT by 2ppts from 3% to 5% from 31 October 2024
* Flags: structural, construction
* Base: `pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71`
* Head: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:11646:015f43cbab8a5a02 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:11652:27a50b13291133b1 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:11658:7bd2fb01df3101cc | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22805:100fbff6a9179adc | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22811:21d31fd21a96d516 | — | — | — | — | — |
| measure_year | total | 0.0 | 0.0 | 0.0 | structural, construction | construction_orientation_changed; baseline_world_reform_dict_changed; construction_revision_changed; premise_check_changed (forward_delta_changes_current_law); premise_check_changed (reversal_differs_from_current_law); reform_world_reform_dict_changed |
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

* base: `results/uk/replays/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2024.json` (sha256 `5dc0f4edeb85f2a2850b86940b49e5ee3dc0ca779b44010e2acd94173a818e74`), forward_delta_on_certified_world; baseline dict `null`; reform dict `{"gov.hmrc.stamp_duty.residential.purchase.additional.rate[0].rate": {"2024-10-31.2035-12-31": 0.05}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[1].rate": {"2024-10-31.2035-12-31": 0.07}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[2].rate": {"2024-10-31.2035-12-31": 0.1}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[3].rate": {"2024-10-31.2035-12-31": 0.15}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[4].rate": {"2024-10-31.2035-12-31": 0.17}}`
* head: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2024.json` (sha256 `3c3c9be770771c5ae58159f8f54e4e12f70fba850f0b7b077bb5df5cc7b1a342`), reversal_on_certified_world; baseline dict `{"gov.hmrc.stamp_duty.residential.purchase.additional.rate[0].rate": {"2024-10-31.2035-12-31": 0.03}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[1].rate": {"2024-10-31.2035-12-31": 0.05}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[2].rate": {"2024-10-31.2035-12-31": 0.08}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[3].rate": {"2024-10-31.2035-12-31": 0.13}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[4].rate": {"2024-10-31.2035-12-31": 0.15}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp --years 2024 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2024
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp --years 2024 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2024
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
