**Verdict:** APPROVE

# Review of PR #247 at `a28223f2` (delta from `8a3e4982`)

`origin/uk/ab2026-tranche2` still points at `a28223f2`. `git diff --stat 8a3e4982 a28223f2` lists two files: `scorecard_db/ingest_uk_ab2026.py` (7 lines) and `tests/test_uk_ab2026_ingest.py` (156 lines). Each finding below is low. None shows a statement in the description to be false.

## Findings

| ID | Severity | Location | Concrete input and wrong output | Exact fix |
|---|---|---|---|---|
| L1 | low | Description line 33, second sentence | The sentence says "the AB2025 registry's `--resolve` check in `validate_budget_2026_registry.py` passed". `640bdd3`'s message says only "--check and --resolve pass". `build_ab2025_registry.py` has no `--resolve` flag. At `640bdd3`, `validate_budget_2026_registry.py` sets `--registry` by default to the AB2026 registry. So the message doesn't show which registry the run resolved, and the description states more than its one source records. "The sort changed" also gives the verb to an operation, not to us (guide lines 20, 22). | Replace the sentence with: "The sort changed only the variable lists of 37 name searches. We recorded in `640bdd3`'s message that `build_ab2025_registry.py --check` and a `--resolve` run passed, but not which registry that run resolved." (13 and 26 words) |
| L2 | low | `scorecard_db/ingest_uk_ab2026.py:685` (`_PRINTED_AMOUNT`); description line 160 | The pattern accepts "£0,123 million" (a comma after a lone zero) and "£01 million" (a leading zero). `_printed_unit` returns £1m for both. Line 160 says "We also refuse misplaced commas in a printed amount", and "£0,123" contradicts that. The refusal list also omits a valid group after a four-digit lead. Mutant X5 widens the lead group to `\d{1,4}`, so the pattern accepts "£1234,567 million", and all 94 tests still pass. No staged row uses any of these forms: the nine reviewed twins print "£2.6 billion", "£10 million", "£5 million" and "£500 million". The stored-value check still ties the number to the value, so no tolerance widens. | Replace the integer capture with `(0\|[1-9]\d*\|[1-9]\d{0,2}(?:,\d{3})+)`. Add `"£0,123 million"`, `"£01 million"` and `"£1234,567 million"` to `test_a_reviewed_twin_printed_in_another_form_raises`. I applied both changes in a scratch worktree and got 97 passed, 0 failed. The staged forms, "£0 million" and the decimal forms still parse. |
| L3 | low | `tests/test_uk_ab2026_ingest.py:717` (`_keeps_conditions`) | The helper checks each staged key and ignores keys the ingest adds. Mutant X7 inserts `cond.setdefault("housing_costs", "AHC")` before the fiscal-event check, which puts an unstaged housing-cost basis on every claim that lacks one, and all 94 tests pass. Invariant 5 promises only "every staged condition", so no sentence is false, but the test doesn't catch a fabricated condition. | After the loop, require every claim condition key to be a staged key, `{key}_verbatim` for a staged key in `_CANONICALISED` or `program`, or one of the keys `_score` and `_verdict_conditions` write: `country`, `value_verbatim`, `benchmark_class`, `estimate_kind`, `staged_metric`, `scoring_method`, `reform_hint`, `counterfactual`, `measure_key`, `pe_expressibility`, `pe_missing`, `action_link`. Also include any key that `with_baseline_condition` or `merge_republications` adds; read those functions for the exact set. Then add a case to `test_preservation_rejects_a_lost_condition`. This could also wait for a later PR. |
| L4 | low | Description line 150, first sentence | "The preservation test now compares every staged condition except a stored `program`" describes `8a3e4982`. At the head, the test no longer exempts a stored program. A reader who skims the log reads "now" as the current state. Sol's R1 asked to replace this sentence, and the coordinator added line 159 instead. Under guide line 44 the history should stay, so change the tense rather than delete the sentence. | Replace it with: "At `8a3e4982`, the preservation test compared every staged condition except a stored `program`, which killed cloud's surviving `price_basis` mutant." (20 words) |
| L5 | low | Description line 159, third sentence | "reject each of those forms in new tests" makes the reader look back to find "those forms" (guide line 36). | Replace it with: "We now count a verbatim field only on `geography`, `income_group` and `program`, require the registered name beside it where one exists, and reject a replaced program and an invented verbatim field in new tests." (34 words) |

## What I verified

**Tests.** I ran the CI-style command (`tests/test_uk_ab2026_ingest.py tests/test_uk_ab2025_harvest.py tests/test_harvest_ingest.py -n 4`) at `a28223f2`: **259 passed**, no failures or errors. That included the four temporary-directory tests Sol couldn't run. `tests/test_uk_ab2026_ingest.py` alone, with the AB2025 differential deselected as in `guard_mutants.py`, gives 94 passed.

**Check 1: R1 to R5.**

- **R1 is answered.** I replayed Sol's CenTax row 100 mutant, which discards the text and stores `winter_fuel_payment`. I also replayed both invented-verbatim mutants (`basis_verbatim`, `housing_costs_verbatim`). Against `test_every_claim_preserves_its_staged_row` alone, they fail. So do "program replaced beside its text", "program dropped", and geography or income group under its own verbatim field: **7 of 7 killed by the preservation test alone**. The helper does what the description says. It counts `_verbatim` only on `geography`, `income_group` and `program`. Where a name is registered, it requires that name and requires the text exactly when the name differs. For an unregistered program, it requires the text alone, with no `program` key.
- **R2 is answered.** The test appends `copy.deepcopy(table[252])`. The coordinator's "exception ignores the table row alone" mutant fails it.
- **R3 is answered for every staged form and for "£10, million".** Check 4 and L2 give the residual.
- **R4 is partly answered.** The sentence names the registry in words, but its one source doesn't support that naming (L1).
- **R5 is answered.** Each replacement Sol supplied appears verbatim:
  - description lines 149, 150 (last sentence), 153 and 167 (first sentence);
  - the test docstrings at the fuel duty freeze, the zero cell, the Ukraine target and the tolerance;
  - the `_printed_unit` docstring.

**Check 2: preservation escapes.** All **18 of the coordinator's mutants are killed** (W and PY repointed, same pytest arguments). I added nine of my own:

| Mutant | Result | Reading |
|---|---|---|
| X1: CenTax row 92 takes row 90's `component` and `income_type` | Killed (`test_every_staged_row_is_ingested_or_tallied`) | Rows 90 and 92 are the only staged pair that agree on every field the preservation test matches on (family, locator, column, print, value, period, unit, quote, table, attribution) and differ only in their conditions. The duplicate merges, so claims fall to 4,686 and the count pin fails. |
| X2: rows 90 and 92 swap those two conditions | Survived | Equivalent mutant: the two rows agree on every other field, so the swap emits the same claim set. Nothing is lost. |
| X3: a registered program always stores its text | Killed | |
| X4: the program branch reverts to `8a3e4982`'s `else:` | Killed | |
| X5: the integer group allows a four-digit lead | **Survived** | L2 |
| X6: the integer group allows two-digit groups | Killed | |
| X7: the ingest adds an unstaged `housing_costs` | **Survived** | L3. This adds a condition and doesn't lose one. |
| X8: the ingest drops a plain condition (`year_note`) | Killed (also by the preservation test alone) | |
| X9: the Ukraine test reverts to the 2030 copy | Survived | This mutates the test, not a guard. The old test also passes on correct code, as expected. |

I found no ingest change that loses or replaces a staged condition on an emitted claim and passes the file. Conditions on rows that merge or drop as twins remain outside the invariant, as the description's line 153 states.

**Check 3: the `program` branch.** I ran `same_claims.py` from worktrees at both heads. Each prints `4687 5952 4687 1265 9d62ee7ab0d90ced017a3f8159aeb2a91ada314262b87e7bb64278e5938a5311`. In both, `program_verbatim` appears on one claim (CenTax, p. 26, section 3.4) and `program` on none. So no claim changes, and line 157's "byte for byte" holds.

For a program a stager registers later, the branch stores the canonical name, and stores the staged text only where the name differs. That mirrors the `geography` and `income_group` branch above it, and X3 and X4 show that the monkeypatched test pins both cases. AB2025's ingest (`ingest_uk_ab2025.py:868`) still stores no text for a registered alias. That stays outside this PR under invariant 7.

**Check 4: printed forms.** Every form that `_printed_unit` meets in the staged data parses, and returns £100m for "£2.6 billion" and £1m for the million forms.

- **Accepted:** "£2.6 billion", "£2.60 billion", "£2,600 million", "£0 million", "£10 million", "£1234 million", "£1,234,567 million", "£1,234.5 million", "£1,000.25 million", "£0,123 million" (L2), "£01 million" (L2).
- **Refused:** "£10, million", "£1,2345 million", "£1234,567 million", "£,123 million", "£1,23 million", "£12,345,67 million", "£1. million", "£.5 billion", "£2.6 Billion", "£2.6  billion" (two spaces), "£2.6billion", "-£2.6 billion", "£-2.6 billion", "£2.6 bn", "£2.6 trillion", "£ 2.6 billion".
- **Misplaced commas:** the pattern refuses every misplaced comma except one after a lone zero (L2).

**Check 5: the new and changed tests.** Each new test fails when I remove its guard:

- The rejection cases fail under the helper mutants: stored name, canonical name, verbatim text, any-verbatim fallback.
- The acceptance cases fail when geography or a registered program is treated as plain.
- The registered-program test fails under X3, X4, "registered program loses its text" and "loses its name".
- The Ukraine test fails when only the target comparison goes.
- The printed-form cases fail under "misplaced commas" and X6.
- The other four changes edit only docstrings.

**Check 6: the description.**

- Every changed sentence holds against the code, git or my runs, apart from L1 (unsupported) and L2 (one form).
- `412c2f49` and `a28223f2` resolve, and each is the other's parent and child in the stated order.
- `git diff --name-only 8a3e4982 a28223f2` touches no file under `data/` or `pipeline/`, no JSON and no `KEY_DECISIONS.md`. So line 114 is true, and the registry doesn't need to be regenerated.
- Line 163's "killed all 18" matches my replay.

**Check 7: voice.** I read all 846 lines of the guide.

- No changed description sentence or docstring exceeds 40 words; the longest are 38 and 31, on line 167.
- I found no passive construction, label opener or self-referential clause in the delta.
- The ingest docstring and the five test docstrings name "we", "the OBR" or "someone" as the actor. The `_keeps_conditions` docstring uses imperatives.
- Apart from L1, L4 and L5, each new sentence gives the reader this:

| Sentence | What it gives the reader |
|---|---|
| 157 (both) | Who reviewed, which commits answer the review, and that the output didn't change |
| 159.1–2 | What the old helper let through, with Sol's concrete case |
| 159.4 | That the ingest changed, and why no claim moved |
| 160.1 | Which guard the Ukraine test now pins |
| 160.2 | Which printed form the ingest now refuses (L2 qualifies this) |
| 161 | Where the text fixes landed |
| 163 | The mutation evidence for this round |
| 114.2 | Why the registry needn't be regenerated |
| `_keeps_conditions` docstring | The exact rule the helper enforces, for each kind of condition |
| registered-program test docstring | Why the test monkeypatches the registry |

## What I couldn't verify

- **Which registry `640bdd3`'s `--resolve` run used (L1).** No log survives beyond the commit message.
- **Engine resolution and registry regeneration at policyengine-uk 2.151.0.** No pinned engine environment was available. Since the delta touches no registry or builder file, those runs don't need repeating.
- **The full repository suite and live CI.** I ran only the three files in the brief.
- **The coordinator's own mutant log.** I replayed the script itself rather than reading the coordinator's output.
