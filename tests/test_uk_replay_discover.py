"""Catch-up discovery of undispatched policyengine.py releases.

PyPI, the wheel, the data release manifest and the scratch install are
stubbed; the request is built from them exactly as in a scheduled run.
"""

import hashlib
import io
import json
import zipfile
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from pipeline import uk_replay_discover as discover
from pipeline import uk_replay_qualify as qualify
from pipeline import uk_replay_variants as rv

FIXTURES = Path(__file__).parent / "fixtures" / "uk_replay"
REQUESTED_BY = {"repository": "PolicyEngine/policyengine-scorecard", "commit": "0" * 40}


def golden():
    return json.loads((FIXTURES / "qualification_request_golden.json").read_text())


def wheel_bytes(manifest: dict, requires: list[str]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as wheel:
        wheel.writestr(discover.MANIFEST_PATH, json.dumps(manifest))
        wheel.writestr(
            "policyengine-6.3.0.dist-info/METADATA",
            "Metadata-Version: 2.1\nName: policyengine\nVersion: 6.3.0\n"
            + "".join(f"Requires-Dist: {line}\n" for line in requires),
        )
    return buffer.getvalue()


def bundle_manifest(model_sha="b" * 64, dataset_sha="d" * 64):
    return {
        "data_releases": {
            "uk": {
                "model_package": {
                    "name": "policyengine-uk",
                    "version": "2.126.8",
                    "sha256": model_sha,
                },
                "certified_data_artifact": {
                    "build_id": "policyengine-uk-data-1.59.0",
                    "dataset": "enhanced_frs_2024_25",
                    "sha256": dataset_sha,
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
                    "6.3.0": [],
                    "6.3.1rc1": [],
                    "junk": [],
                }
            }
        if package == "policyengine":
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
        "6.3.0", tmp_path, token=None, requested_by=REQUESTED_BY
    )
    request["candidate"]["expected_release_bundle"] = {
        **golden()["candidate"]["expected_release_bundle"],
        "policyengine_version": "6.3.0",
        "model_version": "2.126.8",
    }
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
    with pytest.raises(discover.Skipped):
        discover.provisional_request(
            "6.3.0", tmp_path, token=None, requested_by=REQUESTED_BY
        )


def test_candidates_are_newer_unrequested_final_releases(tmp_path):
    document = rv.load_document()
    request = golden()
    request["kind"] = "released_bundle"
    request["candidate"]["policyengine"]["version"] = "6.3.0"
    directory = tmp_path / "requests" / ("a" * 64)
    directory.mkdir(parents=True)
    (directory / "REQUEST.json").write_text(json.dumps(request))
    versions = [
        "6.2.5",
        "6.2.6",
        "6.3.0",
        "6.3.1",
        "6.10.0",
        "6.4.0rc1",
        "junk",
        "7.0.0",
    ]
    assert discover.candidates(versions, document, tmp_path) == [
        "6.3.1",
        "6.10.0",
        "7.0.0",
    ]


def test_discovery_caps_each_run_and_continues_past_a_skip(
    stubs, tmp_path, monkeypatch, capsys
):
    monkeypatch.setattr(discover, "MAX_PER_RUN", 1)
    monkeypatch.setattr(
        discover,
        "expected_bundle",
        lambda request, work: {
            **golden()["candidate"]["expected_release_bundle"],
            "policyengine_version": request["candidate"]["policyengine"]["version"],
            "model_version": "2.126.8",
        },
    )
    found = discover.discover(
        tmp_path / "state", tmp_path / "work", token=None, requested_by=REQUESTED_BY
    )
    assert [r["candidate"]["policyengine"]["version"] for r in found] == ["6.3.0"]
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
    assert all(Version(v) > Version("6.2.6") for v in out)
    assert set(out) == {v for v in versions if Version(v) > Version("6.2.6")}
