"""Replay an OBR fiscal event against the hash-verified certified UK bundle.

AB2025 supplies the shared construction rules; the mode-2 OBR runner supplies
the managed simulation, metadata and exact runtime-file hash checks. This
runner calculates fiscal heads only, reuses each year's certified baseline,
and keeps timings outside the deterministic numerical artifacts.
"""

from __future__ import annotations

import argparse
import inspect
import json
import math
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
    )
    fiscal.assert_managed_bundle(result["policyengine_bundle"], pre["release_bundle"])
    definitions = engine_variables()
    for name in variables:
        variable = definitions[name]
        source = inspect.getsourcefile(type(variable))
        result["variable_metadata"][name].update(
            {
                "documentation": getattr(variable, "documentation", None),
                "engine_source": "policyengine_uk/"
                + source.split("/policyengine_uk/", 1)[1]
                if source and "/policyengine_uk/" in source
                else None,
            }
        )
    return result


@lru_cache(maxsize=1)
def engine_variables() -> dict:
    import policyengine_uk

    return policyengine_uk.CountryTaxBenefitSystem().variables


def run_year_job(job: dict) -> dict:
    """One year's baseline and sequential alternate worlds in one process."""
    year = job["year"]
    pre = job["pre"]
    started = time.perf_counter()
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
        f"[{year}] certified baseline extracted once ({len(job['variables'])} heads)",
        flush=True,
    )
    artifacts = {}
    for key in job["selected"]:
        world = job["runnable"][key]
        measure = job["index"][key]
        variables = list(variable_channels(measure))
        started = time.perf_counter()
        base = (
            run_sim(year, variables, world["baseline_reform"], pre)
            if world["baseline_reform"]
            else baseline
        )
        reform = (
            run_sim(year, variables, world["reform_reform"], pre)
            if world["reform_reform"]
            else baseline
        )
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
        artifacts[str(path.relative_to(ROOT))] = fiscal.sha256_file(path)
        timings.append(
            {"measure_key": key, "year": year, "seconds": time.perf_counter() - started}
        )
        print(
            f"[{year}] {key}: {artifact['measure_total_gbp'] / 1e9:+.3f}bn gain to Exchequer",
            flush=True,
        )
    return {"artifacts": artifacts, "timings": timings}


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
    registry_builder.validate_registry(registry)
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
    pre = preflight()
    gaps = worlds.reversal_delta_mismatches(
        index, worlds.engine_resolver(), years=years
    )
    if gaps:
        raise ValueError("\n".join(gaps))
    verify_registry_identity(registry_path, registry_sha256)
    output_dir.mkdir(parents=True, exist_ok=True)
    previous_manifest_path = output_dir / "RUN_MANIFEST.json"
    previous_manifest = (
        json.loads(previous_manifest_path.read_bytes())
        if args.resume and previous_manifest_path.exists()
        else {}
    )
    if (
        previous_manifest.get("registry_sha256") != registry_sha256
        or previous_manifest.get("certified_dataset_sha256") != pre["sha256"]
    ):
        previous_manifest = {}
    retained = {}
    if args.resume:
        for key in selected:
            for year in years:
                path = output_dir / f"{key}_{year}.json"
                relative = str(path.relative_to(ROOT))
                digest = previous_manifest.get("artifacts", {}).get(relative)
                if digest is None or not path.exists():
                    continue
                if fiscal.sha256_file(path) != digest:
                    raise ValueError(
                        f"retained artifact bytes differ from manifest: {relative}"
                    )
                previous = json.loads(path.read_bytes())
                if (
                    previous.get("registry_sha256") != registry_sha256
                    or previous.get("certified_dataset_sha256") != pre["sha256"]
                ):
                    raise ValueError(
                        "retained artifact identity differs from the retained manifest"
                    )
                retained[(key, year)] = digest
    variables = sorted(
        {variable for key in selected for variable in variable_channels(index[key])}
    )
    timings = []
    artifacts = {
        str((output_dir / f"{key}_{year}.json").relative_to(ROOT)): digest
        for (key, year), digest in retained.items()
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
                }
            )
    if args.workers == 1:
        for job in jobs:
            result = run_year_job(job)
            artifacts.update(result["artifacts"])
            timings.extend(result["timings"])
    elif jobs:
        with ProcessPoolExecutor(
            max_workers=args.workers, mp_context=get_context("spawn")
        ) as pool:
            for result in pool.map(run_year_job, jobs):
                artifacts.update(result["artifacts"])
                timings.extend(result["timings"])
    verify_registry_identity(registry_path, registry_sha256)
    manifest = {
        "schema_version": 1,
        "event": args.event,
        "registry_path": fiscal.relative_to_root(registry_path),
        "registry_sha256": registry_sha256,
        "years": years,
        "measures": selected,
        "artifacts": artifacts,
        "certified_dataset_sha256": pre["sha256"],
        "data_bundle": fiscal.data_bundle_id(pre["release_bundle"]),
        "engine_version": fiscal.package_version("policyengine-uk"),
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
