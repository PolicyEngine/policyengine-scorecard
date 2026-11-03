# Verifier report: `uk_hmt_costings` (source `hm_treasury`, 597 rows)

## Verdict: **APPROVE WITH FIXES**

The 576 Exchequer cells are right. I checked all 68 whole-line notes against Table 6.1 in every year, and they match. I checked every component line's arithmetic, and it matches what the lane reports. I compared 46 of the 96 notes' tables with the PDF page images. The 21 text rows match their pages, and none of them is a design number. One keying error needs a fix: the two tax-gap rows. The other findings are documentation fixes.

**Checks I couldn't run.** This session had no shell, so I could not compute hashes, run Python or open the gzip. As a result:
- I did not recompute the PDF's sha256.
- I did not run `pipeline/ab2026_harvest_contract.py`.
- I did not draw the sample with `random.Random(231)`.

Instead, I read the rows from `stage.py`, which the lane says rebuilds the gzip byte for byte. I checked them against page images of the PDF, and against Table 6.1's figures as the registry records them (`data/uk/ab2026_measures.json`, each line's `source_note`). Row indices below follow `stage.py`'s build order. They hold only if the gzip on disk equals a fresh build. Before merging, please run:
- `shasum -a 256 .ab2026-primaries/uk_hmt_costings/AB26_Policy_Costing.pdf` (expect `f716efad…638bf`);
- `PYTHONPATH=. python3 pipeline/ab2026_harvest_contract.py sources/harvest-uk-ab2026-2026-10-29/uk_hmt_costings`;
- `python3 sources/harvest-uk-ab2026-2026-10-29/uk_hmt_costings/stage.py --verify .ab2026-primaries/uk_hmt_costings/AB26_Policy_Costing.pdf`.

I also read the contract code against `stage.py`'s row builders and found nothing that would fail it:
- every field is allowed;
- `eligible_count`, `revenue_change`, `persons`, `percent`, `gbp` and `properties` all exist in `scorecard_db/models.py`;
- each row has exactly one of `metric`/`proposed_metric` and one of `unit_concept`/`proposed_unit`;
- `fy` and `period` agree;
- component rows name their component and key;
- all three proposed keys appear in NOTES.md;
- every row's `primary_sha256` is the manifest's.

## Findings, most serious first

### 1. Rows 233 and 234 (p.50, UK tax gap 6.4% and £59.2bn): mis-keyed as a component of line 45
- **What's wrong:** both rows carry `measure_key: ab2026__hmrc_tax_gap_package` with `row_type: measure_component`, `table_61_line: 45` and component "Tax Compliance: … 670 officers".
  - Rule 9 defines a component as "a printed part of one Table 6.1 measure". The UK tax gap is not a part of the tax-gap package. It is HMRC's whole-economy statistic.
  - It isn't even the costing's base. p.50 says: "The tax base for this costing is the total tax gap less the additional tax revenues accounted for by previously announced Closing the Tax Gap (CTG) initiatives."
  - The AB2025 contract's rule 3 says a context claim that scores no measure has `measure_key: null` and `reform_hint: null`.
  - `stage.py`'s own `text_rows` docstring says "A context row (the tax gap) scores no measure: null key and reform_hint, no mapping conditions". The code path exists, but neither p.50 entry sets it.
- **Evidence:** p.50, "The tax base": "The UK tax gap in 2024 to 2025 is estimated to be 6.4% of total theoretical tax liabilities, or £59.2 billion in absolute terms."
- **Fix:**
  - Add `'context': True` to both p.50 entries in `TEXT_CLAIMS` and re-run `stage.py`. The rows then get `measure_key: null` and `reform_hint: null`, and lose `row_type`, `component` and `table_61_line`.
  - Keep `restated`, `administrative_fact`, `administrative_data` and fy 2024-25.
  - Update NOTES.md:
    - "76 registry keys on 575 rows" → "76 registry keys on 573 rows";
    - "159 rows … `measure_component`" → "157 rows";
    - the text-rows table row for p.50: "line 45, component p.50" → "context (`measure_key: null`)";
    - "The tax gap" bullet: replace "so the two rows carry the note's line key (line 45, component p.50)" with "but the total tax gap is a context figure, not a part of the measure, so the two rows carry `measure_key: null` (AB2025 rule 3)".

### 2. Rows 176–184 (p.41, BBB defence, proposed `ab2026__british_business_bank_defence_commitments_accelerated`): keep the proposed key, but state the risk of double counting
- **My judgement:**
  - A proposed key is the right call, because no figure ties the note to any line.
  - But NOTES.md uses an argument for Erasmus+ that it doesn't apply here. Footnote 2 leaves out only pp.108–109, and the note exceeds the £10m bar: it prints +10, +20, +25 and +30 in 2028-29 to 2031-32. So the costing almost certainly sits inside some Table 6.1 line.
  - It can't be line 29: pp.33 and 34 sum exactly to line 29 (0, 5, 0, 5, 10, 25).
  - It can't be line 44: p.42 equals line 44 exactly.
  - Its position leaves lines 40–43, and only line 41 has a SUBTOTAL head.
- **Risk:** as written, the key reads as a measure with no Table 6.1 line, so tranche 2 could add it on top of Table 6.1's lines or totals.
- **Fix:** append this sentence to NOTES.md's p.41 bullet, to the p.41 scope cell in the proposed-keys table, and to the p.41 `mapping_note`: "By Table 6.1's footnote 2 and its £10m bar, this costing is very probably inside a Table 6.1 line, most plausibly line 41 (lines 29 and 44 are fully accounted for by their own notes); tranche 2 must never add it to Table 6.1 lines or totals."

### 3. Line 45 and 47 component rows (indices 191–252 and 259–289): `mapping_note` overstates coverage
- **What's wrong:** each note says "The line's figure covers the whole package". A reader could take that to mean the components add up to the line, but they don't.
  - The cross-check section of NOTES.md records the gaps clearly, and no row invites summing. This is low severity.
- **Fix:** in `stage.py`'s line 45 and 47 mapping notes, append:
  - line 45: "These ten notes do not sum to the line: Table 6.1 is lower by 100, 190, 125, 160, 150 and 200."
  - line 47: "These five notes do not sum to the line: Table 6.1 differs by +205, −135, −65, +10, +10 and +5."

### 4. Family-level: uncommitted changes outside this family
- The worktree's git status shows `sources/harvest-uk-ab2026-2026-10-29/README.md` and `pipeline/ab2026_harvest_contract.py` as modified. I couldn't diff them. Check the diff before merging, and merge only `uk_hmt_costings/` from this lane unless the coordinator wrote those edits.

### 5. Minor; no change needed
- **Row 436–439 (p.84, £20m a year):** staging this as a `behavioural_parameter` is borderline. The page says "Borrowing is estimated as £20 million of additional capital borrowing annually", which is a costing estimate rather than a remit, so I accept it. The note's `behavioural_adjustment` is "not stated", but the lexical rule explains that.
- **Row 283 (p.58, +£130m):** this equals Table 6.2 line 9's 2029-30 cell in `uk_hmt_tables`. The two rows have different `row_type`s and NOTES.md records the overlap, so this is acceptable.

## Checks that pass

- **Whole-line identity (68 keys, 408 table cells):** every value equals Table 6.1 in all six years. There are 0 mismatches.
- **Component identity:** each claim below is confirmed from the costing notes and Table 6.1.

| line | components | Table 6.1 | result |
|---|---|---|---|
| 29 | 0, 5, 0, 5, 10, 25 | same | equal |
| 56 | sum 140 in 2031-32 | 145 | within £5m; other years equal |
| 77 | sum −170 in 2026-27 | −175 | within £5m; other years equal |
| 84 | sums −4, −3, −3 in 2027-28 to 2029-30 | −5, −5, −5 | within £5m |
| 72 | AME component prints +25 and +35 | −290 and −375 | p.82 label confirmed: "Exchequer impact [AME savings only]" |
| 45 | sums 110, 290, 240, 2,140, 2,635, 3,360 | 10, 100, 115, 1,980, 2,485, 3,160 | gaps as NOTES.md says |
| 47 | sums −10, 10, 125, 65, 145, 235 | 195, −125, 60, 75, 155, 240 | gaps as NOTES.md says |
| 85 | Erasmus+ −5, 0, −15 in 2029-30 to 2031-32 | −5, 0, −15 | equal in those years; a component by elimination, which I accept |

- **The other two proposed keys:**
  - `private_landlord_register_fee_65` (p.108) and `pwlb_debt_relief_councils_severe_distress` (p.109) are the two measures footnote 2 leaves out.
  - Neither matches a registered key or package. `REGISTRY_KEYS.md` has only the 3 totals packages, `household_energy_vat_and_fuel_duty` and `policyengine_seven`.
- **Conventions:**
  - **PSND/PSNFL signs:** the seven rows put "net cost", "a cost of" and "add an additional cost of" as negative, and "benefit" and "value … increases by" as positive. That is consistent: −32 + 86 = +54 on p.41.
  - **`psnfl_fair_value_impact`:** this is right for the £68m (p.34) and £86m (p.41), because both are increments, not PSNFL totals.
  - **Tax-gap attribution:** `restated` is right. Only the key is wrong (finding 1).
- **Rule 8 (design rows):** 0 design rows. By category: rates 0, thresholds 0, payment amounts 0, dates and durations 0, allocations 0, remits 0, contingent liabilities 0, staff numbers 0.
  - p.42's £10bn and p.83's guaranteed-lending figures are correctly left unstaged.
  - So are p.34's £1,405m, £165m and £450m, and the £70m, £485m and 2,000 staff.
- **Quotes:** every text quote is one or two whole OGL sentences. Table quotes join the table's cells; p.94's quote keeps "Exchequer impact*".
- **NOTES.md tallies:** all recomputed and matching:
  - 597 rows;
  - 416 whole-line rows on 68 keys, 159 component rows on 8 lines, 22 proposed-key rows on 3 keys;
  - 8 behavioural parameters, 7 PSND/PSNFL rows (3 PSND, 2 PSNFL, 2 fair value), 2 eligible counts, 2 tax gap, 1 tax base, 1 financial transaction;
  - 25 components;
  - behavioural classes 56 / 18 / 22, with 13 distinct "none" sentences;
  - 12 `statistic` and 5 `parameter` labels;
  - `measure_scope` pages match.
  - No stale files in the family directory, apart from `stage.py`'s docstring (finding 1 resolves it).
- **Completeness:** I searched every page's text for £, %, "million", "billion" and "estimated". Every unstaged number is in the appendix, including p.91's RPI 4.1% and 7.1% and p.72's "lead option" £50m. Nothing is missing.

## Sample (66 rows: all 21 text rows, plus 45 table rows covering every row type and proposed key)

Every row below matches its page: the printed `value_raw`, its scale and sign, period/fy/time_basis, the quote and the conditions.

**Text rows**

| rows | locator | content | notes |
|---|---|---|---|
| 18, 19 | p.15 cost base | 166,000 and "around 750" | |
| 20 | p.15 costing | 89% | fy 2029-30 |
| 99 | p.28 costing | 25% | fy 2027-28 |
| 124, 125 | p.33 costing | −386m PSND, −375m PSNFL | |
| 132, 133 | p.34 costing | −775m, −68m | |
| 176, 177, 178 | p.41 costing | −32m, +86m, +54m | |
| 233, 234 | p.50 tax base | 6.4%, £59.2bn | value OK; **re-key per finding 1** |
| 283 | p.58 costing | +£130m | fy 2029-30 |
| 338, 339 | p.67 costing | −0.95, 25% | |
| 436–439 | p.84 costing | £20m | fys 2028-29 to 2031-32 |
| 584 | p.108 tax base | 4.9m properties | |

**Table rows** (value shown is the sampled year's cell)

| row | page | value | row type and notes |
|---|---|---|---|
| 0 | p.12 | −755m | |
| 7 | p.13 | −780m | |
| 17 | p.14 | −245m | |
| 24 | p.15 | −70m | |
| 105 | p.28 | −140m | |
| 107 | p.29 | −260m | |
| 115 | p.30 | −65m | |
| 122 | p.32 | −145m | EMI2; locator p.32 |
| 126 | p.33 | +0m | component |
| 139 | p.34 | +25m | component |
| 184 | p.41 | +30m | proposed key |
| 186 | p.42 | +200m | |
| 194 | p.43 | +140m | component |
| 199 | p.44 | −85m | component |
| 208 | p.45 | +1,815m | component |
| 212 | p.46 | +165m | component |
| 219 | p.47 | +65m | component |
| 226 | p.48 | +320m | component |
| 227 | p.49 | +65m | component |
| 237 | p.50 | +310m | component |
| 243 | p.51 | −40m | component |
| 248 | p.52 | −30m | component |
| 255 | p.53 | +320m | |
| 261 | p.54 | +145m | component |
| 266 | p.55 | −5m | component |
| 276 | p.56 | +175m | component |
| 281 | p.57 | −5m | component |
| 287 | p.58 | −35m | component |
| 341 | p.67 | +135m | component |
| 348 | p.68 | +20m | component |
| 360 | p.70 | +1,040m | |
| 426 | p.82 | +35m | label "[AME savings only]" |
| 430 | p.83 | −105m | |
| 445 | p.84 | −30m | |
| 446 | p.85 | −175m | component |
| 452 | p.86 | +5m | component |
| 480 | p.90 | −75m | |
| 491 | p.92 | −3m | component |
| 496 | p.93 | −1m | component |
| 501 | p.94 | +70m | footnote "*Note: This costing also includes delivery costs." |
| 513 | p.96 | −55m | label printed "Exchequ / er impact" |
| 531 | p.99 | −10m | |
| 543 | p.101 | +140m | |
| 589 | p.108 | +230m | fiscal-neutrality footnote |
| 591 | p.109 | +0m | proposed key |