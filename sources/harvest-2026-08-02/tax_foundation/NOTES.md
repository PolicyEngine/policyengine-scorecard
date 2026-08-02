# Tax Foundation harvest notes — 2026-08-02

Source: taxfoundation.org. Model: **Tax Foundation General Equilibrium Model**
(their current name; historically "Taxes and Growth"/TAG — `source_model:
"taxes_and_growth"` used per lane convention; every publication carries the
model vintage in `publication.vintage`, taken verbatim from the table source
notes, e.g. "Tax Foundation General Equilibrium Model, February 2026").

Crawl: sitemap-driven (robots.txt disallows `/wp-json/` and on-site search;
crawl-delay 5 respected, honest UA with contact email). 25 manifest rows =
19 content pages + 3 XLSX model outputs already counted there + 3 sitemap
shards (crawl aids, doc_type `sitemap_xml`).

## Claims staged: 665 (claims_staged.jsonl), 0 unparseable cells skipped

| Reform | Publication | Claims |
|---|---|---|
| OBBBA final law (P.L. 119-21) | Details & Analysis page (Feb 2026 update) | 22 revenue + 44 distribution |
| OBBBA final law, provision detail | Revenue-Effects XLSX (conventional only) | 40 revenue |
| OBBB House-passed (May 2025) | House Details & Analysis page | 22 revenue + 40 distribution |
| OBBB House-passed, provision detail | Full-Revenue-table XLSX | 31 revenue |
| TCJA permanence (Feb 2025) | Revenue Table XLSX (conv + dyn provisions) | 46 revenue |
| TCJA permanence variants | Table 5 (HTML; Individual/Estate/Business/Combined) | 80 distribution |
| Universal tariffs 10/15/20% (Apr 2025) | per-year conv/dyn/dyn-with-retaliation | 99 revenue |
| 2025–26 Trump tariffs (July 2026 vintage) | Tariff Tracker Tables 2 (conv) + 3 (dyn) | 231 revenue |
| 2025–26 Trump tariffs distribution | Tariff Tracker Table 4 | 10 distribution |

Headline anchors (verbatim, cross-checked against page prose):
- OBBBA final: conventional −$5,168.4B 2025–2034; dynamic −$4,331.1B
  (prose: "nearly $5.2 trillion… dynamic score… $4.3 trillion").
- OBBBA final distribution bottom quintile 2034: −0.5% conventional, +0.1%
  dynamic — matches prose sentence exactly.
- TCJA permanence: conventional total −$4,506.3B; dynamic −$3,796.1B.
- House OBBB: conventional −$4,006.5B (XLSX full precision −4006.5102818).

## Conventions and encodings
- `conditions.scoring` = "conventional" | "dynamic", never mixed; tariff
  "Dynamic with Retaliation" rows = scoring:dynamic + retaliation:tit_for_tat.
- Units: revenue values kept in **billions of USD as published**
  (`proposed_unit: "usd_billion"`); distribution in **percent** points
  (`proposed_unit: "percent"`). `value_verbatim` holds the exact cell text.
  Negative revenue_change = revenue reduction (tax cut); tariff rows positive
  = revenue raised.
- Multi-year windows: `period` = window end year + `conditions.window`
  (e.g. "2025-2034"); noted per-row. Per-year rows have no window key.
- `proposed_metric`: "revenue_change" (exists in Metric enum — direct map)
  and "pct_change_after_tax_income" (NOT in enum — needs a deliberate Metric
  extension at ingest; distribution unit_concept likely SHARE over tax_units).
- Income groups: market income percentile, verbatim-normalized labels
  ("0%-20%" … "99.9%-100%", "Total"). TF defines market income = AGI +
  tax-exempt interest + non-taxable Social Security + employer payroll tax
  share + imputed corporate tax liability + fringe benefits + imputed DC
  pension contributions; unit is tax units (see table notes in saved HTML).
  TCJA-permanence Table 5 uses a 99%-100% top group; OBBBA tables split
  99%-99.9% / 99.9%-100%.

## Parse confidence + caveats
- HIGH: all staged tables are plain HTML `<table>` or XLSX; strict numeric
  parser; any non-numeric cell would be logged to parse_skips.json (none).
- Year basis: tariff tracker tables are explicitly headed "Calendar Year".
  OBBBA/TCJA revenue tables do **not** state calendar vs fiscal on-page;
  per-row note added. Do not assume FY when comparing to CBO/JCT.
- OBBBA final page quirk: deficit rows in its Table 2 still carry leftover
  "…of Senate Finance Bill…" labels though the caption/table are the enacted
  OBBBA (page retitled + updated 2026-02-25). Revenue-total rows staged are
  labeled cleanly.
- Vintage mismatch: OBBBA final page tables cite "February 2026"; its linked
  XLSX cites "January 2026" and lacks the Feb distribution update. Values of
  overlapping totals matched at spot-check, but treat XLSX provision rows as
  the Jan 2026 vintage.
- Tariff revenue tables include a "Section 232 Tariffs" subtotal row AND its
  component rows AND a "Total" row — all staged with `tariff_policy` labels;
  don't sum rows blindly (double counting).
- Tariff Table 4 (distribution): conventional/dynamic basis NOT stated in
  header or prose — staged **without** a scoring condition + per-row note.
- TCJA permanence distribution XLSX stores fractions (0.016) where the HTML
  shows 1.6%; staged from HTML percent rendering (scale verified against
  both). XLSX manifested for provenance.

## Artifacts manifested but no claims staged (and why)
- 2024/2025/2026 tax brackets pages: statutory parameters (brackets, standard
  deduction, EITC etc.), not model claims — useful as PE parameter checks.
  2026 page reflects OBBBA changes; links IRS Rev. Proc. 25-32.
- Latest Federal Income Tax Data 2024/2025 pages + XLSX: IRS SOI actuals
  (shares of AGI/taxes paid by percentile) — level-validation candidates but
  they are IRS data summaries, not TAG model output; different source slug
  would be honest ("irs_soi via tax_foundation").
- Trump tax plan 2024 page (campaign scoring, Oct 2024): superseded by 2025
  bills; tables parse fine if wanted later.
- trump_tax_cuts_2025_budget_reconciliation (Jan 2025 "options" page): revenue
  estimates live in per-option summary cards (1-row tables) whose option
  binding needs surrounding-header parsing — LOW confidence mapping, skipped.
  Cards seen: −$5,041.3B, −$4,006.5B, −$3,013.2B, +$2,080.4B, −$4,506.3B.
- OBBBA overview/FAQ page: distribution table duplicates the final-analysis
  Table 3 (identical values, Dec 2025 mod date) — not double-staged.
- obbba_avg_tax_cut_map, obbba_state_tax_impact, obbba_complexity: state-level
  average tax change tables are Datawrapper embeds (no static table in HTML);
  would need the datawrapper CSV endpoints — pointer for a follow-up pass.
- Tariff tracker Table 4 second column "Nominal Tax Change, 2026" (avg $ per
  tax unit by group: $81 … $36,044): metric not in the proposed set — pointer.
- Long-run economic effects tables (GDP/GNP/capital stock/wages/FTE jobs) on
  every analysis: out of metric scope — all preserved in saved HTML/XLSX.
- TCJA permanence XLSX has "Added Interest Costs" rows; OBBBA tables carry
  CBO-scored spending and deficit rows — excluded (not tax revenue_change).

## Gaps / follow-ups
- Datawrapper CSVs for state/district OBBBA tables (chart ids in saved HTML).
- Their "10 Percent Universal Tariff" page also exists pre-April-2025 vintage
  (universal-tariff page supersedes; older vintages not harvested).
- TF distributional XLSX for OBBBA final not published (HTML only).
- No CSV endpoints found; all downloads are wp-content XLSX uploads.
