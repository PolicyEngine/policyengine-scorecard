"""Family ``fns_snap_rates``: PolicyEngine counterparts for the FNS state
SNAP participation rates (sources/fns-snap-rates/, lane fns-snap-rates).

FNS (Cunnyngham 2025, Mathematica) publishes, per State and fiscal year,
the share of people eligible for SNAP "under Federal income and resource
rules" who participate, in an average month. Two concept choices follow
from the report's Appendix A (equations 1-3) and are built here rather
than approximated:

* Federal rules, not BBCE. FNS excludes "participants who were eligible
  through State-expanded categorical eligibility policies but would not
  meet federal SNAP income and resource criteria" from the numerator, and
  never counts such people as eligible. In policyengine-us 2.2.1 BBCE
  enters SNAP only through ``is_tanf_non_cash_eligible`` in the
  ``gov.usda.snap.categorical_eligibility`` list
  (``meets_snap_categorical_eligibility``); no benefit formula reads
  categorical status. So the federal-rules world is the baseline with
  ``is_tanf_non_cash_eligible`` forced False for all twelve months:
  ``is_snap_eligible`` there is (net & gross & asset tests) OR traditional
  categorical eligibility (all-SSI unit, TANF cash), and a federally
  eligible unit's ``snap`` is the same as in the baseline.
* Average month, persons. Counts are weighted persons in eligible
  (participating) SPM units who are not ``is_snap_excluded_member``,
  computed for each month of the calendar year and averaged; the rate is
  average participants / average eligible people, as FNS divides average
  monthly counts.

Two simulations, each in its own child process (``common.run_job``):
``federal`` (the counterpart) and ``baseline`` (as served, BBCE included)
for the diagnostic BBCE-only share and the all-participant count. PE's
period is calendar 2024, the certified data year; FNS's latest year is
FY 2022 — the ingest annotates the vintage, this module does not bridge
it.

Usage (writes sources/fns-snap-rates/pe/<bundle_id>.json and the run log
pipeline/campaign_us/runs/fns_snap_rates__<bundle_id>.json):

    .venv-pe/bin/python pipeline/campaign_us/fns_snap_rates.py
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

STEM = "fns_snap_rates"
YEAR = 2024
MONTHS = [f"{YEAR}-{m:02d}" for m in range(1, 13)]
BBCE_INPUT = "is_tanf_non_cash_eligible"
OUT_DIR = REPO / "sources" / "fns-snap-rates" / "pe"
RUN_ID = "fns-snap-rates-20261006"

# The 50 States and DC — the FNS table rows. A dataset state outside this
# set (or one of these missing) fails the measure.
STATES = (
    "AL",
    "AK",
    "AZ",
    "AR",
    "CA",
    "CO",
    "CT",
    "DE",
    "DC",
    "FL",
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
    "NV",
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
    "SD",
    "TN",
    "TX",
    "UT",
    "VT",
    "VA",
    "WA",
    "WV",
    "WI",
    "WY",
)

POLICYENGINE_VARIABLES = [
    "is_snap_eligible",
    "snap",
    "is_snap_excluded_member",
    BBCE_INPUT,
    "takes_up_snap_if_eligible",
    "state_code_str",
]


def measures(sim) -> dict:
    """Per month and geography: weighted eligible and participating
    persons (non-excluded members of eligible / participating SPM units),
    eligible persons whose unit carries the take-up flag (the saturation
    diagnostic), participating SPM units, and the post-set mean of the
    BBCE input (the toggle check)."""
    state_ms = sim.calculate("state_code_str", YEAR, map_to="person")
    state = np.asarray(state_ms.values).astype(str)
    extra = sorted(set(state) - set(STATES))
    missing = sorted(set(STATES) - set(state))
    if extra or missing:
        raise RuntimeError(f"state coverage: extra {extra}, missing {missing}")
    ones = sim.calculate("age", YEAR) >= -1  # person MicroSeries of True
    geos = {"US": np.ones(len(state), dtype=bool)}
    geos.update({s: state == s for s in STATES})
    takes_up = (
        np.asarray(
            sim.calculate("takes_up_snap_if_eligible", YEAR, map_to="person").values
        )
        > 0
    )
    unit_ones = sim.calculate("spm_unit_id", YEAR) >= -1  # SPM-unit MicroSeries
    out = {}
    for month in MONTHS:
        member = ~np.asarray(
            sim.calculate("is_snap_excluded_member", month).values
        ).astype(bool)
        elig = (
            np.asarray(sim.calculate("is_snap_eligible", month, map_to="person").values)
            > 0
        )
        part = np.asarray(sim.calculate("snap", month, map_to="person").values) > 0
        if (part & ~elig).any():
            raise RuntimeError(f"{month}: snap > 0 in a unit that is not eligible")
        bbce = np.asarray(sim.calculate(BBCE_INPUT, month).values).astype(float)
        out[f"bbce_input_mean|{month}"] = float(bbce.mean())
        unit_part = np.asarray(sim.calculate("snap", month).values) > 0
        out[f"participating_units|{month}|US"] = unit_ones[unit_part].sum()
        for g, gm in geos.items():
            out[f"eligible|{month}|{g}"] = ones[elig & member & gm].sum()
            out[f"participants|{month}|{g}"] = ones[part & member & gm].sum()
            out[f"eligible_taking_up|{month}|{g}"] = ones[
                elig & member & takes_up & gm
            ].sum()
    return out


JOBS = {
    "federal": {
        "label": f"fns federal rules CY{YEAR}",
        "measure": f"{STEM}:measures",
        "inputs": {BBCE_INPUT: {"value": False, "years": [YEAR]}},
    },
    "baseline": {
        "label": f"fns baseline CY{YEAR}",
        "measure": f"{STEM}:measures",
    },
}


def _average(values: dict, kind: str, geo: str) -> float:
    return sum(values[f"{kind}|{m}|{geo}"] for m in MONTHS) / len(MONTHS)


def run() -> tuple[dict, dict]:
    results = {name: run_job(job) for name, job in JOBS.items()}
    prov = provenance(list(results.values()))
    fed, base = results["federal"]["values"], results["baseline"]["values"]
    # Toggle verification (binding rule): the forced input must read back
    # as all-False in the federal world and must bind somewhere in the
    # baseline, or the two worlds are the same world.
    fed_means = {m: fed[f"bbce_input_mean|{m}"] for m in MONTHS}
    base_means = {m: base[f"bbce_input_mean|{m}"] for m in MONTHS}
    if any(v != 0.0 for v in fed_means.values()):
        raise RuntimeError(f"BBCE input not forced off: {fed_means}")
    if not all(v > 0.0 for v in base_means.values()):
        raise RuntimeError(f"BBCE input never true in the baseline: {base_means}")
    geos = {}
    for geo in ["US", *STATES]:
        row = {
            "eligible_persons": _average(fed, "eligible", geo),
            "participants": _average(fed, "participants", geo),
            "baseline_eligible_persons": _average(base, "eligible", geo),
            "baseline_participants": _average(base, "participants", geo),
        }
        if row["eligible_persons"] > row["baseline_eligible_persons"] + 1e-6:
            raise RuntimeError(f"{geo}: federal-rules eligibility exceeds baseline")
        row["participation_rate"] = row["participants"] / row["eligible_persons"]
        # share of federally eligible people whose unit carries the take-up
        # flag: 1.0 means every eligible unit is set to take up (saturation)
        row["takeup_flag_share"] = (
            _average(fed, "eligible_taking_up", geo) / row["eligible_persons"]
        )
        geos[geo] = row
    # the grain check: participating SPM units (household grain, the
    # calibrated quantity) next to the persons counted in them
    geos["US"]["baseline_participating_spm_units"] = _average(
        base, "participating_units", "US"
    )
    staged = {
        "family": STEM,
        "run_id": RUN_ID,
        "computed_at": now_utc(),
        "period": YEAR,
        "time_basis": "average_month",
        "provenance": prov,
        "policyengine_variables": POLICYENGINE_VARIABLES,
        "pe_construction": (
            f"Average of the 12 months of CY{YEAR}: weighted persons who are not "
            "is_snap_excluded_member in SPM units with is_snap_eligible "
            "(eligible_persons) and with snap > 0 (participants), in the "
            f"federal-rules world ({BBCE_INPUT} forced False for every month, "
            "so BBCE-only units are neither eligible nor participants); "
            "participation_rate = participants / eligible_persons; "
            "takeup_flag_share = eligible_persons whose SPM unit has "
            "takes_up_snap_if_eligible / eligible_persons. baseline_* repeat "
            "the counts in the as-served world (BBCE included)."
        ),
        "toggle_check": {"federal": fed_means, "baseline": base_means},
        "geographies": geos,
    }
    meta = {
        "family": STEM,
        "provenance": prov,
        "jobs": [
            {k: v for k, v in r.items() if k != "values"} for r in results.values()
        ],
        "values": {name: r["values"] for name, r in results.items()},
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
    us = staged["geographies"]["US"]
    log(
        f"wrote {out}: US rate {us['participation_rate']:.4f} "
        f"({us['participants']:,.0f} / {us['eligible_persons']:,.0f})"
    )


if __name__ == "__main__":
    main()
