# Contract `published_end_state_same_weights.v1`

The policy-world contract for vintage-faithful replays of Spring Statement
2022, Autumn Statement 2022 and Autumn Budget 2021, chosen under cos d1344
([decision record](../HISTORICAL_DECISIONS.md)). A selector binds this file
by its SHA-256; any change to these terms is a new contract version.

## Terms

1. **Published world: the event's own law and forecast.** For each event and
   scoring fiscal year, the published world is the post-measures world of the
   event's OBR forecast, read from the event's committed
   [source locks](../../../data/uk/events/vintage_locks/).
   - **Law.** The engine runs that world's law, not its own current law where
     the two differ. That law is the policy schedule as it stood at the event:
     the event's measures with their announced dates, plus policy announced
     earlier.
   - **Uprating.** The uprating inputs are the event's forecast, not later
     outturn.
   - **Recorded policy list.** Each event's target compilation records the
     policies its published world contains and the audited parameter or
     input path that sets each one. For example, the Spring Statement 2022
     published world cuts the basic rate to 19% from April 2024 (March 2022
     Annex A `TA.2!C9`). policyengine-uk 2.130.1 holds 20% throughout, so
     its current law is not that world.
2. **Targets, classified one by one.**
   - **Pre/post classification.** Each target level is classified as post- or
     pre-measures consistent from its source. Only post-measures-consistent
     levels are calibration targets. Some published levels are pre-measures:
     the Scottish Block Grant adjustments (`3.4!B38`, March 2022 and October
     2021) and devolved-government costings (March 2022 Annex A `TA.4!B12`).
   - **Kept distinct.** Administrative observations and forecast levels are
     kept distinct and labelled.
   - **Never calibrate.** Every target is checked against the never-calibrate
     rule: survey-derived tax-benefit quantities never become targets
     ([ARCHITECTURE.md](../../ARCHITECTURE.md#what-may-never-become-a-target)).
   - **Excluded and flagged sources.**
     - A sheet in a lock's `unavailable_sheets` supplies no target.
     - A source that is not the event-day file is flagged on every target it
       supplies. That covers a `later_revision` file, the March 2025
       historical forecasts database, and a DWP edition published after the
       event.
     - Cash-basis receipts are not targets until a documented cash-to-liability
       bridge maps them to the liabilities the engine computes; until then
       they stay held-out level comparisons.
3. **One weight vector per comparison.** The calibrated records, non-policy
   inputs, claimant assignment and weights are frozen for a scoring year and
   shared by both compared worlds. Weights may differ between scoring years,
   never between the compared worlds within one.
4. **The counterfactual.** Each measure's pre-measures world is a separately
   sourced schedule applied to the same population.
   - **How it is built.** The announcement is reversed through an audited
     parameter or input path. Previously announced policies and package
     interactions are included as the event's counterfactual requires.
   - **What it never comes from.** It is never inferred from today's default
     law, from a parameter's earliest key, or from the held-out OBR costing.
   - **How it is checked.** The reform route must give each world's intended
     fiscal-year value in each engine period. The selector's annualisation
     bridge names the route and the check.
5. **No forcing.** No reform is calibrated separately to reproduce its OBR
   delta, and the counterfactual is not reweighted to the published level.
6. **Orientation.** As in [RECIPE.md](../RECIPE.md),
   `literal = gain_to_exchequer(counterfactual - published)` and
   `announced_effect = -literal`. Results are presented pre to post, with
   positive numbers meaning gains to the Exchequer: tax increases are
   positive, spending increases negative.
7. **Take-up and behaviour.** The engine's static take-up convention applies
   to both worlds. Behavioural responses in OBR costings stay a divergence
   axis, never a target.
8. **Geography.** Records are UK-wide. Devolved heads follow the event
   registry's head mapping. Public-budget adjustments are not household
   targets.
9. **Annualisation.** Fiscal years map to engine periods only through the
   selector's resolved annualisation bridge, including its rule for
   parameters that change within a fiscal year. The rule applies equally to
   the published world and the counterfactual.
10. **Recorded gaps and tags.** The following are recorded per measure, never
    filled: missing income-distribution forecasts, unsupported heads,
    behavioural channels, part-year effects and cash-versus-liability
    timing. Each comparison carries these tags:
    - `calibrated_aggregate`: the measure acts on an aggregate the
      calibration fixes, so its result is not independent of the
      calibration.
    - `macro_vintage`: the published world uses post-measures macro inputs,
      while the OBR costs against its pre-measures forecast. November 2022
      publishes both.

## Not decided here

This contract builds no population and certifies nothing. Each population
built under it needs its licensed survey receipt, its target compilation
(with the recorded policy list of term 1) and its own certification with the
engine actually used ([POPULATION_MANIFEST.md](../POPULATION_MANIFEST.md)).
A complete, independently evidenced pre-measures level bridge for an event
would allow `documented_pre_measures_bridge.v1` as a new, separately reviewed
decision.
