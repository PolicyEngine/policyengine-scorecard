"""Construction changes are selected by installed metadata, never versions."""

import copy
import hashlib
import json

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
