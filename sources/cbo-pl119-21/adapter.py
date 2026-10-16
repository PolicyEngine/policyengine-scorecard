"""Adapter: CBO's analyses of P.L. 119-21 against its January 2025 baseline
-> tidy rows (lane cbo-cost-estimates).

Input (raw/, cbo.gov through the Wayback Machine — the live site blocks
scripted fetches; capture ids and hashes in source.json):
    61367-data.xlsx                   figure data of the distributional
                                      letter: Figures 1 and 2, average
                                      annual change in household resources
                                      over 2026-2034, by income decile and
                                      channel
    61367-Distributional-Effects.pdf  the letter (August 11, 2025); its text
                                      quotes four deciles, an independent
                                      check on the workbook
    61367-SNAP.pdf                    the supplemental information on SNAP
                                      (sections 10101-10105), whose
                                      period-window statements are staged
                                      here
Output: data/externals/cbo-pl119-21.json.

Rows:
  * distribution — 10 deciles x 5 columns (four channels and the net
    effect) x 2 figures (2025 dollars per household; percent of baseline
    income after transfers and taxes) = 100 rows, each an annual average
    over 2026-2034.
  * snap — one row per number in SNAP_STATEMENTS, captured from its
    verbatim sentence. Signs: a reduction is negative; affected counts and
    shares are positive.

The supplement's single-year TFP numbers (section 10101, 2034) are already
staged by the 2026-08-02 harvest (scorecard_db/ingest_cbo.py) and are not
repeated here.

QC (any failure raises):
  1. the workbook's figure titles, units, column headers and decile labels
     are verbatim
  2. in every decile the four channels add to the net effect, within the
     rounding of five rounded cells (2.5 dollars; 0.25 percent)
  3. the letter's quoted deciles equal the workbook's cells (dollars to
     the letter's hundreds, percents exactly)
  4. section 10102's four groups add to its 2.4 million total
  5. every SNAP statement occurs exactly once in the supplement's text

Run (needs pypdf; imported lazily so the parsing helpers stay importable
without it):
    uv run --with pypdf python sources/cbo-pl119-21/adapter.py
"""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
OUT = HERE.parent.parent / "data" / "externals" / "cbo-pl119-21.json"
WORKBOOK = RAW / "61367-data.xlsx"
LETTER = RAW / "61367-Distributional-Effects.pdf"
SUPPLEMENT = RAW / "61367-SNAP.pdf"

NS = {
    "m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "p": "http://schemas.openxmlformats.org/package/2006/relationships",
}

DIST_WINDOW = "2026-2034"
# sheet -> (verbatim title, verbatim unit line, metric, unit_concept)
FIGURES = {
    "Figure 1": (
        (
            "Figure 1. Average Annual Change in Resources per Household Relative "
            "to CBO's January 2025 Baseline, 2026 to 2034"
        ),
        "2025 dollars",
        "avg_change_after_tax_income_usd",
        "usd_per_household",
    ),
    "Figure 2": (
        (
            "Figure 2. Average Annual Change in Household Resources as a "
            "Percentage of Income in CBO's January 2025 Baseline, After "
            "Transfers and Taxes, 2026 to 2034"
        ),
        "Percent",
        "pct_change_after_tax_income",
        "percent",
    ),
}
# verbatim column header -> component slug; the last is the net effect
COLUMNS = {
    "Federal taxes and cash transfers": "federal_taxes_and_cash_transfers",
    "Federal and state in-kind transfers": "federal_and_state_in_kind_transfers",
    "States' fiscal responses": "states_fiscal_responses",
    "Other spending and revenue": "other_spending_and_revenue",
    "Net effect": "net_effect",
}
DECILES = [
    "Lowest",
    "2nd",
    "3rd",
    "4th",
    "5th",
    "6th",
    "7th",
    "8th",
    "9th",
    "Highest",
]
# five rounded cells: four channels and the net effect
ROUNDING = {"Figure 1": 5 * 0.5, "Figure 2": 5 * 0.05}

# The letter's own quotes of the workbook (p. 4): decile -> (dollars as
# quoted, percent as quoted, verbatim anchor of each).
LETTER_QUOTES = {
    "Lowest": (
        r"will decrease by about \$([\d,]+) per year \(in 2025 dollars\)",
        r"That amounts to ([\d.]+) percent of their income",
        -1,
    ),
    "5th": (
        r"will see their resources increase by \$([\d,]+) \(or",
        r"increase by \$800 \(or ([\d.]+) percent of projected income\)",
        1,
    ),
    "6th": (
        r"\) and \$([\d,]+) \(or [\d.]+ percent of projected income\), respectively",
        r"\) and \$1,200 \(or ([\d.]+) percent of projected income\), respectively",
        1,
    ),
    "Highest": (
        r"by about \$([\d,]+) annually for households in the highest decile",
        r"amounting to ([\d.]+) percent of their projected income",
        1,
    ),
}

# The supplement's period-window statements. Each pattern is the verbatim
# sentence fragment (whitespace collapsed, non-breaking hyphens folded)
# with ONE capture group around the number.
# key: (section, pattern, scale, sign, metric, unit_concept, time_basis,
#       window, window_kind, program, extra conditions)
SNAP_STATEMENTS = {
    "work_requirements_total": (
        "10102",
        (
            r"reduce participation in SNAP by roughly ([\d.]+) million people in "
            r"an average month over the 2025-2034 period"
        ),
        1e6,
        -1,
        "participant_count_change",
        "persons",
        "average_month",
        "2025-2034",
        "annual_average",
        "snap",
        {"subgroup": "total"},
    ),
    "work_requirements_abawds_through_64": (
        "10102",
        (
            r"Of those people, about ([\d,]+) will be able-bodied adults through "
            r"age 64 who do not live with dependent children"
        ),
        1,
        -1,
        "participant_count_change",
        "persons",
        "average_month",
        "2025-2034",
        "annual_average",
        "snap",
        {"subgroup": "abawds_through_64"},
    ),
    "work_requirements_adults_with_children_14_plus": (
        "10102",
        (
            r"Another ([\d,]+) will be able-bodied adults ages 18 to 64 who live "
            r"with children who are age 14 or older"
        ),
        1,
        -1,
        "participant_count_change",
        "persons",
        "average_month",
        "2025-2034",
        "annual_average",
        "snap",
        {"subgroup": "adults_18_64_with_children_14_plus"},
    ),
    "work_requirements_waiver_loss": (
        "10102",
        (
            r"And roughly ([\d.]+) million will be able-bodied adults ages 18 to "
            r"54 \(or 18 to 49, starting in 2031\) who do not live with "
            r"dependents but who, in CBO.s January 2025 baseline projections "
            r"\(which preceded the law.s enactment\), would have received a "
            r"waiver from the work requirements"
        ),
        1e6,
        -1,
        "participant_count_change",
        "persons",
        "average_month",
        "2025-2034",
        "annual_average",
        "snap",
        {"subgroup": "abawds_losing_waivers"},
    ),
    "work_requirements_exemption_changes_net": (
        "10102",
        (
            r"resulting in a net reduction in SNAP participation of ([\d,]+) "
            r"people in those groups"
        ),
        1,
        -1,
        "participant_count_change",
        "persons",
        "average_month",
        "2025-2034",
        "annual_average",
        "snap",
        {"subgroup": "veterans_homeless_former_foster_youth_net_of_american_indians"},
    ),
    "sua_energy_assistance_benefit_change": (
        "10103",
        (
            r"the monthly SNAP benefit will decrease by roughly \$(\d+) for about "
            r"3 percent of households, on average, in each year over the "
            r"2026-2034 period"
        ),
        1,
        -1,
        "average_monthly_benefit_change",
        "usd",
        "average_month",
        "2026-2034",
        "annual_average",
        "snap",
        {"per": "household", "subgroup": "affected_households"},
    ),
    "sua_energy_assistance_affected_share": (
        "10103",
        (
            r"the monthly SNAP benefit will decrease by roughly \$100 for about "
            r"(\d+) percent of households, on average, in each year over the "
            r"2026-2034 period"
        ),
        0.01,
        1,
        "affected_share",
        "share",
        "annual",
        "2026-2034",
        "annual_average",
        "snap",
        {"subgroup": "snap_households"},
    ),
    "internet_expenses_benefit_change": (
        "10104",
        (
            r"the SNAP monthly benefit will decrease by about \$(\d+) for roughly "
            r"65 percent of households, on average, in each year over the "
            r"2026-2034 period"
        ),
        1,
        -1,
        "average_monthly_benefit_change",
        "usd",
        "average_month",
        "2026-2034",
        "annual_average",
        "snap",
        {"per": "household", "subgroup": "affected_households"},
    ),
    "internet_expenses_affected_share": (
        "10104",
        (
            r"the SNAP monthly benefit will decrease by about \$10 for roughly "
            r"(\d+) percent of households, on average, in each year over the "
            r"2026-2034 period"
        ),
        0.01,
        1,
        "affected_share",
        "share",
        "annual",
        "2026-2034",
        "annual_average",
        "snap",
        {"subgroup": "snap_households"},
    ),
    "matching_funds_direct_spending": (
        "10105",
        (
            r"section 10105 will reduce direct spending by \$(\d+) billion over "
            r"the 2028-2034 period"
        ),
        1e9,
        -1,
        "benefit_cost_change",
        "usd",
        "fiscal_year",
        "2028-2034",
        "total",
        "snap",
        {"component": "total"},
    ),
    "matching_funds_state_cost_share": (
        "10105",
        (
            r"Most of that reduction \(about \$(\d+) billion\) stems from states "
            r"paying a portion of SNAP benefits"
        ),
        1e9,
        -1,
        "benefit_cost_change",
        "usd",
        "fiscal_year",
        "2028-2034",
        "total",
        "snap",
        {"component": "state_cost_share"},
    ),
    "matching_funds_state_responses_people": (
        "10105",
        (
            r"in an average month over the 2028-2034 period states collectively "
            r"will reduce or eliminate SNAP benefits for about ([\d,]+) people"
        ),
        1,
        1,
        "affected_count",
        "persons",
        "average_month",
        "2028-2034",
        "annual_average",
        "snap",
        {"component": "state_responses"},
    ),
    "matching_funds_state_responses_spending": (
        "10105",
        (
            r"Those changes will reduce direct spending by about \$(\d+) billion "
            r"over the period"
        ),
        1e9,
        -1,
        "benefit_cost_change",
        "usd",
        "fiscal_year",
        "2028-2034",
        "total",
        "snap",
        {"component": "state_responses"},
    ),
    "matching_funds_child_nutrition_children": (
        "10105",
        (
            r"subsidies provided through child nutrition programs will decrease "
            r"for about ([\d,]+) children"
        ),
        1,
        1,
        "affected_count",
        "children",
        "average_month",
        "2028-2034",
        "annual_average",
        "child_nutrition",
        {"component": "state_responses"},
    ),
    "matching_funds_child_nutrition_spending": (
        "10105",
        (
            r"reducing direct spending by about \$(\d+) million over the "
            r"2028-2034 period"
        ),
        1e6,
        -1,
        "benefit_cost_change",
        "usd",
        "fiscal_year",
        "2028-2034",
        "total",
        "child_nutrition",
        {"component": "state_responses"},
    ),
}
WORK_REQUIREMENT_GROUPS = (
    "work_requirements_abawds_through_64",
    "work_requirements_adults_with_children_14_plus",
    "work_requirements_waiver_loss",
    "work_requirements_exemption_changes_net",
)
EXPECTED_ROWS = 100 + len(SNAP_STATEMENTS)


def _clean(text: str) -> str:
    """Collapse whitespace and fold the non-breaking hyphens CBO uses."""
    return re.sub(r"\s+", " ", text.replace("‑", "-").replace("‐", "-"))


def _number(text: str) -> float:
    return float(text.replace(",", ""))


def read_sheets(path: Path) -> dict[str, list[list]]:
    """Every worksheet as a grid of rows (None for empty cells), by name.
    Shared strings and numbers are decoded; nothing else is expected."""
    with zipfile.ZipFile(path) as z:
        shared = []
        root = ET.fromstring(z.read("xl/sharedStrings.xml"))
        for si in root.findall("m:si", NS):
            shared.append("".join(t.text or "" for t in si.iter(f"{{{NS['m']}}}t")))
        rels = {
            r.get("Id"): r.get("Target")
            for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels")).findall(
                "p:Relationship", NS
            )
        }
        book = ET.fromstring(z.read("xl/workbook.xml"))
        sheets = {}
        for s in book.find("m:sheets", NS).findall("m:sheet", NS):
            target = rels[s.get(f"{{{NS['r']}}}id")]
            sheets[s.get("name")] = ET.fromstring(z.read(f"xl/{target}"))
    out = {}
    for name, sheet in sheets.items():
        grid = []
        for row in sheet.find("m:sheetData", NS).findall("m:row", NS):
            cells = {}
            for c in row.findall("m:c", NS):
                col = re.match(r"[A-Z]+", c.get("r")).group(0)
                kind, v = c.get("t"), c.find("m:v", NS)
                if v is None:
                    continue
                if kind == "s":
                    value = shared[int(v.text)]
                elif kind == "str":  # a formula's cached text
                    value = v.text or ""
                elif kind in (None, "n"):
                    value = float(v.text)
                else:
                    raise ValueError(f"{name}: unexpected cell type {kind!r}")
                cells[col] = value
            cols = sorted(cells, key=lambda c: (len(c), c))
            grid.append([cells[c] for c in cols])
        out[name] = grid
    return out


def parse_figures(sheets: dict[str, list[list]]) -> dict[str, dict[str, list]]:
    """{figure: {decile: [four channels..., net effect]}}, with check 1."""
    out = {}
    for name, (title, unit, _, _) in FIGURES.items():
        rows = [r for r in sheets[name] if r]
        texts = [" ".join(str(r[0]).split()) for r in rows if len(r) == 1]
        if title not in texts or unit not in texts:
            raise ValueError(f"QC failed: {name} title or unit line changed")
        header = next(r for r in rows if len(r) == 6)
        labels = [" ".join(str(h).split()) for h in header[1:]]
        if labels != list(COLUMNS) or " ".join(header[0].split()) != (
            "Household income decile"
        ):
            raise ValueError(f"QC failed: {name} columns changed: {labels}")
        body = rows[rows.index(header) + 1 :]
        table = {r[0]: r[1:] for r in body if len(r) == 6}
        if list(table) != DECILES:
            raise ValueError(f"QC failed: {name} deciles changed: {list(table)}")
        out[name] = table
    return out


def _close(a: float, b: float, tol: float, what: str) -> None:
    if abs(a - b) > tol + 1e-9:
        raise ValueError(f"QC failed: {what}: {a} vs {b} (tolerance {tol})")


def qc_figures(figures: dict, letter_text: str | None) -> None:
    """Checks 2 and 3 (check 3 only when the letter's text is given)."""
    for name, table in figures.items():
        for decile, cells in table.items():
            _close(sum(cells[:4]), cells[4], ROUNDING[name], f"{name} {decile}")
    if letter_text is None:
        return
    for decile, (usd_re, pct_re, sign) in LETTER_QUOTES.items():
        usd = [_number(m) for m in re.findall(usd_re, letter_text)]
        pct = [_number(m) for m in re.findall(pct_re, letter_text)]
        if len(usd) != 1 or len(pct) != 1:
            raise ValueError(f"QC failed: letter quote for {decile} not found once")
        _close(
            sign * usd[0],
            round(figures["Figure 1"][decile][4], -2),
            0,
            f"letter dollars, {decile} decile",
        )
        _close(
            sign * pct[0],
            figures["Figure 2"][decile][4],
            0,
            f"letter percent, {decile} decile",
        )


def parse_statements(text: str) -> dict[str, tuple[float, str]]:
    """Check 5: every statement occurs exactly once. Returns the signed,
    scaled value and the sentence fragment exactly as matched."""
    out = {}
    for key, spec in SNAP_STATEMENTS.items():
        found = list(re.finditer(spec[1], text))
        if len(found) != 1:
            raise ValueError(f"QC failed: statement {key} found {len(found)} times")
        m = found[0]
        out[key] = (round(spec[3] * _number(m.group(1)) * spec[2], 10), m.group(0))
    return out


def qc_statements(values: dict[str, tuple[float, str]]) -> None:
    """Check 4: section 10102's groups add to its total (both rounded to
    the 100,000 people the supplement states)."""
    groups = sum(values[k][0] for k in WORK_REQUIREMENT_GROUPS)
    _close(groups, values["work_requirements_total"][0], 0, "section 10102 groups")


def _pdf_text(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as e:
        raise SystemExit("this adapter needs pypdf: uv run --with pypdf ...") from e
    import logging

    logging.getLogger("pypdf").setLevel(logging.ERROR)
    return _clean(" ".join(p.extract_text() for p in PdfReader(path).pages))


def tidy(figures: dict, values: dict[str, tuple[float, str]]) -> list[dict]:
    rows = []
    for name, (_, unit_line, metric, unit) in FIGURES.items():
        for decile, cells in figures[name].items():
            for (header, component), value in zip(COLUMNS.items(), cells):
                rows.append(
                    {
                        "source": "cbo-pl119-21",
                        "country": "US",
                        "family": "distribution",
                        "section": None,
                        "program": None,
                        "metric": metric,
                        "unit_concept": unit,
                        "time_basis": "annual",
                        "geography": "US",
                        "period": DIST_WINDOW,
                        "window_kind": "annual_average",
                        "conditions": {
                            "income_group": decile,
                            "component": component,
                        },
                        "value": value,
                        "status": "ok",
                        "source_column": (
                            f"61367-data.xlsx, {name}: {decile}, {header} ({unit_line})"
                        ),
                    }
                )
    for key, spec in SNAP_STATEMENTS.items():
        section, _, _, _, metric, unit, basis, window, kind, program, extra = spec
        value, verbatim = values[key]
        rows.append(
            {
                "source": "cbo-pl119-21",
                "country": "US",
                "family": "snap",
                "section": section,
                "program": program,
                "metric": metric,
                "unit_concept": unit,
                "time_basis": basis,
                "geography": "US",
                "period": window,
                "window_kind": kind,
                "conditions": dict(extra),
                "value": value,
                "status": "ok",
                "source_column": f'61367-SNAP.pdf, section {section}: "{verbatim}"',
                "statement": key,
            }
        )
    return rows


def run() -> list[dict]:
    figures = parse_figures(read_sheets(WORKBOOK))
    qc_figures(figures, _pdf_text(LETTER))
    values = parse_statements(_pdf_text(SUPPLEMENT))
    qc_statements(values)
    rows = tidy(figures, values)
    if len(rows) != EXPECTED_ROWS:
        raise SystemExit(f"row contract broken: {len(rows)} != {EXPECTED_ROWS}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rows, indent=1) + "\n")
    return rows


if __name__ == "__main__":
    out = run()
    print(f"wrote {len(out)} rows to {OUT}")
