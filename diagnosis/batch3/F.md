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

## F3. Iowa and Wisconsin: PE puts too much of the SNAP caseload in BBCE-only units, so too few federally eligible people carry the take-up flag

- **Class:** `pe_gap` (confidence medium); **claims:** 2; **route:** https://github.com/PolicyEngine/microcosm/issues/647

**Evidence**

- Iowa PE 84.9% vs FNS 97.6%; Wisconsin 86.0% vs 100% (capped by FNS; Exhibit A.3 implied 113.5%). Neither State is flag-saturated.
- Eligibility is not the outlier: PE's eligible people are 1.135x (IA) and 1.159x (WI) FNS Table A.18, at the median of the 16 non-saturated States (1.15). Participants are: PE's federal-rules participants are 0.987x and 0.997x Table A.3, against a non-saturated median of 1.14x (sources/fns-snap-rates/pe/us-6.2.1.json).
- PE's as-served participants are 1.296x (IA) and 1.403x (WI) FNS Table A.1, but only 59.8% and 52.9% of them are in federally eligible units; FNS Table A.2 puts 78.54% and 74.49% of participants under federal rules. PE's federal-rules share is below FNS's in 40 of 51 jurisdictions (median 60.3% vs 82.2%).
- In the federal-rules world the take-up flag is on for 84.9% (IA) and 86.0% (WI) of federally eligible people and for 53.0% and 79.4% of BBCE-only eligible people (diagnosis/batch3/probes/snap_take_up_split.py, outputs alongside).
- Mechanism: microcosm snap_state_take_up.py at the Build P commit cae8640 (docstring lines 13-25; unchanged from 8828dee) anchors ASEC reporters, fills non-reporters at one State rate (FNS household caseload over weighted modeled-eligible units, BBCE eligibility included) and calibrates to FNS household caseloads that include BBCE-only households. Nothing separates federal-rules participants, so where the fill rate does not saturate, the federal-rules rate is what the uniform draw leaves.
- The anchor cannot be separated from the draw in the release: spm_unit_snap (the reported ASEC subsidy) is zero for every SPM unit in us-6.2.1 (probe outputs).

**Fix (upstream_issue):** Comment on microcosm#647: the State take-up fill spreads draws uniformly over BBCE-expanded eligibility, so PE's BBCE-only share of participants (median 39.7%) is about twice FNS Table A.2's share outside federal rules (17.8%, which also counts erroneous payments); weight the fill toward federal-rules eligibility, or add the A.2 federal-rules share as a target or diagnostic.
