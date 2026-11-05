# Smaller producers: Autumn Budget 2026

We keep `stage.py`, which writes `manifest.jsonl` and `claims_staged.jsonl.gz`, on branch `uk/ab2026-harvest-staging` at `harvest-staging/ab2026/lanes/thinktanks-b/uk_thinktank_misc/stage.py`. We commit only NOTES.md, `manifest.jsonl` and `claims_staged.jsonl.gz` to this branch, and the repository holds no primary bytes. The lane never committed its local primaries folder (`.ab2026-primaries/`), so fetch each primary from its `manifest.jsonl` URL and check its sha256.

We staged this family from five primary HTML responses that their producers published on 28 October 2026. We use the sources `cps`, `institute_for_government`, `learning_and_work_institute` and `citizens_advice`; we manifested Age UK's response but staged zero rows from it. We stage **12 rows and 5 primaries**. We embedded the readings in `stage.py`, which recreates the manifest and deterministic gzip with only Python's standard library.

## Changes on 3 November 2026 (thinktanks-b review)

- Finding 1: we made CPS's £3.1 billion PuFins row context. CPS names no Budget decision, line or year and ties the figure to a CPS paper from before the Budget, so we gave the row no proposed key. We set `reform_hint` to null, named the row's subject in `conditions.measure_type` and withdrew `ab2026__package_cps_public_financial_institutions`.
- Finding 5: we moved Trussell's row and primary to the AB2026 family `uk_trussell_wpi`, with source `trussell_wpi`, as we staged Trussell's Budget responses in AB2025. This family now has 12 rows and 5 primaries.
- Finding 6: for IfG's count of one tax measure, we now name the measure it counted in `conditions.subgroup`, not `component`, which we use only for parts of a measure (rule 9).

We re-opened no primary on 3 November, because the session's network policy refused every producer's site. We only relabelled fields, changed no printed value and updated the 29 October record below for the new row set.

## Changes on 4 November 2026 (reviews A and B)

Review B (PR #231, issue comment 6635498758) approved this family with fixes, and review A's H-6(a) asked for its finding 2. We put the fixes in a block after the rows in `stage.py`, shared word for word with `uk_trussell_wpi`'s (judgement call 10). We re-opened no primary and changed no value.

- Finding 1: in "around 80%" (row 8) IfG restates HM Treasury's paragraph 3.5, which we stage as `uk_hmt_redbook` row 191. We now mark the row `restated`, with `source_model: administrative_data`, `conditions.originator: "HM Treasury, Budget 2026 para 3.5"`, geography England, denominator "households in England (HM Treasury)" and a rewritten note. Own 4, restated 8.
- Finding 2 and H-6(a): we now record the registered `fiscal_headroom`, `affected_share` and `affected_count` in `metric` on rows 2, 8 and 10, with `proposed_metric` null.
- Finding 3: we set row 9's `measure_type` to "real household disposable income per person".
- H-6(d): we set `geography: "not stated"` on row 11 (Citizens Advice).

## Access recipe and primary hashes

We fetched every primary afresh on 29 October 2026 with `curl -sSL -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"`, and every server answered HTTP 200. The lane kept the HTML bytes, headers and text extracts in its local primaries folder and checked hashes with `shasum -a 256`. It read each page's own body text from BeautifulSoup extracts, but hashed the HTML, not the extracts. We staged no PDF or spreadsheet in this family.

Nobody supplied assigned local copies or earlier document versions, and we hit no blocked fetch, used no fallback and saw no replacement. Because HTML can change, we record the fetch-completion time in each manifest note.

| Primary | Fetch completion (UTC) | Bytes | Rows | SHA256 |
|---|---|---:|---:|---|
| [CPS verdict](https://cps.org.uk/media/post/2026/a-dangerous-continuation-of-labours-tax-and-spend-fantasy-cps-verdict-on-the-budget/) | 2026-10-29 15:22:34 | 70,197 | 4 | `2c832e011866eb9f63f20597e7bf43bc01d44b6b1b5be43eee866ad6fc5ecd24` |
| [IfG commentary](https://www.instituteforgovernment.org.uk/comment/john-healeys-underwhelming-budget) | 2026-10-29 15:22:31 | 153,352 | 6 | `ecf19f14b4f808846fb8230b28a3244b0b65812484735842f9ab537a50195c69` |
| [Age UK response](https://www.ageuk.org.uk/latest-press/age-uk-response-to-the-budget/) | 2026-10-29 15:22:31 | 105,862 | 0 | `3035a8bbbb0f023dc24e805b430052163aa0dbfce3c975a6e0a0568983db6bf0` |
| [Learning and Work Institute response](https://learningandwork.org.uk/responding-to-autumn-budget-2026/) | 2026-10-29 15:22:31 | 122,809 | 1 | `c7fe077a0d9f4784aa4c91c906bcefa087cc9a4ece8b28026d24347c2a8b5dcf` |
| [Citizens Advice response](https://www.citizensadvice.org.uk/about-us/media-centre/press-releases/citizens-advice-responds-to-chancellors-budget/) | 2026-10-29 15:23:24 | 22,671 | 1 | `6a10336a67fc058512a4ccd9d0e80a27470fee8ba5775690fb1fcba39db67385` |

We followed Citizens Advice's press index to its dated response; the coordinator assigned the other four URLs in the lane's brief (`harvest-staging/ab2026/briefs/thinktanks-b.md` on the staging branch). CPS prints “Date Added: Wednesday 28th October 2026”, IfG prints “28 OCT 2026” and LWI prints “28 October 2026”. Age UK prints publication on 28 October 2026 at 04:14 PM and a last update that date.

## Coverage and conventions

We read in the order CPS, IfG, Age UK, LWI, Citizens Advice, then top to bottom within each page, and quote only contiguous excerpts under 15 words. We read no charts and derived no gaps, totals, ratios or annualisations.

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

We attach the sole registered key to the specific rebate's coverage, not to the entire cost-of-living package. IfG names the £100 council-tax rebate for bands A–D, so we match it to line 1, and IfG gives no contrary scope. Its "around 80%" restates HM Treasury's paragraph 3.5 ("around 80% of households in England"). So we mark the row `restated`, `administrative_data`, geography England, as we stage `uk_hmt_redbook` row 191; we made that change on 4 November, after review B finding 1. We gave null measure keys and null reform hints to context forecasts, outturns and document counts, including CPS's PuFins assertion.

- We keep printed signs and cash magnitudes in GBP values and take “Tops £3 trillion” as the printed strict lower bound of debt stock; we don't multiply the six-month £61 billion debt-interest total to a year. We record fiscal headroom as positive headroom and PuFins' £3.1 billion as a positive debt increase, and we reversed no sign.
- We keep percentages as percentages. For “Almost 100” we keep the printed upper threshold 100 and infer no exact policy count. For “Around 80%” we keep the qualifier in conditions.
- We record each single published observation or forecast as `point`, not `central`, because no producer labels one a central scenario. We use `range_low` or `range_high` for thresholds. We record the 2% real-income growth as `cumulative` over the printed comparison window, not a 2% annual rate.
- Only IfG names a fiscal year, for its fiscal-rule probabilities: we normalise “2029/30” to `fy: 2029-30`, period 2030, `fiscal_year`. IfG prints calendar 2030 for the income projection, so we use `annual` without `fy`. For the other observations we use the publication-year point-in-time anchor 2026 and keep “last six months”, “this winter”, “each year”, “last 12 months” or the unspecified horizon explicitly. We claim no fiscal or calendar scoring year that the producer did not print. We give the PuFins annual-rate assertion medium confidence, because CPS supplies no scoring year and no fiscal or calendar basis.
- We keep real income real, and leave every other price basis unspecified where the producer names none. These current observations and explicitly named context comparisons need no baseline proposal.
- CPS doesn't identify the calculation behind its own PuFins assertion, so we use `source_model: unstated`. We use `administrative_data` and `administrative_fact` for official debt and outturn context. We mark CPS's headroom and IfG's fiscal probabilities and income forecasts `restated`, `obr_efo_forecast`, `different_model`. We couldn't identify the original release behind CPS's unsourced figures, so we state these originator assignments in the rows.
- We record IfG's two counts as its own `arithmetic`, `different_model` observations. Its rebate share restates HM Treasury (paragraph 3.5), so since 4 November we mark it `restated`, `administrative_data`, with `conditions.originator` naming the paragraph. We treat LWI's rounded NEET figure as restated official labour-market context, `administrative_data`, `administrative_fact`; LWI gives no quarter, age range or citation. We treat Citizens Advice's unsourced bill forecast as its own assertion with `source_model: unstated`, and we record that it gives no method or geography. We give Citizens Advice's estimate, CPS's PuFins assertion and IfG's rebate share medium confidence, and the other nine rows high confidence.

## Proposed keys, metrics and units

We propose no measure key. We made CPS's PuFins row context (see the 3 November changes above).

Since 4 November, after review A's H-6(a) and review B's finding 2, we record these registered metrics in `metric`, not `proposed_metric`, because `models.py` registers them:

- `fiscal_headroom` (1; GBP): CPS's current post-Budget buffer against the fiscal rule; target year unspecified.
- `affected_share` (1; percent): IfG's share of households in England receiving the rebate, restating HM Treasury.
- `affected_count` (1; persons): LWI's rounded current count of young people not in education, employment or training.

We propose these metrics (counts and exact meaning):

- `public_debt_level` (1; GBP): CPS's current national-debt stock lower bound; CPS supplies no series definition.
- `debt_interest_cost` (1; GBP): CPS's total debt interest over the last six months, not the change caused by a measure.
- `public_debt_change` (1; GBP): CPS's asserted annual debt increase through PuFins, a context row; period limitations above.
- `measure_count` (2; proposed unit `measures`; AB2025 family precedent): IfG's approximate full scorecard count and exact count of tax measures costing/saving more than £1bn in the last forecast year.
- `fiscal_rule_probability` (2; percent): current and last-budget OBR probabilities of a current-budget surplus in 2029/30, as reported by IfG.
- `average_energy_bill_change` (1; GBP/month; AB2025 IFS/RF proposal spelling): Citizens Advice's forecast monthly household energy-bill increase, excluding any assertion that this is a Budget measure effect.

We record IfG's restatement of the OBR's 2% cumulative growth in real household disposable income per person (EFO para 1.2) under the registered `real_income_growth`. Since 4 November, after review B finding 3, `conditions.measure_type` says "per person". We use the proposed unit `measures` only for the two counts, and registered units for the rest. We propose no baselines.

## What we left out, and the primaries' limits

- **Age UK: zero rows.** Age UK prints no numeric Budget estimate in its own response. We read the exact “On Income Tax threshold.” subsection; Age UK welcomes protecting low-income pensioners from cash tax demands there but prints no number. We didn't treat dates, contact numbers, the navigation's “Nearly 4,000 flu mortalities” or the unrelated £2 donation link as Budget claims.
- IfG gives the £100 rebate as a bare policy parameter, and we stage its 80% coverage separately. IfG counts one tax measure above a £1bn cutoff, and we keep the cutoff in conditions, not as that measure's costing. We treat the other dates and the 1991 council-tax valuation year as context labels, not model outcomes.
- LWI mentions extra Mayoral apprenticeship funding and OBR employment effects but prints no amount or employment effect. We keep its “one million” NEET level as context, and we harvested no navigation cards or unrelated articles.
- Citizens Advice gives no source, exact winter dates, geography or method for £60/month. Since 4 November we set `geography: "not stated"`, to fit the contract's closed geography list. We record those gaps as explicit limitations and filled none of them from secondary material.
- CPS does not link its “paper released last week”. That paper falls outside the assigned 28–29 October post-Budget window, and we staged no unseen figures from it. CPS compares six-month debt interest with an annual defence budget but prints no second amount or exact ratio, so we derived none.
- We stage the seven official/OBR context rows and IfG's restatement of HM Treasury's 80% with `restated` and an originator. We found no PolicyEngine restatement.
- We reached every page, and found no chart in these primaries with unstaged numeric labels.

IfG describes the £100 rebate as reaching “around 80%” of households without naming the denominator's geography. HM Treasury's paragraph 3.5, which IfG restates, says households in England, so since 4 November we record England on the row. CPS gives no components, annual dates or method for its PuFins claim, so we keep that row as context. CPS also gives no target year for its £15 billion headroom. Age UK prints no number in its Pension Tax Allowance paragraph despite the assignment's pointer. We repaired none of these gaps from other sources.

## Verification

- On 4 November, the contract checker reported 12 rows, 0 problems, and when we re-ran `stage.py` it reproduced both files byte for byte.
- On 3 November, the contract checker reported 12 rows, 0 problems, and when we re-ran `stage.py` it reproduced `manifest.jsonl` and `claims_staged.jsonl.gz` byte for byte (COUNTS.json pins the gzip's sha256). We only relabelled fields, so the lane's checks below stand for the rows that remain.
- On 29 October, the lane checked 13 rows, including Trussell's, now in `uk_trussell_wpi`:


Command:

```text
PYTHONPATH=. uv run -q python pipeline/ab2026_harvest_contract.py sources/harvest-uk-ab2026-2026-10-29/uk_thinktank_misc
sources/harvest-uk-ab2026-2026-10-29/uk_thinktank_misc: 13 rows, 0 problems
```

The lane re-ran `python3 sources/harvest-uk-ab2026-2026-10-29/uk_thinktank_misc/stage.py`, and the claims SHA256 before and after read **`d677dde1f96e629097696f5d17b575c8f1d34baaca42b96297cd46be773669ea`**. The stager writes the gzip header with mtime zero and no original filename. The lane checked manifest byte counts and all six primary hashes, Trussell's included, against the saved HTML. It verified that all 13 quotes appear as contiguous text in their pinned primary, run under 15 words and contain their `value_raw`.

The lane drew its random sample with `random.Random(230).sample(range(13), 10)`, using zero-based indexes, and reports one-based row numbers below. For each, it reopened the saved primary, checked its SHA256 and read the paragraph at the locator to verify the number, sign, unit and period. It also checked the three remaining rows (CPS debt interest, IfG count of one, Trussell share) for quote/value correspondence and basis.

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

In its scope review the lane found one non-null key: IfG's specifically identified bands A–D £100 rebate, Table 6.1 line 1. We attach no broader support-package figure to that key, and on 3 November we removed the CPS row's proposed key (see above). The lane ran no git state-changing commands, commits or pushes.
