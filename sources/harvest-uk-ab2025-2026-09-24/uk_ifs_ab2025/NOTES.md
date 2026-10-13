# uk_ifs_ab2025 — Institute for Fiscal Studies, Autumn Budget 2025 (staged 2026-09-24)

931 claims from 23 manifested primaries. `source: ifs`; `source_model: ifs_taxben` for TAXBEN
outputs, `survey_microdata` for the ASHE-only salary-sacrifice tables, `arithmetic` / `hmrc_data`
where the IFS states a non-model computation, and the OBR/HMT/DWP engines on `restated` rows.
Period is the FY END year throughout (`conditions.fy` carries the label). Seeds:
`SEED_INVENTORY/scores-1-official-ifs.md` § Institute for Fiscal Studies.

## Access recipe per document

ifs.org.uk article, publication, collection and data-item routes are Cloudflare-403 to curl.
Static `/sites/default/files/...` paths serve 200 with a browser User-Agent. Gated pages were
read from the Wayback Machine (`https://web.archive.org/web/<ts>id_/<url>`, raw bytes). The
availability API (`archive.org/wayback/available`) returned HTTP 429 all afternoon; the CDX index
(`web.archive.org/cdx/search/cdx?url=...&output=json&filter=statuscode:200`) worked and gave the
snapshot ids below. Flourish charts were read from `public.flourish.studio/visualisation/<id>/embed`
(`_Flourish_data` JSON, balanced-brace extraction; `_Flourish_settings` for titles, axis labels,
footers). Flourish *stories* redirect through a service-worker stub at `public.flourish.studio/story/<id>/embed`;
the story body (which names its visualisation ids) is served by `https://flo.uri.sh/story/<id>/embed`.

- 14 Nov 2025 comment "How are frozen tax thresholds reshaping who pays personal taxes?" — Wayback
  `20251121231532` (also 20251124171134, 20251126203709, 20251209131222). Its three Flourish
  figures: 26088869 (Figure 1, taxpayer shares 1990-91..2029-30 under Extension / No freeze / Current),
  26089263 (Figure 2, HRT vs earnings percentiles 2014-15..2029-30), 26092052 (Figure 3, decile
  distribution of the extension: Net income / Direct taxes / Means-tested benefits).
- 27 Nov 2025 data item "Effect of new threshold freezes on employee tax liabilities in 2030-31" —
  Wayback `20260102163741`; Flourish 26497565 (151 points, earnings 0..150,000 step 1,000).
- 23 Oct 2025 comment "Options for reforming the two-child limit" — Wayback `20251125161459`
  (also 20251110230438 … 20260309093209). Figure 2 = Flourish 25591304; Figure 3 = story 3377796 →
  visualisations 25590658 (six options × ten metrics) and 25591134 (average income change by AHC
  decile, two facets); Figure 1 = story 3376325 → 25599322/25599328/25599330/25599331/25599335/
  25599340/25644622 (HBAI poverty trends; not claim-mined). Nesta deck PDF direct.
- 26 Nov 2025 "Autumn Budget 2025: initial response" — Wayback `20251126193537` (19:35 UTC, the
  earliest); the 1 Dec capture `20251201121156` (sha256 82fd91b2…) carries identical numbers.
- 27 Nov 2025 collection page (Helen Miller's opening remarks, key-chart list) — Wayback `20251201200622`.
- Waters, Delestre and Ridpath decks — direct PDFs (sha256 identical to the 2026-08-02 manifest).
- 13 May 2026 salary-sacrifice report — publication page Wayback `20260513223736` (full report text);
  report PDF `Salary-sacrifice-pension-contributions.pdf` (22 pp.) and data workbook
  `underlying_data_0.xlsx` (sheets fig1..fig10) direct. The seed's URL
  `Assessing-the-announced-reform-to-salary-sacrifice-pension-contributions-L-Obrien.pdf` is the
  19-slide launch deck, fetched and manifested but not claim-mined (every number is in the report).
- 13 Oct 2025 Green Budget chapter 4 PDF direct (Table 4.1 already staged in 2026-08-02).

Not fetched: the other five 27 Nov key-chart Flourish items (PSNB change, current budget deficit,
tax changes by parliament, >£2m sales map, RHDI by parliament) — their headline straplines are staged
from the collection page; `Distributional-analysis-2025.xlsx` linked from the 25591134 footer
(the Flourish JSON carries the same data).

## Already in sources/harvest-uk-2026-08-02/uk_ifs (NOT re-staged)

- Flourish 26495404 decile chart (22 rows, 2026-27 and 2030-31 × Poorest..Richest + All).
- Waters deck: £13bn by 2030-31 with the 25%/£21bn/£8bn band; 5.2m / 4.8m freeze-as-a-whole
  counts; two-child limit £3.2bn and 560,000 families.
- Green Budget 2025 Table 4.1 (28 revenue_change rows incl. the deck £13bn).
- GB2024 Table 6.5 and Figure 6.1 workbook; TAXBEN guide.
Grep: `gunzip -c sources/harvest-uk-2026-08-02/uk_ifs/claims_staged.jsonl.gz | grep <value>`.

## Coverage tally (seed bullets → staged)

"Options for tax increases" (13 Oct, 15 bullets): Table 4.1 values already staged; new here =
£51.1bn existing freezes, £10.5bn/£26.8bn March-2021 freeze re-estimate, £5.4bn fuel-duty freeze
cost, £1.2bn bank surcharge to 6%, £4.4bn G/H surcharge, the £20bn illustrative package, £3,800/
£4,560 G/H worked bills, 37.4% tax/GDP (restated), VAT reliefs £83.1bn/£45.8bn/£30.6bn/£19.0bn/£7.8bn,
fuel duty £24.4bn/£17.4bn (17 rows). Not staged: £14.1bn "mostly from the highest-income tenth"
(qualitative), 62%/69.5% marginal rates (rates, not scores), £22bn/£1.5bn/£6bn pension options and
£30bn relief cost (already Table 4.1 or no year), IHT 6.2%/9.7% deaths (OBR restated, not a Budget
score), 4.3% council tax growth assumption.

"Options for reforming the two-child limit" (23 Oct, 7 bullets): all quantified bullets staged
(21 text rows + 60 + 20 + 264 Flourish rows + 1 deck annotation). The seed's "under-5 / under-1
values not recoverable" is CORRECTED: Flourish 25590658 gives them exactly (under 5: 290,493
children, 2.00 ppt, £1,517,181,649, 424,155 households; under 1: 65,711, 0.45 ppt, £352,118,998,
106,901). Poverty context 27%→31%, absolute lines £23,000/£30,000, Cook +3ppt staged; Figure 1
poverty trend series not staged (HBAI levels; DWP lane).

"How are frozen tax thresholds…" (14 Nov, 5 bullets): all staged (23 text rows + 6 + 14 + 33
Flourish rows). Figure 3 decile values, which the seed said were "not extracted", are exact
(Flourish 26092052).

"Initial response" (26 Nov, 6 bullets): 26 rows, 59% restated. Not staged: "tax rises exceed any
parliament since 1970" (unquantified), "borrowing higher in each of the next three years".

27 Nov event (10 bullets): freeze-by-earnings series (151 exact rows), Miller remarks (17), Waters
slide 4/7 (8), Delestre deck (18), Ridpath deck (11). Not staged: Waters slide 5 HRT-percentile chart
(unlabelled; the same series is exact in Flourish 26089263 from the 14 Nov piece and staged there),
Ridpath PSNB decomposition bars and "largest tax rising parliament" bars (unlabelled), waterfall
labels other than the headroom endpoints.

Salary-sacrifice report (13 May 2026, 7 bullets): 29 text rows + 212 workbook rows; every figure
(1-10) is exact from `underlying_data_0.xlsx` — the seed's "Figures 3-10 unlabelled" is superseded.
Not staged: the OBR behavioural discussion beyond the £0.7bn (qualitative).

## Distinct condition values per axis (this family)

- fy: 2010-11, 2015-16, 2019-20, 2022-23, 2023-24, 2024-25, 2025-26, 2026-27, 2027-28, 2028-29, 2029-30 (354 rows), 2030-31 (171).
- geography: UK (923), England (8). basis: static (822), current inflation forecasts (4), post_behavioural (1).
- income_group: all, decile_1..decile_10 (household income deciles; equivalised AHC for the two-child
  charts, equivalised for the salary-sacrifice Figures 9-10, unstated equivalisation for 14 Nov Figure 3),
  earnings_decile_1_2, earnings_decile_3..earnings_decile_10 (ASHE earnings deciles; the report groups
  deciles 1 and 2 for disclosure — spelled `earnings_decile_1_2`, not `earnings_decile_1` / `_2`).
- income_axis: earnings_decile (50); employee earnings (£, 2025-26 prices) (151, with
  conditions.earnings = the £ point); equivalised household income decile (82); equivalised household
  income decile, after housing costs (264).
- housing_costs: ahc (335). poverty_line: absolute_60_fye2011_median (40), absolute_50_fye2011_median
  (12), absolute_40_fye2011_median (12), relative_60_median (7).
- horizon: long run (two-child limit fully rolled out) (361; period 2035 marker), by the time all cars
  are electric (2; period 2050 marker), 2024 to 2029 (parliament, calendar years) (2), 2026-27 to 2028-29,
  from 2029-30, from 2029-30 onwards, five years to 2029-30.
- option (two-child limit): Scrap two-child limit; Exempt children under age 1; Exempt children under
  age 5; Introduce 50% child element [for third and subsequent children]; Three child limit; Exempt
  familes with earnings from work (producer's spelling). child_element_share: 10% (£350) … 100% (£3510).
- facet: Among all households; Among households with families of three or more children; the two
  Figure-1 taxpayer facets. scenario: Extension / No freeze / Current worlds; employee-NICs-only vs
  employer NICs passed onto wages. sector, employer_size, age_group, sex, nics_component,
  contribution_band as in the workbook headers. household_type: worked-example labels verbatim.
- sign_convention: 37 spellings, all "positive = …" sentences.

## Proposals used (producer definition quoted)

- `employee_tax_liability_change` (gbp): "Real increase in tax liability (£, 2025-26 prices)" for an
  employee at each earnings point, 2030-31; "Assumes rise in employer NICs is incident on employees."
- `affected_share` / `affected_count` (share/households/children): "48% of employees in the highest
  earnings decile would be directly affected by the policy"; "No. of households affected".
- `salary_sacrifice_share`: "% of employees salary sacrificing into a pension".
- `average_additional_nics_per_employee` (gbp): "Mean extra yearly NICs per employee assuming no
  behavioural change … calculated over all employees, i.e. including those who are not affected".
- `share_of_additional_nics_liability`: "69% of the total additional NICs liability is borne by the top
  earnings decile and their employers".
- `average_income_change_among_affected` (gbp): "the average change among those affected in this decile is £888 per year".
- `share_no_change`: "Around 65% of households in the top decile would experience no change in income".
- `pct_change_after_tax_income_component` (percent): Figure 3's "Direct taxes" and "Means-tested
  benefits" contributions to the "Net income" % change.
- `taxpayer_share`: "73% of people aged 16 or over"; `tax_threshold_level` (gbp): Figure 2 "Higher-rate threshold" series.
- `cost_per_child_lifted_out_of_poverty` (gbp): "Cost per child out of poverty (£ per year)".
- `household_tax_change` (gbp): "a full-time minimum wage worker paying £137 per year more in tax".
- `weekly_hours_at_minimum_wage_to_pay_income_tax` (proposed_unit `hours_per_week`); `marginal_retention_per_pound_earned` (gbp).
- `average_energy_bill_change` (gbp/percent): "Combined impact on average annual bills: 2026-27 to 2028-29: £131 (7%) reduction".
- `motoring_externality_cost` (proposed_unit `pence_per_km`): "Motoring externalities, p/km, 2024–25".
- `fiscal_headroom`, `forecast_revenue_change`, `forecast_spending_change`, `forecast_borrowing_change`,
  `spending_pressure`, `spending_share_of_headroom_increase`, `real_spending_growth`, `tax_to_gdp_ratio`,
  `share_of_property_sales_over_2m`, `congestion_cost_share`, `share_of_affected_contributions`,
  `poverty_line_level`, `poverty_rate_gap`, `average_loss_share_of_disposable_income`,
  `employment_rate_change`, `threshold_real_value`.
- proposed_baseline (7 rows): "IFS 'no freezes at all' world: the April 2021 thresholds uprated to 2029
  (endnote 6: 'relative to the April 2021 thresholds being uprated to 2029')".
- baseline_policy `ifs_2cl_fp_removal_rolled_out` on all 361 two-child-limit option rows (long-run,
  fully rolled out; the registered IFS Green-Budget world).

## Attribution decisions

- `own` (872): TAXBEN and ASHE computations, IFS arithmetic, Flourish/xlsx data.
- `restated` (59): OBR EFO aggregates (headroom, £26bn, £12.7bn/£13bn/£8bn freeze yields, 5.2m/4.8m
  "freeze as a whole" counts), HMT costings (£2.6bn salary sacrifice and capital-income rises, £0.4bn
  HVCTS, £1.9bn eVED, £4.9bn efficiency), the Government's 450,000 / 3.1ppt poverty estimate
  (`dwp_policy_simulation_model`), £4.7bn/£2.6bn/£0.7bn salary-sacrifice costing, Cook (2025) +3ppt.
- `benchmark_class: administrative_fact` (18): HBAI poverty levels, Land Registry sale shares, RTI
  earnings percentiles, SPI taxpayer share.
- Miller's "£220 / £600" and the deck's "£390" are the rounded annotations of the exact Flourish
  plateaus 220.1462 / 603.4957 / 393.5896 (both staged; the exact series carries the measure).

## Inventory corrections

- Seed: 23 Oct under-5 / under-1 exemption values "not recoverable" → recovered exactly (above).
- Seed: 14 Nov Figure 3 "chart values not extracted" → exact via Flourish 26092052.
- Seed: salary-sacrifice Figures 3-10 "unlabelled" → exact via the published data workbook.
- Seed listed the salary-sacrifice PDF as the L-Obrien file; that is the launch deck. The report is
  `Salary-sacrifice-pension-contributions.pdf` (22 pp., sha256 9d08cabad3…).
- Seed's Flourish 26497565 readings (£36.0 / £220.1 / £270.5 …) match the data to one decimal.
- Freeze-by-earnings plateau at £5,000-£11,000 (35.99089) is the employer-NICs secondary-threshold leg
  (`ab2025__employer_nics_secondary_threshold_freeze_to_2031`), noted per row; the series as a whole is
  keyed to `ab2025__personal_tax_thresholds_freeze_to_2031`.

## Not staged

- Figure 1 (23 Oct) HBAI poverty trend series (Flourish story 3376325) — levels for the DWP lane.
- Ridpath deck PSNB bars, parliament tax-change bars; Waters HRT-percentile slide (exact twin staged
  from 26089263); 26 Nov unquantified comparisons; "Be the Chancellor".
- Five 27 Nov key-chart Flourish items other than 26495404 and 26497565.
