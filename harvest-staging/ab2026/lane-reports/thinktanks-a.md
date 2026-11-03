# AB2026 harvest, think tanks A: report

All five family directories are staged under `sources/harvest-uk-ab2026-2026-10-29/`. The contract checker reports 0 problems for each, and every `stage.py` reproduces its claims file byte for byte. Three families have rows; CPAG and SMF have none, because Cloudflare blocked both sites. I committed nothing and touched nothing outside the family directories and `.ab2026-primaries/`.

| family | rows | primaries | claims sha256 |
|---|--:|--:|---|
| `uk_tpa` | 306 (own 245, restated 61) | 10 | `3740d45a5f2d190a2688a983b0804b2c4d1a0ea341508338d8dbf71243108731` |
| `uk_centax` | 110 (own 108, restated 2) | 5 | `f004e6b06f33bb48ea83982bb9eb75fbbb2b800e5074bf5b6851a81938610af8` |
| `uk_ippr` | 3 (restated 2, own 1) | 3 | `89f8fed930de0fc9c48779fd28233dc9ae04c7dbc699acc0b08a903f3cd86613` |
| `uk_cpag` | 0 | 0 (unreached) | `9ceffb73…` (empty gzip) |
| `uk_smf` | 0 | 0 (unreached) | `9ceffb73…` (empty gzip) |

**The README and checker changed mid-run.** Someone edited them in this worktree while I worked, adding rule 8 (stage estimates, not design) and rule 9 (a part of one measure keeps its key). I brought the families into line and removed 9 rows that are now design:

- TPA: the Pension Tax Allowance's £94 maximum and £282 withdrawal band, now held in conditions.
- CenTax: its 33.3% and 100% rates (both taper rates restated), the partnership top-up rates of 6.9%, 7.6% and 9.6%, and the £111,000 threshold.
- IPPR: IPPR North's £285m, a spending allocation.

The £1.6bn timely-payment figure now carries line 45's key as a `measure_component`.

**The repository tests give 8 passed and 2 failed.** Both failures are the COUNTS.json pins, which you add when you merge the families.

## Primaries (all fetched directly on 2026-10-29; no local copies needed or used)

- **`uk_tpa`:**
  - The article "Budget 2026 – what it means" (`9d803165…fc350d`).
  - Seven ECharts chart data files the article embeds: tax rises by event (`62d64a90…`), tax take by government (`b1308789…`), tax as % of GDP (`a96c8f8f…`), by tax 2027/28 (`dcf10b6e…`), by year (`db22d5e0…`), by measure in real terms (`7355f24b…`) and investment bank tax (`7a8454d6…`).
  - The calculator screenshot linked from footnote 1 (`e69c25ad…`).
  - The calculator page, a 0-row descriptor (`69a72c68…`).
- **`uk_centax`:**
  - The 28 October reaction (`92c60088…`).
  - "Taxes at the top", 23 September: landing page (`c954e08f…`, 0 rows) and PDF (`af4cab61…`).
  - "Unicorn Relief", 8 October: landing page (`91a6c8dc…`, 0 rows) and PDF (`9fd8ce97…`).
  - The two briefings are linked from the reaction page.
- **`uk_ippr`:** the three 28 October responses on the media-office listing: "Unfinished business" (`f834beaa…`), IPPR North (`9b1e6ee7…`) and IPPR Scotland (`9f328d54…`, 0 rows).

Full hashes are in each `manifest.jsonl`.

## Rows by measure key

- **`uk_tpa`:**
  - `null`: 207 (65 with a proposed key, 142 context).
  - `ab2026__package_total_tax_policy_decisions` 37, `writing_down_allowance_12pc_and_fya_50pc` 15, `bank_surcharge_6pc_temporary` 11, `hmrc_tax_gap_package` 8, `foreign_permanent_establishment_exemption_mandatory` 5, `foreign_sovereign_investments_taxation` 4, `pension_tax_allowance` 3, `electricity_vat_zero_rate_to_july_2027` 2.
  - One row each for the measures on lines 3, 5, 15, 26, 44, 46, 49, 56, 59, 60, 61, 62, 86 and 96.
- **`uk_centax`:** `null` 108 (52 proposed, 56 context); `pension_tax_allowance` 1; `hmrc_tax_gap_package` 1.
- **`uk_ippr`:** `null` 3 (2 proposed, 1 context).

## Proposed keys and their scope

**TPA (14).** TPA groups the Table 6.1 tax lines in its charts but doesn't publish the mapping ("available on request"). I recovered it by matching values. Each by-year group reproduces TPA's figures exactly in all six years, and the groups partition the 53 tax lines. Deflators fitted to the real-terms chart reproduce all 23 of its bars to within £1m.

| key | Table 6.1 lines |
|---|---|
| `ab2026__package_property_and_savings_income_rates` (redbook's spelling) | 61, 62 |
| `…_tpa_savings_property_income_and_cash_isa` | 11, 61, 62 |
| `…_tpa_temporary_vat_and_fuel_cuts` | 2, 3, 18, 65, 66 |
| `…_tpa_fuel_duty_red_diesel_and_hgv_ved` | 3, 18, 65 |
| `…_tpa_business_rates` | 12, 13, 14, 57, 76, 80 |
| `…_tpa_energy_and_environment` | 17, 69, 71, 90, 96 |
| `…_tpa_other_income_tax` | 5, 15, 28, 52, 53, 86, 94 |
| `…_tpa_other_vat` | 36, 46, 51, 59, 88, 89 |
| `…_tpa_other_corporate_tax` | 49, 50, 54, 68, 97 |
| `…_tpa_other_by_year` | 10, 16, 19, 26, 44, 56, 60, 77, 78, 79, 93, 95, 98 |
| `…_tpa_tariffs` | 10, 16, 77, 78, 95 |
| `…_tpa_cgt_founders_relief_and_badr` | 26, 60 |
| `…_tpa_other_by_tax_2027_28` | 17, 19, 44, 56, 69, 71, 79, 90, 93, 96, 98 (line 66 undetermined, zero in 2027-28) |
| `…_tpa_other_by_measure` | 11, 17, 18, 19, 28, 36, 50, 51, 53, 65, 66, 69, 71, 79, 88, 89, 90, 93, 94, 97, 98 |

**CenTax (7 options, none on a Table 6.1 line):**
- `ab2026_option__cgt_reform_package`: equalise CGT with income tax rates, an investment allowance, removal of uplift at death, and rebasing on arrival with deemed disposal on departure.
- `…__nics_on_partnership_income`: an Employer NICs equivalent on partnership profits, with a £10,500 allowance and a £5,000 exempt amount.
- `…__nics_on_investment_income`: Class 1 NICs on rental, savings and other non-dividend investment income.
- Four childcare options at the £100,000 threshold: `…__childcare_100k_threshold_removed`, `…_removed_first_15_hours_under_3s`, `…_threshold_raised` (£125k or £150k) and `…_entitlement_taper` (8p, 18p or 28p).

**IPPR (2):**
- `ab2026__package_cost_of_living_support`: IPPR doesn't define its scope; the matching OBR figure covers lines 2 and 3.
- `ab2026_option__income_tax_5pc_share_devolved_to_mayors`.

**Attribution rule.** TPA builds no yield estimates of its own:
- A single HMT number it repeats is `restated`.
- Its re-expressions (sums, deflation, ratios to GDP) are `own`, with `source_model: arithmetic` and `conditions.derived_from` naming the HMT input. This matches the IFS lane, so please confirm the convention across lanes.

## Not staged

- **CPAG (both pages) and SMF:** unreached. Each returned HTTP 403 with a Cloudflare challenge on two fetches, at 16:17Z and 16:37Z. No local copy was listed, so I didn't try to get round it. The challenge pages' hashes are in NOTES as evidence only; a local copy would let a re-run stage them.
- **Design under rule 8:** rates, thresholds, payment amounts and allocations, including the £100 Household Energy Payment, the £1.5bn borrowing facility and the 24/44/49% rates.
- **Other exclusions:**
  - duplicate phrasings within one primary;
  - charts with no printed values (CenTax's figures);
  - Unicorn Relief's illustrations, since it costs no relief;
  - reader comments under the TPA article;
  - TPA's approximate "£3,000bn GDP", which has no year.
- **CenTax's childcare report:** not re-staged, because #207 already holds it in `data/externals/centax-childcare-100k.json`.
- **Outside the assigned scope, hashed and listed in NOTES for a follow-up:** IPPR's pre-Budget releases of 8, 15 and 27 October, which include £16bn of options and a £1bn bank windfall surcharge, and TPA's 22 October bank-tax article.

## Checks

- **Checker:** all five families report 0 problems under the updated checker.
- **Self-checks:** each `stage.py --verify` finds every quote in its primary, reads every chart value back from its JSON path, and re-derives the TPA group scopes. All pass.
- **My spot check, on the final files:**
  - **TPA (20 rows):** 19, 24, 29, 35, 37, 44, 46, 48, 77, 109, 123, 165, 187, 202, 214, 222, 259, 274, 282, 298.
  - **CenTax (10 rows):** 6, 9, 12, 19, 41, 46, 50, 68, 83, 105.
  - **IPPR:** all 3 rows (0, 1, 2).
  - Each was re-opened at its locator; number, sign, unit and period all match.
- **Independent check:** a separate agent checked 15 more rows. It found no number, sign, unit, period or quote errors, and reproduced all 11 by-year groups with no alternative mapping. It did find scope problems, now fixed:
  - TPA's bank levy and VAT components carried the surcharge key, though the surcharge doesn't change them;
  - zero fills for years before Table 6.1 starts carried the total key;
  - footnote 15's £450m/£495m range ends sat at the wrong years;
  - line 66 sat in TPA's by-tax "Other";
  - one NOTES sentence on net totals was wrong;
  - the calculator rows used "change" metrics for levels;
  - IPPR's £285m was a component of line 20, not the whole line.

## Problems in the primaries (reported, not fixed)

- **TPA's Pension Tax Allowance figures:** the article says "up to £94 a year" and, a paragraph later, "£93". The stated rule on TPA's own £13,036.40 gives £93.28, and the £282 band is 3 × £94.
- **TPA's start year:** the £123bn sentence says "since 2021"; footnote 3 says "since March 2020".
- **OBR's property figure:** OBR paragraph 3.17 gives £0.4bn a year from 2028-29 for the property rise, below Table 6.1 line 61's average of £478m.

## Other lanes' output

- **uk_hmt_redbook:**
  - It stages "84% of income tax payers will be unaffected" as `affected_share` = 84, which inverts the meaning.
  - It stages the £285m Good Growth Funds allocation as a row, which rule 8 may now exclude.
- **Timely-payment key:** redbook and costings each propose a different key, but rule 9 now puts it on line 45 as a component.

HANDED TO the harvest coordinator for merge into PR #231.