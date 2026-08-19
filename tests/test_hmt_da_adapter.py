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
    yaml = pytest.importorskip("yaml")
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


def test_document_anchoring_in_ci_when_pypdf_available():
    """The lane's strongest honesty guarantee — every registry title and
    figure anchor is verbatim in the real PDF — enforced in any test env
    with pypdf+pyyaml rather than only on a manual adapter run. Skips
    (like the yaml-gated schema test) where CI's bare env lacks them;
    the adapter's own run() remains the local backstop."""
    pytest.importorskip("pypdf")
    pytest.importorskip("yaml")
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
