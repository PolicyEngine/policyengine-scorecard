# PWBM harvest notes (2026-08-02)

Target: budgetmodel.wharton.upenn.edu, 2025–2026 budgetary/distributional
estimates, OBBBA prioritized. Honest UA
(`PolicyEngine-Scorecard-Harvester/0.1 ... max@policyengine.org`), ~2s
between requests, all public pages.

## Site structure (changed since task was written)

PWBM redesigned onto Astro. **`/issues` no longer exists (404)** — analysis
briefs now live at `/p/<date-slug>/`, short estimates at
`/estimates/<date-slug>/`, blog notes at `/blog/`. Full URL inventory came
from `/sitemap-0.xml` (718 URLs, saved; 2025–2026 subset in
`target_urls.txt` + `all_urls.txt`). Briefs are server-rendered with real
HTML tables (no JS needed). `/estimates/<slug>/` pages are stubs linking
`charts.html` (legacy fragment, mostly style-only), `data.xlsx` (the real
data), and `doc.pdf`.

## Coverage

25 brief/stub pages + 6 data.xlsx + 6 charts.html + 1 PDF + 5 index/sitemap
files = 43 manifest rows. 85+ tables extracted to `tables/*.csv` (HTML
tables via pandas; xlsx sheets dumped raw). **717 claims staged** from 15
confidently parsed tables across 13 publications.

Staged (parse confidence HIGH — all values verbatim, spot-checked against
page text: signed-bill conventional $3,211B / dynamic $3,631B and WATCA
99–99.9% avg tax change +$18,260 both match PWBM prose):

- **OBBBA signed 2025-07-08** (final = Senate version): T3 deficit
  conventional-vs-dynamic per FY 2025–2034 + window totals; T2 revenue by
  provision category; T5 distribution (2027/2030/2033 × 9 income groups ×
  {avg $ change, group % change, median % change}).
- **OBBBA House 5/19 and House-passed 5/23**: T3 conv/dyn deficit.
- **OBBBA House proposals distribution 5/16** (data.xlsx): 2026/2030/2033 ×
  9 groups × 3 stats (xlsx stores fractions directly).
- **Keep Your Pay Act 2026-03-11**: revenue by provision FY2026–2035 (T4),
  distribution 2026 (T5), package-with-top-rate variant (T6, T7).
- **Working Americans' Tax Cut Act 2026-03-16**: revenue (T3), distribution
  2026 (T4 — literally "Avg Tax Change" → `avg_tax_change_usd`).
- **Eliminate SS benefits income taxation 2025-02-07**: revenue FY2025–2034
  + window total; distribution 2026/2034/2054 (avg tax change + % income).
- **Section 199A reform options 2025-01-27**: 6 options × FY2026–2035.
- **Top ordinary rate options 2025-05-05**: 3 options × FY2026–2035.
- **Jan 2025 budget options** (corp SALT $10k cap; buyback excise 2%/4%;
  PTC repayment limitation removal) via data.xlsx.
- **Tariff revenue projection as of 2025-06-10** (data.xlsx): static vs
  after-import-demand-response, per year + 10-yr window.

## Vocabulary decisions (for ingest)

- `metric: revenue_change` (closed vocab) for all revenue tables. Sign
  verbatim per PWBM convention: **+ = revenue increase**. Values normalized
  billions → USD (×1e9); `unit_note` on every row.
- `proposed_metric: primary_deficit_change` — OBBBA Tables 3 are **primary
  deficit** effects (spending + revenue; + = deficit increase), not revenue;
  outside the task's three-metric vocabulary but it is PWBM's flagship
  conventional-vs-dynamic pair (66 rows). Ingest call: adopt or drop.
- `proposed_metric: pct_change_after_tax_income` for distribution % rows,
  **but** PWBM's concept is percent change in **after-tax-AND-TRANSFER
  income** (includes spending-side changes) for OBBBA/SS tables — recorded
  per row as `conditions.income_concept` (`after_tax_and_transfer_income`
  vs `after_tax_income` for KYPA/WATCA). Values stored as fractions
  (−1.1% → −0.011). `conditions.statistic`: `group_aggregate` vs `median`.
- `proposed_metric: avg_tax_change_usd` ONLY where PWBM's column is
  literally an average tax change (WATCA T4, SS T3; + = tax increase).
  OBBBA dollar columns are "Average change in after-tax-and-transfer
  income" → `proposed_metric: avg_change_after_tax_transfer_income_usd`
  (KYPA: `avg_change_after_tax_income_usd`); + = income gain, USD per
  household. These recur (72 rows) — candidates for deliberate vocab
  extension.
- `conditions.scoring`: `conventional` / `dynamic` (OBBBA T3);
  `static` / `with_import_demand_response` (tariffs). Revenue provision
  tables are conventional-basis.
- Window totals: `conditions.aggregation=window_total` +
  `conditions.budget_window=FY2025-2034` etc., `period` = window's last FY.
- **Baseline matters**: Jan-2025 options, 199A, and top-rate tables score
  against a **TCJA-permanent-extension baseline**, not current law —
  `conditions.baseline_policy=tcja_extension`. OBBBA tables: pre-OBBBA
  current law. KYPA/WATCA (2026): post-OBBBA current law.
- Unit (distribution): household (PWBM prose: "The average household in
  the lowest quintile…"). Income groups normalized:
  first/second/middle/fourth_quintile, p80_90, p90_95, p95_99, p99_99.9,
  top_0.1.

## Ambiguities / flags

1. **Tariff xlsx units unlabeled** — neither sheet, stub, nor PDF states
   units. Inferred billions USD from magnitude consistency (10-yr
   post-response 2,593 ≈ $2.6T vs their 2026-07-29 headline "$2.1 trillion
   over 10 years" for the updated policy set; import base ~$2.8T/yr matches
   US goods imports). Every tariff row carries `UNITS INFERRED` in
   unit_note.
2. **`*` cells** ("less than $500 million"): 3 skipped (signed-bill T2:
   Extend-TCJA 2025, Expand-business 2026, New-individual 2034). One
   `+<0.1%` cell skipped (a top-group % change bounded below 0.1%) — not
   representable verbatim as a float.
3. Signed bill T1 (deficit by Senate committee) and T2 partially
   incorporate CBO/JCT numbers for non-tax committees / "Other tax
   provisions (CBO and JCT)" — PWBM says so in table notes. Rows staged
   as published; attribution caveat lives here.
4. Senate-passed 6/29 brief T3 is numerically identical to the signed-bill
   T3 (final bill = Senate version) — staged once under the signed
   publication to avoid duplicate claims.
5. NOT staged (harvested only): macro-effects tables (GDP/capital/wages —
   no Scorecard metric), OBBBA provision-parameter tables, mass-deportation
   brief (fiscal effects of immigration enforcement — no PE reform
   mapping), Social Security reform options 2026-03-09 (trust-fund
   metrics), budget outlook 2026-05-29 (baseline levels — could seed
   level-validation later), student-loans distribution xlsx (per-borrower
   loan savings, not tax), 2026-07-29 tariff headline ($2.1T — prose, not
   table), OBBBA international tax 2025-10-29 (staged? no — GILTI/FDII
   provisions unrunnable in PE; tables saved), permanence-scenario briefs
   5/20 + 5/28 (illustrative non-enacted variants; tables saved in
   downloads, stageable later).
6. PWBM distribution tables give **lower income cutoffs** per group
   (baseline dollars) — not staged (levels, not reform effects); in CSVs.

## PolicyEngine-runnable mapping (best → worst)

1. **Eliminate SS benefits taxation** — clean parametric PE reform
   (gov.irs.social_security.taxability). Direct comparison.
2. **KYPA** — standard deduction ×~2.33, CTC $4,320/$3,600 fully
   refundable + newborn bonus, EITC childless expansion: all PE-expressible.
3. **WATCA** — millionaire surtax expressible as extra brackets;
   alternative-maximum-tax needs custom logic but feasible.
4. **Top ordinary rate options** — trivially parametric (39.6% over $1M /
   $2.5M) BUT against TCJA-extension baseline, so PE run needs the same
   baseline reform dict.
5. **OBBBA individual provisions** (signed T2 "Extend TCJA individual"
   −$3,369B etc.) — PE has OBBBA current law; the *bill vs pre-OBBBA law*
   comparison is runnable per provision group. Distribution tables include
   spending-side (SNAP/Medicaid) changes — PE can cover SNAP but the
   income concept (incl. Medicaid valuation) needs care.
6. **199A options** — QBI machinery exists in PE; option definitions
   (guardrails/phase-outs) encodable with effort.
7. Stock-buyback excise, corp SALT, tariffs, deportation — corporate/trade
   side, not PE-runnable (tariff *household* incidence could be compared
   to PE's tariff modules if any).

## Files

- `target_urls.txt` — the 25 crawled briefs; `all_urls.txt` — full sitemap.
- `extract_tables.py` — HTML/xlsx → tables/*.csv + manifest.jsonl.
- `stage_claims.py` — tables → claims_staged.jsonl (717 rows). Both
  re-runnable end to end.
