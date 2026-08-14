"""The mode-3 case-diff schema (#41, shared with taxsim-cases per #5):
the UK battery validates, ids are unique and country-prefixed, cases stay
inputs-only, and the classifier's closed vocabulary fails loudly."""

import json
from pathlib import Path

import pytest

from scorecard_db.case_diffs import (
    DEFAULT_TOLERANCES,
    CaseResult,
    CaseSpec,
    DiffClassification,
    Oracle,
    VariableClass,
    classify,
    load_battery,
)

BATTERY = Path(__file__).parent.parent / "sources/ukmod-cases/battery/cases.json"


def case_kwargs(**kw):
    base = dict(
        case_id="uk-test-case",
        description="test",
        policy_year=2026,
        country="UK",
        household={
            "people": {"adult_1": {"age": 30}},
            "benefit_units": [{"adults": ["adult_1"], "children": []}],
            "tenure": "rented_social",
            "rent": 6240,
        },
        expected_focus=["universal_credit"],
    )
    base.update(kw)
    return base


class TestBattery:
    def test_loads_and_validates(self):
        cases = load_battery(BATTERY)
        assert 12 <= len(cases) <= 16
        assert all(isinstance(c, CaseSpec) for c in cases)

    def test_unique_ids(self):
        cases = load_battery(BATTERY)
        ids = [c.case_id for c in cases]
        assert len(ids) == len(set(ids))

    def test_uk_battery_shape(self):
        for c in load_battery(BATTERY):
            assert c.country == "UK"
            assert c.case_id.startswith("uk-")
            assert c.policy_year == 2026
            assert c.rationale  # every case explains itself

    def test_battery_is_inputs_only(self):
        # No case embeds expected output values (SCHEMA.md doctrine).
        raw = json.loads(BATTERY.read_text())
        for entry in raw["cases"]:
            assert set(entry) <= {
                "case_id",
                "description",
                "policy_year",
                "country",
                "household",
                "expected_focus",
                "rationale",
            }

    def test_focus_coverage(self):
        focus = {v for c in load_battery(BATTERY) for v in c.expected_focus}
        assert {
            "universal_credit",
            "income_tax",
            "national_insurance",
            "child_benefit",
            "pension_credit",
            "benefit_cap",
            "scottish_child_payment",
            "carers_allowance",
        } <= focus

    def test_duplicate_ids_rejected(self, tmp_path):
        raw = json.loads(BATTERY.read_text())
        raw["cases"].append(dict(raw["cases"][0]))
        p = tmp_path / "cases.json"
        p.write_text(json.dumps(raw))
        with pytest.raises(ValueError, match="duplicate case_ids"):
            load_battery(p)

    def test_unknown_case_key_rejected(self, tmp_path):
        raw = json.loads(BATTERY.read_text())
        raw["cases"][0]["expected_value"] = 123.0
        p = tmp_path / "cases.json"
        p.write_text(json.dumps(raw))
        with pytest.raises(ValueError, match="unknown keys"):
            load_battery(p)


class TestCaseSpec:
    def test_unknown_country_rejected(self):
        with pytest.raises(ValueError, match="unknown country"):
            CaseSpec(**case_kwargs(country="FR"))

    def test_country_prefix_enforced(self):
        with pytest.raises(ValueError, match="prefixed"):
            CaseSpec(**case_kwargs(case_id="single-unemployed"))

    def test_unknown_person_key_rejected(self):
        kw = case_kwargs()
        kw["household"]["people"]["adult_1"]["wages"] = 1000
        with pytest.raises(ValueError, match="unknown keys"):
            CaseSpec(**kw)

    def test_unassigned_person_rejected(self):
        kw = case_kwargs()
        kw["household"]["people"]["adult_2"] = {"age": 40}
        with pytest.raises(ValueError, match="exactly once"):
            CaseSpec(**kw)

    def test_owner_with_rent_rejected(self):
        kw = case_kwargs()
        kw["household"]["tenure"] = "owned_outright"
        with pytest.raises(ValueError, match="no rent"):
            CaseSpec(**kw)

    def test_missing_age_rejected(self):
        kw = case_kwargs()
        kw["household"]["people"]["adult_1"] = {"employment_income": 1000}
        with pytest.raises(ValueError, match="age"):
            CaseSpec(**kw)

    def test_empty_focus_rejected(self):
        with pytest.raises(ValueError, match="expected_focus"):
            CaseSpec(**case_kwargs(expected_focus=[]))


class TestClassify:
    def test_exact(self):
        assert classify(100.0, 100.0, VariableClass.CURRENCY) == (
            DiffClassification.MATCH_EXACT
        )

    def test_within_tolerance(self):
        # 52 x GBP 0.01 = 0.52/year currency tolerance.
        assert classify(100.0, 100.52, VariableClass.CURRENCY) == (
            DiffClassification.MATCH_WITHIN_TOLERANCE
        )

    def test_above_tolerance_defaults_unclassified(self):
        assert classify(100.0, 100.53, VariableClass.CURRENCY) == (
            DiffClassification.UNCLASSIFIED
        )

    def test_bool_exact_only(self):
        assert classify(1.0, 1.0, VariableClass.BOOLEAN) == (
            DiffClassification.MATCH_EXACT
        )
        assert classify(1.0, 0.0, VariableClass.BOOLEAN) == (
            DiffClassification.UNCLASSIFIED
        )

    def test_null_sides(self):
        assert classify(None, 5.0, VariableClass.CURRENCY) == (
            DiffClassification.PE_GAP
        )
        assert classify(5.0, None, VariableClass.CURRENCY) == (
            DiffClassification.POLICY_SCOPE_MISMATCH
        )

    def test_unknown_variable_class_rejected(self):
        with pytest.raises(ValueError):
            classify(1.0, 1.0, "percentage")

    def test_missing_tolerance_rejected(self):
        with pytest.raises(ValueError, match="no tolerance"):
            classify(1.0, 2.0, VariableClass.CURRENCY, tolerance_table={})

    def test_default_tolerances_closed(self):
        assert set(DEFAULT_TOLERANCES) == set(VariableClass)


class TestCaseResult:
    def result_kwargs(self, **kw):
        base = dict(
            case_id="uk-uc-single-unemployed",
            variable="universal_credit",
            pe_value=4796.48,
            oracle_value=4796.52,
            oracle="ukmod",
            engine_version="policyengine-uk 2.0.0",
            oracle_version="UKMOD B2026.08",
            computed_at="2026-08-14T12:00:00Z",
            classification="match_within_tolerance",
            abs_diff=0.04,
        )
        base.update(kw)
        return base

    def test_valid_row(self):
        r = CaseResult(**self.result_kwargs())
        assert r.oracle is Oracle.UKMOD
        assert r.classification is DiffClassification.MATCH_WITHIN_TOLERANCE

    def test_unknown_oracle_rejected(self):
        with pytest.raises(ValueError):
            CaseResult(**self.result_kwargs(oracle="euromod-lite"))

    def test_unknown_classification_rejected(self):
        with pytest.raises(ValueError):
            CaseResult(**self.result_kwargs(classification="close_enough"))

    def test_abs_diff_must_be_consistent(self):
        with pytest.raises(ValueError, match="abs_diff"):
            CaseResult(**self.result_kwargs(abs_diff=1.0))

    def test_null_pe_value_requires_pe_gap(self):
        with pytest.raises(ValueError, match="pe_gap"):
            CaseResult(**self.result_kwargs(pe_value=None, abs_diff=None))
        r = CaseResult(
            **self.result_kwargs(pe_value=None, abs_diff=None, classification="pe_gap")
        )
        assert r.classification is DiffClassification.PE_GAP

    def test_null_oracle_value_requires_scope_mismatch(self):
        with pytest.raises(ValueError, match="policy_scope_mismatch"):
            CaseResult(**self.result_kwargs(oracle_value=None, abs_diff=None))

    def test_match_exact_requires_identity(self):
        with pytest.raises(ValueError, match="match_exact"):
            CaseResult(**self.result_kwargs(classification="match_exact"))
