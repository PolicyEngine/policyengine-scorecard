# Investigation packet: autumn_budget_2024 / autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Stamp Duty Land Tax (SDLT): Increase the Higher Rate of Additional Dwelling (HRAD) of SDLT by 2ppts from 3% to 5% from 31 October 2024
* Flags: numerical, structural, inertness, construction
* Base: `pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71`
* Head: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:11648:48bd77ddd06dec27 | 1,936.3 | — | — | inertness | inert_on_head_only |
| source_row | obr_pmd_nov2025:11654:d3b9bc5fd38a798c | — | — | — | — | — |
| source_row | obr_pmd_nov2025:11660:8cf7ed109cbbb468 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22807:422d5d733ecadc39 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22813:efbafd1fd9337894 | — | — | — | — | — |
| measure_year | total | 1,936.3 | 0.0 | -1,936.3 | numerical, structural, inertness, construction | move_above_threshold; zero_crossing; inert_on_head_only; premise_check_changed (forward_delta_changes_current_law) |
| head | stamp_duty_land_tax | 1,936.3 | 0.0 | -1,936.3 | numerical, structural | move_above_threshold; zero_crossing |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:11648:48bd77ddd06dec27 (row 11648) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Stamp duty | 334.2 | 1,936.3 | — |
| base | obr_pmd_nov2025:11654:d3b9bc5fd38a798c (row 11654) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Capital gains tax | -121.4 | — | — |
| base | obr_pmd_nov2025:11660:8cf7ed109cbbb468 (row 11660) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Inheritance tax | -66.4 | — | — |
| base | obr_pmd_nov2025:22807:422d5d733ecadc39 (row 22807) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Scottish BGA (current) | 15.5 | — | — |
| base | obr_pmd_nov2025:22813:efbafd1fd9337894 (row 22813) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSCE in RDEL | 6.8 | — | — |
| head | obr_pmd_nov2025:11648:48bd77ddd06dec27 (row 11648) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Stamp duty | 334.2 | 1,936.3 | — |
| head | obr_pmd_nov2025:11654:d3b9bc5fd38a798c (row 11654) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Capital gains tax | -121.4 | — | — |
| head | obr_pmd_nov2025:11660:8cf7ed109cbbb468 (row 11660) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Inheritance tax | -66.4 | — | — |
| head | obr_pmd_nov2025:22807:422d5d733ecadc39 (row 22807) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Scottish BGA (current) | 15.5 | — | — |
| head | obr_pmd_nov2025:22813:efbafd1fd9337894 (row 22813) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSCE in RDEL | 6.8 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2026.json` (sha256 `2dd9c7fe3ef93a4ea9c55c828cc6ceaf47bba9f3528ea7031c420fdb769d2e5c`), forward_delta_on_certified_world; baseline dict `null`; reform dict `{"gov.hmrc.stamp_duty.residential.purchase.additional.rate[0].rate": {"2024-10-31.2035-12-31": 0.05}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[1].rate": {"2024-10-31.2035-12-31": 0.07}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[2].rate": {"2024-10-31.2035-12-31": 0.1}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[3].rate": {"2024-10-31.2035-12-31": 0.15}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[4].rate": {"2024-10-31.2035-12-31": 0.17}}`
* head: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2026.json` (sha256 `79d7cccfad6224458d311e67d9bfa1a58b805cf56cca55d8db40361c57cff7e5`), forward_delta_on_certified_world; baseline dict `null`; reform dict `{"gov.hmrc.stamp_duty.residential.purchase.additional.rate[0].rate": {"2024-10-31.2035-12-31": 0.05}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[1].rate": {"2024-10-31.2035-12-31": 0.07}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[2].rate": {"2024-10-31.2035-12-31": 0.1}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[3].rate": {"2024-10-31.2035-12-31": 0.15}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[4].rate": {"2024-10-31.2035-12-31": 0.17}}`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2026
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
