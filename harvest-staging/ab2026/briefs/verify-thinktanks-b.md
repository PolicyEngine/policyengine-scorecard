
## Your assignment: families `uk_niesr`, `uk_fai_sfc`, `uk_thinktank_misc` and `uk_devolved_govts`

Verify these four families under `sources/harvest-uk-ab2026-2026-10-29/`. Ignore `uk_hmt_tables`, which is already in the PR. Together they hold 32 rows from 9 primaries: NIESR 0, Scottish Government 5, the misc family 13 (CPS, IfG, Age UK, Learning and Work Institute, Citizens Advice, Trussell) and the Welsh Government 14.

- **Sample:** every row.
- **NIESR (0 rows):** check that NOTES.md's exclusions hold: macro calls belong to the #55 lane, and NIESR's other figures don't concern a measure.

**Settled; don't reopen:**
- The two `measure_count` rows in `uk_thinktank_misc` stay. They follow the AB2025 misc family's precedent, and the AB2026 IFS family stages its "98 measures" the same way.
- Fraser of Allander returned 403 both to curl and in a browser. It is unreached, and nothing replaces it.

**Look hard at the two proposed packages:**
- `ab2026__package_welsh_settlement_changes`;
- `ab2026__package_cps_public_financial_institutions`.

For each, judge whether its scope is stated clearly enough for tranche 2 to register it. If a row is a context figure about no measure, it should have `measure_key: null` and no proposed key.
