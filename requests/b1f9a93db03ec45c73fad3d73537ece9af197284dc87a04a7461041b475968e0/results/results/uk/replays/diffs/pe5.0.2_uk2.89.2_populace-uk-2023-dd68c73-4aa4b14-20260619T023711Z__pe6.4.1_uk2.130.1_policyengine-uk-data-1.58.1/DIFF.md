# Release diff: `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z` → `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1`

Movements of the event replay between two certified releases. Flags are investigation prompts, not verdicts; ratio bins are descriptive.

A numerical flag means the move exceeds max(£1m, 1% of the larger magnitude). Structural, coverage, mapping, support, inertness and construction flags are raised regardless of size. A year supported on one side only is a support flag, not coverage.

## Executions

| Field | Base | Head |
|---|---|---|
| certified_dataset_sha256 | `f17306ccb2aad7ff0130be3589b560afb2e2a12a943570911cd0c77f07934833` | `056e80fd8e9151d78f432a25cde863340baee81304c6216a37fb575ce8563784` |
| data_bundle | `populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z` | `policyengine-uk-data-1.58.1` |
| policyengine_core_version | `3.27.1` | `3.33.0` |
| policyengine_uk_version | `2.89.2` | `2.130.1` |
| policyengine_version | `5.0.2` | `6.4.1` |
| variant_id | `pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z` | `pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1` |

Construction premises compared: base `02688ac6a26c1169ae7235be2ea8ff906a74fbc339a075d146fa3b9ca30edb7a`, head `59504b1dce718a92b441f71e254fad225c4f50030407d0ad8e2711b8e78a6296`.

## Flags by event

| Event | Supported years (base → head) | numerical | structural | coverage | mapping | support | inertness | construction |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| autumn_budget_2024 | 2024–2029 → 2024–2029 | 90 | 2 | 1 | 0 | 0 | 0 | 6 |
| autumn_budget_2025 | absent → 2025–2030 | 0 | 0 | 1512 | 0 | 0 | 0 | 0 |
| autumn_statement_2023 | 2023–2028 → 2024–2028 | 100 | 5 | 0 | 0 | 18 | 0 | 0 |
| spring_budget_2023 | 2023–2027 → 2024–2027 | 24 | 0 | 0 | 0 | 5 | 0 | 0 |
| spring_budget_2024 | 2023–2028 → 2024–2028 | 78 | 10 | 0 | 0 | 11 | 0 | 0 |
| spring_statement_2025 | 2024–2029 → 2024–2029 | 24 | 0 | 0 | 0 | 0 | 0 | 0 |
| **all** | | 316 | 17 | 1513 | 0 | 34 | 0 | 6 |

## Flagged movements

Showing 200 of 1832 rows with a flag other than support, rows without a numerical change first, then by absolute change. £m, positive = gain to the Exchequer.

| Event | Measure | CY | Level | Key | Base | Head | Change | Flags |
|---|---|---:|---|---|---:|---:|---:|---|
| autumn_budget_2024 | capital_gains_main_rates_and_reliefs | 2024 | source_row | obr_pmd_nov2025:11682:73295721bdfdb9e8 | — | 575.0 | — | coverage |
| autumn_budget_2025 | ab2025__advanced_corporation_tax_shadow_act_abolished | 2025 | source_row | obr_pmd_nov2025:12588:322e2c68e89822d1 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__advanced_corporation_tax_shadow_act_abolished | 2026 | source_row | obr_pmd_nov2025:12589:2ad090e241f5854f | — | — | — | coverage |
| autumn_budget_2025 | ab2025__advanced_corporation_tax_shadow_act_abolished | 2027 | source_row | obr_pmd_nov2025:12590:b086d4cfc95c9d89 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__advanced_corporation_tax_shadow_act_abolished | 2028 | source_row | obr_pmd_nov2025:12591:f4dd5da018c449f1 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__advanced_corporation_tax_shadow_act_abolished | 2029 | source_row | obr_pmd_nov2025:12592:5853b1dada491566 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__advanced_corporation_tax_shadow_act_abolished | 2030 | source_row | obr_pmd_nov2025:12593:209982cc3c724049 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__apd_higher_rate_extended_to_private_jets | 2025 | source_row | obr_pmd_nov2025:12426:f75f3e76fe8c5014 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__apd_higher_rate_extended_to_private_jets | 2026 | source_row | obr_pmd_nov2025:12427:d4c24fdda23ab75c | — | — | — | coverage |
| autumn_budget_2025 | ab2025__apd_higher_rate_extended_to_private_jets | 2027 | source_row | obr_pmd_nov2025:12428:79d7233e344d244c | — | — | — | coverage |
| autumn_budget_2025 | ab2025__apd_higher_rate_extended_to_private_jets | 2028 | source_row | obr_pmd_nov2025:12429:c0f89fd6eeed1c58 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__apd_higher_rate_extended_to_private_jets | 2029 | source_row | obr_pmd_nov2025:12430:a97366204f47d7a1 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__apd_higher_rate_extended_to_private_jets | 2030 | source_row | obr_pmd_nov2025:12431:93551cb0db793092 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__apr_bpr_unused_allowance_transferable_between_spouses | 2025 | source_row | obr_pmd_nov2025:12684:2e7b089220d29eec | — | — | — | coverage |
| autumn_budget_2025 | ab2025__apr_bpr_unused_allowance_transferable_between_spouses | 2026 | source_row | obr_pmd_nov2025:12685:57c04c13ea0d4413 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__apr_bpr_unused_allowance_transferable_between_spouses | 2027 | source_row | obr_pmd_nov2025:12686:7637fbd2a1fb3d55 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__apr_bpr_unused_allowance_transferable_between_spouses | 2028 | source_row | obr_pmd_nov2025:12687:715e2dfb90963806 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__apr_bpr_unused_allowance_transferable_between_spouses | 2029 | source_row | obr_pmd_nov2025:12688:71aa1e3dd1311ea0 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__apr_bpr_unused_allowance_transferable_between_spouses | 2030 | source_row | obr_pmd_nov2025:12689:f47004cbb91db7cc | — | — | — | coverage |
| autumn_budget_2025 | ab2025__british_business_bank_growth_guarantee_scheme | 2025 | source_row | obr_pmd_nov2025:23735:565572611eea5dc7 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__british_business_bank_growth_guarantee_scheme | 2026 | source_row | obr_pmd_nov2025:23736:a45ec80ff9d6f25f | — | — | — | coverage |
| autumn_budget_2025 | ab2025__british_business_bank_growth_guarantee_scheme | 2027 | source_row | obr_pmd_nov2025:23737:f2d3dc4de37192c8 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__british_business_bank_growth_guarantee_scheme | 2028 | source_row | obr_pmd_nov2025:23738:dc7add7d0d7b795c | — | — | — | coverage |
| autumn_budget_2025 | ab2025__british_business_bank_growth_guarantee_scheme | 2029 | source_row | obr_pmd_nov2025:23739:740d34647636730d | — | — | — | coverage |
| autumn_budget_2025 | ab2025__british_business_bank_growth_guarantee_scheme | 2030 | source_row | obr_pmd_nov2025:23740:140ee471237108b0 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__british_coal_staff_superannuation_scheme_reserve_transfer | 2025 | source_row | obr_pmd_nov2025:12690:46b7ef379e15241c | — | — | — | coverage |
| autumn_budget_2025 | ab2025__british_coal_staff_superannuation_scheme_reserve_transfer | 2025 | source_row | obr_pmd_nov2025:12696:1c9a95d220a9d5ec | — | — | — | coverage |
| autumn_budget_2025 | ab2025__british_coal_staff_superannuation_scheme_reserve_transfer | 2025 | source_row | obr_pmd_nov2025:24125:48d66730c7d20b08 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__british_coal_staff_superannuation_scheme_reserve_transfer | 2026 | source_row | obr_pmd_nov2025:12691:b357f77d77e4d2bc | — | — | — | coverage |
| autumn_budget_2025 | ab2025__british_coal_staff_superannuation_scheme_reserve_transfer | 2026 | source_row | obr_pmd_nov2025:12697:9691f289c3a88f30 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__british_coal_staff_superannuation_scheme_reserve_transfer | 2026 | source_row | obr_pmd_nov2025:24126:6825fce747b14578 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__british_coal_staff_superannuation_scheme_reserve_transfer | 2027 | source_row | obr_pmd_nov2025:12692:16824392362abacd | — | — | — | coverage |
| autumn_budget_2025 | ab2025__british_coal_staff_superannuation_scheme_reserve_transfer | 2027 | source_row | obr_pmd_nov2025:12698:158456023dfaa169 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__british_coal_staff_superannuation_scheme_reserve_transfer | 2027 | source_row | obr_pmd_nov2025:24127:cff22fe644a40c51 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__british_coal_staff_superannuation_scheme_reserve_transfer | 2028 | source_row | obr_pmd_nov2025:12693:eeebfaef22935f59 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__british_coal_staff_superannuation_scheme_reserve_transfer | 2028 | source_row | obr_pmd_nov2025:12699:76d1cef992bcfb83 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__british_coal_staff_superannuation_scheme_reserve_transfer | 2028 | source_row | obr_pmd_nov2025:24128:b20107c18163b90b | — | — | — | coverage |
| autumn_budget_2025 | ab2025__british_coal_staff_superannuation_scheme_reserve_transfer | 2029 | source_row | obr_pmd_nov2025:12694:39f5d748b37ab9d1 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__british_coal_staff_superannuation_scheme_reserve_transfer | 2029 | source_row | obr_pmd_nov2025:12700:04389d92401a2c1b | — | — | — | coverage |
| autumn_budget_2025 | ab2025__british_coal_staff_superannuation_scheme_reserve_transfer | 2029 | source_row | obr_pmd_nov2025:24129:85d0315d54e07201 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__british_coal_staff_superannuation_scheme_reserve_transfer | 2030 | source_row | obr_pmd_nov2025:12695:5a208e3ccaed48b5 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__british_coal_staff_superannuation_scheme_reserve_transfer | 2030 | source_row | obr_pmd_nov2025:12701:52845dbea8417bb0 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__british_coal_staff_superannuation_scheme_reserve_transfer | 2030 | source_row | obr_pmd_nov2025:24130:8e14d091d903952e | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_retention_gla_and_pilots | 2025 | source_row | obr_pmd_nov2025:23789:0823667ed4e2a468 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_retention_gla_and_pilots | 2025 | source_row | obr_pmd_nov2025:23795:94ee8d6bda798dbe | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_retention_gla_and_pilots | 2025 | source_row | obr_pmd_nov2025:23801:90c4f8cee2c9d0f9 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_retention_gla_and_pilots | 2025 | source_row | obr_pmd_nov2025:23807:419f2bf3b2433142 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_retention_gla_and_pilots | 2025 | source_row | obr_pmd_nov2025:23813:11ab3f767f101441 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_retention_gla_and_pilots | 2025 | source_row | obr_pmd_nov2025:23819:31d30cc2b318f31c | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_retention_gla_and_pilots | 2026 | source_row | obr_pmd_nov2025:23790:f04c53ff10f68178 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_retention_gla_and_pilots | 2026 | source_row | obr_pmd_nov2025:23796:f7fcb515238f856f | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_retention_gla_and_pilots | 2026 | source_row | obr_pmd_nov2025:23802:2e60f699be7ca1dd | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_retention_gla_and_pilots | 2026 | source_row | obr_pmd_nov2025:23808:accc2b03fb519350 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_retention_gla_and_pilots | 2026 | source_row | obr_pmd_nov2025:23814:5be117b1f57fac7f | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_retention_gla_and_pilots | 2026 | source_row | obr_pmd_nov2025:23820:568734484795b38c | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_retention_gla_and_pilots | 2027 | source_row | obr_pmd_nov2025:23791:00b25ab90b4436fd | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_retention_gla_and_pilots | 2027 | source_row | obr_pmd_nov2025:23797:85dd174a21091903 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_retention_gla_and_pilots | 2027 | source_row | obr_pmd_nov2025:23803:5bbb4d1128e67eb3 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_retention_gla_and_pilots | 2027 | source_row | obr_pmd_nov2025:23809:45fd9580fd6536ab | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_retention_gla_and_pilots | 2027 | source_row | obr_pmd_nov2025:23815:e6f8b6b873d84333 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_retention_gla_and_pilots | 2027 | source_row | obr_pmd_nov2025:23821:33ef26066b0a0a99 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_retention_gla_and_pilots | 2028 | source_row | obr_pmd_nov2025:23792:5dfeba95cb8437ee | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_retention_gla_and_pilots | 2028 | source_row | obr_pmd_nov2025:23798:8e3f1993faaa7904 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_retention_gla_and_pilots | 2028 | source_row | obr_pmd_nov2025:23804:06a84127a4a2ada9 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_retention_gla_and_pilots | 2028 | source_row | obr_pmd_nov2025:23810:4b5617fb2745d918 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_retention_gla_and_pilots | 2028 | source_row | obr_pmd_nov2025:23816:35915daca82a00a2 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_retention_gla_and_pilots | 2028 | source_row | obr_pmd_nov2025:23822:944cab30d7537928 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_retention_gla_and_pilots | 2029 | source_row | obr_pmd_nov2025:23793:78a5420d81c9b32d | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_retention_gla_and_pilots | 2029 | source_row | obr_pmd_nov2025:23799:fe1a7a50e1fecc02 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_retention_gla_and_pilots | 2029 | source_row | obr_pmd_nov2025:23805:2c37c9e6710e6e89 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_retention_gla_and_pilots | 2029 | source_row | obr_pmd_nov2025:23811:8922a33257b51e5c | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_retention_gla_and_pilots | 2029 | source_row | obr_pmd_nov2025:23817:cb38d53f5331964d | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_retention_gla_and_pilots | 2029 | source_row | obr_pmd_nov2025:23823:14ff0c5ba697fffc | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_retention_gla_and_pilots | 2030 | source_row | obr_pmd_nov2025:23794:8d8b3904d3d31a45 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_retention_gla_and_pilots | 2030 | source_row | obr_pmd_nov2025:23800:c91de807e91808b6 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_retention_gla_and_pilots | 2030 | source_row | obr_pmd_nov2025:23806:62bb456cc6c6b1d9 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_retention_gla_and_pilots | 2030 | source_row | obr_pmd_nov2025:23812:266f8f7b8a577061 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_retention_gla_and_pilots | 2030 | source_row | obr_pmd_nov2025:23818:62e42fc53af88f7a | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_retention_gla_and_pilots | 2030 | source_row | obr_pmd_nov2025:23824:bb03ef0d9696ac3e | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier | 2025 | source_row | obr_pmd_nov2025:12138:29edd34b16460548 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier | 2025 | source_row | obr_pmd_nov2025:12144:2cd41ec9f17ba80a | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier | 2025 | source_row | obr_pmd_nov2025:12150:a04cf0f76a09ce06 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier | 2025 | source_row | obr_pmd_nov2025:12156:1636bb1429a3e00a | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier | 2025 | source_row | obr_pmd_nov2025:23663:e6ff42b91f753547 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier | 2025 | source_row | obr_pmd_nov2025:23669:12f6f13c23b9cfc2 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier | 2025 | source_row | obr_pmd_nov2025:23675:517450fa7a3a4792 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier | 2026 | source_row | obr_pmd_nov2025:12139:d6efa97ddf121464 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier | 2026 | source_row | obr_pmd_nov2025:12145:c5150d3f922204ea | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier | 2026 | source_row | obr_pmd_nov2025:12151:032a6e2e551de9e9 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier | 2026 | source_row | obr_pmd_nov2025:12157:598b098a7db201ba | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier | 2026 | source_row | obr_pmd_nov2025:23664:7d0cd59ed5ffd23f | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier | 2026 | source_row | obr_pmd_nov2025:23670:320d01eb5696465c | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier | 2026 | source_row | obr_pmd_nov2025:23676:96495bb03656997b | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier | 2027 | source_row | obr_pmd_nov2025:12140:a3d782103cef363f | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier | 2027 | source_row | obr_pmd_nov2025:12146:2d219d4b4f3ab417 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier | 2027 | source_row | obr_pmd_nov2025:12152:1844c70b0f3ad4f0 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier | 2027 | source_row | obr_pmd_nov2025:12158:1f8914465750eaf4 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier | 2027 | source_row | obr_pmd_nov2025:23665:62c9ac17549a3961 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier | 2027 | source_row | obr_pmd_nov2025:23671:f9a3ec3888ff65c7 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier | 2027 | source_row | obr_pmd_nov2025:23677:cab316c5284835ef | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier | 2028 | source_row | obr_pmd_nov2025:12141:20ff4a4e84d4354f | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier | 2028 | source_row | obr_pmd_nov2025:12147:61698b7debaf0a15 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier | 2028 | source_row | obr_pmd_nov2025:12153:01a3574b35124ea7 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier | 2028 | source_row | obr_pmd_nov2025:12159:3b975ad45201533e | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier | 2028 | source_row | obr_pmd_nov2025:23666:a3b10dc4e33de161 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier | 2028 | source_row | obr_pmd_nov2025:23672:523114267babffd1 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier | 2028 | source_row | obr_pmd_nov2025:23678:c94c3ed3310bd3e9 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier | 2029 | source_row | obr_pmd_nov2025:12142:b040aec451138a46 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier | 2029 | source_row | obr_pmd_nov2025:12148:de078921d50bc912 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier | 2029 | source_row | obr_pmd_nov2025:12154:b49b9ec252821534 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier | 2029 | source_row | obr_pmd_nov2025:12160:28604b116a593dc1 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier | 2029 | source_row | obr_pmd_nov2025:23667:9603969948beddca | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier | 2029 | source_row | obr_pmd_nov2025:23673:7429908588fa3a50 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier | 2029 | source_row | obr_pmd_nov2025:23679:2fde307c7ecea996 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier | 2030 | source_row | obr_pmd_nov2025:12143:d35d40c4b97b2944 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier | 2030 | source_row | obr_pmd_nov2025:12149:3076e2aea9d6a237 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier | 2030 | source_row | obr_pmd_nov2025:12155:87fc96014f9a8ce1 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier | 2030 | source_row | obr_pmd_nov2025:12161:560c0e5e5d795172 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier | 2030 | source_row | obr_pmd_nov2025:23668:ca598a45756bff3a | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier | 2030 | source_row | obr_pmd_nov2025:23674:502419d2560889ad | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier | 2030 | source_row | obr_pmd_nov2025:23680:06bcf16e369a3578 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_transitional_relief_and_supplement | 2025 | source_row | obr_pmd_nov2025:12114:b297e77c2623274b | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_transitional_relief_and_supplement | 2025 | source_row | obr_pmd_nov2025:12120:e3db573a8a005731 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_transitional_relief_and_supplement | 2025 | source_row | obr_pmd_nov2025:12126:23c1bcefc917b39c | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_transitional_relief_and_supplement | 2025 | source_row | obr_pmd_nov2025:12132:fa9d58c81917a6b4 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_transitional_relief_and_supplement | 2025 | source_row | obr_pmd_nov2025:23645:d8d2c193e950efd5 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_transitional_relief_and_supplement | 2025 | source_row | obr_pmd_nov2025:23651:b6e0135f5c59f4ba | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_transitional_relief_and_supplement | 2025 | source_row | obr_pmd_nov2025:23657:7f197afda64059d5 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_transitional_relief_and_supplement | 2026 | source_row | obr_pmd_nov2025:12115:95603c4f9037eebd | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_transitional_relief_and_supplement | 2026 | source_row | obr_pmd_nov2025:12121:309e53b8ea3096a5 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_transitional_relief_and_supplement | 2026 | source_row | obr_pmd_nov2025:12127:a89ba82f3c58a77f | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_transitional_relief_and_supplement | 2026 | source_row | obr_pmd_nov2025:12133:d339e47869edd070 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_transitional_relief_and_supplement | 2026 | source_row | obr_pmd_nov2025:23646:75d57b1fb9860038 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_transitional_relief_and_supplement | 2026 | source_row | obr_pmd_nov2025:23652:2df21f5069f27f96 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_transitional_relief_and_supplement | 2026 | source_row | obr_pmd_nov2025:23658:529f4f8acd07fe72 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_transitional_relief_and_supplement | 2027 | source_row | obr_pmd_nov2025:12116:65b4483168ecbcca | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_transitional_relief_and_supplement | 2027 | source_row | obr_pmd_nov2025:12122:abfda8e927ebb411 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_transitional_relief_and_supplement | 2027 | source_row | obr_pmd_nov2025:12128:29abe8d3b050e995 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_transitional_relief_and_supplement | 2027 | source_row | obr_pmd_nov2025:12134:3ed95420cb1fae11 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_transitional_relief_and_supplement | 2027 | source_row | obr_pmd_nov2025:23647:adcd1ba4a5575cea | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_transitional_relief_and_supplement | 2027 | source_row | obr_pmd_nov2025:23653:892dd98e94be663a | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_transitional_relief_and_supplement | 2027 | source_row | obr_pmd_nov2025:23659:de48ef77e56d4708 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_transitional_relief_and_supplement | 2028 | source_row | obr_pmd_nov2025:12117:5fa20f19609e9a7a | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_transitional_relief_and_supplement | 2028 | source_row | obr_pmd_nov2025:12123:0632257ef9dc5665 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_transitional_relief_and_supplement | 2028 | source_row | obr_pmd_nov2025:12129:d1d0161097d93127 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_transitional_relief_and_supplement | 2028 | source_row | obr_pmd_nov2025:12135:21a38d3223adbf61 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_transitional_relief_and_supplement | 2028 | source_row | obr_pmd_nov2025:23648:ee6c74c0cca1d898 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_transitional_relief_and_supplement | 2028 | source_row | obr_pmd_nov2025:23654:75d5fe4848618fbc | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_transitional_relief_and_supplement | 2028 | source_row | obr_pmd_nov2025:23660:de167f73c73604c0 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_transitional_relief_and_supplement | 2029 | source_row | obr_pmd_nov2025:12118:e7dbf792e8878d27 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_transitional_relief_and_supplement | 2029 | source_row | obr_pmd_nov2025:12124:993d9a1548bf2980 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_transitional_relief_and_supplement | 2029 | source_row | obr_pmd_nov2025:12130:780e154153fc8637 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_transitional_relief_and_supplement | 2029 | source_row | obr_pmd_nov2025:12136:a44a56692b7ca514 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_transitional_relief_and_supplement | 2029 | source_row | obr_pmd_nov2025:23649:ced124f81fc9443c | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_transitional_relief_and_supplement | 2029 | source_row | obr_pmd_nov2025:23655:7e0aaa355393f716 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_transitional_relief_and_supplement | 2029 | source_row | obr_pmd_nov2025:23661:b6193921058bc57e | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_transitional_relief_and_supplement | 2030 | source_row | obr_pmd_nov2025:12119:2d69b7e021ca5ae4 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_transitional_relief_and_supplement | 2030 | source_row | obr_pmd_nov2025:12125:2afa3e3fe885ef9c | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_transitional_relief_and_supplement | 2030 | source_row | obr_pmd_nov2025:12131:0e62ed9994f5c298 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_transitional_relief_and_supplement | 2030 | source_row | obr_pmd_nov2025:12137:e7f7bb04e629cbb9 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_transitional_relief_and_supplement | 2030 | source_row | obr_pmd_nov2025:23650:af0fce7fbea68d8d | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_transitional_relief_and_supplement | 2030 | source_row | obr_pmd_nov2025:23656:0b489bfb45a4742a | — | — | — | coverage |
| autumn_budget_2025 | ab2025__business_rates_transitional_relief_and_supplement | 2030 | source_row | obr_pmd_nov2025:23662:3f0ef3bf25c1f8d5 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__carers_allowance_overpayments_review | 2025 | source_row | obr_pmd_nov2025:23549:112d57419951fde5 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__carers_allowance_overpayments_review | 2025 | source_row | obr_pmd_nov2025:23555:b831fbbbf86eb6c8 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__carers_allowance_overpayments_review | 2025 | source_row | obr_pmd_nov2025:23561:9bae2101918d5839 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__carers_allowance_overpayments_review | 2026 | source_row | obr_pmd_nov2025:23550:cd6402cbacc8e48e | — | — | — | coverage |
| autumn_budget_2025 | ab2025__carers_allowance_overpayments_review | 2026 | source_row | obr_pmd_nov2025:23556:4ff9107569db4e50 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__carers_allowance_overpayments_review | 2026 | source_row | obr_pmd_nov2025:23562:097f75acd04d91ec | — | — | — | coverage |
| autumn_budget_2025 | ab2025__carers_allowance_overpayments_review | 2027 | source_row | obr_pmd_nov2025:23551:58a4336802093431 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__carers_allowance_overpayments_review | 2027 | source_row | obr_pmd_nov2025:23557:b4013104476436a7 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__carers_allowance_overpayments_review | 2027 | source_row | obr_pmd_nov2025:23563:2e13daff8edafd6d | — | — | — | coverage |
| autumn_budget_2025 | ab2025__carers_allowance_overpayments_review | 2028 | source_row | obr_pmd_nov2025:23552:e13352560d197fc5 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__carers_allowance_overpayments_review | 2028 | source_row | obr_pmd_nov2025:23558:cfb15636c1b1f021 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__carers_allowance_overpayments_review | 2028 | source_row | obr_pmd_nov2025:23564:2d9cdc796eeee56e | — | — | — | coverage |
| autumn_budget_2025 | ab2025__carers_allowance_overpayments_review | 2029 | source_row | obr_pmd_nov2025:23553:4e75e3b2af35f2e0 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__carers_allowance_overpayments_review | 2029 | source_row | obr_pmd_nov2025:23559:51be39604064b82b | — | — | — | coverage |
| autumn_budget_2025 | ab2025__carers_allowance_overpayments_review | 2029 | source_row | obr_pmd_nov2025:23565:b42823e157f61608 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__carers_allowance_overpayments_review | 2030 | source_row | obr_pmd_nov2025:23554:86904a2977990d0c | — | — | — | coverage |
| autumn_budget_2025 | ab2025__carers_allowance_overpayments_review | 2030 | source_row | obr_pmd_nov2025:23560:9cd21dd8eda495b4 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__carers_allowance_overpayments_review | 2030 | source_row | obr_pmd_nov2025:23566:2559d0cd19719b74 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__cbam_indirect_emissions_removed | 2025 | source_row | obr_pmd_nov2025:12582:720587433099c69f | — | — | — | coverage |
| autumn_budget_2025 | ab2025__cbam_indirect_emissions_removed | 2026 | source_row | obr_pmd_nov2025:12583:6258a69e3273c060 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__cbam_indirect_emissions_removed | 2027 | source_row | obr_pmd_nov2025:12584:7e45d4f29c5dd7ea | — | — | — | coverage |
| autumn_budget_2025 | ab2025__cbam_indirect_emissions_removed | 2028 | source_row | obr_pmd_nov2025:12585:86fae73495de4dc0 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__cbam_indirect_emissions_removed | 2029 | source_row | obr_pmd_nov2025:12586:02cb957f1fd3ba6c | — | — | — | coverage |
| autumn_budget_2025 | ab2025__cbam_indirect_emissions_removed | 2030 | source_row | obr_pmd_nov2025:12587:f6bb95801c8e98e4 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__cgt_employee_ownership_trust_relief_cut_to_50pct | 2025 | source_row | obr_pmd_nov2025:12354:a243dd3fbba60585 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__cgt_employee_ownership_trust_relief_cut_to_50pct | 2025 | source_row | obr_pmd_nov2025:12360:22e0ccdc5a9d581a | — | — | — | coverage |
| autumn_budget_2025 | ab2025__cgt_employee_ownership_trust_relief_cut_to_50pct | 2025 | source_row | obr_pmd_nov2025:23975:18ad4b3b872bfb44 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__cgt_employee_ownership_trust_relief_cut_to_50pct | 2025 | source_row | obr_pmd_nov2025:23981:53c85bfa84f289e3 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__cgt_employee_ownership_trust_relief_cut_to_50pct | 2026 | source_row | obr_pmd_nov2025:12355:f39321421b5c5146 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__cgt_employee_ownership_trust_relief_cut_to_50pct | 2026 | source_row | obr_pmd_nov2025:12361:3d3cb7cb3acd2fef | — | — | — | coverage |
| autumn_budget_2025 | ab2025__cgt_employee_ownership_trust_relief_cut_to_50pct | 2026 | source_row | obr_pmd_nov2025:23976:7ebded74e51c2efa | — | — | — | coverage |
| autumn_budget_2025 | ab2025__cgt_employee_ownership_trust_relief_cut_to_50pct | 2026 | source_row | obr_pmd_nov2025:23982:5d3375c84812c7b8 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__cgt_employee_ownership_trust_relief_cut_to_50pct | 2027 | source_row | obr_pmd_nov2025:12356:03cf00e183475a86 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__cgt_employee_ownership_trust_relief_cut_to_50pct | 2027 | source_row | obr_pmd_nov2025:12362:64c44a566554cfe0 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__cgt_employee_ownership_trust_relief_cut_to_50pct | 2027 | source_row | obr_pmd_nov2025:23977:59b5ada8fd875923 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__cgt_employee_ownership_trust_relief_cut_to_50pct | 2027 | source_row | obr_pmd_nov2025:23983:eebdd3afacc7b418 | — | — | — | coverage |
| autumn_budget_2025 | ab2025__cgt_employee_ownership_trust_relief_cut_to_50pct | 2028 | source_row | obr_pmd_nov2025:12357:acd3d501bfb4a697 | — | — | — | coverage |

## Years supported on one side only

Each has a packet; the population of one release cannot supply the year.

| Event | CY | Level | Rows |
|---|---:|---|---:|
| autumn_statement_2023 | 2023 | measure_year | 4 |
| autumn_statement_2023 | 2023 | source_row | 14 |
| spring_budget_2023 | 2023 | measure_year | 2 |
| spring_budget_2023 | 2023 | source_row | 3 |
| spring_budget_2024 | 2023 | measure_year | 3 |
| spring_budget_2024 | 2023 | source_row | 8 |

## PE/OBR ratio-bin transitions (source rows on both sides)

### autumn_budget_2024

| Base bin | Head bin | Rows |
|---|---|---:|
| both_zero | both_zero | 2 |
| not_available | not_available | 1100 |
| not_available | obr_zero | 1 |
| opposite_sign | opposite_sign | 2 |
| same_sign_ratio_0.8_to_1.25 | same_sign_ratio_0.8_to_1.25 | 5 |
| same_sign_ratio_0.8_to_1.25 | same_sign_ratio_1.25_to_2 | 5 |
| same_sign_ratio_1.25_to_2 | same_sign_ratio_0.8_to_1.25 | 1 |
| same_sign_ratio_at_least_2 | same_sign_ratio_at_least_2 | 13 |
| same_sign_ratio_below_0.5 | same_sign_ratio_below_0.5 | 5 |

### autumn_budget_2025

| Base bin | Head bin | Rows |
|---|---|---:|
| — | — | 0 |

### autumn_statement_2023

| Base bin | Head bin | Rows |
|---|---|---:|
| both_zero | both_zero | 2 |
| both_zero | not_available | 7 |
| not_available | not_available | 1059 |
| pe_zero | pe_zero | 13 |
| same_sign_ratio_0.5_to_0.8 | same_sign_ratio_1.25_to_2 | 9 |
| same_sign_ratio_0.5_to_0.8 | same_sign_ratio_at_least_2 | 1 |
| same_sign_ratio_0.8_to_1.25 | same_sign_ratio_0.8_to_1.25 | 1 |
| same_sign_ratio_0.8_to_1.25 | same_sign_ratio_at_least_2 | 2 |
| same_sign_ratio_1.25_to_2 | same_sign_ratio_0.8_to_1.25 | 6 |
| same_sign_ratio_1.25_to_2 | same_sign_ratio_1.25_to_2 | 6 |
| same_sign_ratio_1.25_to_2 | same_sign_ratio_at_least_2 | 7 |
| same_sign_ratio_at_least_2 | same_sign_ratio_1.25_to_2 | 2 |
| same_sign_ratio_at_least_2 | same_sign_ratio_at_least_2 | 1 |

### spring_budget_2023

| Base bin | Head bin | Rows |
|---|---|---:|
| not_available | not_available | 1005 |
| pe_zero | not_available | 1 |
| pe_zero | pe_zero | 4 |
| same_sign_ratio_at_least_2 | not_available | 1 |
| same_sign_ratio_at_least_2 | same_sign_ratio_at_least_2 | 4 |
| same_sign_ratio_below_0.5 | not_available | 1 |
| same_sign_ratio_below_0.5 | same_sign_ratio_at_least_2 | 4 |

### spring_budget_2024

| Base bin | Head bin | Rows |
|---|---|---:|
| both_zero | both_zero | 2 |
| both_zero | not_available | 8 |
| not_available | not_available | 768 |
| pe_zero | pe_zero | 8 |
| pe_zero | same_sign_ratio_0.5_to_0.8 | 4 |
| pe_zero | same_sign_ratio_0.8_to_1.25 | 1 |
| same_sign_ratio_0.5_to_0.8 | same_sign_ratio_1.25_to_2 | 4 |
| same_sign_ratio_0.5_to_0.8 | same_sign_ratio_at_least_2 | 1 |
| same_sign_ratio_0.8_to_1.25 | same_sign_ratio_0.8_to_1.25 | 2 |
| same_sign_ratio_0.8_to_1.25 | same_sign_ratio_at_least_2 | 3 |
| same_sign_ratio_1.25_to_2 | same_sign_ratio_0.8_to_1.25 | 8 |
| same_sign_ratio_1.25_to_2 | same_sign_ratio_at_least_2 | 2 |
| same_sign_ratio_at_least_2 | same_sign_ratio_at_least_2 | 5 |

### spring_statement_2025

| Base bin | Head bin | Rows |
|---|---|---:|
| both_zero | both_zero | 4 |
| not_available | not_available | 486 |
| same_sign_ratio_0.5_to_0.8 | same_sign_ratio_0.8_to_1.25 | 1 |
| same_sign_ratio_below_0.5 | same_sign_ratio_0.5_to_0.8 | 3 |
| same_sign_ratio_below_0.5 | same_sign_ratio_0.8_to_1.25 | 1 |
| same_sign_ratio_below_0.5 | same_sign_ratio_below_0.5 | 3 |

## Investigation packets

* [autumn_budget_2024__capital_gains_main_rates_and_reliefs__2024](packets/autumn_budget_2024__capital_gains_main_rates_and_reliefs__2024.md)
* [autumn_budget_2024__capital_gains_main_rates_and_reliefs__2025](packets/autumn_budget_2024__capital_gains_main_rates_and_reliefs__2025.md)
* [autumn_budget_2024__capital_gains_main_rates_and_reliefs__2026](packets/autumn_budget_2024__capital_gains_main_rates_and_reliefs__2026.md)
* [autumn_budget_2024__capital_gains_main_rates_and_reliefs__2027](packets/autumn_budget_2024__capital_gains_main_rates_and_reliefs__2027.md)
* [autumn_budget_2024__capital_gains_main_rates_and_reliefs__2028](packets/autumn_budget_2024__capital_gains_main_rates_and_reliefs__2028.md)
* [autumn_budget_2024__capital_gains_main_rates_and_reliefs__2029](packets/autumn_budget_2024__capital_gains_main_rates_and_reliefs__2029.md)
* [autumn_budget_2024__employer_nics_package__2025](packets/autumn_budget_2024__employer_nics_package__2025.md)
* [autumn_budget_2024__employer_nics_package__2026](packets/autumn_budget_2024__employer_nics_package__2026.md)
* [autumn_budget_2024__employer_nics_package__2027](packets/autumn_budget_2024__employer_nics_package__2027.md)
* [autumn_budget_2024__employer_nics_package__2028](packets/autumn_budget_2024__employer_nics_package__2028.md)
* [autumn_budget_2024__employer_nics_package__2029](packets/autumn_budget_2024__employer_nics_package__2029.md)
* [autumn_budget_2024__private_school_vat_20pct__2025](packets/autumn_budget_2024__private_school_vat_20pct__2025.md)
* [autumn_budget_2024__private_school_vat_20pct__2026](packets/autumn_budget_2024__private_school_vat_20pct__2026.md)
* [autumn_budget_2024__private_school_vat_20pct__2027](packets/autumn_budget_2024__private_school_vat_20pct__2027.md)
* [autumn_budget_2024__private_school_vat_20pct__2028](packets/autumn_budget_2024__private_school_vat_20pct__2028.md)
* [autumn_budget_2024__private_school_vat_20pct__2029](packets/autumn_budget_2024__private_school_vat_20pct__2029.md)
* [autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp__2025](packets/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp__2025.md)
* [autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp__2026](packets/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp__2026.md)
* [autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp__2027](packets/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp__2027.md)
* [autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp__2028](packets/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp__2028.md)
* [autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp__2029](packets/autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp__2029.md)
* [autumn_budget_2024__winter_fuel_means_test__2024](packets/autumn_budget_2024__winter_fuel_means_test__2024.md)
* [autumn_budget_2024__winter_fuel_means_test__2025](packets/autumn_budget_2024__winter_fuel_means_test__2025.md)
* [autumn_budget_2024__winter_fuel_means_test__2026](packets/autumn_budget_2024__winter_fuel_means_test__2026.md)
* [autumn_budget_2024__winter_fuel_means_test__2027](packets/autumn_budget_2024__winter_fuel_means_test__2027.md)
* [autumn_budget_2024__winter_fuel_means_test__2028](packets/autumn_budget_2024__winter_fuel_means_test__2028.md)
* [autumn_budget_2024__winter_fuel_means_test__2029](packets/autumn_budget_2024__winter_fuel_means_test__2029.md)
* [autumn_budget_2025__ab2025__advanced_corporation_tax_shadow_act_abolished__2025](packets/autumn_budget_2025__ab2025__advanced_corporation_tax_shadow_act_abolished__2025.md)
* [autumn_budget_2025__ab2025__advanced_corporation_tax_shadow_act_abolished__2026](packets/autumn_budget_2025__ab2025__advanced_corporation_tax_shadow_act_abolished__2026.md)
* [autumn_budget_2025__ab2025__advanced_corporation_tax_shadow_act_abolished__2027](packets/autumn_budget_2025__ab2025__advanced_corporation_tax_shadow_act_abolished__2027.md)
* [autumn_budget_2025__ab2025__advanced_corporation_tax_shadow_act_abolished__2028](packets/autumn_budget_2025__ab2025__advanced_corporation_tax_shadow_act_abolished__2028.md)
* [autumn_budget_2025__ab2025__advanced_corporation_tax_shadow_act_abolished__2029](packets/autumn_budget_2025__ab2025__advanced_corporation_tax_shadow_act_abolished__2029.md)
* [autumn_budget_2025__ab2025__advanced_corporation_tax_shadow_act_abolished__2030](packets/autumn_budget_2025__ab2025__advanced_corporation_tax_shadow_act_abolished__2030.md)
* [autumn_budget_2025__ab2025__apd_higher_rate_extended_to_private_jets__2025](packets/autumn_budget_2025__ab2025__apd_higher_rate_extended_to_private_jets__2025.md)
* [autumn_budget_2025__ab2025__apd_higher_rate_extended_to_private_jets__2026](packets/autumn_budget_2025__ab2025__apd_higher_rate_extended_to_private_jets__2026.md)
* [autumn_budget_2025__ab2025__apd_higher_rate_extended_to_private_jets__2027](packets/autumn_budget_2025__ab2025__apd_higher_rate_extended_to_private_jets__2027.md)
* [autumn_budget_2025__ab2025__apd_higher_rate_extended_to_private_jets__2028](packets/autumn_budget_2025__ab2025__apd_higher_rate_extended_to_private_jets__2028.md)
* [autumn_budget_2025__ab2025__apd_higher_rate_extended_to_private_jets__2029](packets/autumn_budget_2025__ab2025__apd_higher_rate_extended_to_private_jets__2029.md)
* [autumn_budget_2025__ab2025__apd_higher_rate_extended_to_private_jets__2030](packets/autumn_budget_2025__ab2025__apd_higher_rate_extended_to_private_jets__2030.md)
* [autumn_budget_2025__ab2025__apr_bpr_unused_allowance_transferable_between_spouses__2025](packets/autumn_budget_2025__ab2025__apr_bpr_unused_allowance_transferable_between_spouses__2025.md)
* [autumn_budget_2025__ab2025__apr_bpr_unused_allowance_transferable_between_spouses__2026](packets/autumn_budget_2025__ab2025__apr_bpr_unused_allowance_transferable_between_spouses__2026.md)
* [autumn_budget_2025__ab2025__apr_bpr_unused_allowance_transferable_between_spouses__2027](packets/autumn_budget_2025__ab2025__apr_bpr_unused_allowance_transferable_between_spouses__2027.md)
* [autumn_budget_2025__ab2025__apr_bpr_unused_allowance_transferable_between_spouses__2028](packets/autumn_budget_2025__ab2025__apr_bpr_unused_allowance_transferable_between_spouses__2028.md)
* [autumn_budget_2025__ab2025__apr_bpr_unused_allowance_transferable_between_spouses__2029](packets/autumn_budget_2025__ab2025__apr_bpr_unused_allowance_transferable_between_spouses__2029.md)
* [autumn_budget_2025__ab2025__apr_bpr_unused_allowance_transferable_between_spouses__2030](packets/autumn_budget_2025__ab2025__apr_bpr_unused_allowance_transferable_between_spouses__2030.md)
* [autumn_budget_2025__ab2025__british_business_bank_growth_guarantee_scheme__2025](packets/autumn_budget_2025__ab2025__british_business_bank_growth_guarantee_scheme__2025.md)
* [autumn_budget_2025__ab2025__british_business_bank_growth_guarantee_scheme__2026](packets/autumn_budget_2025__ab2025__british_business_bank_growth_guarantee_scheme__2026.md)
* [autumn_budget_2025__ab2025__british_business_bank_growth_guarantee_scheme__2027](packets/autumn_budget_2025__ab2025__british_business_bank_growth_guarantee_scheme__2027.md)
* [autumn_budget_2025__ab2025__british_business_bank_growth_guarantee_scheme__2028](packets/autumn_budget_2025__ab2025__british_business_bank_growth_guarantee_scheme__2028.md)
* [autumn_budget_2025__ab2025__british_business_bank_growth_guarantee_scheme__2029](packets/autumn_budget_2025__ab2025__british_business_bank_growth_guarantee_scheme__2029.md)
* [autumn_budget_2025__ab2025__british_business_bank_growth_guarantee_scheme__2030](packets/autumn_budget_2025__ab2025__british_business_bank_growth_guarantee_scheme__2030.md)
* [autumn_budget_2025__ab2025__british_coal_staff_superannuation_scheme_reserve_transfer__2025](packets/autumn_budget_2025__ab2025__british_coal_staff_superannuation_scheme_reserve_transfer__2025.md)
* [autumn_budget_2025__ab2025__british_coal_staff_superannuation_scheme_reserve_transfer__2026](packets/autumn_budget_2025__ab2025__british_coal_staff_superannuation_scheme_reserve_transfer__2026.md)
* [autumn_budget_2025__ab2025__british_coal_staff_superannuation_scheme_reserve_transfer__2027](packets/autumn_budget_2025__ab2025__british_coal_staff_superannuation_scheme_reserve_transfer__2027.md)
* [autumn_budget_2025__ab2025__british_coal_staff_superannuation_scheme_reserve_transfer__2028](packets/autumn_budget_2025__ab2025__british_coal_staff_superannuation_scheme_reserve_transfer__2028.md)
* [autumn_budget_2025__ab2025__british_coal_staff_superannuation_scheme_reserve_transfer__2029](packets/autumn_budget_2025__ab2025__british_coal_staff_superannuation_scheme_reserve_transfer__2029.md)
* [autumn_budget_2025__ab2025__british_coal_staff_superannuation_scheme_reserve_transfer__2030](packets/autumn_budget_2025__ab2025__british_coal_staff_superannuation_scheme_reserve_transfer__2030.md)
* [autumn_budget_2025__ab2025__business_rates_retention_gla_and_pilots__2025](packets/autumn_budget_2025__ab2025__business_rates_retention_gla_and_pilots__2025.md)
* [autumn_budget_2025__ab2025__business_rates_retention_gla_and_pilots__2026](packets/autumn_budget_2025__ab2025__business_rates_retention_gla_and_pilots__2026.md)
* [autumn_budget_2025__ab2025__business_rates_retention_gla_and_pilots__2027](packets/autumn_budget_2025__ab2025__business_rates_retention_gla_and_pilots__2027.md)
* [autumn_budget_2025__ab2025__business_rates_retention_gla_and_pilots__2028](packets/autumn_budget_2025__ab2025__business_rates_retention_gla_and_pilots__2028.md)
* [autumn_budget_2025__ab2025__business_rates_retention_gla_and_pilots__2029](packets/autumn_budget_2025__ab2025__business_rates_retention_gla_and_pilots__2029.md)
* [autumn_budget_2025__ab2025__business_rates_retention_gla_and_pilots__2030](packets/autumn_budget_2025__ab2025__business_rates_retention_gla_and_pilots__2030.md)
* [autumn_budget_2025__ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier__2025](packets/autumn_budget_2025__ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier__2025.md)
* [autumn_budget_2025__ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier__2026](packets/autumn_budget_2025__ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier__2026.md)
* [autumn_budget_2025__ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier__2027](packets/autumn_budget_2025__ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier__2027.md)
* [autumn_budget_2025__ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier__2028](packets/autumn_budget_2025__ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier__2028.md)
* [autumn_budget_2025__ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier__2029](packets/autumn_budget_2025__ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier__2029.md)
* [autumn_budget_2025__ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier__2030](packets/autumn_budget_2025__ab2025__business_rates_rhl_lower_multipliers_and_high_value_multiplier__2030.md)
* [autumn_budget_2025__ab2025__business_rates_transitional_relief_and_supplement__2025](packets/autumn_budget_2025__ab2025__business_rates_transitional_relief_and_supplement__2025.md)
* [autumn_budget_2025__ab2025__business_rates_transitional_relief_and_supplement__2026](packets/autumn_budget_2025__ab2025__business_rates_transitional_relief_and_supplement__2026.md)
* [autumn_budget_2025__ab2025__business_rates_transitional_relief_and_supplement__2027](packets/autumn_budget_2025__ab2025__business_rates_transitional_relief_and_supplement__2027.md)
* [autumn_budget_2025__ab2025__business_rates_transitional_relief_and_supplement__2028](packets/autumn_budget_2025__ab2025__business_rates_transitional_relief_and_supplement__2028.md)
* [autumn_budget_2025__ab2025__business_rates_transitional_relief_and_supplement__2029](packets/autumn_budget_2025__ab2025__business_rates_transitional_relief_and_supplement__2029.md)
* [autumn_budget_2025__ab2025__business_rates_transitional_relief_and_supplement__2030](packets/autumn_budget_2025__ab2025__business_rates_transitional_relief_and_supplement__2030.md)
* [autumn_budget_2025__ab2025__carers_allowance_overpayments_review__2025](packets/autumn_budget_2025__ab2025__carers_allowance_overpayments_review__2025.md)
* [autumn_budget_2025__ab2025__carers_allowance_overpayments_review__2026](packets/autumn_budget_2025__ab2025__carers_allowance_overpayments_review__2026.md)
* [autumn_budget_2025__ab2025__carers_allowance_overpayments_review__2027](packets/autumn_budget_2025__ab2025__carers_allowance_overpayments_review__2027.md)
* [autumn_budget_2025__ab2025__carers_allowance_overpayments_review__2028](packets/autumn_budget_2025__ab2025__carers_allowance_overpayments_review__2028.md)
* [autumn_budget_2025__ab2025__carers_allowance_overpayments_review__2029](packets/autumn_budget_2025__ab2025__carers_allowance_overpayments_review__2029.md)
* [autumn_budget_2025__ab2025__carers_allowance_overpayments_review__2030](packets/autumn_budget_2025__ab2025__carers_allowance_overpayments_review__2030.md)
* [autumn_budget_2025__ab2025__cbam_indirect_emissions_removed__2025](packets/autumn_budget_2025__ab2025__cbam_indirect_emissions_removed__2025.md)
* [autumn_budget_2025__ab2025__cbam_indirect_emissions_removed__2026](packets/autumn_budget_2025__ab2025__cbam_indirect_emissions_removed__2026.md)
* [autumn_budget_2025__ab2025__cbam_indirect_emissions_removed__2027](packets/autumn_budget_2025__ab2025__cbam_indirect_emissions_removed__2027.md)
* [autumn_budget_2025__ab2025__cbam_indirect_emissions_removed__2028](packets/autumn_budget_2025__ab2025__cbam_indirect_emissions_removed__2028.md)
* [autumn_budget_2025__ab2025__cbam_indirect_emissions_removed__2029](packets/autumn_budget_2025__ab2025__cbam_indirect_emissions_removed__2029.md)
* [autumn_budget_2025__ab2025__cbam_indirect_emissions_removed__2030](packets/autumn_budget_2025__ab2025__cbam_indirect_emissions_removed__2030.md)
* [autumn_budget_2025__ab2025__cgt_employee_ownership_trust_relief_cut_to_50pct__2025](packets/autumn_budget_2025__ab2025__cgt_employee_ownership_trust_relief_cut_to_50pct__2025.md)
* [autumn_budget_2025__ab2025__cgt_employee_ownership_trust_relief_cut_to_50pct__2026](packets/autumn_budget_2025__ab2025__cgt_employee_ownership_trust_relief_cut_to_50pct__2026.md)
* [autumn_budget_2025__ab2025__cgt_employee_ownership_trust_relief_cut_to_50pct__2027](packets/autumn_budget_2025__ab2025__cgt_employee_ownership_trust_relief_cut_to_50pct__2027.md)
* [autumn_budget_2025__ab2025__cgt_employee_ownership_trust_relief_cut_to_50pct__2028](packets/autumn_budget_2025__ab2025__cgt_employee_ownership_trust_relief_cut_to_50pct__2028.md)
* [autumn_budget_2025__ab2025__cgt_employee_ownership_trust_relief_cut_to_50pct__2029](packets/autumn_budget_2025__ab2025__cgt_employee_ownership_trust_relief_cut_to_50pct__2029.md)
* [autumn_budget_2025__ab2025__cgt_employee_ownership_trust_relief_cut_to_50pct__2030](packets/autumn_budget_2025__ab2025__cgt_employee_ownership_trust_relief_cut_to_50pct__2030.md)
* [autumn_budget_2025__ab2025__child_benefit_16_19_illness_disability_12_hour_rule_exemption__2025](packets/autumn_budget_2025__ab2025__child_benefit_16_19_illness_disability_12_hour_rule_exemption__2025.md)
* [autumn_budget_2025__ab2025__child_benefit_16_19_illness_disability_12_hour_rule_exemption__2026](packets/autumn_budget_2025__ab2025__child_benefit_16_19_illness_disability_12_hour_rule_exemption__2026.md)
* [autumn_budget_2025__ab2025__child_benefit_16_19_illness_disability_12_hour_rule_exemption__2027](packets/autumn_budget_2025__ab2025__child_benefit_16_19_illness_disability_12_hour_rule_exemption__2027.md)
* [autumn_budget_2025__ab2025__child_benefit_16_19_illness_disability_12_hour_rule_exemption__2028](packets/autumn_budget_2025__ab2025__child_benefit_16_19_illness_disability_12_hour_rule_exemption__2028.md)
* [autumn_budget_2025__ab2025__child_benefit_16_19_illness_disability_12_hour_rule_exemption__2029](packets/autumn_budget_2025__ab2025__child_benefit_16_19_illness_disability_12_hour_rule_exemption__2029.md)
* [autumn_budget_2025__ab2025__child_benefit_16_19_illness_disability_12_hour_rule_exemption__2030](packets/autumn_budget_2025__ab2025__child_benefit_16_19_illness_disability_12_hour_rule_exemption__2030.md)
* [autumn_budget_2025__ab2025__compensation_payments_post_office_capture_and_infected_blood__2025](packets/autumn_budget_2025__ab2025__compensation_payments_post_office_capture_and_infected_blood__2025.md)
* [autumn_budget_2025__ab2025__compensation_payments_post_office_capture_and_infected_blood__2026](packets/autumn_budget_2025__ab2025__compensation_payments_post_office_capture_and_infected_blood__2026.md)
* [autumn_budget_2025__ab2025__compensation_payments_post_office_capture_and_infected_blood__2027](packets/autumn_budget_2025__ab2025__compensation_payments_post_office_capture_and_infected_blood__2027.md)
* [autumn_budget_2025__ab2025__compensation_payments_post_office_capture_and_infected_blood__2028](packets/autumn_budget_2025__ab2025__compensation_payments_post_office_capture_and_infected_blood__2028.md)
* [autumn_budget_2025__ab2025__compensation_payments_post_office_capture_and_infected_blood__2029](packets/autumn_budget_2025__ab2025__compensation_payments_post_office_capture_and_infected_blood__2029.md)
* [autumn_budget_2025__ab2025__compensation_payments_post_office_capture_and_infected_blood__2030](packets/autumn_budget_2025__ab2025__compensation_payments_post_office_capture_and_infected_blood__2030.md)
* [autumn_budget_2025__ab2025__cross_border_vat_grouping_reverted__2025](packets/autumn_budget_2025__ab2025__cross_border_vat_grouping_reverted__2025.md)
* [autumn_budget_2025__ab2025__cross_border_vat_grouping_reverted__2026](packets/autumn_budget_2025__ab2025__cross_border_vat_grouping_reverted__2026.md)
* [autumn_budget_2025__ab2025__cross_border_vat_grouping_reverted__2027](packets/autumn_budget_2025__ab2025__cross_border_vat_grouping_reverted__2027.md)
* [autumn_budget_2025__ab2025__cross_border_vat_grouping_reverted__2028](packets/autumn_budget_2025__ab2025__cross_border_vat_grouping_reverted__2028.md)
* [autumn_budget_2025__ab2025__cross_border_vat_grouping_reverted__2029](packets/autumn_budget_2025__ab2025__cross_border_vat_grouping_reverted__2029.md)
* [autumn_budget_2025__ab2025__cross_border_vat_grouping_reverted__2030](packets/autumn_budget_2025__ab2025__cross_border_vat_grouping_reverted__2030.md)
* [autumn_budget_2025__ab2025__db_pension_scheme_surplus_extraction__2025](packets/autumn_budget_2025__ab2025__db_pension_scheme_surplus_extraction__2025.md)
* [autumn_budget_2025__ab2025__db_pension_scheme_surplus_extraction__2026](packets/autumn_budget_2025__ab2025__db_pension_scheme_surplus_extraction__2026.md)
* [autumn_budget_2025__ab2025__db_pension_scheme_surplus_extraction__2027](packets/autumn_budget_2025__ab2025__db_pension_scheme_surplus_extraction__2027.md)
* [autumn_budget_2025__ab2025__db_pension_scheme_surplus_extraction__2028](packets/autumn_budget_2025__ab2025__db_pension_scheme_surplus_extraction__2028.md)
* [autumn_budget_2025__ab2025__db_pension_scheme_surplus_extraction__2029](packets/autumn_budget_2025__ab2025__db_pension_scheme_surplus_extraction__2029.md)
* [autumn_budget_2025__ab2025__db_pension_scheme_surplus_extraction__2030](packets/autumn_budget_2025__ab2025__db_pension_scheme_surplus_extraction__2030.md)
* [autumn_budget_2025__ab2025__dividend_rates_plus_2pp__2025](packets/autumn_budget_2025__ab2025__dividend_rates_plus_2pp__2025.md)
* [autumn_budget_2025__ab2025__dividend_rates_plus_2pp__2026](packets/autumn_budget_2025__ab2025__dividend_rates_plus_2pp__2026.md)
* [autumn_budget_2025__ab2025__dividend_rates_plus_2pp__2027](packets/autumn_budget_2025__ab2025__dividend_rates_plus_2pp__2027.md)
* [autumn_budget_2025__ab2025__dividend_rates_plus_2pp__2028](packets/autumn_budget_2025__ab2025__dividend_rates_plus_2pp__2028.md)
* [autumn_budget_2025__ab2025__dividend_rates_plus_2pp__2029](packets/autumn_budget_2025__ab2025__dividend_rates_plus_2pp__2029.md)
* [autumn_budget_2025__ab2025__dividend_rates_plus_2pp__2030](packets/autumn_budget_2025__ab2025__dividend_rates_plus_2pp__2030.md)
* [autumn_budget_2025__ab2025__dwp_fraud_and_error_pension_credit_accuracy_reviews__2025](packets/autumn_budget_2025__ab2025__dwp_fraud_and_error_pension_credit_accuracy_reviews__2025.md)
* [autumn_budget_2025__ab2025__dwp_fraud_and_error_pension_credit_accuracy_reviews__2026](packets/autumn_budget_2025__ab2025__dwp_fraud_and_error_pension_credit_accuracy_reviews__2026.md)
* [autumn_budget_2025__ab2025__dwp_fraud_and_error_pension_credit_accuracy_reviews__2027](packets/autumn_budget_2025__ab2025__dwp_fraud_and_error_pension_credit_accuracy_reviews__2027.md)
* [autumn_budget_2025__ab2025__dwp_fraud_and_error_pension_credit_accuracy_reviews__2028](packets/autumn_budget_2025__ab2025__dwp_fraud_and_error_pension_credit_accuracy_reviews__2028.md)
* [autumn_budget_2025__ab2025__dwp_fraud_and_error_pension_credit_accuracy_reviews__2029](packets/autumn_budget_2025__ab2025__dwp_fraud_and_error_pension_credit_accuracy_reviews__2029.md)
* [autumn_budget_2025__ab2025__dwp_fraud_and_error_pension_credit_accuracy_reviews__2030](packets/autumn_budget_2025__ab2025__dwp_fraud_and_error_pension_credit_accuracy_reviews__2030.md)
* [autumn_budget_2025__ab2025__dwp_fraud_and_error_uc_targeted_case_review_extended__2025](packets/autumn_budget_2025__ab2025__dwp_fraud_and_error_uc_targeted_case_review_extended__2025.md)
* [autumn_budget_2025__ab2025__dwp_fraud_and_error_uc_targeted_case_review_extended__2026](packets/autumn_budget_2025__ab2025__dwp_fraud_and_error_uc_targeted_case_review_extended__2026.md)
* [autumn_budget_2025__ab2025__dwp_fraud_and_error_uc_targeted_case_review_extended__2027](packets/autumn_budget_2025__ab2025__dwp_fraud_and_error_uc_targeted_case_review_extended__2027.md)
* [autumn_budget_2025__ab2025__dwp_fraud_and_error_uc_targeted_case_review_extended__2028](packets/autumn_budget_2025__ab2025__dwp_fraud_and_error_uc_targeted_case_review_extended__2028.md)
* [autumn_budget_2025__ab2025__dwp_fraud_and_error_uc_targeted_case_review_extended__2029](packets/autumn_budget_2025__ab2025__dwp_fraud_and_error_uc_targeted_case_review_extended__2029.md)
* [autumn_budget_2025__ab2025__dwp_fraud_and_error_uc_targeted_case_review_extended__2030](packets/autumn_budget_2025__ab2025__dwp_fraud_and_error_uc_targeted_case_review_extended__2030.md)
* [autumn_budget_2025__ab2025__electric_car_grant_and_charging_infrastructure__2025](packets/autumn_budget_2025__ab2025__electric_car_grant_and_charging_infrastructure__2025.md)
* [autumn_budget_2025__ab2025__electric_car_grant_and_charging_infrastructure__2026](packets/autumn_budget_2025__ab2025__electric_car_grant_and_charging_infrastructure__2026.md)
* [autumn_budget_2025__ab2025__electric_car_grant_and_charging_infrastructure__2027](packets/autumn_budget_2025__ab2025__electric_car_grant_and_charging_infrastructure__2027.md)
* [autumn_budget_2025__ab2025__electric_car_grant_and_charging_infrastructure__2028](packets/autumn_budget_2025__ab2025__electric_car_grant_and_charging_infrastructure__2028.md)
* [autumn_budget_2025__ab2025__electric_car_grant_and_charging_infrastructure__2029](packets/autumn_budget_2025__ab2025__electric_car_grant_and_charging_infrastructure__2029.md)
* [autumn_budget_2025__ab2025__electric_car_grant_and_charging_infrastructure__2030](packets/autumn_budget_2025__ab2025__electric_car_grant_and_charging_infrastructure__2030.md)
* [autumn_budget_2025__ab2025__emi_eligibility_extended_to_scale_ups__2025](packets/autumn_budget_2025__ab2025__emi_eligibility_extended_to_scale_ups__2025.md)
* [autumn_budget_2025__ab2025__emi_eligibility_extended_to_scale_ups__2026](packets/autumn_budget_2025__ab2025__emi_eligibility_extended_to_scale_ups__2026.md)
* [autumn_budget_2025__ab2025__emi_eligibility_extended_to_scale_ups__2027](packets/autumn_budget_2025__ab2025__emi_eligibility_extended_to_scale_ups__2027.md)
* [autumn_budget_2025__ab2025__emi_eligibility_extended_to_scale_ups__2028](packets/autumn_budget_2025__ab2025__emi_eligibility_extended_to_scale_ups__2028.md)
* [autumn_budget_2025__ab2025__emi_eligibility_extended_to_scale_ups__2029](packets/autumn_budget_2025__ab2025__emi_eligibility_extended_to_scale_ups__2029.md)
* [autumn_budget_2025__ab2025__emi_eligibility_extended_to_scale_ups__2030](packets/autumn_budget_2025__ab2025__emi_eligibility_extended_to_scale_ups__2030.md)
* [autumn_budget_2025__ab2025__employee_car_ownership_schemes_bik_delayed__2025](packets/autumn_budget_2025__ab2025__employee_car_ownership_schemes_bik_delayed__2025.md)
* [autumn_budget_2025__ab2025__employee_car_ownership_schemes_bik_delayed__2026](packets/autumn_budget_2025__ab2025__employee_car_ownership_schemes_bik_delayed__2026.md)
* [autumn_budget_2025__ab2025__employee_car_ownership_schemes_bik_delayed__2027](packets/autumn_budget_2025__ab2025__employee_car_ownership_schemes_bik_delayed__2027.md)
* [autumn_budget_2025__ab2025__employee_car_ownership_schemes_bik_delayed__2028](packets/autumn_budget_2025__ab2025__employee_car_ownership_schemes_bik_delayed__2028.md)
* [autumn_budget_2025__ab2025__employee_car_ownership_schemes_bik_delayed__2029](packets/autumn_budget_2025__ab2025__employee_car_ownership_schemes_bik_delayed__2029.md)
* [autumn_budget_2025__ab2025__employee_car_ownership_schemes_bik_delayed__2030](packets/autumn_budget_2025__ab2025__employee_car_ownership_schemes_bik_delayed__2030.md)
* [autumn_budget_2025__ab2025__employer_nics_secondary_threshold_freeze_to_2031__2025](packets/autumn_budget_2025__ab2025__employer_nics_secondary_threshold_freeze_to_2031__2025.md)
* [autumn_budget_2025__ab2025__employer_nics_secondary_threshold_freeze_to_2031__2026](packets/autumn_budget_2025__ab2025__employer_nics_secondary_threshold_freeze_to_2031__2026.md)
* [autumn_budget_2025__ab2025__employer_nics_secondary_threshold_freeze_to_2031__2027](packets/autumn_budget_2025__ab2025__employer_nics_secondary_threshold_freeze_to_2031__2027.md)
* [autumn_budget_2025__ab2025__employer_nics_secondary_threshold_freeze_to_2031__2028](packets/autumn_budget_2025__ab2025__employer_nics_secondary_threshold_freeze_to_2031__2028.md)
* [autumn_budget_2025__ab2025__employer_nics_secondary_threshold_freeze_to_2031__2029](packets/autumn_budget_2025__ab2025__employer_nics_secondary_threshold_freeze_to_2031__2029.md)
* [autumn_budget_2025__ab2025__employer_nics_secondary_threshold_freeze_to_2031__2030](packets/autumn_budget_2025__ab2025__employer_nics_secondary_threshold_freeze_to_2031__2030.md)
* [autumn_budget_2025__ab2025__environmental_regeneration_grant_scheme__2025](packets/autumn_budget_2025__ab2025__environmental_regeneration_grant_scheme__2025.md)
* [autumn_budget_2025__ab2025__environmental_regeneration_grant_scheme__2026](packets/autumn_budget_2025__ab2025__environmental_regeneration_grant_scheme__2026.md)
* [autumn_budget_2025__ab2025__environmental_regeneration_grant_scheme__2027](packets/autumn_budget_2025__ab2025__environmental_regeneration_grant_scheme__2027.md)
* [autumn_budget_2025__ab2025__environmental_regeneration_grant_scheme__2028](packets/autumn_budget_2025__ab2025__environmental_regeneration_grant_scheme__2028.md)
* [autumn_budget_2025__ab2025__environmental_regeneration_grant_scheme__2029](packets/autumn_budget_2025__ab2025__environmental_regeneration_grant_scheme__2029.md)
* [autumn_budget_2025__ab2025__environmental_regeneration_grant_scheme__2030](packets/autumn_budget_2025__ab2025__environmental_regeneration_grant_scheme__2030.md)
* [autumn_budget_2025__ab2025__ets_expansion_to_international_maritime__2025](packets/autumn_budget_2025__ab2025__ets_expansion_to_international_maritime__2025.md)
* [autumn_budget_2025__ab2025__ets_expansion_to_international_maritime__2026](packets/autumn_budget_2025__ab2025__ets_expansion_to_international_maritime__2026.md)
* [autumn_budget_2025__ab2025__ets_expansion_to_international_maritime__2027](packets/autumn_budget_2025__ab2025__ets_expansion_to_international_maritime__2027.md)
* [autumn_budget_2025__ab2025__ets_expansion_to_international_maritime__2028](packets/autumn_budget_2025__ab2025__ets_expansion_to_international_maritime__2028.md)
* [autumn_budget_2025__ab2025__ets_expansion_to_international_maritime__2029](packets/autumn_budget_2025__ab2025__ets_expansion_to_international_maritime__2029.md)
* [autumn_budget_2025__ab2025__ets_expansion_to_international_maritime__2030](packets/autumn_budget_2025__ab2025__ets_expansion_to_international_maritime__2030.md)
* [autumn_budget_2025__ab2025__eved_mileage_supplement_electric_and_phev__2025](packets/autumn_budget_2025__ab2025__eved_mileage_supplement_electric_and_phev__2025.md)
* [autumn_budget_2025__ab2025__eved_mileage_supplement_electric_and_phev__2026](packets/autumn_budget_2025__ab2025__eved_mileage_supplement_electric_and_phev__2026.md)
* [autumn_budget_2025__ab2025__eved_mileage_supplement_electric_and_phev__2027](packets/autumn_budget_2025__ab2025__eved_mileage_supplement_electric_and_phev__2027.md)
* [autumn_budget_2025__ab2025__eved_mileage_supplement_electric_and_phev__2028](packets/autumn_budget_2025__ab2025__eved_mileage_supplement_electric_and_phev__2028.md)
* [autumn_budget_2025__ab2025__eved_mileage_supplement_electric_and_phev__2029](packets/autumn_budget_2025__ab2025__eved_mileage_supplement_electric_and_phev__2029.md)
* [autumn_budget_2025__ab2025__eved_mileage_supplement_electric_and_phev__2030](packets/autumn_budget_2025__ab2025__eved_mileage_supplement_electric_and_phev__2030.md)
* [autumn_budget_2025__ab2025__expensive_car_supplement_threshold_for_zevs_50000__2025](packets/autumn_budget_2025__ab2025__expensive_car_supplement_threshold_for_zevs_50000__2025.md)
* [autumn_budget_2025__ab2025__expensive_car_supplement_threshold_for_zevs_50000__2026](packets/autumn_budget_2025__ab2025__expensive_car_supplement_threshold_for_zevs_50000__2026.md)
* [autumn_budget_2025__ab2025__expensive_car_supplement_threshold_for_zevs_50000__2027](packets/autumn_budget_2025__ab2025__expensive_car_supplement_threshold_for_zevs_50000__2027.md)
* [autumn_budget_2025__ab2025__expensive_car_supplement_threshold_for_zevs_50000__2028](packets/autumn_budget_2025__ab2025__expensive_car_supplement_threshold_for_zevs_50000__2028.md)
* [autumn_budget_2025__ab2025__expensive_car_supplement_threshold_for_zevs_50000__2029](packets/autumn_budget_2025__ab2025__expensive_car_supplement_threshold_for_zevs_50000__2029.md)
* [autumn_budget_2025__ab2025__expensive_car_supplement_threshold_for_zevs_50000__2030](packets/autumn_budget_2025__ab2025__expensive_car_supplement_threshold_for_zevs_50000__2030.md)
* [autumn_budget_2025__ab2025__fisheries_and_coastal_growth_fund__2025](packets/autumn_budget_2025__ab2025__fisheries_and_coastal_growth_fund__2025.md)
* [autumn_budget_2025__ab2025__fisheries_and_coastal_growth_fund__2026](packets/autumn_budget_2025__ab2025__fisheries_and_coastal_growth_fund__2026.md)
* [autumn_budget_2025__ab2025__fisheries_and_coastal_growth_fund__2027](packets/autumn_budget_2025__ab2025__fisheries_and_coastal_growth_fund__2027.md)
* [autumn_budget_2025__ab2025__fisheries_and_coastal_growth_fund__2028](packets/autumn_budget_2025__ab2025__fisheries_and_coastal_growth_fund__2028.md)
* [autumn_budget_2025__ab2025__fisheries_and_coastal_growth_fund__2029](packets/autumn_budget_2025__ab2025__fisheries_and_coastal_growth_fund__2029.md)
* [autumn_budget_2025__ab2025__fisheries_and_coastal_growth_fund__2030](packets/autumn_budget_2025__ab2025__fisheries_and_coastal_growth_fund__2030.md)
* [autumn_budget_2025__ab2025__fuel_duty_freeze_extension_2026_27__2025](packets/autumn_budget_2025__ab2025__fuel_duty_freeze_extension_2026_27__2025.md)
* [autumn_budget_2025__ab2025__fuel_duty_freeze_extension_2026_27__2026](packets/autumn_budget_2025__ab2025__fuel_duty_freeze_extension_2026_27__2026.md)
* [autumn_budget_2025__ab2025__fuel_duty_freeze_extension_2026_27__2027](packets/autumn_budget_2025__ab2025__fuel_duty_freeze_extension_2026_27__2027.md)
* [autumn_budget_2025__ab2025__fuel_duty_freeze_extension_2026_27__2028](packets/autumn_budget_2025__ab2025__fuel_duty_freeze_extension_2026_27__2028.md)
* [autumn_budget_2025__ab2025__fuel_duty_freeze_extension_2026_27__2029](packets/autumn_budget_2025__ab2025__fuel_duty_freeze_extension_2026_27__2029.md)
* [autumn_budget_2025__ab2025__fuel_duty_freeze_extension_2026_27__2030](packets/autumn_budget_2025__ab2025__fuel_duty_freeze_extension_2026_27__2030.md)
* [autumn_budget_2025__ab2025__fya_zero_emission_cars_and_charge_points_extended__2025](packets/autumn_budget_2025__ab2025__fya_zero_emission_cars_and_charge_points_extended__2025.md)
* [autumn_budget_2025__ab2025__fya_zero_emission_cars_and_charge_points_extended__2026](packets/autumn_budget_2025__ab2025__fya_zero_emission_cars_and_charge_points_extended__2026.md)
* [autumn_budget_2025__ab2025__fya_zero_emission_cars_and_charge_points_extended__2027](packets/autumn_budget_2025__ab2025__fya_zero_emission_cars_and_charge_points_extended__2027.md)
* [autumn_budget_2025__ab2025__fya_zero_emission_cars_and_charge_points_extended__2028](packets/autumn_budget_2025__ab2025__fya_zero_emission_cars_and_charge_points_extended__2028.md)
* [autumn_budget_2025__ab2025__fya_zero_emission_cars_and_charge_points_extended__2029](packets/autumn_budget_2025__ab2025__fya_zero_emission_cars_and_charge_points_extended__2029.md)
* [autumn_budget_2025__ab2025__fya_zero_emission_cars_and_charge_points_extended__2030](packets/autumn_budget_2025__ab2025__fya_zero_emission_cars_and_charge_points_extended__2030.md)
* [autumn_budget_2025__ab2025__gambling_commission_illegal_market_funding__2025](packets/autumn_budget_2025__ab2025__gambling_commission_illegal_market_funding__2025.md)
* [autumn_budget_2025__ab2025__gambling_commission_illegal_market_funding__2026](packets/autumn_budget_2025__ab2025__gambling_commission_illegal_market_funding__2026.md)
* [autumn_budget_2025__ab2025__gambling_commission_illegal_market_funding__2027](packets/autumn_budget_2025__ab2025__gambling_commission_illegal_market_funding__2027.md)
* [autumn_budget_2025__ab2025__gambling_commission_illegal_market_funding__2028](packets/autumn_budget_2025__ab2025__gambling_commission_illegal_market_funding__2028.md)
* [autumn_budget_2025__ab2025__gambling_commission_illegal_market_funding__2029](packets/autumn_budget_2025__ab2025__gambling_commission_illegal_market_funding__2029.md)
* [autumn_budget_2025__ab2025__gambling_commission_illegal_market_funding__2030](packets/autumn_budget_2025__ab2025__gambling_commission_illegal_market_funding__2030.md)
* [autumn_budget_2025__ab2025__gambling_duties_rgd_40_remote_betting_25__2025](packets/autumn_budget_2025__ab2025__gambling_duties_rgd_40_remote_betting_25__2025.md)
* [autumn_budget_2025__ab2025__gambling_duties_rgd_40_remote_betting_25__2026](packets/autumn_budget_2025__ab2025__gambling_duties_rgd_40_remote_betting_25__2026.md)
* [autumn_budget_2025__ab2025__gambling_duties_rgd_40_remote_betting_25__2027](packets/autumn_budget_2025__ab2025__gambling_duties_rgd_40_remote_betting_25__2027.md)
* [autumn_budget_2025__ab2025__gambling_duties_rgd_40_remote_betting_25__2028](packets/autumn_budget_2025__ab2025__gambling_duties_rgd_40_remote_betting_25__2028.md)
* [autumn_budget_2025__ab2025__gambling_duties_rgd_40_remote_betting_25__2029](packets/autumn_budget_2025__ab2025__gambling_duties_rgd_40_remote_betting_25__2029.md)
* [autumn_budget_2025__ab2025__gambling_duties_rgd_40_remote_betting_25__2030](packets/autumn_budget_2025__ab2025__gambling_duties_rgd_40_remote_betting_25__2030.md)
* [autumn_budget_2025__ab2025__hb_and_pension_credit_administration_brought_together__2025](packets/autumn_budget_2025__ab2025__hb_and_pension_credit_administration_brought_together__2025.md)
* [autumn_budget_2025__ab2025__hb_and_pension_credit_administration_brought_together__2026](packets/autumn_budget_2025__ab2025__hb_and_pension_credit_administration_brought_together__2026.md)
* [autumn_budget_2025__ab2025__hb_and_pension_credit_administration_brought_together__2027](packets/autumn_budget_2025__ab2025__hb_and_pension_credit_administration_brought_together__2027.md)
* [autumn_budget_2025__ab2025__hb_and_pension_credit_administration_brought_together__2028](packets/autumn_budget_2025__ab2025__hb_and_pension_credit_administration_brought_together__2028.md)
* [autumn_budget_2025__ab2025__hb_and_pension_credit_administration_brought_together__2029](packets/autumn_budget_2025__ab2025__hb_and_pension_credit_administration_brought_together__2029.md)
* [autumn_budget_2025__ab2025__hb_and_pension_credit_administration_brought_together__2030](packets/autumn_budget_2025__ab2025__hb_and_pension_credit_administration_brought_together__2030.md)
* [autumn_budget_2025__ab2025__health_and_disability_benefits_operations__2025](packets/autumn_budget_2025__ab2025__health_and_disability_benefits_operations__2025.md)
* [autumn_budget_2025__ab2025__health_and_disability_benefits_operations__2026](packets/autumn_budget_2025__ab2025__health_and_disability_benefits_operations__2026.md)
* [autumn_budget_2025__ab2025__health_and_disability_benefits_operations__2027](packets/autumn_budget_2025__ab2025__health_and_disability_benefits_operations__2027.md)
* [autumn_budget_2025__ab2025__health_and_disability_benefits_operations__2028](packets/autumn_budget_2025__ab2025__health_and_disability_benefits_operations__2028.md)
* [autumn_budget_2025__ab2025__health_and_disability_benefits_operations__2029](packets/autumn_budget_2025__ab2025__health_and_disability_benefits_operations__2029.md)
* [autumn_budget_2025__ab2025__health_and_disability_benefits_operations__2030](packets/autumn_budget_2025__ab2025__health_and_disability_benefits_operations__2030.md)
* [autumn_budget_2025__ab2025__high_value_council_tax_surcharge__2025](packets/autumn_budget_2025__ab2025__high_value_council_tax_surcharge__2025.md)
* [autumn_budget_2025__ab2025__high_value_council_tax_surcharge__2026](packets/autumn_budget_2025__ab2025__high_value_council_tax_surcharge__2026.md)
* [autumn_budget_2025__ab2025__high_value_council_tax_surcharge__2027](packets/autumn_budget_2025__ab2025__high_value_council_tax_surcharge__2027.md)
* [autumn_budget_2025__ab2025__high_value_council_tax_surcharge__2028](packets/autumn_budget_2025__ab2025__high_value_council_tax_surcharge__2028.md)
* [autumn_budget_2025__ab2025__high_value_council_tax_surcharge__2029](packets/autumn_budget_2025__ab2025__high_value_council_tax_surcharge__2029.md)
* [autumn_budget_2025__ab2025__high_value_council_tax_surcharge__2030](packets/autumn_budget_2025__ab2025__high_value_council_tax_surcharge__2030.md)
* [autumn_budget_2025__ab2025__hmrc_further_measures_to_close_the_tax_gap__2025](packets/autumn_budget_2025__ab2025__hmrc_further_measures_to_close_the_tax_gap__2025.md)
* [autumn_budget_2025__ab2025__hmrc_further_measures_to_close_the_tax_gap__2026](packets/autumn_budget_2025__ab2025__hmrc_further_measures_to_close_the_tax_gap__2026.md)
* [autumn_budget_2025__ab2025__hmrc_further_measures_to_close_the_tax_gap__2027](packets/autumn_budget_2025__ab2025__hmrc_further_measures_to_close_the_tax_gap__2027.md)
* [autumn_budget_2025__ab2025__hmrc_further_measures_to_close_the_tax_gap__2028](packets/autumn_budget_2025__ab2025__hmrc_further_measures_to_close_the_tax_gap__2028.md)
* [autumn_budget_2025__ab2025__hmrc_further_measures_to_close_the_tax_gap__2029](packets/autumn_budget_2025__ab2025__hmrc_further_measures_to_close_the_tax_gap__2029.md)
* [autumn_budget_2025__ab2025__hmrc_further_measures_to_close_the_tax_gap__2030](packets/autumn_budget_2025__ab2025__hmrc_further_measures_to_close_the_tax_gap__2030.md)
* [autumn_budget_2025__ab2025__home_office_people_smuggling_funding__2025](packets/autumn_budget_2025__ab2025__home_office_people_smuggling_funding__2025.md)
* [autumn_budget_2025__ab2025__home_office_people_smuggling_funding__2026](packets/autumn_budget_2025__ab2025__home_office_people_smuggling_funding__2026.md)
* [autumn_budget_2025__ab2025__home_office_people_smuggling_funding__2027](packets/autumn_budget_2025__ab2025__home_office_people_smuggling_funding__2027.md)
* [autumn_budget_2025__ab2025__home_office_people_smuggling_funding__2028](packets/autumn_budget_2025__ab2025__home_office_people_smuggling_funding__2028.md)
* [autumn_budget_2025__ab2025__home_office_people_smuggling_funding__2029](packets/autumn_budget_2025__ab2025__home_office_people_smuggling_funding__2029.md)
* [autumn_budget_2025__ab2025__home_office_people_smuggling_funding__2030](packets/autumn_budget_2025__ab2025__home_office_people_smuggling_funding__2030.md)
* [autumn_budget_2025__ab2025__housing_benefit_cliff_edge_supported_and_temporary_accommodation__2025](packets/autumn_budget_2025__ab2025__housing_benefit_cliff_edge_supported_and_temporary_accommodation__2025.md)
* [autumn_budget_2025__ab2025__housing_benefit_cliff_edge_supported_and_temporary_accommodation__2026](packets/autumn_budget_2025__ab2025__housing_benefit_cliff_edge_supported_and_temporary_accommodation__2026.md)
* [autumn_budget_2025__ab2025__housing_benefit_cliff_edge_supported_and_temporary_accommodation__2027](packets/autumn_budget_2025__ab2025__housing_benefit_cliff_edge_supported_and_temporary_accommodation__2027.md)
* [autumn_budget_2025__ab2025__housing_benefit_cliff_edge_supported_and_temporary_accommodation__2028](packets/autumn_budget_2025__ab2025__housing_benefit_cliff_edge_supported_and_temporary_accommodation__2028.md)
* [autumn_budget_2025__ab2025__housing_benefit_cliff_edge_supported_and_temporary_accommodation__2029](packets/autumn_budget_2025__ab2025__housing_benefit_cliff_edge_supported_and_temporary_accommodation__2029.md)
* [autumn_budget_2025__ab2025__housing_benefit_cliff_edge_supported_and_temporary_accommodation__2030](packets/autumn_budget_2025__ab2025__housing_benefit_cliff_edge_supported_and_temporary_accommodation__2030.md)
* [autumn_budget_2025__ab2025__iht_nil_rate_bands_and_apr_bpr_allowance_frozen_to_2031__2025](packets/autumn_budget_2025__ab2025__iht_nil_rate_bands_and_apr_bpr_allowance_frozen_to_2031__2025.md)
* [autumn_budget_2025__ab2025__iht_nil_rate_bands_and_apr_bpr_allowance_frozen_to_2031__2026](packets/autumn_budget_2025__ab2025__iht_nil_rate_bands_and_apr_bpr_allowance_frozen_to_2031__2026.md)
* [autumn_budget_2025__ab2025__iht_nil_rate_bands_and_apr_bpr_allowance_frozen_to_2031__2027](packets/autumn_budget_2025__ab2025__iht_nil_rate_bands_and_apr_bpr_allowance_frozen_to_2031__2027.md)
* [autumn_budget_2025__ab2025__iht_nil_rate_bands_and_apr_bpr_allowance_frozen_to_2031__2028](packets/autumn_budget_2025__ab2025__iht_nil_rate_bands_and_apr_bpr_allowance_frozen_to_2031__2028.md)
* [autumn_budget_2025__ab2025__iht_nil_rate_bands_and_apr_bpr_allowance_frozen_to_2031__2029](packets/autumn_budget_2025__ab2025__iht_nil_rate_bands_and_apr_bpr_allowance_frozen_to_2031__2029.md)
* [autumn_budget_2025__ab2025__iht_nil_rate_bands_and_apr_bpr_allowance_frozen_to_2031__2030](packets/autumn_budget_2025__ab2025__iht_nil_rate_bands_and_apr_bpr_allowance_frozen_to_2031__2030.md)
* [autumn_budget_2025__ab2025__illegal_high_street_operations_taskforce__2025](packets/autumn_budget_2025__ab2025__illegal_high_street_operations_taskforce__2025.md)
* [autumn_budget_2025__ab2025__illegal_high_street_operations_taskforce__2026](packets/autumn_budget_2025__ab2025__illegal_high_street_operations_taskforce__2026.md)
* [autumn_budget_2025__ab2025__illegal_high_street_operations_taskforce__2027](packets/autumn_budget_2025__ab2025__illegal_high_street_operations_taskforce__2027.md)
* [autumn_budget_2025__ab2025__illegal_high_street_operations_taskforce__2028](packets/autumn_budget_2025__ab2025__illegal_high_street_operations_taskforce__2028.md)
* [autumn_budget_2025__ab2025__illegal_high_street_operations_taskforce__2029](packets/autumn_budget_2025__ab2025__illegal_high_street_operations_taskforce__2029.md)
* [autumn_budget_2025__ab2025__illegal_high_street_operations_taskforce__2030](packets/autumn_budget_2025__ab2025__illegal_high_street_operations_taskforce__2030.md)
* [autumn_budget_2025__ab2025__innovation_in_wales_semiconductor_cluster__2025](packets/autumn_budget_2025__ab2025__innovation_in_wales_semiconductor_cluster__2025.md)
* [autumn_budget_2025__ab2025__innovation_in_wales_semiconductor_cluster__2026](packets/autumn_budget_2025__ab2025__innovation_in_wales_semiconductor_cluster__2026.md)
* [autumn_budget_2025__ab2025__innovation_in_wales_semiconductor_cluster__2027](packets/autumn_budget_2025__ab2025__innovation_in_wales_semiconductor_cluster__2027.md)
* [autumn_budget_2025__ab2025__innovation_in_wales_semiconductor_cluster__2028](packets/autumn_budget_2025__ab2025__innovation_in_wales_semiconductor_cluster__2028.md)
* [autumn_budget_2025__ab2025__innovation_in_wales_semiconductor_cluster__2029](packets/autumn_budget_2025__ab2025__innovation_in_wales_semiconductor_cluster__2029.md)
* [autumn_budget_2025__ab2025__innovation_in_wales_semiconductor_cluster__2030](packets/autumn_budget_2025__ab2025__innovation_in_wales_semiconductor_cluster__2030.md)
* [autumn_budget_2025__ab2025__jobs_and_skills_youth_guarantee_and_levy__2025](packets/autumn_budget_2025__ab2025__jobs_and_skills_youth_guarantee_and_levy__2025.md)
* [autumn_budget_2025__ab2025__jobs_and_skills_youth_guarantee_and_levy__2026](packets/autumn_budget_2025__ab2025__jobs_and_skills_youth_guarantee_and_levy__2026.md)
* [autumn_budget_2025__ab2025__jobs_and_skills_youth_guarantee_and_levy__2027](packets/autumn_budget_2025__ab2025__jobs_and_skills_youth_guarantee_and_levy__2027.md)
* [autumn_budget_2025__ab2025__jobs_and_skills_youth_guarantee_and_levy__2028](packets/autumn_budget_2025__ab2025__jobs_and_skills_youth_guarantee_and_levy__2028.md)
* [autumn_budget_2025__ab2025__jobs_and_skills_youth_guarantee_and_levy__2029](packets/autumn_budget_2025__ab2025__jobs_and_skills_youth_guarantee_and_levy__2029.md)
* [autumn_budget_2025__ab2025__jobs_and_skills_youth_guarantee_and_levy__2030](packets/autumn_budget_2025__ab2025__jobs_and_skills_youth_guarantee_and_levy__2030.md)
* [autumn_budget_2025__ab2025__kernow_industrial_growth_fund__2025](packets/autumn_budget_2025__ab2025__kernow_industrial_growth_fund__2025.md)
* [autumn_budget_2025__ab2025__kernow_industrial_growth_fund__2026](packets/autumn_budget_2025__ab2025__kernow_industrial_growth_fund__2026.md)
* [autumn_budget_2025__ab2025__kernow_industrial_growth_fund__2027](packets/autumn_budget_2025__ab2025__kernow_industrial_growth_fund__2027.md)
* [autumn_budget_2025__ab2025__kernow_industrial_growth_fund__2028](packets/autumn_budget_2025__ab2025__kernow_industrial_growth_fund__2028.md)
* [autumn_budget_2025__ab2025__kernow_industrial_growth_fund__2029](packets/autumn_budget_2025__ab2025__kernow_industrial_growth_fund__2029.md)
* [autumn_budget_2025__ab2025__kernow_industrial_growth_fund__2030](packets/autumn_budget_2025__ab2025__kernow_industrial_growth_fund__2030.md)
* [autumn_budget_2025__ab2025__landfill_tax_lower_rate_increase__2025](packets/autumn_budget_2025__ab2025__landfill_tax_lower_rate_increase__2025.md)
* [autumn_budget_2025__ab2025__landfill_tax_lower_rate_increase__2026](packets/autumn_budget_2025__ab2025__landfill_tax_lower_rate_increase__2026.md)
* [autumn_budget_2025__ab2025__landfill_tax_lower_rate_increase__2027](packets/autumn_budget_2025__ab2025__landfill_tax_lower_rate_increase__2027.md)
* [autumn_budget_2025__ab2025__landfill_tax_lower_rate_increase__2028](packets/autumn_budget_2025__ab2025__landfill_tax_lower_rate_increase__2028.md)
* [autumn_budget_2025__ab2025__landfill_tax_lower_rate_increase__2029](packets/autumn_budget_2025__ab2025__landfill_tax_lower_rate_increase__2029.md)
* [autumn_budget_2025__ab2025__landfill_tax_lower_rate_increase__2030](packets/autumn_budget_2025__ab2025__landfill_tax_lower_rate_increase__2030.md)
* [autumn_budget_2025__ab2025__loan_charge_review_response__2025](packets/autumn_budget_2025__ab2025__loan_charge_review_response__2025.md)
* [autumn_budget_2025__ab2025__loan_charge_review_response__2026](packets/autumn_budget_2025__ab2025__loan_charge_review_response__2026.md)
* [autumn_budget_2025__ab2025__loan_charge_review_response__2027](packets/autumn_budget_2025__ab2025__loan_charge_review_response__2027.md)
* [autumn_budget_2025__ab2025__loan_charge_review_response__2028](packets/autumn_budget_2025__ab2025__loan_charge_review_response__2028.md)
* [autumn_budget_2025__ab2025__loan_charge_review_response__2029](packets/autumn_budget_2025__ab2025__loan_charge_review_response__2029.md)
* [autumn_budget_2025__ab2025__loan_charge_review_response__2030](packets/autumn_budget_2025__ab2025__loan_charge_review_response__2030.md)
* [autumn_budget_2025__ab2025__low_value_imports_customs_reform__2025](packets/autumn_budget_2025__ab2025__low_value_imports_customs_reform__2025.md)
* [autumn_budget_2025__ab2025__low_value_imports_customs_reform__2026](packets/autumn_budget_2025__ab2025__low_value_imports_customs_reform__2026.md)
* [autumn_budget_2025__ab2025__low_value_imports_customs_reform__2027](packets/autumn_budget_2025__ab2025__low_value_imports_customs_reform__2027.md)
* [autumn_budget_2025__ab2025__low_value_imports_customs_reform__2028](packets/autumn_budget_2025__ab2025__low_value_imports_customs_reform__2028.md)
* [autumn_budget_2025__ab2025__low_value_imports_customs_reform__2029](packets/autumn_budget_2025__ab2025__low_value_imports_customs_reform__2029.md)
* [autumn_budget_2025__ab2025__low_value_imports_customs_reform__2030](packets/autumn_budget_2025__ab2025__low_value_imports_customs_reform__2030.md)
* [autumn_budget_2025__ab2025__motability_vat_on_advance_payments_and_ipt__2025](packets/autumn_budget_2025__ab2025__motability_vat_on_advance_payments_and_ipt__2025.md)
* [autumn_budget_2025__ab2025__motability_vat_on_advance_payments_and_ipt__2026](packets/autumn_budget_2025__ab2025__motability_vat_on_advance_payments_and_ipt__2026.md)
* [autumn_budget_2025__ab2025__motability_vat_on_advance_payments_and_ipt__2027](packets/autumn_budget_2025__ab2025__motability_vat_on_advance_payments_and_ipt__2027.md)
* [autumn_budget_2025__ab2025__motability_vat_on_advance_payments_and_ipt__2028](packets/autumn_budget_2025__ab2025__motability_vat_on_advance_payments_and_ipt__2028.md)
* [autumn_budget_2025__ab2025__motability_vat_on_advance_payments_and_ipt__2029](packets/autumn_budget_2025__ab2025__motability_vat_on_advance_payments_and_ipt__2029.md)
* [autumn_budget_2025__ab2025__motability_vat_on_advance_payments_and_ipt__2030](packets/autumn_budget_2025__ab2025__motability_vat_on_advance_payments_and_ipt__2030.md)
* [autumn_budget_2025__ab2025__national_level_regulation_food_businesses__2025](packets/autumn_budget_2025__ab2025__national_level_regulation_food_businesses__2025.md)
* [autumn_budget_2025__ab2025__national_level_regulation_food_businesses__2026](packets/autumn_budget_2025__ab2025__national_level_regulation_food_businesses__2026.md)
* [autumn_budget_2025__ab2025__national_level_regulation_food_businesses__2027](packets/autumn_budget_2025__ab2025__national_level_regulation_food_businesses__2027.md)
* [autumn_budget_2025__ab2025__national_level_regulation_food_businesses__2028](packets/autumn_budget_2025__ab2025__national_level_regulation_food_businesses__2028.md)
* [autumn_budget_2025__ab2025__national_level_regulation_food_businesses__2029](packets/autumn_budget_2025__ab2025__national_level_regulation_food_businesses__2029.md)
* [autumn_budget_2025__ab2025__national_level_regulation_food_businesses__2030](packets/autumn_budget_2025__ab2025__national_level_regulation_food_businesses__2030.md)
* [autumn_budget_2025__ab2025__national_year_of_reading_book_funding__2025](packets/autumn_budget_2025__ab2025__national_year_of_reading_book_funding__2025.md)
* [autumn_budget_2025__ab2025__national_year_of_reading_book_funding__2026](packets/autumn_budget_2025__ab2025__national_year_of_reading_book_funding__2026.md)
* [autumn_budget_2025__ab2025__national_year_of_reading_book_funding__2027](packets/autumn_budget_2025__ab2025__national_year_of_reading_book_funding__2027.md)
* [autumn_budget_2025__ab2025__national_year_of_reading_book_funding__2028](packets/autumn_budget_2025__ab2025__national_year_of_reading_book_funding__2028.md)
* [autumn_budget_2025__ab2025__national_year_of_reading_book_funding__2029](packets/autumn_budget_2025__ab2025__national_year_of_reading_book_funding__2029.md)
* [autumn_budget_2025__ab2025__national_year_of_reading_book_funding__2030](packets/autumn_budget_2025__ab2025__national_year_of_reading_book_funding__2030.md)
* [autumn_budget_2025__ab2025__nhs_england_abolition_funding_brought_forward__2025](packets/autumn_budget_2025__ab2025__nhs_england_abolition_funding_brought_forward__2025.md)
* [autumn_budget_2025__ab2025__nhs_england_abolition_funding_brought_forward__2026](packets/autumn_budget_2025__ab2025__nhs_england_abolition_funding_brought_forward__2026.md)
* [autumn_budget_2025__ab2025__nhs_england_abolition_funding_brought_forward__2027](packets/autumn_budget_2025__ab2025__nhs_england_abolition_funding_brought_forward__2027.md)
* [autumn_budget_2025__ab2025__nhs_england_abolition_funding_brought_forward__2028](packets/autumn_budget_2025__ab2025__nhs_england_abolition_funding_brought_forward__2028.md)
* [autumn_budget_2025__ab2025__nhs_england_abolition_funding_brought_forward__2029](packets/autumn_budget_2025__ab2025__nhs_england_abolition_funding_brought_forward__2029.md)
* [autumn_budget_2025__ab2025__nhs_england_abolition_funding_brought_forward__2030](packets/autumn_budget_2025__ab2025__nhs_england_abolition_funding_brought_forward__2030.md)
* [autumn_budget_2025__ab2025__nhs_prescription_charges_frozen_2026__2025](packets/autumn_budget_2025__ab2025__nhs_prescription_charges_frozen_2026__2025.md)
* [autumn_budget_2025__ab2025__nhs_prescription_charges_frozen_2026__2026](packets/autumn_budget_2025__ab2025__nhs_prescription_charges_frozen_2026__2026.md)
* [autumn_budget_2025__ab2025__nhs_prescription_charges_frozen_2026__2027](packets/autumn_budget_2025__ab2025__nhs_prescription_charges_frozen_2026__2027.md)
* [autumn_budget_2025__ab2025__nhs_prescription_charges_frozen_2026__2028](packets/autumn_budget_2025__ab2025__nhs_prescription_charges_frozen_2026__2028.md)
* [autumn_budget_2025__ab2025__nhs_prescription_charges_frozen_2026__2029](packets/autumn_budget_2025__ab2025__nhs_prescription_charges_frozen_2026__2029.md)
* [autumn_budget_2025__ab2025__nhs_prescription_charges_frozen_2026__2030](packets/autumn_budget_2025__ab2025__nhs_prescription_charges_frozen_2026__2030.md)
* [autumn_budget_2025__ab2025__nhs_technology_investment__2025](packets/autumn_budget_2025__ab2025__nhs_technology_investment__2025.md)
* [autumn_budget_2025__ab2025__nhs_technology_investment__2026](packets/autumn_budget_2025__ab2025__nhs_technology_investment__2026.md)
* [autumn_budget_2025__ab2025__nhs_technology_investment__2027](packets/autumn_budget_2025__ab2025__nhs_technology_investment__2027.md)
* [autumn_budget_2025__ab2025__nhs_technology_investment__2028](packets/autumn_budget_2025__ab2025__nhs_technology_investment__2028.md)
* [autumn_budget_2025__ab2025__nhs_technology_investment__2029](packets/autumn_budget_2025__ab2025__nhs_technology_investment__2029.md)
* [autumn_budget_2025__ab2025__nhs_technology_investment__2030](packets/autumn_budget_2025__ab2025__nhs_technology_investment__2030.md)
* [autumn_budget_2025__ab2025__nics_class_2_abroad_removed_and_class_3_residency_requirement__2025](packets/autumn_budget_2025__ab2025__nics_class_2_abroad_removed_and_class_3_residency_requirement__2025.md)
* [autumn_budget_2025__ab2025__nics_class_2_abroad_removed_and_class_3_residency_requirement__2026](packets/autumn_budget_2025__ab2025__nics_class_2_abroad_removed_and_class_3_residency_requirement__2026.md)
* [autumn_budget_2025__ab2025__nics_class_2_abroad_removed_and_class_3_residency_requirement__2027](packets/autumn_budget_2025__ab2025__nics_class_2_abroad_removed_and_class_3_residency_requirement__2027.md)
* [autumn_budget_2025__ab2025__nics_class_2_abroad_removed_and_class_3_residency_requirement__2028](packets/autumn_budget_2025__ab2025__nics_class_2_abroad_removed_and_class_3_residency_requirement__2028.md)
* [autumn_budget_2025__ab2025__nics_class_2_abroad_removed_and_class_3_residency_requirement__2029](packets/autumn_budget_2025__ab2025__nics_class_2_abroad_removed_and_class_3_residency_requirement__2029.md)
* [autumn_budget_2025__ab2025__nics_class_2_abroad_removed_and_class_3_residency_requirement__2030](packets/autumn_budget_2025__ab2025__nics_class_2_abroad_removed_and_class_3_residency_requirement__2030.md)
* [autumn_budget_2025__ab2025__non_reimbursed_homeworking_expenses_relief_removed__2025](packets/autumn_budget_2025__ab2025__non_reimbursed_homeworking_expenses_relief_removed__2025.md)
* [autumn_budget_2025__ab2025__non_reimbursed_homeworking_expenses_relief_removed__2026](packets/autumn_budget_2025__ab2025__non_reimbursed_homeworking_expenses_relief_removed__2026.md)
* [autumn_budget_2025__ab2025__non_reimbursed_homeworking_expenses_relief_removed__2027](packets/autumn_budget_2025__ab2025__non_reimbursed_homeworking_expenses_relief_removed__2027.md)
* [autumn_budget_2025__ab2025__non_reimbursed_homeworking_expenses_relief_removed__2028](packets/autumn_budget_2025__ab2025__non_reimbursed_homeworking_expenses_relief_removed__2028.md)
* [autumn_budget_2025__ab2025__non_reimbursed_homeworking_expenses_relief_removed__2029](packets/autumn_budget_2025__ab2025__non_reimbursed_homeworking_expenses_relief_removed__2029.md)
* [autumn_budget_2025__ab2025__non_reimbursed_homeworking_expenses_relief_removed__2030](packets/autumn_budget_2025__ab2025__non_reimbursed_homeworking_expenses_relief_removed__2030.md)
* [autumn_budget_2025__ab2025__northern_ireland_post_brexit_trade_support__2025](packets/autumn_budget_2025__ab2025__northern_ireland_post_brexit_trade_support__2025.md)
* [autumn_budget_2025__ab2025__northern_ireland_post_brexit_trade_support__2026](packets/autumn_budget_2025__ab2025__northern_ireland_post_brexit_trade_support__2026.md)
* [autumn_budget_2025__ab2025__northern_ireland_post_brexit_trade_support__2027](packets/autumn_budget_2025__ab2025__northern_ireland_post_brexit_trade_support__2027.md)
* [autumn_budget_2025__ab2025__northern_ireland_post_brexit_trade_support__2028](packets/autumn_budget_2025__ab2025__northern_ireland_post_brexit_trade_support__2028.md)
* [autumn_budget_2025__ab2025__northern_ireland_post_brexit_trade_support__2029](packets/autumn_budget_2025__ab2025__northern_ireland_post_brexit_trade_support__2029.md)
* [autumn_budget_2025__ab2025__northern_ireland_post_brexit_trade_support__2030](packets/autumn_budget_2025__ab2025__northern_ireland_post_brexit_trade_support__2030.md)
* [autumn_budget_2025__ab2025__personal_tax_thresholds_freeze_to_2031__2025](packets/autumn_budget_2025__ab2025__personal_tax_thresholds_freeze_to_2031__2025.md)
* [autumn_budget_2025__ab2025__personal_tax_thresholds_freeze_to_2031__2026](packets/autumn_budget_2025__ab2025__personal_tax_thresholds_freeze_to_2031__2026.md)
* [autumn_budget_2025__ab2025__personal_tax_thresholds_freeze_to_2031__2027](packets/autumn_budget_2025__ab2025__personal_tax_thresholds_freeze_to_2031__2027.md)
* [autumn_budget_2025__ab2025__personal_tax_thresholds_freeze_to_2031__2028](packets/autumn_budget_2025__ab2025__personal_tax_thresholds_freeze_to_2031__2028.md)
* [autumn_budget_2025__ab2025__personal_tax_thresholds_freeze_to_2031__2029](packets/autumn_budget_2025__ab2025__personal_tax_thresholds_freeze_to_2031__2029.md)
* [autumn_budget_2025__ab2025__personal_tax_thresholds_freeze_to_2031__2030](packets/autumn_budget_2025__ab2025__personal_tax_thresholds_freeze_to_2031__2030.md)
* [autumn_budget_2025__ab2025__phev_emissions_standard_and_bik_easement__2025](packets/autumn_budget_2025__ab2025__phev_emissions_standard_and_bik_easement__2025.md)
* [autumn_budget_2025__ab2025__phev_emissions_standard_and_bik_easement__2026](packets/autumn_budget_2025__ab2025__phev_emissions_standard_and_bik_easement__2026.md)
* [autumn_budget_2025__ab2025__phev_emissions_standard_and_bik_easement__2027](packets/autumn_budget_2025__ab2025__phev_emissions_standard_and_bik_easement__2027.md)
* [autumn_budget_2025__ab2025__phev_emissions_standard_and_bik_easement__2028](packets/autumn_budget_2025__ab2025__phev_emissions_standard_and_bik_easement__2028.md)
* [autumn_budget_2025__ab2025__phev_emissions_standard_and_bik_easement__2029](packets/autumn_budget_2025__ab2025__phev_emissions_standard_and_bik_easement__2029.md)
* [autumn_budget_2025__ab2025__phev_emissions_standard_and_bik_easement__2030](packets/autumn_budget_2025__ab2025__phev_emissions_standard_and_bik_easement__2030.md)
* [autumn_budget_2025__ab2025__pip_not_proceeding_with_ss2025_eligibility_reforms__2025](packets/autumn_budget_2025__ab2025__pip_not_proceeding_with_ss2025_eligibility_reforms__2025.md)
* [autumn_budget_2025__ab2025__pip_not_proceeding_with_ss2025_eligibility_reforms__2026](packets/autumn_budget_2025__ab2025__pip_not_proceeding_with_ss2025_eligibility_reforms__2026.md)
* [autumn_budget_2025__ab2025__pip_not_proceeding_with_ss2025_eligibility_reforms__2027](packets/autumn_budget_2025__ab2025__pip_not_proceeding_with_ss2025_eligibility_reforms__2027.md)
* [autumn_budget_2025__ab2025__pip_not_proceeding_with_ss2025_eligibility_reforms__2028](packets/autumn_budget_2025__ab2025__pip_not_proceeding_with_ss2025_eligibility_reforms__2028.md)
* [autumn_budget_2025__ab2025__pip_not_proceeding_with_ss2025_eligibility_reforms__2029](packets/autumn_budget_2025__ab2025__pip_not_proceeding_with_ss2025_eligibility_reforms__2029.md)
* [autumn_budget_2025__ab2025__pip_not_proceeding_with_ss2025_eligibility_reforms__2030](packets/autumn_budget_2025__ab2025__pip_not_proceeding_with_ss2025_eligibility_reforms__2030.md)
* [autumn_budget_2025__ab2025__planning_capacity_and_capability__2025](packets/autumn_budget_2025__ab2025__planning_capacity_and_capability__2025.md)
* [autumn_budget_2025__ab2025__planning_capacity_and_capability__2026](packets/autumn_budget_2025__ab2025__planning_capacity_and_capability__2026.md)
* [autumn_budget_2025__ab2025__planning_capacity_and_capability__2027](packets/autumn_budget_2025__ab2025__planning_capacity_and_capability__2027.md)
* [autumn_budget_2025__ab2025__planning_capacity_and_capability__2028](packets/autumn_budget_2025__ab2025__planning_capacity_and_capability__2028.md)
* [autumn_budget_2025__ab2025__planning_capacity_and_capability__2029](packets/autumn_budget_2025__ab2025__planning_capacity_and_capability__2029.md)
* [autumn_budget_2025__ab2025__planning_capacity_and_capability__2030](packets/autumn_budget_2025__ab2025__planning_capacity_and_capability__2030.md)
* [autumn_budget_2025__ab2025__playground_refurbishment_funding__2025](packets/autumn_budget_2025__ab2025__playground_refurbishment_funding__2025.md)
* [autumn_budget_2025__ab2025__playground_refurbishment_funding__2026](packets/autumn_budget_2025__ab2025__playground_refurbishment_funding__2026.md)
* [autumn_budget_2025__ab2025__playground_refurbishment_funding__2027](packets/autumn_budget_2025__ab2025__playground_refurbishment_funding__2027.md)
* [autumn_budget_2025__ab2025__playground_refurbishment_funding__2028](packets/autumn_budget_2025__ab2025__playground_refurbishment_funding__2028.md)
* [autumn_budget_2025__ab2025__playground_refurbishment_funding__2029](packets/autumn_budget_2025__ab2025__playground_refurbishment_funding__2029.md)
* [autumn_budget_2025__ab2025__playground_refurbishment_funding__2030](packets/autumn_budget_2025__ab2025__playground_refurbishment_funding__2030.md)
* [autumn_budget_2025__ab2025__port_talbot_brownfield_remediation__2025](packets/autumn_budget_2025__ab2025__port_talbot_brownfield_remediation__2025.md)
* [autumn_budget_2025__ab2025__port_talbot_brownfield_remediation__2026](packets/autumn_budget_2025__ab2025__port_talbot_brownfield_remediation__2026.md)
* [autumn_budget_2025__ab2025__port_talbot_brownfield_remediation__2027](packets/autumn_budget_2025__ab2025__port_talbot_brownfield_remediation__2027.md)
* [autumn_budget_2025__ab2025__port_talbot_brownfield_remediation__2028](packets/autumn_budget_2025__ab2025__port_talbot_brownfield_remediation__2028.md)
* [autumn_budget_2025__ab2025__port_talbot_brownfield_remediation__2029](packets/autumn_budget_2025__ab2025__port_talbot_brownfield_remediation__2029.md)
* [autumn_budget_2025__ab2025__port_talbot_brownfield_remediation__2030](packets/autumn_budget_2025__ab2025__port_talbot_brownfield_remediation__2030.md)
* [autumn_budget_2025__ab2025__ppf_and_fas_pre_1997_inflation_protection__2025](packets/autumn_budget_2025__ab2025__ppf_and_fas_pre_1997_inflation_protection__2025.md)
* [autumn_budget_2025__ab2025__ppf_and_fas_pre_1997_inflation_protection__2026](packets/autumn_budget_2025__ab2025__ppf_and_fas_pre_1997_inflation_protection__2026.md)
* [autumn_budget_2025__ab2025__ppf_and_fas_pre_1997_inflation_protection__2027](packets/autumn_budget_2025__ab2025__ppf_and_fas_pre_1997_inflation_protection__2027.md)
* [autumn_budget_2025__ab2025__ppf_and_fas_pre_1997_inflation_protection__2028](packets/autumn_budget_2025__ab2025__ppf_and_fas_pre_1997_inflation_protection__2028.md)
* [autumn_budget_2025__ab2025__ppf_and_fas_pre_1997_inflation_protection__2029](packets/autumn_budget_2025__ab2025__ppf_and_fas_pre_1997_inflation_protection__2029.md)
* [autumn_budget_2025__ab2025__ppf_and_fas_pre_1997_inflation_protection__2030](packets/autumn_budget_2025__ab2025__ppf_and_fas_pre_1997_inflation_protection__2030.md)
* [autumn_budget_2025__ab2025__property_income_separate_rates__2025](packets/autumn_budget_2025__ab2025__property_income_separate_rates__2025.md)
* [autumn_budget_2025__ab2025__property_income_separate_rates__2026](packets/autumn_budget_2025__ab2025__property_income_separate_rates__2026.md)
* [autumn_budget_2025__ab2025__property_income_separate_rates__2027](packets/autumn_budget_2025__ab2025__property_income_separate_rates__2027.md)
* [autumn_budget_2025__ab2025__property_income_separate_rates__2028](packets/autumn_budget_2025__ab2025__property_income_separate_rates__2028.md)
* [autumn_budget_2025__ab2025__property_income_separate_rates__2029](packets/autumn_budget_2025__ab2025__property_income_separate_rates__2029.md)
* [autumn_budget_2025__ab2025__property_income_separate_rates__2030](packets/autumn_budget_2025__ab2025__property_income_separate_rates__2030.md)
* [autumn_budget_2025__ab2025__rail_fares_freeze_2026__2025](packets/autumn_budget_2025__ab2025__rail_fares_freeze_2026__2025.md)
* [autumn_budget_2025__ab2025__rail_fares_freeze_2026__2026](packets/autumn_budget_2025__ab2025__rail_fares_freeze_2026__2026.md)
* [autumn_budget_2025__ab2025__rail_fares_freeze_2026__2027](packets/autumn_budget_2025__ab2025__rail_fares_freeze_2026__2027.md)
* [autumn_budget_2025__ab2025__rail_fares_freeze_2026__2028](packets/autumn_budget_2025__ab2025__rail_fares_freeze_2026__2028.md)
* [autumn_budget_2025__ab2025__rail_fares_freeze_2026__2029](packets/autumn_budget_2025__ab2025__rail_fares_freeze_2026__2029.md)
* [autumn_budget_2025__ab2025__rail_fares_freeze_2026__2030](packets/autumn_budget_2025__ab2025__rail_fares_freeze_2026__2030.md)
* [autumn_budget_2025__ab2025__rdel_efficiencies_and_savings__2025](packets/autumn_budget_2025__ab2025__rdel_efficiencies_and_savings__2025.md)
* [autumn_budget_2025__ab2025__rdel_efficiencies_and_savings__2026](packets/autumn_budget_2025__ab2025__rdel_efficiencies_and_savings__2026.md)
* [autumn_budget_2025__ab2025__rdel_efficiencies_and_savings__2027](packets/autumn_budget_2025__ab2025__rdel_efficiencies_and_savings__2027.md)
* [autumn_budget_2025__ab2025__rdel_efficiencies_and_savings__2028](packets/autumn_budget_2025__ab2025__rdel_efficiencies_and_savings__2028.md)
* [autumn_budget_2025__ab2025__rdel_efficiencies_and_savings__2029](packets/autumn_budget_2025__ab2025__rdel_efficiencies_and_savings__2029.md)
* [autumn_budget_2025__ab2025__rdel_efficiencies_and_savings__2030](packets/autumn_budget_2025__ab2025__rdel_efficiencies_and_savings__2030.md)
* [autumn_budget_2025__ab2025__rebuilding_britain_capital_investment__2025](packets/autumn_budget_2025__ab2025__rebuilding_britain_capital_investment__2025.md)
* [autumn_budget_2025__ab2025__rebuilding_britain_capital_investment__2026](packets/autumn_budget_2025__ab2025__rebuilding_britain_capital_investment__2026.md)
* [autumn_budget_2025__ab2025__rebuilding_britain_capital_investment__2027](packets/autumn_budget_2025__ab2025__rebuilding_britain_capital_investment__2027.md)
* [autumn_budget_2025__ab2025__rebuilding_britain_capital_investment__2028](packets/autumn_budget_2025__ab2025__rebuilding_britain_capital_investment__2028.md)
* [autumn_budget_2025__ab2025__rebuilding_britain_capital_investment__2029](packets/autumn_budget_2025__ab2025__rebuilding_britain_capital_investment__2029.md)
* [autumn_budget_2025__ab2025__rebuilding_britain_capital_investment__2030](packets/autumn_budget_2025__ab2025__rebuilding_britain_capital_investment__2030.md)
* [autumn_budget_2025__ab2025__renewables_obligation_exchequer_funded_75pct__2025](packets/autumn_budget_2025__ab2025__renewables_obligation_exchequer_funded_75pct__2025.md)
* [autumn_budget_2025__ab2025__renewables_obligation_exchequer_funded_75pct__2026](packets/autumn_budget_2025__ab2025__renewables_obligation_exchequer_funded_75pct__2026.md)
* [autumn_budget_2025__ab2025__renewables_obligation_exchequer_funded_75pct__2027](packets/autumn_budget_2025__ab2025__renewables_obligation_exchequer_funded_75pct__2027.md)
* [autumn_budget_2025__ab2025__renewables_obligation_exchequer_funded_75pct__2028](packets/autumn_budget_2025__ab2025__renewables_obligation_exchequer_funded_75pct__2028.md)
* [autumn_budget_2025__ab2025__renewables_obligation_exchequer_funded_75pct__2029](packets/autumn_budget_2025__ab2025__renewables_obligation_exchequer_funded_75pct__2029.md)
* [autumn_budget_2025__ab2025__renewables_obligation_exchequer_funded_75pct__2030](packets/autumn_budget_2025__ab2025__renewables_obligation_exchequer_funded_75pct__2030.md)
* [autumn_budget_2025__ab2025__salary_sacrifice_pension_nics_cap_2000__2025](packets/autumn_budget_2025__ab2025__salary_sacrifice_pension_nics_cap_2000__2025.md)
* [autumn_budget_2025__ab2025__salary_sacrifice_pension_nics_cap_2000__2026](packets/autumn_budget_2025__ab2025__salary_sacrifice_pension_nics_cap_2000__2026.md)
* [autumn_budget_2025__ab2025__salary_sacrifice_pension_nics_cap_2000__2027](packets/autumn_budget_2025__ab2025__salary_sacrifice_pension_nics_cap_2000__2027.md)
* [autumn_budget_2025__ab2025__salary_sacrifice_pension_nics_cap_2000__2028](packets/autumn_budget_2025__ab2025__salary_sacrifice_pension_nics_cap_2000__2028.md)
* [autumn_budget_2025__ab2025__salary_sacrifice_pension_nics_cap_2000__2029](packets/autumn_budget_2025__ab2025__salary_sacrifice_pension_nics_cap_2000__2029.md)
* [autumn_budget_2025__ab2025__salary_sacrifice_pension_nics_cap_2000__2030](packets/autumn_budget_2025__ab2025__salary_sacrifice_pension_nics_cap_2000__2030.md)
* [autumn_budget_2025__ab2025__savings_rates_plus_2pp_and_starter_limit_held__2025](packets/autumn_budget_2025__ab2025__savings_rates_plus_2pp_and_starter_limit_held__2025.md)
* [autumn_budget_2025__ab2025__savings_rates_plus_2pp_and_starter_limit_held__2026](packets/autumn_budget_2025__ab2025__savings_rates_plus_2pp_and_starter_limit_held__2026.md)
* [autumn_budget_2025__ab2025__savings_rates_plus_2pp_and_starter_limit_held__2027](packets/autumn_budget_2025__ab2025__savings_rates_plus_2pp_and_starter_limit_held__2027.md)
* [autumn_budget_2025__ab2025__savings_rates_plus_2pp_and_starter_limit_held__2028](packets/autumn_budget_2025__ab2025__savings_rates_plus_2pp_and_starter_limit_held__2028.md)
* [autumn_budget_2025__ab2025__savings_rates_plus_2pp_and_starter_limit_held__2029](packets/autumn_budget_2025__ab2025__savings_rates_plus_2pp_and_starter_limit_held__2029.md)
* [autumn_budget_2025__ab2025__savings_rates_plus_2pp_and_starter_limit_held__2030](packets/autumn_budget_2025__ab2025__savings_rates_plus_2pp_and_starter_limit_held__2030.md)
* [autumn_budget_2025__ab2025__sdil_threshold_cut_and_milk_based_drinks__2025](packets/autumn_budget_2025__ab2025__sdil_threshold_cut_and_milk_based_drinks__2025.md)
* [autumn_budget_2025__ab2025__sdil_threshold_cut_and_milk_based_drinks__2026](packets/autumn_budget_2025__ab2025__sdil_threshold_cut_and_milk_based_drinks__2026.md)
* [autumn_budget_2025__ab2025__sdil_threshold_cut_and_milk_based_drinks__2027](packets/autumn_budget_2025__ab2025__sdil_threshold_cut_and_milk_based_drinks__2027.md)
* [autumn_budget_2025__ab2025__sdil_threshold_cut_and_milk_based_drinks__2028](packets/autumn_budget_2025__ab2025__sdil_threshold_cut_and_milk_based_drinks__2028.md)
* [autumn_budget_2025__ab2025__sdil_threshold_cut_and_milk_based_drinks__2029](packets/autumn_budget_2025__ab2025__sdil_threshold_cut_and_milk_based_drinks__2029.md)
* [autumn_budget_2025__ab2025__sdil_threshold_cut_and_milk_based_drinks__2030](packets/autumn_budget_2025__ab2025__sdil_threshold_cut_and_milk_based_drinks__2030.md)
* [autumn_budget_2025__ab2025__sizewell_c_rab_levy_reclassification__2025](packets/autumn_budget_2025__ab2025__sizewell_c_rab_levy_reclassification__2025.md)
* [autumn_budget_2025__ab2025__sizewell_c_rab_levy_reclassification__2026](packets/autumn_budget_2025__ab2025__sizewell_c_rab_levy_reclassification__2026.md)
* [autumn_budget_2025__ab2025__sizewell_c_rab_levy_reclassification__2027](packets/autumn_budget_2025__ab2025__sizewell_c_rab_levy_reclassification__2027.md)
* [autumn_budget_2025__ab2025__sizewell_c_rab_levy_reclassification__2028](packets/autumn_budget_2025__ab2025__sizewell_c_rab_levy_reclassification__2028.md)
* [autumn_budget_2025__ab2025__sizewell_c_rab_levy_reclassification__2029](packets/autumn_budget_2025__ab2025__sizewell_c_rab_levy_reclassification__2029.md)
* [autumn_budget_2025__ab2025__sizewell_c_rab_levy_reclassification__2030](packets/autumn_budget_2025__ab2025__sizewell_c_rab_levy_reclassification__2030.md)
* [autumn_budget_2025__ab2025__student_finance_lle_launch_and_loan_outlay__2025](packets/autumn_budget_2025__ab2025__student_finance_lle_launch_and_loan_outlay__2025.md)
* [autumn_budget_2025__ab2025__student_finance_lle_launch_and_loan_outlay__2026](packets/autumn_budget_2025__ab2025__student_finance_lle_launch_and_loan_outlay__2026.md)
* [autumn_budget_2025__ab2025__student_finance_lle_launch_and_loan_outlay__2027](packets/autumn_budget_2025__ab2025__student_finance_lle_launch_and_loan_outlay__2027.md)
* [autumn_budget_2025__ab2025__student_finance_lle_launch_and_loan_outlay__2028](packets/autumn_budget_2025__ab2025__student_finance_lle_launch_and_loan_outlay__2028.md)
* [autumn_budget_2025__ab2025__student_finance_lle_launch_and_loan_outlay__2029](packets/autumn_budget_2025__ab2025__student_finance_lle_launch_and_loan_outlay__2029.md)
* [autumn_budget_2025__ab2025__student_finance_lle_launch_and_loan_outlay__2030](packets/autumn_budget_2025__ab2025__student_finance_lle_launch_and_loan_outlay__2030.md)
* [autumn_budget_2025__ab2025__student_loans_plan2_threshold_freeze__2025](packets/autumn_budget_2025__ab2025__student_loans_plan2_threshold_freeze__2025.md)
* [autumn_budget_2025__ab2025__student_loans_plan2_threshold_freeze__2026](packets/autumn_budget_2025__ab2025__student_loans_plan2_threshold_freeze__2026.md)
* [autumn_budget_2025__ab2025__student_loans_plan2_threshold_freeze__2027](packets/autumn_budget_2025__ab2025__student_loans_plan2_threshold_freeze__2027.md)
* [autumn_budget_2025__ab2025__student_loans_plan2_threshold_freeze__2028](packets/autumn_budget_2025__ab2025__student_loans_plan2_threshold_freeze__2028.md)
* [autumn_budget_2025__ab2025__student_loans_plan2_threshold_freeze__2029](packets/autumn_budget_2025__ab2025__student_loans_plan2_threshold_freeze__2029.md)
* [autumn_budget_2025__ab2025__student_loans_plan2_threshold_freeze__2030](packets/autumn_budget_2025__ab2025__student_loans_plan2_threshold_freeze__2030.md)
* [autumn_budget_2025__ab2025__supporting_savers_help_to_save_and_cash_isa_limit__2025](packets/autumn_budget_2025__ab2025__supporting_savers_help_to_save_and_cash_isa_limit__2025.md)
* [autumn_budget_2025__ab2025__supporting_savers_help_to_save_and_cash_isa_limit__2026](packets/autumn_budget_2025__ab2025__supporting_savers_help_to_save_and_cash_isa_limit__2026.md)
* [autumn_budget_2025__ab2025__supporting_savers_help_to_save_and_cash_isa_limit__2027](packets/autumn_budget_2025__ab2025__supporting_savers_help_to_save_and_cash_isa_limit__2027.md)
* [autumn_budget_2025__ab2025__supporting_savers_help_to_save_and_cash_isa_limit__2028](packets/autumn_budget_2025__ab2025__supporting_savers_help_to_save_and_cash_isa_limit__2028.md)
* [autumn_budget_2025__ab2025__supporting_savers_help_to_save_and_cash_isa_limit__2029](packets/autumn_budget_2025__ab2025__supporting_savers_help_to_save_and_cash_isa_limit__2029.md)
* [autumn_budget_2025__ab2025__supporting_savers_help_to_save_and_cash_isa_limit__2030](packets/autumn_budget_2025__ab2025__supporting_savers_help_to_save_and_cash_isa_limit__2030.md)
* [autumn_budget_2025__ab2025__systems_and_compliance_investment_hmrc_dwp__2025](packets/autumn_budget_2025__ab2025__systems_and_compliance_investment_hmrc_dwp__2025.md)
* [autumn_budget_2025__ab2025__systems_and_compliance_investment_hmrc_dwp__2026](packets/autumn_budget_2025__ab2025__systems_and_compliance_investment_hmrc_dwp__2026.md)
* [autumn_budget_2025__ab2025__systems_and_compliance_investment_hmrc_dwp__2027](packets/autumn_budget_2025__ab2025__systems_and_compliance_investment_hmrc_dwp__2027.md)
* [autumn_budget_2025__ab2025__systems_and_compliance_investment_hmrc_dwp__2028](packets/autumn_budget_2025__ab2025__systems_and_compliance_investment_hmrc_dwp__2028.md)
* [autumn_budget_2025__ab2025__systems_and_compliance_investment_hmrc_dwp__2029](packets/autumn_budget_2025__ab2025__systems_and_compliance_investment_hmrc_dwp__2029.md)
* [autumn_budget_2025__ab2025__systems_and_compliance_investment_hmrc_dwp__2030](packets/autumn_budget_2025__ab2025__systems_and_compliance_investment_hmrc_dwp__2030.md)
* [autumn_budget_2025__ab2025__tariffs_changes_since_spring_2025__2025](packets/autumn_budget_2025__ab2025__tariffs_changes_since_spring_2025__2025.md)
* [autumn_budget_2025__ab2025__tariffs_changes_since_spring_2025__2026](packets/autumn_budget_2025__ab2025__tariffs_changes_since_spring_2025__2026.md)
* [autumn_budget_2025__ab2025__tariffs_changes_since_spring_2025__2027](packets/autumn_budget_2025__ab2025__tariffs_changes_since_spring_2025__2027.md)
* [autumn_budget_2025__ab2025__tariffs_changes_since_spring_2025__2028](packets/autumn_budget_2025__ab2025__tariffs_changes_since_spring_2025__2028.md)
* [autumn_budget_2025__ab2025__tariffs_changes_since_spring_2025__2029](packets/autumn_budget_2025__ab2025__tariffs_changes_since_spring_2025__2029.md)
* [autumn_budget_2025__ab2025__tariffs_changes_since_spring_2025__2030](packets/autumn_budget_2025__ab2025__tariffs_changes_since_spring_2025__2030.md)
* [autumn_budget_2025__ab2025__toms_private_hire_vehicles_excluded__2025](packets/autumn_budget_2025__ab2025__toms_private_hire_vehicles_excluded__2025.md)
* [autumn_budget_2025__ab2025__toms_private_hire_vehicles_excluded__2026](packets/autumn_budget_2025__ab2025__toms_private_hire_vehicles_excluded__2026.md)
* [autumn_budget_2025__ab2025__toms_private_hire_vehicles_excluded__2027](packets/autumn_budget_2025__ab2025__toms_private_hire_vehicles_excluded__2027.md)
* [autumn_budget_2025__ab2025__toms_private_hire_vehicles_excluded__2028](packets/autumn_budget_2025__ab2025__toms_private_hire_vehicles_excluded__2028.md)
* [autumn_budget_2025__ab2025__toms_private_hire_vehicles_excluded__2029](packets/autumn_budget_2025__ab2025__toms_private_hire_vehicles_excluded__2029.md)
* [autumn_budget_2025__ab2025__toms_private_hire_vehicles_excluded__2030](packets/autumn_budget_2025__ab2025__toms_private_hire_vehicles_excluded__2030.md)
* [autumn_budget_2025__ab2025__trust_charges_cap_and_post_departure_trade_profits__2025](packets/autumn_budget_2025__ab2025__trust_charges_cap_and_post_departure_trade_profits__2025.md)
* [autumn_budget_2025__ab2025__trust_charges_cap_and_post_departure_trade_profits__2026](packets/autumn_budget_2025__ab2025__trust_charges_cap_and_post_departure_trade_profits__2026.md)
* [autumn_budget_2025__ab2025__trust_charges_cap_and_post_departure_trade_profits__2027](packets/autumn_budget_2025__ab2025__trust_charges_cap_and_post_departure_trade_profits__2027.md)
* [autumn_budget_2025__ab2025__trust_charges_cap_and_post_departure_trade_profits__2028](packets/autumn_budget_2025__ab2025__trust_charges_cap_and_post_departure_trade_profits__2028.md)
* [autumn_budget_2025__ab2025__trust_charges_cap_and_post_departure_trade_profits__2029](packets/autumn_budget_2025__ab2025__trust_charges_cap_and_post_departure_trade_profits__2029.md)
* [autumn_budget_2025__ab2025__trust_charges_cap_and_post_departure_trade_profits__2030](packets/autumn_budget_2025__ab2025__trust_charges_cap_and_post_departure_trade_profits__2030.md)
* [autumn_budget_2025__ab2025__uc_child_element_remove_two_child_limit__2025](packets/autumn_budget_2025__ab2025__uc_child_element_remove_two_child_limit__2025.md)
* [autumn_budget_2025__ab2025__uc_child_element_remove_two_child_limit__2026](packets/autumn_budget_2025__ab2025__uc_child_element_remove_two_child_limit__2026.md)
* [autumn_budget_2025__ab2025__uc_child_element_remove_two_child_limit__2027](packets/autumn_budget_2025__ab2025__uc_child_element_remove_two_child_limit__2027.md)
* [autumn_budget_2025__ab2025__uc_child_element_remove_two_child_limit__2028](packets/autumn_budget_2025__ab2025__uc_child_element_remove_two_child_limit__2028.md)
* [autumn_budget_2025__ab2025__uc_child_element_remove_two_child_limit__2029](packets/autumn_budget_2025__ab2025__uc_child_element_remove_two_child_limit__2029.md)
* [autumn_budget_2025__ab2025__uc_child_element_remove_two_child_limit__2030](packets/autumn_budget_2025__ab2025__uc_child_element_remove_two_child_limit__2030.md)
* [autumn_budget_2025__ab2025__uc_standard_allowance_and_health_element_rebalancing__2025](packets/autumn_budget_2025__ab2025__uc_standard_allowance_and_health_element_rebalancing__2025.md)
* [autumn_budget_2025__ab2025__uc_standard_allowance_and_health_element_rebalancing__2026](packets/autumn_budget_2025__ab2025__uc_standard_allowance_and_health_element_rebalancing__2026.md)
* [autumn_budget_2025__ab2025__uc_standard_allowance_and_health_element_rebalancing__2027](packets/autumn_budget_2025__ab2025__uc_standard_allowance_and_health_element_rebalancing__2027.md)
* [autumn_budget_2025__ab2025__uc_standard_allowance_and_health_element_rebalancing__2028](packets/autumn_budget_2025__ab2025__uc_standard_allowance_and_health_element_rebalancing__2028.md)
* [autumn_budget_2025__ab2025__uc_standard_allowance_and_health_element_rebalancing__2029](packets/autumn_budget_2025__ab2025__uc_standard_allowance_and_health_element_rebalancing__2029.md)
* [autumn_budget_2025__ab2025__uc_standard_allowance_and_health_element_rebalancing__2030](packets/autumn_budget_2025__ab2025__uc_standard_allowance_and_health_element_rebalancing__2030.md)
* [autumn_budget_2025__ab2025__uc_surplus_earnings_threshold_2500_extended__2025](packets/autumn_budget_2025__ab2025__uc_surplus_earnings_threshold_2500_extended__2025.md)
* [autumn_budget_2025__ab2025__uc_surplus_earnings_threshold_2500_extended__2026](packets/autumn_budget_2025__ab2025__uc_surplus_earnings_threshold_2500_extended__2026.md)
* [autumn_budget_2025__ab2025__uc_surplus_earnings_threshold_2500_extended__2027](packets/autumn_budget_2025__ab2025__uc_surplus_earnings_threshold_2500_extended__2027.md)
* [autumn_budget_2025__ab2025__uc_surplus_earnings_threshold_2500_extended__2028](packets/autumn_budget_2025__ab2025__uc_surplus_earnings_threshold_2500_extended__2028.md)
* [autumn_budget_2025__ab2025__uc_surplus_earnings_threshold_2500_extended__2029](packets/autumn_budget_2025__ab2025__uc_surplus_earnings_threshold_2500_extended__2029.md)
* [autumn_budget_2025__ab2025__uc_surplus_earnings_threshold_2500_extended__2030](packets/autumn_budget_2025__ab2025__uc_surplus_earnings_threshold_2500_extended__2030.md)
* [autumn_budget_2025__ab2025__uk_eu_sps_agreement_defra_costs__2025](packets/autumn_budget_2025__ab2025__uk_eu_sps_agreement_defra_costs__2025.md)
* [autumn_budget_2025__ab2025__uk_eu_sps_agreement_defra_costs__2026](packets/autumn_budget_2025__ab2025__uk_eu_sps_agreement_defra_costs__2026.md)
* [autumn_budget_2025__ab2025__uk_eu_sps_agreement_defra_costs__2027](packets/autumn_budget_2025__ab2025__uk_eu_sps_agreement_defra_costs__2027.md)
* [autumn_budget_2025__ab2025__uk_eu_sps_agreement_defra_costs__2028](packets/autumn_budget_2025__ab2025__uk_eu_sps_agreement_defra_costs__2028.md)
* [autumn_budget_2025__ab2025__uk_eu_sps_agreement_defra_costs__2029](packets/autumn_budget_2025__ab2025__uk_eu_sps_agreement_defra_costs__2029.md)
* [autumn_budget_2025__ab2025__uk_eu_sps_agreement_defra_costs__2030](packets/autumn_budget_2025__ab2025__uk_eu_sps_agreement_defra_costs__2030.md)
* [autumn_budget_2025__ab2025__uk_listing_relief_sdrt__2025](packets/autumn_budget_2025__ab2025__uk_listing_relief_sdrt__2025.md)
* [autumn_budget_2025__ab2025__uk_listing_relief_sdrt__2026](packets/autumn_budget_2025__ab2025__uk_listing_relief_sdrt__2026.md)
* [autumn_budget_2025__ab2025__uk_listing_relief_sdrt__2027](packets/autumn_budget_2025__ab2025__uk_listing_relief_sdrt__2027.md)
* [autumn_budget_2025__ab2025__uk_listing_relief_sdrt__2028](packets/autumn_budget_2025__ab2025__uk_listing_relief_sdrt__2028.md)
* [autumn_budget_2025__ab2025__uk_listing_relief_sdrt__2029](packets/autumn_budget_2025__ab2025__uk_listing_relief_sdrt__2029.md)
* [autumn_budget_2025__ab2025__uk_listing_relief_sdrt__2030](packets/autumn_budget_2025__ab2025__uk_listing_relief_sdrt__2030.md)
* [autumn_budget_2025__ab2025__vat_relief_business_donations_of_goods_to_charity__2025](packets/autumn_budget_2025__ab2025__vat_relief_business_donations_of_goods_to_charity__2025.md)
* [autumn_budget_2025__ab2025__vat_relief_business_donations_of_goods_to_charity__2026](packets/autumn_budget_2025__ab2025__vat_relief_business_donations_of_goods_to_charity__2026.md)
* [autumn_budget_2025__ab2025__vat_relief_business_donations_of_goods_to_charity__2027](packets/autumn_budget_2025__ab2025__vat_relief_business_donations_of_goods_to_charity__2027.md)
* [autumn_budget_2025__ab2025__vat_relief_business_donations_of_goods_to_charity__2028](packets/autumn_budget_2025__ab2025__vat_relief_business_donations_of_goods_to_charity__2028.md)
* [autumn_budget_2025__ab2025__vat_relief_business_donations_of_goods_to_charity__2029](packets/autumn_budget_2025__ab2025__vat_relief_business_donations_of_goods_to_charity__2029.md)
* [autumn_budget_2025__ab2025__vat_relief_business_donations_of_goods_to_charity__2030](packets/autumn_budget_2025__ab2025__vat_relief_business_donations_of_goods_to_charity__2030.md)
* [autumn_budget_2025__ab2025__vct_and_eis_investment_limits_increased__2025](packets/autumn_budget_2025__ab2025__vct_and_eis_investment_limits_increased__2025.md)
* [autumn_budget_2025__ab2025__vct_and_eis_investment_limits_increased__2026](packets/autumn_budget_2025__ab2025__vct_and_eis_investment_limits_increased__2026.md)
* [autumn_budget_2025__ab2025__vct_and_eis_investment_limits_increased__2027](packets/autumn_budget_2025__ab2025__vct_and_eis_investment_limits_increased__2027.md)
* [autumn_budget_2025__ab2025__vct_and_eis_investment_limits_increased__2028](packets/autumn_budget_2025__ab2025__vct_and_eis_investment_limits_increased__2028.md)
* [autumn_budget_2025__ab2025__vct_and_eis_investment_limits_increased__2029](packets/autumn_budget_2025__ab2025__vct_and_eis_investment_limits_increased__2029.md)
* [autumn_budget_2025__ab2025__vct_and_eis_investment_limits_increased__2030](packets/autumn_budget_2025__ab2025__vct_and_eis_investment_limits_increased__2030.md)
* [autumn_budget_2025__ab2025__vct_income_tax_relief_reduced__2025](packets/autumn_budget_2025__ab2025__vct_income_tax_relief_reduced__2025.md)
* [autumn_budget_2025__ab2025__vct_income_tax_relief_reduced__2026](packets/autumn_budget_2025__ab2025__vct_income_tax_relief_reduced__2026.md)
* [autumn_budget_2025__ab2025__vct_income_tax_relief_reduced__2027](packets/autumn_budget_2025__ab2025__vct_income_tax_relief_reduced__2027.md)
* [autumn_budget_2025__ab2025__vct_income_tax_relief_reduced__2028](packets/autumn_budget_2025__ab2025__vct_income_tax_relief_reduced__2028.md)
* [autumn_budget_2025__ab2025__vct_income_tax_relief_reduced__2029](packets/autumn_budget_2025__ab2025__vct_income_tax_relief_reduced__2029.md)
* [autumn_budget_2025__ab2025__vct_income_tax_relief_reduced__2030](packets/autumn_budget_2025__ab2025__vct_income_tax_relief_reduced__2030.md)
* [autumn_budget_2025__ab2025__warm_homes_plan_and_warm_home_discount_expansion__2025](packets/autumn_budget_2025__ab2025__warm_homes_plan_and_warm_home_discount_expansion__2025.md)
* [autumn_budget_2025__ab2025__warm_homes_plan_and_warm_home_discount_expansion__2026](packets/autumn_budget_2025__ab2025__warm_homes_plan_and_warm_home_discount_expansion__2026.md)
* [autumn_budget_2025__ab2025__warm_homes_plan_and_warm_home_discount_expansion__2027](packets/autumn_budget_2025__ab2025__warm_homes_plan_and_warm_home_discount_expansion__2027.md)
* [autumn_budget_2025__ab2025__warm_homes_plan_and_warm_home_discount_expansion__2028](packets/autumn_budget_2025__ab2025__warm_homes_plan_and_warm_home_discount_expansion__2028.md)
* [autumn_budget_2025__ab2025__warm_homes_plan_and_warm_home_discount_expansion__2029](packets/autumn_budget_2025__ab2025__warm_homes_plan_and_warm_home_discount_expansion__2029.md)
* [autumn_budget_2025__ab2025__warm_homes_plan_and_warm_home_discount_expansion__2030](packets/autumn_budget_2025__ab2025__warm_homes_plan_and_warm_home_discount_expansion__2030.md)
* [autumn_budget_2025__ab2025__winter_fuel_payment_income_test_35000__2025](packets/autumn_budget_2025__ab2025__winter_fuel_payment_income_test_35000__2025.md)
* [autumn_budget_2025__ab2025__winter_fuel_payment_income_test_35000__2026](packets/autumn_budget_2025__ab2025__winter_fuel_payment_income_test_35000__2026.md)
* [autumn_budget_2025__ab2025__winter_fuel_payment_income_test_35000__2027](packets/autumn_budget_2025__ab2025__winter_fuel_payment_income_test_35000__2027.md)
* [autumn_budget_2025__ab2025__winter_fuel_payment_income_test_35000__2028](packets/autumn_budget_2025__ab2025__winter_fuel_payment_income_test_35000__2028.md)
* [autumn_budget_2025__ab2025__winter_fuel_payment_income_test_35000__2029](packets/autumn_budget_2025__ab2025__winter_fuel_payment_income_test_35000__2029.md)
* [autumn_budget_2025__ab2025__winter_fuel_payment_income_test_35000__2030](packets/autumn_budget_2025__ab2025__winter_fuel_payment_income_test_35000__2030.md)
* [autumn_budget_2025__ab2025__writing_down_allowances_14pct_and_40pct_fya__2025](packets/autumn_budget_2025__ab2025__writing_down_allowances_14pct_and_40pct_fya__2025.md)
* [autumn_budget_2025__ab2025__writing_down_allowances_14pct_and_40pct_fya__2026](packets/autumn_budget_2025__ab2025__writing_down_allowances_14pct_and_40pct_fya__2026.md)
* [autumn_budget_2025__ab2025__writing_down_allowances_14pct_and_40pct_fya__2027](packets/autumn_budget_2025__ab2025__writing_down_allowances_14pct_and_40pct_fya__2027.md)
* [autumn_budget_2025__ab2025__writing_down_allowances_14pct_and_40pct_fya__2028](packets/autumn_budget_2025__ab2025__writing_down_allowances_14pct_and_40pct_fya__2028.md)
* [autumn_budget_2025__ab2025__writing_down_allowances_14pct_and_40pct_fya__2029](packets/autumn_budget_2025__ab2025__writing_down_allowances_14pct_and_40pct_fya__2029.md)
* [autumn_budget_2025__ab2025__writing_down_allowances_14pct_and_40pct_fya__2030](packets/autumn_budget_2025__ab2025__writing_down_allowances_14pct_and_40pct_fya__2030.md)
* [autumn_budget_2025__council_tax_precepts_5_flexibility_for_fire_authorities__2025](packets/autumn_budget_2025__council_tax_precepts_5_flexibility_for_fire_authorities__2025.md)
* [autumn_budget_2025__council_tax_precepts_5_flexibility_for_fire_authorities__2026](packets/autumn_budget_2025__council_tax_precepts_5_flexibility_for_fire_authorities__2026.md)
* [autumn_budget_2025__council_tax_precepts_5_flexibility_for_fire_authorities__2027](packets/autumn_budget_2025__council_tax_precepts_5_flexibility_for_fire_authorities__2027.md)
* [autumn_budget_2025__council_tax_precepts_5_flexibility_for_fire_authorities__2028](packets/autumn_budget_2025__council_tax_precepts_5_flexibility_for_fire_authorities__2028.md)
* [autumn_budget_2025__council_tax_precepts_5_flexibility_for_fire_authorities__2029](packets/autumn_budget_2025__council_tax_precepts_5_flexibility_for_fire_authorities__2029.md)
* [autumn_budget_2025__council_tax_precepts_5_flexibility_for_fire_authorities__2030](packets/autumn_budget_2025__council_tax_precepts_5_flexibility_for_fire_authorities__2030.md)
* [autumn_budget_2025__hm_treasury_allowance_for_shortfall_assumption_psce_in_rdel__2025](packets/autumn_budget_2025__hm_treasury_allowance_for_shortfall_assumption_psce_in_rdel__2025.md)
* [autumn_budget_2025__hm_treasury_allowance_for_shortfall_assumption_psce_in_rdel__2026](packets/autumn_budget_2025__hm_treasury_allowance_for_shortfall_assumption_psce_in_rdel__2026.md)
* [autumn_budget_2025__hm_treasury_allowance_for_shortfall_assumption_psce_in_rdel__2027](packets/autumn_budget_2025__hm_treasury_allowance_for_shortfall_assumption_psce_in_rdel__2027.md)
* [autumn_budget_2025__hm_treasury_allowance_for_shortfall_assumption_psce_in_rdel__2028](packets/autumn_budget_2025__hm_treasury_allowance_for_shortfall_assumption_psce_in_rdel__2028.md)
* [autumn_budget_2025__hm_treasury_allowance_for_shortfall_assumption_psce_in_rdel__2029](packets/autumn_budget_2025__hm_treasury_allowance_for_shortfall_assumption_psce_in_rdel__2029.md)
* [autumn_budget_2025__hm_treasury_allowance_for_shortfall_assumption_psce_in_rdel__2030](packets/autumn_budget_2025__hm_treasury_allowance_for_shortfall_assumption_psce_in_rdel__2030.md)
* [autumn_budget_2025__hm_treasury_allowance_for_shortfall_assumption_psgi_in_cdel__2025](packets/autumn_budget_2025__hm_treasury_allowance_for_shortfall_assumption_psgi_in_cdel__2025.md)
* [autumn_budget_2025__hm_treasury_allowance_for_shortfall_assumption_psgi_in_cdel__2026](packets/autumn_budget_2025__hm_treasury_allowance_for_shortfall_assumption_psgi_in_cdel__2026.md)
* [autumn_budget_2025__hm_treasury_allowance_for_shortfall_assumption_psgi_in_cdel__2027](packets/autumn_budget_2025__hm_treasury_allowance_for_shortfall_assumption_psgi_in_cdel__2027.md)
* [autumn_budget_2025__hm_treasury_allowance_for_shortfall_assumption_psgi_in_cdel__2028](packets/autumn_budget_2025__hm_treasury_allowance_for_shortfall_assumption_psgi_in_cdel__2028.md)
* [autumn_budget_2025__hm_treasury_allowance_for_shortfall_assumption_psgi_in_cdel__2029](packets/autumn_budget_2025__hm_treasury_allowance_for_shortfall_assumption_psgi_in_cdel__2029.md)
* [autumn_budget_2025__hm_treasury_allowance_for_shortfall_assumption_psgi_in_cdel__2030](packets/autumn_budget_2025__hm_treasury_allowance_for_shortfall_assumption_psgi_in_cdel__2030.md)
* [autumn_budget_2025__increase_financial_conduct_authority_levies_from_april_2026__2025](packets/autumn_budget_2025__increase_financial_conduct_authority_levies_from_april_2026__2025.md)
* [autumn_budget_2025__increase_financial_conduct_authority_levies_from_april_2026__2026](packets/autumn_budget_2025__increase_financial_conduct_authority_levies_from_april_2026__2026.md)
* [autumn_budget_2025__increase_financial_conduct_authority_levies_from_april_2026__2027](packets/autumn_budget_2025__increase_financial_conduct_authority_levies_from_april_2026__2027.md)
* [autumn_budget_2025__increase_financial_conduct_authority_levies_from_april_2026__2028](packets/autumn_budget_2025__increase_financial_conduct_authority_levies_from_april_2026__2028.md)
* [autumn_budget_2025__increase_financial_conduct_authority_levies_from_april_2026__2029](packets/autumn_budget_2025__increase_financial_conduct_authority_levies_from_april_2026__2029.md)
* [autumn_budget_2025__increase_financial_conduct_authority_levies_from_april_2026__2030](packets/autumn_budget_2025__increase_financial_conduct_authority_levies_from_april_2026__2030.md)
* [autumn_budget_2025__increase_financial_conduct_authority_levies_from_april_2027__2025](packets/autumn_budget_2025__increase_financial_conduct_authority_levies_from_april_2027__2025.md)
* [autumn_budget_2025__increase_financial_conduct_authority_levies_from_april_2027__2026](packets/autumn_budget_2025__increase_financial_conduct_authority_levies_from_april_2027__2026.md)
* [autumn_budget_2025__increase_financial_conduct_authority_levies_from_april_2027__2027](packets/autumn_budget_2025__increase_financial_conduct_authority_levies_from_april_2027__2027.md)
* [autumn_budget_2025__increase_financial_conduct_authority_levies_from_april_2027__2028](packets/autumn_budget_2025__increase_financial_conduct_authority_levies_from_april_2027__2028.md)
* [autumn_budget_2025__increase_financial_conduct_authority_levies_from_april_2027__2029](packets/autumn_budget_2025__increase_financial_conduct_authority_levies_from_april_2027__2029.md)
* [autumn_budget_2025__increase_financial_conduct_authority_levies_from_april_2027__2030](packets/autumn_budget_2025__increase_financial_conduct_authority_levies_from_april_2027__2030.md)
* [autumn_budget_2025__increase_immigration_skills_charge_by_32_from_october_2025__2025](packets/autumn_budget_2025__increase_immigration_skills_charge_by_32_from_october_2025__2025.md)
* [autumn_budget_2025__increase_immigration_skills_charge_by_32_from_october_2025__2026](packets/autumn_budget_2025__increase_immigration_skills_charge_by_32_from_october_2025__2026.md)
* [autumn_budget_2025__increase_immigration_skills_charge_by_32_from_october_2025__2027](packets/autumn_budget_2025__increase_immigration_skills_charge_by_32_from_october_2025__2027.md)
* [autumn_budget_2025__increase_immigration_skills_charge_by_32_from_october_2025__2028](packets/autumn_budget_2025__increase_immigration_skills_charge_by_32_from_october_2025__2028.md)
* [autumn_budget_2025__increase_immigration_skills_charge_by_32_from_october_2025__2029](packets/autumn_budget_2025__increase_immigration_skills_charge_by_32_from_october_2025__2029.md)
* [autumn_budget_2025__increase_immigration_skills_charge_by_32_from_october_2025__2030](packets/autumn_budget_2025__increase_immigration_skills_charge_by_32_from_october_2025__2030.md)
* [autumn_budget_2025__increase_to_the_economic_crime_levy__2025](packets/autumn_budget_2025__increase_to_the_economic_crime_levy__2025.md)
* [autumn_budget_2025__increase_to_the_economic_crime_levy__2026](packets/autumn_budget_2025__increase_to_the_economic_crime_levy__2026.md)
* [autumn_budget_2025__increase_to_the_economic_crime_levy__2027](packets/autumn_budget_2025__increase_to_the_economic_crime_levy__2027.md)
* [autumn_budget_2025__increase_to_the_economic_crime_levy__2028](packets/autumn_budget_2025__increase_to_the_economic_crime_levy__2028.md)
* [autumn_budget_2025__increase_to_the_economic_crime_levy__2029](packets/autumn_budget_2025__increase_to_the_economic_crime_levy__2029.md)
* [autumn_budget_2025__increase_to_the_economic_crime_levy__2030](packets/autumn_budget_2025__increase_to_the_economic_crime_levy__2030.md)
* [autumn_budget_2025__international_student_levy__2025](packets/autumn_budget_2025__international_student_levy__2025.md)
* [autumn_budget_2025__international_student_levy__2026](packets/autumn_budget_2025__international_student_levy__2026.md)
* [autumn_budget_2025__international_student_levy__2027](packets/autumn_budget_2025__international_student_levy__2027.md)
* [autumn_budget_2025__international_student_levy__2028](packets/autumn_budget_2025__international_student_levy__2028.md)
* [autumn_budget_2025__international_student_levy__2029](packets/autumn_budget_2025__international_student_levy__2029.md)
* [autumn_budget_2025__international_student_levy__2030](packets/autumn_budget_2025__international_student_levy__2030.md)
* [autumn_budget_2025__main_estimates_departmental_cdel_plans_for_2025_26__2025](packets/autumn_budget_2025__main_estimates_departmental_cdel_plans_for_2025_26__2025.md)
* [autumn_budget_2025__main_estimates_departmental_cdel_plans_for_2025_26__2026](packets/autumn_budget_2025__main_estimates_departmental_cdel_plans_for_2025_26__2026.md)
* [autumn_budget_2025__main_estimates_departmental_cdel_plans_for_2025_26__2027](packets/autumn_budget_2025__main_estimates_departmental_cdel_plans_for_2025_26__2027.md)
* [autumn_budget_2025__main_estimates_departmental_cdel_plans_for_2025_26__2028](packets/autumn_budget_2025__main_estimates_departmental_cdel_plans_for_2025_26__2028.md)
* [autumn_budget_2025__main_estimates_departmental_cdel_plans_for_2025_26__2029](packets/autumn_budget_2025__main_estimates_departmental_cdel_plans_for_2025_26__2029.md)
* [autumn_budget_2025__main_estimates_departmental_cdel_plans_for_2025_26__2030](packets/autumn_budget_2025__main_estimates_departmental_cdel_plans_for_2025_26__2030.md)
* [autumn_budget_2025__main_estimates_departmental_rdel_plans_for_2025_26__2025](packets/autumn_budget_2025__main_estimates_departmental_rdel_plans_for_2025_26__2025.md)
* [autumn_budget_2025__main_estimates_departmental_rdel_plans_for_2025_26__2026](packets/autumn_budget_2025__main_estimates_departmental_rdel_plans_for_2025_26__2026.md)
* [autumn_budget_2025__main_estimates_departmental_rdel_plans_for_2025_26__2027](packets/autumn_budget_2025__main_estimates_departmental_rdel_plans_for_2025_26__2027.md)
* [autumn_budget_2025__main_estimates_departmental_rdel_plans_for_2025_26__2028](packets/autumn_budget_2025__main_estimates_departmental_rdel_plans_for_2025_26__2028.md)
* [autumn_budget_2025__main_estimates_departmental_rdel_plans_for_2025_26__2029](packets/autumn_budget_2025__main_estimates_departmental_rdel_plans_for_2025_26__2029.md)
* [autumn_budget_2025__main_estimates_departmental_rdel_plans_for_2025_26__2030](packets/autumn_budget_2025__main_estimates_departmental_rdel_plans_for_2025_26__2030.md)
* [autumn_budget_2025__obr_allowance_for_shortfall_assumptions_psce_in_rdel__2025](packets/autumn_budget_2025__obr_allowance_for_shortfall_assumptions_psce_in_rdel__2025.md)
* [autumn_budget_2025__obr_allowance_for_shortfall_assumptions_psce_in_rdel__2026](packets/autumn_budget_2025__obr_allowance_for_shortfall_assumptions_psce_in_rdel__2026.md)
* [autumn_budget_2025__obr_allowance_for_shortfall_assumptions_psce_in_rdel__2027](packets/autumn_budget_2025__obr_allowance_for_shortfall_assumptions_psce_in_rdel__2027.md)
* [autumn_budget_2025__obr_allowance_for_shortfall_assumptions_psce_in_rdel__2028](packets/autumn_budget_2025__obr_allowance_for_shortfall_assumptions_psce_in_rdel__2028.md)
* [autumn_budget_2025__obr_allowance_for_shortfall_assumptions_psce_in_rdel__2029](packets/autumn_budget_2025__obr_allowance_for_shortfall_assumptions_psce_in_rdel__2029.md)
* [autumn_budget_2025__obr_allowance_for_shortfall_assumptions_psce_in_rdel__2030](packets/autumn_budget_2025__obr_allowance_for_shortfall_assumptions_psce_in_rdel__2030.md)
* [autumn_budget_2025__obr_allowance_for_shortfall_assumptions_psgi_in_cdel__2025](packets/autumn_budget_2025__obr_allowance_for_shortfall_assumptions_psgi_in_cdel__2025.md)
* [autumn_budget_2025__obr_allowance_for_shortfall_assumptions_psgi_in_cdel__2026](packets/autumn_budget_2025__obr_allowance_for_shortfall_assumptions_psgi_in_cdel__2026.md)
* [autumn_budget_2025__obr_allowance_for_shortfall_assumptions_psgi_in_cdel__2027](packets/autumn_budget_2025__obr_allowance_for_shortfall_assumptions_psgi_in_cdel__2027.md)
* [autumn_budget_2025__obr_allowance_for_shortfall_assumptions_psgi_in_cdel__2028](packets/autumn_budget_2025__obr_allowance_for_shortfall_assumptions_psgi_in_cdel__2028.md)
* [autumn_budget_2025__obr_allowance_for_shortfall_assumptions_psgi_in_cdel__2029](packets/autumn_budget_2025__obr_allowance_for_shortfall_assumptions_psgi_in_cdel__2029.md)
* [autumn_budget_2025__obr_allowance_for_shortfall_assumptions_psgi_in_cdel__2030](packets/autumn_budget_2025__obr_allowance_for_shortfall_assumptions_psgi_in_cdel__2030.md)
* [autumn_budget_2025__reclassification_from_departmental_expenditure_limits_to_annually_manage__2025](packets/autumn_budget_2025__reclassification_from_departmental_expenditure_limits_to_annually_manage__2025.md)
* [autumn_budget_2025__reclassification_from_departmental_expenditure_limits_to_annually_manage__2026](packets/autumn_budget_2025__reclassification_from_departmental_expenditure_limits_to_annually_manage__2026.md)
* [autumn_budget_2025__reclassification_from_departmental_expenditure_limits_to_annually_manage__2027](packets/autumn_budget_2025__reclassification_from_departmental_expenditure_limits_to_annually_manage__2027.md)
* [autumn_budget_2025__reclassification_from_departmental_expenditure_limits_to_annually_manage__2028](packets/autumn_budget_2025__reclassification_from_departmental_expenditure_limits_to_annually_manage__2028.md)
* [autumn_budget_2025__reclassification_from_departmental_expenditure_limits_to_annually_manage__2029](packets/autumn_budget_2025__reclassification_from_departmental_expenditure_limits_to_annually_manage__2029.md)
* [autumn_budget_2025__reclassification_from_departmental_expenditure_limits_to_annually_manage__2030](packets/autumn_budget_2025__reclassification_from_departmental_expenditure_limits_to_annually_manage__2030.md)
* [autumn_budget_2025__reclassification_of_spend_for_mayoral_combined_authorities__2025](packets/autumn_budget_2025__reclassification_of_spend_for_mayoral_combined_authorities__2025.md)
* [autumn_budget_2025__reclassification_of_spend_for_mayoral_combined_authorities__2026](packets/autumn_budget_2025__reclassification_of_spend_for_mayoral_combined_authorities__2026.md)
* [autumn_budget_2025__reclassification_of_spend_for_mayoral_combined_authorities__2027](packets/autumn_budget_2025__reclassification_of_spend_for_mayoral_combined_authorities__2027.md)
* [autumn_budget_2025__reclassification_of_spend_for_mayoral_combined_authorities__2028](packets/autumn_budget_2025__reclassification_of_spend_for_mayoral_combined_authorities__2028.md)
* [autumn_budget_2025__reclassification_of_spend_for_mayoral_combined_authorities__2029](packets/autumn_budget_2025__reclassification_of_spend_for_mayoral_combined_authorities__2029.md)
* [autumn_budget_2025__reclassification_of_spend_for_mayoral_combined_authorities__2030](packets/autumn_budget_2025__reclassification_of_spend_for_mayoral_combined_authorities__2030.md)
* [autumn_budget_2025__reduced_non_fiscal_capital_provision_for_intra_government_leases__2025](packets/autumn_budget_2025__reduced_non_fiscal_capital_provision_for_intra_government_leases__2025.md)
* [autumn_budget_2025__reduced_non_fiscal_capital_provision_for_intra_government_leases__2026](packets/autumn_budget_2025__reduced_non_fiscal_capital_provision_for_intra_government_leases__2026.md)
* [autumn_budget_2025__reduced_non_fiscal_capital_provision_for_intra_government_leases__2027](packets/autumn_budget_2025__reduced_non_fiscal_capital_provision_for_intra_government_leases__2027.md)
* [autumn_budget_2025__reduced_non_fiscal_capital_provision_for_intra_government_leases__2028](packets/autumn_budget_2025__reduced_non_fiscal_capital_provision_for_intra_government_leases__2028.md)
* [autumn_budget_2025__reduced_non_fiscal_capital_provision_for_intra_government_leases__2029](packets/autumn_budget_2025__reduced_non_fiscal_capital_provision_for_intra_government_leases__2029.md)
* [autumn_budget_2025__reduced_non_fiscal_capital_provision_for_intra_government_leases__2030](packets/autumn_budget_2025__reduced_non_fiscal_capital_provision_for_intra_government_leases__2030.md)
* [autumn_budget_2025__send_manage_send_pressures_within_overall_del_envelope_from_28_29__2025](packets/autumn_budget_2025__send_manage_send_pressures_within_overall_del_envelope_from_28_29__2025.md)
* [autumn_budget_2025__send_manage_send_pressures_within_overall_del_envelope_from_28_29__2026](packets/autumn_budget_2025__send_manage_send_pressures_within_overall_del_envelope_from_28_29__2026.md)
* [autumn_budget_2025__send_manage_send_pressures_within_overall_del_envelope_from_28_29__2027](packets/autumn_budget_2025__send_manage_send_pressures_within_overall_del_envelope_from_28_29__2027.md)
* [autumn_budget_2025__send_manage_send_pressures_within_overall_del_envelope_from_28_29__2028](packets/autumn_budget_2025__send_manage_send_pressures_within_overall_del_envelope_from_28_29__2028.md)
* [autumn_budget_2025__send_manage_send_pressures_within_overall_del_envelope_from_28_29__2029](packets/autumn_budget_2025__send_manage_send_pressures_within_overall_del_envelope_from_28_29__2029.md)
* [autumn_budget_2025__send_manage_send_pressures_within_overall_del_envelope_from_28_29__2030](packets/autumn_budget_2025__send_manage_send_pressures_within_overall_del_envelope_from_28_29__2030.md)
* [autumn_budget_2025__send_manage_send_pressures_within_overall_del_envelope_from_28_30__2025](packets/autumn_budget_2025__send_manage_send_pressures_within_overall_del_envelope_from_28_30__2025.md)
* [autumn_budget_2025__send_manage_send_pressures_within_overall_del_envelope_from_28_30__2026](packets/autumn_budget_2025__send_manage_send_pressures_within_overall_del_envelope_from_28_30__2026.md)
* [autumn_budget_2025__send_manage_send_pressures_within_overall_del_envelope_from_28_30__2027](packets/autumn_budget_2025__send_manage_send_pressures_within_overall_del_envelope_from_28_30__2027.md)
* [autumn_budget_2025__send_manage_send_pressures_within_overall_del_envelope_from_28_30__2028](packets/autumn_budget_2025__send_manage_send_pressures_within_overall_del_envelope_from_28_30__2028.md)
* [autumn_budget_2025__send_manage_send_pressures_within_overall_del_envelope_from_28_30__2029](packets/autumn_budget_2025__send_manage_send_pressures_within_overall_del_envelope_from_28_30__2029.md)
* [autumn_budget_2025__send_manage_send_pressures_within_overall_del_envelope_from_28_30__2030](packets/autumn_budget_2025__send_manage_send_pressures_within_overall_del_envelope_from_28_30__2030.md)
* [autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p__2023](packets/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p__2023.md)
* [autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p__2024](packets/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p__2024.md)
* [autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p__2025](packets/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p__2025.md)
* [autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p__2026](packets/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p__2026.md)
* [autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p__2027](packets/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p__2027.md)
* [autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p__2028](packets/autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p__2028.md)
* [autumn_statement_2023__class_2_self_employed_nics_abolition__2023](packets/autumn_statement_2023__class_2_self_employed_nics_abolition__2023.md)
* [autumn_statement_2023__class_2_self_employed_nics_abolition__2024](packets/autumn_statement_2023__class_2_self_employed_nics_abolition__2024.md)
* [autumn_statement_2023__class_2_self_employed_nics_abolition__2025](packets/autumn_statement_2023__class_2_self_employed_nics_abolition__2025.md)
* [autumn_statement_2023__class_2_self_employed_nics_abolition__2026](packets/autumn_statement_2023__class_2_self_employed_nics_abolition__2026.md)
* [autumn_statement_2023__class_2_self_employed_nics_abolition__2027](packets/autumn_statement_2023__class_2_self_employed_nics_abolition__2027.md)
* [autumn_statement_2023__class_2_self_employed_nics_abolition__2028](packets/autumn_statement_2023__class_2_self_employed_nics_abolition__2028.md)
* [autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p__2023](packets/autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p__2023.md)
* [autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p__2024](packets/autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p__2024.md)
* [autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p__2025](packets/autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p__2025.md)
* [autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p__2026](packets/autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p__2026.md)
* [autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p__2027](packets/autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p__2027.md)
* [autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p__2028](packets/autumn_statement_2023__class_4_self_employed_nics_main_rate_cut_1p__2028.md)
* [autumn_statement_2023__lha_reset_to_30th_percentile__2023](packets/autumn_statement_2023__lha_reset_to_30th_percentile__2023.md)
* [autumn_statement_2023__lha_reset_to_30th_percentile__2024](packets/autumn_statement_2023__lha_reset_to_30th_percentile__2024.md)
* [autumn_statement_2023__lha_reset_to_30th_percentile__2025](packets/autumn_statement_2023__lha_reset_to_30th_percentile__2025.md)
* [autumn_statement_2023__lha_reset_to_30th_percentile__2026](packets/autumn_statement_2023__lha_reset_to_30th_percentile__2026.md)
* [autumn_statement_2023__lha_reset_to_30th_percentile__2027](packets/autumn_statement_2023__lha_reset_to_30th_percentile__2027.md)
* [autumn_statement_2023__lha_reset_to_30th_percentile__2028](packets/autumn_statement_2023__lha_reset_to_30th_percentile__2028.md)
* [spring_budget_2023__pension_annual_allowance_package__2023](packets/spring_budget_2023__pension_annual_allowance_package__2023.md)
* [spring_budget_2023__pension_annual_allowance_package__2024](packets/spring_budget_2023__pension_annual_allowance_package__2024.md)
* [spring_budget_2023__pension_annual_allowance_package__2025](packets/spring_budget_2023__pension_annual_allowance_package__2025.md)
* [spring_budget_2023__pension_annual_allowance_package__2026](packets/spring_budget_2023__pension_annual_allowance_package__2026.md)
* [spring_budget_2023__pension_annual_allowance_package__2027](packets/spring_budget_2023__pension_annual_allowance_package__2027.md)
* [spring_budget_2023__uc_childcare_cap_increase__2023](packets/spring_budget_2023__uc_childcare_cap_increase__2023.md)
* [spring_budget_2023__uc_childcare_cap_increase__2024](packets/spring_budget_2023__uc_childcare_cap_increase__2024.md)
* [spring_budget_2023__uc_childcare_cap_increase__2025](packets/spring_budget_2023__uc_childcare_cap_increase__2025.md)
* [spring_budget_2023__uc_childcare_cap_increase__2026](packets/spring_budget_2023__uc_childcare_cap_increase__2026.md)
* [spring_budget_2023__uc_childcare_cap_increase__2027](packets/spring_budget_2023__uc_childcare_cap_increase__2027.md)
* [spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp__2023](packets/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp__2023.md)
* [spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp__2024](packets/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp__2024.md)
* [spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp__2025](packets/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp__2025.md)
* [spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp__2026](packets/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp__2026.md)
* [spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp__2027](packets/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp__2027.md)
* [spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp__2028](packets/spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp__2028.md)
* [spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp__2023](packets/spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp__2023.md)
* [spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp__2024](packets/spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp__2024.md)
* [spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp__2025](packets/spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp__2025.md)
* [spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp__2026](packets/spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp__2026.md)
* [spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp__2027](packets/spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp__2027.md)
* [spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp__2028](packets/spring_budget_2024__class_4_self_employed_nics_main_rate_cut_2pp__2028.md)
* [spring_budget_2024__hicbc_threshold_and_taper__2023](packets/spring_budget_2024__hicbc_threshold_and_taper__2023.md)
* [spring_budget_2024__hicbc_threshold_and_taper__2024](packets/spring_budget_2024__hicbc_threshold_and_taper__2024.md)
* [spring_budget_2024__hicbc_threshold_and_taper__2025](packets/spring_budget_2024__hicbc_threshold_and_taper__2025.md)
* [spring_budget_2024__hicbc_threshold_and_taper__2026](packets/spring_budget_2024__hicbc_threshold_and_taper__2026.md)
* [spring_budget_2024__hicbc_threshold_and_taper__2027](packets/spring_budget_2024__hicbc_threshold_and_taper__2027.md)
* [spring_budget_2024__hicbc_threshold_and_taper__2028](packets/spring_budget_2024__hicbc_threshold_and_taper__2028.md)
* [spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut__2026](packets/spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut__2026.md)
* [spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut__2027](packets/spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut__2027.md)
* [spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut__2028](packets/spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut__2028.md)
* [spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut__2029](packets/spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut__2029.md)
* [spring_statement_2025__uc_standard_allowance_above_inflation__2026](packets/spring_statement_2025__uc_standard_allowance_above_inflation__2026.md)
* [spring_statement_2025__uc_standard_allowance_above_inflation__2027](packets/spring_statement_2025__uc_standard_allowance_above_inflation__2027.md)
* [spring_statement_2025__uc_standard_allowance_above_inflation__2028](packets/spring_statement_2025__uc_standard_allowance_above_inflation__2028.md)
* [spring_statement_2025__uc_standard_allowance_above_inflation__2029](packets/spring_statement_2025__uc_standard_allowance_above_inflation__2029.md)
