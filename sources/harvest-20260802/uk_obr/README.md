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
- Selection rule: for every registry head mapped in calendar proxy years
  2024–2030, retain the sole source row selected by OBR source, period,
  verbatim `reform_hint`, effective `source_table` and metric, fiscal event
  where present, and mapped head condition. The union contains 215 rows.

`obr_costings_claims.jsonl` preserves those complete source lines byte for
byte and in source-file order. It is 315,910 bytes with SHA-256
`99b8748ccd318a0d0cee0ddbbade757526d186099e15f6ca5a8e4b8d6c2dcca9`.
