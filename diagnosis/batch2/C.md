# Cluster C — Census state SPM poverty rates (3-year averages)

Batch-2 divergence diagnosis. 15 queued claims: 13 state SPM child rates where PE is 1.50–2.58x Census (TN, ME, UT, RI, VT, DE, MA, NE, WV, VA, FL, WA, NH), one state total rate (OR, 1.51x), and one child rate far below Census (MT, 0.31x).

Certified bundle: us-6.2.1 (policyengine-us 2.2.1 + `populace-us-2024-spm-20260915`, H5 sha256 `6496cc43…`, SPM selection `geography_kind: county`, scenario `ce_trend`). The bundle record came from the managed simulation itself (`pe.us.managed_microsimulation().policyengine_bundle`).

## Summary

| Item | Claims (primary) | Class | Confidence | Fix |
|---|---|---|---|---|
| C-1 Pooled 2022–2024 incomes are in nominal own-year dollars, but the engine measures them against 2024 SPM thresholds | MA, NE, WA, NH (secondary: 10 more) | `pe_gap` (split `construction_issue`) | high (mechanism), medium (size) | `pe_issue` (microcosm; comment on #646) |
| C-2 `market_income` omits partnership/S-corp income, but `spm_unit_taxes` subtracts the tax on it | TN (secondary: MA, UT, NE, WV, WA, DE, FL, OR) | `pe_gap` | high | `pe_issue` (policyengine-us) |
| C-3 Thin state samples: after the common national shift is removed, the deviations are within PE's own sampling error | ME, UT, RI, VT, DE, WV, VA, FL, OR | `construction_issue` (split `pe_gap`: data sparsity and weighting) | high (FL: medium) | `construction_fix` + `annotation` |
| C-4 Montana 0.31x: three cloned source families on about 52 effective households | MT | `construction_issue` (split `concept_mismatch`) | high | `annotation` |

**What this means for #646 (national child SPM).** The national child excess over Census (PE 15.83% vs 13.4%) splits as follows. The populace weighting adds +3.1 pp. On the same weighted records, Census's own `SPM_POOR` flag gives 16.50% child and 14.03% total, against published rates of 13.4% and 12.9%. The vintage mismatch (C-1) adds +2.6 pp and the partnership omission (C-2) adds +1.3 pp (both first-order estimates). PE's other resource differences offset these by about −4.5 pp. With both C-1 and C-2 corrected, PE is 12.0% child and 10.7% total, which is below Census. That is the direction batch 1 expected. Of the +2.3 pp by which children are worse off than the total population (relative to Census), about +2.0 pp comes from weighting, about +1.0 pp from vintage and about +0.4 pp from partnership income, offset by about −1.1 pp from other engine effects. C-1 and C-2 are resource-side defects, which is what #646 asked for. The weighting component is a data-composition finding. It is not a calibration target, because poverty stays a holdout.

## Method (all computed this session)

1. **Registry reproduction.** I ran one managed simulation and wrote person-level `in_poverty`, `is_child`, `person_weight` and `state_fips` (map_to person), plus SPM-unit resource components. The state child and total rates reproduce the registry `microcosm.budget_effect` to ≤0.0002 for every row in this cluster. The only larger residual is NC (0.006, child), which is outside the cluster. `in_poverty` is identical to `spm_unit_is_in_spm_poverty` for every person (`in_poverty.py:11-12` is `poverty_gap > 0`; `poverty_gap.py:12-15`; `spm_unit_is_in_spm_poverty.py:10-13`).
2. **Census's own flag on the same records.** The H5 person table carries the raw CPS ASEC SPM columns (`SPM_POOR`, `SPM_RESOURCES`, `SPM_POVTHRESHOLD`, `SPM_GEOADJ` and components), `source_year` (2022/2023/2024), `A_FNLWGT`, and the household `household_support_channel` (`asec` vs `puf_tax_detail` clone). PE and Census SPM units align exactly: 0 of 59,900 PE units span more than one Census `SPM_ID`. Within each unit, `SPM_POOR == (SPM_RESOURCES < SPM_POVTHRESHOLD)` holds for 100% of units. This lets me split each gap into two parts:
   - **weights**: Census `SPM_POOR` on populace weights − Census published.
   - **engine**: PE `in_poverty` − Census `SPM_POOR` on the same weighted records.
3. **Sampling error.** I computed household-cluster linearized SEs of the ratio estimator with the populace weights. I also computed the Kish effective number of child households, `(Σ w·k)² / Σ (w·k)²`, and the top-10-household share of child weight.
4. **Counterfactuals (first order).** Taxes and benefits are not recomputed.
   - (a) Own-year thresholds: PE threshold × (Census base threshold of the source year / 2024 base, by tenure).
   - (b) Add positive `partnership_income + s_corp_income + farm_rent_income + non_sch_d_capital_gains` to SPM resources.

Scripts and intermediate files are in the scratchpad `batch2-C/` (`extract.py`, `analyze.py`, `units.py`, `final_table.csv`).

## Per-claim table (pp unless noted)

`gap` = PE − Census. `wts` = Census flag on populace weights − Census. `vint` = PE − PE(own-year thresholds). `partn` = PE − PE(partnership income added). `both` = PE with both counterfactuals. `z` = (PE − Census − national bias) / PE SE, where the national child bias is +2.43 pp and the total bias is +0.16 pp. `neff` = effective child households. `top10` = % of child weight held by the 10 largest households.

| claim_id | row | Census | PE | PE SE | gap | buildo | Census flag on PE wts | wts | vint | partn | both | z | z (both) | child records / hh / SPM units | neff | top10 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|
| `fba997fbb6cfd6c39c4e` | TN child | 8.2 | 21.1 | 4.9 | 12.9 | 19.1 | 11.2 | 3.0 | 4.3 | 5.6 | 11.2 | 2.14 | 1.28 | 1015 / 489 / 491 | 74 | 24 |
| `8896cdbb8213f271fcc1` | ME child | 5.0 | 12.4 | 6.1 | 7.4 | 9.9 | 5.7 | 0.7 | 2.3 | 0.0 | 10.2 | 0.82 | 1.14 | 527 / 286 / 286 | 26 | 48 |
| `01b883e821e73bbef43d` | UT child | 5.9 | 13.2 | 3.7 | 7.3 | 14.7 | 9.8 | 3.9 | 2.4 | 1.7 | 9.2 | 1.30 | 1.43 | 888 / 403 / 403 | 78 | 21 |
| `64058ab1b6764c42b03b` | RI child | 8.1 | 16.8 | 6.4 | 8.7 | 9.7 | 19.3 | 11.2 | 3.6 | 0.8 | 12.4 | 0.98 | 0.94 | 558 / 296 / 297 | 39 | 38 |
| `55715497136e3eb9c9dc` | VT child | 8.0 | 16.4 | 7.1 | 8.4 | 19.7 | 17.3 | 9.3 | 0.0 | 0.7 | 15.7 | 0.85 | 1.29 | 290 / 158 / 158 | 42 | 36 |
| `5be90ddb7e953a22fe29` | DE child | 10.3 | 19.5 | 5.9 | 9.2 | 22.7 | 13.0 | 2.7 | 1.7 | 1.7 | 16.0 | 1.15 | 1.27 | 744 / 404 / 404 | 45 | 32 |
| `bd4ea8335108373296f7` | MA child | 11.6 | 19.9 | 4.5 | 8.3 | 15.0 | 15.4 | 3.8 | 4.4 | 2.1 | 13.4 | 1.29 | 0.86 | 1073 / 599 / 609 | 83 | 20 |
| `0e68641d4fe06928f3ed` | MT child | 8.1 | 2.5 | 1.3 | −5.6 | 11.0 | 17.5 | 9.4 | 0.5 | 0.6 | 1.4 | −6.35 | −5.65 | 482 / 258 / 258 | 52 | 32 |
| `0679c495803fff9001ca` | NE child | 6.4 | 10.7 | 4.3 | 4.3 | 9.1 | 8.8 | 2.4 | 5.5 | 2.5 | 5.2 | 0.44 | 0.06 | 880 / 414 / 414 | 51 | 30 |
| `84359f336a5104b0d41d` | WV child | 11.0 | 17.9 | 5.8 | 6.9 | 16.5 | 14.9 | 3.9 | 0.6 | 2.4 | 14.9 | 0.78 | 0.96 | 651 / 346 / 346 | 55 | 31 |
| `51fa48d774c937b2e09f` | VA child | 11.1 | 17.8 | 4.2 | 6.7 | 20.1 | 21.5 | 10.4 | 2.2 | 0.5 | 15.2 | 1.02 | 1.40 | 1156 / 593 / 595 | 83 | 20 |
| `e4a68546c4be960ea5d1` | FL child | 17.6 | 27.6 | 3.7 | 10.0 | 31.0 | 30.9 | 13.3 | 3.1 | 1.7 | 23.7 | 2.05 | 2.11 | 1193 / 625 / 627 | 149 | 15 |
| `2a005f05a8f1ab16c446` | WA child | 9.6 | 14.7 | 4.4 | 5.1 | 13.6 | 12.5 | 2.9 | 2.5 | 1.9 | 10.3 | 0.62 | 0.56 | 992 / 503 / 503 | 68 | 24 |
| `5af425967764dab64322` | OR total | 11.1 | 16.8 | 3.0 | 5.7 | 18.3 | 18.7 | 7.6 | 2.0 | 0.8 | 14.1 | 1.84 | 1.85 | 3349 / 1152 / 1230 (persons) | 155 | 11 |
| `c89efbc4ffd24fb15cf3` | NH child | 7.0 | 10.5 | 3.8 | 3.5 | 9.2 | 9.2 | 2.2 | 3.8 | 0.0 | 6.7 | 0.29 | 0.35 | 586 / 312 / 312 | 43 | 36 |
| (context) `02ce16f73ff66b8dd767` | US child | 13.4 | 15.8 | 0.7 | 2.4 | 17.2 | 16.5 | 3.1 | 2.6 | 1.3 | 12.0 | — | — | 45917 / 23407 / 23461 | 2919 | 1 |
| (context) `2fb69d82a3df911ce693` | US total | 12.9 | 13.1 | 0.4 | 0.2 | 13.9 | 14.0 | 1.1 | 1.6 | 0.9 | 10.7 | — | — | 166321 persons | 8156 | 1 |

The `buildo` column is the per-release history in `data/populations.json`. Except for MT, every high state was also high under Build O (engine 1.764.6), so the pattern is not new to spm-20260915. MT moved from 11.0% to 2.5%.

## Answers to the key questions

**(1) Is this the same child-concentrated excess as #646?** Partly, yes. Across all 51 states, the mean of (PE child − PE total) is +2.17 pp, against −0.01 pp for Census. The common national child shift (+2.43 pp) is present in every state row. The national total shift is only +0.16 pp. This is the #646 pattern. For OR, the excess is in the total rate (+5.7 pp) more than the child rate (+2.5 pp, not queued), so OR is not child-concentrated. Its gap is mostly weighting (+7.6 pp).

**(2) Is this small-state noise or systematic bias?** Mostly noise around a systematic national shift.
- In the queued states, the effective child sample is 26–149 households. The 10 largest households hold 11–48% of child weight. The PE SEs of the child rates are 3.7–7.1 pp, against Census rates of 5–18%.
- After the national bias is removed, 12 of the 14 high-side rows have |z| < 2. The exceptions are TN (2.14) and FL (2.05). Among 51 states, about 2.6 rows at |z| > 1.96 are expected by chance.
- Child rates, all states: chi² of the centred z = 99.4 on 50 df. Without MT it is 59.1 on 49 df (p = 0.15), which is consistent with sampling noise. If a Census SE of 1.5 pp is added (Census MOEs were not extracted, see Limitations), chi² = 66.4 on 50 df including MT.
- Total rates: chi² = 78.7 on 50 df with Census SE = 0, and 51.7 on 50 df with Census SE = 1.5 pp. OR (z = 1.84) is not an outlier.
- The weighting component alone is also consistent with noise around its national value of +3.1 pp: chi² = 53.7 on 50 df, p = 0.33. 44 of 51 states are positive.
- The queue rule |ratio − 1| ≥ 50% selects on noise in low-rate states. When the Census rate is 5–8%, a 2.4 pp common shift plus one SE of noise gives a ratio above 1.5.

**(3) Construction.**
- Each row is a person-level weighted share. The registry computes `in_poverty` mapped to persons, sets `mask_variable: is_child` (`is_child.py:10-11` is `age < 18`), and slices by `state_fips` mapped to persons (microcosm `reform_validation.py:933-982`, state slice at `:973-977`).
- The period is single-year 2024. The benchmark is the Census P60-287 2022–2024 three-year average. The config comment states this caveat (`state_spm_poverty_levels.json:2`, MT row at `:856-868`).
- The simulation declares county SPM geography (`reform_validation.py:672-684`, used at `:700-716`). The engine reads each household's `county_fips` for the SPM threshold (`policyengine_us/spm.py:251-252`), so each state rate uses its own records' county adjustments. These match Census: the child-weighted median of the PE geographic factor / Census `SPM_GEOADJ` is 0.997, 0.997 and 1.000 for source years 2022, 2023 and 2024.
- The threshold *year* does not match. The child-weighted median of PE threshold / Census threshold is 1.137 for 2022, 1.058 for 2023 and 1.004 for 2024.
- For 2-adult/2-child units, the PE 2024 base thresholds are 39,220 (renters), 39,231 (owners with mortgage) and 32,879 (owners without mortgage). The Census base thresholds on the same units are 34,518 / 37,482 / 39,430 for renters in 2022 / 2023 / 2024.
- The pooled H5 already spans the 3-year window, with child weight shares of 34.1% / 31.8% / 34.1% for 2022 / 2023 / 2024. The mismatch is therefore not "one year vs three years". It is that 2022 and 2023 incomes are tested against 2024 thresholds (C-1).

**(4) Why is Montana so low?** See C-4. Three source families (each also present as a PUF clone) hold 14.75 pp of MT child weight. Census flags all three as poor and PE flags none.

## C-1 — Pooled income years stay in nominal dollars, but thresholds are 2024 (`pe_gap`, split `construction_issue`)

**Finding.** Build P pools ASEC income years 2022–2024. microcosm documents that it does not restate their dollars: `docs/us-asec-source-pins.md:216-220` says the pooled tables carry nominal dollars of each income year and no build stage restates them by source year. microcosm `docs/us-spm-role-stage.md:144` names the Build P vintages as income years 2022-2024.

I confirmed this on the certified H5:
- On ASEC-channel units, the median of PE (`market_income` + Social Security + SSI + UC) / Census `SPM_TOTVAL` is 1.0000, 0.9999 and 0.9999 for 2022, 2023 and 2024.
- Wage inputs equal `WSAL_VAL` for 100% of ASEC-channel adults and 99.9% of PUF-clone adults.
- The engine prices every unit at 2024 thresholds (ratios above).

The 2022-income records (34% of child weight) therefore meet a threshold 13.7% higher than the one Census used for them. The 2023 records meet one 5.8% higher.

**Size (first order).**
- By source year (2022 / 2023 / 2024), the PE child rate is 17.2 / 14.6 / 15.6 and the Census flag on the same records is 15.4 / 17.5 / 16.6. Only the 2022 records exceed the Census flag.
- With own-year thresholds, the national child rate falls 15.83 → 13.24 and the total rate falls 13.06 → 11.48.
- Per queued state, the effect is 0–5.5 pp (table, `vint`). In ME, all PE-only poor children (6.7 pp of child weight) are in 2022-source records.

This is a first-order estimate. Benefits and taxes are computed at 2024 law on nominal income, and they are not recomputed. Uprating income instead of deflating thresholds would use an income-growth factor, not SPM-threshold growth. For the single-year national row, the right factor is open.

**Why it is `pe_gap`.** The H5's dollar vintage is a data-construction choice that biases every threshold-based 2024 output. The `construction_issue` split applies to the 3-year rows only: a like-for-like 3-year construction would test each record against its own source-year threshold.

**Fix draft (microcosm issue, link from #646).** Title: "Pooled ASEC income years enter the US H5 at nominal own-year dollars; SPM poverty tests them against 2024 thresholds". Body:
- the doc lines above;
- the three median ratios (income/`SPM_TOTVAL` ≈ 1.000 for each year; PE/Census threshold 1.137 / 1.058 / 1.004);
- the counterfactual (national child −2.59 pp, total −1.58 pp);
- the note that a pool whose *mean* income year equals the target year (the new 2023–2025 default) still biases threshold-based rates, because poverty is nonlinear in income.

Options: (a) age pooled-year dollar inputs to the target year at build time; (b) evaluate SPM status against source-year thresholds in the 3-year backtest rows. A test must use an external ground truth: the Census `SPM_POOR` flag on the ASEC-channel records should be reproduced within a stated tolerance by year.

## C-2 — SPM resources leave out partnership/S-corp income but subtract the tax on it (`pe_gap`)

**Finding.**
- `market_income` (`variables/household/income/person/general/market_income.py:13-29`) does not list `partnership_s_corp_income`, `farm_rent_income` or `non_sch_d_capital_gains`.
- All three are IRS gross-income sources (`parameters/gov/irs/gross_income/sources.yaml:7,9,12`). `partnership_s_corp_income` adds `partnership_income` and `s_corp_income` (`partnership_s_corp_income.py:11`).
- `spm_unit_net_income` adds market income and benefits, and subtracts `spm_unit_taxes` and expenses (`spm_unit_net_income.py:11-18`). `spm_unit_taxes` includes `spm_unit_federal_tax` (`spm_unit_taxes.py:11-17`), which sums `income_tax` (`spm_unit_federal_tax.py:11-12`).
- A family with partnership income therefore loses the tax on that income but never gets the income.

**Evidence (records).** These are TN PUF-clone households.
- Household 1031181: `partnership_income` $341,300; PE federal tax $68,920 against $110,802 market income; SPM resources $7,634; Census resources for the source family $107,498.
- Household 1030751: `partnership_income` $287,010; federal tax plus SE tax $51,891 against $11,408 market income; resources −$17,378.
- Household 1087066: `partnership_income` $99,700.

Nationally, adding these incomes back moves the child rate 15.83 → 14.52 (total 13.06 → 12.18). This is entirely in the PUF-clone channel: clone children go 13.10 → 10.87 and ASEC children are unchanged. For TN it is 5.6 pp, which is the largest single component of TN's 12.9 pp gap. With C-1 and C-2 both corrected, TN = 11.2%. That equals the Census flag on the same records (11.2%), and the remaining +3.0 pp vs published is within one SE (4.9 pp).

**Fix draft (policyengine-us issue).** Title: "SPM net income subtracts tax on partnership/S-corp, farm rent and non-Schedule-D gains but never adds the income". Body:
- the five file:line cites above and the three household examples.

Proposed change: add `partnership_s_corp_income` (and review `farm_rent_income`, `non_sch_d_capital_gains`) to `market_income`, or to `spm_unit_market_income` only if broader `market_income` consumers must stay unchanged. The PR must list every consumer of `market_income`. Tests: a household with partnership income only must get positive SPM resources equal to income minus the computed taxes. Search existing issues before filing.

## C-3 — Thin state samples around a common shift (`construction_issue`, split `pe_gap`)

**Finding.** For ME, UT, RI, VT, DE, WV, VA, FL and OR, no state-specific engine defect is supported. Each gap is the national shift (C-1, C-2, weighting) plus sampling error from 26–155 effective households. After centring, the z values are 0.8–1.8, except FL at 2.05. In RI, VT, VA, FL and OR, the largest component is *weighting*: Census's own SPM flag on our weighted records is 7.6–13.3 pp above the published rate. For these states, the engine is actually *below* the Census flag on the same records (engine −0.9 to −3.6 pp).

FL (z = 2.05, weighting z ≈ 2.6) is the one weighting outlier:
- The FL ASEC-channel children kept in the sparse sample are very poor by Census's own flag: 40.3% on populace weights and 37.5% on `A_FNLWGT`.
- These records carry 39% of FL child weight.

This is a sample-composition property of the build, so confidence for FL is medium.

**Fix draft.**
- (a) **construction_fix** in microcosm `reform_validation.py` `_person_rate`: emit a household-cluster linearized SE and the effective household count with every `statistic="rate"` row. The scorecard can then queue on |z| instead of |ratio − 1| ≥ 50%.
- (b) **Annotation** for the nine rows: "PE's state child (or total) SPM rate rests on about N effective households (PE SE ≈ X pp). After the national shift tracked in #646 is removed, the gap is within sampling error. Census's own SPM flag on the same weighted records is Y%. Do not read this row as a state-specific model defect."

## C-4 — Montana 0.31x (`construction_issue`, split `concept_mismatch`)

**Finding.** PE's 2.5% MT child rate comes from 22 households (40 child records). Census's own flag on the same weighted records is 17.5%, which is above Census's published 8.1%. Twenty source families make up that 17.5%. Three of them, each duplicated as an ASEC record plus a PUF clone, hold 14.75 pp. PE flags none of the three as poor:
1. **SPM_ID 101735 (2023 source, 9 persons, 7 children; households 96756 and 1096756; 8.6 pp).** Census resources are $49,516 against a $51,674 threshold. PE net income is $62,912 against $55,110. The difference is mainly PE's modeled SNAP, $18,828 vs $9,276 reported, plus school meals of $5,175 vs $4,110. This is PE's benefit modeling of a reported-low recipient, not a defect.
2. **SPM_ID 160075 (2024 source; households 40642 and 1040642; 4.6 pp).** Census `SPM_RESOURCES` = −$47,552. Census federal tax $315,555 and state tax $60,061 exceed money income `SPM_TOTVAL` $356,550, because `CAP_VAL` = 999,999 (topcoded capital gains) is taxed but is not money income. Census therefore counts this family as SPM-poor. PE counts the capital gains in market income ($1.33M) and gets net income of $945k. This is a Census-side measurement convention: `concept_mismatch`.
3. **SPM_ID 160106 (PUF clone 1040672; 1.5 pp).** The clone has $124k market income against $78k for its source.

The MT estimate rests on about 52 effective households, and it moved from 11.0% (Build O) to 2.5% when the sparse selection changed. The linearized SE (1.3 pp) understates the uncertainty when so few poor records exist. C-1 and C-2 barely matter for MT (0.5 pp and 0.6 pp).

**Fix draft (annotation).** "Montana's PE child SPM rate (2.5%) rests on about 52 effective households. Three source families hold 14.75 pp of MT child weight. Census flags them as poor and PE does not: one through PE's modeled SNAP, and one whose Census SPM resources are negative because taxes on topcoded capital gains exceed money income. The value moved from 11.0% (Build O) to 2.5% between releases. Treat it as sampling-limited, not as evidence of an MT-specific model gap."

## Limitations

- Census 3-year MOEs were not extracted. The files are not stored locally and I did not download them. The noise tests use PE-side SEs only; including Census MOE would only lower the z values. The only Census rates quoted are the registry values.
- The C-1 and C-2 counterfactuals are first-order: taxes and benefits are not recomputed. A full rerun with aged inputs and corrected `market_income` is the confirming test.
- For PUF clones, the "Census flag on populace weights" is the source ASEC family's flag. Clone wages equal the source wages, but some other income items differ by design (for example, partnership income).
- The registry construction says per-state person and child counts are calibrated (`state_spm_poverty_levels.json:2`). I did not verify that against the target surface.
- After both counterfactuals, the dispersion of the state child rates exceeds noise (chi² 187 on 50 df), driven by states far *below* Census (AR, MS, LA, KY, HI). These are outside this cluster and are worth a separate look.
- Tooling observation (not verified as a bug): `sim.calculate("state_fips" | "household_id", 2024, map_to="spm_unit")` returned values misaligned with the H5 for 9% of SPM units, including non-integer household ids, although SPM units nest in households. Person-level mapping, which the registry uses, was exact. I used H5 ids for all unit-level joins.
