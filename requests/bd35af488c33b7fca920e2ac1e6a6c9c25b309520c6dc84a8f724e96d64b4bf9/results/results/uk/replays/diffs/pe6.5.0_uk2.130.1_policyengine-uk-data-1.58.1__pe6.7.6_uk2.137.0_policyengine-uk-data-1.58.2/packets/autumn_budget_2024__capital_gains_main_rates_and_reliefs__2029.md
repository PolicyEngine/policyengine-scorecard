# Investigation packet: autumn_budget_2024 / autumn_budget_2024__capital_gains_main_rates_and_reliefs / CY2029

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Capital Gains Tax: Increase the main rates of CGT to 18% and 24% from 30 October 2024, and the Business Asset Disposal Relief (BADR) and Investors' Relief (IR) rate to 14% from 6 April 2025 and to 18% from 6 April 2026
* Flags: numerical
* Base: `pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`
* Head: `pe6.7.6_uk2.137.0_policyengine-uk-data-1.58.2`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:11687:f738e039412d9872 | 2,660.3 | 1,995.5 | -664.8 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:11693:fce3f1c54885e725 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:11699:6ff71275479301e4 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22834:74c3bd563eca97a5 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22840:1197e330a3c46ef4 | — | — | — | — | — |
| measure_year | total | 2,660.3 | 1,995.5 | -664.8 | numerical | move_above_threshold |
| head | capital_gains_tax | 2,660.3 | 1,995.5 | -664.8 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:11687:f738e039412d9872 (row 11687) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Capital gains tax | 985.9 | 2,660.3 | 1,995.5 |
| base | obr_pmd_nov2025:11693:fce3f1c54885e725 (row 11693) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Stamp duty | -58.7 | — | — |
| base | obr_pmd_nov2025:11699:6ff71275479301e4 (row 11699) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Income tax | 1,470.6 | — | — |
| base | obr_pmd_nov2025:22834:74c3bd563eca97a5 (row 22834) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Scottish BGA (current) | 86.7 | — | — |
| base | obr_pmd_nov2025:22840:1197e330a3c46ef4 (row 22840) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | PSCE in RDEL | 6.8 | — | — |
| head | obr_pmd_nov2025:11687:f738e039412d9872 (row 11687) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Capital gains tax | 985.9 | 2,660.3 | 1,995.5 |
| head | obr_pmd_nov2025:11693:fce3f1c54885e725 (row 11693) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Stamp duty | -58.7 | — | — |
| head | obr_pmd_nov2025:11699:6ff71275479301e4 (row 11699) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Income tax | 1,470.6 | — | — |
| head | obr_pmd_nov2025:22834:74c3bd563eca97a5 (row 22834) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Scottish BGA (current) | 86.7 | — | — |
| head | obr_pmd_nov2025:22840:1197e330a3c46ef4 (row 22840) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | PSCE in RDEL | 6.8 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__capital_gains_main_rates_and_reliefs_2029.json` (sha256 `5e3adf4fcffed12be4388beb9b93be61747ed19eb63cb6754fc61b01e69b2628`), reversal_on_certified_world; baseline dict `{"gov.hmrc.cgt.additional_rate": {"2024-01-01.2035-12-31": 0.2}, "gov.hmrc.cgt.basic_rate": {"2024-01-01.2035-12-31": 0.1}, "gov.hmrc.cgt.higher_rate": {"2024-01-01.2035-12-31": 0.2}}`; reform dict `null`
* head: `results/uk/replays/pe6.7.6_uk2.137.0_policyengine-uk-data-1.58.2/autumn_budget_2024/autumn_budget_2024__capital_gains_main_rates_and_reliefs_2029.json` (sha256 `09eda2d476ab94394fdebd29f508661ceb763fc25e512729ff2f1bf79f0ea40b`), reversal_on_certified_world; baseline dict `{"gov.hmrc.cgt.additional_rate": {"2024-01-01.2035-12-31": 0.2}, "gov.hmrc.cgt.basic_rate": {"2024-01-01.2035-12-31": 0.1}, "gov.hmrc.cgt.higher_rate": {"2024-01-01.2035-12-31": 0.2}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__capital_gains_main_rates_and_reliefs --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1/autumn_budget_2024/autumn_budget_2024__capital_gains_main_rates_and_reliefs_2029
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.7.6_uk2.137.0_policyengine-uk-data-1.58.2 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__capital_gains_main_rates_and_reliefs --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.7.6_uk2.137.0_policyengine-uk-data-1.58.2/autumn_budget_2024/autumn_budget_2024__capital_gains_main_rates_and_reliefs_2029
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
