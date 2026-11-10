"""clone_copy makes the copy its shutil namesake makes, without the bytes.

Differential: for any contents, mode (setuid and sticky included) and
umask, each function leaves the file shutil leaves (bytes, mode bits and
file flags, and for copy2 the timestamps) and returns the same path. Independence: a clone and its source never see each other's
later writes. Cost: on APFS a fresh clone holds no data blocks of its own,
and the clone path is the one taken (a broken binding would silently fall
back to byte copies, which no other test would notice)."""

import ast
import ctypes
import ctypes.util
import errno
import os
import shutil
import stat
import struct
import sys
import tempfile
from pathlib import Path

import clone_copy
import pytest
from hypothesis import example, given, settings
from hypothesis import strategies as st

APFS = sys.platform == "darwin"
MODES = st.sampled_from(
    [0o644, 0o600, 0o755, 0o640, 0o444, 0o400, 0o700, 0o664, 0o666, 0o777]
    # setuid, setgid (dropped by chmod where the file's group is not the
    # caller's) and sticky: clonefile(2) drops the first two.
    + [0o4755, 0o2755, 0o6755, 0o1755]
)
UMASKS = st.sampled_from([0o022, 0o077, 0o002, 0o027, 0o000])
CONTENTS = st.binary(max_size=3 * 4096 + 7)
NAMES = ("copyfile", "copy", "copy2")
TESTS = Path(__file__).resolve().parent


def _private_bytes(path) -> int:
    """APFS ATTR_CMNEXT_PRIVATESIZE: the file's blocks no clone shares."""

    class AttrList(ctypes.Structure):
        _fields_ = [
            ("bitmapcount", ctypes.c_ushort),
            ("reserved", ctypes.c_uint16),
            ("commonattr", ctypes.c_uint32),
            ("volattr", ctypes.c_uint32),
            ("dirattr", ctypes.c_uint32),
            ("fileattr", ctypes.c_uint32),
            ("forkattr", ctypes.c_uint32),
        ]

    libc = ctypes.CDLL(ctypes.util.find_library("c"), use_errno=True)
    getattrlist = libc.getattrlist
    getattrlist.argtypes = [
        ctypes.c_char_p,
        ctypes.POINTER(AttrList),
        ctypes.c_void_p,
        ctypes.c_size_t,
        ctypes.c_ulong,
    ]
    request = AttrList(5, 0, 0, 0, 0, 0, 0x00000008)  # ATTR_CMNEXT_PRIVATESIZE
    buffer = ctypes.create_string_buffer(32)
    # FSOPT_NOFOLLOW | FSOPT_ATTR_CMN_EXTENDED
    rc = getattrlist(os.fsencode(path), ctypes.byref(request), buffer, 32, 0x21)
    assert rc == 0, os.strerror(ctypes.get_errno())
    length, value = struct.unpack_from("=Iq", buffer, 0)
    assert length >= 12
    return value


def _seen(path):
    st_ = os.stat(path)
    flags = getattr(st_, "st_flags", 0)  # BSD file flags; Linux has none
    return Path(path).read_bytes(), stat.S_IMODE(st_.st_mode), flags


@pytest.fixture(scope="module")
def scratch(tmp_path_factory):
    return tmp_path_factory.mktemp("clone-copy")


@settings(max_examples=60, deadline=None)
@given(name=st.sampled_from(NAMES), contents=CONTENTS, mode=MODES, umask=UMASKS)
# The cases a clone alone gets wrong, every run: setuid, which clonefile(2)
# drops, and a umask other than the one at import time.
@example(name="copy", contents=b"setuid", mode=0o4755, umask=0o022)
@example(name="copy2", contents=b"setuid", mode=0o4755, umask=0o022)
@example(name="copyfile", contents=b"umask", mode=0o644, umask=0o077)
def test_each_function_leaves_the_file_shutil_leaves(
    scratch, name, contents, mode, umask
):
    with tempfile.TemporaryDirectory(dir=scratch) as d:
        d = Path(d)
        src = d / "src.bin"
        src.write_bytes(contents)
        os.chmod(src, mode)
        os.utime(src, ns=(1_600_000_000_123_456_789, 1_700_000_000_987_654_321))
        old = os.umask(umask)  # copyfile's new-file mode depends on it
        try:
            ours = getattr(clone_copy, name)(src, d / "ours")
            theirs = getattr(shutil, name)(src, d / "theirs")
        finally:
            os.umask(old)
        assert Path(ours).name == "ours" and Path(theirs).name == "theirs"
        assert _seen(d / "ours") == _seen(d / "theirs")
        if name == "copy2":
            assert os.stat(d / "ours").st_mtime_ns == os.stat(src).st_mtime_ns
            assert os.stat(d / "ours").st_mtime_ns == os.stat(d / "theirs").st_mtime_ns
        else:
            # copyfile and copy stamp the copy with the time of copying.
            assert os.stat(d / "ours").st_mtime_ns > os.stat(src).st_mtime_ns
        assert src.read_bytes() == contents


@settings(max_examples=25, deadline=None)
@given(name=st.sampled_from(("copy", "copy2")), contents=CONTENTS)
def test_copy_and_copy2_copy_into_a_directory_as_shutil_does(scratch, name, contents):
    with tempfile.TemporaryDirectory(dir=scratch) as d:
        d = Path(d)
        src = d / "src.bin"
        src.write_bytes(contents)
        (d / "a").mkdir()
        (d / "b").mkdir()
        ours = getattr(clone_copy, name)(src, d / "a")
        theirs = getattr(shutil, name)(src, d / "b")
        assert Path(ours) == d / "a" / "src.bin"
        assert Path(theirs) == d / "b" / "src.bin"
        assert _seen(ours) == _seen(theirs)


@settings(max_examples=40, deadline=None)
@given(
    name=st.sampled_from(NAMES),
    contents=CONTENTS.filter(len),
    edit=st.binary(min_size=1, max_size=64),
    offset=st.integers(0, 3 * 4096),
)
def test_a_copy_and_its_source_never_see_each_others_writes(
    scratch, name, contents, edit, offset
):
    with tempfile.TemporaryDirectory(dir=scratch) as d:
        d = Path(d)
        src = d / "src.bin"
        src.write_bytes(contents)
        dst = Path(getattr(clone_copy, name)(src, d / "dst.bin"))
        offset = offset % len(contents)
        with open(dst, "r+b") as fh:
            fh.seek(offset)
            fh.write(edit)
        assert src.read_bytes() == contents
        with open(src, "r+b") as fh:
            fh.seek(offset)
            fh.write(bytes(b ^ 0xFF for b in edit))
        expected = bytearray(contents)
        expected[offset : offset + len(edit)] = edit
        assert dst.read_bytes() == bytes(expected)


def test_an_existing_destination_is_overwritten_as_shutil_overwrites(tmp_path):
    src = tmp_path / "src"
    src.write_bytes(b"new bytes")
    for name in NAMES:
        for who, module in (("ours", clone_copy), ("theirs", shutil)):
            dst = tmp_path / f"{name}-{who}"
            dst.write_bytes(b"old bytes that are longer")
            os.chmod(dst, 0o600)
            getattr(module, name)(src, dst)
        assert _seen(tmp_path / f"{name}-ours") == _seen(tmp_path / f"{name}-theirs")


@pytest.mark.skipif(not hasattr(os, "chflags"), reason="file flags are BSD's")
@pytest.mark.parametrize("name", NAMES)
@pytest.mark.parametrize(
    "flags",
    [
        stat.UF_NODUMP | stat.UF_HIDDEN,
        stat.UF_IMMUTABLE,
        stat.UF_IMMUTABLE | stat.UF_NODUMP,
    ],
    ids=["nodump-hidden", "immutable", "immutable-nodump"],
)
def test_file_flags_end_as_shutil_leaves_them(tmp_path, name, flags):
    """A clone carries the source's flags; shutil's copyfile and copy leave
    none and copy2 copies them. The setuid bit makes copy2 clear an
    immutable flag to put the bit back, then set the flag again."""
    src = tmp_path / "src"
    src.write_bytes(b"flagged")
    os.chmod(src, 0o4755)
    try:
        os.chflags(src, flags)
        outcome = {}
        for who, module in (("ours", clone_copy), ("theirs", shutil)):
            dst = tmp_path / who
            try:
                getattr(module, name)(src, dst)
            except OSError as error:
                outcome[who] = type(error).__name__
            else:
                # copy2's modification time (shutil reads the source's
                # data and a clone does not, so its access time can differ).
                mtime = os.stat(dst).st_mtime_ns if name == "copy2" else None
                outcome[who] = (*_seen(dst), mtime)
        assert outcome["ours"] == outcome["theirs"]
        assert isinstance(outcome["ours"], tuple), outcome
    finally:
        for path in tmp_path.iterdir():
            os.chflags(path, 0)  # an immutable file would outlive the test


@pytest.mark.parametrize("name", NAMES)
def test_errors_are_shutils_errors(tmp_path, name):
    missing = tmp_path / "missing"
    with pytest.raises(FileNotFoundError):
        getattr(clone_copy, name)(missing, tmp_path / "x")
    src = tmp_path / "src"
    src.write_bytes(b"x")
    with pytest.raises(shutil.SameFileError):
        getattr(clone_copy, name)(src, src)
    with pytest.raises(FileNotFoundError):
        getattr(clone_copy, name)(src, tmp_path / "no-such-dir" / "x")


def test_copytree_copies_the_tree_shutil_copies(tmp_path):
    src = tmp_path / "src"
    (src / "a" / "b").mkdir(parents=True)
    (src / "top.json").write_text("{}")
    (src / "a" / "mid.py").write_text("x = 1\n")
    (src / "a" / "b" / "deep.bin").write_bytes(bytes(range(256)) * 50)
    os.chmod(src / "a" / "mid.py", 0o755)
    (src / "a" / "__pycache__").mkdir()
    (src / "a" / "__pycache__" / "mid.pyc").write_bytes(b"\0")
    (src / "link.json").symlink_to("top.json")
    ignore = shutil.ignore_patterns("__pycache__")
    for symlinks in (False, True):
        ours = tmp_path / f"ours-{symlinks}"
        theirs = tmp_path / f"theirs-{symlinks}"
        clone_copy.copytree(src, ours, ignore=ignore, symlinks=symlinks)
        shutil.copytree(src, theirs, ignore=ignore, symlinks=symlinks)

        def listing(root):
            out = {}
            for path in sorted(root.rglob("*")):
                rel = path.relative_to(root).as_posix()
                if path.is_symlink():
                    out[rel] = ("link", os.readlink(path))
                elif path.is_file():
                    out[rel] = ("file", *_seen(path))
                else:
                    out[rel] = ("dir",)
            return out

        assert listing(ours) == listing(theirs)
        assert "a/__pycache__" not in listing(ours)


def _write_synced(path, data, offset=None):
    """Write and fsync: APFS allocates blocks when data reaches the disk, so
    private bytes are only meaningful after a sync."""
    with open(path, "r+b" if offset is not None else "wb") as fh:
        if offset is not None:
            fh.seek(offset)
        fh.write(data)
        fh.flush()
        os.fsync(fh.fileno())


@pytest.mark.skipif(not APFS, reason="clonefile(2) is macOS's")
def test_on_apfs_a_copy_is_a_clone_that_holds_no_blocks_of_its_own(tmp_path):
    src = tmp_path / "big.bin"
    _write_synced(src, os.urandom(1 << 20))
    probe = tmp_path / "probe"
    code = clone_copy._clonefile(
        os.fsencode(src), os.fsencode(probe), clone_copy._CLONE_NOOWNERCOPY
    )
    if code != 0:
        reason = ctypes.get_errno()
        if reason in (errno.ENOTSUP, errno.EXDEV):
            pytest.skip(f"this temp volume cannot clone: {os.strerror(reason)}")
        pytest.fail(f"clonefile failed: {os.strerror(reason)}")
    assert _private_bytes(src) == 0  # the probe shares every block
    os.unlink(probe)
    assert _private_bytes(src) >= 1 << 20
    for name in NAMES:
        dst = Path(getattr(clone_copy, name)(src, tmp_path / name))
        assert _private_bytes(dst) == 0, name
        # One written byte copies one extent (16 KiB here), not the file.
        _write_synced(dst, b"x", offset=0)
        assert 0 < _private_bytes(dst) <= 64 * 1024, name
    for name in NAMES:
        os.unlink(tmp_path / name)
    assert _private_bytes(src) >= 1 << 20


# --- every copy in the tests goes through clone_copy -------------------------

_COPIERS = {"copy", "copy2", "copyfile", "copytree"}


def _direct_copies(source: str) -> list[tuple[int, str]]:
    """Where code (not a string) names one of shutil's file copiers: a call,
    a reference such as copy_function=shutil.copy, or an import."""
    tree = ast.parse(source)
    names = {"shutil"}  # and any `import shutil as x`
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names |= {a.asname for a in node.names if a.name == "shutil" and a.asname}
    found = []
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Attribute)
            and node.attr in _COPIERS
            and isinstance(node.value, ast.Name)
            and node.value.id in names
        ):
            found.append((node.lineno, f"shutil.{node.attr}"))
        elif isinstance(node, ast.ImportFrom) and node.module == "shutil":
            found += [
                (node.lineno, f"from shutil import {a.name}")
                for a in node.names
                if a.name in _COPIERS or a.name == "*"
            ]
    return sorted(found)


def test_no_test_copies_a_file_with_shutil_directly():
    """A byte copy of the database or of a replay tree costs its full size
    in temp disk; clone_copy's copy costs only what the test then changes.
    Scripts that a test writes out and runs in a subprocess hold their
    copies in strings, which this leaves alone: tests/ is not on their path."""
    offenders = {}
    for path in sorted(TESTS.glob("*.py")):
        if path.name in {"clone_copy.py", Path(__file__).name}:
            continue
        hits = _direct_copies(path.read_text())
        if hits:
            offenders[path.name] = hits
    assert offenders == {}, "use clone_copy's copy functions instead"


def test_the_copy_guard_sees_calls_references_and_imports_not_strings():
    source = (
        "import shutil\n"
        "import shutil as sh\n"
        "shutil.copy2(a, b)\n"
        "shutil.copytree(a, b, copy_function=shutil.copy)\n"
        "from shutil import copyfile as cf, rmtree\n"
        "sh.copyfile(a, b)\n"
        "SCRIPT = 'shutil.copytree(a, b)'\n"
        "shutil.rmtree(a)\n"
        "shutil.copyfileobj(f, g)\n"
        "clone_copy.copy2(a, b)\n"
    )
    assert _direct_copies(source) == [
        (3, "shutil.copy2"),
        (4, "shutil.copy"),
        (4, "shutil.copytree"),
        (5, "from shutil import copyfile"),
        (6, "shutil.copyfile"),
    ]
