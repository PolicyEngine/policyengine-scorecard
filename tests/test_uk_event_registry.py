"""Exact source-row/GBP coverage and authored fiscal-event world contracts."""

from __future__ import annotations

import copy
import json
from decimal import Decimal
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from pipeline import build_uk_event_registry as registry

ROOT = Path(__file__).resolve().parent.parent


def row(identity, value, fy="2024-25", classification="partial"):
    return {
        "source_row_id": identity,
        "value_gbp_decimal": str(value),
        "value_gbp": float(value),
        "fy": fy,
        "tax_head": "Income tax",
        "metric": "revenue_change",
        "classification": classification,
    }


@pytest.mark.parametrize(
    "title, program",
    [
        ("Savings: Adult ISAs and Junior ISAs", "savings"),
        ("Individual Savings Accounts: subscription limits", "savings"),
        ("Help to Save: extend the scheme", "savings"),
        ("VAT: revise a sector rate", "indirect_tax"),
        ("NICs: revise a contribution threshold", "tax_benefit"),
        ("Universal Credit: managed migration", "welfare"),
    ],
)
def test_gap_keywords_keep_standalone_acronyms_and_policy_phrases(title, program):
    assert registry.gap_reason(title, [row("one", "0")])[2] == program


@pytest.mark.parametrize(
    "title, program",
    [
        (
            "Universal Credit: Amending Severe Disability Premium transitional protection regulations",
            "welfare",
        ),
        (
            "Home office fees: increase in visa fees and immigration health surcharge",
            "other",
        ),
        ("DWP: employment programme for disabled people", "other"),
        ("Increased capacity for processing disability benefits", "welfare"),
        (
            "Support for Local Government: capitalisation directions and precept flexibilities",
            "other",
        ),
        (
            "Private Intermittent Securities and Capital Exchange System (PISCES): Exempt transfers of shares from Stamp Taxes on Shares",
            "other",
        ),
        ("Technical adjustment to a transaction rule", "other"),
    ],
)
def test_gap_keywords_do_not_match_inside_unrelated_words(title, program):
    assert registry.gap_reason(title, [row("one", "0")])[2] == program


@pytest.mark.parametrize(
    "acronym, program",
    [
        ("ISA", "savings"),
        ("ISAs", "savings"),
        ("VAT", "indirect_tax"),
        ("NIC", "tax_benefit"),
        ("NICs", "tax_benefit"),
    ],
)
@given(
    prefix=st.text(alphabet="qxz", min_size=1, max_size=20),
    suffix=st.text(alphabet="qxz", min_size=1, max_size=20),
)
@settings(deadline=None)
def test_embedded_acronyms_never_select_their_gap_category(
    acronym, program, prefix, suffix
):
    assert (
        registry.gap_reason(f"{prefix}{acronym}{suffix}", [row("one", "0")])[2]
        != program
    )


@pytest.mark.parametrize("head", ["Scottish AME (capital) ", " Scottish AME (current)"])
def test_public_budget_scope_lookup_preserves_padded_source_labels(head):
    source = {**row("one", "0"), "tax_head": head}
    assert registry.is_non_household_head(head)
    classification, reason, program, _ = registry.gap_reason(
        "Capital Investment: growth-enhancing investment and defence innovation",
        [source],
    )
    assert classification == "out_of_household_scope"
    assert program == "scope"
    assert "public-budget" in reason
    assert source["tax_head"] == head


def test_send_accounts_scope_does_not_generalize_other_ame_cash_payments():
    source = {**row("one", "0"), "tax_head": "Other AME (current)"}
    classification, reason, _, _ = registry.gap_reason(
        "Special Education Needs and Disabilities: Reduction in Local Authority SEND deficits as a result of additional DEL funding",
        [source],
    )
    assert classification == "out_of_household_scope"
    assert "local-authority SEND deficits" in reason
    assert (
        registry.gap_reason("Cash payment to eligible households", [source])[0]
        == "not_expressible"
    )
    assert (
        registry.gap_reason(
            "Special Education Needs and Disabilities: Household disability grant paid directly to eligible families",
            [source],
        )[0]
        == "not_expressible"
    )


def test_registry_search_metadata_does_not_depend_on_engine_mapping_order(monkeypatch):
    source = {
        **row("one", "0"),
        "title": "Transaction mechanism",
        "fiscal_event": "Audit Event",
    }
    monkeypatch.setattr(registry, "source_rows", lambda _: [source])
    parameters = {"gov.z.transaction": 0, "gov.a.transaction": 1}
    variables = {"z_transaction": {}, "a_transaction": {}}
    forward = registry.build_registry("audit_event", parameters, variables, None)
    reverse = registry.build_registry(
        "audit_event",
        dict(reversed(list(parameters.items()))),
        dict(reversed(list(variables.items()))),
        None,
    )
    assert registry.canonical_bytes(forward) == registry.canonical_bytes(reverse)


@given(st.lists(st.integers(-(10**12), 10**12), min_size=1, max_size=80), st.data())
@settings(deadline=None)
def test_accounting_preserves_rows_and_signed_and_absolute_pounds(values, data):
    rows = [
        row(str(i), Decimal(v) / 100, f"{2024 + i % 3}-{str(2025 + i % 3)[-2:]}")
        for i, v in enumerate(values)
    ]
    classes = data.draw(
        st.lists(
            st.sampled_from(registry.CLASSES), min_size=len(rows), max_size=len(rows)
        )
    )
    measures = []
    for cls in registry.CLASSES:
        classified = [
            {**r, "classification": c} for r, c in zip(rows, classes) if c == cls
        ]
        measures.append({"classification": cls, "source_rows": classified})
    account = registry.accounting(rows, measures)
    assert account["rows_in"] == account["rows_classified"] == len(rows)
    assert account["net_gbp_in_decimal"] == account["net_gbp_classified_decimal"]
    assert (
        account["absolute_gbp_in_decimal"] == account["absolute_gbp_classified_decimal"]
    )
    assert sum(v["rows"] for v in account["by_class"].values()) == len(rows)
    assert sum(
        Decimal(v["net_gbp_decimal"]) for v in account["by_class"].values()
    ) == sum(Decimal(v) / 100 for v in values)


@pytest.mark.parametrize(
    "change", ["duplicate", "drop", "change_value", "change_head", "invalid_class"]
)
def test_accounting_rejects_lost_duplicated_or_changed_source_cells(change):
    rows = [row("one", "100"), row("two", "-100")]
    measures = [{"classification": "partial", "source_rows": copy.deepcopy(rows)}]
    if change == "duplicate":
        measures[0]["source_rows"].append(copy.deepcopy(rows[0]))
    elif change == "drop":
        measures[0]["source_rows"].pop()
    elif change == "change_value":
        measures[0]["source_rows"][0]["value_gbp_decimal"] = "99"
    elif change == "change_head":
        measures[0]["source_rows"][0]["tax_head"] = "NICs"
    else:
        measures[0]["source_rows"][0]["classification"] = "guessed"
    with pytest.raises(ValueError, match="accounting"):
        registry.accounting(rows, measures)


def test_pound_account_does_not_round_small_cells_beside_large_cancelling_cells():
    rows = [
        row("big", "10000000000000000000000000000"),
        row("small", "0.0000000000000000000001"),
        row("negative", "-10000000000000000000000000000"),
    ]
    measures = [{"classification": "partial", "source_rows": list(reversed(rows))}]
    actual = registry.accounting(rows, measures)
    assert Decimal(actual["net_gbp_in_decimal"]) == Decimal("0.0000000000000000000001")
    assert actual["net_gbp_in_decimal"] == actual["net_gbp_classified_decimal"]


@pytest.mark.parametrize("event_slug", registry.EVENTS)
def test_every_event_retains_every_harvested_row_and_pound_exactly_once(event_slug):
    p = ROOT / "data/uk/events" / f"{event_slug}_measures.json"
    document = json.loads(p.read_text())
    original = registry.source_rows(event_slug)
    assert registry.accounting(original, document["measures"]) == document["accounting"]
    assert len({m["measure_key"] for m in document["measures"]}) == len(
        document["measures"]
    )
    for measure in document["measures"]:
        assert measure["classification"] in registry.CLASSES
        assert measure["name_search"]["searched"] == [
            "full_parameter_tree",
            "full_variable_list",
        ]
        assert "population_vintage" in measure["divergence_axes"]
        if measure["classification"] in {"partial", "not_expressible"}:
            assert measure["pe_gap"] and measure["missing_legs"]
        if measure["classification"] == "expressible":
            assert (
                measure.get("pe_baseline_modifier")
                or measure.get("pe_reform_delta")
                or measure.get("package_of_registry_measures")
            )
        for source in measure["source_rows"]:
            assert source["sign_convention"] == "positive_gain_to_exchequer"
            if source["tax_head"] in registry.NON_HOUSEHOLD_HEADS:
                assert source["classification"] == "out_of_household_scope"


def test_spending_proposed_metric_is_preserved_as_exchequer_impact():
    rows = registry.source_rows("autumn_budget_2024")
    spending = [r for r in rows if r["head_kind"] == "spending"]
    assert len(spending) == 570
    assert {r["metric"] for r in spending} == {"exchequer_impact"}
    tax = [r for r in rows if r["head_kind"] == "tax"]
    assert len(tax) == 564
    assert {r["metric"] for r in tax} == {"revenue_change"}


def test_source_events_are_not_restricted_to_the_five_pilot_events():
    rows = registry.source_rows("autumn_budget_2025")
    assert rows
    assert {r["fiscal_event"] for r in rows} == {"Autumn Budget 2025"}
    assert "autumn_budget_2025" not in registry.EVENTS


def test_unknown_source_event_is_rejected_instead_of_an_empty_registry():
    with pytest.raises(ValueError, match="has no source rows"):
        registry.source_rows("not_an_obr_fiscal_event")


def test_autumn_budget_2024_employer_package_is_partial_and_not_duplicated():
    p = ROOT / "data/uk/events/autumn_budget_2024_measures.json"
    d = json.loads(p.read_text())
    m = next(
        m for m in d["measures"] if m["measure_key"].endswith("__employer_nics_package")
    )
    assert m["classification"] == "partial"
    assert "Employment Allowance" in m["pe_gap"]
    assert m["pe_baseline_modifier"][
        "gov.hmrc.national_insurance.class_1.rates.employer"
    ] == {"2025-01-01": 0.138}
    assert all(
        r["classification"] == "out_of_household_scope"
        for r in m["source_rows"]
        if r["tax_head"] == "Corporation tax (onshore)"
    )


def test_calendar_year_rule_accounts_earlier_fys_without_running_them():
    d = json.loads(
        (ROOT / "data/uk/events/spring_budget_2023_measures.json").read_text()
    )
    assert "2022-23" in d["accounting"]["by_fy"]
    assert 2022 not in d["calendar_years"]
    assert d["calendar_years"] == [2023, 2024, 2025, 2026, 2027]


def test_as2023_reversal_matches_measured_processed_fiscal_parameters():
    d = json.loads(
        (ROOT / "data/uk/events/autumn_statement_2023_measures.json").read_text()
    )
    m = next(
        m
        for m in d["measures"]
        if m["measure_key"].endswith("__class_1_employee_nics_main_rate_cut_2p")
    )
    rates = m["pe_baseline_modifier"][
        "gov.hmrc.national_insurance.class_1.rates.employee.main"
    ]
    probe = json.loads(
        (ROOT / "tests/fixtures/uk_replay_processed_employee_nics.json").read_text()
    )
    assert probe["engine_version"] == "2.89.2"
    assert probe["parameter"] in m["engine_baseline_by_year"]["2024"]
    assert m["engine_baseline_by_year"]["2024"][probe["parameter"]] == 0.08
    assert probe["observed_values_list_2024"] == [
        {"instant_str": "2024-01-01", "value": 0.08}
    ]
    # Compare against the measured processed engine, not a raw-YAML
    # January/April schedule that the fiscal-year conversion discards.
    for date, certified_rate in probe["observed_current_law_2024"].items():
        reversed_rate = rates[max(k for k in rates if k <= date)]
        assert reversed_rate - certified_rate == pytest.approx(0.02)
    assert "raw January-March rates do not survive" in m["note"]


def test_annual_allowance_modifier_covers_january_2023_lookup():
    m = registry.authored_construction(
        "spring_budget_2023", "Annual Allowance (AA): increase", None
    )
    assert all(
        list(schedule) == ["2023-01-01"]
        for schedule in m["pe_baseline_modifier"].values()
    )


def test_standard_allowance_counterfactual_matches_legislated_cpi_anchor():
    def resolve(path, date):
        if path == "gov.benefit_uprating_cpi":
            return {
                "2026-04-06": 413.74,
                "2027-04-06": 422.0148,
                "2028-04-06": 430.455096,
                "2029-04-06": 439.06419792,
            }[date]
        return 400.14

    m = registry.authored_construction(
        "spring_statement_2025", "Universal Credit Standard Allowance:", resolve
    )
    schedule = m["pe_baseline_modifier"][
        "gov.dwp.universal_credit.standard_allowance.amount.SINGLE_OLD"
    ]
    assert schedule["2026"] == 415.35
    assert schedule["2027"] == round(400.14 * 1.038 * 1.02, 2)
    assert "policyengine-uk#2239" in m["note"]


@pytest.mark.parametrize(
    "event,title,path,value",
    [
        (
            "autumn_statement_2023",
            "Local Housing Allowance (LHA): set to the 30th percentile from April 2024",
            "gov.dwp.LHA.freeze",
            True,
        ),
        (
            "autumn_statement_2023",
            "National Insurance contributions (NICs): abolish Class 2 self-employed NICs liability from April 2024",
            "gov.hmrc.national_insurance.class_2.flat_rate",
            3.70,
        ),
    ],
)
def test_new_reversals_are_executable_and_explicit_about_scope(
    event, title, path, value
):
    m = registry.authored_construction(event, title, None)
    assert m["classification"] == "partial"
    assert m["pe_baseline_modifier"][path] == {"2024-01-01": value}
    assert m["heads"] and m["missing_legs"]
    if path.endswith("class_2.flat_rate"):
        assert m["pe_baseline_modifier"][
            "gov.hmrc.national_insurance.class_2.small_profits_threshold"
        ] == {"2024-01-01": 12570}


def test_childcare_old_caps_preserve_subsequent_certified_uprating():
    def resolve(path, date):
        base = 951 if path.endswith(".1") else 1630
        return base * 1.05 ** (int(date[:4]) - 2023)

    m = registry.authored_construction(
        "spring_budget_2023",
        "DWP: increase the maximum support available in Universal Credit for childcare costs",
        resolve,
    )
    spec = m["pe_baseline_modifier"]
    assert spec["gov.dwp.universal_credit.elements.childcare.cap.1"]["2023"] == 646.35
    assert spec["gov.dwp.universal_credit.elements.childcare.cap.2"]["2023"] == 1108.04
    assert spec["gov.dwp.universal_credit.elements.childcare.cap.1"]["2024"] == round(
        646.35 * 1.05, 2
    )
    assert "June2023" in m["missing_legs"][0]
