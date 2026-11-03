# uk_cpag: Child Poverty Action Group, Autumn Budget 2026

This family holds no rows and lists no primaries: both pages the assignment names were unreachable. Source slug `cpag`, as in the AB2025 `uk_cpag` family.

`stage.py` writes the empty `manifest.jsonl` and the empty, deterministic `claims_staged.jsonl.gz`, and records the unreached pages as data.

- **Rows:** 0.
- **Primaries:** 0.

## Unreached pages

Each page was fetched twice on 2026-10-29 with `curl -sSL` and the browser User-Agent in the brief. Every fetch returned HTTP 403 with Cloudflare's JavaScript challenge ("Just a moment... Enable JavaScript and cookies to continue"), not the page. Under the brief, nothing was done to get round the challenge.

The coordinator opened the Budget response page (https://cpag.org.uk/news/cpags-2026-budget-response) in the Claude desktop app's built-in browser at about 17:31Z on 2026-10-29. Cloudflare's security verification page didn't clear on its own, and the coordinator didn't interact with it, so both pages remain unreached.

The assignment lists no local copy, and the coordinator's `local-primaries/` holds none for CPAG. The challenge pages' sha256 are recorded only as evidence of the refusal; they are not primaries.

| page | fetches (UTC) | challenge-page sha256 |
|---|---|---|
| https://cpag.org.uk/news/cpags-2026-budget-response (CPAG's Budget response, 28 October) | 16:17, 16:37: 403 | `b493071ca65505df…`, `131449484af19395…` |
| https://cpag.org.uk/news/campaigners-call-ps10-child-uk-budget-boost-child-benefit (pre-Budget call; the URL slug reads "campaigners call £10 child UK budget boost child benefit") | 16:17, 16:37: 403 | `8d238b41566d6f9e…`, `0f9decd1941d6c0c…` |

## What the family would hold

The seed inventory describes the Budget response (28 October) and a child benefit item. The assignment asks for the pre-Budget call to be staged only if it is about this Budget's options, with `ab2026_option__` keys. If the page costs the £10-a-child boost its slug names, that would be such an option (for example `ab2026_option__child_benefit_plus_10_per_child`), but nothing about it can be staged until the page is read.

A local copy saved by a browser session that passed the challenge would let a re-run stage these pages with `access: "local copy"`.
