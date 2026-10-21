"""The populations export: Urban exclusion, uncomputed-claim retention,
per-release ordering, ratio guards, lane sync, and committed-DB integration."""

import json
from dataclasses import replace

import pytest
from hypothesis import given, strategies as st

from scorecard_db import ScorecardDB
from scorecard_db.export_populations import (
    PMD_REGISTRY,
    REPO,
    _compact_rows,
    export,
    release_label,
)

from scorecard_db.models import (
    BASELINE,
    ComparisonStatus,
    ExternalScore,
    Metric,
    PEResult,
    ReformRef,
    TimeBasis,
    UnitConcept,
)

COMMITTED_DB = REPO / "data" / "scorecard.db"


def _expand_archive(payload):
    return [
        {
            **payload["common"],
            **row,
            "conditions": {**payload["common_conditions"], **row["conditions"]},
        }
        for row in payload["rows"]
    ]


def _all_rows(payload, directory):
    rows = list(payload["rows"])
    for archive in payload.get("event_archives", []):
        rows.extend(
            _expand_archive(
                json.loads(
                    (directory / archive["path"].removeprefix("data/")).read_text()
                )
            )
        )
    return rows


@given(
    st.lists(
        st.fixed_dictionaries(
            {
                "claim_id": st.text(),
                "external_value": st.one_of(st.none(), st.integers()),
                "conditions": st.dictionaries(
                    st.text(), st.one_of(st.text(), st.none()), max_size=5
                ),
            }
        ),
        min_size=1,
        max_size=12,
    )
)
def test_archive_factoring_preserves_every_value(rows):
    assert _expand_archive(_compact_rows(rows)) == rows


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
        publication={
            "name": kw.get("name", column),
            "window": "FY2026",
            **(
                {"publish_without_result": True}
                if kw.get("publish_without_result")
                else {}
            ),
        },
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
    uncomputed = _claim("obr", "no_results", 7.0, publish_without_result=True)
    hidden_uncomputed = _claim("tax_foundation", "hidden_no_results", 8.0)
    db.upsert_scores([multi, zero, urban, uncomputed, hidden_uncomputed])
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
    assert stats["rows"] == 3  # urban + unopted uncomputed claims excluded
    payload = json.loads(out.read_text())
    assert payload["built"] == "2026-08-05"
    by_col = {r["source_column"]: r for r in payload["rows"]}
    assert set(by_col) == {"multi", "zero_external", "no_results"}

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

    # Claims awaiting their first model run remain visible without inventing
    # a result-history entry.
    u = by_col["no_results"]
    assert u["results"] == []
    assert u["latest"] == {
        "value": None,
        "status": "not_computed",
        "engine_version": "",
        "data_bundle": "",
        "release": "",
        "construction": "",
        "policyengine_variables": [],
        "computed_at": "",
        "annotations": [],
        "baseline": None,
        "status_effective": "not_computed",
        "ratio": None,
        "delta": None,
    }
    assert payload["summary"]["by_latest_status"]["not_computed"] == 1


def test_pmd_events_are_reachable_without_inflating_initial_feed(tmp_path, small_db):
    db_path, _ = small_db
    db = ScorecardDB(db_path)
    claims = [
        _claim(
            "obr_pmd",
            f"historical_{index}",
            value,
            publish_without_result=True,
            conditions={
                "country": "UK",
                "fiscal_event": event,
                "measure_key": f"historical_measure_{index}",
                "measure": f"Historical measure {index}",
            },
        )
        for index, (event, value) in enumerate(
            [("budget_1970", 0), ("budget_1970", 12), ("spring_budget_2024", -4)]
        )
    ]
    claims = [
        replace(
            claim,
            publication={
                **{
                    key: value
                    for key, value in claim.publication.items()
                    if key != "name"
                },
                "registry": PMD_REGISTRY,
                "title": "Policy measures database (November 2025)",
                "fiscal_event_name": (
                    "Budget 1970"
                    if claim.conditions["fiscal_event"] == "budget_1970"
                    else "Spring Budget 2024"
                ),
            },
        )
        for claim in claims
    ]
    db.upsert_scores(claims)
    # A recorded gap history is visible but supplies no numerical counterpart.
    db.add_results(
        [
            _result(
                claims[2].claim_id(), None, "gap", "2026-10-11", ComparisonStatus.PE_GAP
            )
        ]
    )
    db.close()
    out = tmp_path / "populations.json"
    export(db_path, out_path=out, built="2026-10-11")
    first = out.read_bytes()
    payload = json.loads(first)
    assert len(payload["rows"]) == 3
    assert payload["summary"]["claims"] == 6
    assert payload["summary"]["by_country"]["UK"] == {
        "claims": 3,
        "with_result": 1,
        "with_value": 0,
        "without_result": 2,
        "multi_release_claims": 0,
    }
    assert {archive["label"] for archive in payload["event_archives"]} == {
        "Budget 1970",
        "Spring Budget 2024",
    }
    rows = _all_rows(payload, tmp_path)
    assert len({row["claim_id"] for row in rows}) == len(rows) == 6
    pmd = [row for row in rows if row["source"] == "obr_pmd"]
    assert sorted(row["name"] for row in pmd) == [
        "Historical measure 0",
        "Historical measure 1",
        "Historical measure 2",
    ]
    assert sorted(row["external_value"] for row in pmd) == [-4, 0, 12]
    assert all(row["latest"]["value"] is None for row in pmd)
    shard_bytes = {
        archive["path"]: (tmp_path / archive["path"].removeprefix("data/")).read_bytes()
        for archive in payload["event_archives"]
    }
    export(db_path, out_path=out, built="2026-10-11")
    assert out.read_bytes() == first
    assert all(
        (tmp_path / path.removeprefix("data/")).read_bytes() == content
        for path, content in shard_bytes.items()
    )


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
    assert release_label("populace-us-2024-spm-20260915") == "spm-20260915"
    assert (
        release_label("microcosm_be_v05h_corrected@f138697423c7") == "microcosm_be_v05h"
    )


@pytest.mark.skipif(not COMMITTED_DB.exists(), reason="no committed DB")
def test_integration_committed_db(tmp_path):
    stats = export(COMMITTED_DB, out_path=tmp_path / "p.json", built="2026-08-05")
    payload = json.loads((tmp_path / "p.json").read_text())
    db = ScorecardDB(COMMITTED_DB)
    expected = db.conn.execute(
        """SELECT COUNT(*) FROM external_scores s
           WHERE source != 'urban_sotsn'
             AND (EXISTS (SELECT 1 FROM pe_results r
                          WHERE r.claim_id = s.claim_id)
                  OR json_extract(s.publication,
                                  '$.publish_without_result') = 1)"""
    ).fetchone()[0]
    db.close()
    all_rows = _all_rows(payload, tmp_path)
    assert stats["rows"] == expected == len(all_rows)
    # Every row carries an explicit country (#42/#50 gate: 14 UK reckoner
    # rows shipped into a feed the exporter never country-tagged, so the
    # app's missing-key US default classified them all as US).
    dist: dict = {}
    for r in all_rows:
        dist[r["country"]] = dist.get(r["country"], 0) + 1
    # UK: 14 reckoner rows + 3,994 national-grain Autumn Budget 2025 claims
    # opted into pre-result display (#136) + 483 UKMOD WP 3/26 rows (uk_ukmod_ab2025)
    # + 12 fiscal-headroom calls and 39 macro-house calls (#55 lane, tranche 4)
    # US: 270 + 6 JCT tax-expenditure rows first scored by the
    # populace-us-2024-spm-20260915 release (SE health insurance, HSA,
    # student-loan interest, SE pension, traditional IRA, CDCC + employer
    # child care) + 104 FY 2022 FNS state SNAP claims (52 rates, 52
    # eligible counts) with federal-rules PE counterparts (#2) + 53 TY2022
    # IRS/Census EITC participation rates (52 ACS, 1 CPS headline) (#2) +
    # 14 ASPE Indicator 4 claims at their latest period (TANF, SNAP, SSI) +
    # 88 Census STC State income tax collections (44 jurisdictions, FY2023
    # and FY2025) with CY2024 counterparts (#176).
    # The March 2026 PMD contributes only its 246 new cells; November's
    # historical/comprehensive claims and the existing main feed stay intact.
    # Pre-publish comparables (docs/COMPARABLES.md) add every staged claim of
    # each analysis record: 20 for the £100,000 childcare dashboard (12 CenTax,
    # 8 Centre for British Progress), with or without a result.
    assert dist == {"US": 535, "UK": 5163 + 23_752 + 246 + 20, "BE": 9, "NZ": 12}
    nz = [row for row in payload["rows"] if row["country"] == "NZ"]
    assert len(nz) == 12
    assert {row["source"] for row in nz} == {"nz_treasury"}
    assert all(row["results"] == [] for row in nz)
    assert all(row["latest"]["status_effective"] == "not_computed" for row in nz)
    be_pit = [
        row
        for row in payload["rows"]
        if row["source"] in {"spf_finances", "cour_des_comptes", "policyengine"}
    ]
    assert len(be_pit) == 7
    assert all(row["country"] == "BE" for row in be_pit)
    assert {
        source: sum(row["source"] == source for row in be_pit)
        for source in ("spf_finances", "cour_des_comptes", "policyengine")
    } == {"spf_finances": 1, "cour_des_comptes": 1, "policyengine": 5}
    assert sorted(
        (row["source"], row["period"], row["external_value"]) for row in be_pit
    ) == [
        ("cour_des_comptes", 2030, -5_000_000_000.0),
        ("policyengine", 2026, -513_450_000.0),
        ("policyengine", 2027, -456_510_000.0),
        ("policyengine", 2028, -779_680_000.0),
        ("policyengine", 2029, -2_457_460_000.0),
        ("policyengine", 2030, -4_155_520_000.0),
        ("spf_finances", 2030, -4_000_000_000.0),
    ]
    # The committed deployment artifact must match a fresh export (modulo
    # the build date) — stale committed data can't pass CI.
    committed = json.loads((REPO / "data" / "populations.json").read_text())
    assert committed["rows"] == payload["rows"]
    assert committed["summary"] == payload["summary"]
    assert committed["event_archives"] == payload["event_archives"]
    # Every event is reachable in the deployed copy, with bounded requests.
    # 5,719 + the 20 pre-publish comparables rows of the childcare record
    assert len(payload["rows"]) == 5719 + 20
    for archive in payload["event_archives"]:
        relative = archive["path"].removeprefix("data/")
        freshly_exported = (tmp_path / relative).read_bytes()
        assert len(freshly_exported) < 5_000_000
        assert (REPO / "data" / relative).read_bytes() == freshly_exported
        assert (
            REPO / "app" / "public" / "data" / relative
        ).read_bytes() == freshly_exported
    # The reform-validation registry is in there with its release history.
    rv_multi = [r for r in payload["rows"] if len(r["results"]) > 1]
    assert payload["summary"]["multi_release_claims"] == len(rv_multi) > 0
    # Rows without results carry a synthetic latest status for filtering, but
    # never a fabricated history entry.
    for row in payload["rows"]:
        if not row["results"]:
            assert row["latest"]["status"] == "not_computed"
            assert row["latest"]["status_effective"] == "not_computed"
            assert row["latest"]["value"] is None
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
