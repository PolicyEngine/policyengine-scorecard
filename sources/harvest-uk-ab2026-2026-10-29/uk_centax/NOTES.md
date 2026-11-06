# uk_centax: CenTax, Autumn Budget 2026

In this family we stage three CenTax publications:

- **"Autumn Budget 2026: Initial reaction"** (28 October 2026, centax.org.uk).
- **The two AB2026 briefings it links.** In "Taxes at the top: Understanding what high earners pay and options for reform" (23 September 2026), CenTax sets out "reforms available at the 2026 Budget". The second is "Capital Gains Tax on Entrepreneurs: Should the UK have a 'Unicorn Relief'?" (8 October 2026).

We use the source slug `centax`, as in the AB2025 `uk_centax` family, and `source_model` `hmrc_administrative_microdata` for CenTax's estimates and descriptive statistics.

We keep `stage.py` on branch `uk/ab2026-harvest-staging` at `harvest-staging/ab2026/lanes/thinktanks-a/uk_centax/stage.py`. We commit only NOTES.md, `manifest.jsonl` and `claims_staged.jsonl.gz` to this branch, and no primary bytes to the repository. The lane never committed its local primaries folder (`.ab2026-primaries/uk_centax/`), so fetch each primary from its `manifest.jsonl` URL and check its sha256.

We wrote the rows into `stage.py` as data, and it rewrites `manifest.jsonl` and `claims_staged.jsonl.gz` byte for byte. `stage.py --verify` checks each primary's sha256 and finds every quote in its primary's text (HTML text, or `pdftotext -layout`, whitespace-normalised); it reports 0 problems.

- Rows: 112 (own 108, restated 4).
- Primaries: 6 (the reaction page in two versions, rule 7).

## Access recipe

The lane fetched every primary directly on 2026-10-29 with `curl -sSL` and the browser User-Agent in the brief (HTTP 200). It took nothing from a local copy and didn't use LinkedIn.

- The lane fetched the reaction page at 16:17Z. CenTax says "This page is being updated live" and prints no published or modified time, so a later fetch may hash differently.
- Review B retrieved the reaction page's 4 November version on 2026-11-04 (sha256 `5103e06ae3a5831a…`, 271,039 bytes), and the coordinator's own fetch that day matched it. In it CenTax says "This page has finished updating". CenTax added seven sections that the 29 October copy lacks: Big picture; Tax reliefs for founders and employees (with its CGT, BADR, Founders' Relief, EMI2/CSOP and evaluation parts); Company distributions framework. CenTax's markup for those sections accounts for the growth from 248,542 bytes. We treat it as a second primary (README rule 7). On the 3 earlier rows we keep citing the 29 October copy, whose quotes CenTax still prints, and on the 2 rows from the new sections we cite the new version. This session re-opened neither version; the coordinator chose the two new rows' quotes and checked them against its local copy.
- The lane fetched the two briefing landing pages at 16:30Z. CenTax prints no figures on either (0 rows) and links each PDF from it, so we manifest them as the route to the PDFs.
- It fetched the two PDFs at 16:31Z and read them with `pdftotext -layout`. We use printed page numbers as locators; in "Taxes at the top" CenTax puts the Key findings on p. 1.

## Rows by primary

| primary | sha256 | rows |
|---|---|--:|
| Autumn Budget 2026: Initial reaction (HTML, 28 Oct; fetched 29 Oct) | `92c6008835547d41…` | 3 |
| Autumn Budget 2026: Initial reaction (HTML, 4 Nov version, finished updating) | `5103e06ae3a5831a…` | 2 |
| Taxes at the top, landing page (HTML) | `c954e08f2aa6de7a…` | 0 |
| Taxes at the top (PDF, 35 pp., 23 Sep) | `af4cab614220c286…` | 104 |
| Unicorn Relief, landing page (HTML) | `91a6c8dc749273b1…` | 0 |
| Unicorn Relief (PDF, 74 pp., 8 Oct) | `9fd8ce97f3343f7a…` | 3 |

## Rows by measure key

| measure_key | rows |
|---|--:|
| the seven option keys below | 53 |
| `null`: context (descriptive HMRC statistics, current-policy childcare behaviour, OBR CGT forecasts) | 56 |
| `ab2026__pension_tax_allowance` (CenTax's 53% marginal rate) | 1 |
| `ab2026__hmrc_tax_gap_package` (the timely-payment component, restated from the OBR, `row_type: measure_component`, README rule 9) | 1 |
| `ab2026__distributions_framework_modernised` (the £800m, restated from Table 6.1 line 49) | 1 |

## Option keys

On 29 October we gave the 53 option rows `measure_key: null` and proposed the seven keys below, and in tranche 2 we registered them. The government took none of these options in the Budget. It chose Founders' Relief (Table 6.1 line 26) and the BADR cut (line 60), a different CGT design from CenTax's package. CenTax designed each option, and we give each in CenTax's words:

| key | scope | rows |
|---|---|--:|
| `ab2026_option__cgt_reform_package` | "Structural reform of CGT and equalising rates with Income Tax": equalise CGT rates with Income Tax rates; an investment allowance for the risk-free rate; remove uplift at death; rebasing on arrival with deemed disposal on departure. "We use administrative data from HMRC to cost the first four elements"; CenTax doesn't cost the fifth, more generous loss relief. No Table 6.1 line | 10 |
| `ab2026_option__nics_on_partnership_income` | "Applying an equivalent of Employer NICs to partnership profits": a top-up rate ("6.9% on partnership profits taxed at the additional rate, 7.6% … higher rate, and 9.6% … basic rate"), a £10,500 Partnership allowance and a £5,000 annual exempt amount per partner. No Table 6.1 line | 24 |
| `ab2026_option__nics_on_investment_income` | "Applying an equivalent of Class 1 NICs to investment income": rental income, savings income outside ISAs and other non-dividend investment income (`conditions.income_type`). No Table 6.1 line | 10 |
| `ab2026_option__childcare_100k_threshold_removed` | "Removing the £100,000 childcare cliff-edge": make the free childcare entitlement in England available to parents with incomes over £100,000. No Table 6.1 line | 3 |
| `ab2026_option__childcare_100k_threshold_removed_first_15_hours_under_3s` | "Remove the threshold for the first 15 hours of childcare for under-3s" | 1 |
| `ab2026_option__childcare_100k_threshold_raised` | "Increase the threshold at which entitlement to free childcare is withdrawn", to £125,000 or £150,000 (`conditions.threshold`) | 2 |
| `ab2026_option__childcare_100k_entitlement_taper` | "'Taper' the withdrawal of free childcare", at 8p, 18p or 28p per £1 over £100,000 (`conditions.taper_rate`) | 3 |

CenTax says the options short of full removal (rows 101–106) are "costed on an actual ANI basis", and we record that in `conditions.costing_basis`; we give the full removal's £640m and £520m (rows 1, 25 and 99) no costing basis. CenTax's actual-ANI threshold itself ("could be set higher (£111,000) … at the same overall fiscal cost") forms that option's design, so we staged no row for it (README rule 8).

Under README rule 9 we key the £1.6bn timely-payment figure to `ab2026__hmrc_tax_gap_package`, not a new key. CenTax repeats the OBR's printed average (EFO paras 3.4 and 3.13), so we mark the row `restated` (review B, finding 1). HM Treasury lists more timely payment for Self Assessment as Table 6.3 line 3, a sub-measure of Table 6.1 line 45. We set `conditions.row_type: measure_component` on the row and name the part in `conditions.component`.

## Conventions

- **Tax years.** CenTax names each tax year by its later year ("2022 is tax year 2021-22", Taxes at the top footnote 2). So we stage "2030" as `fy` 2029-30, "2028" as 2027-28 and the descriptive 2022 data as 2021-22, and give every such row a `year_note`. We read the same CenTax childcare figures this way in #207.
- **Sign.**
  - We stage revenue-raising options as `positive = yield to the Exchequer`.
  - We stage the childcare options as `positive = cost to the Exchequer`. We stage the one exception, the 28p taper's "raise £20 million", as +2e7 with `positive = yield to the Exchequer`, because we don't re-sign values (AB2025 README; changed on 3 November, review finding 4).
- **"Central".** We record CenTax's central scenario as `conditions.scenario: central`. For CGT CenTax uses "elasticities drawn from the best available international evidence", for partnership NICs its "central revenue estimate, after accounting for behavioural responses", and for childcare its central bunching scenario. CenTax gives the investment-income NICs figures as static upper bounds ("naturally at the upper bound", footnote 13), so we stage them as `range_high` with `basis: static`.
- **Units.**
  - We give shares as fractions (`share`).
  - We give effective and marginal rates in `percent` and rate gaps in `percentage_points`. We stage no top-up rate, because the partnership top-up rates form the option's design (below).
  - We stage the CGT package's "increase revenue by 62%" as `revenue_change` in `percent` of baseline CGT revenue.
  - We name income groups as in AB2025 (`top_10pct`, `top_1pct`, `top_0.1pct`, `top_0.01pct`, `decile_10`, `bottom_50pct`), and percentile bands `p50_p60` … `p99.5_p99.9`. We name single percentiles `median`, `p99` and `p99.99`, and p. 11's "by around 2.8 percentage points on average" `top groups, on average`.
- **Attribution.**
  - We mark CenTax's model estimates `own` / `different_model`.
  - We mark descriptive HMRC statistics `own` / `administrative_fact`, as in AB2025.
  - We mark the OBR's £32bn and £16bn CGT forecasts `restated`.
  - CenTax repeats the OBR's printed figure for the £1.6bn timely-payment average, so we mark it `restated`, with `source_model: obr_efo_forecast`, and name EFO paras 3.4 and 3.13 in `conditions.originator` (review B, finding 1).
  - CenTax restates Table 6.1 line 49 for the £800m for the distributions framework (4 November version), so we mark it `restated`, `hmt_costing_obr_certified`.
  - We mark CenTax's 53% marginal rate `own`, with `source_model: arithmetic`.
  - CenTax makes the "over half of CGT payers" claim (4 November version) on its own account, about its own CGT package. We mark it `own`, `share_with_tax_cut`, value 0.5, `range_low`, medium confidence; CenTax prints no year, so we stage it with the package's 2030 costing.
- **Context rows.** We gave no measure key and no proposal to the descriptive 2022 tax statistics or the current-policy childcare behaviour (bunching counts, response shares, partners leaving work). We key to the options only their costings and the distribution of their revenue or affected taxpayers.

## Proposed metrics (registered metrics where they fit)

We use these registered metrics: `revenue_change`, `revenue_share` (also for "paid 60% of Income Tax and NICs"), `income_share`, `income_statistic`, `average_tax_rate`, `affected_share`, `share_with_tax_cut`, `participation_rate`, `tax_collections`.

We propose these, with CenTax's own words:

- **`marginal_tax_rate` (percent):** "a new marginal rate of 53%".
- **`effective_tax_rate_gap` (percentage points):** "the gap between headline rates and the average EATRs".
- **`taxpayer_share` (share):** "one in ten pays close to the headline rate of 47%" and the other dispersion statements on p. 11.
- **`behavioural_response_share` (share):** "fewer than one in ten employees with eligible children responded to the cliff-edge".
- **`workforce_exit_share` and `female_share` (share):** "3% of lower paid partners … leaving the workforce, with 90% of those partners being women".
- **`partner_not_in_work_share` (share):** "the share of parents whose partner is not in work is about 6%".
- **`parents_bunching` (count):** "from 1,100 in 2022 to 11,980 by 2030" (rows 26–27; we gave these counts this name in #207's `data/externals/centax-childcare-100k.json`. The repository's childcare ingester drops them as "a behavioural-model count of parents" with no registered metric; review B, finding 3).

## Not staged, and why

- **"Around four times as many parents would be bunching"** (p. 25): CenTax gives this for its halved-unresponsiveness sensitivity, as a scenario ratio, not an estimate of an option's effect. We added this entry on 3 November, after review finding 6.

- We staged each duplicate within one primary once:
  - in "Taxes at the top":
    - Key findings, repeated on pp. 17-27: 62%, 88%, £19.7bn, £2.1bn, 98%, 1,100, 90% and £640m;
    - p. 9: 37%, 34% and 30%;
    - p. 13: 17%→12%, 33%→36% and 37%→33%;
    - Conclusion: 40.5%, 60%, 43.9%, 61.5%, 47%, 20% and 23%;
  - in the Unicorn Relief PDF: CenTax's "almost £20 billion" restates the £19.7bn in the same footnote.
- At ingest we merge six rows into another printing of the same figure, and list them in the ingest's `REPEATED_PRINTINGS`. In section 3.2 of Taxes at the top, CenTax rounds two of Table 1's shares (rows 62 and 64, into rows 82 and 67) and bounds a third (row 65, into row 66). It also prints three figures in two documents each. It gives the £640m in Taxes at the top's key findings and on its reaction page (row 25, into row 1). In footnote 9 of the Unicorn Relief PDF it repeats the £19.7bn of Taxes at the top's key findings and the £14bn of its section 3.1 (rows 107 and 108, into rows 21 and 58).
- Under README rule 8 we left out these figures, which set an option's or a measure's design and estimate nothing:
  - the reaction page's "marginal tax rate of 33.3%", the Pension Tax Allowance's £1-for-£3 withdrawal rate restated as a percentage, which we keep in the 53% row's conditions;
  - its "a 100% marginal tax rate" (the Carer's Allowance taper of £1 for every £1, restated);
  - Taxes at the top's partnership top-up rates of 6.9%, 7.6% and 9.6% (the option's rates, quoted in its scope above) and its £111,000 actual-ANI threshold.
- We left out policy parameters, which we also treat as design under rule 8:
  - in the reaction page: the £12,570 Personal Allowance; the 24%, 44% and 49% rates; the £12,000 cash ISA cap from AB2025; the Direct Recovery of Debts thresholds (£1,000, £5,000, £10,000) and dates;
  - in "Taxes at the top": Employer NICs at 15%, CenTax's "effective rate of Employer NICs is 13.04%", the £10,500 and £5,000 allowances, footnote 11's rates, and Appendix A's rates.
- We left out the reaction page's worked mechanics. CenTax uses the payments-on-account example (a £10,000 liability, two £5,000 payments) to explain the existing regime, not to give a figure about the Budget.
- We left out charts on which CenTax prints no values: Taxes at the top Figures 1-7, B1 and B2.
- We left out Unicorn Relief's illustrations and design parameters:
  - the risk-aversion example (£100,000 v £1 million at 10%);
  - footnote 27's net-of-tax returns on a £100m gain (76% → 76.06% → 77.4%);
  - the £20m break-even example at a 15% rate;
  - the taper example (45% → 44% per £1m above £750m);
  - the £750m / US$1bn threshold;
  - EMI and SEIS limits.
  CenTax uses these to illustrate design choices, not to estimate outcomes, the same test we applied in AB2025 uk_centax ("thresholds/equivalences, not scoreable values"). CenTax says it doesn't cost Unicorn Relief ("It is difficult to model how much Unicorn Relief would cost").
- We didn't re-stage the September 2026 childcare report ("Removing the £100,000 childcare cliff-edge: Impacts and cost of reform", linked from the reaction page). We already store its Table 4.2 in `data/externals/centax-childcare-100k.json` (#207). That file differs from this family in three ways (thinktanks-a review, finding 3):
  - **sign:** in #207 we store the full removal's central net fiscal cost as −640m, negative for a cost; in this family we store +640m with `positive = cost to the Exchequer`;
  - **coverage:** #207 covers only Table 4.2's full removal; we take the cheaper options (rows 101–106) only from "Taxes at the top";
  - **bunching counts:** in row 27 we stage "11,980 by 2030", where CenTax gives 16,280 as #207's 2030 central "Number Bunching, Before Removal". CenTax may mean a different concept, or may differ between its two publications, and we say so in row 27's note. In the £520m and £640m we stage here, CenTax repeats its own central net fiscal cost in AB2026 publications; at ingest we score them as CenTax's claims on `ab2026_option__childcare_100k_threshold_removed` (rows 1, 25 and 99). We don't link them to #207's estimate, so that link stays open.
- **LinkedIn:** CenTax's 28 October LinkedIn post (seed inventory) needs a login, and we didn't use it.
- We left out the 4 November version's design figures (README rule 8): the BADR lifetime limit's cut from £1 million to £500,000, Founders' Relief's 10% rate on up to £10 million of gains, and the EMI, EMI2 and CSOP limits. CenTax gives them as the measures' parameters, not estimates. In its "Big picture" section CenTax repeats the Budget's headline figures and gives no estimate of its own.
- We left out two passages from "Taxes at the top", pp. 2–3. CenTax uses "around two-thirds of total tax revenue" to describe the tax base, not to estimate anything about the Budget or an option. It restates the "over 100%" marginal rates at the childcare cliff edge as the current regime's design.

## Review fixes, 3 November 2026

In its review (`harvest-staging/ab2026/reviews/verify-thinktanks-a.md` on the staging branch), the thinktanks-a reviewer approved this family with fixes. We put each in an explicit block at the end of `stage.py`'s rows. We re-opened no primary, because the session's network policy refused centax.org.uk, and changed no printed value.

- Finding 1: CenTax prints £3bn, £0.6bn and £0.4bn (p. 22; rows 84–86) as the parts of its "up to £4 billion" (row 24; 3 + 0.6 + 0.4 = 4.0). We set `conditions.row_type: measure_component` on them and name the income type in `conditions.component`, so an ingest never adds them to the total.
- Finding 2: the reviewer confirmed it. Row 2's derivation cites Table 6.3 row 3 at 1,355, 1,605 and 1,815 (£m, 2029-30 to 2031-32), and we stage exactly those cells in `uk_hmt_redbook`.
- Finding 3: we record the #207 file's three differences under "Not staged" and in row 27's note.
- Finding 4 (optional, applied): we stage row 105 as +2e7 with `positive = yield to the Exchequer` and normalisation "£ million × 1e6".
- Finding 5 (optional, applied): for row 18 (23%, a 25th-percentile EATR) we use the registered `average_tax_rate`, as on rows 7–15. On rows 19–20 we put `revenue_change` in `percent`. At ingest we drop row 19 (62%) as a ratio and row 20 (88%) as CenTax's earlier estimate restated, so neither becomes a claim.
- Finding 6: CenTax gives p. 25's "around four times as many parents would be bunching" in the halved-unresponsiveness scenario as a scenario ratio, and we list it under "Not staged".
- Finding 7: we stage CenTax's 2024-era estimates at fy 2025-26 under the CGT option key in rows 20, 58, 108 and 109, and say so in their `scenario` condition. At ingest we drop row 20 and score rows 58, 108 and 109 on `ab2026_option__cgt_reform_package`, with the `scenario` condition on each claim.
- The contract checker reports 110 rows, 0 problems, and when we re-run `stage.py` it reproduces both files byte for byte. COUNTS.json pins the gzip's sha256.

## Review fixes, 4 November 2026

Review B (PR #231, issue comment 6635498758) approved this family with fixes, and the coordinator settled finding 2 in the brief. We put the fixes in an explicit block after the 3 November fixes in `stage.py`. This session re-opened no primary.

- Finding 1: we mark row 2 (£1.6bn) `restated`, `source_model: obr_efo_forecast`, with `conditions.originator` "OBR, Economic and fiscal outlook October 2026, paras 3.4 and 3.13" in place of `derived_from`.
- Finding 2, the coordinator's call: we treat the reaction page's 4 November version as a second primary (`5103e06a…`) and stage two rows from it (rows 110–111). We stage the £800m in 2029-30 for the distributions framework as `restated` on `ab2026__distributions_framework_modernised`. We stage CenTax's claim that "over half of CGT payers" would pay less tax under its package as `own` on `ab2026_option__cgt_reform_package`, 0.5 `range_low`. We list the new sections' design figures under "Not staged".
- Finding 3: on rows 26–27 (the bunching counts) we dropped `affected_count` for `proposed_metric: parents_bunching`.
- Finding 4: we mark rows 87–92 as `measure_component`s of the investment-income option, with `component` = the row's `income_type`.
- Finding 5: on Table 1's share-of-affected-population rows (67, 69, …, 83) we set `conditions.denominator: "taxpayers affected by the reform"`.
- Finding 6: we name only rows 101–106 in the costing-basis sentence and say we stage no top-up rate. We added `median`, `p99`, `p99.99` and `top groups, on average` to the income-group list, gave row 0 a `year_note`, and list pp. 2–3's two-thirds and "over 100%" rates under "Not staged".
