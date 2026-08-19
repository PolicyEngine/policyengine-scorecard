# uk_obr harvest notes (2026-08-02)

Source: Office for Budget Responsibility (obr.uk). Publisher slug used in rows: `obr`.

## Access route (no bypasses)
obr.uk is Cloudflare-protected: curl and WebFetch get 403 with an honest UA, and
the live site served an **interactive Turnstile checkbox** in the browser pane —
NOT clicked, per the no-CAPTCHA rule. All bytes came from archives:
- **Wayback Machine original bytes** (`/web/<ts>id_/` URLs, honest harvester UA) —
  all 16 artifacts. Per-file snapshot URL in `manifest.jsonl` (`wayback_snapshot`).
- UK Government Web Archive (webarchive.nationalarchives.gov.uk) was probed and
  works for obr.uk *pages* but had not captured the target xlsx files.
- Wayback SPN (save-page-now) rejected anonymous saves (520) — could not force
  captures of the missing March 2026 files.
- Discovery recipe: archived `/data/` and EFO pages -> `/download/<slug>/`
  links; Wayback replay of a `/download/` slug follows the stored 302 to the
  real file under `obr.uk/docs/...`; plus a domain-wide CDX query filtered to
  `.xlsx` (2026 window) which surfaced newer vintages than the archived data
  page linked (November 2025 PMD, uncertainty ratings, Spring 2026 HOFD).

## Artifacts (16, all sha256'd in manifest.jsonl)
Costings core: Policy measures database **November 2025** (latest vintage; its
Tax Summary includes Autumn Budget 2025 — vintage confirmed from content) and
**March 2025** vintage; Uncertainty ratings database November 2025; Policy
risks database November 2025; EFO Oct 2024 policy tables (Autumn Budget 2024
scorecard as published in the EFO).
Forecast tables: EFO March 2026 receipts (latest); EFO Nov 2025 receipts /
expenditure / aggregates; EFO Oct 2024 receipts; EFO Mar 2025 expenditure;
EFO Mar 2026 chapter 3 charts+tables.
Databases: Historical official forecasts database Spring 2026 + March 2025;
March 2025 ready reckoner; Welfare trends report Oct 2024 charts+tables.

## claims_staged.jsonl — 25,558 rows
| block | rows | metric | notes |
|---|---|---|---|
| PMD Tax Measures | 12,773 | `revenue_change` | 2,579 measure×tax-head rows, 84 fiscal events, Budget 1970 -> Autumn Budget 2025 |
| PMD Spending Measures | 11,531 | proposed `exchequer_impact` | 1,954 rows, June Budget 2010 -> Autumn Budget 2025 |
| EFO Mar 2026 3.4 + 3.8 | 490 | proposed `revenue_level` | income tax/NICs detail + tax-by-tax cash receipts, 2024-25 outturn + forecast to 2030-31 |
| EFO Nov 2025 4.9 + 4.11 | 441 | `benefit_cost` | welfare spending by program (UC elements, PIP, DLA, AA, carer's, child benefit, HB, JSA/ESA, state pension block) |
| EFO Mar 2026 3.17 | 95 | `revenue_change` | latest re-estimated yield of personal tax measures (PA/HRT freezes, ART cut, NICs thresholds) — reform_hint per measure |
| EFO Mar 2026 3.18 | 99 | proposed `taxpayer_count` (persons) | taxpayers with/without indexation, brought into tax / higher rate |
| EFO Mar 2026 3.19 | 129 | proposed `policy_parameter_level` | actual (frozen) vs with-indexation counterfactual PA/HRT/NICs thresholds, £ |

Conventions on every row: value normalized to GBP (proposed unit `gbp`;
UnitConcept lacks it — extend deliberately), `value_raw` = verbatim cell,
`normalization` documents ×1e6 (£m) or ×1e9 (£bn); `period` = FY start year,
`time_basis` fiscal_year, `conditions.fy` = "1970-71"-style label;
`conditions.basis` outturn|forecast from the workbook's own Outturn/Forecast
marker row (`unstated` where the table has no marker — 3.17/3.19).

### PMD staging decisions (the load-bearing ones)
- **Units/sign, verbatim from the Notes sheet**: "All the figures in this
  database are in £ million… We use the Treasury scorecard convention that a
  positive sign implies a gain to the Exchequer, and so reduces borrowing."
  Tax rows: that convention coincides with revenue_change semantics (tax rise
  = +). Spending rows: a positive value = *reduced* borrowing (e.g. the
  June-2010 CPI-indexation switch and DLA gateway show +) — so it is NOT a
  spending change; staged untransformed as proposed `exchequer_impact` with
  `conditions.sign_convention=positive_gain_to_exchequer` and
  `conditions.impact_channel=spending_measure`.
- **Extension cells excluded**: OBR extends costings beyond the original
  scorecard using nominal GDP growth and shades those cells; the shading is
  machine-readable (solid fill FFE1E9EE). Staged only original-scorecard
  cells (24,304); skipped 48,902 extended cells (`costing_phase=
  original_scorecard` on every staged row). Extended values remain available
  in the artifact if ever wanted.
- Pre-June-2010 events are Treasury scorecard numbers (2-year horizons,
  £5m rounding, £50m publication threshold); post-2010 are OBR-scrutinised
  5-year costings (£1m rounding since Budget 2018). source_model =
  `hmt_scorecard_obr_database` for all; the fiscal_event condition dates each row.
- **March 2025 PMD vintage downloaded but not staged**: the database carries
  original costings unchanged across vintages (per its own notes), so
  re-staging would duplicate ~everything minus the two 2025 events; kept for
  vintage diffing at ingest.
- Measures hitting both receipts and spending appear on both sheets (e.g.
  Warm Homes Plan: Environmental levies on tax side, PSGI in CDEL on spending
  side) — both staged, distinguished by tax_head/spending_head conditions.

### Spot-checks passed
- AB2024 "Employer National Insurance contributions: Increase rate by 1.2 ppts
  to 15%…" = +£24.17bn (2027-28), non-dom abolition +£5.73bn — match the
  published scorecard magnitudes.
- 4.11 incapacity spending 2024-25 outturn £29.4bn; 3.4 income tax (gross)
  2024-25 outturn £305.9bn — right scales.
- All 25,558 rows JSON-clean, conditions strictly str->str, 0 failures.

## uncertainty_ratings.jsonl — 1,179 rows (sidecar, not claims)
Final rating + data/behavioural/modelling sub-ratings per measure per event,
Autumn Statement 2014 -> Autumn Budget 2025 (23 events). Join to PMD rows at
ingest on (fiscal_event exact, measure name fuzzy) to populate
`conditions.costing_certainty`. Names differ slightly between the two
workbooks — do the fuzzy join deliberately, not automatically.

## PolicyEngine-UK-runnable costings (best validation surface)
Directly parametric in policyengine_uk:
- **PA + HRT freezes** — 3.17 gives the OBR yield path (£24.3bn 2024-25 ->
  £49.1bn 2029-30) AND 3.19 gives the exact counterfactual thresholds to
  encode the uprated baseline. Cleanest possible reform-validation pair.
- Employer NICs rate 13.8->15% + Secondary Threshold £9,100->£5,000 (AB2024).
- Additional rate threshold £150k->£125,140; employee NICs main-rate cuts
  (AS2023 12->10%, SB2024 10->8%); NICs primary threshold July-2022 rise.
- HICBC threshold changes; two-child-limit removal (AB2025, spending side);
  UC taper 63%->55% + work allowances (AB2021); state pension triple-lock
  upratings; VAT on private school fees (AB2024).
- 3.18 taxpayer counts (brought into tax / higher rate by freezes) are
  PE-computable headcounts.
Level validation: 4.9/4.11 welfare benefit_cost by program × year vs PE UK
program totals; 3.4/3.8 receipts levels vs PE income tax/NICs aggregates.

## Blockers / follow-up fetch queue (one click each in a real browser)
- EFO **March 2026** detailed tables: **policy** (Spring 2026 event costings),
  **expenditure** (latest welfare tables), aggregates — never archived;
  live URLs (pattern confirmed from siblings):
  `https://obr.uk/docs/d055fbf02d5b3g6jq8l2/efo-march-2026-detailed-forecast-tables-{policy,expenditure,aggregates}.xlsx`
  (also available via `https://obr.uk/download/march-2026-economic-and-fiscal-outlook-detailed-forecast-tables-zip-file/`).
- EFO Nov 2025 policy tables (Autumn Budget 2025 scorecard as published):
  not found in archives under any tried name.
- Policy measures database **post-AB2025 refresh**: as of the June-2026
  archived data page the linked PMD was still the March-2025 slug; the Nov
  2025 file is the newest archived. Check live site for a Spring-2026 update.
- Welfare trends report Oct 2024: artifact retained, tables not yet staged
  (overlaps 4.9-style content at an older vintage) — parse at ingest if wanted.
- Ready reckoner staged as artifact only: it is determinant-sensitivity
  (earnings/employment scenarios), not policy levers.

## Parse confidence
High for everything staged: units read from each table's own unit row
("£ billion"/"£ million"/"Million"/"£"), basis from each table's own marker
row, extension flags from the workbook's own shading key. No inferred
mechanics. Re-runnable scripts: stage_pmd.py, stage_efo_tables.py,
stage_receipts_measures.py, stage_uncertainty.py.
