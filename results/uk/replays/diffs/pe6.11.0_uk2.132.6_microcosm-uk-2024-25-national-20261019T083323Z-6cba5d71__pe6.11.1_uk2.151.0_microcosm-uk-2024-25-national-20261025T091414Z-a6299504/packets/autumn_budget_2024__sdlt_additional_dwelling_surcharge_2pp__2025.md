# Investigation packet: autumn_budget_2024 / autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp / CY2025

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Stamp Duty Land Tax (SDLT): Increase the Higher Rate of Additional Dwelling (HRAD) of SDLT by 2ppts from 3% to 5% from 31 October 2024
* Flags: numerical, structural, construction
* Base: `pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71`
* Head: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:11647:b269082735adb83b | 1,874.3 | 984.1 | -890.2 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:11653:f9403f5df25abb27 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:11659:58ae63699eb03986 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22806:de888a245348bcc1 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22812:2180748e886ef44d | — | — | — | — | — |
| measure_year | total | 1,874.3 | 984.1 | -890.2 | numerical, structural, construction | move_above_threshold; construction_orientation_changed; baseline_world_reform_dict_changed; construction_revision_changed; premise_check_changed (forward_delta_changes_current_law); premise_check_changed (reversal_differs_from_current_law); reform_world_reform_dict_changed |
| head | stamp_duty_land_tax | 1,874.3 | 984.1 | -890.2 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:11647:b269082735adb83b (row 11647) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Stamp duty | 208.3 | 1,874.3 | 984.1 |
| base | obr_pmd_nov2025:11653:f9403f5df25abb27 (row 11653) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Capital gains tax | -92.2 | — | — |
| base | obr_pmd_nov2025:11659:58ae63699eb03986 (row 11659) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Inheritance tax | -39.1 | — | — |
| base | obr_pmd_nov2025:22806:de888a245348bcc1 (row 22806) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Scottish BGA (current) | 9.7 | — | — |
| base | obr_pmd_nov2025:22812:2180748e886ef44d (row 22812) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | PSCE in RDEL | 4.2 | — | — |
| head | obr_pmd_nov2025:11647:b269082735adb83b (row 11647) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Stamp duty | 208.3 | 1,874.3 | 984.1 |
| head | obr_pmd_nov2025:11653:f9403f5df25abb27 (row 11653) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Capital gains tax | -92.2 | — | — |
| head | obr_pmd_nov2025:11659:58ae63699eb03986 (row 11659) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Inheritance tax | -39.1 | — | — |
| head | obr_pmd_nov2025:22806:de888a245348bcc1 (row 22806) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Scottish BGA (current) | 9.7 | — | — |
| head | obr_pmd_nov2025:22812:2180748e886ef44d (row 22812) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | PSCE in RDEL | 4.2 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2025.json` (sha256 `5e33da7bc7453196b76e03e176bf0dd19843ef0471810d7d7d3320ad8cf89b92`), forward_delta_on_certified_world; baseline dict `null`; reform dict `{"gov.hmrc.stamp_duty.residential.purchase.additional.rate[0].rate": {"2024-10-31.2035-12-31": 0.05}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[1].rate": {"2024-10-31.2035-12-31": 0.07}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[2].rate": {"2024-10-31.2035-12-31": 0.1}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[3].rate": {"2024-10-31.2035-12-31": 0.15}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[4].rate": {"2024-10-31.2035-12-31": 0.17}}`
* head: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2025.json` (sha256 `46df5f500f55b6efb5cc2c6e13f65c97020d96a257a828603be2cc6251cd5991`), reversal_on_certified_world; baseline dict `{"gov.hmrc.stamp_duty.residential.purchase.additional.rate[0].rate": {"2024-10-31.2035-12-31": 0.03}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[1].rate": {"2024-10-31.2035-12-31": 0.05}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[2].rate": {"2024-10-31.2035-12-31": 0.08}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[3].rate": {"2024-10-31.2035-12-31": 0.13}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[4].rate": {"2024-10-31.2035-12-31": 0.15}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2025
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2025
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
