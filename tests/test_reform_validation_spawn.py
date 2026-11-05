"""Spawn/liveness decision table for tools/reform_validation/spawn_or_wait.py
(re-gate blocker 2/3). Modal isn't a CI dependency and the module imports it at
top level, so we stub `modal`, `modal.exception`, and `modal_backfill_app` in
sys.modules before importing spawn_or_wait, then drive check() through the
decision table — especially the fail-closed paths that a transport blip must
never turn into a respawn."""

import sys
import time
import types
from pathlib import Path

import pytest

# --------------------------------------------------------------------------- #
# Stubs, installed before importing spawn_or_wait
# --------------------------------------------------------------------------- #
_STATE = {
    "files": {},  # path -> str contents
    "errors": {},  # path -> Exception to raise on read
    "listing": [],  # entries returned by listdir("/")
    "call_get": "timeout",  # "timeout" | None (completed) | Exception
    "listdir_error": None,
}

_mexc = types.ModuleType("modal.exception")
for _name in (
    "RemoteError",
    "ExecutionError",
    "FunctionTimeoutError",
    "NotFoundError",
    "InvalidError",
):
    setattr(_mexc, _name, type(_name, (Exception,), {}))


class _Entry:
    def __init__(self, path):
        self.path = path


class _FakeVolume:
    @staticmethod
    def from_name(name, create_if_missing=False):
        return _FakeVolume()

    def read_file(self, path):
        err = _STATE["errors"].get(path)
        if err is not None:
            raise err
        if path in _STATE["files"]:
            return [_STATE["files"][path].encode()]
        raise FileNotFoundError(path)

    def listdir(self, path):
        if _STATE["listdir_error"] is not None:
            raise _STATE["listdir_error"]
        return _STATE["listing"]


class _FakeFunctionCall:
    @staticmethod
    def from_id(call_id):
        return _FakeFunctionCall()

    def get(self, timeout=0):
        beh = _STATE["call_get"]
        if beh == "timeout":
            raise TimeoutError()
        if isinstance(beh, Exception):
            raise beh
        return None  # completed successfully


_modal = types.ModuleType("modal")
_modal.Volume = _FakeVolume
_modal.FunctionCall = _FakeFunctionCall
_modal.Function = object
_modal.exception = _mexc
sys.modules["modal"] = _modal
sys.modules["modal.exception"] = _mexc

_app = types.ModuleType("modal_backfill_app")
_app.APP_NAME = "app"
_app.VOLUME_NAME = "vol"
sys.modules["modal_backfill_app"] = _app

TOOLS = Path(__file__).resolve().parent.parent / "tools" / "reform_validation"
sys.path.insert(0, str(TOOLS))
import spawn_or_wait  # noqa: E402

REL = "populace-us-2024-buildp-sparse-rmloss100-deadbeef-20260801T000000Z"
PREFIX = f"rv_{spawn_or_wait._sha8(REL)}"


def _reset(**over):
    _STATE.update(
        files={}, errors={}, listing=[], call_get="timeout", listdir_error=None
    )
    _STATE.update(over)


def _started(age_hours):
    return f"{REL}\nproducer abc\nstarted_at {int(time.time() - age_hours * 3600)}\n"


# --------------------------------------------------------------------------- #
# Decision table
# --------------------------------------------------------------------------- #
def test_call_running_waits():
    _reset(files={f"{PREFIX}/call_id": "call-1"}, call_get="timeout")
    assert spawn_or_wait.check(REL)[0] == "WAIT"


def test_call_terminally_failed_spawns():
    _reset(files={f"{PREFIX}/call_id": "call-1"}, call_get=_mexc.RemoteError("boom"))
    assert spawn_or_wait.check(REL)[0] == "SPAWN"


def test_completed_with_artifact_waits_not_respawn():
    # Healthy-completion TOCTOU: the call returned and the artifact IS on the
    # Volume — the drain will harvest it; respawning would redo finished work.
    _reset(
        files={f"{PREFIX}/call_id": "call-1"},
        call_get=None,
        listing=[_Entry(f"reform_validation_{REL}.json")],
    )
    assert spawn_or_wait.check(REL)[0] == "WAIT"


def test_completed_without_artifact_spawns():
    _reset(files={f"{PREFIX}/call_id": "call-1"}, call_get=None, listing=[])
    assert spawn_or_wait.check(REL)[0] == "SPAWN"


def test_call_id_unreadable_fails_closed_to_wait():
    # THE blocker-2 fix: a transport blip reading the call_id marker must not
    # look like "no run recorded" and double-spawn a live 64GB container.
    _reset(errors={f"{PREFIX}/call_id": ConnectionError("blip")})
    assert spawn_or_wait.check(REL)[0] == "WAIT"


def test_indeterminate_with_recent_marker_waits():
    _reset(
        files={f"{PREFIX}/call_id": "call-1", f"{PREFIX}/started": _started(1)},
        call_get=ConnectionError("blip"),  # not a terminal Modal error
    )
    assert spawn_or_wait.check(REL)[0] == "WAIT"


def test_no_run_recorded_spawns():
    _reset()
    assert spawn_or_wait.check(REL)[0] == "SPAWN"


def test_no_call_id_stale_marker_spawns():
    _reset(files={f"{PREFIX}/started": _started(30)})  # >24h
    assert spawn_or_wait.check(REL)[0] == "SPAWN"


def test_no_call_id_recent_marker_waits():
    _reset(files={f"{PREFIX}/started": _started(1)})
    assert spawn_or_wait.check(REL)[0] == "WAIT"


def test_read_fails_closed_only_on_missing_file():
    # _read returns None only for a genuinely absent file; any other error
    # propagates (so callers can fail closed).
    _reset(errors={"x": ConnectionError("blip")})
    vol = spawn_or_wait.modal.Volume.from_name("vol")
    assert spawn_or_wait._read(vol, "absent") is None
    with pytest.raises(ConnectionError):
        spawn_or_wait._read(vol, "x")
