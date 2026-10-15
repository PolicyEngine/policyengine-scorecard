"""Engine-free checks of diagnostic scheduling and recorded source evidence."""

import hashlib
import json
from copy import deepcopy
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from pipeline import diagnose_uk_event_models as diagnostics


def established():
    return json.loads(
        (diagnostics.ROOT / "results/uk/events/MODEL_DIAGNOSTICS.json").read_text()
    )


def test_reverify_scopes_historical_text_and_uses_the_measured_predicate(monkeypatch):
    prior = established()
    measured = deepcopy(prior)
    for record in measured:
        record["engine_version"] = "2.125.1"
        record["interpretation"] = "Legacy text emitted by investigate"
    employer = next(
        r for r in measured if r["id"] == "employer_nics_state_pension_age_exemption"
    )
    employer["observation"]["ni_class_1_employer"] = [6750.0, 6750.0]
    missing = next(r for r in measured if r["id"] == "cgt_main_rate_commencement")
    missing["evidence"] = {"engine_file": "moved.yaml", "missing": True}
    calls = []

    def investigate(case, *, expect_engine, tolerant):
        calls.append((case, expect_engine, tolerant))
        return measured

    monkeypatch.setattr(diagnostics, "investigate", investigate)
    results = diagnostics.reverify(prior, expect_engine="2.125.1")
    assert calls == [(None, "2.125.1", True)]
    for result, old in zip(results, prior):
        assert "interpretation" not in result
        assert result["established"]["engine_version"] == "2.89.2"
        assert result["established"]["interpretation"] == old["interpretation"]
        for key in (
            "primary_source",
            "assessment",
            "existing_issue",
            "observation_provenance",
        ):
            assert key not in result
            if key in old:
                assert result["established"][key] == old[key]
        assert result["status"] == diagnostics.defect_status(result)
        assert result["status_on_established_observation"] == diagnostics.defect_status(
            old
        )
        assert "policyengine-uk 2.125.1" in result["engine_observation"]
        assert (
            "--reverify results/uk/events/MODEL_DIAGNOSTICS.json"
            in result["reproducer"]
        )
    assert employer["status"] == "resolved"
    assert missing["status"] == "inconclusive"
    assert all("established" not in r for r in prior)


def test_reverify_rejects_a_different_case_set(monkeypatch):
    monkeypatch.setattr(diagnostics, "investigate", lambda *a, **kw: [])
    with pytest.raises(RuntimeError, match="case set differs"):
        diagnostics.reverify(established(), expect_engine="2.125.1")


def test_reverified_report_labels_engine_history_and_handles_missing_source(
    monkeypatch, tmp_path
):
    prior = established()
    records = deepcopy(prior)
    for record in records:
        record["engine_version"] = "2.125.1"
        record["evidence"] = {"engine_file": "moved.yaml", "missing": True}
    monkeypatch.setattr(diagnostics, "investigate", lambda *a, **kw: records)
    prior_path = tmp_path / "prior.json"
    prior_path.write_text(json.dumps(prior))
    output = tmp_path / "current.json"
    report = tmp_path / "report.md"
    assert (
        diagnostics.main(
            [
                "--reverify",
                str(prior_path),
                "--expect-engine",
                "2.125.1",
                "--output",
                str(output),
                "--report",
                str(report),
                "--case",
                "cgt_main_rate_commencement",
            ]
        )
        == 0
    )
    text = report.read_text()
    assert "inspect policyengine-uk 2.125.1" in text
    assert "Established on policyengine-uk 2.89.2:" in text
    assert "file missing on this engine" in text
    assert ".venv-candidate/bin/python" in text
    assert (
        "--reverify results/uk/events/MODEL_DIAGNOSTICS.json --expect-engine 2.125.1 --case cgt_main_rate_commencement"
        in text
    )
    assert ".venv-replay" not in text
    # Rendering saved observations also follows the current engine and history.
    saved_report = tmp_path / "saved.md"
    assert (
        diagnostics.main(["--from-json", str(output), "--report", str(saved_report)])
        == 0
    )
    assert saved_report.read_bytes() == report.read_bytes()


def test_committed_variant_statuses_reproduce_both_engine_observations():
    prior = {r["id"]: r for r in established()}
    records = json.loads(
        (
            diagnostics.ROOT
            / "results/uk/replays/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/MODEL_DIAGNOSTICS.json"
        ).read_text()
    )
    assert {r["id"] for r in records} == set(prior)
    for record in records:
        assert "interpretation" not in record
        assert record["status"] == diagnostics.defect_status(record), record["id"]
        assert record["status_on_established_observation"] == diagnostics.defect_status(
            prior[record["id"]]
        )
        assert (
            record["established"]["interpretation"]
            == prior[record["id"]]["interpretation"]
        )


def test_cgt_resolution_requires_all_three_exact_day_weighted_rates():
    record = next(r for r in established() if r["id"] == "cgt_main_rate_commencement")
    old, new = (0.10, 0.20, 0.20), (0.18, 0.24, 0.24)
    names = ("basic", "higher", "additional")
    blended = {
        name: a * 207 / 365 + b * 158 / 365 for name, a, b in zip(names, old, new)
    }
    record["observation"]["2024-10-30"] = blended
    assert diagnostics.defect_status(record) == "resolved"
    for name, full in zip(names, new):
        wrong = deepcopy(record)
        wrong["observation"]["2024-10-30"][name] = full
        assert diagnostics.defect_status(wrong) == "inconclusive", name
        wrong["observation"]["2024-10-30"].pop(name)
        assert diagnostics.defect_status(wrong) == "inconclusive", name
    wrong = deepcopy(record)
    wrong["observation"]["2024-10-30"]["basic"] += 1e-5
    assert diagnostics.defect_status(wrong) == "inconclusive"


# Corrupt predicate-required numerical inputs in otherwise valid observations.
REQUIRED_INPUTS = (
    [
        ("carers_allowance_earnings_test_absent", ("annual_carers_allowance_gbp", i))
        for i in (0, 1)
    ]
    + [
        ("cgt_main_rate_commencement", (date, rate))
        for date in ("2024-10-30", "2025-04-06")
        for rate in ("basic", "higher", "additional")
    ]
    + [
        ("sdlt_additional_home_hike_absent", ("2025-04-06", 0)),
        ("private_school_vat_current_law_lever_zero", ("2025-06-01",)),
        ("dividend_band_threshold_lag", ("2024-06-01", "uk_higher_threshold")),
        (
            "class4_threshold_indexation_from_2027",
            ("2027-06-01", "lower_profits_limit"),
        ),
        (
            "uc_lcwra_protection_stops_at_2030",
            ("annual_synthetic_lcwra_element", "2030", 0),
        ),
        ("employer_nics_state_pension_age_exemption", ("ni_class_1_employer", 0)),
        ("pension_taper_omits_employer_contributions", ("pension_annual_allowance", 0)),
        (
            "annual_allowance_charge_single_marginal_rate",
            ("personal_pension_contributions_tax", 0),
        ),
    ]
)
WRONG_NUMBERS = (
    st.none()
    | st.booleans()
    | st.text()
    | st.lists(st.integers())
    | st.dictionaries(st.text(), st.integers())
)


@settings(max_examples=150, deadline=None)
@given(st.sampled_from(REQUIRED_INPUTS), WRONG_NUMBERS)
def test_wrong_type_required_inputs_are_always_inconclusive(case, value):
    identifier, path = case
    record = next(r for r in established() if r["id"] == identifier)
    node = record["observation"]
    for part in path[:-1]:
        node = node[part]
    node[path[-1]] = value
    assert diagnostics.defect_status(record) == "inconclusive"


@settings(max_examples=100, deadline=None)
@given(
    st.sampled_from(sorted(diagnostics.DEFECT_PREDICATES)),
    st.sampled_from([float("nan"), float("inf"), -float("inf")]),
)
def test_nonfinite_observations_are_always_inconclusive(identifier, value):
    record = next(r for r in established() if r["id"] == identifier)
    # Even an unused nested observation must not allow a definite status.
    record["observation"]["extra"] = [{"value": value}]
    assert diagnostics.defect_status(record) == "inconclusive"


@settings(max_examples=100, deadline=None)
@given(
    st.sampled_from(sorted(diagnostics.DEFECT_PREDICATES)),
    st.sampled_from(["evidence", "observation"]),
    st.none() | st.booleans() | st.integers() | st.text() | st.lists(st.integers()),
)
def test_wrong_record_containers_are_always_inconclusive(identifier, field, value):
    record = next(r for r in established() if r["id"] == identifier)
    record[field] = value
    assert diagnostics.defect_status(record) == "inconclusive"


@pytest.mark.parametrize(
    "case,path",
    [
        (identifier, path[:-1])
        for identifier, path in REQUIRED_INPUTS
        if isinstance(path[-1], int)
        and identifier != "sdlt_additional_home_hike_absent"
    ],
)
def test_wrong_person_counts_are_inconclusive(case, path):
    record = next(r for r in established() if r["id"] == case)
    node = record["observation"]
    for part in path:
        node = node[part]
    node.append(node[0])
    assert diagnostics.defect_status(record) == "inconclusive"


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
        lambda root, path, **options: {
            "engine_file": path,
            "sha256": "recorded separately",
        },
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


def test_a_plain_run_on_another_engine_is_refused(capsys):
    # Review of 463fc8d, 3: without --reverify a run on another engine would
    # stamp 2.89.2 interpretations with the new engine's version.
    with pytest.raises(SystemExit) as exit_info:
        diagnostics.main(
            ["--expect-engine", "2.125.1", "--case", "cgt_main_rate_commencement"]
        )
    assert exit_info.value.code == 2
    assert "use --reverify" in capsys.readouterr().err


def test_reverification_starts_from_the_established_record():
    # A re-verified file has lost the legacy fields to `established`;
    # re-verifying from it would drop the 2.89.2 interpretation.
    reverified = [{"id": "x", "engine_version": "2.125.1", "established": {}}]
    with pytest.raises(ValueError, match="established diagnostics"):
        diagnostics.reverify(reverified, expect_engine="2.130.1")
