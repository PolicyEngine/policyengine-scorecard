# Investigation packet: autumn_budget_2025 / ab2025__personal_tax_thresholds_freeze_to_2031 / CY2028

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Personal Tax: Maintain the personal income tax and equivalent national insurance thresholds at current levels for a further three years until April 2031
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12231:4ba2e06431d2eb73 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12237:0c8c820d59cc8062 | — | 3,859.5 | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12243:489d985f59a57f6e | — | 0.0 | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12249:06e004e47cbe1979 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23912:f3f16f2fd20c9cbf | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23918:cb97d1297e767678 | — | -75.4 | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23924:e306b642355353f8 | — | — | — | coverage | event_on_head_only |
| measure_year | total | — | 3,784.1 | — | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12231:4ba2e06431d2eb73 (row 12231) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Capital gains tax | 6.3 | — | — |
| head | obr_pmd_nov2025:12237:0c8c820d59cc8062 (row 12237) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Income tax | 3,220.1 | — | 3,859.5 |
| head | obr_pmd_nov2025:12243:489d985f59a57f6e (row 12243) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | NICs | 156.4 | — | 0.0 |
| head | obr_pmd_nov2025:12249:06e004e47cbe1979 (row 12249) | Tax Measures (Policy measures database) / 2028-29 | 2028-29 | Corporation tax (onshore) | -203.2 | — | — |
| head | obr_pmd_nov2025:23912:f3f16f2fd20c9cbf (row 23912) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | PSCE in RDEL | 21.0 | — | — |
| head | obr_pmd_nov2025:23918:cb97d1297e767678 (row 23918) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Welfare inside cap | -77.5 | — | -75.4 |
| head | obr_pmd_nov2025:23924:e306b642355353f8 (row 23924) | Spending Measures (Policy measures database) / 2028-29 | 2028-29 | Scottish BGA (current) | 241.2 | — | — |

## Executed worlds

* base: no artifact
* head: `results/uk/replays/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__personal_tax_thresholds_freeze_to_2031_2028.json` (sha256 `1ed059c069b9dafc8703483b203eba38de09adbee6a46b1ae5b7ac28c275d3df`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.allowances.personal_allowance.amount": {"2028-01-01.2028-12-31": 12821.388032703, "2029-01-01.2029-12-31": 13077.7873710267, "2030-01-01.2030-12-31": 13339.3476061836}, "gov.hmrc.income_tax.rates.dividends[1].threshold": {"2028-01-01.2028-12-31": 38453.940508488, "2029-01-01.2029-12-31": 39222.9827084964, "2030-01-01.2030-12-31": 40007.3554135334}, "gov.hmrc.income_tax.rates.uk[1].threshold": {"2028-01-01.2028-12-31": 38453.940508488, "2029-01-01.2029-12-31": 39222.9827084964, "2030-01-01.2030-12-31": 40007.3554135334}}`; reform dict `null`

## Reproduce

base:

```bash
# This event is absent from this namespace.
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__personal_tax_thresholds_freeze_to_2031 --years 2028 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__personal_tax_thresholds_freeze_to_2031_2028
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
