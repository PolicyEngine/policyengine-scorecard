"""The Autumn Budget 2025 ingest (#136).

Every one of the 8,194 staged rows is a claim or a tallied drop; what is
pinned here is what could go wrong quietly: the per-family accounting, the
disposition of 140 harvest-side proposals, the attribution guard's
position, the three retrieval axes on every claim (producer, measure,
event), the registry verdict on every keyed row, and the visibility flag
that puts national-grain rows on the page before a counterpart exists.
"""

import gzip
import json
import sqlite3
from pathlib import Path

import pytest

from scorecard_db import ScorecardDB
from scorecard_db.ingest_uk_ab2025 import (
    DISPOSITIONS,
    DROPS,
    FAMILIES,
    HARVEST,
    LANES,
    REGISTRY,
    REGISTRY_MARK,
    _DROP_BY_NAME,
    check_accounting,
    expected,
    ingest,
    stage,
)
from scorecard_db.models import CalibrationRelationship, Metric

ROOT = Path(__file__).resolve().parent.parent
COUNTS = json.loads((HARVEST / "COUNTS.json").read_text())


@pytest.fixture(scope="module")
def staged():
    return stage()


def _raw(family):
    p = HARVEST / family / "claims_staged.jsonl.gz"
    return [json.loads(line) for line in gzip.open(p, "rt")]


# --- the accounting --------------------------------------------------------


def test_every_staged_row_is_ingested_or_tallied(staged):
    scores, acct = staged
    exp = expected()
    assert acct["read"] == exp["read"] == COUNTS["_totals"]["rows"]
    assert acct["ingested"] == len(scores) == exp["ingested"]
    assert acct["ingested"] + acct["dropped"] == acct["read"]
    for fam, v in acct["by_family"].items():
        assert v["read"] == COUNTS[fam]["rows"], fam
        assert v["ingested"] + v["dropped"] == v["read"], fam
    check_accounting(acct)


def test_every_drop_states_a_reason(staged):
    _, acct = staged
    for key, entry in acct["drops"].items():
        assert entry["rows"] > 0, key
        assert len(entry["reason"]) > 80, key
    assert set(_DROP_BY_NAME.values()) <= set(DROPS)
    assert not (set(DISPOSITIONS) & set(_DROP_BY_NAME))


def test_restated_rows_are_tallied_not_carried(staged):
    """342 re-published official figures (the #86 rule) — the tally equals
    the harvest's own count, so none was quietly carried or lost."""
    _, acct = staged
    assert (
        acct["drops"]["restated_official_figure"]["rows"]
        == COUNTS["_totals"]["restated"]
    )


def test_attribution_is_checked_before_the_metric_disposition():
    import inspect

    from scorecard_db import ingest_uk_ab2025

    src = inspect.getsource(ingest_uk_ab2025.stage)
    assert src.index('row["attribution"] == "restated"') < src.index(
        "name in _DROP_BY_NAME"
    )
    assert src.index('row["attribution"] == "restated"') < src.index(
        "DISPOSITIONS[name]"
    )


def test_worked_examples_are_tallied_for_mode_3(staged):
    """The commercial family stages 121 rows and ingests none: they are
    single-household cases (#63), tallied so the harvest is complete."""
    _, acct = staged
    fam = acct["by_family"]["uk_cases_commercial"]
    assert fam["read"] == 121 and fam["ingested"] == 0
    assert acct["drops"]["mode3_worked_example"]["rows"] == 105
    assert acct["drops"]["mode3_specimen_household"]["rows"] > 0


def test_every_proposal_is_dispositioned():
    names = set()
    for fam in FAMILIES:
        for r in _raw(fam):
            names.add(r.get("metric") or r.get("proposed_metric"))
    undecided = sorted(
        n for n in names if n not in DISPOSITIONS and n not in _DROP_BY_NAME
    )
    # the residue is dropped by unit or by family, never inferred
    for n in undecided:
        rows = [
            r
            for fam in FAMILIES
            for r in _raw(fam)
            if (r.get("metric") or r.get("proposed_metric")) == n
        ]
        assert all(
            r["attribution"] == "restated"
            or r["value_kind"] == "categorical"
            or (r.get("proposed_unit") or "") != ""
            or any(
                k in r["conditions"]
                for k in ("household_type", "household", "employment_income")
            )
            or r["source"] in FAMILIES["uk_cases_commercial"][1]
            for r in rows
        ), n


def test_an_undecided_proposal_raises(monkeypatch):
    monkeypatch.delitem(DISPOSITIONS, "affected_count")
    with pytest.raises(ValueError, match="no disposition"):
        stage()


# --- what every claim carries ----------------------------------------------


def test_claim_ids_do_not_collide(staged):
    scores, _ = staged
    ids = [s.claim_id() for s in scores]
    assert len(ids) == len(set(ids))


def test_the_three_retrieval_axes_are_on_every_claim(staged):
    scores, _ = staged
    for s in scores:
        assert s.conditions["country"] == "UK"
        assert s.conditions["fiscal_event"] == "autumn_budget_2025"
        assert s.conditions["benchmark_class"] in (
            "different_model",
            "administrative_fact",
            "same_assumptions",
        )
        assert s.publication["registry"] == REGISTRY_MARK
        assert s.publication["family"] in FAMILIES
        assert s.calibration_relationship is CalibrationRelationship.HELD_OUT


def test_keyed_rows_carry_the_registry_verdict(staged):
    scores, _ = staged
    from scorecard_db.ingest_uk_ab2025 import MACRO_LINK, MACRO_METRICS

    keyed = [s for s in scores if "measure_key" in s.conditions]
    assert len(keyed) > 5000
    for s in keyed:
        m = REGISTRY[s.conditions["measure_key"]]
        if s.metric in MACRO_METRICS:
            # a macro-fiscal call carries the #55 lane's verdict whatever
            # measure it is keyed to (the household model has no lever)
            assert s.conditions["pe_expressibility"] == "not_expressible"
            assert s.conditions["action_link"] == MACRO_LINK
            continue
        assert s.conditions["pe_expressibility"] == m["computability"]
        if m["computability"] == "not_expressible":
            assert s.conditions["action_link"].startswith("https://")
            assert s.conditions["pe_missing"]
        # the measure is the reform world's slug, so producers share keys
        assert s.reform.reform["policy"] == s.conditions["measure_key"]


def test_producers_share_a_reform_key_per_measure(staged):
    """Retrieval by measure: the two-child measure is scored by HM Treasury,
    the OBR, the IFS, RF, JRF, IPPR and CPAG; every row shares one key."""
    scores, _ = staged
    key = "ab2025__uc_child_element_remove_two_child_limit"
    rows = [s for s in scores if s.conditions.get("measure_key") == key]
    assert len({s.source for s in rows}) >= 5
    # one reform key per baseline world, never per producer
    assert len({s.reform.key() for s in rows}) == len(
        {s.reform.baseline_key() for s in rows}
    )


def test_same_assumptions_rows_are_the_fabians_policyengine_rows(staged):
    scores, _ = staged
    same = [s for s in scores if s.conditions["benchmark_class"] == "same_assumptions"]
    assert len(same) == 4
    assert {s.source for s in same} == {"fabian_society"}
    assert all(s.source_model == "policyengine_uk" for s in same)


def test_values_are_verbatim_never_re_signed(staged):
    scores, _ = staged
    for s in scores:
        assert "value_verbatim" in s.conditions
    # HMT prints costs negative; the row keeps the sign and the convention
    two_child = [
        s
        for s in scores
        if s.source == "hm_treasury"
        and s.conditions.get("measure_key")
        == "ab2025__uc_child_element_remove_two_child_limit"
        and s.metric is Metric.REVENUE_CHANGE
        and s.conditions.get("fy") == "2026-27"
    ]
    assert two_child and all(s.value < 0 for s in two_child)
    assert all("sign_convention" in s.conditions for s in two_child)


def test_distinct_distributions_stay_distinct(staged):
    scores, _ = staged
    rf = {
        s.conditions.get("income_group")
        for s in scores
        if s.source == "resolution_foundation"
    }
    ifs = {s.conditions.get("income_group") for s in scores if s.source == "ifs"}
    assert "vigintile_1" in rf and "vigintile_1" not in ifs
    assert "earnings_decile_10" in ifs
    # WPI's severe-hardship counts share the poverty_count_change metric
    # with its HBAI-poverty rows; the measure condition keeps them apart
    wpi = [
        s
        for s in scores
        if s.source == "trussell_wpi" and s.metric is Metric.POVERTY_COUNT_CHANGE
    ]
    hardship = [s for s in wpi if s.conditions.get("poverty_measure")]
    assert hardship and len(hardship) < len(wpi)
    assert all(
        s.conditions["poverty_measure"] == "wpi_severe_hardship" for s in hardship
    )


def test_baselines_are_registered_worlds(staged):
    """Every non-current-law world a row is scored against is a registered
    descriptor (#13): the OBR's rows carry the (round, counterfactual-kind)
    descriptor whose label is obr_pre_measures_autumn_budget_2025__policy_parameters."""
    from scorecard_db.baselines import BASELINES
    from scorecard_db.models import baseline_key

    keys = {baseline_key(b[0]) for b in BASELINES}
    scores, _ = staged
    worlds = set()
    for s in scores:
        if s.reform.baseline is not None:
            assert s.reform.baseline_key() in keys, s.reform.baseline
            assert s.conditions["baseline_policy"] == s.reform.baseline["policy"]
            worlds.add(s.reform.baseline_key())
    assert len(worlds) >= 15


def test_national_rows_reach_the_page_and_constituency_rows_wait(staged):
    scores, _ = staged
    feed = [s for s in scores if s.publication["publish_without_result"]]
    held = [s for s in scores if not s.publication["publish_without_result"]]
    assert len(feed) + len(held) == len(scores)
    assert all(s.source == "tax_policy_associates" for s in held)
    assert len(held) == 2991


def test_unregistered_identity_raises(staged):
    from scorecard_db.uk_aliases import canon

    with pytest.raises(ValueError, match="unregistered"):
        canon("jrf", "income_group", "decile_1")


# --- the round trip --------------------------------------------------------


def test_round_trip_and_lanes(tmp_path):
    db_path = tmp_path / "t.db"
    ScorecardDB(db_path).close()
    summary = ingest(db_path, tmp_path / "lanes.json")  # never the committed feed
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    n = conn.execute(
        "SELECT COUNT(*) FROM external_scores"
        " WHERE json_extract(publication, '$.registry') = ?",
        (REGISTRY_MARK,),
    ).fetchone()[0]
    assert n == summary["claims"] == expected()["ingested"]
    lanes = {
        r["lane"]: r
        for r in conn.execute("SELECT * FROM lanes WHERE lane LIKE 'uk-ab2025-%'")
    }
    assert set(lanes) == set(LANES)
    assert lanes["uk-ab2025-cases"]["stage"] == "cataloged"
    assert (
        "121 staged rows = 0 ingested + 121 tallied drops"
        in lanes["uk-ab2025-cases"]["detail"]
    )
    assert lanes["uk-ab2025-microsim"]["stage"] == "ingested"
    conn.close()


def test_ingest_is_idempotent_and_touches_only_its_own_rows(tmp_path):
    db_path = tmp_path / "t.db"
    ScorecardDB(db_path).close()
    ingest(db_path, tmp_path / "lanes.json")
    ingest(db_path, tmp_path / "lanes.json")
    conn = sqlite3.connect(db_path)
    n = conn.execute(
        "SELECT COUNT(*) FROM external_scores"
        " WHERE json_extract(publication, '$.registry') = ?",
        (REGISTRY_MARK,),
    ).fetchone()[0]
    assert n == expected()["ingested"]
    conn.close()


def test_build_db_registers_both_steps():
    import inspect

    from scorecard_db import build_db

    src = inspect.getsource(build_db)
    assert "ingest_uk_ab2025.ingest(db_path)" in src
    assert "ingest_uk_ab2025.ingest_verdicts(db_path)" in src


def test_the_lanes_reach_mission_control():
    lanes = json.loads((ROOT / "data" / "lanes.json").read_text())["lanes"]
    ids = {lane["id"]: lane for lane in lanes}
    for lane in LANES:
        assert ids[lane]["country"] == "UK", lane


def test_accounting_drift_raises(staged):
    _, acct = staged
    bad = json.loads(json.dumps(acct))
    bad["ingested"] -= 1
    bad["dropped"] += 1
    with pytest.raises(ValueError, match="accounting drifted"):
        check_accounting(bad)


# --- one engine at several releases ---------------------------------------


def test_versioned_engine_spellings_are_recorded_releases(staged):
    """The release rides on the claim (ukmod_b1.13) and the ledger says
    which publisher ran which; the two must agree."""
    from scorecard_db.engines import known_release, split_release

    scores, _ = staged
    versioned = {
        (s.source, s.source_model)
        for s in scores
        if split_release(s.source_model)[1] is not None
    }
    assert versioned == {
        ("cpag", "ukmod_b1.11"),
        ("cpag", "ukmod_b1.13"),
        ("wbg", "ukmod_b2025.08"),
        ("ukmod", "ukmod_b2025.09"),
    }
    for source, model in versioned:
        assert known_release(source, model), (source, model)


def test_a_release_the_ledger_lacks_raises():
    from scorecard_db.ingest_uk_ab2025 import _source_model

    assert _source_model("cpag", {"source_model": "ukmod_b1.13"}) == "ukmod_b1.13"
    assert _source_model("cpag", {"source_model": None}) == "ukmod"
    assert _source_model("fraser_of_allander", {"source_model": "ukmod"}) == "ukmod"
    with pytest.raises(ValueError, match="does not record"):
        _source_model("cpag", {"source_model": "ukmod_b9.99"})
    with pytest.raises(ValueError, match="different engine"):
        _source_model("cpag", {"source_model": "ifs_taxben"})
    with pytest.raises(ValueError, match="no source_model"):
        _source_model("fraser_of_allander", {"source_model": ""})
