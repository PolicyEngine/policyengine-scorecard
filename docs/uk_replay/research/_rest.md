
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
| `uk_obr/downloads/Receipts_Detailed_forecast_tables_October_2024.xlsx` | October 2024, **Autumn Budget 2024** | **3.4** IT (PAYE, SA, company, repayments) and **NICs by class** (Class 1 employee, Class 1 employer, Class 4+2, statutory payment recoveries), FY 2023-24..2029-30. **3.5** growth of self-employed, dividend, property and savings income. **3.9** cash receipts by every tax head, 2023-24..2029-30. **3.18** taxpayers with/without threshold indexation (brought into IT, higher rate, additional rate). **3.19** actual vs counterfactual PA/HRT/ART thresholds plus CPI used. 3.13 IHT (deaths share), 3.10-3.12 APD, tobacco and alcohol volumes |
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
