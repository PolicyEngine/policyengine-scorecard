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
    assert claims[-1]["released"] is False
    assert claims[-1]["expires"] <= time.time() + runner.INTERRUPT_GRACE_SECONDS


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
    _, _, replay = runner.modal_function(mounts)
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
    def __init__(self):
        self.now = 1_000.0

    def __call__(self):
        return self.now


CHAIN_IDS = itertools.count()


def slots_for(store, clock, holder, **kwargs):
    return runner.SimulationSlots(
        store,
        holder=holder,
        clock=clock,
        chain_id=lambda: f"chain{next(CHAIN_IDS)}",
        **kwargs,
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
    """Each slot's newest generation, if it is held now."""
    held = {}
    for key, head in store.data.items():
        if not key.startswith("head-"):
            continue
        slot = int(key.split("-")[1])
        generation, newest = head["generation"], None
        while True:
            claim = store.data.get(f"claim-{slot}-{head['chain']}-{generation + 1}")
            if claim is None:
                break
            generation, newest = generation + 1, claim
        newest = newest or store.data.get(f"claim-{slot}-{head['chain']}-{generation}")
        if newest and not newest["released"] and newest["expires"] > clock():
            held[slot] = newest["holder"]
    return held


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


def test_a_stale_release_cannot_free_a_newer_holder():
    # Review of #166, 2(a): a holder past its lease releases after the slot
    # passed on; the release writes only its own generation.
    clock = Clock()
    store = FakeDict(clock)
    late = slots_for(store, clock, "late", count=1)
    old = late.acquire()
    clock.now += runner.LEASE_SECONDS + 1
    successor = slots_for(store, clock, "successor", count=1).acquire()
    late.release(old)
    assert holders_of(store, clock) == {0: "successor"}
    third = slots_for(store, clock, "third", count=1)
    assert run_steps(store, third._try_steps(0)) == (True, None)
    assert successor.generation == old.generation + 1


def test_a_reclaimer_cannot_displace_a_claim_made_after_it_looked():
    # Review of #166, 2(b): A sees the slot free, then C takes it before A
    # writes; A's create-if-absent of the same generation fails.
    clock = Clock()
    store = FakeDict(clock)
    holder = slots_for(store, clock, "holder", count=1)
    lease = holder.acquire()
    a = slots_for(store, clock, "a", count=1)
    c = slots_for(store, clock, "c", count=1)
    clock.now += runner.LEASE_SECONDS + 1
    steps = a._try_steps(0)
    call = next(steps)
    while call[0] == "get":  # A reads up to its create
        call = steps.send(store.get(call[1]))
    holder.release(lease)
    assert run_steps(store, c._try_steps(0))[1] is not None
    with pytest.raises(StopIteration) as done:  # A's create now fails
        steps.send(store.put(call[1], call[2], skip_if_exists=call[3]))
    assert done.value.value is None
    assert holders_of(store, clock) == {0: "c"}


@pytest.mark.parametrize("calls", range(8))
def test_a_holder_that_dies_at_any_step_frees_its_slot_after_the_lease(calls):
    # Review of #166, 1: a caller that dies mid-protocol never loses a slot
    # for good.
    clock = Clock()
    store = FakeDict(clock)
    dying = slots_for(store, clock, "dying", count=1)
    run_steps(store, dying._try_steps(0), limit=calls)
    clock.now += runner.LEASE_SECONDS + 1
    assert slots_for(store, clock, "next", count=1).acquire(wait_seconds=0).slot == 0


def test_a_lapsed_lease_is_not_renewed_even_when_its_next_key_is_free():
    # The slot changes hands across days and Modal expires the old keys; a
    # client back from a week asleep must not renew into a key that no
    # longer exists while someone else holds the slot.
    day = 24 * 60 * 60
    clock = Clock()
    store = FakeDict(clock)
    sleeper = slots_for(store, clock, "sleeper", count=1)
    stale = sleeper.acquire()
    clock.now += runner.LEASE_SECONDS + 1
    for name in ("b", "c"):
        slots = slots_for(store, clock, name, count=1)
        slots.release(slots.acquire())
        clock.now += day
    clock.now += 8 * day  # every old key idles past Modal's 7 days
    current = slots_for(store, clock, "current", count=1).acquire()
    following = runner.SimulationSlots.claim_key(0, stale.chain, stale.generation + 1)
    assert store.get(following) is None  # a create here would succeed
    with pytest.raises(runner.LeaseLost):
        sleeper.renew(stale)
    assert holders_of(store, clock) == {0: "current"}
    assert current.slot == 0


def test_renewal_after_a_takeover_is_refused():
    clock = Clock()
    store = FakeDict(clock)
    slow = slots_for(store, clock, "slow", count=1)
    lease = slow.acquire()
    clock.now += runner.LEASE_SECONDS + 1
    slots_for(store, clock, "fast", count=1).acquire()
    with pytest.raises(runner.LeaseLost):
        slow.renew(lease)
    assert holders_of(store, clock) == {0: "fast"}


def test_renewal_extends_from_now_and_keeps_the_slot():
    clock = Clock()
    store = FakeDict(clock)
    slots = slots_for(store, clock, "a", count=1)
    lease = slots.acquire()
    clock.now += 3_000  # image build
    renewed = slots.renew(lease)
    assert renewed.expires == clock.now + runner.LEASE_SECONDS
    assert renewed.generation == lease.generation + 1
    clock.now += runner.LEASE_SECONDS - 1
    assert holders_of(store, clock) == {0: "a"}


def test_an_interrupt_frees_the_slot_after_the_grace_period():
    clock = Clock()
    store = FakeDict(clock)
    slots = slots_for(store, clock, "a", count=1)
    lease = slots.acquire()
    slots.release(lease, grace=runner.INTERRUPT_GRACE_SECONDS)
    assert holders_of(store, clock) == {0: "a"}
    clock.now += runner.INTERRUPT_GRACE_SECONDS
    assert holders_of(store, clock) == {}


def test_the_lease_covers_the_timeout_margin_and_scheduling():
    timeout = runner.RESOURCE_LIMITS["timeout_seconds"]
    assert runner.LEASE_SECONDS >= timeout + runner.GUARD_MARGIN_SECONDS + 30 * 60
    assert runner.STALE_STEP_SECONDS < FakeDict.TTL
    assert runner.INTERRUPT_GRACE_SECONDS < runner.LEASE_SECONDS


TIMEOUT = runner.RESOURCE_LIMITS["timeout_seconds"]
# Modal's disconnect stops an ephemeral app's tasks "in a few seconds"
# (modal/runner.py); the model allows a minute, inside the grace period.
STOP_AFTER_DISCONNECT = 60


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
    yield ("pause",)  # image build
    try:
        lease = yield from slots._renew_steps(lease)
    except runner.LeaseLost:
        yield from slots._release_steps(lease)
        return
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


@settings(max_examples=600, deadline=None)
@given(st.data())
def test_interleaved_holders_never_overlap_on_a_slot_and_never_lose_one(data):
    """Model check: holders interleaved call by call, with clock jumps,
    crashes (no release; a started run continues to its end), interrupts and
    Dict entry expiry. Safety: two runs never overlap on one slot, so at most
    SLOT_COUNT run at once. Liveness: once every lease has lapsed, both slots
    can be taken again."""
    clock = Clock()
    store = FakeDict(clock)
    count = data.draw(st.integers(2, 4), label="holders")
    actors = []
    for index in range(count):
        program = holder_program(slots_for(store, clock, f"h{index}"))
        actors.append(
            {"program": program, "call": next(program), "done": False, "since": 1e3}
        )
    runs = []

    def send(actor, value):
        before = actor["call"][0]
        try:
            actor["call"] = actor["program"].send(value)
        except StopIteration:
            actor["done"] = True
            return
        if actor["call"][0] in ("get", "put") and before not in ("get", "put"):
            actor["since"] = clock.now  # a protocol step begins

    for _ in range(data.draw(st.integers(0, 150), label="actions")):
        action = data.draw(
            st.sampled_from(
                ["step", "step", "step", "tick", "crash", "interrupt", "disconnect"]
            )
        )
        if action == "tick":
            seconds = data.draw(
                st.sampled_from([1, 60, 600, 3600, TIMEOUT, 4 * 3600, 8 * 86400])
            )
            # The stated assumption: no protocol step (consecutive Dict
            # calls) spans 7 days, so Modal never expires a key a step read
            # before the step ends; between steps, anything goes.
            limit = min(
                (
                    6 * 86400 - (clock.now - a["since"])
                    for a in actors
                    if not a["done"] and a["call"][0] in ("get", "put")
                ),
                default=seconds,
            )
            clock.now += max(0, min(seconds, limit))
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
            if clock.now + TIMEOUT + runner.GUARD_MARGIN_SECONDS > lease.expires:
                send(actor, "refused")  # the remote guard: a remote error
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

    # Once every lease has lapsed both slots can be taken, after at most one
    # further lease when a reader had to block a slot whose head outlived
    # its claim.
    clock.now += runner.LEASE_SECONDS + 1
    taken = set()
    for attempt in range(2):
        for n in range(runner.SLOT_COUNT):
            holder = slots_for(store, clock, f"fresh{attempt}-{n}")
            for slot in range(runner.SLOT_COUNT):
                if slot not in taken and holder._drive(holder._try_steps(slot)):
                    taken.add(slot)
                    break
        if taken == set(range(runner.SLOT_COUNT)):
            break
        clock.now += runner.LEASE_SECONDS + 1
    assert taken == set(range(runner.SLOT_COUNT)), (taken, clock.now, store.data)


def test_a_week_stalled_acquire_cannot_replace_a_live_chain():
    # Review of dff81d0, 2: A reads the head, stalls a week (Modal expires
    # every key), B builds a new chain and holds the slot; A's late writes
    # must not point the head back at A's dead chain.
    day = 24 * 60 * 60
    clock = Clock()
    store = FakeDict(clock)
    old = slots_for(store, clock, "old", count=1)
    old.release(old.acquire())
    a = slots_for(store, clock, "a", count=1)
    steps = a._try_steps(0)
    call = next(steps)
    while call[0] == "get":
        call = steps.send(store.get(call[1]))
    clock.now += 8 * day
    b = slots_for(store, clock, "b", count=1).acquire()
    with pytest.raises(StopIteration) as done:
        while True:
            if call[0] == "get":
                call = steps.send(store.get(call[1]))
            else:
                call = steps.send(store.put(call[1], call[2], skip_if_exists=call[3]))
    assert done.value.value is None
    assert store.get("head-0")["chain"] == b.chain
    assert holders_of(store, clock) == {0: "b"}
    third = slots_for(store, clock, "third", count=1)
    assert run_steps(store, third._try_steps(0)) == (True, None)


def test_a_lost_connection_keeps_the_claim_until_the_lease_lapses(
    monkeypatch, tmp_path
):
    # Review of dff81d0, 1: the runner re-raises a lost connection without
    # asking the server to stop the app, so the run may still be going.
    class LostConnection(Exception):
        pass

    def lost(payload, lease_expires):
        raise LostConnection

    slots = FakeDict()
    monkeypatch.setattr(runner, "validate_selection", lambda request: None)
    monkeypatch.setattr(
        runner, "input_manifest", lambda event, hf_cache=None: ({"event": event}, {})
    )
    monkeypatch.setattr(runner, "download_prefix", lambda value: tmp_path / "download")
    monkeypatch.setattr(
        runner,
        "modal_function",
        lambda mounts: (
            SimpleNamespace(
                enable_output=nullcontext,
                Dict=SimpleNamespace(from_name=lambda name, create_if_missing: slots),
            ),
            SimpleNamespace(run=nullcontext),
            SimpleNamespace(remote=lost),
        ),
    )
    with pytest.raises(LostConnection):
        runner.main(["--event", "autumn_budget_2024", "--execute"])
    claims = [v for k, v in slots.data.items() if k.startswith("claim-")]
    newest = max(claims, key=lambda claim: claim["expires"])
    assert newest["released"] is False
    assert newest["expires"] >= time.time() + runner.LEASE_SECONDS - 60


def test_a_finished_run_frees_its_slot_at_once(monkeypatch, tmp_path):
    slots = FakeDict()
    monkeypatch.setattr(runner, "validate_selection", lambda request: None)
    monkeypatch.setattr(
        runner, "input_manifest", lambda event, hf_cache=None: ({"event": event}, {})
    )
    monkeypatch.setattr(runner, "download_prefix", lambda value: tmp_path / "download")
    monkeypatch.setattr(runner, "save_download", lambda *args: [])
    monkeypatch.setattr(
        runner,
        "modal_function",
        lambda mounts: (
            SimpleNamespace(
                enable_output=nullcontext,
                Dict=SimpleNamespace(from_name=lambda name, create_if_missing: slots),
            ),
            SimpleNamespace(run=nullcontext),
            SimpleNamespace(remote=lambda payload, lease_expires: {"files": {}}),
        ),
    )
    assert runner.main(["--event", "autumn_budget_2024", "--execute"]) == 0
    claims = [v for k, v in slots.data.items() if k.startswith("claim-")]
    assert max(claims, key=lambda claim: claim["expires"])["released"] is True


def finish(store, steps, call):
    """Drive a protocol generator from a pending call to its return value."""
    try:
        while True:
            if call[0] == "get":
                call = steps.send(store.get(call[1]))
            else:
                call = steps.send(store.put(call[1], call[2], skip_if_exists=call[3]))
    except StopIteration as done:
        return done.value


def test_a_head_response_read_before_a_week_asleep_is_not_acted_on():
    # Review of 4a5a272, 1(a): the head was answered, then the machine slept
    # a week before the step used it; the step must not look fresh.
    day = 24 * 60 * 60
    clock = Clock()
    store = FakeDict(clock)
    old = slots_for(store, clock, "old", count=1)
    old.release(old.acquire())
    a = slots_for(store, clock, "a", count=1)
    steps = a._try_steps(0)
    call = next(steps)
    assert call == ("get", "head-0")
    answered = store.get("head-0")  # the server answers...
    clock.now += 8 * day  # ...and the response sits unread
    b = slots_for(store, clock, "b", count=1).acquire()
    assert finish(store, steps, steps.send(answered)) is None
    assert store.get("head-0")["chain"] == b.chain
    assert holders_of(store, clock) == {0: "b"}


def test_a_fresh_chain_head_read_before_a_week_asleep_is_not_acted_on():
    # The same stall on a chain with no claim yet (generation -1): only the
    # step's own clock, read before its first call, shows it is stale.
    day = 24 * 60 * 60
    clock = Clock()
    store = FakeDict(clock)
    store.put("head-0", {"chain": "abandoned", "generation": -1})
    a = slots_for(store, clock, "a", count=1)
    steps = a._try_steps(0)
    assert next(steps) == ("get", "head-0")
    answered = store.get("head-0")
    clock.now += 8 * day
    b = slots_for(store, clock, "b", count=1).acquire()
    assert finish(store, steps, steps.send(answered)) is None
    assert store.get("head-0")["chain"] == b.chain
    assert holders_of(store, clock) == {0: "b"}


def test_a_head_written_a_week_late_blocks_the_slot_instead_of_hiding_a_holder():
    # Review of 4a5a272, 1(b): A's head write lands after every key expired
    # and B built a new chain. A reader must not take the slot from B.
    day = 24 * 60 * 60
    clock = Clock()
    store = FakeDict(clock)
    a = slots_for(store, clock, "a", count=1)
    steps = a._try_steps(0)
    call = next(steps)
    while not (call[0] == "put" and call[1] == "head-0" and not call[3]):
        if call[0] == "get":
            call = steps.send(store.get(call[1]))
        else:
            call = steps.send(store.put(call[1], call[2], skip_if_exists=call[3]))
    late_head = call  # A's claim exists; its head write is in flight
    clock.now += 8 * day
    b = slots_for(store, clock, "b", count=1)
    b_lease = b.renew(b.acquire())
    store.put(late_head[1], late_head[2], skip_if_exists=False)  # it lands
    assert store.get("head-0")["chain"] != b_lease.chain
    c = slots_for(store, clock, "c", count=1)
    assert run_steps(store, c._try_steps(0)) == (True, None)
    assert run_steps(store, c._try_steps(0)) == (True, None)  # still blocked
    # B's lease began before the late write, so it ends within the block.
    clock.now += runner.LEASE_SECONDS + 1
    assert b_lease.expires <= clock.now
    assert slots_for(store, clock, "d", count=1).acquire(wait_seconds=0).slot == 0


class FailingHeadPuts(FakeDict):
    """Dict whose unconditional head writes fail (a lost connection)."""

    def put(self, key, value, *, skip_if_exists=False):
        if key.startswith("head-") and not skip_if_exists:
            raise OSError("connection lost")
        return super().put(key, value, skip_if_exists=skip_if_exists)


def test_a_failed_head_write_gives_the_claim_back():
    # A claim without its hint would hold the slot for a lease with no run.
    clock = Clock()
    store = FailingHeadPuts(clock)
    a = slots_for(store, clock, "a", count=1)
    with pytest.raises(OSError):
        a.acquire(wait_seconds=0)
    claims = [v for k, v in store.data.items() if k.startswith("claim-")]
    assert claims and all(claim["released"] for claim in claims)
    # The same on renewal: the new generation is released, not held.
    store2 = FakeDict(clock)
    b = slots_for(store2, clock, "b", count=1)
    lease = b.acquire()
    b.store = FailingHeadPuts(clock)
    b.store.data, b.store.touched = store2.data, store2.touched
    with pytest.raises(OSError):
        b.renew(lease)
    newest = store2.data[
        runner.SimulationSlots.claim_key(0, lease.chain, lease.generation + 1)
    ]
    assert newest["released"] is True


def test_a_returned_result_survives_a_failed_app_exit(monkeypatch, tmp_path):
    class ExitFails:
        def __enter__(self):
            return self

        def __exit__(self, kind, value, traceback):
            raise OSError("stop request failed")

    slots = FakeDict()
    saved = []
    monkeypatch.setattr(runner, "validate_selection", lambda request: None)
    monkeypatch.setattr(
        runner, "input_manifest", lambda event, hf_cache=None: ({"event": event}, {})
    )
    monkeypatch.setattr(runner, "download_prefix", lambda value: tmp_path / "download")
    monkeypatch.setattr(runner, "save_download", lambda *args: saved.append(args) or [])
    monkeypatch.setattr(
        runner,
        "modal_function",
        lambda mounts: (
            SimpleNamespace(
                enable_output=nullcontext,
                Dict=SimpleNamespace(from_name=lambda name, create_if_missing: slots),
            ),
            SimpleNamespace(run=ExitFails),
            SimpleNamespace(remote=lambda payload, lease_expires: {"files": {}}),
        ),
    )
    assert runner.main(["--event", "autumn_budget_2024", "--execute"]) == 0
    assert len(saved) == 1
    claims = [v for k, v in slots.data.items() if k.startswith("claim-")]
    assert max(claims, key=lambda claim: claim["expires"])["released"] is True
