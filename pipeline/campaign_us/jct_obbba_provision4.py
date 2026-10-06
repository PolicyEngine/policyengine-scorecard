"""Family ``jct_obbba_provision4`` (1 row, original run_id campaign-20260802-obbba).

JCT JCX-35-25 provision 4 ("Extension and enhancement of increased child
tax credit"), FY2026, present-law baseline.

Construction (original ``pe_construction``): "scored as expiry reversal
from enacted law; negated (exact for the same static world pair)" with the
expiry-world CTC parameters

    gov.irs.credits.ctc.amount.base[0].amount: -> 1000
    gov.irs.credits.ctc.amount.adult_dependent: -> 0
    gov.irs.credits.ctc.refundable.individual_max: -> 1000
    gov.irs.credits.ctc.refundable.phase_in.threshold: -> 3000
    gov.irs.credits.ctc.phase_out.threshold.JOINT: -> 110000
    gov.irs.credits.ctc.phase_out.threshold.SINGLE: -> 75000
    gov.irs.credits.ctc.phase_out.threshold.HEAD_OF_HOUSEHOLD: -> 75000
    gov.irs.credits.ctc.phase_out.threshold.SURVIVING_SPOUSE: -> 75000
    gov.irs.credits.ctc.phase_out.threshold.SEPARATE: -> 55000

Two simulations — current law (enacted OBBBA) and the expiry world (the
nine values above from 2026-01-01). pe_value = -(income_tax_expiry -
income_tax_current_law), weighted federal ``income_tax`` sums, CY2026,
rounded to whole dollars (the original is a whole-dollar value).

The original construction text quotes "The 1.87 ratio vs JCT's stack
position" — PE / JCT (JCX-35-25 FY2026 provision 4 = -$48,769M, the
matched claim's value). That ratio is a number derived from the old
bundle's result, so the staged text recomputes it from this run (same
two-decimal format); everything else in the text is carried verbatim.
"""

from __future__ import annotations

import re

from common import FAR_END, emit_row, load_original, now_utc, provenance, run_job

STEM = "jct_obbba_provision4"
YEAR = 2026
JCT_CLAIM_VALUE = (
    -48_769_000_000.0
)  # JCX-35-25 provision 4, FY2026 (claim 01304f138bf44f724ef0)
EXPIRY = {
    "gov.irs.credits.ctc.amount.base[0].amount": 1000,
    "gov.irs.credits.ctc.amount.adult_dependent": 0,
    "gov.irs.credits.ctc.refundable.individual_max": 1000,
    "gov.irs.credits.ctc.refundable.phase_in.threshold": 3000,
    "gov.irs.credits.ctc.phase_out.threshold.JOINT": 110000,
    "gov.irs.credits.ctc.phase_out.threshold.SINGLE": 75000,
    "gov.irs.credits.ctc.phase_out.threshold.HEAD_OF_HOUSEHOLD": 75000,
    "gov.irs.credits.ctc.phase_out.threshold.SURVIVING_SPOUSE": 75000,
    "gov.irs.credits.ctc.phase_out.threshold.SEPARATE": 55000,
}
REFORM = {p: {f"{YEAR}-01-01.{FAR_END}": v} for p, v in EXPIRY.items()}


def measures(sim) -> dict:
    return {"income_tax": sim.calculate("income_tax", YEAR).sum()}


def run() -> tuple[list[dict], dict]:
    (orig,) = load_original(STEM)
    base = run_job(
        {"label": "jct current law CY2026", "measure": "jct_obbba_provision4:measures"}
    )
    ref = run_job(
        {
            "label": "jct expiry world CY2026",
            "reform": REFORM,
            "measure": "jct_obbba_provision4:measures",
        }
    )
    prov = provenance([base, ref])
    unrounded = -(ref["values"]["income_tax"] - base["values"]["income_tax"])
    value = float(round(unrounded))
    ratio = value / JCT_CLAIM_VALUE
    text, n = re.subn(
        r"The \d+\.\d{2} ratio", f"The {ratio:.2f} ratio", orig["pe_construction"]
    )
    if n != 1:
        raise RuntimeError("ratio phrase not found in the original construction")
    row = emit_row(orig, value, prov, now_utc(), pe_construction=text)
    meta = {
        "provenance": prov,
        "jobs": [base, ref],
        "unrounded": unrounded,
        "ratio_vs_jct": ratio,
    }
    return [row], meta
