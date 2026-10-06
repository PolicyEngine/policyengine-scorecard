"""Family ``pwbm_ss_elimination`` (2 rows, original run_id campaign-20260802-pwbm-ss).

PWBM "Ending taxation of Social Security benefits", conventional revenue
change, periods 2025 and 2026.

Construction (original ``pe_construction``, verbatim parameter list):

    gov.irs.social_security.taxability.rate.base.excess: 0.5 -> 0
    gov.irs.social_security.taxability.rate.base.benefit_cap: 0.5 -> 0
    gov.irs.social_security.taxability.rate.additional.bracket: 0.5 -> 0
    gov.irs.social_security.taxability.rate.additional.excess: 0.85 -> 0
    gov.irs.social_security.taxability.rate.additional.benefit_cap: 0.85 -> 0

Revenue change for year Y = weighted sum of federal ``income_tax`` under
the reform (all five rates 0 from 2025-01-01 onward) minus under current
law, CY Y, rounded to whole dollars (the original values are whole
dollars). Each year is computed in its OWN pair of fresh simulations, as
the original did (its two rows carry separate computed_at stamps, 19:21
and 19:51): in policyengine-us 1.764.6 a simulation that has already
computed CY2025 returns a slightly different CY2026 ``income_tax`` than a
fresh one (observed here: baseline CY2026 differs by ~$103M, i.e. 4e-5),
so computing both years in one simulation reproduces CY2026 only to ~1e-5.

The original annotation "construction verified: taxable_social_security =
0.0 exactly" is re-checked on every run: each reform run returns the
weighted sum and the maximum absolute value of ``taxable_social_security``
for its year, and the run fails if the maximum is non-zero.
"""

from __future__ import annotations

import numpy as np
from common import FAR_END, emit_row, load_original, now_utc, provenance, run_job

STEM = "pwbm_ss_elimination"
YEARS = (2025, 2026)
PATHS = [
    "gov.irs.social_security.taxability.rate.base.excess",
    "gov.irs.social_security.taxability.rate.base.benefit_cap",
    "gov.irs.social_security.taxability.rate.additional.bracket",
    "gov.irs.social_security.taxability.rate.additional.excess",
    "gov.irs.social_security.taxability.rate.additional.benefit_cap",
]
REFORM = {p: {f"2025-01-01.{FAR_END}": 0.0} for p in PATHS}


def measures(sim, years=YEARS, check_taxable_ss: bool = False) -> dict:
    v = {}
    for y in years:
        v[f"income_tax_{y}"] = sim.calculate("income_tax", y).sum()
        if check_taxable_ss:
            tss = sim.calculate("taxable_social_security", y)
            v[f"taxable_ss_sum_{y}"] = tss.sum()
            v[f"taxable_ss_maxabs_{y}"] = float(np.abs(np.asarray(tss.values)).max())
    return v


def run() -> tuple[list[dict], dict]:
    originals = load_original(STEM)
    m = "pwbm_ss_elimination:measures"
    base, ref = {}, {}
    for y in YEARS:
        base[y] = run_job(
            {
                "label": f"pwbm baseline CY{y}",
                "measure": m,
                "measure_args": {"years": [y]},
            }
        )
        ref[y] = run_job(
            {
                "label": f"pwbm reform CY{y}",
                "reform": REFORM,
                "measure": m,
                "measure_args": {"years": [y], "check_taxable_ss": True},
            }
        )
        if ref[y]["values"][f"taxable_ss_maxabs_{y}"] != 0.0:
            raise RuntimeError(f"taxable_social_security not zero in {y}")
    jobs = [j for y in YEARS for j in (base[y], ref[y])]
    prov = provenance(jobs)
    unrounded = {
        y: ref[y]["values"][f"income_tax_{y}"] - base[y]["values"][f"income_tax_{y}"]
        for y in YEARS
    }
    at = now_utc()
    rows = []
    for o in originals:
        y = o["external_claim_match"]["period"]
        rows.append(emit_row(o, float(round(unrounded[y])), prov, at))
    meta = {
        "provenance": prov,
        "jobs": jobs,
        "unrounded": {str(y): v for y, v in unrounded.items()},
    }
    return rows, meta
