# Divergence diagnosis batch 1 — Urban SotSN vs PolicyEngine scorecard

Defensive audit: for each divergence below, FIRST ask what would make our
number wrong, then what would make theirs wrong. Classify each as exactly one
primary class (with optional split):

- `pe_gap` — our eligibility encoding, data, target surface, or take-up
  seeding is wrong/missing → fix draft = PE issue text + PR sketch
- `external_model_issue` — Urban/ATTIS construction looks wrong → memo
  paragraph (ATTIS is closed-source; no upstream PR possible)
- `concept_mismatch` — the numbers measure different things → annotation text
- `data_vintage` — period/data-year difference explains it → annotation text

**Evidence rule (binding): every classification must cite its evidence** —
engine file:line (certified engine 1.764.6 at
`~/populace-sotsn-takeup/.venv-pe/lib/python3.13/site-packages/policyengine_us/`),
populace repo code/targets (`~/PolicyEngine/populace`), a section of
`docs/replication-assessment.md` or `docs/mechanics-audit.md` in this repo, an
administrative series you name precisely, or a computation you perform on the
data files in `data/`. Unevidenced classifications stay `open`. Do NOT state
how any mechanism works without reading it this session.

**Hard constraints**: NO new Microsimulation runs (heavy sims are locked on
this machine) — quantify only from `data/pe/pe_metrics.json`,
`data/comparison.json`, `data/externals/urban-sotsn.json`, and static code
reading. No network. No git push. Work only in this repo's `diagnosis/`
directory plus read-only elsewhere.

Context documents (read first):
- `docs/replication-assessment.md` — methodology both sides, the three
  calibration regimes, §8 definitional deltas
- `docs/mechanics-audit.md` — engine take-up mechanics with file:line cites
- `sources/urban-sotsn/annotations.json` — annotations already shipped
- `data/pe/pe_meta.json` — runtime-recorded variable metadata + run toggles

PE values: annual 2024, certified Populace Build P
(`populace_us_2024 @ populace-us-2024-buildp-sparse-rmloss100-cae8640`,
policyengine-us 1.764.6 via policyengine.py 5.0.1). Urban: average-month
2023, ATTIS on pooled 2022+2023 ACS; participation numerator = actual admin
caseload.

## The queue (national, total rows unless noted)

1. **SNAP participation rate 91.1% (PE) vs 57.5% (Urban); gap 5.90M vs
   29.36M persons.** Eligibility nearly agrees (66.36M vs 69.13M). Expected:
   annual-ever vs average-month semantics + count calibration. Verify and
   QUANTIFY: what do FNS average-month person counts (~42M FY23/FY24) imply
   for an average-month PE rate against our annual eligible pool? Where does
   the residual sit?

2. **TANF eligible persons 8.50M (PE, tanf>0 under forced take-up) vs 11.40M
   (Urban); participation 40.8% vs 18.5%; TANF dollars −36% vs ACF.** Is our
   state TANF rule depth cutting eligibility (which states' machinery is
   stubbed/narrow?), or does Urban count units ours excludes (child-only
   cases, SSF programs)? The −36% dollar miss and the −25% eligible miss may
   share a root.

3. **EITC eligible tax units 26.94M (PE, eitc>0 under forced flag) vs 18.45M
   (Urban); rates 16.6% vs 10.6%.** SOI actual claims ≈ 23.4M sit between.
   Audit our forced-EITC universe: investment-income limit, filing
   assumptions, QC identification, separate-filer exclusions — vs ATTIS's
   eligibility sim. Which side is closer to the IRS/Treasury nonparticipation
   literature's eligible universe (~23–26M in TY2016 NTA work)?

4. **Refundable CTC 17.66M (PE, claims-calibrated) vs 11.79M (Urban
   'eligible for refundable CTC').** SOI ACTC claim counts — name the actual
   TY2023 number — likely sit near ours. Is Urban's eligible universe
   (positive ACTC given eligibility) just narrower than claims by
   construction, or is one side wrong?

5. **SSI eligible adults 9.99M (PE payable-under-forced) vs 12.60M (Urban);
   participation 63.7% vs 51.0%.** Our is_ssi_eligible is pre-income-test;
   payable-under-forced applies the full payment computation. What does
   Urban's 'eligible' include that our payable concept excludes (e.g.
   essential-person rules, state supplements, categorical channels)?

6. **Housing participation 2.7% vs 26.0%; eligible 25.39M SPM units (≤80%
   AMI) vs 16.78M households (≤50% AMI).** Known double concept mismatch +
   HAP dollar under-delivery ($5.6B computed vs HUD ~$50B+). Split the
   divergence into its concept and pe_gap components; the pe_gap piece needs
   an issue draft (HUD PSH count targets + HAP valuation).

7. **Full-participation poverty: −5.1% (PE all-flags) vs −33.6% (Urban);
   child −8.4% vs −43.6%; people lifted −2.36M vs −15.39M.** The shipped
   'fullpart-headroom' annotation claims the baselines differ structurally
   (PE baseline already near admin participation annually; Urban's
   average-month baseline at 57.5% SNAP). Verify empirically from
   pe_metrics.json (fullpart_all vs fullpart_urban6 vs baseline), and check
   whether the Early Head Start $112B defect (populace#593) inflates baseline
   SPM resources enough to suppress measured headroom — quantify its
   plausible contribution WITHOUT new sims (bound it from data/docs).

8. **Baseline child SPM poverty 17.0% (PE 2024) vs 13.8% (Urban 2023).**
   Decompose plausible contributions: year (2023 vs 2024 policy/economy),
   measure construction, EHS distortion, model. Classification may be split.

9. **Alaska SNAP: participation 100.0% of eligible, gap ≈ 2 persons (Urban:
   34.2%, gap 57k).** Smells like the state count-calibration stage forcing
   AK. Read the populace SNAP state stage; is AK's target consistent with FNS
   AK households? Any other states pinned at 100% (check
   data/comparison.json state rows)?

10. **WIC (control case): eligible 9.37M vs 9.44M, rate 51.4% vs 53.5% —
    agreement with ZERO WIC calibration targets.** Confirm from populace
    targets that WIC truly has no anchors, and check the age_0 / age_1thr4
    splits for offsetting errors (populace#520 infant-geography caution).
    Write this up as the out-of-sample validation exhibit.

## Deliverables (write into `diagnosis/`)

1. `diagnoses.json`: array of
   `{queue_id, title, classification, split: {class: share}|null,
   confidence: high|medium|low, evidence: [strings with file:line or series
   names], quantification: string|null, fix_draft: {type:
   pe_issue|upstream_memo|annotation, title, body} | null, open_questions}`
2. `DIAGNOSES.md`: the memo, ordered by importance — what a PE maintainer
   should fix first and why, and what we'd tell Urban if asked.

Commit your work in this repo (branch `diagnosis-batch-1`), do not push.
