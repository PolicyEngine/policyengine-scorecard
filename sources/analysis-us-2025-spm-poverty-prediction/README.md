# Our 2025 poverty prediction, graded: comparables backfill

First search: 2026-10-22, `backfill`. The registry publication date is 2026-09-29.
Owner: `max-ghenis`; scope: federal. This record follows `docs/COMPARABLES.md`.

The search covered all 14 required US producers in registry order. It found 33
Columbia CPSP monthly SPM nowcasts and no independent calendar-year 2025 SPM
forecast. The monthly figures sit beside the annual prediction for the same age
group with `concept_mismatch`; no gap ratio is computed between monthly and annual
resource measures. Census published rates are logged under `open_search` as survey
outturns and are not staged as external model estimates.

## Published PolicyEngine figures

All 89 independently estimated fixed outputs in the post are pinned in
`analysis.json`, including its diagnostics. The live post embeds static markdown
rather than fetching a JSON result at runtime; its footnotes link the result files
that supply those numbers.

The article bytes exactly match
`PolicyEngine/policyengine-app-v2@5351fc508e20dc57c50416a9b06eea8d1009fbce`,
`app/src/data/posts/articles/2025-spm-poverty-prediction.md` (SHA-256
`2c1dc3d19febfe19a188da3fc5d104629e49ddf1f5530129ee633f29c1e9c98a`).
The latest successful `Production – policyengine-website` GitHub deployment,
[7260745377](https://api.github.com/repos/PolicyEngine/policyengine-app-v2/deployments/7260745377/statuses),
identifies that commit. Direct Vercel deployment HTML requires authentication;
the deployment identity is supported by this status plus the exact live-source
markdown match, rather than a private-build HTML comparison.

The linked results repository is `PolicyEngine/spm-threshold-paper` at
`22d8b7a1b9f97d94f796042bc067813b649a2f20`. Every estimate names an exact file,
field, hash, model/data provenance and recorded timing limitation. Counts by file:

| Results file | Pinned figures |
|---|---:|
| `data/predictions/2025-spm-poverty-rates-2026-09-11.json` | 15 |
| `data/predictions/2025-spm-poverty-rates-2026-09-11.grade-2026-09-17.json` | 9 |
| `analysis/prediction-grade-2025/results/model_decomposition.json` | 12 |
| `analysis/prediction-grade-2025/results/near_line_growth.json` | 3 |
| `analysis/prediction-grade-2025/results/raw_aging.json` | 9 |
| `analysis/prediction-grade-2025/uprating/results/variant_comparison.json` | 25 |
| `analysis/prediction-grade-2025/uprating/results/variant_split.json` | 1 |
| `analysis/prediction-grade-2025/results/senior_deduction.json` | 4 |
| `analysis/prediction-grade-2025/uprating/results/near_line_sources-baseline.json` | 4 |
| `analysis/prediction-grade-2025/uprating/results/survey_growth.json` | 6 |
| `analysis/prediction-grade-2025/uprating/results/wage_deciles.json` | 1 |

Poverty levels are normalized to shares, poverty-rate changes to percentage
points, and nominal income/resource growth diagnostics to percent. The senior
counterfactual scores removal of the deduction relative to current law, matching
the post: the stored negative contribution of adding the deduction is reversed
with `sign: -1`, while the stored count lifted by adding it is the positive count
pushed into poverty by removal.

Census/BLS/SSA observations, statutory parameter amounts, sample/calibration
counts, group boundaries and unpublished base-100 input indices are not
PolicyEngine estimated outputs. Rounded repetitions and the prose error-reduction
calculation are represented by their pinned source figures rather than invented
result fields.

## External evidence

- CPSP: all available 2025 months for all people, children under 18 and people 65+.
  The [versioned CSV](https://datawrapper.dwcdn.net/55gWy/15/dataset.csv) matches
  the producer-linked spreadsheet and age-chart dataset byte for byte. Its
  current version was published on 2026-04-20, verified by the chart HTML's
  `publishedAt`; this is not a claim about the original monthly release dates.
  October is absent because the producer says the CPS was not collected.
- The [monthly-method technical note](https://povertycenter.columbia.edu/sites/povertycenter.columbia.edu/files/content/Data/Monthly%20SPM%20Technical%20Note%20for%202024_updated%2010%2013%2025.pdf)
  explains monthly resources and tax/transfer timing, in contrast to the annual
  resources in the PolicyEngine prediction. `annotations.json` cites both methods.
- CPSP's annual historical databook explicitly uses Census data for the historical
  SPM from 2009 onward. Its 2025 endpoint is not an independent annual forecast.
- Census P60-290 and Table 5 were read and hashed. Table 5 prints 2025 rates of
  13.11%, 13.40% and 15.37% for the three groups. These are calibration material.
- Yale's tariff-poverty paper is dated September 2025 but explicitly models 2026.
  Urban's nearby projections and policy simulations target other years.
- CBPP's 2025 pre-release outlook is qualitative; its subsequent review and ITEP's
  poverty articles restate Census. No other producer's annual 2025 SPM forecast
  was located. `search_log.json` records the queries, pages and access limits.

## Review and limits

All 33 manifest hashes were recomputed with `shasum -a 256`, and byte counts
checked. Every one of the 89 PE result fields resolves to its recorded
`value_raw` in the hashed file. The 33 monthly cells and their publication dates
received an independent review, as did the post's output coverage.

The required source validator prints `ok`; the report lists 33 new claims and
`over_threshold: []`. There are no compared external claims, pending gaps or
tracking issues. There is one concept-mismatch annotation covering all monthly
claims. No issue was opened.

The diagnostic results record no calculation timestamps. Their `computed_at`
values explicitly identify the real publication commit time as an upper bound;
registered and grade files use their recorded written/graded dates. Actual run
times are unrecorded. Survey-derived outputs also omit input-file hashes and
runtime package versions. The pinned decomposition code references
`analysis/asec-2026-anchored-thresholds`, which is absent from that repository tree,
so the underlying anchored-survey recomputation could not be checked or rerun.

JCT's publications catalog and TPC's TaxVox catalog blocked direct reads. NBER
33656/34759 and SSRN 5531697 full texts also blocked reads; their indexed abstracts
were inspected. PWBM's old `/issues` URL returned 404; its current homepage and
baseline outlook were checked. No claim is inferred from an unread primary.

Downloaded primaries are outside the repository, under
`/private/tmp/claude-501/comparables-primaries/analysis-us-2025-spm-poverty-prediction/`.
Only this source directory is committed. The batch dispatcher will add the pushed
branch to [the existing backfill PR](https://github.com/PolicyEngine/policyengine-scorecard/pull/222).
The comparables index, database and exported feeds were not regenerated.
