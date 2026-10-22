# Middle East war and UK living standards: comparables record

A backfill under the pre-publish comparables gate (docs/COMPARABLES.md). The dashboard was
listed on policyengine.org on 25 September 2026, before the gate existed.

- **Published figures** (pinned in `analysis.json`, 42 estimates, all for 2027-28): for each of
  the three annual stress tests (Summer 2026 prices, Sustained escalation, Severe escalation),
  the mean cost of the energy, fuel and food price rises per household, the energy channel per
  household, and the people and households newly below the anchored poverty line; and the
  gross outlay of each of the ten policy responses. They are read from
  `PolicyEngine/impact-iran-war-living-standards` at `45592bb`, the Vercel production
  deployment the live page serves, `dashboard/public/data/iran_impact_results.json`, SHA-256
  `382d64b9…`; the live page's copy has the same hash.
- **These are the figures live today, not those of 25 September.** The results file was
  regenerated eleven times on 28 September. Against the results file of the 25 September
  production deployments (the last, `928851a`, at 16:07 UTC), the accelerated uprating cost
  moved from £1.11bn, £2.64bn and £4.51bn to £0.66bn, £3.64bn and £7.27bn, the combined package
  from £38.07bn, £54.62bn and £79.0bn to £37.63bn, £55.61bn and £81.76bn, and the household
  poverty count was added; the other pinned figures are unchanged.
  The file's own provenance records generation at `976b7a8` from a dirty tree, before the
  commit that holds it.
- **What the search found** (2026-10-21, every UK producer): 34 claims from the Resolution
  Foundation, IFS, HM Treasury, NIESR, JRF, Cebr and the TUC. Most are for 2026 or 2026-27,
  while the dashboard models 2027-28 only, so each says in `pe_missing` why it is not compared.
  They include the price-cap figures the dashboard sets beside its own energy channel (RF's
  ~£500 if prices were sustained, and its £130, £230 and £440 July 2026 cap scenarios).
- **The comparisons**: two, both constructed across worlds. IFS puts the annual cost of making
  the electricity VAT cut permanent at about £1.5bn and RF the cut's annual cost in future years
  at £1.7bn; the dashboard's full-year 2027-28 extension costs £1.55bn under Summer 2026 prices,
  3% above IFS and 9% below RF. Neither producer names a year, so the 2027-28 reading is noted
  on each claim; the dashboard's version also covers Northern Ireland, which the enacted cut
  does not, and omits the non-household supplies the relief covers. Under the escalation
  scenarios the same extension costs £1.95bn and £2.56bn.
- **Annotated**: the IFS cost of making the 5p fuel duty cut permanent and freezing duty for a
  further year (£2.7bn, or £3.2bn on Barclays inflation) and RF's cost of reversing the cut
  gradually (over £1bn in 2027-28) score different policies from the dashboard's 5p cut
  (£2.18bn), so they are recorded as concept mismatches, not compared.
- **Not staged**, with the reason in `search_log.json`: figures whose primary could not be
  read (IFS's VAT-cut response, behind Cloudflare; Cornwall Insight's cap forecasts, including
  the £288 JRF cites, behind a 401); figures a producer repeats from others (the Government
  costs RF and IFS restate, the 2022 schemes); budgets a producer chose rather than estimated
  (RF's £3.75bn envelopes and £2bn targeted discounts); options with no counterpart among the
  dashboard's ten; Ofgem's announced caps, which anchor the Summer 2026 prices scenario; and
  inflation figures, since the dashboard's CPI additions are scenario parameters, not
  estimates.

One of the dashboard's own external comparisons links the wrong page: it cites RF's 2 April
2026 release for the ~£500 bill rise, which is in RF's 4 March release. Its NIESR figure of
about 200,000 households is NIESR's own rounding of the 195,000 staged here.
