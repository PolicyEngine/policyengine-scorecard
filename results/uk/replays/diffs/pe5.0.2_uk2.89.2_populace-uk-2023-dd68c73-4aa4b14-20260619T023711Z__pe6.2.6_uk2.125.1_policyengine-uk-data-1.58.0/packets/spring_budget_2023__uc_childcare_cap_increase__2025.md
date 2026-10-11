# Investigation packet: spring_budget_2023 / spring_budget_2023__uc_childcare_cap_increase / CY2025

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: DWP: increase the maximum support available in Universal Credit for childcare costs
* Flags: numerical
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:20828:196813c189064172 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:20834:e0b34fcdbf83f61a | -1.7 | -228.9 | -227.1 | numerical | move_above_threshold |
| measure_year | total | -1.7 | -228.9 | -227.1 | numerical | move_above_threshold |
| head | universal_credit | -1.7 | -228.9 | -227.1 | numerical | move_above_threshold |

## OBR source cells

| Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---:|---:|---:|
| obr_pmd_nov2025:20828:196813c189064172 (row 20828) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | PSCE in RDEL | 0.0 | — | — |
| obr_pmd_nov2025:20834:e0b34fcdbf83f61a (row 20834) | Spending Measures (Policy measures database) / 2025-26 | 2025-26 | Welfare inside cap | -75.4 | -1.7 | -228.9 |

## Executed worlds

* base: `results/uk/events/spring_budget_2023/spring_budget_2023__uc_childcare_cap_increase_2025.json` (sha256 `d269d29a7d160f2075655e1c5e66835b505d5bf86fb7fa88e36e5787f056fa1f`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.elements.childcare.cap.1": {"2023-01-01.2023-12-31": 646.35, "2024-01-01.2024-12-31": 689.6, "2025-01-01.2025-12-31": 701.32, "2026-01-01.2026-12-31": 727.97, "2027-01-01.2027-12-31": 727.97}, "gov.dwp.universal_credit.elements.childcare.cap.2": {"2023-01-01.2023-12-31": 1108.04, "2024-01-01.2024-12-31": 1182.39, "2025-01-01.2025-12-31": 1202.49, "2026-01-01.2026-12-31": 1248.18, "2027-01-01.2027-12-31": 1248.18}}`; reform dict `null`
* head: `results/uk/replays/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/spring_budget_2023/spring_budget_2023__uc_childcare_cap_increase_2025.json` (sha256 `39e4be7f0a7f66995126004c95802e6b7b690a5a0139ac6062f75662586ecdbc`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.elements.childcare.cap.1": {"2023-01-01.2023-12-31": 646.35, "2024-01-01.2024-12-31": 689.6, "2025-01-01.2025-12-31": 701.32, "2026-01-01.2026-12-31": 727.97, "2027-01-01.2027-12-31": 727.97}, "gov.dwp.universal_credit.elements.childcare.cap.2": {"2023-01-01.2023-12-31": 1108.04, "2024-01-01.2024-12-31": 1182.39, "2025-01-01.2025-12-31": 1202.49, "2026-01-01.2026-12-31": 1248.18, "2027-01-01.2027-12-31": 1248.18}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2023 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --measures spring_budget_2023__uc_childcare_cap_increase --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/spring_budget_2023/spring_budget_2023__uc_childcare_cap_increase_2025
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2023 --variant pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0 --measures spring_budget_2023__uc_childcare_cap_increase --years 2025 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/spring_budget_2023/spring_budget_2023__uc_childcare_cap_increase_2025
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
