"""One read-only copy of the built database, shared by the tests that only
read it.

The share is a snapshot of data/scorecard.db (snapshot below: a clone on
APFS, which writes no data blocks, and a byte copy elsewhere) with its
write bits cleared. SQLite opens a
file it cannot write read-only, so any write through it fails at once with
"attempt to write a readonly database", inside the test that tried. Two
checks catch a write that gets around the mode bits (a test that chmods the
file back, or a process running as root): every test that takes the share
compares its stat signature before and after, and the session compares the
file's SHA-256 at the end with the one taken when the share was made.

Before it seals the share, the session lets a ``prepare`` step write to it.
conftest.py's step opens it with ScorecardDB, whose open brings a file with
an older schema up to the code's (scorecard_db/db.py: _migrate and
_ensure_view) and writes nothing to a file this code built. So no reader
ever needs to write, and an older data/scorecard.db is migrated in the
share, never in place.
"""

from __future__ import annotations

import contextlib
import hashlib
import os
import sqlite3
import stat
from pathlib import Path

import clone_copy


class SharedDatabaseWritten(AssertionError):
    """A test changed the database that read-only tests share."""


class StaleDatabaseWarning(UserWarning):
    """The built database predates the code's schema."""


def sha256(path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def signature(path) -> tuple:
    """What any write to the file changes: inode, size, mtime and mode."""
    st = os.stat(path)
    return (st.st_ino, st.st_size, st.st_mtime_ns, stat.S_IMODE(st.st_mode))


def siblings(path) -> list[str]:
    """Files beside the share: SQLite's -journal, -wal or -shm would mean a
    connection opened it for writing."""
    path = Path(path)
    return sorted(p.name for p in path.parent.iterdir() if p.name != path.name)


def snapshot(source, dest, copy=clone_copy.copy2):
    """Copy the SQLite database at ``source`` to the new path ``dest`` as
    its readers see it, and return ``dest``.

    A file copy alone can catch the database mid-write. A writer that died
    inside a transaction (an interrupted build or ingest, which write
    data/scorecard.db in place) leaves its uncommitted pages in the file and
    the originals in a hot journal beside it, and a live writer can change
    the file while the copy runs. So the copy runs inside a read
    transaction on ``source``, as a reader's query would: SQLite first rolls
    back a hot journal (in place, as every reader of the file would), and a
    writer cannot change the file until the copy ends; one that holds it
    makes this wait, for up to a minute. A database in WAL mode keeps
    committed pages in its -wal file, which a file copy misses, so it goes
    through SQLite's backup API instead, into a copy in rollback mode.
    """
    uri = Path(source).resolve().as_uri() + "?mode=rw"  # never create it
    conn = sqlite3.connect(uri, uri=True, timeout=60, isolation_level=None)
    try:
        conn.execute("BEGIN")
        conn.execute("SELECT COUNT(*) FROM sqlite_master").fetchone()
        if conn.execute("PRAGMA journal_mode").fetchone()[0] == "wal":
            target = sqlite3.connect(dest)
            try:
                conn.backup(target)
                target.execute("PRAGMA journal_mode=DELETE")
            finally:
                target.close()
        else:
            copy(source, dest)
    finally:
        conn.close()  # ends the read transaction
    return Path(dest)


def bring_up_to_date(path) -> bool:
    """Open ``path`` with ScorecardDB, as a test would, and close it; return
    whether that wrote to the file (it does only when the file's schema
    predates the code's)."""
    from scorecard_db import ScorecardDB

    before = signature(path)
    ScorecardDB(path).close()
    return signature(path) != before


@contextlib.contextmanager
def read_only_share(source, directory, prepare=None):
    """Yield a read-only snapshot of ``source`` in ``directory``, once
    ``prepare(path)``, if given, has run on it while it is still writable.
    On exit, raise SharedDatabaseWritten if its bytes changed or a sidecar
    file appeared, after making it writable again so pytest can delete it."""
    path = Path(directory) / Path(source).name
    snapshot(source, path)
    if prepare is not None:
        prepare(path)
    os.chmod(path, 0o444)
    expected = sha256(path)
    try:
        yield path
    finally:
        found = sha256(path) if path.exists() else None
        extra = siblings(path)
        if path.exists():
            os.chmod(path, 0o644)
        if found != expected or extra:
            raise SharedDatabaseWritten(
                f"the shared read-only database {path} changed during the "
                f"session: sha256 {expected} -> {found}, files beside it {extra}"
            )


@contextlib.contextmanager
def unchanged_by(path, who: str):
    """Raise SharedDatabaseWritten if ``path`` changes inside the block."""
    before = signature(path)
    yield path
    after = signature(path)
    if after != before or siblings(path):
        raise SharedDatabaseWritten(
            f"{who} wrote to the shared read-only database {path}: "
            f"signature {before} -> {after}, files beside it {siblings(path)}"
        )
