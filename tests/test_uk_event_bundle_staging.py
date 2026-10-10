"""Bundle isolation at the engine-free staging and comparison boundaries."""

import hashlib
import json

import pytest

from pipeline import compare_uk_event as comparison
from pipeline import stage_uk_event as staging
from pipeline import uk_bundle as bundles

DEV = "test-development-bundle"


@pytest.fixture
def pinned_stage(tmp_path):
    default_pin = tmp_path / "data/uk/certified_bundle.json"
    default_pin.parent.mkdir(parents=True)
    default_pin.write_bytes(bundles.bundle_pin_path().read_bytes())
    pin = bundles.load_bundle()
    pin.update(
        bundle_key=DEV,
        data_year=2024,
        supported_calendar_years=[2024, 2030],
        sha256="d" * 64,
        data_build_id="development-build",
        revision="development-build",
    )
    pin_path = tmp_path / "data/uk/certified_bundles/dev.json"
    pin_path.parent.mkdir(parents=True)
    pin_path.write_text(json.dumps(pin))
    (pin_path.parent / "index.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "default_bundle": bundles.DEFAULT_BUNDLE,
                "bundles": {
                    bundles.DEFAULT_BUNDLE: "data/uk/certified_bundle.json",
                    DEV: "data/uk/certified_bundles/dev.json",
                },
            }
        )
    )
    for label in ("requirements_freeze", "offline_audit"):
        destination = tmp_path / pin[label]
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes((bundles.ROOT / pin[label]).read_bytes())
    identity = bundles.bundle_identity(DEV, root=tmp_path)
    registry = {
        "event_slug": "event",
        "event_name": "Event",
        "calendar_years": [2024],
        "bundle": pin,
        **identity,
        "accounting": {
            "rows_in": 2,
            "by_class": {
                "out_of_household_scope": {
                    "measures": 0,
                    "rows": 2,
                    "net_gbp_decimal": "2",
                    "absolute_gbp_decimal": "2",
                }
            },
        },
        "measures": [
            {
                "measure_key": "event__gap",
                "title": "Gap",
                "computability": "not_expressible",
                "gap_kind": "construction_pending",
                "pe_gap": "Unconstructed test case",
                "source_rows": [
                    {
                        "source_row_id": str(year),
                        "fy": f"{year}-{str(year + 1)[-2:]}",
                        "tax_head": "Other",
                        "metric": "revenue_change",
                        "value_gbp": 1.0,
                        "value_gbp_decimal": "1",
                        "classification": "out_of_household_scope",
                    }
                    for year in (2023, 2024)
                ],
            }
        ],
    }
    registry_path = bundles.registry_path("event", DEV, root=tmp_path)
    registry_path.parent.mkdir(parents=True)
    registry_path.write_text(json.dumps(registry))
    digest = hashlib.sha256(registry_path.read_bytes()).hexdigest()
    output = bundles.event_output_dir("event", DEV, root=tmp_path)
    output.mkdir(parents=True)
    manifest = {
        **identity,
        "event": "event",
        "registry_sha256": digest,
        "artifacts": {},
    }
    return registry, manifest, registry_path, output, tmp_path


def save_stage(values):
    registry, manifest, _registry_path, output, root = values
    rows, tally = staging.stage_event(
        registry,
        manifest,
        artifact_dir=output,
        registry_sha256=manifest["registry_sha256"],
        bundle=DEV,
        bundle_root=root,
    )
    (output / "RUN_MANIFEST.json").write_text(json.dumps(manifest))
    staged = output / "STAGED.jsonl"
    staged.write_text("".join(json.dumps(row) + "\n" for row in rows))
    receipt = {
        **tally,
        "event": "event",
        "staged_path": str(staged.relative_to(root)),
        "staged_sha256": hashlib.sha256(staged.read_bytes()).hexdigest(),
    }
    (output / "STAGING_MANIFEST.json").write_text(json.dumps(receipt))
    return rows, tally, staged


def test_pre_window_source_rows_accounted_once_distinctly_even_outside_scope(
    pinned_stage,
):
    rows, tally, _ = save_stage(pinned_stage)
    outside = next(row for row in rows if row["year"] == 2023)
    assert outside["status"] == "outside_bundle_window"
    assert outside["computability"] == "out_of_household_scope"
    assert outside["pe_value"] is None
    assert tally["source_rows"] == tally["staged_rows"] == 2
    assert tally["source_value_gbp_decimal"] == tally["staged_value_gbp_decimal"] == "2"
    assert tally["bundle_key"] == DEV


@pytest.mark.parametrize(
    "field",
    [
        "bundle_key",
        "bundle_pin_sha256",
        "certified_dataset_sha256",
        "engine_versions",
        "supported_calendar_years",
    ],
)
def test_stage_rejects_foreign_bundle_compute_manifest(pinned_stage, field):
    registry, manifest, _, output, root = pinned_stage
    manifest[field] = "foreign"
    with pytest.raises(ValueError, match="bundle identity mismatch"):
        staging.stage_event(
            registry,
            manifest,
            artifact_dir=output,
            registry_sha256=manifest["registry_sha256"],
            bundle=DEV,
            bundle_root=root,
        )


def test_stage_cli_validates_the_registry_against_the_selected_bundle(
    pinned_stage, monkeypatch
):
    """The CLI must pass --bundle to identity validation, not the default."""
    _registry, _manifest, registry_path, output, _root = pinned_stage
    seen = {}

    class Stop(Exception):
        pass

    def capture(registry, event, bundle=bundles.DEFAULT_BUNDLE):
        seen["bundle"] = bundle
        raise Stop

    monkeypatch.setattr(bundles, "registry_path", lambda event, key: registry_path)
    monkeypatch.setattr(bundles, "event_output_dir", lambda event, key: output)
    monkeypatch.setattr(bundles, "validate_bundle_path", lambda *a, **k: a[0])
    monkeypatch.setattr(staging.compute, "validate_event_identity", capture)
    with pytest.raises(Stop):
        staging.main(["--event", "event", "--bundle", DEV])
    assert seen["bundle"] == DEV


def test_stage_refuses_foreign_registry_or_window(pinned_stage):
    registry, manifest, _, output, root = pinned_stage
    registry["bundle"] = bundles.bundle_document()
    with pytest.raises(ValueError, match="registry bundle pin"):
        staging.stage_event(
            registry,
            manifest,
            artifact_dir=output,
            registry_sha256=manifest["registry_sha256"],
            bundle=DEV,
            bundle_root=root,
        )
    registry["bundle"] = bundles.bundle_document(DEV, root=root)
    registry["calendar_years"] = [2023, 2024]
    with pytest.raises(ValueError, match="year outside"):
        staging.stage_event(
            registry,
            manifest,
            artifact_dir=output,
            registry_sha256=manifest["registry_sha256"],
            bundle=DEV,
            bundle_root=root,
        )


def test_nondefault_comparison_and_summary_bind_selected_pin(pinned_stage):
    _registry, _manifest, registry_path, output, root = pinned_stage
    _, _, staged = save_stage(pinned_stage)
    rows = comparison.write_comparison(
        "event",
        registry_path=registry_path,
        staged_path=staged,
        output_dir=output,
        artifact_root=root,
        bundle=DEV,
    )
    assert rows[0]["status"] == "outside_bundle_window"
    assert (
        comparison.load_verified_comparison(
            output / "COMPARISON.json", artifact_root=root, bundle=DEV
        )
        == rows
    )
    comparison.write_summary(output.parent, artifact_root=root, bundle=DEV)
    prose = (output / "COMPARISON.md").read_text()
    assert "certified 2024 population" in prose
    assert "fiscal-year conversion" in prose
    assert "annualized from the engine's 30 April snapshot" not in prose
    assert DEV in (output.parent / "SUMMARY.md").read_text()
    with pytest.raises(comparison.EventComparisonError):
        comparison.load_verified_comparison(
            output / "COMPARISON.json",
            artifact_root=root,
            bundle=bundles.DEFAULT_BUNDLE,
        )


@pytest.mark.parametrize("receipt", ["stage", "comparison", "registry"])
def test_nondefault_comparison_rejects_foreign_receipts_before_output(
    pinned_stage, receipt
):
    _registry, _manifest, registry_path, output, root = pinned_stage
    _, _, staged = save_stage(pinned_stage)
    comparison.write_comparison(
        "event",
        registry_path=registry_path,
        staged_path=staged,
        output_dir=output,
        artifact_root=root,
        bundle=DEV,
    )
    filename = {
        "stage": output / "STAGING_MANIFEST.json",
        "comparison": output / "COMPARISON_PROVENANCE.json",
        "registry": registry_path,
    }[receipt]
    payload = json.loads(filename.read_text())
    payload["bundle_key"] = bundles.DEFAULT_BUNDLE
    filename.write_text(json.dumps(payload))
    with pytest.raises(comparison.EventComparisonError):
        comparison.write_summary(output.parent, artifact_root=root, bundle=DEV)
    assert not (output.parent / "SUMMARY.md").exists()


def test_comparison_rejects_pre_window_row_without_distinct_status(pinned_stage):
    registry, _, _, _, root = pinned_stage
    rows, _, _ = save_stage(pinned_stage)
    rows[0]["status"] = "not_computed"
    with pytest.raises(comparison.EventComparisonError, match="outside_bundle_window"):
        comparison.build_comparison_rows(registry, rows, artifact_root=root, bundle=DEV)


@pytest.mark.parametrize("kind", ["registry", "results"])
def test_path_selection_rejects_other_bundles_including_default(pinned_stage, kind):
    _, _, _, _, root = pinned_stage
    if kind == "registry":
        foreign = bundles.registry_path("event", bundles.DEFAULT_BUNDLE, root=root)
        selected = bundles.registry_path("event", DEV, root=root)
    else:
        foreign = bundles.event_output_dir("event", bundles.DEFAULT_BUNDLE, root=root)
        selected = bundles.event_output_dir("event", DEV, root=root)
    with pytest.raises(ValueError, match="another bundle"):
        bundles.validate_bundle_path(foreign, DEV, kind=kind, root=root)
    with pytest.raises(ValueError, match="another bundle"):
        bundles.validate_bundle_path(
            selected, bundles.DEFAULT_BUNDLE, kind=kind, root=root
        )


def test_engine_generator_binds_every_input_and_writes_deterministically(pinned_stage):
    from pipeline import compare_uk_engines as engines

    registry, _manifest, registry_path, output, root = pinned_stage
    _, _, staged = save_stage(pinned_stage)
    comparison.write_comparison(
        "event",
        registry_path=registry_path,
        staged_path=staged,
        output_dir=output,
        artifact_root=root,
        bundle=DEV,
    )
    other = "test-other-development-bundle"
    pin = bundles.load_bundle(DEV, root=root)
    pin.update(bundle_key=other, data_year=2025, supported_calendar_years=[2025, 2030])
    other_pin_path = root / "data/uk/certified_bundles/other.json"
    other_pin_path.write_text(json.dumps(pin))
    index_path = bundles.bundle_index_path(root=root)
    index = json.loads(index_path.read_text())
    index["bundles"][other] = str(other_pin_path.relative_to(root))
    index_path.write_text(json.dumps(index))
    other_identity = bundles.bundle_identity(other, root=root)
    other_registry = {
        **registry,
        **other_identity,
        "bundle": pin,
        "calendar_years": [2025],
    }
    other_registry_path = bundles.registry_path("event", other, root=root)
    other_registry_path.parent.mkdir(parents=True)
    other_registry_path.write_text(json.dumps(other_registry))
    other_output = bundles.event_output_dir("event", other, root=root)
    other_output.mkdir(parents=True)
    other_manifest = {
        **other_identity,
        "event": "event",
        "artifacts": {},
        "registry_sha256": hashlib.sha256(other_registry_path.read_bytes()).hexdigest(),
    }
    (other_output / "RUN_MANIFEST.json").write_text(json.dumps(other_manifest))
    other_rows, tally = staging.stage_event(
        other_registry,
        other_manifest,
        artifact_dir=other_output,
        registry_sha256=other_manifest["registry_sha256"],
        bundle=other,
        bundle_root=root,
    )
    other_staged = other_output / "STAGED.jsonl"
    other_staged.write_text("".join(json.dumps(row) + "\n" for row in other_rows))
    (other_output / "STAGING_MANIFEST.json").write_text(
        json.dumps(
            {
                **tally,
                "event": "event",
                "staged_sha256": hashlib.sha256(other_staged.read_bytes()).hexdigest(),
            }
        )
    )
    comparison.write_comparison(
        "event",
        registry_path=other_registry_path,
        staged_path=other_staged,
        output_dir=other_output,
        artifact_root=root,
        bundle=other,
    )
    axes = root / "data/uk/obr_divergence_axes.json"
    axes.write_bytes(comparison.AXES_PATH.read_bytes())
    attribution_path = root / "data/uk/events/engine_attribution/example.json"
    attribution_path.parent.mkdir(parents=True)
    attribution_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "base": DEV,
                "new": other,
                "entries": [
                    {
                        "event": "event",
                        "measure_key": "event__gap",
                        "drivers": [
                            {
                                "driver": "window_change",
                                "evidence": [
                                    {
                                        "kind": "diagnostic",
                                        "reference": "test-only window observation",
                                    }
                                ],
                                "sized": False,
                            }
                        ],
                    }
                ],
            }
        )
    )
    rows = engines.write_engine_comparison(
        DEV, other, attribution_path=attribution_path, artifact_root=root
    )
    assert len(rows) == 2
    directory = root / "results/uk/events"
    before = {
        path.name: path.read_bytes() for path in directory.glob("ENGINE_COMPARISON*")
    }
    assert set(before) == {
        "ENGINE_COMPARISON.json",
        "ENGINE_COMPARISON.csv",
        "ENGINE_COMPARISON.md",
        "ENGINE_COMPARISON_PROVENANCE.json",
    }
    provenance = json.loads(before["ENGINE_COMPARISON_PROVENANCE.json"])
    expected_inputs = [
        registry_path,
        other_registry_path,
        attribution_path,
        index_path,
        axes,
        bundles.bundle_pin_path(DEV, root=root),
        other_pin_path,
        output / "RUN_MANIFEST.json",
        other_output / "RUN_MANIFEST.json",
        root / pin["requirements_freeze"],
        root / pin["offline_audit"],
    ]
    assert all(
        str(path.relative_to(root)) in provenance["inputs_sha256"]
        for path in expected_inputs
    )
    for reference, digest in provenance["inputs_sha256"].items():
        assert hashlib.sha256((root / reference).read_bytes()).hexdigest() == digest
    engines.write_engine_comparison(
        DEV, other, attribution_path=attribution_path, artifact_root=root
    )
    assert before == {
        path.name: path.read_bytes() for path in directory.glob("ENGINE_COMPARISON*")
    }
    missing_comparisons = [
        bundles.registry_path("uncompared_event", key, root=root)
        for key in (DEV, other)
    ]
    for uncomputed_registry in missing_comparisons:
        uncomputed_registry.write_bytes(registry_path.read_bytes())
    with pytest.raises(engines.EngineComparisonError, match="every event"):
        engines.write_engine_comparison(
            DEV, other, attribution_path=attribution_path, artifact_root=root
        )
    assert before == {
        path.name: path.read_bytes() for path in directory.glob("ENGINE_COMPARISON*")
    }
    for uncomputed_registry in missing_comparisons:
        uncomputed_registry.unlink()
    staged.write_bytes(staged.read_bytes() + b"\n")
    with pytest.raises(comparison.EventComparisonError, match="SHA-256"):
        engines.write_engine_comparison(
            DEV, other, attribution_path=attribution_path, artifact_root=root
        )
    assert before == {
        path.name: path.read_bytes() for path in directory.glob("ENGINE_COMPARISON*")
    }


def test_sized_paired_artifact_verifies_real_endpoints(pinned_stage):
    from pipeline import compare_uk_engines as engines

    _registry, manifest, _registry_path, _output, root = pinned_stage
    endpoints = {}
    for side, value in (("base", 100), ("new", 120)):
        numerical = {
            **bundles.bundle_identity(DEV, root=root),
            "measure_key": "event__tax",
            "year": 2024,
            "event": "event",
            "registry_sha256": manifest["registry_sha256"],
            "construction": "forward_delta_on_certified_world",
            "head_effects": {"income_tax": value},
            "head_channels": {"income_tax": "tax"},
            "totals": {
                "baseline": {"heads": {"income_tax": 0}},
                "reform": {"heads": {"income_tax": value}},
            },
            "literal_reform_minus_baseline": {"income_tax": value},
            "measure_total_gbp": value,
        }
        path = root / f"{side}.json"
        path.write_bytes(engines.canonical_bytes(numerical))
        endpoints[side] = {
            "path": path.name,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
    paired = {
        "artifact_type": "paired_run",
        "status": "computed",
        "effect_gbp": 20,
        "base_bundle": DEV,
        "new_bundle": DEV,
        "base_artifact": endpoints["base"],
        "new_artifact": endpoints["new"],
        "head_variables": ["income_tax"],
    }
    path = root / "paired.json"
    path.write_bytes(engines.canonical_bytes(paired))
    attribution = {
        "schema_version": 1,
        "entries": [
            {
                "event": "event",
                "measure_key": "event__tax",
                "fy": "2024-25",
                "drivers": [
                    {
                        "driver": "other_engine_change",
                        "sized": True,
                        "value_gbp": 20,
                        "evidence": [
                            {"kind": "paired_run", "reference": "paired.json"}
                        ],
                        "artifact": {
                            "path": path.name,
                            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                            "value_path": ["effect_gbp"],
                        },
                    }
                ],
            }
        ],
    }
    hashes = {}
    engines.validate_attribution(attribution, artifact_root=root, input_hashes=hashes)
    assert set(hashes) == {"base.json", "new.json", "paired.json"}
    # Copying a paired receipt under another name does not create a second
    # independently sized contribution from the same executed endpoints.
    second_pair = {**paired, "note": "another named mechanism, same numerical term"}
    second_path = root / "paired-copy.json"
    second_path.write_bytes(engines.canonical_bytes(second_pair))
    first_driver = attribution["entries"][0]["drivers"][0]
    second_driver = json.loads(json.dumps(first_driver))
    second_driver.update(driver="data_release")
    second_driver["artifact"].update(
        path=second_path.name,
        sha256=hashlib.sha256(second_path.read_bytes()).hexdigest(),
    )
    attribution["entries"][0]["drivers"].append(second_driver)
    with pytest.raises(engines.EngineComparisonError, match="same computed term"):
        engines.validate_attribution(attribution, artifact_root=root)
    attribution["entries"][0]["drivers"].pop()
    (root / "new.json").write_bytes((root / "new.json").read_bytes() + b"\n")
    with pytest.raises(engines.EngineComparisonError, match="endpoint SHA-256"):
        engines.validate_attribution(attribution, artifact_root=root)


def test_summary_rejects_another_bundles_model_observations(pinned_stage):
    _registry, _manifest, registry_path, output, root = pinned_stage
    _, _, staged = save_stage(pinned_stage)
    comparison.write_comparison(
        "event",
        registry_path=registry_path,
        staged_path=staged,
        output_dir=output,
        artifact_root=root,
        bundle=DEV,
    )
    foreign_diagnostic = {
        "bundle_key": bundles.DEFAULT_BUNDLE,
        "engine_version": "2.89.2",
    }
    (output.parent / "MODEL_DIAGNOSTICS.json").write_text(
        json.dumps([foreign_diagnostic])
    )
    with pytest.raises(
        comparison.EventComparisonError, match="bundle identity mismatch"
    ):
        comparison.write_summary(output.parent, artifact_root=root, bundle=DEV)
    assert not (output.parent / "SUMMARY.md").exists()
