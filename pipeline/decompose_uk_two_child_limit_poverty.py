"""Decompose the September and October two-child limit poverty estimates.

PolicyEngine published two figures for the children lifted from relative
poverty after housing costs in 2029-30 by removing the two-child limit:
about 253,000 (scorecard's 25 September 2026 run, results/uk/ab2025/
ab2025__uc_child_element_remove_two_child_limit_2029.json: Populace UK 2023
on policyengine-uk 2.89.2, under-18s, the line held at the with-limit
world's median) and about 548,000 (the 23 October 2026 docs page,
PolicyEngine/policyengine-uk#1724: Microcosm UK 2024-25 on policyengine-uk
2.148.3, HBAI dependent children, each world's own median). This script
measures what moves the number between them.

Inputs, all from pipeline/compute_uk_two_child_limit_poverty.py:
    diagnostics/<data>_uk<engine>.json  a bare Microsimulation of the
        with-limit and current-law worlds in 2029 for every data x engine
        cell that runs (Populace UK 2023, Microcosm UK 2024-25; 2.89.2,
        2.132.6, 2.148.3)
    <pair_id>.json  the certified-pair run (managed route), whose 2029
        children count is the value attached to the benchmarks

Every cell gives the lifted count for two child concepts (under_18:
is_child; children: is_hbai_dependent_child, absent on 2.89.2) and two
lines (relative_fixed_at_with_limit; relative_moving, each world's own
median). The path holds everything but one factor fixed at each step, in
the order the factors changed:

    published September value (pe.py 5.0.2 managed route)
    1 route     the same pair through a bare Microsimulation
    2 engine    2.89.2 -> 2.132.6 on Populace
    3 data      Populace -> Microcosm on 2.132.6
    4 children  under-18s -> HBAI dependent children (Microcosm, 2.132.6)
    5 line      fixed -> each world's own median (= the certified pair)
    6 engine    2.132.6 -> 2.148.3 on Microcosm (= the docs page's figure)

Steps 2 and 3 are path-dependent; where the Microcosm x 2.89.2 cell runs,
the other order (data first) is reported beside them. A cell that fails to
run is recorded with its error, never interpolated.

Checks (any failure raises): the bare certified-pair cell equals the
managed run (differential: the managed route adds nothing to these
counts); the steps sum to the difference between the end points.

    PYTHONPATH=. python pipeline/decompose_uk_two_child_limit_poverty.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIR = ROOT / "results" / "uk" / "two_child_limit_poverty"
SEPT = (
    ROOT
    / "results"
    / "uk"
    / "ab2025"
    / "ab2025__uc_child_element_remove_two_child_limit_2029.json"
)
PAIR = ROOT / "data" / "uk" / "two_child_limit_poverty" / "certified_pair.json"
YEAR = "2029"
CELLS = {
    ("populace", "2.89.2"): "populace_uk2.89.2",
    ("populace", "2.132.6"): "populace_uk2.132.6",
    ("populace", "2.148.3"): "populace_uk2.148.3",
    ("microcosm", "2.89.2"): "microcosm_uk2.89.2",
    ("microcosm", "2.132.6"): "microcosm_uk2.132.6",
    ("microcosm", "2.148.3"): "microcosm_uk2.148.3",
}
DATA_LABEL = {
    "populace": "Populace UK 2023 (populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z)",
    "microcosm": "Microcosm UK 2024-25 (microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71)",
}
FAILED = DIR / "diagnostics" / "FAILED.json"
TOLERANCE = 1.0  # one weighted child


def lifted(art: dict, basis: str, line: str, group: str) -> float | None:
    wl = art["worlds"]["with_limit"]["years"][YEAR]["below"][basis][line][group]
    cl = art["worlds"]["current_law"]["years"][YEAR]["below"][basis][line][group]
    return None if wl is None or cl is None else wl - cl


def money(art: dict) -> dict:
    wl = art["worlds"]["with_limit"]["years"][YEAR]
    cl = art["worlds"]["current_law"]["years"][YEAR]
    d = {k: cl["sums_gbp"][k] - wl["sums_gbp"][k] for k in cl["sums_gbp"]}
    return {
        "exchequer_cost_gbp": d["gov_spending"] - d["gov_tax"],
        "universal_credit_change_gbp": d["universal_credit"],
        "limit_affected_children": wl["limit_affected_children"],
        "limit_gb": wl["limit_gb"],
        "children_population": wl["population"]["children"],
        "under_18_population": wl["population"]["under_18"],
    }


def cell_summary(art: dict) -> dict:
    out = {"installed": art["installed"], "route": art["route"]}
    for basis in ("ahc", "bhc"):
        out[basis] = {
            line: {
                group: lifted(art, basis, line, group)
                for group in ("under_18", "children")
            }
            for line in ("relative_fixed_at_with_limit", "relative_moving")
        }
    out["money"] = money(art)
    return out


def sept_published() -> dict:
    s = json.loads(SEPT.read_text())["poverty"]
    out = {}
    for basis in ("ahc", "bhc"):
        out[basis] = {
            "relative_fixed_at_with_limit": {
                "under_18": s[
                    f"relative_60_median_fixed_at_baseline_{basis}__baseline"
                ]["children"]
                - s[f"relative_60_median_fixed_at_baseline_{basis}__reform"][
                    "children"
                ],
                "children": None,
            },
            "relative_moving": {
                "under_18": s[f"relative_60_median_moving_{basis}__baseline"][
                    "children"
                ]
                - s[f"relative_60_median_moving_{basis}__reform"]["children"],
                "children": None,
            },
        }
    return out


def main() -> int:
    pair = json.loads(PAIR.read_text())
    certified = json.loads((DIR / f"{pair['pair_id']}.json").read_text())
    failed = json.loads(FAILED.read_text()) if FAILED.exists() else {}
    cells, missing = {}, {}
    for (data, engine), label in CELLS.items():
        path = DIR / "diagnostics" / f"{label}.json"
        if path.exists():
            cells[label] = cell_summary(json.loads(path.read_text()))
        else:
            missing[label] = failed.get(label, "not run")
    cert = cell_summary(certified)
    sept = sept_published()

    # differential: bare certified-pair cell == managed run
    bare = cells["microcosm_uk2.132.6"]
    for basis in ("ahc", "bhc"):
        for line in ("relative_fixed_at_with_limit", "relative_moving"):
            for group in ("under_18", "children"):
                a, b = bare[basis][line][group], cert[basis][line][group]
                if abs(a - b) > TOLERANCE:
                    raise SystemExit(
                        f"managed and bare runs differ: {basis} {line} {group} {a} {b}"
                    )

    def v(label, basis, line, group):
        return cells[label][basis][line][group]

    steps, notes = {}, {}
    for basis in ("ahc", "bhc"):
        fixed, moving = "relative_fixed_at_with_limit", "relative_moving"
        points = [
            (
                "published September run (policyengine 5.0.2 managed route; Populace, 2.89.2, under-18s, fixed line)",
                sept[basis][fixed]["under_18"],
            ),
            (
                "1 route: the same pair through a bare Microsimulation",
                v("populace_uk2.89.2", basis, fixed, "under_18"),
            ),
            (
                "2 engine 2.89.2 -> 2.132.6 (Populace)",
                v("populace_uk2.132.6", basis, fixed, "under_18"),
            ),
            (
                "3 data Populace -> Microcosm (2.132.6)",
                v("microcosm_uk2.132.6", basis, fixed, "under_18"),
            ),
            (
                "4 children: under-18s -> HBAI dependent children",
                v("microcosm_uk2.132.6", basis, fixed, "children"),
            ),
            (
                "5 line: fixed -> each world's own median (= the certified pair)",
                v("microcosm_uk2.132.6", basis, moving, "children"),
            ),
            (
                "6 engine 2.132.6 -> 2.148.3 (Microcosm; the docs page's run)",
                v("microcosm_uk2.148.3", basis, moving, "children"),
            ),
        ]
        rows = []
        for i, (label, value) in enumerate(points):
            rows.append(
                {
                    "step": label,
                    "lifted": value,
                    "change": None if i == 0 else value - points[i - 1][1],
                }
            )
        total = points[-1][1] - points[0][1]
        if abs(sum(r["change"] for r in rows[1:]) - total) > TOLERANCE:
            raise SystemExit("steps do not sum to the end-point difference")
        alt = None
        if "microcosm_uk2.89.2" in cells:
            m289 = v("microcosm_uk2.89.2", basis, fixed, "under_18")
            alt = {
                "data first: Populace -> Microcosm on 2.89.2": m289
                - v("populace_uk2.89.2", basis, fixed, "under_18"),
                "then engine 2.89.2 -> 2.132.6 on Microcosm": v(
                    "microcosm_uk2.132.6", basis, fixed, "under_18"
                )
                - m289,
            }
        steps[basis] = {"path": rows, "other_order": alt, "total_change": total}
        r = {row["step"][:1]: row["change"] for row in rows[1:]}
        notes[basis] = (
            f"Against PolicyEngine's September 2026 result on these benchmarks ({rows[0]['lifted'] / 1e3:,.0f}k children "
            f"{basis.upper()}: Populace UK 2023, policyengine-uk 2.89.2, under-18s, line held at the with-limit median), "
            f"this run moves by: engine 2.89.2 to 2.132.6 {r['2'] / 1e3:+,.0f}k, data Populace to Microcosm "
            f"{r['3'] / 1e3:+,.0f}k, under-18s to HBAI dependent children {r['4'] / 1e3:+,.0f}k, fixed line to each "
            f"world's own median {r['5'] / 1e3:+,.0f}k (route {r['1'] / 1e3:+,.0f}k). policyengine-uk 2.148.3, the "
            f"docs page's engine, adds {r['6'] / 1e3:+,.0f}k. Measured: results/uk/two_child_limit_poverty/DECOMPOSITION.json."
        )
    out = {
        "kind": "uk_two_child_limit_poverty_decomposition",
        "year": "2029-30 (engine period 2029)",
        "quantity": "children lifted from relative poverty: with-limit world minus current law",
        "data": DATA_LABEL,
        "cells": cells,
        "missing_cells": missing,
        "certified": cert,
        "september_published": sept,
        "steps": steps,
        "notes": notes,
    }
    (DIR / "DECOMPOSITION.json").write_text(
        json.dumps(out, indent=1, sort_keys=True) + "\n"
    )
    (DIR / "DECOMPOSITION.md").write_text(markdown(out))
    print(json.dumps(steps, indent=1))
    return 0


def _fmt(x: float | None) -> str:
    return "n/a" if x is None else f"{x / 1e3:,.0f}k"


def _signed(x: float | None) -> str:
    return "" if x is None else f"{x / 1e3:+,.0f}k"


def markdown(d: dict) -> str:
    """DECOMPOSITION.md: the same numbers as DECOMPOSITION.json, for reading."""
    lines = [
        "# Two-child limit: from the September estimate to the October one",
        "",
        "Generated by `pipeline/decompose_uk_two_child_limit_poverty.py` from the",
        "runs in this folder; edit the script, not this file.",
        "",
        f"Quantity: {d['quantity']}, {d['year']}.",
        "",
    ]
    for basis in ("ahc", "bhc"):
        s = d["steps"][basis]
        lines += [
            f"## {basis.upper()}",
            "",
            "| Step | Children lifted | Change |",
            "|---|---:|---:|",
        ]
        for row in s["path"]:
            lines.append(
                f"| {row['step']} | {_fmt(row['lifted'])} | {_signed(row['change'])} |"
            )
        lines += ["", f"Total change: {_signed(s['total_change'])}.", ""]
        if s["other_order"]:
            lines += ["Engine and data in the other order (fixed line, under-18s):", ""]
            lines += [f"- {k}: {_signed(v)}" for k, v in s["other_order"].items()]
            lines.append("")
    lines += [
        "## Every cell (fixed line / own median; under-18s, HBAI dependent children)",
        "",
        "| Cell | AHC fixed, u18 | AHC own, u18 | AHC fixed, HBAI | AHC own, HBAI | Exchequer cost | Children without a child element (with limit) |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for label, c in sorted(d["cells"].items()):
        a = c["ahc"]
        lines.append(
            f"| {label} | {_fmt(a['relative_fixed_at_with_limit']['under_18'])} | "
            f"{_fmt(a['relative_moving']['under_18'])} | "
            f"{_fmt(a['relative_fixed_at_with_limit']['children'])} | "
            f"{_fmt(a['relative_moving']['children'])} | "
            f"£{c['money']['exchequer_cost_gbp'] / 1e9:.2f}bn | "
            f"{_fmt(c['money']['limit_affected_children'])} |"
        )
    if d["missing_cells"]:
        lines += ["", "Cells that did not run:", ""]
        lines += [f"- {k}: {v}" for k, v in sorted(d["missing_cells"].items())]
    lines += [
        "",
        "Data: " + "; ".join(f"{k} = {v}" for k, v in d["data"].items()) + ".",
        "",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    sys.exit(main())
