# Batch 3 — comment drafts (not posted)

Each draft adds independent evidence from the scorecard's new lanes to an
issue that batch 1 filed. All figures are from bundle us-6.2.1
(policyengine-us 2.2.1 + `populace-us-2024-spm-20260915`).

## microcosm#647 (SNAP saturation and the household-to-person bridge)

> Independent confirmation from the FNS State SNAP participation rates
> (Mathematica for FNS, FY 2022, federal rules), now a scorecard lane
> (PolicyEngine/policyengine-scorecard#150).
>
> **Saturation is measured, not inferred.** In a federal-rules world (BBCE
> input `is_tanf_non_cash_eligible` forced off, average month of 2024), every
> federally eligible person's SPM unit carries `takes_up_snap_if_eligible` in
> **30 States**. 14 of the 16 State rates that sit 10+ points from FNS are in
> those States: PE 98.5–100% against FNS 58.9–89.9%. Nationally, PE is 97.0%
> against FNS's 88%.
>
> **The person grain drives the eligible counts too.** Across the 51
> jurisdictions, PE/FNS eligible people correlates 0.82 with PE/FNS federally
> eligible participants. us-6.2.1 calibrates SNAP households and benefits (104
> `usda_snap.fy2024.*` targets) but no SNAP people or household size. The FY
> 2023 SNAP QC report gives 1.9 people per SNAP household (1.6–2.2 across
> States); PE's participating SPM units average 2.7, and its as-served
> participants are a median 1.45× the QC participants by State.
>
> **Possible fixes:** (1) a release gate that fails when a State's
> post-calibration take-up flag share among eligible units reaches 1;
> (2) SNAP participant (person) targets by State — the QC Table B.1 counts are
> staged for Chronicle in policyengine-scorecard
> `data/ledger/us_admin_outturns.jsonl` (PolicyEngine/policyengine-scorecard#154).

## microcosm#643 (TANF payable eligibility and participation)

> New evidence from ASPE's Welfare Indicators, 25th Report to Congress
> (Table 10, TRIM3), now a scorecard lane
> (PolicyEngine/policyengine-scorecard#153).
>
> - The take-up flag is seeded at 21.9% (24th report, Table 10) and is on for
>   23.8% of PE's TANF-eligible SPM units (unweighted). The **weighted** rate
>   is **41.2%** (911k of 2.21M units, any time in 2024), against ASPE's 22.1%
>   (0.857M of 3.870M families, average month of 2023).
> - The drift comes with the 23 `hhs_acf_tanf.fy2024.cash_assistance` dollar
>   targets (national and 22 States): calibration pushes weight onto
>   participating units and still misses the national target by 36.1%.
> - Eligibility is low as well: 2.21M units eligible at any time in the year,
>   against TRIM3's 3.87M families in an average month.

## microcosm#644 (SSI payable eligibility)

> New evidence against TRIM3 (ASPE Welfare Indicators, 25th Report, Table 12,
> 2023), now a scorecard lane (PolicyEngine/policyengine-scorecard#153).
> PE counts adults with `ssi_if_takes_up > 0` (average month of 2024).
>
> | Unit type | PE eligible | TRIM3 eligible | PE rate | TRIM3 rate |
> |---|---:|---:|---:|---:|
> | Aged individuals | 2.88M | 4.2M (−31.5%) | 60.0% | 49.9% |
> | Disabled individuals | 5.12M | 6.3M (−18.7%) | 74.2% | 62.1% |
> | Couples | 1.00M | 1.0M | 41.9% | 22.7% |
>
> Participants sit near SSA's counts (calibrated), so the eligibility
> shortfall shows up as high participation rates — the same finding as this
> issue's ATTIS comparison. Couples are the exception: equal eligibility, but
> PE has twice TRIM3's participating couple units (0.42M vs 0.2M), which the
> scorecard leaves open.
