Staged **32 rows from 9 primaries**. All four families pass the checker with **0 problems**, and every `stage.py` rerun reproduces identical gzip bytes. Nothing was committed or pushed.

| Family/report | Rows | Primaries | Rows by measure key |
|---|---:|---:|---|
| [uk_niesr](/Users/maxghenis/reviews/scorecard-ab2026-harvest/wt/thinktanks-b/sources/harvest-uk-ab2026-2026-10-29/uk_niesr/NOTES.md) | 0 | 1 | null: 0 |
| [uk_fai_sfc](/Users/maxghenis/reviews/scorecard-ab2026-harvest/wt/thinktanks-b/sources/harvest-uk-ab2026-2026-10-29/uk_fai_sfc/NOTES.md) | 5 | 1 | null: 5 |
| [uk_thinktank_misc](/Users/maxghenis/reviews/scorecard-ab2026-harvest/wt/thinktanks-b/sources/harvest-uk-ab2026-2026-10-29/uk_thinktank_misc/NOTES.md) | 13 | 6 | household energy payment: 1; null: 12 |
| [uk_devolved_govts](/Users/maxghenis/reviews/scorecard-ab2026-harvest/wt/thinktanks-b/sources/harvest-uk-ab2026-2026-10-29/uk_devolved_govts/NOTES.md) | 14 | 1 | null: 14 |

The sole registered key is `ab2026__household_energy_payment_100_bands_a_to_d`.

Primary SHA256s:

| Primary | Rows | SHA256 |
|---|---:|---|
| [NIESR](https://niesr.ac.uk/blog/breathing-space-not-strategy) | 0 | `0108b60ad2a85e65a717c03a68060ad9c45fdcbe09cb5a24eca374a618436ccb` |
| [Scottish Government](https://www.gov.scot/news/uk-budget-delivers-real-cut-to-scotlands-funding/) | 5 | `f3d0183e470f711b6821e4956e108c5d17210a392e6a6e471eccf297c807a6ac` |
| [CPS](https://cps.org.uk/media/post/2026/a-dangerous-continuation-of-labours-tax-and-spend-fantasy-cps-verdict-on-the-budget/) | 4 | `2c832e011866eb9f63f20597e7bf43bc01d44b6b1b5be43eee866ad6fc5ecd24` |
| [IfG](https://www.instituteforgovernment.org.uk/comment/john-healeys-underwhelming-budget) | 6 | `ecf19f14b4f808846fb8230b28a3244b0b65812484735842f9ab537a50195c69` |
| [Age UK](https://www.ageuk.org.uk/latest-press/age-uk-response-to-the-budget/) | 0 | `3035a8bbbb0f023dc24e805b430052163aa0dbfce3c975a6e0a0568983db6bf0` |
| [Learning and Work Institute](https://learningandwork.org.uk/responding-to-autumn-budget-2026/) | 1 | `c7fe077a0d9f4784aa4c91c906bcefa087cc9a4ece8b28026d24347c2a8b5dcf` |
| [Citizens Advice](https://www.citizensadvice.org.uk/about-us/media-centre/press-releases/citizens-advice-responds-to-chancellors-budget/) | 1 | `6a10336a67fc058512a4ccd9d0e80a27470fee8ba5775690fb1fcba39db67385` |
| [Trussell](https://www.trussell.org.uk/news-and-research/news/our-response-to-the-autumn-budget-2026) | 1 | `6cd2162d1382f03e937a382a39bd38c497a83d357bd969d2c85598740d17a95e` |
| [Welsh Government](https://www.gov.wales/written-statement-welsh-government-response-uk-autumn-budget-2026) | 14 | `87490552c36d8ffd5787db18127704e467d93599e5708627adb6da7dcfe17c7c` |

Two measure keys are proposed:

- `ab2026__package_welsh_settlement_changes`: 12 rows covering the £448m headline and Resource/Capital/Total settlement changes over 2026–27 to 2029–30, excluding employer pension contribution savings.
- `ab2026__package_cps_public_financial_institutions`: one row covering CPS’s asserted £3.1bn annual debt increase through PuFins.

**Neither primary enumerates the component Treasury lines.** Exact Table 6.1 membership—and Table 6.2 membership for CPS—remains explicitly unresolved. No registered package equivalence was inferred.

Verification included primary hashes and byte counts, quote containment and length, scope review, and these reopened checks:

- **Wales, 10 random rows:** Resource £146m for 2028–29; Capital −£27m/−£19m/£2m/−£18m across the four years; Total £172m/£148m/−£18m for 2026–27/2028–29/2029–30; Resource reduction 0.5% for 2027–28; Capital reduction almost 10% by 2029–30.
- **Miscellaneous, 10 random rows:** CPS £61bn debt interest and £3.1bn/year; IfG almost 100 policies, one qualifying tax measure, 56%/59% probabilities, and 80% rebate coverage; LWI one million NEET people; Citizens Advice £60/month; Trussell over half.
- **Scotland, all five rows:** £650m total, 1.3%/£550m Resource, 1.5%/£100m Capital, all for 2027–28.
- **NIESR:** no eligible rows; ten excluded figure groups were reopened instead.

Signs, units and periods passed; detailed locators appear in each report.

FAI returned **403**; no bypass or fallback was used. No qualifying SFC publication or further NIESR analysis dated 28–29 October was found. NIESR’s macro/fiscal figures were excluded under #55. Age UK’s specified tax-threshold paragraph contains no number. Bare payment parameters, existing rail commitments, unrelated navigation figures and unlabelled chart readings were excluded.

Source limitations remain recorded: NIESR’s £12.4bn borrowing aggregation is unclear; Scotland has conflicting modification timestamps and unspecified comparison/price bases; IfG’s rebate denominator geography is unstated; CPS’s PuFins components and scoring years are unspecified. No primary figures were repaired.