"""Queue bounds and control-job behavior against local git repositories."""

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
RUN = "https://github.com/PolicyEngine/policyengine-scorecard/actions/runs/1"


def git(directory, *args):
    return subprocess.run(
        ["git", "-C", str(directory), *args],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def local_state(tmp_path):
    state = tmp_path / "state"
    state.mkdir()
    git(state, "init", "-q")
    git(state, "config", "user.name", "Test")
    git(state, "config", "user.email", "test@example.org")
    return state


def test_fourth_stale_attempt_is_terminal_with_a_committed_failed_receipt(tmp_path):
    state = local_state(tmp_path)
    request_id, _ = queue.enqueue(
        state, {"invalid": "request"}, run_url=RUN, now="2026-10-01T00:00:00Z"
    )
    for day in (1, 2, 3):
        queue.set_status(
            state,
            request_id,
            "running",
            run_url=RUN,
            now=f"2026-10-0{day}T01:00:00Z",
        )
    assert queue.pending(state, now="2026-10-04T09:00:00Z") == [request_id]
    with pytest.raises(ValueError, match="exhausted its 3 running attempts"):
        queue.set_status(
            state,
            request_id,
            "running",
            run_url=RUN,
            now="2026-10-04T09:00:00Z",
        )
    stale_results = state / "requests" / request_id / "results"
    stale_results.mkdir()
    (stale_results / "old-attempt.json").write_text("{}")
    receipt = queue.write_failure_receipt(
        state,
        request_id,
        code="attempt_limit_exceeded",
        detail="The request exhausted three running attempts",
    )
    git(state, "add", ".")
    git(state, "commit", "-qm", "Failure receipt")
    receipt_commit = git(state, "rev-parse", "HEAD")
    status = queue.set_status(
        state,
        request_id,
        "failed",
        run_url=RUN,
        now="2026-10-04T09:00:00Z",
        receipt_sha256=receipt["receipt_sha256"],
        receipt_commit=receipt_commit,
    )
    assert not stale_results.exists()
    interface.validate(receipt, interface.RECEIPT_SCHEMA_ID)
    interface.validate(status, interface.STATUS_SCHEMA_ID)
    assert queue.running_attempts(status) == 3
    assert queue.pending(state, now="2026-10-05T09:00:00Z") == []
    committed = json.loads(
        git(
            state, "show", f"{receipt_commit}:requests/{request_id}/REPLAY_RECEIPT.json"
        )
    )
    assert committed == receipt


@pytest.mark.parametrize("exhaust_push_retries", [False, True])
def test_enqueue_reapplies_after_a_real_concurrent_git_conflict(
    tmp_path, exhaust_push_retries
):
    """The first push loses to another enqueue of exactly the same request."""
    seed = tmp_path / "seed"
    seed.mkdir()
    git(seed, "init", "-q", "-b", "main")
    git(seed, "config", "user.name", "Test")
    git(seed, "config", "user.email", "test@example.org")
    for relative in (
        "pipeline/uk_replay_queue.py",
        "pipeline/uk_replay_interface.py",
        ".github/scripts/uk_replay_state.sh",
        ".github/scripts/uk_replay_enqueue.sh",
    ):
        destination = seed / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, destination)
    shutil.copytree(ROOT / "docs/uk_replay/schemas", seed / "docs/uk_replay/schemas")
    git(seed, "add", ".")
    git(seed, "commit", "-qm", "Code")
    git(seed, "switch", "--orphan", "replay-state")
    git(seed, "commit", "--allow-empty", "-qm", "Queue")
    remote = tmp_path / "remote.git"
    subprocess.run(["git", "clone", "-q", "--bare", str(seed), str(remote)], check=True)
    runner, competitor = tmp_path / "runner", tmp_path / "competitor"
    for path in (runner, competitor):
        subprocess.run(["git", "clone", "-q", str(remote), str(path)], check=True)
        git(path, "config", "user.name", "Test")
        git(path, "config", "user.email", "test@example.org")
    git(runner, "switch", "-q", "main")
    request = {"invalid": "same received request"}
    request_file = tmp_path / "request.json"
    request_file.write_text(json.dumps(request))
    request_id, _ = queue.enqueue(
        competitor, request, run_url=RUN, now="2026-10-10T00:00:00Z"
    )
    git(competitor, "add", ".")
    git(competitor, "commit", "-qm", "Concurrent queue")
    competing_commit = git(competitor, "rev-parse", "HEAD")
    # A wrapper injects the competing push at the first push from the script.
    # All fetches, rebases, conflicts and subsequent pushes are real local git.
    tools = tmp_path / "bin"
    tools.mkdir()
    real_git = shutil.which("git")
    wrapper = tools / "git"
    wrapper.write_text(
        f"#!{sys.executable}\n"
        "import os, subprocess, sys\n"
        "from pathlib import Path\n"
        "args = sys.argv[1:]\n"
        "marker = Path(os.environ['PUSH_MARKER'])\n"
        "if 'push' in args and not marker.exists():\n"
        "    marker.touch()\n"
        f"    subprocess.run([{real_git!r}, '-C', os.environ['COMPETITOR'], 'push', '-q', 'origin', 'HEAD:replay-state'], check=True)\n"
        "if 'push' in args and os.environ['REJECT_PUSHES'] == '1':\n"
        "    sys.exit(1)\n"
        f"os.execv({real_git!r}, [{real_git!r}, *args])\n"
    )
    wrapper.chmod(0o755)
    uv = tools / "uv"
    uv.write_text(
        f"#!{sys.executable}\nimport os, sys\n"
        "args = sys.argv[1:]\n"
        f"os.execv({sys.executable!r}, [{sys.executable!r}, *args[args.index('python') + 1:]])\n"
    )
    uv.chmod(0o755)
    sleep = tools / "sleep"
    sleep.write_text('#!/usr/bin/env bash\nprintf "%s\\n" "$1" >> "$BACKOFF_LOG"\n')
    sleep.chmod(0o755)
    environment = {
        **os.environ,
        "PATH": f"{tools}:{os.environ['PATH']}",
        "PYTHONPATH": str(runner),
        "STATE_BRANCH": "replay-state",
        "REQUEST_FILE": str(request_file),
        "RUNNER_TEMP": str(tmp_path),
        "RUN_URL": RUN,
        "COMPETITOR": str(competitor),
        "PUSH_MARKER": str(tmp_path / "pushed"),
        "BACKOFF_LOG": str(tmp_path / "backoff"),
        "REJECT_PUSHES": "1" if exhaust_push_retries else "0",
    }
    result = subprocess.run(
        ["bash", ".github/scripts/uk_replay_enqueue.sh"],
        cwd=runner,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    if exhaust_push_retries:
        assert result.returncode == 1
        assert (
            "could not enqueue and push the request after five attempts"
            in result.stderr
        )
        assert (tmp_path / "backoff").read_text() == "1\n2\n3\n4\n5\n"
    else:
        assert result.returncode == 0
        assert (tmp_path / "backoff").read_text() == "1\n"
    assert "enqueue conflicted; reapplying" in result.stdout
    assert git(remote, "rev-parse", "replay-state") == competing_commit
    status = json.loads(
        git(remote, "show", f"replay-state:requests/{request_id}/STATUS.json")
    )
    interface.validate(status, interface.STATUS_SCHEMA_ID)
    assert len(status["history"]) == 1
    assert status["history"][0]["at"] == "2026-10-10T00:00:00Z"
    assert git(runner / "state", "status", "--porcelain") == ""


def test_candidate_job_has_read_permission_and_no_dataset_token_or_credentials():
    workflow = yaml.safe_load((ROOT / ".github/workflows/uk-replay.yml").read_text())
    candidate = workflow["jobs"]["run"]
    assert candidate["permissions"] == {"contents": "read"}
    checkout = next(
        step for step in candidate["steps"] if step.get("uses") == "actions/checkout@v4"
    )
    assert checkout["with"]["persist-credentials"] is False
    # The read-only data token reaches only the dataset fetch, which runs
    # before any candidate code and only on dispatches (never on a schedule
    # tick or a pull request), and only from the scoped org secret.
    with_token = [step for step in candidate["steps"] if "secrets." in json.dumps(step)]
    assert [step["name"] for step in with_token] == [
        "Fetch and verify the dataset before any candidate code"
    ]
    (fetch,) = with_token
    assert fetch["env"] == {
        "HUGGING_FACE_TOKEN": "${{ secrets.PE_UK_PRIVATE_HF_READ_TOKEN }}"
    }
    assert fetch["if"] == (
        'contains(fromJSON(\'["workflow_dispatch", "repository_dispatch"]\'), '
        "github.event_name)"
    )
    # Then a private copy for the unprivileged account, the run as that
    # account, every candidate process killed and the output taken back, the
    # guard, and the upload only when the guard passed.
    steps = [step.get("name") for step in candidate["steps"]]
    order = [
        fetch["name"],
        "Hand a private copy to the unprivileged candidate account",
        "Run the candidate and preserve logs and outcome",
        "Stop every candidate process and take its output back",
        "Nothing household-level leaves the runner",
        "Upload the receipt and results for the recorder",
    ]
    assert [steps.index(name) for name in order] == sorted(
        steps.index(name) for name in order
    )
    by_name = {step.get("name"): step for step in candidate["steps"]}
    assert by_name[order[1]]["run"] == "bash .github/scripts/uk_replay_sandbox.sh setup"
    assert by_name[order[2]]["run"] == "bash .github/scripts/uk_replay_sandbox.sh run"
    assert by_name[order[3]] == {
        "name": order[3],
        "if": "always()",
        "run": "bash .github/scripts/uk_replay_sandbox.sh collect",
    }
    assert "huggingface_hub==2.2.0" in fetch["run"]
    rest = {k: v for k, v in candidate.items() if k != "steps"}
    assert "secrets." not in json.dumps(rest)
    assert workflow["jobs"]["record"]["permissions"] == {
        "contents": "write",
        "actions": "write",
    }
    assert (
        "format('uk-replay-enqueue-{0}', github.run_id)"
        in workflow["concurrency"]["group"]
    )
    assert workflow["concurrency"]["cancel-in-progress"] is False
    for job in workflow["jobs"].values():
        for step in job["steps"]:
            assert "${{" not in step.get("run", "")


def test_ci_checks_untracked_regeneration_and_announces_skipped_real_replay():
    workflow = yaml.safe_load((ROOT / ".github/workflows/ci.yml").read_text())
    steps = workflow["jobs"]["python"]["steps"]
    build = next(step for step in steps if "build1.json" in step.get("run", ""))
    assert ' > "$RUNNER_TEMP/build1.json"' in build["run"]
    assert ' > "$RUNNER_TEMP/build2.json"' in build["run"]
    regeneration_index = next(
        i
        for i, step in enumerate(steps)
        if step.get("name") == "Replay namespaces regenerate and seals hold"
    )
    assert "git status --porcelain" in steps[regeneration_index + 1]["run"]
    fetch = next(
        step
        for step in workflow["jobs"]["replay-engine"]["steps"]
        if step.get("name") == "Fetch the certified dataset for the real replay"
    )
    assert '"$RESULT_ROOT/REPLAY_RECEIPT.json"' in fetch["run"]
    assert '"$RESULT_ROOT/NAMESPACE_MANIFEST.json"' in fetch["run"]
    assert fetch["run"].count("nothing was replayed") == 2


def test_nonzero_candidate_exit_keeps_logs_and_uploadable_outcome(tmp_path):
    scripts = tmp_path / ".github/scripts"
    scripts.mkdir(parents=True)
    shutil.copyfile(
        ROOT / ".github/scripts/uk_replay_drain.sh", scripts / "uk_replay_drain.sh"
    )
    tools = tmp_path / "bin"
    tools.mkdir()
    uv = tools / "uv"
    uv.write_text(
        f"#!{sys.executable}\n"
        "import json, sys\n"
        "from pathlib import Path\n"
        "args = sys.argv[1:]\n"
        "print('corpus log before a crash', flush=True)\n"
        "Path(args[args.index('--result-file') + 1]).write_text(json.dumps({'status': 'failed', 'receipt_sha256': 'a' * 64}))\n"
        "sys.exit(17)\n"
    )
    uv.chmod(0o755)
    result = subprocess.run(
        ["bash", ".github/scripts/uk_replay_drain.sh"],
        cwd=tmp_path,
        env={
            **os.environ,
            "PATH": f"{tools}:{os.environ['PATH']}",
            "REQUEST_ID": "b" * 64,
            "RUNNER_TEMP": str(tmp_path),
            "REPLAY_RUNNER": "test runner",
        },
        capture_output=True,
        text=True,
        check=True,
    )
    assert "corpus log before a crash" in result.stdout
    assert "run-request exited 17" in result.stdout
    assert (tmp_path / "output/run-exit.txt").read_text() == "17\n"
    assert json.loads((tmp_path / "output/outcome.json").read_text()) == {
        "status": "failed",
        "receipt_sha256": "a" * 64,
    }


def control_runner(tmp_path, seed):
    """A code checkout and a queue remote, both temporary and entirely local."""
    git(seed, "branch", "-M", "replay-state")
    remote = tmp_path / "remote.git"
    subprocess.run(["git", "clone", "-q", "--bare", str(seed), str(remote)], check=True)
    runner = tmp_path / "runner"
    subprocess.run(["git", "clone", "-q", str(remote), str(runner)], check=True)
    git(runner, "switch", "-q", "--detach")
    for relative in ("pipeline/uk_replay_queue.py", "pipeline/uk_replay_interface.py"):
        destination = runner / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, destination)
    shutil.copytree(ROOT / "docs/uk_replay/schemas", runner / "docs/uk_replay/schemas")
    scripts = runner / ".github/scripts"
    scripts.mkdir(parents=True)
    for path in (ROOT / ".github/scripts").glob("uk_replay_*.sh"):
        shutil.copyfile(path, scripts / path.name)
    tools = tmp_path / "bin"
    tools.mkdir()
    uv = tools / "uv"
    uv.write_text(
        f"#!{sys.executable}\nimport os, sys\nargs = sys.argv[1:]\n"
        f"os.execv({sys.executable!r}, [{sys.executable!r}, *args[args.index('python') + 1:]])\n"
    )
    uv.chmod(0o755)
    gh = tools / "gh"
    gh.write_text(
        "#!/usr/bin/env bash\necho 'unexpected dispatch in an empty local queue' >&2\nexit 93\n"
    )
    gh.chmod(0o755)
    environment = {
        **os.environ,
        "PATH": f"{tools}:{os.environ['PATH']}",
        "PYTHONPATH": str(runner),
        "STATE_BRANCH": "replay-state",
        "RUNNER_TEMP": str(tmp_path),
        "RUN_URL": RUN,
        "GITHUB_OUTPUT": str(tmp_path / "job-output.txt"),
    }
    return runner, remote, environment


def test_prepare_terminalizes_the_fourth_stale_attempt_before_selecting_again(tmp_path):
    seed = local_state(tmp_path)
    request_id, _ = queue.enqueue(
        seed, {"invalid": "request"}, run_url=RUN, now="2020-01-01T00:00:00Z"
    )
    for day in (1, 2, 3):
        queue.set_status(
            seed, request_id, "running", run_url=RUN, now=f"2020-01-0{day}T01:00:00Z"
        )
    git(seed, "add", ".")
    git(seed, "commit", "-qm", "Three stale attempts")
    runner, remote, environment = control_runner(tmp_path, seed)
    subprocess.run(
        ["bash", ".github/scripts/uk_replay_prepare.sh"],
        cwd=runner,
        env=environment,
        check=True,
        capture_output=True,
        text=True,
    )
    status = json.loads(
        git(remote, "show", f"replay-state:requests/{request_id}/STATUS.json")
    )
    interface.validate(status, interface.STATUS_SCHEMA_ID)
    assert status["status"] == "failed"
    assert queue.running_attempts(status) == 3
    receipt_commit = status["receipt_commit"]
    receipt = json.loads(
        git(
            remote,
            "show",
            f"{receipt_commit}:requests/{request_id}/REPLAY_RECEIPT.json",
        )
    )
    interface.validate(receipt, interface.RECEIPT_SCHEMA_ID)
    assert receipt["receipt_sha256"] == status["receipt_sha256"]
    assert receipt["integrity"]["failures"][0]["code"] == "attempt_limit_exceeded"
    prior_status = json.loads(
        git(remote, "show", f"{receipt_commit}:requests/{request_id}/STATUS.json")
    )
    assert prior_status["status"] == "running"
    assert (tmp_path / "job-output.txt").read_text() == "request_id=\n"


@pytest.mark.parametrize("invalid_outcome", [False, True])
def test_recorder_handles_missing_or_invalid_run_artifact_and_clears_stale_results(
    tmp_path, invalid_outcome
):
    seed = local_state(tmp_path)
    request_id, _ = queue.enqueue(
        seed, {"invalid": "request"}, run_url=RUN, now="2020-01-01T00:00:00Z"
    )
    queue.set_status(
        seed, request_id, "running", run_url=RUN, now="2020-01-01T01:00:00Z"
    )
    results = seed / "requests" / request_id / "results"
    results.mkdir()
    (results / "earlier-attempt.json").write_text("{}")
    git(seed, "add", ".")
    git(seed, "commit", "-qm", "Running request with stale results")
    runner, remote, environment = control_runner(tmp_path, seed)
    if invalid_outcome:
        output = runner / "output"
        output.mkdir()
        (output / "outcome.json").write_text(
            '{"status":"complete","receipt_sha256":"bad"}'
        )
    subprocess.run(
        ["bash", ".github/scripts/uk_replay_record.sh"],
        cwd=runner,
        env={**environment, "REQUEST_ID": request_id},
        check=True,
        capture_output=True,
        text=True,
    )
    status = json.loads(
        git(remote, "show", f"replay-state:requests/{request_id}/STATUS.json")
    )
    interface.validate(status, interface.STATUS_SCHEMA_ID)
    assert status["status"] == "failed"
    receipt = json.loads(
        git(
            remote,
            "show",
            f"{status['receipt_commit']}:requests/{request_id}/REPLAY_RECEIPT.json",
        )
    )
    interface.validate(receipt, interface.RECEIPT_SCHEMA_ID)
    assert receipt["receipt_sha256"] == status["receipt_sha256"]
    assert receipt["integrity"]["failures"][0]["code"] == "run_artifact_failed"
    assert (
        git(
            remote,
            "ls-tree",
            "-r",
            "--name-only",
            "replay-state",
            f"requests/{request_id}/results",
        )
        == ""
    )
    prior_status = json.loads(
        git(
            remote,
            "show",
            f"{status['receipt_commit']}:requests/{request_id}/STATUS.json",
        )
    )
    assert prior_status["status"] == "running"


def test_recorder_replaces_an_earlier_attempts_results_with_this_runs(tmp_path):
    # Review of 176e974: the success path, not only the failure receipt,
    # must leave no file of an earlier attempt beside this run's results.
    seed = local_state(tmp_path)
    request_id, _ = queue.enqueue(
        seed, {"invalid": "request"}, run_url=RUN, now="2020-01-01T00:00:00Z"
    )
    queue.set_status(
        seed, request_id, "running", run_url=RUN, now="2020-01-01T01:00:00Z"
    )
    stale = seed / "requests" / request_id / "results"
    stale.mkdir()
    (stale / "earlier-attempt.json").write_text("{}")
    git(seed, "add", ".")
    git(seed, "commit", "-qm", "Running request with stale results")
    runner, remote, environment = control_runner(tmp_path, seed)
    scratch = tmp_path / "scratch"
    receipt = queue.write_failure_receipt(
        scratch, request_id, code="event_run_failed", detail="this run's outcome"
    )
    uploaded = runner / "output" / "state" / "requests" / request_id
    (uploaded / "results").mkdir(parents=True)
    (uploaded / "results" / "this-run.json").write_text("{}")
    (uploaded / "REPLAY_RECEIPT.json").write_text(json.dumps(receipt))
    (runner / "output" / "outcome.json").write_text(
        json.dumps(
            {"status": receipt["status"], "receipt_sha256": receipt["receipt_sha256"]}
        )
    )
    subprocess.run(
        ["bash", ".github/scripts/uk_replay_record.sh"],
        cwd=runner,
        env={**environment, "REQUEST_ID": request_id},
        check=True,
        capture_output=True,
        text=True,
    )
    status = json.loads(
        git(remote, "show", f"replay-state:requests/{request_id}/STATUS.json")
    )
    assert status["receipt_sha256"] == receipt["receipt_sha256"]
    assert git(
        remote,
        "ls-tree",
        "-r",
        "--name-only",
        "replay-state",
        f"requests/{request_id}/results",
    ).splitlines() == [f"requests/{request_id}/results/this-run.json"]


def test_empty_pending_cli_has_no_output_for_redispatch_decision(tmp_path, capsys):
    assert (
        queue.main(
            ["pending", "--state", str(tmp_path), "--now", "2026-10-11T12:00:00Z"]
        )
        == 0
    )
    assert capsys.readouterr().out == ""


@pytest.mark.parametrize("regeneration", ["identical", "drift", "untracked"])
def test_ci_regeneration_preserves_sealed_source_and_detects_every_changed_byte(
    tmp_path, regeneration
):
    source = tmp_path / "source"
    source.mkdir()
    git(source, "init", "-q", "-b", "main")
    git(source, "config", "user.name", "Test")
    git(source, "config", "user.email", "test@example.org")
    namespace = Path("results/uk/replays/candidate")
    original = {
        namespace / "REPLAY_RECEIPT.json": b'{"receipt":"original"}\n',
        namespace / "NAMESPACE_MANIFEST.json": b'{"manifest":"original"}\n',
        namespace / "event/RUN_MANIFEST.json": b"{}\n",
        namespace / "event/STAGED.jsonl": b'{"value":"original"}\n',
        namespace / "SUMMARY.md": b"original summary\n",
    }
    for relative, contents in original.items():
        path = source / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(contents)
    script = source / ".github/scripts/uk_replay_regenerate.sh"
    script.parent.mkdir(parents=True)
    shutil.copyfile(ROOT / ".github/scripts/uk_replay_regenerate.sh", script)
    git(source, "add", ".")
    git(source, "commit", "-qm", "Sealed namespace")
    tools = tmp_path / "bin"
    tools.mkdir()
    uv = tools / "uv"
    uv.write_text(
        f"#!{sys.executable}\n"
        "import os, sys\nfrom pathlib import Path\n"
        "args = sys.argv[1:]\n"
        "namespace = Path('results/uk/replays/candidate')\n"
        "if 'verify-sealed' in args:\n"
        "    assert Path.cwd() == Path(os.environ['SOURCE'])\n"
        "    assert (namespace / 'REPLAY_RECEIPT.json').exists()\n"
        "    assert (namespace / 'NAMESPACE_MANIFEST.json').exists()\n"
        "else:\n"
        "    assert Path.cwd() == Path(os.environ['RUNNER_TEMP']) / 'replay-regeneration'\n"
        "    assert os.environ['PYTHONPATH'] == '.'\n"
        "    assert not (namespace / 'REPLAY_RECEIPT.json').exists()\n"
        "    assert not (namespace / 'NAMESPACE_MANIFEST.json').exists()\n"
        "    if 'pipeline/stage_uk_event.py' in args:\n"
        "        artifact = args[args.index('--artifact-dir') + 1]\n"
        "        assert artifact.startswith('results/uk/replays/candidate/')\n"
        "        assert not Path(artifact).is_absolute()\n"
        "        if os.environ['REGENERATION'] == 'drift':\n"
        "            (namespace / 'event/STAGED.jsonl').write_text('drift\\n')\n"
        "        if os.environ['REGENERATION'] == 'untracked':\n"
        "            (namespace / 'event/NEW.json').write_text('{}\\n')\n"
    )
    uv.chmod(0o755)
    result = subprocess.run(
        ["bash", ".github/scripts/uk_replay_regenerate.sh"],
        cwd=source,
        env={
            **os.environ,
            "PATH": f"{tools}:{os.environ['PATH']}",
            "PYTHONPATH": ".",
            "RUNNER_TEMP": str(tmp_path),
            "SOURCE": str(source),
            "REGENERATION": regeneration,
        },
        capture_output=True,
        text=True,
    )
    assert result.returncode == (0 if regeneration == "identical" else 1), result.stderr
    if regeneration != "identical":
        assert (
            "replay regeneration changed committed bytes or created untracked files"
            in result.stderr
        )
        assert (
            "STAGED.jsonl" in result.stdout
            if regeneration == "drift"
            else "NEW.json" in result.stdout
        )
    for relative, contents in original.items():
        assert (source / relative).read_bytes() == contents
    assert git(source, "status", "--porcelain") == ""
    fresh = tmp_path / "replay-regeneration"
    for name in ("REPLAY_RECEIPT.json", "NAMESPACE_MANIFEST.json"):
        assert (fresh / namespace / name).read_bytes() == original[namespace / name]
    assert (
        git(fresh, "status", "--porcelain") == ""
        if regeneration == "identical"
        else git(fresh, "status", "--porcelain") != ""
    )


GUARD = ROOT / ".github/scripts/uk_replay_output_guard.py"


def guard(directory: Path) -> subprocess.CompletedProcess:
    # As the workflow runs it: isolated, standard library only.
    return subprocess.run(
        [sys.executable, "-I", str(GUARD), str(directory)],
        capture_output=True,
        text=True,
    )


def guarded_output(tmp_path):
    output = tmp_path / "output"
    results = output / "state" / "requests" / ("a" * 64) / "results" / "ab2024"
    results.mkdir(parents=True)
    (results / "COMPARISON.json").write_text('{"rows": []}')
    (results / "STAGED.jsonl").write_text('{"row": 1}\n\n{"row": 2}\n')
    (results / "COMPARISON.csv").write_text("a,b\n1,2\n")
    (results / "SUMMARY.md").write_text("# Summary\n")
    (output / "run-exit.txt").write_text("0\n")
    return output, results


def test_output_guard_allows_only_parsable_aggregates(tmp_path):
    # Scorecard is public (d1383): an allowlist, not a denylist. Every file
    # must be a regular file with an allowed extension whose bytes parse as
    # that format, under per-file and total caps.
    output, results = guarded_output(tmp_path)
    assert guard(output).returncode == 0, guard(output).stdout
    assert guard(tmp_path / "absent").returncode == 0
    refused = {
        "dataset.h5": b"\x89HDF",
        "people.parquet": b"PAR1",
        "frame.feather": b"ARROW1",
        "frame.pkl": b"\x80\x04",
        "no_extension": b"{}",
        "split.json": b"\x1f\x8b\x08\x00",  # gzip bytes renamed
        "broken.json": b'{"rows": [',
        "broken.jsonl": b'{"row": 1}\nnot json\n',
        "binary.csv": b"a,b\n\xff\xfe\n",
        "nul.md": b"# x\x00\n",
    }
    for name, data in refused.items():
        bad = results / name
        bad.write_bytes(data)
        result = guard(output)
        assert result.returncode == 1 and name in result.stdout, name
        bad.unlink()
    big = results / "artifact.json"
    big.write_text('"' + "x" * (10 * 1024 * 1024) + '"')
    assert guard(output).returncode == 1
    big.unlink()
    outside = tmp_path / "input.json"
    outside.write_text("{}")
    (results / "link.json").symlink_to(outside)
    result = guard(output)
    assert result.returncode == 1 and "not a regular file" in result.stdout
    (results / "link.json").unlink()
    os.mkfifo(results / "pipe.json")
    assert guard(output).returncode == 1
    (results / "pipe.json").unlink()
    assert guard(output).returncode == 0


def test_output_guard_caps_the_total(tmp_path):
    output, results = guarded_output(tmp_path)
    for index in range(12):  # 108 MiB in all, each under 10 MiB
        (results / f"part_{index}.json").write_text('"' + "x" * (9 * 1024 * 1024) + '"')
    result = guard(output)
    assert result.returncode == 1 and "in all" in result.stdout


def test_candidate_code_runs_as_an_unprivileged_account_with_nothing_inherited():
    script = (ROOT / ".github/scripts/uk_replay_sandbox.sh").read_text()
    # The account has no sudo; a check fails the job if it ever does.
    assert 'sudo useradd --create-home --shell /bin/bash "$CANDIDATE"' in script
    assert "not allowed to run sudo" in script
    # Its environment is built from nothing: no token, no runtime token, no
    # GITHUB_ENV or GITHUB_PATH, no uv cache directory from setup-uv.
    assert 'sudo -n -u "$CANDIDATE" env -i' in script
    assert "--preserve-env" not in script and "sudo -E" not in script
    assert "exec bash .github/scripts/uk_replay_drain.sh" in script
    # Nothing it starts outlives the run, and its output comes back as a
    # copy that keeps links as links, for the guard to refuse.
    assert 'sudo pkill -KILL -u "$CANDIDATE"' in script
    assert 'sudo cp -R --no-preserve=all "$COPY/output" output' in script
    result = subprocess.run(
        ["bash", "-n", str(ROOT / ".github/scripts/uk_replay_sandbox.sh")]
    )
    assert result.returncode == 0


def test_nothing_crosses_jobs_but_the_request_and_guarded_output():
    workflow = yaml.safe_load((ROOT / ".github/workflows/uk-replay.yml").read_text())
    uploads = [
        (name, step)
        for name, job in workflow["jobs"].items()
        for step in job["steps"]
        if step.get("uses", "").startswith("actions/upload-artifact")
    ]
    assert [(name, step["with"]["path"]) for name, step in uploads] == [
        ("prepare", "input/REQUEST.json"),
        ("run", "output/"),
    ]
    steps = workflow["jobs"]["run"]["steps"]
    names = [step.get("name") for step in steps]
    guard_step = steps[names.index("Nothing household-level leaves the runner")]
    upload = steps[names.index("Upload the receipt and results for the recorder")]
    assert names.index(guard_step["name"]) < names.index(upload["name"])
    assert guard_step["run"] == (
        "python3 -I .github/scripts/uk_replay_output_guard.py output"
    )
    assert upload["if"] == "always() && steps.guard.outcome == 'success'"
    assert guard_step["id"] == "guard" and guard_step["if"] == "always()"
    # The recorder checks again, where no candidate code has run, and drops
    # a refused output before anything reaches the public branch.
    record = workflow["jobs"]["record"]["steps"]
    record_names = [step.get("name") for step in record]
    recheck = record[
        record_names.index("Nothing household-level reaches the public branch")
    ]
    assert (
        "python3 -I .github/scripts/uk_replay_output_guard.py output" in recheck["run"]
    )
    assert "rm -rf output" in recheck["run"]
    assert record_names.index(recheck["name"]) < record_names.index(
        "Record the outcome and continue the queue"
    )
    # No cache crosses jobs: setup-uv caches by default (v5: enable-cache
    # auto), so every use here turns it off, as does the CI job that runs a
    # variant's engine; nothing uses actions/cache.
    uses = [
        step
        for job in workflow["jobs"].values()
        for step in job["steps"]
        if step.get("uses", "").startswith("astral-sh/setup-uv")
    ]
    assert len(uses) == 4
    ci = yaml.safe_load((ROOT / ".github/workflows/ci.yml").read_text())
    uses += [
        step
        for step in ci["jobs"]["replay-engine"]["steps"]
        if step.get("uses", "").startswith("astral-sh/setup-uv")
    ]
    assert all(step.get("with", {}).get("enable-cache") is False for step in uses)
    for document in (workflow, ci):
        for job in document["jobs"].values():
            for step in job["steps"]:
                assert not step.get("uses", "").startswith("actions/cache")


def test_the_data_token_is_used_only_outside_pull_requests():
    replay = yaml.safe_load((ROOT / ".github/workflows/uk-replay.yml").read_text())
    # PyYAML reads the bare key `on` as True.
    assert set(replay[True]) == {"repository_dispatch", "workflow_dispatch", "schedule"}
    ci = yaml.safe_load((ROOT / ".github/workflows/ci.yml").read_text())
    token = "secrets.PE_UK_PRIVATE_HF_READ_TOKEN"
    # Exactly two steps hold it, each with exactly this condition.
    holders = {
        (step["name"], step["if"])
        for document in (replay, ci)
        for job in document["jobs"].values()
        for step in job["steps"]
        if token in json.dumps(step)
    }
    assert holders == {
        (
            "Fetch and verify the dataset before any candidate code",
            'contains(fromJSON(\'["workflow_dispatch", "repository_dispatch"]\'), '
            "github.event_name)",
        ),
        (
            "Fetch the certified dataset for the real replay",
            "env.LEGACY == 'False' && github.event_name == 'push'",
        ),
    }
    for document in (replay, ci):
        # Never at workflow or job level, where every step would see it.
        assert "secrets." not in json.dumps(document.get("env", {}))
        for job in document["jobs"].values():
            assert "secrets." not in json.dumps(job.get("env", {}))
            for step in job["steps"]:
                assert "secrets.HUGGING_FACE_TOKEN" not in json.dumps(step)
    # The CI job that runs a variant's engine reads only, keeps no checkout
    # credential, and runs the engine in a later step than the token.
    engine = ci["jobs"]["replay-engine"]
    assert engine["permissions"] == {"contents": "read"}
    checkout = next(
        s for s in engine["steps"] if s.get("uses") == "actions/checkout@v4"
    )
    assert checkout["with"]["persist-credentials"] is False
    names = [step.get("name") for step in engine["steps"]]
    fetch = engine["steps"][
        names.index("Fetch the certified dataset for the real replay")
    ]
    replay_step = engine["steps"][
        names.index("One real measure-year replays byte for byte")
    ]
    assert names.index(fetch["name"]) < names.index(replay_step["name"])
    assert replay_step["if"] == "steps.fetch.outputs.fetched == 'true'"
    assert "env" not in replay_step and "huggingface_hub==2.2.0" in fetch["run"]
