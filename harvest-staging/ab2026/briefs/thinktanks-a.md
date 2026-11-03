## Your assignment: five families

1. **`uk_tpa`** (source `tax_policy_associates`): https://taxpolicy.org.uk/2026/10/28/budget-2026-what-it-means/
   - Covers the Pension Tax Allowance design, its taper and the resulting marginal rates, and other measures.
   - Stage any linked spreadsheet or calculator data TPA published for the Budget. The AB2025 `uk_tpa` family had 3,008 rows from such tables; follow its conventions.
2. **`uk_centax`** (source `centax`): https://centax.org.uk/autumn-budget-2026-reaction/
   - Also stage any CenTax AB2026 briefing or data linked from it.
   - Don't use LinkedIn; it needs a login.
3. **`uk_cpag`** (source `cpag`):
   - https://cpag.org.uk/news/cpags-2026-budget-response
   - https://cpag.org.uk/news/campaigners-call-ps10-child-uk-budget-boost-child-benefit (a pre-Budget call: stage its numbers only if it is about this Budget's options, with `ab2026_option__` proposed keys)
4. **`uk_ippr`** (source `ippr`): https://www.ippr.org/media-office/unfinished-business-on-economic-reform-after-sound-budget-says-ippr
   - Also stage IPPR's other AB2026 responses of 28–29 October, if you can find them on ippr.org's media office or news pages.
5. **`uk_smf`** (source `smf`): https://www.smf.co.uk/todays-budget-provides-immediate-relief-for-households-but-details-of-changes-on-many-larger-issues-yet-to-come-think-tank-says/

**General rules:**
- Producers often restate HMT or OBR numbers. Stage them as `restated`; the ingest drops them, with a count.
- Stage a producer's own estimate as `own`.
- A family whose primaries hold no numbers about the Budget still gets a directory: NOTES.md says so, the manifest lists the primaries, and the claims file holds zero rows (an empty gzip written as above).

**Precedent:** follow each AB2025 family of the same name.

**Quotes:** fewer than 15 words.
