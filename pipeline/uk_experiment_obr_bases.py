"""Extract the OBR's forecast head totals that scale policy-experiment costings.

The OBR's Historical official forecasts database holds, for each forecast
vintage, its forecast of each tax head and welfare total by fiscal year. A
policy experiment (docs/uk_replay/POLICY_EXPERIMENTS.md) scales an old
costing by the ratio of a modern base to the event-vintage forecast of the
same head. This builder reads the Spring 2026 edition, keeps every vintage
row of the sheets below with its cell reference, and checks that every
vintage row also present in the March 2025 edition (the one the event vintage
locks name) is identical.

    python3 -m pipeline.uk_experiment_obr_bases            # write
    python3 -m pipeline.uk_experiment_obr_bases --check    # compare with the committed file
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "data" / "uk" / "experiments" / "obr_head_forecasts.json"
DOWNLOADS = Path.home() / "scorecard-harvest" / "uk_obr" / "downloads"
SOURCES = {
    "spring_2026": {
        "file": "Historical_official_forecasts_database_Spring_2026.xlsx",
        "url": "https://obr.uk/docs/dlm_uploads/Historical_official_forecasts_database_Spring_2026.xlsx",
        "archive": "https://web.archive.org/web/20260328182841id_/https://obr.uk/docs/dlm_uploads/Historical_official_forecasts_database_Spring_2026.xlsx",
        "sha256": "e00b17cb7ec8dfddc4bfd4d212c1e93362147fff81d74a10480e599b26e634db",
    },
    "march_2025": {
        "file": "Historical_official_forecasts_database_March_2025.xlsx",
        "url": "https://obr.uk/docs/Historical_official_forecasts_database_March_2025.xlsx",
        "archive": "https://web.archive.org/web/20250404155002id_/https://obr.uk/docs/Historical_official_forecasts_database_March_2025.xlsx",
        # The edition data/uk/events/vintage_locks/*.json lock as hofd_row.
        "sha256": "d69fa5112266c71fff0c74bffe416b7c7c0f663b44e0b87e7a82899d09ba39d5",
    },
}
PRIMARY = "spring_2026"
# Sheet -> the head it forecasts. Sheet names are the database's own.
SHEETS = {
    "IT": "Income tax",
    "NICS": "National insurance contributions",
    "HSC": "Health and social care levy",
    "CGT": "Capital gains tax",
    "IHT": "Inheritance tax",
    "Fuel": "Fuel duties",
    "VAT": "Value added tax",
    "PTT": "Property transaction taxes",
    "Alcohol": "Alcohol duties",
    "Tobacco": "Tobacco duties",
    "VED": "Vehicle excise duties",
    "Council": "Council tax",
    "Total welfare": "Welfare spending",
    "Welfare in": "Welfare spending inside the welfare cap",
    "Welfare out": "Welfare spending outside the welfare cap",
}
FY = re.compile(r"^(\d{4})-(\d{2})$")
VINTAGE = re.compile(
    r"^(January|February|March|April|May|June|July|August|September|October|November|December) (\d{4})$"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def column_letter(index: int) -> str:
    """1-based column number to its spreadsheet letters."""
    letters = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        letters = chr(65 + remainder) + letters
    return letters


def read_sheet(workbook, sheet: str) -> dict[str, dict[str, dict]]:
    """vintage -> FY -> {value_gbp_bn, cell}; only forecast vintage rows.

    The header row is the one whose second cell is a fiscal-year label. Rows
    whose first cell is not a month-year vintage (the outturn row, notes) are
    skipped: an outturn is never an event's forecast."""
    rows = list(workbook[sheet].iter_rows(values_only=True))
    header_index = next(
        i
        for i, row in enumerate(rows)
        if len(row) > 1 and isinstance(row[1], str) and FY.match(row[1])
    )
    header = rows[header_index]
    out: dict[str, dict[str, dict]] = {}
    for offset, row in enumerate(rows[header_index + 1 :], start=header_index + 2):
        label = row[0]
        if not isinstance(label, str) or not VINTAGE.match(label.strip()):
            continue
        values = {}
        for column, (fy, value) in enumerate(zip(header, row), start=1):
            if column == 1 or not isinstance(fy, str) or not FY.match(fy):
                continue
            if value is None or isinstance(value, str):
                continue
            number = float(value)
            if not math.isfinite(number):
                raise ValueError(f"{sheet}!{column_letter(column)}{offset}: not finite")
            values[fy] = {
                "value_gbp_bn": number,
                "cell": f"{sheet}!{column_letter(column)}{offset}",
            }
        if values:
            if label.strip() in out:
                raise ValueError(f"{sheet}: repeated vintage row {label!r}")
            out[label.strip()] = values
    return out


def build(downloads: Path = DOWNLOADS) -> dict:
    import openpyxl

    tables = {}
    for name, source in SOURCES.items():
        path = downloads / source["file"]
        digest = sha256_file(path)
        if digest != source["sha256"]:
            raise ValueError(f"{path}: sha256 {digest}, expected {source['sha256']}")
        workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
        tables[name] = {sheet: read_sheet(workbook, sheet) for sheet in SHEETS}
        workbook.close()
    primary = tables[PRIMARY]
    for sheet, vintages in tables["march_2025"].items():
        for vintage, values in vintages.items():
            later = primary[sheet].get(vintage)
            if later is None:
                raise ValueError(
                    f"{sheet} {vintage}: missing from the Spring 2026 edition"
                )
            for fy, cell in values.items():
                if later.get(fy, {}).get("value_gbp_bn") != cell["value_gbp_bn"]:
                    raise ValueError(
                        f"{sheet} {vintage} {fy}: March 2025 edition "
                        f"{cell['value_gbp_bn']}, Spring 2026 edition "
                        f"{later.get(fy, {}).get('value_gbp_bn')}"
                    )
    vintage_order = sorted(
        {v for sheet in primary.values() for v in sheet},
        key=lambda v: (int(VINTAGE.match(v)[2]), _month(VINTAGE.match(v)[1])),
    )
    return {
        "schema_version": 1,
        "kind": "obr_head_forecasts",
        "purpose": (
            "Scaling bases for policy experiments on the modern population "
            "(docs/uk_replay/POLICY_EXPERIMENTS.md). Forecast vintage rows "
            "only; outturn rows are excluded."
        ),
        "unit": "GBP billion, fiscal year",
        "source": {name: {k: v for k, v in s.items()} for name, s in SOURCES.items()},
        "primary_source": PRIMARY,
        "cross_check": (
            "Every vintage row in the March 2025 edition equals the Spring 2026 "
            "edition's row, value for value."
        ),
        "sheets": SHEETS,
        "vintages": vintage_order,
        "forecasts": primary,
    }


def _month(name: str) -> int:
    return [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ].index(name)


def canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(value, indent=1, sort_keys=True, allow_nan=False) + "\n"
    ).encode()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--downloads", type=Path, default=DOWNLOADS)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    payload = canonical_bytes(build(args.downloads))
    if args.check:
        if OUTPUT.read_bytes() != payload:
            print(f"{OUTPUT} differs from the database editions", file=sys.stderr)
            return 1
        print(f"{OUTPUT} matches")
        return 0
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_bytes(payload)
    print(f"wrote {OUTPUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
