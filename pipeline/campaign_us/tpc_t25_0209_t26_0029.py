"""Family ``tpc_t25_0209_t26_0029`` (14 rows incl. 4 exhibits, original run_id
campaign-20260802-tpc).

TPC T25-0209 (CTC options x 39.6% top rate, three options + totals) and
T26-0029 (American Family Act), revenue change, CY2026 (vs TPC FY2026).

Revenue change of a reform = weighted sum of federal ``income_tax`` under
the reform minus under current law (enacted OBBBA), CY2026, rounded to
whole dollars (the original values are whole dollars).

Reforms, from the original ``pe_construction`` texts:

* CTC option 1: "CTC base 2200 -> 2500" ->
  ``gov.irs.credits.ctc.amount.base[0].amount = 2500``.
* CTC option 2: option 1 + "refundable max 1700 -> 2000" ->
  ``gov.irs.credits.ctc.refundable.individual_max = 2000``.
* CTC option 3: option 2 + "phase-in from first dollar of earnings
  (threshold 2500 -> 0)" ->
  ``gov.irs.credits.ctc.refundable.phase_in.threshold = 0``.
  CTC changes apply from 2025-01-01; separate CY2025 simulations give the
  "CY2025 variant" each CTC row's annotation quotes.
* Top-rate options: "additional 39.6% bracket above {thresholds} (contrib
  additional_tax_bracket structural reform; slots 1-7 mirrored from
  current-law tree at runtime)" -> ``gov.contrib.additional_tax_bracket``
  with ``in_effect = True``, ``rates.1..7`` and ``thresholds.1..6.<status>``
  copied from the engine's current-law ``gov.irs.income.bracket`` at
  2026-01-01 (read at runtime inside the simulation process),
  ``thresholds.7.<status>`` = the option's thresholds (SEPARATE = joint/2,
  SURVIVING_SPOUSE = joint, as in the original), ``rates.8 = 0.396``.
* Totals: the option's CTC reform and top-rate reform together.
* American Family Act: "AFA-2025 statute: arpa 4320/3600, fully refundable,
  age<18, second-tier HoH 300k; ... mid-tier floor kept at OBBBA $2,200" ->
  ``amount.arpa[0].amount = 4320`` (under 6), ``amount.arpa[1].amount =
  3600`` (6-17), ``phase_out.arpa.in_effect = True`` (implied: the ARPA
  addition and its first-tier phase-out only exist when this is on),
  ``refundable.fully_refundable = True``, ``amount.base[1].threshold = 18``
  (age < 18 qualifies), ``phase_out.threshold.HEAD_OF_HOUSEHOLD = 300000``;
  base amount left at the current-law 2200 (the floor). From 2026-01-01.
  A second run with ``base[0].amount = 2000`` regenerates the annotation
  "floor-construction bound: bill-text $2,000 floor gives X (width Y)".

Exhibit rows (derived pair-differences, ``exhibit: true``) are differences
of the option rows' unrounded revenue changes, rounded to $0.01B as the
originals are (1.67e9, 0.85e9, -2.37e9, -2.99e9). Their construction text
quotes the PE number ("PE +1.67B vs TPC +1.8B"); the staged text
regenerates that number from this run — the TPC side is carried verbatim.
Likewise the "CY2025 variant: X" and AFA floor-bound annotations quote
old-bundle numbers and are regenerated from this run.
"""

from __future__ import annotations

import re

from common import FAR_END, emit_row, load_original, now_utc, provenance, run_job

STEM = "tpc_t25_0209_t26_0029"
YEAR = 2026
STATUSES = ["SINGLE", "JOINT", "SEPARATE", "HEAD_OF_HOUSEHOLD", "SURVIVING_SPOUSE"]

CTC_RANGE = f"2025-01-01.{FAR_END}"
RANGE_2026 = f"{YEAR}-01-01.{FAR_END}"

CTC = {
    1: {"gov.irs.credits.ctc.amount.base[0].amount": 2500},
    2: {
        "gov.irs.credits.ctc.amount.base[0].amount": 2500,
        "gov.irs.credits.ctc.refundable.individual_max": 2000,
    },
    3: {
        "gov.irs.credits.ctc.amount.base[0].amount": 2500,
        "gov.irs.credits.ctc.refundable.individual_max": 2000,
        "gov.irs.credits.ctc.refundable.phase_in.threshold": 0,
    },
}
TOP_THRESHOLDS = {
    1: {
        "JOINT": 2120000,
        "SINGLE": 1884425,
        "HEAD_OF_HOUSEHOLD": 2002200,
        "SEPARATE": 1060000.0,
        "SURVIVING_SPOUSE": 2120000,
    },
    2: {
        "JOINT": 1720000,
        "SINGLE": 1528875,
        "HEAD_OF_HOUSEHOLD": 1624400,
        "SEPARATE": 860000.0,
        "SURVIVING_SPOUSE": 1720000,
    },
    3: {
        "JOINT": 1562500,
        "SINGLE": 1388875,
        "HEAD_OF_HOUSEHOLD": 1475650,
        "SEPARATE": 781250.0,
        "SURVIVING_SPOUSE": 1562500,
    },
}
AFA = {
    "gov.irs.credits.ctc.amount.arpa[0].amount": 4320,
    "gov.irs.credits.ctc.amount.arpa[1].amount": 3600,
    "gov.irs.credits.ctc.phase_out.arpa.in_effect": True,
    "gov.irs.credits.ctc.refundable.fully_refundable": True,
    "gov.irs.credits.ctc.amount.base[1].threshold": 18,
    "gov.irs.credits.ctc.phase_out.threshold.HEAD_OF_HOUSEHOLD": 300000,
}
AFA_FLOOR_2000 = {**AFA, "gov.irs.credits.ctc.amount.base[0].amount": 2000}


def _ctc_reform(opt: int) -> dict:
    return {p: {CTC_RANGE: v} for p, v in CTC[opt].items()}


def reform(ctc_option: int | None = None, top_option: int | None = None) -> dict:
    """Reform dict; the top-rate part mirrors the live current-law bracket
    tree, so it is built inside the simulation process."""
    out = {}
    if ctc_option:
        out.update(_ctc_reform(ctc_option))
    if top_option:
        from policyengine_core.parameters import get_parameter
        from policyengine_us.system import system

        p = system.parameters
        at = f"{YEAR}-01-01"
        c = "gov.contrib.additional_tax_bracket"
        out[f"{c}.in_effect"] = {RANGE_2026: True}
        for i in range(1, 8):
            rate = get_parameter(p, f"gov.irs.income.bracket.rates.{i}")(at)
            out[f"{c}.bracket.rates.{i}"] = {RANGE_2026: float(rate)}
        for i in range(1, 7):
            for fs in STATUSES:
                thr = get_parameter(p, f"gov.irs.income.bracket.thresholds.{i}.{fs}")(
                    at
                )
                out[f"{c}.bracket.thresholds.{i}.{fs}"] = {RANGE_2026: float(thr)}
        for fs in STATUSES:
            out[f"{c}.bracket.thresholds.7.{fs}"] = {
                RANGE_2026: float(TOP_THRESHOLDS[top_option][fs])
            }
        out[f"{c}.bracket.rates.8"] = {RANGE_2026: 0.396}
    return out


def measures(sim, years=(YEAR,)) -> dict:
    return {f"income_tax_{y}": sim.calculate("income_tax", y).sum() for y in years}


def _jobs() -> list[dict]:
    """One fresh simulation per (world, year): CY2026 for every row, and
    CY2025 for current law + the three CTC options (the annotation's
    "CY2025 variant"). Years are never computed in the same simulation —
    in policyengine-us 1.764.6 a simulation that already computed CY2025
    returns a slightly different CY2026 ``income_tax`` (see
    ``pwbm_ss_elimination``)."""
    m = "tpc_t25_0209_t26_0029:measures"
    y25 = {"years": [2025]}
    jobs = [{"key": "baseline", "label": "tpc current law CY2026", "measure": m}]
    for o in (1, 2, 3):
        jobs.append(
            {
                "key": f"ctc{o}",
                "label": f"tpc ctc option {o} CY2026",
                "reform": _ctc_reform(o),
                "measure": m,
            }
        )
    for o in (1, 2, 3):
        jobs.append(
            {
                "key": f"top{o}",
                "label": f"tpc top-rate option {o} CY2026",
                "reform_builder": "tpc_t25_0209_t26_0029:reform",
                "reform_builder_args": {"top_option": o},
                "measure": m,
            }
        )
    for o in (1, 2, 3):
        jobs.append(
            {
                "key": f"tot{o}",
                "label": f"tpc total option {o} CY2026",
                "reform_builder": "tpc_t25_0209_t26_0029:reform",
                "reform_builder_args": {"ctc_option": o, "top_option": o},
                "measure": m,
            }
        )
    jobs.append(
        {
            "key": "afa",
            "label": "tpc AFA CY2026",
            "measure": m,
            "reform": {p: {RANGE_2026: v} for p, v in AFA.items()},
        }
    )
    jobs.append(
        {
            "key": "afa_floor2000",
            "label": "tpc AFA $2,000-floor bound CY2026",
            "measure": m,
            "reform": {p: {RANGE_2026: v} for p, v in AFA_FLOOR_2000.items()},
        }
    )
    jobs.append(
        {
            "key": "baseline@2025",
            "label": "tpc current law CY2025",
            "measure": m,
            "measure_args": y25,
        }
    )
    for o in (1, 2, 3):
        jobs.append(
            {
                "key": f"ctc{o}@2025",
                "label": f"tpc ctc option {o} CY2025",
                "reform": _ctc_reform(o),
                "measure": m,
                "measure_args": y25,
            }
        )
    return jobs


def _fmt_b(x: float, nd: int, plus: bool) -> str:
    s = f"{abs(x) / 1e9:.{nd}f}B"
    return ("-" if x < 0 else ("+" if plus else "")) + s


def run() -> tuple[list[dict], dict]:
    originals = load_original(STEM)
    results = {}
    for job in _jobs():
        key = job.pop("key")
        results[key] = run_job(job)
    prov = provenance(list(results.values()))

    def delta(key: str, y: int = YEAR) -> float:
        sfx = "" if y == YEAR else f"@{y}"
        return (
            results[key + sfx]["values"][f"income_tax_{y}"]
            - results["baseline" + sfx]["values"][f"income_tax_{y}"]
        )

    unrounded = {k: delta(k) for k in results if "@" not in k and k != "baseline"}
    cy2025 = {f"ctc{o}": delta(f"ctc{o}", 2025) for o in (1, 2, 3)}
    exhibit_src = {
        "tpc_t25_0209_toprate_opt2_minus_opt1": unrounded["top2"] - unrounded["top1"],
        "tpc_t25_0209_toprate_opt3_minus_opt2": unrounded["top3"] - unrounded["top2"],
        "tpc_t25_0209_ctc_opt3_minus_opt2": unrounded["ctc3"] - unrounded["ctc2"],
        "tpc_t25_0209_ctc_opt2_minus_opt1": unrounded["ctc2"] - unrounded["ctc1"],
    }

    at = now_utc()
    rows = []
    for o in originals:
        if o.get("exhibit"):
            rk = o["exhibit_meta"]["reform_key"]
            v = float(round(exhibit_src[rk] / 1e7) * 1e7)
            text, n = re.subn(
                r"PE [+-]\d+\.\d{2}B", "PE " + _fmt_b(v, 2, True), o["pe_construction"]
            )
            if n != 1:
                raise RuntimeError(f"PE number not found in exhibit text: {rk}")
            rows.append(emit_row(o, v, prov, at, pe_construction=text))
            continue
        cond = o["external_claim_match"]["conditions"]
        prov_row = cond["provision_row"]
        opt = int(cond["option"].split()[-1]) if "option" in cond else None
        anns = list(o["annotations"])
        if prov_row == "American Family Act":
            key = "afa"
            afa, floor = unrounded["afa"], unrounded["afa_floor2000"]
            new = (
                f"floor-construction bound: bill-text $2,000 floor gives "
                f"{_fmt_b(floor, 1, False)} (width {abs(afa - floor) / 1e9:.1f}B)"
            )
            anns = [
                new if a.startswith("floor-construction bound:") else a for a in anns
            ]
        elif prov_row == "Total for both provisions":
            key = f"tot{opt}"
        elif "top individual income tax rate" in prov_row:
            key = f"top{opt}"
        else:
            key = f"ctc{opt}"
            anns = [
                f"CY2025 variant: {_fmt_b(cy2025[key], 1, False)}"
                if a.startswith("CY2025 variant:")
                else a
                for a in anns
            ]
        rows.append(
            emit_row(o, float(round(unrounded[key])), prov, at, annotations=anns)
        )
    meta = {
        "provenance": prov,
        "jobs": list(results.values()),
        "unrounded_cy2026": unrounded,
        "cy2025": cy2025,
        "exhibits_unrounded": exhibit_src,
    }
    return rows, meta
