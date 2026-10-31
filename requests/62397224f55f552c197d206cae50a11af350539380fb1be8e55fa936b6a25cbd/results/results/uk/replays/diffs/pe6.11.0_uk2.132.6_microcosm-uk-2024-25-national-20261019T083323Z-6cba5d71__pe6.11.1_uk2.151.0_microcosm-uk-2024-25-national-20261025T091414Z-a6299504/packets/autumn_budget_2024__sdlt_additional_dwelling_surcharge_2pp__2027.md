# Investigation packet: autumn_budget_2024 / autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Stamp Duty Land Tax (SDLT): Increase the Higher Rate of Additional Dwelling (HRAD) of SDLT by 2ppts from 3% to 5% from 31 October 2024
* Flags: numerical, structural, construction
* Base: `pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71`
* Head: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:11649:910077d14a180f90 | 2,006.3 | 1,044.7 | -961.6 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:11655:2e1dc1d269227e2f | — | — | — | — | — |
| source_row | obr_pmd_nov2025:11661:a5ce1ea1b223ab58 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22808:c8fe3aecef088bf1 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22814:3608d4c47b99f4c7 | — | — | — | — | — |
| measure_year | total | 2,006.3 | 1,044.7 | -961.6 | numerical, structural, construction | move_above_threshold; construction_orientation_changed; baseline_world_reform_dict_changed; construction_revision_changed; premise_check_changed (forward_delta_changes_current_law); premise_check_changed (reversal_differs_from_current_law); reform_world_reform_dict_changed |
| head | stamp_duty_land_tax | 2,006.3 | 1,044.7 | -961.6 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:11649:910077d14a180f90 (row 11649) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Stamp duty | 413.5 | 2,006.3 | 1,044.7 |
| base | obr_pmd_nov2025:11655:2e1dc1d269227e2f (row 11655) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Capital gains tax | -117.9 | — | — |
| base | obr_pmd_nov2025:11661:a5ce1ea1b223ab58 (row 11661) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Inheritance tax | -70.6 | — | — |
| base | obr_pmd_nov2025:22808:c8fe3aecef088bf1 (row 22808) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | 19.3 | — | — |
| base | obr_pmd_nov2025:22814:3608d4c47b99f4c7 (row 22814) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | 8.4 | — | — |
| head | obr_pmd_nov2025:11649:910077d14a180f90 (row 11649) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Stamp duty | 413.5 | 2,006.3 | 1,044.7 |
| head | obr_pmd_nov2025:11655:2e1dc1d269227e2f (row 11655) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Capital gains tax | -117.9 | — | — |
| head | obr_pmd_nov2025:11661:a5ce1ea1b223ab58 (row 11661) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Inheritance tax | -70.6 | — | — |
| head | obr_pmd_nov2025:22808:c8fe3aecef088bf1 (row 22808) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | 19.3 | — | — |
| head | obr_pmd_nov2025:22814:3608d4c47b99f4c7 (row 22814) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | 8.4 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2027.json` (sha256 `7b1cced77d0d442f568239e6f4b87f5ad6f3e9c8b21f6f771cb556b8f9f7a687`), forward_delta_on_certified_world; baseline dict `null`; reform dict `{"gov.hmrc.stamp_duty.residential.purchase.additional.rate[0].rate": {"2024-10-31.2035-12-31": 0.05}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[1].rate": {"2024-10-31.2035-12-31": 0.07}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[2].rate": {"2024-10-31.2035-12-31": 0.1}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[3].rate": {"2024-10-31.2035-12-31": 0.15}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[4].rate": {"2024-10-31.2035-12-31": 0.17}}`
* head: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2027.json` (sha256 `90c6f663a71c27a5ab320be04630651d98eac47affe19e724a612c67f4a194d2`), reversal_on_certified_world; baseline dict `{"gov.hmrc.stamp_duty.residential.purchase.additional.rate[0].rate": {"2024-10-31.2035-12-31": 0.03}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[1].rate": {"2024-10-31.2035-12-31": 0.05}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[2].rate": {"2024-10-31.2035-12-31": 0.08}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[3].rate": {"2024-10-31.2035-12-31": 0.13}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[4].rate": {"2024-10-31.2035-12-31": 0.15}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2027
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
