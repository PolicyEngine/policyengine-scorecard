"""Catch up on policyengine.py releases whose dispatch never arrived.

Release qualification (W4) notifies this repository after each release, but
a missing GitHub App, an outage or a cancelled run can lose that dispatch.
The empty-request manual drain therefore also looks at PyPI itself: for each
stable release above both the certified and requested version floors, it
checks trusted-publisher provenance and the dispatch grace period before
building a ``released_bundle`` qualification request for the queue.

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
import io
import json
import os
import re
import sys
import urllib.error
import urllib.request
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

from packaging.version import Version

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline import uk_replay_qualify as qualify
from pipeline import uk_replay_variants as variants

PYPI = "https://pypi.org/pypi/{package}/json"
PROVENANCE = "https://pypi.org/integrity/policyengine/{version}/{filename}/provenance"
TRUSTED_PUBLISHER = {
    "kind": "GitHub",
    "repository": "PolicyEngine/policyengine.py",
    "workflow": "push.yaml",
    "environment": "pypi",
}
MANIFEST_PATH = "policyengine/data/bundle/manifest.json"
MAX_PER_RUN = 3
MAX_ATTEMPTS_PER_RUN = 30
MIN_RELEASE_AGE = timedelta(hours=6)
MAX_WHEEL_BYTES = 64 * 1024 * 1024
MAX_JSON_BYTES = 1024 * 1024
MAX_WHEEL_ENTRY_BYTES = 1024 * 1024
MAX_WHEEL_COMPRESSION_RATIO = 100
READ_CHUNK_BYTES = 64 * 1024
MAX_SKIP_REASON_LENGTH = 2000
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


def copy_response(response, destination, *, max_bytes: int) -> str:
    """Bound memory/disk use and hash response bytes as they arrive."""
    digest = hashlib.sha256()
    size = 0
    while payload := response.read(min(READ_CHUNK_BYTES, max_bytes - size + 1)):
        size += len(payload)
        if size > max_bytes:
            # An incomplete response has no whole-response digest, so this
            # resource refusal remains retryable rather than permanent.
            raise Skipped(f"response exceeds the {max_bytes}-byte limit")
        digest.update(payload)
        destination.write(payload)
    return digest.hexdigest()


def response_bytes(response) -> tuple[bytes, str]:
    destination = io.BytesIO()
    digest = copy_response(response, destination, max_bytes=MAX_JSON_BYTES)
    return destination.getvalue(), digest


def pypi(package: str, version: str | None = None) -> dict:
    url = PYPI.format(package=package if version is None else f"{package}/{version}")
    with urllib.request.urlopen(url, timeout=60) as response:  # Fixed HTTPS host.
        payload, _ = response_bytes(response)
    return json.loads(payload)


def trusted_provenance(version: str, filename: str) -> str:
    """Read PyPI's static JSON; require its exact reviewed publisher fields."""
    url = PROVENANCE.format(version=version, filename=filename)
    try:
        with urllib.request.urlopen(url, timeout=60) as response:
            payload, digest = response_bytes(response)
    except urllib.error.HTTPError as exc:
        # https://docs.pypi.org/api/integrity/ documents 404 as "file has no
        # provenance"; 403 is access "temporarily disabled by the PyPI
        # administrators" and 406 an unrecognised Accept header. Only a 404
        # is a permanent refusal: anything else is retried next drain, since a
        # recorded skip suppresses the release for good.
        if exc.code != 404:
            raise
        # Hash the actual error body as evidence, just as for an unreadable
        # successful response.
        with exc:
            payload, digest = response_bytes(exc)
        print(f"policyengine {version}: PyPI provenance sha256={digest}")
        raise Skipped(
            f"PyPI Trusted Publishing provenance unavailable (HTTP {exc.code})",
            permanent=True,
            evidence_sha256={"policyengine_provenance": digest},
        ) from exc
    print(f"policyengine {version}: PyPI provenance sha256={digest}")
    try:
        document = json.loads(payload)
        bundles = document["attestation_bundles"]
        accepted = isinstance(bundles, list) and any(
            isinstance(bundle, dict)
            # Every reviewed identity field must be present and equal. A field
            # PyPI adds later cannot change which repository, workflow and
            # environment published the wheel, and refusing it would record a
            # permanent skip for a genuine release.
            and isinstance(bundle.get("publisher"), dict)
            and all(
                key in bundle["publisher"] and bundle["publisher"][key] == value
                for key, value in TRUSTED_PUBLISHER.items()
            )
            and isinstance(bundle.get("attestations"), list)
            and any(
                isinstance(attestation, dict) and bool(attestation)
                for attestation in bundle["attestations"]
            )
            for bundle in bundles
        )
    except (ValueError, KeyError, TypeError, RecursionError):
        accepted = False
    if not accepted:
        raise Skipped(
            "PyPI provenance has no attestation from the required trusted publisher",
            permanent=True,
            evidence_sha256={"policyengine_provenance": digest},
        )
    return digest


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
        "upload_time": wheels[0].get("upload_time_iso_8601")
        or wheels[0].get("upload_time"),
    }


def requested_versions(state: Path) -> set[Version]:
    """Wrapper versions named by a recorded ``released_bundle`` request, in
    any status (complete, failed and rejected included).

    A pre-promotion ``candidate`` request names the version the candidate will
    be released as, but pins the candidate's wheels; push.yaml rebuilds the
    released wheel, and only a replay of those released bytes is evidence for
    the release (W4, 2026-10-16). So a candidate request neither covers nor
    floors the released version, and a missed release dispatch is still
    caught.
    """
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


def floor_versions(requested: set[Version], published: set[Version]) -> set[Version]:
    """Requested versions that raise the discovery floor: plain final releases
    (no epoch, local, pre, post or dev segment) that PyPI actually lists. A
    stored request naming a version PyPI has never published, however large,
    cannot stop discovery; it still counts against duplicating itself through
    requested_versions. A request for an unpublished candidate starts to count
    once that version is published."""
    return {
        version
        for version in requested & published
        if not (
            version.epoch
            or version.local
            or version.is_prerelease
            or version.is_devrelease
            or version.is_postrelease
        )
    }


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
    """Final releases above both the certified and requested floors, oldest first."""
    certified = {
        Version(r["identity"]["packages"]["policyengine"]["version"])
        for r in document["variants"]
        if r["status"] == "certified"
    }
    if not certified:
        print("no certified policyengine release; discovery has no baseline")
        return []
    requested = requested_versions(state)
    published = set()
    for value in set(all_versions):
        try:
            published.add(Version(value))
        except ValueError:
            continue
    floor = max(certified | floor_versions(requested, published))
    seen = requested | certified | skipped_versions(state)
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
    def read_entry(wheel, entry):
        if (
            entry.file_size > MAX_WHEEL_ENTRY_BYTES
            or entry.file_size
            > max(entry.compress_size, 1) * MAX_WHEEL_COMPRESSION_RATIO
        ):
            raise Skipped(
                f"wheel entry exceeds size or compression limit: {entry.filename}"
            )
        return wheel.read(entry)

    with zipfile.ZipFile(path) as wheel:
        manifest = read_entry(wheel, wheel.getinfo(MANIFEST_PATH))
        metadata = next(
            read_entry(wheel, entry).decode()
            for entry in wheel.infolist()
            if entry.filename.endswith(".dist-info/METADATA")
        )
    return manifest, metadata


def fetch(url: str, destination: Path, sha256: str) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        with (
            urllib.request.urlopen(url, timeout=300) as response,
            destination.open("wb") as output,
        ):
            digest = copy_response(response, output, max_bytes=MAX_WHEEL_BYTES)
        if digest != sha256:
            raise Skipped(f"{destination.name} bytes differ from PyPI's digest")
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    return destination


def release_manifest(data_package: dict, *, token: str | None) -> bytes:
    from huggingface_hub import hf_hub_download

    try:
        path = hf_hub_download(
            repo_id=data_package["repo_id"],
            # policyengine 6.5.0 policyengine/provenance/manifest.py:30-31
            # defaults DataPackageVersion's repo_type and manifest path.
            repo_type=data_package.get("repo_type", "model"),
            filename=data_package.get("release_manifest_path", "release_manifest.json"),
            revision=data_package.get("release_manifest_revision")
            or data_package["version"],
            token=token or None,
        )
    except Exception as exc:  # Retryable, never a permanent skip.
        raise Skipped(
            f"data release manifest unavailable: {type(exc).__name__}"
        ) from exc
    with Path(path).open("rb") as manifest:
        payload, _ = response_bytes(manifest)
    return payload


def provisional_request(
    version: str, work: Path, *, token: str | None, requested_by: dict, now: datetime
) -> dict:
    """A complete request from wheel metadata and the data release manifest."""
    wrapper = wheel_entry(pypi("policyengine", version))
    if not wrapper["upload_time"]:
        raise Skipped("the wheel's PyPI upload time is unavailable")
    uploaded = datetime.fromisoformat(wrapper["upload_time"].replace("Z", "+00:00"))
    if uploaded.tzinfo is None:
        uploaded = uploaded.replace(tzinfo=timezone.utc)
    if now - uploaded < MIN_RELEASE_AGE:
        raise Skipped("the wheel is inside the six-hour dispatch grace period")
    provenance_digest = trusted_provenance(version, wrapper["filename"])
    requested_by = {**requested_by, "pypi_provenance_sha256": provenance_digest}
    wheel = fetch(wrapper["url"], work / wrapper["filename"], wrapper["sha256"])
    manifest_bytes, metadata = read_wheel(wheel)
    evidence = {
        "policyengine_provenance": provenance_digest,
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
    core/tax_benefit_model_version.py:137-210 (6.4.1), :148-222 (6.5.0)
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
    state: Path, work: Path, *, token: str | None, requested_by: dict, now: datetime
) -> list[dict]:
    document = variants.load_document()
    try:
        versions = candidates(pypi("policyengine")["releases"], document, state)
    except Exception as exc:  # noqa: BLE001 - discovery must never block the drain
        print(f"policyengine release listing unavailable: {exc!r}")
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
                version, work / version, token=token, requested_by=requested_by, now=now
            )
            request_id = qualify.request_id(request)
        except Exception as exc:  # noqa: BLE001 - one bad release cannot stop catch-up
            print(f"policyengine {version}: not requested: {exc!r}")
            if isinstance(exc, Skipped) and exc.permanent and exc.evidence_sha256:
                try:
                    directory = state / "discovery" / "skipped"
                    directory.mkdir(parents=True, exist_ok=True)
                    (directory / f"{Version(version)}.json").write_text(
                        json.dumps(
                            {
                                "schema": "policyengine.uk-replay-discovery-skip/v1",
                                "version": str(Version(version)),
                                "reason": str(exc)[:MAX_SKIP_REASON_LENGTH],
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
                        f"policyengine {version}: could not record skip: {record_error!r}"
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
        args.state,
        args.work,
        token=token,
        requested_by=requested_by,
        now=datetime.now(timezone.utc),
    ):
        path = args.output_dir / f"{qualify.request_id(request)}.json"
        path.write_bytes(qualify.canonical_bytes(request))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
