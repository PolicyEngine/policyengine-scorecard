"""The database is a DERIVED artifact (scorecard_db/build_db.py): build it
BEFORE test collection when absent, so a fresh clone's plain `pytest` runs
the full suite — several modules gate on the DB's existence in
collection-time skipif conditions, which evaluate before any fixture
could build it. CI builds explicitly (with the determinism check) first,
making this a no-op there.

Tests reach the built database through two fixtures, never a copy of
their own: `readonly_scorecard_db`, one read-only file shared by every
test that only reads (shared_db.py), and `writable_scorecard_db`, a
private copy for a test that writes, made as an APFS clone where the
filesystem allows (clone_copy.py)."""

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import clone_copy  # noqa: E402
import shared_db  # noqa: E402

_DB = REPO / "data" / "scorecard.db"


def pytest_configure(config):
    if not _DB.exists():
        from scorecard_db.build_db import build

        build(_DB)


@pytest.fixture(scope="session")
def shared_scorecard_db(tmp_path_factory):
    """The built database as one read-only file per session (per xdist
    worker). Its teardown fails the session if the file's bytes changed."""
    directory = tmp_path_factory.mktemp("shared-db")
    with shared_db.read_only_share(_DB, directory) as path:
        yield path


@pytest.fixture
def readonly_scorecard_db(shared_scorecard_db, request):
    """The shared read-only database, for a test that only reads it. The
    test fails at teardown if it changed the file (shared_db)."""
    with shared_db.unchanged_by(shared_scorecard_db, request.node.nodeid):
        yield shared_scorecard_db


@pytest.fixture
def writable_scorecard_db(tmp_path):
    """A private copy of the built database for a test that writes to it:
    a clone on APFS, which costs only the pages the test changes."""
    path = tmp_path / "scorecard.db"
    clone_copy.copy(_DB, path)
    return path
