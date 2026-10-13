# CenTax — Autumn Budget 2025 harvest (source `centax`)

Staged 2026-09-24 from the primary documents. **87 claims** in `claims_staged.jsonl.gz`, **4 documents** in `manifest.jsonl`. Row contract, enums and rules: `../README.md`; measure keys: `../REGISTRY_KEYS.md`. Every `value` is verbatim (normalised to the unit as recorded in `normalization`); nothing is derived.

## Access recipe

Both policy-report PDFs and both landing pages were fetched directly with `curl` (browser User-Agent, HTTP 200);
PDFs text-extracted with pypdf. Dates are the landing-page dates (4 Sep 2025; 14 Aug 2025); PDF CreationDates are one
day earlier (3 Sep; 13 Aug). Landing pages carry the "Key Findings" / "Executive Summary" verbatim and are used as the
primary for those sentences; table values come from the PDFs (Tables 3, 4, 5; Figure 3/4 notes).

`source_model` is `hmrc_administrative_microdata` on every row (pseudonymised HMRC administrative data: universe of
partners, tax year 2020; HMRC IHT estates data 2018–2022). "Tax Reforms for Growth" (5 Nov 2025) was not fetched:
the seed checked it and it has no £ figures. The Tax Journal non-dom piece is paywalled (only the standfirst is
visible) → nothing to stage.

### Documents (manifest.jsonl)

- 2025-08-14 · Policy Report: The Impact of Changes to Inheritance Tax on Farm Estates (landing page, executive summary) · `html` · access `direct` · 177,006 bytes · sha256 `93b062d72c24ae15…` · **29 rows**  
  <https://centax.org.uk/policy-brief-the-impact-of-changes-to-inheritance-tax-on-farm-estates/>
- 2025-09-04 · Policy report: Equalising National Insurance on Partnership Income: Revenue and Distributional Effects (landing page, key findings) · `html` · access `direct` · 162,085 bytes · sha256 `0df29279a82bac03…` · **12 rows**  
  <https://centax.org.uk/policy-report-equalising-national-insurance-on-partnership-income-revenue-and-distributional-effects/>
- 2025-08-14 · The Impact of Changes to Inheritance Tax on Farm Estates · `pdf` · access `direct` · 1,954,923 bytes · sha256 `62dcfef3154b9007…` · **0 rows**  
  <https://centax.org.uk/wp-content/uploads/2025/08/AdvaniGazmuribarkerMahajanSummers2025_TheImpactOfChangesToInheritanceTaxOnFarmEstates.pdf>
- 2025-09-04 · Equalising National Insurance on Partnership Income: Revenue and Distributional Effects · `pdf` · access `direct` · 834,699 bytes · sha256 `9325dcc42fae95ea…` · **46 rows**  
  <https://centax.org.uk/wp-content/uploads/2025/09/AdvaniGazmuribarkerLonsdaleSummers2025_PartnershipNICs.pdf>

## Coverage tally (seed bullets → claims staged → not staged)

Seed: `scores-3-other-shops.md` § CenTax (7 bullets incl. TPA's "£2bn lawyer tax", which is staged in `uk_tpa`).

Staged (87 rows):
- Partnership NICs static revenue: £2.4bn total, Table 3 components (+£4.5bn, −£2.1bn, −£0.1bn), £0.6bn allowance
  cost → 5 rows. Post-behavioural Table 4: seven ETI rows (0.0 → £2.4bn … 0.25 → £1.9bn central … 0.5 → £1.5bn)
  with `conditions.pct_change_from_static` carrying the printed % column → 7 rows; landing-page £1.9bn headline → 1.
- Counts and shares: N = 191,000 affected; "fewer than 200,000" of "roughly 457,000" partners above the exempt
  amount; 66% with no additional tax → 4 rows.
- Distribution: 98% of revenue from the top decile, 58% from the top 0.1%, >70% of affected in the top decile,
  bottom 50%: 9% of affected and <0.4% of revenue; London 46% of static revenue; Table 5 ten industries × (revenue,
  share liable) → 26 rows.
- Marginal effective rate +6.9pp (additional-rate), 6.9–9.6pp range; retention rate 58.6% → 53.5% → 5 rows.
- Descriptive 2020 partnership income (administrative_fact): top 0.1% 46% of partnership income vs <5% of employment
  income; Kensington 1,800 partners / >£1.8bn; 65,000 partners in Wales and NI; Liverpool Walton £1.5m; solicitors
  20% / >£300,000; finance >£600,000; >25% in 12 constituencies → 10 rows.
- Farm estates (AB2024 APR/BPR reform; AB2025 froze and made transferable the allowance): 480–600 estates/yr, 205
  small family farms (43%, 15% of tax), passive-investor rows (32%, 15/yr, 3%, 2%), value bands (>80% from 34% over
  £5m; 55% from >£10m; <1% from the 11% under £2m), income bands (10% / 47% / 23%), ownership types (17%/37%,
  64%/42%), payability (49% <5pp; 15/yr; 25/yr; 86%; ~70/yr; ~40/yr), two revenue-neutral alternative allowances
  (£5m minimum-share rule; £2m upper limit) → 29 rows.

Not staged (with reason):
- "≈ 1p on the higher rate of income tax" equivalence and "a two-partner firm needs >£90,000 profit" — thresholds
  /equivalences, not scoreable values (kept in notes).
- The Table 4 "% change from static" column is carried in `conditions`, not as rows (derivable from the two
  printed revenues; the printed percentages are preserved verbatim in the condition value).
- Farm estates: the £1.5m allowance "if the wealthiest respond more than the central estimate" — the landing-page
  sentence is truncated in the extracted text ("then i"), so it was not read verbatim → not staged.
- Regional shares (Figure 4) other than London are chart-only → not staged.
- 26 Nov "Budget 2025 reaction" explainers: no fresh CenTax numbers (restated HMT/OBR list in the seed) → not fetched.

### Row counts

- by `source`: centax 87
- by `attribution`: own 87
- by `benchmark_class`: administrative_fact 14, different_model 73
- by `source_model`: hmrc_administrative_microdata 87
- by `value_kind`: central 2, point 71, range_high 6, range_low 8
- by `parse_confidence`: high 77, medium 10
- by `measure_key`:
  - `ab2025_option__nics_on_partnership_income` 48
  - `null` 39

## Metrics, units and baselines used

- `revenue_change` (registered) for all revenue rows; `conditions.sign_convention` "positive = yield to the
  Exchequer" (or "positive = cost to the Exchequer" for the £0.6bn allowance cost), `conditions.basis` static /
  post_behavioural, `conditions.scoring_method` as the caller asked, `conditions.elasticity_of_taxable_income`.
  Producer definition (p.21): "raise £2.4 billion on a static basis for the 2027 tax year"; (p.24) post-behavioural
  "Using the central elasticity from Saez, Slemrod and Giertz (2012), we estimate the proposed reform would raise
  £1.9 billion. This implies a reduction of 20% in revenue relative to the static costing."
- `proposed_metric: affected_count` (README list) with `unit_concept: persons` (partners) or `proposed_unit: estates`
  (farm estates per year of deaths); `proposed_metric: affected_share` with `unit_concept: share` (denominator in
  `conditions.denominator`); `proposed_metric: revenue_share` (share of the reform's revenue by group; CenTax p.25:
  "Almost all (98%) of the revenue from the proposed reform would come from individuals in the top decile by total
  income"); `proposed_metric: tax_base` (README list) for the 457,000 partners above the exempt amount;
  `proposed_metric: marginal_effective_tax_rate_change` (`percentage_points`; p.88 of the landing page: "the marginal
  effective rate would rise by 6.9 percentage points"); `proposed_metric: retention_rate` (`percent`; p.24 "the
  average retention rate would go from 58.6% to 53.5% on a static basis"); `proposed_metric: revenue_neutral_allowance`
  (`gbp`) for the £5m/£2m alternative combined allowances.
- Registered `income_share`, `income_aggregate`, `income_statistic`, `taxpayer_count` for the 2020 descriptive rows.
- `period`: partnership rows 2026-27 (`period: 2027`; "the 2027 tax year" in the PDF, "in 2026-27" on the landing
  page); descriptive rows `period: 2020`, `fy: 2019-20` ("2020 tax year" as printed, medium confidence); farm-estate
  rows 2026-27 ("uprated to 2027", reform from April 2026).
- `measure_key`: `ab2025_option__nics_on_partnership_income` for all partnership rows; farm-estate rows have
  `measure_key: null` with a populated `reform_hint` (the AB2024 reform; the AB2025 linkage is in `note`).
- Baselines: all `baseline_policy: null`.

### As staged

- registered `metric`: `income_aggregate` 2, `income_share` 4, `income_statistic` 2, `revenue_change` 23, `taxpayer_count` 2
- `proposed_metric`: `affected_count` 10, `affected_share` 24, `marginal_effective_tax_rate_change` 3, `retention_rate` 2, `revenue_neutral_allowance` 2, `revenue_share` 12, `tax_base` 1
- registered `unit_concept`: `gbp` 29, `percent` 2, `percentage_points` 3, `persons` 5, `share` 40
- `proposed_unit`: `estates` 8
- `baseline_policy`: None 87 (null = current law at the scoring date)
- `proposed_baseline`: none

## Distinct values per `conditions` axis

- `basis` (2 distinct): static (65); post_behavioural (8)
- `component` (4 distinct): 1) Partnership NICs (1); 2) Reduction in Income Tax (1); 3) Reduction in Class 4 NICs (1); Partnership Allowance (£10,500) (1)
- `constraint` (1 distinct): at least as much revenue as the planned reform (2)
- `denominator` (6 distinct): additional tax from farm estates (6); all impacted farm estates (6); additional tax from the reform (2); all farm estates (2); impacted farm estates (2); all farm estates benefiting from APR and/or BPR (1)
- `design` (2 distinct): minimum share rule (APR/BPR claim at least 60% of the estate) (1); upper limit of £10 million of relief (1)
- `elasticity_of_taxable_income` (7 distinct): 0.25 (2); 0.0 (1); 0.1 (1); 0.2 (1); 0.3 (1); 0.4 (1); 0.5 (1)
- `fiscal_event` (1 distinct): autumn_budget_2025 (87)
- `fy` (2 distinct): 2026-27 (77); 2019-20 (10)
- `geography` (6 distinct): UK (81); Kensington (2); 12 constituencies (11 in London) (1); Liverpool Walton (1); London (1); Wales and Northern Ireland (1)
- `geography_level` (2 distinct): westminster_constituency (4); ITL1 (1)
- `incidence` (1 distinct): full incidence on partners, zero behavioural response (5)
- `income_concept` (3 distinct): partnership income (5); total income (all taxpayers) (5); employment income (1)
- `income_group` (3 distinct): top_0.1pct (3); bottom_50pct (2); decile_10 (2)
- `industry` (11 distinct): Solicitors (4); Accounting, and auditing activities (2); Activities of patent and copyright agents; other legal activities (2); Fund management activities (2); General medical practice activities (2); Management consultancy activities (2); Mixed farming (2); Other activities auxiliary to financial services (2); Other engineering activities (2); Real estate agencies (2); finance (some sectors) (1)
- `industry_classification` (1 distinct): 5-digit SIC (10)
- `measure_type` (1 distinct): per year of deaths, uprated to 2027 (27)
- `pct_change_from_static` (7 distinct): -16% (1); -20% (1); -24% (1); -32% (1); -40% (1); -8% (1); 0% (1)
- `response_assumption` (1 distinct): central (1)
- `scenario` (2 distinct): baseline (before Partnership NICs) (1); reform (with Partnership NICs) (1)
- `scoring_method` (2 distinct): post_behavioural (elasticity of taxable income) (8); static (4)
- `sign_convention` (2 distinct): positive = yield to the Exchequer (22); positive = cost to the Exchequer (1)
- `statistic` (2 distinct): mean partnership income per partner (1); mean partnership profits per partner (1)
- `subgroup` (24 distinct): partners liable (10); farm estates with an APR/BPR claim covering less than 20% of the estate (likely passive investors) (4); ‘small family farms’ (APR/BPR share > 60% of estate and estate value < £5m) (3); affected partners (range across current marginal rates) (2); affected partners, average (2); impacted estates worth over £5 million (2); impacted farm estates valued at less than £2 million (2); landowners (2); owner-farmers (2); partners (2); partners liable to Partnership NICs (2); additional-rate taxpayer (1); current partners with no additional tax due (1); deceased with income over £100,000 (1); deceased with income over £500,000 (1); deceased with total income under £25,000 per year (five-year average before death) (1); farm estates facing an increase larger than 15pp (all valued at over £7.5 million) (1); farm estates worth less than £2.5 million facing an increase larger than 5pp (1); impacted estates over £10 million (1); impacted farm estates able to pay the entire IHT bill from non-farm assets (1); impacted farm estates facing a residual bill greater than 20% of farm income if paid in ten-year instalments (1); impacted farm estates unable to pay the entire IHT bill from non-farm assets (1); impacted farm estates with an effective tax rate increase of less than 5 percentage points (1); partners with profits above the Partners’ Exempt Amount (£5,000) (1)
- `unit_population` (1 distinct): farm estates (estates of individuals who died owning farm assets on which relief was claimed) (27)
- `uprating` (1 distinct): 2020 profits uprated to the 2027 tax year with OBR wage growth (1)

## Attribution decisions

- Revenue estimates, counts of affected, shares of revenue, marginal rates: `own` / `different_model` (CenTax's own
  modelling on HMRC data).
- Descriptive administrative statistics (2020 partnership income distribution, Kensington/Wales/Walton, industry
  averages; farm-estate population shares such as "32% of all farm estates … less than 20% of the estate",
  owner-farmer/landowner shares of *all* farm estates, the 457,000 partners): `own` / `administrative_fact`.
- Nothing restated: the two reports report only CenTax's own output. TPA's rounding of the £1.9bn to "£2bn" is in
  `uk_tpa` as `restated`.
