# Welsh Government — Autumn Budget 2026

Source `welsh_government`; 14 rows from one primary. No AB2025
`uk_devolved_govts` directory exists in this checkout. Conventions follow the
AB2025 `uk_fai_sfc` block-grant rows (`source_model: arithmetic`, proposal
`block_grant_effect`, components in `conditions.component`).

## Access and primary

The [written statement](https://www.gov.wales/written-statement-welsh-government-response-uk-autumn-budget-2026)
was first published and last updated on 28 October 2026. It was fetched fresh
with `curl -sSL` and the exact requested User-Agent:

```text
Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15
```

HTTP 200; response Date 2026-10-29T15:22:18Z. Unaltered HTML is saved at
`.ab2026-primaries/uk_devolved_govts/welsh-response.html`; response headers
are alongside it. BeautifulSoup read the page's paragraphs and actual HTML
table cells, not chart geometry. `shasum -a 256` gives:

```text
87490552c36d8ffd5787db18127704e467d93599e5708627adb6da7dcfe17c7c
```

The fetched primary is 26,908 bytes. No local copy was provided, no fallback
was used, and there is no earlier assigned version against which to establish
a change. No requested Welsh page was blocked or unreached.

## Coverage and attribution

All 14 rows cite that primary:

| Position | Rows | Coverage |
|---|---:|---|
| Paragraph before Table 1 | 1 | Printed £448m cumulative funding headline |
| Table 1, Resource row | 3 | 199 / 165 / 146 (£m); 2029-30 is N/A |
| Table 1, Capital row | 4 | -27 / -19 / 2 / -18 (£m) |
| Table 1, Total row | 4 | 172 / 146 / 148 / -18 (£m) |
| Paragraphs after Table 1 | 2 | 0.5% resource and almost 10% capital real-terms reductions |

By `measure_key`: **null 14**. Twelve rows have the proposed package below;
the two real-terms settlement-level projections have no proposed measure key.
By metric: `proposed_metric: block_grant_effect` 14. By unit: `gbp` 12,
`percent` 2. By attribution: `own` 14; benchmark `different_model` 14.

These are the Welsh Government's own published settlement accounting and
real-terms comparisons. The statement does not credit another producer for
these calculations, so no HM Treasury attribution is inferred. They are
prospective funding changes rather than administrative outturns or counts.
The source does not name a formal model; `arithmetic` describes the
settlement accounting, consistent with the earlier devolved harvest.

## Scope and proposals

`ab2026__package_welsh_settlement_changes` (12 rows) is the producer's
reported change in the Welsh settlement following this Budget, over
2026-27 to 2029-30, split into Resource, Capital and Total. Producer wording:
“Changes to the Welsh Government Settlement”; the paragraph expressly
excludes employer pension contribution savings. **Table 6.1 line numbers
are not enumerated by the primary and cannot be established from it.** The
scope may contain the consequences of spending announcements beyond a
simple sum of Table 6.1 lines. No line set is invented. In particular these
rows are not attached to `ab2026__package_total_spending_policy_decisions`.
The proposed key preserves that unresolved mapping for registry review.

`block_grant_effect` is the existing AB2025 metric proposal, reused for
funding changes in GBP and for the percentage change in the real value of
the settlement. The two latter rows describe the full settlement relative
to a comparator the page does not expressly date. They are context, not
isolated effects of additional Budget funding; `measure_key` and
`reform_hint` are null and no package proposal is attached to them.

No unit or baseline proposals. `baseline_policy: null` follows the source's
current settlement comparison; it does not introduce an indexed or other
counterfactual. The two real-terms context rows explicitly say that the
price year and comparator year are unspecified.

## Numeric and period conventions

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

## Not staged

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

## Verification and report

`stage.py` embeds all row data and metadata and writes the sorted-key UTF-8
JSONL in a gzip with `mtime=0` and `filename=""`. Re-running it reproduces
the claims file; sha256:

```text
66c65dadbe415cb73dc23226a93d83f570cdecc09defe5b3f15993e0141f96fe
```

Contract command (with uv cache/environment directed into the ignored
primary folder and Python bytecode disabled):

```text
PYTHONPATH=. uv run -q python pipeline/ab2026_harvest_contract.py sources/harvest-uk-ab2026-2026-10-29/uk_devolved_govts
sources/harvest-uk-ab2026-2026-10-29/uk_devolved_govts: 14 rows, 0 problems
```

Ten rows selected with `random.Random(2302026).sample(range(14), 10)`
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

Nothing in this primary is internally contradictory: the four printed
Total cells add to the printed £448m headline. The page warns about rounding.
Resource 2029-30 being N/A while Capital and Total are numeric is preserved,
not interpreted as zero. No effort was made to repair or fill the primary.
