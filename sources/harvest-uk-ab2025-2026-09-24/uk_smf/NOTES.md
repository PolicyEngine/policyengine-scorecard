# Social Market Foundation — Autumn Budget 2025 harvest (source `smf`)

Staged 2026-09-24 from the primary documents. **40 claims** in `claims_staged.jsonl.gz`, **3 documents** in `manifest.jsonl`. Row contract, enums and rules: `../README.md`; measure keys: `../REGISTRY_KEYS.md`. Every `value` is verbatim (normalised to the unit as recorded in `normalization`); nothing is derived.

## Access recipe

"The impossible Budget" PDF (CreationDate 2025-11-24; the publication page says "Published: 21 November 2025" and the
seed dates it 21 Nov — `date` 2025-11-21), its publication page, and the 26 Nov Budget-reaction page
(`article:published_time` 2025-11-26T15:49) fetched directly (`curl`, browser User-Agent, HTTP 200). pypdf/BeautifulSoup
text. `source_model: arithmetic` on every row (SMF's own estimates and adjustments; the gambling figure comes from
SMF's "Duty to Differentiate").

### Documents (manifest.jsonl)

- 2025-11-26 · Chancellor’s pay-per-mile tax risk collapsing UK EV market, think tank says (Budget reaction) · `html` · access `direct` · 71,200 bytes · sha256 `76b3e410e6196852…` · **7 rows** — article:published_time 2025-11-26T15:49; modified 2025-12-08  
  <https://www.smf.co.uk/chancellors-pay-per-mile-tax-risk-collapsing-uk-ev-market-think-tank-says/>
- 2025-11-21 · The impossible Budget (publication page) · `html` · access `direct` · 54,002 bytes · sha256 `82908c53d97332a7…` · **0 rows**  
  <https://www.smf.co.uk/publications/the-impossible-budget/>
- 2025-11-21 · The impossible Budget: Options and expectations for the Government’s ‘smorgasbord’ (briefing paper) · `pdf` · access `direct` · 222,372 bytes · sha256 `2d4d585893b39c3a…` · **33 rows** — PDF CreationDate 2025-11-24; publication page says published 21 November 2025  
  <https://www.smf.co.uk/wp-content/uploads/2025/11/The-impossible-Budget-November-2025-1.pdf>

## Coverage tally (seed bullets → claims staged → not staged)

Seed: `scores-3-other-shops.md` § Social Market Foundation (9 bullets).

Staged (40 rows):
- Gambling package "around £1.9bn" (likelihood 4/5) → 1.
- Housing 'fairness' taxes £3.9bn; vacant property tax "up to £2bn"; 676,000 vacant properties; non-resident purchase
  tax "more than £1.3bn"; ~16,000 sales; rapid sales tax "around £500m"; ~25,000 flips; ~£1bn profits → 8.
- Fuel duty: £3.4bn a year from unfreezing; cumulative £150bn (next year) and £200bn (2028) foregone → 3.
- Minimum unit tax: £659m total, £481m single-rate, £177m spirits uplift; retailer windfall £600m (E&W) and £65m
  (Scotland); MUP alone reduces receipts by "a little over £300 million" → 6.
- Triple lock: double lock £2.6bn over five years; earnings link £3.2bn; inflation link ~£23.1bn; triple lock +£20bn
  over five years → 4.
- Housing First: ~£75m first year; ~£45m thereafter; nearly £200m net fiscal benefit over five years; £8,000–£10,000
  saved per person per year → 5.
- Other options: SME investment +£60bn/yr; compliance costs ≥£15.4bn; £430bn excess cash; WHP £13.2bn, ECO ~£2bn/yr,
  BUS £295m (government → restated) → 6.
- EV reaction (26 Nov): OBR 440,000 fewer sales and 130,000 grant uptake (restated); SMF 88,000 and "net loss of EVs of
  over 350,000" → 4. Fuel duty freeze: top fifth £153 / bottom fifth £56 → 2; "£14 billion cost over the following
  four years" avoided by uprating → 1 (`parse_confidence: low`, attribution unclear in the text).

Not staged (with reason):
- Maintenance grants (revenue neutral, 5/5 in the PDF vs 4/5 on the web summary): no £ value.
- "If things don’t change" cumulative fuel duty statements duplicated in the cover text; likelihood ratings are
  carried in `conditions.likelihood_rating`, not as rows.
- Restated: "By the OBR's own estimates" statements are staged as `restated` (2 rows); cash ISA cut, HVCTS £2m,
  GBD 25% — descriptive, no value to stage.
- No SMF revenue estimate for the per-mile charge itself, the threshold freeze, HVCTS or salary sacrifice.

### Row counts

- by `source`: smf 40
- by `attribution`: own 35, restated 5
- by `benchmark_class`: administrative_fact 1, different_model 39
- by `source_model`: arithmetic 40
- by `value_kind`: central 2, cumulative 12, point 20, range_high 2, range_low 4
- by `parse_confidence`: high 35, low 1, medium 4
- by `measure_key`:
  - `null` 20
  - `ab2025_option__alcohol_minimum_unit_tax` 6
  - `ab2025_option__housing_first_for_rough_sleepers` 5
  - `ab2025__eved_mileage_supplement_electric_and_phev` 4
  - `ab2025__fuel_duty_freeze_extension_2026_27` 2
  - `ab2025_option__end_fuel_duty_freeze_and_start_road_pricing` 1
  - `ab2025_option__gambling_duties_consolidated_or_raised` 1
  - `ab2025_option__triple_lock_replaced_with_double_lock` 1

## Metrics, units and baselines used

- `revenue_change` (registered) for every yield/saving row ("positive = yield to the Exchequer"; foregone fuel duty
  "positive = cost to the Exchequer"; MUP alone negative). Producer definitions: "We estimate these changes would raise
  around £1.9bn in additional tax revenue for the Government"; "Ending the fuel duty freeze - a saving of £3.4 billion
  annually"; "our central estimate is that MUP would reduce tax receipts by a little over £300 million".
- `benefit_cost_change` (registered; `value_kind: cumulative`, "positive = saving to the Exchequer") for the triple
  lock options ("shifting to the double lock would save £2.6bn over the next five years"); `benefit_cost` for the
  Housing First first-year/ongoing costs and the WHP/ECO/BUS levels.
- `average_household_income_change` (registered; `gbp_per_household`; `income_group` quintile_5 / quintile_1) for
  "The top fifth of income earners will pocket £153 from this freeze, while those on the bottom will gain just £56."
- `proposed_metric: vehicle_sales_change` (`proposed_unit: vehicles`, cumulative over the five-year forecast) for the
  EV rows; `tax_base` (README list; `proposed_unit: dwellings` / `transactions`, or `gbp` for the £1bn flipping
  profits); `retailer_windfall` (`gbp`); `net_fiscal_benefit` (`gbp`); `saving_per_person` (`gbp`);
  `investment_change`, `compliance_cost`, `excess_cash_savings` (`gbp`, context).
- `period`: "annually" options with no year → 2026-27 (`period: 2027`, said in `note`); five-year cumulative rows →
  2030-31; fuel-duty cumulative → 2026-27 ("next year") and calendar 2028.
- `measure_key`: gambling → `ab2025_option__gambling_duties_consolidated_or_raised`; fuel duty/road pricing →
  `ab2025_option__end_fuel_duty_freeze_and_start_road_pricing`; MUT → `ab2025_option__alcohol_minimum_unit_tax`;
  double lock → `ab2025_option__triple_lock_replaced_with_double_lock`; Housing First →
  `ab2025_option__housing_first_for_rough_sleepers`; EV → `ab2025__eved_mileage_supplement_electric_and_phev`; freeze
  incidence → `ab2025__fuel_duty_freeze_extension_2026_27`; housing taxes, earnings/inflation links, SME/ISA context →
  `null` + `reform_hint`.
- Baselines: all `baseline_policy: null`.

### As staged

- registered `metric`: `average_household_income_change` 2, `benefit_cost` 5, `benefit_cost_change` 4, `revenue_change` 13
- `proposed_metric`: `compliance_cost` 1, `excess_cash_savings` 1, `investment_change` 1, `net_fiscal_benefit` 1, `retailer_windfall` 2, `saving_per_person` 2, `tax_base` 4, `vehicle_sales_change` 4
- registered `unit_concept`: `gbp` 31, `gbp_per_household` 2
- `proposed_unit`: `dwellings` 1, `transactions` 2, `vehicles` 4
- `baseline_policy`: None 40 (null = current law at the scoring date)
- `proposed_baseline`: none

## Distinct values per `conditions` axis

- `assumption` (1 distinct): only one third of grant-supported purchases are additional (2)
- `basis` (1 distinct): static (21)
- `component` (8 distinct): Electric Car Grant extension to 2029 (2); 36p single-rate MUT alongside 65p MUP, vs MUP alone (1); Non-Resident Purchases Tax (25% of sale value) (1); Rapid Sales Tax (half of flipping gains) (1); Vacant Property Tax (1% annual value tax) (1); additional 46p rate on spirits (increment over the single-rate MUT) (1); net of pay-per-mile charge and grant extension (1); pay-per-mile charge (1)
- `fiscal_event` (1 distinct): autumn_budget_2025 (40)
- `fy` (5 distinct): 2026-27 (25); 2030-31 (10); 2025-26 (2); 2027-28 (1); 2029-30 (1)
- `geography` (6 distinct): UK (26); England (8); England and Scotland (pilots) (2); England and Wales (2); Great Britain (1); Scotland (1)
- `horizon` (8 distinct): over the five-year forecast period (cumulative) (4); over the next five years (cumulative) (4); annual, after the first year (1); first year (1); over five years (cumulative) (1); since 2010 (cumulative, 'next year') (1); since 2010 (cumulative, by 2028) (1); the four years following 2026-27 (cumulative) (1)
- `income_group` (2 distinct): quintile_1 (1); quintile_5 (1)
- `likelihood_rating` (4 distinct): 1/5 (3); 3/5 (3); 2/5 (1); 4/5 (1)
- `measure_type` (2 distinct): cumulative revenue foregone from the fuel duty freeze (2); saving per benefiting person per year (2)
- `originator` (3 distinct): government (3); OBR (2); council tax records (1)
- `program` (3 distinct): Boiler Upgrade Scheme (1); Energy Company Obligation (ECO4) (1); Warm Homes Plan (committed funding) (1)
- `scenario` (3 distinct): 65p Minimum Unit Price (2); 65p Minimum Unit Price alone (1); SMEs investing at the same rate as larger companies (1)
- `sign_convention` (7 distinct): positive = yield to the Exchequer (11); positive = more EV sales (4); positive = saving to the Exchequer (3); positive = cost to the Exchequer (2); positive = gain to households (2); positive = increase in spending (1); positive = net fiscal benefit (1)
- `statistic` (1 distinct): mean (2)
- `subgroup` (4 distinct): annual profit on homes 'flipped' within 12 months (1); homes sold within 12 months ('flipped') each year (1); properties sold to non-residents each year (1); vacant properties (council tax records) (1)
- `unit_population` (2 distinct): electric vehicles (sales) (4); persons benefiting (2)

## Attribution decisions

- `own` / `different_model` for SMF estimates (35 rows), including the 88,000 and >350,000 EV adjustments.
- `restated`: OBR 440,000 and 130,000; government WHP £13.2bn, ECO ~£2bn/yr, BUS £295m. The "£14 billion" avoided
  cost is kept `own` with `parse_confidence: low` because the text does not name a source.
