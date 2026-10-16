# Investigation packet: autumn_budget_2025 / ab2025__vct_and_eis_investment_limits_increased / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Venture Capital Schemes: Increase the Venture Capital Trust (VCT) scheme and the Enterprise Investment Scheme (EIS) annual and lifetime investment limits and the gross assets test from 6 April 2026
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12188:572e4dcb78229daf | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12194:2446b4fc21bc2b6d | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23695:cab75fedc3c96cf1 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23701:95e4b32ae876c8e0 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12188:572e4dcb78229daf (row 12188) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Capital gains tax | 0.0 | — | — |
| head | obr_pmd_nov2025:12194:2446b4fc21bc2b6d (row 12194) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | -53.0 | — | — |
| head | obr_pmd_nov2025:23695:cab75fedc3c96cf1 (row 23695) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | -1.0 | — | — |
| head | obr_pmd_nov2025:23701:95e4b32ae876c8e0 (row 23701) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | -4.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__vct_and_eis_investment_limits_increased --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__vct_and_eis_investment_limits_increased_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
