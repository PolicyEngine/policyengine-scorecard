# Belgian PIT reform registry progress

## State

The Belgian PIT-reform registry work is implemented and exported. The fresh database build is stable, all 273 Python tests and all 6 Bun source tests pass, and the committed data/app feeds contain the seven new BE rows. The frozen Bun dependency install cannot fetch lockfile packages in the network-disabled sandbox, so dependency-backed lint and production build remain unavailable here.

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
- Exported 293 populations rows with the canonical module invocation and synchronized the committed app feed through its canonical `prebuild` script.
- Verified the seven PIT-reform rows directly in `app/public/data/populations.json`: one SPF Finances row, one Cour des comptes row, and five PolicyEngine rows, all for BE with the requested negative values.
- Reran the full Python suite after synchronization: `273 passed in 7.36s`; Ruff reports `53 files already formatted`.
- Mirrored the app commands: `bun test src` passes (`6 pass`, `0 fail`); `bun install --frozen-lockfile` cannot obtain uncached lockfile packages without network access, leaving `oxlint` and `tsc` unavailable for lint/build.

## Next

- Commit the generated feeds, perform the final deterministic rebuild/no-drift check, and write the lane report.
