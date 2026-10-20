# Investigation packet: autumn_budget_2025 / ab2025__personal_tax_thresholds_freeze_to_2031 / CY2029

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Personal Tax: Maintain the personal income tax and equivalent national insurance thresholds at current levels for a further three years until April 2031
* Flags: numerical
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.8.0_uk2.139.2_policyengine-uk-data-1.58.2`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12232:6192e83494d8ae4f | — | — | — | — | — |
| source_row | obr_pmd_nov2025:12238:ed7d488b306dcf83 | 8,079.0 | 8,005.2 | -73.8 | — | — |
| source_row | obr_pmd_nov2025:12244:5ebeab8e54fb9380 | 0.0 | 0.0 | 0.0 | — | — |
| source_row | obr_pmd_nov2025:12250:a20cefba9a79d467 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:23913:3660478e58dc0c33 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:23919:d57980273e85240e | -150.4 | -152.5 | -2.1 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:23925:d67929eb924e3879 | — | — | — | — | — |
| measure_year | total | 7,928.6 | 7,852.6 | -75.9 | — | — |
| head | income_tax | 8,079.0 | 8,005.2 | -73.8 | — | — |
| head | ni_class_1_employee | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_1_employer | 0.0 | 0.0 | 0.0 | — | — |
| head | ni_class_4 | 0.0 | 0.0 | 0.0 | — | — |
| head | universal_credit | -150.4 | -152.5 | -2.1 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:12232:6192e83494d8ae4f (row 12232) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Capital gains tax | 14.6 | — | — |
| base | obr_pmd_nov2025:12238:ed7d488b306dcf83 (row 12238) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Income tax | 7,427.3 | 8,079.0 | 8,005.2 |
| base | obr_pmd_nov2025:12244:5ebeab8e54fb9380 (row 12244) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | NICs | 329.1 | 0.0 | 0.0 |
| base | obr_pmd_nov2025:12250:a20cefba9a79d467 (row 12250) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Corporation tax (onshore) | -406.0 | — | — |
| base | obr_pmd_nov2025:23913:3660478e58dc0c33 (row 23913) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | PSCE in RDEL | 44.0 | — | — |
| base | obr_pmd_nov2025:23919:d57980273e85240e (row 23919) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Welfare inside cap | -157.1 | -150.4 | -152.5 |
| base | obr_pmd_nov2025:23925:d67929eb924e3879 (row 23925) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Scottish BGA (current) | 529.9 | — | — |
| head | obr_pmd_nov2025:12232:6192e83494d8ae4f (row 12232) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Capital gains tax | 14.6 | — | — |
| head | obr_pmd_nov2025:12238:ed7d488b306dcf83 (row 12238) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Income tax | 7,427.3 | 8,079.0 | 8,005.2 |
| head | obr_pmd_nov2025:12244:5ebeab8e54fb9380 (row 12244) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | NICs | 329.1 | 0.0 | 0.0 |
| head | obr_pmd_nov2025:12250:a20cefba9a79d467 (row 12250) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Corporation tax (onshore) | -406.0 | — | — |
| head | obr_pmd_nov2025:23913:3660478e58dc0c33 (row 23913) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | PSCE in RDEL | 44.0 | — | — |
| head | obr_pmd_nov2025:23919:d57980273e85240e (row 23919) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Welfare inside cap | -157.1 | -150.4 | -152.5 |
| head | obr_pmd_nov2025:23925:d67929eb924e3879 (row 23925) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Scottish BGA (current) | 529.9 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__personal_tax_thresholds_freeze_to_2031_2029.json` (sha256 `543023fa8c109445d152cb1bdca991ef58997cd4701b07662dbbb2d2fcd0df0e`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.allowances.personal_allowance.amount": {"2028-01-01.2028-12-31": 12821.388032703, "2029-01-01.2029-12-31": 13077.7873710267, "2030-01-01.2030-12-31": 13339.3476061836}, "gov.hmrc.income_tax.rates.dividends[1].threshold": {"2028-01-01.2028-12-31": 38453.940508488, "2029-01-01.2029-12-31": 39222.9827084964, "2030-01-01.2030-12-31": 40007.3554135334}, "gov.hmrc.income_tax.rates.uk[1].threshold": {"2028-01-01.2028-12-31": 38453.940508488, "2029-01-01.2029-12-31": 39222.9827084964, "2030-01-01.2030-12-31": 40007.3554135334}}`; reform dict `null`
* head: `results/uk/replays/pe6.8.0_uk2.139.2_policyengine-uk-data-1.58.2/autumn_budget_2025/ab2025__personal_tax_thresholds_freeze_to_2031_2029.json` (sha256 `3508ab28f3855f10a88ef8e188a71a6e73c453d6cf09aa27939011c808e32588`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.allowances.personal_allowance.amount": {"2028-01-01.2028-12-31": 12821.388032703, "2029-01-01.2029-12-31": 13077.7873710267, "2030-01-01.2030-12-31": 13339.3476061836}, "gov.hmrc.income_tax.rates.dividends[1].threshold": {"2028-01-01.2028-12-31": 38453.940508488, "2029-01-01.2029-12-31": 39222.9827084964, "2030-01-01.2030-12-31": 40007.3554135334}, "gov.hmrc.income_tax.rates.uk[1].threshold": {"2028-01-01.2028-12-31": 38453.940508488, "2029-01-01.2029-12-31": 39222.9827084964, "2030-01-01.2030-12-31": 40007.3554135334}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__personal_tax_thresholds_freeze_to_2031 --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__personal_tax_thresholds_freeze_to_2031_2029
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.8.0_uk2.139.2_policyengine-uk-data-1.58.2 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__personal_tax_thresholds_freeze_to_2031 --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.8.0_uk2.139.2_policyengine-uk-data-1.58.2/autumn_budget_2025/ab2025__personal_tax_thresholds_freeze_to_2031_2029
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
