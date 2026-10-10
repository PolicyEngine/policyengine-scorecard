# Populations and forecast vintages

Scope: issue #156, track 2; inspected 9 October 2026. **All 32 events have
aggregate OBR forecast targets in the harvest. None has an event-vintage
population build in the reviewed Microcosm configuration.** The population
problem is larger than downloading the OBR workbooks: historical survey
release pins, annual builds, vintage selection, income distributions and
certification all need work. No build or microsimulation was run here.

The small, durable [receipt collection](evidence/population_receipts.json)
preserves source commits, paths, hashes, selected source text, workbook cells,
the 32-event archive catalog and newly fetched DWP publication metadata.
[The collector](evidence/collect_population_evidence.py) imports no engine.
The earlier [Microcosm notes](research/microcosm_uk.md),
[harvest notes](research/vintage_harvest.md), [OBR archive catalog](research/archive_obr.md)
and [GOV.UK catalog](research/archive_govuk.md) remain detailed finding aids;
their estimates and unchecked claims are not treated as implementations.

## What Microcosm can actually build

The reviewed sources are `PolicyEngine/microcosm@7f235941c27c64d1a2d3e02ed3c483e071b8a366`
and `PolicyEngine/chronicle@1ee7dfe257415ec0066fcf511e01fbaaec23cacd`.
Microcosm's consumed Chronicle artifact has its own older pin,
`825406f98913ab7324c834c3642804e9317a2256`; scanning today's Chronicle
checkout does not prove every scanned package is in that consumed artifact.

| Year(s) | UK population/build status in the reviewed code | What a historical replay needs |
|---|---|---|
| Every year 2010–2022 | No corresponding FRS base release is pinned; no UK annual build family or backcast path is supplied by the reviewed configuration. This is a configuration/code finding, not proof that historical survey files are unavailable. | Pin and adapt historical FRS releases; compile period-specific target contracts; build/certify separate annual populations. Survey acquisition rights and compatibility of old column maps remain unknown. |
| 2023 | The registered default is the certified `populace_uk_2023.h5`, built by the older populace/UK-data pipeline, rather than today's Microcosm UK builder. Its receipt has 149 targets and calibration year 2023. | Recover/review a reproducible 2023 release build and create event-specific forecast projections; preserve the certified artifact as the track 1 comparator. |
| 2024 | FRS 2024-25 is the pinned survey/base year. It is an input to the 2025 build, not a separately certified 2024 calibration. | Author a 2024 target contract and annual certification; parameterizing a CLI year alone does not establish adequate target coverage. |
| 2025 | The UK graph has national and dense build/release roles, using base 2024 and calibration year 2025. The national registry variant is kept off the default pending promotion. Actual current Hub promotion was not checked. | Licensed sources, the pinned Chronicle artifact and release gates are required. Replace the latest-world forecast targets with each event's own vintage. |
| 2026–2030 | Track 1 can project the certified 2023 population through the engine. These are projected inputs on one artifact, not independently built Microcosm annual releases. | Implement/review UK annual projections with event forecast determinants, then certify each scoring-year artifact. |

The base pin is one cached release object with survey/base year 2024 and
calibration year 2025, not a collection of interchangeable survey vintages.
The loader requires `survey_year <= base_year < calibration_year`, and the
country adapter checks source identity and target period. Evidence:
[`uk/frs_release.json`](https://github.com/PolicyEngine/microcosm/blob/7f235941c27c64d1a2d3e02ed3c483e071b8a366/packages/microcosm-build/src/microcosm/build/uk/frs_release.json),
[`uk_runtime/frs_release.py`](https://github.com/PolicyEngine/microcosm/blob/7f235941c27c64d1a2d3e02ed3c483e071b8a366/packages/microcosm-build/src/microcosm/build/uk_runtime/frs_release.py)
and [`country_adapter.py`](https://github.com/PolicyEngine/microcosm/blob/7f235941c27c64d1a2d3e02ed3c483e071b8a366/packages/microcosm-build/src/microcosm/build/uk_runtime/country_adapter.py).
The previous one-year retarget touched 21 raw-table hashes, take-up year,
parity inputs and input-mass receipts; that is a useful concrete template for
historical re-pinning, not an estimate of its cost. See
[`changelog.d/723-uk-frs-2024-25-retarget.changed.md`](https://github.com/PolicyEngine/microcosm/blob/7f235941c27c64d1a2d3e02ed3c483e071b8a366/changelog.d/723-uk-frs-2024-25-retarget.changed.md).
The release pin's `notes` retain SPI 2022-23, WAS round 8 and LCFS 2023-24
donors across that retarget. Historical work therefore also needs a donor
vintage review; changing the FRS year alone would retain much newer donor
information for the earliest events.

Generic forward static aging changes demographic weights and monetary
factors on a fixed cross-section. Its code rejects every projection year at
or before the base year; its documentation explicitly says there is no UK
projection reader. Thus it supplies neither a historical backcast nor a
ready UK multi-year build. It also leaves record memberships and employment
status unchanged. Evidence:
[`static_aging.py`, year guard](https://github.com/PolicyEngine/microcosm/blob/7f235941c27c64d1a2d3e02ed3c483e071b8a366/packages/microcosm-calibrate/src/microcosm/calibrate/static_aging.py#L336),
[`docs/static-aging.md`](https://github.com/PolicyEngine/microcosm/blob/7f235941c27c64d1a2d3e02ed3c483e071b8a366/docs/static-aging.md).
The UK build outputs named single-year H5s and target/gate receipts; see
[`docs/uk-full-build-graph.md`](https://github.com/PolicyEngine/microcosm/blob/7f235941c27c64d1a2d3e02ed3c483e071b8a366/docs/uk-full-build-graph.md)
and [`microcosm-data/registry.py`](https://github.com/PolicyEngine/microcosm/blob/7f235941c27c64d1a2d3e02ed3c483e071b8a366/packages/microcosm-data/src/microcosm/data/registry.py#L101).
The inspected annual publication checks are explicitly for US dataset
families:
[`microcosm-data/annual_projections.py`](https://github.com/PolicyEngine/microcosm/blob/7f235941c27c64d1a2d3e02ed3c483e071b8a366/packages/microcosm-data/src/microcosm/data/annual_projections.py).

The certified 2023 fixture records FRS 2023-24 plus WAS/LCFS/ETB/SPI and
derived imputations, 535,080 households, UK-data commit `dd68c739…`, populace
commit `4aa4b14…`, and artifact SHA-256
`f17306ccb2aad7ff0130be3589b560afb2e2a12a943570911cd0c77f07934833`.
Its 149-target calibration and construction are observations from
[`uk_june_2023/.../release_manifest.json`](https://github.com/PolicyEngine/microcosm/blob/7f235941c27c64d1a2d3e02ed3c483e071b8a366/packages/microcosm-data/tests/fixtures/uk_june_2023/populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z/release_manifest.json),
`build_manifest.json` and `calibration_diagnostics.json` in the same directory;
they do not demonstrate that the current graph reproduces that bundle.

## Calibration and vintage selection

Microcosm's UK graph binds a reviewed household axis, original weights and
selected target problem to its shared calibration kernel. It refuses skipped
selected targets. The full-build target compiler has **1,231 national
references** and stops if any reference is unsupported at the requested
calibration year. A committed older-period receipt compiles only **919** at
2023. This is evidence of a deficient historical target surface; it is not
a live compilation against today's feed, and it does not establish exact
failure counts for other years. Sources:
[`graph_calibration.py`](https://github.com/PolicyEngine/microcosm/blob/7f235941c27c64d1a2d3e02ed3c483e071b8a366/packages/microcosm-build/src/microcosm/build/uk_runtime/graph_calibration.py#L112),
[`full_targets.py`](https://github.com/PolicyEngine/microcosm/blob/7f235941c27c64d1a2d3e02ed3c483e071b8a366/packages/microcosm-build/src/microcosm/build/uk_runtime/full_targets.py#L127),
[`target_references.json`](https://github.com/PolicyEngine/microcosm/blob/7f235941c27c64d1a2d3e02ed3c483e071b8a366/packages/microcosm-build/src/microcosm/build/uk/target_references.json)
and `uk/ledger_compile_parity_production_2023_signed_differences.json`.

Chronicle distinguishes observations from publisher projections and carries
`source.vintage`; its release key hashes the vintage and source-byte identity.
This can represent distinct OBR forecasts for the same costing year. The
reviewed OBR EFO packages are March 2026 only; additional April 2024 fuel-duty
and February 2026 salary-sacrifice releases do not supply the complete
forecast vintage of any of the 32 events. See
[`consumer_fact.v4.schema.json`](https://github.com/PolicyEngine/chronicle/blob/1ee7dfe257415ec0066fcf511e01fbaaec23cacd/docs/schemas/consumer_fact.v4.schema.json),
[`consumer_contract.py::build_source_release_key`](https://github.com/PolicyEngine/chronicle/blob/1ee7dfe257415ec0066fcf511e01fbaaec23cacd/chronicle/consumer_contract.py#L90),
[`efo_receipts_march_2026/source_package.yaml`](https://github.com/PolicyEngine/chronicle/blob/1ee7dfe257415ec0066fcf511e01fbaaec23cacd/packages/obr/efo_receipts_march_2026/source_package.yaml),
and the package list in the receipt collection. Chronicle admin outturns are
useful historic observations, but a modern publication containing historical
outturns does not recreate what was known at an earlier event.

Microcosm target resolution currently uses period policies (`exact`,
`latest_not_after`, `source_window`); its closed selector vocabulary has
`source_table` and fact identity keys but lacks `vintage` and
`source_release_key`. Its series key also normalizes publication-year tokens.
It therefore needs an explicit event-vintage contract, using pinned existing
identity selectors or a reviewed selector extension. **Inference:** mixing
multiple EFO vintages into unpinned period-only references risks ambiguity;
this audit did not execute such a compilation. Evidence:
[`build/ledger_targets.py`, policies and selectors](https://github.com/PolicyEngine/microcosm/blob/7f235941c27c64d1a2d3e02ed3c483e071b8a366/packages/microcosm-build/src/microcosm/build/ledger_targets.py#L3717),
and its `_selector_period_invariant_key` and `_strip_trailing_vintage_year`.

The parallel UK-data target adapter provides a useful list of required source
families, not a historical solution: its pinned OBR vintage is March 2026,
with receipts/expenditure tables, HMRC SPI/ITL/CGT, DWP Stat-Xplore and ONS
population/household sources. Its fiscal-year column mapping is hard-coded
for FY2024-25–2030-31, and its fallback uses committed workbooks of that
same vintage. Evidence:
[`policyengine_uk_data/targets/sources.yaml`](https://github.com/PolicyEngine/policyengine-uk-data/blob/0dc9ef28d8ad303003d4bedcee9b7ddd56f214c5/policyengine_uk_data/targets/sources.yaml)
and [`targets/sources/obr.py`](https://github.com/PolicyEngine/policyengine-uk-data/blob/0dc9ef28d8ad303003d4bedcee9b7ddd56f214c5/policyengine_uk_data/targets/sources/obr.py).

## What the harvest contains

Both `~/scorecard-harvest/uk_obr/downloads/Historical_official_forecasts_database_{March_2025,Spring_2026}.xlsx`
were re-read. Each has 131 worksheets, including 114 data sheets. Spring
2026 adds the November 2025 event forecast and March 2026 forecast; March
2025 covers the first 31 replay events. Use the event-labelled forecast row,
never the workbook's latest `Outturn data*` row. The OBR describes this
database as successive forecasts and recent outturns since 2010. See the
[OBR explanation](https://obr.uk/faq/where-can-i-find-your-previous-forecasts/).

Every event has income tax (total/PAYE/SA), total NICs, VAT, fuel duty, CGT,
IHT, property transaction tax, council tax and total welfare forecast rows,
plus employment, average earnings growth, wages-and-salaries growth, CPI,
RPI and house prices. Those fiscal rows cover the original costing windows
listed below. Welfare inside/outside the cap exists for 23 events, from
December 2014; claimant count exists for 15, November 2010–March 2017.
These are cells verified in the two workbooks, preserved under
`hofd.*.target_sheets` in the receipt collection.

The refreshed comparison finds one removed historic cell: March 2024
employment for CY2022 was 32.929 million in the March 2025 workbook and is
blank in Spring 2026. Other compared shared numeric forecast cells agree.
Consequently Spring 2026 is sufficient for all 32 forecast labels, but it is
not an exact content superset of March 2025. Retain both pins. Parser checks
must handle datetime vintage labels and footnote suffixes; raw vintage
definitions can differ between events (`Contents!B3`).

Only **3 events** have any detailed receipts/expenditure calibration files
in the harvest: October 2024 receipts, March 2025 expenditure, and November
2025 both. Class-specific NICs and non-labour income growth occur in the
two receipts files; programme welfare and population occur in the two
expenditure files. OBR March 2025 ready-reckoner determinants and the HMRC
June 2025 tax ready reckoner provide additional Spring Statement 2025
evidence. No event-matched DWP caseload forecast or complete income
distribution is staged. The harvested DWP forecast is Spring 2026; harvested
HMRC ITL projections use March 2026 assumptions. Their historical rows are
current-publication outturns, not earlier forecast vintages. Workbook names,
sheet lists and selected cells are in `detailed_workbooks`; source coverage
and publication basis are detailed in [the reviewed harvest notes](research/vintage_harvest.md).

## Event-by-event population and target requirements

For **each row**, build a separate population for every listed scoring FY,
with demographics and monetary inputs projected using the stated event
forecast, rather than today's outturn. Use the corresponding HOFD vintage
and the EFO tables from the event's publication; ingest the matching DWP
edition where its publication/revision basis is established. No row is
already delivered as a vintage-faithful Microcosm population.

`H` means only the common HOFD aggregate target set is harvested; `R` adds
detailed receipts; `W` adds detailed expenditure; `RR` adds ready-reckoner
evidence. For public EFO files, `Y` means a capture is listed in the reviewed
archive catalog; `*` means a later revision/re-upload, whose equivalence to
the launch file is unknown; `?` means attribution is inferred; `~` means
captured workbook content remains uninspected; `—` means no 200 capture was
found under the researched names, not proof of global unavailability.
E/R/W are economy/receipts/welfare files. DWP links are publication pages
with event-labelled attachments, newly checked via the Content API; those
attachments have not all been re-downloaded or inspected. ITL entries are
same-EFO publication leads, not an assertion that the later HMRC release
was available at Budget time.

| # | Event | Forecast vintage | Required scoring FYs | Harvest | Public EFO E/R/W | DWP edition page | HMRC ITL same-EFO lead |
|---|---|---|---|---|---|---|---|
| 1 | Budget 2010 #2 | June 2010 | 2010-11–2014-15 | H | Y~/Y~/Y~ | [2010, June](https://www.gov.uk/government/publications/benefit-expenditure-and-caseload-tables-2010) | Unknown; pre-OBR HMRC edition needs recovery |
| 2 | Autumn 2010 | November 2010 | 2010-11–2015-16 | H | Y/Y/Y | [2010, Autumn](https://www.gov.uk/government/publications/benefit-expenditure-and-caseload-tables-2010) | January 2011; basis unverified |
| 3 | Budget 2011 | March 2011 | 2011-12–2015-16 | H | Y*/—/— | [2011, Budget](https://www.gov.uk/government/publications/data-about-people-that-were-receiving-benefits-in-2011-as-published-with-the-budget-and-the-autumn-statement) | April 2011; basis unverified |
| 4 | Autumn 2011 | November 2011 | 2011-12–2016-17 | H | Y/Y/Y | [2011, Autumn](https://www.gov.uk/government/publications/data-about-people-that-were-receiving-benefits-in-2011-as-published-with-the-budget-and-the-autumn-statement) | Not found; unknown |
| 5 | Budget 2012 | March 2012 | 2012-13–2016-17 | H | Y/Y/Y | [2012, Budget](https://www.gov.uk/government/publications/benefit-expenditure-and-caseload-tables-2012) | April 2012; basis unverified |
| 6 | Autumn 2012 | December 2012 | 2012-13–2017-18 | H | Y/Y*/Y* | [2012, Autumn](https://www.gov.uk/government/publications/benefit-expenditure-and-caseload-tables-2012) | January 2013; December 2012 EFO |
| 7 | Budget 2013 | March 2013 | 2013-14–2017-18 | H | Y/Y*/Y* | [2013, Budget](https://www.gov.uk/government/publications/benefit-expenditure-and-caseload-tables-2013) | April 2013; March 2013 EFO |
| 8 | Autumn 2013 | December 2013 | 2013-14–2018-19 | H | —/Y*/Y* | [2013, Autumn](https://www.gov.uk/government/publications/benefit-expenditure-and-caseload-tables-2013) | February 2014; basis unverified |
| 9 | Budget 2014 | March 2014 | 2014-15–2018-19 | H | Y/Y/Y | [2014, Budget](https://www.gov.uk/government/publications/benefit-expenditure-and-caseload-tables-2014) | April 2014; basis unverified |
| 10 | Autumn 2014 | December 2014 | 2014-15–2019-20 | H | Y/Y/Y | [2014, Autumn](https://www.gov.uk/government/publications/benefit-expenditure-and-caseload-tables-2014) | February 2015; basis unverified |
| 11 | Budget 2015 | March 2015 | 2015-16–2019-20 | H | Y*/Y*/Y* | [2015, March](https://www.gov.uk/government/publications/benefit-expenditure-and-caseload-tables-2015) | May 2015; basis unverified |
| 12 | Budget 2015 #2 | July 2015 | 2015-16–2020-21 | H | Y?/Y*/Y* | [2015, Summer](https://www.gov.uk/government/publications/benefit-expenditure-and-caseload-tables-2015) | No tied edition established |
| 13 | Autumn 2015 | November 2015 | 2015-16–2020-21 | H | Y/Y/Y | [2015, Autumn](https://www.gov.uk/government/publications/benefit-expenditure-and-caseload-tables-2015) | No tied edition established |
| 14 | Budget 2016 | March 2016 | 2015-16–2020-21 | H | Y/Y/Y | [2016, March](https://www.gov.uk/government/publications/benefit-expenditure-and-caseload-tables-2016) | May 2016; basis check pending |
| 15 | Autumn 2016 | November 2016 | 2016-17–2021-22 | H | Y/Y/Y | [2016, Autumn](https://www.gov.uk/government/publications/benefit-expenditure-and-caseload-tables-2016) | No tied edition established |
| 16 | Budget 2017 | March 2017 | 2017-18–2021-22 | H | Y/Y/Y | [2017, Spring](https://www.gov.uk/government/publications/benefit-expenditure-and-caseload-tables-2017) | May 2017; March 2017 EFO |
| 17 | Autumn Budget 2017 | November 2017 | 2017-18–2022-23 | H | Y/Y/Y | [2017, Autumn](https://www.gov.uk/government/publications/benefit-expenditure-and-caseload-tables-2017) | No tied edition established |
| 18 | Spring Statement 2018 | March 2018 | 2017-18–2022-23 | H | Y*/Y/Y | [2018, Spring](https://www.gov.uk/government/publications/benefit-expenditure-and-caseload-tables-2018) | May 2018; basis unverified |
| 19 | Budget 2018 | October 2018 | 2018-19–2023-24 | H | Y/Y/Y | [2018, Autumn](https://www.gov.uk/government/publications/benefit-expenditure-and-caseload-tables-2018) | No tied edition established |
| 20 | Spring Statement 2019 | March 2019 | 2018-19–2023-24 | H | Y/Y/Y | [2019, Spring](https://www.gov.uk/government/publications/benefit-expenditure-and-caseload-tables-2019) | June 2019; basis unverified |
| 21 | Budget 2020 | March 2020 | 2019-20–2024-25 | H | Y/Y/Y | [2020, Spring](https://www.gov.uk/government/publications/benefit-expenditure-and-caseload-tables-2020) | June 2020; basis unverified |
| 22 | Spending Review 2020 | November 2020 | 2019-20–2025-26 | H | Y/Y/Y | [2020, Autumn](https://www.gov.uk/government/publications/benefit-expenditure-and-caseload-tables-2020) | No tied edition established |
| 23 | Spring Budget 2021 | March 2021 | 2020-21–2025-26 | H | Y/Y/Y | [2021, Spring](https://www.gov.uk/government/publications/benefit-expenditure-and-caseload-tables-2021) | June 2021; basis check pending |
| 24 | Autumn Budget 2021 | October 2021 | 2021-22–2026-27 | H | Y/Y/Y | [2021, Autumn](https://www.gov.uk/government/publications/benefit-expenditure-and-caseload-tables-2021) | No tied edition established |
| 25 | Spring Statement 2022 | March 2022 | 2021-22–2026-27 | H | Y/Y/Y | [2022, Spring](https://www.gov.uk/government/publications/benefit-expenditure-and-caseload-tables-2022) | June 2022; basis check pending |
| 26 | Autumn Statement 2022 | November 2022 | 2022-23–2027-28 | H | Y/Y/Y | [2022, Autumn](https://www.gov.uk/government/publications/benefit-expenditure-and-caseload-tables-2022) | No tied edition established |
| 27 | Spring Budget 2023 | March 2023 | 2022-23–2027-28 | H | Y/Y/Y | [2023, Spring](https://www.gov.uk/government/publications/benefit-expenditure-and-caseload-tables-2023) | June 2023; March 2023 EFO |
| 28 | Autumn Statement 2023 | November 2023 | 2023-24–2028-29 | H | Y/Y/Y | [2023, Autumn](https://www.gov.uk/government/publications/benefit-expenditure-and-caseload-tables-2023) | No tied edition established |
| 29 | Spring Budget 2024 | March 2024 | 2023-24–2028-29 | H | Y/Y/Y | [2024, Spring](https://www.gov.uk/government/publications/benefit-expenditure-and-caseload-tables-2024) | June 2024; March 2024 EFO |
| 30 | Autumn Budget 2024 | October 2024 | 2024-25–2029-30 | H+R | Y/Y/Y | [2024, Autumn](https://www.gov.uk/government/publications/benefit-expenditure-and-caseload-tables-2024) | No tied edition established |
| 31 | Spring Statement 2025 | March 2025 | 2024-25–2029-30 | H+W+RR | Y/Y/Y | [2025, Spring](https://www.gov.uk/government/publications/benefit-expenditure-and-caseload-tables-2025) | June 2025; March 2025 EFO |
| 32 | Autumn Budget 2025 | November 2025 | 2025-26–2030-31 | H+R+W | Y/Y/Y | [2025, Autumn](https://www.gov.uk/government/publications/benefit-expenditure-and-caseload-tables-2025) | No tied edition established |

The table's public EFO status comes from reviewed capture/file identities
preserved under `obr_archive_catalog`, with exact per-file links in
[archive_obr.md](research/archive_obr.md). Availability of individual capture
bytes today remains a fetch task; a capture is not a content-equivalence
certificate. Early fiscal tables combine receipts and expenditure; later
releases split those families. A March 2017 expenditure workbook sample was
already staged by the earlier lane and checked for programme-level welfare
tables in this continuation; its sheet/cell receipt is
[obr_2017_expenditure_check.json](evidence/obr_2017_expenditure_check.json).
Original-launch equivalence is unresolved for
the revised/re-uploaded 2011–2015 files and the updated March 2018 economy
file. Recovery of March 2011 fiscal tables and December 2013 economy tables
is particularly uncertain.

## HMRC and DWP vintages: availability is not an as-at guarantee

All 16 DWP publication pages covering 2010–2025 were fetched again as
public JSON. They list corresponding Spring/Autumn forecast editions for
all 32 events. DWP says the 2010 forecasts are consistent with the relevant
EFO; the 2025 page identifies November 2025 EFO consistency. These provide
programme spending/caseload leads absent from the harvest, not ready,
validated target files. Early migrated page timestamps do not establish
original release dates. See [DWP 2010](https://www.gov.uk/government/publications/benefit-expenditure-and-caseload-tables-2010)
and [DWP 2025](https://www.gov.uk/government/publications/benefit-expenditure-and-caseload-tables-2025).

DWP files can change while retaining the event label. The 2025 page records
a 22 October 2025 correction to Spring 2025 incapacity caseloads and a
5 January 2026 update to Autumn 2025 attachments. Spring 2024 tables also
acquired additional UC detail after initial publication. Therefore retain
the file hash, original publication date, revision date, forecast vintage
and exact costing-year basis separately. Whether every original first-release
DWP file survives in archives is **unknown**; corrected public editions can
be useful but need a clearly named revision convention. The refreshed
change-history evidence is in `dwp_public_metadata`.

HMRC's ITL publications are often tied to a Spring EFO and project only
three tax years after the SPI outturn. They can supply taxpayer counts and
distributional controls missing from HOFD, but cannot cover every six-year
costing horizon. The checked June 2023 commentary explicitly uses March
2023 assumptions and projects from 2019-20 SPI because of pandemic concerns;
the June 2025 commentary uses March 2025 assumptions and 2022-23 SPI.
These are later auxiliary publications and may contain information not
available at the event. They must not silently become event-day observations.
See [HMRC June 2023 commentary](https://www.gov.uk/government/statistics/income-tax-liabilities-statistics-tax-year-2020-to-2021-to-tax-year-2023-to-2024/bulletin-commentary)
and [HMRC June 2025 commentary](https://www.gov.uk/government/statistics/income-tax-liabilities-statistics-tax-year-2022-to-2023-to-tax-year-2025-to-2026/bulletin-commentary).
The older January/April 2013 and May 2017 PDFs were re-read with `pdftotext`;
their forecast-basis receipts are in
[hmrc_itl_pdf_checks.json](evidence/hmrc_itl_pdf_checks.json), and their public
file links remain in [archive_govuk.md, section 5.1](research/archive_govuk.md).
Unverified
attributions stay labelled in the matrix.

The HMRC ready-reckoner page currently contains June 2025 and explicitly
links old editions to The National Archives. Some removed attachment URLs
were found to return 410 in the earlier audit; page change histories alone
do not recover their numeric tables. Existing archive leads include a
November 2016 table PDF, April 2019 ODS/PDF, and old-site 2010–2014 table
snapshots whose event alignment needs inspection. Do not assume an autumn
ITL distribution exists because a tax ready reckoner does. See
[HMRC ready-reckoner page](https://www.gov.uk/government/statistics/direct-effects-of-illustrative-tax-changes)
and [the explicit per-edition leads and unknowns](research/archive_govuk.md).

## Fetch policy and remaining work

Permitted sources are public GOV.UK pages/Content API and assets, public
Wayback CDX indexes and archived original bytes, and UKGWA pages/files when
they are openly served. These can be pinned without circumventing access
controls. Wayback capture metadata and already-staged samples provide
concrete fetch leads for most EFO detail; they are not promises of stable
availability. Fresh network probes are saved in
[archive_spotchecks.json](evidence/archive_spotchecks.json). UKGWA returned
a verification/WAF response in the earlier audit; its file holdings remain
unknown here. A failed fresh probe does not show an archive is empty.
No challenge-solving, proxy rotation, credential borrowing or contact with
publishers was attempted.

The next target-ingestion lane should produce an event×year×series registry
with source release/file hashes and release dates, followed by these gates:

1. Extract each event's own forecast rows; retain original/revised editions
   separately and distinguish publisher projections from outturns.
2. Reconcile receipts against modeled liabilities, GB/UK coverage and
   fiscal-year against calendar-year periods. HOFD property transaction tax
   totals do not by themselves allocate SDLT/LBTT/LTT. NICs and the planned
   Health and Social Care Levy are separate sheets at October 2021/March
   2022; map the two policy concepts explicitly rather than changing the
   baseline silently. Their values are retained in the HOFD receipt.
3. Declare which policy world the population targets describe. Detailed
   expenditure sheets contain **post-measures** forecasts. Either calibrate
   that released-policy world once and evaluate pre-measures on the same
   records/weights, or document a defensible pre-measures target bridge.
   Never refit each reform to the OBR costing being compared. Survey-derived
   tax/benefit quantities remain prohibited targets under
   [the repository's architecture contract](../ARCHITECTURE.md).
4. Fill missing demographic and distributional controls using sources
   available at the event, with explicit assumptions where no forecast
   distribution exists. Aggregate earnings growth cannot identify the
   distribution around tax thresholds. Calendar-year macro horizons also
   need a reviewed FY bridge for the final scoring year.
5. Produce a pinned annual population family for the event; certify each
   artifact with build-time and scoring-time engine identities, target
   exclusions, holdouts and period bridges. The generic static-aging docs
   explicitly require projected years' own evidence, not inheritance of
   base-year certification.

Track 1's
[`RECIPE.md`](https://github.com/PolicyEngine/policyengine-scorecard/blob/b469ffc4f14b582360a90ab8c18b69b025e73731/docs/uk_replay/RECIPE.md)
and [`YEARS.md`](https://github.com/PolicyEngine/policyengine-scorecard/blob/b469ffc4f14b582360a90ab8c18b69b025e73731/docs/uk_replay/YEARS.md)
already provide the measure registry, accounting, world orientation,
artifact hashes and a supported 2023–2030 calendar-year projection window.
Reuse that execution and provenance contract after the historical
population/vintage gates are met. Until then, an older policy applied to
that artifact answers a labelled present-population sensitivity question;
it does not reconstruct its historical OBR costing environment.
