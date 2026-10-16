"""Catch up on policyengine.py releases whose dispatch never arrived.

Release qualification (W4) notifies this repository after each release, but
a missing GitHub App, an outage or a cancelled run can lose that dispatch.
The empty-request manual drain therefore also looks at PyPI itself: for every
policyengine release newer than the newest certified replay variant that no
request already names, it builds a ``released_bundle`` qualification request
and leaves it for the queue.

The request is built from primary artifacts: the wheel's SHA-256 from PyPI
(checked against the downloaded bytes), the packaged bundle manifest inside
that wheel (its SHA-256, the UK model and certified dataset), the model and
core wheel digests from PyPI (the model digest must equal the one the
manifest records), and the data release manifest from Hugging Face (its
SHA-256 and the dataset's size). The expected release bundle is projected
statically from the wheel's packaged manifest. No package is installed or
imported and no release code runs here, including in the step that holds
the read-only data token. The receiver independently checks that projection
against the installed release under packaged certification in its sandbox.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import urllib.request
import zipfile
from pathlib import Path

from packaging.version import Version

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline import uk_replay_qualify as qualify
from pipeline import uk_replay_variants as variants

PYPI = "https://pypi.org/pypi/{package}/json"
MANIFEST_PATH = "policyengine/data/bundle/manifest.json"
MAX_PER_RUN = 3
MAX_ATTEMPTS_PER_RUN = 30
EXTRA_PIN = re.compile(
    r"^(policyengine-uk|policyengine-core)\s*==\s*([^;\s]+)\s*;\s*extra\s*==\s*\"uk\"$"
)


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
    with urllib.request.urlopen(url, timeout=60) as response:  # Fixed HTTPS host.
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
    """Wrapper versions named by a candidate or released-bundle request.

    W4 may already be qualifying a release before promotion. Its candidate
    request counts too, including when it is queued or running.
    """
    out = set()
    for path in (state / "requests").glob("*/REQUEST.json"):
        try:
            request = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(request, dict) or request.get("kind") not in {
                "candidate",
                "released_bundle",
            }:
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
    with urllib.request.urlopen(url, timeout=300) as response:  # PyPI file URL.
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
    except Exception as exc:  # Retryable, never a permanent skip.
        raise Skipped(
            f"data release manifest unavailable: {type(exc).__name__}"
        ) from exc
    return Path(path).read_bytes()


def provisional_request(
    version: str, work: Path, *, token: str | None, requested_by: dict
) -> dict:
    """A complete request from wheel metadata and the data release manifest."""
    wrapper = wheel_entry(pypi("policyengine", version))
    wheel = fetch(wrapper["url"], work / wrapper["filename"], wrapper["sha256"])
    manifest_bytes, metadata = read_wheel(wheel)
    evidence = {
        "policyengine_wheel": wrapper["sha256"],
        "packaged_bundle_manifest": hashlib.sha256(manifest_bytes).hexdigest(),
    }
    manifest = json.loads(manifest_bytes)
    uk = manifest["data_releases"]["uk"]
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
    bundle = expected_bundle(manifest, evidence_sha256=evidence)
    if bundle["policyengine_version"] != version:
        raise Skipped(
            "the manifest's wrapper version differs from the PyPI release",
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
            "expected_release_bundle": bundle,
        },
        "compare_to": "latest_certified",
        "requested_by": requested_by,
    }


def expected_bundle(
    manifest: dict, *, evidence_sha256: dict[str, str] | None = None
) -> dict:
    """Project the successful packaged-certification bundle without release code.

    Read from both policyengine 6.4.1 and 6.5.0 wheels: provenance/manifest.py
    :321-335 reads this manifest, :395-422 returns its certification offline
    for the pinned model, and :184-191 chooses the certified default URI.
    core/tax_benefit_model_version.py:137-210 (6.4.1), :149-222 (6.5.0)
    defines precisely these fields. Missing optional fields remain JSON null.
    A nonlegacy runtime fingerprint mismatch can reject certification; it
    never changes a successful bundle. The receiver still checks at runtime.
    """
    uk = manifest["data_releases"]["uk"]
    model, data = uk["model_package"], uk["data_package"]
    certification = uk.get("certification")
    artifact = uk["certified_data_artifact"]
    if (
        uk.get("country_id") != "uk"
        or model.get("name") != "policyengine-uk"
        or certification is None
        or certification.get("certified_for_model_version") != model["version"]
        or uk.get("default_dataset") != artifact["dataset"]
    ):
        raise Skipped(
            "the packaged manifest does not certify its pinned UK model and default dataset",
            permanent=True,
            evidence_sha256=evidence_sha256,
        )
    return {
        "bundle_id": uk.get("bundle_id"),
        "country_id": uk["country_id"],
        "policyengine_version": uk["policyengine_version"],
        "model_package": model["name"],
        "model_version": model["version"],
        "data_package": data["name"],
        "data_version": data["version"],
        "default_dataset": uk["default_dataset"],
        "default_dataset_uri": artifact["uri"],
        # A present certification's null build id does not fall back to the
        # artifact's build id in the release_bundle property.
        "certified_data_build_id": certification.get("data_build_id"),
        "certified_data_artifact_sha256": artifact.get("sha256"),
        "data_build_model_version": certification.get("built_with_model_version"),
        "data_build_model_git_sha": certification.get("built_with_model_git_sha"),
        "data_build_fingerprint": certification.get("data_build_fingerprint"),
        "compatibility_basis": certification["compatibility_basis"],
        "certified_by": certification.get("certified_by"),
    }


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
