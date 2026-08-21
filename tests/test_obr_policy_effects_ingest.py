"""Tests for the OBR policy-effects -> DB ingest path (#55 step 2).

Mapping-layer tests run on synthetic rows so they hold on any branch;
the staged-file tests activate once the harvest output (#75) is present
under data/externals/.
"""

import json

import pytest

from scorecard_db import Metric, ScorecardDB, UnitConcept
from scorecard_db.ingest_obr_policy_effects import (
    _BP10_HORIZON,
    _EVENT_BASELINE,
    EXTERNALS,
    PUBLICATIONS,
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
        "unit_concept": "percent_of_real_gdp",
        "period": "2026-27",
        "value": 0.26,
        "status": "ok",
        "fiscal_event": "autumn_budget_2025",
        "basis": "forecast",
        "scoring_method": "post_behavioural",
        "scope": "package",
        "aggregate_level": "total",
        "parent": None,
        "artifact": "efo_november2025_chapter3.xlsx",
        "baseline": "obr_pre_measures_autumn_budget_2025",
        "baseline_counterfactual": "policy_parameters",
        "baseline_locator": (
            "EFO November 2025, Chart 3.3: policy impacts on real GDP, "
            "measured as deviations from the pre-measures November 2025 "
            "forecast."
        ),
        "source_column": "C3.3:Total",
    }
    base.update(over)
    # each round is scored against its OWN pre-measures world; keep the
    # synthetic rows self-consistent the way the adapter's are
    base["baseline"] = _EVENT_BASELINE.get(base["fiscal_event"], base["baseline"])
    if "baseline" in over:
        base["baseline"] = over["baseline"]
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
        ("scoring_method", "dynamic", "scoring_method"),
        ("baseline", "current_law", "baseline policy"),
        ("baseline_counterfactual", "vibes", "baseline counterfactual"),
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
                program="restart_scheme",
                subgroup="labour",
                variant="del",
                period="forecast_horizon",
                unit_concept="percent_of_potential_gdp",
                scoring_method="supply_side",
                scope="measure",
                aggregate_level="component",
                fiscal_event="spring_budget_2023",
                source_column="T2.1:Restart",
                description="Employment support",
            )
        ],
    )
    (s,) = scores
    fy, period = _BP10_HORIZON["spring_budget_2023"]
    assert (fy, period) == ("2027-28", 2028)
    assert s.period == period
    assert s.conditions["fy"] == fy
    assert s.conditions["horizon"] == "fifth_year_of_scoring_round_forecast"
    assert "fifth year of our forecast" in s.conditions["horizon_note"]


def test_supply_side_horizon_is_per_scoring_round(monkeypatch):
    """Briefing paper No.10 re-states scorings made at FIVE earlier
    events. "The fifth year of our forecast" is each measure's own
    round's fifth year, not the November 2025 round's — period is claim
    identity, so one shared 2030-31 would be 19 wrong claims."""

    def measure(event):
        return _row(
            metric="supply_side_impact",
            program="employee_nics_cut",
            subgroup="labour",
            variant="tax",
            period="forecast_horizon",
            unit_concept="percent_of_potential_gdp",
            scoring_method="supply_side",
            scope="measure",
            aggregate_level="component",
            fiscal_event=event,
            source_column="T2.1:Employee NICs cut",
            description="",
        )

    scores, _ = _staged(monkeypatch, [measure(e) for e in _BP10_HORIZON])
    got = {s.conditions["fiscal_event"]: (s.conditions["fy"], s.period) for s in scores}
    assert got == {
        "spring_budget_2023": ("2027-28", 2028),
        "autumn_statement_2023": ("2028-29", 2029),
        "spring_budget_2024": ("2028-29", 2029),
        "autumn_budget_2024": ("2029-30", 2030),
        "spring_statement_2025": ("2029-30", 2030),
    }
    # and not one of them is the November 2025 round's horizon
    assert 2031 not in {p for _, p in got.values()}


def test_supply_side_horizon_for_an_unregistered_round_raises(monkeypatch):
    """A horizon-terminal number whose round has no registered horizon
    must stop, not borrow another round's year."""
    monkeypatch.delitem(_BP10_HORIZON, "spring_budget_2023")
    with pytest.raises(ValueError, match="no forecast horizon registered"):
        _staged(
            monkeypatch,
            [
                _row(
                    metric="supply_side_impact",
                    program="employee_nics_cut",
                    subgroup="labour",
                    variant="tax",
                    period="forecast_horizon",
                    unit_concept="percent_of_potential_gdp",
                    scoring_method="supply_side",
                    scope="measure",
                    aggregate_level="component",
                    fiscal_event="spring_budget_2023",
                    source_column="T2.1:x",
                    description="",
                )
            ],
        )


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
                unit_concept="percent_of_potential_gdp",
                scoring_method="supply_side",
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
    # NOT the null baseline: OBR measures both as deviations from the
    # October 2024 round's pre-measures forecast, and every claim mirrors
    # that world into conditions for queryability
    for s in scores:
        assert s.reform.baseline == {
            "policy": "obr_pre_measures_autumn_budget_2024",
            "counterfactual": "policy_parameters",
        }
        assert s.conditions["baseline_policy"] == (
            "obr_pre_measures_autumn_budget_2024"
        )


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
                unit_concept="percent_of_potential_gdp",
                scoring_method="supply_side",
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
        Metric.GDP_LEVEL_EFFECT.value: UnitConcept.PERCENT_OF_REAL_GDP.value,
        Metric.CPI_INFLATION_EFFECT.value: UnitConcept.PERCENTAGE_POINTS.value,
        Metric.SUPPLY_SIDE_IMPACT.value: UnitConcept.PERCENT_OF_POTENTIAL_GDP.value,
        Metric.DECISIONS_EFFECT_ON_BORROWING.value: UnitConcept.GBP.value,
    }
    # the three percent-shaped quantities never collapse into one label
    assert UnitConcept.PERCENT.value not in units.values()

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
            _BP10_HORIZON[row["fiscal_event"]][1]
            if row["period"] == "forecast_horizon"
            else _fy(row["period"])[0]
        )
        assert score.period == expected


# --- units: validate, THEN map ----------------------------------------------


def test_each_metric_carries_its_own_unit_concept(monkeypatch):
    """Three quantities that all look like "percent" — a GDP-level
    deviation, a CPI effect in percentage points, and an impact on
    potential output — must never share one unit concept."""
    rows = [
        _row(),
        _row(
            metric="cpi_inflation_effect",
            unit_concept="percentage_points",
            subgroup="fuel_duty_freeze_extension",
            source_column="C3.4:Fuel duty freeze extension",
            aggregate_level="component",
            parent="policy_package",
        ),
        _row(
            metric="supply_side_impact",
            program="employee_nics_cut",
            subgroup="labour",
            variant="tax",
            period="forecast_horizon",
            unit_concept="percent_of_potential_gdp",
            scoring_method="supply_side",
            scope="measure",
            aggregate_level="component",
            fiscal_event="autumn_statement_2023",
            source_column="T2.1:Employee NICs cut",
            description="",
        ),
    ]
    scores, _ = _staged(monkeypatch, rows)
    assert [s.unit_concept for s in scores] == [
        UnitConcept.PERCENT_OF_REAL_GDP,
        UnitConcept.PERCENTAGE_POINTS,
        UnitConcept.PERCENT_OF_POTENTIAL_GDP,
    ]


def test_staged_unit_is_validated_not_discarded(monkeypatch):
    """The staged label used to be canon-checked and then thrown away, so
    a GDP row mislabeled gbp_nominal staged as a percent. It must raise."""
    with pytest.raises(ValueError, match="staged unit"):
        _staged(monkeypatch, [_row(unit_concept="gbp_nominal")])
    with pytest.raises(ValueError, match="staged unit"):
        _staged(
            monkeypatch,
            [_row(metric="cpi_inflation_effect", unit_concept="percent_of_real_gdp")],
        )
    # and bare "percent" is not even a registered label any more
    with pytest.raises(ValueError, match="unregistered unit"):
        _staged(monkeypatch, [_row(unit_concept="percent")])


# --- publication provenance -------------------------------------------------


def test_publication_is_per_artifact_with_the_release_date():
    """One generic publications/ URL dated to the newest round misdated
    every earlier round's claims, and the March 2026 rows carried the
    Wayback CAPTURE date rather than the publication date."""
    dates = {k: v["date"] for k, v in PUBLICATIONS.items()}
    assert dates == {
        "efo_november2023_chapter2.xlsx": "2023-11-22",
        "efo_march2024_chapter2.xlsx": "2024-03-06",
        "efo_october2024_chapter2.xlsx": "2024-10-30",
        "efo_november2025_chapter3.xlsx": "2025-11-26",
        "efo_march2026_annex_tables.xlsx": "2026-03-03",
        "obr_briefing_paper_10_supply_side.xlsx": "2025-11-26",
    }
    assert "2026-03-16" not in dates.values()  # the Wayback capture
    for pub in PUBLICATIONS.values():
        assert pub["url"].endswith(".xlsx")  # the dated artifact, not a hub page
        assert pub["url"] != "https://obr.uk/publications/"


def test_unregistered_artifact_raises(monkeypatch):
    with pytest.raises(ValueError, match="no publication registered"):
        _staged(monkeypatch, [_row(artifact="efo_march2027_chapter9.xlsx")])


def test_a_rows_publication_follows_its_own_round(monkeypatch):
    scores, _ = _staged(
        monkeypatch,
        [
            _row(
                fiscal_event="autumn_statement_2023",
                artifact="efo_november2023_chapter2.xlsx",
                source_column="C2.A:Total effect",
            ),
            _row(),
        ],
    )
    assert [s.publication["date"] for s in scores] == ["2023-11-22", "2025-11-26"]


# --- baseline worlds --------------------------------------------------------


def test_baseline_must_match_the_rows_own_round(monkeypatch):
    with pytest.raises(ValueError, match="not interchangeable|are scored against"):
        _staged(
            monkeypatch,
            [
                _row(
                    fiscal_event="autumn_budget_2024",
                    source_column="C2.A:GDP",
                    baseline="obr_pre_measures_autumn_budget_2025",
                )
            ],
        )


def test_baseline_without_a_locator_raises(monkeypatch):
    with pytest.raises(ValueError, match="no locator"):
        _staged(monkeypatch, [_row(baseline_locator="  ")])


@pytest.mark.skipif(not harvest_present, reason="harvest output not present (#75)")
def test_no_claim_defaults_to_current_law():
    from scorecard_db.models import CURRENT_LAW_DESCRIPTOR, baseline_key

    scores, _ = stage()
    null = baseline_key(CURRENT_LAW_DESCRIPTOR)
    assert all(s.reform.baseline is not None for s in scores)
    assert all(s.reform.baseline_key() != null for s in scores)
    # seven rounds, and the counterfactual kind is part of the identity
    worlds = {s.conditions["baseline_policy"] for s in scores}
    assert len(worlds) == 7
    kinds = {
        (s.reform.baseline["policy"], s.reform.baseline["counterfactual"])
        for s in scores
    }
    assert ("obr_pre_measures_spring_statement_2025", "regulatory") in kinds
    assert ("obr_pre_measures_autumn_budget_2024", "del_activity") in kinds


@pytest.mark.skipif(not harvest_present, reason="harvest output not present (#75)")
def test_every_baseline_world_is_registered(tmp_path):
    """The registration gate runs inside the claims' own transaction, so
    an unregistered world rolls the whole replacement back. Assert it
    passes for real — and that it is not passing by registering the null
    world instead."""
    from scorecard_db.ingest_obr_policy_effects import ingest

    ingest(tmp_path / "t.db")
    db = ScorecardDB(tmp_path / "t.db")
    assert db.unregistered_baselines() == []
    labels = [
        r[0]
        for r in db.conn.execute(
            "SELECT DISTINCT b.label FROM external_scores s"
            " JOIN baselines b ON b.baseline_key = s.baseline_key"
            " WHERE s.source = ?",
            (SOURCE,),
        ).fetchall()
    ]
    assert "current_law" not in labels
    assert len(labels) == 11  # the (round, counterfactual) pairs in the data
    db.close()
