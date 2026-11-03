# uk_ifs_ab2026 — Institute for Fiscal Studies, Autumn Budget 2026

**Working files.** `stage.py`, which writes `claims_staged.jsonl.gz` and is the file meant wherever these notes say `stage.py`, lives on branch `uk/ab2026-harvest-staging` at `harvest-staging/ab2026/lanes/ifs/uk_ifs_ab2026/stage.py`; this branch carries only NOTES.md, `manifest.jsonl` and `claims_staged.jsonl.gz`. `.ab2026-primaries/uk_ifs_ab2026/` was the lane's local primaries folder and was never committed: the repository carries no primary bytes, so fetch each primary from its `manifest.jsonl` URL and check its sha256.

**87 rows from four current briefing decks** (five manifested PDF versions, including the superseded TW_0). `source: ifs`. The first lane staged 106 rows on 29 October. On 3 November the IFS addendum (`briefs/ifs-addendum.md` on the staging branch) was applied: sections 3 and 4 in full, section 2 as far as the network allowed (none), section 1 not at all (see "Pending" below). Its edits sit in an explicit block at the end of `stage.py`'s data. The sections below this summary keep the first lane's per-deck record; where they differ from the summary, the summary wins.

## Pending: rows to be added from browser-read text (addendum section 1)

These two IFS pages refuse non-browser clients, and their text is not on GitHub. The coordinator read them in a browser on 29 October and adds their rows locally after this family lands:

- https://ifs.org.uk/articles/autumn-budget-2026-initial-response — pending: rows to be added from browser-read text.
- https://ifs.org.uk/collections/autumn-budget-2026 (Helen Miller's opening remarks) — pending: rows to be added from browser-read text.

The addendum brief records that the coordinator's browser read found no estimates in the IFS explainer or the fiscal devolution comment, so those pages are no longer listed as unreached for want of access; they hold nothing to stage.

## Unreached: the seven IFS data items (addendum section 2)

The seven charts in the collection's "Key charts" section (listed in `harvest-staging/ab2026/ifs/data-items.json` on the staging branch) serve their data through Flourish. On 3 November the session's network policy refused public.flourish.studio and flo.uri.sh at the proxy (HTTP 403 to CONNECT), so no visualisation's data was read and none is staged. No value was read off an image. Each is unreached:

| Data item | Flourish |
|---|---|
| https://ifs.org.uk/data-items/growth-real-household-disposable-income-over-decade-1950s-2020s | visualisation/30734907 |
| https://ifs.org.uk/data-items/current-budget-deficit-march-2026-and-october-2026-forecasts | visualisation/30726471 |
| https://ifs.org.uk/data-items/headroom-share-gdp | visualisation/30726788 |
| https://ifs.org.uk/data-items/real-gdp-growth-over-forecast | visualisation/30726917 |
| https://ifs.org.uk/data-items/average-annual-growth-real-household-disposable-income-parliament | visualisation/30726939 |
| https://ifs.org.uk/data-items/long-term-impact-announced-tax-changes-fiscal-event | visualisation/30726047 |
| https://ifs.org.uk/data-items/number-individuals-aged-16-paying-higher-or-additional-rate-income-tax-0 | visualisation/30727239 |

## Coverage

| Primary | Rows |
|---|--:|
| Weathering the fiscal storm? (Isabel Stockton) | 39 |
| Cost of living measures, TW_1 (Tom Wernham) | 15 |
| Cost of living measures, TW_0 (superseded) | 0 |
| Spending on public services: the Achilles' heel? (Bee Boileau) | 21 |
| Tax measures (Stuart Adam) | 12 |

| measure_key | Rows | of which components (rule 9) |
|---|--:|--:|
| `null`, context (no proposed key) | 60 | 0 |
| `null` with a proposed key | 4 | 0 |
| `ab2026__founders_relief_cgt` | 4 | 0 |
| `ab2026__household_energy_payment_100_bands_a_to_d` | 3 | 0 |
| `ab2026__package_household_energy_vat_and_fuel_duty` | 3 | 0 |
| `ab2026__hmrc_tax_gap_package` | 2 | 2 |
| `ab2026__badr_lifetime_limit_500000` | 1 | 0 |
| `ab2026__business_rates_sbrr_rhl_thresholds_raised` | 1 | 0 |
| `ab2026__distributions_framework_modernised` | 1 | 0 |
| `ab2026__electricity_vat_zero_rate_to_july_2027` | 1 | 0 |
| `ab2026__fuel_duty_5p_cut_extended_and_rpi_rise_deferred` | 1 | 0 |
| `ab2026__package_total_tax_policy_decisions` | 1 | 0 |
| `ab2026__writing_down_allowance_12pc_and_fya_50pc` | 1 | 0 |

Attribution: 36 `own`, 51 `restated`.

## Proposed measure keys

- `ab2026__package_property_and_savings_income_rates` (1 row): exactly Table 6.1 lines 61 and 62, Adam slide 2's "Increased income tax on savings & property income", £1.1bn in 2031–32 (lines 61 and 62 print 455 + 590 = 1,045).
- `ab2026__gas_standing_charge_moved_to_unit_rates` (3 rows): no Table 6.1 line. Wernham slide 8's "Shifting gas standing charge onto unit price": "This charge will be scrapped, but per-unit price will be increased to absorb this". The spelling is the RF family's.

## Keys the addendum changed (rules 3 and 9)

| Rows (first lane, 0-based) | Was | Now | Why |
|---|---|---|---|
| 45, 46, 52 (£5bn, £140, 35%) | proposed `ab2026__package_ifs_cost_of_living_support` | `ab2026__package_household_energy_vat_and_fuel_duty` | IFS's three measures are the energy payment, the whole electricity VAT cut and the fuel duty cut, exactly lines 1, 2 and 3 (README rule 3, corrected). Lines 1+2+3 print 5,040 over 2026-27 and 2027-28, IFS's £5bn. |
| 48 (£36) | proposed `ab2026__package_ifs_electricity_vat_oct_2026_june_2027` | `ab2026__electricity_vat_zero_rate_to_july_2027` | Line 2 costs the whole cut, 1 October 2026 to 1 July 2027, including the weeks before the Budget. |
| 89 (£1.8bn) | proposed `ab2026__package_ifs_self_assessment_payment_timing` | `ab2026__hmrc_tax_gap_package`, component | Table 6.3 row 3, "More timely payment" for Self Assessment, +1,815m in 2031–32: a part of line 45. |
| 92 (£1bn) | proposed `ab2026__package_ifs_hmrc_compliance_staff_and_debt_collection` | `ab2026__hmrc_tax_gap_package`, component | Table 6.3 rows 7 (debt management, +575m) and 8 (compliance officers, +415m), 990 in 2031–32: a part of line 45. |
| 91 (£1.1bn) | proposed `ab2026__package_ifs_savings_and_property_income_tax` | proposed `ab2026__package_property_and_savings_income_rates` | The name README rule 2 gives exactly lines 61 and 62. |
| 55–57 | proposed `ab2026__package_ifs_gas_standing_charge_reallocation` | proposed `ab2026__gas_standing_charge_moved_to_unit_rates` | A measure with no Table 6.1 line is `ab2026__<slug>`; the RF family's spelling. |
| 61 (£1.2bn per year) | proposed `ab2026__package_ifs_defence_investment_plan_funding` | dropped | See below. |

**Defence Investment Plan funding.** The addendum asked whether IFS's "£1.2bn per year gap in Defence Investment Plan funding" is an estimate (keep, as context) or not. The first lane's own note calls it the government's DIP funding announcement, restated: the Budget "filled" the gap. That makes it a spending allocation, which rule 8 excludes, so it is dropped rather than kept as context. It is close to, but not exactly, Table 6.1 line 41 (capital reallocation to fully fund the DIP: +1,100, +1,135, +1,180 in 2029-30 to 2031-32), so it is not keyed there either.

## Not staged (rules 8 and 9)

The addendum dropped 19 of the first lane's 106 rows, all under rule 8:

| Category | Rows | Examples (deck, slide) |
|---|--:|---|
| Measure parameters: rates, payment amounts, thresholds, a fare cap | 10 | £100 Household Energy Payment (Wernham 3); 5p fuel duty cut (Wernham 3); 0% VAT on electricity (Wernham 3, Adam 5); £2 bus fare cap (Wernham 15); Founders' Relief 10% rate, 24% comparator and £10m limit (Adam 3); RHL rateable values £12,000 and £21,000 (Adam 4) |
| Government targets | 3 | defence at 3% of GDP by 2030 (Boileau 4, repeated on 8); the DIP's earlier 2.7% in 2029–30 (Boileau 4) |
| Inputs of IFS's own spending scenarios | 2 | defence held at 2.7% of GDP, or at 3% by 2030–31 (Boileau 7 and 9); the scenarios' computed growth rates stay |
| Financing and allocations | 2 | ~£1bn a year of NWF and BBB financing for defence (Boileau 5); the £1.2bn a year of DIP funding (Boileau 4) |
| The base a measure moves | 2 | the £108 average gas standing charge and its 13% share of a typical gas bill (Wernham 8), as the red book dropped its £108 |

Each dropped parameter that names a measure stays in the kept rows' `reform_hint`. The 25% capital and 40% day-to-day reserve shares (Boileau 11) stay: the addendum lists them as estimates. The bond spread and debt-ownership context rows (Stockton 7) are not design and stay as context.

## Verification (3 November 2026)

- **Checker:** `PYTHONPATH=. python pipeline/ab2026_harvest_contract.py sources/harvest-uk-ab2026-2026-10-29/uk_ifs_ab2026` reports 87 rows, 0 problems.
- **Determinism:** a re-run of `stage.py` reproduces `claims_staged.jsonl.gz` byte for byte. COUNTS.json pins its sha256.
- **Spot check: not done.** The addendum asked for 15 random rows re-opened at their locators, five from the new primaries. There are no new primaries (sections 1 and 2 above), and the session's network policy refused ifs.org.uk, so no deck could be re-fetched. Every kept row's printed value is unchanged from the first lane, whose spot checks are recorded in the deck sections below.
- **Stale files:** the family had no report or spot-check files.

## Access recipe and primary inventory

Fresh fetches began **2026-10-29 15:43:43 UTC**, using exactly:

```sh
curl -sSL -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15" URL
```

The fetch also saved response headers and HTTP status and imposed a 50-second
timeout. Bytes are under `.ab2026-primaries/uk_ifs_ab2026/`, outside the vendored
family. SHA256s were checked with `shasum -a 256`. PDFs were read with
`pdftotext -layout` and rendered for visual checks of labels and embedded images.
None of the PDF annotations links to a chart-data download.

| Primary | Access | Bytes | Rows | SHA256 |
|---|---|--:|--:|---|
| [Weathering the fiscal storm?](https://ifs.org.uk/system/files/2026-10/Weathering-the-fiscal-storm-IS.pdf) | direct | 318,348 | 39 | `fd09e707a4bc0a8e0a3de4a3fa902c8ccdc1e4c44ccdd0dee92866857aa4690b` |
| [Cost of living measures (TW_0, superseded)](https://ifs.org.uk/system/files/2026-10/Cost-of-living-measures-TW_0.pdf) | local copy | 231,180 | 0 | `abb63d9c4ecd21c3c9173077c5e92d8015c7cc30aebd12be159185d7d157f12a` |
| [Cost of living measures (TW_1, revised)](https://ifs.org.uk/system/files/2026-10/Cost-of-living-measures-TW_1.pdf) | direct | 222,191 | 21 | `6ed174b22b4d22a34c8bbd450194fb2b4181a9d566b137913bee52ca49a0299b` |
| [Spending on public services: the Achilles heel](https://ifs.org.uk/system/files/2026-10/Spending-on-public-services-the-Achilles-heel-BB.pdf) | direct | 157,838 | 28 | `7403ecc0641b23f5ffc0cb28f67435dbd1b8df6b124874ffae7ae7f75e357aa6` |
| [Tax measures](https://ifs.org.uk/system/files/2026-10/Tax-measures-SA.pdf) | direct | 133,005 | 18 | `6792dc448f40d34f174b6a3c839863b5c969a7334263f5d6b539be62a0428bb8` |

Stockton's fresh file is byte-for-byte identical to assigned `stockton.pdf`,
confirming it is **Weathering-the-fiscal-storm-IS.pdf**. The other three current
decks also match their supplied local copies. TW_0 returned HTTP 403; the
supplied local PDF was copied to `TW_0-local.pdf` and hashed. All rows from the
cost-of-living presentation cite TW_1, not the superseded version. Full TW_0/TW_1
changes are documented below; no numerical claim changed.

HTML pages that returned a Cloudflare challenge (HTTP 403) to the first lane at 15:43:43 UTC; see "Pending" above for what has become of each:

- https://ifs.org.uk/articles/autumn-budget-2026-initial-response
- https://ifs.org.uk/articles/autumn-budget-2026-explained
- https://ifs.org.uk/collections/autumn-budget-2026
- https://ifs.org.uk/events/autumn-budget-2026-ifs-analysis

No assigned local HTML copies exist. No attempt was made to bypass the blocks.
Challenge pages are retained only as fetch evidence in the ignored primaries
directory; they are not IFS publications and are not manifested. No rows are
staged from them. The explainer's existence/content cannot be confirmed from its
challenge response. The blocked collection and event pages prevent discovering
additional AB2026 items or linked xlsx/csv downloads. No data file was identified
inside the reachable PDFs; this is an access limit, not a finding that IFS posted
no data. No Wayback, alternative domain or other bypass was attempted.

## Family conventions

- Fiscal years use their end year and `conditions.fy`. Calendar years,
  cross-fiscal-year nine-month support, and publication-date snapshots have
  no `fy`; full horizons and missing dates are disclosed. Unspecified-year
  Founders' Relief annual figures use annual 2026 publication markers and
  medium confidence, not an inferred implementation year.
- Monetary magnitudes and signs are verbatim. £bn and £m are normalised to
  GBP. Percentage forecasts and rates stay percent; recipient shares divide
  by 100. Fiscal cells say percent of GDP or revenues as printed, rather
  than inventing a real-GDP unit. 134 basis points is 1.34 percentage points.
  The fuel-duty parameter keeps proposed unit `pence_per_litre`.
- Real/cash and price bases stay as published. Nine-month household support
  is not annualised. A printed positive magnitude followed by “decrease”
  remains positive, with the direction recorded in conditions.
- All figures are `point`: no producer scenario is substituted for a central
  OBR estimate and no confidence band is invented. “Central” would mean a
  producer-labelled central forecast; the staged figures contain no such label.
- `arithmetic` is used for IFS calculations where the deck does not name
  TAXBEN. Official costings/forecasts are `restated`, with original source
  named in notes where supplied or inferable; administrative policy parameters
  are distinguished from IFS estimates. IFS does not cite PolicyEngine here.
- Current-law/default baseline is null. No new baseline world is inferred.
  Every condition value is a string. Quotes are under 15 words, contain the
  exact value_raw, and refer to printed text, a data label or a numeric cell.

## Stockton fiscal deck

39 rows: 38 printed numeric cells in slide 7's **Fiscal traffic lights** image
table, plus slide 8's “roughly 1 in 4 revisions” risk annotation. Text extraction
misses the entire image table; all cells were transcribed from the rendered
slide and independently audited. The table spans FY2026-27, 2027-28, 2029-30 and
2031-32; missing intermediate years were not invented. Net worth is explicitly
inverted and the signs were not reversed. The debt-interest denominator is
revenues, while debt ownership is a share of total debt.

The table prints no source citation. OBR attribution for the 36 forecast cells
is inferred from the surrounding OBR forecast slides, not presented as an
explicit citation; these rows have medium confidence and disclose the inference.
Debt-ownership's administrative origin likewise has no named original provider
or observation date. The 134bp spread is an IFS market comparison with other
G7 economies whose source/weighting/date are unspecified. The latter two use a
2026 in-year snapshot. The 1-in-4 risk uses historical forecast revisions since
2010 excluding 2020-21; “Spring” is interpreted as Spring 2027 and disclosed.
All fiscal rows have null measure_key and no proposed measure.

Not staged: slides 3–6 forecast/borrowing bars, diamonds and lines, and slide 8's
forecast/outturn lines, because they have no numeric data labels. Axis ticks,
chart origins and dates are not outcome rows. Slides 1–6 were visually checked
for hidden printed numbers. No headroom or tax/GDP number is printed there.

## Proposed metrics and units

The table lists every proposed metric used. Producer-specific meanings and
scopes are in the component sections and each row's statistic/conditions.
Existing AB2025 spellings are reused where they fit. `statutory_tax_rate` is a
single spelling across Adam and Wernham; `real_spending_growth_revision`
distinguishes a historical growth revision (percentage points) from growth.

| Proposed metric | Rows | Unit(s) | Scope example |
|---|--:|---|---|
| `affected_share` | 2 | share | £100 Household Energy Payment (Jan 2027) |
| `average_energy_bill_change` | 1 | gbp | EDF forecast £470 increase in annual household gas and electricity prices in January |
| `average_household_support` | 4 | gbp | Cost of living support, Oct-June, England: energy payment, removal of VAT on electricity, fuel duty freeze and cut |
| `benefit_payment_amount` | 1 | gbp | £100 one-off household energy payment in England, January 2027 |
| `business_rates_bill_change` | 1 | gbp | maximum annual bill saving |
| `cpi_inflation_rate` | 2 | percent | The OBR forecasts 3.8% CPI inflation in Q1 2027 |
| `current_budget_deficit` | 4 | percent | Current budget deficit (% of GDP) |
| `current_budget_deficit_revision_risk` | 1 | share | Risks from the forecast |
| `debt_interest_share_of_revenue` | 4 | percent | Debt interest costs (% of revenues) |
| `debt_owned_by_non_residents_share` | 1 | percent | Debt owned by non-residents (% of total) |
| `energy_standing_charge` | 1 | gbp | Average standing charge for gas is £108 a year: |
| `energy_standing_charge_share` | 1 | share | 13% of typical gas bill |
| `fare_cap` | 1 | gbp | £2 cap on bus fares |
| `forecast_spending_change` | 1 | gbp | defence financing |
| `fuel_duty_rate_cut` | 1 | pence_per_litre | Temporary extension of 5p fuel duty cut and freeze to cover January to June 2027 inclusive |
| `gross_financing_requirement` | 4 | percent | Gross financing requirement (% of GDP) |
| `primary_deficit` | 4 | percent | Primary deficit (% of GDP) |
| `public_sector_net_borrowing` | 4 | percent | Net Borrowing (% of GDP) |
| `public_sector_net_debt_ex_boe` | 4 | percent | PSND ex BoE (% of GDP) |
| `public_sector_net_debt_ex_boe_change` | 4 | percent | PSND ex BoE (year-on-year change, % of GDP) |
| `public_sector_net_financial_liabilities_change` | 4 | percent | PSNFL (year-on-year change, % of GDP) |
| `public_sector_net_worth_inverted_change` | 4 | percent | PSNW (inverted, year-on-year change, % of GDP) |
| `real_spending_growth` | 11 | percent | average annual real-terms budget growth |
| `real_spending_growth_revision` | 1 | percentage_points | average revision to annual spending growth when budgets must be allocated |
| `reserve_allocated_share` | 2 | percent | share of reserve already allocated |
| `share_of_energy_price_increase_offset` | 1 | share | Three cost-of-living measures: household energy payment, electricity VAT relief and fuel duty freeze/cut |
| `spending_pressure` | 7 | gbp | total departmental spending |
| `statutory_tax_rate` | 4 | percent | Temporary 0% VAT on domestic electricity; previously announced for Oct to April, extended to end of June |
| `tax_threshold_level` | 3 | gbp | maximum qualifying gains |
| `taxpayer_gain` | 1 | gbp | maximum gain per beneficiary |
| `ten_year_bond_spread_other_g7` | 1 | percentage_points | 10-year bond spread (bps, vs. other G7 economies) |

The only proposed unit is `pence_per_litre`: the printed 5p fuel duty cut's
per-litre amount, following the policy's named basis. No proposed baseline.

## Wernham cost-of-living deck

Tom Wernham component: 21 rows from the revised 17-slide Cost of living measures deck, cover dated 29 October 2026. Source slug `ifs`; own household-price calculations use `arithmetic` (the deck does not name TAXBEN), OBR forecasts use `obr_efo_forecast`, EDF's energy-price forecast uses `edf_energy_price_forecast`, and announced statutory parameters use `administrative_data` with restated attribution and administrative_fact benchmark. No chart bars were read for values.

Access/version evidence:

- TW_1 freshly fetched directly at 2026-10-29 15:43:43Z using the assigned Safari user agent. SHA256 `6ed174b22b4d22a34c8bbd450194fb2b4181a9d566b137913bee52ca49a0299b`, 222191 bytes. This hash is identical to the coordinator's local copy of the TW_1 PDF.
- TW_0 fresh URL returned HTTP403, so the assigned local file was copied to `.ab2026-primaries/uk_ifs_ab2026/TW_0-local.pdf`, hashed, and extracted using `pdftotext -layout`. SHA256 `abb63d9c4ecd21c3c9173077c5e92d8015c7cc30aebd12be159185d7d157f12a`, 231180 bytes; manifest access must be `local copy`. No bypass was attempted.
- Text diff: TW_0 has18 pages, TW_1 has17. TW_0 p4 already includes the80%/91% eligibility annotations; TW_1 p4 omits these. TW_0 p5 has those eligibility annotations overlapping the VAT/fuel commentary. TW_1 p5 relocates eligibility to the lower chart and VAT/fuel commentary to the upper chart. TW_0 p6 is another copy of the unannotated support chart and was removed. TW_0 p7–18 correspond to TW_1 p6–17. No printed numerical claim changes. All staged rows cite TW_1; TW_0 contributes zero rows but is manifested as the changed primary required by rule7.

Coverage by measure_key: null14; `ab2026__household_energy_payment_100_bands_a_to_d`4; `ab2026__fuel_duty_5p_cut_extended_and_rpi_rise_deferred`2; `ab2026__bus_fare_cap_2_england_outside_london_2027`1. Within null: 6 unscored context rows; the remaining8 use proposed measure keys below. Rows per primary: TW_1=21, TW_0=0.

Proposed measure scopes: the first lane's three Wernham proposals were re-keyed on 3 November (see "Keys the addendum changed" above). The cost-of-living package is exactly lines 1, 2 and 3, because line 2 costs the whole VAT cut including the weeks before the Budget; the full-period VAT row is line 2; the gas standing-charge rows use `ab2026__gas_standing_charge_moved_to_unit_rates`.

Proposed metrics and units:

- `cpi_inflation_rate`: printed OBR3.8% and1.9% CPI forecast levels for Q12027, not inflation effects from measures.
- `average_energy_bill_change`: existing AB2025 proposal; EDF£470 annual energy-price increase from January2027.
- `benefit_payment_amount`: £100 per eligible household one-off payment, rather than the average gain across all households.
- `fuel_duty_rate_cut`, proposed_unit `pence_per_litre`: printed5p extension; no negative sign is inserted. Per-litre basis follows the named policy, though the slide prints only5p.
- `statutory_tax_rate`:0% electricity VAT during October2026–June2027, not an effective tax rate.
- `average_household_support`: nine-month cash support, including indirect tax reductions; no conversion to annual gains or household income changes. Printed£140 headline and £24/£36/£80 all-household chart labels.
- `affected_share`: existing AB2025 proposal, payment receipt by80% of all England households and91% of the poorest30%; normalized to0.8 and0.91 shares. Household ranking is by spending, not income decile.
- `share_of_energy_price_increase_offset`: the printed "around35%" of forecast price increases covered by the three measures; normalized to0.35 share, no ratio derived from bars.
- `energy_standing_charge`: current annual gas standing charge£108; context.
- `energy_standing_charge_share`: current13% of a typical gas bill; normalized to0.13 share, context.
- `fare_cap`: £2 single bus fare cap, a restated policy parameter. Exact2027 timing and England-outside-London scope follow registered Table6.1 line4; the slide itself gives only "£2 cap on bus fares", and the row explicitly says this.

Conventions: GBP amounts stay as printed in cash or2026-27 prices as specified; the £5bn aggregate is multiplied by1e9. Shares divide printed percentages by100, while CPI percentages and the printed1% income decrease remain percentages. Positive cost is cost to the Exchequer; positive household support is a gain. The printed1% decrease in real household disposable income is not re-signed; its direction is explicit in sign_convention. October2026–June2027 figures use annual time_basis, end-period marker2027 and horizon strings, with no fiscal-year condition because the nine months cross fiscal years. The1% RHDI decrease spansFY2024-25 toFY2026-27 and usesFY2026-27/end2027. No row is described as central: all figures are printed point estimates/parameters. For gas reform, year2026 is explicitly only a publication marker because no implementation year is printed. Baseline remains null; unsupported counterfactual definitions were not invented.

Not staged:

- Spending-decile bars in pp4–6, energy-price bars/percentiles pp7/16/17, carbon implicit-tax bars p9, and real-income decade/forecast lines pp11/14 have no data labels (apart from the separately staged£24/£36/£80 all-household labels and1% annotation). Visual inspection found no further printed values, embedded raster tables, or hidden numeric labels.
- Slide5 repeats p4's £140/£24/£36/£80 chart values; only its new80%/91% annotations are additional rows. Repeated£100 legend descriptions are not extra rows.
- Richest30% "lose a similar amount" is not an exact printed cash number; no negative£13 was inferred.
-30% subgroup labels,5–15 bus-travel age eligibility, dates, axis ticks, years and0% chart origins are conditions/context, not separate scored estimates.
- Other temporary announcements on p15 (food tariffs, family-days-out VAT, free bus travel) have no printed cost/effect values, apart from the£2 bus fare parameter staged.
- Gas-standing-charge reform's average "no give-away" and "does not change overall costs" are qualitative; no numerical zero was invented. Its future electricity counterpart has no printed effect.
- No data download was identified within the PDF; the collection/event fetches were blocked as documented above.

Potential contradictions/limits: the package's modelled full electricity-VAT period includes already-announced relief, despite being discussed beside Budget measures. This is why the package and full-period electricity rows have proposed scopes. The printed£140 headline is rounded; do not derive a different total from a plotted stack. Gas reform has unspecified implementation year and geography. The positive1% magnitude is explicitly a decrease. No numerical difference was detected between TW_0 and TW_1.

Component spot check: deterministic random sample seed230,10 of21 rows, reopened directly from TW_1 PDF text; labels and direction were also checked against rendered pp4,5,7,8,14. One-based component rows1,6,7,8,10,11,14,15,18,19: p2 3.8% CPI inQ12027; p3 0% VAT October2026–June2027; p3 £5bn positive Exchequer cost across nine months; p4 £140 nine-month household support; p4 £36 VAT label; p4 £80 payment label (all in2026-27 prices); p7 around35% offset→0.35; p8 current£108 annual gas charge; p8 40% worse off→0.4 losing share; p8 poorest30% gain£13 per year, date unspecified/publication marker2026. All values found verbatim. The21 component rows pass row_problems with0 problems using UV_CACHE_DIR=/tmp/ab2026-ifs-uv-cache (default uv cache is outside the sandbox).


## Bee Boileau public services deck

Primary: *Spending on public services: the Achilles’ heel?*, 29 October 2026,
https://ifs.org.uk/system/files/2026-10/Spending-on-public-services-the-Achilles-heel-BB.pdf.
Fresh direct fetch 2026-10-29 15:43:43Z with the required Safari User-Agent;
157,838 bytes, sha256 `7403ecc0641b23f5ffc0cb28f67435dbd1b8df6b124874ffae7ae7f75e357aa6`.
The coordinator's assigned local copy and fresh copy are byte-identical. Read with
`pdftotext -layout`; visually inspected all 13 slides and the slide 7/9 data labels.
No raster-only numeric table was missed.

Coverage: 28 rows, all `measure_key: null` (one has the proposed package below).
By slide: 3:1, 4:4, 5:1, 7:6, 8:1, 9:10, 10:3, 11:2.
The figures are 21 own arithmetic calculations/scenario assumptions and 7 restated
announced policy/target/reserve figures. No exact registered AB2026 measure is assigned.

The first lane's one proposed key here, for the £1.2bn a year of DIP funding, went with that row, which the addendum dropped as an allocation (see "Keys the addendum changed" above). The rule 8 drops also removed slide 4's and 8's targets, slide 5's financing and the two scenario inputs on slides 7 and 9, so the deck now has 21 rows.

Metric proposals reuse `spending_pressure`, `forecast_spending_change` and
`real_spending_growth` from AB2025. The historical one-percentage-point revision uses `real_spending_growth_revision`. New `reserve_allocated_share` means the
percentage of the specified day-to-day/capital reserve already allocated over
its printed multi-year window. No new unit or baseline proposal.

`arithmetic` is the IFS's own scenario/growth calculation, or an announced target
restated without a named model; the £1.2bn funding amount is marked restated with
`hmt_costing_obr_certified`. Restated rows name their government/DIP origin in
`note`; two announced reserve allocation shares are `administrative_fact`.
Real growth remains percent, growth revisions are percentage points, cash
amounts are GBP, and signs are as printed. Positive pressure means additional
spending required; negative growth is a real cut. There are no central-value
rows: IFS's scenarios are point estimates, never substituted for OBR forecasts.

The 2027–28 to 2030–31 chart rates are average annual real growth over the whole
interval: `growth_period` preserves that interval, and the row's fiscal period
is its terminal year, 2031. The reserve shares likewise retain their complete
allocation windows, ending 2028–29 and 2029–30 respectively. The published £1.2bn
and ~£1bn annual flows have no fiscal year: they carry a 2026 publication-date
snapshot, `time_basis: point_in_time`, `reference_date`, and medium confidence;
the rows do not claim these are 2026 annual outlays. The historical average
1-percentage-point growth revision since 2010 uses the same dated-snapshot
convention. Slide 4 states a calendar-2030 defence target, so that row has no fy;
slide 9 explicitly says 2030–31 and is recorded as fiscal. The difference in date
labels is preserved, not resolved by the harvest.

Not staged: slide 3's unlabelled growth bars and axis ticks; all dates, document
address numbers and slide enumeration; qualitative/unquantified claims; the
second occurrence of the identical 3%-of-GDP scenario annotation within slide 9.
Slide 7 and slide 9 repeated printed labels are retained at their separate
locators, and slide 9's two health bars are separate scenario observations.
The £1bn financing flow is explicitly investment/financing, not military
purchases, matching the slide's caution. The deck identifies no downloadable
data file or distributional chart. No public-services primary was unreached.

Validation: `row_problems` from the AB2026 checker, with registered keys and enums,
reported **28 rows, 0 row problems**. Full-family validation is recorded below. A full visual pass found no contradictory value.
The calendar/fiscal defence target wording and unspecified flow years above are
material limitations.

Deterministic random spot-check (seed 230, 1-based indices within the Boileau component):

| Row | Locator | Printed value | Normalized unit/value | Period check |
|---|---|---|---|---|
| 1 | slide 3 | £8 billion | GBP 8,000,000,000 | FY2030–31 |
| 6 | slide 5 | ~£1bn per year | GBP 1,000,000,000 | no year printed; dated snapshot, medium |
| 10 | slide 7 | 1.7% | percent 1.7 | average 2027–28 to2030–31 |
| 14 | slide 9 | 0.9% | percent 0.9 | average 2027–28 to2030–31 |
| 16 | slide 9 | £9 billion | GBP 9,000,000,000 | interval ends FY2030–31 |
| 18 | slide 9 | 2.7% | percent 2.7 | yellow health bar, average interval |
| 22 | slide 9 | -0.9% | percent -0.9 | green other-departments bar, average interval |
| 23 | slide 9 | -2.1% | percent -2.1 | yellow other-departments bar, average interval |
| 24 | slide 10 | £28 billion | GBP 28,000,000,000 | FY2030–31 |
| 25 | slide 10 | 1 percentage point | percentage_points 1 | historic since2010, dated snapshot |

For every sampled row the primary PDF was reopened with `pdftotext -f/-l` and the
number/string, sign, unit and context checked; slide 7/9 labels were also viewed
at full-page resolution. All printed value strings matched. No bar reading or
arithmetic derived by the harvest was used.


## Stuart Adam: Tax measures

18 rows from one six-slide PDF. Direct fetch with the required browser User-Agent,
2026-10-29 15:43:43Z; 133,005 bytes;
sha256 `6792dc448f40d34f174b6a3c839863b5c969a7334263f5d6b539be62a0428bb8`.
The fetched bytes match the assignment's local copy. Text read with
`pdftotext -layout`; all six slides rendered and visually read as a safeguard
against raster text. Slides 2–6 have no embedded raster images and all printed
numbers are in the text extraction. No distributional chart or data download
is linked inside this deck.

Rows by registered key: `ab2026__package_total_tax_policy_decisions` 1;
`ab2026__writing_down_allowance_12pc_and_fya_50pc` 1;
`ab2026__distributions_framework_modernised` 1;
`ab2026__badr_lifetime_limit_500000` 1;
`ab2026__founders_relief_cgt` 6;
`ab2026__business_rates_sbrr_rhl_thresholds_raised` 3;
`ab2026__electricity_vat_zero_rate_to_july_2027` 1; null 4.
### Proposed measure scopes

Superseded on 3 November (see "Keys the addendum changed" above): the self-assessment timing and the compliance-staff and debt-collection figures are line 45 components, matched to Table 6.3's items by value, and the savings and property income figure uses `ab2026__package_property_and_savings_income_rates`. Rule 8 dropped this deck's six parameter rows (the Founders' Relief rate, comparator and limit, the RHL rateable values and the 0% VAT rate), so it now has 12 rows.

### Conventions and metric proposals

All monetary figures preserve printed signs. Revenue-raising amounts are
positive yields; the Founders' Relief £0.3bn is a positive cost, explicitly
labelled as such. Amounts expressed in £bn/£m are multiplied by 1e9/1e6.
Tax rates remain percent. All quoted excerpts have fewer than 15 words and
contain their exact `value_raw`.

The HMT-certified Budget costings are `restated` with
`source_model: hmt_costing_obr_certified`; rates and eligibility parameters
are `restated` announced-government design with `administrative_data`.
The deck does not cite a source for its beneficiary count or gain calculations;
these are presented as IFS `own`, `arithmetic`. Its maximum business-rate
saving is also IFS arithmetic. `point` is used for printed single estimates;
the £12,000–£21,000 benefiting-property range uses range endpoints. No
uncertainty range is inferred. There are no rows labelled `central` in this deck.

- Reused `tax_threshold_level` (GBP): the £10m cap on qualifying Founders'
  Relief gains and the lower/upper rateable-value bounds identifying RHL
  properties benefiting from higher relief thresholds.
- Proposed `statutory_tax_rate` (percent): the statutory 10% Founders' Relief rate,
  its current 24% standard-rate comparator, and the temporary 0% electricity
  VAT rate. These are statutory parameters, not effective marginal rates.
- Proposed `taxpayer_gain` (GBP): the printed maximum £1.4m gain per
  Founders' Relief beneficiary, with the maximum recorded in conditions.
- Proposed `business_rates_bill_change` (GBP): maximum annual bill saving
  to an RHL property from the higher relief thresholds, £7,146 in 2027-28;
  positive means a gain to the business.

Fiscal-year impacts use their end year. The BADR £0.3bn bullet omits the
year; 2031–32 is inherited from the preceding slide's final-year comparison
and its adjacent Founders' Relief bullet. That row has medium parse confidence
and explains the inheritance. The annual count of 600 beneficiaries and
average £500,000 gain have no year printed; they use an annual 2026
publication-year marker, with explicit `period_assignment` and `horizon`
conditions and medium confidence. This marker does not claim the relief operated in 2026.
Unspecified-year parameters and the maximum £1.4m gain use point-in-time
2026 as announcements, with no fiscal-year condition. No baseline proposal.

### Omissions and source issues

- No effective marginal rates, distributions or unlabelled charts occur in
  this deck. No amounts are inferred from qualitative bullets.
- Dates and durations are descriptive scope rather than numerical impact
  rows: the bank surcharge's 15-month period; two years of business-rate
  discounts; the 2029 revaluation; April 2028 income-tax revenue devolution.
  The devolution slide prints no quantified spending or revenue amount.
- The title slide prints “28 October 2026”, despite the assignment describing
  the 29 October briefing and PDF metadata showing creation/modification on
  29 October. Publication date follows the printed cover (2026-10-28); the
  contradictory date evidence is preserved here, not silently corrected.
- IFS's £1.1bn combined savings/property yield is retained verbatim. The
  corresponding Table 6.1 line-61/62 final-year amounts are £455m and £590m,
  totalling £1.045bn. Different rounding/aggregation could explain the
  displayed £1.1bn; no correction or derivation is staged.
- The £1bn HMRC compliance/debt-collection figure is narrower than line 45's
  full £3.160bn. It is not treated as a contradictory costing of the full package.

### Verification

The 18 individual rows pass `row_problems` from the harvest contract with
zero problems. All 18 short quotes were matched against whitespace-normalised
`pdftotext -layout` output and visually checked on the rendered slides.
Random spot-check seed 230 selected the following ten local rows. Each was
reopened at its slide and checked for exact value, sign, unit and period:

| Local row | Slide | Printed value | Sign/basis | Period |
|--:|--:|---|---|---|
| 1 | 2 | £7bn | positive Exchequer yield, GBP | 2031-32 |
| 6 | 2 | £0.8bn | positive Exchequer yield, GBP | 2031-32 |
| 7 | 3 | £0.3bn | positive Exchequer yield, GBP | inherited 2031-32, disclosed |
| 8 | 3 | £0.3bn | positive Exchequer cost, GBP | explicit 2031-32 |
| 10 | 3 | 24% | standard statutory rate, percent | 2026 context marker |
| 11 | 3 | £10m | qualifying gains cap, GBP | 2026 announcement marker |
| 13 | 3 | £1.4m | maximum positive taxpayer gain, GBP | 2026 announcement marker |
| 14 | 3 | £500,000 | average positive beneficiary gain, GBP | annual, year unspecified; 2026 marker disclosed |
| 15 | 4 | £12,000 | lower rateable-value bound, GBP | 2027-28 |
| 16 | 4 | £21,000 | upper rateable-value bound, GBP | 2027-28 |


## Final family verification

The required command, with its uv cache confined to the ignored family primaries
directory, completed successfully:

```sh
UV_CACHE_DIR=.ab2026-primaries/uk_ifs_ab2026/uv-cache PYTHONPATH=. uv run -q python pipeline/ab2026_harvest_contract.py sources/harvest-uk-ab2026-2026-10-29/uk_ifs_ab2026
```

```text
sources/harvest-uk-ab2026-2026-10-29/uk_ifs_ab2026: 106 rows, 0 problems
```

Re-running `stage.py` produced the same gzip SHA256 before and after:
`4f0c9cd197d970486608ea093bf3822ae1d92fa56ebc4a2ac1fae3086430b1cb`.
68 text-row value_raw strings were also matched at their exact PDF slide
locators. Sixty-five quotes match the whitespace-normalised extraction directly;
three Boileau chart annotations interleave with other columns in pdftotext and
were confirmed against rendered slides 7 and 9. All 38 embedded fiscal-table
cells were independently checked visually. All quotes have fewer than 15 words
and contain value_raw.

The final family random sample uses seed 230, ten of 106 rows, one-based gzip
indices. Each primary was reopened at the locator and its number, sign, unit and
period checked. All ten passed; unspecified dates are disclosed markers, not
confirmed implementation dates.

| Row | Primary / locator | Value and sign | Normalized unit | Period checked |
|--:|---|---|---|---|
| 3 | Stockton, slide 7, current budget deficit | -0.4, surplus direction | percent of GDP | FY2029-30 / 2030 |
| 21 | Stockton, slide 7, PSND ex BoE year-on-year change | 3.4, positive change | percent of GDP as printed | FY2026-27 / 2027 |
| 39 | Stockton, slide 8, forecast risk annotation | roughly 1 in 4 | share 0.25 | Spring 2027 inference disclosed |
| 56 | Wernham, slide 8, gas reform winners | 60%, better off | share 0.60 | implementation unspecified; 2026 publication marker |
| 69 | Boileau, slide 7, Health and Social Care | 2.7%, positive real growth | percent | annual average FY2027-28 to FY2030-31 / 2031 |
| 85 | Boileau, slide 10, historical top-ups | 1 percentage point increase | percentage_points 1 | historical since 2010; 2026 snapshot |
| 87 | Boileau, slide 11, day-to-day reserve | 40%, already allocated | percent | FY2027-28 to FY2028-29 / 2029 |
| 91 | Adam, slide 2, business investment allowances | £1.1bn, positive yield | GBP 1,100,000,000 | FY2031-32 / 2032 |
| 93 | Adam, slide 2, HMRC staffing/debt collection | £1bn, positive yield | GBP 1,000,000,000 | FY2031-32 / 2032 |
| 106 | Adam, slide 5, electricity VAT | 0%, statutory rate | percent 0 | announcement at publication in 2026; no fy |

Registered-key scope review covered every non-null row:

| Registered key suffix (all prefixed ab2026__) | Table 6.1 line | Printed scope checked |
|---|--:|---|
| household_energy_payment_100_bands_a_to_d | 1 | one-off payment and all-household mean/receipt estimates |
| fuel_duty_5p_cut_extended_and_rpi_rise_deferred | 3 | 5p cut/freeze extension and its Jan-Jun average support |
| bus_fare_cap_2_england_outside_london_2027 | 4 | £2 fare parameter; registry timing/geography explicitly sourced in note |
| founders_relief_cgt | 26 | relief costing, design, beneficiary count and gains |
| distributions_framework_modernised | 49 | reclassification of capital gains as dividends |
| badr_lifetime_limit_500000 | 60 | further cut to BADR |
| business_rates_sbrr_rhl_thresholds_raised | 13 | benefiting rateable-value range and maximum saving from threshold increase |
| writing_down_allowance_12pc_and_fya_50pc | 58 | business investment allowances |
| electricity_vat_zero_rate_to_july_2027 | 2 | Adam statutory zero-rate parameter, no full-period gain/cost attached |
| package_total_tax_policy_decisions | total | net Budget tax rise in final forecast year |

Wernham's full-period VAT *impact* uses a proposal because it includes prior
relief; Adam's zero-rate *parameter* is directly stated for the measure and is
not a costing of the full period. All broader or unidentified packages use null
measure_key with proposals. Source issues are preserved: Adam's cover date,
savings/property rounding, Boileau's calendar/fiscal target wording and undated
flows, Wernham's undated gas reform, and Stockton's uncited attribution. None
was silently corrected.

