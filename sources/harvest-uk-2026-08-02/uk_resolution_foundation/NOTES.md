# Resolution Foundation harvest — 2026-08-02

Source slug: `resolution_foundation` (research institute; source_model
"resolution_foundation", never administrative fact). Underlying engine for
their distributional/projection work: **the IPPR Tax Benefit Model** run on
DWP FRS/HBAI microdata (every distributional figure sources "RF projections
including use of the IPPR Tax Benefit Model"). RF is therefore a *third*
UK microsimulation lineage alongside IFS (TAXBEN) and government (Policy
Simulation Model / IGOTM) — good triangulation value.

## Coverage
15 artifacts manifested (all sha256'd, honest UA, robots.txt fully
permissive `Allow: /`, ~3-4s politeness delay, zero bypasses needed).
71 staged claims from 5 publications:

| pub | date | staged |
|---|---|---|
| Living Standards Outlook 2026 | 2026-02-10 | 27 |
| The Living Standards Outlook 2025 | 2025-06-26 | 14 |
| Stairway to headroom (Autumn Budget 2025 response) | 2025-11-27 | 12 |
| Catching up? (April 2026 uprating spotlight) | 2025-10-22 | 8 |
| Happy new tax year 2026 | 2026-04-02 | 10 |

Downloaded but not claim-mined (context/coverage): Black holes and
consolidations (pre-Budget briefing), Low Pay Britain 2025 (minimum wage
flagship), State of the nations (devolved social security), Delivering
dignity (Scotland ADP), Measuring household income (RHDI-vs-HBAI
methodology), New Year Outlook 2026, Credit where credit's due (mortgage
rules — NOT a UC report despite the title), Bye bye baby (birth rates),
Much ado about PuFins (public financial institutions), It's personal
(taxation) (PDF extracts 0 text lines via pdftotext -layout — needs OCR or
-raw retry; valid Word-produced PDF).

## Chart-data downloads: none (site practice changed)
The task expected chart-data downloads. Current RF report pages ship **PDF
only** — no per-report chart-data xlsx/zip anywhere on the 15 pages
fetched (checked hrefs for xlsx/zip/csv/"chart data"; probed obvious
upload-path names → 404). The site-wide "Data" nav item points to just two
standing dashboards (housing-indicators; RTI-based employment estimates).
All staged values were transcribed verbatim from PDF text (pdftotext
-layout), mostly from prose + printed chart labels, so axis-only chart
series (e.g. full vigintile growth curves in LSO Figure 6, full vigintile
gain/loss bars in HNTY Figure 1 / Stairway Figure 19) could NOT be
extracted — only the labelled points and prose-stated group aggregates.

## Conventions used in claims_staged.jsonl
- Fiscal years Apr–Mar: `period` = start year (2026-27 → 2026),
  `time_basis` fiscal_year, `conditions.fy` verbatim.
- GBP values: `proposed_unit: "gbp"` (UnitConcept lacks it). value_kind
  "usd" is the closed-vocab currency kind — flagged here, not renamed.
- Income concept: RF poverty and income-growth work is **equivalised
  household disposable income, after housing costs (AHC)** — stamped on
  every distribution row (`income_concept`, `equivalisation`). LSO 2026
  Figure 15 title says "relative poverty after housing costs" explicitly;
  LSO 2025 Figure 15 note defines relative poverty as below 60% of
  median in the given year.
- Geography verbatim: UK for LSO/HNTY headline rows; **GB** for the
  two-child-limit impact-assessment counts (DWP IA covers GB); Scotland
  rows labelled Scotland.
- `attribution` field (8 rows): values RF **cites from government** (HMT
  Budget 2025 Table 4.1 costings; DWP final-stage impact assessment
  510k families/£4,560; government −450k child-poverty estimate; UC
  rebalancing net cost £330m/−£210m; EV charge £1.9bn) — these are NOT
  RF-model outputs; ingest should either reroute to the government source
  or keep with the attribution tag. Everything without `attribution` is
  RF's own modelling.
- `reform_hint` (26 rows): plain-language mapping to a PE-runnable reform
  (two-child limit repeal Apr 2026; UC standard allowance CPI+2.3%
  Apr 2026 (+£6/wk, phased to +4.8% vs CPI-only by 2029-30); UC health
  element halved+frozen for new claims (£50/wk); IT/NICs threshold freeze
  extension to Apr 2030; mansion tax; EV per-mile charge).

## Methodology (verbatim extracts, LSO 2026 Annex 1, pp.34-37) — for the assumptions registry
- Base data: "nowcasting and forecasting the latest household income data
  (DWP's Family Resources Survey and Households Below Average Income
  statistics, 2023-24) to the years from 2024-25 through to 2029-30."
- Reweighting: "We reweight the population to match ONS forecasts for
  demographic change by age and gender" ("reweight2" in Stata; ONS
  2022-based projections, **migration category variant**); labour force
  participation from "the OBR's March 2025 outlook".
- Earnings: "all employee and self-employed earnings are uprated equally
  in each year. Overall wage growth is constrained to match ONS figures
  for the outturn period and OBR figures for the projection period";
  wage floor modelled each year with "some 'spillover effect' for those
  just above the wage floor"; NLW extension to 21-22 in 2024-25 and
  "(provisionally) to those aged 18-20 by 2029-30"; "the wage floor
  beyond 2025-26 rises in line with average earnings."
- Take-up: "We model incomplete take-up of the main means-tested
  benefits. For example, we assume **80 per cent take-up of Universal
  Credit**... we assume a rise in **Pension Credit take-up from 65 per
  cent to 70 per cent** following Winter Fuel Payment reform."
- UC rollout: "We assume that full roll-out of Universal Credit is
  completed in 2026-27."
- Two-child limit: "applied to children born from April 2017, and so
  affects a growing proportion of the caseload each year. It is removed
  from April 2026 in line with Government policy."
- Deflator: "we create a specific deflator for 'after housing costs'
  income, in line with DWP definitions" (removes housing costs from CPI);
  OBR November 2025 CPI forecast is the starting point.
- Rents: ONS Price Index of Private Rents for nowcast; "Beyond September
  2025, private rents are assumed to rise in line with average earnings,
  with a 12-month lag."
- **Changes-not-levels discipline**: "we apply income growth rates (and
  absolute changes in poverty and inequality metrics) from our modelling
  to the 2023-24 outturn data, rather than directly using the projected
  levels." → RF projected *levels* inherit any error in HBAI 2023-24;
  treat RF rows as changes-anchored-to-outturn when comparing.
- Not modelled: benefit sanctions; mixed-age-couple Pension Credit
  transitional protection ("We instead use the new eligibility rules for
  everyone, in every year"); detailed migration; tenure change; Council
  Tax Support variation by LA.
- PIP: "We model receipt of Personal Independence Payment based on future
  caseload projections."
- Deductions: benefit deductions modelled "consistent with the 2025 Fair
  Repayment Rate reform" (15% cap on UC deductions, down from 25%).

Stairway to headroom Box 2 (distributional-analysis scope, pp.37-39):
models "just over half (52 per cent) of the total tax changes announced
since Autumn Budget 2024 and the majority (85 per cent) of the total
welfare spending changes; we model £20 billion of the total £34 billion";
RDEL analysis covers "70 per cent" (£47bn of £67bn); "our distribution
analysis of changes to tax and benefits and our distributional analysis of
changes to public spending cannot sensibly be combined"; Treasury's
Budget-2025 distributional analysis models 2028-29 while RF models
2029-30 — direct RF-vs-HMT comparisons must adjust for this.

## Diagnosis seeds / errata
1. **Source typo in Catching up? (p.3)**: "cost the Government £800m in
   2026-27, rising to **£1.85 million** in 2029-30" — plainly £1.85bn.
   Staged 2026-27 only, typo flagged in the row note.
2. **Cross-publication cost drift**: same UC over-indexation measure
   costed £800m (Catching up?, Oct 2025) vs £810m (HNTY, Apr 2026) for
   2026-27; LSO 2026 reports the *net* rebalancing package (uplift +
   health-element cut) at £330m net cost 2026-27 → −£210m saving 2029-30.
   Three different scopes — do not treat as contradictions.
3. **Same-group different-vintage gains**: poorest-fifth average gain from
   two-child-limit removal is **£290** (HNTY, 2026-27 impact) vs **£360**
   (Stairway, 2029-30 impact in 2025-26 prices) — year and price base
   differ, both staged with conditions.
4. RF flags (LSO 2025, p.31) that HBAI outturns are "expected to be
   revised in March 2026 as part of a welcome stats overhaul using
   administrative data", with "a likely consequence... an (even) lower
   pensioner poverty rate" — vintage risk on any pre-2026 RF level.

## UK triangulation (overlap with IFS / OBR / DWP on the same measures)
- **Child poverty projections**: RF LSO 2026 (33% → 30% relative AHC,
  −420k children in 2026-27) vs **DWP's own February 2026 projections**
  ("also project a fall in child poverty from 33 per cent in 2025-26 to
  30 per cent in 2026-27" — RF footnote 21) vs IFS's living-standards
  projections. Three-way UK poverty triangle on identical
  concept/period.
- **Two-child limit repeal**: RF (£2.4bn 2026-27 → £3.1bn 2029-30, HMT
  scorecard; 510k families; £4,560 avg gain; govt −450k children) — IFS
  and JRF publish rival costings/poverty impacts of the same reform;
  PE-runnable as a parametric UK reform.
- **Budget 2025 decile impacts**: RF Stairway (2029-30, AHC deciles) vs
  **HM Treasury's own distributional analysis** (2028-29) vs IFS
  post-Budget analysis — same event, three models, documented scope
  difference (52% of tax measures modelled).
- **April 2026 uprating rates** (3.8% CPI-linked / 4.8% State Pension /
  6.2% UC / 6.8% under-25 UC / 1.5% existing UC-health / 0% LHA): pure
  parameter checks against policyengine-uk uprating parameters; also
  OBR EFO Nov 2025 carries the same UC Act 2025 path.
- **RHDI vs HBAI**: Measuring-household-income spotlight (2026-07-31)
  reconciles ONS RHDI with DWP HBAI — useful when Scorecard compares
  OBR (RHDI-based) with RF/IFS (HBAI-based) income-growth rows.

## Blockers / follow-ups
- No chart-data files exist to fetch (see above) — full decile/vigintile
  series would need RF correspondence or figure digitisation.
- It's personal (taxation) PDF yields no text via pdftotext; retry with
  `-raw`/OCR next pass.
- Annex 1 of LSO 2025 has per-nation child poverty projections (table not
  parsed this pass — PDF table extraction needed).
- Low Pay Britain 2025 (minimum wage bite/coverage) downloaded but
  unmined; State of the nations Scotland section cites Scottish
  Government cumulative impact assessment (SCP −10pp/−100k children in
  2026-27) — government-model numbers, left unstaged deliberately.
