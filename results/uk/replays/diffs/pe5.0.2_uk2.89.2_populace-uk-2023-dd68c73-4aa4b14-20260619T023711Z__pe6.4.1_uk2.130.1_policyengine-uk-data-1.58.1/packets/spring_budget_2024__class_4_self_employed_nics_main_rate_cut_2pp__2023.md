# Investigation packet: spring_budget_2024 / spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp / CY2023

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: National Insurance contributions (NICs): 2 percentage point cut to the main rate of Class 4 self-employed NICs from 6 April 2024
* Flags: support
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:10968:f0c2d5c4f10ba12c | 0.0 | — | — | support | supported_on_base_only |
| source_row | obr_pmd_nov2025:10974:fdd0e608076292a8 | 0.0 | — | — | support | supported_on_base_only |
| source_row | obr_pmd_nov2025:10980:deff8921a24aba7e | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22187:cc8ffca6f2f5e590 | 0.0 | — | — | support | supported_on_base_only |
| source_row | obr_pmd_nov2025:22193:b3628ed306ea8ac5 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22199:1f16d2f22987a987 | — | — | — | — | — |
| measure_year | total | 0.0 | — | — | support | supported_on_base_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:10968:f0c2d5c4f10ba12c (row 10968) | Tax Measures (Policy measures database) / 2023-24 | 2023-24 | Income tax | 0.0 | 0.0 | — |
| base | obr_pmd_nov2025:10974:fdd0e608076292a8 (row 10974) | Tax Measures (Policy measures database) / 2023-24 | 2023-24 | NICs | 0.0 | 0.0 | — |
| base | obr_pmd_nov2025:10980:deff8921a24aba7e (row 10980) | Tax Measures (Policy measures database) / 2023-24 | 2023-24 | Corporation tax (onshore) | 0.0 | — | — |
| base | obr_pmd_nov2025:22187:cc8ffca6f2f5e590 (row 22187) | Spending Measures (Policy measures database) / 2023-24 | 2023-24 | Welfare inside cap | 0.0 | 0.0 | — |
| base | obr_pmd_nov2025:22193:b3628ed306ea8ac5 (row 22193) | Spending Measures (Policy measures database) / 2023-24 | 2023-24 | PSCE in RDEL | 0.0 | — | — |
| base | obr_pmd_nov2025:22199:1f16d2f22987a987 (row 22199) | Spending Measures (Policy measures database) / 2023-24 | 2023-24 | Scottish BGA (current) | 0.0 | — | — |
| head | obr_pmd_nov2025:10968:f0c2d5c4f10ba12c (row 10968) | Tax Measures (Policy measures database) / 2023-24 | 2023-24 | Income tax | 0.0 | 0.0 | — |
| head | obr_pmd_nov2025:10974:fdd0e608076292a8 (row 10974) | Tax Measures (Policy measures database) / 2023-24 | 2023-24 | NICs | 0.0 | 0.0 | — |
| head | obr_pmd_nov2025:10980:deff8921a24aba7e (row 10980) | Tax Measures (Policy measures database) / 2023-24 | 2023-24 | Corporation tax (onshore) | 0.0 | — | — |
| head | obr_pmd_nov2025:22187:cc8ffca6f2f5e590 (row 22187) | Spending Measures (Policy measures database) / 2023-24 | 2023-24 | Welfare inside cap | 0.0 | 0.0 | — |
| head | obr_pmd_nov2025:22193:b3628ed306ea8ac5 (row 22193) | Spending Measures (Policy measures database) / 2023-24 | 2023-24 | PSCE in RDEL | 0.0 | — | — |
| head | obr_pmd_nov2025:22199:1f16d2f22987a987 (row 22199) | Spending Measures (Policy measures database) / 2023-24 | 2023-24 | Scottish BGA (current) | 0.0 | — | — |

## Executed worlds

* base: `results/uk/events/spring_budget_2024/spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp_2023.json` (sha256 `5c540b7158ad426f82023df034744c02507ed4a4aa56bd1944458fed0b96aeb6`), reversal_on_certified_world; baseline dict `{"gov.hmrc.national_insurance.class_4.rates.main": {"2024-01-01.2035-12-31": 0.08}}`; reform dict `null`
* head: no artifact

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp --years 2023 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/spring_budget_2024/spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp_2023
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2024 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/spring_budget_2024_measures.json --measures spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp --years 2023 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/spring_budget_2024/spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp_2023
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
