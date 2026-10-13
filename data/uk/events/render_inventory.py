"""Render the reviewable event tables from event_summary.json; engine-free."""
import json
from collections import defaultdict
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
j=json.loads((HERE/'event_summary.json').read_text())
events=sorted(j['events'].items(),key=lambda kv:kv[1]['event_index'])
keys=['in:expressible','in:partial','in:not','out']
allc=defaultdict(lambda:[0,0.])
for ev,s in events:
 for k,c in s['classes'].items():allc[k][0]+=c['rows'];allc[k][1]+=c['gross_gbp_m']
gross=sum(s['gross_gbp_m'] for _,s in events)
text='''# Inventory of OBR-costed fiscal events, June 2010–Autumn Budget 2025

Track 2 of #156, reviewed 9 October 2026. This inventory covers **32 events,
3,796 measure × head rows** and **{measures:,} event-specific measure titles**.
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

Expressibility is checked against **policyengine-uk {version}**, the latest
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
'''.format(measures=sum(s['measures'] for _,s in events),version=j['engine'].split()[-1])
names={'in:expressible':'In / expressible','in:partial':'In / partial','in:not':'In / not expressible','out':'Outside household scope'}
for k in keys:
 n,g=allc[k];text+=f'| {names[k]} | {n:,} | {g/1000:,.3f} | {g/gross:.1%} |\n'
text+=f'\nHousehold scope contains **{sum(allc[k][0] for k in keys[:3]):,} rows** and **{sum(allc[k][1] for k in keys[:3])/gross:.1%}** of gross £; fully expressible rows cover **{allc[keys[0]][1]/gross:.1%}** of gross £. Including partial rows gives an upper scoping envelope of **{(allc[keys[0]][1]+allc[keys[1]][1])/gross:.1%}**, not a computed coverage fraction.\n'
text+='\n| Event | Titles | Rows | Expressible | Partial | Not | Out | Original scoring FYs |\n|---|---:|---:|---:|---:|---:|---:|---|\n'
for ev,s in events:
 counts=[s['classes'].get(k,{}).get('rows',0) for k in keys]
 text+=f"| {ev} | {s['measures']} | {s['rows']} | "+' | '.join(str(n) for n in counts)+f" | {' → '.join(s['scoring_fys'])} |\n"
text+='\n| Event | Gross £bn | Expressible £bn | Partial £bn | Not £bn | Out £bn | Household share | Household + expressible share |\n|---|---:|---:|---:|---:|---:|---:|---:|\n'
for ev,s in events:
 gs=[s['classes'].get(k,{}).get('gross_gbp_m',0)/1000 for k in keys]
 text+=f"| {ev} | {s['gross_gbp_m']/1000:,.3f} | "+' | '.join(f'{g:,.3f}' for g in gs)+f" | {s['share_in_scope']:.1%} | {s['share_in_scope_expressible']:.1%} |\n"
text+='''
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
'''
(ROOT/'docs/uk_replay/INVENTORY.md').write_text(text)
print('wrote INVENTORY.md')
