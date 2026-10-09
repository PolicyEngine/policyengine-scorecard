"""Engine-free event comparison invariants, including sign/scale properties."""

import copy
import hashlib
import json

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from pipeline import compare_uk_event as comparison
from pipeline.compare_uk_event import (
    DEFAULT_AXES,
    EventComparisonError,
    build_comparison_rows,
    describe_decomposition,
    load_verified_comparison,
    render_csv,
    render_markdown,
    render_summary,
    validate_artifact,
    write_comparison,
    write_summary,
)
from pipeline.compare_uk_obr_costings import ratio_and_bin


def artifact(reversal=True):
    return {
        "measure_key": "event__tax",
        "year": 2024,
        "construction": "reversal_on_certified_world"
        if reversal
        else "delta_on_certified_world",
        "head_effects": {"income_tax": 100.0, "ni_class_1_employee": -20.0},
        "head_channels": {"income_tax": "tax", "ni_class_1_employee": "tax"},
        "totals": {
            "baseline": {"heads": {"income_tax": 0.0, "ni_class_1_employee": 20.0}},
            "reform": {"heads": {"income_tax": 100.0, "ni_class_1_employee": 0.0}},
        },
        "measure_total_gbp": 80.0,
        "literal_reform_minus_baseline": {
            "income_tax": -100.0 if reversal else 100.0,
            "ni_class_1_employee": 20.0 if reversal else -20.0,
        },
        "literal_reversal_minus_certified_gbp": -80.0 if reversal else None,
    }


@pytest.fixture
def inputs(tmp_path):
    payload = json.dumps(artifact()).encode()
    (tmp_path / "artifact.json").write_bytes(payload)
    registry = {
        "event_slug": "event",
        "event_name": "Event",
        "measures": [
            {
                "measure_key": "event__tax",
                "title": "Tax change",
                "classification": "expressible",
                "program": "income_tax",
                "source_rows": [
                    {
                        "source_row_id": "row",
                        "fy": "2024-25",
                        "tax_head": "Income tax",
                        "value_gbp": 90.0,
                        "value_gbp_decimal": "90.0",
                    }
                ],
            }
        ],
    }
    staged = [
        {
            "source_row_id": "row",
            "measure_key": "event__tax",
            "fy": "2024-25",
            "tax_head": "Income tax",
            "external_value_gbp": 90.0,
            "external_value_gbp_decimal": "90.0",
            "pe_value": 100.0,
            "head_variables": ["income_tax"],
            "artifact_path": "artifact.json",
            "artifact_sha256": hashlib.sha256(payload).hexdigest(),
            "status": "constructed",
        }
    ]
    return registry, staged, tmp_path


def test_source_rows_preserved_and_artifact_verified(inputs):
    registry, staged, root = inputs
    rows = build_comparison_rows(registry, staged, artifact_root=root)
    assert len(rows) == 1
    assert rows[0]["pe_value_gbp"] == 100
    assert rows[0]["obr_value_gbp_decimal"] == "90.0"
    assert set(DEFAULT_AXES) <= set(rows[0]["axes"])
    assert rows[0]["explained_share"] is None
    assert rows[0]["residual_label"] == "residual_plus_unsized"


@pytest.mark.parametrize(
    "mutation",
    [
        "missing",
        "duplicate",
        "extra",
        "source_value",
        "source_fy",
        "pe_value",
        "digest",
    ],
)
def test_rejects_source_and_artifact_drift(inputs, mutation):
    registry, staged, root = inputs
    if mutation == "missing":
        staged = []
    elif mutation == "duplicate":
        staged.append(copy.deepcopy(staged[0]))
    elif mutation == "extra":
        staged.append({**staged[0], "source_row_id": "extra"})
    elif mutation == "source_value":
        staged[0]["external_value_gbp"] += 1
    elif mutation == "source_fy":
        staged[0]["fy"] = "2025-26"
    elif mutation == "pe_value":
        staged[0]["pe_value"] += 1
    else:
        staged[0]["artifact_sha256"] = "0" * 64
    with pytest.raises(EventComparisonError):
        build_comparison_rows(registry, staged, artifact_root=root)


def test_uncomputed_source_rows_stay_in_comparison(inputs):
    registry, staged, root = inputs
    registry["measures"][0]["classification"] = "not_expressible"
    staged[0].update(
        pe_value=None,
        head_variables=[],
        artifact_path=None,
        artifact_sha256=None,
        reason="pe_gap: no firm entity",
        status="not_computed",
    )
    row = build_comparison_rows(registry, staged, artifact_root=root)[0]
    assert row["obr_value_gbp"] == 90
    assert row["ratio_bin"] == "not_available"
    assert "population_vintage" in row["axes"]


@pytest.mark.parametrize("changed", ["decimal", "number", "missing", "nonfinite"])
def test_exact_source_accounting_rejects_subpenny_drift(inputs, changed):
    registry, staged, root = inputs
    if changed == "decimal":
        staged[0]["external_value_gbp_decimal"] = "90.000000000000000000000001"
    elif changed == "number":
        staged[0]["external_value_gbp"] = 90.0001
    elif changed == "missing":
        staged[0].pop("external_value_gbp_decimal")
    else:
        staged[0]["external_value_gbp_decimal"] = "NaN"
    with pytest.raises(EventComparisonError):
        build_comparison_rows(registry, staged, artifact_root=root)


def test_decimal_commitment_retains_precision_beyond_float(inputs):
    registry, staged, root = inputs
    value = "90.000000000000000000000001"
    registry["measures"][0]["source_rows"][0]["value_gbp_decimal"] = value
    staged[0]["external_value_gbp_decimal"] = value
    rows = build_comparison_rows(registry, staged, artifact_root=root)
    assert rows[0]["obr_value_gbp_decimal"] == value
    assert value in render_csv(rows)


def test_legacy_sources_without_decimal_fields_remain_supported(inputs):
    registry, staged, root = inputs
    registry["measures"][0]["source_rows"][0].pop("value_gbp_decimal")
    staged[0].pop("external_value_gbp_decimal")
    assert build_comparison_rows(registry, staged, artifact_root=root)


def test_measure_class_counts_do_not_overlap_across_source_heads(inputs):
    registry, staged, root = inputs
    registry["measures"][0]["source_rows"][0]["classification"] = (
        "out_of_household_scope"
    )
    rows = build_comparison_rows(registry, staged, artifact_root=root)
    markdown = render_markdown(registry, rows)
    assert "| expressible | 1 | 0 |" in markdown
    assert "| out_of_household_scope | 0 | 1 |" in markdown


def test_partial_construction_warnings_remain_visible(inputs):
    registry, staged, root = inputs
    measure = registry["measures"][0]
    measure.update(
        classification="partial",
        missing_legs=["Rate parameter is under active development"],
        note="Annual period-start sampling delays commencement",
    )
    rows = build_comparison_rows(registry, staged, artifact_root=root)
    assert rows[0]["missing_legs"] == measure["missing_legs"]
    assert rows[0]["construction_note"] == measure["note"]
    assert "under active development" in render_csv(rows)
    markdown = render_markdown(registry, rows)
    assert "under active development" in markdown
    assert "delays commencement" in markdown


@pytest.mark.parametrize("reversal", [True, False])
def test_literal_delta_sign_and_head_total(reversal):
    value = artifact(reversal)
    validate_artifact(value, "test")
    value["head_effects"]["income_tax"] *= -1
    value["measure_total_gbp"] = sum(value["head_effects"].values())
    with pytest.raises(EventComparisonError):
        validate_artifact(value, "test")


def test_deterministic_rendering(inputs):
    registry, staged, root = inputs
    left = build_comparison_rows(registry, staged, artifact_root=root)
    right = build_comparison_rows(registry, staged, artifact_root=root)
    assert render_csv(left).encode() == render_csv(right).encode()
    assert (
        render_markdown(registry, left).encode()
        == render_markdown(registry, right).encode()
    )


def _save_staging(inputs):
    registry, staged, root = inputs
    registry_path, staged_path = root / "registry.json", root / "STAGED.jsonl"
    registry_path.write_text(json.dumps(registry))
    staged_path.write_text("\n".join(json.dumps(r) for r in staged) + "\n")
    manifest = {
        "registry_sha256": hashlib.sha256(registry_path.read_bytes()).hexdigest(),
        "staged_sha256": hashlib.sha256(staged_path.read_bytes()).hexdigest(),
        "staged_rows": len(staged),
        "source_value_gbp_decimal": "90.0",
        "staged_value_gbp_decimal": "90.0",
    }
    (root / "STAGING_MANIFEST.json").write_text(json.dumps(manifest))
    return registry_path, staged_path, root


@pytest.mark.parametrize(
    "field", ["source_value_gbp_decimal", "staged_value_gbp_decimal"]
)
def test_manifest_exact_total_is_checked(inputs, field):
    registry_path, staged_path, root = _save_staging(inputs)
    path = root / "STAGING_MANIFEST.json"
    manifest = json.loads(path.read_text())
    manifest[field] = "90.000000000000000000000001"
    path.write_text(json.dumps(manifest))
    with pytest.raises(EventComparisonError, match="exact £ total"):
        write_comparison(
            "event",
            registry_path=registry_path,
            staged_path=staged_path,
            output_dir=root / "output",
            artifact_root=root,
        )


def test_manifest_bound_comparison_outputs_are_byte_identical(inputs):
    registry_path, staged_path, root = _save_staging(inputs)
    options = {
        "registry_path": registry_path,
        "staged_path": staged_path,
        "output_dir": root / "output",
        "artifact_root": root,
    }
    write_comparison("event", **options)
    before = {p.name: p.read_bytes() for p in (root / "output").iterdir()}
    write_comparison("event", **options)
    assert before == {p.name: p.read_bytes() for p in (root / "output").iterdir()}


@pytest.mark.parametrize("changed", ["registry", "staged"])
def test_manifest_rejects_changed_input_bytes(inputs, changed):
    registry_path, staged_path, root = _save_staging(inputs)
    path = registry_path if changed == "registry" else staged_path
    path.write_bytes(path.read_bytes() + b"\n")
    with pytest.raises(EventComparisonError, match="SHA-256"):
        write_comparison(
            "event",
            registry_path=registry_path,
            staged_path=staged_path,
            output_dir=root / "output",
            artifact_root=root,
        )


def _save_comparison(inputs):
    registry_path, staged_path, root = _save_staging(inputs)
    output = root / "results" / "uk" / "events" / "event"
    rows = write_comparison(
        "event",
        registry_path=registry_path,
        staged_path=staged_path,
        output_dir=output,
        artifact_root=root,
    )
    return rows, output, root


def test_summary_verifies_receipts_before_aggregation(inputs):
    rows, output, root = _save_comparison(inputs)
    assert (
        load_verified_comparison(output / "COMPARISON.json", artifact_root=root) == rows
    )
    write_summary(output.parent, artifact_root=root)
    summary = (output.parent / "SUMMARY.md").read_text()
    assert "Numerical comparison outputs available: 1" in summary
    assert (
        "PYTHONPATH=. .venv-replay/bin/python pipeline/compute_uk_event.py" in summary
    )
    assert (
        "--output-dir .venv-replay-checks/reproductions/event/event__tax_2024"
        in summary
    )


@pytest.mark.parametrize(
    "changed",
    ["registry", "staged", "staging_manifest", "json", "csv", "md", "artifact", "axes"],
)
def test_summary_rejects_stale_or_modified_comparisons(inputs, changed, monkeypatch):
    _, output, root = _save_comparison(inputs)
    paths = {
        "registry": root / "registry.json",
        "staged": root / "STAGED.jsonl",
        "staging_manifest": root / "STAGING_MANIFEST.json",
        "json": output / "COMPARISON.json",
        "csv": output / "COMPARISON.csv",
        "md": output / "COMPARISON.md",
        "artifact": root / "artifact.json",
    }
    if changed == "axes":
        altered = root / "axes.json"
        altered.write_bytes(comparison.AXES_PATH.read_bytes() + b"\n")
        monkeypatch.setattr(comparison, "AXES_PATH", altered)
    else:
        path = paths[changed]
        path.write_bytes(path.read_bytes() + b"\n")
    with pytest.raises(EventComparisonError, match="SHA-256"):
        write_summary(output.parent, artifact_root=root)
    assert not (output.parent / "SUMMARY.md").exists()


def test_summary_rejects_changed_canonical_event_registry(inputs):
    _, output, root = _save_comparison(inputs)
    canonical = root / "data" / "uk" / "events" / "event_measures.json"
    canonical.parent.mkdir(parents=True)
    canonical.write_bytes((root / "registry.json").read_bytes() + b"\n")
    with pytest.raises(EventComparisonError, match="current event registry"):
        write_summary(output.parent, artifact_root=root)


def test_incomplete_grid_is_visible_in_event_and_summary(inputs):
    registry_path, staged_path, root = _save_staging(inputs)
    manifest_path = root / "STAGING_MANIFEST.json"
    manifest = json.loads(manifest_path.read_text())
    manifest.update(
        computed_measure_years=1,
        full_event_grid_size=6,
        full_event_complete=False,
        missing_measure_years=[{"year": 2025}],
    )
    manifest_path.write_text(json.dumps(manifest))
    output = root / "results" / "uk" / "events" / "event"
    write_comparison(
        "event",
        registry_path=registry_path,
        staged_path=staged_path,
        output_dir=output,
        artifact_root=root,
    )
    write_summary(output.parent, artifact_root=root)
    assert (
        "Numerical replay grid incomplete: 1 of 6"
        in (output / "COMPARISON.md").read_text()
    )
    assert "replay grid incomplete (1/6)" in (output.parent / "SUMMARY.md").read_text()


@given(st.integers(1, 10**9), st.integers(-(10**9), 10**9), st.integers(1, 10**6))
@settings(deadline=None)
def test_signed_ratio_bins_are_invariant_to_scale_and_orientation(obr, pe, scale):
    ratio, category = ratio_and_bin(obr, pe)
    scaled_ratio, scaled_category = ratio_and_bin(obr * scale, pe * scale)
    flipped_ratio, flipped_category = ratio_and_bin(-obr, -pe)
    assert scaled_ratio == pytest.approx(ratio)
    assert flipped_ratio == pytest.approx(ratio)
    assert scaled_category == flipped_category == category


@given(st.integers(-(10**9), 10**9), st.integers(-(10**9), 10**9))
@settings(deadline=None)
def test_reversal_orientation_is_an_involution(tax, spending):
    value = artifact()
    value["head_effects"] = {"income_tax": tax, "benefit": -spending}
    value["head_channels"] = {"income_tax": "tax", "benefit": "spending"}
    value["totals"] = {
        "baseline": {"heads": {"income_tax": 0, "benefit": 0}},
        "reform": {"heads": {"income_tax": tax, "benefit": spending}},
    }
    value["measure_total_gbp"] = tax - spending
    value["literal_reform_minus_baseline"] = {"income_tax": -tax, "benefit": spending}
    value["literal_reversal_minus_certified_gbp"] = spending - tax
    validate_artifact(value, "property")


def component(value, axis="head_scope"):
    return {
        "name": "scope",
        "axis": axis,
        "value_gbp": value,
        "status": "sized",
        "provenance": "test fixture primary cell",
    }


def test_axis_tags_do_not_count_as_an_explained_share():
    result = describe_decomposition(100, list(DEFAULT_AXES), [component(50)])
    assert result["explained_share"] is None
    assert "population_vintage" in result["unsized_axes"]
    assert result["residual_gbp"] == 50


@pytest.mark.parametrize("value,share", [(50, 0.5), (-50, None), (150, None)])
def test_complete_decomposition_requires_same_direction_and_share_bound(value, share):
    result = describe_decomposition(100, ["head_scope"], [component(value)])
    assert result["explained_share"] == share


def test_decomposition_refuses_unsupported_provenance():
    value = component(50)
    value.pop("provenance")
    with pytest.raises(EventComparisonError, match="provenance"):
        describe_decomposition(100, ["head_scope"], [value])


def test_decomposition_rejects_duplicate_components():
    with pytest.raises(EventComparisonError, match="unique"):
        describe_decomposition(100, ["head_scope"], [component(25), component(25)])


def test_inventory_summary_does_not_claim_completed_replays(inputs):
    registry, _, _ = inputs
    registry["accounting"] = {
        "rows_in": 1,
        "by_class": {
            "expressible": {
                "measures": 1,
                "rows": 1,
                "net_gbp_decimal": "90",
                "absolute_gbp_decimal": "90",
            }
        },
    }
    summary = render_summary({}, registries={"event": registry})
    assert "Numerical comparison outputs available: 0" in summary
    assert "Registry seeded; numerical replay incomplete" in summary
    assert "Registry coverage does not supply a PE/OBR agreement profile" in summary
    assert "event / expressible" in summary


@given(st.integers(-(10**9), 10**9), st.integers(-(10**9), 10**9))
@settings(deadline=None)
def test_residual_accounting_is_conserved(gap, amount):
    result = describe_decomposition(gap, ["head_scope"], [component(amount)])
    assert (
        result["residual_gbp"]
        + sum(c["value_gbp"] for c in result["valued_components"])
        == gap
    )
