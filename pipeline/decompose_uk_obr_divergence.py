"""Decompose the OBR costings divergences into named components (#59).

The UK sibling of the Yale-TPC divergence decomposition (#30): each
measure x FY comparison row from the mode-2 lane (PR #56,
results/uk/obr_costings/COMPARISON.csv) is decomposed into signed GBP
components from the axes registry (data/uk/obr_divergence_axes.json),
with the arithmetic identity

    gap = PE - OBR = sum(sized components) + residual

holding exactly by construction. Honesty rules, enforced here and by
tests/test_obr_divergence_decomposition.py:

  - A sized component must carry a per-FY GBP value with verbatim
    primary-source provenance in the registry; the pipeline never
    invents or defaults a size.
  - Any unsized component on a measure forces
    ``decomposition_status: partial`` and the remainder is labelled
    ``residual_plus_unsized`` — a partial decomposition never presents
    as explained.
  - ``explained_share`` is emitted only when every non-residual
    component is sized.

Engine-free: pure csv/json arithmetic, runnable anywhere. The
comparison CSV is #56's output consumed by path (no shared commits);
until that PR merges, point --comparison at a checkout of its branch
or use the committed fixture
(tests/fixtures/obr_costings_comparison_20260817.csv, a verbatim copy
of origin/obr-costings-mode2:results/uk/obr_costings/COMPARISON.csv).

Row selection per (measure, FY): the registry names the row_kind the
decomposition targets (total > mapped_head_total > head); a measure
whose named row_kind is absent from the CSV errors rather than
silently decomposing a different scope.

Usage:
    python pipeline/decompose_uk_obr_divergence.py \
        [--comparison results/uk/obr_costings/COMPARISON.csv] \
        [--registry data/uk/obr_divergence_axes.json] \
        [--out results/uk/obr_divergence]
"""

import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

AXES = (
    "behavioural_adjustment",
    "baseline_vintage",
    "cy_proxies_fy",
    "head_scope",
    "construction_scope",
    "residual",
)


def load_registry(path):
    reg = json.loads(Path(path).read_text())
    for key, m in reg["measures"].items():
        for c in m["components"]:
            if c["axis"] not in AXES:
                raise ValueError(f"{key}/{c['name']}: unknown axis {c['axis']}")
            if c["status"] == "sized":
                if not c.get("values_gbp"):
                    raise ValueError(f"{key}/{c['name']}: sized but no values_gbp")
                if not c.get("provenance"):
                    raise ValueError(f"{key}/{c['name']}: sized but no provenance")
            elif c["status"] == "unsized":
                if not c.get("recipe"):
                    raise ValueError(f"{key}/{c['name']}: unsized but no recipe")
            else:
                raise ValueError(f"{key}/{c['name']}: bad status {c['status']}")
    return reg


def comparison_rows(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def decompose(registry, rows):
    """One decomposition record per (measure, FY) in the registry."""
    out = []
    for key, m in registry["measures"].items():
        kind = m["comparison_row_kind"]
        picked = [r for r in rows if r["measure_key"] == key and r["row_kind"] == kind]
        if not picked:
            raise ValueError(f"{key}: no comparison row of kind {kind}")
        for r in picked:
            fy = r["fy"]
            obr = float(r["obr_value_gbp"])
            pe = float(r["pe_value_gbp"])
            gap = pe - obr
            sized, unsized = [], []
            for c in m["components"]:
                if c["status"] == "sized" and fy in c["values_gbp"]:
                    sized.append(
                        {
                            "name": c["name"],
                            "axis": c["axis"],
                            "value_gbp": float(c["values_gbp"][fy]),
                            "provenance": c["provenance"],
                        }
                    )
                else:
                    unsized.append(
                        {
                            "name": c["name"],
                            "axis": c["axis"],
                            "recipe": c.get(
                                "recipe", "sized for other FYs only; extend values_gbp"
                            ),
                        }
                    )
            residual = gap - sum(c["value_gbp"] for c in sized)
            partial = bool(unsized)
            rec = {
                "measure_key": key,
                "fy": fy,
                "row_kind": kind,
                "obr_value_gbp": obr,
                "pe_value_gbp": pe,
                "gap_gbp": gap,
                "sized_components": sized,
                "unsized_components": unsized,
                "residual_label": "residual_plus_unsized" if partial else "residual",
                "residual_gbp": residual,
                "decomposition_status": "partial" if partial else "complete",
            }
            if not partial and gap:
                rec["explained_share"] = 1.0 - residual / gap
            out.append(rec)
    return out


def render_md(records):
    lines = [
        "# OBR costings divergence decomposition (#59)",
        "",
        "gap = PE − OBR (GBP bn, announced-measure orientation). Signed components",
        "sum with the residual to the gap exactly. `partial` rows carry unsized",
        "components: their remainder is `residual_plus_unsized`, not an explanation.",
        "",
        "| Measure | FY | Gap | Component | Value | Status |",
        "|---|---|---:|---|---:|---|",
    ]
    for r in records:
        first = True
        for c in r["sized_components"]:
            lines.append(
                f"| {r['measure_key'] if first else ''} | {r['fy'] if first else ''} "
                f"| {r['gap_gbp'] / 1e9:.3f} | {c['name']} ({c['axis']}) "
                f"| {c['value_gbp'] / 1e9:+.3f} | sized |"
            )
            first = False
        for c in r["unsized_components"]:
            lines.append(
                f"| {r['measure_key'] if first else ''} | {r['fy'] if first else ''} "
                f"| {r['gap_gbp'] / 1e9:.3f} | {c['name']} ({c['axis']}) |  | unsized |"
            )
            first = False
        lines.append(
            f"| {r['measure_key'] if first else ''} | {r['fy'] if first else ''} "
            f"| {r['gap_gbp'] / 1e9:.3f} | **{r['residual_label']}** "
            f"| {r['residual_gbp'] / 1e9:+.3f} | {r['decomposition_status']} |"
        )
    return "\n".join(lines) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--comparison", default=str(ROOT / "results/uk/obr_costings/COMPARISON.csv")
    )
    ap.add_argument(
        "--registry", default=str(ROOT / "data/uk/obr_divergence_axes.json")
    )
    ap.add_argument("--out", default=str(ROOT / "results/uk/obr_divergence"))
    args = ap.parse_args(argv)

    registry = load_registry(args.registry)
    records = decompose(registry, comparison_rows(args.comparison))
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "DECOMPOSITION.json").write_text(json.dumps(records, indent=1))
    (out / "DECOMPOSITION.md").write_text(render_md(records))
    partial = sum(r["decomposition_status"] == "partial" for r in records)
    print(f"{len(records)} decompositions ({partial} partial) -> {out}")
    return records


if __name__ == "__main__":
    main()
