"""Adapter: OBR published economic effects of policy -> tidy rows (#55).

The external side of the Macro entry point: OBR's published estimates of
what fiscal policy DOES to the economy — package effects on real GDP and
CPI, per-measure supply-side impacts on potential output, and the
direct/indirect split of the decisions' effect on borrowing. These are
the claims the PolicyEngine Macro members (OBR emulator, OG-UK, PE-UK
LSR) will later answer; this build emits the external side only.

Inputs (raw/, all Wayback original bytes — obr.uk is Cloudflare-guarded;
URLs, snapshot timestamps and SHA-256 per file in raw/README.md):

  efo_november2023_chapter2.xlsx   C2.A  AS2023 package: real GDP impacts
                                          by channel (full expensing,
                                          NICs cut, welfare reforms,
                                          demand, total)
  efo_march2024_chapter2.xlsx      C2.A  SB2024 package: real GDP impacts
                                          by channel
  efo_october2024_chapter2.xlsx    C2.A  AB2024 package: real GDP impacts
                                          by expenditure component
                                   C2.B  AB2024 package: real GDP impacts
                                          by measure/channel
  efo_november2025_chapter3.xlsx   C3.3  AB2025 package: real GDP impacts
                                          by expenditure component
                                   C3.4  AB2025 package: CPI inflation
                                          impacts by measure
  efo_march2026_annex_tables.xlsx  TB.1  March 2026: total effect of
                                          Government decisions on
                                          borrowing, direct/indirect
                                          split, GBP bn (nested)
  obr_briefing_paper_10_supply_side.xlsx
                                   T2.1  Briefing paper No.10 (Nov 2025):
                                          every policy measure with a
                                          supply-side effect in the OBR
                                          forecast, per-measure impact on
                                          potential output (% of GDP) by
                                          channel, March 2023 -> March
                                          2025 fiscal events

Output: data/externals/obr-policy-effects.json — tidy rows.

Value semantics:
    - GDP/CPI chart data and supply-side impacts are PER CENT at full
      float precision (0.26 means 0.26 per cent) -> unit 'percent'
    - TB.1 amounts are GBP BILLION -> raw GBP ('gbp_nominal'); the
      published sign convention is carried verbatim in the row's
      'sign_convention' (positive = increases borrowing, per the table
      note) — NOT normalised here
    - periods are financial years '2023-24'.. as published; briefing
      paper supply-side impacts carry period 'forecast_horizon' (the
      table publishes one number per measure, not a path)

Every row records fiscal_event, basis ('post_behavioural' for package
effects — OBR publishes the post-adjustment path; 'supply_side' for the
briefing-paper channel scorings), scope ('package', 'measure' or
'component'), and source_column (sheet:series verbatim). Titles are
anchored: a sheet whose title cell does not start with the expected
published prefix is a hard error, so a silently re-shuffled workbook
cannot emit rows under the wrong label. TB.1 carries the same
aggregate_level/parent hierarchy convention as the obr-welfare adapter
so no consumer can double-count the nested 'of which' rows.
"""

import hashlib
import json
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
OUT_DIR = HERE.parent.parent / "data" / "externals"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SOURCE_ID = "obr-policy-effects"

MNS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
RNS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"

# file -> sha256 of the exact bytes this adapter was written against.
# A drifted raw file is a hard error, never a silently different parse.
SHA256 = {
    "efo_november2023_chapter2.xlsx": (
        "4b4b8092c1bf3e2cb84d7e6c16efcf122eec528cc5b1a40d599d3d2c89be3bdf"
    ),
    "efo_march2024_chapter2.xlsx": (
        "b3bec6bc914efed2b5a7245f2f705ec82d722467c32f2057682a212c1d793e1a"
    ),
    "efo_october2024_chapter2.xlsx": (
        "9d402b235e1d8d7b469c136b13035d120eb6ea089b489a7cbe5bff7cac905a3b"
    ),
    "efo_november2025_chapter3.xlsx": (
        "bb84ae66ad1e867af4c751b915b3e8d59c83146f7c6b3f9f92fc8fc7699fe3d8"
    ),
    "efo_march2026_annex_tables.xlsx": (
        "58a0c59cac93651a477f2c097b0f99b1dbcee417e9b54e0be3c6f92294ba0ad8"
    ),
    "obr_briefing_paper_10_supply_side.xlsx": (
        "8ca1af0be01762edc75a4c3c9fde1e455732068b0140483cd1ffde2c4b11843f"
    ),
}


def _grid(path, sheet_name):
    """Sheet -> {(row, col): value} with shared strings resolved."""
    z = zipfile.ZipFile(path)
    try:
        ss = [
            "".join(t.text or "" for t in si.iter(MNS + "t"))
            for si in ET.fromstring(z.read("xl/sharedStrings.xml")).iter(MNS + "si")
        ]
    except KeyError:
        ss = []
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    rid = {r.get("Id"): r.get("Target") for r in rels}
    for s in wb.iter(MNS + "sheet"):
        if s.get("name").strip() != sheet_name:
            continue
        root = ET.fromstring(z.read("xl/" + rid[s.get(RNS + "id")].lstrip("/")))
        grid = {}
        for row in root.iter(MNS + "row"):
            for c in row.iter(MNS + "c"):
                v = c.find(MNS + "v")
                if v is None:
                    continue
                ref = c.get("r")
                m = re.match(r"([A-Z]+)(\d+)", ref)
                col = 0
                for ch in m.group(1):
                    col = col * 26 + (ord(ch) - 64)
                val = ss[int(v.text)] if c.get("t") == "s" else v.text
                grid[(int(m.group(2)), col)] = val
        return grid
    raise KeyError(f"{path.name}: no sheet {sheet_name!r}")


def _check_sha(fname):
    digest = hashlib.sha256((RAW / fname).read_bytes()).hexdigest()
    if digest != SHA256[fname]:
        raise RuntimeError(
            f"{fname}: sha256 {digest} != pinned {SHA256[fname]} — raw file "
            "drifted from the bytes this adapter was written against"
        )


def _title(grid, expect_prefix, cell=(2, 2)):
    got = str(grid.get(cell, "")).strip()
    if not got.startswith(expect_prefix):
        raise RuntimeError(f"title anchor failed: {got!r} !~ {expect_prefix!r}")
    return got


def _slug(label):
    s = re.sub(r"[^a-z0-9]+", "_", str(label).strip().lower()).strip("_")
    return s


def _num(v):
    return float(v)


FY = re.compile(r"^\d{4}-\d{2}$")


def _chart_series_rows(grid, header_row=25):
    """OBR chart-data layout: header row 25, data rows below, col B is
    the row key. Returns (headers {col: label}, data rows list)."""
    headers = {
        c: str(v).strip() for (r, c), v in grid.items() if r == header_row and c >= 2
    }
    rows = sorted(
        {r for (r, c) in grid if r > header_row and (r, 2) in grid and c >= 2}
    )
    return headers, rows


def parse_gdp_chart(fname, sheet, title_prefix, fiscal_event, orient, out):
    """Package GDP-impact chart data.

    orient='years_down': col B holds FYs, header row holds series
    (Nov 2023 / Mar 2024 layout). orient='series_down': col B holds
    series, header row holds FYs (Oct 2024 / Nov 2025 layout).
    """
    grid = _grid(RAW / fname, sheet)
    _title(grid, title_prefix)
    headers, rows = _chart_series_rows(grid)
    n = 0
    for r in rows:
        key = str(grid[(r, 2)]).strip()
        for c, label in sorted(headers.items()):
            if c == 2 or (r, c) not in grid:
                continue
            if orient == "years_down":
                period, series = key, label
            else:
                period, series = label, key
            if not FY.match(period.strip()):
                raise RuntimeError(f"{fname}:{sheet}: not a FY: {period!r}")
            total = series.strip().lower() in (
                "total effect",
                "total",
                "change in real gdp",
                "gdp",
            )
            out.append(
                {
                    "source": SOURCE_ID,
                    "country": "UK",
                    "program": "policy_package",
                    "metric": "gdp_level_effect",
                    "subgroup": "total" if total else _slug(series),
                    "variant": None,
                    "geography": "UK",
                    "unit_concept": "percent",
                    "period": period.strip(),
                    "value": _num(grid[(r, c)]),
                    "status": "ok",
                    "fiscal_event": fiscal_event,
                    "basis": "post_behavioural",
                    "scope": "package",
                    "aggregate_level": "total" if total else "component",
                    "parent": None if total else "policy_package",
                    "source_column": f"{sheet}:{series.strip()}",
                }
            )
            n += 1
    return n


def parse_cpi_chart(fname, sheet, title_prefix, fiscal_event, out):
    """AB2025 CPI-impact chart: years down col B, measures across."""
    grid = _grid(RAW / fname, sheet)
    _title(grid, title_prefix)
    headers, rows = _chart_series_rows(grid)
    n = 0
    for r in rows:
        period = str(grid[(r, 2)]).strip()
        if not FY.match(period):
            raise RuntimeError(f"{fname}:{sheet}: not a FY: {period!r}")
        for c, series in sorted(headers.items()):
            if c == 2 or (r, c) not in grid:
                continue
            total = series.strip().lower() == "total"
            out.append(
                {
                    "source": SOURCE_ID,
                    "country": "UK",
                    "program": "policy_package",
                    "metric": "cpi_inflation_effect",
                    "subgroup": "total" if total else _slug(series),
                    "variant": None,
                    "geography": "UK",
                    "unit_concept": "percent",
                    "period": period,
                    "value": _num(grid[(r, c)]),
                    "status": "ok",
                    "fiscal_event": fiscal_event,
                    "basis": "post_behavioural",
                    "scope": "package",
                    "aggregate_level": "total" if total else "component",
                    "parent": None if total else "policy_package",
                    "source_column": f"{sheet}:{series.strip()}",
                }
            )
            n += 1
    return n


# Fiscal-event section headers exactly as printed in briefing paper T2.1.
BP10_EVENTS = {
    "March 2023": "spring_budget_2023",
    "November 2023": "autumn_statement_2023",
    "March 2024": "spring_budget_2024",
    "October 2024": "autumn_budget_2024",
    "March 2025": "spring_statement_2025",
}


def parse_bp10_supply_side(fname, sheet, out):
    """Briefing paper No.10 Table 2.1: per-measure supply-side impact on
    potential output (% of GDP), grouped under fiscal-event header rows.
    Columns: B measure, C description, E type, F channel, G impact
    (column D is absorbed by a merge in the published workbook)."""
    grid = _grid(RAW / fname, sheet)
    _title(grid, "Table 2.1: Policy measures with supply")
    event = None
    n = 0
    rows = sorted({r for (r, c) in grid if c == 2 and r > 2})
    for r in rows:
        label = str(grid[(r, 2)]).strip()
        if label in BP10_EVENTS:
            event = BP10_EVENTS[label]
            continue
        if label == "Policy measure" or (r, 7) not in grid:
            continue  # column-header / note / blank rows
        if event is None:
            raise RuntimeError(f"BP10 T2.1: measure {label!r} before any event header")
        out.append(
            {
                "source": SOURCE_ID,
                "country": "UK",
                "program": _slug(label),
                "metric": "supply_side_impact",
                "subgroup": _slug(grid[(r, 6)]),  # channel: labour/capital/tfp
                "variant": _slug(grid[(r, 5)]),  # type: tax/welfare/del/regulation
                "geography": "UK",
                "unit_concept": "percent",
                "period": "forecast_horizon",
                "value": _num(grid[(r, 7)]),
                "status": "ok",
                "fiscal_event": event,
                "basis": "supply_side",
                "scope": "measure",
                "aggregate_level": "component",
                "parent": None,
                "source_column": f"{sheet}:{label}",
                "description": str(grid.get((r, 3), "")).strip(),
            }
        )
        n += 1
    return n


# TB.1 nested rows, exactly as printed: (label prefix, slug, level, parent).
TB1_ROWS = [
    ("Total effect of Government decisions", "total_effect", "total", None),
    (
        "Direct effects of Government decisions",
        "direct_effects",
        "subtotal",
        "total_effect",
    ),
    ("Spending measures", "spending_measures", "subtotal", "direct_effects"),
    (
        "Additional departmental spending",
        "additional_departmental_spending",
        "component",
        "spending_measures",
    ),
    (
        "Local authority support measures",
        "local_authority_support",
        "component",
        "spending_measures",
    ),
    (
        "Other spending measures",
        "other_spending_measures",
        "component",
        "spending_measures",
    ),
    ("Tax measures", "tax_measures", "subtotal", "direct_effects"),
    ("Reforms to Pillar 2", "pillar_2_reforms", "component", "tax_measures"),
    ("Other tax measures", "other_tax_measures", "component", "tax_measures"),
    (
        "Indirect effects of Government decisio",
        "indirect_effects",
        "subtotal",
        "total_effect",
    ),
]


def parse_tb1_decisions(fname, sheet, out):
    """March 2026 Table B.1: effect of Government decisions since the
    November 2025 Budget on borrowing, GBP bn, direct/indirect split."""
    grid = _grid(RAW / fname, sheet)
    _title(grid, "Table B.1: Total effect of Government")
    # header row: financial years
    hdr_row = min(r for (r, c), v in grid.items() if FY.match(str(v).strip() or "x"))
    periods = {
        c: str(v).strip()
        for (r, c), v in grid.items()
        if r == hdr_row and FY.match(str(v).strip())
    }
    labels = {r: str(grid[(r, 2)]).strip() for (r, c) in grid if c == 2 and r > hdr_row}
    matched = set()
    n = 0
    for r, label in sorted(labels.items()):
        hit = next(
            (t for t in TB1_ROWS if label.startswith(t[0]) and t[1] not in matched),
            None,
        )
        if hit is None:
            continue
        prefix, slug, level, parent = hit
        matched.add(slug)
        for c, period in sorted(periods.items()):
            if (r, c) not in grid:
                continue
            out.append(
                {
                    "source": SOURCE_ID,
                    "country": "UK",
                    "program": slug,
                    "metric": "decisions_effect_on_borrowing",
                    "subgroup": "total",
                    "variant": None,
                    "geography": "UK",
                    "unit_concept": "gbp_nominal",
                    "period": period,
                    "value": _num(grid[(r, c)]) * 1e9,
                    "status": "ok",
                    "fiscal_event": "march_2026_efo",
                    "basis": "post_behavioural",
                    "scope": "package",
                    "sign_convention": "as_published_positive_increases",
                    "aggregate_level": level,
                    "parent": parent,
                    "source_column": f"{sheet}:{label}",
                }
            )
            n += 1
    missing = {t[1] for t in TB1_ROWS} - matched
    if missing:
        raise RuntimeError(f"TB.1: rows not found: {sorted(missing)}")
    return n


def build():
    for fname in SHA256:
        _check_sha(fname)
    rows = []
    counts = {
        "as2023_gdp": parse_gdp_chart(
            "efo_november2023_chapter2.xlsx",
            "C2.A",
            "Chart 2.A: Real GDP impacts",
            "autumn_statement_2023",
            "years_down",
            rows,
        ),
        "sb2024_gdp": parse_gdp_chart(
            "efo_march2024_chapter2.xlsx",
            "C2.A",
            "Chart 2.A: Impact of policy measures on real GDP",
            "spring_budget_2024",
            "years_down",
            rows,
        ),
        "ab2024_gdp_components": parse_gdp_chart(
            "efo_october2024_chapter2.xlsx",
            "C2.A",
            "Chart A: Policy impacts on real GDP and its components",
            "autumn_budget_2024",
            "series_down",
            rows,
        ),
        "ab2024_gdp_measures": parse_gdp_chart(
            "efo_october2024_chapter2.xlsx",
            "C2.B",
            "Chart B: Policy impacts on real GDP, by measure",
            "autumn_budget_2024",
            "series_down",
            rows,
        ),
        "ab2025_gdp_components": parse_gdp_chart(
            "efo_november2025_chapter3.xlsx",
            "C3.3",
            "Chart 3.3: Policy impacts on real ",
            "autumn_budget_2025",
            "series_down",
            rows,
        ),
        "ab2025_cpi": parse_cpi_chart(
            "efo_november2025_chapter3.xlsx",
            "C3.4",
            "Chart 3.4: Impact of budget polici",
            "autumn_budget_2025",
            rows,
        ),
        "bp10_supply_side": parse_bp10_supply_side(
            "obr_briefing_paper_10_supply_side.xlsx", "T2.1", rows
        ),
        "tb1_decisions": parse_tb1_decisions(
            "efo_march2026_annex_tables.xlsx", "TB.1", rows
        ),
    }
    out = OUT_DIR / f"{SOURCE_ID}.json"
    out.write_text(json.dumps(rows, indent=1))
    print(f"wrote {len(rows)} rows -> {out}")
    for k, v in counts.items():
        print(f"  {k}: {v}")
    return rows, counts


if __name__ == "__main__":
    build()
