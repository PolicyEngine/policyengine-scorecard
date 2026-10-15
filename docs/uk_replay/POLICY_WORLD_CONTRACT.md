# Policy-world contract for the 2022 events

**Decided under cos d1344: Option A**, `published_end_state_same_weights.v1`,
for all three events. Max decided d1344 on 15 October 2026, delegating the
call to the workstream with independent review. The
[decision record](HISTORICAL_DECISIONS.md) gives both readings and the
reasons, and the [contract](contracts/published_end_state_same_weights.v1.md)
states the terms the [selectors](selectors/) bind by digest. This page is the
proposal as written before the decision; it builds no population and
establishes no historical engine's policy schedules.

The two alternatives come from [PLAN.md](PLAN.md), read at scorecard commit
`61c13e38cfe4676756a7857e4fc6f67eac33cd0c`. The fetched files now confirm that
the 2022 expenditure tables describe post-measures welfare levels. Original
launch equivalence is a separate question recorded in the locks, not assumed
from the event label or an early archive timestamp.

## Option A: published end-state with fixed weights

Contract id proposed: `published_end_state_same_weights.v1`.

For each event and scoring FY, pin the event's forecast inputs and admissible
historical survey edition, map approved administrative and forecast level
targets to the published policy world, and calibrate that world once. Record
which announced and already-announced policies it contains. Freeze the
resulting records, non-policy inputs, claimant assignment and weights for the
comparison. Apply a separately sourced pre-measure schedule to the same
population; do not reweight that counterfactual to the released post-measures
level. Weights can differ between scoring FYs, but not between the compared
policy worlds within a FY.

The pre-measure schedule must specify the event's counterfactual, previous
policy announcements and package interactions. It cannot be inferred from
today's default law or from a parameter's earliest key. The
[historical-rule audit](HISTORICAL_RULES.md) names the remaining schedule and
annual-processing checks. Changing a policy world must use an audited input
and parameter path and preserve the documented take-up/behaviour convention.
Whether a future engine can perform every required reversal remains unverified.

For a reversal from the published world, retain the literal counterfactual
minus published result. Present the announcement effect in pre-to-post order,
with positive numbers meaning gains to the Exchequer: tax increases are
positive; spending increases are negative. [RECIPE.md](RECIPE.md#construction-patterns)
at the checkpoint supplies this orientation and the existing source-head
accounting contract. A package's interaction and omitted legs remain explicit;
its policy costings are held-out comparisons.

## Option B: documented pre-measures level bridge

Contract id proposed: `documented_pre_measures_bridge.v1`.

Obtain a publisher-evidenced pre-measures level series or a reviewed bridge
from published levels to that world. It must identify the forecast release,
every relevant programme/head/FY, policy boundary, units, geography, cash
versus liability treatment and any indirect macro or behavioural assumptions.
Preserve the bridge's source cells, arithmetic, exclusions and receipt digest.
Calibrate the resulting pre-measures world once, then apply the announcement
on the same records and weights. A macro pre/post series alone does not supply
programme welfare or tax-liability levels.

Do not construct this bridge by subtracting the held-out OBR measure costings
or summing PMD rows until a desired delta emerges. Doing so would put the
comparison signal into the targets. If a proposed publisher-derived bridge
consumes a specific costing as an input, that costing is no longer an
independent holdout and must be excluded from held-out comparisons. An
aggregate sources-of-change table also needs reconciliation before it can
serve as a complete level bridge; it cannot identify a distribution around
tax thresholds or reconstruct claimant transitions by itself.

## What the source locks establish

Each event has all six required roles in its
[committed lock](../../data/uk/events/vintage_locks/): economy, receipts,
expenditure, policy tables, selected HOFD forecast rows and a DWP benefit
expenditure/caseload edition. The byte digests, exact replay URLs, sheet names
and edition caveats are in those receipts. The
[cell evidence](evidence/vintage_policy_world_sources.json) records the read
titles and coordinates behind the conclusions below.

| Event | Verified source support | What Option B still needs |
|---|---|---|
| Spring Statement 2022 | March 2022 economy/receipts, expenditure and Annex A workbooks; historical HOFD row; Spring Statement DWP edition. Expenditure `3.7!B2` is “3.7 Post measures breakdown of welfare spending”; `3.8!B2` names sources of changes in welfare spending. | A complete pre-measures programme/head/FY level bridge; completeness and distributional controls are unverified. |
| Autumn Statement 2022 | November 2022 economy/receipts, expenditure and charts/tables workbooks; historical HOFD row; Autumn Statement DWP edition. Expenditure `3.7!B2` has the same post-measures title; `3.8!B2` describes changes since March 2022. Charts `C.16!B34/B43` and `C.18!B35/B39` distinguish pre/post-measures macro series. | Evidence that the pre/post labels reconcile to all required programme/head/FY levels, including intervening policy announcements. Such a complete bridge has not been established. |
| Autumn Budget 2021 | October 2021 economy/receipts, expenditure and Annex A workbooks; historical HOFD row; Autumn Budget DWP edition. Expenditure `3.7!B2` explicitly labels its welfare breakdown post measures. The receipts workbook was saved after the event and is labelled a later revision; numerical equivalence with launch bytes is unverified. | The same programme-level bridge and release-equivalence review before extending the contract to this predecessor pilot. |

The post-measures titles were read from the
[March 2022 expenditure capture](https://web.archive.org/web/20220323220800id_/https://obr.uk/docs/dlm_uploads/Fiscal_Supplementary_Tables_Expenditure_March_2022.xlsx)
and the
[November 2022 expenditure capture](https://web.archive.org/web/20221117131030id_/https://obr.uk/docs/dlm_uploads/Fiscal_supplementary_tables_expenditure_November_2022.xlsx).
The pre/post macro labels were read from the
[November 2022 charts capture](https://web.archive.org/web/20221117122512id_/https://obr.uk/docs/dlm_uploads/Economic_and_fiscal_outlook_charts_and_tables_November_2022.xlsx).
These statements do not assert that every numeric source cell has been
reconciled to a model variable.

The [October 2021 expenditure capture](https://web.archive.org/web/20211101172726id_/https://obr.uk/download/october-2021-economic-and-fiscal-outlook-supplementary-fiscal-tables-expenditure/)
also has the post-measures welfare title. Its `3.4!B38`, and the same cell in
March 2022, describe Scottish Block Grant adjustments as pre-measures-consistent
and say a later update will align them with the post-measures forecast. Policy
worlds therefore need classification per target, not one assumption for an
entire workbook. These public-budget adjustments do not supply a household
welfare bridge.

The welfare change tables contain grouped channels and direct government
decision effects. November 2022 `3.8!B8` literally labels its new forecast
“October 22 forecast”, while the workbook is the November edition. Preserve
that source-label anomaly and verify its interpretation before compiling
targets; do not silently correct it. Neither grouped changes nor direct
policy-effect rows have been established here as an independent, complete
pre-measures target bridge.

The locked HOFD is the March 2025 cross-vintage database, explicitly a later
database edition selecting historical event-labelled forecast rows, not its
latest outturn. The DWP files are later auxiliary publications tied by title
to the event forecast: the existing publication receipts record 24 May 2022,
21 December 2022 and 19 November 2021 respectively. They are not evidence of
event-day availability. DWP captures in 2025 for the two 2022 files do not
establish original-launch byte equivalence; both remain `unknown`. The
[source-lock note](VINTAGE_LOCKS.md) explains this revision convention.

## Recommendation and acceptance requirements

Choose Option A for the 2022 pilot, subject to the methodology call. It uses
the explicitly published post-measures welfare surface, preserves a single
weight vector for each comparison and avoids an unevidenced subtraction
bridge. Retain Option B when a complete independent level bridge has been
documented. The presence of pre/post macro labels makes further source review
worthwhile, but does not yet justify a programme-level bridge contract.

Approval should specify the covered targets and heads, policy-boundary
schedule, release/revision convention, take-up and behaviour treatment,
geographical mapping and annualisation and cash/liability bridges. The
same-world target compilation must keep administrative observations distinct
from forecasts and exclude survey-derived tax-benefit quantities under
[ARCHITECTURE.md](../ARCHITECTURE.md#what-may-never-become-a-target). No reform
gets separate calibration to force its OBR delta. Missing income-distribution
forecasts, unsupported heads, behavioural channels and part-year effects
remain recorded gaps.

After a decision, digest the approved contract, resolve the selectors, pin
the licensed historical inputs, and certify each resulting population with
the engine actually used. The [population manifest](POPULATION_MANIFEST.md)
and [adapter design](HISTORICAL_ADAPTER.md) describe that join. No target
compiler, bridge, historical population or new certification is delivered
by this proposal.
