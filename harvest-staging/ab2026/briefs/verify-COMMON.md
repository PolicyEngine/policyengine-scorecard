# Verify staged Autumn Budget 2026 harvest families for the PolicyEngine scorecard (#230)

You are an independent verifier. Another lane staged the families named in your assignment below for the Autumn Budget 2026 (AB2026) harvest in PolicyEngine/policyengine-scorecard. The coordinator merges a family into PR #231 only after your review. Your verdict decides whether a family merges as it is, merges after mechanical fixes, or goes back for rework.

You work read-only in a git worktree of the scorecard repository. Don't edit, create or delete files, and don't run `stage.py` (it writes). Your final message is the deliverable.

## Read first

1. `sources/harvest-uk-ab2026-2026-10-29/README.md`: the AB2026 rules 1–9. Rules 8 (stage estimates, not design) and 9 (a component of one measure keeps that measure's key) matter most here.
2. `sources/harvest-uk-ab2025-2026-09-24/README.md`: the full row contract and the AB2025 rules.
3. `sources/harvest-uk-ab2026-2026-10-29/REGISTRY_KEYS.md`: every registered measure key, with its HM Treasury Table 6.1 line and title.
4. Each assigned family's `NOTES.md`, `manifest.jsonl` and rows. Read rows with:
   `python3 -c "import gzip,json;[print(i,json.dumps(json.loads(l),ensure_ascii=False)) for i,l in enumerate(gzip.open('PATH/claims_staged.jsonl.gz','rt'))]"`
   Row indices in your report are 0-based in that order.
5. The AB2025 family of the same producer, where one exists (`sources/harvest-uk-ab2025-2026-09-24/<family>/`), for the producer's conventions.

The primaries are under `.ab2026-primaries/<family>/` in this worktree (git ignores them). Use `pdftotext -layout`, openpyxl or plain text tools to read them. Never read values off a chart's bars.

## Checks, per family

1. **Hashes.** Recompute the sha256 of every primary the manifest lists, and match it to `manifest.jsonl`. Every row's `publication.primary_sha256` must be a manifest primary.
2. **Contract.** `PYTHONPATH=. python3 pipeline/ab2026_harvest_contract.py sources/harvest-uk-ab2026-2026-10-29/<family>` must report 0 problems.
3. **Rows against the primaries.** For the sample your assignment sets (rows drawn with Python's `random.Random(231)`, plus at least one row from every primary, every proposed key and every row type), re-open the primary at the row's locator. Confirm each of these:
   - the printed figure is `value_raw`;
   - `value` normalises it correctly (scale, unit and sign convention);
   - `period`, `conditions.fy` and `time_basis` are right;
   - the `quote` appears in the primary;
   - the conditions describe the figure correctly (breakdown, geography, price basis).
4. **Keys and scope (rules 2, 3 and 9).**
   - For every distinct `measure_key`, confirm the producer's figure covers exactly that Table 6.1 line.
   - For every proposed key, confirm that NOTES.md's scope matches the producer's words, and that no registered key or package matches exactly. Flag a proposed key that is really a part of one Table 6.1 line (rule 9 makes it a component of that line) or that equals a registered package.
   - For components, confirm each is a part of one measure, and that no row lets an ingest add components to their total.
   - Where a family prints both components and totals, test the identity: components sum to the printed total within rounding, for a sample of measures and years. List every failure.
5. **Design rows (rule 8).** List every row whose value is a measure's design: a rate, threshold, payment amount, date or duration, a spending allocation, a financing remit or a contingent liability. Give row indices and counts by category.
6. **Attribution.** `own` rows are the producer's own estimates. `restated` rows repeat an official or other producer's figure and say whose in `note`. `benchmark_class` fits the row.
7. **Quotes.** HM Treasury and OBR quotes are whole cells or sentences. Every other producer's quote has fewer than 15 words.
8. **NOTES.md.** Recompute the coverage tallies from the rows and compare. Check that the proposed keys and the not-staged section match the rows, and that nothing in the family directory is stale (old reports or spot-check files).
9. **Completeness.** Skim each primary for in-scope estimates that were neither staged nor listed as not staged. Report what you find, with locators.

## Verdict (your final message)

For each family, give one of these verdicts:

- **APPROVE:** merge as it is.
- **APPROVE WITH FIXES:** the coordinator can apply exact, mechanical fixes and merge.
- **REWORK:** the problems are systematic and need the staging lane.

Then list findings, most serious first. Each finding gives:

- row indices (or "family-level");
- what is wrong;
- evidence: the primary, locator and what it prints;
- the exact fix: drop these rows; set this field to this value; re-key to this key with these conditions.

End with your sample: each checked row's index, locator and result. Be specific. Don't fix anything yourself.
