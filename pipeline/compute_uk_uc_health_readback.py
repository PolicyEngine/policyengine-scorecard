"""PolicyEngine-UK's new-claimant share of the UC health element, read from
the parameter tree (lane dwp-uc-health, issue #87).

No simulation and no dataset. ``new_claimant_share`` is the share of
benefit units with the LCWRA element that PolicyEngine-UK pays the
new-claimant (lower) rate, by tax year; the model assigns it by a seeded
draw when the data do not carry the status. Each year's value is read at
1 June (inside the tax year from April), with the parameter's own
description and reference titles.

Usage (any interpreter with policyengine-uk installed; writes
sources/dwp-uc-health/pe/uk-<version>.json):

    <venv>/bin/python pipeline/compute_uk_uc_health_readback.py
"""

from __future__ import annotations

import importlib.metadata as md
import json
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT_DIR = REPO / "sources" / "dwp-uc-health" / "pe"
SHARE = "gov.dwp.universal_credit.rebalancing.new_claimant_share"
YEARS = range(2026, 2030)


def read() -> dict:
    from policyengine_uk.system import system

    node = system.parameters
    for part in SHARE.split("."):
        node = getattr(node, part)
    references = node.metadata.get("reference") or []
    return {
        "path": SHARE,
        "values": {str(y): float(node(f"{y}-06-01")) for y in YEARS},
        "description": " ".join(node.description.split()),
        "references": [r.get("title", "") for r in references],
    }


def main() -> None:
    version = md.version("policyengine-uk")
    computed_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    staged = {
        "family": "uk_uc_health_readback",
        "run_id": f"uk-uc-health-readback-{version}-{computed_at[:10]}",
        "computed_at": computed_at,
        "provenance": {
            "engine": "policyengine-uk",
            "engine_version": version,
            "policyengine_core_version": md.version("policyengine-core"),
            "data_bundle": "parameter-tree",
            "bundle_id": f"uk-{version}",
        },
        "pe_construction": (
            f"Parameter-tree read-back on policyengine-uk {version}, no "
            f"simulation: {SHARE} read at 1 June of each tax year."
        ),
        "new_claimant_share": read(),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"uk-{version}.json"
    out.write_text(json.dumps(staged, indent=1) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
