**Verdict:** APPROVE

# Review of PR #249 at `75c4a1ff9aef9ace619a9b48bb455491bdc02d1a`

Scope: `a58ddc3e..75c4a1ff`, which changes only `tests/test_uk_ab2026_counterparts.py`, plus the whole PR description as `pulls/249 .body` returned it (base `main`, head `75c4a1ff`). `origin/uk/ab2026-tranche3` pointed at `75c4a1ff` and `origin/main` at `3557c2b5` when I fetched.

M1 and L1 to L3 from my review of `a58ddc3e` landed, and L4 is deferred to a named follow-up. I found one low finding and no false statement.

## Findings

| id | severity | location | input → wrong output | fix |
|---|---|---|---|---|
| L1 | low | description, "The review of a58ddc3", bullet "The behavioural claim (cloud L4)" | "…and update the claim ids we pin here." `stage_uk_ab2026_expected.json` pins no id for `f59d84db9343c682f25b`; `grep` finds it 0 times there and in no test. The id appears only in the committed `results/uk/ab2026/STAGING_UNANSWERED.jsonl`, which `stage` regenerates. Changing the claim's aggregation changes its id, so that file moves, and no pin does. | "…and regenerate `STAGING_UNANSWERED.jsonl`, which lists the claim by id." |

## Verified

**Branch state.**

- `git diff a58ddc3e 75c4a1ff --stat`: one file, `tests/test_uk_ab2026_counterparts.py`, 92 insertions and 3 deletions.
- `git merge-tree --write-tree origin/main 75c4a1ff` exits 0 with tree `16420785…` and reports no conflict.
- No file this PR changes (`origin/main...75c4a1ff`) appears in `git diff 1615e267 origin/main` (15 files from #252 and #246).
- `python -B pipeline/stage_uk_ab2026.py stage` exits 0, and `git status --short` stays empty.

**L1 and L2 from the last review.**

- The test's `REASONS` dict holds 16 entries. `test_each_reason_reads_as_we_wrote_it` asserts `S.REASONS == REASONS` and passes at the head, so the copy matches the stager word for word.
- `test_an_exchequer_claim_without_a_readable_sign_raises` now adds `signs.MAGNITUDE_CONVENTION` and matches `sign magnitude ` for that case. It still matches `sign unknown ` for the other three.

My mutants, rerun in worktrees at `75c4a1ff` (patch the stager, run `stage`, run `pytest tests/test_uk_ab2026_counterparts.py -x -n 2`, restore):

| mutant | at `a58ddc3e` | at `75c4a1ff` |
|---|---|---|
| Y1 the sign guard rejects only `unknown` | survived | killed: `test_an_exchequer_claim_without_a_readable_sign_raises[magnitude_with_direction_in_label-magnitude]` |
| Y2 the taken-out-of-tax reason says "rises" | survived | killed: `test_each_reason_reads_as_we_wrote_it` |
| Y3 the behavioural years start in 2029-30 | killed | killed |
| Y4 the England reason says "with a figure for England alone" | survived | killed: `test_each_reason_reads_as_we_wrote_it` |
| Y5 the behavioural sentence says "raising the yield" | killed | killed |

**The 36 earlier mutants.** I reran Appendix C's 36 (from the previous request) the same way across three worktrees. All 36 patches applied once, `stage` exited 0 for each, and **all 36 were killed**.

**Tests.** The nine-file command with `-n 4 -rs` and no deselection gave **2,473 passed, 0 skipped**. The registry's regeneration ran, since `.venv-pe2151` exists, and the two tests you deselected passed here. That squares with your 2,470 passed and 1 skipped plus those three.

**M1.** The annotations bullet in "The reviews of a21cabd" now reads: "In `53cdc41` we wrote that the OBR expects more landlords to incorporate to save tax and more to underpay, cutting the yield by £0.1 billion a year on average from 2028-29. We took the average out in `a58ddc3` (Sol N1)." `git show 53cdc41:pipeline/stage_uk_ab2026.py` (lines 601-603) carries that sentence with the average, and `a58ddc3` removes it. The record is true and agrees with the N1 bullet.

**L3 and the full pass.** I diffed the description against the body I reviewed at `a58ddc3e`; 15 paragraphs or bullets changed.

- **The six sentences I named:**
  - "…without moving any claim, value or cell" (twice): true; I checked both merges in earlier rounds.
  - "#247's ingest … gives it one `pe_gap` verdict, so we store one more result and export one fewer row as not computed": matches Sol's measured delta and my wiring counts (3,207 results, 1,454 not computed).
  - "…and its ingest drops three IFS claims…": true (`claims()` at `2cfdf22` vs `f28367f`).
  - "…in which we added only tests to tranche 2": true; `04224e6` and `b8a8a11` change tests only.
  - "…and its ingest drops HM Treasury's two red book repetitions…": as recorded in round one.
- **"We" verbs where the dashboard or the site had them:** invariant 2, invariant 8, "The public site", the Carer's Allowance bullet, the behavioural bullet, the trading bullet and the receipts bullet in "The review of eb7c13b". Each statement holds against the receipts I read in earlier rounds:
  - Carer's Allowance's Universal Credit and PAYE limit;
  - property's "Incomes are held fixed, with no behavioural response";
  - the trading allowance's gross-receipts limit;
  - "In England and Wales" and "England, Wales and Northern Ireland".

  "We" stands for PolicyEngine, which publishes the dashboard, as guide line 24 asks.
- **What still acts.** I grepped for a merge, commit, PR, review, hand-off, receipt, CSV, site or file taking a verb. No document, merge or commit acts. The remaining actors are programs: the stager, tranche 2's and #247's ingest, the dashboard's generator, the tests and CI. Guide line 20 lets a program act.

**The new section "The review of a58ddc3".**

- One medium and four low findings: true.
- "We changed only the counterparts test, so no claim, value, cell or staged row moved": true. `stage` is clean and the stager is unchanged.
- The M1, L1, L2 and L3 bullets describe the diff and the description accurately.
- The L4 bullet's present-tense half is true: the claim's aggregation reads "annual average from 2028-29 (same costing paragraph)" on `main`. Its plan is L1 above.
- "2,470 passed and 1 skipped" squares with my run. "A test killed each of the 36 earlier mutants and the reviewer's three survivors": rerun, true.

**Voice, against the whole guide (reread in full).**

- **Length.** 143 sentences outside tables, headings, bold labels and the closing line. Mean 23.4 words, median 23. Only the row-27 example runs over 40, and most of it quotes the annotation.
- **Patterns.** No label openers in prose, no defensive framing, no glosses. Corrections keep their history, as guide line 44 asks.
- **The new section.** Each sentence records a finding, the change and its result.

## Not verified

- The follow-up PR the L4 bullet promises (paragraph 4.30 and Table 6.3) doesn't exist yet.
- I didn't rerun the wiring counts at this head. The stager and staging are byte-identical to `a58ddc3e`, where I ran them, and `main`'s new commits touch none of this PR's files. I didn't build the merged tree either.
- I didn't run CI or the app.
