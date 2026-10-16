"""Run discovery's snapshot and metadata handoff without network or installers."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = (
    Path(__file__).resolve().parent.parent / ".github/scripts/uk_replay_discover.sh"
)


@pytest.fixture
def discovery_shell(tmp_path):
    binaries = tmp_path / "bin"
    binaries.mkdir()
    # The fake remote holds only public state metadata. The shell still runs
    # its real branch-exists/fetch/snapshot path and copies its own baseline.
    git = binaries / "git"
    git.write_text(
        f"#!{sys.executable}\n"
        "import os, shutil, sys\n"
        "from pathlib import Path\n"
        "remote = Path(os.environ['FAKE_REMOTE'])\n"
        "args = sys.argv[1:]\n"
        "if args[0] == 'ls-remote':\n"
        "    sys.exit(0 if remote.is_dir() else 2)\n"
        "if args[0] == 'fetch':\n"
        "    sys.exit(0)\n"
        "if args[:2] == ['worktree', 'add']:\n"
        "    shutil.copytree(remote, args[-2], symlinks=True)\n"
        "    sys.exit(0)\n"
        "raise AssertionError(args)\n"
    )
    # Behave like only the discovery module's filesystem outputs: create its
    # request directory and optionally record one new immutable skip in state.
    # No uv, package installer or separate virtual environment actually runs.
    uv = binaries / "uv"
    uv.write_text(
        f"#!{sys.executable}\n"
        "import json, os, sys\n"
        "from pathlib import Path\n"
        "args = sys.argv[1:]\n"
        "assert args[:1] == ['run']\n"
        "assert args[args.index('-m') + 1] == 'pipeline.uk_replay_discover'\n"
        "output = Path(args[args.index('--output-dir') + 1])\n"
        "output.mkdir(parents=True, exist_ok=True)\n"
        "if os.environ.get('FAKE_NEW_SKIP'):\n"
        "    state = Path(args[args.index('--state') + 1])\n"
        "    record = json.loads(os.environ['FAKE_NEW_SKIP'])\n"
        "    target = state / 'discovery' / 'skipped' / (record['version'] + '.json')\n"
        "    target.parent.mkdir(parents=True, exist_ok=True)\n"
        "    target.write_text(json.dumps(record))\n"
    )
    git.chmod(0o755)
    uv.chmod(0o755)
    runner_temp = tmp_path / "runner-temp"
    runner_temp.mkdir()
    environment = {
        **os.environ,
        "PATH": f"{binaries}:{os.environ['PATH']}",
        "STATE": str(tmp_path / "state"),
        "STATE_BRANCH": "replay-state",
        "DISCOVERY_DIR": str(tmp_path / "discovery"),
        "RUNNER_TEMP": str(runner_temp),
        "GITHUB_OUTPUT": str(tmp_path / "github-output"),
        "GITHUB_SHA": "0" * 40,
        "GITHUB_RUN_ID": "1",
        "FAKE_REMOTE": str(tmp_path / "remote"),
    }

    def run(command, **overrides):
        return subprocess.run(
            ["bash", str(SCRIPT), command],
            env={**environment, **overrides},
            cwd=tmp_path,
            capture_output=True,
            text=True,
            check=True,
        )

    return tmp_path, environment, run


def test_missing_state_branch_and_empty_discovery_have_no_artifact(discovery_shell):
    root, environment, run = discovery_shell
    run("snapshot")
    assert Path(environment["STATE"]).is_dir()
    run("run")
    assert (root / "github-output").read_text() == "has_metadata=false\n"
    assert list((root / "discovery" / "requests").iterdir()) == []
    assert list((root / "discovery" / "skipped").iterdir()) == []


@pytest.mark.parametrize("new_skip", [False, True])
def test_snapshot_transfers_only_new_skip_metadata(discovery_shell, new_skip):
    root, environment, run = discovery_shell
    historical = {"version": "6.5.0", "reason": "old immutable mismatch"}
    remote = Path(environment["FAKE_REMOTE"]) / "discovery" / "skipped"
    remote.mkdir(parents=True)
    historical_bytes = json.dumps(historical).encode()
    (remote / "6.5.0.json").write_bytes(historical_bytes)

    run("snapshot")
    baseline = root / "runner-temp" / "discovery-existing-skips" / "6.5.0.json"
    assert baseline.read_bytes() == historical_bytes
    new = {"version": "6.5.1", "reason": "new immutable mismatch"}
    run("run", FAKE_NEW_SKIP=json.dumps(new) if new_skip else "")

    skipped = root / "discovery" / "skipped"
    assert not (skipped / "6.5.0.json").exists()
    assert (remote / "6.5.0.json").read_bytes() == historical_bytes
    assert baseline.read_bytes() == historical_bytes
    assert {path.name for path in skipped.iterdir()} == (
        {"6.5.1.json"} if new_skip else set()
    )
    if new_skip:
        assert json.loads((skipped / "6.5.1.json").read_bytes()) == new
    assert (root / "github-output").read_text() == (
        f"has_metadata={str(new_skip).lower()}\n"
    )


def test_snapshot_and_handoff_skip_symlinks(discovery_shell):
    root, environment, run = discovery_shell
    remote = Path(environment["FAKE_REMOTE"]) / "discovery" / "skipped"
    remote.mkdir(parents=True)
    outside = root / "outside.json"
    outside.write_text('{"version":"6.7.0","reason":"not state metadata"}')
    (remote / "6.7.0.json").symlink_to(outside)

    run("snapshot")
    baseline = root / "runner-temp" / "discovery-existing-skips"
    assert list(baseline.iterdir()) == []
    assert (Path(environment["STATE"]) / "discovery/skipped/6.7.0.json").is_symlink()
    run("run")
    assert list((root / "discovery/skipped").iterdir()) == []
    assert (root / "github-output").read_text() == "has_metadata=false\n"
