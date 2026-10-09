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

| sheet | title (B1) | unit (A2) | year basis / header | event vintages with data (of 32) | first..last event vintage with data | +Mar 2026 |
|---|---|---|---|---|---|---|
| £PSNB | Public sector net borrowing (£ billion) | £ billion | FY 1970-71..2030-31 | 32 | June 2010 .. November 2025 | Y |
| PSNB | Public sector net borrowing (per cent of GDP) | per cent of GDP | FY 1976-77..2030-31 | 32 | June 2010 .. November 2025 | Y |
| £PSCR | Public sector current receipts (£ billion) | £ billion | FY 1989-90..2030-31 | 32 | June 2010 .. November 2025 | Y |
| PSCR | Public sector current receipts (per cent of GDP) | per cent of GDP | FY 1989-90..2030-31 | 32 | June 2010 .. November 2025 | Y |
| £TME | Total managed expenditure (£ billion) | £ billion | FY 1989-90..2030-31 | 32 | June 2010 .. November 2025 | Y |
| TME | Total managed expenditure (per cent of GDP) | per cent of GDP | FY 1989-90..2030-31 | 32 | June 2010 .. November 2025 | Y |
| CACB | Cyclically-adjusted current budget deficit (per cent of GDP) | per cent of GDP | FY 1997-98..2030-31 | 32 | June 2010 .. November 2025 | Y |
| CAPSNB | Cyclically-adjusted public sector net borrowing (per cent of | per cent of GDP | FY 2000-01..2030-31 | 31 | June 2010 .. November 2025 | Y |
| PSNFL | Public sector net financial liabilities (per cent of GDP) | per cent of GDP | FY 2008-09..2030-31 | 18 | November 2016 .. November 2025 | Y |
| PSND | Public sector net debt (per cent of GDP) | per cent of GDP | FY 2000-01..2030-31 | 32 | June 2010 .. November 2025 | Y |
| PSNI | Public sector net investment | Per cent of GDP | FY 2008-09..2030-31 | 32 | June 2010 .. November 2025 | Y |
| £CB | Current budget deficit | £ billion | FY 2008-09..2030-31 | 32 | June 2010 .. November 2025 | Y |
| CB | Current budget deficit | Per cent of GDP | FY 2008-09..2030-31 | 32 | June 2010 .. November 2025 | Y |
| IT | Income tax (£ billion) | £ billion | FY 2008-09..2030-31 | 32 | June 2010 .. November 2025 | Y |
| SA IT | Self assessed income tax (£ billion) | £ billion | FY 2008-09..2030-31 | 32 | June 2010 .. November 2025 | Y |
| PAYE IT | Pay as you earn (PAYE) income tax (£ billion) | £ billion | FY 2008-09..2030-31 | 32 | June 2010 .. November 2025 | Y |
| NICS | National insurance contributions (NICs) (£ billion) | £ billion | FY 2008-09..2030-31 | 32 | June 2010 .. November 2025 | Y |
| VAT | Value added tax (VAT) (£ billion) | £ billion | FY 2008-09..2030-31 | 32 | June 2010 .. November 2025 | Y |
| Onshore | Onshore corporation tax (£ billion) | £ billion | FY 2008-09..2030-31 | 32 | June 2010 .. November 2025 | Y |
| Alcohol | Alcohol duties (£ billion) | £ billion | FY 2008-09..2030-31 | 32 | June 2010 .. November 2025 | Y |
| Oilandgas | UK oil and gas revenues (£ billion) | £ billion | FY 2008-09..2030-31 | 32 | June 2010 .. November 2025 | Y |
| Fuel | Fuel duties (£ billion) | £ billion | FY 2008-09..2030-31 | 32 | June 2010 .. November 2025 | Y |
| Business | Business rates receipts (£ billion) | £ billion | FY 2008-09..2030-31 | 32 | June 2010 .. November 2025 | Y |
| CGT | Capital gains tax (£ billion) | £ billion | FY 2008-09..2030-31 | 32 | June 2010 .. November 2025 | Y |
| IHT | Inheritance tax (£ billion) | £ billion | FY 2008-09..2030-31 | 32 | June 2010 .. November 2025 | Y |
| PTT | Property transaction taxes (£ billion) | £ billion | FY 2008-09..2030-31 | 32 | June 2010 .. November 2025 | Y |
| Shares | Stamp taxes on shares (£ billion) | £ billion | FY 2008-09..2030-31 | 32 | June 2010 .. November 2025 | Y |
| Tobacco | Tobacco duties (£ billion) | £ billion | FY 2008-09..2030-31 | 32 | June 2010 .. November 2025 | Y |
| Spirits | Spirits duties (£ billion) | £ billion | FY 2008-09..2030-31 | 32 | June 2010 .. November 2025 | Y |
| Wine | Wine duties (£ billion) | £ billion | FY 2008-09..2030-31 | 32 | June 2010 .. November 2025 | Y |
| Beercider | Beer and cider duties (£ billion) | £ billion | FY 2008-09..2030-31 | 32 | June 2010 .. November 2025 | Y |
| VED | Vehicle excise duties (£ billion) | £ billion | FY 2008-09..2030-31 | 32 | June 2010 .. November 2025 | Y |
| VATrefunds | VAT refunds (£ billion) | £ billion | FY 2008-09..2030-31 | 32 | June 2010 .. November 2025 | Y |
| Council | Council tax (£ billion) | £ billion | FY 2008-09..2030-31 | 32 | June 2010 .. November 2025 | Y |
| APD | Air passenger duty (£ billion) | £ billion | FY 2008-09..2030-31 | 32 | June 2010 .. November 2025 | Y |
| IPT | Insurance premium tax (£ billion) | £ billion | FY 2008-09..2030-31 | 32 | June 2010 .. November 2025 | Y |
| CCL | Climate change levy (£ billion) | £ billion | FY 2008-09..2030-31 | 30 | March 2011 .. November 2025 | Y |
| Bank | Bank levy (£ billion) | £ billion | FY 2008-09..2030-31 | 32 | June 2010 .. November 2025 | Y |
| Licence | Licence fee receipts (£ billion) | £ billion | FY 2008-09..2030-31 | 31 | November 2010 .. November 2025 | Y |
| ETS | Emission trading scheme auction receipts (£ billion)1 | £ billion | FY 2008-09..2030-31 | 30 | March 2011 .. November 2025 | Y |
| EGL | Electricity generators levy (£ billion) | £ billion | FY 2008-09..2030-31 | 7 | November 2022 .. November 2025 | Y |
| CBAM | Carbon border adjustment mechanism (£ billion) | £ billion | FY 2008-09..2030-31 | 4 | March 2024 .. November 2025 | Y |
| Vapes | Vaping tax (£ billion) | £ billion | FY 2008-09..2030-31 | 4 | March 2024 .. November 2025 | Y |
| Scotland | Scottish taxes (£ billion) | £ billion | FY 2008-09..2030-31 | 21 | July 2015 .. November 2025 | Y |
| HSC | National insurance contributions (NICs) (£ billion) | £ billion | FY 2008-09..2028-29 | 2 | October 2021 .. March 2022 | - |
| RDEL | PSCE in RDEL (£ billion) | £ billion | FY 2008-09..2030-31 | 32 | June 2010 .. November 2025 | Y |
| CDEL | PSGI in CDEL (£ billion) | £ billion | FY 2008-09..2030-31 | 32 | June 2010 .. November 2025 | Y |
| Total welfare | Welfare spending (£ billion) | £ billion | FY 2008-09..2030-31 | 32 | June 2010 .. November 2025 | Y |
| Welfare in | Welfare spending: inside welfare cap (£ billion) | £ billion | FY 2008-09..2030-31 | 23 | December 2014 .. November 2025 | Y |
| Welfare out | Welfare spending: outside welfare cap (£ billion) | £ billion | FY 2008-09..2030-31 | 23 | December 2014 .. November 2025 | Y |
| LASFEcurr | Locally financed current expenditure (£ billion) | £ billion | FY 2008-09..2030-31 | 32 | June 2010 .. November 2025 | Y |
| LASFEcap | Locally financed capital expenditure (£ billion) | £ billion | FY 2008-09..2030-31 | 32 | June 2010 .. November 2025 | Y |
| PSDebtint | Public sector debt interest (£ billion) | £ billion | FY 2008-09..2030-31 | 32 | June 2010 .. November 2025 | Y |
| Debtint | Central government gross debt interest (£ billion) | £ billion | FY 2008-09..2030-31 | 32 | June 2010 .. November 2025 | Y |
| APF | Reductions of debt interest due to APF | £ billion | FY 2008-09..2030-31 | 23 | December 2014 .. November 2025 | Y |
| Netdebtint | Central government debt interest (net of APF) (£ billion) | £ billion | FY 2008-09..2030-31 | 32 | June 2010 .. November 2025 | Y |
| PCDebtint | Public corporations' debt interest (£ billion) | £ billion | FY 2008-09..2030-31 | 20 | November 2015 .. November 2025 | Y |
| Pensions | Unfunded public service pension payments (£ billion) | £ billion | FY 2008-09..2030-31 | 32 | June 2010 .. November 2025 | Y |
| EU | Expenditure transfers to EU institutions  (£ billion) | £ billion | FY 2008-09..2030-31 | 32 | June 2010 .. November 2025 | Y |
| PCcapex | Public corporations' capital expenditure (£ billion) | £ billion | FY 2008-09..2030-31 | 32 | June 2010 .. November 2025 | Y |
| Ctaxcreds | Company tax credits (£ billion) | £ billion | FY 2008-09..2030-31 | 32 | June 2010 .. November 2025 | Y |
| BBCcur | BBC current expenditure (£ billion) | £ billion | FY 2008-09..2030-31 | 32 | June 2010 .. November 2025 | Y |
| Lotterycur | National lottery current grants (£ billion) | £ billion | FY 2008-09..2030-31 | 32 | June 2010 .. November 2025 | Y |
| Lotterycap | National lottery capital grants (£ billion) | £ billion | FY 2008-09..2030-31 | 32 | June 2010 .. November 2025 | Y |
| Studentloans | Student loans expenditure (£ billion) | £ billion | FY 2008-09..2030-31 | 12 | March 2020 .. November 2025 | Y |
| Fundedpensions | Funded public sector pension schemes (£ billion) | £ billion | FY 2008-09..2030-31 | 12 | March 2020 .. November 2025 | Y |
| GGIpensions | General government imputed pensions (£ billion) | £ billion | FY 2008-09..2030-31 | 23 | December 2014 .. November 2025 | Y |
| Taxlit | Tax litigation (£ billion) | £ billion | FY 2008-09..2030-31 | 19 | March 2016 .. November 2025 | Y |
| GGdepreciation | General government depreciation (£ billion) | £ billion | FY 2008-09..2030-31 | 30 | March 2011 .. November 2025 | Y |
| NRcap | Network Rail capital expenditure (£ billion) | £ billion | FY 2008-09..2030-31 | 12 | December 2014 .. March 2020 | - |
| NRcur | Network Rail current expenditure (£ billion) | £ billion | FY 2008-09..2030-31 | 12 | December 2014 .. March 2020 | - |
| R&D | Research and development expenditure (£ billion) | £ billion | FY 2008-09..2021-22 | 5 | December 2014 .. March 2016 | - |
| SUME | Single use military expenditure (£ billion) | £ billion | FY 2008-09..2021-22 | 12 | March 2011 .. March 2016 | - |
| NGDP | Nominal GDP (£ billion) | £ billion | FY 1981-82..2030-31 | 32 | June 2010 .. November 2025 | Y |
| UKGDP | Real GDP growth | per cent | CY 1982..2030 | 32 | June 2010 .. November 2025 | Y |
| Outputgap | Output gap | Per cent of potential output | CY 2008..2030 | 32 | June 2010 .. November 2025 | Y |
| Demand | Domestic demand | Percentage change on a year earlier | CY 2008..2030 | 32 | June 2010 .. November 2025 | Y |
| HHconsumption | Household consumption | Percentage change on a year earlier | CY 2008..2030 | 32 | June 2010 .. November 2025 | Y |
| Govconsumption | Government consumption | Percentage change on a year earlier | CY 2008..2030 | 32 | June 2010 .. November 2025 | Y |
| Fixedinv | Total fixed investment | Percentage change on a year earlier | CY 2008..2030 | 32 | June 2010 .. November 2025 | Y |
| Businessinv | Business investment | Percentage change on a year earlier | CY 2008..2030 | 32 | June 2010 .. November 2025 | Y |
| Empl | Employment (millions) | Millions | CY 2008..2030 | 32 | June 2010 .. November 2025 | Y |
| Govtinv | General government investment | Percentage change on a year earlier | CY 2008..2030 | 32 | June 2010 .. November 2025 | Y |
| Privatedwellingsinv | Private dwellings investment | Percentage change on a year earlier | CY 2008..2030 | 32 | June 2010 .. November 2025 | Y |
| Inventories | Change in inventories | Percentage point contribution to GDP growth | CY 2008..2030 | 32 | June 2010 .. November 2025 | Y |
| Exports | Exports of goods and services | Percentage change on a year earlier | CY 2008..2030 | 32 | June 2010 .. November 2025 | Y |
| Imports | Imports of goods and services | Percentage change on a year earlier | CY 2008..2030 | 32 | June 2010 .. November 2025 | Y |
| Currentacc£ | Current account (£ billion) | £ billion | CY 2008..2030 | 32 | June 2010 .. November 2025 | Y |
| Currentacc%GDP | Current account (Per cent of GDP) | Per cent of GDP | CY 2008..2030 | 32 | June 2010 .. November 2025 | Y |
| CPI | CPI | Percentage change on a year earlier | CY 2008..2030 | 32 | June 2010 .. November 2025 | Y |
| RPI | RPI | Percentage change on a year earlier | CY 2008..2030 | 32 | June 2010 .. November 2025 | Y |
| Deflator | GDP deflator at market prices | Percentage change on a year earlier | CY 2008..2030 | 32 | June 2010 .. November 2025 | Y |
| Prod | Productivity per hour | Percentage change on a year earlier | CY 2008..2030 | 32 | June 2010 .. November 2025 | Y |
| Wages&Salaries | Wages and salaries | Percentage change on a year earlier | CY 2008..2030 | 32 | June 2010 .. November 2025 | Y |
| Earnings | Average earnings | Percentage change on a year earlier | CY 2008..2030 | 32 | June 2010 .. November 2025 | Y |
| Unemplrate | ILO unemployment rate | Percentage rate | CY 2008..2030 | 32 | June 2010 .. November 2025 | Y |
| RHHDI | Real household disposable income | Percentage change on a year earlier | CY 2008..2030 | 32 | June 2010 .. November 2025 | Y |
| Savingratio | Saving ratio | Level, per cent | CY 2008..2030 | 32 | June 2010 .. November 2025 | Y |
| Houseprices | House prices | Percentage change on a year earlier | CY 2008..2030 | 32 | June 2010 .. November 2025 | Y |
| HHnetworthtoincome | Household net worth to income ratio | Per cent | CY 2008..2030 | 32 | June 2010 .. November 2025 | Y |
| WorldGDP | World GDP at purchasing power parity | Percentage change on a year earlier | CY 2008..2030 | 32 | June 2010 .. November 2025 | Y |
| Worldtrade | World trade in goods and services | Percentage change on a year earlier | CY 2008..2030 | 31 | June 2010 .. November 2025 | Y |
| EuroGDP | Euro area GDP | Percentage change on a year earlier | CY 2008..2030 | 31 | June 2010 .. November 2025 | Y |
| UKexportmarkets | UK export markets | Percentage change on a year earlier | CY 2008..2030 | 31 | June 2010 .. November 2025 | Y |
| Non-oilPNFCprofits | Non-oil private non-financial corporation profits | Percentage change on a year earlier | CY 2008..2030 | 32 | June 2010 .. November 2025 | Y |
| Oilprices($) | Oil prices ($ per barrel) | None | CY 2008..2030 | 32 | June 2010 .. November 2025 | Y |
| Oilprices(£) | Oil prices (£ per barrel) | None | CY 2008..2030 | 31 | November 2010 .. November 2025 | Y |
| Gas Prices | Gas prices (£/therm) | None | CY 2008..2030 | 30 | March 2011 .. November 2025 | - |
| Equityprices | Equity prices | FTSE All-Share Index | FY 2008-09..2030-31 | 32 | June 2010 .. November 2025 | Y |
| Shorttermrates | Market short-term interest rates | Percentage rate | FY 2008-09..2030-31 | 32 | June 2010 .. November 2025 | Y |
| Gilts | Market gilt rates | Per cent, weighted average maturity of the gilts issued over the forecast | FY 2008-09..2030-31 | 32 | June 2010 .. November 2025 | Y |
| £€rate | Euro/Sterling exchange rate (€/£) | None | FY 2008-09..2030-31 | 31 | November 2010 .. November 2025 | Y |
| Nomconsumerspending | Nominal consumer spending | None | CY 2008..2030 | 32 | June 2010 .. November 2025 | Y |
| CC | Claimant count (millions) | Millions | CY 2008..2023 | 15 | November 2010 .. March 2017 | - |
Reading the table for calibration purposes:
* **Receipts by tax head (32 sheets)**: IT, SA IT, PAYE IT, NICS, HSC, VAT, Onshore CT, Oil and gas, Fuel,
  Business rates, CGT, IHT, PTT, Shares, Tobacco, Spirits, Wine, Beer and cider, Alcohol, VED, VAT refunds, Council tax, APD, IPT,
  CCL, Bank levy, Licence fee, ETS, EGL, CBAM, Vapes, Scottish taxes. Units: £ billion, FY.
  Coverage of the 32 event vintages: IT, PAYE, SA, NICS, VAT, Onshore, Fuel, CGT, IHT, PTT, Council and most others have 32/32.
  HSC has 2 (October 2021 and March 2022, FYs 2023-24..2026-27). Its B1 title is a copy of the NICs title, but A1 reads "Health and social care levy". `PTT!B2`: "Forecast includes SDLT, LBTT, LTT".
* **Spending**: `Total welfare` (32/32, from June 2010), `Welfare in` and `Welfare out` (inside/outside the welfare cap,
  22/32, from December 2014), and `Pensions`, which is *unfunded public service* pensions, not the state pension. **There is no
  welfare-by-programme or caseload sheet in the HOFD.** `PMD Notes!D29` records the Autumn 2014 reclassification of
  social security and tax credits into welfare inside/outside the cap.
* **Aggregates**: £PSNB, PSNB %GDP, £PSCR, PSCR, £TME, TME, CACB, CAPSNB, PSNFL (from November 2016), PSND, PSNI, £CB, CB.
  Fourteen fiscal sheets carry a `Memo: supplementary March 2020 forecast` row (e.g. s26 `£PSNB!A115`). Thirteen carry
  `Memo: restated March 2019 forecast` (e.g. s26 `£PSNB!A114`, `Studentloans!A42`), and `Studentloans` row 2 notes the new ONS
  student-loan accounting treatment from September 2019. Three carry `Memo: Restated March 2019` (PSNI, £CB, CB), and `PSNFL` has `Memo: restated March 2024 forecast`.
* **Economy (calendar year unless noted)**: NGDP (£bn, FY), UKGDP (real growth %), output gap, demand components,
  **CPI and RPI** (% y/y), GDP deflator, **Empl** (employment, millions, level), productivity, **Wages&Salaries** (% y/y),
  **Earnings** (average earnings % y/y; `Earnings` row 2: "Definition: Wages and salaries divided by employees"),
  **Unemplrate** (ILO rate, level), **CC** (claimant count, millions; row 2: "We no longer forecast the claimant
  count"; 15/32 event vintages, November 2010..March 2017, CY 2008..2023 header), RHHDI, saving ratio, **Houseprices** (% y/y;
  row 2: "From November 2016 we started forecasting the new ONS house price index"), household net worth/income,
  world GDP and trade, export markets, PNFC profits, oil and gas prices, equity prices, short rates, gilts, €/£, and
  nominal consumer spending.
* **Not in the HOFD at all**: population, households, benefit caseloads, NICs by class, income distribution or
  taxpayer counts, mixed (self-employment), property, savings or dividend income, and rents.

### 1.3 Vintage labels present
* OBR vintages (s26, 33): June 2010, November 2010, March 2011, November 2011, March 2012, December 2012, March 2013,
  December 2013, March 2014, December 2014, March 2015, July 2015, November 2015, March 2016, November 2016, March 2017,
  November 2017, March 2018, October 2018, March 2019, March 2020, November 2020, March 2021, October 2021, March 2022,
  November 2022, March 2023, November 2023, March 2024, October 2024, March 2025, November 2025, March 2026.
  m25 has the first 31, ending at March 2025.
* Pre-OBR Treasury vintages, earliest per sheet: April 1970 (£PSNB), March 1982 (NGDP), November 1983 (UKGDP), March 1990 (PSCR/TME) and others.
  The last Treasury vintage is "March 2010". It appears on 11 sheets with data, which shows that receipts by head start only at June 2010.
* Number of data sheets with values per vintage (identical in m25 and s26 for shared vintages): June 2010 88;
  November 2010 92; March 2011..March 2014 97; December 2014 and March 2015 104; July 2015 105; November 2015 106; March 2016 107;
  November 2016 106; March 2017 106; November 2017..March 2019 105; March 2020 107; November 2020 and March 2021 105;
  October 2021 106; March 2022 103; November 2022 106; March 2023 105; November 2023 106; March 2024..November 2025 108; March 2026 107.

### 1.4 Event to vintage match
**Method.** The PMD `Borrowing Summary` col B (rows 4-97) lists exactly **32 events** from "Budget 2010 #2" to "Autumn
Budget 2025", in order. `Tax Measures` and `Spending Measures` give the same 32 in the same order, and the Tax Measures event before them is "Budget 2010", preceded by "PBR 2009".
The HOFD has exactly **32 OBR vintage labels from June 2010 to November 2025**, in order. Paired one-to-one, every pair
shares its calendar year, and no event is left without a label. **No event lacks a matching vintage.** The HOFD has no other 2010-2025
vintage label (e.g. no September 2022).

**Independent checks, from files read in this task** (all others rest on order plus year):

| Event | Vintage | Evidence |
|---|---|---|
| Budget 2018 | October 2018 | `~/scorecard-harvest/uk_deductions/b2018_red.txt` lines 6-28 ("29 October 2018"). Its Table 1.1 (line 643) matches HOFD "October 2018" rows for CPI, Empl and UKGDP, 2017-2023: **21/21 values equal at 1 dp** |
| Budget 2020 | March 2020 (main row, not the supplementary memo) | `b2020_red.txt` lines 8-33 ("11 March 2020"). Its Table 1.2 (line 1027) matches HOFD "March 2020" for UKGDP, CPI, Empl, Unemplrate and Prod, 2019-2024: **30/30 equal at 1 dp** |
| Autumn Budget 2024 | October 2024 | `~/scorecard-harvest/uk_hmt/downloads/AB2024_Data_Sources.pdf` (pdftotext line ~99: OBR October 2024 EFO). `Policy_Detailed_forecast_tables_October_2024.xlsx` `2.1!C4` "Breakdown of policy decisions since March 2024" |
| Spring Statement 2025 | March 2025 | `SS2025_Data_Sources.pdf` (line ~97, OBR March 2025 EFO). HMRC `rr_bulletin_june2025.html`: "...forecasts from the OBR published on 26 March 2025, alongside the Spring Statement 2025" |
| Autumn Budget 2025 | November 2025 | `B2025_Data_Sources.pdf` (line ~101, OBR November 2025 EFO; HMT titles the event "Budget 2025") |
| Spring Budget 2024 | March 2024 | HMRC `rr_bulletin_june2025.html`: "...OBR at Spring Budget 2024 ... presented in their Economic and Fiscal Outlook for March 2024" |
| Autumn 2014 | December 2014 | Indirect only. The Uncertainty ratings DB `Introduction!B5` reads "In our December 2014 Economic and fiscal outlook, we introduced...", and its earliest event sheet is `Autumn Statement 2014` |

**Cross-checks of HOFD rows against the EFO detailed tables of the same vintage** (code, `_efo_vs_hofd*.py`):
* HOFD `IT`, `PAYE IT`, `SA IT` and `NICS` equal Receipts Table 3.4 exactly (max |diff| 0.000 over 7 FYs) for October 2024 and November 2025.
* HOFD `Fuel` and `CGT` equal Table 3.9 exactly.
* HOFD `Total welfare` equals Expenditure 4.7 "Total welfare" (March 2025, row 56) and 4.9 "Total welfare" (November 2025 row 47; March 2026 row 47) exactly.
* HOFD `VAT` differs from Table 3.9's cash-basis VAT by up to £1.98bn (October 2024) and £2.30bn (November 2025). HOFD PAYE differs from 3.9 cash PAYE by up to £3.26bn, PTT from 3.9 SDLT by up to £2.01bn, and Council from 3.9 council tax by up to £1.05bn.
  So HOFD IT, NICs and SA follow Table 3.4 (which PE-UK-data's `targets/sources/obr.py` calls the "accrued basis"). The basis of the HOFD VAT series is not stated in its sheet and is **unknown**.

### 1.5 Coverage of costing years
Computed from the PMD fill key (`Notes!C11` fill FFE1E9EE = "extended beyond original scorecard"; 12,773 tax and 11,531 spending
original-scorecard cells, matching the harvest NOTES counts).
* **32/32 events**: the vintage's fiscal-year rows cover every original costing FY.
* **31/32 events**: the calendar-year economy rows end in the calendar year the last costing FY *starts*. For Budget 2018 that means 2023 against a costing window to 2023-24. The final January-March quarter is therefore not covered by an annual CY value. Only June 2010 (CY to 2015, costing to 2014-15) is fully covered.

### 1.6 Matrix: event, vintage label, HOFD coverage and years
"Key HOFD sheets missing" is computed over 26 calibration-relevant sheets: IT, PAYE IT, SA IT, NICS, HSC, VAT, Onshore, Fuel,
CGT, IHT, PTT, Council, Total welfare, Welfare in, NGDP, UKGDP, CPI, RPI, Earnings, Wages&Salaries, Empl, Unemplrate,
CC, Houseprices, RHHDI and Nomconsumerspending. "x/y" in the economy column means sheets differ: some start one year later, e.g. for March 2021,
UKGDP, CPI and RPI start in 2020 while Earnings, Empl and Unemplrate start in 2019. All 32 vintages have all of IT, PAYE IT, SA IT, NICS, VAT, Onshore, Fuel, CGT,
IHT, PTT, Council, Total welfare, NGDP, UKGDP, CPI, RPI, Earnings, Wages&Salaries, Empl, Unemplrate, Houseprices, RHHDI and
Nomconsumerspending. The s26 row numbers are A5 (June 2010) through A36 (November 2025) on every standard sheet.

| # | event (PMD) | HOFD vintage | costing FYs (PMD original scorecard) | HOFD fiscal rows: first..last FY | HOFD economy rows: first..last CY | key HOFD sheets missing for this vintage (of 26 checked) |
|---|---|---|---|---|---|---|
| 1 | Budget 2010 #2 | June 2010 | 2010-11..2014-15 | 2008-09..2015-16 | 2009..2015 | HSC, Welfare in, CC |
| 2 | Autumn 2010 | November 2010 | 2010-11..2015-16 | 2009-10..2015-16 | 2009..2015 | HSC, Welfare in |
| 3 | Budget 2011 | March 2011 | 2011-12..2015-16 | 2009-10..2015-16 | 2009..2015 | HSC, Welfare in |
| 4 | Autumn 2011 | November 2011 | 2011-12..2016-17 | 2010-11..2016-17 | 2010..2016 | HSC, Welfare in |
| 5 | Budget 2012 | March 2012 | 2012-13..2016-17 | 2010-11..2016-17 | 2010..2016 | HSC, Welfare in |
| 6 | Autumn 2012 | December 2012 | 2012-13..2017-18 | 2011-12..2017-18 | 2011..2017 | HSC, Welfare in |
| 7 | Budget 2013 | March 2013 | 2013-14..2017-18 | 2011-12..2017-18 | 2011..2017 | HSC, Welfare in |
| 8 | Autumn 2013 | December 2013 | 2013-14..2018-19 | 2012-13..2018-19 | 2012..2018 | HSC, Welfare in |
| 9 | Budget 2014 | March 2014 | 2014-15..2018-19 | 2012-13..2018-19 | 2012..2018 | HSC, Welfare in |
| 10 | Autumn 2014 | December 2014 | 2014-15..2019-20 | 2013-14..2019-20 | 2013..2019 | HSC |
| 11 | Budget 2015 | March 2015 | 2015-16..2019-20 | 2013-14..2019-20 | 2013..2019 | HSC |
| 12 | Budget 2015 #2 | July 2015 | 2015-16..2020-21 | 2014-15..2020-21 | 2014..2020 | HSC |
| 13 | Autumn 2015 | November 2015 | 2015-16..2020-21 | 2014-15..2020-21 | 2014..2020 | HSC |
| 14 | Budget 2016 | March 2016 | 2015-16..2020-21 | 2014-15..2020-21 | 2014..2020 | HSC |
| 15 | Autumn 2016 | November 2016 | 2016-17..2021-22 | 2015-16..2021-22 | 2015..2021 | HSC |
| 16 | Budget 2017 | March 2017 | 2017-18..2021-22 | 2015-16..2021-22 | 2015..2021 | HSC |
| 17 | Autumn Budget 2017 | November 2017 | 2017-18..2022-23 | 2016-17..2022-23 | 2016..2022 | HSC, CC |
| 18 | Spring Statement 2018 | March 2018 | 2017-18..2022-23 | 2016-17..2022-23 | 2016..2022 | HSC, CC |
| 19 | Budget 2018 | October 2018 | 2018-19..2023-24 | 2017-18..2023-24 | 2017..2023 | HSC, CC |
| 20 | Spring Statement 2019 | March 2019 | 2018-19..2023-24 | 2017-18..2023-24 | 2017..2023 | HSC, CC |
| 21 | Budget 2020 | March 2020 | 2019-20..2024-25 | 2018-19..2024-25 | 2018..2024 | HSC, CC |
| 22 | Spending Review 2020 | November 2020 | 2019-20..2025-26 | 2019-20..2025-26 | 2019..2025 | HSC, CC |
| 23 | Spring Budget 2021 | March 2021 | 2020-21..2025-26 | 2019-20..2025-26 | 2019/2020..2025 | HSC, CC |
| 24 | Autumn Budget 2021 | October 2021 | 2021-22..2026-27 | 2020-21..2026-27 | 2020..2026 | CC |
| 25 | Spring Statement 2022 | March 2022 | 2021-22..2026-27 | 2020-21..2026-27 | 2020/2021..2026 | CC |
| 26 | Autumn Statement 2022 | November 2022 | 2022-23..2027-28 | 2021-22..2027-28 | 2021..2027 | HSC, CC |
| 27 | Spring Budget 2023 | March 2023 | 2022-23..2027-28 | 2021-22..2027-28 | 2021/2022..2027 | HSC, CC |
| 28 | Autumn Statement 2023 | November 2023 | 2023-24..2028-29 | 2022-23..2028-29 | 2022/2023..2028 | HSC, CC |
| 29 | Spring Budget 2024 | March 2024 | 2023-24..2028-29 | 2022-23..2028-29 | 2022/2023..2028 | HSC, CC |
| 30 | Autumn Budget 2024 | October 2024 | 2024-25..2029-30 | 2023-24..2029-30 | 2023..2029 | HSC, CC |
| 31 | Spring Statement 2025 | March 2025 | 2024-25..2029-30 | 2023-24..2029-30 | 2024..2029 | HSC, CC |
| 32 | Autumn Budget 2025 | November 2025 | 2025-26..2030-31 | 2024-25..2030-31 | 2024..2030 | HSC, CC |
## 2. Differences between the March 2025 and Spring 2026 HOFD files
Computed by `_hofd_diff.py` and `_hofd_diff2.py`:
* **Sheets**: the same 131 names, with no additions or removals. Sheet *order* changed:
  * HSC moved from after NICS to after Scotland, and Onshore/Alcohol swapped.
  * NRcap/NRcur moved from after PCcapex to after GGdepreciation.
* **Vintages added**: **November 2025** (108 data sheets with values) and **March 2026** (107). The year headers extend by one year (FY to 2030-31, CY to 2030). Titles and units are unchanged on every data sheet.
* **Historic vintage rows are frozen**: 24,913 shared forecast cells were compared and exactly **1 differs**. That cell is `Empl`, "March 2024" row, CY 2022: 32.929 in m25, blank in s26 (s26 `Empl!A33` starts at 2023).
* **Outturn rows were revised and extended**: 1,099 of 1,782 overlapping outturn cells changed (e.g. `£PSNB` 1970-71 outturn -3.947 to -0.323). Outturn was extended one year (IT, NICS, VAT and Total welfare to 2024-25; CPI to 2025). Outturn rows are "as available at last forecast", so they are not vintage targets.
* **Format regressions in s26**: 14 sheets with datetime-typed labels, plus "March2026" (`Empl`, `Govtinv`) and "#REF!" (`NGDP (2)`, `UKGDP (2)`). Parsers must normalise labels.
* **Effect on the replay**: s26 strictly supersedes m25 for the 32 events. m25 lacks only the Autumn Budget 2025 vintage.

## 3. Other harvested EFO and OBR tables: which event, and what is calibration-relevant

| File (path) | Vintage, so event | Calibration-relevant tables |
|---|---|---|
| `uk_obr/downloads/Receipts_Detailed_forecast_tables_October_2024.xlsx` | October 2024, **Autumn Budget 2024** | **3.4** IT (PAYE, SA, company, repayments) and **NICs by class** (Class 1 employee, Class 1 employer, Class 4+2, statutory payment recoveries), FY 2023-24..2029-30. **3.5** growth of self-employed, dividend, property and savings income. **3.9** cash receipts by tax head (HMRC heads, VED, business rates, council tax and others; rows 7-65), 2023-24..2029-30. **3.18** taxpayers with/without threshold indexation (brought into IT, higher rate, additional rate). **3.19** actual vs counterfactual PA/HRT/ART thresholds plus CPI used. 3.13 IHT (deaths share), 3.10-3.12 APD, tobacco and alcohol volumes |
| `.../Receipts_Detailed_forecast_tables_November_2025.xlsx` | November 2025, **Autumn Budget 2025** | Same as above, 2024-25..2030-31. **3.18** latest yield of personal-tax measures. **3.19** taxpayer counts (with/without indexation). **3.20** thresholds |
| `.../efo-march-2026-detailed-forecast-tables-receipts.xlsx` | March 2026, **none of the 32** (after Autumn Budget 2025) | Same family (3.4, 3.5, 3.8 cash receipts, 3.17-3.19) |
| `.../efo-march-2026-charts-and-tables-chapter-3.xlsx` | March 2026, none | Changes since November 2025, by head (T3.2-T3.7) |
| `.../Expenditure_Detailed_forecast_tables_March_2025.xlsx` | March 2025, **Spring Statement 2025** | **4.7** post-measures welfare by programme (housing benefit, DLA/PIP, incapacity, AA, pension credit, carer's allowance, SMP, IS, winter fuel, UC inside and outside the cap, tax credits, child benefit, tax-free childcare, state pension, JSA, NI, cost-of-living payments), FY 2023-24..2029-30. **4.9** health and disability welfare by age group. **4.1** council tax. **4.3** row 34 "Population (thousand)" FY to 2029-30. 4.16 BBC |
| `.../Expenditure_Detailed_forecast_tables_November_2025.xlsx` | November 2025, **Autumn Budget 2025** | **4.9** welfare by programme, **4.11** health and disability welfare, 4.1, 4.3 population (to 2030-31), 4.10 changes since March 2025, 4.12 UC fraud and error, 4.19 BBC |
| `.../Aggregates_Detailed_forecast_tables_November_2025.xlsx` | November 2025, Autumn Budget 2025 | Fiscal aggregates only (6.1-6.18). Not household calibration targets |
| `.../Policy_Detailed_forecast_tables_October_2024.xlsx` | October 2024, Autumn Budget 2024 | 2.1 policy decisions since March 2024, by head. These are costing targets, not population targets |
| `.../March_2025_Economic_and_fiscal_outlook_ready_reckoner.xlsx` | March 2025, **Spring Statement 2025** (Notes!D32 "consistent with the March 2025 EFO") | `Determinants` B5:AO12: FY 2022-23..2029-30 **levels** of the earnings index, mixed income (£bn), employment (000s), nominal and real consumption, house price index, property transactions, RPI/CPI indices, unemployment (millions), triple lock and others. `Receipts_RR£`: £m effect of 1% earnings or employment on PAYE and NICs, and of mixed income on SA, 2023-24..2029-30 |
| `.../Welfare-trends-report-October-2024-charts-and-tables.xlsx` | Outturn history only (0 cells match forecast/EFO/projection) | Incapacity-benefit caseloads and prevalence (e.g. C3.1 claimants 2008-09..) |
| `.../Policy_measures_database_*`, `Uncertainty_ratings_*`, `Policy_risks_*` | Costing metadata for all events | Not population targets |
| repo `sources/obr-welfare/raw/efo_march2026_detailed_expenditure.xlsx` | March 2026, none | 4.9 and 4.11 at March 2026. This is what PE-UK-data consumes today |
| repo `sources/obr-policy-effects/raw/efo_{november2023,march2024,october2024}_chapter2.xlsx` | Each EFO also carries the previous vintage's series | November 2023 file: C2.12 quarterly unemployment and **employment rates** and C2.13 nominal and real earnings growth, as columns "March 2023 forecast" and "November 2023 forecast" (verified), which covers **Spring Budget 2023 and Autumn Statement 2023**. The March 2024 and October 2024 files have same-titled charts (titles verified, columns not inspected). The **employment rate** is not in the HOFD |
| repo `.../efo_november2025_chapter3.xlsx` | November 2025, Autumn Budget 2025 | T3.2 two-child-limit costing (incl. families gaining), T3.3 threshold freeze. Costing targets |
| repo `.../efo_march2026_annex_tables.xlsx` | March 2026, none | TA.3 determinants (earnings, employment, CPI, RPI, house prices and others) |
| `uk_deductions/b2018_red.txt`, `b2020_red.txt` | Budget 2018 and Budget 2020 | Red Book tables of the OBR forecast summary. These duplicate the HOFD (verified 21/21 and 30/30 matches) |
| `uk_hmt/downloads/*Red_Book.pdf`, `*Data_Sources.pdf` | Autumn Budget 2024, Spring Statement 2025, Autumn Budget 2025 | Vintage attribution (see 1.4). `AB2024_Impact_on_households.pdf` §2.11 describes HMT IGOTM: pooled LCF 2017-18 to 2019-20, "projected forward ... using historical ASHE data on earnings growth at different points across the income distribution as well as the latest OBR average earnings and inflation forecasts ... no changes to the underlying demographics, employment levels or expenditure patterns" |

**What PE-UK-data consumes today**, for reference on what a replay needs per vintage. `/tmp/uk-replay-scope/policyengine-uk-data` is at commit 0dc9ef28.
* `targets/sources.yaml` pins `obr.vintage: "march_2026"`.
* `targets/sources/obr.py` reads:
  * receipts 3.4 for income tax and NICs by class;
  * the cash "Current receipts" sheet for NICs, VAT, fuel duties, CGT and SDLT;
  * expenditure 4.1 for council tax;
  * 4.9 for DLA+PIP, incapacity, AA, carer's allowance, SMP, winter fuel, child benefit, state pension, JSA and UC;
  * 4.19 for the TV licence.
* Other sources: HMRC SPI 2023-24, ITL and CGT; DWP Stat-Xplore; ONS population projections and households.
* The full OBR set (receipts plus expenditure tables) exists for **Autumn Budget 2025 only**. Autumn Budget 2024 has the receipts half; Spring Statement 2025 has the expenditure half.

## 4. DWP and HMRC forecast or statistics vintages in the harvests

| Artifact | Vintage basis (verified) | Matches an event? |
|---|---|---|
| DWP `uk_dwp/downloads/outturn-and-forecast-tables-spring-forecast-2026.xlsx` (benefit expenditure and caseload tables) | `Notes!B5`: "consistent with the Spring 2026 EFO ... OBR ... 3rd of March 2026". Outturn to 2024/25, forecast 2025/26..2030/31 (`Table 1a!CB3:CH3`). Expenditure by benefit (1a nominal, 1b real), **caseloads by benefit (1c, thousands, full-year average)**, by age (2a-2c), by claimant group (3a-3c), disability (4), per-benefit sheets (UC elements, UC caseload, state pension components and caseload) | **No** (March 2026). `uk_dwp/NOTES.md`: "BECL prior vintage (Autumn/2025 edition) not staged", and it is not in downloads |
| DWP take-up FYE 2024 and FYE 2023 editions; HBAI FYE 2025 and FYE 2024 editions; UC quarterly to February 2026 | Outturn statistics | No forecast vintage |
| HMRC Income Tax liabilities, July 2026 edition (`Collated_Income_Tax_liabilities_..._2.1_to_2.6.ods`) | SPI 2023-24 outturn. 2024-25..2026-27 projected, `2_1_Footnotes` row 12 note 10: "economic assumptions consistent with the OBR's March 2026 EFO". Table 2.1 taxpayers by marginal rate 1990-91..2026-27. 2.5 liabilities by income range and band, 2023-24..2026-27 | **No** (March 2026). Historic rows are current-edition outturn |
| HMRC SPI 2023-24 (`Collated_Tables_3_1_to_3_11_2324.ods`, updated April 2026) | `Table_3_1_before_tax` percentile points 1992-93..2023-24, taxpayers only | Outturn, current edition. No projections |
| HMRC Direct effects of illustrative tax changes, June 2025 (`June_2025_TRR_ODS__1_.ods` plus bulletin) | Bulletin: "updated in line with the latest ... forecasts from the OBR published on 26 March 2025, alongside the Spring Statement 2025". FY 2026-27..2028-29 (e.g. "Change basic rate by 1p" 6,900 / 8,250 / 8,200 £m) | **Spring Statement 2025** only |
| HMRC Child Benefit (August 2025), tax credits finalised awards 2022-23, CGT (August 2025) | Outturn | No forecast vintage |
| OBR ready reckoner, March 2025 (see section 3) | March 2025 EFO | **Spring Statement 2025** only |
| Repo `sources/hmrc-personal-tax/raw` and `sources/dwp-takeup/raw` | Same ITL and TRR files; DWP take-up FYE 2324 | As above |

There are **no historic DWP benefit-expenditure/caseload forecast editions, no historic SPI projections and no historic ITL editions** in any harvest.

## 5. Per-event: what the harvest provides against what a household calibration needs
Key: **P** present at the event's own vintage; **p** partial; **A** absent.
Columns:
* IT: income tax total and PAYE/SA (HOFD)
* NIC: NICs total (HOFD; plus HSC where present)
* NICcls: NICs by class (EFO 3.4)
* VAT: HOFD
* OthTax: fuel, CGT, IHT, PTT, council tax (HOFD)
* Wel: total welfare (HOFD)
* WelCap: welfare inside/outside the cap (HOFD)
* WelProg: welfare by programme (EFO 4.7 or 4.9)
* Case: benefit caseloads
* CC: claimant count (HOFD)
* Earn: average earnings and wages & salaries growth (HOFD)
* EarnDist: earnings distribution or taxpayers by band (EFO 3.18-3.20, counts with/without indexation only, so at most p)
* NonLab: self-employment, dividend, property and savings income (EFO 3.5 growth; RR mixed-income level)
* Emp: employment level and ILO unemployment rate (HOFD)
* Price: CPI and RPI (HOFD)
* HP: house prices (HOFD)
* Pop: population (EFO 4.3)
* Sens: tax or determinant sensitivities (OBR RR, HMRC TRR)

| # | Event | Vintage | IT | NIC | NICcls | VAT | OthTax | Wel | WelCap | WelProg | Case | CC | Earn | EarnDist | NonLab | Emp | Price | HP | Pop | Sens | notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Budget 2010 #2 | June 2010 | P | P | A | P | P | P | A | A | A | A | P | A | A | P | P | P | A | A | HOFD row A5; FY 2008-09..2015-16 |
| 2 | Autumn 2010 | November 2010 | P | P | A | P | P | P | A | A | A | P | P | A | A | P | P | P | A | A |  |
| 3 | Budget 2011 | March 2011 | P | P | A | P | P | P | A | A | A | P | P | A | A | P | P | P | A | A |  |
| 4 | Autumn 2011 | November 2011 | P | P | A | P | P | P | A | A | A | P | P | A | A | P | P | P | A | A |  |
| 5 | Budget 2012 | March 2012 | P | P | A | P | P | P | A | A | A | P | P | A | A | P | P | P | A | A |  |
| 6 | Autumn 2012 | December 2012 | P | P | A | P | P | P | A | A | A | P | P | A | A | P | P | P | A | A |  |
| 7 | Budget 2013 | March 2013 | P | P | A | P | P | P | A | A | A | P | P | A | A | P | P | P | A | A |  |
| 8 | Autumn 2013 | December 2013 | P | P | A | P | P | P | A | A | A | P | P | A | A | P | P | P | A | A |  |
| 9 | Budget 2014 | March 2014 | P | P | A | P | P | P | A | A | A | P | P | A | A | P | P | P | A | A |  |
| 10 | Autumn 2014 | December 2014 | P | P | A | P | P | P | P | A | A | P | P | A | A | P | P | P | A | A | first vintage with welfare in/out cap; PMD Notes D29 reclassification |
| 11 | Budget 2015 | March 2015 | P | P | A | P | P | P | P | A | A | P | P | A | A | P | P | P | A | A |  |
| 12 | Budget 2015 #2 | July 2015 | P | P | A | P | P | P | P | A | A | P | P | A | A | P | P | P | A | A |  |
| 13 | Autumn 2015 | November 2015 | P | P | A | P | P | P | P | A | A | P | P | A | A | P | P | P | A | A |  |
| 14 | Budget 2016 | March 2016 | P | P | A | P | P | P | P | A | A | P | P | A | A | P | P | P | A | A |  |
| 15 | Autumn 2016 | November 2016 | P | P | A | P | P | P | P | A | A | P | P | A | A | P | P | P | A | A |  |
| 16 | Budget 2017 | March 2017 | P | P | A | P | P | P | P | A | A | P | P | A | A | P | P | P | A | A | last vintage with claimant count |
| 17 | Autumn Budget 2017 | November 2017 | P | P | A | P | P | P | P | A | A | A | P | A | A | P | P | P | A | A |  |
| 18 | Spring Statement 2018 | March 2018 | P | P | A | P | P | P | P | A | A | A | P | A | A | P | P | P | A | A |  |
| 19 | Budget 2018 | October 2018 | P | P | A | P | P | P | P | A | A | A | P | A | A | P | P | P | A | A |  |
| 20 | Spring Statement 2019 | March 2019 | P | P | A | P | P | P | P | A | A | A | P | A | A | P | P | P | A | A | also 'Memo: restated March 2019 forecast' on 13 fiscal sheets (student-loan treatment) |
| 21 | Budget 2020 | March 2020 | P | P | A | P | P | P | P | A | A | A | P | A | A | P | P | P | A | A | use main 'March 2020' row (Red Book match 30/30); 'Memo: supplementary March 2020' exists on 14 fiscal sheets |
| 22 | Spending Review 2020 | November 2020 | P | P | A | P | P | P | P | A | A | A | P | A | A | P | P | P | A | A | B2025_Data_Sources: OBR produced no usual 'pre-measures' forecast in November 2020 |
| 23 | Spring Budget 2021 | March 2021 | P | P | A | P | P | P | P | A | A | A | P | A | A | P | P | P | A | A |  |
| 24 | Autumn Budget 2021 | October 2021 | P | P | A | P | P | P | P | A | A | A | P | A | A | P | P | P | A | A | NICS falls 182.0 to 168.1 in 2023-24 as HSC (18.3) starts, so the NICs target = NICS+HSC from 2023-24 |
| 25 | Spring Statement 2022 | March 2022 | P | P | A | P | P | P | P | A | A | A | P | A | A | P | P | P | A | A | same NICS/HSC split (179.0 to 162.0; HSC 18.4); world trade, euro GDP and export markets not updated (footnote) |
| 26 | Autumn Statement 2022 | November 2022 | P | P | A | P | P | P | P | A | A | A | P | A | A | P | P | P | A | A | market-data rows reflect fiscal-forecast conditioning (footnote) |
| 27 | Spring Budget 2023 | March 2023 | P | P | A | P | P | P | P | A | A | A | P | A | A | P | P | P | A | A | employment rate and earnings growth also in repo Nov 2023 ch2 C2.12/C2.13 ('March 2023 forecast') |
| 28 | Autumn Statement 2023 | November 2023 | P | P | A | P | P | P | P | A | A | A | P | A | A | P | P | P | A | A | employment rate and earnings also in repo Nov 2023 ch2 |
| 29 | Spring Budget 2024 | March 2024 | P | P | A | P | P | P | P | A | A | A | P | A | A | P | P | P | A | A |  |
| 30 | Autumn Budget 2024 | October 2024 | P | P | P | P | P | P | P | A | A | A | P | p | P | P | P | P | A | A | EFO Receipts Oct 2024 3.4/3.5/3.9/3.18/3.19; no Oct 2024 expenditure tables in harvest |
| 31 | Spring Statement 2025 | March 2025 | P | P | A | P | P | P | P | P | A | A | P | A | p | P | P | P | P | P | EFO Expenditure Mar 2025 4.7/4.9/4.3; RR Mar 2025; HMRC TRR June 2025; no Mar 2025 receipts tables |
| 32 | Autumn Budget 2025 | November 2025 | P | P | P | P | P | P | P | P | A | A | P | p | P | P | P | P | P | A | EFO Receipts+Expenditure+Aggregates Nov 2025; only event with the full PE-UK-data OBR table set; HOFD only in s26 |
| | **events with P (of 32)** | | 32 | 32 | 2 | 32 | 32 | 32 | 23 | 2 | 0 | 15 | 32 | 0 | 2 | 32 | 32 | 32 | 2 | 1 | |
Column totals of **P**:
* All 32 events: IT, NIC, VAT, OthTax, Wel, Earn, Emp, Price and HP.
* 23 events: WelCap (Autumn 2014 onward).
* 15 events: CC.
* 2 events: NICcls (Autumn Budget 2024 and Autumn Budget 2025), WelProg (Spring Statement 2025 and Autumn Budget 2025), NonLab (Autumn Budget 2024 and Autumn Budget 2025; Spring Statement 2025 is only p) and Pop (Spring Statement 2025 and Autumn Budget 2025).
* 1 event: Sens (Spring Statement 2025).
* No event: Case (benefit caseloads) or a full earnings distribution.

## 6. Caveats that affect target use
1. **Definitions drift across vintages** (`Contents!B3`, quoted in 1.1). Examples found:
   * the welfare-cap split from December 2014 and the reclassification of tax credits out of negative tax (`PMD Notes!D29`);
   * HSC carved out of NICs for the October 2021 and March 2022 vintages from 2023-24;
   * the student-loan accounting restatement (restated March 2019 memo rows);
   * the new ONS house price index from November 2016 (`Houseprices` row 2).
2. **Receipts, not liabilities.** HOFD IT, NICs and SA equal EFO Table 3.4, and PAYE differs from the cash table 3.9. The HOFD VAT basis is unknown. A PE replay computes liabilities, so a receipts-to-liabilities bridge is needed for every vintage. The harvest has no historical bridge.
3. **Earnings are averages only**: growth of wages and salaries divided by employees. The harvest has no vintage-specific distribution, and HMRC SPI and ITL are current-edition only.
4. **Calendar-year economy rows stop one calendar year short** of the final costing fiscal year for 31/32 events (1.5).
5. **The earliest cells in each vintage row are then-current estimates of past years**, not forecasts. The HOFD does not mark them.
6. **Parser hazards in s26**: datetime-typed labels on 14 sheets, "March2026", the "March 0203" typo, and the "Successive forecasts" label in Index.

## 7. Not in any harvest; availability unknown (not checked in this task)
* EFO detailed receipts tables (3.4 NICs by class, 3.5 non-labour income, threshold counts) for every vintage except October 2024, November 2025 and March 2026.
* EFO detailed expenditure tables (welfare by programme, population) for every vintage except March 2025, November 2025 and March 2026.
* DWP benefit expenditure and caseload tables for any edition other than Spring Forecast 2026 (`uk_dwp/NOTES.md` names the Autumn 2025 edition as unstaged).
* HMRC income tax liabilities projections and ready reckoners for any edition other than July 2026 ITL and June 2025 TRR.
* OBR ready reckoners for any vintage other than March 2025.
