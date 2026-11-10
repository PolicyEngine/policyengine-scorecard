# Investigation packet: autumn_budget_2025 / ab2025__personal_tax_thresholds_freeze_to_2031 / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Personal Tax: Maintain the personal income tax and equivalent national insurance thresholds at current levels for a further three years until April 2031
* Flags: numerical
* Base: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`
* Head: `pe6.17.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12231:4ba2e06431d2eb73 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:12237:0c8c820d59cc8062 | 3,735.9 | 3,838.2 | 102.3 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:12243:489d985f59a57f6e | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:12249:06e004e47cbe1979 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:23912:f3f16f2fd20c9cbf | — | — | — | — | — |
| source_row | obr_pmd_nov2025:23918:cb97d1297e767678 | -58.7 | -57.0 | 1.7 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:23924:e306b642355353f8 | — | — | — | — | — |
| measure_year | total | 3,677.2 | 3,781.2 | 104.0 | numerical | move_above_threshold |
| head | income_tax | 3,735.9 | 3,838.2 | 102.3 | numerical | move_above_threshold |
| head | ni_class_1_employee | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | 0.0 | 0.0 | 0.0 | — | — |
| head | universal_credit | -58.7 | -57.0 | 1.7 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:12231:4ba2e06431d2eb73 (row 12231) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Capital gains tax | 6.3 | — | — |
| base | obr_pmd_nov2025:12237:0c8c820d59cc8062 (row 12237) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | 3,220.1 | 3,735.9 | 3,838.2 |
| base | obr_pmd_nov2025:12243:489d985f59a57f6e (row 12243) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | NICs | 156.4 | 0.0 | 0.0 |
| base | obr_pmd_nov2025:12249:06e004e47cbe1979 (row 12249) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Corporation tax (onshore) | -203.2 | — | — |
| base | obr_pmd_nov2025:23912:f3f16f2fd20c9cbf (row 23912) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | 21.0 | — | — |
| base | obr_pmd_nov2025:23918:cb97d1297e767678 (row 23918) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | -77.5 | -58.7 | -57.0 |
| base | obr_pmd_nov2025:23924:e306b642355353f8 (row 23924) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | 241.2 | — | — |
| head | obr_pmd_nov2025:12231:4ba2e06431d2eb73 (row 12231) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Capital gains tax | 6.3 | — | — |
| head | obr_pmd_nov2025:12237:0c8c820d59cc8062 (row 12237) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | 3,220.1 | 3,735.9 | 3,838.2 |
| head | obr_pmd_nov2025:12243:489d985f59a57f6e (row 12243) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | NICs | 156.4 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:12249:06e004e47cbe1979 (row 12249) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Corporation tax (onshore) | -203.2 | — | — |
| head | obr_pmd_nov2025:23912:f3f16f2fd20c9cbf (row 23912) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | 21.0 | — | — |
| head | obr_pmd_nov2025:23918:cb97d1297e767678 (row 23918) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | -77.5 | -58.7 | -57.0 |
| head | obr_pmd_nov2025:23924:e306b642355353f8 (row 23924) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | 241.2 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2025/ab2025__personal_tax_thresholds_freeze_to_2031_2028.json` (sha256 `ff9b2742949ef1d829ce69785c9ca7ca57c449fedeab8e485353178f369069e8`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.allowances.personal_allowance.amount": {"2028-01-01.2028-12-31": 12821.388032703, "2029-01-01.2029-12-31": 13077.7873710267, "2030-01-01.2030-12-31": 13339.3476061836}, "gov.hmrc.income_tax.rates.dividends[1].threshold": {"2028-01-01.2028-12-31": 38453.940508488, "2029-01-01.2029-12-31": 39222.9827084964, "2030-01-01.2030-12-31": 40007.3554135334}, "gov.hmrc.income_tax.rates.uk[1].threshold": {"2028-01-01.2028-12-31": 38453.940508488, "2029-01-01.2029-12-31": 39222.9827084964, "2030-01-01.2030-12-31": 40007.3554135334}}`; reform dict `null`
* head: `results/uk/replays/pe6.17.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_budget_2025/ab2025__personal_tax_thresholds_freeze_to_2031_2028.json` (sha256 `b27cda71ac19d2837e70efeb245ccdfa26716c913f39f440bbaaa0e105963b01`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.allowances.personal_allowance.amount": {"2028-01-01.2028-12-31": 12821.388032703, "2029-01-01.2029-12-31": 13077.7873710267, "2030-01-01.2030-12-31": 13339.3476061836}, "gov.hmrc.income_tax.rates.dividends[1].threshold": {"2028-01-01.2028-12-31": 38453.940508488, "2029-01-01.2029-12-31": 39222.9827084964, "2030-01-01.2030-12-31": 40007.3554135334}, "gov.hmrc.income_tax.rates.uk[1].threshold": {"2028-01-01.2028-12-31": 38453.940508488, "2029-01-01.2029-12-31": 39222.9827084964, "2030-01-01.2030-12-31": 40007.3554135334}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__personal_tax_thresholds_freeze_to_2031 --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2025/ab2025__personal_tax_thresholds_freeze_to_2031_2028
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.17.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__personal_tax_thresholds_freeze_to_2031 --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.17.1_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_budget_2025/ab2025__personal_tax_thresholds_freeze_to_2031_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
