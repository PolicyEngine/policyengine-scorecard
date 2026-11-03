
## Your assignment: family `uk_hmt_costings` (source `hm_treasury`)

Verify only `sources/harvest-uk-ab2026-2026-10-29/uk_hmt_costings/`. This worktree also holds `uk_hmt_tables` (Tables 6.1, 6.2 and 6.4, already in the PR); use it as the reference for Table 6.1.

- **Rows:** 597 from one primary, HM Treasury's *Budget 2026: Policy Costings* PDF. 576 are Exchequer-impact cells (96 notes × 6 years); 21 are text rows: behavioural parameters, PSND/PSNFL impacts, eligible counts, tax-gap figures, a tax base and a financial transaction.
- **Sample:** 60 rows, stratified as the common instructions say, including every text row.
- **Whole-line identity:** write a short script to check every row keyed to a whole Table 6.1 line against `uk_hmt_tables` in every year. The lane reports all 68 such keys equal Table 6.1. List any mismatch.
- **Component identity (rule 9):** components of lines 29, 45, 47, 56, 72, 77, 84 and 85 carry their line's key.
  - The lane reports that lines 56, 77 and 84 sum to the line within £5m.
  - It reports that lines 45 and 47 don't sum to the line, and that line 72's note prints only the AME savings.
  - Confirm each claim from the primary. Say whether NOTES.md records the gaps clearly enough that nobody would add components to a total.
- **Proposed keys:** check that each of the three measure-kind keys is an announced measure with no Table 6.1 line:
  - `ab2026__british_business_bank_defence_commitments_accelerated`;
  - `ab2026__private_landlord_register_fee_65`;
  - `ab2026__pwlb_debt_relief_councils_severe_distress`.
  Footnote 2 excludes two of them. The BBB defence measure is placed among lines 40–43 by its position in the document, but no line's title or figures match it; judge that.
- **Conventions to judge:**
  - Seven PSND/PSNFL figures are printed unsigned with words such as "cost" and "benefit"; the lane put them on the Exchequer sign convention.
  - Two fair-value increments use a new proposed metric, `psnfl_fair_value_impact`.
  - The tax-gap rows (6.4% and £59.2bn for 2024-25) are staged as `restated`, as line 45 components.
- **Rule 8:** the lane dropped contingent liabilities, allocations and staff numbers. Check that what remains holds no design numbers.
