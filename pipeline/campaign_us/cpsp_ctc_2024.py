"""Family ``cpsp_ctc_2024`` (8 rows, original run_id campaign-20260802-cpsp).

CPSP "What Could 2024 Child Poverty Rates Have Looked Like Had an Expanded
Child Tax Credit Been in Place?" (Table 1): SPM child poverty rates, CY2024,
for children under 18 and under 6, under four CTC worlds.

Common to every world (original annotation "takeup: credit take-up/filing
flags forced (CPSP ASEC basis); benefit take-up calibrated"): the credit
take-up flag ``takes_up_eitc`` and the refundable-credit filing flag
``would_file_if_eligible_for_refundable_credit`` are set True for every tax
unit for 2024 before any calculation; benefit take-up flags are left as
served (calibrated). Poverty = ``spm_unit_is_in_spm_poverty`` mapped to
persons; rate = weighted poor children / weighted children (age < 18, or
age < 6), 2024.

Worlds, from the original ``pe_construction`` texts (all parameter changes
for 2024 only):

* TCJA CTC — "" (2024 current law is the TCJA CTC): no reform.
* No CTC — "base[0].amount 2000 -> 0; adult_dependent 500 -> 0".
* OBBBA CTC — "base 2000 -> 2137.38; refundable cap 1700 -> 1651.61;
  phase-in threshold 2500 -> 2428.84; thresholds x0.97154": the three
  amounts as printed; ``phase_out.threshold.<status>`` = 2024 value x
  0.97154 (2025-statute parameters deflated to 2024 dollars).
* AFA CTC — "arpa u6 4197.04 / 6-17 3497.53; first-tier {JOINT 145730.6,
  SURVIVING_SPOUSE 145730.6, SINGLE 72865.3, SEPARATE 72865.3,
  HEAD_OF_HOUSEHOLD 109297.95}; qualifying age -> 18; fully refundable":
  ``amount.arpa[0].amount``/``[1].amount``, ``phase_out.arpa.threshold.*``
  as printed, ``amount.base[1].threshold = 18``,
  ``refundable.fully_refundable = True`` and ``phase_out.arpa.in_effect =
  True`` (implied: the ARPA addition and its first-tier phase-out only
  exist when this is on).
"""

from __future__ import annotations

import numpy as np
from common import emit_row, load_original, now_utc, provenance, run_job

STEM = "cpsp_ctc_2024"
YEAR = 2024
R2024 = f"{YEAR}-01-01.{YEAR}-12-31"
CPI_RATIO = 0.97154
STATUSES = ["SINGLE", "JOINT", "SEPARATE", "HEAD_OF_HOUSEHOLD", "SURVIVING_SPOUSE"]
FLAGS = {
    "takes_up_eitc": {"value": True, "years": [YEAR]},
    "would_file_if_eligible_for_refundable_credit": {"value": True, "years": [YEAR]},
}


def _r(d: dict) -> dict:
    return {p: {R2024: v} for p, v in d.items()}


NO_CTC = _r(
    {
        "gov.irs.credits.ctc.amount.base[0].amount": 0,
        "gov.irs.credits.ctc.amount.adult_dependent": 0,
    }
)
AFA = _r(
    {
        "gov.irs.credits.ctc.amount.arpa[0].amount": 4197.04,
        "gov.irs.credits.ctc.amount.arpa[1].amount": 3497.53,
        "gov.irs.credits.ctc.phase_out.arpa.threshold.JOINT": 145730.6,
        "gov.irs.credits.ctc.phase_out.arpa.threshold.SURVIVING_SPOUSE": 145730.6,
        "gov.irs.credits.ctc.phase_out.arpa.threshold.SINGLE": 72865.3,
        "gov.irs.credits.ctc.phase_out.arpa.threshold.SEPARATE": 72865.3,
        "gov.irs.credits.ctc.phase_out.arpa.threshold.HEAD_OF_HOUSEHOLD": 109297.95,
        "gov.irs.credits.ctc.amount.base[1].threshold": 18,
        "gov.irs.credits.ctc.refundable.fully_refundable": True,
        "gov.irs.credits.ctc.phase_out.arpa.in_effect": True,
    }
)


def obbba_reform() -> dict:
    """OBBBA world: phase-out thresholds read from the live 2024 tree and
    multiplied by the CPI ratio (built inside the simulation process)."""
    from policyengine_core.parameters import get_parameter
    from policyengine_us.system import system

    p = system.parameters
    out = {
        "gov.irs.credits.ctc.amount.base[0].amount": 2137.38,
        "gov.irs.credits.ctc.refundable.individual_max": 1651.61,
        "gov.irs.credits.ctc.refundable.phase_in.threshold": 2428.84,
    }
    for fs in STATUSES:
        path = f"gov.irs.credits.ctc.phase_out.threshold.{fs}"
        out[path] = float(get_parameter(p, path)(f"{YEAR}-01-01")) * CPI_RATIO
    return _r(out)


WORLDS = {
    "TCJA CTC": {},
    "No CTC": {"reform": NO_CTC},
    "OBBBA CTC": {"reform_builder": "cpsp_ctc_2024:obbba_reform"},
    "AFA CTC": {"reform": AFA},
}


def measures(sim) -> dict:
    age_ms = sim.calculate("age", YEAR)
    ones = age_ms >= -1  # weighted ones over persons
    age = np.asarray(age_ms.values, dtype=float)
    poor = (
        np.asarray(
            sim.calculate("spm_unit_is_in_spm_poverty", YEAR, map_to="person").values
        )
        > 0
    )
    out = {}
    for name, child in [("children_under_18", age < 18), ("children_under_6", age < 6)]:
        out[f"{name}_poor"] = ones[child & poor].sum()
        out[f"{name}_pop"] = ones[child].sum()
        out[name] = out[f"{name}_poor"] / out[f"{name}_pop"]
    return out


def run() -> tuple[list[dict], dict]:
    originals = load_original(STEM)
    results = {}
    for world, spec in WORLDS.items():
        results[world] = run_job(
            {
                "label": f"cpsp {world} CY2024",
                "measure": "cpsp_ctc_2024:measures",
                "inputs": FLAGS,
                **spec,
            }
        )
    prov = provenance(list(results.values()))
    at = now_utc()
    rows = []
    for o in originals:
        c = o["external_claim_match"]["conditions"]
        v = results[c["policy_scenario"]]["values"][c["subgroup"]]
        rows.append(emit_row(o, v, prov, at))
    return rows, {"provenance": prov, "jobs": list(results.values())}
