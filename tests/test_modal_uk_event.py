"""Offline Modal transport checks; no Modal installation or country imports."""

import hashlib
import itertools
import json
import subprocess  # noqa: F401 - patched in the factory test
import sys
import time
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

    def interrupted_remote(payload, lease_expires):
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
            SimpleNamespace(remote=time.time),
        ),
    )
    monkeypatch.setattr(
        runner,
        "save_download",
        lambda *args: pytest.fail("interrupted run must not download"),
    )
    assert runner.main(["--event", "autumn_budget_2024", "--execute"]) == 130
    assert "interrupted; no output downloaded" in capsys.readouterr().err
    # The interrupted run's slot frees once Modal has had time to stop it.
    claims = [v for k, v in slots.data.items() if k.startswith("claim-")]
    assert claims and all(claim["released"] is False for claim in claims)
    assert all(
        claim["expires"] <= time.time() + runner.INTERRUPT_GRACE_SECONDS + 1
        for claim in claims
    )


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
            recorded.setdefault("functions", []).append(kwargs)
            return lambda fn: fn

    def concurrent(**kwargs):
        recorded["concurrent"] = kwargs
        return lambda fn: fn

    fake = SimpleNamespace(Image=Image, App=App, concurrent=concurrent)
    monkeypatch.setitem(sys.modules, "modal", fake)
    monkeypatch.setattr(
        runner.importlib.metadata, "version", lambda name: runner.MODAL_VERSION
    )
    _, _, replay, modal_time = runner.modal_function(mounts)
    assert abs(modal_time() - time.time()) < 5
    # The remote refuses to start unless its whole timeout fits in the lease.
    monkeypatch.setattr(
        sys.modules["subprocess"],
        "run",
        lambda *args, **kwargs: pytest.fail("a short lease must not start a run"),
    )
    timeout = runner.RESOURCE_LIMITS["timeout_seconds"]
    for slack in (-60, runner.GUARD_MARGIN_SECONDS - 60):
        with pytest.raises(RuntimeError, match="lease does not cover"):
            replay({"request": {}}, time.time() + timeout + slack)
    configuration, clock_configuration = recorded["functions"]
    assert clock_configuration["block_network"] is True
    assert clock_configuration["timeout"] == 60
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
    """A Modal Dict's get/put, with put(skip_if_exists=True) atomic and, given
    a clock, entries expiring after 7 days without a read or write (as
    modal/dict.py documents)."""

    TTL = 7 * 24 * 60 * 60

    def __init__(self, clock=None):
        self.data, self.touched, self.clock = {}, {}, clock

    def _expire(self):
        if self.clock is None:
            return
        for key in [k for k, t in self.touched.items() if self.clock() - t > self.TTL]:
            del self.data[key], self.touched[key]

    def _touch(self, key):
        if self.clock is not None and key in self.data:
            self.touched[key] = self.clock()

    def put(self, key, value, *, skip_if_exists=False):
        self._expire()
        if skip_if_exists and key in self.data:
            self._touch(key)
            return False
        self.data[key] = value
        self._touch(key)
        return True

    def get(self, key, default=None):
        self._expire()
        self._touch(key)
        return self.data.get(key, default)


class Clock:
    """True (Modal) time. Starts mid-morning, well inside a day."""

    def __init__(self, now=10 * 3600.0):
        self.now = now

    def __call__(self):
        return self.now


DAY = runner.EPOCH_SECONDS
TIMEOUT = runner.RESOURCE_LIMITS["timeout_seconds"]
MARGIN = runner.CLOCK_MARGIN_SECONDS


def slots_for(store, clock, holder, *, offset=0.0, **kwargs):
    """A holder whose own clock reads true time plus ``offset``."""
    return runner.SimulationSlots(
        store, holder=holder, clock=lambda: clock() + offset, **kwargs
    )


def run_steps(store, steps, *, limit=None):
    """Drive a protocol generator for at most ``limit`` Dict calls; return
    (finished, value)."""
    calls = 0
    try:
        call = next(steps)
        while True:
            if limit is not None and calls == limit:
                return False, None
            calls += 1
            if call[0] == "get":
                result = store.get(call[1])
            else:
                result = store.put(call[1], call[2], skip_if_exists=call[3])
            call = steps.send(result)
    except StopIteration as done:
        return True, done.value


def holders_of(store, clock):
    """Each slot's live claim in today's chain, by true time."""
    held = {}
    today = int(clock() // DAY)
    for slot in range(runner.SLOT_COUNT):
        generation, newest = -1, None
        while True:
            claim = store.data.get(f"claim-{slot}-{today}-{generation + 1}")
            if claim is None:
                break
            generation, newest = generation + 1, claim
        if newest and not newest["released"] and newest["expires"] > clock():
            held[slot] = newest["holder"]
    return held


def test_the_constants_leave_room_for_a_run_and_for_modal_expiry():
    assert runner.LEASE_SECONDS >= TIMEOUT + runner.GUARD_MARGIN_SECONDS + 30 * 60
    assert runner.INTERRUPT_GRACE_SECONDS < runner.LEASE_SECONDS
    # A day's claims matter for a day plus a lease: far inside Modal's expiry.
    assert runner.EPOCH_SECONDS + 2 * runner.LEASE_SECONDS < FakeDict.TTL / 2
    # Takeover waits out the clock error of two invocations.
    assert runner.CLOCK_MARGIN_SECONDS >= 2 * runner.MAX_CLOCK_DRIFT_SECONDS + 20
    assert runner.GUARD_MARGIN_SECONDS > runner.CLOCK_MARGIN_SECONDS


def test_two_slots_then_a_third_run_waits():
    clock = Clock()
    store = FakeDict(clock)
    a, b, c = (slots_for(store, clock, h) for h in "abc")
    leases = {"a": a.acquire(), "b": b.acquire()}
    assert {lease.slot for lease in leases.values()} == {0, 1}
    sleeps = []

    def sleep(seconds):
        sleeps.append(seconds)
        clock.now += seconds

    with pytest.raises(TimeoutError):
        c.acquire(wait_seconds=60, poll_seconds=30, sleep=sleep)
    assert sleeps == [30, 30]
    a.release(leases["a"])
    assert c.acquire(wait_seconds=0, sleep=sleep).slot == leases["a"].slot
    assert holders_of(store, clock) == {
        leases["a"].slot: "c",
        leases["b"].slot: "b",
    }


def test_a_lapsed_claim_is_taken_only_after_the_clock_margin():
    clock = Clock()
    store = FakeDict(clock)
    dead = slots_for(store, clock, "dead", count=1).acquire()
    nxt = slots_for(store, clock, "next", count=1)
    clock.now = dead.expires + MARGIN - 1
    assert run_steps(store, nxt._try_steps(0)) == (True, None)
    clock.now = dead.expires + MARGIN
    assert run_steps(store, nxt._try_steps(0))[1] is not None


def test_a_stale_release_cannot_free_a_newer_holder():
    clock = Clock()
    store = FakeDict(clock)
    late = slots_for(store, clock, "late", count=1)
    old = late.acquire()
    clock.now = old.expires + MARGIN
    slots_for(store, clock, "successor", count=1).acquire()
    late.release(old)
    assert holders_of(store, clock) == {0: "successor"}
    third = slots_for(store, clock, "third", count=1)
    assert run_steps(store, third._try_steps(0)) == (True, None)


def test_a_contender_cannot_displace_a_claim_made_after_it_looked():
    clock = Clock()
    store = FakeDict(clock)
    holder = slots_for(store, clock, "holder", count=1)
    lease = holder.acquire()
    a = slots_for(store, clock, "a", count=1)
    c = slots_for(store, clock, "c", count=1)
    clock.now = lease.expires + MARGIN
    steps = a._try_steps(0)
    call = next(steps)
    while call[0] == "get":  # A reads up to its create
        call = steps.send(store.get(call[1]))
    assert run_steps(store, c._try_steps(0))[1] is not None
    with pytest.raises(StopIteration) as done:  # A's create now fails
        steps.send(store.put(call[1], call[2], skip_if_exists=call[3]))
    assert done.value.value is None
    assert holders_of(store, clock) == {0: "c"}


@pytest.mark.parametrize("calls", range(6))
def test_a_holder_that_dies_at_any_step_frees_its_slot_after_the_lease(calls):
    clock = Clock()
    store = FakeDict(clock)
    dying = slots_for(store, clock, "dying", count=1)
    run_steps(store, dying._try_steps(0), limit=calls)
    clock.now += runner.LEASE_SECONDS + MARGIN
    assert slots_for(store, clock, "next", count=1).acquire(wait_seconds=0).slot == 0


def test_a_lease_across_midnight_holds_both_days():
    clock = Clock(now=22 * 3600.0)  # two hours before the day ends
    store = FakeDict(clock)
    night = slots_for(store, clock, "night", count=1)
    lease = night.acquire()
    assert [epoch for epoch, _ in lease.claims] == [0, 1]
    clock.now = DAY + 600  # the next day, the run still going
    assert holders_of(store, clock) == {0: "night"}
    morning = slots_for(store, clock, "morning", count=1)
    assert run_steps(store, morning._try_steps(0)) == (True, None)
    night.release(lease)
    assert run_steps(store, morning._try_steps(0))[1] is not None


def test_a_refused_second_day_gives_the_first_day_back():
    # Someone already holds tomorrow's chain: taking today's alone would
    # hold a slot this run cannot keep past midnight.
    clock = Clock(now=22 * 3600.0)
    store = FakeDict(clock)
    store.put(
        "claim-0-1-0",
        {"holder": "other", "expires": DAY + 3 * 3600, "released": False},
    )
    a = slots_for(store, clock, "a", count=1)
    assert run_steps(store, a._try_steps(0)) == (True, None)
    assert store.data["claim-0-0-0"]["released"] is True


def test_an_interrupt_frees_the_slot_after_the_grace_period():
    clock = Clock()
    store = FakeDict(clock)
    slots = slots_for(store, clock, "a", count=1)
    lease = slots.acquire()
    slots.release(lease, grace=runner.INTERRUPT_GRACE_SECONDS)
    assert holders_of(store, clock) == {0: "a"}
    other = slots_for(store, clock, "b", count=1)
    clock.now += runner.INTERRUPT_GRACE_SECONDS + MARGIN - 1
    assert run_steps(store, other._try_steps(0)) == (True, None)
    clock.now += 1
    assert run_steps(store, other._try_steps(0))[1] is not None


def test_a_step_that_outlasts_its_lease_grants_nothing():
    # A machine asleep in the middle of taking a slot: whatever it wrote,
    # it holds nothing afterwards, and nobody is displaced.
    clock = Clock()
    store = FakeDict(clock)
    a = slots_for(store, clock, "a", count=1)
    steps = a._try_steps(0)
    call = next(steps)
    while call[0] == "get":
        call = steps.send(store.get(call[1]))
    clock.now += 9 * DAY  # asleep with the create in flight
    b = slots_for(store, clock, "b", count=1).acquire()
    try:
        while True:
            if call[0] == "get":
                call = steps.send(store.get(call[1]))
            else:
                call = steps.send(store.put(call[1], call[2], skip_if_exists=call[3]))
    except StopIteration as done:
        assert done.value is None
    assert holders_of(store, clock) == {0: "b"}
    assert b.slot == 0


def test_a_week_late_write_lands_in_a_day_that_no_longer_matters():
    # Review of bac8974, 1: with no pointer to roll back, a write that
    # arrives days late cannot change which claim is newest today.
    clock = Clock()
    store = FakeDict(clock)
    early = slots_for(store, clock, "early", count=1)
    lease = early.acquire()
    clock.now += 6.5 * DAY
    current = slots_for(store, clock, "current", count=1).acquire()
    early.release(lease)  # the late write
    stalled = slots_for(store, clock, "stalled", count=1)
    steps = stalled._try_steps(0)
    call = next(steps)
    clock.now += 0.9 * DAY - runner.LEASE_SECONDS  # stalls, then resumes
    result = None
    try:
        while True:
            if call[0] == "get":
                call = steps.send(store.get(call[1]))
            else:
                call = steps.send(store.put(call[1], call[2], skip_if_exists=call[3]))
    except StopIteration as done:
        result = done.value
    live = current.expires > clock.now
    assert result is None or not live


def test_a_fast_clock_cannot_take_an_occupied_slot():
    # Review of bac8974, 2: main() runs every holder on Modal's clock; within
    # the drift it enforces, a contender cannot see a live claim as lapsed
    # before the run under it has ended.
    clock = Clock()
    store = FakeDict(clock)
    drift = runner.MAX_CLOCK_DRIFT_SECONDS
    holder = slots_for(store, clock, "holder", count=1, offset=-drift)
    lease = holder.acquire()
    run_must_end_by = lease.expires - runner.GUARD_MARGIN_SECONDS  # remote guard
    fast = slots_for(store, clock, "fast", count=1, offset=drift)
    clock.now = run_must_end_by
    assert run_steps(store, fast._try_steps(0)) == (True, None)
    taken_at = None
    while taken_at is None:
        clock.now += 1
        if run_steps(store, fast._try_steps(0))[1] is not None:
            taken_at = clock.now
    assert taken_at >= run_must_end_by + runner.GUARD_MARGIN_SECONDS - 2 * drift


def test_a_machine_five_hours_fast_still_sees_modal_time():
    # Review of bac8974, 2, as reported: B's own clock is five hours ahead.
    # main() gives the slots Modal's time (local plus the measured offset),
    # so B sees A's claim as live.
    clock = Clock()
    store = FakeDict(clock)
    slots_for(store, clock, "a", count=1).acquire()

    def b_local():
        return clock() + 5 * 3600

    offset = runner.clock_offset(clock, local=b_local)
    assert offset == -5 * 3600
    b = runner.SimulationSlots(
        store, holder="b", count=1, clock=lambda: b_local() + offset
    )
    assert run_steps(store, b._try_steps(0)) == (True, None)
    assert holders_of(store, clock) == {0: "a"}


def test_the_clock_offset_is_measured_against_modal():
    local = iter([100.0, 104.0])
    assert runner.clock_offset(lambda: 1_102.0, local=lambda: next(local)) == 1_000.0
    # A slow first round trip (a cold start) is retried.
    local = iter([0.0, 50.0, 60.0, 61.0])
    assert runner.clock_offset(lambda: 5.5, local=lambda: next(local)) == -55.0
    slow = iter(range(0, 1000, 20))
    with pytest.raises(runner.LeaseLost):
        runner.clock_offset(lambda: 0.0, local=lambda: float(next(slow)))


class FailingPuts(FakeDict):
    """A Dict whose writes start failing after ``allowed`` of them."""

    def __init__(self, clock, allowed):
        super().__init__(clock)
        self.allowed = allowed

    def put(self, key, value, *, skip_if_exists=False):
        if self.allowed == 0:
            raise OSError("connection lost")
        self.allowed -= 1
        return super().put(key, value, skip_if_exists=skip_if_exists)


def test_a_failed_second_claim_gives_the_first_back_when_it_can():
    clock = Clock(now=22 * 3600.0)  # the lease spans two days: two creates
    store = FailingPuts(clock, allowed=1)
    a = slots_for(store, clock, "a", count=1)
    with pytest.raises(OSError):
        a.acquire(wait_seconds=0)
    store.allowed = 10
    # The first claim stays (its release failed too) but lapses with the lease.
    clock.now += runner.LEASE_SECONDS + MARGIN
    assert slots_for(store, clock, "b", count=1).acquire(wait_seconds=0).slot == 0


def holder_program(slots):
    """main()'s use of the slots, one Dict call or event at a time."""
    lease = None
    while lease is None:
        for slot in range(slots.count):
            lease = yield from slots._try_steps(slot)
            if lease is not None:
                break
        else:
            yield ("pause",)
    outcome = yield ("start", lease)
    if outcome == "running":
        outcome = yield ("await",)
    # main(): a returned run frees the slot now; after a caught ctrl-C
    # (app.run() exited, the stop request sent) it frees after the grace;
    # after a lost connection or a remote error nothing is written.
    if outcome == "returned":
        yield from slots._release_steps(lease)
    elif outcome == "interrupted":
        yield from slots._release_steps(lease, grace=runner.INTERRUPT_GRACE_SECONDS)


# Modal's disconnect stops an ephemeral app's tasks "in a few seconds"
# (modal/runner.py); the model allows a minute, inside the grace period.
STOP_AFTER_DISCONNECT = 60


@settings(max_examples=600, deadline=None)
@given(st.data())
def test_interleaved_holders_never_overlap_on_a_slot_and_never_lose_one(data):
    """Model check: holders interleaved call by call, each on its own clock
    (within the drift main() enforces), with clock jumps of any size at any
    point (a stalled step, a closed laptop, midnight), crashes (no release;
    a started run continues to its end), interrupts, lost connections and
    Dict entry expiry. Safety: two runs never overlap on one slot, so at
    most SLOT_COUNT run at once. Liveness: once every lease has lapsed, both
    slots can be taken again."""
    clock = Clock(now=float(data.draw(st.sampled_from([3600, 12 * 3600, 23 * 3600]))))
    store = FakeDict(clock)
    drift = runner.MAX_CLOCK_DRIFT_SECONDS
    count = data.draw(st.integers(2, 4), label="holders")
    actors = []
    for index in range(count):
        offset = data.draw(st.sampled_from([-drift, 0, drift]), label="offset")
        program = holder_program(slots_for(store, clock, f"h{index}", offset=offset))
        actors.append({"program": program, "call": next(program), "done": False})
    runs = []

    def send(actor, value):
        try:
            actor["call"] = actor["program"].send(value)
        except StopIteration:
            actor["done"] = True

    for _ in range(data.draw(st.integers(0, 150), label="actions")):
        action = data.draw(
            st.sampled_from(
                ["step", "step", "step", "tick", "crash", "interrupt", "disconnect"]
            )
        )
        if action == "tick":
            clock.now += data.draw(
                st.sampled_from(
                    [1, 60, 600, 3600, TIMEOUT, 4 * 3600, 20 * 3600, 6.5 * DAY, 8 * DAY]
                )
            )
            continue
        live = [a for a in actors if not a["done"]]
        if not live:
            break
        if action in ("interrupt", "disconnect"):
            awaiting = [a for a in live if a["call"][0] == "await"]
            if awaiting:
                actor = data.draw(st.sampled_from(awaiting))
                if action == "interrupt":  # ctrl-C: the stop request is sent
                    run = actor["run"]
                    run["end"] = min(run["end"], clock.now + STOP_AFTER_DISCONNECT)
                    send(actor, "interrupted")
                else:  # connection lost: the run goes on to its own end
                    send(actor, "connection_lost")
            continue
        actor = data.draw(st.sampled_from(live))
        if action == "crash":
            actor["done"] = True
            continue
        call = actor["call"]
        if call[0] == "get":
            send(actor, store.get(call[1]))
        elif call[0] == "put":
            send(actor, store.put(call[1], call[2], skip_if_exists=call[3]))
        elif call[0] == "pause":
            send(actor, None)
        elif call[0] == "start":
            lease = call[1]
            # The remote guard, on Modal's (true) clock.
            if clock.now + TIMEOUT + runner.GUARD_MARGIN_SECONDS > lease.expires:
                send(actor, "refused")
                continue
            duration = data.draw(st.integers(1, TIMEOUT), label="run seconds")
            run = {"slot": lease.slot, "start": clock.now, "end": clock.now + duration}
            for other in runs:
                if other["slot"] == run["slot"]:
                    assert other["end"] <= run["start"], (other, run)
            runs.append(run)
            actor["run"] = run
            send(actor, "running")
        elif call[0] == "await" and clock.now >= actor["run"]["end"]:
            send(actor, "returned")
        running = [r for r in runs if r["start"] <= clock.now < r["end"]]
        assert len(running) <= runner.SLOT_COUNT

    clock.now += runner.LEASE_SECONDS + MARGIN + drift
    fresh = [slots_for(store, clock, f"fresh{n}") for n in range(runner.SLOT_COUNT)]
    taken = {s.acquire(wait_seconds=0).slot for s in fresh}
    assert taken == set(range(runner.SLOT_COUNT)), (taken, clock.now, store.data)


def modal_fakes(slots, remote, run=nullcontext):
    return lambda mounts: (
        SimpleNamespace(
            enable_output=nullcontext,
            Dict=SimpleNamespace(from_name=lambda name, create_if_missing: slots),
        ),
        SimpleNamespace(run=run),
        SimpleNamespace(remote=remote),
        SimpleNamespace(remote=time.time),
    )


@pytest.fixture
def stub_main(monkeypatch, tmp_path):
    monkeypatch.setattr(runner, "validate_selection", lambda request: None)
    monkeypatch.setattr(
        runner, "input_manifest", lambda event, hf_cache=None: ({"event": event}, {})
    )
    monkeypatch.setattr(runner, "download_prefix", lambda value: tmp_path / "download")
    saved = []
    monkeypatch.setattr(runner, "save_download", lambda *args: saved.append(args) or [])
    return saved


ARGS = ["--event", "autumn_budget_2024", "--execute"]


def claims_in(slots):
    return [v for k, v in slots.data.items() if k.startswith("claim-")]


def test_a_finished_run_frees_its_slot_at_once(monkeypatch, stub_main):
    slots = FakeDict()
    seen = {}

    def remote(payload, lease_expires):
        seen["expires"] = lease_expires
        return {"files": {}}

    monkeypatch.setattr(runner, "modal_function", modal_fakes(slots, remote))
    assert runner.main(ARGS) == 0
    assert len(stub_main) == 1
    assert all(claim["released"] is True for claim in claims_in(slots))
    # The run was told a lease long enough for its timeout and the margin.
    assert seen["expires"] - time.time() > TIMEOUT + runner.GUARD_MARGIN_SECONDS


def test_a_lost_connection_keeps_the_claim_until_the_lease_lapses(
    monkeypatch, stub_main
):
    # The runner re-raises a lost connection without asking the server to
    # stop the app, so the run may still be going.
    class LostConnection(Exception):
        pass

    def lost(payload, lease_expires):
        raise LostConnection

    slots = FakeDict()
    monkeypatch.setattr(runner, "modal_function", modal_fakes(slots, lost))
    with pytest.raises(LostConnection):
        runner.main(ARGS)
    assert all(claim["released"] is False for claim in claims_in(slots))
    assert all(
        claim["expires"] >= time.time() + runner.LEASE_SECONDS - 60
        for claim in claims_in(slots)
    )


def test_a_returned_result_survives_a_failed_app_exit(monkeypatch, stub_main):
    class ExitFails:
        def __enter__(self):
            return self

        def __exit__(self, kind, value, traceback):
            raise OSError("stop request failed")

    slots = FakeDict()
    monkeypatch.setattr(
        runner,
        "modal_function",
        modal_fakes(slots, lambda payload, lease_expires: {"files": {}}, run=ExitFails),
    )
    assert runner.main(ARGS) == 0
    assert len(stub_main) == 1
    assert all(claim["released"] is True for claim in claims_in(slots))


def test_a_returned_result_survives_a_failed_release(monkeypatch, stub_main, capsys):
    # Review of bac8974, 3: the Dict failing at release must not cost a
    # completed result; the claim simply lapses.
    class ReleaseFails(FakeDict):
        def put(self, key, value, *, skip_if_exists=False):
            if not skip_if_exists:
                raise OSError("connection lost")
            return super().put(key, value, skip_if_exists=skip_if_exists)

    slots = ReleaseFails()
    monkeypatch.setattr(
        runner,
        "modal_function",
        modal_fakes(slots, lambda payload, lease_expires: {"files": {}}),
    )
    assert runner.main(ARGS) == 0
    assert len(stub_main) == 1
    assert "not released" in capsys.readouterr().err


def test_a_clock_that_moved_while_waiting_stops_the_run(monkeypatch, stub_main, capsys):
    slots = FakeDict()
    readings = iter([0.0, 120.0])  # Modal minus local: 0 at first, then 120 s

    def modal_now():
        return time.time() + next(readings)

    def fakes(mounts):
        modal, app, replay, _ = modal_fakes(
            slots, lambda payload, lease_expires: pytest.fail("the run must not start")
        )(mounts)
        return modal, app, replay, SimpleNamespace(remote=modal_now)

    monkeypatch.setattr(runner, "modal_function", fakes)
    assert runner.main(ARGS) == 75
    assert "clock moved" in capsys.readouterr().err
    assert all(claim["released"] is True for claim in claims_in(slots))
