# uk_trussell_wpi — Trussell, Autumn Budget 2026

**Working files.** `stage.py`, which writes `manifest.jsonl` and `claims_staged.jsonl.gz`, lives on branch `uk/ab2026-harvest-staging` at `harvest-staging/ab2026/lanes/thinktanks-b/uk_trussell_wpi/stage.py`; this branch carries only NOTES.md, `manifest.jsonl` and `claims_staged.jsonl.gz`. The repository carries no primary bytes: fetch the primary from its `manifest.jsonl` URL and check its sha256.

Source `trussell_wpi`, as in AB2025's `uk_trussell_wpi`. **1 row from 1 primary.** The thinktanks-b lane staged this row in `uk_thinktank_misc` on 29 October with source `trussell`. On 3 November its review's finding 5 set the slug to AB2025's `trussell_wpi`, and the coordinator moved the row and its manifest line here, as AB2025 keeps Trussell's Budget responses in their own family. The row is otherwise unchanged. `stage.py` is `uk_thinktank_misc`'s script, filtered to Trussell's row and primary.

## Access

The thinktanks-b lane found [Our response to the Autumn Budget 2026](https://www.trussell.org.uk/news-and-research/news/our-response-to-the-autumn-budget-2026) by searching Trussell's own news pages; the page prints “28th Oct 2026”. It was fetched fresh on 29 October 2026 with `curl -sSL` and the harvest's Safari User-Agent: HTTP 200, fetch completed 15:23:24Z, 171,343 bytes, sha256 `6cd2162d1382f03e937a382a39bd38c497a83d357bd969d2c85598740d17a95e`. The page's own body text was read; the hash is of the HTML.

## Coverage and conventions

| measure_key | Rows | What |
|---|---:|---|
| `null` | 1 | Helen Barnard's “over half of private renters on low incomes” in receipt of Local Housing Allowance ran out of food and could not afford more, in the last 12 months |

- `proposed_metric: affected_share`, unit `share`: “over half” is the strict lower bound 0.5, `value_kind: range_low`.
- Trussell calls the finding its own research but gives no method, research dates or exact percentage: `source_model: unstated`, `own`, `administrative_fact` for a retrospective reported observation, `parse_confidence: medium`.
- Context, not the modelled effect of the LHA freeze or of any Budget measure: no measure key and no proposed key. The 12-month window is `conditions.horizon`; the period is the publication-year anchor 2026, `point_in_time`.

## Not staged

- Trussell prints no measured effect of the frozen LHA or of the Budget.
- Its statement that the government has already lifted the two-child limit is qualitative and has no row.

## Verification

- **3 November:** the contract checker reports 1 row, 0 problems; a re-run of `stage.py` reproduces `manifest.jsonl` and `claims_staged.jsonl.gz` byte for byte. No primary was re-opened (the session's network policy refused trussell.org.uk).
- **29 October (in `uk_thinktank_misc`):** the lane re-opened the saved page at the locator and checked the quote and value against it, and checked the quote is contiguous text under 15 words containing `value_raw`.
