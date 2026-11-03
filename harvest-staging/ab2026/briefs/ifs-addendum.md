## Your assignment: extend and rework family `uk_ifs_ab2026` (source `ifs`)

An earlier lane staged `sources/harvest-uk-ab2026-2026-10-29/uk_ifs_ab2026/` in this worktree: 106 rows from the four 29 October briefing decks, with `stage.py`, `manifest.jsonl` and `NOTES.md`. Its report is at /Users/maxghenis/reviews/scorecard-ab2026-harvest/out/ifs.md. It could not reach the IFS web pages, which return Cloudflare 403 to curl. You now have the text of two of them, and the README has two new rules. Edit that lane's `stage.py` and re-stage the family. Keep everything that still passes.

### 1. Add the two IFS pages read in a browser

The coordinator read these pages in the Claude desktop app's built-in browser between 16:56Z and 16:58Z on 29 October, and saved the text of each page's `<main>` element. Read `/Users/maxghenis/reviews/scorecard-ab2026-harvest/local-primaries/ifs/browser/README.md` first; it explains why the text, not the HTML, is the primary.

| file | page | text sha256 |
|---|---|---|
| ifs-initial-response-main.txt | https://ifs.org.uk/articles/autumn-budget-2026-initial-response (published 28 October 2026) | 962f737e4dfb70416f76a7fc3104f9c4d6b04ef6566a58e0e55fd9db709136ff |
| ifs-collection-opening-remarks-main.txt | https://ifs.org.uk/collections/autumn-budget-2026 (Helen Miller's opening remarks, as the collection page prints them) | 5991ccec0e0ebb90952937f23400039a8386c047a4b44c9cd4391f535504723c |

- Copy both files into `.ab2026-primaries/uk_ifs_ab2026/browser/` and confirm the hashes.
- Add a manifest line for each, with `access: "browser text"`, `doc_type: "web page text"`, and a `note` giving the page URL, the read time, the HTML byte count and HTML sha256 from the README, and the reason (Cloudflare 403 to curl; per-request tokens make HTML hashes unstable).
- Don't try to fetch ifs.org.uk yourself. It refuses curl, and you must not get round that.
- Stage what these pages print under the rules below. Examples of what they hold:
  - headroom of £13 billion, and £15 billion in 2029–30 after the decisions (OBR figures IFS restates);
  - giveaways pushing up borrowing by £8 billion this year and £4 billion next year;
  - a top-up of £17 billion needed to avoid real-terms cuts, printed as "in 2030-21" (sic). Stage it as printed, set `parse_confidence: "medium"` and say in `note` that the year is a typo, probably for 2030–31. Don't correct it;
  - £11 billion needed to fund defence plans;
  - 25% of the capital reserve and 40% of the day-to-day reserve already spent (the Boileau deck may already carry one of these; cite each document's own row);
  - the £100 payment reaching around 80% of households in England. 80% is a row (households affected); £100 is the payment's design and goes in `reform_hint`.
- "98 measures" is a count of the Budget's measures. Stage it with `proposed_metric: "measure_count"`, `measure_key: null` and no proposed key, as the AB2025 `uk_thinktank_misc` family staged its measure counts.
- Defence targets (3% of GDP by 2030, 3.5% by 2035, 2.7% next year), "35 years out of date" and "100% of business rates" are design, targets or descriptions, not estimates of an effect. Don't stage them, and count them in NOTES.md's not-staged section.

### 2. Add the seven IFS data items

`/Users/maxghenis/reviews/scorecard-ab2026-harvest/local-primaries/ifs/browser/data-items.json` lists the seven charts in the collection's "Key charts: charts with downloadable data" section, each with its page URL, lead sentence and Flourish visualisation id. The data-item pages on ifs.org.uk refuse curl, but public.flourish.studio answers.

- For each id, fetch the Flourish visualisation's public page or embed (for example `https://public.flourish.studio/visualisation/<id>/` and the embed it points to, such as `https://flo.uri.sh/visualisation/<id>/embed`). Find the chart's data as Flourish serves it, the data the IFS page offers as its download. Save the bytes you read from under `.ab2026-primaries/uk_ifs_ab2026/flourish/`, hash them and add one manifest line per visualisation with the IFS data-item URL, the Flourish URL you read, `access: "flourish public data"` and the lead sentence in `note`.
- If a visualisation's data can't be read, list it as unreached in NOTES.md. Don't scrape a screenshot or read bars.
- Stage values that are about the Autumn Budget 2026 forecast or measures:
  - October 2026 forecast values, and the March 2026 forecast values where the chart compares the two, as restated OBR figures (`attribution: "restated"`, `note` naming the OBR EFO), unless IFS computed them itself;
  - IFS's own calculations, such as decade or parliament averages of real household disposable income growth, as `own`;
  - the Budget's own entry in "long-term impact of announced tax changes at each fiscal event". Earlier fiscal events in that chart are about other events: don't stage them, and say so in NOTES.md.
- Historical outturns in these charts are context and are not staged, except a value the lead sentence itself states as the finding (for example the 2020s value in the decade chart).
- Each data row quotes the data cell with its row and column labels, for example `"2029-30, October 2026 forecast: 0.4"`, so `quote` contains `value_raw`. `locator` names the visualisation id, the series and the row. Follow how the AB2025 families quote spreadsheet cells.
- Context figures that concern no measure get `measure_key: null` and no proposed key (the AB2026 README's rule 2 and the row rules above).

### 3. Re-check all rows against README rules 8 and 9

Rules 8 and 9 in `sources/harvest-uk-ab2026-2026-10-29/README.md` postdate the earlier lane. Re-read them, then re-check every existing row:

- **Rule 8:** drop rows whose value is a measure's design. Row 106 (Adam slide 5, the 0% electricity VAT rate) is one; look for others (rates, thresholds, payment amounts, dates, durations, spending allocations, financing remits). A dropped design number may move into another row's `reform_hint`.
- **Rule 9:** a row about part of one Table 6.1 measure carries that measure's key, with `conditions.component` and `conditions.row_type: "measure_component"`. The earlier lane proposed `ab2026__package_ifs_hmrc_compliance_staff_and_debt_collection` for a subset of line 45; that becomes line 45's key as a component. Check the other six proposed keys the same way:
  - `self_assessment_payment_timing` ("no distinct line established"): look again in `REGISTRY_KEYS.md` for the self-assessment payment-timing line; if one line matches exactly, key it there.
  - `defence_investment_plan_funding`: a funding gap IFS estimates is an estimate, but if no Table 6.1 line or cross-line scope matches, it is a context figure (`measure_key: null`, no proposed key). Decide, and say why in NOTES.md.
  - `cost_of_living_support` ("lines 1 and 3, plus full October–June electricity VAT relief including previously announced support") and `electricity_vat_oct_2026_june_2027` ("line 2 extension plus previously announced VAT relief"): README rule 3's example was wrong and is now corrected. Table 6.1 line 2 costs the whole VAT cut from 1 October 2026 to 1 July 2027, including the weeks before the Budget. So a figure for exactly the energy payment, the VAT cut and the fuel duty cut takes `ab2026__package_household_energy_vat_and_fuel_duty`. A figure for the whole VAT cut takes line 2's key, `ab2026__electricity_vat_zero_rate_to_july_2027`. Check IFS's words and figures for each row before re-keying, and keep a proposal only where the scope truly differs.
  - `savings_and_property_income_tax` (exactly lines 61 and 62) becomes `ab2026__package_property_and_savings_income_rates`, the name README rule 2 gives that scope.
  - `gas_standing_charge_reallocation` is a measure with no Table 6.1 line, so under rule 2's naming it is `ab2026__gas_standing_charge_moved_to_unit_rates`, the spelling the RF family uses.
- Keep the five deck primaries and their manifest lines as they are.

### 4. NOTES.md and verification

- Rewrite NOTES.md's coverage tally (rows per primary and per measure_key, including null), the proposed keys and their scopes, the access recipe (add the browser text and Flourish routes) and the not-staged section. Add a "Not staged (rules 8 and 9)" subsection with counts and examples. The explainer and the fiscal devolution comment are no longer unreached: the browser README records that they hold no estimates, so say that instead.
- Remove any report or spot-check file the earlier lane left that is now stale.
- Verify as the common instructions say: the contract checker reports 0 problems, a re-run of `stage.py` reproduces the gzip byte for byte, and 15 random rows, at least five from the new primaries, re-opened at their locators match on value, sign, unit and period.

Write only inside `sources/harvest-uk-ab2026-2026-10-29/uk_ifs_ab2026/` and `.ab2026-primaries/uk_ifs_ab2026/`. Don't commit or push.

### Report

- Rows before and after, by primary and by measure_key (including null).
- Rows added, dropped (by rule and category) and re-keyed.
- Proposed keys left, with scopes.
- Flourish visualisations read or unreached.
- The checker output and the 15-row spot check.
- Anything in the primaries that looks wrong or contradictory. Report it; don't fix it.
