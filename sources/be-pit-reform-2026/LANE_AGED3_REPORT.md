# LANE AGED3 — declared handling for the RD-pending pieces

Microcosm-BE: synthetic Belgian population calibrated to Belgian administrative and national-accounts targets (sums of Chronicle facts; surveys validation-only). Support records: US survey donor pool, reweighted; a Belgian donor pool is the planned upgrade. Cross-engine agreement is evidence about the encodings.

AGED VARIANT: incomes uprated and parameters indexed per declared FPB projections (record ids cited); population structure, weights, and behaviour static at 2025. Not a forecast — a projection-conditioned mechanics comparison. royal-decree-pending parameters carried at last enacted values, flagged and quantified.

Status: **COMPLETE_WITH_DECLARED_RD_PENDING_ASSUMPTIONS**. The final five-year score and terminal handoff are complete under the two declared assumptions below; `public_release=false` remains explicit.

The Article 178 resolution at `563cf35` stands unchanged, including all 30 coefficients. Commit `8f1bbf1` applies the declared design ruling: Royal-Decree-pending Article 147 inputs are carried at their last enacted or known values, labelled `RD_PENDING`, and quantified; the supplied Article 289ter self-employment credit remains `FROZEN_SUPPLIED`.

No EUROMOD process was started or used. The sealed population and weights were read only; population structure, weights, and behaviour remain static at 2025. Nothing under `out/v05e/`, `out/v05f/`, or `out/v05g/` was edited by this lane, and there was no push or stash operation.

## Result boundary and headline

Each aged delta is reform revenue minus a same-year aged current-law baseline. Assessment year N uses income year N−1. Positive aged-minus-static values mean a smaller estimated revenue loss than in the static exercise; they are not revenue gains.

| AY | Static Δ, EUR | Aged Δ, EUR | Aged minus static, EUR |
|---|---|---|---|
| AY2027 | -619,599,166.74 | -513,454,844.21 | 106,144,322.52 |
| AY2028 | -705,902,818.44 | -456,511,621.84 | 249,391,196.60 |
| AY2029 | -1,156,428,816.07 | -779,679,224.51 | 376,749,591.56 |
| AY2030 | -5,496,024,285.98 | -2,457,460,040.32 | 3,038,564,245.66 |
| AY2031 | -7,236,041,218.53 | -4,155,521,961.68 | 3,080,519,256.85 |

Year-specific drivers:
- AY2027: The aged-minus-static difference reflects first-year wage, pension, self-employment, and movable-income growth, the projected fall in replacement income, and both policies' AY2027-indexed parameters.

- AY2028: The larger cumulative nominal-income shift and the second reform step for the tax-free amount, child amounts, and marital cap move the aged comparison away from the frozen-2025 static cell.

- AY2029: Further wage and pension growth combines with the reform's higher Article 289ter/1 work-bonus rates while projected replacement income remains well below its 2025 level.

- AY2030: The direct EUR 14,450 reform tax-free amount is compared with an AY2030-indexed baseline on 2029 incomes, removing the static cell's nominal-basis mismatch while reform Article 147 inputs are RD_PENDING.

- AY2031: The direct EUR 15,600 reform tax-free amount, the Article 132/133 coefficient step-up, and the senior-age change are compared with an AY2031-indexed baseline while Article 147 RD_PENDING inputs remain carried.

The aged path materially attenuates the static AY2030–2031 cliff, but does not eliminate it and is not monotonic: the same-year revenue loss is EUR 2.46bn in AY2030 and EUR 4.16bn in AY2031. The comparison is a projection-conditioned mechanics result, not a forecast.

## Five same-year aged baseline/reform pairs

The table reports the complete fiscal surface needed to reproduce the v05e-style headline. Ordinary PIT is `pit_revenue`; total PIT adds capital PIT. Employee SSC and capital PIT are identical between policies within each assessment year, so the stored budget delta equals the ordinary-PIT change up to floating summation tolerance.

| AY | Baseline PIT | Reform PIT | Baseline SSC | Reform SSC | Baseline capital PIT | Reform capital PIT | Baseline total PIT | Reform total PIT | Fiscal Δ |
|---|---|---|---|---|---|---|---|---|---|
| AY2027 | 64,442,555,292.97 | 63,929,100,448.76 | 20,191,908,481.28 | 20,191,908,481.28 | 12,512,635,286.63 | 12,512,635,286.63 | 76,955,190,579.60 | 76,441,735,735.39 | -513,454,844.21 |
| AY2028 | 67,375,170,825.93 | 66,918,659,204.09 | 21,456,923,243.15 | 21,456,923,243.15 | 13,007,312,501.10 | 13,007,312,501.10 | 80,382,483,327.03 | 79,925,971,705.19 | -456,511,621.84 |
| AY2029 | 69,749,820,800.27 | 68,970,141,575.76 | 22,439,074,038.50 | 22,439,074,038.50 | 13,382,967,379.72 | 13,382,967,379.72 | 83,132,788,179.99 | 82,353,108,955.48 | -779,679,224.51 |
| AY2030 | 72,204,853,288.93 | 69,747,393,248.61 | 23,334,149,436.87 | 23,334,149,436.87 | 13,808,689,588.53 | 13,808,689,588.53 | 86,013,542,877.46 | 83,556,082,837.14 | -2,457,460,040.32 |
| AY2031 | 75,354,501,442.10 | 71,198,979,480.42 | 24,302,109,259.89 | 24,302,109,259.89 | 14,277,883,431.34 | 14,277,883,431.34 | 89,632,384,873.44 | 85,476,862,911.76 | -4,155,521,961.68 |

Distribution metrics use each year's same-year baseline:

| AY | Baseline Gini | Reform Gini | Baseline median eqd | Reform median eqd | Baseline AROP | Reform AROP | Winners | Losers |
|---|---|---|---|---|---|---|---|---|
| AY2027 | 0.3104 | 0.3102 | 28,292.00 | 28,315.00 | 17.6000% | 17.5800% | 75.6100% | 6.4100% |
| AY2028 | 0.3132 | 0.3130 | 29,089.00 | 29,123.00 | 17.7500% | 17.6000% | 74.0200% | 8.2700% |
| AY2029 | 0.3145 | 0.3142 | 29,738.00 | 29,835.00 | 17.4200% | 17.4200% | 74.0400% | 8.3100% |
| AY2030 | 0.3157 | 0.3152 | 30,553.00 | 30,838.00 | 17.5300% | 16.9600% | 61.4800% | 21.0800% |
| AY2031 | 0.3168 | 0.3160 | 31,312.00 | 31,974.00 | 17.4000% | 16.9100% | 82.2900% | 0.3400% |

Mean equivalised disposable-income gain by fixed baseline decile, EUR:

| AY | D1 | D2 | D3 | D4 | D5 | D6 | D7 | D8 | D9 | D10 |
|---|---|---|---|---|---|---|---|---|---|---|
| AY2027 | 16.31 | 31.48 | 87.06 | 130.43 | 108.57 | 101.37 | 101.90 | 159.53 | 125.95 | 124.91 |
| AY2028 | 17.22 | 39.05 | 94.35 | 132.38 | 82.99 | 76.75 | 80.62 | 143.52 | 81.58 | 123.29 |
| AY2029 | 31.07 | 59.33 | 143.96 | 237.81 | 139.37 | 143.09 | 145.82 | 232.83 | 155.90 | 193.85 |
| AY2030 | 45.90 | 156.50 | 390.61 | 530.72 | 431.23 | 489.73 | 602.52 | 716.81 | 800.30 | 598.77 |
| AY2031 | 63.59 | 271.14 | 659.82 | 827.34 | 743.95 | 880.59 | 1,039.89 | 1,160.26 | 1,377.88 | 1,047.34 |

Decile ranks are fixed within each same-year baseline/reform pair, not across all five assessment years. Growth in baseline PIT between years is therefore not itself a policy effect.

## Worked single-worker cases in nominal aged euros

These are literal €30k, €45k, and €60k nominal amounts in each assessment year's income year for a single worker with no dependants and the declared 7% communal rate. They are not 2025 amounts multiplied by the wage factor.

| AY | Gross | Baseline PIT | Reform PIT | PIT change | Baseline SSC | Reform SSC | Disposable gain |
|---|---|---|---|---|---|---|---|
| AY2027 | €30k | 1,964.49 | 1,796.11 | -168.38 | 1,591.35 | 1,591.35 | 168.38 |
| AY2027 | €45k | 6,498.62 | 6,424.34 | -74.28 | 5,881.50 | 5,881.50 | 74.28 |
| AY2027 | €60k | 11,210.21 | 11,135.93 | -74.28 | 7,842.00 | 7,842.00 | 74.28 |
| AY2028 | €30k | 1,752.10 | 1,559.64 | -192.46 | 1,591.35 | 1,591.35 | 192.46 |
| AY2028 | €45k | 6,237.66 | 6,139.29 | -98.37 | 5,881.50 | 5,881.50 | 98.37 |
| AY2028 | €60k | 10,949.24 | 10,850.88 | -98.36 | 7,842.00 | 7,842.00 | 98.36 |
| AY2029 | €30k | 1,567.82 | 1,219.30 | -348.52 | 1,591.35 | 1,591.35 | 348.52 |
| AY2029 | €45k | 6,010.82 | 5,864.28 | -146.54 | 5,881.50 | 5,881.50 | 146.54 |
| AY2029 | €60k | 10,722.41 | 10,575.87 | -146.54 | 7,842.00 | 7,842.00 | 146.54 |
| AY2030 | €30k | 1,416.07 | 754.39 | -661.68 | 1,591.35 | 1,591.35 | 661.68 |
| AY2030 | €45k | 5,823.73 | 5,364.03 | -459.70 | 5,881.50 | 5,881.50 | 459.70 |
| AY2030 | €60k | 10,535.32 | 10,075.62 | -459.70 | 7,842.00 | 7,842.00 | 459.70 |
| AY2031 | €30k | 1,293.61 | 445.25 | -848.36 | 1,591.35 | 1,591.35 | 848.36 |
| AY2031 | €45k | 5,685.68 | 5,039.30 | -646.38 | 5,881.50 | 5,881.50 | 646.38 |
| AY2031 | €60k | 10,384.76 | 9,738.38 | -646.38 | 7,842.00 | 7,842.00 | 646.38 |

## RD_PENDING parameter schedule and exposure

The 450-row scenario/year parameter table contains 14 scenario-specific `RD_PENDING` cells. They collapse to 9 unique parameter/year rows because the additional-reduction row applies to both policies. The table below reports input-footprint exposure, not a causal tax-effect sensitivity. People and euros are not multiplied by the scenario count, and repeated parameter rows must not be summed.

| AY | Parameter | Status | Policies | Carried value | Raw statutory base, EUR | Article 178 coeff. | Engine value, EUR | Weighted unique persons | Weighted execution units | Weighted input footprint, EUR | Source/assumption |
|---|---|---|---|---|---|---|---|---|---|---|---|
| AY2027 | belgium_pit_article_147_additional_replacement_reduction | RD_PENDING | baseline, reform | applied indexed slot | 236.38 | 1.9793 | 457.23 | 3,606,348.26 | 3,743,439.00 | 79,156,053,128.10 | assumption_authority: fable, 2026-08-26 ~10:20; LANE_AGED3_PROMPT.md<br>last_enacted_known_value: AY2026 applied amount EUR 457.23<br>source: RuleSpec-BE ddc28fe7fba3509019a2b80ada5fb6f3ee922839, tax_reductions_and_credits.yaml; CIR 1992 Article 147, consolidated page 253 |
| AY2028 | belgium_pit_article_147_additional_replacement_reduction | RD_PENDING | baseline, reform | applied indexed slot | 236.38 | 2.0466 | 457.23 | 3,606,348.26 | 3,743,439.00 | 82,008,310,403.95 | assumption_authority: fable, 2026-08-26 ~10:20; LANE_AGED3_PROMPT.md<br>last_enacted_known_value: AY2026 applied amount EUR 457.23<br>source: RuleSpec-BE ddc28fe7fba3509019a2b80ada5fb6f3ee922839, tax_reductions_and_credits.yaml; CIR 1992 Article 147, consolidated page 253 |
| AY2029 | belgium_pit_article_147_additional_replacement_reduction | RD_PENDING | baseline, reform | applied indexed slot | 236.38 | 2.1059 | 457.23 | 3,606,348.26 | 3,743,439.00 | 84,730,338,000.43 | assumption_authority: fable, 2026-08-26 ~10:20; LANE_AGED3_PROMPT.md<br>last_enacted_known_value: AY2026 applied amount EUR 457.23<br>source: RuleSpec-BE ddc28fe7fba3509019a2b80ada5fb6f3ee922839, tax_reductions_and_credits.yaml; CIR 1992 Article 147, consolidated page 253 |
| AY2030 | belgium_pit_article_147_additional_replacement_reduction | RD_PENDING | baseline, reform | applied indexed slot | 236.38 | 2.1544 | 457.23 | 3,606,348.26 | 3,743,439.00 | 87,304,448,992.33 | assumption_authority: fable, 2026-08-26 ~10:20; LANE_AGED3_PROMPT.md<br>last_enacted_known_value: AY2026 applied amount EUR 457.23<br>source: RuleSpec-BE ddc28fe7fba3509019a2b80ada5fb6f3ee922839, tax_reductions_and_credits.yaml; CIR 1992 Article 147, consolidated page 253 |
| AY2030 | belgium_pit_article_147_basic_replacement_reduction | RD_PENDING | reform | raw statutory input before Article 178 | 837.71 | 2.1544 | 1804.76 | 3,606,348.26 | 3,743,439.00 | 87,304,448,992.33 | assumption_authority: fable, 2026-08-26 ~10:20; LANE_AGED3_PROMPT.md<br>interpretation: respect the enacted AY2030 substitution and assume no further Royal-Decree neutralization; this is not a claim about the future decree<br>last_enacted_known_value: AY2030 enacted statutory amount EUR 837.71; carried unchanged into AY2031<br>reform_law_sha256: c95eda87835a874fc49cc84f2d65b834c2f372b150e6b65a1732a1b2f485f9d1<br>source: beReform cf05994bc815d70014eff64261d296c200402384, tax_reductions_and_credits.yaml; M.B. 29 July 2026 Articles 3(d), 3(f), 3(g), and 4 |
| AY2030 | belgium_pit_article_147_sickness_invalidity_reduction | RD_PENDING | reform | raw statutory input before Article 178 | 1230.46 | 2.1544 | 2650.90 | 0.00 | 0.00 | 0.00 | assumption_authority: fable, 2026-08-26 ~10:20; LANE_AGED3_PROMPT.md<br>interpretation: respect the enacted AY2030 substitution and assume no further Royal-Decree neutralization; this is not a claim about the future decree<br>last_enacted_known_value: AY2030 enacted statutory amount EUR 1,230.46; carried unchanged into AY2031<br>reform_law_sha256: c95eda87835a874fc49cc84f2d65b834c2f372b150e6b65a1732a1b2f485f9d1<br>source: beReform cf05994bc815d70014eff64261d296c200402384, tax_reductions_and_credits.yaml; M.B. 29 July 2026 Articles 3(d), 3(f), 3(g), and 4 |
| AY2031 | belgium_pit_article_147_additional_replacement_reduction | RD_PENDING | baseline, reform | applied indexed slot | 236.38 | 2.1932 | 457.23 | 3,606,348.26 | 3,743,439.00 | 90,452,186,781.22 | assumption_authority: fable, 2026-08-26 ~10:20; LANE_AGED3_PROMPT.md<br>last_enacted_known_value: AY2026 applied amount EUR 457.23<br>source: RuleSpec-BE ddc28fe7fba3509019a2b80ada5fb6f3ee922839, tax_reductions_and_credits.yaml; CIR 1992 Article 147, consolidated page 253 |
| AY2031 | belgium_pit_article_147_basic_replacement_reduction | RD_PENDING | reform | raw statutory input before Article 178 | 837.71 | 2.1932 | 1837.27 | 3,606,348.26 | 3,743,439.00 | 90,452,186,781.22 | assumption_authority: fable, 2026-08-26 ~10:20; LANE_AGED3_PROMPT.md<br>interpretation: respect the enacted AY2030 substitution and assume no further Royal-Decree neutralization; this is not a claim about the future decree<br>last_enacted_known_value: AY2030 enacted statutory amount EUR 837.71; carried unchanged into AY2031<br>reform_law_sha256: c95eda87835a874fc49cc84f2d65b834c2f372b150e6b65a1732a1b2f485f9d1<br>source: beReform cf05994bc815d70014eff64261d296c200402384, tax_reductions_and_credits.yaml; M.B. 29 July 2026 Articles 3(d), 3(f), 3(g), and 4 |
| AY2031 | belgium_pit_article_147_sickness_invalidity_reduction | RD_PENDING | reform | raw statutory input before Article 178 | 1230.46 | 2.1932 | 2698.64 | 0.00 | 0.00 | 0.00 | assumption_authority: fable, 2026-08-26 ~10:20; LANE_AGED3_PROMPT.md<br>interpretation: respect the enacted AY2030 substitution and assume no further Royal-Decree neutralization; this is not a claim about the future decree<br>last_enacted_known_value: AY2030 enacted statutory amount EUR 1,230.46; carried unchanged into AY2031<br>reform_law_sha256: c95eda87835a874fc49cc84f2d65b834c2f372b150e6b65a1732a1b2f485f9d1<br>source: beReform cf05994bc815d70014eff64261d296c200402384, tax_reductions_and_credits.yaml; M.B. 29 July 2026 Articles 3(d), 3(f), 3(g), and 4 |

The €457.23 additional reduction is the carried applied value. For AY2030–2031 the carried raw basic and sickness/invalidity inputs are €837.71 and €1,230.46; Article 178 still changes their engine values. Zero sickness/invalidity exposure means that the sealed input is forced to zero and dormant here, not that a future decree would be economically irrelevant.

## Frozen supplied Article 289ter self-employment credit

The supplied credit remains `FROZEN_SUPPLIED` byte-for-byte because it is an input with no statutory aging mechanism. It has 1,730 nonzero raw records, 363,804.86 weighted persons, and EUR 226,467,432.32 weighted magnitude.

| AY | Status | Weighted persons | Weighted magnitude, EUR |
|---|---|---|---|
| AY2027 | FROZEN_SUPPLIED | 363,804.86 | 226,467,432.32 |
| AY2028 | FROZEN_SUPPLIED | 363,804.86 | 226,467,432.32 |
| AY2029 | FROZEN_SUPPLIED | 363,804.86 | 226,467,432.32 |
| AY2030 | FROZEN_SUPPLIED | 363,804.86 | 226,467,432.32 |
| AY2031 | FROZEN_SUPPLIED | 363,804.86 | 226,467,432.32 |

The magnitude is repeated as a disclosure for each assessment year; the five rows are not additive annual exposures.

## Declared 25-row income-factor table

Each factor equals the declared FPB income-year aggregate divided by the same aggregate for 2025. Factors are applied absolutely from the immutable setup snapshots, never compounded year to year.

| Concept | AY | Income year | Numerator, EUR bn | 2025 denominator, EUR bn | Ratio | Numerator record ID(s) | Denominator record ID(s) |
|---|---|---|---|---|---|---|---|
| wages | 2027 | 2026 | 329.711 | 320.578 | 1.0284891664431122 | fpb.economic_outlook_2026_2031.cy2026.household_account.compensation_of_employees.amount_meur | fpb.economic_outlook_2026_2031.cy2025.household_account.compensation_of_employees.amount_meur |
| self_employment | 2027 | 2026 | 41.044 | 39.834 | 1.0303760606517045 | fpb.economic_outlook_2026_2031.cy2026.household_account.net_mixed_income.amount_meur | fpb.economic_outlook_2026_2031.cy2025.household_account.net_mixed_income.amount_meur |
| pensions | 2027 | 2026 | 73.902 | 71.195 | 1.0380223330290048 | fpb.economic_outlook_2026_2031.cy2026.social_benefits_detail.social_security_cash_pensions_total.amount_meur<br>fpb.economic_outlook_2026_2031.cy2026.social_benefits_detail.federal_government_cash_public_sector_pensions.amount_meur<br>fpb.economic_outlook_2026_2031.cy2026.social_benefits_detail.communities_and_regions_cash_public_sector_pensions.amount_meur<br>fpb.economic_outlook_2026_2031.cy2026.social_benefits_detail.local_governments_cash_public_sector_pensions.amount_meur | fpb.economic_outlook_2026_2031.cy2025.social_benefits_detail.social_security_cash_pensions_total.amount_meur<br>fpb.economic_outlook_2026_2031.cy2025.social_benefits_detail.federal_government_cash_public_sector_pensions.amount_meur<br>fpb.economic_outlook_2026_2031.cy2025.social_benefits_detail.communities_and_regions_cash_public_sector_pensions.amount_meur<br>fpb.economic_outlook_2026_2031.cy2025.social_benefits_detail.local_governments_cash_public_sector_pensions.amount_meur |
| replacement_income | 2027 | 2026 | 5.177 | 6.510 | 0.7952380952380952 | fpb.economic_outlook_2026_2031.cy2026.social_benefits_detail.social_security_cash_unemployment_total.amount_meur | fpb.economic_outlook_2026_2031.cy2025.social_benefits_detail.social_security_cash_unemployment_total.amount_meur |
| movable | 2027 | 2026 | 41.736 | 40.219 | 1.0377184912603497 | fpb.economic_outlook_2026_2031.cy2026.household_account.interest_received.amount_meur<br>fpb.economic_outlook_2026_2031.cy2026.household_account.distributed_income_of_corporations.amount_meur | fpb.economic_outlook_2026_2031.cy2025.household_account.interest_received.amount_meur<br>fpb.economic_outlook_2026_2031.cy2025.household_account.distributed_income_of_corporations.amount_meur |
| wages | 2028 | 2027 | 343.380 | 320.578 | 1.0711277754555832 | fpb.economic_outlook_2026_2031.cy2027.household_account.compensation_of_employees.amount_meur | fpb.economic_outlook_2026_2031.cy2025.household_account.compensation_of_employees.amount_meur |
| self_employment | 2028 | 2027 | 42.369 | 39.834 | 1.063639102274439 | fpb.economic_outlook_2026_2031.cy2027.household_account.net_mixed_income.amount_meur | fpb.economic_outlook_2026_2031.cy2025.household_account.net_mixed_income.amount_meur |
| pensions | 2028 | 2027 | 77.199 | 71.195 | 1.0843317648711286 | fpb.economic_outlook_2026_2031.cy2027.social_benefits_detail.social_security_cash_pensions_total.amount_meur<br>fpb.economic_outlook_2026_2031.cy2027.social_benefits_detail.federal_government_cash_public_sector_pensions.amount_meur<br>fpb.economic_outlook_2026_2031.cy2027.social_benefits_detail.communities_and_regions_cash_public_sector_pensions.amount_meur<br>fpb.economic_outlook_2026_2031.cy2027.social_benefits_detail.local_governments_cash_public_sector_pensions.amount_meur | fpb.economic_outlook_2026_2031.cy2025.social_benefits_detail.social_security_cash_pensions_total.amount_meur<br>fpb.economic_outlook_2026_2031.cy2025.social_benefits_detail.federal_government_cash_public_sector_pensions.amount_meur<br>fpb.economic_outlook_2026_2031.cy2025.social_benefits_detail.communities_and_regions_cash_public_sector_pensions.amount_meur<br>fpb.economic_outlook_2026_2031.cy2025.social_benefits_detail.local_governments_cash_public_sector_pensions.amount_meur |
| replacement_income | 2028 | 2027 | 4.731 | 6.510 | 0.7267281105990784 | fpb.economic_outlook_2026_2031.cy2027.social_benefits_detail.social_security_cash_unemployment_total.amount_meur | fpb.economic_outlook_2026_2031.cy2025.social_benefits_detail.social_security_cash_unemployment_total.amount_meur |
| movable | 2028 | 2027 | 43.386 | 40.219 | 1.0787438772719362 | fpb.economic_outlook_2026_2031.cy2027.household_account.interest_received.amount_meur<br>fpb.economic_outlook_2026_2031.cy2027.household_account.distributed_income_of_corporations.amount_meur | fpb.economic_outlook_2026_2031.cy2025.household_account.interest_received.amount_meur<br>fpb.economic_outlook_2026_2031.cy2025.household_account.distributed_income_of_corporations.amount_meur |
| wages | 2029 | 2028 | 353.918 | 320.578 | 1.1039996506310477 | fpb.economic_outlook_2026_2031.cy2028.household_account.compensation_of_employees.amount_meur | fpb.economic_outlook_2026_2031.cy2025.household_account.compensation_of_employees.amount_meur |
| self_employment | 2029 | 2028 | 43.759 | 39.834 | 1.098533915750364 | fpb.economic_outlook_2026_2031.cy2028.household_account.net_mixed_income.amount_meur | fpb.economic_outlook_2026_2031.cy2025.household_account.net_mixed_income.amount_meur |
| pensions | 2029 | 2028 | 80.000 | 71.195 | 1.1236744153381557 | fpb.economic_outlook_2026_2031.cy2028.social_benefits_detail.social_security_cash_pensions_total.amount_meur<br>fpb.economic_outlook_2026_2031.cy2028.social_benefits_detail.federal_government_cash_public_sector_pensions.amount_meur<br>fpb.economic_outlook_2026_2031.cy2028.social_benefits_detail.communities_and_regions_cash_public_sector_pensions.amount_meur<br>fpb.economic_outlook_2026_2031.cy2028.social_benefits_detail.local_governments_cash_public_sector_pensions.amount_meur | fpb.economic_outlook_2026_2031.cy2025.social_benefits_detail.social_security_cash_pensions_total.amount_meur<br>fpb.economic_outlook_2026_2031.cy2025.social_benefits_detail.federal_government_cash_public_sector_pensions.amount_meur<br>fpb.economic_outlook_2026_2031.cy2025.social_benefits_detail.communities_and_regions_cash_public_sector_pensions.amount_meur<br>fpb.economic_outlook_2026_2031.cy2025.social_benefits_detail.local_governments_cash_public_sector_pensions.amount_meur |
| replacement_income | 2029 | 2028 | 4.650 | 6.510 | 0.7142857142857143 | fpb.economic_outlook_2026_2031.cy2028.social_benefits_detail.social_security_cash_unemployment_total.amount_meur | fpb.economic_outlook_2026_2031.cy2025.social_benefits_detail.social_security_cash_unemployment_total.amount_meur |
| movable | 2029 | 2028 | 44.639 | 40.219 | 1.1098983067704318 | fpb.economic_outlook_2026_2031.cy2028.household_account.interest_received.amount_meur<br>fpb.economic_outlook_2026_2031.cy2028.household_account.distributed_income_of_corporations.amount_meur | fpb.economic_outlook_2026_2031.cy2025.household_account.interest_received.amount_meur<br>fpb.economic_outlook_2026_2031.cy2025.household_account.distributed_income_of_corporations.amount_meur |
| wages | 2030 | 2029 | 363.710 | 320.578 | 1.1345444790347434 | fpb.economic_outlook_2026_2031.cy2029.household_account.compensation_of_employees.amount_meur | fpb.economic_outlook_2026_2031.cy2025.household_account.compensation_of_employees.amount_meur |
| self_employment | 2030 | 2029 | 45.157 | 39.834 | 1.1336295626851434 | fpb.economic_outlook_2026_2031.cy2029.household_account.net_mixed_income.amount_meur | fpb.economic_outlook_2026_2031.cy2025.household_account.net_mixed_income.amount_meur |
| pensions | 2030 | 2029 | 82.568 | 71.195 | 1.1597443640705105 | fpb.economic_outlook_2026_2031.cy2029.social_benefits_detail.social_security_cash_pensions_total.amount_meur<br>fpb.economic_outlook_2026_2031.cy2029.social_benefits_detail.federal_government_cash_public_sector_pensions.amount_meur<br>fpb.economic_outlook_2026_2031.cy2029.social_benefits_detail.communities_and_regions_cash_public_sector_pensions.amount_meur<br>fpb.economic_outlook_2026_2031.cy2029.social_benefits_detail.local_governments_cash_public_sector_pensions.amount_meur | fpb.economic_outlook_2026_2031.cy2025.social_benefits_detail.social_security_cash_pensions_total.amount_meur<br>fpb.economic_outlook_2026_2031.cy2025.social_benefits_detail.federal_government_cash_public_sector_pensions.amount_meur<br>fpb.economic_outlook_2026_2031.cy2025.social_benefits_detail.communities_and_regions_cash_public_sector_pensions.amount_meur<br>fpb.economic_outlook_2026_2031.cy2025.social_benefits_detail.local_governments_cash_public_sector_pensions.amount_meur |
| replacement_income | 2030 | 2029 | 4.654 | 6.510 | 0.7149001536098311 | fpb.economic_outlook_2026_2031.cy2029.social_benefits_detail.social_security_cash_unemployment_total.amount_meur | fpb.economic_outlook_2026_2031.cy2025.social_benefits_detail.social_security_cash_unemployment_total.amount_meur |
| movable | 2030 | 2029 | 46.059 | 40.219 | 1.1452050026107063 | fpb.economic_outlook_2026_2031.cy2029.household_account.interest_received.amount_meur<br>fpb.economic_outlook_2026_2031.cy2029.household_account.distributed_income_of_corporations.amount_meur | fpb.economic_outlook_2026_2031.cy2025.household_account.interest_received.amount_meur<br>fpb.economic_outlook_2026_2031.cy2025.household_account.distributed_income_of_corporations.amount_meur |
| wages | 2031 | 2030 | 374.332 | 320.578 | 1.1676783809244553 | fpb.economic_outlook_2026_2031.cy2030.household_account.compensation_of_employees.amount_meur | fpb.economic_outlook_2026_2031.cy2025.household_account.compensation_of_employees.amount_meur |
| self_employment | 2031 | 2030 | 46.512 | 39.834 | 1.1676457297785812 | fpb.economic_outlook_2026_2031.cy2030.household_account.net_mixed_income.amount_meur | fpb.economic_outlook_2026_2031.cy2025.household_account.net_mixed_income.amount_meur |
| pensions | 2031 | 2030 | 85.643 | 71.195 | 1.202935599410071 | fpb.economic_outlook_2026_2031.cy2030.social_benefits_detail.social_security_cash_pensions_total.amount_meur<br>fpb.economic_outlook_2026_2031.cy2030.social_benefits_detail.federal_government_cash_public_sector_pensions.amount_meur<br>fpb.economic_outlook_2026_2031.cy2030.social_benefits_detail.communities_and_regions_cash_public_sector_pensions.amount_meur<br>fpb.economic_outlook_2026_2031.cy2030.social_benefits_detail.local_governments_cash_public_sector_pensions.amount_meur | fpb.economic_outlook_2026_2031.cy2025.social_benefits_detail.social_security_cash_pensions_total.amount_meur<br>fpb.economic_outlook_2026_2031.cy2025.social_benefits_detail.federal_government_cash_public_sector_pensions.amount_meur<br>fpb.economic_outlook_2026_2031.cy2025.social_benefits_detail.communities_and_regions_cash_public_sector_pensions.amount_meur<br>fpb.economic_outlook_2026_2031.cy2025.social_benefits_detail.local_governments_cash_public_sector_pensions.amount_meur |
| replacement_income | 2031 | 2030 | 4.724 | 6.510 | 0.7256528417818741 | fpb.economic_outlook_2026_2031.cy2030.social_benefits_detail.social_security_cash_unemployment_total.amount_meur | fpb.economic_outlook_2026_2031.cy2025.social_benefits_detail.social_security_cash_unemployment_total.amount_meur |
| movable | 2031 | 2030 | 47.624 | 40.219 | 1.1841169596459384 | fpb.economic_outlook_2026_2031.cy2030.household_account.interest_received.amount_meur<br>fpb.economic_outlook_2026_2031.cy2030.household_account.distributed_income_of_corporations.amount_meur | fpb.economic_outlook_2026_2031.cy2025.household_account.interest_received.amount_meur<br>fpb.economic_outlook_2026_2031.cy2025.household_account.distributed_income_of_corporations.amount_meur |

## Weighted factor identity and concepts left unaged

| Factor-authorized concept | Weighted 2025 engine-input mass, EUR |
|---|---|
| movable | 40,192,773,512.31 |
| pensions | 71,253,167,784.72 |
| replacement_income | 6,530,966,888.53 |
| self_employment | 43,335,047,098.34 |
| wages | 177,300,619,638.37 |

The factor-scaled input identity (not an engine score):

| AY | Weighted factor mean | Observed aggregate growth | Residual | Result |
|---|---|---|---|---|
| 2027 | 1.0273333738883608 | 1.0273333738883608 | 0.0 | PASS |
| 2028 | 1.067209295805772 | 1.067209295805772 | 0.0 | PASS |
| 2029 | 1.1006238337938357 | 1.1006238337938357 | 0.0 | PASS |
| 2030 | 1.1329016472783673 | 1.1329016472783673 | 0.0 | PASS |
| 2031 | 1.1685189624559906 | 1.1685189624559906 | 0.0 | PASS |

The unaged-share denominator is EUR 354,127,790,870.29: weighted sum of all positive resources and benefits in the V05C disposable-income identity.

| Concept | Role | Weighted 2025 amount, EUR | Share | Treatment |
|---|---|---|---|---|
| birth_allowance | positive_benefit | 57,038,751.91 | 0.016107% | factor 1.0; never substitute a proxy |
| flemish_jobbonus | positive_benefit | 564,440,403.65 | 0.159389% | factor 1.0; never substitute a proxy |
| pension_contribution | deduction | 2,185,918,764.34 | 0.617268% | factor 1.0; never substitute a proxy |
| self_employed_social_contribution | deduction | 7,148,006,157.51 | 2.018482% | factor 1.0; never substitute a proxy |
| special_social_security_contribution | deduction | 1,420,039,053.20 | 0.400996% | factor 1.0; never substitute a proxy |

## Statbel national-CPI source and levels

Statbel source page: https://statbel.fgov.be/fr/themes/prix-la-consommation/indice-des-prix-la-consommation

Direct workbook: https://statbel.fgov.be/sites/default/files/files/documents/Consumptieprijzen/3.1%20Consumptieprijsindex/Historiek-1920-conv-2025.xls

Downloaded on `2026-08-26`. Workbook SHA-256 `826095f381e9ced8e8f7b7935e63d755d8e7d10eff27b43a70acfaab807453d6`; saved source-page SHA-256 `18857db55918edfe399d4a7d228c87e9683ea43233b0699ebd3b85bdc000521f`.

The workbook's `general index` annual averages are used on the single `2013=100` base. The `health index` is disclosed but rejected as a proxy for Article 178. The incomplete 2026 workbook year is rejected; 2026–2029 are explicit `PROJECTED` extensions from the complete 2025 Statbel level using the declared FPB national-CPI facts.

| Year | Raw/path value | Article 178 R2 level | Classification | Growth % | Authority / record ID |
|---|---|---|---|---|---|
| 1988 | 57.8725 | 57.93 | ACTUAL_CONVERTED_ADMINISTRATIVE_REFERENCE | — | Statbel GLOBAL coefficients with Article 178 administrative rounding; legacy values cross-checked by SPF Finances |
| 1991 | 63.71333333333334 | 63.70 | ACTUAL_CONVERTED_ADMINISTRATIVE_REFERENCE | — | Statbel GLOBAL coefficients with Article 178 administrative rounding; legacy values cross-checked by SPF Finances |
| 1997 | 72.2575 | 72.25 | ACTUAL_CONVERTED_ADMINISTRATIVE_REFERENCE | — | Statbel GLOBAL coefficients with Article 178 administrative rounding; legacy values cross-checked by SPF Finances |
| 2012 | 98.89833333333335 | 98.90 | ACTUAL | — | Statbel general-index annual-average row |
| 2016 | 102.89416666666665 | 102.89 | ACTUAL | — | Statbel general-index annual-average row |
| 2018 | 107.23916666666668 | 107.24 | ACTUAL | — | Statbel general-index annual-average row |
| 2022 | 123.03416666666665 | 123.03 | ACTUAL | — | Statbel general-index annual-average row |
| 2024 | 132.04 | 132.04 | ACTUAL | — | Statbel general-index annual-average row |
| 2025 | 135.2975 | 135.30 | ACTUAL | — | Statbel general-index annual-average row |
| 2026 | 139.8976150 | 139.90 | PROJECTED | 3.4 | fpb.economic_outlook_2026_2031.cy2026.key_figures.price_indices.national_consumer_price_index.growth_rate_percent |
| 2027 | 143.9546458350 | 143.95 | PROJECTED | 2.9 | fpb.economic_outlook_2026_2031.cy2027.key_figures.price_indices.national_consumer_price_index.growth_rate_percent |
| 2028 | 147.2656026892050 | 147.27 | PROJECTED | 2.3 | fpb.economic_outlook_2026_2031.cy2028.key_figures.price_indices.national_consumer_price_index.growth_rate_percent |
| 2029 | 149.9163835376106900 | 149.92 | PROJECTED | 1.8 | fpb.economic_outlook_2026_2031.cy2029.key_figures.price_indices.national_consumer_price_index.growth_rate_percent |

## Article 178 mechanism and all 30 coefficients

Consolidated CIR 1992 Article 178 records: `a0b3a99f-a0a1-5d3c-ac44-46133279f5f5` (be/statute/fisconetplus/cir92/revenus-2025/page-278); `f4cf99cf-de7a-55d5-a604-6e770c2cce38` (be/statute/fisconetplus/cir92/revenus-2025/page-279); `8e37f150-a3dd-5396-9fef-a4a23abac4b9` (be/statute/fisconetplus/cir92/revenus-2025/page-280).

Legal operation order:
1. obtain the applicable annual-average national-CPI level.
2. round each applicable annual average half-up to 0.01 index point (R2).
3. form the encoded ratio, including statutory denominator corrections.
4. round the coefficient half-up to 0.0001 (R4).
5. multiply the statutory base amount by the R4 coefficient.
6. round money as prescribed: normally nearest EUR 10; Article 147 to cents.

Encoded family formulas and rounding:

| Family | Formula | Provision | Money rounding |
|---|---|---|---|
| general | R4(R2(I_(N-2)) / R2(I_1988)) | CIR 1992 Article 178 § 2 | ROUND_HALF_UP to nearest EUR 10 |
| article_289ter_1_default | R4(R2(I_(N-2)) / (R2(I_1988) * (R2(I_1997) / R2(I_1991)))) | CIR 1992 Article 178 § 3, first correction | ROUND_HALF_UP to nearest EUR 10 |
| article_147 | R4(R2(I_(N-2)) / (R2(I_1988) * (R2(I_1997) / R2(I_1991)) * (R2(I_2016) / R2(I_2012)))) | CIR 1992 Article 178 § 3, second correction | ROUND_HALF_UP to EUR 0.01 |
| article_21_tax_expenditure | R4(R2(I_(N-2)) / (R2(I_1988) * (R2(I_1997) / R2(I_1991)) * (R2(I_2016) / R2(I_2012)) * (R2(I_2022) / R2(I_2018)))) | CIR 1992 Article 178 § 3, Article 21 correction | ROUND_HALF_UP to nearest EUR 10 |
| reform_article_132_133 | R4(R2(I_2024) / R2(I_1988))<br>R4(R2(I_(N-2)) / (R2(I_1988) * (R2(I_2028) / R2(I_2024)))) | 15 July 2026 law, Article 104(d)<br>15 July 2026 law, Article 104(d) | ROUND_HALF_UP to nearest EUR 10<br>ROUND_HALF_UP to nearest EUR 10 |
| reform_article_87_88 | R4(R2(I_2024) / (R2(I_1988) * (R2(I_1997) / R2(I_1991)))) | 15 July 2026 law, Article 104(b) | ROUND_HALF_UP to nearest EUR 10 |

Six-family coefficient surface:

| AY | General | Article 289ter/1/default | Article 147 | Article 21 | Reform 132/133 | Reform 87/88 | Result |
|---|---|---|---|---|---|---|---|
| 2027 | 2.3356 | 2.0592 | 1.9793 | 1.7253 | 2.2793 | 2.0096 | PASS |
| 2028 | 2.4150 | 2.1292 | 2.0466 | 1.7840 | 2.2793 | 2.0096 | PASS |
| 2029 | 2.4849 | 2.1908 | 2.1059 | 1.8356 | 2.2793 | 2.0096 | PASS |
| 2030 | 2.5422 | 2.2414 | 2.1544 | 1.8779 | 2.2793 | 2.0096 | PASS |
| 2031 | 2.5880 | 2.2817 | 2.1932 | 1.9117 | 2.3203 | 2.0096 | PASS |

The direct reform Article 131 post-indexation amounts are EUR 14,450 for AY2030 and EUR 15,600 for AY2031; they are not re-indexed a second time.

## Complete active parameter schedule

All 45 active Money slots are present for both policies and all five assessment years: 45 × 2 × 5 = 450 rows. The compact table preserves every engine value and status. `B` means baseline and `R` reform; `RD_PENDING` appears only on the selected Article 147 year/policy cells.

| Pos. | Parameter ID | Label | Kind | Causal status | Family audit | AY2027 B/R | AY2028 B/R | AY2029 B/R | AY2030 B/R | AY2031 B/R |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | be:statutes/income_tax/individual/tax_free_amount#belgium_pit_base_tax_free_amount | Article 131 base tax-free amount | integer | EXERCISED | general_section_2 | B:11180 [INDEXED]<br>R:11550 [INDEXED] | B:11560 [INDEXED]<br>R:12050 [INDEXED] | B:11890 [INDEXED]<br>R:12600 [INDEXED] | B:12160 [INDEXED]<br>R:14450 [DIRECT_POST_INDEXATION_TARGET] | B:12380 [INDEXED]<br>R:15600 [DIRECT_POST_INDEXATION_TARGET] |
| 2 | be:statutes/income_tax/individual/tax_free_amount#belgium_pit_one_child_tax_free_increase | Article 132 child supplements | integer | EXERCISED | baseline general_section_2; reform article_132_133_section_2_1 | B:2030 [INDEXED]<br>R:2130 [INDEXED] | B:2100 [INDEXED]<br>R:2290 [INDEXED] | B:2160 [INDEXED]<br>R:2450 [INDEXED] | B:2210 [INDEXED]<br>R:2650 [INDEXED] | B:2250 [INDEXED]<br>R:2700 [INDEXED] |
| 3 | be:statutes/income_tax/individual/tax_free_amount#belgium_pit_two_children_tax_free_increase | Article 132 child supplements | integer | EXERCISED | baseline general_section_2; reform article_132_133_section_2_1 | B:5230 [INDEXED]<br>R:5130 [INDEXED] | B:5410 [INDEXED]<br>R:5150 [INDEXED] | B:5570 [INDEXED]<br>R:5180 [INDEXED] | B:5690 [INDEXED]<br>R:5300 [INDEXED] | B:5800 [INDEXED]<br>R:5390 [INDEXED] |
| 4 | be:statutes/income_tax/individual/tax_free_amount#belgium_pit_three_children_tax_free_increase | Article 132 child supplements | integer | EXERCISED | baseline general_section_2; reform article_132_133_section_2_1 | B:11720 [INDEXED]<br>R:11440 [INDEXED] | B:12120 [INDEXED]<br>R:11440 [INDEXED] | B:12470 [INDEXED]<br>R:11440 [INDEXED] | B:12760 [INDEXED]<br>R:11440 [INDEXED] | B:12990 [INDEXED]<br>R:11650 [INDEXED] |
| 5 | be:statutes/income_tax/individual/tax_free_amount#belgium_pit_four_children_tax_free_increase | Article 132 child supplements | integer | EXERCISED | baseline general_section_2; reform article_132_133_section_2_1 | B:18970 [INDEXED]<br>R:18510 [INDEXED] | B:19610 [INDEXED]<br>R:18510 [INDEXED] | B:20180 [INDEXED]<br>R:18510 [INDEXED] | B:20640 [INDEXED]<br>R:18510 [INDEXED] | B:21010 [INDEXED]<br>R:18840 [INDEXED] |
| 6 | be:statutes/income_tax/individual/tax_free_amount#belgium_pit_additional_child_after_four_tax_free_increase | Article 132 child supplements | integer | EXERCISED | baseline general_section_2; reform article_132_133_section_2_1 | B:7240 [INDEXED]<br>R:7070 [INDEXED] | B:7490 [INDEXED]<br>R:7070 [INDEXED] | B:7700 [INDEXED]<br>R:7070 [INDEXED] | B:7880 [INDEXED]<br>R:7070 [INDEXED] | B:8020 [INDEXED]<br>R:7190 [INDEXED] |
| 7 | be:statutes/income_tax/individual/tax_free_amount#belgium_pit_child_under_3_tax_free_increase | Article 132 child supplements | integer | EXERCISED | baseline general_section_2; reform article_132_133_section_2_1 | B:760 [INDEXED]<br>R:740 [INDEXED] | B:780 [INDEXED]<br>R:740 [INDEXED] | B:810 [INDEXED]<br>R:740 [INDEXED] | B:830 [INDEXED]<br>R:740 [INDEXED] | B:840 [INDEXED]<br>R:750 [INDEXED] |
| 8 | be:statutes/income_tax/individual/tax_free_amount#belgium_pit_taxpayer_disability_tax_free_increase | Dormant non-child Article 131/132 supplements | integer | DORMANT_BY_POPULATION_ASSIGNMENT | baseline general_section_2; reform article_132_133_section_2_1 | B:2030 [INDEXED]<br>R:1980 [INDEXED] | B:2100 [INDEXED]<br>R:1980 [INDEXED] | B:2160 [INDEXED]<br>R:1980 [INDEXED] | B:2210 [INDEXED]<br>R:1980 [INDEXED] | B:2250 [INDEXED]<br>R:2020 [INDEXED] |
| 9 | be:statutes/income_tax/individual/tax_free_amount#belgium_pit_dependent_elderly_tax_free_increase | Dormant non-child Article 131/132 supplements | integer | DORMANT_BY_POPULATION_ASSIGNMENT | baseline general_section_2; reform article_132_133_section_2_1 | B:6100 [INDEXED]<br>R:5950 [INDEXED] | B:6300 [INDEXED]<br>R:5950 [INDEXED] | B:6490 [INDEXED]<br>R:5950 [INDEXED] | B:6640 [INDEXED]<br>R:5950 [INDEXED] | B:6750 [INDEXED]<br>R:6060 [INDEXED] |
| 10 | be:statutes/income_tax/individual/tax_free_amount#belgium_pit_other_dependent_tax_free_increase | Dormant non-child Article 131/132 supplements | integer | DORMANT_BY_POPULATION_ASSIGNMENT | baseline general_section_2; reform article_132_133_section_2_1 | B:2030 [INDEXED]<br>R:1980 [INDEXED] | B:2100 [INDEXED]<br>R:1980 [INDEXED] | B:2160 [INDEXED]<br>R:1980 [INDEXED] | B:2210 [INDEXED]<br>R:1980 [INDEXED] | B:2250 [INDEXED]<br>R:2020 [INDEXED] |
| 11 | be:statutes/income_tax/individual/article_133_isolated_taxpayer_supplement#belgium_pit_article_133_base_supplement_amount | Article 133 supplement amounts and thresholds | integer | EXERCISED | base/additional supplement: baseline general_section_2 and reform article_132_133_section_2_1; income thresholds: general_section_2 | B:2030 [INDEXED]<br>R:1980 [INDEXED] | B:2100 [INDEXED]<br>R:1980 [INDEXED] | B:2160 [INDEXED]<br>R:1980 [INDEXED] | B:2210 [INDEXED]<br>R:1980 [INDEXED] | B:2250 [INDEXED]<br>R:2020 [INDEXED] |
| 12 | be:statutes/income_tax/individual/article_133_supplements#belgium_pit_article_133_indexed_qualifying_income_amount | Article 133 supplement amounts and thresholds | integer | EXERCISED | base/additional supplement: baseline general_section_2 and reform article_132_133_section_2_1; income thresholds: general_section_2 | B:4200 [INDEXED]<br>R:4200 [INDEXED] | B:4350 [INDEXED]<br>R:4350 [INDEXED] | B:4470 [INDEXED]<br>R:4470 [INDEXED] | B:4580 [INDEXED]<br>R:4580 [INDEXED] | B:4660 [INDEXED]<br>R:4660 [INDEXED] |
| 13 | be:statutes/income_tax/individual/article_133_supplements#belgium_pit_article_133_additional_supplement_full_amount | Article 133 supplement amounts and thresholds | integer | EXERCISED | base/additional supplement: baseline general_section_2 and reform article_132_133_section_2_1; income thresholds: general_section_2 | B:1320 [INDEXED]<br>R:1290 [INDEXED] | B:1360 [INDEXED]<br>R:1290 [INDEXED] | B:1400 [INDEXED]<br>R:1290 [INDEXED] | B:1440 [INDEXED]<br>R:1290 [INDEXED] | B:1460 [INDEXED]<br>R:1310 [INDEXED] |
| 14 | be:statutes/income_tax/individual/article_133_supplements#belgium_pit_article_133_additional_supplement_full_income_ceiling | Article 133 supplement amounts and thresholds | integer | EXERCISED | base/additional supplement: baseline general_section_2 and reform article_132_133_section_2_1; income thresholds: general_section_2 | B:19720 [INDEXED]<br>R:19720 [INDEXED] | B:20390 [INDEXED]<br>R:20390 [INDEXED] | B:20980 [INDEXED]<br>R:20980 [INDEXED] | B:21470 [INDEXED]<br>R:21470 [INDEXED] | B:21860 [INDEXED]<br>R:21860 [INDEXED] |
| 15 | be:statutes/income_tax/individual/article_133_supplements#belgium_pit_article_133_additional_supplement_phaseout_income_ceiling | Article 133 supplement amounts and thresholds | integer | EXERCISED | base/additional supplement: baseline general_section_2 and reform article_132_133_section_2_1; income thresholds: general_section_2 | B:24990 [INDEXED]<br>R:24990 [INDEXED] | B:25840 [INDEXED]<br>R:25840 [INDEXED] | B:26590 [INDEXED]<br>R:26590 [INDEXED] | B:27200 [INDEXED]<br>R:27200 [INDEXED] | B:27690 [INDEXED]<br>R:27690 [INDEXED] |
| 16 | be:statutes/income_tax/individual/dependant_net_resources#belgium_pit_article_136_general_net_resources_ceiling | Articles 136/141/142 dependant-resource amounts | integer | DORMANT_DEPENDANT_RESOURCES_FORCED_ZERO | general_section_2 | B:4200 [INDEXED]<br>R:4200 [INDEXED] | B:4350 [INDEXED]<br>R:4350 [INDEXED] | B:4470 [INDEXED]<br>R:4470 [INDEXED] | B:4580 [INDEXED]<br>R:4580 [INDEXED] | B:4660 [INDEXED]<br>R:4660 [INDEXED] |
| 17 | be:statutes/income_tax/individual/dependant_net_resources#belgium_pit_article_141_separately_taxed_taxpayer_child_net_resources_ceiling | Articles 136/141/142 dependant-resource amounts | integer | DORMANT_DEPENDANT_RESOURCES_FORCED_ZERO | general_section_2 | B:6070 [INDEXED]<br>R:6070 [INDEXED] | B:6280 [INDEXED]<br>R:6280 [INDEXED] | B:6460 [INDEXED]<br>R:6460 [INDEXED] | B:6610 [INDEXED]<br>R:6610 [INDEXED] | B:6730 [INDEXED]<br>R:6730 [INDEXED] |
| 18 | be:statutes/income_tax/individual/dependant_net_resources#belgium_pit_article_141_separately_taxed_taxpayer_disabled_child_net_resources_ceiling | Articles 136/141/142 dependant-resource amounts | integer | DORMANT_DEPENDANT_RESOURCES_FORCED_ZERO | general_section_2 | B:7710 [INDEXED]<br>R:7710 [INDEXED] | B:7970 [INDEXED]<br>R:7970 [INDEXED] | B:8200 [INDEXED]<br>R:8200 [INDEXED] | B:8390 [INDEXED]<br>R:8390 [INDEXED] | B:8540 [INDEXED]<br>R:8540 [INDEXED] |
| 19 | be:statutes/income_tax/individual/dependant_net_resources#belgium_pit_article_142_worker_remuneration_or_profit_minimum_resource_expenses | Articles 136/141/142 dependant-resource amounts | integer | DORMANT_DEPENDANT_RESOURCES_FORCED_ZERO | general_section_2 | B:580 [INDEXED]<br>R:580 [INDEXED] | B:600 [INDEXED]<br>R:600 [INDEXED] | B:620 [INDEXED]<br>R:620 [INDEXED] | B:640 [INDEXED]<br>R:640 [INDEXED] | B:650 [INDEXED]<br>R:650 [INDEXED] |
| 20 | be:statutes/income_tax/individual/tax_free_amount_tax#belgium_pit_article_134_child_tax_credit_cap_per_child | Article 134 refundable-child-credit cap | integer | EXERCISED | general_section_2 | B:580 [INDEXED]<br>R:580 [INDEXED] | B:600 [INDEXED]<br>R:600 [INDEXED] | B:620 [INDEXED]<br>R:620 [INDEXED] | B:640 [INDEXED]<br>R:640 [INDEXED] | B:650 [INDEXED]<br>R:650 [INDEXED] |
| 21 | be:statutes/income_tax/professional_expenses/article_51_forfaits#belgium_pit_article_51_profit_first_threshold | Article 51 profit thresholds | integer | DORMANT_SELFEMP_ACTUAL_EXPENSES_SELECTED | default_section_3 | B:7720 [INDEXED]<br>R:7720 [INDEXED] | B:7980 [INDEXED]<br>R:7980 [INDEXED] | B:8220 [INDEXED]<br>R:8220 [INDEXED] | B:8410 [INDEXED]<br>R:8410 [INDEXED] | B:8560 [INDEXED]<br>R:8560 [INDEXED] |
| 22 | be:statutes/income_tax/professional_expenses/article_51_forfaits#belgium_pit_article_51_profit_second_threshold | Article 51 profit thresholds | integer | DORMANT_SELFEMP_ACTUAL_EXPENSES_SELECTED | default_section_3 | B:15340 [INDEXED]<br>R:15340 [INDEXED] | B:15860 [INDEXED]<br>R:15860 [INDEXED] | B:16320 [INDEXED]<br>R:16320 [INDEXED] | B:16700 [INDEXED]<br>R:16700 [INDEXED] | B:17000 [INDEXED]<br>R:17000 [INDEXED] |
| 23 | be:statutes/income_tax/professional_expenses/article_51_forfaits#belgium_pit_article_51_profit_third_threshold | Article 51 profit thresholds | integer | DORMANT_SELFEMP_ACTUAL_EXPENSES_SELECTED | default_section_3 | B:25530 [INDEXED]<br>R:25530 [INDEXED] | B:26400 [INDEXED]<br>R:26400 [INDEXED] | B:27170 [INDEXED]<br>R:27170 [INDEXED] | B:27790 [INDEXED]<br>R:27790 [INDEXED] | B:28290 [INDEXED]<br>R:28290 [INDEXED] |
| 24 | be:statutes/income_tax/professional_expenses/article_51_forfaits#belgium_pit_article_51_employee_and_business_profit_cap | Article 51 employee cap | integer | EXERCISED | default_section_3 | B:6070 [INDEXED]<br>R:6070 [INDEXED] | B:6280 [INDEXED]<br>R:6280 [INDEXED] | B:6460 [INDEXED]<br>R:6460 [INDEXED] | B:6610 [INDEXED]<br>R:6610 [INDEXED] | B:6730 [INDEXED]<br>R:6730 [INDEXED] |
| 25 | be:statutes/income_tax/professional_expenses/article_51_forfaits#belgium_pit_article_51_assisting_spouse_and_profit_cap | Article 51 assisting-spouse/profit cap | integer | DORMANT_NO_ASSISTING_SPOUSE_INPUT | default_section_3 | B:5340 [INDEXED]<br>R:5340 [INDEXED] | B:5520 [INDEXED]<br>R:5520 [INDEXED] | B:5680 [INDEXED]<br>R:5680 [INDEXED] | B:5810 [INDEXED]<br>R:5810 [INDEXED] | B:5920 [INDEXED]<br>R:5920 [INDEXED] |
| 26 | be:statutes/income_tax/individual/joint_assessment#belgium_pit_article_126_convention_exempt_professional_income_threshold | Article 126 convention threshold | integer | DORMANT_NO_CONVENTION_EXEMPT_INPUT | default_section_3 | B:13800 [INDEXED]<br>R:13800 [INDEXED] | B:14270 [INDEXED]<br>R:14270 [INDEXED] | B:14680 [INDEXED]<br>R:14680 [INDEXED] | B:15020 [INDEXED]<br>R:15020 [INDEXED] | B:15290 [INDEXED]<br>R:15290 [INDEXED] |
| 27 | be:statutes/income_tax/individual/joint_assessment#belgium_pit_article_87_88_spouse_imputation_cap | Articles 87/88 spouse-imputation cap | integer | EXERCISED | baseline default_section_3; reform fixed_article_87_88 | B:13800 [INDEXED]<br>R:11780 [INDEXED] | B:14270 [INDEXED]<br>R:10110 [INDEXED] | B:14680 [INDEXED]<br>R:8420 [INDEXED] | B:15020 [INDEXED]<br>R:6730 [INDEXED] | B:15290 [INDEXED]<br>R:6730 [INDEXED] |
| 28 | be:statutes/income_tax/individual/rate_scale#belgium_pit_article_130_first_bracket_upper_threshold | Article 130 bracket thresholds | integer | EXERCISED | default_section_3 | B:16720 [INDEXED]<br>R:16720 [INDEXED] | B:17290 [INDEXED]<br>R:17290 [INDEXED] | B:17790 [INDEXED]<br>R:17790 [INDEXED] | B:18200 [INDEXED]<br>R:18200 [INDEXED] | B:18530 [INDEXED]<br>R:18530 [INDEXED] |
| 29 | be:statutes/income_tax/individual/rate_scale#belgium_pit_article_130_second_bracket_upper_threshold | Article 130 bracket thresholds | integer | EXERCISED | default_section_3 | B:29510 [INDEXED]<br>R:29510 [INDEXED] | B:30510 [INDEXED]<br>R:30510 [INDEXED] | B:31390 [INDEXED]<br>R:31390 [INDEXED] | B:32120 [INDEXED]<br>R:32120 [INDEXED] | B:32700 [INDEXED]<br>R:32700 [INDEXED] |
| 30 | be:statutes/income_tax/individual/rate_scale#belgium_pit_article_130_third_bracket_upper_threshold | Article 130 bracket thresholds | integer | EXERCISED | default_section_3 | B:51070 [INDEXED]<br>R:51070 [INDEXED] | B:52800 [INDEXED]<br>R:52800 [INDEXED] | B:54330 [INDEXED]<br>R:54330 [INDEXED] | B:55590 [INDEXED]<br>R:55590 [INDEXED] | B:56590 [INDEXED]<br>R:56590 [INDEXED] |
| 31 | be:statutes/income_tax/individual/tax_free_amount_tax#belgium_pit_article_134_first_tax_free_amount_threshold | Article 134 tax-free-amount thresholds | integer | EXERCISED | default_section_3; reform AY2030+ routes to Article 130 ladder | B:11750 [INDEXED]<br>R:11750 [INDEXED] | B:12150 [INDEXED]<br>R:12150 [INDEXED] | B:12500 [INDEXED]<br>R:12500 [INDEXED] | B:12790 [INDEXED]<br>R:18200 [ROUTED_TO_SAME_YEAR_ARTICLE_130_LADDER] | B:13020 [INDEXED]<br>R:18530 [ROUTED_TO_SAME_YEAR_ARTICLE_130_LADDER] |
| 32 | be:statutes/income_tax/individual/tax_free_amount_tax#belgium_pit_article_134_second_tax_free_amount_threshold | Article 134 tax-free-amount thresholds | integer | EXERCISED | default_section_3; reform AY2030+ routes to Article 130 ladder | B:16720 [INDEXED]<br>R:16720 [INDEXED] | B:17290 [INDEXED]<br>R:17290 [INDEXED] | B:17790 [INDEXED]<br>R:17790 [INDEXED] | B:18200 [INDEXED]<br>R:18200 [ROUTED_TO_SAME_YEAR_ARTICLE_130_LADDER] | B:18530 [INDEXED]<br>R:18530 [ROUTED_TO_SAME_YEAR_ARTICLE_130_LADDER] |
| 33 | be:statutes/income_tax/individual/tax_free_amount_tax#belgium_pit_article_134_third_tax_free_amount_threshold | Article 134 tax-free-amount thresholds | integer | EXERCISED | default_section_3; reform AY2030+ routes to Article 130 ladder | B:27860 [INDEXED]<br>R:27860 [INDEXED] | B:28810 [INDEXED]<br>R:28810 [INDEXED] | B:29640 [INDEXED]<br>R:29640 [INDEXED] | B:30330 [INDEXED]<br>R:32120 [ROUTED_TO_SAME_YEAR_ARTICLE_130_LADDER] | B:30870 [INDEXED]<br>R:32700 [ROUTED_TO_SAME_YEAR_ARTICLE_130_LADDER] |
| 34 | be:statutes/income_tax/individual/tax_free_amount_tax#belgium_pit_article_134_fourth_tax_free_amount_threshold | Article 134 tax-free-amount thresholds | integer | EXERCISED | default_section_3; reform AY2030+ routes to Article 130 ladder | B:51070 [INDEXED]<br>R:51070 [INDEXED] | B:52800 [INDEXED]<br>R:52800 [INDEXED] | B:54330 [INDEXED]<br>R:54330 [INDEXED] | B:55590 [INDEXED]<br>R:55590 [ROUTED_TO_SAME_YEAR_ARTICLE_130_LADDER] | B:56590 [INDEXED]<br>R:56590 [ROUTED_TO_SAME_YEAR_ARTICLE_130_LADDER] |
| 35 | be:statutes/income_tax/individual/tax_reductions_and_credits#belgium_pit_article_289ter1_work_bonus_credit_ceiling | Article 289ter/1 fiscal work-bonus ceiling | integer | EXERCISED | default_section_3 | B:1580 [INDEXED]<br>R:2000 [INDEXED] | B:1630 [INDEXED]<br>R:2070 [INDEXED] | B:1680 [INDEXED]<br>R:2130 [INDEXED] | B:1710 [INDEXED]<br>R:2170 [INDEXED] | B:1750 [INDEXED]<br>R:2210 [INDEXED] |
| 36 | be:statutes/income_tax/individual/tax_reductions_and_credits#belgium_pit_article_147_basic_replacement_reduction | Article 147 basic and additional reductions | decimal | EXERCISED | article_147_special, money rounded to cents | B:2274.08 [INDEXED]<br>R:2182.06 [INDEXED] | B:2351.40 [INDEXED]<br>R:2229.77 [INDEXED] | B:2419.53 [INDEXED]<br>R:2237.14 [INDEXED] | B:2475.25 [INDEXED]<br>R:1804.76 [RD_PENDING] | B:2519.83 [INDEXED]<br>R:1837.27 [RD_PENDING] |
| 37 | be:statutes/income_tax/individual/tax_reductions_and_credits#belgium_pit_article_147_additional_replacement_reduction | Article 147 basic and additional reductions | decimal | EXERCISED | article_147_special, money rounded to cents | B:457.23 [RD_PENDING]<br>R:457.23 [RD_PENDING] | B:457.23 [RD_PENDING]<br>R:457.23 [RD_PENDING] | B:457.23 [RD_PENDING]<br>R:457.23 [RD_PENDING] | B:457.23 [RD_PENDING]<br>R:457.23 [RD_PENDING] | B:457.23 [RD_PENDING]<br>R:457.23 [RD_PENDING] |
| 38 | be:statutes/income_tax/individual/tax_reductions_and_credits#belgium_pit_article_147_sickness_invalidity_reduction | Article 147 sickness/invalidity reduction | decimal | DORMANT_SICKNESS_INPUT_ZERO_BUT_REQUIRED_FOR_LITERAL_REPLAY | article_147_special, money rounded to cents | B:3051.47 [INDEXED]<br>R:2959.25 [INDEXED] | B:3155.22 [INDEXED]<br>R:3033.41 [INDEXED] | B:3246.64 [INDEXED]<br>R:3064.04 [INDEXED] | B:3321.42 [INDEXED]<br>R:2650.90 [RD_PENDING] | B:3381.23 [INDEXED]<br>R:2698.64 [RD_PENDING] |
| 39 | be:statutes/income_tax/individual/tax_reductions_and_credits#belgium_pit_article_151_unemployment_phaseout_start | Article 151 unemployment phaseout | integer | EXERCISED | baseline article_147_special; reform default_section_3 from AY2030 | B:29490 [INDEXED]<br>R:29490 [INDEXED] | B:30490 [INDEXED]<br>R:30490 [INDEXED] | B:31380 [INDEXED]<br>R:31380 [INDEXED] | B:32100 [INDEXED]<br>R:33400 [INDEXED] | B:32680 [INDEXED]<br>R:34000 [INDEXED] |
| 40 | be:statutes/income_tax/individual/tax_reductions_and_credits#belgium_pit_article_151_unemployment_phaseout_end | Article 151 unemployment phaseout | integer | EXERCISED | baseline article_147_special; reform default_section_3 from AY2030 | B:36810 [INDEXED]<br>R:36810 [INDEXED] | B:38070 [INDEXED]<br>R:38070 [INDEXED] | B:39170 [INDEXED]<br>R:39170 [INDEXED] | B:40070 [INDEXED]<br>R:41690 [INDEXED] | B:40790 [INDEXED]<br>R:42440 [INDEXED] |
| 41 | be:statutes/income_tax/individual/tax_reductions_and_credits#belgium_pit_article_1511_additional_phaseout_start | Articles 151/1 and 152 phaseouts | integer | EXERCISED | article_147_special | B:20110 [INDEXED]<br>R:20110 [INDEXED] | B:20790 [INDEXED]<br>R:20790 [INDEXED] | B:21400 [INDEXED]<br>R:21400 [INDEXED] | B:21890 [INDEXED]<br>R:21890 [INDEXED] | B:22280 [INDEXED]<br>R:22280 [INDEXED] |
| 42 | be:statutes/income_tax/individual/tax_reductions_and_credits#belgium_pit_article_1511_additional_phaseout_end | Articles 151/1 and 152 phaseouts | integer | EXERCISED | article_147_special | B:29490 [INDEXED]<br>R:29490 [INDEXED] | B:30490 [INDEXED]<br>R:30490 [INDEXED] | B:31380 [INDEXED]<br>R:31380 [INDEXED] | B:32100 [INDEXED]<br>R:32100 [INDEXED] | B:32680 [INDEXED]<br>R:32680 [INDEXED] |
| 43 | be:statutes/income_tax/individual/tax_reductions_and_credits#belgium_pit_article_152_replacement_phaseout_start | Articles 151/1 and 152 phaseouts | integer | EXERCISED | article_147_special | B:29490 [INDEXED]<br>R:29490 [INDEXED] | B:30490 [INDEXED]<br>R:30490 [INDEXED] | B:31380 [INDEXED]<br>R:31380 [INDEXED] | B:32100 [INDEXED]<br>R:32100 [INDEXED] | B:32680 [INDEXED]<br>R:32680 [INDEXED] |
| 44 | be:statutes/income_tax/individual/tax_reductions_and_credits#belgium_pit_article_152_replacement_phaseout_end | Articles 151/1 and 152 phaseouts | integer | EXERCISED | article_147_special | B:58980 [INDEXED]<br>R:58980 [INDEXED] | B:60990 [INDEXED]<br>R:60990 [INDEXED] | B:62760 [INDEXED]<br>R:62760 [INDEXED] | B:64200 [INDEXED]<br>R:64200 [INDEXED] | B:65360 [INDEXED]<br>R:65360 [INDEXED] |
| 45 | be:statutes/income_tax/movable_withholding/rates#belgium_regulated_savings_deposit_interest_exemption_amount | Article 21 regulated-savings exemption | integer | DORMANT_REGULATED_SAVINGS_INPUT_ZERO | article_21_tax_expenditure | B:1080 [INDEXED]<br>R:1080 [INDEXED] | B:1120 [INDEXED]<br>R:1120 [INDEXED] | B:1150 [INDEXED]<br>R:1150 [INDEXED] | B:1170 [INDEXED]<br>R:1170 [INDEXED] | B:1190 [INDEXED]<br>R:1190 [INDEXED] |

## all-factors-1 replay and independent validation

Before aged scoring, all five income factors were set to exactly 1.0. The complete static v05e baseline and AY2027 cells were replayed, not just headline aggregates. This proves transport compatibility; it does not validate the projections or the declared RD assumptions.

`fixed_accounting_bit_exact=true`; static v05e source `1d485d768e53937a31d5942617234365089fc912eafa7e568719595aae0984d0`.

| Cell | Expected hash | Observed hash | Numeric values | Max error | Tolerance | Result |
|---|---|---|---|---|---|---|
| baseline | d0c2e28c352b1d6f124ca03e778a353dd888e699f7f1d8c94531acea35c83fd8 | d0c2e28c352b1d6f124ca03e778a353dd888e699f7f1d8c94531acea35c83fd8 | 322 | 0.0 | 5e-05 | PASS |
| ay2027 | 09bcfd3d666218c8542ba1883b06e75b9ef41169c03363dcfae56cb33f5863f0 | 09bcfd3d666218c8542ba1883b06e75b9ef41169c03363dcfae56cb33f5863f0 | 322 | 0.0 | 5e-05 | PASS |

The independent no-engine v05e-style validator rebuilds all five preflights, verifies the inherited hashes and 30 coefficients, checks all 450 parameter rows, the complete factor-one cells, all five same-year baseline/reform pairs, all 15 worked cases, all nine RD rows, the frozen credit, deterministic result bytes, this report, and the exact stamped lane allowlist. It starts zero Axiom or EUROMOD jobs.

## Pins and artifact hashes

| Artifact | SHA-256 | Bytes |
|---|---|---|
| out/v05h/factor_table.json | 5ed32f7e86962bbdb60ddfa18a53e8a8795d7c13e801fb7566ec2798ff74899c | 152128 |
| out/v05h/statbel_cpi_levels.json | 82e196e1e6dc02db0e43c39874ffb78e595ac61a88cccb584d6f6e141a0dcff7 | 21121 |
| out/v05h/article178_preflight.json | 3b074608d3fdb208789f1385142d84fdddfd9b863e05efb63b5e4766c02225d4 | 57201 |
| out/v05h/parameter_preflight.json | 3aecdb1bddc4cecfb0fedc7f25c6b72bd922c842dbd06490227e0e23c877746c | 464985 |
| out/v05h/accounting_preflight.json | 21ff587e2c26402e5230464645954ab89465964925a082f7002004371a8a4e78 | 9883 |
| out/v05h/aged_results.json | f138697423c77c77af10467dccf253faf10bc9869a0f9844379d31ab5ab88d50 | 786123 |
| out/v05h/generation_manifest.json | 4129afd7dd86799a42aac2e1df27d2fe8b8838f25afdb32da1b8b590a8d327cd | 4329 |

Generation log SHA-256 `d6b73dce85e853610d1ce7b9a161b84625392ec5f73d2629c1460c62398bdfe3`. Unlike the compact data and manifest, the log records elapsed task timings, so its bytes are run evidence rather than a promised cross-run deterministic hash.

Scoring source pins:

| Label | Path | SHA-256 |
|---|---|---|
| accounting_preflight | out/v05h/accounting_preflight.json | 21ff587e2c26402e5230464645954ab89465964925a082f7002004371a8a4e78 |
| aged_generator_source | out/v05h/generator/generate.py | 55101be4237ea499d7acf2db301c077f61521d3c18d2103d17740ec310e61eaa |
| aged_model_source | out/v05h/generator/aged_model.py | 783a8cfcddfe82f0a90fd509e58ffca0698ed63daedcdea211cb167cab7001de |
| article178_preflight | out/v05h/article178_preflight.json | 3b074608d3fdb208789f1385142d84fdddfd9b863e05efb63b5e4766c02225d4 |
| factor_table | out/v05h/factor_table.json | 5ed32f7e86962bbdb60ddfa18a53e8a8795d7c13e801fb7566ec2798ff74899c |
| parameter_preflight | out/v05h/parameter_preflight.json | 3aecdb1bddc4cecfb0fedc7f25c6b72bd922c842dbd06490227e0e23c877746c |
| population_hdf | out/v05/microcosm_be_v05_2025.h5 | 82c0b3cea8843130b3fe77bb435b658ff55c5a2b4398875e22b7d37db67655bd |
| population_weights | out/v05/microcosm_be_v05_2025_weights.npz | 8a8bf654036d66d03a142fb0ab4c02f4c10b574aa222e57f270822f893cf4693 |
| statbel_cpi_levels | out/v05h/statbel_cpi_levels.json | 82e196e1e6dc02db0e43c39874ffb78e595ac61a88cccb584d6f6e141a0dcff7 |
| static_v05e_catalog | out/v05e/generator/reform_bundles.json | 794b0e5f72e806edd8d23a30e9773fb5efa99be528087701ec5eb4d416fe3f84 |
| static_v05e_results | out/v05e/reform_results.json | 1d485d768e53937a31d5942617234365089fc912eafa7e568719595aae0984d0 |
| v05a_component_outputs | out/v05a/microcosm_be_v05_axiom_component_outputs.npz | 8d7e7c9434f371914fe63875a740d0106669ea4533c2c6e65ceff4076ba495d8 |
| v05a_component_results | out/v05a/microcosm_be_v05_axiom_component_results.json | 9a888558ccfc3ae0fc149ec21971b8d263ee5a7a120250ad393f3d0fcfde4721 |

Axiom engine commit `c6cc389a8f5e7238019e4fa06849325fad9acd46`; engine SHA-256 `9452599c5ef641a30ded4ab65ced19cdfc054a667582b62ad33577a8ad787a1f`; RuleSpec-BE commit `ddc28fe7fba3509019a2b80ada5fb6f3ee922839`.

## Reproduction and release checks

Run from the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python out/v05h/generator/statbel_cpi.py
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python out/v05h/generator/article178_preflight.py
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python out/v05h/generator/factors.py
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python out/v05h/generator/parameter_preflight.py
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python out/v05h/generator/accounting_preflight.py
set -o pipefail; PYTHONDONTWRITEBYTECODE=1 .venv/bin/python out/v05h/generator/generate.py 2>&1 | tee out/v05h/generation.log
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python out/v05h/generator/render_report.py
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -p no:cacheprovider -q out/v05h/generator
ruff check out/v05h/generator
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python out/v05h/generator/validate.py
sha256sum out/v05h/*.json out/v05h/*.log LANE_AGED3_REPORT.md
```

The full generation run starts Axiom scoring jobs. The validator itself is no-engine and starts none. No EUROMOD command belongs in this lane.

## Local coherent-step commit ledger

| Commit | Step |
|---|---|
| 563cf35 | Inherited AGED2 Article 178 resolution and 30 coefficients. |
| 6afcc6b | AGED3 establish progress ledger |
| 8f1bbf1 | AGED3 authorize declared parameter schedule |
| 341994b | AGED3 add absolute aged model adapter |
| 548f152 | AGED3 record aged model completion |
| af5907f | AGED3 add deterministic same-year scorer |
| c6513fe | AGED3 route worker aging through writable transport |
| 744505a | AGED3 record factor-one curve smoke |
| 7fb727c | AGED3 record five-year aged score |
| 356fc37 | AGED3 add independent terminal validator |
| b238b77 | AGED3 harden validator emission lifecycle |
| 5b9f289 | AGED3 add deterministic terminal report renderer |

The report and final validation-artifact commits necessarily follow this rendered ledger; no push or stash operation was performed.

## Qualifications

- The Royal-Decree carries are declared forward-exercise assumptions, not claims about future decrees. Their weighted exposure is deliberately visible above.

- RD exposure is an input footprint, not a causal sensitivity or an estimate of revenue at risk. Repeated rows share underlying people and euros.

- The supplied Article 289ter credit is frozen even though self-employment income and indexed thresholds age. Its weighted magnitude is disclosed rather than hidden.

- Population composition, weights, behaviour, and five undeclared-series concepts remain fixed. The output is therefore not a demographic, behavioural, or macroeconomic forecast.

- The result is aggregate synthetic-population evidence. Cross-engine agreement supports the encodings but does not convert the exercise into an administrative forecast or public-release file.

LANE AGED DONE
