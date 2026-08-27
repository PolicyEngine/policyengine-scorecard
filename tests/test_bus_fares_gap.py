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
    # No bus-TRANSPORT parameter exists. The one parameter whose name
    # contains "bus" is gov.hmrc.business_rates — a substring false
    # positive of the search pattern, pinned here so a future reader
    # does not mistake it for a bus lever.
    bus_named = [
        h for h in search["parameter_hits"] if "bus" in h.split(".")[-1].lower()
    ]
    assert bus_named == ["gov.hmrc.business_rates"]
    assert not any(h.startswith("gov.dft.bus") for h in search["parameter_hits"])


def test_validate_rejects_a_parameter_only_search():
    bad = json.loads(json.dumps(REG))
    del bad["name_search"]["variable_hits"]
    with pytest.raises(ValueError, match="parameter-only search"):
        validate(bad)


def test_gov_dft_has_rail_but_no_bus():
    assert sorted(REG["name_search"]["gov_dft_children"]) == ["rail", "spending"]


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


def test_the_nearest_lever_is_named_and_ruled_out():
    """Otherwise a reader finds it and assumes nobody looked."""
    lever = REG["nearest_lever_and_why_it_does_not_work"]
    assert lever["path"] == "gov.contrib.policyengine.economy.transport"
    assert lever["value_2026"] == 0
    assert "not bus-specific" in lever["why_not"]


def test_validate_rejects_an_unruled_out_lever():
    bad = json.loads(json.dumps(REG))
    bad["nearest_lever_and_why_it_does_not_work"]["why_not"] = ""
    with pytest.raises(ValueError, match="assumes it was missed"):
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
