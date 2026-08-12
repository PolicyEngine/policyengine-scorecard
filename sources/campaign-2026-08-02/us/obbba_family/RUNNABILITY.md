# OBBBA family (JCX-35-25 Title VII) — per-provision PE runnability verdicts

Date: 2026-08-02. Scope: Chapter 1 (TCJA extension/enhancement) + Chapter 2
(new individual provisions), FY2026 conventional values from staged JCX-35-25
rows. Convention caveat that applies to EVERY row: JCT estimates provisions
SEQUENTIALLY (each conditional on the prior stack); single-provision PE runs
score marginal-vs-current-law — interaction terms are a named convention
delta until a full-stack replication is built (follow-up design).

Verdict key: PARAMETRIC (paths verified in installed tree) ·
PARAMETRIC-PENDING (modeled; expiry-world values need sourcing, e.g. CBO
Jan-2025 Tax Parameters projections) · STRUCTURAL (needs contrib/structural
reform) · CHECK (model surface unverified) · OUT (not in a household
static microsim).

## Chapter 1 (extension provisions; counterfactual = TCJA-expiry world)
| # | Provision | FY2026 ($M) | Verdict |
|---|-----------|------------|---------|
| 1 | Reduced rates extension | −147,679 | STRUCTURAL — expiry rates 15/25/28/33/39.6 with CBO-projected 2026 thresholds already embedded in gov.contrib.additional_tax_bracket defaults; usable as the expiry-world engine |
| 2 | Standard deduction extension+enhancement | −92,124 | PARAMETRIC-PENDING — gov.irs.deductions.standard.*; expiry-2026 values need CBO projection sourcing |
| 3 | Personal exemption termination (excl. senior deduction) | +110,625 | PARAMETRIC-PENDING — gov.irs.income.exemption.amount (0 now); expiry value ≈ CBO-projected; senior-deduction carve-out is separate current-law param |
| 4 | CTC extension+enhancement | −48,769 | **PARAMETRIC (verified)** — full surface pinned today (cpsp/tpc lanes); expiry world = the tree's own 2013-dated statute values (unindexed pre-TCJA law): base 1000, ODC 0, refundable max 1000, phase-in threshold 3000, phase-out 110k/75k/55k. RUNNER: comparison/obbba_family.py ctc_ext |
| 5 | QBI deduction | −44,331 | CHECK — pe-us models QBI (gov.irs.deductions.qbi.*); expiry = repeal (0); enhancement params to verify |
| 6 | Estate/gift exemption | −3,672 | OUT — no estate tax in household microsim |
| 7 | AMT exemption extension | −76,835 | PARAMETRIC-PENDING — gov.irs.income.amt.exemption.*; expiry values need CBO projection |
| 8 | Residence interest limitation | +1,639 | CHECK — mortgage-interest itemized surface + data coverage |
| 9 | Casualty loss limitation | +86 | CHECK/weak — thin data |
| 10 | Misc itemized termination | +13,419 | CHECK — 2%-floor deduction modeling coverage |
| 11 | Itemized-benefit limitation (2/37) | −16,040 | PARAMETRIC-PENDING — OBBBA's limitation is current law in pe-us; repeal switch to verify |
| 12-14, 18 | fringe/moving/wagering/Sinai | small | OUT/skip — immaterial or unmodeled |
| 20 | SALT cap | +31,617 | PARAMETRIC-PENDING — gov.irs.deductions.itemized.salt_and_real_estate.cap; expiry = uncapped |

## Chapter 2 (new provisions; counterfactual = repeal from current law)
| # | Provision | FY2026 ($M) | Verdict |
|---|-----------|------------|---------|
| 1 | No tax on tips (sunset 12/28) | −10,121 | PARAMETRIC-PENDING — gov.irs.deductions.tip_income.* seen in tree; repeal switch to verify; data: reported tip income |
| 2 | No tax on overtime (sunset 12/28) | −32,806 | PARAMETRIC-PENDING — gov.irs.deductions.overtime_income.* + gov.irs.income.exemption.overtime.* present; **note memory: PE has no hours/participation machinery — overtime amounts are imputed data; state the data basis in any comparison** |
| 3 | No tax on car loan interest | −5,400 | CHECK — auto-loan-interest deduction surface + data |
| 4 | Trump accounts | −6,446 | OUT — new account vehicle, no microsim surface |

## First runnable leg queued
`ctc_ext` (provision 4): current law − CTC-expiry world, 2026. Every expiry
value read from the installed tree's own 2013-dated statute entries at
runtime (fail-loud pins). Baseline for delta: results/us/tpc_ctc/baseline_2026.
Convention deltas named: sequential-stack vs marginal; FY-cash vs CY-liability.

## Stack baselines = baseline definitions (Max ruling 8/2)
The "sequential-stack vs marginal" caveat above is resolvable, not inherent:
JCT's baseline for provision k is expiry-world + provisions 1..k-1 — a
constructible first-class baseline ReformRef per issue #13. Build once from
the CBO Jan-2025 Tax Parameters expiry-2026 projections (workbook already
cited in gov/contrib/additional_tax_bracket/bracket.yaml): expiry values for
std deduction, personal exemption, AMT exemption/phaseout, QBI repeal, SALT
uncap, misc itemized, Pease. Then every Ch1 provision scores at its true
stack position. The ctc_ext run stands as the LAST-IN-STACK variant
(vs full current law) — a different well-defined baseline, published as such.
