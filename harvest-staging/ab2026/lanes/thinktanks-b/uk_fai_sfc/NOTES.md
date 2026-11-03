# uk_fai_sfc — Autumn Budget 2026

Staged 29 October 2026. This family covers the assigned Fraser of Allander Institute (FAI) reaction and a Scottish Government response about Scotland's funding. The Scottish Government publication was found while checking for Scottish Fiscal Commission (SFC) or Scottish Government consequences published on 28–29 October, as requested. FAI was blocked; no qualifying SFC publication was found.

The family contains **5 rows from 1 primary**, all from the Scottish Government, source `scottish_government`, source_model `arithmetic`. They are the producer's reported funding projections and are marked `own` / `different_model`. The article names no other original estimator. The assigned `fraser_of_allander` and `scottish_fiscal_commission` sources contribute zero rows.

## Access recipe and primary

The fresh requests used the prescribed command:

```sh
curl -sSL -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15" URL
```

The responses and headers were saved below `.ab2026-primaries/uk_fai_sfc/`; the HTML bytes were hashed with `shasum -a 256`. No primary is vendored in the family directory and no fallback copy was used.

| Primary | Published | Retrieved | Bytes | Rows | SHA256 |
| --- | --- | --- | ---: | ---: | --- |
| [UK Budget delivers real cut to Scotland’s funding](https://www.gov.scot/news/uk-budget-delivers-real-cut-to-scotlands-funding/) — Scottish Government | 2026-10-28 15:45 | 2026-10-29T15:22:47Z | 27,662 | 5 | `f3d0183e470f711b6821e4956e108c5d17210a392e6a6e471eccf297c807a6ac` |

The Scottish Government page returned HTTP 200. The file is `.ab2026-primaries/uk_fai_sfc/scottish_government_budget_response.html`; a plain-text extract in the same directory was made using Python's HTMLParser. Figures were read in the first two body paragraphs, HTML lines 347–348. Locators identify paragraph, sentence and figure; no chart was read. The page footer licenses its text under OGL v3.0; quotes nevertheless remain fewer than 15 words, as this harvest requires for every producer except HMT and OBR.

### Access failure and discovery coverage

- [FAI UK Budget reaction](https://fraserofallander.org/uk-budget-reaction/): fresh prescribed-UA curl returned **HTTP 403** at 2026-10-29T15:22:23Z. The response body is a 103-byte error page, saved as `fai_uk_budget_reaction.html`, sha256 `f261423d1da97890ff6bfccd31ff4ee0b74f69351cf75095fbe791cb16cbf5bd`. This is failed-fetch evidence, **not a publication primary**, and is excluded from the manifest. No local copy was listed in the assignment. No alternate endpoint, cache or API was used after the refusal. The coordinator also opened the page in the Claude desktop app's built-in browser at 2026-10-29T17:00Z, and it returned the same 403 page. The AB2025 family's WordPress API fallback is superseded by this assignment's blocked-fetch rule. Search-result text was used for discovery only and supplied no staged numbers.
- SFC [Insights](https://fiscalcommission.scot/insights/) and [Analytical publications](https://fiscalcommission.scot/publication-categories/analytical/) returned HTTP 200 to fresh prescribed-UA curl. Their HTML is retained as discovery evidence (`sfc_insights_discovery.html`, `sfc_analytical_discovery.html`). The latest listed Insight was 30 September 2026; the newest analytical publications were August 2026. The [Correspondence 2026](https://fiscalcommission.scot/publications/correspondence-2026/) listing was also inspected and contained no 28–29 October Budget response. Targeted searches for SFC Budget publications on both dates found none. These navigation indexes do not enter the primary-document manifest.
- Scottish Government news searches for 28 and 29 October found the response above. Pre-Budget commentary on 25 October and the September fiscal-framework outturn report fall outside the requested publication window and were not staged.

## Coverage and conventions

Reading order follows the opening paragraph, then paragraph 2 from left to right. No number is derived by summing or dividing other figures.

| Printed figure | Component | Unit | FY | Rows |
| --- | --- | --- | --- | ---: |
| £650 million | Resource and capital budgets | `gbp` | 2027-28 | 1 |
| 1.3% | Resource Block Grant | `percent` | 2027-28 | 1 |
| £550 million | Resource Block Grant, cash equivalent of real-terms reduction | `gbp` | 2027-28 | 1 |
| 1.5% | Capital budget | `percent` | 2027-28 | 1 |
| £100 million | Capital budget, cash equivalent of real-terms reduction | `gbp` | 2027-28 | 1 |

- **Metric:** all 5 reuse the AB2025 proposal `block_grant_effect`, here with `gbp` (3 rows) or `percent` (2). Its scope is the producer's projected real-terms reduction in Scotland's total, resource or capital funding. These are not cash-terms Barnett consequentials from new spending decisions.
- **Sign:** the primary prints unsigned magnitudes and describes reductions. Values retain those positive magnitudes, with `conditions.sign_convention: "positive = magnitude of reduction in Scottish Government funding"`. No minus sign is invented. The three million-pound amounts are multiplied by 1e6; the percentages remain percentages.
- **Period:** all rows use fiscal-year end year `2028`, `time_basis: fiscal_year`, and `conditions.fy: "2027-28"`.
- **Prices and comparison:** all rows say real terms, with an unspecified price base year. The primary does not explicitly name its comparison baseline. `conditions.price_basis` and `comparison_basis` preserve those limits. No cash-basis conversion is made.
- **Point/central:** the page gives one reported estimate per figure, not a named central model scenario, so `value_kind: point`. The money amounts retain the producer's “around” qualifier in `conditions.precision`.
- **Attribution:** all 5 are Scottish Government `own` estimates because the article reports its funding assessment without naming a separate original source. `arithmetic` follows the AB2025 family's funding convention and does not assert access to an unpublished model. None is an administrative outturn or count.
- **Baselines:** `baseline_policy: null`; no proposed baseline. These are context funding projections, not a comparison of a reform against a specified alternative policy.
- **Keys:** **`measure_key: null` — 5 rows**. No registered key is used, and **no proposed measure key** is introduced. The article does not isolate a set of Table 6.1 decisions or establish that its year-on-year real-terms funding assessment matches a registered package. `reform_hint: null` records that it is context. None of the 98 Table 6.1 lines is asserted to be the exact scope of these figures.

## Not staged

- Every FAI figure: the primary refused the required fresh fetch, and no local fallback was supplied. The family therefore has no read primary evidence for FAI's quantitative or qualitative claims.
- SFC: no qualifying publication dated 28–29 October was found. Its earlier forecasts and funding commentary are not recast as post-Budget figures.
- The Scottish Government's £100 household energy-support commitment: it is a payment-policy parameter, not a separate quantified aggregate or model estimate. The article does not specify Scottish eligibility, rollout timing or a fully defined Scottish implementation; the registered Table 6.1 line 1 describes England's council-tax rebate. No England measure key is attached to Scotland's unspecified implementation.
- The £300 energy-bill reduction refers to an earlier political promise, not an AB2026 estimate or a newly costed option.
- The repeated £650 million in the minister's quotation and repeated £100 commitment are not staged twice.
- Dates, earlier political reference years and qualitative references to welfare policies do not form numerical claims. No chart-only numbers, macro forecasts or third-party restatements were used.

## Primary issues

The response labels the figures as a consequence of the UK Budget but does not distinguish changes caused by newly announced decisions from the inherited funding path and inflation. It supplies no derivation, explicit comparison baseline or deflator year. Consequently the five context rows cannot be compared directly with a cash-terms Barnett-consequentials table. The two component cash magnitudes are consistent with the printed total; none was recomputed.

The HTML's JSON-LD `dateModified` is `2026-10-29T08:22:59Z`, while the visible publication time and `dc.date.modified` show 28 October 2026 15:45. No earlier local copy was provided, and the metadata do not establish that the numerical content changed. The manifest pins the sole fetched version and records both timestamps; there is no invented second version.

## Verification

The required contract checker passed:

```text
sources/harvest-uk-ab2026-2026-10-29/uk_fai_sfc: 5 rows, 0 problems
```

Command: `PYTHONPATH=. uv run -q python pipeline/ab2026_harvest_contract.py sources/harvest-uk-ab2026-2026-10-29/uk_fai_sfc`, with `UV_PROJECT_ENVIRONMENT` and `UV_CACHE_DIR` directed into the ignored `.ab2026-primaries/uk_fai_sfc/` subtree.

Re-running `stage.py` produced identical gzip bytes. SHA256 before and after: `518d16f57bc2f2210ce09e1f48cc772560c2f76a7468e2631eb4b3eb2d35bb89`. Each JSON line uses `sort_keys=True, ensure_ascii=False`, and gzip uses `mtime=0, filename=""`.

Because the family contains fewer than 10 rows, all 5 were checked. A reproducibly shuffled order (`random.Random(20261029)`) gave rows **3, 2, 1, 4, 5**. The saved primary was re-opened at every locator; its hash was also checked against each row's publication hash.

| Row | Primary locator | Verbatim figure | Checked normalization | Sign and period |
| ---: | --- | --- | --- | --- |
| 3 | Paragraph 2, sentence 1; HTML 348 | £550 million | 550,000,000 `gbp` | Positive magnitude of reduction; FY2027-28, period 2028 |
| 2 | Paragraph 2, sentence 1; HTML 348 | 1.3% | 1.3 `percent` | Positive magnitude of reduction; FY2027-28, period 2028 |
| 1 | Opening paragraph; HTML 347 | £650 million | 650,000,000 `gbp` | Positive magnitude of reduction; FY2027-28, period 2028 |
| 4 | Paragraph 2, sentence 2; HTML 348 | 1.5% | 1.5 `percent` | Positive magnitude of reduction; FY2027-28, period 2028 |
| 5 | Paragraph 2, sentence 2; HTML 348 | £100 million | 100,000,000 `gbp` | Positive magnitude of reduction; FY2027-28, period 2028 |

All five figures, quotes, units and periods match the primary. All five have null measure keys and no proposed key; none claims an exact Table 6.1 scope. No git state was changed and nothing was committed or pushed.
