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

## E2. Connecticut: PE EITC participation 15 points below IRS

- **Class:** `open` (confidence low); **claims:** 1

**Evidence**

- Connecticut PE 67.3% vs IRS 82.0%; 32.7% of PE's eligible units have the take-up flag off against 12.0% nationally, so calibration to Connecticut's SOI claims put more weight on flag-off units there. The cause is not identified.
