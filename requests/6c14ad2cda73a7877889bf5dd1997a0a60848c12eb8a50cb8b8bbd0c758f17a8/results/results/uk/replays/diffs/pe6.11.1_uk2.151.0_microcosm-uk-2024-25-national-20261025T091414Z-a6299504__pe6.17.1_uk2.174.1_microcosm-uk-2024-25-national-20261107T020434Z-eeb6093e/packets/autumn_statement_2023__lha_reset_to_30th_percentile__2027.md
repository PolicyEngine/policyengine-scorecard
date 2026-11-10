# Investigation packet: autumn_statement_2023 / autumn_statement_2023__lha_reset_to_30th_percentile / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Local Housing Allowance (LHA): set to the 30th percentile from April 2024
* Flags: numerical
* Base: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`
* Head: `pe6.17.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:21633:5ce95c1559b8bc39 | -1,433.6 | -1,533.9 | -100.3 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:21639:7b87de87a4048332 | — | — | — | — | — |
| measure_year | total | -1,433.6 | -1,533.9 | -100.3 | numerical | move_above_threshold |
| head | housing_benefit | -190.8 | -157.0 | 33.8 | numerical | move_above_threshold |
| head | universal_credit | -1,242.8 | -1,376.9 | -134.1 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:21633:5ce95c1559b8bc39 (row 21633) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | -1,259.9 | -1,433.6 | -1,533.9 |
| base | obr_pmd_nov2025:21639:7b87de87a4048332 (row 21639) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare outside cap | -402.0 | — | — |
| head | obr_pmd_nov2025:21633:5ce95c1559b8bc39 (row 21633) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | -1,259.9 | -1,433.6 | -1,533.9 |
| head | obr_pmd_nov2025:21639:7b87de87a4048332 (row 21639) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare outside cap | -402.0 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2027.json` (sha256 `7155d2038b53c93eb4623285eed1728870aa5be1e8464b17d272aca78c58ebf7`), reversal_on_certified_world; baseline dict `{"gov.dwp.LHA.freeze": {"2024-01-01.2035-12-31": true}}`; reform dict `null`
* head: `results/uk/replays/pe6.17.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2027.json` (sha256 `69cf41b757180c6be95fb735248167e951e6b2a08615337929dc721215e31104`), reversal_on_certified_world; baseline dict `{"gov.dwp.LHA.freeze": {"2024-01-01.2035-12-31": true}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__lha_reset_to_30th_percentile --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2027
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.17.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__lha_reset_to_30th_percentile --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.17.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
