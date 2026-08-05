"""Shared helpers for the 2026-08-02 overnight-harvest adapters.

Seven per-source adapters (ingest_jct, ingest_tpc, ingest_budget_lab,
ingest_cpsp, ingest_cbo, ingest_pwbm, ingest_tax_foundation) read the
vendored staging files under sources/harvest-2026-08-02/<source>/ and map
staged rows onto ExternalScore. The contract, per scorecard_db/README.md:

- FAIL LOUDLY. Unknown top-level fields, unmapped metrics, unmapped
  condition keys, unparseable windows, and claim-id collisions all raise.
  Nothing is skipped silently; deliberate drops return a tally.
- Values are normalized in UNITS only (billions -> USD, fraction ->
  percent) — never re-derived. The published number stays recoverable via
  the vendored claims_staged.jsonl referenced from each row's publication.
- Reform worlds ride ReformRef (framework "policy_ref" for named external
  policy worlds); non-current-law baselines ride ReformRef.baseline and
  are mirrored to conditions["baseline_policy"] (COLLATION item 3).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from .models import ExternalScore, ReformRef

REPO = Path(__file__).resolve().parent.parent
HARVEST = REPO / "sources" / "harvest-2026-08-02"


def load_staged(source: str) -> list[dict]:
    path = HARVEST / source / "claims_staged.jsonl"
    if not path.exists():
        raise FileNotFoundError(f"staged claims missing: {path}")
    rows = [json.loads(line) for line in path.open() if line.strip()]
    if not rows:
        raise ValueError(f"no staged rows in {path}")
    return rows


def require_fields(row: dict, known: frozenset, source: str) -> None:
    """Every staged top-level field must be explicitly accounted for."""
    unknown = set(row) - set(known)
    if unknown:
        raise ValueError(
            f"{source}: unhandled staged fields {sorted(unknown)} — "
            "extend the adapter deliberately"
        )


def policy_ref(policy: str, baseline: dict | None = None, **detail) -> ReformRef:
    """Named external policy world. Keep descriptors MINIMAL: only keys
    that define a distinct world (e.g. option) — provenance like table ids
    belongs in publication/conditions, or identical worlds stop sharing a
    reform key across sources."""
    return ReformRef(
        framework="policy_ref",
        reform={"policy": policy, **detail},
        baseline=baseline,
    )


def with_baseline_condition(conditions: dict, reform: ReformRef) -> dict:
    """Mirror a non-current-law ReformRef.baseline into conditions."""
    if reform.baseline is not None:
        conditions["baseline_policy"] = reform.baseline["policy"]
    return conditions


_WINDOW = re.compile(r"^(?:FY)?(\d{4})\s*[-–]\s*(\d{2}|\d{4})$")


def parse_window(text: str) -> tuple[int, int]:
    """'2025-2034' | 'FY2026-2035' | '2025-34' -> (start, end)."""
    m = _WINDOW.match(text.strip())
    if not m:
        raise ValueError(f"unparseable period window: {text!r}")
    start = int(m.group(1))
    end_raw = m.group(2)
    end = int(end_raw) if len(end_raw) == 4 else (start // 100) * 100 + int(end_raw)
    if end <= start:
        raise ValueError(f"window end before start: {text!r}")
    return start, end


def billions(value: float) -> float:
    return value * 1e9


def fraction_to_percent(value: float) -> float:
    return value * 100.0


_STATES = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "District of Columbia": "DC",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
}


def normalize_geography(geo: str) -> str:
    """State names -> USPS codes; 'us' -> 'US'; custom aggregates pass
    through verbatim (e.g. us_38_states_without_refundable_state_ctc)."""
    if geo in ("us", "US"):
        return "US"
    if geo in _STATES:
        return _STATES[geo]
    if set(geo) <= set("abcdefghijklmnopqrstuvwxyz_0123456789"):
        return geo  # documented custom aggregate slug
    raise ValueError(f"unmapped geography: {geo!r}")


def merge_republications(
    scores: list[ExternalScore],
    source: str,
    precision,
    tolerance,
) -> list[ExternalScore]:
    """Sources sometimes publish the SAME statistic twice (an HTML table
    and its companion workbook; TPC's distribution and cut/increase table
    pairs both carry average tax change). One claim, two artifacts: keep
    the higher-`precision(score)` row, require the pair to agree within
    `tolerance(coarse_score)`, and keep the twin's provenance under
    publication["also_published"]. Genuine disagreement raises."""
    by_id: dict[str, list[ExternalScore]] = {}
    for s in scores:
        by_id.setdefault(s.claim_id(), []).append(s)
    merged = []
    for cid, group in by_id.items():
        if len(group) == 1:
            merged.append(group[0])
            continue
        if len(group) > 2:
            raise ValueError(
                f"{source}: >2 rows share claim {cid}: "
                f"{[s.source_column for s in group]}"
            )
        coarse, fine = sorted(group, key=precision)
        if abs(coarse.value - fine.value) > tolerance(coarse):
            raise ValueError(
                f"{source}: twin publications disagree beyond rounding "
                f"for {cid}: {coarse.value} vs {fine.value} "
                f"({coarse.source_column!r} vs {fine.source_column!r})"
            )
        fine.publication["also_published"] = {
            "title": coarse.publication.get("title"),
            "table": coarse.publication.get("table")
            or coarse.publication.get("table_id"),
            "url": coarse.publication.get("url"),
            "source_column": coarse.source_column,
            "value": coarse.value,
        }
        merged.append(fine)
    return merged


def finish(scores: list[ExternalScore], source: str) -> list[ExternalScore]:
    """Uniqueness gate: staged rows mapping to one claim_id means the
    conditions vocabulary lost a distinguishing axis — a bug, not a dedup."""
    seen: dict[str, ExternalScore] = {}
    for s in scores:
        cid = s.claim_id()
        if cid in seen:
            prev = seen[cid]
            raise ValueError(
                f"{source}: claim_id collision {cid}\n"
                f"  a: {prev.metric.value} {prev.period} {prev.conditions} "
                f"value={prev.value}\n"
                f"  b: {s.metric.value} {s.period} {s.conditions} "
                f"value={s.value}"
            )
        seen[cid] = s
    return scores
