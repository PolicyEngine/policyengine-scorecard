# Investigation packet: autumn_budget_2025 / ab2025__vct_and_eis_investment_limits_increased / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Venture Capital Schemes: Increase the Venture Capital Trust (VCT) scheme and the Enterprise Investment Scheme (EIS) annual and lifetime investment limits and the gross assets test from 6 April 2026
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12187:4a024d61d872c669 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12193:fdabf9588b22decb | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23694:c5c419c5d6c10e7b | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23700:f247db930c37dbac | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12187:4a024d61d872c669 (row 12187) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Capital gains tax | 0.0 | — | — |
| head | obr_pmd_nov2025:12193:fdabf9588b22decb (row 12193) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Income tax | 0.0 | — | — |
| head | obr_pmd_nov2025:23694:c5c419c5d6c10e7b (row 23694) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSCE in RDEL | 0.0 | — | — |
| head | obr_pmd_nov2025:23700:f247db930c37dbac (row 23700) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Scottish BGA (current) | 0.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__vct_and_eis_investment_limits_increased --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__vct_and_eis_investment_limits_increased_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
