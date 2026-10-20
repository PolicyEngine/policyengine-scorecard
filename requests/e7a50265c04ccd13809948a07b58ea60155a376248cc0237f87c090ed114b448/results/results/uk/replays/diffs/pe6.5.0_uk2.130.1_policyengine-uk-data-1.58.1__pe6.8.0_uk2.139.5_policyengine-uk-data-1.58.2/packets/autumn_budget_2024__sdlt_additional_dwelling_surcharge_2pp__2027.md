# Investigation packet: autumn_budget_2024 / autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Stamp Duty Land Tax (SDLT): Increase the Higher Rate of Additional Dwelling (HRAD) of SDLT by 2ppts from 3% to 5% from 31 October 2024
* Flags: numerical, structural, inertness
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.8.0_uk2.139.5_policyengine-uk-data-1.58.2`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:11649:910077d14a180f90 | 2,336.0 | — | — | inertness | inert_on_head_only |
| source_row | obr_pmd_nov2025:11655:2e1dc1d269227e2f | — | — | — | — | — |
| source_row | obr_pmd_nov2025:11661:a5ce1ea1b223ab58 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22808:c8fe3aecef088bf1 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22814:3608d4c47b99f4c7 | — | — | — | — | — |
| measure_year | total | 2,336.0 | 0.0 | -2,336.0 | numerical, structural, inertness | move_above_threshold; zero_crossing; inert_on_head_only |
| head | stamp_duty_land_tax | 2,336.0 | 0.0 | -2,336.0 | numerical, structural | move_above_threshold; zero_crossing |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:11649:910077d14a180f90 (row 11649) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Stamp duty | 413.5 | 2,336.0 | — |
| base | obr_pmd_nov2025:11655:2e1dc1d269227e2f (row 11655) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Capital gains tax | -117.9 | — | — |
| base | obr_pmd_nov2025:11661:a5ce1ea1b223ab58 (row 11661) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Inheritance tax | -70.6 | — | — |
| base | obr_pmd_nov2025:22808:c8fe3aecef088bf1 (row 22808) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | 19.3 | — | — |
| base | obr_pmd_nov2025:22814:3608d4c47b99f4c7 (row 22814) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | 8.4 | — | — |
| head | obr_pmd_nov2025:11649:910077d14a180f90 (row 11649) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Stamp duty | 413.5 | 2,336.0 | — |
| head | obr_pmd_nov2025:11655:2e1dc1d269227e2f (row 11655) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Capital gains tax | -117.9 | — | — |
| head | obr_pmd_nov2025:11661:a5ce1ea1b223ab58 (row 11661) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Inheritance tax | -70.6 | — | — |
| head | obr_pmd_nov2025:22808:c8fe3aecef088bf1 (row 22808) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | 19.3 | — | — |
| head | obr_pmd_nov2025:22814:3608d4c47b99f4c7 (row 22814) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | 8.4 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2027.json` (sha256 `f4c39be893fa1a9504f1b558ee5d23fdaeae6a98c1c18c377b8095abc78ef89b`), forward_delta_on_certified_world; baseline dict `null`; reform dict `{"gov.hmrc.stamp_duty.residential.purchase.additional.rate[0].rate": {"2024-10-31.2035-12-31": 0.05}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[1].rate": {"2024-10-31.2035-12-31": 0.07}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[2].rate": {"2024-10-31.2035-12-31": 0.1}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[3].rate": {"2024-10-31.2035-12-31": 0.15}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[4].rate": {"2024-10-31.2035-12-31": 0.17}}`
* head: `results/uk/replays/pe6.8.0_uk2.139.5_policyengine-uk-data-1.58.2/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2027.json` (sha256 `2e64742a027df3aa5c766bffbd70a7461b9566cad96107bffcd5027ee0d1a405`), forward_delta_on_certified_world; baseline dict `null`; reform dict `{"gov.hmrc.stamp_duty.residential.purchase.additional.rate[0].rate": {"2024-10-31.2035-12-31": 0.05}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[1].rate": {"2024-10-31.2035-12-31": 0.07}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[2].rate": {"2024-10-31.2035-12-31": 0.1}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[3].rate": {"2024-10-31.2035-12-31": 0.15}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[4].rate": {"2024-10-31.2035-12-31": 0.17}}`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2027
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.8.0_uk2.139.5_policyengine-uk-data-1.58.2 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.8.0_uk2.139.5_policyengine-uk-data-1.58.2/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
