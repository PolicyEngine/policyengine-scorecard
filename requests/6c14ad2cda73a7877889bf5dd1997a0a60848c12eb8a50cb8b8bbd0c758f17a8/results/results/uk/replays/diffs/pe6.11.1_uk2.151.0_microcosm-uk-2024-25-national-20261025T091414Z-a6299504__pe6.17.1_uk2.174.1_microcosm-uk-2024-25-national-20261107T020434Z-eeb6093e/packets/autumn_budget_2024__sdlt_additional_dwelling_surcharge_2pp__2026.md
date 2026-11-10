# Investigation packet: autumn_budget_2024 / autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Stamp Duty Land Tax (SDLT): Increase the Higher Rate of Additional Dwelling (HRAD) of SDLT by 2ppts from 3% to 5% from 31 October 2024
* Flags: numerical
* Base: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`
* Head: `pe6.17.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:11648:48bd77ddd06dec27 | 1,011.5 | 1,048.2 | 36.7 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:11654:d3b9bc5fd38a798c | — | — | — | — | — |
| source_row | obr_pmd_nov2025:11660:8cf7ed109cbbb468 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22807:422d5d733ecadc39 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22813:efbafd1fd9337894 | — | — | — | — | — |
| measure_year | total | 1,011.5 | 1,048.2 | 36.7 | numerical | move_above_threshold |
| head | stamp_duty_land_tax | 1,011.5 | 1,048.2 | 36.7 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:11648:48bd77ddd06dec27 (row 11648) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Stamp duty | 334.2 | 1,011.5 | 1,048.2 |
| base | obr_pmd_nov2025:11654:d3b9bc5fd38a798c (row 11654) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Capital gains tax | -121.4 | — | — |
| base | obr_pmd_nov2025:11660:8cf7ed109cbbb468 (row 11660) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Inheritance tax | -66.4 | — | — |
| base | obr_pmd_nov2025:22807:422d5d733ecadc39 (row 22807) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Scottish BGA (current) | 15.5 | — | — |
| base | obr_pmd_nov2025:22813:efbafd1fd9337894 (row 22813) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSCE in RDEL | 6.8 | — | — |
| head | obr_pmd_nov2025:11648:48bd77ddd06dec27 (row 11648) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Stamp duty | 334.2 | 1,011.5 | 1,048.2 |
| head | obr_pmd_nov2025:11654:d3b9bc5fd38a798c (row 11654) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Capital gains tax | -121.4 | — | — |
| head | obr_pmd_nov2025:11660:8cf7ed109cbbb468 (row 11660) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Inheritance tax | -66.4 | — | — |
| head | obr_pmd_nov2025:22807:422d5d733ecadc39 (row 22807) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Scottish BGA (current) | 15.5 | — | — |
| head | obr_pmd_nov2025:22813:efbafd1fd9337894 (row 22813) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSCE in RDEL | 6.8 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2026.json` (sha256 `f07842f506c9bcd987909aef1e89bd99278227b20d0bc65a803bb5db27ee0cf6`), reversal_on_certified_world; baseline dict `{"gov.hmrc.stamp_duty.residential.purchase.additional.rate[0].rate": {"2024-10-31.2035-12-31": 0.03}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[1].rate": {"2024-10-31.2035-12-31": 0.05}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[2].rate": {"2024-10-31.2035-12-31": 0.08}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[3].rate": {"2024-10-31.2035-12-31": 0.13}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[4].rate": {"2024-10-31.2035-12-31": 0.15}}`; reform dict `null`
* head: `results/uk/replays/pe6.17.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2026.json` (sha256 `cf30636d3c1187e4fe60c4998fcfa1dc99a5c55a92105a51e491212029f506e0`), reversal_on_certified_world; baseline dict `{"gov.hmrc.stamp_duty.residential.purchase.additional.rate[0].rate": {"2024-10-31.2035-12-31": 0.03}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[1].rate": {"2024-10-31.2035-12-31": 0.05}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[2].rate": {"2024-10-31.2035-12-31": 0.08}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[3].rate": {"2024-10-31.2035-12-31": 0.13}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[4].rate": {"2024-10-31.2035-12-31": 0.15}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2026
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.17.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.17.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
