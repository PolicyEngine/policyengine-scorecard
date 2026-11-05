**Status:** in progress

Review of PR #252 at `58f1eb5c`, the delta from `c9027fe2`. The head of `origin/uk/ab2026-checker-mixed-fractions` was `58f1eb5c` when I fetched it.

## Interim (checks 1–3)

- Check 1 (R1): I replaced each space with each of Python's 29 whitespace characters and four mixed runs in 172 notes (the 148 distinct staged notes plus 24 constructed ones covering nil, sign, power, chain and unread forms). `_factors`, `_says_nil` and the collapsed `WORDED_SIGN` read gave 0 differences. `value_problems` also gave 0 differences across 6 `value_raw` strings × 16 values. No counterexample.
- Check 2 (R2): the coordinator's 14 mutants and 6 of my own were killed (Sol's `"/\t100"` mutant among them). One contrived mutant survived (see L2).
- Check 3: 2,150 passed; 12 families, 5,952 rows, 0 problems. The counts in the description and the commit message match what I ran.
