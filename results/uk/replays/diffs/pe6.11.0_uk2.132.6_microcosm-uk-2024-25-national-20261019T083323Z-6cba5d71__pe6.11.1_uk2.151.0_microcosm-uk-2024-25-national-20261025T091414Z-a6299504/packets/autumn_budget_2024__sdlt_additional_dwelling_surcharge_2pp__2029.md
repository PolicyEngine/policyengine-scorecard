# Investigation packet: autumn_budget_2024 / autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp / CY2029

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Stamp Duty Land Tax (SDLT): Increase the Higher Rate of Additional Dwelling (HRAD) of SDLT by 2ppts from 3% to 5% from 31 October 2024
* Flags: numerical, structural, inertness, construction
* Base: `pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71`
* Head: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:11651:9a7327566a66890c | 2,151.2 | — | — | inertness | inert_on_head_only |
| source_row | obr_pmd_nov2025:11657:7fa7efce401257e4 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:11663:7a186012776764b9 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22810:b94a793fb1d3c286 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22816:4ee584ef8c6c1052 | — | — | — | — | — |
| measure_year | total | 2,151.2 | 0.0 | -2,151.2 | numerical, structural, inertness, construction | move_above_threshold; zero_crossing; inert_on_head_only; premise_check_changed (forward_delta_changes_current_law) |
| head | stamp_duty_land_tax | 2,151.2 | 0.0 | -2,151.2 | numerical, structural | move_above_threshold; zero_crossing |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:11651:9a7327566a66890c (row 11651) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Stamp duty | 490.3 | 2,151.2 | — |
| base | obr_pmd_nov2025:11657:7fa7efce401257e4 (row 11657) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Capital gains tax | -129.2 | — | — |
| base | obr_pmd_nov2025:11663:7a186012776764b9 (row 11663) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Inheritance tax | -84.7 | — | — |
| base | obr_pmd_nov2025:22810:b94a793fb1d3c286 (row 22810) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Scottish BGA (current) | 22.8 | — | — |
| base | obr_pmd_nov2025:22816:4ee584ef8c6c1052 (row 22816) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | PSCE in RDEL | 9.9 | — | — |
| head | obr_pmd_nov2025:11651:9a7327566a66890c (row 11651) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Stamp duty | 490.3 | 2,151.2 | — |
| head | obr_pmd_nov2025:11657:7fa7efce401257e4 (row 11657) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Capital gains tax | -129.2 | — | — |
| head | obr_pmd_nov2025:11663:7a186012776764b9 (row 11663) | Tax Measures (Policy measures database) / 2029-30 | 2029-30 | Inheritance tax | -84.7 | — | — |
| head | obr_pmd_nov2025:22810:b94a793fb1d3c286 (row 22810) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | Scottish BGA (current) | 22.8 | — | — |
| head | obr_pmd_nov2025:22816:4ee584ef8c6c1052 (row 22816) | Spending Measures (Policy measures database) / 2029-30 | 2029-30 | PSCE in RDEL | 9.9 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2029.json` (sha256 `a9864d670f6d80de1bdc98ae8e01535766d686a65e30410c8f703a1253c4198f`), forward_delta_on_certified_world; baseline dict `null`; reform dict `{"gov.hmrc.stamp_duty.residential.purchase.additional.rate[0].rate": {"2024-10-31.2035-12-31": 0.05}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[1].rate": {"2024-10-31.2035-12-31": 0.07}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[2].rate": {"2024-10-31.2035-12-31": 0.1}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[3].rate": {"2024-10-31.2035-12-31": 0.15}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[4].rate": {"2024-10-31.2035-12-31": 0.17}}`
* head: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2029.json` (sha256 `62c04a60ddc7eccbf544359491fe7f36d4c880d656fb4cc9c3372d4f24015e2b`), forward_delta_on_certified_world; baseline dict `null`; reform dict `{"gov.hmrc.stamp_duty.residential.purchase.additional.rate[0].rate": {"2024-10-31.2035-12-31": 0.05}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[1].rate": {"2024-10-31.2035-12-31": 0.07}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[2].rate": {"2024-10-31.2035-12-31": 0.1}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[3].rate": {"2024-10-31.2035-12-31": 0.15}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[4].rate": {"2024-10-31.2035-12-31": 0.17}}`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2029
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp --years 2029 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2029
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
