"""Offline contracts for the OBR costing registry and compute pipeline.

These tests deliberately stop before ``managed_microsimulation``.  Engine
validation instantiates only PolicyEngine-UK's parameter/variable system, and
the command-line test exercises ``--dry-run`` against synthetic source rows.
"""

from __future__ import annotations

import copy
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from pipeline import compute_uk_obr_costings as compute


ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "data" / "uk" / "obr_measure_reforms.yaml"
STAGED_REQUIRED_FIELDS = {
    "external_claim_match",
    "engine_version",
    "data_bundle",
    "pe_value",
    "status",
    "pe_construction",
    "computed_at",
    "run_id",
    "annotations",
}


@pytest.fixture()
def synthetic_measure():
    return {
        "measure_key": "synthetic_event__income_tax_change",
        "fiscal_event": "Synthetic event",
        "obr_description": "Synthetic income tax change",
        "source_table": "Synthetic PMD table",
        "external_metric": "revenue_change",
        "start_fy": 2026,
        "computability": "expressible",
        "construction": "reversal_on_certified_world",
        "pe_reform": {
            "gov.hmrc.income_tax.allowances.personal_allowance.amount": {
                "2026-01-01.2026-12-31": 13_070
            }
        },
        "heads": [
            {
                "obr_head": "Income tax",
                "condition_key": "tax_head",
                "pe_variables": ["income_tax"],
                "channel": "tax",
            }
        ],
        "unmapped_obr_heads": [],
        "notes": "Synthetic construction used only by unit tests.",
    }


@pytest.fixture()
def synthetic_claim(synthetic_measure):
    # Include every PMD discriminator, plus a source note, so the staging test
    # catches any code that silently reduces the harvested conditions mapping.
    conditions = {
        "geography": "United Kingdom",
        "fy": "2026-27",
        "fiscal_event": synthetic_measure["fiscal_event"],
        "tax_head": "Income tax",
        "basis": "nominal",
        "costing_phase": "final",
        "sign_convention": "positive_gain_to_exchequer",
        "note": "retain verbatim",
    }
    return {
        "source": "obr",
        "source_table": synthetic_measure["source_table"],
        "reform_hint": synthetic_measure["obr_description"],
        "metric": "revenue_change",
        "period": 2026,
        "conditions": conditions,
        "value": 40.0,
        "value_raw": "£0.00000004bn",
        "normalization": "synthetic GBP fixture",
        "proposed_unit": "gbp",
        "time_basis": "fy",
    }


def synthetic_run(bundle: dict[str, object], income_tax: float) -> dict[str, object]:
    return {
        "policyengine_bundle": bundle,
        "aggregates_gbp": {"income_tax": income_tax},
        "variable_metadata": {
            "income_tax": {
                "label": "Income Tax",
                "entity": "person",
                "definition_period": "year",
                "unit": "currency-GBP",
            }
        },
        "performance": {
            "wall_seconds": 0.01,
            "peak_rss_bytes": 1,
        },
    }


def test_committed_registry_schema_and_counts():
    spec = compute.load_registry(REGISTRY)
    summary = compute.validate_registry(spec)

    assert spec["schema_version"] == 1
    assert spec["benchmark_class"] == "different_model"
    assert summary == {
        "measures": 20,
        "computability": {
            "expressible": 8,
            "not_expressible": 4,
            "partial": 8,
        },
        "source_head_years": 0,
    }
    assert all(
        measure["pe_reform"] is None
        for measure in spec["measures"]
        if measure["computability"] == "not_expressible"
    )
    assert all(
        measure["pe_reform"]
        for measure in spec["measures"]
        if measure["computability"] != "not_expressible"
    )


def test_registry_rejects_duplicate_keys_and_non_finite_reform_values():
    spec = compute.load_registry(REGISTRY)
    duplicate = copy.deepcopy(spec)
    duplicate["measures"].append(copy.deepcopy(duplicate["measures"][0]))
    with pytest.raises(compute.RegistryError, match="duplicate measure_key"):
        compute.validate_registry(duplicate)

    non_finite = copy.deepcopy(spec)
    reform = non_finite["measures"][0]["pe_reform"]
    first_schedule = next(iter(reform.values()))
    first_period = next(iter(first_schedule))
    first_schedule[first_period] = float("nan")
    with pytest.raises(compute.RegistryError, match="must be finite"):
        compute.validate_registry(non_finite)


def test_every_registry_parameter_and_variable_resolves_in_installed_engine():
    if importlib.util.find_spec("policyengine_uk") is None:
        pytest.skip("policyengine-uk is not installed")
    try:
        from policyengine_uk import CountryTaxBenefitSystem
    except ImportError as exc:
        pytest.skip(f"policyengine-uk cannot be imported: {exc}")

    system = CountryTaxBenefitSystem()
    summary = compute.validate_registry(
        compute.load_registry(REGISTRY), tax_benefit_system=system
    )
    assert summary["measures"] == 20


def test_nics_head_is_exact_required_class_1_employee_employer_plus_class_4():
    spec = compute.load_registry(REGISTRY)
    assert spec["head_definitions"]["national_insurance"]["pe_variables"] == (
        compute.NI_HEAD_VARIABLES
    )

    nics_heads = [
        head
        for measure in spec["measures"]
        for head in measure["heads"]
        if head["obr_head"] == "NICs"
    ]
    assert nics_heads
    assert all(head["pe_variables"] == compute.NI_HEAD_VARIABLES for head in nics_heads)
    assert all("national_insurance" not in head["pe_variables"] for head in nics_heads)


def test_tax_and_spending_sign_mapping_from_synthetic_aggregates():
    baseline = {"income_tax": 100.0, "universal_credit": 60.0}
    reform = {"income_tax": 125.0, "universal_credit": 72.0}

    tax_delta = compute.reform_minus_baseline(baseline, reform, ["income_tax"])
    spending_delta = compute.reform_minus_baseline(
        baseline, reform, ["universal_credit"]
    )
    assert tax_delta == 25.0
    assert compute.to_exchequer_gain(tax_delta, "tax") == 25.0
    assert spending_delta == 12.0
    assert compute.to_exchequer_gain(spending_delta, "spending") == -12.0
    with pytest.raises(ValueError, match="unknown channel"):
        compute.to_exchequer_gain(1.0, "borrowing")


def test_configure_offline_overrides_network_enabled_environment(monkeypatch):
    keys = {
        "HF_HUB_OFFLINE",
        "TRANSFORMERS_OFFLINE",
        "HF_DATASETS_OFFLINE",
        "HF_HUB_DISABLE_TELEMETRY",
    }
    for key in keys:
        monkeypatch.setenv(key, "0")

    compute.configure_offline()

    assert {key: os.environ[key] for key in keys} == {key: "1" for key in keys}


def test_artifact_and_staged_row_preserve_claim_and_run_provenance(
    tmp_path, synthetic_measure, synthetic_claim
):
    bundle = {
        "certified_data_build_id": "synthetic-certified-build",
        "country_package_version": "2.89.2-test",
    }
    output_path = tmp_path / "synthetic_2026.json"
    artifact = compute.build_artifact(
        measure=synthetic_measure,
        year=2026,
        baseline=synthetic_run(bundle, 100.0),
        reform=synthetic_run(bundle, 125.0),
        output_path=output_path,
        computed_at="2026-08-16T12:00:00+00:00",
        run_id="campaign-20260816-obr-costings",
        claims=[synthetic_claim],
    )
    compute.write_json(output_path, artifact)
    rows = compute.stage_artifact_rows(artifact, synthetic_measure)

    assert len(rows) == 1
    row = rows[0]
    assert STAGED_REQUIRED_FIELDS <= set(row)
    assert row["external_claim_match"] == {
        "source": synthetic_claim["source"],
        "metric": synthetic_claim["metric"],
        "period": synthetic_claim["period"],
        "conditions": synthetic_claim["conditions"],
    }
    assert row["external_claim_match"]["conditions"] == synthetic_claim["conditions"]
    assert set(row["external_claim_match"]) == {
        "source",
        "metric",
        "period",
        "conditions",
    }
    assert row["benchmark_class"] == "different_model"
    assert row["status"] == "constructed"
    assert row["pe_value"] == 25.0
    assert row["engine_version"] == artifact["engine_version"]
    assert row["data_bundle"] == artifact["data_bundle"]
    assert row["run_id"] == artifact["run_id"]
    assert row["artifact"] == artifact["artifact"] == str(output_path.resolve())
    assert artifact["artifact"] in row["pe_construction"]
    assert any("static microsimulation" in note for note in row["annotations"])
    assert any("behavioural-adjusted" in note for note in row["annotations"])
    assert any(
        "not the OBR announcement baseline" in note for note in row["annotations"]
    )
    assert any("calendar year 2026" in note for note in row["annotations"])
    assert any("Head mapping" in note for note in row["annotations"])

    saved = json.loads(output_path.read_text())
    assert saved["data_bundle"] == bundle["certified_data_build_id"]
    assert saved["policyengine_bundles"] == {
        "baseline": bundle,
        "reform": bundle,
    }
    assert saved["reform"] == synthetic_measure["pe_reform"]
    assert saved["raw_aggregates"] == {
        "baseline_gbp": {"income_tax": 100.0},
        "reform_gbp": {"income_tax": 125.0},
    }
    assert (
        saved["heads"][0]["external_claim"]["conditions"]
        == synthetic_claim["conditions"]
    )
    assert saved["heads"][0]["raw_reform_minus_baseline_gbp"] == 25.0


def test_resolver_rejects_ambiguous_and_missing_mapped_heads(
    synthetic_measure, synthetic_claim
):
    head = synthetic_measure["heads"][0]
    with pytest.raises(compute.ClaimMatchError, match="2 source matches"):
        compute.resolve_claim(
            [synthetic_claim, copy.deepcopy(synthetic_claim)],
            synthetic_measure,
            head,
            2026,
        )

    other_head_claim = copy.deepcopy(synthetic_claim)
    other_head_claim["conditions"]["tax_head"] = "NICs"
    with pytest.raises(compute.ClaimMatchError, match="zero matches"):
        compute.resolve_claim([other_head_claim], synthetic_measure, head, 2026)

    assert (
        compute.resolve_claim([synthetic_claim], synthetic_measure, head, 2025) is None
    )


def test_json_writers_reject_non_finite_values(tmp_path):
    json_path = tmp_path / "bad.json"
    jsonl_path = tmp_path / "bad.jsonl"

    with pytest.raises(ValueError, match="Out of range float values"):
        compute.write_json(json_path, {"pe_value": float("nan")})
    with pytest.raises(ValueError, match="Out of range float values"):
        compute.write_jsonl(jsonl_path, [{"pe_value": float("inf")}])

    assert not json_path.exists()
    assert not jsonl_path.exists()


def test_default_measure_selection_retains_null_reforms():
    measures = compute.load_registry(REGISTRY)["measures"]
    selected = compute.select_measures(measures, requested=None, limit=None)

    assert selected == measures
    assert any(measure["pe_reform"] is None for measure in selected)


def test_bundle_mismatches_abort_before_artifact_staging(tmp_path, synthetic_measure):
    release_bundle = {
        "certified_data_build_id": "release-build",
        "country_package_version": "2.89.2",
    }
    runtime_bundle = {
        "certified_data_build_id": "different-build",
        "country_package_version": "2.89.2",
    }
    with pytest.raises(RuntimeError, match="differs from release bundle"):
        compute.assert_managed_bundle(runtime_bundle, release_bundle)

    with pytest.raises(RuntimeError, match="baseline/reform bundles differ"):
        compute.build_artifact(
            measure=synthetic_measure,
            year=2026,
            baseline=synthetic_run(release_bundle, 100.0),
            reform=synthetic_run(runtime_bundle, 125.0),
            output_path=tmp_path / "must-not-exist.json",
            computed_at="2026-08-16T12:00:00+00:00",
            run_id="campaign-20260816-obr-costings",
            claims=None,
        )
    assert not (tmp_path / "must-not-exist.json").exists()


def test_dry_run_is_offline_and_writes_no_simulation_outputs(
    tmp_path, synthetic_measure, synthetic_claim
):
    if importlib.util.find_spec("policyengine_uk") is None:
        pytest.skip("policyengine-uk is not installed")

    registry_path = tmp_path / "registry.yaml"
    claims_path = tmp_path / "claims.jsonl"
    output_dir = tmp_path / "artifacts"
    staged_path = tmp_path / "staged.jsonl"
    registry_path.write_text(
        yaml.safe_dump(
            {
                "schema_version": 1,
                "benchmark_class": "different_model",
                "measures": [synthetic_measure],
            },
            sort_keys=False,
        )
    )
    claims_path.write_text(json.dumps(synthetic_claim, allow_nan=False) + "\n")
    environment = os.environ.copy()
    environment.update(
        {
            "HF_HUB_OFFLINE": "0",
            "TRANSFORMERS_OFFLINE": "0",
            "HF_DATASETS_OFFLINE": "0",
            "HF_HUB_DISABLE_TELEMETRY": "0",
            "HF_HOME": str(tmp_path / "empty-hf-cache"),
        }
    )

    completed = subprocess.run(
        [
            sys.executable,
            str(compute.__file__),
            "--registry",
            str(registry_path),
            "--claims",
            str(claims_path),
            "--output-dir",
            str(output_dir),
            "--staged-output",
            str(staged_path),
            "--years",
            "2026",
            "--limit",
            "1",
            "--dry-run",
        ],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert '"HF_HUB_OFFLINE": "1"' in completed.stdout
    assert '"TRANSFORMERS_OFFLINE": "1"' in completed.stdout
    assert '"HF_DATASETS_OFFLINE": "1"' in completed.stdout
    assert "dry-run complete: no managed microsimulation constructed" in (
        completed.stdout
    )
    assert not output_dir.exists()
    assert not staged_path.exists()
