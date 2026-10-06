"""Shared machinery for the US compute-campaign reconstruction.

Every microsimulation runs in its OWN spawned child process
(:func:`run_job`): the child builds ``pe.us.managed_microsimulation()`` —
so the certified dataset of whichever ``policyengine`` bundle is installed
in the interpreter is used — applies the job's reform dict and input
overrides, calls one family measure function, and returns plain floats plus
the bundle provenance. The parent never holds a simulation, so memory is
released when the child exits and at most one simulation exists at a time.

Weighting follows the repo's binding rules (see
``pipeline/compute_counterparts.py``): microdf auto-weighting only — totals
are ``MicroSeries.sum()``, counts are sums of boolean MicroSeries, subgroup
cuts are boolean-array indexing of a MicroSeries; cross-entity values go
through ``calculate(..., map_to=...)``. Weight arrays are never touched.
"""

from __future__ import annotations

import concurrent.futures as cf
import datetime as dt
import json
import multiprocessing as mp
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
ORIGINAL_DIR = REPO / "sources" / "campaign-20260802" / "us"
ORIGINAL_RUN_PREFIX = "campaign-20260802-"
NEW_RUN_PREFIX = "campaign-20261006-"

# Reform period used for every parameter change: a bounded range, so the
# change holds over the computed years and nothing outside them depends on
# the core version's "bare instant flattens later breakpoints" semantics.
FAR_END = "2100-12-31"


def log(msg: str) -> None:
    print(f"[{dt.datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


# ---------------------------------------------------------------------------
# child-process side
# ---------------------------------------------------------------------------


def _get_parameter(parameters, path: str):
    from policyengine_core.parameters import get_parameter

    return get_parameter(parameters, path)


def _check_reform_applied(sim, reform: dict) -> dict:
    """Read every reformed parameter back at its start instant and fail if
    the simulation's tax-benefit system does not carry the requested value
    (a silently ignored path would otherwise score as a zero reform)."""
    checked = {}
    params = sim.tax_benefit_system.parameters
    for path, periods in reform.items():
        node = _get_parameter(params, path)
        for key, value in periods.items():
            start = key.split(".")[0]
            got = node(start)
            ok = (
                bool(got) == bool(value)
                if isinstance(value, bool)
                else abs(float(got) - float(value)) < 1e-9
            )
            if not ok:
                raise RuntimeError(
                    f"reform not applied: {path} at {start} = {got!r},"
                    f" expected {value!r}"
                )
            checked[f"{path}@{start}"] = value
    return checked


def _set_inputs(sim, inputs: dict) -> list[str]:
    """Force input variables before any calculation. ``inputs`` maps a
    variable name to {"value": scalar, "years": [..]}; MONTH-defined
    variables are set for all twelve months of each year."""
    import numpy as np

    vs = sim.tax_benefit_system.variables
    done = []
    for name, spec in inputs.items():
        if name not in vs:
            raise RuntimeError(f"input {name!r} not defined by the pinned engine")
        var = vs[name]
        n = sim.populations[var.entity.key].count
        arr = np.full(n, spec["value"], dtype=type(spec["value"]))
        monthly = str(var.definition_period).lower() in ("month", "monthly")
        for y in spec["years"]:
            periods = [f"{y}-{m:02d}" for m in range(1, 13)] if monthly else [y]
            for p in periods:
                sim.set_input(name, p, arr)
        done.append(f"{name}={spec['value']} {spec['years']}")
    return done


def _child(job: dict) -> dict:
    import gc
    import importlib
    import resource

    sys.path.insert(0, str(HERE))
    t0 = time.time()
    import policyengine as pe

    reform = job.get("reform") or None
    builder = job.get("reform_builder")
    if builder:
        mod_name, fn_name = builder.split(":")
        reform = getattr(importlib.import_module(mod_name), fn_name)(
            **job.get("reform_builder_args", {})
        )
    kwargs = {"reform": reform} if reform else {}
    sim = pe.us.managed_microsimulation(**kwargs)
    bundle = {k: str(v) for k, v in getattr(sim, "policyengine_bundle", {}).items()}
    checked = _check_reform_applied(sim, reform) if reform else {}
    inputs_set = _set_inputs(sim, job.get("inputs", {}))
    mod_name, fn_name = job["measure"].split(":")
    fn = getattr(importlib.import_module(mod_name), fn_name)
    values = fn(sim, **job.get("measure_args", {}))
    del sim
    gc.collect()
    return {
        "label": job["label"],
        "values": {k: float(v) for k, v in values.items()},
        "bundle": bundle,
        "reform": reform,
        "reform_checked": checked,
        "inputs_set": inputs_set,
        "seconds": round(time.time() - t0, 1),
        "maxrss_gb": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e9, 2),
    }


def run_job(job: dict) -> dict:
    """Run one simulation job in a fresh spawned process (sequential)."""
    log(f"sim start: {job['label']}")
    ctx = mp.get_context("spawn")
    with cf.ProcessPoolExecutor(max_workers=1, mp_context=ctx) as ex:
        out = ex.submit(_child, job).result()
    log(f"sim done: {job['label']} ({out['seconds']}s, maxrss {out['maxrss_gb']} GB)")
    return out


# ---------------------------------------------------------------------------
# parent-process side: provenance + row emission
# ---------------------------------------------------------------------------


def provenance(results: list[dict]) -> dict:
    """The one bundle every job of a family executed on (fail if mixed)."""
    keys = {
        (
            r["bundle"].get("model_version"),
            r["bundle"].get("certified_data_build_id"),
        )
        for r in results
    }
    if len(keys) != 1:
        raise RuntimeError(f"jobs ran on mixed bundles: {keys}")
    b = results[0]["bundle"]
    return {
        "engine_version": b["model_version"],
        "data_bundle": b["certified_data_build_id"],
        "bundle_id": b.get("bundle_id"),
        "policyengine_version": b.get("policyengine_version"),
        "legacy_input_renames": b.get("legacy_input_renames"),
    }


def load_original(stem: str) -> list[dict]:
    path = ORIGINAL_DIR / f"{stem}.jsonl"
    return [json.loads(line) for line in path.read_text().splitlines() if line]


def new_run_id(original_run_id: str) -> str:
    if not original_run_id.startswith(ORIGINAL_RUN_PREFIX):
        raise ValueError(f"unexpected original run_id {original_run_id!r}")
    return NEW_RUN_PREFIX + original_run_id[len(ORIGINAL_RUN_PREFIX) :]


def emit_row(
    template: dict,
    value: float,
    prov: dict,
    computed_at: str,
    *,
    pe_construction: str | None = None,
    annotations: list[str] | None = None,
) -> dict:
    """A staged row in the original schema and key order: provenance,
    value, computed_at and run_id are replaced; everything else (match
    descriptor / exhibit fields, status, annotations, construction text)
    is carried from the original row unless explicitly overridden."""
    out = {}
    for k, v in template.items():
        if k == "engine_version":
            out[k] = prov["engine_version"]
        elif k == "data_bundle":
            out[k] = prov["data_bundle"]
        elif k == "pe_value":
            out[k] = value
        elif k == "computed_at":
            out[k] = computed_at
        elif k == "run_id":
            out[k] = new_run_id(v)
        elif k == "pe_construction" and pe_construction is not None:
            out[k] = pe_construction
        elif k == "annotations" and annotations is not None:
            out[k] = annotations
        else:
            out[k] = v
    return out


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def write_family(out_dir: Path, stem: str, rows: list[dict], meta: dict) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"{stem}.jsonl").write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)
    )
    # Run metadata (per-row reproduced values, jobs, bundle) goes NEXT TO
    # the code, never into the staged directory the ingest globs.
    meta_dir = HERE / "runs"
    meta_dir.mkdir(exist_ok=True)
    tag = meta["provenance"]["bundle_id"] or "unknown"
    (meta_dir / f"{stem}__{tag}.json").write_text(json.dumps(meta, indent=1))
