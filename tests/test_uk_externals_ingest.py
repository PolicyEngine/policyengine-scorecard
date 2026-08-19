"""Tests for the UK externals -> DB ingest path (#33).

Mapping-layer tests run on synthetic rows so they hold on any branch;
the staged-file integration tests activate once the five UK adapter
outputs (PRs #43-#47) are present under data/externals/.
"""

import pytest

from scorecard_db import Metric, ScorecardDB, UnitConcept
from scorecard_db.ingest_uk_externals import (
    EXTERNALS,
    _fy,
    stage_dwp_takeup,
    stage_hmrc,
    stage_ukmod,
)
from scorecard_db.models import CalibrationRelationship


def _row(**over):
    base = {
        "source": "x",
        "country": "UK",
        "program": "pension_credit",
        "metric": "recipients_count",
        "subgroup": "total",
        "variant": None,
        "geography": "GB",
        "unit_concept": "benefit_units",
        "period": "FYE 2024",
        "value": 1_320_000.0,
        "status": "ok",
        "source_column": "PC1:Pension Credit Overall",
    }
    base.update(over)
    return base


def test_fy_parsing():
    assert _fy("FYE 2024") == (2024, "2023-24")
    assert _fy("2023-24") == (2024, "2023-24")
    assert _fy("2024/25") == (2025, "2024-25")
    with pytest.raises(ValueError):
        _fy("FY2024")


def test_dwp_mapping_and_drops(monkeypatch):
    rows = [
        _row(),
        _row(metric="caseload_takeup_rate", value=0.62),
        _row(metric="caseload_takeup_rate", variant="range_low", value=0.59),
        _row(metric="caseload_takeup_rate", variant="range_high", value=0.64),
    ]
    monkeypatch.setattr("scorecard_db.ingest_uk_externals._load", lambda name: rows)
    scores, ledger, drops = stage_dwp_takeup()
    assert drops == {"range_variants": 2}
    # The recipient count is a published ADMIN cell: it routes to Ledger
    # (boundary rule 2026-08-02), never to a claim.
    assert len(scores) == 1 and len(ledger) == 1
    (rate,), (admin,) = scores, ledger
    assert admin["metric"] == "recipients_count"
    assert admin["fy"] == "2023-24"
    assert admin["fact_id"].startswith("uk-admin-")
    assert admin["routing"].startswith("ledger")
    # PC take-up rate: the engine PARAMETER cites the FYE-2020 edition of
    # this series -> seed_source, never consumed (evidence in
    # relationships.py, read 2026-08-19).
    assert rate.metric is Metric.PARTICIPATION_RATE
    assert rate.period == 2024
    assert rate.conditions["fy"] == "2023-24"
    assert rate.conditions["basis"] == "caseload"
    assert rate.calibration_relationship is (CalibrationRelationship.SEED_SOURCE)


def test_dwp_unknown_variant_raises(monkeypatch):
    monkeypatch.setattr(
        "scorecard_db.ingest_uk_externals._load",
        lambda name: [_row(variant="central_ish")],
    )
    with pytest.raises(ValueError, match="unknown variant"):
        stage_dwp_takeup()


def test_hmrc_reckoner_rows_are_reform_claims(monkeypatch):
    rows = [
        _row(
            program="income_tax",
            metric="revenue_effect",
            subgroup="Change basic rate by 1p",
            geography="UK",
            unit_concept="gbp_nominal",
            period="2026-27",
            value=6_900_000_000.0,
        ),
        _row(
            program="income_tax",
            metric="taxpayer_count",
            subgroup="basic_rate",
            geography="UK",
            unit_concept="individuals",
            period="2026-27",
            value=31_400_000.0,
        ),
    ]
    monkeypatch.setattr("scorecard_db.ingest_uk_externals._load", lambda name: rows)
    scores, _, _ = stage_hmrc()
    reckoner, level = scores
    assert reckoner.metric is Metric.REVENUE_CHANGE
    assert reckoner.reform.framework == "policy_ref"
    assert reckoner.reform.reform["policy"] == "trr_income_tax_change_basic_rate_by_1p"
    assert reckoner.reform.baseline["policy"] == ("hmrc_indexed_baseline_spring_2025")
    assert reckoner.conditions["option"] == "Change basic rate by 1p"
    assert reckoner.conditions["baseline_policy"] == (
        "hmrc_indexed_baseline_spring_2025"
    )
    assert level.metric is Metric.TAXPAYER_COUNT
    assert level.reform.framework == "baseline"
    assert level.conditions["subgroup"] == "basic_rate"


def test_reckoner_unknown_unit_raises(monkeypatch):
    """Regression (round-2 gate probe): the reckoner branch returns
    early and used to bypass the closed unit registry entirely — an
    unknown unit was accepted and silently emitted as GBP."""
    rows = [
        _row(
            program="income_tax",
            metric="revenue_effect",
            subgroup="Change basic rate by 1p",
            geography="UK",
            unit_concept="usd_million",
            period="2026-27",
            value=6_900_000_000.0,
        )
    ]
    monkeypatch.setattr("scorecard_db.ingest_uk_externals._load", lambda name: rows)
    with pytest.raises(ValueError, match="unregistered unit value 'usd_million'"):
        stage_hmrc()


def test_reckoner_slug_separates_tax_heads(monkeypatch):
    """HMRC prints the same change label under two different tax heads.

    "Change standard rate by 1 percentage point" appears under both VAT
    and Insurance Premium Tax. Slugged on the description alone the two
    collapse into ONE reform world, and a single PE compute of a VAT
    change would be joined as the counterpart to the IPT claim — worlds
    that differ 14x in magnitude.
    """
    rows = [
        _row(
            program=program,
            metric="revenue_effect",
            subgroup="Change standard rate by 1 percentage point",
            geography="UK",
            unit_concept="gbp_nominal",
            period="2027-28",
            value=value,
        )
        for program, value in (("vat", 9.2e9), ("insurance_premium_tax", 6.4e8))
    ]
    monkeypatch.setattr("scorecard_db.ingest_uk_externals._load", lambda name: rows)
    scores, _, _ = stage_hmrc()
    vat, ipt = scores
    assert vat.reform.reform["policy"] != ipt.reform.reform["policy"]
    assert vat.reform.key() != ipt.reform.key()
    assert vat.claim_id() != ipt.claim_id()


def test_calibration_comes_from_the_registry(monkeypatch):
    """No relationship is decided in the ingest; unassigned pairs raise."""
    from scorecard_db.models import CalibrationRelationship as CR
    from scorecard_db.relationships import uk_relationship

    # PC family: engine parameter cites an OLDER edition -> seed_source
    assert (
        uk_relationship(
            "dwp_takeup",
            Metric.PARTICIPATION_RATE,
            program="pension_credit",
            kind="takeup_rate",
        )[0]
        is CR.SEED_SOURCE
    )
    assert (
        uk_relationship(
            "dwp_takeup",
            Metric.PARTICIPATION_GAP_COUNT,
            program="guarantee_credit",
            kind="modeled_estimate",
        )[0]
        is CR.SEED_SOURCE
    )
    # HB: engine sets take-up = 1 by stated design -> held_out
    assert (
        uk_relationship(
            "dwp_takeup",
            Metric.PARTICIPATION_RATE,
            program="housing_benefit_pensioners",
            kind="takeup_rate",
        )[0]
        is CR.HELD_OUT
    )
    # OBR: consumption is per LINE (pe-uk-data@dd68c73's 12 named rows);
    # outturn cells must never reach relationship assignment at all.
    assert (
        uk_relationship(
            "obr", Metric.BENEFIT_COST, program="pension_credit", kind="forecast"
        )[0]
        is CR.CONSUMED_AS_TARGET
    )
    assert (
        uk_relationship(
            "obr", Metric.BENEFIT_COST, program="christmas_bonus", kind="forecast"
        )[0]
        is CR.HELD_OUT
    )
    with pytest.raises(ValueError, match="route to Ledger"):
        uk_relationship(
            "obr", Metric.BENEFIT_COST, program="pension_credit", kind="outturn"
        )
    # HMRC: shared SPI base -> seed_source for levels; reckoner held out
    assert (
        uk_relationship(
            "uk_hmrc", Metric.TAX_LIABILITY, program="income_tax", kind="liabilities"
        )[0]
        is CR.SEED_SOURCE
    )
    assert (
        uk_relationship(
            "uk_hmrc", Metric.REVENUE_CHANGE, program="vat", kind="reckoner"
        )[0]
        is CR.HELD_OUT
    )
    assert uk_relationship("ukmod", Metric.CASELOAD)[0] is CR.HELD_OUT
    with pytest.raises(ValueError, match="no UK calibration relationship"):
        uk_relationship("some_new_source", Metric.CASELOAD)


def test_poverty_counts_can_never_be_consumed():
    """HBAI counts are survey-derived; the doctrine covers derivatives."""
    from scorecard_db.models import CalibrationRelationship as CR
    from scorecard_db.relationships import never_calibrate, uk_relationship

    assert never_calibrate(Metric.POVERTY_COUNT)
    assert never_calibrate(Metric.POVERTY_RATE)
    for metric in (Metric.POVERTY_COUNT, Metric.POVERTY_RATE):
        rel, basis = uk_relationship("dwp_hbai", metric)
        assert rel is CR.HELD_OUT
        assert "PERMANENT holdout" in basis


def test_ukmod_primary_variant_only(monkeypatch):
    rows = [
        _row(
            program="universal_credit",
            metric="caseload",
            variant="ukmod",
            geography="UK",
            unit_concept="families",
            period="2025",
            value=6_941_000.0,
        ),
        _row(
            program="universal_credit",
            metric="caseload",
            variant="official_as_cited",
            geography="UK",
            unit_concept="families",
            period="2025",
            value=6_493_000.0,
        ),
        _row(
            program="poverty",
            metric="poverty_rate_below_60pct_median",
            subgroup="children",
            variant="ukmod",
            geography="UK",
            unit_concept="fraction",
            period="2025",
            value=0.19,
        ),
    ]
    monkeypatch.setattr("scorecard_db.ingest_uk_externals._load", lambda name: rows)
    scores, _, drops = stage_ukmod()
    assert drops == {"non_primary_variants": 1}
    caseload, poverty = scores
    assert caseload.metric is Metric.CASELOAD
    assert caseload.unit_concept is UnitConcept.FAMILIES
    assert caseload.time_basis.value == "annual"
    assert caseload.source_model == "ukmod_b2026.01"
    assert poverty.metric is Metric.POVERTY_RATE
    assert poverty.conditions == {
        "country": "UK",
        "geography": "UK",
        "subgroup": "children",
        "poverty_line": "relative_60_median",
        "housing_costs": "bhc",
        "equivalisation": "modified_oecd",
    }


def test_ukmod_unknown_metric_raises(monkeypatch):
    monkeypatch.setattr(
        "scorecard_db.ingest_uk_externals._load",
        lambda name: [
            _row(
                metric="mystery",
                variant="ukmod",
                geography="UK",
                unit_concept="families",
                period="2025",
            )
        ],
    )
    with pytest.raises(ValueError, match="unknown metric"):
        stage_ukmod()


# --- integration on the real adapter outputs (post #43-#47 merge) --------

_FILES = {
    "dwp_takeup": "dwp-takeup",
    "dwp_hbai": "hbai-poverty",
    "uk_hmrc": "hmrc-personal-tax",
    "obr": "obr-welfare",
    "ukmod": "ukmod-stats",
}

externals_present = all((EXTERNALS / f"{f}.json").exists() for f in _FILES.values())


@pytest.mark.skipif(
    not externals_present, reason="UK adapter outputs not present (PRs #43-#47)"
)
def test_full_ingest_round_trip(tmp_path):
    from scorecard_db.ingest_uk_externals import ingest

    summary = ingest(tmp_path / "t.db")
    # Exact accounting (adjudication blocker 7 — a drifted adapter
    # regeneration must fail, never pass a >0 check): 15,851 claims +
    # 1,073 Ledger facts = 16,924 admitted rows; + 1,829 deliberate
    # drops = 18,753, every adapter row.
    assert summary["claims"] == {
        "dwp_takeup": 1092,
        "dwp_hbai": 13056,
        "uk_hmrc": 723,
        "obr": 222,
        "ukmod": 758,
    }
    assert summary["ledger"] == {"dwp_takeup": 546, "uk_hmrc": 490, "obr": 37}
    assert summary["drops"] == {
        "dwp_takeup": {"range_variants": 1456},
        "ukmod": {"non_primary_variants": 373},
    }
    db = ScorecardDB(tmp_path / "t.db")
    # exactly-one-match works for a reckoner claim keyed by option + fy —
    # the join the campaign's hmrc_reckoner_t2 family needs once its
    # descriptors are re-emitted with the change label
    hits = db.conn.execute(
        "SELECT value FROM external_scores WHERE source='uk_hmrc'"
        " AND metric='revenue_change'"
        " AND json_extract(conditions, '$.option') = 'Change basic rate by 1p'"
        " AND json_extract(conditions, '$.fy') = '2026-27'"
    ).fetchall()
    assert len(hits) == 1
    assert hits[0][0] == pytest.approx(6_900_000_000)
    # no reform world may span two tax heads (the VAT/IPT collision)
    spanning = db.conn.execute(
        "SELECT reform_key FROM external_scores WHERE metric='revenue_change'"
        " GROUP BY reform_key"
        " HAVING COUNT(DISTINCT json_extract(conditions, '$.program')) > 1"
    ).fetchall()
    assert not spanning
    # and no survey-derived poverty claim may be marked consumed
    consumed_poverty = db.conn.execute(
        "SELECT COUNT(*) FROM external_scores"
        " WHERE metric IN ('poverty_rate','poverty_count')"
        " AND calibration_relationship != 'held_out'"
    ).fetchone()[0]
    assert consumed_poverty == 0
    # Relationship distribution pinned per source — the doctrine-true
    # shape, from the consumption surfaces read at the certified pins.
    rel = {
        (r[0], r[1]): r[2]
        for r in db.conn.execute(
            "SELECT source, calibration_relationship, COUNT(*)"
            " FROM external_scores GROUP BY 1, 2"
        )
    }
    assert rel == {
        ("dwp_hbai", "held_out"): 13056,
        ("dwp_takeup", "held_out"): 78,
        ("dwp_takeup", "seed_source"): 1014,
        ("obr", "consumed_as_target"): 78,
        ("obr", "held_out"): 144,
        ("uk_hmrc", "held_out"): 225,
        ("uk_hmrc", "seed_source"): 498,
        ("ukmod", "held_out"): 758,
    }
    # No admin outturn ever reaches claims.
    assert (
        db.conn.execute(
            "SELECT COUNT(*) FROM external_scores"
            " WHERE json_extract(conditions, '$.basis') = 'outturn'"
        ).fetchone()[0]
        == 0
    )

    # Semantic condition pins (round-2 gate): count-only accounting
    # cannot detect loss of the load-bearing anchor/equivalisation
    # conditions — pin the values themselves.
    def _one(sql: str) -> int:
        return db.conn.execute(sql).fetchone()[0]

    # HBAI absolute lines: every absolute row carries an anchor, in the
    # Notes-sheet distribution (Note 3: FYE-2025 for 2021/22 on,
    # FYE-2011 before, windows straddling the break = explicit mixed).
    anchors = dict(
        db.conn.execute(
            "SELECT json_extract(conditions, '$.poverty_line_anchor'),"
            " COUNT(*) FROM external_scores WHERE source='dwp_hbai' AND"
            " json_extract(conditions, '$.poverty_line')"
            " = 'absolute_60_fixed_median' GROUP BY 1"
        ).fetchall()
    )
    assert anchors == {
        "fye_2011": 5632,
        "fye_2025": 480,
        "mixed_fye2011_fye2025": 416,
    }
    # pre-break single year -> FYE-2011; post-break -> FYE-2025
    for fy, anchor in (("2019-20", "fye_2011"), ("2023-24", "fye_2025")):
        got = {
            r[0]
            for r in db.conn.execute(
                "SELECT DISTINCT json_extract(conditions,"
                " '$.poverty_line_anchor') FROM external_scores"
                " WHERE source='dwp_hbai' AND json_extract(conditions,"
                f" '$.fy') = '{fy}' AND json_extract(conditions,"
                " '$.poverty_line') = 'absolute_60_fixed_median'"
            )
        }
        assert got == {anchor}, (fy, got)
    # every mixed anchor is a multi-year window, never a single year
    assert (
        _one(
            "SELECT COUNT(*) FROM external_scores WHERE source='dwp_hbai'"
            " AND json_extract(conditions, '$.poverty_line_anchor')"
            " = 'mixed_fye2011_fye2025' AND json_extract(conditions,"
            " '$.window_kind') IS NULL"
        )
        == 0
    )
    # HBAI equivalisation rides every row and tracks housing costs
    # (modified OECD; companion scale AHC).
    assert (
        _one(
            "SELECT COUNT(*) FROM external_scores WHERE source='dwp_hbai'"
            " AND (json_extract(conditions, '$.equivalisation') IS NULL"
            " OR json_extract(conditions, '$.equivalisation') <> CASE"
            " json_extract(conditions, '$.housing_costs') WHEN 'ahc'"
            " THEN 'modified_oecd_companion_ahc'"
            " ELSE 'modified_oecd' END)"
        )
        == 0
    )
    # UKMOD distribution statistics (Gini + income levels) all carry
    # BHC + modified-OECD — and the guard cannot pass vacuously.
    ukmod_dist = dict(
        db.conn.execute(
            "SELECT metric, COUNT(*) FROM external_scores WHERE"
            " source='ukmod' AND metric IN ('gini','income_statistic')"
            " GROUP BY 1"
        ).fetchall()
    )
    assert ukmod_dist == {"gini": 8, "income_statistic": 56}
    assert (
        _one(
            "SELECT COUNT(*) FROM external_scores WHERE source='ukmod'"
            " AND metric IN ('gini','income_statistic')"
            " AND (json_extract(conditions, '$.equivalisation')"
            " <> 'modified_oecd' OR json_extract(conditions,"
            " '$.housing_costs') <> 'bhc')"
        )
        == 0
    )
    db.close()


def _obr_row(**over):
    base = _row(
        source="obr",
        program="pension_credit",
        metric="welfare_spending",
        geography="UK",
        unit_concept="gbp_nominal",
        period="2023-24",
        value=5_500_000_000.0,
        aggregate_level="component",
        parent="dwp_social_security",
    )
    base.update(over)
    return base


def test_obr_hierarchy_lands_in_conditions(monkeypatch):
    """aggregate_level + parent must ride on every OBR claim: without
    them the 259 rows are sibling benefit_cost claims and any consumer
    summing OBR benefit_cost by FY double-counts totals against their
    components."""
    from scorecard_db.ingest_uk_externals import stage_obr

    rows = [
        _obr_row(period="2025-26"),
        _obr_row(
            program="total_welfare",
            aggregate_level="total",
            parent=None,
            period="2025-26",
            value=310_000_000_000.0,
        ),
    ]
    monkeypatch.setattr("scorecard_db.ingest_uk_externals._load", lambda name: rows)
    scores, _, _ = stage_obr()
    leaf, total = scores
    assert leaf.conditions["aggregate_level"] == "component"
    assert leaf.conditions["parent"] == "dwp_social_security"
    assert total.conditions["aggregate_level"] == "total"
    assert "parent" not in total.conditions  # top of the roll-up


def test_hierarchy_condition_keys_are_registered():
    from scorecard_db.models import STANDARD_CONDITIONS

    assert {
        "aggregate_level",
        "parent",
        "component",
        "equivalisation",
        "poverty_line_anchor",
    } <= STANDARD_CONDITIONS


def test_load_gate_rejects_unhandled_adapter_fields(tmp_path, monkeypatch):
    """The require_fields gate (harvest.py contract): a new adapter
    column must be handled deliberately, never silently dropped — the
    OBR hierarchy columns slipped through exactly this way."""
    import json as _json

    from scorecard_db import ingest_uk_externals as mod

    (tmp_path / "obr-welfare.json").write_text(
        _json.dumps([_obr_row(surprise_column=1)])
    )
    monkeypatch.setattr(mod, "EXTERNALS", tmp_path)
    with pytest.raises(ValueError, match="unhandled staged fields.*surprise_column"):
        mod._load("obr-welfare")


# --- closed identity registry (uk_aliases) --------------------------------


def test_alias_registry_is_closed():
    from scorecard_db.uk_aliases import canon

    with pytest.raises(ValueError, match="unregistered program"):
        canon("ukmod", "program", "brand_new_benefit")
    with pytest.raises(ValueError, match="unregistered poverty_line"):
        canon("ukmod", "poverty_line", "40")


def test_cross_source_poverty_triangle():
    # HBAI-relative and UKMOD-60 canonicalize to the SAME world by
    # deliberate construction; HBAI-absolute and UKMOD-50/70 never join
    # either of them.
    from scorecard_db.uk_aliases import canon

    hbai_rel = canon("dwp_hbai", "poverty_line", "relative")
    ukmod_60 = canon("ukmod", "poverty_line", "60")
    assert hbai_rel == ukmod_60 == "relative_60_median"
    assert canon("dwp_hbai", "poverty_line", "absolute") not in (
        hbai_rel,
        canon("ukmod", "poverty_line", "50"),
        canon("ukmod", "poverty_line", "70"),
    )
    for src_, basis in (("dwp_hbai", "bhc"), ("ukmod", "bhc")):
        assert canon(src_, "housing_costs", basis) == "bhc"


def test_winter_fuel_alias_and_distinct_pairs():
    from scorecard_db.uk_aliases import DISTINCT, canon

    # same benefit, two official names -> one canonical program
    assert canon("ukmod", "program", "winter_fuel_allowance") == (
        canon("obr", "program", "winter_fuel_payment")
    )
    # near-neighbours recorded DISTINCT must canonicalize apart
    assert ("dwp_takeup:housing_benefit_pensioners", "ukmod:housing_benefit") in (
        DISTINCT
    )
    assert canon("dwp_takeup", "program", "housing_benefit_pensioners") != (
        canon("ukmod", "program", "housing_benefit")
    )
    assert canon("dwp_takeup", "unit", "benefit_units") != canon(
        "ukmod", "unit", "families"
    )


# --- Ledger routing --------------------------------------------------------


def test_obr_outturn_routes_to_ledger_with_consuming_pin(monkeypatch):
    from scorecard_db.ingest_uk_externals import stage_obr

    rows = [
        _obr_row(period="2024-25"),  # outturn column
        _obr_row(period="2024-25", program="christmas_bonus", parent=None),
        _obr_row(period="2025-26"),  # forecast
    ]
    monkeypatch.setattr("scorecard_db.ingest_uk_externals._load", lambda name: rows)
    scores, ledger, _ = stage_obr()
    assert len(scores) == 1 and len(ledger) == 2
    by_prog = {r["program"]: r for r in ledger}
    # pension_credit is a consumed 4.9 line -> the pin is named
    assert "pe-uk-data@dd68c73" in by_prog["pension_credit"]["consumed_by"]
    # christmas_bonus is not consumed -> no pin, still Ledger (outturn)
    assert by_prog["christmas_bonus"]["consumed_by"] is None
    assert scores[0].conditions["basis"] == "forecast"


def test_hmrc_outturn_routes_to_ledger(monkeypatch):
    from scorecard_db.ingest_uk_externals import stage_hmrc

    rows = [
        _row(
            program="income_tax",
            metric="taxpayer_count",
            subgroup="total",
            geography="UK",
            unit_concept="individuals",
            period="2023-24",  # SPI outturn year
            value=34_500_000.0,
        ),
        _row(
            program="income_tax",
            metric="taxpayer_count",
            subgroup="total",
            geography="UK",
            unit_concept="individuals",
            period="2025-26",  # projection
            value=35_100_000.0,
        ),
    ]
    monkeypatch.setattr("scorecard_db.ingest_uk_externals._load", lambda name: rows)
    scores, ledger, _ = stage_hmrc()
    assert len(scores) == 1 and len(ledger) == 1
    assert ledger[0]["fy"] == "2023-24"
    assert "SPI" in ledger[0]["consumed_by"]
    assert scores[0].conditions["fy"] == "2025-26"


def test_ledger_facts_are_deterministic(monkeypatch):
    from scorecard_db.ingest_uk_externals import stage_obr

    rows = [_obr_row(period="2024-25")]
    monkeypatch.setattr("scorecard_db.ingest_uk_externals._load", lambda name: rows)
    _, first, _ = stage_obr()
    _, again, _ = stage_obr()
    assert first == again
    assert first[0]["fact_id"] == again[0]["fact_id"]


# --- atomicity + accounting ------------------------------------------------


@pytest.mark.skipif(
    not externals_present, reason="UK adapter outputs not present (PRs #43-#47)"
)
def test_write_phase_failure_rolls_back(tmp_path, monkeypatch):
    import sqlite3

    from scorecard_db.ingest_uk_externals import ingest

    first = ingest(tmp_path / "t.db")

    real = ScorecardDB.score_row
    calls = {"n": 0}

    def sabotaged(s):
        row = real(s)
        calls["n"] += 1
        if calls["n"] == 5000:
            return row[:17] + ("bogus_status",) + row[18:]
        return row

    monkeypatch.setattr(ScorecardDB, "score_row", staticmethod(sabotaged))
    with pytest.raises(sqlite3.IntegrityError):
        ingest(tmp_path / "t.db")
    monkeypatch.undo()

    db = ScorecardDB(tmp_path / "t.db")
    counts = {
        r[0]: r[1]
        for r in db.conn.execute(
            "SELECT source, COUNT(*) FROM external_scores GROUP BY 1"
        )
    }
    db.close()
    assert counts == first["claims"]


@pytest.mark.skipif(
    not externals_present, reason="UK adapter outputs not present (PRs #43-#47)"
)
def test_unregistered_baseline_gate_rolls_back(tmp_path, monkeypatch):
    """The deliberate-registration gate guards PERSISTENCE, not just the
    post-commit state (round-2 gate probe: registration used to run
    after the claims committed, so the raise validated a DB it had
    already failed to protect). A claim referencing an unregistered
    baseline world must leave the DB byte-identical: prior claims
    intact, zero poison claims, and the poison world never registered."""
    import dataclasses

    from scorecard_db import ingest_uk_externals as mod
    from scorecard_db.models import ReformRef, baseline_key

    first = mod.ingest(tmp_path / "t.db")
    poison_baseline = {"policy": "never_registered_world"}

    real = mod.stage_all

    def poisoned():
        scores, ledger, summary = real()
        bad = dataclasses.replace(
            scores[0],
            reform=ReformRef(
                framework="policy_ref",
                reform={"policy": "poison_probe"},
                baseline=poison_baseline,
            ),
        )
        return scores + [bad], ledger, summary

    monkeypatch.setattr(mod, "stage_all", poisoned)
    with pytest.raises(ValueError, match="not in the registry"):
        mod.ingest(tmp_path / "t.db")
    monkeypatch.undo()

    db = ScorecardDB(tmp_path / "t.db")
    counts = {
        r[0]: r[1]
        for r in db.conn.execute(
            "SELECT source, COUNT(*) FROM external_scores GROUP BY 1"
        )
    }
    poison_key = baseline_key(poison_baseline)
    poison_claims = db.conn.execute(
        "SELECT COUNT(*) FROM external_scores WHERE baseline_key = ?",
        (poison_key,),
    ).fetchone()[0]
    poison_registered = db.conn.execute(
        "SELECT COUNT(*) FROM baselines WHERE baseline_key = ?",
        (poison_key,),
    ).fetchone()[0]
    db.close()
    assert counts == first["claims"]
    assert poison_claims == 0
    assert poison_registered == 0


@pytest.mark.skipif(
    not externals_present, reason="UK adapter outputs not present (PRs #43-#47)"
)
def test_accounting_drift_fails_loudly(monkeypatch):
    from scorecard_db import ingest_uk_externals as mod

    real = mod.stage_ukmod

    def drifted():
        scores, ledger, drops = real()
        return scores[:-1], ledger, drops  # one row short

    monkeypatch.setitem(mod.STAGERS, "ukmod", drifted)
    with pytest.raises(ValueError, match="claim accounting drifted"):
        mod.stage_all()
