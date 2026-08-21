# Belgium: JRC EUROMOD country-report lane

This package ingests the JRC's *EUROMOD Country Report Belgium 2025* Annex 3 validation extract under the Scorecard's model/admin boundary.

Provenance is pinned to the Chronicle repository's local `origin/main` commit `1cab80987a462e00055f259cc56dc6b311c030bf`. The CSV was originally introduced at Chronicle commit `243c4afb2ebc350af17ad1cd9b4c46d1e7c01ccc`; its SHA-256 is `2ed1f8a677799fefe7cc2f092b4f30221940a2a2fc9deecbf29e7a5f7d71b69f`. The copied Chronicle manifest has SHA-256 `04cb66729ae960f3a6e5c13eff43967ec276b715f6134a9ad599824ea7f3ddb0`.

The source contains 18 data records (19 physical lines including the header), despite the lane brief saying 19 rows and eight EUROMOD claims:

- 6 `euromod` model-output rows become Scorecard claims;
- 6 `external` statistical rows become deterministic Ledger staging facts in `data/ledger/be_admin_outturns.jsonl`;
- 6 `ratio` rows are rounded `euromod / external` derivations and are not persisted as claims or facts.

Chronicle's source-package metadata defines A3.4/A3.6 as calendar year 2023 and A3.7/A3.8 as calendar year 2022. Local J2.0+ data configuration corroborates that these are the EUROMOD policy-system/output years and coincident income-reference years, not survey collection years. The report vintage is 2025.

The two attached Axiom values are deliberately `concept_mismatch`: the result period is CY2026 rather than CY2023, the demo population uses US survey support records reweighted to Belgian administrative targets rather than Belgian SILC microdata, and the result scope is a positive-remuneration worker slice rather than the report's national population. The other four claims have no attached value.
