# Investigation packet: autumn_budget_2025 / ab2025__personal_tax_thresholds_freeze_to_2031 / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Personal Tax: Maintain the personal income tax and equivalent national insurance thresholds at current levels for a further three years until April 2031
* Flags: numerical
* Base: `pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12231:4ba2e06431d2eb73 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:12237:0c8c820d59cc8062 | 3,859.5 | 3,814.2 | -45.4 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:12243:489d985f59a57f6e | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:12249:06e004e47cbe1979 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:23912:f3f16f2fd20c9cbf | — | — | — | — | — |
| source_row | obr_pmd_nov2025:23918:cb97d1297e767678 | -75.4 | -57.0 | 18.5 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:23924:e306b642355353f8 | — | — | — | — | — |
| measure_year | total | 3,784.1 | 3,757.2 | -26.9 | — | — |
| head | income_tax | 3,859.5 | 3,814.2 | -45.4 | numerical | move_above_threshold |
| head | ni_class_1_employee | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | 0.0 | 0.0 | 0.0 | — | — |
| head | universal_credit | -75.4 | -57.0 | 18.5 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:12231:4ba2e06431d2eb73 (row 12231) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Capital gains tax | 6.3 | — | — |
| base | obr_pmd_nov2025:12237:0c8c820d59cc8062 (row 12237) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | 3,220.1 | 3,859.5 | 3,814.2 |
| base | obr_pmd_nov2025:12243:489d985f59a57f6e (row 12243) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | NICs | 156.4 | 0.0 | 0.0 |
| base | obr_pmd_nov2025:12249:06e004e47cbe1979 (row 12249) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Corporation tax (onshore) | -203.2 | — | — |
| base | obr_pmd_nov2025:23912:f3f16f2fd20c9cbf (row 23912) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | 21.0 | — | — |
| base | obr_pmd_nov2025:23918:cb97d1297e767678 (row 23918) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | -77.5 | -75.4 | -57.0 |
| base | obr_pmd_nov2025:23924:e306b642355353f8 (row 23924) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | 241.2 | — | — |
| head | obr_pmd_nov2025:12231:4ba2e06431d2eb73 (row 12231) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Capital gains tax | 6.3 | — | — |
| head | obr_pmd_nov2025:12237:0c8c820d59cc8062 (row 12237) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | 3,220.1 | 3,859.5 | 3,814.2 |
| head | obr_pmd_nov2025:12243:489d985f59a57f6e (row 12243) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | NICs | 156.4 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:12249:06e004e47cbe1979 (row 12249) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Corporation tax (onshore) | -203.2 | — | — |
| head | obr_pmd_nov2025:23912:f3f16f2fd20c9cbf (row 23912) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | 21.0 | — | — |
| head | obr_pmd_nov2025:23918:cb97d1297e767678 (row 23918) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | -77.5 | -75.4 | -57.0 |
| head | obr_pmd_nov2025:23924:e306b642355353f8 (row 23924) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | 241.2 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__personal_tax_thresholds_freeze_to_2031_2028.json` (sha256 `86b2be1063b56f11c561c21d4d0f2e3eceeb5cb8b23097dc3557e01e25d4e077`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.allowances.personal_allowance.amount": {"2028-01-01.2028-12-31": 12821.388032703, "2029-01-01.2029-12-31": 13077.7873710267, "2030-01-01.2030-12-31": 13339.3476061836}, "gov.hmrc.income_tax.rates.dividends[1].threshold": {"2028-01-01.2028-12-31": 38453.940508488, "2029-01-01.2029-12-31": 39222.9827084964, "2030-01-01.2030-12-31": 40007.3554135334}, "gov.hmrc.income_tax.rates.uk[1].threshold": {"2028-01-01.2028-12-31": 38453.940508488, "2029-01-01.2029-12-31": 39222.9827084964, "2030-01-01.2030-12-31": 40007.3554135334}}`; reform dict `null`
* head: `results/uk/replays/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_budget_2025/ab2025__personal_tax_thresholds_freeze_to_2031_2028.json` (sha256 `39766a2a02f03ab743f28cb74a3c6c3ecd8df4c0729121fe824075517cc3391b`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.allowances.personal_allowance.amount": {"2028-01-01.2028-12-31": 12821.388032703, "2029-01-01.2029-12-31": 13077.7873710267, "2030-01-01.2030-12-31": 13339.3476061836}, "gov.hmrc.income_tax.rates.dividends[1].threshold": {"2028-01-01.2028-12-31": 38453.940508488, "2029-01-01.2029-12-31": 39222.9827084964, "2030-01-01.2030-12-31": 40007.3554135334}, "gov.hmrc.income_tax.rates.uk[1].threshold": {"2028-01-01.2028-12-31": 38453.940508488, "2029-01-01.2029-12-31": 39222.9827084964, "2030-01-01.2030-12-31": 40007.3554135334}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__personal_tax_thresholds_freeze_to_2031 --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__personal_tax_thresholds_freeze_to_2031_2028
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__personal_tax_thresholds_freeze_to_2031 --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_budget_2025/ab2025__personal_tax_thresholds_freeze_to_2031_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
