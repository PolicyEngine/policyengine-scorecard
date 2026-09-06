# Schema notes: what the platform needs from the interchange format

The `comparison/` schema (`urban_tidy.csv` columns: source, program,
geography, metric, unit, breakdown, year, value, value_kind, raw) is a good
minimal core. Building the scorecard platform against it surfaced the
following required changes — each grounded in a concrete failure or need from
the reconciliation:

1. **`unit` must be part of every join key, and non-optional.** Urban
   publishes TANF eligibility at both family-unit and person level under the
   same metric family; a (program, metric, geography, breakdown) join
   silently compared families to persons (RECONCILIATION.md #5). The
   platform uses an explicit `unit_concept` vocabulary
   (`persons | adults_18plus | children_0thr4 | children_under_13 |
   families | households | tax_units | spm_units`) and enforces an expected
   concept per program-side construction.

2. **`variant` as a first-class column.** TANF's with/without
   solely-state-funded rates are methodological forks, not subgroups;
   encoding them in `breakdown` (`total_with_SSF`) makes subgroup joins
   lossy. Platform schema: `subgroup` + nullable `variant`.

3. **Change/counterfactual metrics need first-class names.** The
   `fullpart_change_*` regex fall-through (RECONCILIATION.md #1) came from
   treating metric names as an open set. The platform registry enumerates
   metrics (`eligible_count, eligibility_rate, participation_rate,
   participation_gap_count, poverty_rate, poverty_rate_fullpart,
   poverty_rate_relative_change_fullpart, poverty_count_change_fullpart`) and
   adapters must fail loudly on unparsed columns (B's adapter raises;
   A's collected them silently into `unparsed`).

4. **Scaling normalizes at the adapter boundary.** Counts in raw units,
   rates as fractions — and the adapter must know which columns are which
   *before* scaling (the ×1000-on-raw-persons bug). `value_kind` stays as a
   check, not the scaling driver.

5. **Suppression is a status, not a null.** Platform rows carry
   `status: ok | suppressed` from the source plus a comparison-side status
   (`comparable | constructed | concept_mismatch | pe_gap | not_computed`).
   That taxonomy is what makes "misses stay on the page" structural.

6. **Every row keeps `source_column` provenance** (A's `raw` keeps only
   suppressed markers). Diagnosing a divergence starts from the source's own
   name for the number.

7. **PE-side values carry their construction.** A's `concept_note` prose is
   the right instinct; the platform splits it into a machine-readable
   `pe_construction` recipe plus **annotation ids** resolving to a registry
   where every annotation has a `basis` (assessment doc §, engine metadata
   recorded at runtime, issue link, or measured diagnostic). That registry is
   what enforces the no-fabricated-mechanisms rule at scale.

8. **Counterfactual runs must log toggle verification.** The
   `would_claim_wic` bug (RECONCILIATION.md #2) was caught only because the
   platform's sim records post-set flag means per run in `pe_meta.json`.
   Interchange metadata for any counterfactual PE file should include the
   flag list actually set, at which periods, with post-set means.

9. **Vintage columns generalize.** `pe_value` (calibrated year) +
   `pe_value_2026` (projected) is the right shape; the platform renders a
   vintage chip per value (`2023 external / 2024 calibrated / 2026+
   projected`). For N sources add `external_year` per row rather than
   assuming one vintage per source.

10. **Planned extensions** (from docs/ARCHITECTURE.md in the platform repo):
    `country` and `reform` columns (constant today; keys for EUROMOD/UKMOD
    and CBO/JCT-score sources), and a `composition` metric family for
    SNAP-QC-style caseload-share comparisons.

11. **`source_measurement` typing on claims** (`administrative | survey | model`), so the never-calibrate rule ("no tax-benefit quantity from a survey, nor anything derived from such") can be enforced mechanically for any future source rather than per-metric: a claim that is BOTH a tax-benefit quantity AND survey/model-measured can never be referenced by a target profile. Natural home: the Chronicle comparator catalog (#6) carries it per fact package; scorecard_db mirrors it.
