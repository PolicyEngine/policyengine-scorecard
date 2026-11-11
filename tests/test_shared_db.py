"""The shared read-only database: what it is, and that no test can change it.

Tests that only read take `readonly_scorecard_db`, one read-only clone of
data/scorecard.db per session (shared_db.py, wired up in conftest.py). This
module checks the share against the built database, checks that SQLite and
the file system both refuse writes to it, and then runs inner pytest
sessions, through the real conftest fixtures, in which a read-only test
writes to the share or clears its read-only mode: each such session fails,
and its report names the test. One more inner session starts from a
database whose schema predates the code: its readers pass, the source keeps
its bytes, and the report says to rebuild it. Between the two, a section
checks that a copy holds what SQLite's readers see when a writer died
mid-transaction, while a writer holds the file, when a writer tries to
commit during the copy, and when the database runs in WAL mode.
"""

import contextlib
import importlib.util
import os
import sqlite3
import stat
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

import clone_copy
import pytest
import shared_db
from hypothesis import given, settings
from hypothesis import strategies as st

from scorecard_db import ScorecardDB

pytest_plugins = ["pytester"]

TESTS = Path(__file__).resolve().parent
BUILT = TESTS.parent / "data" / "scorecard.db"


# --- the share --------------------------------------------------------------


def test_the_share_is_the_built_database_and_read_only(shared_scorecard_db, tmp_path):
    # The built database as ScorecardDB's open leaves it: the file itself
    # when this code built it, or the file migrated to the code's schema
    # when it predates it (conftest.py warns then).
    expected = Path(clone_copy.copy2(BUILT, tmp_path / BUILT.name))
    stale = shared_db.bring_up_to_date(expected)
    assert shared_scorecard_db != BUILT
    assert shared_scorecard_db.name == BUILT.name
    assert shared_db.sha256(shared_scorecard_db) == shared_db.sha256(expected)
    if not stale:  # the usual case, and CI's: the share has the file's bytes
        assert shared_db.sha256(shared_scorecard_db) == shared_db.sha256(BUILT)
    assert stat.S_IMODE(os.stat(shared_scorecard_db).st_mode) == 0o444
    assert shared_db.siblings(shared_scorecard_db) == []


def test_sqlite_refuses_a_write_through_the_share(readonly_scorecard_db):
    conn = sqlite3.connect(readonly_scorecard_db)
    with pytest.raises(sqlite3.OperationalError, match="readonly"):
        conn.execute("CREATE TABLE written_by_a_test (x)")
    conn.close()
    # The repository's own reader opens it: its schema checks only read.
    db = ScorecardDB(readonly_scorecard_db)
    with pytest.raises(sqlite3.OperationalError, match="readonly"):
        db.conn.execute("DELETE FROM lanes")
    db.close()


@pytest.mark.skipif(os.geteuid() == 0, reason="root ignores file modes")
def test_the_file_system_refuses_to_open_the_share_for_writing(
    readonly_scorecard_db,
):
    with pytest.raises(PermissionError):
        open(readonly_scorecard_db, "r+b")


def test_a_writable_copy_is_private(writable_scorecard_db, shared_scorecard_db):
    conn = sqlite3.connect(writable_scorecard_db)
    conn.execute("DELETE FROM lanes")
    conn.commit()
    assert conn.execute("SELECT COUNT(*) FROM lanes").fetchone() == (0,)
    conn.close()
    for untouched in (BUILT, shared_scorecard_db):
        with sqlite3.connect(f"file:{untouched}?mode=ro", uri=True) as other:
            assert other.execute("SELECT COUNT(*) FROM lanes").fetchone()[0] > 0


# --- the guards, on a small database ----------------------------------------


def _small_database(path: Path) -> Path:
    """A database with one table of 500 rows and none of ScorecardDB's
    schema: to ScorecardDB, a file whose schema predates the code."""
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE t (x)")
    conn.executemany("INSERT INTO t VALUES (?)", [(i,) for i in range(500)])
    conn.commit()
    conn.close()
    return path


def _current_database(path: Path) -> Path:
    """The same table in a file with this code's schema, as a build leaves
    it: ScorecardDB's open writes nothing to it."""
    ScorecardDB(path).close()
    return _small_database(path)


def test_bringing_a_schema_up_to_date_writes_only_to_an_older_one(tmp_path):
    """The share test above relies on this: two migrations of one older file
    agree byte for byte, and a current file takes no write at all."""
    older = _small_database(tmp_path / "older.db")
    migrated = []
    for name in ("a.db", "b.db"):
        path = Path(clone_copy.copy2(older, tmp_path / name))
        assert shared_db.bring_up_to_date(path)
        migrated.append(shared_db.sha256(path))
    assert migrated[0] == migrated[1] != shared_db.sha256(older)
    current = _current_database(tmp_path / "current.db")
    before = shared_db.sha256(current)
    assert not shared_db.bring_up_to_date(current)
    assert shared_db.sha256(current) == before


def _folder(parent, name) -> Path:
    path = Path(parent) / name
    path.mkdir()
    return path


def _overwrite(path: Path, offset: int, data: bytes) -> None:
    """Write around the mode bits, as a test running as root could."""
    mode = stat.S_IMODE(os.stat(path).st_mode)
    os.chmod(path, 0o644)
    with open(path, "r+b") as fh:
        fh.seek(offset)
        fh.write(data)
    os.chmod(path, mode)


@settings(max_examples=60, deadline=None)
@given(where=st.floats(0, 1, exclude_max=True), flip=st.integers(0, 255))
def test_the_session_check_catches_any_byte_changed(tmp_path_factory, where, flip):
    """Any change to any byte of the share fails the session's check, and an
    unchanged share passes it; either way the share ends writable, so the
    retention policy can delete it."""
    # One folder per example, deleted as the example ends.
    with tempfile.TemporaryDirectory(dir=tmp_path_factory.getbasetemp()) as d:
        source = _small_database(Path(d) / "source.db")
        offset = int(where * source.stat().st_size)
        with pytest.raises(shared_db.SharedDatabaseWritten) if flip else _passes():
            with shared_db.read_only_share(source, _folder(d, "share")) as share:
                original = share.read_bytes()[offset]
                if flip:
                    _overwrite(share, offset, bytes([original ^ flip]))
        assert stat.S_IMODE(os.stat(Path(d) / "share" / source.name).st_mode) == 0o644


class _passes:
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def test_the_session_check_catches_a_journal_left_beside_the_share(tmp_path):
    source = _small_database(tmp_path / "source.db")
    with pytest.raises(shared_db.SharedDatabaseWritten, match="-journal"):
        with shared_db.read_only_share(source, _folder(tmp_path, "share")) as share:
            (share.parent / f"{share.name}-journal").write_bytes(b"")


def test_the_per_test_check_names_the_test_that_wrote(tmp_path):
    source = _small_database(tmp_path / "source.db")
    with shared_db.read_only_share(source, _folder(tmp_path, "share")) as share:
        with pytest.raises(shared_db.SharedDatabaseWritten, match="test_y"):
            with shared_db.unchanged_by(share, "tests/x.py::test_y"):
                _overwrite(share, 100, b"\0")
        _overwrite(share, 100, source.read_bytes()[100:101])
        # Reads leave the signature as it was.
        with shared_db.unchanged_by(share, "tests/x.py::test_z"):
            with sqlite3.connect(share) as conn:
                assert conn.execute("SELECT COUNT(*) FROM t").fetchone() == (500,)


# --- copying a database mid-write --------------------------------------------

ROWS = 20_000

# A writer whose transaction outgrows a five-page cache: SQLite writes the
# original pages to the -journal and then the changed ones into the database
# file itself, before any commit.
_WRITE_UNCOMMITTED = """
import os, sqlite3, sys
conn = sqlite3.connect(sys.argv[1], isolation_level=None)
conn.execute("PRAGMA cache_size=5")
conn.execute("BEGIN")
conn.execute("UPDATE t SET s = 'uncommitted'")
if sys.argv[2] == "die":
    os._exit(0)  # no rollback: a hot journal stays beside the file
print("written", flush=True)
sys.stdin.readline()  # hold the file until told to let go
conn.execute("ROLLBACK")
"""


def _rows_database(path: Path, rows: int = ROWS) -> Path:
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE t (i INTEGER PRIMARY KEY, s TEXT)")
    conn.executemany(
        "INSERT INTO t VALUES (?, 'committed')", ((i,) for i in range(rows))
    )
    conn.commit()
    conn.close()
    return path


def _values(path) -> dict:
    with contextlib.closing(sqlite3.connect(f"file:{path}?mode=ro", uri=True)) as c:
        return dict(c.execute("SELECT s, COUNT(*) FROM t GROUP BY s").fetchall())


def _file_alone(source: Path, scratch: Path) -> dict:
    """What a copy of the database file alone, without its journal, holds."""
    return _values(clone_copy.copy2(source, _folder(scratch, "raw") / source.name))


def _snapshot_by(how: str, source: Path, scratch: Path) -> dict:
    """The values in a copy made the way the share or a private copy is."""
    if how == "share":
        with shared_db.read_only_share(source, _folder(scratch, "share")) as share:
            return _values(share)
    copy = shared_db.snapshot(source, scratch / "private.db", clone_copy.copy)
    return _values(copy)


@pytest.mark.parametrize("how", ["share", "private"])
def test_a_copy_drops_what_a_writer_that_died_left_uncommitted(tmp_path, how):
    source = _rows_database(tmp_path / "source.db")
    subprocess.run(
        [sys.executable, "-c", _WRITE_UNCOMMITTED, str(source), "die"], check=True
    )
    journal = tmp_path / "source.db-journal"
    assert journal.stat().st_size > 0
    assert _file_alone(source, tmp_path).get("uncommitted", 0) > ROWS // 2
    assert _snapshot_by(how, source, tmp_path) == {"committed": ROWS}
    # SQLite rolled the journal back into the file, as any reader's open would.
    assert not journal.exists()
    assert _values(source) == {"committed": ROWS}


@pytest.mark.parametrize("how", ["share", "private"])
def test_a_copy_waits_for_a_writer_that_holds_the_file(tmp_path, how):
    source = _rows_database(tmp_path / "source.db")
    # The writer holds its uncommitted pages in the file until told to roll
    # back. A timer tells it half a second after the copy starts, so a copy
    # that waits for the writer takes that long and finds the committed rows.
    # Leaving the block closes the pipes and waits for the writer.
    with subprocess.Popen(
        [sys.executable, "-c", _WRITE_UNCOMMITTED, str(source), "hold"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
    ) as writer:
        assert writer.stdout.readline() == "written\n"
        assert _file_alone(source, tmp_path).get("uncommitted", 0) > ROWS // 2

        def let_go():
            writer.stdin.write("go\n")
            writer.stdin.flush()

        timer = threading.Timer(0.5, let_go)
        started = time.monotonic()
        timer.start()
        try:
            values = _snapshot_by(how, source, tmp_path)
            waited = time.monotonic() - started  # before join(), which waits too
        finally:
            timer.join()
        assert values == {"committed": ROWS}
        assert waited >= 0.5
    assert writer.returncode == 0
    assert _values(source) == {"committed": ROWS}


def test_a_copy_of_a_wal_database_holds_the_pages_its_wal_file_holds(tmp_path):
    source = tmp_path / "wal.db"
    holder = sqlite3.connect(source, isolation_level=None)
    try:
        holder.execute("PRAGMA journal_mode=WAL")
        holder.execute("PRAGMA wal_autocheckpoint=0")  # keep every page in -wal
        holder.execute("BEGIN")
        holder.execute("CREATE TABLE t (i INTEGER PRIMARY KEY, s TEXT)")
        holder.executemany(
            "INSERT INTO t VALUES (?, 'committed')", ((i,) for i in range(500))
        )
        holder.execute("COMMIT")
        assert (tmp_path / "wal.db-wal").stat().st_size > 0
        with pytest.raises(sqlite3.OperationalError, match="no such table"):
            _file_alone(source, tmp_path)
        with shared_db.read_only_share(source, _folder(tmp_path, "share")) as share:
            assert _values(share) == {"committed": 500}
            assert share.read_bytes()[18:20] == b"\x01\x01"  # rollback mode
    finally:
        holder.close()


def test_no_writer_commits_while_a_copy_runs(tmp_path):
    """The copy runs inside a read transaction, so a writer that starts
    after it began cannot commit until it ends; once it ends, the same
    write goes through."""
    source = _rows_database(tmp_path / "source.db", rows=500)

    def copy_while_a_writer_tries(src, dst):
        writer = sqlite3.connect(src, timeout=0, isolation_level=None)
        try:
            with pytest.raises(sqlite3.OperationalError, match="locked"):
                writer.execute("UPDATE t SET s = 'during the copy'")
        finally:
            writer.close()
        return clone_copy.copy2(src, dst)

    copy = shared_db.snapshot(source, tmp_path / "copy.db", copy_while_a_writer_tries)
    assert _values(copy) == {"committed": 500}
    with contextlib.closing(sqlite3.connect(source, isolation_level=None)) as writer:
        writer.execute("UPDATE t SET s = 'after the copy'")
    assert _values(source) == {"after the copy": 500}


def test_a_copy_never_creates_a_missing_database(tmp_path):
    with pytest.raises(sqlite3.OperationalError):
        shared_db.snapshot(tmp_path / "missing.db", tmp_path / "copy.db")
    assert sorted(p.name for p in tmp_path.iterdir()) == []


# --- inner sessions through the real fixtures ---------------------------------

INNER_CONFTEST = """
import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, {tests!r})
spec = importlib.util.spec_from_file_location("scorecard_conftest", {conftest!r})
real = importlib.util.module_from_spec(spec)
spec.loader.exec_module(real)
# The real fixtures, pointed at a small database instead of the built one.
real._DB = Path({source!r})
shared_scorecard_db = real.shared_scorecard_db
readonly_scorecard_db = real.readonly_scorecard_db
writable_scorecard_db = real.writable_scorecard_db
"""


@pytest.fixture
def inner(pytester, tmp_path):
    """Run ``body`` as an inner session's test file, its database made by
    ``make``; return the result, the database and its SHA-256 before."""
    source = tmp_path / "scorecard.db"
    pytester.makeconftest(
        INNER_CONFTEST.format(
            tests=str(TESTS), conftest=str(TESTS / "conftest.py"), source=str(source)
        )
    )

    def run(body, make=_current_database):
        before = shared_db.sha256(make(source))
        pytester.makepyfile(test_inner="import os, sqlite3\n" + body)
        return pytester.runpytest("-p", "no:cacheprovider", "-q"), source, before

    return run


def test_an_inner_session_of_readers_passes(inner):
    result, source, before = inner(
        "def test_reads(readonly_scorecard_db):\n"
        "    with sqlite3.connect(readonly_scorecard_db) as conn:\n"
        "        assert conn.execute('SELECT COUNT(*) FROM t').fetchone() == (500,)\n"
        "def test_writes_its_own_copy(writable_scorecard_db):\n"
        "    with sqlite3.connect(writable_scorecard_db) as conn:\n"
        "        conn.execute('DELETE FROM t')\n"
    )
    result.assert_outcomes(passed=2)
    assert "StaleDatabaseWarning" not in result.stdout.str()
    assert shared_db.sha256(source) == before


def test_an_older_schema_is_migrated_in_the_share_never_in_place(inner):
    """ScorecardDB's open migrates a file whose schema predates the code. The
    session does that to the share before sealing it, so a reader that opens
    ScorecardDB passes; the source keeps its bytes, and the report says to
    rebuild it. Without that step this reader would fail with "attempt to
    write a readonly database", and a test that opened the committed file
    in place would have migrated it."""
    result, source, before = inner(
        "from scorecard_db import ScorecardDB\n"
        "def test_opens_it(readonly_scorecard_db):\n"
        "    db = ScorecardDB(readonly_scorecard_db)\n"
        "    assert db.conn.execute('SELECT COUNT(*) FROM t').fetchone()[0] == 500\n"
        "    db.close()\n",
        make=_small_database,
    )
    result.assert_outcomes(passed=1)
    out = result.stdout.str()
    assert "StaleDatabaseWarning" in out and "a schema other than" in out
    assert shared_db.sha256(source) == before
    with sqlite3.connect(f"file:{source}?mode=ro", uri=True) as conn:
        tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master")}
    assert tables == {"t"}, "the source keeps its older schema"


def _died_mid_write(path: Path) -> Path:
    """A database with this code's schema, left with a hot journal."""
    ScorecardDB(path).close()
    _rows_database(path)
    subprocess.run(
        [sys.executable, "-c", _WRITE_UNCOMMITTED, str(path), "die"], check=True
    )
    assert Path(f"{path}-journal").stat().st_size > 0
    return path


@pytest.mark.parametrize("fixture", ["readonly_scorecard_db", "writable_scorecard_db"])
def test_each_fixture_holds_the_committed_rows_when_a_writer_died(inner, fixture):
    """Each fixture alone, so each is the first to copy the torn source."""
    result, source, _ = inner(
        f"def test_reads({fixture}):\n"
        f"    with sqlite3.connect({fixture}) as conn:\n"
        "        rows = dict(conn.execute('SELECT s, COUNT(*) FROM t GROUP BY s'))\n"
        f"    assert rows == {{'committed': {ROWS}}}, rows\n",
        make=_died_mid_write,
    )
    result.assert_outcomes(passed=1)
    assert not Path(f"{source}-journal").exists()


def test_a_read_only_test_that_writes_through_sqlite_fails(inner):
    result, source, before = inner(
        "def test_writes(readonly_scorecard_db):\n"
        "    with sqlite3.connect(readonly_scorecard_db) as conn:\n"
        "        conn.execute('DELETE FROM t')\n"
    )
    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines(["*attempt to write a readonly database*"])
    assert "SharedDatabaseWritten" not in result.stdout.str()


def test_a_read_only_test_that_writes_around_the_mode_fails(inner):
    """A write that gets past the mode bits (here the test restores them; a
    process running as root needs no chmod) fails the test that made it at
    its teardown, and fails the session's own check at the end."""
    result, source, before = inner(
        "def test_writes(readonly_scorecard_db):\n"
        "    os.chmod(readonly_scorecard_db, 0o644)\n"
        "    with sqlite3.connect(readonly_scorecard_db) as conn:\n"
        "        conn.execute('DELETE FROM t')\n"
        "    os.chmod(readonly_scorecard_db, 0o444)\n"
        "def test_reads_after(readonly_scorecard_db):\n"
        "    pass\n"
    )
    assert result.ret != 0
    out = result.stdout.str()
    assert "test_inner.py::test_writes changed the shared read-only database" in out
    assert "changed during the session" in out
    assert source.stat().st_mode & 0o200, "the source itself stays untouched"
    assert shared_db.sha256(source) == before


def test_a_read_only_test_that_makes_the_share_writable_fails(inner):
    """A test that only clears the share's read-only mode writes no byte, so
    the session's hash check passes, but every later test could then write
    to it: its own teardown fails it, by name."""
    result, source, before = inner(
        "def test_unlocks(readonly_scorecard_db):\n"
        "    os.chmod(readonly_scorecard_db, 0o644)\n"
        "def test_reads_after(readonly_scorecard_db):\n"
        "    pass\n"
    )
    assert result.ret != 0
    out = result.stdout.str()
    assert "test_inner.py::test_unlocks changed the shared read-only database" in out
    assert "test_reads_after changed" not in out
    assert "changed during the session" not in out
    assert shared_db.sha256(source) == before


def test_the_inner_conftest_loads_the_real_fixture_code():
    """The inner sessions above run the conftest's own fixture functions,
    not copies of them."""
    spec = importlib.util.spec_from_file_location("probe", TESTS / "conftest.py")
    probe = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(probe)
    for name in (
        "shared_scorecard_db",
        "readonly_scorecard_db",
        "writable_scorecard_db",
    ):
        assert hasattr(probe, name), name
    assert probe._DB == BUILT
