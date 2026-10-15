# Event vintage selector contract

The [v1 schema](schemas/event_vintage_selector.v1.json) binds an event to
one OBR release, its source receipts, every original scoring FY and the
historical surveys published before the event. The three
[selectors](selectors/) bind the methodology decisions made under cos d1344
([HISTORICAL_DECISIONS.md](HISTORICAL_DECISIONS.md)); they are not
population builds. Their release choices and dates follow
[PLAN.md](PLAN.md) and [POPULATIONS_AND_VINTAGES.md](POPULATIONS_AND_VINTAGES.md)
at scorecard commit `61c13e38cfe4676756a7857e4fc6f67eac33cd0c`.

## Fields and gates

`event_slug` is the inventory's `event_key`. `event_date` is the announcement
date. `forecast_vintage` identifies the EFO publication, separately from
the years it forecasts. `scoring_fys` is the ordered union of the event's
`costing_gbp_m` keys in [inventory.jsonl](../../data/uk/events/inventory.jsonl),
including zero cells and years unsupported by the current executor.

`source_locks` names committed lock paths and their `receipt_sha256` values.
That digest uses the collector's canonical JSON convention, not the
pretty-printed lock file's byte hash. Each referenced source also carries
its role, retrieval status and file digest. An unavailable file has an
explicit null digest; it does not acquire another vintage's bytes. All six
core roles remain visible. Capture dates do not establish publication dates
or original-launch equivalence. A later HOFD database can supply a named
historical forecast row, but its current outturn row cannot replace it.

`admissible_survey_releases` lists the reviewed FRS candidates for this
slice, not every older survey in existence. `preferred_survey_release`
records the plan's choice. FRS 2019–20 was published on 25 March 2021 and is
the choice for Autumn Budget 2021 and Spring Statement 2022. FRS 2020–21
was published on 31 March 2022, after the 23 March Spring Statement, and
is admissible only for Autumn Statement 2022 among these events. Earlier
FRS releases require their own release review before addition.

These dates describe statistical publication, as recorded in the plan. They
do not pin the licensed UK Data Service microdata edition. Original microdata
availability for FRS 2019–20 remains unverified; the FRS 2020–21 microdata
notice is dated 10 June 2022. Both original-edition byte identities remain
unverified. The [FRS requirements](HISTORICAL_FRS.md) distinguish those access
and edition questions. A population build must supply its licensed-source
receipt before the preferred survey generation becomes an executable input.

`policy_world_contract` is either an approved contract id and digest or
`status: "pending", value: "pending"`, with the
[proposal](POLICY_WORLD_CONTRACT.md) and decision `cos d1344`. All three
selectors now bind `published_end_state_same_weights.v1` by the SHA-256 of
[its contract](contracts/published_end_state_same_weights.v1.md). The two allowed
contract ids are `published_end_state_same_weights.v1` and
`documented_pre_measures_bridge.v1`. `annualisation_bridge` likewise needs a
reviewed id/receipt, or a pending pointer to the
[adapter design](HISTORICAL_ADAPTER.md); the selectors bind `fy_start_year.v1`
by the SHA-256 of [its receipt](contracts/annualisation_fy_start_year.v1.json).
Neither pending value is a default.

JSON Schema checks shape, enums, digests and date formats. The offline
tests additionally check inventory FY equality, source-lock identity and
role coverage, valid successive-year FY labels, preferred-survey membership
and strict publication-before-event ordering. A runtime consumer must repeat
those semantic gates, inspect source availability and revision conventions,
and refuse unresolved contracts. `ready_for_population_build` means both
methodology fields are resolved; it does not certify an artifact or promise
complete target coverage.

## Rechecking

Run the collector's offline check and the contract tests with the designated
Python interpreter. No survey files or model imports are required:

```bash
python data/uk/events/collect_vintage_locks.py --check
python -m pytest --noconftest tests/test_uk_vintage_locks.py
```
