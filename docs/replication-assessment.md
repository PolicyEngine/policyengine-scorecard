# Replicating Urban's State of the Safety Net with Populace

*2026-08-01. Canonical computation via **policyengine.py 5.0.1** (`pe.us.managed_microsimulation()`), which resolves the certified **Build P sparse** artifact `populace_us_2024.h5 @ populace-us-2024-buildp-sparse-rmloss100-cae8640-20260728T011454Z` (engine pin pe-us 1.764.6, bundle `us-5.0.1`, sha `48b9d479…`), year 2024. A comparison run on the June 19 dense artifact (`c86a631`, pe-us 1.779.4's internal default) isolates what the take-up contract changed. Scripts + outputs in `~/populace-sotsn-takeup/` (`results/` = Build P canonical; `results_c86a631_direct/` = June comparison; `audit/AUDIT.md` = sol mechanics audit with file:line citations).*

## TLDR

Yes — most of State of the Safety Net is replicable today, and the effective-take-up question has a crisp answer. **Effective take-up in Populace = stored take-up flags × formula eligibility × calibrated weights**, and what each program's rate means depends on which of three regimes it sits in:

1. **Seeded + count-targeted** (SNAP, Medicaid, ACA, EITC/CTC claims; SSI): record-level flags are seeded (sourced rate, receipt anchor, or anchored fill) and calibration softly constrains admin participation counts. Effective participation lands on admin: SNAP participating units 21.8M vs FNS's 22.2M average-monthly-household target (−1.8%); Medicaid enrollment 72.3M vs CMS 71.8M; assigned PTC $60.4B hits its SOI target exactly.
2. **Seeded, dollars-only** (TANF): flag seeded at 0.219 (ASPE/TRIM3) but only dollar targets exist — Build P misses TANF dollars by −36%.
3. **Unseeded/untargeted** (CHIP, Early Head Start, BHP; WIC has a seeded legacy gate but no targets; housing has a receipt anchor but no targets): flags default True → mechanical 100%-of-eligible take-up (CHIP, EHS), or the seeded gate floats free (WIC at 52.8%, coincidentally ≈ Urban's 53.5%).

**The certified artifact matters as much as the mechanism.** The June dense artifact (which pe-us 1.779.4 still pins internally as its own default) predates the take-up contract: it stores nearly all flags all-True, so SNAP ran at 93.4% effective take-up with 30.7M participating units, WIC and Medicaid at literal 100%, and Medicaid *eligibility* was crushed down to equal enrollment (the calibration solver's only degree of freedom). Build P — what policyengine.py actually serves — flips SNAP/TANF/EITC/Medicaid/SSI/Head Start into seeded territory. This is exactly why analysis must load through policyengine.py: the two "defaults" are different worlds.

## 1. What Urban publishes (verified from their March 2026 slides + webtool)

- **Nine programs**: SSI, TANF, SNAP, WIC, CCDF child care, HUD housing, LIHEAP, EITC, refundable CTC (ACTC).
- **Four metrics**: eligible counts, eligibility rates, participation rates, participation gaps — national + 51 states + demographic subgroups + metro/non-metro. Participation rates published for 6 programs (not CCDF/EITC/CTC).
- **Method** (slide 14): ATTIS simulates *eligibility* on pooled 2022+2023 ACS (2.7M households, adjusted to 2023); **participation rate = actual administrative caseload ÷ simulated eligible count**. The numerator is admin data, not simulation. Estimates refer to the **average month** of 2023.
- **Headline 2023 rates among eligibles**: LIHEAP 17.2% (households), TANF 18.5% (people, excl. solely-state-funded), housing 26.0% (households), SSI 51.0% (adults), WIC 53.5% (children 0–4), SNAP 57.5% (people, denominator includes BBCE).
- **Eligibility**: SNAP 69.1M people (21.2%), SSI adults 12.6M (5.0%), TANF 11.4M people (3.5%), WIC children 9.4M (51.7%), CCDF children 11.0M (21.1%), housing 16.8M hh (12.8%), LIHEAP 34.1M hh (26.0%), ACTC 11.8M tax units (6.8%), EITC 18.4M tax units (10.6%).
- **Poverty what-if**: 100% participation in all programs → SPM poverty −34% (−15.4M people), child SPM −44% (−4.4M children), with state maps.
- Funders include the **Pritzker Children's Initiative** (also a PolicyEngine funder), Annie E. Casey, and Packard.

## 2. Engine mechanics (verified in code; corroborated by the sol audit)

- `takes_up_*` flags are **pure inputs, `default_value = True`, no formulas, no randomness anywhere in the engine** (sol's exhaustive scan: 5,651 variable files, zero RNG calls — randomness lives in the populace build, by design).
- Benefit formulas hard-gate on them via `defined_for` (`snap`, `ssi`, `tanf`, `wic` on 1.779.4) or multiply them in (`eitc × takes_up_eitc × filer`; `assigned_aca_ptc = aca_ptc × takes_up_aca_if_eligible` — **gross `aca_ptc` is pre-take-up; use `premium_tax_credit` for participation**).
- Medicaid chain: `medicaid` ← `medicaid_cost` (state-spending allocation via SLCSP index) ← `medicaid_enrolled` ← `is_medicaid_eligible` × flag. CHIP analogous.
- On the certified engine (1.764.6), WIC's take-up gate is the legacy `would_claim_wic` input; 1.779.4 replaced it with `takes_up_wic_if_eligible` — creating a **contract drift**: the engine now has 14 flags vs the contract's 13, so the exact-set release gate fails against 1.779.4 until WIC is added (the certified stack pins 1.764.6, where sets match).
- Eligibility concepts vs Urban's: `is_snap_eligible` includes the full battery incl. **BBCE categorical eligibility** (denominator concept matches Urban's). `is_ssi_eligible` is explicitly "without income test" — broader than Urban's payable concept. `is_eligible_for_housing_assistance` = current recipient OR renter ≤ 80%-AMI (Urban uses ≤ 50% AMI). TANF has **no national income-tested eligibility variable** (state-by-state machinery only).
- LIHEAP/CCDF: not absent, but partial — LIHEAP exists for DC/IL/MA (+ TX CEAP, Riverside County), CCDF via state `child_care_subsidies` + a generic `spm_unit_ccdf_subsidy`; no national LIHEAP output.

## 3. The take-up contract (populace main; live in Build P)

`take_up_contract.json` + dedicated stages (all cited in `audit/AUDIT.md` §C):

| Flag | Treatment | Detail |
|---|---|---|
| SNAP | dedicated stage | **0.82 FNS national prior**, reported recipients forced True, state stage recalibrates to **state household counts** |
| TANF | seed | calibrated Bernoulli @ **0.219** (ASPE 24th Welfare Indicators Table 10 — a TRIM3 rate, i.e. an Urban-model number) |
| EITC | seed | by children: 0=0.65, 1=0.86, 2=0.85, 3+=0.82 (IRS NTA 2020, TY2016; corrects us-data's unsourced 0.85); BLAKE2 stable draws |
| Medicaid, SSI | count_calibrated | reported-coverage/receipt anchor (always takes up) + fill calibrated to CMS state enrollment / SSA Dec-2024 recipient facts (SSI: age-band priors) — **no rate ever cited** |
| Medicare, Head Start, housing | measured-input stages | ASEC `MCARE`; SIPP donor proxy; measured/imputed receipt anchor ("never turns a reporter off, does not add unobserved take-up") |
| ACA | anchored rate/count stage | clipped CMS APTC ÷ eligible-weight fill |
| CHIP, BHP, DC PTC, Early Head Start | rate_unsourced | left unseeded (→100%) with a parity-gate exemption rather than copying us-data's fabricated-rate class |

Doctrine note that matters for a SotSN comparison: the contract's provenance rule **excludes "model-relative ratios (admin numerator over a policyengine eligibility estimate)"** from seedable rates. Urban's published participation rates are exactly that construction — a fine reporting statistic, but populace refuses to bake that class into record-level flags, using count-calibration instead. A PE-built SotSN publishes the same *kind* of statistic (it falls out of count-calibrated builds automatically) without hard-coding anyone's ratio.

**Seeds are not final take-up rates.** The seed fixes *which records* carry a flag; weight calibration then moves every weighted statistic, and the benefit formula zeroes some flagged units. Measured on Build P, the seed → weighted flag share among eligibles → effective participation chain is:

| Program | Seed/prior | Weighted flag share among eligibles | Final effective rate / level |
|---|---|---|---|
| SNAP | 0.82 FNS prior (+ reported anchor + state count matching) | 93.7% | 91.2%; participating units land on the FNS household-count target (−1.8%) |
| TANF | 0.219 (ASPE) | 23.4% | 2.1% on the demographic denominator (income screens zero most flagged units); dollars still miss −36% |
| EITC | ~0.78 blend by children | 74.6% | claims 23.69M ≈ SOI target — the count target, not the seed, sets the level |

So a published take-up rate must always be *measured post-calibration on the artifact* (what `results/takeup_national.csv` does), never quoted from the seed. Where the final rate should be administratively meaningful, the binding instrument is a count target; the seed's job is composition (who participates), not level.

**This divergence is the estimator, not a defect.** The calibrated rate is an indirect-inference estimate of take-up: the numerator is disciplined by admin participation counts, and the denominator — simulated eligibility, which no agency observes — is disciplined by every other targeted margin (income by source × state, demographics, program cross-tabs) flowing through statute-encoded eligibility rules. With enough support, the seed's *level* washes out entirely (EITC: ~0.78 prior blend, final claims pinned to SOI regardless; SNAP: 0.82 prior, final 91–94% against count targets), and the implied rate is jointly consistent with hundreds of administrative facts — better identified than any single survey ratio, including the caseload-÷-one-model construction Urban publishes. Convergence conditions, each auditable: (1) a participation count target exists (TANF today shows the prior-dominated regime — dollars only, rate stays near the seed); (2) the seed's *support* covers the targeted cells — a degenerate all-True prior breaks the estimator by forcing the denominator to absorb the count target (the June Medicaid crush is the proof); (3) the eligibility encoding is correct; (4) heterogeneity below the target surface's resolution remains prior-driven (subgroup take-up rates are identified only where cross-tabbed targets exist — FNS QC composition tables are the natural next family). Built-in falsification (stated precisely): seeds *do* come from FNS/ASPE/NTA where those clear the provenance bar, so held-out validation is program-specific — for count_calibrated programs (Medicaid, SSI) *no* rate is ever cited, so every published participation-rate estimate is out-of-sample; for SNAP, the FNS *national* prior is consumed but FNS's official *state* rates are not, and the final rates are count-driven, so state-level comparison remains substantially independent; for EITC/TANF, comparing our implied rate to the seed's source mostly tests eligibility-model differences (theirs vs ours), which is still informative but not independent validation of the level. A seed-perturbation sensitivity (∂rate/∂seed per program) would turn "the prior doesn't bind" into a reported diagnostic: ~0 for count-targeted programs, ~1 for TANF.

Precision on "pinning" (sol audit §D.3/E): calibration is reweighting with *soft* aggregate constraints. A count target approximately constrains the weighted recipient numerator; it never sets record-level flags and doesn't constrain the eligible denominator independently. With an all-True flag + a count target the solver instead **shrinks weighted eligibility toward the enrollment count** — the June Medicaid pathology (eligibility ≡ enrollment ≡ 73.3M), called out verbatim in `medicaid_take_up.py` and fixed by the anchor-and-fill stage.

## 4. What calibration targets

**Build P (the certified artifact): 5,659 targets over 57,240 records, final loss 0.0177, 95.7% within 10%.** Program surface: SNAP dollars **and average-monthly household counts** (national 22.20M, −1.8%; + state), SSI state recipient counts + payments (111 targets), TANF dollars only (national −36.1% — the visibly failing program), Medicaid/CHIP enrollment counts incl. **standalone CHIP** (7.31M target, −40.8% — under-modeled), ACA marketplace/APTC counts + SOI PTC returns (7.84M, +2.1%) and dollars ($60.4B, exact), EITC/CTC claims + dollars. **WIC and housing: zero targets.**

June dense (comparison): 4,408 targets, 88.2% within 10%; same families minus the SNAP household counts, SSI recipient counts, and standalone CHIP — i.e., SNAP/SSI/TANF were dollars-only there.

## 5. Computed effective take-up — certified Build P via policyengine.py (year 2024)

Full tables: `results/takeup_national.csv`, `results/takeup_by_state.csv` (8 programs × 51 states), `results/aca_assigned_fix.json`.

| Program | Eligible | Participants | Effective rate | Stored flag share among eligible | Dollars | Admin/Urban anchor |
|---|---|---|---|---|---|---|
| SNAP (SPM units) | 23.91M | 21.81M (60.6M persons) | **91.2%** | 93.7% | $92.0B | FNS FY24: 22.5M avg-month hh, $93.9B; Urban rate 57.5% (people, avg month) |
| SSI (persons; pre-income-test denom) | 34.44M | 6.54M | **19.0%** | 51.2% | $56.1B | SSA: ~7.4M recipients, $63B; Urban 51.0% (payable-adult denom) |
| TANF (SPM units; demographic denom) | 42.29M | 0.89M (3.5M persons) | 2.1% | **23.4%** (≈ the 0.219 seed) | $5.0B | ACF basic assistance $7.8B (−36% miss); Urban 18.5% |
| WIC (persons) | 12.66M | 6.68M | **52.8%** | (`would_claim_wic` gate) | $6.7B | actual avg-month ≈ 6.6M; Urban 53.5% |
| EITC (tax units) | (broad `eitc_eligible` 100.7M) | 23.69M | — | 74.6% (≈ NTA by-children blend) | $66.8B | SOI claims ≈ 23.4M — claims-targeted |
| Refundable CTC | — | 17.66M | — | — | $37.5B | claims + dollars targeted |
| Medicaid (persons) | 77.3M | 72.3M | **93.5%** | 93.5% | $880B | CMS Dec-24: 71.8M — eligibility now *exceeds* enrollment (June crush fixed) |
| CHIP (persons) | 4.32M | 4.32M | 100% (unseeded) | absent → True | $13.0B | CHIP target 7.31M missed −41% |
| ACA PTC (tax units, **assigned** PTC) | 29.8M | 8.01M | **26.9%** | 26.9% | $60.4B | SOI PTC returns 7.84M (+2.1%), dollars exact |
| Housing (SPM units) | 25.4M (June's degenerate 94.7M resolved) | 0.69M | 2.7% | 10.6% (receipt anchor) | $5.6B | HUD ~4.6M assisted hh — computed HAP under-delivers; untargeted |
| Head Start (persons) | 5.03M | 0.30M | 5.9% (SIPP proxy) | 5.9% | $4.9B | plausible |
| Early Head Start (persons) | 5.16M | 5.16M | **100% (defect)** | unseeded | **$112.3B** | actual ~$1–2B — task chip filed |
| Free school meals (SPM units) | — | 15.06M | — | — | $28.1B | untargeted |

### 5b. The A/B: June dense (pre-contract) vs Build P (contract live)

| Program | June: rate / participants | Build P: rate / participants | What changed |
|---|---|---|---|
| SNAP | 93.4% / 30.7M units | 91.2% / 21.8M units | flags seeded (0.82 prior + anchors) + household-count targets → participants land on FNS |
| TANF flag share | 100% | 23.4% | the ASPE 0.219 seed, live |
| EITC flag share | 100% | 74.6% | the NTA by-children seeds, live |
| WIC | 100% / 11.6M | 52.8% / 6.7M | seeded legacy gate carries variation |
| Medicaid | 100%, eligibility crushed to 73.3M | 93.5%, eligibility 77.3M > enrollment 72.3M | anchor-and-fill count calibration |
| SSI | 31.7% (all-True flag) | 19.0% (flag 51.2%) | count-calibrated stage + SSA recipient facts (broad denominator unchanged) |
| Housing eligible denom | 94.7M units (degenerate) | 25.4M units | data fix in Build P inputs |

By state (Build P, `results/takeup_by_state.csv`): SNAP and SSI now carry state count targets, so state effective rates are admin-shaped rather than free-floating; TANF state dollars remain rough (they were wild in June: NY −77%, WI +572%).

## 6. Can we replicate SotSN? Program-by-program

| Urban program | PE status | Verdict |
|---|---|---|
| SNAP | eligibility (incl. BBCE) + seeded take-up + household-count calibration | ✅ now; add avg-month person framing |
| SSI | count-calibrated; needs a payable-eligibility denominator for Urban-comparable rates | ✅ with denominator care |
| TANF | seeded flag; dollars miss −36%; no income-tested national eligibility variable | ⚠️ needs eligibility + target work |
| WIC | eligibility + seeded gate; zero targets (rate is luck, not anchoring) | ⚠️ add FNS targets |
| EITC / ACTC | claims + dollars targeted | ✅ (richer than Urban: we can show claims vs eligibility) |
| Housing | receipt anchor; needs ≤50%-AMI denominator + HAP dollar work; untargeted | ⚠️ |
| LIHEAP | state fragments only (DC/IL/MA/TX); no national output | ❌ build |
| CCDF | state programs + generic subsidy; no national coverage | ❌ build out |
| (bonus: Medicaid, CHIP, ACA, school meals, Head Start — PE covers, Urban doesn't) | | ➕ |

The poverty side (SPM with/without programs, full-participation counterfactual, state maps) is stock output. On Build P the baseline now embeds *seeded* take-up, so Urban's headline what-if is literally `set all takes_up_* flags True` (plus `would_claim_wic`) — a one-line reform.

## 7. What to build (priority order)

1. **TANF**: income-tested eligibility variable + fix the −36% dollar miss (state TANF rule depth); consider ACF caseload count targets.
2. **WIC**: FNS participation targets (dollars + participants by category) so the 52.8% is anchored, not lucky.
3. **Housing**: ≤50%-AMI denominator variant + HAP dollar validation (computed $5.6B vs HUD ~$50B+ is the gap to close before publishing housing rates); consider HUD Picture-of-Subsidized-Households count targets.
4. **CHIP depth** (target missed −41%) and **Early Head Start seeding** (chip filed — $112B at 100% take-up).
5. **National LIHEAP + CCDF surfaces** (state fragments exist).
6. **SSI payable-eligibility denominator** (amount>0 under forced take-up) for Urban-comparable published rates.
7. Then the webtool: 4 metrics × 9 programs × 51 states + subgroups + poverty what-ifs, filtered from the one national artifact, average-month semantics per populace#332.

## 8. Definitional deltas to state in any comparison

- PE = annual 2024; Urban = average-month 2023. PE units = SPM units/persons/tax units; Urban = households, adults, children 0–4, tax units.
- Urban's participation numerator is admin caseloads over ATTIS eligibility; PE's is simulated (seeded + calibrated) participation — for count-targeted programs these converge by construction.
- SOI-based targets make PE's EITC/CTC/PTC recipients match *claims* (including erroneous claims); Urban publishes no EITC participation rate partly because claims exceed their eligibles (23.4M vs 18.4M).
- SSI/TANF effective rates here use broader denominators than Urban's (pre-income-test / demographic-only); don't quote them side-by-side without relabeling.
