"""SQLite storage for the Scorecard database.

One file (`scorecard.db`), four tables:

- external_scores — the claims (populace-targets shape; see models.py)
- pe_results     — PolicyEngine computations, full history per claim
- diagnoses      — adjudications of material divergences
- lanes          — live mission-control status per (source × area) lane

`comparisons` is a VIEW joining each claim to its latest PE result. Common
conditions (geography, program) are extracted into indexed columns; the full
conditions mapping stays canonical JSON queryable via json_extract.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Iterable, Optional

from .models import ExternalScore, PEResult

DDL = """
CREATE TABLE IF NOT EXISTS external_scores (
    claim_id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    source_model TEXT,
    ledger_fact TEXT,
    source_column TEXT,
    publication TEXT NOT NULL DEFAULT '{}',
    reform_key TEXT NOT NULL,
    reform_json TEXT NOT NULL,
    metric TEXT NOT NULL,
    unit_concept TEXT NOT NULL,
    period INTEGER NOT NULL,
    time_basis TEXT NOT NULL,
    conditions TEXT NOT NULL DEFAULT '{}',
    geography TEXT,
    program TEXT,
    value REAL,
    value_kind TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('ok','suppressed')),
    calibration_relationship TEXT NOT NULL CHECK (
        calibration_relationship IN
        ('consumed_as_target','seed_source','held_out')
    ),
    period_start INTEGER,
    period_end INTEGER
);
CREATE INDEX IF NOT EXISTS idx_scores_source ON external_scores(source);
CREATE INDEX IF NOT EXISTS idx_scores_geo ON external_scores(geography);
CREATE INDEX IF NOT EXISTS idx_scores_prog ON external_scores(program);
CREATE INDEX IF NOT EXISTS idx_scores_reform ON external_scores(reform_key);

CREATE TABLE IF NOT EXISTS pe_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    claim_id TEXT NOT NULL REFERENCES external_scores(claim_id),
    computed_value REAL,
    status TEXT NOT NULL CHECK (status IN (
        'comparable','constructed','concept_mismatch','pe_gap','not_computed'
    )),
    engine_version TEXT NOT NULL,
    data_bundle TEXT NOT NULL,
    pe_construction TEXT NOT NULL DEFAULT '',
    run_id TEXT NOT NULL DEFAULT '',
    computed_at TEXT NOT NULL DEFAULT '',
    annotations TEXT NOT NULL DEFAULT '[]'
);
CREATE INDEX IF NOT EXISTS idx_results_claim ON pe_results(claim_id);

CREATE TABLE IF NOT EXISTS diagnoses (
    claim_id TEXT PRIMARY KEY REFERENCES external_scores(claim_id),
    diagnosis_class TEXT NOT NULL CHECK (diagnosis_class IN (
        'pe_gap','external_issue','concept_mismatch','vintage','undiagnosed'
    )),
    rationale TEXT NOT NULL DEFAULT '',
    action_link TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS pe_exhibits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exhibit TEXT NOT NULL,
    reform_key TEXT NOT NULL,
    reform_json TEXT NOT NULL,
    metric TEXT NOT NULL,
    unit_concept TEXT NOT NULL,
    period INTEGER NOT NULL,
    time_basis TEXT NOT NULL,
    conditions TEXT NOT NULL DEFAULT '{}',
    geography TEXT,
    program TEXT,
    value REAL NOT NULL,
    baseline_value REAL,
    delta REAL,
    engine_version TEXT NOT NULL,
    data_bundle TEXT NOT NULL,
    run_id TEXT NOT NULL DEFAULT '',
    computed_at TEXT NOT NULL DEFAULT '',
    note TEXT NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_exhibits_kind ON pe_exhibits(exhibit);

CREATE TABLE IF NOT EXISTS lanes (
    lane TEXT PRIMARY KEY,
    stage TEXT NOT NULL CHECK (stage IN (
        'registered','cataloged','ingested','computed','diagnosing',
        'published','regressed'
    )),
    detail TEXT NOT NULL DEFAULT '',
    updated_at TEXT NOT NULL DEFAULT ''
);

CREATE VIEW IF NOT EXISTS comparisons AS
SELECT
    s.*,
    r.computed_value AS pe_value,
    r.status AS pe_status,
    r.engine_version,
    r.data_bundle,
    r.pe_construction,
    r.computed_at,
    r.computed_value - s.value AS delta,
    CASE WHEN s.value != 0 THEN r.computed_value / s.value END AS ratio,
    d.diagnosis_class,
    d.rationale AS diagnosis_rationale,
    d.action_link
FROM external_scores s
LEFT JOIN pe_results r ON r.id = (
    SELECT id FROM pe_results
    WHERE claim_id = s.claim_id
    ORDER BY computed_at DESC, id DESC LIMIT 1
)
LEFT JOIN diagnoses d ON d.claim_id = s.claim_id;
"""


SCORES_SQL = (
    "INSERT OR REPLACE INTO external_scores"
    " (claim_id, source, source_model, ledger_fact,"
    " source_column, publication, reform_key, reform_json,"
    " metric, unit_concept, period, time_basis, conditions,"
    " geography, program, value, value_kind, status,"
    " calibration_relationship, period_start, period_end)"
    " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
)
RESULTS_SQL = (
    "INSERT INTO pe_results (claim_id, computed_value, status,"
    " engine_version, data_bundle, pe_construction, run_id,"
    " computed_at, annotations) VALUES (?,?,?,?,?,?,?,?,?)"
)
EXHIBITS_SQL = (
    "INSERT INTO pe_exhibits (exhibit, reform_key, reform_json,"
    " metric, unit_concept, period, time_basis, conditions,"
    " geography, program, value, baseline_value, delta,"
    " engine_version, data_bundle, run_id, computed_at, note)"
    " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
)
LANE_SQL = (
    "INSERT INTO lanes (lane, stage, detail, updated_at)"
    " VALUES (?,?,?,?) ON CONFLICT(lane) DO UPDATE SET"
    " stage=excluded.stage, detail=excluded.detail,"
    " updated_at=excluded.updated_at"
)


class ScorecardDB:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(DDL)
        self._migrate()

    def _migrate(self):
        """Bring a pre-existing file up to the current schema.

        CREATE TABLE IF NOT EXISTS leaves old files untouched, so columns
        added later (period_start/period_end, 2026-08-02) are ALTERed in.
        The comparisons view stores its SELECT as text and expands s.* at
        query time, so it needs no rebuild.
        """
        cols = {
            r["name"] for r in self.conn.execute("PRAGMA table_info(external_scores)")
        }
        with self.conn:
            for col in ("period_start", "period_end"):
                if col not in cols:
                    self.conn.execute(
                        f"ALTER TABLE external_scores ADD COLUMN {col} INTEGER"
                    )

    def close(self):
        self.conn.close()

    # -- writes ---------------------------------------------------------
    # Row preparers are exposed so ingests that need several writes in ONE
    # transaction can executemany(SCORES_SQL / RESULTS_SQL, ...) inside a
    # single `with db.conn:` block; the convenience methods below commit
    # per call.
    @staticmethod
    def score_row(s: ExternalScore) -> tuple:
        return (
            s.claim_id(),
            s.source,
            s.source_model,
            s.ledger_fact,
            s.source_column,
            json.dumps(s.publication, sort_keys=True),
            s.reform.key(),
            s.reform.to_json(),
            s.metric.value,
            s.unit_concept.value,
            s.period,
            s.time_basis.value,
            json.dumps(s.conditions, sort_keys=True),
            s.conditions.get("geography"),
            s.conditions.get("program"),
            s.value,
            s.value_kind,
            s.status,
            s.calibration_relationship.value,
            s.period_start,
            s.period_end,
        )

    @staticmethod
    def result_row(r: PEResult) -> tuple:
        return (
            r.claim_id,
            r.computed_value,
            r.status.value,
            r.engine_version,
            r.data_bundle,
            r.pe_construction,
            r.run_id,
            r.computed_at,
            json.dumps(r.annotations),
        )

    def upsert_scores(self, scores: Iterable[ExternalScore]) -> int:
        rows = [self.score_row(s) for s in scores]
        with self.conn:
            self.conn.executemany(SCORES_SQL, rows)
        return len(rows)

    def add_results(self, results: Iterable[PEResult]) -> int:
        rows = [self.result_row(r) for r in results]
        with self.conn:
            self.conn.executemany(RESULTS_SQL, rows)
        return len(rows)

    @staticmethod
    def exhibit_row(r: dict) -> tuple:
        return (
            r["exhibit"],
            r["reform_key"],
            r["reform_json"],
            r["metric"],
            r["unit_concept"],
            r["period"],
            r["time_basis"],
            json.dumps(r.get("conditions", {}), sort_keys=True),
            r.get("geography"),
            r.get("program"),
            r["value"],
            r.get("baseline_value"),
            r.get("delta"),
            r["engine_version"],
            r["data_bundle"],
            r.get("run_id", ""),
            r.get("computed_at", ""),
            r.get("note", ""),
        )

    def add_exhibits(self, rows: Iterable[dict]) -> int:
        """PE-only exhibits: computations with no external claim to attach
        to (e.g. per-program take-up poverty attribution)."""
        prepared = [self.exhibit_row(r) for r in rows]
        with self.conn:
            self.conn.executemany(EXHIBITS_SQL, prepared)
        return len(prepared)

    def exhibits(self, exhibit: str) -> list[sqlite3.Row]:
        return self.conn.execute(
            "SELECT * FROM pe_exhibits WHERE exhibit = ?", (exhibit,)
        ).fetchall()

    def set_lane(self, lane: str, stage: str, detail: str = "", at: str = ""):
        with self.conn:
            self.conn.execute(LANE_SQL, (lane, stage, detail, at))

    def diagnose(
        self,
        claim_id: str,
        diagnosis_class: str,
        rationale: str = "",
        action_link: str = "",
    ):
        with self.conn:
            self.conn.execute(
                "INSERT INTO diagnoses VALUES (?,?,?,?) ON CONFLICT(claim_id)"
                " DO UPDATE SET diagnosis_class=excluded.diagnosis_class,"
                " rationale=excluded.rationale,"
                " action_link=excluded.action_link",
                (claim_id, diagnosis_class, rationale, action_link),
            )

    # -- reads ----------------------------------------------------------
    def comparisons(
        self,
        source: Optional[str] = None,
        program: Optional[str] = None,
        geography: Optional[str] = None,
        held_out_only: bool = False,
        condition: Optional[tuple[str, str]] = None,
    ) -> list[sqlite3.Row]:
        q = "SELECT * FROM comparisons WHERE 1=1"
        args: list = []
        for col, val in (
            ("source", source),
            ("program", program),
            ("geography", geography),
        ):
            if val is not None:
                q += f" AND {col} = ?"
                args.append(val)
        if held_out_only:
            q += " AND calibration_relationship = 'held_out'"
        if condition:
            q += " AND json_extract(conditions, ?) = ?"
            args += [f"$.{condition[0]}", condition[1]]
        return self.conn.execute(q, args).fetchall()

    def coverage(self) -> dict:
        row = self.conn.execute(
            "SELECT COUNT(*) AS claims,"
            " SUM(pe_value IS NOT NULL) AS computed,"
            " SUM(pe_value IS NOT NULL AND"
            "     calibration_relationship='held_out') AS held_out_computed"
            " FROM comparisons WHERE status='ok'"
        ).fetchone()
        return dict(row)
