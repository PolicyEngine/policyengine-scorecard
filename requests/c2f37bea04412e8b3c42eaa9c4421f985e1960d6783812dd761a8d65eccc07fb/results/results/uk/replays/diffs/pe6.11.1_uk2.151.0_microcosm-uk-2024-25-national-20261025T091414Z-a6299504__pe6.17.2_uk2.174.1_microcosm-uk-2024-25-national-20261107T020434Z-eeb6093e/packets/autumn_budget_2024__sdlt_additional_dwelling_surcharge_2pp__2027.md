# Investigation packet: autumn_budget_2024 / autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp / CY2027

This pipeline files no issues. The coordinating session reviews the packet and decides whether to file upstream.

* Title: Stamp Duty Land Tax (SDLT): Increase the Higher Rate of Additional Dwelling (HRAD) of SDLT by 2ppts from 3% to 5% from 31 October 2024
* Flags: numerical
* Base: `pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504`
* Head: `pe6.17.2_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e`

## Movements (£m, positive = gain to the Exchequer)

| Level | Key | Base | Head | Change | Flags | Details |
|---|---|---:|---:|---:|---|---|
| source_row | obr_pmd_nov2025:11649:910077d14a180f90 | 1,044.7 | 1,075.2 | 30.5 | numerical | move_above_threshold |
| source_row | obr_pmd_nov2025:11655:2e1dc1d269227e2f | — | — | — | — | — |
| source_row | obr_pmd_nov2025:11661:a5ce1ea1b223ab58 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22808:c8fe3aecef088bf1 | — | — | — | — | — |
| source_row | obr_pmd_nov2025:22814:3608d4c47b99f4c7 | — | — | — | — | — |
| measure_year | total | 1,044.7 | 1,075.2 | 30.5 | numerical | move_above_threshold |
| head | stamp_duty_land_tax | 1,044.7 | 1,075.2 | 30.5 | numerical | move_above_threshold |

## OBR source cells

| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |
|---|---|---|---|---|---:|---:|---:|
| base | obr_pmd_nov2025:11649:910077d14a180f90 (row 11649) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Stamp duty | 413.5 | 1,044.7 | 1,075.2 |
| base | obr_pmd_nov2025:11655:2e1dc1d269227e2f (row 11655) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Capital gains tax | -117.9 | — | — |
| base | obr_pmd_nov2025:11661:a5ce1ea1b223ab58 (row 11661) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Inheritance tax | -70.6 | — | — |
| base | obr_pmd_nov2025:22808:c8fe3aecef088bf1 (row 22808) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | 19.3 | — | — |
| base | obr_pmd_nov2025:22814:3608d4c47b99f4c7 (row 22814) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | 8.4 | — | — |
| head | obr_pmd_nov2025:11649:910077d14a180f90 (row 11649) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Stamp duty | 413.5 | 1,044.7 | 1,075.2 |
| head | obr_pmd_nov2025:11655:2e1dc1d269227e2f (row 11655) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Capital gains tax | -117.9 | — | — |
| head | obr_pmd_nov2025:11661:a5ce1ea1b223ab58 (row 11661) | Tax Measures (Policy measures database) / 2027-28 | 2027-28 | Inheritance tax | -70.6 | — | — |
| head | obr_pmd_nov2025:22808:c8fe3aecef088bf1 (row 22808) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | Scottish BGA (current) | 19.3 | — | — |
| head | obr_pmd_nov2025:22814:3608d4c47b99f4c7 (row 22814) | Spending Measures (Policy measures database) / 2027-28 | 2027-28 | PSCE in RDEL | 8.4 | — | — |

## Executed worlds

* base: `results/uk/replays/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2027.json` (sha256 `ad56cbb268ec539e83582900ff9a23cc11a0640ee8f31de2490cc1d0b612882b`), reversal_on_certified_world; baseline dict `{"gov.hmrc.stamp_duty.residential.purchase.additional.rate[0].rate": {"2024-10-31.2035-12-31": 0.03}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[1].rate": {"2024-10-31.2035-12-31": 0.05}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[2].rate": {"2024-10-31.2035-12-31": 0.08}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[3].rate": {"2024-10-31.2035-12-31": 0.13}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[4].rate": {"2024-10-31.2035-12-31": 0.15}}`; reform dict `null`
* head: `results/uk/replays/pe6.17.2_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2027.json` (sha256 `7ad1e3839169ce25286a9bc280f2ad83c70ec2d08960a4c1450e556cc6266d02`), reversal_on_certified_world; baseline dict `{"gov.hmrc.stamp_duty.residential.purchase.additional.rate[0].rate": {"2024-10-31.2035-12-31": 0.03}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[1].rate": {"2024-10-31.2035-12-31": 0.05}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[2].rate": {"2024-10-31.2035-12-31": 0.08}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[3].rate": {"2024-10-31.2035-12-31": 0.13}, "gov.hmrc.stamp_duty.residential.purchase.additional.rate[4].rate": {"2024-10-31.2035-12-31": 0.15}}`; reform dict `null`

## Reproduce

base:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504 --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.11.1_uk2.151.0_microcosm-uk-2024-25-national-20261025T091414Z-a6299504/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2027
```

head:

```bash
PYTHONPATH=. python pipeline/compute_uk_event.py --event autumn_budget_2024 --variant pe6.17.2_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e --registry data/uk/events/autumn_budget_2024_measures.json --measures autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp --years 2027 --workers 1 --output-dir .venv-replay-checks/reproductions/pe6.17.2_uk2.174.1_microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e/autumn_budget_2024/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp_2027
```

## Sources the registry cites

* none recorded

## Minimal case

To be completed by the investigating lane.

## Statutory evidence

To be completed by the investigating lane.
