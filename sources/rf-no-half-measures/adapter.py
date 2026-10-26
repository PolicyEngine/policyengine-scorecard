"""Adapter: Resolution Foundation, "No half measures: Setting child poverty on
a downward course at the Autumn Budget" (Clegg and Judge, 30 October 2025)
-> tidy rows (lane uk-two-child-limit-poverty).

Input (raw/), each pinned by sha256 in source.json:
    No-half-measures_v2.pdf
        the spotlight as published (9 pages)
    Living-Standards-Outlook-2024.pdf
        Clegg and Corlett, The Living Standards Outlook 2024 (August 2024),
        whose Annex (pages 34-37) the spotlight cites for its projection
        method (footnote 4)
    pages_layout.txt
        ``pdftotext -layout`` (poppler 26.09.0) of the spotlight's nine
        pages and the annex's four, each under a ``=== <file> page N ===``
        header
Output: data/externals/rf-no-half-measures.json

Rows (7): the spotlight's two-child limit figures, all for the UK, relative
child poverty after housing costs unless stated:
  - scrap the limit in full: 480,000 fewer children in poverty in 2029-30
    "than the counterfactual" (page 3), at a cost of £3.5 billion (page 3),
    330,000 fewer "today" (2025-26) and "a further 150,000 ... by 2029-30"
    (page 1)
  - the partial repeals of endnote 8 (page 9), each against the
    current-policy projection for 2029-30: a three-child limit 350,000, a
    third-and-later child element at two-thirds of the standard rate
    340,000, the limit lifted for families in work only 330,000
Each is already a claim of the Autumn Budget 2025 harvest
(sources/harvest-uk-ab2025-2026-09-24/uk_rf_ab2025); the ingest matches
every row to exactly one such claim rather than minting a second one, so
``measure_key``, ``metric`` and the value here are those claims'.

Not staged: £7,280 per child lifted (the cost divided by the 480,000; QC
3) and the figures that are not two-child-limit reform scores (the baseline
rates and counts, the free school meals and benefit-cap packages, Figure 3's
year-by-year bars and Figure 5's parliaments).

Years: RF names financial years ("2029-30"); ``period`` is the end year,
the repo's UK convention, and ``fy`` the label.

QC (any failure raises):
  1. every raw file matches its source.json digest
  2. the extract holds the spotlight's pages 1-9 and the annex's pages 34-37
  3. 330,000 + 150,000 = 480,000, and £3.5 billion / 480,000 is within 1%
     of the £7,280 per child the spotlight prints (both figures rounded)
  4. the method statements the annotations rest on are present: modelled
     policy changes occur in April 2026; the Scottish Government's
     mitigation is excluded; the projection uses the IPPR Tax Benefit
     Model, OBR March 2025 earnings and the Bank of England's August 2025
     CPI forecast (footnote 4, which cites the LSO 2024 Annex); the annex
     reweights "the numbers of dependent children of each age" and holds
     Universal Credit take-up at 80 per cent, unchanged "between years (or
     scenarios)"

Run (stdlib only):
    python sources/rf-no-half-measures/adapter.py
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
OUT = HERE.parent.parent / "data" / "externals" / "rf-no-half-measures.json"
SPOTLIGHT = RAW / "No-half-measures_v2.pdf"
LSO = RAW / "Living-Standards-Outlook-2024.pdf"
PAGES = RAW / "pages_layout.txt"
RAW_FILES = (SPOTLIGHT, LSO, PAGES)
WANT_PAGES = {
    SPOTLIGHT.name: list(range(1, 10)),
    LSO.name: [34, 35, 36, 37],
}
PER_CHILD_TOLERANCE = 0.01

# (measure_key, metric, fy, value, page, the sentence it is read from)
ROWS = (
    (
        "ab2025_option__scrap_two_child_limit",
        "poverty_count_change",
        "2029-30",
        480_000,
        3,
        r"would result in an estimated (480,000) fewer children growing in poverty "
        r"in 2029-30 than the counterfactual",
    ),
    (
        "ab2025_option__scrap_two_child_limit",
        "benefit_cost_change",
        "2029-30",
        3_500_000_000,
        3,
        r"than the counterfactual, at a cost of £(3\.5) billion",
    ),
    (
        "ab2025_option__scrap_two_child_limit",
        "poverty_count_change",
        "2025-26",
        330_000,
        1,
        r"reduce the number of children growing up in poverty by (330,000) today",
    ),
    (
        "ab2025_option__scrap_two_child_limit",
        "poverty_count_change",
        "2029-30",
        150_000,
        1,
        r"and save a further (150,000) children from that fate by 2029-30",
    ),
    (
        "ab2025_option__three_child_limit",
        "poverty_count_change",
        "2029-30",
        350_000,
        9,
        r"moving to a three-child limit would reduce child poverty by (350,000) in "
        r"2029-30 compared to our projection for that year based on current policy",
    ),
    (
        "ab2025_option__two_child_limit_partial_child_element_for_third_plus_children",
        "poverty_count_change",
        "2029-30",
        340_000,
        9,
        r"\(at two-thirds of the standard child element\) would bring the number down "
        r"by (340,000)",
    ),
    (
        "ab2025_option__two_child_limit_exempt_working_families",
        "poverty_count_change",
        "2029-30",
        330_000,
        9,
        r"scrapping the two-child limit only for families in work would reduce child "
        r"poverty by (330,000) by that date",
    ),
)
# A footnote number pdftotext lifts into the running text, matched in a
# METHOD phrase where it falls.
FOOTNOTE_MARK = "<fn>"
METHOD = (
    (SPOTLIGHT.name, "Modelled policy changes occur in April 2026."),
    (
        SPOTLIGHT.name,
        "Does not include the Scottish Government’s intention to mitigate the "
        "two-child limit from April 2026.",
    ),
    (SPOTLIGHT.name, "RF projections including use of the IPPR Tax Benefit Model"),
    (
        SPOTLIGHT.name,
        "Full details of our projection methodology are available in the Annex of "
        "A Clegg and A Corlett, The Living Standards Outlook 2024",
    ),
    (
        SPOTLIGHT.name,
        "We use the OBR’s projection for earnings growth from its March 2025 "
        "Economic and Fiscal Outlook. Our starting point in accounting for inflation "
        "is the Bank of England’s August 2025 CPI forecast",
    ),
    (
        LSO.name,
        # pdftotext sets the annex's footnote 27 marker inside this sentence
        "This includes modelling changes in the numbers of dependent"
        + FOOTNOTE_MARK
        + " children of each age.",
    ),
    (
        LSO.name,
        "80 per cent take-up of Universal Credit. We assume that these figures do "
        "not change between years (or scenarios).",
    ),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_digests() -> None:
    """QC 1."""
    spec = json.loads((HERE / "source.json").read_text())["raw_sha256"]
    for path in RAW_FILES:
        got = sha256(path)
        if got != spec[path.name]:
            raise ValueError(
                f"QC failed: {path.name} sha256 {got} != {spec[path.name]}"
            )


def pages() -> dict[tuple[str, int], str]:
    """{(file, page): whitespace-collapsed text} from the extract (QC 2)."""
    out: dict[tuple[str, int], list[str]] = {}
    current = None
    for line in PAGES.read_text().splitlines():
        m = re.fullmatch(r"=== (\S+\.pdf) page (\d+) ===", line)
        if m:
            current = (m.group(1), int(m.group(2)))
            out[current] = []
        elif current is not None:
            out[current].append(line)
    found = {}
    for name, page in out:
        found.setdefault(name, []).append(page)
    if found != WANT_PAGES:
        raise ValueError(f"QC failed: extract pages {found}")
    return {k: " ".join(" ".join(v).split()) for k, v in out.items()}


def read_rows(text: dict[tuple[str, int], str]) -> list[dict]:
    rows = []
    for measure, metric, fy, value, page, pattern in ROWS:
        m = re.search(pattern, text[(SPOTLIGHT.name, page)])
        if not m:
            raise ValueError(f"QC failed: page {page} lacks {pattern!r}")
        printed = m.group(1)
        parsed = (
            float(printed) * 1e9
            if metric == "benefit_cost_change"
            else int(printed.replace(",", ""))
        )
        if parsed != value:
            raise ValueError(f"QC failed: page {page} prints {printed}, not {value}")
        end = int(fy[:4]) + 1
        rows.append(
            {
                "source": "rf-no-half-measures",
                "country": "UK",
                "measure_key": measure,
                "metric": metric,
                "fy": fy,
                "period": end,
                "value": float(value),
                "value_verbatim": " ".join(m.group(0).split()),
                "page": page,
                "unit_concept": "gbp"
                if metric == "benefit_cost_change"
                else "children",
                "status": "ok",
                "source_column": f"No half measures, page {page}",
            }
        )
    return rows


def check_arithmetic(rows: list[dict], text: dict) -> None:
    """QC 3."""
    scrap = {
        (r["metric"], r["fy"], r["page"]): r["value"]
        for r in rows
        if r["measure_key"] == "ab2025_option__scrap_two_child_limit"
    }
    if (
        scrap[("poverty_count_change", "2025-26", 1)]
        + scrap[("poverty_count_change", "2029-30", 1)]
        != scrap[("poverty_count_change", "2029-30", 3)]
    ):
        raise ValueError("QC failed: 330,000 + 150,000 != 480,000")
    m = re.search(
        r"\(or £([\d,]+) per child lifted out of poverty\)", text[(SPOTLIGHT.name, 3)]
    )
    if not m:
        raise ValueError("QC failed: per-child cost missing")
    per_child = int(m.group(1).replace(",", ""))
    ratio = (
        scrap[("benefit_cost_change", "2029-30", 3)]
        / scrap[("poverty_count_change", "2029-30", 3)]
    )
    if abs(ratio / per_child - 1) > PER_CHILD_TOLERANCE:
        raise ValueError(
            f"QC failed: £3.5bn / 480,000 = {ratio:.0f}, printed {per_child}"
        )


def check_method(text: dict) -> None:
    """QC 4."""
    by_file: dict[str, str] = {}
    for (name, _), page in sorted(text.items()):
        by_file[name] = by_file.get(name, "") + " " + page
    for name, phrase in METHOD:
        pattern = r"(?: \d+)?".join(map(re.escape, phrase.split(FOOTNOTE_MARK)))
        if not re.search(pattern, by_file[name]):
            raise ValueError(f"QC failed: {name} lacks {phrase!r}")


def run() -> list[dict]:
    check_digests()
    text = pages()
    rows = read_rows(text)
    check_arithmetic(rows, text)
    check_method(text)
    if len(rows) != len(ROWS):
        raise SystemExit(f"row contract broken: {len(rows)} != {len(ROWS)}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rows, indent=1, ensure_ascii=False) + "\n")
    return rows


if __name__ == "__main__":
    out = run()
    print(f"wrote {len(out)} rows to {OUT}")
