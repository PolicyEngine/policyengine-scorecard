# Investigation packet: autumn_budget_2025 / ab2025__vct_and_eis_investment_limits_increased / CY2025

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Venture Capital Schemes: Increase the Venture Capital Trust (VCT) scheme and the Enterprise Investment Scheme (EIS) annual and lifetime investment limits and the gross assets test from 6 April 2026
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12186:4696d7f8e8918628 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12192:6c94267e428e16e3 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23693:6039055e2cbe7056 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23699:88e3a06d83247c3b | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12186:4696d7f8e8918628 (row 12186) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Capital gains tax | 0.0 | — | — |
| head | obr_pmd_nov2025:12192:6c94267e428e16e3 (row 12192) | Tax Measures (Policy measures database) / 2025-26 | 2025-26 | Income tax | 0.0 | — | — |
| head | obr_pmd_nov2025:23693:6039055e2cbe7056 (row 23693) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | PSCE in RDEL | 0.0 | — | — |
| head | obr_pmd_nov2025:23699:88e3a06d83247c3b (row 23699) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Scottish BGA (current) | 0.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__vct_and_eis_investment_limits_increased --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__vct_and_eis_investment_limits_increased_2025
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
