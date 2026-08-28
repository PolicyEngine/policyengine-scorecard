"""SQLite storage for the Scorecard database.

One file (`scorecard.db`), seven tables:

- external_scores — the claims (populace-targets shape; see models.py).
                   Provenance is INTERNED: the row carries publication_id
                   and reform_key; the JSON lives once per distinct value
                   in the publications / reforms side tables (58k claims
                   carried 8.7k distinct publication dicts and 289
                   distinct reform dicts inline — 20 MB of duplication).
                   The comparisons view re-exposes both columns, so view
                   readers are unaffected; base-table readers join.
- publications   — content-addressed publication dicts
                   (publication_id = sha256(canonical JSON)[:16])
- reforms        — reform_key -> canonical ReformRef JSON (reform_key was
                   already the hash of exactly this JSON, so the table is
                   pure normalization)
- pe_results     — PolicyEngine computations, full history per claim
- baselines      — registry of baseline worlds (issue #13): every claim and
                   every PE run carries a baseline_key FK; the comparisons
                   view exposes both sides and refuses to render plain
                   agreement across different baselines
- diagnoses      — adjudications of material divergences (descriptive
                   register, issue #9: pe_gap / external_issue require a
                   citable known issue in action_link)
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

from .models import (
    CURRENT_LAW_DESCRIPTOR,
    GATED_DIAGNOSIS_CLASSES,
    DiagnosisClass,
    ExternalScore,
    PEResult,
    baseline_key as _baseline_key,
    publication_key as _publication_key,
)

# The null world's key, injected into the view SQL so the guard works on
# fresh files before the registry is seeded.
CURRENT_LAW_KEY = _baseline_key(CURRENT_LAW_DESCRIPTOR)

DDL = """
CREATE TABLE IF NOT EXISTS external_scores (
    claim_id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    source_model TEXT,
    ledger_fact TEXT,
    source_column TEXT,
    publication_id TEXT,
    reform_key TEXT NOT NULL,
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
    period_end INTEGER,
    baseline_key TEXT
);
CREATE INDEX IF NOT EXISTS idx_scores_source ON external_scores(source);
CREATE INDEX IF NOT EXISTS idx_scores_geo ON external_scores(geography);
CREATE INDEX IF NOT EXISTS idx_scores_prog ON external_scores(program);
CREATE INDEX IF NOT EXISTS idx_scores_reform ON external_scores(reform_key);

CREATE TABLE IF NOT EXISTS publications (
    publication_id TEXT PRIMARY KEY,
    publication TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS reforms (
    reform_key TEXT PRIMARY KEY,
    reform_json TEXT NOT NULL
);

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
    annotations TEXT NOT NULL DEFAULT '[]',
    baseline_key TEXT
);
CREATE INDEX IF NOT EXISTS idx_results_claim ON pe_results(claim_id);

CREATE TABLE IF NOT EXISTS baselines (
    baseline_key TEXT PRIMARY KEY,
    label TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL DEFAULT '',
    framework TEXT NOT NULL DEFAULT '',
    spec_json TEXT,
    provenance TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS diagnoses (
    claim_id TEXT PRIMARY KEY REFERENCES external_scores(claim_id),
    diagnosis_class TEXT NOT NULL CHECK (diagnosis_class IN (
        'pe_gap','external_issue','concept_mismatch',
        'methodological_difference','vintage','undiagnosed'
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
    note TEXT NOT NULL DEFAULT '',
    baseline_key TEXT
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

"""

# Everything below is (re)created after _migrate so it may reference
# columns added by migration (baseline_key on pre-#13 files); DROP+CREATE
# keeps the view definition current on old files.
VIEW_DDL = """
CREATE INDEX IF NOT EXISTS idx_scores_baseline
    ON external_scores(baseline_key);
DROP VIEW IF EXISTS comparisons;
CREATE VIEW comparisons AS
SELECT
    s.*,
    p.publication AS publication,
    rf.reform_json AS reform_json,
    r.computed_value AS pe_value,
    r.status AS pe_status,
    r.engine_version,
    r.data_bundle,
    r.pe_construction,
    r.computed_at,
    r.baseline_key AS pe_baseline_key,
    bc.label AS claim_baseline_label,
    bp.label AS pe_baseline_label,
    -- Issue #13 guard: a result computed against a different baseline
    -- world than the claim's can never render as plain agreement — it is
    -- at best a documented construction. (A registry-equivalence table
    -- can relax specific pairs later; none exist yet.)
    CASE
        WHEN r.status = 'comparable'
             AND r.baseline_key IS NOT NULL
             AND s.baseline_key IS NOT NULL
             AND r.baseline_key != s.baseline_key
        THEN 'constructed'
        -- Legacy result with no recorded executed baseline meeting a
        -- claim scored against a non-current-law world: agreement is
        -- unverifiable, never plain.
        WHEN r.status = 'comparable'
             AND r.baseline_key IS NULL
             AND s.baseline_key IS NOT NULL
             AND s.baseline_key != '__CURRENT_LAW_KEY__'
        THEN 'baseline_unvalidated'
        ELSE r.status
    END AS pe_status_effective,
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
LEFT JOIN diagnoses d ON d.claim_id = s.claim_id
LEFT JOIN baselines bc ON bc.baseline_key = s.baseline_key
LEFT JOIN baselines bp ON bp.baseline_key = r.baseline_key
LEFT JOIN publications p ON p.publication_id = s.publication_id
LEFT JOIN reforms rf ON rf.reform_key = s.reform_key;
"""


SCORES_SQL = (
    "INSERT OR REPLACE INTO external_scores"
    " (claim_id, source, source_model, ledger_fact,"
    " source_column, publication_id, reform_key,"
    " metric, unit_concept, period, time_basis, conditions,"
    " geography, program, value, value_kind, status,"
    " calibration_relationship, period_start, period_end, baseline_key)"
    " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
)
# Provenance side tables are content-addressed, so INSERT OR IGNORE is
# exact: identical content maps to the identical key. Every raw
# executemany(SCORES_SQL, ...) site must also executemany these with
# ScorecardDB.provenance_rows(scores) in the same transaction (the
# convenience upsert_scores does it for you); build_db asserts no claim
# references a missing side-table row.
PUBLICATIONS_SQL = "INSERT OR IGNORE INTO publications VALUES (?,?)"
REFORMS_SQL = "INSERT OR IGNORE INTO reforms VALUES (?,?)"
RESULTS_SQL = (
    "INSERT INTO pe_results (claim_id, computed_value, status,"
    " engine_version, data_bundle, pe_construction, run_id,"
    " computed_at, annotations, baseline_key)"
    " VALUES (?,?,?,?,?,?,?,?,?,?)"
)
EXHIBITS_SQL = (
    "INSERT INTO pe_exhibits (exhibit, reform_key, reform_json,"
    " metric, unit_concept, period, time_basis, conditions,"
    " geography, program, value, baseline_value, delta,"
    " engine_version, data_bundle, run_id, computed_at, note,"
    " baseline_key)"
    " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
)
LANE_SQL = (
    "INSERT INTO lanes (lane, stage, detail, updated_at)"
    " VALUES (?,?,?,?) ON CONFLICT(lane) DO UPDATE SET"
    " stage=excluded.stage, detail=excluded.detail,"
    " updated_at=excluded.updated_at"
)
BASELINE_SQL = (
    "INSERT INTO baselines VALUES (?,?,?,?,?,?)"
    " ON CONFLICT(baseline_key) DO UPDATE SET"
    " label=excluded.label, description=excluded.description,"
    " framework=excluded.framework, spec_json=excluded.spec_json,"
    " provenance=excluded.provenance"
)


def _legacy_claim_baseline_key(row) -> str:
    """Exact projection of a legacy claim's baseline world from its own
    reform_json. Absent baseline (missing key or JSON null) IS the null
    current_law world by the registry convention; any other shape —
    non-dict reform_json, falsy-but-present baseline ({} / [] / false),
    non-string policy — fails loudly rather than silently keying current
    law."""
    parsed = json.loads(row["reform_json"])
    if not isinstance(parsed, dict):
        raise ValueError(
            f"{row['claim_id']}: reform_json is not an object: {row['reform_json']!r}"
        )
    descriptor = parsed.get("baseline", None)
    if descriptor is None:
        return CURRENT_LAW_KEY
    return _baseline_key(descriptor)


class ScorecardDB:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(DDL)
        self._migrate()
        self._ensure_view()

    def _ensure_view(self):
        """(Re)create the comparisons view ONLY when its stored
        definition differs from the code's. The old unconditional
        DROP+CREATE wrote a schema change on EVERY open, so a process
        that merely READ the committed DB (tests, exporters) bumped its
        header counters and left the binary dirty — the recurring
        "harmless header churn" the #48/#52 gates kept flagging."""
        ddl = VIEW_DDL.replace("__CURRENT_LAW_KEY__", CURRENT_LAW_KEY)
        index_sql, create = ddl.split("DROP VIEW IF EXISTS comparisons;", 1)
        self.conn.executescript(index_sql)  # IF NOT EXISTS — no-op when present
        expected = create.strip().removesuffix(";")
        stored = self.conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='view' AND name='comparisons'"
        ).fetchone()
        if stored is None or stored["sql"] != expected:
            self.conn.executescript("DROP VIEW IF EXISTS comparisons;" + create)

    def _migrate(self):
        """Bring a pre-existing file up to the current schema.

        CREATE TABLE IF NOT EXISTS leaves old files untouched, so columns
        added later (period_start/period_end 2026-08-02, baseline_key
        2026-08-02 #13) are ALTERed in, and the diagnoses CHECK is
        rebuilt when it predates methodological_difference (issue #9).
        The comparisons view is dropped and recreated after migration so
        its definition always matches the code.
        """

        def cols(table):
            return {r["name"] for r in self.conn.execute(f"PRAGMA table_info({table})")}

        with self.conn:
            score_cols = cols("external_scores")
            for col, typ in (
                ("period_start", "INTEGER"),
                ("period_end", "INTEGER"),
                ("baseline_key", "TEXT"),
            ):
                if col not in score_cols:
                    self.conn.execute(
                        f"ALTER TABLE external_scores ADD COLUMN {col} {typ}"
                    )
            for table in ("pe_results", "pe_exhibits"):
                if "baseline_key" not in cols(table):
                    self.conn.execute(
                        f"ALTER TABLE {table} ADD COLUMN baseline_key TEXT"
                    )
            diag_sql = self.conn.execute(
                "SELECT sql FROM sqlite_master WHERE type='table' AND name='diagnoses'"
            ).fetchone()
            if diag_sql and "methodological_difference" not in diag_sql["sql"]:
                self.conn.executescript(
                    """
                    ALTER TABLE diagnoses RENAME TO diagnoses_old;
                    CREATE TABLE diagnoses (
                        claim_id TEXT PRIMARY KEY
                            REFERENCES external_scores(claim_id),
                        diagnosis_class TEXT NOT NULL CHECK (
                            diagnosis_class IN (
                                'pe_gap','external_issue','concept_mismatch',
                                'methodological_difference','vintage',
                                'undiagnosed'
                            )
                        ),
                        rationale TEXT NOT NULL DEFAULT '',
                        action_link TEXT NOT NULL DEFAULT ''
                    );
                    INSERT INTO diagnoses SELECT * FROM diagnoses_old;
                    DROP TABLE diagnoses_old;
                    """
                )
            # Backfill legacy claims' baseline_key by exact projection
            # from the descriptor each row already carries in reform_json
            # — never an inference (a claim without a baseline descriptor
            # IS the null current_law world by the registry convention).
            # Legacy pe_results stay NULL: the baseline a run actually
            # executed is provenance we don't have; the comparisons view
            # downgrades those to 'baseline_unvalidated' wherever the
            # claim's world is not current law.
            if "reform_json" in cols("external_scores"):
                legacy = self.conn.execute(
                    "SELECT claim_id, reform_json FROM external_scores"
                    " WHERE baseline_key IS NULL"
                ).fetchall()
                if legacy:
                    self.conn.executemany(
                        "UPDATE external_scores SET baseline_key = ?"
                        " WHERE claim_id = ?",
                        [
                            (_legacy_claim_baseline_key(r), r["claim_id"])
                            for r in legacy
                        ],
                    )
            self._intern_provenance(cols)

    def _intern_provenance(self, cols):
        """Migrate a pre-interning file: move the inline publication /
        reform_json columns into the content-addressed side tables and
        drop them. Runs AFTER the legacy baseline backfill (which reads
        the inline reform_json on pre-#13 files). reform_key is by
        construction the hash of exactly the row's reform_json; that
        1:1-ness is asserted, never assumed."""
        if "publication" not in cols("external_scores"):
            return
        clash = self.conn.execute(
            "SELECT reform_key FROM external_scores"
            " GROUP BY reform_key HAVING COUNT(DISTINCT reform_json) > 1"
        ).fetchall()
        if clash:
            raise ValueError(
                "interning migration: reform_key maps to multiple "
                f"reform_json values: {[r['reform_key'] for r in clash]}"
            )
        rows = self.conn.execute(
            "SELECT claim_id, publication, reform_json, reform_key FROM external_scores"
        ).fetchall()
        self.conn.executemany(
            PUBLICATIONS_SQL,
            sorted(
                {
                    (_publication_key(json.loads(r["publication"])), r["publication"])
                    for r in rows
                }
            ),
        )
        self.conn.executemany(
            REFORMS_SQL,
            sorted({(r["reform_key"], r["reform_json"]) for r in rows}),
        )
        if "publication_id" not in cols("external_scores"):
            self.conn.execute(
                "ALTER TABLE external_scores ADD COLUMN publication_id TEXT"
            )
        self.conn.executemany(
            "UPDATE external_scores SET publication_id = ? WHERE claim_id = ?",
            [
                (_publication_key(json.loads(r["publication"])), r["claim_id"])
                for r in rows
            ],
        )
        # The stored view may reference the doomed columns; drop it first
        # (_ensure_view recreates the current definition right after).
        self.conn.execute("DROP VIEW IF EXISTS comparisons")
        self.conn.execute("ALTER TABLE external_scores DROP COLUMN publication")
        self.conn.execute("ALTER TABLE external_scores DROP COLUMN reform_json")

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
            _publication_key(s.publication),
            s.reform.key(),
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
            s.reform.baseline_key(),
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
            r.baseline_key,
        )

    @staticmethod
    def provenance_rows(
        scores: Iterable[ExternalScore],
    ) -> tuple[list[tuple], list[tuple]]:
        """Deduped (publications, reforms) rows for a batch of scores —
        the mandatory companion of any raw executemany(SCORES_SQL, ...)."""
        publications: dict[str, str] = {}
        reforms: dict[str, str] = {}
        for s in scores:
            publications[_publication_key(s.publication)] = json.dumps(
                s.publication, sort_keys=True
            )
            reforms[s.reform.key()] = s.reform.to_json()
        return sorted(publications.items()), sorted(reforms.items())

    def upsert_scores(self, scores: Iterable[ExternalScore]) -> int:
        scores = list(scores)
        rows = [self.score_row(s) for s in scores]
        pub_rows, reform_rows = self.provenance_rows(scores)
        with self.conn:
            self.conn.executemany(PUBLICATIONS_SQL, pub_rows)
            self.conn.executemany(REFORMS_SQL, reform_rows)
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
            r.get("baseline_key"),
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

    def register_baseline(
        self,
        baseline_key: str,
        label: str,
        description: str = "",
        framework: str = "",
        spec_json: Optional[str] = None,
        provenance: str = "",
    ):
        with self.conn:
            self.conn.execute(
                BASELINE_SQL,
                (baseline_key, label, description, framework, spec_json, provenance),
            )

    def unregistered_baselines(self) -> list[str]:
        """baseline_keys referenced by claims or results but missing from
        the registry — runners fail loudly on these so every baseline
        world is deliberately described (issue #13)."""
        return [
            r["baseline_key"]
            for r in self.conn.execute(
                "SELECT DISTINCT baseline_key FROM ("
                "  SELECT baseline_key FROM external_scores"
                "  UNION SELECT baseline_key FROM pe_results"
                "  UNION SELECT baseline_key FROM pe_exhibits)"
                " WHERE baseline_key IS NOT NULL AND baseline_key NOT IN"
                "  (SELECT baseline_key FROM baselines)"
            )
        ]

    def diagnose(
        self,
        claim_id: str,
        diagnosis_class: str,
        rationale: str = "",
        action_link: str = "",
    ):
        # Descriptive register (issue #9): normative classes are gated on
        # a citable known issue; divergence alone never qualifies.
        if DiagnosisClass(diagnosis_class) in GATED_DIAGNOSIS_CLASSES and (
            not action_link
        ):
            raise ValueError(
                f"{diagnosis_class} requires a citable known issue in "
                "action_link (descriptive register, issue #9)"
            )
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
