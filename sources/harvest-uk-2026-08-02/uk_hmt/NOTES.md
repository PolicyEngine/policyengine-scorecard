# uk_hmt harvest — HM Treasury fiscal events (gov.uk)

Harvested 2026-08-02 (overnight UK fleet). Access: all direct `curl` with honest UA
`PolicyEngine-Scorecard-Harvester/1.0 (research; contact: max@policyengine.org)` — gov.uk and
assets.publishing.service.gov.uk served everything without any bot mitigation. Zero bypasses. Discovery
via the gov.uk search + content APIs (`/api/search.json`, `/api/content/...`).

## Coverage

Three fiscal events, per the tasking (Autumn Budget 2024; Spring Statement 2025; Budget 2025 — the
Nov-2025 event is titled "Budget 2025" on gov.uk, not "Autumn Budget 2025"). For each event: policy
costings document, distributional analysis ("Impact on households"), data-sources document, the fiscal
event document (Red Book), and the machine-readable scorecard XLSX where published (AB2024 Table 5.1 +
5.2; B2025 Table 4.1 + 4.2; SS2025 published no XLSX — its scorecard is Table 3.1 inside the Spring
Statement PDF, parsed from the text layer).

**Spring Statement 2026: no fiscal-event publications exist.** A Spring Statement occurred 3 March 2026
(HMT published "GDP deflators ... March 2026 (Spring Statement)" and the Debt Management Report 2026-27
that day), but gov.uk search/content APIs surface NO Spring Statement 2026 document, policy costings, or
distributional analysis — consistent with a forecast-only statement with no scorecard. Any March-2026
measures would appear in the OBR March 2026 EFO (harvest-obr's territory).

## Staged claims: 1368 rows

| block | rows |
|---|---|
| Autumn Budget 2024 — exchequer_impact | 450 |
| Autumn Budget 2024 — median_gross_income | 50 |
| Budget 2025 — exchequer_impact | 546 |
| Budget 2025 — median_gross_income | 50 |
| Spring Statement 2025 — exchequer_impact | 222 |
| Spring Statement 2025 — median_gross_income | 50 |

Blocks:
1. **Scorecard per-measure Exchequer impacts** (proposed_metric `exchequer_impact`, proposed_unit `gbp`):
   AB2024 Table 5.1 (70 measures + 5 total/subtotal lines, FY2024-25..2029-30, from XLSX);
   B2025 Table 4.1 (88 measures + 3 totals, FY2025-26..2030-31, from XLSX);
   SS2025 Table 3.1 (33 measures incl. 2 `o/w` sub-lines + 4 totals, FY2024-25..2029-30, from PDF text layer).
   reform_hint = verbatim measure name. Values £m as printed (value_raw), converted ×1e6 to GBP.
2. **Distributional-analysis annex Table 2.C** (proposed_metric `median_gross_income`, proposed_unit `gbp`):
   median gross income by decile × household composition, one table per event (AB2024: 2025-26;
   SS2025 and B2025: 2028-29). 10 deciles × 5 compositions × 3 events = 150 rows (blank cells staged
   suppressed with the verbatim small-sample footnote).

## Conventions (LOAD-BEARING — read before ingest)

- **Sign, SS2025 (STATED verbatim, incl. HMT's typo):** "Costings reflect the OBR's latest economic and
  fiscal determinants. Figures given as fiscal impacts, postive numbers showing savings and negative
  numbers costs." (Table 3.1 footnote 1.)
- **Sign, AB2024/B2025 XLSX:** no explicit legend in the workbooks. OBSERVED convention matches SS2025:
  announced giveaways/spending increases carry negative values (e.g. AB2024 line 1 "Investing in Public
  Services: Funding..." = −26,450 in 2024-25), takeaways positive (Employer NICs +23,770 in 2025-26,
  cross-checked against the AB2024 policy-costings note's "+23,770m"). Recorded per row as sign_note.
- **Fiscal years Apr–Mar.** period = int(first year of the FY label); time_basis = fiscal_year;
  conditions.fiscal_year carries the verbatim label ("2025-26").
- **Metric choice:** staged as proposed_metric `exchequer_impact`, NOT `revenue_change`, deliberately.
  The tables' concept is total Exchequer impact on PSNB (National Accounts basis, OBR-certified), and
  scorecard footnote (verbatim): "Many measures have both tax and spend impacts. Measures are identified
  as tax or spend on the basis of their largest impact." So even head=Tax rows can include spend-side
  effects. Mapping Tax-head rows to Metric.REVENUE_CHANGE is an ingest decision; conditions.head carries
  the verbatim Tax/Spend classification (Table 5.1/4.1 only — Table 3.1 has no head column; its totals
  split into "Total spending impact" and "Total tax & fees impact" rows instead).
- **OBR certification (verbatim, AB2024 costings intro):** "These costings are all submitted to the
  independent Office for Budget Responsibility (OBR) for their certification. All measures were
  certified." And: "All costings are presented on a National Accounts basis." The scorecard XLSX
  footnote: "Costings reflect the OBR's latest economic and fiscal determinants." These ARE the
  OBR-certified Red Book scorecard tables (Table 4.1-style of the tasking).
- **B2025 scorecard exclusions (verbatim footnote 2):** "Measures with no net increase to borrowing are
  not set out on this presentational scorecard. These are increases to levies (Economic Crime Levy,
  Financial Conduct Authority levies, Immigration Skills Charge, International Student Levy) to fund
  spending on government priorities, reclassification of spend for Mayoral Combined Authorities and
  police & fire pensions. AME and tax costings with an impact of less than ±£10 million in every year are
  excluded from the scorecard."
- **Rounding:** "Totals may not sum due to rounding." Verified: sum(measures) vs Total row differs by
  ≤£30m per column in every table (measures rounded to £5m).

## Distributional analysis — income concept and equivalisation (VERBATIM, AB2024 §2.7–2.8; SS2025 §2.7 and B2025 §2.7 confirmed to carry the same "before housing costs" + "modified OECD" definitions)

```
2.7  This distributional analysis uses equivalised net household
income, before housing costs, as the main indicator by which to rank
households from lowest income to highest income. This indicator is
comprised of several components:
•   ‘Equivalised’: equivalisation is a process that adjusts a household’s
    net income to take into account the fact that larger households will
    require a higher net income to achieve the same standard of living
    as a household with fewer members. The equivalisation factors used
    in the analysis are the modified OECD factors (as also used in DWP’s
    Households Below Average Income publication)

•   ‘Net’: household incomes are ranked after deductions from direct
    taxes, and after additions from welfare benefits. Deductions from
    indirect taxes, or additions through benefits-in-kind from public
    services, are not used to rank households

•   ‘Household’: incomes are assessed in aggregate at the household,
    not individual level. Comparing household, rather than individual,
    incomes reduces the subjectivity of this analysis, ensuring that no
    assumptions are made about how incomes or expenditure are
    shared between separate individuals within the household

•   ‘Before housing costs’: housing costs such as rent or the cost of
    servicing a mortgage are not deducted from household incomes
2.8    The household income distribution is created by ranking
households from the lowest equivalised net income to the highest
equivalised net income, and then dividing this ranking into ten equally
sized groups called deciles, across which the analysis is produced.




4 DWP, Income Dynamics: Movements between quintiles: 2010 to 2022, March 2024.

                                                   13
```

Model basis (verbatim, AB2024 §2.11):

```
2.11   Where possible, tax and welfare policy changes are analysed
using HM Treasury’s Intra-Governmental Tax and Benefit
Microsimulation model (IGOTM), which is underpinned by data from
the ONS’s Living Costs and Food (LCF) survey. The sample size of the
LCF means that in order to produce robust analysis three years of data
have been pooled together, specifically 2017-18 to 2019-206. This data is
then projected forward to reflect the financial year being modelled,
using historical Annual Survey of Hours and Earnings data on earnings
growth at different points across the income distribution as well as the
latest Office for Budget Responsibility average earnings and inflation
forecasts. The model generally makes no changes to the underlying
demographics, employment levels or expenditure patterns in the base
data.
```

So for every distributional row: income_concept = equivalised net household income, **BHC** (before
housing costs); equivalisation = **modified OECD** (HBAI-consistent); model = HMT IGOTM on pooled LCF
2017-18 to 2019-20. The annex Table 2.C cells themselves are **unequivalised household GROSS income**
medians ("pre-tax private income including earnings, private pensions, savings and investments, plus
benefit income") within deciles that are DEFINED by equivalised net BHC income — both facts are in each
row's conditions.

## Gaps and blockers

1. **Decile impact values (Figures 1.A/1.B/1.C) are chart graphics only.** No data labels in the PDF
   text layer, no underlying data table in the PDF or the gov.uk HTML rendition (checked SS2025 HTML:
   its only numeric table is annex Table 2.C). HMT does not publish the chart data. Staging them would
   require chart digitization = NOT verbatim, so not staged. This is the biggest gap: the per-decile
   % - of - net - income policy impacts (the headline UK distributional claims) have no published numbers.
   Options for the platform: (a) FOI/correspondence for the underlying data; (b) digitize with an
   explicit non-verbatim flag and generous error bars; (c) validate only the published qualitative
   statements (e.g. AB2024: "all but the richest 10% of households will benefit as a percentage of
   income from policy decisions in 2025-26").
2. **Table 5.2 / Table 4.2 (previously-announced measures) downloaded but NOT staged** — same £m-by-FY
   shape as 5.1/4.1; a rerun of the stager with their column layout covers them.
3. **SS2025 Table 2.1 (defence/ODA £bn table) not staged** (DEL plans, not tax-benefit measures).
4. **B2025 Red Book / AB2024 Red Book** downloaded for provenance; their Chapter tables duplicate the
   staged XLSXs.
5. Costings-document per-measure "Exchequer impact (£m)" tables equal the scorecard rows (spot-checked
   Employer NICs; both +23,770m for 2025-26) — not double-staged. The SS2025 costings PDF uses a
   2-column note layout; its 25 notes parse but with more layout noise (parse_confidence would be
   medium) — scorecard numbers were taken from Table 3.1 instead.

## PolicyEngine-UK-runnable measures (scorecard rows → parametric reforms)

Directly expressible (measure → PE-UK lever):
- **AB2024 Employer NICs** (rate 13.8→15%, secondary threshold →£5,000, Employment Allowance →£10,500,
  cap removed) — the headline £23.8-25.7bn/yr line.
- **AB2024 CGT main rates 18/24%** (+BADR/IR 14%→18% steps).
- **AB2024 IHT**: threshold freeze to 2030; pensions into estates (2027); APR/BPR £1m 100%→50% reform.
- **AB2024 VAT on private school fees** (20% from Jan 2025) + business-rates relief removal.
- **AB2024 SDLT higher rates** 3→5ppt (additional dwellings).
- **AB2024 Fuel duty** 5p-cut extension + no RPI uprating 2025-26.
- **AB2024 Winter Fuel Payments** restriction to Pension Credit recipients.
- **AB2024 Carer's Allowance earnings limit** to 16h @ NLW.
- **AB2024 abolition of non-dom regime** (4-year FIG) — partially modellable.
- **SS2025 PIP 4-point requirement** (from Nov 2026) and **UC health element** (50% cut for new claims,
  freeze) + **UC standard allowance CPI+5% path** — PE-UK parameter set covers UC rates; PIP assessment
  change needs an eligibility-share assumption (methodology note captured).
- **B2025 threshold freeze extension to April 2031** (PA £12,570, HRT £50,270, ART £125,140 + NICs
  equivalents) — the single biggest B2025 line.
- **B2025 property/savings/dividend rate rises (+2ppt each, staged years)**.
- **B2025 salary-sacrifice pension NICs cap (£2,000/yr from April 2029)**.
- **B2025 removal of the UC two-child limit** (from April 2026) — the child-poverty headline.
- **B2025 High Value Council Tax Surcharge** (£2m+ homes, from 2028-29) — needs property-value data.
- **B2025 Winter Fuel Payment targeting** (taxable income ≤£35,000).
- **B2025 fuel duty** cancel-uprating.
Comparisons: HMT/OBR-certified totals vs PE-UK microsimulation of the same parametric change;
divergences decompose into behavioural adjustments (HMT includes them; captured verbatim in the
methodology notes below), coverage, and data vintage.

## Assumptions registry — verbatim costing methodology notes

Each note below is the full verbatim text (title, measure description, tax/cost base, costing incl.
behavioural adjustments, Exchequer impact table, uncertainty) from the event's Policy Costings document
(pdftotext -layout extraction; £m table alignment may wobble but numbers are verbatim).

### [Autumn Budget 2024] Employer National Insurance contributions:

```
Employer National Insurance contributions:
Increase rate by 1.2 ppts to 15%, cut the Secondary
Threshold to £5,000 until 5 April 2028 and uprate
with CPI thereafter, increase Employment
Allowance to £10,500, remove the £100,000
Employment Allowance eligibility threshold
Measure description
This measure introduces a number of changes to Employer National
Insurance Contributions (NICs), including:

• Reducing the Secondary Threshold (ST) from £9,100 annual equivalent to
  £5,000 annual equivalent, then increasing it in line with CPI from 2028-29;

• Increasing the Employer NICs (ER NICs) rate from 13.8% to 15% (over the ST);

• Increasing the Employment Allowance (EA) from £5,000 to £10,500;

• Removing the Employment Allowance cap, meaning employers with ER
  NIC liabilities over £100,000 in the previous tax year (but which are
  otherwise eligible) are able to claim the full £10,500 Employment
  Allowance.
This measure will be effective from 6th April 2025.

The tax base
The tax base includes all employers paying ER NICs from April 2025. This is
estimated using HMRC’s Personal Tax Model based on the 2021-22 Survey of
Personal Incomes, projected forward using OBR’s Autumn Budget 2024
economic determinants.

For the Employment Allowance, the tax base consists of eligible ER NIC
liabilities between their current Employment Allowance claim and £10,500.

Costing
The static costing is estimated by applying the pre- and post-measure tax
regimes to the tax base described above.

The costing also accounts for changes to future incorporations of businesses.

Exchequer impact (£m)
               2024-25     2025-26      2026-27       2027-28    2028-29        2029-30

 Exchequer       +0m      +23,770m     +23,690m       +24,170m   +24,930m       +25,710m
 impact


Areas of uncertainty
The main uncertainties in this costing relate to the size of the tax base and
behavioural response.




                                      38
```

### [Autumn Budget 2024] Capital Gains Tax: Increase the main rates of CGT

```
Capital Gains Tax: Increase the main rates of CGT
to 18% and 24% from 30 October 2024, and the
Business Asset Disposal Relief (BADR) and
Investors' Relief (IR) rate to 14% from 6 April 2025
and to 18% from 6 April 2026
Measure description
This measure will increase the Capital Gains Tax (CGT) main rates to 18% and
24% for the lower and higher rate respectively, to be aligned with the
existing rates on residential property.

This measure will be effective from 30 October 2024.

The Business Asset Disposal Relief (BADR) and Investors’ Relief (IR) rate will
also increase to 14% from 6 April 2025 and 18% from 6 April 2026.

The tax base
The tax base consists of all CGT liable main rate assets and BADR and IR
eligible assets disposed of during the scorecard period. The tax base is grown
over that horizon by using the OBR’s Capital Gains Tax forecast.

Costing
The costing is estimated by applying the pre- and post-measure tax regimes
to the tax base described above.

The costing then accounts for behavioural responses, such as changing the
timing of disposals.

Exchequer impact (£m)
                2024-25    2025-26     2026-27    2027-28     2028-29    2029-30

 Exchequer       +90m      +1,440m     +1,370m    +1,350m    +2,180m     +2,490m
 impact


Areas of uncertainty
The main uncertainties in this costing relate to the size of the tax base and
the behavioural response.




                                      39
```

### [Autumn Budget 2024] Inheritance Tax: Include unused pension funds

```
Inheritance Tax: Include unused pension funds
and death benefits payable from a pension in the
value of estates from 6 April 2027
Measure description
This measure brings unused pension funds and death benefits payable from
a pension into a person’s estate for Inheritance Tax (IHT) purposes.

This measure will be effective from 6 April 2027.

The tax base
The tax base consists of death estates that contain unused pension funds
and death benefits. It is estimated using a combination of HMRC
administrative data and data from the Wealth and Assets Survey.

The tax base is grown over the scorecard period in line with the OBR forecast
for equity prices.

Costing
The static costing is estimated by applying the pre- and post-measure tax
regimes to the tax base described above.

The costing accounts for a behavioural response whereby individuals
restructure their estates by increasing the rate at which they draw down
their unused pensions, or by making greater use of other available reliefs and
exemptions.

Exchequer impact (£m)
                  2024-25    2025-26   2026-27      2027-28   2028-29    2029-30

 Exchequer          +0m       +0m           +0m     +640m     +1,340m    +1,460m
 impact


Areas of uncertainty
The main uncertainties in this costing relate to the size of the tax base and
the behavioural response.




                                       40
```

### [Autumn Budget 2024] Inheritance Tax: Reform agricultural property

```
Inheritance Tax: Reform agricultural property
relief and business property relief from 6 April
2026 by maintaining 100% relief for the first £1m of
combined assets and 50% relief thereafter, and
50% relief for “not listed” shares on the markets of
a recognised stock exchange
Measure description
This measure reforms Agricultural Property Relief (APR) and Business
Property Relief (BPR). In addition to existing nil-rate bands and exemptions,
the current 100% rates of relief will continue for the first £1 million of
combined agricultural and business property. The rate of relief will be 50%
thereafter, and in all circumstances for shares designated as “not listed” on
the markets of recognised stock exchanges, such as the Alternative
Investment Market (AIM).

This measure will be effective from 6 April 2026.

The tax base
The tax base consists of all estates subject to IHT that are projected to claim
APR or BPR across the scorecard period. The tax base is estimated using
HMRC administrative data.

The tax base is grown over the forecast in line with the OBR’s forecast for IHT
receipts.

Costing
The static costing is estimated by applying the pre- and post-measure tax
regimes to the tax base described above.

The costing accounts for a behavioural response whereby individuals
restructure their estates by making greater use of other available reliefs and
exemptions.

Exchequer impact (£m)
                  2024-25    2025-26    2026-27     2027-28    2028-29    2029-30

 Exchequer          +0m        +0m      +230m       +495m      +520m      +520m
 impact


Areas of uncertainty
The main uncertainties in this costing relate to the size of the tax base and
the behavioural response.




                                       41
```

### [Autumn Budget 2024] Inheritance Tax: Maintain thresholds at current

```
Inheritance Tax: Maintain thresholds at current
levels for a further two years until 6 April 2030
Measure description
This measure fixes the Nil-Rate Band and Residence Nil-Rate Band
thresholds at £325,000 and £175,000 respectively for tax years 2028-29 and
2029-30. It also fixes the Residence Nil-Rate Band taper at the current level of
£2 million.

This measure will be effective from 6 April 2028.

The tax base
The tax base consists of Inheritance Tax (IHT) liable estates estimated using
HMRC administrative data and projected using OBR economic
determinants.

Costing
The difference between the baseline IHT forecast and the forecast with these
changes, using the tax base above, gives the estimated static yield of the
threshold changes.

The costing accounts for a behavioural response whereby some estates
respond to the change in threshold relative to the pre-measures baseline.

Exchequer impact (£m)
                  2024-25    2025-26    2026-27     2027-28   2028-29    2029-30

 Exchequer          +0m        +0m          +0m      +0m       +110m      +355m
 impact


Areas of uncertainty
The main uncertainties in this costing relate to the size of the tax base and
sensitivity to the CPI forecast.




                                       42
```

### [Autumn Budget 2024] VAT: Applying the standard rate (20%) to

```
VAT: Applying the standard rate (20%) to
education and boarding services provided by
private schools from 1 January 2025
Measure description
This measure introduces VAT on independent school fees at the Standard
Rate of 20%.

This measure will be effective for school terms commencing on or after 1
January 2025.

The tax base
The tax base is the total fee income of private schools. This is estimated by
multiplying numbers of pupils at independent schools by average fees per
pupil. Pupil numbers are taken from the DfE school census and devolved
governments’ data. Average fees for member schools of the Independent
Schools Council (ISC) are taken from the ISC’s 2024 Census, and for other
schools are estimated using data from sampling.

The tax base is projected over the forecast period by applying forecast
growth in average earnings with an uplift based on observed historic growth
in fees.

Costing
Additional output VAT is calculated at 20% of the tax base above. This is then
reduced by estimated input VAT on purchases to arrive at the static costing.

The costing accounts for a behavioural response whereby schools absorb
part of the VAT liability through reserves and cost reductions, and pass on
the remainder as fee increases. An elasticity of demand is then applied to the
resulting average increase in fees. The demand effect is then phased over
the forecast period based on the expected timing of pupil movements. The
costing further assumes that expenditure displaced to or from spending on
school fees, from fee increases or departures from private schools, will partly
be displaced from or to other Standard Rated expenditure.

Exchequer impact (£m)
                  2024-25    2025-26   2026-27     2027-28    2028-29    2029-30

 Exchequer        +460m      +1,505m   +1,560m     +1,610m    +1,665m    +1,725m
 impact


Areas of uncertainty
The main uncertainties in this costing relate to the size of the tax base and
behavioural responses.




                                       34
```

### [Autumn Budget 2024] Stamp Duty Land Tax (SDLT): Increase the Higher

```
Stamp Duty Land Tax (SDLT): Increase the Higher
Rate of Additional Dwelling (HRAD) of SDLT by
2ppts from 3% to 5% from 31 October 2024
Measure description
This measure will increase the Higher Rates for Additional Dwellings (the
higher rates) surcharge on Stamp Duty Land Tax (SDLT) by 2 percentage
points from 3% to 5%. It will also increase the single rate of SDLT that is
charged on the purchase of dwellings costing more than £500,000 by
corporate bodies from 15% to 17%.

This measure will be effective from 31 October 2024.

The tax base
The tax base reflects property transactions that currently attract the higher
rates surcharge and single rate for corporate bodies. It is estimated using
HMRC’s SDLT microsimulation model, based on transactions in the financial
year 2022-23, and is grown in line with the OBR’s forecast of residential
property prices and transactions.

Costing
The static costing is estimated by applying the pre- and post-measure tax
regimes to the tax base described above.

The costing accounts for a behavioural response, including impacts on
residential property transactions liable to the higher rates and the single rate
for corporate bodies, and on residential property prices. The costing assumes
that a proportion of the disincentivised higher rates transactions will be
displaced by primary residence transactions.

Exchequer impact (£m)
                  2024-25    2025-26    2026-27    2027-28    2028-29    2029-30

 Exchequer         +115m      +90m      +170m       +255m      +280m      +310m
 impact


Areas of uncertainty
The main uncertainties in this costing relate to the size of the tax base and
behavioural response.




                                       37
```

### [Autumn Budget 2024] Fuel duty: One year extension to the 5p cut in

```
Fuel duty: One year extension to the 5p cut in
rates and no RPI increase in 2025-26
Measure description
This measure freezes the rate of fuel duty for a further 12 months. This
includes maintaining the 5 pence per litre (ppl) cut, which was first
implemented on 23 March 2022, on rates for heavy oil (diesel and kerosene),
unleaded petrol, and light oil, with a proportionate percentage cut
(equivalent to 5ppl from the main fuel duty rate of 57.95ppl) in other lower
rates and the rates for rebated fuels where practical.
The cut is currently due to expire on 23 March 2025 but will be extended to
22 March 2026.

The tax base
The tax base is all taxable fuel that is made available for use in the UK. The
projected volumes of taxable fuel are taken directly from the HMRC fuel duty
forecasting model.

Costing
The costing is calculated by taking the forecast baseline and applying the
difference in the forecast and policy duty rates.
Behavioural responses are included to account for changes in consumption
in response to this measure.

Exchequer impact (£m)
                  2024-25    2025-26   2026-27     2027-28    2028-29    2029-30

 Exchequer         -45m      -3,015m    -880m      -890m       -900m      -890m
 impact


Areas of uncertainty
The main uncertainties in this costing relate to the size of the tax base and
the behavioural response.




                                       60
```

### [Autumn Budget 2024] Winter Fuel Payments: Target payments at

```
Winter Fuel Payments: Target payments at
recipients of Pension Credit and certain other
means-tested benefits from winter 2024-25
Measure description
This measure targets Winter Fuel Payments to pensioner households in
receipt of Pension Credit, Universal Credit, income-related Employment and
Support Allowance (ESA), income-based Jobseeker’s Allowance (JSA),
Income Support, Child Tax Credit or Working Tax Credit. Winter Fuel
Payments are devolved to the Scottish Government and the Northern
Ireland Executive. All figures are on a UK-wide basis, reflecting the Scottish
Government’s Block Grant Adjustment and Northern Ireland Executive
funding changes.

This measure will be effective from Winter 2024-25.

The cost base
The cost base is estimated using benefit caseload, expenditure forecasts and
official statistics from the DWP publication ‘Income-related benefits:
estimates of take-up’.

Costing
The costing is estimated by applying the pre- and post-measure benefit
regimes to the cost base described above.

A behavioural adjustment is made to account for changes in Pension Credit
take-up.

Exchequer impact (£m)
                  2024-25    2025-26   2026-27     2027-28    2028-29    2029-30

 Exchequer        +1,450m    +1,510m   +1,555m     +1,580m    +1,605m    +1,655m
 impact


Areas of uncertainty
The main uncertainties in this costing relate to the size of the behavioural
response.




                                       50
```

### [Autumn Budget 2024] Carer’s Allowance: Increasing the earnings limit to

```
Carer’s Allowance: Increasing the earnings limit to
the equivalent of 16 hours at the National Living
Wage from April 2025
Measure description
This measure will raise the Carer’s Allowance Weekly Earnings Limit from
£151 to the equivalent of 16 hours per week at the National Living Wage
(£196). The Weekly Earnings Limit will then increase in line with future
National Living Wage increases.

This measure will be effective from 7 April 2025.

The cost base
The cost base is DWP’s forecast caseload for Carer’s Allowance and OBR
projections for increases in the National Living Wage.

Costing
The costing is calculated by measuring the potential group of new claimants
who fall between the previously assumed earnings limits and the projected
new earnings limit. This group has been estimated by using weighted labour
market data.

Exchequer impact (£m)
                  2024-25    2025-26    2026-27     2027-28    2028-29    2029-30

 Exchequer          +0m        -25m      -70m        -105m      -135m      -165m
 impact


Areas of uncertainty
The main uncertainties in this costing relate to the size of the behavioural
response in relation to levels of take-up of Carer’s Allowance amongst newly
eligible individuals. Additionally, the precise earnings distribution for carers
in employment is not known.




                                       64
```

### [Autumn Budget 2024] Abolition of non-domicile tax status and

```
Abolition of non-domicile tax status and
introduction of a residence-based regime: remove
the 50% discount on foreign income in 2025/26;
apply inheritance tax; set Capital Gains Tax
rebasing date at 5 April 2017; and extend the
Temporary Repatriation Facility from two to three
years
Measure description
The remittance basis of taxation for non-UK domiciled individuals is being
abolished and replaced with a simpler residence-based regime. Individuals
opting into the regime will not pay UK tax on foreign income and gains (FIG)
for the first four years of tax residence, provided they have been non-tax
resident for the previous 10 years.

This measure introduces a residence-based system for Inheritance Tax and
the planned 50% reduction in foreign income subject to tax in the first year
will be scrapped. For Capital Gains Tax purposes, current and past
remittance basis users will be able to rebase personally held foreign assets to
5 April 2017 on disposal where certain conditions are met.

Overseas Workday Relief will be extended to a four-year period and will be
subject to an annual financial limit of the lower of £300,000 or 30% of net
employment income. This measure also extends the previously announced
Temporary Repatriation Facility to three years and expands the scope to
trust structures.

This measure will be effective from 6 April 2025.

The tax base
The tax base is made up of the foreign assets, income and gains of UK
residents from HMRC administrative data and is grown over the forecast
horizon using the OBR forecast for world equity prices.

Costing
The static costing is estimated by applying the pre- and post-measure tax
regimes to the tax base described above.

The costing accounts for behavioural responses including migration and tax
planning.

Exchequer impact (£m)
               2024-25    2025-26     2026-27       2027-28   2028-29    2029-30

 Exchequer      +0m           *       +4,170m       +5,895m   +2,545m      +95m
 impact


Areas of uncertainty
The main uncertainties in this costing relate to the size of the tax base and
behavioural response.


                                      32
```

### [Spring Statement 2025] Personal Independence Payment (PIP): Change

```
Personal Independence Payment (PIP): Change
the PIP assessment so claimants must score four
points in any one activity from 2026-27
Measure description
This measure will require those claiming the Personal Independence
Payment (PIP) to score a minimum of 4 points in at least one activity to
qualify for a daily living award.

This measure will be effective for new claims from November 2026 and for
existing claimants at their next award review following this date.

The cost base
The cost base for this measure is estimated from current and forecasted PIP
cases and those of passported benefits like Carer’s Allowance and Universal
Credit Carer’s Element.

Costing
The costing accounts for AME savings to DWP by estimating the number of
daily living claims that will no longer meet the new requirement to score a
minimum of four points in an activity.

The costing also accounts for changes in claimant behaviour as the policy
becomes more widely known, with varying reductions in volumes impacted
by the changes over different cohorts.

Exchequer impact (£m)
                  2024-25   2025-26   2026-27     2027-28    2028-29   2029-30

 Exchequer
                   +0m        +0m         +210m   +1,755m    +3,365m   +4,515m
 impact


Areas of uncertainty
The main uncertainty in this costing relates to the size of the behavioural
response. Additionally, the composition and timing of new claims and award
reviews could vary compared to the forecast, which is based on recent
trends.




                                      8
Personal Independence Payment (PIP): Increase
capacity for processing award reviews from April
2026
```

### [Spring Statement 2025] Work Capability Assessment: Do not proceed with

```
Work Capability Assessment: Do not proceed with
Autumn Statement 2023 descriptor reforms
Measure description
This measure will cancel the implementation of the reforms to the Work
Capability Assessment (WCA) announced at Autumn Statement 2023 that
were due to take effect this year.

The cost base
The cost base for this measure is the OBR Spring Statement 2025 forecast for
Employment and Support Allowance (ESA) and Universal Credit Health
Element (UCHE) spending. This forecast incorporates the estimated impact
of removing the descriptor reforms as announced at Autumn Statement
2023.

Costing
The impact of reversing the decision to remove the reformed descriptors is
estimated using the same methodology as the original decision scored at
Autumn Statement 2023, with updates for latest forecasts and other data.

Exchequer impact (£m)
                  2024-25    2025-26   2026-27     2027-28    2028-29    2029-30

 Exchequer
                    +0m       +0m       -200m      -730m      -1,205m    -1,645m
 impact


Areas of uncertainty
The main uncertainty in this costing relates to the size of the behavioural
response.




                                       10
```

### [Spring Statement 2025] Universal Credit Health Element: Maintain at 2025-

```
Universal Credit Health Element: Maintain at 2025-
26 rate until 2029-30, reduce rate by 50% for new
claimants from April 2026 and maintain until
2029-30
Measure description
This measure will reduce the gap between the Universal Credit Standard
Allowance (UCSA) and Health Element (UCHE). From 2026-27, the award rate
of UCHE will be frozen for existing claimants and new claimants will receive a
lower award, set at 50% of the Limited Capability for Work- and Work-
Related Activity (LCWRA) rate for 2026/27. This will be frozen over the
forecast.

This measure will be effective from 1 April 2026

The cost base
The cost base for this measure for this measure is the OBR forecast for
Employment and Support Allowance (ESA) and UCHE spending at Spring
Statement 2025.

Costing
The savings from existing claimants are calculated by applying the frozen
UCHE weekly rate against the counterfactual CPI-uprated weekly rate. For
new claimants the savings are calculated by applying the 50% rate, against
the counterfactual current rate uprated by CPI. To find total savings, these
counterfactuals are applied to the proportion of the caseload which are new
claims, and which are existing claims, in each year.

Exchequer impact (£m)
                  2024-25    2025-26        2026-27   2027-28   2028-29   2029-30

 Exchequer
                    +0m        +0m          +750m     +1,535m   +2,295m   +3,005m
 impact


Areas of uncertainty
The main uncertainty in this costing relates to the size of the behavioural
response.




                                       12
```

### [Spring Statement 2025] Work Capability Assessment: Do not proceed with

```
Work Capability Assessment: Do not proceed with
Autumn Statement 2023 descriptor reforms
Measure description
This measure will cancel the implementation of the reforms to the Work
Capability Assessment (WCA) announced at Autumn Statement 2023 that
were due to take effect this year.

The cost base
The cost base for this measure is the OBR Spring Statement 2025 forecast for
Employment and Support Allowance (ESA) and Universal Credit Health
Element (UCHE) spending. This forecast incorporates the estimated impact
of removing the descriptor reforms as announced at Autumn Statement
2023.

Costing
The impact of reversing the decision to remove the reformed descriptors is
estimated using the same methodology as the original decision scored at
Autumn Statement 2023, with updates for latest forecasts and other data.

Exchequer impact (£m)
                  2024-25    2025-26   2026-27     2027-28    2028-29    2029-30

 Exchequer
                    +0m       +0m       -200m      -730m      -1,205m    -1,645m
 impact


Areas of uncertainty
The main uncertainty in this costing relates to the size of the behavioural
response.




                                       10
```

### [Budget 2025] Property Income: Introduce separate tax rates for

```
Property Income: Introduce separate tax rates for
property income at 22% for the property basic
rate, 42% for the property higher rate and 47% for
the property additional rate, from 6 April 2027
Measure description
This measure creates a separate income tax rate for property rental income
which increases tax on property income for unincorporated landlords by
adding 2 percentage points to the basic rate, higher rate, and additional rate.

This measure will be effective from 6 April 2027.

The tax base
The tax base consists of all individuals and partnerships that receive property
income. It is estimated using HMRC administrative data from the 2023/24
Self-Assessment returns.

The tax base is grown over the forecast horizon using the OBR’s forecast for
growth in land and property income.

Costing
The costing is estimated by applying the pre- and post-measure tax regimes
to the tax base described above.

The costing accounts for a behavioural response whereby some landlords
choose to operate through a company structure rather than as an
unincorporated business to avoid the increased property income taxation,
though this response is expected to be limited.
The costing also accounts for the impact of this measure on rental prices and
house prices.

Exchequer impact (£m)
                  2025-26    2026-27   2027-28      2028-29   2029-30    2030-31

 Exchequer          +0m       +0m           +5m     +590m      +435m     +445m
 impact


Areas of uncertainty
The main uncertainties in this costing relate to the size of the behavioural
response.




                                       44
```

### [Budget 2025] Savings Income: Increase tax rates on savings

```
Savings Income: Increase tax rates on savings
income by 2ppts at the basic, higher and
additional rate from 6 April 2027 and maintain the
Starting Rate of Savings limit at £5000 from April
2026 to April 2031
Measure description
This measure increases the Basic, Higher and Additional Income Tax rates on
savings income by 2 percentage points. It applies to taxable savings income,
excluding Individual Savings Account returns and savings income covered
by the Personal Allowance, Personal Savings Allowance, or the Starting Rate
for Savings.

This measure will be effective from 6 April 2027.

The tax base
The tax base consists of taxable savings income held by individuals. This is
estimated using HMRC’s Personal Tax Model, drawing on administrative data
from the 2022–23 Survey of Personal Incomes.

The tax base is grown over the forecast horizon using the OBR’s forecast for
growth in savings income.

Costing
The costing is estimated by applying the pre- and post-measure tax regimes
to the tax base described above

The costing accounts for a behavioural response whereby some individuals
shift their savings into tax-advantaged products such as Individual Savings
Accounts (ISAs).

Exchequer impact (£m)
                  2025-26    2026-27    2027-28     2028-29    2029-30       2030-31

 Exchequer          +0m        +5m       +55m       +525m       +470m        +505m
 impact


Areas of uncertainty
The main uncertainties in this costing relate to the size of the tax base,
behavioural response, and forecast of future returns to savings.




                                       46
```

### [Budget 2025] Dividend Income: Increase tax rates on dividend

```
Dividend Income: Increase tax rates on dividend
income by 2ppts at the ordinary and upper rate
from 6 April 2026
Measure description
This measure increases the ordinary and upper rate of dividend tax by two
percentage points.

This measure will be effective from 6 April 2026.

The tax base
The tax base consists of all taxable dividend income received by individuals.
This is estimated using HMRC’s Personal Tax Model, using data from the
2022–23 Survey of Personal Incomes.

The tax base is grown over the forecast horizon using the OBR’s forecast for
growth in dividend income.

Costing
The costing is estimated by applying the pre- and post-measure tax regimes
to the tax base described above.

The costing accounts for a behavioural response whereby individuals reduce
their taxable dividend income, bring dividend income forward (forestalling),
or change their decision to incorporate businesses in response to the rate
increase.

Exchequer impact (£m)
                  2025-26    2026-27   2027-28      2028-29   2029-30    2030-31

 Exchequer          +0m      +280m      +985m       +1,160m   +1,325m    +1,390m
 impact


Areas of uncertainty
The main uncertainties in this costing relate to the size of the behavioural
response.




                                       45
```

### [Budget 2025] Salary Sacrifice: Limit the value of salary sacrificed

```
Salary Sacrifice: Limit the value of salary sacrificed
pension contributions that can receive employee
and employer NICs relief to £2,000 per year from 6
April 2029
Measure description
This measure applies Class 1 Employee (Primary) and Employer (Secondary)
National Insurance Contributions (NICs) to “salary sacrificed” pension
contributions above an annual cap of £2,000, effective from 6 April 2029. The
policy aims to restrict the incentive for employers and employees to use salary
sacrifice arrangements for pension contributions to access additional NICs
savings.

Tax base and data
The tax base consists of salary sacrifice and bonus sacrifice pension
contributions above the £2,000 annual cap.

   •   The main data source is the 2024 ONS Annual Survey of Hours and
       Earnings (ASHE), from which estimates of the number of employees
       using salary sacrifice and the value of employee pension contributions
       are made.

   •   The tax base is projected in line with the historic trends and the OBR’s
       forecast for employment and wage growth.
In 2024, it is estimated £32bn of pensions contributions used salary sacrifice
pension arrangements, with the value of contributions predominantly from
higher and additional rate taxpayers.

Static costing
The static Exchequer impact is calculated by applying the pre- and post-
measure tax regimes to the tax base described above. This results in the
following static costing:

Static Exchequer impact (£m)

              2025-26    2026-27    2027-28    2028-29    2029-30    2030-31

 Exchequer
              +0m        +0m        +0m        +0m        +4,870m    +5,070m
 impact

Post-behavioural costing
The costing includes various behavioural responses, two key ones have been
set out below:

  Behaviour                Description




                                      47
  Employers may react      The costing assumes that employers put 5% of
  to these reforms by      pay growth of the affected population towards
  changing how they        employer contributions.
  compensate staff to
  replicate some of the
                           Furthermore, the costing assumes a reduction in
  savings afforded by
                           the tax base of 5% rising to 10% by the end of the
  the existing salary
                           forecast     reflects      other     formalisation
  sacrifice regime.
                           arrangements.


                           The extent of the adjustment made reflects
                           HMRC and OBR judgement.
  Employees        may     The costing assumes an overall 5% reduction in
  smooth           their   the tax base from this behaviour.
  contributions
  between pay periods
                           This adjustment      reflects   HMRC   and   OBR
  to make efficient use
                           judgement.
  of NICs exemption on
  contributions under
  £2k.
The OBR also assume employers will seek to pass through some costs to
wages. A behavioural adjustment has been made for this in the costing. The
OBR's pass-through assumptions are detailed in their Economic and Fiscal
Outlook.

The costing also accounts for other behaviours, including:

   •   Forestalling prior to the implementation of the measure (the bringing
       forward of contributions
   •   Shifting towards other schemes (i.e. ‘net pay arrangements’ or ‘relief at
       source’)
   •   Increased contributions to meet auto-enrolment minimums
   •   Reduction in contributions by individuals in DC schemes

The table below sets out the post-behavioural costing

Post-behavioural Exchequer impact (£m)

                 2025-26   2026-27    2027-28   2028-29    2029-30    2030-31
 Exchequer
                 +0m       -40m       -55m      -75m       +4,845m +2,585m
 impact

Areas of uncertainty
The main uncertainties relate to behavioural responses, the use of ASHE
sample data, population growth, and economic factors such as wage growth.
The extent to which employers and employees will adapt their behaviour in
response to the measure is particularly uncertain.




                                      48
```

### [Budget 2025] High Value Council Tax Surcharge: Introduce a

```
High Value Council Tax Surcharge: Introduce a
surcharge on owners of residential properties
valued over £2m in England from 1 April 2028
Measure description
The High Value Council Tax Surcharge (HVCTS) introduces a new annual
charge on owners of properties in England valued at £2.0 million and above,
taking effect from April 2028. The charge will be based on a targeted
revaluation exercise carried out by the Valuation Office, on the basis of
property values in 2026. It will apply in addition to existing Council Tax. Among
other areas the government will consult on the criteria for and mechanism
through which to deliver support, reliefs, exemptions and appeals.

Tax base and data
The tax base comprises properties in England valued above £2 million in 2026.
Estimates combine commercial valuation data, Council Tax statistics, SDLT
transaction data, and Valuation Office data. Further adjustments, including for
social housing, reduce the base by 2.5%. OBR property price forecasts and
new-build assumptions are used to project property prices and volumes,
resulting in an estimated 165,000 properties subject to the tax in 2028–29.

Static costing
Static costing multiplies projected properties by band charges, uprated by CPI
from 2029–30.

Static Exchequer impact (£m)

                         2025-26          2026-27          2027-28           2028-29          2029-30           2030-31
 Exchequer               +0m              +0m              +0m               +605             +620m             +635m
 impact

Post-behavioural costing
The costing includes two main behavioural responses, which have been set
out below:

 Behaviour                  Description
                            Based on a range of studies2, 100% capitalisation is
 Price                      assumed, phased in over 3 years. The net present value
                            (NPV) of the annual charge is calculated, assuming it
 Capitalisation
                            continues in perpetuity and using a discount rate of 5%. The
                            price adjustment is phased in gradually: one-third in the




2 Giertz, S.H., Ramezani, R. and Beron, K.J. (2021). Property tax capitalization, a case study of Dallas County. Regional

  Science and Urban Economics, 89, p.103680. doi:https://doi.org/10.1016/j.regsciurbeco.2021.103680.

Coste, J. (2024). Capitalization of Property Tax Incentives: Evidence From Philadelphia. FHFA Staff Working Papers.
  Available at: https://ideas.repec.org/p/hfa/wpaper/24-01.html.

Smith, O., Palmon, O. and Smith, B.A. (2025). New Evidence on Property Tax Capitalization. Journal of Political Economy,
  106(5), pp.1099–1128. DOI:http://dx.doi.org/10.1086/250041

                                                               51
                          first year, two-thirds in the second, and full pass-through
                          from the third year onwards.
                          Drawing on research into SDLT notches3, the costing
                          assumes relatively lower demand for properties at values
                          just above band thresholds. Bunching elasticities of 1.0 to 1.5
                          are used. These are adjusted downward compared to the
                          SDLT empirical evidence to reflect the smaller impact on
 Bunching
                          credit constraints of a recurring tax compared to an upfront
                          transaction tax. The elasticities are used to estimate a value
                          range above a threshold for which properties would see
                          price effects additional to the capitalisation effect, using the
                          net present value of the tax.

The costing also includes a small adjustment for changes to the growth in the
stock of impacted properties.

The costing includes adjustments for compliance, appeals and an assumed
support scheme:

     •    Non-payment: The assumption reflects the Council Tax non-payment
          rate uplifted to account for the owners, rather than occupiers, being
          liable for the tax.

     •    Appeals: Successful appeals are assumed based on Council Tax and
          Business Rates appeal success rates.

     •    Support scheme and inability to pay: The Wealth and Assets Survey is
          used to estimate the share of households who may be unable to pay
          the charge, including those who may qualify for a support scheme,
          which is to be consulted on.

The costing also accounts for impacts on other tax heads. Price capitalisation
affects SDLT, CGT, IHT, and ATED receipts. Transaction impacts include
temporary reductions pre-implementation and increases in churn post-
implementation, impacting SDLT and CGT receipts.

Post-behavioural Exchequer impact (£m)

                       2025-26          2026-27          2027-28          2028-29          2029-30          2030-31
 Exchequer
                       -60m             -120m            -155m            +400m            +430m            +435m
 impact


Areas of uncertainty
The main uncertainties in this costing surround the size of the tax base,
behavioural and compliance effects and resultant impacts on other tax heads.




3 Best, M.C. and Kleven, H.J. (2017). Housing Market Responses to Transaction Taxes: Evidence From Notches and

 Stimulus in the U.K. The Review of Economic Studies, 85(1), pp.157–193. doi:https://doi.org/10.1093/restud/rdx032.

                                                           52
```

### [Budget 2025] Universal Credit Child Element: Remove the two

```
Universal Credit Child Element: Remove the two
child limit from April 2026, taking 450,000
children out of poverty
Measure description
The measure will remove the limit on the number of children a household on
Universal Credit can claim the child element for.

Cost base and data
The cost base is the Universal Credit expenditure forecast before removal of
the two-child limit.
The main data sources are the Family Resources Survey (FRS) on which
DWP’s Policy Simulation Model (PSM) based, the UC forecasts and the OBR’s
economic assumptions, which are both incorporated into the model. UC
administrative data is also used to account for exceptions to the current
policy, which are not modelled in the PSM.

Static costing
The static Exchequer impact is calculated by comparing the baseline
Universal Credit expenditure forecast before the policy change to
expenditure after removal of the two-child limit for households with third
and subsequent children born after April 2017.

Static Exchequer impact (£m)

                     2025-26   2026-27    2027-28     2028-29    2029-30    2030-31

 Exchequer
                     +0m       -2,055m    -2,250m     -2,445m -2,715m       -2,850m
 impact


Post-behavioural costing
The costing includes one key behavioural response, which is set out below:

 Behaviour             Description

 Some eligible
                       Estimated using the Policy Simulation Model (PSM) and
 households may
                       Family Resources Survey data. An additional take up rate is
 begin claiming
                       applied at 11% for those newly entitled and 22% for
 due to the higher
                       previously entitled but non-claiming households. This
 entitlement or
                       estimate is uncertain and reflects judgement as to how
 increased
                       people will respond to the change.
 publicity



The costing assumes no significant impacts assumed for other benefits. The
PSM modelling accounts for interactions between the policy and the benefit
cap.
After applying the behavioural responses above, this results in the following
post-behavioural costing


                                           15
Post-behavioural Exchequer impact (£m)

                 2025-26   2026-27   2027-28   2028-29   2029-30    2030-31

 Exchequer       +0m       -2,365m   -2,590m   -2,815m   -3,095m    -3,235m
 impact



Areas of uncertainty
The main uncertainties in this costing are on behavioural assumptions. The
estimate for increased take-up is highly uncertain, and the actual response
may differ. Costs are also sensitive to wider demographic and
macroeconomic trends.




                                     16
```

### [Budget 2025] Winter Fuel Payment: Target to pensioners with

```
Winter Fuel Payment: Target to pensioners with
taxable income below or equal to £35,000 from
Winter 2025
Measure description
This measure targets Winter Fuel Payments in England and Wales to
pensioners with a taxable income below or equal to £35,000. The Winter Fuel
Payment will be made to all eligible pensioners who do not opt-out and the
full value of the payment will be recovered via HMRC for individuals with
taxable incomes exceeding £35,000 and not in receipt of Pension Credit,
Universal Credit, income-related Employment and Support Allowance (ESA),
income-based Jobseeker’s Allowance (JSA), Income Support, Child Tax Credit
or Working Tax Credit. This measure will be effective from Winter 2025-26.

Inclusion of devolved government funding implications is without prejudice
decisions made by those governments. Figures are presented on a UK-wide
basis for transparency and consistency. Winter heating assistance is
devolved in Scotland, and Winter Fuel Payments are a transferred matter in
Northern Ireland. All figures reflect the UK government’s policy impact on
England and Wales, as well as resulting changes to the Scottish Block Grant
Adjustment and Northern Ireland Executive funding.

The cost base
The cost base is estimated using benefit caseload, expenditure forecasts and
official statistics from the DWP publication ‘Income-related benefits:
estimates of take-up’.

The tax base for the tax charge consists of all pensioners in England and
Wales with total income above £35,000 who are in receipt of the Winter Fuel
Payment. This is estimated using HMRC’s Personal Tax Model, based on
administrative data from the 2022–23 Survey of Personal Incomes. The tax
base is grown over the forecast horizon using the OBR’s forecast for growth
in pensioner incomes.

Costing
The costing is estimated by applying the pre- and post-measure benefit
regimes to the cost base described above and accounts for behavioural
responses of increased Winter Fuel Payment opt outs for those eligible for
the HMRC recovery.

Exchequer impact (£m)
                  2025-26    2026-27   2027-28     2028-29    2029-30    2030-31

 Exchequer
                  -1,785m    -1,390m    -910m      -1,330m    -1,340m    -1,325m
 impact


Areas of uncertainty
The main uncertainties in this costing relate to the size of the behavioural
response.


                                       84
Universal Credit: Changes to the standard
allowance and health element to protect existing
claimants and new health element claimants who
meet the Severe Conditions Criteria from April
2026
```

### [Budget 2025] Fuel Duty: Cancel uprating for 2026-27; extend the

```
Fuel Duty: Cancel uprating for 2026-27; extend the
5p cut in rates to 31 August 2026, then increase by
1p from 1 September 2026, 2p from 1 December
2026, and 2p from 1 March 2027
Measure description
This measure extends the temporary 5 pence per litre (ppl) cut in fuel duty,
which was first implemented on 23 March 2022, from 23 March 2026 to 31
August 2026 on rates for heavy oil (diesel and kerosene), unleaded petrol,
and light oil, with a proportionate percentage cut (equivalent to 5ppl from
the main fuel duty rate of 57.95ppl) in other lower rates and the rates for
rebated fuels where practical.

Rates will then gradually return to early 2022 levels in three stages: for main
rates, by 1p on 1 September 2026, 2p on 1 December 2026, and 2p on 1 March
2027, returning to 57.95 pence per litre at that point. The planned increase in
line with inflation for 2026/27 is also cancelled.

From 1 April 2027, fuel duty rates will be uprated annually in line with the
Retail Price Index.

This measure will be effective from 23 March 2026.

The tax base
The tax base is every litre of taxable fuel made available for use in the UK.
Projected volumes are taken from the fuel duty forecasting model.

Costing
The costing is calculated by taking the forecast baseline and applying the
difference in the forecast and policy duty rates.

The static costing is estimated by applying the pre- and post-measure tax
regimes to the tax base. Behavioural responses are accounted for by
measuring changes in consumption in response to changes in pump prices,
with separate elasticities for petrol and diesel reflecting short and long-run
effects.

Exchequer impact (£m)
                   2025-26   2026-27    2027-28    2028-29    2029-30    2030-31

Exchequer           -45m     -2,370m     -855m      -855m      -850m      -840m
impact



Areas of uncertainty
The main uncertainties in this costing relate to the size of the tax base and
the behavioural response.




                                       14
```

### [Budget 2025] Personal Tax: Maintain the personal income tax

```
Personal Tax: Maintain the personal income tax
and equivalent national insurance thresholds at
current levels for a further three years until April
2031
Measure description
This measure maintains the income tax Personal Allowance at £12,570 and
the higher rate threshold at £50,270; and the additional rate threshold at
£125,140, all from April 2028 to April 2031. The Personal Allowance threshold
applies UK-wide.

The higher rate threshold for non-savings, dividend and property income
and for property income will apply to taxpayers in England, Wales, and
Northern Ireland, and for savings and dividend income it will apply UK-wide.

This measure maintains the NICs Primary Threshold (PT) and Lower Profits
Limit (LPL) at £12,570 from April 2028 until April 2031. The NICs Upper
Earnings Limit (UEL) and Upper Profits Limit (UPL) will be maintained at
£50,270 from April 2028 to April 2031. The Upper Secondary Threshold and
Apprentices Upper Secondary Threshold will stay fixed at £50,270 per annum
until April 2031, to remain aligned with the UEL and UPL.

This measure will be implemented on 06 April 2028.

Tax base and data
The tax base is an estimate of the income in excess of the thresholds. This is
estimated using HMRCs Personal Tax Model. The costing reflects the
following data sources:

   •   The main source of data is from the 2022-23 Survey of Personal
       Incomes.

   •   The tax base is projected using the Office for Budget Responsibility
       (OBR) economic forecast.
The overall estimate of the tax base in 2028-29 is around £2 trillion of income.

Static costing
The static exchequer impact is calculated by applying the pre- and post-
measure tax regimes to the tax base described above. This results in the
following static costing:

Static Exchequer impact (£m)

              2025-26    2026-27    2027-28    2028-29    2029-30     2030-31

 Exchequer
              +0m        +0m        +0m        +3,325m     +7,650m    +11,890m
 impact


Post-behavioural costing
This costing builds in behavioural effects for individuals with income taxable
at the higher and additional rates of tax. Estimates of the behavioural effects
of the individuals outlined above are based on the Taxable Income
                                      40
Elasticities, which estimates how taxable income changes in response to
changes in tax rates. These behavioural effects reduce the static costing by
£180m (1.3%) in 2030-31.

The costing is also adjusted to reflected Tax Motivated Incorporations (TMIs)
as a result of this measure.

The OBR also expect workers to shift part of the incidence of the tax increase
onto employers, by bargaining for a higher nominal wage. The impact of this
on nominal wages and profits is captured in a behavioural adjustment to the
costing. More detail on the OBR’s assessment is set out in the EFO.

Post-behavioural Exchequer impact (£m)

                        2025-26         2026-27          2027-28          2028-29         2029-30          2030-31

 Exchequer
                        +0m             +0m              -25m             +3,365m         +7,780m +12,435m
 impact1


Areas of uncertainty
The main uncertainties in this costing surround CPI growth as well as the
size of the tax base towards the end of the costing period, and the
behavioural response.




1 A slightly higher yield from Personal Tax Threshold Freezes is presented in the OBR’s EFO due to an error identified in

  the calculation of the shift of some of the incidence of the tax increase being passed onto employers after the forecast
  had closed.

                                                            41
```

## Bonus diagnosis seed

The B2025 Table 4.1 scorecard row for the two-child limit carries HMT's poverty claim inside the verbatim
measure name: "Universal Credit Child Element: Remove the two child limit from April 2026, taking 450,000
children out of poverty" (line 6, Spend, −£2,365m in 2026-27). That 450,000-children figure is a
government poverty_count_change claim directly testable in PolicyEngine-UK (poverty metric + income
concept unstated in the scorecard itself — the DA documents define HMT's income concepts; DWP's
HBAI/absolute-vs-relative choice for the 450k is NOT stated here, flag concept_mismatch risk).
