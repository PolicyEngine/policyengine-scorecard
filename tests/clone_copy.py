"""shutil's copy functions, made as APFS clones where the filesystem allows.

A test that needs its own writable copy of a large committed artifact (the
built database, a sealed replay namespace, the pipeline tree) used to get a
byte-for-byte copy in tmp_path. On APFS, clonefile(2) makes the same copy
by writing metadata only: the clone shares the source's blocks until either
file is written, and then only the written blocks are copied. A test that
changes a few pages of a 200 MB database pays for those pages, not for
200 MB.

Each function here takes the arguments of its shutil namesake, returns what
it returns, and leaves a file with the same bytes, the same mode bits
(setuid and sticky included), the same file flags and, for copy2, the same
access and modification times. Where a clone is not possible (another
platform, such as CI's Linux runners; another volume; an existing
destination), it calls the shutil function itself.

Two differences remain, and no test here reads either: a clone keeps the
source's extended attributes and its creation time, where shutil's copies
on macOS get none of the first and the current time for the second.
"""

from __future__ import annotations

import ctypes
import os
import shutil
import stat
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


def _umask() -> int:
    """The process umask now. Only setting it reads it, so set it straight
    back (the tests that use this module run one thread each)."""
    mask = os.umask(0o022)
    os.umask(mask)
    return mask


def _clear_flags(path) -> int:
    """Clear a clone's file flags and return them. A file that shutil
    creates starts with none, and an immutable flag carried over from the
    source would refuse the chmod and utime that follow."""
    flags = os.stat(path).st_flags
    if flags:
        os.chflags(path, 0)
    return flags


def _into(src, dst):
    """shutil.copy and copy2 copy *into* a destination directory."""
    if os.path.isdir(dst):
        return os.path.join(dst, os.path.basename(src))
    return dst


def copyfile(src, dst, *, follow_symlinks=True):
    """shutil.copyfile: the bytes, a new file's mode and the current time."""
    if follow_symlinks and clone(src, dst):
        _clear_flags(dst)
        os.chmod(dst, 0o666 & ~_umask())
        os.utime(dst)
        return dst
    return shutil.copyfile(src, dst, follow_symlinks=follow_symlinks)


def copy(src, dst, *, follow_symlinks=True):
    """shutil.copy: the bytes and the mode bits, with the current time."""
    target = _into(src, dst)
    if follow_symlinks and clone(src, target):
        _clear_flags(target)
        # clonefile(2) drops setuid and setgid; shutil.copymode keeps them.
        os.chmod(target, stat.S_IMODE(os.stat(src).st_mode))
        os.utime(target)
        return target
    return shutil.copy(src, dst, follow_symlinks=follow_symlinks)


def copy2(src, dst, *, follow_symlinks=True):
    """shutil.copy2: the bytes, the mode bits, the file flags and the access
    and modification times. A clone carries the source's flags and times as
    they were at the moment of the clone."""
    target = _into(src, dst)
    if follow_symlinks and clone(src, target):
        mode = stat.S_IMODE(os.stat(src).st_mode)
        if stat.S_IMODE(os.stat(target).st_mode) != mode:
            # Put back the setuid or setgid bit clonefile(2) dropped. chmod
            # and chflags change no access or modification time.
            flags = _clear_flags(target)
            os.chmod(target, mode)
            if flags:
                os.chflags(target, flags)
        return target
    return shutil.copy2(src, dst, follow_symlinks=follow_symlinks)


def copytree(src, dst, **kwargs):
    """shutil.copytree with every file made by copy2 above."""
    kwargs.setdefault("copy_function", copy2)
    return shutil.copytree(src, dst, **kwargs)
