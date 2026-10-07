"""Family ``irs_eitc_participation``: PolicyEngine counterparts for the
IRS/Census EITC participation rates (sources/irs-eitc-participation/, lane
nta-eitc).

IRS publishes, per State and tax year, "the percentage of eligible
taxpayers who receive an EITC payment (number receiving an EITC
payment/Number eligible for EITC)", with eligibility modeled on ACS (CPS
for the national headline) and receipt read from IRS records. Eligible
taxpayers include non-filers. The PE counterpart, in tax units:

* participants — tax units with ``eitc > 0`` as served. In policyengine-us
  2.2.1 ``eitc`` = min(phased-in, max(0, maximum - reduction)) x
  ``takes_up_eitc`` x filer, where filer = required to file OR files
  voluntarily OR ``would_file_if_eligible_for_refundable_credit``.
* eligible — tax units with ``eitc > 0`` when ``takes_up_eitc`` and
  ``would_file_if_eligible_for_refundable_credit`` are forced True (the
  campaign's cpsp_ctc_2024 construction), i.e. every entitled unit,
  filer or not.

Two simulations, each in its own child process (``common.run_job``):
``forced`` (eligible) and ``baseline`` (participants). The baseline run
also rebuilds the entitlement from the formula's parts and splits the
entitled-but-not-paid units into "take-up flag off" and "does not file";
the parent requires its entitled count to equal the forced run's eligible
count (the toggle check), so the two worlds measure the same population.
On us-6.2.1 the filing flag is stored True for every unit, so as served
every non-participant is a take-up-flag-off unit; the run records it.
Tax units are counted through their heads (``is_tax_unit_head``) on the
person MicroSeries, because a household string does not map to tax units.
PE's period is calendar 2024; the IRS State series ends at TY2022.

Usage (writes sources/irs-eitc-participation/pe/<bundle_id>.json and the
run log pipeline/campaign_us/runs/irs_eitc_participation__<bundle_id>.json):

    .venv-pe/bin/python pipeline/campaign_us/irs_eitc_participation.py
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

STEM = "irs_eitc_participation"
YEAR = 2024
OUT_DIR = REPO / "sources" / "irs-eitc-participation" / "pe"
RUN_ID = "irs-eitc-participation-20261006"
FORCED = {
    "takes_up_eitc": {"value": True, "years": [YEAR]},
    "would_file_if_eligible_for_refundable_credit": {"value": True, "years": [YEAR]},
}
CHILD_BINS = ("0", "1", "2", "3+")

# The 50 States and DC — the IRS table rows.
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
    "eitc",
    "takes_up_eitc",
    "would_file_if_eligible_for_refundable_credit",
    "eitc_eligible",
    "eitc_maximum",
    "eitc_phased_in",
    "eitc_reduction",
    "eitc_child_count",
    "is_tax_unit_head",
    "state_code_str",
]


def _person(sim, var: str) -> np.ndarray:
    """A tax-unit variable projected onto its members."""
    return np.asarray(sim.calculate(var, YEAR, map_to="person").values)


def measures(sim, world: str) -> dict:
    """Weighted tax-unit counts by geography (and, nationally, by
    qualifying children): units with eitc > 0, and in the baseline the
    entitlement rebuilt from the formula's parts and its split."""
    state = np.asarray(
        sim.calculate("state_code_str", YEAR, map_to="person").values
    ).astype(str)
    extra = sorted(set(state) - set(STATES))
    missing = sorted(set(STATES) - set(state))
    if extra or missing:
        raise RuntimeError(f"state coverage: extra {extra}, missing {missing}")
    ones = sim.calculate("age", YEAR) >= -1  # person MicroSeries of True
    head = np.asarray(sim.calculate("is_tax_unit_head", YEAR).values).astype(bool)
    paid = _person(sim, "eitc") > 0
    children = _person(sim, "eitc_child_count")
    bins = {
        "0": children == 0,
        "1": children == 1,
        "2": children == 2,
        "3+": children >= 3,
    }
    geos = {"US": np.ones(len(state), dtype=bool)}
    geos.update({s: state == s for s in STATES})
    out = {
        "flag_mean|takes_up_eitc": float(_person(sim, "takes_up_eitc")[head].mean()),
        "flag_mean|would_file": float(
            _person(sim, "would_file_if_eligible_for_refundable_credit")[head].mean()
        ),
    }
    masks = {"paid": paid}
    if world == "baseline":
        limitation = np.maximum(
            0, _person(sim, "eitc_maximum") - _person(sim, "eitc_reduction")
        )
        entitled = (_person(sim, "eitc_eligible") > 0) & (
            np.minimum(_person(sim, "eitc_phased_in"), limitation) > 0
        )
        if (paid & ~entitled).any():
            raise RuntimeError("eitc > 0 for a unit with no entitlement")
        flag = _person(sim, "takes_up_eitc") > 0
        masks.update(
            {
                "entitled": entitled,
                "entitled_flag_off": entitled & ~flag,
                "entitled_flag_on_not_paid": entitled & flag & ~paid,
            }
        )
    for name, m in masks.items():
        for g, gm in geos.items():
            out[f"{name}|{g}"] = ones[m & head & gm].sum()
        for b, bm in bins.items():
            out[f"{name}|US|children_{b}"] = ones[m & head & bm].sum()
    return out


JOBS = {
    "forced": {
        "label": f"irs eitc forced take-up and filing CY{YEAR}",
        "measure": f"{STEM}:measures",
        "measure_args": {"world": "forced"},
        "inputs": FORCED,
    },
    "baseline": {
        "label": f"irs eitc baseline CY{YEAR}",
        "measure": f"{STEM}:measures",
        "measure_args": {"world": "baseline"},
    },
}


def run() -> tuple[dict, dict]:
    results = {name: run_job(job) for name, job in JOBS.items()}
    prov = provenance(list(results.values()))
    forced, base = results["forced"]["values"], results["baseline"]["values"]
    # Toggle check: both inputs read back all-True in the forced world, and
    # the forced world's eligible count equals the baseline entitlement
    # rebuilt from the formula's parts (same population, two routes).
    for flag in ("takes_up_eitc", "would_file"):
        if forced[f"flag_mean|{flag}"] != 1.0:
            raise RuntimeError(f"{flag} not forced: {forced[f'flag_mean|{flag}']}")
    # The take-up flag must bind as served, or the two worlds are one. The
    # filing flag need not: us-6.2.1 stores it True for every unit, so as
    # served no entitled unit is blocked by not filing (recorded, below).
    if not 0.0 < base["flag_mean|takes_up_eitc"] < 1.0:
        raise RuntimeError("takes_up_eitc does not vary in the baseline")
    gap = abs(forced["paid|US"] / base["entitled|US"] - 1)
    if gap > 1e-6:
        raise RuntimeError(f"forced eligible != rebuilt entitlement ({gap:.2e})")
    geos = {}
    for geo in ["US", *STATES]:
        row = {
            "eligible_tax_units": forced[f"paid|{geo}"],
            "participants": base[f"paid|{geo}"],
            "entitled_flag_off": base[f"entitled_flag_off|{geo}"],
            "entitled_flag_on_not_paid": base[f"entitled_flag_on_not_paid|{geo}"],
        }
        row["participation_rate"] = row["participants"] / row["eligible_tax_units"]
        geos[geo] = row
    by_children = {
        b: {
            "eligible_tax_units": forced[f"paid|US|children_{b}"],
            "participants": base[f"paid|US|children_{b}"],
            "participation_rate": base[f"paid|US|children_{b}"]
            / forced[f"paid|US|children_{b}"],
            "entitled_flag_off": base[f"entitled_flag_off|US|children_{b}"],
        }
        for b in CHILD_BINS
    }
    staged = {
        "family": STEM,
        "run_id": RUN_ID,
        "computed_at": now_utc(),
        "period": YEAR,
        "time_basis": "annual",
        "provenance": prov,
        "policyengine_variables": POLICYENGINE_VARIABLES,
        "pe_construction": (
            f"CY{YEAR} tax units, counted through is_tax_unit_head: "
            "participants = units with eitc > 0 as served; eligible_tax_units "
            "= units with eitc > 0 when takes_up_eitc and "
            "would_file_if_eligible_for_refundable_credit are forced True "
            "(filers and non-filers); participation_rate = participants / "
            "eligible_tax_units. entitled_flag_off / entitled_flag_on_not_paid "
            "split the entitled non-participants as served (take-up flag off; "
            "flag on but not a filer)."
        ),
        "toggle_check": {
            "forced": {
                k: forced[f"flag_mean|{k}"] for k in ("takes_up_eitc", "would_file")
            },
            "baseline": {
                k: base[f"flag_mean|{k}"] for k in ("takes_up_eitc", "would_file")
            },
            "forced_eligible_vs_rebuilt_entitlement_gap": gap,
        },
        "geographies": geos,
        "national_by_children": by_children,
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
        f"({us['participants']:,.0f} / {us['eligible_tax_units']:,.0f})"
    )


if __name__ == "__main__":
    main()
