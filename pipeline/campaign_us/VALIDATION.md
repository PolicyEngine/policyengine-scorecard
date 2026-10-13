# US compute-campaign reconstruction — validation

Reconstruction of the six US families staged in
`sources/campaign-20260802/us/` (112 rows: 108 claim rows + 4 TPC exhibit
rows). The original campaign code is not available; each module in this
directory re-implements its rows from the recipe text the original rows
carry (`pe_construction` + annotations). The code was run twice:

* **Old bundle (reproduction check)** — `.venv-pe501`: policyengine 5.0.1,
  bundle `us-5.0.1` = policyengine-us 1.764.6 + certified data
  `populace-us-2024-buildp-sparse-rmloss100-cae8640-20260728T011454Z`
  (sha256 48b9d479…), the bundle every original row names. Output:
  `pipeline/campaign_us/runs/old-us-5.0.1/`.
* **New bundle** — `.venv-pe`: policyengine 6.2.1, bundle `us-6.2.1` =
  policyengine-us 2.2.1 + certified data `populace-us-2024-spm-20260915`
  (sha256 6496cc43…). Only rows reproduced on the old bundle are staged, to
  `sources/campaign-20261006/us/` (run_ids `campaign-20261006-<suffix>`).

**Result: all 112 rows reproduce on the old bundle with zero difference**
(bit-identical values; every regenerated text — see below — also equals
the original text), so all 112 are staged on the new bundle.

Tolerance: reproduced = |relative diff| <= 0.1% (counts, dollars), or
|absolute diff| <= 1e-4 for rates. Every run's raw job values, applied
reform dicts (read back from the simulation's parameter tree) and timings
are in `pipeline/campaign_us/runs/<family>__<bundle_id>.json`.

## Environment note (old bundle)

`uv pip install "policyengine[us]==5.0.1"` resolves `spm-calculator`
1.0.0.post1 (released 2026-09-14), which no longer ships
`spm_calculator.geoadj`; policyengine-us 1.764.6 imports it and fails to
load. The env pins `spm-calculator==0.3.1`, the latest release at the time
of the original campaign (2026-04-17; policyengine-us 1.764.6 requires
`>=0.2.0`).

## Construction decisions (all stated in the module docstrings)

* **cbo_free_joins** — the SSI "year-grid part_pop" is adults 18+ with
  `ssi > 0` (the year-grid counterpart runner's Urban SSI universe,
  `pipeline/compute_counterparts.py`); the all-ages count (6,288,302 on the
  old bundle) does not reproduce the original 6,108,392.
* **pwbm_ss_elimination / tpc** — each (world, year) is computed in its own
  fresh simulation. In policyengine-us 1.764.6 a simulation that has
  already computed CY2025 returns a different CY2026 `income_tax`
  (baseline: 2,605,788,866,110 vs 2,605,685,778,045 fresh, 4.0e-5);
  computing both years in one simulation reproduced the PWBM CY2026 row
  only to 1.1e-5. Separate simulations reproduce it exactly, matching the
  original rows' separate computed_at stamps.
* **cpsp_ctc_2024** — "credit take-up/filing flags forced" =
  `takes_up_eitc` and `would_file_if_eligible_for_refundable_credit` set
  True for 2024; the ARPA-style worlds also set
  `phase_out.arpa.in_effect = True` (the ARPA addition does not exist
  without it); OBBBA phase-out thresholds = 2024 value x 0.97154.
* **urban_subgroup_counts** — SSI eligibility is the person's own
  `is_ssi_eligible` (all ages); the unit reading overstates by 9-98%.
  Earners = `tax_unit_earned_income > 0`. Race5 = `is_hispanic` first, then
  `cps_race` 1 / 2 / {4,5} / other.
* **jct_obbba_provision4** — expiry world minus current law, negated.

## Parameter paths on policyengine-us 2.2.1

No mapping was needed. All 85 (parameter path, start instant) pairs the
reforms touch resolve in both engines, with identical current-law values
at those instants (checked with `policyengine_core.parameters.get_parameter`
in both envs); each run also reads every reformed parameter back from the
simulation and fails if a value did not apply. The one engine rename that
touches these families is an input, not a parameter: policyengine 6.2.1
maps the stored `would_claim_wic` onto `takes_up_wic_if_eligible`
(recorded as `legacy_input_renames` in the bundle provenance).

## Text regenerated from the run (old-bundle numbers in the originals)

`pe_construction` is carried verbatim except where it quotes a PE number,
and annotations are carried verbatim except those that quote a PE number:

* jct_obbba_provision4 construction: "The 1.87 ratio vs JCT's stack
  position" -> recomputed PE / JCT (JCX-35-25 FY2026 = -$48,769M).
* tpc exhibit constructions: "PE +1.67B" etc. -> recomputed (the TPC twin
  is verbatim).
* tpc CTC annotations "CY2025 variant: X" and the AFA annotation
  "floor-construction bound: bill-text $2,000 floor gives X (width Y)" ->
  recomputed from CY2025 / $2,000-floor simulations.

On the old bundle every regenerated text equals the original text. On the
new bundle two texts change: the ctc2-ctc1 exhibit ("PE -2.99B" -> "PE
-2.98B") and the AFA floor bound ("-130.7B" -> "-130.6B"). The JCT ratio
(1.87) and the three CY2025 variants (-12.3B / -15.1B / -17.6B) are the
same at their printed precision. Staged rows otherwise equal the originals
in every field except pe_value, engine_version, data_bundle, computed_at
and run_id (key order preserved).

## New-bundle run notes

* Runs (2026-10-06, EDT): cbo_free_joins, pwbm_ss_elimination and
  jct_obbba_provision4 at 12:04–12:22. The first cpsp_ctc_2024 attempt ran
  under memory pressure from a concurrent job (one simulation took 31 min)
  and its process was killed before it wrote anything; cpsp_ctc_2024,
  urban_subgroup_counts and tpc_t25_0209_t26_0029 were rerun at
  13:58–15:06. Peak RSS per simulation: ~40 GB (CY2026 tax runs) to ~84 GB
  (CPSP CY2024 poverty runs).
* Independent cross-check: where the construction is the same, the new
  urban rows equal the other session's `platform-grid-2024` results on the
  same bundle bit for bit (SNAP eligibility by subgroup, WIC eligibility
  and WIC eligible-minus-participants; e.g. WIC age_0thr3 = 7,017,855.898).
* Largest moves: SNAP (CY2026 total +10.3%, participants +6.5%, average
  benefit +3.5%; CY2024 eligibility by subgroup +0.9% to +16.8%) and CPSP
  child SPM poverty (-0.4 to -1.2 pp in every world; TCJA world under-18
  16.77% -> 15.61%). SSI, TANF-demographic and housing eligibility counts
  are unchanged; revenue rows move by at most 0.24%.

## Rerun

```
uv venv .venv-pe501 --python 3.12
uv pip install --python .venv-pe501/bin/python "policyengine[us]==5.0.1" "spm-calculator==0.3.1"
.venv-pe501/bin/python pipeline/campaign_us/run.py all --out pipeline/campaign_us/runs/old-us-5.0.1
.venv-pe/bin/python pipeline/campaign_us/run.py all --out sources/campaign-20261006/us \
    --require-reproduced pipeline/campaign_us/runs/old-us-5.0.1
.venv-pe/bin/python pipeline/campaign_us/validate.py --old pipeline/campaign_us/runs/old-us-5.0.1 \
    --new sources/campaign-20261006/us --md pipeline/campaign_us/VALIDATION.md
```

## Summary

| family | rows reproduced / total | max abs rel diff (old) | rows staged (new) | old bundle run | new bundle run |
|---|---|---|---|---|---|
| cbo_free_joins | 9 / 9 | 0.00e+00 | 9 | 1.764.6 / populace-us-2024-buildp-sparse-rmloss100-cae8640-20260728T011454Z (2026-10-06T14:44:44Z) | 2.2.1 / populace-us-2024-spm-20260915 (2026-10-06T16:06:30Z) |
| pwbm_ss_elimination | 2 / 2 | 0.00e+00 | 2 | 1.764.6 / populace-us-2024-buildp-sparse-rmloss100-cae8640-20260728T011454Z (2026-10-06T15:26:54Z) | 2.2.1 / populace-us-2024-spm-20260915 (2026-10-06T16:17:17Z) |
| jct_obbba_provision4 | 1 / 1 | 0.00e+00 | 1 | 1.764.6 / populace-us-2024-buildp-sparse-rmloss100-cae8640-20260728T011454Z (2026-10-06T15:04:43Z) | 2.2.1 / populace-us-2024-spm-20260915 (2026-10-06T16:22:20Z) |
| cpsp_ctc_2024 | 8 / 8 | 0.00e+00 | 8 | 1.764.6 / populace-us-2024-buildp-sparse-rmloss100-cae8640-20260728T011454Z (2026-10-06T15:17:36Z) | 2.2.1 / populace-us-2024-spm-20260915 (2026-10-06T18:16:08Z) |
| urban_subgroup_counts | 78 / 78 | 0.00e+00 | 78 | 1.764.6 / populace-us-2024-buildp-sparse-rmloss100-cae8640-20260728T011454Z (2026-10-06T15:06:51Z) | 2.2.1 / populace-us-2024-spm-20260915 (2026-10-06T18:19:03Z) |
| tpc_t25_0209_t26_0029 | 14 / 14 | 0.00e+00 | 14 | 1.764.6 / populace-us-2024-buildp-sparse-rmloss100-cae8640-20260728T011454Z (2026-10-06T16:03:58Z) | 2.2.1 / populace-us-2024-spm-20260915 (2026-10-06T19:06:34Z) |

## Per row

Original = staged 2026-08-02 value (engine 1.764.6, buildp bundle). Reproduced = this reconstruction on the same old bundle. New = this reconstruction on the new certified bundle (blank when the row did not reproduce and was not staged). "new vs old-reproduced" is (new - old) / old, so for a negative value + means larger in magnitude; rates show the absolute change.

### cbo_free_joins

| # | row | original | reproduced (old) | rel diff | reproduced? | new | new vs old-reproduced |
|---|---|---|---|---|---|---|---|
| 0 | benefit_cost 2026 snap total | 90,927,596,850 | 90,927,596,850 | +0.00e+00 | yes | 100,265,316,841 | +10.27% |
| 1 | participant_count 2026 snap | 58,419,680 | 58,419,680 | +0.00e+00 | yes | 62,235,895 | +6.53% |
| 2 | average_monthly_benefit 2026 snap | 129.7046 | 129.7046 | +0.00e+00 | yes | 134.2544 | +3.51% |
| 3 | benefit_cost 2026 ssi payment_shift_adjusted | 57,857,268,952 | 57,857,268,952 | +0.00e+00 | yes | 57,855,559,926 | -0.00% |
| 4 | participant_count 2026 ssi | 6,108,392 | 6,108,392 | +0.00e+00 | yes | 6,108,392 | +0.00% |
| 5 | average_monthly_benefit 2026 ssi | 789.3139 | 789.3139 | +0.00e+00 | yes | 789.2906 | -0.00% |
| 6 | benefit_cost 2026 tanf total_outlays | 4,936,866,453 | 4,936,866,453 | +0.00e+00 | yes | 5,045,530,740 | +2.20% |
| 7 | benefit_cost 2026 eitc_ctc_other_credits outlays unadjusted | 109,071,629,469 | 109,071,629,469 | +0.00e+00 | yes | 108,835,815,945 | -0.22% |
| 8 | benefit_cost 2026 eitc_ctc_other_credits outlays payment_shift_adjusted | 109,071,629,469 | 109,071,629,469 | +0.00e+00 | yes | 108,835,815,945 | -0.22% |

### pwbm_ss_elimination

| # | row | original | reproduced (old) | rel diff | reproduced? | new | new vs old-reproduced |
|---|---|---|---|---|---|---|---|
| 0 | revenue_change 2025 Ending taxation of Social Security benefits | -102,121,875,631 | -102,121,875,631 | -0.00e+00 | yes | -102,370,343,777 | +0.24% |
| 1 | revenue_change 2026 Ending taxation of Social Security benefits | -114,046,325,481 | -114,046,325,481 | -0.00e+00 | yes | -114,313,256,644 | +0.23% |

### jct_obbba_provision4

| # | row | original | reproduced (old) | rel diff | reproduced? | new | new vs old-reproduced |
|---|---|---|---|---|---|---|---|
| 0 | revenue_change 2026 4. Extension and enhancement of increased child  | -91,169,531,318 | -91,169,531,318 | -0.00e+00 | yes | -91,195,453,103 | +0.03% |

### cpsp_ctc_2024

| # | row | original | reproduced (old) | rel diff | reproduced? | new | new vs old-reproduced |
|---|---|---|---|---|---|---|---|
| 0 | poverty_rate 2024 children_under_18 TCJA CTC | 0.167711 | 0.167711 | +0.00e+00 | yes | 0.156126 | -0.011585 (abs) |
| 1 | poverty_rate 2024 children_under_6 TCJA CTC | 0.177919 | 0.177919 | +0.00e+00 | yes | 0.170092 | -0.007827 (abs) |
| 2 | poverty_rate 2024 children_under_18 No CTC | 0.211547 | 0.211547 | +0.00e+00 | yes | 0.207259 | -0.004288 (abs) |
| 3 | poverty_rate 2024 children_under_6 No CTC | 0.227376 | 0.227376 | +0.00e+00 | yes | 0.222880 | -0.004496 (abs) |
| 4 | poverty_rate 2024 children_under_18 OBBBA CTC | 0.167401 | 0.167401 | +0.00e+00 | yes | 0.155776 | -0.011626 (abs) |
| 5 | poverty_rate 2024 children_under_6 OBBBA CTC | 0.178093 | 0.178093 | +0.00e+00 | yes | 0.169440 | -0.008653 (abs) |
| 6 | poverty_rate 2024 children_under_18 AFA CTC | 0.106548 | 0.106548 | +0.00e+00 | yes | 0.098459 | -0.008089 (abs) |
| 7 | poverty_rate 2024 children_under_6 AFA CTC | 0.115203 | 0.115203 | +0.00e+00 | yes | 0.109736 | -0.005467 (abs) |

### urban_subgroup_counts

| # | row | original | reproduced (old) | rel diff | reproduced? | new | new vs old-reproduced |
|---|---|---|---|---|---|---|---|
| 0 | 6447f789574d90d43db2 housing elig_pop subgroup=age_0thr17 | 21,281,754 | 21,281,754 | +0.00e+00 | yes | 21,281,754 | +0.00% |
| 1 | 3ff62f5226f0bf90c9f0 housing elig_pop subgroup=age_0thr3 | 4,611,626 | 4,611,626 | +0.00e+00 | yes | 4,611,626 | +0.00% |
| 2 | 1ada7614f8924309f9c8 housing elig_pop subgroup=age_4thr5 | 2,706,715 | 2,706,715 | +0.00e+00 | yes | 2,706,715 | +0.00% |
| 3 | b5d9ffbff88a57cd1da7 housing elig_pop subgroup=age_6thr17 | 13,963,413 | 13,963,413 | +0.00e+00 | yes | 13,963,413 | +0.00% |
| 4 | c9093a4a186d9be218d9 housing elig_pop subgroup=age_18thr24 | 6,674,559 | 6,674,559 | +0.00e+00 | yes | 6,674,559 | +0.00% |
| 5 | 9efba3fb797a12c480c5 housing elig_pop subgroup=age_25thr59 | 27,427,424 | 27,427,424 | +0.00e+00 | yes | 27,427,424 | +0.00% |
| 6 | 480a692ec3d87a67e646 housing elig_pop subgroup=race_aapi | 3,405,428 | 3,405,428 | +0.00e+00 | yes | 3,405,428 | +0.00% |
| 7 | 8204e971dd256e187e9f housing elig_pop subgroup=race_black | 13,184,139 | 13,184,139 | +0.00e+00 | yes | 13,184,139 | +0.00% |
| 8 | 35d2dfab8926737f96af housing elig_pop subgroup=race_hispanic | 18,967,045 | 18,967,045 | +0.00e+00 | yes | 18,967,045 | +0.00% |
| 9 | 92d84366f9d06ef52ae2 housing elig_pop subgroup=race_white | 23,455,581 | 23,455,581 | +0.00e+00 | yes | 23,455,581 | +0.00% |
| 10 | 9350e1e11bdef30d0bfa housing elig_pop subgroup=race_multi_other | 2,537,411 | 2,537,411 | +0.00e+00 | yes | 2,537,411 | +0.00% |
| 11 | 4c7373a00d57e5b22b8c housing elig_pop subgroup=disability_yes | 7,184,385 | 7,184,385 | +0.00e+00 | yes | 7,184,385 | +0.00% |
| 12 | 8f2550e81b3df5ee699e housing elig_pop subgroup=disability_no | 54,365,220 | 54,365,220 | +0.00e+00 | yes | 54,365,220 | +0.00% |
| 13 | 86739b581abb822b0b77 housing elig_pop subgroup=status_citizen | 54,143,439 | 54,143,439 | +0.00e+00 | yes | 54,143,439 | +0.00% |
| 14 | ccde4898b54fe93643b7 housing elig_pop subgroup=status_noncitizen | 7,406,166 | 7,406,166 | +0.00e+00 | yes | 7,406,166 | +0.00% |
| 15 | 77c1719980eb2e7dcdcb housing elig_pop subgroup=fam_earners_yes | 56,374,269 | 56,374,269 | +0.00e+00 | yes | 56,374,269 | +0.00% |
| 16 | e4e1fcfb390973dd18ef housing elig_pop subgroup=fam_earners_no | 5,175,336 | 5,175,336 | +0.00e+00 | yes | 5,175,336 | +0.00% |
| 17 | 49b81ec743d82176b7a7 housing elig_pop - part_pop subgroup=race_aapi | 3,342,462 | 3,342,462 | +0.00e+00 | yes | 3,340,692 | -0.05% |
| 18 | b670317b61b233b37bf9 housing elig_pop - part_pop subgroup=race_black | 12,601,313 | 12,601,313 | +0.00e+00 | yes | 12,601,313 | +0.00% |
| 19 | 3a08443a63e8ec1a58fc housing elig_pop - part_pop subgroup=race_hispanic | 18,376,649 | 18,376,649 | +0.00e+00 | yes | 18,376,649 | +0.00% |
| 20 | 35366d5f3fbebecc9477 housing elig_pop - part_pop subgroup=race_white | 22,985,406 | 22,985,406 | +0.00e+00 | yes | 22,985,406 | -0.00% |
| 21 | e8e5d0b1c0d75bedc5d6 snap elig_pop subgroup=age_0thr17 | 25,771,914 | 25,771,914 | +0.00e+00 | yes | 27,410,799 | +6.36% |
| 22 | 4cb70669e6fc54f7cc19 snap elig_pop subgroup=age_18plus | 40,591,712 | 40,591,712 | +0.00e+00 | yes | 44,214,671 | +8.93% |
| 23 | dd989b8e67c53bb3e769 snap elig_pop subgroup=age_0thr3 | 5,541,992 | 5,541,992 | +0.00e+00 | yes | 5,611,228 | +1.25% |
| 24 | c60af358830cb6252b9d snap elig_pop subgroup=age_4thr5 | 3,456,083 | 3,456,083 | +0.00e+00 | yes | 3,486,271 | +0.87% |
| 25 | 08fe5f8882cd2bcb87d0 snap elig_pop subgroup=age_6thr17 | 16,773,839 | 16,773,839 | +0.00e+00 | yes | 18,313,301 | +9.18% |
| 26 | b53baa41f78b5252ffa4 snap elig_pop subgroup=age_18thr24 | 4,292,172 | 4,292,172 | +0.00e+00 | yes | 5,011,054 | +16.75% |
| 27 | c89fc693bda40211bee7 snap elig_pop subgroup=age_25thr59 | 24,033,495 | 24,033,495 | +0.00e+00 | yes | 26,673,621 | +10.99% |
| 28 | 17611500c31a50d00073 snap elig_pop subgroup=age_60thr64 | 3,198,855 | 3,198,855 | +0.00e+00 | yes | 3,311,040 | +3.51% |
| 29 | cae1dcd6da190310a80f snap elig_pop subgroup=age_65plus | 9,067,190 | 9,067,190 | +0.00e+00 | yes | 9,218,957 | +1.67% |
| 30 | b6669fe9866d766629c2 snap elig_pop subgroup=race_aapi | 3,011,605 | 3,011,605 | +0.00e+00 | yes | 3,474,088 | +15.36% |
| 31 | aa01e6a3b8ef4093aeb9 snap elig_pop subgroup=race_black | 12,046,859 | 12,046,859 | +0.00e+00 | yes | 12,321,914 | +2.28% |
| 32 | 07d6e0d9f78a886b0770 snap elig_pop subgroup=race_hispanic | 16,156,938 | 16,156,938 | +0.00e+00 | yes | 17,986,987 | +11.33% |
| 33 | a1ea1368d68983aef790 snap elig_pop subgroup=race_white | 31,750,917 | 31,750,917 | +0.00e+00 | yes | 34,365,659 | +8.24% |
| 34 | 6ce727a9db2dc0772e01 snap elig_pop subgroup=race_multi_other | 3,397,308 | 3,397,308 | +0.00e+00 | yes | 3,476,822 | +2.34% |
| 35 | 43fa866df2bd63174afc snap elig_pop subgroup=disability_yes | 9,377,701 | 9,377,701 | +0.00e+00 | yes | 9,685,750 | +3.28% |
| 36 | cee96cbb60f4755e29b4 snap elig_pop subgroup=disability_no | 56,985,926 | 56,985,926 | +0.00e+00 | yes | 61,939,720 | +8.69% |
| 37 | 9af7e8ddc84597e33f65 snap elig_pop subgroup=status_citizen | 61,911,984 | 61,911,984 | +0.00e+00 | yes | 66,445,155 | +7.32% |
| 38 | 62edbb18407f3844a044 snap elig_pop subgroup=status_noncitizen | 4,451,643 | 4,451,643 | +0.00e+00 | yes | 5,180,315 | +16.37% |
| 39 | 9abb058ca2a4828d5489 snap elig_pop subgroup=fam_earners_no | 10,659,911 | 10,659,911 | +0.00e+00 | yes | 11,061,921 | +3.77% |
| 40 | e1eae55364677a8d15e5 snap elig_pop subgroup=fam_earners_yes | 55,703,716 | 55,703,716 | +0.00e+00 | yes | 60,563,549 | +8.72% |
| 41 | ac45f06409c1ca976dd1 ssi elig_pop subgroup=age_18thr24 | 1,865,020 | 1,865,020 | +0.00e+00 | yes | 1,865,020 | +0.00% |
| 42 | cfc3d5fd8d06f927ad33 ssi elig_pop subgroup=age_25thr59 | 6,969,486 | 6,969,486 | +0.00e+00 | yes | 6,969,486 | +0.00% |
| 43 | 2a30c3e4a13c0cfa4a0c ssi elig_pop subgroup=age_60thr64 | 475,763.9909 | 475,763.9909 | +0.00e+00 | yes | 475,763.9909 | +0.00% |
| 44 | 43e7c7f7bf368f79c1a4 ssi elig_pop subgroup=age_65plus | 24,827,093 | 24,827,093 | +0.00e+00 | yes | 24,827,093 | +0.00% |
| 45 | ee0334f0cb3b17851414 ssi elig_pop subgroup=race_aapi | 2,367,943 | 2,367,943 | +0.00e+00 | yes | 2,367,943 | +0.00% |
| 46 | bd58a981db6391fbfee7 ssi elig_pop subgroup=race_black | 4,202,935 | 4,202,935 | +0.00e+00 | yes | 4,202,935 | +0.00% |
| 47 | d9993c0651e2776000d5 ssi elig_pop subgroup=race_hispanic | 4,694,070 | 4,694,070 | +0.00e+00 | yes | 4,694,070 | +0.00% |
| 48 | 27464c35d442c4277ce7 ssi elig_pop subgroup=race_white | 22,443,714 | 22,443,714 | +0.00e+00 | yes | 22,443,714 | +0.00% |
| 49 | d9a3129a77914df92a00 ssi elig_pop subgroup=race_multi_other | 731,033.6954 | 731,033.6954 | +0.00e+00 | yes | 731,033.6954 | +0.00% |
| 50 | 613fd9c0daa39cbf4748 ssi elig_pop subgroup=status_citizen | 32,759,710 | 32,759,710 | +0.00e+00 | yes | 32,759,710 | +0.00% |
| 51 | fa0333164c09f1b57005 ssi elig_pop subgroup=status_noncitizen | 1,679,986 | 1,679,986 | +0.00e+00 | yes | 1,679,986 | +0.00% |
| 52 | 1253eb2b24b308efccba tanf elig_pop subgroup=age_0thr17 | 76,683,005 | 76,683,005 | +0.00e+00 | yes | 76,683,005 | +0.00% |
| 53 | 0b917d2b18a2365345fd tanf elig_pop subgroup=age_18plus | 92,252,460 | 92,252,460 | +0.00e+00 | yes | 92,252,460 | +0.00% |
| 54 | 340dfb8da12c16a6fa88 tanf elig_pop subgroup=age_0thr3 | 14,243,938 | 14,243,938 | +0.00e+00 | yes | 14,243,938 | +0.00% |
| 55 | 4510653dd654ee2ab85a tanf elig_pop subgroup=age_4thr5 | 8,454,002 | 8,454,002 | +0.00e+00 | yes | 8,454,002 | +0.00% |
| 56 | 9edfd55dcaf005f12148 tanf elig_pop subgroup=age_6thr17 | 53,985,065 | 53,985,065 | +0.00e+00 | yes | 53,985,065 | +0.00% |
| 57 | c19582a5fb59ef7ac3a9 tanf elig_pop subgroup=age_18thr24 | 11,022,577 | 11,022,577 | +0.00e+00 | yes | 11,022,577 | +0.00% |
| 58 | d0f657f33feb3b0114c3 tanf elig_pop subgroup=age_25thr59 | 73,886,447 | 73,886,447 | +0.00e+00 | yes | 73,886,447 | +0.00% |
| 59 | 17261e1dd99765c99652 tanf elig_pop subgroup=age_60thr64 | 2,552,992 | 2,552,992 | +0.00e+00 | yes | 2,552,992 | +0.00% |
| 60 | 74a309678ad820aaae72 tanf elig_pop subgroup=age_65plus | 4,790,443 | 4,790,443 | +0.00e+00 | yes | 4,790,443 | +0.00% |
| 61 | 9736841c4f6b0f8aa462 tanf elig_pop subgroup=race_aapi | 10,729,258 | 10,729,258 | +0.00e+00 | yes | 10,729,258 | +0.00% |
| 62 | 6332745f08b65d136acf tanf elig_pop subgroup=race_black | 22,370,368 | 22,370,368 | +0.00e+00 | yes | 22,370,368 | +0.00% |
| 63 | 335cc0e56d438dedc2da tanf elig_pop subgroup=race_hispanic | 40,688,385 | 40,688,385 | +0.00e+00 | yes | 40,688,385 | +0.00% |
| 64 | 85b4394097f79c4b290e tanf elig_pop subgroup=race_white | 87,803,562 | 87,803,562 | +0.00e+00 | yes | 87,803,562 | +0.00% |
| 65 | 6c71471f20ad1a35ba52 tanf elig_pop subgroup=race_multi_other | 7,343,893 | 7,343,893 | +0.00e+00 | yes | 7,343,893 | +0.00% |
| 66 | 42c8336af7bb63aa38ea tanf elig_pop subgroup=disability_yes | 9,362,530 | 9,362,530 | +0.00e+00 | yes | 9,362,530 | +0.00% |
| 67 | 8f6ab540110c4d3f8ff5 tanf elig_pop subgroup=disability_no | 159,572,936 | 159,572,936 | +0.00e+00 | yes | 159,572,936 | +0.00% |
| 68 | 5aea010ba512b3f4784b tanf elig_pop subgroup=status_citizen | 157,713,786 | 157,713,786 | +0.00e+00 | yes | 157,713,786 | +0.00% |
| 69 | dec9adf49bff95877f33 tanf elig_pop subgroup=status_noncitizen | 11,221,680 | 11,221,680 | +0.00e+00 | yes | 11,221,680 | +0.00% |
| 70 | db9d8df9c0d985394b1c tanf elig_pop subgroup=fam_earners_no | 8,040,762 | 8,040,762 | +0.00e+00 | yes | 8,040,762 | +0.00% |
| 71 | 2fd9975531633b1b995f tanf elig_pop subgroup=fam_earners_yes | 160,894,704 | 160,894,704 | +0.00e+00 | yes | 160,894,704 | +0.00% |
| 72 | 19c4437d63229b51f30b wic elig_pop subgroup=age_0thr3 | 7,019,257 | 7,019,257 | +0.00e+00 | yes | 7,017,856 | -0.02% |
| 73 | 666f3ca7886b7c656bf1 wic elig_pop subgroup=age_4 | 2,348,042 | 2,348,042 | +0.00e+00 | yes | 2,348,042 | +0.00% |
| 74 | 3141e4d5c8ff66b43c01 wic elig_pop subgroup=age_1thr4 | 7,973,256 | 7,973,256 | +0.00e+00 | yes | 7,992,039 | +0.24% |
| 75 | 6c3efbba00a61df63318 wic elig_pop - part_pop subgroup=age_0thr3 | 3,213,471 | 3,213,471 | +0.00e+00 | yes | 3,232,254 | +0.58% |
| 76 | 1459c0cb07814b7e4970 wic elig_pop - part_pop subgroup=age_4 | 1,337,883 | 1,337,883 | +0.00e+00 | yes | 1,337,883 | -0.00% |
| 77 | d29a3eae8b93e6fd20c8 wic elig_pop - part_pop subgroup=age_1thr4 | 4,293,729 | 4,293,729 | +0.00e+00 | yes | 4,312,512 | +0.44% |

### tpc_t25_0209_t26_0029

| # | row | original | reproduced (old) | rel diff | reproduced? | new | new vs old-reproduced |
|---|---|---|---|---|---|---|---|
| 0 | revenue_change 2026 Option 1 Increase child tax credit (CTC) amount to $2,500 | -12,413,332,840 | -12,413,332,840 | -0.00e+00 | yes | -12,422,174,012 | +0.07% |
| 1 | revenue_change 2026 Option 2 Increase CTC amount to $2,500 and CTC maximum re | -15,401,563,611 | -15,401,563,611 | -0.00e+00 | yes | -15,398,407,688 | -0.02% |
| 2 | revenue_change 2026 Option 3 Increase CTC amount to $2,500 and CTC maximum re | -17,771,840,580 | -17,771,840,580 | -0.00e+00 | yes | -17,764,929,017 | -0.04% |
| 3 | revenue_change 2026 Option 1 Increase top individual income tax rate to 39.6  | 1,892,688,240 | 1,892,688,240 | +0.00e+00 | yes | 1,890,896,018 | -0.09% |
| 4 | revenue_change 2026 Option 2 Increase top individual income tax rate to 39.6  | 3,560,167,298 | 3,560,167,298 | +0.00e+00 | yes | 3,558,368,808 | -0.05% |
| 5 | revenue_change 2026 Option 3 Increase top individual income tax rate to 39.6  | 4,413,149,613 | 4,413,149,613 | +0.00e+00 | yes | 4,411,351,614 | -0.04% |
| 6 | revenue_change 2026 Option 1 Total for both provisions | -10,520,644,600 | -10,520,644,600 | -0.00e+00 | yes | -10,531,277,994 | +0.10% |
| 7 | revenue_change 2026 Option 2 Total for both provisions | -11,841,396,313 | -11,841,396,313 | -0.00e+00 | yes | -11,840,038,880 | -0.01% |
| 8 | revenue_change 2026 Option 3 Total for both provisions | -13,358,690,967 | -13,358,690,967 | -0.00e+00 | yes | -13,353,577,403 | -0.04% |
| 9 | revenue_change 2026 American Family Act | -132,466,602,193 | -132,466,602,193 | -0.00e+00 | yes | -132,327,788,230 | -0.10% |
| 10 | exhibit tpc_t25_0209_toprate_opt2_minus_opt1 | 1,670,000,000 | 1,670,000,000 | +0.00e+00 | yes | 1,670,000,000 | +0.00% |
| 11 | exhibit tpc_t25_0209_toprate_opt3_minus_opt2 | 850,000,000 | 850,000,000 | +0.00e+00 | yes | 850,000,000 | +0.00% |
| 12 | exhibit tpc_t25_0209_ctc_opt3_minus_opt2 | -2,370,000,000 | -2,370,000,000 | -0.00e+00 | yes | -2,370,000,000 | -0.00% |
| 13 | exhibit tpc_t25_0209_ctc_opt2_minus_opt1 | -2,990,000,000 | -2,990,000,000 | -0.00e+00 | yes | -2,980,000,000 | -0.33% |
