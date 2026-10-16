# Batch 3, cluster E: IRS/Census EITC participation rates

Lane `nta-eitc`, source `irs_eitc_participation`. Generated from `E.json` (the ingested record); evidence cites the files and releases named in each bullet.

## E1. PE EITC participation runs high because PE has no EITC non-filers

- **Class:** `pe_gap` (confidence medium); **claims:** 17; **route:** https://github.com/PolicyEngine/microcosm/issues/1133

**Evidence**

- sources/irs-eitc-participation/pe/us-6.2.1.json: would_file_if_eligible_for_refundable_credit = 1.0 for every tax unit; entitled_flag_on_not_paid = 0, so every PE non-participant has takes_up_eitc off.
- CES-WP-24-75 Table 2: 4.6 million of 5.7 million eligible non-claimants in TY2021 were non-filers.
- PE is above IRS in 39 of 51 jurisdictions; 15 States are 10+ points above (PE 87.6-100% vs IRS 73.6-82.8%). National: PE 88.0% vs 80.8% (ACS) and 78% (CPS).
- Minnesota reaches 100% (13 weighted units with the flag off): calibration to SOI TY2022 State claims by children (us-6.2.1 targets) fills the eligible pool, the SNAP saturation pattern.

**Fix (upstream_issue):** microcosm#1133: seed would_file_if_eligible_for_refundable_credit from a non-filer propensity; then re-run this lane.

## E2. Connecticut: PE EITC participation 15 points below IRS; the flag-off mass rests on few records that the weight solve does not down-weight

- **Class:** `open` (confidence medium); **claims:** 1

**Evidence**

- Connecticut PE 67.3% vs IRS 82.0%. PE's Connecticut claims hit the SOI target (201,016 vs 200,860, calibration_diagnostics.json irs_soi.ty2022.historic_table_2.state_eitc.ct.ct.eitc_claims), so the gap is the eligible pool: 298,638 entitled units, of which 97,623 (32.7%) have the take-up flag off against 12.0% nationally.
- By qualifying children, Connecticut's flag-off shares are 45.7% (none), 12.4% (one), 43.1% (two) and 0.0% (three or more), against 26.1%, 4.4%, 5.3% and 5.3% nationally. Its flag-off share among units with children (24.3%) is the highest of the 51 jurisdictions (next NH 16.7%; median 4.6%) (diagnosis/batch3/probes/eitc_ssi_split.json).
- Connecticut's entitled pool rests on 138 tax-unit records; 39 (28.3%) have the flag off against 20.1% of records nationally, and two-child units have 13 flag-off records of 34 (national 15.3%) (diagnosis/batch3/probes/eitc_records.json).
- Nationally, flag-off records carry about half the weight of flag-on records (mean 1,425 vs 2,633); in Connecticut they carry more (2,503 vs 2,030). No target ties eligibility or the flag-off mass, so the State's other targets set those weights.
- No microcosm issue covers State-level take-up-flag mass yet, so the item stays open.
