"""Compare reproduced rows with the original August 2026 campaign rows.

    python pipeline/campaign_us/validate.py --old <old-bundle out dir>
        [--new <new-bundle out dir>] [--md pipeline/campaign_us/VALIDATION.md]

Old-bundle rows are paired positionally with the originals (the families
emit rows in the original order) and the pairing is asserted on the match
descriptor / exhibit key; new-bundle rows are joined on that key (rows that
did not reproduce are never staged, and staging one fails this check).
Reproduced = |relative diff| <= 0.1% for counts and dollar totals, or
|abs diff| <= 1e-4 for rates (values in (0, 1)).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from common import ORIGINAL_DIR
from run import FAMILIES

REL_TOL = 1e-3
RATE_TOL = 1e-4


def _rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(x) for x in path.read_text().splitlines() if x]


def _key(r: dict) -> str:
    if r.get("exhibit"):
        return "exhibit:" + r["exhibit_meta"]["reform_key"]
    return json.dumps(r["external_claim_match"], sort_keys=True)


def _label(r: dict) -> str:
    if r.get("exhibit"):
        return "exhibit " + r["exhibit_meta"]["reform_key"]
    m = r["external_claim_match"]
    if "claim_id" in m:
        return (
            m["claim_id"]
            + " "
            + r["pe_construction"]
            .split(" |")[0]
            .replace("pass2 ", "")
            .replace(" CY2024", "")
        )
    c = m.get("conditions", {})
    bits = [m["metric"], str(m["period"])]
    for k in (
        "program",
        "component",
        "timing",
        "subgroup",
        "policy_scenario",
        "option",
        "provision_row",
        "provision",
    ):
        if k in c:
            bits.append(str(c[k])[:48])
    return " ".join(bits)


def is_rate(v: float) -> bool:
    return 0 < abs(v) < 1


def compare(orig: float, rep: float) -> tuple[float, bool]:
    rel = (rep - orig) / orig if orig else (0.0 if rep == 0 else float("inf"))
    ok = abs(rep - orig) <= RATE_TOL if is_rate(orig) else abs(rel) <= REL_TOL
    return rel, ok


def table(old_dir: Path, new_dir: Path | None) -> tuple[list[dict], dict]:
    out, summary = [], {}
    for fam in FAMILIES:
        orig = _rows(ORIGINAL_DIR / f"{fam}.jsonl")
        rep = _rows(old_dir / f"{fam}.jsonl")
        new = _rows(new_dir / f"{fam}.jsonl") if new_dir else []
        new_by_key = {_key(r): r for r in new}
        assert len(new_by_key) == len(new), f"{fam}: duplicate match keys"
        if not rep:
            summary[fam] = {"total": len(orig), "reproduced": 0, "ran": False}
            continue
        assert len(rep) == len(orig), fam
        n_ok, max_rel, text_diffs = 0, 0.0, []
        for i, (o, r) in enumerate(zip(orig, rep)):
            assert _key(o) == _key(r), (fam, i)
            rel, ok = compare(o["pe_value"], r["pe_value"])
            n_ok += ok
            max_rel = max(max_rel, abs(rel))
            for fld in ("pe_construction", "annotations", "status"):
                if o.get(fld) != r.get(fld):
                    text_diffs.append(f"row {i} {fld}")
            row = {
                "family": fam,
                "row": i,
                "label": _label(o),
                "original": o["pe_value"],
                "reproduced": r["pe_value"],
                "rel_diff": rel,
                "reproduced_ok": ok,
            }
            if _key(o) in new_by_key:
                if not ok:
                    raise AssertionError(f"{fam} row {i} staged but not reproduced")
                row["new"] = new_by_key[_key(o)]["pe_value"]
            out.append(row)
        summary[fam] = {
            "total": len(orig),
            "reproduced": n_ok,
            "max_abs_rel_diff": max_rel,
            "old_text_diffs": text_diffs,
            "ran": True,
            "old_bundle": rep[0]["data_bundle"],
            "old_engine": rep[0]["engine_version"],
            "old_computed_at": rep[0]["computed_at"],
            "new_staged": len(new),
            "new_bundle": new[0]["data_bundle"] if new else None,
            "new_engine": new[0]["engine_version"] if new else None,
            "new_computed_at": new[0]["computed_at"] if new else None,
        }
    return out, summary


def _fmt(v: float | None) -> str:
    if v is None:
        return "—"
    if is_rate(v):
        return f"{v:.6f}"
    if abs(v) >= 1e6:
        return f"{v:,.0f}"
    return f"{v:,.4f}"


def markdown(rows: list[dict], summary: dict, preamble: str = "") -> str:
    lines = [preamble] if preamble else []
    lines += [
        "## Summary",
        "",
        "| family | rows reproduced / total | max abs rel diff (old) | rows staged (new) | old bundle run | new bundle run |",
        "|---|---|---|---|---|---|",
    ]
    for fam, s in summary.items():
        if not s["ran"]:
            lines.append(f"| {fam} | not run | | | | |")
            continue
        lines.append(
            f"| {fam} | {s['reproduced']} / {s['total']} | {s['max_abs_rel_diff']:.2e} |"
            f" {s['new_staged']} |"
            f" {s['old_engine']} / {s['old_bundle']} ({s['old_computed_at'][:19]}Z) |"
            + (
                f" {s['new_engine']} / {s['new_bundle']} ({s['new_computed_at'][:19]}Z) |"
                if s["new_bundle"]
                else " — |"
            )
        )
    lines += [
        "",
        "## Per row",
        "",
        "Original = staged 2026-08-02 value (engine 1.764.6, buildp bundle). "
        "Reproduced = this reconstruction on the same old bundle. "
        "New = this reconstruction on the new certified bundle (blank when "
        'the row did not reproduce and was not staged). "new vs old-reproduced" '
        "is (new - old) / old, so for a negative value + means larger in "
        "magnitude; rates show the absolute change.",
        "",
    ]
    for fam in summary:
        fr = [r for r in rows if r["family"] == fam]
        if not fr:
            continue
        lines += [
            f"### {fam}",
            "",
            "| # | row | original | reproduced (old) | rel diff | reproduced? | new | new vs old-reproduced |",
            "|---|---|---|---|---|---|---|---|",
        ]
        for r in fr:
            new = r.get("new")
            chg = ""
            if new is not None and r["reproduced"]:
                chg = (
                    f"{new - r['reproduced']:+.6f} (abs)"
                    if is_rate(r["reproduced"])
                    else f"{(new - r['reproduced']) / r['reproduced']:+.2%}"
                )
            lines.append(
                f"| {r['row']} | {r['label']} | {_fmt(r['original'])} | {_fmt(r['reproduced'])} |"
                f" {r['rel_diff']:+.2e} | {'yes' if r['reproduced_ok'] else '**NO**'} |"
                f" {_fmt(new) if new is not None else ''} | {chg} |"
            )
        lines.append("")
    return "\n".join(lines)


PREAMBLE = """# US compute-campaign reconstruction — validation

Reconstruction of the six US families staged in
`sources/campaign-20260802/us/` (112 rows: 108 claim rows + 4 TPC exhibit
rows). The original campaign code is not available; each module in this
directory re-implements its rows from the recipe text the original rows
carry (`pe_construction` + annotations). The code was run twice:

* **Old bundle (reproduction check)** — `.venv-pe501`: policyengine 5.0.1,
  bundle `us-5.0.1` = policyengine-us 1.764.6 + certified data
  `populace-us-2024-buildp-sparse-rmloss100-cae8640-20260728T011454Z`
  (sha256 48b9d479…), the bundle every original row names. Output:
  `pipeline/campaign_us/runs/old-us-5.0.1/`.
* **New bundle** — `.venv-pe`: policyengine 6.2.1, bundle `us-6.2.1` =
  policyengine-us 2.2.1 + certified data `populace-us-2024-spm-20260915`
  (sha256 6496cc43…). Only rows reproduced on the old bundle are staged, to
  `sources/campaign-20261006/us/` (run_ids `campaign-20261006-<suffix>`).

**Result: all 112 rows reproduce on the old bundle with zero difference**
(bit-identical values; every regenerated text — see below — also equals
the original text), so all 112 are staged on the new bundle.

Tolerance: reproduced = |relative diff| <= 0.1% (counts, dollars), or
|absolute diff| <= 1e-4 for rates. Every run's raw job values, applied
reform dicts (read back from the simulation's parameter tree) and timings
are in `pipeline/campaign_us/runs/<family>__<bundle_id>.json`.

## Environment note (old bundle)

`uv pip install "policyengine[us]==5.0.1"` resolves `spm-calculator`
1.0.0.post1 (released 2026-09-14), which no longer ships
`spm_calculator.geoadj`; policyengine-us 1.764.6 imports it and fails to
load. The env pins `spm-calculator==0.3.1`, the latest release at the time
of the original campaign (2026-04-17; policyengine-us 1.764.6 requires
`>=0.2.0`).

## Construction decisions (all stated in the module docstrings)

* **cbo_free_joins** — the SSI "year-grid part_pop" is adults 18+ with
  `ssi > 0` (the year-grid counterpart runner's Urban SSI universe,
  `pipeline/compute_counterparts.py`); the all-ages count (6,288,302 on the
  old bundle) does not reproduce the original 6,108,392.
* **pwbm_ss_elimination / tpc** — each (world, year) is computed in its own
  fresh simulation. In policyengine-us 1.764.6 a simulation that has
  already computed CY2025 returns a different CY2026 `income_tax`
  (baseline: 2,605,788,866,110 vs 2,605,685,778,045 fresh, 4.0e-5);
  computing both years in one simulation reproduced the PWBM CY2026 row
  only to 1.1e-5. Separate simulations reproduce it exactly, matching the
  original rows' separate computed_at stamps.
* **cpsp_ctc_2024** — "credit take-up/filing flags forced" =
  `takes_up_eitc` and `would_file_if_eligible_for_refundable_credit` set
  True for 2024; the ARPA-style worlds also set
  `phase_out.arpa.in_effect = True` (the ARPA addition does not exist
  without it); OBBBA phase-out thresholds = 2024 value x 0.97154.
* **urban_subgroup_counts** — SSI eligibility is the person's own
  `is_ssi_eligible` (all ages); the unit reading overstates by 9-98%.
  Earners = `tax_unit_earned_income > 0`. Race5 = `is_hispanic` first, then
  `cps_race` 1 / 2 / {4,5} / other.
* **jct_obbba_provision4** — expiry world minus current law, negated.

## Parameter paths on policyengine-us 2.2.1

No mapping was needed. All 85 (parameter path, start instant) pairs the
reforms touch resolve in both engines, with identical current-law values
at those instants (checked with `policyengine_core.parameters.get_parameter`
in both envs); each run also reads every reformed parameter back from the
simulation and fails if a value did not apply. The one engine rename that
touches these families is an input, not a parameter: policyengine 6.2.1
maps the stored `would_claim_wic` onto `takes_up_wic_if_eligible`
(recorded as `legacy_input_renames` in the bundle provenance).

## Text regenerated from the run (old-bundle numbers in the originals)

`pe_construction` is carried verbatim except where it quotes a PE number,
and annotations are carried verbatim except those that quote a PE number:

* jct_obbba_provision4 construction: "The 1.87 ratio vs JCT's stack
  position" -> recomputed PE / JCT (JCX-35-25 FY2026 = -$48,769M).
* tpc exhibit constructions: "PE +1.67B" etc. -> recomputed (the TPC twin
  is verbatim).
* tpc CTC annotations "CY2025 variant: X" and the AFA annotation
  "floor-construction bound: bill-text $2,000 floor gives X (width Y)" ->
  recomputed from CY2025 / $2,000-floor simulations.

On the old bundle every regenerated text equals the original text. On the
new bundle two texts change: the ctc2-ctc1 exhibit ("PE -2.99B" -> "PE
-2.98B") and the AFA floor bound ("-130.7B" -> "-130.6B"). The JCT ratio
(1.87) and the three CY2025 variants (-12.3B / -15.1B / -17.6B) are the
same at their printed precision. Staged rows otherwise equal the originals
in every field except pe_value, engine_version, data_bundle, computed_at
and run_id (key order preserved).

## New-bundle run notes

* Runs (2026-10-06, EDT): cbo_free_joins, pwbm_ss_elimination and
  jct_obbba_provision4 at 12:04–12:22. The first cpsp_ctc_2024 attempt ran
  under memory pressure from a concurrent job (one simulation took 31 min)
  and its process was killed before it wrote anything; cpsp_ctc_2024,
  urban_subgroup_counts and tpc_t25_0209_t26_0029 were rerun at
  13:58–15:06. Peak RSS per simulation: ~40 GB (CY2026 tax runs) to ~84 GB
  (CPSP CY2024 poverty runs).
* Independent cross-check: where the construction is the same, the new
  urban rows equal the other session's `platform-grid-2024` results on the
  same bundle bit for bit (SNAP eligibility by subgroup, WIC eligibility
  and WIC eligible-minus-participants; e.g. WIC age_0thr3 = 7,017,855.898).
* Largest moves: SNAP (CY2026 total +10.3%, participants +6.5%, average
  benefit +3.5%; CY2024 eligibility by subgroup +0.9% to +16.8%) and CPSP
  child SPM poverty (-0.4 to -1.2 pp in every world; TCJA world under-18
  16.77% -> 15.61%). SSI, TANF-demographic and housing eligibility counts
  are unchanged; revenue rows move by at most 0.24%.

## Rerun

```
uv venv .venv-pe501 --python 3.12
uv pip install --python .venv-pe501/bin/python "policyengine[us]==5.0.1" "spm-calculator==0.3.1"
.venv-pe501/bin/python pipeline/campaign_us/run.py all --out pipeline/campaign_us/runs/old-us-5.0.1
.venv-pe/bin/python pipeline/campaign_us/run.py all --out sources/campaign-20261006/us \\
    --require-reproduced pipeline/campaign_us/runs/old-us-5.0.1
.venv-pe/bin/python pipeline/campaign_us/validate.py --old pipeline/campaign_us/runs/old-us-5.0.1 \\
    --new sources/campaign-20261006/us --md pipeline/campaign_us/VALIDATION.md
```
"""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--old", type=Path, required=True)
    ap.add_argument("--new", type=Path)
    ap.add_argument("--md", type=Path)
    ap.add_argument(
        "--preamble", type=Path, help="markdown file prepended to the table"
    )
    args = ap.parse_args()
    rows, summary = table(args.old, args.new)
    print(json.dumps(summary, indent=1))
    for r in rows:
        if not r["reproduced_ok"]:
            print(
                "NOT REPRODUCED",
                r["family"],
                r["row"],
                r["label"],
                r["original"],
                r["reproduced"],
                f"{r['rel_diff']:+.3e}",
            )
    if args.md:
        pre = args.preamble.read_text() if args.preamble else PREAMBLE
        args.md.write_text(markdown(rows, summary, pre))


if __name__ == "__main__":
    main()
