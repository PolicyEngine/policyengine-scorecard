# UK fiscal-event replay: DWP, HMRC and HM Treasury vintage documents on GOV.UK and public archives

Scope: policyengine-scorecard issue #156, track 2. This file covers the 32 OBR-costed fiscal events from June 2010 to Autumn Budget 2025. For each event it records what HM Treasury, DWP and HMRC published at the time and whether it can be fetched today without getting past any access control.

- Researched on 2026-10-09 with User-Agent `policyengine-scorecard-research/1.0`, about one request per second (three to six seconds for the Wayback Machine).
- Sources used:
  - GOV.UK Content API (`https://www.gov.uk/api/content/<path>`)
  - GOV.UK Search API (`https://www.gov.uk/api/search.json`)
  - Wayback Machine CDX API (`https://web.archive.org/cdx/search/cdx`)
  - HEAD requests on `assets.publishing.service.gov.uk`
- Raw API responses are cached in `/tmp/uk-replay-scope/agents/work_archive/cache/`. The helper scripts are `fetch.py`, `listatt.py` and `wb.py` in the same directory.
- Sample files I downloaded are in `/tmp/uk-replay-scope/agents/archive_samples/` (see section 9).

## 0. Access findings (read first)

| Source | Status on 2026-10-09 | Evidence |
|---|---|---|
| GOV.UK Content API and Search API | Open. Returns JSON, including `details.attachments`, `change_history` and collection groups | e.g. `https://www.gov.uk/api/content/government/publications/budget-2013-documents` |
| `assets.publishing.service.gov.uk` (attachments) | Open. Current attachments return 200. **Attachments that were replaced or removed return HTTP 410 Gone** (see 4.2) | HEAD checks in section 9 |
| Wayback Machine CDX and `id_` captures | Open, but with intermittent HTTP 503/504 and connection refusals under light load. Requests needed about 3–6 s spacing and retries. | e.g. `https://web.archive.org/cdx/search/cdx?url=cdn.hm-treasury.gov.uk/&matchType=prefix&filter=original:.*[Cc]osting.*` |
| **UK Government Web Archive (UKGWA)** | **Blocked to programmatic access.** Both `https://webarchive.nationalarchives.gov.uk/ukgwa/timemap/link/http://cdn.hm-treasury.gov.uk/budget2012_policy_costings.pdf` and `https://webarchive.nationalarchives.gov.uk/ukgwa/cdx?url=...` returned **HTTP 405 with an AWS WAF "Human Verification" JavaScript challenge**. I did not try to get past it. | One request each, 2026-10-09 |

The UKGWA block matters most for two series. HMRC's ready-reckoner page and its tax-relief pages say that older editions are kept "in The National Archives". I could not confirm what the UKGWA holds, so anything that exists only there is marked **unknown (UKGWA-only, not verifiable here)**.

## 1. Events and verified dates

Dates come from the `first_published_at` field of the HM Treasury GOV.UK page unless noted otherwise.

| # | Event (PMD name) | Date | Date source |
|---|---|---|---|
| 1 | Budget 2010 #2 (June) | 22 Jun 2010 | `/government/publications/budget-june-2010` (first_published 2010-06-22) |
| 2 | Autumn 2010 | Spending Review 20 Oct 2010; OBR EFO and Chancellor's "autumn forecast statement" 29 Nov 2010 | SR docs page `hm-treasury.gov.uk/spend_sr2010_documents.htm` first captured in Wayback on 20101020; GOV.UK press release `/government/news/chancellors-autumn-forecast-statement` (2010-11-29) says the statement "responds to the OBR's EFO published at 1pm on 29 November 2010" |
| 3 | Budget 2011 | 23 Mar 2011 | `/government/publications/budget-2011` |
| 4 | Autumn Statement 2011 | 29 Nov 2011 | `/government/publications/autumn-statement-2011` |
| 5 | Budget 2012 | 21 Mar 2012 | `/government/publications/budget-2012` |
| 6 | Autumn Statement 2012 | 5 Dec 2012 | `/government/publications/autumn-statement-2012-documents` |
| 7 | Budget 2013 | 20 Mar 2013 | `/government/publications/budget-2013-documents` |
| 8 | Autumn Statement 2013 | 5 Dec 2013 | `/government/publications/autumn-statement-2013-documents` |
| 9 | Budget 2014 | 19 Mar 2014 | `/government/publications/budget-2014-documents` |
| 10 | Autumn Statement 2014 | 3 Dec 2014 | `/government/publications/autumn-statement-documents` |
| 11 | Budget 2015 (March) | 18 Mar 2015 | `/government/publications/budget-2015-documents` |
| 12 | Summer Budget 2015 ("Budget 2015 #2") | 8 Jul 2015 | `/government/publications/summer-budget-2015` |
| 13 | Spending Review and Autumn Statement 2015 | 25 Nov 2015 | `/government/publications/spending-review-and-autumn-statement-2015-documents` |
| 14 | Budget 2016 | 16 Mar 2016 | `/government/publications/budget-2016-documents` |
| 15 | Autumn Statement 2016 | 23 Nov 2016 | `/government/publications/autumn-statement-2016-documents` |
| 16 | Spring Budget 2017 | 8 Mar 2017 | `/government/publications/spring-budget-2017-documents` |
| 17 | Autumn Budget 2017 | 22 Nov 2017 | `/government/publications/autumn-budget-2017-documents` |
| 18 | Spring Statement 2018 | 13 Mar 2018 | `/government/topical-events/spring-statement-2018`; speech and news dated 2018-03-13 |
| 19 | Budget 2018 | 29 Oct 2018 | `/government/publications/budget-2018-documents` |
| 20 | Spring Statement 2019 | 13 Mar 2019 | `/government/publications/spring-statement-2019-written-ministerial-statement` |
| 21 | Budget 2020 | 11 Mar 2020 | `/government/publications/budget-2020-documents` |
| 22 | Spending Review 2020 | 25 Nov 2020 | `/government/publications/spending-review-2020-documents` |
| 23 | Budget 2021 | 3 Mar 2021 | `/government/publications/budget-2021-documents` |
| 24 | Autumn Budget and Spending Review 2021 | 27 Oct 2021 | `/government/publications/autumn-budget-and-spending-review-2021-documents` |
| 25 | Spring Statement 2022 | 23 Mar 2022 | `/government/publications/spring-statement-2022-documents` |
| 26 | Autumn Statement 2022 | 17 Nov 2022 | `/government/publications/autumn-statement-2022-documents` |
| 27 | Spring Budget 2023 | 15 Mar 2023 | `/government/publications/spring-budget-2023` |
| 28 | Autumn Statement 2023 | 22 Nov 2023 | `/government/publications/autumn-statement-2023` |
| 29 | Spring Budget 2024 | 6 Mar 2024 | `/government/publications/spring-budget-2024` |
| 30 | Autumn Budget 2024 | 30 Oct 2024 | `/government/publications/autumn-budget-2024` |
| 31 | Spring Statement 2025 | 26 Mar 2025 | `/government/publications/spring-statement-2025-document` |
| 32 | Autumn Budget 2025 | 26 Nov 2025 | `/government/publications/budget-2025-document` |

All paths in the table are relative to `https://www.gov.uk`.

Not in the 32, but relevant to the replay:

- The Growth Plan of 23 Sep 2022 had no OBR forecast. Its reversals are scored in Autumn Statement 2022 Table 5.2.
- The March Budget 2010 (pre-coalition) has a DWP vintage, `budget2010a.zip`, on the 2010 DWP page.

## 2. HM Treasury policy costings documents (measure-level methodology notes)

All URLs are live GOV.UK assets (HEAD 200 for those I sampled; see section 9) unless marked "Wayback".

| # | Event | Policy costings document |
|---|---|---|
| 1 | June 2010 | **Not on GOV.UK.** The GOV.UK page holds only the full-text Budget PDF. **Wayback:** `http://www.hm-treasury.gov.uk/d/junebudget_costings.pdf`, captured 20101118114518 (200, application/pdf) |
| 2 | Autumn 2010 (SR2010) | **Not on GOV.UK.** The SR2010 page holds the SR document, executive summary, statistical annex and distributional annex. **Wayback:** `http://cdn.hm-treasury.gov.uk:80/sr2010_policycostings.pdf` captured 20101214054251 (200), and `http://www.hm-treasury.gov.uk/d/sr2010_policycostings.pdf` captured 20121030154558 (200). There was no separate HMT costings note for the 29 Nov 2010 statement; none was found. |
| 3 | Budget 2011 | **Not on GOV.UK. Wayback:** `http://www.hm-treasury.gov.uk/d/2011budget_policycostings.pdf` captured 20110406084427 (200), and `http://cdn.hm-treasury.gov.uk:80/2011budget_policycostings.pdf` captured 20110409142925 (200) |
| 4 | AS 2011 | **Not on GOV.UK. Wayback:** `http://cdn.hm-treasury.gov.uk/as2011policy_costings.pdf` captured 20111201172936 (200) |
| 5 | Budget 2012 | **Not on GOV.UK. Wayback:** `http://cdn.hm-treasury.gov.uk/budget2012_policy_costings.pdf` captured 20120403141403 (200). The `www.hm-treasury.gov.uk` copy was already 410 by 20131202. |
| 6 | AS 2012 | https://assets.publishing.service.gov.uk/media/5a7c8414e5274a2674eab2f5/as2012_policy_costings.pdf |
| 7 | Budget 2013 | https://assets.publishing.service.gov.uk/media/5a7b9f3d40f0b62826a04c18/budget2013_policy_costings.pdf |
| 8 | AS 2013 | https://assets.publishing.service.gov.uk/media/5a7c4a44e5274a1b00422c3d/autumn_statement_2013_policy_costings.pdf |
| 9 | Budget 2014 | https://assets.publishing.service.gov.uk/media/5a7c7cb8e5274a559005a340/PU1638_policy_costings_bud_2014_with_correction_slip.pdf (includes a correction slip) |
| 10 | AS 2014 | https://assets.publishing.service.gov.uk/media/5a7d866ae5274a6b89a50953/AS2014_policy_costings_final.pdf |
| 11 | Budget 2015 | https://assets.publishing.service.gov.uk/media/5a7f5361ed915d74e33f5beb/Policy_Costings_18_00.pdf |
| 12 | Summer Budget 2015 | https://assets.publishing.service.gov.uk/media/5a81782de5274a2e8ab54294/Policy_costings_summer_budget_2015.pdf |
| 13 | SR&AS 2015 | https://assets.publishing.service.gov.uk/media/5a817507ed915d74e62325e4/SRAS2015_policy_costings_amended_page_25.pdf ("amended page 25") |
| 14 | Budget 2016 | https://assets.publishing.service.gov.uk/media/5a8169cae5274a2e8ab53dae/PU1912_Policy_Costings_FINAL3.pdf |
| 15 | AS 2016 | https://assets.publishing.service.gov.uk/media/5a80e284e5274a2e87dbc5d4/Policy_Costings_AS_2016_web_final.pdf |
| 16 | Spring Budget 2017 | https://assets.publishing.service.gov.uk/media/5a801f9ee5274a2e87db7fd5/PU2055_Spring_Budget_2017_web_2.pdf |
| 17 | Autumn Budget 2017 | https://assets.publishing.service.gov.uk/media/5a74d88ee5274a3cb2867a6c/Autumn_Budget_Policy_costings_document_web.pdf |
| 18 | Spring Statement 2018 | **None found.** The topical-event page `/government/topical-events/spring-statement-2018` features only news, the speech and a consultation. Guessed paths `/government/publications/spring-statement-2018(-documents)` return 404. |
| 19 | Budget 2018 | https://assets.publishing.service.gov.uk/media/5bd719a540f0b604c0d2353c/Budget_2018_policy_costings_PDF.pdf |
| 20 | Spring Statement 2019 | **None found.** Only the written ministerial statement exists: https://assets.publishing.service.gov.uk/media/5c88d8ce40f0b65164a64a7e/WMS_final_Commons.pdf |
| 21 | Budget 2020 | https://assets.publishing.service.gov.uk/media/5e68f679d3bf7f26918b77f8/Budget_2020_policy_costings.pdf |
| 22 | SR 2020 | https://assets.publishing.service.gov.uk/media/5fbd2087d3bf7f5735e29b41/Policy_costings_2020_final.pdf ("Policy costings: November 2020") |
| 23 | Budget 2021 | https://assets.publishing.service.gov.uk/media/603d2bef8fa8f577bcd9ded8/Budget_2021_policy_costings_.pdf |
| 24 | ABSR 2021 | https://assets.publishing.service.gov.uk/media/617c2631e90e07197f18fe04/Policy_Costings_Document_FINAL.pdf |
| 25 | SS 2022 | https://assets.publishing.service.gov.uk/media/623a2c7cd3bf7f6abf0c764b/Policy_Costings_Document_Spring_Statement_2022.pdf |
| 26 | AS 2022 | https://assets.publishing.service.gov.uk/media/6375caf8e90e072848403c47/Autumn_Statement_2022_Policy_Costings_.pdf |
| 27 | SB 2023 | https://assets.publishing.service.gov.uk/media/6411603be90e076ccf66d781/Costing_Document_-_Spring_Budget_2023.pdf |
| 28 | AS 2023 | https://assets.publishing.service.gov.uk/media/6560c3ef3d77410012420197/Autumn_Statement_2023_Policy_Costings_-_Final.pdf |
| 29 | SB 2024 | https://assets.publishing.service.gov.uk/media/65e7920c08eef600155a5617/Published_Costing_Document_Spring_Budget_2024_Final.pdf |
| 30 | AB 2024 | https://assets.publishing.service.gov.uk/media/6721d2c54da1c0d41942a8d2/Policy_Costing_Document_-_Autumn_Budget_2024.pdf |
| 31 | SS 2025 | PDF https://assets.publishing.service.gov.uk/media/67e562fc33afcd62e4ca4c9e/SS25_Published_Costing_Document.pdf; HTML version `/government/publications/supporting-documents-for-spring-statement-2025/spring-statement-2025-policy-costings` |
| 32 | AB 2025 | https://assets.publishing.service.gov.uk/media/692872fd2a37784b16ecf676/Budget_2025-Policy_Costings.pdf (on `/government/publications/supporting-documents-for-budget-2025`) |

Related HMT documents published alongside most events: "Data sources", "Impact on households: distributional analysis" and (from 2015) "Impact on equalities". Their URLs are on the same GOV.UK pages; a listing is cached via `listatt.py`.

## 3. HM Treasury scorecard (policy decisions table)

| # | Event | Scorecard location |
|---|---|---|
| 1 | June 2010 | Inside "Budget June 2010 – Full Text": https://assets.publishing.service.gov.uk/media/5a7b7f37ed915d1a79023a82/0061.pdf. Chapter 2 policy decisions table; table number not text-verified. |
| 2 | Autumn 2010 | Inside "Spending Review 2010": https://assets.publishing.service.gov.uk/media/5a7f0a11e5274a2e8ab49c3e/Spending_review_2010.pdf. Table number not text-verified. No separate HMT document for the 29 Nov 2010 statement. |
| 3 | Budget 2011 | Inside the full-text PDF: https://assets.publishing.service.gov.uk/media/5a7cb09ded915d6822361ef8/0836.pdf. Table number not text-verified (expected Table 2.1/2.2). |
| 4 | AS 2011 | Inside https://assets.publishing.service.gov.uk/media/5a7c0151e5274a7202e18f39/8231.pdf. Table number not text-verified. |
| 5 | Budget 2012 | Inside https://assets.publishing.service.gov.uk/media/5a7c923ced915d6969f45d0b/1853.pdf. Table number not text-verified. |
| 6 | AS 2012 | AS document https://assets.publishing.service.gov.uk/media/5a7c9a3b40f0b65b3de09f36/autumn_statement_2012_complete.pdf, plus an HTML statistics page `/government/statistics/autumn-statement-2012-policy-decisions-table` |
| 7 | Budget 2013 | Table 2.1 XLS https://assets.publishing.service.gov.uk/media/5a7cc68bed915d6822362798/budget2013_table2-1_policy_decisions.xls; Table 2.2 XLS https://assets.publishing.service.gov.uk/media/5a7c6caced915d696ccfcb01/budget2013_table2-2_previous_measures_with_effect_april2013.xls; HTML `/government/statistics/budget-2013-policy-decisions-table` |
| 8 | AS 2013 | "Policy decisions table" https://assets.publishing.service.gov.uk/media/5a756dbee5274a1baf95e801/Scorecard.xlsx |
| 9 | Budget 2014 | Inside https://assets.publishing.service.gov.uk/media/5a7c939ced915d12ab4bbb37/37630_Budget_2014_Web_Accessible.pdf. No separate XLS attached. |
| 10 | AS 2014 | Table 2.1 https://assets.publishing.service.gov.uk/media/5a7dbf0fe5274a5eb14e6efc/2014-12-02_Table_2.1_-_online_final.xlsx; welfare-cap table https://assets.publishing.service.gov.uk/media/5a7debb440f0b62305b7f9ed/2014-11-_30_Welfare_Cap_-_online_table_final2.xlsx |
| 11 | Budget 2015 | Table 2.1 https://assets.publishing.service.gov.uk/media/5a7f23c240f0b6230268dad4/2015-03-17_Table_2_1_FINAL__online_.xlsx; Table 2.2 https://assets.publishing.service.gov.uk/media/5a74e1e3ed915d3c7d528af3/2015-03-18_Table_2.2_final__online_.xlsx |
| 12 | Summer Budget 2015 | Table 2.1 https://assets.publishing.service.gov.uk/media/5a7f102040f0b62305b84d75/2015-07-07_online_scorecard.xlsx |
| 13 | SR&AS 2015 | Table 2.1 https://assets.publishing.service.gov.uk/media/5a7f7bd5ed915d74e33f6b6b/2015-11-24_FINAL_online_scorecard_v1.xlsx |
| 14 | Budget 2016 | Table 2.1 https://assets.publishing.service.gov.uk/media/5a800ee940f0b6230269141c/B2016Table_2.1.xlsx; Table 2.2 https://assets.publishing.service.gov.uk/media/5a74cc4440f0b61df477892d/B2016Table2.2.xlsx |
| 15 | AS 2016 | Table 2.1 https://assets.publishing.service.gov.uk/media/5a81b404ed915d74e33ffa2a/20161122_Autumn_Statement_Policy_Decisions_-_ONLINE.xlsx |
| 16 | SB 2017 | Table 2.1 https://assets.publishing.service.gov.uk/media/5a809e12e5274a2e8ab512bd/20170308_Table_2.1_-_ONLINE_VERSION.xlsx; Table 2.2 https://assets.publishing.service.gov.uk/media/5a814d8fe5274a2e8ab533dd/Table_2.2_-_ONLINE.xlsx |
| 17 | AB 2017 | Table 2.1 https://assets.publishing.service.gov.uk/media/5a75006140f0b6399b2afe09/B2017Table2.1.xlsx; Table 2.2 https://assets.publishing.service.gov.uk/media/5a81d002ed915d74e62343eb/B2017Table2.2.XLSX |
| 18 | SS 2018 | **None found** (no HMT documents page). |
| 19 | Budget 2018 | Table 2.1 https://assets.publishing.service.gov.uk/media/5bd60d25e5274a6e3cff0ce7/Table_2.1_Budget_2018_policy_decisions.xlsx; Table 2.2 on the same page |
| 20 | SS 2019 | **None found.** WMS only. |
| 21 | Budget 2020 | Table 2.1 https://assets.publishing.service.gov.uk/media/5e6a3f9ad3bf7f269dbeeef9/Table_2.1._Budget_2020.xlsx; Table 2.2 https://assets.publishing.service.gov.uk/media/5e67c4b5e90e070ac58c629b/Table_2.2_final.xlsx |
| 22 | SR 2020 | Table 1.1 "Policy decisions since Budget 2020" https://assets.publishing.service.gov.uk/media/5fbe3a8ad3bf7f572b163f7d/Table_1.1_Policy_decisions_since_Budget_2020.xlsx |
| 23 | Budget 2021 | Table 2.1 https://assets.publishing.service.gov.uk/media/603e271ae90e077dd08f15ae/Table_2.1_Policy_decisions_at_Budget_2021.xlsx; Table 2.2 https://assets.publishing.service.gov.uk/media/603e690cd3bf7f02223ebaa6/Table_2.2_2021.xlsx |
| 24 | ABSR 2021 | Table 5.1 (corrected) https://assets.publishing.service.gov.uk/media/617c224cd3bf7f5603ecf152/Table_5.1_-_Policy_decisions_at_Autumn_Budget_and_Spending_Review_2021_corrected.xlsx; Table 5.2 on the same page. Two correction slips are also attached. |
| 25 | SS 2022 | Table 3.1 https://assets.publishing.service.gov.uk/media/623a2f41e90e0779a2c99543/Table_3.1_Policy_decisions_at_Spring_Statement_2022.xlsx |
| 26 | AS 2022 | Table 5.1 https://assets.publishing.service.gov.uk/media/6376126ce90e072854bcab28/Table_5.1_Autumn_Statement_2022_policy_decisions.xlsx; Table 5.2 Growth Plan reversals https://assets.publishing.service.gov.uk/media/637612838fa8f57715d83cdf/Table_5.2_Growth_Plan_2022_reversals.xlsx |
| 27 | SB 2023 | Table 4.1 https://assets.publishing.service.gov.uk/media/6410e2e68fa8f556141b030a/Table_4.1_Policy_decisions_at_Spring_Budget_2023.xlsx; Table 4.2 on the same page; correction slip attached |
| 28 | AS 2023 | Table 5.1 (file name "UPDATE_3") https://assets.publishing.service.gov.uk/media/6560c4091fd90c000dac3b87/Table_5.1_Policy_decisions_at_Autumn_Statement_2023_UPDATE_3.xlsx; correction slip attached |
| 29 | SB 2024 | Table 5.1 https://assets.publishing.service.gov.uk/media/65e85f423649a20011ed630e/Table_5.1_-_Spring_Budget_2024_Policy_Decisions.xlsx; Table 5.2 on the same page |
| 30 | AB 2024 | Table 5.1 https://assets.publishing.service.gov.uk/media/67222f364da1c0d41942a9b2/Table_5.1_-_Autumn_Budget_2024_Policy_Decisions.xlsx; Table 5.2 on the same page |
| 31 | SS 2025 | **No XLS.** Table 3.1 "Spring Statement 2025 policy decisions" sits in the HTML document `/government/publications/spring-statement-2025-document/spring-statement-2025-html` (text-verified via the Content API) and the PDF https://assets.publishing.service.gov.uk/media/67e3ec2df356a2dc0e39b488/E03274109_HMT_Spring_Statement_Mar_25_Web_Accessible_.pdf |
| 32 | AB 2025 | Table 4.1 https://assets.publishing.service.gov.uk/media/69269df29fd433badebc31b3/Table_4.1_-_Budget_2025_Policy_Decisions.xlsx; Table 4.2 https://assets.publishing.service.gov.uk/media/692622272945773cf12dd0a0/Table_4.2_-_Measures_announced_at_Spring_Statement_2025_or_earlier_that_will_take_effect_from_27_November_2025_or_later.xlsx |

Caveat on 2010–2012 (rows 1–5): those GOV.UK PDFs are migrated copies. Their `Last-Modified` dates are 2013 (e.g. 0061.pdf: Sat, 05 Oct 2013). The original 2010–12 HMT web pages, which may have attached the scorecard tables as XLS, are only on the Wayback Machine (e.g. `hm-treasury.gov.uk/junebudget_documents.htm` captured 20100628033415, `2011budget_documents.htm` 20110326221320, `as2011_documents.htm` 20111201173019, `budget2012_documents.htm` 20120321172848). I did not open those captures to list their links.

## 4. DWP benefit expenditure and caseload tables (forecast vintages)

- Collection: `/government/collections/benefit-expenditure-and-caseload-tables` (group "Benefit expenditure and caseload tables from 2010").
- There is one page per calendar year; each holds the "Outturn and forecast" workbook for that year's Budget or Spring vintage and its Autumn vintage.
- **Every vintage from June Budget 2010 to Autumn Budget 2025 exists on GOV.UK.** The DWP labels do not always match the event names (see the label column).
- DWP publishes these **with a lag of 2–8 weeks after the event**. Several current files are **later revisions**: the forecast vintage is the same, but errors were corrected.

### 4.1 Per-event DWP vintage

For pages before 2018, the date the vintage was added comes from the page `change_history`. For 2010–2012 the pages are migration stubs dated 31 Dec. "Current-file media date" is decoded from the GOV.UK media ObjectId and gives the upload date of the file now served. Every pre-2018 asset carries a Feb-2018 date from the asset-manager migration, so for those files the media date says nothing.

| # | Event | DWP page (`/government/publications/...`) | Attachment label | Current file URL | Vintage added / revisions |
|---|---|---|---|---|---|
| 1 | June 2010 | `benefit-expenditure-and-caseload-tables-2010` | "Outturn and Forecast: June Budget 2010" | https://assets.publishing.service.gov.uk/media/5a7b8c9a40f0b62826a044b3/june_budget2010.zip | Inner xls dated 2010-09-15 (zip listing of the sample download). Tables run to 2015/16. |
| 2 | Autumn 2010 | same | "Outturn and Forecast: Autumn Statement 2010" | https://assets.publishing.service.gov.uk/media/5a756ce5ed915d7314959dbc/autumn2010.zip | DWP calls the Nov-2010 vintage "Autumn Statement 2010". Release date unknown. |
| 3 | Budget 2011 | `data-about-people-that-were-receiving-benefits-in-2011-as-published-with-the-budget-and-the-autumn-statement` | "Outturn and Forecast: Budget 2011" | https://assets.publishing.service.gov.uk/media/5a7ba3abe5274a7202e1877c/budget2011.zip | release date unknown |
| 4 | AS 2011 | same | "Outturn and Forecast: Autumn Statement 2011" | https://assets.publishing.service.gov.uk/media/5a7b7e91e5274a7202e178b2/autumn2011.zip | release date unknown |
| 5 | Budget 2012 | `benefit-expenditure-and-caseload-tables-2012` | "Outturn and forecast budget 2012" | https://assets.publishing.service.gov.uk/media/5a7bae66ed915d4147621f42/budget_2012_300712.xls | File name suggests a 30 Jul 2012 file |
| 6 | AS 2012 | same | "Outturn and forecast Autumn Statement 2012" | https://assets.publishing.service.gov.uk/media/5a74c44040f0b619c865a443/budget_2012_211212.xls | File name suggests 21 Dec 2012 (named "budget_2012" but labelled AS 2012) |
| 7 | Budget 2013 | `benefit-expenditure-and-caseload-tables-2013` | "Outturn and forecast: Budget 2013" | https://assets.publishing.service.gov.uk/media/5a7c01d2e5274a7318b90764/expenditure_tables_Budget_2013.xls | Page first published 2013-04-23 |
| 8 | AS 2013 | same | "Outturn and forecast: Autumn Statement 2013" | https://assets.publishing.service.gov.uk/media/5a7d5f27e5274a7b50cce8fe/outturn-and-forecast-expenditure-201213.xls | Added 2013-12-09; updated 2013-12-20; updated 2014-01-20 "with more up to date figures from HMRC" |
| 9 | Budget 2014 | `benefit-expenditure-and-caseload-tables-2014` | "Outturn and forecast: Budget 2014" | https://assets.publishing.service.gov.uk/media/5a7eaabbe5274a2e87db123f/outturn-and-forecast-budget-2014.xls | Summary 2014-03-26; full version 2014-04-23; formula amendment 2014-05-01 |
| 10 | AS 2014 | same | "Outturn and forecast: Autumn Statement 2014" | https://assets.publishing.service.gov.uk/media/5a74aee8e5274a56317a64a6/Outturn-and-forecast-AS-2014.xlsx | Amended 2015-02-09 (Social Fund rows, Winter Fuel Payment split) |
| 11 | Budget 2015 | `benefit-expenditure-and-caseload-tables-2015` | "Outturn and forecast: March Budget 2015" | https://assets.publishing.service.gov.uk/media/5a8087f3ed915d74e622efe5/Outturn-and-forecast-Budget-2015.xlsx | 2015-03-23; full version 2015-03-26 |
| 12 | Summer Budget 2015 | same | "Outturn and forecast: Summer Budget 2015" | https://assets.publishing.service.gov.uk/media/5a74dd26ed915d3c7d5288a9/outturn-and-forecast-summer-budget-2015-v2.xlsx | Added 2015-09-22; v2 with revised ESA 2015/16 on 2015-09-30 |
| 13 | SR&AS 2015 | same | "Outturn and forecast: Autumn Statement 2015" | https://assets.publishing.service.gov.uk/media/5a816681ed915d74e33fe007/outturn-and-forecast-autumn-statement-2015.xlsx | Added 2015-12-22; revised 2016-01-07 (DLA split) and 2016-02-15 |
| 14 | Budget 2016 | `benefit-expenditure-and-caseload-tables-2016` | "Outturn and forecast: March Budget 2016" | https://assets.publishing.service.gov.uk/media/5a81919c40f0b62302698038/outturn-and-forecast-budget-2016.xlsx | 2016-04-07; revised 2016-05-03 and 2016-05-18 |
| 15 | AS 2016 | same | "Outturn and forecast: Autumn Statement 2016 (XLS/ODS)" | https://assets.publishing.service.gov.uk/media/5a7f310840f0b62305b85a4b/outturn-and-forecast-autumn-statement-2016.xlsx | Added 2016-12-21 |
| 16 | SB 2017 | `benefit-expenditure-and-caseload-tables-2017` | "Outturn and forecast: Spring Budget 2017" | https://assets.publishing.service.gov.uk/media/5a74dd5f40f0b65f61322db5/outturn-and-forecast-spring-budget-2017.xlsx | Added 2017-03-21; revised 2017-03-27 (FY GDP deflator) |
| 17 | AB 2017 | same | "Outturn and forecast: Autumn Budget 2017" | https://assets.publishing.service.gov.uk/media/5a820c7b40f0b62305b92336/outturn-and-forecast-autumn-budget-2017.xlsx | Added 2017-12-21; revised 2018-01-23 |
| 18 | SS 2018 | `benefit-expenditure-and-caseload-tables-2018` | "Outturn and forecast: Spring Statement 2018" | XLS https://assets.publishing.service.gov.uk/media/5ab0f19640f0b62d8291e35b/outturn-and-forecast-spring-statement-2018.xlsx (media date 2018-03-20); ODS revised 2018-10-11 | Page first published 2018-03-21 |
| 19 | Budget 2018 | same | "Outturn and forecast: Autumn Budget 2018" | https://assets.publishing.service.gov.uk/media/5bf29689e5274a2b126a3243/outturn-and-forecast-autumn-budget-2018.xlsx | Added 2018-11-21 |
| 20 | SS 2019 | `benefit-expenditure-and-caseload-tables-2019` | "Outturn and forecast: Spring Statement 2019" | https://assets.publishing.service.gov.uk/media/5cbf2256e5274a74e0b11bc8/outturn-and-forecast-spring-statement-2019.xlsx | 2019-04-24. There was no autumn 2019 vintage (no event). |
| 21 | Budget 2020 | `benefit-expenditure-and-caseload-tables-2020` | "Outturn and forecast: Spring Budget 2020" | https://assets.publishing.service.gov.uk/media/5eb9224786650c2799a57ab1/outturn-and-forecast-spring-statement-2020.xlsx | Page first published 2020-03-20, but the current file's media date is 2020-05-11. It was replaced without a change note, so the original version is unknown. |
| 22 | SR 2020 | same | "Outturn and forecast: Autumn Budget 2020" | https://assets.publishing.service.gov.uk/media/600550e0e90e0763a5d760c9/outturn-and-forecast-autumn-budget-2020-revised.xlsx | Added 2020-12-22; revised 2021-01-18 (sum formula) |
| 23 | Budget 2021 | `benefit-expenditure-and-caseload-tables-2021` | "Outturn and forecast: Spring Budget 2021" | https://assets.publishing.service.gov.uk/media/6050b444e90e075280ad694b/outturn-and-forecast-spring-statement-2021.xlsx | 2021-03-19 |
| 24 | ABSR 2021 | same | "Outturn and Forecast tables: Autumn Budget 2021" (ODS only) | https://assets.publishing.service.gov.uk/media/61967bf68fa8f50382034d2a/outturn-and-forecast-tables-autumn-budget-2021.ods | Added 2021-11-19 |
| 25 | SS 2022 | `benefit-expenditure-and-caseload-tables-2022` | "Outturn and Forecast tables: Spring Statement 2022" | https://assets.publishing.service.gov.uk/media/628765278fa8f5561f02a41b/outturn-and-forecast-spring-statement-2022.xlsx | 2022-05-24 |
| 26 | AS 2022 | same | "Outturn and Forecast tables: Autumn Statement 2022" | https://assets.publishing.service.gov.uk/media/63a05310d3bf7f375f7c4359/outturn-and-forecast-tables-autumn-statement-2022.xlsx | Added 2022-12-21 |
| 27 | SB 2023 | `benefit-expenditure-and-caseload-tables-2023` | "Outturn and Forecast tables: Spring Budget 2023" | https://assets.publishing.service.gov.uk/media/644273aa8b86bb0013f1b70e/outturn-and-forecast-tables-spring-budget-2023.xlsx | 2023-04-24/25 |
| 28 | AS 2023 | same | "Outturn and Forecast tables: Autumn Statement 2023" | https://assets.publishing.service.gov.uk/media/660d6d6297e606001a2b2235/outturn-and-forecast-tables-autumn-statement-2023.xlsx | Added 2023-12-21; updated 2024-01-02 and 2024-01-16; **replaced 2024-04-03 to correct UC figures** |
| 29 | SB 2024 | `benefit-expenditure-and-caseload-tables-2024` | "Outturn and forecast tables: Spring Budget 2024" | https://assets.publishing.service.gov.uk/media/664b4ec8993111924d9d3823/outturn-and-forecast-tables-spring-budget-2024.xlsx | 2024-04-18/19; UC breakdowns added 2024-05-21 |
| 30 | AB 2024 | same | "Outturn and Forecast tables: Autumn Statement 2024" (the file is named autumn-budget-2024) | https://assets.publishing.service.gov.uk/media/67c84efa2ecc810ad1fc659e/outturn-and-forecast-tables-autumn-budget-2024.xlsx | Added 2024-11-21; corrected 2024-12-09 and 2025-01-06; updated 2025-03-07 |
| 31 | SS 2025 | `benefit-expenditure-and-caseload-tables-2025` | "Outturn and forecast tables: Spring Statement 2025" | https://assets.publishing.service.gov.uk/media/68f8923724fc2bb7eed11ac8/outturn-and-forecast-tables-spring-statement-2025.xlsx | 2025-04-22/23; **updated 2025-10-22** (IB caseload totals) |
| 32 | AB 2025 | same | "Outturn and forecast tables: Autumn Budget 2025" | https://assets.publishing.service.gov.uk/media/694931be888ddc41b48a546f/outturn-and-forecast-tables-autumn-budget-2025.xlsx | Added 2025-12-18; updated 2026-01-05 |

The methodology note is at `/government/publications/benefit-expenditure-and-caseload-tables-guidance-and-methodology`. The 2026 page, holding "Spring Forecast 2026", is outside scope.

### 4.2 Implication for vintage faithfulness

For rows 8–17, 21, 22 and 28–32, the file served today is not the file published at the time. Whether the original first-release versions are on the Wayback Machine is **unknown**: I did not run CDX lookups per file for DWP. For HMRC files, replaced GOV.UK attachments return **410** (section 5.2), so the originals can only come from web archives.

## 5. HMRC statistics with event-tied vintages

### 5.1 Income tax liabilities statistics (ITL; projected years)

- Collection: `/government/collections/income-tax-statistics-and-distributions` (groups "National statistics" and "Previous publications").
- **Release pattern, verified from the PDF text of my sample downloads and from Table 2.5's change history:**
  - Twice a year up to Feb 2015: a January/February edition projected on the OBR autumn EFO, and an April/May edition projected on the March Budget EFO.
  - The Jan 2013 PDF says its projections are "consistent with the OBR's December 2012 EFO".
  - The Apr 2013 PDF says "March 2013 Economic and fiscal outlook".
  - From 2016, once a year in May/June, projected on that spring's March EFO.
  - The May 2017 PDF says "March 2017 Economic and fiscal outlook". It also promised a Jan/Feb 2018 update on the Autumn Budget 2017 forecast, but no such edition is on GOV.UK, and the change history of `/government/statistics/income-tax-liabilities-by-income-range` shows no winter update after 2015-02-13.

| ITL edition (GOV.UK page) | Published | Projection basis | Tied event |
|---|---|---|---|
| Early-2010 edition (old HMRC site; Wayback `hmrc.gov.uk/stats/income_tax/table2-1.pdf` captures 20100424/20100806) | ~2010 | **unknown** (pre-OBR) | none; this is what was in force at June 2010 |
| "January 2011" PDF on `/government/statistics/income-tax-liabilities-statistics-tax-year-2008-to-2009-to-tax-year-2011-to-2012` (https://assets.publishing.service.gov.uk/media/5a7ba86440f0b645ba3c5bbe/Income_tax_liabilities_statistics_January_2011.pdf) | Jan 2011 | inferred Nov 2010 EFO (not text-verified) | Autumn 2010 |
| "April 2011" PDF, same page (https://assets.publishing.service.gov.uk/media/5a7c1f4ced915d210ade1b7e/Income_tax_liabilities_statistics_April_2011.pdf) | 27 Apr 2011 | inferred Mar 2011 EFO | Budget 2011 |
| Jan/Feb 2012 edition | **not found** on GOV.UK. No Wayback capture of a changed table between 20110615 and 20120505. | unknown | AS 2011: **gap** |
| "April 2012" on `...2009-to-2010-to-tax-year-2012-to-2013` (https://assets.publishing.service.gov.uk/media/5a7c1c06e5274a25a914082a/Income_tax_liabilities_statistics_April_2012.pdf) | 26 Apr 2012 | inferred Mar 2012 EFO | Budget 2012 |
| "January 2013" on `/government/statistics/income-tax-liabilities-statistics-2010-to-2014` (https://assets.publishing.service.gov.uk/media/5a7d650b40f0b60aaa294294/Income_tax_Liabilities_Statistics_-_January_2013.pdf) | Jan 2013 | **Dec 2012 EFO (text-verified)** | AS 2012 |
| "April 2013" same page (https://assets.publishing.service.gov.uk/media/5a7c5de140f0b62aff6c12c0/liabilities.pdf) | 29 Apr 2013 | **Mar 2013 EFO (text-verified)** | Budget 2013 |
| "February 2014" on `...2011-to-2012-to-tax-year-2013-to-2014` (https://assets.publishing.service.gov.uk/media/5a75bdbded915d506ee8123f/Income_Tax_Liabilities_Statistics_-_February_2014.pdf) | Feb 2014 (Table 2.5 change 2014-02-07) | inferred Dec 2013 EFO | AS 2013 |
| "April 2014" (https://assets.publishing.service.gov.uk/media/5a7e3d3be5274a2e8ab46bbb/Income_Tax_Liabilities_Statistics_-_April_2014.pdf) | 30 Apr 2014 | inferred Mar 2014 EFO | Budget 2014 |
| "February 2015" on `...2012-to-2013-to-tax-year-2014-to-2015` (https://assets.publishing.service.gov.uk/media/5a80f480e5274a2e8ab531d7/Income_Tax_Liabilities_Statistics_-_February_2015.pdf) | 13 Feb 2015 | inferred Dec 2014 EFO | AS 2014 |
| "May 2015" on `...2012-to-2013-to-tax-year-2015-to-2016` (https://assets.publishing.service.gov.uk/media/5a818468e5274a2e8ab546ac/Income_Tax_Liabilities_Statistics_May_2015.pdf) | 22 May 2015 | inferred Mar 2015 EFO | Budget 2015 (March) |
| May 2016 (`...2013-to-2014-to-tax-year-2016-to-2017`) | 18 May 2016 | Mar 2016 EFO (stated in a historical-table footnote in the May 2017 PDF) | Budget 2016 |
| May 2017 (`...2014-to-2015-to-tax-year-2017-to-2018`) | 31 May 2017 | **Mar 2017 EFO (text-verified)** | SB 2017 |
| May 2018 (`...2015-to-2016-to-tax-year-2018-to-2019`) | 25 May 2018 | inferred Mar 2018 EFO | SS 2018 |
| June 2019 (`...2016-to-2017-to-tax-year-2019-to-2020`) | 28 Jun 2019 | inferred Mar 2019 EFO | SS 2019 |
| June 2020 (`...2017-to-2018-to-tax-year-2020-to-2021`) | 26 Jun 2020 | inferred Mar 2020 EFO | Budget 2020 |
| June 2021 (`...2018-to-2019-to-tax-year-2021-to-2022`) | 30 Jun 2021 | **Mar 2021 EFO** (commentary HTML; the summary page says "March 2020", which looks like a typo) | Budget 2021 |
| June 2022 (`...2019-to-2020-to-tax-year-2022-to-2023`) | 30 Jun 2022 | **Mar 2022 EFO** (HTML) | SS 2022 |
| June 2023 (`...2020-to-2021-to-tax-year-2023-to-2024`) | 29 Jun 2023 | **Mar 2023 EFO** (HTML; projected from the 2019-20 SPI) | SB 2023 |
| June 2024 (`...2021-to-2022-to-tax-year-2024-to-2025`) | 26–27 Jun 2024 | **Mar 2024 EFO** (HTML) | SB 2024 |
| June 2025 (`...2022-to-2023-to-tax-year-2025-to-2026`) | 25–26 Jun 2025 | **Mar 2025 EFO** (HTML) | SS 2025 |
| July 2026 (`...2023-to-2024-to-tax-year-2026-to-2027`) | 15 Jul 2026 | Mar 2026 EFO | (after AB 2025) |

No ITL edition is tied to these events:

- June 2010
- AS 2011
- Summer Budget 2015
- SR&AS 2015
- AS 2016
- AB 2017
- Budget 2018
- SR 2020
- ABSR 2021
- AS 2022
- AS 2023
- AB 2024
- AB 2025

The pre-2011 HMRC tables are on the Wayback Machine under `hmrc.gov.uk/stats/income_tax/` (table2-1 … table2-7, pdf and xls). Distinct-content captures exist at 20100424/20100806, 20110202 (= Jan 2011 edition), 20110615 (= Apr 2011) and 20120505/20120604 (= Apr 2012). The CDX listing is in the cache.

### 5.2 Direct effects of illustrative tax changes (tax ready reckoner)

- Live page: `/government/statistics/direct-effects-of-illustrative-tax-changes`; collection `/government/collections/tax-expenditures-and-ready-reckoners`.
- **The page is overwritten in place** and today carries only the June 2025 edition: https://assets.publishing.service.gov.uk/media/68552862b46781eacfd71d71/June_2025_TRR_ODS__1_.ods. The body says it is "up to and including the Spring Statement 2025" and that "Archived copies of this publication can be found in The National Archives".
- Old attachments return **HTTP 410** on GOV.UK. Examples:
  - `.../attachment_data/file/414437/20150318_effectsillustrativechangesR4_v2_published.xlsx`
  - `.../file/680942/Table_for_publication_Final.xlsx`
  - `.../file/1048408/Direct_Effects_of_Illustrative_Tax_Changes_Jan_22_Final_ODS.ods`
  - `/media/6674053dd427ab249955cec9/Final_S24_ODS_file.ods`
- The edition dates below come from the page's `change_history`. The file names were recovered from Wayback captures of the page (`https://web.archive.org/web/<ts>id_/https://www.gov.uk/government/statistics/direct-effects-of-illustrative-tax-changes`). "Wayback copy of table" is the result of a CDX lookup of the exact asset URL on both `www.gov.uk` and `assets.publishing.service.gov.uk`.

| Edition (change_history) | Tied event | File(s) named in the page capture | Wayback copy of table |
|---|---|---|---|
| hmrc.gov.uk `stats/tax_expenditures/table1-6.xls` / `.pdf` ("Table 1.6 – Direct effects of illustrative tax changes", confirmed from Wayback `menu.htm` 20110507) | June 2010 → Budget 2012 | Captures 20100424 (pdf), 20101006, 20110202, 20110406/20110615, 20120104/20120207, 20120405 | Captured, but which event each capture matches is **inferred from dates only** |
| hmrc.gov.uk `statistics/expenditures/table1-6.xls` / `.pdf` | AS 2012? / Budget 2013? | Captures 20131011 (xls/pdf) and 20140114 (pdf) | Captured. The AS 2012 edition is **unknown**. |
| 2013-10-28 GOV.UK first published | (Budget 2013 basis?) | unknown | unknown |
| 2014-03-19 | Budget 2014 | not in captures (first page capture is 2015-05) | unknown |
| 2014-12-03 (also a separate page `/government/statistics/direct-effects-of-illustrative-tax-changes-december-2014`) | AS 2014 | — | separate page captured 20190723 and 20260313; asset not checked |
| 2015-03-18 | Budget 2015 | `file/414437/20150318_effectsillustrativechangesR4_v2_published.xlsx` | **none** (www: none; assets: none) |
| 2015-07-08 | Summer Budget 2015 | `file/442580/Jul15_effectsillustrativechanges_Final.xlsx`; bulletin pdf `file/442579` | xlsx none; table pdf `file/442581` only a 301 capture (20160118); bulletin captured (www 20151113044406 200) |
| 2015-11-25 | SR&AS 2015 | not captured | unknown |
| 2016-03-16 | Budget 2016 | `file/513915/Mar16_..._R4_pub.xlsx`; bulletin `file/508120` | xlsx none on either host (retry); bulletin captured (www 20160608132545 200) |
| 2016-11-23 | AS 2016 | `file/571368/Nov16_...xlsx`, `file/571370/Nov16_...pdf` | xlsx none; **table pdf captured (assets 20170214133003 200)** |
| 2017-04-19 | SB 2017 | `file/608034/Table_for_publication_v1.3.xlsx`, `file/609275/..._v1_3.pdf` | xlsx unknown (CDX 503 twice); pdf none on either host; bulletin `file/608033` captured (assets 20171013135406 200) |
| 2018-01-17 | AB 2017 | `file/680942/Table_for_publication_Final.xlsx`, `file/680944/...pdf` | none (bulletin `file/680941` only 404/410 captures) |
| 2018-04-24 | SS 2018 | `file/714484/SS18_Table_for_publicationFinal_v1.1.xlsx`, `file/714485/...pdf` | none |
| 2019-01-25 | Budget 2018 | not captured | unknown |
| 2019-04-26 | SS 2019 | `file/797043/Table_for_Publication_Apr19.ods`, `file/797044/...pdf` | **captured** (assets 20190725004804 200 ods; 20190725004803 200 pdf) |
| 2020-05-01 | Budget 2020 | `file/881033/Tax_Ready_Reckoner_Table_May20.ods` | none |
| 2021-01-22 | SR 2020 | `file/954599/Jan21_Direct_Effects_of_Illustrative_Tax_Changes_Table_FINAL.ods` | none |
| 2021-06-24 | Budget 2021 | `file/995928/Direct_Effects_of_Illustrative_Tax_Changes_June_2021.ods` | none |
| 2022-01-21 | ABSR 2021 | `file/1048408/Direct_Effects_of_Illustrative_Tax_Changes_Jan_22_Final_ODS.ods` | none |
| 2022-06-16 | SS 2022 | `file/1082493/Direct_Effects_of_Illustrative_Tax_Changes_June_22_ODS.ods` (the target of the 410 redirects) | not checked |
| 2023-01-31 | AS 2022 | page capture 20230312 had no parsable attachment links | unknown |
| 2023-06-30 | SB 2023 | not captured | unknown |
| 2024-01-23 | AS 2023 | capture 20240123 had no parsable links | unknown |
| 2024-06-28 | SB 2024 | `/media/6674053dd427ab249955cec9/Final_S24_ODS_file.ods` | none |
| 2025-01-28 | AB 2024 | `/media/678e6033af483d80fc9bdb08/TRR_January_2025_-_final.ods` | none |
| 2025-06-24 | SS 2025 | `/media/68552862b46781eacfd71d71/June_2025_TRR_ODS__1_.ods` (**live**) | live on GOV.UK; also captured (assets 20250624110021 200) |
| — | AB 2025 | **No post-AB2025 edition found.** As of 2026-10-09 the page still shows June 2025, and a GOV.UK search for HMRC items since 2025-07-01 found none. | — |

**Bottom line for the ready reckoner:** two editions survive as tables, live or in the Wayback Machine:

- SS 2019 (ods and pdf, Wayback)
- SS 2025 (live)

Two more survive only as pdf tables (no spreadsheet):

- AS 2016 (Wayback)
- Old-site table 1.6 snapshots, 2010–2014

Bulletins alone survive for Summer Budget 2015, Budget 2016 and SB 2017. Every other edition is unknown or missing outside the UKGWA, which I could not query. The CDX results are in `/tmp/uk-replay-scope/agents/work_archive/detc_wayback_assets.json` and the background-task outputs. The retry results for lookups that first returned 503/504 are in `/tmp/uk-replay-scope/agents/work_archive/retry_detc.txt`. After the retry, the SB 2017 xlsx and the SS 2019 bulletin still returned 503, so both are **unknown**.

### 5.3 Personal incomes statistics (SPI aggregates)

- Collection: `/government/collections/personal-incomes-statistics`. Edition pages and their first publication dates are listed below.
- These are published aggregates. The SPI Public Use Tape microdata is distributed through the UK Data Service under its own licence; this research did not look at it.

| SPI tax year | GOV.UK page (`/government/statistics/...`) | First published |
|---|---|---|
| 2010-11 | `personal-incomes-statistics-for-the-tax-year-2010-to-2011` (+ tables 3.11–3.15a `personal-incomes-statistics-2010-to-2011--2`, 2013-01-31) | 2012-12-28 |
| 2011-12 | `personal-incomes-statistics-for-the-tax-year-2011-to-2012` (+3.12–3.15a 2014-02-28) | 2014-01-31 |
| 2012-13 | `personal-incomes-statistics-tables-31-to-311-for-the-tax-year-2012-to-2013` (+3.12–3.15a 2015-02-27) | 2015-01-30 |
| 2013-14 | `personal-incomes-statistics-for-the-tax-year-2013-to-2014` (+3.12–3.15a 2016-03-31) | 2016-03-01 |
| 2014-15 | `personal-incomes-statistics-for-the-tax-year-2014-to-2015` | 2017-03-02 (updated 2017-04-19) |
| 2015-16 | `personal-incomes-tables-31-to-311-for-the-tax-year-2015-to-2016` | 2018-03-06 |
| 2016-17 | `personal-incomes-statistics-for-the-tax-year-2016-to-2017` | 2019-03-06 |
| 2017-18 | `personal-incomes-statistics-for-the-tax-year-2017-to-2018` | 2020-03-05 (updated 2020-06-26) |
| 2018-19 | `personal-incomes-statistics-for-the-tax-year-2018-to-2019` | 2021-03-31 |
| 2019-20 | `personal-incomes-statistics-for-the-tax-year-2019-to-2020` | 2022-03-16 |
| 2020-21 | `personal-incomes-statistics-for-the-tax-year-2020-to-2021` | 2023-03-08 (updated 2024-02-29) |
| 2021-22 | `personal-incomes-statistics-for-the-tax-year-2021-to-2022` | 2024-02-29 |
| 2022-23 | `personal-incomes-statistics-for-the-tax-year-2022-to-2023` | 2025-03-12 |
| 2023-24 | `personal-incomes-statistics-for-the-tax-year-2023-to-2024` | 2026-04-29 |

- SPI years 2007-08 to 2009-10, which were current at events 1–5, are not on GOV.UK. They would be on the old HMRC site (`hmrc.gov.uk/stats/income_distribution/`), whose Wayback holdings I did not check: **unknown**.
- The 19 "Individual Tables" pages (3.1–3.15a) are **overwritten in place**. Their file names say "2010-to-2011", but they now hold 2023-24 data.

### 5.4 Estimated costs of tax reliefs

- Collection: `/government/collections/tax-relief-statistics`.
- Current page: `/government/statistics/tax-reliefs`, first published 2026-01-22, with the Jan 2026 edition https://assets.publishing.service.gov.uk/media/69a0194e3e672177d0bc76e6/tax_relief_statistics_january_2026.ods.
- Older pages:
  - `/government/statistics/main-tax-expenditures-and-structural-reliefs` (now titled "Non-structural tax reliefs")
  - `/government/statistics/minor-tax-expenditures-and-structural-reliefs` ("Structural tax reliefs")
- These keep only the Jan 2023, May 2023, Dec 2023, May 2024 and Dec 2024 files. The 2022-08-03 change note says "old releases have been removed" and links to The National Archives (UKGWA, which I could not query).

Editions, from change_history:

| Edition | Tied event |
|---|---|
| 2014-03-11 | Budget 2014 |
| 2014-12-31 (structural) / 2015-01-07 (main) | AS 2014 |
| 2015-12-31 | SR&AS 2015 |
| 2016-12-30 | AS 2016 |
| 2018-01-23 | AB 2017 |
| 2019-01-31 | Budget 2018 |
| 2019-10-10 | — |
| 2020-10-30 | — |
| 2021-12-10 | ABSR 2021 |
| 2022-05-27 | — |
| 2023-01-12 | AS 2022 |
| 2023-12-07 | AS 2023 |
| 2024-12-05 | AB 2024 |
| 2026-01-22 | AB 2025 |

Before GOV.UK: Wayback has `hmrc.gov.uk/stats/tax_expenditures/table1-5.xls` / `.pdf` ("Table 1.5 – Main tax expenditures and structural reliefs") with captures 20100424, 20101006, 20110202, 20110615, 20120207. It also has `hmrc.gov.uk/statistics/expenditures/table1-5.*` captured 20130228, 20131011 and 20140122.

## 6. HMRC tax information and impact notes (TIINs)

- The master collection `/government/collections/tax-information-and-impact-notes-tiins` only goes back to Jan 2023. Its groups:

  | Group | TIINs |
  |---|---|
  | "Spring Finance Bill 2023" | 67 |
  | "Autumn Finance Bill 2023" | 24 |
  | "Spring Finance Bill 2024" | 13 |
  | "Autumn Budget 2024" | 42 |
  | "Budget 2025" | 70 |
  | "Finance Bill 2025-26" | 15 |
  | "Finance Bill 2026-27" | 25 |
  | "TIINs published from January 2023" | 77 |

- Before 2023, TIINs sit in per-event HMRC "tax-related documents" collections.
- For autumn events from 2011 to 2016, most TIINs came out about a week later with the **draft Finance Bill ("L-day")** rather than on the day.
- Before 2013, TIINs exist only on the old `hmrc.gov.uk` site (Wayback).

| # | Event | TIIN location | Count / notes |
|---|---|---|---|
| 1 | June 2010 | **No TIINs** (format not yet in use). HMRC "Budget notes" BN01–BN6x are on Wayback at `hmrc.gov.uk/budget2010/bnNN.htm` / `.pdf` (e.g. bn01.pdf captured 20100704). | 353 budget2010 files captured on or after 2010-06-22 |
| 2 | Autumn 2010 | Draft Finance Bill 2011 (9 Dec 2010): Wayback `hmrc.gov.uk/budget-updates/autumn-tax/` | 81 TIIN-like file names, first capture 20101212. GOV.UK has only the HMT press release `/government/news/government-publishes-draft-legislation-to-implement-tax-changes`. |
| 3 | Budget 2011 | Wayback `hmrc.gov.uk/budget2011/tiinNNNN.pdf` / `.htm` | 94 TIIN-like captures, first 20110404 |
| 4 | AS 2011 | Draft FB2012 (6 Dec 2011): Wayback `hmrc.gov.uk/budget-updates/06dec11/` (31 files). GOV.UK `/government/publications/finance-bill-2012-consultation-on-draft-legislation` has 99 attachments incl. "Draft legislation, EN and TIIN"; the page is dated 2012-03-13. | Attachment dates not verified |
| 5 | Budget 2012 | Wayback `hmrc.gov.uk/budget2012/tiin-NNNN.pdf` | 85 TIIN-like captures, first 20120324. GOV.UK `/government/publications/finance-bill-2012` has 1 TIIN (fuel duty new clause). |
| 6 | AS 2012 | Draft FB2013 (11 Dec 2012): GOV.UK `/government/publications/finance-bill-2013-consultation-on-draft-legislation` (91 attachments; TIIN-titled: 0) and Wayback `hmrc.gov.uk/budget-updates/11dec12/` (31 files) | TIINs probably bundled with the legislation; **unverified** |
| 7 | Budget 2013 | Wayback `hmrc.gov.uk/budget2013/tiin-NNNN.pdf` (21 captured). GOV.UK `/government/publications/finance-bill-2013` has "Overview of tax legislation and rates: 20 March 2013" (https://assets.publishing.service.gov.uk/media/5a7ce915ed915d36e95f0679/022_fb20013_ootlar.pdf). | No HMRC GOV.UK policy papers dated 2013-03-20/21 |
| 8 | AS 2013 | GOV.UK `/government/publications/finance-bill-2014-tiins` (HTML, 10 Dec 2013); `/government/publications/tax-information-and-impact-notes-tiins-issued-in-the-autumn-statement-2013` (NICs Bill) | 24 HMRC policy papers dated 5–11 Dec 2013 |
| 9 | Budget 2014 | `/government/collections/budget-2014-hm-revenue-customs`; OOTLAR `/government/publications/finance-bill-2014-overview-documents-at-budget-2014` | 44 docs |
| 10 | AS 2014 | `/government/collections/autumn-statement-2014-hm-revenue-and-customs` (18) plus draft FB2015 (10 Dec 2014) in `/government/collections/finance-bill-2015` | 85 HMRC policy papers 3–11 Dec 2014 |
| 11 | Budget 2015 | `/government/collections/budget-2015-hm-revenue-and-customs` | TIIN group: 16; OOTLAR `/government/publications/finance-bill-2015-overview-documents-at-budget-2015` |
| 12 | Summer Budget 2015 | `/government/collections/budget-july-2015-hm-revenue-and-customs` | TIIN group: 33; OOTLAR `/government/publications/summer-finance-bill-2015-overview-documents-at-summer-budget-2015` |
| 13 | SR&AS 2015 | `/government/publications/main-tax-announcements-for-autumn-statement-2015` plus draft FB2016 (9 Dec 2015) in `/government/collections/finance-bill-2016` | 62 HMRC policy papers 25 Nov–10 Dec 2015 |
| 14 | Budget 2016 | `/government/collections/budget-2016-tax-related-documents` | 52; OOTLAR `/government/publications/budget-2016-overview-of-tax-legislation-and-rates-ootlar` |
| 15 | AS 2016 | `/government/collections/autumn-statement-2016-tax-related-documents` (5) plus draft FB2017 (5 Dec 2016) in `/government/collections/finance-bill-2017` | 59 HMRC policy papers 23 Nov–6 Dec 2016 |
| 16 | SB 2017 | `/government/collections/spring-budget-2017-tax-related-documents` | 12; OOTLAR `/government/publications/spring-budget-2017-overview-of-tax-legislation-and-rates-ootlar` |
| 17 | AB 2017 | `/government/collections/autumn-budget-2017-tax-related-documents` | 32; OOTLAR `/government/publications/autumn-budget-2017-overview-of-tax-legislation-and-rates-ootlar` |
| 18 | SS 2018 | **None found** | — |
| 19 | Budget 2018 | `/government/collections/budget-2018` | 43; OOTLAR `/government/publications/budget-2018-overview-of-tax-legislation-and-rates-ootlar` |
| 20 | SS 2019 | **None found** | — |
| 21 | Budget 2020 | `/government/collections/budget-2020-tax-related-documents` | 36; OOTLAR `/government/publications/budget-2020-overview-of-tax-legislation-and-rates-ootlar` |
| 22 | SR 2020 | **None found** (no tax collection) | — |
| 23 | Budget 2021 | `/government/collections/budget-2021-tax-related-documents` | 57; OOTLAR `/government/publications/budget-2021-overview-of-tax-legislation-and-rates-ootlar` |
| 24 | ABSR 2021 | `/government/collections/autumn-budget-2021-tax-related-documents` | 42; OOTLAR `/government/publications/autumn-budget-2021-overview-of-tax-legislation-and-rates-ootlar` |
| 25 | SS 2022 | `/government/collections/spring-statement-2022-tax-related-documents` | 4 |
| 26 | AS 2022 | `/government/collections/autumn-statement-2022-tax-related-documents` | "Autumn Finance Bill 2022" group: 9 |
| 27 | SB 2023 | `/government/collections/spring-budget-2023-tax-related-documents` | 67; OOTLAR `/government/publications/spring-budget-2023-overview-of-tax-legislation-and-rates-ootlar` |
| 28 | AS 2023 | `/government/collections/autumn-statement-2023-tax-related-documents` | 31; OOTLAR `/government/publications/autumn-statement-2023-overview-of-tax-legislation-and-rates-ootlar` |
| 29 | SB 2024 | `/government/collections/spring-budget-2024-tax-related-documents` | 14; OOTLAR `/government/publications/spring-budget-2024-overview-of-tax-legislation-and-rates-ootlar` |
| 30 | AB 2024 | `/government/collections/autumn-budget-2024-tax-related-documents` | 25 plus a draft-legislation/TIIN group; OOTLAR `/government/publications/autumn-budget-2024-overview-of-tax-legislation-and-rates-ootlar` |
| 31 | SS 2025 | `/government/collections/spring-statement-2025-tax-related-documents` | 8 docs (2 policy papers, 6 consultations); whether the policy papers are TIINs is unverified |
| 32 | AB 2025 | `/government/collections/budget-2025-tax-related-documents` | 68; OOTLAR `/government/publications/budget-2025-overview-of-tax-legislation-and-rates-ootlar` |

Counts are the sizes of the collection groups, not verified counts of TIINs. Individual TIIN pages are sometimes updated after the event (e.g. "Alcohol Duty: rates change" updated 2026-02-04).

## 7. Matrix (event → document availability)

Legend:

- **G** = live on GOV.UK
- **W** = Wayback Machine only (capture timestamp in sections 2–6)
- **G\*** = live, but the current file is a post-event revision
- **–** = none published or none found
- **?** = unknown

| # | Event | HMT costings | HMT scorecard | DWP BE&C | HMRC ITL edition tied | HMRC ready reckoner edition | TIINs |
|---|---|---|---|---|---|---|---|
| 1 | Jun 2010 | W | G (PDF, in red book) | G (zip) | – (early-2010 edition W; basis ?) | W (old table1-6; mapping inferred) | – (Budget notes W) |
| 2 | Autumn 2010 | W (SR2010 costings) | G (SR2010 PDF) | G | G Jan 2011 (basis inferred) | W (inferred) | W (Dec 2010 draft FB2011) |
| 3 | Budget 2011 | W | G (PDF) | G | G Apr 2011 (inferred) | W (inferred) | W |
| 4 | AS 2011 | W | G (PDF) | G | – / ? (no Jan 2012 edition found) | W (inferred) | W + G (FB2012 draft page) |
| 5 | Budget 2012 | W | G (PDF) | G | G Apr 2012 (inferred) | W (inferred) | W |
| 6 | AS 2012 | G | G (PDF + HTML table) | G | G Jan 2013 (verified) | ? | G/W (draft FB2013; bundling unverified) |
| 7 | Budget 2013 | G | G (XLS 2.1/2.2) | G | G Apr 2013 (verified) | W? (2013-10-11 capture) | W (+ G OOTLAR) |
| 8 | AS 2013 | G | G (XLSX) | G\* | G Feb 2014 | W? (2014-01 capture) | G |
| 9 | Budget 2014 | G | G (PDF only) | G\* | G Apr 2014 | ? (file name not recovered) | G |
| 10 | AS 2014 | G | G (XLSX) | G\* | G Feb 2015 | ? (Dec-2014 page exists; asset not checked) | G |
| 11 | Budget 2015 | G | G (XLSX) | G\* | G May 2015 | – (none in W) | G |
| 12 | Summer B 2015 | G | G (XLSX) | G\* | – | bulletin W; table – | G |
| 13 | SR&AS 2015 | G | G (XLSX) | G\* | – | ? | G (incl. draft FB2016) |
| 14 | Budget 2016 | G | G (XLSX) | G\* | G May 2016 | bulletin W; table – | G |
| 15 | AS 2016 | G | G (XLSX) | G | – | W (table PDF only) | G (incl. draft FB2017) |
| 16 | SB 2017 | G | G (XLSX) | G\* | G May 2017 (verified) | bulletin W; table ? | G |
| 17 | AB 2017 | G | G (XLSX) | G\* | – | – | G |
| 18 | SS 2018 | – | – | G\* (ODS rev.; XLSX orig.) | G May 2018 | – (none in W) | – |
| 19 | Budget 2018 | G | G (XLSX) | G | – | ? | G |
| 20 | SS 2019 | – | – | G | G Jun 2019 | **W (ODS + PDF)** | – |
| 21 | Budget 2020 | G | G (XLSX) | G\* | G Jun 2020 | – | G |
| 22 | SR 2020 | G | G (XLSX T1.1) | G\* | – | – | – |
| 23 | Budget 2021 | G | G (XLSX) | G | G Jun 2021 (verified) | – | G |
| 24 | ABSR 2021 | G | G (XLSX corrected) | G (ODS) | – | – | G |
| 25 | SS 2022 | G | G (XLSX) | G | G Jun 2022 (verified) | ? (target of 410 redirect; not checked) | G |
| 26 | AS 2022 | G | G (XLSX) | G | – | ? | G |
| 27 | SB 2023 | G | G (XLSX) | G | G Jun 2023 (verified) | ? | G |
| 28 | AS 2023 | G | G (XLSX) | G\* | – | ? | G |
| 29 | SB 2024 | G | G (XLSX) | G\* | G Jun 2024 (verified) | – | G |
| 30 | AB 2024 | G | G (XLSX) | G\* | – | – | G |
| 31 | SS 2025 | G (PDF + HTML) | G (HTML/PDF only, T3.1) | G\* | G Jun 2025 (verified) | **G (live)** | G (2 policy papers; TIIN status unverified) |
| 32 | AB 2025 | G | G (XLSX) | G\* | – | – (not published by 2026-10-09) | G |

## 8. Completeness by era and gaps

### Complete eras

- **AS 2012 to AB 2025, HMT side.** Costings and scorecards are live on GOV.UK. The exceptions are the two Spring Statements without measures (SS 2018 and SS 2019), and Budget 2014 and SS 2025, whose scorecards are only in PDF/HTML.
- **DWP, all 32 events.** Every vintage exists on GOV.UK, including June 2010 and "Autumn Statement 2010" (Nov 2010).
- **TIINs, Budget 2014 onward.** Live GOV.UK collections for every event with tax measures.

### Gaps

1. **HMT policy costings for June 2010 to Budget 2012 (events 1–5)** exist only on the Wayback Machine (captures listed in section 2). They are probably also in the UKGWA, but I could not check.
2. **Pre-2013 scorecards** exist only as tables inside migrated PDF red books. I did not text-verify the table numbers.
3. **Ready reckoner**, the biggest gap:
   - Live: only the June 2025 edition (SS 2025).
   - Old attachments: 410 Gone.
   - Wayback tables found: SS 2019 (ODS + PDF); AS 2016 (PDF only).
   - Old-site table1-6 snapshots exist for 2010–2014, but which event each matches is inferred from dates.
   - No AB 2025 edition has been published.
4. **DWP revisions.** About half of the current DWP files are post-event revisions, and replaced GOV.UK attachments generally return 410. If the original first-release file is wanted, it has to come from the Wayback Machine or the UKGWA. DWP originals: unknown (no CDX lookups run).
5. **ITL.**
   - No tied edition exists for most autumn events after Feb 2015, nor for Summer Budget 2015.
   - The AS 2011 (Jan 2012) edition was not found.
   - Projection bases for 2011–2012 and for 2014–2020 are inferred rather than text-verified, except where marked.
6. **Tax relief statistics before Jan 2023** have been removed from GOV.UK and point to the UKGWA. The old-site table1-5 is on the Wayback Machine for 2010–2014.
7. **TIINs before 2014** are only on the Wayback Machine (old hmrc.gov.uk). June 2010 had "Budget notes" rather than TIINs.
8. **UKGWA** is bot-protected and could not be queried. It is the most likely complete source for gaps 1, 3, 4 and 6.

## 9. Fetch recipe

1. **GOV.UK pages.**
   - Call `GET https://www.gov.uk/api/content<path>` for each path in sections 2–6.
   - Read `details.attachments[]` (`title`, `url`, `content_type`) and `details.change_history[]`.
   - For collections, map `details.collection_groups[].documents[]` (content_ids) to `links.documents[]`.
   - Use `listatt.py <path>` in `/tmp/uk-replay-scope/agents/work_archive/` to print these.
2. **Current asset files.** GET the `assets.publishing.service.gov.uk/media/<id>/<name>` URL directly. Record the `Last-Modified` header and the decoded ObjectId time (`int(id[:8],16)`) as provenance; any Feb-2018 ObjectId reflects the asset-manager migration.
3. **Superseded attachments** (GOV.UK returns 410).
   - Recover the attachment URL from a Wayback capture of the GOV.UK page: `https://web.archive.org/web/<ts>id_/https://www.gov.uk/<path>`; regex `/government/uploads/system/uploads/attachment_data/file/\d+/...` or `/media/<24hex>/...`.
   - Then run a CDX lookup on both `www.gov.uk<path>` and `assets.publishing.service.gov.uk<path>`: `https://web.archive.org/cdx/search/cdx?url=<host+path>&fl=timestamp,statuscode,mimetype,length`.
   - Fetch with `https://web.archive.org/web/<ts>id_/<original>` (the `id_` suffix returns the raw bytes).
4. **Pre-2013 HMT and HMRC files.** Run CDX prefix queries:
   - `url=cdn.hm-treasury.gov.uk/&matchType=prefix&filter=original:.*[Cc]osting.*` (costings)
   - `url=hm-treasury.gov.uk/d/&matchType=prefix`
   - `url=hmrc.gov.uk/budget20NN/&matchType=prefix` (TIINs)
   - `url=hmrc.gov.uk/budget-updates/&matchType=prefix` (L-day packs)
   - `url=hmrc.gov.uk/stats/income_tax/&matchType=prefix&collapse=digest` (ITL tables)
   - `url=hmrc.gov.uk/stats/tax_expenditures/&matchType=prefix&collapse=digest` (Tables 1.5 and 1.6)
   - Use `collapse=digest` to get one row per distinct content version.
5. **Politeness.** GOV.UK tolerated about 1 request per second. The Wayback Machine needed 3–6 s spacing with retries; it returned 503/504 and refused connections at about 1–2 requests per second.
6. **UKGWA.** Do not script it: it serves a WAF human-verification challenge. If a gap-filling source is needed, a person can browse `https://webarchive.nationalarchives.gov.uk/ukgwa/*/https://www.gov.uk/government/statistics/direct-effects-of-illustrative-tax-changes` interactively, or ask TNA for bulk access.

### Samples downloaded (to confirm content only)

All in `/tmp/uk-replay-scope/agents/archive_samples/`:

- `itl_jan2013.pdf` (448,557 bytes): "consistent with the OBR's December 2012" EFO.
- `itl_apr2013.pdf` (397,964 bytes): "March 2013 Economic and fiscal outlook"; describes the twice-yearly pattern.
- `itl_may2017.pdf` (1,878,903 bytes): "March 2017 Economic and fiscal outlook"; promised a Jan/Feb 2018 Autumn Budget 2017 update, which was not found.
- `dwp_june_budget2010.zip` (642,726 bytes) plus extracted `dwp_jb2010/June Budget 2010/Alltables_June budget 2010 values.xls` (zip entry dated 2010-09-15; tables to 2015/16).

HEAD checks run on 2026-10-09, all returning 200: the June 2010 red book 0061.pdf, SR2010 PDF, Budget 2011 0836.pdf, AS2011 8231.pdf, Budget 2012 1853.pdf, as2012_policy_costings.pdf, budget2013_policy_costings.pdf, AS2013 Scorecard.xlsx, Budget_2025-Policy_Costings.pdf, june_budget2010.zip, autumn2010.zip, budget_2012_211212.xls and the AB2025 DWP xlsx.
