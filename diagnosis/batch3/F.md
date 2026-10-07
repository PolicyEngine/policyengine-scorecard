# Batch 3, cluster F: FNS State SNAP participation rates

Lane `fns-snap-rates`, source `fns_snap_rates`. Generated from `F.json` (the ingested record); evidence cites the files and releases named in each bullet.

## F1. SNAP State rates of 96-100% are saturation, not take-up: every federally eligible unit carries the take-up flag

- **Class:** `pe_gap` (confidence high); **claims:** 17; **route:** https://github.com/PolicyEngine/microcosm/issues/647

**Evidence**

- sources/fns-snap-rates/pe/us-6.2.1.json: takeup_flag_share = 1 (every federally eligible person's SPM unit has takes_up_snap_if_eligible) in 30 States; 14 of the 16 far-apart State rates are in those States, with PE at 98.5-100% against FNS 58.9-89.9%.
- Alaska (+27.0 points) and South Dakota (+15.9) are not flag-saturated but carry the household-to-person bridge of batch 1's Alaska item: PE's federal-rules participants are 2.03x and 1.51x FNS's (Table A.3).
- Populace snap_state_take_up.py:186-211 (batch 1 evidence, diagnosis/diagnoses.json): the take-up stage sets every eligible unit to take up when the FNS household target meets or exceeds the eligible weight.
- National: PE 97.0% against FNS 88% (FY 2022, whole percent); the saturated States carry the national gap.

**Fix (upstream_issue):** Comment on microcosm#647 with this independent federal-rules confirmation (30 saturated States on us-6.2.1, measured take-up flag share) and the release gate it suggests: fail a certification when a State's post-calibration flag share among eligible units reaches 1.

## F2. State SNAP eligible-count gaps follow PE's participant scale (person grain), not the eligibility rules

- **Class:** `pe_gap` (confidence medium); **claims:** 10; **route:** https://github.com/PolicyEngine/microcosm/issues/647

**Evidence**

- Across the 51 jurisdictions, PE/FNS eligible people correlates 0.82 with PE/FNS federal-rules participants (sources/fns-snap-rates/pe/us-6.2.1.json against Tables A.18 and A.3). In the 10 far-apart States the two ratios move together: DC 0.59/0.59, ME 0.51/0.55, MT 0.65/0.62, VT 0.66/0.67, NV 1.52/1.54, IN 1.44/1.62.
- PE's SNAP calibration fits households, not people: us-6.2.1 has 104 usda_snap.fy2024.* targets (households and benefits, national and by State) and none for participants or household size (calibration_diagnostics.json).
- FY 2023 SNAP QC Table B.1-B.2 (staged in data/ledger/us_admin_outturns.jsonl): 1.9 people per SNAP household nationally (1.6-2.2 across States); PE has 2.7 people per participating SPM unit, and its as-served participants are a median 1.45x the QC participants by State.
- In DC, 62% of PE's participants are in BBCE-only units, so its federal-rules participants (and eligible people) fall to 0.59x FNS even though all its participants are 1.46x the QC participants.

**Fix (upstream_issue):** Comment on microcosm#647: add SNAP participant (person) targets by State from the QC Table B.1 facts now staged for Chronicle, or calibrate household size, so person counts stop scaling with SPM-unit size.

## F3. Iowa and Wisconsin: PE rates 13-14 points below FNS with matching participants

- **Class:** `open` (confidence low); **claims:** 2

**Evidence**

- Iowa PE 84.9% vs FNS 97.6%; Wisconsin 86.0% vs 100% (capped). PE's federal-rules participants match FNS (0.99x, 1.00x Table A.3) while its eligible people are 1.14x and 1.16x FNS; neither State is saturated.
- Wisconsin is capped at 100% by FNS (Exhibit A.3: implied 113.5%), so FNS's eligible count there is set to participants.
