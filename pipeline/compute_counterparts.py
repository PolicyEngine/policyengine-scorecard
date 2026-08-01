"""SotSN counterpart metrics on the certified populace US artifact.

Three sequential runs via policyengine.py managed_microsimulation() (Build P):
  1. baseline        — as-served artifact (seeded + calibrated take-up)
  2. fullpart_all    — every stored takes_up_* flag True + would_claim_wic True
  3. fullpart_urban6 — only the flags matching Urban SotSN programs
                       (SNAP, SSI, TANF, housing, EITC, WIC gate)

Emits weighted COUNTS only (rates are derived downstream in
build_comparison.py so there is one source of arithmetic truth):
  data/pe/pe_metrics.json — {run, program, metric, subgroup, geography, value}
  data/pe/pe_meta.json    — bundle info + metadata of every variable used
                            (label, entity, documentation) + flag toggle logs,
                            so concept annotations trace to engine metadata.

Weighted aggregation rules (Max's binding constraints):
  - Microsimulation + microdf auto-weighting only; never touch weight arrays.
  - Cross-entity combinations always via calculate(..., map_to=...).
  - Subgroup/state cuts by BOOLEAN-ARRAY INDEXING of MicroSeries
    (series[np_mask].sum() preserves weights); products only between two
    same-entity MicroSeries. Never multiply a MicroSeries by a plain
    ndarray (risks silent unweighted fallback).
"""

import gc
import json
import time
import traceback
from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parent.parent / "data" / "pe"
OUT.mkdir(parents=True, exist_ok=True)
YEAR = 2024

t0 = time.time()


def log(msg):
    print(f"[{time.time() - t0:7.1f}s] {msg}", flush=True)


URBAN6_FLAGS = [
    "takes_up_snap_if_eligible",
    "takes_up_ssi_if_eligible",
    "takes_up_tanf_if_eligible",
    "takes_up_housing_assistance_if_eligible",
    "takes_up_eitc",
]
ALL_FLAGS = [
    "takes_up_aca_if_eligible",
    "takes_up_eitc",
    "takes_up_head_start_if_eligible",
    "takes_up_housing_assistance_if_eligible",
    "takes_up_medicaid_if_eligible",
    "takes_up_medicare_if_eligible",
    "takes_up_snap_if_eligible",
    "takes_up_ssi_if_eligible",
    "takes_up_tanf_if_eligible",
]
WIC_GATE = "would_claim_wic"

rows = []
meta = {"year": YEAR, "runs": {}, "variables": {}}


def emit(run, program, metric, subgroup, geo, value):
    rows.append(
        {
            "run": run,
            "program": program,
            "metric": metric,
            "subgroup": subgroup,
            "geography": geo,
            "value": float(value),
        }
    )


def record_var(vs, name):
    if name and name in vs and name not in meta["variables"]:
        v = vs[name]
        meta["variables"][name] = {
            "label": getattr(v, "label", None),
            "entity": v.entity.key,
            "definition_period": str(getattr(v, "definition_period", None)),
            "documentation": getattr(v, "documentation", None),
        }


def pick(vs, candidates):
    for c in candidates:
        if c in vs:
            return c
    return None


def build_sim(run_name, flags_true):
    """Fresh managed sim; set take-up inputs BEFORE any calculate."""
    import policyengine as pe

    sim = pe.us.managed_microsimulation()
    vs = sim.tax_benefit_system.variables
    run_meta = {"flags_set_true": [], "flag_means_after": {}}
    for f in flags_true:
        if f not in vs:
            run_meta.setdefault("flags_missing", []).append(f)
            log(f"  WARNING: flag {f} not in variables")
            continue
        entity = vs[f].entity.key
        n = sim.populations[entity].count
        arr = np.ones(n, dtype=bool)
        monthly = str(getattr(vs[f], "definition_period", "")).lower() in (
            "month", "monthly",
        )
        periods = (
            [f"{YEAR}-{m:02d}" for m in range(1, 13)] if monthly else [YEAR]
        )
        try:
            for p in periods:
                sim.set_input(f, p, arr)
            run_meta["flags_set_true"].append(
                f + (" (12 months)" if monthly else "")
            )
        except Exception as e:
            log(f"  set_input({f}) failed: {e}; trying eternity")
            try:
                sim.set_input(f, "eternity", arr)
                run_meta["flags_set_true"].append(f + " (eternity)")
            except Exception:
                log(f"  ERROR setting {f}:\n{traceback.format_exc(limit=2)}")
                run_meta.setdefault("flags_failed", []).append(f)
    for f in flags_true:
        if f in vs:
            try:
                monthly = str(
                    getattr(vs[f], "definition_period", "")
                ).lower() in ("month", "monthly")
                probe = f"{YEAR}-06" if monthly else YEAR
                run_meta["flag_means_after"][f] = float(
                    np.mean(
                        np.array(sim.calculate(f, probe).values, dtype=float)
                    )
                )
            except Exception:
                pass
    meta["runs"][run_name] = run_meta
    if flags_true:
        log(f"  flag means after set: {run_meta['flag_means_after']}")
    return sim, vs


def first_person_anchor_state(sim, entity, person_state):
    """State of each group-entity row via its first person member
    (household-enum projection to group entities crashes in core)."""
    pop = sim.populations[entity]
    row_of_person = np.asarray(pop.members_entity_id)
    first = pd.Series(person_state).groupby(pd.Series(row_of_person)).first()
    return first.reindex(np.arange(pop.count)).to_numpy().astype(str)


def cut_sum(series, np_mask):
    """Weighted sum of a MicroSeries under an optional numpy bool mask."""
    if np_mask is None:
        return float(series.sum())
    return float(series[np_mask].sum())


def analyze(run_name, flags_true):
    log(f"=== run {run_name}: constructing sim ===")
    sim, vs = build_sim(run_name, flags_true)
    log(f"=== run {run_name}: sim ready ===")

    if run_name == "baseline":
        meta["bundle"] = {
            k: str(v)
            for k, v in getattr(sim, "policyengine_bundle", {}).items()
        }

    # --- shared person-level frames (numpy masks; MicroSeries for values) ---
    age_ms = sim.calculate("age", YEAR)
    ones_p = age_ms >= -1  # bool MicroSeries of all persons (weighted ones)
    age = np.asarray(age_ms.values, dtype=float)
    person_state = np.array(
        sim.calculate("state_code", YEAR, map_to="person").values
    ).astype(str)
    states = sorted(set(person_state))
    state_np = {s: person_state == s for s in states}

    person_bands = {
        "age_0thr17": age < 18,
        "age_18plus": age >= 18,
        "age_0thr3": age < 4,
        "age_4thr5": (age >= 4) & (age < 6),
        "age_6thr17": (age >= 6) & (age < 18),
        "age_18thr24": (age >= 18) & (age < 25),
        "age_25thr59": (age >= 25) & (age < 60),
        "age_60thr64": (age >= 60) & (age < 65),
        "age_65plus": age >= 65,
    }
    wic_bands = {
        "age_0": age < 1,
        "age_1thr4": (age >= 1) & (age < 5),
        "age_0thr3": age < 4,
        "age_4": (age >= 4) & (age < 5),
    }

    # Optional demographic axes (probe; skip if absent from the artifact).
    demo_np = {}
    race_var = pick(vs, ["race"])
    if race_var:
        try:
            race = np.array(sim.calculate(race_var, YEAR).values).astype(str)
            record_var(vs, race_var)
            meta["race_categories_on_artifact"] = sorted(set(np.unique(race)))
            mapping = {
                "race_white": ["WHITE"],
                "race_black": ["BLACK"],
                "race_hispanic": ["HISPANIC"],
                "race_aapi": ["ASIAN", "AAPI", "ASIAN_PACIFIC"],
                "race_multi_other": ["OTHER", "MULTIPLE", "OTHER_RACE"],
            }
            for sub, cats in mapping.items():
                m = np.isin(race, cats)
                if m.any():
                    demo_np[sub] = m
        except Exception:
            log(f"race probe failed:\n{traceback.format_exc(limit=1)}")
    dis_var = pick(vs, ["is_disabled"])
    if dis_var:
        try:
            dis = np.array(
                sim.calculate(dis_var, YEAR).values, dtype=bool
            )
            record_var(vs, dis_var)
            demo_np["disability_yes"] = dis
            demo_np["disability_no"] = ~dis
        except Exception:
            log(f"disability probe failed:\n{traceback.format_exc(limit=1)}")

    def emit_cuts(program, metric, series, subs, universe=None):
        """Emit national + state values for each subgroup mask."""
        for sub, band in subs.items():
            base = None
            for m in (universe, band):
                if m is None:
                    continue
                base = m if base is None else (base & m)
            emit(
                run_name, program, metric, sub, "US", cut_sum(series, base)
            )
            for s in states:
                sm = state_np[s] if base is None else (base & state_np[s])
                emit(run_name, program, metric, sub, s, cut_sum(series, sm))

    def person_program(program, elig, part, universe=None, bands=None,
                       demo=True):
        subs = {"total": None}
        subs.update(bands if bands is not None else person_bands)
        if demo:
            subs.update(demo_np)
        if elig is not None:
            emit_cuts(program, "eligible_count", elig, subs, universe)
        if part is not None:
            emit_cuts(program, "participant_count", part, subs, universe)
        if elig is not None and part is not None:
            emit_cuts(
                program, "elig_participant_count", part * elig, subs, universe
            )

    # --- denominators ---
    emit_cuts("_persons", "count", ones_p, {"total": None, **person_bands})
    emit_cuts(
        "_children_0thr4", "count", ones_p,
        {"total": None, **wic_bands}, universe=(age < 5),
    )
    for entity, id_var, label in [
        ("household", "household_id", "_households"),
        ("tax_unit", "tax_unit_id", "_tax_units"),
        ("spm_unit", "spm_unit_id", "_spm_units"),
    ]:
        try:
            ones = sim.calculate(id_var, YEAR) >= 0
            st = first_person_anchor_state(sim, entity, person_state)
            emit(run_name, label, "count", "total", "US", cut_sum(ones, None))
            for s in states:
                emit(
                    run_name, label, "count", "total", s,
                    cut_sum(ones, st == s),
                )
        except Exception:
            log(f"denominator {label} failed:\n{traceback.format_exc(limit=1)}")
    log("denominators done")

    # --- SNAP (person concept; eligibility incl. BBCE) ---
    try:
        for v in ["is_snap_eligible", "snap"]:
            record_var(vs, v)
        elig = sim.calculate("is_snap_eligible", YEAR, map_to="person") > 0
        part = sim.calculate("snap", YEAR, map_to="person") > 0
        person_program("snap", elig, part)
        emit(
            run_name, "snap", "benefit_dollars", "total", "US",
            float(sim.calculate("snap", YEAR).sum()),
        )
        log("snap done")
    except Exception:
        log(f"snap failed:\n{traceback.format_exc(limit=1)}")

    # --- SSI (universe = adults 18+, Urban's concept; broad denominator) ---
    try:
        for v in ["ssi", "is_ssi_eligible"]:
            record_var(vs, v)
        ssi_amt = sim.calculate("ssi", YEAR)
        part = ssi_amt > 0
        elig_broad = sim.calculate("is_ssi_eligible", YEAR) > 0
        adult_bands = {
            k: v
            for k, v in person_bands.items()
            if k in ("age_18thr24", "age_25thr59", "age_60thr64", "age_65plus")
        }
        person_program(
            "ssi", elig_broad, part, universe=(age >= 18), bands=adult_bands
        )
        emit(
            run_name, "ssi", "participant_count_all_ages", "total", "US",
            cut_sum(part, None),
        )
        emit(
            run_name, "ssi", "benefit_dollars", "total", "US",
            float(ssi_amt.sum()),
        )
        log("ssi done")
    except Exception:
        log(f"ssi failed:\n{traceback.format_exc(limit=1)}")

    # --- TANF (person concept; eligibility = demographic-only, native) ---
    try:
        for v in ["tanf", "is_demographic_tanf_eligible"]:
            record_var(vs, v)
        elig = (
            sim.calculate(
                "is_demographic_tanf_eligible", YEAR, map_to="person"
            )
            > 0
        )
        part = sim.calculate("tanf", YEAR, map_to="person") > 0
        person_program("tanf", elig, part)
        emit(
            run_name, "tanf", "benefit_dollars", "total", "US",
            float(sim.calculate("tanf", YEAR).sum()),
        )
        log("tanf done")
    except Exception:
        log(f"tanf failed:\n{traceback.format_exc(limit=1)}")

    # --- WIC (universe = children 0-4; Urban's concept) ---
    try:
        for v in ["wic", "is_wic_eligible", WIC_GATE]:
            record_var(vs, v)
        wic_amt = sim.calculate("wic", YEAR)
        elig = sim.calculate("is_wic_eligible", YEAR) > 0
        part = wic_amt > 0
        person_program(
            "wic", elig, part, universe=(age < 5),
            bands=wic_bands,
        )
        emit(
            run_name, "wic", "benefit_dollars", "total", "US",
            float(wic_amt.sum()),
        )
        log("wic done")
    except Exception:
        log(f"wic failed:\n{traceback.format_exc(limit=1)}")

    # --- tax-unit programs: EITC, refundable CTC ---
    try:
        tu_state = first_person_anchor_state(sim, "tax_unit", person_state)
        tu_state_np = {s: tu_state == s for s in states}
        for prog, var in [("eitc", "eitc"), ("ctc_refund", "refundable_ctc")]:
            record_var(vs, var)
            amt = sim.calculate(var, YEAR)
            part = amt > 0
            emit(
                run_name, prog, "participant_count", "total", "US",
                cut_sum(part, None),
            )
            emit(
                run_name, prog, "benefit_dollars", "total", "US",
                float(amt.sum()),
            )
            for s in states:
                emit(
                    run_name, prog, "participant_count", "total", s,
                    cut_sum(part, tu_state_np[s]),
                )
        cc_var = pick(
            vs, ["eitc_child_count", "count_eitc_qualifying_children"]
        )
        if cc_var:
            record_var(vs, cc_var)
            cc = np.asarray(sim.calculate(cc_var, YEAR).values, dtype=float)
            eitc_part = sim.calculate("eitc", YEAR) > 0
            emit(
                run_name, "eitc", "participant_count", "age_child", "US",
                cut_sum(eitc_part, cc > 0),
            )
            emit(
                run_name, "eitc", "participant_count", "age_nochild", "US",
                cut_sum(eitc_part, cc == 0),
            )
        log("eitc/ctc done")
    except Exception:
        log(f"eitc/ctc failed:\n{traceback.format_exc(limit=1)}")

    # --- Housing assistance (spm_unit; PE concept ≤80% AMI or recipient) ---
    try:
        for v in ["housing_assistance", "is_eligible_for_housing_assistance"]:
            record_var(vs, v)
        su_state = first_person_anchor_state(sim, "spm_unit", person_state)
        su_state_np = {s: su_state == s for s in states}
        elig = sim.calculate("is_eligible_for_housing_assistance", YEAR) > 0
        amt = sim.calculate("housing_assistance", YEAR)
        part = amt > 0
        both = part * elig
        for metric, series in [
            ("eligible_count", elig),
            ("participant_count", part),
            ("elig_participant_count", both),
        ]:
            emit(
                run_name, "housing", metric, "total", "US",
                cut_sum(series, None),
            )
            for s in states:
                emit(
                    run_name, "housing", metric, "total", s,
                    cut_sum(series, su_state_np[s]),
                )
        emit(
            run_name, "housing", "benefit_dollars", "total", "US",
            float(amt.sum()),
        )
        log("housing done")
    except Exception:
        log(f"housing failed:\n{traceback.format_exc(limit=1)}")

    # --- SPM poverty (persons; total + child) ---
    try:
        pov_var = pick(vs, ["spm_unit_is_in_spm_poverty", "in_poverty"])
        record_var(vs, pov_var)
        poor = sim.calculate(pov_var, YEAR, map_to="person") > 0
        for sub, m in [("total", None), ("child", age < 18)]:
            emit(
                run_name, "_poverty", "poor_count", sub, "US",
                cut_sum(poor, m),
            )
            emit(
                run_name, "_poverty", "population", sub, "US",
                cut_sum(ones_p, m),
            )
            for s in states:
                sm = state_np[s] if m is None else (m & state_np[s])
                emit(
                    run_name, "_poverty", "poor_count", sub, s,
                    cut_sum(poor, sm),
                )
                emit(
                    run_name, "_poverty", "population", sub, s,
                    cut_sum(ones_p, sm),
                )
        log(f"poverty done (var={pov_var})")
    except Exception:
        log(f"poverty failed:\n{traceback.format_exc(limit=1)}")

    log(f"=== run {run_name} complete: {len(rows)} cumulative rows ===")
    del sim
    gc.collect()


def main():
    import sys

    run_specs = {
        "baseline": [],
        "fullpart_all": ALL_FLAGS + [WIC_GATE],
        "fullpart_urban6": URBAN6_FLAGS + [WIC_GATE],
    }
    selected = sys.argv[1].split(",") if len(sys.argv) > 1 else list(run_specs)

    # Merge with prior output when re-running a subset of runs.
    metrics_path = OUT / "pe_metrics.json"
    meta_path = OUT / "pe_meta.json"
    if metrics_path.exists() and set(selected) != set(run_specs):
        prior = json.loads(metrics_path.read_text())
        rows.extend(r for r in prior if r["run"] not in selected)
        if meta_path.exists():
            prior_meta = json.loads(meta_path.read_text())
            meta["variables"].update(prior_meta.get("variables", {}))
            for k, v in prior_meta.get("runs", {}).items():
                if k not in selected:
                    meta["runs"][k] = v
            for k in ("bundle", "race_categories_on_artifact"):
                if k in prior_meta:
                    meta.setdefault(k, prior_meta[k])
        log(f"merging: kept {len(rows)} prior rows from other runs")

    for name in selected:
        analyze(name, run_specs[name])

    metrics_path.write_text(json.dumps(rows))
    meta_path.write_text(json.dumps(meta, indent=2))
    log(f"DONE: {len(rows)} rows -> {OUT}")


if __name__ == "__main__":
    main()
