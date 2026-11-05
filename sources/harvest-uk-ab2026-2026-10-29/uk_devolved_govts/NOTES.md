# uk_devolved_govts — devolved governments, Autumn Budget 2026

We keep `stage.py`, which writes `manifest.jsonl` and `claims_staged.jsonl.gz`, on branch `uk/ab2026-harvest-staging` at `harvest-staging/ab2026/lanes/thinktanks-b/uk_devolved_govts/stage.py`. We commit only NOTES.md, `manifest.jsonl` and `claims_staged.jsonl.gz` to this branch, and no primary bytes to the repository. The lane never committed its local primaries folder (`.ab2026-primaries/`), so fetch each primary from its `manifest.jsonl` URL and check its sha256.

We stage **19 rows from two primaries.** Rows 0–13 (0-based) come from the Welsh Government (source `welsh_government`), and rows 14–18 from the Scottish Government (source `scottish_government`). The lane staged the Scottish rows in `uk_fai_sfc` on 29 October. On 3 November, after finding 7 of the thinktanks-b review, we moved them here so that both devolved governments share one family; we left `uk_fai_sfc` with no rows and don't commit it (see the harvest README). We follow the conventions of the AB2025 `uk_fai_sfc` block-grant rows (`source_model: arithmetic`).

## Changes on 3 November 2026 (thinktanks-b review)

- Finding 2: we gave the Welsh Table 1 Resource and Capital cells (rows 1–7) `conditions.row_type: "measure_component"` with their `component`. We gave the four Total cells and the £448m headline (rows 0 and 8–11) `row_type: "total"` and no `component`. On 4 November we superseded that, and all twelve now form parts of the three-government package (see "Changes on 4 November 2026", finding 1). An ingest can no longer add parts to their total.
- Finding 3: we named the Welsh package key for its scope, not the nation: `ab2026__package_barnett_consequentials`, which we share with HM Treasury's figures for the same scope in `uk_hmt_redbook`. We record the nation in `conditions.geography`.
- Finding 4: we gave the seven real-terms settlement rows (Welsh rows 12–13, Scottish rows 14–18) `proposed_metric: devolved_funding_real_terms_change`. In AB2025 we used `block_grant_effect` for a policy's effect on the grant, positive for an increase. In these rows the two governments instead give a year-on-year real-terms change in the whole settlement, which we store as positive for a reduction.
- Finding 7: we moved the Scottish Government's rows here (above), and we now list both slugs in the harvest README's slug table.
- `component` on context rows: on the seven real-terms rows we had named their budget (Resource, Capital and so on) in `component`, which we use only for parts of a measure (rule 9). Following the reasoning of the review's finding 6, we now name it in `budget`.
- Attribution, which the coordinator checked under finding 3: we keep the Welsh rows `own`. The Welsh Government cites no source, and the coordinator's settled calls do not change this; we stage HM Treasury's own consequentials as HM Treasury's in `uk_hmt_redbook`.

We re-opened no primary on 3 November, because the session's network policy refused gov.wales and gov.scot. We only relabelled fields and changed no printed value.

## Changes on 4 November 2026 (review B)

Review B (PR #231, issue comment 6635498758) approved this family with fixes, and the coordinator settled the Barnett key with review A's K-7(b) in the brief (section 3.3). We put the fixes in `review_fixes()` in `stage.py`, re-opened no primary and changed no value.

- Finding 1 (Barnett): we give the shared key the red book's scope. HM Treasury prints the £1.3bn (red book row 252), and we take it as the total and each government as a part (rule 9: "a part can be ... a nation"). So we mark rows 0 and 8–11 `measure_component` with `component: "Welsh Government"`, name rows 1–7 `"Welsh Government: Resource"` or `"Welsh Government: Capital"`, and give row 0 `fy: 2029-30`. In the section on the package key below, we give it the red book's scope.
- Finding 2: we changed row 13's locator to "third sentence", and we no longer repeat row 12's "next financial year" sentence in its note. We set rows 14–18's `source_column` to null, as on rows 12–13, because we wrote those labels and the producer didn't print them. We removed the old `uk_fai_sfc` folder's name from the Scottish manifest note. We corrected the sentence that called the Welsh package mapping "unresolved".

## Coverage

| Primary | Position | Rows | Coverage |
|---|---|---:|---|
| Welsh written statement | Paragraph before Table 1 | 1 | £448m cumulative headline (component "Welsh Government") |
| | Table 1, Resource row | 3 | 199 / 165 / 146 (£m); 2029-30 is N/A (component "Welsh Government: Resource") |
| | Table 1, Capital row | 4 | -27 / -19 / 2 / -18 (£m) (component "Welsh Government: Capital") |
| | Table 1, Total row | 4 | 172 / 146 / 148 / -18 (£m) (component "Welsh Government") |
| | Paragraphs after Table 1 | 2 | 0.5% resource and almost 10% capital real-terms reductions (context) |
| Scottish Government news release | Opening paragraph and paragraph 2 | 5 | £650 million; 1.3% and £550 million (resource); 1.5% and £100 million (capital), all 2027-28 real-terms reductions (context) |

By `measure_key`: **`ab2026__package_barnett_consequentials` 12, null 7**. We key the twelve Welsh package rows to it, all `measure_component`, since Wales forms a part of the three-government package. On 3 November we gave these rows the key as a proposal, and in tranche 2 we registered it. We stage the seven real-terms rows as context with no key. By metric we give 12 rows `block_grant_effect` and 7 `devolved_funding_real_terms_change`; by unit, 15 `gbp` and 4 `percent`; we mark all 19 `own`, benchmark `different_model`.

## Package key

We give `ab2026__package_barnett_consequentials` (12 rows here) the scope we give it in `uk_hmt_redbook`. It covers the Barnett consequentials of "decisions confirmed at Budget" for the Scottish, Welsh and Northern Ireland governments together, 2026-27 to 2029-30. It excludes the technical reduction from lower employer pension contributions (red book paragraph 4.150). We scope the key across Table 6.1's England spending lines, and HM Treasury prints no line of its own for it. HM Treasury prints the £1.3bn three-government figure (`uk_hmt_redbook` row 252), and we take it as the key's total and each government's figure as a component. So we mark every Welsh row here `row_type: measure_component`. We give the £448m ("an additional £448m of funding over the current spending review period", `fy` 2029-30, cumulative) and the four Table 1 Totals `component: "Welsh Government"`, and the Resource and Capital cells `"Welsh Government: Resource"` and `"Welsh Government: Capital"`. The Welsh Government, like HM Treasury, leaves employer-pension-contribution savings out of its figures. Compare the Welsh £448m with HM Treasury's £450m for Wales (red book row 254), component with component; never add either to the £1.3bn.

## Welsh Government

### Access

The Welsh Government first published and last updated the
[written statement](https://www.gov.wales/written-statement-welsh-government-response-uk-autumn-budget-2026)
on 28 October 2026. The lane fetched it fresh with `curl -sSL` and the exact
requested User-Agent:

```text
Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15
```

The server answered HTTP 200, with response Date 2026-10-29T15:22:18Z. The
lane saved the unaltered HTML and response headers in its local primaries
folder. It read the page's paragraphs and actual HTML table cells with
BeautifulSoup, not chart geometry. `shasum -a 256` gives:

```text
87490552c36d8ffd5787db18127704e467d93599e5708627adb6da7dcfe17c7c
```

The fetched primary runs to 26,908 bytes. Nobody provided a local copy, we
used no fallback, and we have no earlier assigned version against which to
establish a change. We reached every requested Welsh page.

### Attribution

The Welsh Government publishes these figures as its own settlement accounting and real-terms comparisons. In the statement the Welsh Government credits no other producer for these calculations, so we infer no HM Treasury attribution. The Welsh Government reports prospective funding changes, not administrative outturns or counts. It names no formal model, so we use `arithmetic` for the settlement accounting.

### Welsh numeric and period conventions

- We multiply the printed £m cells or headline by one million to get GBP
  values. We keep signed table values, with positive for an increase in
  Welsh funding, and derive no totals or differences.
- The Welsh Government heads the table columns with fiscal years, so we set
  `period` to the end year and keep the printed year in `fy`. The Welsh
  Government gives the £448m headline as cumulative over the four displayed
  years. We record it at `period: 2030` and `fy: 2029-30` (the horizon's
  final year) and state that horizon; the £448m doesn't measure
  2029-30 alone.
- Given the publication date, we read the resource real-terms reduction
  “next financial year” as 2027-28. The Welsh Government dates the capital
  reduction explicitly by 2029-30. We keep the printed magnitude of the
  percentages and state in the conditions that positive means a reduction. We keep
  “Almost 10%” in `value_raw`, mark the upper endpoint 10 `range_high` and
  keep the qualifier.
- The Welsh Government states no real-terms basis for the monetary table,
  and we apply no deflation. We keep the percentage context rows in real
  terms and invent no price year. Every row concerns Wales.
- We use `value_kind: point` for a single published figure, not a separately
  identified central-model scenario, and use `central` on no row.
- We quote an exact page fragment or table cell in every row, containing
  `value_raw` and fewer than 15 words. We read tables by row and then column.

### Welsh figures we left out

- The Welsh Government prints Resource 2029-30 as `N/A`, not a number and not zero.
- The Welsh Government restates OBR GDP growth of 1.2% in 2026 and 1.0% in
  2027 as macro context. That falls outside this assignment's
  devolved-consequentials scope, and the Welsh Government asserts no own
  estimate of a Budget measure there.
- The Welsh Government announces how it will implement the £100
  council-tax-band A-D payment, a policy parameter, but prints no
  implementation date, reach, aggregate cost or estimated household gain. We
  didn't attach it to the England-only Treasury line 1 key or fabricate an
  impact row from it.
- We treat the £14 billion rail commitment and the £302m already allocated
  over the spending review as existing commitments, not newly estimated
  effects of AB2026; the statement doesn't isolate a Budget measure's
  effect.
- We don't count dates, council tax band letters or rounding caveats as
  estimates, and the Welsh Government prints no charts that need bar
  readings. We use no inaccessible Welsh page or unavailable local copy as evidence.

## Scottish Government

The lane fetched the [news release](https://www.gov.scot/news/uk-budget-delivers-real-cut-to-scotlands-funding/) ("UK Budget delivers real cut to Scotland's funding", 28 October 2026) fresh on 2026-10-29 with the same User-Agent: HTTP 200, 27,662 bytes, sha256 `f3d0183e470f711b6821e4956e108c5d17210a392e6a6e471eccf297c807a6ac`.

- **Sign.** The Scottish Government prints unsigned magnitudes and describes reductions. We keep those positive magnitudes, with `conditions.sign_convention: "positive = magnitude of reduction in Scottish Government funding"`, and invent no minus sign. We multiply the three million-pound amounts by 1e6 and keep the percentages as percentages.
- **Period.** On all rows we use fiscal-year end year `2028`, `time_basis: fiscal_year` and `conditions.fy: "2027-28"`.
- **Prices and comparison.** The Scottish Government gives every figure in real terms, with an unspecified price base year, and doesn't explicitly name its comparison baseline. We record those limits in `conditions.price_basis` and `comparison_basis`, and make no cash-basis conversion.
- **Point or central.** The Scottish Government reports one estimate per figure, not a named central model scenario, so we use `value_kind: point`. We keep its “around” qualifier on the money amounts in `conditions.precision`.
- **Attribution.** We mark all 5 as the Scottish Government's `own` estimates, because it reports its funding assessment without naming a separate original source. We use `arithmetic` to follow the AB2025 family's funding convention, without claiming access to an unpublished model. The Scottish Government reports no administrative outturn or count here.
- **Baselines.** We set `baseline_policy: null` and propose no baseline. We stage these funding projections as context: the Scottish Government doesn't compare a reform with a specified alternative policy.
- **Keys.** We give **5 rows `measure_key: null`**. We use no registered key and introduce **no proposed measure key**. The Scottish Government doesn't isolate a set of Table 6.1 decisions or show that its year-on-year real-terms funding assessment matches a registered package. We set `reform_hint: null` to record that we stage the rows as context. We assert none of the 98 Table 6.1 lines as the exact scope of these figures.

### Scottish figures we left out

- Every FAI figure: FAI's site refused the required fresh fetch, and nobody supplied a local fallback. So we read no primary evidence for FAI's quantitative or qualitative claims.
- SFC: we found no qualifying publication dated 28–29 October, and we don't recast its earlier forecasts and funding commentary as post-Budget figures.
- The Scottish Government's £100 household energy-support commitment: the Scottish Government sets a payment-policy parameter, not a separate quantified aggregate or model estimate. It specifies no Scottish eligibility, rollout timing or fully defined Scottish implementation, and on the registered Table 6.1 line 1 HM Treasury describes England's council-tax rebate. We attach no England measure key to Scotland's unspecified implementation.
- The Scottish Government's £300 energy-bill reduction refers to an earlier political promise, not an AB2026 estimate or a newly costed option.
- We don't stage the minister's repeated £650 million or the repeated £100 commitment twice.
- We don't treat dates, earlier political reference years or qualitative references to welfare policies as numerical claims. We used no chart-only numbers, macro forecasts or third-party restatements.

### Scottish Government primary issues

The Scottish Government attributes the figures to the UK Budget but doesn't separate the changes that newly announced decisions cause from the inherited funding path and inflation. It supplies no derivation, explicit comparison baseline or deflator year, so nobody can compare the five context rows directly with a cash-terms Barnett-consequentials table. The two component cash magnitudes agree with the printed total, and we recomputed none.

On its page the Scottish Government gives `2026-10-29T08:22:59Z` in JSON-LD `dateModified`, and 28 October 2026 15:45 in the visible publication time and `dc.date.modified`. Nobody provided an earlier local copy, and the metadata don't show that the numbers changed. We pin the sole fetched version in the manifest, record both timestamps there and invent no second version.

## Verification

- On 4 November, the contract checker reported 19 rows, 0 problems, and when we re-ran `stage.py` it reproduced both files byte for byte.
- On 3 November, the contract checker reported 19 rows, 0 problems, and when we re-ran `stage.py` it reproduced `manifest.jsonl` and `claims_staged.jsonl.gz` byte for byte (COUNTS.json pins the gzip's sha256). We only relabelled fields, so we repeated no spot check, and the lanes' checks below stand.
- Welsh rows, 29 October: the lane selected ten rows with `random.Random(2302026).sample(range(14), 10)`
and checked them against the saved, hash-verified HTML, reselecting the table
row/column or paragraph. We give one-based row numbers below. Every check
confirmed the number, sign/magnitude convention, unit and end-year period.

| Row | Reopened locator | Printed value | Normalized value and period |
|---:|---|---|---|
| 4 | Table 1 Resource, 2028-29 | 146 | GBP 146,000,000; 2029 |
| 5 | Table 1 Capital, 2026-27 | -27 | GBP -27,000,000; 2027 |
| 6 | Table 1 Capital, 2027-28 | -19 | GBP -19,000,000; 2028 |
| 7 | Table 1 Capital, 2028-29 | 2 | GBP 2,000,000; 2029 |
| 8 | Table 1 Capital, 2029-30 | -18 | GBP -18,000,000; 2030 |
| 9 | Table 1 Total, 2026-27 | 172 | GBP 172,000,000; 2027 |
| 11 | Table 1 Total, 2028-29 | 148 | GBP 148,000,000; 2029 |
| 12 | Table 1 Total, 2029-30 | -18 | GBP -18,000,000; 2030 |
| 13 | First paragraph after table/rounding footnote, last sentence | 0.5% | 0.5 percent reduction; 2028 |
| 14 | Second paragraph after table, second sentence | almost 10% | Upper endpoint 10 percent reduction; 2030 |

The lane also read the headline and all remaining numeric cells directly
when transcribing, and every row's quote contains its raw value. Its scope
review found no assigned registry key. On 3 November we gave the Welsh
package rows the shared proposed key `ab2026__package_barnett_consequentials`
(scope above), which we registered in tranche 2, and the context rows no key.
- Scottish rows, 29 October, in `uk_fai_sfc`: we then had fewer than 10 rows in the family, so the lane checked all 5. It shuffled them reproducibly (`random.Random(20261029)`) and checked rows **3, 2, 1, 4, 5** in that order (now rows 17, 16, 15, 18, 19 of this family, one-based). It re-opened the saved primary at every locator and checked its hash against each row's publication hash.

| Row | Primary locator | Verbatim figure | Checked normalization | Sign and period |
| ---: | --- | --- | --- | --- |
| 3 | Paragraph 2, sentence 1; HTML 348 | £550 million | 550,000,000 `gbp` | Positive magnitude of reduction; FY2027-28, period 2028 |
| 2 | Paragraph 2, sentence 1; HTML 348 | 1.3% | 1.3 `percent` | Positive magnitude of reduction; FY2027-28, period 2028 |
| 1 | Opening paragraph; HTML 347 | £650 million | 650,000,000 `gbp` | Positive magnitude of reduction; FY2027-28, period 2028 |
| 4 | Paragraph 2, sentence 2; HTML 348 | 1.5% | 1.5 `percent` | Positive magnitude of reduction; FY2027-28, period 2028 |
| 5 | Paragraph 2, sentence 2; HTML 348 | £100 million | 100,000,000 `gbp` | Positive magnitude of reduction; FY2027-28, period 2028 |
