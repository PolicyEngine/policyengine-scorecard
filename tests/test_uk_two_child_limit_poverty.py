"""The two-child limit poverty benchmarks (lane uk-two-child-limit-poverty):
the DWP and Resolution Foundation rows are exactly what the adapters derive
from the vendored publications; the QC catches broken tables; the
certified-pair artifact holds the invariants a limit removal implies; every
result's status is one stated annotation; the RF and HM Treasury claims gain
a result without being duplicated; and nothing here is a calibration
target."""

import hashlib
import importlib.util
import json
import shutil
import sqlite3
import subprocess
from pathlib import Path

import pytest
from hypothesis import given
from hypothesis import strategies as st

from scorecard_db import ingest_uk_two_child_limit_poverty as lane
from scorecard_db import signs
from scorecard_db.models import STANDARD_CONDITIONS

REPO = Path(__file__).resolve().parent.parent
DWP_SRC = REPO / "sources" / "dwp-two-child-limit-poverty"
RF_SRC = REPO / "sources" / "rf-no-half-measures"
DB = REPO / "data" / "scorecard.db"
RESULTS = REPO / "results" / "uk" / "two_child_limit_poverty"

# DWP Table 1 (relative low income AHC) as published, read from the note on
# 2026-10-23: FYE -> (children, working-age adults, individuals)
TABLE_1 = {
    2027: (-300_000, -100_000, -400_000),
    2028: (-350_000, -150_000, -500_000),
    2029: (-450_000, -150_000, -600_000),
    2030: (-450_000, -150_000, -600_000),
    2031: (-450_000, -150_000, -550_000),
}
FIXED_LINES = ("relative_fixed_at_with_limit", "absolute_served", "absolute_fye2011")
GROUPS = ("people", "children", "under_18", "working_age_adults", "pensioners")


def _module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def dwp():
    return _module("dwp_two_child_limit_poverty_adapter", DWP_SRC / "adapter.py")


@pytest.fixture(scope="module")
def rf():
    return _module("rf_no_half_measures_adapter", RF_SRC / "adapter.py")


@pytest.fixture(scope="module")
def artifact():
    return lane.load_artifact()[0]


@pytest.fixture(scope="module")
def conn():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    yield c
    c.close()


# --- the vendored sources ---------------------------------------------------


@pytest.mark.parametrize("src", [DWP_SRC, RF_SRC])
def test_raw_files_match_their_recorded_hashes(src):
    recorded = json.loads((src / "source.json").read_text())["raw_sha256"]
    assert set(recorded) == {p.name for p in (src / "raw").iterdir()}
    for name, digest in recorded.items():
        assert hashlib.sha256((src / "raw" / name).read_bytes()).hexdigest() == digest


@pytest.mark.skipif(shutil.which("pdftotext") is None, reason="needs poppler")
def test_rf_extract_is_a_faithful_extract_of_the_pdfs():
    """Every page of the extract re-extracts from its PDF byte for byte."""
    text = (RF_SRC / "raw" / "pages_layout.txt").read_text()
    chunks = text.split("=== ")[1:]
    seen = {}
    for chunk in chunks:
        header, body = chunk.split(" ===\n", 1)
        name, _, page = header.rpartition(" page ")
        seen.setdefault(name, []).append(int(page))
        fresh = subprocess.run(
            [
                "pdftotext",
                "-layout",
                "-f",
                page,
                "-l",
                page,
                str(RF_SRC / "raw" / name),
                "-",
            ],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        assert body == fresh, f"{name} page {page}"
    spec = json.loads((RF_SRC / "source.json").read_text())["pages_extracted"]["pages"]
    assert seen == spec


def test_dwp_rows_are_the_adapters_output_and_the_published_table(
    dwp, tmp_path, monkeypatch
):
    monkeypatch.setattr(dwp, "OUT", tmp_path / "out.json")
    rows = dwp.run()
    assert rows == json.loads(
        (REPO / "data/externals/dwp-two-child-limit-poverty.json").read_text()
    )
    assert len(rows) == dwp.EXPECTED_ROWS == 123
    got = {
        (r["fye"], r["group"]): r["value"]
        for r in rows
        if r["table"] == "Table 1" and r["metric"] == "poverty_count_change"
    }
    for fye, (children, wa, individuals) in TABLE_1.items():
        assert (
            got[(fye, "children")],
            got[(fye, "working_age_adults")],
            got[(fye, "individuals")],
        ) == (
            children,
            wa,
            individuals,
        )


def test_rf_rows_are_the_adapters_output(rf, tmp_path, monkeypatch):
    monkeypatch.setattr(rf, "OUT", tmp_path / "out.json")
    rows = rf.run()
    assert rows == json.loads(
        (REPO / "data/externals/rf-no-half-measures.json").read_text()
    )
    by = {(r["measure_key"], r["fy"], r["metric"], r["page"]): r["value"] for r in rows}
    assert (
        by[
            (
                "ab2025_option__scrap_two_child_limit",
                "2029-30",
                "poverty_count_change",
                3,
            )
        ]
        == 480_000
    )
    assert (
        by[
            (
                "ab2025_option__scrap_two_child_limit",
                "2029-30",
                "benefit_cost_change",
                3,
            )
        ]
        == 3.5e9
    )


def _swap_after(html: str, anchor: str, old: str, new: str) -> str:
    """Replace the first ``old`` after ``anchor``."""
    at = html.index(anchor)
    hit = html.index(old, at)
    return html[:hit] + new + html[hit + len(old) :]


def test_dwp_qc_catches_a_changed_republication(dwp, monkeypatch):
    """Any difference between Tables 1-4 and the Child Poverty Strategy's
    A1-A4 beyond the one recorded cell raises."""
    original = dwp.body

    def tampered(path):
        html = original(path)
        if path == dwp.STRATEGY:
            html = _swap_after(html, "Table A1:", "-450,000", "-500,000")
        return html

    monkeypatch.setattr(dwp, "body", tampered)
    with pytest.raises(ValueError, match="Tables A1-A4 differ"):
        dwp.check_strategy(dwp.parse_tables(original(dwp.NOTE), "Table "), "")


def test_dwp_qc_catches_an_unrounded_cell(dwp):
    tables = dwp.parse_tables(dwp.body(dwp.NOTE), "Table ")
    tables[3]["cells"][("children", "number", 2030)] = "-260,000"
    with pytest.raises(ValueError, match="QC failed: Table 3"):
        dwp.check_rounding_and_sums(tables)


def test_dwp_qc_requires_the_table_2_header_typo_to_be_a_typo(dwp):
    tables = dwp.parse_tables(dwp.body(dwp.NOTE), "Table ")
    tables[2]["cells"] = dict(tables[1]["cells"])
    with pytest.raises(ValueError, match="repeats Table 1"):
        dwp.check_structure(tables)


@given(st.integers(min_value=-200, max_value=200))
def test_dwp_number_cells_round_trip(k):
    dwp_mod = _module("dwp_prop", DWP_SRC / "adapter.py")
    value = k * 50_000
    assert dwp_mod.number(f"{value:,}") == value


@given(st.integers(min_value=-999, max_value=999))
def test_dwp_point_cells_round_trip(k):
    dwp_mod = _module("dwp_prop2", DWP_SRC / "adapter.py")
    text = f"{k / 10:.1f}%"
    assert dwp_mod.points(text) == pytest.approx(k / 10)


# --- annotations ------------------------------------------------------------


def test_every_annotation_cites_a_basis_and_uses_known_facets():
    specs = lane.annotation_specs()
    ids = [a["id"] for a in specs]
    assert len(ids) == len(set(ids))
    for a in specs:
        assert a["basis"].strip()
        assert set(a["applies_to"]) <= lane.FACETS
        assert a.get("status") in (
            None,
            "comparable",
            "constructed",
            "concept_mismatch",
            "pe_gap",
        )


@given(
    a=st.floats(min_value=-1e7, max_value=1e7, allow_nan=False),
    b=st.floats(min_value=-1e7, max_value=1e7, allow_nan=False),
)
def test_spread_is_symmetric_and_reads_the_source_rounding(a, b):
    key = ("dwp", "poverty_count_change")
    assert lane._spread(*key, a, b) == lane._spread(*key, b, a)
    assert (lane._spread(*key, a, b) == "within_rounding") == (abs(a - b) <= 25_000)


# --- the certified-pair artifact ---------------------------------------------


def test_artifact_is_the_certified_pair(artifact):
    pair = json.loads(
        (REPO / "data/uk/two_child_limit_poverty/certified_pair.json").read_text()
    )
    assert artifact["pair_id"] == pair["pair_id"]
    assert artifact["installed"]["policyengine"] == pair["policyengine"]["version"]
    assert artifact["installed"]["policyengine-uk"] == pair["model_package"]["version"]
    assert (
        artifact["release_bundle"]["certified_data_build_id"]
        == pair["dataset"]["revision"]
    )
    assert artifact["route"].startswith("certified")


def test_each_world_executed_the_limit_it_names(artifact):
    for name, world in artifact["worlds"].items():
        for year, entry in world["years"].items():
            limit = entry["executed_limit"]
            if name == "with_limit":
                assert limit == 2
            elif name == "three_child_limit":
                assert limit == 3
            elif name == "removed_2025":
                assert limit >= 1e100
            else:
                assert limit == (2 if int(year) < 2026 else float("inf"))


def test_counts_are_bounded_by_their_populations(artifact):
    for world in artifact["worlds"].values():
        for entry in world["years"].values():
            pop = entry["population"]
            assert pop["pensioners"] >= 0
            assert pop["people"] == pytest.approx(
                pop["children"] + pop["working_age_adults"] + pop["pensioners"]
            )
            for basis in ("bhc", "ahc"):
                for line, counts in entry["below"][basis].items():
                    if line.endswith("disagreeing_households"):
                        continue
                    for g in GROUPS:
                        assert 0 <= counts[g] <= pop[g] * (1 + 1e-12), (line, g)


def test_the_engine_flag_is_the_recomputed_line(artifact):
    """in_relative_poverty_* and 60% of the world's own person-weighted
    median recomputed here mark the same households."""
    for world in artifact["worlds"].values():
        for entry in world["years"].values():
            for basis in ("bhc", "ahc"):
                assert (
                    entry["below"][basis]["relative_moving_disagreeing_households"] == 0
                )


def test_populations_do_not_move_between_worlds(artifact):
    worlds = artifact["worlds"]
    for year, entry in worlds["current_law"]["years"].items():
        assert entry["population"] == worlds["with_limit"]["years"][year]["population"]


def test_removing_the_limit_makes_no_household_worse_off(artifact):
    for name in ("current_law", "removed_2025", "three_child_limit"):
        for year, entry in artifact["worlds"][name]["years"].items():
            g = entry["gainers_vs_with_limit"]
            assert g["hbai_income_falls"]["households"] == 0, (name, year)
            assert g["equivalised_ahc_income_falls_households"] == 0
            assert g["equivalised_bhc_income_falls_households"] == 0
            assert g["benunits_uc_falls"] == 0


def test_counts_below_a_fixed_line_cannot_rise_when_the_limit_goes(artifact):
    """No household loses, so below any line held fixed across the worlds
    the removal world has no more people than the with-limit world."""
    wl = artifact["worlds"]["with_limit"]["years"]
    for name in ("current_law", "removed_2025"):
        for year, entry in artifact["worlds"][name]["years"].items():
            for basis in ("bhc", "ahc"):
                for line in FIXED_LINES:
                    for g in GROUPS:
                        assert (
                            entry["below"][basis][line][g]
                            <= wl[year]["below"][basis][line][g] + 1e-6
                        ), (name, year, basis, line, g)


def test_before_the_measure_starts_the_worlds_coincide(artifact):
    a = artifact["worlds"]["with_limit"]["years"]["2025"]
    b = artifact["worlds"]["current_law"]["years"]["2025"]
    assert a["below"] == b["below"] and a["sums_gbp"] == b["sums_gbp"]


def test_the_fye2011_line_sits_below_the_served_line_and_both_rise(artifact):
    years = sorted(artifact["worlds"]["with_limit"]["years"], key=int)
    for basis in ("bhc", "ahc"):
        lines = [
            artifact["worlds"]["with_limit"]["years"][y]["lines_gbp_year"][basis]
            for y in years
        ]
        for line in lines:
            assert line["absolute_fye2011"] < line["absolute_served"]
        for earlier, later in zip(lines, lines[1:]):
            assert later["absolute_fye2011"] > earlier["absolute_fye2011"]
            assert later["absolute_served"] > earlier["absolute_served"]


def test_the_decomposition_matches_the_artifact_and_sums(artifact):
    d = json.loads((RESULTS / "DECOMPOSITION.json").read_text())
    for basis in ("ahc", "bhc"):
        wl = artifact["worlds"]["with_limit"]["years"]["2029"]["below"][basis][
            "relative_moving"
        ]["children"]
        cl = artifact["worlds"]["current_law"]["years"]["2029"]["below"][basis][
            "relative_moving"
        ]["children"]
        assert d["certified"][basis]["relative_moving"]["children"] == pytest.approx(
            wl - cl
        )
        path = d["steps"][basis]["path"]
        assert sum(r["change"] for r in path[1:]) == pytest.approx(
            d["steps"][basis]["total_change"]
        )
        # the managed route and a bare Microsimulation on the certified pair agree
        bare = d["cells"]["microcosm_uk2.132.6"][basis]["relative_moving"]["children"]
        assert bare == pytest.approx(wl - cl, abs=1.0)


# --- the built database -------------------------------------------------------


def test_dwp_claims_are_minted_once_and_held_out(conn):
    rows = conn.execute(
        "SELECT * FROM external_scores WHERE json_extract(publication, '$.registry') = ?",
        (lane.REGISTRY_MARK,),
    ).fetchall()
    assert len(rows) == 123
    assert {r["source"] for r in rows} == {"dwp"}
    assert {r["calibration_relationship"] for r in rows} == {"held_out"}
    for r in rows:
        cond = json.loads(r["conditions"])
        assert set(cond) <= STANDARD_CONDITIONS
        assert cond["measure_key"] == lane.MEASURE
        assert json.loads(r["publication"])["publish_without_result"] is True


def test_every_lane_result_has_one_stated_status(conn):
    rows = conn.execute(
        "SELECT s.source, r.status, r.annotations FROM pe_results r"
        " JOIN external_scores s USING (claim_id) WHERE r.run_id LIKE 'uk-two-child-limit-poverty-%'"
    ).fetchall()
    assert len(rows) == lane._EXPECTED["results"]
    for r in rows:
        assert json.loads(r["annotations"])


def test_rf_and_hmt_claims_gain_a_result_without_a_duplicate(conn):
    nhm = conn.execute(
        "SELECT COUNT(*) FROM external_scores WHERE json_extract(publication, '$.url') LIKE '%No-half-measures%'"
    ).fetchone()[0]
    assert nhm == 26  # the harvest's own count; this lane mints none
    latest = conn.execute(
        "SELECT s.source, r.run_id FROM external_scores s JOIN pe_results r USING (claim_id)"
        " WHERE r.computed_at = (SELECT MAX(computed_at) FROM pe_results x WHERE x.claim_id = s.claim_id)"
        " AND s.source IN ('resolution_foundation', 'hm_treasury')"
        " AND r.run_id LIKE 'uk-two-child-limit-poverty-%'"
    ).fetchall()
    assert sorted(r["source"] for r in latest).count("hm_treasury") == 12
    assert sorted(r["source"] for r in latest).count("resolution_foundation") == 5


def test_signs_resolve_for_every_lane_result(conn):
    """Each attached result is oriented to its claim, so the exporter's sign
    rule never reads 'unknown' on this lane."""
    rows = conn.execute(
        "SELECT s.source, s.metric, s.conditions, s.value, r.annotations FROM pe_results r"
        " JOIN external_scores s USING (claim_id) WHERE r.run_id LIKE 'uk-two-child-limit-poverty-%'"
        " AND r.status != 'pe_gap'"
    ).fetchall()
    for r in rows:
        row = {
            "source": r["source"],
            "metric": r["metric"],
            "country": "UK",
            "conditions": json.loads(r["conditions"]),
            "latest": {"annotations": json.loads(r["annotations"])},
        }
        relation, basis = signs.classify(row)
        assert relation == signs.SAME, (r["source"], r["metric"], basis)
