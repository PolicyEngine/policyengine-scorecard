# Autumn Budget 2026: PolicyEngine's Budget-day artifacts

We vendor these files from the UK Autumn Budget dashboard
(`PolicyEngine/uk-autumn-budget-dashboard-2026`) at commit `1eca3182`, the
commit `data/uk/ab2026_measures.json` pins for each `pe_modifier` measure.
Each folder keeps the dashboard's `public/data/artifacts/<run>/<hash>/` path.

- A `receipt.json` for each of the seven measures and for their combined
  run. Each receipt records policyengine 6.11.1, policyengine-uk
  2.151.0 and the Microcosm UK cut of 25 October 2026, the pair
  `data/uk/certified_pairs.json` records.
- `budgetary_impact.csv` for the five measures whose exchequer claims take a
  counterpart, and `age_impact.csv` for the Pension Tax Allowance.

`MANIFEST.json` gives each file's sha256, source path and source commit.
`pipeline/stage_uk_ab2026.py vendor` writes it, and checks each receipt
against the registry and each CSV against its receipt.

`pipeline/stage_uk_ab2026.py stage` pairs each AB2026 claim on these measures
with one cell, or tallies a reason. It writes the counterparts to
`results/uk/staged_ab2026/`, the counts to `STAGING_TALLY.json` and one line
per unanswered claim to `STAGING_UNANSWERED.jsonl`.
`pipeline/stage_uk_ab2026_expected.json` pins the counts, and the file,
column and row each paired claim reads.
