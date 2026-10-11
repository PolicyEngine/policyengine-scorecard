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


def pypi(package: str, version: str | None = None) -> dict:
    url = PYPI.format(package=package if version is None else f"{package}/{version}")
    with urllib.request.urlopen(url, timeout=60) as response:  # noqa: S310 - fixed https host
        return json.loads(response.read())


def wheel_entry(document: dict) -> dict:
    wheels = [u for u in document["urls"] if u["packagetype"] == "bdist_wheel"]
    if len(wheels) != 1:
        raise Skipped(f"expected one wheel, found {len(wheels)}")
    return {
        "filename": wheels[0]["filename"],
        "url": wheels[0]["url"],
        "sha256": wheels[0]["digests"]["sha256"],
    }


def requested_versions(state: Path) -> set[str]:
    """Wrapper versions that already have a released_bundle request."""
    out = set()
    for path in (state / "requests").glob("*/REQUEST.json"):
        request = json.loads(path.read_text(encoding="utf-8"))
        if request.get("kind") == "released_bundle":
            out.add(request["candidate"]["policyengine"]["version"])
    return out


def candidates(all_versions: list[str], document: dict, state: Path) -> list[str]:
    """Releases newer than the newest certified variant's wrapper, not yet
    requested, oldest first (so the queue replays them in release order)."""
    certified = [
        Version(r["identity"]["packages"]["policyengine"]["version"])
        for r in document["variants"]
        if r["status"] == "certified"
    ]
    floor = max(certified)
    seen = requested_versions(state) | {str(v) for v in certified}
    out = []
    for value in set(all_versions):
        try:
            version = Version(value)
        except ValueError:
            continue
        if version > floor and not version.is_prerelease and value not in seen:
            out.append(value)
    return sorted(out, key=Version)


def uk_pins(metadata: str) -> dict[str, str]:
    pins = {}
    for line in metadata.splitlines():
        if line.startswith("Requires-Dist:"):
            match = EXTRA_PIN.match(line.removeprefix("Requires-Dist:").strip())
            if match:
                pins[match.group(1)] = match.group(2)
    if set(pins) != {"policyengine-uk", "policyengine-core"}:
        raise Skipped(f"the wheel's uk extra pins {pins}, not exactly model and core")
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
    except Exception as exc:  # noqa: BLE001 - recorded as a skip
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
    uk = json.loads(manifest_bytes)["data_releases"]["uk"]
    pins = uk_pins(metadata)
    model = uk["model_package"]
    if model["version"] != pins["policyengine-uk"]:
        raise Skipped(
            f"manifest model {model['version']} differs from the uk extra {pins['policyengine-uk']}"
        )
    uk_wheel = wheel_entry(pypi("policyengine-uk", model["version"]))
    if model.get("sha256") and model["sha256"] != uk_wheel["sha256"]:
        raise Skipped("the manifest's model wheel digest differs from PyPI's")
    core_wheel = wheel_entry(pypi("policyengine-core", pins["policyengine-core"]))
    artifact = uk["certified_data_artifact"]
    dataset = uk["datasets"][artifact["dataset"]]
    manifest_payload = release_manifest(uk["data_package"], token=token)
    released = json.loads(manifest_payload)["artifacts"].get(artifact["dataset"])
    if released is None or released.get("sha256") != artifact["sha256"]:
        raise Skipped("the data release manifest does not certify the bundle's dataset")
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
                "repo_type": uk["data_package"].get("repo_type") or "model",
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
    qualify.prepare(request, venv, work / "wheels")
    result = subprocess.run(
        [str(venv / "bin" / "python"), "-c", BUNDLE_PROBE],
        cwd=ROOT,
        env={**os.environ, "PYTHONPATH": str(ROOT)},
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout.strip().splitlines()[-1])


def discover(
    state: Path, work: Path, *, token: str | None, requested_by: dict
) -> list[dict]:
    document = variants.load_document()
    versions = candidates(list(pypi("policyengine")["releases"]), document, state)
    if len(versions) > MAX_PER_RUN:
        print(
            f"{len(versions)} unreplayed releases; building the oldest {MAX_PER_RUN} now, "
            f"the rest on later runs: {versions[MAX_PER_RUN:]}"
        )
    requests = []
    for version in versions[:MAX_PER_RUN]:
        try:
            request = provisional_request(
                version, work / version, token=token, requested_by=requested_by
            )
            request["candidate"]["expected_release_bundle"] = expected_bundle(
                request, work / version
            )
            qualify.request_id(request)
        except (Skipped, qualify.Rejected, subprocess.CalledProcessError) as exc:
            print(f"policyengine {version}: not requested: {exc}")
            continue
        requests.append(request)
        print(f"policyengine {version}: request {qualify.request_id(request)}")
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
