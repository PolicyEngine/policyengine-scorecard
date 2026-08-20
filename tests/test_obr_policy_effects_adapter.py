"""Pins for the obr-policy-effects harvest (#55, step 1: external side).

The committed data/externals/obr-policy-effects.json is what downstream
consumes; these tests pin its shape and totals, plus (when the raw
workbooks are present) that a rebuild from the committed raw bytes
reproduces the committed output byte-for-byte and the published
hierarchy identities hold.
"""

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
EXTERNAL = ROOT / "data" / "externals" / "obr-policy-effects.json"
RAW = ROOT / "sources" / "obr-policy-effects" / "raw"

pytestmark = pytest.mark.skipif(
    not EXTERNAL.exists(), reason="no committed obr-policy-effects.json"
)


@pytest.fixture(scope="module")
def rows():
    return json.loads(EXTERNAL.read_text())


def test_row_count_and_block_totals(rows):
    assert len(rows) == 266
    by = {}
    for r in rows:
        by[(r["metric"], r["fiscal_event"])] = (
            by.get((r["metric"], r["fiscal_event"]), 0) + 1
        )
    assert by[("gdp_level_effect", "autumn_statement_2023")] == 30
    assert by[("gdp_level_effect", "spring_budget_2024")] == 20
    assert by[("gdp_level_effect", "autumn_budget_2024")] == 66  # components+measures
    assert by[("gdp_level_effect", "autumn_budget_2025")] == 35
    assert by[("cpi_inflation_effect", "autumn_budget_2025")] == 36
    assert by[("decisions_effect_on_borrowing", "march_2026_efo")] == 60
    assert sum(v for (m, _), v in by.items() if m == "supply_side_impact") == 19


def test_row_shape_is_closed(rows):
    required = {
        "source",
        "country",
        "program",
        "metric",
        "subgroup",
        "variant",
        "geography",
        "unit_concept",
        "period",
        "value",
        "status",
        "fiscal_event",
        "basis",
        "scope",
        "aggregate_level",
        "parent",
        "source_column",
    }
    for r in rows:
        assert required <= set(r), sorted(required - set(r))
        assert r["source"] == "obr-policy-effects"
        assert r["country"] == "UK"
        assert r["status"] == "ok"
        assert isinstance(r["value"], float)


def test_units_match_metric(rows):
    for r in rows:
        if r["metric"] == "decisions_effect_on_borrowing":
            assert r["unit_concept"] == "gbp_nominal"
            # sign convention carried verbatim, never normalised silently
            assert r["sign_convention"] == "as_published_positive_increases"
        else:
            assert r["unit_concept"] == "percent"


def test_spot_values_trace_to_published_cells(rows):
    def get(**kw):
        hits = [r for r in rows if all(r[k] == v for k, v in kw.items())]
        assert len(hits) == 1, (kw, len(hits))
        return hits[0]["value"]

    # AS2023 C2.A: NICs cut supply effect on real GDP, 2028-29 (per cent)
    assert get(
        fiscal_event="autumn_statement_2023",
        metric="gdp_level_effect",
        subgroup="supply_nics_cut",
        period="2028-29",
    ) == pytest.approx(0.16741543499136508)
    # Briefing paper T2.1: the same measure's supply-side scoring —
    # published identical to the AS2023 chart's terminal-year value
    assert get(
        metric="supply_side_impact",
        program="employee_nics_cut",
        fiscal_event="autumn_statement_2023",
    ) == pytest.approx(0.16741543499136508)
    # AB2024 C2.B employer NICs, 2029-30 — also BP10's AB2024 entry
    assert get(
        fiscal_event="autumn_budget_2024",
        metric="gdp_level_effect",
        subgroup="supply_employer_nics",
        period="2029-30",
    ) == pytest.approx(-0.087084388859310025)
    # TB.1 indirect effects 2028-29, GBP raw
    assert get(
        metric="decisions_effect_on_borrowing",
        program="indirect_effects",
        period="2028-29",
    ) == pytest.approx(-1785290340.7289479)
    # BP10: tax thresholds freeze is the one large negative labour entry
    assert get(metric="supply_side_impact", program="tax_thresholds") == pytest.approx(
        -0.25
    )


def test_tb1_hierarchy_reconciles(rows):
    """direct + indirect == total, and each subtotal equals its
    components, per period — the published nesting must survive parsing
    (double-count guard, same convention as the obr-welfare adapter)."""
    tb = [r for r in rows if r["metric"] == "decisions_effect_on_borrowing"]
    by = {(r["program"], r["period"]): r["value"] for r in tb}
    periods = {p for (_, p) in by}
    assert len(periods) == 6
    for p in periods:
        assert by[("direct_effects", p)] + by[("indirect_effects", p)] == (
            pytest.approx(by[("total_effect", p)], abs=1.0)
        )
        assert by[("spending_measures", p)] + by[("tax_measures", p)] == (
            pytest.approx(by[("direct_effects", p)], abs=1.0)
        )
        comps = [
            "additional_departmental_spending",
            "local_authority_support",
            "other_spending_measures",
        ]
        assert sum(by[(c, p)] for c in comps) == pytest.approx(
            by[("spending_measures", p)], abs=1.0
        )
        assert by[("pillar_2_reforms", p)] + by[("other_tax_measures", p)] == (
            pytest.approx(by[("tax_measures", p)], abs=1.0)
        )


def test_parents_exist_and_totals_have_none(rows):
    programs = {r["program"] for r in rows}
    for r in rows:
        if r["aggregate_level"] == "total":
            assert r["parent"] is None
        if r["parent"] is not None and r["metric"] == "decisions_effect_on_borrowing":
            assert r["parent"] in programs


@pytest.mark.skipif(not RAW.exists(), reason="raw workbooks not present")
def test_rebuild_is_byte_stable(tmp_path, monkeypatch):
    """Re-running the adapter against the committed raw bytes must
    reproduce the committed JSON exactly (includes the sha256 gate on
    every raw file)."""
    # unique module name: several sources/ trees ship a module called
    # "adapter", and a plain import would hit whichever loaded first
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "obr_policy_effects_adapter",
        ROOT / "sources" / "obr-policy-effects" / "adapter.py",
    )
    adapter = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(adapter)
    monkeypatch.setattr(adapter, "OUT_DIR", tmp_path)
    adapter.build()
    assert (tmp_path / "obr-policy-effects.json").read_text() == EXTERNAL.read_text()
