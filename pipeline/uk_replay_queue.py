"""The persistent qualification queue on the ``replay-state`` branch.

GitHub keeps at most one pending run per concurrency group and cancels older
pending runs, so a request must be written down before anything else can
lose it. Each request lives at ``requests/<request_id>/`` in a checkout of
the state branch: ``REQUEST.json`` (the request as received), ``STATUS.json``
(schema policyengine.uk-replay-status/v1) and, once terminal,
``REPLAY_RECEIPT.json`` and ``results/``. Enqueueing is idempotent: a
request already present keeps its status. The workflow commits and pushes
after each call; this module only edits files.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline import uk_replay_interface as interface  # noqa: E402

TERMINAL = ("complete", "rejected", "failed")
STATUSES = ("queued", "running", *TERMINAL)
# A running request whose last update is older than this has lost its run
# (a cancelled or crashed job never writes a terminal status).
STALE_RUNNING = timedelta(hours=7)


def canonical_bytes(value) -> bytes:
    return (
        json.dumps(value, indent=1, sort_keys=True, ensure_ascii=False) + "\n"
    ).encode()


def request_dir(state: Path, request_id: str) -> Path:
    if len(request_id) != 64 or any(c not in "0123456789abcdef" for c in request_id):
        raise ValueError("request_id must be 64 lowercase hex characters")
    return state / "requests" / request_id


def read_status(state: Path, request_id: str) -> dict | None:
    path = request_dir(state, request_id) / "STATUS.json"
    return json.loads(path.read_bytes()) if path.exists() else None


def write_status(state: Path, status: dict) -> None:
    interface.validate(status, interface.STATUS_SCHEMA_ID)
    path = request_dir(state, status["request_id"]) / "STATUS.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(status))


def enqueue(state: Path, request: dict, *, run_url: str, now: str) -> tuple[str, str]:
    """Record a request; returns (request_id, its status). Idempotent.

    A request that fails the schema is still recorded, by the digest of its
    canonical bytes, so the receipt that rejects it has an address."""
    try:
        request_id = interface.validate_request(request)
    except Exception:  # noqa: BLE001 - recorded, rejected by the drain step
        request_id = interface.jcs_sha256(request)
    existing = read_status(state, request_id)
    if existing is not None:
        return request_id, existing["status"]
    directory = request_dir(state, request_id)
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "REQUEST.json").write_bytes(canonical_bytes(request))
    write_status(
        state,
        {
            "schema": interface.STATUS_SCHEMA_ID,
            "request_id": request_id,
            "status": "queued",
            "history": [{"status": "queued", "at": now, "run_url": run_url}],
        },
    )
    return request_id, "queued"


def set_status(
    state: Path,
    request_id: str,
    status: str,
    *,
    run_url: str,
    now: str,
    receipt_sha256: str | None = None,
    receipt_commit: str | None = None,
) -> dict:
    current = read_status(state, request_id)
    if current is None:
        raise ValueError(f"{request_id} is not queued")
    if current["status"] in TERMINAL:
        raise ValueError(
            f"{request_id} is already {current['status']}; terminal states are final"
        )
    if status not in STATUSES:
        raise ValueError(f"unknown status {status}")
    updated = {
        **current,
        "status": status,
        "history": [
            *current["history"],
            {"status": status, "at": now, "run_url": run_url},
        ],
    }
    if status in TERMINAL:
        if not (receipt_sha256 and receipt_commit):
            raise ValueError("a terminal status names its receipt digest and commit")
        updated.update(receipt_sha256=receipt_sha256, receipt_commit=receipt_commit)
    write_status(state, updated)
    return updated


def _at(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def pending(state: Path, *, now: str) -> list[str]:
    """Requests to run, oldest first: queued, or running past the stale bound."""
    out = []
    for path in sorted((state / "requests").glob("*/STATUS.json")):
        status = json.loads(path.read_bytes())
        last = status["history"][-1]["at"]
        if status["status"] == "queued" or (
            status["status"] == "running" and _at(now) - _at(last) > STALE_RUNNING
        ):
            out.append((status["history"][0]["at"], status["request_id"]))
    return [request_id for _, request_id in sorted(out)]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    add = commands.add_parser("enqueue")
    add.add_argument("--state", type=Path, required=True)
    add.add_argument("--request", type=Path, required=True)
    add.add_argument("--run-url", required=True)
    add.add_argument("--now", required=True)
    nxt = commands.add_parser("pending")
    nxt.add_argument("--state", type=Path, required=True)
    nxt.add_argument("--now", required=True)
    mark = commands.add_parser("set-status")
    mark.add_argument("--state", type=Path, required=True)
    mark.add_argument("--request-id", required=True)
    mark.add_argument("--status", choices=STATUSES, required=True)
    mark.add_argument("--run-url", required=True)
    mark.add_argument("--now", required=True)
    mark.add_argument("--receipt-sha256")
    mark.add_argument("--receipt-commit")
    args = parser.parse_args(argv)
    if args.command == "enqueue":
        request = json.loads(args.request.read_text(encoding="utf-8"))
        request_id, status = enqueue(
            args.state, request, run_url=args.run_url, now=args.now
        )
        print(f"{request_id} {status}")
    elif args.command == "pending":
        print("\n".join(pending(args.state, now=args.now)))
    else:
        set_status(
            args.state,
            args.request_id,
            args.status,
            run_url=args.run_url,
            now=args.now,
            receipt_sha256=args.receipt_sha256,
            receipt_commit=args.receipt_commit,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
