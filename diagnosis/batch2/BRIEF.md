# Divergence diagnosis batch 2 — US reform-validation registry

Same discipline as batch 1 (`diagnosis/BRIEF.md`): defensive audit — FIRST ask what would make our number wrong, then theirs. One primary class per item (optional split): `pe_gap`, `external_model_issue`, `concept_mismatch`, `data_vintage`, plus `construction_issue` when the registry's own scoring construction (period, baseline world, stacking order, sign, scope) does not match the claim. Unevidenced classifications stay `open`.

**Evidence rule (binding):** cite engine file:line (policyengine-us 2.2.1 at `.venv-pe/lib/python3.12/site-packages/policyengine_us/`), microcosm code (`/Users/pavelmakarchuk/microcosm` @ 581b569, esp. `packages/microcosm-build/src/microcosm/build/us_runtime/reform_validation.py`), the registry row (`sources/populace-reform-validation/raw/populace-us-2024-spm-20260915.json`: each row's `jct` = external claim and `microcosm` = PE block), the claim in `data/populations.json` (per-release history), a named official series/document, or a computation you ran this session. Do NOT describe a mechanism you have not read this session. Engine outputs generate hypotheses, never evidence for what a statute or document says.

**PE values:** certified bundle us-6.2.1 = policyengine-us 2.2.1 + `populace-us-2024-spm-20260915` (a source enrichment of Build P), produced by microcosm's post-export probe (see the raw file's `_backfill_note`). Earlier per-release values (buildi/j/o, l0-refit, f0af251) are in each claim's `results` in `data/populations.json` — use them to separate data/engine drift from construction issues.

**Compute:** small targeted calculations are allowed with `.venv-pe/bin/python` + `policyengine.pe.us.managed_microsimulation()` (one simulation at a time; free it before the next), and direct reads of input columns from `data/populace_us_2024.h5`. No git commits, no network posting.

**Output per cluster:** `diagnosis/batch2/<cluster>.md` (memo: per item finding, class, confidence, evidence, fix draft) and `diagnosis/batch2/<cluster>.json` — a list of items `{claim_ids: [...], title, classification, split, confidence, evidence: [...], fix_type: pe_issue|annotation|upstream_memo|construction_fix|none, fix_draft}`. Group claim_ids that share one root cause into one item.

## Queue (|PE/external − 1| ≥ 50% or PE = 0 on spm-20260915)

### A. JCT OBBBA provision scores (JCX-35-25)

| claim_id | source | claim | external | PE | ratio | window |
|---|---|---|---:|---:|---:|---|
| `ecb717a9acc4a1b38078` | jct | 5. 0.5 percent floor on deduction of contributions made by individuals | 1.346e+09 | 7.44e+09 | 5.53 |  |
| `0b9f7c2b76e0753b5f75` | jct | 5. Enhancement of child and dependent care tax credit [1] | -4.09e+08 | -1.548e+09 | 3.79 |  |
| `2b90f7cd21917bcf9730` | jct | 9. Extension and modification of limitation on casualty loss deduction [1] | 8.6e+07 | 2.901e+08 | 3.37 |  |
| `8c39fd4f728cdc2a89f9` | jct | 8. Extension of limitation on deduction for qualified residence interest [1] | 1.639e+09 | 4.092e+09 | 2.50 |  |
| `1cb8833f070d370af65f` | jct | 4. Permanent and expanded reinstatement of partial deduction for charitable cont | -1.543e+09 | -3.516e+09 | 2.28 |  |
| `03d90cf1164672f10599` | jct | 9. Extension and modification of limitation on casualty loss deduction [1] | 1.28e+08 | 2.901e+08 | 2.27 |  |
| `71c9d1d62387ef6b688d` | jct | 6. Extension and enhancement of increased estate and gift tax exemption amounts | -3.672e+09 | 0 | -0.00 |  |
| `3244357bc57dbb8f68a4` | jct | 6. Extension and enhancement of increased estate and gift tax exemption amounts | -2.028e+10 | 0 | -0.00 |  |
| `a822378f6be2661eb525` | jct | 20. Limitation on individual deductions for certain State and local taxes [1] | 3.162e+10 | 6.198e+10 | 1.96 |  |
| `cf49ed4913b68459b9b0` | jct | 3. No tax on car loan interest | -8.07e+09 | -1.083e+09 | 0.13 |  |
| `3dd3cd4f14af2d46bd66` | jct | 7. Extension of increased alternative minimum tax exemption amounts, modificatio | -7.684e+10 | -1.421e+11 | 1.85 |  |
| `01304f138bf44f724ef0` | jct | 4. Extension and enhancement of increased child tax credit [1] | -4.877e+10 | -8.981e+10 | 1.84 |  |
| `73ef6ebfd109b05e4d60` | jct | 1. No tax on tips (sunset 12/31/28) [5] | -1.012e+10 | -1.929e+09 | 0.19 |  |
| `17ba03f21f372df6c315` | jct | 3. No tax on car loan interest | -5.4e+09 | -1.083e+09 | 0.20 |  |
| `f227bd9991831f737066` | jct | 1. No tax on tips (sunset 12/31/28) [5] | -7.664e+09 | -1.929e+09 | 0.25 |  |
| `85abfca7dfcd7c68d978` | jct | 4. Permanent and expanded reinstatement of partial deduction for charitable cont | -7.791e+09 | -3.516e+09 | 0.45 |  |

### B. JCT tax expenditures and IRS SOI income-tax aggregates

| claim_id | source | claim | external | PE | ratio | window |
|---|---|---|---:|---:|---:|---|
| `4c1e51a09563b19229d8` | jct | jct.tax_expenditures.cy2024.self_employed_pension_contribution_deduction.revenue | 1.66e+10 | 2.069e+08 | 0.01 | annual |
| `788712a4db74edbd1398` | irs_soi | Education credits (nonrefundable) | 7.555e+09 | 7.802e+08 | 0.10 | TY2023 |
| `db63c233d9e3d2e33f86` | jct | jct.tax_expenditures.cy2024.traditional_ira_deduction.revenue_loss | 1.6e+10 | 3.133e+09 | 0.20 | annual |
| `000c6065155be0232de2` | jct | jct.tax_expenditures.cy2024.health_savings_account_deduction.revenue_loss | 1.22e+10 | 3.125e+09 | 0.26 | annual |
| `0bd035cc14714f0a289a` | jct | jct.tax_expenditures.cy2024.self_employed_health_insurance_deduction.revenue_los | 8.4e+09 | 2.379e+09 | 0.28 | annual |
| `705dc2ffcbb72e8915a0` | irs_soi | Alternative minimum tax | 2.752e+09 | 4.394e+09 | 1.60 | TY2023 |

### C. Census state SPM poverty rates (3-year averages)

| claim_id | source | claim | external | PE | ratio | window |
|---|---|---|---:|---:|---:|---|
| `fba997fbb6cfd6c39c4e` | census | Tennessee SPM child poverty rate | 0.082 | 0.2112 | 2.58 | 2022-2024 3-year average |
| `8896cdbb8213f271fcc1` | census | Maine SPM child poverty rate | 0.05 | 0.1245 | 2.49 | 2022-2024 3-year average |
| `01b883e821e73bbef43d` | census | Utah SPM child poverty rate | 0.059 | 0.1321 | 2.24 | 2022-2024 3-year average |
| `64058ab1b6764c42b03b` | census | Rhode Island SPM child poverty rate | 0.081 | 0.1678 | 2.07 | 2022-2024 3-year average |
| `55715497136e3eb9c9dc` | census | Vermont SPM child poverty rate | 0.08 | 0.1642 | 2.05 | 2022-2024 3-year average |
| `5be90ddb7e953a22fe29` | census | Delaware SPM child poverty rate | 0.103 | 0.1953 | 1.90 | 2022-2024 3-year average |
| `bd4ea8335108373296f7` | census | Massachusetts SPM child poverty rate | 0.116 | 0.1987 | 1.71 | 2022-2024 3-year average |
| `0e68641d4fe06928f3ed` | census | Montana SPM child poverty rate | 0.081 | 0.02531 | 0.31 | 2022-2024 3-year average |
| `0679c495803fff9001ca` | census | Nebraska SPM child poverty rate | 0.064 | 0.1071 | 1.67 | 2022-2024 3-year average |
| `84359f336a5104b0d41d` | census | West Virginia SPM child poverty rate | 0.11 | 0.1793 | 1.63 | 2022-2024 3-year average |
| `51fa48d774c937b2e09f` | census | Virginia SPM child poverty rate | 0.111 | 0.1784 | 1.61 | 2022-2024 3-year average |
| `e4a68546c4be960ea5d1` | census | Florida SPM child poverty rate | 0.176 | 0.2759 | 1.57 | 2022-2024 3-year average |
| `2a005f05a8f1ab16c446` | census | Washington SPM child poverty rate | 0.096 | 0.1473 | 1.53 | 2022-2024 3-year average |
| `5af425967764dab64322` | census | Oregon SPM poverty rate | 0.111 | 0.168 | 1.51 | 2022-2024 3-year average |
| `c89efbc4ffd24fb15cf3` | census | New Hampshire SPM child poverty rate | 0.07 | 0.1052 | 1.50 | 2022-2024 3-year average |

### D. State credit costs (admin actuals and fiscal notes)

| claim_id | source | claim | external | PE | ratio | window |
|---|---|---|---:|---:|---:|---|
| `03d666ddda6fe83bd6f4` | co_admin | Colorado Child Tax Credit | 8.916e+07 | 2.009e+08 | 2.25 | TY2023 |
| `e3eb837aef9d9269a700` | ia_fiscal_note | IA HF1020 — child and dependent care credit expansion | -1.77e+07 | -1.836e+06 | 0.10 | FY2026 |
| `4bac6a16f6267328daf0` | oh_admin | Ohio EITC (30% nonrefundable) | 5.93e+07 | 1.089e+08 | 1.84 | FY2025 (TY2024 proxy) |
| `a4ac9f4bd35f476eee27` | co_admin | Colorado Family Affordability Credit (refundable) | 6.54e+08 | 1.151e+09 | 1.76 | TY2024 (implied) |
| `e598532e06e1a4b95e8f` | md_admin | Maryland Child Tax Credit | 1.38e+07 | 2.408e+07 | 1.74 | FY2024 |
| `e053f2018d75bd10cecc` | il_admin | Illinois Child Tax Credit | 5e+07 | 7.944e+07 | 1.59 | TY2024 |
| `901232245430396bdea5` | mn_admin | Minnesota Working Family Credit | 1.915e+08 | 2.896e+08 | 1.51 | TY2024 |
| `bd2894a6bf3d1e1eda0d` | id_admin | Idaho Child Tax Credit ($205/child nonrefundable) | 6.396e+07 | 9.666e+07 | 1.51 | CY2024 (revised) |
| `9eda40b94ca5ce924e04` | ca_admin | California Young Child Tax Credit | 4.13e+08 | 6.219e+08 | 1.51 | TY2023 |
