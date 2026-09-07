"""The IFS + Resolution Foundation ingest (#86).

Two families were harvested in the 2026-08-02 UK sweep and never
ingested. What is pinned here is the thing that could most easily go
wrong quietly: the disposition of the 145 rows that carry only a
harvest-side PROPOSAL, and the 8 rows that are not the publisher's
claims at all.
"""

import gzip
import json
import sqlite3
from pathlib import Path

import pytest

from scorecard_db import ScorecardDB
from scorecard_db.ingest_uk_thinktanks import (
    DISPOSITIONS,
    DROPS,
    FAMILIES,
    HARVEST,
    _EXPECTED,
    check_accounting,
    ingest,
    stage,
)
from scorecard_db.models import CalibrationRelationship, Metric

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def staged():
    return stage()


def _raw(family):
    p = HARVEST / family / "claims_staged.jsonl.gz"
    return [json.loads(line) for line in gzip.open(p, "rt")]


# --- the accounting --------------------------------------------------------


def test_every_staged_row_is_ingested_or_tallied(staged):
    """339 read = 314 ingested + 25 dropped. The 145 proposal-only rows
    could have shrunk silently to zero and nobody would have seen it."""
    scores, acct = staged
    assert acct["read"] == 339
    assert acct["ingested"] == len(scores) == 314
    assert acct["dropped"] == 25
    assert acct["ingested"] + acct["dropped"] == acct["read"]
    check_accounting(acct)


def test_the_harvest_still_holds_what_the_accounting_claims():
    assert len(_raw("uk_ifs")) == 268
    assert len(_raw("uk_resolution_foundation")) == 71


def test_every_drop_states_a_reason(staged):
    _, acct = staged
    for key, entry in acct["drops"].items():
        assert entry["rows"] > 0
        assert len(entry["reason"]) > 80, key


def test_claim_ids_do_not_collide(staged):
    scores, _ = staged
    assert len({s.claim_id() for s in scores}) == len(scores)


# --- a proposal is not a decision ------------------------------------------


def test_all_proposal_only_rows_are_dispositioned():
    """145 rows carry `proposed_metric` and no `metric`. Every proposed
    name must be a deliberate decision — adopted or dropped."""
    proposals = {
        r["proposed_metric"]
        for family in FAMILIES
        for r in _raw(family)
        if not r.get("metric") and r.get("proposed_metric")
    }
    assert len(proposals) == 21
    undecided = sorted(proposals - set(DISPOSITIONS) - set(DROPS))
    assert not undecided, undecided
    n_proposal_only = sum(
        1 for family in FAMILIES for r in _raw(family) if not r.get("metric")
    )
    assert n_proposal_only == 145


def test_an_undecided_proposal_raises(monkeypatch):
    monkeypatch.delitem(DISPOSITIONS, "share_of_spending_to_group")
    with pytest.raises(ValueError, match="a proposal is not a decision"):
        stage()


def test_a_metric_is_adopted_or_dropped_never_both():
    assert not (set(DISPOSITIONS) & set(DROPS))


def test_adopted_proposals_land_on_registered_metrics(staged):
    scores, _ = staged
    used = {s.metric for s in scores}
    assert Metric.SPENDING_SHARE in used
    assert Metric.BENEFIT_UPRATING_RATE in used
    assert Metric.REAL_INCOME_GROWTH in used
    assert Metric.AVERAGE_HOUSEHOLD_INCOME_CHANGE in used
    assert Metric.BENEFIT_COST_CHANGE in used
    assert all(isinstance(m, Metric) for m in used)


def test_change_metrics_are_distinct_from_their_levels():
    """A change is not a level — the rule that already keeps
    revenue_change apart from revenue_level."""
    for level, change in (
        (Metric.BENEFIT_COST, Metric.BENEFIT_COST_CHANGE),
        (Metric.TAXPAYER_COUNT, Metric.TAXPAYER_COUNT_CHANGE),
        (Metric.POVERTY_RATE, Metric.POVERTY_RATE_CHANGE),
    ):
        assert level is not change and level.value != change.value


def test_derived_ratios_are_dropped_not_ingested():
    """cost-per-child-lifted-out-of-poverty is cost divided by a poverty
    change: PE could only 'answer' it by dividing two of its own numbers,
    which makes agreement mechanical rather than evidential."""
    assert "cost_per_child_lifted_out_of_poverty" in DROPS
    assert "ratio" in DROPS["cost_per_child_lifted_out_of_poverty"].lower()
    for key in ("benefit_rate_gap_weekly", "inflation_rate_gap_pp"):
        assert "derived" in DROPS[key].lower()


# --- attribution: whose claim is it? ---------------------------------------


def test_third_party_rows_are_not_staged_as_publisher_claims(staged):
    """8 RF rows carry an `attribution` naming HM Treasury, a Parliament
    impact assessment or a Government estimate. Staging them under
    `resolution_foundation` would attribute a government figure to a
    think tank, and a PE divergence would read as disagreement with a
    model that never produced it."""
    _, acct = staged
    assert acct["drops"]["third_party_attribution"]["rows"] == 8
    attributed = [r for r in _raw("uk_resolution_foundation") if r.get("attribution")]
    assert len(attributed) == 8
    assert any("HM Treasury" in r["attribution"] for r in attributed)
    assert any("Parliament" in r["attribution"] for r in attributed)


def test_attribution_is_checked_before_the_metric_disposition(staged):
    """The ordering is load-bearing: ALL EIGHT attributed rows carry a
    metric this module adopts, so a guard placed after the disposition
    would ingest every one of them."""
    attributed = [r for r in _raw("uk_resolution_foundation") if r.get("attribution")]
    adopted = [
        r
        for r in attributed
        if (r.get("metric") or r.get("proposed_metric")) in DISPOSITIONS
    ]
    assert len(adopted) == 8, "the ordering guard would be untested otherwise"

    # RF contributes 71 read - 13 dropped = 58; the eight are among the
    # dropped, not the ingested.
    _, acct = staged
    assert acct["by_family"]["resolution_foundation"]["ingested"] == 58

    # ...and the guard really does sit first in the loop
    import inspect

    from scorecard_db import ingest_uk_thinktanks as tt

    src = inspect.getsource(tt.stage)
    assert src.index('row.get("attribution")') < src.index("name in DROPS")


# --- identity --------------------------------------------------------------


def test_coverage_restricted_geographies_are_not_the_uk(staged):
    """IFS's Scotland- and NI-excluding analyses are not UK figures;
    aliasing them to UK would file an England-and-Wales number as UK."""
    from scorecard_db.uk_aliases import DISTINCT

    scores, _ = staged
    geos = {s.conditions.get("geography") for s in scores}
    assert "UK_excl_northern_ireland" in geos
    assert "UK_excl_scotland" in geos
    assert ("ifs:UK_excl_northern_ireland", "ifs:UK") in DISTINCT
    # ...and the publication's own wording survives as provenance
    restricted = next(
        s for s in scores if s.conditions.get("geography") == "UK_excl_scotland"
    )
    assert "Excludes Scotland" in restricted.conditions["geography_verbatim"]


def test_publisher_deciles_are_never_unified(staged):
    """The DISTINCT set is an audit ledger, so it is exhaustive over the
    pairs the prose claims rather than carrying examples (review)."""
    from scorecard_db.uk_aliases import DISTINCT

    for i, q in (
        (1, 1),
        (2, 1),
        (3, 2),
        (4, 2),
        (5, 3),
        (6, 3),
        (7, 4),
        (8, 4),
        (9, 5),
        (10, 5),
    ):
        assert (f"ifs:decile_{i}", f"ukmod:q{q}") in DISTINCT
    assert ("resolution_foundation:quintile_1", "ukmod:q1") in DISTINCT
    assert ("resolution_foundation:quintile_5", "ukmod:q5") in DISTINCT
    assert ("resolution_foundation:decile_1", "ifs:decile_1") in DISTINCT
    assert ("resolution_foundation:decile_10", "ifs:decile_10") in DISTINCT


def test_hbai_is_deliberately_absent_from_the_ledger():
    """HBAI registers no decile or quantile vocabulary — its subgroups
    are children/pensioners/working_age/total — so there is nothing on
    that side to be distinct FROM, and asserting a pair against a value
    nobody registered would be the same overclaiming the ledger exists
    to prevent."""
    from scorecard_db.uk_aliases import DISTINCT, known

    # Narrowed (#93): the claim is about RANKING vocabulary, which is
    # what the rationale above actually argues. HBAI registers no
    # quantile or decile values, so no ranking pair can name it. It DOES
    # register unit values, and lpc:jobs vs dwp_hbai:persons is a
    # legitimate never-unify pair on that axis — a job is not a person.
    ranking = ("decile", "quintile", "quantile", "q1", "q2", "q3", "q4", "q5")
    assert not any(
        "hbai" in a + b and any(r in a + b for r in ranking) for a, b in DISTINCT
    )
    assert not known("dwp_hbai", "income_group")
    assert not known("dwp_hbai", "quantile")
    assert known("dwp_hbai", "subgroup") == frozenset(
        {"children", "pensioners", "working_age", "total"}
    )


def test_prose_identities_are_canonicalised(staged):
    scores, _ = staged
    groups = {
        s.conditions["income_group"] for s in scores if "income_group" in s.conditions
    }
    assert "Decile Poorest" not in groups
    assert "decile_1" in groups
    benefits = {s.conditions["benefit"] for s in scores if "benefit" in s.conditions}
    assert benefits <= {
        "universal_credit_standard_allowance",
        "universal_credit_standard_allowance_under_25",
        "universal_credit_health_element",
        "local_housing_allowance",
        "state_pension",
        "inflation_linked_benefits",
    }


def test_an_unregistered_identity_value_raises(staged):
    from scorecard_db.uk_aliases import canon

    with pytest.raises(ValueError, match="unregistered"):
        canon("ifs", "income_group", "the poorest people")


def test_every_row_is_uk_and_held_out(staged):
    scores, _ = staged
    assert all(s.conditions["country"] == "UK" for s in scores)
    assert all(
        s.calibration_relationship is CalibrationRelationship.HELD_OUT for s in scores
    )


def test_the_held_out_evidence_names_where_it_looked():
    from scorecard_db.relationships import uk_relationship

    # poverty_rate is a PERMANENT repo-wide holdout, so it never reaches
    # a per-source branch — use a metric that does.
    for source in ("ifs", "resolution_foundation"):
        _, evidence = uk_relationship(source, Metric.REVENUE_CHANGE)
        assert "2026-08-24" in evidence
        assert "pe-uk-data" in evidence or "policyengine-uk" in evidence
    # and the doctrine still wins where it applies
    rel, basis = uk_relationship("ifs", Metric.POVERTY_RATE)
    assert rel is CalibrationRelationship.HELD_OUT
    assert "PERMANENT holdout" in basis


def test_values_are_never_re_derived(staged):
    """Values arrive in raw units from the harvest. In particular an
    exchequer COST is mapped to revenue_change without re-signing it —
    the published sign convention rides in conditions instead."""
    scores, _ = staged
    raw = {}
    for family, source in FAMILIES.items():
        for r in _raw(family):
            raw.setdefault((source, r.get("source_column")), []).append(r["value"])
    for s in scores:
        vals = raw.get((s.source, s.source_column))
        assert vals is not None and s.value in vals


# --- persistence -----------------------------------------------------------


def test_full_ingest_round_trip(tmp_path):
    db_path = tmp_path / "t.db"
    ScorecardDB(db_path).close()
    summary = ingest(db_path)
    assert summary["claims"] == 314
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    n = conn.execute(
        "SELECT COUNT(*) FROM external_scores WHERE source IN ('ifs','resolution_foundation')"
    ).fetchone()[0]
    assert n == 314
    consumed = conn.execute(
        "SELECT COUNT(*) FROM external_scores"
        " WHERE source IN ('ifs','resolution_foundation')"
        " AND calibration_relationship != 'held_out'"
    ).fetchone()[0]
    assert consumed == 0
    lane = conn.execute(
        "SELECT stage, detail FROM lanes WHERE lane = 'uk-thinktanks'"
    ).fetchone()
    conn.close()
    assert lane["stage"] == "ingested"
    assert "339 staged rows = 314 ingested + 25 tallied drops" in lane["detail"]


def test_ingest_is_idempotent(tmp_path):
    db_path = tmp_path / "t.db"
    ScorecardDB(db_path).close()
    ingest(db_path)
    ingest(db_path)
    conn = sqlite3.connect(db_path)
    n = conn.execute(
        "SELECT COUNT(*) FROM external_scores WHERE source IN ('ifs','resolution_foundation')"
    ).fetchone()[0]
    conn.close()
    assert n == 314


def test_build_db_registers_the_step():
    import inspect

    from scorecard_db import build_db

    assert "ingest_uk_thinktanks.ingest" in inspect.getsource(build_db)


def test_the_lane_reaches_mission_control():
    lanes = json.loads((ROOT / "data" / "lanes.json").read_text())["lanes"]
    entry = next(lane for lane in lanes if lane["id"] == "uk-thinktanks")
    assert entry["country"] == "UK"


def test_accounting_drift_raises():
    bad = {"read": 339, "ingested": 313, "dropped": 26, "drops": _EXPECTED["drops"]}
    with pytest.raises(ValueError, match="accounting drifted"):
        check_accounting(
            {**bad, "drops": {k: {"rows": v} for k, v in bad["drops"].items()}}
        )
