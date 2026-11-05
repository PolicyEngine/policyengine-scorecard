**Verdict:** APPROVE

Review of PR #252 at `58f1eb5c`, the delta from `c9027fe2`. The head of `origin/uk/ab2026-checker-mixed-fractions` was `58f1eb5c` when I fetched it. I found two low findings and no false statement.

## Findings

| id | severity | location | Concrete input and wrong output | Exact fix |
|---|---|---|---|---|
| L1 | low | description line 20 | "and a test killed all 14 mutants" reads as one test killing every mutant. In my replay, six different tests reported the first failure: `test_a_numeric_mixed_fraction_is_a_problem_at_any_value`, `test_a_word_after_and_leaves_the_factor_alone`, `test_rule_4_reads_where_the_locator_places_the_number`, `test_a_run_of_whitespace_in_a_note_reads_as_one_space`, `test_a_worded_sign_reads_in_any_spacing_or_case` and `test_each_form_reads_at_its_values_and_no_others`. | Replace the sentence with: "We weakened the new pattern four ways, limited the locator's closing square brackets to one, and weakened the whitespace rule and the sign read nine ways. A test killed each of the 14 mutants." |
| L2 | low | `tests/test_ab2026_harvest_contract.py`, `test_a_run_of_whitespace_in_a_note_reads_as_one_space` | The deterministic test tries only six runs (`"  "`, `"   "`, `"\t"`, `"\n"`, `" \t "`, `" "`). Only Hypothesis's random draws cover the other 23 whitespace characters. A mutant that fails only on one of those characters next to a sign word survived one full run: `WORDED_SIGN.search(_collapsed((r.get("normalization") or "").replace("sign ", "sig ")))`. Every one of my more realistic mutants failed, including one that drops all whitespace characters outside the six runs, one that drops the separators `\x1c`–`\x1f`, `\x85`, ` ` and ` `, and one that keeps case. No staged note has a run of whitespace. | In the parametrized test, also run every character: `for at, run in product(spaces, ("  ", "   ", "\t", "\n", " \t ", *WHITESPACE)):`. Each stretched note then compares factors and full problem lists for all 29 characters without relying on a random draw. |

## What I verified

- **Set up.** I checked out `58f1eb5c` detached and read the description through `gh api .../pulls/252 --jq .body`.
- **Tests.** I ran the CI command with `-n 4`, and **2,150 passed**. The family checker reported **12 families, 5,952 rows, 0 problems**.
- **R1, the fix.** `value_problems` now passes `_collapsed(r.get("normalization"))` to `WORDED_SIGN`. `_collapsed` (lower-case, then `" ".join(...split())`) also feeds `_factors`. `_says_nil` already collapsed each clause.
  - Python counts 29 characters as whitespace. `str.split()` and `re`'s `\s` both treat all 29 as whitespace, so the collapse and the `\s` in `_factors`'s regexes agree.
  - I replaced each space with each of the 29 characters and four mixed runs in **172 notes**: the **148 distinct staged notes** and 24 constructed notes covering nil clauses, worded signs, powers, chains, mixed fractions and unread forms. `_factors`, `_says_nil` and the worded-sign read returned **0 differences**. `value_problems` also returned **0 differences** across 6 `value_raw` strings and 16 values for five of the runs. Adding leading and trailing runs changed nothing either. I found no note whose reading changes when a run of whitespace replaces a space.
  - At `c9027fe2`, `value_raw="4", value=-8` failed with the opposite-sign problem under `"sign  from the wording; x 2"`, its tab variant and `"Sign from the wording; x 2"`. At `58f1eb5c`, all three pass, and `"x 2"` still fails.
- **Lower-casing.** Lower-casing only lets capitalised forms of the four phrases match. The pattern's letters have no capitals outside ASCII that fold to them, and `-> -\d` has no letters. Of the 148 staged notes, 26 have capitals. **0 of 5,952 rows** change their worded-sign reading, and 24 rows (11 distinct notes) carry a worded sign.
- **Before and after.** I loaded the checker at `8200b418`, `c9027fe2` and `58f1eb5c` and compared each staged row's factors, nil reading, worded-sign reading and problem list. **0 of 5,952 rows changed** between the first two commits, and **0 changed** between the last two. That supports description line 21.
- **R2 and mutants.** I re-ran the coordinator's 14 mutants against `58f1eb5c` in a separate worktree, with the CI dependencies installed. **All 14 failed a test**. Sol's `"/\t100"` mutant (the coordinator's "a tab after a slash doubles the factor") failed at `[x 1,000,000 / 100]`. I added seven mutants of my own:
  - `_collapsed` keeps case;
  - only the six test runs collapse;
  - Unicode spaces collapse but separators don't;
  - `_says_nil` only strips;
  - `_factors` stops lower-casing;
  - `"x\n2"` reads as `x 1`;
  - an em space after "sign" (L2).
  The first six were killed, and the seventh survived.
  - The mutation script treats exit code 2 as a kill. Under `-x` with xdist, pytest exits 2, so I counted a kill only where a `FAILED` line appeared. All 20 kills had one.
  - The new parametrized test passes `.04` and `40000` (Sol's R2) and compares `_factors` and complete problem lists.
- **Counts in the description and the commit message.**
  - `SPACED_NOTES` holds **20 notes**.
  - The parametrized test uses **10 values**: 4, −8, 8, 10, 40, 400, 0.04, 40,000, 4e6 and 0.
  - Python counts **29 characters** as whitespace.
  - The test file passes **2,150 tests**: 2,120 at `c9027fe2`, plus 20 parametrized notes, 9 sign cases and 1 negative case.
  - The coordinator's script has **14 mutants**: 4 + 1 + 9, matching line 20's breakdown.
  - The staged families hold **5,952 rows**, with 148 distinct notes.
  - In five runs of the Hypothesis strategy, each with 300 examples, every run drew all 29 characters. The commit message says "Hypothesis tries all 29 whitespace characters". That holds in practice, though Hypothesis doesn't guarantee it.
- **Statements.** The commit message's example, its README citation (README line 75) and its description of the fix match the code and my runs. Description lines 5, 6, 8, 15, 19 and 21 are true as written.
- **Voice.** I read all 846 lines of the guide and then reread the whole description.
  - Line 15 gives "reads" to the checker and "tries" to Hypothesis, which answers Sol's R3 on line 14.
  - The new sentences name actors ("the checker", "we", "Hypothesis") and use active verbs.
  - They hold no self-referential clause, label opener or be-verb comparison.
  - Their change history fits the guide's rule for PR descriptions (guide line 44, "Corrections and records keep their history").
  - L1 is the only wording finding.

What each new or changed sentence gives the reader (guide line 42):

| Sentence | Reader value |
|---|---|
| Line 1, added `c9027fe2` | Which reviews this commit answers |
| Line 6, first sentence | The failing note, its spacing, and the wrong outcome at −8 |
| Line 6, second sentence | What the checker now does, and that the sign read shares the factor read's rule |
| Line 15, first sentence | The invariant the tests guard |
| Line 15, second sentence | The deterministic test's grid (notes, runs, factors and problems, values) |
| Line 15, third sentence | Generated coverage beyond the grid |
| Line 19 | The full-suite result |
| Line 20 | How the tests were weakened, and that each mutant died (L1) |
| Line 21 | That no staged reading moved |

## What I couldn't verify

- The coordinator ran `compare_notes.py` and `mutants.py` on their own machine. I re-ran equivalent code, not their runs.
- A single run can't rule out the L2 mutant being killed by a lucky Hypothesis draw in another run. I report one run.
- I didn't fetch the earlier versions of the description, so I can't diff it. I read the current text in full.
