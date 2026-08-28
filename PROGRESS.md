# Rebase progress

## State

Complete. `db-provenance-interning` is rebased onto `origin/main` (`20fc092`) with exactly the original two commit messages and all provenance contracts preserved.

## Done

- Confirmed the checkout is clean and `origin/main` resolves to `20fc092`.
- Read `e3b31c1` and `111d2c0` in full, including the prior #111 lane-query port.
- Rebased both commits; Git reported no textual conflicts.
- Audited the new Belgium PIT writer/tests and the changed main files for inline provenance access and raw score inserts.
- Ported the Belgium registry selector and test queries to the side tables.
- Added same-transaction, collision-verified provenance insertion and pruning to the Belgium raw writer.
- Ported #111's lane-advancement `reform_json` read to `JOIN reforms`.
- Autosquashed the semantic ports into the appropriate original commits.
- Passed the complete suite: 292 passed, 2 skipped, 2 warnings.
- Passed Ruff format and format-check with all 56 files unchanged/formatted.
- Built `/tmp/rb_a.db` and `/tmp/rb_b.db`; both have content hash `b3386d6e3cf9cfd7f904cbe845d8ac4ab6cb74f249807d7f264a799423d62996` and size 39,940,096 bytes.
- Confirmed `git diff --stat data/` is empty and the branch contains exactly two commits over `origin/main`.

## Next

- None. Final report: `/tmp/policyengine-scorecard-rebase-report.md`. Hand off the local branch without pushing.
