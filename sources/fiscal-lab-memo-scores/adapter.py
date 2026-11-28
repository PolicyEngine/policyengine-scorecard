"""Adapter: Fiscal Lab's Memo Bill Scores -> per-bill extract (lane
fiscal-lab-memo-scores).

On 2026-11-24 Fiscal Lab on Capitol Hill published estimates for all 110
items, bills and proposals alike, that the Cost-of-Living Healthcare Working
Group's memo of September 1, 2026 sent to Leader Jeffries. The scores live on one dashboard
page, which embeds its data as ``const DATA = {...}`` and builds its
"Download table (CSV)" in the browser from that data. The CSV therefore has
no URL of its own.

Terms. Fiscal Lab's Terms of Use (effective 2026-11-16, section 5) say its
publications are its own, allow links and short excerpts with attribution,
and ask anyone republishing to contact it first. So this repository commits
no Fiscal Lab file: not the page and not the CSV. ``fetch`` saves the live
page to raw/ (git-ignored), replacing the pinned copy only when the page
matches its pinned hash. ``build`` checks the page against the sha256
pinned in source.json, rebuilds the CSV byte for byte as the page's own
``summaryCsv()`` does and checks that hash too, runs the QC, and writes
data/externals/fiscal-lab-memo-scores.json. The CSV's closing source line
is read from the page's own code at build time, so this file holds none of
it. Per bill the extract holds the identifiers and title, Fiscal Lab's model
labels and effect label, the FY2027-2036 total as the CSV prints it, the low
and high cases where the bill has a range, a link to the bill on the
dashboard and the congress.gov link the page gives. H.R. 4849 also carries
its superseded values from the November 21 build. Annual paths, components,
coverage and State tables, notes and narrative stay out.

QC (any failure raises):
  1. the page's sha256 and DATA.built equal source.json's pins
  2. 110 bills with unique slugs; DATA.years is FY2027 to FY2036
  3. the rebuilt CSV's sha256 equals the CSV captured from the page
  4. per bill, the ten annual figures add to the ten-year figure
  5. per bill and year, the deficit equals direct spending less revenue
  6. a bill with a range has low <= central <= high
  7. the zero flag holds exactly when the central figure is zero, and the
     CSV's effect label agrees with the sign
  8. H.R. 4849, the one bill revised after the release, has a changelog
     entry whose structured before and after figures match the superseded
     and current values the extract records
  9. per bill, the score table's total row carries the central figure; on a
     bill with a range, the headline low and high equal that row's or its
     rounding to $0.1 billion. The bills where Fiscal Lab rounded them are
     pinned in RANGE_ROUNDED and flagged ``range_rounded`` in the extract

Usage (stdlib only):
    python sources/fiscal-lab-memo-scores/adapter.py fetch
    python sources/fiscal-lab-memo-scores/adapter.py build [--dashboard PATH]
    python sources/fiscal-lab-memo-scores/adapter.py check [--dashboard PATH]

``check`` rebuilds the extract and fails if it differs from the committed
one. A new Fiscal Lab build changes the page hash, so it fails ``build``
until source.json is updated on purpose.
"""

from __future__ import annotations

import argparse
import errno
import hashlib
import json
import os
import re
import sys
import tempfile
import urllib.request
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
SOURCE_JSON = HERE / "source.json"
RAW = HERE / "raw"
DEFAULT_DASHBOARD = RAW / "dashboard.html"
OUT = REPO / "data" / "externals" / "fiscal-lab-memo-scores.json"

YEARS = list(range(2027, 2037))
WINDOW = "FY2027-2036"
N_BILLS = 110
ROMAN = {
    "I": 1,
    "II": 2,
    "III": 3,
    "IV": 4,
    "V": 5,
    "VI": 6,
    "VII": 7,
    "VIII": 8,
    "IX": 9,
    "X": 10,
}
# The page's EFFECT labels (const EFFECT) by effectOf(b).
EFFECT = {
    "cost": "adds to deficits",
    "save": "reduces deficits",
    "zero": "no significant effect",
    "none": "not estimated",
}
KINDS = {"bill", "proposal", "resolution"}
# The fields every row of the committed extract carries, in order. _row adds
# only the optional range_rounded and superseded fields after them.
ROW_FIELDS = (
    "slug",
    "bill",
    "kind",
    "congress",
    "version",
    "title",
    "models",
    "window",
    "central",
    "low",
    "high",
    "effect",
    "url",
    "bill_url",
)
# H.R. 4849 as released on 2026-11-24 (the November 21 build), before the
# November 25 revision. The adapter checks these against the changelog
# entry's before and after figures; `--release` also checks them against
# that build's page.
SUPERSEDED = {
    "H_R_4849": {
        "build": "November 21, 2026",
        "central": "2008.089",
        "low": "1551.100",
        "high": "2225.425",
        "changelog_id": "2026-11-25-hr4849-sections",
    }
}
# Bills whose headline low and high (DATA.low/high, which the CSV prints) are
# the score table's total row rounded to $0.1 billion rather than the row
# itself. QC 9 recomputes this set and fails if it moves.
RANGE_ROUNDED = frozenset(
    {"H_J_Res_189", "H_R_3521", "H_R_5343", "H_R_7920", "H_R_7961", "S_1096"}
)
_BILL_URL = re.compile(
    r"^https://www\.congress\.gov/bill/(\d+)(?:st|nd|rd|th)-congress/"
    r"(house-bill|senate-bill|house-joint-resolution)/(\d+)$"
)
_TEXT_URL = re.compile(r"^https://www\.congress\.gov/(\d+)/bills/[a-z]+\d+/")
_OLD_CONGRESS = re.compile(r"\bof the (\d+)(?:st|nd|rd|th) Congress;")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_source() -> dict:
    return json.loads(SOURCE_JSON.read_text())


def pin(source: dict, raw_id: str) -> dict:
    hits = [r for r in source["raw"] if r["id"] == raw_id]
    if len(hits) != 1:
        raise ValueError(f"source.json: expected one raw entry {raw_id!r}")
    return hits[0]


def extract_data(html: str) -> dict:
    """The page's embedded ``const DATA = {...}`` object, brace-matched
    over JSON string syntax (the object is strict JSON)."""
    start = html.index("{", html.index("const DATA ="))
    depth, in_str, esc = 0, False, False
    for k in range(start, len(html)):
        c = html[k]
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
        elif c == '"':
            in_str = True
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return json.loads(html[start : k + 1])
    raise ValueError("unterminated DATA object")


def to_fixed3(value: float | None) -> str:
    """JavaScript's ``(+v).toFixed(3)`` on a finite number: the exact
    binary value, ties away from zero; -0 prints as 0.000. ``None`` is the
    page's empty cell."""
    if value is None:
        return ""
    if value == 0:
        return "0.000"
    return str(Decimal(value).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP))


def effect_of(bill: dict) -> str:
    if bill["figure"] is None:
        return "none"
    if bill["zero"]:
        return "zero"
    return "cost" if bill["figure"] > 0 else "save"


def _csv_cell(value) -> str:
    text = str(value)
    if any(c in text for c in '",\r\n'):
        return '"' + text.replace('"', '""') + '"'
    return text


def memo_order(bills: list[dict]) -> list[dict]:
    """The page's default sort ("memo"): memo section, then memo order."""
    order = sorted(
        enumerate(bills), key=lambda t: (ROMAN.get(t[1]["section_no"], 99), t[0])
    )
    return [b for _, b in order]


_FOOTER_CALL = 'lines.push("", q('


def csv_footer(html: str, built: str) -> str:
    """The CSV's closing source line, read from the page's own
    ``summaryCsv()``: the template literals joined by ``+`` inside its
    ``lines.push("", q(...))``, with ``${DATA.built}`` filled in. Reading it
    keeps Fiscal Lab's sentence out of this repository."""
    fn = html.index("function summaryCsv")
    body_end = html.index("\n}\n", fn)
    k = html.index(_FOOTER_CALL, fn) + len(_FOOTER_CALL)
    if k > body_end:
        raise ValueError("summaryCsv footer call not found in summaryCsv")
    parts = []
    while True:
        while html[k].isspace():
            k += 1
        if html[k] != "`":
            raise ValueError("summaryCsv footer: expected a template literal")
        end = html.index("`", k + 1)
        parts.append(html[k + 1 : end])
        k = end + 1
        while html[k].isspace():
            k += 1
        if html[k] == "+":
            k += 1
            continue
        if html[k] == ")":
            break
        raise ValueError(f"summaryCsv footer: unexpected {html[k]!r}")
    text = "".join(parts)
    if "\\" in text or text.count("${DATA.built}") != 1:
        raise ValueError("summaryCsv footer: template changed shape")
    text = text.replace("${DATA.built}", built)
    if "${" in text:
        raise ValueError("summaryCsv footer: unknown substitution")
    return text


def summary_csv(data: dict, footer: str) -> bytes:
    """The bytes of the page's "Download table (CSV)" with no filter set,
    as ``summaryCsv()`` builds them (BOM, CRLF, trailing source line, which
    the caller reads from the page with ``csv_footer``)."""
    head = [
        "Bill",
        "Title",
        "Sponsor",
        "Memo section",
        "Memo timing",
        *[f"FY{y}" for y in data["years"]],
        "FY2027-2036",
        "Low",
        "High",
        "Effect",
    ]
    lines = [",".join(_csv_cell(h) for h in head)]
    for b in memo_order(data["bills"]):
        section = (
            f"{b['section_no']}. {b['section']}" if b["section_no"] else b["section"]
        )
        cells = [
            "Proposal" if b["is_concept"] else b["label"],
            b["title"],
            b["sponsor"] or "",
            section,
            b["timing"] or "",
            *[to_fixed3(v) for v in b["glance"]["deficit"]],
            to_fixed3(b["figure"]),
            to_fixed3(b["low"]) if b["has_range"] else "",
            to_fixed3(b["high"]) if b["has_range"] else "",
            EFFECT[effect_of(b)],
        ]
        lines.append(",".join(_csv_cell(c) for c in cells))
    lines.append("")
    lines.append(_csv_cell(footer))
    return ("﻿" + "\r\n".join(lines) + "\r\n").encode("utf-8")


def _congress_and_version(b: dict) -> tuple[str | None, str]:
    notes = b["glance"]["notes"]
    version = "memo_description" if "as the memo describes it" in notes else None
    if version is None and f"{b['label']}, as introduced;" in notes:
        version = "introduced"
    m = _BILL_URL.match(b["url"] or "") or _TEXT_URL.match(b["url"] or "")
    congress = m.group(1) if m else None
    old = _OLD_CONGRESS.search(notes.split(";")[0] + ";")
    if old:
        if congress not in (None, old.group(1)):
            raise ValueError(f"{b['slug']}: Congress in URL and notes disagree")
        congress = old.group(1)
        version = version or "introduced"
    if version is None:
        raise ValueError(f"{b['slug']}: no version clause in the notes")
    return congress, version


def _close(a: float, b: float, tol: float, what: str) -> None:
    if abs(a - b) > tol:
        raise ValueError(f"QC failed: {what}: {a} vs {b}")


def qc_bill(b: dict) -> None:
    g = b["glance"]
    if len(g["deficit"]) != len(YEARS):
        raise ValueError(f"QC failed: {b['slug']} has {len(g['deficit'])} years")
    _close(sum(g["deficit"]), b["figure"], 1e-6, f"{b['slug']} annual sum")
    for i, year in enumerate(YEARS):
        _close(
            g["direct"][i] - g["revenue"][i],
            g["deficit"][i],
            1e-6,
            f"{b['slug']} FY{year} direct - revenue",
        )
    if b["has_range"] and not (b["low"] <= b["figure"] <= b["high"]):
        raise ValueError(f"QC failed: {b['slug']} range does not bracket central")
    if b["zero"] != (b["figure"] == 0):
        raise ValueError(f"QC failed: {b['slug']} zero flag")


def _on_tenth(value: float) -> bool:
    return abs(value * 10 - round(value * 10)) < 1e-6


def qc_range_table(b: dict) -> bool:
    """QC 9. Returns whether the headline range is the score table's total
    rounded to $0.1 billion (True) or the total itself (False)."""
    rows = (b.get("t2") or {}).get("rows") or []
    totals = [r for r in rows if r.get("total")]
    if not totals:
        if b["has_range"]:
            raise ValueError(f"QC failed: {b['slug']} has a range but no total row")
        return False
    if len(totals) != 1 or rows[-1] is not totals[0]:
        raise ValueError(f"QC failed: {b['slug']} score table total row")
    total = totals[0]
    _close(total["central"], b["figure"], 1e-9, f"{b['slug']} table total central")
    if not b["has_range"]:
        return False
    rounded = False
    for side in ("low", "high"):
        shown, exact = b[side], total[side]
        if abs(shown - exact) <= 1e-9:
            continue
        if not _on_tenth(shown) or abs(shown - exact) > 0.05 + 1e-9:
            raise ValueError(
                f"QC failed: {b['slug']} {side} {shown} is neither the table "
                f"total {exact} nor its rounding to 0.1"
            )
        rounded = True
    return rounded


def _row(b: dict) -> dict:
    congress, version = _congress_and_version(b)
    if b["thing"] not in KINDS:
        raise ValueError(f"{b['slug']}: unknown kind {b['thing']!r}")
    if b["is_concept"] != (b["thing"] == "proposal"):
        raise ValueError(f"{b['slug']}: proposal flag disagrees with kind")
    row = {
        "slug": b["slug"],
        "bill": None if b["is_concept"] else b["label"],
        "kind": b["thing"],
        "congress": congress,
        "version": version,
        "title": b["title"],
        "models": list(b["models"]),
        "window": WINDOW,
        "central": to_fixed3(b["figure"]),
        "low": to_fixed3(b["low"]) if b["has_range"] else None,
        "high": to_fixed3(b["high"]) if b["has_range"] else None,
        "effect": EFFECT[effect_of(b)],
        "url": (
            "https://fiscallab.org/score/healthcare-working-group-memo-scores/"
            f"dashboard.html#{b['slug']}"
        ),
        "bill_url": b["url"] or None,
    }
    assert tuple(row) == ROW_FIELDS
    if qc_range_table(b):
        row["range_rounded"] = True
    if b["slug"] in SUPERSEDED:
        row["superseded"] = dict(SUPERSEDED[b["slug"]])
    return row


def _bn_text(text: str) -> float:
    return float(text.replace(",", ""))


def qc_superseded(data: dict, rows: list[dict]) -> None:
    """Every revised bill has a changelog entry whose structured before and
    after figures (to $0.1 billion) match the superseded and current values
    the extract records. The entry's prose is not read."""
    by_slug = {r["slug"]: r for r in rows}
    entries = {e["id"]: e for e in data.get("changelog", [])}
    for slug, sup in SUPERSEDED.items():
        entry = entries.get(sup["changelog_id"])
        if entry is None:
            raise ValueError(f"QC failed: no changelog entry {sup['changelog_id']}")
        row = by_slug[slug]
        if entry.get("bill") != row["bill"]:
            raise ValueError(f"QC failed: changelog entry names {entry.get('bill')!r}")
        for side, values in (("before", sup), ("after", row)):
            got = entry.get(side) or {}
            if set(got) != {"central", "low", "high"}:
                raise ValueError(f"QC failed: {slug} changelog {side} figures")
            for case in ("central", "low", "high"):
                _close(
                    _bn_text(values[case]),
                    got[case],
                    0.05,
                    f"{slug} {side} {case} vs changelog",
                )


def qc_release(release_html: str) -> None:
    """The superseded values equal the November 21 build's own figures."""
    old = {b["slug"]: b for b in extract_data(release_html)["bills"]}
    for slug, sup in SUPERSEDED.items():
        b = old[slug]
        got = (to_fixed3(b["figure"]), to_fixed3(b["low"]), to_fixed3(b["high"]))
        if got != (sup["central"], sup["low"], sup["high"]):
            raise ValueError(f"QC failed: {slug} superseded {got} != release")


def build(dashboard: Path, release: Path | None = None) -> dict:
    source = load_source()
    page = pin(source, "dashboard_20261125")
    csv_pin = pin(source, "csv_20261125")
    if not dashboard.exists():
        raise FileNotFoundError(
            f"{dashboard} missing: run `python {Path(__file__).name} fetch` "
            "(the page is not committed; see source.json terms)"
        )
    if sha256(dashboard) != page["sha256"]:
        raise ValueError(
            f"{dashboard} sha256 {sha256(dashboard)} != pinned {page['sha256']}: "
            "Fiscal Lab has published a new build; update source.json on purpose"
        )
    html = dashboard.read_text(encoding="utf-8")
    data = extract_data(html)
    if data["built"] != page["build"]:
        raise ValueError(f"DATA.built {data['built']!r} != {page['build']!r}")
    if data["years"] != YEARS:
        raise ValueError(f"DATA.years {data['years']} != FY2027-2036")
    bills = data["bills"]
    if len(bills) != N_BILLS or len({b["slug"] for b in bills}) != N_BILLS:
        raise ValueError(f"expected {N_BILLS} unique bills, got {len(bills)}")
    csv = summary_csv(data, csv_footer(html, data["built"]))
    if hashlib.sha256(csv).hexdigest() != csv_pin["sha256"]:
        raise ValueError("rebuilt CSV differs from the CSV captured from the page")
    if len(csv) != csv_pin["bytes"]:
        raise ValueError("rebuilt CSV length differs from the captured CSV")
    for b in bills:
        qc_bill(b)
    rows = [_row(b) for b in bills]
    rounded = {r["slug"] for r in rows if r.get("range_rounded")}
    if rounded != RANGE_ROUNDED:
        raise ValueError(
            f"QC failed: rounded ranges moved: +{sorted(rounded - RANGE_ROUNDED)} "
            f"-{sorted(RANGE_ROUNDED - rounded)}"
        )
    qc_superseded(data, rows)
    if release is not None:
        rel = pin(source, "dashboard_20261121")
        if sha256(release) != rel["sha256"]:
            raise ValueError(f"{release} is not the pinned November 21 build")
        qc_release(release.read_text(encoding="utf-8"))
    return {
        "schema_version": 1,
        "registry": "fiscal_lab_memo_scores",
        "source_pin": page["id"],
        "source_sha256": page["sha256"],
        "build": data["built"],
        "unit": "billions of dollars, as the page's CSV prints them",
        "bills": rows,
    }


def render(extract: dict) -> str:
    return json.dumps(extract, indent=1, ensure_ascii=False) + "\n"


def beside(dest: Path, digest: str) -> Path:
    """Where a page that differs from the pin is kept:
    ``<stem>.<sha256[:12]><suffix>`` next to ``dest``. Its name is always 13
    bytes longer than dest's, so it is never dest itself, and it is never cut
    short to fit: where the filesystem refuses it as too long, ``fetch``
    stops instead."""
    return dest.with_name(f"{dest.stem}.{digest[:12]}{dest.suffix}")


def fetch(dest: Path = DEFAULT_DASHBOARD) -> tuple[str, Path]:
    """Fetch the live page. ``dest`` is replaced only when the body matches
    the pinned sha256; a body that differs is kept beside it as
    ``<stem>.<sha256[:12]><suffix>`` (see ``beside``) for inspection, so a
    new Fiscal Lab build never overwrites the pinned copy (the URL serves
    only the latest build). The filesystem decides which names fit: where it
    refuses the kept copy's name as too long, fetch removes its staging file
    and raises ValueError, and dest is left as it was. Returns the body's
    sha256 and the path it was saved to."""
    page = pin(load_source(), "dashboard_20261125")
    req = urllib.request.Request(page["url"], headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        body = resp.read()
    digest = hashlib.sha256(body).hexdigest()
    saved = dest if digest == page["sha256"] else beside(dest, digest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    # Each fetch stages its own body, so overlapping fetches cannot rename
    # one another's bytes into place. The staging name is fixed-length, not
    # built from dest's, so any dest name the filesystem accepts can be staged.
    fd, part = tempfile.mkstemp(dir=dest.parent, prefix=".fetch-", suffix=".part")
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(body)
        os.replace(part, saved)
    except BaseException as exc:
        Path(part).unlink(missing_ok=True)
        # Only the kept copy's name is longer than one the caller chose, so
        # only its refusal as too long is put as the page differing. Any
        # other error, and any refusal of dest's own name, is raised as is.
        if saved != dest and getattr(exc, "errno", None) == errno.ENAMETOOLONG:
            raise ValueError(
                f"the page differs from the pinned build, and the filesystem "
                f"refused the name of its copy beside {dest.name!r} as too long "
                f"({len(os.fsencode(saved.name))} bytes); {dest.name!r} was left "
                "as it was, so fetch to a shorter --dashboard name"
            ) from exc
        raise
    return digest, saved


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("command", choices=["fetch", "build", "check"])
    ap.add_argument("--dashboard", type=Path, default=DEFAULT_DASHBOARD)
    ap.add_argument(
        "--release",
        type=Path,
        default=None,
        help="the November 21 build's page, to check the superseded values",
    )
    args = ap.parse_args(argv)
    if args.command == "fetch":
        digest, saved = fetch(args.dashboard)
        want = pin(load_source(), "dashboard_20261125")["sha256"]
        print(f"saved {saved} sha256 {digest}")
        if digest != want:
            print(
                f"differs from the pinned build ({want}); {args.dashboard} "
                "was left as it was",
                file=sys.stderr,
            )
            return 1
        return 0
    text = render(build(args.dashboard, args.release))
    if args.command == "build":
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(text)
        print(f"wrote {N_BILLS} bills to {OUT}")
        return 0
    if OUT.read_text() != text:
        print(f"{OUT} is stale against {args.dashboard}", file=sys.stderr)
        return 1
    print(f"{OUT} matches {args.dashboard}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
