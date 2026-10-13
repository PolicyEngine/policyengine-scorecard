"""The OBR costings lane's external side and its attach (#54, #56).

Gate round 1 on #56 named the failure modes; each is pinned here: the
slice is re-derivable from the vendored harvest with an exact tally; the
ingest is in the build chain with exact accounting; every condition key
is closed and claims key the FY END year; the relationship is derived;
every claim names the announcement-time world OBR scored it against and
every attached result names the world PE executed, both registered.
"""

import json
import sqlite3
from pathlib import Path

import pytest

from scorecard_db import (
    ingest_campaign,
    ingest_obr_costings as mod,
    produce_obr_costings,
)
from scorecard_db import ScorecardDB
from scorecard_db.baselines import BASELINES
from scorecard_db.models import STANDARD_CONDITIONS, baseline_key

ROOT = Path(__file__).resolve().parent.parent
REGISTERED = {baseline_key(d) for d, *_ in BASELINES}


@pytest.fixture(scope="module")
def staged():
    return mod.stage()


# --- the slice is derived, not hand-cut -------------------------------------


def test_the_slice_and_index_reproduce_from_the_vendored_harvest():
    pytest.importorskip("yaml")
    from pipeline import select_obr_costings_claims as sel

    reg = sel.load_registry()
    rows, tally = sel.select(reg)
    assert tally["read"] == 25558
    assert tally["selected"] == 621 == len(rows)
    assert tally["not_selected"] == {
        "other_source": 0,
        "description_not_in_registry": 24937,
        "other_fiscal_event": 0,
        "other_table": 0,
    }
    assert sel.render(rows) == sel.SLICE.read_text()
    assert sel.render_index(sel.measure_index(reg)) == sel.INDEX.read_text()


# --- accounting and identity --------------------------------------------------


def test_exact_accounting(staged):
    scores, acct = staged
    assert acct == mod.EXPECTED
    assert len(scores) == 621
    assert len({s.claim_id() for s in scores}) == 621


def test_every_condition_key_is_closed_and_periods_are_fy_end(staged):
    scores, _ = staged
    events = set(mod.EVENTS.values()) | {mod.EFO_EVENT}
    for s in scores:
        assert set(s.conditions) <= STANDARD_CONDITIONS | {
            "country",
            "value_verbatim",
            "benchmark_class",
        }, sorted(set(s.conditions) - STANDARD_CONDITIONS)
        assert s.conditions["country"] == "UK"
        assert s.conditions["fiscal_event"] in events
        assert s.period == int(s.conditions["fy"][:4]) + 1
        assert s.conditions["benchmark_class"] == "different_model"
        assert s.conditions["obr_measure_key"] in mod.measures()
        assert s.conditions["pe_expressibility"] in (
            "expressible",
            "partial",
            "not_expressible",
        )
        if s.conditions["pe_expressibility"] == "not_expressible":
            assert s.conditions["action_link"].startswith("https://github.com/")
        assert s.reform.reform["policy"] == s.conditions["measure_key"]
        assert s.reform.baseline is not None
        assert s.reform.baseline_key() in REGISTERED
        assert s.conditions["baseline_policy"] == s.reform.baseline["policy"]


def test_spending_rows_name_the_fiscal_measure(staged):
    scores, _ = staged
    spend = [s for s in scores if "spending_head" in s.conditions]
    assert len(spend) == 228
    assert all(s.conditions["fiscal_measure"] == "exchequer_impact" for s in spend)
    assert all(s.metric.value == "revenue_change" for s in scores)


def test_autumn_budget_2025_rows_join_the_port_registry(staged):
    """Retrieval by measure across producers: the OBR leg of the
    two-child measure carries the #136 key HM Treasury, the IFS and RF
    carry, not a private one."""
    scores, _ = staged
    ab = [s for s in scores if s.conditions["fiscal_event"] == "autumn_budget_2025"]
    assert ab and all(s.conditions["measure_key"].startswith("ab2025__") for s in ab)
    keys = {s.conditions["measure_key"] for s in ab}
    assert "ab2025__uc_child_element_remove_two_child_limit" in keys
    two = [s for s in ab if s.conditions["measure_key"].endswith("two_child_limit")]
    assert all(s.conditions["pe_expressibility"] == "expressible" for s in two)
    # earlier events keep the YAML registry's own key
    others = [s for s in scores if s.conditions["fiscal_event"] != "autumn_budget_2025"]
    assert all(
        s.conditions["measure_key"] == s.conditions["obr_measure_key"] for s in others
    )


def test_announcement_time_baselines_per_event(staged):
    scores, _ = staged
    for s in scores:
        ev = s.conditions["fiscal_event"]
        if ev == mod.EFO_EVENT:
            assert s.reform.baseline == mod.EFO_BASELINE
            assert s.source == "obr_efo"
        else:
            assert s.reform.baseline == mod.EVENT_BASELINE[ev]
            assert s.source == "obr_pmd"
    worlds = {s.reform.baseline_key() for s in scores}
    assert len(worlds) == 5


def test_relationship_is_derived_not_copied():
    from scorecard_db.models import CalibrationRelationship
    from scorecard_db.relationships import uk_relationship

    rel, basis = uk_relationship("obr_pmd", None, kind="forecast")
    assert rel is CalibrationRelationship.HELD_OUT
    assert "Policy Measures Database" in basis


# --- executed worlds (the result side of finding 1) --------------------------


def test_executed_world_per_construction():
    cur = mod._CURRENT_LAW_KEY
    labels = {b[1]: baseline_key(b[0]) for b in BASELINES}
    assert (
        mod.executed_world_key("efo_march_2026__pa_and_hrt_freezes")
        == labels["obr_announcement_baseline_efo_march_2026"]
    )
    assert (
        mod.executed_world_key(
            "autumn_budget_2025__uc_child_element_remove_two_child_limit"
        )
        == labels["pre_ab2025"]
    )
    assert (
        mod.executed_world_key("autumn_budget_2025__dividend_income_rate_increase")
        == labels["pre_ab2025__dividend_rates_plus_2pp"]
    )
    assert (
        mod.executed_world_key("spring_budget_2024__hicbc_threshold_and_taper")
        == labels["pre_spring_budget_2024__hicbc_threshold_and_taper"]
    )
    # a forward delta and a measure with no reform execute current law
    assert (
        mod.executed_world_key("autumn_budget_2024__hmrc_5000_compliance_staff") == cur
    )
    assert (
        mod.executed_world_key("autumn_budget_2025__uc_standard_and_health_protections")
        == cur
    )


def test_every_measure_has_an_executed_world():
    for key in mod.measures():
        assert mod.executed_world_key(key) in REGISTERED | {mod._CURRENT_LAW_KEY}


# --- the round trip ---------------------------------------------------------


def _fresh(tmp_path):
    db_path = tmp_path / "t.db"
    ScorecardDB(db_path).close()
    mod.ingest(db_path)
    return db_path


def test_round_trip_lane_and_idempotence(tmp_path):
    db_path = _fresh(tmp_path)
    mod.ingest(db_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    n = conn.execute(
        "SELECT COUNT(*) FROM external_scores"
        " WHERE json_extract(publication, '$.registry') = ?",
        (mod.REGISTRY_MARK,),
    ).fetchone()[0]
    assert n == 621
    by_src = dict(
        conn.execute(
            "SELECT source, COUNT(*) FROM external_scores"
            " WHERE json_extract(publication, '$.registry') = ? GROUP BY 1",
            (mod.REGISTRY_MARK,),
        ).fetchall()
    )
    assert by_src == {"obr_pmd": 552, "obr_efo": 69}
    lane = conn.execute("SELECT * FROM lanes WHERE lane = ?", (mod.LANE_ID,)).fetchone()
    assert (
        lane["stage"] == "ingested"
        and "621 slice rows = 621 ingested" in lane["detail"]
    )
    # the claims' worlds are registered rows
    missing = conn.execute(
        "SELECT COUNT(*) FROM external_scores s LEFT JOIN baselines b USING (baseline_key)"
        " WHERE json_extract(s.publication, '$.registry') = ? AND b.baseline_key IS NULL",
        (mod.REGISTRY_MARK,),
    ).fetchone()[0]
    assert missing == 0
    conn.close()


def test_resolved_staging_attaches_with_executed_worlds(tmp_path):
    """The compute staging resolves to claim ids and executed worlds and
    attaches like any campaign; every result names a registered world
    and the #13 guard sees it."""
    db_path = _fresh(tmp_path)
    out = tmp_path / "resolved"
    summary = produce_obr_costings.produce(db_path, out)
    rows = [
        json.loads(l) for l in (out / "obr_costings.jsonl").read_text().splitlines()
    ]
    assert summary["resolved"] == len(rows) > 0
    assert all(set(r["external_claim_match"]) == {"claim_id"} for r in rows)
    assert all(r["baseline_key"] in REGISTERED for r in rows)
    attached = ingest_campaign.ingest(db_path, out)
    assert attached["attached"] == len(rows)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    res = conn.execute(
        "SELECT r.baseline_key, r.status, s.baseline_key AS claim_world, c.pe_status_effective"
        " FROM pe_results r JOIN external_scores s USING (claim_id)"
        " JOIN comparisons c USING (claim_id)"
    ).fetchall()
    assert len(res) == len(rows)
    assert all(r["baseline_key"] is not None for r in res)
    # OBR scored against its pre-measures forecast; PE executed the
    # reversed certified world: different registered worlds, so nothing
    # here may read as plain agreement
    assert all(r["pe_status_effective"] != "comparable" for r in res)
    conn.close()


def test_campaign_ingest_refuses_an_unregistered_executed_world(tmp_path):
    db_path = _fresh(tmp_path)
    out = tmp_path / "resolved"
    produce_obr_costings.produce(db_path, out)
    path = out / "obr_costings.jsonl"
    rows = [json.loads(l) for l in path.read_text().splitlines()]
    rows[0]["baseline_key"] = "not-a-registered-world"
    path.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    with pytest.raises(ValueError, match="not registered worlds"):
        ingest_campaign.ingest(db_path, out)
    conn = sqlite3.connect(db_path)
    assert conn.execute("SELECT COUNT(*) FROM pe_results").fetchone()[0] == 0
    conn.close()


def test_an_unregistered_event_or_drifted_period_raises():
    index = mod.measures()
    join = mod._ab2025_join()
    row = mod.load_rows()[0]
    bad = json.loads(json.dumps(row))
    bad["conditions"]["fiscal_event"] = "Budget 2099"
    # the measure lookup is the first gate: a row whose event matches no
    # registry measure is drift between the slice and the registry
    with pytest.raises(ValueError, match="no registry measure"):
        mod._score(bad, index, join)
    bad = json.loads(json.dumps(row))
    bad["period"] = bad["period"] + 1
    with pytest.raises(ValueError, match="does not open fy"):
        mod._score(bad, index, join)


def test_build_db_registers_the_three_steps():
    import inspect

    from scorecard_db import build_db

    src = inspect.getsource(build_db)
    assert "ingest_obr_costings.ingest(db_path)" in src
    assert "produce_obr_costings.produce(db_path)" in src
    assert "ingest_campaign.ingest(db_path, produce_obr_costings.RESOLVED)" in src
