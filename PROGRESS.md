# Belgian PIT reform registry progress

## State

The architecture and source evidence have been inspected. Seven exact claims and their upstream SHA-256 pins are now vendored under `sources/be-pit-reform-2026/`; raw PDFs remain outside the repository.

## Done

- Confirmed the requested branch and starting commit.
- Confirmed that no GitNexus repository index is available, so repository files will be inspected directly.
- Recorded the implementation and validation plan.
- Read the Belgian JRC and reform-validation adapters, registry models and README, build order, exporter, app view, tests, and CI commands.
- Confirmed that the populations exporter requires a result for every rendered claim; the two official claims therefore need descriptive cross-attachments with explicit period-basis ambiguity.
- Vendored `claims.json`, `NOTES.md`, and `manifest.jsonl` with seven claims and five upstream artifact/PDF pins.

## Next

- Implement the hash-gated registry adapter, registered baselines, build wiring, and focused tests.
- Remove the wrong-layer `data/externals/be-pit-reform-2026.json`.
- Rebuild/export the registry feed and run the Python and app CI commands.
