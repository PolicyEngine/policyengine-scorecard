"""Adapter: California fiscal notes on young child tax credit (YCTC) bills
-> tidy rows (lane ca-fiscal-notes, issue #4).

Input (raw/, Assembly Committee on Revenue and Taxation bill analyses, as
fetched 2026-10-19 from arev.assembly.ca.gov; ftb.ca.gov and leginfo refuse
scripted fetches):
    arev_898_ab397.pdf   AB 397 (Mark González, et al.), as introduced
                         February 3, 2025; hearing April 28, 2025
    arev_969_ab1690.pdf  AB 1690 (Ahrens), as introduced February 3, 2026;
                         hearing March 16, 2026
Each analysis restates the Franchise Tax Board's estimate in its "FISCAL
EFFECT" paragraph: General Fund revenue losses by State fiscal year.
Output: data/externals/ca-fiscal-notes.json — one row per fiscal year.

Each row also carries the bill's YCTC age schedule, parsed from the
analysis's summary (the age below which a child qualifies, by tax year),
so the test can check the PolicyEngine reform encodes exactly that.

QC (any failure raises):
  1. the version line, the hearing date and the FISCAL EFFECT sentence each
     occur exactly once
  2. every estimate in the sentence is a revenue loss in a named fiscal
     year, and the years are consecutive
  3. the age schedule parses for every tax year the estimates cover

Run (needs pypdf; imported lazily so the parsing helpers stay importable
without it):
    uv run --with pypdf python sources/ca-fiscal-notes/adapter.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
OUT = HERE.parent.parent / "data" / "externals" / "ca-fiscal-notes.json"

BILLS = {
    "AB 397": "arev_898_ab397.pdf",
    "AB 1690": "arev_969_ab1690.pdf",
}
SCHEDULE_YEARS = range(2025, 2031)
_WORDS = {"five": 5, "six": 6, "seven": 7, "eight": 8}
_MONTHS = {
    m: i
    for i, m in enumerate(
        "January February March April May June July August September "
        "October November December".split(),
        start=1,
    )
}
EXPECTED_ROWS = 5


def _clean(text: str) -> str:
    """Collapse whitespace and fold curly quotes."""
    text = text.replace("“", '"').replace("”", '"').replace("’", "'")
    return re.sub(r"\s+", " ", text)


def _once(pattern: str, text: str, what: str) -> re.Match:
    found = list(re.finditer(pattern, text))
    if len(found) != 1:
        raise ValueError(f"QC failed: {what} found {len(found)} times")
    return found[0]


def _iso(month: str, day: str, year: str) -> str:
    return f"{year}-{_MONTHS[month]:02d}-{int(day):02d}"


def parse_estimates(text: str) -> tuple[str, list[tuple[str, float]]]:
    """(sentence, [(fiscal year 'YYYY-YY', revenue change in dollars)])."""
    m = _once(r"FISCAL EFFECT: The FTB estimates [^.]*\.", text, "FISCAL EFFECT")
    sentence = m.group(0)
    if "revenue losses of" not in sentence:
        raise ValueError(f"QC failed: not a revenue loss: {sentence!r}")
    pairs = re.findall(
        r"\$(\d+(?:\.\d+)?) (million|billion) in (?:fiscal year \(FY\)|FY) "
        r"(\d{4}-\d{2})",
        sentence,
    )
    if not pairs:
        raise ValueError(f"QC failed: no estimates in {sentence!r}")
    scale = {"million": 1e6, "billion": 1e9}
    out = [(fy, -float(v) * scale[unit]) for v, unit, fy in pairs]
    starts = [int(fy[:4]) for fy, _ in out]
    if starts != list(range(starts[0], starts[0] + len(starts))):
        raise ValueError(f"QC failed: fiscal years not consecutive: {starts}")
    return sentence, out


def parse_schedule(text: str) -> dict[int, int]:
    """{tax year: age below which a child qualifies} over SCHEDULE_YEARS.
    Two drafting forms: explicit bands ('less than 10 years of age') and an
    'age increase factor' added to a base age."""
    bands = re.findall(
        r"For taxable years beginning on or after January 1, (\d{4})"
        r"(?:, and before January 1, (\d{4}))?, less than (\d+) years of age",
        text,
    )
    factor = re.search(
        r"For taxable years beginning on or after January 1, (\d{4}), and "
        r"before January 1, (\d{4}), younger than (\w+) years of age plus the "
        r'"age increase factor"',
        text,
    )
    schedule: dict[int, int] = {}
    if factor:
        start, end, base = int(factor.group(1)), int(factor.group(2)), factor.group(3)
        origin = _once(
            r"elapsed between January 1, (\d{4}), and the last day of the "
            r"applicable taxable year",
            text,
            "age increase factor origin",
        )
        zero = int(origin.group(1))
        for year in range(start, end):
            # whole calendar years from January 1 of `zero` to December 31
            # of `year`
            schedule[year] = _WORDS[base.lower()] + (year - zero)
    for start, end, age in bands:
        stop = int(end) if end else max(SCHEDULE_YEARS) + 1
        for year in range(int(start), stop):
            schedule[year] = int(age)
    return {y: a for y, a in sorted(schedule.items()) if y in SCHEDULE_YEARS}


def parse_bill(bill: str, text: str) -> list[dict]:
    version = _once(
        re.escape(bill) + r" \(([^)]+)\) – As Introduced ([A-Z][a-z]+) (\d+), (\d{4})",
        text,
        f"{bill} version line",
    )
    hearing = _once(
        r"Date of Hearing: ([A-Z][a-z]+) (\d+), (\d{4})", text, "hearing date"
    )
    sentence, estimates = parse_estimates(text)
    schedule = parse_schedule(text)
    rows = []
    for fy, value in estimates:
        tax_year = int(fy[:4])
        if tax_year not in schedule:
            raise ValueError(f"QC failed: {bill} has no age for tax year {tax_year}")
        rows.append(
            {
                "source": "ca-fiscal-notes",
                "country": "US",
                "bill": bill,
                "authors": version.group(1),
                "version": "introduced",
                "version_date": _iso(*version.group(2, 3, 4)),
                "hearing_date": _iso(*hearing.group(1, 2, 3)),
                "estimator": "FTB",
                "publisher": "Assembly Committee on Revenue and Taxation",
                "metric": "revenue_change",
                "geography": "CA",
                "unit_concept": "usd",
                "period": f"FY {fy}",
                "value": value,
                "status": "ok",
                "age_schedule": {str(y): a for y, a in schedule.items()},
                "source_column": f"{BILLS[bill]}: {sentence}",
            }
        )
    return rows


def _pdf_text(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as e:
        raise SystemExit("this adapter needs pypdf: uv run --with pypdf ...") from e
    return _clean(" ".join(p.extract_text() for p in PdfReader(path).pages))


def run() -> list[dict]:
    rows = []
    for bill, name in BILLS.items():
        rows += parse_bill(bill, _pdf_text(RAW / name))
    if len(rows) != EXPECTED_ROWS:
        raise SystemExit(f"row contract broken: {len(rows)} != {EXPECTED_ROWS}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rows, indent=1, ensure_ascii=False) + "\n")
    return rows


if __name__ == "__main__":
    out = run()
    print(f"wrote {len(out)} rows to {OUT}")
