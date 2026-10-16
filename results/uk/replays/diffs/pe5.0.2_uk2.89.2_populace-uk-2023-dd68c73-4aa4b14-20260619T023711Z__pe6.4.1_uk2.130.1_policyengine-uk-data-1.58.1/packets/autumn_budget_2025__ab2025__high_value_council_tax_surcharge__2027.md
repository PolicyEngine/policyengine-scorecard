# Investigation packet: autumn_budget_2025 / ab2025__high_value_council_tax_surcharge / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: High Value Council Tax Surcharge: Introduce a surcharge on owners of residential properties valued over £2m in England from 1 April 2028
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12368:c7e702797da2671f | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12374:54d5dda3f0350cd9 | — | 0.0 | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12380:e3ebdd53fd67d884 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12386:e147c775aba66446 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23989:7bff20ee7164468f | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23995:dd9d1b9a31aa35c2 | — | — | — | coverage | event_on_head_only |
| measure_year | total | — | 0.0 | — | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12368:c7e702797da2671f (row 12368) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Capital gains tax | -51.4 | — | — |
| head | obr_pmd_nov2025:12374:54d5dda3f0350cd9 (row 12374) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | High-value council tax surcharge | 0.0 | — | 0.0 |
| head | obr_pmd_nov2025:12380:e3ebdd53fd67d884 (row 12380) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Inheritance tax | -8.1 | — | — |
| head | obr_pmd_nov2025:12386:e147c775aba66446 (row 12386) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Stamp duty | -89.8 | — | — |
| head | obr_pmd_nov2025:23989:7bff20ee7164468f (row 23989) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | -1.8 | — | — |
| head | obr_pmd_nov2025:23995:dd9d1b9a31aa35c2 (row 23995) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | -4.2 | — | — |

## Executed worlds

* base: no artifact
* head: `results/uk/replays/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__high_value_council_tax_surcharge_2027.json` (sha256 `9bf5943c2a91d1292eb5b5bbb3dad541e3b1691e233caa58b48170a645bf0427`), reversal_on_certified_world; baseline dict `{"gov.hmrc.council_tax.high_value_surcharge.amount[1].amount": {"2028-01-01.2030-12-31": 0}, "gov.hmrc.council_tax.high_value_surcharge.amount[2].amount": {"2028-01-01.2030-12-31": 0}, "gov.hmrc.council_tax.high_value_surcharge.amount[3].amount": {"2028-01-01.2030-12-31": 0}, "gov.hmrc.council_tax.high_value_surcharge.amount[4].amount": {"2028-01-01.2030-12-31": 0}}`; reform dict `null`

## Reproduce

base:

```bash
# This event is absent from this namespace.
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__high_value_council_tax_surcharge --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__high_value_council_tax_surcharge_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
