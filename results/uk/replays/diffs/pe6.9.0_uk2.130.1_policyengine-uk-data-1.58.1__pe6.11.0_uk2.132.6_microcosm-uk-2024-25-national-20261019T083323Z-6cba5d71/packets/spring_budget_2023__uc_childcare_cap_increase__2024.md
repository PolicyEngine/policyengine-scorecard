# Investigation packet: spring_budget_2023 / spring_budget_2023__uc_childcare_cap_increase / CY2024

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: DWP: increase the maximum support available in Universal Credit for childcare costs
* Flags: numerical
* Base: `pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:20827:22d8d3be038c9fa2 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:20833:270c17d92e54dca4 | -239.0 | -36.5 | 202.5 | numerical | move_above_threshold |
| measure_year | total | -239.0 | -36.5 | 202.5 | numerical | move_above_threshold |
| head | universal_credit | -239.0 | -36.5 | 202.5 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:20827:22d8d3be038c9fa2 (row 20827) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | PSCE in RDEL | 0.0 | — | — |
| base | obr_pmd_nov2025:20833:270c17d92e54dca4 (row 20833) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Welfare inside cap | -86.8 | -239.0 | -36.5 |
| head | obr_pmd_nov2025:20827:22d8d3be038c9fa2 (row 20827) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | PSCE in RDEL | 0.0 | — | — |
| head | obr_pmd_nov2025:20833:270c17d92e54dca4 (row 20833) | Spending Measures (Policy measures database) / 2024-25 | 2024-25 | Welfare inside cap | -86.8 | -239.0 | -36.5 |

## Executed worlds

* base: `results/uk/replays/pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1/spring_budget_2023/spring_budget_2023__uc_childcare_cap_increase_2024.json` (sha256 `6255dc09bfba81b42e7f4eb11dd9fa2b84a950b76bb31a43b33e5e0ab63930f6`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.elements.childcare.cap.1": {"2023-01-01.2023-12-31": 646.35, "2024-01-01.2024-12-31": 689.6, "2025-01-01.2025-12-31": 701.32, "2026-01-01.2026-12-31": 727.97, "2027-01-01.2027-12-31": 727.97}, "gov.dwp.universal_credit.elements.childcare.cap.2": {"2023-01-01.2023-12-31": 1108.04, "2024-01-01.2024-12-31": 1182.39, "2025-01-01.2025-12-31": 1202.49, "2026-01-01.2026-12-31": 1248.18, "2027-01-01.2027-12-31": 1248.18}}`; reform dict `null`
* head: `results/uk/replays/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/spring_budget_2023/spring_budget_2023__uc_childcare_cap_increase_2024.json` (sha256 `4317114c58531a1f0485e39ce9fe12df4da1aa77df8b4394aacc1c0cc3de73c7`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.elements.childcare.cap.1": {"2023-01-01.2023-12-31": 646.35, "2024-01-01.2024-12-31": 689.6, "2025-01-01.2025-12-31": 701.32, "2026-01-01.2026-12-31": 727.97, "2027-01-01.2027-12-31": 727.97}, "gov.dwp.universal_credit.elements.childcare.cap.2": {"2023-01-01.2023-12-31": 1108.04, "2024-01-01.2024-12-31": 1182.39, "2025-01-01.2025-12-31": 1202.49, "2026-01-01.2026-12-31": 1248.18, "2027-01-01.2027-12-31": 1248.18}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2023 --variant pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/spring_budget_2023_measures.json --measures spring_budget_2023__uc_childcare_cap_increase --years 2024 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1/spring_budget_2023/spring_budget_2023__uc_childcare_cap_increase_2024
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2023 --variant pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71 --registry data/uk/events/spring_budget_2023_measures.json --measures spring_budget_2023__uc_childcare_cap_increase --years 2024 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/spring_budget_2023/spring_budget_2023__uc_childcare_cap_increase_2024
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
