# Investigation packet: spring_budget_2023 / spring_budget_2023__uc_childcare_cap_increase / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: DWP: increase the maximum support available in Universal Credit for childcare costs
* Flags: numerical
* Base: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`
* Head: `pe6.18.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:20829:83521e444ba1a390 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:20835:1e730fccbdf4c015 | -55.1 | -76.5 | -21.4 | numerical | move_above_threshold |
| measure_year | total | -55.1 | -76.5 | -21.4 | numerical | move_above_threshold |
| head | universal_credit | -55.1 | -76.5 | -21.4 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:20829:83521e444ba1a390 (row 20829) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSCE in RDEL | 0.0 | — | — |
| base | obr_pmd_nov2025:20835:1e730fccbdf4c015 (row 20835) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare inside cap | -81.6 | -55.1 | -76.5 |
| head | obr_pmd_nov2025:20829:83521e444ba1a390 (row 20829) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSCE in RDEL | 0.0 | — | — |
| head | obr_pmd_nov2025:20835:1e730fccbdf4c015 (row 20835) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Welfare inside cap | -81.6 | -55.1 | -76.5 |

## Executed worlds

* base: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/spring_budget_2023/spring_budget_2023__uc_childcare_cap_increase_2026.json` (sha256 `339a7bf81034374831d34573213d27eb27049c410017cbfa43519610315641dd`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.elements.childcare.cap.1": {"2023-01-01.2023-12-31": 646.35, "2024-01-01.2024-12-31": 689.6, "2025-01-01.2025-12-31": 701.32, "2026-01-01.2026-12-31": 727.97, "2027-01-01.2027-12-31": 727.97}, "gov.dwp.universal_credit.elements.childcare.cap.2": {"2023-01-01.2023-12-31": 1108.04, "2024-01-01.2024-12-31": 1182.39, "2025-01-01.2025-12-31": 1202.49, "2026-01-01.2026-12-31": 1248.18, "2027-01-01.2027-12-31": 1248.18}}`; reform dict `null`
* head: `results/uk/replays/pe6.18.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/spring_budget_2023/spring_budget_2023__uc_childcare_cap_increase_2026.json` (sha256 `48c98bba9d97783b1cf3b5ac2e52f796ec97bc3d9eaeb3d890ecc7a25ca0f8fa`), reversal_on_certified_world; baseline dict `{"gov.dwp.universal_credit.elements.childcare.cap.1": {"2023-01-01.2023-12-31": 646.35, "2024-01-01.2024-12-31": 689.6, "2025-01-01.2025-12-31": 701.32, "2026-01-01.2026-12-31": 727.97, "2027-01-01.2027-12-31": 727.97}, "gov.dwp.universal_credit.elements.childcare.cap.2": {"2023-01-01.2023-12-31": 1108.04, "2024-01-01.2024-12-31": 1182.39, "2025-01-01.2025-12-31": 1202.49, "2026-01-01.2026-12-31": 1248.18, "2027-01-01.2027-12-31": 1248.18}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2023 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/spring_budget_2023_measures.json --measures spring_budget_2023__uc_childcare_cap_increase --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/spring_budget_2023/spring_budget_2023__uc_childcare_cap_increase_2026
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event spring_budget_2023 --variant pe6.18.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e --registry data/uk/events/spring_budget_2023_measures.json --measures spring_budget_2023__uc_childcare_cap_increase --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.18.0_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/spring_budget_2023/spring_budget_2023__uc_childcare_cap_increase_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
