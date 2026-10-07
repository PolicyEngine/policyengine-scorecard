"""The IRS/Census EITC participation lane (#2, nta-eitc): the committed
extract matches the adapter's contract and QC, the parser fails loudly, and
the ingest's claims, relationships and PE attachments are exact."""

import importlib.util
import json
from collections import Counter
from pathlib import Path

import pytest

from scorecard_db import ingest_irs_eitc_participation as eitc
from scorecard_db.models import CalibrationRelationship, ComparisonStatus, Metric
from scorecard_db.relationships import us_source_relationship

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "sources" / "irs-eitc-participation"
EXTRACT = REPO / "data" / "externals" / "irs-eitc-participation.json"


def _adapter():
    # a unique module name: several lanes ship an adapter.py
    spec = importlib.util.spec_from_file_location("eitc_adapter", SRC / "adapter.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_committed_extract_matches_contract():
    a = _adapter()
    rows = json.loads(EXTRACT.read_text())
    assert len(rows) == a.EXPECTED_ROWS
    acs = [r for r in rows if r["variant"] is None]
    assert len(acs) == 52 * 9
    assert {r["geography"] for r in acs} == {*a.STATES.values(), "US"}
    assert all(0.5 < r["value"] < 1 for r in acs)


def test_state_table_editions_agree_where_they_overlap():
    """The QC's second edition, re-run here without pypdf: every cell the
    May 2024 edition shares with the current one is identical."""
    a = _adapter()
    current = a.parse_state_table(a.PAGE.read_text(encoding="utf-8"), a.YEARS)
    old = a.parse_state_table(a.OLD_PAGE.read_text(encoding="utf-8"), a.OLD_YEARS)
    shared = [(s, y) for s in old for y in old[s] if y in current[s]]
    assert len(shared) == 52 * 7
    assert all(current[s][y] == old[s][y] for s, y in shared)


def test_footnotes_tie_to_the_national_row():
    a = _adapter()
    page = a.PAGE.read_text(encoding="utf-8")
    notes = a.page_footnotes(page)
    current = a.parse_state_table(page, a.YEARS)
    year, unclaimed = notes["unclaimed_share"]
    assert year == 2022 and round(100 - current["National"][2022], 1) == unclaimed
    assert notes["cps_national"] == (2022, 78.0)


def test_parser_fails_on_an_unknown_row_or_cell():
    a = _adapter()
    page = a.PAGE.read_text(encoding="utf-8")
    with pytest.raises(ValueError, match="unknown row label"):
        a.parse_state_table(page.replace(">Wyoming<", ">Guam<"), a.YEARS)
    with pytest.raises(ValueError, match="header"):
        a.parse_state_table(page, a.OLD_YEARS)
    bad = page.replace("80.8%", "80.8 %", 1)
    with pytest.raises(ValueError, match="unparsed cell"):
        a.parse_state_table(bad, a.YEARS)


def test_ces_recompute_catches_an_inconsistent_table():
    a = _adapter()
    rows = json.loads(EXTRACT.read_text())

    def cell(column):
        return next(r["value"] for r in rows if column in r["source_column"])

    good = {
        2021: {
            "eligible_tax_units": cell("Table 1, Tax Year 2021: Tax Units"),
            "taxpayer_rate": cell("Table 1, Tax Year 2021: Taxpayer") * 100,
            "eligible_dollars": cell("Table 1, Tax Year 2021: EITC Dollars"),
            "dollar_rate": cell("Table 1, Tax Year 2021: Dollar") * 100,
            "nonclaimants_nonfilers": 4.6e6,
            "nonclaimants_filers": 1.1e6,
            "nonclaimants_total": 5.7e6,
            "unclaimed_nonfilers": 5.6e9,
            "unclaimed_filers_no_eitc": 1.3e9,
            "unclaimed_underclaimants": 1.3e9,
            "unclaimed_total": 8.2e9,
        }
    }
    current = {"National": {2022: 80.8}}
    notes = {"unclaimed_share": (2022, 19.2)}
    a.qc(current, {}, notes, good)
    bad = {2021: {**good[2021], "nonclaimants_total": 6.7e6}}
    with pytest.raises(ValueError, match="non-claimants"):
        a.qc(current, {}, notes, bad)


def test_claims_and_relationships():
    scores = eitc.stage()
    assert len(scores) == 502
    rel = Counter((s.metric, s.calibration_relationship) for s in scores)
    consumed = CalibrationRelationship.CONSUMED_AS_TARGET
    held = CalibrationRelationship.HELD_OUT
    assert rel == {
        (Metric.PARTICIPATION_RATE, consumed): 52 * 9 + 1 + 3 * 2,
        (Metric.PARTICIPATION_GAP_COUNT, consumed): 9,
        (Metric.UNCLAIMED_BENEFIT_AMOUNT, consumed): 12,
        (Metric.ELIGIBLE_COUNT, held): 3,
        (Metric.BENEFIT_COST, held): 3,
    }
    # the two national TY2022 figures differ by method and stay apart
    us_2022 = [
        s
        for s in scores
        if s.period == 2022
        and s.conditions["geography"] == "US"
        and s.metric == Metric.PARTICIPATION_RATE
    ]
    assert sorted(s.conditions["survey_basis"] for s in us_2022) == ["acs", "cps"]
    with pytest.raises(ValueError, match="deliberate"):
        us_source_relationship("irs_eitc_participation", "eitc", Metric.GINI)


def test_results_attach_to_ty2022_taxpayer_rates():
    scores = eitc.stage()
    claims = {s.claim_id(): s for s in scores}
    results = eitc.results(scores)
    assert len(results) == 53
    for r in results:
        s = claims[r.claim_id]
        assert s.period == 2022 and s.conditions["rate_unit"] == "tax_units"
        assert r.status == ComparisonStatus.CONSTRUCTED
        assert 0 < r.computed_value < 1
        measured = [a for a in r.annotations if "Measured: after calibration" in a]
        assert len(measured) == 1


def test_staged_counterpart_records_its_toggle_check():
    staged = json.loads((SRC / "pe" / "us-6.2.1.json").read_text())
    check = staged["toggle_check"]
    assert check["forced"] == {"takes_up_eitc": 1.0, "would_file": 1.0}
    assert 0 < check["baseline"]["takes_up_eitc"] < 1
    # the certified data files every unit: recorded, and the notes say so
    assert check["baseline"]["would_file"] == 1.0
    assert check["forced_eligible_vs_rebuilt_entitlement_gap"] <= 1e-6
    us = staged["geographies"]["US"]
    assert us["entitled_flag_on_not_paid"] == 0.0
    assert us["participants"] + us["entitled_flag_off"] == pytest.approx(
        us["eligible_tax_units"], rel=1e-9
    )
