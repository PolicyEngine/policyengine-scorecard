"""The bus fare cap gap registry (#106).

What is pinned here is that the gap is EARNED: backed by a search of
both parameters and variables, honest about what the engine does have,
and specific about what would close it.
"""

import json

import pytest

from pipeline.validate_bus_fares_gap import load, validate

REG = load()


def test_registry_validates():
    assert validate(REG) == "ab2026__bus_fare_cap"


def test_the_search_covers_variables_not_only_parameters():
    """The first pass at this measure searched only the parameter tree
    and concluded bus was absent. bus_subsidy_spending is a VARIABLE."""
    search = REG["name_search"]
    assert "bus_subsidy_spending" in search["variable_hits"]
    assert "VARIABLES as well as PARAMETERS" in REG["search_rule"]
    # At 2.89.2 the only "bus" parameter was gov.hmrc.business_rates, a
    # substring false positive. At 2.92.0 gov.dft.bus exists too. Both
    # are pinned: the false positive so nobody mistakes it for a lever,
    # the real node because it IS bus and still is not a price.
    bus_named = sorted(
        h for h in search["parameter_hits"] if "bus" in h.split(".")[-1].lower()
    )
    assert bus_named == ["gov.dft.bus", "gov.hmrc.business_rates"]


def test_validate_rejects_a_parameter_only_search():
    bad = json.loads(json.dumps(REG))
    del bad["name_search"]["variable_hits"]
    with pytest.raises(ValueError, match="parameter-only search"):
        validate(bad)


def test_gov_dft_gained_a_bus_node_and_it_is_still_not_a_lever():
    """v1 recorded gov.dft as rail + spending. At 2.92.0 there is a bus
    node — and it holds an ALLOCATION weight, not a price."""
    assert sorted(REG["name_search"]["gov_dft_children"]) == ["bus", "rail", "spending"]
    weight = next(
        l
        for l in REG["nearest_levers_and_why_they_do_not_work"]
        if l["path"].endswith("fare_allocation_weight_by_age")
    )
    assert "not a price" in weight["why_not"]
    assert "2.92.0" in weight["appeared_in"]


def test_every_bus_named_parameter_is_ruled_out_by_name():
    ruled = {l["path"] for l in REG["nearest_levers_and_why_they_do_not_work"]}
    bus_nodes = {
        h for h in REG["name_search"]["parameter_hits"] if h.startswith("gov.dft.bus")
    }
    assert bus_nodes and bus_nodes <= ruled


def test_validate_rejects_an_unaddressed_bus_parameter():
    bad = json.loads(json.dumps(REG))
    bad["name_search"]["parameter_hits"].append("gov.dft.bus.fare_cap")
    with pytest.raises(ValueError, match="never ruled out"):
        validate(bad)


def test_the_stale_evidence_is_logged_not_quietly_rewritten():
    """The verdict survived the engine bump; the evidence behind it did
    not. A gap registry that silently refreshes its own evidence is
    indistinguishable from one nobody re-checked."""
    log = " ".join(REG["corrections_log"])
    assert "2.89.2" in log and "gov.dft.bus" in log
    assert "VERDICT is unchanged" in log


def test_the_registry_says_what_the_engine_DOES_have():
    """A gap registry that omits the present-but-unusable machinery
    overstates itself."""
    bss = REG["what_the_engine_does_have"]["bus_subsidy_spending"]
    assert bss["has_formula"] is False
    assert "dft_subsidy_spending" in bss["feeds"]
    assert "NOT 'PolicyEngine does not do buses'" in bss["note"]


def test_validate_rejects_omitting_the_present_machinery():
    bad = json.loads(json.dumps(REG))
    del bad["what_the_engine_does_have"]["bus_subsidy_spending"]
    with pytest.raises(ValueError, match="overstates the gap"):
        validate(bad)


def test_the_gap_is_a_missing_factorisation_not_a_missing_subject():
    gap = REG["the_gap"]
    assert "missing FACTORISATION" in gap
    assert "rail_usage x gov.dft.rail.fare_index" in gap


def test_the_verdict_turns_on_bus_being_a_pure_input():
    """If bus_subsidy_spending ever gains a formula, the verdict is no
    longer safe — so the registry refuses to record it as anything but
    a pure input."""
    bad = json.loads(json.dumps(REG))
    bad["what_the_engine_does_have"]["bus_subsidy_spending"]["has_formula"] = True
    with pytest.raises(ValueError, match="pure input with no formula IS the gap"):
        validate(bad)


def test_the_nearest_levers_are_named_and_ruled_out():
    """Otherwise a reader finds one and assumes nobody looked."""
    levers = {l["path"]: l for l in REG["nearest_levers_and_why_they_do_not_work"]}
    contrib = levers["gov.contrib.policyengine.economy.transport"]
    assert contrib["value_2026"] == 0
    assert "not bus-specific" in contrib["why_not"]
    for lever in levers.values():
        assert lever["why_not"].strip()


def test_validate_rejects_an_unruled_out_lever():
    bad = json.loads(json.dumps(REG))
    bad["nearest_levers_and_why_they_do_not_work"][0]["why_not"] = ""
    with pytest.raises(ValueError, match="reads as an oversight"):
        validate(bad)


def test_a_gap_carries_an_upstream_item():
    """not_expressible without one is a shrug."""
    up = REG["upstream_item"]
    assert "bus_usage" in up and "gov.dft.bus.fare_index" in up
    assert REG["policyengine_uk_development_item"] is True


def test_validate_rejects_a_gap_with_no_upstream_item():
    bad = json.loads(json.dumps(REG))
    bad["upstream_item"] = ""
    with pytest.raises(ValueError, match="is a shrug"):
        validate(bad)


def test_it_stages_no_value_claims():
    assert "stages NO value claims" in REG["registry_rule"]
    blob = json.dumps(REG)
    for k in ("value", "saving_gbp", "claims", "costing", "revenue_gbp"):
        assert f'"{k}"' not in blob


def test_validate_rejects_a_staged_figure():
    bad = json.loads(json.dumps(REG))
    bad["costing"] = 700_000_000
    with pytest.raises(ValueError, match="belong to their originators"):
        validate(bad)


def test_the_engine_pin_is_derived_not_typed():
    """v1 pinned 2.89.2 — copied from a sibling spec — while the
    searches ran against the installed engine. For a gap registry this
    matters more than elsewhere: the verdict is only as good as the
    engine it was searched in."""
    pin = REG["engine_pin"]
    assert "importlib.metadata" in pin["pin_rule"]
    assert "only as good as the engine it was searched in" in pin["pin_rule"]
