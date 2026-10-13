# Fabian Society — Autumn Budget 2025 harvest (source `fabian_society`)

Staged 2026-09-24 from the primary documents. **21 claims** in `claims_staged.jsonl.gz`, **2 documents** in `manifest.jsonl`. Row contract, enums and rules: `../README.md`; measure keys: `../REGISTRY_KEYS.md`. Every `value` is verbatim (normalised to the unit as recorded in `normalization`); nothing is derived.

## Access recipe

"Taxing Questions" PDF and its publication page fetched directly (`curl`, HTTP 200). Publication date 2025-10-25
(`article:published_time`); the PDF's ModDate is 2025-11-06 (re-uploaded; page modified the same day). pypdf text;
chapter passages read in full for verbatim quotes.

### Documents (manifest.jsonl)

- 2025-10-25 · Taxing Questions (publication page) · `html` · access `direct` · 76,300 bytes · sha256 `cac73bba5b4e4aec…` · **0 rows**  
  <https://fabians.org.uk/publication/taxing-questions/>
- 2025-10-25 · Taxing Questions: How the chancellor can raise revenue fairly at the Autumn Budget · `pdf` · access `direct` · 593,527 bytes · sha256 `658ca83c8d771b0f…` · **21 rows** — publication page article:published_time 2025-10-25; PDF ModDate 2025-11-06 (re-uploaded); page modified 2025-11-06  
  <https://fabians.org.uk/wp-content/uploads/2025/10/Taxing-Questions-FINAL-word-betterworld.pdf>

## Coverage tally (seed bullets → claims staged → not staged)

Seed: `scores-3-other-shops.md` § Fabian Society (8 bullets).

Staged (21 rows):
- Chapter 3 (Joe Dromey), computed with PolicyEngine (footnote 3 "Modelling conducted using Policy Engine"): £11.7bn
  from a two-year freeze extension; 49% of revenue from the highest-earning fifth; 4% from the poorest fifth; median
  household −£20 a month by 2030 → 4 rows, `source_model: policyengine_uk`, `attribution: same_assumptions`,
  `benchmark_class: same_assumptions`.
- Chapter 2 gambling: "nearly £2bn annually" and the £140m levy → 2 rows (`own`, `arithmetic`, medium confidence: no
  originator named; the design mirrors the SMF's £1.9bn package).
- Chapter 5 IPT on PMI: +£550m (own arithmetic); £888m base and "up to £1bn" (restated) → 3.
- Chapter 7 bank windfalls: £3.5bn reversing the surcharge cut, £16bn at 38% on big-four 2024 profits (own
  arithmetic); >£11bn (Positive Money), £7–8bn (IPPR, 2 rows), £22bn/yr and £85.9bn transfers (Treasury/BoE) → 6.
- Chapter 8 rental income: £1–2bn (2 rows, own); £170/yr for a one-property landlord (own worked example) → 3.
- Chapter 6 pensions: NICs relief on salary sacrifice "worth over £4bn per year" (HMRC, restated) → 1.
- Chapter 1 oil and gas: windfall tax yielded £5.6bn (restated) → 1.

Not staged (with reason):
- Restated OBR/IFS figures in ch. 3 (£45bn/yr from the existing freeze by 2027/28; £22bn needed); "nearly £12bn" (same
  as £11.7bn); "state pension will exceed the personal allowance by 2027" (no value).
- Ch. 6: pension tax relief ~£80bn vs £25bn income tax on private pensions; 53% of relief to the top fifth (Fabian
  2024); £1.50 relief per £1 — cited context, not Budget-option scores; lump-sum/annual-allowance/NICs-equivalent
  options carry no £ figure in the chapter.
- Ch. 7: £895bn QE (context); Fairer Share 0.48% property tax ≈ £50bn, CenTax CGT £11.5bn, NI on investment income
  ~£3.1bn (wealth chapter, cited) — not fetched as own numbers.
- Ch. 1: ">£30bn post-tax profits" (context).

### Row counts

- by `source`: fabian_society 21
- by `attribution`: own 8, restated 9, same_assumptions 4
- by `benchmark_class`: administrative_fact 3, different_model 14, same_assumptions 4
- by `source_model`: arithmetic 17, policyengine_uk 4
- by `value_kind`: cumulative 2, point 11, range_high 4, range_low 4
- by `parse_confidence`: high 12, low 1, medium 8
- by `measure_key`:
  - `ab2025_option__personal_tax_threshold_freeze_two_more_years_to_2030` 4
  - `ab2025_option__corporation_tax_plus_1p_and_bank_surcharge` 3
  - `ab2025_option__insurance_premium_tax_on_private_medical_insurance_20pct` 3
  - `ab2025_option__boe_apf_indemnity_or_reserves_remuneration_reform` 2
  - `ab2025_option__gambling_duties_consolidated_or_raised` 2
  - `ab2025_option__nics_on_rental_income` 2
  - `null` 2
  - `ab2025__property_income_separate_rates` 1
  - `ab2025__salary_sacrifice_pension_nics_cap_2000` 1
  - `ab2025_option__oil_and_gas_windfall_measures` 1

## Metrics, units and baselines used

- `revenue_change` (registered) for all yield rows. Producer definition (ch. 3, p.11): "Our modelling at the Fabian
  Society suggests that freezing income tax thresholds for a further two years until 2029/30 would raise a further
  £11.7bn in revenue"; footnote 3: "The basic and higher rate thresholds were frozen in cash terms for an additional
  two years (2028/29 and 2029/30)".
- `proposed_metric: revenue_share` (`share`; `income_group` quintile_5 / quintile_1, `unit_population: households`)
  for "half (49 per cent) of the revenue raised would come from the highest earning fifth of households" / "the
  poorest fifth of households would bear just 4 per cent".
- `average_household_income_change` (registered) with `unit_concept: gbp_per_month` and `conditions.statistic: median`
  for "the median household would be worse off by around £20 a month by 2030".
- `proposed_metric: household_tax_change` (README list; `gbp`) for the £170 landlord example; `proposed_metric:
  levy_yield` (`gbp`) for the £140m Horserace Betting Levy (revenue to racing, not the Exchequer);
  `proposed_metric: tax_base` for the £888m IPT-on-PMI receipts; `proposed_metric: central_bank_loss_transfer` for the
  £22bn/yr and £85.9bn; `tax_expenditure` (registered) for the £4bn NICs relief.
- `period`: £11.7bn and quintile shares 2029-30 (the second frozen year; the sentence names no year — said in
  `note`); £20/month "by 2030" → 2029-30; "annually"/"a year" options with no year → 2026-27.
- `measure_key`: `ab2025_option__personal_tax_threshold_freeze_two_more_years_to_2030`;
  `ab2025_option__gambling_duties_consolidated_or_raised`;
  `ab2025_option__insurance_premium_tax_on_private_medical_insurance_20pct`;
  `ab2025_option__corporation_tax_plus_1p_and_bank_surcharge`;
  `ab2025_option__boe_apf_indemnity_or_reserves_remuneration_reform`; `ab2025_option__nics_on_rental_income` (nearest
  key for aligning rental-income rates with work); `ab2025__property_income_separate_rates` (the £170 2pp example);
  `ab2025__salary_sacrifice_pension_nics_cap_2000`; `ab2025_option__oil_and_gas_windfall_measures`.
- Baselines: all `baseline_policy: null`.

### As staged

- registered `metric`: `average_household_income_change` 1, `revenue_change` 12, `tax_expenditure` 1
- `proposed_metric`: `central_bank_loss_transfer` 2, `household_tax_change` 1, `levy_yield` 1, `revenue_share` 2, `tax_base` 1
- registered `unit_concept`: `gbp` 18, `gbp_per_month` 1, `share` 2
- `proposed_unit`: none
- `baseline_policy`: None 21 (null = current law at the scoring date)
- `proposed_baseline`: none

## Distinct values per `conditions` axis

- `assumption` (1 distinct): taxable profits half of gross rent (1)
- `basis` (1 distinct): static (16)
- `fiscal_event` (1 distinct): autumn_budget_2025 (21)
- `fy` (3 distinct): 2026-27 (12); 2029-30 (4); 2024-25 (3)
- `geography` (1 distinct): UK (21)
- `horizon` (4 distinct): a year over this parliament (2); 2022 and 2023 (cumulative) (1); a year over the next five years (1); end of 2022 to March 2025 (cumulative) (1)
- `household` (1 distinct): landlord of one property (1)
- `income_group` (2 distinct): quintile_1 (1); quintile_5 (1)
- `model` (1 distinct): PolicyEngine ('Modelling conducted using Policy Engine', footnote 3) (1)
- `originator` (8 distinct): IPPR (2); 'some estimates' (unnamed) (1); HM Treasury / BoE APF accounts (1); HMRC (1); HMRC receipts (1); OBR/HM Treasury (APF indemnity) (1); Positive Money (1); not stated (IPT receipts statistic) (1)
- `program` (1 distinct): NICs relief on salary sacrifice pension contributions (1)
- `rent` (1 distinct): around £1,400 per month (ONS) (1)
- `sign_convention` (5 distinct): positive = yield to the Exchequer (12); positive = cost to the Exchequer (2); positive = gain to households (1); positive = increase in tax paid (1); positive = yield to British racing (Horserace Betting Levy) (1)
- `statistic` (1 distinct): median (1)
- `subgroup` (2 distinct): big four banks (1); big four banks, 2024 profits (1)
- `tax` (2 distinct): Energy Profits Levy (windfall tax) (1); IPT receipts on private medical insurance at 12 per cent (1)
- `unit_population` (1 distinct): households (3)

## Attribution decisions

- `same_assumptions` / `same_assumptions` (PolicyEngine-computed, per footnote 3) for the four chapter-3 rows —
  these are not independent benchmarks.
- `own` / `different_model` (`arithmetic`) where the chapter author computes the figure without naming an originator
  (gambling package, £140m levy, IPT +£550m, bank surcharge £3.5bn and £16bn, rental £1–2bn and £170).
- `restated` naming the originator in `conditions.originator`: £888m and "up to £1bn" (IPT statistics/"some
  estimates"), >£11bn (Positive Money), £7–8bn (IPPR), £22bn/yr and £85.9bn (HM Treasury/BoE), >£4bn (HMRC), £5.6bn
  (HMRC receipts).
