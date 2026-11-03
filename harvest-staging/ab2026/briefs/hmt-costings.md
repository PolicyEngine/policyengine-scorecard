## Your assignment: family `uk_hmt_costings` (source `hm_treasury`)

**Primary:** HM Treasury, *Budget 2026: Policy costings*, 28 October 2026.
- URL: https://assets.publishing.service.gov.uk/media/6ae1883fe4367e5c8b0467df/AB26_Policy_Costing.pdf
- Local copy: /Users/maxghenis/reviews/scorecard-ab2026-harvest/local-primaries/hmt-2026-10-29/AB26_Policy_Costing.pdf (sha256 f716efad…, the same bytes on 28 and 29 October).

The document sets out the methodology for each costed measure.
- **Measure key:** each measure's section names a Table 6.1 measure; match it to its key in REGISTRY_KEYS.md by title and line.
- **What to stage:** every number the document prints for a measure:
  - the static costing;
  - each behavioural adjustment and the post-behavioural costing, per fiscal year;
  - tax bases, behavioural parameters (elasticities) and the number affected;
  - any uncertainty rating.
- **Precedent:** follow the AB2025 `uk_hmt_costings` family exactly: its metric choices for static versus behavioural legs, `scoring_method` conditions, proposed metrics such as `costing_uncertainty_rating` and `tax_base`, and its sign convention.
- **Cross-check:** where a final costing is printed, compare it with Table 6.1 (`uk_hmt_tables`) for the same line and year. Report any mismatch; don't fix it.

The document is OGL, so quotes may be whole sentences or cells.
