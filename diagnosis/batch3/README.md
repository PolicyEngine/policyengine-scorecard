# Diagnosis batch 3 — the FNS, EITC and ASPE lanes (2026-10-07)

Scope: the claims of the three new mode-1 lanes whose PolicyEngine value is
"far apart" by the app's own thresholds (rates 10 points or more; counts 30%
or more), plus each lane's national headline rows. The certified bundle is
**us-6.2.1** (policyengine-us 2.2.1 + `populace-us-2024-spm-20260915`). TANF
counts are excluded: they are already `concept_mismatch` (any-time-in-year
against average month). Memos: [F.md](F.md) (FNS), [E.md](E.md) (EITC),
[A.md](A.md) (ASPE). Machine-readable items: `<cluster>.json`, ingested by
`scorecard_db/ingest_diagnoses.py::ingest_batch3` (build step
`diagnoses_batch3`, after the lanes' own ingests).

**Result:** 57 claims in 9 items — 50 `pe_gap`, 2 `concept_mismatch`, 5 open.
Every `pe_gap` routes to an issue that already exists; batch 3 adds
independent evidence to them.

| Item | Claims | Class | Route | Finding |
|---|---:|---|---|---|
| F1 | 17 | pe_gap | microcosm#647 | 14 far State rates are flag-saturated (PE 98.5-100%); AK and SD carry the household-to-person bridge; 30 States saturated overall |
| F2 | 10 | pe_gap | microcosm#647 | State eligible-count gaps track PE's participant scale (r = 0.82), not eligibility rules; no SNAP person targets; QC: 1.9 people per household vs PE 2.7 |
| F3 | 2 | open | — | Iowa and Wisconsin: PE 13-14 points below FNS with matching participants |
| E1 | 17 | pe_gap | microcosm#1133 | No EITC non-filers in the certified data; PE above IRS in 39 of 51 jurisdictions; Minnesota saturates |
| E2 | 1 | open | — | Connecticut: PE 15 points below IRS; a third of eligible units have the flag off |
| A1 | 1 | pe_gap | microcosm#643 | TANF: the 21.9% seed becomes 41.2% after calibration to ACF dollar targets (national target missed by 36%) |
| A2 | 5 | pe_gap | microcosm#644 | SSI payable eligibility low against TRIM3 (aged -31.5%, disabled -18.7%) while participants sit near SSA, so rates run high |
| A3 | 2 | open | — | SSI couples: PE has twice TRIM3's participating couple units |
| A4 | 2 | concept_mismatch | annotation | SNAP households: PE SPM units are fewer and larger than FNS households |

## Upstream

Posted 2026-10-07 from [COMMENT_DRAFTS.md](COMMENT_DRAFTS.md):
[microcosm#647](https://github.com/PolicyEngine/microcosm/issues/647#issuecomment-6040889778),
[microcosm#643](https://github.com/PolicyEngine/microcosm/issues/643#issuecomment-6040891162),
[microcosm#644](https://github.com/PolicyEngine/microcosm/issues/644#issuecomment-6040892484).
microcosm#1133 (filed 2026-10-07) already carries E1's evidence.
