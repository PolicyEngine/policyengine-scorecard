"""Discovery's permission boundary and actual enqueue behavior on local git."""

import ast
import copy
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from pipeline import uk_replay_interface as interface
from pipeline import uk_replay_queue as queue

ROOT = Path(__file__).resolve().parent.parent
RUN_URL = "https://github.com/PolicyEngine/policyengine-scorecard/actions/runs/1"
EMPTY_DRAIN = (
    "github.event_name == 'workflow_dispatch' && github.event.inputs.request == ''"
)
DATA_TOKEN = "secrets.PE_UK_PRIVATE_HF_READ_TOKEN"


def workflow():
    return yaml.safe_load((ROOT / ".github/workflows/uk-replay.yml").read_text())


def test_discovery_holds_the_token_only_in_an_empty_manual_drain():
    document = workflow()
    jobs = document["jobs"]
    assert set(document[True]) == {
        "repository_dispatch",
        "workflow_dispatch",
        "schedule",
    }
    assert jobs["tick"]["if"] == "github.event_name == 'schedule'"
    assert jobs["tick"]["permissions"] == {"actions": "write"}
    assert "secrets." not in json.dumps(jobs["tick"])
    assert len(jobs["tick"]["steps"]) == 1
    assert "gh workflow run uk-replay.yml" in jobs["tick"]["steps"][0]["run"]
    assert "--request" not in jobs["tick"]["steps"][0]["run"]
    assert "secrets." not in json.dumps(document.get("env", {}))
    for job in jobs.values():
        assert "secrets." not in json.dumps(job.get("env", {}))

    holders = [
        (name, step)
        for name, job in jobs.items()
        for step in job["steps"]
        if DATA_TOKEN in json.dumps(step)
    ]
    assert {name for name, _ in holders} == {"discover", "run"}
    assert len(holders) == 2
    fetch = next(step for name, step in holders if name == "run")
    assert fetch["if"] == (
        'contains(fromJSON(\'["workflow_dispatch", "repository_dispatch"]\'), '
        "github.event_name)"
    )
    discovery = jobs["discover"]
    assert discovery["if"] == EMPTY_DRAIN
    token_step = next(step for name, step in holders if name == "discover")
    assert token_step["if"] == EMPTY_DRAIN
    assert token_step["env"] == {
        "HUGGING_FACE_TOKEN": "${{ secrets.PE_UK_PRIVATE_HF_READ_TOKEN }}"
    }
    assert token_step["run"] == "bash .github/scripts/uk_replay_discover.sh run"
    steps = discovery["steps"]
    snapshot = next(
        step
        for step in steps
        if step.get("run") == "bash .github/scripts/uk_replay_discover.sh snapshot"
    )
    upload = next(
        step
        for step in steps
        if step.get("uses", "").startswith("actions/upload-artifact")
    )
    guard = next(
        step
        for step in steps
        if step.get("run")
        == "python3 -I .github/scripts/uk_replay_output_guard.py discovery"
    )
    assert (
        steps.index(snapshot)
        < steps.index(token_step)
        < steps.index(guard)
        < steps.index(upload)
    )
    assert upload["with"]["name"] == "replay-discovery"
    assert upload["with"]["path"] == "discovery/"
    assert guard["id"] == "guard"
    assert upload["if"] == (
        "steps.guard.outcome == 'success' "
        "&& steps.discover.outputs.has_metadata == 'true'"
    )


def test_discovery_and_enqueue_are_separate_and_failure_cannot_block_the_drain():
    jobs = workflow()["jobs"]
    discover, enqueue, prepare = (
        jobs["discover"],
        jobs["discover_enqueue"],
        jobs["prepare"],
    )
    assert discover["permissions"] == {"contents": "read"}
    checkout = next(
        step
        for step in discover["steps"]
        if step.get("uses", "").startswith("actions/checkout")
    )
    assert checkout["with"]["persist-credentials"] is False
    assert enqueue["permissions"] == {"contents": "write"}
    assert enqueue["timeout-minutes"] == 10
    assert enqueue["needs"] == "discover"
    assert prepare["needs"] == "discover_enqueue"
    # always() is true even in a cancelled run; !cancelled() is not.
    assert prepare["if"] == f"${{{{ !cancelled() && {EMPTY_DRAIN} }}}}"
    assert "needs.discover" not in prepare["if"]
    assert jobs["run"]["if"] == (
        "${{ !cancelled() && needs.prepare.result == 'success' "
        "&& needs.prepare.outputs.request_id != '' }}"
    )
    assert "secrets." not in json.dumps(enqueue)
    download = next(
        step
        for step in enqueue["steps"]
        if step.get("uses", "").startswith("actions/download-artifact")
    )
    assert download["with"] == {
        "name": "replay-discovery",
        "path": "discovery/",
    }
    enqueue_step = next(
        step
        for step in enqueue["steps"]
        if step.get("run") == "bash .github/scripts/uk_replay_discover_enqueue.sh"
    )
    assert enqueue["steps"].index(download) < enqueue["steps"].index(enqueue_step)


def test_token_and_write_jobs_never_install_or_execute_a_release():
    jobs = workflow()["jobs"]
    for name in ("discover", "discover_enqueue"):
        commands = "\n".join(step.get("run", "") for step in jobs[name]["steps"])
        scripts = [
            ROOT / ".github/scripts/uk_replay_discover.sh"
            if name == "discover"
            else ROOT / ".github/scripts/uk_replay_discover_enqueue.sh"
        ]
        if name == "discover_enqueue":
            scripts.append(ROOT / ".github/scripts/uk_replay_state.sh")
        commands += "\n" + "\n".join(path.read_text() for path in scripts)
        for forbidden in (
            "uv venv",
            "pip install",
            "uk_replay_sandbox.sh",
            "uk_replay_drain.sh",
            "run-request",
            "BUNDLE_PROBE",
            "install_uk_replay_variant",
        ):
            assert forbidden not in commands, (name, forbidden)
    # Downloading and inspecting wheel bytes is safe only while no module
    # from the release is imported and no subprocess can run a wheel probe.
    for relative in (
        "pipeline/uk_replay_discover.py",
        ".github/scripts/uk_replay_discovery_guard.py",
    ):
        tree = ast.parse((ROOT / relative).read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                imports = [node.module or ""]
            else:
                continue
            assert not {name.split(".")[0] for name in imports} & {
                "policyengine",
                "policyengine_uk",
                "policyengine_core",
                "subprocess",
            }
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                assert node.func.id not in {"eval", "exec", "__import__"}


def test_no_discovery_job_uses_a_cache():
    for job in workflow()["jobs"].values():
        for step in job["steps"]:
            action = step.get("uses", "")
            assert not action.startswith("actions/cache")
            if action.startswith("astral-sh/setup-uv"):
                assert step["with"]["enable-cache"] is False


def git(directory, *arguments):
    return subprocess.run(
        ["git", "-C", str(directory), *arguments],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def released_request(version="6.6.0", *, attempt=1):
    request = copy.deepcopy(
        json.loads(
            (
                ROOT / "tests/fixtures/uk_replay/qualification_request_golden.json"
            ).read_text()
        )
    )
    request["kind"] = "released_bundle"
    request["attempt"] = attempt
    request["candidate"]["policyengine"].update(
        version=version, source={"pypi": {"wheel_sha256": "a" * 64}}
    )
    bundle = request["candidate"]["expected_release_bundle"]
    bundle.update(bundle_id=f"uk-{version}", policyengine_version=version)
    request["requested_by"] = {
        "repository": "PolicyEngine/policyengine-scorecard",
        "commit": "b" * 40,
        "trigger": "discovery test",
    }
    interface.validate_request(request)
    return request


@pytest.fixture
def enqueue_runner(tmp_path):
    """Use real state commits and pushes without creating any environment."""
    seed = tmp_path / "seed"
    seed.mkdir()
    git(seed, "init", "-q", "-b", "main")
    git(seed, "config", "user.name", "Test")
    git(seed, "config", "user.email", "test@example.org")
    shutil.copytree(
        ROOT / "pipeline",
        seed / "pipeline",
        ignore=shutil.ignore_patterns("__pycache__"),
    )
    shutil.copytree(ROOT / ".github/scripts", seed / ".github/scripts")
    shutil.copytree(ROOT / "docs/uk_replay/schemas", seed / "docs/uk_replay/schemas")
    git(seed, "add", ".")
    git(seed, "commit", "-qm", "Receiver code")
    git(seed, "switch", "--orphan", "replay-state")
    git(seed, "commit", "--allow-empty", "-qm", "Queue")
    remote = tmp_path / "remote.git"
    subprocess.run(["git", "clone", "-q", "--bare", str(seed), str(remote)], check=True)
    tools = tmp_path / "bin"
    tools.mkdir()
    uv = tools / "uv"
    uv.write_text(
        f"#!{sys.executable}\n"
        "import os, sys\n"
        "args = sys.argv[1:]\n"
        "assert args[0] == 'run' and 'python' in args, args\n"
        "assert 'venv' not in args and 'pip' not in args, args\n"
        f"os.execv({sys.executable!r}, [{sys.executable!r}, *args[args.index('python') + 1:]])\n"
    )
    uv.chmod(0o755)
    (tools / "python3").symlink_to(sys.executable)
    sequence = 0

    def create(*requests):
        nonlocal sequence
        sequence += 1
        runner = tmp_path / f"runner-{sequence}"
        subprocess.run(
            ["git", "clone", "-q", "--branch", "main", str(remote), str(runner)],
            check=True,
        )
        artifact = runner / "discovery"
        (artifact / "requests").mkdir(parents=True)
        (artifact / "skipped").mkdir()
        for request in requests:
            (
                artifact / "requests" / f"{interface.request_id(request)}.json"
            ).write_text(json.dumps(request))
        runner_temp = runner / "tmp"
        runner_temp.mkdir()
        env = {
            **os.environ,
            "PATH": f"{tools}:{os.environ['PATH']}",
            "PYTHONPATH": ".",
            "PYTHONDONTWRITEBYTECODE": "1",
            "STATE_BRANCH": "replay-state",
            "RUNNER_TEMP": str(runner_temp),
            "RUN_URL": RUN_URL,
        }
        for name in ("HUGGING_FACE_TOKEN", "HF_TOKEN", "HUGGINGFACE_HUB_TOKEN"):
            env.pop(name, None)

        def run(**overrides):
            return subprocess.run(
                ["bash", ".github/scripts/uk_replay_discover_enqueue.sh"],
                cwd=runner,
                env={**env, **overrides},
                capture_output=True,
                text=True,
                check=False,
            )

        return runner, artifact, run

    return seed, remote, create


@pytest.mark.parametrize("invalid", ["malformed_json", "schema_invalid"])
def test_enqueue_validates_the_whole_artifact_before_writing(enqueue_runner, invalid):
    _, remote, create = enqueue_runner
    valid = released_request()
    runner, artifact, run = create(valid)
    # A good request sorts first: validating while enqueueing would already
    # mutate the queue before discovering the second invalid request.
    path = next((artifact / "requests").glob("*.json"))
    bad = artifact / "requests" / ("f" * 64 + ".json")
    assert path.name < bad.name
    bad.write_text("{" if invalid == "malformed_json" else '{"kind":"released_bundle"}')
    before = git(remote, "rev-parse", "replay-state")
    result = run()
    assert result.returncode != 0, result.stdout + result.stderr
    assert git(remote, "rev-parse", "replay-state") == before
    assert not list((runner / "state" / "requests").glob("*/REQUEST.json"))


@pytest.mark.parametrize("invalid", ["extra_field", "bad_repo_id"])
def test_enqueue_schema_validation_refuses_a_digest_named_complete_request(
    enqueue_runner, invalid
):
    _, remote, create = enqueue_runner
    runner, artifact, run = create()
    request = released_request()
    if invalid == "extra_field":
        request["unexpected"] = "must be rejected by the closed schema"
    else:
        request["candidate"]["data"]["repo_id"] = "a/../b"
    # Every later guard check passes: released PyPI bundle, stable version,
    # unique version, and a filename matching its JCS digest. Only validation
    # against the vendored schema can refuse this request before queue.enqueue,
    # which intentionally records invalid requests for the receiver to reject.
    digest = interface.jcs_sha256(request)
    (artifact / "requests" / f"{digest}.json").write_text(json.dumps(request))
    before = git(remote, "rev-parse", "replay-state")
    result = run()
    assert result.returncode != 0, result.stdout + result.stderr
    assert "ValidationError" in result.stderr
    assert git(remote, "rev-parse", "replay-state") == before
    assert not list((runner / "state" / "requests").glob("*/REQUEST.json"))


@pytest.mark.parametrize(
    "invalid", ["extra_field", "bad_evidence", "bad_version", "long_reason"]
)
def test_enqueue_rejects_invalid_skip_metadata_before_any_request_write(
    enqueue_runner, invalid
):
    _, remote, create = enqueue_runner
    _, artifact, run = create(released_request())
    skipped = {
        "schema": "policyengine.uk-replay-discovery-skip/v1",
        "version": "6.7.0",
        "reason": "inconsistent immutable wheel metadata",
        "evidence_sha256": {"policyengine_wheel": "a" * 64},
    }
    if invalid == "extra_field":
        skipped["candidate_code"] = "print('untrusted')"
    elif invalid == "bad_evidence":
        skipped["evidence_sha256"] = {"policyengine_wheel": "not-a-digest"}
    elif invalid == "long_reason":
        skipped["reason"] = "x" * 2001
    else:
        skipped["version"] = "../outside"
    (artifact / "skipped/6.7.0.json").write_text(json.dumps(skipped))
    before = git(remote, "rev-parse", "replay-state")
    result = run()
    assert result.returncode != 0, result.stdout + result.stderr
    assert git(remote, "rev-parse", "replay-state") == before


@pytest.mark.parametrize("kind", ["request", "skip"])
def test_enqueue_refuses_metadata_with_the_wrong_filename(enqueue_runner, kind):
    _, remote, create = enqueue_runner
    runner, artifact, run = create(released_request())
    if kind == "request":
        path = next((artifact / "requests").glob("*.json"))
        wrong_digest = "0" * 64 if path.stem != "0" * 64 else "1" * 64
        path.rename(path.with_name(f"{wrong_digest}.json"))
        error = "request filename differs from its digest"
    else:
        skipped = {
            "schema": "policyengine.uk-replay-discovery-skip/v1",
            "version": "6.7.0",
            "reason": "immutable wheel mismatch",
            "evidence_sha256": {"policyengine_wheel": "a" * 64},
        }
        (artifact / "skipped/6.8.0.json").write_text(json.dumps(skipped))
        error = "skip filename differs from its release version"
    before = git(remote, "rev-parse", "replay-state")
    result = run()
    assert result.returncode != 0, result.stdout + result.stderr
    assert error in result.stderr
    assert git(remote, "rev-parse", "replay-state") == before
    assert not list((runner / "state" / "requests").glob("*/REQUEST.json"))


@pytest.mark.parametrize("kind", ["request", "skip"])
def test_enqueue_refuses_batches_above_each_per_run_bound(enqueue_runner, kind):
    _, remote, create = enqueue_runner
    requests = [released_request(f"6.6.{patch}") for patch in range(4)]
    runner, artifact, run = create(*(requests if kind == "request" else requests[:1]))
    if kind == "skip":
        for patch in range(31):
            skipped = {
                "schema": "policyengine.uk-replay-discovery-skip/v1",
                "version": f"6.7.{patch}",
                "reason": "immutable wheel mismatch",
                "evidence_sha256": {"policyengine_wheel": "a" * 64},
            }
            (artifact / "skipped" / f"6.7.{patch}.json").write_text(json.dumps(skipped))
    before = git(remote, "rev-parse", "replay-state")
    result = run()
    assert result.returncode != 0, result.stdout + result.stderr
    assert "per-run bounds" in result.stderr
    assert git(remote, "rev-parse", "replay-state") == before
    assert not list((runner / "state" / "requests").glob("*/REQUEST.json"))


def test_enqueue_refuses_a_prerelease_above_the_certified_floor(enqueue_runner):
    _, remote, create = enqueue_runner
    runner, _, run = create(released_request("6.6.0rc1"))
    before = git(remote, "rev-parse", "replay-state")
    result = run()
    assert result.returncode != 0, result.stdout + result.stderr
    assert "prerelease discovery version: 6.6.0rc1" in result.stderr
    assert git(remote, "rev-parse", "replay-state") == before
    assert not list((runner / "state" / "requests").glob("*/REQUEST.json"))


@pytest.mark.parametrize("collision", ["two_requests", "request_and_skip"])
def test_enqueue_refuses_a_batch_naming_one_version_twice(enqueue_runner, collision):
    # Review of 2043fa0: duplicate versions inside one batch are refused
    # whole, before any write.
    _, remote, create = enqueue_runner
    if collision == "two_requests":
        runner, _, run = create(
            released_request("6.6.0"), released_request("6.6.0", attempt=2)
        )
    else:
        runner, artifact, run = create(released_request("6.6.0"))
        (artifact / "skipped/6.6.0.json").write_text(
            json.dumps(
                {
                    "schema": "policyengine.uk-replay-discovery-skip/v1",
                    "version": "6.6.0",
                    "reason": "inconsistent immutable wheel metadata",
                    "evidence_sha256": {"policyengine_wheel": "a" * 64},
                }
            )
        )
    before = git(remote, "rev-parse", "replay-state")
    result = run()
    assert result.returncode != 0, result.stdout + result.stderr
    assert "duplicate or prerelease discovery version: 6.6.0" in result.stderr
    assert git(remote, "rev-parse", "replay-state") == before
    assert not list((runner / "state" / "requests").glob("*/REQUEST.json"))


@pytest.mark.parametrize("refused", ["binary", "symlink"])
def test_enqueue_applies_the_receivers_output_guard(enqueue_runner, refused):
    _, remote, create = enqueue_runner
    runner, artifact, run = create(released_request())
    if refused == "binary":
        (artifact / "dataset.h5").write_bytes(b"\x89HDF")
    else:
        outside = runner / "outside.json"
        outside.write_text("{}")
        (artifact / "linked.json").symlink_to(outside)
    before = git(remote, "rev-parse", "replay-state")
    result = run()
    assert result.returncode != 0, result.stdout + result.stderr
    assert "refusing to publish" in result.stdout
    assert git(remote, "rev-parse", "replay-state") == before


def test_enqueue_rejects_a_schema_valid_candidate_request(enqueue_runner):
    _, remote, create = enqueue_runner
    candidate = released_request()
    candidate["kind"] = "candidate"
    interface.validate_request(candidate)
    _, _, run = create(candidate)
    before = git(remote, "rev-parse", "replay-state")
    result = run()
    assert result.returncode != 0, result.stdout + result.stderr
    assert "only released PyPI bundles" in result.stderr
    assert git(remote, "rev-parse", "replay-state") == before


def test_enqueue_records_skip_only_metadata_idempotently(enqueue_runner):
    _, remote, create = enqueue_runner
    skipped = {
        "schema": "policyengine.uk-replay-discovery-skip/v1",
        "version": "6.7.0",
        "reason": "inconsistent immutable wheel metadata",
        "evidence_sha256": {"policyengine_wheel": "a" * 64},
    }
    _, artifact, run = create()
    (artifact / "skipped/6.7.0.json").write_text(json.dumps(skipped))
    result = run()
    assert result.returncode == 0, result.stdout + result.stderr
    assert (
        json.loads(git(remote, "show", "replay-state:discovery/skipped/6.7.0.json"))
        == skipped
    )
    before = git(remote, "rev-parse", "replay-state")
    _, next_artifact, run_again = create()
    (next_artifact / "skipped/6.7.0.json").write_text(json.dumps(skipped))
    result = run_again()
    assert result.returncode == 0, result.stdout + result.stderr
    assert git(remote, "rev-parse", "replay-state") == before


def test_enqueue_valid_requests_is_idempotent(enqueue_runner):
    _, remote, create = enqueue_runner
    request = released_request()
    request_id = interface.request_id(request)
    _, _, run = create(request)
    result = run()
    assert result.returncode == 0, result.stdout + result.stderr
    stored = json.loads(
        git(remote, "show", f"replay-state:requests/{request_id}/REQUEST.json")
    )
    status = json.loads(
        git(remote, "show", f"replay-state:requests/{request_id}/STATUS.json")
    )
    assert stored == request
    assert status["status"] == "queued"
    assert len(status["history"]) == 1
    before = git(remote, "rev-parse", "replay-state")
    _, _, run_again = create(request)
    result = run_again()
    assert result.returncode == 0, result.stdout + result.stderr
    assert git(remote, "rev-parse", "replay-state") == before


@pytest.mark.parametrize(
    "status", ["queued", "running", "complete", "failed", "rejected"]
)
def test_enqueue_does_not_duplicate_a_release_already_in_the_queue(
    enqueue_runner, status
):
    seed, remote, create = enqueue_runner
    existing = released_request("6.5.0")
    existing_id, _ = queue.enqueue(
        seed, existing, run_url=RUN_URL, now="2026-10-16T00:00:00Z"
    )
    if status != "queued":
        queue.set_status(
            seed,
            existing_id,
            status,
            run_url=RUN_URL,
            now="2026-10-16T01:00:00Z",
            receipt_sha256="c" * 64 if status in queue.TERMINAL else None,
            receipt_commit="d" * 40 if status in queue.TERMINAL else None,
        )
    git(seed, "add", ".")
    git(seed, "commit", "-qm", "Already dispatched 6.5.0")
    git(seed, "push", "-q", str(remote), "HEAD:replay-state")
    before = git(remote, "rev-parse", "replay-state")
    duplicate = released_request("6.5.0", attempt=2)
    _, _, run = create(duplicate)
    result = run()
    assert result.returncode == 0, result.stdout + result.stderr
    assert git(remote, "rev-parse", "replay-state") == before
    assert (
        json.loads(
            git(remote, "show", f"replay-state:requests/{existing_id}/STATUS.json")
        )["status"]
        == status
    )


def test_a_pre_promotion_candidate_request_does_not_cover_the_release(enqueue_runner):
    # W4, 2026-10-16: the candidate qualification pins the candidate's wheels;
    # the released wheel is rebuilt, so its discovered request is queued.
    seed, remote, create = enqueue_runner
    candidate = released_request("6.5.0")
    candidate["kind"] = "candidate"
    queue.enqueue(seed, candidate, run_url=RUN_URL, now="2026-10-16T00:00:00Z")
    git(seed, "add", ".")
    git(seed, "commit", "-qm", "W4 pre-promotion qualification")
    git(seed, "push", "-q", str(remote), "HEAD:replay-state")
    discovered = released_request("6.5.0", attempt=2)
    _, _, run = create(discovered)
    result = run()
    assert result.returncode == 0, result.stdout + result.stderr
    stored = git(remote, "ls-tree", "-r", "--name-only", "replay-state").splitlines()
    assert f"requests/{interface.request_id(discovered)}/REQUEST.json" in stored


def test_enqueue_rechecks_versions_after_a_concurrent_dispatch(enqueue_runner):
    seed, remote, create = enqueue_runner
    discovered = released_request("6.5.0", attempt=2)
    later = released_request("6.6.0")
    runner, _, run = create(discovered, later)
    # W4's released_bundle dispatch for 6.5.0 lands mid-discovery.
    incoming = released_request("6.5.0")
    incoming_id, _ = queue.enqueue(
        seed, incoming, run_url=RUN_URL, now="2026-10-16T00:00:00Z"
    )
    git(seed, "add", ".")
    git(seed, "commit", "-qm", "W4 dispatch during discovery")
    # Publish W4's distinct request immediately before the discovery job's
    # first real push. A normal rebase could succeed and duplicate 6.5.0;
    # the writer must reset and deduplicate against the new remote state.
    real_git = shutil.which("git")
    wrapper = remote.parent / "bin/git"
    wrapper.write_text(
        f"#!{sys.executable}\n"
        "import os, subprocess, sys\n"
        "from pathlib import Path\n"
        "args = sys.argv[1:]\n"
        "marker = Path(os.environ['DISPATCH_PUSH_MARKER'])\n"
        "if 'push' in args and not marker.exists():\n"
        "    marker.touch()\n"
        f"    subprocess.run([{real_git!r}, '-C', {str(seed)!r}, 'push', '-q', {str(remote)!r}, 'HEAD:replay-state'], check=True)\n"
        f"os.execv({real_git!r}, [{real_git!r}, *args])\n"
    )
    wrapper.chmod(0o755)
    marker = runner / "concurrent-dispatch-pushed"
    result = run(DISPATCH_PUSH_MARKER=str(marker))
    assert result.returncode == 0, result.stdout + result.stderr
    assert marker.exists()
    assert "discovery enqueue raced" in result.stdout
    stored = git(remote, "ls-tree", "-r", "--name-only", "replay-state").splitlines()
    request_paths = [path for path in stored if path.endswith("/REQUEST.json")]
    assert sorted(request_paths) == sorted(
        [
            f"requests/{incoming_id}/REQUEST.json",
            f"requests/{interface.request_id(later)}/REQUEST.json",
        ]
    )
    assert (
        json.loads(
            git(remote, "show", f"replay-state:requests/{incoming_id}/REQUEST.json")
        )
        == incoming
    )
