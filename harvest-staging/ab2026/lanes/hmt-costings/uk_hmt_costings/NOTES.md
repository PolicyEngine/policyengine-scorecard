# uk_hmt_costings: HM Treasury, Budget 2026: Policy Costings (PU 3699)

**Working files.** `stage.py`, the file meant wherever these notes say `stage.py`, lives on branch `uk/ab2026-harvest-staging` at `harvest-staging/ab2026/lanes/hmt-costings/uk_hmt_costings/stage.py`; this branch carries only NOTES.md, `manifest.jsonl` and `claims_staged.jsonl.gz`. The repository carries no primary bytes: fetch the costings PDF from its `manifest.jsonl` URL and check its sha256.

This family dates from 2026-10-29 and follows README rules 1 to 10, including rule 8 ("stage estimates, not design"), rule 9 ("a component of one measure keeps that measure's key") and rule 10 (below, under Conventions). `stage.py` (on the staging branch; see 'Working files') holds the rows as data and rewrites `claims_staged.jsonl.gz` byte for byte.

Source slug `hm_treasury` and source_model `hmt_costing_obr_certified`, as in the AB2025 family. The exception is the two tax gap rows, which use `administrative_data`.

- **Rows:** 597.
  - 576 Exchequer impact cells: 96 costing notes, each across six fiscal years from 2026-27 to 2031-32.
  - 21 rows of estimates printed in the notes' text:
    - behavioural parameters (8);
    - PSND and PSNFL impacts (7);
    - eligible counts (2);
    - the tax gap behind one tax base (2);
    - one tax base;
    - one financial-transaction impact.
- **Primaries:** 1 PDF.
- **Measure keys:** 76 registry keys on 573 rows.
  - 416 rows cost a whole Table 6.1 line: `conditions.row_type: measure`, 68 keys.
  - 157 rows cost a printed part of one line: `row_type: measure_component`, 8 lines' keys.
  - 22 rows carry `measure_key: null` and one of 3 proposed keys, for measures with no Table 6.1 line or none this family can identify. 6 of them (p.108's receipts) are `measure_component`, so 163 rows in all are components.
  - 2 rows (p.50's UK tax gap) are context: `measure_key: null` and no proposed key.

## Access recipe

- **Fetch:** `curl -sSL` with a browser User-Agent to https://assets.publishing.service.gov.uk/media/6ae1883fe4367e5c8b0467df/AB26_Policy_Costing.pdf on 2026-10-29 at 16:14 UTC.
  - HTTP 200, `application/pdf`, 745,488 bytes, sha256 `f716efada8a4d0726ce12b0f97d3f0dac671c31b2d005ecf300a48ff309638bf`.
  - The site showed no bot mitigation, so the fetch needed no fallback.
  - The bytes equal the harvest's local copy downloaded on 28 October. The primary has not changed since Budget day, so README rule 7 does not apply.
- **Reading:** `pdftotext -layout`.
  - 122 pages: the introduction on p.10, costing notes on pp.12-109 and Annex A on pp.110-121.
  - Two notes run onto a second page: EMI2 (pp.31-32, table on p.32) and Writing-down Allowances (pp.70-71, table on p.70).
  - This file cites each note by its first page. A row's locator cites the page that prints the figure.
- **Where the data in `stage.py` comes from:** a scratch parser, not vendored, split the text into notes at each "Measure description" heading and read each note's sections.
  - Every note prints exactly one "Exchequer impact (£m)" table: one row of six signed values for 2026-27 to 2031-32.
  - I reviewed the parse against the page text. All 96 titles match the document's contents list.
  - Prose joins a line-end hyphen without a space, except a suspended one: p.82's "18- to 24-year-old".
- **Re-check:**
  - `python3 stage.py` rewrites the gzip.
  - `python3 stage.py --verify <path to the PDF>` writes nothing. It checks that the gzip on disk equals a fresh build and that the PDF has the pinned sha256. For every row it then checks the page its locator cites:
    - **table rows:** the heading, the six years, the six values in order and the row's value in its year's column. The row label must equal the page's label exactly, and any footnote must appear.
    - **text rows:** the quote, verbatim, with `value_raw` inside it. `value` must equal `value_raw`'s number at the scale and sign the `normalization` names.
    - **every keyed row:** the measure's title, on the note's first page.
  - All 597 rows pass. An in-memory mutation test confirms the check catches each of: a wrong table value; swapped columns; a wrong or shortened label (p.82 without "[AME savings only]"); a text figure off by sign, scale or value; and a wrong title.
- **Table quotes.** A table row's `quote` joins the table's cells in reading order: heading | years | label and six values | footnote. p.96 prints its label broken across two lines as "Exchequ / er impact"; the quote and `table_row` write it "Exchequer impact".

## What the family stages

### Exchequer impact tables (576 rows)

- **One row per note and fiscal year:**
  - `metric: revenue_change` and `unit_concept: gbp`.
  - `value` is `value_raw` (£m, with the sign and trailing "m" as printed) × 1e6.
- **Every table is `scoring_method: final`.**
  - No AB2026 note prints separate static and post-behavioural tables; in AB2025, 8 notes did.
  - No note prints a behavioural adjustment in pounds; AB2025's thresholds note printed £180m.
  - So the family has no static, post-behavioural or behavioural-effect legs to stage. Several notes mention a static costing, and p.108 a "pre-behavioural costing", but none prints a figure for it.
- **`conditions.behavioural_adjustment`** classifies the words of each note's costing section. The pages listed are each note's first page.
  - **"included (see note)" on 56 notes:** pp.12, 13, 14, 16, 18, 19, 23, 24, 25, 26, 27, 29, 30, 31, 36, 38, 39, 40, 43, 44, 45, 46, 47, 48, 49, 51, 52, 53, 60, 62, 65, 66, 67, 68, 70, 72, 73, 74, 75, 77, 78, 79, 80, 81, 82, 85, 86, 87, 90, 95, 100, 102, 103, 104, 107 and 108.
    - p.90 adds its sentence: the Infected Blood costing keeps the scheme's cost model, whose "behavioural assumptions" the changes "do not materially alter".
  - **"none: '<the costing section's sentence>'" on 18 notes:** pp.17, 35, 37, 42, 50, 54, 55, 56, 58, 59, 61, 63, 64, 91, 94, 101, 106 and 109.
  - **"not stated (the note's costing section does not use the word 'behaviour' or 'behavioural')" on 22 notes:** pp.15, 20, 21, 22, 28, 33, 34, 41, 57, 69, 76, 83, 84, 88, 89, 92, 93, 96, 97, 98, 99 and 105.
    - This class is lexical and reads the costing section only; AB2025 used only the first two classes.
    - Six of these notes name behaviour in their "Areas of uncertainty" instead:
      - pp.20, 21, 22, 69 and 89: "the impact of behavioural responses";
      - p.93: "the behavioural response to the rebate scheme".
    - Others describe a response in other words:
      - p.15 assumes 89% take-up;
      - p.28 puts 25% of income into reserves;
      - p.76 "includes an assumed timing effect";
      - p.84 assumes the zone facilitates borrowing;
      - p.88 says self-assessment "may affect how taxpayers interact with the tax system";
      - p.99 adjusts "for expected utilisation of the cap".
- **`conditions.static_impact`:** three notes say the measure has no static impact, so the whole costing is behavioural.
  - p.19 (Cash ISAs) and p.43 (E-invoicing): "The costing has no static impact on taxpayer liabilities."
  - p.44 (Employment expenses): "The measure has no static impact on taxpayer liabilities."
- **`conditions.table_row`:** "Exchequer impact" on 95 notes; "Exchequer impact [AME savings only]" on p.82.
- **`conditions.table_footnote`:**
  - p.94: "*Note: This costing also includes delivery costs."
  - p.108: "Note: this is offset by increased DEL spending so is fiscally neutral."
- **`conditions.fiscally_neutral`:** pp.108 and 109, each with the note's own sentence.
- **`note`:** the note's base section, then its costing section, then "Areas of uncertainty", verbatim and joined by " || ". Component and off-table notes have a mapping paragraph in front (see "Measure keys").

### Estimates from the notes' text (21 rows)

| page | figure, verbatim | staged as | period | key |
|---|---|---|---|---|
| 15 | "an estimated 166,000 fathers and partners and around 750 self-employed adopters" | `eligible_count`, persons (2 rows) | 2026, point in time | `ab2026__parental_allowance_fathers_partners_adopters` |
| 15 | "an 89% take-up rate" | `behavioural_parameter`, percent | 2029-30 | same |
| 28 | "25% of the additional income above the baseline is placed into MSAs’ reserves" | `behavioural_parameter`, percent | 2027-28 | `ab2026__business_rates_retention_mayoral_authorities` |
| 33 | "public sector net debt (PSND) (approx. £386m) and public sector net financial liabilities (PSNFL) (approx. £375m)" | `psnd_impact` -386m, `psnfl_impact` -375m | to 2031-32, cumulative | line 29, component p.33 |
| 34 | "a cost of approximately £775m" (PSND); "add an additional cost of £68m" (PSNFL fair value) | `psnd_impact` -775m, `psnfl_fair_value_impact` -68m | to 2031-32, cumulative | line 29, component p.34 |
| 41 | "a cost of approximately £32m" (PSND); "the value of the portfolio increases by approximately £86m (total PSNFL benefit of £54m)" | `psnd_impact` -32m, `psnfl_fair_value_impact` +86m, `psnfl_impact` +54m | to 2031-32, cumulative | proposed, p.41 |
| 50 | "6.4% of total theoretical tax liabilities, or £59.2 billion in absolute terms" | `tax_gap`, percent and gbp | 2024-25, outturn | context (`measure_key: null`) |
| 58 | "an impact of +£130m estimated in 2029-30 in cash terms" | `financial_transaction_cash_impact` | 2029-30 | line 47, component p.58 |
| 67 | "An elasticity of -0.95 is used, with 25% of the reduction in stakes then assumed to substitute to Remote Gaming Duty" | `behavioural_parameter`, elasticity and percent | 2027-28 | line 56, component p.67 |
| 84 | "£20 million of additional capital borrowing annually from 2028-29 to 2031-32" | `behavioural_parameter`, gbp, one row per year | 2028-29 to 2031-32 | `ab2026__leeds_city_fund` |
| 108 | "approximately 4.9 million eligible properties are in scope" | `tax_base`, properties | 2026, point in time | proposed, p.108 |

- **Labels.** Each text row names its quantity in `conditions.statistic`, or `conditions.parameter` for a behavioural parameter. Rule 9 reserves `conditions.component` for the part of the measure.
- **Per-year rows.** p.84's sentence gives one figure for each of four named years, so the family stages one row per year, each quoting the whole sentence. The family sums and splits nothing.
- **Year of a parameter.** The note gives no year for p.15's take-up, p.28's reserves share or p.67's two parameters. As in the AB2025 family, `fy` is the measure's first year, and the row's `note` says so.
- **Present-tense counts** (p.15 "There are an estimated", p.108 "The current estimate") print no year. They carry `period: 2026` and `time_basis: point_in_time`, with `basis: outturn`.
- **Metric choices that could go either way:**
  - p.15's population is the people a new benefit would cover, so it takes the registered `eligible_count`.
  - p.108's 4.9 million is the base the fee falls on, so it takes `tax_base`, as AB2025's 165,000 HVCTS properties did.
  - p.84's £20 million is the council's estimated response to the measure ("Additional business rates income is assumed to facilitate borrowing", and "none is assumed without the zone"). So it is a `behavioural_parameter` in pounds, as the AB2025 uk_obr_tables family staged costing assumptions (its £1,849 row), not a financing remit.
- **PSND and PSNFL figures.**
  - They sum over "the period to 2031-32", so they carry `value_kind: cumulative`, `period: 2032`, `conditions.horizon` and no `fy`.
  - The document prints them unsigned, with words. The family gives all seven one convention, matching the Exchequer rows: positive = lower PSND or PSNFL (an improvement); negative = higher (a cost).
  - `normalization` and `sign_convention` quote the words each sign comes from: "net cost", "a cost of" and "add an additional cost of" are negative; "benefit" and "the value of the portfolio increases by" are positive.
  - The £68m (p.34) and the £86m (p.41) are fair-value movements: increments to PSNFL beyond PSND, not PSNFL totals. They take their own proposal, `psnfl_fair_value_impact`.
  - p.41's figures agree: -32 + 86 = +54.
  - p.34 prints no PSNFL total, so the family stages none.
- **The tax gap.**
  - p.50 prints HMRC's tax gap for 2024 to 2025 in its tax base section, as the base's starting point: "The tax base for this costing is the total tax gap less the additional tax revenues accounted for by previously announced Closing the Tax Gap (CTG) initiatives."
  - Rule 8 counts a tax base as an estimate, but the total tax gap is a context figure, not a part of the measure, so the two rows carry `measure_key: null` (AB2025 rule 3).
  - They are an official HMRC statistic repeated by HM Treasury, so they carry `attribution: restated`, `benchmark_class: administrative_fact`, `source_model: administrative_data` and `basis: outturn`, with the uk_rf_ab2025 proposal spelling `tax_gap`.
  - The note does not cite the HMRC publication.

## Conventions (load-bearing)

- **Sign.** The document prints no legend.
  - `conditions.sign_convention` on every Exchequer row reads "positive = yield to the Exchequer (reduces borrowing); negative = cost to the Exchequer". The full text also gives the evidence:
    - p.38 says its figures "represent net income from developer fees" and prints +50m to +95m from 2027-28, after -15m in 2026-27.
    - The Bank Surcharge rise prints +, and the VAT cut on domestic electricity prints -.
    - Table 6.1 prints the same values with the same signs.
  - Values are NOT re-signed.
  - Text rows carry their own `sign_convention`: as printed for p.58's "+£130m", and for the PSND and PSNFL rows as described above.
- **Rule 10 (borrowing metric).** pp.34, 35 and 41 say their tables' figures "impact public sector net borrowing (PSNB)". They are single measures' Exchequer impacts, which Table 6.1 frames the same way (red book para 6.1), and README rule 10 keeps single measures on `revenue_change` unless the producer states the Budget's effect on borrowing. So rows 134–145 and 179–184 keep `revenue_change`; p.35 equals line 30. No row in this family takes `decisions_effect_on_borrowing`.
- **period** is the FY end year (2026-27 → 2027), with `conditions.fy` holding the label.
- **geography** is "UK" on every row, because these are Exchequer impacts. `conditions.measure_scope` names the territory where the note or its title says the measure applies:
  - England: pp.20, 21, 22, 36, 69, 96, 102 and 108.
  - Great Britain: pp.15 and 59.
  - England and Northern Ireland: p.99.
  - pp.91 and 94 name England only for their cost bases ("English borrowers", "English undergraduate student loan outlay"), so they carry no `measure_scope`.
- **baseline_policy** is null throughout: current law at scoring, including the pre-announced indexation in Annex A. There is no `proposed_baseline`.
- **impact_channel** comes from the Table 6.1 line's Tax or Spend head in the registry:
  - `tax_measure` or `spending_measure`;
  - `not_on_table_6_1` for pp.108-109;
  - `not_identified_on_table_6_1` for p.41.
- **national_accounts_basis**: "All costings are presented on a National Accounts basis (p.10)" on every Exchequer row.
- **parse_confidence** is "high" on every row. The document prints every value as text, and `--verify` finds each on its page.

## Measure keys

The document orders its costing notes by Table 6.1 line. Mapping each note to its line gives a non-decreasing sequence from line 2 to line 98, with the two Table 6.1 exclusions (pp.108-109) at the end. That ordering, together with titles and Table 6.1's footnotes, settles each note's line.

- **Whole lines (68 keys, 416 rows, `row_type: measure`).** These cover every note that is the only costing for its Table 6.1 line and costs all of it.
  - For 64 notes the title equals the line's title exactly.
  - Four differ only by Table 6.1's parenthetical or the year: p.35 (line 30), p.38 (line 37), p.42 (line 44) and p.77 (line 66).
- **Components (8 lines, 25 notes, 157 rows, `row_type: measure_component`).** Under README rule 9, a note that costs a printed part of one Table 6.1 line carries that line's key.
  - `conditions.component` names the part: the note's title, or for p.82 its fiscal head.
  - `conditions.table_61_line` gives the line.
  - The harvest never sums a component with the line's total.

| line | key | component notes (first page) |
|---|---|---|
| 29 | `ab2026__british_business_bank_backing_innovation` | p.33 British Business Bank: bring forward activity; p.34 British Business Bank: increase total financial capacity |
| 45 | `ab2026__hmrc_tax_gap_package` | p.43 E-invoicing; p.44 Employment expenses; p.45 More Timely Payment; p.46 VAT and PAYE direct debit; p.47 Real Estate exchange of information; p.48 Debt Management, recovery from bank accounts; p.49 Debt Management, debt collection agencies; p.50 Tax Compliance, 670 officers; p.51 MTD penalty easement; p.52 Image Rights delay |
| 47 | `ab2026__dwp_fraud_and_error_prevention` | p.54 Abroad Fraud; p.55 Pension Credit capital redeclaration; p.56 UC specialist fraud and error checks; p.57 UC capital verification reversed; p.58 UC New Claim Advances |
| 56 | `ab2026__machine_games_duty_higher_stake_25pc` | p.67 rate rise for higher stake machines; p.68 liability moved to the supplier |
| 72 | `ab2026__youth_guarantee_and_apprenticeships_spring_2026` | p.82: AME savings only ("Exchequer impact [AME savings only]"), for the Youth Guarantee expansion to 22- to 24-year-olds |
| 77 | `ab2026__uk_india_ceta_and_double_contributions_convention` | p.85 CETA tariff changes; p.86 Double Contributions Convention |
| 84 | `ab2026__waste_crime_landfill_tax_clearances` | p.92 six priority site clearances; p.93 local authority pilot |
| 85 | `ab2026__further_priorities_nhs_and_vawg` | p.94 Erasmus+ (by position; see below) |

- **Proposed keys (3 keys, 22 rows; `row_type: measure`, except p.108's six receipts rows, which are `measure_component`).** Rule 9 keeps proposed keys "for scopes that cross Table 6.1 lines, or have none". The registry adds them before ingest; the table gives each key's scope as the producer's own words.

| proposed key | rows | page | scope |
|---|--:|---|---|
| `ab2026__british_business_bank_defence_commitments_accelerated` | 9 | 41 | No identifiable Table 6.1 line (see below). "British Business Bank: Accelerate £450m of commitments to support defence-related and dual-use businesses" By Table 6.1's footnote 2 and its £10m bar, this costing is very probably inside a Table 6.1 line, most plausibly line 41 (lines 29 and 44 are fully accounted for by their own notes); tranche 2 must never add it to Table 6.1 lines or totals. |
| `ab2026__private_landlord_register_fee_65` | 7 | 108 | Not on Table 6.1 (footnote 2). The six Exchequer rows are the fee's receipts, a component (`component: "Receipts (fee income; offset by increased DEL spending, fiscally neutral)"`): p.108's note says "this is offset by increased DEL spending so is fiscally neutral", and the OBR stages the measure's total as 0 (review A, C-1). The seventh row is the 4.9 million tax base. "Renters' Rights: Roll out a £65 fee for the 'Register your rental property' service for private landlords and private properties in England from 15 December 2026" |
| `ab2026__pwlb_debt_relief_councils_severe_distress` | 6 | 109 | Not on Table 6.1 (footnote 2). "Public Works Loan Board (PWLB) Debt Relief for Councils in Severe Financial Distress" |

How I settled each line:

- **Lines 45 and 47.** Table 6.1's footnote 4 on both lines reads "Full costings for the measures in this package are set out in the Budget 2026 Policy Costings document."
  - The ten notes on pp.43-52 sit between line 44's note (p.42) and line 46's (p.53).
  - The five notes on pp.54-58 sit between line 46's and line 48's (p.59).
- **Lines 29, 56, 77 and 84.** The line's title names both notes' measures.
- **Line 72 (p.82).** The note's title equals the line's, but its figure is one fiscal head of the line:
  - its table prints the AME savings only;
  - its text costs the Youth Guarantee's expansion to 22- to 24-year-olds and never mentions the apprenticeship support the line also names.

  Table 6.1 prints -290 and -375 where the note prints +25 and +35 (2027-28 and 2028-29).
- **Line 85 (p.94, Erasmus+).** No Table 6.1 title names Erasmus+.
  - The note sits where line 85 falls: "Further Priorities: Fund key priorities, including pressures facing the NHS and delivery of the Violence against Women and Girls Strategy".
  - Line 85's 2029-30 to 2031-32 figures (-5, 0, -15) equal the note's.
  - Table 6.1's footnote 2 leaves out only two measures, neither of them Erasmus+, and the note's figures exceed the footnote's £10m bar in four of the six years.
  - `conditions.document_position` records the position.
- **p.41.** Position narrows the note to lines 40-43, the national-security block.
  - Table 6.1 prints lines 40-43 under its Spend head and prints no finer fiscal head, so nothing printed singles out one line. (The workbook's hidden column D, "Fiscal Head check (hide)", is not printed, and this family no longer reasons from it; review A, T-3.)
  - But line 41's title, "Defence Investment Plan: Reallocate capital spending to fully fund the Defence Investment Plan", does not name the British Business Bank, and no figure ties the two.
  - So the row carries a proposed key and `document_position`, not line 41's key. By Table 6.1's footnote 2 and its £10m bar, this costing is very probably inside a Table 6.1 line, most plausibly line 41 (lines 29 and 44 are fully accounted for by their own notes); tranche 2 must never add it to Table 6.1 lines or totals.
- **pp.108-109.** Table 6.1's footnote 2 reads "Measures with no net increase to borrowing are not included, these are debt relief for councils in severe financial distress through the Public Works Loan Board and a landlord registration fee for the Private Rented Sector."

No `row_type: measure` row carries a registry key whose title covers more or less than the row's figure.

## Cross-check against Table 6.1 (uk_hmt_tables)

- **All 68 whole-line keys** equal Table 6.1 in all six years.
- **Component lines** (Table 6.1 against the components' sum, 2026-27 to 2031-32; computed for this check only, never staged; reported, not fixed):
  - **Line 29 (pp.33+34):** equal.
  - **Line 56 (pp.67+68):** the components sum to 140 in 2031-32 against Table 6.1's 145. The other years are equal.
  - **Line 77 (pp.85+86):** the components sum to -170 in 2026-27 against Table 6.1's -175. The other years are equal.
  - **Line 84 (pp.92+93):** the components sum to -4, -3, -3 in 2027-28 to 2029-30 against Table 6.1's -5, -5, -5.
  - These three gaps are each £5m or less, and every Table 6.1 cell is a multiple of £5m. That fits Table 6.1 rounding each line from unrounded components, but neither document says so.
  - **Line 72 (p.82):** the AME component prints +0, +25, +35, +0, +0, +0 against Table 6.1's 0, -290, -375, 0, 0, 0.
  - **Line 45 (pp.43-52):** the ten components sum to 110, 290, 240, 2,140, 2,635, 3,360 against Table 6.1's 10, 100, 115, 1,980, 2,485, 3,160. Table 6.1 is lower by 100, 190, 125, 160, 150 and 200.
  - **Line 47 (pp.54-58):** the five components sum to -10, 10, 125, 65, 145, 235 against Table 6.1's 195, -125, 60, 75, 155, 240. The differences are +205, -135, -65, +10, +10 and +5.
  - **Line 85 (p.94):** equal from 2029-30 to 2031-32. Table 6.1 prints larger costs from 2026-27 to 2028-29: -355, -175, -140 against the note's -15, +70, +45.
- **Table 6.2:** p.58's "+£130m estimated in 2029-30 in cash terms" equals Table 6.2 line 9 (DWP Fraud and Error) for 2029-30.
- **Lines without a costing note:** 22 Table 6.1 lines have none: 1, 4, 9, 20, 22, 23, 24, 25, 31, 32, 34, 35, 40, 41, 42, 43, 63, 64, 67, 73, 74 and 81.
  - The introduction limits the document to "tax and annually managed expenditure (AME) policy decisions".
  - Table 6.1 prints all 22 under its Spend head. It prints no finer fiscal head, so whether each is departmental spending (outside the document's scope) is not printed; no note costs them.

## Things in the primary that look wrong or contradictory (reported, not fixed)

- **The £10m threshold.** The introduction says "Measures that were certified by the OBR as below the negligible threshold of £10 million per annum in every year of the forecast period are not considered in this document." Five notes print costings below £10m in every year:
  - p.59 (+0m, then +5m a year);
  - p.92 (-2m, -2m, -3m);
  - p.93 (-2m, -1m);
  - p.33 and p.109 (+0m in all six years; p.33's PSND and PSNFL figures are not zero).

  Table 6.1's footnote 2 sets the same bar for its lines: "AME and tax costings with an impact of less than +-£10 million in every year are not included". Yet two such lines appear:
  - line 48 (0, then +5 a year; Spend head);
  - line 84 (0, -5, -5, -5, 0, 0; Spend head).

  Lines 9 and 81 are also below £10m every year. The footnote's bar covers AME and tax costings only, and Table 6.1 prints no head finer than Tax or Spend to say whether these two are AME or departmental spending.
- **The lines 45 and 47 differences.** Table 6.1's footnote 4 points to this document for the packages' full costings, but the components do not sum to the lines (above), and no note explains the gap.
  - For line 45, the gap has the sign the HMRC spending the notes describe would give: £70 million on debt collection (p.49) and £485 million on compliance staff (p.50), "over the next five years". The document does not say that this spending is the difference.
  - For line 47, the gap changes sign: +205 in 2026-27, -135 in 2027-28.
- **Notes with no Table 6.1 title.** BBB defence (p.41) and Erasmus+ (p.94) have costing notes, but no Table 6.1 title names them.
- **Minor title and wording differences:**
  - p.77's title says "from 25 June to 1 September", while Table 6.1 says "from 25 June 2026 to 1 September 2026".
  - p.16's title says "Weekly Earning Limit", while its text says "Weekly Earnings Limit" (Table 6.1 follows the title).

## Not staged, and why

The family stages every Exchequer table and every printed estimate in the notes' text: tax bases, behavioural parameters, eligible counts, PSND, PSNFL and financial-transaction impacts. The appendix lists everything else page by page.

- **Design (README rule 8):** a measure's own rates, thresholds, payment amounts, dates and durations, and counts of products, sites or bodies. They stay in `reform_hint` and `note`.
- **Contingent liabilities (rule 8):**
  - p.42's "£10 billion in new guarantees are issued each year between 2027-28 and 2030-31" (UK Export Finance);
  - p.83's guaranteed lending "by £1.0 billion in 2026-27, £1.5 billion in 2027-28 and £2.0 billion in each of 2028-29 and 2029-30" and its £6.5 billion total (Growth Guarantee Scheme).

  Both are the volumes on which the notes cost fees and losses. Each note's `note` keeps the sentence.
- **Spending allocations to programmes and financing remits (rule 8):**
  - p.34's split of the British Business Bank recapitalisation (£1,405 million for commercial equity, £165 million of CDFI lending and £450 million of venture debt, within c. £2 billion), kept in `note`;
  - p.33's £1 billion reprofiled; p.35's £2bn Energy Wealth Fund; p.41's £450 million; p.42's £50 billion of capacity;
  - p.109's £700m of PWLB debt repaid;
  - HMRC's £70 million (p.49) and £485 million (p.50) and the staff numbers on pp.50 and 56.
- **Numbers printed only in titles:** AB2025 kept these in `reform_hint`, and Table 6.1 carries the same titles.
- **Baseline parameters:** p.91's RPI outturn and counterfactual maximum rate.
- **p.58's "-£35m in 2029-30 in expenditure terms":** the same figure as that note's Exchequer table cell for 2029-30, so staging it would count it twice.
- **p.94's "£0.6bn was allocated for the cost of Erasmus+ association for 2027-28":** an allocation made at Spring Forecast 2026, an earlier event, with a different scope from this note's student-loan and delivery costs.
- **Annex A (pp.110-121):** indexation assumptions in the forecast baseline, not measure costings. AB2025 did not stage them either.
- **The introduction (p.10):** the £10 million negligible threshold, and the list of five measures whose methodology "the government will publish further information on ... by the end of the year":
  - More Timely Payment, Distributions, Foreign Sovereign Investments, Founders' Relief and BADR.
  - Those publications will be new primaries when they appear.
- **References, not quantities:** scheme, form and statute numbers such as EMI2, Plan 2 and Plan 3, form P87, Class 1 and 1A, Group 7 of Schedule 9 to the VAT Act 1994, FRS 102 and the Five-Year Strategic Plan.
- **Uncertainty ratings:** the document prints none. Each row's `note` keeps the note's "Areas of uncertainty" text. p.101 says "there is no uncertainty over the figures involved". The OBR's ratings belong to uk_obr_tables.
- **Charts:** the document has none.
- **Unreached pages:** none.

### Appendix: every unstaged number, by page

D marks design, C a contingent liability, S a spending allocation, input or measure size, T a number printed only in a title, B a baseline parameter.

- **p.10:** £10 million negligible threshold; BADR's £500,000 in the further-publications list (T).
- **p.12:** VAT 5% → 0% (D).
- **p.13:** 5p (5 pence) per litre cut extended by 6 months; 57.95 ppl main rate; 5ppl rise (D).
- **p.14:** 55p for the first 10,000 business miles; 35p above 10,000 miles (D).
- **p.15:**
  - two weeks paid between £27 and the statutory rate of £194.32;
  - 2 weeks at the lower of £194.32 or 90% of average weekly earnings;
  - up to 39 weeks for adopters (D).
- **p.16:** Weekly Earnings Limit at 16 times the National Living Wage; taper set at 100% (D).
- **p.17:** £2,500 surplus earnings threshold for one year (D).
- **p.18:** two packages of suspensions (D); 135 and 101 food products (T).
- **p.19:** £20,000 and £12,000 cash ISA limits; individuals under 65 (D).
- **p.20:** relief up 20ppt from 15% to 35%; rateable value of £1 million (D).
- **p.21:** £12,000 → £18,000 for 100% relief; £15,000 → £21,000 for tapered relief (D).
- **p.22:** two-year real-terms bills freeze; one-year Supporting Small Business extension; 1p Transitional Relief Supplement for two years (D).
- **p.23:** £1,000 → £3,000 trading allowance (D).
- **p.24:** 72 products; 269 extended and 23 expiring suspensions; all 92; 361 products (D/T).
- **p.26:** 3.7ppl cut from 10.18 to 6.48 ppl, extended a further 6 months; the 5ppl cut (D).
- **p.27:** ABV bands 1.3%, 3.4%, 3.5% and 8.4%; RPI plus an additional 10% (D).
- **p.28:** 20% share of growth (D).
- **p.29:** 10% CGT rate; £10 million lifetime limit; at least 25% holding; two of three tests (D).
- **p.30:** no claim in the past 3 years (D).
- **p.31:**
  - option limit £60,000 → £120,000;
  - £250,000 EMI limit;
  - exercise and exception periods 10 → 15 years;
  - exercise window 90 → 180 days (D).
- **p.33:** £1 billion of commitments reprofiled into 2026-27 (S).
- **p.34:** c. £2 billion of financial capacity; £1,405 million, £165 million and £450 million allocations (S).
- **p.35:** £2bn for the Energy Wealth Fund (S); commitments over the next five years (D).
- **p.38:** around 70,000 first-time buyers (T); 20% equity loans; deposits as low as 2.5% (D).
- **p.39:** 25% bonus; £450,000 home value (D).
- **p.40:** withdrawal charge 25% → 20%; £450,000 price cap (D).
- **p.41:** £450 million of commitments accelerated (S).
- **p.42:** £50 billion of added capacity (S); £10 billion of new guarantees each year, 2027-28 to 2030-31 (C).
- **p.43:** two revenue channels (D).
- **p.44:** £2,500 Self Assessment expenses threshold (D).
- **p.45:** forecast liability above £1,000; less than 80% collected at source (D).
- **p.48:** debts up to £5,000 (individuals) and £10,000 (companies) (D).
- **p.49:** £70 million over the next five years (S); aged debt over 12 months old (D).
- **p.50:** £485 million over the next five years; 670 FTE (also in the title); 5,500 previously announced staff; 6,170 FTE total (S).
- **p.51:** 12 month penalty easement (D).
- **p.52:** delay by one year (D).
- **p.53:** £90,000 platform threshold (D).
- **p.56:** 2,000 specialist fraud staff (S).
- **p.58:** -£35m in 2029-30 in expenditure terms (the table cell).
- **p.64:** members under age 75; benefits paid more than two years after; 45% flat rate (D).
- **p.66:** surcharge 3% → 6%; combined rate 28% → 31%; 15 months (D).
- **p.67:** rate 20% → 25%; stake above £1; prize above £100 (D).
- **p.70:** writing-down allowance 14% → 12%; first-year allowance 40% → 50% (D).
- **p.72:** £50 million turnover threshold (D).
- **p.73:** £500,000 lifetime limit; 24% and 18% CGT rates (D).
- **p.74 and p.75:** 2 percentage points (D).
- **p.76:** VED of £1 for 12 months; vehicles over 3,500 kg (D).
- **p.77:** VAT 20% → 5% (D).
- **p.79:** levy 45% → 55% (D).
- **p.82:**
  - 18- to 24-year-olds on Universal Credit for 18 months;
  - a six-month job paid at 100% of costs for 25 hours a week;
  - eligibility widened from 18- to 21-year-olds; cost base of 22- to 24-year-olds (D).
- **p.83:**
  - £6.5 billion of lending; £1.0 billion, £1.5 billion and £2.0 billion a year (C);
  - maximum loan term six → ten years;
  - turnover £45 million → £54 million (D).
- **p.84:** 100% retention of business rates growth for 25 years (D).
- **p.86:** detached-worker period 52 weeks → 60 months; two countries; contributions in only one country at a time (D).
- **p.87:** 50% out-of-quota tariff (D).
- **p.89:** 100% relief for ten years (D).
- **p.91:**
  - 6% interest cap; Plan 2 borrowers starting between academic years 2012/13 and 2022/23 (D);
  - RPI outturn of 4.1% for the 12 months to March 2026, and a 7.1% maximum rate without the measure (B).
- **p.92:** six priority sites (T).
- **p.93:** three-year pilot (T).
- **p.94:** £0.6bn allocated at Spring Forecast 2026 (see above).
- **p.95:** rates 1 percentage point above 2029-30; maximum of 40% (D).
- **p.97:** VAT 20% → 0% (D).
- **p.99:** credit cap 5.3% → 8.3% (D).
- **p.100:** providers with 300 or more students (D).
- **p.102:** properties valued at £2 million and above (D).
- **p.104:** £135 relief; £39 private consignments (D).
- **p.106:** spread over five years (D).
- **p.108:** £65 annual fee (D).
- **p.109:**
  - £700m of PWLB debt repaid, £500m for Woking and £200m for Thurrock (S);
  - two local authorities; a transfer between two central government bodies (D).

## Proposals used

- `proposed_metric`:
  - Reused from earlier families: `behavioural_parameter` (8 rows), `tax_gap` (2, the uk_rf_ab2025 spelling), `tax_base` (1) and `financial_transaction_cash_impact` (1, the uk_hmt_tables spelling).
  - New:
    - `psnd_impact` (3): a measure's cumulative impact on public sector net debt;
    - `psnfl_impact` (2): its impact on net financial liabilities;
    - `psnfl_fair_value_impact` (2): the fair-value part of the PSNFL impact beyond PSND.

    They parallel the existing `psnd_share_of_gdp` and `psnfl_share_of_gdp`.
- `proposed_unit`: `elasticity` (1).
- Registered values used beyond `revenue_change` and `gbp`:
  - `eligible_count` with `persons`;
  - `percent`;
  - `properties`, a unit registered since the AB2025 harvest proposed it.
- `proposed_baseline`: none.

## Attribution

- **`own` and `different_model`:** 595 rows. They are HMT and HMRC costings that the OBR certified ("All of these costings were submitted to the independent Office for Budget Responsibility (OBR) for their certification", p.10).
- **`restated` and `administrative_fact`:** the two tax gap rows.

## Distinct condition values

- `row_type`: measure | measure_component
- `component` (26 values): each component note's title, p.82's fiscal head, and p.108's receipts
- `basis`: forecast | outturn (the tax gap and the two present-tense counts)
- `scoring_method`: final (every Exchequer and parameter row)
- `table_row`: Exchequer impact | Exchequer impact [AME savings only]
- `impact_channel`: tax_measure | spending_measure | not_on_table_6_1 | not_identified_on_table_6_1
- `measure_scope`: England | Great Britain | England and Northern Ireland
- `behavioural_adjustment`:
  - included (see note), plus p.90's variant;
  - not stated (the note's costing section does not use the word 'behaviour' or 'behavioural');
  - 13 distinct "none: '<sentence>'".
- `horizon`: the period to 2031-32 (cumulative)
- Also used: `table_61_line`, `proposed_measure_key`, `document_position`, `fiscally_neutral`, `static_impact`, `table_footnote`, `statistic` (12 labels) and `parameter` (5 labels).

## Review fixes, 3 November 2026

The costings review (`harvest-staging/ab2026/reviews/verify-costings.md` on the staging branch) approved this family with fixes. They sit in an explicit block before `build()` in `stage.py`. No primary was re-opened (the session's network policy refused gov.uk); no printed value changed.

- **Finding 1:** p.50's UK tax gap rows (6.4% and £59.2bn) are context: `measure_key` and `reform_hint` null, no `row_type`, `component` or `table_61_line`. They stay `restated`, `administrative_fact`, `administrative_data`, fy 2024-25. Registry keys now cover 573 rows, and components 157.
- **Finding 2:** p.41 keeps its proposed key; the double-counting caveat is in its `mapping_note`, the p.41 bullet and the proposed-key table.
- **Finding 3:** the line 45 and 47 component mapping notes now say their notes do not sum to the line, with Table 6.1's differences.
- **Finding 4:** no action. The coordinator found that the lane's copies of `pipeline/ab2026_harvest_contract.py` and the harvest README match #231's head byte for byte, so only this family directory moved.
- **Finding 5:** no change (p.84's £20m and p.58's +£130m are accepted as staged).
- **Verification:** the contract checker reports 597 rows, 0 problems, and a re-run of `stage.py` reproduces the gzip byte for byte. COUNTS.json pins its sha256.

## Review fixes, 4 November 2026

Review A (PR #231, issue comment 6635870934) approved this family with fixes C-1 to C-7. They sit in an explicit block before `build()` in `stage.py`. No primary was re-opened; no printed value changed.

- **C-1:** p.108's six Exchequer rows (the landlord fee's receipts, 585–590) are `row_type: measure_component` with `component: "Receipts (fee income; offset by increased DEL spending, fiscally neutral)"`. Value, metric and proposed key stay. Components: 157 → 163.
- **C-2:** p.50's two context rows (233–234) no longer say they are "a tax-base input of the measure"; their note says they are context figures with null key and reform_hint (AB2025 rule 3).
- **C-3:** p.41's three text rows (176–178) carry finding 2's double-counting sentence.
- **C-4:** the family follows rules 1 to 10; the Conventions bullet on rule 10 says why pp.34, 35 and 41's PSNB wording keeps `revenue_change`.
- **C-5:** the key tally names the 2 context rows.
- **C-6:** p.84's precedent is the AB2025 uk_obr_tables family, in NOTES and the row note.
- **C-7:** `stage.py` is on the staging branch.
- **T-3 (uk_hmt_tables):** `uk_hmt_tables` no longer emits `conditions.fiscal_head`, read from the workbook's hidden check column. The sentences here that reasoned from it (the p.41 bullet, lines 9, 48, 81 and 84, and the lines without a costing note) now rely only on Table 6.1's printed Tax and Spend heads.
