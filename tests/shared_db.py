"""One read-only copy of the built database, shared by the tests that only
read it.

The share is a clone of data/scorecard.db (clone_copy: no data blocks on
APFS, a byte copy elsewhere) with its write bits cleared. SQLite opens a
file it cannot write read-only, so any write through it fails at once with
"attempt to write a readonly database", inside the test that tried. Two
checks catch a write that gets around the mode bits (a test that chmods the
file back, or a process running as root): every test that takes the share
compares its stat signature before and after, and the session compares the
file's SHA-256 at the end with the one taken when the share was made.
"""

from __future__ import annotations

import contextlib
import hashlib
import os
import stat
from pathlib import Path

import clone_copy


class SharedDatabaseWritten(AssertionError):
    """A test changed the database that read-only tests share."""


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


@contextlib.contextmanager
def read_only_share(source, directory):
    """Yield a read-only clone of ``source`` in ``directory``; on exit, raise
    SharedDatabaseWritten if its bytes changed or a sidecar file appeared,
    after making it writable again so pytest can delete it."""
    path = Path(directory) / Path(source).name
    clone_copy.copy2(source, path)
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
