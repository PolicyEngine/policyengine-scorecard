"""Tests for the FRR claim-family ingest (#39, staged per #21)."""

import json
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
    assert psncr.value_kind == "gbp"  # never usd on a UK claim

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
    # a per-household average is never bare GBP (a query could sum it)
    assert {s.unit_concept for s in gain} == {UnitConcept.GBP_PER_HOUSEHOLD}

    level = _one(scores, Metric.PARTICIPANT_COUNT)
    assert level.value == 2_800_000
    assert level.reform.framework == "baseline"


def test_frr_rows_score_against_the_pre_frr_world():
    """The costing's own counterfactual is the 25%-cap law the FRR
    replaced — NOT today's current law, which includes the FRR. Every
    reform row must carry the registered pre-FRR baseline descriptor,
    mirrored in conditions (load-bearing, COLLATION worklist item 3)."""
    scores = stage_scores()
    reform_rows = [s for s in scores if s.reform.framework == "policy_ref"]
    assert len(reform_rows) == 7
    for s in reform_rows:
        assert s.reform.baseline == {"policy": "pre_frr_uc_deductions"}
        assert s.conditions["baseline_policy"] == "pre_frr_uc_deductions"
    (level,) = [s for s in scores if s.reform.framework == "baseline"]
    assert "baseline_policy" not in level.conditions


def test_period_must_be_fy_end_year(tmp_path, monkeypatch):
    """The live claim convention (models.py): integer period = FY END
    year. A staged row keyed by start year must fail, never ingest."""
    import scorecard_db.ingest_uk_deductions as mod

    rows = [
        json.loads(line) for line in STAGED.read_text().splitlines() if line.strip()
    ]
    rows[0]["period"] = rows[0]["period"] - 1  # start-year keying
    bad = tmp_path / "claims_staged.jsonl"
    bad.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    monkeypatch.setattr(mod, "STAGED", bad)
    with pytest.raises(ValueError, match="end year"):
        stage_scores()


def test_unknown_identity_values_raise(tmp_path, monkeypatch):
    """Identity values route through the closed registry: an unregistered
    subgroup raises, never passes through."""
    import scorecard_db.ingest_uk_deductions as mod

    rows = [
        json.loads(line) for line in STAGED.read_text().splitlines() if line.strip()
    ]
    target = next(r for r in rows if r["conditions"].get("subgroup"))
    target["conditions"]["subgroup"] = "lone_parents"
    bad = tmp_path / "claims_staged.jsonl"
    bad.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    monkeypatch.setattr(mod, "STAGED", bad)
    with pytest.raises(ValueError, match="unregistered subgroup"):
        stage_scores()


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
        assert s.unit_concept in (
            UnitConcept.GBP,
            UnitConcept.GBP_PER_HOUSEHOLD,
            UnitConcept.HOUSEHOLDS,
        )


def test_round_trip(tmp_path):
    from scorecard_db.models import baseline_key

    assert ingest(tmp_path / "t.db") == {"claims": 8}
    db = ScorecardDB(tmp_path / "t.db")
    n = db.conn.execute(
        "SELECT COUNT(*) FROM external_scores WHERE metric='cash_requirement_change'"
    ).fetchone()[0]
    assert n == 1
    # the pre-FRR world is REGISTERED (the deliberate-registration gate
    # ran inside the write transaction) and every reform row is keyed
    # to it
    pre_frr = baseline_key({"policy": "pre_frr_uc_deductions"})
    assert (
        db.conn.execute(
            "SELECT COUNT(*) FROM baselines WHERE baseline_key = ?", (pre_frr,)
        ).fetchone()[0]
        == 1
    )
    assert (
        db.conn.execute(
            "SELECT COUNT(*) FROM external_scores WHERE baseline_key = ?", (pre_frr,)
        ).fetchone()[0]
        == 7
    )
    # no usd value kinds on UK sources; lane row set by the ingest
    assert (
        db.conn.execute(
            "SELECT COUNT(*) FROM external_scores WHERE value_kind='usd'"
            " AND source IN ('hm_treasury','dwp')"
        ).fetchone()[0]
        == 0
    )
    lane = db.conn.execute(
        "SELECT stage, detail FROM lanes WHERE lane='uk-deductions-frr'"
    ).fetchone()
    assert lane["stage"] == "ingested" and lane["detail"] == "8 claims"
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
