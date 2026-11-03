## Your assignment: four families

1. **`uk_niesr`** (source `niesr`): https://niesr.ac.uk/blog/breathing-space-not-strategy
   - Also stage any NIESR AB2026 post-Budget analysis, for example a living-standards or fiscal commentary from 28–29 October.
   - Macro forecasts belong to the #55 lane, not here (AB2025 rule 10).
2. **`uk_fai_sfc`** (sources `fraser_of_allander` and `scottish_fiscal_commission`):
   - https://fraserofallander.org/uk-budget-reaction/
   - Also stage any Scottish Fiscal Commission or Scottish Government publication on the UK Budget's consequences for Scotland's block grant, published 28–29 October, if you find one.
   - Barnett consequentials use the AB2025 proposal `block_grant_effect`.
3. **`uk_thinktank_misc`:**
   - Centre for Policy Studies (`cps`): https://cps.org.uk/media/post/2026/a-dangerous-continuation-of-labours-tax-and-spend-fantasy-cps-verdict-on-the-budget/
   - Institute for Government (`institute_for_government`): https://www.instituteforgovernment.org.uk/comment/john-healeys-underwhelming-budget
   - Age UK (`age_uk`): https://www.ageuk.org.uk/latest-press/age-uk-response-to-the-budget/ (its Pension Tax Allowance paragraph sits under "On Income Tax threshold")
   - Learning and Work Institute (`learning_and_work_institute`): https://learningandwork.org.uk/responding-to-autumn-budget-2026/
   - Citizens Advice and the Trussell Trust: find their Budget responses of 28 October on their press pages.
4. **`uk_devolved_govts`** (source `welsh_government`): https://www.gov.wales/written-statement-welsh-government-response-uk-autumn-budget-2026
   - It prints the consequentials for Wales. Stage them with `proposed_metric` `block_grant_effect`, as AB2025 did for devolved consequentials.

**General rules:**
- Producers often restate HMT or OBR numbers. Stage them as `restated`; the ingest drops them, with a count.
- Stage a producer's own estimate as `own`.
- A family whose primaries hold no numbers about the Budget still gets a directory: NOTES.md says so, the manifest lists the primaries, and the claims file holds zero rows (an empty gzip written as above).

**Precedent:** follow each AB2025 family of the same name.

**Quotes:** fewer than 15 words.
