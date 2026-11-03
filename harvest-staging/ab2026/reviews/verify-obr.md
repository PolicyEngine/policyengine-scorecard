**Verdict for `uk_obr_tables`: REWORK.**

The extracted numbers are sound. Every workbook total I compared matches HM Treasury's Table 6.1 within its £5m rounding, and components sum to their totals. The PDF and aggregates rows match the primaries. The rework is confined to how rows are keyed and typed, which design rows were staged, and the NOTES.md rewrite that follows. It is systematic, not a few slips. NOTES.md itself describes five proposed keys as "Component of Table 6.1 line 45/47/77" and still leaves them unkeyed, against rule 9. It also staged all of Table 3.2 and several other design inputs, and keyed the Table 3.3 tax-head figures as if they were whole-measure totals. Every fix below is exact, so the lane can apply them quickly.

**Three things I could not do.** This session had file read and search only, with no shell.
- **Hashes and contract:** I did not recompute the sha256 hashes or run the contract. Before merging, run `shasum -a 256` on the three primaries and run the contract. Two notes on that:
  - The two workbook hashes in `manifest.jsonl` match the ones recorded independently in `PROVENANCE.md` on 28 October. The PDF's hash has no second source.
  - `pipeline/ab2026_harvest_contract.py` has uncommitted changes in this worktree, and the 7 rating rows use `value_kind: "categorical"`. Run the committed version of the contract, so the lane's "0 problems" doesn't depend on the local edit.
- **The seeded sample:** I could not draw the `random.Random(231)` sample. I used a stratified sample of 110 rows instead (listed at the end).
- **Workbook cells:** I could not open the xlsx files. Workbook rows were checked against HM Treasury Table 6.1, against Table 3.3, and by the component-to-total identity.

Row indices are 0-based. Row *i* is line 639+*i* of `stage.py`'s `CELLS` block, which the gzip reproduces.

---

## Findings, most serious first

### 1. Design rows (rule 8): drop 57 rows, plus 1 probable

**The 35 `compliance_funding` rows: confirmed, all 35 are spending allocations.** Table 3.2 (printed p.68, PDF p.71) is headed "Funding costs of HMRC and DWP baseline and newly announced compliance, debt and fraud and error activity", with "Source: HM Treasury". Paragraph 3.14 calls it "the funding provision". The table has no yield or net Exchequer line, so no row stays.

The same applies to the 12 Table 3.2 rows the coordinator didn't list. These are the "Budget 2026 additional" lines, which carry `metric: operating_cost_change`:
- Rows 2711–2716 carry proposed key `…tax_administration_compliance_and_debt`.
- Rows 2734–2739 carry `measure_key: ab2026__dwp_fraud_and_error_prevention` with no row type. An ingest would read them as line-47 estimates.

They are not the scored costs either. Table 3.2's DWP line prints −16, 188, 178, 188, 210, 214, while the workbook's measure-47 departmental spending cells print 218, −194, −184, −195, −217, −221.

| Category | Rows | Count |
|---|---|---|
| Funding allocations (Table 3.2): baseline, Budget 2025 and total lines (`compliance_funding`) | 2699–2710, 2717–2733, 2740–2745 | 35 |
| Funding allocations (Table 3.2): Budget 2026 additional lines | 2711–2716, 2734–2739 | 12 |
| Staffing inputs to the measures (2,000 / 200 / 150 DWP staff; 5,500 and 670 HMRC staff; "23 per cent increase") | 2689, 2690, 2691, 2695, 2696, 2697 | 6 |
| Guarantee capacity, a contingent liability (UKEF £40bn; Growth Guarantee Scheme £7bn) | 2776, 2778 | 2 |
| Lending allocation (Your First Home loans £0.7bn and £1bn) | 2782, 2783 | 2 |
| Probable financing allocation: "raises the Government's financing requirement by £1.9 billion a year" (paragraph 3.20); coordinator's call | 2771 | 1 |

**Fix:** drop rows 2689–2691, 2695–2697, 2699–2745, 2776, 2778, 2782, 2783, and probably 2771. Move the staffing figures into the `reform_hint` or `conditions` of the yield rows.

### 2. Components carrying proposed keys instead of their measure's key (rule 9): re-key 37 rows

For each group below: set `measure_key`, remove `conditions.proposed_measure_key`, and set `conditions.row_type: "measure_component"` with the `component` given. On rating rows, set only `component`.

| Rows | Producer's figure | Evidence it is part of one line | Fix |
|---|---|---|---|
| 2797–2801, 2802 | Table 3.3 "Direct recovery of debt" | NOTES says it is a component of line 45 | `ab2026__hmrc_tax_gap_package`, component "Direct recovery of debt (Table 3.3, Tax head)" |
| 2821–2825, 2826 | Table 3.3 "E-invoicing mandation" | same | same key, component "E-invoicing mandation" |
| 2616–2621, 2538, 2693, 2827 | "Timely payment for self-assessment" (Table 3.1, paragraphs 3.4, 3.13, 3.25) | same | same key, component "Timely payment for self assessment" |
| 2694 | £0.4bn from the compliance workforce changes | same | same key, component "Changes to HMRC's compliance workforce" |
| 2809–2813, 2814 | Table 3.3 "Verification assurance officers" (Spend head) | NOTES says it is a component of line 47 | `ab2026__dwp_fraud_and_error_prevention`, component "Verification assurance officers (Table 3.3, Spend head)" |
| 2833 | India–UK free trade agreement, +0.13% of GDP by 2040 | NOTES says it is part of line 77 | `ab2026__uk_india_ceta_and_double_contributions_convention`, component "India-UK FTA (CETA) GDP effect" |
| 2815–2819, 2820 | Table 3.3 "Company Share Option Plan scheme reform": 26 / 33 / 47 / 143 / 141 | Workbook line 28 (EMI2) total: −26 / −33 / −47 / −144 / −142. HM Treasury: −25 / −35 / −45 / −145 / −140. Same costing under OBR's name; paragraph 3.24 describes the line-28 policy. | `ab2026__emi2_option_limit_120000`, component "Tax head (Table 3.3; OBR title: Company Share Option Plan scheme reform)" |
| 2777 | UK Export Finance "reduces borrowing by £0.2 billion a year" | Workbook line 44 total: 0 / 200 / 200 / 200 / 200 / 0; HM Treasury identical | `ab2026__uk_export_finance_defence_capacity`, no component. Also set `period: 2031`, `fy: "2030-31"`: line 44 is 0 in 2031-32, so the staged year is wrong. |
| 2779, 2780, 2781 | Growth Guarantee Scheme: +£0.1bn, +£0.1bn, +£0.2bn borrowing | Workbook line 75: −103 / −143 / −181 / −168 / −159 / −155, the same profile. The £7bn and £6.5bn are different quantities of the same measure (guarantee capacity versus lending supported). | `ab2026__growth_guarantee_scheme_expansion` |
| 2540, 2747 | Writing-down allowance and first-year allowance, "£1 billion a year on average from 2027-28" | Workbook line 58: 766 / 1040 / 1077 / 1100 / 1121, averaging about £1.02bn. The date difference is a description difference, not a scope difference. | `ab2026__writing_down_allowance_12pc_and_fya_50pc`, keeping the date note |

After these fixes and the drops in finding 1, nine proposed keys have no rows left: `…direct_recovery_of_debt`, `…e_invoicing_mandation`, `…timely_payment_self_assessment`, `…hmrc_compliance_workforce`, `…verification_assurance_officers`, `…india_uk_free_trade_agreement`, `…company_share_option_plan_reform`, `…additional_uk_export_finance_guarantees` and `…growth_guarantee_scheme_7bn`. `…wda_and_first_year_allowance_as_printed` also goes if the coordinator accepts the re-key of 2540 and 2747.

### 3. Keyed rows that are parts of a measure but carry no row type: set `row_type: "measure_component"`

- **Table 3.3 rows 2785–2789 (line 54), 2791–2795 (line 61) and 2803–2807 (line 46).** Table 3.3's "Head: Tax" values are the measure's receipts only, not its total.
  - Line 61: receipts 2+0 / 539+4 / 394+6 / 403+8 / 412+10 equal Table 3.3's −2 / −543 / −400 / −411 / −422 exactly. The total is 34 / 575 / 433 / 445 / 457.
  - Line 54: receipts give 105 / 478 / 688 / 677 / 657, against Table 3.3's −105 / −479 / … The total is 111 / 496.
  - Fix: add `row_type: "measure_component"` and `component: "Tax head (receipts), Table 3.3"`.
- **Behavioural effects:**
  - Rows 2749 (−£190m, bank surcharge), 2753 (−£0.2bn, savings) and 2755 (−£0.1bn, property): set `row_type: "measure_component"`; their `component` already reads "behavioural erosion of yield".
  - Row 2749 also needs `value_kind: "cumulative"`, as on its sibling row 2748.
- **Row 2688** (DWP, "reduce welfare spending by £0.5 billion in 2031-32"): this is the welfare part of line 47; the workbook's welfare cells give 367+97=464. Set `row_type: "measure_component"`, `component: "welfare spending (AME), para 3.12"`.

### 4. Two workbook summary rows carry a sign convention that misdescribes them

- Rows 2514–2519 (cell row 555, indirect effect) carry the workbook legend "negative = loss to the Exchequer". Their signs actually follow PSNB: −1,308 / 3,483 / … against Table 3.1's −1.3 / 3.5 / …
- Rows 2490–2495 (cell row 549) are the arithmetic sum of rows 551 and 555 (−7,597 + −1,308 = −8,905), so they mix the two conventions.
- The notes explain this, but `conditions.sign_convention` is what an ingest reads.
- **Fix:**
  - On rows 2514–2519, set `sign_convention` to "positive = increase in PSNB (matches EFO Table 3.1; contradicts the workbook legend)".
  - On rows 2490–2495, set it to "mixed: row 551 (negative = loss to Exchequer) plus row 555 (positive = increase in PSNB)".

### 5. Text figures that repeat a staged table cell (recommended; coordinator's call)

The AB2025 OBR family didn't re-stage these ("the table cells are the staged rows"). This is that family's choice, not a README rule.
- **Text that repeats a Table 3.1 cell:** 2520–2524, 2527, 2528, 2534, 2536, 2537, 2678, 2679, 2680, 2692, 2746, 2751, 2759–2761.
- **Text that repeats earlier text:** 2681 (=2529), 2682 (=2533), 2683 (=2531), 2687 (=2530), 2693 (=2538), 2747 (=2540).
- **Repeats within Table 3.1:** the "Spending measures" rows 2574–2579 repeat "Direct effect of spending measures" (2550–2555). The "Tax measures" rows 2604–2609 repeat "Direct effect of tax measures" (2556–2561).

If rows 2693 and 2747 are dropped here, their re-keys in finding 2 fall away.

### 6. Smaller field fixes

- **Row 2774** (£0.6bn of additional National Wealth Fund / British Business Bank investment income) uses `metric: income_aggregate`. In `models.py` that metric is the CBO tax-return income aggregate. Set `metric: "decisions_effect_on_borrowing"` with `component: "gross additional investment income"`, or `metric: null` with a proposal.
- **Row 2828** (paragraph 3.28, the Budget 2025 salary-sacrifice measure's yield revised up by £0.4bn) could carry `measure_key: ab2025__salary_sacrifice_pension_nics_cap_2000` with `conditions.recosting_of: "autumn_budget_2025"`. The contract accepts that. This is optional; the lane's assignment kept the key null.

### 7. Family-level: stale and extra files

- **`REPORT.md`:** no other family carries one, including `uk_hmt_tables` and the AB2025 families. It numbers rows from 1 and uses a different seed. Delete it and replace NOTES.md's "See `REPORT.md`" paragraph with a one-line validation statement.
- **The PDF's manifest note** says its provenance is in `PROVENANCE.md`, but that file doesn't list the PDF. Change the note to say the PDF's origin and hash are recorded only by this lane.
- **Absolute local paths** (`/Users/maxghenis/…`) appear in NOTES.md and in all three manifest notes. Replace them with a relative description.

### 8. Family-level: NOTES.md rewrite after fixes 1–3

Recompute the per-key and proposed-key tallies, and the 70 `restated` rows, which fall to 23 once Table 3.2 goes. Remove the dropped proposals. Add the rule-8 exclusions (funding, staffing, guarantee capacity, loan totals) to "Not staged".

The current tallies do match the current rows. I checked the 37 proposed-key counts, which sum to 620 (365 + 47 + …). I also checked 17 per-key counts, including lines 1, 2, 3, 45, 47, 54, 61 and 62, and the coverage lines (2,520 / 316 / 55).

### 9. Proposed-key naming (low; the coordinator unifies these)

- **Single measures named as packages:** landlord registration fee, PWLB debt relief, Scottish APD devolution, the 2031-32 departmental spending decision, the public-sector pensions valuation and the adjusted triple lock. Rule 2 names these `ab2026__<slug>`, not `ab2026__package_obr_<slug>`.
- **Scope-defined packages with `obr` in the slug.** For lines 61+62 the README's own example key is `ab2026__package_property_and_savings_income_rates`. Note that Table 3.1 may be a receipts-only grouping (−0.1 in 2027-28, against workbook totals of 34+126), so check its scope before unifying.
- **No proposed key equals a registered package.** The fuel duty and VAT package is lines 2+3, not the registered 1+2+3: workbook 755+574 = 1.3, as printed.

### 10. Completeness (low)

- **Box 3.1 (p.66)** prints "Of the compliance measures announced in this Budget, a third of the yield is expected to reduce the tax gap". That is an AB2026-specific OBR estimate, neither staged nor listed as not staged. Stage it or list it.
- **Everything else in chapter 3** that is in scope is staged or excluded with a reason, including paragraphs 3.29, 3.35–3.36 and 3.48, and paragraph 3.52's 2075-76 figures, which the checker's 2075 cap rules out.
- **Chapters 4–6:** I did not skim them exhaustively.
- **Electricity VAT:** paragraph 3.19 prints £0.7bn where the workbook and HM Treasury have 755. It is staged as printed, which is correct.

---

## Checks passed

- **Identity (17 measures, every year):** lines 1–10, 45 and 47; PWLB, Scottish APD and landlord fee; the departmental spending decision; pensions. All are within ±1, except line 45 in 2031-32, which is +3 across 13 components and within rounding. There were no failures. The summary rows also reconcile: 551 = 552 + 553, and 549 = 551 + 555.
- **Workbook totals against HM Treasury Table 6.1** (lines 1, 2, 28, 44, 45, 46, 54, 58, 61, 62, 70, 75, 77): all within ±£5m.
- **Primaries:** I compared Tables 3.1, 3.2 and 3.3 against the PDF page images, and `efo.txt` matches. Table 7.1 and Table A.9 match `efo.txt`. The workbook's Tables 6.5 and 6.13 match A.9.
- **Page locators** are right: printed page + 3 = physical page.
- **Rows and quotes:** every row's `primary_sha256` is one of the three manifest primaries. Every quote is a whole cell or whole OGL sentence, and each one I checked appears in the primary.
- **Attribution:** 70 restated rows, 2,821 own, as in NOTES.md. `restated` on the fuel-duty rows (per the EFO's p.59 footnote 1), the Health Foundation rows, the India FTA row and the ONS outturn rows is right.
- **Metrics:** all used metrics are registered in `models.py`.

## Sample: 110 rows, stratified (not Random(231))

✓ means value_raw, value, period, fy, quote and conditions matched. Notes refer to the findings above.

**Components (21):**

| Row | Locator | Result |
|---|---|---|
| 0 | I10, −2627 | ✓, identity |
| 15 | L13, 0 | ✓ |
| 18 | I14, −734 | ✓ |
| 30 | I17, −574 | ✓, restated |
| 49 | J21, 173 | ✓ |
| 61 | J24, −170 | ✓ |
| 78 | I27, −7 | ✓ |
| 99 | L31, −69 | ✓ |
| 112 | M34, −33 | ✓ |
| 127 | J38, −142 | ✓ |
| 852 | I198, 0 | ✓ |
| 861 | L199, 1487 | ✓ |
| 905 | N206, 4 | ✓ |
| 911 | N207, −186 | ✓ |
| 948 | I216, 218 | ✓ |
| 959 | N217, 367 | ✓ |
| 1123 | J252, 104 | ✓, matches Table 3.3 |
| 1352 | K297, 539 | ✓, matches Table 3.3 |
| 2125 | J470, 423 | ✓ |
| 2148 | I475, −10 | ✓ |
| 2173 | J485, 15433 | ✓ |

**Measure totals (20):** all ✓, either against HM Treasury or by identity.

| Row | Cell and value | Row | Cell and value |
|---|---|---|---|
| 6 | I11, −2627 | 1293 | L284, 1077 |
| 25 | I15, −755 | 1385 | N302, 457 |
| 37 | J18, −782 | 1401 | L306, 521 |
| 54 | I22, −50 | 1507 | J333, −1235 |
| 90 | I29, −28 | 1599 | L353, −168 |
| 125 | N36, −79 | 1643 | N362, −402 |
| 596 | K138, −33 | 942 | I214, 0 |
| 847 | J196, 200 | 2118 | I468, 0 |
| 933 | L211, 1978 | 2189 | N487, −1169 |
| 966 | I219, 193 | 1167 | L259, 688 |

**Summary (9):**

| Row | Cell and value | Result |
|---|---|---|
| 2190 | I490, −1,749 | ✓ |
| 2209 | J495, 1,053 | ✓ |
| 2461 | J543, −353 | ✓ |
| 2484 | I547, 40 | ✓ |
| 2490 | I549, −8,905 | value ✓; sign convention wrong (finding 4) |
| 2496 | I551, −7,597 | ✓ |
| 2502 | I552, −7,597 | ✓ |
| 2513 | N553, 4,331 | ✓ |
| 2519 | N555, 2,412 | value ✓; sign convention wrong (finding 4) |

**No row type (60):** values matched the primary in every case; the notes flag other findings.

| Row | Locator | Value | Result |
|---|---|---|---|
| 2520 | paragraph 3.2 | £7.6bn | ✓ (finding 5) |
| 2525 | paragraph 3.2 | £12bn | ✓ |
| 2526 | paragraph 3.3 | £3.3bn | ✓ |
| 2528 | paragraph 3.3 | £2.6bn | ✓ (finding 5) |
| 2533 | paragraph 3.3 | £5.5bn | ✓ |
| 2535 | paragraph 3.4 | £6bn | ✓ |
| 2538 | paragraph 3.4 | £1.6bn | ✓ (finding 2) |
| 2540 | paragraph 3.4 | £1bn | ✓ (finding 2) |
| 2541 | paragraph 3.4 | £1bn | ✓ |
| 2544 | Table 3.1 | 6.3 | ✓ |
| 2568 | Table 3.1 | 7.6 | ✓ |
| 2580 | Table 3.1 | 2.6 | ✓ |
| 2615 | Table 3.1 | −3.6 | ✓ |
| 2621 | Table 3.1 | −1.8 | ✓ (finding 2) |
| 2640 | Table 3.1 | 1.3 | ✓ |
| 2652 | Table 3.1 | 7.6 | ✓ |
| 2670 | paragraph 3.6 | £1.3bn | ✓ |
| 2672 | paragraph 3.10 | 0.08pp | ✓ |
| 2675 | paragraph 3.10 | 0.22pp | ✓ |
| 2684 | paragraph 3.12 | £17bn | ✓ |
| 2686 | footnote 5 | <0.1pp | ✓ |
| 2688 | paragraph 3.12 | £0.5bn | ✓ (finding 3) |
| 2689 | paragraph 3.12 | 2,000 | design (finding 1) |
| 2694 | paragraph 3.13 | £0.4bn | ✓ (finding 2) |
| 2695 | paragraph 3.13 | 5,500 | design (finding 1) |
| 2698 | paragraph 3.13 | £1.4bn | ✓ |
| 2699 | Table 3.2 | 2,715 | design (finding 1) |
| 2734 | Table 3.2 | −16 | design (finding 1) |
| 2745 | Table 3.2 | 1,557 | design (finding 1) |
| 2748 | paragraph 3.16 | £1.5bn | ✓ |
| 2749 | paragraph 3.16 | £190m | ✓ (finding 3) |
| 2753 | paragraph 3.17 | £0.2bn | ✓ (finding 3) |
| 2762 | paragraph 3.19 | £0.4bn | ✓ |
| 2763 | paragraph 3.19 | £0.6bn | ✓ |
| 2767 | paragraph 3.19 | £0.7bn | ✓ |
| 2771 | paragraph 3.20 | £1.9bn | probable design (finding 1) |
| 2774 | paragraph 3.20 | £0.6bn | ✓ (finding 6) |
| 2776 | paragraph 3.21 | £40bn | design (finding 1) |
| 2777 | paragraph 3.21 | £0.2bn | ✗ wrong year (finding 2) |
| 2778 | paragraph 3.21 | £7bn | design (finding 1) |
| 2782 | paragraph 3.22 | £0.7bn | design (finding 1) |
| 2784 | paragraph 3.22 | £0.7bn | ✓ |
| 2785 | Table 3.3 | −105 | ✓ (finding 3) |
| 2790 | Table 3.3 | High | ✓ |
| 2797 | Table 3.3 | 0 | ✓ (finding 2) |
| 2812 | Table 3.3 | −255 | ✓ (finding 2) |
| 2815 | Table 3.3 | 26 | ✓ (finding 2) |
| 2827 | paragraph 3.25 | £17bn | ✓ (finding 2) |
| 2828 | paragraph 3.28 | £0.4bn | ✓ (finding 6) |
| 2829 | paragraph 3.41 | £3.5bn | ✓ |
| 2831 | paragraph 3.43 | £4.3bn | ✓ |
| 2833 | paragraph 3.47 | 0.13% | ✓ (finding 2) |
| 2834 | paragraph 3.51 | 1.4% | ✓ |
| 2836 | Table 7.1 | 0.4 | ✓ |
| 2848 | Table 7.1 | −2.8 | ✓ |
| 2849 | Table A.9 | 81.4 | ✓ |
| 2863 | Table A.9 | 134.3 | ✓ |
| 2877 | Table A.9 | 3,633 | ✓ |
| 2878 | workbook 6.5 C14 | 133.2 | ✓ |
| 2884 | workbook 6.13 C23 | 88.9 | ✓ |
| 2890 | workbook 6.13 I23 | 94.0 | ✓ |

The sample covers all three primaries and all four row types. I read the template behind every proposed key and every PDF and aggregates row.