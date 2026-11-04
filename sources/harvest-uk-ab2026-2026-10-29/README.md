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

   Lending and financing follow one rule across families. The harvest stages HM Treasury's Tables 6.1, 6.2 and 6.4 and the OBR's policy workbook whole, as the decisions' costings. Elsewhere, an amount a scheme will lend or spend is design, and an effect on borrowing, debt or the financing requirement is an estimate. So the OBR's paragraph 3.22 loan volumes for Your First Home are not staged, while its effect on debt is, and paragraph 3.20's rise in the Government's financing requirement is staged on `cash_requirement_change`.
9. **A component of one measure keeps that measure's key.** A printed part of one Table 6.1 measure carries that measure's key, with `conditions.component` naming the part and `conditions.row_type: measure_component`. A part can be a fiscal head, a sub-measure within a line (the tax-gap package's items, for example) or a nation. Components are never summed with the measure's total. Proposed package keys are for scopes that cross Table 6.1 lines, or have none.
10. **A producer's stated effect of the Budget's decisions on PSNB takes `decisions_effect_on_borrowing`.** That covers the total effect of Government decisions, its direct and indirect effects and any part of them the producer identifies, its splits into tax and spending and into scorecard and non-scorecard decisions, and figures that restate or recombine those effects without ambiguity. `models.py` defines the metric as PSNB and keeps it apart from `revenue_change`, a receipts line, and `ingest_obr_policy_effects.py` maps March 2026 Table B.1's totals, its direct effects and their tax and spending split to it. HM Treasury sets out in Table 6.1 the cost or yield of the decisions "which have a direct effect on Public Sector Net Borrowing", so Table 6.1's three totals, and the figures that restate them, take the metric. A receipts total or a tax-change estimate keeps `revenue_change` unless its evidence establishes PSNB scope, and a total key or a package label alone doesn't establish it. The OBR sums its receipts heads, from air passenger duty to visa fees, into its policy workbook's total of receipts measures, so that total keeps `revenue_change`. IFS doesn't tie its own estimate of the Budget's tax change at the forecast horizon to PSNB, so that estimate keeps `revenue_change` too. `ingest_uk_ab2025.py` maps AB2025's `package_tax_rise_size` rows to the same metric. Single measures, groups of measures and a total's lines by tax or spending head keep `revenue_change`, unless their producer states the effect on borrowing, as the OBR does for four policies in paragraphs 3.20, 3.21 and 3.43 and IFS does for the Budget's new giveaways. Text that restates a Table 3.1 group or a single measure as an effect on borrowing keeps that row's metric (the OBR's paragraph 3.11 "increase borrowing by £5 billion in 2026-27" restates Table 3.1's other departmental spending changes, which keep `revenue_change`), and Table 3.1's "A positive sign implies an increase in borrowing" is a sign convention, not a statement of PSNB scope. A total that adds the receipts effect of an option the Budget didn't adopt is not a restatement or recombination of the decisions' effects, so it keeps `revenue_change` unless its evidence establishes PSNB scope: Resolution Foundation's Figure 10 "Net effect if Fuel Duty frozen" adds a continued freeze's receipts effect, which its note derives from the OBR's constant-duty-rate fuel duty forecast, and the OBR states the freeze's effect on borrowing for 2029-30 only (paragraph 3.43). A row giving the effect on the current budget deficit (or, for an outturn, the primary deficit) proposes `fiscal_balance_change`, and its sign convention names that deficit. Each row keeps the sign its producer prints, and `conditions.sign_convention` says which way it runs.

## Row contract additions

`pipeline/ab2026_harvest_contract.py` checks the AB2025 row contract with these additions (review A, H-1 to H-6):

- `value_kind` may also be `categorical` (a rating, such as the OBR's Table 3.3 uncertainty ratings).
- `value` is finite, and it is `value_raw`'s number at the scale `value_raw`'s word gives (bn, m, k, %), failing that at the factor `normalization` states, failing that at 1, 10³, 10⁶, 10⁹, 0.01 or 100. Its sign is `value_raw`'s unless `normalization` says the sign comes from the wording.
- A row that carries `conditions.component` is a part: `row_type` is `measure_component` (or the OBR workbook's `measure_total` marker), and the component isn't blank (rule 9).
- No more than two non-restated rows share the AB2025 ingest's claim identity, and two that do agree within 0.5%.
- A registered metric goes in `metric`, never `proposed_metric`.
- `conditions.recosting_of` appears only on `row_type: recosting` rows (Table 6.4).
- `conditions.fy` is one fiscal year, and a `fiscal_year` row without `fy` gives `conditions.horizon`.
- `conditions.geography` is a code: UK, GB, England, Wales, Scotland, Northern Ireland, England and Wales, UK_excl_scotland, "Scotland, Wales and Northern Ireland", "not stated", or a country a producer compares the UK with. Prose goes in `conditions.geography_note`.
- A restated row's `note` says whose figure it restates.
- A proposed key is `ab2026__` or `ab2026_option__` followed by lower-case words joined by single underscores, and NOTES scopes it as a whole token.

## Families staged

12 families, 5,952 rows (450 `restated`), as `COUNTS.json` pins them.

| family | rows | primaries | producer slugs |
|---|--:|--:|---|
| `uk_centax` | 112 | 6 | `centax` |
| `uk_devolved_govts` | 19 | 2 | `scottish_government`, `welsh_government` |
| `uk_hmt_costings` | 597 | 1 | `hm_treasury` |
| `uk_hmt_redbook` | 425 | 6 | `hm_treasury` |
| `uk_hmt_tables` | 768 | 2 | `hm_treasury` |
| `uk_ifs_ab2026` | 144 | 14 | `ifs` |
| `uk_ippr` | 3 | 3 | `ippr` |
| `uk_obr_tables` | 2,800 | 4 | `obr_efo` |
| `uk_rf_ab2026` | 766 | 8 | `resolution_foundation` |
| `uk_thinktank_misc` | 12 | 5 | `citizens_advice`, `cps`, `institute_for_government`, `learning_and_work_institute` |
| `uk_tpa` | 305 | 10 | `tax_policy_associates` |
| `uk_trussell_wpi` | 1 | 1 | `trussell_wpi` |

Each family's `stage.py`, which writes its claims file, is kept on branch `uk/ab2026-harvest-staging` under `harvest-staging/ab2026/lanes/<lane>/<family>/`, with the lane briefs and the five reviews; this branch carries only each family's three files, as AB2025 does. On 3 November 2026 we applied the review fixes, all four sections of the IFS addendum and the cross-family key harmonisation, and each family's NOTES.md records them. On 4 November we applied reviews A and B of 4f424b9 (the registry, the HM Treasury families and the harness; the OBR, Resolution Foundation and think-tank families), and each NOTES.md records those too.

**Families with no rows** are not carried here, as AB2025 has no empty family. Their working files stay on the staging branch:

- `uk_cpag`: both CPAG pages (its Budget response and a pre-Budget call) returned Cloudflare's challenge (HTTP 403) to every fetch on 29 October.
- `uk_smf`: the Social Market Foundation page returned a challenge to every fetch on 29 October.
- `uk_niesr`: NIESR's Budget-day reaction ("Breathing Space, Not a Strategy") was fetched, but it holds macro and fiscal-stance commentary for the #55 lane and restated OBR figures, which the AB2025 NIESR family did not stage either.
- `uk_fai_sfc`: the Fraser of Allander Institute's reaction refused the fetch (HTTP 403), and the Scottish Fiscal Commission published nothing in scope on 28 or 29 October. The reaction's feed text holds only restated OBR figures. A second FAI post, "Rising or falling? Why both claims about Scotland's funding can be true" (29 October), was found on 4 November through FAI's RSS feed and sits behind the same 403. Its table of Scotland's Barnett consequentials is not staged: FAI says the split emerged late on 28 October, so it probably restates HM Treasury's allocations, which `uk_hmt_redbook` rows 258–261 stage. The Scottish Government's five rows, first staged here, moved to `uk_devolved_govts` on 3 November.

## Producer slugs and families

| slug | producer | family dir |
|---|---|---|
| hm_treasury | HM Treasury: Tables 6.1, 6.2 and 6.4 | uk_hmt_tables |
| hm_treasury | HM Treasury: policy costings (static and post-behavioural legs, tax bases, behavioural parameters) | uk_hmt_costings |
| hm_treasury | HM Treasury: Budget 2026 document, Impact on households, Pension Tax Allowance explainer | uk_hmt_redbook |
| obr_efo | OBR: Economic and fiscal outlook, October 2026, and its detailed tables | uk_obr_tables |
| resolution_foundation | Resolution Foundation | uk_rf_ab2026 |
| ifs | Institute for Fiscal Studies | uk_ifs_ab2026 |
| tax_policy_associates, centax, ippr, cps, institute_for_government, learning_and_work_institute, citizens_advice | other producers, each in the AB2025 family of the same name where one exists | uk_tpa, uk_centax, uk_ippr, uk_thinktank_misc |
| cpag, smf, niesr, fraser_of_allander, scottish_fiscal_commission | producers with no rows (see "Families with no rows"); their working files are on the staging branch, not here | none |
| scottish_government, welsh_government | the devolved governments' responses | uk_devolved_govts |
| trussell_wpi | Trussell, as in AB2025 | uk_trussell_wpi |
| commercial firms and platforms | worked examples (mode 3, #63); none was staged for AB2026 | none (AB2025: uk_cases_commercial) |

Macro calls by banks and City forecasters belong to the #55 lane and are not staged here (AB2025 rule 10).
