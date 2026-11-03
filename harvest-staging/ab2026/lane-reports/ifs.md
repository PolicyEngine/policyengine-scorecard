Staged **106 IFS rows** in `uk_ifs_ab2026`, with five manifested PDF versions. Full evidence and verification are in [NOTES.md](/Users/maxghenis/reviews/scorecard-ab2026-harvest/wt/ifs/sources/harvest-uk-ab2026-2026-10-29/uk_ifs_ab2026/NOTES.md). No commits or pushes.

Rows by `measure_key`—all named keys have prefix `ab2026__`:

| Key suffix | Rows |
|---|---:|
| null | 85 |
| founders_relief_cgt | 6 |
| household_energy_payment_100_bands_a_to_d | 4 |
| business_rates_sbrr_rhl_thresholds_raised | 3 |
| fuel_duty_5p_cut_extended_and_rpi_rise_deferred | 2 |
| bus_fare_cap_2_england_outside_london_2027 | 1 |
| package_total_tax_policy_decisions | 1 |
| writing_down_allowance_12pc_and_fya_50pc | 1 |
| distributions_framework_modernised | 1 |
| badr_lifetime_limit_500000 | 1 |
| electricity_vat_zero_rate_to_july_2027 | 1 |

Primaries and SHA256s:

| Primary | Rows | SHA256 |
|---|---:|---|
| Stockton | 39 | `fd09e707a4bc0a8e0a3de4a3fa902c8ccdc1e4c44ccdd0dee92866857aa4690b` |
| Wernham TW_0, local copy | 0 | `abb63d9c4ecd21c3c9173077c5e92d8015c7cc30aebd12be159185d7d157f12a` |
| Wernham TW_1 | 21 | `6ed174b22b4d22a34c8bbd450194fb2b4181a9d566b137913bee52ca49a0299b` |
| Boileau | 28 | `7403ecc0641b23f5ffc0cb28f67435dbd1b8df6b124874ffae7ae7f75e357aa6` |
| Adam | 18 | `6792dc448f40d34f174b6a3c839863b5c969a7334263f5d6b539be62a0428bb8` |

Seven proposed measure keys use prefix `ab2026__package_ifs_`:

| Suffix | Scope |
|---|---|
| cost_of_living_support | Lines 1 and 3, plus full October–June electricity VAT relief including previously announced support |
| electricity_vat_oct_2026_june_2027 | Line 2 extension plus previously announced VAT relief |
| gas_standing_charge_reallocation | Gas standing charges shifted onto unit prices; no Table 6.1 counterpart |
| defence_investment_plan_funding | £1.2bn annual funding gap; lines 40–42 related, exact allocation unspecified |
| self_assessment_payment_timing | Earlier self-assessment payments; no distinct line established |
| savings_and_property_income_tax | Exactly lines 61 and 62 |
| hmrc_compliance_staff_and_debt_collection | Staffing/debt-collection subset of line 45 |

The contract checker reported **106 rows, 0 problems**. Re-running `stage.py` preserved gzip SHA256:

`4f0c9cd197d970486608ea093bf3822ae1d92fa56ebc4a2ac1fae3086430b1cb`

Ten random checks, seed 230, passed value, sign, unit and period checks:

| Row | Locator | Checked figure and period |
|---:|---|---|
| 3 | Stockton slide 7 | −0.4% GDP, FY2029–30 |
| 21 | Stockton slide 7 | +3.4% GDP change, FY2026–27 |
| 39 | Stockton slide 8 | Roughly 1 in 4 → 0.25 share; Spring 2027 inferred |
| 56 | Wernham slide 8 | 60% gainers; implementation year unspecified |
| 69 | Boileau slide 7 | +2.7% real growth, FY2027–28 to FY2030–31 |
| 85 | Boileau slide 10 | +1 percentage point historical revision |
| 87 | Boileau slide 11 | 40% reserve allocated, FY2027–28 to FY2028–29 |
| 91 | Adam slide 2 | £1.1bn yield, FY2031–32 |
| 93 | Adam slide 2 | £1bn yield, FY2031–32 |
| 106 | Adam slide 5 | 0% electricity VAT parameter |

The initial response, explainer, collection and event pages returned Cloudflare 403s. No HTML figures or linked data downloads could be staged. Unlabelled chart values were excluded. TW_0’s blocked fetch used the supplied local copy; its replacement changed layout/repetition, with no numerical change.

Source issues are documented without correction: Adam’s cover date conflicts with the briefing date; its £1.1bn savings/property figure differs from the corresponding £1.045bn official total; several implementation dates are unspecified; and Stockton’s table gives no explicit source citation, so attribution is disclosed as inferred.