"""Decide whether a Modal backfill run is in flight, dead, or missing — and
spawn (or re-spawn) it when needed.

The app writes ``rv_<sha8>/started`` when a run begins, and the spawner
records the Modal call id at ``rv_<sha8>/call_id``. A marker alone is not
proof of life: if the producer dies after the marker is written, every later
tick would see "in flight" and nothing would ever retry (PR #112 review). So
``check`` asks Modal for the recorded call's status first, and only falls
back to the marker's age (24h, comfortably past the 8h function timeout)
when no call id is readable. Re-spawning is always safe: the Volume-backed
workdir checkpoints batch partials, so a re-spawn resumes rather than
restarts.

Usage (from the repo root, Modal credentials in the environment):
    python3 tools/reform_validation/spawn_or_wait.py check <release_id>
        prints WAIT or SPAWN on stdout (reasons go to stderr)
    python3 tools/reform_validation/spawn_or_wait.py spawn <release_id> <producer_ref>
        spawns the backfill and records its call id on the Volume
"""

import hashlib
import re
import sys
import tempfile
import time
from pathlib import Path

import modal
import modal.exception as _mexc

from modal_backfill_app import APP_NAME, VOLUME_NAME

STALE_AFTER_SECONDS = 24 * 3600

# Modal errors that mean the recorded call is genuinely dead/finished-failed
# (as opposed to a transport blip we can't interpret). On these we re-spawn;
# on anything else unexpected we treat the status as indeterminate and lean
# on the marker-age backstop rather than respawning live work (blocker 2).
# Built defensively so a Modal client that renames/omits one of these doesn't
# break the import.
_TERMINAL_CALL_ERRORS = tuple(
    e
    for e in (
        getattr(_mexc, "RemoteError", None),
        getattr(_mexc, "ExecutionError", None),
        getattr(_mexc, "FunctionTimeoutError", None),
        getattr(_mexc, "NotFoundError", None),
        getattr(_mexc, "InvalidError", None),
    )
    if isinstance(e, type) and issubclass(e, BaseException)
)


def _sha8(release_id: str) -> str:
    return hashlib.sha256(release_id.encode()).hexdigest()[:8]


def _read(vol: modal.Volume, path: str) -> str | None:
    """Read a small marker file. Returns None ONLY when the file is genuinely
    absent (FileNotFoundError); any other error (a transport blip) propagates,
    so callers fail closed instead of mistaking an unreadable marker for a
    missing one. Collapsing every error to None was the shared root of the
    blocker-2 double-spawn and the blocker-4 pin overwrite: a live run's
    call_id/producer_ref that momentarily fails to read looked like 'no run
    recorded' and triggered a respawn / fresh-main re-pin."""
    try:
        return b"".join(vol.read_file(path)).decode()
    except FileNotFoundError:
        return None


def _artifact_present(vol: modal.Volume, release_id: str) -> bool:
    """Whether the finished ``reform_validation_<id>.json`` is on the Volume.
    Used to guard the healthy-completion TOCTOU (blocker 2): a call that
    returns just after the drain listed the Volume has published its artifact,
    so a completed call is not proof the work still needs redoing."""
    target = f"reform_validation_{release_id}.json"
    for entry in vol.listdir("/"):
        if getattr(entry, "path", str(entry)).rsplit("/", 1)[-1] == target:
            return True
    return False


def check(release_id: str) -> tuple[str, str]:
    vol = modal.Volume.from_name(VOLUME_NAME, create_if_missing=True)
    prefix = f"rv_{_sha8(release_id)}"

    # Consult the recorded call id FIRST. The spawner writes call_id right
    # after fn.spawn(), but the app only writes the `started` marker after
    # git clone + engine install (minutes later). Checking the marker first
    # (old behaviour) returned SPAWN in that window and double-spawned a live
    # run (blocker 2). An unreadable call_id marker fails closed to WAIT — it
    # is NOT proof the run is absent.
    try:
        call_id = _read(vol, f"{prefix}/call_id")
    except Exception as e:
        return (
            "WAIT",
            f"call_id marker unreadable ({type(e).__name__}) — failing closed",
        )
    indeterminate = None
    if call_id:
        call_id = call_id.strip()
        try:
            modal.FunctionCall.from_id(call_id).get(timeout=0)
        except TimeoutError:
            return "WAIT", f"call {call_id} is still running"
        except _TERMINAL_CALL_ERRORS as e:
            return (
                "SPAWN",
                f"call {call_id} terminally failed ({type(e).__name__}) — "
                "re-spawning; the workdir checkpoints make this a resume",
            )
        except Exception as e:
            # Could not determine status — a transport/transient error, NOT
            # proof of death. Don't respawn live work on a blip; fall through
            # to the marker-age backstop.
            indeterminate = f"{type(e).__name__}: {e}"
        else:
            # Completed. Guard the TOCTOU: the drain may have listed the Volume
            # just before the app published, so a completed call is not proof
            # the artifact is missing — re-check before respawning finished
            # work. An unreadable re-check fails closed to WAIT.
            try:
                published = _artifact_present(vol, release_id)
            except Exception as e:
                return (
                    "WAIT",
                    f"call {call_id} completed; artifact re-check failed "
                    f"({type(e).__name__}) — failing closed",
                )
            if published:
                return (
                    "WAIT",
                    f"call {call_id} finished and the artifact is present — "
                    "the drain will harvest it",
                )
            return (
                "SPAWN",
                f"call {call_id} finished but no artifact was published — re-spawning",
            )

    try:
        marker = _read(vol, f"{prefix}/started")
    except Exception as e:
        return (
            "WAIT",
            f"started marker unreadable ({type(e).__name__}) — failing closed",
        )
    if marker is None and call_id is None:
        return "SPAWN", "no run recorded for this release"

    started_at = None
    for line in (marker or "").splitlines():
        if line.startswith("started_at "):
            started_at = float(line.split()[1])
    age = None if started_at is None else time.time() - started_at
    if age is not None and age < STALE_AFTER_SECONDS:
        tail = f"; call status indeterminate ({indeterminate})" if indeterminate else ""
        return "WAIT", f"marker is {age / 3600:.1f}h old{tail}"
    if age is None and call_id and indeterminate:
        # A call id exists and we merely couldn't reach Modal (no timestamp
        # yet either) — presume alive rather than respawn a just-spawned run.
        return (
            "WAIT",
            f"call {call_id} recorded; status indeterminate ({indeterminate})",
        )
    return (
        "SPAWN",
        "marker stale (>24h or unstamped) — re-spawning; the workdir "
        "checkpoints make this a resume",
    )


def spawn(release_id: str, producer_ref: str, driver_ref: str = "unknown") -> None:
    vol = modal.Volume.from_name(VOLUME_NAME, create_if_missing=True)
    prefix = f"rv_{_sha8(release_id)}"
    # Pin the producer ref for the life of this release: the FIRST spawn
    # records it, every re-spawn reuses it. Otherwise a re-spawn would
    # resolve a fresh microcosm main SHA and, resuming in the same
    # release-keyed workdir, merge partials from two producer revisions
    # (blocker 4). The workflow passes the current main SHA as the candidate;
    # a recorded ref overrides it. The pin read fails CLOSED: an unreadable
    # producer_ref aborts rather than silently re-resolving fresh main and
    # overwriting the pin (the blocker-2 mechanism reappearing inside b4).
    try:
        recorded = _read(vol, f"{prefix}/producer_ref")
    except Exception as e:
        raise SystemExit(
            f"producer_ref unreadable ({type(e).__name__}) — refusing to spawn "
            "rather than risk overwriting the pin with a fresh ref"
        )
    ref = recorded.strip() if recorded else producer_ref

    fn = modal.Function.from_name(APP_NAME, "backfill")
    call = fn.spawn(release_id, ref, driver_ref)
    with tempfile.TemporaryDirectory() as tmp:
        call_p = Path(tmp, "call_id")
        call_p.write_text(call.object_id)
        # release_id in the workdir lets the schedule re-find a run that was
        # spawned, became non-latest, and died before publishing (blocker 3) —
        # sha8 is one-way, so the id has to be stored to be enumerable.
        rid_p = Path(tmp, "release_id")
        rid_p.write_text(release_id)
        with vol.batch_upload(force=True) as batch:
            batch.put_file(call_p, f"{prefix}/call_id")
            batch.put_file(rid_p, f"{prefix}/release_id")
            if recorded is None:
                ref_p = Path(tmp, "producer_ref")
                ref_p.write_text(ref)
                batch.put_file(ref_p, f"{prefix}/producer_ref")
    pinned = " (pinned from first spawn)" if recorded else ""
    print(
        f"spawned Modal backfill {call.object_id} for {release_id} "
        f"at microcosm {ref[:9]}{pinned}",
        file=sys.stderr,
    )


def _id_timestamp(release_id: str) -> str:
    # Trailing YYYYMMDD(THHMMSSZ) — enough to order releases oldest-first
    # without importing the ingest (kept dependency-free for the workflow).
    m = re.search(r"(\d{8})(T\d{6}Z)?$", release_id)
    return m.group(0) if m else release_id


def list_artifacts() -> list[str]:
    """Release ids that have a published reform_validation_<id>.json on the
    Volume, oldest-first. The workflow drains these into raw/ regardless of
    which release is currently ``latest`` — so a run that finished after
    ``latest`` advanced is never stranded (blocker 3)."""
    vol = modal.Volume.from_name(VOLUME_NAME, create_if_missing=True)
    ids = []
    for entry in vol.listdir("/"):
        name = getattr(entry, "path", str(entry)).rsplit("/", 1)[-1]
        if name.startswith("reform_validation_") and name.endswith(".json"):
            ids.append(name[len("reform_validation_") : -len(".json")])
    return sorted(ids, key=_id_timestamp)


def list_pending() -> list[str]:
    """Release ids that have a spawned workdir (``rv_<sha8>/release_id``) but
    no published artifact yet — runs in flight OR dead-before-publish. The
    schedule uses this to revisit a release that became non-latest and then
    died before publishing, which the latest-only spawn path would never
    retry (blocker 3). Oldest-first; artifacts already draining are excluded."""
    vol = modal.Volume.from_name(VOLUME_NAME, create_if_missing=True)
    published = set(list_artifacts())
    ids = []
    for entry in vol.listdir("/"):
        name = getattr(entry, "path", str(entry)).rstrip("/").rsplit("/", 1)[-1]
        if not name.startswith("rv_"):
            continue
        rid = _read(vol, f"{name}/release_id")  # None if not written yet
        if rid and rid.strip() and rid.strip() not in published:
            ids.append(rid.strip())
    return sorted(set(ids), key=_id_timestamp)


def main() -> None:
    mode = sys.argv[1]
    if mode == "check":
        decision, reason = check(sys.argv[2])
        print(reason, file=sys.stderr)
        print(decision)
    elif mode == "spawn":
        # spawn <release_id> <producer_ref> [driver_ref]
        spawn(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "unknown")
    elif mode == "artifacts":
        for rid in list_artifacts():
            print(rid)
    elif mode == "pending":
        for rid in list_pending():
            print(rid)
    else:
        raise SystemExit(
            f"unknown mode {mode!r}; use check, spawn, artifacts or pending"
        )


if __name__ == "__main__":
    main()
