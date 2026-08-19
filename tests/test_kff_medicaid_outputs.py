"""Aggregate-output coverage for the KFF Medicaid campaign lane."""

import csv
import json
import sqlite3

import pytest

from pipeline.build_kff_medicaid_outputs import REFORM_REF, RUN_ID, aggregate
from scorecard_db.ingest_campaign import ingest
from scorecard_db.models import ReformRef


ENGINE = "1.764.6"
DATA_BUNDLE = "populace-us-2024-buildp-sparse-rmloss100-cae8640-20260728T011454Z"
BUNDLE_ID = "us-5.0.2"


def _write_csv(path, columns):
    rows = [
        dict(zip(columns, values, strict=True))
        for values in zip(*columns.values(), strict=True)
    ]
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(columns))
        writer.writeheader()
        writer.writerows(rows)


def _write_extracts(
    tmp_path,
    *,
    sample: bool = True,
    weights: list | None = None,
    engine: str = ENGINE,
    data_bundle: str = DATA_BUNDLE,
    bundle_id: str = BUNDLE_ID,
):
    baseline = {
        "person_id": [1, 2, 3, 4, 5, 6],
        "state": ["CA", "CA", "CA", "TX", "TX", "TX"],
        "age": [30, 10, 70, 40, 17, 25],
        "person_weight": weights or [2.0, 3.0, 5.0, 7.0, 11.0, 13.0],
        "is_medicaid_eligible": [True, True, True, True, False, True],
        "medicaid_enrolled": [True, False, False, False, False, True],
        "medicaid": [1_000.0, 0.0, 0.0, 0.0, 0.0, 2_000.0],
        "medicaid_slcsp_state_denominator": [10.0] * 3 + [20.0] * 3,
        "reported_uninsured": [False, True, False, False, True, True],
        "modeled_uninsured": [False, True, False, False, True, False],
    }
    reform = dict(baseline)
    reform["medicaid_enrolled"] = [True, True, True, True, False, True]
    reform["medicaid"] = [1_100.0, 1_200.0, 1_300.0, 1_400.0, 0.0, 2_100.0]
    baseline_path = tmp_path / "baseline.csv"
    reform_path = tmp_path / "reform.csv"
    _write_csv(baseline_path, baseline)
    _write_csv(reform_path, reform)

    bundle = {
        "model_version": engine,
        "certified_data_build_id": data_bundle,
        "bundle_id": bundle_id,
    }
    common = {
        "sample": sample,
        "engine_version": engine,
        "data_bundle": data_bundle,
        "bundle_id": bundle_id,
        "policyengine_bundle": bundle,
        "coverage_inputs": ["has_esi"],
        "medicare_handling": "medicare_enrolled modeled proxy",
    }
    baseline_meta = {**common, "computed_at": "2026-08-18T18:00:00+00:00"}
    reform_meta = {**common, "computed_at": "2026-08-18T19:00:00+00:00"}
    for path, metadata in (
        (baseline_path, baseline_meta),
        (reform_path, reform_meta),
    ):
        tmp_path.joinpath(f"{path.name}.meta.json").write_text(
            json.dumps(metadata) + "\n"
        )
    return baseline_path, reform_path


def _aggregate(tmp_path, baseline_path, reform_path, *, full=False):
    staged = tmp_path / "staged" / "kff_medicaid.jsonl"
    counterparts = tmp_path / "counterparts.json"
    diagnostics = tmp_path / "diagnostics"
    summary = aggregate(
        baseline_path,
        reform_path,
        diagnostics,
        counterparts,
        staged,
        full,
    )
    return summary, staged, counterparts, diagnostics


def test_builder_emits_and_ingests_complete_reform_shape(tmp_path):
    baseline, reform = _write_extracts(tmp_path)
    summary, staged, counterparts, diagnostics = _aggregate(tmp_path, baseline, reform)
    rows = [json.loads(line) for line in staged.read_text().splitlines()]

    assert summary["sample"] is True
    assert summary["delta_enrollment"] == 15.0
    assert summary["bridge_reported_uninsured"] == 3.0
    assert summary["bridge_other_coverage"] == 12.0
    assert len(rows) == summary["campaign_rows"] == 12
    assert {row["exhibit_context"]["geography"] for row in rows} == {
        "US",
        "CA",
        "TX",
    }
    assert {row["exhibit_context"]["component"] for row in rows} == {
        "total",
        "total_spending",
        "marginal_reported_uninsured",
        "marginal_other_coverage",
    }
    assert all(row["sample"] is True for row in rows)
    assert all(row["run_id"] == RUN_ID for row in rows)
    assert all(row["reform_ref"] == REFORM_REF for row in rows)
    assert all(row["engine_version"] == ENGINE for row in rows)
    assert all(row["data_bundle"] == DATA_BUNDLE for row in rows)
    assert all(row["bundle_id"] == BUNDLE_ID for row in rows)
    assert all(row["computed_at"] == "2026-08-18T19:00:00+00:00" for row in rows)
    assert all(row["benchmark_class"] == "different_model" for row in rows)
    assert all(row["calibration_relationship"] == "held_out" for row in rows)
    assert all(row["policyengine_bundle"]["bundle_id"] == BUNDLE_ID for row in rows)
    assert all(
        row["policyengine_bundle"]["certified_data_build_id"] == DATA_BUNDLE
        for row in rows
    )
    assert all(
        "not publishable" in row["annotations"][-5]
        and "all ages" in row["annotations"][-4]
        and "anchor-and-fill" in row["annotations"][-3]
        and "2025 levels" in row["annotations"][-2]
        for row in rows
    )

    by_geo = {}
    for row in rows:
        context = row["exhibit_context"]
        by_geo.setdefault(context["geography"], {})[context["component"]] = row
    for components in by_geo.values():
        total_delta = components["total"]["delta"]
        bridge_delta = (
            components["marginal_reported_uninsured"]["delta"]
            + components["marginal_other_coverage"]["delta"]
        )
        assert bridge_delta == pytest.approx(total_delta)
        for row in components.values():
            assert row["pe_value"] - row["baseline_value"] == pytest.approx(
                row["delta"]
            )

    payload = json.loads(counterparts.read_text())
    assert payload["provenance"]["sample"] is True
    assert all(row["sample"] is True for row in payload["rows"])
    for filename in (
        "kff_medicaid_moments_2024.csv",
        "kff_medicaid_takeup_2024.csv",
    ):
        with (diagnostics / filename).open(newline="") as handle:
            diagnostic_rows = list(csv.DictReader(handle))
        assert diagnostic_rows
        assert all(row["sample"] == "True" for row in diagnostic_rows)

    db_path = tmp_path / "scorecard.db"
    first = ingest(db_path, staged_dir=staged.parent)
    second = ingest(db_path, staged_dir=staged.parent)
    assert (
        first
        == second
        == {
            "attached": 0,
            "exhibits": 12,
            "families": {},
            "exhibits_deferred": [],
        }
    )
    connection = sqlite3.connect(db_path)
    reform_key, reform_json, geography_count = connection.execute(
        "SELECT reform_key, reform_json, COUNT(DISTINCT geography) "
        "FROM pe_exhibits WHERE run_id = ?",
        (RUN_ID,),
    ).fetchone()
    connection.close()
    expected_reform = ReformRef(**REFORM_REF)
    assert reform_key == expected_reform.key() == "849973669b6526d6"
    assert reform_json == expected_reform.to_json()
    assert geography_count == 3


@pytest.mark.parametrize(
    ("sample", "full", "message"),
    (
        (True, True, "cannot be used with validation-sample"),
        (False, False, "full-file extracts require --full"),
    ),
)
def test_builder_requires_sample_full_provenance_agreement(
    tmp_path, sample, full, message
):
    baseline, reform = _write_extracts(tmp_path, sample=sample)
    with pytest.raises(ValueError, match=message):
        _aggregate(tmp_path, baseline, reform, full=full)


def _blank_cell(path, column, row_index=1):
    lines = path.read_text().splitlines()
    header = lines[0].split(",")
    cells = lines[row_index].split(",")
    cells[header.index(column)] = ""
    lines[row_index] = ",".join(cells)
    path.write_text("\n".join(lines) + "\n")


def test_blank_required_numeric_cell_is_rejected(tmp_path):
    baseline, reform = _write_extracts(tmp_path)
    _blank_cell(baseline, "person_weight")
    with pytest.raises(ValueError, match="person_weight"):
        _aggregate(tmp_path, baseline, reform)


def test_blank_denominator_cell_is_allowed(tmp_path):
    baseline, reform = _write_extracts(tmp_path)
    for path in (baseline, reform):
        _blank_cell(path, "medicaid_slcsp_state_denominator")
    summary, staged, _, _ = _aggregate(tmp_path, baseline, reform)
    assert summary["campaign_rows"] == 12
    for line in staged.read_text().splitlines():
        json.loads(line)


# Anchor-passing full-file weights: eligible sums to 77.325M, enrolled to
# 72.300M, both within the 2% anchor gates.
FULL_WEIGHTS = [
    40_000_000.0,
    2_000_000.0,
    1_500_000.0,
    1_525_000.0,
    1_000_000.0,
    32_300_000.0,
]


def test_full_path_passes_anchors_with_certified_provenance(tmp_path):
    baseline, reform = _write_extracts(tmp_path, sample=False, weights=FULL_WEIGHTS)
    summary, staged, _, _ = _aggregate(tmp_path, baseline, reform, full=True)
    assert summary["sample"] is False
    assert summary["eligible"] == pytest.approx(77_325_000.0)
    assert summary["enrolled"] == pytest.approx(72_300_000.0)
    assert summary["delta_enrollment"] == pytest.approx(5_025_000.0)
    rows = [json.loads(line) for line in staged.read_text().splitlines()]
    assert len(rows) == 12
    assert all(row["sample"] is False for row in rows)


def test_full_path_rejects_self_consistent_wrong_provenance(tmp_path):
    baseline, reform = _write_extracts(
        tmp_path, sample=False, weights=FULL_WEIGHTS, engine="1.999.0"
    )
    with pytest.raises(ValueError, match="certified pin"):
        _aggregate(tmp_path, baseline, reform, full=True)
