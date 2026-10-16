# Investigation packet: autumn_budget_2025 / ab2025__vct_and_eis_investment_limits_increased / CY2029

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Venture Capital Schemes: Increase the Venture Capital Trust (VCT) scheme and the Enterprise Investment Scheme (EIS) annual and lifetime investment limits and the gross assets test from 6 April 2026
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12190:1a6af42d1f6c4619 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12196:2474c0294ef876ba | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23697:3b20fad56d800e9a | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23703:aa36103f1ea2589f | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12190:1a6af42d1f6c4619 (row 12190) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Capital gains tax | -5.0 | — | — |
| head | obr_pmd_nov2025:12196:2474c0294ef876ba (row 12196) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Income tax | -43.0 | — | — |
| head | obr_pmd_nov2025:23697:3b20fad56d800e9a (row 23697) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | PSCE in RDEL | -1.0 | — | — |
| head | obr_pmd_nov2025:23703:aa36103f1ea2589f (row 23703) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Scottish BGA (current) | -3.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__vct_and_eis_investment_limits_increased --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__vct_and_eis_investment_limits_increased_2029
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
