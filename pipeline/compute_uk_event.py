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
from datetime import date
from functools import lru_cache
from multiprocessing import get_context
from pathlib import Path

from pipeline import build_uk_event_registry as registry_builder
from pipeline import compute_uk_ab2025 as worlds
from pipeline import compute_uk_obr_costings as fiscal
from pipeline import uk_replay_variants as variants
from pipeline import uk_construction_revisions as revisions

ROOT = worlds.ROOT
EVENT_PATTERN = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")
UC_HEALTH_ELEMENT_PARAMETER = (
    "gov.dwp.universal_credit.rebalancing.new_claimant_health_element"
)


class ProcessedValueMismatch(RuntimeError):
    """A processed simulation value differs from the construction's intent."""

    def __init__(self, failure: dict):
        self.failure = failure
        super().__init__(failure)


def parameter_scalar(value):
    """JSON representation shared with the parameter-only premises audit."""
    return revisions.scalar(value)


def processed_values_match(intended, processed) -> bool:
    """Relative tolerance only: a zero intended value must remain zero. A path
    with no value on either side agrees; a missing processed value against an
    intended one does not."""
    if intended is None and processed is None:
        return True
    if intended is None or processed is None:
        return False
    if isinstance(intended, (int, float)) and isinstance(processed, (int, float)):
        return (
            math.isfinite(intended)
            and math.isfinite(processed)
            and math.isclose(intended, processed, rel_tol=1e-9, abs_tol=0.0)
        )
    return intended == processed


def check_processed_parameters(sim, checks: list[dict]) -> dict:
    """Read each touched path's period-Y value at 1 January Y from this
    simulation's own processed parameter tree, after its actual reform route.

    It only reads: whether a difference from the intended value refuses the
    artifact is decided after both worlds are computed
    (processed_value_failures). Never sample April or rebuild a parallel world.
    """
    values = {}
    for check in checks:
        for path in check["intended_values"]:
            if path not in values:
                try:
                    node = worlds._resolve_parameter(
                        sim.tax_benefit_system.parameters, path
                    )
                except (AttributeError, IndexError):
                    values[path] = None
                else:
                    values[path] = parameter_scalar(node(f"{check['year']}-01-01"))
    return values


def processed_mismatches(check: dict, values: dict) -> list[dict]:
    """Every path whose processed value differs from the check's intended one."""
    return [
        {
            "code": "processed_value_mismatch",
            **{k: check[k] for k in ("event", "measure_key", "year", "world")},
            "path": path,
            "intended": intended,
            "processed": values.get(path),
        }
        for path, intended in check["intended_values"].items()
        if not processed_values_match(intended, values.get(path))
    ]


def processed_value_failures(
    measure: dict, year: int, artifact: dict, mismatches: list[dict]
) -> tuple[list[dict], list[dict]]:
    """Split a measure-year's mismatches into refusals and recorded notes.

    A mismatch refuses the artifact when it is in the certified current law,
    when the measure is in force that year (from its commences_fy), or when
    the two worlds' totals differ (stage_uk_ab2025.identical_worlds: gov_tax,
    gov_spending, household_net_income and every declared head). A mismatch
    in a year before the measure commences whose worlds come out identical
    moved none of those totals, so it is recorded on the artifact, not
    refused. (policyengine-uk
    2.130.1 rebuilds a construction-time change that starts on a parameter's
    first stated date without its prior law, so a reversal's value appears in
    earlier years: AB2025's high-value council tax surcharge, whose formula
    returns zero before 2028, shows this in 2025 to 2027.)"""
    from pipeline import stage_uk_ab2025 as ab_stage

    commences = measure.get("commences_fy")
    in_force = commences is None or year >= int(commences[:4])
    refusals, notes = [], []
    for mismatch in mismatches:
        if (
            mismatch["world"] == "certified_current_law"
            or in_force
            or not ab_stage.identical_worlds(artifact)
        ):
            refusals.append(mismatch)
        else:
            notes.append({**mismatch, "accepted": "not_in_force_identical_worlds"})
    return refusals, notes


def intended_parameter_check(
    event: str, key: str, year: int, world_name: str, world: dict, current: dict
) -> dict:
    paths = sorted(
        set(world["baseline_reform"] or {}) | set(world["reform_reform"] or {})
    )
    reform = annual_reform(
        world["baseline_reform" if world_name == "baseline_world" else "reform_reform"]
    )
    return {
        "event": event,
        "measure_key": key,
        "year": year,
        "world": world_name,
        "intended_values": {
            path: revisions.intended_value(reform, path, year, lambda p, d: current[p])
            for path in paths
        },
    }


def revision_reform_route(reform: dict | None, revision: dict | None) -> dict | None:
    """A selected blended reversal covers whole fiscal years on either route.

    Older engines edit the annualised tree. Engines exposing dated_reforms
    reprocess construction-time dictionaries against statutory parameters;
    their windows must therefore cover 6 April Y through 5 April Z+1.
    Feature detection follows the actual Scenario entry point, not a version.
    """
    if not reform or not revision:
        return reform
    from policyengine_uk.utils.scenario import Scenario

    if not getattr(Scenario.from_reform(reform), "dated_reforms", None):
        return reform
    return {
        path: {
            (
                f"{start[:4]}-04-06.{int(stop[:4]) + 1}-04-05"
                if path in revision["paths"]
                else window
            ): value
            for window, value in windows.items()
            for start, stop in [window.split(".")]
        }
        for path, windows in reform.items()
    }


def annual_reform(reform: dict | None) -> dict | None:
    """Make the managed dict pathway's January annual lookup explicit.

    The pinned Scenario.from_reform updates an already-processed parameter
    tree, without the raw-tree April fiscal conversion. An October start is
    therefore first visible in the following annual calculation. Preserve
    exactly the January lookups in each authored window; never silently
    assign a part-year reform to the same fiscal-year proxy.
    """
    if reform is None:
        return None
    normalized = {}
    for path, windows in reform.items():
        if not isinstance(windows, dict):
            raise TypeError(f"{path}: executor requires explicit dated reform windows")
        normalized[path] = {}
        for window, value in windows.items():
            try:
                start_text, stop_text = window.split(".")
                start, stop = (
                    date.fromisoformat(start_text),
                    date.fromisoformat(stop_text),
                )
            except (AttributeError, ValueError) as exc:
                raise ValueError(
                    f"{path}: invalid dated reform window {window!r}"
                ) from exc
            first_year = start.year + ((start.month, start.day) != (1, 1))
            last_year = stop.year
            if first_year > last_year or start > stop:
                raise ValueError(
                    f"{path}: reform window {window} contains no 1 January annual lookup"
                )
            annual_window = f"{first_year}-01-01.{last_year}-12-31"
            if (
                annual_window in normalized[path]
                and normalized[path][annual_window] != value
            ):
                raise ValueError(f"{path}: conflicting annual reform windows")
            normalized[path][annual_window] = value
    return normalized


def uc_health_scenario(reform: dict, *, parameter_checks: list[dict] | None = None):
    """Refresh the pinned UC inputs after changing its new-claimant rate.

    The default UK modifier has already fixed uc_LCWRA_element before a
    managed dict reform runs. Reapply the same seeded modifier after the
    parameter update, so both worlds retain the same cohort assignment and
    existing-claimant protections. Other measures keep the ordinary dict
    pathway and its baseline/input behavior.
    """
    from policyengine_uk.scenarios.uc_reform import add_universal_credit_reform
    from policyengine_uk.utils.scenario import Scenario

    parameter_scenario = Scenario.from_reform(reform)

    def apply_and_refresh(sim):
        if getattr(parameter_scenario, "dated_reforms", None):
            # policyengine-uk 2.130 onwards keeps a dict's dated keys in
            # dated_reforms. On a built simulation only Scenario.apply turns
            # every change into an override of the annualised values; the
            # bare modifier applies just single-day keys and paths the
            # statutory tree does not define (utils/scenario.py,
            # _legacy_override_modifier), which would leave this reform inert.
            parameter_scenario.apply(sim)
        else:
            parameter_scenario.simulation_modifier(sim)
        sim.tax_benefit_system.reset_parameter_caches()
        if parameter_checks is None:
            assert_reform_reached(sim, reform)
        # Otherwise the managed runner's readback hook reads this same
        # simulation's tree after construction (check_processed_parameters).
        add_universal_credit_reform(sim)

    return Scenario(simulation_modifier=apply_and_refresh)


def assert_reform_reached(sim, reform: dict) -> None:
    """Refuse a route that left the simulation's processed parameters short
    of the reform: every year whose 1 January lies in a window must read the
    window's value. An engine that silently drops the change would otherwise
    produce an inert reversal."""
    parameters = sim.tax_benefit_system.parameters
    for path, windows in reform.items():
        parameter = parameters.get_child(path)
        for key, value in windows.items():
            start, stop = key.split(".")
            for year in range(int(start[:4]), int(stop[:4]) + 1):
                instant = f"{year}-01-01"
                if not start <= instant <= stop:
                    continue
                actual = parameter(instant)
                if actual is None or abs(float(actual) - float(value)) > 1e-9:
                    raise RuntimeError(
                        f"{path} reads {actual} for {year}, not the reform's "
                        f"{value}: the scenario route did not reach the "
                        "simulation's parameters"
                    )


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
    variant_fields: dict | None = None,
    intended_current_law: dict | None = None,
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
    if variant_fields and "processed_parameter_values" in certified:
        artifact["processed_parameter_values"] = {}
        artifact["parameter_reform_routes"] = {}
        current = (
            intended_current_law
            if intended_current_law is not None
            else certified["processed_parameter_values"]
        )
        for name, simulation in (
            ("baseline_world", baseline),
            ("reform_world", reform),
        ):
            check = intended_parameter_check(
                event, measure["measure_key"], year, name, world, current
            )
            actual = simulation["processed_parameter_values"]
            artifact["processed_parameter_values"][name] = {
                path: {"intended": intended, "processed": actual[path]}
                for path, intended in check["intended_values"].items()
            }
            artifact["parameter_reform_routes"][name] = simulation[
                "parameter_reform_route"
            ]
    if world.get("construction_revision"):
        artifact["construction_revision"] = world["construction_revision"]
    # Legacy artifacts carry no variant fields, so their bytes are unchanged.
    artifact.update(variant_fields or {})
    return artifact


def preflight(variant: dict | None = None) -> dict:
    """The committed pin and the managed release must agree before any run.

    Given the legacy variant record, the run is also isolated like any other
    variant's (packaged certification, engine compiled from its verified
    sources and imported from its own distributions) and the release bundle
    must equal the record's exactly."""
    fiscal.configure_offline()
    worlds.configure_offline()
    if variant is not None:
        variants.isolate_certification_environment()
        variants.isolate_bytecode(variants.RUNTIME_ROOT / variant["variant_id"])
    committed = worlds.preflight()
    managed = fiscal.preflight_certified_dataset()
    if (
        managed["sha256"] != committed["sha256"]
        or fiscal.data_bundle_id(managed["release_bundle"]) != committed["revision"]
    ):
        raise RuntimeError("managed release differs from data/uk/certified_bundle.json")
    if variant is not None:
        import_engine()
        variants.verify_release_bundle(variant, managed["release_bundle"])
        return {**managed, "check_import_origins": True}
    return managed


def import_engine() -> None:
    """Import all three engine packages and check where each came from."""
    import policyengine  # noqa: F401
    import policyengine_core  # noqa: F401
    import policyengine_uk  # noqa: F401

    variants.verify_import_origins()


def variant_identity_fields(variant: dict) -> dict:
    """Artifact and receipt identity of a non-legacy variant; legacy: none."""
    if variants.is_legacy(variant):
        return {}
    return {
        "variant_id": variant["variant_id"],
        "variant_identity_sha256": variant["identity_sha256"],
    }


def check_variant_environment(variant: dict) -> dict:
    """Engine-free: the record is certified and the installed wheels are its own."""
    variants.validate_record(variant)
    return variants.verify_installed(variant)


def variant_pre(
    variant: dict, *, release_bundle: dict, dataset: Path, installed: dict
) -> dict:
    """What every simulation of a non-legacy run is handed."""
    return {
        "release_bundle": release_bundle,
        "sha256": variant["identity"]["dataset"]["sha256"],
        "runtime_dataset_source": str(dataset),
        "installed": installed,
        # A year outside the population's data years must fail, not
        # calculate defaults (compute_uk_obr_costings.run_managed_simulation),
        # and the dataset's whole year set must be the record's data years.
        "require_dataset_years": True,
        "data_years": list(variant["data_years"]),
        "check_import_origins": True,
    }


def variant_preflight(variant: dict, *, dataset_source: Path | None = None) -> dict:
    """Validate a non-legacy variant exactly before any simulation.

    Order matters: the certification environment is isolated before the
    wrapper is imported, and the working directory moves to the runtime
    directory whose ./data holds the verified dataset, where policyengine.py
    6.x materialises its default dataset. Spawned year workers inherit both.
    """
    installed = check_variant_environment(variant)
    variants.isolate_certification_environment()
    fiscal.configure_offline()
    worlds.configure_offline()
    runtime_root = (variants.RUNTIME_ROOT / variant["variant_id"]).resolve()
    dataset = variants.materialize_dataset(variant, runtime_root, source=dataset_source)
    os.chdir(runtime_root)
    variants.isolate_bytecode(runtime_root)
    import policyengine as pe

    import_engine()
    release_bundle = dict(pe.uk.uk_latest.release_bundle)
    variants.verify_release_bundle(variant, release_bundle)
    return variant_pre(
        variant, release_bundle=release_bundle, dataset=dataset, installed=installed
    )


def run_sim(year: int, variables: list[str], reform: dict | None, pre: dict) -> dict:
    reform = annual_reform(reform)
    reform = revision_reform_route(reform, pre.get("construction_revision"))
    scenario = None
    if reform and UC_HEALTH_ELEMENT_PARAMETER in reform:
        scenario = (
            uc_health_scenario(reform, parameter_checks=pre["parameter_checks"])
            if "parameter_checks" in pre
            else uc_health_scenario(reform)
        )
    scenario_kwargs = {"scenario": scenario} if scenario is not None else {}
    if "parameter_checks" in pre:
        scenario_kwargs["parameter_check"] = lambda sim: check_processed_parameters(
            sim, pre["parameter_checks"]
        )
    result = fiscal.run_managed_simulation(
        year=year,
        variables=variables,
        reform=None if scenario is not None else reform,
        runtime_dataset_source=Path(pre["runtime_dataset_source"]),
        expected_dataset_sha256=pre["sha256"],
        include_engine_provenance=True,
        require_dataset_years=pre.get("require_dataset_years", False),
        expected_dataset_years=pre.get("data_years"),
        **scenario_kwargs,
    )
    fiscal.assert_managed_bundle(result["policyengine_bundle"], pre["release_bundle"])
    if "parameter_checks" in pre:
        if "processed_parameter_values" not in result:
            raise RuntimeError(
                "managed simulation did not return processed parameter evidence"
            )
        result["parameter_reform_route"] = {
            "entry_point": "built_simulation_scenario"
            if scenario is not None
            else "construction_reform"
            if reform
            else "certified_current_law",
            "submitted_reform": reform,
        }
    return result


def run_year_job(job: dict) -> dict:
    """One year's baseline and sequential alternate worlds in one process."""
    year = job["year"]
    pre = job["pre"]
    current = pre.get("intended_current_law", {}).get(str(year), {})
    checks = (
        {
            key: {
                name: intended_parameter_check(
                    job["event"], key, year, name, job["runnable"][key], current
                )
                for name in ("baseline_world", "reform_world")
            }
            for key in job["selected"]
        }
        if "intended_current_law" in pre
        else {}
    )
    baseline_pre = pre
    if checks:
        baseline_pre = {
            **pre,
            "parameter_checks": [
                check
                for pair in checks.values()
                for check in pair.values()
                if not job["runnable"][check["measure_key"]][
                    "baseline_reform"
                    if check["world"] == "baseline_world"
                    else "reform_reform"
                ]
            ],
        }
        # Read every touched path even when both announcement worlds modify it.
        baseline_pre["parameter_checks"] += [
            {
                "event": job["event"],
                "measure_key": key,
                "year": year,
                "world": "certified_current_law",
                "intended_values": {
                    path: current[path]
                    for path in pair["baseline_world"]["intended_values"]
                },
            }
            for key, pair in checks.items()
        ]
    started = time.perf_counter()
    print(
        f"[pid {os.getpid()} year {year}] starting certified baseline ({len(job['variables'])} heads)",
        flush=True,
    )
    baseline = run_sim(year, job["variables"], None, baseline_pre)
    # This spawned worker imported the engine itself: check its origin too.
    if pre.get("check_import_origins"):
        variants.verify_import_origins()
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
            alternate_pre = (
                {
                    **pre,
                    "parameter_checks": [checks[key]["baseline_world"]],
                    "construction_revision": world.get("construction_revision"),
                }
                if checks
                else pre
            )
            base = run_sim(year, variables, world["baseline_reform"], alternate_pre)
        reform = baseline
        if world["reform_reform"]:
            print(
                f"[pid {os.getpid()} year {year}] starting {key} reform delta ({world['construction']})",
                flush=True,
            )
            alternate_pre = (
                {
                    **pre,
                    "parameter_checks": [checks[key]["reform_world"]],
                    "construction_revision": world.get("construction_revision"),
                }
                if checks
                else pre
            )
            reform = run_sim(year, variables, world["reform_reform"], alternate_pre)
        artifact = build_artifact(
            measure=measure,
            world=world,
            year=year,
            baseline=base,
            reform=reform,
            certified=baseline,
            registry_sha256=job["registry_sha256"],
            event=job["event"],
            variant_fields=job.get("variant_fields"),
            intended_current_law=current,
        )
        # run_sim refuses a result without processed values whenever checks
        # were requested, so every real run is evaluated here.
        if checks and all(
            "processed_parameter_values" in result
            for result in (baseline, base, reform)
        ):
            # Each world's check against the simulation that computed it;
            # current law against the certified baseline.
            mismatches = processed_mismatches(
                checks[key]["baseline_world"], base["processed_parameter_values"]
            ) + processed_mismatches(
                checks[key]["reform_world"], reform["processed_parameter_values"]
            )
            mismatches += processed_mismatches(
                {
                    **checks[key]["baseline_world"],
                    "world": "certified_current_law",
                    "intended_values": {
                        path: current[path]
                        for path in checks[key]["baseline_world"]["intended_values"]
                    },
                },
                baseline["processed_parameter_values"],
            )
            refusals, notes = processed_value_failures(
                measure, year, artifact, mismatches
            )
            if refusals:
                raise ProcessedValueMismatch(refusals[0])
            if notes:
                artifact["processed_value_notes"] = notes
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
        **(job.get("variant_fields") or {}),
        **(
            {"construction_revisions": job["construction_revisions"]}
            if job.get("construction_revisions")
            else {}
        ),
        "artifacts": artifacts,
    }


def retained_artifact_digests(
    output_dir: Path,
    *,
    event: str,
    years: list[int],
    registry_sha256: str,
    pre: dict,
    variant_fields: dict | None = None,
    construction_revisions: dict | None = None,
) -> dict[str, str]:
    """Read only SHA-bound completed outputs; unreceipted files are ignored."""
    variant_fields = variant_fields or {}
    construction_revisions = construction_revisions or {}
    receipts = []
    manifest_path = output_dir / "RUN_MANIFEST.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_bytes())
        if (
            manifest.get("event") == event
            and manifest.get("registry_sha256") == registry_sha256
            and manifest.get("certified_dataset_sha256") == pre["sha256"]
            and all(manifest.get(k) == v for k, v in variant_fields.items())
            and manifest.get("construction_revisions", {}) == construction_revisions
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
                "variant_fields": variant_fields,
                "construction_revisions": construction_revisions,
            },
            {},
        )
        if receipt.get("construction_revisions", {}) == construction_revisions and all(
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


def validate_variant_years(
    requested: list[int], registry: dict, variant: dict
) -> list[int]:
    """Registry years the variant's population supports.

    A year before the dataset's first time period computes without error but
    from absent inputs (a 2023 income tax of zero on a 2024 dataset), so an
    unsupported year is refused, never run; by default it is reported.
    """
    allowed = registry.get("calendar_years")
    if not allowed:
        raise ValueError("registry must record the supported calendar_years")
    supported, unsupported = variants.supported_years(variant, allowed)
    if not supported:
        raise ValueError(
            f"{variant['variant_id']} supports none of this event's years {allowed}"
        )
    years = sorted(set(requested or supported))
    if set(years) - set(allowed):
        raise ValueError(
            f"years {years} outside this event's documented support {allowed}"
        )
    refused = sorted(set(years) - set(supported))
    if refused:
        raise ValueError(
            f"years {refused} are outside {variant['variant_id']}'s data years "
            f"{variant['data_years'][0]}-{variant['data_years'][-1]}: "
            f"{[row for row in unsupported if row['year'] in refused]}"
        )
    return years


def verify_registry_identity(path: Path, expected_sha256: str) -> None:
    if fiscal.sha256_file(path) != expected_sha256:
        raise ValueError(
            "registry bytes changed after planning; refusing simulation or publication"
        )


def revised_worlds(runnable: dict) -> dict:
    """Read selection metadata from the installed engine, only if needed."""
    parameters = None

    def metadata(path):
        nonlocal parameters
        if parameters is None:
            import policyengine_uk

            parameters = policyengine_uk.CountryTaxBenefitSystem().parameters
        node = worlds._resolve_parameter(parameters, path)
        return dict(getattr(node, "metadata", None) or {})

    return {
        key: revisions.apply_revision(key, world, metadata)
        for key, world in runnable.items()
    }


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
    ap.add_argument(
        "--variant",
        help="certified replay variant (data/uk/replay_variants.json); default: the file's default",
    )
    ap.add_argument(
        "--variants-file",
        type=Path,
        default=variants.VARIANTS_PATH,
        help="variant records to select from (a qualification run adds its candidate)",
    )
    ap.add_argument(
        "--dataset-file",
        type=Path,
        help="a local file holding the variant's certified dataset bytes (verified by SHA-256)",
    )
    ap.add_argument(
        "--allow-uncertified",
        action="store_true",
        help="replay a candidate variant (qualification runs only)",
    )
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
    variant = variants.get_variant(
        args.variant,
        path=args.variants_file.resolve(),
        allow_uncertified=args.allow_uncertified,
    )
    legacy = variants.is_legacy(variant)
    if legacy and args.dataset_file is not None:
        raise ValueError(
            "--dataset-file applies to a variant that materialises its dataset; "
            "the legacy variant reads its pinned Hugging Face cache"
        )
    variant_fields = variant_identity_fields(variant)
    default_registry, default_output = event_paths(args.event)
    if not legacy:
        default_output = variants.event_output_dir(variant, args.event)
    # Absolute before a variant preflight moves into its runtime directory.
    registry_path = (args.registry or default_registry).resolve()
    output_dir = (args.output_dir or default_output).resolve()
    if args.dataset_file is not None:
        args.dataset_file = args.dataset_file.resolve()
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
    years = (
        validate_years(args.years or [], registry)
        if legacy
        else validate_variant_years(args.years or [], registry, variant)
    )
    index = {measure["measure_key"]: measure for measure in registry["measures"]}
    planned = worlds.computable(index, years=years)
    runnable = {key: world for key, world in planned.items() if "alias_of" not in world}
    selected = args.measures or list(runnable)
    if set(selected) - set(runnable):
        raise ValueError(f"not executable: {sorted(set(selected) - set(runnable))}")
    for key in selected:
        variable_channels(index[key])
        annual_reform(runnable[key]["baseline_reform"])
        annual_reform(runnable[key]["reform_reform"])
    coverage = worlds.world_coverage_gaps(index, years=years)
    if coverage:
        raise ValueError("\n".join(coverage))
    if args.dry_run or args.guards:
        if args.guards:
            # --guards reads the installed engine: check it is the certified
            # one and compile it from its verified sources.
            check_variant_environment(variant)
            variants.isolate_bytecode(variants.RUNTIME_ROOT / variant["variant_id"])
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
            if args.guards:
                import_engine()
            guard = "every reversal delta restates certified current law"
            runnable = revised_worlds(runnable)
        plan = {
            "event": args.event,
            "years": years,
            "selected": selected,
            "not_computable": worlds.not_computable(index, years=years),
            "guard": guard,
            "annual_lookup_reforms": {
                key: {
                    field: annual_reform(runnable[key][field])
                    for field in ("baseline_reform", "reform_reform")
                }
                for key in selected
            },
        }
        if not legacy:
            supported, unsupported = variants.supported_years(
                variant, registry["calendar_years"]
            )
            plan.update(
                variant_fields,
                supported_years=supported,
                unsupported_years=unsupported,
                output_dir=fiscal.relative_to_root(output_dir),
            )
        selected_revisions = {
            key: world["construction_revision"]
            for key, world in runnable.items()
            if world.get("construction_revision")
        }
        if selected_revisions:
            plan["construction_revisions"] = selected_revisions
        print(json.dumps(plan, indent=1, sort_keys=True))
        return 0
    started = time.perf_counter()
    variants.assert_not_sealed(output_dir)
    verify_registry_identity(registry_path, registry_sha256)
    print(f"[pid {os.getpid()}] starting offline bundle preflight", flush=True)
    if legacy:
        check_variant_environment(variant)
    pre = (
        preflight(variant)
        if legacy
        else variant_preflight(variant, dataset_source=args.dataset_file)
    )
    print(
        f"[pid {os.getpid()}] offline bundle preflight complete; starting processed-world reversal guard",
        flush=True,
    )
    resolve = worlds.engine_resolver()
    gaps = worlds.reversal_delta_mismatches(index, resolve, years=years)
    gc.collect()
    if gaps:
        raise ValueError("\n".join(gaps))
    runnable = revised_worlds(runnable)
    selected_revisions = {
        key: world["construction_revision"]
        for key, world in runnable.items()
        if world.get("construction_revision")
    }
    paths = sorted(
        {
            path
            for world in runnable.values()
            for field in ("baseline_reform", "reform_reform")
            for path in (world[field] or {})
        }
    )
    pre["intended_current_law"] = {
        str(year): {
            path: parameter_scalar(resolve(path, f"{year}-01-01")) for path in paths
        }
        for year in years
    }
    print(f"[pid {os.getpid()}] processed-world reversal guard complete", flush=True)
    verify_registry_identity(registry_path, registry_sha256)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "INTEGRITY_FAILURES.json").unlink(missing_ok=True)
    supported_calendar_years = (
        registry["calendar_years"]
        if legacy
        else variants.supported_years(variant, registry["calendar_years"])[0]
    )
    previous_digests = retained_artifact_digests(
        output_dir,
        event=args.event,
        years=supported_calendar_years,
        registry_sha256=registry_sha256,
        pre=pre,
        variant_fields=variant_fields,
        construction_revisions=selected_revisions,
    )
    requested_pairs = {(key, year) for key in selected for year in years}
    full_pairs = {
        (key, year) for key in runnable for year in registry["calendar_years"]
    }
    supported_pairs = {
        (key, year) for key, year in full_pairs if year in supported_calendar_years
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
        if (key, year) not in supported_pairs:
            # No artifact exists for a year the population cannot supply,
            # whatever an older receipt says (RELEASE_REPLAY.md).
            raise ValueError(
                f"retained receipt names {key} {year}, outside the variant's "
                "supported years"
            )
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
                for field, value in {**runtime_versions(), **variant_fields}.items()
            )
            or previous.get("construction_revision")
            != runnable[key].get("construction_revision")
            or (not legacy and "processed_parameter_values" not in previous)
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
                    "variant_fields": variant_fields,
                    "construction_revisions": selected_revisions,
                    "retained_artifacts": {
                        str(
                            (output_dir / f"{key}_{year}.json").relative_to(ROOT)
                        ): digest
                        for (key, retained_year), digest in committed.items()
                        if retained_year == year
                    },
                }
            )
    try:
        if args.workers == 1:
            for job in jobs:
                result = run_year_job(job)
                artifacts.update(result["artifacts"])
                timings.extend(result["timings"])
        elif jobs:
            for result in parallel_year_results(jobs, args.workers):
                artifacts.update(result["artifacts"])
                timings.extend(result["timings"])
    except ProcessedValueMismatch as exc:
        fiscal.atomic_write_bytes(
            output_dir / "INTEGRITY_FAILURES.json", canonical_bytes([exc.failure])
        )
        raise
    verify_registry_identity(registry_path, registry_sha256)
    for key, evidence in selected_revisions.items():
        revisions.get_revision(key, evidence)
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
        **(
            {"construction_revisions": selected_revisions} if selected_revisions else {}
        ),
    }
    if not legacy:
        manifest["processed_value_check"] = "processed_period_values.v1"
        manifest.update(
            variants.manifest_fields(
                variant,
                registry["calendar_years"],
                full_pairs,
                supported_pairs,
                artifact_pairs,
            )
        )
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
