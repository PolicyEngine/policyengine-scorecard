## Your assignment: family `uk_hmt_redbook` (source `hm_treasury`)

Three primaries:

1. **Budget 2026 document** (the "red book").
   - URL: https://assets.publishing.service.gov.uk/media/6ae20b85460c1346f7be784e/E03668986_HMT_Budget_2026_ELAY__2_.pdf
   - **The PDF changed after publication.** The 28 October download is /Users/maxghenis/reviews/scorecard-ab2026-harvest/local-primaries/hmt-2026-10-28/E03668986_HMT_Budget_2026_ELAY__2_.pdf (sha256 bed70546…); the 29 October download is /Users/maxghenis/reviews/scorecard-ab2026-harvest/local-primaries/hmt-2026-10-29/E03668986_HMT_Budget_2026_ELAY__2_.pdf (sha256 19b337ac…, 4,679,545 bytes).
   - Fetch it again now, hash every distinct version in the manifest, and stage rows from the current version.
   - Diff the text of the versions (`pdftotext -layout`, then `diff`) and record in NOTES.md which numbers, if any, changed.
   - The gov.uk HTML version is in the content API: https://www.gov.uk/api/content/government/publications/budget-2026-document (find the HTML attachment from there).
2. **Impact on households: distributional analysis to accompany Budget 2026.**
   - URL: https://assets.publishing.service.gov.uk/media/6ae1850f16428df53760627d/Impact_on_households.pdf
   - Local copy: /Users/maxghenis/reviews/scorecard-ab2026-harvest/local-primaries/hmt-2026-10-29/Impact_on_households.pdf (sha256 36cd5afb…).
   - **README rule 4:** never read Figures 1.A or 1.B by bar height. Stage only numbers HM Treasury prints: in text, tables or data labels.
3. **Pension Tax Allowance explainer.**
   - URL: https://www.gov.uk/government/publications/pension-tax-allowance-explainer/pension-tax-allowance-explainer
   - Content API: https://www.gov.uk/api/content/government/publications/pension-tax-allowance-explainer/pension-tax-allowance-explainer
   - Hash the content API JSON; its `details.body` is the text. The 28 and 29 October API responses hash differently (cc3ec22e… and 791d2573…, both under /Users/maxghenis/reviews/scorecard-ab2026-harvest/local-primaries), so say in NOTES.md whether the body text differs.
   - It prints counts of pensioners who gain or pay no tax, and worked cases. Stage worked cases as conditions-rich rows, following the AB2025 redbook family's handling of worked examples.

**Rows to stage:**
- **Measure figures:** every number the red book prints about a measure: costs, people or households affected, amounts per household, dates as numbers. Use the key whose Table 6.1 title matches.
- **No re-staging:** don't re-stage the scorecard table (Table 6.1, already staged in `uk_hmt_tables`) or Table 6.4.
- **Fiscal aggregates** (headroom, borrowing, debt) appear in the red book as OBR figures. Stage them as `restated` with `note` "OBR EFO", and only where the red book prints them.

**Precedent:** follow the AB2025 `uk_hmt_redbook` family's conventions.

**Licence:** the material is OGL, so quotes may be whole sentences.
