
## Your assignment: family `uk_obr_tables` (source `obr_efo`)

Verify only `sources/harvest-uk-ab2026-2026-10-29/uk_obr_tables/`. This worktree also holds `uk_hmt_tables`, which is already in the PR; ignore it except as a reference for Table 6.1.

- **Rows:** 2,891. By row type: 1,572 `measure_component`, 618 `measure_total`, 330 `summary` and 371 with no row type. 37 proposed keys.
- **Primaries:** three. The lane fetched local copies after OBR returned 403; the manifest records each primary's access.
- **Sample:** 80 rows, stratified as the common instructions say, including at least 10 components and 10 measure totals.
- **Identity:** for at least 15 measures, components sum to the measure total in every year.

**A design-row candidate (rule 8):** 35 rows carry `proposed_metric: "compliance_funding"`. They are EFO Table 3.2 levels of HMRC compliance and debt funding and DWP fraud and error funding: baseline, earlier-Budget and total. The coordinator reads them as spending allocations, which rule 8 excludes. Confirm or refute that for each row. A row in that table that is a yield or a net Exchequer effect of a measure stays.

**Settled; don't reopen:**
- The 7 `costing_uncertainty_rating` rows follow the AB2025 OBR family's precedent (101 such rows) and stay.
- The 48 component rows that carry a proposed key are parts of fiscally neutral measures with no Table 6.1 line. Rule 9 allows that. Check only that each is a part of one measure.
