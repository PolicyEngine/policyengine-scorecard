# Vendored OBR costing claims

This directory vendors the OBR harvest rows used by the costing registry so
its staged claim joins can be tested without a sibling `scorecard-harvest`
checkout.

- Harvest date: 2026-08-02.
- Source claims file: `uk_obr/claims_staged.jsonl`, SHA-256
  `46117d14c4de7ac10cbc9bc09acef6c5b5060db1605e02334d4a827cf420a3bd`.
- Workbooks: `Policy_measures_database_November_2025_.xlsx`, SHA-256
  `76fb24ac780364949e5537563a70f8fbbe30cad6c652195704ea5d72b32ea619`;
  and `efo-march-2026-detailed-forecast-tables-receipts.xlsx`, SHA-256
  `f65b6cb7f96931d4abd85940794eb60f6f65afca8bbf16c74a4548bf92766a28`.
- Selection rule: retain every source row matching any of the 26 registry
  measure identities by OBR source, verbatim `reform_hint`, and fiscal event
  where present. This includes every mapped and unmapped head and every source
  period. The 621-row union contains 573 operational-window rows for
  2024–2030 plus 48 rows for 2022–2023 needed to validate each measure's true
  first nonzero costing year.

`obr_costings_claims.jsonl` preserves those complete source lines byte for
byte and in source-file order. It is 945,607 bytes with SHA-256
`bbb285705110779e1c5e31922e91e801279b03e7312670396612b8f817ad072f`.
