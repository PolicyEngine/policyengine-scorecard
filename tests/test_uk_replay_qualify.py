"""Qualification requests, the persistent queue, receipts and seals.

Engine-free: environments, simulations and downloads are not run; the
pieces that decide identity, rejection and sealing are exercised directly.
"""

import copy
import hashlib
import json
from pathlib import Path

import jsonschema
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from pipeline import uk_replay_interface as interface
from pipeline import uk_replay_qualify as qualify
from pipeline import uk_replay_queue as queue
from pipeline import uk_replay_variants as rv

FIXTURES = Path(__file__).parent / "fixtures" / "uk_replay"
CURRENT = "pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0"
RUN = "https://github.com/PolicyEngine/policyengine-scorecard/actions/runs/1"


def golden_request():
    return json.loads((FIXTURES / "qualification_request_golden.json").read_text())


# --- the queue --------------------------------------------------------------------


def test_enqueue_is_idempotent_and_records_the_request(tmp_path):
    request = golden_request()
    rid, status = queue.enqueue(
        tmp_path, request, run_url=RUN, now="2026-10-11T12:00:00Z"
    )
    assert status == "queued" and rid == interface.request_id(request)
    stored = json.loads((tmp_path / "requests" / rid / "REQUEST.json").read_text())
    assert stored == request
    again = queue.enqueue(tmp_path, request, run_url=RUN, now="2026-10-11T13:00:00Z")
    assert again == (rid, "queued")
    status_doc = queue.read_status(tmp_path, rid)
    assert len(status_doc["history"]) == 1


def test_an_invalid_request_is_still_recorded_for_its_rejection(tmp_path):
    request = {"schema": "nonsense"}
    rid, status = queue.enqueue(
        tmp_path, request, run_url=RUN, now="2026-10-11T12:00:00Z"
    )
    assert rid == interface.jcs_sha256(request) and status == "queued"


def test_status_transitions_and_terminal_states(tmp_path):
    rid, _ = queue.enqueue(
        tmp_path, golden_request(), run_url=RUN, now="2026-10-11T12:00:00Z"
    )
    queue.set_status(tmp_path, rid, "running", run_url=RUN, now="2026-10-11T12:01:00Z")
    with pytest.raises(ValueError, match="terminal status names its receipt"):
        queue.set_status(
            tmp_path, rid, "complete", run_url=RUN, now="2026-10-11T12:30:00Z"
        )
    done = queue.set_status(
        tmp_path,
        rid,
        "complete",
        run_url=RUN,
        now="2026-10-11T12:30:00Z",
        receipt_sha256="a" * 64,
        receipt_commit="b" * 40,
    )
    assert [h["status"] for h in done["history"]] == ["queued", "running", "complete"]
    interface.validate(done, interface.STATUS_SCHEMA_ID)
    with pytest.raises(ValueError, match="terminal states are final"):
        queue.set_status(
            tmp_path, rid, "running", run_url=RUN, now="2026-10-11T13:00:00Z"
        )


def test_pending_is_oldest_first_and_recovers_lost_runs(tmp_path):
    first = golden_request()
    second = copy.deepcopy(first)
    second["attempt"] = 2
    third = copy.deepcopy(first)
    third["attempt"] = 3
    a, _ = queue.enqueue(tmp_path, second, run_url=RUN, now="2026-10-11T10:00:00Z")
    b, _ = queue.enqueue(tmp_path, first, run_url=RUN, now="2026-10-11T09:00:00Z")
    c, _ = queue.enqueue(tmp_path, third, run_url=RUN, now="2026-10-11T11:00:00Z")
    queue.set_status(tmp_path, c, "running", run_url=RUN, now="2026-10-11T11:05:00Z")
    assert queue.pending(tmp_path, now="2026-10-11T12:00:00Z") == [b, a]
    # A running request whose job vanished is retried after the stale bound.
    assert queue.pending(tmp_path, now="2026-10-11T18:06:00Z") == [b, a, c]


def test_request_ids_must_be_digests(tmp_path):
    with pytest.raises(ValueError):
        queue.request_dir(tmp_path, "../escape")


# --- requests to environments -----------------------------------------------------


def test_golden_candidate_matches_the_committed_certified_pair():
    document = rv.load_document()
    match = qualify.matching_certified(golden_request(), document)
    assert match is not None and match["variant_id"] == CURRENT
    other = golden_request()
    other["candidate"]["policyengine_uk"]["wheel_sha256"] = "0" * 64
    assert qualify.matching_certified(other, document) is None
    assert qualify.latest_certified(document)["variant_id"] == CURRENT


def test_install_uses_exact_pins_for_a_certified_pair_and_constraints_otherwise(
    tmp_path,
):
    wheels = tmp_path / "wheels"
    wheels.mkdir()
    (wheels / "policyengine_uk-2.125.1-py3-none-any.whl").write_bytes(b"x")
    request = golden_request()
    env = tmp_path / "env.txt"
    exact = qualify.install_command(
        request, tmp_path / "venv", wheels, environment=env, exact=True
    )
    assert exact[exact.index(str(env)) - 1] == "-r"
    loose = qualify.install_command(
        request, tmp_path / "venv", wheels, environment=env, exact=False
    )
    assert loose[loose.index(str(env)) - 1] == "-c"
    assert any(
        part.startswith("policyengine @ git+")
        and part.endswith(
            request["candidate"]["policyengine"]["source"]["git"]["commit"]
        )
        for part in exact
    )
    lines = qualify.environment_lines(rv.get_variant(CURRENT))
    assert lines and not any(line.split("==")[0] in rv.PACKAGES for line in lines)


def test_downloaded_wheels_must_match_the_request(tmp_path):
    request = golden_request()
    wheels = tmp_path / "wheels"
    wheels.mkdir()
    (wheels / "policyengine_uk-2.125.1-py3-none-any.whl").write_bytes(b"not the wheel")
    (wheels / "policyengine_core-3.33.0-py3-none-any.whl").write_bytes(b"core")
    with pytest.raises(qualify.Rejected) as raised:
        qualify.verify_wheels(request, wheels)
    assert raised.value.code == "artifact_hash_mismatch"
    request["candidate"]["policyengine_uk"]["wheel_sha256"] = hashlib.sha256(
        b"not the wheel"
    ).hexdigest()
    request["candidate"]["policyengine_core"]["wheel_sha256"] = hashlib.sha256(
        b"core"
    ).hexdigest()
    digests = qualify.verify_wheels(request, wheels)
    assert set(digests) == {"policyengine_uk", "policyengine_core"}


def test_schema_failures_are_rejections():
    with pytest.raises(qualify.Rejected) as raised:
        qualify.request_id({"schema": "x"})
    assert raised.value.code == "schema_invalid"


def test_freeze_normalisation():
    versions = {
        "policyengine": "6.2.6",
        "policyengine-uk": "2.125.1",
        "policyengine-core": "3.33.0",
    }
    freeze = "\n".join(
        [
            "numpy==2.5.4",
            "policyengine @ git+https://github.com/PolicyEngine/policyengine.py@"
            + "a" * 40,
            "policyengine-core @ file:///tmp/wheels/policyengine_core-3.33.0-py3-none-any.whl",
            "policyengine-uk==2.125.1",
        ]
    )
    text = rv.normalized_freeze(freeze, versions)
    assert rv.requirements_pins(text) == {
        "numpy": "2.5.4",
        "policyengine": "6.2.6",
        "policyengine-core": "3.33.0",
        "policyengine-uk": "2.125.1",
    }
    assert (
        "# policyengine-core installed from policyengine_core-3.33.0-py3-none-any.whl"
        in text
    )
    with pytest.raises(rv.VariantError, match="not an exact pin"):
        rv.normalized_freeze(freeze + "\nother @ file:///x.whl", versions)
    with pytest.raises(rv.VariantError, match="lacks"):
        rv.normalized_freeze("numpy==2.5.4", versions)


def test_variant_ids_take_a_digest_suffix_only_on_a_collision():
    identity = rv.get_variant(CURRENT)["identity"]
    digest = rv.identity_sha256(identity)
    slug = rv.variant_slug(identity)
    assert rv.variant_id_for(identity, {}) == slug
    assert rv.variant_id_for(identity, {slug: digest}) == slug
    assert rv.variant_id_for(identity, {slug: "f" * 64}) == f"{slug}--{digest[:10]}"


def test_every_pinned_distribution_must_be_installed_at_its_version():
    pins = {"numpy": "2.5.4", "pandas": "3.0.6"}
    assert (
        rv.environment_mismatches(
            pins, {"distributions": {"numpy": "2.5.4", "pandas": "3.0.6", "extra": "1"}}
        )
        == []
    )
    assert rv.environment_mismatches(
        pins, {"distributions": {"numpy": "2.5.5", "pandas": "3.0.6"}}
    )
    assert rv.environment_mismatches(pins, {"distributions": {"numpy": "2.5.4"}})


# --- receipts and seals -------------------------------------------------------------


def test_rejected_and_preidentity_failed_receipts_validate():
    request = golden_request()
    rejected = interface.seal_receipt(
        qualify.build_receipt(
            request,
            record=None,
            rejection=qualify.Rejected("data_access_failed", "401"),
            results_path="requests/x/results/",
        )
    )
    interface.validate(rejected, interface.RECEIPT_SCHEMA_ID)
    assert rejected["status"] == "rejected" and rejected["corpus"] is None
    failed = interface.seal_receipt(
        qualify.build_receipt(
            request,
            record=None,
            failures=[
                {"code": "qualification_step_failed", "detail": "pip download: exit 1"}
            ],
            results_path="requests/x/results/",
        )
    )
    interface.validate(failed, interface.RECEIPT_SCHEMA_ID)
    assert failed["status"] == "failed" and failed["integrity"]["status"] == "failed"
    assert failed["execution"] is None


def test_a_complete_receipt_needs_its_execution():
    receipt = interface.seal_receipt(
        {
            **json.loads((FIXTURES / "replay_receipt_golden.json").read_text()),
            "execution": None,
        }
    )
    with pytest.raises(jsonschema.ValidationError):
        interface.validate(receipt, interface.RECEIPT_SCHEMA_ID)


def sealed_namespace(tmp_path):
    namespace = tmp_path / "ns"
    (namespace / "event").mkdir(parents=True)
    (namespace / "event" / "RUN_MANIFEST.json").write_text("{}")
    (namespace / "SUMMARY.md").write_text("# summary\n")
    diff = tmp_path / "diff"
    (diff / "packets").mkdir(parents=True)
    (diff / "DIFF.json").write_text("{}")
    golden = json.loads((FIXTURES / "replay_receipt_golden.json").read_text())
    receipt = {k: v for k, v in golden.items() if k != "receipt_sha256"}
    receipt["results"] = {k: v for k, v in receipt["results"].items() if k != "commit"}
    sealed = qualify.seal(namespace, receipt, diff_dir=diff)
    return namespace, diff, sealed


def test_seal_binds_every_file_and_detects_tampering(tmp_path):
    namespace, diff, sealed = sealed_namespace(tmp_path)
    assert qualify.verify_sealed(namespace, diff_dir=diff) == []
    manifest = json.loads((namespace / qualify.MANIFEST_NAME).read_text())
    assert set(manifest["files"]) == {"event/RUN_MANIFEST.json", "SUMMARY.md"}
    assert (
        sealed["results"]["manifest_sha256"]
        == hashlib.sha256((namespace / qualify.MANIFEST_NAME).read_bytes()).hexdigest()
    )
    (namespace / "SUMMARY.md").write_text("# edited\n")
    assert qualify.verify_sealed(namespace, diff_dir=diff)


def test_seal_detects_added_files_and_diff_edits(tmp_path):
    namespace, diff, _ = sealed_namespace(tmp_path)
    (namespace / "event" / "extra.json").write_text("{}")
    assert any(
        "files differ" in p for p in qualify.verify_sealed(namespace, diff_dir=diff)
    )
    (namespace / "event" / "extra.json").unlink()
    (diff / "DIFF.json").write_text("{ }")
    assert any("diff" in p for p in qualify.verify_sealed(namespace, diff_dir=diff))


def test_sealed_namespaces_refuse_writes(tmp_path):
    namespace, _, _ = sealed_namespace(tmp_path)
    with pytest.raises(rv.VariantError, match="sealed"):
        rv.assert_not_sealed(namespace / "event", root=tmp_path)


@settings(max_examples=50, deadline=None)
@given(st.lists(st.sampled_from(["queued", "running"]), min_size=1, max_size=5))
def test_pending_never_returns_terminal_requests(tmp_path_factory, statuses):
    state = tmp_path_factory.mktemp("state")
    ids = []
    for attempt, status in enumerate(statuses, start=1):
        request = golden_request()
        request["attempt"] = attempt
        rid, _ = queue.enqueue(
            state, request, run_url=RUN, now=f"2026-10-11T0{attempt}:00:00Z"
        )
        if status == "running":
            queue.set_status(
                state, rid, "running", run_url=RUN, now=f"2026-10-11T0{attempt}:10:00Z"
            )
        ids.append(rid)
    finished = ids[0]
    if queue.read_status(state, finished)["status"] == "queued":
        queue.set_status(
            state, finished, "running", run_url=RUN, now="2026-10-11T09:00:00Z"
        )
    queue.set_status(
        state,
        finished,
        "failed",
        run_url=RUN,
        now="2026-10-11T09:30:00Z",
        receipt_sha256="c" * 64,
        receipt_commit="d" * 40,
    )
    later = queue.pending(state, now="2026-10-12T09:00:00Z")
    assert finished not in later
    assert set(later) == set(ids[1:])
