# scorecard_db

The Scorecard database: every claim an external model makes that PolicyEngine
can check, one SQLite file, reform-keyed.

## Design (Max, 2026-08-01)

- **Reform-keyed.** Every row references the policy world it scores:
  `baseline` (current law) for level validation, a PolicyEngine parametric
  reform for score validation, an Axiom rulespec reference reserved. A level
  is a score of the null reform — modes 1 and 2 share one table.
- **Populace-targets shape.** Row = `ledger_fact` (a Ledger
  `validation_comparator` fact id once cataloged; inline publication
  provenance until then) + closed-vocabulary `metric` / `unit_concept` /
  `time_basis` + an open `conditions` mapping (geography, program, subgroup,
  methodological `variant`, `rate_unit`, …). Adapters fail loudly on
  anything unmapped.
- **`calibration_relationship` mandatory** (`consumed_as_target` /
  `seed_source` / `held_out`). Published validation wins = held_out only.
- **History, not state.** `pe_results` keeps every computation (engine
  version × certified data bundle × run); the `comparisons` view joins each
  claim to its latest result. Re-scoring on a new certified artifact appends.
- **Mission control.** `lanes` tracks live stage per source×area lane
  (registered → cataloged → ingested → computed → diagnosing → published →
  regressed); `diagnoses` records adjudications with action links.

## Use

Full rebuild, in order (idempotent; urban/platform/solo read the
machine-local ~/populace-sotsn-takeup/comparison interchange, everything
else reads vendored sources/):

```bash
PYTHONPATH=. python -m scorecard_db.ingest_urban data/scorecard.db
PYTHONPATH=. python -m scorecard_db.ingest_platform data/scorecard.db
PYTHONPATH=. python -m scorecard_db.ingest_solo data/scorecard.db
PYTHONPATH=. python -m scorecard_db.ingest_diagnoses data/scorecard.db
PYTHONPATH=. python -m scorecard_db.ingest_harvest data/scorecard.db
PYTHONPATH=. python -m scorecard_db.ingest_reform_validation data/scorecard.db
PYTHONPATH=. python -m scorecard_db.ingest_uk data/scorecard.db
PYTHONPATH=. python -m scorecard_db.ingest_campaign data/scorecard.db
PYTHONPATH=. python -m scorecard_db.ingest_campaign_uk data/scorecard.db
python -m pytest tests/
```

```python
from scorecard_db import ScorecardDB

db = ScorecardDB("data/scorecard.db")
db.comparisons(program="snap", geography="US", held_out_only=True)
db.coverage()
```

## 2026-08-02 harvest population

Second population: the overnight seven-source harvest — 12,266 claims
(JCT 6,771 · Budget Lab 1,229 · CPSP 1,033 · CBO 931 · TPC 922 · PWBM
717 · Tax Foundation 663) from staging vendored at
sources/harvest-2026-08-02/ (claims + sha256 manifests + notes; raw
downloads stay outside the repo, pinned by the manifests). Run
everything with:

```bash
PYTHONPATH=. python -m scorecard_db.ingest_harvest data/scorecard.db
```

Schema decisions this population forced (COLLATION worklist):

- **Metric/UnitConcept extensions** for the recurring proposed metrics:
  pct_change_after_tax_income (PERCENT, 0–100 scale), avg_tax_change_usd
  and avg_change_after_tax_income_usd (USD_PER_TAX_UNIT for TPC,
  USD_PER_HOUSEHOLD for PWBM — the denominator split is load-bearing),
  share_with_tax_cut, primary_deficit_change, tax_expenditure (reserved
  for JCX-45-25), poverty_count, and the CBO baseline-detail families
  (IIT walk + program benefit statistics).
- **Period ranges**: ten-year-window claims carry period_start /
  period_end with `period == period_end` and
  conditions["window_kind"] ∈ {total, annual_average}; single-year claim
  ids are unchanged (the window keys enter the hash only when set).
- **policy_ref reforms**: named external policy worlds
  ({"policy": slug, …}) pending PE encoding, with non-current-law
  baselines as ReformRef.baseline descriptors (TCJA extension, JCT
  current policy, TPC current-law + Senate Title VII, …), mirrored to
  conditions["baseline_policy"]. Descriptors stay minimal so identical
  worlds share a reform key across sources — JCX-35-25 / TPC
  T25-0229/0236 / TF's enacted-OBBBA page all key to
  obbba_enacted_title_vii, and the JCX-30/31 manager's-amendment twins
  share a slug and differ only in baseline.
- **Conditions vocabulary** standardized in models.STANDARD_CONDITIONS
  (income_group/income_axis/income_concept, scoring, baseline_policy,
  option, statistic, window_kind, month, data_vintage).
- Deliberate exclusions, tallied in lane notes: TPC's 468
  tax-benefit-family rows (beyond the validation vocabulary) and
  T26-0009's 48 rows (staging defect verified against the workbook).
  Same-statistic republication twins (68) are merged with
  rounding-consistency assertions; see
  sources/harvest-2026-08-02/VALIDATION.md for the artifact validation.

## 2026-08-02 UK population + baselines registry

Fourth population: the seven-source UK fleet — **31,762 claims**
(OBR 25,425 · DWP 1,952 · HMT 1,368 · HMRC 987 · UKMOD 1,392 · JRF 300
· IFS 268 · Resolution Foundation 70) from gzipped staging vendored at
sources/harvest-uk-2026-08-02/. Run with:

```bash
PYTHONPATH=. python -m scorecard_db.ingest_uk data/scorecard.db
```

Full accounting against the 33,943 staged rows: 31,762 ingested +
**2,090 admin outturns routed to the Ledger staging file**
(data/ledger/uk_admin_outturns.jsonl — HMRC outturn/provisional 1,855,
OBR EFO outturn columns 133, DWP BECL outturns 102; deterministic
pre-agreed fact ids for the populace/Ledger lane. Routing rule, Max
2026-08-02: admin facts → Ledger, model claims → Scorecard; a forecast
is a model speaking and stays) + 89 deliberate drops tallied in lane
notes (88 JRF MIS budget cells, 1 RF price-index row) + 2 JRF
rounded/unrounded republication twins merged.

Decisions this population forced:

- **period = FY start year everywhere** (pe-uk-data convention),
  re-derived from the verbatim fy label — the staging mixed start-year
  (HMRC/OBR) and FYE end-year (DWP) ints and had a '1999/00'→1900
  defect; conditions["fy"] carries the normalized "2026-27" label.
- **Baselines registry (issue #13)**: `baselines` table + baseline_key
  on external_scores/pe_results/pe_exhibits; the comparisons view
  exposes both sides' labels and pe_status_effective — a result
  computed against a different baseline world can never render as plain
  agreement. IFS's Green-Budget options ride the registered
  ifs_2cl_fp_removal_rolled_out world; HMT/OBR costings score against
  current law at announcement (JCT parity — the event is a condition,
  not a baseline world).
- **Descriptive register (issue #9)**: diagnosis class
  methodological_difference added; pe_gap/external_issue now REQUIRE a
  citable action_link (db.diagnose raises otherwise).
- **calibration_relationship from verified consumption**: exact
  pe-uk-data target lines (targets/sources/obr.py receipts + Table 4.9
  welfare; BECL expenditure for the five exact-line benefits; DWP UC
  admin, PC take-up seed) read 2026-08-02; SPI-family projections are
  seed_source via the shared SPI 2023-24 base; poverty_count and
  persistent_poverty_rate joined the permanent-holdout set.
- **Reconstructed identity axes** the staging dropped: OBR 4.9
  welfare-cap sections, 4.11 parent lines, per-head measure component
  runs, the Mar-2026/Nov-2025 EFO vintage split, IFS recipient groups.

Fifth population: the **2026-08-02 campaign compute batch**, in two
sibling modules over sources/campaign-20260802/. ingest_campaign
attaches the day-1 US families from the campaign's staged descriptor
JSONL (us/); ingest_campaign_uk lands the UK side from the vendored raw
runs (uk_runs/) — 65 results (uk_reckoner 23 · uk_free_joins 23 ·
uk_obr_measures 10 · uk_uprating 6 · two_child_pentagon 3) + 11
two-child-limit exhibits against the registered pre_ab2025 baseline +
8 CPSP register diagnoses. Every result records the baseline it
actually executed (#13); joins assert exactly-one-match. See both
modules' docstrings for the join families and why the staged UK
descriptor files are superseded rather than attached.

First population: Urban SotSN — 30,004 claims (24,717 published values).
`calibration_relationship` is assigned per (program, metric) from the
certified build's documented target surface and seeds
(`scorecard_db/relationships.py`), never defaulted: SNAP/SSI participation
and refundable-CTC counts are `consumed_as_target`, TANF participation is
`seed_source` (ASPE/TRIM3), everything else `held_out`. PE results: the
interchange's 678 totals (run `sotsn-first-cut`) plus the platform's 7,912
subgroup × state grid (run `platform-grid-2024`, with the real status
taxonomy and annotation ids); the `comparisons` view serves the latest per
claim. Counterfactual worlds use the `policyengine_us_inputs` framework —
input-override descriptors (forced take-up flags), not parametric reform
paths, because no such parameters exist in the engine.

## 2026-08-03 population: populace reform-validation registry

Third population: the per-release external-checks registry previously
rendered as calibration-diagnostics' "External checks" tab (being retired
in favor of this scorecard). 205 claims + 675 per-release pe_results from
five certified releases (f0af251 through Build O), vendored at
sources/populace-reform-validation/raw/:

```bash
PYTHONPATH=. python -m scorecard_db.ingest_reform_validation data/scorecard.db
```

What it adds that the other populations don't: **regression history** —
each artifact was computed at its release's exact engine pins
(ENGINE_VERSIONS, with per-row overrides the artifacts document about
themselves), so long-lived claims carry one pe_result per release — and
exactly one: repeal constructions whose benchmark duplicates the direct
level are dropped — and drift across releases is queryable. The OBBBA
suite mints no claims of its own: its results attach to the harvested
JCX-35-25 provision claims (canonical per issue #15), both the FY2026 and
FY2027 ones, with the release's scoring mode (stacked_chained for f0af251,
whose own totals chain; isolated for l0-refit; jcx_stacked from buildi on)
in the pe_construction. Claim periods key the year the claim describes,
parsed from each benchmark's window (fiscal-note FY2028 claims are 2028,
SOI TY2023 is 2023, Census 3-year averages carry period_start/period_end);
anything not identical to PE's single-calendar-year computation is
status=constructed, and rows the artifacts flag as measuring a different
concept (UT's claimed-vs-capped CTC) are concept_mismatch. All parsing
and validation happens before any write, and the replacement (deletes,
claims, results, lane) is a single transaction — a failed re-ingest, at
any point, leaves the DB untouched. First rows on the reserved TAX_EXPENDITURE metric
(JCX-48-24 / Treasury / the jct.tax_expenditures.* calibration targets,
the latter consumed_as_target). Census state SPM rows land as held_out
POVERTY_RATE claims per the poverty-holdout doctrine. Scored rows key off
policy_ref descriptors ({"policy": <registry row id>}) until populace's
payload embeds the executable reform dicts (populace #606). Every claim
this ingest mints is marked publication.registry =
"populace_reform_validation" — that marker is the idempotency contract
(re-ingest deletes and recreates exactly these claims, never the harvest
claims it attaches results to).
