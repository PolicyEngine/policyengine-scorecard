# Belgian PIT reform registry progress

## State

The vendored Belgian PIT-reform claims now have a hash-gated registry adapter, three registered baseline families, seven result attachments, build-chain wiring immediately before final `be_jrc`, and focused passing tests. The wrong-layer `data/externals/` file has been removed.

## Done

- Confirmed the requested branch and starting commit.
- Confirmed that no GitNexus repository index is available, so repository files will be inspected directly.
- Recorded the implementation and validation plan.
- Read the Belgian JRC and reform-validation adapters, registry models and README, build order, exporter, app view, tests, and CI commands.
- Confirmed that the populations exporter requires a result for every rendered claim; the two official claims therefore need descriptive cross-attachments with explicit period-basis ambiguity.
- Vendored `claims.json`, `NOTES.md`, and `manifest.jsonl` with seven claims and five upstream artifact/PDF pins.
- Added seven `ExternalScore` rows and seven `PEResult` rows: five same-computation PolicyEngine self-attachments and two constructed official cross-attachments.
- Registered distinct SPF Finances, Cour des comptes, and Axiom same-year indexed baseline families.
- Wired `be_pit_reform` immediately before final `be_jrc` and removed the unused `data/externals/be-pit-reform-2026.json`.
- Added focused ingest tests; `8 passed in 0.03s`.
- Updated the Belgian Reform validation description and added readable labels for all three new sources; the focused Bun test passes (`1 pass`, `0 fail`).
- Completed an initial from-scratch build; it exposed and prompted a fix for a summary-key collision between the adapter's seven claims and database-wide coverage.
- Rebuilt after the fix: the adapter reports seven claims, seven results, and three sources; the logical content hash remained `945a5fe042343622a696ea4ac7e2e50196df6026af5fc9ba3d4f00804fd0dab0`.

## Next

- Rebuild the database from scratch, run the full Python suite, and export the populations feed.
- Verify all BE values/signs directly, then run the app CI commands and write the final report.
