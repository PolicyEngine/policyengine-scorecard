"""Tests for the FRR claim-family ingest (#39, staged per #21)."""

import pytest

from scorecard_db import Metric, ScorecardDB, UnitConcept
from scorecard_db.ingest_uk_deductions import STAGED, ingest, stage_scores

pytestmark = pytest.mark.skipif(not STAGED.exists(), reason="FRR staging not present")


def _one(scores, metric, **conds):
    hits = [
        s
        for s in scores
        if s.metric is metric
        and all(s.conditions.get(k) == v for k, v in conds.items())
    ]
    assert len(hits) == 1, (metric, conds, len(hits))
    return hits[0]


def test_stage_headline_values():
    scores = stage_scores()
    assert len(scores) == 8
    psncr = _one(scores, Metric.CASH_REQUIREMENT_CHANGE)
    assert psncr.value == 385_000_000
    assert psncr.period == 2030
    assert psncr.conditions["fiscal_measure"] == "psncr"
    assert psncr.reform.reform["policy"] == "uc_fair_repayment_rate"

    hmt_gainers = [
        s
        for s in scores
        if s.metric is Metric.GAINER_COUNT
        and s.source == "hm_treasury"
        and "subgroup" not in s.conditions
    ]
    assert len(hmt_gainers) == 1 and hmt_gainers[0].value == 1_200_000

    with_children = [
        s
        for s in scores
        if s.metric is Metric.GAINER_COUNT
        and s.conditions.get("subgroup") == "families_with_children"
    ]
    assert {s.value for s in with_children} == {700_000}
    assert {s.source for s in with_children} == {"hm_treasury", "dwp"}

    gain = [s for s in scores if s.metric is Metric.AVERAGE_ANNUAL_GAIN]
    assert {s.value for s in gain} == {420.0}

    level = _one(scores, Metric.PARTICIPANT_COUNT)
    assert level.value == 2_800_000
    assert level.reform.framework == "baseline"


def test_no_psnb_shaped_claims():
    # PSNCR-never-PSNB rule (#21): the FRR family must not stage any
    # revenue_change row a PSNB comparison could silently join against.
    scores = stage_scores()
    assert all(s.metric is not Metric.REVENUE_CHANGE for s in scores)


def test_every_claim_carries_quote_and_publication():
    for s in stage_scores():
        assert s.source_column  # the verbatim quote
        assert s.publication.get("url") and s.publication.get("date")
        assert s.conditions["country"] == "UK"
        assert s.unit_concept in (UnitConcept.GBP, UnitConcept.HOUSEHOLDS)


def test_round_trip(tmp_path):
    assert ingest(tmp_path / "t.db") == {"claims": 8}
    db = ScorecardDB(tmp_path / "t.db")
    n = db.conn.execute(
        "SELECT COUNT(*) FROM external_scores WHERE metric='cash_requirement_change'"
    ).fetchone()[0]
    assert n == 1
    db.close()
