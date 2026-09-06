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
"""

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
CI = ROOT / ".github" / "workflows" / "ci.yml"
FRESHNESS = ROOT / ".github" / "workflows" / "gate-freshness.yml"


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
