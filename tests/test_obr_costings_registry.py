"""Offline contracts for the OBR costing registry and compute pipeline.

These tests deliberately stop before ``managed_microsimulation``. Engine
validation instantiates only PolicyEngine-UK's parameter/variable system, and
the command-line tests exercise ``--dry-run`` and artifact-only ``--restage``
against synthetic source rows.
"""

from __future__ import annotations

import copy
import csv
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from pipeline import compare_uk_obr_costings as compare
from pipeline import compute_uk_obr_costings as compute


ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "data" / "uk" / "obr_measure_reforms.yaml"
SMOKE_STAGED = ROOT / "results" / "uk" / "staged" / "obr_costings.jsonl"
SMOKE_MANIFEST = ROOT / "results" / "uk" / "obr_costings" / "RUN_MANIFEST.json"
SMOKE_COMPARISON = ROOT / "results" / "uk" / "obr_costings" / "COMPARISON.csv"
VENDORED_CLAIMS = (
    ROOT / "sources" / "harvest-20260802" / "uk_obr" / "obr_costings_claims.jsonl"
)
FULL_HARVEST_CLAIMS = (
    Path.home() / "scorecard-harvest" / "uk_obr" / "claims_staged.jsonl"
)
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
    "source_model",
    "basis",
    "behavioural_adjustment",
}
DIVIDEND_LAG_NOTE = (
    "pe-uk 2.89.2 dividend band thresholds lag the main bands until "
    "2026-04-06 (policyengine-uk#1822); dividend leg not assumption-matched "
    "for these years"
)
SYNTHETIC_DATASET_SHA256 = "a" * 64
SYNTHETIC_CLAIMS_SHA256 = "b" * 64
SYNTHETIC_REGISTRY_SHA256 = "d" * 64


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
        "impact_channel": "tax",
        "line_item": synthetic_measure["obr_description"],
        "sign_convention": "positive_gain_to_exchequer",
        "spending_head": "None",
        "note": "retain verbatim",
    }
    return {
        "source": "obr",
        "source_model": "synthetic_source_model",
        "source_table": synthetic_measure["source_table"],
        "reform_hint": synthetic_measure["obr_description"],
        "metric": "revenue_change",
        "period": 2026,
        "conditions": conditions,
        "value": -40.0,
        "value_raw": "-£0.00000004bn",
        "normalization": "synthetic GBP fixture",
        "proposed_unit": "gbp",
        "time_basis": "fy",
        "publication": {
            "publisher": "Synthetic OBR publisher",
            "title": "Synthetic costing publication",
            "publication_url": "https://example.test/publication",
            "sign_convention": "positive_gain_to_exchequer",
            "url": "https://example.test/workbook.xlsx",
            "units_note": "GBP",
            "vintage": "Synthetic 2026 vintage",
            "wayback": "https://web.archive.test/workbook.xlsx",
            "workbook": "workbook.xlsx",
        },
        "source_column": "2026-27",
        "status": "ok",
        "calibration_relationship": "held_out",
    }


def synthetic_run(bundle: dict[str, object], income_tax: float) -> dict[str, object]:
    runtime_bundle = dict(bundle)
    expected_sha256 = runtime_bundle.setdefault(
        "certified_data_artifact_sha256", SYNTHETIC_DATASET_SHA256
    )
    return {
        "policyengine_bundle": runtime_bundle,
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
        "dataset_sha256_before": expected_sha256,
        "dataset_sha256_after": expected_sha256,
    }


def synthetic_run_for_variables(
    bundle: dict[str, object], variables: list[str], value: float
) -> dict[str, object]:
    run = synthetic_run(bundle, value)
    run["aggregates_gbp"] = {name: value for name in variables}
    run["variable_metadata"] = {
        name: {
            "label": name,
            "entity": "synthetic",
            "definition_period": "year",
            "unit": "currency-GBP",
        }
        for name in variables
    }
    return run


def test_committed_registry_schema_and_counts():
    spec = compute.load_registry(REGISTRY)
    summary = compute.validate_registry(spec)

    assert spec["schema_version"] == 1
    assert spec["benchmark_class"] == "different_model"
    assert summary == {
        "measures": 26,
        "computability": {
            "expressible": 3,
            "not_expressible": 5,
            "partial": 18,
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
    assert (
        sum(
            measure["construction"] == "reversal_on_certified_world"
            for measure in spec["measures"]
        )
        == 25
    )
    assert (
        sum(
            measure["construction"] == "forward_from_baseline"
            for measure in spec["measures"]
        )
        == 1
    )
    assert (
        sum(
            bool(measure.get("computability_overrides")) for measure in spec["measures"]
        )
        == 2
    )


def test_registry_start_fy_matches_first_nonzero_vendored_costing():
    spec = compute.load_registry(REGISTRY)
    claims = compute.load_claims(VENDORED_CLAIMS)

    summary = compute.validate_registry(spec, claims=claims)

    assert summary["source_head_years"] == 215
    changed = copy.deepcopy(spec)
    changed["measures"][0]["start_fy"] += 1
    with pytest.raises(
        compute.RegistryError,
        match="first nonzero harvested costing",
    ):
        compute.validate_registry(changed, claims=claims)


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

    invalid_override = copy.deepcopy(spec)
    invalid_override["measures"][0]["computability_overrides"] = {
        True: {"computability": "partial", "note": "invalid boolean year"}
    }
    with pytest.raises(
        compute.RegistryError, match="invalid computability override year"
    ):
        compute.validate_registry(invalid_override)

    incomplete_override = copy.deepcopy(spec)
    incomplete_override["measures"][0]["computability_overrides"] = {
        2024: {"computability": "partial"}
    }
    with pytest.raises(compute.RegistryError, match="must contain exactly"):
        compute.validate_registry(incomplete_override)


DIVIDEND_HIGHER_THRESHOLD = "gov.hmrc.income_tax.rates.dividends[1].threshold"
DIVIDEND_ADDITIONAL_THRESHOLD = "gov.hmrc.income_tax.rates.dividends[2].threshold"


def _installed_dividend_threshold_values(rates):
    years = range(compute.YEAR_MIN, compute.YEAR_MAX + 1)
    return {
        DIVIDEND_HIGHER_THRESHOLD: {
            year: (
                rates.uk[1].threshold(f"{year}-01-01"),
                rates.dividends[1].threshold(f"{year}-01-01"),
            )
            for year in years
        },
        DIVIDEND_ADDITIONAL_THRESHOLD: {
            year: (
                rates.uk[2].threshold(f"{year}-01-01"),
                rates.dividends[2].threshold(f"{year}-01-01"),
            )
            for year in years
        },
    }


def _dividend_path_lag_expectations(measures, installed):
    expectations = {}
    for measure in measures:
        for path, schedule in (measure["pe_reform"] or {}).items():
            if path not in installed:
                continue
            scheduled_years = set()
            for date_range in schedule:
                match = compute.DATE_RANGE.fullmatch(str(date_range))
                assert match is not None
                first_year = int(match.group(1))
                final_year = int(match.group(4))
                scheduled_years.update(range(first_year, final_year + 1))
            expectations[(measure["measure_key"], path)] = {
                year
                for year, (main_value, dividend_value) in installed[path].items()
                if year in scheduled_years and dividend_value != main_value
            }
    return expectations


def _dividend_lag_override_findings(measures, expectations):
    findings = []
    expected_override = {
        "computability": "partial",
        "note": DIVIDEND_LAG_NOTE,
    }
    for measure in measures:
        measure_key = measure["measure_key"]
        path_expectations = {
            path: years
            for (key, path), years in expectations.items()
            if key == measure_key
        }
        expected_years = set().union(*path_expectations.values())
        overrides = measure.get("computability_overrides", {})
        invalid_years = sorted(
            year
            for year, override in overrides.items()
            if override != expected_override
        )
        if invalid_years:
            findings.append(f"{measure_key}: invalid overrides {invalid_years}")
        actual_years = set(overrides)
        missing = sorted(expected_years - actual_years)
        if missing:
            paths = sorted(
                path
                for path, years in path_expectations.items()
                if years.intersection(missing)
            )
            findings.append(f"{measure_key} {', '.join(paths)}: missing {missing}")
        unnecessary = sorted(actual_years - expected_years)
        if unnecessary:
            paths = sorted(path_expectations) or ["no dividend threshold path"]
            findings.append(
                f"{measure_key} {', '.join(paths)}: unnecessary {unnecessary}"
            )
    return findings


def test_dividend_lag_overrides_match_installed_engine_dates_per_path():
    if importlib.util.find_spec("policyengine_uk") is None:
        pytest.skip("policyengine-uk is not installed")
    try:
        from policyengine_uk import CountryTaxBenefitSystem
    except ImportError as exc:
        pytest.skip(f"policyengine-uk cannot be imported: {exc}")

    system = CountryTaxBenefitSystem()
    rates = system.parameters.gov.hmrc.income_tax.rates
    installed = _installed_dividend_threshold_values(rates)
    measures = compute.load_registry(REGISTRY)["measures"]
    expectations = _dividend_path_lag_expectations(measures, installed)

    assert compute.package_version("policyengine-uk") == "2.89.2"
    assert installed[DIVIDEND_HIGHER_THRESHOLD][2024] == (37_700, 37_500)
    assert installed[DIVIDEND_HIGHER_THRESHOLD][2025] == (37_700, 37_500)
    assert installed[DIVIDEND_HIGHER_THRESHOLD][2026] == (37_700, 37_700)
    assert installed[DIVIDEND_ADDITIONAL_THRESHOLD][2024] == (125_140, 150_000)
    assert installed[DIVIDEND_ADDITIONAL_THRESHOLD][2025] == (125_140, 150_000)
    assert installed[DIVIDEND_ADDITIONAL_THRESHOLD][2026] == (125_140, 125_140)
    assert expectations == {
        (
            "efo_march_2026__pa_and_hrt_freezes",
            DIVIDEND_HIGHER_THRESHOLD,
        ): {2024, 2025},
        (
            "efo_march_2026__additional_rate_threshold_reduction",
            DIVIDEND_ADDITIONAL_THRESHOLD,
        ): {2024, 2025},
        (
            "autumn_budget_2025__personal_tax_and_nics_threshold_freeze_extension",
            DIVIDEND_HIGHER_THRESHOLD,
        ): set(),
    }
    assert _dividend_lag_override_findings(measures, expectations) == []

    for measure in measures:
        expected_years = set().union(
            *(
                years
                for (key, _), years in expectations.items()
                if key == measure["measure_key"]
            )
        )
        for year in range(compute.YEAR_MIN, compute.YEAR_MAX + 1):
            status, note = compute.effective_computability(measure, year)
            if year in expected_years:
                assert (status, note) == ("partial", DIVIDEND_LAG_NOTE)
            else:
                assert status == measure["computability"]
                assert note is None


def test_dividend_lag_reports_one_caught_up_path_override_as_unnecessary():
    installed = {
        DIVIDEND_HIGHER_THRESHOLD: {
            year: (37_700, 37_500 if year in {2024, 2025} else 37_700)
            for year in range(compute.YEAR_MIN, compute.YEAR_MAX + 1)
        },
        DIVIDEND_ADDITIONAL_THRESHOLD: {
            year: (125_140, 150_000 if year in {2024, 2025} else 125_140)
            for year in range(compute.YEAR_MIN, compute.YEAR_MAX + 1)
        },
    }
    for year in (2024, 2025):
        main_value, _ = installed[DIVIDEND_HIGHER_THRESHOLD][year]
        installed[DIVIDEND_HIGHER_THRESHOLD][year] = (main_value, main_value)
    measures = compute.load_registry(REGISTRY)["measures"]
    expectations = _dividend_path_lag_expectations(measures, installed)

    assert (
        expectations[("efo_march_2026__pa_and_hrt_freezes", DIVIDEND_HIGHER_THRESHOLD)]
        == set()
    )
    assert expectations[
        (
            "efo_march_2026__additional_rate_threshold_reduction",
            DIVIDEND_ADDITIONAL_THRESHOLD,
        )
    ] == {2024, 2025}
    assert _dividend_lag_override_findings(measures, expectations) == [
        "efo_march_2026__pa_and_hrt_freezes "
        f"{DIVIDEND_HIGHER_THRESHOLD}: unnecessary [2024, 2025]"
    ]


def test_dividend_lag_override_is_effective_only_for_affected_artifact_years(
    tmp_path,
):
    measures = {
        measure["measure_key"]: measure
        for measure in compute.load_registry(REGISTRY)["measures"]
    }
    measure = measures["efo_march_2026__pa_and_hrt_freezes"]
    claims = compute.load_claims(VENDORED_CLAIMS)
    bundle = {"certified_data_build_id": "synthetic-certified-build"}

    artifacts = {}
    for year in (2024, 2026):
        artifacts[year] = compute.build_artifact(
            measure=measure,
            year=year,
            baseline=synthetic_run(bundle, 100.0),
            reform=synthetic_run(bundle, 125.0),
            output_path=tmp_path / f"pa_hrt_{year}.json",
            computed_at="2026-08-16T12:00:00+00:00",
            run_id="campaign-20260816-obr-costings",
            claims=claims,
            claims_sha256=compute.sha256_file(VENDORED_CLAIMS),
            registry_sha256=compute.sha256_file(REGISTRY),
        )

    assert artifacts[2024]["computability"] == "partial"
    assert artifacts[2024]["computability_override"] == {
        "computability": "partial",
        "note": DIVIDEND_LAG_NOTE,
    }
    annotations_2024 = compute.stage_artifact_rows(artifacts[2024], measure)[0][
        "annotations"
    ]
    assert any(DIVIDEND_LAG_NOTE in annotation for annotation in annotations_2024)

    assert artifacts[2026]["computability"] == "expressible"
    assert "computability_override" not in artifacts[2026]
    annotations_2026 = compute.stage_artifact_rows(artifacts[2026], measure)[0][
        "annotations"
    ]
    assert all(DIVIDEND_LAG_NOTE not in annotation for annotation in annotations_2026)


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
    assert summary["measures"] == 26


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


@pytest.mark.parametrize(
    ("construction", "channel", "raw_delta", "literal_delta", "pe_value"),
    [
        ("reversal_on_certified_world", "tax", 25.0, 25.0, -25.0),
        ("reversal_on_certified_world", "spending", 12.0, -12.0, 12.0),
        ("forward_from_baseline", "tax", 25.0, 25.0, 25.0),
        ("forward_from_baseline", "spending", 12.0, -12.0, -12.0),
    ],
)
def test_measure_orientation_for_both_constructions_and_channels(
    construction, channel, raw_delta, literal_delta, pe_value
):
    assert compute.orient_exchequer_effect(raw_delta, channel, construction) == (
        literal_delta,
        pe_value,
    )


def test_measure_orientation_rejects_unknown_channel_and_construction():
    with pytest.raises(ValueError, match="unknown channel"):
        compute.orient_exchequer_effect(1.0, "borrowing", "reversal_on_certified_world")
    with pytest.raises(ValueError, match="unknown construction"):
        compute.orient_exchequer_effect(1.0, "tax", "backward_from_baseline")


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
    assert os.environ["POLICYENGINE_UK_DATA_REPO"] == str(
        compute.LOCAL_DATA_MIRROR_ROOT
    )


def test_runtime_dataset_mutation_between_before_and_after_aborts(tmp_path):
    runtime_dataset_source = tmp_path / "fake-certified-dataset.h5"
    runtime_dataset_source.write_bytes(b"certified bytes")
    expected_sha256 = compute.sha256_file(runtime_dataset_source)

    before = compute.verify_runtime_dataset_sha256(
        runtime_dataset_source,
        expected_sha256,
        phase="immediately before simulation construction",
    )
    runtime_dataset_source.write_bytes(b"mutated bytes")

    assert before == expected_sha256
    with pytest.raises(RuntimeError, match="immediately after aggregate reads"):
        compute.verify_runtime_dataset_sha256(
            runtime_dataset_source,
            expected_sha256,
            phase="immediately after aggregate reads",
        )


def test_run_managed_simulation_rejects_dataset_mutation_during_calculate(
    tmp_path, monkeypatch
):
    runtime_dataset_source = tmp_path / "fake-certified-dataset.h5"
    runtime_dataset_source.write_bytes(b"certified bytes")
    expected_sha256 = compute.sha256_file(runtime_dataset_source)
    mutated_bytes = b"certified bytes!"
    mutated_sha256 = hashlib.sha256(mutated_bytes).hexdigest()
    artifact_path = tmp_path / "must-not-exist.json"

    class FakeCalculated:
        def sum(self):
            return 1.0

    class FakeSimulation:
        policyengine_bundle = {
            "certified_data_build_id": "synthetic-certified-build",
            "runtime_dataset_source": str(runtime_dataset_source),
        }
        tax_benefit_system = SimpleNamespace(variables={"income_tax": object()})

        def calculate(self, name, period):
            assert (name, period) == ("income_tax", "2026")
            runtime_dataset_source.write_bytes(mutated_bytes)
            return FakeCalculated()

    fake_policyengine = SimpleNamespace(
        uk=SimpleNamespace(managed_microsimulation=lambda **kwargs: FakeSimulation())
    )
    monkeypatch.setitem(sys.modules, "policyengine", fake_policyengine)

    with pytest.raises(RuntimeError) as exc_info:
        compute.run_managed_simulation(
            year=2026,
            variables=["income_tax"],
            reform={"synthetic.path": {"2026-01-01.2026-12-31": 1}},
            runtime_dataset_source=runtime_dataset_source,
            expected_dataset_sha256=expected_sha256,
        )

    message = str(exc_info.value)
    assert "immediately after aggregate reads" in message
    assert f"expected {expected_sha256}" in message
    assert f"before {expected_sha256}" in message
    assert f"after {mutated_sha256}" in message
    assert not artifact_path.exists()


def test_run_managed_simulation_checks_dataset_before_construction(
    tmp_path, monkeypatch
):
    runtime_dataset_source = tmp_path / "already-drifted-dataset.h5"
    runtime_dataset_source.write_bytes(b"drifted bytes")
    actual_sha256 = compute.sha256_file(runtime_dataset_source)
    expected_sha256 = hashlib.sha256(b"certified bytes").hexdigest()
    constructed = False

    def construct_simulation(**kwargs):
        nonlocal constructed
        constructed = True
        raise AssertionError("managed simulation was constructed")

    fake_policyengine = SimpleNamespace(
        uk=SimpleNamespace(managed_microsimulation=construct_simulation)
    )
    monkeypatch.setitem(sys.modules, "policyengine", fake_policyengine)

    with pytest.raises(RuntimeError) as exc_info:
        compute.run_managed_simulation(
            year=2026,
            variables=["income_tax"],
            reform=None,
            runtime_dataset_source=runtime_dataset_source,
            expected_dataset_sha256=expected_sha256,
        )

    message = str(exc_info.value)
    assert "immediately before simulation construction" in message
    assert f"expected {expected_sha256}" in message
    assert f"actual {actual_sha256}" in message
    assert constructed is False


def test_new_artifact_records_hashes_for_baseline_and_reform(
    tmp_path, synthetic_measure
):
    expected_sha256 = "a" * 64
    bundle = {
        "certified_data_build_id": "synthetic-certified-build",
        "certified_data_artifact_sha256": expected_sha256,
    }
    baseline = synthetic_run(bundle, 100.0)
    reform = synthetic_run(bundle, 125.0)
    for simulation in (baseline, reform):
        simulation["dataset_sha256_before"] = expected_sha256
        simulation["dataset_sha256_after"] = expected_sha256

    artifact = compute.build_artifact(
        measure=synthetic_measure,
        year=2026,
        baseline=baseline,
        reform=reform,
        output_path=tmp_path / "synthetic_2026.json",
        computed_at="2026-08-17T12:00:00+00:00",
        run_id="campaign-20260817-obr-costings",
        claims=None,
        claims_sha256=SYNTHETIC_CLAIMS_SHA256,
        registry_sha256=SYNTHETIC_REGISTRY_SHA256,
    )

    assert artifact["dataset_sha256_before"] == {
        "baseline": expected_sha256,
        "reform": expected_sha256,
    }
    assert artifact["dataset_sha256_after"] == {
        "baseline": expected_sha256,
        "reform": expected_sha256,
    }


@pytest.mark.parametrize(
    "run_id",
    ["campaign-20260816-obr-costings", "campaign-20260817-obr-costings"],
)
def test_only_allowlisted_legacy_artifacts_may_omit_dataset_hash_fields(
    tmp_path, synthetic_measure, run_id
):
    bundle = {"certified_data_build_id": "synthetic-certified-build"}
    artifact = compute.build_artifact(
        measure=synthetic_measure,
        year=2026,
        baseline=synthetic_run(bundle, 100.0),
        reform=synthetic_run(bundle, 125.0),
        output_path=tmp_path / "synthetic_2026.json",
        computed_at="2026-08-16T12:00:00+00:00",
        run_id=run_id,
        claims=None,
        claims_sha256=SYNTHETIC_CLAIMS_SHA256,
        registry_sha256=SYNTHETIC_REGISTRY_SHA256,
    )
    artifact.pop("dataset_sha256_before")
    artifact.pop("dataset_sha256_after")
    compute.validate_artifact_dataset_hash_fields(
        artifact,
        path=tmp_path / "synthetic_2026.json",
        allow_missing=True,
    )

    with pytest.raises(
        compute.ArtifactRestageError,
        match="legacy_artifacts_without_dataset_hashes",
    ):
        compute.validate_artifact_dataset_hash_fields(
            artifact, path=tmp_path / "synthetic_2026.json"
        )


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
        claims_sha256=SYNTHETIC_CLAIMS_SHA256,
        registry_sha256=SYNTHETIC_REGISTRY_SHA256,
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
        "source_table": synthetic_claim["source_table"],
        "reform_hint": synthetic_claim["reform_hint"],
        "conditions": synthetic_claim["conditions"],
    }
    assert row["external_claim_match"]["conditions"] == synthetic_claim["conditions"]
    assert set(row["external_claim_match"]) == {
        "source",
        "metric",
        "period",
        "source_table",
        "reform_hint",
        "conditions",
    }
    assert row["benchmark_class"] == "different_model"
    assert row["source_model"] == synthetic_claim["source_model"]
    assert row["basis"] == synthetic_claim["conditions"]["basis"]
    assert row["behavioural_adjustment"] == "unstated in harvest"
    assert row["status"] == "constructed"
    assert row["pe_value"] == -25.0
    assert row["engine_version"] == artifact["engine_version"]
    assert row["data_bundle"] == artifact["data_bundle"]
    assert row["run_id"] == artifact["run_id"]
    assert row["artifact"] == artifact["artifact"] == str(output_path.resolve())
    assert artifact["artifact"] in row["pe_construction"]
    assert any("static microsimulation" in note for note in row["annotations"])
    assert any(
        "source_model=synthetic_source_model" in note
        and "basis=nominal" in note
        and "behavioural_adjustment=unstated in harvest" in note
        for note in row["annotations"]
    )
    assert any(
        "measure Δ = −(reversal − baseline)" in note for note in row["annotations"]
    )
    assert any("calendar year 2026" in note for note in row["annotations"])
    assert any("Head mapping" in note for note in row["annotations"])

    saved = json.loads(output_path.read_text())
    assert saved["data_bundle"] == bundle["certified_data_build_id"]
    assert saved["claims_sha256"] == SYNTHETIC_CLAIMS_SHA256
    assert saved["registry_sha256"] == SYNTHETIC_REGISTRY_SHA256
    assert saved["frozen_registry"] == compute.frozen_registry_measure(
        synthetic_measure
    )
    frozen_registry = saved["frozen_registry"]
    for field in (
        "notes",
        "unmapped_obr_heads",
        "computability",
        "computability_overrides",
        "heads",
        "construction",
        "pe_reform",
    ):
        expected = (
            synthetic_measure.get(field, {})
            if field == "computability_overrides"
            else synthetic_measure[field]
        )
        assert frozen_registry[field] == expected
    expected_bundle = {
        **bundle,
        "certified_data_artifact_sha256": SYNTHETIC_DATASET_SHA256,
    }
    assert saved["policyengine_bundles"] == {
        "baseline": expected_bundle,
        "reform": expected_bundle,
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
    assert (
        saved["heads"][0]["external_claim"]["source_model"]
        == synthetic_claim["source_model"]
    )
    assert set(saved["heads"][0]["external_claim"]) == {
        "source",
        "source_table",
        "reform_hint",
        "source_model",
        "metric",
        "source_metric_field",
        "period",
        "conditions",
        "value_gbp",
        "value_raw",
        "normalization",
        "unit",
        "time_basis",
        "publication",
        "source_column",
        "status",
        "calibration_relationship",
        "claims_slice_sha256",
        "claim_ordinal",
    }
    assert saved["heads"][0]["external_claim"]["claim_ordinal"] == 0
    assert (
        saved["heads"][0]["external_claim"]["claims_slice_sha256"]
        == SYNTHETIC_CLAIMS_SHA256
    )
    assert saved["heads"][0]["raw_reform_minus_baseline_gbp"] == 25.0
    assert saved["heads"][0]["reversal_delta_exchequer_gain"] == 25.0
    assert saved["heads"][0]["pe_value"] == -25.0


def test_committed_smoke_rows_trace_to_certified_artifacts():
    rows = [json.loads(line) for line in SMOKE_STAGED.read_text().splitlines()]
    manifest = json.loads(SMOKE_MANIFEST.read_text())

    assert len(rows) == manifest["staged_rows"] == 20
    assert manifest["staged"] is True
    assert manifest["run_id"] == "campaign-20260816-obr-costings"
    assert manifest["claims"] == (
        "sources/harvest-20260802/uk_obr/obr_costings_claims.jsonl"
    )
    assert manifest["claims_sha256"] == compute.sha256_file(VENDORED_CLAIMS)
    assert len(manifest["artifacts"]) == 13
    assert manifest["legacy_artifacts_without_dataset_hashes"] == manifest["artifacts"]
    assert all(row["status"] == "constructed" for row in rows)

    traced_artifacts = set()
    for row in rows:
        assert STAGED_REQUIRED_FIELDS <= set(row)
        assert set(row["external_claim_match"]) == {
            "source",
            "metric",
            "period",
            "source_table",
            "reform_hint",
            "conditions",
        }
        assert row["benchmark_class"] == "different_model"

        artifact_path = ROOT / row["artifact"]
        artifact = json.loads(artifact_path.read_text())
        traced_artifacts.add(row["artifact"])

        assert "dataset_sha256_before" not in artifact
        assert "dataset_sha256_after" not in artifact
        compute.validate_artifact_dataset_hash_fields(
            artifact,
            path=artifact_path,
            allow_missing=True,
        )

        assert artifact["artifact"] == row["artifact"]
        assert artifact["claims_sha256"] == manifest["claims_sha256"]
        assert artifact["data_bundle"] == row["data_bundle"]
        assert artifact["engine_version"] == row["engine_version"]
        assert artifact["run_id"] == row["run_id"]
        assert artifact["measure_key"] == row["measure_key"]
        assert artifact["year"] == row["external_claim_match"]["period"]
        assert artifact["diagnostic_only"] is False

        matching_heads = []
        for head in artifact["heads"]:
            claim = head["external_claim"]
            descriptor = {
                "source": claim["source"],
                "metric": claim["metric"],
                "period": claim["period"],
                "source_table": claim["source_table"],
                "reform_hint": claim["reform_hint"],
                "conditions": claim["conditions"],
            }
            if descriptor == row["external_claim_match"]:
                matching_heads.append(head)

        assert len(matching_heads) == 1
        artifact_head = matching_heads[0]
        assert artifact_head["pe_variables"]
        raw_delta = compute.reform_minus_baseline(
            artifact["raw_aggregates"]["baseline_gbp"],
            artifact["raw_aggregates"]["reform_gbp"],
            artifact_head["pe_variables"],
        )
        literal_delta, measure_value = compute.orient_exchequer_effect(
            raw_delta,
            artifact_head["channel"],
            artifact["construction"],
        )
        assert artifact_head["raw_reform_minus_baseline_gbp"] == raw_delta
        assert artifact_head["reversal_delta_exchequer_gain"] == literal_delta
        assert artifact_head["pe_value"] == row["pe_value"] == measure_value
        assert measure_value == -literal_delta
        assert "forward_delta_exchequer_gain" not in artifact_head

    # Six measures across two years are staged. The thirteenth manifest
    # artifact is the separately requested PA +GBP 500 diagnostic.
    assert len(traced_artifacts) == 12
    diagnostic = json.loads(
        (
            ROOT
            / "results"
            / "uk"
            / "obr_costings"
            / "diagnostic__personal_allowance_plus_500_2026.json"
        ).read_text()
    )
    assert "dataset_sha256_before" not in diagnostic
    assert "dataset_sha256_after" not in diagnostic
    compute.validate_artifact_dataset_hash_fields(
        diagnostic,
        path=(
            ROOT
            / "results"
            / "uk"
            / "obr_costings"
            / "diagnostic__personal_allowance_plus_500_2026.json"
        ),
        allow_missing=True,
    )
    assert diagnostic["diagnostic_only"] is True
    assert diagnostic["claims_sha256"] == manifest["claims_sha256"]
    diagnostic_head = diagnostic["heads"][0]
    assert (
        diagnostic_head["forward_delta_exchequer_gain"] == (diagnostic_head["pe_value"])
    )
    assert "reversal_delta_exchequer_gain" not in diagnostic_head
    assert round(diagnostic["heads"][0]["pe_value"] / 1e9, 2) == -4.48
    assert round(
        diagnostic["raw_aggregates"]["baseline_gbp"]["income_tax"] / 1e9, 1
    ) == (421.9)


def test_committed_legacy_artifacts_use_manifest_ordinals_and_stay_byte_exact(
    monkeypatch,
):
    manifest = json.loads(SMOKE_MANIFEST.read_text())
    claims = compute.load_claims(VENDORED_CLAIMS)
    legacy_references = manifest["legacy_artifacts_without_dataset_hashes"]
    ordinal_map = manifest["legacy_claim_ordinals"]
    assert legacy_references == manifest["artifacts"]
    assert set(ordinal_map) == set(legacy_references)
    assert manifest["legacy_claim_ordinal_derivation"] == (
        compute.LEGACY_CLAIM_ORDINAL_DERIVATION
    )
    assert manifest["registry_sha256"] == compute.sha256_file(REGISTRY)
    assert manifest["claims_sha256"] == compute.sha256_file(VENDORED_CLAIMS)

    artifact_paths = []
    for reference in legacy_references:
        path = ROOT / reference
        artifact_paths.append(path)
        artifact = json.loads(path.read_text())
        assert "registry_sha256" not in artifact
        assert "frozen_registry" not in artifact
        derived_ordinals = {}
        for index, head in enumerate(artifact["heads"]):
            snapshot = head.get("external_claim")
            if not isinstance(snapshot, dict):
                continue
            assert "claims_slice_sha256" not in snapshot
            assert "claim_ordinal" not in snapshot
            derived_ordinals[str(index)] = compute.derive_legacy_claim_ordinal(
                claims,
                snapshot,
            )
        assert ordinal_map[reference] == derived_ordinals

    replay_outputs = [
        *artifact_paths,
        SMOKE_STAGED,
        SMOKE_COMPARISON,
        SMOKE_COMPARISON.with_name("COMPARISON.md"),
        SMOKE_MANIFEST,
    ]
    original_bytes = {path: path.read_bytes() for path in replay_outputs}

    def forbidden(*args, **kwargs):
        raise AssertionError("legacy restage reached a simulation entry point")

    monkeypatch.setattr(compute, "configure_offline", forbidden)
    monkeypatch.setattr(compute, "preflight_certified_dataset", forbidden)
    monkeypatch.setattr(compute, "run_managed_simulation", forbidden)
    summary = compute.restage_existing_run(
        manifest_path=SMOKE_MANIFEST,
        output_dir=SMOKE_MANIFEST.parent,
        artifact_root=ROOT,
    )
    assert summary["artifacts"] == 13
    assert summary["staged_rows"] == 20
    assert summary["comparison_rows"] == 26
    assert {path: path.read_bytes() for path in replay_outputs} == original_bytes


def _descriptor_hits(
    descriptor: dict[str, object], claims: list[dict[str, object]]
) -> list[dict[str, object]]:
    return [
        claim for claim in claims if compute.external_claim_match(claim) == descriptor
    ]


def test_every_staged_descriptor_matches_one_vendored_claim():
    staged_rows = [json.loads(line) for line in SMOKE_STAGED.read_text().splitlines()]
    vendored_claims = compute.load_claims(VENDORED_CLAIMS)

    assert len(vendored_claims) == 621
    for row in staged_rows:
        assert len(_descriptor_hits(row["external_claim_match"], vendored_claims)) == 1


def _matching_registry_measure_keys(
    claim: dict[str, object], measures: list[dict[str, object]]
) -> list[str]:
    period = claim.get("period")
    if not isinstance(period, int):
        return []
    return [
        measure["measure_key"]
        for measure in measures
        if compute._source_candidates([claim], measure, period)
    ]


def test_vendored_claims_are_complete_registry_measure_population():
    spec = compute.load_registry(REGISTRY)
    vendored_claims = compute.load_claims(VENDORED_CLAIMS)
    mapped: list[dict[str, object]] = []
    for measure in spec["measures"]:
        for head in measure["heads"]:
            for year in range(compute.YEAR_MIN, compute.YEAR_MAX + 1):
                claim = compute.resolve_claim(vendored_claims, measure, head, year)
                if claim is not None:
                    mapped.append(claim)

    assert len(mapped) == len({id(claim) for claim in mapped}) == 215
    assert all(
        len(_matching_registry_measure_keys(claim, spec["measures"])) == 1
        for claim in vendored_claims
    )
    assert Counter(claim["period"] for claim in vendored_claims) == {
        2022: 5,
        2023: 43,
        2024: 63,
        2025: 100,
        2026: 100,
        2027: 100,
        2028: 100,
        2029: 65,
        2030: 45,
    }
    assert hashlib.sha256(VENDORED_CLAIMS.read_bytes()).hexdigest() == (
        "bbb285705110779e1c5e31922e91e801279b03e7312670396612b8f817ad072f"
    )


@pytest.mark.skipif(
    not FULL_HARVEST_CLAIMS.exists(),
    reason="full ~/scorecard-harvest OBR claims file is unavailable",
)
def test_every_staged_descriptor_matches_one_full_harvest_claim():
    staged_rows = [json.loads(line) for line in SMOKE_STAGED.read_text().splitlines()]
    full_claims = compute.load_claims(FULL_HARVEST_CLAIMS)

    for row in staged_rows:
        assert len(_descriptor_hits(row["external_claim_match"], full_claims)) == 1

    full_bytes = FULL_HARVEST_CLAIMS.read_bytes()
    assert hashlib.sha256(full_bytes).hexdigest() == (
        "46117d14c4de7ac10cbc9bc09acef6c5b5060db1605e02334d4a827cf420a3bd"
    )
    full_lines = full_bytes.splitlines(keepends=True)
    for vendored_line in VENDORED_CLAIMS.read_bytes().splitlines(keepends=True):
        assert full_lines.count(vendored_line) == 1
    measures = compute.load_registry(REGISTRY)["measures"]
    expected_lines = []
    for raw_line in full_lines:
        claim = json.loads(raw_line)
        if _matching_registry_measure_keys(claim, measures):
            expected_lines.append(raw_line)
    assert b"".join(expected_lines) == VENDORED_CLAIMS.read_bytes()


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


@pytest.mark.parametrize(
    "writer",
    [compute.atomic_write_text, compare.atomic_write_text],
)
def test_atomic_writers_preserve_existing_output_mode(tmp_path, writer):
    output_path = tmp_path / "output.txt"
    output_path.write_text("before")
    output_path.chmod(0o640)

    writer(output_path, "after")

    assert output_path.read_text() == "after"
    assert output_path.stat().st_mode & 0o777 == 0o640


def test_default_measure_selection_retains_null_reforms():
    measures = compute.load_registry(REGISTRY)["measures"]
    selected = compute.select_measures(measures, requested=None, limit=None)

    assert selected == measures
    assert any(measure["pe_reform"] is None for measure in selected)


def test_pre_effective_source_rows_are_not_suppressed(
    synthetic_measure, synthetic_claim
):
    measure = copy.deepcopy(synthetic_measure)
    measure["computability"] = "not_expressible"
    measure["pe_reform"] = None
    measure["heads"] = []
    measure["unmapped_obr_heads"] = ["Income tax"]
    measure["start_fy"] = 2026
    claim = copy.deepcopy(synthetic_claim)
    claim["period"] = 2025
    claim["conditions"]["fy"] = "2025-26"

    rows = compute.stage_not_computed_rows(
        measure=measure,
        years=[2025],
        claims=[claim],
        run_id="campaign-20260816-obr-costings",
        computed_at="2026-08-16T12:00:00+00:00",
        release_bundle={"certified_data_build_id": "synthetic-certified-build"},
        engine_version="2.89.2-test",
    )

    assert len(rows) == 1
    assert rows[0]["external_claim_match"]["period"] == 2025
    assert rows[0]["status"] == "not_computed"


def test_hicbc_uses_provisional_fixed_claiming_child_benefit_mapping():
    measures = {
        measure["measure_key"]: measure
        for measure in compute.load_registry(REGISTRY)["measures"]
    }
    hicbc = measures["spring_budget_2024__hicbc_threshold_and_taper"]
    welfare_head = next(
        head for head in hicbc["heads"] if head["obr_head"] == "Welfare inside cap"
    )

    assert welfare_head["pe_variables"] == ["child_benefit"]
    assert welfare_head["channel"] == "spending"
    assert "PROVISIONAL PE head mapping" in hicbc["notes"]
    assert "identifies neither the programme nor a mechanism" in hicbc["notes"]
    assert "would_claim_child_benefit is fixed" in hicbc["notes"]
    assert "child_benefit delta is zero" in hicbc["notes"]
    assert "reform-induced claiming" not in hicbc["notes"]


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
            claims_sha256=SYNTHETIC_CLAIMS_SHA256,
            registry_sha256=SYNTHETIC_REGISTRY_SHA256,
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


def test_default_dry_run_uses_complete_vendored_slice(tmp_path):
    if importlib.util.find_spec("policyengine_uk") is None:
        pytest.skip("policyengine-uk is not installed")

    output_dir = tmp_path / "artifacts"
    staged_path = tmp_path / "staged.jsonl"
    completed = subprocess.run(
        [
            sys.executable,
            str(compute.__file__),
            "--output-dir",
            str(output_dir),
            "--staged-output",
            str(staged_path),
            "--dry-run",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    payload, end = json.JSONDecoder().raw_decode(completed.stdout)
    assert completed.stdout[end:].strip() == (
        "dry-run complete: no managed microsimulation constructed"
    )
    assert payload["validation"]["measures"] == 26
    assert payload["validation"]["source_head_years"] == 215
    assert len(payload["selected_measures"]) == 26
    assert compute.DEFAULT_CLAIMS == compare.DEFAULT_CLAIMS == VENDORED_CLAIMS
    assert not output_dir.exists()
    assert not staged_path.exists()


def test_restage_rejects_claims_path_that_escapes_artifact_root(tmp_path):
    artifact_root = tmp_path / "run"
    outside_dir = tmp_path / "outside"
    outside_dir.mkdir()
    escaped_claims = outside_dir / "claims.jsonl"
    escaped_claims.write_text("{}\n")
    manifest_path = artifact_root / "RUN_MANIFEST.json"
    compute.write_json(
        manifest_path,
        {
            "schema_version": 1,
            "staged": True,
            "run_id": "campaign-20260817-obr-costings",
            "registry": "registry.yaml",
            "claims": "../outside/claims.jsonl",
            "claims_sha256": compute.sha256_file(escaped_claims),
            "artifacts": [],
            "legacy_artifacts_without_dataset_hashes": [],
            "staged_output": "staged.jsonl",
        },
    )

    with pytest.raises(
        compute.ArtifactRestageError,
        match="escapes artifact root",
    ) as exc_info:
        compute.restage_existing_run(
            manifest_path=manifest_path,
            output_dir=artifact_root,
            artifact_root=artifact_root,
        )
    message = str(exc_info.value)
    assert "../outside/claims.jsonl" in message
    assert str(artifact_root.resolve()) in message
    assert escaped_claims.exists()


@pytest.mark.parametrize(
    ("aliased_role", "staged_reference", "artifacts"),
    [
        ("claims", "claims.jsonl", []),
        ("claims", "CLAIMS.JSONL", []),
        ("registry", "registry.yaml", []),
        ("manifest", "RUN_MANIFEST.json", []),
        ("artifacts[0]", "artifact.json", ["artifact.json"]),
        ("artifact directory", ".", []),
        ("comparison CSV", "comparison/comparison.csv", []),
        ("comparison Markdown", "comparison/comparison.md", []),
    ],
)
def test_restage_rejects_staged_output_path_aliases_before_input_parse(
    tmp_path,
    aliased_role,
    staged_reference,
    artifacts,
):
    artifact_root = tmp_path / "run"
    manifest_path = artifact_root / "RUN_MANIFEST.json"
    compute.write_json(
        manifest_path,
        {
            "schema_version": 1,
            "staged": True,
            "run_id": "campaign-20260817-obr-costings",
            "registry": "registry.yaml",
            "claims": "claims.jsonl",
            "artifacts": artifacts,
            "legacy_artifacts_without_dataset_hashes": [],
            "staged_output": staged_reference,
        },
    )
    original_manifest = manifest_path.read_bytes()

    with pytest.raises(compute.ArtifactRestageError) as exc_info:
        compute.restage_existing_run(
            manifest_path=manifest_path,
            output_dir=artifact_root / "comparison",
            artifact_root=artifact_root,
        )
    message = str(exc_info.value)
    assert "path collision" in message
    assert "staged_output" in message
    assert aliased_role in message
    assert manifest_path.read_bytes() == original_manifest


def test_restage_rejects_existing_hardlink_alias_before_input_parse(tmp_path):
    artifact_root = tmp_path / "run"
    artifact_root.mkdir()
    claims_path = artifact_root / "claims.jsonl"
    claims_path.write_text("not parsed\n")
    staged_path = artifact_root / "staged.jsonl"
    os.link(claims_path, staged_path)
    manifest_path = artifact_root / "RUN_MANIFEST.json"
    compute.write_json(
        manifest_path,
        {
            "schema_version": 1,
            "staged": True,
            "run_id": "campaign-20260817-obr-costings",
            "registry": "registry.yaml",
            "claims": "claims.jsonl",
            "artifacts": [],
            "legacy_artifacts_without_dataset_hashes": [],
            "staged_output": "staged.jsonl",
        },
    )

    with pytest.raises(compute.ArtifactRestageError) as exc_info:
        compute.restage_existing_run(
            manifest_path=manifest_path,
            output_dir=artifact_root / "comparison",
            artifact_root=artifact_root,
        )
    message = str(exc_info.value)
    assert "path collision" in message
    assert "claims" in message
    assert "staged_output" in message
    assert "identify the same file" in message


@pytest.mark.parametrize(
    "role",
    [
        "registry",
        "claims",
        "artifacts[0]",
        "legacy_artifacts_without_dataset_hashes[0]",
        "staged_output",
    ],
)
def test_restage_rejects_absolute_recorded_paths_for_every_role(tmp_path, role):
    artifact_root = tmp_path / "run"
    manifest_path = artifact_root / "RUN_MANIFEST.json"
    manifest = {
        "schema_version": 1,
        "staged": True,
        "run_id": "campaign-20260817-obr-costings",
        "registry": "registry.yaml",
        "claims": "claims.jsonl",
        "artifacts": [],
        "legacy_artifacts_without_dataset_hashes": [],
        "staged_output": "staged.jsonl",
    }
    if role == "registry":
        manifest["registry"] = str(artifact_root / "registry.yaml")
    elif role == "claims":
        manifest["claims"] = str(artifact_root / "claims.jsonl")
    elif role == "artifacts[0]":
        manifest["artifacts"] = [str(artifact_root / "artifact.json")]
    elif role == "legacy_artifacts_without_dataset_hashes[0]":
        manifest["artifacts"] = ["artifact.json"]
        manifest["legacy_artifacts_without_dataset_hashes"] = [
            str(artifact_root / "artifact.json")
        ]
    elif role == "staged_output":
        manifest["staged_output"] = str(artifact_root / "staged.jsonl")
    else:
        raise AssertionError(f"unhandled role {role}")
    compute.write_json(manifest_path, manifest)

    with pytest.raises(compute.ArtifactRestageError) as exc_info:
        compute.restage_existing_run(
            manifest_path=manifest_path,
            output_dir=artifact_root / "comparison",
            artifact_root=artifact_root,
        )
    message = str(exc_info.value)
    assert role in message
    assert "must be repo-relative" in message


def test_restage_rejects_no_stage_manifest_before_path_resolution(tmp_path):
    artifact_root = tmp_path / "run"
    manifest_path = artifact_root / "RUN_MANIFEST.json"
    compute.write_json(
        manifest_path,
        {
            "schema_version": 1,
            "staged": False,
        },
    )
    original_manifest = manifest_path.read_bytes()

    with pytest.raises(
        compute.ArtifactRestageError,
        match="non-replayable: run recorded with --no-stage",
    ):
        compute.restage_existing_run(
            manifest_path=manifest_path,
            output_dir=artifact_root,
            artifact_root=artifact_root,
        )
    assert manifest_path.read_bytes() == original_manifest


def test_no_stage_producer_records_explicit_non_replayable_manifest(
    tmp_path,
    monkeypatch,
    synthetic_measure,
    synthetic_claim,
):
    null_measure = copy.deepcopy(synthetic_measure)
    null_measure["computability"] = "not_expressible"
    null_measure["pe_reform"] = None
    registry_path = tmp_path / "registry.yaml"
    claims_path = tmp_path / "claims.jsonl"
    output_dir = tmp_path / "artifacts"
    staged_path = tmp_path / "staged.jsonl"
    registry_path.write_text(
        yaml.safe_dump(
            {
                "schema_version": 1,
                "benchmark_class": "different_model",
                "measures": [null_measure],
            },
            sort_keys=False,
        )
    )
    claims_path.write_text(json.dumps(synthetic_claim, allow_nan=False) + "\n")

    def relative_to_test_root(path, *, role):
        return str(Path(path).resolve().relative_to(tmp_path.resolve()))

    def forbidden_simulation(*args, **kwargs):
        raise AssertionError("--no-stage producer constructed a simulation")

    monkeypatch.setattr(
        compute,
        "recorded_repo_relative_path",
        relative_to_test_root,
    )
    monkeypatch.setattr(compute, "run_managed_simulation", forbidden_simulation)
    monkeypatch.setattr(
        compute,
        "preflight_certified_dataset",
        lambda: {
            "release_bundle": {
                "certified_data_build_id": "synthetic-certified-build",
                "certified_data_artifact_sha256": SYNTHETIC_DATASET_SHA256,
            },
            "runtime_dataset_source": str(tmp_path / "unused-dataset.h5"),
            "hash_seconds": 0.0,
        },
    )

    assert (
        compute.main(
            [
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
                "--no-stage",
            ]
        )
        == 0
    )
    manifest = json.loads((output_dir / "RUN_MANIFEST.json").read_text())
    assert manifest["staged"] is False
    assert manifest["registry_sha256"] == compute.sha256_file(registry_path)
    assert manifest["artifactless_frozen_registry"] == {
        null_measure["measure_key"]: compute.frozen_registry_measure(null_measure)
    }
    assert "staged_output" not in manifest
    assert "staged_rows" not in manifest
    assert not staged_path.exists()
    with pytest.raises(
        compute.ArtifactRestageError,
        match="non-replayable: run recorded with --no-stage",
    ):
        compute.restage_existing_run(
            manifest_path=output_dir / "RUN_MANIFEST.json",
            output_dir=output_dir,
            artifact_root=tmp_path,
        )


def _write_synthetic_replay(
    tmp_path,
    synthetic_measure,
    synthetic_claim,
):
    registry_path = tmp_path / "registry.yaml"
    claims_path = tmp_path / "claims.jsonl"
    output_dir = tmp_path / "artifacts"
    staged_path = tmp_path / "staged.jsonl"
    manifest_path = output_dir / "RUN_MANIFEST.json"
    artifact_path = output_dir / "synthetic_2026.json"
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
    claims_sha256 = compute.sha256_file(claims_path)
    registry_sha256 = compute.sha256_file(registry_path)
    bundle = {"certified_data_build_id": "synthetic-certified-build"}
    artifact = compute.build_artifact(
        measure=synthetic_measure,
        year=2026,
        baseline=synthetic_run(bundle, 100.0),
        reform=synthetic_run(bundle, 125.0),
        output_path=artifact_path,
        computed_at="2026-08-17T12:00:00+00:00",
        run_id="campaign-20260817-obr-costings",
        claims=[synthetic_claim],
        claims_sha256=claims_sha256,
        registry_sha256=registry_sha256,
    )
    artifact_reference = "artifacts/synthetic_2026.json"
    artifact["artifact"] = artifact_reference
    artifact["diagnostic_only"] = False
    compute.write_json(artifact_path, artifact)
    staged_rows = compute.stage_artifact_rows(artifact, synthetic_measure)
    compute.write_jsonl(staged_path, staged_rows)
    compare.write_comparison_outputs_from_rows(
        staged_rows=staged_rows,
        claims=[synthetic_claim],
        registry={synthetic_measure["measure_key"]: synthetic_measure},
        output_dir=output_dir,
        artifact_root=tmp_path,
    )
    manifest = {
        "schema_version": 1,
        "staged": True,
        "run_id": artifact["run_id"],
        "started_at": "2026-08-17T12:00:00+00:00",
        "engine_version": artifact["engine_version"],
        "registry": "registry.yaml",
        "registry_sha256": registry_sha256,
        "claims": "claims.jsonl",
        "claims_sha256": claims_sha256,
        "artifacts": [artifact_reference],
        "legacy_artifacts_without_dataset_hashes": [],
        "artifactless_frozen_registry": {},
        "selected_measures": [synthetic_measure["measure_key"]],
        "years": [2026],
        "pa_smoke_probe": False,
        "certified_cache_preflight": {
            "release_bundle": artifact["policyengine_bundles"]["baseline"]
        },
        "staged_output": "staged.jsonl",
        "staged_rows": 1,
    }
    compute.write_json(manifest_path, manifest)
    output_paths = (
        artifact_path,
        staged_path,
        output_dir / "COMPARISON.csv",
        output_dir / "COMPARISON.md",
        manifest_path,
    )
    return {
        "artifact_path": artifact_path,
        "artifact_root": tmp_path,
        "claims_path": claims_path,
        "manifest": manifest,
        "manifest_path": manifest_path,
        "output_dir": output_dir,
        "output_paths": output_paths,
        "registry_path": registry_path,
        "registry_sha256": registry_sha256,
    }


def test_restage_rederives_existing_artifacts_without_any_simulation(
    tmp_path, monkeypatch, synthetic_measure, synthetic_claim
):
    registry_path = tmp_path / "registry.yaml"
    claims_path = tmp_path / "claims.jsonl"
    output_dir = tmp_path / "artifacts"
    staged_path = tmp_path / "staged.jsonl"
    manifest_path = output_dir / "RUN_MANIFEST.json"
    artifact_path = output_dir / "synthetic_2026.json"
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
    claims_sha256 = compute.sha256_file(claims_path)
    registry_sha256 = compute.sha256_file(registry_path)
    bundle = {"certified_data_build_id": "synthetic-certified-build"}
    artifact = compute.build_artifact(
        measure=synthetic_measure,
        year=2026,
        baseline=synthetic_run(bundle, 100.0),
        reform=synthetic_run(bundle, 125.0),
        output_path=artifact_path,
        computed_at="2026-08-16T12:00:00+00:00",
        run_id="campaign-20260816-obr-costings",
        claims=[synthetic_claim],
        claims_sha256=claims_sha256,
        registry_sha256=registry_sha256,
    )
    artifact["diagnostic_only"] = False
    artifact_reference = "artifacts/synthetic_2026.json"
    artifact["artifact"] = artifact_reference
    artifact.pop("dataset_sha256_before")
    artifact.pop("dataset_sha256_after")
    artifact.pop("registry_sha256")
    artifact.pop("frozen_registry")
    artifact["heads"][0]["external_claim"].pop("claims_slice_sha256")
    artifact["heads"][0]["external_claim"].pop("claim_ordinal")
    artifact["heads"][0].pop("reversal_delta_exchequer_gain")
    artifact["heads"][0]["pe_value"] = 25.0
    compute.write_json(artifact_path, artifact)
    manifest = {
        "schema_version": 1,
        "staged": True,
        "run_id": artifact["run_id"],
        "started_at": "2026-08-16T12:00:00+00:00",
        "engine_version": artifact["engine_version"],
        "registry": "registry.yaml",
        "registry_sha256": registry_sha256,
        "claims": "claims.jsonl",
        "claims_sha256": claims_sha256,
        "artifacts": [artifact_reference],
        "legacy_artifacts_without_dataset_hashes": [artifact_reference],
        "legacy_claim_ordinal_derivation": (compute.LEGACY_CLAIM_ORDINAL_DERIVATION),
        "legacy_claim_ordinals": {artifact_reference: {"0": 0}},
        "artifactless_frozen_registry": {},
        "selected_measures": [synthetic_measure["measure_key"]],
        "years": [2026],
        "pa_smoke_probe": False,
        "certified_cache_preflight": {
            "release_bundle": artifact["policyengine_bundles"]["baseline"]
        },
        "staged_output": "staged.jsonl",
        "staged_rows": 1,
    }
    compute.write_json(manifest_path, manifest)
    original_manifest = manifest_path.read_bytes()
    original_raw = copy.deepcopy(artifact["raw_aggregates"])
    original_claim = copy.deepcopy(artifact["heads"][0]["external_claim"])

    def forbidden(*args, **kwargs):
        raise AssertionError("restage reached simulation or certified-cache setup")

    monkeypatch.setattr(compute, "configure_offline", forbidden)
    monkeypatch.setattr(compute, "preflight_certified_dataset", forbidden)
    monkeypatch.setattr(compute, "run_managed_simulation", forbidden)

    arguments = [
        "--restage",
        "--manifest",
        str(manifest_path),
        "--output-dir",
        str(output_dir),
        "--artifact-root",
        str(tmp_path),
    ]
    assert compute.main(arguments) == 0

    refreshed = json.loads(artifact_path.read_text())
    assert "dataset_sha256_before" not in refreshed
    assert "dataset_sha256_after" not in refreshed
    assert refreshed["raw_aggregates"] == original_raw
    assert refreshed["computed_at"] == artifact["computed_at"]
    assert refreshed["heads"][0]["external_claim"] == original_claim
    assert refreshed["heads"][0]["raw_reform_minus_baseline_gbp"] == 25.0
    assert refreshed["heads"][0]["reversal_delta_exchequer_gain"] == 25.0
    assert refreshed["heads"][0]["pe_value"] == -25.0
    staged = [json.loads(line) for line in staged_path.read_text().splitlines()]
    assert len(staged) == 1
    assert staged[0]["pe_value"] == -25.0
    with (output_dir / "COMPARISON.csv").open(newline="") as source:
        comparison_rows = list(csv.DictReader(source))
    assert len(comparison_rows) == 1
    assert float(comparison_rows[0]["pe_value_gbp"]) == -25.0
    assert comparison_rows[0]["ratio_bin"] == "same_sign_ratio_0.5_to_0.8"
    markdown = (output_dir / "COMPARISON.md").read_text()
    assert "announced-measure orientation" in markdown
    assert "reversals are not re-oriented" not in markdown
    assert manifest_path.read_bytes() == original_manifest

    first_outputs = {
        path: path.read_bytes()
        for path in (
            artifact_path,
            staged_path,
            output_dir / "COMPARISON.csv",
            output_dir / "COMPARISON.md",
            manifest_path,
        )
    }
    assert compute.main(arguments) == 0
    assert {path: path.read_bytes() for path in first_outputs} == first_outputs

    claims_path.write_text(claims_path.read_text() + "\n")
    drifted_sha256 = compute.sha256_file(claims_path)
    with pytest.raises(
        compute.ArtifactRestageError,
        match="claims SHA-256 differs from RUN_MANIFEST",
    ) as exc_info:
        compute.main(arguments)
    message = str(exc_info.value)
    assert f"expected {claims_sha256}" in message
    assert f"actual {drifted_sha256}" in message
    assert "new run" in message
    assert "re-run" in message
    assert {path: path.read_bytes() for path in first_outputs} == first_outputs

    claims_path.write_text(json.dumps(synthetic_claim, allow_nan=False) + "\n")
    mismatched_claims_sha256 = "c" * 64
    mismatched_artifact = json.loads(artifact_path.read_text())
    mismatched_artifact["claims_sha256"] = mismatched_claims_sha256
    compute.write_json(artifact_path, mismatched_artifact)
    mismatch_outputs = {
        path: path.read_bytes()
        for path in (
            artifact_path,
            staged_path,
            output_dir / "COMPARISON.csv",
            output_dir / "COMPARISON.md",
            manifest_path,
        )
    }
    with pytest.raises(
        compute.ArtifactRestageError,
        match="artifact claims_sha256 differs from RUN_MANIFEST",
    ) as exc_info:
        compute.main(arguments)
    message = str(exc_info.value)
    assert f"expected {claims_sha256}" in message
    assert f"actual {mismatched_claims_sha256}" in message
    assert "new run" in message
    assert "re-run" in message
    assert {path: path.read_bytes() for path in mismatch_outputs} == mismatch_outputs
    artifact_path.write_bytes(first_outputs[artifact_path])

    manifest["legacy_artifacts_without_dataset_hashes"] = []
    manifest["legacy_claim_ordinals"] = {}
    manifest.pop("legacy_claim_ordinal_derivation")
    compute.write_json(manifest_path, manifest)
    with pytest.raises(
        compute.ArtifactRestageError,
        match="artifact registry_sha256 differs from RUN_MANIFEST",
    ):
        compute.main(arguments)


@pytest.mark.parametrize("registry_mutation", ["notes", "unmapped_obr_heads"])
def test_restage_rejects_registry_drift_at_sha_gate_before_parse_or_output(
    tmp_path,
    monkeypatch,
    synthetic_measure,
    synthetic_claim,
    registry_mutation,
):
    replay = _write_synthetic_replay(
        tmp_path,
        synthetic_measure,
        synthetic_claim,
    )
    original_outputs = {path: path.read_bytes() for path in replay["output_paths"]}
    registry = yaml.safe_load(replay["registry_path"].read_text())
    measure = registry["measures"][0]
    if registry_mutation == "notes":
        measure["notes"] = "mutated registry note"
    else:
        measure["unmapped_obr_heads"].append("Fabricated unmapped head")
    replay["registry_path"].write_text(yaml.safe_dump(registry, sort_keys=False))
    actual_sha256 = compute.sha256_file(replay["registry_path"])

    def forbidden_parse(*args, **kwargs):
        raise AssertionError("registry SHA gate was bypassed before parsing")

    monkeypatch.setattr(compute, "parse_registry_payload", forbidden_parse)
    with pytest.raises(
        compute.ArtifactRestageError,
        match="registry SHA-256 differs from RUN_MANIFEST",
    ) as exc_info:
        compute.restage_existing_run(
            manifest_path=replay["manifest_path"],
            output_dir=replay["output_dir"],
            artifact_root=replay["artifact_root"],
        )
    message = str(exc_info.value)
    assert f"expected {replay['registry_sha256']}" in message
    assert f"actual {actual_sha256}" in message
    assert "new run" in message
    assert "re-run" in message
    assert {
        path: path.read_bytes() for path in replay["output_paths"]
    } == original_outputs


def test_restage_rechecks_registry_sha_immediately_before_writes(
    tmp_path,
    monkeypatch,
    synthetic_measure,
    synthetic_claim,
):
    replay = _write_synthetic_replay(
        tmp_path,
        synthetic_measure,
        synthetic_claim,
    )
    original_outputs = {path: path.read_bytes() for path in replay["output_paths"]}
    original_rederive = compute.rederive_artifact_orientation
    mutated = False

    def mutate_registry_during_replay(*args, **kwargs):
        nonlocal mutated
        artifact = original_rederive(*args, **kwargs)
        if not mutated:
            registry = yaml.safe_load(replay["registry_path"].read_text())
            registry["measures"][0]["notes"] = "TOCTOU registry mutation"
            replay["registry_path"].write_text(
                yaml.safe_dump(registry, sort_keys=False)
            )
            mutated = True
        return artifact

    monkeypatch.setattr(
        compute,
        "rederive_artifact_orientation",
        mutate_registry_during_replay,
    )
    with pytest.raises(
        compute.ArtifactRestageError,
        match="registry SHA-256 differs from RUN_MANIFEST",
    ) as exc_info:
        compute.restage_existing_run(
            manifest_path=replay["manifest_path"],
            output_dir=replay["output_dir"],
            artifact_root=replay["artifact_root"],
        )
    actual_sha256 = compute.sha256_file(replay["registry_path"])
    message = str(exc_info.value)
    assert mutated
    assert f"expected {replay['registry_sha256']}" in message
    assert f"actual {actual_sha256}" in message
    assert "re-run" in message
    assert {
        path: path.read_bytes() for path in replay["output_paths"]
    } == original_outputs


@pytest.mark.parametrize(
    ("missing_field", "message_fragment"),
    [
        ("registry_sha256", "artifact registry_sha256 differs"),
        ("frozen_registry", "frozen_registry must be a mapping"),
    ],
)
def test_nonlegacy_artifact_must_carry_frozen_registry_replay_fields(
    tmp_path,
    synthetic_measure,
    synthetic_claim,
    missing_field,
    message_fragment,
):
    replay = _write_synthetic_replay(
        tmp_path,
        synthetic_measure,
        synthetic_claim,
    )
    artifact = json.loads(replay["artifact_path"].read_text())
    artifact.pop(missing_field)
    compute.write_json(replay["artifact_path"], artifact)
    original_outputs = {path: path.read_bytes() for path in replay["output_paths"]}

    with pytest.raises(
        compute.ArtifactRestageError,
        match=message_fragment,
    ):
        compute.restage_existing_run(
            manifest_path=replay["manifest_path"],
            output_dir=replay["output_dir"],
            artifact_root=replay["artifact_root"],
        )
    assert {
        path: path.read_bytes() for path in replay["output_paths"]
    } == original_outputs


def _mutate_frozen_claim_field(claim, claim_field):
    if claim_field == "source_metric_field":
        claim["proposed_metric"] = claim.pop("metric")
        return
    keys = claim_field.split(".")
    container = claim
    for key in keys[:-1]:
        container = container[key]
    original = container[keys[-1]]
    if isinstance(original, (int, float)) and not isinstance(original, bool):
        container[keys[-1]] = original + 1
    else:
        container[keys[-1]] = f"changed {original}"


def _nested_value(value, field):
    for key in field.split("."):
        value = value[key]
    return value


@pytest.mark.parametrize(
    ("claim_field", "reported_field"),
    [
        ("source", "source"),
        ("source_table", "source_table"),
        ("reform_hint", "reform_hint"),
        ("source_model", "source_model"),
        ("metric", "metric"),
        ("source_metric_field", "source_metric_field"),
        ("period", "period"),
        ("value", "value_gbp"),
        ("value_raw", "value_raw"),
        ("normalization", "normalization"),
        ("proposed_unit", "unit"),
        ("time_basis", "time_basis"),
        ("source_column", "source_column"),
        ("status", "status"),
        ("calibration_relationship", "calibration_relationship"),
        ("conditions.basis", "conditions.basis"),
        ("conditions.costing_phase", "conditions.costing_phase"),
        ("conditions.fiscal_event", "conditions.fiscal_event"),
        ("conditions.fy", "conditions.fy"),
        ("conditions.geography", "conditions.geography"),
        ("conditions.impact_channel", "conditions.impact_channel"),
        ("conditions.line_item", "conditions.line_item"),
        ("conditions.note", "conditions.note"),
        ("conditions.sign_convention", "conditions.sign_convention"),
        ("conditions.spending_head", "conditions.spending_head"),
        ("conditions.tax_head", "conditions.tax_head"),
        ("publication.publication_url", "publication.publication_url"),
        ("publication.publisher", "publication.publisher"),
        ("publication.sign_convention", "publication.sign_convention"),
        ("publication.title", "publication.title"),
        ("publication.units_note", "publication.units_note"),
        ("publication.url", "publication.url"),
        ("publication.vintage", "publication.vintage"),
        ("publication.wayback", "publication.wayback"),
        ("publication.workbook", "publication.workbook"),
    ],
)
def test_rederive_rejects_every_frozen_claim_field_drift(
    tmp_path,
    synthetic_measure,
    synthetic_claim,
    claim_field,
    reported_field,
):
    bundle = {"certified_data_build_id": "synthetic-certified-build"}
    artifact = compute.build_artifact(
        measure=synthetic_measure,
        year=2026,
        baseline=synthetic_run(bundle, 100.0),
        reform=synthetic_run(bundle, 125.0),
        output_path=tmp_path / "artifact.json",
        computed_at="2026-08-17T12:00:00+00:00",
        run_id="campaign-20260817-obr-costings",
        claims=[synthetic_claim],
        claims_sha256=SYNTHETIC_CLAIMS_SHA256,
        registry_sha256=SYNTHETIC_REGISTRY_SHA256,
    )
    frozen_snapshot = artifact["heads"][0]["external_claim"]
    current_claim = copy.deepcopy(synthetic_claim)
    _mutate_frozen_claim_field(current_claim, claim_field)
    current_snapshot = compute.source_claim_snapshot(
        current_claim,
        claims_slice_sha256=SYNTHETIC_CLAIMS_SHA256,
        claim_ordinal=0,
    )
    frozen_value = _nested_value(frozen_snapshot, reported_field)
    current_value = _nested_value(current_snapshot, reported_field)

    with pytest.raises(compute.ArtifactRestageError) as exc_info:
        compute.rederive_artifact_orientation(
            artifact,
            synthetic_measure,
            path=tmp_path / "artifact.json",
            claims=[current_claim],
            expected_claims_sha256=SYNTHETIC_CLAIMS_SHA256,
            expected_registry_sha256=SYNTHETIC_REGISTRY_SHA256,
        )
    message = str(exc_info.value)
    assert "frozen/claims fields differ" in message
    assert (
        f"field={reported_field} frozen={frozen_value!r} current={current_value!r}"
    ) in message


def test_rederive_rejects_out_of_range_frozen_claim_ordinal(
    tmp_path, synthetic_measure, synthetic_claim
):
    bundle = {"certified_data_build_id": "synthetic-certified-build"}
    artifact = compute.build_artifact(
        measure=synthetic_measure,
        year=2026,
        baseline=synthetic_run(bundle, 100.0),
        reform=synthetic_run(bundle, 125.0),
        output_path=tmp_path / "artifact.json",
        computed_at="2026-08-17T12:00:00+00:00",
        run_id="campaign-20260817-obr-costings",
        claims=[synthetic_claim],
        claims_sha256=SYNTHETIC_CLAIMS_SHA256,
        registry_sha256=SYNTHETIC_REGISTRY_SHA256,
    )
    artifact["heads"][0]["external_claim"]["claim_ordinal"] = 2

    with pytest.raises(
        compute.ArtifactRestageError,
        match="claim_ordinal 2 is out of range for 1 claims rows",
    ) as exc_info:
        compute.rederive_artifact_orientation(
            artifact,
            synthetic_measure,
            path=tmp_path / "artifact.json",
            claims=[synthetic_claim],
            expected_claims_sha256=SYNTHETIC_CLAIMS_SHA256,
            expected_registry_sha256=SYNTHETIC_REGISTRY_SHA256,
        )
    message = str(exc_info.value)
    assert "claim_ordinal 2" in message
    assert "1 claims rows" in message


@pytest.mark.parametrize(
    ("identity_mutation", "message_fragment"),
    [
        ("missing_slice_sha", "claims_slice_sha256 differs"),
        ("boolean_ordinal", "claim_ordinal must be an integer"),
    ],
)
def test_nonlegacy_frozen_claim_requires_slice_hash_and_integer_ordinal(
    tmp_path,
    synthetic_measure,
    synthetic_claim,
    identity_mutation,
    message_fragment,
):
    bundle = {"certified_data_build_id": "synthetic-certified-build"}
    artifact = compute.build_artifact(
        measure=synthetic_measure,
        year=2026,
        baseline=synthetic_run(bundle, 100.0),
        reform=synthetic_run(bundle, 125.0),
        output_path=tmp_path / "artifact.json",
        computed_at="2026-08-17T12:00:00+00:00",
        run_id="campaign-20260817-obr-costings",
        claims=[synthetic_claim],
        claims_sha256=SYNTHETIC_CLAIMS_SHA256,
        registry_sha256=SYNTHETIC_REGISTRY_SHA256,
    )
    snapshot = artifact["heads"][0]["external_claim"]
    if identity_mutation == "missing_slice_sha":
        snapshot.pop("claims_slice_sha256")
    else:
        snapshot["claim_ordinal"] = True

    with pytest.raises(
        compute.ArtifactRestageError,
        match=message_fragment,
    ):
        compute.rederive_artifact_orientation(
            artifact,
            synthetic_measure,
            path=tmp_path / "artifact.json",
            claims=[synthetic_claim],
            expected_claims_sha256=SYNTHETIC_CLAIMS_SHA256,
            expected_registry_sha256=SYNTHETIC_REGISTRY_SHA256,
        )


def test_wrong_in_range_claim_ordinal_reports_descriptor_values(
    tmp_path,
    synthetic_measure,
    synthetic_claim,
):
    bundle = {"certified_data_build_id": "synthetic-certified-build"}
    artifact = compute.build_artifact(
        measure=synthetic_measure,
        year=2026,
        baseline=synthetic_run(bundle, 100.0),
        reform=synthetic_run(bundle, 125.0),
        output_path=tmp_path / "artifact.json",
        computed_at="2026-08-17T12:00:00+00:00",
        run_id="campaign-20260817-obr-costings",
        claims=[synthetic_claim],
        claims_sha256=SYNTHETIC_CLAIMS_SHA256,
        registry_sha256=SYNTHETIC_REGISTRY_SHA256,
    )
    artifact["heads"][0]["external_claim"]["claim_ordinal"] = 1
    wrong_claim = copy.deepcopy(synthetic_claim)
    wrong_claim["conditions"]["tax_head"] = "Corporation tax"

    with pytest.raises(compute.ArtifactRestageError) as exc_info:
        compute.rederive_artifact_orientation(
            artifact,
            synthetic_measure,
            path=tmp_path / "artifact.json",
            claims=[synthetic_claim, wrong_claim],
            expected_claims_sha256=SYNTHETIC_CLAIMS_SHA256,
            expected_registry_sha256=SYNTHETIC_REGISTRY_SHA256,
        )
    assert (
        "field=conditions.tax_head frozen='Income tax' current='Corporation tax'"
    ) in str(exc_info.value)


def test_full_selection_restage_reconstructs_five_null_reforms(tmp_path, monkeypatch):
    registry_path = tmp_path / "registry.yaml"
    registry_path.write_bytes(REGISTRY.read_bytes())
    spec = compute.load_registry(registry_path)
    measures = spec["measures"]
    claims_path = tmp_path / "claims.jsonl"
    claims_path.write_bytes(VENDORED_CLAIMS.read_bytes())
    claims, claims_sha256 = compute.load_claims_with_sha256(claims_path)
    registry_sha256 = compute.sha256_file(registry_path)
    artifacts_dir = tmp_path / "artifacts"
    staged_path = tmp_path / "staged.jsonl"
    output_dir = tmp_path / "comparison"
    manifest_path = tmp_path / "RUN_MANIFEST.json"
    started_at = "2026-08-17T12:00:00+00:00"
    engine_version = compute.package_version("policyengine-uk")
    bundle = {
        "certified_data_build_id": "synthetic-certified-build",
        "certified_data_artifact_sha256": SYNTHETIC_DATASET_SHA256,
    }

    expected_rows = []
    for measure in measures:
        if measure["pe_reform"] is None:
            expected_rows.extend(
                compute.stage_not_computed_rows(
                    measure=measure,
                    years=[2026],
                    claims=claims,
                    run_id="campaign-20260817-obr-costings",
                    computed_at=started_at,
                    release_bundle=bundle,
                    engine_version=engine_version,
                )
            )

    artifact_paths = []
    artifact_references = []
    for measure in measures:
        if measure["pe_reform"] is None:
            continue
        mapped_claims = [
            compute.resolve_claim(claims, measure, head, 2026)
            for head in measure["heads"]
        ]
        assert any(claim is not None for claim in mapped_claims)
        variables = sorted(
            {variable for head in measure["heads"] for variable in head["pe_variables"]}
        )
        output_path = artifacts_dir / f"{measure['measure_key']}_2026.json"
        artifact = compute.build_artifact(
            measure=measure,
            year=2026,
            baseline=synthetic_run_for_variables(bundle, variables, 100.0),
            reform=synthetic_run_for_variables(bundle, variables, 125.0),
            output_path=output_path,
            computed_at=started_at,
            run_id="campaign-20260817-obr-costings",
            claims=claims,
            claims_sha256=claims_sha256,
            registry_sha256=registry_sha256,
        )
        artifact["diagnostic_only"] = False
        artifact_reference = str(output_path.relative_to(tmp_path))
        artifact["artifact"] = artifact_reference
        compute.write_json(output_path, artifact)
        artifact_paths.append(output_path)
        artifact_references.append(artifact_reference)
        expected_rows.extend(compute.stage_artifact_rows(artifact, measure))

    assert len(artifact_references) == 21
    compute.write_jsonl(staged_path, expected_rows)
    compare.write_comparison_outputs(
        registry_path=registry_path,
        claims_path=claims_path,
        staged_path=staged_path,
        output_dir=output_dir,
        artifact_root=tmp_path,
    )
    manifest = {
        "schema_version": 1,
        "staged": True,
        "run_id": "campaign-20260817-obr-costings",
        "started_at": started_at,
        "engine_version": engine_version,
        "registry": "registry.yaml",
        "registry_sha256": registry_sha256,
        "claims": "claims.jsonl",
        "claims_sha256": claims_sha256,
        "years": [2026],
        "selected_measures": [measure["measure_key"] for measure in measures],
        "pa_smoke_probe": False,
        "certified_cache_preflight": {"release_bundle": bundle},
        "artifacts": artifact_references,
        "legacy_artifacts_without_dataset_hashes": [],
        "artifactless_frozen_registry": {
            measure["measure_key"]: compute.frozen_registry_measure(measure)
            for measure in measures
            if measure["pe_reform"] is None
        },
        "staged_output": "staged.jsonl",
        "staged_rows": len(expected_rows),
    }
    compute.write_json(manifest_path, manifest)
    output_paths = [
        *artifact_paths,
        staged_path,
        output_dir / "COMPARISON.csv",
        output_dir / "COMPARISON.md",
        manifest_path,
    ]
    first_outputs = {path: path.read_bytes() for path in output_paths}

    original_stage_not_computed_rows = compute.stage_not_computed_rows
    live_measure_ids = {id(measure) for measure in measures}
    frozen_artifactless_keys = set()

    def verify_artifactless_frozen_measure(*args, **kwargs):
        measure = kwargs["measure"]
        assert id(measure) not in live_measure_ids
        assert (
            measure == manifest["artifactless_frozen_registry"][measure["measure_key"]]
        )
        frozen_artifactless_keys.add(measure["measure_key"])
        return original_stage_not_computed_rows(*args, **kwargs)

    def forbidden(*args, **kwargs):
        raise AssertionError("restage reached simulation or certified-cache setup")

    monkeypatch.setattr(compute, "configure_offline", forbidden)
    monkeypatch.setattr(compute, "preflight_certified_dataset", forbidden)
    monkeypatch.setattr(compute, "run_managed_simulation", forbidden)
    monkeypatch.setattr(
        compute,
        "stage_not_computed_rows",
        verify_artifactless_frozen_measure,
    )

    summary = compute.restage_existing_run(
        manifest_path=manifest_path,
        output_dir=output_dir,
        artifact_root=tmp_path,
    )
    assert summary["artifacts"] == 21
    assert summary["diagnostic_artifacts"] == 0
    assert summary["staged_rows"] == len(expected_rows)
    replayed_rows = compute.load_claims(staged_path)
    constructed_keys = {
        row["measure_key"] for row in replayed_rows if row["status"] == "constructed"
    }
    not_computed_keys = {
        row["measure_key"] for row in replayed_rows if row["status"] == "not_computed"
    }
    assert len(constructed_keys) == 21
    assert len(not_computed_keys) == 5
    assert frozen_artifactless_keys == not_computed_keys
    assert constructed_keys | not_computed_keys == {
        measure["measure_key"] for measure in measures
    }
    assert {path: path.read_bytes() for path in output_paths} == first_outputs

    second_summary = compute.restage_existing_run(
        manifest_path=manifest_path,
        output_dir=output_dir,
        artifact_root=tmp_path,
    )
    assert second_summary == summary
    assert {path: path.read_bytes() for path in output_paths} == first_outputs

    null_measure = next(
        measure
        for measure in measures
        if measure["measure_key"] == "autumn_budget_2024__hmrc_5000_compliance_staff"
    )
    null_claim = next(
        claim
        for claim in compute._source_candidates(claims, null_measure, 2026)
        if claim["conditions"].get("tax_head") == "Income tax"
    )
    assert null_measure["pe_reform"] is None
    assert null_measure["measure_key"] in not_computed_keys
    assert null_claim["value"] == pytest.approx(138_872_923.1165392)

    def mutate_null_claim_value():
        raw_lines = claims_path.read_text().splitlines()
        for index, raw_line in enumerate(raw_lines):
            claim = json.loads(raw_line)
            if claim == null_claim:
                claim["value"] += 123_456_789
                raw_lines[index] = json.dumps(claim)
                break
        else:
            raise AssertionError("null-reform source claim was not found in the slice")
        claims_path.write_text("\n".join(raw_lines) + "\n")
        return compute.sha256_file(claims_path)

    drifted_sha256 = mutate_null_claim_value()
    monkeypatch.setattr(compute, "stage_not_computed_rows", forbidden)

    with pytest.raises(
        compute.ArtifactRestageError,
        match="claims SHA-256 differs from RUN_MANIFEST",
    ) as exc_info:
        compute.restage_existing_run(
            manifest_path=manifest_path,
            output_dir=output_dir,
            artifact_root=tmp_path,
        )
    message = str(exc_info.value)
    assert f"expected {claims_sha256}" in message
    assert f"actual {drifted_sha256}" in message
    assert "new run" in message
    assert "re-run" in message
    assert {path: path.read_bytes() for path in output_paths} == first_outputs

    claims_path.write_bytes(VENDORED_CLAIMS.read_bytes())
    mutated_during_reconstruction = False

    def mutate_during_reconstruction(*args, **kwargs):
        nonlocal mutated_during_reconstruction
        rows = original_stage_not_computed_rows(*args, **kwargs)
        if not mutated_during_reconstruction:
            assert mutate_null_claim_value() == drifted_sha256
            mutated_during_reconstruction = True
        return rows

    monkeypatch.setattr(
        compute,
        "stage_not_computed_rows",
        mutate_during_reconstruction,
    )
    with pytest.raises(
        compute.ArtifactRestageError,
        match="claims SHA-256 differs from RUN_MANIFEST",
    ) as exc_info:
        compute.restage_existing_run(
            manifest_path=manifest_path,
            output_dir=output_dir,
            artifact_root=tmp_path,
        )
    message = str(exc_info.value)
    assert mutated_during_reconstruction
    assert f"expected {claims_sha256}" in message
    assert f"actual {drifted_sha256}" in message
    assert "new run" in message
    assert "re-run" in message
    assert {path: path.read_bytes() for path in output_paths} == first_outputs


@pytest.mark.parametrize(
    ("obr_value", "pe_value", "ratio", "ratio_bin"),
    [
        (None, 1.0, None, "not_available"),
        (0.0, 0.0, None, "both_zero"),
        (0.0, 1.0, None, "obr_zero"),
        (2.0, 0.0, 0.0, "pe_zero"),
        (2.0, -1.0, -0.5, "opposite_sign"),
        (2.0, 0.99, 0.495, "same_sign_ratio_below_0.5"),
        (2.0, 1.0, 0.5, "same_sign_ratio_0.5_to_0.8"),
        (2.0, 1.6, 0.8, "same_sign_ratio_0.8_to_1.25"),
        (2.0, 2.5, 1.25, "same_sign_ratio_1.25_to_2"),
        (2.0, 4.0, 2.0, "same_sign_ratio_at_least_2"),
    ],
)
def test_descriptive_ratio_bins(obr_value, pe_value, ratio, ratio_bin):
    assert compare.ratio_and_bin(obr_value, pe_value) == (ratio, ratio_bin)


def test_comparison_resolves_measure_identity_and_traces_artifact(
    tmp_path, synthetic_measure, synthetic_claim
):
    bundle = {"certified_data_build_id": "synthetic-certified-build"}
    artifact_path = tmp_path / "synthetic_2026.json"
    artifact = compute.build_artifact(
        measure=synthetic_measure,
        year=2026,
        baseline=synthetic_run(bundle, 100.0),
        reform=synthetic_run(bundle, 125.0),
        output_path=artifact_path,
        computed_at="2026-08-16T12:00:00+00:00",
        run_id="campaign-20260816-obr-costings",
        claims=[synthetic_claim],
        claims_sha256=SYNTHETIC_CLAIMS_SHA256,
        registry_sha256=SYNTHETIC_REGISTRY_SHA256,
    )
    compute.write_json(artifact_path, artifact)
    staged = compute.stage_artifact_rows(artifact, synthetic_measure)[0]
    descriptor_twin = copy.deepcopy(synthetic_claim)
    descriptor_twin["reform_hint"] = "Another measure with the same descriptor"

    rows = compare.build_comparison_rows(
        [staged],
        [descriptor_twin, synthetic_claim],
        {synthetic_measure["measure_key"]: synthetic_measure},
    )

    assert len(rows) == 1
    assert rows[0]["obr_value_gbp"] == synthetic_claim["value"]
    assert rows[0]["pe_value_gbp"] == -25.0
    assert rows[0]["benchmark_class"] == "different_model"
    assert rows[0]["source_model"] == "synthetic_source_model"
    assert rows[0]["basis"] == "nominal"
    assert rows[0]["behavioural_adjustment"] == "unstated in harvest"
    assert rows[0]["ratio_bin"] == "same_sign_ratio_0.5_to_0.8"
    assert any(
        "measure Δ = −(reversal − baseline)" in x for x in rows[0]["annotations"]
    )
    assert any(
        "benchmark_class=different_model" in x
        and "head_scope=" in x
        and "remaining_difference=unexplained" in x
        for x in rows[0]["annotations"]
    )

    source_model_drift = copy.deepcopy(artifact)
    source_model_drift["heads"][0]["external_claim"]["source_model"] = (
        "different_source_model"
    )
    compute.write_json(artifact_path, source_model_drift)
    with pytest.raises(compare.ComparisonError, match="0 artifact heads"):
        compare.build_comparison_rows(
            [staged],
            [synthetic_claim],
            {synthetic_measure["measure_key"]: synthetic_measure},
        )
    compute.write_json(artifact_path, artifact)

    literal_staged = copy.deepcopy(staged)
    literal_staged["pe_value"] = 25.0
    with pytest.raises(compare.ComparisonError, match="staged and artifact PE"):
        compare.build_comparison_rows(
            [literal_staged],
            [synthetic_claim],
            {synthetic_measure["measure_key"]: synthetic_measure},
        )
    assert any("remaining_difference=unexplained" in x for x in rows[0]["annotations"])


def test_comparison_total_is_explicitly_mapped_head_only(synthetic_measure):
    synthetic_measure = copy.deepcopy(synthetic_measure)
    synthetic_measure["computability"] = "partial"
    synthetic_measure["unmapped_obr_heads"] = ["Corporation tax (onshore)"]
    common = {
        "measure_key": synthetic_measure["measure_key"],
        "obr_description": synthetic_measure["obr_description"],
        "fiscal_event": synthetic_measure["fiscal_event"],
        "year": 2026,
        "fy": "2026-27",
        "row_kind": "head",
        "status": "constructed",
        "benchmark_class": "different_model",
        "construction": "reversal_on_certified_world",
        "artifact": "synthetic.json",
        "annotations": [],
        "source_model": "synthetic_source_model",
        "basis": "nominal",
        "behavioural_adjustment": "unstated in harvest",
    }
    head_rows = [
        {
            **common,
            "head": "Income tax",
            "obr_value_gbp": 100.0,
            "pe_value_gbp": 75.0,
            "pe_to_obr_ratio": 0.75,
            "ratio_bin": "same_sign_ratio_0.5_to_0.8",
            "source_table": "Tax Measures (Policy measures database)",
            "external_metric": "revenue_change",
        },
        {
            **common,
            "head": "Welfare inside cap",
            "obr_value_gbp": -40.0,
            "pe_value_gbp": -30.0,
            "pe_to_obr_ratio": 0.75,
            "ratio_bin": "same_sign_ratio_0.5_to_0.8",
            "source_table": "Spending Measures (Policy measures database)",
            "external_metric": "exchequer_impact",
        },
    ]

    totals = compare.derive_mapped_head_totals(
        head_rows, {synthetic_measure["measure_key"]: synthetic_measure}
    )

    assert len(totals) == 1
    assert totals[0]["row_kind"] == "mapped_head_total"
    assert totals[0]["obr_value_gbp"] == 60.0
    assert totals[0]["pe_value_gbp"] == 45.0
    assert totals[0]["source_model"] == "synthetic_source_model"
    assert totals[0]["basis"] == "nominal"
    assert totals[0]["behavioural_adjustment"] == "unstated in harvest"
    assert any(
        "not attached to an external TOTAL claim" in x for x in totals[0]["annotations"]
    )
    assert any(
        "measure Δ = −(reversal − baseline)" in x for x in totals[0]["annotations"]
    )
    assert any(
        "benchmark_class=different_model" in x
        and "head_scope=mapped PMD heads only" in x
        and "remaining_difference=unexplained" in x
        for x in totals[0]["annotations"]
    )
    assert any("Partial scope" in x for x in totals[0]["annotations"])


def test_committed_smoke_comparison_is_measure_oriented():
    with SMOKE_COMPARISON.open(newline="") as source:
        rows = list(csv.DictReader(source))

    assert len(rows) == 26
    assert sum(row["row_kind"] == "mapped_head_total" for row in rows) == 6
    assert {
        (row["measure_key"], row["year"], row["head"])
        for row in rows
        if row["ratio_bin"] == "pe_zero"
    } == {
        (
            "spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp",
            "2026",
            "Income tax",
        ),
        (
            "spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp",
            "2027",
            "Income tax",
        ),
        (
            "spring_budget_2024__hicbc_threshold_and_taper",
            "2026",
            "Welfare inside cap",
        ),
        (
            "spring_budget_2024__hicbc_threshold_and_taper",
            "2027",
            "Welfare inside cap",
        ),
    }
    expected_summary_bins = {
        "efo_march_2026__pa_and_hrt_freezes": "same_sign_ratio_1.25_to_2",
        "efo_march_2026__additional_rate_threshold_reduction": (
            "same_sign_ratio_1.25_to_2"
        ),
        "spring_budget_2024__class_1_employee_nics_main_rate_cut_2pp": (
            "same_sign_ratio_1.25_to_2"
        ),
        "spring_budget_2024__hicbc_threshold_and_taper": ("same_sign_ratio_at_least_2"),
        "autumn_budget_2024__employer_nics_package": ("same_sign_ratio_0.5_to_0.8"),
        "autumn_budget_2025__uc_child_element_remove_two_child_limit": (
            "same_sign_ratio_0.5_to_0.8"
        ),
    }
    summary_rows = [
        row
        for row in rows
        if row["row_kind"] in {"total", "mapped_head_total"}
        or row["measure_key"]
        == "autumn_budget_2025__uc_child_element_remove_two_child_limit"
    ]
    assert len(summary_rows) == 12
    assert all(
        row["ratio_bin"] == expected_summary_bins[row["measure_key"]]
        for row in summary_rows
    )


def test_committed_rows_use_only_harvested_source_axes():
    staged_rows = [json.loads(line) for line in SMOKE_STAGED.read_text().splitlines()]
    with SMOKE_COMPARISON.open(newline="") as source:
        comparison_rows = list(csv.DictReader(source))

    forbidden = (
        "OBR behavioural-adjusted",
        "HMT/HMRC costing models",
        "announcement baseline",
        "reform-induced claiming",
    )
    for row in [*staged_rows, *comparison_rows]:
        expected_source_model = (
            "obr_efo_forecast"
            if row["source_table"] == "3.17: 3.17"
            else "hmt_scorecard_obr_database"
        )
        expected_basis = (
            "unstated" if row["source_table"] == "3.17: 3.17" else "forecast"
        )
        assert row["source_model"] == expected_source_model
        assert row["basis"] == expected_basis
        assert row["behavioural_adjustment"] == "unstated in harvest"
        annotations = (
            " ".join(row["annotations"])
            if isinstance(row["annotations"], list)
            else row["annotations"]
        )
        assert "PE: static microsimulation on the certified world" in annotations
        assert not any(text in annotations for text in forbidden)


def test_employer_nics_income_tax_row_cites_incidence_mechanism():
    with SMOKE_COMPARISON.open(newline="") as source:
        rows = list(csv.DictReader(source))
    income_tax_rows = [
        row
        for row in rows
        if row["measure_key"] == "autumn_budget_2024__employer_nics_package"
        and row["row_kind"] == "head"
        and row["head"] == "Income tax"
    ]

    assert len(income_tax_rows) == 2
    for row in income_tax_rows:
        assert float(row["pe_value_gbp"]) != 0
        assert (
            "policyengine_uk/parameters/gov/contrib/policyengine/"
            "employer_ni/employee_incidence.yaml" in row["annotations"]
        )
        assert (
            "policyengine_uk/variables/contrib/policyengine/employer_ni/"
            "employer_ni_fixed_employer_cost_change.py" in row["annotations"]
        )
        assert "holding employer cost fixed" in row["annotations"]
        assert "why the PE Income-tax head is non-zero" in row["annotations"]


def test_hicbc_welfare_rows_and_artifacts_keep_mapping_provisional():
    staged_rows = [json.loads(line) for line in SMOKE_STAGED.read_text().splitlines()]
    welfare_rows = [
        row
        for row in staged_rows
        if row["measure_key"] == "spring_budget_2024__hicbc_threshold_and_taper"
        and row["external_claim_match"]["conditions"].get("spending_head")
        == "Welfare inside cap"
    ]

    assert len(welfare_rows) == 2
    for row in welfare_rows:
        annotations = " ".join(row["annotations"])
        assert "PROVISIONAL PE head mapping" in annotations
        assert "identifies neither the programme nor a mechanism" in annotations
        assert "would_claim_child_benefit is fixed" in annotations
        assert "child_benefit delta is zero" in annotations
        artifact = json.loads((ROOT / row["artifact"]).read_text())
        assert "PROVISIONAL PE head mapping" in artifact["notes"]
        assert "reform-induced claiming" not in artifact["notes"]
