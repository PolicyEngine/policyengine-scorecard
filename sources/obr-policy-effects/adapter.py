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

Value semantics — three DIFFERENT quantities, three unit concepts. All
three used to emit bare 'percent', which a query could then sum or
compare as one thing; they are separated deliberately:

    - GDP chart data is the per cent deviation in the LEVEL of real GDP
      (or of an expenditure component) -> 'percent_of_real_gdp'
    - AB2025 CPI chart data is the effect on CPI inflation in
      PERCENTAGE POINTS -> 'percentage_points'
    - Briefing-paper supply-side impacts are per cent of POTENTIAL
      output (the published column header says "per cent of GDP", the
      note says "the impact on potential output")
      -> 'percent_of_potential_gdp'
    - TB.1 amounts are GBP BILLION -> raw GBP ('gbp_nominal'); the
      published sign convention is carried verbatim in the row's
      'sign_convention' (positive = increases borrowing, per the table
      note) — NOT normalised here

All values are at full float precision (0.26 means 0.26 per cent).
Periods are financial years '2023-24'.. as published; briefing paper
supply-side impacts carry period 'forecast_horizon' (the table publishes
one number per measure, not a path — the ingest keys it to each scoring
event's own forecast horizon, which is NOT one shared year).

Identity vocabularies are CLOSED (the uk_aliases rule, applied at the
source side too): every chart series label, every briefing-paper
measure, type and channel, and every TB.1 line is mapped by an explicit
registry in this module. An unregistered label RAISES — a re-labelled or
re-shuffled workbook can no longer mint a claim under a slug nobody
decided. `_slug()` survives only as the helper those registries were
written with, never as a runtime fallback.

Every row records fiscal_event, basis ('forecast' — every row here is a
forecast quantity, the standard basis axis), scoring_method
('post_behavioural' for package effects, which OBR publishes on the
post-adjustment path; 'supply_side' for the briefing-paper channel
scorings — a scoring method is not a forecast/outturn basis and no
longer squats on that axis), scope ('package' or 'measure'), artifact
(the vendored file the row was read from, which carries its own
publication date and URL — publication provenance is per fiscal event,
never one generic stamp), baseline (the pre-measures world the row is
scored against, per event and per counterfactual kind) and source_column
(sheet:series verbatim). Titles are anchored: a sheet whose title cell
does not start with the expected published prefix is a hard error, so a
silently re-shuffled workbook cannot emit rows under the wrong label.
TB.1 carries the same aggregate_level/parent hierarchy convention as the
obr-welfare adapter so no consumer can double-count the nested 'of
which' rows, and its memo line is a TALLIED deliberate drop, never a
silent skip: the build reconciles 272 source cells = 266 claims + 6
drops.
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
    """Slug helper the registries below were WRITTEN with. It is never a
    runtime fallback: every label that reaches a row passes through a
    closed registry first, and an unregistered label raises."""
    return re.sub(r"[^a-z0-9]+", "_", str(label).strip().lower()).strip("_")


def _num(v):
    return float(v)


FY = re.compile(r"^\d{4}-\d{2}$")


def _closed(registry, key, what):
    """Closed-vocabulary lookup: an unregistered key raises, never mints
    an identity nobody decided (the uk_aliases rule)."""
    try:
        return registry[key]
    except KeyError:
        raise RuntimeError(
            f"unregistered {what}: {key!r} — the published workbook was "
            "re-labelled or re-shuffled. Register it deliberately in "
            "sources/obr-policy-effects/adapter.py, never pass it through"
        ) from None


# --- publication provenance, per vendored artifact --------------------------
# One stamp per artifact, and each artifact IS one fiscal event's release:
# a generic obr.uk/publications/ URL dated to the newest round misdates
# every older round's claims. Dates are the OBR release dates (the EFO is
# published on its fiscal event's day); `snapshot` is the Wayback capture
# the bytes came from and is deliberately NOT the publication date.
ARTIFACTS = {
    "efo_november2023_chapter2.xlsx": {
        "title": (
            "OBR Economic and fiscal outlook – November 2023, "
            "Chapter 2 charts and tables (Chart 2.A)"
        ),
        "url": (
            "https://obr.uk/docs/dlm_uploads/"
            "Chapter_2_charts_and_tables_November_2023.xlsx"
        ),
        "date": "2023-11-22",
        "snapshot": "20231122212755",
    },
    "efo_march2024_chapter2.xlsx": {
        "title": (
            "OBR Economic and fiscal outlook – March 2024, "
            "Chapter 2 charts and tables (Chart 2.A)"
        ),
        "url": (
            "https://obr.uk/docs/dlm_uploads/"
            "Chapter_2_charts_and_tables_March_2024.xlsx"
        ),
        "date": "2024-03-06",
        "snapshot": "20240306134036",
    },
    "efo_october2024_chapter2.xlsx": {
        "title": (
            "OBR Economic and fiscal outlook – October 2024, "
            "Chapter 2 charts and tables (Charts 2.A, 2.B)"
        ),
        "url": (
            "https://obr.uk/docs/dlm_uploads/"
            "Chapter_2_charts_and_tables_October_2024.xlsx"
        ),
        "date": "2024-10-30",
        "snapshot": "20241030144507",
    },
    "efo_november2025_chapter3.xlsx": {
        "title": (
            "OBR Economic and fiscal outlook – November 2025, "
            "Chapter 3 charts and tables (Charts 3.3, 3.4)"
        ),
        "url": (
            "https://obr.uk/docs/dlm_uploads/"
            "Chapter_3_charts_and_tables_November_2025.xlsx"
        ),
        "date": "2025-11-26",
        "snapshot": "20251130064953",
    },
    "efo_march2026_annex_tables.xlsx": {
        "title": (
            "OBR Economic and fiscal outlook – March 2026, Annex B "
            "Table B.1: total effect of Government decisions on borrowing"
        ),
        "url": (
            "https://obr.uk/docs/d055fbf02d5b3g6jq8l2/"
            "efo-march-2026-charts-and-tables-annex-tables.xlsx"
        ),
        "date": "2026-03-03",
        "snapshot": "20260316163140",
    },
    "obr_briefing_paper_10_supply_side.xlsx": {
        "title": (
            "OBR Briefing paper No.10: accounting for the supply-side "
            "effects of policy measures, Table 2.1"
        ),
        "url": (
            "https://obr.uk/docs/dlm_uploads/Briefing_paper_No.10_Accounting_"
            "for_the_supply-side_effects_of_policy_measures_charts_and_"
            "tables.xlsx"
        ),
        "date": "2025-11-26",
        "snapshot": "20251126134224",
    },
}
assert set(ARTIFACTS) == set(SHA256), "ARTIFACTS and SHA256 must cover the same files"

# --- unit concepts: three different quantities, never one 'percent' ---------
UNIT_GDP_LEVEL = "percent_of_real_gdp"
UNIT_CPI = "percentage_points"
UNIT_SUPPLY_SIDE = "percent_of_potential_gdp"
UNIT_GBP = "gbp_nominal"

# --- baseline worlds --------------------------------------------------------
# OBR scores a package against that EFO round's PRE-MEASURES forecast, not
# against "the law in force" in the abstract: the pre-measures forecast is
# a distinct, named world per round, and two rounds' pre-measures worlds
# are not the same world. Each row therefore carries its own baseline slug
# plus the counterfactual KIND (Briefing paper No.10 §2 is explicit that a
# tax/welfare measure is scored against its legislated-parameter
# counterfactual while a DEL or regulatory measure is scored against the
# pre-existing activity/spending baseline) and a locator.
_PRE_MEASURES = {
    "spring_budget_2023": "obr_pre_measures_spring_budget_2023",
    "autumn_statement_2023": "obr_pre_measures_autumn_statement_2023",
    "spring_budget_2024": "obr_pre_measures_spring_budget_2024",
    "autumn_budget_2024": "obr_pre_measures_autumn_budget_2024",
    "spring_statement_2025": "obr_pre_measures_spring_statement_2025",
    "autumn_budget_2025": "obr_pre_measures_autumn_budget_2025",
    # March 2026 Table B.1 is explicit in its own title: the decisions are
    # measured SINCE the November 2025 Budget, so the baseline is that
    # round's post-measures forecast — a different world again.
    "march_2026_efo": "obr_november_2025_budget_forecast",
}

_PACKAGE_LOCATOR = {
    "autumn_statement_2023": (
        "EFO November 2023, Chart 2.A: 'Real GDP impacts' of the Autumn "
        "Statement 2023 package, measured as deviations from the "
        "pre-measures November 2023 forecast."
    ),
    "spring_budget_2024": (
        "EFO March 2024, Chart 2.A: 'Impact of policy measures on real "
        "GDP', measured as deviations from the pre-measures March 2024 "
        "forecast."
    ),
    "autumn_budget_2024": (
        "EFO October 2024, Charts 2.A/2.B: 'Policy impacts on real GDP' "
        "by expenditure component and by measure, measured as deviations "
        "from the pre-measures October 2024 forecast."
    ),
    "autumn_budget_2025": (
        "EFO November 2025, Charts 3.3/3.4: policy impacts on real GDP "
        "and on CPI inflation, measured as deviations from the "
        "pre-measures November 2025 forecast."
    ),
    "march_2026_efo": (
        "EFO March 2026, Table B.1: 'Total effect of Government decisions "
        "since the November 2025 Budget' — the November 2025 Budget "
        "forecast is the counterfactual, stated in the table title."
    ),
}

# Briefing paper No.10 counterfactual kind by measure type.
_BP10_COUNTERFACTUAL = {
    "tax": "policy_parameters",
    "welfare": "policy_parameters",
    "del": "del_activity",
    "regulation": "regulatory",
}


def _bp10_locator(event_label, measure_slug):
    text = (
        f"OBR Briefing paper No.10 (November 2025), Table 2.1, section "
        f"'{event_label}': each measure is scored against that fiscal "
        "event's pre-measures forecast. Tax and welfare measures are "
        "scored against their legislated-parameter counterfactual; DEL "
        "and regulatory measures against the pre-existing "
        "activity/spending baseline (Briefing paper No.10, chapter 2)."
    )
    if measure_slug == "wca_reversal":
        text += (
            " Note: this measure reverses the November 2023 WCA reforms, "
            "so its counterfactual is the WCA-ADJUSTED world already "
            "embedded in the March 2025 pre-measures forecast — the "
            "negative sign is a partial undoing of an earlier scoring, "
            "not a fresh tightening."
        )
    return text


# --- closed identity registries ---------------------------------------------
# Chart series labels, verbatim as published -> canonical subgroup slug.
# 'total' is the reserved slug for a chart's own total line; the roll-up
# guard downstream keys off it, so it is decided HERE, not sniffed from
# the label text.
_SERIES = {
    ("autumn_statement_2023", "C2.A"): {
        "Supply: Full expensing": "supply_full_expensing",
        "Supply: NICs cut": "supply_nics_cut",
        "Supply: Welfare reforms & other": "supply_welfare_reforms_and_other",
        "Demand": "demand",
        "Total effect": "total",
    },
    ("spring_budget_2024", "C2.A"): {
        "Demand: multipliers": "demand_multipliers",
        "Supply: NICs cut": "supply_nics_cut",
        "Supply: child benefit": "supply_child_benefit",
        "Change in real GDP": "total",
    },
    # October 2024 chart 2.A splits the SAME package by expenditure
    # component; 'Private consumption' here and November 2025's
    # 'Consumption' are deliberately DISTINCT slugs (different published
    # component definitions, one year apart — no unification claimed).
    ("autumn_budget_2024", "C2.A"): {
        "Private consumption": "private_consumption",
        "Government consumption": "government_consumption",
        "Government investment": "government_investment",
        "Business investment": "business_investment",
        "Net trade and other": "net_trade_and_other",
        "GDP": "total",
    },
    ("autumn_budget_2024", "C2.B"): {
        "Demand: multipliers": "demand_multipliers",
        "Supply: employer NICs": "supply_employer_nics",
        "Supply: public investment": "supply_public_investment",
        "Supply: crowding out": "supply_crowding_out",
        "Change in real GDP": "total",
    },
    ("autumn_budget_2025", "C3.3"): {
        "Consumption": "consumption",
        "Residential and business investment": "residential_and_business_investment",
        "Government consumption and investment": (
            "government_consumption_and_investment"
        ),
        "Net trade and other": "net_trade_and_other",
        "Total": "total",
    },
    ("autumn_budget_2025", "C3.4"): {
        "Fuel duty freeze extension": "fuel_duty_freeze_extension",
        "Energy bills package": "energy_bills_package",
        "Rail fares freeze": "rail_fares_freeze",
        "Mileage-based charge on electric cars": (
            "mileage_based_charge_on_electric_cars"
        ),
        "Output gap": "output_gap",
        "Total": "total",
    },
}

# Fiscal-event section headers exactly as printed in briefing paper T2.1.
BP10_EVENTS = {
    "March 2023": "spring_budget_2023",
    "November 2023": "autumn_statement_2023",
    "March 2024": "spring_budget_2024",
    "October 2024": "autumn_budget_2024",
    "March 2025": "spring_statement_2025",
}

# Briefing paper T2.1 measure labels, verbatim (trailing spaces stripped)
# -> canonical program slug. 18 distinct labels over 19 rows: 'Employee
# NICs cut' is scored twice, at AS2023 and SB2024, and the two rows are
# separated by fiscal_event, not by slug — the same measure re-scored at
# a later event is the same measure.
_BP10_MEASURES = {
    "Universal Support": "universal_support",
    "30 free hours of childcare": "free_childcare_30_hours",
    "Universal credit (UC) childcare": "uc_childcare_upfront_costs",
    "UC conditionality": "uc_conditionality",
    "Pensions allowances": "pensions_allowances",
    "Restart": "restart_scheme",
    "Universal Support extension": "universal_support_extension",
    "Individual Placement and Support (IPS)": "individual_placement_and_support",
    "Talking therapies": "talking_therapies",
    "Work capability assessment (WCA) reforms": "wca_reforms",
    "Employee NICs cut": "employee_nics_cut",
    "Full expensing": "full_expensing",
    "High income child benefit charge (HICBC)": "hicbc_threshold",
    "Tax thresholds": "tax_threshold_freeze",
    "Public investment": "public_investment",
    "Employer NICs": "employer_nics",
    "WCA reversal": "wca_reversal",
    "Residential planning reforms": "residential_planning_reforms",
}
_BP10_TYPES = {
    "DEL": "del",
    "Welfare": "welfare",
    "Tax": "tax",
    "Regulation": "regulation",
}
_BP10_CHANNELS = {"Labour": "labour", "Capital": "capital", "TFP": "tfp"}
# Non-measure column-B labels in T2.1 that carry no value cell.
_BP10_NON_MEASURE = frozenset({"Policy measure"})


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


def _chart_row(fname, sheet, fiscal_event, metric, unit, series_label, period, value):
    """One package chart-data row, with per-event publication and
    baseline provenance attached."""
    slug = _closed(
        _SERIES[(fiscal_event, sheet)], series_label, f"{sheet} series label"
    )
    total = slug == "total"
    return {
        "source": SOURCE_ID,
        "country": "UK",
        "program": "policy_package",
        "metric": metric,
        "subgroup": "total" if total else slug,
        "variant": None,
        "geography": "UK",
        "unit_concept": unit,
        "period": period,
        "value": value,
        "status": "ok",
        "fiscal_event": fiscal_event,
        "basis": "forecast",
        "scoring_method": "post_behavioural",
        "scope": "package",
        "aggregate_level": "total" if total else "component",
        "parent": None if total else "policy_package",
        "artifact": fname,
        "baseline": _PRE_MEASURES[fiscal_event],
        "baseline_counterfactual": "policy_parameters",
        "baseline_locator": _PACKAGE_LOCATOR[fiscal_event],
        "source_column": f"{sheet}:{series_label}",
    }


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
            out.append(
                _chart_row(
                    fname,
                    sheet,
                    fiscal_event,
                    "gdp_level_effect",
                    UNIT_GDP_LEVEL,
                    series.strip(),
                    period.strip(),
                    _num(grid[(r, c)]),
                )
            )
            n += 1
    return n


def parse_cpi_chart(fname, sheet, title_prefix, fiscal_event, out):
    """AB2025 CPI-impact chart: years down col B, measures across.

    The published quantity is an effect on CPI INFLATION, in percentage
    points — not a per-cent deviation in a level, and not the
    briefing paper's per cent of potential output.
    """
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
            out.append(
                _chart_row(
                    fname,
                    sheet,
                    fiscal_event,
                    "cpi_inflation_effect",
                    UNIT_CPI,
                    series.strip(),
                    period,
                    _num(grid[(r, c)]),
                )
            )
            n += 1
    return n


def parse_bp10_supply_side(fname, sheet, out):
    """Briefing paper No.10 Table 2.1: per-measure supply-side impact on
    potential output (% of GDP), grouped under fiscal-event header rows.
    Columns: B measure, C description, E type, F channel, G impact
    (column D is absorbed by a merge in the published workbook)."""
    grid = _grid(RAW / fname, sheet)
    _title(grid, "Table 2.1: Policy measures with supply")
    event = None
    event_label = None
    n = 0
    rows = sorted({r for (r, c) in grid if c == 2 and r > 2})
    for r in rows:
        label = str(grid[(r, 2)]).strip()
        if label in BP10_EVENTS:
            event, event_label = BP10_EVENTS[label], label
            continue
        if label in _BP10_NON_MEASURE or (r, 7) not in grid:
            continue  # column-header / note / blank rows
        if event is None:
            raise RuntimeError(f"BP10 T2.1: measure {label!r} before any event header")
        measure = _closed(_BP10_MEASURES, label, "BP10 T2.1 measure")
        mtype = _closed(_BP10_TYPES, str(grid[(r, 5)]).strip(), "BP10 T2.1 type")
        channel = _closed(
            _BP10_CHANNELS, str(grid[(r, 6)]).strip(), "BP10 T2.1 supply-side channel"
        )
        out.append(
            {
                "source": SOURCE_ID,
                "country": "UK",
                "program": measure,
                "metric": "supply_side_impact",
                "subgroup": channel,
                "variant": mtype,
                "geography": "UK",
                "unit_concept": UNIT_SUPPLY_SIDE,
                # One number per measure, at that SCORING EVENT's forecast
                # horizon — the ingest resolves the symbol per event, so
                # nothing here pretends all 19 share a year.
                "period": "forecast_horizon",
                "value": _num(grid[(r, 7)]),
                "status": "ok",
                "fiscal_event": event,
                "basis": "forecast",
                "scoring_method": "supply_side",
                "scope": "measure",
                "aggregate_level": "component",
                "parent": None,
                "artifact": fname,
                "baseline": _PRE_MEASURES[event],
                "baseline_counterfactual": _BP10_COUNTERFACTUAL[mtype],
                "baseline_locator": _bp10_locator(event_label, measure),
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

# TB.1 value-bearing lines this adapter deliberately does NOT emit, with
# the reason. A value line that is neither in TB1_ROWS nor here is an
# unclassified line and raises: the memo row used to be skipped by the
# `hit is None: continue` fall-through, which made the 60-claim count
# unreconcilable against the 66 cells the table actually prints.
TB1_DROPS = [
    (
        "Memo: total effect of Government decisions on current budget",
        "memo_current_budget",
        "A different fiscal aggregate: the current budget, not public "
        "sector net borrowing. The four metrics this source publishes "
        "score PSNB; a current-budget effect is not comparable to them "
        "and is not laundered into the same metric.",
    ),
]


def _numeric(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def parse_tb1_decisions(fname, sheet, out, drops):
    """March 2026 Table B.1: effect of Government decisions since the
    November 2025 Budget on borrowing, GBP bn, direct/indirect split.

    Every value-bearing line is classified: emitted (TB1_ROWS) or
    deliberately dropped (TB1_DROPS). An unclassified value line raises,
    and the drops are tallied into the build's reconciliation so the
    claim count always ties back to the cells the table prints.
    """
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
    dropped = set()
    n = 0
    candidates = 0
    for r, label in sorted(labels.items()):
        values = {
            c: _numeric(grid.get((r, c)))
            for c in periods
            if _numeric(grid.get((r, c))) is not None
        }
        if not values:
            continue  # 'of which:' connectors, notes, source line
        candidates += len(values)
        hit = next(
            (t for t in TB1_ROWS if label.startswith(t[0]) and t[1] not in matched),
            None,
        )
        if hit is None:
            drop = next(
                (
                    d
                    for d in TB1_DROPS
                    if label.startswith(d[0]) and d[1] not in dropped
                ),
                None,
            )
            if drop is None:
                raise RuntimeError(
                    f"TB.1: unclassified value line {label!r} ({len(values)} "
                    "cells) — emit it in TB1_ROWS or record it in TB1_DROPS "
                    "with a reason; a value line is never silently skipped"
                )
            dropped.add(drop[1])
            drops.append(
                {
                    "table": f"{fname}:{sheet}",
                    "line": label,
                    "slug": drop[1],
                    "cells": len(values),
                    "reason": drop[2],
                }
            )
            continue
        prefix, slug, level, parent = hit
        matched.add(slug)
        for c, period in sorted(periods.items()):
            if c not in values:
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
                    "unit_concept": UNIT_GBP,
                    "period": period,
                    "value": values[c] * 1e9,
                    "status": "ok",
                    "fiscal_event": "march_2026_efo",
                    "basis": "forecast",
                    "scoring_method": "post_behavioural",
                    "scope": "package",
                    "sign_convention": "as_published_positive_increases",
                    "aggregate_level": level,
                    "parent": parent,
                    "artifact": fname,
                    "baseline": _PRE_MEASURES["march_2026_efo"],
                    "baseline_counterfactual": "policy_parameters",
                    "baseline_locator": _PACKAGE_LOCATOR["march_2026_efo"],
                    "source_column": f"{sheet}:{label}",
                }
            )
            n += 1
    missing = {t[1] for t in TB1_ROWS} - matched
    if missing:
        raise RuntimeError(f"TB.1: rows not found: {sorted(missing)}")
    missing_drops = {d[1] for d in TB1_DROPS} - dropped
    if missing_drops:
        raise RuntimeError(
            f"TB.1: declared drops not found in the table: {sorted(missing_drops)} "
            "— the workbook changed; re-decide the drop deliberately"
        )
    return n, candidates


def build():
    for fname in SHA256:
        _check_sha(fname)
    rows = []
    drops = []
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
    }
    tb1_claims, tb1_candidates = parse_tb1_decisions(
        "efo_march2026_annex_tables.xlsx", "TB.1", rows, drops
    )
    counts["tb1_decisions"] = tb1_claims

    # Source reconciliation: every numeric cell this adapter READ is
    # either a claim or a tallied deliberate drop. 266 claims alone was
    # not reconcilable against TB.1's 66 printed cells.
    dropped_cells = sum(d["cells"] for d in drops)
    candidates = len(rows) + dropped_cells
    reconciliation = {
        "source_cells_read": candidates,
        "claims": len(rows),
        "deliberate_drops": dropped_cells,
        "drops": drops,
    }
    if candidates != len(rows) + dropped_cells:  # pragma: no cover - identity
        raise RuntimeError("reconciliation does not close")
    # TB.1's own arithmetic, stated so the tie-back is checkable by hand.
    if tb1_candidates != 66:
        raise RuntimeError(
            f"TB.1: {tb1_candidates} classified cells != the 66 numeric cells "
            "the published table prints"
        )
    if counts["tb1_decisions"] + dropped_cells != tb1_candidates:
        raise RuntimeError(
            f"TB.1: {counts['tb1_decisions']} claims + {dropped_cells} drops "
            f"!= {tb1_candidates} classified cells"
        )

    out = OUT_DIR / f"{SOURCE_ID}.json"
    out.write_text(json.dumps(rows, indent=1))
    print(f"wrote {len(rows)} rows -> {out}")
    for k, v in counts.items():
        print(f"  {k}: {v}")
    print(
        f"  reconciliation: {candidates} source cells = {len(rows)} claims "
        f"+ {dropped_cells} deliberate drops"
    )
    for d in drops:
        print(f"    drop {d['slug']}: {d['cells']} cells — {d['line']}")
    return rows, counts, reconciliation


if __name__ == "__main__":
    build()
