"""Offline Modal transport checks; no Modal installation or country imports."""

import hashlib
import json
import sys
from contextlib import nullcontext
from pathlib import Path
from types import SimpleNamespace

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from pipeline import modal_uk_event as runner


@pytest.fixture
def inputs(tmp_path):
    artifact_bytes = b"certified fixture"
    cert = {
        "repo_id": "policyengine/populace-uk-private",
        "artifact": "populace_uk_2023.h5",
        "revision": "fixture-certified-revision",
        "sha256": hashlib.sha256(artifact_bytes).hexdigest(),
        "size_bytes": len(artifact_bytes),
        "compatible_model_packages": [
            {"name": "policyengine-uk", "specifier": "==2.89.2"}
        ],
    }
    audit = {"certified_identity": {**cert, "resolved_hf_commit": runner.HF_COMMIT}}
    for relative in runner.repository_files("autumn_budget_2024"):
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{}")
    (tmp_path / "data/uk/certified_bundle.json").write_text(json.dumps(cert))
    (tmp_path / "docs/uk_replay/OFFLINE_BUNDLE_AUDIT.json").write_text(
        json.dumps(audit)
    )
    requirements = "\n".join(
        f"{name}=={version}" for name, version in runner.ENGINE_PINS.items()
    )
    (tmp_path / "docs/uk_replay/requirements.txt").write_text(requirements)
    (tmp_path / "data/uk/events/autumn_budget_2024_measures.json").write_text(
        json.dumps(
            {
                "event_slug": "autumn_budget_2024",
                "calendar_years": list(range(2024, 2030)),
                "measures": [
                    {"measure_key": "autumn_budget_2024__private_school_vat_20pct"}
                ],
            }
        )
    )
    hf_cache = tmp_path / runner.HF_CACHE_RELATIVE
    repo = hf_cache / runner.HF_REPO_CACHE
    ref = repo / "refs" / cert["revision"]
    artifact = repo / "snapshots" / runner.HF_COMMIT / cert["artifact"]
    ref.parent.mkdir(parents=True)
    artifact.parent.mkdir(parents=True)
    ref.write_text(runner.HF_COMMIT)
    artifact.write_bytes(artifact_bytes)
    (repo / "token").write_text("must never be mounted")
    (repo / "refs/main").write_text("another revision")
    manifest, mounts = runner.input_manifest(
        "autumn_budget_2024", root=tmp_path, hf_cache=hf_cache
    )
    return tmp_path, manifest, mounts


def test_allowlist_mounts_only_pinned_inputs(inputs):
    root, manifest, mounts = inputs
    assert len(mounts) == len(runner.repository_files("autumn_budget_2024")) + 2
    assert all(
        not path.endswith("token") and not path.endswith("refs/main") for path in mounts
    )
    assert not any(".git" in Path(path).parts for path in mounts)
    assert sum(row["kind"] == "certified_artifact" for row in manifest["files"]) == 1
    runner.verify_inputs(manifest, root=root)


def test_upload_hash_gate_rejects_same_size_changed_h5_before_engine_import(inputs):
    root, manifest, mounts = inputs
    artifact = next(
        row["path"] for row in manifest["files"] if row["kind"] == "certified_artifact"
    )
    mounts[artifact].write_bytes(b"x" * mounts[artifact].stat().st_size)
    with pytest.raises(ValueError, match="differs from its digest"):
        runner.verify_inputs(manifest, root=root)


def test_allowlist_rejects_additional_input_even_with_valid_hash(inputs):
    root, manifest, _ = inputs
    extra = root / "unrelated.txt"
    extra.write_text("not a replay input")
    manifest["files"].append(
        {
            "path": "unrelated.txt",
            "sha256": runner.sha256_file(extra),
            "size_bytes": extra.stat().st_size,
        }
    )
    with pytest.raises(ValueError, match="exact allowlist"):
        runner.verify_inputs(manifest, root=root)


@pytest.mark.parametrize(
    "requirement",
    [
        "numpy>=2",
        "--extra-index-url=https://invalid",
        "policyengine==6.2.4",
        "numpy==2\nnumpy==2",
    ],
)
def test_requirements_are_exact_and_engine_compatible(requirement):
    text = "\n".join(
        f"{name}=={version}" for name, version in runner.ENGINE_PINS.items()
    )
    if requirement.startswith("policyengine=="):
        text = text.replace("policyengine==5.0.2", requirement)
    else:
        text += "\n" + requirement
    with pytest.raises(ValueError):
        runner.requirements_pins(text)


@pytest.mark.parametrize(
    "path", ["/tmp/out", "../out", "results/../out", "a//b", "a\\b", "./out"]
)
def test_reject_unnormalized_or_escaping_paths(path):
    with pytest.raises(ValueError):
        runner.relative_path(path)


def request():
    return runner.request_spec(
        "autumn_budget_2024",
        years=[2026],
        measures=["autumn_budget_2024__private_school_vat_20pct"],
        output_dir="results/uk/events/autumn_budget_2024",
        preflight_only=False,
    )


@pytest.mark.parametrize("years", [[2022], [2031], [2026, 2026]])
def test_request_limits_years_and_workers(years):
    with pytest.raises(ValueError):
        runner.request_spec(
            "autumn_budget_2024",
            years=years,
            measures=[],
            output_dir="results/uk/events/autumn_budget_2024",
            preflight_only=False,
        )
    assert request()["workers"] == 1
    assert (
        runner.RESOURCE_LIMITS["max_containers"]
        == runner.RESOURCE_LIMITS["max_inputs"]
        == 1
    )


def test_real_double_underscore_key_and_registry_selection(inputs):
    root, _, _ = inputs
    runner.validate_selection(request(), root=root)
    unknown = {**request(), "measures": ["autumn_budget_2024__unknown_measure"]}
    with pytest.raises(ValueError, match="absent from the event registry"):
        runner.validate_selection(unknown, root=root)
    outside = {**request(), "years": [2030]}
    with pytest.raises(ValueError, match="scoring grid"):
        runner.validate_selection(outside, root=root)


def response_for(payload):
    relative = payload["request"]["output_dir"] + "/private_school_vat_20pct_2026.json"
    artifact = b'{"announcement_effect": 12.0}\n'
    receipt = {
        "request": payload["request"],
        "request_sha256": runner.digest_bytes(
            runner.canonical_bytes(payload["request"])
        ),
        "input_manifest_sha256": runner.digest_bytes(
            runner.canonical_bytes(payload["inputs"])
        ),
        "files": {relative: runner.digest_bytes(artifact)},
    }
    files = {relative: {"bytes": artifact, "sha256": runner.digest_bytes(artifact)}}
    receipt_bytes = runner.canonical_bytes(receipt)
    files[payload["request"]["output_dir"] + "/MODAL_RECEIPT.json"] = {
        "bytes": receipt_bytes,
        "sha256": runner.digest_bytes(receipt_bytes),
    }
    return {"files": files}


def test_download_keeps_canonical_paths_in_receipts_but_writes_only_ignored_prefix(
    tmp_path,
):
    payload = {"request": request(), "inputs": {"verified": "fixture"}}
    response = response_for(payload)
    paths = runner.save_download(
        response, payload, ".venv-replay-checks/download", root=tmp_path
    )
    assert all(
        path.startswith(".venv-replay-checks/download/results/uk/events/")
        for path in paths
    )
    assert not (tmp_path / "results").exists()
    receipt_path = next(path for path in paths if path.endswith("MODAL_RECEIPT.json"))
    receipt = json.loads((tmp_path / receipt_path).read_bytes())
    assert next(iter(receipt["files"])).startswith(
        "results/uk/events/autumn_budget_2024/"
    )
    with pytest.raises(ValueError, match="overwrite"):
        runner.save_download(
            response, payload, ".venv-replay-checks/download", root=tmp_path
        )


def test_download_verifies_bytes_and_forbids_dataset_return(tmp_path):
    payload = {"request": request(), "inputs": {"verified": "fixture"}}
    response = response_for(payload)
    first = next(iter(response["files"].values()))
    first["bytes"] += b" "
    with pytest.raises(ValueError, match="SHA-256"):
        runner.save_download(
            response, payload, ".venv-replay-checks/download", root=tmp_path
        )
    response = response_for(payload)
    response["files"][request()["output_dir"] + "/populace_uk_2023.h5"] = {
        "bytes": b"dataset",
        "sha256": runner.digest_bytes(b"dataset"),
    }
    with pytest.raises(ValueError, match="outside"):
        runner.save_download(
            response, payload, ".venv-replay-checks/download", root=tmp_path
        )


def test_download_rejects_checks_symlink_outside_assigned_workspace(tmp_path):
    workspace = tmp_path / "workspace"
    external = tmp_path / "external"
    workspace.mkdir()
    external.mkdir()
    (workspace / ".venv-replay-checks").symlink_to(external, target_is_directory=True)
    with pytest.raises(ValueError, match="escapes the workspace"):
        runner.download_prefix(".venv-replay-checks/download", root=workspace)


def test_provider_serialization_requires_matching_python_minor(monkeypatch):
    with monkeypatch.context() as context:
        context.setattr(runner.sys, "version_info", (3, 14, 0))
        with pytest.raises(ValueError, match="Python 3.12 control interpreter"):
            runner.modal_function({})


def test_interrupted_modal_context_returns_130_without_downloading(
    monkeypatch, tmp_path, capsys
):
    class SuppressInterrupt:
        def __enter__(self):
            return self

        def __exit__(self, kind, value, traceback):
            return kind is KeyboardInterrupt

    def interrupted_remote(payload):
        raise KeyboardInterrupt

    monkeypatch.setattr(runner, "validate_selection", lambda request: None)
    monkeypatch.setattr(
        runner, "input_manifest", lambda event, hf_cache=None: ({"event": event}, {})
    )
    monkeypatch.setattr(runner, "download_prefix", lambda value: tmp_path / "download")
    slots = FakeDict()
    monkeypatch.setattr(
        runner,
        "modal_function",
        lambda mounts: (
            SimpleNamespace(
                enable_output=nullcontext,
                Dict=SimpleNamespace(from_name=lambda name, create_if_missing: slots),
            ),
            SimpleNamespace(run=SuppressInterrupt),
            SimpleNamespace(remote=interrupted_remote),
        ),
    )
    monkeypatch.setattr(
        runner,
        "save_download",
        lambda *args: pytest.fail("interrupted run must not download"),
    )
    assert runner.main(["--event", "autumn_budget_2024", "--execute"]) == 130
    assert "interrupted; no output downloaded" in capsys.readouterr().err
    # The interrupted run gave its simulation slot back.
    assert not [key for key in slots.data if key.startswith("slot-")]


def test_modal_factory_has_one_blocked_network_worker_and_explicit_uv_venv(
    monkeypatch, inputs
):
    _, _, mounts = inputs
    recorded = {"mounts": [], "commands": [], "env": {}}

    class Image:
        @staticmethod
        def debian_slim(**kwargs):
            assert kwargs == {"python_version": "3.12"}
            return Image()

        def pip_install(self, package):
            assert package == f"uv=={runner.UV_VERSION}"
            return self

        def add_local_file(self, source, destination, *, copy):
            recorded["mounts"].append((source, destination, copy))
            return self

        def run_commands(self, *commands):
            recorded["commands"].extend(commands)
            return self

        def env(self, values):
            recorded["env"] = values
            return self

    class App:
        def __init__(self, name, *, include_source):
            assert include_source is False

        def function(self, **kwargs):
            recorded["function"] = kwargs
            return lambda fn: fn

    def concurrent(**kwargs):
        recorded["concurrent"] = kwargs
        return lambda fn: fn

    fake = SimpleNamespace(Image=Image, App=App, concurrent=concurrent)
    monkeypatch.setitem(sys.modules, "modal", fake)
    monkeypatch.setattr(
        runner.importlib.metadata, "version", lambda name: runner.MODAL_VERSION
    )
    runner.modal_function(mounts)
    configuration = recorded["function"]
    assert configuration["cpu"] == (2, 2)
    assert configuration["memory"] == (32768, 32768)
    assert (
        configuration["timeout"] == runner.RESOURCE_LIMITS["timeout_seconds"] == 10800
    )
    assert configuration["max_containers"] == 1
    assert configuration["block_network"] is True
    assert configuration["include_source"] is False
    assert configuration["serialized"] is True
    assert recorded["concurrent"] == {"max_inputs": 1}
    assert recorded["commands"][0] == "uv python install 3.12.13"
    assert "uv venv --python 3.12.13 /opt/replay-venv" in recorded["commands"]
    assert any(
        "--requirements /opt/replay-requirements.txt" in command
        for command in recorded["commands"]
    )
    assert all(
        recorded["env"][key] == value for key, value in runner.OFFLINE_ENV.items()
    )
    assert all(
        "TOKEN" not in key or key == "HF_HUB_DISABLE_IMPLICIT_TOKEN"
        for key in recorded["env"]
    )
    assert len(recorded["mounts"]) == len(mounts) + 1  # build-time frozen requirements


class FakeDict:
    """A Modal Dict's put/get/pop, with put(skip_if_exists=True) atomic."""

    def __init__(self):
        self.data = {}

    def put(self, key, value, *, skip_if_exists=False):
        if skip_if_exists and key in self.data:
            return False
        self.data[key] = value
        return True

    def get(self, key, default=None):
        return self.data.get(key, default)

    def pop(self, key, default=None):
        return self.data.pop(key, default)


class Clock:
    def __init__(self):
        self.now = 1_000.0

    def __call__(self):
        return self.now


def test_two_slots_then_a_third_run_waits():
    store, clock = FakeDict(), Clock()
    a = runner.SimulationSlots(store, holder="a", clock=clock)
    b = runner.SimulationSlots(store, holder="b", clock=clock)
    c = runner.SimulationSlots(store, holder="c", clock=clock)
    assert {a.acquire(), b.acquire()} == {0, 1}
    sleeps = []

    def sleep(seconds):
        sleeps.append(seconds)
        clock.now += seconds

    with pytest.raises(TimeoutError):
        c.acquire(wait_seconds=60, poll_seconds=30, sleep=sleep)
    assert sleeps == [30, 30]
    c.release(0)  # not its slot: no effect
    assert store.get("slot-0")["holder"] in ("a", "b")
    a.release(0 if store.get("slot-0")["holder"] == "a" else 1)
    assert c.acquire(wait_seconds=0, sleep=sleep) in (0, 1)


def test_an_expired_slot_is_reclaimed_once():
    store, clock = FakeDict(), Clock()
    dead = runner.SimulationSlots(store, holder="dead", clock=clock, count=1)
    dead.acquire()
    clock.now += runner.LEASE_SECONDS + 1
    first = runner.SimulationSlots(store, holder="first", clock=clock, count=1)
    second = runner.SimulationSlots(store, holder="second", clock=clock, count=1)
    assert first._try(0) is True
    assert second._try(0) is False
    assert store.get("slot-0")["holder"] == "first"
    dead.release(0)  # the dead holder cannot free the new lease
    assert store.get("slot-0")["holder"] == "first"


def test_a_live_lease_outlasts_the_function_timeout():
    assert runner.LEASE_SECONDS > runner.RESOURCE_LIMITS["timeout_seconds"]


@settings(max_examples=300, deadline=None)
@given(
    st.lists(
        st.tuples(st.sampled_from("abcd"), st.sampled_from(["try", "release", "tick"])),
        max_size=40,
    )
)
def test_never_more_than_two_live_holders(operations):
    store, clock = FakeDict(), Clock()
    slots = {h: runner.SimulationSlots(store, holder=h, clock=clock) for h in "abcd"}
    held = {}
    for holder, action in operations:
        if action == "tick":
            clock.now += 600  # well inside a lease
        elif action == "try" and holder not in held:
            for slot in range(runner.SLOT_COUNT):
                if slots[holder]._try(slot):
                    held[holder] = slot
                    break
        elif action == "release" and holder in held:
            slots[holder].release(held.pop(holder))
        live = {
            value["holder"]
            for key, value in store.data.items()
            if key.startswith("slot-") and value["expires"] > clock.now
        }
        assert len(live) <= runner.SLOT_COUNT
        assert live == set(held)
