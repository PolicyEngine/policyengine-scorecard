# Investigation packet: autumn_budget_2025 / ab2025__dividend_rates_plus_2pp / CY2026

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Dividend Income: Increase tax rates on dividend income by 2ppts at the ordinary and upper rate from 6 April 2026
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12307:90ac5224d0623421 | — | 926.7 | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12313:b2511408029ed0d7 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12319:e7697416ea2e9816 | — | 0.0 | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12325:2be73b17d5498ede | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23952:acf693b4bf12e0bf | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:23958:fe18a1efe2173692 | — | — | — | coverage | event_on_head_only |
| measure_year | total | — | 926.7 | — | — | — |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12307:90ac5224d0623421 (row 12307) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Income tax | 335.6 | — | 926.7 |
| head | obr_pmd_nov2025:12313:b2511408029ed0d7 (row 12313) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Corporation tax (onshore) | -57.9 | — | — |
| head | obr_pmd_nov2025:12319:e7697416ea2e9816 (row 12319) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | NICs | 0.0 | — | 0.0 |
| head | obr_pmd_nov2025:12325:2be73b17d5498ede (row 12325) | Tax Measures (Policy measures database) / 2026-27 | 2026-27 | Capital gains tax | 0.0 | — | — |
| head | obr_pmd_nov2025:23952:acf693b4bf12e0bf (row 23952) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | PSCE in RDEL | 0.0 | — | — |
| head | obr_pmd_nov2025:23958:fe18a1efe2173692 (row 23958) | Spending Measures (Policy measures database) / 2026-27 | 2026-27 | Scottish BGA (current) | 0.0 | — | — |

## Executed worlds

* base: no artifact
* head: `results/uk/replays/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__dividend_rates_plus_2pp_2026.json` (sha256 `958579265404e6d5efbff75eec4fbd86211833c0ec6693ba71f1c249c7a0061a`), reversal_on_certified_world; baseline dict `{"gov.hmrc.income_tax.rates.dividends[0].rate": {"2026-01-01.2030-12-31": 0.0875}, "gov.hmrc.income_tax.rates.dividends[1].rate": {"2026-01-01.2030-12-31": 0.3375}}`; reform dict `null`

## Reproduce

base:

```bash
# This event is absent from this namespace.
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__dividend_rates_plus_2pp --years 2026 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__dividend_rates_plus_2pp_2026
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
