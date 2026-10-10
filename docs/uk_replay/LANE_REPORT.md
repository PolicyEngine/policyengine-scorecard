# Track 2 scoping lane report — #156

Completed the four requested documents and the per-measure/head inventory for
32 OBR events, June 2010–Autumn Budget 2025. Preserved the earlier research and
parameter indices, recovered 3,796 classifications, integrated 37 targeted audit
corrections, then 17 latest-patch records. The active engine audit is
policyengine-uk 2.125.1; source/wheel pins and immutable prior-version receipts
make the late patch update reviewable.

| Class | Measure×head rows | Gross original-scoring-year £bn | Share of gross £ |
|---|---:|---:|---:|
| Expressible | 220 | 855.258 | 14.9% |
| Partial | 121 | 635.501 | 11.0% |
| Not expressible | 626 | 493.827 | 8.6% |
| Outside household scope | 2,829 | 3,769.352 | 65.5% |

Counts concern disjoint workbook occurrences; there are 1,858 event-specific
measure titles. Gross £ adds absolute original FY costings across heads/years,
not annual spending or a cumulative causal estimate. Fully expressible machinery
covers 14.9% of gross £; household scope covers 34.5%. No numerical replay or new
certification is claimed.

- `INVENTORY.md`: every event's counts, £ and coverage shares; per-row scope,
  parameters/missing machinery, FY costings and source pointers.
- `HISTORICAL_RULES.md`: historical dates/formula gaps for all requested areas;
  RuleSpec files and bounded contribution to missing historical law.
- `POPULATIONS_AND_VINTAGES.md`: actual Microcosm build/source pins; 32-event
  forecast matrix; archival retrieval and missing first-release/detail surfaces.
- `PLAN.md`: 8–12 lane-days of contracts/source work before 28 October;
  182–312 lane-days for supported historical household replays and complete
  accounting; 60–120 additional for broader household coverage. These are gated
  planning estimates. Start with 2022; modern-population sensitivities retain a
  distinct label.

The biggest gaps are the pre-2015 parameter-processing floor, reported/receipt-
gated retired benefits and missing regimes, historical annual populations and
forecast-release selection. Aggregate OBR forecasts exist for all 32 events;
only 3 have harvested detailed calibration tables. Public DWP pages list all 32
forecast editions, but correction/first-release identity still needs work.

Validation:

- All 22,215 retained workbook costing cells match, including 7,958 zero cells
  and 46 repeated-key occurrences; 24,943 extension cells excluded. Workbook
  hash and worksheet locations are in `data/uk/events/validation_receipt.json`.
- The late engine/classification patch left the source matrix unchanged;
  deterministic rebuild, row identities, every cited path/variable, class and
  source accounting were revalidated against 2.125.1.
- Read-only adapter tests: 21 passed (`pytest --noconftest` on
  `tests/test_obr_adapter.py` and `tests/test_obr_policy_effects_adapter.py`).
  The initial ordinary pytest invocation triggered the repository's database-
  building conftest; it was interrupted and its generated `data/scorecard.db`
  removed before the scoped rerun.
- Documentary relative links, evidence JSON/hashes, source-script syntax,
  32-event forecast windows, RuleSpec counts and `git diff --check` passed.
- No simulations, population builds, datasets or new virtual environments.

Git delivery is blocked by the sandbox: `git add` cannot create
`~/PolicyEngine/policyengine-scorecard/.git/worktrees/scorecard-replay-inventory/index.lock`
(`Operation not permitted`). The branch remains `replay/inventory` at the
pre-existing e93cfa6. No new commit, push or draft PR was made; no merge or contact
was attempted. Final files are left for the main session to commit, push and
open a draft PR referencing #156, as the continuation instructions allow.

Scratch cleanup status is recorded in `evidence/cleanup_receipt.json`. All
currently cited source extracts, hashes, workbook cells and publication receipts
were preserved under the allowed directories before deleting
`/tmp/uk-replay-scope/`; older research scratch paths are archival leads only.
