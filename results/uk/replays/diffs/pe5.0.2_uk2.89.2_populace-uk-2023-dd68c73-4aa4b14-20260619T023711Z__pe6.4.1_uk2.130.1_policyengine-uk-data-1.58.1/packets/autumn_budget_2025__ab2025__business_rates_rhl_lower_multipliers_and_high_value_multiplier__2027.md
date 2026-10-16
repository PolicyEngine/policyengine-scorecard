# Investigation packet: autumn_budget_2025 / ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Business Rates: Introduce two new lower multipliers for eligible retail, hospitality and leisure properties funded by a new high-value multiplier from 1 April 2026
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12140:a3d782103cef363f | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12146:2d219d4b4f3ab417 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12152:1844c70b0f3ad4f0 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12158:1f8914465750eaf4 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23665:62c9ac17549a3961 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23671:f9a3ec3888ff65c7 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23677:cab316c5284835ef | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12140:a3d782103cef363f (row 12140) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Business rates | 30.6 | — | — |
| head | obr_pmd_nov2025:12146:2d219d4b4f3ab417 (row 12146) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | 22.5 | — | — |
| head | obr_pmd_nov2025:12152:1844c70b0f3ad4f0 (row 12152) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | NICs | 4.5 | — | — |
| head | obr_pmd_nov2025:12158:1f8914465750eaf4 (row 12158) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Corporation tax (onshore) | -22.2 | — | — |
| head | obr_pmd_nov2025:23665:62c9ac17549a3961 (row 23665) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | 5.9 | — | — |
| head | obr_pmd_nov2025:23671:f9a3ec3888ff65c7 (row 23671) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Locally-financed current expenditure | -19.5 | — | — |
| head | obr_pmd_nov2025:23677:cab316c5284835ef (row 23677) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Other AME (current) | 19.5 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
