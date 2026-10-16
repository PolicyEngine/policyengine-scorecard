# Investigation packet: autumn_budget_2025 / ab2025__high_value_council_tax_surcharge / CY2029

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: High Value Council Tax Surcharge: Introduce a surcharge on owners of residential properties valued over £2m in England from 1 April 2028
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12370:7f7d3d9ec714a95e | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12376:d658edd74795036b | — | 495.7 | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12382:8ddcecd6a5e1169b | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12388:57698fba46d02c0e | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23991:5c8f7b5233d93763 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23997:1a63945e557c2aa7 | — | — | — | coverage | event_on_head_only |
| measure_year | total | — | 495.7 | — | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12370:7f7d3d9ec714a95e (row 12370) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Capital gains tax | -35.0 | — | — |
| head | obr_pmd_nov2025:12376:d658edd74795036b (row 12376) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | High-value council tax surcharge | 466.0 | — | 495.7 |
| head | obr_pmd_nov2025:12382:8ddcecd6a5e1169b (row 12382) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Inheritance tax | -16.1 | — | — |
| head | obr_pmd_nov2025:12388:57698fba46d02c0e (row 12388) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Stamp duty | 15.0 | — | — |
| head | obr_pmd_nov2025:23991:5c8f7b5233d93763 (row 23991) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | PSCE in RDEL | 0.5 | — | — |
| head | obr_pmd_nov2025:23997:1a63945e557c2aa7 (row 23997) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Scottish BGA (current) | 1.1 | — | — |

## Executed worlds

* base: no artifact
* head: `results/uk/replays/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__high_value_council_tax_surcharge_2029.json` (sha256 `532bb9c4576430c59484f54dae9b9fd5557605bbbe53388db967571d90091c88`), reversal_on_certified_world; baseline dict `{"gov.hmrc.council_tax.high_value_surcharge.amount[1].amount": {"2028-01-01.2030-12-31": 0}, "gov.hmrc.council_tax.high_value_surcharge.amount[2].amount": {"2028-01-01.2030-12-31": 0}, "gov.hmrc.council_tax.high_value_surcharge.amount[3].amount": {"2028-01-01.2030-12-31": 0}, "gov.hmrc.council_tax.high_value_surcharge.amount[4].amount": {"2028-01-01.2030-12-31": 0}}`; reform dict `null`

## Reproduce

base:

```bash
# This event is absent from this namespace.
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__high_value_council_tax_surcharge --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__high_value_council_tax_surcharge_2029
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
