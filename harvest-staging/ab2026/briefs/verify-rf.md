
## Your assignment: family `uk_rf_ab2026` (source `resolution_foundation`)

Verify only `sources/harvest-uk-ab2026-2026-10-29/uk_rf_ab2026/`. Ignore `uk_hmt_tables`, except as the reference for Table 6.1.

- **Rows:** 767 from 7 primaries:
  - two press releases;
  - the *Spread thin* landing page;
  - *Spread thin* PDF v1 (superseded on 29 October) and v2;
  - the chart-data workbook;
  - a 29 October comment.
- **Sample:** 80 rows, stratified as the common instructions say. Include at least 15 workbook cells, every row that cites PDF v1, and at least 10 of the 57 rows on the registered package key.
- **Workbook identity:** where the workbook prints components and their net (for example F20's AB26 component columns), check that the components sum to the net within rounding.

**Decisions to adjudicate:**
1. **The cost-of-living package.** RF's package figures carry the registered key `ab2026__package_household_energy_vat_and_fuel_duty`. README rule 3 is now corrected: line 2 costs the whole VAT cut from 1 October 2026. Confirm, row by row, that RF's figure covers exactly lines 1, 2 and 3, and nothing else, such as the gas standing charge or other support.
2. **Context rows.** 332 rows have a null key and no proposed key: bill levels before support, price-cap forecasts, and living-standards and poverty projections. They stay unless rule 8 makes one design. List any that are.
3. **The v1/v2 replacement (rule 7).** Check that the three v1 rows are the superseded figures, are marked as superseded, and that NOTES.md records what changed.
4. **`ab2026__defence_investment_plan_further_savings`.** The lane matched it by a sum, with medium confidence. Confirm the match, or say it should be a proposal.
5. **Proposed-key names (README rule 2's naming bullet).**
   - `ab2026__package_savings_and_property_income_rates_plus_2pp` should be `ab2026__package_property_and_savings_income_rates`.
   - Check each `package_obr_…` and `package_rf_…` key against that rule.
   - Check that each measure-kind key (`ab2026__gas_standing_charge_moved_to_unit_rates`, `ab2026__minimum_wage_rates_april_2027`, `ab2026__gas_supplier_levy_funded_from_general_taxation`) names an announced measure with no Table 6.1 line.
6. **The primary anomalies the lane lists.** Confirm the 14 items in NOTES.md, especially the stale landing page (£158 and £144 against v2's £145 and £130) and the Your First Home sign.
