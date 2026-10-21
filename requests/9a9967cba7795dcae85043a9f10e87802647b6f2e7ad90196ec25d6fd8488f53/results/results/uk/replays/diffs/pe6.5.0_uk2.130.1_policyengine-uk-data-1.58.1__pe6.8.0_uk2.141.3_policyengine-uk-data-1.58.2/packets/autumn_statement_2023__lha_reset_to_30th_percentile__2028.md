# Investigation packet: autumn_statement_2023 / autumn_statement_2023__lha_reset_to_30th_percentile / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Local Housing Allowance (LHA): set to the 30th percentile from April 2024
* Flags: numerical
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.8.0_uk2.141.3_policyengine-uk-data-1.58.2`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:21634:ff94f5b54b89d1ee | -2,000.2 | -2,031.8 | -31.7 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:21640:c223f09f1998ebbe | — | — | — | — | — |
| measure_year | total | -2,000.2 | -2,031.8 | -31.7 | numerical | move_above_threshold |
| head | housing_benefit | -169.2 | -167.1 | 2.1 | numerical | move_above_threshold |
| head | universal_credit | -1,831.0 | -1,864.8 | -33.8 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:21634:ff94f5b54b89d1ee (row 21634) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | -1,273.0 | -2,000.2 | -2,031.8 |
| base | obr_pmd_nov2025:21640:c223f09f1998ebbe (row 21640) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare outside cap | -425.0 | — | — |
| head | obr_pmd_nov2025:21634:ff94f5b54b89d1ee (row 21634) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | -1,273.0 | -2,000.2 | -2,031.8 |
| head | obr_pmd_nov2025:21640:c223f09f1998ebbe (row 21640) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare outside cap | -425.0 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2028.json` (sha256 `2e3843d7652528d7a89efc91b4ed5abac220b927abbb84bbb9d8520d23097edc`), reversal_on_certified_world; baseline dict `{"gov.dwp.LHA.freeze": {"2024-01-01.2035-12-31": true}}`; reform dict `null`
* head: `results/uk/replays/pe6.8.0_uk2.141.3_policyengine-uk-data-1.58.2/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2028.json` (sha256 `2383b495032bec8aa183fee7ec279a67bd721ba12ee055d87b55a2f9d59b2f15`), reversal_on_certified_world; baseline dict `{"gov.dwp.LHA.freeze": {"2024-01-01.2035-12-31": true}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__lha_reset_to_30th_percentile --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2028
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.8.0_uk2.141.3_policyengine-uk-data-1.58.2 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__lha_reset_to_30th_percentile --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.8.0_uk2.141.3_policyengine-uk-data-1.58.2/autumn_statement_2023/autumn_statement_2023__lha_reset_to_30th_percentile_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
