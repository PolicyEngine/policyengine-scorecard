# Investigation packet: autumn_budget_2024 / autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp / CY2029

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Stamp Duty Land Tax (SDLT): Increase the Higher Rate of Additional Dwelling (HRAD) of SDLT by 2ppts from 3% to 5% from 31 October 2024
* Flags: numerical, structural, inertness
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.8.0_uk2.141.1_policyengine-uk-data-1.58.2`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:11651:9a7327566a66890c | 2,500.6 | — | — | inertness | inert_on_head_only |
| source_row | obr_pmd_nov2025:11657:7fa7efce401257e4 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:11663:7a186012776764b9 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22810:b94a793fb1d3c286 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22816:4ee584ef8c6c1052 | — | — | — | — | — |
| measure_year | total | 2,500.6 | 0.0 | -2,500.6 | numerical, structural, inertness | move_above_threshold; zero_crossing; inert_on_head_only |
| head | stamp_duty_land_tax | 2,500.6 | 0.0 | -2,500.6 | numerical, structural | move_above_threshold; zero_crossing |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:11651:9a7327566a66890c (row 11651) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Stamp duty | 490.3 | 2,500.6 | — |
| base | obr_pmd_nov2025:11657:7fa7efce401257e4 (row 11657) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Capital gains tax | -129.2 | — | — |
| base | obr_pmd_nov2025:11663:7a186012776764b9 (row 11663) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Inheritance tax | -84.7 | — | — |
| base | obr_pmd_nov2025:22810:b94a793fb1d3c286 (row 22810) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Scottish BGA (current) | 22.8 | — | — |
| base | obr_pmd_nov2025:22816:4ee584ef8c6c1052 (row 22816) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | PSCE in RDEL | 9.9 | — | — |
| head | obr_pmd_nov2025:11651:9a7327566a66890c (row 11651) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Stamp duty | 490.3 | 2,500.6 | — |
| head | obr_pmd_nov2025:11657:7fa7efce401257e4 (row 11657) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Capital gains tax | -129.2 | — | — |
| head | obr_pmd_nov2025:11663:7a186012776764b9 (row 11663) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Inheritance tax | -84.7 | — | — |
| head | obr_pmd_nov2025:22810:b94a793fb1d3c286 (row 22810) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Scottish BGA (current) | 22.8 | — | — |
| head | obr_pmd_nov2025:22816:4ee584ef8c6c1052 (row 22816) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | PSCE in RDEL | 9.9 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2029.json` (sha256 `86b2c9ee0cdabd375d003a8c086cd9c8185d1213670b9a889af0aa1484340134`), forward_delta_on_certified_world; baseline dict `null`; reform dict `{"gov.hmrc.stamp_duty.residential.purchase.additional.rate[0].rate": {"2024-10-31.2035-12-31": 0.05}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[1].rate": {"2024-10-31.2035-12-31": 0.07}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[2].rate": {"2024-10-31.2035-12-31": 0.1}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[3].rate": {"2024-10-31.2035-12-31": 0.15}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[4].rate": {"2024-10-31.2035-12-31": 0.17}}`
* head: `results/uk/replays/pe6.8.0_uk2.141.1_policyengine-uk-data-1.58.2/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2029.json` (sha256 `9bd8d1bbce0897a8cd94d3790b3cc03c22786667e06873debdb4d7d80906f5e9`), forward_delta_on_certified_world; baseline dict `null`; reform dict `{"gov.hmrc.stamp_duty.residential.purchase.additional.rate[0].rate": {"2024-10-31.2035-12-31": 0.05}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[1].rate": {"2024-10-31.2035-12-31": 0.07}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[2].rate": {"2024-10-31.2035-12-31": 0.1}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[3].rate": {"2024-10-31.2035-12-31": 0.15}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[4].rate": {"2024-10-31.2035-12-31": 0.17}}`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2029
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.8.0_uk2.141.1_policyengine-uk-data-1.58.2 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.8.0_uk2.141.1_policyengine-uk-data-1.58.2/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2029
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
