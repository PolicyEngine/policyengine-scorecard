# Harvest: Autumn Budget 2026 scores from every producer (#230)

Staged from 2026-10-29, the day after the Budget, from the primary documents. The layout follows the AB2025 harvest (`sources/harvest-uk-ab2025-2026-09-24/`):

- One family directory per producer group.
- Each family holds:
  - `NOTES.md`: access recipe, coverage tally, and what was **not** staged and why;
  - `manifest.jsonl`: one line per primary document, with its sha256;
  - `claims_staged.jsonl.gz`: one line per claim.
- `COUNTS.json` pins each family's rows, primaries, producer slugs and the sha256 of its claims file. `pipeline/harvest_counts.py` writes and checks it.
- `REGISTRY_KEYS.md` lists every measure key. `pipeline/build_ab2026_registry.py` generates it.
- `SEED_INVENTORY/` lists the publications the harvest starts from, compiled while monitoring reactions on 28 and 29 October.

Nothing reads this harvest yet. Tranche 2 of #230 adds the ingest. That ingest's exact accounting will read `read = ingested + dropped` against the rows pinned in `COUNTS.json`. `tests/test_uk_ab2026_harvest.py` checks every row against the contract below.

## Rules

The AB2025 harvest README's rules 1–10 and its row contract apply unchanged, except for the following:

1. **`fiscal_event` is the slug `autumn_budget_2026`** on every row, whatever the publication calls it.
2. **Measure keys come from `data/uk/ab2026_measures.json`.**
   - `ab2026__…` keys cover announced measures: every HM Treasury Table 6.1 line, Table 6.2 line 4, and the `ab2026__package_…` packages.
   - `ab2026_option__…` keys cover options a producer costed. None is registered yet. A row on an unregistered option, or on a package whose scope is not one of the registered packages, has `measure_key: null`. Its proposed key goes in `conditions.proposed_measure_key`, and its NOTES says what the scope is. The registry adds it before ingest.
   - Table 6.4 recostings are the one exception. They carry the earlier event's key, named in `conditions.recosting_of`.
3. **A measure's scope is the producer's, not ours.** A producer's figure for "the cost-of-living package" joins `ab2026__package_household_energy_vat_and_fuel_duty` only when its scope is exactly Table 6.1 lines 1, 2 and 3. Otherwise it is a proposal (rule 2).
   - For example, RF's package also includes the electricity VAT cut that was announced before the Budget, and its own rows say so.
4. **HMT Impact on households, Figures 1.A and 1.B: no bar readings** (AB2025 rule 9, #61). Values HM Treasury prints as numbers, in text, tables or data labels, are staged as printed.
5. **PolicyEngine's own published figures are not harvested here.** They are tranche 3's counterparts, computed from the dashboard's receipts. A producer that restates a PolicyEngine figure is staged with `attribution: same_assumptions`, as the Fabian Society's row was for AB2025.
6. **Quotes from producers outside the Open Government Licence stay short.** `quote` is the sentence or cell carrying the number, cut to the words that carry it: under 15 words for think tanks, firms and the press. HM Treasury and OBR material is OGL, and its cells and sentences are quoted whole.
7. **A primary that changes is a second primary.** If a producer replaces a document, both versions are hashed in `manifest.jsonl` and rows cite the version they were read from. IFS replaced its cost-of-living deck on 29 October, and HM Treasury replaced the Budget 2026 document PDF after 28 October. NOTES says what changed.

## Producer slugs and families

| slug | producer | family dir |
|---|---|---|
| hm_treasury | HM Treasury: Tables 6.1, 6.2 and 6.4 | uk_hmt_tables |
| hm_treasury | HM Treasury: policy costings (static and post-behavioural legs, tax bases, behavioural parameters) | uk_hmt_costings |
| hm_treasury | HM Treasury: Budget 2026 document, Impact on households, Pension Tax Allowance explainer | uk_hmt_redbook |
| obr_efo | OBR: Economic and fiscal outlook, October 2026, and its detailed tables | uk_obr_tables |
| resolution_foundation | Resolution Foundation | uk_rf_ab2026 |
| ifs | Institute for Fiscal Studies | uk_ifs_ab2026 |
| tax_policy_associates, centax, cpag, ippr, niesr, fraser_of_allander, scottish_fiscal_commission, cps, institute_for_government, age_uk, … | other producers, each in the AB2025 family of the same name where one exists | uk_tpa, uk_centax, uk_cpag, uk_ippr, uk_niesr, uk_fai_sfc, uk_thinktank_misc, … |
| commercial firms and platforms | worked examples (mode 3, #63) | uk_cases_commercial |

Macro calls by banks and City forecasters belong to the #55 lane and are not staged here (AB2025 rule 10).
