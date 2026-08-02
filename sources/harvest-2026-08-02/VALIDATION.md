# Ingest validation — 2026-08-02 harvest

Run before committing the ingest (2026-08-02). Two layers:

1. **Artifact re-derivation.** For each source, recompute the manifested
   sha256 of sampled artifacts and re-derive staged values from the raw
   files (openpyxl for workbooks, `pdftotext -layout` for JCT PDFs, page
   HTML for PWBM). 18/18 checks passed:

| source | check | result | detail |
|---|---|---|---|
| jct | sha256 JCX-35-25.pdf | MATCH | b33299c3d829aa38 |
| jct | JCX-35-25 provision 1 FY2026 −147,679 in PDF | MATCH | pdftotext -layout |
| jct | JCX-35-25 NET TOTAL FY2025-34 −4,474,972 in PDF | MATCH | NET TOTAL row |
| cbo | sha256 51312-2026-02-snap.xlsx | MATCH | ec1df943e22143f6 |
| cbo | SNAP FY2026 outlays SNAP_02-2026!D15 (millions) | MATCH | 100,053 → $100.053B |
| cbo | sha256 51313-2026-02-ssi.xlsx | MATCH | 58f8a598935099f3 |
| cbo | SSI FBR 2026 SSI_02-2026!D36 | MATCH | 994.0 |
| cpsp | sha256 CPSP-monthly-poverty-dataset.xlsx | MATCH | d92cba80cef44a4d |
| cpsp | monthly SPM 2024-01 all-persons 0.182 | MATCH | sheet "Primary" |
| budget_lab | sha256 TBL_Data_Reconcilation_Distribution_202506.xlsx | MATCH | 7130cda0f3337cf0 |
| budget_lab | staged publication sha256 == manifest sha256 | MATCH | 7130cda0f3337cf0 |
| budget_lab | F1 Medicaid Q1 fraction at F1!B8 | MATCH | −0.0153846030793173 |
| tax_foundation | sha256 obbba_house_full_revenue_table.xlsx | MATCH | 26f4c8b2583e0ee4 |
| tax_foundation | House conv total 2025-34 at Sheet1!L37 | MATCH | −4006.5102818049845 |
| pwbm | sha256 signed-reconciliation-bill page HTML | MATCH | fde4cd66753f4b7c |
| pwbm | Table 3 conv 2025 −43 and total 3,211 on page | MATCH | page HTML |
| tpc | sha256 T26-0014.xlsx | MATCH | ce8edcc4008102b8 |
| tpc | T26-0014 FY2026 staged values in workbook (7 rows) | MATCH | all found |

2. **COLLATION headliner cross-checks** (asserted in
   tests/test_harvest_ingest.py): JCX-35-25 NET TOTAL −$4,474,972M;
   JCX-26-25R −$3,798,248M; TF OBBBA conv −$5,168.4B / dyn −$4,331.1B;
   TF SALT-cap provision +$1,020.43B / +$782.68B; PWBM signed
   primary-deficit +$3,211B conv / +$3,631B dyn; TPC Family First lowest
   quintile +1.1% (unrounded 1.05); CPSP 2024-01 SPM 18.2%.

## Findings that changed the ingest

- **TPC T26-0010 page/file mismatch.** The taxpolicycenter.org page
  titles T26-0010 "Options to Expand the Child Tax Credit"; the workbook
  it serves (sha256 b465e716…, matching the manifest) is internally
  "T26-0010 — Trump Administration Tariffs Announced From January 20,
  2025 Through April 02, 2026, Baseline: Current Law with Pre-2025
  Tariffs". The adapter keys the table off the workbook. External-issue
  diagnosis seed for TPC.
- **TPC T26-0112/0113 baselines are stated in the workbooks** ("Current
  Law With Pre-2025 Tariffs") even though the pages don't state them;
  the staged "assumed, not stated" hints were upgraded to the
  file-internal baseline.
- **TPC T26-0009 staging defective** (verified against the workbook):
  it is the OBBBA-by-racial/ethnic-group five-sheet set; staging
  collapsed the race axis and mixed dollar columns into percent rows.
  Its 48 rows were excluded from the first ingest
  (`ingest_tpc.EXCLUDED_TABLES`) and later replaced by a per-sheet
  re-parse — see the addendum below.
- **Same-statistic republication twins** (TF page vs XLSX; TPC
  distribution vs cut/increase tables; BL Table 1 vs Table 3): merged
  with rounding-consistency assertions, twin provenance kept under
  `publication["also_published"]` (68 merges total).
- **BL Table 2b scope**: its rows decompose the Finance title; its
  "Total" (−$3,296B) is the Title VII total, not the whole-bill total
  (−$3,062B). Components are scoped "Title VII. Finance / …".
- **CBO 61367 vintage**: the SNAP cost-estimate rows ($213 reform /
  $227 baseline, 2034) describe the January-2025 baseline and carry
  `data_vintage=january_2025_baseline`, keeping them distinct from the
  Feb-2026 workbook's 2034 row ($219.86).
- **CPSP erratum**: the 2024 historical brief's key findings say 16.6%
  where body Figure 3 and the arithmetic give 11.4%; 11.4 staged, and
  the claim is pre-seeded as an `external_issue` diagnosis.
- **calibration_relationship review**: CBO's 317 consumed_as_target
  rows honored as staged (pre-verified against
  policyengine-us/parameters/calibration/gov/cbo/). CPSP annual SPM ≈
  Census reviewed: policyengine-us calibration consumes Census only for
  population totals (calibration/gov/census/populations/), no SPM or
  poverty targets — held_out stands.

## Addendum — T26-0009 per-sheet re-parse (2026-08-02)

The 48 defective rows were replaced by
`tpc/reparse_t26_0009.py` (coordinate-pinned: title block, header
anchors, row labels, and the baseline panel's position are asserted
verbatim on every sheet before any value is read). 135 rows staged:
5 sheets (All Tax Units + White/Black non-Hispanic, Hispanic, Additional
Races as `conditions.subgroup`) x 9 income groups x 3 metrics
(share_with_tax_cut C / pct_change_after_tax_income K /
avg_tax_change_usd O, tax-change panel rows 15-25 only). Checks run
before commit:

| check | result | detail |
|---|---|---|
| sha256 T26-0009.xlsx == manifest | MATCH | 2ff5369423befd72 |
| staged rows re-verified against the workbook cell each publication names | 135/135 MATCH | reparse_t26_0009.verify |
| coverage is the full sheet x group x metric cross-product | MATCH | 5 x 9 x 3 |
| hand-transcribed spot values (raw openpyxl dump, independent of the parser) | 18/18 MATCH | e.g. All!K20 2.8, White!O19 −12710, Black!C15 57.3, Hispanic!K25 4.0, Additional Races!O25 −26820 |
| baseline-panel dollar cells absent from staged values | MATCH | 1020 / 50060 / 19900 / 20910 not staged |
| percent-unit rows on the percent scale | MATCH | all in [−10, 100]; dollar rows integer-valued |

Ingest: rows ride `obbba_enacted_title_vii` against
`ReformRef.baseline = {"policy": "pre_obbba_law"}` (the workbook's
stated "Law Prior to the 2025 Budget Reconciliation Act"), keyed
separately from the current-law-baseline 2025 scorings of the same text
(T25-0229/0236, JCX-35-25). TPC claims 922 → 1,057; harvest total
12,266 → 12,401. Spot values are asserted in
tests/test_harvest_ingest.py (TestTPC.test_t26_0009_*).
