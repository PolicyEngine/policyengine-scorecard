"""The CI gates, and the guard that stops a stale branch skipping them.

GitHub runs a `pull_request` workflow from the PULL REQUEST'S OWN
branch, not from the base. A branch that forked before a gate was added
therefore keeps running the older workflow — and its green tick looks
identical to a full one while meaning strictly less.

That happened here: #74 made the database a derived artifact and added a
determinism check and a no-drift gate, and branches forked before it
were reviewed and approved on the understanding that both had run
against them when neither had.

`gate-freshness.yml` closes it by running from the BASE via
`pull_request_target`. These tests keep that guard honest — a workflow
nobody can weaken by accident is the point of it.

They also pin the token ci.yml's jobs hold: the repository's default
GITHUB_TOKEN is write, so a job the file does not narrow would hold it.

And they keep every secret out of the workflows that run on pull requests,
which install and run third-party packages: a runner receives a secret its
job names even in a step that never runs, and GitHub scrubs only the secrets
"not referenced in the workflow".
"""

import re
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS = ROOT / ".github" / "workflows"
CI = WORKFLOWS / "ci.yml"
DETERMINISM = WORKFLOWS / "uk-replay-determinism.yml"
FRESHNESS = WORKFLOWS / "gate-freshness.yml"
PUBLISH = WORKFLOWS / "publish-db.yml"

READ = {"contents": "read"}
LEVEL = {"none": 0, "read": 1, "write": 2}
# A ci.yml job that needs more than READ goes here with exactly the scopes it
# needs, and why. None does: checkout fetches this repository, setup-uv and
# setup-bun read public releases, and the database artifact is uploaded on
# the Actions runtime token, not GITHUB_TOKEN.
NEEDS_MORE: dict[str, dict[str, str]] = {}
# publish-db.yml reads CI's jobs and downloads its artifact, which takes
# actions: read, and reads main's tip, which takes contents: read.
PUBLISH_NEEDS = {"publish-db": {"actions": "read", "contents": "read"}}

# The events a pull request starts runs for: opening or updating it, a review
# or review comment on it, a comment on its conversation (issue_comment), and
# adding it to a merge queue.
PULL_REQUEST_EVENTS = {
    "pull_request",
    "pull_request_target",
    "pull_request_review",
    "pull_request_review_comment",
    "issue_comment",
    "merge_group",
}
# The secrets a workflow that runs on pull requests may name: none. A debug
# re-run of #215's pull-request CI (job 119587048984) evaluated a secret its
# job named only in a skipped step, so naming one anywhere in such a workflow
# may hand it to runners that run a pull request's packages.
SECRETS_ON_PULL_REQUESTS: frozenset[str] = frozenset()
SUPABASE = {"SUPABASE_SCORECARD_URL", "SUPABASE_SCORECARD_KEY"}


def ci() -> dict:
    return yaml.safe_load(CI.read_text())


def workflows() -> dict[str, dict]:
    return {
        path.name: yaml.safe_load(path.read_text())
        for path in sorted(WORKFLOWS.glob("*.y*ml"))
    }


def triggers(workflow: dict) -> set[str]:
    """A workflow's events. PyYAML reads the bare key `on` as True."""
    on = workflow[True]
    return {on} if isinstance(on, str) else set(on)


def templates(text: str) -> list[str]:
    """The body of each ${{ }} in ``text``, read as GitHub's parser reads
    it: a }} inside a single-quoted string literal does not end it. An
    escaped quote ('') toggles twice, which leaves the state as it was."""
    found, start = [], text.find("${{")
    while start != -1:
        end, quoted = start + 3, False
        while end < len(text) and (quoted or not text.startswith("}}", end)):
            quoted ^= text[end] == "'"
            end += 1
        found.append(text[start + 3 : end])
        start = text.find("${{", end + 2)
    return found


# The secrets context itself, not a property named secrets (inputs.secrets),
# in any case, so Secrets.x or SECRETS.X cannot slip past.
CONTEXT = re.compile(r"(?<![\w.])secrets\b", re.I)
NAMED = re.compile(
    r"(?<![\w.])secrets\s*(?:\.\s*([A-Za-z_][\w-]*)"
    r"|\[\s*'([^']*)'\s*\]|\[\s*\"([^\"]*)\"\s*\])",
    re.I,
)


def expressions(node, key=None):
    """Every expression in a parsed workflow: each ${{ }} in any key or
    string, and each `if` whole, since GitHub evaluates it with or without
    ${{ }}. Comments are never evaluated, and YAML drops them."""
    if isinstance(node, dict):
        for k, v in node.items():
            yield from expressions(k)
            yield from expressions(v, k)
    elif isinstance(node, list):
        for item in node:
            yield from expressions(item)
    elif isinstance(node, str):
        yield from [node] if key == "if" else templates(node)


def named_secrets(workflow: dict) -> set[str]:
    """The secrets ``workflow`` names, upper-cased. A reference that names
    no one secret, such as toJSON(secrets), secrets[format(...)] or a
    reusable-workflow call's `secrets:`, counts as "*", every secret."""
    names = set()
    for expression in expressions(workflow):
        matches = NAMED.findall(expression)
        names |= {next(n for n in groups if n).upper() for groups in matches}
        if len(CONTEXT.findall(expression)) > len(matches):
            names.add("*")
    if any("secrets" in job for job in workflow["jobs"].values()):
        names.add("*")
    return names


def granted(workflow: dict, job: str):
    """The GITHUB_TOKEN scopes ``job`` gets from the file. GitHub applies the
    workflow's block, then the job's, and a block that names any scope sets
    every scope it leaves out to none, so a job's own block is all it gets.
    None means neither says, and the repository default applies."""
    return workflow["jobs"][job].get("permissions", workflow.get("permissions"))


def overreach(workflow: dict, needs_more=NEEDS_MORE) -> list[str]:
    """Every grant beyond READ, or beyond a job's ``needs_more`` entry."""
    found = []
    if workflow.get("permissions") != READ:
        found.append(f"the workflow level is {workflow.get('permissions')!r}")
    for job in workflow["jobs"]:
        scopes, allowed = granted(workflow, job), needs_more.get(job, READ)
        if not isinstance(scopes, dict):
            found.append(f"{job} gets {scopes!r}")
            continue
        for scope, level in scopes.items():
            if LEVEL[level] > LEVEL[allowed.get(scope, "none")]:
                found.append(f"{job} gets {scope}: {level}")
    return found


def test_the_gates_ci_defines_are_still_there():
    """These two lines are what a green tick is supposed to mean."""
    text = CI.read_text()
    assert "git diff --exit-code" in text, "the no-drift gate is gone"
    assert "nondeterministic" in text, "the determinism check is gone"


def test_the_freshness_guard_exists():
    assert FRESHNESS.exists(), (
        "gate-freshness.yml is what stops a branch that forked before a "
        "gate from skipping it"
    )


def test_it_runs_from_the_base_branch():
    """`pull_request` would run it from the PR's own branch, which is the
    exact failure it exists to prevent — a stale branch would simply not
    have the guard."""
    text = FRESHNESS.read_text()
    assert "pull_request_target:" in text
    assert not re.search(r"^on:\s*\n\s+pull_request:", text, re.M)


def test_it_never_executes_pull_request_code():
    """pull_request_target runs in the base repo's context, so checking
    out and running PR code would be a privilege-escalation hole. This
    job reads git metadata only."""
    text = FRESHNESS.read_text()
    assert "ref: ${{ github.event.pull_request.base.sha }}" in text
    assert "ref: ${{ github.event.pull_request.head.sha }}" not in text
    assert "contents: read" in text
    # Scan only the EXECUTABLE part: the failure message is a heredoc
    # that tells the author to run pytest, which is help text, not
    # something this job does.
    body = text.split("Fetch the head commit as data", 1)[1]
    executable = re.sub(r"cat <<'MSG'.*?\n\s*MSG\n", "", body, flags=re.S)
    for danger in ("pip install", "pytest ", "uv run", "python -m scorecard_db"):
        assert danger not in executable, f"the guard must not run {danger!r}"
    # ...and the help text really is still there
    assert "pytest tests/ -q" in body


def test_the_gate_set_is_derived_from_the_base_not_hardcoded():
    """A gate added to ci.yml later must be enforced on every open PR
    without anyone remembering to update the guard."""
    text = FRESHNESS.read_text()
    assert 'git show "$BASE_SHA:.github/workflows/ci.yml"' in text
    assert "required-gates.txt" in text


def test_it_also_catches_the_committed_database():
    """A branch that still tracks data/scorecard.db forked before #74, so
    its build cannot have been from-scratch."""
    text = FRESHNESS.read_text()
    assert "data/scorecard.db" in text
    assert "still TRACKED" in text


def test_the_failure_message_says_what_to_do():
    """A gate that fails without a fix is a gate people learn to ignore."""
    text = FRESHNESS.read_text()
    assert "git merge origin/main" in text
    assert "rm -f data/scorecard.db" in text
    assert "nothing about your own changes needs to move" in text.lower()


def test_every_ci_job_reads_the_repository_and_nothing_more():
    """The pytest job runs PyPI packages on pushes to main with checkout's
    persisted token. Until the workflow-level block, that job, the app job
    and publish-db (in publish-db.yml since) held the repository's write
    default."""
    workflow = ci()
    assert workflow["permissions"] == READ
    assert set(NEEDS_MORE) <= set(workflow["jobs"]), "NEEDS_MORE names a gone job"
    assert overreach(workflow) == []


def test_every_real_replay_job_reads_the_repository_and_nothing_more():
    """The push-only real replay holds the dataset token beside the
    variant's engine; its GITHUB_TOKEN reads and nothing more."""
    workflow = yaml.safe_load(DETERMINISM.read_text())
    assert not set(NEEDS_MORE) & set(workflow["jobs"])
    assert overreach(workflow) == []


@pytest.mark.parametrize(
    "edit",
    [
        lambda w: w.pop("permissions"),
        lambda w: w.update(permissions="write-all"),
        lambda w: w.update(permissions="read-all"),
        lambda w: w.update(permissions={"contents": "write"}),
        lambda w: w.update(permissions={**READ, "actions": "read"}),
        lambda w: w["jobs"]["python"].update(permissions={"contents": "write"}),
        lambda w: w["jobs"]["app"].update(permissions="write-all"),
        lambda w: w["jobs"]["replay-variants"].update(
            permissions={**READ, "actions": "read"}
        ),
        lambda w: w["jobs"]["replay-engine"].update(permissions={"id-token": "write"}),
    ],
    ids=[
        "no-workflow-block",
        "workflow-write-all",
        "workflow-read-all",
        "workflow-contents-write",
        "workflow-adds-actions",
        "python-contents-write",
        "app-write-all",
        "replay-variants-adds-actions",
        "replay-engine-id-token",
    ],
)
def test_the_check_catches_every_wider_token(edit):
    workflow = ci()
    edit(workflow)
    assert overreach(workflow)


def test_the_check_lets_a_job_narrow_its_token():
    workflow = ci()
    workflow["jobs"]["app"]["permissions"] = {}
    workflow["jobs"]["receiver-sandbox"]["permissions"] = {"contents": "none"}
    assert overreach(workflow) == []


def test_ci_uploads_the_database_without_a_token():
    """actions/upload-artifact v4 has no token input: it uploads through the
    Actions runtime token (ACTIONS_RUNTIME_TOKEN), which is why ci.yml needs
    no actions scope. Re-check this when the action changes major version.
    No step is handed GITHUB_TOKEN explicitly; setup-uv and setup-bun take
    it by default, to read public releases. publish-db.yml downloads the
    artifact once the run completes (tests/test_publish_db.py)."""
    text = CI.read_text()
    assert "secrets.GITHUB_TOKEN" not in text and "github.token" not in text
    jobs = ci()["jobs"]
    (upload,) = [
        s
        for s in jobs["python"]["steps"]
        if s.get("uses", "").startswith("actions/upload-artifact")
    ]
    assert upload["uses"] == "actions/upload-artifact@v4"
    assert upload["with"]["name"] == "scorecard-db-${{ github.sha }}"
    assert "publish-db" not in jobs
    assert "download-artifact" not in text


def test_publish_db_reads_what_it_needs_and_nothing_more():
    workflow = yaml.safe_load(PUBLISH.read_text())
    assert granted(workflow, "publish-db") == PUBLISH_NEEDS["publish-db"]
    assert overreach(workflow, PUBLISH_NEEDS) == []


@pytest.mark.parametrize(
    "scopes",
    [
        "write-all",
        "read-all",
        {"actions": "write"},
        {"actions": "read", "contents": "write"},
        {"actions": "read", "contents": "read", "id-token": "write"},
    ],
)
def test_the_check_catches_a_wider_publish_token(scopes):
    workflow = yaml.safe_load(PUBLISH.read_text())
    workflow["jobs"]["publish-db"]["permissions"] = scopes
    assert overreach(workflow, PUBLISH_NEEDS)


def test_no_workflow_that_runs_on_pull_requests_names_a_secret():
    """ci.yml runs PyPI packages and each certified variant's pins on pull
    requests, as a user with passwordless sudo. No workflow that runs on
    pull requests may name a secret, even in a job or step that never runs
    for one: publish-db named the Supabase secrets inside ci.yml, push-only,
    until it moved to publish-db.yml."""
    found = {
        name: named_secrets(workflow) - SECRETS_ON_PULL_REQUESTS
        for name, workflow in workflows().items()
        if triggers(workflow) & PULL_REQUEST_EVENTS
    }
    assert {"ci.yml", "gate-freshness.yml"} <= set(found)
    assert {name: names for name, names in found.items() if names} == {}


def test_only_publish_db_names_the_supabase_secrets():
    """And the scanner sees them where they are."""
    named = {name: named_secrets(w) for name, w in workflows().items()}
    assert {name for name, names in named.items() if names & SUPABASE} == {
        "publish-db.yml"
    }
    assert named["publish-db.yml"] == SUPABASE
    assert not triggers(workflows()["publish-db.yml"]) & PULL_REQUEST_EVENTS


@pytest.mark.parametrize(
    "edit",
    [
        lambda w: w["jobs"]["app"]["steps"][0].update(
            env={"K": "${{ secrets.SUPABASE_SCORECARD_KEY }}"}
        ),
        lambda w: w["jobs"]["app"]["steps"][0].update(
            {"with": {"k": "${{ secrets['ANY_TOKEN'] }}"}}
        ),
        lambda w: w["jobs"]["app"]["steps"][0].update(
            {"with": {"k": '${{ secrets["ANY_TOKEN"] }}'}}
        ),
        lambda w: w["jobs"]["app"]["steps"].append(
            {"run": "echo '${{ toJSON(secrets) }}'"}
        ),
        lambda w: w["jobs"]["app"]["steps"].append(
            {"run": "echo ${{ secrets[format('{0}_KEY', 'X')] }}"}
        ),
        lambda w: w["jobs"]["app"]["steps"].append(
            {"if": "secrets.ANY_TOKEN != ''", "run": "true"}
        ),
        lambda w: w.update(env={"K": "${{ Secrets . any_token }}"}),
        lambda w: w["jobs"].update(
            call={"uses": "./.github/workflows/x.yml", "secrets": "inherit"}
        ),
        lambda w: w["jobs"]["app"]["steps"].append(
            {"run": "echo ${{ format('}}', secrets.SUPABASE_SCORECARD_KEY) }}"}
        ),
        lambda w: w["jobs"]["app"]["steps"].append(
            {"run": "echo ${{ format('it''s }}', secrets.ANY_TOKEN) }}"}
        ),
        lambda w: w["jobs"]["app"]["steps"].append(
            {"if": "${{ '}}' != secrets.ANY_TOKEN }}", "run": "true"}
        ),
    ],
    ids=[
        "step-env",
        "bracket-single",
        "bracket-double",
        "to-json",
        "computed-name",
        "bare-if",
        "case-and-spaces",
        "reusable-inherit",
        "braces-in-a-string",
        "escaped-quote-then-braces",
        "braces-in-an-if",
    ],
)
def test_the_scanner_catches_every_way_to_name_a_secret(edit):
    workflow = ci()
    assert named_secrets(workflow) == set()
    edit(workflow)
    assert named_secrets(workflow) - SECRETS_ON_PULL_REQUESTS


def test_the_template_reader_ends_where_github_does():
    assert templates("a ${{ x }} b ${{ y }}") == [" x ", " y "]
    assert templates("${{ format('}}', s) }}") == [" format('}}', s) "]
    assert templates("${{ 'it''s }}' }} tail") == [" 'it''s }}' "]
    assert templates("no expression }}") == []


def test_the_scanner_ignores_what_names_no_secret():
    """A property called secrets, the word in a script, and comments."""
    workflow = yaml.safe_load(CI.read_text() + "  # ${{ secrets.IN_A_COMMENT }}\n")
    workflow["jobs"]["app"]["steps"].append(
        {
            "if": "github.event.inputs.secrets == 'x'",
            "run": "echo 'no secrets here' ${{ github.event.inputs.secrets }}",
        }
    )
    assert named_secrets(workflow) == set()


@pytest.mark.skipif(not (ROOT / ".git").exists(), reason="needs a git checkout")
def test_the_database_is_not_tracked_here():
    """The property the guard checks, asserted for this tree too."""
    import subprocess

    tracked = subprocess.run(
        ["git", "ls-files", "data/scorecard.db"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    ).stdout.strip()
    assert not tracked, "data/scorecard.db is a derived artifact (#74)"
