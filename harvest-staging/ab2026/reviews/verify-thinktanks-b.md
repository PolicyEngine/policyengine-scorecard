# Verification: `uk_niesr`, `uk_fai_sfc`, `uk_thinktank_misc`, `uk_devolved_govts` (#230 → PR #231)

**Three required checks were not run.** This session had only read, search and web tools: no shell and no Python. So I could not:

- recompute any sha256;
- run `pipeline/ab2026_harvest_contract.py`;
- decompress any `claims_staged.jsonl.gz`.

Instead I rebuilt each row from the family's `stage.py`, which each NOTES says reproduces the gzip byte for byte. I then checked those rows against the saved primaries in `.ab2026-primaries/` and against the contract code by reading it. Row indices are 0-based in `stage.py` emission order; each family's NOTES numbers its rows from 1. **Before merging, the coordinator should run these three commands for each family:**

1. `shasum -a 256` on each primary;
2. the contract checker;
3. the gzip-vs-`stage.py` comparison.

By my reading of the code, the checker should report 0 problems for all four families.

## Verdicts

| Family | Rows | Verdict |
|---|---:|---|
| `uk_niesr` | 0 | **APPROVE** (one optional NOTES wording fix) |
| `uk_fai_sfc` | 5 | **APPROVE WITH FIXES** |
| `uk_thinktank_misc` | 13 | **APPROVE WITH FIXES** |
| `uk_devolved_govts` | 14 | **APPROVE WITH FIXES** |

**Design rows (rule 8): none in any family.** All design figures the primaries print were correctly left out:

- the £100 payment in the Welsh and Scottish statements;
- the Welsh £14bn rail commitment and £302m allocation;
- NIESR's £7.4bn DMO financing remit;
- IfG's £1bn cut-off, which is kept in conditions.

**Identity tests (`uk_devolved_govts`, Table 1): all pass.** Resource plus Capital equals Total in every year: 199−27=172, 165−19=146, 146+2=148, and N/A plus −18 gives −18. The four Totals sum to the headline: 172+146+148−18 = 448. For the Scottish Government rows, 550+100 = 650. No failures.

## Findings, most serious first

### 1. `uk_thinktank_misc` row 3: the CPS proposed package can't be registered and should be removed
- **What's wrong:** the CPS sentence names no Table 6.1 or Table 6.2 lines and no years, and it ties the figure to a CPS paper from before the Budget. So the figure is about the government's whole Public Financial Institutions (PuFins) channel, not about AB2026 decisions. Tranche 2 has nothing it could register.
- **Evidence:** `cps.html` line 262, Herring paragraph: "By channelling investment into Public Financial Institutions (PuFins), Labour is increasing debt by £3.1 billion each year … As we noted in our CPS paper released last week".
- **Fix:**
  - row 3: delete `conditions.proposed_measure_key`;
  - set `reform_hint` to `null`;
  - add `conditions.measure_type`: "debt increase from channelling investment into Public Financial Institutions (PuFins), as asserted by CPS";
  - keep `measure_key: null`, and rewrite `note` so it no longer says "line membership is unresolved";
  - NOTES.md: replace the "One measure key is proposed" bullet with "No measure key is proposed", and record that the row is context;
  - the coordinator should leave `ab2026__package_cps_public_financial_institutions` out of PROPOSED_KEYS.md.

### 2. `uk_devolved_govts` rows 0–11: totals and components share one key, and nothing tells them apart
- **What's wrong:** rows 0–11 all carry `ab2026__package_welsh_settlement_changes`, and each sets `conditions.component` to Resource, Capital or "Total". No row sets `row_type`. An ingest that groups by key and fiscal year would add Resource, Capital and Total together. This breaks the rule 9 principle that components are never summed with their total. The `uk_hmt_tables` convention is `row_type` set to `total` or `measure_component`.
- **Evidence:** Table 1 in `welsh-response.html` line 248; the identities above show the components already sum to the Totals.
- **Fix:**
  - rows 1–7 (Resource and Capital): add `conditions.row_type: "measure_component"`;
  - rows 0 and 8–11: delete `conditions.component` and add `conditions.row_type: "total"`;
  - row 0 is already `value_kind: cumulative`, which separates it from rows 8–11.

### 3. `uk_devolved_govts` rows 0–11: the Welsh package is registrable, but the key should name the scope, not the nation
- **Scope is clear enough to register:**
  - the producer's words are "Changes to the Welsh Government Settlement" and "an additional £448m of funding over the current spending review period";
  - it excludes "changes as a result of employer pension contribution savings";
  - the figures are split into resource and capital, for 2026-27 to 2029-30;
  - this is a devolved-government consequential (rule 8), and rule 9 lets a package have no Table 6.1 lines.
- **What's wrong:** the NOTES text "may contain the consequences of spending announcements beyond a simple sum of Table 6.1 lines … unresolved mapping" is vague. Also, putting the nation in the slug breaks rule 2's "slug names the scope … so that producers with the same scope share one key". HM Treasury's devolved-funding figures and any Scottish or Northern Ireland block-grant figure could never share it. Rule 9 treats a nation as a condition or part, not as the scope.
- **Fix:**
  - set `conditions.proposed_measure_key` to `ab2026__package_barnett_consequentials` (the coordinator chooses the final spelling);
  - keep `geography: "Wales"` and `exclusion`;
  - NOTES "Scope and proposals": state the scope as "change in a devolved government's block grant from UK Government decisions at AB2026, by resource and capital, as the producer prints it; nation in `conditions.geography`; the Welsh rows exclude employer-pension-contribution savings";
  - delete the "unresolved mapping" sentences.
- **Coordinator check:** if `uk_hmt_redbook` stages HM Treasury's devolved funding table, align with that family's key. Also decide whether these rows should be `restated` with `conditions.originator: "HM Treasury (Barnett formula)"`. AB2025 `uk_fai_sfc` marked HM Treasury's Barnett table `restated`. The Welsh page cites no source, so `own` can be defended. This is a judgement call, not a defect.

### 4. `uk_fai_sfc` rows 0–4 and `uk_devolved_govts` rows 12–13: one metric name now covers two concepts with opposite signs
- **What's wrong:** AB2025 used `block_grant_effect` to mean a policy's effect on the grant, with "positive = increase in … funding". These 7 rows use it for a year-on-year real-terms change in the whole settlement, with "positive = magnitude of reduction". Welsh rows 0–11 use the same proposal with the AB2025 sign, so the one proposal now carries both meanings.
- **Evidence:**
  - `scottish_government_budget_response.html` lines 347–348: "real terms cut … around £650 million in 2027-28", "reduce by 1.3% in real terms";
  - `welsh-response.html` line 248: "0.5% lower in real terms next financial year", "almost 10% lower in real terms by 2029-30".
- **Fix:** on those 7 rows, set `proposed_metric` to `devolved_funding_real_terms_change` (or the coordinator's spelling). Keep the values, the signs and the null keys, and update both NOTES metric bullets.

### 5. `uk_thinktank_misc` row 12: Trussell's producer slug doesn't match AB2025
- **What's wrong:** AB2025 stages Trussell's own Budget-response pages as `source: trussell_wpi` in family `uk_trussell_wpi` (see that family's NOTES, lines 3 and 22–30). AB2026 README line 59 says each producer goes "in the AB2025 family of the same name where one exists".
- **Fix:** set `source` to `trussell_wpi`. The coordinator decides whether to also move the row to a new `uk_trussell_wpi` AB2026 family; if so, move its manifest line 6 with it and update the misc tallies to 12 rows and 5 primaries.

### 6. `uk_thinktank_misc` row 5: `conditions.component` is used on a context row
- **What's wrong:** `component` is the rule 9 field for a part of a measure. Here it names the one measure IfG counted.
- **Fix:** rename `conditions.component` to `conditions.subgroup`, keeping the value "a change to capital allowances". The row itself stays (the count rows are settled).

### 7. Family-level (low): placement, slugs and `stage.py`
- The Scottish Government sits in `uk_fai_sfc` and the Welsh Government in `uk_devolved_govts`. Neither `scottish_government` nor `welsh_government` is in the README slug table.
  - **Fix:** add both slugs to README line 59. Optionally move the Scottish Government's 5 rows and manifest line to `uk_devolved_govts`.
- Every family keeps a `stage.py` in its own directory. That isn't part of the README layout, and the existing convention is `pipeline/stage_ab2026_hmt_tables.py`. The files are not stale: they match NOTES and the manifests.
  - **Fix:** move each one to `pipeline/stage_ab2026_<family>.py`, or accept it as is.
- No old reports or spot-check files are in any family directory.

### 8. `uk_niesr` NOTES (optional wording fix)
- **The exclusions hold** under the AB2025 NIESR precedent ("restated OBR/HMT figures were not staged … none of them is a household/static row") and AB2025 rule 10.
- **But one stated reason is wrong.** "£12.4 billion … £7 billion on average" is not a macro call. It is NIESR restating the OBR's borrowing effect of "policies announced in this budget" (`breathing-space-not-strategy.html` line 555). That does concern the package of measures.
- **Fix:** in that inventory line, change the reason to "Restated OBR estimate of the policy package's borrowing effect; AB2025 NIESR precedent stages no restated OBR/HMT figures (the OBR's own figure belongs to `uk_obr_tables`)".
- The other excluded items are correctly #55 or design:
  - the DMO remit is a financing remit;
  - the debt and gilt figures are macro context;
  - the credibility dividend is NIESR's hypothetical scenario.
- The inventory is complete against HTML lines 543–563.

### Checks that passed
- **Quotes:** every quote is under 15 words and appears in its primary.
  - The CPS headroom quote matches only after HTML entities are decoded (`&#8216;headroom&#8217;`, `cps.html` line 252). Expect this if the checker reads the raw HTML.
- **Attribution and NOTES tallies match the rows:**
  - misc: 6 `own`, 7 `restated`; 1 registered key and 12 null; metric counts as stated; 4 rows at medium confidence;
  - Scottish Government: 5 rows (3 `gbp`, 2 `percent`);
  - Welsh: 1/3/4/4/2 by position, 12 rows with the proposal, 12 `gbp` and 2 `percent`.
- **Completeness:** I found no unstaged in-scope estimates in any of the 9 primaries.
- **Registered key:** the only one used is on misc row 8. IfG's "£100 council tax rebate to households in bands A-D" matches Table 6.1 line 1 exactly, and no proposed key comes with it. Correct.

## Sample: every row

The value, normalisation, period/`fy`/`time_basis`, quote and conditions are correct for every row unless noted.

**`uk_fai_sfc`** (`scottish_government_budget_response.html`)

| Row | Locator | Figure | Result |
|---:|---|---|---|
| 0 | line 347 | £650 million → 6.5e8, FY 2027-28 (period 2028) | OK; finding 4 |
| 1 | line 348 | 1.3% | OK; finding 4 |
| 2 | line 348 | £550 million | OK; finding 4 |
| 3 | line 348 | 1.5% | OK; finding 4 |
| 4 | line 348 | £100 million | OK; finding 4 |

**`uk_thinktank_misc`**

| Row | Locator | Figure | Result |
|---:|---|---|---|
| 0 | `cps.html` line 250 | £3tn (`range_low`) | OK |
| 1 | `cps.html` line 250 | £61bn | OK |
| 2 | `cps.html` line 252 | £15bn | OK |
| 3 | `cps.html` line 262 | £3.1bn | Finding 1 |
| 4 | `ifg.html` line 1813 | "almost 100" (`range_high`) | OK |
| 5 | `ifg.html` line 1813 | "one" | OK; finding 6 |
| 6 | `ifg.html` line 1813 | 56%, FY 2029-30 (period 2030) | OK |
| 7 | `ifg.html` line 1813 | 59%, FY 2029-30 (period 2030) | OK |
| 8 | `ifg.html` line 1896 | 80%, key line 1 | OK |
| 9 | `ifg.html` line 1896 | 2%, cumulative, 2030, `annual` | OK |
| 10 | `lwi.html` line 432 | one million | OK |
| 11 | `citizens_advice.html` line 245 | £60 a month (`gbp_per_month`) | OK |
| 12 | `trussell.html` line 1 | "over half" → 0.5 (`range_low`) | OK; finding 5 |

**`uk_devolved_govts`** (`welsh-response.html` line 248)

| Row | Locator | Figure | Result |
|---:|---|---|---|
| 0 | paragraph before Table 1 | £448m, cumulative, period 2030 | OK; findings 2 and 3 |
| 1 | Resource, 2026-27 | 199 | OK; finding 2 |
| 2 | Resource, 2027-28 | 165 | OK; finding 2 |
| 3 | Resource, 2028-29 | 146 (2029-30 is N/A and correctly not staged) | OK; finding 2 |
| 4 | Capital, 2026-27 | −27 | OK; finding 2 |
| 5 | Capital, 2027-28 | −19 | OK; finding 2 |
| 6 | Capital, 2028-29 | 2 | OK; finding 2 |
| 7 | Capital, 2029-30 | −18 | OK; finding 2 |
| 8 | Total, 2026-27 | 172 | OK; finding 2 |
| 9 | Total, 2027-28 | 146 | OK; finding 2 |
| 10 | Total, 2028-29 | 148 | OK; finding 2 |
| 11 | Total, 2029-30 | −18 | OK; finding 2 |
| 12 | paragraph after Table 1 | 0.5%, FY 2027-28 | OK; finding 4 |
| 13 | second paragraph after Table 1 | "almost 10%" → 10 (`range_high`), FY 2029-30 | OK; finding 4 |

**`uk_niesr`:** no rows. I checked all 9 inventory locators against HTML lines 543–560, and every one matches.