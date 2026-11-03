# uk_rf_ab2026: Resolution Foundation, Autumn Budget 2026

**Working files.** `stage.py`, the file meant wherever these notes say `stage.py`, lives on branch `uk/ab2026-harvest-staging` at `harvest-staging/ab2026/lanes/rf/uk_rf_ab2026/stage.py`; this branch carries only NOTES.md, `manifest.jsonl` and `claims_staged.jsonl.gz`. The lane's local primaries folder (`.ab2026-primaries/uk_rf_ab2026/`, which the `--check-primaries` command below reads) was never committed: the repository carries no primary bytes, so fetch each primary from its `manifest.jsonl` URL and check its sha256.

Staged 2026-10-29 by `stage.py`, which holds every row as data and rewrites `claims_staged.jsonl.gz` byte for byte. Source slug `resolution_foundation`.

- **Rows:** 766 (767 before the review dropped row 397; see "Review fixes" at the end).
  - Text: 212 rows from the two press releases, the Spread thin page, both versions of the Spread thin PDF and one comment.
  - Workbook: 554 rows from the chart-data workbook RF links from the Spread thin page.
- **Primaries:** 7 (manifest.jsonl).
- **source_model:**
  - `landman_ttm`: the IPPR tax-benefit model behind RF's distributional and living-standards figures (488 rows).
  - `arithmetic`: RF's sums, averages and energy-bill construction on OBR, HMT and Ofgem inputs (148).
  - `survey_microdata`: LCF, NEED and HBAI analysis, including HBAI outturn years (42).
  - Restated rows carry the original engine: `obr_efo_forecast` (42), `hmt_costing_obr_certified` (38), `administrative_data` (5), `hm_government_publication` (3, Government figures that aren't Table 6.1 cells).

`python3 stage.py --check-primaries ../../../.ab2026-primaries/uk_rf_ab2026` re-hashes every primary against the manifest. It also finds every text quote in its document (pdftotext `-layout`, `-raw` and default modes for the PDFs) and compares all 759 embedded workbook cells with the sheet XML. On 2026-10-29 it reported 0 problems.

## Primaries and access recipe

Every primary came from `curl -sSL` with the Safari User-Agent, HTTP 200, with no blocks or challenges. A second fetch at 17:02Z returned identical bytes for all seven.

| primary | sha256 | bytes | fetched (UTC) | rows |
|---|---|--:|---|--:|
| Press release, 28 Oct: *Budget balancing act leaves families braced for tough winter…* | `ac5369e6…f98878` | 118,327 | 16:16:35 | 24 |
| Press release, 29 Oct: *Britain braced for painful second half of the Parliament* | `40b10268…c7c22d` | 116,817 | 16:16:36 | 19 |
| Spread thin publication page | `66a999dc…69d792` | 152,177 | 16:16:38 | 18 |
| Spread thin PDF, first version (`Spread-thin-1.pdf`) | `a669f39d…595603` | 1,410,169 | 16:16:41 | 3 |
| Spread thin PDF, replaced version (`Spread-thin.pdf`) | `9536b6cd…5d9ff` | 1,410,388 | 16:17:29 | 147 |
| Chart-data workbook (`Final-clean-charts-all-sections-for-comms.xlsx`) | `a4e1c072…6e0d1` | 14,637,565 | 16:17:32 | 555 |
| Comment, *It's good to be flexible* (Nye Cominetti, 29 Oct) | `3510a245…62fcfc` | 131,349 | 16:20:03 | 1 |

- **HTML pages:** the stager quotes each page's own article text. Locators count body paragraphs after the dateline (press releases and comment) or name the bullet list ("measures bullet 2", "Key findings bullet 3").
- **PDFs:** read with `pdftotext -layout`, and with `-raw` for the two-column boxes. Locators give the PDF page, which matches the printed folio, and the paragraph, bullet, box, footnote or figure label.
- **Workbook:** one sheet per figure (F1 to F23, plus "Extra spending stats").
  - `value_raw` is the cell's stored `<v>` string from the sheet XML, at full precision, not the rounded display: F8's `_-"£"* #,##0_-` shows 145.33 as £145.
  - The quote is "series label | category | stored value".
  - Locators are `sheet F8, cell J8`.
  - Each figure's plotted ranges come from the chart objects in the workbook. Figure 21 has no chart object; its column AD carries RF's own marker, "**USED IN CHART" (AD60).
- **Local copy:** the assignment's copy of `Spread-thin-1.pdf` (downloaded 08:46Z) hashes to the same `a669f39d…`, so v1 rows cite the fresh fetch.

## The replaced PDF (README rule 7)

RF replaced the briefing on the morning of 29 October.

- **v1, `Spread-thin-1.pdf`:** PDF CreationDate 04:33 EDT; server Last-Modified 08:37:45 GMT. The URL still serves it, but the landing page no longer links it.
- **v2, `Spread-thin.pdf`:** CreationDate 08:13 EDT; Last-Modified 12:14:43 GMT. The landing page links this version.
- **Text changes, from a page-by-page word diff:**
  - p.5: "the poorest half gain on average £158 … a paltry £14 more than the £144" became £145 / £15 / £130.
  - p.19: "(equivalent to an average £158 for poorer households, compared to £144 for richer households)" became "(equivalent to under £145 on average for poorer households, compared to over £130 for richer households – a gap of less than £15)".
  - Figure 8: the Council Tax rebate bars fall from about £100 to about £88 per household (vigintile 2); the other components are unchanged; the axis top moved accordingly, from +£180 / +3.6% to +£160 / +3.2%.
  - Figure 4: the x-axis gains 2031.
  - p.30: "restated the last Keir Starmer’s commitment" lost "the last".
  - Elsewhere the lines only reflow.
- **Which version rows cite:** v2 is the source for every PDF row except the three p.5 v1 rows (£158, £14, £144), which carry `conditions.document_version: "v1 (superseded)"`.
- **Workbook:** uploaded at 12:16:43 GMT, it matches v2. Its Figure 8 net gains average about £145 over vigintiles 2–10.
- **Landing page:** its Key findings still printed v1's "gains £158 on average, against £144 for the richer half" at both fetches. Those two rows carry `document_version: "page text at fetch time; matches Spread thin v1, not v2"`.

## Harvest rules 8 and 9

The coordinator added two rules to the AB2026 README during this family's staging, and `pipeline/ab2026_harvest_contract.py` now checks rule 9's rows. This family follows both:

- **Rule 8: stage estimates, not design.** A row is a number someone estimated, forecast or counted about the effect of a measure or of the Budget.
  - A measure's own parameters are design: rates, thresholds, payment amounts, dates and durations. So are spending allocations to programmes, financing remits and contingent liabilities.
  - Design goes in `reform_hint` or `conditions`, never as rows.
  - A worked example's inputs are design too; its computed outcome is a row.
- **Rule 9: a component of one measure keeps that measure's key.** The row carries `conditions.component` and `conditions.row_type: measure_component`. Proposed package keys are only for scopes that cross Table 6.1 lines, or have none.

"Not staged" below lists the 36 design rows rule 8 removed and where their facts went. The electricity VAT cut's "original" six months and three-month "extension" are parts of Table 6.1 line 2, so their 39 rows carry line 2's key as measure components.

## What the family stages

- **Text:** every number RF prints that estimates, forecasts or counts the effect of the Budget's measures or of the Budget as a whole. That covers costs and yields, households affected, gains and losses, bill changes, distributional and poverty effects, and the public finances after the Budget.
  - The text rows also include the living-standards and poverty projections and the energy-bill context the cost-of-living measures address, as `measure_key: null` context.
  - Within one document, a number printed twice with the same meaning gets one row, at the occurrence that states its period or scope most completely. For example, p.16 states the £2,192 cap level as Q1 2027, which p.5 calls "next year", so the row cites p.16.
  - Different documents' statements of the same figure are each staged (the AB2025 precedent; dedup belongs to the ingest).
- **Workbook:** the chart data behind figures of RF's own estimates.
  - F7 (energy bill and support by year).
  - F8 (temporary AB26 policies by vigintile).
  - F9 (LHA unfreeze and Your First Home by decile).
  - F10 (tax decisions and a continued Fuel Duty freeze by year).
  - F20 (permanent tax and benefit changes this Parliament by vigintile, including the four AB26 component columns the chart doesn't plot).
  - F21 (median non-pensioner income growth since 2023-24).
  - F22 (non-pensioner income growth by vigintile and year).
  - F23 (change in AHC poverty since 2023-24).
- **Structural zeros, not staged:**
  - F7 support components in years when the support didn't exist (for example the Energy Price Guarantee in 2019-20).
  - The 2023-24 zero base of F21 and F23.
  - F22's vigintile 1, a zero placeholder for the excluded bottom 5 per cent.
  - F8 and F20 leave vigintile 1 blank.

## Coverage tally

**Rows by workbook sheet:** F20 190, F8 114, F22 114, F10 54, F7 33, F9 26, F23 15, F21 8.

**Rows by measure_key:**

| measure_key | rows |
|---|--:|
| null (proposed key, or context) | 529 |
| `ab2026__package_household_energy_vat_and_fuel_duty` | 57 |
| `ab2026__electricity_vat_zero_rate_to_july_2027` | 42 (39 of them measure components) |
| `ab2026__household_energy_payment_100_bands_a_to_d` | 31 |
| `ab2026__fuel_duty_5p_cut_extended_and_rpi_rise_deferred` | 27 |
| `ab2026__pension_tax_allowance` | 21 |
| `ab2026__machine_games_duty_higher_stake_25pc` | 20 |
| `ab2026__your_first_home_equity_loan` | 16 |
| `ab2026__bank_surcharge_6pc_temporary` | 8 |
| `ab2026__writing_down_allowance_12pc_and_fya_50pc` | 6 |
| `ab2026__carers_allowance_earnings_taper` | 4 |
| `ab2026__business_rates_retention_mayoral_authorities` | 2 |
| `ab2026__package_total_policy_decisions` | 1 |
| `ab2026__founders_relief_cgt` | 1 |
| `ab2026__defence_investment_plan_further_savings` | 1 |

The 529 null rows split into 197 with a `proposed_measure_key` (listed below) and 332 context rows. The context rows cover fiscal aggregates, energy bill levels, living standards and poverty. They also include the three pre-AB26 component columns of F20 (57 rows: "pre-AB26 Direct tax changes", "pre-AB26 Benefit changes" and "pre-AB26 Indirect tax changes"), which score earlier events' measures.

## Conventions

- **Sign.** Each row's `conditions.sign_convention` states it, and no value is re-signed from what the primary prints or stores.
  - Household rows use "positive = gain to households". Text printed as a fall ("£2,000 lower", "fall by 3.0 per cent", "worse off by an average of £61") carries a negative value, as in AB2025.
  - Exchequer rows say "positive = cost" or "positive = yield", matching how RF writes the figure.
  - Figure 10 rows keep RF's plotted sign, positive = raises revenue. RF flipped the OBR's borrowing sign (workbook F10 I15, "Signs flipped from source").
  - F7 support components are negative, meaning a reduction in the typical bill, as stored.
- **Units.** £ values are in pounds (`gbp`), and `normalization` records the scaling, for example "£ billion × 1e9 → £".
  - Per cent figures are `percent`; shares and "one-in-five"-style fractions are `share`.
  - The stager multiplies workbook cells that store fractions (F8 K, F20 M, F21, F22) by 100 to give `percent`. F23 already stores percentage points.
- **Price basis:**
  - F8 and the package's halves figures: cash terms.
  - F7, F20 and the energy text: 2026-27 prices (Spread thin fn 13).
  - £ living-standards figures: 2026-27 prices, as printed.
  - `conditions.price_basis` records the basis on each row.
- **Period:**
  - Fiscal-year figures carry `fy` and the end year.
  - The temporary package (Figure 8, the 52/48 split, the halves' averages) covers 2026-27 and 2027-28 together. Those rows carry no `fy`, `period` 2028 and `conditions.horizon`.
  - Averages over a span (for example "£11 billion a year on average over the next five years") take the span's end year with `statistic: annual average`.
  - Calendar figures (the 2027 average bill, decade and Parliament RHDI growth) are `annual`; Q1-2027 cap levels and "currently" figures are `point_in_time`.
- **Value kinds.** RF prints point estimates throughout.
  - "under", "up to" and "less than" give `range_high`; "over" and "just over" give `range_low`.
  - Totals over several years and growth since a base year are `cumulative`.
- **Income groups.** `income_group` uses the AB2025 spellings `vigintile_N`, `decile_N`, `quintile_N`, `bottom_half` and `top_half`, the last two for RF's "poorer / richer half". The AB2025 NOTES flagged `bottom_half` / `top_half` for an ingest ruling.
- **Geography.**
  - F8 rows are "UK", with `modelling_geography` quoting RF's note (Council Tax and VAT cuts modelled for GB, Fuel Duty for the UK).
  - F9 and the Your First Home and LHA rows are England (Figure 9).
  - Energy bills are GB.
- **Baselines.**
  - F20's net and pre-AB26 columns, and the Parliament-wide text figures (99 rows), use `rf_start_of_parliament_policy` ("relative to the baseline inherited from Chancellor Hunt").
  - Every AB26 measure row is null: pre-Budget policy, current law at the scoring date. That includes F20's AB26 component columns, increments within RF's stack.
- **Attribution.**
  - `restated` (84 rows): HM Treasury Table 6.1 costings, OBR forecasts and the Government's count of carers. `note` names the original on each.
  - `own` (683): everything RF computes, including its sums and averages of official figures.
  - `benchmark_class` is `administrative_fact` for outturns and official counts (53 rows), including the 2024-25 HBAI outturn year in F21–F23, and `different_model` otherwise.
- **Worked examples (mode 3):** the computed outcomes only (rule 8).
  - The p.25 Pension Tax Allowance comparison: £34 Income Tax and £10 NICs for the worker, "nothing" for the pensioner. The £12,739 earnings input sits in `household_type`.
  - The Box 4 Carer's Allowance cliff edge: net income of £280, then £216 a week.
  - The NLW worker's £1,040 a year.

## Measure keys: how RF's scopes map to the registry

### Registered keys

- **`ab2026__package_household_energy_vat_and_fuel_duty` (Table 6.1 lines 1, 2 and 3).** This key covers RF's "cost of living package": Figure 8's net change and per cent change, the 52 / 48 per cent split, the halves' averages and gap, the £4.4bn costing and the landing page's £158 / £144.
  - RF's package is the Household Energy Payment, the electricity VAT cut ("original" six months plus the three-month "extension") and the Fuel Duty delay.
  - Table 6.1 line 2's title covers the whole cut ("from 1 October 2026 to 1 July 2027"), and its costs (£755m in 2026-27, £305m in 2027-28) include the original six months.
  - The registry's own modifier note gives the same reading: "about 57% of 2026-27 … about 22% of 2027-28". So RF's package equals lines 1, 2 and 3 exactly.
  - The £4.4bn rows also carry `costing_basis`: RF counts Fuel Duty at the share accruing directly to households (fn 19).
- **`ab2026__electricity_vat_zero_rate_to_july_2027` (line 2):**
  - **The whole cut:** the £40 "total nine-month benefit of the cut", and Figure 7's "Electricity VAT cut" series split by financial year (£26.77 in 2026-27, £12.80 in 2027-28).
  - **Measure components (rule 9, `row_type: measure_component`):** Figure 8's "Energy VAT cut (original)" (the six months to the end of Q1 2027, 19 vigintile rows), "Energy VAT cut extension" (April to 1 July 2027, 19 rows), and p.17's extension "worth £12". `conditions.component` and `measure_part` name the part. Never sum them with a whole-cut row.
- **`ab2026__household_energy_payment_100_bands_a_to_d`:** Figure 8's "Council Tax rebate", the eligibility shares and counts, and the £2.6bn cost. The £100 payment itself is design (rule 8).
- **`ab2026__fuel_duty_5p_cut_extended_and_rpi_rise_deferred`:** Figure 8's "Fuel Duty freeze extension", Figure 10's "Fuel Duty" series (equal to line 3), the "just under £1.4 billion" cost and the "around half" household incidence.
- **`ab2026__pension_tax_allowance`:** F20's "Pensioner Personal Allowance" (the workbook's label; the PDF says "Pension Tax Allowance"), the £150m cost and the pensioner who "will pay nothing".
- **`ab2026__machine_games_duty_higher_stake_25pc`:** F20's "Machine Games Levy" and "around £145 million per year … through Gambling Duties … well-targeted at machine gaming" (Table 6.1 line 56 prints £145m a year from 2029-30).
- **`ab2026__your_first_home_equity_loan`:** Figure 9's "Could access Your First Home", the 76 per cent top-half share, "up to 70,000 families" and the £95m.
- **`ab2026__carers_allowance_earnings_taper`:** the £80m, the 48,000 carers and the Box 4 cliff edge the taper removes.
- **Restated lines.** These are each exactly one Table 6.1 line, restated by RF:
  - Bank Surcharge (line 55): Figure 10 and "around £1.5 billion".
  - Writing-down allowances (line 58): Figure 10's "Capital allowances".
  - Founders' Relief (line 26): £300m.
  - Business Rates Retention (line 21): £10m and £140m.
  - Table 6.1 total policy decisions: £7.6bn in 2026-27.
  - Defence Investment Plan line 40: RF's "addition to pay for the DIP … £6.7 billion between 2026-27 and 2031-32" equals line 40's sum (-£6,670m). The row stays at medium confidence because line 40's title reads "Commitment to further savings made at announcement on 30 June 2026".

### Proposed keys

Each row below has `measure_key: null` and this key in `conditions.proposed_measure_key`. Every one crosses Table 6.1 lines or has none (rule 9).

| proposed key | rows | scope (Table 6.1 lines; RF's words) |
|---|--:|---|
| `ab2026__package_rf_parliament_permanent_tax_and_benefit_measures` | 42 | All permanent personal tax (direct and indirect) and benefit changes announced this Parliament, from the 2024 election to AB26 inclusive, against the policy inherited from Hunt. F20 "Net change in income" and "% change in income"; p.40 £320 / £2,000; p.41 0.9–2.2 per cent. Spans several events; AB26's part is lines 52, 56, 61, 62 and the gas standing charge. |
| `ab2026__gas_standing_charge_moved_to_unit_rates` | 31 | The announced abolition of the gas standing charge, "moving the £108 a year paid by the typical household onto unit rates by the end of 2027 or soon after". It costs the Exchequer nothing and has no Table 6.1 line. Covers p.18–19 (unit rates up around one-tenth; gainers and losers, by half and by children) and F20 "Remove standing charge on gas bills". The £108 sits in `reform_hint`. |
| `ab2026__package_property_and_savings_income_rates` | 25 | Table 6.1 lines 61 and 62 together: F10 "Savings & property" (their sum) and F20 "Property and savings tax rise". |
| `ab2026__package_rf_ab26_permanent_personal_measures` | 19 | F20 "AB26 Changes" = lines 52, 56, 61, 62 plus the gas standing charge (the workbook's column K equals columns F + G + I + J). |
| `ab2026_option__lha_unfreeze_2027_28` | 17 | Unfreezing Local Housing Allowance in 2027-28 instead of prolonging the freeze (no Table 6.1 line). Figure 9 "Would benefit if LHA were unfrozen"; "over a million families lose out, 91 per cent … in the bottom half". |
| `ab2026__package_tax_decisions_since_march_2026` | 13 | The OBR's Table 3.1 "Direct effect of tax measures" since March, sign flipped. F10 "Net direct effects", the p.23 labels, and p.4 "about £5 billion annually from next year". Differs from Table 6.1's tax total (-£1,749m vs -£1,645m in 2026-27). |
| `ab2026_option__tax_decisions_with_continued_fuel_duty_freeze` | 11 | The OBR's direct effect of tax measures plus keeping Fuel Duty at current rates: F10 "Net effect if Fuel Duty frozen" and its p.23 labels. |
| `ab2026__package_tax_administration_compliance_and_debt_collection` | 7 | The OBR's Table 3.1 group "Tax administration, compliance and debt collection measures" (it includes line 45 and timely payment for Self Assessment; RF doesn't list the lines). F10 row 52; p.4 "over £3 billion annually by 2030-31". |
| `ab2026_option__fuel_duty_continued_freeze` | 6 | Fuel Duty rates held at 52.95p a litre instead of rising to 60.59p in July 2027, relative to the announced policy: the OBR's constant-duty-rate alternative less its central forecast. F10 "… and if Fuel Duty frozen"; p.24 £4.3bn in 2029-30. |
| `ab2026__package_rf_other_tax_measures` | 6 | RF's residual in F10 "Other tax measures": OBR net direct effects less Fuel Duty, Bank Surcharge, capital allowances, savings and property, and tax administration. |
| `ab2026__package_household_energy_payment_and_electricity_vat` | 5 | Lines 1 and 2: "A £3.7 billion package of household support"; p.17 "£3.4 billion in 2026-27", "£0.3 billion in 2027-28", 45 per cent. The sums show line 2 is the whole cut; see the discrepancies below. |
| `ab2026__package_government_decisions_since_march_2026` | 3 | The OBR's total effect of the Budget's decisions on borrowing, direct and indirect, including decisions not on Table 6.1: "an average of £2 billion a year" (two documents); fn 47 "no overall impact". |
| `ab2026__package_rdel_decisions_excluding_household_energy_payment` | 3 | All the Budget's RDEL decisions over the Spending Review period except the Household Energy Payment: "£3 billion a year", "£9 billion top up" (two documents). A fiscal aggregate, not a programme allocation. |
| `ab2026__package_rf_absolute_policy_changes` | 2 | Every policy decision counted at absolute value (RF's fiscal-event size measure): "£7 billion". RF lists no lines. |
| `ab2026__package_rf_energy_bill_support_announced_at_budget` | 2 | "Support of up to £116 announced today" and "less than a fifth" of the 2027 bill rise. RF doesn't itemise the £116; it includes the £100 Household Energy Payment. |
| `ab2026_option__fuel_duty_rpi_uprating_since_2011` | 2 | Fuel Duty uprated by RPI since January 2011: "around £20 billion" a year (two documents). |
| `ab2026__minimum_wage_uprating_april_2027` | 2 | The April 2027 minimum wage rates the Chancellor confirmed (no Table 6.1 line): "worth £1,040 a year for someone working 40 hours a week" (PDF p.12 and the comment). The rates (3.9 per cent; £13.21; 50p) sit in `reform_hint`. |
| `ab2026__gas_supplier_levy_funded_from_general_taxation` | 1 | Funding the Gas Supplier Levy from general taxation: "save the typical household £7 in 2027-28" (fn 12). No Table 6.1 line found. |

## Proposed metrics

None of these is a registered Metric. Each row carries one as `proposed_metric`, reusing the AB2025 spelling where one exists: `forecast_borrowing_change`, `average_energy_bill_change`, `incidence_share`, `tax_to_gdp_ratio`, `real_spending_growth`, `spending_pressure` and `forecast_revenue_change`. The rest are new. Every unit is a registered UnitConcept.

- **Energy:**
  - `typical_energy_bill`: the typical household's annual bill level.
  - `average_energy_bill_change`: a change in it from prices or support combined, not from one policy. The registered `energy_bill_change` carries single-policy effects.
  - `unit_rate_change`.
  - `bill_rise_offset_share`.
- **Public finances:**
  - `debt_interest_spending`, `debt_interest_change`, `debt_interest_share_of_gdp`.
  - `current_budget_balance` (positive = deficit).
  - `primary_balance`, `primary_balance_change`.
  - `tax_revenue_change`.
  - `psnb_share_of_gdp`, `psnd_share_of_gdp`, `psni_share_of_gdp`.
  - `headroom_share_of_previous`, `share_of_headroom_change`.
  - `tax_to_gdp_ratio_change`.
  - `absolute_policy_change`.
  - `share_of_total_policy_cost`.
- **Spending:**
  - `rdel_change`.
  - `rdel_share_of_gdp`.
  - `real_rdel_per_person_change`.
  - `real_spending_change` (positive = size of a real cut).
  - `defence_spending_share_of_gdp`.
- **Households:**
  - `real_income_change` (£ change in a real income statistic).
  - `income_change_gap`.
  - `net_weekly_income`.
  - `annual_earnings_change`.

## Not staged, and why

- **Design, not estimates (rule 8; 36 rows removed after the rule arrived):**
  - **Fuel Duty rates:** PR28's "7.6p rise"; p.24's 52.95p to 60.59p a litre and "over 14 per cent". The rates sit in the continued-freeze option row's `conditions.counterfactual`.
  - **Minimum wage rates and counterfactual upratings:** 3.9 per cent, £13.21 and 50p (p.12 and the comment), the "on-course" 5.7 per cent and the youth rate's 10 per cent (Box 1 and the comment). The rates sit in the £1,040 rows' `reform_hint`.
  - **Financing remits:** NWF £15.4bn, BBB £5bn, the combined £20.4bn (PR28 and p.6), the 0.27 per cent of GDP of investment commitments, the £5bn defence ringfence and "around a quarter" (p.33).
  - **Programme allocations:**
    - The AI package's £700m, with £165m biosecurity, £120m AI Security Institute, £140m Sovereign AI Unit, £30m local partnerships and the £15m challenge prize.
    - Good Growth Funds' £285m in 2027-28.
    - The Social and Affordable Homes Programme's £1.5bn top-up and its 10,000 homes.
  - **The £108 gas standing charge:** it sits in the gas rows' `reform_hint`.
  - **A worked example's input:** the £12,739 part-time earnings, which sit in the worker rows' `household_type`.
  - **Figure 7's flat payments:** the Council Tax rebates (£100 in 2026-27, the 2022 £150) and the 2022-23 £400 Energy Bills Support Scheme, as F7 cells E7, L7 and L11.
  - **The 23 per cent rise in private rents since September 2023 (p.21):** an ONS statistic about no measure.
- **Charts without printed values.** The PDF's figures print no bar values except where staged: Figure 7's two 'After rebate' annotations (the two 'Net bill' labels are staged from p.17 bullet 2), Figure 10's eleven line labels and Figure 23's end labels. The exact values come from the workbook instead. Figure 5's decade labels for the 1960s–2010s are historical ONS outturn, not about the Budget; the text rows carry the 2020s values (1.4 per cent, £400).
- **Workbook sheets left out:**
  - These sheets chart OBR, ONS, IMF or HMT aggregates and history, or RF's arithmetic on them. This follows AB2025, which staged these charts' headline text values instead.
    - F1 (borrowing and debt, pre-measures).
    - F2 (borrowing decomposition).
    - F3 (gilt yields, debt interest).
    - F4 (CPI, earnings).
    - F5 (RHDI by decade).
    - F6 (GDP decomposition).
    - F11 (monthly real Fuel Duty rates, 2008–2032).
    - F13 (real RDEL per person decomposition).
    - F14 (spending growth by period).
    - F15 (departmental RDEL indices).
    - F16 (PSNB paths).
    - F17 (current balance and PSNFL).
    - F18 (current-balance forecast history).
    - F19 (international borrowing).
    - "Extra spending stats".
  - F12 holds marginal tax rates, which are design.
  - Within the staged sheets, the family leaves out:
    - Working and input blocks: F9's raw winner tables, F10's HMT and OBR input rows 5–40, F21's percentile columns other than AD, and F23's level, raw and scenario blocks.
    - F22's second chart (bottom 7 / middle 6 / top 7 vigintiles since 2019-20), which the briefing doesn't print.
- **Text numbers left out:**
  - **Macro forecasts and statistics:**
    - CPI paths (6.5 / 3.9 per cent, 43 / 22 per cent, 2.1 / 3.8 per cent, 16 / 13 per cent).
    - Gilt yields (44 basis points).
    - GDP growth (1.1 / 1.2 per cent, 1 per cent, 0.6 points, 0.5 per cent, 1.75 per cent).
    - Unemployment and earnings (5 per cent; 68 / 26 per cent; 3.8 per cent real earnings; 0.1 per cent real wages).
    - Migration levels (171,000; 331,000; 340,000 / 290,000 / 230,000; 70,000).
    - Wholesale gas and pump prices (60 per cent, a quarter, £2 a litre, a fifth, 22 / 14 per cent).
    - ONS business survey (15 per cent, 10 points).
    - Rents forecast to rise 3.6 per cent in 2027-28.
    - The OBR's 3.6 per cent Q2 2027 inflation.
    - ASHE's 5.9 per cent and the LPC's 3.7 per cent April estimate (Box 1 and comment).
    - The comment's 3.7 / 3.3 per cent earnings figures.
  - **History and international comparisons:**
    - Tax/GDP 37.2 per cent in 1948 and 4.6 points to 2019-20.
    - Receipts margins (6.3 / 3.5 per cent, fn 24).
    - Spending growth in earlier parliaments (1.8 / 1.4 / 3.6 per cent).
    - Unprotected departments' 4.6 per cent low (2018-19) and 7 per cent (2009-10).
    - Benefit and NI rates in past years (p.44).
    - Fuel Duty's 40 per cent real fall since 2011.
    - The EIB's 0.29 per cent of GDP.
    - The G7, OECD and IMF borrowing comparison (3 and 0.3 points).
    - The £72bn average of Reeves's two Budgets, which has no single period.
    - The 19th of 34 fiscal events (a rank).
  - **Other design:** £100, bands A-D, 5p, 3p / 2p, 2 points, 3 to 6 per cent, the 31 per cent headline bank rate, 20 / 25 per cent, the £1.5bn Good Growth lending facility, the 20 per cent equity loan and 2.5 per cent deposit, the £110,000 / £140,000 income caps, £86.45, £204, 16 hours, £1 for £1, the 55 per cent UC taper, Business Rates retention shares (20 / 50 / 70 / 100 per cent), and the 3 and 3.5 per cent defence targets.
  - **Third-party figures:**
    - Anthropic's $65bn (£48bn) round and the "1.5 per cent" comparison.
    - The Health Foundation's £7.5bn.
    - EDF's "top £2,000 in each quarter" (fn 9).
    - Arin Dube's 70 per cent bite.
  - **Ratios and qualitative multiples:**
    - "twice the level of funding given to households".
    - "twice the level of support" for a targeted scheme.
    - "one-tenth of the growth rate achieved in the 2010s".
    - "enough to cut employee National Insurance by 2p".
    - "help half as many poorer households twice as much".
    - "About half of that buffer was wiped out".
    - The "0.3 percentage point gap" (3.0 minus 2.7).
    - "35-year old property valuations".
  - **Other context:**
    - The 16 mayoral areas' £26bn (7 per cent of Income Tax).
    - "at least 28 MSAs".
    - 1.5 million homes.
    - 33GW / 300GW and £750bn of infrastructure.
    - "around half a million low-income families" (the AB2025 two-child limit repeal).
    - The £24bn year-four headroom (a rounding of £23.6bn).
    - p.15's "£7 billion in 2029-30" (a rounding of Box 2's £6.7bn).
- **Publications checked:**
  - RF's publications, press-release, comment, Top of the Charts, events and Budgets listings were all fetched at 16:19–16:20Z.
  - The only other RF Budget output from 28–29 October is the launch event page, *Pleasing people and satisfying markets*. It is an embedded YouTube video with no printed figures, so the family neither hashes nor stages it.
  - The comment's three slide images (`Slide1-1-scaled.png` to `Slide3-1-scaled.png`) are charts, not staged; its numbers are minimum-wage design apart from the £1,040.
  - No Budget response briefing, chart pack or Top of the Charts Budget special from 28–29 October appeared.
  - The Spread thin page's "Further reading" links two pre-Budget briefings, outside this window and not staged:
    - *Counting the cost* (8 Oct; page sha256 `415deda6…`).
    - *Hitting the buffers* (13 Oct; `881bbd4d…`).

## Discrepancies in the primaries (reported, not fixed)

1. **v1 and v2 disagree on the income halves.** v1 prints £158 / £14 / £144; v2 prints £145 / £15 / £130, and v2 p.19 hedges them as "under £145 … over £130 … less than £15". The landing page still printed £158 / £144 when fetched.
2. **The £4.4bn package's years.** p.19 calls it "the Government’s £4.4 billion cost of living package for 2025-26 and 2026-27". The measures fall in 2026-27 and 2027-28 (Table 6.1 lines 1–3). The press release and p.47 print no years. The family stages the period as printed, at medium confidence.
3. **The £3.4bn's scope.** p.17 says "Together, these measures cost £3.4 billion in 2026-27" of the Household Energy Payment and "a three-month extension to the VAT cut". The extension falls in 2027-28, and £3.4bn equals lines 1 and 2 in 2026-27 (£2,625m + £755m), so the figure includes the original six months of the VAT cut.
4. **Your First Home's sign.** p.21 calls £95m in 2029-30 "a cost". Table 6.1 line 37 prints +95, a yield ("net income from developer fees").
5. **SAHP top-up** (not staged, rule 8). p.21's "£1.5 billion top-up" differs from Table 6.1 line 35, which sums to £1,750m over 2027-28 to 2030-31.
6. **Good Growth Funds** (not staged, rule 8). p.33's "£285 million in 2027-28" differs from line 20, which prints -£340m that year (the line includes the lending subsidy).
7. **Tax gap measures.** p.4's "over £3 billion annually by 2030-31" doesn't match the workbook's OBR series (F10 row 52): 2.89 in 2030-31 and 3.64 in 2031-32.
8. **Figure 20's AB26 component.** The note says "‘AB26 Changes’ includes the Pension Tax Allowance, removal of standing charges on gas bills, and the Machine Games Levy". The workbook's AB26 Changes also includes "Property and savings tax rise" (column K = F + G + I + J). The workbook labels the Pension Tax Allowance "Pensioner Personal Allowance".
9. **Figure 10's Fuel Duty series.** Its note says the series shows "Fuel Duty changes announced in May and October", but the values (-0.575, -0.78) equal Table 6.1 line 3 alone.
10. **Primary balance years.** p.39 says the £107bn of higher tax revenues runs to the end of the Parliament (2028-29). Footnote 53 computes it "between 2023-24 and 2029-30, multiplied by forecasted GDP in 2029-30".
11. **Energy bill figures, release vs briefing:**
    - The 28 October release's "£2,210 across 2027" (the 2027 average) differs from Spread thin's £2,192 (the Q1 2027 cap), which p.5 calls the bill "next year".
    - The 29 October release's 2022-23 net bill of £1,685 differs from Figure 7's "After rebate: £1,686" (workbook 1,686.20).
    - p.17's VAT extension "worth £12" differs from the workbook's 12.80 for the cut in 2027-28 (2026-27 prices).
12. **Footnote 50's figure reference.** It reads "From the forecasts shown in Figure 7", but the current-balance forecasts appear in Figure 18; Figure 7 is the energy bill chart.
13. **Capacity vs Table 6.2** (not staged, rule 8). The NWF's £15.4bn and BBB's £5bn "capacity" boosts don't match Table 6.2's financial transactions: NWF line 2 sums to £10.2bn over 2028-29 to 2031-32, BBB line 3 to £0.75bn.
14. *(Withdrawn on 3 November: the README's rule 3 example was corrected, so RF's package equals the registered one; see "Measure keys".)*
15. **The VAT element's description.** PR28 para 5 and p.17 bullet 2 describe the package's VAT element as the "three-month extension", and p.17 calls the six-month cut "support announced before this Budget". Yet Figure 8, the 52/48 split and the £4.4bn all include "Energy VAT cut (original)".

## Review fixes, 3 November 2026

The RF review (`harvest-staging/ab2026/reviews/verify-rf.md` on the staging branch) approved this family with fixes; all thirteen are applied, finding 1 as the `P_SAV_PROP` constant and the rest in an explicit block before `write()` in `stage.py`. No primary was re-opened (the session's network policy refused resolutionfoundation.org); no printed value changed.

1. The 25 rows for exactly lines 61 and 62 use `ab2026__package_property_and_savings_income_rates`, README rule 2's name (F10 row 51 equals lines 61 + 62 in every year).
2. The passage and discrepancy 14 that contradicted README rule 3's old example are gone; that example has been corrected.
3. Row 168's note names the Government's Defence Investment Plan projection.
4. Row 38's note names the ONS/OBR outturn.
5. The v1→v2 record notes Figure 8's lower Council Tax rebate bars.
6. "Figure 7's four annotations" now reads two, with the two "Net bill" labels staged from p.17.
7. The workbook hash typo is fixed.
8. Row 23 (−0.4 per cent) is a `point`, `statistic: RHDI per person, average annual growth`, `parse_confidence: medium`.
9. Row 167 (0.5 per cent) is `statistic: real RDEL per person, average annual change (Figure 14)`.
10. Rows 28, 29, 56, 57, 61 and 63 carry `price_basis: cash terms (Figure 8)`.
11. (Optional, applied.) Row 397, F10 C48's floating-point zero (−7.46e-7 bn), is dropped: F10 54 rows, `ab2026_option__fuel_duty_continued_freeze` 6, `arithmetic` 148, total 766.
12. (Optional, applied; England, the coordinator's call.) Rows 109 and 110 (£358 and 20 per cent) are `geography: England`, as row 108 is.
13. Discrepancy 15 records the VAT element's description.

- **Verification:** the contract checker reports 766 rows, 0 problems, and a re-run of `stage.py` reproduces the gzip byte for byte. COUNTS.json pins its sha256. Proposed-key names may change again in the cross-family harmonisation recorded below.

## Key harmonisation, 3 November 2026

The coordinator gave each scope one key across families (tranche 1, task 3.4). This family's renames:

- `ab2026__minimum_wage_rates_april_2027` → `ab2026__minimum_wage_uprating_april_2027`
- `ab2026__package_obr_total_effect_of_government_decisions` → `ab2026__package_government_decisions_since_march_2026`
- `ab2026__package_obr_direct_effect_of_tax_measures` → `ab2026__package_tax_decisions_since_march_2026`
- `ab2026__package_obr_tax_administration_compliance_and_debt_collection` → `ab2026__package_tax_administration_compliance_and_debt_collection`
- `ab2026_option__obr_tax_measures_with_continued_fuel_duty_freeze` → `ab2026_option__tax_decisions_with_continued_fuel_duty_freeze`

RF's three OBR groupings are restatements of the OBR's own Table 3.1 rows, so they take the OBR family's scope names, which carry no `obr` (OBR review, finding 9). The minimum wage key takes the red book's spelling for the same measure. `ab2026_option__fuel_duty_continued_freeze` is now shared with the OBR family, whose paragraph 3.43 prints the same alternative's £4.3bn in 2029-30.
