# Investigation packet: autumn_budget_2025 / ab2025__high_value_council_tax_surcharge / CY2025

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: High Value Council Tax Surcharge: Introduce a surcharge on owners of residential properties valued over £2m in England from 1 April 2028
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12366:465503aced3e49c3 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12372:2657bff11b71f228 | — | 0.0 | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12378:39a0da2eb6974545 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12384:01e3de17fd36acfb | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23987:6bb4c3da8a53b910 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23993:3bf572d33c2a90bf | — | — | — | coverage | event_on_head_only |
| measure_year | total | — | 0.0 | — | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12366:465503aced3e49c3 (row 12366) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Capital gains tax | -12.7 | — | — |
| head | obr_pmd_nov2025:12372:2657bff11b71f228 (row 12372) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | High-value council tax surcharge | 0.0 | — | 0.0 |
| head | obr_pmd_nov2025:12378:39a0da2eb6974545 (row 12378) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Inheritance tax | -1.0 | — | — |
| head | obr_pmd_nov2025:12384:01e3de17fd36acfb (row 12384) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Stamp duty | -45.6 | — | — |
| head | obr_pmd_nov2025:23987:6bb4c3da8a53b910 (row 23987) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | PSCE in RDEL | -0.9 | — | — |
| head | obr_pmd_nov2025:23993:3bf572d33c2a90bf (row 23993) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Scottish BGA (current) | -2.1 | — | — |

## Executed worlds

* base: no artifact
* head: `results/uk/replays/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__high_value_council_tax_surcharge_2025.json` (sha256 `c17c47edb6caedc04ce4ed302344acda98002110a186ac7400dee9dea29a3fa0`), reversal_on_certified_world; baseline dict `{"gov.hmrc.council_tax.high_value_surcharge.amount[1].amount": {"2028-01-01.2030-12-31": 0}, "gov.hmrc.council_tax.high_value_surcharge.amount[2].amount": {"2028-01-01.2030-12-31": 0}, "gov.hmrc.council_tax.high_value_surcharge.amount[3].amount": {"2028-01-01.2030-12-31": 0}, "gov.hmrc.council_tax.high_value_surcharge.amount[4].amount": {"2028-01-01.2030-12-31": 0}}`; reform dict `null`

## Reproduce

base:

```bash
# This event is absent from this namespace.
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__high_value_council_tax_surcharge --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__high_value_council_tax_surcharge_2025
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
