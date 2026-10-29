# Harvest: Autumn Budget 2026 scores from every producer (#230)

Staged from 2026-10-29, the day after the Budget, from the primary documents. The layout follows the AB2025 harvest (`sources/harvest-uk-ab2025-2026-09-24/`):

- One family directory per producer group.
- Each family holds:
  - `NOTES.md`: access recipe, coverage tally, and what was **not** staged and why;
  - `manifest.jsonl`: one line per primary document, with its sha256;
  - `claims_staged.jsonl.gz`: one line per claim.
- `COUNTS.json` pins each family's rows, primaries, producer slugs and the sha256 of its claims file. `pipeline/harvest_counts.py` writes and checks it.
- `REGISTRY_KEYS.md` lists every measure key. `pipeline/build_ab2026_registry.py` generates it.
- `PROPOSED_KEYS.md` lists every proposed key a row names (rule 2), for tranche 2 to register. `pipeline/ab2026_proposed_keys.py` generates it.
- `SEED_INVENTORY/` lists the publications the harvest starts from, compiled while monitoring reactions on 28 and 29 October.

Nothing reads this harvest yet. Tranche 2 of #230 adds the ingest. That ingest's exact accounting will read `read = ingested + dropped` against the rows pinned in `COUNTS.json`. `tests/test_uk_ab2026_harvest.py` checks every row against the contract below.

## Rules

The AB2025 harvest README's rules 1–10 and its row contract apply, with the AB2026 exceptions and additions below:

1. **`fiscal_event` is the slug `autumn_budget_2026`** on every row, whatever the publication calls it.
2. **Measure keys come from `data/uk/ab2026_measures.json`.**
   - `ab2026__…` keys cover announced measures: every HM Treasury Table 6.1 line, Table 6.2 line 4, and the `ab2026__package_…` packages.
   - `ab2026_option__…` keys cover options a producer costed. None is registered yet. A row on an unregistered option, or on a package whose scope is not one of the registered packages, has `measure_key: null`. Its proposed key goes in `conditions.proposed_measure_key`, and its NOTES says what the scope is. The registry adds it before ingest.
   - Table 6.4 recostings are the one exception. They carry the earlier event's key, named in `conditions.recosting_of`.
   - **Naming a proposed key:**
     - An announced measure with no Table 6.1 line is `ab2026__<slug>`, naming the measure. That covers a measure below Table 6.1's £10m threshold, a fiscally neutral one and one costed only elsewhere.
     - A package is `ab2026__package_<slug>`, and the slug names the scope, not the producer, so that producers with the same scope share one key. Lines 61 and 62 together are `ab2026__package_property_and_savings_income_rates`. A producer's or the OBR's name goes in the slug only for a grouping that is its own, such as `ab2026__package_tpa_other_vat`.
     - An option a producer costed is `ab2026_option__<slug>`.
     - The coordinator gives each scope one key across families before merging. `PROPOSED_KEYS.md` lists the result.
3. **A measure's scope is the producer's, not ours.** A producer's figure for "the cost-of-living package" joins `ab2026__package_household_energy_vat_and_fuel_duty` only when its scope is exactly Table 6.1 lines 1, 2 and 3. Otherwise it is a proposal (rule 2).
   - Line 2 costs the whole electricity VAT cut, from 1 October 2026 to 1 July 2027 (£755m in 2026-27 and £305m in 2027-28), including the weeks before the Budget. A package of the energy payment, the VAT cut and the fuel duty cut is therefore exactly lines 1, 2 and 3. A package that also counts the gas standing-charge change, which has no Table 6.1 line, is a proposal.
4. **HMT Impact on households, Figures 1.A and 1.B: no bar readings** (AB2025 rule 9, #61). Values HM Treasury prints as numbers, in text, tables or data labels, are staged as printed.
5. **PolicyEngine's own published figures are not harvested here.** They are tranche 3's counterparts, computed from the dashboard's receipts. A producer that restates a PolicyEngine figure is staged with `attribution: same_assumptions`, as the Fabian Society's row was for AB2025.
6. **Quotes from producers outside the Open Government Licence stay short.** `quote` is the sentence or cell carrying the number, cut to the words that carry it: under 15 words for think tanks, firms and the press. HM Treasury and OBR material is OGL, and its cells and sentences are quoted whole.
7. **A primary that changes is a second primary.** If a producer replaces a document, both versions are hashed in `manifest.jsonl` and rows cite the version they were read from. IFS replaced its cost-of-living deck on 29 October, and HM Treasury replaced the Budget 2026 document PDF after 28 October. NOTES says what changed.
8. **Stage estimates, not design.** A row is a number someone estimated, forecast or counted about the effect of a measure or of the Budget. That covers:
   - a cost or yield;
   - people or households affected;
   - a gain, loss or bill change;
   - a distributional or poverty effect;
   - a behavioural adjustment or tax base;
   - a fiscal aggregate;
   - a consequential for a devolved government.

   A measure's own parameters are its design: rates, thresholds, payment amounts, dates and durations. So are spending allocations to programmes, financing remits and contingent liabilities. They go in `reform_hint` or `conditions`, never as rows (the AB2025 red book family kept "£9.90" in `reform_hint` the same way). A worked example's inputs follow this rule too, and its computed outcome is a row.
9. **A component of one measure keeps that measure's key.** A printed part of one Table 6.1 measure carries that measure's key, with `conditions.component` naming the part and `conditions.row_type: measure_component`. A part can be a fiscal head, a sub-measure within a line (the tax-gap package's items, for example) or a nation. Components are never summed with the measure's total. Proposed package keys are for scopes that cross Table 6.1 lines, or have none.

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
