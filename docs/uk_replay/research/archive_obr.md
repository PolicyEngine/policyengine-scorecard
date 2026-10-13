# OBR forecast tables in public archives: 32 fiscal events, June 2010 to November 2025

Scope: policyengine-scorecard issue #156, track 2 (vintage-faithful replay). Research run 2026-10-09 by a read-only agent. Every availability claim below cites a Wayback Machine capture (`/web/<timestamp>id_/` = original bytes) or the CDX query that returned no 200 capture. `unknown` means not established in this pass.

## Access status (how the evidence was gathered)

- **obr.uk**: not contacted at all (Cloudflare). All bytes and listings came from archives.
- **Wayback Machine**: works with an honest UA (`policyengine-scorecard-research/1.0`). CDX listings, `id_` replays, stored 302s and HTTP Range requests (206) all work. It throttled us (connection refused, then HTTP 503 on CDX for a few minutes) when two request streams ran in parallel at about 1.6 req/s combined; a single stream at 1 request per 1.2-2.5 s was fine.
- **UK Government Web Archive (UKGWA)**: blocked for scripted access on 2026-10-09. Replay, `cdx` and `timemap` URLs all return HTTP 405 with header `x-amzn-waf-action: captcha` and a 'Human Verification' page, e.g. `https://webarchive.nationalarchives.gov.uk/ukgwa/20240306000000/https://obr.uk/efo/economic-and-fiscal-outlook-march-2024/` and `https://webarchive.nationalarchives.gov.uk/ukgwa/cdx?url=obr.uk/efo/&matchType=prefix&output=json&limit=5`. I did not try to get past it. So **UKGWA availability is unknown for every file in this report**. The prior harvest (`~/scorecard-harvest/uk_obr/NOTES.md`, 2026-08-02) found UKGWA held obr.uk pages but not the target xlsx files.
- Samples downloaded to confirm content and vintage (all in `/tmp/uk-replay-scope/agents/archive_samples/`): `nov2010_economy_supplementary_tables_291110.xls`, `nov2010_economy_supplementary_tables_resaved_210211.xls`, `nov2010_fiscal_supplementary_tables_291110.xls`, `mar2017_Fiscal_Supplementary_Tables_Expenditure_March_2017-4.xlsx`, plus two 8 KB zip-directory tails (`nov25_dft_zip_tail.bin`, `nov25_dft_zip1_tail.bin`). Sheet names of three other xlsx files were read through Range requests without downloading them.
- CDX `length` is the compressed WARC record size, not the file size (e.g. the June 2010 tables are listed on the 2010 page as 644 KB but have CDX length 70,674).

Domain-wide CDX listings used as the master index (earliest 200 capture per URL):

- `http://web.archive.org/cdx/search/cdx?url=budgetresponsibility.independent.gov.uk&output=json&matchType=domain&fl=timestamp%2Coriginal%2Cmimetype%2Cstatuscode%2Clength&filter=original%3A.%2A%5C.%28xls%7Cxlsx%7CXLS%7CXLSX%7Czip%7CZIP%29%28%24%7C%5C%3F.%2A%29&filter=statuscode%3A200&collapse=urlkey`
- `http://web.archive.org/cdx/search/cdx?url=budgetresponsibility.independent.gov.uk&output=json&matchType=domain&fl=timestamp%2Coriginal%2Cmimetype%2Cstatuscode%2Clength&filter=original%3A.%2A%5C.%28pdf%7CPDF%29%28%24%7C%5C%3F.%2A%29&filter=statuscode%3A200&collapse=urlkey`
- `http://web.archive.org/cdx/search/cdx?url=budgetresponsibility.org.uk&output=json&matchType=domain&fl=timestamp%2Coriginal%2Cmimetype%2Cstatuscode%2Clength&filter=original%3A.%2A%5C.%28xls%7Cxlsx%7CXLS%7CXLSX%7Czip%7CZIP%29%28%24%7C%5C%3F.%2A%29&filter=statuscode%3A200&collapse=urlkey`
- `http://web.archive.org/cdx/search/cdx?url=budgetresponsibility.org.uk&output=json&matchType=domain&fl=timestamp%2Coriginal%2Cmimetype%2Cstatuscode%2Clength&filter=original%3A.%2A%5C.%28pdf%7CPDF%29%28%24%7C%5C%3F.%2A%29&filter=statuscode%3A200&collapse=urlkey`
- `http://web.archive.org/cdx/search/cdx?url=obr.uk&output=json&matchType=domain&fl=timestamp%2Coriginal%2Cmimetype%2Cstatuscode%2Clength&filter=original%3A.%2A%5C.%28xls%7Cxlsx%7CXLS%7CXLSX%7Czip%7CZIP%29%28%24%7C%5C%3F.%2A%29&filter=statuscode%3A200&collapse=urlkey`
- `http://web.archive.org/cdx/search/cdx?url=obr.uk&output=json&matchType=domain&fl=timestamp%2Coriginal%2Cmimetype%2Cstatuscode%2Clength&filter=original%3A.%2A%5C.%28pdf%7CPDF%29%28%24%7C%5C%3F.%2A%29&filter=statuscode%3A200&collapse=urlkey`

Event-page link lists came from the earliest 200 capture of each `obr.uk/efo/<slug>/` page (the 2010-2017 pages were first captured in 2018, after the site migration), cross-checked against the as-published pages on the old domains for 2010-2015. Each `/download/<slug>/` link was resolved by replaying its stored 302 (`https://web.archive.org/web/<ts>id_/https://obr.uk/download/<slug>/` without following redirects; the `Location` header gives the real `/docs/...` file). Working files: `/tmp/uk-replay-scope/agents/work_archive_obr/` (`resolved.json`, `curated.json`, `file_index.json`, `efo_pages_links.json`).

## EFO dates (verified)

All 32 expected EFO months are correct. Dates come from each archived obr.uk EFO page's download metadata; where the page stamp differs from the publication day, the publication day is used.

- Budget 2010 #2: OBR 'Budget forecast - June 2010', 22 Jun 2010. A separate 'Pre-Budget forecast' (14 Jun 2010, `pre_budget_forecast_140610.pdf`, archived 20100704212008) is not a costed event.
- Spring Budget 2021: published 3 Mar 2021 (page stamp says 2 Mar). Autumn Statement 2022: 17 Nov 2022 (page stamp 16 Nov). Spring Budget 2023: 15 Mar 2023 (page stamp 8 Mar).
- Spending Review 2020 goes with the 25 Nov 2020 EFO, whose supplementary files carry the label `AB20`.
- Autumn Budget 2025: the PDF `OBR_Economic_and_fiscal_outlook_November_2025.pdf` was captured at 11:58 UTC on 26 Nov 2025, and the OBR later posted `01122025-Investigation-into-November-2025-EFO-publication-error.pdf` (captured 20251201144334; not read).

## Table-family eras

| Era | Economy | Fiscal | Policy measures as published |
|---|---|---|---|
| Jun 2010 | one 'Budget forecast tables' xls (`junebudget_chapterc_tables.xls`) | same workbook | PDF |
| Nov 2010 - Mar 2016 | 'Economy supplementary tables' xls | one 'Fiscal supplementary tables' xls covering receipts, social security/welfare and aggregates (verified for Nov 2010: tables 1.1-1.3 receipts, 1.4 social security breakdown, 1.11-1.15 sector/economic-category aggregates) | EFO PDF annex, plus the 'charts and tables' xls of all EFO tables |
| Nov 2016 - Nov 2023 | 'supplementary economy tables' xlsx | split into 'supplementary fiscal tables: receipts and other' and 'supplementary fiscal tables: expenditure' (verified for Mar 2017: 2.4 income tax and NICs detail, 2.21 post-measures welfare breakdown, 2.22 UC marginal cost) | charts and tables xlsx (Nov 2016 workbook verified to hold Annex A tables TA.1-TA.3); from Mar 2020 a separate 'charts and tables: Annex A' xlsx; Nov 2022 a single charts-and-tables xlsx |
| Mar 2024 - Nov 2025 | 'detailed forecast tables: economy' | 'detailed forecast tables': receipts, expenditure, aggregates, debt interest | 'detailed forecast tables: policy' plus Annex A charts and tables |

Cumulative costing databases (cover every event): Budget/Policy measures database (first archived as `Budget_measures_database.xls`, 20120817043233; latest vintage Nov 2025 already harvested) and the policy-costings uncertainty ratings database (Mar 2017 onward archived; the first edition, Mar 2015 `Policy-costings-uncertainty-ratings-database-180315.xls`, has only a 302 capture).

## Matrix

Key: **Y** = the as-published file (name linked at or near publication) has a 200 capture. **Y\*** = only a later revision or renamed re-upload is captured, so content equivalence with the as-published file is unknown. **Y?** = captured, but the attribution to this event is inferred. **Y~** = captured, but the sheets were not inspected, so which tables it holds is unknown. **N** = no 200 capture under any name found. **DFT** = detailed forecast tables. A year in brackets is the year of the earliest 200 capture when it is well after publication. UKGWA is unknown for every row (see access status).

| # | Event | EFO date | EFO PDF | Economy tables | Receipts tables | Expenditure / welfare tables | Policy tables | Note |
|---|---|---|---|---|---|---|---|---|
| 1 | Budget 2010 #2 | 2010-06-22 | Y | Y~ (one 'Budget forecast tables' xls; sheets not inspected) | Y~ (same workbook) | Y~ (same workbook) | in PDF (annex not inspected); later-linked 'June 2010 Supplementary tables' N | OBR doc is 'Budget forecast - June 2010' (file junebudget_annexc.pdf); a separate pre-Budget forecast (14 Jun 2010) is not a costed event |
| 2 | Autumn 2010 | 2010-11-29 | Y | Y (as-published 291110; verified) | Y (fiscal supp. tables 1.1-1.3; verified) | Y (table 1.4 social security; verified) | charts&tables Y (25 Jan 2011 file) | obr.uk later linked a 21 Feb 2011 re-save of the economy tables |
| 3 | Budget 2011 | 2011-03-23 | Y | Y* (20 Apr 2011 revision only) | N | N | charts&tables Y | as-published obr_economy_supplementary_tables.xls, obr_fiscal_supplementary_tables.xls and obr_fiscal_supplementary_tables1.xls never captured 200 |
| 4 | Autumn 2011 | 2011-11-29 | Y | Y | Y | Y | charts&tables Y |  |
| 5 | Budget 2012 | 2012-03-21 | Y | Y | Y | Y | charts&tables Y | first Budget measures database archived Aug 2012 |
| 6 | Autumn 2012 | 2012-12-05 | Y | Y | Y* (tables5, Feb 2013; as-published ...12112.xls N) | Y* (same file) | charts&tables Y |  |
| 7 | Budget 2013 | 2013-03-20 | Y | Y | Y* (renamed re-upload, Aug 2013 capture) | Y* (same file) | charts&tables Y* (May 2013) | as-published fiscal (...56745354.xls) and charts (...134123.xls) never captured 200 |
| 8 | Autumn 2013 | 2013-12-05 | Y | N | Y* (Tables2, first captured 2021) | Y* (same file) | charts&tables Y* (Tables2, 2022) | economy tables (-amended / Tables1) never captured 200 |
| 9 | Budget 2014 | 2014-03-19 | Y | Y | Y | Y | charts&tables Y | Budget measures database BUD14 archived |
| 10 | Autumn 2014 | 2014-12-03 | Y | Y | Y (first captured 2022) | Y (same file) | charts&tables Y (2022) | file names match the Jan 2015 page |
| 11 | Budget 2015 | 2015-03-18 | Y | Y* (renamed; 2021) | Y* (v3, last modified 2015-05-13; 2021) | Y* (same file) | charts&tables Y (as-published _03-18) | first uncertainty-ratings db (180315) N |
| 12 | Budget 2015 #2 | 2015-07-08 | Y | Y? (Economy_Supplementary_Tables-2015.xls; July attribution inferred) | Y* (-20151.xls, linked 28 Jul 2015) | Y* (same file) | charts&tables Y (2021) | as-published -3242.xlsx / -6444.xls N |
| 13 | Autumn 2015 | 2015-11-25 | Y | Y | Y | Y | charts&tables Y; tax-credits costings PDF Y |  |
| 14 | Budget 2016 | 2016-03-16 | Y | Y (2021) | Y | Y | charts&tables Y; Annex A PDF Y |  |
| 15 | Autumn 2016 | 2016-11-23 | Y | Y | Y (receipts&other) | Y (expenditure) | charts&tables Y (Annex A TA.1-TA.3 verified); Annex A PDF Y | first year receipts/expenditure split |
| 16 | Budget 2017 | 2017-03-08 | Y | Y | Y | Y (2.21 welfare post-measures; verified) | charts&tables Y; Annex A PDF Y; PMD+uncertainty db Y |  |
| 17 | Autumn Budget 2017 | 2017-11-22 | Y | Y (2023 / slug 2021) | Y | Y (2023) | charts&tables Y; PMD+uncertainty db Y |  |
| 18 | Spring Statement 2018 | 2018-03-13 | Y | Y* ('Updated_' file; 2019) | Y | Y (2019) | charts&tables v2 Y (2019) |  |
| 19 | Budget 2018 | 2018-10-29 | Y | Y (slug 2021; -3 file 2019) | Y (2020) | Y (2019) | charts&tables Y (slug 2021) | uncertainty db Y |
| 20 | Spring Statement 2019 | 2019-03-13 | Y | Y | Y | Y | charts&tables Y; PMD+uncertainty db Y |  |
| 21 | Budget 2020 | 2020-03-11 | Y | Y | Y | Y (v4) | Annex A xlsx Y |  |
| 22 | Spending Review 2020 | 2020-11-25 | Y | Y (slug Apr 2021) | Y (slug Apr 2021) | Y (Jan 2021) | Annex A xlsx Y (2022); zip Y (Mar 2021) | files labelled 'AB20' |
| 23 | Spring Budget 2021 | 2021-03-03 | Y | Y (slug 3 Mar 2021) | Y (slug 3 Mar 2021) | Y (slug 3 Mar 2021) | Annex A xlsx Y (slug 3 Mar 2021) | separate OBR costing notes (CJRS, CT rate, fuel duty, ...) archived |
| 24 | Autumn Budget 2021 | 2021-10-27 | Y (slug 27 Oct 2021) | Y (slug Nov 2021) | Y (slug Nov 2021) | Y (slug Nov 2021) | Annex A xlsx Y (slug 4 Nov 2021) | named /docs/ files first captured 2022; slug URLs captured earlier |
| 25 | Spring Statement 2022 | 2022-03-23 | Y | Y | Y | Y | Annex A xlsx Y | all captured on publication day |
| 26 | Autumn Statement 2022 | 2022-11-17 | Y | Y | Y | Y | single charts&tables xlsx Y | v2/v3 revisions added Dec 2022 |
| 27 | Spring Budget 2023 | 2023-03-15 | Y | Y | Y | Y | Annex A xlsx Y | all captured on publication day |
| 28 | Autumn Statement 2023 | 2023-11-22 | Y | Y | Y | Y | Annex A xlsx Y | all captured on publication day |
| 29 | Spring Budget 2024 | 2024-03-06 | Y | Y (DFT) | Y (DFT) | Y (DFT) | DFT policy Y; Annex A Y | first 'detailed forecast tables' (incl. aggregates, debt interest, policy) |
| 30 | Autumn Budget 2024 | 2024-10-30 | Y | Y (DFT) | Y (DFT) | Y (DFT) | DFT policy Y; Annex A Y |  |
| 31 | Spring Statement 2025 | 2025-03-26 | Y | Y (DFT) | Y (DFT) | Y (DFT) | DFT policy Y; Annex A Y |  |
| 32 | Autumn Budget 2025 | 2025-11-26 | Y | Y (DFT) | Y (DFT) | Y (DFT) | DFT policy: only inside later zip (-1.zip, captured 2026-01-21); Annex A Y | launch-day zip has no policy workbook |

Not archived (no 200 capture anywhere), with the evidence query:

- Budget 2011 supplementary economy (original `obr_economy_supplementary_tables.xls`) and fiscal (`obr_fiscal_supplementary_tables.xls`, `obr_fiscal_supplementary_tables1.xls`) tables. These were linked from the as-published page `https://web.archive.org/web/20110325051917id_/http://budgetresponsibility.independent.gov.uk:80/econ-fiscal-outlook-march.html` as `cdn.budgetresponsibility.independent.gov.uk/...`. The only captures are 301, 302, 404 or 500: `http://web.archive.org/cdx/search/cdx?url=budgetresponsibility.independent.gov.uk&output=json&matchType=domain&fl=timestamp%2Coriginal%2Cstatuscode%2Clength&filter=original%3A.%2A%28obr_fiscal_supp%7Cobr_economy_supp%7CMarch-2011%7Cmarch_2011%7Cmarch2011%7C23032011%29.%2A&collapse=urlkey` (with the same query on `budgetresponsibility.org.uk` and `obr.uk`). The obr.uk download slugs `march-2011-economic-and-fiscal-outlook-supplementary-{economy-table,fiscal-tables}` have no captures: `http://web.archive.org/cdx/search/cdx?url=obr.uk%2Fdownload%2Fmarch-2011-economic-and-fiscal-outlook-supplementary-fiscal-tables%2F&output=json&matchType=prefix&fl=timestamp%2Coriginal%2Cstatuscode%2Clength&limit=200`.
- As-published 2012-2015 names that have only `/pubs/` 302 captures: Dec 2012 fiscal `...fiscal-supplementary-tables12112.xls`; Mar 2013 fiscal `...-56745354.xls` and charts `...-134123.xls`; Dec 2013 economy (`...-amended.xls`, `...Tables1.xls`), fiscal and charts (`...Tables.xls`, `...Tables1.xls`); Mar 2015 `150318-Economy_...xls` and `150318_Fiscal_...xls`; Jul 2015 `Economy_Supplementary_Tables-2015-3242.xlsx` and `Fiscal_Supplementary_Tables-2015-6444.xls`. Evidence: `http://web.archive.org/cdx/search/cdx?url=budgetresponsibility.org.uk&output=json&matchType=domain&fl=timestamp%2Coriginal%2Cstatuscode%2Cmimetype&filter=original%3A.%2A%2856745354%7C134123%7CTables-amended%7CDecember-2013-EFO-Charts-and-Tables1%7CDecember-2013-EFO-Fiscal-Supplementary-Tables%5C.xls%7C150318%7C180315%7C2015-3242%7C2015-6444%7CDecember-2013-EFO-Economy%29.%2A&collapse=urlkey` (same on `obr.uk` and `budgetresponsibility.independent.gov.uk`), plus absence from the domain-wide 200 listings above. The replay `https://web.archive.org/web/20131215055707id_/http://budgetresponsibility.org.uk:80/pubs/March-2013-EFO-fiscal-supplementary-tables-56745354.xls` redirects to a download-monitor URL that Wayback answers with 404.
- June 2010 'Supplementary tables' (`June-2010-Supplementary-Tables.xls`, linked only from the later site; the 2010 publications page does not list it): `http://web.archive.org/cdx/search/cdx?url=budgetresponsibility.org.uk%2Fdocs%2Fdlm_uploads%2FJune-2010-Supplementary-Tables.xls&output=json&matchType=exact&fl=timestamp%2Coriginal%2Cstatuscode%2Clength&limit=30` returned `[]`, and so did the `obr.uk/docs/dlm_uploads/` equivalent.
- Autumn Budget 2025 standalone policy workbook: exact queries for `obr.uk/docs/dlm_uploads/Policy_detailed_forecast_tables_November_2025_.xlsx` (and variants) returned `[]`, and so did the slug `http://web.archive.org/cdx/search/cdx?url=obr.uk%2Fdownload%2Fnovember-2025-economic-and-fiscal-outlook-detailed-forecast-tables-policy%2F&output=json&matchType=prefix&fl=timestamp%2Coriginal%2Cstatuscode%2Clength&limit=20`. The workbook is a member of the later zip `https://web.archive.org/web/20260121172819id_/https://obr.uk/docs/dlm_uploads/November-2025-Economic-and-fiscal-outlook-%E2%80%93-detailed-forecast-tables-zip-file-1.zip` (central directory read by Range request: `Policy_detailed_forecast_tables_November_2025_.xlsx` plus aggregates, debt interest, economy, expenditure and receipts). The launch-day zip `https://web.archive.org/web/20251126134217id_/https://obr.uk/docs/dlm_uploads/November-2025-Economic-and-fiscal-outlook-%E2%80%93-detailed-forecast-tables-zip-file.zip` has the other five workbooks but no policy workbook. The policy link appears on the page capture `https://web.archive.org/web/20260714135030id_/https://obr.uk/efo/economic-and-fiscal-outlook-november-2025/` but not on the launch-day capture.

## Per-event best URLs

All URLs are Wayback original-bytes replays (earliest 200 capture). Keys: pdf, econ (economy), fisc (combined fiscal), rec (receipts and other), exp (expenditure), agg (aggregates), pol (policy), annexA, ct (charts and tables), zip, db (costing databases), costing (OBR costing notes). Entries marked NOT ARCHIVED are as-published names with no 200 capture.

### 1. Budget 2010 #2 (EFO 2010-06-22)

- EFO page (archived): `https://web.archive.org/web/20180215092317id_/https://obr.uk/efo/budget-2010/`
- EFO PDF: `junebudget_annexc.pdf` -> `https://web.archive.org/web/20101012115830id_/http://budgetresponsibility.independent.gov.uk/d/junebudget_annexc.pdf`
- Budget forecast tables: `junebudget_chapterc_tables.xls` -> `https://web.archive.org/web/20101207205202id_/http://budgetresponsibility.independent.gov.uk:80/d/junebudget_chapterc_tables.xls`
- supplementary material PDF: `junebudget_supplementary_material.pdf` -> `https://web.archive.org/web/20101013024726id_/http://budgetresponsibility.independent.gov.uk/d/junebudget_supplementary_material.pdf`

### 2. Autumn 2010 (EFO 2010-11-29)

- EFO page (archived): `https://web.archive.org/web/20180215085419id_/https://obr.uk/efo/economic-and-fiscal-outlook-november-2010/`
- EFO PDF: `econ_fiscal_outlook_291110.pdf` -> `https://web.archive.org/web/20101130042645id_/http://budgetresponsibility.independent.gov.uk/d/econ_fiscal_outlook_291110.pdf`
- economy: `economy_supplementary_tables_291110.xls` -> `https://web.archive.org/web/20101207100619id_/http://budgetresponsibility.independent.gov.uk:80/d/economy_supplementary_tables_291110.xls`
- economy: `obr_economy_supplementary_tables_210211.xls` -> `https://web.archive.org/web/20110805185151id_/http://budgetresponsibility.independent.gov.uk/wordpress/docs/obr_economy_supplementary_tables_210211.xls`
- fiscal supplementary (receipts + spending): `fiscal_supplementary_tables_291110.xls` -> `https://web.archive.org/web/20101207100759id_/http://budgetresponsibility.independent.gov.uk:80/d/fiscal_supplementary_tables_291110.xls`
- charts and tables: `charts_tables250111.xls` -> `https://web.archive.org/web/20110805184952id_/http://budgetresponsibility.independent.gov.uk/wordpress/docs/charts_tables250111.xls`

### 3. Budget 2011 (EFO 2011-03-23)

- EFO page (archived): `https://web.archive.org/web/20180215085415id_/https://obr.uk/efo/economic-and-fiscal-outlook-march-2011/`
- EFO PDF: `economic_and_fiscal_outlook_23032011.pdf` -> `https://web.archive.org/web/20110805184216id_/http://budgetresponsibility.independent.gov.uk/wordpress/docs/economic_and_fiscal_outlook_23032011.pdf`
- economy: `obr_economy_supplementary_tables new 200411.xls` -> `https://web.archive.org/web/20110805184222id_/http://budgetresponsibility.independent.gov.uk/wordpress/docs/obr_economy_supplementary_tables%20new%20200411.xls`
- charts and tables: `efo_charts_tables_march2011.xls` -> `https://web.archive.org/web/20110805184914id_/http://budgetresponsibility.independent.gov.uk/wordpress/docs/efo_charts_tables_march2011.xls`

### 4. Autumn 2011 (EFO 2011-11-29)

- EFO page (archived): `https://web.archive.org/web/20180215092100id_/https://obr.uk/efo/economic-and-fiscal-outlook-november-2011/`
- EFO PDF: `Autumn2011EFO_web_version138469072346.pdf` -> `https://web.archive.org/web/20111201172827id_/http://cdn.budgetresponsibility.independent.gov.uk/Autumn2011EFO_web_version138469072346.pdf`
- economy: `0011Economy-Supplementary-Tables-AS11.xls` -> `https://web.archive.org/web/20111202210256id_/http://cdn.budgetresponsibility.independent.gov.uk:80/0011Economy-Supplementary-Tables-AS11.xls`
- economy: `Economy-Supplementary-Tables-AS11.xls` -> `https://web.archive.org/web/20120405041834id_/http://budgetresponsibility.independent.gov.uk/wordpress/docs/Economy-Supplementary-Tables-AS11.xls`
- fiscal supplementary (receipts + spending): `Fiscal-Supplementary-Tables-AS11.xls` -> `https://web.archive.org/web/20111202210357id_/http://budgetresponsibility.independent.gov.uk:80/wordpress/docs/Fiscal-Supplementary-Tables-AS11.xls`
- charts and tables: `Autumn-2011-EFO-Charts-Tables129467.xls` -> `https://web.archive.org/web/20111202210321id_/http://cdn.budgetresponsibility.independent.gov.uk:80/Autumn-2011-EFO-Charts-Tables129467.xls`

### 5. Budget 2012 (EFO 2012-03-21)

- EFO page (archived): `https://web.archive.org/web/20180215092321id_/https://obr.uk/efo/economic-and-fiscal-outlook-march-2012/`
- EFO PDF: `March-2012-EFO.pdf` -> `https://web.archive.org/web/20120324040348id_/http://cdn.budgetresponsibility.independent.gov.uk:80/March-2012-EFO.pdf`
- EFO PDF: `March-2012-EFO1.pdf` -> `https://web.archive.org/web/20120328214350id_/http://budgetresponsibility.independent.gov.uk:80/wordpress/docs/March-2012-EFO1.pdf`
- economy: `March-2012-Supplementary-tables-economy.xls` -> `https://web.archive.org/web/20120405040437id_/http://budgetresponsibility.independent.gov.uk/wordpress/docs/March-2012-Supplementary-tables-economy.xls`
- fiscal supplementary (receipts + spending): `March-2012-Fiscal-Supplementary-Tables1.xls` -> `https://web.archive.org/web/20120405041334id_/http://budgetresponsibility.independent.gov.uk/wordpress/docs/March-2012-Fiscal-Supplementary-Tables1.xls`
- charts and tables: `March-2012-EFO-charts-and-tables.xls` -> `https://web.archive.org/web/20120405040412id_/http://budgetresponsibility.independent.gov.uk/wordpress/docs/March-2012-EFO-charts-and-tables.xls`

### 6. Autumn 2012 (EFO 2012-12-05)

- EFO page (archived): `https://web.archive.org/web/20180215092054id_/https://obr.uk/efo/economic-and-fiscal-outlook-december-2012/`
- EFO PDF: `December-2012-Economic-and-fiscal-outlook23423423.pdf` -> `https://web.archive.org/web/20121206053310id_/http://cdn.budgetresponsibility.independent.gov.uk/December-2012-Economic-and-fiscal-outlook23423423.pdf`
- economy: `December-2012-EFO-economy-supplementary-tables2343.xls` -> `https://web.archive.org/web/20130203193056id_/http://budgetresponsibility.independent.gov.uk:80/wordpress/docs/December-2012-EFO-economy-supplementary-tables2343.xls`
- fiscal supplementary (receipts + spending): `December-2012-EFO-fiscal-supplementary-tables12112.xls` -> NOT ARCHIVED
- fiscal supplementary (receipts + spending): `December-2012-EFO-fiscal-supplementary-tables5.xls` -> `https://web.archive.org/web/20130203193100id_/http://budgetresponsibility.independent.gov.uk:80/wordpress/docs/December-2012-EFO-fiscal-supplementary-tables5.xls`
- fiscal supplementary (receipts + spending): `Copy-of-December-2012-EFO-fiscal-supplementary-tables4.xls` -> `https://web.archive.org/web/20130402083746id_/http://budgetresponsibility.independent.gov.uk:80/wordpress/docs/Copy-of-December-2012-EFO-fiscal-supplementary-tables4.xls`
- charts and tables: `December-2012-EFO-charts-and-tables2342.xls` -> `https://web.archive.org/web/20121224053508id_/http://cdn.budgetresponsibility.independent.gov.uk:80/December-2012-EFO-charts-and-tables2342.xls`

### 7. Budget 2013 (EFO 2013-03-20)

- EFO page (archived): `https://web.archive.org/web/20180215092156id_/https://obr.uk/efo/economic-and-fiscal-outlook-march-2013/`
- EFO PDF: `March-2013-EFO-44734674673453.pdf` -> `https://web.archive.org/web/20130401043723id_/http://cdn.budgetresponsibility.independent.gov.uk:80/March-2013-EFO-44734674673453.pdf`
- economy: `March-2013-EFO-economy-supplementary-tables-453246.xls` -> `https://web.archive.org/web/20130531053307id_/http://budgetresponsibility.independent.gov.uk:80/wordpress/docs/March-2013-EFO-economy-supplementary-tables-453246.xls`
- fiscal supplementary (receipts + spending): `March-2013-EFO-fiscal-supplementary-tables-56745354.xls` -> NOT ARCHIVED
- fiscal supplementary (receipts + spending): `Economic-and-fiscal-outlook-supplementary-fiscal-tables-March-2013.xls` -> `https://web.archive.org/web/20130805073824id_/http://budgetresponsibility.independent.gov.uk:80/wordpress/docs/Economic-and-fiscal-outlook-supplementary-fiscal-tables-March-2013.xls`
- charts and tables: `March-2013-EFO-charts-and-tables-134123.xls` -> NOT ARCHIVED
- charts and tables: `March-2013-EFO-charts-and-tables.xls` -> `https://web.archive.org/web/20130531042958id_/http://budgetresponsibility.independent.gov.uk:80/wordpress/docs/March-2013-EFO-charts-and-tables.xls`

### 8. Autumn 2013 (EFO 2013-12-05)

- EFO page (archived): `https://web.archive.org/web/20180215092111id_/https://obr.uk/efo/economic-fiscal-outlook-december-2013/`
- EFO PDF: `Economic-and-fiscal-outlook-December-2013.pdf` -> `https://web.archive.org/web/20131228074907id_/http://cdn.budgetresponsibility.independent.gov.uk:80/Economic-and-fiscal-outlook-December-2013.pdf`
- economy: `December-2013-EFO-Economy-Supplementary-Tables-amended.xls` -> NOT ARCHIVED
- economy: `December-2013-EFO-Economy-Supplementary-Tables1.xls` -> NOT ARCHIVED
- fiscal supplementary (receipts + spending): `December-2013-EFO-Fiscal-Supplementary-Tables.xls` -> NOT ARCHIVED
- fiscal supplementary (receipts + spending): `December-2013-EFO-Fiscal-Supplementary-Tables2.xls` -> `https://web.archive.org/web/20210723154603id_/https://obr.uk/docs/dlm_uploads/December-2013-EFO-Fiscal-Supplementary-Tables2.xls`
- charts and tables: `December-2013-EFO-Charts-and-Tables1.xls` -> NOT ARCHIVED
- charts and tables: `December-2013-EFO-Charts-and-Tables2.xls` -> `https://web.archive.org/web/20220627052846id_/https://obr.uk//docs/dlm_uploads/December-2013-EFO-Charts-and-Tables2.xls`

### 9. Budget 2014 (EFO 2014-03-19)

- EFO page (archived): `https://web.archive.org/web/20180215092115id_/https://obr.uk/efo/economic-fiscal-outlook-march-2014/`
- EFO PDF: `37839-OBR-Cm-8820-accessible-web-v2.pdf` -> `https://web.archive.org/web/20140319163752id_/http://cdn.budgetresponsibility.org.uk/37839-OBR-Cm-8820-accessible-web-v2.pdf`
- economy: `March_2014_EFO_Economy_Supplementary_Tables.xls` -> `https://web.archive.org/web/20140505143637id_/http://budgetresponsibility.org.uk/wordpress/docs/March_2014_EFO_Economy_Supplementary_Tables.xls`
- fiscal supplementary (receipts + spending): `83723-March_2014_EFO_Fiscal_Supplementary_Tables.xls` -> `https://web.archive.org/web/20140505164333id_/http://cdn.budgetresponsibility.org.uk/83723-March_2014_EFO_Fiscal_Supplementary_Tables.xls`
- charts and tables: `March_2014_EFO_Charts_and_Tables.xls` -> `https://web.archive.org/web/20140505143535id_/http://budgetresponsibility.org.uk/wordpress/docs/March_2014_EFO_Charts_and_Tables.xls`

### 10. Autumn 2014 (EFO 2014-12-03)

- EFO page (archived): `https://web.archive.org/web/20180215085425id_/https://obr.uk/efo/economic-fiscal-outlook-december-2014/`
- EFO PDF: `December_2014_EFO-web513.pdf` -> `https://web.archive.org/web/20141203181155id_/http://cdn.budgetresponsibility.independent.gov.uk/December_2014_EFO-web513.pdf`
- economy: `Economy_Supplementary_Tables_Dec2014.v2.xls` -> `https://web.archive.org/web/20150812170156id_/http://budgetresponsibility.org.uk/wordpress/docs/Economy_Supplementary_Tables_Dec2014.v2.xls`
- fiscal supplementary (receipts + spending): `Fiscal_Supplementary_Tables_Dec_2014.v2.xls` -> `https://web.archive.org/web/20220516091644id_/https://obr.uk//docs/dlm_uploads/Fiscal_Supplementary_Tables_Dec_2014.v2.xls`
- charts and tables: `December_2014_Charts_and_tables-web516.xls` -> `https://web.archive.org/web/20220516074152id_/https://obr.uk//docs/dlm_uploads/December_2014_Charts_and_tables-web516.xls`

### 11. Budget 2015 (EFO 2015-03-18)

- EFO page (archived): `https://web.archive.org/web/20190511210240id_/https://obr.uk/efo/economic-fiscal-outlook-march-2015/`
- EFO PDF: `March2015EFO_18-03-webv1.pdf` -> `https://web.archive.org/web/20150405023303id_/http://cdn.budgetresponsibility.independent.gov.uk:80/March2015EFO_18-03-webv1.pdf`
- economy: `150318-Economy_Supplementary_Tables_March_2015.xls` -> NOT ARCHIVED
- economy: `Economy_Supplementary_Tables_March_2015.xls` -> `https://web.archive.org/web/20211016173743id_/https://obr.uk/docs/dlm_uploads/Economy_Supplementary_Tables_March_2015.xls`
- fiscal supplementary (receipts + spending): `150318_Fiscal_Supplementary_Tables_March_2015.xls` -> NOT ARCHIVED
- fiscal supplementary (receipts + spending): `Fiscal_Supplementary_Tables-2015.v3.xlsx` -> `https://web.archive.org/web/20211016175056id_/https://obr.uk/docs/dlm_uploads/Fiscal_Supplementary_Tables-2015.v3.xlsx`
- charts and tables: `Charts-and-Tables-March-2015-Economic-and-fiscal-outlook_03-18.xls` -> `https://web.archive.org/web/20160529050818id_/http://budgetresponsibility.org.uk/docs/dlm_uploads/Charts-and-Tables-March-2015-Economic-and-fiscal-outlook_03-18.xls`
- charts and tables: `Charts-and-Tables-March-2015-Economic-and-fiscal-outlook.xls` -> `https://web.archive.org/web/20170711155753id_/http://budgetresponsibility.org.uk/docs/dlm_uploads/Charts-and-Tables-March-2015-Economic-and-fiscal-outlook.xls`

### 12. Budget 2015 #2 (EFO 2015-07-08)

- EFO page (archived): `https://web.archive.org/web/20180215085429id_/https://obr.uk/efo/economic-fiscal-outlook-july-2015/`
- EFO PDF: `July-2015-EFO-234224.pdf` -> `https://web.archive.org/web/20150714183906id_/http://cdn.budgetresponsibility.independent.gov.uk:80/July-2015-EFO-234224.pdf`
- economy: `Economy_Supplementary_Tables-2015-3242.xlsx` -> NOT ARCHIVED
- economy: `Economy_Supplementary_Tables-2015.xls` -> `https://web.archive.org/web/20210723161619id_/https://obr.uk/docs/dlm_uploads/Economy_Supplementary_Tables-2015.xls`
- fiscal supplementary (receipts + spending): `Fiscal_Supplementary_Tables-2015-6444.xls` -> NOT ARCHIVED
- fiscal supplementary (receipts + spending): `Fiscal_Supplementary_Tables-20151.xls` -> `https://web.archive.org/web/20180717145605id_/http://obr.uk/docs/dlm_uploads/Fiscal_Supplementary_Tables-20151.xls`
- charts and tables: `July-2015-Charts-and-tables.xls` -> `https://web.archive.org/web/20211130024040id_/https://obr.uk/docs/dlm_uploads/July-2015-Charts-and-tables.xls`

### 13. Autumn 2015 (EFO 2015-11-25)

- EFO page (archived): `https://web.archive.org/web/20180215092105id_/https://obr.uk/efo/economic-and-fiscal-outlook-november-2015/`
- EFO PDF: `EFO_November__2015.pdf` -> `https://web.archive.org/web/20151126073529id_/http://cdn.budgetresponsibility.independent.gov.uk/EFO_November__2015.pdf`
- economy: `Economy_Supplementary_Tables__November___2015.xls` -> `https://web.archive.org/web/20200105093526id_/https://obr.uk/docs/dlm_uploads/Economy_Supplementary_Tables__November___2015.xls`
- economy: `Economy_Supplementary_Tables_November_2015.xls` -> `https://web.archive.org/web/20211130022957id_/https://obr.uk/docs/dlm_uploads/Economy_Supplementary_Tables_November_2015.xls`
- fiscal supplementary (receipts + spending): `Fiscal_Supplementary_Tables_November_2015.xls` -> `https://web.archive.org/web/20160425124728id_/http://budgetresponsibility.org.uk/docs/dlm_uploads/Fiscal_Supplementary_Tables_November_2015.xls`
- charts and tables: `Charts_and_tables__November___2015.xls` -> `https://web.archive.org/web/20160425064655id_/http://budgetresponsibility.org.uk/docs/dlm_uploads/Charts_and_tables__November___2015.xls`
- costing notes: `Tax-credits-costings_November2015.pdf` -> `https://web.archive.org/web/20200130045445id_/https://obr.uk/docs/dlm_uploads/Tax-credits-costings_November2015.pdf`

### 14. Budget 2016 (EFO 2016-03-16)

- EFO page (archived): `https://web.archive.org/web/20180414004514id_/https://obr.uk/efo/economic-fiscal-outlook-march-2016/`
- EFO PDF: `March2016EFO.pdf` -> `https://web.archive.org/web/20160318025347id_/http://cdn.budgetresponsibility.org.uk/March2016EFO.pdf`
- EFO PDF: `AnnexA_March2016EFO.pdf` -> `https://web.archive.org/web/20230608020433id_/https://obr.uk/docs/dlm_uploads/AnnexA_March2016EFO.pdf`
- economy: `Economy_supplementary_tables_March_2016-4.xlsx` -> `https://web.archive.org/web/20210525002827id_/https://obr.uk/docs/dlm_uploads/Economy_supplementary_tables_March_2016-4.xlsx`
- fiscal supplementary (receipts + spending): `Fiscal_supplementary_tables_March_2016-1.xls` -> `https://web.archive.org/web/20160409143918id_/http://budgetresponsibility.org.uk:80/docs/dlm_uploads/Fiscal_supplementary_tables_March_2016-1.xls`
- fiscal supplementary (receipts + spending): `Fiscal_supplementary_tables_March_2016.xls` -> `https://web.archive.org/web/20220209173159id_/http://obr.uk/docs/dlm_uploads/Fiscal_supplementary_tables_March_2016.xls`
- charts and tables: `Charts_and_tables_March_2016-1.xls` -> `https://web.archive.org/web/20160323194707id_/http://budgetresponsibility.org.uk:80/docs/dlm_uploads/Charts_and_tables_March_2016-1.xls`
- charts and tables: `Charts_and_tables_March_2016-2.xls` -> `https://web.archive.org/web/20160624105843id_/http://budgetresponsibility.org.uk/docs/dlm_uploads/Charts_and_tables_March_2016-2.xls`

### 15. Autumn 2016 (EFO 2016-11-23)

- EFO page (archived): `https://web.archive.org/web/20180124173918id_/https://obr.uk/efo/economic-and-fiscal-outlook-november-2016/`
- EFO PDF: `Nov2016EFO.pdf` -> `https://web.archive.org/web/20161129034441id_/http://cdn.budgetresponsibility.org.uk/Nov2016EFO.pdf`
- EFO PDF: `AnnexA_Nov2016EFO.pdf` -> `https://web.archive.org/web/20190723140721id_/https://cdn.obr.uk/AnnexA_Nov2016EFO.pdf`
- economy: `Supplementary_Economy_Tables-1.xlsx` -> `https://web.archive.org/web/20170302110012id_/http://cdn.budgetresponsibility.org.uk/Supplementary_Economy_Tables-1.xlsx`
- receipts and other: `Supplementary_Tables_Receipts_Fiscal-4.xlsx` -> `https://web.archive.org/web/20170302230855id_/http://budgetresponsibility.org.uk/docs/dlm_uploads/Supplementary_Tables_Receipts_Fiscal-4.xlsx`
- expenditure (incl. welfare): `Fiscal_Supplementary_Tables_Expenditure-1412.xlsx` -> `https://web.archive.org/web/20170302144129id_/http://budgetresponsibility.org.uk/docs/dlm_uploads/Fiscal_Supplementary_Tables_Expenditure-1412.xlsx`
- charts and tables: `Exec_Summary_-to_Chapter3_Charts_and_tables.xlsx` -> `https://web.archive.org/web/20170302152229id_/http://cdn.budgetresponsibility.org.uk/Exec_Summary_-to_Chapter3_Charts_and_tables.xlsx`
- charts and tables: `Chapter4_to_annexC_Charts_and_tables.xlsx` -> `https://web.archive.org/web/20170302152119id_/http://budgetresponsibility.org.uk/docs/dlm_uploads/Chapter4_to_annexC_Charts_and_tables.xlsx`

### 16. Budget 2017 (EFO 2017-03-08)

- EFO page (archived): `https://web.archive.org/web/20180129010308id_/https://obr.uk/efo/economic-fiscal-outlook-march-2017/`
- EFO PDF: `March2017EFO-231.pdf` -> `https://web.archive.org/web/20170308190255id_/http://cdn.budgetresponsibility.org.uk/March2017EFO-231.pdf`
- EFO PDF: `AnnexA_March2017EFO.pdf` -> `https://web.archive.org/web/20170706055706id_/http://cdn.budgetresponsibility.org.uk/AnnexA_March2017EFO.pdf`
- economy: `SupplementaryEconomytablesMarch2017-2.xlsx` -> `https://web.archive.org/web/20170711143340id_/http://cdn.budgetresponsibility.org.uk/SupplementaryEconomytablesMarch2017-2.xlsx`
- economy: `SupplementaryEconomytablesMarch2017.xlsx` -> `https://web.archive.org/web/20170930053529id_/http://budgetresponsibility.org.uk:80/docs/dlm_uploads/SupplementaryEconomytablesMarch2017.xlsx`
- receipts and other: `Fiscal_Supplementary_Tables_Receiptsother_March_2017-1.xlsx` -> `https://web.archive.org/web/20171013095554id_/http://cdn.budgetresponsibility.org.uk:80/Fiscal_Supplementary_Tables_Receiptsother_March_2017-1.xlsx`
- expenditure (incl. welfare): `Fiscal_Supplementary_Tables_Expenditure_March_2017-4.xlsx` -> `https://web.archive.org/web/20171013094653id_/http://budgetresponsibility.org.uk:80/docs/dlm_uploads/Fiscal_Supplementary_Tables_Expenditure_March_2017-4.xlsx`
- charts and tables: `March-2017-EFO-charts-and-tables-fiscal-1.xlsx` -> `https://web.archive.org/web/20170427085224id_/http://budgetresponsibility.org.uk/docs/dlm_uploads/March-2017-EFO-charts-and-tables-fiscal-1.xlsx`
- charts and tables: `March-2017-EFO-charts-and-tables-economy-1.xlsx` -> `https://web.archive.org/web/20170427074840id_/http://cdn.budgetresponsibility.org.uk/March-2017-EFO-charts-and-tables-economy-1.xlsx`
- costing databases: `Policy_measures_database_March_2017-1.xlsx` -> `https://web.archive.org/web/20170607051507id_/http://budgetresponsibility.org.uk:80/docs/dlm_uploads/Policy_measures_database_March_2017-1.xlsx`
- costing databases: `Policy_costings_uncertainty_ratings_database_March_2017.xlsx` -> `https://web.archive.org/web/20170706081226id_/http://cdn.budgetresponsibility.org.uk/Policy_costings_uncertainty_ratings_database_March_2017.xlsx`

### 17. Autumn Budget 2017 (EFO 2017-11-22)

- EFO page (archived): `https://web.archive.org/web/20180122142420id_/https://obr.uk/efo/economic-fiscal-outlook-november-2017/`
- EFO PDF: `Nov2017EFOwebversion-2.pdf` -> `https://web.archive.org/web/20171123012224id_/http://cdn.budgetresponsibility.org.uk/Nov2017EFOwebversion-2.pdf`
- EFO PDF: `Nov2017EFOwebversion.pdf` -> `https://web.archive.org/web/20180202042050id_/http://obr.uk/docs/dlm_uploads/Nov2017EFOwebversion.pdf`
- economy: `November_2017_EFO_Supplementary_economy_tables-1.xlsx` -> `https://web.archive.org/web/20230129124833id_/https://obr.uk/docs/dlm_uploads/November_2017_EFO_Supplementary_economy_tables-1.xlsx`
- receipts and other: `November_2017_EFO_Supplementary_receipts_other-1.xlsx` -> `https://web.archive.org/web/20171207095755id_/http://budgetresponsibility.org.uk/docs/dlm_uploads/November_2017_EFO_Supplementary_receipts_other-1.xlsx`
- expenditure (incl. welfare): `November_2017_EFO_Supplementary_fiscal_tables_expenditure-2.xlsx` -> `https://web.archive.org/web/20230129124343id_/https://obr.uk/docs/dlm_uploads/November_2017_EFO_Supplementary_fiscal_tables_expenditure-2.xlsx`
- charts and tables: `November_2017_EFO_Fiscal_charts_and_tables-1.xlsx` -> `https://web.archive.org/web/20171207004855id_/http://cdn.budgetresponsibility.org.uk:80/November_2017_EFO_Fiscal_charts_and_tables-1.xlsx`
- charts and tables: `November_2017_EFO_Economy_charts_and_tables.xlsx` -> `https://web.archive.org/web/20220627061254id_/https://obr.uk//docs/dlm_uploads/November_2017_EFO_Economy_charts_and_tables.xlsx`
- costing databases: `November_2017_EFO_Policy_measures_database.xlsx` -> `https://web.archive.org/web/20180406080635id_/http://obr.uk:80/docs/dlm_uploads/November_2017_EFO_Policy_measures_database.xlsx`
- costing databases: `November_2017_EFO_Uncertainty_ratings_database.xlsx` -> `https://web.archive.org/web/20171122204345id_/http://budgetresponsibility.org.uk:80/docs/dlm_uploads/November_2017_EFO_Uncertainty_ratings_database.xlsx`

### 18. Spring Statement 2018 (EFO 2018-03-13)

- EFO page (archived): `https://web.archive.org/web/20180313211245id_/https://obr.uk/efo/economic-fiscal-outlook-march-2018/`
- EFO PDF: `EFO-MaRch_2018.pdf` -> `https://web.archive.org/web/20180314023901id_/http://cdn.obr.uk/EFO-MaRch_2018.pdf`
- economy: `Updated_Economy_Supplementary_Tables_March_2018_EFO.xlsx` -> `https://web.archive.org/web/20190323232403id_/https://obr.uk/docs/dlm_uploads/Updated_Economy_Supplementary_Tables_March_2018_EFO.xlsx`
- receipts and other: `Fiscal_Supplementary_Tables_Receiptsother_March_2018_EFO-1.xlsx` -> `https://web.archive.org/web/20180406080156id_/http://cdn.obr.uk:80/Fiscal_Supplementary_Tables_Receiptsother_March_2018_EFO-1.xlsx`
- expenditure (incl. welfare): `Fiscal_Supplementary_Tables_Expenditure_March_2018_EFO-1.xlsx` -> `https://web.archive.org/web/20190323220755id_/https://cdn.obr.uk/Fiscal_Supplementary_Tables_Expenditure_March_2018_EFO-1.xlsx`
- charts and tables: `Charts_and_tables_chapters_1-3_March_2018_EFO-v2.xlsx` -> `https://web.archive.org/web/20190324025139id_/https://cdn.obr.uk/Charts_and_tables_chapters_1-3_March_2018_EFO-v2.xlsx`
- charts and tables: `Charts_and_tables_chapters_4-B_March_2018_EFO-v2.xlsx` -> `https://web.archive.org/web/20190324025052id_/https://cdn.obr.uk/Charts_and_tables_chapters_4-B_March_2018_EFO-v2.xlsx`

### 19. Budget 2018 (EFO 2018-10-29)

- EFO page (archived): `https://web.archive.org/web/20181128102601id_/https://obr.uk/efo/economic-fiscal-outlook-october-2018/`
- EFO PDF: `EFO_October-2018.pdf` -> `https://web.archive.org/web/20181103132906id_/https://cdn.obr.uk/EFO_October-2018.pdf`
- economy: `Supplementary_economy_tables_October_2018-3.xlsx` -> `https://web.archive.org/web/20191023140751id_/https://obr.uk/docs/dlm_uploads/Supplementary_economy_tables_October_2018-3.xlsx`
- receipts and other: `Supplementary_fiscal_tables_receipts_other_October_2018.xlsx` -> `https://web.archive.org/web/20200226025542id_/https://obr.uk/docs/dlm_uploads/Supplementary_fiscal_tables_receipts_other_October_2018.xlsx`
- expenditure (incl. welfare): `Supplementary_fiscal_tables_expenditure_October_2018-3.xlsx` -> `https://web.archive.org/web/20190405040714id_/https://cdn.obr.uk/Supplementary_fiscal_tables_expenditure_October_2018-3.xlsx`
- charts and tables: `Fiscal_charts_and_tables_October_2018.xlsx` -> `https://web.archive.org/web/20190723140745id_/https://cdn.obr.uk/Fiscal_charts_and_tables_October_2018.xlsx`
- charts and tables: `Economy_charts_and_tables_October_2018.xlsx` -> `https://web.archive.org/web/20190722233219id_/https://cdn.obr.uk/Economy_charts_and_tables_October_2018.xlsx`
- costing databases: `Uncertainty_ratings_database_October_2018-.xlsx` -> `https://web.archive.org/web/20190207072515id_/https://obr.uk/docs/dlm_uploads/Uncertainty_ratings_database_October_2018-.xlsx`

### 20. Spring Statement 2019 (EFO 2019-03-13)

- EFO page (archived): `https://web.archive.org/web/20190314153504id_/https://obr.uk/efo/economic-fiscal-outlook-march-2019/`
- EFO PDF: `March-2019_EFO_Web-Accessible.pdf` -> `https://web.archive.org/web/20190324101319id_/https://cdn.obr.uk/March-2019_EFO_Web-Accessible.pdf`
- economy: `Economy_supplementary_tables_March_2019.xlsx` -> `https://web.archive.org/web/20190723141118id_/https://obr.uk/docs/dlm_uploads/Economy_supplementary_tables_March_2019.xlsx`
- receipts and other: `Fiscal_supplementary_tables_receipts_and_other_March_2019.xlsx` -> `https://web.archive.org/web/20190723140521id_/https://obr.uk/docs/dlm_uploads/Fiscal_supplementary_tables_receipts_and_other_March_2019.xlsx`
- expenditure (incl. welfare): `Fiscal_Supplementary_Tables_Expenditure_March_2019.xlsx` -> `https://web.archive.org/web/20190723140711id_/https://obr.uk/docs/Fiscal_Supplementary_Tables_Expenditure_March_2019.xlsx`
- charts and tables: `Fiscal_charts_and_tables_March_2019.xlsx` -> `https://web.archive.org/web/20190723140256id_/https://cdn.obr.uk/Fiscal_charts_and_tables_March_2019.xlsx`
- charts and tables: `Economy_charts_and_tables_March_2019.xlsx` -> `https://web.archive.org/web/20190723140700id_/https://cdn.obr.uk/Economy_charts_and_tables_March_2019.xlsx`
- costing databases: `Policy_measures_database_March_2019.xlsx` -> `https://web.archive.org/web/20190524004446id_/https://obr.uk/docs/dlm_uploads/Policy_measures_database_March_2019.xlsx`
- costing databases: `Policy_costings_uncertainty_ratings_database_March_2019.xlsx` -> `https://web.archive.org/web/20190723140425id_/https://obr.uk/docs/dlm_uploads/Policy_costings_uncertainty_ratings_database_March_2019.xlsx`

### 21. Budget 2020 (EFO 2020-03-11)

- EFO page (archived): `https://web.archive.org/web/20200414002611id_/https://obr.uk/efo/economic-and-fiscal-outlook-march-2020/`
- EFO PDF: `EFO_March-2020_Accessible.pdf` -> `https://web.archive.org/web/20200312091900id_/https://cdn.obr.uk/EFO_March-2020_Accessible.pdf`
- economy: `Economy_supplementary_tables_March_2020_EFO.xlsx` -> `https://web.archive.org/web/20200608040056id_/https://cdn.obr.uk/Economy_supplementary_tables_March_2020_EFO.xlsx`
- receipts and other: `Fiscal_Supplementary_Tables_Receipts_March_2020_EFO-1.xlsx` -> `https://web.archive.org/web/20200519103942id_/https://obr.uk/docs/dlm_uploads/Fiscal_Supplementary_Tables_Receipts_March_2020_EFO-1.xlsx`
- expenditure (incl. welfare): `Fiscal_Supplementary_Tables_Expenditure_March_2020_EFOv4.xlsx` -> `https://web.archive.org/web/20200519100548id_/https://obr.uk/docs/Fiscal_Supplementary_Tables_Expenditure_March_2020_EFOv4.xlsx`
- Annex A / policy charts and tables: `Annex_A_Charts_and_tables_EFO_March_2020.xlsx` -> `https://web.archive.org/web/20200608014934id_/https://cdn.obr.uk/Annex_A_Charts_and_tables_EFO_March_2020.xlsx`
- zip: `Supplementary_Tables_March_2020_EFO.zip` -> `https://web.archive.org/web/20230129113622id_/https://obr.uk/docs/dlm_uploads/Supplementary_Tables_March_2020_EFO.zip`

### 22. Spending Review 2020 (EFO 2020-11-25)

- EFO page (archived): `https://web.archive.org/web/20201128143548id_/https://obr.uk/efo/economic-and-fiscal-outlook-november-2020/`
- EFO PDF: `CCS1020397650-001_OBR-November2020-EFO-v2-Web-accessible.pdf` -> `https://web.archive.org/web/20201125132325id_/http://cdn.obr.uk/CCS1020397650-001_OBR-November2020-EFO-v2-Web-accessible.pdf`
- economy: `Economy_Supplementary_Tables_AB20.xlsx` -> `https://web.archive.org/web/20220901000537id_/https://obr.uk//docs/Economy_Supplementary_Tables_AB20.xlsx`
- receipts and other: `Fiscal_Supplementary_Tables_Receiptsother_AB20.xlsx` -> `https://web.archive.org/web/20230608010755id_/https://obr.uk/docs/dlm_uploads/Fiscal_Supplementary_Tables_Receiptsother_AB20.xlsx`
- expenditure (incl. welfare): `Fiscal_Supplementary_Tables_Expenditure_AB20.xlsx` -> `https://web.archive.org/web/20210103210927id_/http://cdn.obr.uk/Fiscal_Supplementary_Tables_Expenditure_AB20.xlsx`
- Annex A / policy charts and tables: `Annex_A_Charts_and_tables_November_2020.xlsx` -> `https://web.archive.org/web/20220815101040id_/https://obr.uk//docs/dlm_uploads/Annex_A_Charts_and_tables_November_2020.xlsx`
- zip: `Charts_and_tables_November_2020.zip` -> `https://web.archive.org/web/20210318120340id_/https://obr.uk/docs/dlm_uploads/Charts_and_tables_November_2020.zip`

### 23. Spring Budget 2021 (EFO 2021-03-03)

- EFO page (archived): `https://web.archive.org/web/20210303132517id_/https://obr.uk/efo/economic-and-fiscal-outlook-march-2021/`
- EFO PDF: `March2021EFOweb.pdf` -> `https://web.archive.org/web/20210303132913id_/https://obr.uk/docs/dlm_uploads/March2021EFOweb.pdf`
- EFO PDF: `CCS207_CCS0221988872-001_CP-387-OBR-EFO-Web-Accessible.pdf` -> `https://web.archive.org/web/20220525093854id_/https://obr.uk/docs/CCS207_CCS0221988872-001_CP-387-OBR-EFO-Web-Accessible.pdf`
- economy: `Economy_supplementary_tables_EFO_March_2021.xlsx` -> `https://web.archive.org/web/20220705185205id_/https://obr.uk//docs/Economy_supplementary_tables_EFO_March_2021.xlsx`
- receipts and other: `Fiscal_Supplementary_Tables_Receiptsother_March_2021.xlsx` -> `https://web.archive.org/web/20220621152751id_/https://obr.uk//docs/Fiscal_Supplementary_Tables_Receiptsother_March_2021.xlsx`
- expenditure (incl. welfare): `Fiscal_Supplementary_Tables_Expenditure_March_2021.xlsx` -> `https://web.archive.org/web/20240723123452id_/https://obr.uk/docs/dlm_uploads/Fiscal_Supplementary_Tables_Expenditure_March_2021.xlsx`
- Annex A / policy charts and tables: `Annex_A_charts_and_tables_March_2021.xlsx` -> `https://web.archive.org/web/20220705190556id_/https://obr.uk//docs/dlm_uploads/Annex_A_charts_and_tables_March_2021.xlsx`
- zip: `EFO_March_2021_Supplementary_tables.zip` -> `https://web.archive.org/web/20230129123015id_/https://obr.uk/docs/dlm_uploads/EFO_March_2021_Supplementary_tables.zip`

### 24. Autumn Budget 2021 (EFO 2021-10-27)

- EFO page (archived): `https://web.archive.org/web/20211027124330id_/https://obr.uk/efo/economic-and-fiscal-outlook-october-2021/`
- EFO PDF: `CCS1021486854-001_OBR-EFO-October-2021_CS_Web-Accessible_v2.pdf` -> `https://web.archive.org/web/20220622231543id_/https://obr.uk//docs/dlm_uploads/CCS1021486854-001_OBR-EFO-October-2021_CS_Web-Accessible_v2.pdf`
- EFO PDF: `CCS1021486854-001_OBR-EFO-October-2021.pdf` -> `https://web.archive.org/web/20221115132454id_/https://obr.uk/docs/dlm_uploads/CCS1021486854-001_OBR-EFO-October-2021.pdf`
- EFO PDF: `Annex_A_Economic_and_fiscal_outlook_October_2021.pdf` -> `https://web.archive.org/web/20250428054108id_/https://obr.uk/docs/Annex_A_Economic_and_fiscal_outlook_October_2021.pdf`
- economy: `Economy_Supplementary_Tables_October_2021.xlsx` -> `https://web.archive.org/web/20220529105416id_/https://obr.uk//docs/Economy_Supplementary_Tables_October_2021.xlsx`
- receipts and other: `Fiscal_Supplementary_Tables_Receiptsother_October_2021.xlsx` -> `https://web.archive.org/web/20220529122054id_/https://obr.uk//docs/Fiscal_Supplementary_Tables_Receiptsother_October_2021.xlsx`
- expenditure (incl. welfare): `Fiscal_Supplementary_Tables_Expenditure_October_2021.xlsx` -> `https://web.archive.org/web/20220529123037id_/https://obr.uk//docs/Fiscal_Supplementary_Tables_Expenditure_October_2021.xlsx`
- Annex A / policy charts and tables: `Annex_A_charts_and_tables_October_2021.xlsx` -> `https://web.archive.org/web/20220705191829id_/https://obr.uk//docs/dlm_uploads/Annex_A_charts_and_tables_October_2021.xlsx`
- zip: `Supplementary_Tables_October_2021.zip` -> `https://web.archive.org/web/20221208033746id_/https://obr.uk/docs/Supplementary_Tables_October_2021.zip`

### 25. Spring Statement 2022 (EFO 2022-03-23)

- EFO page (archived): `https://web.archive.org/web/20220323151027id_/https://obr.uk/efo/economic-and-fiscal-outlook-march-2022/`
- EFO PDF: `CCS0222366764-001_OBR-EFO-March-2022_Web-Accessible-2.pdf` -> `https://web.archive.org/web/20220323164728id_/https://obr.uk/docs/dlm_uploads/CCS0222366764-001_OBR-EFO-March-2022_Web-Accessible-2.pdf`
- economy: `Economy_Supplementary_Tables_March_2022-1.xlsx` -> `https://web.archive.org/web/20220323220804id_/https://obr.uk/docs/dlm_uploads/Economy_Supplementary_Tables_March_2022-1.xlsx`
- receipts and other: `Fiscal_Supplementary_Tables_Receiptsother_March_2022-2.xlsx` -> `https://web.archive.org/web/20220323220807id_/https://obr.uk/docs/dlm_uploads/Fiscal_Supplementary_Tables_Receiptsother_March_2022-2.xlsx`
- expenditure (incl. welfare): `Fiscal_Supplementary_Tables_Expenditure_March_2022.xlsx` -> `https://web.archive.org/web/20220323220800id_/https://obr.uk/docs/dlm_uploads/Fiscal_Supplementary_Tables_Expenditure_March_2022.xlsx`
- Annex A / policy charts and tables: `Annex_A_charts_and_tables_March_2022.xlsx` -> `https://web.archive.org/web/20220323220812id_/https://obr.uk/docs/dlm_uploads/Annex_A_charts_and_tables_March_2022.xlsx`
- zip: `Economic_and_fiscal_outlook_Supplementary_Tables_March_2022.zip` -> `https://web.archive.org/web/20220323220800id_/https://obr.uk/docs/dlm_uploads/Economic_and_fiscal_outlook_Supplementary_Tables_March_2022.zip`

### 26. Autumn Statement 2022 (EFO 2022-11-17)

- EFO page (archived): `https://web.archive.org/web/20221117122632id_/https://obr.uk/efo/economic-and-fiscal-outlook-november-2022/`
- EFO PDF: `CCS0822661240-002_CCS001_SECURE_OBR_EFO_November_2022_BOOKMARK.pdf` -> `https://web.archive.org/web/20221117122526id_/https://obr.uk/docs/dlm_uploads/CCS0822661240-002_CCS001_SECURE_OBR_EFO_November_2022_BOOKMARK.pdf`
- economy: `Economy_supplementary_tables_November_2022.xlsx` -> `https://web.archive.org/web/20221117122504id_/https://obr.uk/docs/dlm_uploads/Economy_supplementary_tables_November_2022.xlsx`
- receipts and other: `Fiscal_supplementary_tables_Receiptsother_November_2022.xlsx` -> `https://web.archive.org/web/20221117122532id_/https://obr.uk/docs/dlm_uploads/Fiscal_supplementary_tables_Receiptsother_November_2022.xlsx`
- expenditure (incl. welfare): `Fiscal_supplementary_tables_expenditure_November_2022.xlsx` -> `https://web.archive.org/web/20221117131030id_/https://obr.uk/docs/dlm_uploads/Fiscal_supplementary_tables_expenditure_November_2022.xlsx`
- Annex A / policy charts and tables: `Economic_and_fiscal_outlook_charts_and_tables_November_2022.xlsx` -> `https://web.archive.org/web/20221117122512id_/https://obr.uk/docs/dlm_uploads/Economic_and_fiscal_outlook_charts_and_tables_November_2022.xlsx`
- zip: `November-2022-Economic-and-fiscal-outlook-–-supplementary-tables.zip` -> `https://web.archive.org/web/20221117122535id_/https://obr.uk/docs/dlm_uploads/November-2022-Economic-and-fiscal-outlook-%E2%80%93-supplementary-tables.zip`

### 27. Spring Budget 2023 (EFO 2023-03-15)

- EFO page (archived): `https://web.archive.org/web/20230315134148id_/https://obr.uk/efo/economic-and-fiscal-outlook-march-2023/`
- EFO PDF: `OBR-EFO-March-2023_Web_Accessible.pdf` -> `https://web.archive.org/web/20230315133841id_/https://obr.uk/docs/dlm_uploads/OBR-EFO-March-2023_Web_Accessible.pdf`
- economy: `Economy_supplementary_tables_March_2023.xlsx` -> `https://web.archive.org/web/20230315133847id_/https://obr.uk/docs/dlm_uploads/Economy_supplementary_tables_March_2023.xlsx`
- receipts and other: `Fiscal_supplementary_tables_receiptsother_March_2023.xlsx` -> `https://web.archive.org/web/20230315133917id_/https://obr.uk/docs/dlm_uploads/Fiscal_supplementary_tables_receiptsother_March_2023.xlsx`
- expenditure (incl. welfare): `Fiscal_supplementary_tables_expenditure_March_2023.xlsx` -> `https://web.archive.org/web/20230315133845id_/https://obr.uk/docs/dlm_uploads/Fiscal_supplementary_tables_expenditure_March_2023.xlsx`
- Annex A / policy charts and tables: `Annex_A_charts_and_tables_March_2023.xlsx` -> `https://web.archive.org/web/20230315133900id_/https://obr.uk/docs/dlm_uploads/Annex_A_charts_and_tables_March_2023.xlsx`
- zip: `March-2023-Economic-and-fiscal-outlook-–-supplementary-tables.zip` -> `https://web.archive.org/web/20230315134120id_/https://obr.uk/docs/dlm_uploads/March-2023-Economic-and-fiscal-outlook-%E2%80%93-supplementary-tables.zip`

### 28. Autumn Statement 2023 (EFO 2023-11-22)

- EFO page (archived): `https://web.archive.org/web/20231122152125id_/https://obr.uk/efo/economic-and-fiscal-outlook-november-2023/`
- EFO PDF: `E03004355_November-Economic-and-Fiscal-Outlook_Web-Accessible.pdf` -> `https://web.archive.org/web/20231122172706id_/https://obr.uk/docs/dlm_uploads/E03004355_November-Economic-and-Fiscal-Outlook_Web-Accessible.pdf`
- economy: `Economy_supplementary_tables_November_2023.xlsx` -> `https://web.archive.org/web/20231122205250id_/https://obr.uk/docs/dlm_uploads/Economy_supplementary_tables_November_2023.xlsx`
- receipts and other: `Fiscal_supplementary_tables_receipts_and_other_November_2023.xlsx` -> `https://web.archive.org/web/20231122203452id_/https://obr.uk/docs/dlm_uploads/Fiscal_supplementary_tables_receipts_and_other_November_2023.xlsx`
- expenditure (incl. welfare): `Fiscal_supplementary_tables_expenditure_November_2023.xlsx` -> `https://web.archive.org/web/20231122220737id_/https://obr.uk/docs/dlm_uploads/Fiscal_supplementary_tables_expenditure_November_2023.xlsx`
- Annex A / policy charts and tables: `Annex_A_charts_and_tables_November_2023.xlsx` -> `https://web.archive.org/web/20231122202322id_/https://obr.uk/docs/dlm_uploads/Annex_A_charts_and_tables_November_2023.xlsx`
- zip: `November 2023 Economic and fiscal outlook – supplementary tables.zip` -> `https://web.archive.org/web/20231122144234id_/https://obr.uk/docs/dlm_uploads/November%202023%20Economic%20and%20fiscal%20outlook%20%E2%80%93%20supplementary%20tables.zip`

### 29. Spring Budget 2024 (EFO 2024-03-06)

- EFO page (archived): `https://web.archive.org/web/20240306134014id_/https://obr.uk/efo/economic-and-fiscal-outlook-march-2024/`
- EFO PDF: `E03057758_OBR_EFO-March-2024_Web-AccessibleFinal.pdf` -> `https://web.archive.org/web/20240306133954id_/https://obr.uk/docs/dlm_uploads/E03057758_OBR_EFO-March-2024_Web-AccessibleFinal.pdf`
- economy: `Detailed_forecast_tables_Economy_March_2024.xlsx` -> `https://web.archive.org/web/20240306134030id_/https://obr.uk/docs/dlm_uploads/Detailed_forecast_tables_Economy_March_2024.xlsx`
- receipts and other: `Detailed_forecast_tables_Receipts_March_2024.xlsx` -> `https://web.archive.org/web/20240306134021id_/https://obr.uk/docs/dlm_uploads/Detailed_forecast_tables_Receipts_March_2024.xlsx`
- expenditure (incl. welfare): `Detailed_forecast_tables_Expenditure_March_2024.xlsx` -> `https://web.archive.org/web/20240306134016id_/https://obr.uk/docs/dlm_uploads/Detailed_forecast_tables_Expenditure_March_2024.xlsx`
- aggregates: `Detailed_forecast_tables_Aggregates_March_2024.xlsx` -> `https://web.archive.org/web/20240306134022id_/https://obr.uk/docs/dlm_uploads/Detailed_forecast_tables_Aggregates_March_2024.xlsx`
- policy (detailed forecast tables): `Detailed_forecast_tables_Policy_March_2024.xlsx` -> `https://web.archive.org/web/20240306134020id_/https://obr.uk/docs/dlm_uploads/Detailed_forecast_tables_Policy_March_2024.xlsx`
- Annex A / policy charts and tables: `Annex_A_charts_and_tables_March_2024.xlsx` -> `https://web.archive.org/web/20240306134023id_/https://obr.uk/docs/dlm_uploads/Annex_A_charts_and_tables_March_2024.xlsx`
- zip: `March-2024-Economic-and-fiscal-outlook-–-detailed-forecast-tables.zip` -> `https://web.archive.org/web/20240306134017id_/https://obr.uk/docs/dlm_uploads/March-2024-Economic-and-fiscal-outlook-%E2%80%93-detailed-forecast-tables.zip`

### 30. Autumn Budget 2024 (EFO 2024-10-30)

- EFO page (archived): `https://web.archive.org/web/20241030171702id_/https://obr.uk/efo/economic-and-fiscal-outlook-october-2024/`
- EFO PDF: `OBR_Economic_and_fiscal_outlook_Oct_2024.pdf` -> `https://web.archive.org/web/20241030142448id_/https://obr.uk/docs/dlm_uploads/OBR_Economic_and_fiscal_outlook_Oct_2024.pdf`
- economy: `Economy_Detailed_forecast_tables_October_2024.xlsx` -> `https://web.archive.org/web/20241030143907id_/https://obr.uk/docs/dlm_uploads/Economy_Detailed_forecast_tables_October_2024.xlsx`
- receipts and other: `Receipts_Detailed_forecast_tables_October_2024.xlsx` -> `https://web.archive.org/web/20241030141049id_/https://obr.uk/docs/dlm_uploads/Receipts_Detailed_forecast_tables_October_2024.xlsx`
- expenditure (incl. welfare): `Expenditure_Detailed_forecast_tables_October_2024.xlsx` -> `https://web.archive.org/web/20241030141317id_/https://obr.uk/docs/dlm_uploads/Expenditure_Detailed_forecast_tables_October_2024.xlsx`
- aggregates: `Aggregates_Detailed_forecast_tables_October_2024.xlsx` -> `https://web.archive.org/web/20241030140852id_/https://obr.uk/docs/dlm_uploads/Aggregates_Detailed_forecast_tables_October_2024.xlsx`
- policy (detailed forecast tables): `Policy_Detailed_forecast_tables_October_2024.xlsx` -> `https://web.archive.org/web/20241030143359id_/https://obr.uk/docs/dlm_uploads/Policy_Detailed_forecast_tables_October_2024.xlsx`
- Annex A / policy charts and tables: `Annex_A_charts_and_tables_October_2024.xlsx` -> `https://web.archive.org/web/20241030142646id_/https://obr.uk/docs/dlm_uploads/Annex_A_charts_and_tables_October_2024.xlsx`
- zip: `October-2024-Economic-and-fiscal-outlook-–-detailed-forecast-tables.zip` -> `https://web.archive.org/web/20241030144026id_/https://obr.uk/docs/dlm_uploads/October-2024-Economic-and-fiscal-outlook-%E2%80%93-detailed-forecast-tables.zip`

### 31. Spring Statement 2025 (EFO 2025-03-26)

- EFO page (archived): `https://web.archive.org/web/20250326132001id_/https://obr.uk/efo/economic-and-fiscal-outlook-march-2025/`
- EFO PDF: `OBR_Economic_and_fiscal_outlook_March_2025.pdf` -> `https://web.archive.org/web/20250326131454id_/https://obr.uk/docs/dlm_uploads/OBR_Economic_and_fiscal_outlook_March_2025.pdf`
- economy: `Economy_Detailed_forecast_tables_March_2025.xlsx` -> `https://web.archive.org/web/20250326135827id_/https://obr.uk/docs/dlm_uploads/Economy_Detailed_forecast_tables_March_2025.xlsx`
- receipts and other: `Receipts_Detailed_forecast_tables_March_2025.xlsx` -> `https://web.archive.org/web/20250326161954id_/https://obr.uk/docs/dlm_uploads/Receipts_Detailed_forecast_tables_March_2025.xlsx`
- expenditure (incl. welfare): `Expenditure_Detailed_forecast_tables_March_2025.xlsx` -> `https://web.archive.org/web/20250326152855id_/https://obr.uk/docs/dlm_uploads/Expenditure_Detailed_forecast_tables_March_2025.xlsx`
- aggregates: `Aggregates_Detailed_forecast_tables_March_2025.xlsx` -> `https://web.archive.org/web/20250326142503id_/https://obr.uk/docs/dlm_uploads/Aggregates_Detailed_forecast_tables_March_2025.xlsx`
- policy (detailed forecast tables): `Policy_Detailed_forecast_tables_March_2025.xlsx` -> `https://web.archive.org/web/20250326141251id_/https://obr.uk/docs/dlm_uploads/Policy_Detailed_forecast_tables_March_2025.xlsx`
- Annex A / policy charts and tables: `Annex_A_charts_and_tables_March_2025.xlsx` -> `https://web.archive.org/web/20250326143650id_/https://obr.uk/docs/dlm_uploads/Annex_A_charts_and_tables_March_2025.xlsx`
- zip: `March-2025-Economic-and-fiscal-outlook-–-detailed-forecast-tables-zip-file.zip` -> `https://web.archive.org/web/20250326135544id_/https://obr.uk/docs/dlm_uploads/March-2025-Economic-and-fiscal-outlook-%E2%80%93-detailed-forecast-tables-zip-file.zip`

### 32. Autumn Budget 2025 (EFO 2025-11-26)

- EFO page (archived): `https://web.archive.org/web/20251126134217id_/https://obr.uk/efo/economic-and-fiscal-outlook-november-2025/`
- EFO PDF: `OBR_Economic_and_fiscal_outlook_November_2025-8364713188.pdf` -> `https://web.archive.org/web/20251126134317id_/https://obr.uk/docs/dlm_uploads/OBR_Economic_and_fiscal_outlook_November_2025-8364713188.pdf`
- EFO PDF: `OBR_Economic_and_fiscal_outlook_November_2025.pdf` -> `https://web.archive.org/web/20251126115825id_/https://obr.uk/docs/dlm_uploads/OBR_Economic_and_fiscal_outlook_November_2025.pdf`
- economy: `Economy_Detailed_forecast_tables_November_2025.xlsx` -> `https://web.archive.org/web/20251126134517id_/https://obr.uk/docs/dlm_uploads/Economy_Detailed_forecast_tables_November_2025.xlsx`
- receipts and other: `Receipts_Detailed_forecast_tables_November_2025.xlsx` -> `https://web.archive.org/web/20251126134206id_/https://obr.uk/docs/dlm_uploads/Receipts_Detailed_forecast_tables_November_2025.xlsx`
- expenditure (incl. welfare): `Expenditure_Detailed_forecast_tables_November_2025.xlsx` -> `https://web.archive.org/web/20251126134142id_/https://obr.uk/docs/dlm_uploads/Expenditure_Detailed_forecast_tables_November_2025.xlsx`
- aggregates: `Aggregates_Detailed_forecast_tables_November_2025.xlsx` -> `https://web.archive.org/web/20251126134346id_/https://obr.uk/docs/dlm_uploads/Aggregates_Detailed_forecast_tables_November_2025.xlsx`
- policy (detailed forecast tables): `Policy_detailed_forecast_tables_November_2025_.xlsx` -> NOT ARCHIVED
- Annex A / policy charts and tables: `Annex_A_charts_and_tables_November_2025.xlsx` -> `https://web.archive.org/web/20251126134240id_/https://obr.uk/docs/dlm_uploads/Annex_A_charts_and_tables_November_2025.xlsx`
- zip: `November-2025-Economic-and-fiscal-outlook-–-detailed-forecast-tables-zip-file.zip` -> `https://web.archive.org/web/20251126134217id_/https://obr.uk/docs/dlm_uploads/November-2025-Economic-and-fiscal-outlook-%E2%80%93-detailed-forecast-tables-zip-file.zip`
- zip: `November-2025-Economic-and-fiscal-outlook-–-detailed-forecast-tables-zip-file-1.zip` -> `https://web.archive.org/web/20260121172819id_/https://obr.uk/docs/dlm_uploads/November-2025-Economic-and-fiscal-outlook-%E2%80%93-detailed-forecast-tables-zip-file-1.zip`

## Download slugs captured directly (earlier or alternative URLs)

Some `obr.uk/download/<slug>/` URLs were captured with status 200 and the file's own MIME type, so the slug URL replays the file itself. Several of these captures predate the earliest capture of the named `/docs/` file:

- `november-2017-economic-and-fiscal-outlook-supplementary-fiscal-tables-receipts-and-other`: `https://web.archive.org/web/20210511052609id_/https://obr.uk/download/november-2017-economic-and-fiscal-outlook-supplementary-fiscal-tables-receipts-and-other/` (xlsx)
- `november-2017-economic-and-fiscal-outlook-supplementary-economy-tables`: `https://web.archive.org/web/20210921234324id_/https://obr.uk/download/november-2017-economic-and-fiscal-outlook-supplementary-economy-tables/` (xlsx)
- `october-2018-economic-and-fiscal-outlook-charts-and-tables-fiscal`: `https://web.archive.org/web/20210921235627id_/https://obr.uk/download/october-2018-economic-and-fiscal-outlook-charts-and-tables-fiscal/` (xlsx)
- `october-2018-economic-and-fiscal-outlook-charts-and-tables-economy`: `https://web.archive.org/web/20210922001135id_/https://obr.uk/download/october-2018-economic-and-fiscal-outlook-charts-and-tables-economy/` (xlsx)
- `october-2018-economic-and-fiscal-outlook-supplementary-economy-tables`: `https://web.archive.org/web/20210922001411id_/https://obr.uk/download/october-2018-economic-and-fiscal-outlook-supplementary-economy-tables/` (xlsx)
- `march-2021-economic-and-fiscal-outlook-charts-and-tables-annex-b`: `https://web.archive.org/web/20210303150049id_/https://obr.uk/download/march-2021-economic-and-fiscal-outlook-charts-and-tables-annex-b/` (xlsx)
- `march-2021-economic-and-fiscal-outlook-supplementary-fiscal-tables-expenditure`: `https://web.archive.org/web/20210303220023id_/https://obr.uk/download/march-2021-economic-and-fiscal-outlook-supplementary-fiscal-tables-expenditure/` (xlsx)
- `october-2021-economic-and-fiscal-outlook-charts-and-tables-annex-a`: `https://web.archive.org/web/20211104130349id_/https://obr.uk/download/october-2021-economic-and-fiscal-outlook-charts-and-tables-annex-a/` (xlsx)
- `economic-and-fiscal-outlook-october-2021`: `https://web.archive.org/web/20211027125218id_/https://obr.uk/download/economic-and-fiscal-outlook-october-2021/` (pdf)
- `october-2021-economic-and-fiscal-outlook-supplementary-economy-tables`: `https://web.archive.org/web/20211118203949id_/https://obr.uk/download/october-2021-economic-and-fiscal-outlook-supplementary-economy-tables/` (xlsx)
- `october-2021-economic-and-fiscal-outlook-supplementary-fiscal-tables-receipts-and-other`: `https://web.archive.org/web/20211103105119id_/https://obr.uk/download/october-2021-economic-and-fiscal-outlook-supplementary-fiscal-tables-receipts-and-other/` (xlsx)
- `october-2021-economic-and-fiscal-outlook-supplementary-fiscal-tables-expenditure`: `https://web.archive.org/web/20211101172726id_/https://obr.uk/download/october-2021-economic-and-fiscal-outlook-supplementary-fiscal-tables-expenditure/` (xlsx)
- `november-2020-economic-and-fiscal-outlook-supplementary-economy-tables`: `https://web.archive.org/web/20210420041706id_/https://obr.uk/download/november-2020-economic-and-fiscal-outlook-supplementary-economy-tables/` (xlsx)
- `november-2020-economic-and-fiscal-outlook-supplementary-fiscal-tables-receipts-and-other`: `https://web.archive.org/web/20210421054719id_/https://obr.uk/download/november-2020-economic-and-fiscal-outlook-supplementary-fiscal-tables-receipts-and-other/` (xlsx)
- `march-2021-economic-and-fiscal-outlook-supplementary-economy-tables`: `https://web.archive.org/web/20210303145813id_/https://obr.uk/download/march-2021-economic-and-fiscal-outlook-supplementary-economy-tables/` (xlsx)
- `march-2021-economic-and-fiscal-outlook-supplementary-fiscal-tables-receipts-and-other`: `https://web.archive.org/web/20210303173632id_/https://obr.uk/download/march-2021-economic-and-fiscal-outlook-supplementary-fiscal-tables-receipts-and-other/` (xlsx)
- `march-2021-economic-and-fiscal-outlook-charts-and-tables-annex-a`: `https://web.archive.org/web/20210303151251id_/https://obr.uk/download/march-2021-economic-and-fiscal-outlook-charts-and-tables-annex-a/` (xlsx)
- `november-2017-economic-and-fiscal-outlook-supplementary-fiscal-tables-expenditure`: `https://web.archive.org/web/20220308233325id_/https://obr.uk/download/november-2017-economic-and-fiscal-outlook-supplementary-fiscal-tables-expenditure/` (xlsx)
- `march-2018-economic-and-fiscal-outlook-supplementary-economy-tables`: `https://web.archive.org/web/20220119022439id_/https://obr.uk/download/march-2018-economic-and-fiscal-outlook-supplementary-economy-tables/` (xlsx)

CDX form used: `http://web.archive.org/cdx/search/cdx?url=obr.uk%2Fdownload%2F<slug>%2F&output=json&matchType=prefix&fl=timestamp%2Coriginal%2Cmimetype%2Clength&filter=statuscode%3A200&limit=5`. The 2013-2016 slugs checked this way (Dec 2013, Dec 2014, Mar 2015, Jul 2015, Mar 2016) have no 200 capture. The full query list is in `work_archive_obr/slug200_extra.json`.

Vintage drift on slug captures: the three captures of `october-2021-economic-and-fiscal-outlook-charts-and-tables-annex-a` (20211104130349, 20220127174955, 20220307164841) have CDX lengths 1,529,082, 194,245 and 1,161,168. The file behind the slug therefore changed over time, and the earliest capture is the one to use.

## Policy costings published by the OBR (item 4)

- **Every event**: the OBR publishes its record of the costings it certified inside the EFO itself. Annex A is confirmed through the separate Annex A PDFs (2016, 2017, Oct 2021) and the Annex A workbooks (Nov 2016, Mar 2020 onward). The pre-2016 PDFs were not opened, so the name and location of their policy annex is unknown. The Treasury's 'Policy costings' document is an HM Treasury publication (gov.uk), not an OBR file, and was not checked here.
- **Machine-readable annex tables**: charts-and-tables workbooks for 2010-2019 (the Nov 2016 `Chapter4_to_annexC_Charts_and_tables.xlsx` was verified by Range-reading its `xl/workbook.xml`: sheets 'Annex A', 'TA.1', 'TA.2', 'TA.3'). Separate 'charts and tables: Annex A' xlsx from Mar 2020; 'detailed forecast tables: policy' from Mar 2024. Older charts-and-tables `.xls` files were not opened, so their annex coverage is unknown.
- **Separate Annex A PDFs**: Mar 2016, Nov 2016 and Mar 2017 (URLs in the per-event lists); `Annex_A_Economic_and_fiscal_outlook_October_2021.pdf` (first captured 2025-04-28).
- **OBR costing notes**: Nov 2015 tax credits costings PDF; Dec 2014 SDLT costing elasticities (`https://web.archive.org/web/20150228233728id_/http://budgetresponsibility.org.uk/wordpress/docs/SDLT-costing-elasticities.pdf`); Mar 2021 notes on CJRS (`https://web.archive.org/web/20230726214554id_/https://obr.uk/docs/dlm_uploads/March-2021-Economic-and-fiscal-outlook-CJRS.pdf`), corporation tax rate increase (`https://web.archive.org/web/20220929224054id_/https://obr.uk//docs/dlm_uploads/March-2021-Economic-and-fiscal-outlook-Corporation-tax-rate-increase.pdf`), fuel duty, EU settlement and state pension underpayment correction; Nov 2023 WCA reform (`https://web.archive.org/web/20240111111130id_/https://obr.uk/docs/dlm_uploads/November-2023-Economic-and-fiscal-outlook-WCA-reform.pdf`). The later Nov 2025 page capture links eight 'supplementary forecast information ... costing' notes (CGT relief on qualifying disposals, APR/BPR, eVED, high value council tax surcharge, non-labour income tax, non-dom update, SEND, salary sacrifice). Their archive status was not checked: unknown.
- **Cumulative databases**: Budget measures database Jul 2012 (`https://web.archive.org/web/20120817043233id_/http://budgetresponsibility.independent.gov.uk/wordpress/docs/Budget_measures_database.xls`), BUD14 (`https://web.archive.org/web/20140505144716id_/http://budgetresponsibility.org.uk/wordpress/docs/Budget_measures_database_BUD14_web.xls`), Mar 2017, Nov 2017, Mar 2019, Nov 2023 (`https://web.archive.org/web/20240205130515id_/https://obr.uk/docs/dlm_uploads/November_2023_Policy_Measures_Database.xlsx`), Mar 2024 (`https://web.archive.org/web/20240524043615id_/https://obr.uk/docs/dlm_uploads/March-2024-Policy-Measures-Database-PUBLISHED_.xlsx`) and Nov 2025 (`https://web.archive.org/web/20260102175529id_/https://obr.uk/docs/dlm_uploads/Policy_measures_database_November_2025_.xlsx`, already harvested). Per the prior harvest notes, the PMD carries original costings unchanged across vintages, so the Nov 2025 vintage covers all 32 events, including those whose per-event tables are missing. Uncertainty-ratings databases are archived for Mar 2017, Nov 2017, Oct 2018, Mar 2019, Mar 2022, Mar 2023, Nov 2023, Mar 2024, Oct 2024, Mar 2025 and Nov 2025.
- **Historical official forecasts database (HOFD)**: one cross-vintage file of each EFO's forecasts. The earliest archived edition is `https://web.archive.org/web/20120816235940id_/http://budgetresponsibility.independent.gov.uk/wordpress/docs/Historical-official-forecasts-database.xls` and the latest is Spring 2026 (harvested). Its contents were not inspected in this pass. It is the obvious fallback for headline vintages where supplementary tables are missing (Mar 2011, Dec 2013).

## Patterns

- **EFO PDFs**: all 32 have a 200 capture, most within days or a few weeks of publication. The latest first captures are June 2010 (12 Oct 2010) and Budget 2011 (5 Aug 2011; earlier captures of the cdn URL are 301s).
- **Archived as published (on or near publication day)**: Autumn 2010, Autumn 2011, Budget 2012, Budget 2014, Autumn 2015, Autumn 2016 through Spring Statement 2019, Budget 2020, Spring Budget 2021 and Autumn Budget 2021 (through download-slug captures), and Spring Statement 2022 through Autumn Budget 2025. From Mar 2022, every table file was captured on publication day itself.
- **Archived, but only as later re-uploads, renames or captures years after publication**: Autumn 2012 (fiscal), Budget 2013 (fiscal, charts), Autumn 2013 (fiscal, charts), Autumn 2014 (fiscal and charts first captured 2022, names unchanged), Budget 2015 (economy and fiscal; the fiscal file is 'v3', last modified 13 May 2015), July 2015 (economy, fiscal), Budget 2016 (economy, 2021), Autumn Budget 2017 (economy and expenditure, 2021-2023), Spring Statement 2018 (economy 'Updated_'), Spending Review 2020 (Annex A, 2022). For a vintage-faithful replay these are usable with a caveat: the OBR re-uploads corrected files (`-1`, `-2`, `v2`, `v3`, `v4`, `Updated_`, `Copy-of-`, `amended`), and a capture years later may hold a corrected file under the same name.
- **Gaps**: Budget 2011 fiscal supplementary tables (the receipts and welfare detail) and the original economy tables; Autumn 2013 economy supplementary tables; the June 2010 'Supplementary tables' linked only by the later site; the Autumn Budget 2025 standalone policy workbook (recoverable from the later zip). For these the EFO PDF (archived for all 32) and the charts-and-tables workbook (archived for every event from Nov 2010; June 2010 has its own tables workbook) carry the chapter-level receipts and welfare tables.

## Fetch recipe

1. List: `http://web.archive.org/cdx/search/cdx?url=<host>/<path>&output=json&matchType=exact&filter=statuscode:200&fl=timestamp,original,mimetype,length` (no `collapse`, to see every capture). For discovery use `matchType=domain` on `budgetresponsibility.independent.gov.uk` (2010-13; includes `cdn.`, `/d/`, `/pubs/`, `/wordpress/docs/`), `budgetresponsibility.org.uk` (2013-17; `/pubs/`, `/wordpress/docs/`, `/docs/dlm_uploads/`, `cdn.`) and `obr.uk` (2017+; `/docs/dlm_uploads/`, `/docs/`, `cdn.obr.uk`, `/download/<slug>/`) with `filter=original:.*<regex>.*`.
2. Prefer the earliest 200 capture of the as-published name. As-published pages: 2010 `publications.html` and `econ-fiscal-outlook*.html`; 2011-13 `/economic-and-fiscal-outlook-<month>-<year>/`; 2013-15 `budgetresponsibility.org.uk/economic-fiscal-outlook-<month>-<year>/`; 2016+ the earliest capture of `obr.uk/efo/<slug>/` (list below).
3. Download original bytes: `https://web.archive.org/web/<timestamp>id_/<original>`. HTML pages may come back gzip-encoded; decompress them.
4. Resolve an obr.uk `/download/<slug>/` link: GET `https://web.archive.org/web/<ts>id_/https://obr.uk/download/<slug>/` **without following redirects**. The `Location` header is the stored 302 target (`/web/<ts>id_/https://obr.uk/docs/dlm_uploads/<file>`). Some slugs were captured as 200 file bytes directly (section above). 2010-15 `/pubs/<name>` links redirect through `wordpress/wp-content/plugins/download-monitor/download.php?id=<name>` to `/wordpress/docs/<name>` or `cdn.<domain>/<name>`.
5. Zip members and xlsx metadata without a full download: Range requests on `id_` URLs return 206. Read the last 64 KB for the zip central directory, then fetch single members such as `xl/workbook.xml` (sheet names) or `docProps/core.xml` (dates). Scripts: `work_archive_obr/ziprange.py`, `work_archive_obr/zipcore.py`.
6. Politeness: one stream, 1.2-2.5 s between requests. Two parallel streams tripped throttling here. Do not cache 5xx or connection errors as results.

As-published pages used (Wayback):

- `https://web.archive.org/web/20100712141819id_/http://budgetresponsibility.independent.gov.uk:80/publications.html`
- `https://web.archive.org/web/20101202020459id_/http://budgetresponsibility.independent.gov.uk:80/econ-fiscal-outlook.html`
- `https://web.archive.org/web/20110325051917id_/http://budgetresponsibility.independent.gov.uk:80/econ-fiscal-outlook-march.html`
- `https://web.archive.org/web/20121206150735id_/http://budgetresponsibility.independent.gov.uk/economic-and-fiscal-outlook-december-2012/`
- `https://web.archive.org/web/20130321035502id_/http://budgetresponsibility.independent.gov.uk/economic-and-fiscal-outlook-march-2013/`
- `https://web.archive.org/web/20131209055845id_/http://budgetresponsibility.org.uk:80/economic-fiscal-outlook-december-2013/`
- `https://web.archive.org/web/20150114233200id_/http://budgetresponsibility.org.uk:80/economic-fiscal-outlook-december-2014/`
- `https://web.archive.org/web/20150321060958id_/http://budgetresponsibility.org.uk:80/economic-fiscal-outlook-march-2015/`
- `https://web.archive.org/web/20150709003630id_/http://budgetresponsibility.org.uk/economic-fiscal-outlook-july-2015/`
- `https://web.archive.org/web/20150728082339id_/http://budgetresponsibility.org.uk:80/economic-fiscal-outlook-supplementary-fiscal-tables-july-2015/`

## Open items (unknown)

- UKGWA holdings for every file (WAF captcha; needs a person in a browser, or a different access route).
- Whether the re-uploaded or renamed files (Y\*) match the as-published ones. Where both exist (e.g. Autumn 2012 tables5 vs Copy-of-tables4), download both, or compare against the EFO PDF tables.
- The July 2015 economy table attribution (`Economy_Supplementary_Tables-2015.xls`). The obr.uk July 2015 economy slug has no captures; the file was not opened.
- Sheet contents of the June 2010 'Budget forecast tables' workbook and of the pre-2016 charts-and-tables `.xls` files (annex coverage).
- Archive status of the Nov 2025 'supplementary forecast information' costing notes.
