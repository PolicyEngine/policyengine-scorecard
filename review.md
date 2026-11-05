**Verdict:** APPROVE

# Review of PR #246 at `e78e1921`, the delta from `0e444f7f`

Reviewed commit `e78e1921d36f3c79e9bba28c5fa76e1ab240b01c`, which is the head of `uk/ab2026-notes-voice`. The delta changes 8 lines in 3 notes (IFS 6, OBR 1, TPA 1).

## Findings

| ID | Severity | Location | Input and wrong output | Exact fix |
|---|---|---|---|---|
| L1 | low | IFS L637–638 | "though the coordinator assigned the 29 October briefing" reads as if the coordinator assigned a briefing, not a deck. The old text said the assignment described the deck as the 29 October briefing, and that is the date evidence the sentence weighs against the cover. | "though the coordinator assigned it as the 29 October briefing deck, and in the PDF metadata IFS records creation and modification on 29 October." |
| L2 | low | PR description, "Changes in answer to the review of `0e444f7f`", last sentence | "one number token that moved only in its punctuation". My comparison finds two: IFS "7." to "7" (rule 7) and TPA "11," to "11" (line 11). A tokenizer that strips trailing punctuation finds none. Both counts leave every number's value unchanged. | "…the £100, and number tokens that moved only in their punctuation." |

## What I verified

1. **F1 (fixed):** IFS L155 now reads "When a dropped parameter names a measure, such as the £100 payment, we keep it in the kept rows' `reform_hint`." This is my wording, and it agrees with L96, L162, L166 and the staged hints on `main`.
2. **L1 to L3 (fixed with my wording):**
   - TPA's line 11 cell quotes "Maintain the cash ISA limit at £20,000", which is Table 6.1 line 11's title.
   - OBR L247 now quotes "15 measures expected to reduce the tax gap", matching rows 2663–2664.
   - IFS L177 reads "In her remarks Miller gives no number…".
3. **L4 (fixed with your wording):** "but we give it a manifest line as a changed primary, as README rule 7 requires". The actor stays "we", and the rule's requirement is back.
4. **L5 (fixed):** "in the PDF metadata IFS records creation and modification on 29 October". The new actor in the first clause raises L1 above.
5. **Token comparison, `0e444f7f` to `e78e1921`.** No quoted phrase is lost, and two are new: "Maintain the cash ISA limit at £20,000" and "15 measures expected to reduce the tax gap". One number is new (100), two move only in their punctuation (L2), and no code span changes.
6. **Description section.**
   - IFS `reform_hint` on `main` includes "£100 Household Energy Payment (Jan 2027)" in three rows. True.
   - "took its wording for TPA's line 11 and the OBR's…": true.
   - The Miller, rule 7 and PDF metadata statements match the diff. True.
   - The script report is true, apart from the count in L2.
   - Its two longest sentences have 33 and about 30 words. It has no label openers or inanimate actors.

## What I couldn't verify

- Whether the coordinator's assignment text calls the deck the 29 October briefing. The manifest records only an "assignment local copy".
