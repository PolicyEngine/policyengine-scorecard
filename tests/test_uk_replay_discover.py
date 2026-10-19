"""Catch-up discovery of undispatched policyengine.py releases.

PyPI, the wheel and the data release manifest are stubbed; candidate code
is never imported, installed or executed while building a request.
"""

import hashlib
import io
import json
import subprocess
import sys
import types
import urllib.error
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from packaging.version import Version

from pipeline import uk_replay_discover as discover
from pipeline import uk_replay_qualify as qualify
from pipeline import uk_replay_variants as rv

FIXTURES = Path(__file__).parent / "fixtures" / "uk_replay"
NOW = datetime(2026, 10, 16, tzinfo=timezone.utc)
UPLOAD_TIME = "2026-10-15T00:00:00Z"
PROVENANCE_DOCUMENT = {
    "version": 1,
    "attestation_bundles": [
        {
            "publisher": {
                "kind": "GitHub",
                "repository": "PolicyEngine/policyengine.py",
                "workflow": "push.yaml",
                "environment": "pypi",
            },
            "attestations": [{"version": 1}],
        }
    ],
}
PROVENANCE_BYTES = json.dumps(PROVENANCE_DOCUMENT).encode()
PROVENANCE_DIGEST = hashlib.sha256(PROVENANCE_BYTES).hexdigest()
REQUESTED_BY = {"repository": "PolicyEngine/policyengine-scorecard", "commit": "0" * 40}
REAL_FETCH = discover.fetch
REAL_RELEASE_MANIFEST = discover.release_manifest
# The floor cases below were written when 6.5.0 was the newest certified
# variant. Each newly certified variant is appended to the committed index
# (pipeline/uk_replay_results_pr.py), so they read the index as it stood then,
# both where a test passes it in and where discover() loads it itself.
FLOOR_VARIANT = "pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1"
LOAD_DOCUMENT = rv.load_document


def floor_document():
    document = LOAD_DOCUMENT()
    ids = [v["variant_id"] for v in document["variants"]]
    document["variants"] = document["variants"][: ids.index(FLOOR_VARIANT) + 1]
    return document


@pytest.fixture(autouse=True)
def index_at_the_floor(monkeypatch):
    # discover() reads the committed index through variants.load_document();
    # a test that needs another index patches it again itself.
    monkeypatch.setattr(discover.variants, "load_document", floor_document)


def test_the_floor_index_ends_at_6_5_0_whatever_main_has_certified_since():
    assert discover.variants.load_document()["variants"][-1]["variant_id"] == (
        FLOOR_VARIANT
    )
    assert [v["variant_id"] for v in floor_document()["variants"]] == [
        v["variant_id"] for v in LOAD_DOCUMENT()["variants"]
    ][: len(floor_document()["variants"])]


@pytest.fixture(autouse=True)
def forbid_network(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("tests must not access the network")

    monkeypatch.setattr(discover.urllib.request, "urlopen", forbidden)


def golden():
    return json.loads((FIXTURES / "qualification_request_golden.json").read_text())


def request_for(version):
    request = golden()
    request["kind"] = "released_bundle"
    request["candidate"]["policyengine"]["source"] = {
        "pypi": {"wheel_sha256": "a" * 64}
    }
    request["candidate"]["policyengine"]["version"] = version
    request["candidate"]["expected_release_bundle"]["policyengine_version"] = version
    return request


def wheel_bytes(manifest: dict, requires: list[str]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as wheel:
        wheel.writestr(discover.MANIFEST_PATH, json.dumps(manifest))
        wheel.writestr(
            "policyengine-6.5.0.dist-info/METADATA",
            "Metadata-Version: 2.1\nName: policyengine\nVersion: 6.5.0\n"
            + "".join(f"Requires-Dist: {line}\n" for line in requires),
        )
    return buffer.getvalue()


def bundle_manifest(model_sha="b" * 64, dataset_sha="d" * 64, version="6.5.0"):
    return {
        "data_releases": {
            "uk": {
                "bundle_id": f"uk-{version}",
                "country_id": "uk",
                "policyengine_version": version,
                "default_dataset": "enhanced_frs_2024_25",
                "certification": {
                    "compatibility_basis": "legacy_compatible_model_package",
                    "certified_for_model_version": "2.126.8",
                    "data_build_id": "policyengine-uk-data-1.59.0",
                    "certified_by": "policyengine.py bundle certification",
                },
                "model_package": {
                    "name": "policyengine-uk",
                    "version": "2.126.8",
                    "sha256": model_sha,
                },
                "certified_data_artifact": {
                    "build_id": "policyengine-uk-data-1.59.0",
                    "dataset": "enhanced_frs_2024_25",
                    "sha256": dataset_sha,
                    "uri": "hf://policyengine/policyengine-uk-data-private/enhanced_frs_2024_25.h5@1.59.0",
                },
                "datasets": {
                    "enhanced_frs_2024_25": {
                        "repo_id": "policyengine/policyengine-uk-data-private",
                        "revision": "1.59.0",
                        "path": "enhanced_frs_2024_25.h5",
                        "sha256": dataset_sha,
                    }
                },
                "data_package": {
                    "name": "policyengine-uk-data",
                    "repo_id": "policyengine/policyengine-uk-data-private",
                    "repo_type": "model",
                    "release_manifest_path": "releases/1.59.0/release_manifest.json",
                    "release_manifest_revision": "a" * 40,
                    "version": "1.59.0",
                },
            }
        }
    }


REQUIRES = [
    'policyengine-uk==2.126.8; extra == "uk"',
    'policyengine-core==3.34.0; extra == "uk"',
    'policyengine-us==2.3.0; extra == "us"',
]


@pytest.fixture
def stubs(tmp_path, monkeypatch):
    state = {"manifest": bundle_manifest(), "requires": list(REQUIRES), "release": None}

    def pypi(package, version=None):
        if version is None:
            return {
                "releases": {
                    "6.2.5": [],
                    "6.2.6": [],
                    "6.5.1": [],
                    "6.6.0rc1": [],
                    "junk": [],
                }
            }
        if package == "policyengine":
            if "uk" in state["manifest"].get("data_releases", {}):
                state["manifest"]["data_releases"]["uk"]["policyengine_version"] = (
                    version
                )
            payload = wheel_bytes(state["manifest"], state["requires"])
            state["wheel"] = payload
            digest = hashlib.sha256(payload).hexdigest()
        else:
            digest = {"policyengine-uk": "b" * 64, "policyengine-core": "c" * 64}[
                package
            ]
        return {
            "urls": [
                {
                    "packagetype": "bdist_wheel",
                    "filename": f"{package}-{version}-py3-none-any.whl",
                    "url": f"https://files.example/{package}-{version}.whl",
                    "digests": {"sha256": digest},
                    "upload_time_iso_8601": state.get("upload_time", UPLOAD_TIME),
                },
                {
                    "packagetype": "sdist",
                    "filename": "x.tar.gz",
                    "url": "u",
                    "digests": {"sha256": "s" * 64},
                },
            ]
        }

    def fetch(url, destination, sha256):
        payload = state["wheel"]
        assert hashlib.sha256(payload).hexdigest() == sha256
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(payload)
        return destination

    def release_manifest(data_package, *, token):
        release = state["release"] or {
            "artifacts": {
                "enhanced_frs_2024_25": {"sha256": "d" * 64, "size_bytes": 130_000_000}
            }
        }
        return json.dumps(release).encode()

    def provenance_response(url, **kwargs):
        assert url.startswith("https://pypi.org/integrity/policyengine/")
        if "provenance_error" in state:
            raise state["provenance_error"]
        return io.BytesIO(state.get("provenance", PROVENANCE_BYTES))

    monkeypatch.setattr(discover.urllib.request, "urlopen", provenance_response)
    monkeypatch.setattr(discover, "pypi", pypi)
    monkeypatch.setattr(discover, "fetch", fetch)
    monkeypatch.setattr(discover, "release_manifest", release_manifest)
    return state


def test_a_release_becomes_a_valid_released_bundle_request(stubs, tmp_path):
    request = discover.provisional_request(
        "6.5.0", tmp_path, token=None, requested_by=REQUESTED_BY, now=NOW
    )
    rid = qualify.request_id(request)
    assert len(rid) == 64
    candidate = request["candidate"]
    assert candidate["policyengine"]["source"] == {
        "pypi": {"wheel_sha256": hashlib.sha256(stubs["wheel"]).hexdigest()}
    }
    manifest_bytes = zipfile.ZipFile(io.BytesIO(stubs["wheel"])).read(
        discover.MANIFEST_PATH
    )
    assert (
        candidate["policyengine"]["packaged_bundle_manifest_sha256"]
        == hashlib.sha256(manifest_bytes).hexdigest()
    )
    assert candidate["policyengine_core"] == {
        "version": "3.34.0",
        "wheel_sha256": "c" * 64,
    }
    assert candidate["data"]["size_bytes"] == 130_000_000
    assert request["kind"] == "released_bundle"
    assert request["requested_by"]["pypi_provenance_sha256"] == PROVENANCE_DIGEST
    assert "pypi_provenance_sha256" not in REQUESTED_BY
    assert candidate["expected_release_bundle"] == discover.expected_bundle(
        stubs["manifest"]
    )


@pytest.mark.parametrize("missing", sorted(discover.TRUSTED_PUBLISHER))
def test_a_publisher_missing_any_identity_field_is_refused(stubs, tmp_path, missing):
    document = json.loads(PROVENANCE_BYTES)
    del document["attestation_bundles"][0]["publisher"][missing]
    stubs["provenance"] = json.dumps(document).encode()
    with pytest.raises(discover.Skipped, match="required trusted publisher") as caught:
        discover.provisional_request(
            "6.5.0", tmp_path, token=None, requested_by=REQUESTED_BY, now=NOW
        )
    assert caught.value.permanent


def test_a_field_pypi_adds_to_the_publisher_does_not_refuse_a_release(stubs, tmp_path):
    # The identity fields decide; an added field must not permanently skip a
    # genuine release.
    document = json.loads(PROVENANCE_BYTES)
    document["attestation_bundles"][0]["publisher"]["claims"] = {
        "ref": "refs/heads/main"
    }
    stubs["provenance"] = payload = json.dumps(document).encode()
    request = discover.provisional_request(
        "6.5.0", tmp_path, token=None, requested_by=REQUESTED_BY, now=NOW
    )
    assert (
        request["requested_by"]["pypi_provenance_sha256"]
        == hashlib.sha256(payload).hexdigest()
    )


@pytest.mark.parametrize("version", ["6.4.1", "6.5.0"])
def test_static_bundle_reproduces_w4_requests_byte_for_byte(version):
    fixture = FIXTURES / "discovery"
    manifest_bytes = (fixture / f"pe{version}-manifest.json").read_bytes()
    request = json.loads((fixture / f"pe{version}-request.json").read_bytes())
    # These are the unmodified packaged manifest bytes, independently bound
    # by the hand-built W4 request rather than by this implementation.
    assert (
        hashlib.sha256(manifest_bytes).hexdigest()
        == request["candidate"]["policyengine"]["packaged_bundle_manifest_sha256"]
    )
    bundle = discover.expected_bundle(json.loads(manifest_bytes))
    expected_bytes = (
        fixture / f"pe{version}-expected-release-bundle.json"
    ).read_bytes()
    assert (
        json.dumps(bundle, indent=2, sort_keys=True) + "\n"
    ).encode() == expected_bytes
    assert bundle == request["candidate"]["expected_release_bundle"]


def test_static_bundle_keeps_optional_nulls_including_certification_build_id():
    manifest = bundle_manifest()
    certification = manifest["data_releases"]["uk"]["certification"]
    del certification["data_build_id"]
    del certification["certified_by"]
    bundle = discover.expected_bundle(manifest)
    assert bundle["certified_data_build_id"] is None
    assert bundle["certified_by"] is None
    assert bundle["data_build_model_version"] is None
    assert bundle["data_build_model_git_sha"] is None
    assert bundle["data_build_fingerprint"] is None


@pytest.mark.parametrize(
    "change",
    [
        lambda uk: uk.update(country_id="us"),
        lambda uk: uk.update(certification=None),
        lambda uk: uk["certification"].update(certified_for_model_version="2.0.0"),
        lambda uk: uk.update(default_dataset="other_dataset"),
    ],
    ids=["wrong-country", "missing-certification", "wrong-model", "wrong-dataset"],
)
def test_static_bundle_refuses_inconsistent_packaged_certification(change):
    manifest = bundle_manifest()
    change(manifest["data_releases"]["uk"])
    with pytest.raises(discover.Skipped, match="does not certify") as caught:
        discover.expected_bundle(manifest)
    assert caught.value.permanent


def test_request_building_never_runs_installers_or_release_code(
    stubs, tmp_path, monkeypatch
):
    def forbidden(*args, **kwargs):
        raise AssertionError("discovery must not start an installer or probe")

    monkeypatch.setattr(subprocess, "run", forbidden)
    original = wheel_bytes

    def hostile_wheel(manifest, requires):
        payload = io.BytesIO(original(manifest, requires))
        with zipfile.ZipFile(payload, "a") as wheel:
            wheel.writestr("policyengine/__init__.py", "raise RuntimeError('executed')")
            wheel.writestr("release.pth", "import policyengine\n")
        return payload.getvalue()

    monkeypatch.setitem(globals(), "wheel_bytes", hostile_wheel)
    request = discover.provisional_request(
        "6.5.0", tmp_path, token="read-only-secret", requested_by=REQUESTED_BY, now=NOW
    )
    assert qualify.request_id(request)


@pytest.mark.parametrize(
    "change",
    [
        lambda s: s.update(manifest=bundle_manifest(model_sha="x" * 64)),
        lambda s: s.update(
            release={
                "artifacts": {
                    "enhanced_frs_2024_25": {"sha256": "e" * 64, "size_bytes": 1}
                }
            }
        ),
        lambda s: s.update(release={"artifacts": {}}),
        lambda s: s.update(requires=REQUIRES[1:]),
        lambda s: s.update(
            requires=['policyengine-uk==2.126.9; extra == "uk"', REQUIRES[1]]
        ),
    ],
    ids=[
        "model-digest",
        "dataset-digest",
        "dataset-absent",
        "missing-pin",
        "pin-differs",
    ],
)
def test_inconsistent_releases_are_skipped_with_a_reason(stubs, tmp_path, change):
    change(stubs)
    with pytest.raises(discover.Skipped) as caught:
        discover.provisional_request(
            "6.5.0", tmp_path, token=None, requested_by=REQUESTED_BY, now=NOW
        )
    assert caught.value.permanent
    assert (
        caught.value.evidence_sha256["policyengine_wheel"]
        == hashlib.sha256(stubs["wheel"]).hexdigest()
    )
    assert "packaged_bundle_manifest" in caught.value.evidence_sha256


@pytest.mark.parametrize("dataset_repo_type", [None, "dataset"])
def test_dataset_repo_type_overrides_the_data_package(
    stubs, tmp_path, dataset_repo_type
):
    # The installed 6.2.6 UK manifest omits this field on dataset entries;
    # entries for a different HF repository can explicitly declare it.
    dataset = stubs["manifest"]["data_releases"]["uk"]["datasets"][
        "enhanced_frs_2024_25"
    ]
    if dataset_repo_type:
        dataset["repo_type"] = dataset_repo_type
    request = discover.provisional_request(
        "6.5.0", tmp_path, token=None, requested_by=REQUESTED_BY, now=NOW
    )
    assert request["candidate"]["data"]["repo_type"] == (dataset_repo_type or "model")


def test_data_certification_at_a_movable_tag_is_not_permanently_skipped(
    stubs, tmp_path
):
    stubs["manifest"]["data_releases"]["uk"]["data_package"][
        "release_manifest_revision"
    ] = "1.59.0"
    stubs["release"] = {"artifacts": {}}
    with pytest.raises(discover.Skipped) as caught:
        discover.provisional_request(
            "6.5.0", tmp_path, token=None, requested_by=REQUESTED_BY, now=NOW
        )
    assert not caught.value.permanent
    assert "data_release_manifest" in caught.value.evidence_sha256


def test_candidates_are_newer_unrequested_final_releases(tmp_path):
    document = floor_document()
    request = golden()
    request["kind"] = "released_bundle"
    request["candidate"]["policyengine"]["version"] = "6.5.0"
    directory = tmp_path / "requests" / ("a" * 64)
    directory.mkdir(parents=True)
    (directory / "REQUEST.json").write_text(json.dumps(request))
    versions = [
        "6.2.5",
        "6.2.6",
        "6.3.0",
        "6.4.0",
        "6.4.1",
        "6.5.0",
        "6.5.1",
        "6.10.0",
        "6.6.0rc1",
        "junk",
        "7.0.0",
    ]
    assert discover.candidates(versions, document, tmp_path) == [
        "6.5.1",
        "6.10.0",
        "7.0.0",
    ]


@pytest.mark.parametrize(
    "status", ["queued", "running", "complete", "failed", "rejected"]
)
@pytest.mark.parametrize("kind", ["candidate", "released_bundle"])
def test_only_a_released_bundle_request_in_any_status_sets_the_floor(
    tmp_path, status, kind
):
    # Keep the requested release above the current certified floor: otherwise
    # certification itself would hide a regression that ignored terminal states.
    # Only a released_bundle request counts: a pre-promotion candidate request
    # pins the candidate's wheels, not the rebuilt released ones (W4).
    request = request_for("6.6.0")
    request["kind"] = kind
    directory = tmp_path / "requests" / qualify.request_id(request)
    directory.mkdir(parents=True)
    (directory / "REQUEST.json").write_text(json.dumps(request))
    (directory / "STATUS.json").write_text(json.dumps({"status": status}))
    assert discover.candidates(
        ["6.5.0", "6.5.1", "6.6.0", "6.6.1"], floor_document(), tmp_path
    ) == (["6.6.1"] if kind == "released_bundle" else ["6.5.1", "6.6.0", "6.6.1"])


@pytest.mark.parametrize(
    "version", ["999999999!0", "9999.0", "9999.0+local", "6.6.0rc1", "6.6.0.post1"]
)
def test_a_request_naming_an_unpublished_or_odd_version_cannot_raise_the_floor(
    tmp_path, version
):
    # Review of 2043fa0: a stored request naming an absurd version must not
    # stop discovery for good. Written by name, since some fail the schema.
    request = request_for("6.6.0")
    request["candidate"]["policyengine"]["version"] = version
    directory = tmp_path / "requests" / ("a" * 64)
    directory.mkdir(parents=True)
    (directory / "REQUEST.json").write_text(json.dumps(request))
    # A prerelease or post release PyPI lists still cannot raise the floor; the
    # requested post release itself is never duplicated.
    published = ["6.5.0", "6.5.1", "6.6.0"] + (
        [version] if version in {"6.6.0rc1", "6.6.0.post1"} else []
    )
    assert discover.candidates(published, floor_document(), tmp_path) == [
        "6.5.1",
        "6.6.0",
    ]


def test_a_released_bundle_request_counts_once_its_version_is_published(tmp_path):
    request = request_for("6.6.0")
    directory = tmp_path / "requests" / ("b" * 64)
    directory.mkdir(parents=True)
    (directory / "REQUEST.json").write_text(json.dumps(request))
    document = floor_document()
    # Not yet on PyPI: the floor stays at the certified 6.5.0.
    assert discover.candidates(["6.5.0", "6.5.1"], document, tmp_path) == ["6.5.1"]
    # Published: 6.6.0 raises the floor, and is itself never duplicated.
    assert discover.candidates(
        ["6.5.0", "6.5.1", "6.6.0", "6.6.1"], document, tmp_path
    ) == ["6.6.1"]


@pytest.mark.parametrize("kind", ["candidate", "unsupported"])
def test_a_pre_promotion_or_other_request_neither_covers_nor_floors_a_release(
    tmp_path, kind
):
    # W4, 2026-10-16: a candidate qualification names the version it will be
    # released as, but the released wheel is rebuilt, so a missed release
    # dispatch must still be caught.
    request = request_for("6.6.0")
    request["kind"] = kind
    directory = tmp_path / "requests" / ("c" * 64)
    directory.mkdir(parents=True)
    (directory / "REQUEST.json").write_text(json.dumps(request))
    (directory / "STATUS.json").write_text(json.dumps({"status": "complete"}))
    assert discover.candidates(
        ["6.5.0", "6.5.1", "6.6.0"], floor_document(), tmp_path
    ) == ["6.5.1", "6.6.0"]


def test_an_epoch_version_cannot_raise_the_floor_even_when_published(tmp_path):
    # Review of f3f21a7 (N4): the epoch check, not the PyPI listing, excludes it.
    request = request_for("6.6.0")
    request["candidate"]["policyengine"]["version"] = "1!0.1"
    directory = tmp_path / "requests" / ("d" * 64)
    directory.mkdir(parents=True)
    (directory / "REQUEST.json").write_text(json.dumps(request))
    assert discover.candidates(
        ["6.5.0", "6.5.1", "1!0.1"], floor_document(), tmp_path
    ) == ["6.5.1"]


versions_strategy = st.lists(
    st.tuples(st.integers(5, 7), st.integers(0, 6), st.integers(0, 3)),
    min_size=1,
    max_size=12,
    unique=True,
).map(lambda parts: [f"{a}.{b}.{c}" for a, b, c in parts])


@settings(max_examples=150, deadline=None)
@given(
    versions_strategy,
    st.data(),
)
def test_candidates_respect_the_floor_and_never_repeat_a_request(published, data):
    # Review of f3f21a7 (N5): invariants over published and requested sets.
    import tempfile

    # Review of 23cff0a: repeated versions (so one version can carry a
    # candidate and a released_bundle request), unsupported and missing kinds,
    # and versions PyPI never published.
    requested = data.draw(
        st.lists(st.sampled_from([*published, "9.9.9", "4.0.0"]), max_size=5)
    )
    kinds = data.draw(
        st.lists(
            st.sampled_from(["released_bundle", "candidate", "unsupported", None]),
            min_size=len(requested),
            max_size=len(requested),
        )
    )
    with tempfile.TemporaryDirectory() as root:
        state = Path(root)
        for index, (version, kind) in enumerate(zip(requested, kinds)):
            request = request_for(version)
            if kind is None:
                del request["kind"]
            else:
                request["kind"] = kind
            directory = state / "requests" / (f"{index:x}" * 64)[:64]
            directory.mkdir(parents=True)
            (directory / "REQUEST.json").write_text(json.dumps(request))
        document = floor_document()
        out = [Version(v) for v in discover.candidates(published, document, state)]
    certified = max(
        Version(r["identity"]["packages"]["policyengine"]["version"])
        for r in document["variants"]
        if r["status"] == "certified"
    )
    released = {Version(v) for v, k in zip(requested, kinds) if k == "released_bundle"}
    listed = {Version(p) for p in published}
    floor = max({certified} | (released & listed))
    assert out == sorted(out)
    for version in out:
        assert str(version) in published or version in {Version(p) for p in published}
        assert version > floor and version not in released
    expected = sorted({Version(p) for p in published if Version(p) > floor} - released)
    assert out == expected


@pytest.mark.parametrize(
    "malformed",
    [
        None,
        [],
        "request",
        1,
        {},
        {"kind": "released_bundle"},
        {"kind": "released_bundle", "candidate": None},
        {"kind": "released_bundle", "candidate": []},
        {"kind": "released_bundle", "candidate": {"policyengine": None}},
        {"kind": "released_bundle", "candidate": {"policyengine": []}},
        {
            "kind": "released_bundle",
            "candidate": {"policyengine": {"version": 630}},
        },
        {
            "kind": "released_bundle",
            "candidate": {"policyengine": {"version": "invalid"}},
        },
        # Review of 23cff0a (D3): a request without a released_bundle kind
        # covers nothing, whatever version it names.
        {"candidate": {"policyengine": {"version": "6.5.1"}}},
        {"kind": None, "candidate": {"policyengine": {"version": "6.5.1"}}},
        {
            "kind": "Released_Bundle",
            "candidate": {"policyengine": {"version": "6.5.1"}},
        },
    ],
)
def test_malformed_stored_requests_do_not_break_discovery(tmp_path, malformed):
    directory = tmp_path / "requests" / ("a" * 64)
    directory.mkdir(parents=True)
    (directory / "REQUEST.json").write_text(json.dumps(malformed))
    assert discover.requested_versions(tmp_path) == set()
    assert discover.candidates(["6.5.1"], floor_document(), tmp_path) == ["6.5.1"]


def test_invalid_json_stored_request_is_ignored(tmp_path):
    directory = tmp_path / "requests" / ("a" * 64)
    directory.mkdir(parents=True)
    (directory / "REQUEST.json").write_text("{broken")
    assert discover.requested_versions(tmp_path) == set()


def test_version_aliases_are_compared_and_deduplicated_as_versions(tmp_path):
    request = request_for("6.5")
    directory = tmp_path / "requests" / ("a" * 64)
    directory.mkdir(parents=True)
    (directory / "REQUEST.json").write_text(json.dumps(request))
    document = {
        "variants": [
            {
                "status": "certified",
                "identity": {"packages": {"policyengine": {"version": "6.2.6.0"}}},
            }
        ]
    }
    assert discover.requested_versions(tmp_path) == {Version("6.5.0")}
    assert discover.candidates(
        ["6.2.6", "6.5.0", "6.6", "6.6.0"], document, tmp_path
    ) == ["6.6"]


def test_discovery_without_a_certified_baseline_requests_nothing(
    stubs, tmp_path, monkeypatch, capsys
):
    monkeypatch.setattr(discover.variants, "load_document", lambda: {"variants": []})
    assert (
        discover.discover(
            tmp_path / "state",
            tmp_path / "work",
            token=None,
            requested_by=REQUESTED_BY,
            now=NOW,
        )
        == []
    )
    assert "no baseline" in capsys.readouterr().out


@pytest.mark.parametrize("release_yanked", [False, True])
def test_yanked_release_or_wheel_is_not_a_candidate(tmp_path, release_yanked):
    files = [
        {"packagetype": "bdist_wheel", "yanked": not release_yanked},
        {"packagetype": "sdist", "yanked": False},
    ]
    releases = {
        "6.5.0": {"yanked": True, "urls": files} if release_yanked else files,
        "6.5.1": [{"packagetype": "bdist_wheel", "yanked": False}],
    }
    assert discover.candidates(releases, floor_document(), tmp_path) == ["6.5.1"]


@pytest.mark.parametrize("location", ["release", "info", "wheel"])
def test_a_release_yanked_after_listing_is_skipped(
    stubs, tmp_path, monkeypatch, location
):
    original = discover.pypi

    def pypi(package, version=None):
        document = original(package, version)
        if package == "policyengine" and version:
            if location == "wheel":
                document["urls"][0]["yanked"] = True
            elif location == "info":
                document["info"] = {"yanked": True}
            else:
                document["yanked"] = True
        return document

    monkeypatch.setattr(discover, "pypi", pypi)
    with pytest.raises(discover.Skipped, match="yanked") as caught:
        discover.provisional_request(
            "6.5.0", tmp_path, token=None, requested_by=REQUESTED_BY, now=NOW
        )
    assert not caught.value.permanent


def test_discovery_caps_each_run_and_continues_past_a_skip(
    stubs, tmp_path, monkeypatch, capsys
):
    monkeypatch.setattr(discover, "MAX_PER_RUN", 1)
    found = discover.discover(
        tmp_path / "state",
        tmp_path / "work",
        token=None,
        requested_by=REQUESTED_BY,
        now=NOW,
    )
    assert [r["candidate"]["policyengine"]["version"] for r in found] == ["6.5.1"]
    assert (
        "building the oldest 1 now" not in capsys.readouterr().out
    )  # one candidate only
    stubs["manifest"] = bundle_manifest(model_sha="x" * 64)
    assert (
        discover.discover(
            tmp_path / "state",
            tmp_path / "work2",
            token=None,
            requested_by=REQUESTED_BY,
            now=NOW,
        )
        == []
    )
    assert "not requested" in capsys.readouterr().out


@pytest.mark.parametrize("error_type", [urllib.error.URLError, urllib.error.HTTPError])
def test_pypi_listing_outage_does_not_raise(tmp_path, monkeypatch, capsys, error_type):
    def pypi(package, version=None):
        if error_type is urllib.error.HTTPError:
            raise error_type("https://pypi.org", 503, "unavailable", {}, None)
        raise error_type("unavailable")

    monkeypatch.setattr(discover, "pypi", pypi)
    assert (
        discover.discover(
            tmp_path / "state",
            tmp_path / "work",
            token=None,
            requested_by=REQUESTED_BY,
            now=NOW,
        )
        == []
    )
    assert "release listing unavailable" in capsys.readouterr().out


@pytest.mark.parametrize(
    "failure",
    ["url-error", "http-error", "missing-manifest", "missing-uk", "manifest-json"],
)
def test_release_errors_do_not_stop_later_candidates(
    stubs, tmp_path, monkeypatch, capsys, failure
):
    original = discover.pypi

    def pypi(package, version=None):
        if version is None:
            return {"releases": {"6.5.1": [], "6.5.2": []}}
        if package == "policyengine":
            stubs["manifest"] = bundle_manifest()
            if version == "6.5.1":
                if failure == "url-error":
                    raise urllib.error.URLError("PyPI unavailable")
                if failure == "http-error":
                    raise urllib.error.HTTPError("u", 503, "unavailable", {}, None)
                if failure == "missing-uk":
                    stubs["manifest"] = {"data_releases": {}}
            document = original(package, version)
            if version == "6.5.1" and failure in {"missing-manifest", "manifest-json"}:
                buffer = io.BytesIO()
                with zipfile.ZipFile(buffer, "w") as wheel:
                    wheel.writestr("policyengine-6.5.0.dist-info/METADATA", "metadata")
                    if failure == "manifest-json":
                        wheel.writestr(discover.MANIFEST_PATH, "{broken")
                stubs["wheel"] = buffer.getvalue()
                document["urls"][0]["digests"]["sha256"] = hashlib.sha256(
                    stubs["wheel"]
                ).hexdigest()
            return document
        return original(package, version)

    monkeypatch.setattr(discover, "pypi", pypi)
    state = tmp_path / "state"
    requests = discover.discover(
        state, tmp_path / "work", token=None, requested_by=REQUESTED_BY, now=NOW
    )
    assert [r["candidate"]["policyengine"]["version"] for r in requests] == ["6.5.2"]
    assert "policyengine 6.5.1: not requested" in capsys.readouterr().out
    assert not list((state / "discovery" / "skipped").glob("*.json"))


def test_permanent_skips_do_not_starve_the_good_release_in_this_or_next_run(
    stubs, tmp_path, monkeypatch
):
    original = discover.pypi
    attempted = []

    def pypi(package, version=None):
        if version is None:
            return {"releases": {f"6.5.{index}": [] for index in range(1, 5)}}
        if package == "policyengine":
            attempted.append(version)
            stubs["manifest"] = bundle_manifest()
            stubs["requires"] = REQUIRES[1:] if version != "6.5.4" else REQUIRES
        return original(package, version)

    monkeypatch.setattr(discover, "pypi", pypi)
    state = tmp_path / "state"
    requests = discover.discover(
        state, tmp_path / "work", token=None, requested_by=REQUESTED_BY, now=NOW
    )
    assert [r["candidate"]["policyengine"]["version"] for r in requests] == ["6.5.4"]
    assert attempted == ["6.5.1", "6.5.2", "6.5.3", "6.5.4"]
    records = list((state / "discovery" / "skipped").glob("*.json"))
    assert len(records) == 3
    for path in records:
        record = json.loads(path.read_text())
        assert record["reason"].startswith("the wheel's uk extra pins")
        assert set(record["evidence_sha256"]) == {
            "policyengine_wheel",
            "packaged_bundle_manifest",
            "policyengine_provenance",
        }
        assert all(len(digest) == 64 for digest in record["evidence_sha256"].values())
    directory = state / "requests" / qualify.request_id(requests[0])
    directory.mkdir(parents=True)
    (directory / "REQUEST.json").write_text(json.dumps(requests[0]))
    attempted.clear()
    assert (
        discover.discover(
            state, tmp_path / "work2", token=None, requested_by=REQUESTED_BY, now=NOW
        )
        == []
    )
    assert attempted == []


def test_discovery_has_a_separate_attempt_limit(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(discover, "MAX_PER_RUN", 3)
    monkeypatch.setattr(discover, "MAX_ATTEMPTS_PER_RUN", 2)
    monkeypatch.setattr(
        discover,
        "pypi",
        lambda package: {"releases": {f"6.5.{i}": [] for i in range(1, 6)}},
    )
    attempted = []

    def provisional(version, work, **kwargs):
        attempted.append(version)
        raise TimeoutError("retry later")

    monkeypatch.setattr(discover, "provisional_request", provisional)
    assert (
        discover.discover(
            tmp_path / "state",
            tmp_path / "work",
            token=None,
            requested_by=REQUESTED_BY,
            now=NOW,
        )
        == []
    )
    assert attempted == ["6.5.1", "6.5.2"]
    assert "2 attempts" in capsys.readouterr().out
    assert not list((tmp_path / "state" / "discovery" / "skipped").glob("*.json"))


@settings(max_examples=100, deadline=None)
@given(
    st.lists(
        st.sampled_from(["good", "permanent", "failed", "recorded", "yanked"]),
        max_size=15,
    )
)
def test_discovery_for_any_mix_is_bounded_and_excludes_recorded_or_yanked(
    tmp_path_factory, outcomes
):
    state = tmp_path_factory.mktemp("mix-state")
    work = tmp_path_factory.mktemp("mix-work")
    versions = {f"6.5.{index + 1}": outcome for index, outcome in enumerate(outcomes)}
    releases = {
        version: [{"packagetype": "bdist_wheel", "yanked": outcome == "yanked"}]
        for version, outcome in versions.items()
    }
    records = state / "discovery" / "skipped"
    records.mkdir(parents=True)
    for version, outcome in versions.items():
        if outcome == "recorded":
            (records / f"{version}.json").write_text(json.dumps({"version": version}))
    attempted = []

    def provisional(version, work, **kwargs):
        attempted.append(version)
        outcome = versions[version]
        if outcome == "permanent":
            raise discover.Skipped(
                "immutable mismatch",
                permanent=True,
                evidence_sha256={"wheel": "a" * 64},
            )
        if outcome == "failed":
            raise urllib.error.URLError("transient outage")
        assert outcome == "good"
        return request_for(version)

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(discover, "pypi", lambda package: {"releases": releases})
        patch.setattr(discover, "provisional_request", provisional)
        requests = discover.discover(
            state, work, token=None, requested_by=REQUESTED_BY, now=NOW
        )
    requested = [
        request["candidate"]["policyengine"]["version"] for request in requests
    ]
    assert len(requested) <= discover.MAX_PER_RUN
    assert len(attempted) <= discover.MAX_ATTEMPTS_PER_RUN
    assert all(versions[version] == "good" for version in requested)
    assert all(versions[version] not in {"recorded", "yanked"} for version in attempted)
    assert set(discover.skipped_versions(state)) == {
        Version(version)
        for version, outcome in versions.items()
        if outcome == "recorded" or outcome == "permanent" and version in attempted
    }


@settings(max_examples=100, deadline=None)
@given(
    st.lists(
        st.tuples(st.integers(0, 9), st.integers(0, 12), st.integers(0, 12)),
        max_size=12,
    )
)
def test_candidates_are_sorted_strictly_above_the_floor(tmp_path_factory, triples):
    versions = [f"{a}.{b}.{c}" for a, b, c in triples]
    out = discover.candidates(versions, floor_document(), tmp_path_factory.mktemp("s"))
    from packaging.version import Version

    assert out == sorted(set(out), key=Version)
    assert all(Version(v) > Version("6.5.0") for v in out)
    assert set(out) == {v for v in versions if Version(v) > Version("6.5.0")}


@pytest.mark.parametrize(
    "field,value",
    [
        ("repository", "attacker/policyengine.py"),
        ("repository", "policyengine/policyengine.py"),
        ("workflow", "release.yaml"),
        ("environment", "production"),
        ("kind", "GitLab"),
        ("environment", None),
        ("repository", "PolicyEngine/policyengine.py "),
    ],
)
def test_wrong_publisher_is_permanently_refused_before_bundle_building(
    stubs, tmp_path, monkeypatch, field, value
):
    document = json.loads(PROVENANCE_BYTES)
    document["attestation_bundles"][0]["publisher"][field] = value
    payload = json.dumps(document).encode()
    stubs["provenance"] = payload

    def forbidden(*args, **kwargs):
        raise AssertionError(
            "untrusted provenance must be checked before reading a wheel"
        )

    monkeypatch.setattr(discover, "fetch", forbidden)
    monkeypatch.setattr(discover, "expected_bundle", forbidden)
    with pytest.raises(discover.Skipped, match="required trusted publisher") as caught:
        discover.provisional_request(
            "6.5.1", tmp_path, token=None, requested_by=REQUESTED_BY, now=NOW
        )
    assert caught.value.permanent
    assert caught.value.evidence_sha256 == {
        "policyengine_provenance": hashlib.sha256(payload).hexdigest()
    }


@pytest.mark.parametrize(
    "payload",
    [
        b"{unreadable",
        b"null",
        b"{}",
        b'{"attestation_bundles": []}',
        json.dumps(
            {
                "attestation_bundles": [
                    {
                        "publisher": PROVENANCE_DOCUMENT["attestation_bundles"][0][
                            "publisher"
                        ]
                    }
                ]
            }
        ).encode(),
        json.dumps(
            {
                "attestation_bundles": [
                    {
                        "publisher": PROVENANCE_DOCUMENT["attestation_bundles"][0][
                            "publisher"
                        ],
                        "attestations": [],
                    }
                ]
            }
        ).encode(),
        json.dumps(
            {
                "attestation_bundles": [
                    {
                        "publisher": PROVENANCE_DOCUMENT["attestation_bundles"][0][
                            "publisher"
                        ],
                        "attestations": [None],
                    }
                ]
            }
        ).encode(),
    ],
)
def test_missing_or_unreadable_provenance_has_response_digest(stubs, tmp_path, payload):
    stubs["provenance"] = payload
    with pytest.raises(discover.Skipped) as caught:
        discover.provisional_request(
            "6.5.1", tmp_path, token=None, requested_by=REQUESTED_BY, now=NOW
        )
    assert caught.value.permanent
    assert (
        caught.value.evidence_sha256["policyengine_provenance"]
        == hashlib.sha256(payload).hexdigest()
    )


def test_missing_provenance_http_response_is_permanent_evidence(stubs, tmp_path):
    payload = b'{"message": "No attestations found"}'
    stubs["provenance_error"] = urllib.error.HTTPError(
        "https://pypi.org/integrity/policyengine/6.5.1/wheel/provenance",
        404,
        "not found",
        {},
        io.BytesIO(payload),
    )
    state = tmp_path / "state"
    assert (
        discover.discover(
            state, tmp_path / "work", token=None, requested_by=REQUESTED_BY, now=NOW
        )
        == []
    )
    record = json.loads((state / "discovery" / "skipped" / "6.5.1.json").read_text())
    assert record["evidence_sha256"] == {
        "policyengine_provenance": hashlib.sha256(payload).hexdigest()
    }


@pytest.mark.parametrize("code", [403, 406, 408, 425, 429, 500, 503, None])
def test_transient_provenance_failure_is_retried_instead_of_recorded(
    stubs, tmp_path, code
):
    stubs["provenance_error"] = (
        urllib.error.HTTPError(
            "https://pypi.org", code, "try later", {}, io.BytesIO(b"outage")
        )
        if code is not None
        else urllib.error.URLError("try later")
    )
    state = tmp_path / "state"
    assert (
        discover.discover(
            state, tmp_path / "first", token=None, requested_by=REQUESTED_BY, now=NOW
        )
        == []
    )
    assert not list((state / "discovery" / "skipped").glob("*.json"))
    del stubs["provenance_error"]
    requests = discover.discover(
        state, tmp_path / "retry", token=None, requested_by=REQUESTED_BY, now=NOW
    )
    assert [r["candidate"]["policyengine"]["version"] for r in requests] == ["6.5.1"]


@pytest.mark.parametrize(
    "age,accepted",
    [
        (timedelta(hours=6) - timedelta(microseconds=1), False),
        (timedelta(hours=6), True),
        (timedelta(hours=6) + timedelta(microseconds=1), True),
    ],
)
def test_wheel_upload_grace_period_boundary(stubs, tmp_path, age, accepted):
    assert discover.MIN_RELEASE_AGE == timedelta(hours=6)
    stubs["upload_time"] = (NOW - age).isoformat()
    if accepted:
        assert discover.provisional_request(
            "6.5.1", tmp_path, token=None, requested_by=REQUESTED_BY, now=NOW
        )
    else:
        with pytest.raises(discover.Skipped, match="grace period") as caught:
            discover.provisional_request(
                "6.5.1", tmp_path, token=None, requested_by=REQUESTED_BY, now=NOW
            )
        assert not caught.value.permanent


@pytest.mark.parametrize("floor_source", ["requested", "certified"])
def test_642_and_643_are_not_backfilled_after_650(tmp_path, floor_source):
    document = {
        "variants": [
            {
                "status": "certified",
                "identity": {
                    "packages": {
                        "policyengine": {
                            "version": "6.5.0"
                            if floor_source == "certified"
                            else "6.4.1"
                        }
                    }
                },
            }
        ]
    }
    if floor_source == "requested":
        directory = tmp_path / "requests" / ("a" * 64)
        directory.mkdir(parents=True)
        # A released_bundle request sets the floor in any status, including
        # one the queue rejected.
        request = request_for("6.5.0")
        (directory / "REQUEST.json").write_text(json.dumps(request))
        (directory / "STATUS.json").write_text(json.dumps({"status": "rejected"}))
    assert discover.candidates(
        ["6.4.1", "6.4.2", "6.4.3", "6.5.0", "6.5.1"], document, tmp_path
    ) == ["6.5.1"]


def test_prerelease_above_current_floor_is_not_discovered(tmp_path):
    assert discover.candidates(["6.6.0rc1", "6.6.0"], floor_document(), tmp_path) == [
        "6.6.0"
    ]


class BoundedResponse(io.BytesIO):
    def __init__(self, payload):
        super().__init__(payload)
        self.read_sizes = []
        self.bytes_read = 0

    def read(self, size=-1):
        assert size > 0, "responses must be streamed with bounded reads"
        self.read_sizes.append(size)
        payload = super().read(size)
        self.bytes_read += len(payload)
        return payload


@pytest.mark.parametrize("correct_digest", [True, False])
def test_fetch_streams_and_checks_the_actual_wheel_digest(
    tmp_path, monkeypatch, correct_digest
):
    payload = b"static wheel bytes" * 10000
    response = BoundedResponse(payload)
    monkeypatch.setattr(
        discover.urllib.request, "urlopen", lambda *args, **kwargs: response
    )
    destination = tmp_path / "wheel.whl"
    digest = hashlib.sha256(payload).hexdigest() if correct_digest else "0" * 64
    if correct_digest:
        assert (
            discover.fetch("https://files.example/wheel.whl", destination, digest)
            == destination
        )
        assert destination.read_bytes() == payload
    else:
        with pytest.raises(discover.Skipped, match="differ from PyPI's digest"):
            discover.fetch("https://files.example/wheel.whl", destination, digest)
        assert not destination.exists()
    assert len(response.read_sizes) > 1
    assert max(response.read_sizes) <= discover.READ_CHUNK_BYTES


@pytest.mark.parametrize("kind", ["wheel", "json", "provenance"])
def test_response_caps_stop_reading_after_limit(tmp_path, monkeypatch, kind):
    response = BoundedResponse(b"x" * 10000)
    monkeypatch.setattr(
        discover.urllib.request, "urlopen", lambda *args, **kwargs: response
    )
    monkeypatch.setattr(discover, "MAX_WHEEL_BYTES", 100)
    monkeypatch.setattr(discover, "MAX_JSON_BYTES", 100)
    with pytest.raises(discover.Skipped, match="100-byte limit") as caught:
        if kind == "wheel":
            discover.fetch(
                "https://files.example/wheel.whl", tmp_path / "wheel.whl", "a" * 64
            )
        elif kind == "json":
            discover.pypi("policyengine")
        else:
            discover.trusted_provenance("6.5.1", "wheel.whl")
    assert response.bytes_read == 101
    assert not caught.value.permanent
    assert not caught.value.evidence_sha256
    assert not (tmp_path / "wheel.whl").exists()


@pytest.mark.parametrize(
    "entry", [discover.MANIFEST_PATH, "policyengine-6.5.1.dist-info/METADATA"]
)
@pytest.mark.parametrize("limit", ["size", "compression"])
def test_wheel_entries_are_checked_before_decompression(
    tmp_path, monkeypatch, entry, limit
):
    path = tmp_path / "bomb.whl"
    manifest = json.dumps(bundle_manifest()).encode()
    metadata = "".join(f"Requires-Dist: {line}\n" for line in REQUIRES).encode()
    content = b"a" * (
        discover.MAX_WHEEL_ENTRY_BYTES + 1 if limit == "size" else 128 * 1024
    )
    compression = zipfile.ZIP_STORED if limit == "size" else zipfile.ZIP_DEFLATED
    with zipfile.ZipFile(path, "w", compression=compression) as wheel:
        wheel.writestr(
            discover.MANIFEST_PATH,
            content if entry == discover.MANIFEST_PATH else manifest,
        )
        wheel.writestr(
            "policyengine-6.5.1.dist-info/METADATA",
            content if entry.endswith("METADATA") else metadata,
        )
    original = zipfile.ZipFile.read

    def checked_read(wheel, info, *args, **kwargs):
        assert info.filename != entry, "unsafe ZIP entry must not be decompressed"
        return original(wheel, info, *args, **kwargs)

    monkeypatch.setattr(zipfile.ZipFile, "read", checked_read)
    with pytest.raises(discover.Skipped, match="size or compression limit"):
        discover.read_wheel(path)


@pytest.mark.parametrize("failure", ["zip-bomb", "oversized-wheel"])
def test_large_artifact_refusal_does_not_stop_the_drain(
    stubs, tmp_path, monkeypatch, failure
):
    original_pypi = discover.pypi
    original_wheel_bytes = wheel_bytes

    def pypi(package, version=None):
        if version is None:
            return {"releases": {"6.5.1": [], "6.5.2": []}}
        return original_pypi(package, version)

    def maybe_bomb(manifest, requires):
        if (
            failure == "zip-bomb"
            and manifest["data_releases"]["uk"]["policyengine_version"] == "6.5.1"
        ):
            buffer = io.BytesIO()
            with zipfile.ZipFile(
                buffer, "w", compression=zipfile.ZIP_DEFLATED
            ) as wheel:
                wheel.writestr(discover.MANIFEST_PATH, b"a" * (128 * 1024))
                wheel.writestr("policyengine-6.5.1.dist-info/METADATA", "metadata")
            return buffer.getvalue()
        return original_wheel_bytes(manifest, requires)

    def response(url, **kwargs):
        if "/integrity/" in url:
            return BoundedResponse(PROVENANCE_BYTES)
        if failure == "oversized-wheel" and "6.5.1" in url:
            return BoundedResponse(b"x" * (16 * 1024 + 1))
        return BoundedResponse(stubs["wheel"])

    monkeypatch.setitem(globals(), "wheel_bytes", maybe_bomb)
    monkeypatch.setattr(discover, "pypi", pypi)
    monkeypatch.setattr(discover, "fetch", REAL_FETCH)
    monkeypatch.setattr(discover, "MAX_WHEEL_BYTES", 16 * 1024)
    monkeypatch.setattr(discover.urllib.request, "urlopen", response)
    state = tmp_path / "state"
    requests = discover.discover(
        state, tmp_path / "work", token=None, requested_by=REQUESTED_BY, now=NOW
    )
    assert [r["candidate"]["policyengine"]["version"] for r in requests] == ["6.5.2"]
    assert not list((state / "discovery" / "skipped").glob("*.json"))


@pytest.mark.parametrize("oversized", [False, True])
def test_release_manifest_runtime_defaults_and_bounded_read(
    tmp_path, monkeypatch, oversized
):
    path = tmp_path / "release_manifest.json"
    path.write_bytes(
        b"x" * (discover.MAX_JSON_BYTES + 1) if oversized else b'{"artifacts": {}}'
    )
    calls = []

    def download(**kwargs):
        calls.append(kwargs)
        return path

    monkeypatch.setitem(
        sys.modules, "huggingface_hub", types.SimpleNamespace(hf_hub_download=download)
    )
    package = {"repo_id": "policyengine/private", "version": "1.2.3"}
    if oversized:
        with pytest.raises(discover.Skipped, match="byte limit"):
            REAL_RELEASE_MANIFEST(package, token="read-only")
    else:
        assert REAL_RELEASE_MANIFEST(package, token="read-only") == path.read_bytes()
    assert calls == [
        {
            "repo_id": "policyengine/private",
            "repo_type": "model",
            "filename": "release_manifest.json",
            "revision": "1.2.3",
            "token": "read-only",
        }
    ]


def test_transient_skip_with_evidence_is_never_persisted(tmp_path, monkeypatch):
    monkeypatch.setattr(discover, "pypi", lambda package: {"releases": {"6.5.1": []}})
    attempts = []

    def provisional(version, work, **kwargs):
        attempts.append(version)
        if len(attempts) == 1:
            raise discover.Skipped(
                "retry later", evidence_sha256={"policyengine_provenance": "a" * 64}
            )
        return request_for(version)

    monkeypatch.setattr(discover, "provisional_request", provisional)
    state = tmp_path / "state"
    assert (
        discover.discover(
            state, tmp_path / "first", token=None, requested_by=REQUESTED_BY, now=NOW
        )
        == []
    )
    assert not list((state / "discovery" / "skipped").glob("*.json"))
    assert (
        len(
            discover.discover(
                state,
                tmp_path / "retry",
                token=None,
                requested_by=REQUESTED_BY,
                now=NOW,
            )
        )
        == 1
    )
    assert attempts == ["6.5.1", "6.5.1"]


def test_discovery_logs_untrusted_exception_text_on_one_line(stubs, tmp_path, capsys):
    stubs["manifest"]["data_releases"]["uk"]["model_package"]["version"] = (
        "invalid\n::error::injected"
    )
    assert (
        discover.discover(
            tmp_path / "state",
            tmp_path / "work",
            token=None,
            requested_by=REQUESTED_BY,
            now=NOW,
        )
        == []
    )
    output = capsys.readouterr().out
    assert "::error::injected" in output
    assert not any(line.startswith("::") for line in output.splitlines())


@pytest.mark.parametrize("outcome", ["good", "transient", "permanent"])
def test_default_three_request_and_thirty_attempt_bounds(
    tmp_path, monkeypatch, outcome
):
    assert discover.MAX_PER_RUN == 3
    assert discover.MAX_ATTEMPTS_PER_RUN == 30
    monkeypatch.setattr(
        discover,
        "pypi",
        lambda package: {"releases": {f"6.5.{i}": [] for i in range(1, 36)}},
    )
    attempts = []

    def provisional(version, work, **kwargs):
        attempts.append(version)
        if outcome == "transient":
            raise TimeoutError("retry later")
        if outcome == "permanent":
            raise discover.Skipped(
                "immutable mismatch",
                permanent=True,
                evidence_sha256={"wheel": "a" * 64},
            )
        return request_for(version)

    monkeypatch.setattr(discover, "provisional_request", provisional)
    state = tmp_path / "state"
    requests = discover.discover(
        state, tmp_path / "work", token=None, requested_by=REQUESTED_BY, now=NOW
    )
    assert len(requests) == (3 if outcome == "good" else 0)
    assert len(attempts) == (3 if outcome == "good" else 30)
    assert len(list((state / "discovery" / "skipped").glob("*.json"))) == (
        30 if outcome == "permanent" else 0
    )


def test_permanent_skip_reason_stays_within_public_schema_limit(tmp_path, monkeypatch):
    monkeypatch.setattr(discover, "pypi", lambda package: {"releases": {"6.5.1": []}})

    def provisional(*args, **kwargs):
        raise discover.Skipped(
            "untrusted " * 1000, permanent=True, evidence_sha256={"wheel": "a" * 64}
        )

    monkeypatch.setattr(discover, "provisional_request", provisional)
    state = tmp_path / "state"
    assert (
        discover.discover(
            state, tmp_path / "work", token=None, requested_by=REQUESTED_BY, now=NOW
        )
        == []
    )
    record = json.loads((state / "discovery" / "skipped" / "6.5.1.json").read_text())
    assert len(record["reason"]) == 2000
