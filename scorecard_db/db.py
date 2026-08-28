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
from contextlib import contextmanager
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

EXTERNAL_SCORES_COLUMNS = (
    "claim_id",
    "source",
    "source_model",
    "ledger_fact",
    "source_column",
    "publication_id",
    "reform_key",
    "metric",
    "unit_concept",
    "period",
    "time_basis",
    "conditions",
    "geography",
    "program",
    "value",
    "value_kind",
    "status",
    "calibration_relationship",
    "period_start",
    "period_end",
    "baseline_key",
)

EXTERNAL_SCORES_SCHEMA = """(
    claim_id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    source_model TEXT,
    ledger_fact TEXT,
    source_column TEXT,
    publication_id TEXT NOT NULL,
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
)"""

SCORE_INDEX_SQL = (
    "CREATE INDEX IF NOT EXISTS idx_scores_source ON external_scores(source)",
    "CREATE INDEX IF NOT EXISTS idx_scores_geo ON external_scores(geography)",
    "CREATE INDEX IF NOT EXISTS idx_scores_prog ON external_scores(program)",
    "CREATE INDEX IF NOT EXISTS idx_scores_reform ON external_scores(reform_key)",
)

DDL = (
    "CREATE TABLE IF NOT EXISTS external_scores "
    + EXTERNAL_SCORES_SCHEMA
    + ";\n"
    + """
CREATE INDEX IF NOT EXISTS idx_scores_source ON external_scores(source);
CREATE INDEX IF NOT EXISTS idx_scores_geo ON external_scores(geography);
CREATE INDEX IF NOT EXISTS idx_scores_prog ON external_scores(program);
CREATE INDEX IF NOT EXISTS idx_scores_reform ON external_scores(reform_key);

CREATE TABLE IF NOT EXISTS publications (
    publication_id TEXT PRIMARY KEY NOT NULL,
    publication TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS reforms (
    reform_key TEXT PRIMARY KEY NOT NULL,
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
)

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
# INSERT OR IGNORE is paired with exact post-insert verification by
# ScorecardDB.insert_provenance(). Raw score writers must use that method
# in their enclosing score transaction; using these statements directly
# would make a truncated-hash collision silently retain the older JSON.
PUBLICATIONS_SQL = (
    "INSERT OR IGNORE INTO publications (publication_id, publication) VALUES (?,?)"
)
REFORMS_SQL = "INSERT OR IGNORE INTO reforms (reform_key, reform_json) VALUES (?,?)"
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


PROVENANCE_ORPHANS_SQL = """
SELECT COUNT(*)
FROM external_scores AS s
WHERE s.publication_id IS NULL
   OR NOT EXISTS (
       SELECT 1
       FROM publications AS p
       WHERE p.publication_id = s.publication_id
   )
   OR NOT EXISTS (
       SELECT 1
       FROM reforms AS r
       WHERE r.reform_key = s.reform_key
   )
"""


def provenance_orphan_count(conn: sqlite3.Connection) -> int:
    """Count claims with NULL or dangling provenance references.

    Correlated NOT EXISTS is deliberate: unlike NOT IN, a schema-valid
    NULL key in an older/malformed side table cannot poison the predicate.
    """
    return conn.execute(PROVENANCE_ORPHANS_SQL).fetchone()[0]


def require_complete_provenance(
    conn: sqlite3.Connection, *, context: str = "operation"
) -> None:
    """Fail loudly before a build/export can publish incomplete claims."""
    orphans = provenance_orphan_count(conn)
    if orphans:
        raise SystemExit(
            f"{context}: {orphans} claims reference missing provenance rows"
        )


@contextmanager
def _savepoint(conn: sqlite3.Connection, name: str):
    """Nested-safe explicit transaction for SQLite schema changes.

    Python's sqlite3 context manager does not itself begin a transaction
    for DDL, so DROP/CREATE pairs need an explicit savepoint even when the
    caller is written as ``with conn:``.
    """
    conn.execute(f"SAVEPOINT {name}")
    try:
        yield
    except BaseException:
        conn.execute(f"ROLLBACK TO {name}")
        conn.execute(f"RELEASE {name}")
        raise
    else:
        conn.execute(f"RELEASE {name}")


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
        index_sql, expected = self._view_parts()
        stored = self.conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='view' AND name='comparisons'"
        ).fetchone()
        if stored is None or stored["sql"] != expected:
            # DDL does not make ``with self.conn`` start a transaction.
            # The explicit savepoint makes DROP+CREATE one atomic schema
            # replacement, including when no other write is in flight.
            with _savepoint(self.conn, "refresh_comparisons_view"):
                self._replace_view(index_sql, expected)
        else:
            # The view can be current while an index was removed manually.
            # A single CREATE INDEX IF NOT EXISTS statement is atomic itself.
            self.conn.execute(index_sql)

    @staticmethod
    def _view_parts() -> tuple[str, str]:
        ddl = VIEW_DDL.replace("__CURRENT_LAW_KEY__", CURRENT_LAW_KEY)
        index_sql, create = ddl.split("DROP VIEW IF EXISTS comparisons;", 1)
        return index_sql.strip().removesuffix(";"), create.strip().removesuffix(";")

    def _replace_view(self, index_sql: str | None = None, create: str | None = None):
        """Replace comparisons inside a caller-owned transaction/savepoint."""
        if index_sql is None or create is None:
            index_sql, create = self._view_parts()
        self.conn.execute(index_sql)
        self.conn.execute("DROP VIEW IF EXISTS comparisons")
        self.conn.execute(create)

    def _migrate(self):
        """Bring a pre-existing file up to the current schema.

        CREATE TABLE IF NOT EXISTS leaves old files untouched, so columns
        added later (period_start/period_end 2026-08-02, baseline_key
        2026-08-02 #13) are ALTERed in, and the diagnoses CHECK is
        rebuilt when it predates methodological_difference (issue #9).
        An interning rebuild recreates the comparisons view before its
        savepoint is committed; _ensure_view conditionally repairs older
        definitions for migrations that do not rebuild external_scores.
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
        rebuild external_scores in the exact fresh-schema order. Runs
        AFTER the legacy baseline backfill (which reads inline reform_json).
        The whole side insert / rebuild / view replacement is one explicit
        savepoint, including for an empty legacy table."""
        score_cols = cols("external_scores")
        inline = {"publication", "reform_json"} & score_cols
        if not inline:
            return
        if inline != {"publication", "reform_json"}:
            raise ValueError(
                "interning migration: expected publication and reform_json "
                f"together, found {sorted(inline)}"
            )
        with _savepoint(self.conn, "intern_provenance"):
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
                "SELECT claim_id, publication, reform_json, reform_key"
                " FROM external_scores"
            ).fetchall()
            publication_map: dict[str, str] = {}
            publication_values: dict[str, str] = {}
            for row in rows:
                parsed = json.loads(row["publication"])
                publication_id = _publication_key(parsed)
                canonical = json.dumps(parsed, sort_keys=True)
                if (
                    publication_id in publication_values
                    and publication_values[publication_id] != canonical
                ):
                    raise ValueError(
                        "publication provenance collision for key "
                        f"{publication_id}: multiple JSON values in migration"
                    )
                publication_map[row["publication"]] = publication_id
                publication_values[publication_id] = canonical
            pub_rows = sorted(publication_values.items())
            reform_rows = sorted({(r["reform_key"], r["reform_json"]) for r in rows})
            self.insert_provenance(pub_rows, reform_rows)

            self.conn.execute(
                "CREATE TEMP TABLE _intern_publications ("
                " publication TEXT PRIMARY KEY NOT NULL,"
                " publication_id TEXT NOT NULL)"
            )
            self.conn.executemany(
                "INSERT INTO _intern_publications VALUES (?,?)",
                sorted(publication_map.items()),
            )
            self.conn.execute(
                "CREATE TABLE _external_scores_interned " + EXTERNAL_SCORES_SCHEMA
            )
            column_sql = ", ".join(EXTERNAL_SCORES_COLUMNS)
            self.conn.execute(
                f"INSERT INTO _external_scores_interned ({column_sql}) "
                "SELECT s.claim_id, s.source, s.source_model, s.ledger_fact,"
                " s.source_column, m.publication_id, s.reform_key, s.metric,"
                " s.unit_concept, s.period, s.time_basis, s.conditions,"
                " s.geography, s.program, s.value, s.value_kind, s.status,"
                " s.calibration_relationship, s.period_start, s.period_end,"
                " s.baseline_key FROM external_scores AS s"
                " JOIN _intern_publications AS m"
                " ON m.publication = s.publication"
            )
            copied = self.conn.execute(
                "SELECT COUNT(*) FROM _external_scores_interned"
            ).fetchone()[0]
            if copied != len(rows):
                raise ValueError(
                    "interning migration: publication mapping copied "
                    f"{copied} of {len(rows)} claims"
                )

            # The old view can reference the inline columns. Recreate it
            # against the renamed fresh-shape table before releasing the
            # savepoint, so no committed migration state lacks comparisons.
            self.conn.execute("DROP VIEW IF EXISTS comparisons")
            self.conn.execute("DROP TABLE external_scores")
            self.conn.execute(
                "ALTER TABLE _external_scores_interned RENAME TO external_scores"
            )
            self.conn.execute("DROP TABLE _intern_publications")
            for index_sql in SCORE_INDEX_SQL:
                self.conn.execute(index_sql)
            self._replace_view()
            self.prune_provenance()

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

        def remember(rows: dict[str, str], key: str, value: str, kind: str) -> None:
            if key in rows and rows[key] != value:
                raise ValueError(
                    f"{kind} provenance collision for key {key}: "
                    "multiple JSON values in one batch"
                )
            rows[key] = value

        for s in scores:
            remember(
                publications,
                _publication_key(s.publication),
                json.dumps(s.publication, sort_keys=True),
                "publication",
            )
            remember(reforms, s.reform.key(), s.reform.to_json(), "reform")
        return sorted(publications.items()), sorted(reforms.items())

    def insert_provenance(
        self, pub_rows: Iterable[tuple], reform_rows: Iterable[tuple]
    ) -> None:
        """Insert side rows and verify every key's stored JSON exactly.

        Transaction ownership deliberately stays with the caller so raw
        writers can include provenance, claims, results, and lane state in
        one outer transaction. A collision raises before that transaction
        can commit and names the conflicting shipped 16-hex key.
        """
        batches = (
            (
                "publication",
                "publications",
                "publication_id",
                "publication",
                PUBLICATIONS_SQL,
                list(pub_rows),
            ),
            (
                "reform",
                "reforms",
                "reform_key",
                "reform_json",
                REFORMS_SQL,
                list(reform_rows),
            ),
        )
        for kind, table, key_column, json_column, insert_sql, rows in batches:
            self.conn.executemany(insert_sql, rows)
            for key, incoming in rows:
                stored = self.conn.execute(
                    f"SELECT {json_column} FROM {table} WHERE {key_column} = ?",
                    (key,),
                ).fetchone()
                if stored is None or stored[json_column] != incoming:
                    raise ValueError(
                        f"{kind} provenance collision for key {key}: "
                        "incoming JSON does not match stored JSON"
                    )

    def prune_provenance(self) -> None:
        """Remove side rows unreferenced by any claim.

        This method does not own a transaction; writers call it after their
        score changes inside the same enclosing transaction.
        """
        self.conn.execute(
            "DELETE FROM publications WHERE NOT EXISTS ("
            " SELECT 1 FROM external_scores AS s"
            " WHERE s.publication_id = publications.publication_id)"
        )
        self.conn.execute(
            "DELETE FROM reforms WHERE NOT EXISTS ("
            " SELECT 1 FROM external_scores AS s"
            " WHERE s.reform_key = reforms.reform_key)"
        )

    def upsert_scores(self, scores: Iterable[ExternalScore]) -> int:
        scores = list(scores)
        rows = [self.score_row(s) for s in scores]
        pub_rows, reform_rows = self.provenance_rows(scores)
        with self.conn:
            self.insert_provenance(pub_rows, reform_rows)
            self.conn.executemany(SCORES_SQL, rows)
            self.prune_provenance()
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
