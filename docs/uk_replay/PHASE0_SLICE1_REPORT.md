# Phase 0 slice 1 report

Prepared on `w6/historical-phase0` from checkpoint
`61c13e38cfe4676756a7857e4fc6f67eac33cd0c`. The initial working tree was
clean. No runner changes, microdata downloads, population builds or
microsimulations were made. Existing tracked files changed only to add links
from PLAN.md and INVENTORY.md; the remaining artifacts are new files within
the requested paths.

## Sources and contracts

All six required roles were obtained for each event: economy, receipts,
expenditure, policy tables, HOFD historical forecast rows and the DWP benefit
expenditure/caseload edition. The 18 role receipts identify 16 distinct
workbooks because the three HOFD selections share one database. Every role has
a locked file, but not every table in it: the OBR's Autumn Statement 2022
event-day files deferred 15 tables to 24 November (economy 1.8, 1.10, 1.12 and
1.19; receipts 2.13, 3.1–3.4, 3.8, 3.11, 3.17 and 3.18; expenditure 3.2 and
3.18). The locks record those sheets as unavailable in the locked bytes
(`deferred_sheets`) and name the later files of the same forecast, first
archived on 9 December 2022, without locking them (`later_versions`). Unsuccessful exploratory lookups for the guessed
HOFD path and modern Autumn 2021 DWP media URL were resolved to captured
original URLs; they do not establish global archive absence.

| Event | Canonical source-lock receipt SHA-256 |
|---|---|
| Spring Statement 2022 | `cdff2fd50b5033ad337f571eb9a8df9397d21f775de9912f901aabd8eb924782` |
| Autumn Statement 2022 | `eedee2388971f7997dc182d6fb2540023f55a523a673372449ea2d2c2b557bb6` |
| Autumn Budget 2021 | `c98e70e9bae5b0c526e873cbd8827028aa1f1fa39dea16afe5b7fcd65c476a1f` |

The [collector and lock contract](VINTAGE_LOCKS.md) retain exact capture URLs,
timestamps, retrieval dates, byte hashes/sizes, media types, sheet names and
revision evidence. HOFD is explicitly the later March 2025 database selecting
historical event-labelled rows. Autumn 2021 receipts were saved after the
event and are classified as a later revision. All other original event-file
equivalence assessments remain unknown. November 2022's policy-role workbook
contains aggregate Government decision effects; its individual scorecard
rows were not established.

Added the [event selector](EVENT_VINTAGE_SELECTOR.md) and
[population manifest](POPULATION_MANIFEST.md) schemas and three bound
selectors. Original scoring FYs are retained. Survey choices follow the plan;
statistical publication dates are distinguished from licensed microdata
edition identity. The policy-world decision and annualisation bridge remain
explicitly pending.

The [policy-world proposal](POLICY_WORLD_CONTRACT.md) recommends calibrating
each published end-state once and evaluating pre-measures on the same records
and weights. Fetched expenditure captions support that choice. Grouped welfare
changes and pre/post macro labels exist, but a complete independent programme
level bridge is unverified. The proposal remains a methodology call under
cos d1344. [Historical FRS requirements](HISTORICAL_FRS.md) enumerate 14 raw
tables and reader columns, known historical mappings and access requirements.
The [adapter design](HISTORICAL_ADAPTER.md) preserves all source accounting,
requires manifest coverage and engine-bound certification, and cites the
current 2023–2030 execution limits.

## Commands and verification

The commands ran with an existing Python 3.12 environment holding the
test dependencies; no packages were installed.

```bash
# Collection: a scratch wrapper around the collector, described below.
python data/uk/events/collect_vintage_locks.py --check
PYTHONDONTWRITEBYTECODE=1 python -m pytest --noconftest -p no:cacheprovider tests/test_uk_vintage_locks.py -q
ruff format data/uk/events/collect_vintage_locks.py tests/test_uk_vintage_locks.py
ruff format --check data/uk/events/collect_vintage_locks.py tests/test_uk_vintage_locks.py
ruff check data/uk/events/collect_vintage_locks.py tests/test_uk_vintage_locks.py
git diff --check
```

Collection used a scratch wrapper that imported the collector, seeded its
cache with the initial economy workbook already fetched by curl with saved
HTTP headers, and called `main(['--scratch-dir',
'<scratch>/downloads'])`. The remaining 15 distinct workbooks used
the normal collector client. The direct collection CLI documented in
VINTAGE_LOCKS.md is rerun guidance; it was not the original collection command.

Final result: **29 tests passed in 84.96 seconds**; offline validation reported
`Validated 3 vintage locks offline`; Ruff checks succeeded. A Python scratch
audit rehashed all 16 downloaded workbooks and matched every byte size, digest
and sheet list to its receipt. Public workbook bytes were then removed by
targeted `Path.unlink`; scratch scripts and archive-access metadata stayed in a
temporary scratch directory outside the repository. No downloaded workbook is part of the change.
Final scope review confirmed all 22 changed paths are authorized, all new JSON
parses, local document links resolve and the test-generated database is absent.

A preliminary pytest invocation without `--noconftest` triggered the unrelated
repository database-build hook and was interrupted. Its generated database
was removed. The first full scoped run had 23 passing tests and one Hypothesis
deadline failure, with no contract assertion failure. The file-backed
properties now disable the default 200 ms deadline and cache repeated
inventory/schema reads; the final run above includes the added rejection cases.

Read-only research used `git show origin/main:<path>` and `gh api` commit and
repository metadata. Required fetch attempts for the two external clones
were denied at `.git/FETCH_HEAD`; GitHub API identities matched the local
refs: Microcosm `90958612874e7a52174c4d89d7df3f0f030783ba`, UK-data
`2b9c1c2c64ced6e1d95fed1ed398a22627233669`. The variant documentation/code
was read at `origin/w6/replay-variants`, commit
`eec87f42719cc73f41774ac940f67f5e55a67dba`, without checkout.

## Remaining unverified claims and delivery restriction

- Original-launch byte equivalence, numerical impact of the Autumn 2021
  receipts revision, and HOFD historical-cell equivalence to launch editions.
- Original DWP 2022 file identities from the later 2025 captures; event labels
  alone do not establish event-day availability or reconciled numeric targets.
- Individual November 2022 scorecard rows in the locked aggregate workbook,
  and the meaning of the November expenditure table's literal “October 22
  forecast” label.
- Complete pre-measures programme/head/FY/cash bridges, target-variable
  reconciliation, historical distributional controls and approved period,
  geography, behaviour and liability/cash mappings.
- Original historical FRS bytes, exact headers, code domains, units, date
  formats and missing-value/benefit-code conventions; historical availability
  of `UCSTART` and `UCHOUSEL`.
- First FRS 2019–20 microdata availability, exact FRS 2020–21 edition licence
  and byte identity, and historical donor vintages, access and rights.
- Historical ingestion/derivation and engine compatibility, historical policy
  schedules, projections, population artifacts and new certification. These
  remain requirements rather than demonstrated implementations.

**Delivery.** The lane's sandbox could not write git metadata, so the main
session committed the work (3209e0b) and opened PR #170. Its independent
review found the Autumn Statement 2022 event-day files' deferred tables and
that the offline check did not tie a source to its event; both are fixed in
the follow-up commit: the deferred sheets and later files are recorded, and
`check_locks` now refuses an OBR file naming another forecast, any source
other than the HOFD captured before the event, and a `launch` label on a file
modified after the event.
