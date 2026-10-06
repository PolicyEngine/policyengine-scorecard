# Diagnosis batch 2 — US reform-validation registry (2026-10-06)

Scope: the 46 US registry claims at least 50% from their benchmark (or PE = 0)
on the certified bundle **us-6.2.1** (policyengine-us 2.2.1 +
`populace-us-2024-spm-20260915`). Method and queue: [BRIEF.md](BRIEF.md).
Memos with evidence and fix drafts: [A.md](A.md) (JCT OBBBA provisions),
[B.md](B.md) (JCT tax expenditures, IRS SOI), [C.md](C.md) (Census state SPM
poverty), [D.md](D.md) (state credits). Machine-readable items: `<cluster>.json`,
ingested by `scorecard_db/ingest_diagnoses.py` (one diagnosis per claim).

**Result:** 46 claims in 23 items — 18 `pe_gap`, 20 construction issues,
5 concept mismatch, 3 open. The largest single cause is A1: seven "far apart"
JCT claims compared a full calendar-2026 liability with JCT's partial first
fiscal year.

## Applied in this repo

| Item | Change |
|---|---|
| A1 | `ingest_reform_validation._fy2026_timing`: FY2026 results of provisions effective `tyba 12/31/25` (JCX-35-25's Effective column, from the harvest staging) are `concept_mismatch` with a timing annotation; FY2027 stays the headline comparison. TY2025-onset provisions keep `constructed` with an annotation. |
| B7 | `SOI_HELD_OUT`: the AMT and education-credit SOI rows match no calibration target and are relabeled `held_out` (other SOI rows unchanged pending the same check). |

## Routed upstream (drafts in the memos; not yet filed)

| Item | Claims | Class | Route | Finding |
|---|---:|---|---|---|
| C1 | 4 | pe_gap | microcosm (link #646) | Pooled 2022–2024 ASEC incomes stay in nominal own-year dollars but are tested against 2024 SPM thresholds; about +2.6pp of the national child excess (C.md decomposition: weighting +3.1, C1 +2.6, C2 +1.3, other resources −4.5) |
| C2 | 1 | pe_gap | policyengine-us | `market_income` omits partnership/S-corp income (and farm rent, non-Schedule-D gains) while SPM taxes include the tax on it; about +1.3pp nationally, +5.6pp in TN |
| A2 | 2 | pe_gap | microcosm | Tip imputation leaves ~93% of listed-occupation workers with zero tips |
| A3 | 2 | pe_gap | microcosm | Car-loan interest proxy uses one year of loan issuance as the TY2026 stock (residual open) |
| A4 | 1 | pe_gap | microcosm | Non-itemizer cash giving imputed from TY2015 Schedule A misses non-itemizer donors |
| A5 | 2 | pe_gap | policyengine-us + microcosm | Engine zeroes all casualty losses (no declared-disaster carve-out); input rests on 33 records |
| A6 | 2 | pe_gap | policyengine-us (+ annotation) | No estate inputs (PE = 0 by construction); `estate_tax_credit` returns the exclusion amount, not the tentative tax on it |
| B1 | 1 | pe_gap | microcosm | SE (Keogh) pension contributions ~3% of SOI |
| B2 | 1 | pe_gap | microcosm | SE health insurance: right claimant count, half the SOI amount, missing at AGI $200K+ |
| B5 | 1 | pe_gap | microcosm | Education credits 10% of SOI: LLC structurally zero, thin AOTC student pool |
| B6 | 1 | pe_gap | microcosm | AMT from 70 records: top-tail compression |
| D1 | 1 | construction | microcosm (registry spec) | IA HF1020 bracket indices moved under policyengine-us 2.2.1 |
| D2 | 1 | construction | microcosm (registry spec) | MN WFC row measures the repealed pre-2023 `mn_wfc` |
| D3 | 1 | construction | microcosm (registry spec) | Idaho CTC row sums the uncapped nonrefundable credit |
| D4 | 1 | open | policyengine-us | Ohio EITC ordered first among nonrefundable credits; law puts it after CDCC/exemption/joint-filing credits |
| D5 | 1 | open | microcosm (registry spec) | Colorado CTC: TY2024-law simulation vs TY2023 actual explains ~30% |

## Annotations / no model change

| Item | Claims | Class | Finding |
|---|---:|---|---|
| B3 | 1 | concept_mismatch | HSA: JCT line includes employer cafeteria-plan contributions |
| B4 | 1 | concept_mismatch | Traditional IRA: JCT's line values more than the deduction |
| D6 | 3 | concept_mismatch | Flat refundable child credits (CA YCTC, CO FAC, MD CTC): full entitlement vs counted claims |
| D7 | 1 | open | Illinois CTC: pre-enactment cost estimate as benchmark |
| C3 | 9 | construction | Thin state samples around the national shift; state gaps within PE's sampling error (microcosm to emit an SE per rate row) |
| C4 | 1 | construction | Montana: cloned source families on ~52 effective households; one Census negative-resources record |

Spillover outside this repo: policyengine-taxsim maps Minnesota's v39 EITC to
the pre-2023 `mn_wfc` (`policyengine_taxsim/core/state_output_resolver.py:54`).
