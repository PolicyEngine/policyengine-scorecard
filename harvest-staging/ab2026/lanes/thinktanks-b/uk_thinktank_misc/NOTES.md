# Smaller producers: Autumn Budget 2026

Staged from six primary HTML responses published on 28 October 2026. Sources are `cps`, `institute_for_government`, `learning_and_work_institute`, `citizens_advice` and `trussell`; the manifested Age UK response contributes zero rows. There are **13 rows and 6 primaries**. `stage.py` embeds the readings and recreates the manifest and deterministic gzip using only Python's standard library.

## Access recipe and primary hashes

Every primary was fetched afresh on 29 October 2026 using `curl -sSL -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"`; every response was HTTP 200. HTML bytes, headers and text extracts are under the ignored `.ab2026-primaries/uk_thinktank_misc/`. Hashes were checked using `shasum -a 256`. BeautifulSoup extracts were used to read the page's own body text; hashes refer to HTML, not extracts. There are no PDFs or spreadsheets in this family.

No assigned local copies or earlier document versions were supplied. There was no blocked fetch, fallback or observed replacement. Fetch-completion timestamps are recorded in each manifest note because HTML can change.

| Primary | Fetch completion (UTC) | Bytes | Rows | SHA256 |
|---|---|---:|---:|---|
| [CPS verdict](https://cps.org.uk/media/post/2026/a-dangerous-continuation-of-labours-tax-and-spend-fantasy-cps-verdict-on-the-budget/) | 2026-10-29 15:22:34 | 70,197 | 4 | `2c832e011866eb9f63f20597e7bf43bc01d44b6b1b5be43eee866ad6fc5ecd24` |
| [IfG commentary](https://www.instituteforgovernment.org.uk/comment/john-healeys-underwhelming-budget) | 2026-10-29 15:22:31 | 153,352 | 6 | `ecf19f14b4f808846fb8230b28a3244b0b65812484735842f9ab537a50195c69` |
| [Age UK response](https://www.ageuk.org.uk/latest-press/age-uk-response-to-the-budget/) | 2026-10-29 15:22:31 | 105,862 | 0 | `3035a8bbbb0f023dc24e805b430052163aa0dbfce3c975a6e0a0568983db6bf0` |
| [Learning and Work Institute response](https://learningandwork.org.uk/responding-to-autumn-budget-2026/) | 2026-10-29 15:22:31 | 122,809 | 1 | `c7fe077a0d9f4784aa4c91c906bcefa087cc9a4ece8b28026d24347c2a8b5dcf` |
| [Citizens Advice response](https://www.citizensadvice.org.uk/about-us/media-centre/press-releases/citizens-advice-responds-to-chancellors-budget/) | 2026-10-29 15:23:24 | 22,671 | 1 | `6a10336a67fc058512a4ccd9d0e80a27470fee8ba5775690fb1fcba39db67385` |
| [Trussell response](https://www.trussell.org.uk/news-and-research/news/our-response-to-the-autumn-budget-2026) | 2026-10-29 15:23:24 | 171,343 | 1 | `6cd2162d1382f03e937a382a39bd38c497a83d357bd969d2c85598740d17a95e` |

Citizens Advice's press index linked its dated response. Trussell's response was discovered by searching its own news pages; its primary prints “28th Oct 2026”. The other four URLs were assigned. CPS prints “Date Added: Wednesday 28th October 2026”; IfG prints “28 OCT 2026”; LWI prints “28 October 2026”; Age UK prints publication on 28 October 2026 at 04:14 PM and last update that date.

## Coverage and conventions

Reading order is CPS, IfG, Age UK, LWI, Citizens Advice, Trussell, then top to bottom within each page. Only contiguous excerpts under 15 words are quoted. There are no chart readings or derived gaps, totals, ratios or annualisations.

| Source | Rows | Own | Restated |
|---|---:|---:|---:|
| `cps` | 4 | 1 | 3 |
| `institute_for_government` | 6 | 3 | 3 |
| `learning_and_work_institute` | 1 | 0 | 1 |
| `citizens_advice` | 1 | 1 | 0 |
| `trussell` | 1 | 1 | 0 |
| `age_uk` (manifest only) | 0 | 0 | 0 |
| Total | 13 | 6 | 7 |

| Measure key | Rows | Scope |
|---|---:|---|
| `ab2026__household_energy_payment_100_bands_a_to_d` | 1 | IfG share receiving the £100 council-tax rebate for bands A–D; Table 6.1 line 1 |
| `null` | 12 | 11 context/document-tally observations and the one proposed CPS package row below |

The sole registered key is attached to the specific rebate's coverage, not to the entire cost-of-living package. IfG's exact identification of the £100 council-tax rebate for bands A–D identifies line 1; it gives no contrary scope. Its household denominator's geography is unspecified and is not inferred. Context forecasts, outturns and document counts have null measure keys and null reform hints. The CPS package has a null key, its own proposed key, and the producer's wording in `reform_hint`.

- GBP values preserve printed signs and cash magnitudes. “Tops £3 trillion” is the printed strict lower bound of debt stock. The six-month £61 billion debt-interest total is not multiplied to a year. Fiscal headroom is positive headroom; PuFins' £3.1 billion is a positive debt increase. No sign is reversed.
- Percentages remain percentages except Trussell's “over half”, which is the strict lower-bound share 0.5. “Almost 100” retains the printed upper threshold 100; no exact policy count is inferred. “Around 80%” retains the qualifier in conditions.
- `point`, rather than `central`, records each single published observation/forecast: none is labelled a central scenario. Thresholds use `range_low` or `range_high`. The 2% real-income growth is `cumulative` over the printed comparison window, not a 2% annual rate.
- Only IfG's fiscal-rule probabilities name a fiscal year: “2029/30” is normalised to `fy: 2029-30`, period 2030, `fiscal_year`. The income projection prints calendar 2030 and uses `annual` without `fy`. Other observations use the publication-year point-in-time anchor 2026 and preserve “last six months”, “this winter”, “each year”, “last 12 months”, or unspecified horizon explicitly. They do not claim a fiscal/calendar scoring year that the producer did not print. The PuFins annual-rate assertion has medium confidence because no scoring year or fiscal/calendar basis is supplied.
- Real income remains real; all other price bases are left unspecified where the page does not identify one. No baseline proposal is needed for these current observations and explicitly named context comparisons.
- CPS's own PuFins assertion uses `source_model: unstated` because it does not identify its calculation. Official debt/outturn context uses `administrative_data` and `administrative_fact`. CPS headroom and IfG fiscal probabilities/income forecasts are `restated`, `obr_efo_forecast`, `different_model`. The precise original release behind the unsourced CPS figures is not identified, so these originator assignments are explicit in rows.
- IfG's two counts are its own `arithmetic`, `different_model` observations. Its unsourced rebate share uses `source_model: unstated`, `own`, `different_model`. LWI's rounded NEET figure is treated as restated official labour-market context, `administrative_data`, `administrative_fact`; its response gives neither a quarter, age range nor a citation. Citizens Advice's unsourced bill forecast is treated as its own assertion with `source_model: unstated`, with missing method/geography acknowledged. Trussell explicitly calls the food-insecurity finding its own research, but supplies no method: `source_model: unstated`, `own`, `administrative_fact` for the retrospective reported observation. These three method-unspecified estimates and CPS's PuFins assertion have medium confidence; the other nine rows have high confidence.

## Proposed keys, metrics and units

One measure key is proposed:

- **`ab2026__package_cps_public_financial_institutions`** (1 row): CPS's annual public-debt increase from “channelling investment into Public Financial Institutions (PuFins)”. The £3.1 billion assertion is the producer's own package scope. **Table 6.1 line membership: unresolved; Table 6.2 membership: unresolved.** The primary enumerates no component programmes or lines. No Table 6.1/6.2 numbers or registered-package equivalence are inferred. This unresolved mapping requires clarification before comparison/ingest; the row is retained as a proposal rather than attached to a broader registered key.

Proposed metrics (counts and exact meaning):

- `public_debt_level` (1; GBP): CPS's current national-debt stock lower bound; no series definition is supplied.
- `debt_interest_cost` (1; GBP): CPS's total debt interest over the last six months, not the change caused by a measure.
- `fiscal_headroom` (1; GBP; existing README proposal): CPS's current post-Budget buffer against the fiscal rule; target year unspecified.
- `public_debt_change` (1; GBP): CPS's asserted annual debt increase through PuFins, scope and period limitations above.
- `measure_count` (2; proposed unit `measures`; AB2025 family precedent): IfG's approximate full scorecard count and exact count of tax measures costing/saving more than £1bn in the last forecast year.
- `fiscal_rule_probability` (2; percent): current and last-budget OBR probabilities of a current-budget surplus in 2029/30, as reported by IfG.
- `affected_share` (2; existing README proposal): IfG share of all households receiving the rebate (percent); Trussell lower-bound share of low-income private renters receiving LHA who ran out of food and could not buy more (share).
- `affected_count` (1; persons; existing README proposal): LWI's rounded current count of young people not in education, employment or training.
- `average_energy_bill_change` (1; GBP/month; AB2025 IFS/RF proposal spelling): Citizens Advice's forecast monthly household energy-bill increase, excluding any assertion that this is a Budget measure effect.

Registered `real_income_growth` accounts for the remaining row (IfG's restated OBR 2% cumulative income growth). Proposed unit `measures` is used only for the two counts. Other units are registered. There are no proposed baselines.

## Not staged and primary limitations

- **Age UK: zero rows.** Its own response has no numeric Budget estimate. The exact “On Income Tax threshold.” subsection was read; it welcomes protecting low-income pensioners from cash tax demands but prints no number. Dates, contact numbers, navigation “Nearly 4,000 flu mortalities” and the unrelated £2 donation link are not Budget claims.
- IfG's £100 rebate is a bare policy parameter; its 80% coverage is staged separately. The £1bn cutoff defines its count of one tax measure and is preserved in conditions rather than misrepresented as that measure's costing. Other dates and the 1991 council-tax valuation year are context labels, not model outcomes.
- LWI mentions extra Mayoral apprenticeship funding and OBR employment effects but prints no amount or employment effect. Its “one million” NEET level is retained as context. Navigation cards and unrelated articles are not harvested.
- Trussell does not print a measured effect of frozen LHA or the Budget. “Over half” is staged as its own research context; the 12-month reference window is a condition, not a separate outcome. Its statement that the government has already lifted the two-child limit is qualitative and receives no row.
- Citizens Advice gives no source, exact winter dates, geography or method for £60/month. Those are explicit limitations, not supplied from secondary material.
- CPS does not link its “paper released last week”. It is outside the assigned 28–29 October post-Budget window, and no unseen figures from it are staged. The comparison between six-month debt interest and an annual defence budget prints no second amount or exact ratio, so none is derived.
- No restated figure is silently removed: the seven official/OBR context rows are staged with `restated` and an originator note. No PolicyEngine restatement was identified.
- No pages were unreached. No charts contain unstaged numeric labels in these primaries.

Potentially ambiguous source wording is retained: IfG describes the £100 rebate as reaching “around 80%” of households but does not identify the denominator's geography. No UK/England assumption or correction is made; the row identifies the precise rebate and flags the missing denominator scope. CPS's PuFins claim lacks components, annual dates and method; its £15 billion headroom lacks a target year. Age UK's Pension Tax Allowance paragraph contains no number despite the assignment's pointer. These gaps have not been repaired using other sources.

## Verification

Command (environment/cache paths are contained within this family's ignored primaries directory):

```text
UV_PROJECT_ENVIRONMENT=.ab2026-primaries/uk_thinktank_misc/.venv UV_CACHE_DIR=.ab2026-primaries/uk_thinktank_misc/.uv-cache PYTHONPATH=. uv run -q python pipeline/ab2026_harvest_contract.py sources/harvest-uk-ab2026-2026-10-29/uk_thinktank_misc
sources/harvest-uk-ab2026-2026-10-29/uk_thinktank_misc: 13 rows, 0 problems
```

Re-ran `python3 sources/harvest-uk-ab2026-2026-10-29/uk_thinktank_misc/stage.py`; claims SHA256 before and after was **`d677dde1f96e629097696f5d17b575c8f1d34baaca42b96297cd46be773669ea`**. The gzip header has mtime zero and no original filename. Manifest byte counts and all six primary hashes were checked against saved HTML. All 13 quotes were verified as contiguous text in their pinned primary and under 15 words; each contains its `value_raw`.

Random sample was `random.Random(230).sample(range(13), 10)`, using zero-based indexes and reporting one-based row numbers below. For each, the saved primary was reopened, its SHA256 checked, and the paragraph at the locator read to verify the number, sign, unit and period. The three remaining rows (CPS debt interest, IfG count of one, Trussell share) were also checked for quote/value correspondence and basis.

| Sample row | Primary and locator | Rechecked value, sign, unit and period |
|---:|---|---|
| 12 | Citizens Advice, second Moriarty paragraph | £60/month positive bill increase; winter forecast, no exact dates; publication-time 2026 anchor, no FY |
| 3 | CPS, final Halligan paragraph | £15 billion positive fiscal headroom → 15e9 GBP; target year absent; 2026 statement anchor |
| 5 | IfG, opening body paragraph | “almost 100” policies; upper threshold 100 measures, no exact count invented; 2026 scorecard |
| 9 | IfG, energy-support first paragraph | “around 80%” rebate coverage; percent remains 80; this winter, no FY; geography unspecified |
| 1 | CPS, national-debt paragraph | “tops £3 trillion”; positive stock strict lower bound → 3e12 GBP; current at publication in 2026 |
| 7 | IfG, fiscal-picture second paragraph | 56% current probability; FY 2029/30 → `fy: 2029-30`, period 2030 |
| 8 | IfG, same paragraph, last-budget clause | 59% previous-budget comparator for that fiscal rule; FY 2029/30 → period 2030; no change calculated |
| 10 | IfG, energy-support first paragraph, final sentence | 2% higher real incomes in calendar 2030 versus before pandemic; cumulative, positive; annual time basis, no FY |
| 4 | CPS, Herring's PuFins paragraph | £3.1 billion positive debt increase each year → 3.1e9 GBP; no start/end year; 2026 statement anchor with annual horizon retained |
| 11 | LWI, Evans's main quotation | “one million” young NEET people → 1e6 persons; current context at publication 2026; no quarter invented |

Scope review found one non-null key: IfG's specifically identified bands A–D £100 rebate, Table 6.1 line 1. No broader support-package figure is attached to that key. The CPS public-financial-institutions package remains null with its proposed key and unresolved component mapping explicitly flagged above. No git state-changing commands, commits or pushes were run.
