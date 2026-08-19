"""Tests for the UK externals -> DB ingest path (#33).

Mapping-layer tests run on synthetic rows so they hold on any branch;
the staged-file integration tests activate once the five UK adapter
outputs (PRs #43-#47) are present under data/externals/.
"""

import pytest

from scorecard_db import Metric, ScorecardDB, UnitConcept
from scorecard_db.ingest_uk_externals import (
    EXTERNALS,
    STAGERS,
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
    scores, drops = stage_dwp_takeup()
    assert drops == {"range_variants": 2}
    assert len(scores) == 2
    count, rate = scores
    assert count.metric is Metric.PARTICIPANT_COUNT
    assert count.unit_concept is UnitConcept.BENEFIT_UNITS
    assert count.period == 2024
    assert count.conditions["fy"] == "2023-24"
    assert count.conditions["country"] == "UK"
    # the recipient count is the DWP admin caseload PE UK calibrates to
    assert count.calibration_relationship is (
        CalibrationRelationship.CONSUMED_AS_TARGET
    )
    # take-up rates are consumed_as_target: pe-uk take-up parameters cite
    # the same publication
    assert rate.metric is Metric.PARTICIPATION_RATE
    assert rate.conditions["basis"] == "caseload"
    assert rate.calibration_relationship is (CalibrationRelationship.CONSUMED_AS_TARGET)


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
            period="2026-27",
            value=6_900_000_000.0,
        ),
        _row(
            program="income_tax",
            metric="taxpayer_count",
            subgroup="basic_rate",
            geography="UK",
            period="2026-27",
            value=31_400_000.0,
        ),
    ]
    monkeypatch.setattr("scorecard_db.ingest_uk_externals._load", lambda name: rows)
    scores, _ = stage_hmrc()
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
            period="2027-28",
            value=value,
        )
        for program, value in (("vat", 9.2e9), ("insurance_premium_tax", 6.4e8))
    ]
    monkeypatch.setattr("scorecard_db.ingest_uk_externals._load", lambda name: rows)
    scores, _ = stage_hmrc()
    vat, ipt = scores
    assert vat.reform.reform["policy"] != ipt.reform.reform["policy"]
    assert vat.reform.key() != ipt.reform.key()
    assert vat.claim_id() != ipt.claim_id()


def test_calibration_comes_from_the_registry(monkeypatch):
    """No relationship is decided in the ingest; unassigned pairs raise."""
    from scorecard_db.models import CalibrationRelationship as CR
    from scorecard_db.relationships import uk_relationship

    assert uk_relationship("dwp_takeup", Metric.PARTICIPATION_RATE)[0] is (
        CR.CONSUMED_AS_TARGET
    )
    # entitled non-recipients are an algebraic derivative of a consumed
    # rate (takeup = R/(R+ENR)) — "nor anything derived from such"
    assert uk_relationship("dwp_takeup", Metric.PARTICIPATION_GAP_COUNT)[0] is (
        CR.CONSUMED_AS_TARGET
    )
    assert uk_relationship("dwp_takeup", Metric.UNCLAIMED_BENEFIT_AMOUNT)[0] is (
        CR.CONSUMED_AS_TARGET
    )
    # OBR consumption turns on the year, not the metric
    assert uk_relationship("obr", Metric.BENEFIT_COST, "outturn")[0] is (
        CR.CONSUMED_AS_TARGET
    )
    assert uk_relationship("obr", Metric.BENEFIT_COST, "forecast")[0] is CR.HELD_OUT
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
    scores, drops = stage_ukmod()
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
        "poverty_line": "60",
        "housing_costs": "bhc",
    }


def test_ukmod_unknown_metric_raises(monkeypatch):
    monkeypatch.setattr(
        "scorecard_db.ingest_uk_externals._load",
        lambda name: [_row(metric="mystery", variant="ukmod", period="2025")],
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
    assert set(summary["claims"]) == set(STAGERS)
    assert all(n > 0 for n in summary["claims"].values())
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
    db.close()


def _obr_row(**over):
    base = _row(
        source="obr",
        program="pension_credit",
        metric="welfare_spending",
        geography="UK",
        unit_concept="gbp",
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
        _obr_row(),
        _obr_row(
            program="total_welfare",
            aggregate_level="total",
            parent=None,
            value=310_000_000_000.0,
        ),
    ]
    monkeypatch.setattr("scorecard_db.ingest_uk_externals._load", lambda name: rows)
    scores, _ = stage_obr()
    leaf, total = scores
    assert leaf.conditions["aggregate_level"] == "component"
    assert leaf.conditions["parent"] == "dwp_social_security"
    assert total.conditions["aggregate_level"] == "total"
    assert "parent" not in total.conditions  # top of the roll-up


def test_hierarchy_condition_keys_are_registered():
    from scorecard_db.models import STANDARD_CONDITIONS

    assert {"aggregate_level", "parent", "component"} <= STANDARD_CONDITIONS


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
