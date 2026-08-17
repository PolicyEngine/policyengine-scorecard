# OBR costings Follow-up 2 report

Status: complete locally on `obr-costings-mode2`; committed, not pushed.

## Review findings

1. **Certified bytes:** every future managed simulation now hashes the exact
   resolved `runtime_dataset_source` immediately before construction and after
   aggregate reads, verifies the simulation reports that same path, and records
   baseline/reform hash pairs in new artifacts
   (`pipeline/compute_uk_obr_costings.py:695`, `:712`, `:727`, `:750`, `:777`).
   The mutation-abort and dated-legacy contracts are tested at
   `tests/test_obr_costings_registry.py:397` and `:453`.
2. **Unique external joins:** `external_claim_match` now owns all six match
   keys, including verbatim `source_table` and `reform_hint`
   (`pipeline/compute_uk_obr_costings.py:207`). The repo vendors exactly 215
   byte-identical selected harvest lines with provenance and the source/subset
   hashes (`sources/harvest-20260802/uk_obr/README.md:7`); vendored and optional
   full-harvest uniqueness tests begin at
   `tests/test_obr_costings_registry.py:679` and `:712`.
3. **Sourced axes/mechanisms:** staged and comparison rows now carry harvested
   `source_model`, `basis`, and `behavioural_adjustment = unstated in harvest`
   (`pipeline/compute_uk_obr_costings.py:220`). The employer-NIC note cites the
   installed incidence parameter and fixed-employer-cost wage formula and
   explains the non-zero Income-tax head
   (`data/uk/obr_measure_reforms.yaml:529`).
4. **HICBC welfare head:** `child_benefit` is explicitly a PROVISIONAL PE
   mapping; the note says the harvest identifies neither programme nor
   mechanism and attributes the zero PE delta only to fixed
   `would_claim_child_benefit` (`data/uk/obr_measure_reforms.yaml:493`).
5. **Register framing:** the aggregate sign-concordance headline and matching
   all-rows assertion are gone; only row-level values and descriptive bins
   remain (`PROGRESS.md:22`).
6. **Dividend thresholds:** four dividend-path entries have validated 2024 and
   2025 `partial` overrides with the policyengine-uk#1822 note, while 2026+
   retains each base status (`data/uk/obr_measure_reforms.yaml:40`,
   `pipeline/compute_uk_obr_costings.py:276`). The installed-value/date-sensitive
   test is at `tests/test_obr_costings_registry.py:212`.

## Restage and tests

- Final command: `python pipeline/compute_uk_obr_costings.py --restage`.
- Result: 13 existing artifacts (one diagnostic), 20 staged rows, and 26
  comparison rows; **0 managed simulations**.
- All 26 comparison row identities, OBR/PE values, signed ratios, and bins are
  unchanged. Descriptors, sourced axes, and annotations changed.
- Focused suite: **44 passed**, 1 upstream Pydantic deprecation warning.
- Full suite: **211 passed**, 1 upstream Pydantic deprecation warning.
- `git diff --check` passes and the worktree was clean after restaging.
- Independent final audits approved the byte binding, harvest joins/HICBC/
  dividend overrides, and sourced-axis/register changes without finding gaps.

## Offline limitations

No simulation was run, as required. The sibling full harvest was available, so
its optional exactly-one-match and byte-identity test ran rather than skipping.
GitNexus graph resources and private issue/PR bodies were unavailable; source,
installed package files, committed harvest data, and offline tests supplied all
evidence needed for the six fixes.

The designated parent output path
`/Users/maxghenis/scorecard-lanes/obr-costings-followup-2-report.md` is outside
the sandbox's writable roots; copying this report there was rejected with
`Operation not permitted`. This identical report is therefore committed inside
the repository as `obr-costings-followup-2-report.md`.
