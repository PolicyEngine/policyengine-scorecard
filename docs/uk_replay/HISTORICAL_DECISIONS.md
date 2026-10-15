# Historical replay methodology decisions (cos d1344)

On 15 October 2026 Max decided cos d1344: the methodology calls the Budget
CI plan raises are made by the workstream sessions. Each call needs an
independent review that agrees, and its exceptions must be recorded. This
file records the two calls phase 0 left pending for Spring Statement 2022,
Autumn Statement 2022 and Autumn Budget 2021: the readings considered, the
choice, the reasons and the exceptions. The selectors bind each choice, and
this record, by SHA-256.

Every source cell cited below was read in the locked bytes, and each file's
SHA-256 matched its lock, unless marked otherwise.

## 1. Policy world: `published_end_state_same_weights.v1`

The readings, from [POLICY_WORLD_CONTRACT.md](POLICY_WORLD_CONTRACT.md):

- **A. Published end state, same weights.** Calibrate each scoring year to
  the event's published post-measures world once, then evaluate a sourced
  pre-measures counterfactual on the same records and weights.
- **B. Documented pre-measures bridge.** Calibrate a pre-measures world built
  from a publisher-evidenced level bridge, then apply the announcement on the
  same records and weights.

**Chosen: A, for all three events**
([contract](contracts/published_end_state_same_weights.v1.md)). Why:

- **A needs no constructed bridge.** B needs a complete pre-measures
  programme, head and year level series. Among the locked sources reviewed
  in phase 0, none supplies one.
  - The pre-measures series that exist are aggregates. In the November 2022
    charts and tables workbook they are `C.1`, `C.2`, `C.8`, `C.11`, `C.15`,
    `C.16`, `C.17`, `C.18`, `C.21` and `C.D`, the fiscal-target comparisons
    in `T.7`, and the indirect-effects rows of `T.1`, `T.5` and `C.20`
    (found by a scan of every sheet for "pre-measures" and "indirect
    effects").
  - `C.16!B34/B43` and `C.18!B35/B39` label pre- and post-measures series on
    the tax-to-GDP and spending-to-GDP charts.
- **The plan rules out a bridge built from the costings.**
  [PLAN.md](PLAN.md) treats the OBR's costings as held-out comparisons,
  never inputs. A bridge built from them would turn the comparison into an
  input.
- **The welfare levels are post-measures where the sources say so.** Each
  event's expenditure workbook titles `3.7!B2` "3.7 Post measures breakdown
  of welfare spending". But not every published level is post-measures, so
  targets are classified one by one (contract term 2):
  - the Scottish Block Grant adjustments are "consistent with pre-measures
    forecasts" (`3.4!B38`, March 2022 and October 2021);
  - the March 2022 devolved costings "are included in our pre-measures
    forecast" (Annex A `TA.4!B12`);
  - none of the three receipts workbooks labels a pre- or post-measures
    basis;
  - a lead for any future Option B, outside the locks: the Autumn Statement
    2022 DWP edition says the OBR's 25 November 2022 supplementary caseloads
    (PIP, DLA, UC LCW and LCWRA, ESA) were pre-measures (`Notes!B12`).

Neither option makes the comparison independent of calibration.
- Under A, the calibrated post-measures aggregate equals the OBR's
  pre-measures level plus its costings and the indirect effects of policy. So for a measure acting on that
  aggregate, PolicyEngine's divergence from the OBR reappears as a level gap
  in the uncalibrated pre-measures world.
- Under B, the same divergence would appear in the post-measures world.
- Under A it is recorded: such comparisons carry the `calibrated_aggregate`
  tag (contract term 10).

**Recorded exceptions**

1. **The published world is not the engine's current law.** It runs the
   event's law and forecast uprating, with the policies it contains recorded
   (contract term 1).
   - Example: the March 2022 Annex A `TA.2!C9` cuts the basic rate to 19%
     from April 2024, while policyengine-uk 2.130.1 holds 20% throughout.
   - Running current law instead would push the policy gap into the weights.
2. **Targets from sources other than the event-day file are flagged.** These
   are:
   - Autumn Budget 2021's receipts workbook, a later revision (modified
     28 October 2021);
   - the March 2025 historical forecasts database rows, a later revision for
     all three events;
   - the DWP outturn and forecast editions, published after each event
     (24 May 2022, 21 December 2022 and 19 November 2021), with capture
     status `unknown`.
3. **Autumn Budget 2021's release-equivalence review is waived for the
   policy-world choice, not for its targets.**
   - The proposal made that review a precondition for extending the contract
     to Autumn Budget 2021.
   - The policy-world question is answered by `3.7`, which is labelled post
     measures in a file that predates the event.
   - The review is still required before any value from the later-revision
     receipts workbook becomes a target.
4. **Autumn Statement 2022's event-day files lack 39 tables**: 15 deferred,
   and 24 not produced for that forecast ([VINTAGE_LOCKS.md](VINTAGE_LOCKS.md)).
   Those tables supply no targets.
5. **Cash-basis receipts are not calibration targets** until a documented
   cash-to-liability bridge exists. Until then they stay held-out level
   comparisons.
6. **Macro inputs differ in vintage.** The published world uses
   post-measures macro inputs, while the OBR costs measures against its
   pre-measures forecast. Comparisons carry the `macro_vintage` tag.
7. **Counterfactuals are constructed per measure.** Where a counterfactual
   cannot express the announcement, the measure is a recorded gap, not a
   forced number.

## 2. Annualisation bridge: `fy_start_year.v1`

The readings:

- **Fiscal-year start, day-weighted within the year.** Fiscal year Y–(Y+1)
  maps to the engine's period Y. A flow parameter whose law changes within
  that fiscal year takes its day-weighted fiscal-year value in period Y.
- **Fiscal-year start with the engine's default sampling.** The value in
  force on 30 April Y applies to the whole of period Y.
- **Two-period blend.** Fiscal year Y–(Y+1) is 9/12 of period Y plus 3/12
  of period Y+1.

**Chosen: the first**
([receipt](contracts/annualisation_fy_start_year.v1.json)). Why:

- **The engine already treats period Y as the fiscal year from 6 April Y.**
  In policyengine-uk 2.125.1 and 2.130.1, `convert_to_fiscal_year_parameters`
  works as follows:
  - it samples parameters at 30 April Y by default;
  - it day-weights the six files flagged `fiscal_year_blend` (CGT rates and
    fuel duty in 2.130.1);
  - it keeps statutory dates for the files flagged `preserve_calendar_dates`
    (33 in 2.130.1, including the energy price cap and guarantee; 32 in
    2.125.1).

  The legacy 2.89.2 samples the same way ([YEARS.md](YEARS.md)).
  policyengine.py#617 certifies 2.130.1 with policyengine-uk-data 1.58.1;
  2.130.1 is not yet a scorecard replay variant.
- **The 30 April sample alone would contaminate calibration.** It keeps a
  mid-year change out of period Y, while the OBR's fiscal-year level
  includes it. Examples:
  - the National Insurance primary threshold rise from July 2022 (March
    2022 Annex A `TA.2!C7`) is sampled at £190 a week in 2.130.1, whose
    timeline keys the rise at 1 July 2022 although its own comment says
    6 July (intended values therefore come from the statute, not the
    engine's timeline);
  - the Universal Credit taper cut from late 2021 (October 2021 Annex A
    `TA.2!C21`) is sampled at 63% for period 2021;
  - the Health and Social Care Levy, repealed for earnings paid from
    6 November 2022, is sampled as in force for period 2022 (2.130.1's own
    tests).

  Calibrating those years would push each change into the weights.
  Day-weighting flow parameters is the engine's own rule for them. Where a
  change cannot be expressed this way, the targets it moves are flagged and
  excluded from that year's calibration.
- **The blend would mix fiscal years.** It would apply fiscal year Y+1's
  policy to January to March of fiscal year Y–(Y+1).

**Recorded exceptions**

- **Reform routes differ by entry point.** In 2.130.1 a reform passed when
  the simulation is constructed goes onto the statutory timeline and is
  reprocessed. `Scenario.apply` on a built simulation, in either engine,
  edits the annualised parameters, read at 1 January. `parameter_changes`
  apply to every period. So every population run must:
  - record each changed parameter's processed period-Y value against its
    intended value;
  - refuse a mismatch;
  - re-read this evidence for the engine actually certified.
- **Population inputs.** Period Y's inputs are annual projections, so every
  comparison keeps the `cy_proxies_fy` tag.
- **Part-year effects.** Cash-versus-liability timing and part-year effects
  are recorded per measure. No part-year coverage is claimed from an annual
  result.

## Effect

The three selectors move from `contracts_pending` to
`ready_for_population_build`. They bind the contract, the bridge receipt and
this record by SHA-256. That readiness means only that the methodology
fields are resolved. Before a population runs, it still needs:
- its licensed survey receipt;
- a target compilation under the contract, including the published world's
  recorded policy list;
- the processed-value check;
- certification with the engine actually used.
