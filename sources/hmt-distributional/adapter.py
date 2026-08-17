"""Adapter: HMT "Impact on households" (Budget 2025) -> verified structure.

Input:  raw/Impact_on_households.pdf (Budget 2025 supporting document,
        published 2025-11-26, fetched from gov.uk — see raw/README.md)
        ../../data/uk/hmt_da_packages.yaml (the package registry this
        adapter verifies against the document)
Output: data/externals/hmt-distributional-meta.json — the verified
        document structure: figure inventory, package composition counts,
        and the value-availability statement.

THIS ADAPTER EMITS NO VALUE CLAIMS, deliberately. HMT publishes the
decile impacts of Figures 1.A-1.C as unlabeled chart bars in a PDF; no
spreadsheet or chart-data file exists (the Budget 2025 supporting
documents carry XLSX only for the costings tables 4.1/4.2). The text
layer carries figure titles, axis ticks, the policy scope lists and the
methodology — those are verifiable, and this adapter verifies them:

  - the raw PDF's SHA-256 matches the registry entry (a silently swapped
    or re-fetched file fails loudly)
  - every figure the registry advertises appears in the document
  - every package component title in the registry is verbatim-anchored in
    the document's in-scope list (normalized for the PDF text layer's
    line breaks and typographic quotes), so the registry cannot drift
    from the publication it claims to describe

Per-decile external values enter this lane only if HMT releases data
tables or a documented chart digitization lands with per-bar provenance.
Requires pypdf and pyyaml (like ukmod-stats requires pypdf); run:
    uv run --with pypdf --with pyyaml python sources/hmt-distributional/adapter.py
"""

import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
RAW = HERE / "raw" / "Impact_on_households.pdf"
REGISTRY = ROOT / "data" / "uk" / "hmt_da_packages.yaml"
OUT_DIR = ROOT / "data" / "externals"

EXPECTED_PAGES = 20
FIGURE_TITLES = {
    "1.A": "Impact of decisions from Autumn Budget 2024",
    "1.B": "in cash terms",
    "1.C": "Overall level of public spending received",
}
COMPUTABILITY = {"expressible", "partial", "not_expressible"}


def normalize(text):
    """Collapse the PDF text layer's line breaks, repeated whitespace and
    typographic quotes/dashes so verbatim registry titles anchor."""
    text = text.replace("’", "'").replace("‘", "'")
    text = text.replace("–", "-").replace("—", "-")
    # PDF line breaks split hyphenated tokens ("non- standard", "2026- 27");
    # closing the gap after a hyphen is safe here because registry titles
    # carry no hyphen-space sequences.
    text = re.sub(r"-\s+", "-", text)
    return re.sub(r"\s+", " ", text).strip()


def load_registry():
    import yaml

    reg = yaml.safe_load(REGISTRY.read_text())
    for pkg in reg["packages"]:
        for comp in pkg["components"]:
            assert comp["computability"] in COMPUTABILITY, comp["title"]
            if comp["computability"] == "partial":
                assert comp.get("missing"), f"partial without missing: {comp['title']}"
            if comp["computability"] == "not_expressible":
                assert comp.get("why"), f"not_expressible without why: {comp['title']}"
    return reg


def document_text():
    from pypdf import PdfReader

    reader = PdfReader(RAW)
    if len(reader.pages) != EXPECTED_PAGES:
        raise ValueError(f"expected {EXPECTED_PAGES} pages, got {len(reader.pages)}")
    return normalize(" ".join(p.extract_text() for p in reader.pages))


def run():
    reg = load_registry()
    pkg = next(
        p
        for p in reg["packages"]
        if p["package_key"] == "budget_2025__impact_on_households"
    )

    sha = hashlib.sha256(RAW.read_bytes()).hexdigest()
    if sha != pkg["sha256"]:
        raise ValueError(f"raw PDF sha256 {sha} != registry {pkg['sha256']}")

    text = document_text()

    for fig, anchor in FIGURE_TITLES.items():
        if normalize(anchor) not in text:
            raise ValueError(f"figure {fig} anchor not found: {anchor!r}")
    registry_figs = {c["figure"] for c in pkg["charts"]}
    if registry_figs != set(FIGURE_TITLES):
        raise ValueError(f"registry charts {registry_figs} != document figures")

    unanchored = []
    for comp in pkg["components"]:
        # Full verbatim titles span PDF line breaks; normalize() flattens
        # both sides, so the whole title must anchor.
        title = normalize(comp["title"])
        if title not in text:
            unanchored.append(comp["title"])
    if unanchored:
        raise ValueError(f"registry components not verbatim in document: {unanchored}")

    counts = {"by_computability": {}, "by_channel": {}}
    for comp in pkg["components"]:
        for key, field in (
            ("by_computability", "computability"),
            ("by_channel", "channel"),
        ):
            counts[key][comp[field]] = counts[key].get(comp[field], 0) + 1

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / "hmt-distributional-meta.json"
    out.write_text(
        json.dumps(
            {
                "source": "hmt-distributional",
                "package_key": pkg["package_key"],
                "raw_sha256": sha,
                "figures_verified": sorted(FIGURE_TITLES),
                "components": len(pkg["components"]),
                "component_counts": counts,
                "value_claims_emitted": 0,
                "value_availability": reg["value_availability_rule"],
            },
            indent=1,
        )
    )
    print(f"verified {len(pkg['components'])} components, 3 figures -> {out}")
    print(f"  computability: {counts['by_computability']}")
    print("  value claims emitted: 0 (chart-only publication; see module docstring)")


if __name__ == "__main__":
    run()
