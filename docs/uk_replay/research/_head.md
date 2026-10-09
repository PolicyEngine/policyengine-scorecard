# Vintage harvest for a vintage-faithful replay of 32 OBR-costed UK fiscal events (issue #156, track 2)

Read-only scoping, 2026-10-09. Every count below was produced by code in this task (scripts in
`/tmp/uk-replay-scope/agents/_*.py`; parsed JSON in `_hofd_full.json`, `_hofd_mx2.json`, `_pmd_years.json`).
Abbreviations: HOFD = OBR Historical official forecasts database; m25 = `Historical_official_forecasts_database_March_2025.xlsx`;
s26 = `Historical_official_forecasts_database_Spring_2026.xlsx` (both in `~/scorecard-harvest/uk_obr/downloads/`);
PMD = `Policy_measures_database_November_2025_.xlsx` (same folder). "Event vintage" = one of the 32 OBR forecasts June 2010..November 2025.

## Bottom line

* **HOFD gives an aggregate, vintage-faithful target set for all 32 events**: income tax (total, PAYE, SA), NICs, VAT, onshore CT, fuel duty, CGT, IHT, property transaction taxes, council tax, total welfare (plus inside/outside the welfare cap from December 2014), nominal GDP, and calendar-year CPI, RPI, average earnings growth, wages and salaries growth, employment level, unemployment rate, house prices and RHHDI. Every event's PMD original-scorecard costing years fall inside its vintage's fiscal-year range (32/32).
* **Missing for 29 of 32 events: anything below aggregate level.** That covers welfare by programme, NICs by class, taxpayer counts by band, non-labour income streams and population. These exist only for **Autumn Budget 2024** (receipts tables only), **Spring Statement 2025** (expenditure tables plus the ready reckoners) and **Autumn Budget 2025** (receipts, expenditure and aggregates). Only Autumn Budget 2025 has both the receipts and the expenditure tables that the current PE-UK-data calibration consumes.
* **No benefit-caseload forecast for any of the 32 vintages is in the harvest.** The only DWP caseload forecast is the Spring Forecast 2026 (consistent with the OBR's March 2026 EFO), which matches none of the 32 events. The HOFD has a claimant count only, for 15 vintages (November 2010 to March 2017).
* **No vintage earnings distribution exists for any event.** HMRC SPI and income tax liabilities data are present only as the current edition (SPI 2023-24 outturn, with projections consistent with the March 2026 EFO).

---

## 1. HOFD structure (both vintages)

### 1.1 Workbook layout
* Both files have **131 sheets** (sheet names identical; order differs, see section 2). Composition, counted:
  114 data sheets + 11 chart-helper sheets suffixed "(2)" (`£PSCR (2)`, `£TME (2)`, `PSCR (2)`, `TME (2)`, `£PSNB (2)`,
  `PSNB (2)`, `CACB (2)`, `CAPSNB (2)`, `PSND (2)`, `NGDP (2)`, `UKGDP (2)`) + `Index` (chart table) + 5 navigation
  sheets (`Contents`, `Aggregates`, `Receipts`, `Spending`, `Economy`).
* `Contents` (s26 rows 2-156) maps each tab to its full name in col AA/AB. Col D gives the first vintage per series ("Since:"). Example: D38 to D41 give income tax, SA, PAYE and NICs "June 2010", and D133 gives claimant count "November 2010".
  Contents B3 (verbatim): *"The forecasts shown in this database for fiscal aggregates, and receipts and spending
  categories reflect the definitions and classifications used at the time of each forecast and so may not be
  consistent over fiscal events."*
* **Data-sheet layout** (verified on IT, CPI, NICS, Total welfare and others): row 1 holds the title (A1 short name, B1 full title), row 2 col A
  the unit, row 4 the year header (col A "Back to contents", cols B.. = years). Then **one row per forecast
  publication, label in col A** (e.g. s26 `IT!A5`="June 2010" ... `IT!A36`="November 2025", `IT!A37`="March 2026";
  m25 `IT!A5`..`IT!A35` = June 2010..March 2025), followed by `Outturn data*` (s26 row 39 on the standard sheets) and the footnote
  "*as available at last forecast". There are no Outturn/Forecast marker rows. The earliest cells of each vintage row fall before
  the publication date (e.g. the June 2010 IT row starts at 2008-09), so they are the estimates of past years current at that time. The HOFD does not flag which
  cells are estimates and which are forecasts.
* Fiscal sheets use FY headers ("2008-09".."2030-31" in s26 cols B..X). Economy sheets use calendar years
  (2008..2030), except `Equityprices`, `Shorttermrates`, `Gilts` and `£€rate`, which use FY headers. `£PSNB` runs from 1970-71, `NGDP` from 1981-82 and
  `UKGDP` from 1982, so their June 2010 rows sit lower (s26 `£PSNB!A77`, `NGDP!A61`, `UKGDP!A59`).
* Label anomalies, found by code:
  * 14 s26 sheets store the vintage label as a datetime, not text (`PCcapex`, `Ctaxcreds`, `BBCcur`, `Lotterycur`, `Lotterycap`, `Studentloans`, `Fundedpensions`, `GGIpensions`, `Taxlit`, `GGdepreciation`, `NRcap`, `NRcur`, `R&D`, `SUME`). m25 has none. A text-only parser silently reads these sheets as empty.
  * s26 `Empl!A37` and `Govtinv!A37` read "March2026".
  * `CAPSNB!A46` reads "March 0203" in both files. It sits between November 2022 and November 2023, so it is positionally the March 2023 row.
  * The `Index` chart table labels the November 2016 row "Successive forecasts" (`Index!B20`). Its values equal `£PSNB!A91` "November 2016".
  * Footnote-suffixed labels: "November 2017†", "October 2018**", "March 2022**", "November 2022**"/"***".
  * The `(2)` chart sheets use labels like "December-20131" and "#REF!".

### 1.2 Variables (114 data sheets; s26 shown; m25 identical except the last two vintages)
Generated table follows. "Event vintages with data" counts how many of the 32 event vintages have at least one numeric cell.
