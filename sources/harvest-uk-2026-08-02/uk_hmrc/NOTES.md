# uk_hmrc harvest notes — 2026-08-02

**2,842 staged claims** from 11 manifested artifacts (10 ODS + 1 bulletin HTML), all
sha256'd, verbatim values only, per-row provenance (workbook/sheet/row_index),
zero bot-mitigation bypasses. gov.uk is fully curl-friendly with honest UA
(`PolicyEngine-Scorecard-Harvest/1.0 (research data collection; contact
max@maxghenis.com)`); discovery via the gov.uk content API
(`/api/content/government/statistics/<slug>`) and search API — no scraping needed.
All ODS parsed with `ods_rows.py` (pure-stdlib parser, handles repeated
cols/rows); staging scripts `stage_{rr,itl,cb,tc,cgt,spi}.py` are re-runnable.

## Claims by source file
| file | claims | what |
|---|---|---|
| claims_rr.jsonl | 225 | Ready reckoner: 73 illustrative changes x FY2026-27/27-28/28-29 (8 suppressed "Neg") |
| claims_itl.jsonl | 1,151 | Income Tax liabilities July 2026 edn: 2.1 (UK by band/sex/age 2010-11+), 2.2 (13 countries/regions x band, 2023-24..2026-27), 2.5 (liability x income range x band, 4 years) |
| claims_cb.jsonl | 515 | Child Benefit Aug 2025: families/children in receipt by geo 2013+, take-up rate (Table 15), HICBC (Table 16), opt-outs (Table 9) |
| claims_tc.jsonl | 453 | Tax credits finalised awards 2022-23 (FINAL edition): caseloads by family type 2018-19+, entitlement GBP, award-band distribution |
| claims_cgt.jsonl | 138 | CGT Aug 2025: annual taxpayers/gains/tax 2008-09..2023-24 + 2023-24 by country/region |
| claims_spi.jsonl | 360 | SPI 2023-24: income percentile points before/after tax (3.1 named pctiles 2015-16+; 3.1a full 1-99 for 2023-24) |

## UK-FLEET conventions applied
- `proposed_unit: "gbp"` on every money row; conversions per-row in `unit_note`
  (GBP millions x 1e6, thousands x 1e3; verbatim printed string kept in `value_raw`).
- `time_basis: fiscal_year` + `conditions.fy` ("2026-27") for Apr–Mar years;
  Child Benefit August/May snapshots are `point_in_time` + `conditions.as_of`.
- `conditions.basis`: outturn | projected | provisional, from each table's own
  markers (see per-source gotchas). Geography labels verbatim; ONS area codes
  carried as `conditions.area_code` where printed.
- proposed metrics (recur across sheets, several match the CBO harvest):
  `taxpayer_count` (909), `tax_liability` (214), `income_aggregate` (48),
  `income_percentile_point` (360), `average_tax_rate` (48, staged as ODS
  fraction, e.g. 0.015 for printed "1.5%"), `average_tax_amount` (48),
  `chargeable_gains` (46). In-vocab: revenue_change, caseload,
  participant_count, participation_rate, benefit_cost.

## Per-source notes and gotchas

### Ready reckoner (the reform-score surface)
- June 2025 edition (published 2025-06-24) is the LIVE latest; covers
  FY2026-27..2028-29. No 2026 edition existed on the live page at harvest time.
- Sign semantics are LOAD-BEARING (staged per row as
  `conditions.direction_semantics` + `sign_convention`): rows suffixed
  "(cost)" report a positive number as a cost, "(yield)" as a yield; bulletin
  note 33: "negative values for costs indicate net yield and negative values
  for yields are a net costs". CGT/SDLT-additional-dwellings rows go NEGATIVE
  (behavioural loss from a rate rise) — HMRC's estimates INCLUDE behavioural
  response, so static PE-UK scores will legitimately diverge on
  additional-rate, CGT and SDLT rows (diagnosis material, not error).
- "Neg" = "larger than zero but would round down to zero" (verbatim sheet
  note) — 8 cells staged as status=suppressed with value_raw="Neg".
- Non-linearity warning (bulletin): allowance/limit changes don't scale
  linearly; 1p rate changes roughly do.

### Income Tax liabilities (July 2026 edition — post-cutoff fresh)
- SPI 2023-24 outturn; 2024-25..2026-27 projected per footnote 10 on "economic
  assumptions consistent with the OBR's March 2026 Economic and Fiscal
  Outlook" — carried as basis=projected.
- Scottish band-classification footnotes (8/9/11) matter for band counts:
  Scottish taxpayers are classified against UK-government limits by income,
  not Scottish marginal rate. `conditions.band` values are verbatim column
  heads (Savers/Basic/Higher/Additional rate).
- Table 2.5 "[no estimate]" cells skipped (no value printed). Numbers
  independently rounded to 3 s.f.; All-Ranges totals cross-check (36,700k
  taxpayers, GBP 274,000m liability 2023-24 ✓ = Table 2.1 / receipts scale).
- NOT staged (in the same workbook, parse-ready): 2.4 percentile shares of
  income/tax, 2.6 liability by income source.

### Child Benefit (data at August 2025)
- Internal consistency verified: 7,552,330 registered − 684,635 opted out
  = 6,867,695 in receipt (Aug 2025, UK) ✓.
- Table 15 is a genuine TAKE-UP rate (participation_rate): % of eligible
  children for whom CB is claimed INCLUDING opted-out claims — All Ages
  86.6% May 2025, series back to 2011; per-age staged for May 2025 only.
- Table 16 HICBC: exact-GBP fiscal-year series; 2024-25 row provisional +
  rounded to nearest 10k/GBP 10m (note 6) — basis=provisional.
- Charge-threshold regime note for comparisons: HICBC threshold rose to
  £60k (taper to £80k) from April 2024.

### Tax credits (finalised awards 2022-23)
- 2022-23 is the FINAL finalised-awards edition — no 2023-24 publication
  exists on gov.uk (404; program ended 5 April 2025). Historic-validation
  surface only (UC migration collapse visible: 339k out-of-work families).
- WORKBOOK STORES NUMBERS AS TEXT (no ODS office:values) incl. "1.4m"
  shorthand — parse_cell() in stage_tc.py handles both; other workbooks are
  numeric.
- Counts are annual AVERAGES of recipient families
  (`count_basis=average_number`); entitlement rows are finalised annual
  entitlement GBP. Table 2_3 bands are ANNUAL-ENTITLEMENT bands (not income).

### CGT (August 2025 edition)
- 2021-22 onwards provisional (table header, staged basis=provisional);
  2023-24 first appears here: 378k taxpayers, GBP 65,937m gains,
  GBP 12,086m tax (individuals+trusts).
- Staged from 2008-09 only: footnote 2 — taper relief pre-2008 makes gains
  non-comparable.
- Trusts detail columns and Tables 2 (size of gain), 3 (gain x income) are
  downloaded + manifested but unstaged (follow-up; Table 3's gain-x-taxable-
  income grid is the most PE-comparable of the three).

### SPI personal incomes (2023-24, March 2026 release)
- Percentile points are of the TAXPAYER income distribution (SPI covers only
  individuals above the PA threshold) — carried verbatim in
  conditions.population; do NOT compare against all-adult percentiles.
- 3.1 vs 3.1a overlap rows agree exactly (median before-tax 2023-24
  GBP 29,700 in both) — cross-check passed.
- NOT staged (manifested, parse-ready): 3.2-3.11 (age/sex/source
  distributions) and the second workbook Collated_Tables_3_12_to_3_15a_2324.ods
  (region/country/LA-level income + tax) — biggest remaining SPI value.

## Blockers / follow-ups
1. No blockers hit: no Cloudflare/DataDome anywhere on gov.uk or
   assets.publishing.service.gov.uk; every fetch was a clean 200.
2. Unstaged-but-downloaded: ITL 2.4/2.6; CGT Tables 2/3 (+ Table 4 BADR,
   6-9 not downloaded); SPI 3.2-3.11 + regional workbook; CB small-area file
   and Tables 2-8/10-14/17 detail.
3. Not fetched (deliberate, out of 30-artifact budget): ITL tables 2.7-2.11
   (separate publications), historic 2.1a/2.5a, Child Benefit August 2026
   release (not yet published; annual ~Aug), HMRC receipts monthly bulletin
   (harvest-obr/hmt overlap), UK income dynamics/NICs tables.
4. Ready reckoner June 2026 edition: watch the live page — the June 2025
   ODS is current as of today.
5. Ingest schema: same gbp UnitConcept extension as the rest of the UK fleet;
   percentile/band/fy/basis/as_of condition keys to standardize.
