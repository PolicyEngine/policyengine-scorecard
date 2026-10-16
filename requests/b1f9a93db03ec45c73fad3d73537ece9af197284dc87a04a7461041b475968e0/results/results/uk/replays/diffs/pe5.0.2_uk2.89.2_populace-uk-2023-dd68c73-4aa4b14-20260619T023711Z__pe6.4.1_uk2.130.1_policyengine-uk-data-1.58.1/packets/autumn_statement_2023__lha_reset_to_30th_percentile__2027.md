# Investigation packet: autumn_statement_2023 / autumn_statement_2023__lha_reset_to_30th_percentile / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Local Housing Allowance (LHA): set to the 30th percentile from April 2024
* Flags: numerical
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:21633:5ce95c1559b8bc39 | -859.1 | -1,979.1 | -1,120.1 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:21639:7b87de87a4048332 | — | — | — | — | — |
| measure_year | total | -859.1 | -1,979.1 | -1,120.1 | numerical | move_above_threshold |
| head | housing_benefit | -83.6 | -163.6 | -80.0 | numerical | move_above_threshold |
| head | universal_credit | -775.5 | -1,815.6 | -1,040.1 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:21633:5ce95c1559b8bc39 (row 21633) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | -1,259.9 | -859.1 | -1,979.1 |
| base | obr_pmd_nov2025:21639:7b87de87a4048332 (row 21639) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare outside cap | -402.0 | — | — |
| head | obr_pmd_nov2025:21633:5ce95c1559b8bc39 (row 21633) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | -1,259.9 | -859.1 | -1,979.1 |
| head | obr_pmd_nov2025:21639:7b87de87a4048332 (row 21639) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare outside cap | -402.0 | — | — |

## Executed worlds

* base: `results/uk/events/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2027.json` (sha256 `508c7d7ee1bcbd331d0c7da32e17240dd120cf1f6f8e07d0acc98de13eacdc74`), reversal_on_certified_world; baseline dict `{"gov.dwp.LHA.freeze": {"2024-01-01.2035-12-31": true}}`; reform dict `null`
* head: `results/uk/replays/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2027.json` (sha256 `20643a109ffa67d2192db42ec2a72f1f2e470a58fd16ac477eaa2f36d52316e9`), reversal_on_certified_world; baseline dict `{"gov.dwp.LHA.freeze": {"2024-01-01.2035-12-31": true}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__lha_reset_to_30th_percentile --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2027
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__lha_reset_to_30th_percentile --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
