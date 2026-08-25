# Belgium: JRC EUROMOD country-report lane

This package ingests the JRC's *EUROMOD Country Report Belgium 2025* Annex 3 validation extract under the Scorecard's model/admin boundary.

Provenance is pinned to the Chronicle repository's local `origin/main` commit `1cab80987a462e00055f259cc56dc6b311c030bf`. The CSV was originally introduced at Chronicle commit `243c4afb2ebc350af17ad1cd9b4c46d1e7c01ccc`; its SHA-256 is `2ed1f8a677799fefe7cc2f092b4f30221940a2a2fc9deecbf29e7a5f7d71b69f`. The copied Chronicle manifest has SHA-256 `04cb66729ae960f3a6e5c13eff43967ec276b715f6134a9ad599824ea7f3ddb0`.

The source contains 18 data records (19 physical lines including the header), despite the lane brief saying 19 rows and eight EUROMOD claims:

- 5 `euromod` model-output rows become Scorecard claims (EUROMOD version **J1.0+** per the report front matter, p. 3; 2025 is only the report vintage);
- 1 `euromod`-labelled row — unemployment benefits — is a **non-simulated uprated EU-SILC survey input** (Table A3.6 marks `bun` Simulated=N, p. 127; `bun_be` is switched off in the baseline, p. 24; the 11,706 for 2023 is the SILC income-year-2021 base of 10,416 uprated) and routes to Ledger staging with that provenance pinned, never to a claim;
- 6 `external` statistical rows become deterministic Ledger staging facts in `data/ledger/be_admin_outturns.jsonl`, each carrying its underlying issuer (NBB for income tax, employee SICs, and child benefits; RVA for unemployment; EU-SILC for the Gini and AROP comparators) with JRC as the secondary publisher;
- 6 `ratio` rows are rounded `euromod / external` derivations and are not persisted as claims or facts.

Periods on model claims are EUROMOD policy-system/output years (2023 for A3.4/A3.6, 2022 for A3.7/A3.8) simulated from database `BE_2022_c1` — EU-SILC 2022 collection, income reference year **2021**, coverage **private households** (Table 3.1, p. 97) — with monetary values uprated into each simulation year. They are not matched income-reference years and not SILC collection years. Model claims carry `population_frame=private_households` and `input_database=be_2022_c1_silc2022_income2021` pins so the modeled universe is never presented as an unqualified national frame.

The two attached Axiom values are deliberately `concept_mismatch`: the result period is CY2026 rather than CY2023, the demo population uses US survey support records reweighted to Belgian administrative targets rather than Belgian SILC microdata, and the result scope is a positive-remuneration worker slice rather than the report's national population. The other three claims have no attached value.
