# AB2026 harvest staging (not for merge)

This directory holds the inputs a cloud session needs to finish PR #231 (tranche 1 of #230). It lives only on branch `uk/ab2026-harvest-staging` and never merges; the owner deletes the branch once #231 lands.

The 29 October harvest ran as seven local lanes, each in its own worktree at commit 9a0189cf. Their output never reached GitHub until now. This branch copies it as it stood on 3 November 2026, unchanged.

| Path here | What it is | Path the briefs and reviews use |
|---|---|---|
| `lanes/<lane>/<family>/` | Each lane's staged family: `stage.py`, `NOTES.md`, `manifest.jsonl`, `claims_staged.jsonl.gz`, and any report the lane left | `<lane worktree>/sources/harvest-uk-ab2026-2026-10-29/<family>/` |
| `lane-reports/<lane>.md` | Each lane's final report | `/Users/maxghenis/reviews/scorecard-ab2026-harvest/out/<lane>.md` |
| `reviews/verify-*.md` | The five independent reviews (Opus 5.5 on Subfleet lanes, read-only, 29 October) | `/Users/maxghenis/reviews/scorecard-ab2026-harvest/out/verify-*.md` |
| `briefs/` | The lane briefs, the shared instructions (`COMMON.md`, `verify-COMMON.md`) and the two rework briefs | `/Users/maxghenis/reviews/scorecard-ab2026-harvest/briefs/` |
| `ifs/data-items.json` | The seven IFS data items (page URL, lead sentence, Flourish id) for the IFS addendum's section 2 | `/Users/maxghenis/reviews/scorecard-ab2026-harvest/local-primaries/ifs/browser/data-items.json` |

Lanes: `hmt-costings` (uk_hmt_costings), `hmt-redbook` (uk_hmt_redbook), `ifs` (uk_ifs_ab2026), `obr-tables` (uk_obr_tables), `rf` (uk_rf_ab2026), `thinktanks-a` (uk_tpa, uk_centax, uk_ippr, uk_cpag, uk_smf), `thinktanks-b` (uk_niesr, uk_fai_sfc, uk_thinktank_misc, uk_devolved_govts).

Not here, on purpose:
- **Primaries.** The lanes kept local copies of the source documents in `.ab2026-primaries/<family>/`. This public repository carries no primary bytes, as for AB2025. Each family's `manifest.jsonl` gives the URL and SHA256 to fetch and check.
- **The two IFS pages read in a browser** (the IFS addendum's section 1). ifs.org.uk refuses non-browser clients, and the page text is IFS's, so it stays off GitHub. The owner adds those rows locally after the cloud work lands.

State of the two rework jobs:
- `hmt-redbook`: the rework (`briefs/rework-hmt-redbook.md`) ran on 29 October and stopped before writing its report. Its files are what it left (432 rows, down from 1,699); nothing has checked them against the brief yet.
- `ifs`: the addendum (`briefs/ifs-addendum.md`) never ran. The family is the first lane's 106 rows.
