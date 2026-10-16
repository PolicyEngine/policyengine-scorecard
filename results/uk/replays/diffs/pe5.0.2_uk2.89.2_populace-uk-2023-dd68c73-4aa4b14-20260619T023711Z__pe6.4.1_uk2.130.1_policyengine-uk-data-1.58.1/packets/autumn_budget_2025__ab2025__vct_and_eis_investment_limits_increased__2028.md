# Investigation packet: autumn_budget_2025 / ab2025__vct_and_eis_investment_limits_increased / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Venture Capital Schemes: Increase the Venture Capital Trust (VCT) scheme and the Enterprise Investment Scheme (EIS) annual and lifetime investment limits and the gross assets test from 6 April 2026
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12189:1ebb14219911bb9b | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12195:c8194f2514775c90 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23696:c8db8ef9be1ab61f | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23702:5a579cf4e775ce5a | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12189:1ebb14219911bb9b (row 12189) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Capital gains tax | 0.0 | — | — |
| head | obr_pmd_nov2025:12195:c8194f2514775c90 (row 12195) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | -42.0 | — | — |
| head | obr_pmd_nov2025:23696:c8db8ef9be1ab61f (row 23696) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | -1.0 | — | — |
| head | obr_pmd_nov2025:23702:5a579cf4e775ce5a (row 23702) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | -3.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__vct_and_eis_investment_limits_increased --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__vct_and_eis_investment_limits_increased_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
