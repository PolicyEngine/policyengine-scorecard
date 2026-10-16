# Investigation packet: autumn_budget_2025 / ab2025__business_rates_transitional_relief_and_supplement / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Business Rates: Introduce both a three year Transitional Relief scheme, partially funded by a 1p Transitional Relief Supplement in 2026/27, and a Supporting Small Business scheme from 1 April 2026
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12116:65b4483168ecbcca | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12122:abfda8e927ebb411 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12128:29abe8d3b050e995 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12134:3ed95420cb1fae11 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23647:adcd1ba4a5575cea | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23653:892dd98e94be663a | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23659:de48ef77e56d4708 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12116:65b4483168ecbcca (row 12116) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Business rates | -1,394.0 | — | — |
| head | obr_pmd_nov2025:12122:abfda8e927ebb411 (row 12122) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | 56.7 | — | — |
| head | obr_pmd_nov2025:12128:29abe8d3b050e995 (row 12128) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | NICs | 11.1 | — | — |
| head | obr_pmd_nov2025:12134:3ed95420cb1fae11 (row 12134) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Corporation tax (onshore) | 204.0 | — | — |
| head | obr_pmd_nov2025:23647:adcd1ba4a5575cea (row 23647) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | -266.9 | — | — |
| head | obr_pmd_nov2025:23653:892dd98e94be663a (row 23653) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Locally-financed current expenditure | 850.0 | — | — |
| head | obr_pmd_nov2025:23659:de48ef77e56d4708 (row 23659) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Other AME (current) | -850.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__business_rates_transitional_relief_and_supplement --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__business_rates_transitional_relief_and_supplement_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
