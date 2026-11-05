**Verdict:** REQUEST CHANGES

# Review of PR #249 at `a58ddc3eff5397d3f46993bb6902f2ea6d0bfdc6`

Scope: `570ed6c4` (the merge of tranche 2 at `a28223f2`) and `a58ddc3e` (the answer to Sol's review of `44d226dc`), plus the whole PR description as `pulls/249 .body` returned it (base `main`, head `a58ddc3e`). `origin/uk/ab2026-tranche3` pointed at `a58ddc3e` when I fetched.

One sentence in the description misstates what `53cdc41` did and contradicts the description's own account two sections up (M1). No row, value or test is wrong, and the code and staging are ready to merge. Correct that sentence and the PR has only low findings; I'd then approve.

## Findings

| id | severity | location | input → wrong output | fix |
|---|---|---|---|---|
| M1 | medium (false statement in the description) | description, "The reviews of a21cabd", bullet "Annotations (cloud L3, L4)" | The bullet records what `53cdc41` did: "We now say in the behavioural sentence that the OBR expects more landlords to incorporate to save tax and more to underpay, cutting the yield by £0.1 billion a year." At `53cdc41` the stager wrote "…cutting the yield by £0.1 billion a year on average from 2028-29, and we hold incomes fixed." (`git show 53cdc41:pipeline/stage_uk_ab2026.py`, lines 601-603). The bullet "The behavioural sentence (Sol N1)" says "We had put the average on the £0.1 billion in `53cdc41`", so the two contradict each other, and the older bullet hides the wording `a58ddc3` corrected (guide line 44). Sol's suggested fix for N1 asked for this edit; it rewrote history. The average came from my L3 on `a21cabd2`, which wrongly tied it to the £0.1 billion. | Replace the bullet's first sentence with: "We now name landlords in the behavioural sentence, which read "The OBR expects more landlords to incorporate to save tax and more to underpay, cutting the yield by £0.1 billion a year on average from 2028-29, and we hold incomes fixed." until `a58ddc3` took out the average." Keep the trading allowance sentence. |
| L1 | low | `pipeline/stage_uk_ab2026.py`, `classify`, `if relation not in (signs.SAME, signs.OPPOSITE):`; `tests/test_uk_ab2026_counterparts.py`, `test_an_exchequer_claim_without_a_readable_sign_raises` | The test feeds only conventions that read as `unknown`. Mutant Y1 (`if relation == signs.UNKNOWN:`) passes all counterpart tests. Under it, claim `443d09eaf699205595fd` with `sign_convention` `magnitude_with_direction_in_label` and value +£79m classifies as `exchequer` and stages `pe_value` +£47,583,833.17 with "We reverse our sign to match the claim's (PE oriented to it)." The head raises "sign magnitude (magnitude_in_label)". | Add `signs.MAGNITUDE_CONVENTION` to the test's parametrize list and match `"sign (unknown|magnitude)"`. |
| L2 | low | `tests/test_uk_ab2026_counterparts.py`, the reason tests; `REASONS`, shown on the site | The new tests pin producer names and one substring per count reason, not each reason's text. Mutant Y2 ("income tax falls" → "income tax rises" in `taken_out_of_tax_count`) and mutant Y4 ("with no figure for England alone" → "with a figure for England alone" in `england_only_average`) each pass all counterpart tests and change the sentence a reader sees. | Write the 16 reasons out in the test, as `SCOPE` does for the scope sentences, and assert `S.REASONS == REASONS`. |
| L3 | low | description: "Review fixes" paragraph; "The review of 44d226d" first paragraph; "The merge of 8a3e498"; "The review of 2cfdf22" last bullet; "The review of 229bbc1" last bullet | Five sentences still give the verb to a merge or a commit (guide lines 22 and 46): "…at `589f822`, which moved no claim, value or cell"; "…in `570ed6c`, which moved no claim"; "…under the macro verdict, which adds one `pe_gap` verdict"; "…at `5ff3c4b`, which drops three IFS claims…" and "…`002d90c`, which add tests only"; "…at `c58128e`, which drops HM Treasury's two red book repetitions…". | "After the review of `2cfdf22`, we merged tranche 2 at `589f822`, and no claim, value or cell changed." / "We merged tranche 2 at `a28223f` in `570ed6c`, and no claim changed, and we answered the findings in `a58ddc3`." / "#247's ingest now keeps OBR row 2740 on `decisions_effect_on_borrowing` under the macro verdict and gives it one `pe_gap` verdict, so the database gains a result and the export lists one fewer row as not computed." / "We merged tranche 2 at `5ff3c4b`, and its ingest drops three IFS claims that split households by spending (…)." and "We also merged `b227956` and `002d90c`, whose commits add tests only, and no paired claim, value or cell changed in any of the three merges." / "We merged tranche 2 at `c58128e`, and its ingest drops HM Treasury's two red book repetitions of…". |
| L4 | low, outside this PR | `sources/harvest-uk-ab2026-2026-10-29`, claim `f59d84db9343c682f25b` (on `main` since #247) | The behavioural claim's `aggregation` still reads "annual average from 2028-29 (same costing paragraph)", the reading `a58ddc3` dropped from the annotation. The claim is tallied, so it reaches no comparison. | In a follow-up to the harvest, set the claim's aggregation to "annual" and leave "average from 2028-29" on `f05c0312` (the £0.4 billion). |

## Verified

**Branch state.** `git diff a28223f2 origin/main` prints nothing. `git diff origin/main...a58ddc3e --stat` lists 26 files, all tranche 3: the 6.11.1 pair and its freeze, the stager and its pin, the vendored artifacts and manifest, the staging, the counterparts test, and in `scorecard_db/ingest_uk_ab2026.py` and `tests/test_uk_ab2026_ingest.py` only `STAGED_COUNTERPARTS`, `advance_lanes` and the AB2025 differential test's counterparts and lanes. `git diff 570ed6c4 a58ddc3e` touches the stager (the comment and the behavioural sentence), the staging and the counterparts test.

**Merge `570ed6c4`.** `claims()` gives the same 368 claims, byte for byte in id, value and conditions, at `44d226d`, `570ed6c4` and `a58ddc3e`. The merge changes `scorecard_db/ingest_uk_ab2026.py` (7 lines) and `tests/test_uk_ab2026_ingest.py` only.

**Tests.** The nine-file command with `-n 4 -rs` and no deselection: **2,471 passed, 0 skipped**, in 114s. Here the registry's regeneration test ran, since `.venv-pe2151` (policyengine-uk 2.151.0) exists, and the two tests the coordinator deselected found their inputs and passed. That matches the description's 2,468 passed and 1 skipped plus those three.

**N1, the behavioural sentence.** Against paragraph 3.17 as quoted in the request: the OBR attaches "on average from 2028-29" to the £0.4 billion yield and states the behavioural cut as £0.1 billion a year. "Cutting the yield by £0.1 billion a year" now carries the amount and the period as the OBR prints them. "More landlords to incorporate to save tax and more to underpay" renders "additional tax-motivated incorporation and higher non-compliance" with the people who act as subject. The sentence leaves out the OBR's "small", which the amount already shows. The rows it sits on (2028-29 to 2031-32, none in 2027-28) follow the yield's "from 2028-29", which the new stager comment states. I find it faithful. Against `570ed6c4`, the same 35 rows differ only in `annotations`, and only on the eight property rows from 2028-29, where "…a year on average from 2028-29, and…" became "…a year, and…". `python -B pipeline/stage_uk_ab2026.py stage` exits 0, and `git status --short` stays empty.

**N2, the new tests.** Each new or widened test fails with its guard removed or weakened:

- gainer geography over five areas and none;
- gainer unit over four units;
- exchequer shape over unit, geography and year;
- unreadable sign, three conventions;
- the costings lane, Hypothesis over the lane's registry keys and any text;
- the named line under the borrowing convention, a reversed note and none;
- the behavioural line under a reversed convention and none;
- the opposite-sign annotation in the flip test;
- each reason's producers;
- the £1 minimum and decile filter in the two count reasons.

**Mutants.** I ran Appendix C's 36 mutants (the 22 earlier ones less the dropped average mutant, plus 15, Sol's ten among them), repointed to three worktrees at `a58ddc3e`. Each worktree patched the stager, ran `stage`, ran `pytest tests/test_uk_ab2026_counterparts.py -x -n 2`, then restored the stager and staging. All 36 patches applied once, and **all 36 were killed**. For example, Sol's "no unknown-sign rejection" died on `test_an_exchequer_claim_without_a_readable_sign_raises[None]`, and "opposite-sign annotation corrupted" died on the flip test. My own five:

| mutant | outcome |
|---|---|
| Y1 the sign guard rejects only `unknown` | **survived** (L1) |
| Y2 the taken-out-of-tax reason says "rises" | **survived** (L2) |
| Y3 the behavioural years start in 2029-30 | killed: behavioural test |
| Y4 the England reason says "with a figure for England alone" | **survived** (L2) |
| Y5 the behavioural sentence says "raising the yield" | killed: behavioural test |

**Wiring.** Fresh `ScorecardDB`, a copy of `data/lanes.json`, `ingest`, `ingest_verdicts`, `ingest_campaign.ingest` (35 attached), `advance_lanes`, then `export_populations.export(db, out, None)` into the scratchpad. All match the description:

- 4,687 claims, 3,207 with a result: 35 `constructed`, 3,172 `pe_gap`;
- 4,661 export rows: 3,172 `pe_gap`, 1,454 not computed, 35 constructed;
- lanes 35 of 3,828, 0 of 586 and 0 of 273.

The tally gives 368 claims, 35 computed and 333 tallied under 16 reasons.

**The description, sentence by sentence on the changed parts.** True:

- first paragraph (#247 merged as `1615e267`, base `main`);
- 368 claims and 16 reasons;
- invariants 7, 8, 10 and 11 against the tests named above;
- invariant 9 (CI fetch);
- the wiring paragraph;
- "The review of 44d226d": the merge moved no claim (checked), only eight annotations changed (checked), and the three bullets match the diff;
- the 2,468/1 test count (consistent with my run);
- the 36 killed mutants (rerun);
- the reworded "The reviewer of" openers on the three older sections.

False: M1.

**Voice, against the guide (all 846 lines read before judging).**

- **Description.** 128 sentences outside tables, headings and the closing line, mean 24.2 words, median 23.5. Over 40 words: the row-27 example (most of it a quoted annotation) and three bullets whose bold label pushes them to 41-42 words; without labels the longest runs 38. I'd keep the bold finding labels, since they tie each bullet to a reviewer's id.
- **Remaining issues.** The merge-as-actor sentences are L3. The new behavioural annotation names its actors (the OBR, landlords, "we") and needs no change.

## Not verified

- I didn't open OBR paragraph 3.17 itself. I relied on the text quoted in the request.
- I didn't rerun the hand-off's earlier history (`53cdc41` and `44d226d` test counts) beyond reading `53cdc41`'s stager for M1.
- I didn't run CI or the app.
- I didn't read the full `53cdc41` and `44d226d` diffs again, since Sol reviewed them. I judged only the changed description sentences that describe them.
