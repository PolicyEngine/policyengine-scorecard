
## Your assignment: families `uk_tpa`, `uk_centax`, `uk_ippr`, `uk_cpag` and `uk_smf`

Verify these five families under `sources/harvest-uk-ab2026-2026-10-29/`. Ignore `uk_hmt_tables`, except as the reference for Table 6.1.

- **Rows:** TPA 306, CenTax 110, IPPR 3. CPAG and SMF hold none: Cloudflare challenged both, and the coordinator's ordinary browser visit didn't clear either.
- **Sample:** TPA 50, CenTax 30, and every IPPR row.

**TPA:**
- TPA groups Table 6.1's tax lines in its charts without publishing the mapping. The lane recovered the mapping by matching values, and reports two things:
  - each by-year group reproduces TPA's figures exactly in all six years, and the groups partition the 53 tax lines;
  - fitted deflators reproduce the real-terms chart.
- Re-derive at least four groups yourself from `uk_hmt_tables`, and check the partition.
- Attribution: a single HMT number TPA repeats is `restated`. A sum, deflation or ratio TPA computes is `own`, with `source_model: arithmetic` and `conditions.derived_from` naming the input. Compare that with the AB2025 `uk_tpa` family's convention and say whether it matches.
- Check the 14 proposed keys against README rule 2's naming bullet. `ab2026__package_property_and_savings_income_rates` is the agreed name for lines 61 and 62.

**CenTax:**
- Its 7 option keys are reforms CenTax costed. Check each scope as NOTES.md states it.
- The lane didn't re-stage CenTax's childcare report, because `data/externals/centax-childcare-100k.json` already holds it (#207). Confirm that file exists and covers the same figures.

**IPPR:** `ab2026__package_cost_of_living_support` has a scope IPPR doesn't define. Judge whether the row should instead be a context figure (`measure_key: null`, no proposed key), or whether IPPR's words pin the scope down.

**CPAG and SMF:** check that their NOTES.md, manifest and empty claims files are consistent, and that no challenge page is listed as a primary.
