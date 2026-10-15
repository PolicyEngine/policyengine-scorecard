"""Qualification requests, the persistent queue, receipts and seals.

Engine-free: environments, simulations and downloads are not run; the
pieces that decide identity, rejection and sealing are exercised directly.
"""

import copy
import hashlib
import json
import os
import shutil
import subprocess
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


def replay_workflow():
    import yaml

    path = Path(__file__).resolve().parents[1] / ".github/workflows/uk-replay.yml"
    return yaml.safe_load(path.read_text())


@pytest.mark.parametrize(
    "discovery_result", ["success", "skipped", "failure", "cancelled"]
)
def test_drain_runs_even_when_discovery_fails(discovery_result):
    from types import SimpleNamespace

    drain = replay_workflow()["jobs"]["drain"]
    assert "discover" in drain["needs"]
    expression = drain["if"].replace("&&", "and").replace("||", "or")
    functions = {
        "__builtins__": {},
        "always": lambda: True,
        "contains": lambda values, value: value in values,
        "fromJSON": json.loads,
    }
    for enqueue_result in ("success", "skipped", "failure", "cancelled"):
        needs = SimpleNamespace(
            enqueue=SimpleNamespace(result=enqueue_result),
            discover=SimpleNamespace(result=discovery_result),
        )
        assert eval(expression, functions, {"needs": needs}) is (
            enqueue_result in ("success", "skipped")
        )


def test_discovery_serializes_jobs_and_pushes_skips_after_build_errors():
    jobs = replay_workflow()["jobs"]
    assert jobs["discover"]["concurrency"] == {
        "group": "uk-replay-discover",
        "cancel-in-progress": False,
    }
    assert "concurrency" not in jobs["enqueue"]
    steps = jobs["discover"]["steps"]
    build = next(
        step for step in steps if "pipeline.uk_replay_discover" in step.get("run", "")
    )
    push = next(step for step in steps if "uk_replay_enqueue.sh" in step.get("run", ""))
    assert steps.index(build) < steps.index(push)
    assert push["if"] == "always()"
    assert 'bash .github/scripts/uk_replay_enqueue.sh "${requests[@]}"' in push["run"]
    assert 'if [ "${#requests[@]}"' not in push["run"]


def test_workflow_credentials_are_only_supplied_to_push_steps():
    workflow = replay_workflow()
    assert not any("TOKEN" in name for name in workflow["env"])
    for job in workflow["jobs"].values():
        assert not any("TOKEN" in name for name in job.get("env", {}))
        for step in job["steps"]:
            if step.get("uses", "").startswith("actions/checkout@"):
                assert step["with"]["persist-credentials"] is False
            if "PUSH_TOKEN" in step.get("env", {}):
                assert step["env"]["PUSH_TOKEN"] == "${{ github.token }}"
                assert any(
                    script in step["run"]
                    for script in ("uk_replay_enqueue.sh", "uk_replay_drain.sh")
                )
            if "pipeline.uk_replay_discover" in step.get("run", ""):
                assert "PUSH_TOKEN" not in step.get("env", {})


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


def test_late_dispatch_keeps_its_own_request_after_discovery(tmp_path):
    dispatched = golden_request()
    dispatched["kind"] = "released_bundle"
    dispatched["candidate"]["policyengine"]["source"] = {
        "pypi": {"wheel_sha256": "a" * 64}
    }
    discovered = copy.deepcopy(dispatched)
    discovered["requested_by"] = {
        "repository": "PolicyEngine/policyengine-scorecard",
        "commit": "0" * 40,
        "trigger": "scheduled catch-up of an undispatched policyengine.py release",
    }
    discovery_id, _ = queue.enqueue(
        tmp_path, discovered, run_url=RUN, now="2026-10-11T12:00:00Z"
    )
    dispatch_id, _ = queue.enqueue(
        tmp_path, dispatched, run_url=RUN, now="2026-10-11T13:00:00Z"
    )
    assert discovery_id != dispatch_id
    assert dispatch_id == interface.request_id(dispatched)
    assert queue.pending(tmp_path, now="2026-10-11T14:00:00Z") == [
        discovery_id,
        dispatch_id,
    ]


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


# --- state-branch shell transactions (local Git only) -----------------------------


SCRIPTS = Path(__file__).resolve().parents[1] / ".github" / "scripts"


def shell_git(directory, *args):
    return subprocess.check_output(
        [shutil.which("git"), "-C", str(directory), *args], text=True
    ).strip()


@pytest.fixture
def replay_shell_repo(tmp_path):
    root = tmp_path / "checkout"
    root.mkdir()
    remote = tmp_path / "remote.git"
    subprocess.run([shutil.which("git"), "init", "--bare", str(remote)], check=True)
    shell_git(root, "init", "-b", "control")
    shell_git(root, "remote", "add", "origin", str(remote))
    state = root / "state"
    state.mkdir()
    shell_git(state, "init", "-b", "replay-state")
    shell_git(state, "config", "user.name", "test")
    shell_git(state, "config", "user.email", "test@example.com")
    shell_git(state, "remote", "add", "origin", str(remote))
    (state / "shared.txt").write_text("original\n")
    shell_git(state, "add", ".")
    shell_git(state, "commit", "-m", "Initial state")
    shell_git(state, "push", "origin", "HEAD:replay-state")

    binaries = tmp_path / "bin"
    binaries.mkdir()
    git_log = tmp_path / "git.tsv"
    git_shim = binaries / "git"
    git_shim.write_text(
        r"""#!/bin/bash
set -euo pipefail
exported_tokens=""
for name in PUSH_TOKEN GITHUB_TOKEN REPLAY_PUSH_AUTH; do
  if declare -p "$name" >/dev/null 2>&1; then
    exported_tokens+="$name,"
  fi
done
{
  printf '%s' "${GIT_CONFIG_VALUE_0-}"
  printf '\t%s' "$exported_tokens" "$@"
  printf '\n'
} >> "$GIT_LOG"
command=$1
if [ "$1" = "-C" ]; then command=$3; fi
if [ "$command" = "push" ] && [ "${GIT_TEST_MODE-}" = "false-success" ]; then
  exit 0
fi
if [ "$command" = "push" ] && [ "${GIT_TEST_MODE-}" = "race" ] && [ ! -e "$GIT_LOG.race" ]; then
  : > "$GIT_LOG.race"
  "$REAL_GIT" -C "$RIVAL_DIR" push -q origin HEAD:replay-state
fi
exec "$REAL_GIT" "$@"
"""
    )
    git_shim.chmod(0o755)
    uv_shim = binaries / "uv"
    uv_shim.write_text(
        r"""#!/bin/bash
set -euo pipefail
credentials=""
for name in PUSH_TOKEN GITHUB_TOKEN REPLAY_PUSH_AUTH GIT_CONFIG_VALUE_0; do
  if declare -p "$name" >/dev/null 2>&1; then
    credentials+="$name,"
  fi
done
{
  printf '%s' "${GIT_CONFIG_VALUE_0-}"
  printf '\t%s' "$credentials" "$@"
  printf '\n'
} >> "$CONTROL_LOG"
request="state/requests/$TEST_REQUEST_ID"
status_path="$request/STATUS.json"
command=""
for arg in "$@"; do
  case "$arg" in pending|set-status|run-request) command=$arg ;; esac
done
case "$command" in
  pending)
    document=$(< "$status_path")
    if [[ "$document" != *'"status":"complete"'* ]]; then
      printf '%s\n' "$TEST_REQUEST_ID"
    fi
    ;;
  set-status)
    status="" receipt_commit=""
    while [ "$#" -gt 0 ]; do
      case "$1" in
        --status) status=$2; shift 2 ;;
        --receipt-commit) receipt_commit=$2; shift 2 ;;
        *) shift ;;
      esac
    done
    if [ -n "$receipt_commit" ]; then
      printf '{"status":"%s","receipt_commit":"%s"}' "$status" "$receipt_commit" > "$status_path"
    else
      printf '{"status":"%s"}' "$status" > "$status_path"
    fi
    ;;
  run-request)
    if [ "${WRITE_RECEIPT-yes}" = "yes" ]; then
      printf '{"status":"complete"}' > "$request/REPLAY_RECEIPT.json"
    fi
    printf 'complete %s\n' "$TEST_RECEIPT_SHA"
    ;;
  *) printf 'unexpected control command\n' >&2; exit 1 ;;
esac
"""
    )
    uv_shim.chmod(0o755)
    env = {
        **os.environ,
        "PATH": f"{binaries}{os.pathsep}{os.environ['PATH']}",
        "REAL_GIT": shutil.which("git"),
        "GIT_LOG": str(git_log),
        "CONTROL_LOG": str(tmp_path / "control.tsv"),
        "STATE_BRANCH": "replay-state",
        "RUN_URL": RUN,
        "RUNNER_TEMP": str(tmp_path / "runner"),
        "REPLAY_RUNNER": "test",
        "PUSH_TOKEN": "synthetic-push-token",
        "GITHUB_TOKEN": "synthetic-github-token",
        "TEST_REQUEST_ID": "a" * 64,
        "TEST_RECEIPT_SHA": "b" * 64,
    }
    return root, state, remote, env


def run_replay_shell(repo, script, *, timeout=300):
    root, _, _, env = repo
    return subprocess.run(
        ["bash", str(SCRIPTS / script)],
        cwd=root,
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def shell_log(repo, *, control=False):
    # Fixture paths, argument strings and synthetic credentials contain no tabs
    # or newlines. Keep the drivers in Bash so a Git operation never needs to
    # start a second Python interpreter just to append its observation.
    name = "CONTROL_LOG" if control else "GIT_LOG"
    credential_key = "credentials" if control else "exported_tokens"
    records = []
    for line in Path(repo[3][name]).read_text().splitlines():
        credential, exported_tokens, *args = line.split("\t")
        records.append(
            {
                "args": args,
                "credential": credential or None,
                credential_key: [
                    value for value in exported_tokens.split(",") if value
                ],
            }
        )
    return records


def make_shell_rival(repo, *, conflict):
    root, _, remote, env = repo
    rival = root.parent / "rival"
    subprocess.run(
        [env["REAL_GIT"], "clone", "-q", "-b", "replay-state", str(remote), str(rival)],
        check=True,
    )
    shell_git(rival, "config", "user.name", "rival")
    shell_git(rival, "config", "user.email", "rival@example.com")
    (rival / ("shared.txt" if conflict else "rival.txt")).write_text("rival\n")
    shell_git(rival, "add", ".")
    shell_git(rival, "commit", "-m", "Concurrent writer")
    env.update(GIT_TEST_MODE="race", RIVAL_DIR=str(rival))
    return rival


@pytest.mark.parametrize("existing_branch", [False, True])
def test_state_checkout_keeps_credentials_ephemeral(replay_shell_repo, existing_branch):
    _, state, remote, env = replay_shell_repo
    shutil.rmtree(state)
    if not existing_branch:
        subprocess.run(
            [
                env["REAL_GIT"],
                "--git-dir",
                str(remote),
                "update-ref",
                "-d",
                "refs/heads/replay-state",
            ],
            check=True,
        )
    result = run_replay_shell(replay_shell_repo, "uk_replay_state.sh")
    assert result.returncode == 0, result.stderr
    if existing_branch:
        assert (state / "shared.txt").read_text() == "original\n"
    else:
        # Discovery can have no requests or skip records on the first run.
        assert not (state / "shared.txt").exists()
        assert (
            run_replay_shell(replay_shell_repo, "uk_replay_enqueue.sh").returncode == 0
        )
    assert shell_git(state, "symbolic-ref", "--short", "HEAD") == "replay-state"
    assert shell_git(state, "config", "user.name") == "github-actions[bot]"
    assert "extraheader" not in shell_git(state, "config", "--local", "--list")
    operations = shell_log(replay_shell_repo)
    assert all(not op["exported_tokens"] for op in operations)
    assert all(
        op["credential"].startswith("AUTHORIZATION: basic ")
        for op in operations
        if op["args"][0] in {"ls-remote", "fetch"}
    )


def test_enqueue_persists_skip_records_after_a_concurrent_push(replay_shell_repo):
    _, state, _, _ = replay_shell_repo
    skip = state / "discovery" / "skipped" / "6.3.0.json"
    skip.parent.mkdir(parents=True)
    skip.write_text('{"reason":"inconsistent published identity"}')
    make_shell_rival(replay_shell_repo, conflict=False)
    # Allow extra time for the rebase and the second push on a busy host.
    result = run_replay_shell(replay_shell_repo, "uk_replay_enqueue.sh", timeout=300)
    assert result.returncode == 0, result.stderr
    assert skip.exists() and (state / "rival.txt").exists()
    assert (
        shell_git(state, "rev-parse", "HEAD")
        == shell_git(state, "ls-remote", "origin", "refs/heads/replay-state").split()[0]
    )
    pushes = [op for op in shell_log(replay_shell_repo) if "push" in op["args"]]
    assert len(pushes) == 2


def test_conflicted_push_aborts_rebase_before_any_further_push(replay_shell_repo):
    _, state, _, _ = replay_shell_repo
    (state / "shared.txt").write_text("local\n")
    rival = make_shell_rival(replay_shell_repo, conflict=True)
    result = run_replay_shell(replay_shell_repo, "uk_replay_enqueue.sh")
    assert result.returncode != 0
    assert "could not rebase" in result.stderr
    assert (state / "shared.txt").read_text() == "local\n"
    assert not (state / ".git" / "rebase-merge").exists()
    assert not (state / ".git" / "rebase-apply").exists()
    operations = shell_log(replay_shell_repo)
    assert any(op["args"][-2:] == ["rebase", "--abort"] for op in operations)
    assert len([op for op in operations if "push" in op["args"]]) == 1
    assert shell_git(state, "ls-remote", "origin", "refs/heads/replay-state").split()[
        0
    ] == shell_git(rival, "rev-parse", "HEAD")


@pytest.mark.parametrize("new_changes", [False, True])
def test_push_success_without_remote_update_is_rejected(replay_shell_repo, new_changes):
    _, state, _, env = replay_shell_repo
    (state / "receipt.json").write_text("{}")
    if not new_changes:
        shell_git(state, "add", ".")
        shell_git(state, "commit", "-m", "Unpublished receipt")
    env["GIT_TEST_MODE"] = "false-success"
    result = run_replay_shell(replay_shell_repo, "uk_replay_enqueue.sh")
    assert result.returncode != 0
    assert "could not push and verify" in result.stderr
    operations = shell_log(replay_shell_repo)
    assert len([op for op in operations if "push" in op["args"]]) == 5
    assert (
        shell_git(state, "rev-parse", "HEAD")
        != shell_git(state, "ls-remote", "origin", "refs/heads/replay-state").split()[0]
    )


@pytest.mark.parametrize("new_receipt", [False, True])
def test_drain_names_only_a_verified_receipt_commit_and_hides_git_tokens(
    replay_shell_repo, new_receipt
):
    _, state, _, env = replay_shell_repo
    request = state / "requests" / ("a" * 64)
    request.mkdir(parents=True)
    (request / "STATUS.json").write_text('{"status":"queued"}')
    (request / "REQUEST.json").write_text("{}")
    if not new_receipt:
        (request / "REPLAY_RECEIPT.json").write_text('{"status":"complete"}')
        env["WRITE_RECEIPT"] = "no"
    shell_git(state, "add", ".")
    shell_git(state, "commit", "-m", "Queued request")
    shell_git(state, "push", "origin", "HEAD:replay-state")
    result = run_replay_shell(replay_shell_repo, "uk_replay_drain.sh")
    assert result.returncode == 0, result.stderr
    status = json.loads((request / "STATUS.json").read_text())
    receipt_commit = status["receipt_commit"]
    receipt_path = f"requests/{'a' * 64}/REPLAY_RECEIPT.json"
    assert json.loads(shell_git(state, "show", f"{receipt_commit}:{receipt_path}")) == {
        "status": "complete"
    }
    assert shell_git(state, "merge-base", "--is-ancestor", receipt_commit, "HEAD") == ""
    assert (
        shell_git(state, "rev-parse", "HEAD")
        == shell_git(state, "ls-remote", "origin", "refs/heads/replay-state").split()[0]
    )
    control = shell_log(replay_shell_repo, control=True)
    assert any("run-request" in operation["args"] for operation in control)
    assert all(not operation["credentials"] for operation in control)
    git_operations = shell_log(replay_shell_repo)
    assert all(not op["exported_tokens"] for op in git_operations)
    assert all(
        op["credential"].startswith("AUTHORIZATION: basic ")
        for op in git_operations
        if "push" in op["args"]
    )
