# uk_centax: CenTax, Autumn Budget 2026

This family stages three CenTax publications:

- **"Autumn Budget 2026: Initial reaction"** (28 October 2026, centax.org.uk).
- **The two AB2026 briefings it links:** "Taxes at the top: Understanding what high earners pay and options for reform" (23 September 2026), which sets out "reforms available at the 2026 Budget", and "Capital Gains Tax on Entrepreneurs: Should the UK have a 'Unicorn Relief'?" (8 October 2026).

The source slug is `centax`, as in the AB2025 `uk_centax` family, and `source_model` is `hmrc_administrative_microdata` for CenTax's estimates and descriptive statistics.

`stage.py` holds the rows as data and rewrites `manifest.jsonl` and `claims_staged.jsonl.gz` byte for byte. `stage.py --verify` checks each primary's sha256 and finds every quote in its primary's text (HTML text, or `pdftotext -layout`, whitespace-normalised). Result: 0 problems.

- **Rows:** 110 (own 108, restated 2).
- **Primaries:** 5.

## Access recipe

Every primary was fetched directly on 2026-10-29 with `curl -sSL` and the browser User-Agent in the brief (HTTP 200). Nothing came from a local copy, and LinkedIn was not used.

- **The reaction page** was fetched at 16:17Z. It says "This page is being updated live" and carries no published or modified time, so a later fetch may hash differently.
- **The two briefing landing pages** were fetched at 16:30Z. Each prints no figures (0 rows) and links its PDF; they are manifested as the route to the PDFs.
- **The two PDFs** were fetched at 16:31Z and read with `pdftotext -layout`. Locators are printed page numbers; in "Taxes at the top" the Key findings are p. 1.

## Rows by primary

| primary | sha256 | rows |
|---|---|--:|
| Autumn Budget 2026: Initial reaction (HTML, 28 Oct) | `92c6008835547d41…` | 3 |
| Taxes at the top, landing page (HTML) | `c954e08f2aa6de7a…` | 0 |
| Taxes at the top (PDF, 35 pp., 23 Sep) | `af4cab614220c286…` | 104 |
| Unicorn Relief, landing page (HTML) | `91a6c8dc749273b1…` | 0 |
| Unicorn Relief (PDF, 74 pp., 8 Oct) | `9fd8ce97f3343f7a…` | 3 |

## Rows by measure key

| measure_key | rows |
|---|--:|
| `null`: 52 with a proposed key, 56 context (descriptive HMRC statistics, current-policy childcare behaviour, OBR CGT forecasts) | 108 |
| `ab2026__pension_tax_allowance` (CenTax's 53% marginal rate) | 1 |
| `ab2026__hmrc_tax_gap_package` (the timely-payment component, `row_type: measure_component`, README rule 9) | 1 |

## Proposed measure keys

The Budget took none of the options below. Founders' Relief (Table 6.1 line 26) and the BADR cut (line 60) are a different CGT design from CenTax's package. Each option is CenTax's own design, in CenTax's words:

| proposed key | scope | rows |
|---|---|--:|
| `ab2026_option__cgt_reform_package` | "Structural reform of CGT and equalising rates with Income Tax": equalise CGT rates with Income Tax rates; an investment allowance for the risk-free rate; remove uplift at death; rebasing on arrival with deemed disposal on departure. "We use administrative data from HMRC to cost the first four elements"; the fifth, more generous loss relief, isn't costed. No Table 6.1 line | 9 |
| `ab2026_option__nics_on_partnership_income` | "Applying an equivalent of Employer NICs to partnership profits": a top-up rate ("6.9% on partnership profits taxed at the additional rate, 7.6% … higher rate, and 9.6% … basic rate"), a £10,500 Partnership allowance and a £5,000 annual exempt amount per partner. No Table 6.1 line | 24 |
| `ab2026_option__nics_on_investment_income` | "Applying an equivalent of Class 1 NICs to investment income": rental income, savings income outside ISAs and other non-dividend investment income (`conditions.income_type`). No Table 6.1 line | 10 |
| `ab2026_option__childcare_100k_threshold_removed` | "Removing the £100,000 childcare cliff-edge": make the free childcare entitlement in England available to parents with incomes over £100,000. No Table 6.1 line | 3 |
| `ab2026_option__childcare_100k_threshold_removed_first_15_hours_under_3s` | "Remove the threshold for the first 15 hours of childcare for under-3s" | 1 |
| `ab2026_option__childcare_100k_threshold_raised` | "Increase the threshold at which entitlement to free childcare is withdrawn", to £125,000 or £150,000 (`conditions.threshold`) | 2 |
| `ab2026_option__childcare_100k_entitlement_taper` | "'Taper' the withdrawal of free childcare", at 8p, 18p or 28p per £1 over £100,000 (`conditions.taper_rate`) | 3 |

Every childcare option is "costed on an actual ANI basis" (`conditions.costing_basis`). CenTax's actual-ANI threshold itself ("could be set higher (£111,000) … at the same overall fiscal cost") is that option's design and has no row (README rule 8).

The £1.6bn timely-payment figure carries `ab2026__hmrc_tax_gap_package` under README rule 9, not a proposed key. More timely payment for Self Assessment is HM Treasury Table 6.3 line 3, a sub-measure of Table 6.1 line 45. The row has `conditions.row_type: measure_component`, with `conditions.component` naming the part.

## Conventions

- **Tax years:** CenTax gives tax years as the later year ("2022 is tax year 2021-22", Taxes at the top footnote 2). So "2030" is staged as `fy` 2029-30, "2028" as 2027-28, and the descriptive 2022 data as 2021-22. Every such row carries a `year_note`. This matches #207's reading of the same CenTax childcare figures.
- **Sign:**
  - Revenue-raising options are `positive = yield to the Exchequer`.
  - The childcare options are `positive = cost to the Exchequer`, so "raise £20 million" (28p taper) is staged as −2e7 (AB2025 uk_centax precedent for its allowance cost).
- **"Central":** CenTax's central scenario (`conditions.scenario: central`). It uses "elasticities drawn from the best available international evidence" for CGT, its "central revenue estimate, after accounting for behavioural responses" for partnership NICs, and its central bunching scenario for childcare. The investment-income NICs figures are static upper bounds ("naturally at the upper bound", footnote 13), so they are `range_high` with `basis: static`.
- **Units:**
  - Shares are fractions (`share`).
  - Effective and marginal rates are `percent`; rate gaps and top-up rates are `percentage_points`.
  - The CGT package's "increase revenue by 62%" is `revenue_change` in `percent` of baseline CGT revenue.
  - Income groups follow the AB2025 names (`top_10pct`, `top_1pct`, `top_0.1pct`, `top_0.01pct`, `decile_10`, `bottom_50pct`); percentile bands are `p50_p60` … `p99.5_p99.9`.
- **Attribution:**
  - CenTax's model estimates are `own` / `different_model`.
  - Descriptive HMRC statistics are `own` / `administrative_fact`, as in AB2025.
  - The OBR's £32bn and £16bn CGT forecasts are `restated`.
  - CenTax's 53% marginal rate and its £1.6bn three-year average of HM Treasury's timely-payment costing are `own` with `source_model: arithmetic`. The £1.6bn row carries `conditions.derived_from` naming Table 6.3 line 3, the same rule as uk_tpa.
- **Context rows:** the descriptive 2022 tax statistics and the current-policy childcare behaviour (bunching counts, response shares, partners leaving work) have no measure key and no proposal. The option keys carry only the options' costings and the distribution of their revenue or affected taxpayers.

## Proposed metrics (registered Metrics used where they fit)

Registered: `revenue_change`, `revenue_share` (also for "paid 60% of Income Tax and NICs"), `income_share`, `income_statistic`, `average_tax_rate`, `affected_count`, `affected_share`, `participation_rate`, `tax_collections`.

Proposed, with CenTax's own words:

- **`marginal_tax_rate` (percent):** "a new marginal rate of 53%".
- **`effective_tax_rate` (percent, AB2025 README list):** "this lower threshold is likely to have risen to 23%".
- **`effective_tax_rate_gap` (percentage points):** "the gap between headline rates and the average EATRs".
- **`taxpayer_share` (share):** "one in ten pays close to the headline rate of 47%" and the other dispersion statements on p. 11.
- **`behavioural_response_share` (share):** "fewer than one in ten employees with eligible children responded to the cliff-edge".
- **`workforce_exit_share` and `female_share` (share):** "3% of lower paid partners … leaving the workforce, with 90% of those partners being women".
- **`partner_not_in_work_share` (share):** "the share of parents whose partner is not in work is about 6%".

## Not staged, and why

- **Duplicates within one primary,** staged once:
  - in "Taxes at the top": 62%, 88%, £19.7bn, £2.1bn, 98%, 1,100, 90% and £640m (Key findings, repeated on pp. 17-27); 37%, 34% and 30% (p. 9); 17%→12%, 33%→36% and 37%→33% (p. 13); 40.5%, 60%, 43.9%, 61.5%, 47%, 20% and 23% (Conclusion);
  - in the Unicorn Relief PDF: "almost £20 billion" restates the £19.7bn in the same footnote.
- **Design, not estimates** (README rule 8):
  - the reaction page's "marginal tax rate of 33.3%" (the Pension Tax Allowance's £1-for-£3 withdrawal rate, restated as a percentage; kept in the 53% row's conditions) and "a 100% marginal tax rate" (the Carer's Allowance taper of £1 for every £1, restated);
  - Taxes at the top's partnership top-up rates of 6.9%, 7.6% and 9.6% (the option's rates, quoted in its scope above) and its £111,000 actual-ANI threshold.
- **Policy parameters** (also design under rule 8):
  - in the reaction page: the £12,570 Personal Allowance; the 24%, 44% and 49% rates; the £12,000 cash ISA cap from AB2025; the Direct Recovery of Debts thresholds (£1,000, £5,000, £10,000) and dates;
  - in "Taxes at the top": Employer NICs at 15%, its "effective rate of Employer NICs is 13.04%", the £10,500 and £5,000 allowances, footnote 11's rates, and Appendix A's rates.
- **The reaction page's worked mechanics:** the payments-on-account example (a £10,000 liability, two £5,000 payments) explains the existing regime; it is not a figure about the Budget.
- **Charts without printed values:** Taxes at the top Figures 1-7, B1 and B2.
- **Unicorn Relief's illustrations and design parameters:**
  - the risk-aversion example (£100,000 v £1 million at 10%);
  - footnote 27's net-of-tax returns on a £100m gain (76% → 76.06% → 77.4%);
  - the £20m break-even example at a 15% rate;
  - the taper example (45% → 44% per £1m above £750m);
  - the £750m / US$1bn threshold;
  - EMI and SEIS limits.
  These illustrate design choices rather than estimate outcomes, the same test AB2025 uk_centax applied ("thresholds/equivalences, not scoreable values"). The report says it does not cost Unicorn Relief ("It is difficult to model how much Unicorn Relief would cost").
- **The September 2026 childcare report** ("Removing the £100,000 childcare cliff-edge: Impacts and cost of reform", linked from the reaction page) is not re-staged. Its Table 4.2 is already in `data/externals/centax-childcare-100k.json` (#207). The £520m and £640m staged here are CenTax repeating its own central net fiscal cost in AB2026 publications; the ingest should treat them as the same estimate as #207's.
- **LinkedIn:** CenTax's 28 October LinkedIn post (seed inventory) needs a login; not used.
