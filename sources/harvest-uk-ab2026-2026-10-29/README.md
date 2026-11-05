# Harvest: Autumn Budget 2026 scores from every producer (#230)

We began staging this harvest from the primary documents on 29 October 2026, the day after the Budget. We lay it out as in the AB2025 harvest (`sources/harvest-uk-ab2025-2026-09-24/`):

- One family directory per producer group.
- Each family's directory contains:
  - `NOTES.md`: how we fetched each primary, a tally of what we staged, and what we left out and why;
  - `manifest.jsonl`: one line per primary document, with its sha256;
  - `claims_staged.jsonl.gz`: one line per claim.
- In `COUNTS.json`, we pin each family's rows, primaries, producer slugs and the sha256 of its claims file. `pipeline/harvest_counts.py` writes and checks it.
- `pipeline/build_ab2026_registry.py` writes `REGISTRY_KEYS.md`, a list of every measure key.
- `pipeline/ab2026_proposed_keys.py` writes `PROPOSED_KEYS.md`, a list of every proposed key on a row (rule 2). We register those keys in tranche 2.
- In `SEED_INVENTORY/`, we list the publications we started from, which we gathered while we monitored reactions on 28 and 29 October.

No code reads this harvest yet; we add the ingest in tranche 2 of #230. In its accounting, the ingest will require `read = ingested + dropped` exactly, against the rows we pin in `COUNTS.json`. `tests/test_uk_ab2026_harvest.py` checks every row against the contract below.

## Rules

We follow the AB2025 harvest README's rules 1–10 and its row contract, with the AB2026 exceptions and additions below:

1. **We set `fiscal_event` to the slug `autumn_budget_2026`** on every row, whatever each producer calls the Budget.
2. **We take measure keys from `data/uk/ab2026_measures.json`.**
   - We give `ab2026__…` keys to announced measures: every HM Treasury Table 6.1 line, Table 6.2 line 4, and the `ab2026__package_…` packages.
   - We give `ab2026_option__…` keys to options a producer costed, and we haven't registered any yet. On a row for an unregistered option, or for a package whose scope matches no registered package, we set `measure_key: null`. We put its proposed key in `conditions.proposed_measure_key`, state the key's scope in the family's NOTES, and add the key to the registry before the ingest.
   - We make one exception, for Table 6.4's recostings: we give each the earlier event's key, and name that event in `conditions.recosting_of`.
   - **We name proposed keys this way:**
     - We key an announced measure with no Table 6.1 line `ab2026__<slug>`, and name the measure in the slug. We use this form for a measure below Table 6.1's £10m threshold, a fiscally neutral measure and one whose only costing appears elsewhere.
     - We key a package `ab2026__package_<slug>` and name its scope in the slug, not its producer, so that producers with the same scope share one key. For example, we key lines 61 and 62 together as `ab2026__package_property_and_savings_income_rates`. We put a producer's or the OBR's name in the slug only for a grouping of its own, such as `ab2026__package_tpa_other_vat`.
     - We key an option a producer costed `ab2026_option__<slug>`.
     - Before we merge, we give each scope one key across families, and `pipeline/ab2026_proposed_keys.py` lists the result in `PROPOSED_KEYS.md`.
3. **We use the producer's scope for a measure, not ours.** We key a producer's figure for "the cost-of-living package" to `ab2026__package_household_energy_vat_and_fuel_duty` only when its scope matches Table 6.1 lines 1, 2 and 3. Otherwise, we give it a proposed key (rule 2).
   - In line 2, HM Treasury costs the whole electricity VAT cut, from 1 October 2026 to 1 July 2027 (£755m in 2026-27 and £305m in 2027-28), including the weeks before the Budget. So a package of the energy payment, the VAT cut and the fuel duty cut matches lines 1, 2 and 3. If a producer's package also counts the gas standing-charge change, which has no Table 6.1 line, we give it a proposed key.
4. **We don't read bars off HM Treasury's Impact on households Figures 1.A and 1.B** (AB2025 rule 9, #61). We stage the numbers HM Treasury prints in text, tables or data labels, at the values it prints.
5. **We don't harvest PolicyEngine's own published figures here.** In tranche 3, we compute them from the dashboard's receipts and add them as counterparts. When a producer restates a PolicyEngine figure, we stage its row with `attribution: same_assumptions`, as we did for the Fabian Society's row in AB2025.
6. **We keep quotes from producers outside the Open Government Licence short.** In `quote`, we cut the sentence or cell with the number down to the phrase around it: under 15 words for think tanks, firms and the press. HM Treasury and the OBR publish under the OGL, so we quote their cells and sentences whole.
7. **We treat a changed primary as a second primary.** If a producer replaces a document, we hash both versions in `manifest.jsonl` and cite, on each row, the version we read it from. IFS replaced its cost-of-living deck on 29 October, and HM Treasury replaced the Budget 2026 document PDF after 28 October. We record what changed in the family's NOTES.
8. **Stage estimates, not design.** We stage as a row each number someone estimated, forecast or counted about the effect of a measure or of the Budget, including:
   - a cost or yield;
   - people or households a measure affects;
   - a gain, loss or bill change;
   - a distributional or poverty effect;
   - a behavioural adjustment or tax base;
   - a fiscal aggregate;
   - a consequential for a devolved government.

   We treat as design a measure's own parameters (rates, thresholds, payment amounts, dates and durations), spending allocations to programmes, financing remits and contingent liabilities. We put design in `reform_hint` or `conditions`, never in rows, as we kept "£9.90" in `reform_hint` in the AB2025 red book family. We treat a worked example's inputs as design too, and stage the outcome its producer computes as a row.

   We apply one rule to lending and financing across families. We stage HM Treasury's Tables 6.1, 6.2 and 6.4 and the OBR's policy workbook whole, as the decisions' costings. Elsewhere, we treat an amount a scheme will lend or spend as design, and an effect on borrowing, debt or the financing requirement as an estimate. So we leave out the OBR's paragraph 3.22 loan volumes for Your First Home but stage its effect on debt, and we stage paragraph 3.20's rise in the Government's financing requirement on `cash_requirement_change`.
9. **We give a component of one measure that measure's key.** On a row with a printed part of one Table 6.1 measure, we set that measure's key, name the part in `conditions.component` and set `conditions.row_type: measure_component`. We count a fiscal head, a sub-measure within a line (the tax-gap package's items, for example) or a nation as a part. We never sum components with the measure's total. We propose package keys for scopes that cross Table 6.1 lines, or have none.
10. **We give a producer's stated effect of the Budget's decisions on PSNB `decisions_effect_on_borrowing`.** We give it to the total effect of Government decisions, its direct and indirect effects and any part of them the producer identifies, and its splits into tax and spending and into scorecard and non-scorecard decisions. We also give it to any figure a producer derives, without ambiguity, by restating or recombining those effects. `models.py` defines the metric as PSNB and keeps it apart from `revenue_change`, a receipts line. `ingest_obr_policy_effects.py` maps March 2026 Table B.1's totals, its direct effects and their tax and spending split to it. HM Treasury sets out in Table 6.1 the cost or yield of the decisions "which have a direct effect on Public Sector Net Borrowing". So we give the metric to Table 6.1's three totals and to any producer's restatement of them.

    We keep `revenue_change` on a receipts total or a tax-change estimate unless its evidence establishes PSNB scope, and we don't take a total key or a package label alone as that evidence. The OBR sums its receipts heads, from air passenger duty to visa fees, into its policy workbook's total of receipts measures, so we keep `revenue_change` on that total. IFS doesn't tie its own estimate of the Budget's tax change at the forecast horizon to PSNB, so we keep `revenue_change` on that estimate too. `ingest_uk_ab2025.py` maps AB2025's `package_tax_rise_size` rows to `revenue_change` as well.

    We keep `revenue_change` on single measures, groups of measures and a total's lines by tax or spending head, unless their producer states the effect on borrowing. The OBR states it for four policies in paragraphs 3.20, 3.21 and 3.43, and IFS for the Budget's new giveaways. When a producer restates a Table 3.1 group or a single measure as an effect on borrowing, we give the restatement the metric of the row it restates. For example, in paragraph 3.11 the OBR restates Table 3.1's other departmental spending changes with "increase borrowing by £5 billion in 2026-27", and we keep `revenue_change` on both. We read Table 3.1's "A positive sign implies an increase in borrowing" as a sign convention, not a statement of PSNB scope.

    When a producer adds to a total the receipts effect of an option the Government didn't adopt, we don't count the result as a restatement or recombination of the decisions' effects. We keep `revenue_change` on it unless its evidence establishes PSNB scope. For example, in Figure 10's "Net effect if Fuel Duty frozen", Resolution Foundation adds a continued freeze's receipts effect, which it derives in a note from the OBR's constant-duty-rate fuel duty forecast. The OBR states the freeze's effect on borrowing for 2029-30 only (paragraph 3.43).

    On a row with the effect on the current budget deficit (or, for an outturn, the primary deficit), we propose `fiscal_balance_change` and name that deficit in the sign convention. We keep the sign each producer prints, and state in `conditions.sign_convention` which way it runs.

## Row contract additions

`pipeline/ab2026_harvest_contract.py` checks the AB2025 row contract with these additions:

- The checker accepts `value_kind: categorical` for a rating with no digits, such as the OBR's Table 3.3 uncertainty ratings.
- It requires a finite number in `value`. Unless the row has `value_kind: categorical`, it reads `value_raw` only if the whole string, in any case and spacing, matches one of the forms listed here. It reports any other string as a problem, and we narrow `value_raw` to the number, which `quote` still contains: "£5" from "£5 in 10 years", or "1 in 4" from "2025, 1 in 4". It reads:
  - digits, with a sign, a currency sign or both, and one multiplier (k, m, mn, bn, tn, hundred, thousand, million, billion, trillion) or percentage word (%, per cent, percent, percentage point or points, pp, ppt, ppts): "-£1.7bn", ".5", "4%";
  - number words up to nine hundred and ninety-nine, with a sign and one multiplier or percentage word: "four", "-four", "a hundred and five", "two hundred thousand", "a million", "four per cent";
  - a worded fraction: "half" alone, or a numerator ("a", "an", "another", or one to ten) and a denominator from "half" to "tenth" ("a third", "three-fifths"), with a sign if printed ("-three-fifths");
  - a worded fraction of a multiplier or percentage: "half a million", "a quarter of a percentage point", "half per cent";
  - a whole number and a fraction, with the whole number in digits or in words up to nine hundred and ninety-nine. A percentage word may follow, and so may a multiplier other than "hundred" after a space or hyphen: "two and a half", "one and a half million", "2 and a half bn", "one hundred and a half";
  - a ratio of two numbers, in digits or number words, with at most one multiplier each: "1 in 4", "1 in 2 million". The checker takes "in", "in every", "out of" or "out of every" between them, with spaces or hyphens throughout: "3 out of 10", "one-in-every-ten";
  - a range: two figures joined by a dash, with no spaces or a space on each side ("£4-5 million", "4 – 5%"), or two numbers joined by "to" ("four to five", "4bn to 5bn");
  - "nil", "none", "nothing", "no change", "no impact" or "no overall impact", as zero. It also reads a dash as zero where we say, in one whole clause of `normalization`, that the producer prints it for nil. It accepts forms such as "dash for nil" and "the table prints nil as a dash". A comma, semicolon, full stop or bracket ends a clause.
- It also reads a qualifier before the number ("about", "up to" and the others in `QUALIFIERS`), "a" before digits ("less than a 0.1 percentage point"), and "a year" or "of GDP" after the number. It reads a ratio or worded fraction with its percentage in brackets, in either order, if the two agree to the nearest percentage point: "one third (33%)", "25% (1 in 4)". It matches `value` to either number there or in a range. It reports a range that joins a percentage to a multiplier ("4% to 2 million") or a fraction to a percentage ("a third to 40%"). It also reports a range whose first number exceeds its second, unless neither is positive: it reports "2025-26" and "2 to -3", and reads "-4 to -5". After a bare "in", it reports a year from 2010 to 2099 ("5 in 2027").
- It takes each number's scale from its own word (bn, million, %). When only a range's second number has one, it gives that word to the first number too. When digits, number words or a whole number with a fraction have no word of their own, it uses the factor in `normalization`, failing that 1. It reads a factor whole ("x 1,000,000", "/ 100", "(x 10^6)"), multiplies operations in a row ("x 1,000,000 / 100" as 10,000), and takes either factor where a semicolon or a word separates two. It reads x, ×, *, / or ÷ as a factor wherever a number follows, at the note's start or after a space or bracket. It ignores a slash between digits ("2/3", "2026/27"), and we write "page 3 of 4" rather than "page 3 / 4". At any value, it reports "x 1 million", "x (1e6)", "x one million", "times 1,000", "multiply by 1,000,000" and "£m×1e6". It reads a percentage as a share or in percent units, and requires digits and number words to match `value` within four units in the last place.
- It reads a ratio or a worded fraction on its own as a share, and accepts a `value` within 0.1% of that share. On a `unit_concept: percent` row, it requires 100 times the share instead ("1 in 4" as 25). It won't match `value` to either of a ratio's numbers alone, and it reads "-1 in 4" and "1 in -4" as −0.25. It also allows 0.1% on a whole number with a fraction, and on a fraction of a multiplier or percentage.
- It requires `value` to share `value_raw`'s sign unless we note in `normalization` that we took the sign from the wording.
- It treats an HM Treasury Impact on households row as a bar reading (rule 4) if the row has `value_kind: approx_chart_reading`. It does the same if we mention a bar, chart, graph, plot, diagram or visual in the locator, in any spacing and with or without hyphens. "Off" or "from" up to four words before a figure there counts too. So does a note that we read, took, estimated or measured the number using, on, in or of a figure, or read it by eye. It reads "Fig." and "Figs." as figures and looks past a colon, brackets or quotes before them. It counts "read off Fig. 1.A", "read off: Fig. 1.A" and "read from [Figure 1.A]". It counts "column 3 of Figure 1.A" and leaves "Table 2.1, column 3" alone. It ignores such a phrase right after one "no", "not", "never", "without", "cannot" or "n't" ("not a bar reading"). It counts the phrase after two negations in the same clause ("not possible without reading off the chart").
- When we cite Figure 1.A or 1.B on those rows ("Fig. 1A", "Figure 1(a)", "Figures 1.A and 1.B"), it reads the locator up to the first comma or semicolon. Before that point we must name a paragraph, table or box by number, or a data label. It accepts "paragraph 1.7", "paragraphs 1.7–1.8", "Tables 2.B and 2.C", "Table 2.C and Figure 1.A", "Figure 1.A data label" and "data label for decile 3". It treats any other wording as a bar reading, including "Figure 1.A data label unavailable" and "Figure 1.A, decile 3 bar; see paragraph 1.7".
- It reports a malformed row as a problem, never as an exception: a row that isn't an object, lacks a field, or has a field of the wrong type. It requires:
  - a string in `source`, `source_model`, `value_raw`, `normalization`, `quote`, `status`, `value_kind`, `time_basis`, `attribution`, `benchmark_class` and `parse_confidence`;
  - a string or null in the other text fields, such as `measure_key`, `reform_hint` and `source_table`, and in each `publication` field;
  - an integer in `period`, a number in `value`, and an object in `conditions` and `publication`, with a string in each condition.

  It also reports a line it can't parse as JSON, or a file it can't read, as a problem. When it compares rows, it skips any value it can't compare, such as an integer too large for a float.
- It treats a row with `conditions.component` as a part of one measure (rule 9), and requires `row_type: measure_component`, or the OBR workbook's `measure_total` marker, and a non-blank component.
- It allows at most two non-restated, non-categorical rows to share the AB2025 ingest's claim identity, and requires two that do to agree within 0.5%.
- It requires a registered metric in `metric`, never in `proposed_metric`.
- It accepts `conditions.recosting_of` only on `row_type: recosting` rows (Table 6.4).
- It requires `conditions.fy` to name one fiscal year, and `conditions.horizon` on a `fiscal_year` row without `fy`.
- It accepts only a code in `conditions.geography`: UK, GB, England, Wales, Scotland, Northern Ireland, England and Wales, UK_excl_scotland, "Scotland, Wales and Northern Ireland", "not stated", or a country a producer compares the UK with. Put prose in `conditions.geography_note`.
- It requires a `note` on each restated row with the name of the original figure's producer, and rejects a blank one.
- It requires a proposed key of the form `ab2026__…` or `ab2026_option__…`, with lower-case words of letters and digits after the prefix and single underscores between them. It looks for the whole key in the family's NOTES, where we state its scope.

## Families staged

We pin 12 families and 5,952 rows (450 `restated`) in `COUNTS.json`.

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

Each family's `stage.py` writes its claims file, and we keep it on branch `uk/ab2026-harvest-staging` under `harvest-staging/ab2026/lanes/<lane>/<family>/`, with the lane briefs and the review records. We record each family's review changes in its NOTES.md, and keep only its three files here, as in AB2025.

We leave the **families with no rows** out, since AB2025 has no empty family, and keep their working files on the staging branch:

- `uk_cpag`: Cloudflare answered every fetch of both CPAG pages (its Budget response and a pre-Budget call) with its challenge (HTTP 403) on 29 October.
- `uk_smf`: the Social Market Foundation's site answered every fetch of its page with a challenge on 29 October.
- `uk_niesr`: we fetched NIESR's Budget-day reaction ("Breathing Space, Not a Strategy"), but in it NIESR gives macro and fiscal-stance commentary for the #55 lane and restates OBR figures, and we staged neither in the AB2025 NIESR family.
- `uk_fai_sfc`: the Fraser of Allander Institute's site refused our fetch of its reaction (HTTP 403), and the Scottish Fiscal Commission published nothing in scope on 28 or 29 October. In the reaction's feed text, FAI only restates OBR figures. On 4 November, we found a second FAI post through FAI's RSS feed, "Rising or falling? Why both claims about Scotland's funding can be true" (29 October), behind the same 403. We leave its table of Scotland's Barnett consequentials for tranche 2. FAI says the split emerged late on 28 October, so in the table FAI probably restates HM Treasury's allocations, which we stage in `uk_hmt_redbook` rows 252–255 (paragraphs 4.150, 4.154, 4.157 and 4.160). We stage the Scottish Government's five rows in `uk_devolved_govts`.

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
| cpag, smf, niesr, fraser_of_allander, scottish_fiscal_commission | producers with no rows (see "families with no rows"); we keep their working files on the staging branch, not here | none |
| scottish_government, welsh_government | the devolved governments' responses | uk_devolved_govts |
| trussell_wpi | Trussell, as in AB2025 | uk_trussell_wpi |
| commercial firms and platforms | worked examples (mode 3, #63); we staged none for AB2026 | none (AB2025: uk_cases_commercial) |

We leave macro calls by banks and City forecasters to the #55 lane and don't stage them here (AB2025 rule 10).
