# Mode-3 case-diff schema (shared: UKMOD/EUROMOD and TAXSIM lanes)

The scorecard's third claim class: **record-level case diffs**. Instead of a
published aggregate, the external model is run as an *oracle* on curated
hypothetical households, and PolicyEngine's per-variable outputs are compared
case by case. One schema serves every mode-3 lane — this document is the
single contract for both `ukmod-cases` (#41) and `taxsim-cases` (#5); the
`country` and `oracle` fields are what keep it engine-agnostic. Do not fork a
second schema for a new oracle: extend the closed vocabularies here, fail-loud
style, and note the extension.

Code: `scorecard_db/case_diffs.py` (dataclasses, battery loader, classifier).
Battery: `sources/ukmod-cases/battery/cases.json`. Tests:
`tests/test_case_schema.py`.

## Case (input) — `CaseSpec`

A case is a fully specified hypothetical household plus the variables it is
designed to exercise. **Inputs only** — a case never embeds expected output
values; both sides of every comparison come from engine runs (PE and the
oracle), so the battery cannot smuggle in hand-computed "truth".

```json
{
  "case_id": "uk-uc-single-unemployed",
  "description": "Single unemployed adult, social rent, on UC",
  "policy_year": 2026,
  "country": "UK",
  "household": { ... },
  "expected_focus": ["universal_credit", "income_tax"],
  "rationale": "Why this case is in the battery, and what edge it pins"
}
```

- `case_id` — globally unique slug, prefixed with the country
  (`uk-…`, `us-…`); stable forever once results reference it.
- `policy_year` — the tax-benefit year the case is evaluated in (for the UK,
  the fiscal year starting 6 April of that calendar year).
- `country` — closed set, currently `{"UK", "US"}`; extend when a new
  mode-3 lane lands (EUROMOD EU countries, state calculators).
- `expected_focus` — the output variables (canonical names, below) the case
  was designed to exercise. The runner computes and diffs *all* mapped
  variables; `expected_focus` drives coverage accounting (every battery must
  exercise each focus area at least once) and diff triage order.
- `rationale` — human audit trail: why these numbers, what boundary they sit
  on.

### Household spec (engine-agnostic)

The household is described in a small, closed, engine-neutral input
vocabulary. Each lane's connector owns the mapping from this vocabulary to
its engines' variables (PE UK / UKMOD policy spine; PE US / TAXSIM v35
columns); the mapping table lives with the connector, never in the battery.
Unknown keys are a hard error — adding an input concept means extending the
vocabulary in `case_diffs.py` and documenting it here.

```json
{
  "people": {
    "adult_1": {"age": 35, "employment_income": 12000},
    "child_1": {"age": 8}
  },
  "benefit_units": [
    {"adults": ["adult_1"], "children": ["child_1"]}
  ],
  "region": "LONDON",
  "tenure": "rented_private",
  "rent": 13000
}
```

Conventions:

- **All monetary amounts are annual, in the country's currency** (GBP for
  UK, USD for US). Weekly-quoted UK amounts enter as weekly × 52 (round,
  auditable numbers preferred — e.g. £250/week rent = 13000).
- Every person appears in exactly one benefit unit. A benefit unit is the
  assessment unit (UK: single/couple + dependent children; US: the tax
  unit). Multi-benefit-unit households are allowed (e.g. a non-dependant
  adult) but every person must be assigned.
- Omitted person keys default to 0 / false. Only non-defaults are written,
  so each case reads as exactly its rationale.

Person keys (closed set):

| key | type | meaning |
|---|---|---|
| `age` | int, required | age at the start of the policy year |
| `date_of_birth` | `YYYY-MM-DD`, a real calendar date (`2026-13-40` fails) | only when the exact date is load-bearing (two-child-limit protection, state pension age) |
| `employment_income` | number ≥ 0 | gross annual employee earnings |
| `self_employment_income` | number ≥ 0 | annual trading profit |
| `pension_income` | number ≥ 0 | private/occupational pension in payment |
| `state_pension` | number ≥ 0 | annual state pension in payment |
| `savings_income` | number ≥ 0 | annual interest income |
| `capital` | number ≥ 0 | liquid capital / savings stock |
| `employee_pension_contributions` | number ≥ 0 | annual employee pension contributions; `salary_sacrifice` true means they reduce gross pay for tax and NI |
| `salary_sacrifice` | bool | pension contributions are via salary sacrifice |
| `is_disabled` | bool | disabled for benefit purposes (drives disability elements/premia; the connector maps to each engine's disability concept and records the mapping) |
| `is_carer` | bool | provides ≥ 35 hours/week care for a disabled person (Carer's Allowance / UC carer element eligibility) |
| `gainfully_self_employed` | bool | in gainful self-employment for UC (minimum income floor applies after the start-up period) |
| `hours_worked_per_week` | number ≥ 0 | contracted weekly hours |

Household keys (closed set): `people`, `benefit_units`, `region`, `tenure`
(`owned_outright` | `owned_mortgage` | `rented_social` | `rented_private`),
`rent` (annual), `council_tax` (annual, optional), `brma`. `region` uses
the target country's own geography vocabulary (UK: ITL-1 slugs like
`LONDON`, `SCOTLAND`; US: state codes) — it is what routes devolved policy
(Scottish income tax, Scottish Child Payment; US state taxes) and the
benefit-cap tier. It is a CLOSED registry (`VALID_REGIONS`), never free
text: an unrecognised region would otherwise reach a connector that
silently falls back to a default.

`brma` is REQUIRED on a UK `rented_private` case and forbidden elsewhere.
Local Housing Allowance rates are set per Broad Rental Market Area, not
per ITL-1 region, so a region alone does not fix the world the two engines
run — "the rent clears the cap in most Yorkshire BRMAs" is not a pinned
comparison. `BRMA_REGION` is the registry, and each entry names the region
it sits in, so a case cannot pin a BRMA outside its own region.

`expected_focus` is likewise closed per country (`FOCUS_VARIABLES`): it
names the output variables the case is curated to exercise, and a name no
connector maps produces no comparison at all rather than an error.

Amounts must be FINITE. NaN silently defeats every comparison operator,
and an infinite rent produces an infinite entitlement rather than a
failure.

### `baseline` — the policy world a case is evaluated in

Optional; absent means current law. A descriptor of the same shape
`ReformRef.baseline` carries, and it must already be REGISTERED in
`scorecard_db/baselines.py` — an unnamed counterfactual is exactly the
"which law did this run?" ambiguity mode 3 exists to remove.

This is how a case pins a SAME-YEAR counterfactual instead of leaning on a
year-on-year delta. The two-child-limit family uses it: three 2026 cases,
`uk-uc-two-child-limit-binding` and `uk-uc-two-child-limit-multiple-birth`
in the registered `pre_ab2025` world (limit reinstated at two children)
and `uk-uc-two-child-limit-abolished` under current law. The binding /
abolished pair differs only in the world, so it attributes the abolition;
the binding / multiple-birth pair differs only in `child_3`'s date of
birth, so it attributes the exception. An earlier design paired a 2025
case against a 2026 one, which moved ages, uprated rates and the policy
year together, and used twins in the "limit in force" case — where an
engine that wrongly kept the limit but rightly applied the multiple-birth
exception still paid three elements and passed.

## Result row — `CaseResult`

One row per case × output variable × run. History is preserved: re-running
on a new engine or oracle version appends, never overwrites (same doctrine
as `pe_results`).

`variable_class` and `schema_version` are REQUIRED. Both used to be
omissible, and an omitted `schema_version` defaulted to the current one —
precisely the silent reinterpretation the field exists to prevent.
`engine_version` and `oracle_version` may not be blank. A boolean-class
comparison may only carry 0 or 1 on either side.

### The classify → CaseResult seam is enforced, not conventional

`CaseResult.__post_init__` RECOMPUTES `classify()` and compares. A stored
classification is valid only if it is what the classifier says, or if it
is an ADJUDICATION of a row the classifier left `unclassified`, drawn from
`ADJUDICATABLE` (`oracle_difference`, `rounding`, `pe_gap`,
`policy_scope_mismatch`) and carrying a writeup in `annotations`. A row
the classifier has already decided is not up for reinterpretation, and
nothing may be adjudicated INTO a match.

Note the two-sidedness of `pe_gap` and `policy_scope_mismatch`: the
classifier emits them mechanically for a null side, and a human may also
assign them to a numeric-vs-numeric difference — where they are a
judgement and need explaining. Previously only `oracle_difference` and
`rounding` demanded a writeup, so `100` vs `200` could be filed as a
`pe_gap` with nothing said.

Tolerances come from `DEFAULT_TOLERANCES` alone. `from_classification`
no longer accepts a tolerance table and a hand-written row carrying a
tolerance other than the registered one is rejected — a caller-supplied
tolerance is how a boolean `1` vs `0` became a `match_within_tolerance`.
`from_classification` does accept `annotations`, because some lanes
require one (the #64 calculator rows must carry an archive annotation).

### Calculator oracles carry structured reading provenance

A live calculator has no release version, so a `CaseResult` from one must
carry a `reading` (`CalculatorReading`): the reading date as a real
calendar date, the exact `https` page read, the tax/benefit year the
SERVICE computed, where the archived screenshot / saved page lives, and
sha256 digests of both the archived bytes and the canonical input vector.
A date buried in free-text `oracle_version` is a string, not provenance —
any ten-character chunk passed, and a bare `annotations=["archive:"]`
satisfied the citation rule. The `oracle_version` date must now be the
reading's own, the archive annotation must cite the reading's own
`archive_ref`, and a reading may not postdate its row.

`CALCULATOR_POLICY_YEARS` declares which years each service actually
computes. GOV.UK's income-tax estimator serves only the current tax year,
so a 2025 case pointed at it would return a confident number for a year it
never calculates: both the work list and each row are checked against it.
For the same reason a case evaluated in a registered non-current-law
world (the `pre_ab2025` two-child cases) can never be a calculator entry —
production calculators compute current law only.

`validate_results(results, cases)` checks a run against the battery it
claims to be from: a result must name a case that exists and a variable
that case's `expected_focus` asks for.

### Every oracle's epistemic standing is assigned, with evidence

`ORACLE_BENCHMARK` gives each oracle a `benchmark_class` and a
`calibration_relationship` plus the publisher evidence behind them, and
both land on the row. All are `different_model` + `held_out`: GOV.UK
describes its own tools' outputs as ESTIMATES and explicitly lists
Entitledto, Turn2us and Policy in Practice among INDEPENDENT benefits
calculators, so none of them is an authority PE is fitted to — and nothing
in pe-uk-data or policyengine-uk consumes any of them. The assignment is
per oracle, never one umbrella "official" claim, and a caller cannot
relabel a calculator as authoritative.

### Not yet built

There is no case/result TABLE, writer, exporter or `build_db` step, so
mode-3 rows do not persist to the DB yet. The epistemic wiring that rides
on those columns — `calibration_relationship`, the executed baseline key,
case/battery digests, engine bundle and run pins, the JRC connector
revision, and a citable adjudication link — lands with that table, as does
splitting the descriptive comparison status from the normative diagnosis
the way `external_scores` and `diagnoses` already do. That design has
repo-wide surface and is being paired on rather than decided here.

```json
{
  "case_id": "uk-uc-single-unemployed",
  "variable": "universal_credit",
  "pe_value": 4796.48,
  "oracle_value": 4796.52,
  "oracle": "ukmod",
  "engine_version": "policyengine-uk 2.x.y",
  "oracle_version": "UKMOD B2026.08 / EUROMOD I7.0+",
  "computed_at": "2026-08-14T12:00:00Z",
  "abs_diff": 0.04,
  "tolerance": 0.52,
  "variable_class": "currency",
  "classification": "match_within_tolerance",
  "schema_version": 1
}
```

- `variable` — canonical output name in PE's vocabulary for the case's
  country (`universal_credit`, `income_tax`, `national_insurance`,
  `child_benefit`, `pension_credit`, …). The connector's mapping table
  pairs it with the oracle's variable (UKMOD `bsauc_s`, etc.) and records
  any construction (e.g. summing UKMOD monthly output × 12).
- `oracle` — closed set: the model oracles `ukmod` and `taxsim`, plus the
  official-calculator oracles (#63) `govuk_income_tax_estimator`,
  `govuk_hicbc_calculator`, `policy_in_practice_boc`, `entitledto`,
  `turn2us`; grows with #5.
- `pe_value` / `oracle_value` — annual amounts (booleans as 0/1). `null`
  means that side cannot produce the variable: `pe_value: null` ⇒
  `pe_gap`; `oracle_value: null` ⇒ `policy_scope_mismatch` (the oracle
  does not model it — e.g. TAXSIM has no benefits; UKMOD's UK model omits
  some devolved payments depending on version).
- `abs_diff` — `|pe_value − oracle_value|` when both sides are numeric,
  else `null`. Stored, not derived at read time, so the miss table is
  self-contained.
- `tolerance` — required on (and only on) `match_within_tolerance` rows:
  the numeric tolerance the row was judged against, satisfying
  `0 < abs_diff ≤ tolerance`. Stored so a tolerance-table change can never
  silently re-bless old rows.
- `variable_class` — which tolerance rule applied (`currency` /
  `boolean`), persisted so a stored row can be re-classified and
  audited without inferring the class from the free-text `variable`.
- `schema_version` — this contract's version (currently `1`), on the
  battery file and every result row; a mismatched version raises, so
  a future breaking change migrates stored artifacts explicitly.
- Connectors build rows via `CaseResult.from_classification(...)` —
  the one wiring path from `classify` to a stored row. It derives
  `abs_diff`, threads the exact tolerance `classify` judged against,
  and persists `variable_class`, so no caller re-derives the
  tolerance by hand.
- `annotations` — a list of non-empty strings. Required (non-empty) on the
  adjudicated-only classifications `oracle_difference` and `rounding`: the
  traceable writeup naming the oracle defect / documented rounding rule.
  A row claiming either without a writeup fails validation.

## Classification (closed set — fail loud)

| classification | meaning | assigned by |
|---|---|---|
| `match_exact` | values identical | classifier |
| `match_within_tolerance` | nonzero diff ≤ the variable class's tolerance | classifier |
| `pe_gap` | PE cannot produce the variable, or adjudication found PE wrong | classifier (null side) / adjudication |
| `oracle_difference` | adjudication found the oracle wrong (upstream report filed) | adjudication |
| `policy_scope_mismatch` | the two engines model different policy scope for this variable (documented) | classifier (null side) / adjudication |
| `rounding` | diff fully explained by the oracle's documented rounding rules (e.g. UKMOD monthly rounding × 12) | adjudication |
| `unclassified` | diff above tolerance, not yet adjudicated | classifier (default) |

The classifier (`case_diffs.classify`) only ever emits `match_exact`,
`match_within_tolerance`, `pe_gap` / `policy_scope_mismatch` (null sides),
or `unclassified`. Every `unclassified` row is a work item: adjudication —
the diagnosis stage, human-or-agent, with a traceable writeup — moves it to
`pe_gap`, `oracle_difference`, `policy_scope_mismatch`, or `rounding`.
Nothing defaults to a flattering bucket; misses stay visible, exactly as in
modes 1–2. Unknown classification strings raise. The writeup requirement is
enforced at validation: `oracle_difference` and `rounding` rows raise
without a non-empty `annotations` writeup, and `match_within_tolerance`
rows raise without the `tolerance` they were judged against.

## Tolerances (per variable class)

| variable class | tolerance | rationale |
|---|---|---|
| `currency` | £0.01/week ⇒ **0.52/year** (same rule in USD for TAXSIM) | benefit rules are stated weekly to the penny; comparisons are annual, so 52 × 0.01. A wider tolerance is allowed only with a documented oracle rounding rule, and then the adjudicated class is `rounding`, not a silent tolerance bump. |
| `boolean` | exact (0) | eligibility flags either agree or they don't |

The tolerance table is data (`DEFAULT_TOLERANCES`), passed to `classify`
explicitly; a variable class missing from the table raises rather than
guessing.

## Official-calculator oracles (#63)

Calculator oracles are live services (gov.uk estimators; production benefit
calculators), not versioned model releases, so their result rows carry a
stricter provenance contract, enforced at validation:

- `oracle_version` **must contain the reading date** (`YYYY-MM-DD`, a
  real calendar date — `2026-13-45` fails validation) — a calculator
  answer is only meaningful with the date it was read.
- Every reading must be **archived** (screenshot or saved page) and the
  archive cited in `annotations` as an `archive: <path-or-url>` entry —
  a calculator-oracle row **without** an `archive:` annotation fails
  validation, so this rule is enforced, not prose. Readings are
  entered manually or via documented, terms-compliant access — one case at
  a time; these are oracle *readings*, never a harvest or a scrape.
- The starter work list lives in `battery/calculator_set.json`
  (`load_calculator_set`): each entry names a battery case and the ≥ 2
  calculators it is to be entered into, so a PE-vs-UKMOD disagreement
  always has an adjudicating third reading. Entries are inputs only —
  results arrive as ordinary `CaseResult` rows.

## What this lane still needs (out of scope here)

The JRC connector run (runnable per axiom-oracles#264, needs the UKMOD
environment): map the vocabulary to UKMOD input variables, execute the
battery on both engines, append `CaseResult` rows, publish the miss table,
and advance the lane. Until then the battery is inputs + focus only, by
design.
