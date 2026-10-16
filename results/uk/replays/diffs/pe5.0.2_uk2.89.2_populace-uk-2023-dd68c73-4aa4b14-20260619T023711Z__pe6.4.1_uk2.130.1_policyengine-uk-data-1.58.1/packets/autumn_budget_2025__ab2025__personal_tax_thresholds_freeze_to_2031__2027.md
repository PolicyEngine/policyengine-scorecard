# Investigation packet: autumn_budget_2025 / ab2025__personal_tax_thresholds_freeze_to_2031 / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Personal Tax: Maintain the personal income tax and equivalent national insurance thresholds at current levels for a further three years until April 2031
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12230:70e3551d03ce85cf | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12236:a4aebc6995d1f171 | — | 0.0 | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12242:8821990307cd4ca7 | — | 0.0 | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12248:4e867af4cf8e98ea | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23911:38c95e0dae337e30 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23917:f813a593e6390ba1 | — | 0.0 | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23923:32225f68f6d6e9b1 | — | — | — | coverage | event_on_head_only |
| measure_year | total | — | 0.0 | — | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12230:70e3551d03ce85cf (row 12230) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Capital gains tax | 0.0 | — | — |
| head | obr_pmd_nov2025:12236:a4aebc6995d1f171 (row 12236) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | 0.0 | — | 0.0 |
| head | obr_pmd_nov2025:12242:8821990307cd4ca7 (row 12242) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | NICs | 0.0 | — | 0.0 |
| head | obr_pmd_nov2025:12248:4e867af4cf8e98ea (row 12248) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Corporation tax (onshore) | -24.4 | — | — |
| head | obr_pmd_nov2025:23911:38c95e0dae337e30 (row 23911) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | 0.0 | — | — |
| head | obr_pmd_nov2025:23917:f813a593e6390ba1 (row 23917) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Welfare inside cap | 0.0 | — | 0.0 |
| head | obr_pmd_nov2025:23923:32225f68f6d6e9b1 (row 23923) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | 0.0 | — | — |

## Executed worlds

* base: no artifact
* head: `results/uk/replays/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__personal_tax_thresholds_freeze_to_2031_2027.json` (sha256 `53959b623aba1367232aa5fdda33668d491a55fe3adc2f9110752fed56fdf3fe`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.allowances.personal_allowance.amount": {"2028-01-01.2028-12-31": 12821.388032703, "2029-01-01.2029-12-31": 13077.7873710267, "2030-01-01.2030-12-31": 13339.3476061836}, "gov.hmrc.income_tax.rates.dividends[1].threshold": {"2028-01-01.2028-12-31": 38453.940508488, "2029-01-01.2029-12-31": 39222.9827084964, "2030-01-01.2030-12-31": 40007.3554135334}, "gov.hmrc.income_tax.rates.uk[1].threshold": {"2028-01-01.2028-12-31": 38453.940508488, "2029-01-01.2029-12-31": 39222.9827084964, "2030-01-01.2030-12-31": 40007.3554135334}}`; reform dict `null`

## Reproduce

base:

```bash
# This event is absent from this namespace.
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__personal_tax_thresholds_freeze_to_2031 --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__personal_tax_thresholds_freeze_to_2031_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
