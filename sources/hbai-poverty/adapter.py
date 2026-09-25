"""Adapter: DWP Households Below Average Income (HBAI) -> tidy rows.

Input:  raw/summary-hbai-1994-95-2024-25-tables.ods (headline UK series)
        raw/{population,children,workingage,pensioners}-hbai-timeseries-
        1994-95-2024-25-tables.ods (region/country breakdowns)
        (FYE 2025 publication, 2026-03-26, tables as fetched from gov.uk)
Output: data/externals/hbai-poverty.json — tidy rows in the scorecard schema.

Coverage in this build: relative/absolute low income, rate + count, BHC and
AHC, for all individuals / children / working-age adults / pensioners —
single-year UK series (summary tables 1.3-1.6) and three-year-average
region/country series (timeseries tables 3.17-3.20, 4.16/17/22/23,
5.17-5.20, 6.10/11/15/16). Material-deprivation, disability, food-security
and inequality tables are in the same raw files but not yet emitted.

Value semantics:
    - numeric cells are read from the ODS office:value attribute — the
      UNROUNDED value the workbook stores (e.g. 75.875 behind a
      displayed "75.9") — with the display text kept as a consistency
      check: the text must be the rounded rendering of the attribute,
      or the cell pairing is wrong and the run aborts (#44 follow-up:
      the adapter used to keep the rounded display text)
    - rates are percent-scale numbers -> fractions 0-1
    - counts are millions -> raw persons
    - '[x]' (not published, e.g. Northern Ireland before the FRS covered
      it), '[u]' (small sample) and '[low]' (rounds to zero at published
      precision, i.e. < 0.05 million) -> status 'suppressed'
    - summary rows are GB before 2002/03 ('FRS (GB)') and UK from 2002/03
      ('FRS (UK)'); the geography column tracks the switch
    - 'Change' rows (year-on-year deltas with [ns] significance flags) are
      derived values and are skipped
    - regional periods like '94/95-96/97' are expanded to '1994/95-1996/97'

Sheet-grammar traps (each cost real rows once; see check_completeness):
    - column A is not a row-type signal: DWP parks the series-break
      annotation next to live 2021/22 and 2022/23 data, so the year cell in
      column B decides what is a data row
    - one period header carries a stray internal space ('20/21- 22/23'),
      so period labels are whitespace-squashed before matching
"""

import json
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT_DIR = HERE.parent.parent / "data" / "externals"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SOURCE_ID = "hbai-poverty"
PROGRAM = "hbai_low_income"

TNS = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
NS = {"table": TNS, "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0"}
ONS = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
NUMERIC_TYPES = ("float", "percentage")

SUMMARY_FILE = "summary-hbai-1994-95-2024-25-tables.ods"
# sheet -> (subgroup, unit_concept, kind)
SUMMARY_TABLES = {
    "1_3a": ("total", "persons", "rate"),
    "1_3b": ("total", "persons", "count"),
    "1_4a": ("children", "children", "rate"),
    "1_4b": ("children", "children", "count"),
    "1_5a": ("working_age", "working_age_adults", "rate"),
    "1_5b": ("working_age", "working_age_adults", "count"),
    "1_6a": ("pensioners", "pensioners", "rate"),
    "1_6b": ("pensioners", "pensioners", "count"),
}

# file -> {sheet: (subgroup, unit_concept, poverty_line, kind)}
REGIONAL_FILES = {
    "population-hbai-timeseries-1994-95-2024-25-tables.ods": {
        "3_17ts": ("total", "persons", "relative", "rate"),
        "3_18ts": ("total", "persons", "relative", "count"),
        "3_19ts": ("total", "persons", "absolute", "rate"),
        "3_20ts": ("total", "persons", "absolute", "count"),
    },
    "children-hbai-timeseries-1994-95-2024-25-tables.ods": {
        "4_16ts": ("children", "children", "relative", "rate"),
        "4_17ts": ("children", "children", "relative", "count"),
        "4_22ts": ("children", "children", "absolute", "rate"),
        "4_23ts": ("children", "children", "absolute", "count"),
    },
    "workingage-hbai-timeseries-1994-95-2024-25-tables.ods": {
        "5_17ts": ("working_age", "working_age_adults", "relative", "rate"),
        "5_18ts": ("working_age", "working_age_adults", "relative", "count"),
        "5_19ts": ("working_age", "working_age_adults", "absolute", "rate"),
        "5_20ts": ("working_age", "working_age_adults", "absolute", "count"),
    },
    "pensioners-hbai-timeseries-1994-95-2024-25-tables.ods": {
        "6_10ts": ("pensioners", "pensioners", "relative", "rate"),
        "6_11ts": ("pensioners", "pensioners", "relative", "count"),
        "6_15ts": ("pensioners", "pensioners", "absolute", "rate"),
        "6_16ts": ("pensioners", "pensioners", "absolute", "count"),
    },
}

REGIONS = {
    "England",
    "North East",
    "North West",
    "Yorkshire and the Humber",
    "East Midlands",
    "West Midlands",
    "East",
    "London",
    "South East",
    "South West",
    "Wales",
    "Scotland",
    "Northern Ireland",
}

SUPPRESSED = {"[x]", "[u]", "[low]"}

YEAR_RE = re.compile(r"^\d{4}/\d{2}$")
SPAN_RE = re.compile(r"^\d{2}/\d{2}-\d{2}/\d{2}$")


def metric_name(poverty_line, kind):
    return f"{poverty_line}_low_income_{kind}"


class Cell(str):
    """A sheet cell: the display text (str identity, so every label and
    regex read stays unchanged) carrying the workbook's UNROUNDED
    office:value when the cell is numeric. num is (value, value_type)
    or None for label/empty cells."""

    __slots__ = ("num",)

    def __new__(cls, text, num=None):
        cell = super().__new__(cls, text)
        cell.num = num
        return cell


def read_sheets(path, wanted):
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read("content.xml"))
    out = {}
    for t in root.findall(".//table:table", NS):
        name = t.get(f"{{{TNS}}}name")
        if name not in wanted:
            continue
        rows = []
        for r in t.findall("table:table-row", NS):
            row = []
            for c in r.findall("table:table-cell", NS):
                rep = int(c.get(f"{{{TNS}}}number-columns-repeated", "1"))
                txt = " ".join(
                    "".join(p.itertext()) for p in c.findall("text:p", NS)
                ).strip()
                vt = c.get(f"{{{ONS}}}value-type")
                v = c.get(f"{{{ONS}}}value")
                num = (float(v), vt) if v is not None and vt in NUMERIC_TYPES else None
                row.extend([Cell(txt, num)] * min(rep, 40))
            while row and not row[-1]:
                row.pop()
            rows.append(row)
        out[name] = rows
    missing = set(wanted) - set(out)
    if missing:
        raise ValueError(f"{path}: sheets not found: {sorted(missing)}")
    return out


def parse_value(cell, kind):
    if cell in SUPPRESSED:
        return None, "suppressed"
    if not cell or not re.match(r"^-?[\d,.]+$", cell):
        return None, "empty"
    shown = float(cell.replace(",", ""))
    num = getattr(cell, "num", None)
    if num is None:
        v = shown
    else:
        v, vtype = num
        if vtype == "percentage":
            # ODS percentage cells store the fraction; the sheet displays
            # the percent-scale number — align to display scale so ONE
            # kind conversion below applies to both cell types.
            v *= 100
        # The display text must be the rounded rendering of the stored
        # value at the text's own precision; a mismatch means text and
        # attribute came from different cells — abort, never emit.
        dp = len(cell.split(".")[1]) if "." in cell else 0
        if abs(v - shown) > 0.5 * 10**-dp + 1e-9:
            raise ValueError(
                f"cell text {str(cell)!r} is not the rounded rendering "
                f"of its office:value {v!r}"
            )
    return (v / 100 if kind == "rate" else v * 1_000_000), "ok"


def squash_ws(text):
    """Drop whitespace inside a period label.

    DWP leaves a stray space in one pensioner-table period header
    ('20/21- 22/23' in 6_10ts/6_11ts/6_15ts/6_16ts). These labels have no
    legitimate internal whitespace, so squashing it is safe and keeps the
    match strict about everything else.
    """
    return re.sub(r"\s+", "", text)


def expand_span(span):
    """'94/95-96/97' -> '1994/95-1996/97' (century split at 94)."""
    span = squash_ws(span)

    def expand_pair(pair):
        a, b = pair.split("/")
        century = "19" if int(a) >= 94 else "20"
        return f"{century}{a}/{b}"

    lo, hi = span.split("-")
    return f"{expand_pair(lo)}-{expand_pair(hi)}"


def emit(
    rows,
    metric,
    subgroup,
    variant,
    geography,
    unit_concept,
    period,
    value,
    status,
    source_column,
):
    rows.append(
        {
            "source": SOURCE_ID,
            "country": "UK",
            "program": PROGRAM,
            "metric": metric,
            "subgroup": subgroup,
            "variant": variant,
            "geography": geography,
            "unit_concept": unit_concept,
            "period": period,
            "value": value,
            "status": status,
            "source_column": source_column,
        }
    )


def parse_summary_sheet(sheet, rows, subgroup, unit_concept, kind, out):
    # Measure columns: exactly rel/abs BHC then rel/abs AHC, in that order
    # (the merged BHC/AHC caption sits offset from its first data column, so
    # positional pairing is the reliable read).
    line_row = next(r for r in rows if "Relative low income" in r)
    measure_cols = [
        (i, "relative" if label.startswith("Relative") else "absolute")
        for i, label in enumerate(line_row)
        if label in ("Relative low income", "Absolute low income")
    ]
    if [line for _, line in measure_cols] != [
        "relative",
        "absolute",
        "relative",
        "absolute",
    ]:
        raise ValueError(f"{sheet}: unexpected measure columns: {measure_cols}")
    cols = [
        (i, line, "bhc" if n < 2 else "ahc") for n, (i, line) in enumerate(measure_cols)
    ]

    geography = None
    for row in rows:
        first = row[0] if row else ""
        if first == "FRS (GB)":
            geography = "GB"
        elif first == "FRS (UK)":
            geography = "UK"
        elif first == "Change":
            continue
        # Column A is NOT a reliable row-type signal: DWP puts series-break
        # annotations ('Admin-linked benefits data from 2021/22', 'See Note 1')
        # in column A alongside live 2021/22 and 2022/23 data. The year cell in
        # column B is what distinguishes a data row -- prose and header rows
        # never carry a bare YYYY/YY there, and the 'Change' row's column B is
        # a span ('2023/24-2024/25'), excluded both by name above and by shape.
        year = row[1] if len(row) > 1 else ""
        if not YEAR_RE.match(year):
            continue
        if geography is None:
            raise ValueError(f"{sheet}: data row before FRS scope marker: {year}")
        for i, line, variant in cols:
            text = row[i] if i < len(row) else ""
            value, status = parse_value(text, kind)
            if status == "empty":
                raise ValueError(f"{sheet} {year} col {i}: unparsed cell {text!r}")
            emit(
                out,
                metric_name(line, kind),
                subgroup,
                variant,
                geography,
                unit_concept,
                year,
                value,
                "suppressed" if value is None else "ok",
                f"{sheet}:col{i}",
            )


def parse_regional_sheet(sheet, rows, subgroup, unit_concept, line, kind, out):
    period_row = next(
        r for r in rows if sum(bool(SPAN_RE.match(squash_ws(c))) for c in r) > 5
    )
    periods = {
        i: expand_span(c)
        for i, c in enumerate(period_row)
        if SPAN_RE.match(squash_ws(c))
    }
    variant = None
    for row in rows:
        first = row[0] if row else ""
        if first.lower() == "before housing costs":
            variant = "bhc"
            continue
        if first.lower() == "after housing costs":
            variant = "ahc"
            continue
        if first not in REGIONS:
            continue
        if variant is None:
            raise ValueError(f"{sheet}: region row before BHC/AHC marker: {first}")
        for i, period in periods.items():
            text = row[i] if i < len(row) else ""
            value, status = parse_value(text, kind)
            if status == "empty":
                raise ValueError(f"{sheet} {first} {period}: unparsed cell {text!r}")
            emit(
                out,
                metric_name(line, kind),
                subgroup,
                variant,
                first,
                unit_concept,
                period,
                value,
                "suppressed" if value is None else "ok",
                f"{sheet}:{first}",
            )


def next_fiscal_year(year):
    """'2002/03' -> '2003/04'."""
    start = int(year[:4])
    return f"{start + 1}/{(start + 2) % 100:02d}"


def check_completeness(rows):
    """Fail loud if any series lost rows.

    The inline headline checks below only touch hand-picked cells, so they
    cannot see a whole year or period column going missing (both of which
    happened: a series-break annotation in column A dropped 2021/22-2022/23,
    and a stray space in a period header dropped 20/21-22/23 from the
    pensioner regional tables). These assertions are structural: they hold
    for any future vintage and break the run rather than emit a gapped series.
    """
    single, regional = {}, {}
    for r in rows:
        key = (r["metric"], r["subgroup"], r["variant"])
        if r["geography"] in ("GB", "UK"):
            single.setdefault(key, {}).setdefault(r["geography"], set()).add(
                r["period"]
            )
        else:
            regional.setdefault(key, {}).setdefault(r["geography"], set()).add(
                r["period"]
            )

    if not single or not regional:
        raise ValueError("completeness: no rows emitted")

    # 1. UK/GB single-year series: one unbroken fiscal-year run per series,
    #    GB handing over to UK with no gap and no overlap.
    spans = set()
    for key, by_geo in sorted(single.items()):
        if set(by_geo) != {"GB", "UK"}:
            raise ValueError(f"completeness: {key} geographies {sorted(by_geo)}")
        years = sorted(by_geo["GB"] | by_geo["UK"])
        for prev, nxt in zip(years, years[1:]):
            if next_fiscal_year(prev) != nxt:
                raise ValueError(f"completeness: {key} gap {prev} -> {nxt}")
        if max(by_geo["GB"]) >= min(by_geo["UK"]):
            raise ValueError(f"completeness: {key} GB/UK scope overlap")
        spans.add((years[0], years[-1], min(by_geo["UK"])))
    if len(spans) != 1:
        raise ValueError(f"completeness: single-year spans differ: {sorted(spans)}")

    # 2. Regional tables: identical period sets across every age group,
    #    geography and variant (this is exactly what the dropped period
    #    column broke -- pensioners had 28 periods where children had 29).
    period_sets = {
        (key, geo): frozenset(periods)
        for key, by_geo in regional.items()
        for geo, periods in by_geo.items()
    }
    if len(set(period_sets.values())) != 1:
        example = {}  # one representative table per distinct period set
        for (key, geo), periods in sorted(period_sets.items()):
            example.setdefault(periods, (key, geo, len(periods)))
        raise ValueError(
            "completeness: regional period sets differ: "
            + "; ".join(f"{k}/{g}: {n} periods" for k, g, n in example.values())
        )
    for key, by_geo in sorted(regional.items()):
        if set(by_geo) != REGIONS:
            raise ValueError(
                f"completeness: {key} missing geographies "
                f"{sorted(REGIONS - set(by_geo))}"
            )
    for key in regional:
        if (key[0], key[1], "bhc" if key[2] == "ahc" else "ahc") not in regional:
            raise ValueError(f"completeness: {key} has no BHC/AHC counterpart")


def run():
    rows = []
    sheets = read_sheets(HERE / "raw" / SUMMARY_FILE, SUMMARY_TABLES)
    for sheet, (subgroup, unit_concept, kind) in SUMMARY_TABLES.items():
        parse_summary_sheet(sheet, sheets[sheet], subgroup, unit_concept, kind, rows)
    for fname, tables in REGIONAL_FILES.items():
        sheets = read_sheets(HERE / "raw" / fname, tables)
        for sheet, (subgroup, unit_concept, line, kind) in tables.items():
            parse_regional_sheet(
                sheet, sheets[sheet], subgroup, unit_concept, line, kind, rows
            )

    check_completeness(rows)

    out = OUT_DIR / f"{SOURCE_ID}.json"
    out.write_text(json.dumps(rows))
    print(f"{len(rows)} rows -> {out}")

    # --- validation against the FYE 2025 publication's headline figures ---
    def get(metric, subgroup="total", variant="bhc", geography="UK", period="2024/25"):
        for r in rows:
            if (
                r["metric"] == metric
                and r["subgroup"] == subgroup
                and r["variant"] == variant
                and r["geography"] == geography
                and r["period"] == period
            ):
                return r["value"]
        raise KeyError((metric, subgroup, variant, geography, period))

    checks = [
        ("individuals rel BHC 16%", get("relative_low_income_rate"), 0.16),
        (
            "individuals rel AHC 20%",
            get("relative_low_income_rate", variant="ahc"),
            0.20,
        ),
        ("individuals abs BHC 16%", get("absolute_low_income_rate"), 0.16),
        (
            "individuals abs AHC 20%",
            get("absolute_low_income_rate", variant="ahc"),
            0.20,
        ),
        ("individuals rel BHC 10.9M", get("relative_low_income_count"), 10_900_000),
        (
            "individuals rel AHC 13.4M",
            get("relative_low_income_count", variant="ahc"),
            13_400_000,
        ),
        (
            "children rel BHC 21%",
            get("relative_low_income_rate", subgroup="children"),
            0.21,
        ),
        (
            "children rel AHC 27%",
            get("relative_low_income_rate", subgroup="children", variant="ahc"),
            0.27,
        ),
        (
            "working-age rel AHC 19%",
            get("relative_low_income_rate", subgroup="working_age", variant="ahc"),
            0.19,
        ),
        (
            "pensioners rel BHC 16%",
            get("relative_low_income_rate", subgroup="pensioners"),
            0.16,
        ),
        (
            "pensioners rel AHC 14%",
            get("relative_low_income_rate", subgroup="pensioners", variant="ahc"),
            0.14,
        ),
        (
            "GB series starts 1994/95 at 19%",
            get("relative_low_income_rate", geography="GB", period="1994/95"),
            0.19,
        ),
        (
            "England rel BHC 94/95-96/97 18%",
            get(
                "relative_low_income_rate",
                geography="England",
                period="1994/95-1996/97",
            ),
            0.18,
        ),
    ]
    failed = False
    for label, got, want in checks:
        # got carries the office:value precision; the publication's
        # headline is its rounded rendering (rates to whole percents,
        # counts to 0.1 million) — so validate rounds-to, not equality.
        if got is None:
            ok = False
        elif want < 1:  # rate fraction
            ok = abs(round(got, 2) - want) < 1e-9
        else:  # person count, published to 0.1M
            ok = abs(round(got / 100_000) * 100_000 - want) < 1e-6
        print(f"  {'OK ' if ok else 'FAIL'} {label}: {got}")
        failed = failed or not ok
    suppressed = sum(r["status"] == "suppressed" for r in rows)
    print(f"  suppressed cells: {suppressed}")
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    run()
