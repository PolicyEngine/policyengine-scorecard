"""Tests for the OBR policy-effects -> DB ingest path (#55 step 2).

Mapping-layer tests run on synthetic rows so they hold on any branch;
the staged-file tests activate once the harvest output (#75) is present
under data/externals/.
"""

import json

import pytest

from scorecard_db import Metric, ScorecardDB, UnitConcept
from scorecard_db.ingest_obr_policy_effects import (
    _BP10_HORIZON_FY,
    _BP10_HORIZON_PERIOD,
    EXTERNALS,
    SOURCE,
    _decomposition,
    _fy,
    stage,
)
from scorecard_db.models import CalibrationRelationship


def _row(**over):
    base = {
        "source": "obr-policy-effects",
        "country": "UK",
        "program": "policy_package",
        "metric": "gdp_level_effect",
        "subgroup": "total",
        "variant": None,
        "geography": "UK",
        "unit_concept": "percent",
        "period": "2026-27",
        "value": 0.26,
        "status": "ok",
        "fiscal_event": "autumn_budget_2025",
        "basis": "post_behavioural",
        "scope": "package",
        "aggregate_level": "total",
        "parent": None,
        "source_column": "C3.3:Total",
    }
    base.update(over)
    return base


def _staged(monkeypatch, rows):
    monkeypatch.setattr(
        "scorecard_db.ingest_obr_policy_effects._load", lambda: list(rows)
    )
    return stage()


def _write_externals(monkeypatch, tmp_path, rows):
    """Point the module at a temp externals dir holding `rows`, so the
    _load() gates run against a real file."""
    (tmp_path / "obr-policy-effects.json").write_text(json.dumps(rows))
    monkeypatch.setattr("scorecard_db.ingest_obr_policy_effects.EXTERNALS", tmp_path)


# --- financial-year parsing -------------------------------------------------


def test_fy_parsing():
    assert _fy("2023-24") == (2024, "2023-24")
    assert _fy("2030-31") == (2031, "2030-31")
    assert _fy("1999-00") == (2000, "1999-00")
    with pytest.raises(ValueError, match="unparseable"):
        _fy("FYE 2024")
    # the suffix must be start + 1 — never silently accept a malformed span
    with pytest.raises(ValueError, match="suffix"):
        _fy("2029-99")
    # fullmatch: a trailing newline must not pass
    with pytest.raises(ValueError, match="unparseable"):
        _fy("2029-30\n")


# --- fail-loud identity gates ----------------------------------------------


def test_unknown_metric_raises(monkeypatch):
    with pytest.raises(KeyError):
        _staged(monkeypatch, [_row(metric="employment_effect")])


@pytest.mark.parametrize(
    "field,value,match",
    [
        ("fiscal_event", "autumn_budget_2027", "fiscal_event"),
        ("basis", "static", "basis"),
        ("scope", "economy", "scope"),
        ("aggregate_level", "grand_total", "aggregate_level"),
    ],
)
def test_unregistered_closed_axis_raises(monkeypatch, field, value, match):
    with pytest.raises(ValueError, match=match):
        _staged(monkeypatch, [_row(**{field: value})])


def test_unregistered_subgroup_and_program_raise(monkeypatch):
    with pytest.raises(ValueError, match="subgroup"):
        _staged(monkeypatch, [_row(subgroup="animal_spirits")])
    with pytest.raises(ValueError, match="program"):
        _staged(monkeypatch, [_row(program="growth_package")])


def test_unhandled_adapter_field_raises(monkeypatch, tmp_path):
    """require_fields: a new adapter column is handled deliberately or
    the ingest stops — never silently dropped."""
    row = _row()
    row["confidence_interval"] = "0.1"
    _write_externals(monkeypatch, tmp_path, [row])
    with pytest.raises(ValueError, match="unhandled staged fields"):
        stage()


def test_non_uk_row_raises(monkeypatch, tmp_path):
    _write_externals(monkeypatch, tmp_path, [_row(country="US")])
    with pytest.raises(ValueError, match="not 'UK'"):
        stage()


def test_foreign_source_slug_raises(monkeypatch, tmp_path):
    _write_externals(monkeypatch, tmp_path, [_row(source="obr-welfare")])
    with pytest.raises(ValueError, match="is not 'obr-policy-effects'"):
        stage()


def test_missing_harvest_file_raises(monkeypatch, tmp_path):
    monkeypatch.setattr("scorecard_db.ingest_obr_policy_effects.EXTERNALS", tmp_path)
    with pytest.raises(FileNotFoundError, match="adapter.py"):
        stage()


# --- the decomposition axis -------------------------------------------------


def test_decomposition_distinguishes_the_two_ab2024_charts():
    """October 2024 prints the AB2024 package twice: chart 2.A by
    expenditure component, 2.B by measure/channel. Both publish 'total'
    and 'demand_multipliers', so without this axis the rows collide."""
    a = _decomposition(_row(fiscal_event="autumn_budget_2024", source_column="C2.A:x"))
    b = _decomposition(_row(fiscal_event="autumn_budget_2024", source_column="C2.B:x"))
    assert a == "expenditure_component"
    assert b == "channel"
    assert a != b


def test_same_sheet_id_can_mean_different_decompositions():
    """C2.A is by-channel in Nov 2023 and by-expenditure-component in
    Oct 2024 — the sheet id alone is not the identity."""
    assert (
        _decomposition(
            _row(fiscal_event="autumn_statement_2023", source_column="C2.A:x")
        )
        == "channel"
    )
    assert (
        _decomposition(_row(fiscal_event="autumn_budget_2024", source_column="C2.A:x"))
        == "expenditure_component"
    )


def test_unregistered_event_sheet_pair_raises():
    with pytest.raises(ValueError, match="unregistered"):
        _decomposition(_row(source_column="C9.9:x"))


def test_two_ab2024_totals_stage_without_collision(monkeypatch):
    rows = [
        _row(
            fiscal_event="autumn_budget_2024",
            source_column="C2.A:Total",
            value=0.0855,
        ),
        _row(
            fiscal_event="autumn_budget_2024",
            source_column="C2.B:Total",
            value=0.0855,
        ),
    ]
    scores, counts = _staged(monkeypatch, rows)
    assert counts == {"gdp_level_effect": 2}
    assert len({s.claim_id() for s in scores}) == 2


# --- period handling --------------------------------------------------------


def test_supply_side_horizon_is_named_not_guessed(monkeypatch):
    """The briefing paper states the horizon in words; the mapping to a
    year is deliberate, carries the verbatim note, and lives in one
    place."""
    scores, _ = _staged(
        monkeypatch,
        [
            _row(
                metric="supply_side_impact",
                program="restart",
                subgroup="labour",
                variant="del",
                period="forecast_horizon",
                unit_concept="percent",
                basis="supply_side",
                scope="measure",
                aggregate_level="component",
                fiscal_event="spring_budget_2023",
                source_column="T2.1:Restart",
                description="Employment support",
            )
        ],
    )
    (s,) = scores
    assert s.period == _BP10_HORIZON_PERIOD
    assert s.conditions["fy"] == _BP10_HORIZON_FY
    assert s.conditions["horizon"] == "fifth_year_of_forecast"
    assert "fifth year of our forecast" in s.conditions["horizon_note"]


def test_forecast_horizon_on_a_chart_metric_raises(monkeypatch):
    """Only the briefing-paper table publishes a horizon-terminal
    number; a chart row arriving without a year is a parse fault."""
    with pytest.raises(ValueError, match="horizon-terminal"):
        _staged(monkeypatch, [_row(period="forecast_horizon")])


# --- reform worlds ----------------------------------------------------------


def test_package_and_measure_worlds_never_share_a_slug(monkeypatch):
    scores, _ = _staged(
        monkeypatch,
        [
            _row(fiscal_event="autumn_budget_2024", source_column="C2.A:Total"),
            _row(
                metric="supply_side_impact",
                program="employer_nics",
                subgroup="labour",
                variant="tax",
                period="forecast_horizon",
                basis="supply_side",
                scope="measure",
                aggregate_level="component",
                fiscal_event="autumn_budget_2024",
                source_column="T2.1:Employer NICs",
                description="",
            ),
        ],
    )
    slugs = {s.reform.reform["policy"] for s in scores}
    assert slugs == {
        "obr_autumn_budget_2024_package",
        "obr_autumn_budget_2024_employer_nics",
    }
    # the null baseline: OBR scores an announcement against the law in
    # force at its own scoring date (baselines.py convention), so this
    # module registers no new baseline world
    assert all(s.reform.baseline is None for s in scores)


def test_same_measure_at_two_events_is_two_worlds(monkeypatch):
    scores, _ = _staged(
        monkeypatch,
        [
            _row(
                metric="supply_side_impact",
                program="employee_nics_cut",
                subgroup="labour",
                variant="tax",
                period="forecast_horizon",
                basis="supply_side",
                scope="measure",
                aggregate_level="component",
                fiscal_event=event,
                source_column="T2.1:Employee NICs cut",
                description="",
            )
            for event in ("autumn_statement_2023", "spring_budget_2024")
        ],
    )
    assert len({s.reform.reform["policy"] for s in scores}) == 2
    assert len({s.claim_id() for s in scores}) == 2


# --- relationships ----------------------------------------------------------


def test_every_claim_is_held_out(monkeypatch):
    """No pe-uk-data target or policyengine-uk parameter is fitted to a
    macro-effect path: these are what the Macro members are scored
    against."""
    scores, _ = _staged(monkeypatch, [_row()])
    assert all(
        s.calibration_relationship is CalibrationRelationship.HELD_OUT for s in scores
    )


def test_unknown_basis_needs_a_deliberate_assignment():
    from scorecard_db.relationships import uk_relationship

    with pytest.raises(ValueError, match="deliberate"):
        uk_relationship(SOURCE, Metric.GDP_LEVEL_EFFECT, program="x", kind="static")


# --- staged-file integration ------------------------------------------------

harvest_present = (EXTERNALS / "obr-policy-effects.json").exists()


@pytest.mark.skipif(not harvest_present, reason="harvest output not present (#75)")
def test_full_stage_accounting():
    """Exact accounting — a drifted harvest regeneration must fail here,
    never grow or shrink the catalog silently."""
    scores, counts = stage()
    assert counts == {
        "gdp_level_effect": 151,
        "cpi_inflation_effect": 36,
        "supply_side_impact": 19,
        "decisions_effect_on_borrowing": 60,
    }
    assert len(scores) == 266
    assert len({s.claim_id() for s in scores}) == 266


@pytest.mark.skipif(not harvest_present, reason="harvest output not present (#75)")
def test_full_ingest_round_trip(tmp_path):
    from scorecard_db.ingest_obr_policy_effects import ingest

    summary = ingest(tmp_path / "t.db")
    assert summary["claims"] == 266
    db = ScorecardDB(tmp_path / "t.db")
    n = db.conn.execute(
        "SELECT COUNT(*) FROM external_scores WHERE source = ?", (SOURCE,)
    ).fetchone()[0]
    assert n == 266

    # units: the percent families never land as GBP and vice versa
    units = dict(
        db.conn.execute(
            "SELECT metric, unit_concept FROM external_scores"
            " WHERE source = ? GROUP BY metric, unit_concept",
            (SOURCE,),
        )
    )
    assert units == {
        Metric.GDP_LEVEL_EFFECT.value: UnitConcept.PERCENT.value,
        Metric.CPI_INFLATION_EFFECT.value: UnitConcept.PERCENT.value,
        Metric.SUPPLY_SIDE_IMPACT.value: UnitConcept.PERCENT.value,
        Metric.DECISIONS_EFFECT_ON_BORROWING.value: UnitConcept.GBP.value,
    }

    # the double-count guard survives to the DB: every Table B.1 row
    # carries its level, and the nested ones name their parent
    levels = dict(
        db.conn.execute(
            "SELECT json_extract(conditions, '$.aggregate_level'), COUNT(*)"
            " FROM external_scores WHERE source = ?"
            " AND metric = 'decisions_effect_on_borrowing' GROUP BY 1",
            (SOURCE,),
        )
    )
    assert levels == {"total": 6, "subtotal": 24, "component": 30}
    orphans = db.conn.execute(
        "SELECT COUNT(*) FROM external_scores WHERE source = ?"
        " AND metric = 'decisions_effect_on_borrowing'"
        " AND json_extract(conditions, '$.aggregate_level') != 'total'"
        " AND json_extract(conditions, '$.parent') IS NULL",
        (SOURCE,),
    ).fetchone()[0]
    assert orphans == 0

    # nothing may be consumed: these claims are scored, never fitted
    consumed = db.conn.execute(
        "SELECT COUNT(*) FROM external_scores WHERE source = ?"
        " AND calibration_relationship != 'held_out'",
        (SOURCE,),
    ).fetchone()[0]
    assert consumed == 0

    # the two AB2024 charts stay distinguishable in the DB
    ab2024_totals = db.conn.execute(
        "SELECT DISTINCT json_extract(conditions, '$.decomposition')"
        " FROM external_scores WHERE source = ?"
        " AND json_extract(conditions, '$.fiscal_event') = 'autumn_budget_2024'",
        (SOURCE,),
    ).fetchall()
    assert sorted(r[0] for r in ab2024_totals) == [
        "channel",
        "expenditure_component",
        "supply_side_channel",
    ]
    db.close()


@pytest.mark.skipif(not harvest_present, reason="harvest output not present (#75)")
def test_values_pass_through_verbatim():
    """Values arrive in raw units from the adapter and are never
    re-derived here — spot-checked against the committed harvest."""
    raw = json.loads((EXTERNALS / "obr-policy-effects.json").read_text())
    scores, _ = stage()
    # staging preserves adapter row order, so the pairing is positional —
    # source_column alone is not unique (the same sheet label recurs
    # across fiscal events)
    assert len(scores) == len(raw)
    for score, row in zip(scores, raw):
        assert score.value == row["value"]
        assert score.source_column == row["source_column"]
        assert score.status == row["status"]
        expected = (
            _BP10_HORIZON_PERIOD
            if row["period"] == "forecast_horizon"
            else _fy(row["period"])[0]
        )
        assert score.period == expected
