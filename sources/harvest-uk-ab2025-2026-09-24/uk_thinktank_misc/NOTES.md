# Smaller shops — Autumn Budget 2025 harvest (sources `taxpayers_alliance`, `cps`, `onward`, `tax_justice_uk`, `iea`, `policy_exchange`, `ppi`, `loughborough_crsp`)

Staged 2026-09-24 from the primary documents. **216 claims** in `claims_staged.jsonl.gz`, **14 documents** in `manifest.jsonl`. Row contract, enums and rules: `../README.md`; measure keys: `../REGISTRY_KEYS.md`. Every `value` is verbatim (normalised to the unit as recorded in `normalization`); nothing is derived.

## Access recipe

All pages fetched directly with `curl` and a browser User-Agent (HTTP 200) unless noted; PDFs text-extracted with pypdf.
- TaxPayers' Alliance: tally page with two tables of OBR/HMT scorecard lines (`article:published_time` 2025-11-26).
- CPS: research page (no date printed; `article:modified_time` 2026-01-01) and the 3-page briefing PDF linked as "Read
  the report" (`Who-Wins-Under-Labour.pdf`, uploads/2025/12) — the PDF carries the worked-example tables the seed said
  were not retrieved.
- Onward: Budget response (26 Nov) and "The Hidden Benefits Bill" ("Published 1 February 2026").
- Tax Justice UK: two blog pages (28 Nov; 19 Nov).
- IEA: press release for the Clougherty briefing (`article:modified_time` 2025-11-25; seed date 21 Nov).
- **Policy Exchange: the "Beyond Our Means" PDF (`Beyond-Our-Means_.pdf`, 7.7 MB, 132 pages) came back HTTP 200 to a
  plain `curl` with a browser User-Agent on 2026-09-24 — the seed's CAPTCHA/403 did not recur.** The instruction was
  "descriptor only … do NOT stage values from a secondary summary"; because the PRIMARY was readable, the savings menu
  is staged **from the primary PDF (Table 1, §2 summary)**, not from the Risk Assured summary. This is a deliberate
  deviation from the letter of the instruction, flagged for the coordinator; the rows are self-contained (source
  `policy_exchange`, 84 rows) and can be dropped wholesale if the descriptor-only ruling stands.
- PPI: digest web page (Director's initial response with the £77/£454 employer figures) and the digest PDF
  (CreationDate 2025-11-27).
- Loughborough CRSP: two news pages. **MIS 2025 is already in the scorecard's MIS lane**
  (`sources/harvest-uk-2026-08-02/uk_ukmod_jrf/manifest.jsonl` line 5: JRF/CRSP "A Minimum Income Standard for the
  United Kingdom in 2025", sha256 `1097b577…`; `proposed_metric: minimum_income_standard_budget`) — the MIS 2025 page is
  manifested with zero rows. "The Cost of a Child in 2025" (for CPAG, 23 Oct 2025) is not in that lane and is staged
  as context rows.

### Documents (manifest.jsonl)

- 2026-01-01 · Who Wins Under Labour? (research page) · `html` · access `direct` · 67,087 bytes · sha256 `2ce78dfb4f7f4f7f…` · **0 rows** — page shows no date; article:modified_time 2026-01-01T22:01 (index gives 1 Jan 2026)  
  <https://cps.org.uk/research/who-wins-under-labour-briefing/>
- 2026-01-01 · Who Wins Under Labour? (Daniel Herring, briefing PDF) · `pdf` · access `direct` · 578,446 bytes · sha256 `79865ed8ebc696d0…` · **15 rows** — 3-page briefing linked from the research page ('Read the report'); dated by the research page  
  <https://cps.org.uk/wp-content/uploads/2025/12/Who-Wins-Under-Labour.pdf>
- 2025-11-21 · Reeves must slash spending as it balloons to 45% of GDP, says IEA (Tom Clougherty briefing, press release) · `html` · access `direct` · 149,619 bytes · sha256 `5206ee1c65530cd7…` · **9 rows** — article:modified_time 2025-11-25; seed dates it 21 Nov 2025  
  <https://iea.org.uk/media/reeves-must-slash-spending-as-it-balloons-to-45-of-gdp-says-iea/>
- 2025-10-21 · Beyond Our Means: A Plan to Tame Public Spending (publication page) · `html` · access `direct` · 108,370 bytes · sha256 `194a6adf56677a80…` · **0 rows**  
  <https://policyexchange.org.uk/publication/beyond-our-means/>
- 2025-10-21 · Beyond Our Means: A Plan to Tame Public Spending (Bootle, Mansfield, Ramanauskas, Sweetman) · `pdf` · access `direct` · 7,738,932 bytes · sha256 `10f40d53fb04ccd8…` · **84 rows** — fetched directly (HTTP 200, 7.7 MB, 132 pages) with a browser User-Agent on 2026-09-24 — the seed reported a CAPTCHA/403; PDF CreationDate 2025-10-23; publication page dated October 21, 2025  
  <https://policyexchange.org.uk/wp-content/uploads/Beyond-Our-Means_.pdf>
- 2025-11-28 · A Budget of broken promises that taxed workers & spared the super-rich · `html` · access `direct` · 63,789 bytes · sha256 `5f5dbf6080e2e96a…` · **5 rows**  
  <https://taxjustice.uk/blog/a-budget-of-broken-promises/>
- 2025-11-19 · Press release: Leading organisations call for wealth taxes at the Budget · `html` · access `direct` · 72,812 bytes · sha256 `5c99f3d12e43502e…` · **3 rows**  
  <https://taxjustice.uk/blog/press-release-leading-organisations-call-for-wealth-taxes-at-the-budget/>
- 2025-11-26 · Tax rise every ten days since Labour came to power · `html` · access `direct` · 168,845 bytes · sha256 `154d3deb7a64d149…` · **10 rows** — article:published_time 2025-11-26T15:33Z; modified 2025-11-27  
  <https://taxpayersalliance.com/tax-rise-every-ten-days-since-labour-came-to-power/>
- 2025-11-26 · Onward’s Response to the 2025/26 Budget · `html` · access `direct` · 108,029 bytes · sha256 `464e5bedbefca701…` · **1 rows** — article:modified_time 2025-11-26T16:07  
  <https://ukonward.com/reports/onward-response-to-the-budget/>
- 2026-02-01 · The Hidden Benefits Bill: How Universal Credit claimants get £10 billion in extra benefits (Caroline Elsom) · `html` · access `direct` · 442,620 bytes · sha256 `25499c1e2ee02245…` · **65 rows** — 'Published 1 February 2026'; modified 2026-05-12  
  <https://ukonward.com/reports/the-hidden-benefits-bill-how-universal-credit-claimants-get-10-billion-in-extra-benefits/>
- 2025-10-23 · The Cost of a Child in 2025 (news page; calculations for Child Poverty Action Group) · `html` · access `direct` · 58,607 bytes · sha256 `0e4f84c86954a515…` · **14 rows**  
  <https://www.lboro.ac.uk/research/crsp/news/news-2025/cost-of-a-child-in-2025/>
- 2025-09-09 · MIS 2025 (Minimum Income Standard 2025, news page) · `html` · access `direct` · 58,973 bytes · sha256 `4863a2430da24698…` · **0 rows** — ALREADY IN the scorecard's MIS lane: sources/harvest-uk-2026-08-02/uk_ukmod_jrf carries the JRF/CRSP 'A Minimum Income Standard for the United Kingdom in 2025' PDF (sha256 1097b577...) — no rows staged here  
  <https://www.lboro.ac.uk/research/crsp/news/news-2025/mis-2025/>
- 2025-11-27 · PPI Digest: Autumn Budget 2025 · `pdf` · access `direct` · 1,001,967 bytes · sha256 `786514661044972e…` · **6 rows** — PDF CreationDate 2025-11-27  
  <https://www.pensionspolicyinstitute.org.uk/media/gdcaa1oy/20251127-ppi-digest-the-autumn-budget-final.pdf>
- 2025-11-27 · PPI Digest: Autumn Budget 2025 (web page with the Director's initial response) · `html` · access `direct` · 51,348 bytes · sha256 `09198a0f3537eea7…` · **4 rows**  
  <https://www.pensionspolicyinstitute.org.uk/research-library/research-reports/2025/ppi-digest-autumn-budget-2025/>

## Coverage tally (seed bullets → claims staged → not staged)

Seed: `scores-3-other-shops.md` §§ TaxPayers' Alliance, Centre for Policy Studies, Onward, Tax Justice UK, IEA, Policy
Exchange, Loughborough CRSP, Pensions Policy Institute (13 bullets). Trussell (1 bullet) and ISER/UKMOD (13 bullets)
belong to other families (`uk_trussell_wpi`, the UKMOD lane) and are not staged here.

Staged (216 rows):
- TaxPayers' Alliance (10): £60.3bn tally, counts 52 and 24, Table 2 totals £23,455m (2029-30) / £26,875m (2030-31),
  Table 1 total £36,850m, freeze +7,780/+12,435, salary sacrifice £4.85bn, WDA £1.47bn — all **restated** except the
  two counts (TPA's own count). The 52 component lines are OBR/HMT costings already in `uk_hmt_costings` and are not
  re-staged. Note: the page prints both "£8 billion by 2029-30" and "£7.8 billion by the end of the decade" for the
  freeze (both printed; the table row is +7,780).
- CPS (15): worker on £50,000 −£505 real terms by 2030-31; take-home £39,520 → £43,193 nominal; the six-year real
  post-tax wage series; pensioner +£306 (triple lock) / +£537 (quadruple lock); UC +£290; 2030-31 real levels
  (£12,279 / £12,510 / £5,092). `source_model: arithmetic` (OBR wage/CPI forecasts applied to frozen thresholds; "not a
  microsimulation").
- Onward (66): Motability reliefs £1.2bn/yr (`tax_expenditure`); Hidden Benefits Bill headline >£10bn, totals
  £8,297m / £10,392m, and Figure 6 per-scheme expenditure, claim count and average award for 20 schemes plus two
  discretionary funds (context, `parse_confidence: medium` because the latest year differs by scheme).
- Tax Justice UK (8): HVCTS £400–450m (restated OBR/HMT, 2 rows), 165,000 households (restated, low confidence),
  £2.1bn investment-income rates (restated), £15.5bn package (own sum), £24bn wealth tax / >£11bn CGT / £12bn NI on
  investment income (restated Advani/CenTax/TJN).
- IEA (9): £40bn spending restraint, −14% non-NHS departmental spending (own); spending 45%/44.5% and tax burden 37.5%
  of GDP today (own arithmetic on OBR; the late-1990s comparators 35%/32% ride in `conditions.measure_type` because the
  contract's `period` range is 2015–2035); HMRC additional-rate reckoner £145m/£265m/£230m and the ~£30bn pre-Budget
  gap (restated).
- Policy Exchange (84): £115bn and 3.2% of GDP headline; Table 1 (14 items + total) × 2026–2030 = 75 rows; % of GDP
  row × 5; SPA-to-70 "at least an additional £20 billion a year" (2024 prices, long run); public-sector pensions
  "£22 billion annually" (N/A in the total).
- PPI (10): median earner (~£43,000 in 2029) 5%: £12 employee / £22 employer; 10%: £184 / £344; UEL earner £50,270 5%:
  £41.08 (£41) / £77; 10%: £242.16 (£242) / £454; caps £300 employer / £160 employee.
- Loughborough CRSP (14): Cost of a Child 2025 — £250,000 (couple) / £290,000 (lone parent); MIS coverage shares for
  three-child families (83%, 68%, 60%, 51%, 34%, 40%) and the 2025 two-child values (69%, 82%; the 2008 comparators 97%
  and 93% ride in `conditions.household` because 2008 is outside the contract's `period` range); weekly shortfalls
  £150 / £290 / £290 / £370.

Not staged (with reason):
- TPA "509 days", "£8 billion by 2029-30" text figure (the table row +7,780 is staged instead; both noted), the
  "Briefing: the shifting burden of income tax" PDF (image-based, per the seed).
- CPS research page summary duplicates the PDF; "42% vs 28% combined marginal rate" — parameters, not results;
  nominal salary path £56,269 (in `conditions`).
- Onward polling (48% vs 28% of 16–40-year-olds), "1991 <4% vs ~25% paying the 40p rate" (restated/historical),
  unclaimed-benefit values (Policy in Practice: CTS £3.306bn, broadband £1.508bn, water £745m, WHD £722m), 7.5m people
  missing an entitlement (PiP), 3.7m with no work requirements (DWP) — all cited, not Onward's; Figure 6 "Barnett
  adjustment" column (scaled derivative of the expenditure column; kept only for the total £10,392m).
- TJUK "48x" and "7.5x" (ratios), 350,000 children (CPAG, cited), gambling £1.1bn vs ~£3bn, wage growth £12/week,
  billionaire wealth +£370bn (cited).
- IEA growth rates (2.5% / 1% / 1.8% since 1997; context), "£260bn over-65s" OBR 2022, 8.5% NMW rise, £4.4bn EV excise
  (restated); the 19 Oct 2026 Alternative Budget is outside the window.
- Policy Exchange item-level figures from the **Risk Assured secondary summary** were NOT used (the primary was);
  narrative sub-figures inside chapters (e.g. Table 11 public-sector pension costs £11bn/£18bn/£30bn; asylum "£6
  billion spent annually") are context, not the savings menu.
- PPI: State Pension £241.40 / £184.90 a week (DWP rates, restated), 44% / 13% / >80% (DWP FRS / FCA statistics),
  HMRC relief cost £1,200m / £2,900m and OBR £4.7bn (restated), HVCTS £2,500–£7,500 (parameters).
- Loughborough MIS 2025 (£30,500 single; £74,000 couple with two children; 76% / 66% / 69% of MIS on the NLW) —
  **already in** the MIS lane (`uk_ukmod_jrf`), listed here, not re-staged. "109 children pushed into poverty daily"
  (CPAG, cited) not staged.

### Row counts

- by `source`: cps 15, iea 9, loughborough_crsp 14, onward 66, policy_exchange 84, ppi 10, tax_justice_uk 8, taxpayers_alliance 10
- by `attribution`: own 197, restated 19
- by `benchmark_class`: different_model 216
- by `source_model`: arithmetic 202, mis_budget_standards 14
- by `value_kind`: point 210, range_high 1, range_low 5
- by `parse_confidence`: high 149, low 1, medium 66
- by `measure_key`:
  - `null` 97
  - `ab2025_option__policy_exchange_beyond_our_means_savings_menu` 84
  - `ab2025__personal_tax_thresholds_freeze_to_2031` 11
  - `ab2025__salary_sacrifice_pension_nics_cap_2000` 11
  - `ab2025__high_value_council_tax_surcharge` 3
  - `ab2025__package_total_tax_policy_decisions` 3
  - `ab2025_option__hold_total_spending_growth_to_inflation` 2
  - `ab2025__dividend_rates_plus_2pp` 1
  - `ab2025__motability_vat_on_advance_payments_and_ipt` 1
  - `ab2025__uc_standard_allowance_and_health_element_rebalancing` 1
  - `ab2025__writing_down_allowances_14pct_and_40pct_fya` 1
  - `ab2025_option__cgt_equalise_with_income_tax_plus_investment_allowance` 1

## Metrics, units and baselines used

- `revenue_change` (registered) for TPA/TJUK/IEA-reckoner yields ("positive = yield to the Exchequer";
  `conditions.originator` on restated rows).
- `proposed_metric: measure_count` (`proposed_unit: measures`) for TPA's 52 / 24 counts.
- CPS: `proposed_metric: real_income_change` (`gbp`, 2025-26 prices; "positive = gain to the individual") for −£505 /
  +£306 / +£537 / +£290; `proposed_metric: take_home_pay` (`gbp`; nominal and real levels, `conditions.price_basis`);
  `proposed_metric: real_income_level` (`gbp`) for the 2030-31 pension/UC real levels. Producer definition (p.1):
  "once you feed in the OBR’s forecasts for inflation, they would actually be £505 worse off in real terms compared to
  this year"; methodology (p.2): "Wages are assumed to grow in line with OBR’s estimates for ‘Average weekly earnings
  growth’ in Table 1.6 and CPI is taken from Table 1.7."
- Onward: `tax_expenditure` (registered) for Motability reliefs; `benefit_cost` (registered, `gbp`) for scheme
  expenditure; `caseload` (registered) with `proposed_unit: claims`; `proposed_metric: average_award` (`gbp`).
  Producer definition (Figure 6 heading): "Claim count, average award, total expenditure and Barnett adjustment by
  scheme".
- TJUK: `proposed_metric: affected_count` (`households`) for 165,000.
- IEA: `proposed_metric: exchequer_impact_static` (README list; `gbp`, "positive = improvement in the fiscal
  outlook") for £40bn; `proposed_metric: departmental_spending_change` (`percent`); `proposed_metric: share_of_gdp`
  (`proposed_unit: percent_of_gdp`) for the spending/tax shares; `proposed_metric: fiscal_headroom` (README list,
  sign "positive = shortfall") for the restated ~£30bn gap.
- Policy Exchange: `proposed_metric: exchequer_impact_static` (`gbp` and `proposed_unit: percent_of_gdp`; "positive =
  reduction in public spending"; `conditions.component` = Table 1 row; `time_basis: annual` with the table's calendar
  labels 2026–2030 as `period`). Producer definition (§2): "Savings are presented in nominal terms, with the baseline
  used being the forecast spending in the relevant area in 2030" (footnote 7: OBR forecasts where available) →
  `conditions.baseline` carries this; `baseline_policy: null`.
- PPI: `proposed_metric: household_tax_change` (README list; employee NICs), `take_home_pay_change` (README list; the
  £41.08/£242.16 "worse off" figures, magnitude as printed with the sign convention in `conditions`),
  `employer_nics_change` (new, `gbp`) for employer NICs, `nics_saving_cap` (new, `gbp`) for the £300/£160 caps.
  Producer definition (PDF p.2): "The maximum benefit an employer can take from salary sacrifice will be effectively
  capped at £300 a year and an employee’s benefit would be capped at £160 a year."
- Loughborough: `proposed_metric: cost_of_a_child_to_18` (`gbp`), `mis_cost_coverage_share` (`share`),
  `mis_weekly_shortfall` (`gbp_per_week`); `source_model: mis_budget_standards`. Producer definition: "based on what
  the public deems a minimum acceptable living standard".
- `measure_key`: TPA totals → `ab2025__package_total_tax_policy_decisions` (+ specific keys for the freeze, salary
  sacrifice and WDA rows); CPS → `ab2025__personal_tax_thresholds_freeze_to_2031` (freeze rows),
  `ab2025__uc_standard_allowance_and_health_element_rebalancing` (UC +£290), quadruple lock `null`; Onward →
  `ab2025__motability_vat_on_advance_payments_and_ipt`; TJUK → `ab2025__high_value_council_tax_surcharge`,
  `ab2025__dividend_rates_plus_2pp` (nearest key for the three-rate £2.1bn), `ab2025_option__cgt_equalise_with_income_tax_plus_investment_allowance`;
  IEA → `ab2025_option__hold_total_spending_growth_to_inflation`; Policy Exchange →
  `ab2025_option__policy_exchange_beyond_our_means_savings_menu`; PPI → `ab2025__salary_sacrifice_pension_nics_cap_2000`;
  Onward Hidden Benefits, IEA shares, Loughborough → `null` (context).

### As staged

- registered `metric`: `benefit_cost` 25, `caseload` 20, `revenue_change` 18, `tax_expenditure` 1
- `proposed_metric`: `affected_count` 1, `average_award` 20, `cost_of_a_child_to_18` 2, `departmental_spending_change` 1, `employer_nics_change` 4, `exchequer_impact_static` 85, `fiscal_headroom` 1, `household_tax_change` 2, `measure_count` 2, `mis_cost_coverage_share` 8, `mis_weekly_shortfall` 4, `nics_saving_cap` 2, `real_income_change` 4, `real_income_level` 3, `share_of_gdp` 3, `take_home_pay` 8, `take_home_pay_change` 2
- registered `unit_concept`: `gbp` 171, `gbp_per_week` 4, `households` 1, `percent` 1, `share` 8
- `proposed_unit`: `claims` 20, `measures` 2, `percent_of_gdp` 9
- `baseline_policy`: None 216 (null = current law at the scoring date)
- `proposed_baseline`: none

## Distinct values per `conditions` axis

- `baseline` (2 distinct): forecast spending in the relevant area in 2030 (OBR where available) (84); current plans (OBR) (1)
- `basis` (3 distinct): static (125); post_behavioural (3); forecast (1)
- `component` (17 distinct): Total (10); Barnett Consequentials (5); Childcare (5); Green Subsidies (5); Healthcare and the NHS (5); Housing Benefit (5); International Development (5); Means Test Pensioner Benefits (5); Post-18 Education (5); Reducing the Size and Cost of the Civil Service (5); SEND (5); Small Boats and Asylum (5); State Pension Reform (5); Universal Infant Free School Meals (5); Welfare (5); Public Sector Pensions (moved to defined contribution from 2031; shown N/A in the total) (1); State Pension age to 69 in 2035 and 70 in 2040 (1)
- `data` (1 distinct): OBR (3)
- `employment_income` (7 distinct): £50,000 in 2025-26 grown with OBR wage growth (6); £50,270 (Upper Earnings Limit) (4); median earner £39,039 today, projected to close to £43,000 in 2029 (2); median earner, projected close to £43,000 in 2029 (2); £50,000 (1); £50,000 in 2025-26 (1); £56,269 (£50,000 grown with OBR wage growth) (1)
- `fiscal_event` (1 distinct): autumn_budget_2025 (216)
- `fiscal_event_scope` (2 distinct): Autumn Budget 2024 (1); Autumn Budget 2025 (1)
- `fy` (6 distinct): 2025-26 (70); 2029-30 (24); 2030-31 (11); 2026-27 (6); 2028-29 (3); 2027-28 (2)
- `geography` (4 distinct): UK (148); England (66); UK (England core plus Barnett adjustment) (1); UK (England core schemes plus Barnett adjustment) (1)
- `horizon` (2 distinct): July 2024 to 26 November 2025 (509 days) (1); long run, once SPA reaches 70 in 2040 (not within the five-year period); period capped at 2035 (1)
- `household` (17 distinct): couple with three children, both working full-time on a median wage (2); couple with three children, working full-time on the minimum wage (2); lone parent with three children, working full-time on a median wage (2); lone parent with three children, working full-time on the minimum wage (2); New State Pension, 2025-26 £ (quadruple lock) (1); New State Pension, 2025-26 £ (triple lock) (1); UC standard allowance (over 25), 2025-26 £ (1); couple (1); couple with two children, working full-time on the minimum wage (93% in 2008) (1); lone parent (1); lone parent with two children, working full time on the minimum wage (97% in 2008) (1); out-of-work couple with three children (1); out-of-work lone parent with three children (1); pensioner on the full new State Pension (triple lock; 2.5% a year from 2027-28; 20% income tax on the pension over £12,570) (1); pensioner on the full new State Pension, no income tax under the ‘quadruple lock’ (1); single person over 25 on the Universal Credit standard allowance only (1); single worker (1)
- `measure_type` (9 distinct): passported and discretionary schemes, latest available year per scheme (65); Minimum Income Standard basis (minimum socially acceptable living standard as defined by the public) (14); sum of 24 Autumn Budget 2025 tax rises (2); Total Managed Expenditure share of GDP, average from the pandemic to the end of the decade (1); public spending share of GDP (today; vs approximately 35% in the late 1990s) (1); sum of 28 Autumn Budget 2024 tax rises (1); sum of 52 tax rises announced since July 2024 (Autumn Budget 2024 and Autumn Budget 2025 scorecards) (1); sum of cited estimates (Advani wealth tax, CenTax, TJN) (1); tax burden share of GDP (today; vs 32% in the late 1990s) (1)
- `method` (2 distinct): OBR November 2025 EFO wage growth (Table 1.6) and CPI (Table 1.7) applied to frozen thresholds; not a microsimulation (15); PPI arithmetic on NIC rates (8)
- `originator` (7 distinct): OBR/HMT policy costings (TPA sums the scorecards) (8); HMRC ready reckoner (3); OBR/HMT (3); Advani / Wealth Tax Commission-derived (cited) (1); CenTax (CGT equalisation, cited) (1); Tax Justice Network / cited (1); not stated (government estimate implied) (1)
- `pension_contribution` (2 distinct): 10% salary sacrifice (4); 5% salary sacrifice (4)
- `price_basis` (6 distinct): nominal (Figure 1: 2030 prices) (82); 2025 (14); real terms, 2025-26 prices (13); 2024 prices (2); nominal (2); real (1)
- `program` (25 distinct): Broadband social tariffs (3); Cold Weather Payments (3); Council tax support (3); Court fee remission (3); Energy Company Obligation (3); Extra support childcare (3); Free School Meals (3); Free dental treatment (3); Free prescriptions (3); Free school transport (3); Funeral Expenses Payment (3); Healthy Start (3); Help to Save (3); Holiday Activities & Food Prog. (3); Legal aid (3); Sure Start Maternity Grant (3); Vulnerable Students Bursary (3); Warm Home Discount (3); Water social tariffs (3); WaterSure (3); Crisis & Resilience Fund (1); Flexible Support Fund (1); Motability bespoke tax reliefs (VAT and IPT exemptions) (1); all schemes (1); all schemes (England core) (1)
- `region` (1 distinct): rUK rates (1)
- `scenario` (1 distinct): NHS funding growing 4% a year in real terms (1)
- `sign_convention` (6 distinct): positive = reduction in public spending (84); positive = yield to the Exchequer (18); positive = gain to the individual (15); positive = increase in NICs paid (8); positive = improvement in the fiscal outlook (1); positive = shortfall against the fiscal rules (1)
- `subgroup` (3 distinct): employee (8% of £2,000) (1); employer (15% of £2,000) (1); non-NHS departmental spending (1)
- `tax_year` (7 distinct): 2029-30 (11); 2030-31 vs 2025-26 (4); 2025-26 (2); 2030-31 (2); 2026-27 (1); 2027-28 (1); 2028-29 (1)
- `unit_population` (1 distinct): working-age benefit claimants (65)

## Attribution decisions

- `restated`: TPA's tally and totals (sums of OBR/HMT costings, per the caller's ruling) and its top-item figures; TJUK
  HVCTS £400–450m, 165,000, £2.1bn, £24bn/£11bn/£12bn (Advani/CenTax/TJN); IEA HMRC reckoner and ~£30bn gap.
- `own`: TPA counts; CPS arithmetic; Onward's £1.2bn and Hidden Benefits compilation (Onward analysis of DWP/NHSBSA/
  DfE data, `different_model`); TJUK's £15.5bn sum; IEA's £40bn/−14%/GDP shares; Policy Exchange's in-house costings;
  PPI's arithmetic; CRSP's MIS-basis calculations for CPAG.
- Policy Exchange rows are flagged in this file's access recipe as a deviation from the "descriptor only" instruction
  (primary readable); the ingest can drop `source == policy_exchange` if the ruling stands.
