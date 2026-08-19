"""Decompose the OBR costings divergences into named components (#59).

The UK sibling of the Yale-TPC divergence decomposition (#30): each
measure x FY comparison row from the mode-2 lane (PR #56,
results/uk/obr_costings/COMPARISON.csv) is decomposed into signed GBP
components from the axes registry (data/uk/obr_divergence_axes.json).
``residual = gap - sum(valued components)`` holds by construction —
that identity is bookkeeping, NOT evidence the decomposition is right,
so the record carries diagnostics that can actually fail:

  - Every valued component is classified by direction against the gap:
    ``explains_gap`` (same sign — the axis accounts for part of the
    observed divergence) or ``masks_gap`` (opposite sign — the axis
    HIDES part of a larger like-for-like disagreement). A record with
    any masking component carries ``divergence_understated: true`` and
    ``like_for_like_gap_gbp`` (the gap with masking axes removed): the
    observed gap understates the model disagreement, and the artifact
    says so instead of presenting the masking terms as explanation.
  - ``residual_exceeds_gap`` flags |residual| > |gap|.
  - ``explained_share`` is emitted only for a complete decomposition
    (no unsized components) with NO masking components and a nonzero
    gap; it can never be produced by the identity alone.

Honesty rules on the registry side, enforced by load_registry and
tests/test_obr_divergence_decomposition.py:

  - ``sized`` = per-FY GBP values quoted VERBATIM from a fetched
    primary source (no arithmetic beyond unit scaling); a sized
    component must not carry a ``derivation``.
  - ``derived`` = values computed from quoted numbers; the derivation
    formula is mandatory and travels into the artifact, so a derived
    number can never present as a quoted one.
  - ``unsized`` = recipe only. Any unsized component forces
    ``decomposition_status: partial`` and the remainder is labelled
    ``residual_plus_unsized``.

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
                if c.get("derivation"):
                    raise ValueError(
                        f"{key}/{c['name']}: sized components are verbatim quotes; "
                        "a derivation means the status must be 'derived'"
                    )
            elif c["status"] == "derived":
                if not c.get("values_gbp"):
                    raise ValueError(f"{key}/{c['name']}: derived but no values_gbp")
                if not c.get("provenance"):
                    raise ValueError(f"{key}/{c['name']}: derived but no provenance")
                if not c.get("derivation"):
                    raise ValueError(
                        f"{key}/{c['name']}: derived but no derivation formula"
                    )
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
            valued, unsized = [], []
            for c in m["components"]:
                if c["status"] in ("sized", "derived") and fy in c["values_gbp"]:
                    value = float(c["values_gbp"][fy])
                    entry = {
                        "name": c["name"],
                        "axis": c["axis"],
                        "status": c["status"],
                        "value_gbp": value,
                        # a component whose sign matches the gap accounts
                        # for part of it; an opposite-signed one hides part
                        # of a larger like-for-like disagreement
                        "direction": (
                            "explains_gap"
                            if gap and (value > 0) == (gap > 0)
                            else "masks_gap"
                        ),
                        "provenance": c["provenance"],
                    }
                    if c["status"] == "derived":
                        entry["derivation"] = c["derivation"]
                    valued.append(entry)
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
            residual = gap - sum(c["value_gbp"] for c in valued)
            masking = [c for c in valued if c["direction"] == "masks_gap"]
            partial = bool(unsized)
            rec = {
                "measure_key": key,
                "fy": fy,
                "row_kind": kind,
                "obr_value_gbp": obr,
                "pe_value_gbp": pe,
                "gap_gbp": gap,
                "valued_components": valued,
                "unsized_components": unsized,
                "residual_label": "residual_plus_unsized" if partial else "residual",
                "residual_gbp": residual,
                "residual_exceeds_gap": abs(residual) > abs(gap),
                "divergence_understated": bool(masking),
                "decomposition_status": "partial" if partial else "complete",
            }
            if masking:
                # the gap with the masking axes stripped out: the
                # like-for-like disagreement the observed gap understates
                rec["like_for_like_gap_gbp"] = gap - sum(
                    c["value_gbp"] for c in masking
                )
            if not partial and not masking and gap:
                rec["explained_share"] = 1.0 - residual / gap
            out.append(rec)
    return out


def render_md(records):
    lines = [
        "# OBR costings divergence decomposition (#59)",
        "",
        "gap = PE − OBR (GBP bn, announced-measure orientation). The identity",
        "residual = gap − Σ(valued) is bookkeeping, not explanation. `masks_gap`",
        "components hide part of a larger like-for-like disagreement: those rows",
        "state the widened gap. `partial` rows carry unsized components: their",
        "remainder is `residual_plus_unsized`, not an explanation.",
        "",
        "| Measure | FY | Gap | Component | Value | Status | Direction |",
        "|---|---|---:|---|---:|---|---|",
    ]
    for r in records:
        first = True
        for c in r["valued_components"]:
            lines.append(
                f"| {r['measure_key'] if first else ''} | {r['fy'] if first else ''} "
                f"| {r['gap_gbp'] / 1e9:.3f} | {c['name']} ({c['axis']}) "
                f"| {c['value_gbp'] / 1e9:+.3f} | {c['status']} | {c['direction']} |"
            )
            first = False
        for c in r["unsized_components"]:
            lines.append(
                f"| {r['measure_key'] if first else ''} | {r['fy'] if first else ''} "
                f"| {r['gap_gbp'] / 1e9:.3f} | {c['name']} ({c['axis']}) "
                f"|  | unsized |  |"
            )
            first = False
        note = ""
        if r["divergence_understated"]:
            note = (
                f" — divergence understated; like-for-like gap "
                f"{r['like_for_like_gap_gbp'] / 1e9:+.3f}"
            )
        lines.append(
            f"| {r['measure_key'] if first else ''} | {r['fy'] if first else ''} "
            f"| {r['gap_gbp'] / 1e9:.3f} | **{r['residual_label']}**{note} "
            f"| {r['residual_gbp'] / 1e9:+.3f} | {r['decomposition_status']} |  |"
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
