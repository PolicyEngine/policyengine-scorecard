"""Family ``ca_fiscal_notes``: PolicyEngine counterparts for California
fiscal notes on young child tax credit (YCTC) bills (sources/ca-fiscal-notes/,
lane ca-fiscal-notes, issue #4).

FTB's estimates, restated in the Assembly Revenue and Taxation Committee
analyses, are General Fund revenue losses by State fiscal year:

* AB 397 (as introduced 2025-02-03) raises the YCTC age limit from "under 6"
  to under 10 (tax year 2025), 13 (2026), 16 (2027) and 19 (2028 on; 24 for
  students, a provision outside the claims' years).
* AB 1690 (as introduced 2026-02-03) sets it to 6 plus the whole years
  elapsed since 2026-01-01: under 7 in tax year 2027, under 8 in 2028.

The reform sets ``gov.states.ca.tax.income.credits.young_child.ineligible_age``
year by year (``ca_yctc`` tests ``age < ineligible_age``). The counterpart of
a fiscal year's revenue change is the reform-minus-baseline weighted total of
``ca_income_tax`` for the tax year whose returns are filed in that fiscal
year (FY 2025-26 <- tax year 2025): the YCTC is refundable and is paid when
returns are filed. The ingest records that mapping on each result.

Three simulations, each in its own child process (``common.run_job``):
baseline, AB 397 and AB 1690, each measuring tax years 2025-2028.

Usage (writes sources/ca-fiscal-notes/pe/<bundle_id>.json and the run log
pipeline/campaign_us/runs/ca_fiscal_notes__<bundle_id>.json):

    .venv-pe/bin/python pipeline/campaign_us/ca_fiscal_notes.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from common import FAR_END, REPO, log, now_utc, provenance, run_job

STEM = "ca_fiscal_notes"
YEARS = (2025, 2026, 2027, 2028)
OUT_DIR = REPO / "sources" / "ca-fiscal-notes" / "pe"
RUN_ID = "ca-fiscal-notes-20261019"
AGE = "gov.states.ca.tax.income.credits.young_child.ineligible_age"


def _ages(by_year: dict[int, int], last: int) -> dict:
    """{period: age}: one-year windows, the last value held to FAR_END."""
    out = {}
    for year, age in by_year.items():
        end = f"{FAR_END}" if year == last else f"{year}-12-31"
        out[f"{year}-01-01.{end}"] = age
    return out


BILLS = {
    "ab397": {AGE: _ages({2025: 10, 2026: 13, 2027: 16, 2028: 19}, 2028)},
    "ab1690": {AGE: _ages({2027: 7, 2028: 8}, 2028)},
}

POLICYENGINE_VARIABLES = ["ca_income_tax", "ca_yctc", "state_code_str"]


def measures(sim) -> dict:
    """Per tax year: weighted California income tax (tax units; the
    variable is defined for California only), the YCTC total, and the
    number of tax units with a YCTC."""
    out = {}
    for year in YEARS:
        tax = sim.calculate("ca_income_tax", year)
        yctc = sim.calculate("ca_yctc", year)
        out[f"ca_income_tax|{year}"] = tax.sum()
        out[f"ca_yctc|{year}"] = yctc.sum()
        out[f"ca_yctc_units|{year}"] = (yctc > 0).sum()
        out[f"ineligible_age|{year}"] = float(
            sim.tax_benefit_system.parameters(
                f"{year}-01-01"
            ).gov.states.ca.tax.income.credits.young_child.ineligible_age
        )
    return out


JOBS = {
    "baseline": {"label": "ca fiscal notes baseline", "measure": f"{STEM}:measures"},
    **{
        bill: {
            "label": f"ca fiscal notes {bill}",
            "reform": reform,
            "measure": f"{STEM}:measures",
        }
        for bill, reform in BILLS.items()
    },
}


def run() -> tuple[dict, dict]:
    results = {name: run_job(job) for name, job in JOBS.items()}
    prov = provenance(list(results.values()))
    base = results["baseline"]["values"]
    if any(base[f"ineligible_age|{y}"] != 6 for y in YEARS):
        raise RuntimeError("baseline YCTC age limit is not 6 in every year")
    bills = {}
    for bill in BILLS:
        ref = results[bill]["values"]
        bills[bill] = {
            str(y): {
                "ineligible_age": ref[f"ineligible_age|{y}"],
                "revenue_change": ref[f"ca_income_tax|{y}"]
                - base[f"ca_income_tax|{y}"],
                "yctc_change": ref[f"ca_yctc|{y}"] - base[f"ca_yctc|{y}"],
                "yctc_units_change": ref[f"ca_yctc_units|{y}"]
                - base[f"ca_yctc_units|{y}"],
            }
            for y in YEARS
        }
    staged = {
        "family": STEM,
        "run_id": RUN_ID,
        "computed_at": now_utc(),
        "time_basis": "annual",
        "provenance": prov,
        "policyengine_variables": POLICYENGINE_VARIABLES,
        "pe_construction": (
            "reform_delta:ca_income_tax — weighted total of ca_income_tax "
            f"with {AGE} set year by year, minus the baseline total, per "
            "tax year on the certified bundle (static, no behavioural "
            "response)."
        ),
        "baseline": {
            str(y): {
                "ca_income_tax": base[f"ca_income_tax|{y}"],
                "ca_yctc": base[f"ca_yctc|{y}"],
                "ca_yctc_units": base[f"ca_yctc_units|{y}"],
            }
            for y in YEARS
        },
        "bills": bills,
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
    for bill, years in staged["bills"].items():
        log(
            f"{bill}: "
            + ", ".join(
                f"{y} {v['revenue_change'] / 1e6:,.0f}M" for y, v in years.items()
            )
        )
    log(f"wrote {out}")


if __name__ == "__main__":
    main()
