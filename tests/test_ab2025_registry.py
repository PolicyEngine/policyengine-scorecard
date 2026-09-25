"""The Autumn Budget 2025 measure registry (#136).

data/uk/ab2025_measures.json is the key space every AB2025 claim carries in
conditions.measure_key and the computability verdict that decides whether a
producer's row gets a PolicyEngine counterpart or a pe_gap finding. These
tests pin the honesty rules the port depends on: every gap has a computed
name search and somewhere to go, every reversal names the world it executes,
the nine dashboard measures are present, and the keys join the OBR
divergence registry without renames.
"""

import json
import re
from pathlib import Path

import pytest

from pipeline.validate_budget_2026_registry import key_prefix, load, validate

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "data" / "uk" / "ab2025_measures.json"
REG = load(PATH)
BY_KEY = {m["measure_key"]: m for m in REG["measures"]}

DASHBOARD_MEASURES = {
    "ab2025__uc_child_element_remove_two_child_limit",
    "ab2025__fuel_duty_freeze_extension_2026_27",
    "ab2025__personal_tax_thresholds_freeze_to_2031",
    "ab2025__dividend_rates_plus_2pp",
    "ab2025__savings_rates_plus_2pp_and_starter_limit_held",
    "ab2025__property_income_separate_rates",
    "ab2025__student_loans_plan2_threshold_freeze",
    "ab2025__rail_fares_freeze_2026",
    "ab2025__salary_sacrifice_pension_nics_cap_2000",
}


def test_registry_validates():
    assert validate(REG) == len(REG["measures"])
    assert REG["fiscal_event"] == "autumn_budget_2025"
    assert key_prefix(REG) == "ab2025__"


def test_every_table_41_line_is_registered():
    """88 measure lines on HM Treasury's Table 4.1, each once."""
    lines = sorted(m["table_41_line"] for m in REG["measures"] if "table_41_line" in m)
    assert lines == list(range(1, 89))


def test_announced_and_option_keys_are_distinct_spaces():
    for m in REG["measures"]:
        if m["reported_status"] == "announced":
            assert m["measure_key"].startswith("ab2025__")
            assert not m["measure_key"].startswith("ab2025_option__")
        else:
            assert m["reported_status"] == "option_costed_by_others"
            assert m["measure_key"].startswith("ab2025_option__")
            assert m["producers"], m["measure_key"]


def test_every_gap_has_a_computed_name_search_and_somewhere_to_go():
    for m in REG["measures"]:
        if m["computability"] != "not_expressible":
            continue
        k = m["measure_key"]
        assert re.match(r"https://github\.com/PolicyEngine/", m["action_link"]), k
        assert m["pe_reform_delta"] is None, k
        assert m["why"].strip(), k
        # computed, not typed: the search records counts and samples
        ns = m["name_search"]
        assert "Parameters:" in ns and "Variables:" in ns and "VARIABLE" in ns, k
        assert "policyengine-uk 2.89.2" in ns, k
        assert m.get("out_of_model_scope") or m.get(
            "policyengine_uk_development_item"
        ), k


def test_development_items_name_their_upstream_item():
    devs = [m for m in REG["measures"] if m.get("policyengine_uk_development_item")]
    assert len(devs) >= 10
    for m in devs:
        assert m["upstream_item"].startswith("policyengine-uk:"), m["measure_key"]


def test_the_eved_gap_rules_out_the_vehicle_variables_it_found():
    """The bundle counts vehicles; it is fuel type and mileage that are missing.
    A verdict that said 'no vehicle data' would be false at the pin."""
    m = BY_KEY["ab2025__eved_mileage_supplement_electric_and_phev"]
    assert "num_vehicles" in m["name_search"]
    assert m["nearest_variable_and_why_it_does_not_work"]["variable"] == "num_vehicles"
    assert "mileage" in m["why"]


def test_every_reversal_records_the_world_it_executes():
    for m in REG["measures"]:
        if m.get("construction") == "reversal_on_certified_world":
            k = m["measure_key"]
            assert m["pe_baseline_modifier"], k
            assert m["engine_baseline_2026"], k
            assert m["head_variables"], k
            # every modifier path is also a recorded engine baseline path, so
            # --resolve checks the pre-Budget world's paths too
            for path in m["pe_baseline_modifier"]:
                assert path in m["engine_baseline_2026"], (k, path)


def test_the_nine_dashboard_measures_are_present_and_computable():
    for k in DASHBOARD_MEASURES:
        assert k in BY_KEY, k
        assert BY_KEY[k]["computability"] == "expressible", k
        assert BY_KEY[k]["construction"] == "reversal_on_certified_world", k


def test_the_threshold_freeze_states_its_mixed_baseline_honestly():
    """At the pin the income tax thresholds are frozen to 2031 but the NI
    thresholds uprate from April 2028 (class 4 from April 2027): the measure is
    half in the baseline. A registry that called it 'already in baseline'
    would score the NI legs at zero."""
    m = BY_KEY["ab2025__personal_tax_thresholds_freeze_to_2031"]
    assert m["already_in_baseline"] == "income tax legs only"
    assert (
        "gov.hmrc.national_insurance.class_1.thresholds.primary_threshold"
        in m["pe_reform_delta"]
    )
    assert (
        "gov.hmrc.income_tax.allowances.personal_allowance.amount"
        in m["pe_baseline_modifier"]
    )
    assert "NOT frozen" in m["baseline_integrity_note"]


def test_the_uc_rebalancing_names_the_missing_protection():
    m = BY_KEY["ab2025__uc_standard_allowance_and_health_element_rebalancing"]
    assert m["computability"] == "partial"
    assert "claim-start" in m["missing"] or "claim history" in m["missing"].lower()
    assert m["policyengine_uk_development_item"]


def test_obr_divergence_axes_keys_join_without_renames():
    axes = json.loads((ROOT / "data" / "uk" / "obr_divergence_axes.json").read_text())
    pmd_keys = {
        m["obr_pmd_measure_key"]
        for m in REG["measures"]
        if m.get("obr_pmd_measure_key")
    }
    ab2025 = [k for k in axes["measures"] if k.startswith("autumn_budget_2025__")]
    assert ab2025, "the axes registry carries the two-child measure"
    for key in ab2025:
        assert key in pmd_keys, key


def test_the_package_totals_are_partial_and_say_why():
    for k in (
        "ab2025__package_total_policy_decisions",
        "ab2025__package_total_tax_policy_decisions",
        "ab2025__package_total_spending_policy_decisions",
    ):
        m = BY_KEY[k]
        assert m["computability"] == "partial"
        assert m["construction"] == "package_of_registry_measures"
        assert "never compared" in m["missing"]


def test_the_pin_follows_the_certified_bundle():
    bundle = json.loads((ROOT / "data" / "uk" / "certified_bundle.json").read_text())
    pin = REG["engine_pin"]
    assert pin["policyengine_uk"] == "2.89.2"
    assert pin["certified_bundle"]["revision"] == bundle["revision"]
    assert (
        pin["certified_bundle"]["compatible_model_packages"]
        == bundle["compatible_model_packages"]
    )


def test_triage_counts_reconcile():
    t = REG["triage"]
    n = len(REG["measures"])
    assert t["expressible"] + t["partial"] + t["not_expressible"] == n
    assert t["announced"] + t["options"] == n
    assert (
        sum(1 for m in REG["measures"] if m.get("out_of_model_scope"))
        == t["out_of_model_scope"]
    )


def test_validate_rejects_a_gap_with_nowhere_to_go():
    bad = json.loads(json.dumps(REG))
    gap = next(m for m in bad["measures"] if m["computability"] == "not_expressible")
    del gap["action_link"]
    with pytest.raises(ValueError, match="nowhere to go"):
        validate(bad)


def test_validate_rejects_a_reversal_without_its_world():
    bad = json.loads(json.dumps(REG))
    m = next(
        x
        for x in bad["measures"]
        if x.get("construction") == "reversal_on_certified_world"
    )
    del m["pe_baseline_modifier"]
    with pytest.raises(ValueError, match="pe_baseline_modifier"):
        validate(bad)


def test_validate_rejects_a_mis_prefixed_option():
    bad = json.loads(json.dumps(REG))
    m = next(
        x for x in bad["measures"] if x["reported_status"] == "option_costed_by_others"
    )
    m["measure_key"] = "ab2025__" + m["measure_key"].split("__", 1)[1]
    with pytest.raises(ValueError, match="_option__ prefix"):
        validate(bad)
