"""Export the complete UK-extra freeze from a policyengine.py release tag.

Copies only pyproject.toml, uv.lock and README.md from the local repository's
tag into a temporary directory. ``uv export`` runs frozen, offline and without
an uv cache. It never creates a worktree, environment or downloads a dataset.
Install the emitted freeze using ``uv pip install --no-deps -r <freeze>``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path

import tomllib

from pipeline.uk_bundle import ROOT, _key


def _git_file(repository, tag, name):
    return subprocess.run(
        ["git", "-C", str(repository), "show", f"{tag}:{name}"],
        check=True,
        capture_output=True,
    ).stdout


def export_requirements(repository, tag, key, *, uv="uv"):
    _key(key)
    if not tag or tag.startswith("-") or ":" in tag:
        raise ValueError("invalid release tag")
    project = _git_file(repository, tag, "pyproject.toml")
    lock = _git_file(repository, tag, "uv.lock")
    version = tomllib.loads(project.decode())["project"]["version"]
    if tag.removeprefix("v") != version:
        raise ValueError("tag differs from project release version")
    commit = subprocess.run(
        ["git", "-C", str(repository), "rev-parse", f"{tag}^{{commit}}"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    with tempfile.TemporaryDirectory(prefix="uk-bundle-freeze-") as temporary:
        directory = Path(temporary)
        (directory / "pyproject.toml").write_bytes(project)
        (directory / "uv.lock").write_bytes(lock)
        (directory / "README.md").write_bytes(_git_file(repository, tag, "README.md"))
        command = [
            uv,
            "export",
            "--frozen",
            "--no-hashes",
            "--no-dev",
            "--extra",
            "uk",
            "--no-emit-project",
            "--offline",
            "--no-cache",
        ]
        result = subprocess.run(
            command,
            cwd=directory,
            check=True,
            capture_output=True,
            text=True,
            env={**os.environ, "UV_NO_CACHE": "1"},
        )
    # Strip uv's location-dependent generated header and bind the actual inputs.
    exported = "\n".join(
        line for line in result.stdout.splitlines() if not line.startswith("#")
    ).strip()
    freeze = f"# UK replay bundle {key}\n# policyengine.py tag {tag}, commit {commit}\n# uv.lock SHA-256 {hashlib.sha256(lock).hexdigest()}\n# uv export --frozen --no-hashes --no-dev --extra uk --no-emit-project\n{exported}\npolicyengine=={version}\n"
    provenance = {
        "bundle_key": key,
        "policyengine_tag": tag,
        "policyengine_commit": commit,
        "uv_lock_sha256": hashlib.sha256(lock).hexdigest(),
        "freeze_sha256": hashlib.sha256(freeze.encode()).hexdigest(),
        "export_command": command,
    }
    return freeze, provenance


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", required=True, type=Path)
    parser.add_argument("--tag", required=True)
    parser.add_argument("--key", required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--uv", default="uv")
    args = parser.parse_args(argv)
    freeze, provenance = export_requirements(
        args.repository, args.tag, args.key, uv=args.uv
    )
    path = args.output or ROOT / "docs/uk_replay" / f"requirements-{args.key}.txt"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(freeze)
    path.with_suffix(".provenance.json").write_text(
        json.dumps(provenance, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps({"output": str(path), **provenance}, sort_keys=True))


if __name__ == "__main__":
    main()
