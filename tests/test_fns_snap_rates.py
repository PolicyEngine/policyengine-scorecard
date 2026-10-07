"""The FNS state SNAP participation-rate lane (#2): the committed extract
matches the adapter's contract and its own arithmetic, the parser fails
loudly, and the ingest's claims, drops and PE attachments are exact."""

import importlib.util
import json
from collections import Counter
from pathlib import Path

import pytest

from scorecard_db import ingest_fns_snap_rates as fns
from scorecard_db.models import CalibrationRelationship, ComparisonStatus, Metric

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "sources" / "fns-snap-rates"
EXTRACT = REPO / "data" / "externals" / "fns-snap-rates.json"


def _adapter():
    # a unique module name: several lanes ship an adapter.py, and a bare
    # `import adapter` would return whichever one another test cached
    spec = importlib.util.spec_from_file_location("fns_adapter", SRC / "adapter.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _rows():
    return json.loads(EXTRACT.read_text())


def _cell(rows, metric, geo, period, variant=None):
    hits = [
        r
        for r in rows
        if (r["metric"], r["geography"], r["period"], r["variant"])
        == (metric, geo, period, variant)
    ]
    assert len(hits) == 1, (metric, geo, period, variant, len(hits))
    return hits[0]["value"]


def test_committed_extract_matches_contract():
    a = _adapter()
    rows = _rows()
    assert len(rows) == a.EXPECTED_ROWS
    states = set(a.STATES.values())
    assert {r["geography"] for r in rows if r["metric"] == "eligible_count"} == (
        states | {"US"}
    )


def test_rates_recompute_from_their_published_parts():
    """Report eq. 44: rate = eligible participants / eligible people. The
    extract carries all three, so the rate is checked without the PDF."""
    a = _adapter()
    rows = _rows()
    for code in a.STATES.values():
        for period in a.YEARS:
            rate = _cell(rows, "participation_rate", code, period)
            part = _cell(rows, "federal_rules_eligible_participant_count", code, period)
            elig = _cell(rows, "eligible_count", code, period)
            assert abs(part / elig - rate) < 6e-5, (code, period)


def test_capped_cells_are_exhibit_a3_plus_the_pinned_secondary_cap():
    a = _adapter()
    rows = _rows()
    capped = {
        (r["geography"], r["period"])
        for r in rows
        if r["metric"] == "participation_rate"
        and r["variant"] is None
        and r["geography"] in a.STATES.values()
        and r["value"] == 1.0
    }
    listed = {
        (r["geography"], r["period"])
        for r in rows
        if r["variant"] == "uncapped_implied"
    }
    assert len(listed) == 16  # "16 instances" (report Appendix A)
    assert capped == listed | {("MI", "FY 2022")}
    assert all(
        _cell(rows, "participation_rate", g, p, "uncapped_implied") > 1
        for g, p in listed
    )


def test_parser_fails_on_an_unexpected_row():
    a = _adapter()
    title = a.TABLES["B.2b"][0]
    body = [f"{label} 90 92" for label in [*a.REGIONS, a.US]]
    good = "\n".join(["Appendix B", title, ". FY 2020 FY 2022", *body, "  "])
    assert set(a.parse_table([good], "B.2b")) == set(a.REGIONS) | {a.US}
    bad = good.replace("Midwest Region 90 92", "Midwest Region 90 92\nGuam 70 71")
    with pytest.raises(ValueError, match="missing|unparsed"):
        a.parse_table([bad], "B.2b")
    short = good.replace("Western Region 90 92", "Western Region 90")
    with pytest.raises(ValueError, match="values, want 2"):
        a.parse_table([short], "B.2b")


def test_parser_follows_a_table_onto_its_continuation_page():
    a = _adapter()
    title = a.TABLES["A.1"][0]
    names = [*a.STATES, a.US]
    first = "\n".join([title, ". FY 2020 FY 2022", *[f"{n} 1 2" for n in names[:20]]])
    second = "\n".join(
        ["Appendix A", ". FY 2020 FY 2022", *[f"{n} 1 2" for n in names[20:]]]
    )
    assert len(a.parse_table([first, second], "A.1")) == len(names)


def test_claims_relationships_and_drops():
    scores, drops, uncapped = fns.stage()
    assert len(scores) == 208
    by_metric = Counter(s.metric for s in scores)
    assert by_metric == {Metric.PARTICIPATION_RATE: 104, Metric.ELIGIBLE_COUNT: 104}
    rel = {s.metric: s.calibration_relationship for s in scores}
    # the numerator class (FNS caseloads) is a calibration target; the
    # eligible count is the held-out signal
    assert rel[Metric.PARTICIPATION_RATE] == CalibrationRelationship.CONSUMED_AS_TARGET
    assert rel[Metric.ELIGIBLE_COUNT] == CalibrationRelationship.HELD_OUT
    assert drops == {
        "admin:federal_rules_eligible_participant_count": 102,
        "admin:federal_rules_eligible_share": 102,
        "admin:participant_count": 104,
        "fns_region": 14,
        "method_constant": 2,
        "variant:standard_error": 204,
        "variant:uncapped_implied": 16,
    }
    assert len(uncapped) == 16


def test_results_attach_to_fy2022_with_the_federal_rules_construction():
    scores, _, uncapped = fns.stage()
    results = fns.results(scores, uncapped)
    period = {s.claim_id(): s.period for s in scores}
    assert len(results) == 104
    assert {period[r.claim_id] for r in results} == {2022}
    assert all(r.status == ComparisonStatus.CONSTRUCTED for r in results)
    assert all(r.data_bundle == "populace-us-2024-spm-20260915" for r in results)
    assert all("is_tanf_non_cash_eligible" in r.pe_construction for r in results)
    assert all(len(r.annotations) >= 5 for r in results)
    capped = [r for r in results if any("is capped" in a for a in r.annotations)]
    # rate + eligible count for the 9 Exhibit A.3 cells of FY 2022 and
    # Michigan's secondary cap
    assert len(capped) == 2 * 10


def test_staged_counterpart_records_its_toggle_check():
    staged = json.loads((SRC / "pe" / "us-6.2.1.json").read_text())
    federal = staged["toggle_check"]["federal"]
    baseline = staged["toggle_check"]["baseline"]
    assert len(federal) == len(baseline) == 12
    assert set(federal.values()) == {0.0}
    assert all(v > 0 for v in baseline.values())
    us = staged["geographies"]["US"]
    assert us["eligible_persons"] < us["baseline_eligible_persons"]
    assert 0 < us["participation_rate"] <= 1


def test_saturation_and_grain_notes_follow_their_matchers():
    scores, _, uncapped = fns.stage()
    staged = json.loads((SRC / "pe" / "us-6.2.1.json").read_text())
    share = {g: v["takeup_flag_share"] for g, v in staged["geographies"].items()}
    claim = {s.claim_id(): s for s in scores}
    for r in fns.results(scores, uncapped):
        s = claim[r.claim_id]
        noted = any("This State is saturated" in a for a in r.annotations)
        expect = (
            s.metric == Metric.PARTICIPATION_RATE
            and share[s.conditions["geography"]] >= 1 - 1e-9
        )
        assert noted == expect, (s.conditions, r.computed_value)
        if noted:
            # a saturated State's eligible non-participants have no benefit,
            # so its rate sits at or just under 100%
            assert r.computed_value > 0.95
        grain = [a for a in r.annotations if a.startswith("FNS counts people")]
        assert len(grain) == 1 and "Measured: as served" in grain[0]
        assert "(Table A.1)" in grain[0]
