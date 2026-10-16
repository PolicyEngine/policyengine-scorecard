# Investigation packet: autumn_budget_2025 / ab2025__ppf_and_fas_pre_1997_inflation_protection / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Defined Benefit Pensions: Provide inflation protection for pre-1997 pensions in the Pension Protection Fund (PPF) and Financial Assistance Scheme (FAS) where members’ former schemes provided it, from 1 January 2027
* Flags: coverage
* Base: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`
* Head: `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:12704:08235b22b049f6bb | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:12710:ba37676958390965 | — | — | — | coverage | event_on_head_only |
| source_row | obr_pmd_nov2025:24133:4fa9a81c3f5d9506 | — | — | — | coverage | event_on_head_only |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| head | obr_pmd_nov2025:12704:08235b22b049f6bb (row 12704) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Gross operating surplus | -62.0 | — | — |
| head | obr_pmd_nov2025:12710:ba37676958390965 (row 12710) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Income tax | 4.0 | — | — |
| head | obr_pmd_nov2025:24133:4fa9a81c3f5d9506 (row 24133) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Public corporations capital expenditure | 0.0 | — | — |

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
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2025 --variant pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2025_measures.json --measures ab2025__ppf_and_fas_pre_1997_inflation_protection --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2025/ab2025__ppf_and_fas_pre_1997_inflation_protection_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
