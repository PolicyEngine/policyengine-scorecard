"""Decompose the OBR costings divergences into named components (#59).

The UK sibling of the Yale-TPC divergence decomposition (#30): each
measure x FY comparison row from the mode-2 lane (PR #56,
results/uk/obr_costings/COMPARISON.csv) is decomposed into signed GBP
components from the axes registry (data/uk/obr_divergence_axes.json).
``residual = gap - sum(valued components)`` holds by construction —
that identity is bookkeeping, NOT evidence the decomposition is right,
so the record carries diagnostics that can actually fail:

  - Recipes are EXECUTED, not asserted. A `computed` component names an
    executor that the pipeline runs against the comparison rows on every
    run, and it may not carry a hard-coded value at all; the derivation
    it produces states the assumption it rests on. The adjacent-CY 3:1
    interpolation is the first: it sizes the cy_proxies_fy axis for both
    focal March-2026 divergences from the fixture's own runs, which is
    what turned two "residual = the entire gap" records into decompositions
    with something actually attributed. Where the adjacent run is absent
    the component stays unsized and says which run is missing.

  - Every valued component is classified by direction against the gap:
    ``explains_gap`` (same sign — the axis accounts for part of the
    observed divergence) or ``masks_gap`` (opposite sign — the axis
    HIDES part of a larger like-for-like disagreement). A record with
    any masking component carries ``divergence_understated: true`` and
    ``like_for_like_gap_gbp`` (the gap with masking axes removed): the
    observed gap understates the model disagreement, and the artifact
    says so instead of presenting the masking terms as explanation.
  - ``residual_exceeds_gap`` flags |residual| > |gap|.
  - Components that share a channel are not additive. A component may
    declare ``overlaps``; when two overlapping components are both
    valued the record says so and withholds ``explained_share``.
  - ``explained_share`` is emitted only for a complete decomposition (no
    unsized components) with no masking components, no overlapping
    components, a nonzero gap — and a share that is actually a share.
    A value outside [0, 1] is withheld with a stated reason: "150%
    explained" is a residual of the opposite sign wearing an
    explanation's name.

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

# `residual` is deliberately NOT an axis. It was both a registry axis and
# the quantity the pipeline computes, so a component could be filed under
# the name of the thing it was supposed to be explaining — and the
# identity would still close.
AXES = (
    "behavioural_adjustment",
    "baseline_vintage",
    "cy_proxies_fy",
    "head_scope",
    "construction_scope",
    # A term that bundles two axes and cannot be attributed to either.
    # The employer-NICs "behavioural" component was one: it subtracts a
    # FULL-MEASURE static total from a MAPPED-HEAD post-behavioural
    # subtotal, so it carries a scope difference and a behavioural
    # response together. Filing it as behavioural_adjustment claimed an
    # attribution the arithmetic does not support.
    "joint_behavioural_and_scope",
)

# Recipes the pipeline EXECUTES, rather than components that assert a
# number. An executed component's value is recomputed from the comparison
# rows on every run, so it cannot drift from the data it claims to be
# derived from — the failure mode a hard-coded values_gbp has.
EXECUTORS = {}


def executor(name):
    def register(fn):
        EXECUTORS[name] = fn
        return fn

    return register


# FY Y-(Y+1) accrues nine months of CY Y and three of CY Y+1, so an
# equal-accrual interpolation weights them 3:1. The PE leg proxies the FY
# with the single CY-Y run, so the axis component is the difference:
#
#     (0.75*PE_Y + 0.25*PE_{Y+1}) - PE_Y  =  0.25 * (PE_{Y+1} - PE_Y)
#
# EQUAL ACCRUAL IS AN ASSUMPTION, not an engine fact: a measure whose
# effect is concentrated in part of the year (a threshold that bites at
# uprating, a rate change effective in April) does not accrue evenly, and
# then 3:1 is an approximation whose error is unbounded. It is stated on
# every value this executor produces. Note also that the FY label keys the
# END year in claim identity (FY2026-27 -> period 2027) while the PE run's
# calendar year is the START year — the two are different keys for the
# same span and the executor reads the CSV's own `year` column rather than
# inferring either from the other.
_CY_CONFOUNDS = (
    "Assumes EQUAL ACCRUAL across the financial year. A measure whose "
    "effect concentrates in part of the year (a threshold biting at "
    "April uprating, a mid-year rate change) does not accrue evenly and "
    "the 3:1 weighting is then an approximation with unbounded error. "
    "The FY label keys the END year in claim identity while the PE run's "
    "calendar year is the START year; both are read from the comparison "
    "row, never inferred from each other."
)


@executor("cy_3_to_1_from_adjacent_runs")
def _cy_proxies_fy(component, row, rows_by_measure_year):
    """Execute the adjacent-CY interpolation from the comparison rows."""
    year = int(row["year"])
    nxt = rows_by_measure_year.get((row["measure_key"], row["row_kind"], year + 1))
    if nxt is None:
        return None, (
            f"no adjacent CY{year + 1} comparison row for this measure and "
            "row_kind, so the 3:1 interpolation cannot be executed"
        )
    value = 0.25 * (float(nxt["pe_value_gbp"]) - float(row["pe_value_gbp"]))
    derivation = (
        f"0.25 * (PE CY{year + 1} - PE CY{year}) = 0.25 * "
        f"({float(nxt['pe_value_gbp'])} - {float(row['pe_value_gbp'])}) = {value}. "
        f"{_CY_CONFOUNDS}"
    )
    return value, derivation


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
            elif c["status"] == "computed":
                if c.get("values_gbp"):
                    raise ValueError(
                        f"{key}/{c['name']}: a computed component is EXECUTED "
                        "from the comparison rows; a hard-coded values_gbp "
                        "would let it drift from the data it claims"
                    )
                if c.get("executor") not in EXECUTORS:
                    raise ValueError(
                        f"{key}/{c['name']}: unknown executor "
                        f"{c.get('executor')!r} (known: {sorted(EXECUTORS)})"
                    )
                if not c.get("recipe"):
                    raise ValueError(f"{key}/{c['name']}: computed but no recipe")
            elif c["status"] == "unsized":
                if not c.get("recipe"):
                    raise ValueError(f"{key}/{c['name']}: unsized but no recipe")
            else:
                raise ValueError(f"{key}/{c['name']}: bad status {c['status']}")
            # A component that overlaps another names it, so the pipeline
            # can refuse to present two terms that share a channel as an
            # additive explanation.
            for other in c.get("overlaps", []):
                if other not in {x["name"] for x in m["components"]}:
                    raise ValueError(
                        f"{key}/{c['name']}: overlaps unknown component {other!r}"
                    )
    return reg


def comparison_rows(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def decompose(registry, rows):
    """One decomposition record per (measure, FY) in the registry."""
    out = []
    by_measure_year = {
        (r["measure_key"], r["row_kind"], int(r["year"])): r for r in rows
    }
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
                if c["status"] == "computed":
                    value, note = EXECUTORS[c["executor"]](c, r, by_measure_year)
                    if value is None:
                        unsized.append(
                            {
                                "name": c["name"],
                                "axis": c["axis"],
                                "recipe": f"{c['recipe']} NOT EXECUTED: {note}",
                            }
                        )
                        continue
                    valued.append(
                        {
                            "name": c["name"],
                            "axis": c["axis"],
                            "status": "computed",
                            "value_gbp": value,
                            "direction": (
                                "explains_gap"
                                if gap and (value > 0) == (gap > 0)
                                else "masks_gap"
                            ),
                            "provenance": (
                                "EXECUTED by this pipeline from the comparison "
                                f"rows on this run (executor {c['executor']})"
                            ),
                            "derivation": note,
                            "overlaps": c.get("overlaps", []),
                        }
                    )
                    continue
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
                    entry["overlaps"] = c.get("overlaps", [])
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
            # Components that share a channel are not additive: HICBC's
            # welfare_head_missing and its take-up behavioural axis are
            # the same £391m twice if both are ever valued.
            named = {c["name"] for c in valued}
            overlapping = sorted(
                {
                    f"{c['name']}~{o}"
                    for c in valued
                    for o in c.get("overlaps", [])
                    if o in named
                }
            )
            if overlapping:
                rec["overlapping_components"] = overlapping
            # explained_share is the ONE number a reader will quote, so it
            # is emitted only when it means something: a complete
            # decomposition, no masking terms, no overlapping terms, and a
            # share that is actually a share. The synthetic test used to
            # permit 1.5 — a "150% explained" gap, which is a residual of
            # the opposite sign wearing an explanation's name.
            if not partial and not masking and not overlapping and gap:
                share = 1.0 - residual / gap
                if 0.0 <= share <= 1.0:
                    rec["explained_share"] = share
                else:
                    rec["explained_share_withheld"] = (
                        f"computed share {share} is outside [0, 1]: the "
                        "components do not explain a fraction of this gap, "
                        "they over- or counter-shoot it"
                    )
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


LIVE_COMPARISON = ROOT / "results/uk/obr_costings/COMPARISON.csv"
FIXTURE_COMPARISON = ROOT / "tests/fixtures/obr_costings_comparison_20260817.csv"


def choose_comparison(explicit=None):
    """Which comparison CSV to decompose, and say which out loud.

    A clean invocation used to FileNotFoundError on #56's output, which
    does not exist on this branch — so the tool did not stand alone. It
    now falls back to the committed fixture and NAMES the fallback: a
    decomposition of a frozen snapshot must never read as a
    decomposition of live results.
    """
    if explicit is not None:
        return Path(explicit), "explicit"
    if LIVE_COMPARISON.exists():
        return LIVE_COMPARISON, "live"
    return FIXTURE_COMPARISON, "fixture"


def fixture_drift():
    """Whether the committed fixture still matches #56's live output.

    The fixture is a frozen copy, so #56's baseline fixes would NOT
    propagate to a decomposition built from it, silently. When both files
    exist the difference is reported rather than discovered later.
    """
    if not (LIVE_COMPARISON.exists() and FIXTURE_COMPARISON.exists()):
        return None
    import hashlib

    live = hashlib.sha256(LIVE_COMPARISON.read_bytes()).hexdigest()
    fixed = hashlib.sha256(FIXTURE_COMPARISON.read_bytes()).hexdigest()
    return None if live == fixed else {"live_sha256": live, "fixture_sha256": fixed}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--comparison", default=None)
    ap.add_argument(
        "--registry", default=str(ROOT / "data/uk/obr_divergence_axes.json")
    )
    ap.add_argument("--out", default=str(ROOT / "results/uk/obr_divergence"))
    args = ap.parse_args(argv)

    registry = load_registry(args.registry)
    comparison, provenance = choose_comparison(args.comparison)
    if provenance == "fixture":
        print(
            f"NOTE: {LIVE_COMPARISON} is absent (it is PR #56's output), so "
            f"this decomposition is of the FROZEN FIXTURE {comparison.name}. "
            "Its numbers are a snapshot, not live results."
        )
    drift = fixture_drift()
    if drift:
        print(
            "WARNING: the committed fixture no longer matches #56's live "
            f"COMPARISON.csv ({drift}); a fixture-based decomposition will "
            "not carry #56's later baseline fixes. Re-freeze the fixture."
        )
    records = decompose(registry, comparison_rows(comparison))
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "DECOMPOSITION.json").write_text(json.dumps(records, indent=1) + "\n")
    (out / "DECOMPOSITION.md").write_text(render_md(records))
    (out / "PROVENANCE.json").write_text(
        json.dumps(
            {
                "comparison": str(comparison),
                "comparison_provenance": provenance,
                "fixture_drift": drift,
                "records": len(records),
            },
            indent=1,
        )
        + "\n"
    )
    partial = sum(r["decomposition_status"] == "partial" for r in records)
    executed = sum(
        1 for r in records for c in r["valued_components"] if c["status"] == "computed"
    )
    print(
        f"{len(records)} decompositions ({partial} partial, {executed} executed "
        f"components) -> {out}"
    )
    return records


if __name__ == "__main__":
    main()
