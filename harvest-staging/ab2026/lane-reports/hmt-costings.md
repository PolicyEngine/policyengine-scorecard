I staged `uk_hmt_costings`: 597 rows from one primary. The contract checker reports 0 problems, and re-running `stage.py` reproduces the gzip byte for byte. Nothing is committed; the family directory is ready for you to copy.

**Rule change mid-task.** While I was staging, someone edited the AB2026 README (new rules 8 and 9) and `pipeline/ab2026_harvest_contract.py` in my worktree. I didn't touch either file, but I re-staged to the new rules:
- **Rule 8** dropped 11 rows that are contingent liabilities or allocations: UK Export Finance's guarantees, the Growth Guarantee Scheme's supported lending and the British Business Bank recapitalisation split.
- **Rule 9** re-keyed the parts of Table 6.1 lines 29, 45, 47, 56, 72, 77, 84 and 85 to their line's key as `row_type: measure_component`; before, I had given them proposed keys.

If those edits don't land, the families staged before them will disagree with this one.

## `uk_hmt_costings` (source `hm_treasury`)

**Primary:** HM Treasury, *Budget 2026: Policy Costings* (PU 3699).
- sha256 `f716efada8a4d0726ce12b0f97d3f0dac671c31b2d005ecf300a48ff309638bf`, 745,488 bytes.
- Fetched directly on 2026-10-29 with HTTP 200. The bytes are identical to the local copy from 28 October, so the document hasn't changed.

**Rows: 597.**
- **576 Exchequer impact cells:** 96 costing notes × 6 years. Every note prints exactly one table, so no static or post-behavioural legs exist to stage, and all are `scoring_method: final`.
- **21 text rows:**
  - 8 behavioural parameters;
  - 7 PSND/PSNFL impacts;
  - 2 eligible counts;
  - 2 tax-gap rows;
  - 1 tax base;
  - 1 financial-transaction impact.

**Rows by measure key:**
- **68 whole-line keys:** 416 rows. Each has 6 rows except Parental Allowance (9), Business Rates Retention (7) and Leeds City Fund (10).
- **Components (8 line keys, 159 rows):**

| Table 6.1 line | Rows | Notes |
|---|--:|---|
| 45 (HMRC tax gap package) | 62 | 10 |
| 47 (DWP fraud and error) | 31 | 5 |
| 29 (BBB Backing Innovation) | 16 | 2 |
| 56 (Machine Games Duty) | 14 | 2 |
| 77 (UK-India) | 12 | 2 |
| 84 (Waste Crime) | 12 | 2 |
| 72 (Youth Guarantee, AME savings only) | 6 | 1 |
| 85 (Erasmus+, placed by its position in the document) | 6 | 1 |

- **Null key:** 22 rows across the three proposed keys below.

**Proposed keys:**
- `ab2026__british_business_bank_defence_commitments_accelerated` (p.41, 9 rows): "British Business Bank: Accelerate £450m of commitments to support defence-related and dual-use businesses". Its position puts it among lines 40–43, but no line's title or figures match it.
- `ab2026__private_landlord_register_fee_65` (p.108, 7 rows): the £65 'Register your rental property' fee. Table 6.1's footnote 2 excludes it.
- `ab2026__pwlb_debt_relief_councils_severe_distress` (p.109, 6 rows): also excluded by footnote 2.

**Conventions worth knowing:**
- **Exchequer signs** are as printed: + is a yield, – a cost. The document prints no legend, so this comes from the notes' own wording and Table 6.1.
- **PSND/PSNFL figures** are printed unsigned with words like "cost" and "benefit". I put all seven on the Exchequer convention (+ means an improvement).
- **Fair-value increments** (£68m on p.34, £86m on p.41) are a new proposal, `psnfl_fair_value_impact`, rather than PSNFL totals.
- **The tax gap rows** (6.4% and £59.2bn for 2024–25, p.50) are `restated`, because they repeat HMRC's statistic. They carry line 45's key as a component.

## Not staged
- **Design numbers (rule 8):** rates, thresholds, amounts, dates and durations.
- **Contingent liabilities:** UK Export Finance's £10bn of guarantees a year; the Growth Guarantee Scheme's supported lending (£1.0bn, £1.5bn and £2.0bn a year, £6.5bn in total).
- **Allocations and staff:** the British Business Bank's £1,405m/£165m/£450m split; £70m and £485m of HMRC spending; staff numbers.
- **Other exclusions:**
  - numbers printed only in titles;
  - p.91's 4.1% and 7.1% baseline rates;
  - p.58's –£35m, which repeats a table cell;
  - p.94's £0.6bn, allocated at an earlier event;
  - Annex A.
- **Uncertainty ratings:** the document prints none.
- **Charts and unreached pages:** none.

NOTES.md lists every unstaged number page by page.

## Checks
- **Contract checker:** `uk_hmt_costings: 597 rows, 0 problems`.
- **Byte stability:** re-running `stage.py` gives the same sha256, `0d42e2390171a4530f7c2088560d74d81d5ec4d2f063933129058fcc7f7ae2a7`.
- **`stage.py --verify`:** it checks every row against its cited page, including the value's column and the sign of text figures. All 597 pass, and a mutation test confirmed it catches wrong values, swapped columns, wrong labels, sign or scale errors and wrong titles.
- **Repository harvest tests:** 8 pass and 2 fail. Both failures are only because `COUNTS.json` doesn't pin this family yet. The pin entry is: rows 597, primaries 1, sources `["hm_treasury"]`, claims_sha256 `0d42e239…`.
- **Spot check against the PDF:** all 16 rows match in number, sign, unit and period. I reviewed one complete note's six rows (p.15) and checked the other 15 rows as single cells.

| Row | Locator | Year | Value | Key |
|---|---|---|---|---|
| 102 | p.28 | 2028-29 | –45m | line 21 |
| 166 | p.39 | 2028-29 | +0m | line 38 |
| 263 | p.54 | 2030-31 | +40m | line 47 component |
| 280 | p.57 | 2029-30 | +15m | line 47 component |
| 315 | p.63 | 2027-28 | –45m | line 52 |
| 354 | p.69 | 2028-29 | +10m | line 57 |
| 386 | p.75 | 2030-31 | +555m | line 62 |
| 447 | p.85 | 2027-28 | –260m | line 77 component |
| 518 | p.97 | 2026-27 | –15m | line 88 |
| 537 | p.100 | 2027-28 | +70m | line 91 |
| 547 | p.101 | 2031-32 | +0m | line 92 |
| 573 | p.106 | 2027-28 | +40m | line 97 |

  Text rows checked: p.15's 166,000 (persons, 2026), p.41's £54m (cumulative to 2031-32), p.50's £59.2bn (2024-25) and p.84's £20m (2028-29).
- **Independent reviews:** three reviewers checked all 576 cells and every text row and found no wrong values. Their labelling and NOTES findings are all fixed, and a second round confirmed the fixes.

## Cross-check against Table 6.1
All 68 whole-line keys equal Table 6.1 in every year. Where a line has several notes, I compared the notes' sum (computed for this check only, never staged):
- **Line 56:** 140 against 145 in 2031-32.
- **Line 77:** –170 against –175 in 2026-27.
- **Line 84:** –4/–3/–3 against –5/–5/–5. These three gaps are all £5m or less, which fits rounding.
- **Line 45:** the notes sum higher than the line in every year: 110, 290, 240, 2,140, 2,635 and 3,360, against 10, 100, 115, 1,980, 2,485 and 3,160.
- **Line 47:** the gaps (line minus notes) are +205, –135, –65, +10, +10 and +5.
- **Line 72:** the note prints the AME savings only (+25, +35) against the line's –290 and –375.

p.58's +£130m financial transaction equals Table 6.2 line 9 for 2029-30.

## Things in the primary that look wrong
- **The £10m threshold.** The introduction says measures under £10m in every year are left out, yet pp.59, 92 and 93 print costings below that and pp.33 and 109 print zeros. Table 6.1's footnote 2 says the same, yet lines 48 and 84 are under £10m every year and still appear.
- **Lines 45 and 47.** Footnote 4 says the full costings for these packages are in this document, but the notes don't sum to the lines and nothing explains the gaps.
- **Missing titles.** No Table 6.1 title names the BBB defence measure (p.41) or Erasmus+ (p.94).
- **Minor wording.** p.77 drops the years from its title ("25 June to 1 September"). p.16's title says "Earning Limit" while its text says "Earnings Limit".

Files are in `sources/harvest-uk-ab2026-2026-10-29/uk_hmt_costings/`:
- NOTES.md
- manifest.jsonl
- claims_staged.jsonl.gz
- stage.py

DONE