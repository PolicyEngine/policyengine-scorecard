# CPSP harvest notes (2026-08-02)

Source: Center on Poverty and Social Policy, Columbia University (povertycenter.columbia.edu).
Scope: poverty-impact publications 2024-2026 — monthly poverty series, CTC counterfactuals,
SNAP poverty effects, annual historical/anchored SPM rates.

## Access mechanics (matters for refresh runs)
- The live domain sits behind a **Cloudflare managed challenge for HTML pages** (`cf-mitigated:
  challenge`); curl cannot fetch pages regardless of UA. **Static files under `/sites/` are NOT
  challenge-gated** and download fine with an honest UA. So: artifacts fetched live; HTML pages
  fetched from the Wayback Machine (latest capture; `id_` original bytes, sometimes gzipped —
  decompress before parsing). Wayback timestamps recorded per page in manifest.jsonl.
- The site migrated from Squarespace (www.povertycenter…, `static1.squarespace.com` assets) to
  Columbia Drupal (`/sites/default/files/` then `/sites/povertycenter.columbia.edu/files/`) in
  late 2024; old URLs live on in redirects. Publication URLs are `/publication/2025/<slug>`.
- Monthly dataset is a **public Google Sheet** (export?format=xlsx worked):
  docs.google.com/spreadsheets/d/1t4BiF6hDkViCGekmi3HMf8jer7iJaON6ivrztJF3KJ0

## Coverage
- 25 artifacts in downloads/ (20 PDFs, 5 xlsx; all live-fetched except the anchored-rates xlsx,
  which came from Wayback) + 16 HTML pages in pages/; 41 manifest rows total. 1,033 claims
  staged (after dedupe; 961 construct as ExternalScore today, 72 carry proposed_* awaiting
  vocabulary decisions).
- Claims by block:
  - **Monthly SPM series** (230 rows): 2024-01…2025-12 from the Primary sheet of the monthly
    dataset. time_basis=point_in_time, conditions.month="YYYY-MM". Subgroups: all, children,
    age_18_64, age_65_plus, latino, asian, black, white (all under "With All Taxes & Transfers");
    plus All-persons rows for scenario columns "Without COVID Relief" and "Pre-Tax/Transfer".
    **2025-10 is missing in the source** (row present, values blank — presumably the
    shutdown-delayed CPS). **The project ended with December 2025** (Gates funding concluded;
    the 2026-07 page says no new monthly data will be published).
  - **CTC counterfactuals 2024** (What Could 2024 …, Table 1): scenarios No CTC / TCJA CTC /
    OBBBA CTC / AFA CTC; child (<18) and <6 rates, relative reductions, counts, moved-out counts.
  - **CTC counterfactuals 2023** (What Could 2023 …, Table 1): No CTC / 2023 TCJA / 2023 AFA ×
    thresholds 100/50/150/200% SPM (conditions.poverty_threshold).
  - **SNAP TFP revocation** (May 2025 brief): national Table 1 (incl. SNAP-recipient subgroups)
    + Tables 2-3 by state (51+DC overall, child). Vermont child moved-count is censored "<1,000"
    → omitted. AK/HI rows carry a caveat condition (TFP adjustment for AK/HI not modeled).
  - **Refundable state CTC designs** (Table 3): pooled "38 states without refundable CTCs"
    geography label; 13 state designs × poverty + deep poverty.
  - **Annual historical rates** 2023/2024 × measure_variant (historical_spm, anchored_2012_spm,
    anchored_2022_spm, relative_50pct_median; child pre-tax/transfer variants).

## Conventions used in claims_staged.jsonl
- **All rates are decimal shares** (11.8% → 0.118); pp changes /100; relative changes /100 with
  conditions.change_type ∈ {percentage_point, relative_percent_reduction,
  relative_percent_increase, count_moved_out, count_moved_into_poverty}.
- **Sign convention: value <0 = poverty falls** (children moved OUT stored negative);
  TFP revocation increases stored positive. source_column keeps the verbatim table label.
- proposed_metric "poverty_count" for level counts in poverty (Metric enum has only the change);
  proposed_unit_concept "children_under_6" (enum's children_0thr4 is 0-4, not <6 — do NOT map).
- CPSP "children" = under 18 (their standard); left-behind reports use "under 17" for the CTC
  age universe — that's why left-behind counts were NOT staged as poverty metrics.
- SNAP TFP: **period=2019** with conditions.data_vintage="TRIM3-adjusted CPS-ASEC pooled
  2015-2019" — the brief models the cut on pooled 2015-19 TRIM data, so levels are NOT
  2025-comparable; treat as vintage/concept flag at ingest. Policy world is the 2025 proposal.
- State-CTC-designs geography is the pooled non-CTC-38-states universe, labeled
  `us_38_states_without_refundable_state_ctc` — not PE-comparable without replicating the pool.

## Data quality flags
- **Erratum in "2024 Poverty Rates in Historical Perspective"**: Key Findings bullet says
  anchored-2022 SPM was "16.6% in 2024", but the body (Fig. 3 discussion) says 11.4% and the
  quoted 59% decline from 27.9% implies ~11.4%. Staged 11.4% (flagged in source_column);
  16.6% NOT staged. (16.6% equals the 2024 no-CTC child rate from the What-Could brief —
  likely a copy-paste slip.)
- Monthly sheet "All Estimates" (long format) tab is stale (ends 2023-12); Primary tab is
  current through 2025-12. Claims use Primary.
- TFP Table 1 SNAP-recipients-all pp: 40.3−36.5=3.8 but table prints 3.9 p.p. (rounding);
  staged verbatim 3.9 with source_column pointing at the table.
- What-Could-2024 note: OBBBA CTC estimates "do not account for new restrictions on
  eligibility for children with immigrant parents" nor other OBBBA cuts — scenario is CTC
  parameters only. Both What-Could briefs assume 100% CTC take-up, no behavioral response
  (Appendix C has employment-response variants; not staged).

## What maps cleanest to PolicyEngine SPM outputs
1. **CTC counterfactual tables (2023, 2024)** — cleanest of all: CPS-ASEC annual SPM, national,
   child rates under explicit parametric CTC worlds (TCJA / OBBBA / AFA H.R.2763 [2025] and
   H.R.3899 [2023]). Directly expressible as policyengine_us reforms; 100% take-up matches PE
   default tax logic.
2. **Annual historical SPM levels** (12.9% 2023/2024 overall; 13.3% 2024 child) — matches
   Census published SPM for recent years; populace may already consume Census SPM as targets →
   ingest should consider calibration_relationship=consumed_as_target rather than held_out.
3. **Monthly series** — unique validation surface but PE has no monthly SPM machinery; a PE
   comparison needs an annual-to-monthly construction (their method: monthly income concept
   w/ annualized taxes/credits at receipt timing — see Monthly-SPM-Technical-Note artifact).
   Mark PE side "constructed" at best.
4. **SNAP TFP state tables** — good reform-direction check (PE can model TFP revocation), but
   vintage mismatch (2015-19 TRIM base) means compare *changes*, not levels.
5. **State CTC designs** — pooled-universe geography makes direct comparison awkward; the
   design parameters (their Table 1) are useful for reform specs.

## Gaps / blockers
- `The-Potential-of-Local-Child-Tax-Credits-to-Reduce-Child-Poverty.pdf`: 404 live, no Wayback
  capture of the file (page manifested; brief published 2025-11). Needs a browser session or a
  retry later.
- Anchored/historical rates **xlsx block labels ambiguous** (merged header cells: Total
  Population + 3 unlabeled blocks, almost certainly Children / working-age / 65+ by value
  pattern). Claims NOT staged from the xlsx — verify labels at ingest before using; annual
  claims came from the briefs instead. A 1967-2024 update may exist behind /historical-spm-data
  (challenge-gated; not archived recently).
- The **Historical SPM Data Portal** offers person-level public-use files (via portal UI) —
  worth a separate grab if we want the microdata; only the documentation PDF harvested.
- Left-behind CTC counts (17M/19M "left behind" under TCJA/H.R.1; state + congressional-district
  xlsx artifacts harvested and manifested) are NOT poverty metrics — staged nothing; consider a
  future metric like `ineligible_full_ctc_count` if Scorecard wants them.
- Economic Costs of Cutting SNAP: societal cost multiplier ($14-$20 per $1 SNAP cut) — not a
  poverty metric; artifact + appendix harvested for the record.
- Publications listing pages themselves aren't cleanly archived post-migration; discovery ran
  via the Wayback CDX domain sweep instead — a future live-browser crawl of
  /publications?topic=… would confirm nothing 2026-published was missed (as of the 2026-07-10
  archive of the monthly page, no 2026 poverty-impact briefs surfaced in CDX).
