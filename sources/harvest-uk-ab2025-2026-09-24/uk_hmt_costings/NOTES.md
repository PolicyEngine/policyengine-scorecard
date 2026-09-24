# uk_hmt_costings — HM Treasury "Budget 2025: Policy costings" (PU 3595)

Staged 2026-09-24. Source slug `hm_treasury`, source_model `hmt_costing_obr_certified`. 699 rows in
`claims_staged.jsonl.gz`; 1 primary in `manifest.jsonl`. Every value is verbatim from the PDF text layer;
nothing is derived. Staging scripts (scratchpad, not vendored): `parse_hmt_costings.py` (machine-parses every
"Exchequer impact (£m)" table on pp.12-115) and `stage_hmt_costings.py` (rows + the hand-transcribed tax-base and
behavioural-parameter claims).

## Access recipe

- `curl -sSL` with a browser User-Agent to
  https://assets.publishing.service.gov.uk/media/692872fd2a37784b16ecf676/Budget_2025-Policy_Costings.pdf
  (HTTP 200, 817,945 bytes, sha256 e4b87104f1a6cd1aeb7081e7815b604a7aa9ff1b760668e4a4c2e4719477fda4). No bot
  mitigation. gov.uk records the document as updated 27 Nov 2025 (two clarifying change notes); the hashed file
  is the current one.
- Text extracted with pypdf (`uv run --with pypdf`), 128 pages. Costing notes run pp.12-115; Annex A (indexation
  assumptions) p.116 onwards is not staged.
- Parser: each page whose text opens with a title followed by "Measure description" starts a measure;
  continuation pages (static/post-behavioural splits on pp.15-16, 24-25, 40-41, 47-48, 49-50, 51-52, 58-59,
  69-70, 86-87) are attached to the preceding measure. Within a page, every heading matching
  `(Static |Post-behavioural )?Exchequer impact (£m)` opens a table; tokens matching `^[+-]?\d[\d,]*m?$` are values,
  six per row, and the text between rows is the row label. The parse was printed in full and checked row by row
  against the page text (94 measures, 109 table rows, 654 cells).

## What is staged

- 654 Exchequer-impact cells: one row per (measure, FY, table row), `metric: revenue_change`, `unit_concept: gbp`,
  `value = value_raw (£m, sign and trailing "m" as printed) x 1e6`. 86 measures print a single "Exchequer impact
  (£m)" table; 8 print both a static and a post-behavioural table (two-child limit, Motability, personal tax
  thresholds, salary sacrifice, EOT CGT relief, HVCTS, gambling duties, eVED). Sub-rows are kept as printed
  (`conditions.table_row`): "o/w additional revenue / o/w additional spending" (Warm Home Discount, fire
  precepts), "Transitional Relief / Transitional Relief Supplement", "RHL multipliers / High-value multiplier /
  Small business rates relief and rural rate relief interaction", "Exchequer impact [AME savings only]".
- 12 tax-base claims (`proposed_metric: tax_base`): Motability lease payments ~£3.5bn 2026-27; personal-tax
  income base ~£2 trillion 2028-29; salary-sacrificed pension contributions £32bn in 2024 (calendar year,
  `time_basis: annual`); EOT chargeable gains ~£6.8bn 2026-27; HVCTS 165,000 properties 2028-29
  (`proposed_unit: properties`); gambling GGY ~£10bn 2026-27 and its £2.3bn / £7.1bn / £0.3bn split; eVED 5.5m cars
  and 8,000 miles a year 2028-29 (`proposed_unit: cars`, `miles_per_car_per_year`); CIS labour fraud c£0.5bn a year
  (2022 assessment, `basis: outturn`).
- 32 behavioural-parameter claims (`proposed_metric: behavioural_parameter`, unit `percent` or proposed
  `elasticity` / `years`): RO household share ~41%; two-child-limit take-up 11% / 22%; Motability pass-through
  36% and elasticity -1.75; business-rates-retention reserves 25%; thresholds TIE response 1.3%; salary sacrifice
  5% pay growth, 5% rising to 10% base reduction (range_low/range_high), 5% smoothing; EOT 55% / 45% split and
  elasticities 1.3 / 3.4; HVCTS 2.5% base reduction, 100% capitalisation, 5% discount rate, bunching elasticities
  1.0-1.5 (range); gambling 89% pass-through and elasticities -1.7 / -1.15; SDIL 65% reformulation; eVED
  elasticity -2, 5% discount rate, 15-year life, driving elasticity -0.16, 98.5% compliance; fire precept 95%
  take-up; third-party-data 90% matching; debt-staff optimism bias 75%.
- 1 behavioural component in GBP: the thresholds TIE response "reduce the static costing by £180m (1.3%) in
  2030-31" (`metric: revenue_change`, `scoring_method: behavioural_effect`, sign convention as worded).

## Conventions (load-bearing)

- **Sign.** The document prints no legend. `conditions.sign_convention` on every exchequer row reads: "positive =
  yield to the Exchequer (reduces borrowing); negative = cost to the Exchequer (no legend printed in the
  document; convention observed from the costings' own wording, e.g. 'yield' rows carry + and 'cost' rows carry
  -)". Values are NOT re-signed. The same convention is stated in the Table 4.1 XLSX harvest
  (sources/harvest-uk-2026-08-02/uk_hmt) and in the SS2025 Table 3.1 footnote.
- **scoring_method.** `static` for "Static Exchequer impact (£m)" tables, `post_behavioural` for
  "Post-behavioural Exchequer impact (£m)" tables, and **`final`** for the single "Exchequer impact (£m)" table of
  the 86 one-table measures. `final` is used rather than forcing static/post_behavioural because 18 of those
  measures state that no behavioural adjustment was made and the rest say the costing "accounts for a
  behavioural response"; the verbatim classification is carried in `conditions.behavioural_adjustment`
  ("none: '<sentence>'" or "included (see note)") and the full costing-methodology paragraph is in `note`.
  Measures stating no behavioural adjustment (start page): 12 RO, 13 WHD, 17 UC surplus earnings, 20 HB cliff
  edge, 27 NICs Class 2/3 abroad, 29 BR Supporting Small Business, 36 VAT charity donations, 62 ETS maritime,
  66 homeworking relief, 67 CBAM, 74 Sizewell C, 81 British Coal, 82 PPF/FAS, 88 Horizon compensation,
  89 Capture redress, 96 Scottish police & fire pensions, 102 debt management staff, 112 Penalty Reform NMSA.
- **impact_channel** comes from the registry's Table 4.1 head (`spending_measure` / `tax_measure`);
  `not_on_table_4_1` for the six fiscally neutral measures. Spending-side costings (two-child limit, PIP, WFP,
  UC health element, ...) are still `metric: revenue_change` per the harvest brief, with the channel flagged so
  the ingest can re-map to benefit_cost_change if it prefers.
- **period** = FY end year (2025-26 -> 2026); `conditions.fy` carries the label. Calendar-year claims: the £32bn
  salary-sacrifice base (2024) and the CIS fraud assessment (2022), `time_basis: annual`.
- **baseline_policy** null throughout (current law at scoring, incl. the pre-announced indexation baseline in
  Annex A). No proposed_baseline.
- **geography** "UK" on every row (Exchequer impact); `conditions.measure_scope` names England / England and
  Northern Ireland / England and Wales where the costing text says so (business rates, HVCTS, landfill tax,
  WFP "presented on a UK-wide basis", International Student Levy, fire precepts).
- `parse_confidence: medium` on one cell: HVCTS static 2028-29 printed "+605" without the trailing "m".

## Coverage tally (seed bullets in "Policy costings document" and "Table 4.1" -> this family)

Seed bullets staged here (every costing page in the seed plus every page the seed does not list): RO;
Warm Home Discount; fuel duty; two-child limit (both legs); UC surplus earnings; Child Benefit 16-19;
Carer's Allowance review; HB cliff edge; TCR extension; Pension Credit accuracy; health and disability
operations; Motability (both legs + tax base + parameters); HB/PC administration; NICs Class 2/3 abroad;
personal tax thresholds (both legs + £2tn base + £180m/1.3%); employer NICs ST; Plan 2 student loans;
property income; dividends; savings; salary sacrifice (both legs + £32bn + parameters); HVCTS (both legs +
165,000 + parameters); IHT thresholds; trust-charges cap; post-departure loophole; gambling (both legs + GGY
bases + parameters); TOMS; low value imports; homeworking relief; eVED (both legs + 5.5m/8,000 + parameters);
ECS threshold; ECOS delay; PHEV easement and PHEV regulatory standard changes (two separate costings); LLE and
maintenance grants; supporting savers; APR/BPR transferability; British Coal; PPF/FAS; PIP reversal; WFP;
UC standard allowance/health element; fire precepts (net 0 + o/w rows + 95%); loan charge (pp.86-87, same
figures as the seed's Table 4.1 line 86).
Also staged although absent from the seed (the brief asks for every per-measure row): the business-rates,
EMI, VCT/EIS, UK Listing Relief, Youth Guarantee AME savings, VAT charity donations, cross-border VAT grouping,
business rates retention, soil and land remediation, EOT CGT relief (both legs), writing-down allowances, APD,
ETS maritime, DB surplus extraction, landfill tax, SDIL, CBAM, ACT, FYA zero-emission cars, Sizewell C,
compensation payments (Horizon, Capture), tariffs, the six fiscally neutral measures (MaPS levy, Immigration
Skills Charge, Economic Crime Levy, International Student Levy, fire precepts, Scottish police & fire pensions)
and the 18 "Closing the Tax Gap" costings.

Seed bullets in my sections NOT staged in this family, with reasons:
- Rail fares freeze and NHS prescription freeze (seed cites Table 4.1 lines 4-5): no costing note exists for
  them in PU 3595; they are Table 4.1 lines, already harvested (README rule 9).
- "Table 4.1 totals" and "Table 4.1 household lines" bullets: Table 4.1 already harvested (rule 9).
- Two-child limit "taking 450,000 children out of poverty": appears here only in the measure title
  (kept verbatim in `reform_hint`); the poverty claim is staged from Box 2.A in `uk_hmt_redbook`.
- TIIN bullets (thresholds, PSD, IHT, gambling, homeworking, ECS, ECOS, PHEV, WFP): staged in `uk_hmrc_tiins`.
- HVCTS factsheet: staged in `uk_hmt_redbook` (HM Treasury publication, not the costings document).
- Distributional analysis bullets (Figures 1.A/1.B/1.C, Table 2.C, Box 2.B): rule 9 (Figures 1.A/1.B never
  staged; 1.C table and 2.C already harvested; Box 2.B restates 1.A with no new number).

Numbers in the costings document deliberately not staged (recorded here so the tally is complete): the
Warm Home Discount "gross impact ... around £600 million a year" (the o/w rows carry the exact 590-640 figures);
UK Listing Relief "approximately £14bn to £17bn of capital raised from new listings per year" (an activity
assumption with no year, not the SDRT base); MaPS levy totals £185m-£197m and DEL £4m/£8m/£12.5m (levy levels,
not a tax base); the £59m / £64m / £89m HMRC investment envelopes (spending inputs); International Student Levy
£925 per student and 220-student allowance, Economic Crime Levy band charges, HVCTS band charges, eVED rates,
fuel duty pence-per-litre steps (policy design parameters, kept in `reform_hint`/`note`); thresholds "adjustment
for Tax Motivated Incorporations" and employer NICs ST "assumed to be negligible" (no number);
EOT "+£15m IT receipts per ppt increase" (per-ppt sensitivity, not a costing parameter); phasing "one-third /
two-thirds / full" for HVCTS capitalisation (in the note of the 100% row); third-party data "nearly two-thirds of
tax returns pre-populated" (not numeric).

## Distinct condition values

- geography: UK
- measure_scope: England | England and Northern Ireland | England and Wales (presented UK-wide incl. Scottish
  BGA and NI Executive funding)
- fy: 2025-26 | 2026-27 | 2027-28 | 2028-29 | 2029-30 | 2030-31 (plus calendar years 2024, 2022 via `period`)
- basis: forecast | outturn
- scoring_method: static | post_behavioural | final | behavioural_effect (absent on the 11 pure tax-base rows)
- sign_convention: the observed HMT convention (above) | "as worded: 'reduce the static costing by' (positive =
  reduction in the static yield)" (the £180m row)
- costing_leg_heading: Exchequer impact (£m) | Static Exchequer impact (£m) | Post-behavioural Exchequer impact (£m)
- table_row: Exchequer impact | Exchequer impact [AME savings only] | o/w additional revenue | o/w additional
  spending | Transitional Relief | Transitional Relief Supplement | RHL multipliers | High-value multiplier |
  Small business rates relief and rural rate relief interaction
- impact_channel: tax_measure | spending_measure | not_on_table_4_1
- behavioural_adjustment: "included (see note)" | 13 verbatim "none: '...'" sentences
- document_section: Fiscally Neutral Measures | Closing the Tax Gap Measures; fiscally_neutral: yes (...)
- national_accounts_basis: "All costings are presented on a National Accounts basis (p.10)"
- parameter (32 distinct labels) and component (13 distinct labels) on the tax-base/parameter rows

## Proposals used

- proposed_metric: `tax_base` (12), `behavioural_parameter` (32) — the latter is new to the proposal list;
  numeric behavioural assumptions are staged as claims (brief: "tax base and behavioural parameters as separate
  claims"), non-numeric ones live in `note`/`conditions`.
- proposed_unit: `elasticity` (9), `properties` (1), `cars` (1), `miles_per_car_per_year` (1), `years` (1).
- proposed_baseline: none.

## Attribution

All rows `attribution: own`, `benchmark_class: different_model` (HMT/HMRC/DWP costings certified by the OBR;
no restated figures in this document). measure_key: 66 registry keys; 49 rows null = the six fiscally neutral
measures (not on Table 4.1, no registry entry) and the fire-precept 95% parameter. Costing notes that share one
registry key: pp.28+29 (business rates TR/SSB), pp.54+55 (trust cap + post-departure loophole), pp.75+76
(PHEV easement + regulatory), pp.77+78 (LLE + maintenance grants), pp.88+89 (Horizon + Capture) and the 18
tax-gap notes (line 59).
