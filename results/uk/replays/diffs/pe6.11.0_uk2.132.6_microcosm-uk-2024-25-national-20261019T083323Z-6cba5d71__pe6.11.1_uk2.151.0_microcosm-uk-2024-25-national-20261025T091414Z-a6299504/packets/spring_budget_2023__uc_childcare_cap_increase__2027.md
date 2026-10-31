# Investigation packet: spring_budget_2023 / spring_budget_2023__uc_childcare_cap_increase / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: DWP: increase the maximum support available in Universal Credit for childcare costs
* Flags: numerical, construction
* Base: `pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71`
* Head: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:20830:0a15663b3de35bc8 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:20836:76beca3818ed1fe1 | -40.3 | -61.7 | -21.4 | numerical | move_above_threshold |
| measure_year | total | -40.3 | -61.7 | -21.4 | numerical, construction | move_above_threshold; premise_check_changed (authored_construction_reproduces) |
| head | universal_credit | -40.3 | -61.7 | -21.4 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:20830:0a15663b3de35bc8 (row 20830) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | 0.0 | — | — |
| base | obr_pmd_nov2025:20836:76beca3818ed1fe1 (row 20836) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | -86.8 | -40.3 | -61.7 |
| head | obr_pmd_nov2025:20830:0a15663b3de35bc8 (row 20830) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | 0.0 | — | — |
| head | obr_pmd_nov2025:20836:76beca3818ed1fe1 (row 20836) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | -86.8 | -40.3 | -61.7 |

## Executed worlds

* base: `results/uk/replays/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/spring_budget_2023/spring_budget_2023__uc_childcare_cap_increase_2027.json` (sha256 `8e9ca98c5ee7af5db896ec92e12709f1fa199b5d71c449ca36232572e9001a02`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.elements.childcare.cap.1": {"2023-01-01.2023-12-31": 646.35, "2024-01-01.2024-12-31": 689.6, "2025-01-01.2025-12-31": 701.32, "2026-01-01.2026-12-31": 727.97, "2027-01-01.2027-12-31": 727.97}, "gov.dwp.universal_credit.elements.childcare.cap.2": {"2023-01-01.2023-12-31": 1108.04, "2024-01-01.2024-12-31": 1182.39, "2025-01-01.2025-12-31": 1202.49, "2026-01-01.2026-12-31": 1248.18, "2027-01-01.2027-12-31": 1248.18}}`; reform dict `null`
* head: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/spring_budget_2023/spring_budget_2023__uc_childcare_cap_increase_2027.json` (sha256 `3ecbad9c9f96f84f5247d03ad463b74c18abd85062f706915a28dd223422ebc9`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.elements.childcare.cap.1": {"2023-01-01.2023-12-31": 646.35, "2024-01-01.2024-12-31": 689.6, "2025-01-01.2025-12-31": 701.32, "2026-01-01.2026-12-31": 727.97, "2027-01-01.2027-12-31": 727.97}, "gov.dwp.universal_credit.elements.childcare.cap.2": {"2023-01-01.2023-12-31": 1108.04, "2024-01-01.2024-12-31": 1182.39, "2025-01-01.2025-12-31": 1202.49, "2026-01-01.2026-12-31": 1248.18, "2027-01-01.2027-12-31": 1248.18}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2023 --variant pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71 --registry data/uk/events/spring_budget_2023_measures.json --measures spring_budget_2023__uc_childcare_cap_increase --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/spring_budget_2023/spring_budget_2023__uc_childcare_cap_increase_2027
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2023 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/spring_budget_2023_measures.json --measures spring_budget_2023__uc_childcare_cap_increase --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/spring_budget_2023/spring_budget_2023__uc_childcare_cap_increase_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
