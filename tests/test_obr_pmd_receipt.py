"""March 2026 PMD receipt checks never require network or retained workbooks."""

from __future__ import annotations

import copy
import hashlib
import io
import json
import zipfile

import pytest

from data.uk.events.collect_vintage_locks import canonical_receipt_digest
from scorecard_db import collect_obr_pmd as collector


def workbook_bytes() -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr(
            "xl/workbook.xml",
            '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            '<sheets><sheet name="Tax Measures"/></sheets></workbook>',
        )
        archive.writestr(
            "docProps/core.xml",
            '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
            'xmlns:dcterms="http://purl.org/dc/terms/">'
            "<dcterms:created>2021-03-26T18:16:26Z</dcterms:created>"
            "<dcterms:modified>2026-03-25T11:22:45Z</dcterms:modified>"
            "</cp:coreProperties>",
        )
    return buffer.getvalue()


def source(timestamp: str, digest: str = "a" * 64) -> dict:
    replay = f"https://web.archive.org/web/{timestamp}id_/{collector.ORIGINAL_URL}"
    return {
        "role": "policy_measures",
        "original_url": collector.ORIGINAL_URL,
        "archive_capture_url": replay,
        "archive_timestamp": timestamp,
        "edition": collector.EDITION,
        "status": "obtained",
        "retrieved_at": "2026-10-15T19:58:13+00:00",
        "byte_size": 1234,
        "sha256": digest,
        "media_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "sheet_names": ["Notes", "Tax Measures", "Spending Measures"],
        "workbook_properties": {
            "created": "2021-03-26T18:16:26Z",
            "modified": "2026-03-25T11:22:45Z",
        },
        "original_last_modified": "Thu, 26 Mar 2026 11:43:38 GMT",
        "failure_reason": None,
        "attempts": [
            {
                "url": replay,
                "retrieved_at": "2026-10-15T19:58:13+00:00",
                "http_status": 200,
                "error": None,
            }
        ],
    }


@pytest.fixture
def receipt():
    return collector.build_receipt([source(stamp) for stamp in collector.CAPTURES])


def rehash(receipt):
    for capture in receipt["captures"]:
        capture["receipt_sha256"] = canonical_receipt_digest(capture)
    receipt["receipt_sha256"] = canonical_receipt_digest(receipt)


def test_committed_receipt_and_offline_cli(monkeypatch, capsys):
    def forbid_network(*args, **kwargs):
        raise AssertionError("Offline checking attempted a network request")

    monkeypatch.setattr(collector.ArchiveClient, "fetch", forbid_network)
    committed = json.loads(collector.RECEIPT_PATH.read_text())
    assert collector.check_receipt(committed) is committed
    assert collector.main(["--check"]) == 0
    assert committed["receipt_sha256"] in capsys.readouterr().out
    assert [capture["archive_timestamp"] for capture in committed["captures"]] == list(
        collector.CAPTURES
    )
    assert committed["comparison"]["bytes_identical"] is True
    assert committed["byte_size"] == 1650665
    assert committed["sha256"] == (
        "1364c625a62daab8ec9b97a81ca5f93044a067fdf471e1645a62d73fdfa498f6"
    )


def test_receipt_refuses_changed_digest(receipt):
    receipt["sha256"] = "b" * 64
    with pytest.raises(ValueError, match="Receipt digest mismatch"):
        collector.check_receipt(receipt)


def test_capture_digest_is_checked_independently(receipt):
    receipt["captures"][1]["sha256"] = "b" * 64
    receipt["receipt_sha256"] = canonical_receipt_digest(receipt)
    with pytest.raises(ValueError, match="Capture receipt digest mismatch"):
        collector.check_receipt(receipt)


@pytest.mark.parametrize("replacement", ["im_", ""])
def test_receipt_refuses_non_id_replay_even_with_recomputed_digests(
    receipt, replacement
):
    receipt["captures"][0]["archive_capture_url"] = receipt["captures"][0][
        "archive_capture_url"
    ].replace("id_/", replacement + "/")
    receipt["archive_capture_url"] = receipt["captures"][0]["archive_capture_url"]
    rehash(receipt)
    with pytest.raises(ValueError, match="exact pinned id_ capture"):
        collector.check_receipt(receipt)


def test_receipt_refuses_wrong_capture_or_original(receipt):
    receipt["captures"][1]["original_url"] = "https://obr.uk/another.xlsx"
    rehash(receipt)
    with pytest.raises(ValueError, match="exact pinned id_ capture"):
        collector.check_receipt(receipt)


def test_differing_captures_lock_earlier_candidate_and_keep_both_digests():
    receipt = collector.build_receipt(
        [source(collector.CAPTURES[0]), source(collector.CAPTURES[1], "b" * 64)]
    )
    assert receipt["comparison"]["bytes_identical"] is False
    assert "different SHA-256" in receipt["comparison"]["classification_evidence"]
    assert receipt["launch_candidate"] is True
    assert receipt["archive_timestamp"] == collector.CAPTURES[0]
    assert collector.locked_source(receipt)["sha256"] == "a" * 64
    assert receipt["captures"][1]["sha256"] == "b" * 64


def test_post_publication_modification_is_a_later_revision():
    captures = [source(stamp) for stamp in collector.CAPTURES]
    for capture in captures:
        capture["workbook_properties"]["modified"] = "2026-03-27T11:22:45Z"
    receipt = collector.build_receipt(captures)
    assert receipt["capture_status"] == "later_revision"
    assert "postdates publication" in receipt["capture_status_evidence"]


def test_locked_source_does_not_mutate_receipt(receipt):
    before = copy.deepcopy(receipt)
    selected = collector.locked_source(receipt)
    selected["sheet_names"].append("Changed")
    assert receipt == before


def test_collection_persists_receipts_and_keeps_bytes_outside_repo(
    tmp_path, monkeypatch
):
    payload = workbook_bytes()
    requested = []

    class FakeArchiveClient:
        def __init__(self, pause_seconds, max_attempts):
            assert pause_seconds >= 4
            assert max_attempts == 3

        def fetch(self, url):
            requested.append(url)
            stamp = "2026-10-15T19:58:13+00:00"
            return (
                payload,
                {
                    "archive_capture_url": url,
                    "media_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    "original_last_modified": None,
                    "memento_datetime": None,
                    "retrieved_at": stamp,
                },
                [
                    {
                        "url": url,
                        "retrieved_at": stamp,
                        "http_status": 200,
                        "error": None,
                    }
                ],
            )

    monkeypatch.setattr(collector, "ArchiveClient", FakeArchiveClient)
    scratch = tmp_path / "scratch"
    receipt_path = tmp_path / "harvest/receipt.json"
    receipt = collector.collect(scratch, receipt_path)
    assert requested == [
        f"https://web.archive.org/web/{stamp}id_/{collector.ORIGINAL_URL}"
        for stamp in collector.CAPTURES
    ]
    digest = hashlib.sha256(payload).hexdigest()
    assert (scratch / f"{digest}.workbook").read_bytes() == payload
    assert receipt["sha256"] == digest
    assert json.loads(receipt_path.read_text()) == receipt
    attempts = json.loads((scratch / "collection_attempts.json").read_text())
    assert len(attempts["captures"]) == 2
    manifest = json.loads((receipt_path.parent / "manifest.jsonl").read_text())
    assert manifest["sha256"] == digest
    assert manifest["bytes"] == len(payload)
    assert set(receipt_path.parent.iterdir()) == {
        receipt_path,
        receipt_path.parent / "manifest.jsonl",
    }


def test_refuses_workbook_storage_under_repository():
    with pytest.raises(ValueError, match="outside the repository"):
        collector.collect(collector.ROOT / "downloads")


def test_failed_collection_retains_attempts_without_publishing_receipt(
    tmp_path, monkeypatch
):
    class FailedArchiveClient:
        def __init__(self, pause_seconds, max_attempts):
            pass

        def fetch(self, url):
            return (
                None,
                {},
                [
                    {
                        "url": url,
                        "retrieved_at": "2026-10-15T19:58:13+00:00",
                        "http_status": 503,
                        "error": "HTTP Error 503: Service Unavailable",
                    }
                ],
            )

    monkeypatch.setattr(collector, "ArchiveClient", FailedArchiveClient)
    scratch = tmp_path / "scratch"
    receipt_path = tmp_path / "harvest/receipt.json"
    with pytest.raises(ValueError, match="Both captures must be obtained"):
        collector.collect(scratch, receipt_path)
    assert not receipt_path.exists()
    captures = json.loads((scratch / "collection_attempts.json").read_text())[
        "captures"
    ]
    assert len(captures) == 2
    assert all(capture["status"] == "unavailable" for capture in captures)
    assert all(capture["attempts"][0]["http_status"] == 503 for capture in captures)
