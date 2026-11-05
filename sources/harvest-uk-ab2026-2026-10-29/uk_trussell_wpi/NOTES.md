# uk_trussell_wpi — Trussell, Autumn Budget 2026

We keep `stage.py`, which writes `manifest.jsonl` and `claims_staged.jsonl.gz`, on branch `uk/ab2026-harvest-staging` at `harvest-staging/ab2026/lanes/thinktanks-b/uk_trussell_wpi/stage.py`. We commit only NOTES.md, `manifest.jsonl` and `claims_staged.jsonl.gz` to this branch, and no primary bytes to the repository: fetch the primary from its `manifest.jsonl` URL and check its sha256.

We use source `trussell_wpi`, as AB2025's `uk_trussell_wpi` does, and stage **1 row from 1 primary.** The thinktanks-b lane staged this row in `uk_thinktank_misc` on 29 October with source `trussell`. On 3 November, that family's review asked in finding 5 for AB2025's slug `trussell_wpi`, and the coordinator moved the row and its manifest line here, since AB2025 keeps Trussell's Budget responses in their own family. The coordinator changed nothing else in the row. We copied `uk_thinktank_misc`'s script into `stage.py` and filtered it to Trussell's row and primary.

## Access

The thinktanks-b lane found [Our response to the Autumn Budget 2026](https://www.trussell.org.uk/news-and-research/news/our-response-to-the-autumn-budget-2026) by searching Trussell's own news pages, and Trussell dates the page “28th Oct 2026”. The lane fetched it fresh on 29 October 2026 with `curl -sSL` and the harvest's Safari User-Agent: HTTP 200, fetch completed 15:23:24Z, 171,343 bytes, sha256 `6cd2162d1382f03e937a382a39bd38c497a83d357bd969d2c85598740d17a95e`. The lane read the page's own body text and hashed the HTML.

## Coverage and conventions

| measure_key | Rows | What |
|---|---:|---|
| `null` | 1 | Helen Barnard's “over half of private renters on low incomes” in receipt of Local Housing Allowance ran out of food and could not afford more, in the last 12 months |

- We record `metric: affected_share` with unit `share`. Because `models.py` registers that metric, we put it in `metric`, not `proposed_metric`; we made that change on 4 November, after review B finding 1 and review A's H-6(a). We read “over half” as the strict lower bound 0.5, `value_kind: range_low`.
- Trussell calls the finding its own research but gives no method, research dates or exact percentage. We therefore record `source_model: unstated`, `own`, `administrative_fact` for a retrospective reported observation, and `parse_confidence: medium`.
- Trussell reports context, not the modelled effect of the LHA freeze or of any Budget measure, so we gave the row no measure key and no proposed key. We put the 12-month window in `conditions.horizon` and use the publication-year anchor 2026, `point_in_time`, as the period.

## Not staged

- Trussell prints no measured effect of the frozen LHA or of the Budget.
- Trussell states that the government has already lifted the two-child limit, a qualitative claim we staged no row for.

## Verification

- On 4 November, review B (PR #231, issue comment 6635498758) raised finding 1, and we now record the registered `affected_share` in `metric`, with `proposed_metric` null. We made the edit in the review-fixes block, which we copied word for word into both families' `stage.py`. The contract checker reports 1 row, 0 problems, and when we re-run `stage.py` it reproduces both files byte for byte. We re-opened no primary.
- On 3 November, the contract checker reported 1 row, 0 problems, and when we re-ran `stage.py` it reproduced `manifest.jsonl` and `claims_staged.jsonl.gz` byte for byte. We re-opened no primary, because the session's network policy refused trussell.org.uk.
- On 29 October, while the row stood in `uk_thinktank_misc`, the lane re-opened the saved page at the locator and checked the quote and value against it. It also checked that the quote runs as contiguous text under 15 words and contains `value_raw`.
