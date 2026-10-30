"""publish-db.yml: the one workflow that names the Supabase secrets.

It publishes the database ci.yml's pytest job built, from that run's
artifact, once CI completes on a push to main. It moved out of ci.yml so that
no workflow that runs on pull requests names a secret
(tests/test_ci_gates.py). These tests pin what the move had to keep: it
publishes only for main's own pushes, only what passed CI's pytest job, and
runs no package code beside the key; latest.db.gz never moves off main's tip;
unset secrets skip with a notice, a failed upload is a warning, and curl never
prints the host. The step scripts run here under
`bash -e`, the shell GitHub's log shows for them, with `gh` and `curl` stubs.
"""

import gzip
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS = ROOT / ".github" / "workflows"
CI = WORKFLOWS / "ci.yml"
PUBLISH = WORKFLOWS / "publish-db.yml"

FIND = "Find the database CI built"
DOWNLOAD = "Download it"
UPLOAD = "Publish it"
# v4.3.0, the commit actions/download-artifact's v4 tag also names.
DOWNLOAD_ACTION = "actions/download-artifact@d3f86a106a0bac45b974a628896c90dbdf5c8093"
SHA = "0123456789abcdef0123456789abcdef01234567"
NEWER = "fedcba9876543210fedcba9876543210fedcba98"
RUN_ID = "39698300855"
ATTEMPT = "2"
REPOSITORY = "PolicyEngine/policyengine-scorecard"
HOST = "secret-project-ref.supabase.co"
KEY = "sb_secret_key_value"


def workflow() -> dict:
    return yaml.safe_load(PUBLISH.read_text())


def job() -> dict:
    return workflow()["jobs"]["publish-db"]


def step(name: str) -> dict:
    (found,) = [s for s in job()["steps"] if s.get("name") == name]
    return found


def test_it_runs_when_ci_completes_on_main():
    ci = yaml.safe_load(CI.read_text())
    assert workflow()[True] == {
        "workflow_run": {
            "workflows": [ci["name"]],
            "types": ["completed"],
            "branches": ["main"],
        }
    }
    assert ci[True]["push"] == {"branches": ["main"]}
    assert list(workflow()["jobs"]) == ["publish-db"]
    # GitHub cancels a concurrency group's pending job when another enters,
    # so an older run's completion could drop the publish for main's tip.
    assert "concurrency" not in workflow() and "concurrency" not in job()
    # Without a group, this limit keeps a publish for an older tip from ending
    # after the next commit's, which waits for that commit's CI. Each upload's
    # time limit fits inside it, so a stalled upload warns before the job ends.
    assert job()["timeout-minutes"] == 5
    assert "--max-time 120 " in step(UPLOAD)["run"]


def test_it_is_the_only_workflow_run_workflow():
    """A workflow_run workflow runs with the repository's secrets for every
    run it follows, pull requests' included. Another one needs the same
    guard as publish-db and its own test."""
    found = {
        path.name
        for path in WORKFLOWS.glob("*.y*ml")
        if "workflow_run" in yaml.safe_load(path.read_text())[True]
    }
    assert found == {"publish-db.yml"}


# The guard, one clause per field of the triggering run. The fields are the
# run object's: GET /repos/{owner}/{repo}/actions/runs returns `event`,
# `head_branch`, `head_repository.full_name` and `path` for this repository's
# CI runs, and the workflow_run event carries that object.
GUARD = {
    "github.event.workflow_run.event == 'push'",
    "github.event.workflow_run.head_branch == 'main'",
    "github.event.workflow_run.head_repository.full_name == github.repository",
    "github.event.workflow_run.path == '.github/workflows/ci.yml'",
}


def guard_admits(run: dict, repository: str = REPOSITORY) -> bool:
    """The job's `if`, evaluated: a conjunction of equalities, each between
    a field of the triggering run and a quoted literal or github.repository.
    GitHub compares strings ignoring case, and so does this."""
    condition = job()["if"]
    assert "||" not in condition and "!" not in condition
    context = {"github": {"repository": repository, "event": {"workflow_run": run}}}

    def value(term):
        term = term.strip()
        if term.startswith("'"):
            return term.strip("'")
        node = context
        for part in term.split("."):
            node = node[part]
        return node

    clauses = [c.split("==") for c in condition.split("&&")]
    return all(value(left).lower() == value(right).lower() for left, right in clauses)


def ci_run(**changes) -> dict:
    run = {
        "event": "push",
        "head_branch": "main",
        "head_repository": {"full_name": REPOSITORY},
        "path": ".github/workflows/ci.yml",
    }
    return {**run, **changes}


def test_the_guard_admits_only_cis_pushes_to_main_here():
    """workflow_run runs main's copy of the file with the repository's
    secrets after any CI run, a fork's pull request included, and the
    `branches` filter names a branch only: a fork's pull request from a
    branch called main gets past it."""
    assert {c.strip() for c in job()["if"].split("&&")} == GUARD
    assert guard_admits(ci_run())
    fork = {"full_name": "someone/policyengine-scorecard"}
    for refused in (
        ci_run(event="pull_request"),
        ci_run(event="pull_request", head_repository=fork),
        ci_run(event="pull_request_target"),
        ci_run(event="workflow_dispatch"),
        ci_run(head_branch="feature"),
        ci_run(head_repository=fork),
        ci_run(path=".github/workflows/other.yml"),
    ):
        assert not guard_admits(refused), refused


def test_it_downloads_what_ci_uploaded_for_that_commit():
    ci = yaml.safe_load(CI.read_text())
    (upload,) = [
        s
        for s in ci["jobs"]["python"]["steps"]
        if s.get("uses", "").startswith("actions/upload-artifact")
    ]
    assert upload["with"]["name"] == "scorecard-db-${{ github.sha }}"
    assert upload["with"]["path"] == "data/scorecard.db"
    download = step(DOWNLOAD)
    assert download["uses"] == DOWNLOAD_ACTION
    assert download["with"] == {
        "name": "scorecard-db-${{ github.event.workflow_run.head_sha }}",
        "run-id": "${{ github.event.workflow_run.id }}",
        "github-token": "${{ github.token }}",
    }
    assert download["if"] == step(UPLOAD)["if"] == "steps.find.outputs.found == 'true'"
    assert step(FIND)["id"] == "find"
    assert 'artifact="scorecard-db-$CI_SHA"' in step(FIND)["run"]
    assert job()["env"] == {
        "CI_RUN_ID": "${{ github.event.workflow_run.id }}",
        "CI_ATTEMPT": "${{ github.event.workflow_run.run_attempt }}",
        "CI_SHA": "${{ github.event.workflow_run.head_sha }}",
    }


def test_find_reads_the_job_ci_names_pytest():
    """A rename in ci.yml would otherwise leave nothing to match, and every
    publish would skip with a notice."""
    name = yaml.safe_load(CI.read_text())["jobs"]["python"]["name"]
    assert f'select(.name == "{name}")' in step(FIND)["run"]


def test_no_script_interpolates_the_triggering_run():
    """A pull request's author chooses its branch name, and GitHub pastes a
    ${{ }} into a script before the shell reads it. The scripts take the run
    id and commit from the environment and interpolate nothing."""
    for s in job()["steps"]:
        assert "${{" not in s.get("run", ""), s.get("name")


def test_no_script_reads_github_sha():
    """In a workflow_run run GITHUB_SHA is not the CI commit, and a re-run
    keeps its original value, so it is not main's tip either."""
    for s in job()["steps"]:
        assert "GITHUB_SHA" not in s.get("run", ""), s.get("name")


def test_the_job_runs_no_package_code():
    """No checkout and no package manager or interpreter: what runs beside
    the key is actions/download-artifact and the runner image's gh, gzip
    and curl."""
    assert [s["uses"] for s in job()["steps"] if "uses" in s] == [DOWNLOAD_ACTION]
    commands = re.compile(
        r"\b(uvx?|pip3?|python3?|bun|bunx|npm|npx|node|make|bash|sh|source)\b"
        r"|\.github/scripts|\./"
    )
    for s in job()["steps"]:
        assert not commands.search(s.get("run", "")), s["name"]


def test_the_tokens_are_where_they_are_used():
    """GITHUB_TOKEN reaches the steps that read CI's run, and the Supabase
    secrets the step that uploads, never the workflow or job environment."""
    with_github_token = [
        s["name"] for s in job()["steps"] if "github.token" in json.dumps(s)
    ]
    assert with_github_token == [FIND, DOWNLOAD]
    assert step(FIND)["env"] == {"GH_TOKEN": "${{ github.token }}"}
    with_secrets = [s["name"] for s in job()["steps"] if "secrets." in json.dumps(s)]
    assert with_secrets == [UPLOAD]
    assert step(UPLOAD)["env"] == {
        "MAIN_TIP": "${{ steps.find.outputs.main_tip }}",
        "SUPABASE_URL": "${{ secrets.SUPABASE_SCORECARD_URL }}",
        "SUPABASE_KEY": "${{ secrets.SUPABASE_SCORECARD_KEY }}",
    }
    assert "env" not in workflow()


# Stand-ins for the runner image's gh and curl. Each records its arguments
# and the variables the script reads; curl also keeps the bytes it would
# send. gh answers by endpoint, and fails for the one named in `fails_on`.
# Like the real curl, a failing stub prints its error, host included, unless
# one of its short options includes -s.
GH_STUB = """#!{python} -I
import json, os, sys
with open({record!r}, "a") as handle:
    handle.write(json.dumps({{"argv": sys.argv[1:], "token": os.environ.get("GH_TOKEN")}}) + "\\n")
endpoint = sys.argv[2]
if {fails_on!r} and {fails_on!r} in endpoint:
    sys.stderr.write("HTTP 502\\n")
    sys.exit(1)
print(next(answer for path, answer in {answers!r}.items() if path in endpoint))
"""
CURL_STUB = """#!{python} -I
import json, sys
args = sys.argv[1:]
payload = args[args.index("--data-binary") + 1].removeprefix("@")
with open(payload, "rb") as handle:
    sent = handle.read().hex()
with open({record!r}, "a") as handle:
    handle.write(json.dumps({{"argv": args, "sent": sent}}) + "\\n")
if {status}:
    silent = any(a.startswith("-") and not a.startswith("--") and "s" in a for a in args)
    if not silent:
        url = [a for a in args if a.startswith("https://")][0]
        sys.stderr.write("curl: (6) Could not resolve host: " + url.split("/")[2] + "\\n")
    sys.exit({status})
"""


def run_step(
    tmp_path,
    name,
    *,
    env=(),
    script=None,
    pytest_conclusion="success",
    artifacts="1",
    fails_on="",
    status=0,
):
    """``name``'s script under `bash -e`, in a fresh workspace holding a
    database, with gh and curl stubs first on PATH."""
    work = tmp_path / "work"
    work.mkdir()
    (work / "scorecard.db").write_bytes(b"SQLite format 3\x00" + bytes(range(256)))
    stubs = tmp_path / "stubs"
    stubs.mkdir()
    records = {tool: tmp_path / f"{tool}.jsonl" for tool in ("gh", "curl")}
    (stubs / "gh").write_text(
        GH_STUB.format(
            python=sys.executable,
            record=str(records["gh"]),
            answers={
                "/jobs": pytest_conclusion,
                "/artifacts": artifacts,
                "/git/ref/": NEWER,
            },
            fails_on=fails_on,
        )
    )
    (stubs / "curl").write_text(
        CURL_STUB.format(
            python=sys.executable, record=str(records["curl"]), status=status
        )
    )
    for stub in stubs.iterdir():
        stub.chmod(0o755)
    path = tmp_path / "step.sh"
    path.write_text(script if script is not None else step(name)["run"])
    output, summary = tmp_path / "github_output", tmp_path / "step_summary"
    output.touch()
    summary.touch()
    environment = {
        "PATH": f"{stubs}:/usr/bin:/bin",
        "HOME": str(tmp_path),
        "GITHUB_OUTPUT": str(output),
        "GITHUB_STEP_SUMMARY": str(summary),
        "GITHUB_REPOSITORY": REPOSITORY,
        "GITHUB_SERVER_URL": "https://github.com",
        "CI_RUN_ID": RUN_ID,
        "CI_ATTEMPT": ATTEMPT,
        "CI_SHA": SHA,
        "MAIN_TIP": SHA,
        # What the runner sets on a re-run of this commit's publish, whatever
        # main has moved to since.
        "GITHUB_SHA": SHA,
        "GH_TOKEN": "ghs_runtoken",
        "SUPABASE_URL": f"https://{HOST}",
        "SUPABASE_KEY": KEY,
        **dict(env),
    }
    result = subprocess.run(
        ["bash", "-e", str(path)],
        cwd=work,
        env=environment,
        capture_output=True,
        text=True,
    )
    calls = {
        tool: [json.loads(line) for line in record.read_text().splitlines()]
        if record.exists()
        else []
        for tool, record in records.items()
    }
    return result, calls, output.read_text(), summary.read_text(), work


def test_find_says_found_when_ci_passed_and_uploaded_the_database(tmp_path):
    result, calls, output, _, _ = run_step(tmp_path, FIND)
    assert result.returncode == 0, result.stderr
    assert output == f"found=true\nmain_tip={NEWER}\n"
    assert "::notice::" not in result.stdout
    run = f"repos/{REPOSITORY}/actions/runs/{RUN_ID}"
    assert calls["gh"] == [
        {
            "argv": [
                "api",
                f"{run}/attempts/{ATTEMPT}/jobs?per_page=100",
                "--jq",
                '.jobs[] | select(.name == "pytest · ruff format") | .conclusion',
            ],
            "token": "ghs_runtoken",
        },
        {
            "argv": [
                "api",
                f"{run}/artifacts?name=scorecard-db-{SHA}",
                "--jq",
                "[.artifacts[] | select(.expired | not)] | length",
            ],
            "token": "ghs_runtoken",
        },
        {
            "argv": [
                "api",
                f"repos/{REPOSITORY}/git/ref/heads/main",
                "--jq",
                ".object.sha",
            ],
            "token": "ghs_runtoken",
        },
    ]


def test_find_skips_with_a_notice_when_the_pytest_job_uploaded_nothing(tmp_path):
    result, calls, output, _, _ = run_step(tmp_path, FIND, artifacts="0")
    assert result.returncode == 0, result.stderr
    assert output == f"found=false\nmain_tip={NEWER}\n"
    assert result.stdout == (
        f"::notice::CI run {RUN_ID} attempt {ATTEMPT} has nothing to publish: its "
        f"pytest job ended success, with 0 scorecard-db-{SHA}\n"
    )
    assert not calls["curl"]


@pytest.mark.parametrize("conclusion", ["failure", "cancelled", "skipped", ""])
def test_find_skips_an_artifact_this_attempts_pytest_job_did_not_pass(
    tmp_path, conclusion
):
    """An artifact can outlive the attempt that uploaded it: a re-run of a
    job that passed shares its attempt's artifact (run 39698458972), so the
    artifact alone does not say the attempt that fired this run passed."""
    result, _, output, _, _ = run_step(tmp_path, FIND, pytest_conclusion=conclusion)
    assert result.returncode == 0, result.stderr
    assert output == f"found=false\nmain_tip={NEWER}\n"
    assert f"pytest job ended {conclusion or 'unknown'}," in result.stdout


@pytest.mark.parametrize("endpoint", ["/jobs", "/artifacts", "/git/ref/"])
def test_find_fails_the_run_when_it_cannot_ask(tmp_path, endpoint):
    result, _, output, _, _ = run_step(tmp_path, FIND, fails_on=endpoint)
    assert result.returncode != 0
    assert output == ""


@pytest.mark.parametrize("unset", ["SUPABASE_URL", "SUPABASE_KEY"])
def test_publish_skips_with_a_notice_when_a_secret_is_unset(tmp_path, unset):
    result, calls, _, summary, work = run_step(tmp_path, UPLOAD, env={unset: ""})
    assert result.returncode == 0, result.stderr
    assert result.stdout == "::notice::Supabase secrets not set — skipping publish\n"
    assert not calls["curl"] and summary == ""
    assert not (work / "scorecard.db.gz").exists()


def test_publish_uploads_the_commits_database_then_latest(tmp_path):
    result, calls, _, summary, work = run_step(tmp_path, UPLOAD)
    assert result.returncode == 0, result.stderr
    names = [f"{SHA}.db.gz", "latest.db.gz"]
    assert result.stdout == "".join(
        f"uploaded scorecard-artifacts/{n}\n" for n in names
    )
    assert summary == ""
    database = (work / "scorecard.db").read_bytes()
    for call, name in zip(calls["curl"], names, strict=True):
        assert call["argv"] == [
            "-sf",
            "--max-time",
            "120",
            "-X",
            "POST",
            f"https://{HOST}/storage/v1/object/scorecard-artifacts/{name}",
            "-H",
            f"Authorization: Bearer {KEY}",
            "-H",
            "Content-Type: application/gzip",
            "-H",
            "x-upsert: true",
            "--data-binary",
            "@scorecard.db.gz",
        ]
        assert gzip.decompress(bytes.fromhex(call["sent"])) == database


def test_latest_waits_for_mains_tip(tmp_path):
    """When main has moved on (a newer push cancelled this run, or an older
    CI or publish run was re-run), the commit's own copy is uploaded and
    latest.db.gz is not rolled back. On a re-run of an old publish GITHUB_SHA
    is still that commit, as run_step sets it, so only the tip the find step
    read tells the two apart."""
    result, calls, _, summary, _ = run_step(tmp_path, UPLOAD, env={"MAIN_TIP": NEWER})
    assert result.returncode == 0, result.stderr
    assert result.stdout == (
        f"::notice::main is at {NEWER} now, not {SHA}: latest.db.gz is left "
        f"to the run for main's tip\nuploaded scorecard-artifacts/{SHA}.db.gz\n"
    )
    assert [call["argv"][5].rsplit("/", 1)[1] for call in calls["curl"]] == [
        f"{SHA}.db.gz"
    ]
    assert summary == ""


def test_a_failed_upload_is_a_warning_and_never_prints_the_host(tmp_path):
    result, calls, _, summary, _ = run_step(tmp_path, UPLOAD, status=6)
    assert result.returncode == 0, result.stderr
    assert len(calls["curl"]) == 1
    message = (
        f"curl exit 6 uploading scorecard-artifacts/{SHA}.db.gz: the published "
        f"database was not updated. The database CI built is the "
        f"scorecard-db-{SHA} artifact of "
        f"https://github.com/{REPOSITORY}/actions/runs/{RUN_ID}."
    )
    assert result.stdout == f"::warning title=Supabase publish failed::{message}\n"
    assert summary == f"**Supabase publish failed.** {message}\n"
    for shown in (result.stdout, result.stderr, summary):
        assert HOST not in shown and KEY not in shown


def test_without_curls_silence_the_host_would_print(tmp_path):
    """The stub does print the host when curl is not silenced, so the test
    above is not passing for want of anything to print."""
    script = step(UPLOAD)["run"]
    assert script.count("curl -sf ") == 1
    result, *_ = run_step(
        tmp_path, UPLOAD, status=6, script=script.replace("curl -sf ", "curl -f ")
    )
    assert HOST in result.stderr
