# Autumn Budget 2024: FY2026–27 source-head audit

The three selected FY2026-27 OBR amounts are genuine direct policy costing head cells, with correct labels, FY and GBP-million normalization. CGT95.779m is its CGT head, not the whole main-rate/BADR/IR package: the package additionally includes income-tax, stamp-duty, Scottish-block-grant and departmental-spending cells. No source-field shift or missing duplicate selected head was found. This receipt verifies source identity and scope; it does not size behaviour or forecast-vintage effects or diagnose a PolicyEngine defect.

Workbook: [Policy_measures_database_November_2025_.xlsx](https://obr.uk/docs/dlm_uploads/Policy_measures_database_November_2025_.xlsx); SHA-256 `76fb24ac780364949e5537563a70f8fbbe30cad6c652195704ea5d72b32ea619`. In Tax Measures, the three adjacent header cells are BH3=`2025-26`, BI3=`2026-27`, BJ3=`2027-28`. The event, measure description and head are physically in columns B, C and D. These fields match the harvest independently; no column or head shift occurred. Spending Measures has its own FY columns, retained separately in the JSON receipt.

| Measure | Head | Sheet / cell | Source ordinal | Exact harvested GBP | Mapping |
|---|---|---|---:|---:|---|
| SDLT additional-home rate | Stamp duty | Tax Measures / BI2395 | 11648 | 334228735.0 | computed head |
| SDLT additional-home rate | Capital gains tax | Tax Measures / BI2396 | 11654 | -121433670.0 | uncomputed household head |
| SDLT additional-home rate | Inheritance tax | Tax Measures / BI2397 | 11660 | -66413874.00000001 | uncomputed household head |
| Employer NICs package | Income tax | Tax Measures / BI2398 | 11666 | -312921791.2621155 | computed head |
| Employer NICs package | NICs | Tax Measures / BI2399 | 11672 | 23923342053.649563 | computed head |
| Employer NICs package | Corporation tax (onshore) | Tax Measures / BI2400 | 11678 | 104302519.83016719 | outside household scope |
| CGT main rates / BADR / IR | Capital gains tax | Tax Measures / BI2401 | 11684 | 95778978.2266941 | computed head |
| CGT main rates / BADR / IR | Stamp duty | Tax Measures / BI2402 | 11690 | -65673194.77414581 | uncomputed household head |
| CGT main rates / BADR / IR | Income tax | Tax Measures / BI2403 | 11696 | 1262326238.2390866 | uncomputed household head |
| SDLT additional-home rate | Scottish BGA (current) | Spending Measures / U1708 | 22807 | 15535346.1708672 | outside household scope |
| SDLT additional-home rate | PSCE in RDEL | Spending Measures / U1709 | 22813 | 6761880.829132819 | outside household scope |
| Employer NICs package | Scottish BGA (current) | Spending Measures / U1710 | 22819 | -22555697.86413367 | outside household scope |
| Employer NICs package | PSCE in RDEL | Spending Measures / U1711 | 22825 | -2722169.4714540956 | outside household scope |
| CGT main rates / BADR / IR | Scottish BGA (current) | Spending Measures / U1712 | 22831 | 73870561.55572048 | outside household scope |
| CGT main rates / BADR / IR | PSCE in RDEL | Spending Measures / U1713 | 22837 | 5757889.723234422 | outside household scope |

The workbook cells contain numeric values, with no cell formula. The JSON receipt retains their exact OOXML strings and the exact harvested GBP decimals separately; binary floating conversion followed by multiplication by one million reproduces the harvest. Small representation differences are retained rather than silently rewriting source accounting.

| Measure | Mapped-head source subtotal GBP | Uncomputed household-head GBP | Outside-scope GBP | All-head source subtotal GBP |
|---|---:|---:|---:|---:|
| CGT main rates / BADR / IR | 95778978.2266941 | 1196653043.46494079 | 79628451.278954902 | 1372060472.970589792 |
| SDLT additional-home rate | 334228735.0 | -187847544.00000001 | 22297227.000000019 | 168678418.000000009 |
| Employer NICs package | 23610420262.3874475 | 0 | 79024652.4945794244 | 23689444914.8820269244 |

Subtotals are arithmetic over this one measure title and fiscal year; they are descriptive source subtotals, not new OBR claims or computed whole-package PolicyEngine effects.

For CGT, the tax-head subtotal is £1292432021.69163489; including the two spending accounts gives £1372060472.970589792. Only the CGT head has a numerical counterpart in the current partial construction. The Income Tax and Stamp duty cells remain uncomputed. BADR/IR qualifying-gain and rate histories are missing parameter legs within the announced package; they are not separate source heads, and this receipt cannot allocate a monetary share to them.

The source notes establish:

- Notes D19: this database contains direct policy effects and excludes indirect macroeconomic effects.
- Notes D20: measures since June2010 are disaggregated into individual tax and spending categories; the aggregate corresponds to the announcement costing.
- Notes D23: figures are GBP million; positive denotes a gain to the Exchequer.
- Notes D27: entries retain original policy costings, rather than later revisions.
- Notes D29 and D33: head categories can vary by event, and Income Tax is recorded gross of personal tax credits.

The employer-NIC Income Tax ratio compares a small direct source channel with a model channel that changes wages under the pinned employer-incidence setting. The source notes establish the direct/macro scope distinction, but do not quantify its contribution. SDLT compares the literal Stamp duty head; its behavioural and transaction-population differences remain unsized. The CGT ratio compares only the small CGT head within a package whose larger Income Tax channel is uncomputed. These facts limit interpretation of the large raw ratios.

No engine was imported or simulation run for this audit. Registry bytes were not changed. The JSON receipt retains source ids, ordinals, full descriptions, fiscal-event cells, raw numeric strings, neighboring rows and source-note text.
