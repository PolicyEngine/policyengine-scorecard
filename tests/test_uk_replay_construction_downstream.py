"""Engine-free consumers retain revision and refused-world evidence."""

import copy
import hashlib
import json
import subprocess
from pathlib import Path

import pytest

from pipeline import compare_uk_event as compare
from pipeline import compute_uk_ab2025 as worlds
from pipeline import compute_uk_event as compute
from pipeline import diff_uk_event_runs as diff
from pipeline import stage_uk_event as stage
from pipeline import uk_construction_revisions as revisions
from pipeline import uk_replay_interface as interface
from pipeline import uk_replay_qualify as qualify
from pipeline import uk_replay_variants as variants

EVENT = "autumn_budget_2024"
KEY = f"{EVENT}__capital_gains_main_rates_and_reliefs"
CURRENT = "pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0"


def selected_revision():
    return revisions.select_revision(KEY, lambda path: {"fiscal_year_blend": True})


@pytest.mark.parametrize("revised", [False, True])
def test_staging_reads_recorded_revision_activation(tmp_path, monkeypatch, revised):
    registry = json.loads(
        (compute.ROOT / f"data/uk/events/{EVENT}_measures.json").read_bytes()
    )
    measure = next(m for m in registry["measures"] if m["measure_key"] == KEY)
    registry["measures"] = [measure]
    registry["calendar_years"] = [2024]
    world = worlds.worlds_for(measure, {KEY: measure}, years=[2024])
    evidence = selected_revision() if revised else None
    world = revisions.apply_selected_revision(KEY, world, evidence)
    variables = compute.variable_channels(measure)
    simulation = {
        "aggregates_gbp": {v: 1000.0 for v in variables},
        "variable_metadata": {v: {} for v in variables},
        "policyengine_bundle": {
            "model_version": "test",
            "certified_data_build_id": "test",
        },
        "dataset_sha256_before": "a" * 64,
        "dataset_sha256_after": "a" * 64,
    }
    artifact = compute.build_artifact(
        measure=measure,
        world=world,
        year=2024,
        baseline=simulation,
        reform=simulation,
        certified=simulation,
        registry_sha256="b" * 64,
        event=EVENT,
    )
    payload = compute.canonical_bytes(artifact)
    (tmp_path / "cgt.json").write_bytes(payload)
    manifest = {
        "event": EVENT,
        "registry_sha256": "b" * 64,
        "certified_dataset_sha256": "a" * 64,
        "artifacts": {"cgt.json": hashlib.sha256(payload).hexdigest()},
    }
    if evidence is not None:
        manifest["construction_revisions"] = {KEY: evidence}
    monkeypatch.setattr(compute, "ROOT", tmp_path)
    monkeypatch.setattr(stage, "manifest_variant", lambda *a, **k: None)
    rows, tally = stage.stage_event(
        registry, manifest, artifact_dir=tmp_path, registry_sha256="b" * 64
    )
    source = next(
        row
        for row in measure["source_rows"]
        if row["fy"] == "2024-25" and row["tax_head"] == "Capital gains tax"
    )
    assert stage.mapped_variables(source, measure) == ["capital_gains_tax"]
    first_year = next(
        row for row in rows if row["source_row_id"] == source["source_row_id"]
    )
    # Refusing a counterpart intentionally leaves head_variables empty, so
    # identify the registered source head independently of its staged status.
    assert first_year["status"] == ("inert_construction" if revised else "not_computed")
    assert bool(tally.get("inert_measure_years")) is revised
    if revised:
        artifact.pop("construction_revision")
        payload = compute.canonical_bytes(artifact)
        (tmp_path / "cgt.json").write_bytes(payload)
        manifest["artifacts"]["cgt.json"] = hashlib.sha256(payload).hexdigest()
        with pytest.raises(ValueError, match="artifact construction revision differs"):
            stage.stage_event(
                registry, manifest, artifact_dir=tmp_path, registry_sha256="b" * 64
            )


def test_comparison_note_reports_the_revision_that_ran(tmp_path):
    evidence = selected_revision()
    (tmp_path / "RUN_MANIFEST.json").write_text(
        json.dumps(
            {
                "engine_version": "engine-with-blend",
                "variant_id": "variant",
                "construction_revisions": {KEY: evidence},
            }
        )
    )
    identity = compare.run_identity(tmp_path)
    note = compare.construction_note({"measure_key": KEY}, identity=identity)
    # The note is the registry's own record of the revision that ran.
    recorded = revisions.get_revision(KEY, evidence)
    assert note.startswith(f"Construction revision {evidence['revision_id']} ran:")
    assert recorded["intent"] in note and "FY2024-25" in note
    assert all(limitation in note for limitation in recorded["limitations"])
    assert "Business Asset Disposal Relief" in note
    assert compare.construction_note({"measure_key": KEY, "note": "frozen"}) != note


def test_release_diff_flags_a_recorded_construction_revision(tmp_path, monkeypatch):
    from test_uk_event_diff import KEY as SYNTHETIC_KEY
    from test_uk_event_diff import make_namespace, synthetic_record

    monkeypatch.setattr(compute, "ROOT", tmp_path)
    monkeypatch.setattr(stage, "manifest_variant", synthetic_record)
    base, head = make_namespace(tmp_path, "base"), make_namespace(tmp_path, "head")
    event = next(iter(head["events"]))
    head["events"][event]["artifacts"][(SYNTHETIC_KEY, 2024)]["artifact"][
        "construction_revision"
    ] = selected_revision()
    record = next(
        r
        for r in diff.diff_sides(base, head)["rows"]
        if r["level"] == "measure_year" and r["year"] == 2024
    )
    assert record["flags"] == ["construction"]
    assert [d["code"] for d in record["details"]] == ["construction_revision_changed"]
    reverse = next(
        r
        for r in diff.diff_sides(head, base)["rows"]
        if r["level"] == "measure_year" and r["year"] == 2024
    )
    assert reverse["flags"] == record["flags"]
    assert reverse["details"][0]["head"] is None


def test_release_diff_binds_premises_revision_to_the_run():
    evidence = selected_revision()
    identity = {
        "policyengine_version": "wrapper",
        "policyengine_uk_version": "engine",
        "policyengine_core_version": "core",
    }
    premises = {
        "engine": {
            "policyengine": "wrapper",
            "policyengine_uk": "engine",
            "policyengine_core": "core",
        },
        "events": {
            EVENT: {
                "registry_sha256": "b" * 64,
                "measures": {KEY: {"construction_revision": evidence}},
            }
        },
    }
    events = {
        EVENT: {
            "registry_sha256": "b" * 64,
            "manifest": {"construction_revisions": {KEY: evidence}},
        }
    }
    diff._verify_premises(
        premises, identity, events, Path("CONSTRUCTION_PREMISES.json")
    )
    events[EVENT]["manifest"].pop("construction_revisions")
    with pytest.raises(diff.DiffError, match="premises construction revisions differ"):
        diff._verify_premises(
            premises, identity, events, Path("CONSTRUCTION_PREMISES.json")
        )


def mismatch():
    return {
        "code": "processed_value_mismatch",
        "event": EVENT,
        "measure_key": KEY,
        "year": 2024,
        "world": "baseline_world",
        "path": "gov.hmrc.cgt.basic_rate",
        "intended": 0.13463013698630138,
        "processed": 0.1138082191780822,
    }


@pytest.mark.parametrize(
    "world", ["baseline_world", "reform_world", "certified_current_law"]
)
def test_refused_world_becomes_an_integrity_failure_in_the_v1_receipt(
    tmp_path, monkeypatch, world
):
    record = variants.get_variant(CURRENT)
    namespace = variants.namespace_root(record, root=tmp_path)
    refused = {**mismatch(), "world": world}

    def run(command, *, cwd):
        if "pipeline.compute_uk_event" in command:
            directory = namespace / EVENT
            directory.mkdir(parents=True)
            (directory / "INTEGRITY_FAILURES.json").write_text(json.dumps([refused]))
            raise subprocess.CalledProcessError(1, command)

    monkeypatch.setattr(qualify, "run", run)
    failures = qualify.run_corpus(
        record, tmp_path / "variants.json", events=(EVENT,), root=tmp_path
    )
    assert len(failures) == 1 and failures[0]["code"] == "processed_value_mismatch"
    assert json.loads(failures[0]["detail"]) == {
        k: refused[k] for k in ("world", "path", "intended", "processed")
    }
    # W4's v1 failure schema is closed. The exact values remain machine-readable
    # JSON in detail; the receiving interface does not need a schema upgrade.
    assert set(failures[0]) == {"code", "detail", "event", "measure_key", "year"}
    monkeypatch.setattr(qualify, "event_results", lambda *a, **k: ({}, []))
    request = json.loads(
        (
            Path(__file__).parent
            / "fixtures/uk_replay/qualification_request_golden.json"
        ).read_bytes()
    )
    receipt = qualify.build_receipt(
        request,
        record=record,
        failures=failures,
        root=tmp_path,
        results_path="requests/x/results/",
    )
    assert receipt["status"] == receipt["integrity"]["status"] == "failed"
    interface.validate(qualify.seal(namespace, receipt), interface.RECEIPT_SCHEMA_ID)


@pytest.mark.parametrize(
    "field,value",
    [
        ("event", "other"),
        ("world", "other"),
        ("year", True),
        ("path", ""),
        ("code", "other"),
    ],
)
def test_refused_world_evidence_must_identify_this_event(tmp_path, field, value):
    evidence = copy.deepcopy(mismatch())
    evidence[field] = value
    path = tmp_path / "INTEGRITY_FAILURES.json"
    path.write_text(json.dumps([evidence]))
    with pytest.raises(ValueError, match="invalid processed-value evidence"):
        qualify.processed_value_failures(path, EVENT)
