"""Catch up on policyengine.py releases whose dispatch never arrived.

Release qualification (W4) notifies this repository after each release, but
a missing GitHub App, an outage or a cancelled run can lose that dispatch.
The scheduled receiver therefore also looks at PyPI itself: for every
policyengine release newer than the newest certified replay variant that no
request already names, it builds a ``released_bundle`` qualification request
and leaves it for the queue.

The request is built from primary artifacts: the wheel's SHA-256 from PyPI
(checked against the downloaded bytes), the packaged bundle manifest inside
that wheel (its SHA-256, the UK model and certified dataset), the model and
core wheel digests from PyPI (the model digest must equal the one the
manifest records), and the data release manifest from Hugging Face (its
SHA-256 and the dataset's size). The expected release bundle is read from
the wrapper installed in a scratch environment with tokens removed, so for
a discovered request the receiver's bundle check repeats that reading; the
artifact digests above are the independent part.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path

from packaging.version import Version

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline import uk_replay_qualify as qualify  # noqa: E402
from pipeline import uk_replay_variants as variants  # noqa: E402

PYPI = "https://pypi.org/pypi/{package}/json"
MANIFEST_PATH = "policyengine/data/bundle/manifest.json"
MAX_PER_RUN = 3
MAX_ATTEMPTS_PER_RUN = 30
EXTRA_PIN = re.compile(
    r"^(policyengine-uk|policyengine-core)\s*==\s*([^;\s]+)\s*;\s*extra\s*==\s*\"uk\"$"
)
BUNDLE_PROBE = """
import json, warnings
warnings.simplefilter("ignore")
from pipeline import uk_replay_variants as variants
variants.isolate_certification_environment()
import policyengine as pe
print(json.dumps(dict(pe.uk.uk_latest.release_bundle), sort_keys=True))
"""


class Skipped(Exception):
    """A release that cannot become a valid request; the reason is logged."""

    def __init__(
        self,
        reason: str,
        *,
        permanent: bool = False,
        evidence_sha256: dict[str, str] | None = None,
    ):
        super().__init__(reason)
        self.permanent = permanent
        self.evidence_sha256 = evidence_sha256 or {}


def pypi(package: str, version: str | None = None) -> dict:
    url = PYPI.format(package=package if version is None else f"{package}/{version}")
    with urllib.request.urlopen(url, timeout=60) as response:  # noqa: S310 - fixed https host
        return json.loads(response.read())


def wheel_entry(document: dict) -> dict:
    if document.get("yanked") or document.get("info", {}).get("yanked"):
        raise Skipped("the PyPI release is yanked")
    wheels = [u for u in document["urls"] if u["packagetype"] == "bdist_wheel"]
    if any(wheel.get("yanked") for wheel in wheels):
        raise Skipped("the PyPI wheel is yanked")
    if len(wheels) != 1:
        raise Skipped(f"expected one wheel, found {len(wheels)}")
    return {
        "filename": wheels[0]["filename"],
        "url": wheels[0]["url"],
        "sha256": wheels[0]["digests"]["sha256"],
    }


def requested_versions(state: Path) -> set[Version]:
    """Wrapper versions that already have a released_bundle request."""
    out = set()
    for path in (state / "requests").glob("*/REQUEST.json"):
        try:
            request = json.loads(path.read_text(encoding="utf-8"))
            if (
                not isinstance(request, dict)
                or request.get("kind") != "released_bundle"
            ):
                continue
            value = request["candidate"]["policyengine"]["version"]
            if isinstance(value, str):
                out.add(Version(value))
        except (OSError, ValueError, KeyError, TypeError):
            # Invalid requests are deliberately stored by the queue so the
            # drain can issue a rejection receipt for their canonical digest.
            continue
    return out


def skipped_versions(state: Path) -> set[Version]:
    out = set()
    for path in (state / "discovery" / "skipped").glob("*.json"):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
            out.add(Version(record["version"]))
        except (OSError, ValueError, KeyError, TypeError):
            continue
    return out


def yanked_release(release: list[dict] | dict) -> bool:
    if isinstance(release, dict):
        if release.get("yanked"):
            return True
        files = release.get("urls", [])
    else:
        files = release
    return (
        any(
            file.get("yanked") and file.get("packagetype") == "bdist_wheel"
            for file in files
        )
        or bool(files)
        and all(file.get("yanked") for file in files)
    )


def candidates(
    all_versions: list[str] | dict[str, list[dict] | dict], document: dict, state: Path
) -> list[str]:
    """Releases newer than the newest certified variant's wrapper, not yet
    requested, oldest first (so the queue replays them in release order)."""
    certified = {
        Version(r["identity"]["packages"]["policyengine"]["version"])
        for r in document["variants"]
        if r["status"] == "certified"
    }
    if not certified:
        print("no certified policyengine release; discovery has no baseline")
        return []
    floor = max(certified)
    seen = requested_versions(state) | certified | skipped_versions(state)
    out = {}
    for value in sorted(set(all_versions)):
        try:
            version = Version(value)
        except ValueError:
            continue
        if isinstance(all_versions, dict) and yanked_release(all_versions[value]):
            continue
        if version > floor and not version.is_prerelease and version not in seen:
            out.setdefault(version, value)
    return [out[version] for version in sorted(out)]


def uk_pins(
    metadata: str, *, evidence_sha256: dict[str, str] | None = None
) -> dict[str, str]:
    pins = {}
    for line in metadata.splitlines():
        if line.startswith("Requires-Dist:"):
            match = EXTRA_PIN.match(line.removeprefix("Requires-Dist:").strip())
            if match:
                pins[match.group(1)] = match.group(2)
    if set(pins) != {"policyengine-uk", "policyengine-core"}:
        raise Skipped(
            f"the wheel's uk extra pins {pins}, not exactly model and core",
            permanent=True,
            evidence_sha256=evidence_sha256,
        )
    return pins


def read_wheel(path: Path) -> tuple[bytes, str]:
    with zipfile.ZipFile(path) as wheel:
        manifest = wheel.read(MANIFEST_PATH)
        metadata = next(
            wheel.read(name).decode()
            for name in wheel.namelist()
            if name.endswith(".dist-info/METADATA")
        )
    return manifest, metadata


def fetch(url: str, destination: Path, sha256: str) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=300) as response:  # noqa: S310 - PyPI file URL
        payload = response.read()
    if hashlib.sha256(payload).hexdigest() != sha256:
        raise Skipped(f"{destination.name} bytes differ from PyPI's digest")
    destination.write_bytes(payload)
    return destination


def release_manifest(data_package: dict, *, token: str | None) -> bytes:
    from huggingface_hub import hf_hub_download

    try:
        path = hf_hub_download(
            repo_id=data_package["repo_id"],
            repo_type=data_package.get("repo_type") or "model",
            filename=data_package["release_manifest_path"],
            revision=data_package.get("release_manifest_revision")
            or data_package["version"],
            token=token or None,
        )
    except Exception as exc:  # noqa: BLE001 - retryable, never a permanent skip
        raise Skipped(
            f"data release manifest unavailable: {type(exc).__name__}"
        ) from exc
    return Path(path).read_bytes()


def provisional_request(
    version: str, work: Path, *, token: str | None, requested_by: dict
) -> dict:
    """Everything but the expected release bundle, from primary artifacts."""
    wrapper = wheel_entry(pypi("policyengine", version))
    wheel = fetch(wrapper["url"], work / wrapper["filename"], wrapper["sha256"])
    manifest_bytes, metadata = read_wheel(wheel)
    evidence = {
        "policyengine_wheel": wrapper["sha256"],
        "packaged_bundle_manifest": hashlib.sha256(manifest_bytes).hexdigest(),
    }
    uk = json.loads(manifest_bytes)["data_releases"]["uk"]
    # Only contradictions in verified immutable artifacts are permanent:
    # the wheel's UK pins, model version/digest, and data certification at a
    # pinned HF commit. Wheel counts, corrupt downloads and HF availability
    # can change on retry, as can a data manifest addressed by a movable tag.
    pins = uk_pins(metadata, evidence_sha256=evidence)
    model = uk["model_package"]
    if model["version"] != pins["policyengine-uk"]:
        raise Skipped(
            f"manifest model {model['version']} differs from the uk extra {pins['policyengine-uk']}",
            permanent=True,
            evidence_sha256=evidence,
        )
    uk_wheel = wheel_entry(pypi("policyengine-uk", model["version"]))
    evidence["policyengine_uk_wheel"] = uk_wheel["sha256"]
    if model.get("sha256") and model["sha256"] != uk_wheel["sha256"]:
        raise Skipped(
            "the manifest's model wheel digest differs from PyPI's",
            permanent=True,
            evidence_sha256=evidence,
        )
    core_wheel = wheel_entry(pypi("policyengine-core", pins["policyengine-core"]))
    evidence["policyengine_core_wheel"] = core_wheel["sha256"]
    artifact = uk["certified_data_artifact"]
    dataset = uk["datasets"][artifact["dataset"]]
    manifest_payload = release_manifest(uk["data_package"], token=token)
    evidence["data_release_manifest"] = hashlib.sha256(manifest_payload).hexdigest()
    released = json.loads(manifest_payload)["artifacts"].get(artifact["dataset"])
    if released is None or released.get("sha256") != artifact["sha256"]:
        revision = uk["data_package"].get("release_manifest_revision", "")
        raise Skipped(
            "the data release manifest does not certify the bundle's dataset",
            permanent=bool(re.fullmatch(r"[0-9a-f]{40}", revision)),
            evidence_sha256=evidence,
        )
    return {
        "schema": "policyengine.uk-replay-qualification-request/v1",
        "kind": "released_bundle",
        "attempt": 1,
        "candidate": {
            "policyengine": {
                "version": version,
                "source": {"pypi": {"wheel_sha256": wrapper["sha256"]}},
                "packaged_bundle_manifest_sha256": hashlib.sha256(
                    manifest_bytes
                ).hexdigest(),
            },
            "policyengine_uk": {
                "version": model["version"],
                "wheel_sha256": uk_wheel["sha256"],
            },
            "policyengine_core": {
                "version": pins["policyengine-core"],
                "wheel_sha256": core_wheel["sha256"],
            },
            "data": {
                "build_id": artifact["build_id"],
                "dataset": artifact["dataset"],
                "repo_id": dataset["repo_id"],
                "repo_type": dataset.get("repo_type")
                or uk["data_package"].get("repo_type")
                or "model",
                "revision": dataset["revision"],
                "path": dataset["path"],
                "sha256": artifact["sha256"],
                "size_bytes": released["size_bytes"],
                "release_manifest_sha256": hashlib.sha256(manifest_payload).hexdigest(),
            },
            "expected_release_bundle": {},
        },
        "compare_to": "latest_certified",
        "requested_by": requested_by,
    }


def expected_bundle(request: dict, work: Path) -> dict:
    """Install the release exactly as the receiver will, then read its bundle."""
    venv = work / "venv"
    credentials = {
        "HUGGING_FACE_TOKEN",
        "HF_TOKEN",
        "HUGGING_FACE_HUB_TOKEN",
        "HUGGINGFACE_HUB_TOKEN",
        "GITHUB_TOKEN",
    }
    environment = {
        **{key: value for key, value in os.environ.items() if key not in credentials},
        "PYTHONPATH": str(ROOT),
    }
    work.mkdir(parents=True, exist_ok=True)
    request_file = work / "REQUEST.json"
    request_file.write_bytes(qualify.canonical_bytes(request))
    # Installers can run release code too; run prepare in a credential-free
    # control subprocess so its own children inherit the same environment.
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pipeline.uk_replay_qualify",
            "prepare",
            "--request",
            str(request_file.resolve()),
            "--venv",
            str(venv.resolve()),
            "--wheels",
            str((work / "wheels").resolve()),
            "--output",
            str((work / "wheel-digests.json").resolve()),
        ],
        cwd=ROOT,
        env=environment,
        check=True,
    )
    result = subprocess.run(
        [str(venv / "bin" / "python"), "-c", BUNDLE_PROBE],
        cwd=ROOT,
        env=environment,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout.strip().splitlines()[-1])


def discover(
    state: Path, work: Path, *, token: str | None, requested_by: dict
) -> list[dict]:
    document = variants.load_document()
    try:
        versions = candidates(pypi("policyengine")["releases"], document, state)
    except Exception as exc:  # noqa: BLE001 - discovery must never block the drain
        print(f"policyengine release listing unavailable: {type(exc).__name__}: {exc}")
        return []
    requests = []
    for attempt, version in enumerate(versions, start=1):
        if len(requests) >= MAX_PER_RUN or attempt > MAX_ATTEMPTS_PER_RUN:
            print(
                f"discovery limit reached: {len(requests)} requests, {attempt - 1} attempts; "
                "remaining releases will be considered on later runs"
            )
            break
        try:
            request = provisional_request(
                version, work / version, token=token, requested_by=requested_by
            )
            request["candidate"]["expected_release_bundle"] = expected_bundle(
                request, work / version
            )
            request_id = qualify.request_id(request)
        except Exception as exc:  # noqa: BLE001 - one bad release cannot stop catch-up
            print(f"policyengine {version}: not requested: {type(exc).__name__}: {exc}")
            if isinstance(exc, Skipped) and exc.permanent and exc.evidence_sha256:
                try:
                    directory = state / "discovery" / "skipped"
                    directory.mkdir(parents=True, exist_ok=True)
                    (directory / f"{Version(version)}.json").write_text(
                        json.dumps(
                            {
                                "schema": "policyengine.uk-replay-discovery-skip/v1",
                                "version": str(Version(version)),
                                "reason": str(exc),
                                "evidence_sha256": exc.evidence_sha256,
                            },
                            sort_keys=True,
                            indent=1,
                        )
                        + "\n",
                        encoding="utf-8",
                    )
                except Exception as record_error:  # noqa: BLE001 - keep draining
                    print(
                        f"policyengine {version}: could not record skip: {record_error}"
                    )
            continue
        requests.append(request)
        print(f"policyengine {version}: request {request_id}")
    return requests


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--run-id", type=int)
    args = parser.parse_args(argv)
    requested_by = {
        "repository": "PolicyEngine/policyengine-scorecard",
        "commit": args.commit,
        "trigger": "scheduled catch-up of an undispatched policyengine.py release",
    }
    if args.run_id:
        requested_by["workflow_run_id"] = args.run_id
    token = os.environ.get("HUGGING_FACE_TOKEN") or os.environ.get("HF_TOKEN")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for request in discover(
        args.state, args.work, token=token, requested_by=requested_by
    ):
        path = args.output_dir / f"{qualify.request_id(request)}.json"
        path.write_bytes(qualify.canonical_bytes(request))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
