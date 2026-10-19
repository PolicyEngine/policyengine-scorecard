# Investigation packet: spring_budget_2023 / spring_budget_2023__uc_childcare_cap_increase / CY2024

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: DWP: increase the maximum support available in Universal Credit for childcare costs
* Flags: numerical
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.7.6_uk2.137.1_policyengine-uk-data-1.58.2`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:20827:22d8d3be038c9fa2 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:20833:270c17d92e54dca4 | -239.0 | -233.5 | 5.6 | numerical | move_above_threshold |
| measure_year | total | -239.0 | -233.5 | 5.6 | numerical | move_above_threshold |
| head | universal_credit | -239.0 | -233.5 | 5.6 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:20827:22d8d3be038c9fa2 (row 20827) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | PSCE in RDEL | 0.0 | — | — |
| base | obr_pmd_nov2025:20833:270c17d92e54dca4 (row 20833) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Welfare inside cap | -86.8 | -239.0 | -233.5 |
| head | obr_pmd_nov2025:20827:22d8d3be038c9fa2 (row 20827) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | PSCE in RDEL | 0.0 | — | — |
| head | obr_pmd_nov2025:20833:270c17d92e54dca4 (row 20833) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Welfare inside cap | -86.8 | -239.0 | -233.5 |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/spring_budget_2023/spring_budget_2023__uc_childcare_cap_increase_2024.json` (sha256 `6aff0ab74b16a45362b9b32bcfb01f0f07aad2318f9140e8cd83153ba56ab74b`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.elements.childcare.cap.1": {"2023-01-01.2023-12-31": 646.35, "2024-01-01.2024-12-31": 689.6, "2025-01-01.2025-12-31": 701.32, "2026-01-01.2026-12-31": 727.97, "2027-01-01.2027-12-31": 727.97}, "gov.dwp.universal_credit.elements.childcare.cap.2": {"2023-01-01.2023-12-31": 1108.04, "2024-01-01.2024-12-31": 1182.39, "2025-01-01.2025-12-31": 1202.49, "2026-01-01.2026-12-31": 1248.18, "2027-01-01.2027-12-31": 1248.18}}`; reform dict `null`
* head: `results/uk/replays/pe6.7.6_uk2.137.1_policyengine-uk-data-1.58.2/spring_budget_2023/spring_budget_2023__uc_childcare_cap_increase_2024.json` (sha256 `d1af607456c8ae3a3ce542951beb34121b26000f2fb19bd10e82ae741e6be98f`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.elements.childcare.cap.1": {"2023-01-01.2023-12-31": 646.35, "2024-01-01.2024-12-31": 689.6, "2025-01-01.2025-12-31": 701.32, "2026-01-01.2026-12-31": 727.97, "2027-01-01.2027-12-31": 727.97}, "gov.dwp.universal_credit.elements.childcare.cap.2": {"2023-01-01.2023-12-31": 1108.04, "2024-01-01.2024-12-31": 1182.39, "2025-01-01.2025-12-31": 1202.49, "2026-01-01.2026-12-31": 1248.18, "2027-01-01.2027-12-31": 1248.18}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2023 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/spring_budget_2023_measures.json --measures spring_budget_2023__uc_childcare_cap_increase --years 2024 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/spring_budget_2023/spring_budget_2023__uc_childcare_cap_increase_2024
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2023 --variant pe6.7.6_uk2.137.1_policyengine-uk-data-1.58.2 --registry data/uk/events/spring_budget_2023_measures.json --measures spring_budget_2023__uc_childcare_cap_increase --years 2024 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.7.6_uk2.137.1_policyengine-uk-data-1.58.2/spring_budget_2023/spring_budget_2023__uc_childcare_cap_increase_2024
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
