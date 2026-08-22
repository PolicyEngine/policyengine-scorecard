"""The populations export: Urban exclusion, per-release ordering, ratio
guards, lane sync, and an integration pass over the committed DB."""

import json

import pytest

from scorecard_db import ScorecardDB
from scorecard_db.export_populations import REPO, export, release_label
from dataclasses import replace

from scorecard_db.models import (
    BASELINE,
    ReformRef,
    ComparisonStatus,
    ExternalScore,
    Metric,
    PEResult,
    TimeBasis,
    UnitConcept,
)

COMMITTED_DB = REPO / "data" / "scorecard.db"


def _claim(source, column, value, **kw):
    return ExternalScore(
        source=source,
        metric=kw.get("metric", Metric.REVENUE_CHANGE),
        unit_concept=UnitConcept.USD,
        period=2026,
        time_basis=TimeBasis.FISCAL_YEAR,
        value=value,
        conditions=kw.get("conditions", {"geography": "US"}),
        reform=BASELINE,
        calibration_relationship=kw.get("relationship", "held_out"),
        source_column=column,
        publication={"name": kw.get("name", column), "window": "FY2026"},
        value_kind="usd",
    )


def _result(
    cid,
    value,
    bundle,
    at,
    status=ComparisonStatus.CONSTRUCTED,
    annotations=(),
):
    return PEResult(
        claim_id=cid,
        computed_value=value,
        status=status,
        engine_version="1.764.6",
        data_bundle=bundle,
        pe_construction="reform_delta:test",
        run_id="test-run",
        computed_at=at,
        annotations=list(annotations),
    )


@pytest.fixture()
def small_db(tmp_path):
    db = ScorecardDB(tmp_path / "s.db")
    multi = _claim("jct", "multi", 2000.0)
    zero = _claim("cbo", "zero_external", 0.0)
    urban = _claim("urban_sotsn", "urban_row", 5.0)
    uncomputed = _claim("obr", "no_results", 7.0)
    db.upsert_scores([multi, zero, urban, uncomputed])
    db.add_results(
        [
            _result(
                multi.claim_id(),
                1500.0,
                "populace-us-2024-buildo-x",
                "2026-07-22",
                annotations=["named axis: FY-vs-CY"],
            ),
            _result(
                multi.claim_id(),
                1000.0,
                "populace-us-2024-sparse-l0-refit-x",
                "2026-07-01",
            ),
            _result(zero.claim_id(), 10.0, "populace-us-2024-buildo-x", "2026-07-22"),
            _result(urban.claim_id(), 5.0, "populace-us-2024-buildo-x", "2026-07-22"),
        ]
    )
    db.diagnose(multi.claim_id(), "vintage", "test rationale", "issue-link")
    db.close()
    return tmp_path / "s.db", multi.claim_id()


def test_export_shape_and_guards(tmp_path, small_db):
    db_path, multi_id = small_db
    out = tmp_path / "populations.json"
    stats = export(db_path, out_path=out, built="2026-08-05")
    assert stats["rows"] == 2  # urban excluded, uncomputed excluded
    payload = json.loads(out.read_text())
    assert payload["built"] == "2026-08-05"
    by_col = {r["source_column"]: r for r in payload["rows"]}
    assert set(by_col) == {"multi", "zero_external"}

    m = by_col["multi"]
    # Results ordered by computed_at; latest is the newest.
    assert [r["computed_at"] for r in m["results"]] == [
        "2026-07-01",
        "2026-07-22",
    ]
    assert m["latest"]["value"] == 1500.0
    assert m["latest"]["ratio"] == pytest.approx(0.75)
    assert m["latest"]["delta"] == pytest.approx(-500.0)
    # Result annotations survive the export (the campaign's named axes).
    assert m["latest"]["annotations"] == ["named axis: FY-vs-CY"]
    assert m["results"][0]["annotations"] == []
    assert m["diagnosis"] == {
        "class": "vintage",
        "rationale": "test rationale",
        "action_link": "issue-link",
    }
    assert payload["summary"]["multi_release_claims"] == 1
    assert [r["release"] for r in m["results"]] == ["l0-refit", "buildo"]

    # Zero external value -> ratio is None, delta still computed.
    z = by_col["zero_external"]
    assert z["latest"]["ratio"] is None
    assert z["latest"]["delta"] == pytest.approx(10.0)
    assert z["diagnosis"] is None


def test_lane_sync_merges_without_touching_other_lanes(tmp_path, small_db):
    db_path, _ = small_db
    db = ScorecardDB(db_path)
    db.set_lane("populace-reform-validation", "ingested", "205 claims", "2026-08-04")
    # The UK lane is written by build_db's uk_reform_validation step —
    # as ingested rows, or as an explicit awaiting-artifact row.
    db.set_lane(
        "populace-uk-reform-validation",
        "registered",
        "0 claims — awaiting issue #79's artifact",
        "2026-08-17",
    )
    db.close()
    feed = tmp_path / "lanes.json"
    feed.write_text(
        json.dumps(
            {
                "updated": "old",
                "lanes": [
                    {
                        "id": "other-lane",
                        "source": "X",
                        "area": "y",
                        "mode": 1,
                        "stage": "computed",
                        "running": False,
                        "updated": "old",
                        "note": "untouched",
                    },
                ],
            }
        )
    )
    stats = export(
        db_path, out_path=tmp_path / "p.json", lanes_path=feed, built="2026-08-05"
    )
    assert stats["lanes_synced"] == 2
    out = json.loads(feed.read_text())
    lanes = {lane["id"]: lane for lane in out["lanes"]}
    assert lanes["other-lane"]["note"] == "untouched"
    rv = lanes["populace-reform-validation"]
    assert rv["stage"] == "ingested"
    assert rv["source"] == "Populace releases"
    assert out["updated"] == "2026-08-05"
    # The UK lane reaches mission control too, filed under UK — the feed
    # used to list only the US lane, so both the tracked-feed count and
    # the UK page silently lost it.
    uk = lanes["populace-uk-reform-validation"]
    assert uk["country"] == "UK"
    assert uk["stage"] == "registered"

    # An independently pinned older lane sync cannot make the feed look older.
    export(
        db_path,
        out_path=tmp_path / "p-older.json",
        lanes_path=feed,
        built="2026-08-04",
    )
    assert json.loads(feed.read_text())["updated"] == "2026-08-05"


def test_release_label():
    assert release_label("populace-us-2024-buildo-sparse-x") == "buildo"
    assert release_label("populace-us-2024-sparse-l0-refit-57k-x") == "l0-refit"
    assert release_label("populace-us-2024-f0af251-703bd81a565c-x") == "f0af251"


@pytest.mark.skipif(not COMMITTED_DB.exists(), reason="no committed DB")
def test_integration_committed_db(tmp_path):
    stats = export(COMMITTED_DB, out_path=tmp_path / "p.json", built="2026-08-05")
    payload = json.loads((tmp_path / "p.json").read_text())
    db = ScorecardDB(COMMITTED_DB)
    expected = db.conn.execute(
        """SELECT COUNT(DISTINCT s.claim_id) FROM external_scores s
           JOIN pe_results r ON r.claim_id = s.claim_id
           WHERE s.source != 'urban_sotsn'"""
    ).fetchone()[0]
    db.close()
    assert stats["rows"] == expected == len(payload["rows"])
    # Every row carries an explicit country (#42/#50 gate: 14 UK reckoner
    # rows shipped into a feed the exporter never country-tagged, so the
    # app's missing-key US default classified them all as US).
    dist: dict = {}
    for r in payload["rows"]:
        dist[r["country"]] = dist.get(r["country"], 0) + 1
    assert dist == {"US": 270, "UK": 14, "BE": 2}
    # The committed deployment artifact must match a fresh export (modulo
    # the build date) — stale committed data can't pass CI.
    committed = json.loads((REPO / "data" / "populations.json").read_text())
    assert committed["rows"] == payload["rows"]
    assert committed["summary"] == payload["summary"]
    # The reform-validation registry is in there with its release history.
    rv_multi = [r for r in payload["rows"] if len(r["results"]) > 1]
    assert payload["summary"]["multi_release_claims"] == len(rv_multi) > 0
    # Every row has at least one result and carries its relationship.
    assert all(r["results"] for r in payload["rows"])
    assert all(
        r["calibration_relationship"]
        in ("consumed_as_target", "seed_source", "held_out")
        for r in payload["rows"]
    )


def test_export_carries_effective_status_downgrades(tmp_path):
    # The #13 guard end-to-end: a comparable result against a claim in a
    # different world exports status_effective='constructed'; a legacy
    # NULL result against a non-current-law world exports
    # 'baseline_unvalidated'. Raw status is preserved alongside.
    from scorecard_db.models import baseline_key as bk

    db = ScorecardDB(tmp_path / "s.db")
    world_ref = ReformRef(
        framework="policy_ref",
        reform={"policy": "opt"},
        baseline={"policy": "tcja_extension"},
    )
    world = _claim("jct", "world_claim", 100.0)
    world = ExternalScore(
        source="jct",
        metric=Metric.REVENUE_CHANGE,
        unit_concept=UnitConcept.USD,
        period=2026,
        time_basis=TimeBasis.FISCAL_YEAR,
        value=100.0,
        conditions={"geography": "US"},
        reform=world_ref,
        calibration_relationship="held_out",
        source_column="world_claim",
        publication={"name": "w", "window": "FY2026"},
        value_kind="usd",
    )
    db.upsert_scores([world])
    cross = _result(
        world.claim_id(),
        90.0,
        "populace-us-2024-buildo-x",
        "2026-07-22",
        status=ComparisonStatus.COMPARABLE,
    )
    cross = replace(cross, baseline_key=bk({"policy": "current_policy"}))
    legacy = replace(
        _result(
            world.claim_id(),
            91.0,
            "populace-us-2024-buildp-x",
            "2026-07-28",
            status=ComparisonStatus.COMPARABLE,
        ),
    )
    db.add_results([cross, legacy])
    db.close()

    out = tmp_path / "p.json"
    export(tmp_path / "s.db", out_path=out, built="2026-08-19")
    row = json.loads(out.read_text())["rows"][0]
    statuses = {
        r["data_bundle"]: (r["status"], r["status_effective"]) for r in row["results"]
    }
    assert statuses["populace-us-2024-buildo-x"] == ("comparable", "constructed")
    assert statuses["populace-us-2024-buildp-x"] == (
        "comparable",
        "baseline_unvalidated",
    )
    assert row["latest"]["status_effective"] == "baseline_unvalidated"
