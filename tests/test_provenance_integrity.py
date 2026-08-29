"""Fail-loud checks for missing interned provenance rows."""

import sqlite3

import pytest

from scorecard_db.build_db import _provenance_gate
from scorecard_db.db import provenance_orphan_count


@pytest.fixture()
def nullable_provenance_db():
    """A pre-hardening shape whose TEXT primary keys still accept NULL."""
    conn = sqlite3.connect(":memory:")
    conn.executescript(
        """
        CREATE TABLE external_scores (
            claim_id TEXT PRIMARY KEY,
            publication_id TEXT,
            reform_key TEXT
        );
        CREATE TABLE publications (
            publication_id TEXT PRIMARY KEY,
            publication TEXT NOT NULL
        );
        CREATE TABLE reforms (
            reform_key TEXT PRIMARY KEY,
            reform_json TEXT NOT NULL
        );

        INSERT INTO publications VALUES (NULL, '{"registry":"poison"}');
        INSERT INTO publications VALUES ('valid-publication', '{}');
        INSERT INTO reforms VALUES (NULL, '{"framework":"poison"}');
        INSERT INTO reforms VALUES ('valid-reform', '{}');
        INSERT INTO external_scores VALUES (
            'healthy', 'valid-publication', 'valid-reform'
        );
        """
    )
    try:
        yield conn
    finally:
        conn.close()


@pytest.mark.parametrize(
    ("publication_id", "reform_key"),
    [
        ("missing-publication", "valid-reform"),
        ("valid-publication", "missing-reform"),
    ],
    ids=("missing-publication", "missing-reform"),
)
def test_build_gate_counts_orphans_despite_null_poison(
    nullable_provenance_db, publication_id, reform_key
):
    conn = nullable_provenance_db
    conn.execute(
        "INSERT INTO external_scores VALUES ('broken', ?, ?)",
        (publication_id, reform_key),
    )

    assert provenance_orphan_count(conn) == 1
    with pytest.raises(
        SystemExit,
        match=r"build_db: 1 claims reference missing provenance rows",
    ):
        _provenance_gate(conn)
