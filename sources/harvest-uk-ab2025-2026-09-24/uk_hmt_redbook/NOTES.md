# uk_hmt_redbook — Budget 2025 red book (HC 1492) household-facing headline claims + HVCTS factsheet

Staged 2026-09-24. Source slug `hm_treasury`. 39 rows (35 from the red book, 4 from the HM Treasury "High Value
Council Tax Surcharge" factsheet, which is HMT's own publication and so sits in this family rather than
`uk_hmrc_tiins`). 2 primaries in `manifest.jsonl`. Script: `stage_redbook.py` (hand-transcribed rows, every
`quote` verbatim from the text layer).

## Access recipe

- Red book: `curl -sSL` with a browser User-Agent to
  https://assets.publishing.service.gov.uk/media/6929b353345e31ab14ecf735/E03444720_Budget_2025_Web_Accessible.pdf
  (200, 4,330,185 bytes, sha256 fc112784bdcfccfd1dc362202dbcc7c54d4f17c2969dafae244e2edead7c468a); pypdf text
  extract, 152 PDF pages. Locators cite the printed page (PDF page = printed page + 6 in chapters 1-2): executive
  summary p.6, paras 2.3-2.4 and footnote 77 p.28, paras 2.8-2.10 p.29, Chapter 2 table and Box 2.A p.31,
  paras 2.20-2.23 p.32, Box 2.B p.33, para 4.168 p.113, Annex B p.131.
- HVCTS factsheet: gov.uk content API,
  https://www.gov.uk/api/content/government/publications/high-value-council-tax-surcharge/high-value-council-tax-surcharge
  (publication first_published_at 2025-11-26T13:41:59; organisations = HM Treasury). The hash is of the API JSON
  body (7,971 bytes); `details.body` HTML converted to text for quoting. `access: govuk_api`.

## What is staged

- Energy bills package (para 2.4, footnote 77, Chapter 2 table): £150 rounded and £154 unrounded average per GB
  household 2026-27 (`metric: average_annual_gain`, `unit: gbp_per_household`), the £88 / £59 / £7 components
  (RO / ECO / VAT) and the price-cap equivalents £134 = £67 + £60 + £6 (`proposed_metric: energy_price_cap_change`,
  Q1 2026 dual fuel cap, `time_basis: point_in_time`). Only the RO component carries the registry key
  `ab2025__renewables_obligation_exchequer_funded_75pct`; the totals and the ECO/VAT parts are `measure_key: null`
  because the ECO non-renewal has no Table 4.1 line. The footnote's method (total cost / GB households from the
  LCF 2021-24 grown with the OBR over-16 determinant) is in `note`; source_model `arithmetic`.
- CPI: "reduce inflation by over 0.2 percentage points in 2026-27" (range_low) and "cuts inflation by 0.4
  percentage points next year" — both OBR figures the red book repeats (footnotes 75/78): `attribution: restated`,
  source_model `obr_efo_forecast`.
- Warm Home Discount: six million households (total) and "a further 3 million" (extension), `affected_count`.
- Rail fares £300 per year (para 2.8, point) and "more than £300" (executive summary, range_low), per passenger;
  prescriptions "around £12 million" aggregate saving (`proposed_metric: aggregate_household_saving`); fuel £89
  per household with a car (includes Fuel Finder) and the Fuel Finder "around £40 a year" (restated DESNZ
  analysis, `measure_key: null`).
- Box 2.A: 450,000 children lifted out of poverty (`metric: poverty_count_change`, `unit: children`, value
  positive with `sign_convention` "as worded: 'lift ... out of poverty' (positive = reduction ...)") and the
  "around 550,000" package figure (`measure_key: null`); 95,000 children in Scotland and 69,000 in Wales
  (`affected_count`, geography Scotland/Wales). The red book gives no year: `period` 2030 (FY 2029-30) is taken
  from the OBR restatement (EFO para 3.20 "by 2029-30") and flagged `parse_confidence: medium`,
  `conditions.horizon: unstated in the red book ...`, `poverty_line: unstated in the red book`.
- Upratings (`metric: benefit_uprating_rate`, unit percent): UC Standard Allowance "over 6%" (range_low),
  other working-age benefits 3.8%, State Pension 4.8%, Pension Credit SMG 4.8% — all `measure_key: null`
  (pre-Budget legislation / statutory uprating, not Table 4.1 lines). State Pension: "over 12 million"
  pensioners (range_low), "up to £575" (range_high, per pensioner), 1.1 million Scotland / 700,000 Wales; UC
  Standard Allowance 540,000 households Scotland / 320,000 Wales (Annex B).
- NLW: £900 gross annual earnings for a full-time NLW worker (`proposed_metric: gross_earnings_change`) and
  "around 2.4 million" workers (`parse_confidence: medium` — footnote 104 calls the number provisional).
- HVCTS factsheet: "Fewer than 1%" of properties in England (`affected_share`, range_high, 2028-29); "around £430
  million of revenue per year from 2028/29" (`metric: revenue_change`); Council Tax raised £40.3bn in England
  2024-25 (`proposed_metric: revenue_level`, context, `measure_key: null`); average band D £2,280 with the £250
  Mayfair comparison in `conditions.comparator` (`proposed_metric: household_tax_change`, a level used for a worked
  comparison, `measure_key: null`).

## Coverage tally (seed bullets "Budget 2025 red book: household-facing headline claims" + HVCTS factsheet)

- Energy bills package £150/£154 = £88 + £59 + £7; £134 = £67 + £60 + £6; CPI "over 0.2ppt" -> staged (13 rows).
- Warm Home Discount six million / further 3 million -> staged.
- Rail fares £300; prescriptions £9.90 and ~£12m; fuel £89 -> staged (£9.90 is a policy parameter, kept in
  `reform_hint`; the seed's "the average car driver £89" wording is in Annex B, the para 2.9 wording "households
  with a car £89" is the quoted one).
- State Pension +4.8%, over 12 million, up to £575, 1.1m Scotland, 700,000 Wales, PC SMG +4.8% -> staged.
- NLW £12.71 (+4.1%), around 2.4 million, +£900 -> staged (rate and % kept in `reform_hint`).
- UC Standard Allowance over 6%, other benefits 3.8% -> staged.
- Two-child limit Box 2.A 450,000 / ~550,000 -> staged (+ Scotland/Wales child counts).
- Box 2.B restatement -> NOT staged: restates Figure 1.A with no new number (rule 9).
- HVCTS factsheet (<1%, £430m, £2,280, £250, £40.3bn) -> staged (4 rows; the £250 is a derived comparison kept in
  `conditions.comparator` rather than a value).
- Not staged from Box 2.A: the CPAG "£40 billion per year" cost of poverty and the "around 25% less at age 30"
  figure (third-party research the box cites, not scores of the measure).

## Distinct condition values

- geography: UK | Great Britain | England | Scotland | Wales
- fy: 2024-25 | 2025-26 | 2026-27 | 2028-29 | 2029-30 (4 rows `point_in_time`, period 2026, Q1 2026 cap)
- basis: static | forecast | outturn
- sign_convention: positive = gain to households (reduction in costs) | as worded: 'lift ... out of poverty'
  (positive = reduction in the number of children in poverty) | as worded: 'reduce inflation by' / 'cuts
  inflation by' (positive = reduction in CPI inflation) | as worded: 'raise' (positive = yield) | positive =
  increase in gross annual earnings
- subgroup (19 distinct): all GB households (average) | additional poorest households ... | typical dual fuel
  household ... | average passenger on the most expensive routes | commuters on the more expensive routes |
  patients in England (aggregate) | households with a car | households who own a car | pensioners (maximum ...) |
  pensioners supported by the Triple Lock | pensioners benefitting ... | households directly benefitting from the
  UC Standard Allowance uprating | full-time worker on the National Living Wage | low-paid workers ... | children
  in Scotland/Wales who will benefit | properties in England above the £2 million threshold | average band D
  charge ...
- component: energy bills package (rounded / unrounded) | RO | ECO | VAT savings | Measures to reduce energy bills
  | Fuel Finder ... | two child limit removal alongside other measures ... | Council Tax raised across England
- program: Universal Credit Standard Allowance | other working age benefit rates ... | basic and new State
  Pension | Pension Credit Standard Minimum Guarantee; index: September 2025 CPI | average weekly earnings
- horizon / poverty_line: "unstated in the red book ..."; policy_vintage: Universal Credit Act 2025 | Low Pay
  Commission recommendation ...; per: passenger | commuter | pensioner | worker per year; period_detail: Q1 2026
  dual fuel cap announced on 21 November 2025; comparison: compared with previous plans; status: provisional
  until DBT publish their Impact Assessment; measure_scope: England; aggregation: per year from 2028/29.

## Proposals used

- proposed_metric: `affected_count` (10), `energy_price_cap_change` (4), `affected_share` (1),
  `aggregate_household_saving` (1), `gross_earnings_change` (1), `revenue_level` (1), `household_tax_change` (1).
  `energy_price_cap_change`, `aggregate_household_saving`, `gross_earnings_change` and `revenue_level` are new
  spellings (the price-cap equivalents, the aggregate prescription saving, the NLW gross earnings figure and the
  Council Tax level fit no registered metric).
- proposed_unit: none (all units registered: gbp, gbp_per_household, percent, percentage_points, households,
  persons, children).
- proposed_baseline: none; `baseline_policy` null throughout (current law / pre-Budget world).

## Attribution

36 rows `own` (HM Treasury's own arithmetic, DWP-sourced government estimates published by HMT, administrative
counts); 3 rows `restated` (the two CPI effects, which the red book attributes to the OBR EFO, and the Fuel Finder
£40 attributed to DESNZ analysis). benchmark_class `administrative_fact` for counts/upratings from administrative
data and `different_model` for the modelled/arithmetic figures. Worked-example rows (rail £300, fuel £89, NLW
£900, band D £2,280, £575 maximum) are mode-3 material (README rule 10) and say so in `note`.
