# Investigation packet: spring_budget_2023 / spring_budget_2023__uc_childcare_cap_increase / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: DWP: increase the maximum support available in Universal Credit for childcare costs
* Flags: numerical
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.9.0_uk2.142.0_policyengine-uk-data-1.59.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:20830:0a15663b3de35bc8 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:20836:76beca3818ed1fe1 | -266.0 | -296.0 | -30.0 | numerical | move_above_threshold |
| measure_year | total | -266.0 | -296.0 | -30.0 | numerical | move_above_threshold |
| head | universal_credit | -266.0 | -296.0 | -30.0 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:20830:0a15663b3de35bc8 (row 20830) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | 0.0 | — | — |
| base | obr_pmd_nov2025:20836:76beca3818ed1fe1 (row 20836) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | -86.8 | -266.0 | -296.0 |
| head | obr_pmd_nov2025:20830:0a15663b3de35bc8 (row 20830) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | 0.0 | — | — |
| head | obr_pmd_nov2025:20836:76beca3818ed1fe1 (row 20836) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | -86.8 | -266.0 | -296.0 |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/spring_budget_2023/spring_budget_2023__uc_childcare_cap_increase_2027.json` (sha256 `ba12f958842a1ceab1fd3b6f11cd788d63a4e33f29c1c29cb648a3114b4d96f8`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.elements.childcare.cap.1": {"2023-01-01.2023-12-31": 646.35, "2024-01-01.2024-12-31": 689.6, "2025-01-01.2025-12-31": 701.32, "2026-01-01.2026-12-31": 727.97, "2027-01-01.2027-12-31": 727.97}, "gov.dwp.universal_credit.elements.childcare.cap.2": {"2023-01-01.2023-12-31": 1108.04, "2024-01-01.2024-12-31": 1182.39, "2025-01-01.2025-12-31": 1202.49, "2026-01-01.2026-12-31": 1248.18, "2027-01-01.2027-12-31": 1248.18}}`; reform dict `null`
* head: `results/uk/replays/pe6.9.0_uk2.142.0_policyengine-uk-data-1.59.1/spring_budget_2023/spring_budget_2023__uc_childcare_cap_increase_2027.json` (sha256 `206506f71a6ff9a5e95a1b4a1b11ff2a7a229df24fe7a88ff8fcdcd841023379`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.elements.childcare.cap.1": {"2023-01-01.2023-12-31": 646.35, "2024-01-01.2024-12-31": 689.6, "2025-01-01.2025-12-31": 701.32, "2026-01-01.2026-12-31": 727.97, "2027-01-01.2027-12-31": 727.97}, "gov.dwp.universal_credit.elements.childcare.cap.2": {"2023-01-01.2023-12-31": 1108.04, "2024-01-01.2024-12-31": 1182.39, "2025-01-01.2025-12-31": 1202.49, "2026-01-01.2026-12-31": 1248.18, "2027-01-01.2027-12-31": 1248.18}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2023 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/spring_budget_2023_measures.json --measures spring_budget_2023__uc_childcare_cap_increase --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/spring_budget_2023/spring_budget_2023__uc_childcare_cap_increase_2027
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2023 --variant pe6.9.0_uk2.142.0_policyengine-uk-data-1.59.1 --registry data/uk/events/spring_budget_2023_measures.json --measures spring_budget_2023__uc_childcare_cap_increase --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.142.0_policyengine-uk-data-1.59.1/spring_budget_2023/spring_budget_2023__uc_childcare_cap_increase_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
