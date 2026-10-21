"""The £100,000 childcare limit costings (lane uk-childcare-100k): CenTax's
Table 4.2 and the Centre for British Progress appendix are exactly what the
adapters derive from the vendored PDFs; the QC catches broken tables; the
certified-pair artifact moves only the childcare heads; every result's
status is one stated annotation; the published dashboard figure stays in
the history beside the certified run; and a reform estimate is never a
calibration target."""

import hashlib
import importlib.util
import json
import shutil
import sqlite3
import subprocess
from collections import Counter
from itertools import product
from pathlib import Path

import pytest
from hypothesis import given
from hypothesis import strategies as st

from scorecard_db import ingest_uk_childcare_100k as lane
from scorecard_db import signs
from scorecard_db.models import STANDARD_CONDITIONS
from scorecard_db.models import CalibrationRelationship as CR
from scorecard_db.relationships import uk_relationship

REPO = Path(__file__).resolve().parent.parent
CENTAX_SRC = REPO / "sources" / "centax-childcare-100k"
CBP_SRC = REPO / "sources" / "cbp-rates-and-wrongs"
DB = REPO / "data" / "scorecard.db"
CERTIFIED = json.loads((REPO / "data" / "uk" / "certified_bundle.json").read_text())

# Table 4.2 as printed (printed page 41), read from the PDF on 2026-10-21:
# (scenario, year) -> (bunching before, after, static, intensive, extensive, net), £m
TABLE_4_2 = {
    ("central", 2028): (13_360, 3_850, -800, 150, 120, -520),
    ("central", 2030): (16_280, 4_300, -980, 210, 130, -640),
    ("high_cost", 2028): (9_710, 3_850, -820, 100, 120, -610),
    ("high_cost", 2030): (10_860, 4_300, -1_010, 120, 120, -770),
    ("low_cost", 2028): (58_510, 3_850, -580, 630, 90, 140),
    ("low_cost", 2030): (67_650, 4_300, -700, 770, 90, 160),
}
# CBP technical appendix, "Abolish Cliff" rows, £bn as printed
CBP_ABOLISH = {
    "endogenous_pension_exogenous_labour": (0.070, 0.077, 0.091, 0.132, 0.147, 0.172),
    "endogenous_labour_no_pension": (0.330, 0.349, 0.399, 0.427, 0.462, 0.507),
}


def _module(name: str, path: Path):
    # a unique module name: several lanes ship an adapter.py
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def centax():
    return _module("centax_childcare_adapter", CENTAX_SRC / "adapter.py")


@pytest.fixture(scope="module")
def cbp():
    return _module("cbp_rates_and_wrongs_adapter", CBP_SRC / "adapter.py")


@pytest.fixture(scope="module")
def artifact():
    return lane.load_artifact()[0]


# --- the vendored sources ---------------------------------------------------


@pytest.mark.parametrize("src", [CENTAX_SRC, CBP_SRC])
def test_raw_files_match_their_recorded_hashes(src):
    recorded = json.loads((src / "source.json").read_text())["raw_sha256"]
    assert set(recorded) == {p.name for p in (src / "raw").iterdir()}
    for name, digest in recorded.items():
        assert hashlib.sha256((src / "raw" / name).read_bytes()).hexdigest() == digest


@pytest.mark.skipif(shutil.which("pdftotext") is None, reason="needs poppler")
@pytest.mark.parametrize("src", [CENTAX_SRC, CBP_SRC])
def test_page_extract_is_a_faithful_extract_of_the_pdf(src):
    """Every page of the extract re-extracts from the PDF byte for byte, so
    a number in the extract is a number in the publication."""
    spec = json.loads((src / "source.json").read_text())
    pdf = next(p for p in (src / "raw").iterdir() if p.suffix == ".pdf")
    text = (src / "raw" / "pages_layout.txt").read_text()
    chunks = text.split("=== PDF page ")[1:]
    assert [int(c.split(" ", 1)[0].split("=")[0]) for c in chunks] == spec[
        "pages_extracted"
    ]["pdf_pages"]
    for chunk in chunks:
        header, body = chunk.split("===\n", 1)
        page = int(header.split()[0])
        fresh = subprocess.run(
            ["pdftotext", "-layout", "-f", str(page), "-l", str(page), str(pdf), "-"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        assert body == fresh, f"{src.name} PDF page {page}"


def test_centax_extract_is_the_adapters_output_and_the_published_table(centax):
    rows = centax.tidy(centax.parse_table_4_2(centax.pages()[42]))
    assert rows == json.loads(
        (REPO / "data/externals/centax-childcare-100k.json").read_text()
    )
    assert len(rows) == centax.EXPECTED_ROWS == 36
    columns = (*centax.COUNTS, *centax.MONEY)
    for (scenario, year), printed in TABLE_4_2.items():
        got = {
            r["column"]: r["value"]
            for r in rows
            if (r["scenario"], r["period"]) == (scenario, year)
        }
        want = {
            c: v * (1_000_000 if c in centax.MONEY else 1)
            for c, v in zip(columns, printed)
        }
        assert got == want, (scenario, year)
    assert {r["fy"] for r in rows if r["period"] == 2028} == {"2027-28"}
    assert {r["fy"] for r in rows if r["period"] == 2030} == {"2029-30"}


def test_centax_run_passes_every_qc(centax):
    assert len(centax.run()) == 36


def test_centax_qc_catches_a_component_that_no_longer_adds_up(centax):
    table = centax.parse_table_4_2(centax.pages()[42])
    table[("central", 2028)]["static_cost"] -= 30
    with pytest.raises(ValueError, match="components miss net"):
        centax.check_sums(table)


def test_centax_qc_catches_table_4_3_disagreeing(centax):
    pages = centax.pages()
    table = centax.parse_table_4_2(pages[42])
    table[("central", 2030)]["net_fiscal_cost"] = -650
    with pytest.raises(ValueError, match="Table 4.3"):
        centax.check_table_4_3(table, pages[45])


def test_centax_qc_catches_prose_disagreeing(centax):
    pages = centax.pages()
    table = centax.parse_table_4_2(pages[42])
    table[("central", 2030)]["intensive_margin"] = 200
    with pytest.raises(ValueError, match="prose"):
        centax.check_prose(table, pages[42] + pages[43])


def test_centax_qc_catches_a_shifted_row(centax):
    text = centax.pages()[42].replace("13,360", "13,360       9", 1)
    with pytest.raises(ValueError):
        centax.parse_table_4_2(text)


def test_cbp_extract_is_the_adapters_output_and_the_published_tables(cbp):
    rows = cbp.run()
    assert rows == json.loads(
        (REPO / "data/externals/cbp-rates-and-wrongs.json").read_text()
    )
    assert len(rows) == cbp.EXPECTED_ROWS == 72
    for model, printed in CBP_ABOLISH.items():
        got = [
            r["value"]
            for r in rows
            if (r["model"], r["policy"]) == (model, "abolish_cliff")
        ]
        assert got == [round(v * 1e9) for v in printed]
    assert [r["fy"] for r in rows[:6]] == [
        "2026-27",
        "2027-28",
        "2028-29",
        "2029-30",
        "2030-31",
        "2031-32",
    ]
    assert [r["period"] for r in rows[:6]] == [2027, 2028, 2029, 2030, 2031, 2032]


def test_cbp_qc_catches_a_column_shift(cbp):
    pages = cbp.pages()
    table = cbp.parse_table("2", pages[8])
    table["taper_1pct"][3] = ("0.100", 0.100)
    with pytest.raises(ValueError, match="not rising"):
        cbp.check_order("2", table)


# --- properties of the adapters' arithmetic ----------------------------------


@given(
    st.lists(
        st.floats(min_value=-2_000, max_value=2_000, allow_nan=False),
        min_size=3,
        max_size=3,
    )
)
def test_rounding_tolerance_covers_any_three_components(parts):
    """Invariant behind QC 4: if net is the exact sum of three components and
    each of the four figures is rounded to the nearest £10m, the rounded
    components miss the rounded net by at most SUM_TOLERANCE_GBP_M."""
    a = _module("centax_childcare_adapter_p", CENTAX_SRC / "adapter.py")
    step = a.ROUNDING_GBP_M

    def rnd(x):
        return step * round(x / step)

    net = sum(parts)
    assert abs(sum(rnd(p) for p in parts) - rnd(net)) <= a.SUM_TOLERANCE_GBP_M


@given(st.integers(min_value=-99_999, max_value=99_999))
def test_money_cells_round_trip(value):
    a = _module("centax_childcare_adapter_r", CENTAX_SRC / "adapter.py")
    cell = f"{'+' if value >= 0 else '-'}{abs(value):,}m"
    assert a._gbp_m(cell) == value


# --- the certified-pair artifact ---------------------------------------------


def test_artifact_ran_on_the_certified_bundle_without_behaviour(artifact):
    assert artifact["data_bundle"] == CERTIFIED["revision"]
    assert artifact["dataset"]["sha256"] == CERTIFIED["sha256"]
    assert artifact["engine_version"] == "2.89.2"
    assert artifact["behavioural_response"] == "none (static)"
    for world in (*artifact["worlds"].values(), *artifact["diagnostics"].values()):
        assert world["dataset_sha256_before"] == world["dataset_sha256_after"]


def test_each_world_removes_exactly_its_limits(artifact):
    hours = "gov.dfe.extended_childcare_entitlement.income.limit"
    tfc = "gov.hmrc.tax_free_childcare.income.income_limit"
    for year, block in artifact["worlds"]["baseline"]["years"].items():
        assert block["limits_executed"] == {hours: 100_000.0, tfc: 100_000.0}, year
    for year, block in artifact["worlds"]["free_hours"]["years"].items():
        assert block["limits_executed"] == {hours: 1e100, tfc: 100_000.0}, year
    for year, block in artifact["worlds"]["free_hours_and_tfc"]["years"].items():
        assert block["limits_executed"] == {hours: 1e100, tfc: 1e100}, year


def _d(art, world, year, var, group="worlds", base="baseline"):
    years = art[group]
    return (
        years[world]["years"][year]["sums_gbp"][var]
        - years[base]["years"][year]["sums_gbp"][var]
    )


def test_reforms_move_only_the_childcare_heads(artifact):
    heads = (*lane.FREE_HOURS, lane.TFC)
    for world in ("free_hours", "free_hours_and_tfc"):
        for year in artifact["worlds"][world]["years"]:
            moved = sum(_d(artifact, world, year, v) for v in heads)
            assert abs(_d(artifact, world, year, "gov_spending") - moved) < 1e6
            assert abs(_d(artifact, world, year, "gov_tax")) < 1e6
    # removing the 30-hours limit leaves Tax-Free Childcare alone
    for year in artifact["worlds"]["free_hours"]["years"]:
        assert abs(_d(artifact, "free_hours", year, lane.TFC)) < 1e6


def test_free_hours_leg_is_the_same_in_both_worlds(artifact):
    """Differential: the TFC limit does not touch the free hours, so the two
    reform worlds agree on every free-hours head."""
    for year in artifact["years"]:
        for v in lane.FREE_HOURS:
            a = artifact["worlds"]["free_hours"]["years"][str(year)]["sums_gbp"][v]
            b = artifact["worlds"]["free_hours_and_tfc"]["years"][str(year)][
                "sums_gbp"
            ][v]
            assert a == pytest.approx(b, rel=1e-12, abs=1.0), (year, v)


def test_removing_the_limit_costs_money_and_switches_universal_hours_off(artifact):
    for year in artifact["worlds"]["free_hours"]["years"]:
        assert lane.counterpart(artifact, lane.CENTAX, int(year)) < 0
        assert _d(artifact, "free_hours", year, "extended_childcare_entitlement") > 0
        assert _d(artifact, "free_hours", year, "universal_childcare_entitlement") < 0


def test_full_use_diagnostic_took_effect_and_costs_more(artifact):
    diag = artifact["diagnostics"]
    for world in diag.values():
        assert world["input_override"]["value"] == 30.0
        for mean in world["input_override"]["post_set_weighted_mean"].values():
            assert mean == pytest.approx(30.0)
    for year in diag["baseline__full_use_hours"]["years"]:
        full = sum(
            diag["free_hours__full_use_hours"]["years"][year]["sums_gbp"][v]
            - diag["baseline__full_use_hours"]["years"][year]["sums_gbp"][v]
            for v in lane.FREE_HOURS
        )
        assert full > -lane.counterpart(artifact, lane.CENTAX, int(year))


def test_no_child_under_one_receives_extended_hours(artifact):
    """The pe-under-ones construction note states this for every world and
    year; the artifact must keep it true."""
    for group in ("worlds", "diagnostics"):
        for world in artifact[group].values():
            for block in world["years"].values():
                assert block["counts"]["children_under_one_receiving_extended"] == 0


# --- claims, statuses, annotations -------------------------------------------


def test_claims_drops_relationships_and_conditions():
    scores, drops, _, _ = lane.stage()
    assert Counter(s.source for s in scores) == {lane.CENTAX: 24, lane.CBP: 12}
    assert drops == {"cbp_taper_rows": 60, "centax_bunching_counts": 12}
    for s in scores:
        assert s.calibration_relationship == CR.HELD_OUT
        assert s.reform.framework == "policy_ref"
        assert set(s.conditions) <= STANDARD_CONDITIONS
        assert s.publication["publish_without_result"] is True
        assert s.conditions["measure_key"] == lane.MEASURES[s.source]
    assert uk_relationship(lane.CBP, None)[0] == CR.HELD_OUT
    assert len({s.claim_id() for s in scores}) == len(scores)


def _all_facets(source):
    if source == lane.CENTAX:
        return [
            {"component": c, "scenario": sc, "period": p}
            for c, sc, p in product(
                lane.CENTAX_ATTACHED, ("central", "high_cost", "low_cost"), (2028, 2030)
            )
        ]
    return [
        {"model": m, "period": p} for m, p in product(CBP_ABOLISH, range(2027, 2032))
    ]


def test_every_attached_result_has_exactly_one_stated_status():
    """Exhaustive over the attached facets: no result's status is a
    default, and the statuses are the ones the lane promises."""
    scores, _, _, _ = lane.stage()
    specs = {
        lane.CENTAX: lane._spec(CENTAX_SRC / "annotations.json"),
        lane.CBP: lane._spec(CBP_SRC / "annotations.json"),
    }
    seen = Counter()
    for s in scores:
        if (
            s.source == lane.CENTAX
            and s.conditions["component"] not in lane.CENTAX_ATTACHED
        ):
            continue
        kinds = ["certified"]
        if s.source == lane.CENTAX and s.conditions["scenario"] == "central":
            kinds.append("published_dashboard")
        for kind in kinds:
            _, status = lane.match_annotations(s, kind, specs[s.source])
            key = (s.source, s.conditions.get("component"), kind)
            seen[(key, status.value)] += 1
    assert seen == {
        ((lane.CENTAX, "static_cost", "certified"), "comparable"): 6,
        ((lane.CENTAX, "net_fiscal_cost", "certified"), "concept_mismatch"): 6,
        ((lane.CENTAX, "static_cost", "published_dashboard"), "constructed"): 2,
        (
            (lane.CENTAX, "net_fiscal_cost", "published_dashboard"),
            "concept_mismatch",
        ): 2,
        ((lane.CBP, None, "certified"), "concept_mismatch"): 12,
    }


def test_every_annotation_has_a_basis_and_cites_files_that_exist():
    for path in (
        CENTAX_SRC / "annotations.json",
        CBP_SRC / "annotations.json",
        REPO / "results/uk/childcare_100k/construction_annotations.json",
    ):
        for a in lane._spec(path):
            assert a["basis"]
            for token in a["basis"].replace(";", " ").split():
                if token.startswith(("raw/", "pe/")):
                    assert (path.parent / token.rstrip(",")).exists(), (a["id"], token)
                if token.startswith("sources/"):
                    assert (REPO / token.rstrip(",")).exists(), (a["id"], token)


# --- the built database --------------------------------------------------------


def _rows(sql, *args):
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    out = conn.execute(sql, args).fetchall()
    conn.close()
    return out


def test_built_db_lane_counts_and_latest_result_is_the_certified_run():
    rows = _rows(
        "SELECT * FROM comparisons WHERE json_extract(publication, '$.registry') = ?",
        lane.REGISTRY_MARK,
    )
    assert len(rows) == 36
    computed = [r for r in rows if r["pe_value"] is not None]
    assert len(computed) == 22
    assert {r["data_bundle"] for r in computed} == {CERTIFIED["revision"]}
    assert {r["engine_version"] for r in computed} == {"2.89.2"}
    lanes = _rows("SELECT stage FROM lanes WHERE lane = ?", lane.LANE_ID)
    assert [r["stage"] for r in lanes] == ["computed"]


def test_published_dashboard_miss_stays_in_the_history():
    rows = _rows(
        "SELECT s.period, json_extract(s.conditions, '$.component') AS comp,"
        " r.computed_value, r.status, r.engine_version, r.data_bundle, r.computed_at"
        " FROM pe_results r JOIN external_scores s USING (claim_id)"
        " WHERE s.source = 'centax' AND r.run_id = 'uk-childcare-100k-dashboard-1b57118'"
        " ORDER BY s.period, comp"
    )
    got = {(r["period"], r["comp"]): (r["computed_value"], r["status"]) for r in rows}
    assert got == {
        (2028, "net_fiscal_cost"): (-434_000_000.0, "concept_mismatch"),
        (2028, "static_cost"): (-434_000_000.0, "constructed"),
        (2030, "net_fiscal_cost"): (-505_000_000.0, "concept_mismatch"),
        (2030, "static_cost"): (-505_000_000.0, "constructed"),
    }
    assert {r["engine_version"] for r in rows} == {"2.102.3"}
    assert {r["data_bundle"] for r in rows} == {
        "microcosm-uk-2024-25-national-20261002T230158Z-5c6b3f68"
    }
    # history, not the latest: the lane's certified run is newer
    certified = _rows(
        "SELECT MIN(computed_at) AS t FROM pe_results WHERE run_id = ?",
        lane.load_artifact()[0]["run_id"],
    )[0]["t"]
    assert max(r["computed_at"] for r in rows) < certified


def test_central_static_rows_carry_the_hours_draw_diagnosis():
    rows = _rows(
        "SELECT period, diagnosis_class, action_link, diagnosis_rationale"
        " FROM comparisons WHERE source = 'centax'"
        " AND json_extract(conditions, '$.component') = 'static_cost'"
        " AND diagnosis_class IS NOT NULL ORDER BY period"
    )
    assert [(r["period"], r["diagnosis_class"]) for r in rows] == [
        (2028, "pe_gap"),
        (2030, "pe_gap"),
    ]
    assert {r["action_link"] for r in rows} == {
        "https://github.com/PolicyEngine/microcosm/issues/1126"
    }
    assert "15.3 of 30 weekly hours" in rows[0]["diagnosis_rationale"]


def test_no_reform_estimate_is_a_calibration_target():
    """The 2026-08-02 rulings: another model's reform estimate is never a
    calibration target. never_calibrate() is keyed on metric (the poverty
    family), so this checks the rule on the built DB for every source:
    a claim that scores any world other than the baseline (a policy_ref
    reform, a PolicyEngine reform or an input-override counterfactual) is
    held out, never consumed_as_target or seed_source."""
    rows = _rows(
        "SELECT source, calibration_relationship, COUNT(*) AS n FROM external_scores"
        " WHERE json_extract(reform_json, '$.framework') != 'baseline'"
        " AND calibration_relationship != 'held_out'"
        " GROUP BY source, calibration_relationship"
    )
    assert [tuple(r) for r in rows] == []
    lane_rows = _rows(
        "SELECT DISTINCT json_extract(reform_json, '$.framework') AS fw,"
        " calibration_relationship AS cr FROM external_scores"
        " WHERE json_extract(publication, '$.registry') = ?",
        lane.REGISTRY_MARK,
    )
    assert [tuple(r) for r in lane_rows] == [("policy_ref", "held_out")]


def test_exported_feed_rows_state_the_lane_signs_and_history():
    """The deployed feed is what a reader sees: CenTax rows point the same
    way as PolicyEngine's; CBP states no sign rule, so its rows are
    unknown; the central static rows carry both results, the published
    figure first and the certified run as the latest."""
    feed = json.loads((REPO / "data" / "populations.json").read_text())
    rows = [
        r
        for r in feed["rows"]
        if r["conditions"].get("measure_key") in set(lane.MEASURES.values())
    ]
    assert len(rows) == 36
    got = Counter(
        (r["source"], r["sign_relative_to_pe"], r["sign_basis"]) for r in rows
    )
    assert got == {
        (lane.CENTAX, "same", "stated:exchequer:same"): 24,
        (lane.CBP, "unknown", "no_stated_convention"): 12,
    }
    central = [
        r
        for r in rows
        if r["conditions"].get("scenario") == "central"
        and r["conditions"].get("component") == "static_cost"
    ]
    assert len(central) == 2
    for r in central:
        assert [x["engine_version"] for x in r["results"]] == ["2.102.3", "2.89.2"]
        assert r["latest"]["data_bundle"] == CERTIFIED["revision"]
        assert r["latest"]["status_effective"] == "comparable"
        assert r["results"][0]["status_effective"] == "constructed"
    unscored = [r for r in rows if not r["results"]]
    assert len(unscored) == 14  # 12 CenTax margins + CBP's two 2031-32 cells
    assert all(r["conditions"].get("pe_missing") for r in unscored)
