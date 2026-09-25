# CeMPA WP 3/26 (Frimpong, Feb 2026) — second-pass extraction notes

Source: `cempa3-26.pdf`, sha256 `7c3f48bda8f213f933b153482c50be58c5e0d8a86b49257359876c64dec6097a`
(verified). Text is extracted with `pypdf` (35 PDF pages) by the vendored extractor
`tools/extract_second_pass.py` (re-runnable: `uv run --with pypdf python tools/extract_second_pass.py <cempa3-26.pdf>`
against the primary fetched from the manifest URL; it asserts the cell counts and re-runs the
verbatim check). Output: 302 rows, one per printed number, converted into this family's rows.

Printed page = PDF page - 2 (the cover and inner cover are unnumbered).

## Tables found and rows staged

- Table 4 "Income shares by decile (after housing costs, 2026 and 2030)" — PDF p.25 /
  printed p.23. 10 deciles x (2026 baseline, reform, change; 2030 baseline, reform, change)
  = 60 rows. Only 2026 and 2030 are printed, not every year 2026-2030.
- Table 4.1 "Income shares by nation - Bottom and Top Deciles (2026 and 2030, AHC)" — PDF
  p.26 / printed p.24. 4 nations x (2026 D1, 2026 D10, 2030 D1, 2030 D10) = 16 rows.
- Table 5 "Mean household income by decile ( After Housing Costs, 2026 and 2030)" — PDF
  p.27 / printed p.25. 12 rows (Decile 1-10, All, Poor) x 6 columns = 72 rows.
- Table 5.1 "Mean household income by nation (After Housing Costs, 2026 and 2030)" — PDF
  p.28 / printed p.26. 4 nations x 6 = 24 rows.
- Table 5.2 "Bottom and top decile patterns by nation (2026)" — PDF p.29 / printed p.27.
  4 nations x (D1 baseline, reform, change; D10 baseline, reform, change) = 24 rows.
  NOT explicitly requested (task named 5 and 5.1); staged as the decile twin of 5.1 and
  clearly labelled by `source_table` so it can be dropped.
- §8 "Gainers and Losers Analysis" starts PDF p.29 / printed p.27.
  - Table 6 "Distribution of gains and losses (2026 and 2030)" — PDF p.30 / printed p.28.
    11 rows (Decile 1-10, All) x (2026 gainers, losers; 2030 gainers, losers) = 44 rows.
  - share_no_change (within +/-1%): prose only, 2 rows — "91.73%" (2026, Executive Summary
    'Distribution of Impacts', printed p.4) and "90.7%" (2030, §8 intro, printed p.27).
    §8 also prints "91.7% in 2026" (same number rounded) and Key Findings prints
    "90.7 -91.7%"; neither is staged separately to avoid duplicates.
  - Table 6.1 "Household type patterns (2026 and 2030)" — PDF p.31 / printed p.29.
    7 household types x 4 = 28 rows (extra key `conditions.household_type`).
  - Table 6.2 "Gainers and Losers by Nation (2026 and 2030)" — PDF p.32 / printed p.30.
    4 nations x 4 = 16 rows.
  - Table 6.3 "Household type patterns by nation (2026)" — PDF p.33 / printed p.31.
    4 nations x (Elderly gainers, losers; With Children gainers, losers) = 16 rows.
  Tables 6.1-6.3 go beyond "overall and by decile" but are inside the section the task
  said to extract in full; filter by `source_table` if only Table 6 is wanted.

Total 302 = 60 + 16 + 72 + 24 + 24 + 44 + 2 + 28 + 16 + 16.

## Verbatim check

Every `value_raw` (302/302) is found verbatim in the pypdf text: NOT-FOUND count = 0.
Every `quote` (the full printed table row, or the prose sentence) is also found verbatim
(NOT-FOUND = 0), after joining the PDF's cell line-break in "Northern \nIreland" and, for
the two prose quotes, the line wrap inside the sentence. No number was computed or derived;
change columns are staged exactly as printed with `scenario = reform_minus_baseline`.

## Definitions as the paper words them

- Scenarios (§1 'What this analysis compares'): "The analysis compares baseline scenarios
  for each year from 2026 to 2030 under pre-Budget legislation with reform scenarios in
  which the Autumn Budget Statement 2025 policies are implemented. Each year represents a
  separate comparison between baseline and reform scenarios, with identical market incomes
  and economic conditions". UKMOD B2025.09, input data UK_2023_a2 (FRS 2023-24, income
  uprated to 2026), OBR November 2025 uprating. Static, no behavioural response (§2.4).
- Deciles (§1): "The poverty line and decile groups are held fixed at baseline levels for
  each year." "All monetary values are expressed in nominal terms for each respective
  year." §6: "Income shares show what percentage of the UK's total disposable income goes
  to each group." The paper does NOT state whether deciles are of households or
  individuals, nor the equivalisation scale; Table 4.1/5.2 nation deciles read as
  within-nation deciles (not stated either).
- Mean income (§7): "Mean household income shows average weekly income across the
  distribution. After housing costs (AHC), see Table 5, captures disposable income
  available after meeting housing expenses". Table 5 levels are printed to whole £/week;
  the Executive Summary gives Decile 1 2026 as "£158.75 per week to £159.19 per week", so
  the printed Change column (to the penny) is the paper's figure, not reproducible from
  the rounded levels.
- Gainers/losers threshold (§8): "This analysis identifies households experiencing income
  changes exceeding 1% or 5% thresholds after housing costs. Gainers see income increases
  while losers experience income decreases from the reform." Executive Summary: "Only
  1.78% of UK households are estimated to gain more than 1% of equivalised disposable
  income in 2026, while 6.49% experience losses exceeding 1%". Staged as
  `conditions.threshold = 1_percent_of_equivalised_ahc_disposable_income` with the paper's
  wording in `conditions.note`. The 5% threshold has no table; the only 5% statement is
  qualitative (lone parents / 3+ children: "all gainers experiencing income increases
  exceeding 5%").

## Conventions used

- `period` = FY END year per the task brief (paper "2026" = UK_2026 policy system =
  FY 2026-27 -> period 2027, `conditions.fy = "2026-27"`; "2030" -> 2031, "2030-31").
  The first pass staged this same paper's Tables 1-3 with FY START periods in
  `sources/harvest-uk-2026-08-02/uk_ukmod_jrf/`; this family converts those rows to FY END
  periods (NOTES.md, "Conversion"), so both passes agree here.
- `geography`: "UK" for UK tables; "England" / "Scotland" / "Wales" / "Northern Ireland"
  for nation tables (first pass used lowercase "uk").
- `income_group`: decile_1..decile_10, all, plus "poor" for Table 5's "Poor" row (not in
  the enumerated set; paper does not define it in §7 — read as households below the
  fixed AHC poverty line used in §4; medium confidence).
- `housing_costs = "ahc"` wherever the table title or its section says so; omitted for
  Table 5.2 (title silent; context is AHC, see row notes; medium confidence).
- `source_column` is the printed header; where the header prints a bare "Change" under a
  year block (Tables 5, 5.1) the year prefix is added ("2026 Change").
- Percentages -> share (/100); "0.00pp" -> 0.0 percentage_points; "£1,028" -> 1028
  gbp_per_week; "+£0.44" / "-£1.55" -> 0.44 / -1.55 gbp_per_week.
- `parse_confidence`: high for 240 rows; medium for Table 4.1 (scenario not labelled),
  Table 5 "Poor" row, Table 5.2 (housing basis not stated) and Table 6.3 (">1%" not
  repeated in the column header).

## Ambiguities and things not staged

- Table 4.1 has no baseline/reform columns. §6.1 says reform changes round to zero at
  this precision ("largest change is Northern Ireland's Decile 4 (+0.012 percentage
  points), while most deciles show changes under 0.002 percentage points"), so the printed
  values serve for both scenarios; staged once as `scenario = baseline`, medium confidence.
- Share within +/-1% BY DECILE exists only as Figure 3 (chart, PDF p.30) — not readable
  from text, not staged. Figures 3.1 and 3.2 (household type / nation charts) likewise.
- Prose-only numbers not staged: the §6.1 income-share gaps (17.47pp, 24.60pp, 19.28pp,
  22.04pp, 25.02pp, 17.57pp, 7.03pp — paper-computed differences), the "+0.012 percentage
  points" NI Decile 4 change and "<0.002" (no table), the Executive Summary's more precise
  Decile 1 2026 levels "£158.75" -> "£159.19" and the annualised "+£23" / "-£14", and the
  §7 uprating growth figures (+£0, +£45, +£175, +£105/week, 14%). Executive Summary and Key
  Findings restatements of Table 6/6.1 cells (1.78%, 6.49%, 1.42% v 0.20%, etc.) duplicate
  table cells and are not staged again.
- Title-year quirk carried from the first pass: WP cover says "Autumn Budget Statement
  2026", inner cover and body say "2025"; the measures are the November 2025 Budget.
- "Poor" row in Table 5 and Tables 6.1/6.3 household types ("With Children", "Lone
  Parent", "Three+ Children", "Elderly", "No Earners", "Disabled", "Two+ Earners") are
  undefined in the paper; staged with labels as printed.
