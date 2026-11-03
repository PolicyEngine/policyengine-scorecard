# Verification report: `uk_rf_ab2026` (Resolution Foundation, AB2026)

## Verdict: **APPROVE WITH FIXES**, once two commands pass

The fixes are mechanical: one proposed-key rename, a few NOTES edits and some field edits on a handful of rows. I found nothing systematic.

**Three checks I could not run.** This session had no shell, only read, grep and PDF-page tools, so:
- I couldn't recompute the sha256 hashes (check 1).
- I couldn't run the contract script (check 2).
- I couldn't draw the sample with `random.Random(231)`. I chose a stratified sample by hand instead (listed at the end).

I couldn't decompress `claims_staged.jsonl.gz` either, so I rebuilt every row's index and fields from `stage.py`. That file holds all 767 rows as data, in write order, and the counts match NOTES exactly. The coordinator should run these before merging:

```
shasum -a 256 .ab2026-primaries/uk_rf_ab2026/{pr_2026-10-28.html,pr_2026-10-29.html,spread-thin.html,Spread-thin-1.pdf,Spread-thin.pdf,Final-clean-charts-all-sections-for-comms.xlsx,comment_flexible.html}
PYTHONPATH=. python3 pipeline/ab2026_harvest_contract.py sources/harvest-uk-ab2026-2026-10-29/uk_rf_ab2026
```

A static read suggests both will pass:
- **Hashes:** the seven hashes in `stage.py` match `manifest.jsonl` character for character.
- **Contract:** `add()` asserts that every quote is under 15 words, that each quote contains its `value_raw`, and that `fy` agrees with `period`.
- **Metrics and units:** all 20 registered metrics and 9 units the rows use exist in `scorecard_db/models.py`.
- **Keys:** all 14 measure keys are in `REGISTRY_KEYS.md`. All 18 proposed keys appear in NOTES, and none of them is registered.

I didn't open the workbook's XML (I can't read xlsx here). I checked the 555 workbook rows indirectly instead: identities within the workbook, agreement with the PDF's printed labels and text, and agreement with Table 6.1.

## Findings, most serious first

1. **Rows 415–420 and the F20 column G rows (443, 453, … 623): 25 rows have the wrong proposed-key name.** README rule 2 names lines 61 and 62 together `ab2026__package_property_and_savings_income_rates`.
   - **Fix:** set `conditions.proposed_measure_key` to `ab2026__package_property_and_savings_income_rates` on all 25 rows (`P_SAV_PROP` in `stage.py:160`), and rename it in the NOTES proposed-keys table.
   - **Scope is right:** F10 row 51 equals lines 61 + 62 in every year (15, 160, 1130, 955, 1000, 1045).

2. **Family-level: NOTES is stale on README rule 3.** The README now says line 2 costs the whole cut, so these passages contradict it:
   - NOTES:163–164, the bullet "This contradicts the example in the harvest README's rule 3…";
   - discrepancy 14.
   - **Fix:** delete both.

3. **Row 168 is restated but its note doesn't say whose figure it is** (V2 p.30 para 2, "2.7 per cent", `hm_government_publication`). The `note` is empty.
   - **Fix:** set `note` to "Restates the Government's Defence Investment Plan projection (Spread thin p.30)."

4. **Row 38 is restated but its note doesn't name the source** (PR29 takeaways bullet 4, "2.5 per cent", PSNI 2023-24). The note reads only "Outturn inherited from Jeremy Hunt."
   - **Fix:** set `note` to "Restates the ONS/OBR outturn for public sector net investment in 2023-24 (inherited from Jeremy Hunt)."

5. **Family-level: the v1→v2 change record misses the substantive change.**
   - v1's Figure 8 (p.20) plots the Council Tax rebate bars at about £100–103 for vigintiles 2–10. v2 plots them at about £82–88 (workbook F8 D8 = 87.96).
   - The Fuel Duty and VAT segments look the same in both versions.
   - So the lower halves' averages come from a re-estimated Household Energy Payment component. NOTES mentions only the axis change.
   - **Fix:** add to "Text changes": "Figure 8: the Council Tax rebate bars fall from about £100 to about £88 per household (vigintile 2); the other components are unchanged; the axis top moved accordingly."

6. **Family-level: NOTES says "Figure 7's four annotations" were staged (NOTES:253), but only two annotation rows exist.** Rows 112 and 113 cover £1,686 and £1,748. The £1,860 and £1,848 labels are staged from the p.17 text instead (rows 106–107).
   - **Fix:** reword to "Figure 7's two 'After rebate' annotations (the two 'Net bill' labels are staged from p.17 bullet 2)".

7. **Family-level: NOTES has a hash typo.** The workbook row of the primaries table reads `a4e1c072…6d0d1`, but the hash ends `…d6e0d1`.
   - **Fix:** change it to `a4e1c072…6e0d1`.

8. **Row 23 (PR28 para 16, "-0.4 per cent") probably has the wrong statistic.** RF sets it against "an average of just 0.6 per cent a year" (row 21), so it is most likely the last Parliament's average annual growth, not a total.
   - **Fix:** set `value_kind` to `point`, add `conditions.statistic` = "RHDI per person, average annual growth", and set `parse_confidence` to `medium`.

9. **Row 167 (V2 p.30 para 1, "0.5 per cent") can be pinned down.** Figure 14 on the same page plots *average annual* change, and its 2028-29 to 2031-32 RDEL bar is about 0.5%.
   - **Fix:** set `conditions.statistic` to "real RDEL per person, average annual change (Figure 14)", and drop the note's "does not say" sentence.

10. **Rows 28, 29, 56, 57, 61 and 63 lack a price basis.** These are the halves' averages from PR29, the landing page and v1. Rows 74 and 76 carry `price_basis: "cash terms (Figure 8)"`, and these rows have the same basis.
    - **Fix:** add `conditions.price_basis` = "cash terms (Figure 8)" to all six.

11. **Row 397 (F10 C48, value −£746) is a floating-point zero.** C48 is −7.46e-7 bn, and 2026-27 has no Fuel Duty freeze effect; the chart draws no bar. It matches the structural zeros the family skips elsewhere.
    - **Optional fix:** drop row 397. That changes the counts to F10 54, `ab2026_option__fuel_duty_continued_freeze` 6, total 766.

12. **Rows 109–110 (p.17 bullet 4, £358 and 20 per cent): geography is optional to fix.** The subgroup is "those set to receive the £100 rebate", which is England (row 108 uses England).
    - **Optional fix:** set `geography` to "England" for consistency.

13. **Family-level: add one anomaly to NOTES** as item 15.
    - PR28 para 5 and p.17 bullet 2 describe the package's VAT element as the "three-month extension", and p.17 calls the six-month cut "support announced before this Budget".
    - Yet Figure 8, the 52/48 split and the £4.4bn all include "Energy VAT cut (original)".

## Decisions adjudicated

**1. The cost-of-living package: confirmed.** RF's package is exactly Table 6.1 lines 1, 2 and 3, and all 57 rows correctly carry the registered key.
- **The workbook net is the four components.** F8's net column J equals D + E + F + G exactly:
  - vigintile 2: 87.96 + 22.95 + 24.51 + 9.90 = 145.33;
  - vigintiles 3, 10, 15 and 20 also tie to 4 decimal places.
- **F8 has no other column:** no gas standing charge and no policy levies (F7's "Policy levies removed" is a separate, pre-Budget column).
- **The £4.4bn ties out:** 2,625 + 755 + 305 + ½ × 1,355 ≈ £4,363m. That is the whole VAT cut plus Fuel Duty at RF's household share (fn 19).
- **The £3.4bn and £3.7bn sums** (2,625 + 755 = 3,380; plus 305 = 3,685) show RF costs line 2 as the whole cut.

Row by row:
- **Text rows 26–30, 34, 54, 56, 57, 61–63, 74–76, 127, 130 and 131:** these are Figure 8 / p.19 figures or the £4.4bn, so they are in scope.
- **The 38 F8 J/K rows:** in scope.
- **Row 48** ("just over half of measures announced by Burnham and Healey") has looser wording, but it is the same 52% as p.19. Keep it at medium confidence.
- **Rows 30, 54 and 127 (£4.4bn)** are a household-incidence costing, not the Exchequer cost (Table 6.1 lines 1–3 sum to £5,040m). Their `costing_basis` says so, and the ingest must not compare them with Table 6.1's total.
- **Rows 10 and 11 (£116)** are correctly *not* on the package key, because they cover "announced today" support only.

**2. Context rows: none is design.** I checked the F7 bill levels and support columns, the price-cap forecasts, the public-finance aggregates, the living-standards and poverty figures and F20's pre-AB26 columns. F7 columns E and L (the flat £400 / £150 / £100 payments) are correctly excluded. Rows 155 and 156 (£34 / £10) are worked-example outcomes, so they are allowed.

**3. The v1/v2 replacement: confirmed.**
- **v1 rows:** rows 61–63 match v1 p.5 ("£158 … £14 more than the £144"). Each carries `document_version: "v1 (superseded)"` and the superseded note.
- **v2 rows:** v2 p.5 prints £145 / £15 / £130 (rows 74–76), and p.19 hedges them as "under £145 … over £130 … less than £15".
- **NOTES' change record** is accurate apart from finding 5.

**4. `ab2026__defence_investment_plan_further_savings` (row 163): match confirmed.** Keep the registered key at medium confidence rather than making it a proposal.
- **The sum is exact.** Line 40 sums to −1,755 − 1,090 − 1,010 − 905 − 940 − 970 = −6,670, which is RF's "£6.7 billion between 2026-27 and 2031-32".
- **RF cites HMT.** RF's fn 38 cites "HM Treasury, Budget 2026".
- **No other defence line fits.** Line 41 is +7,115 and line 42 is −190, so neither one, nor any combination with line 40, matches.
- **Rule 8 doesn't apply.** This row restates a scored Table 6.1 cost, like row 161's £2.6bn. That is unlike the SAHP £1.5bn (line 35 is 1,750), Good Growth Funds £285m (line 20 is −340) and AI £700m (line 31 is 490), which don't match any line and were rightly dropped as allocations.

**5. Proposed-key names:**
- `…savings_and_property_income_rates_plus_2pp` must be renamed (finding 1).
- **OBR groupings (all fine):** `package_obr_direct_effect_of_tax_measures`, `package_obr_tax_administration_compliance_and_debt_collection` and `package_obr_total_effect_of_government_decisions` are the OBR's own groupings. The second is not line 45, which is 2,485 in 2030-31 against 2.89bn.
- **RF groupings (acceptable):** the five `package_rf_…` keys are RF's own groupings.
  - Optionally, `package_rf_absolute_policy_changes` could become `ab2026__package_total_policy_decisions` with metric `absolute_policy_change`, if you decide RF's scope is Table 6.1's total. RF lists no lines, so I'd keep it as a proposal.
- **Measure-kind keys (all confirmed):** each names an announced measure with no Table 6.1 line.
  - Gas standing charge: "costs the Exchequer nothing" (p.18).
  - Minimum wage: "the Chancellor confirming" the rates (p.12).
  - Gas Supplier Levy: "also announced" (fn 12).
  - I found no matching line in `REGISTRY_KEYS.md` for any of them.

**6. The 14 anomalies:**
- **Confirmed (11):** items 1–4, 6–9, 10, 11 and 12.
  - Landing page Key findings bullet 3 prints "£158 … £144" (`spread-thin.html:679`).
  - Your First Home: p.21 says "at a cost of £95 million", while line 37 prints +95 ("net income from developer fees").
  - Fn 53 says "between 2023-24 and 2029-30". Fn 50 says "From the forecasts shown in Figure 7".
  - Line 20's −340 bears out item 6.
- **Supported:** item 5. Line 35 sums to 1,750.
- **Unverified:** item 13. Table 6.2 isn't in this worktree.
- **Stale:** item 14 (finding 2).
- **Row 136 (Your First Home):** keep as staged. It is documented, at medium confidence and noted, but the ingest should know this restated row's sign is the opposite of HMT's.

## Identities (workbook)

Every identity I tested holds; there are no failures.
- **F8:** J = D + E + F + G for vigintiles 2, 3, 10, 15 and 20.
- **F20, AB26 components:** K = F + G + I + J for vigintiles 2–5 (for example, vigintile 2: 0 − 1.7782 − 5.1913 + 2.8285 = −4.1410).
- **F20, net:** L = D + E + H + K for vigintiles 2–5 (vigintile 2: 431.48).
- **F10, residual:** row 53 = 46 − 47 − 49 − 50 − 51 − 52 for 2026-27, 2029-30 and 2031-32.
- **F10, freeze path:** row 54 = 46 + 48 for 2026-27 and 2027-28.
- **F10 against Table 6.1:** rows 47, 49, 50 and 51 equal lines 3, 55, 58 and 61 + 62 in all six years, and J49 = 1.475.
- **F7:** I = C + D + E + F + H and M = I + L for 2022-23 and 2026-27. The p.17 deltas re-derive: £363, £217, £62, £358.

## Coverage, NOTES and completeness

- **Tallies:** every tally in NOTES re-derives exactly:
  - sheets (555), measure keys, and the 198 proposed / 332 context split;
  - attribution (84 restated);
  - source models (42 OBR / 38 HMT / 5 administrative / 3 Government, 42 survey);
  - 53 `administrative_fact` rows and 99 start-of-Parliament baseline rows.
- **Family directory:** it holds only `NOTES.md`, `manifest.jsonl`, `claims_staged.jsonl.gz` and `stage.py`, so nothing is stale. The spot-check files are under the git-ignored `.ab2026-primaries/`.
- **Running the check rewrites the claims file.** `stage.py --check-primaries` calls `write()` first, so it rewrites the claims file (byte-identical by design).
- **Completeness:** the pages I read in full (PDF pp.3–6, 12, 16–28, 30, 33–35, 40–42, 45–46; both press releases; the landing page) have no unlisted in-scope estimate.
  - Repeats inside one document (p.6 £61 / 9.9m, p.23 "over £3 billion", p.42 "£80 million in a full year") are correctly staged once.
  - **Not read as page images:** pp.7–11, 13–15, 29, 31–32, 36–39, 43–44 and 47–48. I checked their rows' quotes only against the lane's `v2.txt`.

## Sample

The sample is hand-stratified, not `Random(231)`. Every result was OK unless a finding is named.

**Text rows, checked against the primary:**

| Rows | Locator | Result |
|---|---|---|
| 0–23 (all) | PR28 paras 2–16 | OK. Row 23 → finding 8 |
| 24–42 (all) | PR29 bullets and quote | OK. Row 38 → finding 4; rows 28–29 → finding 10 |
| 43–60 (all) | Landing page summary and Key findings | OK. Rows 56–57 are v1 text (confirmed); finding 10 |
| 61–63 | v1 p.5 para 4 | OK, superseded figures; finding 10 |
| 64–77 | v2 pp.3–6 | OK |
| 88 | v2 p.12 | OK |
| 93–140 | v2 pp.16–22 | OK. Rows 109–110 → finding 12 |
| 141–151 | p.23 Figure 10 labels | OK, matched to F10 rows 46 and 54 |
| 152–163 | pp.23–27 | OK. Row 163 → decision 4 |
| 167–170 | p.30 | Row 167 → finding 9; row 168 → finding 3 |
| 174–181 | pp.34–35 | OK |
| 191–197 | pp.40–42 | OK |
| 203–209 | pp.45–46 | OK |
| 211 | Comment para 1 | OK |

**Workbook rows, checked against embedded values, the PDF and Table 6.1 (not against the XML):**

| Rows | Cells | Result |
|---|---|---|
| 212–244 (all F7) | F7 | OK |
| 245–250 | F8 vigintile 2 | OK |
| 251–256 | F8 vigintile 3 | OK |
| 293–298 | F8 vigintile 10 | OK |
| 327 | F8 J21 | OK |
| 353–358 | F8 vigintile 20 | OK |
| 359–360, 379–384 | F9 | OK. M19 0.906 ≈ 91%; N20 0.762 ≈ 76% |
| 385–439 (all F10) | F10 | OK. Row 397 → finding 11 |
| 440–479 | F20 vigintiles 2–5 | OK |
| 630, 632, 634 | F21 AD67, AD69, AD71 | OK. 5.0% and 1.8% match p.43 |
| 638, 656, 733, 734, 751 | F22 V342, AN342, V350, W350, AN350 | OK against the Figure 22 bars' order of magnitude (no values read off bars) |
| 753, 760, 764–766 | F23 AQ67, AR69, AP71, AQ71, AR71 | OK. +0.8 / −0.4 / −2.6 ppts match the labels |

Plan mode was on, but this session had no file-write or plan-exit tool, so no plan file was written. This report is the whole deliverable.