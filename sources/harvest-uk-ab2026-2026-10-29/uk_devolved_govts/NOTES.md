# uk_devolved_govts — devolved governments, Autumn Budget 2026

**Working files.** `stage.py`, which writes `manifest.jsonl` and `claims_staged.jsonl.gz`, lives on branch `uk/ab2026-harvest-staging` at `harvest-staging/ab2026/lanes/thinktanks-b/uk_devolved_govts/stage.py`; this branch carries only NOTES.md, `manifest.jsonl` and `claims_staged.jsonl.gz`. The lane's local primaries folder (`.ab2026-primaries/`) was never committed: the repository carries no primary bytes, so fetch each primary from its `manifest.jsonl` URL and check its sha256.

**19 rows from two primaries.** Rows 0–13 (0-based) are the Welsh Government's (source `welsh_government`); rows 14–18 are the Scottish Government's (source `scottish_government`). The Scottish rows were staged in `uk_fai_sfc` on 29 October. On 3 November the thinktanks-b review's finding 7 moved them here, so that both devolved governments sit in one family; `uk_fai_sfc` is left with no rows and is not carried (see the harvest README). Conventions follow the AB2025 `uk_fai_sfc` block-grant rows (`source_model: arithmetic`).

## Changes on 3 November 2026 (thinktanks-b review)

- **Finding 2:** the Welsh Table 1 Resource and Capital cells (rows 1–7) carry `conditions.row_type: "measure_component"` with their `component`; the four Total cells and the £448m headline (rows 0 and 8–11) carry `row_type: "total"` and no `component`. An ingest can no longer add parts to their total.
- **Finding 3:** the Welsh package key names its scope, not the nation: `ab2026__package_barnett_consequentials`, shared with HM Treasury's figures for the same scope in `uk_hmt_redbook`. Nation is `conditions.geography`.
- **Finding 4:** the seven real-terms settlement rows (Welsh rows 12–13, Scottish rows 14–18) use `proposed_metric: devolved_funding_real_terms_change`. AB2025's `block_grant_effect` means a policy's effect on the grant, positive for an increase; these rows are a year-on-year real-terms change in the whole settlement, positive for a reduction.
- **Finding 7:** the Scottish Government's rows moved here (above). Both slugs are now in the harvest README's slug table.
- **`component` on context rows:** the seven real-terms rows named their budget (Resource, Capital and so on) in `component`, which rule 9 reserves for parts of a measure. They now use `budget`, by the reasoning of the review's finding 6.
- **Attribution (coordinator check under finding 3):** the Welsh rows stay `own`. The page cites no source, and the coordinator's settled calls do not change this; HM Treasury's own consequentials are staged as HM Treasury's in `uk_hmt_redbook`.

No primary was re-opened on 3 November: the session's network policy refused gov.wales and gov.scot. Every change relabels fields; no printed value changed.

## Coverage

| Primary | Position | Rows | Coverage |
|---|---|---:|---|
| Welsh written statement | Paragraph before Table 1 | 1 | £448m cumulative headline (`total`) |
| | Table 1, Resource row | 3 | 199 / 165 / 146 (£m); 2029-30 is N/A (components) |
| | Table 1, Capital row | 4 | -27 / -19 / 2 / -18 (£m) (components) |
| | Table 1, Total row | 4 | 172 / 146 / 148 / -18 (£m) (`total`) |
| | Paragraphs after Table 1 | 2 | 0.5% resource and almost 10% capital real-terms reductions (context) |
| Scottish Government news release | Opening paragraph and paragraph 2 | 5 | £650 million; 1.3% and £550 million (resource); 1.5% and £100 million (capital), all 2027-28 real-terms reductions (context) |

By `measure_key`: **null 19**. Twelve rows carry the proposed key `ab2026__package_barnett_consequentials` (5 `total`, 7 `measure_component`); the seven real-terms rows are context with no proposed key. By metric: `block_grant_effect` 12, `devolved_funding_real_terms_change` 7. By unit: `gbp` 15, `percent` 4. Attribution: `own` 19; benchmark `different_model` 19.

## Proposed measure key

`ab2026__package_barnett_consequentials` (12 rows): the change in a devolved government's block grant from UK Government decisions at AB2026, by resource and capital, as the producer prints it; nation in `conditions.geography`. The Welsh rows exclude employer-pension-contribution savings ("Changes to the Welsh Government Settlement"; "an additional £448m of funding over the current spending review period", 2026-27 to 2029-30), as HM Treasury's do. No Table 6.1 line covers it: the consequentials follow from England's spending lines.

## Welsh Government

### Access

The [written statement](https://www.gov.wales/written-statement-welsh-government-response-uk-autumn-budget-2026)
was first published and last updated on 28 October 2026. It was fetched fresh
with `curl -sSL` and the exact requested User-Agent:

```text
Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15
```

HTTP 200; response Date 2026-10-29T15:22:18Z. The lane saved the unaltered
HTML and response headers in its local primaries folder. BeautifulSoup read the page's paragraphs and actual HTML
table cells, not chart geometry. `shasum -a 256` gives:

```text
87490552c36d8ffd5787db18127704e467d93599e5708627adb6da7dcfe17c7c
```

The fetched primary is 26,908 bytes. No local copy was provided, no fallback
was used, and there is no earlier assigned version against which to establish
a change. No requested Welsh page was blocked or unreached.

### Attribution

These are the Welsh Government's own published settlement accounting and real-terms comparisons. The statement does not credit another producer for these calculations, so no HM Treasury attribution is inferred. They are prospective funding changes rather than administrative outturns or counts. The source does not name a formal model; `arithmetic` describes the settlement accounting.

### Welsh numeric and period conventions

- GBP values are the printed £m cells or headline multiplied by one million.
  Signed table values are retained: positive means an increase in Welsh
  funding. No totals or differences are derived.
- Table columns are fiscal years; `period` is the end year and `fy` retains
  the printed year. The £448m headline is cumulative over the four displayed
  years, `period: 2030`, with that horizon stated explicitly; it is not an
  annual 2029-30 amount.
- Resource real-terms reduction “next financial year” is 2027-28 given the
  publication date. Capital reduction is explicitly by 2029-30. Percentage
  values retain the printed magnitude; conditions say positive means a
  reduction. “Almost 10%” is preserved in `value_raw`, the upper endpoint
  10 is marked `range_high`, and the qualifier is retained.
- The monetary table has no real-terms basis stated; no deflation is
  applied. The percentage context rows retain real terms with no invented
  price year. All rows concern Wales.
- `value_kind: point` means a single published figure, not a separately
  identified central-model scenario. No row uses `central`.
- Every quote is an exact page fragment or table cell, contains `value_raw`
  and is fewer than 15 words. Tables are read by row and then column.

### Welsh rows not staged

- Resource 2029-30 is `N/A`, not a number and not zero.
- OBR GDP growth of 1.2% in 2026 and 1.0% in 2027 is restated macro context,
  outside this assignment's devolved-consequentials scope; no own Welsh
  estimate of a Budget measure is asserted.
- The £100 council-tax-band A-D payment is a Welsh implementation
  announcement and policy parameter, with no implementation date, reach,
  aggregate cost or estimated household gain printed. It is not attached
  to the England-only Treasury line 1 key and is not fabricated into an
  impact row.
- The £14 billion rail commitment and £302m already allocated over the
  spending review are existing commitments, not newly estimated effects of
  AB2026; the statement supplies no isolation of a Budget measure's effect.
- Dates, council tax band letters, and rounding caveats are not estimates.
  There are no charts needing bar readings. No inaccessible Welsh page or
  unavailable local copy is being used as evidence.

## Scottish Government

The [news release](https://www.gov.scot/news/uk-budget-delivers-real-cut-to-scotlands-funding/) ("UK Budget delivers real cut to Scotland's funding", 28 October 2026) was fetched fresh on 2026-10-29 with the same User-Agent; HTTP 200, 27,662 bytes, sha256 `f3d0183e470f711b6821e4956e108c5d17210a392e6a6e471eccf297c807a6ac`.

- **Sign:** the primary prints unsigned magnitudes and describes reductions. Values retain those positive magnitudes, with `conditions.sign_convention: "positive = magnitude of reduction in Scottish Government funding"`. No minus sign is invented. The three million-pound amounts are multiplied by 1e6; the percentages remain percentages.
- **Period:** all rows use fiscal-year end year `2028`, `time_basis: fiscal_year`, and `conditions.fy: "2027-28"`.
- **Prices and comparison:** all rows say real terms, with an unspecified price base year. The primary does not explicitly name its comparison baseline. `conditions.price_basis` and `comparison_basis` preserve those limits. No cash-basis conversion is made.
- **Point/central:** the page gives one reported estimate per figure, not a named central model scenario, so `value_kind: point`. The money amounts retain the producer's “around” qualifier in `conditions.precision`.
- **Attribution:** all 5 are Scottish Government `own` estimates because the article reports its funding assessment without naming a separate original source. `arithmetic` follows the AB2025 family's funding convention and does not assert access to an unpublished model. None is an administrative outturn or count.
- **Baselines:** `baseline_policy: null`; no proposed baseline. These are context funding projections, not a comparison of a reform against a specified alternative policy.
- **Keys:** **`measure_key: null` — 5 rows**. No registered key is used, and **no proposed measure key** is introduced. The article does not isolate a set of Table 6.1 decisions or establish that its year-on-year real-terms funding assessment matches a registered package. `reform_hint: null` records that it is context. None of the 98 Table 6.1 lines is asserted to be the exact scope of these figures.

### Scottish rows not staged

- Every FAI figure: the primary refused the required fresh fetch, and no local fallback was supplied. The family therefore has no read primary evidence for FAI's quantitative or qualitative claims.
- SFC: no qualifying publication dated 28–29 October was found. Its earlier forecasts and funding commentary are not recast as post-Budget figures.
- The Scottish Government's £100 household energy-support commitment: it is a payment-policy parameter, not a separate quantified aggregate or model estimate. The article does not specify Scottish eligibility, rollout timing or a fully defined Scottish implementation; the registered Table 6.1 line 1 describes England's council-tax rebate. No England measure key is attached to Scotland's unspecified implementation.
- The £300 energy-bill reduction refers to an earlier political promise, not an AB2026 estimate or a newly costed option.
- The repeated £650 million in the minister's quotation and repeated £100 commitment are not staged twice.
- Dates, earlier political reference years and qualitative references to welfare policies do not form numerical claims. No chart-only numbers, macro forecasts or third-party restatements were used.

### Scottish Government primary issues

The response labels the figures as a consequence of the UK Budget but does not distinguish changes caused by newly announced decisions from the inherited funding path and inflation. It supplies no derivation, explicit comparison baseline or deflator year. Consequently the five context rows cannot be compared directly with a cash-terms Barnett-consequentials table. The two component cash magnitudes are consistent with the printed total; none was recomputed.

The HTML's JSON-LD `dateModified` is `2026-10-29T08:22:59Z`, while the visible publication time and `dc.date.modified` show 28 October 2026 15:45. No earlier local copy was provided, and the metadata do not establish that the numerical content changed. The manifest pins the sole fetched version and records both timestamps; there is no invented second version.

## Verification

- **3 November:** the contract checker reports 19 rows, 0 problems; a re-run of `stage.py` reproduces `manifest.jsonl` and `claims_staged.jsonl.gz` byte for byte (COUNTS.json pins the gzip's sha256). The fixes relabel fields only, so no spot check was repeated; the lanes' checks below stand.
- **Welsh rows (29 October).** Ten rows selected with `random.Random(2302026).sample(range(14), 10)`
were checked against the saved, hash-verified HTML, reselecting the table
row/column or paragraph. Row numbers below are one-based. Every check
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

The headline and all remaining numeric cells were also read directly when
transcribing. Every row's quote contains its raw value. Scope review found
no assigned registry key: the proposed Welsh package mapping remains
explicitly unresolved, and the context rows carry no proposal.
- **Scottish rows (29 October, in `uk_fai_sfc`).** Because the family contains fewer than 10 rows, all 5 were checked. A reproducibly shuffled order (`random.Random(20261029)`) gave rows **3, 2, 1, 4, 5** (now rows 17, 16, 15, 18, 19 of this family, one-based). The saved primary was re-opened at every locator; its hash was also checked against each row's publication hash.

| Row | Primary locator | Verbatim figure | Checked normalization | Sign and period |
| ---: | --- | --- | --- | --- |
| 3 | Paragraph 2, sentence 1; HTML 348 | £550 million | 550,000,000 `gbp` | Positive magnitude of reduction; FY2027-28, period 2028 |
| 2 | Paragraph 2, sentence 1; HTML 348 | 1.3% | 1.3 `percent` | Positive magnitude of reduction; FY2027-28, period 2028 |
| 1 | Opening paragraph; HTML 347 | £650 million | 650,000,000 `gbp` | Positive magnitude of reduction; FY2027-28, period 2028 |
| 4 | Paragraph 2, sentence 2; HTML 348 | 1.5% | 1.5 `percent` | Positive magnitude of reduction; FY2027-28, period 2028 |
| 5 | Paragraph 2, sentence 2; HTML 348 | £100 million | 100,000,000 `gbp` | Positive magnitude of reduction; FY2027-28, period 2028 |
