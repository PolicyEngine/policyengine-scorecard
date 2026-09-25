"""PolicyEngine counterparts for the Autumn Budget 2025 measures (#136, tranche 3).

For every registry measure in `data/uk/ab2025_measures.json` the certified
engine can express (a `pe_reform_delta`, a `pe_baseline_modifier`, or a
package of such measures), run the managed policyengine-uk simulation on the
certified populace-uk bundle and write one artifact per (measure, year) with
the two worlds' aggregates: head variables, government tax and spending,
household net income, the income distribution by decile and vigintile
(person-weighted, fixed in the baseline world), poverty counts on the
moving relative line, the fixed relative line and the absolute line, and
the affected population. Values are weighted COUNTS and GBP SUMS; every
rate, mean and share is derived downstream (stage_uk_ab2025) from these.

Worlds. A measure the certified world already contains (`construction:
reversal_on_certified_world`) is scored as current law MINUS the
pre-Budget world PE executes by applying `pe_baseline_modifier`; a
measure or option not in the certified world is scored as current law
PLUS `pe_reform_delta` MINUS current law. `effect = reform - baseline`
in both cases, so a positive effect on a tax head is a yield and a
positive effect on a benefit head is a cost. A package
(`package_of_registry_measures`) composes its components' modifiers or
deltas into one world.

Offline and pinned. Hugging Face offline mode is forced before the
engine is imported; the cached artifact is hashed against
`data/uk/certified_bundle.json` before any simulation and again after
every one; the installed engine must be the bundle's declared version.
No digest, no run.

    PYTHONPATH=. .venv-pe289m/bin/python pipeline/compute_uk_ab2025.py --dry-run
    PYTHONPATH=. .venv-pe289m/bin/python pipeline/compute_uk_ab2025.py \\
        --measures ab2025__uc_child_element_remove_two_child_limit --years 2026
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.metadata
import json
import os
import re
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "data" / "uk" / "ab2025_measures.json"
CERTIFIED = ROOT / "data" / "uk" / "certified_bundle.json"
OUTPUT_DIR = ROOT / "results" / "uk" / "ab2025"
YEARS = (2026, 2027, 2028, 2029, 2030)
WINDOW_END = "2035-12-31"
# The distribution block: person-weighted groups of the BASELINE world's
# equivalised HBAI household net income, held fixed for the reform world.
INCOME_AXES = {
    "bhc": "equiv_hbai_household_net_income",
    "ahc": "equiv_hbai_household_net_income_ahc",
}
POVERTY_FLAGS = {
    "relative_60_median_moving": {
        "ahc": "in_relative_poverty_ahc",
        "bhc": "in_relative_poverty_bhc",
    },
    "absolute": {"ahc": "in_poverty_ahc", "bhc": "in_poverty_bhc"},
}
THRESHOLDS = (0.0, 0.01, 0.05)


def configure_offline() -> None:
    for k in ("HF_HUB_OFFLINE", "TRANSFORMERS_OFFLINE", "HF_DATASETS_OFFLINE"):
        os.environ[k] = "1"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_registry() -> dict[str, dict]:
    reg = json.loads(REGISTRY.read_text())
    return {m["measure_key"]: m for m in reg["measures"]}


# --- reform dictionaries -------------------------------------------------------


def _windows(value) -> list[tuple[str, object]]:
    """A registry value -> [(period, value)]. Scalars cover the whole run
    window; year-keyed maps cover each calendar year; date-keyed maps run
    from each date to the day before the next."""
    if not isinstance(value, dict):
        return [(f"{YEARS[0]}-01-01.{WINDOW_END}", value)]
    keys = sorted(value)
    out = []
    for i, k in enumerate(keys):
        if re.fullmatch(r"\d{4}", k):
            out.append((f"{k}-01-01.{k}-12-31", value[k]))
        elif re.fullmatch(r"\d{4}-\d{2}-\d{2}", k):
            if i + 1 < len(keys):
                nxt = dt.date.fromisoformat(keys[i + 1]) - dt.timedelta(days=1)
                end = nxt.isoformat()
            else:
                end = WINDOW_END
            out.append((f"{k}.{end}", value[k]))
        else:
            raise ValueError(f"unparseable period key {k!r}")
    return out


# A registry null means "no limit" (the pre-Budget salary-sacrifice cap, the
# two-child limit's child count under current law). policyengine-core has no
# infinity in a reform dict, so a null executes as this finite sentinel, and
# every artifact records where it was used.
NO_LIMIT = 1e100


def reform_dict(spec: dict) -> tuple[dict, list[str]]:
    """(policyengine-core reform dict, paths where a null executed as
    NO_LIMIT) from a registry parameter map."""
    out: dict = {}
    sentinels: list[str] = []
    for path, value in spec.items():
        windows = _windows(value)
        if any(v is None for _, v in windows):
            sentinels.append(path)
        out[path] = {period: (NO_LIMIT if v is None else v) for period, v in windows}
    return out, sentinels


def worlds_for(measure: dict, index: dict[str, dict]) -> dict:
    """{'construction', 'baseline_reform', 'reform_reform', 'components'}:
    the reform dicts the baseline and reform worlds execute (None = the
    certified world as served)."""
    key = measure["measure_key"]
    construction = str(measure.get("construction") or "")
    if construction.startswith("same_lever_as_"):
        target = construction.removeprefix("same_lever_as_")
        return {"alias_of": target}
    if construction == "package_of_registry_measures":
        comps = measure.get("package_of")
        if not isinstance(comps, list) or not comps:
            raise ValueError(f"{key}: package_of is not a list of measure keys")
        merged_mod: dict = {}
        merged_delta: dict = {}
        sentinels: list[str] = []
        for c in comps:
            w = worlds_for(index[c], index)
            if "alias_of" in w:
                w = worlds_for(index[w["alias_of"]], index)
            if w.get("baseline_reform"):
                merged_mod.update(w["baseline_reform"])
            if w.get("reform_reform"):
                merged_delta.update(w["reform_reform"])
            sentinels += w.get("sentinels", [])
        return {
            "construction": construction,
            "baseline_reform": merged_mod or None,
            "reform_reform": merged_delta or None,
            "components": comps,
            "sentinels": sorted(set(sentinels)),
        }
    modifier = measure.get("pe_baseline_modifier")
    delta = measure.get("pe_reform_delta")
    if construction == "reversal_on_certified_world":
        if not modifier:
            raise ValueError(f"{key}: reversal without pe_baseline_modifier")
        rd, sent = reform_dict(modifier)
        return {
            "construction": construction,
            "baseline_reform": rd,
            "reform_reform": None,
            "components": [key],
            "sentinels": sent,
        }
    if delta:
        rd, sent = reform_dict(delta)
        return {
            "construction": construction or "forward_delta_on_certified_world",
            "baseline_reform": None,
            "reform_reform": rd,
            "components": [key],
            "sentinels": sent,
        }
    raise ValueError(f"{key}: nothing to execute")


def computable(index: dict[str, dict]) -> dict[str, dict]:
    out = {}
    for key, m in index.items():
        if m["computability"] not in ("expressible", "partial"):
            continue
        try:
            out[key] = worlds_for(m, index)
        except ValueError:
            continue
    return out


# --- the certified world -------------------------------------------------------


def preflight() -> dict:
    configure_offline()
    import policyengine as pe
    from huggingface_hub import hf_hub_download

    cert = json.loads(CERTIFIED.read_text())
    bundle = dict(pe.uk.uk_latest.release_bundle)
    if bundle.get("certified_data_build_id") != cert["revision"]:
        raise SystemExit(
            f"managed harness serves {bundle.get('certified_data_build_id')}, the "
            f"certified bundle is {cert['revision']} — not the same world"
        )
    installed = importlib.metadata.version("policyengine-uk")
    want = next(
        s["specifier"].lstrip("=")
        for s in cert["compatible_model_packages"]
        if s["name"] == "policyengine-uk"
    )
    if installed != want:
        raise SystemExit(
            f"policyengine-uk {installed} installed; the bundle declares =={want}"
        )
    cached = Path(
        hf_hub_download(
            repo_id=cert["repo_id"],
            repo_type="dataset",
            filename=cert["artifact"],
            revision=cert["revision"],
            local_files_only=True,
        )
    )
    digest = sha256_file(cached)
    if digest != cert["sha256"]:
        raise SystemExit(
            f"cached artifact sha256 {digest} != certified {cert['sha256']}"
        )
    return {
        "artifact": cached,
        "sha256": digest,
        "revision": cert["revision"],
        "repo_id": cert["repo_id"],
        "engine_version": installed,
    }


def build_sim(reform: dict | None):
    import policyengine as pe

    return (
        pe.uk.managed_microsimulation()
        if reform is None
        else pe.uk.managed_microsimulation(reform=reform)
    )


# --- aggregates -----------------------------------------------------------------


def _arr(series) -> np.ndarray:
    return np.asarray(getattr(series, "values", series), dtype=float)


def _weighted_quantile_groups(x: np.ndarray, w: np.ndarray, n: int) -> np.ndarray:
    """Group index 1..n by weighted quantiles of x (weights w)."""
    order = np.argsort(x, kind="stable")
    cw = np.cumsum(w[order])
    cw = cw / cw[-1]
    ranks = np.minimum((cw * n).astype(int) + 1, n)
    groups = np.empty_like(ranks)
    groups[order] = ranks
    return groups


def _weighted_median(x: np.ndarray, w: np.ndarray) -> float:
    order = np.argsort(x, kind="stable")
    cw = np.cumsum(w[order])
    return float(x[order][np.searchsorted(cw, cw[-1] / 2.0)])


def household_frame(sim, year: int, head_variables: list[str]) -> dict:
    """Everything the distribution and poverty blocks need, at household
    level, for one world and year."""
    hni = sim.calculate("household_net_income", year, map_to="household")
    w = np.asarray(hni.weights, dtype=float)
    frame = {
        "weight": w,
        "people": _arr(
            sim.calculate("household_count_people", year, map_to="household")
        ),
        "children": _arr(sim.calculate("is_child", year, map_to="household")),
        "hni": _arr(hni),
        "equiv_bhc": _arr(sim.calculate(INCOME_AXES["bhc"], year, map_to="household")),
        "equiv_ahc": _arr(sim.calculate(INCOME_AXES["ahc"], year, map_to="household")),
        "gov_tax": _arr(sim.calculate("gov_tax", year, map_to="household")),
        "gov_spending": _arr(sim.calculate("gov_spending", year, map_to="household")),
        "heads": {
            v: _arr(sim.calculate(v, year, map_to="household")) for v in head_variables
        },
        "poverty": {},
    }
    for line, by_basis in POVERTY_FLAGS.items():
        for basis, var in by_basis.items():
            frame["poverty"][f"{line}_{basis}"] = _arr(
                sim.calculate(var, year, map_to="household")
            ).astype(bool)
    return frame


def totals(frame: dict) -> dict:
    w = frame["weight"]
    out = {
        "households": float(w.sum()),
        "people": float((w * frame["people"]).sum()),
        "children": float((w * frame["children"]).sum()),
        "household_net_income": float((w * frame["hni"]).sum()),
        "gov_tax": float((w * frame["gov_tax"]).sum()),
        "gov_spending": float((w * frame["gov_spending"]).sum()),
        "heads": {v: float((w * a).sum()) for v, a in frame["heads"].items()},
    }
    return out


def poverty_block(base: dict, ref: dict) -> dict:
    """Weighted persons and children in poverty in each world, on the
    moving relative line (the engine's flags), the absolute line, and a
    relative line FIXED at 60% of the baseline world's person-weighted
    median equivalised income (the fixed-line convention UKMOD, IPPR and
    the campaign's two-child runs use)."""
    out = {}
    for key in base["poverty"]:
        for name, fr in (("baseline", base), ("reform", ref)):
            m = fr["poverty"][key]
            out[f"{key}__{name}"] = {
                "people": float((fr["weight"] * fr["people"])[m].sum()),
                "children": float((fr["weight"] * fr["children"])[m].sum()),
            }
    for basis in ("bhc", "ahc"):
        x = base[f"equiv_{basis}"]
        pw = base["weight"] * base["people"]
        line = 0.6 * _weighted_median(x, pw)
        for name, fr in (("baseline", base), ("reform", ref)):
            m = fr[f"equiv_{basis}"] < line
            out[f"relative_60_median_fixed_at_baseline_{basis}__{name}"] = {
                "people": float((fr["weight"] * fr["people"])[m].sum()),
                "children": float((fr["weight"] * fr["children"])[m].sum()),
                "line_gbp_year": line,
            }
    return out


def distribution_block(base: dict, ref: dict) -> dict:
    """Per income group (baseline-world, person-weighted): weighted
    households and people, the sum of household net income in each
    world, and the weighted count of households gaining / losing more
    than each threshold of their baseline household net income."""
    out = {}
    d_hni = ref["hni"] - base["hni"]
    rel = np.divide(
        d_hni, np.abs(base["hni"]), out=np.zeros_like(d_hni), where=base["hni"] != 0
    )
    for basis in ("bhc", "ahc"):
        for n, label in ((10, "decile"), (20, "vigintile")):
            groups = _weighted_quantile_groups(
                base[f"equiv_{basis}"], base["weight"] * base["people"], n
            )
            rows = []
            for g in range(1, n + 1):
                m = groups == g
                w = base["weight"][m]
                row = {
                    "group": g,
                    "households": float(w.sum()),
                    "people": float((w * base["people"][m]).sum()),
                    "hni_baseline": float((w * base["hni"][m]).sum()),
                    "hni_reform": float((w * ref["hni"][m]).sum()),
                }
                for t in THRESHOLDS:
                    row[f"gaining_over_{t:g}"] = float(w[rel[m] > t].sum())
                    row[f"losing_over_{t:g}"] = float(w[rel[m] < -t].sum())
                rows.append(row)
            out[f"{basis}_{label}"] = rows
    all_w = base["weight"]
    out["all"] = {
        "households": float(all_w.sum()),
        "people": float((all_w * base["people"]).sum()),
        "hni_baseline": float((all_w * base["hni"]).sum()),
        "hni_reform": float((all_w * ref["hni"]).sum()),
        **{f"gaining_over_{t:g}": float(all_w[rel > t].sum()) for t in THRESHOLDS},
        **{f"losing_over_{t:g}": float(all_w[rel < -t].sum()) for t in THRESHOLDS},
    }
    return out


def affected_block(base: dict, ref: dict) -> dict:
    changed = np.zeros(len(base["weight"]), dtype=bool)
    for v in base["heads"]:
        changed |= ~np.isclose(base["heads"][v], ref["heads"][v], rtol=0, atol=0.5)
    return {
        "households": float(base["weight"][changed].sum()),
        "people": float((base["weight"] * base["people"])[changed].sum()),
        "children": float((base["weight"] * base["children"])[changed].sum()),
    }


# --- the run --------------------------------------------------------------------


def run_measure(
    key: str,
    worlds: dict,
    measure: dict,
    years: list[int],
    base_frames: dict,
    pre: dict,
    run_id: str,
    out_dir: Path,
) -> list[Path]:
    import psutil

    proc = psutil.Process()
    heads = list(measure.get("head_variables") or [])
    written = []
    alt_reform = (
        worlds["baseline_reform"]
        if worlds["baseline_reform"]
        else worlds["reform_reform"]
    )
    alt_is_baseline = worlds["baseline_reform"] is not None
    t0 = time.perf_counter()
    before = sha256_file(pre["artifact"])
    alt = build_sim(alt_reform)
    for year in years:
        fb = base_frames[year]
        if any(v not in fb["heads"] for v in heads):
            raise SystemExit(f"{key}: baseline frame for {year} lacks heads {heads}")
        fb = {**fb, "heads": {v: fb["heads"][v] for v in heads}}
        fa = household_frame(alt, year, heads)
        base_frame, ref_frame = (fa, fb) if alt_is_baseline else (fb, fa)
        artifact = {
            "measure_key": key,
            "year": year,
            "fy_proxy": f"{year}-{(year + 1) % 100:02d}",
            "construction": worlds["construction"],
            "components": worlds["components"],
            "baseline_world": {
                "executed": "certified world with pe_baseline_modifier"
                if alt_is_baseline
                else "certified world as served (current law)",
                "reform_dict": worlds["baseline_reform"],
            },
            "reform_world": {
                "executed": "certified world as served (current law)"
                if alt_is_baseline
                else "certified world with pe_reform_delta",
                "reform_dict": worlds["reform_reform"],
            },
            "head_variables": heads,
            "null_executed_as_no_limit": worlds.get("sentinels", []),
            "totals": {"baseline": totals(base_frame), "reform": totals(ref_frame)},
            "poverty": poverty_block(base_frame, ref_frame),
            "distribution": distribution_block(base_frame, ref_frame),
            "affected": affected_block(base_frame, ref_frame),
            "income_group_rule": "person-weighted quantiles of the BASELINE world's equivalised HBAI household net income (bhc: equiv_hbai_household_net_income; ahc: equiv_hbai_household_net_income_ahc), held fixed for the reform world; gaining/losing thresholds are shares of the household's baseline household_net_income",
            "engine_version": pre["engine_version"],
            "data_bundle": pre["revision"],
            "dataset_sha256_before": before,
            "run_id": run_id,
            "computed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        }
        after = sha256_file(pre["artifact"])
        if after != before:
            raise SystemExit("the certified artifact changed during the run")
        artifact["dataset_sha256_after"] = after
        artifact["peak_rss_gib"] = round(proc.memory_info().rss / 2**30, 2)
        path = out_dir / f"{key}_{year}.json"
        path.write_text(json.dumps(artifact, indent=1, sort_keys=True) + "\n")
        written.append(path)
        eff = (
            artifact["totals"]["reform"]["gov_tax"]
            - artifact["totals"]["baseline"]["gov_tax"]
        )
        print(
            f"[{year}] {key}: gov_tax effect {eff / 1e9:+.3f}bn; heads "
            + ", ".join(
                f"{v}={(artifact['totals']['reform']['heads'][v] - artifact['totals']['baseline']['heads'][v]) / 1e9:+.3f}bn"
                for v in heads
            ),
            flush=True,
        )
    del alt
    print(f"{key}: {len(years)} years in {time.perf_counter() - t0:.0f}s", flush=True)
    return written


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--measures", nargs="*")
    ap.add_argument("--years", nargs="*", type=int, default=list(YEARS))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--run-id", default=f"campaign-{dt.date.today():%Y%m%d}-uk-ab2025")
    ap.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = ap.parse_args(argv)

    index = load_registry()
    comp = computable(index)
    aliases = {k: w["alias_of"] for k, w in comp.items() if "alias_of" in w}
    runnable = {k: w for k, w in comp.items() if "alias_of" not in w}
    selected = list(runnable) if not args.measures else args.measures
    unknown = [k for k in selected if k not in runnable]
    if unknown:
        raise SystemExit(f"not computable (no executable spec or an alias): {unknown}")
    summary = {
        "selected": selected,
        "aliases": aliases,
        "not_computable": sorted(
            k
            for k, m in index.items()
            if m["computability"] in ("expressible", "partial") and k not in comp
        ),
        "years": args.years,
    }
    if args.dry_run:
        for k in selected:
            w = runnable[k]
            print(
                k,
                w["construction"],
                "baseline_reform" if w["baseline_reform"] else "",
                "reform_reform" if w["reform_reform"] else "",
            )
        print(
            json.dumps({k: v for k, v in summary.items() if k != "selected"}, indent=1)
        )
        print(
            f"dry run: {len(selected)} measures would run for {args.years}; no simulation constructed"
        )
        return 0

    pre = preflight()
    print(
        f"certified artifact {pre['revision']} sha256 verified; engine {pre['engine_version']}",
        flush=True,
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    # One simulation alive at a time: each year's baseline FRAME is
    # extracted once (every head variable any selected measure names) and
    # the baseline simulation discarded before the next is built.
    all_heads = sorted(
        {v for k in selected for v in (index[k].get("head_variables") or [])}
    )
    base_frames = {}
    for year in args.years:
        t0 = time.perf_counter()
        base = build_sim(None)
        base_frames[year] = household_frame(base, year, all_heads)
        del base
        print(
            f"[{year}] baseline frame extracted ({len(all_heads)} heads) in "
            f"{time.perf_counter() - t0:.0f}s",
            flush=True,
        )
    written = []
    for k in selected:
        written += run_measure(
            k,
            runnable[k],
            index[k],
            args.years,
            base_frames,
            pre,
            args.run_id,
            args.output_dir,
        )
    manifest = {
        "run_id": args.run_id,
        "engine_version": pre["engine_version"],
        "data_bundle": pre["revision"],
        "artifact_sha256": pre["sha256"],
        "years": args.years,
        "measures": selected,
        "aliases": aliases,
        "not_computable": summary["not_computable"],
        "artifacts": {str(p.relative_to(ROOT)): sha256_file(p) for p in written},
    }
    (args.output_dir / "RUN_MANIFEST.json").write_text(
        json.dumps(manifest, indent=1, sort_keys=True) + "\n"
    )
    print(f"wrote {len(written)} artifacts and RUN_MANIFEST.json to {args.output_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
