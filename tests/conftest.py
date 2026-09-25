"""The database is a DERIVED artifact (scorecard_db/build_db.py): build it
BEFORE test collection when absent, so a fresh clone's plain `pytest` runs
the full suite — several modules gate on the DB's existence in
collection-time skipif conditions, which evaluate before any fixture
could build it. CI builds explicitly (with the determinism check) first,
making this a no-op there."""

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

_DB = REPO / "data" / "scorecard.db"


def pytest_configure(config):
    if not _DB.exists():
        from scorecard_db.build_db import build

        build(_DB)
