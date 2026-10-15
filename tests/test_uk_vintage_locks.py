"""Engine-free contracts for the first historical replay events."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
from datetime import date, timedelta
from functools import lru_cache
from pathlib import Path

import pytest
from hypothesis import given, settings, strategies as st
from jsonschema import Draft202012Validator, FormatChecker, ValidationError

ROOT = Path(__file__).resolve().parents[1]
LOCK_DIR = ROOT / "data/uk/events/vintage_locks"
SELECTOR_DIR = ROOT / "docs/uk_replay/selectors"
SCHEMA_DIR = ROOT / "docs/uk_replay/schemas"
EVENTS = ("spring_statement_2022", "autumn_statement_2022", "autumn_budget_2021")
ROLES = {
    "economy",
    "receipts",
    "expenditure",
    "policy_measures",
    "hofd_row",
    "dwp_benefit_expenditure_caseload",
}
SURVEYS = {"frs_2019_20": "2021-03-25", "frs_2020_21": "2022-03-31"}


def read_json(path):
    return json.loads(path.read_text())


@lru_cache(maxsize=3)
def validator(name):
    schema = read_json(SCHEMA_DIR / f"{name}.v1.json")
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def receipt_digest(lock):
    payload = {key: value for key, value in lock.items() if key != "receipt_sha256"}
    return hashlib.sha256(
        json.dumps(
            payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode()
    ).hexdigest()


@lru_cache(maxsize=len(EVENTS))
def inventory_fys(event):
    rows = [
        json.loads(line)
        for line in (ROOT / "data/uk/events/inventory.jsonl").read_text().splitlines()
    ]
    return sorted(
        {fy for row in rows if row["event_key"] == event for fy in row["costing_gbp_m"]}
    )


def validate_selector(selector):
    """Cross-file/date invariants that JSON Schema cannot express."""
    validator("event_vintage_selector").validate(selector)
    event = selector["event_slug"]
    assert selector["scoring_fys"] == inventory_fys(event)
    for fy in selector["scoring_fys"]:
        assert int(fy[-2:]) == (int(fy[:4]) + 1) % 100
    surveys = selector["admissible_survey_releases"]
    assert len({release["release_id"] for release in surveys}) == len(surveys)
    assert selector["preferred_survey_release"] in {
        release["release_id"] for release in surveys
    }
    for release in surveys:
        fy = release["survey_fy"]
        assert int(fy[-2:]) == (int(fy[:4]) + 1) % 100
        assert release["release_id"] == "frs_" + fy.replace("-", "_")
        assert date.fromisoformat(release["published_at"]) < date.fromisoformat(
            selector["event_date"]
        )
    seen_roles = set()
    for ref in selector["source_locks"]:
        path = ROOT / ref["lock_path"]
        assert path.parent == LOCK_DIR and path.is_file()
        lock = read_json(path)
        assert path.stem == lock["event_slug"] == event
        assert lock["event_date"] == selector["event_date"]
        assert lock["forecast_vintage"] == selector["forecast_vintage"]
        assert receipt_digest(lock) == lock["receipt_sha256"] == ref["lock_sha256"]
        sources = {source["role"]: source for source in lock["sources"]}
        assert len(sources) == len(lock["sources"])
        for source in ref["sources"]:
            role = source["role"]
            assert role not in seen_roles
            seen_roles.add(role)
            assert source == {
                "role": role,
                "status": sources[role]["status"],
                "sha256": sources[role]["sha256"],
            }
    assert seen_roles == ROLES


def test_complete_slice_is_committed():
    assert {path.stem for path in LOCK_DIR.glob("*.json")} == set(EVENTS)
    assert {path.stem for path in SELECTOR_DIR.glob("*.json")} == set(EVENTS)


@pytest.mark.parametrize("path", sorted(LOCK_DIR.glob("*.json")), ids=lambda p: p.stem)
def test_every_lock_validates_and_binds_its_receipt(path):
    lock = read_json(path)
    validator("vintage_lock").validate(lock)
    assert lock["receipt_sha256"] == receipt_digest(lock)
    assert lock["event_slug"] == path.stem
    assert {source["role"] for source in lock["sources"]} == ROLES
    assert len(lock["sources"]) == len(ROLES)
    role_digests = []
    for source in lock["sources"]:
        if source["status"] == "obtained":
            assert re.fullmatch(r"[0-9a-f]{64}", source["sha256"])
            role_digests.append((source["role"], source["sha256"]))
            assert source["byte_size"] > 0
            assert source["failure_reason"] is None
            if "spreadsheet" in source["media_type"] or source["original_url"].endswith(
                (".xlsx", ".ods")
            ):
                assert source["sheet_names"]
        else:
            assert source["sha256"] is None and source["byte_size"] is None
            assert source["failure_reason"]
        if source["archive_capture_url"] is not None:
            assert (
                f"/web/{source['archive_timestamp']}id_/"
                in source["archive_capture_url"]
            )
        if source["role"] == "hofd_row" and source["status"] == "obtained":
            selection = source["selection"]
            assert selection["forecast_label"] == lock["forecast_vintage"]["label"]
            assert selection["verified_rows"]
            for row in selection["verified_rows"]:
                assert row["sheet"] in source["sheet_names"]
                assert row["cells"][row["label_cell"]] == row["raw_label"]
                assert (
                    re.sub(r"[†*]+$", "", row["raw_label"]).strip()
                    == selection["forecast_label"]
                )
    # Shared HOFD bytes across events are legitimate: uniqueness is per event/role.
    assert len(role_digests) == len(set(role_digests))


@pytest.mark.parametrize("event", EVENTS)
def test_selector_validates_and_references_only_committed_locks(event):
    validate_selector(read_json(SELECTOR_DIR / f"{event}.json"))


@given(event=st.sampled_from(EVENTS), release=st.sampled_from(tuple(SURVEYS)))
@settings(deadline=None)
def test_survey_admissibility_matches_publication_date(event, release):
    selector = read_json(SELECTOR_DIR / f"{event}.json")
    actual = {
        item["release_id"]: item for item in selector["admissible_survey_releases"]
    }
    expected = date.fromisoformat(SURVEYS[release]) < date.fromisoformat(
        selector["event_date"]
    )
    assert (release in actual) == expected
    if expected:
        assert actual[release]["published_at"] == SURVEYS[release]


@given(event=st.sampled_from(EVENTS), days=st.integers(min_value=0, max_value=3650))
@settings(max_examples=20, deadline=None)
def test_same_day_or_future_survey_is_rejected(event, days):
    selector = read_json(SELECTOR_DIR / f"{event}.json")
    publication = date.fromisoformat(selector["event_date"]) + timedelta(days=days)
    selector["admissible_survey_releases"][0]["published_at"] = publication.isoformat()
    with pytest.raises(AssertionError):
        validate_selector(selector)


@pytest.mark.parametrize("event", EVENTS)
def test_selector_rejects_changed_lock_digest(event):
    selector = read_json(SELECTOR_DIR / f"{event}.json")
    digest = selector["source_locks"][0]["lock_sha256"]
    selector["source_locks"][0]["lock_sha256"] = (
        "1" if digest[0] == "0" else "0"
    ) + digest[1:]
    with pytest.raises(AssertionError):
        validate_selector(selector)


PENDING = {
    "status": "pending",
    "value": "pending",
    "proposal": "docs/uk_replay/POLICY_WORLD_CONTRACT.md",
}
IDENTITY_FIELDS = (
    "policy_world",
    "historical_survey_release",
    "forecast_release_identity",
    "annualisation_bridge",
    "engine_commit",
    "population_artifact_digest",
    "certification_receipt",
)


def test_manifest_schema_keeps_certification_and_identity_pending():
    manifest = {
        "schema_version": "population_manifest.v1",
        "status": "draft",
        "event_slug": EVENTS[0],
        "costing_fy": "2021-22",
        **{field: PENDING for field in IDENTITY_FIELDS},
        "data_years": ["2021-22"],
    }
    validator("population_manifest").validate(manifest)
    invalid = copy.deepcopy(manifest)
    invalid["status"] = "certified"
    with pytest.raises(ValidationError):
        validator("population_manifest").validate(invalid)


def resolved_manifest_example():
    """Synthetic schema example; these strings do not identify real artifacts."""
    digest = "a" * 64
    engine = "b" * 40
    return {
        "schema_version": "population_manifest.v1",
        "status": "certified",
        "event_slug": EVENTS[0],
        "costing_fy": "2021-22",
        "policy_world": {
            "contract_id": "published_end_state_same_weights.v1",
            "contract_sha256": digest,
            "world": "published_end_state",
        },
        "historical_survey_release": {
            "release_id": "frs_2019_20",
            "published_at": "2021-03-25",
            "source_receipt_sha256": digest,
        },
        "forecast_release_identity": {
            "release_id": "obr_efo_march_2022",
            "selector_sha256": digest,
            "source_lock_sha256": digest,
        },
        "annualisation_bridge": {"bridge_id": "example", "receipt_sha256": digest},
        "engine_commit": engine,
        "population_artifact_digest": digest,
        "certification_receipt": {
            "receipt_sha256": digest,
            "engine_commit": engine,
            "population_artifact_digest": digest,
            "data_years": ["2021-22"],
        },
        "data_years": ["2021-22"],
    }


def test_resolved_certified_manifest_schema_example():
    validator("population_manifest").validate(resolved_manifest_example())


@pytest.mark.parametrize("field", IDENTITY_FIELDS)
def test_certified_manifest_rejects_each_pending_identity_field(field):
    manifest = resolved_manifest_example()
    manifest[field] = PENDING
    with pytest.raises(ValidationError):
        validator("population_manifest").validate(manifest)


@pytest.mark.parametrize("field", ("policy_world_contract", "annualisation_bridge"))
def test_ready_selector_rejects_each_pending_contract(field):
    selector = read_json(SELECTOR_DIR / f"{EVENTS[0]}.json")
    selector["readiness"] = "ready_for_population_build"
    selector["policy_world_contract"] = {
        "status": "resolved",
        "contract_id": "published_end_state_same_weights.v1",
        "contract_sha256": "a" * 64,
        "decision_receipt": "synthetic schema example",
    }
    selector["annualisation_bridge"] = {
        "bridge_id": "example",
        "receipt_sha256": "b" * 64,
    }
    validator("event_vintage_selector").validate(selector)
    selector[field] = {
        "status": "pending",
        "value": "pending",
        "proposal": "docs/uk_replay/POLICY_WORLD_CONTRACT.md",
        **({"decision": "cos d1344"} if field == "policy_world_contract" else {}),
    }
    validator("event_vintage_selector").validate(
        {**selector, "readiness": "contracts_pending"}
    )
    with pytest.raises(ValidationError):
        validator("event_vintage_selector").validate(selector)


@pytest.mark.parametrize("event", EVENTS)
def test_selectors_bind_the_d1344_decisions_by_digest(event):
    # cos d1344 (Max, 2026-10-15): the workstream makes the methodology calls;
    # each selector binds the chosen contract and bridge by their bytes.
    selector = read_json(SELECTOR_DIR / f"{event}.json")
    contracts = ROOT / "docs/uk_replay/contracts"
    contract = selector["policy_world_contract"]
    assert contract["status"] == "resolved"
    path = contracts / f"{contract['contract_id']}.md"
    assert contract["contract_sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
    assert "cos d1344" in contract["decision_receipt"]
    bridge = selector["annualisation_bridge"]
    receipt_path = contracts / "annualisation_fy_start_year.v1.json"
    assert (
        bridge["receipt_sha256"]
        == hashlib.sha256(receipt_path.read_bytes()).hexdigest()
    )
    receipt = read_json(receipt_path)
    assert receipt["bridge_id"] == bridge["bridge_id"]
    # Every scoring FY maps to its start year, and nothing else is mapped.
    assert receipt["event_years"][event] == {
        fy: int(fy[:4]) for fy in selector["scoring_fys"]
    }
    assert selector["readiness"] == "ready_for_population_build"


@pytest.mark.parametrize(
    "mutation", ("digest", "duplicate_role", "outturn", "empty_hofd")
)
def test_offline_checker_rejects_corrupt_receipts(tmp_path, mutation):
    spec = importlib.util.spec_from_file_location(
        "vintage_collector", ROOT / "data/uk/events/collect_vintage_locks.py"
    )
    collector = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(collector)
    locks = {event: read_json(LOCK_DIR / f"{event}.json") for event in EVENTS}
    lock = locks[EVENTS[0]]
    if mutation == "digest":
        lock["receipt_sha256"] = "0" * 64
    else:
        if mutation == "duplicate_role":
            lock["sources"][0]["role"] = lock["sources"][1]["role"]
        else:
            hofd = next(
                source for source in lock["sources"] if source["role"] == "hofd_row"
            )
            if mutation == "outturn":
                row = hofd["selection"]["verified_rows"][0]
                row["raw_label"] = row["cells"][row["label_cell"]] = "Outturn data*"
            else:
                hofd["selection"]["verified_rows"] = []
        lock["receipt_sha256"] = receipt_digest(lock)
    for event, value in locks.items():
        (tmp_path / f"{event}.json").write_text(json.dumps(value))
    with pytest.raises((ValueError, ValidationError)):
        collector.check_locks(tmp_path)


def load_collector():
    spec = importlib.util.spec_from_file_location(
        "vintage_collector", ROOT / "data/uk/events/collect_vintage_locks.py"
    )
    collector = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(collector)
    return collector


def source(lock, role):
    return next(s for s in lock["sources"] if s["role"] == role)


@pytest.mark.parametrize(
    "mutation",
    (
        "another_events_source",
        "false_launch",
        "captured_before_event",
        "unavailable_sheet_not_in_workbook",
        "another_events_dwp_edition",
        "later_revision_downgraded",
        "bad_datetime",
        "bad_uri",
    ),
)
def test_offline_checker_binds_each_source_to_its_event(tmp_path, mutation):
    # Review of 4c5f918: a source from another event, or a launch label on a
    # file edited after the event, passed the offline check.
    collector = load_collector()
    locks = {event: read_json(LOCK_DIR / f"{event}.json") for event in EVENTS}
    ss2022, ab2021 = locks["spring_statement_2022"], locks["autumn_budget_2021"]
    if mutation == "another_events_source":
        # Autumn Budget 2021's economy receipt in Spring Statement 2022's lock.
        borrowed = copy.deepcopy(source(ab2021, "economy"))
        ss2022["sources"] = [
            borrowed if s["role"] == "economy" else s for s in ss2022["sources"]
        ]
        target = ss2022
    elif mutation == "false_launch":
        receipts = source(ab2021, "receipts")
        assert receipts["workbook_properties"]["modified"][:10] > ab2021["event_date"]
        receipts["capture_status"] = "launch"
        target = ab2021
    elif mutation == "captured_before_event":
        economy = source(ss2022, "economy")
        economy["archive_timestamp"] = "20220101000000"
        economy["archive_capture_url"] = (
            f"https://web.archive.org/web/20220101000000id_/{economy['original_url']}"
        )
        target = ss2022
    elif mutation == "unavailable_sheet_not_in_workbook":
        as2022 = locks["autumn_statement_2022"]
        source(as2022, "economy")["unavailable_sheets"].append(
            {
                "sheet": "9.99",
                "reason": "not_produced_for_this_forecast",
                "notice": "x",
            }
        )
        target = as2022
    elif mutation == "another_events_dwp_edition":
        # Review of 55e22e2: DWP files were captured in 2025, so only the
        # edition's own name can tie them to their event.
        borrowed = copy.deepcopy(
            source(locks["autumn_statement_2022"], "dwp_benefit_expenditure_caseload")
        )
        ss2022["sources"] = [
            borrowed if s["role"] == "dwp_benefit_expenditure_caseload" else s
            for s in ss2022["sources"]
        ]
        target = ss2022
    elif mutation == "later_revision_downgraded":
        source(ab2021, "receipts")["capture_status"] = "unknown"
        target = ab2021
    elif mutation == "bad_datetime":
        source(ss2022, "economy")["retrieved_at"] = "not a datetime"
        target = ss2022
    else:
        source(ss2022, "economy")["original_url"] = "not a uri"
        target = ss2022
    target["receipt_sha256"] = receipt_digest(target)
    for event, value in locks.items():
        (tmp_path / f"{event}.json").write_text(json.dumps(value))
    with pytest.raises((ValueError, ValidationError)):
        collector.check_locks(tmp_path)


def test_autumn_statement_2022_records_its_event_day_partial_files():
    # Reviews of 4c5f918 and 55e22e2: in the OBR's event-day files some
    # sheets hold only a notice; each is recorded as unavailable with its
    # reason, and the later files are named without being locked.
    lock = read_json(LOCK_DIR / "autumn_statement_2022.json")
    by_reason = {}
    for role in ("economy", "receipts", "expenditure", "policy_measures"):
        for entry in source(lock, role).get("unavailable_sheets", []):
            by_reason.setdefault((role, entry["reason"]), set()).add(entry["sheet"])
    deferred, not_produced = (
        "deferred_to_later_release",
        "not_produced_for_this_forecast",
    )
    assert by_reason[("economy", deferred)] == {"1.8", "1.10", "1.12", "1.19"}
    assert by_reason[("economy", not_produced)] == {"1.11", "1.14", "1.15", "1.20"}
    assert len(by_reason[("receipts", deferred)]) == 9
    assert len(by_reason[("receipts", not_produced)]) == 12
    assert by_reason[("expenditure", deferred)] == {"3.2", "3.18"}
    assert len(by_reason[("expenditure", not_produced)]) == 8
    assert not any(role == "policy_measures" for role, _ in by_reason)
    for role in ("economy", "receipts", "expenditure", "policy_measures"):
        later = source(lock, role)["later_versions"]
        assert later and all(v["locked"] is False for v in later)
        assert all(v["first_archived"].startswith("20221209") for v in later)


def test_unavailable_source_cannot_invent_a_digest():
    lock = read_json(LOCK_DIR / f"{EVENTS[0]}.json")
    source = lock["sources"][0]
    source.update(
        status="unavailable",
        byte_size=None,
        sha256=None,
        media_type=None,
        sheet_names=[],
        failure_reason="Synthetic unavailable-source schema example",
    )
    validator("vintage_lock").validate(lock)
    source["sha256"] = "a" * 64
    with pytest.raises(ValidationError):
        validator("vintage_lock").validate(lock)


def test_check_command_is_offline(tmp_path):
    # Block sockets in the child too: --check must not depend on any network path.
    (tmp_path / "sitecustomize.py").write_text(
        "import socket\n"
        "def forbidden(*args, **kwargs):\n"
        "    raise RuntimeError('Network is forbidden during --check')\n"
        "socket.socket.connect = forbidden\n"
        "socket.socket.connect_ex = forbidden\n"
        "socket.create_connection = forbidden\n"
        "socket.getaddrinfo = forbidden\n"
    )
    env = {**os.environ, "PYTHONPATH": str(tmp_path)}
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "data/uk/events/collect_vintage_locks.py"),
            "--check",
        ],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stdout + result.stderr
