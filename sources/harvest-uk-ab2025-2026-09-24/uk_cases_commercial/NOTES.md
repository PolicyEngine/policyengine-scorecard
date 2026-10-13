# Commercial firms, platforms and media worked examples — Autumn Budget 2025 harvest (`uk_cases_commercial`)

Staged 2026-09-24 from the primary documents. **121 claims** in `claims_staged.jsonl.gz`, **25 documents** in `manifest.jsonl`. Row contract, enums and rules: `../README.md`; measure keys: `../REGISTRY_KEYS.md`. Every `value` is verbatim (normalised to the unit as recorded in `normalization`); nothing is derived.

## Access recipe

Fetched directly with `curl` (browser User-Agent, HTTP 200) unless noted; BeautifulSoup text; dates from
`datePublished` / `article:published_time` meta (recorded per document in the manifest notes).
- Blick Rothenberg (blickrothenberg.com): Cloudflare challenge (HTTP 403) to every `curl` User-Agent and the Wayback
  availability API answered 429 throughout the session; the page was rendered in a browser session and the article
  element's text captured (`blick-rothenberg-salary-sacrifice.article.txt`); the manifest sha256 is of that capture,
  `access: direct`, the note says so. The GB News page carrying Nimesh Shah's £140 example was fetched normally.
- PwC (pwc.co.uk): HTTP 403 to a browser User-Agent but HTTP 200 to `curl`'s default User-Agent; fetched, manifested,
  no own number (restates OBR "£24 billion in taxes and increasing spending by around £2 billion") → no rows.
- KPMG: fetched; the page is an illustration without a £ output (£5,000 sacrificed → £3,000 subject to NIC) → no rows.
- MoneyWeek live blog: one 2.3 MB page; entry timestamps recovered from the embedded `<time>` elements (2025-11-26
  13:27Z AJ Bell pensions; 2025-11-27 12:27Z InvestEngine/MoneyWeek; 2025-11-27 14:20Z AJ Bell freeze).
- RSM: the page meta now says published-time 2026-09-17 / modified 2026-05-01 (site republish); the memo's "Published
  27 Nov 2025" cannot be verified on the current page (manifest note).
- Which? dates: "How much would an income tax rise cost you?" `datePublished` 2025-11-07T00:01Z (INVENTORY
  CORRECTION: the landscape memo dated it 10 Nov); the main Budget piece is a rolling article first published
  2025-09-03 and updated through Budget day.
- Macro houses (Capital Economics, Goldman Sachs, Deutsche Bank, Barclays, Société Générale, Oxford Economics, EY ITEM
  Club) were NOT fetched — they are the `uk_macro_calls` lane (tranche 4). Cebr's duplicate bullet is staged in
  `uk_cebr`. Evelyn Partners has no own worked example; its OBR yield table is staged as `restated` (12 rows) so the
  tally is complete.
- The seed's "Calculator scopes" section is descriptor material only — summarised under "Calculators (descriptors)"
  below; no values from calculators are staged.

### Documents (manifest.jsonl)

- 2025-11-26 · 2025 Autumn Budget: Key tax, pension, trust and Inheritance Tax changes explained (Royal London for advisers) · `html` · access `direct` · 171,829 bytes · sha256 `cdd6000399205ea2…` · **2 rows** — datePublished 2025-11-26  
  <https://adviser.royallondon.com/technical-central/pensions/budgets-and-acts/autumn-budget-2025/>
- 2025-11-28 · Budget: Salary sacrifice for pensions – what employers should consider (KPMG Tax Matters Digest) · `html` · access `direct` · 193,918 bytes · sha256 `4d1ff8c42def8dbd…` · **0 rows** — event date 28-11-2025 on the page; page last modified 2026-03-06; illustration only (£5,000 sacrificed -> £3,000 subject to NIC), no £ output — no rows staged  
  <https://kpmg.com/uk/en/insights/tax/tmd-salary-sacrifice-for-pensions.html>
- 2025-11-25 · Autumn Budget 2025 live blog (MoneyWeek) · `html` · access `direct` · 2,354,227 bytes · sha256 `755d5ce994e74f1c…` · **17 rows** — article:published_time 2025-11-25T16:34Z (blog opened); entries used: 2025-11-26T13:27Z (AJ Bell pensions), 2025-11-27T12:27Z (InvestEngine/MoneyWeek savings), 2025-11-27T14:20Z (AJ Bell freeze)  
  <https://moneyweek.com/news/live/economy/autumn-budget-2025>
- 2025-11-06 · Higher earners face £50k pension hole if Reeves caps salary sacrifice in Budget (MoneyWeek, AJ Bell analysis) · `html` · access `direct` · 1,631,615 bytes · sha256 `8b7d0bc11bb81355…` · **9 rows** — article:published_time 2025-11-06T00:01Z  
  <https://moneyweek.com/personal-finance/pensions/scrapping-pension-salary-sacrifice-cost>
- 2025-12-15 · High earners face £15k income hit by 2029 following Autumn Budget (MoneyWeek, IG analysis) · `html` · access `direct` · 1,621,500 bytes · sha256 `84b0671783cdcff8…` · **2 rows** — article:published_time 2025-12-15T17:23Z; the analysis is IG's (Chris Beauchamp), not MoneyWeek's  
  <https://moneyweek.com/personal-finance/tax/high-earners-autumn-budget-income-hit>
- 2025-11-26 · Autumn Budget 2025: Employers (Moore Kingston Smith) · `html` · access `direct` · 181,589 bytes · sha256 `1caca6c7a5cdf3c1…` · **4 rows** — datePublished 2025-11-26T19:22:53Z  
  <https://mooreks.co.uk/insights/autumn-budget-2025-employers/>
- 2025-11-26 · Changes to salary sacrifice pension schemes to hit employee pay packets and pension funds (TaxScape press release) · `html` · access `direct` · 23,661 bytes · sha256 `d2c452b63eda6b7b…` · **2 rows** — dated 26 November 2025 on the page  
  <https://taxscape.deloitte.com/uk-budget/autumn-budget-2025/press-releases-autumn-budget-2025/changes-to-salary-sacrifice-pension-schemes.aspx>
- 2025-11-27 · Autumn Budget 2025 overview (Aegon adviser PDF) · `pdf` · access `direct` · 202,391 bytes · sha256 `d4691916f2e3f5eb…` · **2 rows** — PDF CreationDate 2025-11-27T12:16Z  
  <https://www.aegon.co.uk/content/dam/auk/assets/publication/marketing-support/autumn-budget-2025-analysis.pdf>
- 2025-10-31 · The Budget is a month away: What could be on the chopping block (Tom Selby) · `html` · access `direct` · 176,425 bytes · sha256 `1f87cc9f8469e4ed…` · **2 rows** — page date 2025-10-31T11:24  
  <https://www.ajbell.co.uk/news/budget-month-away-what-could-be-chopping-block>
- 2025-11-25 · 'I earn £20,000 and live with my son. The Budget means we will pay more tax' (BBC News case studies with EY modelling) · `html` · access `direct` · 571,707 bytes · sha256 `ab715ca6071f74c3…` · **3 rows** — datePublished 2025-11-25T00:00:32Z (original pre-Budget piece); dateModified 2025-11-27T11:38Z when the EY figures were added  
  <https://www.bbc.co.uk/news/articles/c9d6zwppjvjo>
- 2025-12-01 · Salary Sacrifice Pension Changes: Impacts on Individuals and Employers (Tomm Adams) · `html` · access `direct` · 5,343 bytes · sha256 `3dee4f5135ae942b…` · **2 rows** — article:published_time 2025-12-01T15:16:11Z; modified 2025-12-02. curl receives a Cloudflare challenge (HTTP 403); the page was rendered in a browser session and the article text captured; sha256 is of that text capture, not of the served HTML  
  <https://www.blickrothenberg.com/insights/detail/salary-sacrifice-pension-changes-impacts-on-individuals-and-employers/>
- 2025-11-27 · Budget commentary: Reaction to Rachel Reeves' second budget (Daniel Casali) · `html` · access `direct` · 60,669 bytes · sha256 `7c51b3e6694067c5…` · **12 rows** — datePublished 2025-11-27; modified 2025-11-28  
  <https://www.evelyn.com/insights-and-events/insights/reaction-to-rachel-reeves-second-budget/>
- 2025-11-26 · Autumn Budget: how might the government change pensions? (Ed Monk, Fidelity International) · `html` · access `direct` · 204,644 bytes · sha256 `c5bd3b22e73c7368…` · **2 rows** — 'Published 26 November 2025'; modified Nov 28  
  <https://www.fidelity.co.uk/markets-insights/personal-finance/saving-for-retirement/how-might-the-government-change-pensions>
- 2025-11-26 · Will salary sacrifice changes impact me? (Fidelity International) · `html` · access `direct` · 201,631 bytes · sha256 `a413ee8f8699fc8f…` · **4 rows** — 'Published 26 November 2025'; modified Nov 28  
  <https://www.fidelity.co.uk/markets-insights/personal-finance/saving-for-retirement/why-are-people-talking-about-salary-sacrifice-the-basics>
- 2025-11-26 · How much will Rachel Reeves's Budget cost YOU? (GB News, with Blick Rothenberg quotes and calculator) · `html` · access `direct` · 619,882 bytes · sha256 `090653ecd7ba4ba9…` · **1 rows** — datePublished 2025-11-26T16:42:45Z; modified 2025-11-27T05:13Z  
  <https://www.gbnews.com/money/budget-2025-calculator-rachel-reeves>
- 2025-11-12 · Autumn Budget 2025: tax-free cash cuts off the table but salary sacrifice change looms (Helen Morrissey) · `html` · access `direct` · 242,614 bytes · sha256 `86d42a640a829d00…` · **2 rows** — datePublished 2025-11-12  
  <https://www.hl.co.uk/news/autumn-budget-2025-tax-free-cash-cuts-off-the-table-but-salary-sacrifice-change-looms>
- 2025-11-26 · Autumn Budget 2025 – what you need to know (Christian Peasgood) · `html` · access `direct` · 303,049 bytes · sha256 `134b9b1d0c19106e…` · **3 rows** — datePublished 2025-11-26  
  <https://www.hl.co.uk/news/autumn-budget-2025-what-you-need-to-know>
- 2025-11-26 · UK Budget 2025: PwC UK’s Chief Economist comments on Economic impact · `html` · access `direct` · 133,197 bytes · sha256 `279bd8ab1cb4f5db…` · **0 rows** — fetched with curl's default User-Agent (a browser UA gets HTTP 403); restates OBR figures only ('raising roughly £24 billion in taxes and increasing spending by around £2 billion'); no worked example — no rows staged  
  <https://www.pwc.co.uk/press-room/press-releases/research-commentary/2025/uk-budget-2025-pwc-uk-chief-economist-on-economic-impact.html>
- 2025-08-21 · High earners face £7k extra tax if thresholds freeze extends to 2030 (Rathbones Group) · `html` · access `direct` · 202,638 bytes · sha256 `b27f01e225fc3e5d…` · **12 rows** — article:published_time 2025-08-21T16:25 BST  
  <https://www.rathbones.com/en-gb/wealth-management/media-centre/news-and-comment/high-earners-face-7000-pounds-extra-tax-if-thresholds-freeze-extends-to-2030>
- 2025-11-27 · Autumn Budget 2025 – Detailed analysis (RSM UK) · `html` · access `direct` · 47,946 bytes · sha256 `8e8f7a9d4246ca05…` · **6 rows** — page meta now shows published-time 2026-09-17 / modified-time 2026-05-01 (site republish); 'Published 27 Nov 2025' per the landscape memo — date not verifiable on the current page  
  <https://www.rsmuk.com/insights/budget/autumn-budget-2025-detailed-analysis>
- 2025-09-03 · Autumn Budget 2025: what it contains (Which? main Budget piece) · `html` · access `direct` · 325,125 bytes · sha256 `9bef1723b5d77df2…` · **4 rows** — datePublished 2025-09-03T23:01Z (rolling piece updated through Budget day); restated OBR/government examples only  
  <https://www.which.co.uk/news/article/autumn-budget-2025-when-it-is-and-what-will-it-contain-aZm9i8u75S5h>
- 2025-11-26 · Cash Isa annual allowance slashed to £12,000 - what you need to know (Which?) · `html` · access `direct` · 302,961 bytes · sha256 `dfd18c531d2c02b4…` · **2 rows** — datePublished 2025-11-26T13:03:47Z  
  <https://www.which.co.uk/news/article/cash-isa-annual-allowance-slashed-what-you-need-to-know-aMLdQ9K6x9eX>
- 2025-11-26 · Chancellor confirms salary sacrifice cap for pension contributions: what it means for you (Which?, AJ Bell calculations) · `html` · access `direct` · 277,096 bytes · sha256 `b79f7d38b1db33dd…` · **2 rows** — datePublished 2025-11-26T13:48:57Z  
  <https://www.which.co.uk/news/article/chancellor-confirms-salary-sacrifice-cap-for-pension-contributions-what-it-means-for-you-a9c5n7u9K0Xa>
- 2025-11-07 · How much would an income tax rise cost you? (Which?, AJ Bell table) · `html` · access `direct` · 323,149 bytes · sha256 `b4c0d77adbe45725…` · **24 rows** — datePublished 2025-11-07T00:01Z (INVENTORY CORRECTION: the landscape memo dated it 10 Nov)  
  <https://www.which.co.uk/news/article/how-much-would-an-income-tax-rise-cost-you-avpAh8w8hknt>
- 2025-11-26 · Income tax band freeze extended by three years (Which?, Quilter analysis) · `html` · access `direct` · 308,074 bytes · sha256 `31f70526ebca6193…` · **2 rows** — datePublished 2025-11-26T13:57:48Z  
  <https://www.which.co.uk/news/article/income-tax-band-freeze-extended-by-three-years-a9J7a4s6WPwG>

## Coverage tally (seed bullets → claims staged → not staged)

Seed: `scores-4-commercial.md` (commercial firms and platforms: 31 bullets across 17 producers, excluding the macro
houses and the Cebr duplicate).

Staged (121 rows) by `source`:
- `deloitte` 2: £50,000 / 10% sacrifice → employee NIC +£240, employer +£450 (2029/30).
- `ey` 3 (via BBC News): Deborah (£20,000) +£871 cumulative 2028-29 to 2030-31; Neal and Tara (~£100,000 combined)
  +£3,485 cumulative 2028–2031; Fatima (£25,000) +£215 in 2028-29.
- `aj_bell` 40: £35,000 bill £4,486 → £4,710 under +1p (the seed's "+£224" is derived and not staged); Which? 7 Nov
  table (8 salaries × bill 2025-26, bill after 2p, extra tax paid = 24 rows); pension "hole" £22,060 / >£37,000 /
  ~£50,000 (6 Nov, option) and £22,060 re-issued 26 Nov (announced); Sally's salary-sacrifice-vs-net-pay example
  (take-home £39,161 / £38,720, employee NI £2,953 / £3,394, income tax £7,386, employer saving £825 — context,
  `measure_key: null`); £188 take-home loss (£55,000, 10%); freeze +£259 / +£683 / +£1,292 cumulative 2028–2031.
- `hargreaves_lansdown` 5: +£30 / +£34 (£45,000, 5%, rumoured cap — printed figures differ from a flat 8%/15% on
  £250, noted); £964 (£51,000, freeze; period not stated → 2030-31, medium); pension pots £226,000 vs £283,000.
- `quilter` 2: £843 (£44,000) / £321 (£40,000) cumulative to 2030.
- `fidelity` 6: £40,000 5% → £0 / £0; £40,000 10% → £160; £110,000 £10,000 sacrifice → £160; £120,000 £20,000 →
  £360 employee / £2,700 employer.
- `royal_london` 2: £45,000 5% → "approximately £20" / £37.50.
- `aegon` 2: maximum NI saving still available £160 employee / £300 employer.
- `rsm` 6: Employee A £40k 5% → £0/£0; B £60k 5% → £20 / £150; C £35k 20% → £400 / £750.
- `moore_kingston_smith` 4: £50,000 5% → take-home −"around £40" / employer £77.50; £100,000 5% → −£60 / £465
  (employer figures above a flat 15%, noted).
- `blick_rothenberg` 3: cash ISA cut "over £140" (higher-rate, £8,000 at 4.5%); £60,000 5% → £20 / £150.
- `which` 6: £22,728 / £11,364 savings thresholds at 4.4% (own arithmetic, context); restated OBR/government
  examples £255 EV (8,500 miles), £5,310 × 560,000 families, £900 NLW.
- `investengine` 14 (with MoneyWeek): five-year cash-ISA table — tax due at 20% and 22% for years 1–5 (10 rows) and
  the year-5 cumulative £264 / £290.40 (2 rows); 7.1 million cash ISA savers and "just over two million (28%)"
  above £12,000 (HMRC statistics analysis, `administrative_fact`).
- `ig` 2 (via MoneyWeek 15 Dec): ninth decile −£8,935 and top decile −£15,658 real purchasing power by 2029.
- `rathbones` 12: 4 salaries-in-2022 × cumulative extra tax by end-2025 / end-2028 / end-2030 (option: freeze to
  April 2030; the page's third column header is misprinted "2028", noted).
- `evelyn_partners` 12: OBR yield table (11 measures, 2029-30) + £26bn total — all `restated`.

Not staged (with reason):
- `pwc`: no own number (restated OBR £24bn/£2bn) — manifested only.
- `kpmg`: illustration without a £ output — manifested only.
- AJ Bell "+£224" (derived: £4,710 − £4,486 is not printed; the text says "an increase well in excess of £200");
  MoneyWeek 26 Nov 13:27 "pensions of higher earners could be £50,000 smaller" (restates the 6 Nov figure already
  staged).
- Which? main piece: "£150 a year" energy bill cut and other government restatements without a worked example.
- Rathbones: "£38bn a year in 2029/30" from the existing freeze and "almost 67% of the defence budget" (OBR-derived
  context, footnoted); ts2.tech secondary attributions (Times £2,600; Rathbones £4,043 vs £2,517) — not on any
  primary, excluded as in the seed.
- Macro houses (7 producers, 11 bullets) → `uk_macro_calls` (tranche 4), not fetched here.
- Cebr → staged in `uk_cebr`.

Calculators (descriptors, no rows):
- Deloitte Personal Tax Calculator (bbctaxcalculator.azurewebsites.net; embedded on TaxScape): income tax with frozen
  thresholds, PA taper, NIC, child benefit net of HICBC, dividend rates, Scottish/Welsh rates, alcohol/tobacco/fuel
  duties and VAT on those items; inputs salary/pension, self-employment income, interest, dividends, SPA flag,
  children under 16, Scotland flag, weekly drinks/cigarettes/fuel spend; 2025-26 vs 2026-27; no benefits (child
  benefit only); "Last Updated: 26 November 2025 18:47:20" (client-side stamp per the landscape memo).
- Blick Rothenberg "Autumn Budget 2025 tax calculator" (Enformant iframe; white-labelled to GB News, the Guardian,
  the Independent, the Evening Standard): 2025/26 vs 2026/27 engine parameters — bands frozen (basic £37,700,
  additional £125,140; 20/40/45), dividend rates 8.75→10.75 / 33.75→35.75 / 39.35, NI unchanged (PT £12,570, UEL
  £50,270, 8%/2%), PA £12,570 taper at £100,000, child benefit £26.05→£27.00 / £17.25→£17.85, HICBC £60,000–£80,000,
  fuel duty 52.95p→54.37p, alcohol/tobacco duties uprated, VED bands; inputs age, marital status, children, salary,
  self-employment profit, pension income, rental profits, interest, dividends, consumption quantities, car details,
  partner; rUK only; outputs income tax, NI, child benefit, duties, "Take Home".
- Telegraph five-calculator set (salary sacrifice + property income; mansion tax; stealth tax; dividends; savings),
  Telegraph stealth-tax and pre-Budget income-tax-rise calculators, Times "What does the budget mean for you?" and
  salary-sacrifice calculator, FT Budget 2025 calculator, Daily Mail/Nous.co interactive (widget now 404), Sky News
  two calculators (403 on every route; builder unknown): inputs unreadable (paywall/blocks) — descriptors only.
- Adam Smith Institute "Average Tax Calculator": England-only 2025/26 direct taxes incl. HICBC, PSA, dividend and
  CGT; no AB2025 measures; constituency stats (top-10 mean £18,223.40 / 26.51%; median £7,040 / 18.67%; bottom-10
  16.00%) — descriptor.
- Tax Policy Associates calculator — recorded in `uk_tpa/NOTES.md`.
- BBC "Use our tax calculator to see how Spring Statement forecasts may affect you" (17 Feb 2026, Flourish): extra
  income tax and NICs in 2030-31 from frozen thresholds vs CPI uprating from 2026-27; England/Wales/NI employees only.
- Which? standing income-tax calculator (generic; not opened).

### Row counts

- by `source`: aegon 2, aj_bell 40, blick_rothenberg 3, deloitte 2, evelyn_partners 12, ey 3, fidelity 6, hargreaves_lansdown 5, ig 2, investengine 14, moore_kingston_smith 4, quilter 2, rathbones 12, royal_london 2, rsm 6, which 6
- by `attribution`: own 105, restated 16
- by `benchmark_class`: administrative_fact 2, different_model 119
- by `source_model`: arithmetic 121
- by `value_kind`: cumulative 21, point 95, range_high 1, range_low 4
- by `parse_confidence`: high 108, medium 13
- by `measure_key`:
  - `ab2025__salary_sacrifice_pension_nics_cap_2000` 29
  - `null` 20
  - `ab2025_option__income_tax_basic_rate_plus_2p` 16
  - `ab2025_option__personal_tax_threshold_freeze_two_more_years_to_2030` 12
  - `ab2025__personal_tax_thresholds_freeze_to_2031` 10
  - `ab2025__supporting_savers_help_to_save_and_cash_isa_limit` 9
  - `ab2025__savings_rates_plus_2pp_and_starter_limit_held` 6
  - `ab2025_option__salary_sacrifice_nics_cap_2000_rumoured` 5
  - `ab2025__eved_mileage_supplement_electric_and_phev` 2
  - `ab2025__hmrc_further_measures_to_close_the_tax_gap` 2
  - `ab2025__uc_child_element_remove_two_child_limit` 2
  - `ab2025__cgt_employee_ownership_trust_relief_cut_to_50pct` 1
  - `ab2025__dividend_rates_plus_2pp` 1
  - `ab2025__gambling_duties_rgd_40_remote_betting_25` 1
  - `ab2025__high_value_council_tax_surcharge` 1
  - `ab2025__iht_nil_rate_bands_and_apr_bpr_allowance_frozen_to_2031` 1
  - `ab2025__package_total_tax_policy_decisions` 1
  - `ab2025__writing_down_allowances_14pct_and_40pct_fya` 1
  - `ab2025_option__income_tax_all_rates_plus_1p` 1

## Metrics, units and baselines used

All rows are mode-3 material (#63) staged for the tally; the ingest drops them with a tallied reason. Every row is
`source_model: arithmetic` (or the firm's own projection for pension pots) with the household inputs as strings in
`conditions` (`employment_income`, `pension_contribution`, `tax_year`, `region`, `household`, `age`,
`existing_pension_pot`, `horizon`, `counterfactual`, `indexation`, `interest_rate`, `taxpayer`, …).
- `proposed_metric: household_tax_change` (README list; `gbp`; "positive = increase in tax/NICs paid") — extra
  income tax or employee NICs for a named case; cumulative multi-year figures carry `value_kind: cumulative` and the
  years in `conditions.horizon`.
- `proposed_metric: take_home_pay_change` (README list; `gbp`; "positive = increase in take-home pay") — AJ Bell
  −£188, MKS −£40 / −£60.
- `proposed_metric: pension_pot_projection` (README list; `gbp`; `time_basis: point_in_time`) — AJ Bell "hole" at 65
  (positive = reduction in the pot; `period` = the year the 35-year-old reaches 65, 2055-56), HL pots at retirement
  (`period` approximated as 2071 for a 22-year-old retiring at 68; illustrative).
- `proposed_metric: employer_nics_change` (`gbp`; "positive = increase in tax/NICs paid", or "positive = employer
  NICs saved" for Sally's £825) — employer-side amounts printed beside the employee figures (Deloitte, HL, Fidelity,
  Royal London, RSM, MKS, Blick Rothenberg).
- `proposed_metric: household_income_tax_bill` (`gbp`) — annual bill levels (AJ Bell £4,486 / £4,710 and the Which?
  table's two bill columns; Sally's £7,386); `proposed_metric: take_home_pay` and `employee_nics` (`gbp`) — Sally's
  levels; `proposed_metric: nics_saving_cap` (`gbp`) — Aegon £160 / £300.
- `proposed_metric: taxable_savings_balance_threshold` (`gbp`) — Which? £22,728 / £11,364 (PSA ÷ 4.4%).
- `proposed_metric: real_purchasing_power_change` (`gbp`; decile averages, `income_group` decile_9 / decile_10) — IG.
- `proposed_metric: affected_count` (`persons` / `families`) — InvestEngine 7.1m / 2m; Which? restated 560,000
  families; `proposed_metric: average_annual_gain_restated` — Which?'s restated OBR £5,310 (kept off the registered
  `average_annual_gain` so a restatement is not mistaken for a producer's own average); `proposed_metric:
  gross_earnings_change` — Which?'s restated £900 NLW.
- `revenue_change` (registered) — Evelyn Partners' restated OBR yields.
- `measure_key`: announced cap → `ab2025__salary_sacrifice_pension_nics_cap_2000`; pre-Budget cap →
  `ab2025_option__salary_sacrifice_nics_cap_2000_rumoured`; announced freeze → `ab2025__personal_tax_thresholds_freeze_to_2031`;
  pre-Budget freeze (Rathbones) → `ab2025_option__personal_tax_threshold_freeze_two_more_years_to_2030`; +1p →
  `ab2025_option__income_tax_all_rates_plus_1p`; basic +2p → `ab2025_option__income_tax_basic_rate_plus_2p`; cash ISA →
  `ab2025__supporting_savers_help_to_save_and_cash_isa_limit`; savings +2pp → `ab2025__savings_rates_plus_2pp_and_starter_limit_held`;
  EV → `ab2025__eved_mileage_supplement_electric_and_phev`; two-child limit → `ab2025__uc_child_element_remove_two_child_limit`;
  Evelyn rows → the matching announced-measure keys; baseline bills, Sally's example, IG's package-plus-inflation,
  Which? thresholds → `null`.
- `period`: the tax year the firm names (2029-30 for the cap; 2025-26 for current-rules bills; cumulative rows carry
  the end year; Rathbones and IG carry calendar years with `time_basis: annual`).
- Baselines: all `baseline_policy: null` (current law at the scoring date; counterfactuals such as "thresholds
  uprated annually with inflation" are recorded in `conditions.counterfactual`).

### As staged

- registered `metric`: `revenue_change` 12
- `proposed_metric`: `affected_count` 3, `average_annual_gain_restated` 1, `employee_nics` 2, `employer_nics_change` 12, `gross_earnings_change` 1, `household_income_tax_bill` 19, `household_tax_change` 54, `nics_saving_cap` 2, `pension_pot_projection` 6, `real_purchasing_power_change` 2, `take_home_pay` 2, `take_home_pay_change` 3, `taxable_savings_balance_threshold` 2
- registered `unit_concept`: `families` 1, `gbp` 118, `persons` 2
- `proposed_unit`: none
- `baseline_policy`: None 121 (null = current law at the scoring date)
- `proposed_baseline`: none

## Distinct values per `conditions` axis

- `age` (2 distinct): 35 (4); 22 (2)
- `allowance` (1 distinct): standard personal allowance (24)
- `annual_mileage` (1 distinct): 8,500 miles (1)
- `arrangement` (4 distinct): net-pay scheme (no salary sacrifice) (2); with salary sacrifice (salary £49,500 gross) (2); with salary sacrifice (1); with salary sacrifice / net pay (same) (1)
- `basis` (1 distinct): static (109)
- `counterfactual` (5 distinct): thresholds uprated annually with inflation (12); a system in which thresholds had increased by inflation each year (3); freeze vs thresholds indexed (EY modelling; method not published) (3); indexed thresholds (indexation basis not stated) (2); thresholds increasing with wages (1)
- `data` (1 distinct): HMRC ISA statistics (InvestEngine analysis) (2)
- `displaced_savings` (1 distinct): £8,000 (1)
- `employment_income` (30 distinct): £45,000 (7); £55,000 (7); £40,000 (6); £50,000 (6); £25,000 (5); £35,000 (5); £20,000 (4); £100,000 (3); £100,000 salary in 2022, grown with OBR wage forecasts (3); £15,000 (3); £30,000 (3); £35,000 salary in 2022, grown with OBR wage forecasts (3); £50,000 salary in 2022, grown with OBR wage forecasts (3); £50,270 (3); £80,000 salary in 2022, grown with OBR wage forecasts (3); £120,000 (2); £35k (2); £40k (2); £60,000 (2); £60k (2); combined about £100,000 (couple, both in administration) (1); £110,000 (1); £15,000 today (1); £25,000 ('I make £25,000') (1); £40,000 today (1); £44,000 today (1); £45,000 today (1); £47,000 today (1); £51,000 in the year to April 2028 (1); £75,000 (1)
- `existing_pension_pot` (1 distinct): £30,000 (4)
- `fiscal_event` (1 distinct): autumn_budget_2025 (121)
- `fy` (8 distinct): 2029-30 (51); 2025-26 (34); 2030-31 (8); 2028-29 (4); 2031-32 (4); 2027-28 (3); 2022-23 (2); 2026-27 (1)
- `geography` (1 distinct): UK (121)
- `growth_assumption` (2 distinct): not stated (4); 5% investment growth after charges (2)
- `horizon` (12 distinct): cumulative to end of 2025 (4); cumulative to end of 2028 (4); cumulative to end of 2030 (4); to age 65 (4); the three years between 2028 and 2031 (cumulative) (3); by 2029 (2); five years (cumulative) (2); the next four years to 2030 (cumulative) (2); to retirement (2); 2028 to 2031 (cumulative, combined) (1); 2028-29 to 2030-31 (cumulative) (1); not stated (freeze runs to 2030-31) (1)
- `household` (7 distinct): Employee A (2); Employee B (2); Employee C (2); couple, 58, mortgage paid off (1); full-time worker aged 21 or over on the NLW (1); single mum, level 4 apprentice construction site supervisor, council housing (1); single, 63, NHS admin 33 hours a week, lives with adult son (1)
- `household_income` (2 distinct): average household income £103,700 (1); average household income £65,700 (1)
- `income_group` (2 distinct): decile_10 (1); decile_9 (1)
- `indexation` (1 distinct): pay rising in line with inflation (3)
- `interest_rate` (2 distinct): 4.4% (2); 4.5 per cent (1)
- `originator` (4 distinct): Office for Budget Responsibility, November 2025 (11); OBR (3); OBR/HM Treasury (1); government (1)
- `pension_contribution` (17 distinct): 10% (£5,500) (6); 5% (£2,250) via salary sacrifice (4); 5% personal + 3% employer via salary sacrifice (4); 10% (£5,000) via salary sacrifice (2); 20% (£7k) via salary sacrifice (2); 5% (£2,000) via salary sacrifice (2); 5% (£2,500) via salary sacrifice (2); 5% (£2k) via salary sacrifice (2); 5% (£3,000) via salary sacrifice (2); 5% (£3k) via salary sacrifice (2); 5% (£5,000) via salary sacrifice (2); £20,000 via salary sacrifice; £18,000 over the cap (2); 10% (£4,000) via salary sacrifice; £2,000 over the cap (1); 10% via salary sacrifice (1); own 5% + employer 3% (1); own 5% + employer 5% (1); £10,000 via salary sacrifice to restore the personal allowance; £8,000 over the cap (1)
- `personal_savings_allowance` (1 distinct): none assumed (1)
- `price_basis` (1 distinct): real (2)
- `region` (4 distinct): rUK rates (not stated otherwise) (106); Bradford (rUK rates) (1); Sheffield (rUK rates) (1); north London (rUK rates) (1)
- `savings_tax_rate` (2 distinct): 20% (6); 22% (6)
- `scenario` (4 distinct): £12,000 a year into a cash ISA and £8,000 a year into a top non-ISA account at 4.5%; £1,000 personal savings allowance (12); current rates (baseline) (9); current rules (context for the cap) (6); 1p on income tax (1)
- `sign_convention` (8 distinct): positive = increase in tax/NICs paid (65); positive = yield to the Exchequer (12); positive = gain to households (4); positive = reduction in the pension pot at 65 (4); positive = increase in take-home pay (3); positive = maximum NI saving still available (2); positive = pension pot at retirement (2); positive = employer NICs saved (1)
- `statistic` (1 distinct): mean (1)
- `subgroup` (4 distinct): cash ISA savers putting more than £12,000 in (28% of cash ISA savers) (1); employee (8% of £2,000) (1); employer (15% of £2,000) (1); people who put money in a cash ISA in 2022/23 (1)
- `tax_year` (7 distinct): 2025-26 (23); 2025-26 rates with basic rate 22% (8); current (2025-26) NI rates: 8% between £12,570 and £50,270, 2% above (6); 2029-30 (2); 2025-26 rates plus 1p (1); 2028-29 (1); 2029-30 (once the cap is in force) (1)
- `taxpayer` (4 distinct): basic-rate taxpayer (12); basic-rate taxpayer (£1,000 personal savings allowance) (1); higher-rate taxpayer (40% on savings income; pre-April-2027 rate) (1); higher-rate taxpayer (£500 personal savings allowance) (1)
- `unit_population` (1 distinct): families affected (1)
- `vehicle` (1 distinct): electric car (1)
- `year_of_scenario` (5 distinct): 1 (2); 2 (2); 3 (2); 4 (2); 5 (2)

## Attribution decisions

- `own` / `different_model` for every firm's own arithmetic or projection (105 rows), including figures published
  through a media outlet (EY via BBC News; AJ Bell via Which?/MoneyWeek; Quilter via Which?; IG via MoneyWeek;
  Blick Rothenberg's £140 via GB News) — `source` is the computing firm, `publication.publisher` the outlet.
- `restated` (16 rows): Evelyn Partners' OBR table and £26bn; Which?'s OBR/government examples (£255 EV, £5,310 ×
  560,000 families, £900 NLW). Dropped at ingest (#86).
- InvestEngine's ISA-saver counts (analysis of HMRC statistics) are `own` / `administrative_fact`.
