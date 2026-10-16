# OBR Policy measures database, March 2026

The edition was published on 26 March 2026. Both supplied Wayback captures
were fetched as original bytes using exact `id_` replay URLs and user agent
`policyengine-scorecard-research/1.0`. Collection reuses the vintage-lock
collector's sequential request pacing (at least four seconds), redirect
allowlist and retry backoff. Neither the publisher nor save-page-now was
contacted. Both downloads completed with HTTP 200 on their first attempt.

The captures `20260410184123` and `20260423164140` are byte-identical:
1,650,665 bytes, SHA-256
`1364c625a62daab8ec9b97a81ca5f93044a067fdf471e1645a62d73fdfa498f6`.
The earlier capture is the locked launch candidate. Its classification is
`unknown`: a later archive capture cannot establish first-release byte
equivalence. Workbook properties are created `2021-03-26T18:16:26Z` and
modified `2026-03-25T11:22:45Z`; the archive retains original Last-Modified
`Thu, 26 Mar 2026 11:43:38 GMT`.

`receipt.json` records both captures, HTTP attempts, properties, sheet names,
classification and canonical receipt digests. Digests exclude only the
receipt's own `receipt_sha256` and otherwise use UTF-8 JSON with sorted keys,
compact separators and `ensure_ascii=False`, as in the vintage-lock collector.

| Receipt | SHA-256 |
| --- | --- |
| Edition | `129cc10bb54dfb0d532275bf40f69a25e6dc1c6d4b783f48a124894423abf62d` |
| Earlier capture | `2de05c83332ee63e06ae884025b8ab2764f21327b25268641390f45ab6708b65` |
| Later capture | `32d7357ac68c7f1e93786c1502e82c1b0e307cde84befaf98e252d31093cfa91` |

As in the November harvest, workbook bytes stay outside the repository.
`manifest.jsonl` follows the previous harvest's artifact shape, with the
receipt binding added. `staging_accounting.json` binds the uncompressed
staged JSONL digest, workbook digest and receipt digest.

The staging port reads OOXML using the standard library. Tax cells retain
`revenue_change`; spending cells propose `exchequer_impact` with
`sign_convention=positive_gain_to_exchequer`. GBP millions are multiplied by
1e6, fiscal-year labels and original cell values are retained, and solid fill
`FFE1E9EE` excludes GDP-based extensions. Notes!D23 states the units/sign;
Notes!D11 describes the extensions; Notes!D27 states original costings.
As a parity audit, the port exactly reproduced all 24,304 November PMD staged
rows after removing the new edition/provenance metadata, and excluded the
same 48,902 extensions. The audit used retained November scratch bytes; they
are not needed for offline checks or the test suite.

The March harvest contains 24,548 original-scorecard cells: 12,857 tax and
11,691 spending. It excludes 48,902 extended cells. The uncompressed staged
SHA-256 is
`52ea1b089d7c1dc175599394b9fd3d2309b23b56c7feb4738088b4bdd4c60eb6`.

`edition_diff.json` reports every event, with changed/removed source pointers.
The exact key is event, verbatim measure title, head, table and FY. Repeated
keys retain all occurrences; equal numeric values match first, and unmatched
occurrences then pair in workbook order. November has 24,304 cells but only
24,022 unique keys, so set comparison would lose evidence.

| Partition | Cells |
| --- | ---: |
| Identical | 24,302 |
| Changed | 0 |
| New | 246 |
| Removed | 2 |
| November (identical + changed + removed) | 24,304 |
| March (identical + changed + new) | 24,548 |

All 246 new cells belong to the workbook's **Spring Forecast 2026** event.
It has **19 distinct measure titles**, represented by **41 measure/head rows**
(14 tax and 27 spending), each with six fiscal-year cells. This observation
comes from the workbook. No replay registry is created. The database adds
external source claims and their pre-measures baseline only.

The removed cells are Budget 2016, "Further government decisions", FY 2015-16:
PSCE in RDEL −£400m and PSGI in CDEL +£400m. November harvest lines 15517 and
15523 carry them; March Spending Measures!J501 and J502 are blank and unshaded.
Their November claims remain published. Budget 2016 has 680 identical and two
removed cells; the other 83 November events are fully identical.

Reproduction (use the documented shared Python test environment):

```bash
python -m scorecard_db.collect_obr_pmd --scratch-dir /tmp/obr-pmd-march-2026
python -m scorecard_db.collect_obr_pmd --check
python -m scorecard_db.stage_obr_pmd \
  --workbook /tmp/obr-pmd-march-2026/1364c625a62daab8ec9b97a81ca5f93044a067fdf471e1645a62d73fdfa498f6.workbook \
  --receipt sources/obr-pmd-march-2026/receipt.json \
  --output-dir sources/obr-pmd-march-2026
python -m scorecard_db.obr_pmd_diff \
  sources/harvest-uk-2026-08-02/uk_obr/claims_staged.jsonl.gz \
  sources/obr-pmd-march-2026/claims_staged.jsonl.gz \
  --output sources/obr-pmd-march-2026/edition_diff.json
```

Recollection records new retrieval metadata and requires deliberately
restaging and updating the pinned staged digest. With a fixed receipt and
fixed bytes, JSONL and gzip output are deterministic. Per-event counts follow.

The from-scratch database build succeeded with logical content hash
`072478d3295b22ee1f6656791722ab0146a506877a496ab0c33bea1f3f59f407`.
Export contains 29,629 claims, 5,631 initial-feed rows and 85 event archives.
All 5,631 pre-existing initial-feed rows are equal to the starting commit;
all 84 pre-existing event archives and their deployment copies are
byte-identical. The sole added archive contains 246 uncomputed claims.
Lane data remains byte-identical and build-date noise was restored. PMD
claims total 24,550, retaining the two cells absent from the March edition.
Restaging the actual locked March bytes into a separate scratch directory
reproduced gzip, manifest and staging accounting byte-for-byte.

| Event | Identical | Changed | New | Removed |
| --- | ---: | ---: | ---: | ---: |
| Autumn 2010 | 234 | 0 | 0 | 0 |
| Autumn 2011 | 228 | 0 | 0 | 0 |
| Autumn 2012 | 426 | 0 | 0 | 0 |
| Autumn 2013 | 654 | 0 | 0 | 0 |
| Autumn 2014 | 600 | 0 | 0 | 0 |
| Autumn 2015 | 336 | 0 | 0 | 0 |
| Autumn 2016 | 540 | 0 | 0 | 0 |
| Autumn Budget 2017 | 846 | 0 | 0 | 0 |
| Autumn Budget 2021 | 1080 | 0 | 0 | 0 |
| Autumn Budget 2024 | 1134 | 0 | 0 | 0 |
| Autumn Budget 2025 | 1512 | 0 | 0 | 0 |
| Autumn Statement 2022 | 1176 | 0 | 0 | 0 |
| Autumn Statement 2023 | 1116 | 0 | 0 | 0 |
| Budget 1970 | 2 | 0 | 0 | 0 |
| Budget 1971 | 6 | 0 | 0 | 0 |
| Budget 1972 | 10 | 0 | 0 | 0 |
| Budget 1973 | 4 | 0 | 0 | 0 |
| Budget 1974 | 28 | 0 | 0 | 0 |
| Budget 1975 | 16 | 0 | 0 | 0 |
| Budget 1976 | 24 | 0 | 0 | 0 |
| Budget 1977 | 20 | 0 | 0 | 0 |
| Budget 1978 | 12 | 0 | 0 | 0 |
| Budget 1979 | 30 | 0 | 0 | 0 |
| Budget 1980 | 46 | 0 | 0 | 0 |
| Budget 1981 | 28 | 0 | 0 | 0 |
| Budget 1982 | 36 | 0 | 0 | 0 |
| Budget 1983 | 26 | 0 | 0 | 0 |
| Budget 1984 | 16 | 0 | 0 | 0 |
| Budget 1985 | 14 | 0 | 0 | 0 |
| Budget 1986 | 22 | 0 | 0 | 0 |
| Budget 1987 | 28 | 0 | 0 | 0 |
| Budget 1988 | 26 | 0 | 0 | 0 |
| Budget 1989 | 26 | 0 | 0 | 0 |
| Budget 1990 | 24 | 0 | 0 | 0 |
| Budget 1991 | 32 | 0 | 0 | 0 |
| Budget 1992 | 22 | 0 | 0 | 0 |
| Budget 1993 | 60 | 0 | 0 | 0 |
| Budget 1993 #2 | 60 | 0 | 0 | 0 |
| Budget 1994 | 66 | 0 | 0 | 0 |
| Budget 1995 | 51 | 0 | 0 | 0 |
| Budget 1996 | 48 | 0 | 0 | 0 |
| Budget 1997 | 51 | 0 | 0 | 0 |
| Budget 1998 | 60 | 0 | 0 | 0 |
| Budget 1999 | 81 | 0 | 0 | 0 |
| Budget 2000 | 90 | 0 | 0 | 0 |
| Budget 2001 | 24 | 0 | 0 | 0 |
| Budget 2002 | 84 | 0 | 0 | 0 |
| Budget 2003 | 39 | 0 | 0 | 0 |
| Budget 2004 | 45 | 0 | 0 | 0 |
| Budget 2005 | 57 | 0 | 0 | 0 |
| Budget 2006 | 60 | 0 | 0 | 0 |
| Budget 2007 | 87 | 0 | 0 | 0 |
| Budget 2008 | 51 | 0 | 0 | 0 |
| Budget 2009 | 60 | 0 | 0 | 0 |
| Budget 2010 | 80 | 0 | 0 | 0 |
| Budget 2010 #2 | 330 | 0 | 0 | 0 |
| Budget 2011 | 395 | 0 | 0 | 0 |
| Budget 2012 | 420 | 0 | 0 | 0 |
| Budget 2013 | 545 | 0 | 0 | 0 |
| Budget 2014 | 505 | 0 | 0 | 0 |
| Budget 2015 | 365 | 0 | 0 | 0 |
| Budget 2015 #2 | 660 | 0 | 0 | 0 |
| Budget 2016 | 680 | 0 | 0 | 2 |
| Budget 2017 | 315 | 0 | 0 | 0 |
| Budget 2018 | 1314 | 0 | 0 | 0 |
| Budget 2020 | 1464 | 0 | 0 | 0 |
| PBR 2000 | 20 | 0 | 0 | 0 |
| PBR 2001 | 13 | 0 | 0 | 0 |
| PBR 2002 | 28 | 0 | 0 | 0 |
| PBR 2003 | 24 | 0 | 0 | 0 |
| PBR 2004 | 52 | 0 | 0 | 0 |
| PBR 2005 | 36 | 0 | 0 | 0 |
| PBR 2006 | 40 | 0 | 0 | 0 |
| PBR 2007 | 32 | 0 | 0 | 0 |
| PBR 2008 | 108 | 0 | 0 | 0 |
| PBR 2009 | 84 | 0 | 0 | 0 |
| Spending Review 2020 | 1043 | 0 | 0 | 0 |
| Spring Budget 2021 | 1020 | 0 | 0 | 0 |
| Spring Budget 2023 | 1020 | 0 | 0 | 0 |
| Spring Budget 2024 | 816 | 0 | 0 | 0 |
| Spring Forecast 2026 | 0 | 0 | 246 | 0 |
| Spring Statement 2018 | 101 | 0 | 0 | 0 |
| Spring Statement 2019 | 198 | 0 | 0 | 0 |
| Spring Statement 2022 | 642 | 0 | 0 | 0 |
| Spring Statement 2025 | 498 | 0 | 0 | 0 |
