# SPM level differences vs ASEC-anchored series — what is in hand

Date: 2026-08-02. Register: descriptive (methodological_difference; issue #9
ruling — Scorecard is descriptive by default).

## The difference

Populace calculates benefits and recalibrates where CPS-ASEC carries
survey-reported attributes; SPM level series therefore differ from
ASEC-anchored series (CPSP, Census SPM).

Measured at 2024 on the certified populace_us bundle:
- PE child SPM (unforced year-grid baseline): **16.97%**
- Census-published 2024 child SPM: **13.4%** (CPSP TCJA-world: 13.3%)
- Forcing credit take-up/filing (takes_up_eitc + would_file_*) accounts for
  only **~0.2pp** of the difference (16.97% → ~16.7% forced).

## Named remaining channels (undecomposed)

1. **Calculated vs reported benefits** — PE computes program amounts
   (calibrated take-up) where ASEC carries survey reports. Known-issue
   component: early_head_start at engine-default 100% take-up flows inside
   household_net_income (populace#593; pe_gap citable for these rows).
2. **Recalibration** — populace reweighting/sparsification vs ASEC weights.
3. **Threshold treatment** — the certified environment runs spm-calculator
   0.3.1 (the version policyengine-us#9081 flags). Verified 2026-08-02 from
   the spm-calculator PR#32 branch data (BLS corrected workbook sha256
   e7931a1f…): at sim-year 2024 the installed values EXACTLY equal the
   pre-correction published series (renter 39,430 / owner+m 39,068 /
   owner−m 32,586), so the 2019-2023 hand-entry errors (≤8%) do not affect
   anything computed this session; only the BLS 2026-07-17 correction
   applies at 2024 (−0.53% / +0.42% / +0.90% by tenure — small).

## Decomposition home

Channel decomposition (and an SPM calculation tool) is **Max's own pending
project** — the policyengine-spm-decomposition repo. Not built in the
compute-campaign lane (stood down 8/2 per redirect; a queued threshold-swap
sim was cancelled before running). This file + the methodological_difference
registry entry are the campaign's complete record.
