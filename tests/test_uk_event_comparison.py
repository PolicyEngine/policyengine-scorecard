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


@pytest.mark.parametrize("reason_field", ["scope_reason", "classification_reason"])
def test_outside_source_heads_use_their_account_scope_reason(inputs, reason_field):
    registry, staged, root = inputs
    measure = registry["measures"][0]
    measure["classification"] = "partial"
    measure["missing_legs"] = ["Household eligibility history is unavailable"]
    source = {
        "source_row_id": "departmental",
        "fy": "2024-25",
        "tax_head": "PSCE in RDEL",
        "value_gbp": -100.0,
        "value_gbp_decimal": "-100.0",
        "classification": "out_of_household_scope",
        reason_field: "Departmental expenditure is outside household tax-benefit scope",
    }
    measure["source_rows"].append(source)
    staged.append(
        {
            "source_row_id": "departmental",
            "measure_key": measure["measure_key"],
            "fy": "2024-25",
            "tax_head": "PSCE in RDEL",
            "external_value_gbp": -100.0,
            "external_value_gbp_decimal": "-100.0",
            "pe_value": None,
            "head_variables": [],
            "status": "not_computed",
            "reason": "Household eligibility history is unavailable",
        }
    )
    rows = build_comparison_rows(registry, staged, artifact_root=root)
    household = next(row for row in rows if row["source_row_id"] == "row")
    departmental = next(row for row in rows if row["source_row_id"] == "departmental")
    assert household["reason"] == measure["missing_legs"][0]
    assert departmental["reason"] == source[reason_field]
    assert departmental["classification"] == "out_of_household_scope"
    assert "Departmental expenditure is outside" in render_csv(rows)
    assert "Departmental expenditure is outside" in render_markdown(registry, rows)


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
    assert "employer_ni.employee_incidence=1" in markdown
    assert "not a fixed-wage static costing" in markdown
    assert "indirect macroeconomic effects" in markdown


def test_gap_kind_split_preserves_row_scope_and_exact_amounts(inputs):
    registry, staged, root = inputs
    measure = registry["measures"][0]
    measure.update(classification="not_expressible", gap_kind="construction_pending")
    staged[0].update(pe_value=None, artifact_path=None, artifact_sha256=None)
    second = copy.deepcopy(measure)
    second.update(measure_key="event__missing_model", gap_kind="model_or_data_gap")
    second["source_rows"][0].update(
        source_row_id="model", value_gbp=-10.0, value_gbp_decimal="-10.0"
    )
    outside = copy.deepcopy(second["source_rows"][0])
    outside.update(source_row_id="outside", classification="out_of_household_scope")
    second["source_rows"].append(outside)
    registry["measures"].append(second)
    for source in second["source_rows"]:
        staged.append(
            {
                **staged[0],
                "source_row_id": source["source_row_id"],
                "measure_key": second["measure_key"],
                "external_value_gbp": source["value_gbp"],
                "external_value_gbp_decimal": source["value_gbp_decimal"],
            }
        )
    rows = build_comparison_rows(registry, staged, artifact_root=root)
    assert [r["gap_kind"] for r in rows] == [
        "model_or_data_gap",
        None,
        "construction_pending",
    ]
    markdown = render_markdown(registry, rows)
    assert "| construction_pending | 1 | 1 |" in markdown
    assert "| model_or_data_gap | 1 | 1 |" in markdown
    assert "not_expressible / construction_pending" in markdown
    assert "gap_kind" in render_csv(rows).splitlines()[0]
    registry["accounting"] = {"rows_in": 3, "by_class": {}}
    summary = render_summary({"event": rows}, registries={"event": registry})
    assert "| event / construction_pending | 1 | 1 |" in summary
    assert "| event / model_or_data_gap | 1 | 1 |" in summary


def test_inert_construction_blocks_complete_summary_and_numeric_assertions(inputs):
    registry, staged, root = inputs
    staged[0]["status"] = "inert_construction"
    with pytest.raises(
        EventComparisonError, match="cannot assert a numeric counterpart"
    ):
        build_comparison_rows(registry, staged, artifact_root=root)
    staged[0].update(
        pe_value=None,
        artifact_path=None,
        artifact_sha256=None,
        reason="identical worlds in an in-force year",
    )
    rows = build_comparison_rows(registry, staged, artifact_root=root)
    grid = {
        "full_event_complete": True,
        "computed_measure_years": 1,
        "full_event_grid_size": 1,
    }
    assert "Numerical replay blocked" in render_markdown(registry, rows, grid)
    summary = render_summary({"event": rows}, replay_grids={"event": grid})
    assert "inert_construction (1 source rows)" in summary
    assert "Registered construction replay complete" not in summary


def test_review_diagnoses_retain_causes_issues_and_opposite_direction(inputs):
    registry, staged, root = inputs
    base = build_comparison_rows(registry, staged, artifact_root=root)[0]
    keys = [
        "spring_budget_2023__pension_annual_allowance_package",
        "spring_budget_2024__hicbc_threshold_and_taper",
        "autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p",
        "spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp",
        "autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp",
        "autumn_budget_2024__capital_gains_main_rates_and_reliefs",
        "autumn_budget_2024__winter_fuel_means_test",
        "autumn_budget_2024__employer_nics_package",
        "event__first_extra",
        "event__second_extra",
        "spring_statement_2025__uc_standard_allowance_above_inflation",
    ]
    rows = [
        {
            **base,
            "measure_key": key,
            "title": key,
            "year": 2029,
            "residual_gbp": 1000.0 - number,
        }
        for number, key in enumerate(keys)
    ]
    summary = render_summary({"event": rows})
    for issue in (
        "policyengine-uk#2237",
        "policyengine-uk#2238",
        "policyengine-uk#2239",
    ):
        assert issue in summary
    assert "fixed on main after the certified pin" in summary
    assert "15–20% above the OBR forecast" in summary
    assert "both reduce the charge" in summary
    assert "opposite to the observed excessive PE tax reduction" in summary
    assert "overstating the announced main-rate tax gain" in summary
    assert "pinned wage-incidence construction" in summary
    assert "Baseline vintage" in summary
    assert "| Cause class |" in summary
    # Reviewed causes remain visible below the first ten rows.
    assert keys[-1] in summary
    diagnosis = comparison.review_diagnosis(keys[-1], 2027)
    assert diagnosis["issues"] == ["policyengine-uk#2239"]
    assert comparison.review_diagnosis(keys[-1], 2026)["issues"] == []


def test_corrected_construction_notes_travel_to_comparison():
    for key in (
        "autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p",
        "spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp",
    ):
        note = comparison.construction_note({"measure_key": key, "note": ""})
        assert "10%→8%" in note
        assert "12%→10%" in note
    cgt = comparison.construction_note(
        {
            "measure_key": "autumn_budget_2024__capital_gains_main_rates_and_reliefs",
            "note": "",
        }
    )
    assert "overstates the announced main-rate tax gain" in cgt
    sdlt = comparison.construction_note(
        {
            "measure_key": "autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp",
            "note": "",
        }
    )
    assert "without a new 30 April conversion" in sdlt
    assert "annual lookups resolve at 1 January" in sdlt
    class_2 = comparison.construction_note(
        {
            "measure_key": "autumn_statement_2023__class_2_abolition",
            "note": "",
        }
    )
    assert "£3.15/week versus the actual £3.45" in class_2
    assert "policyengine-uk#1887" in class_2
    assert "profits >= £12,570" in class_2


def test_class_2_comparison_preserves_class_4_interaction_attribution_limit():
    measure = {
        "measure_key": "autumn_statement_2023__class_2_self_employed_nics_abolition",
        "note": "Restore compulsory Class 2 cash liability.",
    }
    note = comparison.construction_note(measure)
    diagnosis = comparison.review_diagnosis(measure["measure_key"], 2027)
    for text in (note, diagnosis["evidence"]):
        assert "−£552.039m in ni_class_2" in text
        assert "−£786.808m in ni_class_4" in text
        assert "pinned" in text
        assert "floating-point" in text
    assert "has not been causally traced" in note
    assert "a full household trace" in diagnosis["evidence"]
    assert "£1,849.49" in diagnosis["evidence"]
    assert diagnosis["issues"] == []


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
    assert "construction/head_scope" in summary
    assert "raw gaps remains unsized" in summary


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


@pytest.mark.parametrize("run_id", ["modal_repeat_1", "modal_repeat_2"])
def test_actual_fresh_repeat_receipt_binds_canonical_bytes_and_coverage(run_id):
    proof = json.loads(
        (
            comparison.ROOT / "results/uk/events/DETERMINISM_VERIFICATION.json"
        ).read_bytes()
    )
    artifact_path = comparison.ROOT / proof["frozen_artifact_copy"]["path"]
    digest = hashlib.sha256(artifact_path.read_bytes()).hexdigest()
    repeat = next(run for run in proof["runs"] if run["run_id"] == run_id)
    assert digest == proof["frozen_artifact_copy"]["sha256"]
    assert digest == proof["canonical_artifact"]["sha256"]
    assert digest == proof["initial_local_observation"]["artifact_sha256"]
    assert digest == repeat["artifact_sha256"]
    assert repeat["byte_identical_to_initial_and_canonical"] is True
    assert repeat["field_differences"] == []
    receipt = repeat["receipt"]
    assert receipt["request"]["preflight_only"] is False
    assert receipt["runtime"]["block_network"] is True
    assert receipt["runtime"]["workers"] == 1
    serialized_inputs = (
        json.dumps(repeat["input_manifest"], indent=1, sort_keys=True, allow_nan=False)
        + "\n"
    ).encode()
    assert (
        receipt["input_manifest_sha256"]
        == hashlib.sha256(serialized_inputs).hexdigest()
    )
    serialized_request = (
        json.dumps(receipt["request"], indent=1, sort_keys=True, allow_nan=False) + "\n"
    ).encode()
    assert receipt["request_sha256"] == hashlib.sha256(serialized_request).hexdigest()
    serialized_receipt = (
        json.dumps(receipt, indent=1, sort_keys=True, allow_nan=False) + "\n"
    ).encode()
    assert repeat["receipt_sha256"] == hashlib.sha256(serialized_receipt).hexdigest()
    manifest = repeat["run_manifest"]
    selected = [{"measure_key": proof["measure_key"], "year": proof["year"]}]
    assert manifest["requested_grid"] == manifest["artifact_grid"] == selected
    assert list(manifest["artifacts"].values()) == [digest]
    assert manifest["registry_sha256"] == proof["registry_sha256"]
    assert repeat["full_event_grid_size"] == 30
    assert manifest["full_event_complete"] is False
    artifact_value = json.loads(artifact_path.read_bytes())
    assert repeat["measure_total_gbp"] == artifact_value["measure_total_gbp"]
    assert (
        manifest["certified_dataset_sha256"]
        == artifact_value["certified_dataset_sha256"]
    )
    validate_artifact(artifact_value, "recorded actual replay")


def test_current_registry_receipt_retains_numeric_identity_and_honest_coverage():
    proof = json.loads(
        (
            comparison.ROOT / "results/uk/events/DETERMINISM_CURRENT_REGISTRY.json"
        ).read_bytes()
    )
    current_path = comparison.ROOT / proof["frozen_artifact_copy"]["path"]
    current_bytes = current_path.read_bytes()
    current = json.loads(current_bytes)
    historic = json.loads(
        (comparison.ROOT / proof["compared_historic_artifact"]["path"]).read_bytes()
    )
    assert hashlib.sha256(current_bytes).hexdigest() == proof["artifact_sha256"]
    assert current["registry_sha256"] == proof["registry_sha256"]
    differences = [key for key in current if current[key] != historic[key]]
    assert differences == ["registry_sha256"]
    assert proof["numeric_values_identical_to_historic"] is True
    assert proof["byte_identical_to_historic"] is False
    assert proof["computed_measure_years"] == 1
    assert proof["full_event_grid_size"] == 30
    assert proof["full_event_complete"] is False
    manifest = proof["run_manifest"]
    assert manifest["requested_grid"] == manifest["artifact_grid"]
    assert len(manifest["artifact_grid"]) == 1
    assert manifest["registry_sha256"] == current["registry_sha256"]
    assert list(manifest["artifacts"].values()) == [proof["artifact_sha256"]]
    inputs_bytes = (
        json.dumps(proof["input_manifest"], indent=1, sort_keys=True, allow_nan=False)
        + "\n"
    ).encode()
    assert (
        hashlib.sha256(inputs_bytes).hexdigest()
        == proof["receipt"]["input_manifest_sha256"]
    )
    assert proof["receipt"]["runtime"]["block_network"] is True
    assert proof["receipt"]["runtime"]["workers"] == 1
    validate_artifact(current, "current-registry actual focused replay")


@given(st.integers(-(10**9), 10**9), st.integers(-(10**9), 10**9))
@settings(deadline=None)
def test_residual_accounting_is_conserved(gap, amount):
    result = describe_decomposition(gap, ["head_scope"], [component(amount)])
    assert (
        result["residual_gbp"]
        + sum(c["value_gbp"] for c in result["valued_components"])
        == gap
    )
