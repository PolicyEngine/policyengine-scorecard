# Investigation packet: autumn_statement_2023 / autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p / CY2023

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance contributions (NICs): 1p cut to the main rate of Class 4 self-employed NICs from April 2024
* Flags: support
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10566:0e8d21e52f88eb57 | 0.0 | — | — | support | supported_on_base_only |
| source_row | obr_pmd_nov2025:10572:2ff1949c7ce7acb3 | 0.0 | — | — | support | supported_on_base_only |
| source_row | obr_pmd_nov2025:10578:668526d85d747acc | — | — | — | — | — |
| source_row | obr_pmd_nov2025:10584:443a5169e8191f85 | — | — | — | support | supported_on_base_only |
| source_row | obr_pmd_nov2025:21479:4eea71bff070729b | 0.0 | — | — | support | supported_on_base_only |
| source_row | obr_pmd_nov2025:21485:54e4e7eb67239171 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21491:d64de9edd1439a8e | — | — | — | — | — |
| measure_year | total | 0.0 | — | — | support | supported_on_base_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10566:0e8d21e52f88eb57 (row 10566) | Tax Measures (Policy measures database) / 2023-24 | 2023-24 | Income tax | 0.0 | 0.0 | — |
| base | obr_pmd_nov2025:10572:2ff1949c7ce7acb3 (row 10572) | Tax Measures (Policy measures database) / 2023-24 | 2023-24 | NICs | 0.0 | 0.0 | — |
| base | obr_pmd_nov2025:10578:668526d85d747acc (row 10578) | Tax Measures (Policy measures database) / 2023-24 | 2023-24 | Corporation tax (onshore) | 0.0 | — | — |
| base | obr_pmd_nov2025:10584:443a5169e8191f85 (row 10584) | Tax Measures (Policy measures database) / 2023-24 | 2023-24 | Capital gains tax | 0.0 | — | — |
| base | obr_pmd_nov2025:21479:4eea71bff070729b (row 21479) | Spending Measures (Policy measures database) / 2023-24 | 2023-24 | Welfare inside cap | 0.0 | 0.0 | — |
| base | obr_pmd_nov2025:21485:54e4e7eb67239171 (row 21485) | Spending Measures (Policy measures database) / 2023-24 | 2023-24 | PSCE in RDEL | 0.0 | — | — |
| base | obr_pmd_nov2025:21491:d64de9edd1439a8e (row 21491) | Spending Measures (Policy measures database) / 2023-24 | 2023-24 | Scottish BGA (current) | 0.0 | — | — |
| head | obr_pmd_nov2025:10566:0e8d21e52f88eb57 (row 10566) | Tax Measures (Policy measures database) / 2023-24 | 2023-24 | Income tax | 0.0 | 0.0 | — |
| head | obr_pmd_nov2025:10572:2ff1949c7ce7acb3 (row 10572) | Tax Measures (Policy measures database) / 2023-24 | 2023-24 | NICs | 0.0 | 0.0 | — |
| head | obr_pmd_nov2025:10578:668526d85d747acc (row 10578) | Tax Measures (Policy measures database) / 2023-24 | 2023-24 | Corporation tax (onshore) | 0.0 | — | — |
| head | obr_pmd_nov2025:10584:443a5169e8191f85 (row 10584) | Tax Measures (Policy measures database) / 2023-24 | 2023-24 | Capital gains tax | 0.0 | — | — |
| head | obr_pmd_nov2025:21479:4eea71bff070729b (row 21479) | Spending Measures (Policy measures database) / 2023-24 | 2023-24 | Welfare inside cap | 0.0 | 0.0 | — |
| head | obr_pmd_nov2025:21485:54e4e7eb67239171 (row 21485) | Spending Measures (Policy measures database) / 2023-24 | 2023-24 | PSCE in RDEL | 0.0 | — | — |
| head | obr_pmd_nov2025:21491:d64de9edd1439a8e (row 21491) | Spending Measures (Policy measures database) / 2023-24 | 2023-24 | Scottish BGA (current) | 0.0 | — | — |

## Executed worlds

* base: `results/uk/events/autumn_statement_2023/autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p_2023.json` (sha256 `98ed1678b547e14c03f26f8b32c4e7e4accf63d65ed7d5300839c00daa21628a`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_4.rates.main": {"2024-01-01.2035-12-31": 0.07}}`; reform dict `null`
* head: no artifact

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p --years 2023 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/autumn_statement_2023/autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p_2023
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p --years 2023 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_statement_2023/autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p_2023
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
