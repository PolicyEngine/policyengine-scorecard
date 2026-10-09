
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
