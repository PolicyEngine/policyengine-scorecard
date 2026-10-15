"""Capture every staged November 2025 PMD cell as an external score.

The exact partition is 24,304 source cells = 552 unchanged obr_costings
cells + 23,752 cells written here (12,449 tax and 11,303 spending). Source
identity is the vendored harvest line and its SHA-256, not a description:
the workbook contains repeated descriptions/heads/FYs. The slice is joined
by the complete staged JSON identity, never by a count or fuzzy title.

Invariants: table/event tallies equal the pinned staged file; the source
partition is disjoint and exhaustive; each verbatim GBP-million cell is
retained (zero included), so Decimal sums by event/table/head are conserved;
FY periods use the end year; every condition is in STANDARD_CONDITIONS;
every announcement baseline is registered. IDs include the replay's source
row identity and are deterministic/unique. Replacement runs in one
transaction, deletes only this module's registry mark, and is idempotent.

The inventory builder's own assign_measure_keys/event_key functions define
keys. For its 32 events we retain the inventory key and use the replay's
canonical registry key where one exists (including existing_registry_key).
Registry keys are joined by verified source_rows, since the inventory does
not identify every later registry alias. Historical keys use the inventory
builder function. Inventory scope/expressibility/readiness and missing
machinery are carried verbatim,
never reclassified. Historical cells explicitly say not_yet_classified.

The 552 older claims retain their original IDs, reforms, conditions and
publication byte content; cell_matches() supplies their source-cell and
inventory metadata alongside the same mapping for every other PMD cell.
Those older claims use the inventory's preferred registry keys. Three
subsequently renamed replay measures cover 132 of their cells; the mapping
exposes replay_measure_key and complete publication evidence for them while
keeping the frozen claims byte-for-byte unchanged.

Only original_scorecard cells were staged: no re-costing phase appears in
this harvest, and GDP-based extensions were deliberately excluded during
staging. No PolicyEngine value is generated or attached here.
"""

from __future__ import annotations

import gzip
import hashlib
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

from . import ingest_obr_costings
from .baselines import BASELINES
from .db import LANE_SQL, SCORES_SQL, ScorecardDB
from .harvest import REPO, finish, policy_ref, require_fields, with_baseline_condition
from .models import (
    ExternalScore,
    Metric,
    STANDARD_CONDITIONS,
    TimeBasis,
    UnitConcept,
    baseline_key,
)
from .obr_pmd_identity import (
    EVENTS,
    HISTORICAL_EVENTS,
    assign_measure_keys,
    baseline_descriptor,
    event_key,
    event_slug,
)
from .relationships import uk_relationship

HARVEST = (
    REPO / "sources" / "harvest-uk-2026-08-02" / "uk_obr" / "claims_staged.jsonl.gz"
)
MANIFEST = HARVEST.parent / "manifest.jsonl"
INVENTORY = REPO / "data" / "uk" / "events" / "inventory.jsonl"
HARVEST_SHA256 = "46117d14c4de7ac10cbc9bc09acef6c5b5060db1605e02334d4a827cf420a3bd"
REGISTRY_MARK = "obr_pmd_all_events"
SOURCE = "obr_pmd"
FAMILY = "uk_obr_pmd"
LANE_ID = "uk-obr-pmd"
LANE_UPDATED = "2026-10-11"
FEED_UPDATED = ingest_obr_costings.FEED_UPDATED
LANE = {
    LANE_ID: {
        "source": "OBR Policy Measures Database (November 2025)",
        "area": "All original Treasury and OBR-scrutinised tax and spending scorecards, Budget 1970 to Autumn Budget 2025",
        "mode": 2,
        "country": "UK",
    }
}
PMD_TABLES = ingest_obr_costings.PMD_TABLES
_TABLE_NAMES = {
    "Tax Measures (Policy measures database)": "tax",
    "Spending Measures (Policy measures database)": "spending",
}
EXPECTED = {
    "read": 24304,
    "costings_slice": 552,
    "ingested": 23752,
    "by_table": {"tax": 12449, "spending": 11303},
}
EXPECTED_STAGED_TABLES = {"tax": 12773, "spending": 11531}
# Counts in the closed workbook event order; changes require a deliberate
# new vintage/partition decision rather than a silently shorter import.
EXPECTED_EVENTS = dict(
    zip(
        EVENTS,
        (
            2,
            6,
            10,
            4,
            28,
            16,
            24,
            20,
            12,
            30,
            46,
            28,
            36,
            26,
            16,
            14,
            22,
            28,
            26,
            26,
            24,
            32,
            22,
            60,
            60,
            66,
            51,
            48,
            51,
            60,
            81,
            90,
            20,
            24,
            13,
            84,
            28,
            39,
            24,
            45,
            52,
            57,
            36,
            60,
            40,
            87,
            32,
            51,
            108,
            60,
            84,
            80,
            330,
            234,
            395,
            228,
            420,
            426,
            545,
            654,
            505,
            600,
            365,
            660,
            336,
            682,
            540,
            315,
            846,
            101,
            1314,
            198,
            1464,
            1043,
            1020,
            1080,
            642,
            1176,
            1020,
            1116,
            816,
            1134,
            498,
            1512,
        ),
        strict=True,
    )
)
_KNOWN_FIELDS = ingest_obr_costings._KNOWN_FIELDS | {"reason", "status_reason"}
_KNOWN_CONDITIONS = ingest_obr_costings._KNOWN_CONDITIONS
_REGISTERED_KEYS = frozenset(baseline_key(desc) for desc, *_ in BASELINES)
_METADATA_KEYS = frozenset(
    {
        "event_key",
        "inventory_measure_key",
        "measure_key",
        "pmd_class",
        "pe_expressibility",
        "pe_readiness",
        "pe_out_reason",
        "pe_missing",
        "pe_expressibility_note",
    }
)


@dataclass(frozen=True)
class Cell:
    harvest_line: int
    line_sha256: str  # inventory: includes the terminating newline
    replay_line_sha256: str  # event registry: excludes the newline
    row: dict

    @property
    def source_row_id(self) -> str:
        return f"obr_pmd_nov2025:{self.harvest_line}:{self.replay_line_sha256[:16]}"


def load_cells() -> list[Cell]:
    raw = gzip.open(HARVEST, "rb").read()
    if hashlib.sha256(raw).hexdigest() != HARVEST_SHA256:
        raise ValueError(f"{REGISTRY_MARK}: staged harvest digest drifted")
    cells = []
    for number, line in enumerate(raw.splitlines(keepends=True), 1):
        row = json.loads(line)
        if row.get("source_table") in PMD_TABLES:
            cells.append(
                Cell(
                    number,
                    hashlib.sha256(line).hexdigest(),
                    hashlib.sha256(line.rstrip(b"\r\n")).hexdigest(),
                    row,
                )
            )
    return cells


def load_rows() -> list[dict]:
    return [cell.row for cell in load_cells()]


def manifest() -> dict:
    entries = [json.loads(line) for line in MANIFEST.read_text().splitlines() if line]
    matches = [
        entry
        for entry in entries
        if entry["local_path"]
        == "downloads/Policy_measures_database_November_2025_.xlsx"
    ]
    if len(matches) != 1:
        raise ValueError(
            f"{REGISTRY_MARK}: November 2025 workbook manifest is not unique"
        )
    return matches[0]


def _identity(row: dict) -> str:
    return json.dumps(row, sort_keys=True, separators=(",", ":"))


def partition() -> tuple[list[Cell], dict[int, ExternalScore], list[Cell]]:
    """Exact source-cell partition, retaining the older lane's claim IDs."""
    cells = load_cells()
    index, ab_join = ingest_obr_costings.measures(), ingest_obr_costings._ab2025_join()
    selected = defaultdict(list)
    for row in ingest_obr_costings.load_rows():
        if row["source_table"] in PMD_TABLES:
            selected[_identity(row)].append(
                ingest_obr_costings._score(row, index, ab_join)
            )
    legacy, complement = {}, []
    for cell in cells:
        candidates = selected.get(_identity(cell.row))
        if candidates:
            legacy[cell.harvest_line] = candidates.pop(0)
        else:
            complement.append(cell)
    unmatched = sum(len(matches) for matches in selected.values())
    if unmatched or len(legacy) != EXPECTED["costings_slice"]:
        raise ValueError(
            f"{REGISTRY_MARK}: slice source identity drift ({unmatched} unmatched, {len(legacy)} matched)"
        )
    if len(cells) != len(legacy) + len(complement):
        raise ValueError(f"{REGISTRY_MARK}: non-exhaustive partition")
    return cells, legacy, complement


def inventory_by_line(cells: list[Cell] | None = None) -> dict[int, dict]:
    """The inventory source pointers, verified against the full staged cell."""
    cells = cells if cells is not None else load_cells()
    source = {cell.harvest_line: cell for cell in cells}
    out = {}
    for line in INVENTORY.read_text().splitlines():
        row = json.loads(line)
        for fy, pointer in row["source_cells"].items():
            n = pointer["harvest_line"]
            cell = source.get(n)
            if cell is None or cell.line_sha256 != pointer["line_sha256"]:
                raise ValueError(
                    f"{REGISTRY_MARK}: inventory source pointer drift at {n}"
                )
            staged = cell.row
            cond = staged["conditions"]
            head = cond.get("tax_head") or cond.get("spending_head")
            if (
                cond["fy"],
                cond["fiscal_event"],
                staged["reform_hint"],
                head,
                staged["value_raw"],
            ) != (
                fy,
                row["event"],
                row["measure"],
                row["head"],
                row["costing_gbp_m"][fy],
            ):
                raise ValueError(
                    f"{REGISTRY_MARK}: inventory cell value/identity drift at {n}"
                )
            if n in out:
                raise ValueError(
                    f"{REGISTRY_MARK}: repeated inventory source pointer {n}"
                )
            out[n] = row
    wanted = {
        cell.harvest_line
        for cell in cells
        if cell.row["conditions"]["fiscal_event"] not in HISTORICAL_EVENTS
    }
    if set(out) != wanted:
        raise ValueError(f"{REGISTRY_MARK}: inventory source coverage drift")
    return out


def _metadata(
    cells: list[Cell], legacy: dict[int, ExternalScore] | None = None
) -> dict[int, dict]:
    legacy = partition()[1] if legacy is None else legacy
    # Recover the same maximal increasing-FY runs as build_inventory.load_rows.
    rows, current = [], None
    for cell in cells:
        row, cond = cell.row, cell.row["conditions"]
        key = (
            row["source_table"],
            cond["fiscal_event"],
            row["reform_hint"],
            cond.get("tax_head") or cond.get("spending_head"),
        )
        fy = int(cond["fy"][:4])
        if current is None or current["identity"] != key or fy <= current["last_fy"]:
            current = {
                "identity": key,
                "last_fy": fy,
                "event_key": event_key(cond["fiscal_event"]),
                "measure": row["reform_hint"],
                "lines": [],
            }
            rows.append(current)
        current["lines"].append(cell.harvest_line)
        current["last_fy"] = fy
    assign_measure_keys(rows)
    inventory = inventory_by_line(cells)
    out = {}
    for row in rows:
        for n in row["lines"]:
            inv = inventory.get(n)
            if inv is not None and (inv["measure_key"], inv["event_key"]) != (
                row["measure_key"],
                row["event_key"],
            ):
                raise ValueError(
                    f"{REGISTRY_MARK}: inventory key function drift at {n}"
                )
            out[n] = {
                "event_key": row["event_key"],
                "inventory_measure_key": row["measure_key"],
                "measure_key": (inv.get("existing_registry_key") or inv["measure_key"])
                if inv
                else row["measure_key"],
                "pmd_class": inv["class"] if inv else "not_yet_classified",
                "pe_expressibility": inv["expressibility"]
                if inv
                else "not_yet_classified",
                "pe_readiness": inv["readiness"] if inv else "not_yet_classified",
                "pe_out_reason": inv.get("out_reason") if inv else None,
                "pe_missing": inv.get("missing_machinery") if inv else None,
                "pe_expressibility_note": inv.get("expressibility_note")
                if inv
                else None,
            }
    # Registries contain additional canonical keys absent from the older
    # inventory's existing_registry_key field. Resolve those aliases by the
    # exact source pointer, retaining inventory_measure_key for its own join.
    source = {cell.harvest_line: cell for cell in cells}
    registry_lines = set()
    for path in sorted((REPO / "data" / "uk" / "events").glob("*_measures.json")):
        registry = json.loads(path.read_text())
        for measure in registry["measures"]:
            for pointer in measure["source_rows"]:
                n = pointer["source_row_number"]
                if n in registry_lines:
                    raise ValueError(
                        f"{REGISTRY_MARK}: repeated replay registry source pointer {n}"
                    )
                registry_lines.add(n)
                cell = source.get(n)
                if (
                    cell is None
                    or pointer["source_row_sha256"] != cell.replay_line_sha256
                    or pointer["source_row_id"] != cell.source_row_id
                ):
                    raise ValueError(
                        f"{REGISTRY_MARK}: replay registry source pointer drift at {n}"
                    )
                existing_key = inventory[n].get("existing_registry_key")
                if (
                    existing_key
                    and existing_key != measure["measure_key"]
                    and (
                        n not in legacy
                        or legacy[n].conditions["measure_key"] != existing_key
                    )
                ):
                    raise ValueError(
                        f"{REGISTRY_MARK}: replay registry key drift at {n}"
                    )
                # Three measures in the unchanged costings slice predate
                # registry renamings. Their claim IDs and reforms must remain
                # stable; the exact source mapping exposes the replay alias.
                out[n]["replay_measure_key"] = measure["measure_key"]
                out[n]["measure_key"] = (
                    legacy[n].conditions["measure_key"]
                    if n in legacy
                    else measure["measure_key"]
                )
    return out


def _provenance(cell: Cell, artifact: dict) -> dict:
    """Source evidence shared by new publications and frozen-cell mappings."""
    row = cell.row
    publication = row["publication"]
    if (
        publication["url"] != artifact["url"]
        or publication["wayback"] != artifact["wayback_snapshot"]
    ):
        raise ValueError(f"{REGISTRY_MARK}: workbook provenance drift")
    return {
        "sha256": artifact["sha256"],
        "wayback_snapshot": artifact["wayback_snapshot"],
        "harvest_line": cell.harvest_line,
        "line_sha256": cell.line_sha256,
        "replay_line_sha256": cell.replay_line_sha256,
        "normalization": row["normalization"],
        "fiscal_event_name": row["conditions"]["fiscal_event"],
        "staged_source": str(HARVEST.relative_to(REPO)),
        **{key: row[key] for key in ("reason", "status_reason") if key in row},
    }


def _score(cell: Cell, metadata: dict, artifact: dict) -> ExternalScore:
    row = cell.row
    require_fields(row, _KNOWN_FIELDS, REGISTRY_MARK)
    if row.get("source") != "obr":
        raise ValueError(f"{REGISTRY_MARK}: unknown source {row.get('source')!r}")
    staged = dict(row["conditions"])
    unknown = set(staged) - _KNOWN_CONDITIONS
    if unknown:
        raise ValueError(
            f"{REGISTRY_MARK}: unhandled staged conditions {sorted(unknown)}"
        )
    event = staged["fiscal_event"]
    baseline = baseline_descriptor(event)
    if baseline_key(baseline) not in _REGISTERED_KEYS:
        raise ValueError(f"{REGISTRY_MARK}: unregistered baseline {baseline!r}")
    start = int(staged["fy"][:4])
    if row["period"] != start or staged["fy"] != f"{start}-{(start + 1) % 100:02d}":
        raise ValueError(
            f"{REGISTRY_MARK}: period {row['period']} does not open fy {staged['fy']!r}"
        )
    name = row.get("metric") or row.get("proposed_metric")
    if (
        name not in ingest_obr_costings.METRICS
        or row["proposed_unit"] != "gbp"
        or row["time_basis"] != "fiscal_year"
    ):
        raise ValueError(f"{REGISTRY_MARK}: unmapped metric/unit/time basis")
    conditions = {
        "country": "UK",
        **staged,
        **{
            key: value
            for key, value in metadata.items()
            if key in _METADATA_KEYS and value is not None
        },
    }
    conditions["fiscal_event"] = event_slug(event)
    conditions["source_row_id"] = cell.source_row_id
    conditions["measure"] = row["reform_hint"]
    conditions["value_verbatim"] = str(row["value_raw"])
    conditions["benchmark_class"] = "different_model"
    if name == "exchequer_impact":
        conditions["fiscal_measure"] = name
    reform = policy_ref(conditions["measure_key"], baseline=baseline)
    with_baseline_condition(conditions, reform)
    if set(conditions) - STANDARD_CONDITIONS:
        raise ValueError(f"{REGISTRY_MARK}: condition vocabulary drift")
    publication = dict(row["publication"])
    publication.update(
        {
            "registry": REGISTRY_MARK,
            "family": FAMILY,
            "table": row["source_table"],
            "publish_without_result": True,
            **_provenance(cell, artifact),
        }
    )
    return ExternalScore(
        source=SOURCE,
        metric=ingest_obr_costings.METRICS[name],
        unit_concept=UnitConcept.GBP,
        period=start + 1,
        time_basis=TimeBasis.FISCAL_YEAR,
        value=None if row["value"] is None else float(row["value"]),
        conditions=conditions,
        reform=reform,
        calibration_relationship=uk_relationship(
            SOURCE, Metric.REVENUE_CHANGE, kind="forecast"
        )[0],
        source_model=row["source_model"],
        source_column=row["source_column"],
        publication=publication,
        value_kind=UnitConcept.GBP.value,
        status=row["status"],
    )


def score_cell(cell: Cell, metadata: dict | None = None) -> ExternalScore:
    """Convert one source cell with verified inventory/replay metadata."""
    if metadata is None:
        metadata = _metadata(load_cells())[cell.harvest_line]
    metadata = {key: value for key, value in metadata.items() if key in _METADATA_KEYS}
    return _score(cell, metadata, manifest())


def stage() -> tuple[list[ExternalScore], dict]:
    cells, legacy, complement = partition()
    metadata, artifact = _metadata(cells, legacy), manifest()
    scores = [
        _score(cell, metadata[cell.harvest_line], artifact) for cell in complement
    ]
    acct = {
        "read": len(cells),
        "costings_slice": len(legacy),
        "ingested": len(scores),
        "by_table": dict(
            Counter(_TABLE_NAMES[cell.row["source_table"]] for cell in complement)
        ),
    }
    staged_tables = dict(
        Counter(_TABLE_NAMES[cell.row["source_table"]] for cell in cells)
    )
    events = dict(Counter(cell.row["conditions"]["fiscal_event"] for cell in cells))
    if (
        acct != EXPECTED
        or staged_tables != EXPECTED_STAGED_TABLES
        or events != EXPECTED_EVENTS
    ):
        raise ValueError(f"{REGISTRY_MARK}: exact PMD accounting drifted: {acct}")
    # A legacy row can only join the same canonical reform, never a new alias.
    for n, score in legacy.items():
        if score.conditions["measure_key"] != metadata[n]["measure_key"]:
            raise ValueError(f"{REGISTRY_MARK}: legacy reform key drift at {n}")
    finish(scores, REGISTRY_MARK)
    if {score.claim_id() for score in scores} & {
        score.claim_id() for score in legacy.values()
    }:
        raise ValueError(f"{REGISTRY_MARK}: partition claim IDs overlap")
    return scores, {**acct, "by_event": events, "staged_by_table": staged_tables}


def cell_matches() -> list[dict]:
    """Every PMD source cell -> its unchanged/external claim and inventory.

    Includes the frozen costings slice's metadata without writing it or
    changing any claim ID, result attachment, condition or reform.
    """
    cells, legacy, _ = partition()
    metadata, artifact = _metadata(cells, legacy), manifest()
    matches = []
    for cell in cells:
        score = legacy.get(cell.harvest_line) or _score(
            cell, metadata[cell.harvest_line], artifact
        )
        matches.append(
            {
                **metadata[cell.harvest_line],
                "harvest_line": cell.harvest_line,
                "line_sha256": cell.line_sha256,
                "replay_line_sha256": cell.replay_line_sha256,
                "source_row_id": cell.source_row_id,
                "claim_id": score.claim_id(),
                # Frozen SQL publications stay unchanged. The source mapping
                # still supplies their complete workbook/capture/hash evidence.
                "publication": {**score.publication, **_provenance(cell, artifact)},
                "registry": ingest_obr_costings.REGISTRY_MARK
                if cell.harvest_line in legacy
                else REGISTRY_MARK,
            }
        )
    return matches


def claim_ids_by_source_cell() -> dict[int, str]:
    return {match["harvest_line"]: match["claim_id"] for match in cell_matches()}


def ingest(db_path: Path) -> dict:
    scores, acct = stage()
    db = ScorecardDB(db_path)
    rows = [ScorecardDB.score_row(score) for score in scores]
    from .baselines import register_baselines_txn
    from .ingest_harvest import sync_lane_feed

    try:
        with db.conn:
            db.conn.execute(
                "DELETE FROM external_scores WHERE json_extract(publication, '$.registry') = ?",
                (REGISTRY_MARK,),
            )
            db.conn.executemany(SCORES_SQL, rows)
            register_baselines_txn(db)
            detail = f"{acct['ingested']} original PMD cells ingested; {acct['read']} staged = {acct['costings_slice']} unchanged costings cells + {acct['ingested']} here; all 84 events, Budget 1970 to Autumn Budget 2025; awaiting PolicyEngine counterparts"
            db.conn.execute(LANE_SQL, (LANE_ID, "ingested", detail, LANE_UPDATED))
        sync_lane_feed(db, REPO / "data" / "lanes.json", FEED_UPDATED, lanes=LANE)
    finally:
        db.close()
    return {"claims": len(rows), **acct}


if __name__ == "__main__":
    import sys

    print(
        json.dumps(
            ingest(Path(sys.argv[1] if len(sys.argv) > 1 else "data/scorecard.db")),
            indent=1,
        )
    )
