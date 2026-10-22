# £100,000 childcare dashboard: comparables record

The first record under the pre-publish comparables gate (docs/COMPARABLES.md). It is a
backfill: the dashboard was published on 12 October 2026, before the gate existed.

- **Published figure** (pinned in `analysis.json`): the static cost of the 30 funded hours, £0.434bn
  in 2027-28 and £0.505bn in 2029-30, from `PolicyEngine/uk-childcare-100k-threshold` at
  `f25f0db` (`data/results.json`).
- **What the search found** (2026-10-21, every UK producer): CenTax's Table 4.2 (static and net,
  central with the high- and low-cost scenarios as a range, for 2027-28 and 2029-30) and Table
  B.1's 2028-29 row, and the Centre for British Progress's net fiscal impact (Tables 2 and 3,
  2026-27 to 2029-30). DfE's FOI estimate and the Conservative Party's £700m are logged as found
  but not staged, because neither has a readable primary.
- **The gap**: the published static cost is 45.8% (2027-28) and 48.5% (2029-30) below CenTax's
  central static cost (£0.80bn and £0.98bn), and below the low-cost end of CenTax's range too. The
  annotation cites microcosm#1126, the Microcosm hours draw that put families' use of the
  extended hours at about 15 of 30, and the dashboard's rerun on the corrected draw
  (uk-childcare-100k-threshold#8). CenTax's net figures sit beside the dashboard's net cost as a
  concept mismatch; CBP's net gain disagrees in sign with it, which the bunching annotation
  explains.
- **Status**: the dashboard was taken off policyengine.org on 21 October 2026
  (PolicyEngine/policyengine-app-v2#1379) while its costing is revised. The record stays: the
  miss stays on the page. A republished version moves these figures to `superseded_estimates`,
  pins its new ones in `pe_estimates`, and needs a new search against its new results files
  (kind `reharvest`) before it goes back up. The re-harvest picks the dashboard up again once it
  is back in `apps.json`.

The same CenTax and CBP publications are staged at producer level in
`sources/centax-childcare-100k/` and `sources/cbp-rates-and-wrongs/` (#207), with
PolicyEngine's certified-pair counterpart.
