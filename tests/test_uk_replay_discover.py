"""Catch-up discovery of undispatched policyengine.py releases.

PyPI, the wheel and the data release manifest are stubbed; candidate code
is never imported, installed or executed while building a request.
"""

import hashlib
import io
import json
import subprocess
import urllib.error
import zipfile
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from packaging.version import Version

from pipeline import uk_replay_discover as discover
from pipeline import uk_replay_qualify as qualify
from pipeline import uk_replay_variants as rv

FIXTURES = Path(__file__).parent / "fixtures" / "uk_replay"
REQUESTED_BY = {"repository": "PolicyEngine/policyengine-scorecard", "commit": "0" * 40}


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
                    "6.5.0": [],
                    "6.5.1rc1": [],
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

    monkeypatch.setattr(discover, "pypi", pypi)
    monkeypatch.setattr(discover, "fetch", fetch)
    monkeypatch.setattr(discover, "release_manifest", release_manifest)
    return state


def test_a_release_becomes_a_valid_released_bundle_request(stubs, tmp_path):
    request = discover.provisional_request(
        "6.5.0", tmp_path, token=None, requested_by=REQUESTED_BY
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
    assert candidate["expected_release_bundle"] == discover.expected_bundle(
        stubs["manifest"]
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
        "6.5.0", tmp_path, token="read-only-secret", requested_by=REQUESTED_BY
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
            "6.5.0", tmp_path, token=None, requested_by=REQUESTED_BY
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
        "6.5.0", tmp_path, token=None, requested_by=REQUESTED_BY
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
            "6.5.0", tmp_path, token=None, requested_by=REQUESTED_BY
        )
    assert not caught.value.permanent
    assert "data_release_manifest" in caught.value.evidence_sha256


def test_candidates_are_newer_unrequested_final_releases(tmp_path):
    document = rv.load_document()
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
        "6.4.0rc1",
        "junk",
        "7.0.0",
    ]
    assert discover.candidates(versions, document, tmp_path) == [
        "6.5.1",
        "6.10.0",
        "7.0.0",
    ]


@pytest.mark.parametrize("status", ["queued", "running"])
@pytest.mark.parametrize("kind", ["candidate", "released_bundle"])
def test_existing_650_qualification_is_never_discovered_again(tmp_path, status, kind):
    request = json.loads((FIXTURES / "discovery" / "pe6.5.0-request.json").read_bytes())
    request["kind"] = kind
    directory = tmp_path / "requests" / qualify.request_id(request)
    directory.mkdir(parents=True)
    (directory / "REQUEST.json").write_text(json.dumps(request))
    (directory / "STATUS.json").write_text(json.dumps({"status": status}))
    assert discover.candidates(
        ["6.4.1", "6.5.0", "6.5.1"], rv.load_document(), tmp_path
    ) == ["6.5.1"]


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
    ],
)
def test_malformed_stored_requests_do_not_break_discovery(tmp_path, malformed):
    directory = tmp_path / "requests" / ("a" * 64)
    directory.mkdir(parents=True)
    (directory / "REQUEST.json").write_text(json.dumps(malformed))
    assert discover.requested_versions(tmp_path) == set()
    assert discover.candidates(["6.5.0"], rv.load_document(), tmp_path) == ["6.5.0"]


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
            tmp_path / "state", tmp_path / "work", token=None, requested_by=REQUESTED_BY
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
    assert discover.candidates(releases, rv.load_document(), tmp_path) == ["6.5.1"]


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
            "6.5.0", tmp_path, token=None, requested_by=REQUESTED_BY
        )
    assert not caught.value.permanent


def test_discovery_caps_each_run_and_continues_past_a_skip(
    stubs, tmp_path, monkeypatch, capsys
):
    monkeypatch.setattr(discover, "MAX_PER_RUN", 1)
    found = discover.discover(
        tmp_path / "state", tmp_path / "work", token=None, requested_by=REQUESTED_BY
    )
    assert [r["candidate"]["policyengine"]["version"] for r in found] == ["6.5.0"]
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
            tmp_path / "state", tmp_path / "work", token=None, requested_by=REQUESTED_BY
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
            return {"releases": {"6.5.0": [], "6.5.1": []}}
        if package == "policyengine":
            stubs["manifest"] = bundle_manifest()
            if version == "6.5.0":
                if failure == "url-error":
                    raise urllib.error.URLError("PyPI unavailable")
                if failure == "http-error":
                    raise urllib.error.HTTPError("u", 503, "unavailable", {}, None)
                if failure == "missing-uk":
                    stubs["manifest"] = {"data_releases": {}}
            document = original(package, version)
            if version == "6.5.0" and failure in {"missing-manifest", "manifest-json"}:
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
        state, tmp_path / "work", token=None, requested_by=REQUESTED_BY
    )
    assert [r["candidate"]["policyengine"]["version"] for r in requests] == ["6.5.1"]
    assert "policyengine 6.5.0: not requested" in capsys.readouterr().out
    assert not list((state / "discovery" / "skipped").glob("*.json"))


def test_permanent_skips_do_not_starve_the_good_release_in_this_or_next_run(
    stubs, tmp_path, monkeypatch
):
    original = discover.pypi
    attempted = []

    def pypi(package, version=None):
        if version is None:
            return {"releases": {f"6.5.{index}": [] for index in range(4)}}
        if package == "policyengine":
            attempted.append(version)
            stubs["manifest"] = bundle_manifest()
            stubs["requires"] = REQUIRES[1:] if version != "6.5.3" else REQUIRES
        return original(package, version)

    monkeypatch.setattr(discover, "pypi", pypi)
    state = tmp_path / "state"
    requests = discover.discover(
        state, tmp_path / "work", token=None, requested_by=REQUESTED_BY
    )
    assert [r["candidate"]["policyengine"]["version"] for r in requests] == ["6.5.3"]
    assert attempted == ["6.5.0", "6.5.1", "6.5.2", "6.5.3"]
    records = list((state / "discovery" / "skipped").glob("*.json"))
    assert len(records) == 3
    for path in records:
        record = json.loads(path.read_text())
        assert record["reason"].startswith("the wheel's uk extra pins")
        assert set(record["evidence_sha256"]) == {
            "policyengine_wheel",
            "packaged_bundle_manifest",
        }
        assert all(len(digest) == 64 for digest in record["evidence_sha256"].values())
    directory = state / "requests" / qualify.request_id(requests[0])
    directory.mkdir(parents=True)
    (directory / "REQUEST.json").write_text(json.dumps(requests[0]))
    attempted.clear()
    assert (
        discover.discover(
            state, tmp_path / "work2", token=None, requested_by=REQUESTED_BY
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
        lambda package: {"releases": {f"6.5.{i}": [] for i in range(5)}},
    )
    attempted = []

    def provisional(version, work, **kwargs):
        attempted.append(version)
        raise TimeoutError("retry later")

    monkeypatch.setattr(discover, "provisional_request", provisional)
    assert (
        discover.discover(
            tmp_path / "state", tmp_path / "work", token=None, requested_by=REQUESTED_BY
        )
        == []
    )
    assert attempted == ["6.5.0", "6.5.1"]
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
    versions = {f"6.5.{index}": outcome for index, outcome in enumerate(outcomes)}
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
        requests = discover.discover(state, work, token=None, requested_by=REQUESTED_BY)
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
    out = discover.candidates(
        versions, rv.load_document(), tmp_path_factory.mktemp("s")
    )
    from packaging.version import Version

    assert out == sorted(set(out), key=Version)
    assert all(Version(v) > Version("6.4.1") for v in out)
    assert set(out) == {v for v in versions if Version(v) > Version("6.4.1")}
