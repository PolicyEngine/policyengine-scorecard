# Investigation packet: spring_budget_2023 / spring_budget_2023__uc_childcare_cap_increase / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: DWP: increase the maximum support available in Universal Credit for childcare costs
* Flags: numerical, construction
* Base: `pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71`
* Head: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:20829:83521e444ba1a390 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:20835:1e730fccbdf4c015 | -38.3 | -55.1 | -16.8 | numerical | move_above_threshold |
| measure_year | total | -38.3 | -55.1 | -16.8 | numerical, construction | move_above_threshold; premise_check_changed (authored_construction_reproduces) |
| head | universal_credit | -38.3 | -55.1 | -16.8 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:20829:83521e444ba1a390 (row 20829) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSCE in RDEL | 0.0 | — | — |
| base | obr_pmd_nov2025:20835:1e730fccbdf4c015 (row 20835) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare inside cap | -81.6 | -38.3 | -55.1 |
| head | obr_pmd_nov2025:20829:83521e444ba1a390 (row 20829) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSCE in RDEL | 0.0 | — | — |
| head | obr_pmd_nov2025:20835:1e730fccbdf4c015 (row 20835) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare inside cap | -81.6 | -38.3 | -55.1 |

## Executed worlds

* base: `results/uk/replays/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/spring_budget_2023/spring_budget_2023__uc_childcare_cap_increase_2026.json` (sha256 `95979bebf5b049937b4cb42682d024f4d2c6a5badb61a527eb2910ed55aed919`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.elements.childcare.cap.1": {"2023-01-01.2023-12-31": 646.35, "2024-01-01.2024-12-31": 689.6, "2025-01-01.2025-12-31": 701.32, "2026-01-01.2026-12-31": 727.97, "2027-01-01.2027-12-31": 727.97}, "gov.dwp.universal_credit.elements.childcare.cap.2": {"2023-01-01.2023-12-31": 1108.04, "2024-01-01.2024-12-31": 1182.39, "2025-01-01.2025-12-31": 1202.49, "2026-01-01.2026-12-31": 1248.18, "2027-01-01.2027-12-31": 1248.18}}`; reform dict `null`
* head: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/spring_budget_2023/spring_budget_2023__uc_childcare_cap_increase_2026.json` (sha256 `93efcb900e4d19751c1d378e6fcaefa9e817739ab1e326c116f4b1793f711775`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.elements.childcare.cap.1": {"2023-01-01.2023-12-31": 646.35, "2024-01-01.2024-12-31": 689.6, "2025-01-01.2025-12-31": 701.32, "2026-01-01.2026-12-31": 727.97, "2027-01-01.2027-12-31": 727.97}, "gov.dwp.universal_credit.elements.childcare.cap.2": {"2023-01-01.2023-12-31": 1108.04, "2024-01-01.2024-12-31": 1182.39, "2025-01-01.2025-12-31": 1202.49, "2026-01-01.2026-12-31": 1248.18, "2027-01-01.2027-12-31": 1248.18}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2023 --variant pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71 --registry data/uk/events/spring_budget_2023_measures.json --measures spring_budget_2023__uc_childcare_cap_increase --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/spring_budget_2023/spring_budget_2023__uc_childcare_cap_increase_2026
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2023 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/spring_budget_2023_measures.json --measures spring_budget_2023__uc_childcare_cap_increase --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/spring_budget_2023/spring_budget_2023__uc_childcare_cap_increase_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
