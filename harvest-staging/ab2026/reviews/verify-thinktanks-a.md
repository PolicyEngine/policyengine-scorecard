# Verdicts: AB2026 harvest families uk_tpa, uk_centax, uk_ippr, uk_cpag, uk_smf

| family | verdict |
|---|---|
| `uk_tpa` | **APPROVE WITH FIXES** |
| `uk_centax` | **APPROVE WITH FIXES** |
| `uk_ippr` | **APPROVE WITH FIXES** |
| `uk_cpag` | **APPROVE** |
| `uk_smf` | **APPROVE** |

**Run these before merging.** This session had only Read, Grep and Glob, with no shell, so three steps from the brief were not done:

- **Check 1 (hashes):** I couldn't recompute any sha256, including those of the CPAG/SMF challenge pages.
- **Check 2 (contract):** I couldn't run `pipeline/ab2026_harvest_contract.py`.
- **Reading the rows:** I couldn't open the `.gz` files or draw the `random.Random(231)` sample. Instead I rebuilt every row, in order, from each family's `stage.py`. NOTES says `stage.py` writes the claims file byte for byte, and its row and key counts match NOTES exactly.

Run `stage.py --verify` (it is read-only apart from rewriting the same bytes) and the contract script on all five families. I applied the contract's rules by hand and found no breach.

My Table 6.1 values come from `.ab2026-primaries/_tools/t61.txt`, a dump of `uk_hmt_tables` written by `t61.py`. They agree with every HMT figure TPA prints: the totals −1,645 / 695 / 2,865 / 5,550 / 6,495 / 6,970, line 54's 690/675/655 and line 68's 480.

---

## uk_tpa: APPROVE WITH FIXES

**Group mapping re-derived: it holds.**
- **By-year chart:** all 11 groups reproduce TPA's figures exactly in all six years. Examples: Business rates is lines 12+13+14+57+76+80 = 10, −490, −685, −30, −40, −45. Other by-year (13 lines) is −205, −360, 55, 5, −30, −245.
- **Partition:** the 11 groups hold 53 lines, each line exactly once, and those are exactly the 53 Tax-head lines. In 2027-28 the groups sum to £700m; in 2026-27 to −£1,635m.
- **By-tax chart:** all 13 bars match in 2027-28. Savings and property is 155 only if line 11 is included (35+125−5). The by-tax groups cover 52 lines, with line 66 undetermined, as NOTES says.
- **By-measure chart:** its bars also partition all 53 lines. Using the lane's fitted deflators I reproduced six bars to within £1m: savings and property 3,981; Tariffs −1,594; Other −1,275; Bank 1,436; Tax gap 7,155; Mileage −1,076.

**Attribution matches the AB2025 convention.**
- AB2025 `uk_tpa` staged "around £2bn" (CenTax's £1.9bn, rounded) as `restated`. AB2026 does the same for rows 3, 15 and 18.
- AB2025 had no TPA sums of official figures. Its NIESR ("arithmetic on OBR figures") and Fabians families staged such arithmetic as `own` / `arithmetic` / `different_model`, which matches AB2026.
- NOTES says this matches "the IFS lane's treatment", but no IFS AB2026 family is in this worktree, so I couldn't check that.

**Proposed keys:** all 14 follow rule 2. `ab2026__package_property_and_savings_income_rates` is the agreed name. The 13 `package_tpa_*` keys each name a TPA grouping. None is a single Table 6.1 line, a registered key or a registered package.

### Findings

1. **Row 16 (£93): design under rule 8. Medium; this is a judgement call.**
   - Evidence: in the article's 'Pension tax' section, TPA writes "prevent pensioners being chased by HMRC for £93". That is the most tax the allowance removes, 20% × (£13,036.40 − £12,570) = £93.28. It is the same quantity as the "up to £94 a year" maximum, which the family already keeps out of the rows as design. NOTES itself treats £93 and £94 as one figure ("Things that look wrong").
   - Fix:
     - drop row 16;
     - add `"tax_removed": "£93 (as printed)"` to row 17's conditions;
     - update NOTES to 305 rows, own 244, article 49, and `ab2026__pension_tax_allowance` 2 rows;
     - list "£93" under the policy parameters not staged.
2. **About 107 keyed `own`/`arithmetic` rows carry `benchmark_class: different_model`. Low; no fix.**
   - These are the group, deflated and %-of-GDP rows. AB2025 rule 4 describes `different_model` as "an independent model", so tranche 2 must separate these rows on `conditions.derived_from`, as NOTES says.
3. **The same totals are staged many times. Low; no fix, but tranche 2 should deduplicate.**
   - The 2027-28 total tax policy decisions appear as rows 3, 26, 27, 147, 169 and 237.
   - The six-year total appears as rows 4 (£19bn), 28 and 265 (£19.1bn).
   - That is not consistent with NOTES dropping "a new 53% band, for £94" as a same-primary duplicate.
4. **Chart quotes are re-serialised JSON, not the file's text. Low.**
   - Example: rows 170–175 quote `"data": [-0.205, -0.36, …]`, but the file prints the array across several lines with `\u00a3` escapes.
   - Fix: reword NOTES' "as it stands in the file, whitespace-normalised" to "the element re-serialised with `json.dumps`".
5. **Row 1 ("two-fifths") uses the registered `revenue_share`. Low.**
   - `models.py` defines that metric as "share of a measure's yield paid by a group"; this row is the share of tax rises coming from a group of Budgets.
   - Optional fix: set `proposed_metric: "revenue_share_by_fiscal_event"` and `metric: null`.
6. **Two by-tax scopes are partly assumed. Low, for the registry.**
   - In `ab2026__package_tpa_other_by_tax_2027_28` and the by-tax bar of `ab2026__package_tpa_other_vat`, the lines that are zero in 2027-28 are placed by assumption, and line 66 is undetermined. The values don't change; the registered scope should carry that caveat.

**Design rows:** row 16 only (one payment amount). The capital-allowance present values, bank effective rates, the 53% rate and the calculator rows are computed outcomes.

**Completeness:** I found nothing in-scope that is missing. The "£3,000bn GDP", "over twice its pre-pandemic share" and "£1.2bn" (a reader comment) are all listed as not staged.

---

## uk_centax: APPROVE WITH FIXES

**Option scopes:** each of the 7 keys matches CenTax's words:
- CGT package: pp. 16–17, "the first four elements" costed;
- partnership NICs: pp. 19–20;
- investment-income NICs: p. 22;
- the four childcare options: pp. 23–26, "All are costed on an actual ANI basis".

None is a registered key or package.

**#207 file:** `data/externals/centax-childcare-100k.json` exists. It holds only Table 4.2 (full removal; central, high-cost and low-cost; 2028 and 2030). Its central net fiscal costs (−520m and −640m) match rows 1, 25 and 99 in size.

### Findings

1. **Rows 84–86 (£3bn / £0.6bn / £0.4bn) are components of row 24's £4bn total but aren't tagged as components. Medium.**
   - Evidence: p. 22 prints "this would raise up to £3 billion, £0.6 billion and £0.4 billion respectively", and Key findings item 7 prints "up to £4 billion". The identity 3 + 0.6 + 0.4 = 4.0 holds.
   - As staged, an ingest can sum the parts with the total.
   - Fix: on rows 84–86 set `conditions.row_type: "measure_component"` and `conditions.component` to each row's `income_type` value. This is rule 9 applied by analogy to an option key.
2. **Row 2 (£1.6bn, timely payment, keyed as a component of line 45) cites figures no staged family holds. Low–medium.**
   - The `derived_from` cites Table 6.3 line 3 (£1,355m, £1,605m, £1,815m). `uk_hmt_tables` stages Tables 6.1, 6.2 and 6.4 only, so I couldn't verify those three figures.
   - They are consistent with the quote: the reaction page prints "around £1.6 billion a year averaged over the three years from 2029–30 to 2031–32", and their mean is £1,592m. They are also below line 45's 1,980 / 2,485 / 3,160.
   - Fix: confirm the three figures against the Budget document before merge.
3. **The #207 file and this family differ in ways NOTES doesn't record. Low; NOTES only.**
   - **Sign:** #207 stores −640m, where a negative value is a cost. This family stores +640m with `positive = cost`.
   - **Coverage:** #207 doesn't hold the cheaper options (rows 101–106); here they come only from "Taxes at the top".
   - **Bunching counts:** row 27 has "11,980 by 2030", while #207's 2030 central "Number Bunching, Before Removal" is 16,280. This may be a different concept, or CenTax may be inconsistent between its two publications.
   - Fix: add these three points to NOTES' #207 bullet and to row 27's note.
4. **Row 105 ("raise £20 million") is re-signed to −2e7. Low, optional.**
   - The AB2025 README says the value is "NOT re-signed".
   - Optional fix: `value: 20000000`, `sign_convention: "positive = yield to the Exchequer"`, `normalization: "£ million × 1e6"`.
5. **Small metric inconsistencies. Low.**
   - Row 18 (23%, a 25th-percentile EATR) uses `proposed_metric: effective_tax_rate`, while rows 7–15 use the registered `average_tax_rate`. Optional fix: `metric: "average_tax_rate"`.
   - Rows 19–20 put `revenue_change` in `percent`. Tranche 2 must not read them as £.
6. **One sensitivity figure is neither staged nor listed. Low, completeness.**
   - p. 25 prints "around four times as many parents would be bunching" for the halved-unresponsiveness scenario.
   - Fix: add it to NOTES' not-staged list as a scenario ratio.
7. **For tranche 2:** rows 20, 58, 108 and 109 are CenTax's 2024-era estimates, at fy 2025-26 under the AB2026 CGT option key. They carry a `scenario` condition that says so.

**Design rows:** none.

---

## uk_ippr: APPROVE WITH FIXES

1. **Row 0 (−0.2pp CPI): stage it as a context figure. Medium.**
   - IPPR's words don't define the scope. Jung's quote says only "The cost of living support announced today", and Quilter-Pinner's says "action to support families with the cost of living".
   - The lines 2 + 3 scope comes from matching the OBR's paragraph 3.10, which is our inference. Rule 3 says the scope must be the producer's.
   - Fix:
     - remove `conditions.proposed_measure_key`, leaving `measure_key: null` with the hint and note kept;
     - set `value_kind: "range_high"`, because "lower by at least 0.2" makes the signed −0.2 an upper bound;
     - in NOTES, change the tally to "1 with a proposed key, 2 context" and delete the `ab2026__package_cost_of_living_support` paragraph.
2. **Rows 1 and 2 check out.** The quotes are verbatim and under 15 words. The £285m (spending allocation), £1.5bn (financing remit) and £100 (payment amount) are correctly excluded as design. Nothing is missing from the three releases.

---

## uk_cpag and uk_smf: APPROVE

- `manifest.jsonl` is empty in both, and NOTES says 0 rows and 0 primaries.
- `stage.py` writes an empty, deterministic claims file.
- All six files under `.ab2026-primaries/uk_{cpag,smf}/` contain "Just a moment", so they are challenge pages, and none is listed as a primary.
- Not verified: I couldn't recompute the challenge-page hashes, and I didn't check that `harvest_counts.py` handles a family with no primaries.

---

## Sample (stand-in for the Random(231) draw)

I checked more than the assigned sample: every row's value and quote against the primaries, plus the reconstruction from `stage.py`.

- **TPA**
  - Rows 0–49: every quote found in the article text at the stated section or footnote, with value, `fy` and price basis correct.
  - Rows 50–112 (by-event chart): values and labels match the JSON.
  - Rows 113–143 (by-government chart): match series 0–4 and the markLine.
  - Rows 144–155 (GDP chart): match, including `value` and `name`.
  - Rows 156–169 (by-tax chart), 170–241 (by-year chart and net totals) and 242–265 (by-measure chart): all match the JSON and the `aria` text.
  - Rows 266–299 (bank chart): totals and component arrays match, with nulls skipped.
  - Rows 300–305 (calculator screenshot): 58.3% / 58.9% / £417 / £400 / £20 / £163 match the image.
  - Only failure: row 16 is a design figure (finding 1).
- **CenTax**
  - Rows 0–2: in the reaction page's PTA, Carer's Allowance and Timely payments sections.
  - Rows 3–29: Key findings, p. 1.
  - Rows 30–55: pp. 5–13.
  - Rows 56–60: pp. 17–18.
  - Rows 61–83: pp. 19–21; the Table 1 shares sum to 99.99% and 100.01%.
  - Rows 84–92: p. 22 (finding 1 applies to 84–86).
  - Rows 93–106: pp. 23–26.
  - Rows 107–109: Unicorn Relief, footnote 9.
  - All quotes found, with tax years read as the later year.
- **IPPR:** row 0 is in Jung's first paragraph (finding 1); row 1 is in his second paragraph; row 2 is in the North release's third paragraph.