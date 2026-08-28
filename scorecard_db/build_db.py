"""Build the scorecard database from committed inputs — the ONE entrypoint.

The database is a DERIVED artifact: every table is a deterministic
function of the vendored primary sources, staged campaign/RV files, and
feed inputs committed to this repo. It therefore does not live in git
(the committed blob reached 55 MB, and rebuild-vs-committed diffs showed
the blob silently lagging the code: solo exhibits it never received,
placeholder timestamps, unstamped legacy baseline provenance). CI builds
it fresh before the test suite; the publish step uploads the built file
so consumers can fetch instead of rebuilding.

Chain order is dependency order and is part of the contract:
    urban        Urban SotSN claims + platform-era results (tidy CSV)
    harvest      seven 2026-08-02 US source adapters + registry + lanes
    reform_validation  populace RV registry (committed raw artifacts)
    platform     full comparison grid results (data/comparison.json)
    solo         solo-counterfactual results + exhibits
    diagnoses    curated diagnosis rows
    campaign_us  staged day-1/day-2 campaign results (claim matching)
    uk_externals five UK primary-source families + Chronicle staging
    uk_deductions FRR family
    produce_uk + campaign_uk  archive-resolved UK reckoner attaches
    be_jrc      JRC EUROMOD-BE model claims + honest demo attachments;
                final so its 2026-08-21 lane update cannot be regressed by
                an older feed sync

Usage:
    PYTHONPATH=. python -m scorecard_db.build_db [data/scorecard.db]
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import sys
from pathlib import Path

from be import ingest_jrc_country_report

from . import (
    ingest_campaign,
    ingest_diagnoses,
    ingest_harvest,
    ingest_platform,
    ingest_reform_validation,
    ingest_solo,
    ingest_uk_deductions,
    ingest_uk_externals,
    ingest_urban,
    produce_campaign_uk,
)


def content_hash(db_path: Path) -> str:
    """Order-insensitive logical hash over every table (autoincrement
    ids excluded) — two builds from the same inputs must match."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    digest = hashlib.sha256()
    tables = sorted(
        r[0]
        for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
            " AND name NOT LIKE 'sqlite_%'"
        )
    )
    for t in tables:
        cols = [r[1] for r in conn.execute(f"PRAGMA table_info({t})") if r[1] != "id"]
        sel = ", ".join(cols)
        rows = sorted(repr(tuple(r)) for r in conn.execute(f"SELECT {sel} FROM {t}"))
        digest.update(t.encode())
        for row in rows:
            digest.update(row.encode())
    conn.close()
    return digest.hexdigest()


def build(db_path: Path) -> dict:
    """Build from scratch. Refuses to overwrite an existing file so a
    stale artifact can never absorb a partial chain — delete it first."""
    if db_path.exists():
        raise SystemExit(
            f"{db_path} exists — the build is from-scratch only; delete the "
            "old artifact first (it is derived, nothing is lost)"
        )
    steps = [
        ("urban", lambda: ingest_urban.ingest(db_path)),
        ("harvest", lambda: ingest_harvest.ingest(db_path)),
        ("reform_validation", lambda: ingest_reform_validation.ingest(db_path)),
        ("platform", lambda: ingest_platform.ingest(db_path)),
        ("solo", lambda: ingest_solo.ingest(db_path)),
        ("diagnoses", lambda: ingest_diagnoses.ingest(db_path)),
        ("campaign_us", lambda: ingest_campaign.ingest(db_path)),
        ("uk_externals", lambda: ingest_uk_externals.ingest(db_path)),
        ("uk_deductions", lambda: ingest_uk_deductions.ingest(db_path)),
        ("produce_uk", lambda: produce_campaign_uk.produce(db_path)),
        (
            "campaign_uk",
            lambda: ingest_campaign.ingest(db_path, produce_campaign_uk.RESOLVED),
        ),
        ("be_jrc", lambda: ingest_jrc_country_report.ingest(db_path)),
    ]
    summary: dict = {"steps": {}}
    for name, fn in steps:
        summary["steps"][name] = fn()
    # id-columns are excluded from the content hash as physical artifacts;
    # that is only sound while no (claim_id, computed_at) pair repeats,
    # because the exporters use id as the tie-breaker in ORDER BY — a tie
    # would let insert order leak into populations.json.
    conn = sqlite3.connect(db_path)
    ties = conn.execute(
        "SELECT claim_id, computed_at, COUNT(*) FROM pe_results"
        " GROUP BY 1, 2 HAVING COUNT(*) > 1"
    ).fetchall()
    # Interned provenance must be complete: a claim referencing a missing
    # publications/reforms row means a writer bypassed provenance_rows.
    orphans = conn.execute(
        "SELECT COUNT(*) FROM external_scores WHERE publication_id IS NULL"
        " OR publication_id NOT IN (SELECT publication_id FROM publications)"
        " OR reform_key NOT IN (SELECT reform_key FROM reforms)"
    ).fetchone()[0]
    conn.close()
    if ties:
        raise SystemExit(f"pe_results (claim_id, computed_at) ties: {ties[:3]}")
    if orphans:
        raise SystemExit(
            f"{orphans} claims reference missing provenance rows — a raw"
            " SCORES_SQL writer skipped ScorecardDB.provenance_rows"
        )
    summary["content_hash"] = content_hash(db_path)
    summary["bytes"] = db_path.stat().st_size
    return summary


if __name__ == "__main__":
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "data/scorecard.db")
    print(json.dumps(build(out), indent=1, default=str))
