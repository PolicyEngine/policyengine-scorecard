"""shutil's copy functions, made as APFS clones where the filesystem allows.

A test that needs its own writable copy of a large committed artifact (the
built database, a sealed replay namespace, the pipeline tree) used to get a
byte-for-byte copy in tmp_path. On APFS, clonefile(2) makes the same copy
by writing metadata only: the clone shares the source's blocks until either
file is written, and then only the written blocks are copied. A test that
changes a few pages of a 200 MB database pays for those pages, not for
200 MB.

Each function here takes the arguments of its shutil namesake, returns what
it returns, and leaves a file with the same bytes and the same mode (and,
for copy2, the same timestamps). Where a clone is not possible (another
platform, such as CI's Linux runners; another volume; an existing
destination), it calls the shutil function itself.
"""

from __future__ import annotations

import ctypes
import os
import shutil
import sys

__all__ = ["clone", "copy", "copy2", "copyfile", "copytree"]

_clonefile = None
if sys.platform == "darwin":
    try:
        _clonefile = ctypes.CDLL(None, use_errno=True).clonefile
    except (OSError, AttributeError):  # pragma: no cover - macOS before 10.12
        _clonefile = None
    else:
        _clonefile.argtypes = (ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint32)
        _clonefile.restype = ctypes.c_int

# clonefile(2) flag: give the clone the caller's ownership, as a copy has.
_CLONE_NOOWNERCOPY = 0x0002

# shutil.copyfile creates a new file with open(dst, "wb"): mode 0o666 less
# the process umask. Read the umask once; reading it means setting it.
_UMASK = os.umask(0o022)
os.umask(_UMASK)


def clone(src, dst) -> bool:
    """Clone the regular file at ``src`` (symlinks followed) to the new path
    ``dst``. Return False, having written nothing, when it cannot: then the
    caller copies the bytes instead."""
    if _clonefile is None:
        return False
    if not os.path.isfile(src) or os.path.lexists(dst):
        # A directory, a missing file or a special file is shutil's to
        # refuse; clonefile(2) never replaces an existing path, shutil does.
        return False
    return _clonefile(os.fsencode(src), os.fsencode(dst), _CLONE_NOOWNERCOPY) == 0


def _into(src, dst):
    """shutil.copy and copy2 copy *into* a destination directory."""
    if os.path.isdir(dst):
        return os.path.join(dst, os.path.basename(src))
    return dst


def copyfile(src, dst, *, follow_symlinks=True):
    """shutil.copyfile: the bytes, a default mode and the current time."""
    if follow_symlinks and clone(src, dst):
        os.chmod(dst, 0o666 & ~_UMASK)
        os.utime(dst)
        return dst
    return shutil.copyfile(src, dst, follow_symlinks=follow_symlinks)


def copy(src, dst, *, follow_symlinks=True):
    """shutil.copy: the bytes and the mode bits, with the current time."""
    target = _into(src, dst)
    if follow_symlinks and clone(src, target):
        os.utime(target)
        return target
    return shutil.copy(src, dst, follow_symlinks=follow_symlinks)


def copy2(src, dst, *, follow_symlinks=True):
    """shutil.copy2: the bytes, the mode and the timestamps. A clone carries
    the source's attributes as they were at the moment of the clone."""
    target = _into(src, dst)
    if follow_symlinks and clone(src, target):
        return target
    return shutil.copy2(src, dst, follow_symlinks=follow_symlinks)


def copytree(src, dst, **kwargs):
    """shutil.copytree with every file made by copy2 above."""
    kwargs.setdefault("copy_function", copy2)
    return shutil.copytree(src, dst, **kwargs)
