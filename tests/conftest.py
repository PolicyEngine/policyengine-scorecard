"""The database is a DERIVED artifact (scorecard_db/build_db.py): build it
once per test session when absent so a fresh clone's `pytest` just works.
CI builds explicitly (with the determinism check) before pytest, making
this a no-op there."""

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))


@pytest.fixture(scope="session", autouse=True)
def built_db():
    db = REPO / "data" / "scorecard.db"
    if not db.exists():
        from scorecard_db.build_db import build

        build(db)
    return db
