"""Construction changes are selected by installed metadata, never versions."""

import copy
import hashlib
import json
import sys
from types import SimpleNamespace

import pytest
from hypothesis import given
from hypothesis import strategies as st

from pipeline import audit_uk_event_premises as premises
from pipeline import compute_uk_ab2025 as worlds
from pipeline import compute_uk_event as compute
from pipeline import uk_construction_revisions as revisions

KEY = "autumn_budget_2024__capital_gains_main_rates_and_reliefs"
PATHS = (
    "gov.hmrc.cgt.basic_rate",
    "gov.hmrc.cgt.higher_rate",
    "gov.hmrc.cgt.additional_rate",
)
RATES = (0.1, 0.2, 0.2)


def frozen_measure():
    registry = json.loads(
        (premises.EVENTS_DIR / "autumn_budget_2024_measures.json").read_bytes()
    )
    return next(m for m in registry["measures"] if m["measure_key"] == KEY)


def frozen_world():
    measure = frozen_measure()
    return worlds.worlds_for(measure, {KEY: measure}, years=[2023, 2024, 2025])


@given(st.tuples(*(st.sampled_from([None, False, True, 1, "true"]) for _ in PATHS)))
def test_revision_selected_exactly_when_all_installed_paths_carry_true(flags):
    metadata = dict(zip(PATHS, flags))
    selected = revisions.select_revision(
        KEY, lambda path: {"fiscal_year_blend": metadata[path]}
    )
    assert (selected is not None) is all(flag is True for flag in flags)
    if selected:
        assert (
            selected["registry_sha256"]
            == hashlib.sha256(revisions.REVISIONS_PATH.read_bytes()).hexdigest()
        )
        assert selected["activation_fy"] == "2024-25"
        assert selected["part_year_rule"] == "part_year_day_weighted"


def test_unrecognized_measure_never_reads_engine_metadata():
    def unavailable(path):
        raise AssertionError("a measure without revisions must not query the engine")

    assert revisions.select_revision("not_a_registered_revision", unavailable) is None


def test_no_metadata_preserves_exact_legacy_world():
    original = frozen_world()
    before = json.dumps(original)
    revised = revisions.apply_revision(KEY, original, lambda path: {})
    assert revised is original
    assert json.dumps(revised) == before
    assert "construction_revision" not in revised


def test_revision_changes_only_annual_baseline_from_2024_and_is_digest_bound():
    original = frozen_world()
    before = copy.deepcopy(original)
    revised = revisions.apply_revision(
        KEY, original, lambda path: {"fiscal_year_blend": True}
    )
    assert original == before
    assert revised["reform_reform"] is None
    assert revised["construction_revision"]["paths"] == list(PATHS)
    annual = compute.annual_reform(revised["baseline_reform"])
    for path, rate in zip(PATHS, RATES):
        for year, expected in [(2023, 9.0), (2024, rate), (2025, rate)]:
            assert (
                revisions.intended_value(annual, path, year, lambda path, date: 9.0)
                == expected
            )
    selected = revised["construction_revision"]
    for field, value in [
        ("registry_sha256", "0" * 64),
        ("revision_id", "a_different_revision"),
        ("activation_fy", "2025-26"),
        ("paths", []),
        ("part_year_rule", "sampled"),
    ]:
        changed = {**selected, field: value}
        with pytest.raises(ValueError, match="does not match registry"):
            revisions.apply_selected_revision(KEY, original, changed)


def test_revision_changes_invalidates_previously_recorded_digest(tmp_path, monkeypatch):
    selected = revisions.select_revision(KEY, lambda path: {"fiscal_year_blend": True})
    changed = tmp_path / "construction_revisions.json"
    changed.write_bytes(revisions.REVISIONS_PATH.read_bytes() + b"\n")
    monkeypatch.setattr(revisions, "REVISIONS_PATH", changed)
    with pytest.raises(ValueError, match="does not match registry"):
        revisions.get_revision(KEY, selected)


def test_premises_and_runtime_share_intended_rule_for_selected_cgt():
    class Engine:
        reads_blend = reads_calendar = True

        def metadata(self, path):
            return {"fiscal_year_blend": True}

        def current_law(self, path, date):
            old = RATES[PATHS.index(path)]
            new = 0.18 if old == 0.1 else 0.24
            year = int(date[:4])
            return (
                old
                if year < 2024
                else (old * 207 / 365 + new * 158 / 365 if year == 2024 else new)
            )

        def raw_30_april(self, path, year):
            return RATES[PATHS.index(path)]

        def annualisation(self, path):
            return {"fiscal_year_blend": True, "preserve_calendar_dates": False}

        resolve = current_law

    engine = Engine()
    frozen = frozen_world()
    revised = revisions.apply_revision(KEY, frozen, engine.metadata)
    audit = premises.audit_measure(
        "autumn_budget_2024", frozen_measure(), frozen, [2023, 2024, 2025], engine
    )
    assert audit["construction_revision"] == revised["construction_revision"]
    for year in (2023, 2024, 2025):
        for path in PATHS:
            record = audit["years"][str(year)]["paths"][path]
            for field, world in [
                ("baseline_world", "baseline_reform"),
                ("reform_world", "reform_reform"),
            ]:
                assert record[field] == revisions.intended_value(
                    compute.annual_reform(revised[world]),
                    path,
                    year,
                    engine.current_law,
                )
    paths_2024 = audit["years"]["2024"]["paths"]
    for path, old in zip(PATHS, RATES):
        assert paths_2024[path]["baseline_world"] == old
        assert paths_2024[path]["reform_world"] > old


def test_intended_annual_lookup_uses_last_update_and_no_limit_sentinel():
    reform = {
        "gov.x": {
            "2024-01-01.2026-12-31": 0.1,
            "2025-01-01.2025-12-31": None,
        }
    }
    assert (
        revisions.intended_value(reform, "gov.x", 2025, lambda *args: 0.2)
        == worlds.NO_LIMIT
    )
    assert revisions.intended_value(reform, "gov.x", 2023, lambda *args: 0.2) == 0.2


def test_namespace_audit_reproduces_recorded_construction_instead_of_revising_history(
    tmp_path,
):
    class Engine:
        reads_blend = reads_calendar = True

        def metadata(self, path):
            return {"fiscal_year_blend": True}

        def current_law(self, path, date):
            return 0.1346 if path.endswith("basic_rate") else 0.2173

        raw_30_april = current_law
        resolve = current_law

        def annualisation(self, path):
            return {"fiscal_year_blend": True, "preserve_calendar_dates": False}

    registry_dir = tmp_path / "registries"
    registry_dir.mkdir()
    (registry_dir / "autumn_budget_2024_measures.json").write_text(
        json.dumps(
            {
                "calendar_years": [2023, 2024, 2025],
                "measures": [frozen_measure()],
            }
        )
    )
    namespace = tmp_path / "namespace"
    event_dir = namespace / "autumn_budget_2024"
    event_dir.mkdir(parents=True)
    manifest_path = event_dir / "RUN_MANIFEST.json"
    engine = Engine()

    def audit():
        return premises.audit(
            ["autumn_budget_2024"], engine, events_dir=registry_dir, namespace=namespace
        )

    manifest_path.write_text("{}")
    historical = audit()
    old_measure = historical["events"]["autumn_budget_2024"]["measures"][KEY]
    assert "construction_revision" not in old_measure
    assert old_measure["years"]["2024"]["paths"][PATHS[0]]["baseline_world"] == 0.1346
    assert historical["description"].startswith("Executed-world values")

    # A fresh non-CGT namespace still describes the new readback contract.
    manifest_path.write_text(
        json.dumps({"processed_value_check": "processed_period_values.v1"})
    )
    assert audit()["description"].startswith("Intended-world values")

    selected = revisions.select_revision(KEY, engine.metadata)
    manifest_path.write_text(json.dumps({"construction_revisions": {KEY: selected}}))
    revised = audit()
    revised_measure = revised["events"]["autumn_budget_2024"]["measures"][KEY]
    assert revised_measure["construction_revision"] == selected
    assert revised_measure["years"]["2024"]["paths"][PATHS[0]]["baseline_world"] == 0.1
    assert revised["description"].startswith("Intended-world values")

    manifest_path.write_text(
        json.dumps(
            {
                "construction_revisions": {
                    KEY: {**selected, "registry_sha256": "0" * 64},
                }
            }
        )
    )
    with pytest.raises(ValueError, match="does not match"):
        audit()

    # Historical sparse namespaces can retain their premises without event
    # manifests. Missing revision evidence still means the frozen construction.
    manifest_path.unlink()
    assert audit() == historical


SURCHARGE = "autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp"
ALLOWANCE = "spring_statement_2025__uc_standard_allowance_above_inflation"
SURCHARGE_PATHS = tuple(
    f"gov.hmrc.stamp_duty.residential.purchase.additional.rate[{band}].rate"
    for band in range(5)
)
ENACTED = dict(zip(SURCHARGE_PATHS, (0.05, 0.07, 0.1, 0.15, 0.17)))
PRIOR = dict(zip(SURCHARGE_PATHS, (0.03, 0.05, 0.08, 0.13, 0.15)))
ALLOWANCE_PATHS = tuple(
    f"gov.dwp.universal_credit.standard_allowance.amount.{claimant}"
    for claimant in ("COUPLE_OLD", "COUPLE_YOUNG", "SINGLE_OLD", "SINGLE_YOUNG")
)
UPLIFT_INDEX = "gov.economic_assumptions.indices.uc_standard_allowance"


def registered(event, key, years):
    registry = json.loads((premises.EVENTS_DIR / f"{event}_measures.json").read_bytes())
    measure = next(m for m in registry["measures"] if m["measure_key"] == key)
    return measure, worlds.worlds_for(measure, {key: measure}, years=years)


def enacted_law(path, date):
    """policyengine-uk 2.151.0's processed values: the 30 April sample of each
    year, so 2024 still holds the old scale and band 1 has no rate."""
    if date >= "2025-01-01":
        return ENACTED[path]
    return None if path == SURCHARGE_PATHS[1] else PRIOR[path]


def surcharge_world():
    return registered("autumn_budget_2024", SURCHARGE, list(range(2024, 2030)))[1]


def no_metadata(path):
    raise AssertionError("a value condition must not read metadata")


def test_every_sealed_namespace_still_validates_its_recorded_revisions():
    manifests = sorted(
        (compute.ROOT / "results/uk/replays").glob("*/*/RUN_MANIFEST.json")
    )
    recorded = [
        (key, evidence)
        for path in manifests
        for key, evidence in json.loads(path.read_bytes())
        .get("construction_revisions", {})
        .items()
    ]
    assert recorded
    for key, evidence in recorded:
        assert revisions.get_revision(key, evidence)["revision_id"]


def test_the_sealed_revision_file_stays_frozen_and_the_files_share_no_measure():
    digest = hashlib.sha256(revisions.REVISIONS_PATH.read_bytes()).hexdigest()
    assert digest == "23993c8fbdcff319045b10bf316b29eb093c283dc6d135c430db237de0050a57"
    sealed, enacted = (
        json.loads(path.read_bytes())["revisions"]
        for path in (revisions.REVISIONS_PATH, revisions.ENACTED_REVISIONS_PATH)
    )
    assert not set(sealed) & set(enacted)


def test_evidence_binds_the_digest_of_the_file_holding_the_revision():
    selected = revisions.select_revision(SURCHARGE, no_metadata, enacted_law)
    assert (
        selected["registry_sha256"]
        == hashlib.sha256(revisions.ENACTED_REVISIONS_PATH.read_bytes()).hexdigest()
    )
    assert selected["paths"] == []


@given(st.lists(st.booleans(), min_size=5, max_size=5))
def test_surcharge_revision_selected_exactly_when_every_enacted_rate_is_law(held):
    installed = {
        path: ENACTED[path] if holds else PRIOR[path]
        for path, holds in zip(SURCHARGE_PATHS, held)
    }
    selected = revisions.select_revision(
        SURCHARGE, no_metadata, lambda path, date: installed[path]
    )
    assert (selected is not None) is all(held)


def test_a_value_condition_refuses_a_caller_without_current_law():
    with pytest.raises(ValueError, match="current-law values"):
        revisions.select_revision(SURCHARGE, no_metadata)


def test_surcharge_revision_reverses_the_delta_over_its_own_windows():
    original = surcharge_world()
    before = copy.deepcopy(original)
    revised = revisions.apply_revision(SURCHARGE, original, no_metadata, enacted_law)
    assert original == before
    assert revised["construction"] == "reversal_on_certified_world"
    assert revised["reform_reform"] is None
    assert revised["construction_revision"]["activation_fy"] == "2025-26"
    assert {
        path: list(windows) for path, windows in revised["baseline_reform"].items()
    } == {path: list(windows) for path, windows in original["reform_reform"].items()}
    for path, windows in revised["baseline_reform"].items():
        assert set(windows.values()) == {PRIOR[path]}
    assert revised["components"] == original["components"]
    assert revised["sentinels"] == original["sentinels"]


@given(st.integers(min_value=2024, max_value=2029))
def test_revised_surcharge_worlds_differ_exactly_from_the_first_annual_lookup(year):
    revised = revisions.apply_revision(
        SURCHARGE, surcharge_world(), no_metadata, enacted_law
    )
    baseline = compute.annual_reform(revised["baseline_reform"])
    for path in SURCHARGE_PATHS:
        law = enacted_law(path, f"{year}-01-01")
        intended = revisions.intended_value(baseline, path, year, enacted_law)
        assert intended == (PRIOR[path] if year >= 2025 else law)
        assert revisions.intended_value(None, path, year, enacted_law) == law


def test_an_older_scale_keeps_the_exact_frozen_forward_delta():
    original = surcharge_world()
    before = json.dumps(original)
    revised = revisions.apply_revision(
        SURCHARGE, original, no_metadata, lambda path, date: PRIOR[path]
    )
    assert revised is original
    assert json.dumps(revised) == before


@pytest.mark.parametrize(
    "mutate",
    [
        lambda world: world["reform_reform"].pop(SURCHARGE_PATHS[0]),
        lambda world: world["reform_reform"][SURCHARGE_PATHS[0]].update(
            {next(iter(world["reform_reform"][SURCHARGE_PATHS[0]])): 0.06}
        ),
        lambda world: world.update(baseline_reform={"gov.other": {}}),
    ],
)
def test_surcharge_revision_refuses_a_delta_it_was_not_written_for(mutate):
    world = surcharge_world()
    mutate(world)
    with pytest.raises(ValueError, match="frozen delta no longer fits"):
        revisions.apply_revision(SURCHARGE, world, no_metadata, enacted_law)


class EnactedEngine:
    reads_blend = reads_calendar = True

    def __init__(self, law=enacted_law):
        self.current_law = law
        self.resolve = law

    def metadata(self, path):
        return {}

    def raw_30_april(self, path, year):
        return self.current_law(path, f"{year}-01-01")

    def annualisation(self, path):
        return {"fiscal_year_blend": False, "preserve_calendar_dates": False}


def test_premises_hold_the_reversal_to_current_law_once_the_revision_runs():
    measure, world = registered(
        "autumn_budget_2024", SURCHARGE, list(range(2024, 2030))
    )
    audit = premises.audit_measure(
        "autumn_budget_2024", measure, world, list(range(2024, 2030)), EnactedEngine()
    )
    assert audit["construction"] == "reversal_on_certified_world"
    assert audit["construction_revision"]["paths"] == []
    assert audit["checks"]["reversal_differs_from_current_law"]["holds"] is True
    assert audit["checks"]["forward_delta_changes_current_law"]["holds"] is None
    assert audit["checks"]["authored_construction_reproduces"]["holds"] is True


def test_premises_keep_the_forward_check_on_an_engine_without_the_surcharge():
    measure, world = registered(
        "autumn_budget_2024", SURCHARGE, list(range(2024, 2030))
    )
    audit = premises.audit_measure(
        "autumn_budget_2024",
        measure,
        world,
        list(range(2024, 2030)),
        EnactedEngine(lambda path, date: PRIOR[path]),
    )
    assert audit["construction"] == "forward_delta_on_certified_world"
    assert "construction_revision" not in audit
    assert audit["checks"]["forward_delta_changes_current_law"]["holds"] is True


def build_surcharge_artifact(world, *, baseline, reform, certified):
    measure = registered("autumn_budget_2024", SURCHARGE, [2025])[0]
    variables = compute.variable_channels(measure)

    def simulation(aggregate):
        return {
            "aggregates_gbp": {variable: aggregate for variable in variables},
            "variable_metadata": {variable: {} for variable in variables},
            "policyengine_bundle": {
                "model_version": "test",
                "certified_data_build_id": "test",
            },
            "dataset_sha256_before": "a" * 64,
            "dataset_sha256_after": "a" * 64,
        }

    return compute.build_artifact(
        measure=measure,
        world=world,
        year=2025,
        baseline=simulation(baseline),
        reform=simulation(reform),
        certified=simulation(certified),
        registry_sha256="b" * 64,
        event="autumn_budget_2024",
    )


@given(
    st.integers(min_value=0, max_value=10**10),
    st.integers(min_value=0, max_value=10**10),
)
def test_a_reversal_on_the_enacted_engine_scores_as_the_forward_delta_did(prior, law):
    """Differential: the two constructions of one measure give one effect, when
    each simulation returns the same aggregate for the same statutory scale."""
    forward = build_surcharge_artifact(
        surcharge_world(), baseline=prior, reform=law, certified=prior
    )
    reversal = build_surcharge_artifact(
        revisions.apply_revision(
            SURCHARGE, surcharge_world(), no_metadata, enacted_law
        ),
        baseline=prior,
        reform=law,
        certified=law,
    )
    assert reversal["head_effects"] == forward["head_effects"]
    assert reversal["measure_total_gbp"] == forward["measure_total_gbp"]
    assert reversal["construction"] != forward["construction"]


@given(
    st.lists(
        st.sampled_from([UPLIFT_INDEX, "gov.benefit_uprating_cpi", None]),
        min_size=4,
        max_size=4,
    )
)
def test_allowance_revision_selected_exactly_when_every_amount_uses_the_uplift_index(
    indices,
):
    uprating = dict(zip(ALLOWANCE_PATHS, indices))
    selected = revisions.select_revision(
        ALLOWANCE, lambda path: {"uprating": uprating[path]}
    )
    assert (selected is not None) is all(index == UPLIFT_INDEX for index in indices)


def test_allowance_revision_runs_the_frozen_worlds_on_their_own_windows(monkeypatch):
    years = [2026, 2027, 2028, 2029]
    original = registered("spring_statement_2025", ALLOWANCE, years)[1]
    revised = revisions.apply_revision(
        ALLOWANCE, original, lambda path: {"uprating": UPLIFT_INDEX}
    )
    evidence = revised.pop("construction_revision")
    assert revised == original
    assert evidence["paths"] == []
    scenario = SimpleNamespace(
        from_reform=lambda reform: SimpleNamespace(dated_reforms=[reform])
    )
    monkeypatch.setitem(
        sys.modules,
        "policyengine_uk.utils.scenario",
        SimpleNamespace(Scenario=scenario),
    )
    annual = compute.annual_reform(original["baseline_reform"])
    assert compute.revision_reform_route(annual, evidence) == annual


def test_a_metadata_condition_keeps_identity_for_a_boolean_flag():
    # 1 == True, but the CGT revision has always required the flag itself.
    assert revisions.select_revision(KEY, lambda path: {"fiscal_year_blend": 1}) is None
