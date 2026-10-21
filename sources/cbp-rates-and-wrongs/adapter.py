"""Adapter: Centre for British Progress, "Rates and wrongs" technical
appendix (25 March 2026), Tables 2 and 3 -> tidy rows (lane
uk-childcare-100k).

Input (raw/):
    rates_and_wrongs_technical_appendix.pdf
        the technical appendix as published (19 pages), pinned by sha256
    pages_layout.txt
        ``pdftotext -layout`` (poppler 26.09.0) of PDF pages 1, 3, 4, 5, 8
        and 10, each under a ``=== PDF page N ===`` header; pinned by sha256
Output: data/externals/cbp-rates-and-wrongs.json

Rows: section 1 (free childcare hours and Tax-Free Childcare), Table 2
(endogenous pension, exogenous labour; PDF page 8) and Table 3 (endogenous
labour, no pension; PDF page 10): "Projected Net Fiscal Impact of Childcare
Entitlements (£bn)" for abolishing the cliff and for tapers of 1% to 5%,
financial years 2026/27 to 2031/32. 2 tables x 6 policies x 6 years = 72
rows, values in pounds (£bn x 1e9) as printed. The appendix states no sign
rule; the values are carried as printed.

Years: the column labels are financial years ("2026/27"); ``period`` is the
end year (the repo's UK convention) and ``fy`` the label ("2026-27").

QC (any failure raises):
  1. the PDF and the extract match their source.json digests
  2. each table parses to exactly the six policies, in order, each with
     six values, under the six year columns 2026/27 .. 2031/32
  3. each table carries its own model title and the note "full utilisation
     of FCWP and £500 utilisation of TFC"
  4. within each year, the published values rise with the taper rate
     (abolish < 1% < ... < 5%), the ordering the appendix's model implies
     for a surcharge added on top of an abolished cliff (section 1.3.6);
     a parse that shifted a column would break it

Run (stdlib only):
    python sources/cbp-rates-and-wrongs/adapter.py
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
OUT = HERE.parent.parent / "data" / "externals" / "cbp-rates-and-wrongs.json"
PDF = RAW / "rates_and_wrongs_technical_appendix.pdf"
PAGES = RAW / "pages_layout.txt"

TABLES = {
    "2": {
        "page": 8,
        "title": "Table 2: Projected Net Fiscal Impact of Childcare Entitlements (£bn): Endoge-",
        "model": "endogenous_pension_exogenous_labour",
        "model_label": "Endogenous Pension, Exogenous Labour",
        "assumptions": "full utilisation of FCWP and £500 utilisation of TFC; friction parameter £1000",
        "note": "It also assumes a friction parameter of £1000.",
    },
    "3": {
        "page": 10,
        "title": "Table 3: Projected Net Fiscal Impact of Childcare Entitlements (£bn): Endoge-",
        "model": "endogenous_labour_no_pension",
        "model_label": "Endogenous Labour, No Pension",
        "assumptions": "full utilisation of FCWP and £500 utilisation of TFC; friction parameter £1000; Frisch elasticity 0.3",
        "note": "It also assumes a friction parameter of £1000 and Frisch elasticity of 0.3.",
    },
}
POLICIES = (
    ("Abolish Cliff", "abolish_cliff"),
    ("1%", "taper_1pct"),
    ("2%", "taper_2pct"),
    ("3%", "taper_3pct"),
    ("4%", "taper_4pct"),
    ("5%", "taper_5pct"),
)
YEAR_LABELS = ("2026/27", "2027/28", "2028/29", "2029/30", "2030/31", "2031/32")
NOTE = "This assumes full utilisation of FCWP and £500 utilisation of TFC."
EXPECTED_ROWS = len(TABLES) * len(POLICIES) * len(YEAR_LABELS)
_VALUE = r"\d+\.\d+"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_digests() -> None:
    """QC 1."""
    spec = json.loads((HERE / "source.json").read_text())["raw_sha256"]
    for path in (PDF, PAGES):
        got = sha256(path)
        if got != spec[path.name]:
            raise ValueError(
                f"QC failed: {path.name} sha256 {got} != {spec[path.name]}"
            )


def pages() -> dict[int, str]:
    out: dict[int, str] = {}
    current = None
    for line in PAGES.read_text().splitlines(keepends=True):
        m = re.match(r"=== PDF page (\d+) ===$", line.rstrip("\n"))
        if m:
            current = int(m.group(1))
            out[current] = ""
            continue
        if current is None:
            raise ValueError("QC failed: extract text before the first page header")
        out[current] += line
    return out


def parse_table(number: str, text: str) -> dict[str, list[tuple[str, float]]]:
    """QC 2-3: {policy: [(verbatim, value) per year]}."""
    spec = TABLES[number]
    start = text.index(spec["title"])
    end = text.index(NOTE, start)
    block = text[start:end]
    title = " ".join(text[start : start + 200].split()).replace(
        "Endoge- nous", "Endogenous"
    )
    if spec["model_label"] not in title:
        raise ValueError(
            f"QC failed: Table {number} title lacks {spec['model_label']!r}"
        )
    header = next(line for line in block.splitlines() if "Taper Rate" in line)
    if header.split()[2:] != list(YEAR_LABELS):
        raise ValueError(f"QC failed: Table {number} year columns {header.split()[2:]}")
    out = {}
    body = [line for line in block.splitlines() if re.search(_VALUE, line)]
    if len(body) != len(POLICIES):
        raise ValueError(f"QC failed: Table {number} has {len(body)} value rows")
    for line, (label, key) in zip(body, POLICIES):
        stripped = line.strip()
        if not stripped.startswith(label):
            raise ValueError(
                f"QC failed: Table {number} row {stripped!r} is not {label!r}"
            )
        cells = re.findall(_VALUE, stripped.removeprefix(label))
        if len(cells) != len(YEAR_LABELS):
            raise ValueError(
                f"QC failed: Table {number} {label} has {len(cells)} values"
            )
        out[key] = [(c, float(c)) for c in cells]
    note = " ".join(text[end : end + 300].split())
    if not note.startswith(f"{NOTE} {spec['note']}"):
        raise ValueError(f"QC failed: Table {number} note changed: {note[:160]!r}")
    return out


def check_order(number: str, table: dict) -> None:
    """QC 4."""
    for i, label in enumerate(YEAR_LABELS):
        column = [table[key][i][1] for _, key in POLICIES]
        if column != sorted(column) or len(set(column)) != len(column):
            raise ValueError(
                f"QC failed: Table {number} {label} not rising with the taper"
            )


def tidy(number: str, table: dict) -> list[dict]:
    spec = TABLES[number]
    rows = []
    for label, key in POLICIES:
        for (verbatim, value), year_label in zip(table[key], YEAR_LABELS):
            start, end = year_label.split("/")
            rows.append(
                {
                    "source": "cbp-rates-and-wrongs",
                    "country": "UK",
                    "table": number,
                    "pdf_page": spec["page"],
                    "model": spec["model"],
                    "policy": key,
                    "fy": f"{start}-{end}",
                    "period": int(start[:2] + end),
                    "unit_concept": "gbp",
                    "value": round(value * 1e9),
                    "value_verbatim": verbatim,
                    "assumptions": spec["assumptions"],
                    "status": "ok",
                    "source_column": (
                        f"Technical appendix Table {number} ({spec['model_label']}), "
                        f"{label}, {year_label}"
                    ),
                }
            )
    return rows


def run() -> list[dict]:
    check_digests()
    text = pages()
    rows = []
    for number, spec in TABLES.items():
        table = parse_table(number, text[spec["page"]])
        check_order(number, table)
        rows += tidy(number, table)
    if len(rows) != EXPECTED_ROWS:
        raise SystemExit(f"row contract broken: {len(rows)} != {EXPECTED_ROWS}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rows, indent=1, ensure_ascii=False) + "\n")
    return rows


if __name__ == "__main__":
    out = run()
    print(f"wrote {len(out)} rows to {OUT}")
