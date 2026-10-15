# Investigation of the largest moves: certified 6.2.6 replay against the legacy run

An independent investigation by a GPT-6.1 Sol lane, commissioned by the
Autumn Budget 2026 coordinating session on 11 October 2026, of the largest
moves between the legacy replay (policyengine 5.0.2, policyengine-uk 2.89.2,
Populace UK 2023) and the certified release replay (policyengine 6.2.6,
policyengine-uk 2.125.1, enhanced FRS 2024-25 from uk-data 1.58.0). It read
this repository at commit 49f1a5ad. Its classifications rest on weighted
input aggregates, controlled calls to source formulas and synthetic
single-household cases; no record-level data is reproduced here.

Reproduced as received. Mechanisms it describes are its findings, cited to
upstream pull requests and source paths; this repository has not
independently re-verified each of them. The later diagnostic separating run
(`docs/uk_replay/SEPARATING_RUN.md`, when it lands) tests its "data
difference" calls with an old-engine-on-new-population decomposition.

Editor's notes. The 6.2.6 replay artifacts it cites at 49f1a5ad are on the
branch of PR #164, not in this commit's ancestry. Its description of #2140
("payment resuming when the charge fraction becomes zero") is narrower than
the installed rule: in 2.125.1 an opted-out family stays opted out only while
fully charged (`opt_out_charge_share` = 1), so payment resumes as soon as the
charge share falls below one; see CONSTRUCTION_REVISIONS.md.

---

Both structural moves are confirmed upstream fixes. The strongest evidence for the other moves is a changed childcare-cost tail among UC families, a much smaller capital-gains input base, and a changed self-employment distribution. LHA and the two UC measures remain only partly attributed.

The certified pair also retains material current-law defects. A smaller replay figure does not establish that its costing is correct.

## Evidence and interpretation

I read the guidance, recipe, constructions, packets and results at scorecard commit **`49f1a5ad4629a38cb8705178bf0783fbe3e981b8`**. I made no edits or external writes.

| Identity | Legacy | New certified pair |
|---|---|---|
| policyengine | 5.0.2 | 6.2.6 |
| policyengine-uk | 2.89.2 | 2.125.1 |
| policyengine-core | 3.27.1 | 3.33.0 |
| Population | Populace UK 2023 | enhanced_frs_2024_25, uk-data release 1.58.0 |
| UK engine SHA | `4fcc895e55d8fbd2c6cbe8d6423f068cb280dc16` | `e89b8abcf524de48e590b9680e1a04288d30eacd` |

The exact cached dataset bytes were independently hashed:

- **Legacy SHA256:** `f17306ccb2aad7ff0130be3589b560afb2e2a12a943570911cd0c77f07934833`
- **New SHA256:** `5ba399ea5ab9a6c7d4e9aaf6c623080beb34d9ad5f330f6244dbad72b8d960b6`

All input aggregates below refer to these hashes. They use household weights joined to people or benefit units. Their source periods are **2023 versus 2024**, so they capture a population/year/imputation difference rather than a clean data-family effect.

The national figures come from the committed replay artifacts under:

`results/uk/replays/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/`

and their legacy counterparts under `results/uk/events/`, all at the scorecard SHA above.

I did **not** obtain a national new-engine/legacy-population separating run. Fresh diagnostics comprise weighted input calculations, controlled calls to exact source formulas, and selected full new-engine synthetic simulations. Previously saved paired full-engine diagnostics are identified explicitly. Synthetic cases have no population dataset hash.

Following the repository guidance, ratios are descriptive. OBR comparisons retain the mapped head and scope: calendar-year model lookups proxy fiscal-year cells, and uncomputed counterpart heads are not silently included. Live statuses of open issues/PRs remain **unverified**; merged fixes were checked through local source and merge ancestry.

## 1. SB2023 UC childcare cap increase

**Classification: data difference is strongly supported; eligibility model fixes also contribute, with their national shares unknown.**

Across CY2024–27, the cost changes from **−£7.512m to −£921.578m**, ×122.69. The mapped OBR inside-cap cells sum to **−£330.720m**: the new magnitude is 2.79 times that comparison.

The critical difference is the childcare-cost distribution **conditional on reported UC**, rather than overall childcare spending.

| Executed base-period input diagnostic | Legacy | New |
|---|---:|---:|
| Total childcare expenses | £8.262bn | £10.175bn |
| Benefit units with positive expenses | 1,884,590 | 1,886,385 |
| Positive expenses and reported UC | 145,514 | 481,559 |
| Expenses in those reported-UC units | £401.053m | £1,919.676m |
| Reported-UC units above the old relevant cap, using the proxy below | 2,324 | 42,512 |

I applied the same 2024 caps to both populations:

```text
gross cap increase =
min(85% × expenses, new cap) − min(85% × expenses, old cap)
```

Monthly caps were £689.60→£1,014.63 for one child and £1,182.39→£1,739.37 for two or more. The diagnostic uses under-18 counts as a proxy for eligible-child counts and excludes means testing and benefit caps.

- Across all expense-positive units: **£543.398m→£656.467m**, ×1.21.
- Among reported-UC units: **£1.721894m→£130.192428m**, **×75.61**.
- Requiring every adult to have positive earnings or hours leaves those reported-UC results unchanged.
- Among `would_claim_uc` units satisfying that work proxy: **£155.995m→£373.224m**, ×2.39.

The legacy reported-UC proxy closely matches the replay’s CY2024 **£1.793718m** cost. The new proxy accounts for about 60% of its **£218.234954m** cost. This locates a substantial cause; it does not fully decompose projection, eligibility or newly entitled claimants.

**Source changes.** At the new engine SHA, [uc_childcare_element.py](https://github.com/PolicyEngine/policyengine-uk/blob/e89b8abcf524de48e590b9680e1a04288d30eacd/policyengine_uk/variables/gov/dwp/universal_credit/childcare_element/uc_childcare_element.py) retains the same `min(cap, coverage × expenses)` arithmetic. The caps and frozen reversal rederive identically.

Relevant merged changes are:

- [#1857](https://github.com/PolicyEngine/policyengine-uk/pull/1857), merge `a6a78c4089b98bd6f5463cae01986b2c0a20fdfb`: adds `would_claim_uc_childcare` to the claim gate. It defaults **True** and is absent from the inspected new population; this change alone cannot increase the costing.
- [#2088](https://github.com/PolicyEngine/policyengine-uk/pull/2088), merge `99d0448d75929d82dca9a82d1bec9ceaaed5b2da`: partner exceptions, treated-as-paid-work cases and offers of work in `uc_childcare_work_condition.py`.
- [#1978](https://github.com/PolicyEngine/policyengine-uk/pull/1978), merge `1a18f93a20fcc90bba25269db1d23791ee8bf3b5`: assessed-claimant income and composition.
- [#2084](https://github.com/PolicyEngine/policyengine-uk/pull/2084), merge `4ed5b3ce463ef7eccfa1ca0d7b9b7b8e8e891375`: single claims within couples.
- [#1896](https://github.com/PolicyEngine/policyengine-uk/pull/1896), merge `3525263f8ec2f75d59e17f11a75aefd96648f9a1`: programme-specific child/claimant definitions.

Neither version’s childcare formula reads `would_claim_tfc`; a removed Tax-Free Childcare exclusion is **not** an evidenced explanation.

**Minimal case.** A worker aged 35 earning £20,000, a nonworking partner with limited capability for work-related activity, and a three-year-old with £18,000 annual childcare costs:

- Exact old/new work-condition formulas: **False→True**.
- Full new-engine simulation: childcare element **£12,175.56**.
- Holding eligibility true, the cap increase adds **£3,900.36 annually**, by the unchanged cap arithmetic.

That demonstrates a lawful eligibility fix, whose national contribution remains unsized.

**Recommended action: draft a UK-data investigation.** New release source `1.58.0`, SHA `4cbedbecca352f52dffe47e849553c2759a00711`, creates childcare expenses in `policyengine_uk_data/datasets/frs.py` by summing registered paid-childcare amounts and multiplying by 52. Agreement with the underlying survey amount-period coding is **unverified**.

**Draft title:** Investigate the high-cost childcare tail among UC families in the certified eFRS replay

**Draft body:**

> The fixed SB2023 childcare-cap reversal costs £1.794m in CY2024 on PE 5.0.2/UK 2.89.2/Populace 2023 and £218.235m on PE 6.2.6/UK 2.125.1/uk-data 1.58.0. Engine and population changed together; this is not an attributed engine defect.
>
> Dataset SHA256s are `f17306ccb2aad7ff0130be3589b560afb2e2a12a943570911cd0c77f07934833` and `5ba399ea5ab9a6c7d4e9aaf6c623080beb34d9ad5f330f6244dbad72b8d960b6`.
>
> Total childcare expenses rise 23%, but expenses among reported-UC units rise £401.053m→£1,919.676m. Applying identical 2024 caps gives gross cap-increase exposure £1.722m→£130.192m; cap-bound reported-UC units rise 2,324→42,512. Requiring all adults to work leaves these results unchanged.
>
> Please audit childcare annualisation, UC receipt linkage, calibration weights and this joint high-cost tail against administrative childcare-element claims. Then obtain a separating run and recipient-level decomposition. Cap arithmetic and the reversal are unchanged; known eligibility fixes may contribute, but their shares are unmeasured.

## 2. AS2023 LHA reset

**Classification: confirmed model fixes plus data difference; attribution of the national ×2.45 increase remains unknown.**

CY2024–28 costs total **−£3.937bn→−£9.629bn**, ×2.446. The mapped OBR inside-cap total is **−£5.766bn**, giving a new/OBR magnitude ratio of 1.67. Outside-cap cells remain uncomputed.

Population exposure changes materially:

- Private-renter households: **5.636m→6.455m**.
- Rent across renting tenures: **£96.375bn→£123.175bn**.
- Reported HB recipients decrease: **1.919m→1.504m**.

**Verified source fixes:**

- [#1844](https://github.com/PolicyEngine/policyengine-uk/pull/1844), `94948a1dc4461b3339225da8586a474f8302cbbf`: national maxima, separate monthly UC maxima, and freezing the latest unfrozen determination.
- [#1926](https://github.com/PolicyEngine/policyengine-uk/pull/1926), merge `40cc541dd94deb2320a6ccc9b57e207fdc83b975`: caps eligible HB rent **before** applying the income taper.
- [#2006](https://github.com/PolicyEngine/policyengine-uk/pull/2006), merge `27dd5f7aa68ebf3a06a45f246f316b6f637912f0`: benefit-unit rent liability and treatment of sharers, boarders and lodgers.
- [#2022](https://github.com/PolicyEngine/policyengine-uk/pull/2022), merge `c004e53180218cfc5ad274732e6647070f1fbf53`: published determinations, anomalous-rate rules and the March 2020 floor.
- [#2134](https://github.com/PolicyEngine/policyengine-uk/pull/2134), merge `f2758cecb3502a3d2d8838883caa3e9f859d9a31`: separate HB/UC category handling.

Pinned source includes [utils/lha.py](https://github.com/PolicyEngine/policyengine-uk/blob/e89b8abcf524de48e590b9680e1a04288d30eacd/policyengine_uk/utils/lha.py), `variables/gov/dwp/{uc_LHA_cap,housing_benefit_LHA_rate}.py`, `housing_benefit/entitlement/housing_benefit_entitlement.py`, and `parameters/gov/dwp/LHA/`.

**Minimal cases show opposing effects.**

For Maidstone category C, CY2024, rent £20,000, the full new-engine UC cap is **£10,860**, versus **£9,779.88** with the reset reversed: an increase of **£1,080.12**. Reconstructing the old rent-list formula with its processed indices gives **£11,169.392 versus £9,771.06**, an increase of **£1,398.332**. This statutory-rate correction shrinks the example’s reset effect.

For HB, with rent £10,000, excess income £5,000, no deductions and an LHA cap increasing £6,000→£7,000, exact source calls give:

| Formula | Before | After | Increase |
|---|---:|---:|---:|
| Legacy | £6,000 | £6,750 | £750 |
| New | £2,750 | £3,750 | £1,000 |

Correcting the taper increases marginal sensitivity despite reducing award levels.

**Recommended action: no new defect issue.** Retain the verified fixes. A national decomposition by UC/HB, BRMA, category, binding rent and claimant status is needed before assigning the multiplier to particular changes.

## 3. SS2025 UC health element

**Classification: mixed data/engine effects; full attribution unknown. A separate inherited current-law defect persists.**

CY2026–29 savings total **£1.666bn→£4.094bn**, ×2.458, against mapped OBR savings of **£7.698bn**. The new figure is 53% of that comparison.

Relevant executed input diagnostics:

| Input | Legacy | New |
|---|---:|---:|
| Reported UC payments | £33.475bn | £55.037bn |
| Benefit units with positive reported UC | 2.938m | 4.158m |
| Positive reported UC and any disabled member | 0.921m | 1.746m |
| Any-disabled benefit units | 4.535m | 6.458m |

“Any disabled member” is an exposure diagnostic, not an LCWRA caseload. Replay current-law UC totals in CY2026 also rise **£39.888bn→£83.510bn**.

**Source changes.** [scenarios/uc_reform.py at the new pin](https://github.com/PolicyEngine/policyengine-uk/blob/e89b8abcf524de48e590b9680e1a04288d30eacd/policyengine_uk/scenarios/uc_reform.py) differs directly through the copy-before-mutation fix:

- [#1988](https://github.com/PolicyEngine/policyengine-uk/pull/1988), merge `068f270c7a02babe0c3a8033dbf6fe815ab397b0`, implementation `25fb97f7461b7862a8b8ccbd60df94349943dd66`.
- `uc_LCWRA_element.py` changes under **#2084**, excluding ineligible partners from assessed claims.
- Wider UC changes include **#1978** claimant-only income; [#1950](https://github.com/PolicyEngine/policyengine-uk/pull/1950), merge `770bc06a05dfb567c51d5258a27f328e310d19e8`, removing actual interest/dividend/rent income from UC unearned income; and [#1949](https://github.com/PolicyEngine/policyengine-uk/pull/1949), merge `fc1ecc4d3d02d9a21e0f4da2c76637d6a9a43a79`, claimant-specific tax/NIC deductions.

The counterfactual rate rederives identically. The construction assigns new-claimant shares of **11%, 13%, 16%, 22%**, using seed 43; these are scenario assumptions rather than observed claim histories. It reverses the new-claimant rate while retaining later protections, so it does not reconstruct every component of the original March 2025 package.

**Minimal current-law defect.** Exact source arithmetic for a protected older single claimant in 2026 gives:

```text
(£400.14 + £423.27) × 1.034 − £424.90 = £426.50594/month
```

The statutory protected LCWRA amount is **£429.80**, a **£39.53 annual shortfall** in this case. The legislation sets the amount directly. [2026 Uprating Regulations, regulation 3](https://www.legislation.gov.uk/uksi/2026/113/regulation/3/made/data.html).

**Recommended action:** fold into [#2247](https://github.com/PolicyEngine/policyengine-uk/issues/2247). Local fix commit `f1f2dc6a62682b3aaf121ac25250092b39ed751a` is outside the certified pin; its live integration status is unverified. Revise or explicitly limit the historical construction if presenting it as the whole SS2025 health package. Neither defect nor construction limitation independently explains ×2.46.

## 4. SS2025 UC standard allowance

**Classification: data difference is supported; engine eligibility effects remain unsized. The direct allowance formula is unchanged, and an inherited schedule defect persists.**

CY2026–29 costs total **−£1.649bn→−£2.952bn**, ×1.790, versus OBR inside-cap **−£4.376bn**. The new magnitude is 67% of that comparison. In CY2026 alone, however, new **−£720.867m** exceeds OBR **−£667.365m**.

The UC population/payment diagnostics above support increased exposure. They do not isolate the contribution of the wider UC fixes.

[uc_standard_allowance.py](https://github.com/PolicyEngine/policyengine-uk/blob/e89b8abcf524de48e590b9680e1a04288d30eacd/policyengine_uk/variables/gov/dwp/universal_credit/standard_allowance/uc_standard_allowance.py) is byte-identical between the two tags: it returns the claimant-type monthly amount multiplied by 12. It does not apply `parameters/gov/dwp/universal_credit/rebalancing/standard_allowance_uplift.yaml`.

The certified pair consequently omits the legislated **2027–29 increases in the above-inflation uplift level**. The statutory levels are 3.1%, 4.0% and 4.8%; they are level adjustments over the CPI reference path, not successive annual additional increases. [Universal Credit Act 2025, section 1](https://www.legislation.gov.uk/ukpga/2025/22/section/1/data.html).

**Minimal case.** Saved paired full-engine receipts for a single adult aged 30 show identical CY2027 allowance **£5,216.06104** on both pins. Fresh formula calls confirm the equality. Under the same inflation assumptions, advancing the embedded 2026 uplift level from 2.3% to the 2027 level of 3.1% adds:

```text
£5,216.06104 × (1.031 / 1.023 − 1) = £40.79031 annually
```

Saved receipts are in the existing replay environment’s diagnostics folder as `{base,new}_uc_standard_allowance_2027_2030_pe_uk_2239.json`.

**Recommended action:** fold into [#2239](https://github.com/PolicyEngine/policyengine-uk/issues/2239) / [#2242](https://github.com/PolicyEngine/policyengine-uk/pull/2242), then certify and rerun the completed fix. Candidate implementation `bc8f00bb2bc25dd9ac43da9c5ee5fa52f4aaf564` is outside 2.125.1; live PR status is unverified. Preserve health-element interactions and uncomputed outside-cap heads.

## 5. AB2024 CGT main rates

**Classification: data difference strongly explains the full-year decline; a separate construction issue omits the first part-year effect.**

CY2024–29 revenues total **£24.788bn→£12.523bn**, ×0.505. CY2026 changes **£4,793.564m→£2,414.558m**.

Executed inputs show a sharply smaller gains base:

| Capital-gains input | Legacy | New |
|---|---:|---:|
| Weighted gains | £91.435bn | £39.118bn |
| Positive-gains people | 1,549,102 | 1,032,538 |
| Gains above £40,000 | 513,571 | 71,117 |

Neither population supplies separate BADR, residential-property or carried-interest gains. Response elasticities are zero. With those named components zero, the new formula preserves the single-schedule calculation; taxable-income changes can still alter band allocation.

**Source changes:**

- [#1806](https://github.com/PolicyEngine/policyengine-uk/pull/1806), `2ddce3094ff0fe1972d4404724503bc8b592785a`: correct 30 October commencement and fiscal-year blending in `parameters/gov/hmrc/cgt/*_rate.yaml` and `utils/parameters.py`.
- [#1861](https://github.com/PolicyEngine/policyengine-uk/pull/1861), merge `06e81c00d6e2ab11da43d6d8f62c15286abd6b32`, formula `4a5f7aa1056918b3d3ad6f09f02b7b30d5c9a83f`: separate gains schedules in [capital_gains_tax.py](https://github.com/PolicyEngine/policyengine-uk/blob/e89b8abcf524de48e590b9680e1a04288d30eacd/policyengine_uk/variables/gov/hmrc/capital_gains_tax/capital_gains_tax.py).
- Response changes: **#1803**, `22a2d343540179120cf4702bf1c71720fc12ed36`; **#1823**, `f40078cbe2cc8470ea355755dc2af263980d6276`; **#1980**, merge `3db24cde37472e6a78e181af96e8d068bf620101`. Their response mechanisms are inactive under the inspected zero-elasticity settings.

**Day-weighting does not explain ×0.51.** Both engines use 18%/24% from CY2025 onward, versus reversal rates 10%/20%.

For £100,000 gains, £100,000 adjusted net income, £12,570 income allowance and £3,000 AEA, controlled source calls give:

| Case | Current CGT | Frozen reversal |
|---|---:|---:|
| Both engines, CY2026 | £23,280 | £19,400 |
| Legacy, CY2024 | £19,400 | £19,400 |
| New, CY2024 | £21,079.56 | £21,079.56 |

The new CY2024 higher rate is `20%×207/365 + 24%×158/365`. Extending the reversal into CY2024 restores £19,400 and captures the omitted **£1,679.56** in this case.

**OBR comparison:** CY2026’s mapped CGT cell is only **£95.779m**, versus PE **£2,414.558m**. OBR also assigns **£1,262.326m** to Income Tax and **−£65.673m** to Stamp Duty, which PE does not compute here. These head allocations must remain explicit. The pooled gains input also prevents isolation of unchanged residential rates.

**Recommended action:** apply the proposed conditional CY2024 reversal revision in [CONSTRUCTION_REVISIONS.md at the requested head](https://github.com/PolicyEngine/policyengine-scorecard/blob/49f1a5ad4629a38cb8705178bf0783fbe3e981b8/docs/uk_replay/CONSTRUCTION_REVISIONS.md). Separately preserve the pooled-gains and unreversed-reliefs limitations. No new engine issue is established by the ×0.51 decline.

## 6. SB2023 Annual Allowance increase

**Classification: data difference is supported; substantial inherited model defects remain.**

CY2024–27 costs total **−£22.190bn→−£12.559bn**, ×0.566. CY2026 Income Tax is **−£3,279.437m**, versus OBR **−£414.630m**, a magnitude ratio of 7.91. PE NICs is zero versus OBR **−£21.110m**.

There are no between-tag changes to:

- [pension_contributions_relief.py](https://github.com/PolicyEngine/policyengine-uk/blob/e89b8abcf524de48e590b9680e1a04288d30eacd/policyengine_uk/variables/gov/hmrc/pensions/pension_contributions_relief.py);
- `pensions/private_pension_contributions_tax.py`;
- `income_tax/allowances/pension_annual_allowance.py`;
- `pensions/pension_contributions_for_annual_allowance.py`;
- the annual-allowance parameters.

The contribution distribution changes despite similar overall totals:

- Sum of personal, employee, employer and salary-sacrifice inputs: **£188.975bn→£190.991bn**.
- People whose four-input sum exceeds £40,000: **456,192→356,870**.
- Exposure between £40,000 and £60,000: **£6.202bn→£5.176bn**.
- People with employer contributions above £60,000: **175,167→92,271**.

These are raw-input proxies, not a complete statutory pension-input calculation. They support changed tail/imputation exposure but do not fully explain ×0.57.

**Minimal defect case, saved paired full-engine receipts:** London adult aged 45, salary £150,000:

| Personal contributions | Relief | AA charge | Income Tax |
|---|---:|---:|---:|
| £60,000 | £60,000 | £0 | £28,460 |
| £80,000 | £60,000 | £8,000 | £36,460 |

Both pins give these outputs. Excess contributions lose relief and also incur a charge: existing **#2237**, rather than a new regression.

Additional saved new-pin cases show:

- £30,000 taxed income and £20,000 AA excess: charge **£4,000**, versus **£6,460** when the excess is correctly taxed across bands.
- Salary £240,000 plus employer contributions £50,000: model AA **£60,000**, versus **£45,000** under the adjusted-income taper.

HMRC specifies charging the excess as a top slice across applicable bands, and includes employer contributions in adjusted income. [AA charge calculation](https://www.gov.uk/hmrc-internal-manuals/pensions-tax-manual/ptm056110), [tapered allowance](https://www.gov.uk/guidance/pension-schemes-work-out-your-tapered-annual-allowance).

**Recommended action:** fold into [#2237](https://github.com/PolicyEngine/policyengine-uk/issues/2237) / [#2240](https://github.com/PolicyEngine/policyengine-uk/pull/2240). Reviewed local candidate commits include `a89d9e19289f08539c8cc361a408d6a88b502639` for relief/charge treatment and `1bb293cac8fe8f94db513d16f9af349a9ff84397` for relief-at-source band extensions. They are outside the certified pin. Preserve the separate taper defect and rerun after certification. The PR’s “open” status is supplied by the brief, not independently verified.

## 7. Class 4 cuts

**Classification: substantial data difference plus confirmed model fixes; exact decomposition unknown.**

SB2024 CY2024–28 costs total **−£5.818bn→−£3.103bn**, ×0.533. The AS2023 cut has almost the same ratio, ×0.534.

Executed inputs:

- Self-employment income: **£145.566bn→£113.761bn**.
- Positive-income people: **4.530m→4.620m**.
- Income above £40,000: **1.093m→0.412m**.
- Common uncapped two-point-cut proxy, `2%×clip(income−12570,0,37700)` for ages 16–65: **£1.077240bn→£0.622690bn**, ×0.578.

The population’s upper-income distribution therefore explains substantial movement without changing the formula.

**Verified engine changes:**

| PR | Implementation SHA | Change/path |
|---|---|---|
| [#1884](https://github.com/PolicyEngine/policyengine-uk/pull/1884) | `66b7e20c3ffdaf33cf50be05f636082a6ab66381` | Robust equality in `ni_class_4_maximum.py` |
| [#1886](https://github.com/PolicyEngine/policyengine-uk/pull/1886) | `4d5b8e248420950de3c556573b13cfbf709cfbe8` | Removes Class 1 NICs deduction from trade profits |
| [#1919](https://github.com/PolicyEngine/policyengine-uk/pull/1919) | `787be8c85e59d4cd7a9a4e179a0f543b0bd049c6` | Chapter-2 profits, allowances and loss relief |
| [#1907](https://github.com/PolicyEngine/policyengine-uk/pull/1907) | `aa45dd7603bc15df5430ba9fa55541edc95a6036` | Age liability at tax-year start |
| [#1959](https://github.com/PolicyEngine/policyengine-uk/pull/1959) | `73c04593a5a1ee7ab6ca8b2054b603df5374440b` | Freezes Class 4 thresholds |
| [#2058](https://github.com/PolicyEngine/policyengine-uk/pull/2058) | `8144373dbdd7c20deb1e47faa7ab5dddf8bcc8fd` | Removes abolished Class 2 cap interaction |

Pinned files are under [variables/gov/hmrc/national_insurance/class_4/](https://github.com/PolicyEngine/policyengine-uk/tree/e89b8abcf524de48e590b9680e1a04288d30eacd/policyengine_uk/variables/gov/hmrc/national_insurance/class_4) and corresponding threshold parameters. Legacy CY2027 thresholds are £12,821.38/£51,275.32; new thresholds remain £12,570/£50,270.

**Minimal case:** £30,000 profits, no Class 1 NICs, common 2026 thresholds:

- Both formulas: 8%→6% cut **£348.60**.
- With £5,000 capital allowances, old remains **£348.60**; new correctly uses £25,000 Chapter-2 profits and gives **£248.60**.

Neither dataset supplies capital-allowance or trading-loss inputs, so this demonstrated fix cannot be assigned a national share from those inputs.

**OBR comparison:** CY2027 SB2024 NICs **−£695.737m**, versus OBR **−£724.046m**; AS2023 **−£347.609m**, versus **−£342.477m**. UC counterparts remain larger: SB2024 **+£46.350m**, versus OBR **+£12.443m**.

**Recommended action: no new issue.** Retain the fixes and document the distribution change. Numerical proximity on the NICs head does not validate omitted or differently sized counterpart heads.

## 8. Private-school VAT

**Classification: data/imputation difference is supported; an inherited statutory-policy mechanism defect persists, with calibration overlap requiring coordinated treatment.**

CY2026 dedicated VAT revenue changes **£1,292.279m→£2,022.771m**, ×1.565. OBR’s mapped VAT cell is **£1,557.694m**, so the new magnitude is 1.30 times that cell.

The key population distinction:

- Legacy supplies frozen `attends_private_school` inputs: **476,778 weighted pupils**.
- New data does **not** supply that field; the engine imputes attendance using income ranks, age and random draws.
- Under-18 population changes only **14.711m→15.116m**, +2.75%.
- The resulting new attendance count was **not independently measured** here.

[private_school_vat.py at the new pin](https://github.com/PolicyEngine/policyengine-uk/blob/e89b8abcf524de48e590b9680e1a04288d30eacd/policyengine_uk/variables/contrib/labour/private_school_vat.py) retains the pupil-count × fee × rate × basis calculation. Fee, basis, attendance factor and rate parameters do not explain a changed policy formula. **#1896**, implementation `04e85a14d2a5c5b7b072b128781f36136740abe7`, changes `is_child` to `age_under_18`; both tested definitions are age<18.

Changes to household net income can also alter newly imputed attendance ranks. Their engine contribution is unsized.

**Reconciliation with #2318.** The certified parameter `gov.contrib.labour.private_school_vat` remains **zero at current law**. The replay deliberately sets it to 20%, so a positive replay increment is consistent with a zero dedicated baseline head.

For one supplied pupil and fee £15,200, basis 0.75, both source formulas give **£0 at rate zero** and **£2,280 at 20%**. This is the model’s effective-yield proxy, not a literal VAT invoice. Statutory VAT applies from January 2025. [HMRC private-school VAT guidance](https://www.gov.uk/guidance/charging-and-reclaiming-vat-on-goods-and-services-related-to-private-school-fees).

However, **zero dedicated fee VAT does not establish missing total baseline VAT**:

- UK-data 1.58.0, SHA `4cbedbecca352f52dffe47e849553c2759a00711`, trains generic VAT imputation on ETB financial-year-ending-2024 data.
- `targets/sources/obr.py` maps generic `vat` to the **whole** OBR VAT receipts line.
- Calibration uses FY2025–26, targeting **£180.168939bn**, with no private-fee subtraction.
- OBR explicitly includes private-school VAT in receipts following the policy. Its continued inclusion in the March 2026 whole-receipts target is an inference from current-law scope; the worksheet does not separately identify it. [OBR October 2024 EFO, paragraphs 4.16–4.18](https://obr.uk/efo/economic-and-fiscal-outlook-october-2024/).

Pending local fix source, commit `ccbab58ad1a6f46d9f41b01c91adef5542b3c5ba`, documents the overlap in `policyengine_uk/data/fiscal_partition.yaml`. The actual overlap and calibration fit remain **unmeasured**.

**Recommended action:** fold into [UK #2318](https://github.com/PolicyEngine/policyengine-uk/issues/2318), coordinating with [UK-data #567](https://github.com/PolicyEngine/policyengine-uk-data/issues/567) and [#568](https://github.com/PolicyEngine/policyengine-uk-data/issues/568), referenced by the pending fix. Their live statuses are unverified. After a statutory baseline fix, revise the historical forward construction and coordinate the generic VAT target. Do not describe the replay’s £2.023bn as revenue proven absent from the total baseline.

## 9. Structural confirmation: AS2023 Class 2 abolition

**Classification: confirmed model fixes.**

The CY2027 Class 4 counterpart changes **−£786.808m→£0**.

Two fixes matter:

1. **#1884**, merge `06f36f929b7ffdad3e4e592fa125824a66a1103f`: replaces the vulnerable equality comparison in [ni_class_4_maximum.py](https://github.com/PolicyEngine/policyengine-uk/blob/e89b8abcf524de48e590b9680e1a04288d30eacd/policyengine_uk/variables/gov/hmrc/national_insurance/class_4/ni_class_4_maximum.py). Floating-point differences could wrongly drop the additional-rate band.
2. **#2058**, merge `cfee0e6b7f9ad9d1156961528adbf10c60fbb4bf`: adds `annual_maximum/includes_class_2.yaml=False` from April 2024 and removes Class 2 terms from the applicable maximum. The statutory amendment removes those terms. [2024 NI Regulations](https://www.legislation.gov.uk/uksi/2024/377/made/data.html).

**Controlled reproduction:** £100,000 profits, no Class 1 NICs:

- Legacy processed non-round thresholds and mixed floating-point types: changing weekly Class 2 from £3.70 to zero changes Class 4 **£3,281.73→£2,307.24**, a spurious **£974.49**.
- New formula and post-abolition parameters: Class 4 **£3,256.60** with either Class 2 value.

This confirms the mechanism, without independently sizing its entire national contribution.

The new direct Class 2 CY2027 cost is **−£461.694m**, versus OBR NICs **−£368.703m**; other counterpart differences remain.

**Recommended action: no issue.** Replace the legacy diagnosis with both verified fixes.

## 10. Structural confirmation: SB2024 HICBC

**Classification: confirmed model fix, with an explicit claim-resumption assumption.**

The Child Benefit counterpart changes from zero to **−£273.422m in CY2024**, reaching **−£366.873m in CY2028**.

[#2140](https://github.com/PolicyEngine/policyengine-uk/pull/2140), merge **`ea5282ae97a42bbc15eb10d9d52e86cfe1396471`**, fixes opted-out claims:

- `fdad84ca3fd2a81774211e888dc81565a64d4b22`: separates claim eligibility from the opt-out/payment gate.
- `27973b9c5bdf0ec018e69b64eaed5c107d991961`: models payment resuming when the charge fraction becomes zero.

Source: [child_benefit.py at the new pin](https://github.com/PolicyEngine/policyengine-uk/blob/e89b8abcf524de48e590b9680e1a04288d30eacd/policyengine_uk/variables/gov/hmrc/child_benefit.py) and `utils/child_benefit.py`. Opt-out inputs exist in both populations; their absence does not explain the structural change.

**Minimal controlled case:** adult with £60,000 adjusted net income, one eight-year-old, claim registered and payments opted out:

- Old formula pays **£1,354.60** under both threshold regimes: counterpart zero.
- New formula pays **£0** under £50,000–£60,000 thresholds and **£1,354.60** under £60,000–£80,000 thresholds.

Actual payments require restarting a claim; automatic resumption in the simulation is an assumption. [HMRC opt-out/restart guidance](https://www.gov.uk/child-benefit-tax-charge/stop-child-benefit).

CY2027 new Child Benefit cost is **−£321.228m**, versus OBR **−£426m**. The Income Tax head remains **−£1,288.446m**, versus OBR **−£221m**; the fix does not explain that remaining gap.

**Recommended action: no issue for the structural move.** Record #2140 and the resumption assumption. The residual Income Tax discrepancy remains an investigation question.

## Ranked risks for Budget-day costing

Ranking reflects practical costing risk, rather than an estimated correction amount.

1. **Annual Allowance:** persistent relief/charge and taper defects can materially distort pension costings. Complete #2237/#2240 and address the taper before relying on this instrument.
2. **CGT:** pooled gains cannot isolate the affected schedules, and the frozen historical reversal misses the newly modelled part-year increase. Correct the construction and expose the gains-composition limitation.
3. **Private-school VAT:** the dedicated statutory mechanism is absent while generic VAT targets whole receipts. Fix the mechanism and calibration together; avoid inferring a £2bn baseline shortfall.
4. **UC standard allowance:** missing legislated 2027–29 uplift-level increases misstate future current law and comparisons against it.
5. **UC health element:** protected amounts are understated, and the historical construction covers only part of the SS2025 package.
6. **Childcare:** the newly exposed high-cost UC tail drives substantial movement but requires an imputation/source audit. Its accuracy is **unverified**.
7. **LHA and residual HICBC Income Tax:** national discrepancies remain undecomposed. Present them as unresolved attribution and scope questions, rather than diagnosed new regressions.