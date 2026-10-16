"""An edition adds delta claims while November remains an immutable source."""

from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import replace

import pytest

from scorecard_db import ScorecardDB
from scorecard_db import ingest_obr_costings as costings
from scorecard_db import ingest_obr_pmd as november
from scorecard_db import ingest_obr_pmd_march2026 as march
from scorecard_db.export_populations import export
from scorecard_db.models import STANDARD_CONDITIONS, ComparisonStatus, PEResult
from scorecard_db.obr_pmd_diff import compare_editions, load_staged


def _cell(number, row):
    raw = (json.dumps(row, ensure_ascii=False) + "\n").encode()
    return march.Cell(
        number,
        hashlib.sha256(raw).hexdigest(),
        hashlib.sha256(raw.rstrip(b"\n")).hexdigest(),
        row,
    )


def _snapshot(conn):
    return {
        table: [tuple(row) for row in conn.execute(f"SELECT * FROM {table} ORDER BY 1")]
        for table in ("external_scores", "pe_results", "baselines", "lanes")
    }


def _all_rows(payload, directory):
    rows = list(payload["rows"])
    for archive in payload["event_archives"]:
        compact = json.loads(
            (directory / archive["path"].removeprefix("data/")).read_text()
        )
        rows.extend(
            {
                **compact["common"],
                **row,
                "conditions": {**compact["common_conditions"], **row["conditions"]},
            }
            for row in compact["rows"]
        )
    return {row["claim_id"]: row for row in rows}


@pytest.fixture(scope="module")
def synthetic_delta():
    """Use actual November source identities with a tiny synthetic next edition."""
    old_cells = november.load_cells()
    rows = [copy.deepcopy(cell.row) for cell in old_cells[:2]]
    rows[1]["value_raw"] += 1
    rows[1]["value"] += 1000000
    fresh = copy.deepcopy(rows[0])
    fresh["reform_hint"] = "Synthetic new measure"
    rows.append(fresh)
    artifact = {
        "url": "https://obr.uk/docs/dlm_uploads/Policy_measures_database_March_2026.xlsx",
        "wayback_snapshot": "https://web.archive.org/web/20260410184123id_/https://obr.uk/docs/dlm_uploads/Policy_measures_database_March_2026.xlsx",
        "sha256": "a" * 64,
        "receipt_sha256": "b" * 64,
    }
    for row in rows:
        row["conditions"]["edition"] = march.EDITION
        row["publication"].update(
            {
                "url": artifact["url"],
                "wayback": artifact["wayback_snapshot"],
                "edition": march.EDITION,
                "sha256": artifact["sha256"],
                "receipt_sha256": artifact["receipt_sha256"],
            }
        )
    cells = [_cell(number, row) for number, row in enumerate(rows, 1)]
    diff = compare_editions(load_staged(november.HARVEST), rows)
    metadata = march._metadata(cells, diff)
    return cells, diff, metadata, artifact


def _stage_synthetic(monkeypatch, synthetic_delta):
    cells, diff, metadata, artifact = synthetic_delta
    monkeypatch.setattr(march, "load_cells", lambda: cells)
    monkeypatch.setattr(march, "edition_diff", lambda *args: diff)
    monkeypatch.setattr(march, "_metadata", lambda *args: metadata)
    monkeypatch.setattr(march, "manifest", lambda: artifact)
    return march.stage()


def test_only_changed_and_new_cells_receive_edition_claims(
    monkeypatch, synthetic_delta
):
    scores, accounting = _stage_synthetic(monkeypatch, synthetic_delta)
    assert accounting["changed"] == accounting["new"] == 1
    assert accounting["ingested"] == len(scores) == 2
    assert accounting["edition_diff"]["totals"]["identical"] == 1
    assert {score.conditions["source_row_id"].split(":")[1] for score in scores} == {
        "2",
        "3",
    }
    for score in scores:
        assert score.conditions["edition"] == march.EDITION
        assert set(score.conditions) <= STANDARD_CONDITIONS
        assert score.publication["edition"] == march.EDITION
        assert score.publication["registry"] == march.REGISTRY_MARK
        assert score.publication["receipt_sha256"] == "b" * 64
        assert score.period == int(score.conditions["fy"][:4]) + 1
        assert score.conditions["sign_convention"] == "positive_gain_to_exchequer"
        assert score.value == float(score.conditions["value_verbatim"]) * 1000000
    assert scores[1].conditions["pe_readiness"] == "not_yet_classified"
    assert "inventory_measure_key" not in scores[1].conditions
    # Edition is an identity axis even if source-row evidence is held constant.
    assert (
        replace(
            scores[0],
            conditions={
                **scores[0].conditions,
                "edition": "November 2025",
            },
        ).claim_id()
        != scores[0].claim_id()
    )


def test_additive_ingest_preserves_every_november_row_result_and_export(
    tmp_path,
    monkeypatch,
    synthetic_delta,
):
    _stage_synthetic(monkeypatch, synthetic_delta)
    monkeypatch.setattr(
        "scorecard_db.ingest_harvest.sync_lane_feed", lambda *args, **kwargs: None
    )
    path = tmp_path / "scores.db"
    costings.ingest(path)
    november.ingest(path)
    db = ScorecardDB(path)
    previous_ids = november.claim_ids_by_source_cell()
    old_line = synthetic_delta[1].changed[0].previous_line
    old_id = previous_ids[old_line]
    old = db.conn.execute(
        "SELECT baseline_key FROM external_scores WHERE claim_id=?", (old_id,)
    ).fetchone()
    db.add_results(
        [
            PEResult(
                claim_id=old_id,
                computed_value=12,
                status=ComparisonStatus.COMPARABLE,
                engine_version="frozen-test-result",
                data_bundle="frozen-test-bundle",
                baseline_key=old["baseline_key"],
            )
        ]
    )
    before = _snapshot(db.conn)
    before_directory = tmp_path / "before"
    before_directory.mkdir()
    before_path = before_directory / "populations.json"
    export(path, before_path, built="2026-10-15")
    before_rows = _all_rows(json.loads(before_path.read_text()), before_directory)
    march.ingest(path)
    after = _snapshot(db.conn)
    old_scores = {row[0]: row for row in before["external_scores"]}
    current = {row[0]: row for row in after["external_scores"]}
    assert len(current) == len(old_scores) + 2
    assert all(current[key] == row for key, row in old_scores.items())
    for table in ("pe_results", "baselines", "lanes"):
        assert after[table] == before[table]
    assert old_id in current
    assert november.claim_ids_by_source_cell() == previous_ids
    # Repeat replacement touches only March's own registry mark.
    march.ingest(path)
    assert _snapshot(db.conn) == after
    after_directory = tmp_path / "after"
    after_directory.mkdir()
    after_path = after_directory / "populations.json"
    export(path, after_path, built="2026-10-15")
    after_rows = _all_rows(json.loads(after_path.read_text()), after_directory)
    assert len(after_rows) == len(before_rows) + 2
    assert {key: after_rows[key] for key in before_rows} == before_rows
    # Both new scores go to compact archives; the initial rows stay unchanged.
    assert (
        json.loads(before_path.read_text())["rows"]
        == json.loads(after_path.read_text())["rows"]
    )
    db.close()


def test_edition_ingest_failure_rolls_back(tmp_path, monkeypatch, synthetic_delta):
    _stage_synthetic(monkeypatch, synthetic_delta)
    path = tmp_path / "rollback.db"
    db = ScorecardDB(path)
    before = _snapshot(db.conn)

    def fail(db):
        raise RuntimeError("test baseline registration failure")

    monkeypatch.setattr("scorecard_db.baselines.register_baselines_txn", fail)
    with pytest.raises(RuntimeError, match="test baseline"):
        march.ingest(path)
    assert _snapshot(db.conn) == before
    db.close()


def test_march_source_digest_is_pinned(tmp_path, monkeypatch):
    import gzip

    altered = tmp_path / "changed.jsonl.gz"
    with gzip.open(altered, "wb") as stream:
        stream.write(b"{}\n")
    monkeypatch.setattr(march, "HARVEST", altered)
    with pytest.raises(ValueError, match="digest drifted"):
        march.load_cells()


@pytest.mark.parametrize("field", ["sha256", "receipt_sha256"])
def test_staged_provenance_cannot_be_relabelled(synthetic_delta, field):
    cells, _, metadata, artifact = synthetic_delta
    changed = copy.deepcopy(cells[1].row)
    changed["publication"][field] = "c" * 64
    with pytest.raises(ValueError, match="workbook provenance drift"):
        march.score_cell(replace(cells[1], row=changed), metadata[2], artifact)


def test_locked_edition_ingests_exact_delta():
    scores, accounting = march.stage()
    assert len(scores) == len({score.claim_id() for score in scores}) == 246
    assert accounting["new"] == 246
    assert accounting["changed"] == 0
    assert accounting["by_event"] == {"Spring Forecast 2026": 246}
    assert accounting["edition_diff"]["totals"] == {
        "identical": 24302,
        "changed": 0,
        "new": 246,
        "removed": 2,
    }
    assert len({score.conditions["measure"] for score in scores}) == 19
    assert (
        len(
            {
                (
                    score.conditions["measure"],
                    score.conditions.get("tax_head"),
                    score.conditions.get("spending_head"),
                    score.publication["table"],
                )
                for score in scores
            }
        )
        == 41
    )
    for score in scores:
        assert score.conditions["fiscal_event"] == "spring_forecast_2026"
        assert (
            score.conditions["baseline_policy"]
            == "obr_pre_measures_spring_forecast_2026"
        )
        assert score.conditions["edition"] == "March 2026"
        assert score.conditions["source_row_id"].startswith("obr_pmd_mar2026:")
        assert score.conditions["pe_readiness"] == "not_yet_classified"
        assert "inventory_measure_key" not in score.conditions
        assert score.publication["workbook_cell"]
        assert score.publication["sha256"] == march.manifest()["sha256"]
