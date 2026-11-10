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
import warnings
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


def _bring_up_to_date(path):
    """Open the share once before it goes read-only, so that no test's
    ScorecardDB has to migrate it. This writes nothing to a database this
    code built; an older data/scorecard.db is migrated in the share, as a
    test's first open migrated it in place before the share existed."""
    if shared_db.bring_up_to_date(path):
        warnings.warn(
            shared_db.StaleDatabaseWarning(
                f"{_DB} predates the schema in scorecard_db/db.py, so the "
                "tests read a copy migrated to it. Delete the file and run "
                "pytest again, which rebuilds a missing one (tests/conftest.py)."
            )
        )


@pytest.fixture(scope="session")
def shared_scorecard_db(tmp_path_factory):
    """The built database as one read-only file per session (per xdist
    worker). Its teardown fails the session if the file's bytes changed."""
    directory = tmp_path_factory.mktemp("shared-db")
    with shared_db.read_only_share(_DB, directory, _bring_up_to_date) as path:
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
