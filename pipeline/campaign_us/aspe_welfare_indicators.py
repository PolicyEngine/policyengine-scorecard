"""Family ``aspe_welfare_indicators``: PolicyEngine counterparts for ASPE's
Welfare Indicators "Indicator 4" — participation among the eligible —
(sources/aspe-welfare-indicators/, lane aspe-welfare-indicators).

ASPE (25th Report to Congress, April 2026) publishes three series:

* Table 10, TANF: families eligible for and receiving standard TANF
  benefits, TRIM3 (CPS ASEC), average month, through 2023.
* Table 11, SNAP: households eligible and participating under federal
  rules, average month of the fiscal year (FNS series), through FY 2022.
* Table 12, SSI: adult units eligible and participating — one-person units
  aged 65+, one-person disabled units, married-couple units — TRIM3,
  average month, through 2023. Children are excluded.

Constructions (CY2024, certified data; each in the staged file's
pe_construction):

* TANF — SPM units with ``tanf_if_takes_up`` > 0 (eligible) and ``tanf``
  > 0 (participating) over the YEAR. policyengine-us 2.2.1's 51 State TANF
  programs mix YEAR and MONTH periods (e.g. ca_tanf YEAR, tx_tanf MONTH),
  so an average-month count is not available: these are any-time-in-year
  counts. The ingest marks the counts concept_mismatch; the ratio is the
  comparable quantity.
* SSI — adults (18+) with ``ssi_if_takes_up`` > 0 (eligible for a payment)
  and ``ssi`` > 0, averaged over the 12 months; joint claims
  (``ssi_claim_is_joint``) are couple units (persons / 2); the rest are
  one-person units, aged if 65+, otherwise disabled.
* SNAP — SPM units with ``is_snap_eligible`` and with ``snap`` > 0 in the
  federal-rules world (``is_tanf_non_cash_eligible`` forced False, as in
  the fns_snap_rates family), averaged over the 12 months.

Two simulations in child processes (``common.run_job``): ``baseline``
(TANF, SSI) and ``federal`` (SNAP); the BBCE toggle is verified as in
fns_snap_rates.

Usage:
    .venv-pe/bin/python pipeline/campaign_us/aspe_welfare_indicators.py
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

STEM = "aspe_welfare_indicators"
YEAR = 2024
MONTHS = [f"{YEAR}-{m:02d}" for m in range(1, 13)]
BBCE_INPUT = "is_tanf_non_cash_eligible"
OUT_DIR = REPO / "sources" / "aspe-welfare-indicators" / "pe"
RUN_ID = "aspe-welfare-indicators-20261007"

POLICYENGINE_VARIABLES = [
    "tanf",
    "tanf_if_takes_up",
    "takes_up_tanf_if_eligible",
    "ssi",
    "ssi_if_takes_up",
    "ssi_claim_is_joint",
    "age",
    "is_snap_eligible",
    "snap",
    BBCE_INPUT,
]


def baseline_measures(sim) -> dict:
    """TANF (year) and SSI (average month) counts as served."""
    units = sim.calculate("spm_unit_id", YEAR) >= -1  # SPM-unit MicroSeries
    tanf_elig = np.asarray(sim.calculate("tanf_if_takes_up", YEAR).values) > 0
    tanf_paid = np.asarray(sim.calculate("tanf", YEAR).values) > 0
    if (tanf_paid & ~tanf_elig).any():
        raise RuntimeError("tanf > 0 in a unit with no entitlement")
    out = {
        "tanf_eligible_units": units[tanf_elig].sum(),
        "tanf_participating_units": units[tanf_paid].sum(),
        "tanf_flag_mean_eligible": float(
            np.asarray(sim.calculate("takes_up_tanf_if_eligible", YEAR).values)[
                tanf_elig
            ].mean()
        ),
    }
    ones = sim.calculate("age", YEAR) >= -1  # person MicroSeries
    age = np.asarray(sim.calculate("age", YEAR).values)
    adult = age >= 18
    joint = np.asarray(sim.calculate("ssi_claim_is_joint", YEAR).values).astype(bool)
    cats = {
        "aged": adult & ~joint & (age >= 65),
        "disabled": adult & ~joint & (age < 65),
        "couples": adult & joint,
    }
    for name in ("eligible", "participating"):
        for cat in cats:
            out[f"ssi_{name}_{cat}"] = 0.0
    for month in MONTHS:
        payable = np.asarray(sim.calculate("ssi_if_takes_up", month).values) > 0
        paid = np.asarray(sim.calculate("ssi", month).values) > 0
        if (paid & ~payable).any():
            raise RuntimeError(f"{month}: ssi > 0 for a person with no payment due")
        for cat, mask in cats.items():
            # couple units count two eligible adults each
            scale = 0.5 if cat == "couples" else 1.0
            out[f"ssi_eligible_{cat}"] += scale * ones[payable & mask].sum() / 12
            out[f"ssi_participating_{cat}"] += scale * ones[paid & mask].sum() / 12
    return out


def federal_snap_measures(sim) -> dict:
    """SNAP household (SPM-unit) counts, average month, federal rules."""
    units = sim.calculate("spm_unit_id", YEAR) >= -1
    out = {"eligible_units": 0.0, "participating_units": 0.0}
    for month in MONTHS:
        elig = np.asarray(sim.calculate("is_snap_eligible", month).values) > 0
        part = np.asarray(sim.calculate("snap", month).values) > 0
        if (part & ~elig).any():
            raise RuntimeError(f"{month}: snap > 0 in a unit that is not eligible")
        out["eligible_units"] += units[elig].sum() / 12
        out["participating_units"] += units[part].sum() / 12
        bbce = np.asarray(sim.calculate(BBCE_INPUT, month).values).astype(float)
        out[f"bbce_input_mean|{month}"] = float(bbce.mean())
    return out


JOBS = {
    "baseline": {
        "label": f"aspe baseline CY{YEAR}",
        "measure": f"{STEM}:baseline_measures",
    },
    "federal": {
        "label": f"aspe snap federal rules CY{YEAR}",
        "measure": f"{STEM}:federal_snap_measures",
        "inputs": {BBCE_INPUT: {"value": False, "years": [YEAR]}},
    },
}


def run() -> tuple[dict, dict]:
    results = {name: run_job(job) for name, job in JOBS.items()}
    prov = provenance(list(results.values()))
    base, fed = results["baseline"]["values"], results["federal"]["values"]
    toggle = {m: fed[f"bbce_input_mean|{m}"] for m in MONTHS}
    if any(v != 0.0 for v in toggle.values()):
        raise RuntimeError(f"BBCE input not forced off: {toggle}")
    series = {
        "tanf": {
            "eligible_count": base["tanf_eligible_units"],
            "participant_count": base["tanf_participating_units"],
            "participation_rate": base["tanf_participating_units"]
            / base["tanf_eligible_units"],
            "takeup_flag_mean_among_eligible": base["tanf_flag_mean_eligible"],
        },
        "snap": {
            "eligible_count": fed["eligible_units"],
            "participant_count": fed["participating_units"],
            "participation_rate": fed["participating_units"] / fed["eligible_units"],
        },
    }
    for cat in ("aged", "disabled", "couples"):
        e, p = base[f"ssi_eligible_{cat}"], base[f"ssi_participating_{cat}"]
        series[f"ssi_{cat}"] = {
            "eligible_count": e,
            "participant_count": p,
            "participation_rate": p / e,
        }
    staged = {
        "family": STEM,
        "run_id": RUN_ID,
        "computed_at": now_utc(),
        "period": YEAR,
        "provenance": prov,
        "policyengine_variables": POLICYENGINE_VARIABLES,
        "pe_construction": {
            "tanf": (
                f"CY{YEAR} SPM units with tanf_if_takes_up > 0 (eligible) and "
                "tanf > 0 (participating) over the year — any-time-in-year "
                "counts: State TANF programs mix YEAR and MONTH periods, so no "
                "average-month count exists."
            ),
            "snap": (
                f"Average of the 12 months of CY{YEAR}: SPM units with "
                "is_snap_eligible (eligible) and snap > 0 (participating) in the "
                f"federal-rules world ({BBCE_INPUT} forced False every month)."
            ),
            "ssi": (
                f"Average of the 12 months of CY{YEAR}: adults 18+ with "
                "ssi_if_takes_up > 0 (eligible for a payment) and ssi > 0 "
                "(participating); joint claims (ssi_claim_is_joint) are couple "
                "units (persons / 2), others one-person units, aged if 65+ else "
                "disabled."
            ),
        },
        "toggle_check": {"federal_bbce_input_mean": toggle},
        "series": series,
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
    for name, s in staged["series"].items():
        log(
            f"{name}: rate {s['participation_rate']:.4f} "
            f"({s['participant_count']:,.0f} / {s['eligible_count']:,.0f})"
        )
    log(f"wrote {out}")


if __name__ == "__main__":
    main()
