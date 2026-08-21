"""The mode-3 case-diff schema (#41, shared with taxsim-cases per #5):
the UK battery validates, ids are unique and country-prefixed, cases stay
inputs-only, and the classifier's closed vocabulary fails loudly."""

import json
from pathlib import Path

import pytest

from scorecard_db.case_diffs import (
    BRMA_REGION,
    SCHEMA_VERSION,
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
        assert 12 <= len(cases) <= 20
        assert all(isinstance(c, CaseSpec) for c in cases)

    def test_unique_ids(self):
        cases = load_battery(BATTERY)
        ids = [c.case_id for c in cases]
        assert len(ids) == len(set(ids))

    def test_uk_battery_shape(self):
        for c in load_battery(BATTERY):
            assert c.country == "UK"
            assert c.case_id.startswith("uk-")
            # Every case is a 2026 case now: the two-child family reaches
            # the pre-abolition world through the registered pre_ab2025
            # baseline instead of through an earlier policy year, so no
            # comparison has to straddle two uprating rounds.
            assert c.policy_year == 2026
            assert c.rationale  # every case explains itself

    def test_two_child_limit_cases_isolate_one_mechanism_each(self):
        """Three cases, two same-year pairs, each differing in exactly
        one thing — the round-2 finding was that the old pair changed the
        policy world, the ages and the uprating round all at once, and
        that its 'limit in force' case used twins, so an engine that
        wrongly kept the limit but rightly applied the multiple-birth
        exception still paid three elements and passed."""
        by_id = {c.case_id: c for c in load_battery(BATTERY)}
        binding = by_id["uk-uc-two-child-limit-binding"]
        abolished = by_id["uk-uc-two-child-limit-abolished"]
        twins = by_id["uk-uc-two-child-limit-multiple-birth"]

        for case in (binding, abolished, twins):
            children = case.household["benefit_units"][0]["children"]
            assert len(children) == 3
            # Every child post-April-2017, so no pre-2017 protection can
            # stand in for the mechanism under test.
            for child in children:
                assert case.household["people"][child]["date_of_birth"] > "2017-04-06"
            assert case.policy_year == 2026  # one uprating round for all three

        # Pair 1 — abolition: same household, same year, different world.
        assert binding.household == abolished.household
        assert binding.baseline == {"policy": "pre_ab2025"}
        assert abolished.baseline is None

        # Pair 2 — the exception: same world, same year, ONE input apart.
        assert twins.baseline == binding.baseline
        differing = [
            pid
            for pid in binding.household["people"]
            if binding.household["people"][pid] != twins.household["people"][pid]
        ]
        assert differing == ["child_3"]
        assert (
            binding.household["people"]["child_3"]["age"]
            == twins.household["people"]["child_3"]["age"]
        )

        # The binding case has no exception to hide behind: three
        # separate births, so the limit itself decides the entitlement.
        b_people = binding.household["people"]
        assert len({b_people[c]["date_of_birth"] for c in ("child_2", "child_3")}) == 2
        # ...and the multiple birth spans a third-or-later child.
        t_people = twins.household["people"]
        assert (
            t_people["child_2"]["date_of_birth"] == t_people["child_3"]["date_of_birth"]
        )

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
                "baseline",
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

    def test_string_focus_rejected(self):
        # A bare string iterates as characters; the schema demands a list.
        with pytest.raises(ValueError, match="expected_focus"):
            CaseSpec(**case_kwargs(expected_focus="universal_credit"))

    def test_string_unit_members_rejected(self):
        kw = case_kwargs()
        kw["household"]["benefit_units"] = [{"adults": "adult_1", "children": []}]
        with pytest.raises(ValueError, match="list of person ids"):
            CaseSpec(**kw)
        kw["household"]["benefit_units"] = [
            {"adults": ["adult_1"], "children": "child_1"}
        ]
        with pytest.raises(ValueError, match="list of person ids"):
            CaseSpec(**kw)


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
            variable_class="currency",
            abs_diff=0.04,
            tolerance=0.52,
            schema_version=SCHEMA_VERSION,
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
            **self.result_kwargs(
                pe_value=None, abs_diff=None, tolerance=None, classification="pe_gap"
            )
        )
        assert r.classification is DiffClassification.PE_GAP

    def test_null_oracle_value_requires_scope_mismatch(self):
        with pytest.raises(ValueError, match="policy_scope_mismatch"):
            CaseResult(**self.result_kwargs(oracle_value=None, abs_diff=None))

    def test_match_exact_requires_identity(self):
        with pytest.raises(ValueError, match="match_exact"):
            CaseResult(**self.result_kwargs(classification="match_exact"))

    def test_within_tolerance_requires_tolerance(self):
        # An empty-annotation, no-tolerance row must not validate.
        with pytest.raises(ValueError, match="tolerance"):
            CaseResult(**self.result_kwargs(tolerance=None))

    def test_within_tolerance_bounds_enforced(self):
        with pytest.raises(ValueError, match="abs_diff <= tolerance"):
            CaseResult(**self.result_kwargs(oracle_value=4797.48, abs_diff=1.0))
        with pytest.raises(ValueError, match="tolerance > 0"):
            CaseResult(**self.result_kwargs(tolerance=0.0))
        with pytest.raises(ValueError, match="abs_diff <= tolerance"):
            # A zero diff is match_exact, never match_within_tolerance.
            CaseResult(**self.result_kwargs(oracle_value=4796.48, abs_diff=0.0))

    def test_tolerance_only_on_within_tolerance_rows(self):
        with pytest.raises(ValueError, match="only on match_within_tolerance"):
            CaseResult(
                **self.result_kwargs(
                    pe_value=None, abs_diff=None, classification="pe_gap"
                )
            )

    def test_adjudicated_classes_require_writeup(self):
        """An adjudication applies to a row the classifier left
        unclassified, and it needs a writeup."""
        # 4796.48 vs 4900.00 is well above the currency tolerance, so the
        # classifier says `unclassified` — the adjudication queue.
        unclassified = dict(oracle_value=4900.0, abs_diff=103.52, tolerance=None)
        for cls in ("oracle_difference", "rounding", "pe_gap"):
            with pytest.raises(ValueError, match="adjudicated"):
                CaseResult(**self.result_kwargs(classification=cls, **unclassified))
            r = CaseResult(
                **self.result_kwargs(
                    classification=cls,
                    annotations=[
                        "UKMOD rounds monthly amounts to the penny; "
                        "x12 explains the difference (writeup ref)"
                    ],
                    **unclassified,
                )
            )
            assert r.classification is DiffClassification(cls)

    def test_adjudication_cannot_overrule_the_classifier(self):
        """Only an `unclassified` row may be adjudicated: a row the
        classifier has already decided is not up for reinterpretation."""
        with pytest.raises(ValueError, match="contradicts the classifier"):
            # a within-tolerance row relabelled as an oracle difference
            CaseResult(
                **self.result_kwargs(
                    classification="oracle_difference",
                    tolerance=None,
                    annotations=["because I say so"],
                )
            )

    def test_a_match_is_never_an_adjudicated_outcome(self):
        """`unclassified` may be explained, never flattered into a
        match."""
        with pytest.raises(ValueError, match="abs_diff <= tolerance"):
            CaseResult(
                **self.result_kwargs(
                    oracle_value=4900.0,
                    abs_diff=103.52,
                    classification="match_within_tolerance",
                    annotations=["close enough"],
                )
            )

    def test_annotations_must_be_nonempty_strings(self):
        with pytest.raises(ValueError, match="annotations"):
            CaseResult(**self.result_kwargs(annotations="a writeup"))
        with pytest.raises(ValueError, match="annotations"):
            CaseResult(**self.result_kwargs(annotations=[""]))


class TestDateOfBirthRealDate:
    def test_impossible_date_rejected(self):
        for bad in ("2026-13-40", "0000-00-00", "2025-02-30"):
            hh = {
                "people": {"adult_1": {"age": 30, "date_of_birth": bad}},
                "benefit_units": [{"adults": ["adult_1"], "children": []}],
            }
            with pytest.raises(ValueError, match="real"):
                CaseSpec(**case_kwargs(household=hh))

    def test_real_date_accepted(self):
        hh = {
            "people": {"adult_1": {"age": 30, "date_of_birth": "1996-02-29"}},
            "benefit_units": [{"adults": ["adult_1"], "children": []}],
        }
        CaseSpec(**case_kwargs(household=hh))


class TestSchemaVersion:
    def test_battery_carries_current_version(self):
        raw = json.loads(BATTERY.read_text())
        assert raw["schema_version"] == SCHEMA_VERSION

    def test_battery_with_wrong_version_rejected(self, tmp_path):
        raw = json.loads(BATTERY.read_text())
        raw["schema_version"] = SCHEMA_VERSION + 1
        p = tmp_path / "cases.json"
        p.write_text(json.dumps(raw))
        with pytest.raises(ValueError, match="schema_version"):
            load_battery(p)

    def test_battery_without_version_rejected(self, tmp_path):
        raw = json.loads(BATTERY.read_text())
        del raw["schema_version"]
        p = tmp_path / "cases.json"
        p.write_text(json.dumps(raw))
        with pytest.raises(ValueError, match="schema_version"):
            load_battery(p)

    def test_result_row_rejects_foreign_version(self):
        kw = TestCaseResult().result_kwargs(schema_version=SCHEMA_VERSION + 1)
        with pytest.raises(ValueError, match="schema_version"):
            CaseResult(**kw)


class TestClassifyToResultSeam:
    """The classify -> CaseResult wiring path (review: previously untested;
    callers had to re-derive the tolerance by hand)."""

    def wired(self, pe, oracle_value, vclass=VariableClass.CURRENCY, **kw):
        base = dict(
            case_id="uk-uc-single-unemployed",
            variable="universal_credit",
            pe_value=pe,
            oracle_value=oracle_value,
            variable_class=vclass,
            oracle=Oracle.UKMOD,
            engine_version="policyengine-uk 2.0.0",
            oracle_version="UKMOD B2026.08",
            computed_at="2026-08-14T12:00:00Z",
        )
        base.update(kw)
        return CaseResult.from_classification(**base)

    def test_tolerance_match_threads_the_applied_tolerance(self):
        r = self.wired(100.0, 100.30)
        assert r.classification is DiffClassification.MATCH_WITHIN_TOLERANCE
        assert r.tolerance == DEFAULT_TOLERANCES[VariableClass.CURRENCY]
        assert r.variable_class is VariableClass.CURRENCY
        assert abs(r.abs_diff - 0.30) < 1e-9

    def test_exact_match_carries_no_tolerance(self):
        r = self.wired(100.0, 100.0)
        assert r.classification is DiffClassification.MATCH_EXACT
        assert r.tolerance is None and r.abs_diff == 0.0

    def test_null_pe_side_wires_to_pe_gap(self):
        r = self.wired(None, 5.0)
        assert r.classification is DiffClassification.PE_GAP
        assert r.abs_diff is None and r.tolerance is None

    def test_a_caller_cannot_widen_the_tolerance(self):
        """Tolerances are a registry decision. The factory no longer
        takes a table, and a hand-written row carrying a wider tolerance
        is rejected — the probe that turned a boolean 1-vs-0 into a
        `match_within_tolerance` with tolerance 100."""
        with pytest.raises(TypeError):
            self.wired(100.0, 100.9, tolerance_table={VariableClass.CURRENCY: 1.0})
        with pytest.raises(ValueError, match="registered tolerance"):
            CaseResult(
                case_id="uk-uc-single-unemployed",
                variable="universal_credit",
                pe_value=100.0,
                oracle_value=100.3,
                oracle=Oracle.UKMOD,
                engine_version="policyengine-uk 2.0.0",
                oracle_version="UKMOD B2026.08",
                computed_at="2026-08-14T12:00:00Z",
                classification="match_within_tolerance",
                variable_class=VariableClass.CURRENCY,
                abs_diff=0.3,
                tolerance=1.0,
                schema_version=SCHEMA_VERSION,
            )

    def test_a_boolean_mismatch_can_never_be_a_match(self):
        r = self.wired(1.0, 0.0, vclass=VariableClass.BOOLEAN)
        assert r.classification is DiffClassification.UNCLASSIFIED
        with pytest.raises(ValueError, match="not an outcome"):
            CaseResult(
                case_id="uk-uc-single-unemployed",
                variable="is_uc_eligible",
                pe_value=1.0,
                oracle_value=0.0,
                oracle=Oracle.UKMOD,
                engine_version="policyengine-uk 2.0.0",
                oracle_version="UKMOD B2026.08",
                computed_at="2026-08-14T12:00:00Z",
                classification="match_within_tolerance",
                variable_class=VariableClass.BOOLEAN,
                abs_diff=1.0,
                tolerance=100.0,
                schema_version=SCHEMA_VERSION,
            )

    def test_the_factory_carries_annotations(self):
        """#64's calculator rows REQUIRE an archive annotation; a factory
        that could not take one made every calculator call raise."""
        r = self.wired(100.0, 100.0, annotations=["archive:https://example/x"])
        assert r.annotations == ["archive:https://example/x"]

    def test_above_tolerance_lands_unclassified(self):
        r = self.wired(100.0, 200.0)
        assert r.classification is DiffClassification.UNCLASSIFIED
        assert r.tolerance is None

    def test_variable_class_is_a_closed_vocabulary(self):
        with pytest.raises(ValueError):
            self.wired(100.0, 100.0, vclass="percentage")


class TestIdentityClosureAtTheEdges:
    """Round-2 probes accepted region="MARS", invented focus variables,
    NaN incomes, infinite rent, boolean values outside {0,1} and an
    arbitrary battery schema. Each is now a closed decision."""

    def test_region_is_a_closed_registry(self):
        hh = dict(case_kwargs()["household"], region="MARS")
        with pytest.raises(ValueError, match="unregistered UK region"):
            CaseSpec(**case_kwargs(household=hh))
        CaseSpec(**case_kwargs(household=dict(hh, region="SCOTLAND")))

    def test_focus_variables_are_closed_per_country(self):
        with pytest.raises(ValueError, match="unregistered UK focus"):
            CaseSpec(**case_kwargs(expected_focus=["vibes_credit"]))
        # a US variable is not a UK variable
        with pytest.raises(ValueError, match="unregistered UK focus"):
            CaseSpec(**case_kwargs(expected_focus=["snap"]))

    def test_focus_variables_do_not_repeat(self):
        with pytest.raises(ValueError, match="must not repeat"):
            CaseSpec(
                **case_kwargs(expected_focus=["universal_credit", "universal_credit"])
            )

    def test_nan_and_infinity_are_not_amounts(self):
        for bad in (float("nan"), float("inf")):
            hh = case_kwargs()["household"]
            people = dict(hh["people"], adult_1={"age": 30, "employment_income": bad})
            with pytest.raises(ValueError, match="finite"):
                CaseSpec(**case_kwargs(household=dict(hh, people=people)))
            with pytest.raises(ValueError, match="finite"):
                CaseSpec(**case_kwargs(household=dict(hh, rent=bad)))

    def test_boolean_class_values_must_be_zero_or_one(self):
        kw = TestCaseResult().result_kwargs(
            variable_class="boolean",
            pe_value=7.0,
            oracle_value=7.0,
            abs_diff=0.0,
            tolerance=None,
            classification="match_exact",
        )
        with pytest.raises(ValueError, match="must be 0 or 1"):
            CaseResult(**kw)

    def test_blank_engine_versions_rejected(self):
        for field in ("engine_version", "oracle_version"):
            with pytest.raises(ValueError, match="required"):
                CaseResult(**TestCaseResult().result_kwargs(**{field: "  "}))

    def test_battery_schema_path_is_closed(self, tmp_path):
        raw = json.loads(BATTERY.read_text())
        raw["schema"] = "sources/made-up/SCHEMA.md"
        p = tmp_path / "cases.json"
        p.write_text(json.dumps(raw))
        with pytest.raises(ValueError, match="not a contract this repo defines"):
            load_battery(p)

    def test_private_rent_cases_pin_a_brma(self):
        """LHA rates are per BRMA, not per ITL-1 region: without one, the
        two engines are not guaranteed the same world."""
        hh = dict(
            case_kwargs()["household"],
            tenure="rented_private",
            rent=9360,
            region="YORKSHIRE",
        )
        with pytest.raises(ValueError, match="must pin a BRMA"):
            CaseSpec(**case_kwargs(household=hh))
        with pytest.raises(ValueError, match="unregistered BRMA"):
            CaseSpec(**case_kwargs(household=dict(hh, brma="Atlantis")))
        with pytest.raises(ValueError, match="sits in"):
            CaseSpec(**case_kwargs(household=dict(hh, brma="Inner London")))
        CaseSpec(**case_kwargs(household=dict(hh, brma="Leeds")))

    def test_every_private_rent_case_in_the_battery_pins_one(self):
        for c in load_battery(BATTERY):
            if c.household.get("tenure") == "rented_private":
                assert c.household["brma"] in BRMA_REGION

    def test_case_baselines_must_be_registered(self):
        with pytest.raises(ValueError, match="unregistered baseline world"):
            CaseSpec(**case_kwargs(baseline={"policy": "a_world_nobody_named"}))
        # the registered reinstated-limit world is accepted
        CaseSpec(**case_kwargs(baseline={"policy": "pre_ab2025"}))
