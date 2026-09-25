# uk_ukmod_jrf — coverage, quirks, parse confidence (2026-08-02)

Two targets in one lane: **UKMOD** (ISER/Essex tax-benefit microsimulation, CeMPA
working papers) and **JRF** (Joseph Rowntree Foundation). 1,782 staged claims
(ukmod 1,392 / jrf 390), 5 manifested artifacts, zero bot-mitigation bypasses.

## Robots compliance
- iser.essex.ac.uk: `User-agent: *` allow-all. ukmod.iser.essex.ac.uk: no robots.txt.
- jrf.org.uk: `Crawl-delay: 20` honored — jrf.org.uk requests spaced >20s (3 total:
  robots, landing page, MIS PDF). The data workbook is served from
  jrf-jrht-brand.frontify.com (their brand-asset CDN; the landing page's own
  download link). Honest UA with contact email on every request.
- microsimulation.ac.uk: blocks only named commercial crawlers; not needed beyond search.

## UKMOD side (source "ukmod")

### CeMPA WP 8/26 — UKMOD Country Report 2023-2030 (van de Ven & Popova, Apr 2026)
UKMOD B2026.01, FRS 2023/24 input (HBAI-adjusted weights/incomes), forecasts from 2025.
Staged the full Section-4 validation block — **another microsimulation's published
self-validation, simulated and official columns side by side**:
- **Table 4.5** caseloads (thousands): 38 rows × (8 UKMOD policy years 2023-2030 +
  8 official-estimate years). Benefits → metric `caseload`; income tax/NIC payers →
  proposed `taxpayer_count`. Caseload unit per table note: families except
  (c) children, (h) households, (i) individuals; NIC/tax rows are people.
- **Table 4.6** expenditure/revenue (£m): 38 rows. Benefits → `benefit_cost`
  (proposed_unit gbp); taxes/NIC → proposed `tax_revenue`.
- **Table 4.7** income distribution (BHC, modified-OECD, individual unit): Gini,
  mean/median £/month, quintile medians and shares × {UKMOD 2023-2030, Input Data
  2023, HBAI 2023}.
- **Table 4.8** poverty rates below 50/60/70% median **BHC** (NB: UKMOD's validation
  poverty is BHC; JRF headline is AHC — never cross-compare without the flag) for
  all/children/over-SPA/men/women × same 10 series.
- `conditions.series` = `ukmod_simulated` | `official_estimate` | `input_data` | `hbai`.
  Official-estimate cells are SECOND-HAND transcriptions of DWP/HMRC/SSS/OBR/SFC
  numbers as cited by UKMOD (full citation string on each row +
  `official_sources_note`); first-hand twins arrive via the dwp/hmrc/obr lanes —
  dedup at ingest, and the (UKMOD-cited vs first-hand) delta is itself diagnosis
  material.
- Parse method: anchor on UKMOD variable names (bch_s, tin12_s, …) in the
  pdftotext -layout text; scoped label anchors for income-tax band sub-rows;
  10 hard-coded spot-check cells asserted on every run (`stage_claims.py`).
- **PDF quirks (verbatim in source):** continuation-page year headers on Tables
  4.5/4.6 print "… 2029 2029" where page 1 prints "… 2029 2030" — columns mapped
  positionally per the page-1 header. Table 4.6's source line is garbled
  ("Source: UKMOD and , and Scottish Government statistics…"). WFA 2024 collapse
  (12,057k → 1,583k simulated; 11,626k → 1,268k official) is the real
  winter-fuel-payment restriction, not a parse error.
- Report's own health warnings (§4.3, worth quoting at diagnosis time): take-up
  probabilities other than Scotland/pension-age **not updated since 2021**; IS
  over-simulated / ESA under-simulated (limited-capability-for-work imputation);
  child poverty understates HBAI (take-up assumptions); tax credits understate
  admin data (prior-year income + finalised awards); UKMOD policy year = Apr-Mar
  fiscal year (report §2, "financial year … April to March") → period = start
  year, conditions.fy = "YYYY/YY".
- NOT staged (available in the PDF for a second pass): Annex 6.6 FRS-only twins
  of all four tables (Tables 6.10-6.15) — useful for input-data-sensitivity
  diagnosis; Table 4.2 earnings by subgroup; COVID-era shock tables.

### CeMPA WP 3/26 — Autumn Budget policy assessment (Frimpong, Feb 2026)
UKMOD static scoring of the Autumn Budget package (income tax threshold freezes,
UC two-child limit removal, WFA restrictions, Pension Credit reductions);
reform_hint verbatim on every row. Staged: Table 1 (UK fiscal overview 2026-2030:
revenue/expenditure levels baseline+reform, revenue_change, expenditure_change,
net_fiscal_impact), Table 1.2 (by nation + per-capita), Table 2 (fixed-line AHC
poverty counts baseline/reform/change by group, 2026+2030), Table 2.1 (poverty
count change by nation, all years), Table 2.4 (child poverty rate baseline→reform
by nation + count change), Tables 3a/3b (Gini + S80/S20, AHC and BHC,
baseline/reform/change). Every transcribed raw string machine-verified to appear
in the extracted text. NOT staged: Tables 4/4.1 (income shares by decile),
5/5.1 (mean income by decile), gainers/losers §8 — in the PDF, second pass.
- **Title-year quirk:** WP title says "Autumn Budget Statement 2026", inner cover
  says "…2025". Measures match the Nov-2025 Autumn Budget (two-child limit
  removal etc.) analyzed over 2026-2030. Kept the WP title verbatim in
  publication; flagged here.
- Baseline is UKMOD's pre-Budget system; `conditions.scenario` =
  baseline | reform | reform_minus_baseline. No executable reform dict staged —
  ingest should build the PE-UK parametric reform from the hint.

## JRF side (source "jrf")

### UK Poverty 2026 data workbook (published 2026-01-27)
81-sheet xlsx behind the landing page's download button — fully machine-readable,
many series **unrounded** (e.g. OG1 poverty rates to 15 decimals). Underlying data
per sheet's own Source row — mostly **HBAI 2023/24 (DWP)**; DDT1 is Understanding
Society. JRF headline measure = relative poverty, **below 60% median AHC**
(deep = 50%, very deep = 40%; persistent = AHC relative poverty in 3+ of last 4
years — definitions sheet A1T2).
Staged: OT1 (headline counts+rates, 12 groups, 2023/24), GT1 (14 nations/regions,
3-year average 2021-2024 per table title), DDT1 (persistent poverty + persistent
very deep poverty, 17 groups, 2022-23), OG1 (headline AHC rate time series
1994/95-2023/24 × 5 groups, 150 obs, unrounded; UK from 2002/03, GB before),
FAST2 (child poverty by family size/parents/age, 13 subgroups), A1T1 (poverty/
deep/very-deep thresholds + median by 5 family types, weekly unrounded + annual
rounded; income concept not stated on-sheet — flagged in conditions).
- Rate cells mix fractions (0.21) and percents (21) across sheets — deterministic
  rule value>1 ⇒ /100, normalization recorded per row.
- `calibration_relationship` left `held_out` BUT: these are HBAI-derived numbers.
  Whether policyengine-uk consumes HBAI poverty stats as calibration targets was
  NOT verified this session — audit against policyengine-uk calibration configs
  at ingest before any "held-out validation" claim.
- NOT staged (clean, high-value second pass): EXG2/DDG1 poverty-depth composition
  time series; GM2 child poverty by Westminster constituency (local-area
  validation surface); SSG2/SST1 poverty by benefit receipt; HOT1/HOG1 by tenure;
  WG1-4 work status; EG1-3 ethnicity; A3G1 median income BHC/AHC series.

### Minimum Income Standard 2025 (JRF / CRSP Loughborough)
Table 2 weekly budgets, April 2025, 4 household types × 16 components + 6 totals
(incl. AHC-comparable and BHC-comparable totals) = 88 cells, all verified against
extracted text. proposed_metric `minimum_income_standard_budget`. MIS is a
consensus budget standard, NOT HBAI-derived — noted in publication.vintage.
- **Erratum seed:** 2024 MIS working-age couple budgets omitted one mobile phone
  (~£3/wk); corrected in 2025 (report note). Any 2024-vintage MIS comparison
  should expect this.

## Schema / ingest worklist for this lane
- proposed_unit **gbp** (+ gbp_per_week/_year/_month/_person) everywhere monetary —
  UnitConcept has USD only. value_kind used: count | share | **currency_gbp**
  (extension needed).
- proposed_metric recurring: tax_revenue, taxpayer_count, poverty_count,
  government_revenue/expenditure, expenditure_change, net_fiscal_impact(_per_capita),
  gini_coefficient(_change), s80_s20_ratio(_change), income_share,
  mean/median_equivalised_disposable_income, median_income, poverty_threshold,
  persistent_poverty_rate, minimum_income_standard_budget.
- Load-bearing conditions on every distribution row: income_concept (BHC for
  UKMOD validation; AHC for JRF headline + CeMPA fixed-poverty; both in 3a/3b),
  equivalisation, series, scenario, fy (Apr-Mar).
- Period: UK fiscal year start-year int + conditions.fy label; GT1 carries a
  3-year window condition; DDT1 a 4-wave window.

## Blockers / follow-ups
- None hard. ISER fully open (no Cloudflare); JRF fine at 20s spacing; frontify
  CDN unrestricted.
- ukmod.iser.essex.ac.uk itself (the model's own site) not needed for tables this
  round — country report carries the validation block. If a "UKMOD statistics
  release" page exists separately, it wasn't needed; CeMPA WP index at
  iser.essex.ac.uk is the canonical feed (cempa2-25 = prior-year country report
  2022-2029, available for vintage-drift analysis).
- Second-pass queue above (annex FRS twins; deciles/gainers tables; ~10 more JRF
  sheets incl. constituency map data).
