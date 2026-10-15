"""Collect public source receipts through Wayback, or check them offline.

This script downloads no survey data and imports no microsimulation engine.
Downloaded public workbooks remain in the caller's scratch directory.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import io
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from datetime import date, datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LOCK_DIR = ROOT / "data/uk/events/vintage_locks"
SCHEMA_PATH = ROOT / "docs/uk_replay/schemas/vintage_lock.v1.json"
USER_AGENT = "policyengine-scorecard-research/1.0"
ROLES = (
    "economy",
    "receipts",
    "expenditure",
    "policy_measures",
    "hofd_row",
    "dwp_benefit_expenditure_caseload",
)
PUBLIC_HOSTS = {"obr.uk", "www.gov.uk", "assets.publishing.service.gov.uk"}
ARCHIVE_PATTERN = re.compile(
    r"^https://web\.archive\.org/web/(\d{14})id_/(https?://.+)$"
)
NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
REL_NS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"


OBR_ROLES = ("economy", "receipts", "expenditure", "policy_measures")
# Autumn Statement 2022: the OBR's event-day files deferred some tables to
# 24 November, and later files of the same forecast replaced them under other
# names (first archived 9 December 2022). The locks keep the event-day bytes,
# record each deferred sheet as unavailable in them, and name the later files
# without locking them. Sheets were found by their shared-string cells reading
# the notice; later files from the archive's CDX index.
FIRST_DAY_FILES = {
    ("autumn_statement_2022", "economy"): (
        ["1.8", "1.10", "1.12", "1.19"],
        ["This table will be published at 11am on 24 November."],
        "Economy_supplementary_tables_November_2022_v2-1.xlsx",
        "20221209171229",
    ),
    ("autumn_statement_2022", "receipts"): (
        ["2.13", "3.1", "3.2", "3.3", "3.4", "3.8", "3.11", "3.17", "3.18"],
        [
            "This table will be published at 11am on 24 November.",
            "This table will be published at 11 am on 24 November.",
        ],
        "Fiscal_supplementary_tables_Receiptsother_November_2022_v3.xlsx",
        "20221209145619",
    ),
    ("autumn_statement_2022", "expenditure"): (
        ["3.2", "3.18"],
        ["This table will be published at 11am on 24 November."],
        "Fiscal_supplementary_tables_expenditure_November_2022_v3.xlsx",
        "20221209171019",
    ),
    ("autumn_statement_2022", "policy_measures"): (
        [],
        [],
        "Economic_and_fiscal_outlook_charts_and_tables_November_2022-2.xlsx",
        "20221209153101",
    ),
}


def canonical_receipt_digest(lock: dict) -> str:
    """The digest binds all metadata except the self-referential digest field."""
    payload = {key: value for key, value in lock.items() if key != "receipt_sha256"}
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _source(role: str, timestamp: str, original: str, edition: str) -> dict:
    return {
        "role": role,
        "original_url": original,
        "archive_capture_url": f"https://web.archive.org/web/{timestamp}id_/{original}",
        "archive_timestamp": timestamp,
        "edition": edition,
        "capture_status": "unknown",
        "capture_status_evidence": (
            "Earliest capture listed in research/archive_obr.md; a capture date "
            "alone does not prove that these are the first published bytes."
        ),
    }


def source_catalog() -> dict[str, dict]:
    """Pinned replay queue: no live publisher endpoint is requested."""
    events = {
        "spring_statement_2022": (
            "2022-03-23",
            "march_2022",
            "March 2022",
            [
                (
                    "economy",
                    "20220323220804",
                    "Economy_Supplementary_Tables_March_2022-1.xlsx",
                ),
                (
                    "receipts",
                    "20220323220807",
                    "Fiscal_Supplementary_Tables_Receiptsother_March_2022-2.xlsx",
                ),
                (
                    "expenditure",
                    "20220323220800",
                    "Fiscal_Supplementary_Tables_Expenditure_March_2022.xlsx",
                ),
                (
                    "policy_measures",
                    "20220323220812",
                    "Annex_A_charts_and_tables_March_2022.xlsx",
                ),
            ],
        ),
        "autumn_statement_2022": (
            "2022-11-17",
            "november_2022",
            "November 2022",
            [
                (
                    "economy",
                    "20221117122504",
                    "Economy_supplementary_tables_November_2022.xlsx",
                ),
                (
                    "receipts",
                    "20221117122532",
                    "Fiscal_supplementary_tables_Receiptsother_November_2022.xlsx",
                ),
                (
                    "expenditure",
                    "20221117131030",
                    "Fiscal_supplementary_tables_expenditure_November_2022.xlsx",
                ),
                (
                    "policy_measures",
                    "20221117122512",
                    "Economic_and_fiscal_outlook_charts_and_tables_November_2022.xlsx",
                ),
            ],
        ),
        "autumn_budget_2021": (
            "2021-10-27",
            "october_2021",
            "October 2021",
            [
                (
                    "economy",
                    "20211118203949",
                    "october-2021-economic-and-fiscal-outlook-supplementary-economy-tables",
                ),
                (
                    "receipts",
                    "20211103105119",
                    "october-2021-economic-and-fiscal-outlook-supplementary-fiscal-tables-receipts-and-other",
                ),
                (
                    "expenditure",
                    "20211101172726",
                    "october-2021-economic-and-fiscal-outlook-supplementary-fiscal-tables-expenditure",
                ),
                (
                    "policy_measures",
                    "20211104130349",
                    "october-2021-economic-and-fiscal-outlook-charts-and-tables-annex-a",
                ),
            ],
        ),
    }
    catalog = {}
    for slug, (date, vintage, label, files) in events.items():
        sources = []
        for role, stamp, name in files:
            original = (
                f"https://obr.uk/docs/dlm_uploads/{name}"
                if name.endswith(".xlsx")
                else f"https://obr.uk/download/{name}/"
            )
            sources.append(_source(role, stamp, original, label))
            if (slug, role) in FIRST_DAY_FILES:
                sheets, notices, later, first_archived = FIRST_DAY_FILES[(slug, role)]
                deferred = (
                    f"Event-day file: sheets {', '.join(sheets)} hold only the notice "
                    "that the table would be published on 24 November, so they are "
                    "unavailable in these bytes. "
                    if sheets
                    else "Event-day file with no deferred-table notice. "
                )
                sources[-1]["capture_status_evidence"] = (
                    f"{deferred}A later file of the same forecast, {later}, was first "
                    f"archived {first_archived[:4]}-{first_archived[4:6]}-"
                    f"{first_archived[6:8]} and is not locked here."
                )
                if sheets:
                    sources[-1]["deferred_sheets"] = {
                        "sheets": sheets,
                        "notices": notices,
                    }
                sources[-1]["later_versions"] = [
                    {
                        "original_url": f"https://obr.uk/docs/dlm_uploads/{later}",
                        "first_archived": first_archived,
                        "locked": False,
                    }
                ]
            if slug == "autumn_budget_2021" and role == "receipts":
                sources[-1].update(
                    capture_status="later_revision",
                    capture_status_evidence=(
                        "Fetched workbook docProps/core.xml modified timestamp is "
                        "2021-10-28T11:59:23Z, after the 27 October 2021 event. "
                        "This identifies a later edited file; whether numeric cells "
                        "changed from launch is unverified."
                    ),
                )
        catalog[slug] = {
            "event_slug": slug,
            "event_date": date,
            "forecast_vintage": {
                "id": f"obr_efo_{vintage}",
                "label": label,
                "published_at": date,
            },
            "sources": sources,
        }
        hofd = _source(
            "hofd_row",
            "20250404155002",
            "https://obr.uk/docs/Historical_official_forecasts_database_March_2025.xlsx",
            "March 2025 cross-vintage database; historical forecast row selected",
        )
        hofd.update(
            capture_status="later_revision",
            capture_status_evidence=(
                "March 2025 database edition postdates the event. Its historical "
                "event-labelled forecast rows are selected, never Outturn data*. "
                "Capture identity also appears in the read-only public harvest manifest."
            ),
            selection={"forecast_label": label, "verified_rows": []},
        )
        sources.append(hofd)
        dwp = {
            "spring_statement_2022": (
                "20250822055644",
                (
                    "https://assets.publishing.service.gov.uk/media/"
                    "628765278fa8f5561f02a41b/outturn-and-forecast-spring-statement-2022.xlsx"
                ),
                "2022-05-24",
            ),
            "autumn_statement_2022": (
                "20250903062039",
                (
                    "https://assets.publishing.service.gov.uk/media/"
                    "63a05310d3bf7f375f7c4359/outturn-and-forecast-tables-autumn-statement-2022.xlsx"
                ),
                "2022-12-21",
            ),
            "autumn_budget_2021": (
                "20211119154331",
                (
                    "https://assets.publishing.service.gov.uk/government/uploads/"
                    "system/uploads/attachment_data/file/1034496/"
                    "outturn-and-forecast-tables-autumn-budget-2021.ods"
                ),
                "2021-11-19",
            ),
        }[slug]
        dwp_source = _source(
            "dwp_benefit_expenditure_caseload",
            dwp[0],
            dwp[1],
            f"Outturn and forecast tables: {slug.replace('_', ' ')}; added {dwp[2]}",
        )
        dwp_source["capture_status_evidence"] = (
            "DWP publication date recorded in research/archive_govuk.md; "
            "the later archive capture cannot establish first-release bytes."
        )
        sources.append(dwp_source)
        if slug == "autumn_budget_2021":
            dwp_source.update(
                capture_status_evidence=(
                    "Attachment URL verified in the GOV.UK publication page captured "
                    "20211119154331, on the edition's 19 November 2021 publication day. "
                    "This establishes the launch attachment; absence of an earlier "
                    "same-day change is not independently established."
                ),
            )
    return catalog


class ArchiveRedirects(urllib.request.HTTPRedirectHandler):
    def __init__(self, pause_seconds: float):
        self.pause_seconds = pause_seconds
        self.attempts: list[dict] = []

    def redirect_request(self, request, fp, code, message, headers, new_url):
        """Do not let archive redirects accidentally contact a live publisher."""
        match = ARCHIVE_PATTERN.fullmatch(new_url)
        if not match or urllib.parse.urlsplit(match[2]).hostname not in PUBLIC_HOSTS:
            raise urllib.error.URLError(f"Refused non-id_ archive redirect: {new_url}")
        self.attempts.append(
            {
                "url": request.full_url,
                "retrieved_at": datetime.now(timezone.utc).isoformat(
                    timespec="seconds"
                ),
                "http_status": code,
                "error": None,
            }
        )
        time.sleep(self.pause_seconds)
        return super().redirect_request(request, fp, code, message, headers, new_url)


class ArchiveClient:
    def __init__(self, pause_seconds: float = 4.0, max_attempts: int = 3):
        self.pause_seconds = pause_seconds
        self.max_attempts = max_attempts
        self.redirects = ArchiveRedirects(pause_seconds)
        self.opener = urllib.request.build_opener(self.redirects)
        self.last_request = 0.0
        self.cache: dict[str, tuple[bytes, dict, list[dict]]] = {}

    def fetch(self, url: str) -> tuple[bytes | None, dict, list[dict]]:
        if url in self.cache:
            return copy.deepcopy(self.cache[url])
        match = ARCHIVE_PATTERN.fullmatch(url)
        if not match or urllib.parse.urlsplit(match[2]).hostname not in PUBLIC_HOSTS:
            raise ValueError(f"Not an allowed public id_ replay: {url}")
        attempts = []
        self.redirects.attempts = attempts
        for attempt in range(self.max_attempts):
            delay = max(0, self.pause_seconds - (time.monotonic() - self.last_request))
            if attempt:
                delay = max(delay, min(60, 15 * 2 ** (attempt - 1)))
            time.sleep(delay)
            self.last_request = time.monotonic()
            observed = datetime.now(timezone.utc).isoformat(timespec="seconds")
            request = urllib.request.Request(
                url, headers={"User-Agent": USER_AGENT, "Accept-Encoding": "identity"}
            )
            try:
                with self.opener.open(request, timeout=60) as response:
                    if response.status != 200:
                        raise urllib.error.URLError(
                            f"Expected complete HTTP 200 file, received {response.status}"
                        )
                    payload = response.read()
                    length = response.headers.get("Content-Length")
                    if length is not None and len(payload) != int(length):
                        raise urllib.error.URLError("Incomplete response body")
                    self.last_request = time.monotonic()
                    metadata = {
                        "archive_capture_url": response.url,
                        "media_type": response.headers.get_content_type(),
                        "original_last_modified": response.headers.get(
                            "x-archive-orig-last-modified"
                        ),
                        "memento_datetime": response.headers.get("memento-datetime"),
                        "retrieved_at": observed,
                    }
                    attempts.append(
                        {
                            "url": url,
                            "retrieved_at": observed,
                            "http_status": response.status,
                            "error": None,
                        }
                    )
                    self.cache[url] = (payload, metadata, attempts)
                    return payload, metadata, attempts
            except (urllib.error.URLError, TimeoutError, OSError) as error:
                status = (
                    error.code if isinstance(error, urllib.error.HTTPError) else None
                )
                attempts.append(
                    {
                        "url": url,
                        "retrieved_at": observed,
                        "http_status": status,
                        "error": str(error),
                    }
                )
                if status is not None and status not in {429, 500, 502, 503, 504}:
                    break
        return None, {}, attempts


def workbook_metadata(payload: bytes) -> tuple[list[str], dict]:
    """Read public xlsx/ods workbook metadata with the standard library."""
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        if "xl/workbook.xml" in archive.namelist():
            workbook = ET.fromstring(archive.read("xl/workbook.xml"))
            names = [
                sheet.attrib["name"]
                for sheet in workbook.findall(f"{NS}sheets/{NS}sheet")
            ]
        elif "content.xml" in archive.namelist():
            root = ET.fromstring(archive.read("content.xml"))
            ods_ns = "{urn:oasis:names:tc:opendocument:xmlns:table:1.0}"
            names = [
                table.attrib[f"{ods_ns}name"] for table in root.iter(f"{ods_ns}table")
            ]
        else:
            raise ValueError("Archive bytes are not an xlsx/ods workbook")
        properties = {}
        if "docProps/core.xml" in archive.namelist():
            for element in ET.fromstring(archive.read("docProps/core.xml")):
                if element.tag.rsplit("}", 1)[-1] in {"created", "modified"}:
                    properties[element.tag.rsplit("}", 1)[-1]] = element.text
        return names, properties


def read_xlsx_cells(
    payload: bytes, *, max_row: int | None = None
) -> dict[str, dict[str, str]]:
    """Resolve string/numeric cells for source titles and selected HOFD rows."""
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        shared = []
        if "xl/sharedStrings.xml" in archive.namelist():
            shared = [
                "".join(element.itertext())
                for element in ET.fromstring(archive.read("xl/sharedStrings.xml"))
            ]
        relationships = {
            element.attrib["Id"]: element.attrib["Target"]
            for element in ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        }
        sheets = {}
        for sheet in ET.fromstring(archive.read("xl/workbook.xml")).findall(
            f"{NS}sheets/{NS}sheet"
        ):
            target = relationships[sheet.attrib[f"{REL_NS}id"]]
            filename = target.lstrip("/") if target.startswith("/") else f"xl/{target}"
            cells = {}
            with archive.open(filename) as stream:
                for event, element in ET.iterparse(stream, events=("start", "end")):
                    if (
                        event == "start"
                        and element.tag == f"{NS}row"
                        and max_row is not None
                        and int(element.attrib["r"]) > max_row
                    ):
                        break
                    if event != "end" or element.tag != f"{NS}c":
                        continue
                    value = element.find(f"{NS}v")
                    inline = element.find(f"{NS}is")
                    if value is not None:
                        raw = value.text or ""
                        cells[element.attrib["r"]] = (
                            shared[int(raw)] if element.get("t") == "s" else raw
                        )
                    elif inline is not None:
                        cells[element.attrib["r"]] = "".join(inline.itertext())
                    element.clear()
            sheets[sheet.attrib["name"]] = cells
        return sheets


def collect_source(client: ArchiveClient, source: dict, scratch: Path) -> dict:
    result = copy.deepcopy(source)
    payload, metadata, attempts = client.fetch(source["archive_capture_url"])
    result.update(
        status="unavailable",
        retrieved_at=attempts[-1]["retrieved_at"],
        byte_size=None,
        sha256=None,
        media_type=None,
        sheet_names=[],
        workbook_properties={},
        original_last_modified=None,
        failure_reason=attempts[-1]["error"],
        attempts=attempts,
    )
    if payload is None:
        return result
    try:
        names, properties = workbook_metadata(payload)
    except (ValueError, zipfile.BadZipFile, ET.ParseError) as error:
        result["failure_reason"] = f"Response is not a readable workbook: {error}"
        return result
    actual = ARCHIVE_PATTERN.fullmatch(metadata["archive_capture_url"])
    if actual is None:
        raise ValueError("Returned response has no exact id_ capture identity")
    stamp = actual[1]
    if metadata["memento_datetime"]:
        observed_stamp = parsedate_to_datetime(metadata["memento_datetime"]).strftime(
            "%Y%m%d%H%M%S"
        )
        if observed_stamp != stamp:
            raise ValueError("Capture URL and Memento-Datetime disagree")
    result.update(
        status="obtained",
        archive_capture_url=metadata["archive_capture_url"],
        archive_timestamp=stamp,
        original_url=actual[2],
        byte_size=len(payload),
        sha256=hashlib.sha256(payload).hexdigest(),
        media_type=metadata["media_type"],
        sheet_names=names,
        workbook_properties=properties,
        original_last_modified=metadata["original_last_modified"],
        failure_reason=None,
    )
    filename = f"{result['sha256']}.workbook"
    (scratch / filename).write_bytes(payload)
    if source["role"] == "hofd_row":
        rows = []
        for sheet, cells in read_xlsx_cells(payload).items():
            for coordinate, value in cells.items():
                if (
                    re.fullmatch(r"A[0-9]+", coordinate)
                    and re.sub(r"[†*]+$", "", value).strip()
                    == source["selection"]["forecast_label"]
                ):
                    row_number = coordinate[1:]
                    values = {
                        ref: text
                        for ref, text in cells.items()
                        if re.fullmatch(rf"[A-Z]+{row_number}", ref)
                    }
                    rows.append(
                        {
                            "sheet": sheet,
                            "label_cell": coordinate,
                            "raw_label": value,
                            "cells": values,
                        }
                    )
        result["selection"]["verified_rows"] = rows
    return result


def check_locks(lock_dir: Path = LOCK_DIR) -> list[dict]:
    """Validate committed receipts only; this function never opens a socket."""
    import jsonschema

    schema = json.loads(SCHEMA_PATH.read_text())
    validator = jsonschema.Draft202012Validator(
        schema, format_checker=jsonschema.FormatChecker()
    )
    locks = []
    for path in sorted(lock_dir.glob("*.json")):
        lock = json.loads(path.read_text())
        validator.validate(lock)
        if path.stem != lock["event_slug"]:
            raise ValueError(f"Wrong event filename: {path}")
        if canonical_receipt_digest(lock) != lock["receipt_sha256"]:
            raise ValueError(f"Receipt digest mismatch: {path}")
        if lock["forecast_vintage"]["published_at"] != lock["event_date"]:
            raise ValueError(f"Forecast publication and event dates disagree: {path}")
        sources = lock["sources"]
        if sorted(source["role"] for source in sources) != sorted(ROLES):
            raise ValueError(
                f"Exactly one source for each core role is required: {path}"
            )
        obtained_digests = []
        event_day = date.fromisoformat(lock["event_date"])
        for source in sources:
            role = source["role"]
            # A source belongs to its event: an OBR file names this forecast,
            # and nothing but the cross-vintage HOFD was captured before the
            # event; a file edited after the event is not its launch bytes.
            if (
                role in OBR_ROLES
                and source["edition"] != lock["forecast_vintage"]["label"]
            ):
                raise ValueError(f"Edition names another forecast: {path}: {role}")
            captured = datetime.strptime(source["archive_timestamp"], "%Y%m%d%H%M%S")
            if role != "hofd_row" and captured.date() < event_day:
                raise ValueError(f"Captured before the event: {path}: {role}")
            modified = (source.get("workbook_properties") or {}).get("modified")
            if (
                source["capture_status"] == "launch"
                and modified
                and date.fromisoformat(modified[:10]) > event_day
            ):
                raise ValueError(f"Launch file edited after the event: {path}: {role}")
            deferred = (source.get("deferred_sheets") or {}).get("sheets", [])
            if source["status"] == "obtained" and not set(deferred) <= {
                name.strip() for name in source["sheet_names"]
            }:
                raise ValueError(f"Deferred sheet not in the workbook: {path}: {role}")
            match = ARCHIVE_PATTERN.fullmatch(source["archive_capture_url"])
            if (
                not match
                or match[1] != source["archive_timestamp"]
                or match[2] != source["original_url"]
            ):
                raise ValueError(f"Capture identity mismatch: {path}: {source['role']}")
            datetime.strptime(source["archive_timestamp"], "%Y%m%d%H%M%S").replace(
                tzinfo=timezone.utc
            )
            if (
                urllib.parse.urlsplit(source["original_url"]).hostname
                not in PUBLIC_HOSTS
            ):
                raise ValueError(f"Unexpected publisher: {path}: {source['role']}")
            if source["status"] == "obtained":
                obtained_digests.append(source["sha256"])
                if source["role"] == "hofd_row":
                    selection = source["selection"]
                    label = lock["forecast_vintage"]["label"]
                    if selection["forecast_label"] != label:
                        raise ValueError(f"HOFD forecast selection mismatch: {path}")
                    if not selection["verified_rows"]:
                        raise ValueError(f"No verified HOFD forecast rows: {path}")
                    for row in selection["verified_rows"]:
                        raw_label = row["raw_label"]
                        normalized = re.sub(r"[†*]+$", "", raw_label.strip()).strip()
                        if (
                            row["sheet"] not in source["sheet_names"]
                            or "outturn" in raw_label.lower()
                            or normalized != label
                            or row["cells"].get(row["label_cell"]) != raw_label
                        ):
                            raise ValueError(
                                f"Invalid selected HOFD row: {path}: {row['sheet']}"
                            )
            elif not source["failure_reason"]:
                raise ValueError(f"Missing reason: {path}: {source['role']}")
        if len(obtained_digests) != len(set(obtained_digests)):
            raise ValueError(f"Two roles bind the same source bytes: {path}")
        locks.append(lock)
    expected = set(source_catalog())
    if {lock["event_slug"] for lock in locks} != expected:
        raise ValueError(f"Expected locks for {sorted(expected)}")
    return locks


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate committed receipts without network",
    )
    parser.add_argument("--event", choices=list(source_catalog()), action="append")
    parser.add_argument(
        "--scratch-dir",
        type=Path,
        help="Required download directory outside the repository",
    )
    parser.add_argument("--pause-seconds", type=float, default=4.0)
    parser.add_argument("--max-attempts", type=int, default=3)
    args = parser.parse_args(argv)
    if args.check:
        locks = check_locks()
        print(f"Validated {len(locks)} vintage locks offline")
        return 0
    if args.scratch_dir is None:
        parser.error("--scratch-dir is required for collection")
    scratch = args.scratch_dir.resolve()
    if scratch == ROOT or ROOT in scratch.parents:
        parser.error("Downloaded files must remain outside the repository")
    if not 3 <= args.pause_seconds <= 6:
        parser.error("--pause-seconds must be between 3 and 6")
    if not 1 <= args.max_attempts <= 5:
        parser.error("--max-attempts must be between 1 and 5")
    scratch.mkdir(parents=True, exist_ok=True)
    LOCK_DIR.mkdir(parents=True, exist_ok=True)
    client = ArchiveClient(args.pause_seconds, args.max_attempts)
    for slug, event in source_catalog().items():
        if args.event and slug not in args.event:
            continue
        lock = {
            "schema_version": "vintage_lock.v1",
            **event,
            "collected_at": datetime.now(timezone.utc).date().isoformat(),
            "collector": {
                "user_agent": USER_AGENT,
                "archive_replay_mode": "id_",
                "pause_seconds": args.pause_seconds,
                "max_attempts": args.max_attempts,
            },
        }
        lock["sources"] = []
        for source in event["sources"]:
            receipt = collect_source(client, source, scratch)
            lock["sources"].append(receipt)
            print(f"{slug}: {receipt['role']}: {receipt['status']}", flush=True)
            lock["receipt_sha256"] = canonical_receipt_digest(lock)
            (LOCK_DIR / f"{slug}.json").write_text(
                json.dumps(lock, indent=2, ensure_ascii=False) + "\n"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
