## Your assignment: family `uk_obr_tables` (source `obr_efo`)

**Primaries:** OBR, *Economic and fiscal outlook*, October 2026, published 28 October 2026. The EFO page is https://obr.uk/efo/economic-and-fiscal-outlook-october-2026/.
- obr.uk may refuse curl. The files were downloaded in a browser on 28 October, and their exact bytes are under /Users/maxghenis/reviews/scorecard-ab2026-harvest/local-primaries/obr/ with /Users/maxghenis/reviews/scorecard-ab2026-harvest/local-primaries/obr/PROVENANCE.md, which gives the resolved URL, bytes, sha256 and Last-Modified.
- Try fetching each resolved URL once.
  - **If it works:** check that the hash matches.
  - **If it's refused:** use the local copy (`access`: "local copy", note citing PROVENANCE.md).
- The PDF's URL isn't in PROVENANCE.md. Find it on the EFO page, or use the local file and note that.

**What to stage:**
- **The policy workbook** (`efo-october-2026-detailed-forecast-tables-policy.xlsx`): every measure line and every year.
  - Measure key: match each measure to its Table 6.1 key by title. OBR's titles can differ slightly from HMT's, so record OBR's title in `reform_hint`.
  - Leave recostings and other non-Table-6.1 lines with `measure_key` null and say so in NOTES.md.
  - If the workbook gives OBR's uncertainty ratings, behavioural adjustments or static/post-behavioural splits, stage them as in the AB2025 `uk_obr_tables` family.
- **EFO chapter 3 (policy) and Annex A text:** each number about a measure's costing or behavioural adjustment. Examples:
  - paragraph 3.17 on the savings and property income tax rises;
  - paragraph 3.19 on the fuel duty path;
  - the energy measures;
  - the Pension Tax Allowance;
  - the Carer's Allowance taper.
- **Headline fiscal aggregates:** headroom against the fiscal rules, PSNB, and PSND ex BoE or PSNFL. Use the measure_key null context rows, as the AB2025 family did, with the same metric and proposed_metric names.

**Precedent:** follow the AB2025 `uk_obr_tables` family's conventions closely (927 rows there). Restrict this family to policy-relevant tables. Don't stage the whole economy forecast (GDP, CPI paths) unless the AB2025 family did; match its scope.

**Licence:** the material is OGL.
