"""Exhaustive, independently reconstructed PMD ingestion invariants.

The source is a sequence of cells, not a set of titles: repeated workbook
rows can have identical titles, heads and FYs. These tests retain the exact
harvest line identity, join every inventory/registry pointer to one SQL row,
and sum Decimal amounts within every event/table/head. The existing costings
slice keeps its rows and IDs; its source pointers and newer classification
metadata are available through the comprehensive lane's public cell mapping.
"""

from __future__ import annotations

import ast
import gzip
import hashlib
import json
import sqlite3
from collections import Counter, defaultdict
from dataclasses import replace
from decimal import Decimal, localcontext
from pathlib import Path

import pytest
from hypothesis import given, settings, strategies as st

from scorecard_db import ScorecardDB
from scorecard_db import ingest_obr_costings as costings
from scorecard_db import ingest_obr_pmd as mod
from scorecard_db.baselines import BASELINES
from scorecard_db.models import (
    STANDARD_CONDITIONS,
    ComparisonStatus,
    PEResult,
    baseline_key,
)
from scorecard_db.obr_pmd_identity import (
    EVENTS,
    HISTORICAL_EVENTS,
    assign_measure_keys,
    baseline_descriptor,
    event_key,
    event_slug,
)

ROOT = Path(__file__).resolve().parents[1]
HARVEST = ROOT / "sources/harvest-uk-2026-08-02/uk_obr/claims_staged.jsonl.gz"
INVENTORY = ROOT / "data/uk/events/inventory.jsonl"
TABLES = {
    "Tax Measures (Policy measures database)": 12773,
    "Spending Measures (Policy measures database)": 11531,
}


def canonical(row):
    return json.dumps(row, sort_keys=True, separators=(",", ":"))


@pytest.fixture(scope="module")
def source_cells():
    """Read source pointers without calling the ingestion's readers."""
    out = {}
    with gzip.open(HARVEST, "rt") as fh:
        for number, line in enumerate(fh, 1):
            row = json.loads(line)
            if row.get("source_table") in TABLES:
                out[number] = {
                    "row": row,
                    "line_sha256": hashlib.sha256(line.encode()).hexdigest(),
                    "replay_line_sha256": hashlib.sha256(
                        line.rstrip("\n").encode()
                    ).hexdigest(),
                }
    return out


@pytest.fixture(scope="module")
def inventory():
    return [json.loads(line) for line in INVENTORY.read_text().splitlines()]


@pytest.fixture(scope="module")
def legacy_by_line(source_cells):
    """Resolve the frozen slice using complete staged-row identity."""
    lines = defaultdict(list)
    for number, cell in source_cells.items():
        lines[canonical(cell["row"])].append(number)
    index = costings.measures()
    ab_join = costings._ab2025_join()
    out = {}
    for row in costings.load_rows():
        if row["source_table"] not in TABLES:
            continue
        matches = lines[canonical(row)]
        assert len(matches) == 1, matches
        number = matches[0]
        assert number not in out
        out[number] = costings._score(row, index, ab_join)
    assert len(out) == 552
    return out


@pytest.fixture(scope="module")
def staged():
    return mod.stage()


@pytest.fixture(scope="module")
def cell_mapping():
    matches = mod.cell_matches()
    mapping = {match["harvest_line"]: match for match in matches}
    assert len(mapping) == len(matches)
    return mapping


def snapshot(conn):
    return {
        table: [
            tuple(row)
            for row in conn.execute(f"SELECT * FROM {table} ORDER BY 1").fetchall()
        ]
        for table in ("external_scores", "baselines", "lanes", "pe_results")
    }


@pytest.fixture(scope="module")
def database(tmp_path_factory, legacy_by_line):
    path = tmp_path_factory.mktemp("obr-pmd") / "scores.db"
    # Ingest tests exercise SQL without rewriting the repository's feed files.
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(
            "scorecard_db.ingest_harvest.sync_lane_feed", lambda *a, **kw: None
        )
        costings.ingest(path)
        db = ScorecardDB(path)
        score = next(iter(legacy_by_line.values()))
        db.add_results(
            [
                PEResult(
                    claim_id=score.claim_id(),
                    computed_value=17.0,
                    status=ComparisonStatus.COMPARABLE,
                    engine_version="test-existing-result",
                    data_bundle="test-existing-bundle",
                    baseline_key=score.reform.baseline_key(),
                )
            ]
        )
        before = snapshot(db.conn)
        db.close()
        mod.ingest(path)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    yield path, conn, before
    conn.close()


@pytest.fixture(scope="module")
def claims_by_line(database, legacy_by_line):
    _, conn, _ = database
    sql_rows = conn.execute("SELECT * FROM external_scores").fetchall()
    by_id = {row["claim_id"]: row for row in sql_rows}
    out = {number: by_id[score.claim_id()] for number, score in legacy_by_line.items()}
    for row in sql_rows:
        pub = json.loads(row["publication"])
        if pub.get("registry") != mod.REGISTRY_MARK:
            continue
        number = pub["harvest_line"]
        assert number not in out
        out[number] = row
    return out


def test_partition_is_an_exact_identity_on_staged_rows(
    source_cells, legacy_by_line, claims_by_line, staged
):
    scores, accounting = staged
    assert len(source_cells) == 24304
    assert set(claims_by_line) == set(source_cells)
    assert len(scores) == 23752
    assert len({score.claim_id() for score in scores}) == 23752
    assert set(legacy_by_line).isdisjoint(set(source_cells) - set(legacy_by_line))
    assert Counter(canonical(c["row"]) for c in source_cells.values()) == (
        Counter(canonical(source_cells[n]["row"]) for n in legacy_by_line)
        + Counter(
            canonical(source_cells[n]["row"])
            for n in set(source_cells) - set(legacy_by_line)
        )
    )
    assert {score.claim_id() for score in scores} == {
        row["claim_id"] for n, row in claims_by_line.items() if n not in legacy_by_line
    }
    assert {key: accounting[key] for key in mod.EXPECTED} == mod.EXPECTED
    assert accounting["staged_by_table"] == mod.EXPECTED_STAGED_TABLES
    assert accounting["by_event"] == mod.EXPECTED_EVENTS


def test_table_event_counts_and_exact_decimal_conservation(
    source_cells, claims_by_line
):
    source_counts = Counter()
    db_counts = Counter()
    event_names = {event_slug(event): event for event in EVENTS}
    with localcontext() as ctx:
        ctx.prec = 100
        source_amounts = defaultdict(Decimal)
        db_amounts = defaultdict(Decimal)
        normalized_source = defaultdict(Decimal)
        normalized_db = defaultdict(Decimal)
        for number, cell in source_cells.items():
            src = cell["row"]
            row = claims_by_line[number]
            cond = src["conditions"]
            stored = json.loads(row["conditions"])
            head = cond.get("tax_head") or cond["spending_head"]
            key = (cond["fiscal_event"], src["source_table"], head)
            source_counts[key[:2]] += 1
            # Resolve the DB's normalized event independently, so conservation
            # also fails if a writer books a cell to the wrong fiscal event.
            db_key = (
                event_names[stored["fiscal_event"]],
                json.loads(row["publication"])["table"],
                stored.get("tax_head") or stored["spending_head"],
            )
            db_counts[db_key[:2]] += 1
            source_amounts[key] += Decimal(str(src["value_raw"])) * 1000000
            db_amounts[db_key] += Decimal(stored["value_verbatim"]) * 1000000
            normalized_source[key] += Decimal(str(src["value"]))
            normalized_db[db_key] += Decimal(str(row["value"]))
        assert source_counts == db_counts
        assert source_amounts == db_amounts
        assert normalized_source == normalized_db
    assert Counter(c["row"]["source_table"] for c in source_cells.values()) == Counter(
        TABLES
    )
    assert len({event for event, _ in source_counts}) == 84
    assert sum(source_counts.values()) == sum(db_counts.values()) == 24304


def test_every_inventory_fy_cell_joins_once_with_its_preferred_measure_key(
    source_cells, inventory, claims_by_line, legacy_by_line, cell_mapping
):
    registry_keys = {
        pointer["source_row_number"]: measure["measure_key"]
        for path in (ROOT / "data/uk/events").glob("*_measures.json")
        if mod.is_replay_registry(json.loads(path.read_text()))
        for measure in json.loads(path.read_text())["measures"]
        for pointer in measure["source_rows"]
    }
    joined = set()
    repeated = Counter()
    for record in inventory:
        repeated[
            (record["event"], record["table"], record["measure"], record["head"])
        ] += 1
        for fy, pointer in record["source_cells"].items():
            number = pointer["harvest_line"]
            assert number not in joined
            joined.add(number)
            source = source_cells[number]
            row = claims_by_line[number]
            cond = json.loads(row["conditions"])
            assert pointer["line_sha256"] == source["line_sha256"]
            assert cond["measure_key"] == (
                legacy_by_line[number].conditions["measure_key"]
                if number in legacy_by_line
                else registry_keys.get(
                    number, record["existing_registry_key"] or record["measure_key"]
                )
            )
            # Inventory and replay use different keys for some measures.
            # Both exact identities remain available without changing the
            # frozen slice's original conditions.
            assert (
                cell_mapping[number]["inventory_measure_key"] == record["measure_key"]
            )
            if number not in legacy_by_line:
                assert cond["inventory_measure_key"] == record["measure_key"]
            assert cond["fy"] == fy
            assert row["period"] == int(fy[:4]) + 1
            assert Decimal(cond["value_verbatim"]) == Decimal(
                str(record["costing_gbp_m"][fy])
            )
            assert row["value"] == source["row"]["value"]
    assert len(inventory) == 3796
    assert len(joined) == 22215
    assert max(repeated.values()) > 1  # Repeated occurrences are exercised.


def test_every_replay_registry_source_cell_joins_once(
    source_cells, claims_by_line, legacy_by_line, cell_mapping
):
    files = sorted(
        path
        for path in (ROOT / "data/uk/events").glob("*_measures.json")
        if mod.is_replay_registry(json.loads(path.read_text()))
    )
    assert len(files) == 6
    total = 0
    frozen_aliases = 0
    for path in files:
        registry = json.loads(path.read_text())
        seen = set()
        for measure in registry["measures"]:
            for pointer in measure["source_rows"]:
                number = pointer["source_row_number"]
                assert number not in seen, path.name
                seen.add(number)
                total += 1
                source = source_cells[number]
                row = claims_by_line[number]
                cond = json.loads(row["conditions"])
                assert pointer["source_row_sha256"] == source["replay_line_sha256"]
                assert pointer["source_row_id"] == (
                    f"obr_pmd_nov2025:{number}:{source['replay_line_sha256'][:16]}"
                )
                match = cell_mapping[number]
                assert match["claim_id"] == row["claim_id"]
                assert match["replay_measure_key"] == measure["measure_key"]
                if cond["measure_key"] != measure["measure_key"]:
                    assert number in legacy_by_line
                    frozen_aliases += 1
                assert cond["fiscal_event"] == registry["event_slug"]
                assert cond["fy"] == pointer["fy"]
                assert Decimal(str(row["value"])) == Decimal(
                    pointer["value_gbp_decimal"]
                )
        assert len(seen) == registry["accounting"]["rows_in"]
    assert total == 6096  # 4584 in the five events, 1512 in Autumn Budget 2025
    assert frozen_aliases == 132


def test_classification_is_copied_and_historical_cells_are_unclassified(
    source_cells, inventory, claims_by_line, legacy_by_line, cell_mapping
):
    classified = {
        p["harvest_line"]: record
        for record in inventory
        for p in record["source_cells"].values()
    }
    assert set(cell_mapping) == set(source_cells)
    for number, row in claims_by_line.items():
        cond = json.loads(row["conditions"])
        meta = cell_mapping[number]
        assert meta["claim_id"] == row["claim_id"]
        assert meta["measure_key"] == cond["measure_key"]
        if number in classified:
            record = classified[number]
            assert meta["event_key"] == record["event_key"]
            assert meta["inventory_measure_key"] == record["measure_key"]
            assert meta["pmd_class"] == record["class"]
            if number in legacy_by_line:
                continue  # Frozen slice has its original classifications.
            assert cond["event_key"] == record["event_key"]
            assert cond["pmd_class"] == record["class"]
            assert cond["pe_expressibility"] == record["expressibility"]
            assert cond["pe_readiness"] == record["readiness"]
            assert cond.get("pe_out_reason") == record["out_reason"]
            assert cond.get("pe_missing") == record["missing_machinery"]
            assert cond.get("pe_expressibility_note") == record["expressibility_note"]
        else:
            assert cond["pmd_class"] == "not_yet_classified"
            assert cond["pe_expressibility"] == "not_yet_classified"
            assert cond["pe_readiness"] == "not_yet_classified"
    assert len(set(source_cells) - set(classified)) == 2089


def test_original_values_semantics_and_full_provenance_are_retained(
    source_cells, claims_by_line, legacy_by_line, cell_mapping
):
    manifest = [
        json.loads(line)
        for line in (HARVEST.parent / "manifest.jsonl").read_text().splitlines()
    ]
    by_url = {entry["url"]: entry for entry in manifest}
    zeroes = 0
    for number, cell in source_cells.items():
        src = cell["row"]
        row = claims_by_line[number]
        cond = json.loads(row["conditions"])
        pub = json.loads(row["publication"])
        assert row["value"] == src["value"]
        assert row["status"] == src["status"]
        assert cond["value_verbatim"] == str(src["value_raw"])
        for key, value in src["publication"].items():
            assert pub[key] == value
        assert pub["publish_without_result"] is True
        assert pub["table"] == src["source_table"]
        assert row["source_model"] == src["source_model"]
        assert row["source_column"] == src["source_column"]
        assert row["unit_concept"] == "gbp"
        assert row["time_basis"] == "fiscal_year"
        for key in (
            "costing_phase",
            "basis",
            "sign_convention",
            "tax_head",
            "spending_head",
        ):
            if key in src["conditions"]:
                assert cond[key] == src["conditions"][key]
        if src.get("proposed_metric") == "exchequer_impact":
            assert cond["fiscal_measure"] == "exchequer_impact"
        if number not in legacy_by_line:
            entry = by_url[pub["url"]]
            assert pub["sha256"] == entry["sha256"]
            assert pub["wayback_snapshot"] == entry["wayback_snapshot"]
            assert pub["harvest_line"] == number
            assert pub["line_sha256"] == cell["line_sha256"]
            assert cond["source_row_id"] == (
                f"obr_pmd_nov2025:{number}:{cell['replay_line_sha256'][:16]}"
            )
            assert pub["normalization"] == src["normalization"]
        evidence = cell_mapping[number]["publication"]
        entry = by_url[evidence["url"]]
        assert evidence["sha256"] == entry["sha256"]
        assert evidence["wayback_snapshot"] == entry["wayback_snapshot"]
        assert evidence["harvest_line"] == number
        assert evidence["line_sha256"] == cell["line_sha256"]
        assert evidence["replay_line_sha256"] == cell["replay_line_sha256"]
        zeroes += row["value"] == 0
    assert zeroes > 0


def test_every_condition_is_closed_and_every_world_registered(database, claims_by_line):
    _, conn, _ = database
    registered = {baseline_key(desc) for desc, *_ in BASELINES}
    worlds = set()
    for row in claims_by_line.values():
        cond = json.loads(row["conditions"])
        assert set(cond) <= STANDARD_CONDITIONS
        assert row["period"] == int(cond["fy"][:4]) + 1
        assert row["baseline_key"] in registered
        worlds.add(row["baseline_key"])
        baseline = json.loads(row["reform_json"])["baseline"]
        assert cond["baseline_policy"] == baseline["policy"]
        assert row["calibration_relationship"] == "held_out"
    assert len(worlds) == 84
    assert (
        conn.execute(
            "SELECT COUNT(*) FROM external_scores s LEFT JOIN baselines b USING (baseline_key) "
            "WHERE s.source='obr_pmd' AND b.baseline_key IS NULL"
        ).fetchone()[0]
        == 0
    )
    extensions = {
        "event_key",
        "pmd_class",
        "pe_out_reason",
        "pe_readiness",
        "pe_expressibility_note",
        "source_row_id",
        "inventory_measure_key",
        "value_verbatim",
    }
    assert extensions <= STANDARD_CONDITIONS


def test_idempotence_preserves_existing_scores_results_and_lane(database):
    path, conn, before = database
    frozen = {row[0]: row for row in before["external_scores"]}
    current = {
        tuple(row)[0]: tuple(row)
        for row in conn.execute("SELECT * FROM external_scores")
    }
    assert all(current[key] == row for key, row in frozen.items())
    assert [tuple(r) for r in conn.execute("SELECT * FROM pe_results")] == before[
        "pe_results"
    ]
    initial = snapshot(conn)
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(
            "scorecard_db.ingest_harvest.sync_lane_feed", lambda *a, **kw: None
        )
        mod.ingest(path)
    assert snapshot(conn) == initial
    lane = conn.execute("SELECT * FROM lanes WHERE lane=?", (mod.LANE_ID,)).fetchone()
    assert lane["stage"] == "ingested"
    assert (
        conn.execute(
            "SELECT COUNT(*) FROM pe_results r JOIN external_scores s USING (claim_id) "
            "WHERE json_extract(s.publication, '$.registry')=?",
            (mod.REGISTRY_MARK,),
        ).fetchone()[0]
        == 0
    )


def test_registry_mark_has_one_writer_and_deletes_only_complement(database, tmp_path):
    writers = []
    for path in (ROOT / "scorecard_db").glob("ingest*.py"):
        tree = ast.parse(path.read_text())
        if any(
            isinstance(node, ast.Assign)
            and isinstance(node.value, ast.Constant)
            and node.value.value == mod.REGISTRY_MARK
            for node in ast.walk(tree)
        ):
            writers.append(path.name)
    assert writers == ["ingest_obr_pmd.py"]
    _, conn, _ = database
    clone = sqlite3.connect(tmp_path / "delete.db")
    conn.backup(clone)
    total = clone.execute("SELECT COUNT(*) FROM external_scores").fetchone()[0]
    clone.execute(
        "DELETE FROM external_scores WHERE json_extract(publication, '$.registry')=?",
        (mod.REGISTRY_MARK,),
    )
    assert clone.execute("SELECT changes()").fetchone()[0] == 23752
    assert (
        clone.execute("SELECT COUNT(*) FROM external_scores").fetchone()[0]
        == total - 23752
        == 621
    )
    assert clone.execute("SELECT COUNT(*) FROM pe_results").fetchone()[0] == 1
    clone.close()


def test_staging_twice_has_identical_ids_and_rows(staged):
    first, accounting = staged
    second, second_accounting = mod.stage()
    assert second_accounting == accounting
    assert [ScorecardDB.score_row(s) for s in first] == [
        ScorecardDB.score_row(s) for s in second
    ]


def test_event_slugs_and_historical_treasury_worlds_are_stable(
    source_cells, inventory, claims_by_line
):
    source_events = {
        cell["row"]["conditions"]["fiscal_event"] for cell in source_cells.values()
    }
    assert set(EVENTS) == source_events
    assert len(EVENTS) == len({event_slug(event) for event in EVENTS}) == 84
    assert len(HISTORICAL_EVENTS) == 52
    assert "Budget 2010" in HISTORICAL_EVENTS
    assert "Budget 2010 #2" not in HISTORICAL_EVENTS
    for event in EVENTS:
        assert event_slug(event) == event_key(event)
    for record in inventory:
        assert event_key(record["event"]) == record["event_key"]
    for number, row in claims_by_line.items():
        event = source_cells[number]["row"]["conditions"]["fiscal_event"]
        world = json.loads(row["reform_json"])["baseline"]
        assert world == baseline_descriptor(event)
        prefix = (
            "hmt_pre_measures_" if event in HISTORICAL_EVENTS else "obr_pre_measures_"
        )
        assert world["policy"] == prefix + event_slug(event)
    for event, slug in costings.EVENTS.items():
        assert event_slug(event) == slug
        assert baseline_descriptor(event) == costings.EVENT_BASELINE[slug]
    with pytest.raises(ValueError, match="unregistered fiscal event"):
        event_slug("Unpublished test event")


@given(
    st.lists(
        st.text(
            alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789:-",
            min_size=1,
            max_size=100,
        ),
        min_size=1,
        max_size=30,
    )
)
@settings(max_examples=75, deadline=None)
def test_inventory_key_function_groups_exact_titles_without_collisions(titles):
    rows = [{"event_key": "budget_1970", "measure": title} for title in titles]
    assign_measure_keys(rows)
    # Same exact title is one reform across heads; distinct titles get distinct
    # keys even when normalization or the 72-character truncation collide.
    keys_by_title = defaultdict(set)
    titles_by_key = defaultdict(set)
    for row in rows:
        keys_by_title[row["measure"]].add(row["measure_key"])
        titles_by_key[row["measure_key"]].add(row["measure"])
    assert all(len(keys) == 1 for keys in keys_by_title.values())
    assert all(len(group) == 1 for group in titles_by_key.values())
    repeated = [{"event_key": "budget_1970", "measure": title} for title in titles]
    assign_measure_keys(repeated)
    assert rows == repeated


def test_non_ok_status_and_source_reason_survive(tmp_path, cell_mapping):
    cell = mod.load_cells()[0]
    modified = {
        **cell.row,
        "value": None,
        "status": "suppressed",
        "status_reason": "Test source withheld its estimate",
    }
    score = mod.score_cell(
        replace(cell, row=modified), metadata=cell_mapping[cell.harvest_line]
    )
    assert score.value is None
    assert score.status == "suppressed"
    assert score.publication["status_reason"] == modified["status_reason"]
    db = ScorecardDB(tmp_path / "suppressed.db")
    db.upsert_scores([score])
    stored = db.conn.execute(
        "SELECT value, status, publication FROM external_scores"
    ).fetchone()
    assert stored["value"] is None
    assert stored["status"] == "suppressed"
    assert (
        json.loads(stored["publication"])["status_reason"] == modified["status_reason"]
    )
    db.close()


def test_unknown_source_fields_conditions_and_fy_drift_fail(cell_mapping):
    cell = mod.load_cells()[0]
    metadata = cell_mapping[cell.harvest_line]
    with pytest.raises(ValueError, match="unhandled staged fields"):
        mod.score_cell(
            replace(cell, row={**cell.row, "unmapped_field": "test"}), metadata=metadata
        )
    with pytest.raises(ValueError, match="condition"):
        mod.score_cell(
            replace(
                cell,
                row={
                    **cell.row,
                    "conditions": {
                        **cell.row["conditions"],
                        "unmapped_condition": "test",
                    },
                },
            ),
            metadata=metadata,
        )
    with pytest.raises(ValueError, match="fy"):
        mod.score_cell(
            replace(cell, row={**cell.row, "period": cell.row["period"] + 1}),
            metadata=metadata,
        )


def test_ingest_failure_rolls_back_the_whole_lane(tmp_path, monkeypatch):
    path = tmp_path / "rollback.db"
    monkeypatch.setattr(
        "scorecard_db.ingest_harvest.sync_lane_feed", lambda *a, **kw: None
    )
    costings.ingest(path)
    db = ScorecardDB(path)
    before = snapshot(db.conn)
    db.close()

    def fail_registration(db):
        raise RuntimeError("test transaction failure after score insertion")

    monkeypatch.setattr(
        "scorecard_db.baselines.register_baselines_txn", fail_registration
    )
    with pytest.raises(RuntimeError, match="test transaction failure"):
        mod.ingest(path)
    db = ScorecardDB(path)
    assert snapshot(db.conn) == before
    db.close()


@given(st.integers(min_value=0, max_value=23751))
@settings(max_examples=75, deadline=None)
def test_claim_identity_is_invariant_to_condition_order(staged, index):
    scores, _ = staged
    original = scores[index]
    reordered = replace(
        original, conditions=dict(reversed(list(original.conditions.items())))
    )
    assert reordered.claim_id() == original.claim_id()
    assert reordered.period == int(reordered.conditions["fy"][:4]) + 1
    # Workbook occurrences remain distinct even when all policy semantics match.
    changed = replace(
        original,
        conditions={
            **original.conditions,
            "source_row_id": original.conditions["source_row_id"] + ":other_occurrence",
        },
    )
    assert changed.claim_id() != original.claim_id()


def test_only_replay_registries_join_the_published_scores():
    historical = json.loads(
        (ROOT / "data/uk/events/spring_statement_2022_measures.json").read_text()
    )
    assert not mod.is_replay_registry(historical)
    assert mod.is_replay_registry(
        json.loads(
            (ROOT / "data/uk/events/autumn_budget_2025_measures.json").read_text()
        )
    )
    assert mod.is_replay_registry({"measures": []})
