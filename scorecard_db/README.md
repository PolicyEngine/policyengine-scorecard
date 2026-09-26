# scorecard_db

The Scorecard database: every claim an external model makes that PolicyEngine
can check, one SQLite file, reform-keyed.

## Design (Max, 2026-08-01)

- **Reform-keyed.** Every row references the policy world it scores:
  `baseline` (current law) for level validation, a PolicyEngine parametric
  reform for score validation, an Axiom rulespec reference reserved. A level
  is a score of the null reform — modes 1 and 2 share one table.
- **Microcosm-targets shape.** Row = `ledger_fact` (a Chronicle
  `validation_comparator` fact id once cataloged; inline publication
  provenance until then — legacy `ledger` field/path names are frozen) + closed-vocabulary `metric` / `unit_concept` /
  `time_basis` + an open `conditions` mapping (geography, program, subgroup,
  methodological `variant`, `rate_unit`, …). Adapters fail loudly on
  anything unmapped.
- **`calibration_relationship` mandatory** (`consumed_as_target` /
  `seed_source` / `held_out`). Published validation comparisons use held-out
  rows only.
- **History, not state.** `pe_results` keeps every computation (engine
  version × certified data bundle × run); the `comparisons` view joins each
  claim to its latest result. Re-scoring on a new certified artifact appends.
- **Mission control.** `lanes` tracks live stage per source×area lane
  (registered → cataloged → ingested → computed → diagnosing → published →
  regressed); `diagnoses` records adjudications with action links.

## Use

The database is a DERIVED artifact and is not committed: build it from
the vendored sources (all inputs live in this repo; ~4 seconds,
deterministic — CI verifies two builds agree on a logical content hash).

```bash
PYTHONPATH=. python -m scorecard_db.build_db data/scorecard.db
PYTHONPATH=. python -m pytest tests/ -q
```

`build_db` is from-scratch only (it refuses to overwrite — delete the
old file first; nothing is lost, it is derived). Plain `pytest` also
works from a fresh clone: a pytest configuration hook builds the database
before collection when it is absent. Individual ingest modules (`ingest_urban`, `ingest_platform`,
…) remain runnable one at a time against an existing database, in the
dependency order documented in `build_db.py`. Built artifacts for every
main commit are published to the `scorecard-artifacts` Supabase storage
bucket as `<sha>.db.gz` and `latest.db.gz`.

```python
from scorecard_db import ScorecardDB

# after build_db (opening a missing path creates an EMPTY db,
# which the from-scratch builder then refuses to overwrite)
db = ScorecardDB("data/scorecard.db")
db.comparisons(program="snap", geography="US", held_out_only=True)
db.coverage()
```

## 2026-08-02 harvest population

Second population: the overnight seven-source harvest — 12,401 claims
(JCT 6,771 · Budget Lab 1,229 · CPSP 1,033 · TPC 1,057 · CBO 931 · PWBM
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
  tax-benefit-family rows (beyond the validation vocabulary).
  T26-0009's original 48 rows (staging defect verified against the
  workbook) were replaced by a coordinate-pinned per-sheet re-parse —
  135 rows, race as conditions["subgroup"] — via
  sources/harvest-2026-08-02/tpc/reparse_t26_0009.py. Same-statistic
  republication twins (68) are merged with rounding-consistency
  assertions; see sources/harvest-2026-08-02/VALIDATION.md for the
  artifact validation.

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

Country dimension (#62): the ingest is parameterised, not forked —
`ingest(..., country="US")` is the default; every minted claim carries
`publication.country` (claim ids are unchanged: publication is outside the
claim-id hash). The `COUNTRIES` map declares the UK lane (raw_uk/ dir,
`populace-uk-rv-` run prefix, `populace_uk_reform_validation` registry
mark, GBP claims) with a deliberately **empty** release map: the first
`reform_validation.json` a managed populace-uk run produces adds its
release_manifest.json pin there. Non-US artifacts use the country-neutral
categories `Reform` / `Program actual` with an explicit `jct.publisher`
(the US category→publisher inference never runs for them). Replacement
scope is per country — run prefixes are disjoint by test, so one country's
wholesale replace cannot delete another's rows.

## 2026-08-20 population: OBR published policy effects (UK)

Fourth UK population and the external half of the Macro entry point
(issue #55): 266 claims from OBR's own published estimates of what
fiscal policy does to the ECONOMY, harvested by
`sources/obr-policy-effects/adapter.py` and ingested by
`ingest_obr_policy_effects` (chain position: after `uk_deductions`,
before the campaign attaches).

```bash
PYTHONPATH=. python -m scorecard_db.ingest_obr_policy_effects data/scorecard.db
```

Four families on four new metrics — `gdp_level_effect` (151),
`cpi_inflation_effect` (36), `supply_side_impact` (19) and
`decisions_effect_on_borrowing` (60). The first and third are
deliberately distinct metrics: a package's effect on the actual-GDP path
is not one measure's supply-side scoring, and
`decisions_effect_on_borrowing` (PSNB) is likewise kept apart from
`revenue_change` and `cash_requirement_change` (PSNCR).

**Units.** Three of the four quantities look like "percent" and are not
one thing, so each carries its own unit concept:
`percent_of_real_gdp` (a deviation in the LEVEL of real GDP),
`percentage_points` (the AB2025 package's effect on CPI inflation) and
`percent_of_potential_gdp` (briefing paper No.10's supply-side
scorings); borrowing is `gbp`. The mapping is validate-THEN-map: the
adapter's staged unit label must equal the one the metric carries or the
ingest raises, so a mislabeled row can never be stored as a different
quantity.

**Baselines.** These claims are NOT scored against `current_law`. OBR
measures a package as a deviation from that EFO round's PRE-MEASURES
forecast — a distinct named world per round — and briefing paper No.10
chapter 2 splits the counterfactual KIND further: tax and welfare
measures against a legislated-parameter counterfactual, DEL and
regulatory measures against the pre-existing activity/spending baseline.
March 2026 Table B.1 states its own counterfactual in its title (the
November 2025 Budget forecast). Each row carries the world and kind as a
`ReformRef.baseline` descriptor with `conditions["baseline_policy"]`
mirroring it, a locator travels with the claim, an event whose baseline
does not match its round raises, and all eleven (round, counterfactual)
worlds are registered in `baselines.py`. Defaulting to `current_law`
would have let a PE result computed against current law read as
comparable.

**Publication.** Provenance is per vendored artifact, so each round's
claims carry their own release date and dated URL (2023-11-22,
2024-03-06, 2024-10-30, 2025-11-26, 2026-03-03) rather than one generic
`obr.uk/publications/` stamp — and the March 2026 rows carry the
publication date, not the Wayback capture.

All 266 are `held_out`: nothing in pe-uk-data or policyengine-uk is
fitted to a macro-effect path — they are what the Macro members get
scored against. `basis` is `forecast` on every row (its repo-wide
meaning); how the effect was scored rides in
`conditions["scoring_method"]` (`post_behavioural` | `supply_side`).

Two identity decisions this population forced:

- **`conditions["decomposition"]`.** The October 2024 workbook prints
  the AB2024 package twice — chart 2.A by expenditure component, 2.B by
  measure/channel — so both publish a `total` and a
  `demand_multipliers`. The decomposition is therefore identity-bearing,
  not provenance, and is keyed off (fiscal_event, sheet): the sheet id
  alone will not do, since C2.A is by-channel in the Nov 2023 and Mar
  2024 workbooks.
- **The supply-side horizon, per scoring round.** Briefing paper No.10's
  Table 2.1 states its year in words ("the impact on potential output in
  the fifth year of our forecast"), never as a digit — and the paper
  re-states scorings made at five EARLIER fiscal events, so "our
  forecast" is each measure's own round. `_BP10_HORIZON` resolves the
  symbol per event (2027-28 for March 2023 through 2029-30 for March
  2025); the note rides verbatim in `conditions["horizon_note"]` and
  `conditions["horizon"]` names the symbol. Period is claim identity, so
  one shared horizon would have been 19 wrong claims.

Table B.1's nested rows keep the `aggregate_level`/`parent` guard the
OBR welfare lines use, so no consumer summing borrowing effects by FY
double-counts. PE counterparts are step 3 of #55 and are not computed
here.

## 2026-09-24 population: every Autumn Budget 2025 score (UK, #136)

Twenty-five harvest families from 27 producers
(`sources/harvest-uk-ab2025-2026-09-24/`), ingested by
`ingest_uk_ab2025` (chain position: after `uk_policy_effects`, before the
campaign attaches) with a second step, `ingest_uk_ab2025.ingest_verdicts`,
after `campaign_uk`.

```bash
PYTHONPATH=. python -m scorecard_db.ingest_uk_ab2025 data/scorecard.db
```

8,194 staged rows = 6,985 claims + 1,209 tallied drops, pinned per family
in `ingest_uk_ab2025_expected.json`. The drops are decisions with written
reasons, never omissions: 342 re-published official figures (the #86
rule; their originators' rows are in the same harvest), 221 single-
household worked examples and specimen families (mode-3 material, #63),
100 categorical uncertainty ratings, 104 behavioural parameters and
non-monetary tax bases, 119 macro-fiscal aggregates (#55, tranche 4), 85
benefits-in-kind readings (#61 decides how an in-kind series is carried),
and the remainder ratios, threshold levels and single-row quantities with
no registered metric. 28 twins (one statistic printed twice by one
producer) are merged through `merge_republications`.

**Three retrieval axes on every claim.** `source` is the producer;
`conditions.measure_key` is the key in `data/uk/ab2025_measures.json`
(shared across producers, so the two-child measure's rows from HM
Treasury, the OBR, the IFS, RF, JRF, IPPR and CPAG join on one reform
key per baseline world); `conditions.fiscal_event` is `autumn_budget_2025`.
`conditions.benchmark_class` is set on every row — the first UK use of
the cross-model epistemics ruling — and the Fabian Society's four
PolicyEngine-computed rows are `same_assumptions`.

**The verdict on the row.** Every keyed claim carries the registry's
`pe_expressibility`, and a `not_expressible` one carries `pe_missing` and
`action_link` (the ONS ETB pattern). The verdicts step then writes, for
each such claim, a `pe_results` row with status `pe_gap` (no value, the
certified pin as engine and bundle, the registry's `why` and name search
as annotations) and a `diagnoses` row of class `pe_gap` carrying the
link, so `SELECT COUNT(*) FROM comparisons WHERE pe_status='pe_gap' AND
action_link=''` is zero by construction. Expressible and partial measures
have no result row until the tranche-3 run attaches one.

**Units and metrics minted** (recurring across producers only):
`affected_count` / `affected_share`, `average_tax_change`,
`share_no_change`, `energy_bill_change`, `revenue_share`; units
`properties` and `estates`.

**Visibility.** Every national-grain claim sets
`publication.publish_without_result` so it reaches the page before a
counterpart exists; the 2,991 constituency-grain Tax Policy Associates
rows stay in the DB and out of `populations.json` until a constituency
view exists.

**Worlds.** Fourteen producer-defined counterfactuals quoted in the
harvest as `proposed_baseline` are registered in `baselines.py` and mapped
by their opening words in `_PROPOSED_BASELINE_PREFIXES`; a row on an
unregistered world raises rather than defaulting to current law (#13).


### Tranche 3 (2026-09-25): PolicyEngine counterparts on the certified bundle

Run `campaign-20260925-uk-ab2025` (`pipeline/compute_uk_ab2025.py`, policyengine-uk
2.89.2 on `populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z`, sha256 `f17306cc…`
checked before every simulation; calendar years 2026–2030 proxy FY 2026-27 to
2030-31; static, no behavioural response): 40 measures × 5 years = 200 artifacts
under `results/uk/ab2025/`, plus `RUN_MANIFEST.json` naming the 24 expressible
measures the runner refused with the reason for each (string `package_of`,
mixed reversal/forward packages, levers the certified engine has no parameter
for) and the two aliases that execute another measure's lever. A measure that
carries BOTH a `pe_baseline_modifier` and a `pe_reform_delta` outside a reversal
(the two-year threshold-freeze option) executes both worlds — the modifier as
the baseline, the delta as the reform — and its executed baseline is the parent
measure's registered pre-Budget world.

`pipeline/stage_uk_ab2025.py` derives `results/uk/staged_ab2025/ab2025_counterparts.jsonl`
from those artifacts against the built database — 915 counterparts on 22
measures, every row `constructed` (the claim's own baseline and the executed
pre-Budget world are named in the annotations, with the period proxy and the
sign orientation) — and writes every claim it could NOT answer to
`results/uk/ab2025/STAGING_TALLY.json` with its reason: 3,321 sub-national claims
(no sub-national compute), 1,133 on a fiscal year or measure the run has no
artifact for, 442 without a fiscal year, 200 on artifacts whose reform world is
identical to the baseline world (the lever did not bite on the certified engine
and data — a switch the engine ignores, a data-driven state pension, an option
that is already current law — tallied `lever inert`, never attached as a zero),
3 exchequer claims whose head moved while `gov_tax` and `gov_spending` did not
(the aggregates do not carry that head), and the metric shapes the mapper has
no counterpart for yet (`average_tax_change` 241, `affected_share` 61,
`participation_rate` 45, `income_statistic` 24, …). The 222 claims that carry
`obr_measure_key` are tallied `owned_elsewhere`: the OBR costings lane above
answers them, so no claim ever carries two computed answers (a fact of the built
database, checked in `tests/test_uk_ab2025_counterparts.py`).

Build step `campaign_uk_ab2025` attaches the staged rows through
`ingest_campaign` (claim_id-direct, executed world stamped from the
`pre_ab2025__*` registry, deletion scoped to this run_id); the lane advancer
then reads `uk-ab2025-official` (270 claims answered), `uk-ab2025-microsim`
(631), `uk-ab2025-admin-other` (13) and `uk-ab2025-macro` (1) as `computed`.
Re-running the stager against the built database must reproduce the committed
file byte-for-byte; the runner's `--resume` picks up an interrupted run from its
artifacts (one simulation at a time, `HDF5_USE_FILE_LOCKING=FALSE`).

## 2026-09-25 population: OBR-certified measure costings (UK, #54/#56)

`ingest_obr_costings` (chain position: after `uk_policy_effects`, before
`uk_ab2025`) ingests the 621-row slice of the OBR Policy Measures Database
(November 2025 vintage, 552 rows, source `obr_pmd`) and the EFO March 2026
Table 3.17 re-estimates (69 rows, source `obr_efo`) that
`data/uk/obr_measure_reforms.yaml` scores. The slice is DERIVED from the
vendored harvest by `pipeline/select_obr_costings_claims.py` (25,558 rows
read = 621 selected + 24,937 outside the registry; `--check` is byte-exact),
which also writes the JSON projection of the YAML registry the build reads.

```
PYTHONPATH=. uv run --with pyyaml python pipeline/select_obr_costings_claims.py --check
PYTHONPATH=. python -m scorecard_db.ingest_obr_costings data/scorecard.db
```

Identity: every condition key is in `STANDARD_CONDITIONS`; claims key the
FY END year; `exchequer_impact` rows carry `REVENUE_CHANGE` with
`fiscal_measure = exchequer_impact`; every row names the registered world
OBR scored it against (that round's `obr_pre_measures_<event>`, or the
indexed-thresholds counterfactual for the March 2026 re-estimates) and, for
the Autumn Budget 2025 measures, the #136 registry key so the OBR leg joins
the other producers' rows on one reform key.

Results: `produce_obr_costings` (after `campaign_uk`) resolves the compute
staging `results/uk/staged/obr_costings.jsonl` to claim ids and stamps the
world PE EXECUTED (`baseline_key`: the registered pre-measure world for a
reversal on the certified world); `campaign_uk_obr_costings` attaches it via
`ingest_campaign`, which now honours a staged `baseline_key` and refuses an
unregistered one.

Ownership of overlapping measures (the #56 / #140 rule): a claim that carries
`conditions.obr_measure_key` is in the OBR costings slice and is answered ONLY by
this lane's compute (per OBR head, in OBR's conventions); every other claim on an
`ab2025__` measure is answered ONLY by the AB2025 counterparts stager
(`pipeline/stage_uk_ab2025.py`), which skips claims carrying `obr_measure_key`.
One claim, one computed answer, never two.
