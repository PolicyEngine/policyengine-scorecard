# Investigation packet: spring_budget_2023 / spring_budget_2023__uc_childcare_cap_increase / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: DWP: increase the maximum support available in Universal Credit for childcare costs
* Flags: numerical
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:20830:0a15663b3de35bc8 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:20836:76beca3818ed1fe1 | -2.1 | -241.9 | -239.8 | numerical | move_above_threshold |
| measure_year | total | -2.1 | -241.9 | -239.8 | numerical | move_above_threshold |
| head | universal_credit | -2.1 | -241.9 | -239.8 | numerical | move_above_threshold |

## OBR source cells

| Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---:|---:|---:|
| obr_pmd_nov2025:20830:0a15663b3de35bc8 (row 20830) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | 0.0 | — | — |
| obr_pmd_nov2025:20836:76beca3818ed1fe1 (row 20836) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | -86.8 | -2.1 | -241.9 |

## Executed worlds

* base: `results/uk/events/spring_budget_2023/spring_budget_2023__uc_childcare_cap_increase_2027.json` (sha256 `e0384d3ab333f6497892de425f25858a4e0ac4652f2f650e5d94da9b1894deed`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.elements.childcare.cap.1": {"2023-01-01.2023-12-31": 646.35, "2024-01-01.2024-12-31": 689.6, "2025-01-01.2025-12-31": 701.32, "2026-01-01.2026-12-31": 727.97, "2027-01-01.2027-12-31": 727.97}, "gov.dwp.universal_credit.elements.childcare.cap.2": {"2023-01-01.2023-12-31": 1108.04, "2024-01-01.2024-12-31": 1182.39, "2025-01-01.2025-12-31": 1202.49, "2026-01-01.2026-12-31": 1248.18, "2027-01-01.2027-12-31": 1248.18}}`; reform dict `null`
* head: `results/uk/replays/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/spring_budget_2023/spring_budget_2023__uc_childcare_cap_increase_2027.json` (sha256 `007c6dc265fec938b0d0b543890d6a2c9eb1a512cffdee4db5dcb6b1d1deb09c`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.elements.childcare.cap.1": {"2023-01-01.2023-12-31": 646.35, "2024-01-01.2024-12-31": 689.6, "2025-01-01.2025-12-31": 701.32, "2026-01-01.2026-12-31": 727.97, "2027-01-01.2027-12-31": 727.97}, "gov.dwp.universal_credit.elements.childcare.cap.2": {"2023-01-01.2023-12-31": 1108.04, "2024-01-01.2024-12-31": 1182.39, "2025-01-01.2025-12-31": 1202.49, "2026-01-01.2026-12-31": 1248.18, "2027-01-01.2027-12-31": 1248.18}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2023 --variant pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z --measures spring_budget_2023__uc_childcare_cap_increase --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/spring_budget_2023/spring_budget_2023__uc_childcare_cap_increase_2027
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2023 --variant pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0 --measures spring_budget_2023__uc_childcare_cap_increase --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/spring_budget_2023/spring_budget_2023__uc_childcare_cap_increase_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
