"""Structure tests for the HMT distributional-analysis lane (#61).

The lane deliberately emits no value claims (HMT publishes decile impacts
as unlabeled chart bars in a PDF; see sources/hmt-distributional/raw/
README.md). What is pinned here is everything checkable without pypdf:
the vendored raw file's identity, the committed meta artifact's honesty
about that, and — when pyyaml is importable — the registry's schema
contract. Full document anchoring (every registry title verbatim in the
PDF) runs in the adapter itself, which needs pypdf.
"""

import ast
import hashlib
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
LANE = ROOT / "sources" / "hmt-distributional"
RAW = LANE / "raw" / "Impact_on_households.pdf"
REGISTRY = ROOT / "data" / "uk" / "hmt_da_packages.yaml"
META = ROOT / "data" / "externals" / "hmt-distributional-meta.json"

RAW_SHA256 = "9f7e68f3e44349c8a6a4a89b9e1427cc23f1691771902b154ef67cadd33480ea"


def test_raw_file_is_the_fetched_publication():
    assert RAW.exists(), "vendored raw PDF missing"
    assert hashlib.sha256(RAW.read_bytes()).hexdigest() == RAW_SHA256


def test_lane_provenance_files_exist():
    assert (LANE / "raw" / "README.md").exists()
    source = json.loads((LANE / "source.json").read_text())
    assert source["id"] == "hmt-distributional"
    assert RAW_SHA256 not in source["url"]  # sha lives in README/registry
    assert any(u.endswith("Impact_on_households.pdf") for u in source["data_urls"])


def test_adapter_compiles_and_emits_no_value_rows_by_construction():
    src = (LANE / "adapter.py").read_text()
    ast.parse(src)
    # The no-values contract is stated and structural: the adapter has no
    # emit path for claim rows at all.
    assert "EMITS NO VALUE CLAIMS" in src
    assert "value_claims_emitted" in src


def test_meta_artifact_is_honest_about_values():
    meta = json.loads(META.read_text())
    assert meta["value_claims_emitted"] == 0
    assert meta["raw_sha256"] == RAW_SHA256
    assert meta["figures_verified"] == ["1.A", "1.B", "1.C"]
    assert meta["components"] == 30


def test_registry_schema():
    import yaml

    reg = yaml.safe_load(REGISTRY.read_text())
    assert reg["benchmark_class"] == "different_model"
    assert reg["value_availability_rule"]
    keys = [p["package_key"] for p in reg["packages"]]
    assert keys == ["budget_2025__impact_on_households"]
    pkg = reg["packages"][0]
    assert pkg["sha256"] == RAW_SHA256
    assert {c["figure"] for c in pkg["charts"]} == {"1.A", "1.B", "1.C"}
    assert len(pkg["components"]) == 30
    for comp in pkg["components"]:
        assert comp["computability"] in {"expressible", "partial", "not_expressible"}
        assert comp["channel"] in {"tax", "welfare", "benefits_in_kind_public_services"}
        if comp["computability"] == "partial":
            assert comp.get("missing"), comp["title"]
        if comp["computability"] == "not_expressible":
            assert comp.get("why"), comp["title"]
        # No invented executable specs: reform parameters live only in the
        # measure registry a component may point at, never here.
        assert "parameters" not in comp and "reform" not in comp
    triage = {c["computability"] for c in pkg["components"]}
    assert triage == {"expressible", "partial", "not_expressible"}


def _load_adapter():
    import importlib.util

    spec = importlib.util.spec_from_file_location("hmt_da_adapter", LANE / "adapter.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_document_anchoring_runs_in_ci():
    """The lane's strongest honesty guarantee — every registry title and
    figure anchor is verbatim in the real PDF. It is NOT optional: CI now
    installs pypdf and pyyaml, so this runs there. It used to
    `importorskip` both while CI installed only pytest, which meant the
    advertised gate never actually ran."""
    adapter = _load_adapter()

    text = adapter.document_text()  # also enforces the 20-page identity
    reg = adapter.load_registry()
    pkg = next(
        p
        for p in reg["packages"]
        if p["package_key"] == "budget_2025__impact_on_households"
    )
    for fig, anchor in adapter.FIGURE_TITLES.items():
        assert adapter.normalize(anchor) in text, f"figure {fig} anchor missing"
    assert {c["figure"] for c in pkg["charts"]} == set(adapter.FIGURE_TITLES)
    unanchored = [
        c["title"]
        for c in pkg["components"]
        if adapter.normalize(c["title"]) not in text
    ]
    assert not unanchored, f"registry titles not verbatim in document: {unanchored}"


# --- the six review findings ------------------------------------------------


def test_chart_omissions_are_exactly_tallied():
    """ "No values emitted" is only honest if it says how many there were.
    3 figures x 11 income groups x 4 series = 132 marks on the page."""
    meta = json.loads(META.read_text())
    cells = meta["chart_cells"]
    assert cells["source_marks"] == 132
    assert cells["emitted"] == 0
    assert cells["chart_not_digitized"] == 132
    assert cells["by_figure"] == {"1.A": 44, "1.B": 44, "1.C": 44}
    assert len(cells["cells"]) == 132
    assert {c["disposition"] for c in cells["cells"]} == {"chart_not_digitized"}
    # every (figure, group, series) is present exactly once
    keys = {(c["figure"], c["income_group"], c["series"]) for c in cells["cells"]}
    assert len(keys) == 132
    # ...and the 30 policy components still reconcile (3+9+18 = 16+9+5)
    comp = meta["component_counts"]
    assert sum(comp["by_computability"].values()) == 30
    assert sum(comp["by_channel"].values()) == 30


def test_decile_identity_is_closed_data_not_prose():
    from scorecard_db.uk_aliases import DISTINCT, canon

    meta = json.loads(META.read_text())
    ident = meta["income_identity"]
    assert ident["housing_costs"] == "bhc"
    assert ident["equivalisation"] == "modified_oecd"
    assert ident["income_groups"] == [f"decile_{i}" for i in range(1, 11)] + [
        "all_households"
    ]
    for group in ident["income_groups"]:
        assert canon("hmt_distributional", "income_group", group) == group
    with pytest.raises(ValueError, match="unregistered income_group"):
        canon("hmt_distributional", "income_group", "bottom fifth")
    # HMT deciles are never aliased to UKMOD quintiles
    assert ("hmt_distributional:decile_1", "ukmod:q1") in DISTINCT
    assert ("hmt_distributional:decile_10", "ukmod:q5") in DISTINCT


def test_baseline_identity_is_per_figure_and_registered():
    """1.A/1.B are changes vs the no-policy world; 1.C is a post-policy
    level. One prose counterfactual over all three would let a future row
    default to current_law."""
    from scorecard_db.baselines import BASELINES

    meta = json.loads(META.read_text())
    assert meta["chart_baselines"] == {
        "1.A": {"kind": "change", "baseline": "hmt_no_policy_change_from_ab2024"},
        "1.B": {"kind": "change", "baseline": "hmt_no_policy_change_from_ab2024"},
        "1.C": {"kind": "level", "baseline": "current_law"},
    }
    registered = {d["policy"] for d, *_ in BASELINES}
    assert "hmt_no_policy_change_from_ab2024" in registered


def test_an_unregistered_chart_baseline_raises(tmp_path, monkeypatch):
    adapter = _load_adapter()
    reg = adapter.load_registry()
    pkg = reg["packages"][0]
    pkg["charts"][0]["baseline"] = "whatever_hmt_meant"
    monkeypatch.setattr(adapter, "load_registry", lambda: reg)
    monkeypatch.setattr(adapter, "OUT_DIR", tmp_path)
    with pytest.raises(ValueError, match="unregistered baseline"):
        adapter.run()


def test_the_lane_survives_a_fresh_build(tmp_path):
    """The blocking finding: the adapter wrote standalone metadata and
    nothing registered in build_db, so a CI-built DB held no trace of
    HMT — not even a zero-claim lane."""
    import sqlite3

    from scorecard_db.db import ScorecardDB
    from scorecard_db.ingest_hmt_distributional import LANE_ID, ingest

    db_path = tmp_path / "db.sqlite"
    ScorecardDB(db_path).close()
    summary = ingest(db_path)
    assert summary["claims"] == 0
    assert summary["source_marks"] == 132
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    lane = conn.execute("SELECT * FROM lanes WHERE lane = ?", (LANE_ID,)).fetchone()
    conn.close()
    assert lane is not None
    assert lane["stage"] == "cataloged"
    assert "132 source marks = 0 emitted + 132 chart_not_digitized" in lane["detail"]


def test_build_db_registers_the_hmt_step():
    import inspect

    from scorecard_db import build_db

    src = inspect.getsource(build_db)
    assert "ingest_hmt_distributional.ingest" in src


def test_the_lane_reaches_mission_control():
    lanes = json.loads((ROOT / "data" / "lanes.json").read_text())["lanes"]
    entry = next(lane for lane in lanes if lane["id"] == "hmt-distributional")
    assert entry["country"] == "UK"
    assert entry["stage"] == "cataloged"


def test_held_out_relationship_is_registered_with_evidence():
    """The resolver failed closed on the unknown source, which was right
    but temporary: the entry is made before any numeric row can land."""
    from scorecard_db.models import CalibrationRelationship, Metric
    from scorecard_db.relationships import uk_relationship

    rel, evidence = uk_relationship(
        "hmt_distributional", Metric.PCT_CHANGE_AFTER_TAX_INCOME
    )
    assert rel is CalibrationRelationship.HELD_OUT
    assert "no pe-uk-data target" in evidence
    assert "2026-08-19" in evidence  # the pin the surfaces were read at


def test_engine_defect_guidance_points_at_the_citable_gate():
    source = json.loads((LANE / "source.json").read_text())
    text = source["diagnosis_upstream"]
    assert "action_link" in text
    assert "citable-known-issue gate" in text


def test_the_meta_artifact_ends_with_a_newline():
    """The no-drift build rewrites this file; without the trailing newline
    the committed copy and a rebuild differ and the tree dirties."""
    assert META.read_text().endswith("}\n")
