"""Shared helpers for the 2026-08-02 UK-harvest adapters.

Seven per-source adapters (ingest_uk_obr, ingest_uk_hmrc, ingest_uk_dwp,
ingest_uk_hmt, ingest_uk_ukmod_jrf, ingest_uk_ifs, ingest_uk_rf) read the
vendored staging under sources/harvest-uk-2026-08-02/<source>/ (gzipped —
the OBR file alone is 36 MB plain) and map staged rows onto ExternalScore
under the same contract as the US harvest (scorecard_db/harvest.py), plus
three UK-specific rules:

1. **Fiscal years.** UK FY runs Apr–Mar and the staging mixes START-year
   ints (HMRC/OBR), END-year ints (DWP "FYE 2010"), and one defective
   parse ("1999/00" → 1900). Adapters therefore RE-DERIVE period from the
   verbatim fy label: period = FY START year (the pe-uk-data convention,
   targets/sources/obr.py `_FY_COL_TO_YEAR`), and conditions["fy"] is the
   normalized "2026-27" form.

2. **Ledger routing (Max 2026-08-02).** Administrative caseload /
   expenditure / receipts OUTTURN rows (DWP BECL outturns, HMRC outturn
   statistics incl. provisional, OBR EFO outturn columns) are populace
   CALIBRATION material: they go to the Ledger staging file
   (data/ledger/uk_admin_outturns.jsonl), NEVER external_scores. Forecast
   / projected rows are a model speaking and DO enter. Survey-outcome
   statistics (HBAI poverty) are not admin outturn — they stay
   scorecard-side as permanent holdouts.

3. **Load-bearing conditions.** income_concept (BHC|AHC) + equivalisation
   ride every distribution row; conditions["basis"] preserves the
   source's own outturn/forecast designation on scorecard-side rows.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import re
from pathlib import Path

from .harvest import REPO
from .models import ExternalScore

UK_HARVEST = REPO / "sources" / "harvest-uk-2026-08-02"
LEDGER_STAGING = REPO / "data" / "ledger" / "uk_admin_outturns.jsonl"


def load_staged_uk(source: str) -> list[dict]:
    path = UK_HARVEST / source / "claims_staged.jsonl.gz"
    if not path.exists():
        raise FileNotFoundError(f"staged claims missing: {path}")
    with gzip.open(path, "rt") as f:
        rows = [json.loads(line) for line in f if line.strip()]
    if not rows:
        raise ValueError(f"no staged rows in {path}")
    return rows


# -- fiscal years -------------------------------------------------------
_FY = re.compile(r"^(?:FYE\s*(\d{4}))$|^(\d{4})\s*[-/–]\s*(\d{2}|\d{4})$")


def parse_fy(label: str) -> tuple[int, str]:
    """Verbatim UK fiscal-year label -> (start_year, normalized 'YYYY-YY').

    'FYE 2010' (year ending Mar 2010) -> (2009, '2009-10');
    '2026-27' / '2023/24' / '1999/00' / '1970-71' -> start-year keyed.
    Non-contiguous spans are rejected — ranges go through parse_fy_window.
    """
    m = _FY.match(label.strip())
    if not m:
        raise ValueError(f"unparseable UK fiscal-year label: {label!r}")
    if m.group(1):  # FYE yyyy = FY (yyyy-1)–yyyy
        start = int(m.group(1)) - 1
    else:
        start = int(m.group(2))
        end_raw = m.group(3)
        end2 = int(end_raw) % 100
        if end2 != (start + 1) % 100:
            raise ValueError(f"non-contiguous fiscal-year label: {label!r}")
    return start, f"{start}-{(start + 1) % 100:02d}"


def parse_fy_window(label: str) -> tuple[int, int, str]:
    """'2025-26 to 2029-30' / '2021/22-2023/24' -> (2025, 2029, normalized).

    Returned bounds are FY START years for period_start/period_end."""
    parts = re.split(r"\s+to\s+|(?<=\d)\s*[-–]\s*(?=\d{4})", label.strip())
    if len(parts) != 2:
        raise ValueError(f"unparseable fiscal-year window: {label!r}")
    first, _ = parse_fy(parts[0])
    last, _ = parse_fy(parts[1])
    if last <= first:
        raise ValueError(f"window end before start: {label!r}")
    return (
        first,
        last,
        f"{first}-{(first + 1) % 100:02d} to " + (f"{last}-{(last + 1) % 100:02d}"),
    )


# -- geography ----------------------------------------------------------
# Canonical UK geography slugs (COLLATION UK conventions: labels verbatim
# in spirit; normalized here only for case and note-stripping so
# cross-source queries join). Verbatim long labels keep their note in
# conditions["geography_note"] at the adapter's discretion.
_GEO = {
    "uk": "UK",
    "united kingdom": "UK",
    "gb": "GB",
    "great britain": "GB",
    "england": "england",
    "scotland": "scotland",
    "wales": "wales",
    "northern ireland": "northern_ireland",
    "england_wales": "england_wales",
    "england and wales": "england_wales",
    "uk excluding northern ireland": "UK_excl_NI",
    "uk excluding scotland": "UK_excl_scotland",
    "north east": "north_east",
    "north west": "north_west",
    "yorkshire and the humber": "yorkshire_and_the_humber",
    "east midlands": "east_midlands",
    "west midlands": "west_midlands",
    "east of england": "east_of_england",
    "east": "east_of_england",  # ONS region, abbreviated in UKMOD tables
    "london": "london",
    "south east": "south_east",
    "south west": "south_west",
}


def normalize_geography_uk(geo: str) -> tuple[str, str | None]:
    """Verbatim staged geography -> (canonical slug, note or None).

    IFS embeds scope notes in the label ("UK excluding Northern Ireland
    (note verbatim: …)"); the note is split off so the slug joins."""
    raw = geo.strip()
    note = None
    m = re.match(r"^(.*?)\s*\((note verbatim:.*)\)$", raw, re.S)
    if m:
        raw, note = m.group(1).strip(), m.group(2)
    slug = _GEO.get(raw.lower())
    if slug is None:
        raise ValueError(f"unmapped UK geography: {geo!r}")
    return slug, note


# -- reform slugs -------------------------------------------------------
def slugify(text: str, max_len: int = 60) -> str:
    """Deterministic readable slug for reform-hint titles. Truncated
    slugs get a short hash of the full text so titles differing only in
    their tail ("…by 1%" vs "…by 10%") can never share a world."""
    s = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    if len(s) <= max_len:
        return s
    digest = hashlib.sha256(text.strip().encode()).hexdigest()[:6]
    return f"{s[:max_len].rstrip('_')}_{digest}"


def measure_slug(prefix: str, event: str, title: str) -> str:
    """Stable policy slug for a fiscal-event measure: readable prefix +
    an 8-hex hash of the verbatim title (titles are long and near-
    duplicated across events; the hash keeps identity exact while the
    verbatim title rides conditions['measure'])."""
    digest = hashlib.sha256(title.strip().encode()).hexdigest()[:8]
    return f"{prefix}:{slugify(event, 24)}:{digest}"


# -- ledger routing -----------------------------------------------------
def ledger_fact_id(source: str, staged: dict, derived: dict | None) -> str:
    """Deterministic pre-agreed fact id for the populace/Ledger lane."""
    digest = hashlib.sha256(
        json.dumps(
            {"staged": staged, "derived": derived or {}},
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
    ).hexdigest()[:20]
    return f"uk:{source}:{digest}"


def ledger_row(
    source: str, staged: dict, reason: str, derived: dict | None = None
) -> dict:
    """Wrap a staged admin-outturn row for the Ledger staging file: the
    verbatim staged row plus routing provenance. `derived` carries
    adapter-reconstructed context the staging dropped (e.g. OBR 4.9
    section — byte-identical subtotal cells recur across sections and
    must not collapse to one fact). Scorecard rows that later reference
    this fact do so via the fact id, never copies."""
    out = {
        "fact_id": ledger_fact_id(source, staged, derived),
        "source": source,
        "routed_because": reason,
        "staged": staged,
    }
    if derived:
        out["derived"] = derived
    return out


def write_ledger_staging(rows: list[dict], path: Path = LEDGER_STAGING) -> int:
    """Write the Ledger handoff file (sorted by fact id — stable diffs)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = sorted(rows, key=lambda r: r["fact_id"])
    ids = [r["fact_id"] for r in rows]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        raise ValueError(f"duplicate ledger fact ids: {sorted(dupes)[:5]}")
    with path.open("w") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    return len(rows)


# -- misc ---------------------------------------------------------------
def require_conditions(staged: dict, known: dict, source: str) -> dict:
    """Map staged condition keys through `known` (staged key -> DB key),
    failing loudly on anything unmapped. None-valued conditions are
    dropped (absent means not applicable)."""
    out = {}
    for k, v in staged.items():
        if k not in known:
            raise ValueError(f"{source}: unmapped condition {k!r}")
        if v is None:
            continue
        if not isinstance(v, str):
            v = json.dumps(v)
        out[known[k]] = v
    return out


def uk_value_kind(staged_kind: str | None, unit_value: str) -> str:
    """Normalize staged value_kind ('currency_gbp'/'gbp'/'usd' drift) to
    the DB convention: gbp for currency, else count/share as staged."""
    if staged_kind in ("currency_gbp", "gbp", "usd"):
        return "gbp"
    if staged_kind in ("count", "share"):
        return staged_kind
    if staged_kind is None:
        return "gbp" if unit_value.startswith("gbp") else "count"
    raise ValueError(f"unmapped value_kind: {staged_kind!r}")


def tally(scores: list[ExternalScore]) -> dict:
    """Per-metric counts for lane details and runner stats."""
    out: dict[str, int] = {}
    for s in scores:
        out[s.metric.value] = out.get(s.metric.value, 0) + 1
    return out
