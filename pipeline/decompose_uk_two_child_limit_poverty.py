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

Step 6 is then attributed to releases: diagnostics/bisect_microcosm_uk<v>_
core3.33.3.json runs the same two worlds at each policyengine-uk release
between 2.132.6 and 2.148.3 that the bisection reached, with
policyengine-core held at 3.33.3 (pipeline/modal_uk_two_child_limit_poverty.py
--release), so each change belongs to the model package; the 2.148.3 cell
on core 3.33.12 (the docs page's) against the same release on 3.33.3
measures the core upgrade on its own.

Checks (any failure raises): the bare certified-pair cell equals the
managed run (differential: the managed route adds nothing to these
counts); the steps sum to the difference between the end points; the
release changes sum to step 6 less the core change.

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
sys.path.insert(0, str(ROOT))
from pipeline.compute_uk_two_child_limit_poverty import DEFAULT_PAIR  # noqa: E402

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
# Every policyengine-uk release from 2.132.6 to 2.148.3, in release order
# (PyPI, read 2026-10-26).
RELEASES = (
    "2.132.6 2.133.0 2.134.0 2.134.1 2.134.2 2.134.3 2.134.4 2.134.5 2.134.6 "
    "2.134.7 2.134.8 2.134.9 2.135.0 2.135.1 2.135.2 2.135.3 2.135.4 2.135.5 "
    "2.135.6 2.135.7 2.136.0 2.136.1 2.137.0 2.137.1 2.138.0 2.139.0 2.139.1 "
    "2.139.2 2.139.3 2.139.4 2.139.5 2.140.0 2.140.1 2.141.0 2.141.1 2.141.2 "
    "2.141.3 2.141.4 2.141.5 2.141.6 2.141.7 2.141.8 2.141.9 2.141.10 2.141.11 "
    "2.141.12 2.142.0 2.143.0 2.144.0 2.145.0 2.145.1 2.145.2 2.146.0 2.146.1 "
    "2.146.2 2.146.3 2.146.4 2.146.5 2.146.6 2.147.0 2.147.1 2.147.2 2.148.0 "
    "2.148.1 2.148.2 2.148.3"
).split()
BISECT_CORE = "3.33.3"
# What each release that moves the count changed, from its section of
# policyengine-uk's CHANGELOG.md (a summary; the changelog is the record).
RELEASE_NOTES: dict[str, str] = {
    "2.134.5": "Pension contributions relief limited by relevant UK earnings; "
    "the annual allowance charge recalculated across bands.",
    "2.134.6": "The Universal Credit Act 2025 standard allowance uplifts for "
    "2027-28 to 2029-30 applied through their own uprating index.",
    "2.134.8": "Relieved pension contributions deducted from adjusted net "
    "income (Personal Allowance taper, High Income Child Benefit Charge).",
    "2.139.2": "Five fixes, among them group inputs assigned to the right "
    "benefit unit and household when dataset tables are not sorted by "
    "identifier, the savings starting-rate band and Scottish thresholds.",
    "2.139.5": "Universal Credit's higher disabled child addition separated "
    "from tax credits; Working Tax Credit conditions on one claimant; the "
    "Child Tax Credit family element limited to children born before 6 April "
    "2017; Child Benefit out of pensioner Council Tax Reduction income.",
    "2.141.6": "Fifteen input columns that declared an uprating index but "
    "stayed flat through 2030 now uprate (water and sewerage, housing "
    "service charges, salary-sacrifice pensions and others).",
    "2.145.1": "Additional State Pension and protected payments uprated by "
    "September CPI, not the full rate's triple-lock rise.",
    "2.146.3": "Universal Credit's LCWRA element, carer element and work "
    "allowance given on the claimants' own circumstances, not a "
    "dependant's.",
    "2.147.1": "HBAI income counts property income after finance costs "
    "(property_income_after_finance_costs), not the profit before them.",
    "2.148.2": "Benefits uprated by the previous September's CPI (#2533), "
    "with fixes to current_education's order dependence, the free TV "
    "licence and the Marriage Allowance reform switch.",
}


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


def release_attribution(cells: dict) -> dict:
    """Step 6 by release: each release the bisection ran, its counts and the
    change from the previous release that ran, naming any release between
    that did not run."""
    runs = {"2.132.6": DIR / "diagnostics" / "microcosm_uk2.132.6.json"}
    for path in (DIR / "diagnostics").glob("bisect_microcosm_uk*_core3.33.3.json"):
        art = json.loads(path.read_text())
        version = art["installed"]["policyengine-uk"]
        if (
            art["installed"]["policyengine-core"] != BISECT_CORE
            or path.name != f"bisect_microcosm_uk{version}_core3.33.3.json"
        ):
            raise SystemExit(
                f"{path.name}: not policyengine-uk {version} on core {BISECT_CORE}"
            )
        runs[version] = path
    if set(runs) - set(RELEASES):
        raise SystemExit(
            f"releases outside RELEASES: {sorted(set(runs) - set(RELEASES))}"
        )
    rows, prev = [], None
    for version in (v for v in RELEASES if v in runs):
        c = cell_summary(json.loads(runs[version].read_text()))
        row = {
            "release": version,
            "ahc": c["ahc"]["relative_moving"]["children"],
            "bhc": c["bhc"]["relative_moving"]["children"],
            "exchequer_cost_gbp": c["money"]["exchequer_cost_gbp"],
        }
        if prev is not None:
            row["from"] = prev["release"]
            row["releases_between_not_run"] = RELEASES[
                RELEASES.index(prev["release"]) + 1 : RELEASES.index(version)
            ]
            row["change_ahc"] = row["ahc"] - prev["ahc"]
            row["change_bhc"] = row["bhc"] - prev["bhc"]
            row["note"] = RELEASE_NOTES.get(version)
        rows.append(row)
        prev = row
    moving = {
        r["release"]
        for r in rows[1:]
        if abs(r["change_ahc"]) > TOLERANCE or abs(r["change_bhc"]) > TOLERANCE
    }
    if moving != set(RELEASE_NOTES):
        raise SystemExit(
            "RELEASE_NOTES must name exactly the releases that move a count: "
            f"{sorted(moving ^ set(RELEASE_NOTES))}"
        )
    if rows[-1]["release"] != "2.148.3":
        raise SystemExit("the bisection has no 2.148.3 cell on core 3.33.3")
    core = {
        basis: cells["microcosm_uk2.148.3"][basis]["relative_moving"]["children"]
        - rows[-1][basis]
        for basis in ("ahc", "bhc")
    }
    for basis in ("ahc", "bhc"):
        step6 = (
            cells["microcosm_uk2.148.3"][basis]["relative_moving"]["children"]
            - cells["microcosm_uk2.132.6"][basis]["relative_moving"]["children"]
        )
        by_release = sum(r[f"change_{basis}"] for r in rows[1:])
        if abs(by_release + core[basis] - step6) > TOLERANCE:
            raise SystemExit(f"{basis}: release changes do not sum to step 6")
    return {
        "core": BISECT_CORE,
        "releases": rows,
        "core_3.33.3_to_3.33.12_at_2.148.3": core,
    }


def main() -> int:
    certified = json.loads((DIR / f"{DEFAULT_PAIR}.json").read_text())
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
    releases = release_attribution(cells)
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
        largest = sorted(
            (row for row in releases["releases"][1:]),
            key=lambda row: -abs(row[f"change_{basis}"]),
        )[:3]
        notes[basis] = (
            f"Against PolicyEngine's September 2026 result on these benchmarks ({rows[0]['lifted'] / 1e3:,.0f}k children "
            f"{basis.upper()}: Populace UK 2023, policyengine-uk 2.89.2, under-18s, line held at the with-limit median), "
            f"this run moves by: engine 2.89.2 to 2.132.6 {r['2'] / 1e3:+,.0f}k, data Populace to Microcosm "
            f"{r['3'] / 1e3:+,.0f}k, under-18s to HBAI dependent children {r['4'] / 1e3:+,.0f}k, fixed line to each "
            f"world's own median {r['5'] / 1e3:+,.0f}k (route {r['1'] / 1e3:+,.0f}k). policyengine-uk 2.148.3, the "
            f"docs page's engine, adds {r['6'] / 1e3:+,.0f}k; the releases that move it most are "
            + ", ".join(
                f"{row['release']} {row[f'change_{basis}'] / 1e3:+,.0f}k"
                for row in largest
            )
            + " (DECOMPOSITION.md, step 6 by release). Measured: "
            "results/uk/two_child_limit_poverty/DECOMPOSITION.json."
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
        "engine_releases": releases,
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


def _fmt1(x: float) -> str:
    return f"{x / 1e3:,.1f}k"


def _signed1(x: float) -> str:
    return f"{x / 1e3:+,.1f}k"


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
    e = d["engine_releases"]
    lines += [
        "## Step 6 by release (Microcosm, HBAI dependent children, own median)",
        "",
        f"Each policyengine-uk release the bisection ran, on policyengine-core {e['core']}; "
        "only releases that move either count are listed. The last column "
        "summarises the release's section of policyengine-uk's CHANGELOG.md. A "
        "release can carry several changes; the bisection does not split one.",
        "",
        "| Release | From | AHC | Change | BHC | Change | Releases between not run | Changelog |",
        "|---|---|---:|---:|---:|---:|---|---|",
    ]
    for r in e["releases"][1:]:
        if abs(r["change_ahc"]) <= TOLERANCE and abs(r["change_bhc"]) <= TOLERANCE:
            continue
        lines.append(
            f"| {r['release']} | {r['from']} | {_fmt1(r['ahc'])} | {_signed1(r['change_ahc'])} | "
            f"{_fmt1(r['bhc'])} | {_signed1(r['change_bhc'])} | "
            f"{', '.join(r['releases_between_not_run']) or 'none'} | {r['note'] or ''} |"
        )
    core = e["core_3.33.3_to_3.33.12_at_2.148.3"]
    lines += [
        "",
        f"policyengine-core 3.33.3 to 3.33.12 at policyengine-uk 2.148.3: "
        f"AHC {_signed(core['ahc']) or '0'}, BHC {_signed(core['bhc']) or '0'}.",
        "",
    ]
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
