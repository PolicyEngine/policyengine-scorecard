# Investigation packet: autumn_budget_2025 / ab2025__personal_tax_thresholds_freeze_to_2031 / CY2030

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Personal Tax: Maintain the personal income tax and equivalent national insurance thresholds at current levels for a further three years until April 2031
* Flags: numerical
* Base: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`
* Head: `pe6.16.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12233:46d608242afb15f6 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:12239:11eea01fb370a818 | 11,962.9 | 12,268.8 | 306.0 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:12245:bcc4c8e8749434d7 | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:12251:1a002f19d93f58bc | — | — | — | — | — |
| source_row | obr_pmd_nov2025:23914:82af6138df257d06 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:23920:07fdfe7c4df486ae | -174.4 | -173.1 | 1.3 | — | — |
| source_row | obr_pmd_nov2025:23926:7658be5fd7ff4733 | — | — | — | — | — |
| measure_year | total | 11,788.5 | 12,095.7 | 307.2 | numerical | move_above_threshold |
| head | income_tax | 11,962.9 | 12,268.8 | 306.0 | numerical | move_above_threshold |
| head | ni_class_1_employee | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | 0.0 | 0.0 | 0.0 | — | — |
| head | universal_credit | -174.4 | -173.1 | 1.3 | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:12233:46d608242afb15f6 (row 12233) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Capital gains tax | 23.7 | — | — |
| base | obr_pmd_nov2025:12239:11eea01fb370a818 (row 12239) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Income tax | 11,532.0 | 11,962.9 | 12,268.8 |
| base | obr_pmd_nov2025:12245:bcc4c8e8749434d7 (row 12245) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | NICs | 533.1 | 0.0 | 0.0 |
| base | obr_pmd_nov2025:12251:1a002f19d93f58bc (row 12251) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Corporation tax (onshore) | -297.8 | — | — |
| base | obr_pmd_nov2025:23914:82af6138df257d06 (row 23914) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | PSCE in RDEL | 68.2 | — | — |
| base | obr_pmd_nov2025:23920:07fdfe7c4df486ae (row 23920) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Welfare inside cap | -235.7 | -174.4 | -173.1 |
| base | obr_pmd_nov2025:23926:7658be5fd7ff4733 (row 23926) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Scottish BGA (current) | 811.8 | — | — |
| head | obr_pmd_nov2025:12233:46d608242afb15f6 (row 12233) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Capital gains tax | 23.7 | — | — |
| head | obr_pmd_nov2025:12239:11eea01fb370a818 (row 12239) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Income tax | 11,532.0 | 11,962.9 | 12,268.8 |
| head | obr_pmd_nov2025:12245:bcc4c8e8749434d7 (row 12245) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | NICs | 533.1 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:12251:1a002f19d93f58bc (row 12251) | Tax Measures (Policy measures database) / 2030-31 | 2030-31 | Corporation tax (onshore) | -297.8 | — | — |
| head | obr_pmd_nov2025:23914:82af6138df257d06 (row 23914) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | PSCE in RDEL | 68.2 | — | — |
| head | obr_pmd_nov2025:23920:07fdfe7c4df486ae (row 23920) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Welfare inside cap | -235.7 | -174.4 | -173.1 |
| head | obr_pmd_nov2025:23926:7658be5fd7ff4733 (row 23926) | Spending Measures (Policy measures database) / 2030-31 | 2030-31 | Scottish BGA (current) | 811.8 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2025/ab2025__personal_tax_thresholds_freeze_to_2031_2030.json` (sha256 `5f30a6f24494e5bcbc871dcbda9c3ef65f0569876d4ff3f961ac44eb281e0868`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.allowances.personal_allowance.amount": {"2028-01-01.2028-12-31": 12821.388032703, "2029-01-01.2029-12-31": 13077.7873710267, "2030-01-01.2030-12-31": 13339.3476061836}, "gov.hmrc.income_tax.rates.dividends[1].threshold": {"2028-01-01.2028-12-31": 38453.940508488, "2029-01-01.2029-12-31": 39222.9827084964, "2030-01-01.2030-12-31": 40007.3554135334}, "gov.hmrc.income_tax.rates.uk[1].threshold": {"2028-01-01.2028-12-31": 38453.940508488, "2029-01-01.2029-12-31": 39222.9827084964, "2030-01-01.2030-12-31": 40007.3554135334}}`; reform dict `null`
* head: `results/uk/replays/pe6.16.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_budget_2025/ab2025__personal_tax_thresholds_freeze_to_2031_2030.json` (sha256 `33a85d8871ba2e6c206cb23eb5c7280a7b27a4082c86ac7ada9a8c0b13566ee9`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.allowances.personal_allowance.amount": {"2028-01-01.2028-12-31": 12821.388032703, "2029-01-01.2029-12-31": 13077.7873710267, "2030-01-01.2030-12-31": 13339.3476061836}, "gov.hmrc.income_tax.rates.dividends[1].threshold": {"2028-01-01.2028-12-31": 38453.940508488, "2029-01-01.2029-12-31": 39222.9827084964, "2030-01-01.2030-12-31": 40007.3554135334}, "gov.hmrc.income_tax.rates.uk[1].threshold": {"2028-01-01.2028-12-31": 38453.940508488, "2029-01-01.2029-12-31": 39222.9827084964, "2030-01-01.2030-12-31": 40007.3554135334}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__personal_tax_thresholds_freeze_to_2031 --years 2030 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2025/ab2025__personal_tax_thresholds_freeze_to_2031_2030
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.16.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__personal_tax_thresholds_freeze_to_2031 --years 2030 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.16.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_budget_2025/ab2025__personal_tax_thresholds_freeze_to_2031_2030
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
