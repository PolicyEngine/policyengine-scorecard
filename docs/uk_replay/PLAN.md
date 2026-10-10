# Plan for vintage-faithful fiscal-event replay

Decision brief for #156, track 2, 9 October 2026. **Fund a gated programme,
starting with 2022; do not promise a complete 2010–2025 numerical replay from
one population.** The inventory makes every OBR measure visible, including
outside-scope and unimplemented rows. Numerical completion means certified
comparisons for the supported household legs, with explicit missing legs and
heads; a household model cannot deliver corporation-tax or departmental-account
counterparts simply by broadening its registry.

[INVENTORY.md](INVENTORY.md) has all 32 events and the count/£ denominators.
[HISTORICAL_RULES.md](HISTORICAL_RULES.md) identifies policy work, and
[POPULATIONS_AND_VINTAGES.md](POPULATIONS_AND_VINTAGES.md) gives every event's
forecast vintage and archive queue. This plan covers the **26 events in
2010–2022** first. The five recent track 1 events and Autumn Budget 2025 remain
in the inventory; their faithful-vintage extensions share the same machinery.

## What already exists

Build on track 1 at commit `b469ffc4f14b582360a90ab8c18b69b025e73731`
([draft PR #157](https://github.com/PolicyEngine/policyengine-scorecard/pull/157)).
Its five registries preserve source-head/FY accounting, named constructions,
reversal orientation, missing legs, deterministic pair artifacts, resume/hash
receipts and staging/comparison. Its
[RECIPE.md](https://github.com/PolicyEngine/policyengine-scorecard/blob/b469ffc4f14b582360a90ab8c18b69b025e73731/docs/uk_replay/RECIPE.md)
and [YEARS.md](https://github.com/PolicyEngine/policyengine-scorecard/blob/b469ffc4f14b582360a90ab8c18b69b025e73731/docs/uk_replay/YEARS.md)
were read here. No track 1 runs were repeated.

The reusable interface is the source accounting and artifact/counterfactual
contract. Its certified dataset declares **policyengine-uk 2.89.2**, and its
single-population projection window is CY2023–2030. Today's **2.125.1** machinery
inventory cannot substitute that engine into the certified bundle. A new
engine/population pairing needs its own certification and managed-loader
integration. The track 1 registry's `construction_pending` gaps are a useful
work queue, not evidence that all underlying formulas are absent.

A faithful build needs an identity richer than year alone:

```text
(event, costing FY, policy world, historical survey release,
 forecast release identity, annualisation bridge, engine commit,
 population artifact digest, certification receipt)
```

Published welfare forecasts often already include the announced measures.
Choose and document a policy-world contract: calibrate the published end-state
once, then evaluate the pre-measure counterfactual on the same records/weights;
or obtain a documented pre-measures level bridge. Do not calibrate each reform
separately to force its OBR delta. Preserve statutory liability versus cash
receipts, devolved geography, fiscal versus calendar year, and behaviour as
comparison axes. Any macro feedback or forestalling remains an explicit omitted
channel unless separately implemented and evidenced. The architecture's ban on
survey-derived tax-benefit calibration targets remains binding: use survey
structure/income margins and administrative observations, with vintage forecast
levels for the projected world. OBR policy costings remain held-out comparisons.

## Phases and effort

These are **planning estimates, not measured throughput**. A lane-day is one
focused working day on a bounded workstream including human review. Ranges
include adapter work, source QA and certification; they exclude waiting for
survey access, external reviews and upstream releases. Parallel lanes reduce
elapsed time, not the sum of lane-days. Missing historic data or unmodelled
bases can exceed these ranges; gate the next phase on evidence from the first.
The policy-area effort labels in HISTORICAL_RULES are diagnostic components,
not another additive budget.

| Phase | Events / milestone | Estimated lane-days | Dependencies and exit gate |
|---|---|---:|---|
| 0. Contracts and source locks | Event-vintage selector, population/year manifest, original-FY and cash/liability bridges; one 2022 target contract | 8–12 | Read-only archive QA; Chronicle release identities; Microcosm selector and source pins. No target silently falls back to another vintage; every unavailable series is recorded. |
| 1. Recent historic pilot | Spring Statement 2022, Autumn Statement 2022, Autumn Budget 2021; prioritise employee NIC thresholds, income-tax thresholds/freezes and UC taper/work allowances | 24–40 | Existing parameter machinery plus historical schedules; 2021/2022 FRS adapters and event/scoring-year builds; vintage OBR determinants and DWP caseload/benefit detail; new certification. Exit: reproducible full source accounting, supported household-leg comparisons, held-out checks and explicit missing years/legs. |
| 2. Extend 2017–2019 | Budget 2017, Autumn Budget 2017, Spring Statement 2018, Budget 2018, Spring Statement 2019 | 25–45 | Reuse phase 1 contracts; annual FRS pins; legacy/UC allocation and income-distribution history. Empty or narrow household events still get an accounted registry. Exit: all five events covered with supported heads or named blockers. |
| 3. Complete 2020–2021 | Budget 2020, Spending Review 2020, Spring Budget 2021 | 35–60 | Pandemic earnings/status and support data; temporary UC/tax-credit changes; per-year weights/targets; CJRS/SEISS eligibility/payment machinery if claimed as numerically replayed. Ordinary static aging cannot establish pandemic employment transitions. Exit: separate statutory and exceptional-support channels; no modern-distribution COVID replay labelled vintage faithful. |
| 4. The transition years | Budget 2015, Budget 2015 #2, Autumn 2015, Budget 2016, Autumn 2016 | 35–60 | Tax-credit/UC transition and receipt gates; legacy entitlement formulas; old/new State Pension cohorts and additional pension data; historic benefit cap, dividend/savings regimes and property-tax dates. Exit: independently checked pre/post-law test cases and two compatible annual population builds before expanding to all five. |
| 5. Reach June 2010 | The ten events Budget 2010 #2 through Autumn 2014 | 55–95 | Extend the engine's pre-2015 processing boundary; complete 2010–2014 parameter history and retired regimes; historical survey adapters, archive targets and certification. Start with VAT/main rates and personal allowances, retaining age-related allowance gaps; then benefit/uprating packages. Exit: all ten events accounted, each supported leg matched to dated law and forecast/population identity. |
| 6. Household coverage expansion | Missing bases and mechanisms across all events: IHT/estates, APD/IPT, transaction/ownership data, ISA/pension histories, old duties and residual entitlements | 60–120 additional | Source availability and household-base definitions first; implement model/data machinery upstream, then certify. No evidence-based promise of 100% household numerical coverage is possible yet. |

Phases 0–5 total **182–312 lane-days** for a first vintage-faithful programme of
supported household legs and complete source accounting. With the optional
coverage expansion, allow **242–432 lane-days**. This does not buy business-tax,
DEL or compliance modelling. The timeline remains unknown until the first
historical survey ingestion and vintage target compilation have passed.
Archive retrieval itself is not the dominant engineering estimate.

The 2022 events offer relatively high fully expressible gross-£ shares in the
inventory and less historical-rule distance. The June 2010 VAT/allowance package
also has substantial machinery coverage, but its pre-2015 infrastructure makes
it a later fidelity phase. Spending Review 2020 and departmental-spending-heavy
Budgets have low household coverage despite large gross £: their spending
accounts should stay outside household simulation. Use the event table to rank
supported **household** legs, rather than ranking raw Budget size or pretending
the entirety of a partial row is executable.

## Dependencies to make explicit

| Workstream | Concrete artifact | What blocks it |
|---|---|---|
| PolicyEngine UK historical rules | Dated pre-measure and measure schedules; retired-scheme formula/input gaps; processed-value QA | Earliest YAML date is not legal-history certification. Backdating current values to 2015 and April sampling can disguise missing law; see the source audit. |
| Microcosm annual populations | Pinned historic FRS readers; annual structure and income inputs; event/scoring-year build manifests | Today's reviewed UK release pin is base 2024/calibration 2025; generic static aging is forward-only and has no UK projection reader. Historic input rights, schema mapping and projections need work. |
| Vintage ingestion | Chronicle releases for each HOFD row and detailed EFO/DWP/HMRC edition, with source-byte/publication identity | HOFD aggregates cover all 32 events, but only three have harvested detailed calibration tables. DWP pages expose all 32 event editions; exact first-release bytes and distributional projections still need checks. |
| Certification and comparison | Managed-loader engine/data compatibility; held-out checks; source head mapping; deterministic receipts and pinned releases | New rules/populations cannot inherit track 1 certification. Missing tax bases and cash/liability differences must remain labelled. |

RuleSpec UK can supply sourced statutory fragments and isolated cases for
selected missing rules. Its current dated corpus does not encode continuous
2010–2025 history or historical household cohorts; it is a source/QA supplement,
not a replacement population or a drop-in engine-history layer. The exact
files, dates and integration gaps are in HISTORICAL_RULES.

## Worth doing before 28 October

Finish phase 0, **8–12 lane-days**, with a small set of reviewable artifacts:
lock the 2022 forecast releases and archive-access receipts; specify the
post/pre-measures calibration contract; enumerate historical FRS source/schema
requirements without downloading datasets; draft the first dated NIC/UC rule
schedules and certification tests. Include an event-registry adapter design that
reuses track 1 accounting while selecting a new engine/population identity.
Run an engine-free target-contract completeness check only if the sources are
available. This is enough to make the post-Budget funding decision concrete.

A separate **2–3 lane-day optional spike** could trace one historic FRS schema
and one published DWP event edition through the contracts, without a population
build. That tests the riskiest assumptions. Do not attempt all annual builds or
an unsupported pre-2023 run before 28 October. In this scoping lane no
microsimulations, population builds or datasets were run/downloaded.

## Where a single population gives a usable labelled answer

Track 1's certified 2023 bundle can answer a policy-sensitivity question in its
supported 2023–2030 window: how a historic main income-tax rate/threshold, NIC
rate/threshold, UC taper/work allowance or household VAT/fuel-duty rate would
change liabilities **on this modern projected population**. It is useful for
construction QA, distributional examples and spotting sign/unit errors.
The wrapper must explicitly apply the old schedule to a supported modern year,
retain its parameter-world definition and label `modern_population_sensitivity`;
this is a proposed extension, not an already implemented historic registry.
The answers are conditional on the model's represented tax base and missing
behaviour. Do not put them next to 2010 OBR totals as matched-vintage estimates.

It would mislead for historical tax credits/legacy benefit migration, old State
Pension cohorts, age-related allowances/contracted-out NICs, pandemic furlough
and employment changes, historical earnings/taxpayer distributions, estate or
asset transaction histories, and inflation-driven threshold freezes measured
against an event's own forecast. It also cannot provide the original pre-2023
costing years: track 1's validator rejects them and extension is forward-only.
Reweighting today's households to an aggregate 2010 total cannot reconstruct
those missing cohorts, receipt gates or statutory regimes. Outturn-calibrated
populations are useful retrospective comparators, with a different label; they
are not substitutes for the event's forecast world.

## Reproducible scoping checks

The inventory scripts do not initialize a model. With the already harvested
workbook and an existing openpyxl environment:

```bash
python3 data/uk/events/build_inventory.py --check
python3 data/uk/events/validate_inventory.py
python data/uk/events/validate_inventory.py \
  --workbook ~/scorecard-harvest/uk_obr/downloads/Policy_measures_database_November_2025_.xlsx \
  --receipt data/uk/events/validation_receipt.json
```

The receipt checks every original costing cell against the workbook, preserves
repeated workbook keys, excludes GDP-extension cells and records file hashes
and worksheet coordinates. Source-only historical and population evidence
collectors are checked in with their receipts; they read code/workbooks and
publication metadata, not microdata. The final lane report records executed
checks, git delivery status and scratch cleanup.
