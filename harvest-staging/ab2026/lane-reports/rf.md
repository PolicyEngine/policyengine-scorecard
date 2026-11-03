# uk_rf_ab2026: Resolution Foundation, Autumn Budget 2026

I staged the family in `sources/harvest-uk-ab2026-2026-10-29/uk_rf_ab2026/`: 767 rows from 7 primaries, and the contract checker reports 0 problems. Nothing is committed, pushed or opened.

The main finding: **RF replaced the Spread thin PDF on the morning of 29 October**, changing its headline income-half figures, and its landing page still prints the old ones.

Two decisions you should check before merging:
- **RF's cost-of-living package carries the registered key `ab2026__package_household_energy_vat_and_fuel_duty`.** That goes against the example in README rule 3, for the reasons under "Things in the primaries that look wrong", item 14.
- **I kept energy-bill and living-standards context rows (null key) after the rule 8 rework.** These are bill levels before support, price-cap forecasts and income projections. Rule 8 could be read strictly as excluding the bill and price-cap rows; the assignment asked for the living-standards and poverty figures explicitly.

**Rules 8 and 9 arrived mid-run.** You added them to the README and checker in this worktree while I was staging; I didn't edit either file. To follow them I removed 36 design rows and re-keyed the electricity VAT cut's two parts as components of line 2. That is why the family went from 803 rows to 767.

## Files
| file | sha256 |
|---|---|
| `claims_staged.jsonl.gz` (767 rows) | `d2ab271c796a748be0748a9f310f309a0a2c1e0eedfdfaf41e26b6a855093886` |
| `manifest.jsonl` | `5986ae49…` |
| `NOTES.md` | covers what you asked for, plus rules 8–9 |
| `stage.py` | rows as data |

Running `stage.py` twice gives the same gzip sha256. `stage.py --check-primaries <dir>` also re-hashes every primary, finds every text quote in its document, and compares all 759 embedded workbook cells with the sheet XML. It reports 0 problems; I mutation-tested both checks and each catches a single changed character.

## Primaries
Every site fetch worked (HTTP 200, no blocks), so I didn't need the local fallback; the assignment's local copy of v1 is byte-identical. A second fetch at 17:02Z returned identical bytes for all seven.

| primary | sha256 | rows |
|---|---|--:|
| Press release, 28 Oct | `ac5369e6f73bbfddc53dfd9977a34a89e032be513e1a21f192a02d124ef98878` | 24 |
| Press release, 29 Oct | `40b102686bbee5dbaff30ea96bfa6bef3f73fe777142a826c811e7fa88c7c22d` | 19 |
| Spread thin landing page | `66a999dc35476a54c003bb9fda0ebbb3648cb52403d7b78c5b9fe9f5f569d792` | 18 |
| Spread thin PDF v1 (`Spread-thin-1.pdf`, the local copy) | `a669f39d30d5648697ce0234692bd9695fadafd85669ee809c02af0c90595603` | 3 |
| Spread thin PDF v2 (`Spread-thin.pdf`, the one the page now links) | `9536b6cd8478dea91f88a103c9004cc7b4cdde269a521f62048e3c523a15d9ff` | 147 |
| Chart-data workbook (linked from the landing page) | `a4e1c072bf8f95f364a470be46ad1d1fad2c4f86fa83d371b45b577df1d6e0d1` | 555 |
| Comment, *It's good to be flexible* (29 Oct) | `3510a245ad89667dee8e6dbb42d175970c05667a244c4034197c43000962fcfc` | 1 |

**The replacement (rule 7):**
- **What changed:** v2 (uploaded 12:14 GMT) changes p.5 and p.19 from £158 / £14 / £144 to £145 / £15 / £130, and lowers the Figure 8 axis.
- **v1 rows:** only the three superseded p.5 figures cite v1, marked as superseded.
- **Landing page:** its key findings still say £158 / £144 for the income halves; I staged them as printed and flagged them.
- **Workbook:** its values match v2.

**Workbook rows:** I read the stored cell values behind each chart (full precision) for the figures of RF's own estimates:
- F7: energy bill and support by year.
- F8: temporary policies by vigintile.
- F9: LHA and Your First Home by decile.
- F10: tax decisions and a continued Fuel Duty freeze.
- F20: permanent tax and benefit changes by vigintile, including the four AB26 component columns the chart doesn't plot.
- F21: median non-pensioner income growth.
- F22: non-pensioner income growth by vigintile.
- F23: poverty change.

## Rows by measure_key
| key | rows |
|---|--:|
| null (198 with a proposed key, 332 context) | 530 |
| `ab2026__package_household_energy_vat_and_fuel_duty` | 57 |
| `ab2026__electricity_vat_zero_rate_to_july_2027` (39 are measure components) | 42 |
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
| `ab2026__defence_investment_plan_further_savings` (matched by its sum; medium confidence) | 1 |

## Proposed keys and their scope
NOTES.md gives each in full.

| proposed key | rows | scope |
|---|--:|---|
| `ab2026__package_rf_parliament_permanent_tax_and_benefit_measures` | 42 | All permanent tax and benefit changes this Parliament, against the policy inherited from Hunt (F20 net, £320 / £2,000, 0.9–2.2 per cent) |
| `ab2026__gas_standing_charge_moved_to_unit_rates` | 31 | Announced, but it has no Table 6.1 line |
| `ab2026__package_savings_and_property_income_rates_plus_2pp` | 25 | Lines 61 and 62 |
| `ab2026__package_rf_ab26_permanent_personal_measures` | 19 | Lines 52, 56, 61, 62 plus the gas standing charge |
| `ab2026_option__lha_unfreeze_2027_28` | 17 | Unfreezing Local Housing Allowance in 2027-28 |
| `ab2026__package_obr_direct_effect_of_tax_measures` | 13 | The OBR's direct effect of tax measures, sign flipped by RF |
| `ab2026_option__obr_tax_measures_with_continued_fuel_duty_freeze` | 11 | The above plus a continued Fuel Duty freeze |
| `ab2026__package_obr_tax_administration_compliance_and_debt_collection` | 7 | The OBR's tax-administration group of measures |
| `ab2026_option__fuel_duty_continued_freeze` | 7 | Rates held at 52.95p instead of rising to 60.59p |
| `ab2026__package_rf_other_tax_measures` | 6 | RF's residual of other tax measures |
| `ab2026__package_household_energy_payment_and_electricity_vat` | 5 | Lines 1 and 2 (£3.7bn, £3.4bn, £0.3bn, 45 per cent) |
| `ab2026__package_obr_total_effect_of_government_decisions` | 3 | The OBR's total effect of decisions on borrowing |
| `ab2026__package_rdel_decisions_excluding_household_energy_payment` | 3 | RDEL decisions excluding the Household Energy Payment |
| `ab2026__package_rf_absolute_policy_changes` | 2 | £7bn of giveaways and clawbacks at absolute value |
| `ab2026__package_rf_energy_bill_support_announced_at_budget` | 2 | "Up to £116" of support |
| `ab2026_option__fuel_duty_rpi_uprating_since_2011` | 2 | Fuel Duty uprated by RPI since 2011 (£20bn) |
| `ab2026__minimum_wage_rates_april_2027` | 2 | The £1,040 gain |
| `ab2026__gas_supplier_levy_funded_from_general_taxation` | 1 | The £7 saving |

## Not staged
- **Design rows removed under rule 8 (36):**
  - **Fuel Duty and minimum wage rates.** These include the 5.7 and 10 per cent counterfactual upratings.
  - **Financing remits:** the National Wealth Fund's £15.4bn, the British Business Bank's £5bn and the combined £20.4bn.
  - **Programme allocations:**
    - the AI package's £700m and its sub-allocations;
    - Good Growth Funds' £285m;
    - the Social and Affordable Homes Programme's £1.5bn top-up and its 10,000 homes.
  - **Payment amounts and inputs:**
    - the £108 standing charge;
    - the £12,739 worked-example input;
    - Figure 7's flat £100, £150 and £400 payments.
  - **Context:** the 23 per cent rent statistic.
  - **Where the design facts went:** `reform_hint` or `conditions` of the related rows.
- **Workbook sheets left out:** F1–F6, F11–F19 and "Extra spending stats". They chart OBR, ONS, IMF and HMT aggregates or history (the AB2025 precedent), and F12 holds tax rates.
- **Chart bars:** none read. Only printed labels were staged: Figure 7's four annotations, Figure 10's eleven and Figure 23's two.
- **Text figures left out:**
  - macro forecasts and statistics: CPI, GDP, gilt yields, migration, energy market prices;
  - history and international comparisons;
  - rankings, ratios and third-party figures (Anthropic, Health Foundation, EDF);
  - the £72bn average of the last two Budgets, which has no single period.
- **Pages checked but not staged:**
  - The launch event page is a video with no printed figures.
  - The comment's slide images are charts.
  - *Counting the cost* (8 Oct) and *Hitting the buffers* (13 Oct) are pre-Budget.
  - I found no other RF Budget briefing or chart pack from 28–29 October.
  - Every page I tried was reachable.

## Checker and spot check
- **Checker:** `sources/harvest-uk-ab2026-2026-10-29/uk_rf_ab2026: 767 rows, 0 problems`.
- **First pass:** I checked 40 random rows by hand on the earlier 803-row version, and all matched.
- **Second pass:** I drew 37 rows on the final version and re-opened each primary at its locator; all 37 matched on number, sign, unit and period:
  - **Press releases and landing page:** rows 27 (48%), 38 (2.5%), 53 (62%), 57 (£144).
  - **PDF text:** rows 66 (£5bn), 75 (£15), 83 (£110bn), 87 (4.14%), 88 (£1,040), 110 (20%), 115/117/120/122 (57%, £46, −£61, 46%), 134 (900,000), 158 (£150m), 161 (£2.6bn), 177 (£2bn), 185 (£18bn), 210 (£9bn).
  - **PDF chart labels:** rows 143 (+£3.1bn) and 150 (+£1.9bn), each matched to its workbook cell (E46 3.078, G54 1.886).
  - **Workbook cells:** F7!I5, F8!D10/F11/F20/F23/F25/D26 (four are VAT components), F10!H53, F20!M17/D24/L25/E26, F22!AI343, F23!AQ67/AP70.
- **Scope audit:** I listed every key against RF's own label for the figure; every one matches.

## Things in the primaries that look wrong
1. **Stale landing page:** its key findings print £158 / £144 while the linked v2 PDF says £145 / £130.
2. **£4.4bn package years:** p.19 dates it to "2025-26 and 2026-27", but the measures fall in 2026-27 and 2027-28.
3. **£3.4bn wording:** p.17 calls it the payment plus "the three-month extension" of the VAT cut. The number equals lines 1 and 2 in 2026-27, so it includes the original six months.
4. **Your First Home sign:** RF calls the £95m in 2029-30 a "cost"; Table 6.1 line 37 prints +95, a yield.
5. **SAHP top-up:** RF says £1.5bn; Table 6.1 line 35 sums to £1,750m.
6. **Good Growth Funds:** RF says £285m in 2027-28; line 20 prints −£340m.
7. **Tax-gap measures:** "over £3 billion annually by 2030-31" doesn't match the workbook's 2.89 in 2030-31 (3.64 in 2031-32).
8. **Figure 20's AB26 Changes:** the note leaves out the property and savings rate rise, but the workbook includes it. The workbook calls the Pension Tax Allowance "Pensioner Personal Allowance".
9. **Figure 10's Fuel Duty series:** the note says "May and October" changes, but the values equal line 3 alone.
10. **The £107bn of extra tax:** footnote 53 computes it to 2029-30; the text says 2028-29.
11. **Energy bill numbers:** £2,210 (28 Oct release) vs £2,192; £1,685 (29 Oct release) vs £1,686; the VAT extension's £12 vs the workbook's 12.80.
12. **Footnote 50:** it cites Figure 7 where it means Figure 18.
13. **Capacity figures:** the NWF's £15.4bn and the BBB's £5bn don't match Table 6.2's financial-transaction sums (£10.2bn and £0.75bn).
14. **README rule 3's example is wrong.** Table 6.1 line 2's title and costs cover the whole VAT cut from 1 October 2026 (£755m in 2026-27), and the registry's own modifier agrees. So RF's package equals lines 1, 2 and 3 exactly, and I staged it under the registered key.

The primaries are hashed under `.ab2026-primaries/uk_rf_ab2026/` (git ignores it), alongside my scratch files.

DONE