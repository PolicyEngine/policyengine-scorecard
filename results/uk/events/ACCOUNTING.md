Whole-measure counts classify each measure once. Source-row classes independently classify each harvested head/FY cell once; a household measure can contain outside-scope rows. GBP below is by source-row class.

| Event | Whole measures | Expressible | Partial | Not expressible | Outside scope | Source rows |
|---|---:|---:|---:|---:|---:|---:|
| Autumn Budget 2024 | 74 | 0 | 5 | 43 | 26 | 1134 |
| Autumn Statement 2023 | 77 | 0 | 4 | 35 | 38 | 1116 |
| Spring Budget 2024 | 49 | 0 | 3 | 26 | 20 | 816 |
| Spring Statement 2025 | 32 | 0 | 2 | 17 | 13 | 498 |
| Spring Budget 2023 | 89 | 0 | 2 | 39 | 48 | 1020 |
| **All events** | 321 | 0 | 16 | 160 | 145 | 4584 |

| Event | Row class | Rows | Signed GBP (exact) | Absolute GBP (exact) |
|---|---|---:|---:|---:|
| Autumn Budget 2024 | `partial` | 60 | 148278589752.7765537585 | 152288337429.1413299085 |
| Autumn Budget 2024 | `not_expressible` | 438 | 42162693475.67742453810 | 71094265972.65404016440 |
| Autumn Budget 2024 | `out_of_household_scope` | 636 | -380605978576.4460772627272 | 477285058784.8563589679028 |
| Autumn Statement 2023 | `partial` | 84 | -55217430907.2756770960 | 65981700168.4486404040 |
| Autumn Statement 2023 | `not_expressible` | 318 | 15971168071.307040306245982 | 21286066210.258327469254018 |
| Autumn Statement 2023 | `out_of_household_scope` | 714 | -67493338569.05955833511087976 | 99222627549.85242051201087976 |
| Spring Budget 2024 | `partial` | 48 | -51929613884.578753403 | 58200990442.328215003 |
| Spring Budget 2024 | `not_expressible` | 276 | 9152381577.7088104666672 | 28291135439.2031551041672 |
| Spring Budget 2024 | `out_of_household_scope` | 492 | -1254963808.40385210849748 | 25416225856.97994206409948 |
| Spring Statement 2025 | `partial` | 18 | 2364990886.3596126 | 13030710886.3596126 |
| Spring Statement 2025 | `not_expressible` | 156 | 13905803182.72034823285452 | 22174211058.30566841825452 |
| Spring Statement 2025 | `out_of_household_scope` | 324 | -10695514936.054166761393 | 39773717081.089675232647 |
| Spring Budget 2023 | `partial` | 18 | -2013792939.418244905 | 2013792939.418244905 |
| Spring Budget 2023 | `not_expressible` | 324 | -22201749958.141974857379284 | 40639730627.120064076713124 |
| Spring Budget 2023 | `out_of_household_scope` | 678 | -63833979218.38919178144453 | 83758999400.68278977338967 |

| All events, by row class | Rows | Signed GBP (exact) | Absolute GBP (exact) |
|---|---:|---:|---:|
| `expressible` | 0 | 0 | 0 |
| `partial` | 228 | 41482742907.8634909545 | 291515531865.6960428205 |
| `not_expressible` | 1512 | 58990296349.271648686488418 | 183485409307.541255232788862 |
| `out_of_household_scope` | 2844 | -523883775108.35284624917308976 | 725456628673.46118655004982976 |
| **Total** | **4584** | **-423410735851.21770660818467176** | **1200457569846.69848460333869176** |

Positive signed GBP means a gain to the Exchequer. These totals cover all harvested fiscal-year cells, all source heads, zero cells and outside-scope accounts. Absolute GBP sums each cell's magnitude. Neither total is a one-year Budget costing, executable coverage amount, or numerical agreement statistic.

The review adds partial constructions for AS2023 LHA and Class 2 abolition and SB2023 UC childcare caps. Source identities and values are unchanged. The remaining 160 not-expressible measures split into 84 construction_pending and 76 model_or_data_gap; each event comparison and SUMMARY show that split. The earlier SEND-deficit and Scottish AME scope classification is retained.

Verification re-read the harvested source gzip for all five events and checked rows, exact signed/absolute GBP, and the same identities within every fiscal year. See REVIEW_FIXES.json for the complete accounting blocks and validation results.
