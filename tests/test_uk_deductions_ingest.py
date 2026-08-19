"""Tests for the FRR claim-family ingest (#39, staged per #21)."""

from pathlib import Path

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


FRR_DIR = Path(__file__).resolve().parent.parent / "sources" / "harvest-uk-deductions"


def _pdf_text(path):
    pypdf = pytest.importorskip("pypdf")
    import re

    reader = pypdf.PdfReader(path)
    text = " ".join((p.extract_text() or "") for p in reader.pages)
    return re.sub(r"\s+", " ", text)


def test_420_quotes_are_two_distinct_verbatim_sentences():
    """Rows 2 and 3 cite the SAME figure from two DIFFERENT passages of
    AB2024 (para 4.111's "£420 per year" sentence vs the para 2.30/5.134
    "£420 a year" sentence). Both must appear verbatim — neither is a
    reworded fragment of the other."""
    text = _pdf_text(FRR_DIR / "frr" / "autumn_budget_2024.pdf")
    assert (
        "This will mean 1.2 million households will be better off by "
        "£420 per year on average as a result of this change." in text
    )
    assert "with households expected to be better off by £420 a year on average" in text


def test_frr_costing_absence_is_machine_checked():
    """The 'verified absence' of an FRR costing line is not trust-me
    prose: the AB2024 policy costings document (93 pages) contains zero
    occurrences of the measure name. The FRR is a financial transaction
    (PSNCR, not PSNB), so a costing line appearing in a future re-vendor
    would mean the wrong document or a mis-staged claim."""
    text = _pdf_text(FRR_DIR / "frr" / "autumn_budget_2024_policy_costings.pdf")
    assert "Fair Repayment Rate" not in text
    assert "repayment rate" not in text.lower()
