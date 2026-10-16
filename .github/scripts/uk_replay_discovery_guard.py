"""Validate the entire public discovery batch before any replay-state write.

No wheel, release code, dataset credential or discovery network call belongs
in this program. The write job uses only the vendored request schema and
the trusted queue implementation. Its shell caller also applies the
receiver's format/size/output guard before invoking this validator.
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import jsonschema
from packaging.version import Version

from pipeline import uk_replay_interface as interface
from pipeline import uk_replay_queue as queue

SKIP_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["schema", "version", "reason", "evidence_sha256"],
    "properties": {
        "schema": {"const": "policyengine.uk-replay-discovery-skip/v1"},
        "version": {"type": "string", "maxLength": 100},
        "reason": {"type": "string", "minLength": 1, "maxLength": 2000},
        "evidence_sha256": {
            "type": "object",
            "minProperties": 1,
            "maxProperties": 10,
            "additionalProperties": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
        },
    },
}


def validate_batch(root: Path) -> tuple[list[dict], list[Path]]:
    """All-or-nothing validation, including metadata names and artifact shape."""
    if root.is_symlink() or not root.is_dir():
        raise ValueError("discovery metadata must be a directory")
    requests, skips, seen = [], [], set()
    for directory in sorted(root.iterdir()):
        if (
            directory.name not in {"requests", "skipped"}
            or directory.is_symlink()
            or not directory.is_dir()
        ):
            raise ValueError(f"unexpected discovery entry: {directory.name}")
        for path in sorted(directory.iterdir()):
            if path.is_symlink() or not path.is_file() or path.suffix != ".json":
                raise ValueError(f"unexpected discovery metadata: {path.name}")
            record = json.loads(path.read_bytes())
            if directory.name == "requests":
                request_id = interface.validate_request(record)
                if (
                    record["kind"] != "released_bundle"
                    or "pypi" not in (record["candidate"]["policyengine"]["source"])
                ):
                    raise ValueError("discovery may enqueue only released PyPI bundles")
                if path.name != f"{request_id}.json":
                    raise ValueError(
                        "discovered request filename differs from its digest"
                    )
                version = Version(record["candidate"]["policyengine"]["version"])
                requests.append(record)
            else:
                jsonschema.Draft202012Validator(SKIP_SCHEMA).validate(record)
                version = Version(record["version"])
                if path.name != f"{version}.json":
                    raise ValueError("skip filename differs from its release version")
                skips.append(path)
            if version in seen or version.is_prerelease or version.is_devrelease:
                raise ValueError(
                    f"duplicate or prerelease discovery version: {version}"
                )
            seen.add(version)
    if len(requests) > 3 or len(skips) > 30:
        raise ValueError("discovery batch exceeds its per-run bounds")
    return requests, skips


def requested_versions(state: Path) -> set[Version]:
    """A recorded ``released_bundle`` request, in any status, covers its
    wrapper version.

    The queue also stores invalid requests to give rejections an address;
    tolerate those. A pre-promotion ``candidate`` request does not cover the
    released version: the released wheel is rebuilt by push.yaml, and its
    replay is the evidence (pipeline/uk_replay_discover.requested_versions).
    """
    versions = set()
    for path in (state / "requests").glob("*/REQUEST.json"):
        try:
            request = json.loads(path.read_bytes())
            if request["kind"] != "released_bundle":
                continue
            value = request["candidate"]["policyengine"]["version"]
            if isinstance(value, str):
                versions.add(Version(value))
        except (OSError, ValueError, KeyError, TypeError):
            continue
    return versions


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("command", choices=["validate", "enqueue"])
    parser.add_argument("root", type=Path)
    parser.add_argument("--state", type=Path)
    parser.add_argument("--run-url")
    parser.add_argument("--now")
    args = parser.parse_args(argv)
    requests, skips = validate_batch(args.root)
    if args.command == "validate":
        return 0
    if args.state is None or args.run_url is None or args.now is None:
        parser.error("enqueue requires --state, --run-url and --now")
    seen = requested_versions(args.state)
    for request in requests:
        version = Version(request["candidate"]["policyengine"]["version"])
        if version in seen:
            print(f"policyengine {version}: already requested; not enqueued")
            continue
        request_id, status = queue.enqueue(
            args.state, request, run_url=args.run_url, now=args.now
        )
        seen.add(version)
        print(f"{request_id} {status}")
    for path in skips:
        destination = args.state / "discovery" / "skipped" / path.name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
