"""Stage locked OBR PMD original-scorecard cells without network access.

Port of the November 2025 harvest's stage_pmd.py. The OOXML reader uses only
the standard library and retains the original solid FFE1E9EE extension-cell
exclusion. Tax values are revenue_change; spending values retain Treasury's
positive-gain-to-Exchequer convention as proposed exchequer_impact.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import math
import posixpath
import re
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlsplit

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
REL_NS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
EXT_FILL = "FFE1E9EE"
FY_PATTERN = re.compile(r"\d{4}-\d{2}")
SHEETS = (
    ("Tax Measures", "tax_head", "tax"),
    ("Spending Measures", "spending_head", "spending"),
)


def _column(reference: str) -> int:
    number = 0
    for char in reference:
        if not char.isalpha():
            break
        number = number * 26 + ord(char) - ord("A") + 1
    return number


def _worksheet_paths(archive: zipfile.ZipFile) -> dict[str, str]:
    relationships = {
        relationship.attrib["Id"]: relationship.attrib["Target"]
        for relationship in ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    }
    paths = {}
    for sheet in ET.fromstring(archive.read("xl/workbook.xml")).findall(
        f"{NS}sheets/{NS}sheet"
    ):
        target = relationships[sheet.attrib[f"{REL_NS}id"]]
        paths[sheet.attrib["name"]] = (
            target.lstrip("/")
            if target.startswith("/")
            else posixpath.normpath(posixpath.join("xl", target))
        )
    return paths


def _extended_styles(archive: zipfile.ZipFile) -> set[int]:
    styles = ET.fromstring(archive.read("xl/styles.xml"))
    fills = []
    for fill in styles.find(f"{NS}fills"):
        pattern = fill.find(f"{NS}patternFill")
        color = None if pattern is None else pattern.find(f"{NS}fgColor")
        fills.append(
            pattern is not None
            and pattern.get("patternType") == "solid"
            and color is not None
            and color.get("rgb") == EXT_FILL
        )
    return {
        index
        for index, style in enumerate(styles.find(f"{NS}cellXfs"))
        if fills[int(style.get("fillId", "0"))]
    }


def _cell_value(cell: ET.Element, shared: list[str]):
    # The original script loaded formula text, not cached results, so formulas
    # never became staged numeric costings.
    if cell.find(f"{NS}f") is not None:
        return None
    kind = cell.get("t", "n")
    if kind == "inlineStr":
        return "".join(part.text or "" for part in cell.findall(f".//{NS}t"))
    value = cell.find(f"{NS}v")
    if value is None or value.text is None:
        return None
    raw = value.text
    if kind == "s":
        return shared[int(raw)]
    if kind in {"str", "e"}:
        return raw
    if kind == "b":
        return raw == "1"
    return float(raw)


def _read_sheet(
    archive: zipfile.ZipFile,
    path: str,
    shared: list[str],
    extended_styles: set[int],
):
    """Yield physical rows, retaining coordinates and original cell styling."""
    with archive.open(path) as stream:
        for _, element in ET.iterparse(stream, events=("end",)):
            if element.tag != f"{NS}row":
                continue
            cells = {}
            for cell in element.findall(f"{NS}c"):
                reference = cell.attrib["r"]
                cells[_column(reference)] = (
                    _cell_value(cell, shared),
                    int(cell.get("s", "0")) in extended_styles,
                    reference,
                )
            yield int(element.attrib["r"]), cells
            element.clear()


def publication_metadata(source: dict, receipt: dict, edition: str) -> dict:
    return {
        "title": f"Policy measures database ({edition})",
        "publisher": "Office for Budget Responsibility",
        "publication_url": "https://obr.uk/data/",
        "url": source["original_url"],
        "wayback": source["archive_capture_url"],
        "vintage": edition,
        "edition": edition,
        "workbook": Path(urlsplit(source["original_url"]).path).name,
        "units_note": "All figures in GBP million; Treasury costings rounded to nearest GBP 5m (GBP 1m since Budget 2018)",
        "sign_convention": "positive = gain to the Exchequer (reduces borrowing); verbatim from Notes sheet",
        "sha256": source["sha256"],
        "receipt_sha256": receipt["receipt_sha256"],
    }


def stage_workbook(
    workbook: Path, receipt: dict, *, edition: str = "March 2026"
) -> tuple[list[dict], dict]:
    """Hash-check scratch bytes against a validated receipt before staging."""
    from .collect_obr_pmd import check_receipt, locked_source

    check_receipt(receipt)
    if edition != receipt["edition_label"]:
        raise ValueError("PMD staging edition does not match the locked receipt")
    source = locked_source(receipt)
    payload = workbook.read_bytes()
    if (
        len(payload) != source["byte_size"]
        or hashlib.sha256(payload).hexdigest() != source["sha256"]
    ):
        raise ValueError("PMD workbook bytes do not match the locked receipt")
    publication = publication_metadata(source, receipt, edition)
    rows = []
    counts = Counter()
    events = defaultdict(Counter)
    titles = defaultdict(set)
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        paths = _worksheet_paths(archive)
        if list(paths) != source["sheet_names"]:
            raise ValueError("PMD workbook sheet names do not match the receipt")
        shared = []
        if "xl/sharedStrings.xml" in archive.namelist():
            shared = [
                "".join(part.text or "" for part in entry.findall(f".//{NS}t"))
                for entry in ET.fromstring(archive.read("xl/sharedStrings.xml"))
            ]
        extended_styles = _extended_styles(archive)
        for sheet, head_field, kind in SHEETS:
            fy_columns = []
            for number, cells in _read_sheet(
                archive, paths[sheet], shared, extended_styles
            ):
                if number == 3:
                    fy_columns = [
                        (column, value)
                        for column, (value, _, _) in sorted(cells.items())
                        if isinstance(value, str) and FY_PATTERN.fullmatch(value)
                    ]
                    continue
                if number < 4:
                    continue
                event = cells.get(2, (None,))[0]
                measure = cells.get(3, (None,))[0]
                head = cells.get(4, (None,))[0]
                if not event or not measure:
                    continue
                event, measure = str(event), str(measure)
                counts[f"{kind}_measure_rows"] += 1
                events[event]["measure_rows"] += 1
                events[event][f"{kind}_measure_rows"] += 1
                titles[event].add(measure)
                for column, fy in fy_columns:
                    raw, extended, reference = cells.get(column, (None, False, None))
                    if raw is None or raw == "":
                        continue
                    try:
                        value = float(raw)
                    except (TypeError, ValueError):
                        continue
                    if not math.isfinite(value):
                        raise ValueError(f"Non-finite PMD value: {sheet}!{reference}")
                    if extended:
                        counts["skipped_extended_cells"] += 1
                        events[event]["skipped_extended_cells"] += 1
                        continue
                    conditions = {
                        "geography": "UK",
                        "fy": fy,
                        "fiscal_event": event,
                        head_field: str(head) if head else "",
                        "basis": "forecast",
                        "costing_phase": "original_scorecard",
                        "sign_convention": "positive_gain_to_exchequer",
                        "edition": edition,
                    }
                    row = {
                        "source": "obr",
                        "proposed_unit": "gbp",
                        "value": value * 1e6,
                        "value_raw": raw,
                        "normalization": "sheet value in GBP millions x 1e6 -> GBP",
                        "period": int(fy[:4]),
                        "time_basis": "fiscal_year",
                        "conditions": conditions,
                        "reform_hint": measure,
                        "calibration_relationship": "held_out",
                        "source_model": "hmt_scorecard_obr_database",
                        "source_column": fy,
                        "source_table": f"{sheet} (Policy measures database)",
                        "publication": {
                            **publication,
                            "workbook_sheet": sheet,
                            "workbook_cell": reference,
                        },
                        "status": "ok",
                    }
                    if kind == "tax":
                        row["metric"] = "revenue_change"
                    else:
                        row["proposed_metric"] = "exchequer_impact"
                        conditions["impact_channel"] = "spending_measure"
                    rows.append(row)
                    counts["staged_original_cells"] += 1
                    counts[f"{kind}_cells"] += 1
                    events[event]["staged_original_cells"] += 1
    accounting = dict(counts)
    accounting["by_event"] = {
        event: {**dict(counts), "measures": len(titles[event])}
        for event, counts in events.items()
    }
    return rows, accounting


def staged_bytes(rows: list[dict]) -> bytes:
    """Use a stable row order and JSON encoding independent of retrieval time."""
    return "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows).encode()


def write_harvest(
    output_dir: Path, rows: list[dict], accounting: dict, receipt: dict
) -> dict:
    from .collect_obr_pmd import locked_source

    source = locked_source(receipt)
    output_dir.mkdir(parents=True, exist_ok=True)
    raw = staged_bytes(rows)
    # An empty filename and zero mtime make the gzip container reproducible.
    with (output_dir / "claims_staged.jsonl.gz").open("wb") as stream:
        with gzip.GzipFile(filename="", mode="wb", fileobj=stream, mtime=0) as zipped:
            zipped.write(raw)
    manifest = {
        "url": source["original_url"],
        "title": "Policy measures database (March 2026)",
        "date": "2026-03-26",
        "sha256": source["sha256"],
        "local_path": f"downloads/{Path(urlsplit(source['original_url']).path).name}",
        "doc_type": "costings_database",
        "access": "wayback_machine_original_bytes",
        "wayback_snapshot": source["archive_capture_url"],
        "bytes": source["byte_size"],
        "receipt_sha256": receipt["receipt_sha256"],
    }
    (output_dir / "manifest.jsonl").write_text(json.dumps(manifest) + "\n")
    audit = {
        **accounting,
        "staged_sha256": hashlib.sha256(raw).hexdigest(),
        "workbook_sha256": source["sha256"],
        "receipt_sha256": receipt["receipt_sha256"],
    }
    (output_dir / "staging_accounting.json").write_text(
        json.dumps(audit, indent=2, ensure_ascii=False) + "\n"
    )
    return audit


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workbook", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    receipt = json.loads(args.receipt.read_text())
    rows, accounting = stage_workbook(args.workbook, receipt)
    audit = write_harvest(args.output_dir, rows, accounting, receipt)
    print(json.dumps(audit, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
