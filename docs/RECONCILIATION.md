# Reconciliation: two independent SotSN comparison builds (2026-08-01)

Two sessions built the Urban State of the Safety Net comparison in parallel
without shared state:

- **Session A** (this directory): `urban_parse.py` + `compare_sim.py` +
  `merge.py` → `urban_tidy.csv`, `pe_baseline*/pe_fullpart*.csv` (2024 +
  2026), `comparison.csv`, `FINDINGS.md`.
- **Session B** (the platform, `~/PolicyEngine/policyengine-scorecard`):
  `sources/urban-sotsn/adapter.py` + `pipeline/compute_counterparts.py` +
  `pipeline/build_comparison.py` → 30,004 tidy externals, 29,514 PE metric
  cells (3 runs × subgroup × state grid), `data/comparison.json`, and the
  scorecard app.

`reconcile.py` diffs the two layer by layer. This is the triangulation logic
the platform exists to perform, applied to itself.

## Verdict

**The two Urban parses agree on every one of 29,588 matched program keys
(zero value disagreements, zero suppression disagreements), and the two PE
computations agree bit-exactly on every shared construction except the
full-participation poverty family — where the difference is a real bug in
Session A's counterfactual (patched below).** Independent implementations,
same artifact, same numbers: both pipelines are now cross-validated.

## Disagreements found, with root causes

| # | Finding | Root cause | Class | Action |
|---|---|---|---|---|
| 1 | A's `fullpart_change_*` rows carried garbled keys (`metric="change"`, breakdown like `spm_pov_rate_100_pop_total`) and values inflated ×1000 (people lifted read −15.39 **billion**; rate change read −336.0) | `urban_parse.py`'s metric regex has no alternation for the change families, so `.+?` split the name at the wrong underscore, and the count×1000 scaling applied to values that are already fractions / raw persons | bug in A (parse) | **Patched**: 208 rows rewritten as `spm_pov_rate_change_100` / `spm_pov_num_change_100`, breakdown `total`/`child`, values ÷1000 — now matching B's parse, which validates against Urban's slides (−33.6%, −15.39M) |
| 2 | A's fullpart SPM poverty differs from B's corrected run (US 13.013% vs 12.910%; AK 9.78% vs 7.95%, a 23% relative gap) | `would_claim_wic` is a **monthly** variable; `compare_sim.py:44` set it at the year period, which leaves the stored monthly gate in place — the counterfactual never forced WIC. B hit the identical trap first, diagnosed it from engine metadata (`definition_period: month`), and re-ran with all 12 months set + post-set verification (toggle means logged in B's `data/pe/pe_meta.json`) | bug in A (sim) | **Patched**: 104 `pe_fullpart.csv` poverty rows replaced with B's corrected-gate values (2024). **`pe_fullpart_2026.csv` still carries the bug** — flagged, not patchable without a new sim run (out of scope per session instructions); its EITC/CTC `elig_units` rows are unaffected (the WIC gate is not in the EITC/CTC formula chain per the mechanics audit / replication assessment §2) |
| 3 | A retained 312 exact-duplicate rows | the webtool file ships six `*_2023_1` duplicate columns; A's regex folds them onto the same key without deduping | schema ambiguity | **Patched**: deduped; both tidies now have 30,004 rows |
| 4 | A's TANF/SSI comparisons use broad denominators (TANF demographic-only 169M, SSI pre-income-test 34.1M), classified in FINDINGS.md as "PE gap — needs a payable variable" | not a bug — A matched Urban against PE's *native* eligibility concepts | improvement available | B already computes the tighter constructions from the forced-take-up run: **TANF income-eligible persons 8.50M vs Urban 11.40M (−25%)** and **SSI payable adults 9.99M vs Urban 12.60M (−21%)**, superseding two of FINDINGS.md's five diagnoses with quantified, same-concept comparisons |
| 5 | Harness note: a naive (program, metric, geography, breakdown) join compared Urban's TANF **family-unit** row against **person** values | Urban publishes both units and persons for the same metric; unit must be part of any join key | schema lesson | folded into SCHEMA_NOTES.md; B's join enforces expected unit concepts per program |

## Cross-validation receipts (identical to ≤1e-9 relative)

SNAP eligible persons (52/52 geographies), SNAP participants, WIC eligible /
participants (children 0–4), SSI broad-eligible adults + recipients, TANF
demographic-eligible + recipients, baseline SPM poverty (total + child, all
geographies), EITC/ACTC positive-credit units under forced take-up — 566
values bit-identical before any patching; the only non-exact family was the
fullpart poverty block explained by #2.

## What each side contributes going forward

- From A: the **2026 projection columns** (`pe_value_2026`) — engine-side
  aging on the same certified artifact, the thing ATTIS can't do; the
  totals-first `comparison.csv`; FINDINGS.md's diagnosis seeds.
- From B: the subgroup × state PE grid (9.3k matched cells), the
  payable-denominator constructions (supersede finding classes 2–3 in
  FINDINGS.md), the status taxonomy + traceable annotations, the coverage
  spine app, and the corrected full-participation counterfactual (both
  variants: all-flags and Urban-six).

Canonical after this reconciliation: the files in this directory (patched),
plus the platform repo's `data/` for subgroup-level and construction-tagged
rows. Schema unification: `SCHEMA_NOTES.md`.

> Canonical home of this document: `~/populace-sotsn-takeup/comparison/` (kept in sync manually).
