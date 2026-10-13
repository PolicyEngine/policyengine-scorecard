
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
