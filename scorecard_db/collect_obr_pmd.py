"""Lock the March 2026 policy measures database through exact Wayback replays.

Only receipts are written to the repository. Workbook bytes and collection
attempt logs stay in an explicitly supplied scratch directory outside it.
"""

from __future__ import annotations

import argparse
import copy
import json
import re
from datetime import date, datetime, timezone
from pathlib import Path

from data.uk.events.collect_vintage_locks import (
    ARCHIVE_PATTERN,
    USER_AGENT,
    ArchiveClient,
    canonical_receipt_digest,
    collect_source,
)

ROOT = Path(__file__).resolve().parents[1]
HARVEST_DIR = ROOT / "sources/obr-pmd-march-2026"
RECEIPT_PATH = HARVEST_DIR / "receipt.json"
ORIGINAL_URL = (
    "https://obr.uk/docs/dlm_uploads/Policy_measures_database_March_2026.xlsx"
)
CAPTURES = ("20260410184123", "20260423164140")
EDITION = "march_2026"
PUBLISHED_AT = "2026-03-26"
SOURCE_FIELDS = (
    "role",
    "original_url",
    "archive_capture_url",
    "archive_timestamp",
    "edition",
    "capture_status",
    "capture_status_evidence",
    "status",
    "retrieved_at",
    "byte_size",
    "sha256",
    "media_type",
    "sheet_names",
    "workbook_properties",
    "original_last_modified",
    "failure_reason",
    "attempts",
)
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")


def _datetime(value: str, field: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError(f"Invalid {field}: expected a timestamp")
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError(f"Invalid {field}: {value}") from error
    if result.tzinfo is None:
        raise ValueError(f"Invalid {field}: timezone required")
    return result


def _capture_status(properties: dict) -> str:
    modified = properties.get("modified")
    if modified and _datetime(
        modified, "workbook modified"
    ).date() > date.fromisoformat(PUBLISHED_AT):
        return "later_revision"
    return "unknown"


def _capture_evidence(properties: dict) -> str:
    evidence = (
        f"Workbook created={properties.get('created')!r}, "
        f"modified={properties.get('modified')!r}; edition published {PUBLISHED_AT}. "
    )
    if _capture_status(properties) == "later_revision":
        evidence += "Workbook modification postdates publication: later edited bytes. "
    return evidence + (
        "An archive capture after publication does not establish first-release "
        "byte equivalence or exclude an earlier correction."
    )


def build_receipt(captures: list[dict]) -> dict:
    """Bind both capture receipts and select the earliest available candidate."""
    if len(captures) != len(CAPTURES):
        raise ValueError("Both pinned captures are required")
    sources = copy.deepcopy(captures)
    for source in sources:
        source["capture_status"] = _capture_status(source["workbook_properties"])
        source["capture_status_evidence"] = _capture_evidence(
            source["workbook_properties"]
        )
        source["receipt_sha256"] = canonical_receipt_digest(source)
    selected = sources[0]
    identical = selected["sha256"] == sources[1]["sha256"]
    comparison_evidence = (
        "Both exact id_ replay captures have identical SHA-256 and byte size. "
        if identical
        else "The exact id_ replay captures have different SHA-256 digests. "
    ) + (
        f"The earlier capture, {CAPTURES[0]}, is locked as the launch candidate; "
        "this selection does not assert verified launch bytes. "
        + _capture_evidence(selected["workbook_properties"])
    )
    receipt = {
        "schema_version": "obr_pmd_receipt.v1",
        "edition_label": "March 2026",
        "published_at": PUBLISHED_AT,
        "collector": {
            "user_agent": USER_AGENT,
            "archive_replay_mode": "id_",
            "pause_seconds": 4.0,
            "max_attempts": 3,
        },
        **{key: selected[key] for key in SOURCE_FIELDS},
        "launch_candidate": True,
        "captures": sources,
        "comparison": {
            "bytes_identical": identical,
            "classification_evidence": comparison_evidence,
        },
    }
    receipt["receipt_sha256"] = canonical_receipt_digest(receipt)
    check_receipt(receipt)
    return receipt


def _check_source(source: dict, timestamp: str) -> None:
    if set(SOURCE_FIELDS) - source.keys():
        raise ValueError("Missing source receipt fields")
    if source.get("receipt_sha256") != canonical_receipt_digest(source):
        raise ValueError("Capture receipt digest mismatch")
    match = ARCHIVE_PATTERN.fullmatch(source["archive_capture_url"])
    if (
        match is None
        or match[1] != timestamp
        or match[2] != ORIGINAL_URL
        or source["original_url"] != ORIGINAL_URL
        or source["archive_timestamp"] != timestamp
    ):
        raise ValueError("Source must name the exact pinned id_ capture")
    datetime.strptime(timestamp, "%Y%m%d%H%M%S")
    retrieved = _datetime(source["retrieved_at"], "retrieved_at")
    capture_time = datetime.strptime(timestamp, "%Y%m%d%H%M%S").replace(
        tzinfo=timezone.utc
    )
    if retrieved < capture_time:
        raise ValueError("Retrieval predates archive capture")
    if source["status"] != "obtained" or source["failure_reason"] is not None:
        raise ValueError("A completed HTTP 200 workbook is required")
    if source["edition"] != EDITION or source["role"] != "policy_measures":
        raise ValueError("Wrong policy measures database edition")
    if (
        type(source["byte_size"]) is not int
        or source["byte_size"] <= 0
        or not isinstance(source["sha256"], str)
        or SHA256_PATTERN.fullmatch(source["sha256"]) is None
    ):
        raise ValueError("Invalid workbook byte metadata")
    if source["media_type"] not in {
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/octet-stream",
        "application/zip",
        "application/vnd.ms-excel",
    }:
        raise ValueError("Unexpected workbook media type")
    sheets = source["sheet_names"]
    if (
        not isinstance(sheets, list)
        or not sheets
        or any(not isinstance(name, str) or not name for name in sheets)
        or len(sheets) != len(set(sheets))
    ):
        raise ValueError("Invalid workbook sheets")
    properties = source["workbook_properties"]
    if not isinstance(properties, dict):
        raise ValueError("Invalid workbook properties")
    for field in ("created", "modified"):
        if properties.get(field) is not None:
            _datetime(properties[field], f"workbook {field}")
    if source["capture_status"] != _capture_status(properties):
        raise ValueError("Capture classification disagrees with workbook properties")
    if source["capture_status_evidence"] != _capture_evidence(properties):
        raise ValueError("Missing capture classification evidence")
    attempts = source["attempts"]
    if not isinstance(attempts, list) or not attempts:
        raise ValueError("Missing fetch attempt log")
    for attempt in attempts:
        if not ARCHIVE_PATTERN.fullmatch(attempt["url"]):
            raise ValueError("Fetch attempt must use id_ replay")
        _datetime(attempt["retrieved_at"], "attempt retrieval")
    if attempts[-1]["http_status"] != 200 or attempts[-1]["error"] is not None:
        raise ValueError("Missing successful HTTP 200 attempt")


def check_receipt(receipt: dict) -> dict:
    """Validate a receipt offline; no scratch bytes or network are needed."""
    if receipt.get("receipt_sha256") != canonical_receipt_digest(receipt):
        raise ValueError("Receipt digest mismatch")
    if (
        receipt.get("schema_version") != "obr_pmd_receipt.v1"
        or receipt.get("edition_label") != "March 2026"
        or receipt.get("published_at") != PUBLISHED_AT
        or receipt.get("launch_candidate") is not True
    ):
        raise ValueError("Invalid March 2026 edition receipt")
    collector = receipt.get("collector", {})
    if (
        collector.get("user_agent") != USER_AGENT
        or collector.get("archive_replay_mode") != "id_"
        or collector.get("pause_seconds", 0) < 4
        or collector.get("max_attempts") not in range(1, 6)
    ):
        raise ValueError("Invalid archive collection etiquette")
    sources = receipt.get("captures", [])
    if len(sources) != len(CAPTURES):
        raise ValueError("Both pinned captures must be recorded")
    for source, stamp in zip(sources, CAPTURES, strict=True):
        _check_source(source, stamp)
    if any(receipt.get(key) != sources[0][key] for key in SOURCE_FIELDS):
        raise ValueError("Locked source must be the earlier capture")
    comparison = receipt.get("comparison", {})
    identical = sources[0]["sha256"] == sources[1]["sha256"]
    if comparison.get("bytes_identical") is not identical:
        raise ValueError("Capture byte comparison disagrees with digests")
    if identical and sources[0]["byte_size"] != sources[1]["byte_size"]:
        raise ValueError("Identical digest has inconsistent byte sizes")
    if not comparison.get("classification_evidence"):
        raise ValueError("Missing comparison classification evidence")
    return receipt


def locked_source(receipt: dict) -> dict:
    """Return the validated earlier capture, including its own receipt digest."""
    check_receipt(receipt)
    return copy.deepcopy(receipt["captures"][0])


def _write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def collect(scratch: Path, receipt_path: Path = RECEIPT_PATH) -> dict:
    """Fetch only the two pinned original-byte replays, sequentially."""
    scratch = scratch.resolve()
    if scratch == ROOT or ROOT in scratch.parents:
        raise ValueError("Downloaded workbooks must remain outside the repository")
    scratch.mkdir(parents=True, exist_ok=True)
    client = ArchiveClient(pause_seconds=4.0, max_attempts=3)
    captures = []
    for stamp in CAPTURES:
        source = {
            "role": "policy_measures",
            "original_url": ORIGINAL_URL,
            "archive_capture_url": f"https://web.archive.org/web/{stamp}id_/{ORIGINAL_URL}",
            "archive_timestamp": stamp,
            "edition": EDITION,
            "capture_status": "unknown",
            "capture_status_evidence": "Pending workbook metadata inspection.",
        }
        result = collect_source(client, source, scratch)
        captures.append(result)
        _write_json(scratch / "collection_attempts.json", {"captures": captures})
        print(f"{stamp}: {result['status']}", flush=True)
    if any(source["status"] != "obtained" for source in captures):
        raise ValueError(
            f"Both captures must be obtained; attempts retained in {scratch}"
        )
    receipt = build_receipt(captures)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    _write_json(receipt_path, receipt)
    source = locked_source(receipt)
    manifest = {
        "url": ORIGINAL_URL,
        "title": "Policy measures database (March 2026 vintage)",
        "date": "2026-03",
        "sha256": source["sha256"],
        "local_path": "downloads/Policy_measures_database_March_2026.xlsx",
        "doc_type": "costings_database",
        "access": "wayback_machine_original_bytes",
        "wayback_snapshot": source["archive_capture_url"],
        "bytes": source["byte_size"],
    }
    (receipt_path.parent / "manifest.jsonl").write_text(
        json.dumps(manifest, ensure_ascii=False) + "\n"
    )
    return receipt


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Validate offline")
    parser.add_argument("--receipt", type=Path, default=RECEIPT_PATH)
    parser.add_argument("--scratch-dir", type=Path)
    args = parser.parse_args(argv)
    if args.check:
        receipt = check_receipt(json.loads(args.receipt.read_text()))
        print(f"Validated March 2026 PMD receipt: {receipt['receipt_sha256']}")
        return 0
    if args.scratch_dir is None:
        parser.error("--scratch-dir is required for collection")
    receipt = collect(args.scratch_dir, args.receipt)
    print(f"Locked March 2026 PMD receipt: {receipt['receipt_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
