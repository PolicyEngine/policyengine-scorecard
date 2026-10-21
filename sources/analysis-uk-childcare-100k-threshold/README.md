# £100,000 childcare dashboard: comparables record

The first record under the pre-publish comparables gate (docs/COMPARABLES.md). It is a
backfill: the dashboard was published on 12 October 2026, before the gate existed.

- **Published figure** (pinned in `analysis.json`): the static cost of the 30 funded hours, £0.434bn
  in 2027-28 and £0.505bn in 2029-30, from `PolicyEngine/uk-childcare-100k-threshold` at
  `f25f0db` (`data/results.json`).
- **What the search found** (2026-10-21, every UK producer): CenTax's Table 4.2 (static and net,
  three scenarios) and the Centre for British Progress's net fiscal impact. DfE's FOI estimate
  and the Conservative Party's £700m are logged as found but not staged, because neither has a
  readable primary.
- **The gap**: CenTax's central static cost is 46% (2027-28) and 49% (2029-30) above the
  published figure. The annotation cites microcosm#1126, the Microcosm hours draw that put
  families' use of the extended hours at about 15 of 30, and the dashboard's rerun on the
  corrected draw (uk-childcare-100k-threshold#8).
- **Status**: the dashboard was taken off policyengine.org on 21 October 2026
  (PolicyEngine/policyengine-app-v2#1379) while its costing is revised. The record stays: the
  miss stays on the page. A republished version needs its own prepublish search appended to
  `search_log.json`. Its new figures are pinned as further `pe_estimates`, and the
  re-harvest picks the dashboard up again once it is back in `apps.json`.

The same CenTax and CBP publications are staged at producer level in
`sources/centax-childcare-100k/` and `sources/cbp-rates-and-wrongs/` (#207), with
PolicyEngine's certified-pair counterpart.
