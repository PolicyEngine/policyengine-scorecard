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
        "scoring_method",
        "scope",
        "aggregate_level",
        "parent",
        "artifact",
        "baseline",
        "baseline_counterfactual",
        "baseline_locator",
        "source_column",
    }
    for r in rows:
        assert required <= set(r), sorted(required - set(r))
        assert r["source"] == "obr-policy-effects"
        assert r["country"] == "UK"
        assert r["status"] == "ok"
        assert isinstance(r["value"], float)


# The three macro quantities are semantically different and must never
# share one unit concept: a per-cent deviation in the LEVEL of real GDP,
# an effect on CPI inflation in PERCENTAGE POINTS, and an impact on
# POTENTIAL output as a per cent of GDP.
_EXPECTED_UNITS = {
    "gdp_level_effect": "percent_of_real_gdp",
    "cpi_inflation_effect": "percentage_points",
    "supply_side_impact": "percent_of_potential_gdp",
    "decisions_effect_on_borrowing": "gbp_nominal",
}


def test_units_match_metric(rows):
    for r in rows:
        assert r["unit_concept"] == _EXPECTED_UNITS[r["metric"]], r["metric"]
        if r["metric"] == "decisions_effect_on_borrowing":
            # sign convention carried verbatim, never normalised silently
            assert r["sign_convention"] == "as_published_positive_increases"
    # and the four are genuinely distinct labels, not aliases
    assert len(set(_EXPECTED_UNITS.values())) == 4


def test_basis_is_the_standard_axis_and_scoring_method_is_its_own(rows):
    """`basis` means forecast|outturn everywhere in this repo; a scoring
    method is not a basis and gets its own axis."""
    for r in rows:
        assert r["basis"] == "forecast"
        assert r["scoring_method"] in {"post_behavioural", "supply_side"}
        assert (r["scoring_method"] == "supply_side") == (
            r["metric"] == "supply_side_impact"
        )


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
    assert get(
        metric="supply_side_impact", program="tax_threshold_freeze"
    ) == pytest.approx(-0.25)


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


@pytest.fixture(scope="module")
def adapter():
    """The adapter module, loaded under a unique name (several sources/
    trees ship a module called "adapter")."""
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "obr_policy_effects_adapter",
        ROOT / "sources" / "obr-policy-effects" / "adapter.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_publication_provenance_is_per_event(rows, adapter):
    """Every row names the vendored artifact it was read from, and each
    artifact carries its OWN release date — one generic publications/
    URL stamped with the newest round's date misdates every older
    round's claims."""
    by_event = {}
    for r in rows:
        assert r["artifact"] in adapter.ARTIFACTS, r["artifact"]
        by_event.setdefault(r["fiscal_event"], set()).add(r["artifact"])
    # the four package rounds each read their own dated release
    # AS2023 is read from its own EFO release AND re-stated in BP10
    assert by_event["autumn_statement_2023"] == {
        "efo_november2023_chapter2.xlsx",
        "obr_briefing_paper_10_supply_side.xlsx",
    }
    assert by_event["autumn_budget_2024"] >= {"efo_october2024_chapter2.xlsx"}
    assert by_event["march_2026_efo"] == {"efo_march2026_annex_tables.xlsx"}
    dates = {f: a["date"] for f, a in adapter.ARTIFACTS.items()}
    assert dates["efo_november2023_chapter2.xlsx"] == "2023-11-22"
    assert dates["efo_march2024_chapter2.xlsx"] == "2024-03-06"
    assert dates["efo_october2024_chapter2.xlsx"] == "2024-10-30"
    assert dates["efo_november2025_chapter3.xlsx"] == "2025-11-26"
    # publication date, NOT the Wayback capture (2026-03-16)
    assert dates["efo_march2026_annex_tables.xlsx"] == "2026-03-03"
    assert len(set(dates.values())) == 5  # BP10 shares the Nov-2025 date


def test_every_row_carries_a_pre_measures_baseline(rows, adapter):
    """OBR scores against each round's PRE-MEASURES forecast — a named
    world per round, never the null current_law."""
    for r in rows:
        assert r["baseline"] == adapter._PRE_MEASURES[r["fiscal_event"]]
        assert r["baseline"] != "current_law"
        assert r["baseline_counterfactual"] in {
            "policy_parameters",
            "del_activity",
            "regulatory",
        }
        assert len(r["baseline_locator"]) > 40
    # six pre-measures rounds (SB2023..AB2025) plus March 2026's
    # since-the-November-2025-Budget world: seven distinct baselines
    assert len(set(r["baseline"] for r in rows)) == 7
    # March 2026's counterfactual is the November 2025 Budget forecast,
    # per Table B.1's own title — not a pre-measures world
    tb = next(r for r in rows if r["fiscal_event"] == "march_2026_efo")
    assert tb["baseline"] == "obr_november_2025_budget_forecast"
    # BP10 splits legislated-parameter counterfactuals from DEL and
    # regulatory activity baselines
    bp10 = [r for r in rows if r["metric"] == "supply_side_impact"]
    kinds = {r["variant"]: r["baseline_counterfactual"] for r in bp10}
    assert kinds == {
        "tax": "policy_parameters",
        "welfare": "policy_parameters",
        "del": "del_activity",
        "regulation": "regulatory",
    }
    wca = next(r for r in bp10 if r["program"] == "wca_reversal")
    assert "WCA-ADJUSTED" in wca["baseline_locator"]


@pytest.mark.skipif(not RAW.exists(), reason="raw workbooks not present")
def test_build_reconciles_every_source_cell(tmp_path, monkeypatch, adapter):
    """272 numeric cells read = 266 claims + 6 deliberately dropped memo
    cells. The memo line is a TALLIED drop, not a silent skip."""
    monkeypatch.setattr(adapter, "OUT_DIR", tmp_path)
    rows, counts, rec = adapter.build()
    assert rec["source_cells_read"] == 272
    assert rec["claims"] == 266 == len(rows)
    assert rec["deliberate_drops"] == 6
    assert len(rec["drops"]) == 1
    drop = rec["drops"][0]
    assert drop["slug"] == "memo_current_budget"
    assert drop["cells"] == 6
    assert "current budget" in drop["reason"]
    # and the four claim metrics still tie out
    assert counts["tb1_decisions"] == 60


@pytest.mark.skipif(not RAW.exists(), reason="raw workbooks not present")
def test_unregistered_labels_raise(monkeypatch, adapter, tmp_path):
    """The identity vocabularies are CLOSED: a re-labelled workbook
    fails loudly instead of minting a claim under an unseen slug."""
    monkeypatch.setattr(adapter, "OUT_DIR", tmp_path)

    series = dict(adapter._SERIES)
    series[("autumn_statement_2023", "C2.A")] = {"Demand": "demand"}
    monkeypatch.setattr(adapter, "_SERIES", series)
    with pytest.raises(RuntimeError, match="unregistered C2.A series label"):
        adapter.build()
    monkeypatch.undo()
    monkeypatch.setattr(adapter, "OUT_DIR", tmp_path)

    monkeypatch.setattr(adapter, "_BP10_MEASURES", {"Universal Support": "us"})
    with pytest.raises(RuntimeError, match="unregistered BP10 T2.1 measure"):
        adapter.build()


@pytest.mark.skipif(not RAW.exists(), reason="raw workbooks not present")
def test_unclassified_tb1_value_line_raises(monkeypatch, adapter, tmp_path):
    """A value-bearing TB.1 line that is neither emitted nor a declared
    drop is an error — the failure mode the memo row slipped through."""
    monkeypatch.setattr(adapter, "OUT_DIR", tmp_path)
    monkeypatch.setattr(adapter, "TB1_DROPS", [])
    with pytest.raises(RuntimeError, match="unclassified value line"):
        adapter.build()
