# Investigation packet: autumn_budget_2025 / ab2025__high_value_council_tax_surcharge / CY2029

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: High Value Council Tax Surcharge: Introduce a surcharge on owners of residential properties valued over £2m in England from 1 April 2028
* Flags: numerical
* Base: `pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12370:7f7d3d9ec714a95e | — | — | — | — | — |
| source_row | obr_pmd_nov2025:12376:d658edd74795036b | 495.7 | 329.2 | -166.6 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:12382:8ddcecd6a5e1169b | — | — | — | — | — |
| source_row | obr_pmd_nov2025:12388:57698fba46d02c0e | — | — | — | — | — |
| source_row | obr_pmd_nov2025:23991:5c8f7b5233d93763 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:23997:1a63945e557c2aa7 | — | — | — | — | — |
| measure_year | total | 495.7 | 329.2 | -166.6 | numerical | move_above_threshold |
| head | high_value_council_tax_surcharge | 495.7 | 329.2 | -166.6 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:12370:7f7d3d9ec714a95e (row 12370) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Capital gains tax | -35.0 | — | — |
| base | obr_pmd_nov2025:12376:d658edd74795036b (row 12376) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | High-value council tax surcharge | 466.0 | 495.7 | 329.2 |
| base | obr_pmd_nov2025:12382:8ddcecd6a5e1169b (row 12382) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Inheritance tax | -16.1 | — | — |
| base | obr_pmd_nov2025:12388:57698fba46d02c0e (row 12388) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Stamp duty | 15.0 | — | — |
| base | obr_pmd_nov2025:23991:5c8f7b5233d93763 (row 23991) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | PSCE in RDEL | 0.5 | — | — |
| base | obr_pmd_nov2025:23997:1a63945e557c2aa7 (row 23997) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Scottish BGA (current) | 1.1 | — | — |
| head | obr_pmd_nov2025:12370:7f7d3d9ec714a95e (row 12370) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Capital gains tax | -35.0 | — | — |
| head | obr_pmd_nov2025:12376:d658edd74795036b (row 12376) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | High-value council tax surcharge | 466.0 | 495.7 | 329.2 |
| head | obr_pmd_nov2025:12382:8ddcecd6a5e1169b (row 12382) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Inheritance tax | -16.1 | — | — |
| head | obr_pmd_nov2025:12388:57698fba46d02c0e (row 12388) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Stamp duty | 15.0 | — | — |
| head | obr_pmd_nov2025:23991:5c8f7b5233d93763 (row 23991) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | PSCE in RDEL | 0.5 | — | — |
| head | obr_pmd_nov2025:23997:1a63945e557c2aa7 (row 23997) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Scottish BGA (current) | 1.1 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__high_value_council_tax_surcharge_2029.json` (sha256 `520aad4bf0c6cddb24dad09d5cccd90fe634cb9fd486d074cee6a0f48247eb6e`), reversal_on_certified_world; baseline dict `{"gov.hmrc.council_tax.high_value_surcharge.amount[1].amount": {"2028-01-01.2030-12-31": 0}, "gov.hmrc.council_tax.high_value_surcharge.amount[2].amount": {"2028-01-01.2030-12-31": 0}, "gov.hmrc.council_tax.high_value_surcharge.amount[3].amount": {"2028-01-01.2030-12-31": 0}, "gov.hmrc.council_tax.high_value_surcharge.amount[4].amount": {"2028-01-01.2030-12-31": 0}}`; reform dict `null`
* head: `results/uk/replays/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_budget_2025/ab2025__high_value_council_tax_surcharge_2029.json` (sha256 `18292f7d37a35d4c72c4bf0c98e9986c3db6f5f6ccad72304755769b46e80485`), reversal_on_certified_world; baseline dict `{"gov.hmrc.council_tax.high_value_surcharge.amount[1].amount": {"2028-01-01.2030-12-31": 0}, "gov.hmrc.council_tax.high_value_surcharge.amount[2].amount": {"2028-01-01.2030-12-31": 0}, "gov.hmrc.council_tax.high_value_surcharge.amount[3].amount": {"2028-01-01.2030-12-31": 0}, "gov.hmrc.council_tax.high_value_surcharge.amount[4].amount": {"2028-01-01.2030-12-31": 0}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__high_value_council_tax_surcharge --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__high_value_council_tax_surcharge_2029
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__high_value_council_tax_surcharge --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_budget_2025/ab2025__high_value_council_tax_surcharge_2029
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
