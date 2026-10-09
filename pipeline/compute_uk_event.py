"""Replay an OBR fiscal event against the hash-verified certified UK bundle.

AB2025 supplies the shared construction rules; the mode-2 OBR runner supplies
the managed simulation, metadata and exact runtime-file hash checks. This
runner calculates fiscal heads only, reuses each year's certified baseline,
and keeps timings outside the deterministic numerical artifacts.
"""

from __future__ import annotations

import argparse
import gc
import json
import math
import os
import re
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from functools import lru_cache
from multiprocessing import get_context
from pathlib import Path

from pipeline import build_uk_event_registry as registry_builder
from pipeline import compute_uk_ab2025 as worlds
from pipeline import compute_uk_obr_costings as fiscal

ROOT = worlds.ROOT
EVENT_PATTERN = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")


def event_paths(event: str) -> tuple[Path, Path]:
    if not EVENT_PATTERN.fullmatch(event):
        raise ValueError("event must be a lowercase underscore-separated slug")
    return (
        ROOT / "data" / "uk" / "events" / f"{event}_measures.json",
        ROOT / "results" / "uk" / "events" / event,
    )


def validate_event_identity(registry: dict, event: str) -> None:
    identity = registry.get("event_slug", registry.get("event"))
    if identity is not None and identity != event:
        raise ValueError("registry event identity differs from --event")


def canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(value, indent=1, sort_keys=True, allow_nan=False) + "\n"
    ).encode()


@lru_cache(maxsize=1)
def runtime_versions() -> dict[str, str]:
    return {
        "policyengine_version": fiscal.package_version("policyengine"),
        "policyengine_core_version": fiscal.package_version("policyengine-core"),
    }


def head_definitions(measure: dict) -> list[dict]:
    """Explicit source-head mappings; fiscal sides are never inferred from a gap."""
    definitions = measure.get("heads") or []
    if not definitions:
        channels = measure.get("head_channels") or {}
        definitions = [
            {
                "obr_head": variable,
                "pe_variables": [variable],
                "channel": channels.get(variable),
            }
            for variable in measure.get("head_variables", [])
        ]
    out = []
    assigned = {}
    for definition in definitions:
        variables = definition.get("pe_variables") or definition.get("head_variables")
        if not variables or definition.get("channel") not in ("tax", "spending"):
            raise ValueError(
                f"{measure['measure_key']}: fiscal heads need variables and tax/spending channel"
            )
        if len(variables) != len(set(variables)):
            raise ValueError(
                f"{measure['measure_key']}: duplicate variables within a fiscal head"
            )
        for variable in variables:
            if variable in assigned:
                raise ValueError(
                    f"{measure['measure_key']}: {variable} appears in multiple fiscal heads"
                )
            assigned[variable] = definition["obr_head"]
        out.append({**definition, "pe_variables": list(variables)})
    return out


def variable_channels(measure: dict) -> dict[str, str]:
    out: dict[str, str] = {}
    for head in head_definitions(measure):
        for variable in head["pe_variables"]:
            if variable in out and out[variable] != head["channel"]:
                raise ValueError(
                    f"{measure['measure_key']}: conflicting fiscal side for {variable}"
                )
            out[variable] = head["channel"]
    declared = set(measure.get("head_variables") or [])
    if declared and declared != set(out):
        raise ValueError(
            f"{measure['measure_key']}: head_variables differ from head mappings"
        )
    return out


def build_artifact(
    *,
    measure: dict,
    world: dict,
    year: int,
    baseline: dict,
    reform: dict,
    certified: dict,
    registry_sha256: str,
    event: str,
) -> dict:
    """Numerical facts only: identical inputs produce identical artifact bytes.

    baseline/reform are announcement-oriented worlds. In a reversal the
    baseline executes the reversal and the reform is certified current law.
    The literal executed reversal minus certified delta is retained separately.
    """
    channels = variable_channels(measure)
    b = baseline["aggregates_gbp"]
    r = reform["aggregates_gbp"]
    effects: dict[str, float] = {}
    literal: dict[str, float] = {}
    reversal = world["construction"] == "reversal_on_certified_world"
    for variable, channel in channels.items():
        raw = r[variable] - b[variable]
        executed_delta = -raw if reversal else raw
        literal[variable], effects[variable] = fiscal.orient_exchequer_effect(
            executed_delta,
            channel,
            "reversal_on_certified_world" if reversal else "forward_from_baseline",
        )
        if not math.isfinite(effects[variable]):
            raise ValueError(f"{measure['measure_key']} {year}: non-finite {variable}")
    bundles = [
        simulation["policyengine_bundle"]
        for simulation in (baseline, reform, certified)
    ]
    if any(bundle != bundles[0] for bundle in bundles[1:]):
        raise ValueError("the two worlds do not use the same certified release")
    digest = certified["dataset_sha256_before"]
    for simulation in (baseline, reform, certified):
        if (
            simulation["dataset_sha256_before"] != digest
            or simulation["dataset_sha256_after"] != digest
        ):
            raise ValueError("certified dataset hashes differ between worlds")
    artifact = {
        "schema_version": 1,
        "event": event,
        "fiscal_event": measure.get("fiscal_event", event),
        "measure_key": measure["measure_key"],
        "year": year,
        "fy_proxy": fiscal.fy_label(year),
        "construction": world["construction"],
        "components": world["components"],
        "baseline_world": {
            "executed": "certified world with pe_baseline_modifier"
            if world["baseline_reform"]
            else "certified world as served (current law)",
            "reform_dict": world["baseline_reform"],
        },
        "reform_world": {
            "executed": "certified world with pe_reform_delta"
            if world["reform_reform"]
            else "certified world as served (current law)",
            "reform_dict": world["reform_reform"],
        },
        "head_variables": list(channels),
        "head_channels": channels,
        "head_definitions": head_definitions(measure),
        "head_effects": effects,
        "measure_total_gbp": sum(effects.values()),
        "literal_reform_minus_baseline": literal,
        "totals": {
            "baseline": {"heads": {v: b[v] for v in channels}},
            "reform": {"heads": {v: r[v] for v in channels}},
        },
        "certified_aggregates_gbp": {
            v: certified["aggregates_gbp"][v] for v in channels
        },
        "null_executed_as_no_limit": world.get("sentinels", []),
        "variable_metadata": {v: certified["variable_metadata"][v] for v in channels},
        "engine_version": bundles[0].get("model_version")
        or bundles[0].get("country_package_version"),
        **runtime_versions(),
        "data_bundle": fiscal.data_bundle_id(bundles[0]),
        "certified_dataset_sha256": digest,
        "dataset_sha256_before": digest,
        "dataset_sha256_after": digest,
        "registry_sha256": registry_sha256,
        "sign_convention": "positive_gain_to_exchequer",
        "calendar_year_proxy": f"PE calendar year {year} proxies FY {fiscal.fy_label(year)}.",
        "scope": "sum of declared fiscal heads; static household microsimulation",
    }
    if reversal:
        artifact["literal_reversal_minus_certified_gbp"] = literal
    return artifact


def preflight() -> dict:
    """The committed pin and the managed release must agree before any run."""
    fiscal.configure_offline()
    worlds.configure_offline()
    committed = worlds.preflight()
    managed = fiscal.preflight_certified_dataset()
    if (
        managed["sha256"] != committed["sha256"]
        or fiscal.data_bundle_id(managed["release_bundle"]) != committed["revision"]
    ):
        raise RuntimeError("managed release differs from data/uk/certified_bundle.json")
    return managed


def run_sim(year: int, variables: list[str], reform: dict | None, pre: dict) -> dict:
    result = fiscal.run_managed_simulation(
        year=year,
        variables=variables,
        reform=reform,
        runtime_dataset_source=Path(pre["runtime_dataset_source"]),
        expected_dataset_sha256=pre["sha256"],
        include_engine_provenance=True,
    )
    fiscal.assert_managed_bundle(result["policyengine_bundle"], pre["release_bundle"])
    return result


def run_year_job(job: dict) -> dict:
    """One year's baseline and sequential alternate worlds in one process."""
    year = job["year"]
    pre = job["pre"]
    started = time.perf_counter()
    print(
        f"[pid {os.getpid()} year {year}] starting certified baseline ({len(job['variables'])} heads)",
        flush=True,
    )
    baseline = run_sim(year, job["variables"], None, pre)
    timings = [
        {
            "world": "certified_baseline",
            "year": year,
            "seconds": time.perf_counter() - started,
            "performance": baseline["performance"],
        }
    ]
    print(
        f"[pid {os.getpid()} year {year}] certified baseline extracted once in {time.perf_counter() - started:.1f}s",
        flush=True,
    )
    artifacts = {}
    progress_artifacts = dict(job.get("retained_artifacts", {}))
    for key in job["selected"]:
        world = job["runnable"][key]
        measure = job["index"][key]
        variables = list(variable_channels(measure))
        started = time.perf_counter()
        base = baseline
        if world["baseline_reform"]:
            print(
                f"[pid {os.getpid()} year {year}] starting {key} baseline modifier ({world['construction']})",
                flush=True,
            )
            base = run_sim(year, variables, world["baseline_reform"], pre)
        reform = baseline
        if world["reform_reform"]:
            print(
                f"[pid {os.getpid()} year {year}] starting {key} reform delta ({world['construction']})",
                flush=True,
            )
            reform = run_sim(year, variables, world["reform_reform"], pre)
        artifact = build_artifact(
            measure=measure,
            world=world,
            year=year,
            baseline=base,
            reform=reform,
            certified=baseline,
            registry_sha256=job["registry_sha256"],
            event=job["event"],
        )
        path = job["output_dir"] / f"{key}_{year}.json"
        fiscal.atomic_write_bytes(path, canonical_bytes(artifact))
        relative = str(path.relative_to(ROOT))
        artifacts[relative] = fiscal.sha256_file(path)
        progress_artifacts[relative] = artifacts[relative]
        fiscal.atomic_write_bytes(
            job["output_dir"] / f"RUN_PROGRESS_{year}.json",
            canonical_bytes(progress_receipt(job, progress_artifacts)),
        )
        timings.append(
            {"measure_key": key, "year": year, "seconds": time.perf_counter() - started}
        )
        print(
            f"[{year}] {key}: {artifact['measure_total_gbp'] / 1e9:+.3f}bn gain to Exchequer",
            flush=True,
        )
    return {"artifacts": artifacts, "timings": timings}


def progress_receipt(job: dict, artifacts: dict[str, str]) -> dict:
    """Commit completed artifact bytes before the next simulation begins."""
    return {
        "schema_version": 1,
        "receipt_kind": "completed_event_artifacts",
        "event": job["event"],
        "year": job["year"],
        "registry_sha256": job["registry_sha256"],
        "certified_dataset_sha256": job["pre"]["sha256"],
        "data_bundle": fiscal.data_bundle_id(job["pre"]["release_bundle"]),
        "engine_version": fiscal.package_version("policyengine-uk"),
        **runtime_versions(),
        "artifacts": artifacts,
    }


def retained_artifact_digests(
    output_dir: Path,
    *,
    event: str,
    years: list[int],
    registry_sha256: str,
    pre: dict,
) -> dict[str, str]:
    """Read only SHA-bound completed outputs; unreceipted files are ignored."""
    receipts = []
    manifest_path = output_dir / "RUN_MANIFEST.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_bytes())
        if (
            manifest.get("event") == event
            and manifest.get("registry_sha256") == registry_sha256
            and manifest.get("certified_dataset_sha256") == pre["sha256"]
        ):
            receipts.append(manifest)
    for year in years:
        path = output_dir / f"RUN_PROGRESS_{year}.json"
        if not path.exists():
            continue
        receipt = json.loads(path.read_bytes())
        expected = progress_receipt(
            {
                "event": event,
                "year": year,
                "registry_sha256": registry_sha256,
                "pre": pre,
            },
            {},
        )
        if all(
            receipt.get(field) == value
            for field, value in expected.items()
            if field != "artifacts"
        ):
            receipts.append(receipt)
    digests = {}
    for receipt in receipts:
        for relative, digest in receipt["artifacts"].items():
            if relative in digests and digests[relative] != digest:
                raise ValueError(f"conflicting completed-artifact receipts: {relative}")
            path = (ROOT / relative).resolve()
            if not path.is_relative_to(output_dir.resolve()):
                raise ValueError(
                    "retained receipt names an artifact outside this event directory"
                )
            digests[relative] = digest
    return digests


def grid_rows(pairs) -> list[dict]:
    return [{"measure_key": key, "year": year} for key, year in sorted(pairs)]


def validate_years(requested: list[int], registry: dict) -> list[int]:
    allowed = registry.get("calendar_years")
    if not allowed:
        raise ValueError("registry must record the supported calendar_years")
    years = sorted(set(requested or allowed))
    if any(year < 2023 or year > 2030 for year in years):
        raise ValueError(
            "certified single-population replay supports 2023 through 2030 only"
        )
    if set(years) - set(allowed):
        raise ValueError(
            f"years {years} outside this event's documented support {allowed}"
        )
    return years


def verify_registry_identity(path: Path, expected_sha256: str) -> None:
    if fiscal.sha256_file(path) != expected_sha256:
        raise ValueError(
            "registry bytes changed after planning; refusing simulation or publication"
        )


def parallel_year_results(jobs: list[dict], workers: int):
    """Stop this runner's child simulations when interrupted or a job fails.

    Python 3.12 has no public executor termination API. Retain the executor's
    owned Process objects so their public terminate methods can stop running
    simulations before shutdown waits for completion.
    """
    pool = ProcessPoolExecutor(max_workers=workers, mp_context=get_context("spawn"))
    try:
        yield from pool.map(run_year_job, jobs)
    except BaseException:
        print(
            f"[pid {os.getpid()}] stopping owned year workers after interruption or job failure",
            flush=True,
        )
        for process in list(pool._processes.values()):
            if process.is_alive():
                process.terminate()
        pool.shutdown(wait=True, cancel_futures=True)
        raise
    else:
        pool.shutdown(wait=True)


def main(argv: list[str] | None = None) -> int:
    fiscal.configure_offline()
    worlds.configure_offline()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--event", required=True)
    ap.add_argument("--registry", type=Path)
    ap.add_argument("--output-dir", type=Path)
    ap.add_argument("--measures", nargs="*")
    ap.add_argument("--years", nargs="*", type=int)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--guards", action="store_true")
    ap.add_argument("--resume", action="store_true")
    ap.add_argument(
        "--workers",
        type=int,
        choices=(1, 2),
        default=1,
        help="spawn at most two year workers; each holds one live managed simulation",
    )
    args = ap.parse_args(argv)
    default_registry, default_output = event_paths(args.event)
    registry_path = args.registry or default_registry
    output_dir = (args.output_dir or default_output).resolve()
    registry_payload = registry_path.read_bytes()
    registry = json.loads(registry_payload)
    validate_event_identity(registry, args.event)
    registry_builder.validate_registry(registry)
    if (
        not (args.dry_run or args.guards)
        and (args.measures or args.years)
        and args.output_dir is None
        and not args.resume
        and (output_dir / "RUN_MANIFEST.json").exists()
    ):
        raise ValueError(
            "focused reruns with an existing default manifest require --resume "
            "or an explicit --output-dir"
        )
    registry_sha256 = fiscal.hashlib.sha256(registry_payload).hexdigest()
    years = validate_years(args.years or [], registry)
    index = {measure["measure_key"]: measure for measure in registry["measures"]}
    planned = worlds.computable(index, years=years)
    runnable = {key: world for key, world in planned.items() if "alias_of" not in world}
    selected = args.measures or list(runnable)
    if set(selected) - set(runnable):
        raise ValueError(f"not executable: {sorted(set(selected) - set(runnable))}")
    for key in selected:
        variable_channels(index[key])
    coverage = worlds.world_coverage_gaps(index, years=years)
    if coverage:
        raise ValueError("\n".join(coverage))
    if args.dry_run or args.guards:
        try:
            resolve = worlds.engine_resolver()
        except ImportError:
            if args.guards:
                raise
            guard = "engine unavailable; reversal guard requires --guards in the pinned venv"
        else:
            gaps = worlds.reversal_delta_mismatches(index, resolve, years=years)
            if gaps:
                raise ValueError("\n".join(gaps))
            guard = "every reversal delta restates certified current law"
        print(
            json.dumps(
                {
                    "event": args.event,
                    "years": years,
                    "selected": selected,
                    "not_computable": worlds.not_computable(index, years=years),
                    "guard": guard,
                },
                indent=1,
                sort_keys=True,
            )
        )
        return 0
    started = time.perf_counter()
    verify_registry_identity(registry_path, registry_sha256)
    print(f"[pid {os.getpid()}] starting offline bundle preflight", flush=True)
    pre = preflight()
    print(
        f"[pid {os.getpid()}] offline bundle preflight complete; starting processed-world reversal guard",
        flush=True,
    )
    gaps = worlds.reversal_delta_mismatches(
        index, worlds.engine_resolver(), years=years
    )
    gc.collect()
    if gaps:
        raise ValueError("\n".join(gaps))
    print(f"[pid {os.getpid()}] processed-world reversal guard complete", flush=True)
    verify_registry_identity(registry_path, registry_sha256)
    output_dir.mkdir(parents=True, exist_ok=True)
    previous_digests = retained_artifact_digests(
        output_dir,
        event=args.event,
        years=registry["calendar_years"],
        registry_sha256=registry_sha256,
        pre=pre,
    )
    requested_pairs = {(key, year) for key in selected for year in years}
    full_pairs = {
        (key, year) for key in runnable for year in registry["calendar_years"]
    }
    expected_paths = {
        str((output_dir / f"{key}_{year}.json").relative_to(ROOT)): (key, year)
        for key, year in full_pairs
    }
    committed = {}
    for relative, digest in previous_digests.items():
        if relative not in expected_paths:
            raise ValueError(
                "retained receipt names a measure/year outside the event grid"
            )
        key, year = expected_paths[relative]
        if not args.resume and (key, year) in requested_pairs:
            continue
        path = ROOT / relative
        if not path.exists():
            continue
        if fiscal.sha256_file(path) != digest:
            raise ValueError(
                f"retained artifact bytes differ from manifest: {relative}"
            )
        previous = json.loads(path.read_bytes())
        if (
            previous.get("registry_sha256") != registry_sha256
            or previous.get("certified_dataset_sha256") != pre["sha256"]
            or previous.get("event") != args.event
            or previous.get("measure_key") != key
            or previous.get("year") != year
            or any(
                previous.get(field) != value
                for field, value in runtime_versions().items()
            )
        ):
            raise ValueError("retained artifact identity differs from its receipt")
        committed[(key, year)] = digest
    retained = {
        pair: digest for pair, digest in committed.items() if pair in requested_pairs
    }
    variables = sorted(
        {variable for key in selected for variable in variable_channels(index[key])}
    )
    timings = []
    artifacts = {
        str((output_dir / f"{key}_{year}.json").relative_to(ROOT)): digest
        for (key, year), digest in committed.items()
    }
    jobs = []
    for year in years:
        pending = [key for key in selected if (key, year) not in retained]
        if pending:
            jobs.append(
                {
                    "year": year,
                    "selected": pending,
                    "index": index,
                    "runnable": runnable,
                    "variables": variables,
                    "pre": pre,
                    "registry_sha256": registry_sha256,
                    "event": args.event,
                    "output_dir": output_dir,
                    "retained_artifacts": {
                        str(
                            (output_dir / f"{key}_{year}.json").relative_to(ROOT)
                        ): digest
                        for (key, retained_year), digest in committed.items()
                        if retained_year == year
                    },
                }
            )
    if args.workers == 1:
        for job in jobs:
            result = run_year_job(job)
            artifacts.update(result["artifacts"])
            timings.extend(result["timings"])
    elif jobs:
        for result in parallel_year_results(jobs, args.workers):
            artifacts.update(result["artifacts"])
            timings.extend(result["timings"])
    verify_registry_identity(registry_path, registry_sha256)
    artifact_pairs = {expected_paths[relative] for relative in artifacts}
    if requested_pairs - artifact_pairs:
        raise ValueError(
            "requested measure/year grid is incomplete; refusing final manifest"
        )
    manifest = {
        "schema_version": 1,
        "event": args.event,
        "registry_path": fiscal.relative_to_root(registry_path),
        "registry_sha256": registry_sha256,
        "years": sorted({year for _, year in artifact_pairs}),
        "measures": sorted({key for key, _ in artifact_pairs}),
        "requested_years": years,
        "requested_measures": selected,
        "requested_grid": grid_rows(requested_pairs),
        "artifact_grid": grid_rows(artifact_pairs),
        "full_event_grid": grid_rows(full_pairs),
        "full_event_complete": full_pairs <= artifact_pairs,
        "artifacts": artifacts,
        "certified_dataset_sha256": pre["sha256"],
        "data_bundle": fiscal.data_bundle_id(pre["release_bundle"]),
        "engine_version": fiscal.package_version("policyengine-uk"),
        **runtime_versions(),
        "not_computable": worlds.not_computable(index, years=years),
    }
    fiscal.atomic_write_bytes(
        output_dir / "RUN_MANIFEST.json", canonical_bytes(manifest)
    )
    fiscal.atomic_write_bytes(
        output_dir / "RUN_LOG.json",
        canonical_bytes(
            {
                "wall_seconds": time.perf_counter() - started,
                "timings": timings,
                "runner": "local managed simulation; one live simulation per process",
                "workers": args.workers,
            }
        ),
    )
    print(
        f"wrote {len(artifacts)} deterministic numerical artifacts to {output_dir}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
