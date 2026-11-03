# uk_smf: Social Market Foundation, Autumn Budget 2026

This family holds no rows and lists no primaries: the page the assignment names was unreachable. Source slug `smf`, as in the AB2025 `uk_smf` family.

`stage.py` writes the empty `manifest.jsonl` and the empty, deterministic `claims_staged.jsonl.gz`, and records the unreached page as data.

- **Rows:** 0.
- **Primaries:** 0.

## Unreached page

The page was fetched twice on 2026-10-29 with `curl -sSL` and the browser User-Agent in the brief. Both fetches returned HTTP 403 with Cloudflare's JavaScript challenge ("Just a moment... Enable JavaScript and cookies to continue"), not the page. Under the brief, nothing was done to get round the challenge.

The coordinator opened the page in the Claude desktop app's built-in browser at about 17:31Z on 2026-10-29. Cloudflare's security verification page didn't clear on its own, and the coordinator didn't interact with it, so the page remains unreached.

The assignment lists no local copy, and the coordinator's `local-primaries/` holds none for SMF. The challenge pages' sha256 are recorded only as evidence of the refusal; they are not primaries.

| page | fetches (UTC) | challenge-page sha256 |
|---|---|---|
| https://www.smf.co.uk/todays-budget-provides-immediate-relief-for-households-but-details-of-changes-on-many-larger-issues-yet-to-come-think-tank-says/ | 16:17, 16:37: 403 | `70b6e26e33ba117f…`, `cb5e681e49f5e4a6…` |

The AB2025 harvest reached smf.co.uk directly on 2026-09-24, so the challenge is new. A local copy saved by a browser session that passed it would let a re-run stage the page with `access: "local copy"`.

## What the family would hold

The seed inventory names the SMF only among "Others". Only the URL slug was seen ("todays-budget-provides-immediate-relief-for-households-but-details-of-changes-on-many-larger-issues-yet-to-come-think-tank-says"); the challenge page's own title is "Just a moment...". Nothing from the page can be staged until it is read.
