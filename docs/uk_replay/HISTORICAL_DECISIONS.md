# Historical replay methodology decisions (cos d1344)

On 15 October 2026 Max decided cos d1344: the methodology calls the Budget
CI plan raises are made by the workstream sessions, each with an independent
review that agrees and with exceptions recorded. This file records the two
calls phase 0 left pending for Spring Statement 2022, Autumn Statement 2022
and Autumn Budget 2021, the readings considered, the choice and why. The
selectors bind each choice by digest.

## 1. Policy world: `published_end_state_same_weights.v1`

The readings, from [POLICY_WORLD_CONTRACT.md](POLICY_WORLD_CONTRACT.md):

- **A. Published end state, same weights.** Calibrate each scoring year to the
  event's published world once, then evaluate a sourced pre-measures
  counterfactual on the same records and weights.
- **B. Documented pre-measures bridge.** Calibrate to a pre-measures world
  built from a publisher-evidenced level bridge, then apply the announcement.

**Chosen: A, for all three events**
([contract](contracts/published_end_state_same_weights.v1.md)). Why:

- **It is the world the sources publish.** Each event's expenditure workbook
  labels its welfare breakdown post measures: `3.7!B2` reads "3.7 Post
  measures breakdown of welfare spending" in the locked March 2022, November
  2022 and October 2021 files (verified in the locked bytes). The levels a
  replay can calibrate to are therefore post-measures levels.
- **B has no source.** Among the locked sources reviewed in phase 0, none
  supplies a complete pre-measures programme, head and year level series.
  November 2022 carries pre/post-measures labels only on its aggregate
  tax-to-GDP and spending-to-GDP charts (`C.16!B34/B43`, `C.18!B35/B39`,
  verified in the locked bytes). Building the bridge from the OBR's own
  measure costings would put the held-out comparison into the targets.
- **Both hold weights fixed; they differ in which world is calibrated.** A
  calibrates the world the sources describe and constructs the
  counterfactual; B would calibrate a world no locked source describes. With
  either, one weight vector per scoring year keeps each reform effect on
  fixed records, as the modern replays do.

**Recorded exceptions**

- **Autumn Budget 2021.** Its receipts workbook is a later revision (modified
  28 October 2021). Targets from it carry the `later_revision` flag. Their
  numerical equivalence with launch bytes stays unverified.
- **Autumn Statement 2022.** Its event-day files lack 39 tables (15 deferred,
  24 not produced for that forecast; see [VINTAGE_LOCKS.md](VINTAGE_LOCKS.md)).
  Those tables supply no targets.
- **The counterfactual.** A's counterfactual schedule is constructed per
  measure. Where it cannot express the announcement, the measure is a
  recorded gap, not a forced number.

## 2. Annualisation bridge: `fy_start_year.v1`

The readings:

- **Fiscal-year start.** Fiscal year Y–(Y+1) maps to the engine's period Y.
- **Two-period blend.** Fiscal year Y–(Y+1) is 9/12 of period Y plus 3/12 of
  period Y+1.

**Chosen: the fiscal-year start**
([receipt](contracts/annualisation_fy_start_year.v1.json)). Why:

- **The engine already treats period Y as the fiscal year from 6 April Y.**
  In policyengine-uk 2.125.1 and in 2.130.1 (the current certified pair),
  `convert_to_fiscal_year_parameters` samples each government parameter at
  30 April Y for period Y. It day-weights the parameters flagged
  `fiscal_year_blend` across the fiscal year (six parameter files in
  2.130.1). The legacy 2.89.2 does the same ([YEARS.md](YEARS.md)).
- **The blend would mix fiscal years.** Blending two periods would combine
  two fiscal years' policy and repeat an April-to-March split the engine has
  already made.

**Recorded exceptions**

- **Population inputs.** Period Y's inputs are annual projections, so every
  comparison keeps the `cy_proxies_fy` axis.
- **Timing.** Cash-versus-liability timing and measures commencing after
  30 April are recorded per measure.
- **No part-year claims.** Part-year coverage is never claimed from an annual
  result.

## Effect

The three selectors move from `contracts_pending` to
`ready_for_population_build`, binding both choices by SHA-256. That readiness
means only that the methodology fields are resolved. Each population still
needs its licensed survey receipt, a target compilation under the contract,
and certification with the engine actually used before it runs.
