# Rework `uk_hmt_redbook` to the harvest's scope (#230)

You staged `sources/harvest-uk-ab2026-2026-10-29/uk_hmt_redbook/` in this worktree earlier today: 1,699 rows and 250 proposed keys. It passes the contract checker, but most rows are outside the harvest's scope. The coordinator has added two rules to `sources/harvest-uk-ab2026-2026-10-29/README.md`; read rules 8 and 9 there now. In short:

- **Rule 8, stage estimates, not design.** A row is a number someone estimated, forecast or counted about an effect. Out of scope, kept at most in `reform_hint` or `conditions`:
  - measure parameters (rates, thresholds, payment amounts, dates, durations);
  - spending allocations to programmes, financing remits (DMO, gilts, T-bills) and contingent liabilities.
- **Rule 9, a component of one measure keeps that measure's key.** A part of one Table 6.1 line carries that line's key, with `conditions.component` and `conditions.row_type: "measure_component"`. Examples: a tax-gap package item under line 45, or an AI programme under the AI package line. Proposed package keys are only for scopes that cross Table 6.1 lines or have no line.

The AB2025 precedent (`sources/harvest-uk-ab2025-2026-09-24/uk_hmt_redbook/`, 39 rows) staged the red book's household-facing headline estimates and kept parameters in `reform_hint`. Re-read its NOTES.md.

## What to do

Edit your `stage.py` and re-stage:

1. **Remove these rows:**
   - every `proposed_metric: policy_parameter` row;
   - every row whose value is a design number under another metric;
   - the allocation and financing metrics: `government_financing_amount`, `financing_amount`, `investment_amount`, `contingent_liability_amount`, `financing_share`, `public_investment_share`, `net_cash_requirement`, `government_spending_level`, `spending_to_tax_ratio`.
   - Exception: a cost or yield that the document presents as a Table 6.1 measure's Exchequer impact stays. Key it to that line, and treat it as a component if it is part of the line.
2. **Re-key under rule 9.** Each row whose proposed key names a part of one Table 6.1 line gets that line's registry key and component conditions. Find the line in `REGISTRY_KEYS.md` by title and by the red book's own paragraph.
   - When a red-book number is a spending programme's allocation inside a Table 6.1 spending line, it is design (rule 8). Drop it unless the red book presents it as the measure's cost.
3. **Keep:**
   - costs and yields of Table 6.1 measures;
   - people, households and businesses affected;
   - gains, losses and bill changes per household;
   - poverty and distributional statements;
   - earnings and price effects;
   - restated OBR fiscal aggregates (headroom, borrowing, debt, the decisions' effect on borrowing), as `restated`;
   - consequentials for devolved governments (`block_grant_effect`);
   - Impact on households' printed values;
   - the Pension Tax Allowance explainer's counts and worked-case outcomes.
4. **Proposed keys:** cut them to those still needed. For each one left, NOTES.md gives its scope as Table 6.1 lines, or says "no Table 6.1 line", with the red book's words.
5. **NOTES.md:** rewrite the coverage tally, the per-key counts and the proposed scopes for the new row set. Add a "Not staged (rules 8 and 9)" section that counts what you dropped by category, with two or three examples each. Keep the primaries, access recipe and source anomalies sections. Delete REPORT.md, spot_checks.json and spot_checks_ch6.json, or bring them up to date; nothing stale may remain.
6. **Verify:**
   - `PYTHONPATH=. uv run -q python pipeline/ab2026_harvest_contract.py sources/harvest-uk-ab2026-2026-10-29/uk_hmt_redbook` reports 0 problems;
   - a re-run of `stage.py` reproduces the gzip byte for byte;
   - 30 random rows re-opened at their locators in the primaries under `.ab2026-primaries/uk_hmt_redbook/` match on value, sign, unit and period.

Write only inside that family directory. Don't touch anything else, and don't commit or push.

## Also fix: findings from other lanes and the coordinator

1. **"84% of income tax payers will be unaffected"** (p.39, para 2.50) is staged as `affected_share` = 84, which inverts its meaning: 84 is the share *not* affected. Stage it as printed with `proposed_metric: "unaffected_share"`. Never convert it to 16, which the document doesn't print.
2. **`ab2026__package_tax_gap_timely_payment`** names a part of Table 6.1 line 45, so under rule 9 its rows carry line 45's key with `conditions.component` and `row_type: measure_component`. The costings and TPA families key the same part that way.
3. **Name proposed keys by README rule 2's new naming bullet.**
   - A measure with no Table 6.1 line is `ab2026__<slug>`, not a package.
   - Keep `ab2026__package_property_and_savings_income_rates` for lines 61 and 62.
   - Where a row shares its scope with another family's key, use that family's spelling:
     - `ab2026__gas_standing_charge_moved_to_unit_rates`;
     - `ab2026__pwlb_debt_relief_councils_severe_distress`;
     - `ab2026__private_landlord_register_fee_65`;
     - `ab2026__british_business_bank_defence_commitments_accelerated`;
     - `ab2026__package_household_energy_payment_and_electricity_vat` (lines 1 and 2).
4. **README rule 3's example was wrong, and is corrected.** Line 2 costs the whole electricity VAT cut from 1 October 2026. A figure for exactly the energy payment, the VAT cut and the fuel duty cut takes the registered key `ab2026__package_household_energy_vat_and_fuel_duty`.

## Report

- The new row count by metric and by measure_key, including null.
- The remaining proposed keys with their scopes.
- Dropped counts by category.
- The checker output and the 30-row spot check.
