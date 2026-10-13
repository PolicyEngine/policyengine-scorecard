# Inventory of OBR-costed fiscal events, June 2010–Autumn Budget 2025

Track 2 of #156, reviewed 9 October 2026. This inventory covers **32 events,
3,796 measure × head rows** and **1,858 event-specific measure titles**.
Every published original-scorecard FY cell, including zeroes, is retained in
[`inventory.jsonl`](../../data/uk/events/inventory.jsonl). The event totals are
in [`event_summary.json`](../../data/uk/events/event_summary.json).

The scope is the November 2025 Policy measures database, from its exact event
label `Budget 2010 #2` to `Autumn Budget 2025`. It includes Statements and the
2020 Spending Review where the database carries costings; it does not silently
add emergency announcements absent from that event list.

## What the classes mean

Household scope includes statutory personal taxes, household consumption
and residential property taxes, benefits, credits, pensions, childcare and
per-employee employer NICs. It describes what a household model could represent
in principle. Business taxes, DEL/block grants, loan-book accounting, operational
compliance yield and public finance accounts remain visible outside scope.
Furlough wage support is included as a per-employee household earnings-support
mechanism, with its employer-grant breadth explicitly recorded in the audit.
Scope reasons are attached to every row; ambiguous decisions are judgements,
not claims that a description fully specifies the law.

Expressibility is checked against **policyengine-uk 2.125.1**, the latest
PyPI release verified in this task, installed in the existing scratch environment
and read as source. `expressible` means today's liability/entitlement machinery
has a parameter construction for the stated household mechanism; `partial`
names omitted legs or a materially narrower representation; `not` names missing
machinery or inputs. The £ attributed to partial rows is the **whole OBR row**,
not an estimate of the executable fraction. These are scoping verdicts: no
reforms were executed, no population was built, and no event has been certified
as a vintage-faithful replay here. Historical effective dates, data adequacy,
processed parameter values, head mapping and counterfactual schedules still need
review before a machinery verdict becomes a runnable registry construction.

This deliberately differs from track 1's stricter executable-construction
standard. At pinned commit `b469ffc4f14b582360a90ab8c18b69b025e73731`, its five
registries total **321 measures: 0 expressible, 13 partial, 163 not expressible,
145 outside scope**, on policyengine-uk **2.89.2** and its certified 2023 bundle.
Its `not_expressible` includes `construction_pending`; that does not prove a
liability formula is absent. The present inventory counts measure × head rows,
uses a newer engine and separates machinery from historic readiness. These
counts cannot be compared as if they measured an engine improvement.
See the pinned [RECIPE.md](https://github.com/PolicyEngine/policyengine-scorecard/blob/b469ffc4f14b582360a90ab8c18b69b025e73731/docs/uk_replay/RECIPE.md)
and [YEARS.md](https://github.com/PolicyEngine/policyengine-scorecard/blob/b469ffc4f14b582360a90ab8c18b69b025e73731/docs/uk_replay/YEARS.md).

## Amounts and counts

Gross £ = sum of the absolute costing of **every original-scorecard FY cell**,
across heads, for the event. A sign change does not cancel another year. Positive
raw costings mean gains to the Exchequer on both sheets. All amounts below are
£bn, rounded for display; machine files retain £m values. This is a multi-year
coverage denominator, not an annual expenditure total or the event's net fiscal
stance. Summing events also sums different horizons and revisions/packages;
it is an inventory workload metric, not cumulative policy impact.

A row is a workbook measure × tax/spending head occurrence. Repeated identical
keys remain separate occurrences. Exact titles group into `measure_key` within
each event; class-specific distinct-title counts in JSON can overlap when one
title has heads in different classes. The disjoint accounting below uses rows.

| Class | Rows | Gross £bn | Share of all gross £ |
|---|---:|---:|---:|
| In / expressible | 220 | 855.258 | 14.9% |
| In / partial | 121 | 635.501 | 11.0% |
| In / not expressible | 626 | 493.827 | 8.6% |
| Outside household scope | 2,829 | 3,769.352 | 65.5% |

Household scope contains **967 rows** and **34.5%** of gross £; fully expressible rows cover **14.9%** of gross £. Including partial rows gives an upper scoping envelope of **25.9%**, not a computed coverage fraction.

| Event | Titles | Rows | Expressible | Partial | Not | Out | Original scoring FYs |
|---|---:|---:|---:|---:|---:|---:|---|
| Budget 2010 #2 | 49 | 66 | 10 | 10 | 32 | 14 | 2010-11 → 2014-15 |
| Autumn 2010 | 26 | 39 | 12 | 0 | 9 | 18 | 2010-11 → 2015-16 |
| Budget 2011 | 60 | 79 | 5 | 4 | 20 | 50 | 2011-12 → 2015-16 |
| Autumn 2011 | 31 | 38 | 7 | 1 | 9 | 21 | 2011-12 → 2016-17 |
| Budget 2012 | 56 | 84 | 3 | 3 | 20 | 58 | 2012-13 → 2016-17 |
| Autumn 2012 | 39 | 71 | 7 | 5 | 8 | 51 | 2012-13 → 2017-18 |
| Budget 2013 | 68 | 109 | 4 | 2 | 32 | 71 | 2013-14 → 2017-18 |
| Autumn 2013 | 60 | 109 | 6 | 1 | 7 | 95 | 2013-14 → 2018-19 |
| Budget 2014 | 57 | 101 | 3 | 4 | 31 | 63 | 2014-15 → 2018-19 |
| Autumn 2014 | 61 | 100 | 0 | 2 | 18 | 80 | 2014-15 → 2019-20 |
| Budget 2015 | 48 | 73 | 3 | 1 | 13 | 56 | 2015-16 → 2019-20 |
| Budget 2015 #2 | 61 | 110 | 13 | 11 | 27 | 59 | 2015-16 → 2020-21 |
| Autumn 2015 | 34 | 56 | 3 | 4 | 11 | 38 | 2015-16 → 2020-21 |
| Budget 2016 | 78 | 136 | 11 | 0 | 31 | 94 | 2015-16 → 2020-21 |
| Autumn 2016 | 48 | 90 | 4 | 0 | 23 | 63 | 2016-17 → 2021-22 |
| Budget 2017 | 37 | 63 | 3 | 1 | 4 | 55 | 2017-18 → 2021-22 |
| Autumn Budget 2017 | 76 | 141 | 4 | 1 | 16 | 120 | 2017-18 → 2022-23 |
| Spring Statement 2018 | 10 | 17 | 0 | 1 | 4 | 12 | 2017-18 → 2022-23 |
| Budget 2018 | 104 | 219 | 5 | 6 | 20 | 188 | 2018-19 → 2023-24 |
| Spring Statement 2019 | 20 | 33 | 1 | 2 | 3 | 27 | 2018-19 → 2023-24 |
| Budget 2020 | 104 | 244 | 5 | 4 | 36 | 199 | 2019-20 → 2024-25 |
| Spending Review 2020 | 62 | 149 | 8 | 4 | 22 | 115 | 2019-20 → 2025-26 |
| Spring Budget 2021 | 65 | 170 | 11 | 2 | 29 | 128 | 2020-21 → 2025-26 |
| Autumn Budget 2021 | 66 | 180 | 7 | 10 | 25 | 138 | 2021-22 → 2026-27 |
| Spring Statement 2022 | 41 | 107 | 12 | 9 | 7 | 79 | 2021-22 → 2026-27 |
| Autumn Statement 2022 | 71 | 196 | 22 | 9 | 23 | 142 | 2022-23 → 2027-28 |
| Spring Budget 2023 | 89 | 170 | 4 | 6 | 24 | 136 | 2022-23 → 2027-28 |
| Autumn Statement 2023 | 77 | 186 | 10 | 2 | 23 | 151 | 2023-24 → 2028-29 |
| Spring Budget 2024 | 49 | 136 | 10 | 3 | 19 | 104 | 2023-24 → 2028-29 |
| Autumn Budget 2024 | 74 | 189 | 8 | 4 | 35 | 142 | 2024-25 → 2029-30 |
| Spring Statement 2025 | 32 | 83 | 2 | 2 | 3 | 76 | 2024-25 → 2029-30 |
| Autumn Budget 2025 | 105 | 252 | 17 | 7 | 42 | 186 | 2025-26 → 2030-31 |

| Event | Gross £bn | Expressible £bn | Partial £bn | Not £bn | Out £bn | Household share | Household + expressible share |
|---|---:|---:|---:|---:|---:|---:|---:|
| Budget 2010 #2 | 221.775 | 87.545 | 30.505 | 19.215 | 84.510 | 61.9% | 39.5% |
| Autumn 2010 | 93.610 | 22.085 | 0.000 | 10.680 | 60.845 | 35.0% | 23.6% |
| Budget 2011 | 55.910 | 11.500 | 4.880 | 5.940 | 33.590 | 39.9% | 20.6% |
| Autumn 2011 | 50.630 | 11.245 | 0.780 | 0.815 | 37.790 | 25.4% | 22.2% |
| Budget 2012 | 55.510 | 2.885 | 15.305 | 11.045 | 26.275 | 52.7% | 5.2% |
| Autumn 2012 | 102.755 | 23.530 | 14.050 | 2.720 | 62.455 | 39.2% | 22.9% |
| Budget 2013 | 67.670 | 5.815 | 4.690 | 21.905 | 35.260 | 47.9% | 8.6% |
| Autumn 2013 | 48.950 | 7.370 | 0.850 | 7.050 | 33.680 | 31.2% | 15.1% |
| Budget 2014 | 39.000 | 0.485 | 8.425 | 10.605 | 19.485 | 50.0% | 1.2% |
| Autumn 2014 | 47.450 | 0.000 | 7.560 | 4.750 | 35.140 | 25.9% | 0.0% |
| Budget 2015 | 33.410 | 7.715 | 3.010 | 7.040 | 15.645 | 53.2% | 23.1% |
| Budget 2015 #2 | 272.035 | 33.860 | 40.605 | 29.610 | 167.960 | 38.3% | 12.4% |
| Autumn 2015 | 124.235 | 22.625 | 23.240 | 4.360 | 74.010 | 40.4% | 18.2% |
| Budget 2016 | 129.145 | 20.275 | 0.000 | 19.175 | 89.695 | 30.5% | 15.7% |
| Autumn 2016 | 78.805 | 6.980 | 0.000 | 17.195 | 54.630 | 30.7% | 8.9% |
| Budget 2017 | 35.770 | 4.105 | 0.400 | 0.445 | 30.820 | 13.8% | 11.5% |
| Autumn Budget 2017 | 86.225 | 10.350 | 0.015 | 6.275 | 69.585 | 19.3% | 12.0% |
| Spring Statement 2018 | 13.820 | 0.000 | 3.490 | 0.540 | 9.790 | 29.2% | 0.0% |
| Budget 2018 | 259.808 | 23.453 | 3.750 | 11.130 | 221.474 | 14.8% | 9.0% |
| Spring Statement 2019 | 23.723 | 0.105 | 1.227 | 1.242 | 21.149 | 10.9% | 0.4% |
| Budget 2020 | 497.799 | 15.482 | 10.446 | 11.575 | 460.296 | 7.5% | 3.1% |
| Spending Review 2020 | 534.346 | 11.872 | 9.563 | 105.973 | 406.937 | 23.8% | 2.2% |
| Spring Budget 2021 | 229.633 | 36.401 | 1.763 | 38.683 | 152.786 | 33.5% | 15.9% |
| Autumn Budget 2021 | 415.637 | 50.301 | 119.683 | 3.423 | 242.230 | 41.7% | 12.1% |
| Spring Statement 2022 | 135.633 | 55.186 | 6.643 | 7.287 | 66.518 | 51.0% | 40.7% |
| Autumn Statement 2022 | 557.310 | 143.584 | 132.645 | 5.678 | 275.402 | 50.6% | 25.8% |
| Spring Budget 2023 | 126.413 | 18.610 | 21.094 | 4.712 | 81.996 | 35.1% | 14.7% |
| Autumn Statement 2023 | 186.490 | 62.549 | 3.428 | 4.955 | 115.559 | 38.0% | 33.5% |
| Spring Budget 2024 | 111.908 | 63.195 | 3.744 | 14.835 | 30.135 | 73.1% | 56.5% |
| Autumn Budget 2024 | 700.668 | 22.815 | 131.722 | 47.044 | 499.087 | 28.8% | 3.3% |
| Spring Statement 2025 | 74.979 | 5.333 | 8.855 | 13.246 | 47.544 | 36.6% | 7.1% |
| Autumn Budget 2025 | 342.887 | 68.001 | 23.132 | 44.679 | 207.075 | 39.6% | 19.8% |

## Provenance, review and limits

The local `~/scorecard-harvest/uk_obr/claims_staged.jsonl` was checked against
this repository's gzip snapshot: uncompressed SHA-256
`46117d14c4de7ac10cbc9bc09acef6c5b5060db1605e02334d4a827cf420a3bd`.
Each row carries the source workbook, sheet, URL and per-FY harvest line/hash.
The OBR workbook is
[Policy measures database, November 2025](https://obr.uk/docs/dlm_uploads/Policy_measures_database_November_2025_.xlsx),
SHA-256 `76fb24ac780364949e5537563a70f8fbbe30cad6c652195704ea5d72b32ea619`.
The [validation receipt](../../data/uk/events/validation_receipt.json) verifies
all retained original workbook cells and records worksheet row/column pointers.
Cells shaded `FFE1E9EE` are nominal-GDP extensions beyond the original scorecard
and are excluded; this follows the workbook Notes and the source staging script
`~/scorecard-harvest/uk_obr/stage_pmd.py`, read during this review.

The earlier lane's classifications were recovered without reclassification of
the entire corpus. This review validates every path/variable and source value,
and spot-checks the central machinery, survivor disputes, largest rows and
cross-event inconsistencies. It is **not a statutory audit of all 3,796 rows**.
[CLASSIFICATION_AUDIT.md](research/CLASSIFICATION_AUDIT.md) records adjudications,
corrections and judgement calls. The raw parameter index resolves cited paths;
`mechanism_evidence` names installed-source files and checked-in assessments.
[The selected source snapshot](evidence/classification_sources.json) preserves
465 base-audit source files and hashes after scratch cleanup.
[The 2.125.1 patch snapshot](evidence/patch_sources.json) and
[release diff](../../data/uk/events/patch_release_receipt.json) preserve the latest
Class 2/Class 4 and UC minimum-income-floor changes, inspected before freezing the
inventory. Earlier source receipts remain labelled with their audited versions.
The [source receipt](../../data/uk/events/source_receipt.json) pins the wheel,
PyPI check and track 1 commit. The older 2.124.0 index/notes remain as research
history; the builder explicitly chooses the new version.

The `parameter_history` flag checks whether each cited YAML leaf has any date
key by 6 April of the first nonzero costing FY. It does **not** establish correct
law throughout the window: nulls, placeholder early values, missing historical
regimes, formula start dates, uprating and fiscal-year processing need the
[historical rules audit](HISTORICAL_RULES.md). Generic input variables alone
cannot make an unimplemented entitlement executable in track 1's parameter-only
executor. Missing baselines and population vintages remain explicit gaps.

Rebuild/verify, without initializing a model:

```bash
python3 data/uk/events/build_inventory.py
python3 data/uk/events/build_inventory.py --check
python3 data/uk/events/validate_inventory.py
python3 data/uk/events/render_inventory.py
```

Re-indexing needs the pinned installed package and policyengine-core, using
`data/uk/events/index_pe_uk.py`; it reads raw parameters and source AST only.
Optional independent workbook validation needs openpyxl and the already
harvested workbook; the exact command is in [the plan](PLAN.md).

The main blockers are the historical-rule floor and retired scheme modelling,
year-specific populations and an event-vintage calibration contract. Aggregate
OBR forecasts are available for all events; detailed harvested forecast tables
cover only three. See [POPULATIONS_AND_VINTAGES.md](POPULATIONS_AND_VINTAGES.md)
and [PLAN.md](PLAN.md) for the route from this inventory to numerical comparisons.
