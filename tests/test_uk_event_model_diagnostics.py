"""Engine-free checks of diagnostic scheduling and recorded source evidence."""

import hashlib
import json
from pathlib import Path

from pipeline import diagnose_uk_event_models as diagnostics


def test_synthetic_diagnostics_release_worlds_and_use_only_supplied_households(
    monkeypatch,
):
    live = 0
    maximum_live = 0
    constructed = []

    class Values:
        def tolist(self):
            return [0]

    class SmallSimulation:
        def __init__(self, *, situation):
            nonlocal live, maximum_live
            live += 1
            maximum_live = max(maximum_live, live)
            constructed.append(situation)

        def calculate(self, variable, year):
            return Values()

        def __del__(self):
            nonlocal live
            live -= 1

    monkeypatch.setattr(
        diagnostics,
        "_source",
        lambda root, path: {"engine_file": path, "sha256": "recorded separately"},
    )
    rows = diagnostics._additional_model_checks(Path("unused"), SmallSimulation, None)
    assert len(rows) == len(constructed) == 3
    assert maximum_live == 1
    assert live == 0
    assert [len(situation["people"]) for situation in constructed] == [2, 1, 1]
    constructed.clear()
    selected = diagnostics._additional_model_checks(
        Path("unused"), SmallSimulation, "pension_taper_omits_employer_contributions"
    )
    assert [row["id"] for row in selected] == [
        "pension_taper_omits_employer_contributions"
    ]
    assert len(constructed) == 1
    assert live == 0


def test_saved_candidates_bind_source_and_measured_observations():
    rows = json.loads(
        (diagnostics.ROOT / "results/uk/events/MODEL_DIAGNOSTICS.json").read_text()
    )
    selected = {row["id"]: row for row in rows if row.get("primary_source")}
    assert set(selected) == {
        "employer_nics_state_pension_age_exemption",
        "pension_taper_omits_employer_contributions",
        "annual_allowance_charge_single_marginal_rate",
        "class4_threshold_indexation_from_2027",
    }
    for row in selected.values():
        assert row["engine_version"] == "2.89.2"
        assert row["national_effect"] == "unsized"
        assert row["primary_source"]["url"].startswith("https://www.gov.uk/")
        for evidence in [row["evidence"], *row.get("supporting_evidence", [])]:
            assert (
                hashlib.sha256(evidence["source"].encode()).hexdigest()
                == evidence["sha256"]
            )
    ni = selected["employer_nics_state_pension_age_exemption"]["observation"]
    assert ni["ni_liable"] == [True, False]
    assert ni["ni_class_1_employer"][0] > 0
    assert ni["ni_class_1_employer"][1] == 0
    assert selected["pension_taper_omits_employer_contributions"]["observation"] == {
        "adjusted_net_income": [240000.0],
        "pension_annual_allowance": [60000.0],
    }
    assert selected["annual_allowance_charge_single_marginal_rate"]["observation"] == {
        "personal_pension_contributions_tax": [4000.0]
    }


def test_integrated_execution_receipt_binds_observations_and_metadata_additions():
    receipt = json.loads(
        (
            diagnostics.ROOT / "results/uk/events/MODEL_DIAGNOSTICS_VERIFICATION.json"
        ).read_text()
    )
    actual_path = diagnostics.ROOT / receipt["actual_output_path"]
    current_path = diagnostics.ROOT / receipt["checked_in_current_path"]
    assert (
        hashlib.sha256(actual_path.read_bytes()).hexdigest()
        == receipt["actual_output_sha256"]
    )
    assert (
        hashlib.sha256(current_path.read_bytes()).hexdigest()
        == receipt["checked_in_current_sha256"]
    )
    actual = {row["id"]: row for row in json.loads(actual_path.read_text())}
    current = {row["id"]: row for row in json.loads(current_path.read_text())}
    assert len(actual) == len(current) == 10
    assert actual.keys() == current.keys()
    for key, observation in actual.items():
        for field in receipt["current_engine_fields_compared"]:
            assert observation.get(field) == current[key].get(field)
    metadata_differences = {
        (key, field)
        for key in actual
        for field in actual[key].keys() | current[key].keys()
        if actual[key].get(field) != current[key].get(field)
    }
    assert metadata_differences == {
        ("employer_nics_state_pension_age_exemption", "observation_provenance"),
        ("pension_taper_omits_employer_contributions", "observation_provenance"),
        ("annual_allowance_charge_single_marginal_rate", "observation_provenance"),
        ("class4_threshold_indexation_from_2027", "primary_source"),
        ("class4_threshold_indexation_from_2027", "national_effect"),
    }
    assert receipt["execution_exit_code"] == 0
    assert receipt["semantic_differences"] == []
