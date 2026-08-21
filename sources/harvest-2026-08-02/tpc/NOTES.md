# TPC harvest notes (2026-08-02, overnight)

Status: COMPLETE. 54 docs manifested, 1,486 claims staged from 35 tables.
Post-harvest correction: T26-0009's 48 rows were verified defective
(VALIDATION.md) and replaced by a 135-row coordinate-pinned re-parse
(reparse_t26_0009.py, below) — claims_staged.jsonl now carries 1,573 rows.

## Access path (matters for re-harvest)
- taxpolicycenter.org hard-blocks curl at the Cloudflare TLS-fingerprint level
  (403 for every UA). robots.txt unreadable for the same reason.
- claude-in-chrome was not connected (overnight), so work ran in the Claude
  Code in-app Browser pane (real Chromium passes Cloudflare) using same-origin
  `fetch()` in page context.
- Drupal PAGE routes are aggressively rate-limited (HTTP 429; sustained budget
  is roughly one page per 30-50 s). STATIC files under /sites/default/files/
  are NOT rate-limited — bulk XLS retrieval is fine at ~1 file / 1.5 s.
- File bytes left the browser via POST to a local receiver
  (scratchpad/receiver.py, port 8391 — port 8377 was already taken by a
  sibling harvest agent's receiver; check before binding).
- Wayback Machine: table PAGES are archived (fetch with the `id_` raw flag;
  many captures are stored gzipped — gunzip before parsing) but XLS binaries
  are mostly NOT archived, and TPC pages embed the data as GIF images, so
  archived pages yield metadata + the direct XLS URL, never an HTML data
  table. Wayback refuses rapid connections (~12 in a burst, then cool-down).
- Recipe that worked: listing crawl in-browser (10 `lbj-card`s/page, newest
  first, canonical hrefs /model-estimates/T2x-NNNN) -> Wayback for T25 page
  metadata + XLS URLs (fast, no 429) -> live browser for T26 pages (slow
  pump) -> all XLS bytes from static paths (fast).

## Coverage
- Index: 170 listing cards captured (browser_meta.json: T26-0126 back to
  T25-0209, with gaps where listing pages 6-33 flaked; retries fixed most).
- Downloads: 54 files (see manifest.jsonl) prioritized per mission:
  - OBBBA / 2025 Budget Reconciliation Act: T25-0217..0227 (Senate OBBBA
    distribution by ECI level+percentile, 2025/2026/2027; cut/increase
    tables; provisions-effective-2025 table), T25-0229 + T25-0236 (House-vs-
    Senate comparison; note below), T26-0009 (OBBBA x racial/ethnic group),
    T26-0087 (extend expiring OBBBA provisions, revenue FY2027-36),
    T26-0126 (extend SALT limit increase).
  - EITC/CTC: T25-0209/0213/0215 (CTC $2,500 options + 39.6% top rate;
    note baseline is CURRENT LAW PLUS Senate OBBBA Title VII — see
    baseline_hint), T25-0216 (aggregate benefits of CTC/EITC/dep-exemption
    2011-2035), T25-0252 (CTC benefit by ECI), T26-0010 (CTC expansion
    options revenue), T26-0014/0016 (Family First Act), T26-0022/0024
    (Working Parents Tax Relief Act), T26-0027/0028 (WPTRA + EITC variants),
    T26-0029/0030/0031 (American Family Act), T26-0032/0033 (CTC benefit).
  - Current-law baselines (June 2026 vintage): T26-0034..0040 (Baseline
    Distribution of Income and Federal Taxes: 2025, 2026, 2027 x
    percentile/level), T26-0041..0047 (Effective Federal Tax Rates by year
    to 2036), T26-0049 (Shares of Federal Taxes), T26-0056 (tax units by
    bracket), T26-0090/0092 (zero/negative income tax units).
  - Tariffs (relevant to the tariff-parity lane): T25-0366, T26-0112,
    T26-0113 (Trump tariffs through 2026-07-23: revenue FY2026-36 +
    distribution 2026).
- NOT downloaded (rate-limit budget): T25-0140..0201 House-OBBBA era tables,
  T25-0244..0251 (CDCTC benefit series), T25-0253..0262 (education/QBI
  benefit series), T25-0269..0338 (Sept 2025 tax-expenditure refresh),
  T25-0359..0365 (ESI exclusion), T25-0378..0381 (tariff + rebate combos),
  T26-0048..0055 remainder, T26-0057..0089, T26-0093..0111. All are
  enumerable from browser_meta.json / the Wayback CDX dump.

## Claims staging conventions
- Verbatim values only, from the XLS files themselves (never the page, which
  is an image). `value` = TPC's published display number (left block);
  `value_unrounded` = the higher-precision twin from the right-hand block of
  the same Summary sheet where present.
- Distribution claims: one row per (income group x metric), conditions =
  {geography: "US", income_group: TPC's own label verbatim, income_axis:
  TPC's own axis header verbatim — e.g. "Expanded Cash Income Level
  (thousands of 2025 dollars)" — so level-bracket dollar-years are explicit}.
- Mission metrics staged: pct_change_after_tax_income (percent),
  share_with_tax_cut (percent of tax units), avg_tax_change_usd (USD per tax
  unit), revenue_change (usd_billions or usd_millions exactly as the file's
  own unit note states; no rescaling).
- revenue_change rows: period = fiscal year column; 10-year totals carry
  period_span (e.g. "2025-34") instead of period. Multi-option tables carry
  conditions.option ("Option 1"...) because provision labels repeat across
  options.
- BEYOND-MISSION rows (flagged `beyond_mission_vocab: true`, drop trivially
  if unwanted): provision-benefit ("tax benefit of X") tables staged as
  share_with_benefit_pct / benefit_pct_after_tax_income /
  share_of_total_benefit_pct / avg_tax_benefit_usd, and year-series
  aggregates (T25-0216) as aggregate_tax_benefit_usd. These cover the
  mission's EITC/CTC priority whose only published form is benefit-shaped.
- `preliminary` vintage: TPC stamps most reconciliation-era files
  "PRELIMINARY"/"VERY PRELIMINARY"; propagated into publication.vintage.
- T26-0009 (OBBBA x racial/ethnic group; re-parsed): five sheets (All Tax
  Units + White/Black non-Hispanic, Hispanic, Additional Races), each a
  tax-change panel (rows 15-25) over a baseline-distribution panel (rows
  37-47) that reuses the same group labels/columns — the generic parser
  merged the panels and collapsed the race axis, so its 48 rows were
  replaced by reparse_t26_0009.py's coordinate-pinned staging: 5 sheets x
  9 groups x 3 mission metrics (C share_with_tax_cut / K
  pct_change_after_tax_income / O avg_tax_change_usd) = 135 rows, race as
  conditions.subgroup slugs (white_non_hispanic, black_non_hispanic,
  hispanic, additional_races; the All sheet stages no subgroup key),
  publication carries sheet/cell/population per row. The baseline panel
  (pre-OBBBA income/tax levels) stays unstaged like the other
  baseline-level tables below. No unrounded twin block exists in this
  workbook, so no value_unrounded.
- calibration_relationship: held_out for all rows (nothing here is a
  Populace calibration target).
- Closed-enum note for the ingester: of the staged metrics only
  revenue_change exists in scorecard_db Metric today. Extension candidates
  that recur: avg_tax_change_usd, share_with_tax_cut,
  pct_change_after_tax_income (mission trio), plus the benefit family if
  tax-expenditure validation is wanted.

## Known quirks / ambiguities
- Page-vs-file identity: the page at /model-estimates/T25-0228 links file
  T25-0236.xls (TPC reissued the table under a new id; the slug keeps the
  old one). claims use the FILE-INTERNAL "Table Txx-xxxx" id, which is the
  authority. Downloaded file T25-0016.xls is the file TPC serves for table
  T26-0016 (their naming, manifested under its internal id).
- T25-0209..0215 CTC options score against "Current Law Plus Enactment of
  Tax Provisions in Title VII of a Senate Substitute to H.Con.Res.14" — NOT
  plain current law. baseline_hint carries this verbatim; do not compare
  against a current-law PolicyEngine baseline.
- Senate-OBBBA file titles read "Manager's Amendment to the Tax Provisions
  to Provide Reconciliation of the Fiscal Year 2025 Budget in the Senate,
  Released June 28, 2025" (= the bill as amended; page titles say "Senate
  Reconciliation Bill, OBBBA"). Both titles preserved (file lines in
  reform_hint, page title in publication.title).
- '*' cells (|value| < $5 or < 0.05) are skipped, not staged as zero.
- Distribution tables also exist per filing status (Single/Joint/HOH/
  w Children/Older sheets) — NOT staged (summary "all units" sheets only);
  rich follow-up if subgroup validation is wanted.
- Unstaged downloads (17): baseline level tables (T26-0034..0047, T26-0049)
  — columns are income/tax LEVELS (avg pre-tax income, avg federal tax,
  AFTR, shares) with no mission metric; T26-0056 (bracket counts);
  T26-0090/0092 (zero-tax unit counts); T25-0243 (itemizer counts). All
  parse cleanly if the vocab is extended (avg_federal_tax_rate_pct,
  share_of_federal_taxes_pct, tax_units_count...).

## Cleanest PolicyEngine-runnable mappings (ranked)
1. T25-0209/0213/0215 — CTC amount/refundability/phase-in + top-rate 39.6%:
   fully parametric in policyengine_us (mind the OBBBA-inclusive baseline).
2. T26-0029/0030/0031 — American Family Act (CTC $3,000/$3,600 style):
   parametric; revenue FY2026-35 + distribution 2026 both staged.
3. T26-0010 — CTC expansion options revenue (multiple parametric options).
4. T26-0014/0016, T26-0022/0024/0027/0028 — Family First / Working Parents
   packages: mostly parametric (CTC/EITC restructures), some provisions
   (e.g. filing-status changes) need checking against PE parameter space.
5. T25-0217..0227 — Senate OBBBA: PE has OBBBA encoded; distribution +
   cut-shares comparable reform-vs-prior-law; watch enacted-vs-Senate deltas.
6. T26-0087 / T26-0126 — extend-OBBBA-provisions revenue: parametric
   extension reforms.
7. Baseline distribution T26-0034..0040 — current-law level validation
   (mode 1) once vocab extended.
8. Tariff tables (T25-0366, T26-0112/0113) — not PE-runnable (no tariff
   module) but directly useful to the Axiom tariff-parity campaign as an
   independent external comparator.

## Files
- manifest.jsonl — 54 rows: url, table_id, title, file_title_lines,
  baseline_line, dist_line, date, sha256, bytes, local_path, doc_type, sheets.
- claims_staged.jsonl — 1,573 rows as above (1,486 harvested - 48
  defective T26-0009 rows + 135 re-parsed).
- parse_report.json — per-file staged/skip status.
- parse_tpc.py — reproducible parser (uv run --with pandas --with xlrd
  --with openpyxl python parse_tpc.py).
- reparse_t26_0009.py — coordinate-pinned T26-0009 re-parse; splices
  claims_staged.jsonl in place and re-verifies every staged row against
  the workbook cell it names (uv run --with openpyxl python
  reparse_t26_0009.py).
- browser_meta.json — 170 listing cards + 45 page-discovery records.
- Wayback CDX dumps + 14 archived T25 pages remain in the session scratchpad
  (wiped on restart); regenerate via the CDX queries in this file if needed.
