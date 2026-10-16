# Investigation packet: autumn_budget_2025 / ab2025__trust_charges_cap_and_post_departure_trade_profits / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Cap trust charges at £5m for pre-30 October 2024 excluded property trusts for charges applying from 6 April 2025 and close post-departure trade profits loophole from 6 April 2026
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12398:8c0c73f9c548049c | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12404:f577c47dfa4a7ab1 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12398:8c0c73f9c548049c (row 12398) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | 118.0 | — | — |
| head | obr_pmd_nov2025:12404:f577c47dfa4a7ab1 (row 12404) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Inheritance tax | -8.6 | — | — |

## Executed worlds

* base: no artifact
* head: no artifact

## Reproduce

base:

```bash
# This event is absent from this namespace.
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__trust_charges_cap_and_post_departure_trade_profits --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__trust_charges_cap_and_post_departure_trade_profits_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
