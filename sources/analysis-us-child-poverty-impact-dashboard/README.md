# Child poverty impact dashboard: comparables record

A backfill under the pre-publish comparables gate (docs/COMPARABLES.md): the dashboard was listed on
policyengine.org on 15 September 2026, before the gate existed. Searched on 21 October 2026, every US
producer.

- **What is pinned.** The page has no default reform and no static results: the report wizard starts
  empty and every figure is computed on demand on the dashboard's Modal backend. The record pins the
  figures the dashboard's own repository publishes, at the commit policyengine.org serves
  (`PolicyEngine/child-poverty-impact-dashboard` at `d918ca2`):
  - `analysis/reform_scores/results.json`, its scorecard of seven representative reforms for 2026
    (restoring the 2021 CTC amounts, a $3,000 child allowance and the Working Parents Tax Relief Act,
    each scored for California; a $2,000 Young Child Tax Credit and a 100% CalEITC adjustment factor in
    California; a $2,000 Empire State Child Credit for children under 4 and repeal of the dependent
    exemption in New York). For each: net budget cost and the change in child and all-ages SPM poverty;
    for the six expansions, children lifted out of poverty too.
  - `analysis/state_audit/ANALYSIS_BUILDP.md`, whose Build P audit gives -4.2 percentage points of child
    poverty for restoring the 2021 CTC in California. The same note gives -6.5 points on the sparse
    Populace pin; that figure is not pinned, because the note records neither its engine nor its run and
    the dashboard no longer serves that dataset.

  Both files are byte-identical at the launch-day production deployment (`dfd03a8`, 15 September) and
  at `d918ca2`. The repository's state audit also sets the dashboard's 2026 baseline child poverty rates
  and state credit costs beside Census and official figures; those are baseline levels, which belong in
  producer-level sources, so this record holds only reform effects.
- **Vintage.** results.json records no engine or dataset. Its runs went to the deployed Modal endpoint,
  not the repository pin: SWEEP.md at the same commit says the deployment was behind the pin, predates
  policyengine-us 1.731.0, and labels it about 1.729.5, and the New York dependent-exemption row matches
  that sweep to every digit. The backend loaded the per-state CPS files from 29 May to 7 July 2026, then
  a sparse Populace pin, then Microcosm Build P from 20 August. The About page says results from before
  the August switch are not comparable with what the live page computes (live backend on 21 October:
  policyengine-us 1.825.2, Build P release `592ae5d6`). The Build P figure is the only pinned one on the
  current dataset.
- **The comparison.** One, for 2026, within the 25% threshold, against the June run: ITEP's Working
  Parents Tax Relief Act table puts California's 2026 cost at $2.523bn; the dashboard's is $2.401bn
  (-4.9%).
- **A pairing labelled concept mismatch.** New York's FY2027 tax expenditure report puts the dependent
  exemptions at $264.0m for tax year 2026; the dashboard has repeal raising $265.9m, 0.7% more. Same
  reform and year, but the report counts New York State tax on resident and nonresident returns, while the
  dashboard counts federal and state income tax, including New York City tax for households its file
  places in the city, less benefits, for resident households. The claim names the estimate as its
  nearest, as the worked example does, and the annotation cites the code and report pages.
- **Staged, not compared.** The rule: a producer's own estimate of the same reform at the geography the
  dashboard publishes (California for the federal and California reforms, New York for the New York
  ones), the latest vintage of each quantity, plus the two national estimates the dashboard's own prior
  file (`analysis/reform_scores/priors.yaml`) cites beside its scenarios. Cousins and other national
  figures are in the search log's notes.
  - California estimates of the 2021 CTC design against the $2,000 credit: CBPP (34% fewer children in
    poverty in tax year 2021; 318,000 children lifted in 2024), Urban (-6.8 points, -33.3%, 613,000
    children, 2018), PPIC (32% on the California Poverty Measure, 2018 data) and ITEP ($10.7bn in 2023).
  - CPSP's California row for the whole 2021 credit against no credit (7.5 points, 41.6%, 2021).
  - The priors: CPSP's national 43% (the whole 2021 credit against none) and Garfinkel et al.'s national
    $96.8bn (2018 incomes).
  - Each is for an earlier year, another baseline or another geography, so no 2026 estimate shares its
    quantity; each carries `pe_missing`.
- **The California poverty effects differ.** CBPP, Urban and PPIC put the 2021 design's effect, against
  the $2,000 credit, at about a third of child poverty (34%, 33.3%, 32%), against 14.1% in the June
  scorecard; Urban's 6.8 points compare with 3.4 in June and 4.2 on Build P. One difference is in the
  dashboard's code: its "Restore 2021 expanded CTC" option sets only the ARPA amounts, refundability and
  phase-out and leaves the credit's age limit at 17, so the restoration gives 17-year-olds nothing (they
  keep the $500 credit for other dependents), although the option's description says ages 6-17. The 2021
  design covered them, and the texts of all four producers of the 2021-design estimates (CBPP, Urban,
  PPIC, ITEP) say their estimates do. The years, baselines and datasets also differ, and the gate does not
  compare across years, so the record does not size these differences.
- **No estimate for California or New York** was found of the $3,000 child allowance, the $2,000 Young
  Child Tax Credit, a 100% CalEITC adjustment factor or the $2,000 young-child Empire State Child Credit,
  in any year. National $3,000 allowances that replace the CTC (Shaefer et al. 2018, the National
  Academies 2019) and a 2017 Tax Policy Center estimate of the total cost of the 2015 CalEITC design at a
  100% factor are in the search log's notes.
- **Search limits.** The session's web-search allowance ran out part-way; the remaining searches used
  producers' own site search, sitemaps and Internet Archive indexes. HTML pages on cbo.gov, jct.gov,
  cbpp.org and ppic.org refuse scripted requests; the manifest names each Internet Archive capture it
  holds. CBPP's analysis of the Working Parents Tax Relief Act, cited in the sponsor's press release, was
  not found.
