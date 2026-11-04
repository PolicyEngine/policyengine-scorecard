# Smaller producers: Autumn Budget 2026

**Working files.** `stage.py`, which writes `manifest.jsonl` and `claims_staged.jsonl.gz`, lives on branch `uk/ab2026-harvest-staging` at `harvest-staging/ab2026/lanes/thinktanks-b/uk_thinktank_misc/stage.py`; this branch carries only NOTES.md, `manifest.jsonl` and `claims_staged.jsonl.gz`. The lane's local primaries folder (`.ab2026-primaries/`) was never committed: the repository carries no primary bytes, so fetch each primary from its `manifest.jsonl` URL and check its sha256.

Staged from five primary HTML responses published on 28 October 2026. Sources are `cps`, `institute_for_government`, `learning_and_work_institute` and `citizens_advice`; the manifested Age UK response contributes zero rows. There are **12 rows and 5 primaries**. `stage.py` embeds the readings and recreates the manifest and deterministic gzip using only Python's standard library.

## Changes on 3 November 2026 (thinktanks-b review)

- **Finding 1:** CPS's £3.1 billion PuFins row is context. It names no Budget decision, line or year and ties the figure to a CPS paper from before the Budget, so it carries no proposed key; `reform_hint` is null and `conditions.measure_type` names it. `ab2026__package_cps_public_financial_institutions` is withdrawn.
- **Finding 5:** Trussell's row and primary moved to the AB2026 family `uk_trussell_wpi`, with source `trussell_wpi`, as AB2025 staged Trussell's Budget responses. This family now has 12 rows and 5 primaries.
- **Finding 6:** IfG's count of one tax measure names the measure it counted in `conditions.subgroup`, not `component`, which rule 9 reserves for parts of a measure.

No primary was re-opened on 3 November (the session's network policy refused every producer's site); every change relabels fields, and no printed value changed. The 29 October record below is updated for the new row set.

## Changes on 4 November 2026 (reviews A and B)

Review B (PR #231, issue comment 6635498758) approved this family with fixes, and review A's H-6(a) asked for its finding 2. The fixes sit in a block after the rows in `stage.py`, shared word for word with `uk_trussell_wpi`'s (judgement call 10). No primary was re-opened, and no value changed.

- **Finding 1:** IfG's "around 80%" (row 8) restates HM Treasury's paragraph 3.5, which `uk_hmt_redbook` row 193 stages: `restated`, `source_model: administrative_data`, `conditions.originator: "HM Treasury, Budget 2026 para 3.5"`, geography England, denominator "households in England (HM Treasury)", and a rewritten note. Own 4, restated 8.
- **Finding 2 and H-6(a):** rows 2, 8 and 10 carry the registered `fiscal_headroom`, `affected_share` and `affected_count` in `metric`, with `proposed_metric` null.
- **Finding 3:** row 9's `measure_type` is "real household disposable income per person".
- **H-6(d):** row 11 (Citizens Advice) carries `geography: "not stated"`.

## Access recipe and primary hashes

Every primary was fetched afresh on 29 October 2026 using `curl -sSL -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"`; every response was HTTP 200. The lane kept the HTML bytes, headers and text extracts in its local primaries folder. Hashes were checked using `shasum -a 256`. BeautifulSoup extracts were used to read the page's own body text; hashes refer to HTML, not extracts. There are no PDFs or spreadsheets in this family.

No assigned local copies or earlier document versions were supplied. There was no blocked fetch, fallback or observed replacement. Fetch-completion timestamps are recorded in each manifest note because HTML can change.

| Primary | Fetch completion (UTC) | Bytes | Rows | SHA256 |
|---|---|---:|---:|---|
| [CPS verdict](https://cps.org.uk/media/post/2026/a-dangerous-continuation-of-labours-tax-and-spend-fantasy-cps-verdict-on-the-budget/) | 2026-10-29 15:22:34 | 70,197 | 4 | `2c832e011866eb9f63f20597e7bf43bc01d44b6b1b5be43eee866ad6fc5ecd24` |
| [IfG commentary](https://www.instituteforgovernment.org.uk/comment/john-healeys-underwhelming-budget) | 2026-10-29 15:22:31 | 153,352 | 6 | `ecf19f14b4f808846fb8230b28a3244b0b65812484735842f9ab537a50195c69` |
| [Age UK response](https://www.ageuk.org.uk/latest-press/age-uk-response-to-the-budget/) | 2026-10-29 15:22:31 | 105,862 | 0 | `3035a8bbbb0f023dc24e805b430052163aa0dbfce3c975a6e0a0568983db6bf0` |
| [Learning and Work Institute response](https://learningandwork.org.uk/responding-to-autumn-budget-2026/) | 2026-10-29 15:22:31 | 122,809 | 1 | `c7fe077a0d9f4784aa4c91c906bcefa087cc9a4ece8b28026d24347c2a8b5dcf` |
| [Citizens Advice response](https://www.citizensadvice.org.uk/about-us/media-centre/press-releases/citizens-advice-responds-to-chancellors-budget/) | 2026-10-29 15:23:24 | 22,671 | 1 | `6a10336a67fc058512a4ccd9d0e80a27470fee8ba5775690fb1fcba39db67385` |

Citizens Advice's press index linked its dated response. The other four URLs were assigned. CPS prints “Date Added: Wednesday 28th October 2026”; IfG prints “28 OCT 2026”; LWI prints “28 October 2026”; Age UK prints publication on 28 October 2026 at 04:14 PM and last update that date.

## Coverage and conventions

Reading order is CPS, IfG, Age UK, LWI, Citizens Advice, then top to bottom within each page. Only contiguous excerpts under 15 words are quoted. There are no chart readings or derived gaps, totals, ratios or annualisations.

| Source | Rows | Own | Restated |
|---|---:|---:|---:|
| `cps` | 4 | 1 | 3 |
| `institute_for_government` | 6 | 2 | 4 |
| `learning_and_work_institute` | 1 | 0 | 1 |
| `citizens_advice` | 1 | 1 | 0 |
| `age_uk` (manifest only) | 0 | 0 | 0 |
| Total | 12 | 4 | 8 |

| Measure key | Rows | Scope |
|---|---:|---|
| `ab2026__household_energy_payment_100_bands_a_to_d` | 1 | IfG's share of households in England receiving the £100 council-tax rebate for bands A–D (restating HM Treasury's paragraph 3.5); Table 6.1 line 1 |
| `null` | 11 | context and document-tally observations; none carries a proposed key |

The sole registered key is attached to the specific rebate's coverage, not to the entire cost-of-living package. IfG's exact identification of the £100 council-tax rebate for bands A–D identifies line 1; it gives no contrary scope. Its "around 80%" restates HM Treasury's paragraph 3.5 ("around 80% of households in England"), so the row is `restated`, `administrative_data`, geography England, as `uk_hmt_redbook` row 193 stages it (changed on 4 November, review B finding 1). Context forecasts, outturns and document counts, including CPS's PuFins assertion, have null measure keys and null reform hints.

- GBP values preserve printed signs and cash magnitudes. “Tops £3 trillion” is the printed strict lower bound of debt stock. The six-month £61 billion debt-interest total is not multiplied to a year. Fiscal headroom is positive headroom; PuFins' £3.1 billion is a positive debt increase. No sign is reversed.
- Percentages remain percentages. “Almost 100” retains the printed upper threshold 100; no exact policy count is inferred. “Around 80%” retains the qualifier in conditions.
- `point`, rather than `central`, records each single published observation/forecast: none is labelled a central scenario. Thresholds use `range_low` or `range_high`. The 2% real-income growth is `cumulative` over the printed comparison window, not a 2% annual rate.
- Only IfG's fiscal-rule probabilities name a fiscal year: “2029/30” is normalised to `fy: 2029-30`, period 2030, `fiscal_year`. The income projection prints calendar 2030 and uses `annual` without `fy`. Other observations use the publication-year point-in-time anchor 2026 and preserve “last six months”, “this winter”, “each year”, “last 12 months”, or unspecified horizon explicitly. They do not claim a fiscal/calendar scoring year that the producer did not print. The PuFins annual-rate assertion has medium confidence because no scoring year or fiscal/calendar basis is supplied.
- Real income remains real; all other price bases are left unspecified where the page does not identify one. No baseline proposal is needed for these current observations and explicitly named context comparisons.
- CPS's own PuFins assertion uses `source_model: unstated` because it does not identify its calculation. Official debt/outturn context uses `administrative_data` and `administrative_fact`. CPS headroom and IfG fiscal probabilities/income forecasts are `restated`, `obr_efo_forecast`, `different_model`. The precise original release behind the unsourced CPS figures is not identified, so these originator assignments are explicit in rows.
- IfG's two counts are its own `arithmetic`, `different_model` observations. Its rebate share restates HM Treasury (paragraph 3.5): `restated`, `administrative_data`, `conditions.originator` naming the paragraph (changed on 4 November). LWI's rounded NEET figure is treated as restated official labour-market context, `administrative_data`, `administrative_fact`; its response gives neither a quarter, age range nor a citation. Citizens Advice's unsourced bill forecast is treated as its own assertion with `source_model: unstated`, with missing method/geography acknowledged. Citizens Advice's estimate, CPS's PuFins assertion and IfG's rebate share have medium confidence; the other nine rows have high confidence.

## Proposed keys, metrics and units

No measure key is proposed. CPS's PuFins row is context (see the 3 November changes above).

Registered metrics (since 4 November, review A's H-6(a) and review B's finding 2; `models.py` registers them, so they go in `metric`, not `proposed_metric`):

- `fiscal_headroom` (1; GBP): CPS's current post-Budget buffer against the fiscal rule; target year unspecified.
- `affected_share` (1; percent): IfG's share of households in England receiving the rebate, restating HM Treasury.
- `affected_count` (1; persons): LWI's rounded current count of young people not in education, employment or training.

Proposed metrics (counts and exact meaning):

- `public_debt_level` (1; GBP): CPS's current national-debt stock lower bound; no series definition is supplied.
- `debt_interest_cost` (1; GBP): CPS's total debt interest over the last six months, not the change caused by a measure.
- `public_debt_change` (1; GBP): CPS's asserted annual debt increase through PuFins, a context row; period limitations above.
- `measure_count` (2; proposed unit `measures`; AB2025 family precedent): IfG's approximate full scorecard count and exact count of tax measures costing/saving more than £1bn in the last forecast year.
- `fiscal_rule_probability` (2; percent): current and last-budget OBR probabilities of a current-budget surplus in 2029/30, as reported by IfG.
- `average_energy_bill_change` (1; GBP/month; AB2025 IFS/RF proposal spelling): Citizens Advice's forecast monthly household energy-bill increase, excluding any assertion that this is a Budget measure effect.

Registered `real_income_growth` accounts for IfG's restated OBR 2% cumulative growth in real household disposable income per person (EFO para 1.2; `conditions.measure_type` says "per person" since 4 November, review B finding 3). Proposed unit `measures` is used only for the two counts. Other units are registered. There are no proposed baselines.

## Not staged and primary limitations

- **Age UK: zero rows.** Its own response has no numeric Budget estimate. The exact “On Income Tax threshold.” subsection was read; it welcomes protecting low-income pensioners from cash tax demands but prints no number. Dates, contact numbers, navigation “Nearly 4,000 flu mortalities” and the unrelated £2 donation link are not Budget claims.
- IfG's £100 rebate is a bare policy parameter; its 80% coverage is staged separately. The £1bn cutoff defines its count of one tax measure and is preserved in conditions rather than misrepresented as that measure's costing. Other dates and the 1991 council-tax valuation year are context labels, not model outcomes.
- LWI mentions extra Mayoral apprenticeship funding and OBR employment effects but prints no amount or employment effect. Its “one million” NEET level is retained as context. Navigation cards and unrelated articles are not harvested.
- Citizens Advice gives no source, exact winter dates, geography or method for £60/month (`geography: "not stated"` since 4 November, for the contract's closed geography list). Those are explicit limitations, not supplied from secondary material.
- CPS does not link its “paper released last week”. It is outside the assigned 28–29 October post-Budget window, and no unseen figures from it are staged. The comparison between six-month debt interest and an annual defence budget prints no second amount or exact ratio, so none is derived.
- No restated figure is silently removed: the seven official/OBR context rows and IfG's restatement of HM Treasury's 80% are staged with `restated` and an originator. No PolicyEngine restatement was identified.
- No pages were unreached. No charts contain unstaged numeric labels in these primaries.

Potentially ambiguous source wording is retained: IfG describes the £100 rebate as reaching “around 80%” of households without naming the denominator's geography; HM Treasury's paragraph 3.5, which it restates, says households in England, so the row carries England (4 November). CPS's PuFins claim lacks components, annual dates and method, so it stays context; its £15 billion headroom lacks a target year. Age UK's Pension Tax Allowance paragraph contains no number despite the assignment's pointer. These gaps have not been repaired using other sources.

## Verification

- **4 November:** the contract checker reports 12 rows, 0 problems, and a re-run of `stage.py` reproduces both files byte for byte.
- **3 November:** the contract checker reports 12 rows, 0 problems; a re-run of `stage.py` reproduces `manifest.jsonl` and `claims_staged.jsonl.gz` byte for byte (COUNTS.json pins the gzip's sha256). The fixes relabel fields only, so the lane's checks below stand for the rows that remain.
- **29 October (13 rows, including Trussell's, now in `uk_trussell_wpi`):**


Command:

```text
PYTHONPATH=. uv run -q python pipeline/ab2026_harvest_contract.py sources/harvest-uk-ab2026-2026-10-29/uk_thinktank_misc
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

Scope review found one non-null key: IfG's specifically identified bands A–D £100 rebate, Table 6.1 line 1. No broader support-package figure is attached to that key. (On 3 November the CPS row lost its proposed key; see above.) No git state-changing commands, commits or pushes were run.
