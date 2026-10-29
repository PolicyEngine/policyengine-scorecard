"""The Autumn Budget 2026 measure registry (#230).

data/uk/ab2026_measures.json is the key space every AB2026 claim carries in
measure_key, and the computability verdict that decides whether a producer's
row gets a PolicyEngine counterpart or a pe_gap finding. These tests pin the
rules the port depends on: every Table 6.1 line once under a key that cannot
move, every gap with a computed name search at the Budget-day engine, every
dashboard measure tied to a receipt by hash, packages that are exactly the
union of their legs, and an outcome for every pre-event key.
"""

import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

import pytest

from pipeline import ab2026_measure_keys as K
from pipeline.validate_budget_2026_registry import key_prefix, load, validate

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "data" / "uk" / "ab2026_measures.json"
REG = load(PATH)
BY_KEY = {m["measure_key"]: m for m in REG["measures"]}
PIN = "2.151.0"

# The seven measures the UK Autumn Budget dashboard ran on Budget day, by
# Table 6.1 line and dashboard id.
DASHBOARD = {
    1: "household_energy_payment_2026",
    2: "domestic_electricity_zero_vat",
    3: "fuel_duty_rise_deferral",
    7: "carers_allowance_earnings_taper",
    15: "trading_allowance_raise",
    52: "state_pension_income_tax_protection",
    61: "property_income_rates_up",
}


def by_line(line):
    return BY_KEY[K.key(line)]


def test_registry_validates():
    assert validate(REG) == len(REG["measures"])
    assert REG["fiscal_event"] == "autumn_budget_2026"
    assert key_prefix(REG) == "ab2026__"


def test_every_table_61_line_is_registered_once_under_its_written_out_key():
    lines = sorted(m["table_61_line"] for m in REG["measures"] if "table_61_line" in m)
    assert lines == list(range(1, 99))
    for line, slug in K.TABLE_61.items():
        m = BY_KEY[K.PREFIX + slug]
        assert m["table_61_line"] == line, slug


def test_table_62_maps_to_table_61_measures_except_sovereign_ai():
    """Table 6.2 lines are financial transactions of Table 6.1 measures; only
    line 4 has no Table 6.1 line and so is a measure of its own."""
    own = [m for m in REG["measures"] if "table_62_line" in m]
    assert [m["table_62_line"] for m in own] == [4]
    for line, slug in K.TABLE_62.items():
        assert K.PREFIX + slug in BY_KEY, (line, slug)


def test_keys_are_unique_and_disjoint_from_the_pre_event_registry():
    keys = [m["measure_key"] for m in REG["measures"]]
    assert len(keys) == len(set(keys))
    pre = load(ROOT / "data" / "uk" / "budget_2026_measures.json")
    assert not set(keys) & {m["measure_key"] for m in pre["measures"]}


def test_every_pre_event_key_has_an_outcome_that_names_real_keys():
    pre = load(ROOT / "data" / "uk" / "budget_2026_measures.json")
    outcomes = REG["pre_event_outcomes"]
    assert set(outcomes) == {m["measure_key"] for m in pre["measures"]}
    for k, text in outcomes.items():
        for named in re.findall(r"\(?(ab2026__[a-z0-9_]+)\)?", text):
            assert named in BY_KEY, (k, named)


def test_every_gap_has_a_computed_name_search_at_the_pin_and_somewhere_to_go():
    for m in REG["measures"]:
        if m["computability"] != "not_expressible":
            continue
        k = m["measure_key"]
        assert re.match(r"https://github\.com/PolicyEngine/", m["action_link"]), k
        assert m["pe_reform_delta"] is None, k
        assert m["why"].strip(), k
        ns = m["name_search"]
        assert "Parameters:" in ns and "Variables:" in ns and "VARIABLE" in ns, k
        assert f"policyengine-uk {PIN}" in ns, k
        assert bool(m.get("out_of_model_scope")) != bool(
            m.get("policyengine_uk_development_item")
        ), k


def test_development_items_name_their_upstream_item():
    devs = [m for m in REG["measures"] if m.get("policyengine_uk_development_item")]
    assert len(devs) == REG["triage"]["policyengine_uk_development_item"]
    for m in devs:
        assert m["upstream_item"].startswith("policyengine-uk:"), m["measure_key"]


def test_the_triage_counts_are_computed_from_the_measures():
    t = REG["triage"]
    ms = REG["measures"]
    for verdict in ("expressible", "partial", "not_expressible"):
        assert t[verdict] == sum(m["computability"] == verdict for m in ms), verdict
    assert t["executed_by_dashboard"] == len(DASHBOARD)
    assert t["executed_by_dashboard"] == sum(
        m.get("construction") == "executed_by_dashboard" for m in ms
    )
    assert t["out_of_model_scope"] == sum(bool(m.get("out_of_model_scope")) for m in ms)
    assert t["announced"] == sum(m["reported_status"] == "announced" for m in ms)


def test_the_seven_dashboard_measures_execute_by_receipt_at_the_budget_day_engine():
    run = REG["engine_pin"]["budget_day_runs"]
    assert REG["engine_pin"]["policyengine_uk"] == PIN
    assert run["certified_for_model_version"] == PIN
    for line, dash_id in DASHBOARD.items():
        m = by_line(line)
        assert m["computability"] == "expressible", line
        assert m["construction"] == "executed_by_dashboard", line
        assert m["dashboard_measure_id"] == dash_id, line
        rc = m["pe_modifier"]["receipt"]
        assert rc["path"].startswith(f"public/data/artifacts/{dash_id}/"), line
        for field in (
            "policyengine",
            "certified_for_model_version",
            "dataset_revision",
            "dataset_sha256",
        ):
            assert rc[field] == run[field], (line, field)


def test_the_remaining_expressible_lines_are_deltas_on_current_law():
    """Savings rates (line 62, off the dashboard release) and the BADR limit
    (line 60) have no receipt; they are parameter deltas the engine resolves."""
    for line in (60, 62):
        m = by_line(line)
        assert m["computability"] == "expressible", line
        assert m["construction"] == "delta_on_current_law", line
        assert m["pe_reform_delta"], line
        assert "pe_modifier" not in m, line


def test_the_bus_cap_is_partial_because_its_pre_measure_world_is_unknown():
    m = by_line(4)
    assert m["computability"] == "partial"
    assert m["intended_construction"] == "reversal_on_certified_world"
    assert "construction" not in m
    hist = m["engine_parameter_history"]["gov.dft.bus.fares.cap"]
    assert hist["2027-01-01"] == 2
    assert "bus_fares_gap.json" in m["missing"]


def test_packages_are_exactly_their_legs():
    tables = {
        "ab2026__package_total_policy_decisions": set(range(1, 99)),
        "ab2026__package_household_energy_vat_and_fuel_duty": {1, 2, 3},
        "ab2026__package_policyengine_seven": set(DASHBOARD),
    }
    for k, lines in tables.items():
        assert set(BY_KEY[k]["package_of"]) == {K.key(n) for n in lines}, k
    tax = set(BY_KEY["ab2026__package_total_tax_policy_decisions"]["package_of"])
    spend = set(BY_KEY["ab2026__package_total_spending_policy_decisions"]["package_of"])
    assert not tax & spend
    assert tax | spend == set(
        BY_KEY["ab2026__package_total_policy_decisions"]["package_of"]
    )
    for leg in tax:
        assert BY_KEY[leg]["table_61_head"] == "Tax", leg
    for leg in spend:
        assert BY_KEY[leg]["table_61_head"] == "Spend", leg


def test_a_package_is_expressible_only_when_every_leg_is():
    for m in REG["measures"]:
        if m.get("construction") != "package_of_registry_measures":
            continue
        legs = [BY_KEY[leg] for leg in m["package_of"]]
        expressible = [
            leg["measure_key"] for leg in legs if leg["computability"] == "expressible"
        ]
        if m["computability"] == "expressible":
            assert len(expressible) == len(legs), m["measure_key"]
        else:
            assert m["computability"] == "partial", m["measure_key"]
            assert sorted(m["expressible_legs"]) == sorted(expressible), m[
                "measure_key"
            ]


def test_the_combined_receipt_covers_the_seven_package():
    m = BY_KEY["ab2026__package_policyengine_seven"]
    assert m["construction"] == "package_of_registry_measures"
    assert m["pe_modifier"]["receipt"]["path"].startswith(
        "public/data/artifacts/combined--"
    )


def test_the_registry_is_regenerated_byte_for_byte():
    """The JSON and REGISTRY_KEYS.md are generated; --check needs the pinned
    engine, so it runs only where its venv exists."""
    py = ROOT / ".venv-pe2151" / "bin" / "python"
    if not py.exists():
        pytest.skip("the policyengine-uk 2.151.0 venv is not installed here")
    out = subprocess.run(
        [str(py), "pipeline/build_ab2026_registry.py", "--check"],
        cwd=ROOT,
        env={**os.environ, "PYTHONPATH": str(ROOT)},
        capture_output=True,
        text=True,
    )
    assert out.returncode == 0, out.stdout + out.stderr


def _dashboard_repo():
    path = Path(
        os.environ.get(
            "UK_BUDGET_DASHBOARD_REPO",
            Path.home() / "PolicyEngine" / "uk-autumn-budget-dashboard-2026",
        )
    )
    return path if (path / ".git").exists() else None


@pytest.mark.parametrize(
    "key",
    sorted(k for k, m in BY_KEY.items() if m.get("pe_modifier")),
)
def test_each_receipt_matches_the_dashboard_commit(key):
    """Hash-check each receipt against the dashboard repository at the pinned
    commit. CI has no checkout of that repository, so this runs where one
    exists (UK_BUDGET_DASHBOARD_REPO, or the default clone path)."""
    repo = _dashboard_repo()
    if repo is None:
        pytest.skip("no uk-autumn-budget-dashboard-2026 checkout")
    rc = BY_KEY[key]["pe_modifier"]["receipt"]
    blob = subprocess.run(
        ["git", "-C", str(repo), "show", f"{rc['commit']}:{rc['path']}"],
        capture_output=True,
        check=True,
    ).stdout
    assert hashlib.sha256(blob).hexdigest() == rc["receipt_file_sha256"]
    receipt = json.loads(blob)
    ex = receipt["execution_receipt"]
    assert ex["reform"]["reform_sha256"] == rc["reform_sha256"]
    assert ex["reform"]["binding"] == rc["reform_binding"]
    assert receipt["dashboard"]["generated_at"] == rc["generated_at"]
    assert (
        ex["certificate"]["certified_for_model_version"]
        == rc["certified_for_model_version"]
    )
    assert ex["data"]["dataset_revision"] == rc["dataset_revision"]
    assert ex["data"]["dataset_sha256"] == rc["dataset_sha256"]
