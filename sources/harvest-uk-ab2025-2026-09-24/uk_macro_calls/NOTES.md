# Macro-house calls — Autumn Budget 2025 harvest (family `uk_macro_calls`, tranche 4 of #136)

Staged 2026-09-25 from the primary documents. **124 claims** in `claims_staged.jsonl.gz`, **20 documents** in `manifest.jsonl`. Row contract, enums and rules: `../README.md`; measure keys: `../REGISTRY_KEYS.md`. Every `value` is verbatim (normalised to the unit as recorded in `normalization`); nothing is derived. Sources (`source` slugs): `capital_economics`, `goldman_sachs`, `deutsche_bank`, `barclays`, `societe_generale`, `oxford_economics`, `ey_item_club`, `niesr` (the NiGEM / macro rows `../uk_niesr/NOTES.md` deferred to this family).

## Access recipe

Fetched 2026-09-25 with `curl` and a browser User-Agent (HTTP 200 on every URL); text extracted with pypdf (PDFs) and
BeautifulSoup (HTML). Scripts and logs: scratchpad `ab2025/macro/` (`stage_macro.py`, `extract_macro.py`,
`logs/fetch_log.tsv`). Per primary:

- **Capital Economics**: the two Focus notes (5 Nov preview; 26 Nov Rapid Response) are behind a sign-in / free-trial
  gate that prints only title, date and author. No paywall was bypassed: the £38bn is read from the abstracts printed
  on CE's public "UK Budget" key-issues hub (`/key-issues/uk-budget`), which is the primary the rows cite; the two
  gated pages are manifested with zero rows so the tally is complete.
- **Goldman Sachs**: the 15 Oct research note is client-only; Yahoo Finance UK quotes it verbatim (in quotation
  marks), so the four rows cite the Yahoo article with `parse_confidence: medium`. The 2 Dec Insights article is
  GS's own page (13 rows).
- **Deutsche Bank** (City AM, 19 Nov) and **Société Générale** (Newsquawk preview sheet, PDF created 24 Nov) are
  client-only research reported second-hand; the seed names these press records as the only public primaries and
  they are cited as such, `parse_confidence: medium`, publisher = the outlet, `source` = the house.
- **Barclays**: the IB insight is Barclays' own page (7 rows). The CNBC item is a video page; only its title
  ("at least £15B") and standfirst ("£25-30 billion") are text, so 3 rows cite those, `parse_confidence: medium`; the
  video was not transcribed.
- **Oxford Economics**: both pages fetched directly. The 27 Nov briefing abstract is qualitative (no number: zero
  rows); the 10 Dec Key Themes blog prints the 2025 (1.4%) and 2026 (1.0%) GDP calls.
- **EY ITEM Club**: the seed's PDF URL now 302-redirects to EY's Economics landing page (HTML, no PDF). The PDF was
  fetched from the Wayback Machine (`web/20251105125743id_/…`, raw bytes, `access: wayback`), PDF CreationDate
  2025-11-03. All 27 EY rows cite the PDF; the Scottish Financial News syndication is manifested with zero rows
  (its inflation and investment figures also appear in the PDF's summary table, which is what is staged).
- **NIESR**: the seven primaries with deferred macro numbers were NOT re-downloaded; the 2026-09-24 bytes held in
  the scratchpad (`ab2025/raw/uk_niesr/`) were re-hashed on 2026-09-25 and every sha256 matches
  `../uk_niesr/manifest.jsonl` (8/8 match; the eighth, "The Distributional Impacts of Tax Rises", has no macro
  number and is not manifested here). Manifest lines keep `retrieved: 2026-09-24` and say so in `note`.
  NIESR Outlook locators are printed pages (PDF page − 1), as in `uk_niesr`; EY's PDF page = printed page.

### Documents (manifest.jsonl)

- 2025-11-05 · Capital Economics · UK Autumn Budget 2025: Economic, financial and housing market implications (key-issues hub; abstracts of the Focus notes) · `html` · access `direct` · 103,836 bytes · sha256 `3df56f6a729c6480…` · **2 rows** — undated hub/listing page; date = the printed date of the 'Autumn Budget 2025 Preview' abstract it carries (5th November 2025). The Focus notes themselves are paywalled, so the £38bn figure is read from the two abstracts printed on this hub. Fetched 2026-09-25; the page also lists 2026 items.  
  <https://www.capitaleconomics.com/key-issues/uk-budget>
- 2025-11-05 · Capital Economics · Autumn Budget 2025 Preview · `html` · access `direct` · 97,937 bytes · sha256 `fc92e110fd9ba057…` · **0 rows** — paywalled (sign-in / free-trial gate): the page prints the title, date and author (Ruth Gregory, Deputy Chief UK Economist) but no abstract and no number; manifested, no rows  
  <https://www.capitaleconomics.com/publications/uk-economics-focus/autumn-budget-2025-preview>
- 2025-11-26 · Capital Economics · UK Budget (26th Nov. 2025) · `html` · access `direct` · 98,772 bytes · sha256 `8886a2dd6b2b903e…` · **0 rows** — paywalled Rapid Response (Paul Dales, Chief UK Economist); its abstract on the hub carries no number; manifested, no rows  
  <https://www.capitaleconomics.com/publications/uk-economics-rapid-response/uk-budget-26th-nov-2025>
- 2025-10-15 · Yahoo Finance UK · £30bn of tax rises and spending cuts expected in autumn budget, warns Goldman Sachs · `html` · access `direct` · 513,879 bytes · sha256 `76f57eb909b01912…` · **4 rows** — press report (Pedro Goncalves, 15 October 2025) quoting a Goldman Sachs research note verbatim; the note itself is client-only  
  <https://uk.finance.yahoo.com/news/tax-rises-spending-cuts-autumn-budget-goldman-sachs-125708109.html>
- 2025-12-02 · Goldman Sachs · What the UK Budget Means for Its Bond and Stock Markets · `html` · access `direct` · 816,394 bytes · sha256 `c782c2fa1b5adc16…` · **13 rows** — Goldman Sachs Insights article (Jari Stehn, George Cole, Sharon Bell), dated Dec 2, 2025 on the page  
  <https://www.goldmansachs.com/insights/articles/what-the-uk-budget-means-for-its-bond-and-stock-markets>
- 2025-11-19 · City AM · Reeves’ Budget will fail to rescue public finances, top bank predicts · `html` · access `direct` · 150,135 bytes · sha256 `1af22b19c3e5016e…` · **2 rows** — article:published_time 2025-11-19T11:08 GMT; press report (Maurício Alencar) of Deutsche Bank research (Sanjay Raja), which is client-only  
  <https://www.cityam.com/reeves-budget-will-fail-to-rescue-public-finances-top-bank-predicts/>
- 2025-10-16 · Barclays Investment Bank · A delicate balancing act for the UK economy · `html` · access `direct` · 99,092 bytes · sha256 `c7a93add52bcf596…` · **7 rows** — Barclays IB insight (Jack Meaning, UK Chief Economist), dated 16 Oct 2025 on the page  
  <https://www.ib.barclays/our-insights/a-delicate-balancing-act-for-the-uk-economy.html>
- 2025-11-26 · CNBC · Reeves to target headroom of at least £15B, Barclays economist says · `html` · access `direct` · 739,748 bytes · sha256 `6bb15b21dcdd44d3…` · **3 rows** — video page (02:05, Europe Early Edition); article:published_time 2025-11-26T08:54:23 GMT; only the title and standfirst are text, the video was not transcribed  
  <https://www.cnbc.com/video/2025/11/26/reeves-to-target-fiscal-headroom-of-at-least-a15-billion-barclays-economist-says.html>
- 2025-11-24 · Newsquawk · UK Autumn Budget - Wednesday, 26th November 2025 (Newsquawk research sheet) · `pdf` · access `direct` · 59,945 bytes · sha256 `750635a17edaab6b…` · **6 rows** — PDF CreationDate 2025-11-24 15:48 UTC (the seed dated it 26 Nov, the event date); an aggregator preview sheet reporting Société Générale's (and Morgan Stanley's) client-only research second-hand  
  <https://www.newsquawk.com/research_sheets/39900/download>
- 2025-11-27 · Oxford Economics · UK Budget papers over the cracks but can’t hide the fiscal risks · `html` · access `direct` · 329,561 bytes · sha256 `a677556fbcc2b57e…` · **0 rows** — article:published_time 2025-11-27T10:45 GMT; public abstract of a subscriber Research Briefing: qualitative only ('at the lower end of expectations', 'won't trigger substantial changes to our already below-consensus GDP forecasts'), no printed number; manifested, no rows  
  <https://www.oxfordeconomics.com/resource/uk-budget-papers-over-the-cracks-but-cant-hide-the-fiscal-risks/>
- 2025-12-10 · Oxford Economics · UK economic outlook 2026: sluggish growth and fiscal worries (UK Key Themes 2026) · `html` · access `direct` · 337,979 bytes · sha256 `708bda2fc18dfa87…` · **2 rows** — article:published_time 2025-12-10T10:41 GMT; public blog text of the Key Themes briefing  
  <https://www.oxfordeconomics.com/resource/uk-key-themes-2026-four-trends-shaping-the-economy/>
- 2025-11-03 · EY ITEM Club (Ernst & Young LLP) · EY ITEM Club Autumn Forecast: Tightening the purse strings · `pdf` · access `wayback` · wayback `20251105125743` · 4,036,620 bytes · sha256 `46f149c9cedd7f48…` · **27 rows** — the live URL now redirects to EY's Economics landing page (HTML), so the PDF was fetched from the Wayback Machine (snapshot 2025-11-05 12:57:43 UTC, id_ raw bytes); PDF CreationDate 2025-11-03 11:00 UTC; PDF page = printed page  
  <https://www.ey.com/content/dam/ey-unified-site/ey-com/en-uk/newsroom/2025/11/ey-uk-ey-item-club-autumn-forecast-11-2025.pdf>
- 2025-11-03 · Scottish Financial News · UK economy set for 1.5% boost due to public spending, says EY ITEM Club · `html` · access `direct` · 63,094 bytes · sha256 `7e7b9b1dda4a162a…` · **0 rows** — press syndication of the EY ITEM Club Autumn Forecast press release (3 Nov 2025); every EY number is staged from the PDF itself; manifested, no rows  
  <https://www.scottishfinancialnews.com/articles/uk-economy-set-to-be-boosted-by-15-due-to-public-spending-says-ey-item-club>
- 2025-10-20 · NIESR · Tax Options for the Chancellor · `html` · access `direct` · 168,558 bytes · sha256 `21bfdba97b8ce6b1…` · **3 rows** — NiGEM macro scenarios deferred from uk_niesr; sha256 verified 2026-09-25 against uk_niesr/manifest.jsonl (same bytes as the 2026-09-24 fetch)  
  <https://niesr.ac.uk/blog/tax-options-chancellor>
- 2025-11-24 · NIESR · Four Key Questions Ahead of the Autumn Budget · `html` · access `direct` · 131,323 bytes · sha256 `fd1412c9d23dd69e…` · **3 rows** — inflation, rate-cut and debt-interest calls deferred from uk_niesr; sha256 verified 2026-09-25 against uk_niesr/manifest.jsonl (same bytes as the 2026-09-24 fetch)  
  <https://niesr.ac.uk/blog/four-key-questions-ahead-autumn-budget>
- 2025-11-26 · NIESR · 2025 Autumn Budget Reaction: A High-Tax, High-Debt Steady State · `html` · access `direct` · 143,424 bytes · sha256 `70a9ee6200c94923…` · **8 rows** — headroom arithmetic and trend-growth call deferred from uk_niesr; sha256 verified 2026-09-25 against uk_niesr/manifest.jsonl (same bytes as the 2026-09-24 fetch)  
  <https://niesr.ac.uk/blog/2025-autumn-budget-reaction>
- 2025-11-28 · NIESR · What is the Stance of Fiscal Policy after Wednesday's Budget? · `html` · access `direct` · 108,460 bytes · sha256 `13d801406c1b12d9…` · **7 rows** — Fiscal Impact Measure (macro) deferred from uk_niesr; sha256 verified 2026-09-25 against uk_niesr/manifest.jsonl (same bytes as the 2026-09-24 fetch)  
  <https://niesr.ac.uk/blog/what-stance-fiscal-policy-after-wednesdays-budget>
- 2025-12-15 · NIESR · Where Did the Fiscal Black Hole Go? · `html` · access `direct` · 173,137 bytes · sha256 `99d67583835d3738…` · **10 rows** — NiGEM-vs-OBR forecast decomposition deferred from uk_niesr; sha256 verified 2026-09-25 against uk_niesr/manifest.jsonl (same bytes as the 2026-09-24 fetch)  
  <https://niesr.ac.uk/blog/where-did-fiscal-black-hole-go>
- 2025-11-03 · NIESR · UK Economic Outlook, Autumn 2025: Stability First · `pdf` · access `direct` · 1,555,228 bytes · sha256 `391956de6fd8ec35…` · **7 rows** — date = PDF CreationDate (2025-11-03); forecast completed 27 Oct 2025; NiGEM headroom/deficit forecasts and Box C/D consolidation figures deferred from uk_niesr; printed page = PDF page - 1; sha256 verified 2026-09-25 against uk_niesr/manifest.jsonl (same bytes as the 2026-09-24 fetch)  
  <https://niesr.ac.uk/wp-content/uploads/2025/11/Economic-Outlook-Autumn-2025.pdf>
- 2026-02-02 · NIESR · UK Economic Outlook, Winter 2026: Normality Under Strain · `pdf` · access `direct` · 2,807,212 bytes · sha256 `c9f35cd3095b28df…` · **20 rows** — date = PDF CreationDate; NiGEM post-Budget headroom, Box C waterfall and rate call deferred from uk_niesr; printed page = PDF page - 1; sha256 verified 2026-09-25 against uk_niesr/manifest.jsonl (same bytes as the 2026-09-24 fetch)  
  <https://niesr.ac.uk/wp-content/uploads/2026/02/UK-Economic-Outlook-Winter-2026.pdf>

## Coverage tally (seed bullets → claims staged → not staged)

Seeds: `SEED_INVENTORY/scores-4-commercial.md` §§ Capital Economics, Goldman Sachs, Deutsche Bank, Barclays,
Société Générale, Oxford Economics, EY ITEM Club (11 MACRO bullets) and `scores-3-other-shops.md` § NIESR (14
bullets; the macro items deferred by `../uk_niesr/NOTES.md`). "One row per printed number" within the five
headline-call categories (package / consolidation size, headroom, GDP effects and growth calls, CPI effects and
calls, Bank Rate calls) plus the NIESR items the deferral list names.

Macro houses (seed bullet → rows):
- CE preview (£38bn) → **2 rows**: the same £38bn printed in two abstracts on the hub (Economics Focus; Housing
  Market Focus). CE day-of Rapid Response → **0 rows** (abstract has no number).
- GS 15 Oct → **4 rows**: £30bn and "1% of GDP" of fiscal measures, the superseded "£20bn before", and the 0.3%
  demand drag (`gdp_level_effect`, keyed to the package with `timing: pre-Budget expectation`).
- GS 2 Dec → **13 rows**: GDP 1.1% (2026), CPI 3.4% / 2.3%, Bank Rate 3% by summer 2026, £21.7bn headroom
  (restated OBR), GS's prior ~£15bn, the OBR's +0.1pp GDP / −0.4pp CPI package effects (restated), borrowing
  revisions £21bn / £9bn average (restated) and GS's expected £13bn, 10-year gilts 4.25% / 4%.
- DB (City AM) → **2 rows**: headroom "just over £16bn"; tax rises "around £30bn".
- Barclays IB 16 Oct → **7 rows**: GDP 1.4% (2025), unemployment "just above 5%", Bank Rate toward 3.5%, shortfall
  "over £20bn" vs the spring forecast (`fiscal_gap`), output gap −1%, potential growth 1% (2026) → 1.5% (2031).
- Barclays CNBC 26 Nov → **3 rows**: headroom target "at least £15B"; shortfall £25-30bn (two range rows).
- SocGen (Newsquawk) → **6 rows**: tax raises GBP 39.5bln/yr, "just under GBP 12bln" higher spending, net tightening
  GBP 30bln/yr, headroom ~GBP 15bln, GBP 9.9bln (restated OBR March), FY25 gilt remit +GBP 15bln.
- OE 27 Nov → **0 rows** (qualitative). OE 10 Dec → **2 rows** (GDP 1.4% 2025; 1.0% 2026).
- EY ITEM Club (PDF) → **27 rows**: GDP 1.5/0.9/1.3/1.4%, consolidation £25-30bn (`fiscal_consolidation_requirement`,
  two range rows), £10bn headroom (restated OBR), typical £25-30bn headroom (two rows), −£5bn from gilt repricing,
  freeze-extension yield ~£10bn (`revenue_change`, option key), up-front tax rises £10-15bn (two rows), OBR multiplier
  −0.3% per 1% of GDP (restated), the base-case GDP effects −0.1/−0.2 (up front) and −0.3/−0.4 (end of forecast), the
  £45bn scenario −0.2/−0.3 and −0.4/−0.5, unemployment 5% peak and 4.7%, Bank Rate 3.5%, CPI 2.7% (2026) and 3.4%
  (2025, summary table). EY SFN syndication → **0 rows**.

NIESR (deferred items → rows; 58 rows):
- Tax Options (20 Oct) → **3 rows**: real GDP −0.87% (VAT), −0.15% (corporation tax), −0.05% (income tax), first
  year, `ab2025_option__niesr_30bn_tax_rise_scenarios`.
- Autumn 2025 Outlook → **7 rows**: pre-measures shortfall £38.2bn and "almost exactly 1 per cent of GDP"
  (`fiscal_headroom` negative, `proposed_baseline` = NIESR pre-measures world), PSNFL 82.2% and the £6.0bn
  investment-rule shortfall, the £30bn recommended buffer, the £50bn / 2% of GDP required consolidation.
- Four Key Questions (24 Nov) → **3 rows**: VAT-on-energy removal −0.17pp CPI (`ab2025_option__nil_rate_vat_on_domestic_electricity`),
  50bp of Bank Rate cuts in 2026 (`bank_rate_change` −0.5pp), £3bn debt interest per 10bp of gilt yields.
- Budget reaction (26 Nov) → **8 rows**: £22bn (restated OBR), 0.6% of GDP, −0.5pp vs the post-2011 median, −£8bn vs
  the £30bn recommendation, the £30bn itself, trend growth 1.25% (own) vs 1.5% (restated OBR), 1.0% average since 2019.
- Fiscal stance (28 Nov) → **7 rows**: Fiscal Impact Measure −0.4pp (2027) and the printed historical values (2010s
  −0.5 to −1pp; 2021 over +5pp; 2022 −1 to −2pp; since 2023 ~+1pp/yr).
- Where Did the Fiscal Black Hole Go? (15 Dec) → **10 rows**: £48bn predicted shortfall (`fiscal_gap`), £4.2bn
  (restated OBR pre-measures), nominal GDP +£40bn, participation +0.5pp and 330,000 more in work (restated OBR
  revisions), the ~£6bn / ~£2.5bn / ~£6.4bn / ~£15bn current-budget contributions, real government consumption −£6.4bn.
- Winter 2026 Outlook → **20 rows**: £26bn tax rises (restated, `revenue_change`), £22bn (restated), Bank Rate 3.25%
  year-end 2026, current budget deficit £0.5bn 2029-30 (own zero headroom, package key), PSNFL 83.7% and £33.1bn
  headroom, PSND 99.1% and +0.7pp vs pre-Budget, Box C: £4.2bn (restated), £38.2bn (restated from the Autumn Outlook),
  the eight Figure C1 waterfall steps (6.0, 2.5, 6.4, 3.0, 11.6, 2.0, 4.8, 6.1), trend growth 1.5% (restated) vs 1.25%.

Not staged (with reason):
- Capital Economics: the Focus/Rapid Response bodies (paywalled; nothing read behind the gate).
- GS 2 Dec: "$28.7 billion" (currency conversion of £21.7bn); 4.45% gilt starting level (market observation, carried
  in `conditions.starting_level`); UK domestic stocks −11% vs the FTSE 100 and mid-cap dividend yield +100bp (market
  observations, not calls). GS 15 Oct: NIESR's "£50bn a year" as quoted by Yahoo (third-party restatement).
- DB (City AM): "£9.9bn" (the article's own restatement of the OBR); "after 2028-29" drag (no number).
- Barclays IB: savings rate 10.7%, profit share 21.3%, rate of return 8.8%, pay growth 8.2% → 4.5%, CPI ~4% and the
  90bp / 160bp gaps, business investment +10% (ONS data restated); TFP −0.5% → +0.4% (not a headline-call category);
  Bank Rate 5.25% → 4% history.
- SocGen sheet: Morgan Stanley's +GBP 10bln and GBP 267bln FY26/27 remit (house outside this family); Newsquawk's own
  GBP 20-35bln hole, the GBP 10-20bln consensus band and Sky's ">GBP 15bln" (aggregator/consensus, not a macro house);
  the per-measure yields in the policy grid (press-reported reckoner figures, not SocGen's); the DMO remit table (data).
- OE 10 Dec: "marked slowdown in real income growth" (no number).
- EY PDF: business investment, consumer spending, pay growth and the 2% inflation target years (not headline-call
  categories); the summary table's other cells (GDP columns duplicate the text; borrowing, current account, earnings,
  annual-average Bank Rate, exchange rate); "around 1.5% weaker" real GDP if the OBR aligns with EY (a forecast-revision
  counterfactual, not a policy effect); "around half" of the tax rises up front (a fraction); the change-in-headroom
  chart bars other than the £5bn (chart-only). EY SFN: all numbers also in the PDF.
- NIESR Autumn Outlook: Box D Figures D1/D3 (no data labels; chart-only) and Table D1 / the 1.2bp, ~5bp and 0.6%
  elasticities (scenario parameters, not results); the £41.2bn August 2025 vintage (superseded, not in the seed); the
  OBR March "£9.9 billion surplus" (restated OBR, already in the OBR/IFS families); the "40 basis points" gilt-yield
  effect of a 2%-of-GDP consolidation (not in the deferral list; a candidate `gilt_yield_effect` row if wanted);
  Box C Table C1 (staged in `uk_niesr`).
- NIESR 24 Nov blog: "£40 billion" / 1.4% and "£31 billion" / 1.1% historical-headroom restatements of Box C Table C1
  (already staged from the Outlook in `uk_niesr`; arithmetic, not macro; left for the `uk_niesr` lane to decide);
  "approximately £15 billion" anticipated headroom and "around £20 billion" tax-rise consensus (media consensus, not
  NIESR's); £9.9bn, welfare +2pp / 13% of GDP, DMO £309.1bn (restated OBR/DMO); "eight basis points" typical Budget-day
  gilt move (market statistic).
- NIESR reaction: 59% / 54% probabilities, productivity −0.3pp / 1.0% / £16bn, PSNFL 83.7% → 83.0% and the 0.7% / 0.4%
  of GDP investment-rule margins, £24.1bn tightening (restated OBR, following `uk_niesr`'s convention of not staging
  restated OBR figures other than the headline headroom); "46 per cent" of 2029-30 revenue from smaller taxes (NIESR
  arithmetic on Table 4.1, package composition — not a headline-call category).
- NIESR stance: the annual chart values (chart-only); "roughly a third of the economy's underlying growth" (derived);
  the OBR's ~1.5% growth (restated).
- NIESR black hole: Resolution Foundation £14bn, IFS £22bn and Capital Economics £38bn in the comparison table
  (third-party figures restated by NIESR; CE's own £38bn is staged from CE's hub); the £25bn mixed-income reallocation,
  the 17% / 27% effective tax rates and the 4.7% independent-average unemployment rate (inputs to the staged
  contributions); £9.9bn.
- NIESR Winter 2026: consumption growth 1.0% / 1.3%, unemployment peak 5.4%, earnings 3.6% / 3.1%, the 3.75% December
  2025 Bank Rate outturn and the "two further 25 basis point cuts" (the 3.25% level is staged), "primary surpluses of at
  least two per cent of GDP" (a sustainability prescription), Box D migration scenarios (not in the deferral list).

### Row counts

- by `source`: barclays 10, capital_economics 2, deutsche_bank 2, ey_item_club 27, goldman_sachs 17, niesr 58, oxford_economics 2, societe_generale 6
- by `attribution`: own 107, restated 17
- by `benchmark_class`: different_model 124
- by `source_model`: arithmetic 23, bank_macro_model 29, capital_economics_forecast 2, item_club_hmt_model 13, niesr_fiscal_impact_measure 7, nigem 31, obr_efo_forecast 17, oxford_economics_forecast 2
- by `value_kind`: point 100, range_high 11, range_low 13
- by `parse_confidence`: high 79, medium 45
- by `measure_key`:
  - `null` 83
  - `ab2025__package_total_policy_decisions` 28
  - `ab2025__package_total_tax_policy_decisions` 7
  - `ab2025_option__niesr_30bn_tax_rise_scenarios` 3
  - `ab2025__package_total_spending_policy_decisions` 1
  - `ab2025_option__nil_rate_vat_on_domestic_electricity` 1
  - `ab2025_option__personal_tax_threshold_freeze_two_more_years_to_2030` 1
- rows per primary:
  - 2 · UK Autumn Budget 2025: Economic, financial and housing market implications (key-
  - 0 · Autumn Budget 2025 Preview
  - 0 · UK Budget (26th Nov. 2025)
  - 4 · £30bn of tax rises and spending cuts expected in autumn budget, warns Goldman Sa
  - 13 · What the UK Budget Means for Its Bond and Stock Markets
  - 2 · Reeves’ Budget will fail to rescue public finances, top bank predicts
  - 7 · A delicate balancing act for the UK economy
  - 3 · Reeves to target headroom of at least £15B, Barclays economist says
  - 6 · UK Autumn Budget - Wednesday, 26th November 2025 (Newsquawk research sheet)
  - 0 · UK Budget papers over the cracks but can’t hide the fiscal risks
  - 2 · UK economic outlook 2026: sluggish growth and fiscal worries (UK Key Themes 2026
  - 27 · EY ITEM Club Autumn Forecast: Tightening the purse strings
  - 0 · UK economy set for 1.5% boost due to public spending, says EY ITEM Club
  - 3 · Tax Options for the Chancellor
  - 3 · Four Key Questions Ahead of the Autumn Budget
  - 8 · 2025 Autumn Budget Reaction: A High-Tax, High-Debt Steady State
  - 7 · What is the Stance of Fiscal Policy after Wednesday's Budget?
  - 10 · Where Did the Fiscal Black Hole Go?
  - 7 · UK Economic Outlook, Autumn 2025: Stability First
  - 20 · UK Economic Outlook, Winter 2026: Normality Under Strain

## Metrics, units and baselines used

Registered metrics used: `gdp_level_effect` (unit `percent_of_real_gdp`, or `percentage_points` where the OBR's
"0.1 percentage point" is restated verbatim), `cpi_inflation_effect` (`percentage_points`), `revenue_change` (`gbp`).

Proposals already in the ingest's disposition table (`scorecard_db/ingest_uk_ab2025.py`): `fiscal_headroom` (per the
tranche brief, staged as `proposed_metric` although `Metric.FISCAL_HEADROOM` is now registered in models.py; the
ingest maps both spellings), `package_tax_rise_size` (the ingest maps it to `revenue_change` with
`conditions.fiscal_measure`), `bank_rate_level`, `fiscal_consolidation_requirement`, `fiscal_gap`,
`forecast_borrowing_change`. Spellings reused from `uk_rf_ab2025` so the ingest sees one name: `psnfl_share_of_gdp`
(RF's "82.2 per cent of GDP" row) and `forecast_spending_change` — neither appears in the disposition table by name,
so they need the same disposition RF's rows get.

New proposals in this family (each needs a disposition before ingest; an unlisted name raises):
- `gdp_growth` (`percent`): annual real GDP growth, potential growth or trend growth — `conditions.statistic` says which.
- `cpi_inflation` (`percent`): annual average CPI inflation forecast.
- `unemployment_rate` (`percent`); `output_gap` (`percent_of_potential_gdp`); `gilt_yield_10y` (`percent`).
- `bank_rate_change` (`percentage_points`): NIESR's "50 basis points" of cuts in 2026 (−0.5).
- `package_spending_change` (`gbp`): SocGen's "just under GBP 12bln" of higher spending in the package.
- `gilt_remit_revision` (`gbp`): SocGen's +GBP 15bln to the 2025-26 gilt remit.
- `fiscal_impulse` (`percentage_points`): NIESR's Fiscal Impact Measure, contribution to annual GDP growth.
- `current_budget_balance_contribution` (`gbp`): a step of NIESR's NiGEM-vs-OBR decomposition of the 2029-30 current
  budget balance (`conditions.factor`; all steps positive = the OBR's path is more favourable than NIESR's).
- `debt_interest_change` (`gbp`): £3bn per sustained 10bp rise in gilt yields.
- `forecast_nominal_gdp_change`, `forecast_employment_change` (`persons`), `forecast_participation_rate_change`
  (`percentage_points`): OBR November-vs-March revisions as NIESR reads them.
- `psnd_share_of_gdp` (`percent`); `debt_ratio_effect` (`percentage_points`, NIESR's +0.7pp PSND vs its pre-Budget forecast).
- `proposed_unit: percent_of_gdp` (4 rows) as in `uk_niesr`.

`package_tax_rise_size` carries `conditions.measure_type` to separate "expected tax rises" (keyed to
`ab2025__package_total_tax_policy_decisions`, the key the IFS/NEF/Evelyn £26bn restatements use) from "expected fiscal
measures" / "net fiscal tightening" (keyed to `ab2025__package_total_policy_decisions`), and `conditions.timing`
("pre-Budget expectation" | "post-Budget assessment" | "pre-Budget expectation (superseded prior)") on every
package-size and headroom row so the ingest can drop pre-Budget expectations from a comparison if it wants to.

`source_model`: `bank_macro_model` (proposal, per the brief) for GS, DB, Barclays and SocGen rows — none of the four
names its model in the primary; `capital_economics_forecast`; `oxford_economics_forecast` (OE's Global Economic Model
is not cited on the page); `item_club_hmt_model` (the ITEM Club "is the only non-governmental economic forecasting
group to use the HM Treasury model of the UK economy", PDF p.2); `nigem` for NIESR Outlook, Box C and tax-options rows
(where the document names NiGEM) and, with `parse_confidence: medium` and a note, for the 24 Nov blog's −0.17pp and
50bp calls and the reaction blog's 1.25% (NiGEM implied, not named); `niesr_fiscal_impact_measure` for the FIM;
`arithmetic` for NIESR/EY arithmetic on OBR or ONS figures; `obr_efo_forecast` on every restated OBR row.

Baselines: `baseline_policy: null` everywhere. One `proposed_baseline` (5 rows: the Autumn Outlook's £38.2bn, 1% of
GDP, 82.2%, £6.0bn and the Winter Box C restatement of £38.2bn) — "NIESR pre-measures forecast (Autumn 2025 Outlook,
completed 27 Oct 2025): no changes to planned spending or tax rates in the Autumn Budget", the producer's own words
being "assuming no changes to planned spending or tax rates in the Budget" (p.24). It must be registered
(baselines.py + the ingest's `_PROPOSED_BASELINE_PREFIXES`) before ingest (#13). The tax-options and EY multiplier
effects are vs an implied no-tax-rise baseline, recorded in `conditions.measure_type` / `method` with baseline null,
as `uk_niesr` did for Box D.

`period` conventions where the year is not printed (all `parse_confidence: medium`): package sizes and headroom
expectations → the fiscal-rule year 2029-30; NIESR tax-options "first year after the tax is applied" → 2029-30 (the
revenue-calibration year, as `uk_niesr` did for "long run"); GS "over the coming years" → 2029-30; EY "up front" →
2026-27 and "by the end of the forecast" → 2029-30; NIESR "medium term" / "over the decade" trend growth → 2030;
"end of this parliament" → 2029-30; EY's "4.7%" unemployment → 2028; FIM "since the start of 2023" average → 2025.

### As staged

- registered `metric`: `cpi_inflation_effect` 2, `gdp_level_effect` 14, `revenue_change` 2
- `proposed_metric`: `bank_rate_change` 1, `bank_rate_level` 4, `cpi_inflation` 4, `current_budget_balance_contribution` 12, `debt_interest_change` 1, `debt_ratio_effect` 1, `fiscal_consolidation_requirement` 4, `fiscal_gap` 4, `fiscal_headroom` 25, `fiscal_impulse` 7, `forecast_borrowing_change` 3, `forecast_employment_change` 1, `forecast_nominal_gdp_change` 1, `forecast_participation_rate_change` 1, `forecast_spending_change` 1, `gdp_growth` 15, `gilt_remit_revision` 1, `gilt_yield_10y` 2, `output_gap` 1, `package_spending_change` 1, `package_tax_rise_size` 10, `psnd_share_of_gdp` 1, `psnfl_share_of_gdp` 2, `unemployment_rate` 3
- registered `unit_concept`: `gbp` 60, `percent` 31, `percent_of_potential_gdp` 1, `percent_of_real_gdp` 13, `percentage_points` 14, `persons` 1
- `proposed_unit`: `percent_of_gdp` 4
- `baseline_policy`: None 124 (null = current law at the scoring date / the producer's own forecast baseline)
- `proposed_baseline`: NIESR pre-measures forecast (Autumn 2025 Outlook, completed 27 Oct 2025): no changes to planned spending or tax rates in the Autumn Budget (5)

## Distinct values per `conditions` axis

- `basis` (2 distinct): forecast (115); outturn (9)
- `comparison` (3 distinct): OBR November vs March 2025 forecast (4); OBR November vs March 2025 forecast, post-measures (2); expected OBR November vs March 2025 revision (1)
- `data` (1 distinct): OBR November 2025 EFO paths (1)
- `factor` (10 distinct): employment and participation revision (OBR November vs March 2025) (2); income composition (£25bn from mixed income to employee compensation; effective tax rates 27% vs 17%) (2); employment, participation, unemployment rate and income composition combined (1); gilt-yield conditioning window (ten working days to 21 October vs 14 October 2025) (1); household saving rate (OBR just below 4 per cent vs NIESR around 7 per cent) (1); other (smaller modelling and accounting differences) (1); trend growth (OBR 1.5 per cent vs NIESR 1.25 per cent) (1); unemployment path (NIESR higher for longer vs OBR) (1); unemployment path (OBR vs independent forecast average of 4.7 per cent) (1); unlegislated welfare savings excluded from the OBR's headroom (1)
- `fiscal_event` (1 distinct): autumn_budget_2025 (124)
- `forecast_vintage` (3 distinct): GS expectation before the 15 October 2025 note (1); OBR Spring Statement, March 2025 (1); OBR Spring Statement, March 2025 (£9.9bn, rounded) (1)
- `fy` (5 distinct): 2029-30 (69); 2026-27 (9); 2025-26 (3); 2027-28 (1); 2028-29 (1)
- `geography` (1 distinct): UK (124)
- `horizon` (30 distinct): 2029-30 (32); up front (4); first year after the tax is applied (3); by 2029/30 (2); by the end of the forecast (2); late 2021 through 2022 (2); medium term (period set to 2030) (2); much of the 2010s (2011 onwards; period set to 2019) (2); over the decade (period set to 2030) (2); 2019 to 2025 (1); average over the four fiscal years after 2025-26 (2026-27 to 2029-30) (1); by 2031 (1); by early 2026 (1); by the end of this parliament (1); by the middle of 2026 (1); by the summer of 2026 (1); by year-end 2026 (1); early 2026 (1); end of 2025 (1); end of 2026 (1); first half of 2026 (1); first year (1); over the coming years (no year printed; period set to the fiscal-rule year 2029-30) (1); over the next few years (no year printed; period set to 2028) (1); peak effect (1); peak in 2021 (1); per year (the 2029-30 figure) (1); settling at 1.4% from 2028 (1); since the start of 2023, per-year average (period set to 2025) (1); total cuts in 2026 (1)
- `measure_type` (21 distinct): effect vs the NiGEM baseline (no tax rise); monetary policy reacts; no labour-supply response (3); expected fiscal measures (tax rises and spending cuts) (3); expected tax rises in the Budget (3); NIESR recommended minimum fiscal buffer (Box C conclusion) (2); consolidation needed to meet the fiscal rules (tax rises or spending cuts) (2); consolidation required to reach a £30 billion buffer (2); entire fiscal shortfall to be closed at the Budget (2); typical headroom left by governments against their fiscal targets (historical norm) (2); up-front tax rises to be introduced almost immediately (the remainder of the £25-30bn found by extending the threshold freeze and trimming 2029-30 spending) (2); NIESR's own post-Budget current budget balance ('approximately balanced', i.e. zero effective headroom vs the OBR's £22 billion) (1); additional demand drag from the expected fiscal measures (1); change in headroom since the Spring Statement from higher market interest rates (ten working days to 15 October 2025) (1); expected higher spending in the Budget (per year) (1); expected net fiscal tightening (tax rises net of higher spending, per year) (1); expected tax rises (per year) (1); gap between the OBR's £22bn headroom (0.6% of GDP) and the post-2011 median headroom for Chancellors, in percentage points of GDP (1); headroom the Chancellor is expected to target in the Budget (1); predicted pre-measures shortfall relative to the £9.9bn March 2025 headroom (1); revision to the 2025-26 gilt financing remit (1); shortfall of the OBR's £22bn headroom against NIESR's pre-Budget recommendation of £30bn (1); shortfall versus the Spring 2025 forecast, implying additional consolidation by 2029-30 (1)
- `method` (2 distinct): OBR fiscal multipliers applied to EY's base-case profile of the £25-30bn tax rises (4); OBR fiscal multipliers applied to a larger tax-rise profile (4)
- `originator` (6 distinct): OBR November 2025 EFO (10); OBR March 2025 EFO (2); OBR November 2025 EFO (£21.7bn, rounded) (2); HMT/OBR Table 4.1 (2029-30 tax measures) (1); OBR November 2025 EFO (£21.7bn) (1); OBR fiscal multipliers (1)
- `path` (2 distinct): a cut in December 2025 then three more cuts in the first half of 2026 (1); two further 25 basis point cuts in 2026 (1)
- `price_basis` (2 distinct): 2023 prices (1); cash terms (1)
- `rule` (2 distinct): current budget (stability rule) (21); investment rule (PSNFL falling as a share of GDP) (2)
- `scenario` (8 distinct): pre-measures (no changes to planned spending or tax rates in the Budget) (5); base case (4); if the Government had to find an additional £45bn (4); OBR November 2025 pre-measures forecast (2); assuming the OBR forecasts a pre-measures deficit of around £20 billion (2); VAT (+3pp average effective rate; HMT reckoner: +3pp on the standard and reduced rates) (1); corporation tax (+4.5pp average effective rate; HMT reckoner: +7.5pp on the corporation tax rate) (1); income tax (+1pp average effective rate; HMT reckoner: +3pp on the basic and additional rates) (1)
- `shock` (2 distinct): a ten-basis-point rise in gilt yields, if sustained (1); tax rises generating revenues equivalent to 1% of GDP (1)
- `sign_convention` (18 distinct): positive = headroom inside the fiscal rule; negative = shortfall against it (25); positive = higher GDP (14); positive = raises the 2029-30 current budget balance relative to NIESR's Autumn 2025 pre-measures forecast (the OBR's more favourable path) (12); positive = fiscal tightening (reduction in borrowing) (8); positive = yield to the Exchequer (8); positive = contribution to annual GDP growth (fiscal impulse); negative = fiscal drag (7); positive = size of the shortfall (4); positive = higher borrowing (3); positive = higher inflation (2); positive = higher Bank Rate (1); positive = higher debt interest (1); positive = higher debt ratio (1); positive = higher gross gilt issuance (1); positive = higher nominal GDP (1); positive = higher participation (1); positive = higher real government consumption (1); positive = higher spending (1); positive = more in work (1)
- `starting_level` (1 distinct): 4.45% as of November 28, 2025 (2)
- `statistic` (15 distinct): annual real GDP growth forecast (8); annual CPI inflation forecast (4); average GDP growth over the decade (trend) (2); potential output growth (2); unemployment rate forecast (2); PSND as a share of GDP (peak) (1); PSND as a share of GDP, change vs NIESR's pre-Budget forecast (1); PSNFL as a share of GDP (1); PSNFL as a share of GDP (peak) (1); average annual GDP growth since 2019 (outturn) (1); level of real government consumption (1); medium-term potential output growth (1); medium-term trend growth (1); output gap estimate, current (October 2025) (1); unemployment rate forecast (peak) (1)
- `timing` (3 distinct): pre-Budget expectation (57); post-Budget assessment (29); pre-Budget expectation (superseded prior) (3)

## Attribution decisions

- `own` (107): the house's own call, including calls reported second-hand (GS 15 Oct via Yahoo, DB via City AM,
  SocGen via Newsquawk, Barclays via CNBC's title/standfirst): the number is the house's, the publisher is the
  outlet, `parse_confidence: medium`. NIESR arithmetic on OBR or ONS figures (0.6% of GDP, −0.5pp, −£8bn, 1.0% since
  2019, £40bn nominal GDP, −£6.4bn real spending, £3bn debt interest) is `own` / `arithmetic`, as in `uk_niesr`.
- `restated` (17): OBR (or HMT Table 4.1) figures printed beside a house's own call — GS: £21.7bn headroom, +0.1pp GDP,
  −0.4pp CPI, £21bn and £9bn borrowing revisions; SocGen: GBP 9.9bln; EY: "just £10bn" and the 0.3%-per-1%-of-GDP
  multiplier; NIESR: £22bn (twice), £4.2bn (twice), 1.5% trend growth (twice), £26bn tax rises, 330,000 and 0.5pp.
  Every one carries `conditions.originator` and `source_model: obr_efo_forecast`, `benchmark_class: different_model`.
  Restated OBR figures NOT beside a house call (probabilities, PSNFL paths, productivity cost, £24.1bn tightening, £9.9bn
  in the blogs) follow `uk_niesr`'s convention and are listed under "Not staged". Third-party restatements (NIESR's
  table of RF / IFS / CE shortfalls; Morgan Stanley in the SocGen sheet; NIESR's £50bn in the Yahoo piece) are not staged.
- No `same_assumptions` rows.
- Cross-family note for the ingest: `uk_ifs_ab2025` staged the OBR's £22bn post-Budget headroom with `measure_key:
  null`; here, per the tranche-4 brief, headroom-after-package rows (own or restated) carry
  `ab2025__package_total_policy_decisions`.

## Machine verbatim check

Every row's `value_raw` and `quote` were searched in the extracted text of the primary it cites (by sha256), comparing with all whitespace removed (pypdf inserts spurious spaces inside words and numbers, e.g. "2029 -30"; the quotes are written as the sentence reads). Checked at staging (`stage_macro.py`, which refuses to write on a miss) and again by this generator reading `claims_staged.jsonl.gz` back: **248 strings checked, 0 not found** (124 rows × value_raw + quote). No row was dropped for a verbatim miss.
