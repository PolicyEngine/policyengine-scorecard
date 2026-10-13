# Fraser of Allander Institute and Scottish Fiscal Commission — Autumn Budget 2025 harvest (sources `fraser_of_allander`, `scottish_fiscal_commission`)

Staged 2026-09-24 from the primary documents. **82 claims** in `claims_staged.jsonl.gz`, **5 documents** in `manifest.jsonl`. Row contract, enums and rules: `../README.md`; measure keys: `../REGISTRY_KEYS.md`. Every `value` is verbatim (normalised to the unit as recorded in `normalization`); nothing is derived.

## Access recipe

- fraserofallander.org returns a Cloudflare "Just a moment..." challenge (HTTP 403) to `curl` with any User-Agent, and
  the Wayback availability API answered `429 Too Many Requests` throughout the session. The three posts were fetched
  from the site's own **WordPress REST API** (`/wp-json/wp/v2/posts?slug=<slug>`, HTTP 200), which returns the
  rendered post HTML plus `date`/`modified`. `access` is recorded as `direct`, `doc_type: html`, the manifest note
  explains the route; sha256 is of the API JSON response (saved as `wpjson_<slug>.json`).
- fiscalcommission.scot: publication page and the revised Full Report PDF (11 Feb 2026) fetched directly (HTTP 200);
  pypdf text; paragraphs 2.24–2.27, 4.5, 4.41, 4.64, 5.34–5.48 and Figure 5.6 read.

### Documents (manifest.jsonl)

- 2026-01-13 · Scotland’s Economic and Fiscal Forecasts – January 2026 (publication page) · `html` · access `direct` · 162,367 bytes · sha256 `6570ce76b3e7258e…` · **0 rows** — published 13 Jan 2026; documents revised 11 Feb 2026  
  <https://fiscalcommission.scot/publications/scotlands-economic-and-fiscal-forecasts-january-2026/>
- 2026-02-11 · Scotland’s Economic and Fiscal Forecasts – January 2026 (Full Report, revised 11 February 2026) · `pdf` · access `direct` · 1,824,362 bytes · sha256 `89afda22dae3aef6…` · **38 rows**  
  <https://fiscalcommission.scot/wp-content/uploads/2026/02/Scotlands-Economic-and-Fiscal-Forecasts-January-2026-revised-11-02-2026.pdf>
- 2025-11-26 · Budget 2025 reaction: meeting the (briefed) expectations · `html` · access `direct` · 28,480 bytes · sha256 `0f83d43237625496…` · **18 rows** — fetched through the site's WordPress REST API (/wp-json/wp/v2/posts?slug=...) because the HTML page returns a Cloudflare 'Just a moment...' challenge (HTTP 403) to curl; sha256 is of the API JSON response; modified 2025-11-26T17:35  
  <https://fraserofallander.org/budget-2025-reaction-meeting-the-briefed-expectations/>
- 2025-10-31 · Budget Preview #1: What might income tax changes by the UK Government mean for Scotland? · `html` · access `direct` · 13,918 bytes · sha256 `3f715d97e62128db…` · **14 rows** — fetched through the site's WordPress REST API (/wp-json/wp/v2/posts?slug=...) because the HTML page returns a Cloudflare 'Just a moment...' challenge (HTTP 403) to curl; sha256 is of the API JSON response  
  <https://fraserofallander.org/budget-preview-1-what-might-income-tax-changes-by-the-uk-government-mean-for-scotland/>
- 2025-11-13 · Budget Preview #2: Implications for Scotland of abolishing the two-child limit · `html` · access `direct` · 15,417 bytes · sha256 `c89e73c5344b7d8e…` · **12 rows** — fetched through the site's WordPress REST API (/wp-json/wp/v2/posts?slug=...) because the HTML page returns a Cloudflare 'Just a moment...' challenge (HTTP 403) to curl; sha256 is of the API JSON response; modified 2026-01-06  
  <https://fraserofallander.org/budget-preview-2-implications-for-scotland-of-abolishing-the-two-child-limit/>

## Coverage tally (seed bullets → claims staged → not staged)

Seed: `scores-3-other-shops.md` § Fraser of Allander Institute (7 bullets incl. SFC).

Staged (82 rows):
- Preview #1 (31 Oct, `arithmetic`): Table 1 BGA effects for four UK rate options × 2026-27/2027-28/2028-29 → 12 rows
  (`proposed_metric: block_grant_effect`); "£1 billion next year" headline → 1; the 2p income-tax/2p NICs switch
  "about £6 billion from 2027-28" (UK `revenue_change`) → 1.
- Preview #2 (13 Nov, `ukmod`): abolition −1pp relative AHC child poverty 2026-27; five reallocation options — four
  print "1ppt" and "an additional 10,000 children" (option 4 shows a dash: "impact is too small to report") → 9
  rows; TCLP £155m (SFC → restated), spillovers ~£34m, net £121m → 3 rows.
- Budget reaction (26 Nov, `ukmod`/`arithmetic`): −1pp and ~10,000 children; 95,000 children (HMT → restated) and
  "closer to 98,000" (own); £155m → £204m TCLP (SFC → restated); £121m net; Barnett consequentials table (resource
  45/307/185/−26/510; capital 0/23/200/4/83/309; HM Treasury → restated) → 18 rows.
- SFC January 2026 (revised 11 Feb; `sfc_forecast`): PA freeze "+£200 million each year" Scottish income tax (para
  4.5/4.41); PIP reversal +£476m BGA; two-child limit removal and TCLP cancellation −£152m (para 5.38); Figure 5.6 four
  series × six years (June 2025 TCLP; January update [A]; net effect on devolved payments [B]; [B]−[A]) → 24 rows;
  para 5.46 components (SCP −£1m/−£5m; Five Family Payments +£10m; UC take-up +£7m; DHP +£8m/+£15m) → 6; SCP caseload
  +7,000 children; DHP ≈ 2,000 → 4,000 UC child elements → 3; para 5.34 TCLP £155m/£204m levels → 2.

Not staged (with reason):
- Property income 22/42/47% rates (SFC para 4.64; FAI 26 Nov): explicitly not quantified ("leads to uncertainty for
  our forecasts from 2027-28"; "likely to be some impact on the Block Grant Adjustment").
- FAI Preview #1 statement that Scottish rate rises of 1p would "roughly" match the BGA cut — qualitative.
- Preview #3 "~£20bn gap" and the seed's "£220m" retail relief figure: the latter is NOT on the 26 Nov page (two
  verbatim searches by the seed; confirmed here — the page says only "there may be Barnett consequentials").
- SFC para 2.24–2.27 income-tax net-position revisions (−£274m in 2026-27 vs December 2024 etc.) — not Budget
  measures (forecast revisions); left for the OBR/SFC forecast lane.

### Row counts

- by `source`: fraser_of_allander 44, scottish_fiscal_commission 38
- by `attribution`: own 67, restated 15
- by `benchmark_class`: different_model 82
- by `source_model`: arithmetic 30, sfc_forecast 38, ukmod 14
- by `value_kind`: cumulative 2, point 80
- by `parse_confidence`: high 82
- by `measure_key`:
  - `ab2025__uc_child_element_remove_two_child_limit` 41
  - `null` 16
  - `ab2025__package_total_spending_policy_decisions` 11
  - `ab2025_option__income_tax_basic_rate_plus_2p` 4
  - `ab2025_option__scrap_two_child_limit` 4
  - `ab2025_option__income_tax_basic_rate_plus_1p` 3
  - `ab2025__personal_tax_thresholds_freeze_to_2031` 1
  - `ab2025__pip_not_proceeding_with_ss2025_eligibility_reforms` 1
  - `ab2025_option__income_tax_plus_2p_employee_nics_minus_2p_switch` 1

## Metrics, units and baselines used

- `proposed_metric: block_grant_effect` (README list) with `unit_concept: gbp`; `conditions.sign_convention`
  "positive = increase in Scottish Government funding (negative = larger income tax BGA deduction)";
  `conditions.mechanism` (income tax BGA; disability and carer payments BGA; Barnett consequentials). Producer
  definition (Preview #1): "the BGA is a proxy for how much revenue would be raised in the absence of devolution of
  the tax. If the UK Government raises rates, then a non-devolved system would have raised more money – and so the
  deduction is larger."
- `poverty_rate_change` (`percentage_points`) and `poverty_count_change` (`children_under_18`) with
  `conditions.housing_costs: ahc`, `poverty_line: relative_60_median` (FAI: "relative child poverty after housing
  costs"; the 60% threshold is the standard definition, implied), `geography: Scotland`.
- `benefit_cost` / `benefit_cost_change` (registered) for TCLP and devolved social security forecasts
  ("positive = increase in Scottish Government spending"); `proposed_metric: net_devolved_saving` (`gbp`) for the
  £121m "left to be spent on other policies"; `proposed_metric: caseload_change` (`children_under_18`) for SCP +7,000;
  `proposed_metric: affected_count` with `proposed_unit: uc_child_elements` for the DHP equivalence.
- `revenue_change` for the SFC "+£200 million each year" (positive = yield to the Scottish Government; `horizon`
  "each year from 2028-29", `period: 2029`) and the FAI £6bn UK switch.
- `measure_key`: UK rate options → `ab2025_option__income_tax_basic_rate_plus_1p` / `_plus_2p`; higher-rate-only
  options have no key (`null` + `reform_hint`); the switch → `ab2025_option__income_tax_plus_2p_employee_nics_minus_2p_switch`;
  pre-Budget abolition → `ab2025_option__scrap_two_child_limit`; announced removal →
  `ab2025__uc_child_element_remove_two_child_limit`; PA freeze → `ab2025__personal_tax_thresholds_freeze_to_2031`;
  PIP reversal → `ab2025__pip_not_proceeding_with_ss2025_eligibility_reforms`; Barnett table →
  `ab2025__package_total_spending_policy_decisions`; the five reallocation options → `null` + `reform_hint`.
- Baselines: all `baseline_policy: null` (FAI: SFC June 2025 benefit rates; SFC: June 2025 forecast as comparator,
  recorded in `conditions`).

### As staged

- registered `metric`: `benefit_cost` 14, `benefit_cost_change` 23, `poverty_count_change` 5, `poverty_rate_change` 6, `revenue_change` 2
- `proposed_metric`: `affected_count` 4, `block_grant_effect` 25, `caseload_change` 1, `net_devolved_saving` 2
- registered `unit_concept`: `children_under_18` 8, `gbp` 66, `percentage_points` 6
- `proposed_unit`: `uc_child_elements` 2
- `baseline_policy`: None 82 (null = current law at the scoring date)
- `proposed_baseline`: none

## Distinct values per `conditions` axis

- `basis` (2 distinct): forecast (38); static (31)
- `component` (2 distinct): Capital Block Grant (including FTs) (6); Resource Block Grant (5)
- `data` (2 distinct): HMRC Ready Reckoner and OBR March 2025 EFO (12); UKMOD; SFC June 2025 benefit rates (11)
- `fiscal_event` (1 distinct): autumn_budget_2025 (82)
- `fy` (6 distinct): 2026-27 (33); 2030-31 (12); 2027-28 (11); 2028-29 (11); 2029-30 (7); 2025-26 (6)
- `geography` (2 distinct): Scotland (81); UK (1)
- `horizon` (3 distinct): total over the years shown (2); each year from 2028-29 (1); from 2027-28 onwards (1)
- `housing_costs` (1 distinct): ahc (11)
- `mechanism` (3 distinct): income tax block grant adjustment (BGA) (13); Barnett consequentials (11); disability and carer payments BGA (1)
- `originator` (2 distinct): HM Treasury (12); Scottish Fiscal Commission (June 2025 forecast) (3)
- `poverty_line` (1 distinct): relative_60_median (11)
- `program` (16 distinct): TCLP cancelled plus knock-on devolved payments (6); TCLP cost, January 2026 update before the UK policy change (6); TCLP cost, June 2025 forecast (pre-Budget baseline) (6); knock-on devolved payments (SCP behavioural, Five Family Payments, UC take-up, DHP benefit-cap mitigation) (6); Two-Child Limit Payment (TCLP), Scottish Government mitigation (3); Discretionary Housing Payments (Benefit Cap mitigation) (2); Discretionary Housing Payments (Benefit Cap mitigation), expressed as UC child elements (2); Scottish Child Payment (behavioural response to the TCLP removed) (2); Two Child Limit Payment (TCLP), June 2025 forecast (2); Five Family Payments (UC take-up behavioural adjustment, in line with the OBR costing) (1); Five Family Payments (higher UC eligibility) (1); Scottish Child Payment (1); TCLP saving net of knock-on UC/Scottish Child Payment/DHP costs (1); TCLP saving net of spillovers (1); devolved social security (TCLP cancellation net of knock-on Five Family Payments and DHP spending) (1); spillovers: Discretionary Housing Payments for benefit-cap mitigation and devolved benefits linked to UC (about half each) (1)
- `scenario` (5 distinct): Option 1, costing about £121m in 2026-27, on top of the two-child limit abolition (2); Option 2, costing about £121m in 2026-27, on top of the two-child limit abolition (2); Option 3, costing about £121m in 2026-27, on top of the two-child limit abolition (2); Option 5, costing about £121m in 2026-27, on top of the two-child limit abolition (2); pre-Budget (TCLP retained) (2)
- `sign_convention` (8 distinct): positive = increase in Scottish Government spending (35); positive = increase in Scottish Government funding (negative = larger income tax BGA deduction) (13); positive = increase in Scottish Government funding (12); positive = increase in poverty (11); positive = resource freed for the Scottish Government (2); positive = increase in caseload (1); positive = yield to the Exchequer (1); positive = yield to the Scottish Government (1)
- `subgroup` (2 distinct): children in households that will benefit from the removal (April 2025 statistics) (1); children in households that will benefit from the removal, including those subject to the Benefit Cap (1)
- `tax` (1 distinct): Scottish Income Tax (1)
- `unit_population` (1 distinct): children (11)

## Attribution decisions

- FAI `own` / `different_model`: BGA arithmetic (HMRC ready reckoner × OBR), UKMOD poverty results, spillovers, the
  98,000 children (FAI's addition of benefit-capped households), £121m net.
- FAI `restated`: TCLP £155m/£204m (SFC June 2025 forecast), 95,000 children (HM Treasury), the Barnett consequentials
  table (HM Treasury) — 15 rows, dropped at ingest (#86).
- SFC `own` / `different_model` (`source_model: sfc_forecast`) for every SFC row, including the June 2025 TCLP
  baseline levels.
