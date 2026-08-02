# Budget Lab (Yale) harvest notes — 2026-08-02

Harvester: Claude (harvest-budgetlab agent), UA
`PolicyEngine-Scorecard-Harvester/0.1 (+https://policyengine.org; contact max@maxghenis.com)`,
~1s between requests. Crawl window ≈ 00:38–00:54 EDT (~16 min).

## Coverage

- Index: crawled all 12 pages of https://budgetlab.yale.edu/our-work
  (`downloads/_index_ourwork_p*.html`) → `listing.json` (165 publications,
  2024–2026, with topic/type/date/updated metadata).
  Note: card links use single-quoted hrefs — grep with `'` not `"`.
- Scope filter: 2025–2026, topics Taxes / Budget Reconciliation /
  Children & Families. Pure-tariff pieces skipped per mission (Trade topic =
  47 pubs, untouched). "State of the Economy" (macro) and AI-scenario pieces
  skipped.
- 22 report pages fetched (`downloads/page__*.html`), 13 XLSX data workbooks
  (`downloads/TBL_Data_*.xlsx`). All in `manifest.jsonl` (35 rows, sha256).
- Budget Lab reliably ships a "TBL Data" XLSX per analysis — the single best
  structured-data source of the six harvest targets. Sheets carry full
  title/subtitle/notes/source lines (good provenance), but layouts vary
  (blank filler rows/columns, multi-panel sheets, per-sheet unit scaling).

## Staged claims: 1,247 rows (`claims_staged.jsonl`, via `stage_claims.py`)

- 644 revenue_change (usd_billions), 603 pct_change_after_tax_income (percent).
- `pct_change_after_tax_income` is NOT in scorecard_db models.py Metric enum —
  staged as proposed_metric per README (mission vocabulary).
- Verbatim policy: `value_raw` = untouched cell; `value` applies only the
  normalization named in `normalization`. **Unit scaling varies by workbook**:
  most distributional sheets store fractions (−0.0248 = −2.48%) but the June
  2025 House-vs-Senate provision workbook stores percent already (0.717 =
  0.717%). Cross-checked TCJA-extension Q1 across both to confirm.
- Windows: rows for multi-year windows carry period = window start,
  `period_window` (also mirrored into conditions so claim_id stays unique),
  plus time_note. Sign conventions per table in `sign_convention`.
- parse_confidence: high 861 / medium 386 (medium = year-not-on-sheet
  inferences flagged in period_note, or provision-level figure sheets).

By publication:
1. **Distributional Effects of Selected Provisions, House & Senate bills**
   (2025-06-30) — 108 rows. Avg annual % change in after-tax-AND-transfer
   income 2026–2034 by quintile/top slices × {Medicaid, SNAP, Taxes, Net} ×
   {House-passed, Senate+Scott, Senate}. The transfer-side jewel.
2. **Tax Provisions: Combined Distributional Impacts** (2025-06-30) — 99 rows.
   % change after-tax income 2026 by group × {TCJA extension, House total/
   on-top/individual-on-top, Senate same}; plus 2026-vs-2030 table.
3. **OBBBA + Tariffs, Dec 2025 update** (pub 2025-08-12, upd 2025-12) — 10
   rows: OBBBA-only (via CBO) column by decile, 2026–2034 avg. Tariff and
   combined columns deliberately NOT staged (tariffs out of scope); $-per-
   household sheet (F2) not staged (metric not in vocabulary).
4. **Financial Cost of the Senate-Passed Budget Bill** (rev 2025-07-17) — 108
   rows: full-bill budget effects (Senate/House × as-written/permanent ×
   FY25-34/35-44/45-55), by Senate committee title, and Finance-title split
   (Individual/Business/International/Medicaid). Concept = revenues+outlays
   excl. interest (concept_note on each row); interest columns not staged.
5. **Options for Expanding the CTC** (2025-04-09, for Third Way) — 430 rows:
   16 CTC scenarios × FY2026–2035 annual + budget-window totals, under
   current-law (T2/T3) and full-TCJA-extension (T4/T5) baselines; window
   totals both Relative-to-Current-Law and Relative-to-Option-1.
   Share-of-GDP window columns not staged (unit outside vocabulary).
6. **Booker Keep Your Pay Act / Van Hollen Working Americans' Tax Cut Act**
   (both 2026-03-12) — 95 + 87 rows: revenue by provision × FY2026–2035(+),
   plus contribution-to-%-change-in-after-tax-income by quintile (and by age
   group for Van Hollen). Distribution year inferred 2026 (period_note).
7. **Standalone Distributional Effects of Major Tax Provisions (House vs
   Senate)** (2025-06-20, rev1) — 279 rows: per-provision % change in
   after-tax income 2026 by quintile/top: TCJA extension, SALT, CTC, standard
   deduction, senior deduction, estate, overtime, tips, QBI, AMT, brackets,
   itemized, CDCTC, charitable floor, cost recovery, car-loan interest.
   Excellent for provision-level PE validation. $-average rows not staged.
8. **Indexing Capital Gains to Inflation** (2026-03-06) — 46 rows: revenue by
   year + windows ("Budget Window"/"Second Decade"/"Third Decade" kept
   verbatim as period_window), % change ATI by quintile, prospective vs
   retrospective.

## Deliberately not staged (all downloaded + manifested)

- **House Budget Resolution illustrative distribution (2025-03-19)**: the
  workbook's "Percent Change" panel headers are WRONG — values match a
  shifted column order (labels say Ind/Estate/Business/Tax/SNAP/Medicaid/…
  but values line up with SNAP at "Tax", Medicaid at "SNAP", tax total at
  "Medicaid"; e.g. bottom quintile "Tax" −1.42% ≈ −$315 SNAP / ~$22k). Sheet
  notes admit "Contains intermediate calculations". Dollar panel is
  internally consistent but $-metrics are outside the vocabulary. The
  page HTML table may have correct labels — follow-up for ingestion if
  wanted.
- **Long-term Impacts of OBBBA (enacted)** workbook: macro (GDP, debt,
  deficit % of GDP by decade) — no vocabulary fit. Downloaded for reference.
- **Distribution of Tax Cuts in the New Tax Law** workbook: share of tax
  units by tax-cut size bucket (overall + by quintile) — no vocabulary fit.
- **Gas Tax Holiday (2026-06-12)**: savings as share of BEFORE-tax income by
  quintile × pass-through scenario — denominator is before-tax income, so
  not pct_change_after_tax_income; skipped rather than mislabeled.
- Booker/CVH auxiliary figures (EMTR curves, filing-time burden, ETR IQR,
  household examples) — no vocabulary fit.
- Two literal "-" cells (self-referential baselines in CTC T2/T4) skipped.

## Poverty metrics: none

Budget Lab's 2025–2026 tax/transfer output measures distribution as % change
in after-tax(-and-transfer) income, not SPM/OPM poverty. The CTC pages cite
external poverty literature but publish no own poverty-rate estimates.
poverty_rate / poverty_rate_change: 0 rows, honestly.

## Gaps / follow-ups

- Pages fetched but with tables only in HTML/PDF (no XLSX), not yet parsed:
  AGI surtax (2025-05-05), top marginal rate options (2025-04-22), carried
  interest (2026-05-04), IRS funding (2025-03-13 + 2026-04), home-sales
  capital gains (2025-07-22), housing capgains score (2026-07-23),
  TCJA-parents, beneficiaries-year-to-year, CTC-full-refundability,
  May 2025 preliminary scores. HTML saved; parseable in an ingestion pass.
- Budget Lab GitHub (`Budget-Lab-Yale/Tax-Simulator`, `Safety-Net`,
  `Household-Tariff-Distribution`) has model code + analysis scripts linked
  from reports — deeper provenance if ever needed.
- `/research` path 500s; `/our-work` (paginated) is the working index.
- Not harvested: 2024 pubs (pre-window), tariff/trade series, macro series.
