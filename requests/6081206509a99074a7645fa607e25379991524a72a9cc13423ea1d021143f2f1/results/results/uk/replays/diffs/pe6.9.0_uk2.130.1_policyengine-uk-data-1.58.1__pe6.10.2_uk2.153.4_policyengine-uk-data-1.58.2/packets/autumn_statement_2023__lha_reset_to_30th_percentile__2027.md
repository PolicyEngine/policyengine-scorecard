# Investigation packet: autumn_statement_2023 / autumn_statement_2023__lha_reset_to_30th_percentile / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Local Housing Allowance (LHA): set to the 30th percentile from April 2024
* Flags: numerical
* Base: `pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.10.2_uk2.153.4_policyengine-uk-data-1.58.2`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:21633:5ce95c1559b8bc39 | -1,979.1 | -1,954.9 | 24.2 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:21639:7b87de87a4048332 | — | — | — | — | — |
| measure_year | total | -1,979.1 | -1,954.9 | 24.2 | numerical | move_above_threshold |
| head | housing_benefit | -163.6 | -161.7 | 1.9 | numerical | move_above_threshold |
| head | universal_credit | -1,815.6 | -1,793.2 | 22.4 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:21633:5ce95c1559b8bc39 (row 21633) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | -1,259.9 | -1,979.1 | -1,954.9 |
| base | obr_pmd_nov2025:21639:7b87de87a4048332 (row 21639) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare outside cap | -402.0 | — | — |
| head | obr_pmd_nov2025:21633:5ce95c1559b8bc39 (row 21633) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | -1,259.9 | -1,979.1 | -1,954.9 |
| head | obr_pmd_nov2025:21639:7b87de87a4048332 (row 21639) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare outside cap | -402.0 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2027.json` (sha256 `58200016c9c1a49b7fe9a9315250f8759bb78ec5d67693b4995d998a062fc58a`), reversal_on_certified_world; baseline dict `{"gov.dwp.LHA.freeze": {"2024-01-01.2035-12-31": true}}`; reform dict `null`
* head: `results/uk/replays/pe6.10.2_uk2.153.4_policyengine-uk-data-1.58.2/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2027.json` (sha256 `d8fc23105d4812938b631b9c3aa63a7bd022de019876d13b0a262fc703c67648`), reversal_on_certified_world; baseline dict `{"gov.dwp.LHA.freeze": {"2024-01-01.2035-12-31": true}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__lha_reset_to_30th_percentile --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2027
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.10.2_uk2.153.4_policyengine-uk-data-1.58.2 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__lha_reset_to_30th_percentile --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.10.2_uk2.153.4_policyengine-uk-data-1.58.2/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
