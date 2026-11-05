**Status:** in progress

# Review of PR #247 at `a28223f2` (delta from `8a3e4982`)

`origin/uk/ab2026-tranche2` still points at `a28223f2`. `git diff --stat 8a3e4982 a28223f2` lists two files: `scorecard_db/ingest_uk_ab2026.py` (7 lines) and `tests/test_uk_ab2026_ingest.py` (156 lines).

CI-style run at the head: `tests/test_uk_ab2026_ingest.py tests/test_uk_ab2025_harvest.py tests/test_harvest_ingest.py -n 4` gives **259 passed**, no failures, no errors.

## Check 1: R1 to R5

- **R1, answered.** Sol's CenTax row 100 mutant (program replaced, text discarded) and both invented-verbatim mutants (`basis_verbatim`, `housing_costs_verbatim`) fail `test_every_claim_preserves_its_staged_row` on its own, not only the new unit tests. So do "program replaced beside its text", "program dropped", and geography and income group moved under their own verbatim field: 7 of 7 killed by the preservation test alone.
- **R2, answered.** The test appends `copy.deepcopy(table[252])`. Mutant results in check 2.
- **R3, answered for the staged forms.** Details in check 4.
- **R4, partly answered.** See finding L2.
- **R5, answered.** Every replacement Sol supplied appears verbatim: description lines 149, 150 (last sentence), 153 and 167; test docstrings for the fuel duty freeze, the zero cell, the Ukraine target and the tolerance; the `_printed_unit` docstring.

## Check 3: the new `program` branch

`same_claims.py` at both heads prints `4687 5952 4687 1265 9d62ee7ab0d90ced017a3f8159aeb2a91ada314262b87e7bb64278e5938a5311`. The census gives `program_verbatim` on one claim (CenTax, p. 26, section 3.4) and `program` on none, at both heads.
