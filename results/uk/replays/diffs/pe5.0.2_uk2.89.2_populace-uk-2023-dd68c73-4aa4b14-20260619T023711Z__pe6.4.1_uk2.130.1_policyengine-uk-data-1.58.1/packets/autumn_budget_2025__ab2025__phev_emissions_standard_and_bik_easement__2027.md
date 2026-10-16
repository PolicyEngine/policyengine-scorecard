# Investigation packet: autumn_budget_2025 / ab2025__phev_emissions_standard_and_bik_easement / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Plug-in hybrid electric vehicle (PHEV) emissions regulatory standard changes and Benefit in Kind easement
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12644:3197782abc0a472e | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12650:7c23d5fd346fb2fe | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12656:b65ccac5d29a452b | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12662:174fab9ace11cbcc | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24103:4e490a91649bf309 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24109:96da8654e9415de4 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12644:3197782abc0a472e (row 12644) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | -2.0 | — | — |
| head | obr_pmd_nov2025:12650:7c23d5fd346fb2fe (row 12650) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | NICs | -0.7 | — | — |
| head | obr_pmd_nov2025:12656:b65ccac5d29a452b (row 12656) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Corporation tax (onshore) | 35.6 | — | — |
| head | obr_pmd_nov2025:12662:174fab9ace11cbcc (row 12662) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Vehicle excise duty | 29.2 | — | — |
| head | obr_pmd_nov2025:24103:4e490a91649bf309 (row 24103) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | 0.0 | — | — |
| head | obr_pmd_nov2025:24109:96da8654e9415de4 (row 24109) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | 0.1 | — | — |

## Executed worlds

* base: no artifact
* head: no artifact

## Reproduce

base:

```bash
# This event is absent from this namespace.
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__phev_emissions_standard_and_bik_easement --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__phev_emissions_standard_and_bik_easement_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
