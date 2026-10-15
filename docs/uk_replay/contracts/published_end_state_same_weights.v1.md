# Contract `published_end_state_same_weights.v1`

The policy-world contract for vintage-faithful replays of Spring Statement
2022, Autumn Statement 2022 and Autumn Budget 2021, chosen under cos d1344
([decision record](../HISTORICAL_DECISIONS.md)). A selector binds this file
by its SHA-256; any change to these terms is a new contract version.

## Terms

1. **Published world.** For each event and each scoring fiscal year in its
   selector, the event's OBR forecast, read from the event's committed
   [source locks](../../../data/uk/events/vintage_locks/), defines the
   published post-measures world. The event population is calibrated to that
   world once per scoring year.
2. **Targets.** Administrative observations and the event's forecast levels
   are kept distinct and labelled. Survey-derived tax-benefit quantities never
   become targets ([ARCHITECTURE.md](../../ARCHITECTURE.md#what-may-never-become-a-target)).
   A sheet recorded in a lock's `unavailable_sheets` supplies no target. A
   source labelled `later_revision` is flagged on every target it supplies.
3. **One weight vector per comparison.** The calibrated records, non-policy
   inputs, claimant assignment and weights are frozen for a scoring year and
   shared by both compared worlds. Weights may differ between scoring years,
   never between the compared worlds within one.
4. **The counterfactual.** Each measure's pre-measures world is a separately
   sourced schedule applied to the same population: the announcement reversed
   through an audited parameter or input path, including previously announced
   policies and package interactions as the event's counterfactual requires.
   It is never inferred from today's default law, from a parameter's earliest
   key, or from the held-out OBR costing.
5. **No forcing.** No reform is calibrated separately to reproduce its OBR
   delta, and the counterfactual is not reweighted to the published level.
6. **Orientation.** The result is the counterfactual minus the published
   world, presented pre to post with positive numbers meaning gains to the
   Exchequer (tax increases positive, spending increases negative), under the
   existing source-head accounting contract ([RECIPE.md](../RECIPE.md)).
7. **Take-up and behaviour.** The engine's static take-up convention applies
   to both worlds. Behavioural responses in OBR costings stay a divergence
   axis, never a target.
8. **Geography.** UK-wide records. Devolved heads follow the event registry's
   head mapping; public-budget adjustments such as Scottish block grant lines
   are not household targets.
9. **Annualisation.** Fiscal years map to engine periods only through the
   selector's resolved annualisation bridge.
10. **Recorded gaps.** Missing income-distribution forecasts, unsupported
    heads, behavioural channels, part-year effects and cash-versus-liability
    timing are recorded per measure, never filled.

## Not decided here

This contract builds no population and certifies nothing. Each population
built under it needs its licensed survey receipt, its target compilation and
its own certification with the engine actually used
([POPULATION_MANIFEST.md](../POPULATION_MANIFEST.md)). A complete,
independently evidenced pre-measures level bridge for an event would allow
`documented_pre_measures_bridge.v1` as a new, separately reviewed decision.
