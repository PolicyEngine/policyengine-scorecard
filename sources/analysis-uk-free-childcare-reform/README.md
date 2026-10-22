# Free childcare hours and a 75% subsidy: comparables record

A backfill under the pre-publish comparables gate (docs/COMPARABLES.md): the dashboard was
listed on policyengine.org on 3 September 2026, before the gate existed.

- **Published figures** (pinned in `analysis.json`): 21 estimates from
  `PolicyEngine/free-childcare-reform` at `1a832f1` (the commit of the live Vercel deployment,
  29 September 2026), `dashboard/public/data/free_childcare_reform_results.json`, the file the
  dashboard fetches (byte-identical to `data/free_childcare_reform_results.json`). They are the
  static cost and the cost with the central labour supply response of the free-hours leg
  (England), the 75% subsidy leg (UK, and its England share) and both legs together, for
  2027-28 to 2029-30: £1.97bn, £4.84bn and £6.64bn static in 2027-28. The free-hours leg is
  costed from age 1, not 9 months: FRS ages are whole years, so the 9-month floor binds at 1
  (`reforms.py`, which puts the missing cohort at about £0.44bn). The file's own
  provenance block says it was generated on 2 September 2026 at analysis commit `5150486`
  from a dirty working tree; it has not changed since `ba56ebb`.
- **Not pinned**: net employment entrants (the scorecard has no registered employment-change
  metric), distributional gains, the take-up, Universal Credit scope and fee-base
  sensitivities, and the extended-entitlement take-up variant. No producer published a
  figure comparable to any of them.
- **What the search found** (2026-10-21, every UK producer): no external estimate of either
  leg or of both together. Three near analogues are staged, none compared:
  - CenTax's row "Abolish the threshold for the first 15 Hours to Under-3s": one group the
    free-hours leg also reaches (under-3s of working parents above £100,000), static and net,
    central scenario, 2027-28 to 2029-30, on both of the report's income tests: actual ANI
    (Table 4.3, its primary results, and Table B.1) and today's expected ANI (Table B.2). The
    rows match the free-hours estimates on metric, unit, period and time basis, so each names
    its nearest estimate and the annotation `centax-over-100k-group-inside-free-hours` says
    why the two differ.
  - IPPR, Towards a childcare guarantee (September 2022): the only costing found of a 75%
    childcare subsidy (read as a scheme total; 95% for families on means-tested benefits;
    replacing Tax-Free Childcare and the UC element), and universal 15 hours for under-twos
    and for two-year-olds, all on the 2022 system.
  - NEF, The Universal Family Childcare Promise (July 2025): the analysis's own "closest
    published analogue", a replacement of the whole system with 15 hours from 9 months plus
    an earnings cap.
- **Found but not staged**: CASE and the Early Education and Childcare Coalition's Reforming
  childcare subsidies (19 October 2026). Its report refused every fetch, and the LSE release
  gives its cost only as a percentage increase on an unstated base.
- **Not staged, other reforms**: the analysis's other listed comparables (the IFS costing for
  the Sutton Trust, 2021; HM Treasury and OBR on the 2023 expansion; the Women's Budget
  Group, 2017) score reforms the analysis does not make. Each is logged in `search_log.json`.
- **Gaps**: no claim is compared, so none is over the threshold.
- **Not read**: obr.uk answered every fetch with a Cloudflare challenge, so the OBR entry
  rests on search results; ifs.org.uk HTML pages were read through a reader proxy.

Primaries were downloaded and hashed on 2026-10-21 outside the repository; `manifest.jsonl`
holds their SHA-256s. The CenTax PDF is the same file as in
`sources/analysis-uk-childcare-100k-threshold/`.
