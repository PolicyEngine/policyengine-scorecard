# uk_hmrc_tiins — HMRC tax information and impact notes published at Budget 2025

Staged 2026-09-24. Source slug `uk_hmrc`. 65 rows; 11 primaries in `manifest.jsonl` (9 TIINs with claims, the
ECS TIIN and the HMRC technical note fetched but with no claims — reasons in the manifest notes). Script:
`stage_tiins.py` (hand-transcribed rows; every `quote` verbatim from the content-API body).

## Access recipe

- Publication pages: `curl` (browser User-Agent) on
  `https://www.gov.uk/api/content/government/publications/<slug>`; each returns `details.attachments[].url`, the
  HTML attachment path.
- TIIN bodies: `https://www.gov.uk/api/content<attachment path>`; the JSON's `details.body` is the TIIN HTML
  (tables come through as `| `-separated cells), `first_published_at` gives the date, `links.organisations`
  the publisher (HM Revenue & Customs for all eleven; the HVCTS factsheet found via the same route is HM Treasury
  and was moved to `uk_hmt_redbook`). The manifest sha256 is of the attachment JSON body as served on 2026-09-24;
  `publication.url` is the human gov.uk URL of the attachment, `access: govuk_api`.
- Slugs: maintaining-income-tax-and-equivalent-national-insurance-contributions-thresholds-until-5-april-2031;
  income-tax-changes-to-tax-rates-for-property-savings-and-dividend-income (27 Nov 2025);
  inheritance-tax-thresholds; inheritance-tax-unused-pension-funds-and-death-benefits; changes-to-gambling-duties;
  income-tax-removal-of-the-tax-relief-for-additional-homeworking-expenses;
  vehicle-excise-duty-for-expensive-car-supplement-threshold-increase-for-zero-emission-vehicles;
  changes-to-employee-car-ownership-schemes-for-income-tax; benefits-in-kind-easement-for-plug-in-hybrid-electric-vehicles;
  income-tax-charge-on-winter-fuel-payments; changes-to-tax-rates-for-property-savings-and-dividend-income
  (technical note).

## What is staged

- Counts of individuals/estates/businesses affected (`proposed_metric: affected_count`, unit `persons` or proposed
  `estates` / `businesses`) and equalities shares (`proposed_metric: affected_share`, unit `percent`, with the
  TIIN's population comparator in `conditions.comparator`): thresholds 700,000 (vs CPI indexation, proposed
  baseline), 53% male, ~20% over SPA; property/savings/dividends 2.4m landlords (6%), 3.8m (9%), 3.9m (9%), 1.6m
  unchanged, 54% aged 55+, 4.8% Asian/Asian British/Indian, 2.9% Hindu; IHT thresholds 2,100 estates, +0.3ppt of
  UK deaths (`unit: percentage_points`, `measure_type: change_in_share`), "more than 90%" of estates no IHT
  (range_low), 79% aged 75+, 51% women; IHT pensions ~213,000 estates (`tax_base`), 10,500, 38,500, average +£34,000
  (`proposed_metric: average_tax_change`, per estate); gambling 134 bingo businesses and ~160 / 95 / 55 remote
  operators; homeworking 300,000 individuals, £62 / £124 (`household_tax_change`, per individual per year);
  WFP charge ~2.2m, ~1.3m PAYE, 900,000 SA, ~800,000 SA+PAYE, ~100,000 self-employed, ~£17 / ~£33 / ~£17 a month
  (`household_tax_change`, `gbp_per_month`), shares 72% under 80, 69% male, 33% disabled, 97% White, ~70%
  Christian, 63% married; ECOS 80,000 individuals, 79% / 79% / 88%, 1,900 + 200 companies; PHEV 150,000 employees,
  ~100,000 businesses, 79% / 79% / 88% (company-car proxy).
- Exchequer lines printed only in a TIIN and not in Table 4.1: the combined property + savings + dividends line
  +285 / +1045 / +2275 / +2230 / +2340 (£m, 2026-27 to 2030-31; `measure_key: null`, sum of three registry
  measures); the ECOS combined AB2024 + Budget 2025 line +15 in 2030-31; and the IHT-on-pensions line +710 / +1485
  / +1600 / +1665 from Table 4.2 (an Autumn Budget 2024 measure, `measure_key: null`, `attribution: restated`,
  staged because Table 4.2 is not in the 2026-08-02 harvest). The gambling TIIN's "raise over £1 billion per
  year" is staged as a range_low with `parse_confidence: medium` (no year printed; period set to 2027-28).
- TIIN Exchequer tables that restate Table 4.1 lines (thresholds line 46, IHT thresholds line 55, gambling line
  60, homeworking line 68, ECS line 73, PHEV line 77, WFP line 84) are NOT re-staged (README rule 9).

## Coverage tally (seed TIIN bullets)

- Thresholds TIIN: 700,000; 53% vs 50%; ~20% vs ~29% -> staged (3 rows).
- Property/savings/dividends TIIN: combined exchequer line; 2.4m/3.8m/3.9m/1.6m and the 6%/9%/9% shares;
  54% vs 39%; 4.8% vs 2.8%; 2.9% vs 1.5% -> staged (15 rows).
- IHT thresholds TIIN: 2,100; +0.3ppt; >90%; 79%; 51/49 -> staged (5 rows).
- IHT unused pension funds TIIN: Table 4.2 line; ~213,000; 10,500; ~38,500; ~£34,000 -> staged (8 rows).
- Gambling TIIN: 134; ~160/95/55 -> staged; "£0.2m a year" administrative saving NOT staged (business admin
  burden, not a score of the measure); equalities paragraph has no numbers.
- Homeworking TIIN: 300,000; £62; £124 -> staged.
- ECS TIIN: NOT staged — Exchequer table restates Table 4.1 line 73 and the CPI effect ("small negative effect")
  is not quantified; the document is in the manifest with that note.
- ECOS TIIN: 80,000; +15 (2030-31, combined); 79%/79% -> staged (+ 88% White and the 1,900/200 companies).
- PHEV TIIN: 150,000; ~100,000 businesses -> staged (+ equalities proxy shares); its Exchequer table restates
  Table 4.1 line 77 (not re-staged).
- WFP charge TIIN: 2.2m; 1.3m; 900,000; 800,000; 100,000; £17/£33/£17; 69% male, ~72% under 80, 33% disabled,
  97% White, ~70% Christian, 63% married -> staged (14 rows).
- Technical note on property/savings/dividend rates: in the manifest, no claims (policy parameters and a worked
  computation only).
- HVCTS factsheet: HM Treasury publication -> staged in `uk_hmt_redbook`.

## Distinct condition values

- geography: UK (measure_scope "England, Wales and Northern Ireland (property rates)" on the two landlord rows)
- fy: 2025-26 | 2026-27 | 2027-28 | 2028-29 | 2029-30 | 2030-31 (2 rows `point_in_time`, period 2025: the IHT
  equalities shares of IHT paid)
- basis: static (counts and shares — the TIINs describe them as static) | forecast (Exchequer lines)
- scoring_method: final (Exchequer lines only)
- sign_convention: positive = yield to the Exchequer (Table 4.1 convention) | positive = yield to the Exchequer
  (Table 4.2 convention) | positive = yield to the Exchequer | as worded: 'raise' (positive = yield) | positive =
  tax increase for the individual | positive = deduction from the pensioner
- subgroup: 44 distinct verbatim descriptors (male; over State Pension Age; landlords facing an increase in tax;
  ... ; PAYE customer with a typical winter payment of £200; aged 35-64 (company car recipients); ...)
- comparator: 50% of the UK adult population | around 29% of the projected UK adult population | 39% of UK adults
  | 2.8% of the UK adult population | 1.5% of the UK adult population | 26% of the UK adult population | 88% of the
  UK adult population | 52% of UK adults | 82% in the UK adult population
- comparison: compared to if these thresholds were indexed with CPI from 2028 to 2029 onwards | compared to
  increasing the thresholds with the Consumer Price Index
- component (13), population (3), measure_type: change_in_share | level share (unaffected) | share of IHT paid;
  per: estate | individual per year; share_of_taxpayers: 6% | 9% of taxpayers in 2029 to 2030; policy_vintage:
  Autumn Budget 2024 measure (Table 4.2 of Budget 2025); aggregation: per year (year unstated)

## Proposals used

- proposed_metric: `affected_count` (23), `affected_share` (24), `household_tax_change` (5), `tax_base` (1),
  `average_tax_change` (1 — new spelling: the IHT-on-pensions "average Inheritance Tax liability is expected to
  increase by around £34,000" is a per-estate change, not a household figure).
- proposed_unit: `businesses` (7), `estates` (4) — both new.
- proposed_baseline: "thresholds indexed with CPI from 2028 to 2029 onwards (TIIN counterfactual)" (1 row);
  "IHT thresholds increased with CPI (TIIN counterfactual)" (2 rows). `baseline_policy` null everywhere else.

## Attribution

61 rows `own` (HMRC's own PTM/SPI projections and administrative counts); 4 rows `restated` (the Table 4.2
IHT-on-pensions Exchequer line the TIIN repeats). benchmark_class: `different_model` for PTM/microsimulation
counts and shares, `administrative_fact` for business counts and the IHT-paid shares. source_model:
`hmrc_personal_tax_model` (24), `administrative_data` (25), `hmt_costing_obr_certified` (11 Exchequer cells),
`arithmetic` (5: £62/£124 and the £17/£33/£17 deductions). measure_key: 10 registry keys; 14 rows null (the
combined PSD line, the AB2024 IHT-on-pensions rows, the PSD equalities share for the combined population).
