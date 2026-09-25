# Harvest: Autumn Budget 2025 scores from every producer (#136)

Staged 2026-09-24 from the primary documents. One family directory per producer group, each
holding `NOTES.md` (access recipe, coverage tally, what was NOT staged and why), `manifest.jsonl`
(one line per primary document with its sha256) and `claims_staged.jsonl.gz` (one line per
claim). The seed for every family is the 24 Sep 2026 inventory in `SEED_INVENTORY/`
(one bullet per claim: `[TAG] measure | metric type | value | basis | model/data | publication,
date | URL`). The harvest is vendored data, ingested by `scorecard_db/ingest_uk_ab2025.py`
(#138, merged 2026-09-25) whose exact accounting reads `read = ingested + dropped` against
the row counts pinned here (`COUNTS.json`). Family `uk_ukmod_ab2025` was added on
2026-09-25 (UKMOD's own Budget brief, CeMPA WP 3/26).

## Rules (from `sources/harvest-2026-08-02/README.md`, extended)

1. **Verbatim values only.** `value_raw` is the string as printed; `value` is the same number
   normalised to the unit (GBP not GBP m; a percent as a percent; a share as a fraction) with
   the conversion written in `normalization`. A number read off a chart with no data label is
   `value_kind: approx_chart_reading` and says so in `note`. Nothing is derived from two other
   numbers (a ratio, a gap, a sum): stage the inputs and let the derivation be downstream.
2. **Never invent an enum value.** `metric` and `unit_concept` are set only when the value is
   one of the registered ones below; otherwise `metric: null` + `proposed_metric` (or
   `unit_concept: null` + `proposed_unit`). A proposal is a suggestion; the ingest's disposition
   table is where it becomes a decision.
3. **Every row names its measure.** `measure_key` is a key from `data/uk/ab2025_measures.json`
   (`ab2025__…` for announced measures, `ab2025_option__…` for options). A level, projection or
   context claim that scores no measure has `measure_key: null` and `reform_hint: null`.
4. **Attribution is a fact of the harvest.** `attribution` is `own` (the producer's own
   computation), `restated` (a government/OBR figure the producer repeats; staged so the tally
   is complete, dropped at ingest under the #86 rule) or `same_assumptions` (computed with
   PolicyEngine, e.g. the Fabian Society's freeze row). `benchmark_class` follows:
   `different_model` for an independent model, `administrative_fact` for administrative or
   survey data, `same_assumptions` for PolicyEngine-derived rows.
5. **`period` is the financial-year END year** (`models.py`): FY 2026-27 → `2027`, with
   `conditions.fy = "2026-27"`. Calendar-year claims use the year with `time_basis: annual`.
6. **`fiscal_event` is the slug `autumn_budget_2025`** on every row, whatever the publication
   calls it.
7. **Baselines are named, not implied.** `baseline_policy` is a registered label
   (`scorecard_db/baselines.py`) or `null` for current law at the scoring date; a world the
   registry does not yet name goes in `proposed_baseline` with the producer's own definition
   quoted in `NOTES.md`, and is registered before ingest (#13).
8. **Primaries, not summaries.** Every publication in `manifest.jsonl` was fetched (directly,
   via the Wayback Machine, or as a Flourish data endpoint) and hashed. A figure whose primary
   could not be read is recorded in `NOTES.md` under "Not staged", never as a claim
   (the seed inventory expected Policy Exchange's PDF to be CAPTCHA-gated; the harvest read
   the primary directly and staged 84 rows from it, see `uk_thinktank_misc/NOTES.md`).
9. **HMT Figures 1.A/1.B bar readings are NOT staged** (`data/uk/hmt_da_packages.yaml`
   `value_availability_rule`, #61). Figure 1.C's table and Table 2.C are already in
   `sources/harvest-uk-2026-08-02/uk_hmt`, as is Table 4.1; do not re-stage them.
10. **Worked examples are staged for the tally**, not for comparison: single-household
    examples (`proposed_metric: household_tax_change` etc.) are mode-3 material (#63) and
    the ingest drops them with a tallied reason. **Bank and City macro calls are NOT in
    this harvest**: they are the #55 lane (`uk_macro_calls`, tranche 4), as are NIESR's
    NiGEM rows; only NIESR's household/static rows are staged here (`uk_niesr/NOTES.md`).

## Row contract (`claims_staged.jsonl.gz`)

```
source              producer slug (see the slug table)
source_model        the ENGINE or method behind the number: "ifs_taxben", "landman_ttm" (the
                    IPPR/RF/JRF/NEF tax-benefit model), "ukmod_b1.13", "ukmod_b2025.08",
                    "hmt_costing_obr_certified", "hmrc_personal_tax_model", "dwp_policy_simulation_model",
                    "obr_efo_forecast", "nigem", "wpi_hardship_model", "arithmetic",
                    "administrative_data", "survey_microdata", "policyengine_uk", …
metric | proposed_metric        registered Metric value, or null + proposal
unit_concept | proposed_unit    registered UnitConcept value, or null + proposal
value               number normalised to the unit
value_raw           string as printed
normalization       how value came from value_raw ("GBP bn x 1e9 -> GBP", "as printed")
value_kind          point | central | range_low | range_high | approx_chart_reading | cumulative
period              int, FY END year (or calendar year)
time_basis          fiscal_year | annual | point_in_time
conditions          {fiscal_event: "autumn_budget_2025", fy: "2026-27", geography: "UK" | "England" |
                    "Scotland" | "UK_excl_northern_ireland" | …, sign_convention: "positive = yield to the
                    Exchequer" | "positive = cost to the Exchequer" | "positive = gain to households" | …,
                    basis: static | post_behavioural | forecast | outturn, scoring_method: …,
                    income_group: decile_1 … decile_10 | quintile_1 … | vigintile_1 … | tertile_1 … | all,
                    housing_costs: ahc | bhc, poverty_line: relative_60_median | absolute_60_fye2011_median | …,
                    horizon: "2029-30", subgroup: …, program: …, measure_type: …, note: …}
                    — every key a string, every value a string
reform_hint         the producer's own words for the world scored, or null for levels/baselines
measure_key         registry key or null
attribution         own | restated | same_assumptions
benchmark_class     different_model | administrative_fact | same_assumptions
baseline_policy     registered label or null;  proposed_baseline: free text when unregistered
publication         {title, url, date (YYYY-MM-DD), publisher, primary_sha256, locator (page/table/figure), access (direct|wayback|flourish|govuk_api)}
source_table        table / figure / chart id as printed
source_column       column / cell / series label as printed
quote               the sentence or cell carrying the number, verbatim
note                anything a reader needs (scope notes, exclusions, chart-reading method)
parse_confidence    high | medium | low
status              ok
```

Registered `Metric` values (models.py): eligible_count, eligibility_rate, participant_count,
participation_rate, participation_gap_count, poverty_rate, poverty_rate_change,
poverty_count_change, poverty_count, benefit_cost, operating_cost_change, revenue_change,
caseload, enrollment, pct_change_after_tax_income, tax_expenditure, income_aggregate,
tax_liability, taxpayer_count, average_tax_rate, average_tax_amount, unclaimed_benefit_amount,
gini, income_statistic, income_share, cash_requirement_change, gainer_count,
average_annual_gain, benefit_cost_change, taxpayer_count_change,
average_household_income_change, share_gaining, share_losing, spending_share,
benefit_uprating_rate, real_income_growth, gdp_level_effect, cpi_inflation_effect,
supply_side_impact, decisions_effect_on_borrowing. Exchequer costings are `revenue_change`
with the published sign carried in `conditions.sign_convention` and the value NOT re-signed.
Proposals in use across families (so the ingest sees one spelling): `affected_count`,
`affected_share`, `household_tax_change`, `take_home_pay_change`, `pension_pot_projection`,
`costing_uncertainty_rating`, `effective_tax_rate`, `severe_hardship_count_change`,
`block_grant_effect`, `fiscal_headroom`, `exchequer_impact_static`, `tax_base`.

Registered `UnitConcept` values: persons, adults_18plus, children_under_18, children,
families, households, benefit_units, gbp, gbp_per_week, gbp_per_month, gbp_per_household,
share, percent, percentage_points, index_0_1, jobs, percent_of_real_gdp,
percent_of_potential_gdp.

Registered baseline labels relevant here: `current_law` (null), `pre_ab2025`,
`hmt_no_policy_change_from_ab2024`, `obr_pre_measures_autumn_budget_2025__policy_parameters`,
`ifs_2cl_fp_removal_rolled_out`, `hmrc_indexed_baseline_spring_2025`. Registered with this
port (baselines.py, tranche 1): `rf_permanent_measures_since_ab2024`,
`rf_start_of_parliament_policy`, `jrf_pre_ab2025_projection_path`,
`ukmod_b2025_09_fixed_baseline_line`, `end_of_parliament_pre_ab2025`.

## Producer slugs (`source`)

| slug | producer | family dir |
|---|---|---|
| hm_treasury | HM Treasury (policy costings, red book, Table 4.1) | uk_hmt_costings, uk_hmt_redbook |
| uk_hmrc | HMRC tax information and impact notes | uk_hmrc_tiins |
| obr_efo | OBR Economic and fiscal outlook tables, boxes, supplementary notes, uncertainty ratings | uk_obr_tables |
| ifs | Institute for Fiscal Studies | uk_ifs_ab2025 |
| resolution_foundation | Resolution Foundation | uk_rf_ab2025 |
| jrf | Joseph Rowntree Foundation | uk_jrf |
| ippr | IPPR | uk_ippr |
| cpag | Child Poverty Action Group | uk_cpag |
| ukmod | UKMOD (CeMPA, ISER, University of Essex) — the Budget brief WP 3/26 | uk_ukmod_ab2025 |
| policy_in_practice | Policy in Practice | uk_pip |
| entitledto | entitledto | uk_entitledto |
| trussell_wpi | Trussell / WPI Economics | uk_trussell_wpi |
| niesr | NIESR | uk_niesr |
| centax | CenTax | uk_centax |
| tax_policy_associates | Tax Policy Associates | uk_tpa |
| nef | New Economics Foundation | uk_nef |
| fraser_of_allander, scottish_fiscal_commission | FAI / SFC | uk_fai_sfc |
| ppi | Pensions Policy Institute | uk_thinktank_misc |
| wbg | Women's Budget Group | uk_wbg |
| cebr | Cebr | uk_cebr |
| smf | Social Market Foundation | uk_smf |
| public_first | Public First | uk_publicfirst |
| demos | Demos | uk_demos |
| fabian_society | Fabian Society | uk_fabians |
| taxpayers_alliance, cps, onward, tax_justice_uk, iea, policy_exchange, loughborough_crsp | the smaller shops | uk_thinktank_misc |
| deloitte, ey, aj_bell, hargreaves_lansdown, quilter, fidelity, royal_london, aegon, rsm, moore_kingston_smith, blick_rothenberg, kpmg, which, moneyweek, investengine, ig, rathbones, evelyn_partners, pwc | commercial firms and platforms (worked examples) | uk_cases_commercial |

Bank macro calls (`uk_macro_calls`) are tranche 4 and are not staged here.

## `manifest.jsonl` line

```
{"url": …, "title": …, "date": "YYYY-MM-DD", "publisher": …, "sha256": …, "bytes": …,
 "doc_type": pdf | html | xlsx | flourish_json | govuk_api_json, "access": direct | wayback | flourish | govuk_api,
 "retrieved": "2026-09-24", "wayback_snapshot": … (when access = wayback), "note": …}
```

Primaries are not vendored (they are hashed); a text extract may be kept under `raw/` when it
is small and the source is fragile (Wayback-only pages).
