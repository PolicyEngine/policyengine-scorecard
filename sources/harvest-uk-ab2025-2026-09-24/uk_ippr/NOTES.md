# uk_ippr — IPPR, Autumn Budget 2025 harvest (2026-09-24)

Source `ippr`. Engine: `landman_ttm` for tax-benefit-model outputs (gambling paper poverty figures,
Fairness first two-child row, Restoring security), `arithmetic` for the gambling-duty, property-tax,
fiscal-gap and Fairness-first revenue estimates. Restoring security's tables are Flourish embeds; the
UK total is the government's 450,000 (`conditions.calibration: government_450000`).

## Access recipe

- ippr.org `robots.txt` allows `*` (only /cpresources, /vendor, /.env, /cache disallowed). All article
  and press pages fetched directly, HTTP 200, browser User-Agent. The gambling report PDF is on
  files.ippr.org (no robots.txt). The property-tax technical appendix is served by a Craft
  `download-file?id=309669` link (content-type application/pdf, 1 page). PDFs text-extracted with pypdf.
- Restoring security: the public showcase pages https://public.flourish.studio/visualisation/26633633/
  and /26633699/ are JS shells (sha256 255d44c5… / 22dfecfb…, 15,125 bytes each) that load
  `visualisation/<id>`; the `_Flourish_data` block lives in the embed at
  https://flo.uri.sh/visualisation/<id>/embed, which is what the manifest hashes (`access: flourish`,
  `doc_type: flourish_json`). Column names, `number_format` settings and version numbers are recorded in
  the manifest note. flourish robots: `User-agent: *` allow-all, named AI crawlers disallowed; one fetch
  per page with a browser UA. Thumbnails were not needed.
- Every `quote` was machine-checked against the extracted text (for the Flourish rows the quote is the
  JSON cell `{"columns":["North East",20000]}` as it appears in the embed source).

## Coverage tally (seed bullets → rows)

- 6 Aug gambling paper — 5 seed bullets + the RESTATED list → 27 rows (PDF 25, press release 2):
  RGD 1.8 / £1.6bn SMF; MGD 0.9 / £880m / Table A2 72+685+6+68 = 858; GBD 0.5 / £450m SMF; total 3.2
  and "just over £3 billion"; two-child + benefit-cap package "around £3 billion", "around half a
  million", 1.6m restated, >450,000 today and 550,000 by the end of the decade; restated 115,000 /
  £60 a week / 69 % / DfE 100,000; own >£3,500 arithmetic; 25 % vs 14 % food insecurity (HBAI 2023/24).
  NOT staged: Appendix 1 Table A1 (hypothetical illustration of odds-worsening, not an estimate);
  Table 1 current duty receipts 2023/24 (HMG levels, second pass); the landing page repeats the summary
  (manifested, no rows).
- 14 Nov property-tax blog + appendix — 5 bullets → 45 rows: £3.9bn (page and appendix cell), "around
  £4 billion" from "roughly 3 million" households, top 10 %, 1 % overbanded, 10,000 rebanding requests;
  the appendix table in full (8 bands × current/proposed multiplier, average bill, average change;
  group rows A–D −2.70 % / 81.10 % / 20,165,770 / −£1bn, E, F–G 50 % / 8.60 % / 2,151,400, H 100 % /
  0.50 % / 147,540); SDLT £120m (summary) and £100m (body), £640m raised / £120m refunded restated;
  package "around £3 billion" (unkeyed package row); 2021 PPT: three in four, 600,000 homes, £3bn GDP.
  NOT staged: the multipliers as rows (they ride on the change rows as `current_band_d_multiplier` /
  `proposed_band_d_multiplier`); the "just under £4 billion" / "almost £4 billion" phrasings of the
  same figure; Onward / Fairer Share PPT designs (no numbers of IPPR's own).
- 19 Nov Fairness first — 10 bullets → 16 rows: fiscal gap £20–30bn and £10bn buffer; £3.9bn and the
  80 % cut; CGT "as much as £13 billion" and +4.6 % investment (restated); NICs partnerships £1.9bn and
  landlords £3bn (restated); gambling £3.2bn (own); BoE £22bn (restated level) and £5–8bn saving (own);
  freeze £7.5bn and 2p switch £6bn (restated); "half a million children" two-child (own, earlier).
  NOT staged: Figure 3 polling (image); the cliff-edge smoothing (no number); the band value thresholds
  (£1.5m / £770,000 — carried in reform_hint).
- 26 Nov press releases — 1 bullet → 4 rows (450,000 restated twice, 1.6m restated, 80 children a day).
- 4 Dec Restoring security — 2 bullets + restated → 26 rows: Table 1 (12 regions, 2026/27 % growth in
  mean income), Table 2 (12 regions, children lifted out), 450,000 (restated, the calibration target),
  >1.6m (restated DWP). NOT staged: Figure 1 scatter (regional poverty rates vs income gain — a third
  Flourish embed whose id is not on the page text; second pass).

## Corrections to the seed inventory

- Seed prints Table 1 with "+" signs ("+0.32%"); the Flourish data holds unsigned values (0.22 … 0.32)
  rendered with `number_format.n_dec 2` and `suffix "%"`, i.e. "0.32%"; the "+" is the page text's
  ("+0.32 per cent"). Values staged as printed in the data.
- Region labels differ between the two tables: "Yorkshire and The Humber" (Table 1) vs "Yorkshire &
  Humber" (Table 2); "Eastern" is used for the East of England in both. Staged as printed.
- The SDLT £120m (summary) vs £100m (body) discrepancy the seed noted is confirmed; both rows staged
  with `conditions.locator_note`.
- The technical appendix prints no year; the 2025-26 basis for the average bills is an inference (band D
  £2,280 equals the 2025-26 England average band D bill) and is recorded in `conditions.data`.
- Seed says the gambling paper's SMF-derived GBD figure is "SMF estimate adopted by IPPR": staged as
  `attribution: restated` (non-government producer) with the origin in conditions.

## Baselines

- `end_of_parliament_pre_ab2025` on the end-of-parliament two-child rows (Table 2 regions, the 450,000
  restatements in the 4 Dec blog and both press releases).
- `pre_ab2025` (the registered "two-child limit reinstated" world) on the 2026/27 Table 1 rows —
  removal vs retention in a single year; documented here because the brief names only the
  end-of-parliament label.
- Option rows (gambling, property, Fairness first) are against current law at the scoring date
  (`baseline_policy: null`).

## Attribution decisions

- own: IPPR's gambling arithmetic (RGD uprating, MGD Appendix 2, totals), the IPPR-TBM poverty rows
  (from Parkes et al 2025), the property appendix table, the SDLT estimates, the fiscal gap/buffer, the
  BoE saving, the 2021 PPT results, the regional splits in Restoring security.
- restated (37 rows): DWP/DfE/HMRC/HMT figures; SMF's £1.6bn and £450m; the Fairness-first figures
  IPPR repeats without stating a source (CGT £13bn and 4.6 %, NICs £1.9bn and £3bn, freeze £7.5bn,
  2p switch £6bn, BoE £22bn) — these are other producers' numbers, marked restated so the #86 rule
  drops them and the seed's "attributed to others" reading is preserved; Restoring security's UK
  450,000 (the calibration target); the appendix's current average bills and property counts.
- Package rows: gambling package total keyed on the gambling option with `conditions.component:
  package_total`; the two-child + benefit-cap rows keyed on the two-child option with
  `conditions.package_second_key`; the property package total (council tax + SDLT) has no single key
  → `measure_key: null`, `conditions.package_keys` lists both.

## Proposals (proposed_metric / proposed_unit) with the producer's definition

- `affected_share` (share): "roughly the top 10 per cent of properties"; "Around 1 per cent of homes in
  bands F-H"; "69 per cent of families affected are single parent families"; "25 per cent of children in
  larger families are food insecure"; appendix "% of properties in England".
- `affected_count` (households / children): appendix "Number of properties in England"; "roughly 3
  million higher-value households"; "10,000 rebanding requests"; DWP "1.6 million children".
- `average_council_tax_bill` and `average_bill_change` (gbp_per_household): appendix columns "Average
  bill" and "Average change" per band.
- `bill_change_pct` (percent): appendix "Proposed change %".
- `tax_revenue` (gbp, cumulative): "the UK surcharge has raised £640 million … around £120 million has
  been refunded".
- `homes_freed_up` (households): "free up an estimated 600,000 homes within five years".
- `fiscal_gap` (gbp): "The size of the fiscal gap … could plausibly be in the region of £20 to £30
  billion"; `fiscal_headroom` (gbp): "an additional £10 billion buffer against shocks".
- `apf_indemnity_losses` (gbp): "the £22 billion taxpayer losses at the Bank of England".
- `business_investment_level_effect` (percent): "increase overall investment by 4.6 per cent compared
  to a ‘no reform’ scenario".
- `benefit_loss_per_child` (gbp): "Affected families lose out by over £3,500 per on year on current
  rates".
- `poverty_entries_per_day` (children): "the two-child limit pushes 80 children a day into poverty".
- No proposed_unit is used; `gdp_level_effect` is carried in gbp ("add £3 billion to GDP in 2019
  values") rather than percent, flagged in the row note.

## Manifest (primaries fetched 2026-09-24, sha256 + bytes)

- 2025-08-06 · pdf · direct · `d785605b91d6d96d…` · 156,327 bytes · Reforming gambling taxation: How to lift half a million children out of poverty (Parkes, Kumar, O'Halloran)  
  https://files.ippr.org/production/Downloads/Reforming_gambling_taxation_August25_2025-08-04-143817_rtlt.pdf
- 2025-08-06 · html · direct · `ef98c919ad844a06…` · 67,931 bytes · Reforming gambling taxation (article landing page)  
  https://www.ippr.org/articles/reforming-gambling-taxation
- 2025-08-06 · html · direct · `f0b81d09c7786e79…` · 61,800 bytes · Reform gambling taxes to lift half a million children out of poverty, urges IPPR (press release)  
  https://www.ippr.org/media-office/reform-gambling-taxes-to-lift-half-a-million-children-out-of-poverty-urges-ippr
- 2025-11-14 · html · direct · `467147a4d3b3bc04…` · 81,327 bytes · Towards a fair and proportional property tax (Sriram, Jung)  
  https://www.ippr.org/articles/towards-a-fair-and-proportional-property-tax
- 2025-11-14 · pdf · direct · `3d0f9c62d1ad38bf…` · 60,837 bytes · Towards a fair and proportional property tax: Technical appendix (band multiplier table)  
  https://www.ippr.org/index.php/actions/tools/tools/download-file?id=309669
- 2025-11-19 · html · direct · `8ab83acd4a1ff55d…` · 89,541 bytes · Fairness first: How the budget can make life better and the economy stronger (Jung, Henry, Quilter-Pinner, Norris, Sriram, Narayanan, Hawkey, Ellis, Parkes)  
  https://www.ippr.org/articles/fairness-first-how-the-budget-can-make-life-better-and-the-economy-stronger
- 2025-11-26 · html · direct · `9fe7fd1feb608314…` · 58,790 bytes · Budget fires starting gun on living standards and ending unfair tax advantages - but must be first shot in war on bills, says IPPR (press release)  
  https://www.ippr.org/media-office/budget-fires-starting-gun-on-living-standards-and-ending-unfair-tax-advantages-but-must-be-first-shot-in-war-on-bills-says-ippr
- 2025-11-26 · html · direct · `907bb3a5a686aa27…` · 57,797 bytes · Scrapping two-child limit is landmark moment for children, says IPPR (press release)  
  https://www.ippr.org/media-office/scrapping-two-child-limit-is-landmark-moment-for-children-says-ippr
- 2025-12-04 · flourish_json · flourish · `389f4434e22fdba2…` · 273,461 bytes · Flourish visualisation 26633633 'Table 1' (Restoring security, Table 1: Growth in mean income from removing the two-child limit, 2026/27) — embed page carrying _Flourish_data  
  https://flo.uri.sh/visualisation/26633633/embed
- 2025-12-04 · flourish_json · flourish · `54e599dc39422874…` · 273,417 bytes · Flourish visualisation 26633699 'Table 2' (Restoring security, Table 2: Children lifted out of poverty by region) — embed page carrying _Flourish_data  
  https://flo.uri.sh/visualisation/26633699/embed
- 2025-12-04 · html · direct · `a5935e445773df19…` · 71,482 bytes · Restoring security: Understanding the effects of removing the two-child limit across the UK (Parkes, Kumar)  
  https://www.ippr.org/articles/restoring-security-understanding-the-effects-of-removing-the-two-child-limit-across-the-uk

## Row tally by publication and measure key

- 2025-08-06: 27 rows
- 2025-11-14: 45 rows
- 2025-11-19: 16 rows
- 2025-11-26: 4 rows
- 2025-12-04: 26 rows

- measure_key `None`: 32
- measure_key `ab2025__uc_child_element_remove_two_child_limit`: 27
- measure_key `ab2025_option__boe_apf_indemnity_or_reserves_remuneration_reform`: 3
- measure_key `ab2025_option__cgt_equalise_with_income_tax_plus_investment_allowance`: 2
- measure_key `ab2025_option__council_tax_bands_f_g_plus_50pct_h_plus_100pct_recycled_to_a_d`: 23
- measure_key `ab2025_option__fsm_extension_to_all_uc_families_england`: 1
- measure_key `ab2025_option__gambling_duties_consolidated_or_raised`: 15
- measure_key `ab2025_option__income_tax_plus_2p_employee_nics_minus_2p_switch`: 1
- measure_key `ab2025_option__nics_on_partnership_income`: 1
- measure_key `ab2025_option__nics_on_rental_income`: 1
- measure_key `ab2025_option__non_uk_resident_sdlt_surcharge_2_to_6pct`: 2
- measure_key `ab2025_option__personal_tax_threshold_freeze_two_more_years_to_2030`: 1
- measure_key `ab2025_option__proportional_property_tax_on_values_over_2m`: 3
- measure_key `ab2025_option__scrap_two_child_limit`: 6

## Attribution and class counts

- attribution: own 81, restated 37
- benchmark_class: administrative_fact 26, different_model 92
- source_model: administrative_data 24, arithmetic 57, dwp_policy_simulation_model 3, landman_ttm 32, survey_microdata 2
- baseline_policy: None 91, end_of_parliament_pre_ab2025 15, pre_ab2025 12
- value_kind: central 10, cumulative 2, point 97, range_high 3, range_low 6; time_basis: annual 4, fiscal_year 105, point_in_time 9; parse_confidence: high 93, low 1, medium 24

## Registered metrics and units used

- metric: average_weekly_benefit 1, caseload 1, gdp_level_effect 1, pct_change_after_tax_income 12, poverty_count_change 21, revenue_change 32, share_gaining 2
- unit_concept: children 25, families 1, gbp 40, gbp_per_household 16, gbp_per_week 1, households 7, percent 17, share 11

## Distinct values on every conditions axis

- `basis` (2): post_behavioural | static
- `calibration` (1): government_450000
- `component` (8): bands A-D cut by 2.7 per cent (recycled £1bn) | bands F-G +50%, H +100% (gross, before recycling) | bands F-H rise with slight A-D reduction (appendix text rounding of £3.9bn) | general_betting_duty_15_to_25_excl_horse_racing | machine_games_duty_to_50_excl_category_D | package_total | recycled to cut bands A-D by 2.7 per cent | remote_gaming_duty_21_to_50
- `council_tax_band` (11): A | A-D | B | C | D | E | F | F-G | F-H | G | H
- `count_unit` (1): properties (dwellings) in England
- `current_band_d_multiplier` (8): 0.67 | 0.78 | 0.89 | 1 | 1.22 | 1.44 | 1.67 | 2
- `data` (4): English council-tax band counts and 2025-26 average bills (technical appendix) | FRS 2021/22-2023/24 (three years pooled) | Gambling Commission industry statistics July 2025; SMF (Noyes 2025) 2024/25 estimates uprated by GGY growth | HBAI 2023/24
- `denominator` (3): all properties in England | families affected by the benefit cap | homes in bands F-H
- `fiscal_event` (1): autumn_budget_2025
- `fy` (4): 2023-24 | 2025-26 | 2026-27 | 2029-30
- `geography` (16): East Midlands | Eastern | England | England (council tax) and UK (SDLT surcharge) | London | North East | North West | Northern Ireland | Scotland | South East | South West | UK | Wales | West Midlands | Yorkshire & Humber | Yorkshire and The Humber
- `hardship_measure` (1): food insecure
- `horizon` (4): end of the decade | end_of_parliament | immediate ('overnight') | within five years
- `housing_costs` (1): ahc
- `income_concept` (1): mean household income (BHC/AHC and equivalisation not stated)
- `locator_note` (2): body-text figure; the summary bullet says around £120 million | summary bullet figure; the body text says around £100 million
- `machine_category` (5): B1 | B3 | B4 | C | total B1+B3+B4+C
- `measure_scope` (1): unkeyed
- `measure_type` (16): attributable_poverty | attributable_poverty_today | average amount capped per family | children affected by the two-child limit and benefit cap | children in households affected by the two-child limit | children living in households affected by the two-child limit | children pushed into poverty per day by the two-child limit (current policy flow) | cumulative receipts since introduction in 2021 | cumulative refunds to purchasers who later became UK residents | current loss per family per child under the two-child limit | households receiving a council tax cut from the recycled £1bn | households whose bills would be cut | pre-Budget fiscal gap against the fiscal rules (IPPR judgement) | rebanding requests expected to arise from the changes | recommended additional headroom against the fiscal rules | taxpayer losses at the Bank of England (level as stated)
- `method` (1): 2023/24 GGY per machine type grown at the most recent annual growth rate to 2026/27 (Appendix 2)
- `model` (1): IPPR tax-benefit model
- `origin` (22): 'a recent report with major think tanks' (Tax Reforms for Growth, 5 Nov 2025, CenTax/Advani modelling); source not stated on the page | DWP | DWP 2025a | DWP 2025b | DWP 2025b (households capped to February 2025) | DfE 2025 | HM Treasury / DWP Budget assessment | HMRC | IPPR 'Getting the child poverty strategy we need' (Parkes et al 2025), IPPR tax-benefit model | IPPR 2021 'Pulling down the ladder' proportional property tax case study, not fresh modelling | IPPR earlier tax-benefit-model work | IPPR research for Channel 4 FactCheck | IPPR's own 14 Nov 2025 technical appendix | IPPR's own 6 Aug 2025 gambling report | Social Market Foundation (Noyes 2025) | Social Market Foundation estimate for 2025 adopted unchanged for 2026/27 | as above (CGT reform package); source not stated on the page | not stated on the page | source not stated on the page | source not stated on the page (identical to Resolution Foundation's figure) | source not stated on the page (matches CenTax, Advani et al, Sept 2025) | the government's own assessment, to which IPPR's model is calibrated
- `package` (2): council tax F-G +50%, H +100% net of £1bn A-D recycling + non-UK-resident SDLT surcharge 2% to 6% | scrap_two_child_limit + remove_the_benefit_cap
- `package_keys` (1): ab2025_option__council_tax_bands_f_g_plus_50pct_h_plus_100pct_recycled_to_a_d + ab2025_option__non_uk_resident_sdlt_surcharge_2_to_6pct
- `package_second_key` (1): ab2025_option__remove_the_benefit_cap
- `poverty_line` (2): government basis (not restated on the page) | relative_60_median
- `prices` (1): 2019 values
- `program` (3): benefit_cap | non_uk_resident_sdlt_surcharge | universal_credit_child_element
- `proposed_band_d_multiplier` (8): 0.65 | 0.76 | 0.86 | 0.97 | 1.22 | 2.17 | 2.5 | 4
- `sign_convention` (10): positive = addition to GDP | positive = children in poverty because of the two-child limit (= lifted out by its removal) | positive = children kept in poverty by the two policies (= lifted out by their removal) | positive = children lifted out of poverty | positive = cost to the Exchequer | positive = higher council tax bill | positive = higher investment than the no-reform scenario | positive = higher mean household income | positive = saving against the current budget rule | positive = yield to the Exchequer
- `statistic` (3): average bill change per property in band | average bill per property in band (current) | mean
- `subgroup` (7): children in larger families (three or more children) | children in smaller families | higher-value households (bands F-H) | homes in bands F-H likely to be in higher bands than their true value justifies | properties in bands F-H (homes worth over £120,000 in 1991 values, typically over £600,000 today) | single parent families | third or subsequent children born after April 2017
- `year_note` (3): SMF figure is for calendar 2025; staged at FY 2025-26 | no year stated ('price tag'); staged at the scoring year | page says only per year; staged at FY 2026-27
