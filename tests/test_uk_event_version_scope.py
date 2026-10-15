"""Diagnoses and construction notes belong to the engine that established them."""

import copy
import json
import re
import shlex
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from pipeline import compare_uk_event as compare
from pipeline import diagnose_uk_event_models as diagnose

ROOT = Path(__file__).resolve().parent.parent
EVENTS = (
    "autumn_budget_2024",
    "autumn_statement_2023",
    "spring_budget_2024",
    "spring_statement_2025",
    "spring_budget_2023",
)
VARIANT = {
    "engine_version": "2.125.1",
    "policyengine_version": "6.2.6",
    "data_bundle": "policyengine-uk-data-1.58.0",
    "variant_id": "pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0",
    "data_years": list(range(2024, 2031)),
    "unsupported_years": [{"year": 2023, "reason": "before_data_year"}],
    "run_manifest": None,
}
# Sentences that state 2.89.2 facts as facts about the run.
LEGACY_ONLY = (
    "£3.15",
    "#1887",
    "still has the 3% surcharge scale",
    "−£786.808m",
    "-£786.808m",
    "processed employee NICs main rate is 8%",
)


def measures():
    for event in EVENTS:
        registry = json.loads(
            (ROOT / f"data/uk/events/{event}_measures.json").read_text()
        )
        yield from registry["measures"]


def test_legacy_review_diagnoses_are_unchanged_and_others_are_prior():
    seen = 0
    for measure in measures():
        for year in (2024, 2027):
            legacy = compare.review_diagnosis(measure["measure_key"], year)
            assert legacy == compare.review_diagnosis(
                measure["measure_key"], year, "", compare.LEGACY_ENGINE
            )
            other = compare.review_diagnosis(
                measure["measure_key"], year, "", "2.125.1"
            )
            if not legacy:
                assert other == {}
                continue
            seen += 1
            assert "cause_class" not in other and "issues" not in other
            (prior,) = other["prior_diagnoses"]
            assert prior["status"] == "not_reverified"
            assert prior["established_on"] == ["2.89.2"]
            assert {
                k: v for k, v in prior.items() if k not in ("status", "established_on")
            } == legacy
    assert seen >= 9


def test_construction_notes_on_another_engine_are_labelled_and_scoped():
    for measure in measures():
        legacy = compare.construction_note(measure)
        assert legacy == compare.construction_note(measure, compare.LEGACY_ENGINE)
        other = compare.construction_note(measure, "2.125.1")
        if not measure.get("note"):
            assert other == ""
            continue
        assert other.startswith("Authored against policyengine-uk 2.89.2: ")
        assert other.endswith("recorded in CONSTRUCTION_PREMISES.json.")
        appended = other.removeprefix("Authored against policyengine-uk 2.89.2: ")
        appended = appended.removeprefix(measure["note"])
        assert not any(marker in appended for marker in LEGACY_ONLY)


def test_same_engine_with_another_data_bundle_keeps_legacy_observations_prior():
    other_data = {
        **VARIANT,
        "engine_version": compare.LEGACY_ENGINE,
        "variant_id": "same-engine-other-data",
        "data_bundle": "other-certified-data",
    }
    seen = 0
    for measure in measures():
        diagnosis = compare.review_diagnosis(
            measure["measure_key"],
            2027,
            engine_version=compare.LEGACY_ENGINE,
            identity=other_data,
        )
        if compare.review_diagnosis(measure["measure_key"], 2027):
            seen += 1
            assert set(diagnosis) == {"prior_diagnoses"}
            assert diagnosis["prior_diagnoses"][0]["status"] == "not_reverified"
        note = compare.construction_note(measure, identity=other_data)
        if measure.get("note"):
            assert note.startswith("Authored against policyengine-uk 2.89.2:")
            assert "CONSTRUCTION_PREMISES.json" in note
        else:
            assert note == ""
    assert seen >= 9

    registry = json.loads(
        (ROOT / "data/uk/events/autumn_budget_2024_measures.json").read_text()
    )
    original = next(
        measure
        for measure in registry["measures"]
        if measure["measure_key"].endswith("__capital_gains_main_rates_and_reliefs")
    )
    source = original["source_rows"][0]
    registry["measures"] = [{**original, "source_rows": [source]}]
    staged = {
        "source_row_id": source["source_row_id"],
        "measure_key": original["measure_key"],
        "fy": source["fy"],
        "tax_head": source["tax_head"],
        "external_value_gbp": source["value_gbp"],
        "external_value_gbp_decimal": source["value_gbp_decimal"],
        "pe_value": None,
        "status": "not_computed",
    }
    rows = compare.build_comparison_rows(registry, [staged], identity=other_data)
    assert set(rows[0]["diagnosis"]) == {"prior_diagnoses"}
    assert rows[0]["construction_note"].startswith(
        "Authored against policyengine-uk 2.89.2:"
    )
    text = compare.render_markdown(registry, rows, identity=other_data)
    assert "## Prior diagnoses" in text
    assert "## Review diagnoses" not in text


def test_run_identity_defaults_to_the_legacy_run(tmp_path):
    identity = compare.run_identity(tmp_path)
    assert identity["engine_version"] == "2.89.2"
    assert not compare.is_variant(identity)
    (tmp_path / "RUN_MANIFEST.json").write_text(
        json.dumps(
            {"engine_version": "2.125.1", "variant_id": "v", "data_years": [2024]}
        )
    )
    identity = compare.run_identity(tmp_path)
    assert compare.is_variant(identity)
    assert identity["run_manifest"] == tmp_path / "RUN_MANIFEST.json"


def test_variant_reports_state_their_execution_and_unsupported_years():
    registry = json.loads(
        (ROOT / "data/uk/events/spring_budget_2023_measures.json").read_text()
    )
    rows = [
        {
            "event_slug": "spring_budget_2023",
            "source_row_id": "x",
            "measure_key": registry["measures"][0]["measure_key"],
            "title": "t",
            "classification": "partial",
            "gap_kind": None,
            "measure_type": "m",
            "fy": "2023-24",
            "year": 2023,
            "tax_head": "Income tax",
            "obr_value_gbp": 1.0,
            "obr_value_gbp_decimal": "1",
            "pe_value_gbp": None,
            "pe_to_obr_ratio": None,
            "ratio_bin": "pe_missing",
            "status": "unsupported_on_variant",
            "reason": "CY2023 is outside v's supported data years 2024–2030 (before_data_year)",
            "diagnosis": compare.review_diagnosis(
                "spring_budget_2023__pension_annual_allowance_package",
                2023,
                "",
                "2.125.1",
            ),
            "gap_gbp": None,
            "explained_share": None,
        }
    ]
    grid = {
        "full_event_complete": False,
        "full_supported_grid_complete": True,
        "unsupported_years": [2023],
    }
    text = compare.render_markdown(registry, rows, grid, VARIANT)
    assert "policyengine-uk 2.125.1 with policyengine 6.2.6" in text
    assert "pinned certified 2023 population" not in text
    assert "Unsupported on this release: calendar years 2023" in text
    assert "1 source rows keep their OBR values" in text
    assert "Numerical replay grid incomplete" not in text
    assert "## Prior diagnoses, established on policyengine-uk 2.89.2" in text
    assert "## Review diagnoses" not in text
    legacy = compare.render_markdown(registry, [], None, None)
    assert "pinned certified 2023 population" in legacy


def established():
    return json.loads((ROOT / "results/uk/events/MODEL_DIAGNOSTICS.json").read_text())


def test_variant_summary_reproduces_statuses_and_counts_only_current_candidates():
    diagnostics = [
        {
            **record,
            "engine_version": VARIANT["engine_version"],
            "established_on": [compare.LEGACY_ENGINE],
            "events": ["autumn_budget_2024"],
            "class": "pe_gap",
        }
        for record in established()[:3]
    ]
    diagnostics[0]["status"] = "persists"
    diagnostics[1]["status"] = "resolved"
    text = compare.render_summary(
        {"autumn_budget_2024": []}, diagnostics=diagnostics, identity=VARIANT
    )
    assert "| Status on this engine |" in text
    assert "| persists (established on 2.89.2) |" in text
    assert "| resolved (established on 2.89.2) |" in text
    assert "| not re-verified (established on 2.89.2) |" in text
    assert "issue candidates recorded: 1." in text
    assert ".venv-replay/bin/python" not in text
    for record in diagnostics:
        line = next(
            line for line in text.splitlines() if line.startswith(f"| {record['id']} |")
        )
        command = shlex.split(line.split("`")[1])
        assert command == [
            "PYTHONPATH=.",
            ".venv-candidate/bin/python",
            "pipeline/diagnose_uk_event_models.py",
            "--reverify",
            "results/uk/events/MODEL_DIAGNOSTICS.json",
            "--expect-engine",
            VARIANT["engine_version"],
            "--case",
            record["id"],
        ]


def test_legacy_summary_counts_established_candidates_without_a_status():
    diagnostic = established()[0]
    assert "status" not in diagnostic
    text = compare.render_summary(
        {diagnostic["events"][0]: []}, diagnostics=[diagnostic]
    )
    assert "issue candidates recorded: 1." in text
    assert "Status on this engine" not in text
    assert (
        "PYTHONPATH=. .venv-replay/bin/python pipeline/diagnose_uk_event_models.py "
        + diagnostic["reproducer"]
    ) in text


@pytest.mark.parametrize("identity", [None, VARIANT])
def test_summary_refuses_diagnostics_from_another_engine(identity):
    diagnostic = {**established()[0], "engine_version": "different-engine"}
    with pytest.raises(compare.EventComparisonError, match="differs from run engine"):
        compare.render_summary(
            {diagnostic["events"][0]: []}, diagnostics=[diagnostic], identity=identity
        )


def test_variant_summary_numerical_reproducer_uses_the_variant_interpreter():
    rows = json.loads(
        (ROOT / "results/uk/events/autumn_budget_2024/COMPARISON.json").read_text()
    )
    row = next(row for row in rows if row["pe_value_gbp"] is not None)
    text = compare.render_summary({"autumn_budget_2024": [row]}, identity=VARIANT)
    assert (
        "PYTHONPATH=. .venv-candidate/bin/python pipeline/compute_uk_event.py" in text
    )
    assert f"--variant {VARIANT['variant_id']}" in text
    assert ".venv-replay/bin/python" not in text


@pytest.mark.parametrize("registered_namespace", [True, False])
def test_summary_without_comparisons_uses_only_registered_namespace_identity(
    tmp_path, registered_namespace
):
    document_path = ROOT / "data/uk/replay_variants.json"
    document = json.loads(document_path.read_text())
    record = next(
        record
        for record in document["variants"]
        if record["variant_id"] == VARIANT["variant_id"]
    )
    copied_document = tmp_path / "data/uk/replay_variants.json"
    copied_document.parent.mkdir(parents=True)
    copied_document.write_bytes(document_path.read_bytes())
    requirements = tmp_path / record["requirements"]["path"]
    requirements.parent.mkdir(parents=True)
    requirements.write_bytes((ROOT / record["requirements"]["path"]).read_bytes())
    registry = tmp_path / "data/uk/events/autumn_budget_2024_measures.json"
    registry.parent.mkdir(parents=True)
    registry.write_bytes(
        (ROOT / "data/uk/events/autumn_budget_2024_measures.json").read_bytes()
    )
    events_root = tmp_path / (
        record["result_root"] if registered_namespace else "unregistered"
    )
    events_root.mkdir(parents=True)
    diagnostic = {
        **established()[0],
        "engine_version": VARIANT["engine_version"],
        "status": "persists",
    }
    (events_root / "MODEL_DIAGNOSTICS.json").write_text(json.dumps([diagnostic]))
    if not registered_namespace:
        with pytest.raises(
            compare.EventComparisonError, match="differs from run engine"
        ):
            compare.write_summary(events_root, artifact_root=tmp_path)
        assert not (events_root / "SUMMARY.md").exists()
        return
    compare.write_summary(events_root, artifact_root=tmp_path)
    text = (events_root / "SUMMARY.md").read_text()
    assert (
        f"This namespace describes certified variant `{VARIANT['variant_id']}`" in text
    )
    assert "policyengine-uk 2.125.1 with policyengine 6.2.6" in text
    assert (
        "Numerical comparison outputs available: 0. Registry inventories available: 1."
        in text
    )
    assert "Unavailable: no completed numerical comparison rows" in text
    assert "| Status on this engine |" in text


def test_every_predicate_finds_its_defect_in_its_founding_observation():
    records = established()
    assert {r["id"] for r in records} == set(diagnose.DEFECT_PREDICATES)
    for record in records:
        assert diagnose.defect_status(record) == "persists", record["id"]


def test_resolution_signatures():
    by_id = {r["id"]: r for r in established()}
    fixed = {
        "carers_allowance_earnings_test_absent": {
            "annual_carers_allowance_gbp": [4331.0, 0.0]
        },
        "cgt_main_rate_commencement": {
            "2024-10-30": {
                "basic": 0.10 * 207 / 365 + 0.18 * 158 / 365,
                "higher": 0.20 * 207 / 365 + 0.24 * 158 / 365,
                "additional": 0.20 * 207 / 365 + 0.24 * 158 / 365,
            },
            "2025-04-06": {"basic": 0.18, "higher": 0.24, "additional": 0.24},
        },
        "sdlt_additional_home_hike_absent": {
            "2025-04-06": [0.05, 0.07, 0.10, 0.15, 0.17]
        },
        "private_school_vat_current_law_lever_zero": {
            "2025-01-01": 0.2,
            "2025-06-01": 0.2,
            "2026-06-01": 0.2,
        },
        "employer_nics_state_pension_age_exemption": {
            "ni_class_1_employer": [6750.0, 6750.0]
        },
        "pension_taper_omits_employer_contributions": {
            "pension_annual_allowance": [45000.0]
        },
        "annual_allowance_charge_single_marginal_rate": {
            "personal_pension_contributions_tax": [6460.0]
        },
    }
    for identifier, observation in fixed.items():
        record = {**by_id[identifier], "observation": observation}
        assert diagnose.defect_status(record) == "resolved", identifier


def test_moved_code_or_missing_variables_are_inconclusive_never_resolved():
    for record in established():
        missing_file = copy.deepcopy(record)
        missing_file["evidence"] = {"engine_file": "x.py", "missing": True}
        assert diagnose.defect_status(missing_file) == "inconclusive"
        absent = {**record, "absent_variables": ["x"]}
        assert diagnose.defect_status(absent) == "inconclusive"


# Every key a predicate reads (test_property_keys_reach_every_predicate_input).
KEYS = [
    "2024-10-30",
    "2025-04-06",
    "2029",
    "2030",
    "basic",
    "higher",
    "additional",
    "ni_class_1_employer",
    "pension_annual_allowance",
    "annual_carers_allowance_gbp",
    "annual_synthetic_lcwra_element",
    "2026-06-01",
    "2027-06-01",
    "lower_profits_limit",
    "upper_profits_limit",
    "2024-06-01",
    "2025-06-01",
    "2025-01-01",
    "personal_pension_contributions_tax",
    "uk_higher_threshold",
    "uk_additional_threshold",
    "dividend_higher_threshold",
    "dividend_additional_threshold",
]

observations = st.recursive(
    st.none()
    | st.booleans()
    | st.floats(allow_nan=True)
    | st.integers()
    # JSON integers parse exactly, so values beyond float range are legal.
    | st.integers(min_value=10**308, max_value=10**400)
    | st.text(max_size=4),
    lambda children: (
        st.lists(children, max_size=3)
        | st.dictionaries(st.sampled_from(KEYS), children, max_size=4)
    ),
    max_leaves=12,
)


@settings(max_examples=400, deadline=None)
@given(st.sampled_from(sorted(diagnose.DEFECT_PREDICATES)), observations)
def test_predicates_are_total(identifier, observation):
    record = {"id": identifier, "evidence": {}, "observation": observation}
    assert diagnose.defect_status(record) in diagnose.STATUSES


def test_property_keys_reach_every_predicate_input():
    """The generated keys cover every key a predicate reads, so the totality
    property exercises each predicate past its first shape check."""
    source = Path(diagnose.__file__).read_text()
    start = source.index("def _close(")
    body = source[start : source.index("DEFECT_PREDICATES = {")]
    read = set(re.findall(r'"([0-9a-z_-]+)"', body)) - set(diagnose.STATUSES)
    generated = set(KEYS)
    assert read <= generated, sorted(read - generated)


records = st.fixed_dictionaries(
    {"id": st.sampled_from(sorted(diagnose.DEFECT_PREDICATES)) | observations},
    optional={
        "evidence": observations,
        "supporting_evidence": observations,
        "absent_variables": observations,
        "observation": observations,
    },
)


@settings(max_examples=400, deadline=None)
@given(records)
def test_status_is_total_over_malformed_records(record):
    assert diagnose.defect_status(record) in diagnose.STATUSES


def test_integers_beyond_float_range_are_inconclusive():
    huge = 10**400
    cases = {
        "private_school_vat_current_law_lever_zero": {
            "2025-01-01": 0,
            "2025-06-01": huge,
            "2026-06-01": 0,
        },
        "cgt_main_rate_commencement": {
            "2024-10-30": {"basic": huge},
            "2025-04-06": {"basic": 0},
        },
        "uc_lcwra_protection_stops_at_2030": {
            "annual_synthetic_lcwra_element": {"2029": [huge], "2030": [0]}
        },
        "employer_nics_state_pension_age_exemption": {
            "ni_class_1_employer": [huge, 0.5]
        },
    }
    for identifier, observation in cases.items():
        record = {"id": identifier, "evidence": {}, "observation": observation}
        assert diagnose.defect_status(record) == "inconclusive", identifier
