# Investigation packet: autumn_budget_2024 / autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Stamp Duty Land Tax (SDLT): Increase the Higher Rate of Additional Dwelling (HRAD) of SDLT by 2ppts from 3% to 5% from 31 October 2024
* Flags: numerical, structural, inertness, construction
* Base: `pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71`
* Head: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:11650:068acce8b0873200 | 2,080.2 | — | — | inertness | inert_on_head_only |
| source_row | obr_pmd_nov2025:11656:e5c5845a4df7a18b | — | — | — | — | — |
| source_row | obr_pmd_nov2025:11662:6d909ba62cdc4a9d | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22809:83691f2969d81ad0 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22815:1312cc7ca835f35b | — | — | — | — | — |
| measure_year | total | 2,080.2 | 0.0 | -2,080.2 | numerical, structural, inertness, construction | move_above_threshold; zero_crossing; inert_on_head_only; premise_check_changed (forward_delta_changes_current_law) |
| head | stamp_duty_land_tax | 2,080.2 | 0.0 | -2,080.2 | numerical, structural | move_above_threshold; zero_crossing |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:11650:068acce8b0873200 (row 11650) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Stamp duty | 450.8 | 2,080.2 | — |
| base | obr_pmd_nov2025:11656:e5c5845a4df7a18b (row 11656) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Capital gains tax | -122.8 | — | — |
| base | obr_pmd_nov2025:11662:6d909ba62cdc4a9d (row 11662) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Inheritance tax | -77.4 | — | — |
| base | obr_pmd_nov2025:22809:83691f2969d81ad0 (row 22809) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | 21.0 | — | — |
| base | obr_pmd_nov2025:22815:1312cc7ca835f35b (row 22815) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | 9.1 | — | — |
| head | obr_pmd_nov2025:11650:068acce8b0873200 (row 11650) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Stamp duty | 450.8 | 2,080.2 | — |
| head | obr_pmd_nov2025:11656:e5c5845a4df7a18b (row 11656) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Capital gains tax | -122.8 | — | — |
| head | obr_pmd_nov2025:11662:6d909ba62cdc4a9d (row 11662) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Inheritance tax | -77.4 | — | — |
| head | obr_pmd_nov2025:22809:83691f2969d81ad0 (row 22809) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | 21.0 | — | — |
| head | obr_pmd_nov2025:22815:1312cc7ca835f35b (row 22815) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | 9.1 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2028.json` (sha256 `ea21f9cbc5bbdfd17c802a20a033069187c51666800b5041e106cb31ba3b04fb`), forward_delta_on_certified_world; baseline dict `null`; reform dict `{"gov.hmrc.stamp_duty.residential.purchase.additional.rate[0].rate": {"2024-10-31.2035-12-31": 0.05}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[1].rate": {"2024-10-31.2035-12-31": 0.07}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[2].rate": {"2024-10-31.2035-12-31": 0.1}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[3].rate": {"2024-10-31.2035-12-31": 0.15}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[4].rate": {"2024-10-31.2035-12-31": 0.17}}`
* head: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2028.json` (sha256 `15b9fded2e944f409259b586a43b42a505c5ba0c9cfa966b5f8155f39c2caf59`), forward_delta_on_certified_world; baseline dict `null`; reform dict `{"gov.hmrc.stamp_duty.residential.purchase.additional.rate[0].rate": {"2024-10-31.2035-12-31": 0.05}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[1].rate": {"2024-10-31.2035-12-31": 0.07}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[2].rate": {"2024-10-31.2035-12-31": 0.1}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[3].rate": {"2024-10-31.2035-12-31": 0.15}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[4].rate": {"2024-10-31.2035-12-31": 0.17}}`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2028
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
