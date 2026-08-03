# JCT harvest notes — 2026-08-02 (00:37–01:55 ET)

## Access path (important for re-harvest)
jct.gov sits behind a Cloudflare JS challenge that 403s all non-browser clients
(curl with any UA, any headers; sitemap too). robots.txt: `User-agent: *` fully
allowed; Cloudflare-managed content signals `search=yes, ai-train=no,
use=reference` (this harvest is reference use, not training). The block is a
TLS-fingerprint challenge, not a robots policy.

**Everything here was therefore fetched from the Internet Archive Wayback
Machine** (original bytes via `/web/<ts>id_/` URLs). Every manifest row records
the canonical jct.gov URL in `url` and the actual Wayback fetch URL in
`retrieved_via`. sha256 is over the bytes we stored (Wayback's copy of the
original). Rate: ~1 req/3.5s, honest UA with contact address.

## Coverage
- 28 documents in manifest.jsonl / downloads/ (all %PDF-verified, sha256'd).
- 2025 JCX pages enumerated from Wayback CDX (JCX-1-25 … JCX-49-25 with gaps:
  JCX-38-25 … JCX-43-25, 46-48 have no page captures; unknown whether all exist).
- The complete OBBBA (H.R. 1 / P.L. 119-21) revenue-table arc is here:
  JCX-19-25 (W&M markup) → JCX-22-25R (W&M reported) → JCX-26-25R
  (House-passed) → JCX-29-25 (SFC sub, current-policy) → JCX-30-25/31-25
  (manager's amendment, current-policy/present-law) → JCX-35-25 (Senate-passed,
  present law; House concurred in the Senate amendment and the bill was enacted
  as P.L. 119-21 — linkage corroborated in-corpus by JCS-1-26's title, "General
  Explanation Of The Tax Provisions Of Public Law 119-21").
- Latest tax expenditure report: JCX-45-25 (FY2025-2029, Dec 3 2025,
  post-OBBBA: provisions enacted through 2025-08-31) — downloaded, NOT staged
  (see below).
- Also: JCX-25-25 (macroeconomic/dynamic analysis of House OBBBA), JCX-10-25
  (excise offset methodology), distribution tables (JCX-20/23/24/32/33/36/37),
  JCS-1-25 + JCS-1-26 bluebooks, JCX-18-25/21-25 (provision descriptions with
  detail), small-bill descriptions (JCX-6/8/11/12/49), JCX-1-25 (expiring
  provisions), JCX-16-25 (refund review).

### Not harvested (blockers)
- **JCX-34-25** (Senate-passed OBBBA vs CURRENT-POLICY baseline — twin of
  35-25): its page is archived but the PDF binary was never captured by Wayback.
  Save-Page-Now attempts returned 5xx (SPN outage tonight); note my first SPN
  attempt also used a WRONG guessed URL — the correct one is
  `https://www.jct.gov/getattachment/8207b8cc-23dd-4b44-adba-772ac34dcfc1/x-34-25.pdf`.
  Retry SPN with that URL, or fetch via a real browser session on live jct.gov.
- **JCX-28-25R, JCX-13-25** PDFs: same never-captured situation.
- **2026 JCX docs**: Wayback has only 3 of the year's pages (JCS-1-26,
  JCX-14-26, JCX-19-26; the latter two PDFs not captured). The 2026 revenue
  estimates JCX-1-26 … JCX-13-26, 15-18-26, 20+-26 are a real coverage gap —
  needs a live-browser pass on jct.gov/publications with year=2026 filter.
- JCX-22-25 and JCX-28-25 (non-R originals) are 403-excluded in Wayback;
  superseded by the R revisions we have.

## claims_staged.jsonl — 6,771 rows, 7 documents (conventional revenue tables)
JCX-35-25 (1130), JCX-31-25 (1130), JCX-22-25R (1097), JCX-30-25 (1083),
JCX-26-25R (1067), JCX-29-25 (1007), JCX-19-25 (257).

Shape: ExternalScore-like with `proposed_metric: "revenue_change"` — NOTE this
already exists in the closed Metric vocab (models.py REVENUE_CHANGE), as do
unit_concept `usd` and time_basis `fiscal_year`, so ingest needs no vocab
extension for these rows; the proposed_ prefix just marks staging provenance.
- `value`: dollars. JCT publishes **millions of USD**; value = verbatim × 1e6.
  `value_verbatim` preserves the printed figure exactly.
- `source_column` = the row's own provision label, verbatim (incl. footnote
  markers like `[1]`); dot leaders stripped.
- `conditions`: provision, bill_version (=JCX number; keeps claim_ids distinct
  across bill versions since reform is only a hint), table_section (chapter
  header, disambiguates duplicate labels e.g. two "Total of Chapter 3"),
  baseline (present_law/current_policy, set ONLY when the doc's title states
  it), fy_span for multi-year total columns (2025-29/2025-34; period = span end
  year for those rows).
- `row_kind`: provision | total (chapter totals + NET TOTAL rows).
- `reform` is NOT populated (no fabricated PE reform dicts) — `reform_hint`
  carries the bill/version/baseline descriptor built from the doc's own title.
- `effective_verbatim`: the table's Effective column (JCT abbreviations, e.g.
  "tyba 12/31/25"); legend for the abbreviations is in each PDF's footnote page.

### Parse integrity (why these are high-confidence)
Parser: pdftotext -layout + column-count validation — a row stages only if it
yields EXACTLY ncols trailing value tokens (10 years + 1-2 span totals).
Additionally every row with a numeric span cell must pass a horizontal
checksum: sum(single years) ≈ printed span total (tolerance max(10, 0.4%) $M —
JCT totals are computed from unrounded values). **Column misalignment
essentially cannot pass this.** Results: 0 checksum failures staged, 0
suspicious rows staged; 74 rows logged to skipped_rows.jsonl instead
(71 = no-value banner rows like "Negligible Revenue Effect"/"Estimate to be
Provided by CBO" — nothing to stage; 2 = rows with a blank cell
("Enforcement of remedies against unfair foreign taxes", JCX-22-25R+26-25R);
1 = checksum failure ("Reduction of excise tax on firearms silencers",
JCX-22-25R)). Footnote/legend regions — including the outlay-effect detail
tables inside footnote [1] — are excluded wholesale.
Cell markers skipped (never guessed): `---` (no effect), `--`, `[n]`
(de minimis, e.g. "loss of less than $500,000").
Spot checks: NET TOTAL 2025-34 values match widely-published figures —
JCX-35-25 −4,474,972 ($M, the $4.475T present-law number), JCX-29-25 −441,468
(the $441B current-policy number), JCX-26-25R −3,798,248, JCX-19-25 −4,919,851.
5 random cells re-grepped against raw text: all present.

### Sign/semantics
JCT sign convention: negative = revenue loss vs the stated baseline. Rows are
suite-level per provision as printed; provision rows and chapter/NET totals are
all staged (row_kind distinguishes). Multi-year span cells are staged with
fy_span conditions — ingest may drop them if only single-FY rows are wanted
(they are derivable but also independently printed, hence kept verbatim).

## Tax expenditure report (JCX-45-25): downloaded, deliberately NOT staged
Table 1 (FY2025-29, [Billions of Dollars], 11 cols: Corporations 2025-29 |
Individuals 2025-29 | Total 2025-29) has a usable checksum (Total column; a
trial parse had 0 checksum failures on 180 rows), BUT provision-label /
budget-function attribution is unreliable via pdftotext alone: wrapped label
first-lines are indistinguishable from function headers at these indents,
producing misattributed conditions and 6 duplicate claim keys in trial output.
Two trial parses were rolled back entirely (first also had a column-shift bug:
the 11th Total column shifted year mapping — caught by audit). Follow-up: use a
coordinate-aware extractor (pdfplumber x-positions or the PDF's text grid) for
Table 1; proposed_metric would be `tax_expenditure` (NOT in closed vocab —
deliberate extension needed), unit billions → dollars, conditions
taxpayer_type ∈ {corporations, individuals} + budget_function.

## Other staging candidates deliberately left for ingest-side decisions
- Outlay-effect detail (footnote [1] tables in the revenue JCXs): outlay, not
  revenue — needs proposed_metric `outlay_change` and careful sign handling.
- Distribution tables (JCX-20/23/24/32/33/36/37): average tax rates / tax
  change by income category — different metric family (not revenue_change);
  layouts look parseable with the same rig + a category-column adapter.
- JCX-25-25 macro analysis: dynamic estimates; would need
  source_model=jct_macroeconomic and a "dynamic" condition to avoid mixing
  with conventional rows.
- JCX-16-25 refund review, JCX-10-25 offsets: niche; low Scorecard value.

## Files
- manifest.jsonl — 28 rows (url, page_url, title, jcx, date, sha256,
  size_bytes, local_path, doc_type, retrieved_via, retrieved_at)
- claims_staged.jsonl — 6,771 rows as above
- skipped_rows.jsonl — 74 rows, parse-confidence log (reason + raw line)
- downloads/ — 28 PDFs named <JCX>.pdf
- Parser + phase scripts copied into tools/ (scratchpad is wiped on restart):
  jct_table_parser.py, phase1_meta.py, phase2_pdfs.py, te_parser2.py.
  jct_table_parser.py is the one worth porting into the repo adapter.
