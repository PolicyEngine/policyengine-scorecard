# uk_rf_ab2026: Resolution Foundation, Autumn Budget 2026

We keep `stage.py` on branch `uk/ab2026-harvest-staging` at `harvest-staging/ab2026/lanes/rf/uk_rf_ab2026/stage.py`. We commit only NOTES.md, `manifest.jsonl` and `claims_staged.jsonl.gz` to this branch, and the repository holds no primary bytes. The lane never committed its local primaries folder (`.ab2026-primaries/uk_rf_ab2026/`, which the `--check-primaries` command below reads), so fetch each primary from its `manifest.jsonl` URL and check its sha256.

We staged this family on 2026-10-29 with `stage.py`. We wrote every row into it as data, and it rewrites `claims_staged.jsonl.gz` byte for byte. We use source slug `resolution_foundation`.

- Rows: 766 (767 before we dropped row 397 after review; see "Review fixes" at the end).
  - Text: 212 rows from the two press releases, the Spread thin page, both versions of the Spread thin PDF and one comment.
  - Workbook: 554 rows from the chart-data workbook RF links from the Spread thin page.
- Primaries: 8 (manifest.jsonl): the seven the lane fetched, plus the Spread thin page's 4 November version, which no row cites (README rule 7; see "The replaced PDF").
- source_model:
  - `landman_ttm`: the IPPR tax-benefit model behind RF's distributional and living-standards figures (488 rows).
  - `arithmetic`: RF's sums, averages and energy-bill construction on OBR, HMT and Ofgem inputs (148).
  - `survey_microdata`: LCF, NEED and HBAI analysis, including HBAI outturn years (42).
  - On restated rows we name the original engine: `obr_efo_forecast` (42), `hmt_costing_obr_certified` (38), `hm_government_publication` (5, Government figures that aren't Table 6.1 cells, including HM Treasury's Household Energy Payment count) and `administrative_data` (1, row 38's outturn). We also mark two own rows `administrative_data` (official counts RF computes from).

`python3 stage.py --check-primaries ../../../.ab2026-primaries/uk_rf_ab2026` re-hashes every primary against the manifest. It also finds every text quote in its document (pdftotext `-layout`, `-raw` and default modes for the PDFs) and compares all 759 embedded workbook cells with the sheet XML. On 2026-10-29 it reported 0 problems.

## Primaries and access recipe

The lane fetched every primary with `curl -sSL` and the Safari User-Agent, and got HTTP 200 with no blocks or challenges. A second fetch at 17:02Z returned identical bytes for all seven. RF's server embeds per-request content in the HTML pages (rotating nonces, tokens and related-article lists), so a later fetch's sha256 can't reproduce the manifest's. For those pages, check instead that every staged quote still appears on the page, as review B did on 4 November.

| primary | sha256 | bytes | fetched (UTC) | rows |
|---|---|--:|---|--:|
| Press release, 28 Oct: *Budget balancing act leaves families braced for tough winter…* | `ac5369e6…f98878` | 118,327 | 16:16:35 | 24 |
| Press release, 29 Oct: *Britain braced for painful second half of the Parliament* | `40b10268…c7c22d` | 116,817 | 16:16:36 | 19 |
| Spread thin publication page | `66a999dc…69d792` | 152,177 | 16:16:38 | 18 |
| Spread thin PDF, first version (`Spread-thin-1.pdf`) | `a669f39d…595603` | 1,410,169 | 16:16:41 | 3 |
| Spread thin PDF, replaced version (`Spread-thin.pdf`) | `9536b6cd…5d9ff` | 1,410,388 | 16:17:29 | 147 |
| Chart-data workbook (`Final-clean-charts-all-sections-for-comms.xlsx`) | `a4e1c072…6e0d1` | 14,637,565 | 16:17:32 | 554 |
| Comment, *It's good to be flexible* (Nye Cominetti, 29 Oct) | `3510a245…62fcfc` | 131,349 | 16:20:03 | 1 |
| Spread thin publication page, 4 November version (review B's fetch) | `d81969ef…0b0259` | 154,801 | 4 Nov | 0 |

- **HTML pages.** The stager quotes each page's own article text. Our locators count body paragraphs after the dateline (press releases and comment) or name the bullet list ("measures bullet 2", "Key findings bullet 3").
- **PDFs.** We read them with `pdftotext -layout`, and with `-raw` for the two-column boxes. Our locators give the PDF page, which matches the printed folio, and the paragraph, bullet, box, footnote or figure label.
- **Workbook.** RF gives one sheet per figure (F1 to F23, plus "Extra spending stats").
  - For `value_raw` we take the cell's stored `<v>` string from the sheet XML, at full precision, not the rounded display: F8's `_-"£"* #,##0_-` shows 145.33 as £145.
  - We write the quote as "series label | category | stored value".
  - We write locators as `sheet F8, cell J8`.
  - We take each figure's plotted ranges from the chart objects in the workbook. RF draws Figure 21 from chart object `chart34.xml` (grouped, plotting AD66:AD74), and marks column AD with its own "**USED IN CHART" (AD60). We stage Figure 8's column J (the net change), though RF's chart doesn't plot it.
  - We name each chart row's series in `conditions.series`. We add `conditions.component` only on the rule 9 parts (Figure 8's two VAT-cut columns and p.17's extension).
- **Local copy.** The assignment's copy of `Spread-thin-1.pdf` (downloaded 08:46Z) hashes to the same `a669f39d…`, so v1 rows cite the fresh fetch.

## The replaced PDF (README rule 7)

RF replaced the briefing on the morning of 29 October.

- **v1, `Spread-thin-1.pdf`:** PDF CreationDate 04:33 EDT; server Last-Modified 08:37:45 GMT. RF still serves it at the URL, but its landing page no longer links it.
- **v2, `Spread-thin.pdf`:** CreationDate 08:13 EDT; Last-Modified 12:14:43 GMT. RF's landing page links this version.
- **Text changes, from our page-by-page word diff:**
  - p.5: RF changed "the poorest half gain on average £158 … a paltry £14 more than the £144" to £145 / £15 / £130.
  - p.19: RF changed "(equivalent to an average £158 for poorer households, compared to £144 for richer households)" to "(equivalent to under £145 on average for poorer households, compared to over £130 for richer households – a gap of less than £15)".
  - Figure 8: RF lowered the Council Tax rebate bars from about £100 to about £88 per household (vigintile 2) and left the other components unchanged. It moved the axis top accordingly, from +£180 / +3.6% to +£160 / +3.2%.
  - Figure 4: RF added 2031 to the x-axis.
  - p.30: RF dropped "the last" from "restated the last Keir Starmer’s commitment".
  - Elsewhere the lines only reflow.
- **Which version rows cite.** We cite v2 for every PDF row except the three p.5 v1 rows (£158, £14, £144), on which we set `conditions.document_version: "v1 (superseded)"`.
- **Workbook.** RF uploaded it at 12:16:43 GMT, and it matches v2. Its Figure 8 net gains average about £145 over vigintiles 2–10.
- **Landing page.** In Key findings RF still printed v1's "gains £158 on average, against £144 for the richer half" at both 29 October fetches. Those two rows (56–57) cite the 29 October bytes, and we set `document_version: "29 October page text (superseded by 4 November)"` on them.
- **RF changed the landing page by 4 November.** Review B's 4 November fetch (sha256 `d81969ef…0b0259`, 154,801 bytes, JSON-LD `dateModified` 2026-11-04T09:21:48Z) shows v2's £145 / £130 in Key findings bullet 3. We record it as manifest line 8 (README rule 7), with no rows: v2 rows 74 and 76 already give £145 / £130, so we don't stage them again. RF's `dateModified` (09:21Z on 4 November) shows only that RF had made the edit by then.

## Harvest rules 8 and 9

The coordinator added two rules to the AB2026 README while we staged this family, and `pipeline/ab2026_harvest_contract.py` now checks rule 9's rows. We follow both:

- **Rule 8: stage estimates, not design.** We stage as a row only a number someone estimated, forecast or counted about the effect of a measure or of the Budget.
  - Under rule 8 we treat a measure's own parameters as design: rates, thresholds, payment amounts, dates and durations. We treat spending allocations to programmes, financing remits and contingent liabilities the same way.
  - We put design in `reform_hint` or `conditions`, never in rows.
  - We treat a worked example's inputs as design too, and stage its computed outcome as a row.
- **Rule 9: a component of one measure keeps that measure's key.** We give the row `conditions.component` and `conditions.row_type: measure_component`. We proposed keys only for scopes that cross Table 6.1 lines or have no line.

Under "Not staged" below we list the 36 design rows we removed under rule 8 and where their facts went. RF splits the electricity VAT cut into an "original" six months and a three-month "extension", both parts of Table 6.1 line 2, so we key their 39 rows to line 2 as measure components.

## What we stage

- **Text.** We stage every number RF prints that estimates, forecasts or counts the effect of the Budget's measures or of the Budget as a whole. That covers costs and yields, households affected, gains and losses, bill changes, distributional and poverty effects, and the public finances after the Budget.
  - We also stage, as `measure_key: null` context, the living-standards and poverty projections and the energy-bill context that the cost-of-living measures address.
  - Where RF prints a number twice with the same meaning in one document, we stage one row, at the occurrence that states its period or scope most completely. For example, RF dates the £2,192 cap level Q1 2027 on p.16 and calls it "next year" on p.5, so the row cites p.16.
  - Where different documents state the same figure, we stage each (the AB2025 precedent). At ingest we merge rows 26, 27, 60, 132 and 201 into the claim of another printing of the same RF figure.
- **Workbook.** We stage the chart data behind the figures that give RF's own estimates.
  - F7 (energy bill and support by year).
  - F8 (temporary AB26 policies by vigintile).
  - F9 (LHA unfreeze and Your First Home by decile).
  - F10 (tax decisions and a continued Fuel Duty freeze by year).
  - F20 (permanent tax and benefit changes this Parliament by vigintile, including the four AB26 component columns the chart doesn't plot).
  - F21 (median non-pensioner income growth since 2023-24).
  - F22 (non-pensioner income growth by vigintile and year).
  - F23 (change in AHC poverty since 2023-24).
- **Structural zeros, which we didn't stage:**
  - F7 support components in years when the support didn't exist (for example the Energy Price Guarantee in 2019-20).
  - The 2023-24 zero base of F21 and F23.
  - F22's vigintile 1, a zero placeholder for the excluded bottom 5 per cent.
  - In F8 and F20 RF leaves vigintile 1 blank.

## Coverage tally

**Rows by workbook sheet:** F20 190, F8 114, F22 114, F10 54, F7 33, F9 26, F23 15, F21 8.

**Rows by measure_key:**

| measure_key | rows |
|---|--:|
| null (context) | 332 |
| the 19 keys we proposed (below) | 200 |
| `ab2026__package_household_energy_vat_and_fuel_duty` | 54 |
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

We key 200 rows to the 19 keys below, which we proposed and registered in tranche 2, and stage 332 as context. As context we stage fiscal aggregates, energy bill levels, living standards and poverty. We also stage as context F20's three pre-AB26 component columns (57 rows: "pre-AB26 Direct tax changes", "pre-AB26 Benefit changes" and "pre-AB26 Indirect tax changes"), in which RF scores earlier events' measures.

## Conventions

- **Sign.** We state the convention in each change row's `conditions.sign_convention`, and we re-signed no value from what RF prints or stores. We give Figures 21 and 22 "positive = growth", the text growth rows and row 117 "positive = gain to households", and row 10 "positive = saving (a reduction in the household's bills)".
  - We give household rows "positive = gain to households". Where RF prints a fall ("£2,000 lower", "fall by 3.0 per cent", "worse off by an average of £61"), we stage a negative value, as in AB2025.
  - On Exchequer rows we say "positive = cost" or "positive = yield", matching how RF writes the figure.
  - On Figure 10 rows we keep RF's plotted sign, positive = raises revenue. RF flipped the OBR's borrowing sign (workbook F10 I15, "Signs flipped from source").
  - We keep F7 support components negative, as RF stores them, for a reduction in the typical bill.
- **Units.** We give £ values in pounds (`gbp`), and record the scaling in `normalization`, for example "£ billion × 1e9 → £".
  - We give per cent figures as `percent`, and shares and "one-in-five"-style fractions as `share`.
  - The stager multiplies workbook cells that store fractions (F8 K, F20 M, F21, F22) by 100 to give `percent`. RF already stores percentage points in F23.
- **Price basis:**
  - F8 and the package's halves figures: cash terms.
  - F7, F20 and the energy text: 2026-27 prices (Spread thin fn 13).
  - £ living-standards figures: 2026-27 prices, as printed.
  - We record the basis on each row in `conditions.price_basis`.
- **Period:**
  - We give fiscal-year figures `fy` and the end year.
  - RF's temporary package (Figure 8, the 52/48 split, the halves' averages and gap, and the £4.4bn) covers 2026-27 and 2027-28 together. We give those rows no `fy`, `period` 2028 (the £4.4bn rows: 2027, which RF prints on p.19 as "2025-26 and 2026-27" for row 127 and which we read from p.19 for rows 34 and 54), `time_basis: fiscal_year` and `conditions.horizon`. In Figure 8 RF shows each measure's "total cash impact" over the two years (v2 p.20; workbook F8 N35). So we mark its rows, and the text figures that restate it, `cumulative`. For the F8 £ columns, our normalization reads "£ per household as stored: total cash impact over 2026-27 and 2027-28 (Figure 8 note)".
  - RF prints no year for the gas standing-charge rows (115–125), so we give them no `fy`. We put them at period 2028 with `conditions.horizon` "year not printed: the change lands by the end of 2027 or soon after (p.18)", at medium confidence.
  - For averages over a span (for example "£11 billion a year on average over the next five years"), we use the span's end year with `statistic: annual average`.
  - We mark calendar figures (the 2027 average bill, decade and Parliament RHDI growth) `annual`, and Q1-2027 cap levels and "currently" figures `point_in_time`.
- **Value kinds.** RF prints point estimates throughout.
  - We read "under", "up to" and "less than" as `range_high`, and "over" and "just over" as `range_low`.
  - We mark totals over several years and growth since a base year `cumulative`: 195 rows, including Figure 8's 114 and the 11 text rows that restate Figure 8 or the £4.4bn.
- **Income groups.** In `income_group` we use the AB2025 spellings `vigintile_N`, `decile_N`, `quintile_N`, `bottom_half` and `top_half`, the last two for RF's "poorer / richer half". In the AB2025 NOTES we flagged `bottom_half` / `top_half` for an ingest ruling.
- **Geography.**
  - We set F8 rows to "UK", with `modelling_geography` quoting RF's note (Council Tax and VAT cuts modelled for GB, Fuel Duty for the UK).
  - We set F9 and the Your First Home and LHA rows to England (Figure 9).
  - We set energy bills to GB.
- **Baselines.**
  - For F20's net and pre-AB26 columns, and the Parliament-wide text figures (99 rows), we use `rf_start_of_parliament_policy` ("relative to the baseline inherited from Chancellor Hunt").
  - We leave the baseline null on every AB26 measure row: pre-Budget policy, current law at the scoring date. That includes F20's AB26 component columns, increments within RF's stack.
- **Attribution.**
  - `restated` (86 rows): HM Treasury Table 6.1 costings, OBR forecasts, the Government's count of carers and HM Treasury's count of Household Energy Payment households (rows 55 and 72, which RF repeats uncited). We name the original in `note` on each.
  - `own` (680): everything RF computes, including its sums and averages of official figures.
  - We set `benchmark_class` to `administrative_fact` for outturns and official counts (53 rows), including the 2024-25 HBAI outturn year in F21–F23, and `different_model` otherwise.
- **Worked examples (mode 3).** We stage the computed outcomes only (rule 8).
  - The p.25 Pension Tax Allowance comparison: £34 Income Tax and £10 NICs for the worker, "nothing" for the pensioner. We put the £12,739 earnings input in `household_type`.
  - The Box 4 Carer's Allowance cliff edge: net income of £280, then £216 a week.
  - The NLW worker's £1,040 a year.

## Measure keys: how RF's scopes map to the registry

### Registered keys

- **`ab2026__package_household_energy_vat_and_fuel_duty` (Table 6.1 lines 1, 2 and 3).** We key RF's "cost of living package" here. That covers Figure 8's net change and per cent change, the 52 / 48 per cent split, the halves' averages and gap, and the landing page's £158 / £144. We moved the £4.4bn costing off it (review A, K-4; see the keys we proposed).
  - RF's package comprises the Household Energy Payment, the electricity VAT cut ("original" six months plus the three-month "extension") and the Fuel Duty delay.
  - HM Treasury's title for Table 6.1 line 2 covers the whole cut ("from 1 October 2026 to 1 July 2027"), and its costs (£755m in 2026-27, £305m in 2027-28) include the original six months.
  - The registry's own modifier note reads the line the same way: "about 57% of 2026-27 … about 22% of 2027-28". So RF's package equals lines 1, 2 and 3 exactly.
  - In the £4.4bn rows (34, 54, 127) RF counts Fuel Duty only at the share accruing directly to households (fn 19, `costing_basis`). Their scope therefore differs from lines 1–3 (rule 3), and we key them to `ab2026__package_household_energy_vat_and_household_share_of_fuel_duty`.
- **`ab2026__electricity_vat_zero_rate_to_july_2027` (line 2):**
  - **The whole cut:** the £40 "total nine-month benefit of the cut", and Figure 7's "Electricity VAT cut" series split by financial year (£26.77 in 2026-27, £12.80 in 2027-28).
  - **Measure components (rule 9, `row_type: measure_component`):** Figure 8's "Energy VAT cut (original)" (the six months to the end of Q1 2027, 19 vigintile rows), "Energy VAT cut extension" (April to 1 July 2027, 19 rows), and p.17's extension "worth £12". We name the part in `conditions.component` and `measure_part`. Never sum them with a whole-cut row.
- **`ab2026__household_energy_payment_100_bands_a_to_d`:** Figure 8's "Council Tax rebate", the eligibility shares and counts, and the £2.6bn cost. We treat the £100 payment itself as design (rule 8).
- **`ab2026__fuel_duty_5p_cut_extended_and_rpi_rise_deferred`:** Figure 8's "Fuel Duty freeze extension", Figure 10's "Fuel Duty" series (equal to line 3), the "just under £1.4 billion" cost and the "around half" household incidence.
- **`ab2026__pension_tax_allowance`:** F20's "Pensioner Personal Allowance" (RF's workbook label; in the PDF RF writes "Pension Tax Allowance"), the £150m cost and the pensioner who "will pay nothing".
- **`ab2026__machine_games_duty_higher_stake_25pc`:** F20's "Machine Games Levy" and "around £145 million per year … through Gambling Duties … well-targeted at machine gaming" (Table 6.1 line 56 prints £145m a year from 2029-30).
- **`ab2026__your_first_home_equity_loan`:** Figure 9's "Could access Your First Home", the 76 per cent top-half share, "up to 70,000 families" and the £95m.
- **`ab2026__carers_allowance_earnings_taper`:** the £80m, the 48,000 carers and the Box 4 cliff edge the taper removes.
- **Restated lines.** In each of these RF restates exactly one Table 6.1 line:
  - Bank Surcharge (line 55): Figure 10 and "around £1.5 billion".
  - Writing-down allowances (line 58): Figure 10's "Capital allowances".
  - Founders' Relief (line 26): £300m.
  - Business Rates Retention (line 21): £10m and £140m.
  - Table 6.1 total policy decisions: £7.6bn in 2026-27.
  - Defence Investment Plan line 40: RF's "addition to pay for the DIP … £6.7 billion between 2026-27 and 2031-32" equals line 40's sum (-£6,670m). We keep the row at medium confidence because HM Treasury titles line 40 "Commitment to further savings made at announcement on 30 June 2026".

### Keys we proposed

We gave each row below `measure_key: null` and its key in `conditions.proposed_measure_key`, and in tranche 2 we registered the keys and moved them into `measure_key`. Every one crosses Table 6.1 lines or has none (rule 9).

| key | rows | scope (Table 6.1 lines; RF's words) |
|---|--:|---|
| `ab2026__package_rf_parliament_permanent_tax_and_benefit_measures` | 42 | All permanent personal tax (direct and indirect) and benefit changes announced this Parliament, from the 2024 election to AB26 inclusive, against the policy inherited from Hunt. F20 "Net change in income" and "% change in income"; p.40 £320 / £2,000; p.41 0.9–2.2 per cent. Spans several events; AB26's part is lines 52, 56, 61, 62 and the gas standing charge. |
| `ab2026__gas_standing_charge_moved_to_unit_rates` | 31 | The announced abolition of the gas standing charge, "moving the £108 a year paid by the typical household onto unit rates by the end of 2027 or soon after". It costs the Exchequer nothing and has no Table 6.1 line. Covers p.18–19 (unit rates up around one-tenth; gainers and losers, by half and by children) and F20 "Remove standing charge on gas bills". We keep the £108 in `reform_hint`. |
| `ab2026__package_property_and_savings_income_rates` | 25 | Table 6.1 lines 61 and 62 together: F10 "Savings & property" (their sum) and F20 "Property and savings tax rise". |
| `ab2026__package_rf_ab26_permanent_personal_measures` | 19 | F20 "AB26 Changes" = lines 52, 56, 61, 62 plus the gas standing charge (the workbook's column K equals columns F + G + I + J). |
| `ab2026_option__lha_unfreeze_2027_28` | 17 | Unfreezing Local Housing Allowance in 2027-28 instead of prolonging the freeze (no Table 6.1 line). Figure 9 "Would benefit if LHA were unfrozen"; "over a million families lose out, 91 per cent … in the bottom half". |
| `ab2026__package_tax_decisions_since_march_2026` | 13 | The OBR's Table 3.1 "Direct effect of tax measures" since March, sign flipped. F10 "Net direct effects", the p.23 labels, and p.4 "about £5 billion annually from next year". Differs from Table 6.1's tax total (-£1,749m vs -£1,645m in 2026-27). |
| `ab2026_option__tax_decisions_with_continued_fuel_duty_freeze` | 11 | The OBR's direct effect of tax measures plus keeping Fuel Duty at current rates: F10 "Net effect if Fuel Duty frozen" and its p.23 labels. On `revenue_change` (README rule 10; see "README rule 10" below). |
| `ab2026__package_tax_administration_compliance_and_debt_collection_receipts` | 7 | The OBR's Table 3.1 group "Tax administration, compliance and debt collection measures", which covers the receipts of Table 6.1 lines 45 and 46 (OBR review B, finding 3; it includes timely payment for Self Assessment; RF doesn't list the lines). F10 row 52; p.4 "over £3 billion annually by 2030-31". |
| `ab2026_option__fuel_duty_continued_freeze` | 6 | Fuel Duty rates held at 52.95p a litre instead of rising to 60.59p in July 2027, relative to the announced policy: the OBR's constant-duty-rate alternative less its central forecast. F10 "… and if Fuel Duty frozen"; p.24 £4.3bn in 2029-30. A receipts cost, on `revenue_change`. At ingest we drop these rows as restatements of the OBR's forecast and keep the OBR family's £4.3bn (paragraph 3.43, row 2740), which we move from `decisions_effect_on_borrowing` to `revenue_change`. |
| `ab2026__package_rf_other_tax_measures` | 6 | RF's residual in F10 "Other tax measures": OBR net direct effects less Fuel Duty, Bank Surcharge, capital allowances, savings and property, and tax administration. |
| `ab2026__package_household_energy_vat_and_household_share_of_fuel_duty` | 3 | Table 6.1 lines 1 and 2 plus the household-incidence share of line 3: RF's "£4.4 billion cost of living package", which counts Fuel Duty "at the share accruing directly to households" (fn 19; about half of line 3's £1.4bn). Lines 1 and 2 sum to £3,685m over 2026-27 and 2027-28. A two-year total, `cumulative` (review A, K-4). |
| `ab2026__package_household_energy_payment_and_electricity_vat` | 5 | Lines 1 and 2: "A £3.7 billion package of household support"; p.17 "£3.4 billion in 2026-27", "£0.3 billion in 2027-28", 45 per cent. The sums show line 2 is the whole cut; see the discrepancies below. |
| `ab2026__package_government_decisions_since_march_2026` | 3 | The OBR's total effect of the Budget's decisions on borrowing, direct and indirect, including decisions not on Table 6.1: "an average of £2 billion a year" (two documents); fn 47 "no overall impact". |
| `ab2026__package_rdel_decisions_excluding_household_energy_payment` | 3 | All the Budget's RDEL decisions over the Spending Review period except the Household Energy Payment: "£3 billion a year", "£9 billion top up" (two documents). A fiscal aggregate, not a programme allocation. |
| `ab2026__package_rf_absolute_policy_changes` | 2 | Every policy decision counted at absolute value (RF's fiscal-event size measure): "£7 billion". RF lists no lines. |
| `ab2026__package_rf_energy_bill_support_announced_at_budget` | 2 | "Support of up to £116 announced today" and "less than a fifth" of the 2027 bill rise. RF doesn't itemise the £116; it includes the £100 Household Energy Payment. |
| `ab2026_option__fuel_duty_rpi_uprating_since_2011` | 2 | Fuel Duty uprated by RPI since January 2011: "around £20 billion" a year (two documents). It mirrors the OBR family's `ab2026__package_fuel_duty_freezes_since_2010_11` (EFO paragraph 3.43): one pair of paths seen from opposite sides, and we keep them on separate keys (review A, K-6). RF's +£20bn measures the revenue the freezes forgo relative to RPI uprating, which we stage "positive = yield" from the option's side. |
| `ab2026__minimum_wage_uprating_april_2027` | 2 | The April 2027 minimum wage rates the Chancellor confirmed (no Table 6.1 line): "worth £1,040 a year for someone working 40 hours a week" (PDF p.12 and the comment). We keep the rates (3.9 per cent; £13.21; 50p) in `reform_hint`. |
| `ab2026__gas_supplier_levy_funded_from_general_taxation` | 1 | Funding the Gas Supplier Levy from general taxation: "save the typical household £7 in 2027-28" (fn 12). We found no Table 6.1 line. |

## Proposed metrics

We have registered none of these in the `Metric` enum of `scorecard_db/models.py`. We give each row one as `proposed_metric`, reusing the AB2025 spelling where one exists: `forecast_borrowing_change`, `average_energy_bill_change`, `incidence_share`, `tax_to_gdp_ratio`, `real_spending_growth`, `spending_pressure` and `forecast_revenue_change`. We coined the rest. Every unit we use appears in the registry as a UnitConcept.

- **Energy:**
  - `typical_energy_bill`: the typical household's annual bill level.
  - `average_energy_bill_change`: a change in it from prices or support combined, not from one policy. We use the registered `energy_bill_change` for single-policy effects.
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
  - `gross_earnings_change` (the AB2025 spelling, which we use in the red book family for the same minimum wage measure; review A, K-7(c)).

## Not staged, and why

- **Design, not estimates (rule 8; we removed 36 rows after the rule arrived):**
  - **Fuel Duty rates:** PR28's "7.6p rise"; p.24's 52.95p to 60.59p a litre and "over 14 per cent". We keep the rates in the continued-freeze option row's `conditions.counterfactual`.
  - **Minimum wage rates and counterfactual upratings:** 3.9 per cent, £13.21 and 50p (p.12 and the comment), the "on-course" 5.7 per cent and the youth rate's 10 per cent (Box 1 and the comment). We keep the rates in the £1,040 rows' `reform_hint`.
  - **Financing remits:** NWF £15.4bn, BBB £5bn, the combined £20.4bn (PR28 and p.6), the 0.27 per cent of GDP of investment commitments, the £5bn defence ringfence and "around a quarter" (p.33).
  - **Programme allocations:**
    - The AI package's £700m, with £165m biosecurity, £120m AI Security Institute, £140m Sovereign AI Unit, £30m local partnerships and the £15m challenge prize.
    - Good Growth Funds' £285m in 2027-28.
    - The Social and Affordable Homes Programme's £1.5bn top-up and its 10,000 homes.
  - **The £108 gas standing charge:** we keep it in the gas rows' `reform_hint`.
  - **A worked example's input:** the £12,739 part-time earnings, which we keep in the worker rows' `household_type`.
  - **Figure 7's flat payments:** the Council Tax rebates (£100 in 2026-27, the 2022 £150) and the 2022-23 £400 Energy Bills Support Scheme, as F7 cells E7, L7 and L11.
  - **The 23 per cent rise in private rents since September 2023 (p.21):** an ONS statistic about no measure.
- **Charts without printed values.** RF prints bar values on only three of the PDF's figures: Figure 7's two 'After rebate' annotations (we stage the two 'Net bill' labels from p.17 bullet 2), Figure 10's eleven line labels and Figure 23's end labels. We take the exact values from the workbook. RF's Figure 5 decade labels for the 1960s–2010s give historical ONS outturn, not anything about the Budget; we stage the 2020s values (1.4 per cent, £400) in text rows.
- **Workbook sheets we left out:**
  - In these sheets RF charts OBR, ONS, IMF or HMT aggregates and history, or its arithmetic on them. We follow AB2025, where we staged these charts' headline text values instead.
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
  - In F12 RF gives marginal tax rates, which we treat as design.
  - Within the staged sheets, we left out:
    - Working and input blocks: F9's raw winner tables, F10's HMT and OBR input rows 5–40, F21's percentile columns other than AD, and F23's level, raw and scenario blocks.
    - F22's second chart (bottom 7 / middle 6 / top 7 vigintiles since 2019-20), which RF doesn't print in the briefing.
    - F23's second chart (AP72:AR73, 2029-30 and 2030-31), which RF doesn't print in the briefing.
- **Text numbers we left out:**
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
    - PR28's "mid-2029" date for living standards to recover, and its ranking of the Parliament as the "second worst … since the 1950s" (a date and a rank, not an estimate of a measure).
  - **Other design:**
    - £100, bands A-D, 5p, 3p / 2p, 2 points, 3 to 6 per cent,
    - the 31 per cent headline bank rate, 20 / 25 per cent,
    - the £1.5bn Good Growth lending facility, the 20 per cent equity loan and 2.5 per cent deposit, the £110,000 / £140,000 income caps,
    - £86.45, £204, 16 hours, £1 for £1, the 55 per cent UC taper,
    - Business Rates retention shares (20 / 50 / 70 / 100 per cent), the 3 and 3.5 per cent defence targets.
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
- **Publications we checked:**
  - The lane fetched RF's publications, press-release, comment, Top of the Charts, events and Budgets listings at 16:19–16:20Z.
  - RF put out one other Budget output on 28–29 October, the launch event page, *Pleasing people and satisfying markets*. RF embeds a YouTube video there and prints no figures, so we neither hash nor stage it.
  - RF illustrates the comment with three slide images (`Slide1-1-scaled.png` to `Slide3-1-scaled.png`), and we didn't stage those charts. Apart from the £1,040, the comment's numbers give minimum-wage design.
  - We found no Budget response briefing, chart pack or Top of the Charts Budget special from 28–29 October.
  - Under "Further reading" on the Spread thin page, RF links two pre-Budget briefings, which fall outside this window and which we didn't stage:
    - *Counting the cost* (8 Oct; page sha256 `415deda6…`).
    - *Hitting the buffers* (13 Oct; `881bbd4d…`).

## Discrepancies in the primaries (reported, not fixed)

1. **v1 and v2 disagree on the income halves.** RF prints £158 / £14 / £144 in v1 and £145 / £15 / £130 in v2, and on v2 p.19 hedges them as "under £145 … over £130 … less than £15". RF still printed £158 / £144 on the landing page when we fetched it on 29 October; by 4 November it printed v2's £145 / £130 (manifest line 8).
2. **The £4.4bn package's years.** On p.19 RF calls it "the Government’s £4.4 billion cost of living package for 2025-26 and 2026-27". The measures fall in 2026-27 and 2027-28 (Table 6.1 lines 1–3), and RF prints no years in the press release or on p.47, so we stage the period as printed, at medium confidence.
3. **The £3.4bn's scope.** On p.17 RF says "Together, these measures cost £3.4 billion in 2026-27" of the Household Energy Payment and "a three-month extension to the VAT cut". The extension falls in 2027-28, and £3.4bn equals lines 1 and 2 in 2026-27 (£2,625m + £755m), so RF's figure includes the original six months of the VAT cut.
4. **Your First Home's sign.** On p.21 RF calls £95m in 2029-30 "a cost". HM Treasury prints +95 on Table 6.1 line 37, a yield ("net income from developer fees").
5. **SAHP top-up** (not staged, rule 8). RF's "£1.5 billion top-up" on p.21 differs from Table 6.1 line 35, which sums to £1,750m over 2027-28 to 2030-31.
6. **Good Growth Funds** (not staged, rule 8). RF's "£285 million in 2027-28" on p.33 differs from line 20, on which HM Treasury prints -£340m that year (the line includes the lending subsidy).
7. **Tax gap measures.** RF's "over £3 billion annually by 2030-31" on p.4 doesn't match the workbook's OBR series (F10 row 52): 2.89 in 2030-31 and 3.64 in 2031-32. We record it in row 67's `conditions.discrepancy` (review A, K-7(h)).
8. **Figure 20's AB26 component.** RF's note says "‘AB26 Changes’ includes the Pension Tax Allowance, removal of standing charges on gas bills, and the Machine Games Levy". In the workbook RF's AB26 Changes also includes "Property and savings tax rise" (column K = F + G + I + J). RF labels the Pension Tax Allowance "Pensioner Personal Allowance" in the workbook.
9. **Figure 10's Fuel Duty series.** RF's note says the series shows "Fuel Duty changes announced in May and October", but the values (-0.575, -0.78) equal Table 6.1 line 3 alone.
10. **Primary balance years.** On p.39 RF says the £107bn of higher tax revenues runs to the end of the Parliament (2028-29). In footnote 53 RF computes it "between 2023-24 and 2029-30, multiplied by forecasted GDP in 2029-30".
11. **Energy bill figures, release vs briefing:**
    - The 28 October release's "£2,210 across 2027" (the 2027 average) differs from Spread thin's £2,192 (the Q1 2027 cap), which RF calls the bill "next year" on p.5.
    - The 29 October release's 2022-23 net bill of £1,685 differs from Figure 7's "After rebate: £1,686" (workbook 1,686.20).
    - p.17's VAT extension "worth £12" differs from the workbook's 12.80 for the cut in 2027-28 (2026-27 prices).
12. **Footnote 50's figure reference.** RF writes "From the forecasts shown in Figure 7", but it shows the current-balance forecasts in Figure 18; Figure 7 charts energy bills.
13. **Capacity vs Table 6.2** (not staged, rule 8). The NWF's £15.4bn and BBB's £5bn "capacity" boosts don't match Table 6.2's financial transactions: NWF line 2 sums to £10.2bn over 2028-29 to 2031-32, BBB line 3 to £0.75bn.
14. *(Withdrawn on 3 November: the coordinator corrected the README's rule 3 example, so RF's package equals the registered one; see "Measure keys".)*
15. **The VAT element's description.** In PR28 para 5 and p.17's heading and paragraph 1 RF describes the package's VAT element as the "three-month extension", and on p.17 it calls the six-month cut "support announced before this Budget". Yet Figure 8, the 52/48 split and the £4.4bn all include "Energy VAT cut (original)".

## Review fixes, 3 November 2026

In its review (`harvest-staging/ab2026/reviews/verify-rf.md` on the staging branch), the RF reviewer approved this family with fixes, and we applied all thirteen: finding 1 as the `P_SAV_PROP` constant, and the rest in an explicit block before `write()` in `stage.py`. We re-opened no primary, because the session's network policy refused resolutionfoundation.org, and changed no printed value.

1. For the 25 rows for exactly lines 61 and 62 we use `ab2026__package_property_and_savings_income_rates`, README rule 2's name (F10 row 51 equals lines 61 + 62 in every year).
2. We removed the passage that contradicted README rule 3's old example, and withdrew discrepancy 14 (kept as a one-line marker); the coordinator has corrected that example.
3. In row 168's note we name the Government's Defence Investment Plan projection.
4. In row 38's note we name the ONS/OBR outturn.
5. In the v1→v2 record we note Figure 8's lower Council Tax rebate bars.
6. We changed "Figure 7's four annotations" to two, and stage the two "Net bill" labels from p.17.
7. We fixed the workbook hash typo.
8. We stage row 23 (−0.4 per cent) as a `point`, `statistic: RHDI per person, average annual growth`, `parse_confidence: medium`.
9. We give row 167 (0.5 per cent) `statistic: real RDEL per person, average annual change (Figure 14)`.
10. We give rows 28, 29, 56, 57, 61 and 63 `price_basis: cash terms (Figure 8)`.
11. (Optional, applied.) We dropped row 397, F10 C48's floating-point zero (−7.46e-7 bn): F10 54 rows, `ab2026_option__fuel_duty_continued_freeze` 6, `arithmetic` 148, total 766.
12. (Optional, applied; England, the coordinator's call.) We set rows 109 and 110 (£358 and 20 per cent) to `geography: England`, as on row 108.
13. We record the VAT element's description as discrepancy 15.

- The contract checker reports 766 rows, 0 problems, and when we re-run `stage.py` it reproduces the gzip byte for byte. COUNTS.json pins its sha256. The coordinator may change proposed-key names again in the cross-family harmonisation recorded below.

## Key harmonisation, 3 November 2026

The coordinator gave each scope one key across families (tranche 1, task 3.4), and renamed these keys in this family:

- `ab2026__minimum_wage_rates_april_2027` → `ab2026__minimum_wage_uprating_april_2027`
- `ab2026__package_obr_total_effect_of_government_decisions` → `ab2026__package_government_decisions_since_march_2026`
- `ab2026__package_obr_direct_effect_of_tax_measures` → `ab2026__package_tax_decisions_since_march_2026`
- `ab2026__package_obr_tax_administration_compliance_and_debt_collection` → `ab2026__package_tax_administration_compliance_and_debt_collection`
- `ab2026_option__obr_tax_measures_with_continued_fuel_duty_freeze` → `ab2026_option__tax_decisions_with_continued_fuel_duty_freeze`

In its three OBR groupings RF restates the OBR's own Table 3.1 rows, so we give them the OBR family's scope names, which drop `obr` (OBR review, finding 9). For the minimum wage key we take the red book's spelling for the same measure. We now share `ab2026_option__fuel_duty_continued_freeze` with the OBR family, where the OBR prints the same alternative's £4.3bn in 2029-30 in paragraph 3.43.

## README rule 10, 3 November 2026

Under README rule 10, in `stage.py` we move the family's totals of the Budget's decisions from `revenue_change` to `decisions_effect_on_borrowing`. We move Table 6.1's total of policy decisions (1 row) and the OBR's direct effect of tax measures that Figure 10 plots (13 rows), 14 rows in all. Counting from 0, the rows are 66, 102, 141–146 and 385–390. We had already given the OBR's total effect of the Budget's decisions (3 rows) that metric, so 17 rows use it. We keep `revenue_change` for single measures and groups of measures, and changed no value or sign.

**Not moved (4 November 2026, review B's RF finding 3, option (b), the coordinator's call).** The 3 November pass had moved the 11 rows of Figure 10's "Net effect if Fuel Duty frozen" (`ab2026_option__tax_decisions_with_continued_fuel_duty_freeze`; rows 147–151 and 432–437). We put them back on `revenue_change`. RF's totals here add the freeze's receipts effect, which row 154's note derives from the OBR's constant-duty-rate Fuel Duty forecast less its central forecast. RF's title for Figure 10 also frames the chart as revenue ("Measures announced raise revenues"). Under rule 10 we treat them as a tax-change estimate whose evidence doesn't establish PSNB scope. The OBR states the freeze's effect on borrowing for 2029-30 only (paragraph 3.43, from Table 7.1). RF's values for the other years give receipts differences, so they don't recombine a stated effect on borrowing. We keep rows 154 and 397–401 (`ab2026_option__fuel_duty_continued_freeze`) on `revenue_change` too.

## Review fixes, 4 November 2026

Two independent reviews of PR #231 at 4f424b9 approved this family with fixes: review B (RF findings 1–8 and nits) and review A (K-4, K-6, K-7(c), K-7(d), K-7(h) and H-1). We applied all of them in a block before `write()` in `stage.py`, with the coordinator's calls on findings 2 and 3, and changed no printed or stored value. We give 4f424b9's indices.

1. **Two-year totals (finding 1).** We mark all 114 Figure 8 rows (245–358), the text rows that restate them (56, 57, 61, 63, 74, 76), the gap rows 62 and 75 and the £4.4bn rows 34, 54 and 127 `cumulative`. For the 95 F8 £ rows, our normalization reads "£ per household as stored: total cash impact over 2026-27 and 2027-28 (Figure 8 note)"; we keep the K rows' own.
2. **RF changed the landing page by 4 November (finding 2, rule 7).** We record the 4 November page as manifest line 8 (no rows cite it). The coordinator chose not to stage its £145 / £130 again, since we stage them in v2 rows 74 and 76. We set `document_version: "29 October page text (superseded by 4 November)"` and a "Superseded" sentence on rows 56–57.
3. **Rule 10 (finding 3, option (b)).** We put rows 147–151 and 432–437 back on `revenue_change`, so the stager's rule 10 count reads 14 (see "README rule 10").
4. **Restated counts (finding 4).** We mark rows 55 and 72 `restated`, `hm_government_publication`, medium confidence, with a note naming HM Treasury.
5. **Tallies (finding 5).** We count 554 workbook rows, corrected the restated source models and recounted the attribution split from the rows (`own` 680, `restated` 86).
6. **Gas standing charge (finding 6).** We gave rows 115–125 `conditions.horizon` and medium confidence.
7. **Signs (finding 7, and K-7(d)).** We give the 122 Figure 21–22 rows (629–750) "positive = growth", and text rows 21, 23, 89, 117, 198, 200, 203 and 204 "positive = gain to households". Row 10 reads "positive = saving (a reduction in the household's bills)".
8. **Nits (finding 8):**
   - We name each chart row's series in `conditions.series` (310 rows), and keep `component` only on the 39 rule 9 parts of line 2 (review A, H-1). On seven text context rows we had used `component` for a driver of a forecast change, or a scenario's spending type; we now use `driver` (rows 51, 80–82, 91, 92) and `spending_type` (row 170);
   - we write F22's category labels "2025-26", not "2025- 26";
   - for stored F7 C/I/M and F9 cells we say "as stored";
   - we name the support series of F7 rows 222, 226, 236 and 241 in `reform_hint`;
   - we gave gap rows 30, 62 and 75 `price_basis: cash terms (Figure 8)`;
   - we corrected the Primaries notes, Figure 21's chart object, F23's second chart, F8 J, discrepancy 15's locator, Review fixes item 2 and the "Not staged" list.
9. **K-4.** We moved the £4.4bn (34, 54, 127) to `ab2026__package_household_energy_vat_and_household_share_of_fuel_duty`.
10. **K-6.** We keep `ab2026_option__fuel_duty_rpi_uprating_since_2011` separate from the OBR's `ab2026__package_fuel_duty_freezes_since_2010_11`, and each family's NOTES names the other.
11. **K-7(c).** We propose `gross_earnings_change` on rows 88 and 211.
12. **K-7(h).** We set `conditions.discrepancy` on row 67.
13. **OBR review B, finding 3.** We key the tax administration group to `ab2026__package_tax_administration_compliance_and_debt_collection_receipts`, as in the OBR family.

- We key both RF's receipts cost (rows 154, 397–401, `revenue_change`) and the OBR's £4.3bn effect on borrowing (paragraph 3.43, `uk_obr_tables` row 2740) to `ab2026_option__fuel_duty_continued_freeze`. At ingest we drop RF's six rows as restatements of the OBR's forecast, and move the OBR's row to `revenue_change`, because the Government didn't adopt the freeze. In rows 385–390 RF restates the OBR workbook's receipts total exactly; we key them to the tax-decisions key with the borrowing metric, and at ingest we drop them as restatements.
- The contract checker reports 766 rows, 0 problems, and when we re-run `stage.py` in a scratch directory it reproduces the gzip byte for byte.
