# Investigation packet: autumn_statement_2023 / autumn_statement_2023__lha_reset_to_30th_percentile / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Local Housing Allowance (LHA): set to the 30th percentile from April 2024
* Flags: numerical
* Base: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`
* Head: `pe6.18.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:21634:ff94f5b54b89d1ee | -1,480.2 | -1,567.3 | -87.1 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:21640:c223f09f1998ebbe | — | — | — | — | — |
| measure_year | total | -1,480.2 | -1,567.3 | -87.1 | numerical | move_above_threshold |
| head | housing_benefit | -199.0 | -165.7 | 33.4 | numerical | move_above_threshold |
| head | universal_credit | -1,281.2 | -1,401.6 | -120.4 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:21634:ff94f5b54b89d1ee (row 21634) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | -1,273.0 | -1,480.2 | -1,567.3 |
| base | obr_pmd_nov2025:21640:c223f09f1998ebbe (row 21640) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare outside cap | -425.0 | — | — |
| head | obr_pmd_nov2025:21634:ff94f5b54b89d1ee (row 21634) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | -1,273.0 | -1,480.2 | -1,567.3 |
| head | obr_pmd_nov2025:21640:c223f09f1998ebbe (row 21640) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare outside cap | -425.0 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2028.json` (sha256 `5c13f874f51af039a8c8c6b3168c4e1f4462e971be86088512ed8126fbbd3384`), reversal_on_certified_world; baseline dict `{"gov.dwp.LHA.freeze": {"2024-01-01.2035-12-31": true}}`; reform dict `null`
* head: `results/uk/replays/pe6.18.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2028.json` (sha256 `5320e1c4da961eb8422533af2781f48339ede00134a3812e0b58ab537c6799b5`), reversal_on_certified_world; baseline dict `{"gov.dwp.LHA.freeze": {"2024-01-01.2035-12-31": true}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__lha_reset_to_30th_percentile --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2028
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.18.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__lha_reset_to_30th_percentile --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.18.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
