"""Family ``census_stc``: PolicyEngine counterparts for the Census Annual
Survey of State Government Tax Collections, item T40 Individual Income
Taxes (sources/census-stc/, lane census-stc, issue #176).

STC publishes each State's individual income tax COLLECTIONS in its fiscal
year (cash, net of refunds). PolicyEngine computes a tax-year LIABILITY, so
the counterpart is constructed, never comparable: the weighted CY2024 total
of the State's own income tax variable, ``<st>_income_tax`` (tax units,
defined for that State only). The run also sums ``state_income_tax`` over
the State's tax units and records it beside the counterpart. The two
differ by design: the engine's sum adds Maryland's county income taxes and
New York City's income tax (local taxes, outside Census's State T40), and
``id_income_tax`` adds Idaho's $10 Permanent Building Fund tax
(``id_pbf``).

us-6.2.1 calibrates to the FY2023 T40 collections of 44 jurisdictions
(``census_stc.fy2023.individual_income_tax_collections.<st>.t40``); the
run records each target's value and its calibrated estimate from the
release's calibration_diagnostics.json beside the counterpart. The solve's
estimate is close to the runtime total but not identical to it (Idaho:
$2,719M against $2,774M), so it is recorded, not asserted.

One simulation (as served, CY2024) in its own child process
(``common.run_job``).

Usage (writes sources/census-stc/pe/<bundle_id>.json and the run log
pipeline/campaign_us/runs/census_stc__<bundle_id>.json):

    .venv-pe/bin/python pipeline/campaign_us/census_stc.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from common import REPO, log, now_utc, provenance, run_job

STEM = "census_stc"
YEAR = 2024
OUT_DIR = REPO / "sources" / "census-stc" / "pe"
RUN_ID = "census-stc-20261015"

# Jurisdictions with T40 collections in FY2023-FY2025 and an income tax
# variable in policyengine-us 2.2.1. Tennessee's residual Hall-tax
# collections have no engine variable (the tax ended with tax year 2020).
STATES = (
    "AL",
    "AZ",
    "AR",
    "CA",
    "CO",
    "CT",
    "DE",
    "DC",
    "GA",
    "HI",
    "ID",
    "IL",
    "IN",
    "IA",
    "KS",
    "KY",
    "LA",
    "ME",
    "MD",
    "MA",
    "MI",
    "MN",
    "MS",
    "MO",
    "MT",
    "NE",
    "NH",
    "NJ",
    "NM",
    "NY",
    "NC",
    "ND",
    "OH",
    "OK",
    "OR",
    "PA",
    "RI",
    "SC",
    "UT",
    "VT",
    "VA",
    "WA",
    "WV",
    "WI",
)

POLICYENGINE_VARIABLES = ["state_income_tax", "state_code_str", "is_tax_unit_head"] + [
    f"{s.lower()}_income_tax" for s in STATES
]

CALIBRATION_PATH = "releases/populace-us-2024-spm-20260915/calibration_diagnostics.json"
CALIBRATION_REVISION = "populace-us-2024-spm-20260915"


def measures(sim) -> dict:
    """Per State: the weighted CY2024 total of ``<st>_income_tax`` (tax
    units) and of ``state_income_tax`` over the State's tax units, counted
    through their heads on the person MicroSeries (a household string does
    not map to tax units — the irs_eitc_participation convention)."""
    state = np.asarray(
        sim.calculate("state_code_str", YEAR, map_to="person").values
    ).astype(str)
    head = np.asarray(sim.calculate("is_tax_unit_head", YEAR).values).astype(bool)
    total = sim.calculate("state_income_tax", YEAR, map_to="person")
    out = {}
    for s in STATES:
        own = sim.calculate(f"{s.lower()}_income_tax", YEAR)
        out[f"own|{s}"] = own.sum()
        out[f"state_income_tax|{s}"] = total[head & (state == s)].sum()
    out["state_income_tax|US"] = total[head].sum()
    return out


JOB = {"label": f"census stc as served CY{YEAR}", "measure": f"{STEM}:measures"}


def _calibration_targets() -> dict:
    from huggingface_hub import hf_hub_download

    path = hf_hub_download(
        "policyengine/populace-us",
        CALIBRATION_PATH,
        repo_type="dataset",
        revision=CALIBRATION_REVISION,
    )
    prefix = "census_stc.fy2023.individual_income_tax_collections."
    out = {}
    for t in json.loads(Path(path).read_text())["targets"]:
        if t["name"].startswith(prefix):
            out[t["name"].split(".")[3].upper()] = {
                "target_name": t["target_name"],
                "target": t["target"],
                "final_estimate": t["final_estimate"],
            }
    return out


def run() -> tuple[dict, dict]:
    result = run_job(JOB)
    prov = provenance([result])
    values = result["values"]
    targets = _calibration_targets()
    geos = {}
    for s in STATES:
        own, masked = values[f"own|{s}"], values[f"state_income_tax|{s}"]
        # The State's own variable is the counterpart (App v3 links to it).
        # state_income_tax is recorded beside it, not asserted equal: the
        # two differ by design where a State variable carries more or less
        # than the generic sum (both totals are kept for the ingest).
        geos[s] = {
            "state_income_tax": own,
            "state_income_tax_variable_total": masked,
        }
        if s in targets:
            geos[s]["calibration"] = targets[s]
    missing = sorted(set(targets) - set(STATES))
    if missing:
        raise RuntimeError(f"calibration targets without a counterpart: {missing}")
    staged = {
        "family": STEM,
        "run_id": RUN_ID,
        "computed_at": now_utc(),
        "period": YEAR,
        "time_basis": "annual",
        "provenance": prov,
        "policyengine_variables": POLICYENGINE_VARIABLES,
        "pe_construction": (
            f"Weighted CY{YEAR} total of <st>_income_tax (tax units; the "
            "variable is defined for that State only) on the certified "
            "bundle: the State government's tax, as Census T40 counts it. "
            "state_income_tax summed over the State's tax units "
            "(state_code_str) is recorded beside it; it differs where the "
            "engine's sum adds local taxes (Maryland counties, New York "
            "City) or a State variable adds a fee (Idaho's $10 Permanent "
            "Building Fund tax, id_pbf). A tax-year liability, compared with "
            "fiscal-year collections."
        ),
        "national_state_income_tax": values["state_income_tax|US"],
        "calibration_source": {
            "path": CALIBRATION_PATH,
            "revision": CALIBRATION_REVISION,
        },
        "geographies": geos,
    }
    meta = {
        "family": STEM,
        "provenance": prov,
        "jobs": [{k: v for k, v in result.items() if k != "values"}],
        "values": values,
    }
    return staged, meta


def main() -> None:
    staged, meta = run()
    tag = staged["provenance"]["bundle_id"] or "unknown"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"{tag}.json"
    out.write_text(json.dumps(staged, indent=1) + "\n")
    runs = HERE / "runs"
    runs.mkdir(exist_ok=True)
    (runs / f"{STEM}__{tag}.json").write_text(json.dumps(meta, indent=1) + "\n")
    log(
        f"wrote {out}: {len(staged['geographies'])} jurisdictions, national "
        f"state_income_tax {staged['national_state_income_tax'] / 1e9:,.1f}B"
    )


if __name__ == "__main__":
    main()
