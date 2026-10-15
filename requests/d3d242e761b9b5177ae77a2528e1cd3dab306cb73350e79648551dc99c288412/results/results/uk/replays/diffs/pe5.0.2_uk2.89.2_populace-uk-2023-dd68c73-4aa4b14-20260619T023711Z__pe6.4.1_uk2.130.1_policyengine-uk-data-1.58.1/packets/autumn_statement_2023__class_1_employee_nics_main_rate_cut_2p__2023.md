# Investigation packet: autumn_statement_2023 / autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p / CY2023

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance contributions (NICs): 2p cut to the main rate of Class 1 employee NICs from January 2024
* Flags: support
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10542:89ab4668e579ad56 | — | — | — | support | supported_on_base_only |
| source_row | obr_pmd_nov2025:10548:f2f563200611f223 | — | — | — | support | supported_on_base_only |
| source_row | obr_pmd_nov2025:10554:cd921be12b9ab588 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:10560:3a6d16cff489f44c | — | — | — | support | supported_on_base_only |
| source_row | obr_pmd_nov2025:21461:f9e31391303b473d | — | — | — | support | supported_on_base_only |
| source_row | obr_pmd_nov2025:21467:50ff3ce409415888 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:21473:ab05b76b7f2d2bb3 | — | — | — | — | — |
| measure_year | total | 0.0 | — | — | support | supported_on_base_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10542:89ab4668e579ad56 (row 10542) | Tax Measures (Policy measures database) / 2023-24 | 2023-24 | Income tax | 84.3 | — | — |
| base | obr_pmd_nov2025:10548:f2f563200611f223 (row 10548) | Tax Measures (Policy measures database) / 2023-24 | 2023-24 | NICs | -2,339.0 | — | — |
| base | obr_pmd_nov2025:10554:cd921be12b9ab588 (row 10554) | Tax Measures (Policy measures database) / 2023-24 | 2023-24 | Corporation tax (onshore) | -6.7 | — | — |
| base | obr_pmd_nov2025:10560:3a6d16cff489f44c (row 10560) | Tax Measures (Policy measures database) / 2023-24 | 2023-24 | Capital gains tax | 0.0 | — | — |
| base | obr_pmd_nov2025:21461:f9e31391303b473d (row 21461) | Spending Measures (Policy measures database) / 2023-24 | 2023-24 | Welfare inside cap | 25.6 | — | — |
| base | obr_pmd_nov2025:21467:50ff3ce409415888 (row 21467) | Spending Measures (Policy measures database) / 2023-24 | 2023-24 | PSCE in RDEL | 0.4 | — | — |
| base | obr_pmd_nov2025:21473:ab05b76b7f2d2bb3 (row 21473) | Spending Measures (Policy measures database) / 2023-24 | 2023-24 | Scottish BGA (current) | 6.1 | — | — |
| head | obr_pmd_nov2025:10542:89ab4668e579ad56 (row 10542) | Tax Measures (Policy measures database) / 2023-24 | 2023-24 | Income tax | 84.3 | — | — |
| head | obr_pmd_nov2025:10548:f2f563200611f223 (row 10548) | Tax Measures (Policy measures database) / 2023-24 | 2023-24 | NICs | -2,339.0 | — | — |
| head | obr_pmd_nov2025:10554:cd921be12b9ab588 (row 10554) | Tax Measures (Policy measures database) / 2023-24 | 2023-24 | Corporation tax (onshore) | -6.7 | — | — |
| head | obr_pmd_nov2025:10560:3a6d16cff489f44c (row 10560) | Tax Measures (Policy measures database) / 2023-24 | 2023-24 | Capital gains tax | 0.0 | — | — |
| head | obr_pmd_nov2025:21461:f9e31391303b473d (row 21461) | Spending Measures (Policy measures database) / 2023-24 | 2023-24 | Welfare inside cap | 25.6 | — | — |
| head | obr_pmd_nov2025:21467:50ff3ce409415888 (row 21467) | Spending Measures (Policy measures database) / 2023-24 | 2023-24 | PSCE in RDEL | 0.4 | — | — |
| head | obr_pmd_nov2025:21473:ab05b76b7f2d2bb3 (row 21473) | Spending Measures (Policy measures database) / 2023-24 | 2023-24 | Scottish BGA (current) | 6.1 | — | — |

## Executed worlds

* base: `results/uk/events/autumn_statement_2023/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p_2023.json` (sha256 `4ad9569c50e598ab5ad1635d16df7d34ed2b5a8ce3baab3fb905ff34a60eee9c`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_1.rates.employee.main": {"2024-01-01.2035-12-31": 0.1}}`; reform dict `null`
* head: no artifact

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p --years 2023 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/autumn_statement_2023/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p_2023
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_statement_2023 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_statement_2023_measures.json --measures autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p --years 2023 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_statement_2023/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p_2023
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
