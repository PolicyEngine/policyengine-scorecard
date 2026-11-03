# OBR AB2026 staging report

**2,891 rows; 3 primaries; contract: 0 problems; deterministic reproduction passed.**

The deliverables are `stage.py`, `claims_staged.jsonl.gz`, `manifest.jsonl`, `NOTES.md` and this report. The self-contained stager embeds every reviewed row. No shared files, COUNTS, registry or other family was changed; no commit, push or PR was made.

## Coverage and primary hashes

| Primary | Rows | SHA-256 |
|---|---:|---|
| Policy workbook | 2,520 | `cdcc2a06b100241bf3010bd159a4e5d43daef2348a3850797b1e88a308fd45fd` |
| EFO PDF | 358 | `9e0e9c340e35e603066f3124a614fcd68feadb3d5d10d1f76fb536e150e6225e` |
| Aggregates workbook | 13 | `3ffa3f1e63667b2ae9fb9626dc1da881673227d43aeeb52f8c3db168a5c75d6b` |

Policy workbook: every one of 2,520 displayed cells, including components, totals and summaries. PDF: 316 chapter-3 claims plus 42 headline aggregate/headroom cells. Aggregates workbook: 13 PSNB/ex-BoE PSND cells.

There are **711 null measure-key rows**: 620 with 37 proposed measure/package keys and 91 context/funding-level/old-policy-recosting rows without proposals. All 98 numbered registry measure titles were checked. The complete per-key tally (including null), all 37 proposal scopes, metric/unit/baseline proposals, access recipe and exclusions are in [NOTES.md](NOTES.md). Unresolved producer group decompositions remain explicit proposals rather than guessed registry mappings.

## Executed validation

```text
PYTHONPATH=. UV_CACHE_DIR=/private/tmp/scorecard-obr-uv-cache uv run -q python pipeline/ab2026_harvest_contract.py sources/harvest-uk-ab2026-2026-10-29/uk_obr_tables
sources/harvest-uk-ab2026-2026-10-29/uk_obr_tables: 2891 rows, 0 problems
```

`stage.py` was rerun; before and after SHA-256 were identical:

`5020e41fd2ec1aebfc015f169403250b52d630285b15a166564855e5864e1adf` (115,893 gzip bytes).

Confirmed gzip mtime zero and no filename header; document/page ordering; every raw value in its quote; string-valued conditions; and no proposed key alongside a registered key. Independent full audits verified all 2,520 workbook cells exactly once, all 98 measure-title lineages, and all 316 PDF policy rows including all 215 printed table/rating cells. All matched their primary except the source contradictions retained below. The 5,500-officer input was corrected to an undated announcement as of 2026 instead of borrowing the neighboring 670-officer delivery year.

## Forty random final-row checks

Selected with `random.Random(2302026).sample(range(2891), 40)`, sorted for reporting. Reopened each workbook cell with openpyxl, or re-extracted the precise PDF page using `pdftotext -layout`. All numbers, signs, units and periods matched. The table uses final gzip row numbers (1-based); policy amounts are GBP after the displayed £million conversion. Prose positive magnitudes preserve the wording's cost/yield direction in conditions.

| Row | Reopened locator | value_raw | Normalized value / unit | FY or time | Result |
|---:|---|---|---|---|---|
| 44 | policy 1.1!J20 / line 4 | -354 | -354,000,000 gbp | 2027-28 | matched |
| 133 | policy 1.1!I39 / line 8 | 0 | 0 gbp | 2026-27 | matched |
| 167 | policy 1.1!M47 / line 11 | -52 | -52,000,000 gbp | 2030-31 | matched |
| 440 | policy 1.1!J105 / line 21 | -263 | -263,000,000 gbp | 2027-28 | matched |
| 500 | policy 1.1!J119 / line 25 | -179 | -179,000,000 gbp | 2027-28 | matched |
| 523 | policy 1.1!I124 / line 26 | 0 | 0 gbp | 2026-27 | matched |
| 584 | policy 1.1!J136 / line 28 | -1 | -1,000,000 gbp | 2027-28 | matched |
| 624 | policy 1.1!N144 / line 30 | 504 | 504,000,000 gbp | 2031-32 | matched |
| 836 | policy 1.1!J193 / line 43 | 0 | 0 gbp | 2027-28 | matched |
| 895 | policy 1.1!I205 / line 45 | 6 | 6,000,000 gbp | 2026-27 | matched |
| 1000 | policy 1.1!L226 / line 49 | 2143 | 2,143,000,000 gbp | 2029-30 | matched |
| 1023 | policy 1.1!K232 / line 51 | 73 | 73,000,000 gbp | 2028-29 | matched |
| 1030 | policy 1.1!L233 / line 51 | 75 | 75,000,000 gbp | 2029-30 | matched |
| 1070 | policy 1.1!J241 / line 52 | 1 | 1,000,000 gbp | 2027-28 | matched |
| 1199 | policy 1.1!M266 / line 56 | -13 | -13,000,000 gbp | 2030-31 | matched |
| 1208 | policy 1.1!J269 / line 57 | 9 | 9,000,000 gbp | 2027-28 | matched |
| 1252 | policy 1.1!L276 / line 57 | 10 | 10,000,000 gbp | 2029-30 | matched |
| 1582 | policy 1.1!L349 / line 74 | -332 | -332,000,000 gbp | 2029-30 | matched |
| 1621 | policy 1.1!I358 / line 76 | 0 | 0 gbp | 2026-27 | matched |
| 1703 | policy 1.1!M375 / line 80 | -2 | -2,000,000 gbp | 2030-31 | matched |
| 1754 | policy 1.1!J387 / line 83 | 9 | 9,000,000 gbp | 2027-28 | matched |
| 1773 | policy 1.1!K391 / line 84 | -20 | -20,000,000 gbp | 2028-29 | matched |
| 1841 | policy 1.1!M404 / line 86 | 312 | 312,000,000 gbp | 2030-31 | matched |
| 1907 | policy 1.1!M420 / line 91 | 0 | 0 gbp | 2030-31 | matched |
| 1923 | policy 1.1!K424 / line 92 | 0 | 0 gbp | 2028-29 | matched |
| 2028 | policy 1.1!N444 / line 95 | -16 | -16,000,000 gbp | 2031-32 | matched |
| 2081 | policy 1.1!M454 / line 96 | -450 | -450,000,000 gbp | 2030-31 | matched |
| 2115 | policy 1.1!K467 | 0 | 0 gbp | 2028-29 | matched |
| 2123 | policy 1.1!M468 | 0 | 0 gbp | 2030-31 | matched |
| 2178 | policy 1.1!N485 | 16570 | 16,570,000,000 gbp | 2031-32 | matched |
| 2308 | policy 1.1!L511 | 213 | 213,000,000 gbp | 2029-30 | matched |
| 2315 | policy 1.1!M512 | -54 | -54,000,000 gbp | 2030-31 | matched |
| 2444 | policy 1.1!J539 | -75 | -75,000,000 gbp | 2027-28 | matched |
| 2458 | policy 1.1!L542 | -445 | -445,000,000 gbp | 2029-30 | matched |
| 2475 | policy 1.1!K545 | 0 | 0 gbp | 2028-29 | matched |
| 2497 | policy 1.1!I551 | -7,597 | -7,597,000,000 gbp | 2026-27 | matched |
| 2546 | Table 3.1 (p.61), Total effect of Government decisions, 2027-28 | 7.0 | 7,000,000,000 gbp | 2027-28 | matched |
| 2585 | Table 3.1 (p.61), Council tax rebate, 2030-31 | 0.0 | 0 gbp | 2030-31 | matched |
| 2615 | Table 3.1 (p.61), Tax administration, compliance and debt collection measures, 2030-31 | -2.9 | -2,900,000,000 gbp | 2030-31 | matched |
| 2813 | Table 3.3 (p.72), Verification assurance officers, 2030-31 | -255 | -255,000,000 gbp | 2030-31 | matched |

## Supplementary fiscal checks

Ten additional rows were sampled from the 55-row fiscal pass with `random.Random(230).sample(range(55),10)` and reopened in the original workbook or PDF. All matched; PDF p.188 is physical page191.

| Locator | Printed value and interpretation | Period | Result |
|---|---|---:|---|
| A.9 p.188, PSNFL cash, FY2029-30 | 2,997 £bn stock → 2,997,000,000,000 GBP | 2030 | matched |
| Workbook 6.13 G23, ex-BoE debt/GDP, FY2029-30 | 94.3 percent of nominal GDP | 2030 | matched |
| 7.1 p.161, PSNFL rule pre-measures margin | 0.6 percent of GDP, positive headroom | 2030 | matched |
| A.9 p.188, PSNFL cash, FY2030-31 | 3,075 £bn → 3,075,000,000,000 GBP | 2031 | matched |
| A.9 p.188, PSNFL cash, FY2027-28 | 2,807 £bn → 2,807,000,000,000 GBP | 2028 | matched |
| A.9 p.188, PSNB/GDP, FY2026-27 | 4.2 percent of nominal GDP | 2027 | matched |
| Workbook 6.5 D14, PSNB FY2027-28 | 112.0 £bn → 112,000,000,000 GBP | 2028 | matched |
| A.9 p.188, PSNFL cash, FY2026-27 | 2,684 £bn → 2,684,000,000,000 GBP | 2027 | matched |
| A.9 p.188, PSNFL/GDP, FY2026-27 | 83.2 percent of nominal GDP | 2027 | matched |
| A.9 p.188, ex-BoE PSND cash, FY2025-26 | 2,787 £bn ONS outturn → 2,787,000,000,000 GBP | 2026 | matched |

Additional edge checks: workbook J497 -397.5 displays -398; L258 negative stored fraction displays 0; I549 displays -8,905; J555 displays 3,483. Fiscal welfare-cap headroom remains the printed **-2.8 £bn breach**.

## Access gaps, exclusions and contradictions

All three fresh remote requests (EFO page, ZIP, chapter-2 workbook) were 403, so exact local copies were used and hashed. The PDF attachment URL remains unknown; its landing URL and local filename are explicit in the manifest. No changed version could be checked after refusal.

No chart bars, unlabeled paths, unprinted cached decimals, or whole-economy GDP/CPI paths were staged. The policy workbook has no static/behavioural split or ratings matrix. The PDF has no PTA or Carer's Allowance taper costing text; their workbook cells are included. Annex A contributes selected fiscal aggregates. A dash funding cell is omitted. Older-policy monitoring and unrequested FRS context are excluded. The printed 2075-76 triple-lock debt scenarios end in 2076, outside the checker's 2075 limit; they are documented rather than misdated. Complete exclusions are in NOTES.md.

Material inconsistencies are preserved:

- Workbook total policy effects appear to mix direct/indirect sign conventions and differ substantially from PDF Table 3.1.
- PDF dates CPS abolition April2027 (HMT April2028) and FYA increase April2027 (HMT January2027).
- PDF Growth Guarantee expansion is £7bn (HMT £6.5bn); PDF CSOP reform differs from the workbook/HMT EMI2 title.
- PDF departmental spending prose, some tax classification totals and rounded £12bn versus table £11.7bn do not align exactly. The social-care footnote calls the cited costs “healthcare”.

Scope/date mismatches use null proposed keys; numbers and dates were not repaired. NOTES.md gives the precise claims, scopes and remaining line-decomposition limits for coordinator review. Global pinning/count tests are deferred because the assignment forbids updating COUNTS; the standalone family contract passed.

