"""The qualification request/receipt identities shared with policyengine.py."""

import copy
import json
import random
from pathlib import Path

import jsonschema
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from pipeline import uk_replay_interface as ui

FIXTURES = Path(__file__).parent / "fixtures" / "uk_replay"
DIGESTS = json.loads((FIXTURES / "DIGESTS.json").read_text())


def golden(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_golden_request_bytes_and_id_are_pinned():
    request = golden("qualification_request_golden.json")
    assert (
        ui.jcs_bytes(request)
        == (FIXTURES / "qualification_request_golden.jcs").read_bytes()
    )
    assert (
        ui.validate_request(request)
        == DIGESTS["qualification_request_golden.json"]["request_id"]
    )


def test_golden_receipt_bytes_and_digest_are_pinned():
    receipt = golden("replay_receipt_golden.json")
    ui.validate(receipt, ui.RECEIPT_SCHEMA_ID)
    body = {k: v for k, v in receipt.items() if k != "receipt_sha256"}
    assert ui.jcs_bytes(body) == (FIXTURES / "replay_receipt_golden.jcs").read_bytes()
    assert (
        receipt["receipt_sha256"]
        == DIGESTS["replay_receipt_golden.json"]["receipt_sha256"]
    )
    assert receipt["request_id"] == ui.request_id(
        golden("qualification_request_golden.json")
    )


def test_jcs_numbers_and_strings_follow_rfc8785_not_json_dumps():
    probe = golden("qualification_request_golden.json")["requested_by"]
    assert ui.jcs_bytes(probe["jcs_probe"]) == (
        b"[1e-7,15000000000000000,0.30000000000000004,0,1e+21,5e-324,"
        b"123456789012345680000,9007199254740991]"
    )
    # json.dumps writes 1e-07 and escapes non-ASCII; JCS does neither.
    assert json.dumps(1e-7) == "1e-07"
    assert ui.jcs_bytes("café £") == '"café £"'.encode()


def test_integers_beyond_double_precision_are_refused():
    with pytest.raises(Exception):
        ui.jcs_bytes([2**53 + 1])


def test_request_id_is_never_a_request_field():
    request = golden("qualification_request_golden.json")
    with pytest.raises(ValueError):
        ui.request_id({**request, "request_id": "0" * 64})
    with pytest.raises(jsonschema.ValidationError):
        ui.validate_request({**request, "request_id": "0" * 64})


@pytest.mark.parametrize(
    "mutate",
    [
        lambda r: r.update(kind="nightly"),
        lambda r: r.update(attempt=0),
        lambda r: r["candidate"]["data"].update(sha256="ABC"),
        lambda r: r["candidate"]["data"].update(repo_type="space"),
        lambda r: r["candidate"]["policyengine_uk"].pop("wheel_sha256"),
        lambda r: r["candidate"].update(extra=True),
        lambda r: r["requested_by"].update(commit="481940ec"),
        # A released bundle is identified by its PyPI wheel, never a branch.
        lambda r: r.update(kind="released_bundle"),
    ],
)
def test_request_schema_rejects_malformed_requests(mutate):
    request = golden("qualification_request_golden.json")
    mutate(request)
    with pytest.raises(jsonschema.ValidationError):
        ui.validate_request(request)


def test_released_bundle_request_names_its_pypi_wheel():
    request = golden("qualification_request_golden.json")
    request["kind"] = "released_bundle"
    request["candidate"]["policyengine"]["source"] = {
        "pypi": {
            "wheel_sha256": "9ac20a2599cc1f4b50c128c2245042b105c40592e07fc25d39c99a529c9f410b"
        }
    }
    assert len(ui.validate_request(request)) == 64


def test_requested_by_accepts_additional_provenance():
    request = golden("qualification_request_golden.json")
    request["requested_by"]["actor"] = "github-actions[bot]"
    ui.validate_request(request)


def test_rejected_receipt_carries_a_reason_and_no_results():
    receipt = golden("replay_receipt_golden.json")
    receipt.update(
        status="rejected",
        rejection={"code": "release_bundle_mismatch", "detail": "model_version"},
        variant_id=None,
        variant_identity_sha256=None,
        execution=None,
        corpus=None,
        diff=None,
        integrity={"status": "not_run", "failures": []},
    )
    ui.validate(ui.seal_receipt(receipt), ui.RECEIPT_SCHEMA_ID)
    with pytest.raises(jsonschema.ValidationError):
        ui.validate(
            ui.seal_receipt({**receipt, "rejection": None}), ui.RECEIPT_SCHEMA_ID
        )
    with pytest.raises(jsonschema.ValidationError):
        ui.validate(
            ui.seal_receipt(
                {**receipt, "corpus": golden("replay_receipt_golden.json")["corpus"]}
            ),
            ui.RECEIPT_SCHEMA_ID,
        )


def _rejected():
    receipt = golden("replay_receipt_golden.json")
    receipt.update(
        status="rejected",
        rejection={"code": "incompatible_pair", "detail": "x"},
        variant_id=None,
        variant_identity_sha256=None,
        execution=None,
        corpus=None,
        diff=None,
        integrity={"status": "not_run", "failures": []},
    )
    return receipt


@pytest.mark.parametrize(
    "change",
    [
        # A rejected request ran nothing and has no identity (review of #160, M6).
        {"variant_id": "pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0"},
        {"variant_identity_sha256": "0" * 64},
        {"execution": golden("replay_receipt_golden.json")["execution"]},
        {"integrity": {"status": "complete", "failures": []}},
        {"integrity": {"status": "failed", "failures": []}},
    ],
)
def test_a_rejected_receipt_cannot_claim_a_run(change):
    ui.validate(ui.seal_receipt(_rejected()), ui.RECEIPT_SCHEMA_ID)
    with pytest.raises(jsonschema.ValidationError):
        ui.validate(ui.seal_receipt({**_rejected(), **change}), ui.RECEIPT_SCHEMA_ID)


def test_a_complete_receipt_names_its_identity_and_sealed_namespace():
    receipt = golden("replay_receipt_golden.json")
    del receipt["receipt_sha256"]
    with pytest.raises(jsonschema.ValidationError):
        ui.validate(
            ui.seal_receipt({**receipt, "variant_identity_sha256": None}),
            ui.RECEIPT_SCHEMA_ID,
        )
    results = {k: v for k, v in receipt["results"].items() if k != "manifest_sha256"}
    with pytest.raises(jsonschema.ValidationError):
        ui.validate(
            ui.seal_receipt({**receipt, "results": results}), ui.RECEIPT_SCHEMA_ID
        )


def test_a_failed_receipt_cannot_report_complete_integrity():
    receipt = golden("replay_receipt_golden.json")
    del receipt["receipt_sha256"]
    receipt["status"] = "failed"
    for status in ("complete", "incomplete", "not_run"):
        with pytest.raises(jsonschema.ValidationError):
            ui.validate(
                ui.seal_receipt(
                    {**receipt, "integrity": {"status": status, "failures": []}}
                ),
                ui.RECEIPT_SCHEMA_ID,
            )


def test_execution_python_is_exactly_a_version():
    receipt = golden("replay_receipt_golden.json")
    del receipt["receipt_sha256"]
    receipt["execution"] = {**receipt["execution"], "python": "3.12.13; rm -rf"}
    with pytest.raises(jsonschema.ValidationError):
        ui.validate(ui.seal_receipt(receipt), ui.RECEIPT_SCHEMA_ID)


@pytest.mark.parametrize("path", ["../x.h5", "a/../x.h5", "a/..", ".."])
def test_request_dataset_path_has_no_parent_segments(path):
    request = golden("qualification_request_golden.json")
    request["candidate"]["data"]["path"] = path
    with pytest.raises(jsonschema.ValidationError):
        ui.validate_request(request)


def test_tampered_receipt_fails_its_digest():
    receipt = golden("replay_receipt_golden.json")
    receipt["diff"]["flagged_rows"][0]["head_gbp"] = 0.3
    with pytest.raises(ValueError):
        ui.validate(receipt, ui.RECEIPT_SCHEMA_ID)


def test_terminal_status_binds_receipt_digest_and_commit():
    status = {
        "schema": ui.STATUS_SCHEMA_ID,
        "request_id": DIGESTS["qualification_request_golden.json"]["request_id"],
        "status": "complete",
        "history": [
            {
                "status": "queued",
                "at": "2026-10-11T12:00:00Z",
                "run_url": "https://github.com/PolicyEngine/policyengine-scorecard/actions/runs/1",
            }
        ],
    }
    with pytest.raises(jsonschema.ValidationError):
        ui.validate(status, ui.STATUS_SCHEMA_ID)
    status.update(receipt_sha256="a" * 64, receipt_commit="b" * 40)
    ui.validate(status, ui.STATUS_SCHEMA_ID)


def _reordered(value, rng):
    if isinstance(value, dict):
        items = list(value.items())
        rng.shuffle(items)
        return {k: _reordered(v, rng) for k, v in items}
    if isinstance(value, list):
        return [_reordered(v, rng) for v in value]
    return value


@settings(max_examples=60, deadline=None)
@given(st.integers(min_value=0, max_value=2**32))
def test_request_id_depends_on_content_not_key_order(seed):
    request = golden("qualification_request_golden.json")
    shuffled = _reordered(request, random.Random(seed))
    assert ui.request_id(shuffled) == ui.request_id(request)


@settings(max_examples=60, deadline=None)
@given(
    st.floats(allow_nan=False, allow_infinity=False),
    st.floats(allow_nan=False, allow_infinity=False),
)
def test_receipt_digest_changes_with_any_flagged_value(a, b):
    receipt = golden("replay_receipt_golden.json")
    left = copy.deepcopy(receipt)
    right = copy.deepcopy(receipt)
    left["diff"]["flagged_rows"][0]["head_gbp"] = a
    right["diff"]["flagged_rows"][0]["head_gbp"] = b
    same = ui.jcs_bytes(a) == ui.jcs_bytes(b)
    assert (ui.receipt_sha256(left) == ui.receipt_sha256(right)) == same
