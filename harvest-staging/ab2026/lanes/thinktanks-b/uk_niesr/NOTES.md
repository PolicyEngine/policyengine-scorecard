# NIESR — Autumn Budget 2026

Source slug `niesr`. **0 rows; 1 primary.** The Budget-day reaction contains
macro/fiscal-stance commentary and no household/static estimates. The AB2025
NIESR precedent and README rule 10 reserve the former for the #55 lane.
`stage.py` embeds the empty row list and the manifest, and reproduces both
output files. The empty claims file is intentional.

## Access recipe and primary

[Breathing Space, Not a Strategy](https://niesr.ac.uk/blog/breathing-space-not-strategy),
Professor Stephen Millard, NIESR, 28 October 2026:

- Fresh direct fetch, HTTP 200, 142,303 HTML bytes. The response Date is
  **2026-10-29T15:22:11Z**. The visible date agrees with the page's
  `article:published_time`, `2026-10-28T15:59:11+00:00`.
- Saved at `.ab2026-primaries/uk_niesr/breathing-space-not-strategy.html`.
  SHA256: `0108b60ad2a85e65a717c03a68060ad9c45fdcbe09cb5a24eca374a618436ccb`.
  Hash checked with `shasum -a 256`.
- Fetch command: `curl -sSL -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15" -D .ab2026-primaries/uk_niesr/breathing-space-not-strategy.headers -o .ab2026-primaries/uk_niesr/breathing-space-not-strategy.html https://niesr.ac.uk/blog/breathing-space-not-strategy`.
- Read the fetched HTML's own body text using BeautifulSoup. Figure 1 is an
  embedded image; no values were read off its plotted line.
- No local fallback or assignment copy was supplied. No block, login wall,
  changed-version comparison or second primary was encountered.

## Follow-up discovery

On 29 October, searched the NIESR domain for the exact reaction title and
combinations of Budget, living standards, household, fiscal, 28 October,
29 October and 2026. Also fetched and read the current first pages of these
public indexes directly with the same curl User-Agent (all HTTP 200):

| Index | Latest visible item | Saved discovery bytes, SHA256 |
|---|---|---|
| <https://niesr.ac.uk/blog> | Budget reaction, 28 October; next item 23 October | `blog-index.html`, `ccc21f8eea432ac06a209c4a0fea0fb11c77654c167ff00d943e5298ba55b6f9` |
| <https://niesr.ac.uk/publications/> | Publication 21 October; report 13 October | `publications-index.html`, `c0a5a3f8a67e06c0d8b15c364b07ed3eca10c47fc939b6364db605b03c089a6f` |
| <https://niesr.ac.uk/news> | News item 28 September | `news-index.html`, `493f6ec19fabd5d212917fef3a62d9f07ea534995a1b5b5bf9007e6385758b81` |

Discovery files and response headers are under `.ab2026-primaries/uk_niesr/`.
Indexes are discovery evidence, not claim-bearing Budget primaries, and are
not counted in the manifest. No additional NIESR post-Budget analysis dated
28–29 October was found. Search results identified a webinar,
[Beyond the Headlines: What Budget 2026 Means for the UK Economy](https://niesr.ac.uk/event/beyond-headlines-what-budget-2026-means-uk-economy),
scheduled for 30 October. Its announcement contains no analysis results and
the event is beyond this harvest's date. The 16 October devolved-government
preview and earlier Budget preparation articles are outside this assignment's
post-Budget window.

## Coverage and conventions

| Primary | Rows |
|---|---:|
| Breathing Space, Not a Strategy | 0 |
| **Total** | **0** |

Rows by measure key: **null 0; registered keys 0**. No proposed measure key,
metric, unit or baseline is used. No source model is asserted for an absent
row. In an eligible household/static estimate we would follow AB2025's
`income_group: decile_N`, producer-specific income concepts and source models;
there are none to apply here. Signs, units, periods, baselines and the meaning
of central are consequently not transformed or imputed.

The general rule to stage restated numbers was applied while screening the
primary. No restated household/static estimate is printed. The official
figures below are all fiscal forecasts or market/macro context, so the
specific #55 exclusion governs them just as in AB2025's NIESR family.

## Not staged, with primary locators

All numbers below are printed in the fetched primary, but belong to the
macro/fiscal-stance lane. This inventory records their exclusion, not claims:

| Locator | Printed figures | Reason |
|---|---|---|
| Opening paragraph, buffer sentence | £23.6 billion in March; £14.5 billion now | Restated official fiscal headroom forecast; #55 |
| Higher borrowing costs are here to stay, paragraph 1 | around 100 basis points; around 5.3 per cent | Gilt market context; #55 |
| Same section, paragraph 2 | £7.4 billion; £250.6 billion; 2026-27 | DMO financing-remit revision and gilt issuance; #55 |
| The debt rachet and path credibility, final paragraph | £12.4 billion over the next three years; £7 billion on average afterwards | Restated OBR estimate of the policy package's borrowing effect; AB2025 NIESR precedent stages no restated OBR/HMT figures (the OBR's own figure belongs to `uk_obr_tables`). Reason corrected on 3 November (thinktanks-b review finding 8). |
| Same paragraph, debt forecast sentence | around 97 per cent in 2028-29; 96 per cent in 2031-32; 94 per cent in August | Restated OBR debt forecasts and debt-ratio context; #55 |
| Global markets are fragile, paragraph 2 | £9 billion | Rounded fiscal-headroom reduction; #55 |
| Same section, paragraph 3 | around £150 billion annually by end of decade | Debt-interest forecast; #55 |
| Same section, paragraph 4 | 10-20 basis points; around £1-2 billion a year by end of parliament | NIESR judgement of a hypothetical credibility dividend; macro scenario, #55 |
| Figure 1, Public Sector Net Debt to GDP ratio | Plotted paths | No chart values read; macro context also excluded |

There are no costings for individual Budget measures, household impacts,
worked examples, living-standards estimates or distributional data labels to
stage. No page identified for this assignment was unreached.

## Validation and primary audit

Required checker:

`PYTHONPATH=. uv run -q python pipeline/ab2026_harvest_contract.py sources/harvest-uk-ab2026-2026-10-29/uk_niesr`

Output: `sources/harvest-uk-ab2026-2026-10-29/uk_niesr: 0 rows, 0 problems`.
The command used `UV_PROJECT_ENVIRONMENT` and `UV_CACHE_DIR` inside
`.ab2026-primaries/uk_niesr/` to keep its environment/cache writes in the
assigned subtree.

Reran `stage.py` and checked the claims gzip SHA256 was unchanged:
`9ceffb7310338057cfe71a4ae1e2c98d2c485d81cdef906532a801f457a38d64`.
There are no rows from which to draw a random 10-row sample. Instead reopened
the fetched primary and checked ten excluded number groups at the locators
above: (1) March headroom, (2) current headroom, (3) gilt yield and rise,
(4) DMO remit change, (5) total issuance and FY, (6) borrowing increase and
later reduction, (7) debt ratios and their years, (8) rounded headroom change,
(9) debt-interest level and horizon, (10) credibility-dividend ranges and
horizon. They match the exclusion inventory. No measure key is attached to
any figure, so no package-scope join is implied.

## Ambiguities and apparent inconsistencies

The page describes the fall from £23.6 billion to £14.5 billion as £9 billion
later on; this appears to be rounding and is recorded as printed. Its
£12.4 billion borrowing sentence does not clearly say whether this is a
three-year total or an annual average, while the following £7 billion is
explicitly an average. The credibility dividend has only an end-of-parliament
horizon; no fiscal year is printed. No period, sum, sign or missing precision
has been inferred to repair these statements.
