"""CBO publication 61367, P.L. 119-21 vs the January 2025 baseline (lane
cbo-cost-estimates): the committed extract is exactly what the adapter
derives from raw/, the QC catches a broken cell, quote or sum, and the
claims carry their windows and the explicit January-2025 baseline."""

import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path

import pytest

from scorecard_db import ingest_cbo
from scorecard_db.models import CalibrationRelationship as CR
from scorecard_db.models import Metric

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "sources" / "cbo-pl119-21"
EXTRACT = REPO / "data" / "externals" / "cbo-pl119-21.json"


def _adapter():
    # a unique module name: several lanes ship an adapter.py
    spec = importlib.util.spec_from_file_location(
        "cbo_pl119_21_adapter", SRC / "adapter.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def parsed():
    a = _adapter()
    figures = a.parse_figures(a.read_sheets(a.WORKBOOK))
    letter = a._pdf_text(a.LETTER)
    values = a.parse_statements(a._pdf_text(a.SUPPLEMENT))
    return a, figures, letter, values


def test_raw_files_match_their_recorded_hashes():
    recorded = json.loads((SRC / "source.json").read_text())["raw_sha256"]
    for name, digest in recorded.items():
        assert hashlib.sha256((SRC / "raw" / name).read_bytes()).hexdigest() == digest


def test_committed_extract_is_the_adapters_output(parsed):
    a, figures, letter, values = parsed
    a.qc_figures(figures, letter)
    a.qc_statements(values)
    rows = a.tidy(figures, values)
    assert rows == json.loads(EXTRACT.read_text())
    assert len(rows) == a.EXPECTED_ROWS == 115


def test_qc_catches_a_broken_channel_sum(parsed):
    a, figures, _, _ = parsed
    broken = {k: {d: list(c) for d, c in t.items()} for k, t in figures.items()}
    broken["Figure 1"]["7th"][0] += 10  # 1,759 -> 1,769 dollars
    with pytest.raises(ValueError, match="Figure 1 7th"):
        a.qc_figures(broken, None)


def test_qc_catches_a_cell_the_letter_contradicts(parsed):
    a, figures, letter, _ = parsed
    broken = {k: {d: list(c) for d, c in t.items()} for k, t in figures.items()}
    # the letter says 2.7 percent; a consistent shift keeps check 2 quiet
    broken["Figure 2"]["Highest"][0] += 0.1
    broken["Figure 2"]["Highest"][4] += 0.1
    with pytest.raises(ValueError, match="letter percent, Highest"):
        a.qc_figures(broken, letter)


def test_qc_catches_work_requirement_groups_that_do_not_add_up(parsed):
    a, _, _, values = parsed
    broken = dict(values)
    value, text = broken["work_requirements_waiver_loss"]
    broken["work_requirements_waiver_loss"] = (value - 100_000, text)
    with pytest.raises(ValueError, match="section 10102 groups"):
        a.qc_statements(broken)


def test_every_statement_is_verbatim_in_its_source_column():
    rows = [r for r in json.loads(EXTRACT.read_text()) if r["family"] == "snap"]
    assert len(rows) == 15
    for r in rows:
        assert r["source_column"].startswith(
            f'61367-SNAP.pdf, section {r["section"]}: "'
        )


def test_claims_windows_and_baseline():
    scores = ingest_cbo.stage_pl119_21()
    assert len(scores) == 115
    assert {s.calibration_relationship for s in scores} == {CR.HELD_OUT}
    assert {s.reform.baseline["policy"] for s in scores} == {
        "cbo_january_2025_baseline"
    }
    assert {s.conditions["baseline_policy"] for s in scores} == {
        "cbo_january_2025_baseline"
    }
    windows = Counter(
        (s.period_start, s.period_end, s.conditions["window_kind"]) for s in scores
    )
    assert windows == {
        (2026, 2034, "annual_average"): 104,
        (2025, 2034, "annual_average"): 5,
        (2028, 2034, "total"): 4,
        (2028, 2034, "annual_average"): 2,
    }
    assert all(s.period == s.period_end for s in scores)


def test_distribution_net_effects_and_signs():
    scores = ingest_cbo.stage_pl119_21()
    net = {
        (s.metric, s.conditions["income_group"]): s.value
        for s in scores
        if s.conditions.get("component") == "net_effect"
    }
    assert net[(Metric.AVG_CHANGE_AFTER_TAX_INCOME_USD, "Lowest")] == -1214
    assert net[(Metric.AVG_CHANGE_AFTER_TAX_INCOME_USD, "Highest")] == 13622
    assert net[(Metric.PCT_CHANGE_AFTER_TAX_INCOME, "Lowest")] == -3.1
    assert {
        s.value_kind for s in scores if s.metric is Metric.PCT_CHANGE_AFTER_TAX_INCOME
    } == {"percent"}


def test_snap_section_values():
    scores = ingest_cbo.stage_pl119_21()
    snap = {
        (
            s.reform.reform["policy"],
            s.metric,
            s.conditions.get("subgroup"),
            s.conditions.get("component"),
            s.conditions["program"],
        ): s.value
        for s in scores
        if "program" in s.conditions
    }
    assert (
        snap[
            (
                "pl119_21_snap_work_requirements",
                Metric.PARTICIPANT_COUNT_CHANGE,
                "total",
                None,
                "snap",
            )
        ]
        == -2_400_000
    )
    assert (
        snap[
            (
                "pl119_21_snap_sua_energy_assistance",
                Metric.AFFECTED_SHARE,
                "snap_households",
                None,
                "snap",
            )
        ]
        == 0.03
    )
    assert (
        snap[
            (
                "pl119_21_snap_state_matching_funds",
                Metric.BENEFIT_COST_CHANGE,
                None,
                "total",
                "snap",
            )
        ]
        == -41e9
    )
    assert (
        snap[
            (
                "pl119_21_snap_state_matching_funds",
                Metric.AFFECTED_COUNT,
                None,
                "state_responses",
                "child_nutrition",
            )
        ]
        == 96_000
    )


def test_tfp_cap_row_shares_the_january_2025_baseline():
    (tfp,) = [
        s for s in ingest_cbo.stage_scores() if s.reform.framework == "policy_ref"
    ]
    assert tfp.reform.baseline == ingest_cbo.CBO_JAN_2025
    assert tfp.conditions["baseline_policy"] == "cbo_january_2025_baseline"
