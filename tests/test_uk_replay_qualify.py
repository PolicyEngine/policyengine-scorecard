"""Qualification requests, the persistent queue, receipts and seals.

Engine-free: environments, simulations and downloads are not run; the
pieces that decide identity, rejection and sealing are exercised directly.
"""

import copy
import hashlib
import json
import shutil
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


@pytest.mark.parametrize("inert", [False, True])
def test_an_inert_construction_makes_the_receipt_incomplete_and_names_the_pair(
    tmp_path, monkeypatch, inert
):
    # Coordinator, 2026-10-11: identical worlds in an in-force year on the
    # candidate's engine must not let a receipt claim a complete corpus.
    import functools
    import shutil

    from test_uk_event_diff import EVENT, KEY, make_namespace, synthetic_record

    from pipeline import compute_uk_event as compute
    from pipeline import stage_uk_event as stage

    monkeypatch.setattr(compute, "ROOT", tmp_path)
    monkeypatch.setattr(stage, "manifest_variant", synthetic_record)
    make_namespace(
        tmp_path, "candidate", variant=CURRENT, identical=(2025,) if inert else ()
    )
    record = rv.get_variant(CURRENT)
    shutil.copytree(
        tmp_path / "ns" / "candidate", rv.namespace_root(record, root=tmp_path)
    )
    monkeypatch.setattr(
        qualify,
        "event_results",
        functools.partial(qualify.event_results, events=[EVENT]),
    )
    receipt = qualify.build_receipt(
        golden_request(),
        record=record,
        root=tmp_path,
        results_path="requests/x/results/",
    )
    event = receipt["corpus"]["events"][EVENT]
    assert receipt["integrity"]["failures"] == []
    if inert:
        assert receipt["integrity"]["status"] == "incomplete"
        assert event["full_supported_grid_complete"] is False
        assert event["inert_measure_years"] == [{"measure_key": KEY, "year": 2025}]
    else:
        assert receipt["integrity"]["status"] == "complete"
        assert event["inert_measure_years"] == []
    # The receipt W4 reads: sealed and valid, the run complete either way.
    sealed = qualify.seal(rv.namespace_root(record, root=tmp_path), receipt)
    interface.validate(sealed, interface.RECEIPT_SCHEMA_ID)
    assert sealed["status"] == "complete"


@pytest.mark.parametrize("premises_say_differ", [False, True])
def test_an_inert_pair_whose_premises_say_the_worlds_differ_fails(
    tmp_path, monkeypatch, premises_say_differ
):
    # Agreed with W4 (2026-10-15): an in-force pair that comes out inert
    # while its construction premises set the two worlds differently is a
    # broken construction (integrity failed, construction_inert); inertness
    # the premises predict stays incomplete. Found by 6.4.1, where the UC
    # health element reversal went inert on policyengine-uk 2.130.1.
    import functools
    import shutil

    from test_uk_event_diff import EVENT, KEY, make_namespace, synthetic_record

    from pipeline import compute_uk_event as compute
    from pipeline import stage_uk_event as stage

    monkeypatch.setattr(compute, "ROOT", tmp_path)
    monkeypatch.setattr(stage, "manifest_variant", synthetic_record)
    make_namespace(tmp_path, "candidate", variant=CURRENT, identical=(2025,))
    record = rv.get_variant(CURRENT)
    namespace = rv.namespace_root(record, root=tmp_path)
    shutil.copytree(tmp_path / "ns" / "candidate", namespace)
    path = "gov.example.amount"
    reform_value = 437.66 if premises_say_differ else 217.26
    premises = {
        "events": {
            EVENT: {
                "measures": {
                    KEY: {
                        "years": {
                            "2025": {
                                "in_force": True,
                                "paths": {
                                    path: {
                                        "baseline_world": 217.26,
                                        "reform_world": reform_value,
                                    }
                                },
                            }
                        }
                    }
                }
            }
        }
    }
    (namespace / "CONSTRUCTION_PREMISES.json").write_text(json.dumps(premises))
    monkeypatch.setattr(
        qualify,
        "event_results",
        functools.partial(qualify.event_results, events=[EVENT]),
    )
    receipt = qualify.build_receipt(
        golden_request(),
        record=record,
        root=tmp_path,
        results_path="requests/x/results/",
    )
    if premises_say_differ:
        assert receipt["status"] == "failed"
        assert receipt["integrity"]["status"] == "failed"
        (failure,) = receipt["integrity"]["failures"]
        assert failure["code"] == "construction_inert"
        assert (failure["event"], failure["measure_key"], failure["year"]) == (
            EVENT,
            KEY,
            2025,
        )
        assert path in failure["detail"]
        # Only W4's vendored failure fields, so old and new receipts validate.
        assert set(failure) == {"code", "detail", "event", "measure_key", "year"}
    else:
        assert receipt["integrity"]["status"] == "incomplete"
        assert receipt["integrity"]["failures"] == []
    sealed = qualify.seal(namespace, receipt)
    interface.validate(sealed, interface.RECEIPT_SCHEMA_ID)


def test_rejection_discards_a_supplied_record_and_cli_accepts_candidate(tmp_path):
    request = golden_request()
    record = copy.deepcopy(rv.get_variant(CURRENT))
    record["status"] = "candidate"
    document = rv.load_document()
    document["variants"][-1] = record
    variants_file = tmp_path / "variants.json"
    variants_file.write_bytes(qualify.canonical_bytes(document))
    request_file = tmp_path / "request.json"
    request_file.write_bytes(qualify.canonical_bytes(request))
    output = tmp_path / "receipt.json"
    assert (
        qualify.main(
            [
                "receipt",
                "--request",
                str(request_file),
                "--variant",
                CURRENT,
                "--variants-file",
                str(variants_file),
                "--rejection",
                "incompatible_pair: refused",
                "--results-path",
                "requests/x/results/",
                "--output",
                str(output),
            ]
        )
        == 0
    )
    receipt = json.loads(output.read_bytes())
    interface.validate(receipt, interface.RECEIPT_SCHEMA_ID)
    assert receipt["variant_id"] is None
    assert receipt["variant_identity_sha256"] is None
    assert receipt["execution"] is None
    assert receipt["integrity"] == {"status": "not_run", "failures": []}


def test_identity_without_event_outputs_has_a_valid_failed_receipt(tmp_path):
    record = rv.get_variant(CURRENT)
    built = qualify.build_receipt(
        golden_request(),
        record=record,
        root=tmp_path,
        failures=[{"code": "event_run_failed", "detail": "preflight failed"}],
        results_path="requests/x/results/",
    )
    assert built["corpus"] is None
    assert built["execution"] is not None
    assert built["variant_identity_sha256"] == record["identity_sha256"]
    namespace = rv.namespace_root(record, root=tmp_path)
    namespace.mkdir(parents=True)
    receipt = qualify.seal(namespace, built)
    interface.validate(receipt, interface.RECEIPT_SCHEMA_ID)
    assert receipt["status"] == "failed"


def test_corpus_passes_candidate_and_work_variants_without_resume(
    tmp_path, monkeypatch
):
    record = rv.get_variant(CURRENT)
    event = qualify.EVENTS[0]
    directory = rv.namespace_root(record, root=tmp_path) / event
    directory.mkdir(parents=True)
    (directory / "RUN_MANIFEST.json").write_text(
        json.dumps({"supported_years": [2024], "unsupported_years": []})
    )
    calls = []
    monkeypatch.setattr(
        qualify, "run", lambda command, *, cwd: calls.append((command, cwd))
    )
    work_variants = tmp_path / "variants.json"
    assert (
        qualify.run_corpus(record, work_variants, events=(event,), root=tmp_path) == []
    )
    compute = calls[0][0]
    assert "--allow-uncertified" in compute
    assert "--resume" not in compute
    staging = calls[1][0]
    assert staging[staging.index("--variants-file") + 1] == str(work_variants)
    assert all(cwd == tmp_path for _, cwd in calls)


def local_runner(tmp_path, variant_id=CURRENT):
    import shutil
    import subprocess

    root = tmp_path / "runner"
    root.mkdir()
    record = rv.get_variant(variant_id)
    for relative in (
        "data/uk/replay_variants.json",
        "data/uk/certified_bundle.json",
        record["requirements"]["path"],
        "results/uk/events/MODEL_DIAGNOSTICS.json",
    ):
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(qualify.ROOT / relative, target)
    namespace = rv.namespace_root(record, root=root)
    (namespace / qualify.EVENTS[0]).mkdir(parents=True)
    (namespace / qualify.EVENTS[0] / "RUN_MANIFEST.json").write_text(
        json.dumps({"variant_id": variant_id})
    )
    (namespace / qualify.EVENTS[0] / "COMPARISON.json").write_text(
        "committed comparison"
    )
    (namespace / "committed-only.txt").write_text(
        "old results must be deleted in the fresh checkout"
    )
    (namespace / rv.RECEIPT_NAME).write_text("committed receipt")
    diff = root / rv.REPLAY_RESULT_ROOT / "diffs" / f"{variant_id}__{variant_id}"
    diff.mkdir(parents=True)
    (diff / "committed-only.txt").write_text("old diff")
    for command in (
        ["git", "init", "-q"],
        ["git", "config", "user.email", "test@example.com"],
        ["git", "config", "user.name", "Test"],
        ["git", "add", "."],
        ["git", "commit", "-qm", "fixture"],
    ):
        subprocess.run(command, cwd=root, check=True)
    dataset = tmp_path / "dataset.h5"
    dataset.write_bytes(b"dataset fixture")
    request = golden_request()
    request["candidate"]["data"]["sha256"] = rv.sha256_file(dataset)
    request["candidate"]["data"]["size_bytes"] = dataset.stat().st_size
    return root, record, dataset, request


def stub_candidate(monkeypatch, root, record, *, no_outputs=False):
    import subprocess

    real_run = subprocess.run
    calls = []

    def prepare(request, venv, wheels, *, root):
        (wheels.parent / "INSTALL.json").write_bytes(
            qualify.canonical_bytes({"resolution": "certified_constraints"})
        )
        return {}

    def process(command, **kwargs):
        if "probe" not in command:
            return real_run(command, **kwargs)
        calls.append((command, kwargs["cwd"], kwargs["env"]))
        document = rv.load_document(root / "data/uk/replay_variants.json")
        Path(command[command.index("--variants-file") + 1]).write_bytes(
            qualify.canonical_bytes(document)
        )
        return subprocess.CompletedProcess(command, 0, record["variant_id"] + "\n", "")

    def run(command, *, cwd):
        if command[0] == "git":
            return real_run(command, cwd=cwd, check=True)
        calls.append((command, cwd, qualify.candidate_environment(cwd)))
        namespace = rv.namespace_root(record, root=cwd)
        if "corpus" in command:
            assert not (namespace / "committed-only.txt").exists()
            assert not (namespace / rv.RECEIPT_NAME).exists()
            if not no_outputs:
                for event in qualify.EVENTS:
                    directory = namespace / event
                    directory.mkdir(parents=True)
                    (directory / "RUN_MANIFEST.json").write_bytes(
                        qualify.canonical_bytes(
                            {
                                "registry_sha256": "a" * 64,
                                "supported_years": [2024],
                                "unsupported_years": [],
                                "artifacts": {},
                            }
                        )
                    )
                    (directory / "STAGING_MANIFEST.json").write_text(
                        '{"full_supported_grid_complete":true}'
                    )
                    (directory / "COMPARISON_PROVENANCE.json").write_text("{}")
            Path(command[command.index("--failures") + 1]).write_text("[]")
        elif "diff" in command:
            base = Path(command[command.index("--base") + 1])
            assert base == rv.namespace_root(record, root=root)
            assert (base / rv.RECEIPT_NAME).read_text() == "committed receipt"
            assert command[command.index("--base-root") + 1] == str(root)
            diff = Path(command[command.index("--output-dir") + 1])
            assert not (diff / "committed-only.txt").exists()
            diff.mkdir(parents=True)
            (diff / "DIFF.json").write_bytes(
                qualify.canonical_bytes(
                    {
                        "base": {"identity": {"variant_id": record["variant_id"]}},
                        "flag_counts": {
                            flag: 0
                            for flag in (
                                "numerical",
                                "structural",
                                "coverage",
                                "mapping",
                                "support",
                                "inertness",
                                "construction",
                            )
                        },
                        "rows": [],
                    }
                )
            )
        else:
            raise AssertionError(command)

    monkeypatch.setattr(qualify, "prepare", prepare)
    monkeypatch.setattr(qualify.subprocess, "run", process)
    monkeypatch.setattr(qualify, "run", run)
    return calls, real_run


def test_requalification_uses_fresh_results_and_leaves_runner_unchanged(
    tmp_path, monkeypatch
):
    root, record, dataset, request = local_runner(tmp_path)
    for name in ("HUGGING_FACE_TOKEN", "HF_TOKEN", "HUGGINGFACE_HUB_TOKEN"):
        monkeypatch.setenv(name, "secret")
    calls, real_run = stub_candidate(monkeypatch, root, record)
    state = tmp_path / "state"
    rid = qualify.request_id(request)
    target = state / "requests" / rid / "results"
    target.mkdir(parents=True)
    (target / "previous-attempt.txt").write_text("stale")
    work = tmp_path / "work"
    receipt = qualify.run_request(
        request, state, work, runner="test", dataset_file=dataset, root=root
    )
    interface.validate(receipt, interface.RECEIPT_SCHEMA_ID)
    assert receipt["status"] == "complete"
    assert receipt["diff"]["base_variant_id"] == CURRENT
    assert not (target / "previous-attempt.txt").exists()
    copied = target / record["result_root"]
    diff = target / rv.REPLAY_RESULT_ROOT / "diffs" / f"{CURRENT}__{CURRENT}"
    assert qualify.verify_sealed(copied, diff_dir=diff) == []
    assert (
        "INSTALL.json"
        in json.loads((copied / qualify.MANIFEST_NAME).read_bytes())["files"]
    )
    assert all(cwd == work / "checkout" for _, cwd, _ in calls)
    assert all(
        not any(
            name in env
            for name in ("HUGGING_FACE_TOKEN", "HF_TOKEN", "HUGGINGFACE_HUB_TOKEN")
        )
        for _, _, env in calls
    )
    assert (
        real_run(
            ["git", "status", "--porcelain"],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        == ""
    )
    assert (
        rv.namespace_root(record, root=root) / rv.RECEIPT_NAME
    ).read_text() == "committed receipt"


@pytest.mark.parametrize(
    "crash_step", ["build_receipt", "seal", "copytree", "event_results"]
)
def test_receipt_step_crashes_produce_minimal_valid_failed_receipts(
    tmp_path, monkeypatch, crash_step
):
    root, record, dataset, request = local_runner(tmp_path)
    stub_candidate(monkeypatch, root, record)

    def crash(*args, **kwargs):
        raise RuntimeError("first line\nprivate traceback details")

    if crash_step == "copytree":
        monkeypatch.setattr(qualify.shutil, "copytree", crash)
    else:
        monkeypatch.setattr(qualify, crash_step, crash)
    state = tmp_path / "state"
    receipt = qualify.run_request(
        request,
        state,
        tmp_path / "work",
        runner="test",
        dataset_file=dataset,
        root=root,
    )
    interface.validate(receipt, interface.RECEIPT_SCHEMA_ID)
    assert receipt["status"] == "failed"
    assert receipt["variant_id"] == CURRENT
    assert receipt["corpus"] is None
    assert receipt["integrity"]["failures"] == [
        {"code": "receipt_step_failed", "detail": "RuntimeError: first line"}
    ]
    assert not (state / "requests" / qualify.request_id(request) / "results").exists()


def test_run_request_with_identity_and_no_outputs_still_seals_failure(
    tmp_path, monkeypatch
):
    root, record, dataset, request = local_runner(tmp_path)
    stub_candidate(monkeypatch, root, record, no_outputs=True)
    receipt = qualify.run_request(
        request,
        tmp_path / "state",
        tmp_path / "work",
        runner="test",
        dataset_file=dataset,
        root=root,
    )
    interface.validate(receipt, interface.RECEIPT_SCHEMA_ID)
    assert receipt["status"] == "failed" and receipt["corpus"] is None
    assert receipt["execution"] is not None
    assert any(
        f["code"] == "event_outputs_missing" for f in receipt["integrity"]["failures"]
    )


@pytest.mark.parametrize(
    "missing", ["REPLAY_RECEIPT.json", "NAMESPACE_MANIFEST.json", "both"]
)
def test_verify_sealed_checks_expected_namespace_with_missing_seal(
    tmp_path, monkeypatch, missing, capsys
):
    namespace, _, _ = sealed_namespace(tmp_path)
    if missing in ("REPLAY_RECEIPT.json", "both"):
        (namespace / rv.RECEIPT_NAME).unlink()
    if missing in ("NAMESPACE_MANIFEST.json", "both"):
        (namespace / qualify.MANIFEST_NAME).unlink()
    monkeypatch.setattr(
        rv,
        "load_document",
        lambda: {
            "variants": [{"layout": "replay_namespace", "result_root": str(namespace)}]
        },
    )
    assert qualify.main(["verify-sealed"]) == 1
    assert "not sealed" in capsys.readouterr().out


def test_a_namespace_must_be_sealed_once_it_holds_replay_results(
    tmp_path, monkeypatch, capsys
):
    # Review of 176e974: premises, diagnostics and an empty summary committed
    # before a variant's replay are not results; one event's run manifest is.
    namespace = tmp_path / "ns"
    namespace.mkdir()
    (namespace / "CONSTRUCTION_PREMISES.json").write_text("{}")
    (namespace / "SUMMARY.md").write_text("# summary\n")
    monkeypatch.setattr(
        rv,
        "load_document",
        lambda: {
            "variants": [{"layout": "replay_namespace", "result_root": str(namespace)}]
        },
    )
    assert qualify.main(["verify-sealed"]) == 0
    (namespace / "an_event").mkdir()
    (namespace / "an_event" / "RUN_MANIFEST.json").write_text("{}")
    assert qualify.main(["verify-sealed"]) == 1
    assert "not sealed" in capsys.readouterr().out


def test_a_once_sealed_namespace_stays_checked_after_its_events_go(
    tmp_path, monkeypatch, capsys
):
    # Review of 2896610: deleting every event directory but keeping the
    # receipt must not pass.
    namespace, _, _ = sealed_namespace(tmp_path)
    shutil.rmtree(namespace / "event")
    monkeypatch.setattr(
        rv,
        "load_document",
        lambda: {
            "variants": [{"layout": "replay_namespace", "result_root": str(namespace)}]
        },
    )
    assert qualify.main(["verify-sealed"]) == 1
    capsys.readouterr()


def test_the_committed_namespaces_pass_the_seal_check():
    # CI's "Replay namespaces regenerate and seals hold" step, on this tree.
    assert qualify.main(["verify-sealed"]) == 0


@pytest.mark.parametrize("code", [None, "artifact_hash_mismatch", "data_access_failed"])
def test_dataset_fetch_cli_hands_file_or_rejection_to_run_request(
    tmp_path, monkeypatch, code
):
    request_path = tmp_path / "request.json"
    request_path.write_bytes(qualify.canonical_bytes(golden_request()))
    source = tmp_path / "source.h5"
    source.write_bytes(b"verified dataset")

    def fetch(request):
        if code:
            raise qualify.Rejected(code, "fetch detail")
        return source

    monkeypatch.setattr(qualify, "fetch_dataset", fetch)
    result = tmp_path / "fetch-result.json"
    output = tmp_path / "output.h5"
    assert (
        qualify.main(
            [
                "fetch-dataset",
                "--request",
                str(request_path),
                "--output",
                str(output),
                "--result-file",
                str(result),
            ]
        )
        == 0
    )
    fetched = json.loads(result.read_bytes())
    if code:
        assert fetched == {
            "dataset_file": None,
            "rejection": {"code": code, "detail": "fetch detail"},
        }
        receipt = qualify.run_request(
            golden_request(),
            tmp_path / "state",
            tmp_path / "work",
            runner="test",
            dataset_file=output,
            dataset_result=result,
        )
        interface.validate(receipt, interface.RECEIPT_SCHEMA_ID)
        assert receipt["rejection"]["code"] == code
    else:
        assert output.read_bytes() == source.read_bytes()
        assert fetched == {"dataset_file": str(output), "rejection": None}


def test_run_request_cli_writes_outcome_file(tmp_path, monkeypatch):
    request = tmp_path / "request.json"
    request.write_bytes(qualify.canonical_bytes(golden_request()))
    receipt = qualify.minimal_failed_receipt(
        qualify.request_id(golden_request()),
        record=None,
        results_path="requests/x/results/",
        detail="crash",
    )
    monkeypatch.setattr(qualify, "run_request", lambda *args, **kwargs: receipt)
    outcome = tmp_path / "outcome.json"
    assert (
        qualify.main(
            [
                "run-request",
                "--request",
                str(request),
                "--state-dir",
                str(tmp_path / "state"),
                "--work",
                str(tmp_path / "work"),
                "--result-file",
                str(outcome),
            ]
        )
        == 0
    )
    assert json.loads(outcome.read_bytes()) == {
        "status": "failed",
        "receipt_sha256": receipt["receipt_sha256"],
    }


@pytest.mark.parametrize(
    "resolution", ["exact_requirements", "certified_constraints", "free_resolution"]
)
def test_prepare_records_resolution_mode(tmp_path, monkeypatch, resolution):
    import subprocess

    request = golden_request()
    if resolution != "exact_requirements":
        request["candidate"]["policyengine_uk"]["wheel_sha256"] = "0" * 64
    attempts = []

    def run(command, *, cwd):
        if "-c" in command and resolution == "free_resolution":
            raise subprocess.CalledProcessError(1, command)
        attempts.append(command)

    monkeypatch.setattr(qualify, "run", run)
    monkeypatch.setattr(
        qualify.subprocess,
        "run",
        lambda command, **kwargs: subprocess.CompletedProcess(command, 0, "", ""),
    )
    monkeypatch.setattr(qualify, "verify_wheels", lambda *args: {})
    qualify.prepare(request, tmp_path / "venv", tmp_path / "wheels")
    installation = json.loads((tmp_path / "INSTALL.json").read_bytes())
    assert installation["resolution"] == resolution
    assert installation["certified_variant_id"] == CURRENT
    assert len(installation["environment_sha256"]) == 64
    assert attempts


def test_missing_pypi_wheel_is_artifact_hash_rejection(tmp_path, monkeypatch):
    import subprocess

    monkeypatch.setattr(qualify, "run", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        qualify.subprocess,
        "run",
        lambda command, **kwargs: subprocess.CompletedProcess(
            command,
            1,
            "",
            "ERROR: No matching distribution found for policyengine-uk==0.0.1",
        ),
    )
    with pytest.raises(qualify.Rejected) as raised:
        qualify.prepare(golden_request(), tmp_path / "venv", tmp_path / "wheels")
    assert raised.value.code == "artifact_hash_mismatch"


def test_nested_receipt_named_files_are_bound_and_sealed_results_cannot_be_resealed(
    tmp_path,
):
    namespace, diff, sealed = sealed_namespace(tmp_path)
    original_manifest = (namespace / qualify.MANIFEST_NAME).read_bytes()
    original_receipt = (namespace / rv.RECEIPT_NAME).read_bytes()
    with pytest.raises(rv.VariantError, match="sealed"):
        qualify.seal(namespace, sealed, diff_dir=diff)
    assert (namespace / qualify.MANIFEST_NAME).read_bytes() == original_manifest
    assert (namespace / rv.RECEIPT_NAME).read_bytes() == original_receipt
    for name in (rv.RECEIPT_NAME, qualify.MANIFEST_NAME):
        nested = namespace / "event" / name
        nested.write_text("added file")
        assert any(
            "files differ" in problem
            for problem in qualify.verify_sealed(namespace, diff_dir=diff)
        )
        nested.unlink()


def test_corpus_refuses_a_sealed_namespace_before_any_subprocess(tmp_path, monkeypatch):
    record = copy.deepcopy(rv.get_variant(CURRENT))
    namespace, _, _ = sealed_namespace(tmp_path)
    record["result_root"] = str(namespace)
    monkeypatch.setattr(
        qualify,
        "run",
        lambda *args, **kwargs: pytest.fail("must not start a subprocess"),
    )
    with pytest.raises(rv.VariantError, match="sealed"):
        qualify.run_corpus(record, tmp_path / "variants.json", root=tmp_path)


def test_legacy_requalification_preserves_original_diagnostics(tmp_path, monkeypatch):
    legacy_id = rv.load_document()["default_variant"]
    root, record, dataset, request = local_runner(tmp_path, variant_id=legacy_id)
    _, real_run = stub_candidate(monkeypatch, root, record)
    receipt = qualify.run_request(
        request,
        tmp_path / "state",
        tmp_path / "work",
        runner="test",
        dataset_file=dataset,
        root=root,
    )
    interface.validate(receipt, interface.RECEIPT_SCHEMA_ID)
    assert receipt["status"] == "complete"
    assert receipt["variant_id"] == legacy_id
    diagnostics = root / "results/uk/events/MODEL_DIAGNOSTICS.json"
    assert (tmp_path / "work/diagnostics.json").read_bytes() == diagnostics.read_bytes()
    assert (
        real_run(
            ["git", "status", "--porcelain"],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        == ""
    )


def test_diff_reads_base_and_head_artifacts_from_their_own_checkouts(
    tmp_path, monkeypatch
):
    from test_uk_event_diff import make_namespace, synthetic_record
    from pipeline import compute_uk_event as compute
    from pipeline import diff_uk_event_runs as diff
    from pipeline import stage_uk_event as stage

    base_root = tmp_path / "runner"
    head_root = tmp_path / "checkout"
    work_variants = tmp_path / "work" / "variants.json"
    # The synthetic sides name synthetic datasets, so the variant lookup is
    # stood in (as in test_uk_event_diff); what is checked here is that each
    # side is looked up in its own checkout's document.
    looked_up = []

    def record(manifest, registry, *, variants_path):
        looked_up.append(Path(variants_path))
        return synthetic_record(manifest, registry, variants_path=variants_path)

    monkeypatch.setattr(stage, "manifest_variant", record)
    monkeypatch.setattr(compute, "ROOT", base_root)
    base = make_namespace(base_root, "pair")
    monkeypatch.setattr(compute, "ROOT", head_root)
    head = make_namespace(
        head_root,
        "pair",
        effects={
            2024: {"income_tax": 200e6, "universal_credit": -60e6},
            2025: {"income_tax": 220e6, "universal_credit": -66e6},
        },
    )
    monkeypatch.setattr(qualify, "ROOT", head_root)
    monkeypatch.setattr(diff, "ROOT", head_root)
    output = head_root / "diff"
    command = [
        "diff",
        "--base",
        str(base["root"]),
        "--base-root",
        str(base_root),
        "--head",
        str(head["root"]),
        "--variants-file",
        str(work_variants),
        "--output-dir",
        str(output),
    ]
    looked_up.clear()
    assert qualify.main(command) == 0
    assert set(looked_up) == {
        base_root / "data" / "uk" / "replay_variants.json",
        work_variants.resolve(),
    }
    result = json.loads((output / "DIFF.json").read_bytes())
    assert result["flag_counts"]["numerical"] > 0
    row = next(
        row
        for row in result["rows"]
        if row["level"] == "head" and row["key"] == "income_tax" and row["year"] == 2024
    )
    assert row["base_gbp"] == -100e6 and row["head_gbp"] == -200e6
    assert result["base"]["root"] == result["head"]["root"] == "ns/pair"
    artifact = next((base["root"] / "test_event").glob("test_event__*.json"))
    artifact.write_text("tampered committed artifact")
    with pytest.raises(diff.DiffError):
        qualify.main(command)
