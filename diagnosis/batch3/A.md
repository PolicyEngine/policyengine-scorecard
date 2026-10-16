# Batch 3, cluster A: ASPE Welfare Indicators, Indicator 4

Lane `aspe-welfare-indicators`, source `aspe_welfare_indicators`. Generated from `A.json` (the ingested record); evidence cites the files and releases named in each bullet.

## A1. TANF rate: the 21.9% seed becomes 41.2% after calibration to ACF dollar targets

- **Class:** `pe_gap` (confidence high); **claims:** 1; **route:** https://github.com/PolicyEngine/microcosm/issues/643

**Evidence**

- microcosm us/spec/take_up.yaml: takes_up_tanf_if_eligible seeded at 0.219 from the 24th report's Table 10 (this series).
- sources/aspe-welfare-indicators/pe/us-6.2.1.json: the flag is on for 23.8% of PE's eligible units (unweighted); the weighted rate is 41.2% (911k of 2.21M SPM units, any time in 2024) against ASPE's 22.1% (0.857M of 3.870M families, 2023).
- us-6.2.1 calibration_diagnostics.json: 23 hhs_acf_tanf.fy2024.cash_assistance targets (national and 22 States); the national target is missed by 36.1%.
- PE's eligible units (2.21M, any time in the year) are well below TRIM3's average-month 3.87M families, so eligibility is low as well (microcosm#643's 'payable eligibility' finding).

**Fix (upstream_issue):** Comment on microcosm#643 with the measured seed-to-weighted drift and the TRIM3 eligible comparison.

## A2. SSI: PE's payable eligibility is low for aged and disabled individuals, so rates run high

- **Class:** `pe_gap` (confidence high); **claims:** 5; **route:** https://github.com/PolicyEngine/microcosm/issues/644

**Evidence**

- sources/aspe-welfare-indicators/pe/us-6.2.1.json against ASPE Table 12 (2023): aged individuals eligible 2.88M vs 4.2M (-31.5%), participating 1.73M vs 2.1M, rate 60.0% vs 49.9%; disabled individuals eligible 5.12M vs 6.3M (-18.7%), participating 3.80M vs 3.9M, rate 74.2% vs 62.1%.
- PE's SSI recipients are calibrated to SSA counts (relationships.py _SSA), so participants sit near the admin level and the eligible shortfall shows up as high rates.
- Same finding as batch 1's SSI item (microcosm#644: payable eligibility low and misallocated within adult age bands), now against TRIM3 instead of ATTIS.

**Fix (upstream_issue):** Comment on microcosm#644 with the TRIM3 comparison by unit type.

## A3. SSI couples: take-up is drawn per person at age-band priors with no couple dimension, so PE couples participate at the band rate, twice TRIM3's

- **Class:** `pe_gap` (confidence medium); **claims:** 2; **route:** https://github.com/PolicyEngine/microcosm/issues/1212

**Evidence**

- PE 0.42M participating couple units (joint claims, persons / 2) vs TRIM3 0.2M (+108%), with equal eligible units (1.00M vs 1.0M), so the rate is 41.9% vs 22.7%.
- Average month 2024: 1,991,297 adults in joint claims have a payment due and 833,976 are paid (41.9%); aged individuals 59.9%, disabled individuals 74.2% (diagnosis/batch3/probes/eitc_ssi_split.py, eitc_ssi_split.json).
- microcosm ssi_take_up.py at the Build P commit cae8640: each person draws once against an age-band prior (_stable_source_draw, lines 494-503; selection, line 1076); the priors are set so band totals hit SSA December 2024 person counts (_band_prior, lines 669-702). Neither the prior nor any target distinguishes couples from individuals.
- Build P's us_ssi_take_up.json (populace-us-2024-buildp-sparse-rmloss100-cae8640-20260728T011454Z, sha256 ce631a37e2fe...): non-anchor priors 38.5% (18-64) and 43.3% (65+); PE's couple rate sits at those priors, while TRIM3 has couples participating at 22.7%.
- microcosm#1212: in the certified frame (Build P plus one SPM column) people 65+ are 81.2% married against ACS 56.2%, and 9.1% live alone against 26.6%; the support selection and the weight solve both favor couples. With person-count band targets, the recipients the frame moves into couples keep the band take-up rate.
- ssi_reported is zero for every person in us-6.2.1, so the release cannot separate reporter anchors from draws (probe output).

**Fix (upstream_issue):** Comment on microcosm#1212: the SSI take-up stage draws per person at age-band priors, so the frame's excess couples participate at the band rate; PE has 0.42M participating SSI couples against TRIM3's 0.2M. A household-composition target (#1212's proposal) lowers the couple mass; a couple dimension in the prior (or one draw per eligible couple) would match the couple rate.

## A4. SNAP households: PE SPM units are fewer and larger than FNS SNAP households

- **Class:** `concept_mismatch` (confidence high); **claims:** 2

**Evidence**

- PE 14.0M federally eligible SPM units vs FNS 19.4M eligible households (FY 2022, ASPE Table 11); rate 96.5% vs 91.6%.
- SNAP households average 1.9 people (FY 2023 QC Table B.2) while PE's participating SPM units average 2.7: a unit-definition difference, already annotated on these results (aspe-snap-federal-households).
