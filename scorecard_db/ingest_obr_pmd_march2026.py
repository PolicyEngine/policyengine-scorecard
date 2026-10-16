"""Add only new or changed cells from the locked March 2026 PMD edition.

November remains the source of every existing claim and replay pointer. Exact
event/title/head/table/FY comparisons account for duplicate occurrences before
selecting this edition's delta. A changed value receives a separate claim; no
November row, result, classification, lane or publication is replaced.
"""

from __future__ import annotations

import gzip
import hashlib
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

from . import ingest_obr_costings, ingest_obr_pmd as november
from .baselines import BASELINES
from .collect_obr_pmd import locked_source
from .db import SCORES_SQL, ScorecardDB
from .harvest import REPO, finish, policy_ref, require_fields, with_baseline_condition
from .models import (
    ExternalScore,
    STANDARD_CONDITIONS,
    TimeBasis,
    UnitConcept,
    baseline_key,
)
from .obr_pmd_diff import EditionDiff, compare_editions, load_staged
from .obr_pmd_identity import (
    assign_measure_keys,
    event_key,
    march_baseline_descriptor as baseline_descriptor,
    march_event_slug as event_slug,
)

DIRECTORY = REPO / "sources" / "obr-pmd-march-2026"
HARVEST = DIRECTORY / "claims_staged.jsonl.gz"
MANIFEST = DIRECTORY / "manifest.jsonl"
RECEIPT = DIRECTORY / "receipt.json"
HARVEST_SHA256 = "52ea1b089d7c1dc175599394b9fd3d2309b23b56c7feb4738088b4bdd4c60eb6"
EDITION = "March 2026"
REGISTRY_MARK = "obr_pmd_march2026"
SOURCE = november.SOURCE
_KNOWN_CONDITIONS = november._KNOWN_CONDITIONS | {"edition"}


@dataclass(frozen=True)
class Cell:
    harvest_line: int
    line_sha256: str
    replay_line_sha256: str
    row: dict

    @property
    def source_row_id(self) -> str:
        return f"obr_pmd_mar2026:{self.harvest_line}:{self.replay_line_sha256[:16]}"


def load_cells() -> list[Cell]:
    raw = gzip.open(HARVEST, "rb").read()
    if hashlib.sha256(raw).hexdigest() != HARVEST_SHA256:
        raise ValueError(f"{REGISTRY_MARK}: staged harvest digest drifted")
    cells = []
    for number, line in enumerate(raw.splitlines(keepends=True), 1):
        row = json.loads(line)
        if row.get("source_table") not in november.PMD_TABLES:
            raise ValueError(f"{REGISTRY_MARK}: unexpected non-PMD staged row")
        cells.append(
            Cell(
                number,
                hashlib.sha256(line).hexdigest(),
                hashlib.sha256(line.rstrip(b"\r\n")).hexdigest(),
                row,
            )
        )
    return cells


def manifest() -> dict:
    entries = [json.loads(line) for line in MANIFEST.read_text().splitlines() if line]
    if len(entries) != 1:
        raise ValueError(f"{REGISTRY_MARK}: workbook manifest is not unique")
    artifact = entries[0]
    receipt = json.loads(RECEIPT.read_text())
    source = locked_source(receipt)
    for key, value in {
        "url": source["original_url"],
        "wayback_snapshot": source["archive_capture_url"],
        "sha256": source["sha256"],
        "bytes": source["byte_size"],
        "receipt_sha256": receipt["receipt_sha256"],
    }.items():
        if artifact.get(key) != value:
            raise ValueError(f"{REGISTRY_MARK}: receipt/manifest {key} drift")
    return artifact


def edition_diff(cells: list[Cell] | None = None) -> EditionDiff:
    # Verify November's frozen source digest as well as this edition's digest.
    november.load_cells()
    cells = load_cells() if cells is None else cells
    return compare_editions(load_staged(november.HARVEST), [cell.row for cell in cells])


def _metadata(cells: list[Cell], diff: EditionDiff) -> dict[int, dict]:
    old_cells, legacy, _ = november.partition()
    old_metadata = november._metadata(old_cells, legacy)
    by_measure, by_line_identity = defaultdict(list), defaultdict(list)
    for cell in old_cells:
        row = cell.row
        identity = (
            row["conditions"]["fiscal_event"],
            row["reform_hint"],
            row["conditions"].get("tax_head", row["conditions"].get("spending_head")),
            row["source_table"],
        )
        by_measure[identity[:2]].append(old_metadata[cell.harvest_line])
        by_line_identity[identity].append(old_metadata[cell.harvest_line])

    # The inventory's exact-title key algorithm remains the basis for new
    # titles, including its collision handling. It never edits the inventory.
    title_rows = [
        {
            "event_key": event_key(cell.row["conditions"]["fiscal_event"]),
            "measure": cell.row["reform_hint"],
        }
        for cell in [*old_cells, *cells]
    ]
    assign_measure_keys(title_rows)
    generated = {
        (row["event_key"], row["measure"]): row["measure_key"] for row in title_rows
    }
    result = {
        match.current_line: dict(old_metadata[match.previous_line])
        for match in diff.changed
    }
    for match in diff.new:
        row = match.current
        event, title = row["conditions"]["fiscal_event"], row["reform_hint"]
        identity = (
            event,
            title,
            row["conditions"].get("tax_head", row["conditions"].get("spending_head")),
            row["source_table"],
        )
        candidates = by_line_identity.get(identity) or by_measure.get(identity[:2])
        if candidates:
            keys = {candidate["measure_key"] for candidate in candidates}
            if len(keys) != 1:
                raise ValueError(
                    f"{REGISTRY_MARK}: ambiguous existing reform {identity!r}"
                )
            if by_line_identity.get(identity):
                # An extra FY for the same exact worksheet measure retains its
                # verified November classification and canonical replay alias.
                result[match.current_line] = dict(candidates[0])
                continue
            measure_key = next(iter(keys))
        else:
            measure_key = generated[event_key(event), title]
        result[match.current_line] = {
            "event_key": event_key(event),
            "measure_key": measure_key,
            "pmd_class": "not_yet_classified",
            "pe_expressibility": "not_yet_classified",
            "pe_readiness": "not_yet_classified",
        }
    return result


def score_cell(cell: Cell, metadata: dict, artifact: dict) -> ExternalScore:
    row = cell.row
    require_fields(row, november._KNOWN_FIELDS, REGISTRY_MARK)
    staged = dict(row["conditions"])
    if row.get("source") != "obr" or staged.get("edition") != EDITION:
        raise ValueError(f"{REGISTRY_MARK}: unknown source or edition")
    if set(staged) - _KNOWN_CONDITIONS:
        raise ValueError(f"{REGISTRY_MARK}: unhandled staged conditions")
    event = staged["fiscal_event"]
    baseline = baseline_descriptor(event)
    if baseline_key(baseline) not in {baseline_key(desc) for desc, *_ in BASELINES}:
        raise ValueError(f"{REGISTRY_MARK}: unregistered baseline {baseline!r}")
    start = int(staged["fy"][:4])
    if row["period"] != start or staged["fy"] != f"{start}-{(start + 1) % 100:02d}":
        raise ValueError(f"{REGISTRY_MARK}: period does not open fy")
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
            if key in november._METADATA_KEYS and value is not None
        },
        "fiscal_event": event_slug(event),
        "source_row_id": cell.source_row_id,
        "measure": row["reform_hint"],
        "value_verbatim": str(row["value_raw"]),
        "benchmark_class": "different_model",
    }
    if name == "exchequer_impact":
        conditions["fiscal_measure"] = name
    reform = policy_ref(conditions["measure_key"], baseline=baseline)
    with_baseline_condition(conditions, reform)
    if set(conditions) - STANDARD_CONDITIONS:
        raise ValueError(f"{REGISTRY_MARK}: condition vocabulary drift")
    publication = dict(row["publication"])
    if (
        publication.get("url") != artifact["url"]
        or publication.get("wayback") != artifact["wayback_snapshot"]
        or publication.get("edition") != EDITION
        or publication.get("sha256") != artifact["sha256"]
        or publication.get("receipt_sha256") != artifact["receipt_sha256"]
    ):
        raise ValueError(f"{REGISTRY_MARK}: workbook provenance drift")
    publication.update(
        {
            "registry": REGISTRY_MARK,
            "family": november.FAMILY,
            "table": row["source_table"],
            "publish_without_result": True,
            "sha256": artifact["sha256"],
            "wayback_snapshot": artifact["wayback_snapshot"],
            "receipt_sha256": artifact["receipt_sha256"],
            "harvest_line": cell.harvest_line,
            "line_sha256": cell.line_sha256,
            "replay_line_sha256": cell.replay_line_sha256,
            "normalization": row["normalization"],
            "fiscal_event_name": event,
            "staged_source": str(HARVEST.relative_to(REPO)),
            **{key: row[key] for key in ("reason", "status_reason") if key in row},
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
        calibration_relationship="held_out",
        source_model=row["source_model"],
        source_column=row["source_column"],
        publication=publication,
        value_kind=UnitConcept.GBP.value,
        status=row["status"],
    )


def stage() -> tuple[list[ExternalScore], dict]:
    cells = load_cells()
    diff = edition_diff(cells)
    metadata, artifact = _metadata(cells, diff), manifest()
    delta = sorted([*diff.changed, *diff.new], key=lambda match: match.current_line)
    scores = [
        score_cell(
            cells[match.current_line - 1], metadata[match.current_line], artifact
        )
        for match in delta
    ]
    finish(scores, REGISTRY_MARK)
    return scores, {
        "ingested": len(scores),
        "changed": len(diff.changed),
        "new": len(diff.new),
        "by_event": dict(Counter(match.key[0] for match in delta)),
        "edition_diff": diff.accounting(),
    }


def ingest(db_path: Path) -> dict:
    scores, accounting = stage()
    db = ScorecardDB(db_path)
    from .baselines import register_baselines_txn

    try:
        with db.conn:
            db.conn.execute(
                "DELETE FROM external_scores WHERE json_extract(publication, '$.registry') = ?",
                (REGISTRY_MARK,),
            )
            db.conn.executemany(
                SCORES_SQL, [ScorecardDB.score_row(score) for score in scores]
            )
            register_baselines_txn(db)
    finally:
        db.close()
    return {"claims": len(scores), **accounting}


if __name__ == "__main__":
    import sys

    print(
        json.dumps(
            ingest(Path(sys.argv[1] if len(sys.argv) > 1 else "data/scorecard.db")),
            indent=1,
        )
    )
