"""PolicyEngine-UK benefit rates and April upratings, read from the parameter
tree (lane uk-benefit-uprating).

No simulation and no dataset: the April uprating of a benefit rate is a
parameter, so the counterpart of a published uprating is the rise in the
rate PolicyEngine-UK holds. Rates are read at 1 June of each year (inside
the tax year from April; pe-uk's uprated values step at 1 January).

Read:
* the UC standard allowance (four amounts), 2024-2029;
* the CPI-linked working-age basket: UC child and carer elements, child
  benefit (eldest and additional child), Carer's Allowance and the PIP
  daily living standard rate, 2025-2027;
* the protected UC health element (pre-2026 claimants), from the model's
  own Universal Credit Act 2025 s. 4 floor
  (``policyengine_uk.scenarios.uc_reform``), and the new-claimant amount;
* the LHA freeze flag;
* the new State Pension and the Pension Credit minimum guarantee, 2025-2026;
* the September CPI rates the model holds, and whether September 2026 is
  an entered outturn or the model's forecast, read from the package's own
  YAML.

Usage (any interpreter with policyengine-uk installed; writes
sources/uk-benefit-uprating/pe/uk-<version>.json):

    <venv>/bin/python pipeline/compute_uk_uprating_readback.py
"""

from __future__ import annotations

import importlib.metadata as md
import json
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT_DIR = REPO / "sources" / "uk-benefit-uprating" / "pe"
SAMPLE = "06-01"
YEARS = range(2024, 2030)

PATHS = {
    "uc_sa_single_25plus": "gov.dwp.universal_credit.standard_allowance.amount.SINGLE_OLD",
    "uc_sa_single_u25": "gov.dwp.universal_credit.standard_allowance.amount.SINGLE_YOUNG",
    "uc_sa_couple_25plus": "gov.dwp.universal_credit.standard_allowance.amount.COUPLE_OLD",
    "uc_sa_couple_u25": "gov.dwp.universal_credit.standard_allowance.amount.COUPLE_YOUNG",
    "uc_child_element": "gov.dwp.universal_credit.elements.child.amount",
    "uc_carer_element": "gov.dwp.universal_credit.elements.carer.amount",
    "child_benefit_eldest": "gov.hmrc.child_benefit.amount.eldest",
    "child_benefit_additional": "gov.hmrc.child_benefit.amount.additional",
    "carers_allowance": "gov.dwp.carers_allowance.rate",
    "pip_daily_living_standard": "gov.dwp.pip.daily_living.standard",
    "uc_lcwra_element": "gov.dwp.universal_credit.elements.disabled.amount",
    "uc_new_claimant_health_element": (
        "gov.dwp.universal_credit.rebalancing.new_claimant_health_element"
    ),
    "new_state_pension": "gov.dwp.state_pension.new_state_pension.amount",
    "pension_credit_mg_single": (
        "gov.dwp.pension_credit.guarantee_credit.minimum_guarantee.SINGLE"
    ),
    "benefit_uprating_cpi_index": "gov.benefit_uprating_cpi",
}
# The working-age rates that rise by September CPI each April.
CPI_BASKET = (
    "uc_child_element",
    "uc_carer_element",
    "child_benefit_eldest",
    "child_benefit_additional",
    "carers_allowance",
    "pip_daily_living_standard",
)
SEPTEMBER_CPI = "gov.economic_assumptions.statutory_uprating_inputs.cpi_september"
OBR_CALENDAR_CPI = "gov.economic_assumptions.yoy_growth.obr.consumer_price_index"
LHA_FREEZE = "gov.dwp.LHA.freeze"
SEPTEMBER_CPI_YAML = (
    "parameters/gov/economic_assumptions/statutory_uprating_inputs/cpi_september.yaml"
)


def node(parameters, path: str):
    for part in path.split("."):
        parameters = getattr(parameters, part)
    return parameters


def rises(values: dict[str, float]) -> dict[str, float]:
    """Year-on-year rise, keyed by the later year."""
    years = sorted(values)
    return {b: values[b] / values[a] - 1 for a, b in zip(years, years[1:])}


class _TreeOnly:
    """The one attribute the uc_reform helpers read from a simulation."""

    def __init__(self, system):
        self.tax_benefit_system = system


def protected_health_element(system) -> dict[str, float]:
    """Monthly protected LCWRA amount for 2026-27 and 2027-28, from the
    model's own s. 4 floor (2027-28 has no legislated amount yet)."""
    from policyengine_uk.scenarios import uc_reform

    shim = _TreeOnly(system)
    return {
        str(y): uc_reform._protected_existing_health_element_monthly(shim, y)
        for y in (2026, 2027)
    }


def september_2026_entered(package_dir: Path) -> bool:
    """True when the package's YAML holds an outturn for September 2026."""
    import yaml

    spec = yaml.safe_load((package_dir / SEPTEMBER_CPI_YAML).read_text())
    for key, value in spec["values"].items():
        if str(key) == "2026-09-01":
            return value is not None
    return False


def read() -> dict:
    import policyengine_uk
    from policyengine_uk.system import system

    p = system.parameters
    rates = {}
    for key, path in PATHS.items():
        values = {str(y): float(node(p, path)(f"{y}-{SAMPLE}")) for y in YEARS}
        rates[key] = {"path": path, "values": values, "rises": rises(values)}
    lha = {str(y): bool(node(p, LHA_FREEZE)(f"{y}-{SAMPLE}")) for y in (2026, 2027)}
    september = {
        str(y): float(node(p, SEPTEMBER_CPI)(f"{y}-09-01")) for y in (2025, 2026)
    }
    return {
        "rates": rates,
        "cpi_basket": list(CPI_BASKET),
        "protected_health_element_monthly": protected_health_element(system),
        "lha_freeze": lha,
        "september_cpi": september,
        "september_2026_entered": september_2026_entered(
            Path(policyengine_uk.__file__).parent
        ),
        "obr_calendar_cpi_2026": float(node(p, OBR_CALENDAR_CPI)("2026-01-01")),
    }


def main() -> None:
    version = md.version("policyengine-uk")
    computed_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    staged = {
        "family": "uk_benefit_uprating",
        "run_id": f"uk-uprating-readback-{version}-{computed_at[:10]}",
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
            f"simulation: each rate read at 1 June of each year (inside the "
            f"tax year from April), the April uprating taken as the year-on-"
            f"year rise."
        ),
        **read(),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"uk-{version}.json"
    out.write_text(json.dumps(staged, indent=1) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
