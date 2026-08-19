"""Run one managed Medicaid simulation and write a person extract.

Run this program once for baseline and again in a separate OS process for the
100%-take-up world.  The reform process sets the annual Medicaid take-up input
before any calculation.  It also receives the baseline allocation denominator
as an execution input, reproducing policyengine-us's intended baseline-branch
cost behavior without retaining two multi-GB simulations in memory.
"""

from __future__ import annotations

import argparse
import gc
import json
import os
import sys
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

import numpy as np
import pandas as pd

try:
    from pipeline.build_kff_medicaid_outputs import require_certified_provenance
except ImportError:  # executed as a script from inside pipeline/
    from build_kff_medicaid_outputs import require_certified_provenance

YEAR = 2024
TAKEUP = "takes_up_medicaid_if_eligible"
DENOMINATOR = "medicaid_slcsp_state_denominator"
EXPECTED_DATASET_URI = (
    "hf://policyengine/populace-us/populace_us_2024.h5@"
    "populace-us-2024-buildp-sparse-rmloss100-cae8640-20260728T011454Z"
)
EXPECTED_BUILD = "populace-us-2024-buildp-sparse-rmloss100-cae8640-20260728T011454Z"
COVERAGE_INPUTS = (
    "has_esi",
    "has_marketplace_health_coverage_at_interview",
    "has_non_marketplace_direct_purchase_health_coverage_at_interview",
    "has_medicaid_health_coverage_at_interview",
    "has_tricare_health_coverage_at_interview",
    "has_va_health_coverage_at_interview",
    "has_champva_health_coverage_at_interview",
    "has_other_means_tested_health_coverage_at_interview",
    "has_indian_health_service_coverage_at_interview",
)
MEDICARE_PROXY = "medicare_enrolled"
CATEGORY_PATHWAYS = (
    # This order mirrors medicaid_category.formula in policyengine-us 1.764.6.
    "is_ssi_recipient_for_medicaid",
    "is_infant_for_medicaid",
    "is_young_child_for_medicaid",
    "is_older_child_for_medicaid",
    "is_pregnant_for_medicaid",
    "is_parent_for_medicaid",
    "is_young_adult_for_medicaid",
    "is_adult_for_medicaid",
    "is_optional_senior_or_disabled_for_medicaid",
    "is_medically_needy_for_medicaid",
    "is_working_disabled_buy_in_for_medicaid",
    "is_medicaid_1115_mec_adult",
)
MISSISSIPPI_WAIVER_PATHWAY = "ms_hmw_eligible"


def log(message: str) -> None:
    print(message, file=sys.stderr, flush=True)


def release_loaded_dataset_frames(sim) -> int:
    """Release HDF DataFrames after core has copied inputs into holders.

    policyengine-us's entity-HDF adapter retains every source DataFrame on
    ``sim.dataset`` after ``build_from_dataset`` has populated the simulation.
    Formula evaluation reads holders, not those frames.  Replacing the retained
    frames with empty frames avoids keeping a second multi-GB copy while
    preserving the managed dataset object's name, period, and cache metadata.
    """
    released = 0
    datasets = getattr(sim.dataset, "datasets", {})
    for single_year in datasets.values():
        empty_tables = []
        for name in single_year.table_names:
            frame = getattr(single_year, name)
            released += int(frame.memory_usage(index=True, deep=True).sum())
            empty = pd.DataFrame()
            setattr(single_year, name, empty)
            empty_tables.append(empty)
        single_year.tables = tuple(empty_tables)
    gc.collect()
    return released


def clear_formula_caches(sim, keep: set[str] | None = None) -> int:
    """Drop calculated holders while retaining dataset and explicit inputs."""
    keep = set(keep or ())
    keep.update(sim.input_variables)
    keep.update(key[0] for key in getattr(sim, "_user_input_keys", set()))
    cleared = 0
    for population in sim.populations.values():
        for name, holder in population._holders.items():
            if name in keep:
                continue
            usage = holder.get_memory_usage()["total_nb_bytes"]
            if holder.get_known_periods():
                holder.delete_arrays()
                cleared += int(usage)
    sim._fast_cache.clear()
    gc.collect()
    return cleared


def calculate_medicaid_eligibility(sim) -> tuple[np.ndarray, list[str]]:
    """Calculate native Medicaid eligibility with bounded formula-cache use.

    ``medicaid_category`` selects from several independent eligibility
    pathways. Evaluating it in one expression retains every pathway's full
    dependency graph at once, which exceeds the memory available for the
    certified file. Materializing each configured pathway as a temporary
    execution input lets PolicyEngine clear that pathway's dependencies before
    moving to the next one. The final value still comes from the native
    ``is_medicaid_eligible`` formula, including immigration, state-coverage,
    and any active work-requirement legs.
    """
    parameters = sim.tax_benefit_system.parameters(YEAR)
    covered = set(parameters.gov.hhs.medicaid.eligibility.categories.covered)
    pathways = [name for name in CATEGORY_PATHWAYS if name in covered]
    pathways.append(MISSISSIPPI_WAIVER_PATHWAY)

    for pathway in pathways:
        log(f"calculating Medicaid category pathway: {pathway}")
        result = values(sim, pathway).astype(bool)
        sim.set_input(pathway, YEAR, result)
        cleared = clear_formula_caches(sim, {pathway})
        log(f"materialized {pathway}; cleared {cleared / 1e9:.2f} GB")

    log("calculating native is_medicaid_eligible from materialized pathways")
    return values(sim, "is_medicaid_eligible").astype(bool), pathways


def serializable(value):
    if isinstance(value, dict):
        return {str(key): serializable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serializable(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def values(sim, variable: str, *, map_to: str | None = None) -> np.ndarray:
    kwargs = {"map_to": map_to} if map_to else {}
    return np.asarray(sim.calculate(variable, YEAR, **kwargs).values)


def variable_metadata(sim, variable: str) -> dict:
    definition = sim.tax_benefit_system.variables[variable]
    return {
        "label": definition.label,
        "entity": definition.entity.key,
        "definition_period": str(definition.definition_period),
        "unit": str(getattr(definition, "unit", None)),
        "documentation": getattr(definition, "documentation", None),
    }


def run(
    mode: str,
    output: Path,
    dataset: Path | None,
    baseline_extract: Path | None,
) -> dict:
    import policyengine as pe
    import policyengine_us
    from policyengine_core.periods import YEAR as YEAR_PERIOD

    started = datetime.now(timezone.utc).isoformat()
    log(f"constructing {mode} managed simulation")
    if dataset is None:
        sim = pe.us.managed_microsimulation()
    else:
        sim = pe.us.managed_microsimulation(
            dataset=str(dataset),
            allow_unmanaged=True,
        )
    bundle = serializable(dict(sim.policyengine_bundle))
    engine_version = getattr(policyengine_us, "__version__", None) or version(
        "policyengine-us"
    )
    # Validate provenance BEFORE any computation or output write, so a
    # rejected rerun can never replace an existing certified CSV.
    if bundle.get("model_version") != engine_version:
        raise AssertionError(
            f"engine {engine_version} != bundle model {bundle.get('model_version')}"
        )
    if dataset is None:
        if bundle.get("default_dataset_uri") != EXPECTED_DATASET_URI:
            raise AssertionError("managed dataset URI differs from certified pin")
        if bundle.get("certified_data_build_id") != EXPECTED_BUILD:
            raise AssertionError("managed data build differs from certified pin")
        require_certified_provenance(
            engine_version,
            bundle.get("bundle_id"),
            bundle.get("certified_data_build_id"),
        )
    released_dataset_bytes = release_loaded_dataset_frames(sim)
    log(
        f"managed simulation ready; released {released_dataset_bytes / 1e9:.2f} GB "
        "of retained source frames"
    )

    variables = sim.tax_benefit_system.variables
    assert variables[TAKEUP].definition_period == YEAR_PERIOD
    n_people = sim.populations["person"].count
    baseline_ids = None
    baseline_eligibility = None
    denominator_preserved = False
    eligibility_preserved = False
    if mode == "reform":
        if baseline_extract is None:
            raise ValueError("reform mode requires --baseline-extract")
        baseline = pd.read_csv(
            baseline_extract,
            usecols=["person_id", "is_medicaid_eligible", DENOMINATOR],
        )
        if len(baseline) != n_people:
            raise ValueError(
                f"baseline has {len(baseline)} people; reform has {n_people}"
            )
        baseline_ids = baseline["person_id"].to_numpy()
        baseline_eligibility = baseline["is_medicaid_eligible"].to_numpy(dtype=bool)
        baseline_denominator = baseline[DENOMINATOR].to_numpy(dtype=float)
        sim.set_input(TAKEUP, YEAR, np.ones(n_people, dtype=bool))
        sim.set_input("is_medicaid_eligible", YEAR, baseline_eligibility)
        sim.set_input(DENOMINATOR, YEAR, baseline_denominator)
        denominator_preserved = True
        eligibility_preserved = True
        log(
            "annual take-up input set; policy-invariant baseline eligibility "
            "and cost denominator supplied"
        )

    log("calculating identifiers, demographics, and coverage")
    person_id = values(sim, "person_id").astype(np.int64)
    if baseline_ids is not None and not np.array_equal(person_id, baseline_ids):
        raise ValueError("baseline and reform person ordering differs")

    age = values(sim, "age").astype(float)
    state = values(sim, "state_code", map_to="person").astype(str)
    weight = values(sim, "person_weight").astype(float)
    coverage = {name: values(sim, name).astype(bool) for name in COVERAGE_INPUTS}
    medicare = values(sim, MEDICARE_PROXY).astype(bool)
    has_coverage = medicare.copy()
    for covered in coverage.values():
        has_coverage |= covered
    reported_uninsured = ~has_coverage
    cleared = clear_formula_caches(sim)
    log(f"cleared {cleared / 1e9:.2f} GB of preliminary formula caches")

    log("calculating Medicaid eligibility")
    if baseline_eligibility is None:
        eligible, materialized_pathways = calculate_medicaid_eligibility(sim)
        log("Medicaid eligibility complete; materializing it as an execution input")
        sim.set_input("is_medicaid_eligible", YEAR, eligible)
        eligibility_execution = (
            "Native is_medicaid_eligible formula after sequentially "
            "materializing its configured medicaid_category pathways as "
            "execution inputs to bound cache memory."
        )
    else:
        eligible = values(sim, "is_medicaid_eligible").astype(bool)
        materialized_pathways = []
        eligibility_execution = (
            "Policy-invariant 2024 eligibility loaded from the separate "
            "certified baseline extract; the take-up input does not enter the "
            "eligibility formula."
        )
    cleared = clear_formula_caches(sim, {"is_medicaid_eligible"})
    log(f"cleared {cleared / 1e9:.2f} GB of eligibility dependencies")

    log("calculating Medicaid enrollment")
    enrolled = values(sim, "medicaid_enrolled").astype(bool)
    sim.set_input("medicaid_enrolled", YEAR, enrolled)
    cleared = clear_formula_caches(
        sim,
        {"is_medicaid_eligible", "medicaid_enrolled"},
    )
    log(f"cleared {cleared / 1e9:.2f} GB of enrollment dependencies")

    log("calculating Medicaid spending")
    medicaid = values(sim, "medicaid").astype(float)
    denominator = values(sim, DENOMINATOR).astype(float)
    log("Medicaid spending complete")
    modeled_uninsured = reported_uninsured & ~enrolled

    if mode == "reform" and not np.array_equal(enrolled, eligible):
        raise AssertionError("100%-take-up enrollment does not equal eligibility")
    expected_states = {
        "AL",
        "AK",
        "AZ",
        "AR",
        "CA",
        "CO",
        "CT",
        "DE",
        "DC",
        "FL",
        "GA",
        "HI",
        "ID",
        "IL",
        "IN",
        "IA",
        "KS",
        "KY",
        "LA",
        "ME",
        "MD",
        "MA",
        "MI",
        "MN",
        "MS",
        "MO",
        "MT",
        "NE",
        "NV",
        "NH",
        "NJ",
        "NM",
        "NY",
        "NC",
        "ND",
        "OH",
        "OK",
        "OR",
        "PA",
        "RI",
        "SC",
        "SD",
        "TN",
        "TX",
        "UT",
        "VT",
        "VA",
        "WA",
        "WV",
        "WI",
        "WY",
    }
    observed_states = set(state)
    if dataset is None and observed_states != expected_states:
        raise AssertionError(
            f"full artifact state set differs: {sorted(observed_states)}"
        )
    if dataset is not None and not observed_states <= expected_states:
        raise AssertionError(f"sample has unexpected states: {sorted(observed_states)}")

    frame = pd.DataFrame(
        {
            "person_id": person_id,
            "state": state,
            "age": age,
            "person_weight": weight,
            "is_medicaid_eligible": eligible,
            "medicaid_enrolled": enrolled,
            "medicaid": medicaid,
            DENOMINATOR: denominator,
            "reported_uninsured": reported_uninsured,
            "modeled_uninsured": modeled_uninsured,
            MEDICARE_PROXY: medicare,
        }
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    csv_tmp = output.with_name(output.name + ".tmp")
    frame.to_csv(csv_tmp, index=False, compression="gzip")

    calculated = (
        "person_id",
        "state_code",
        "age",
        "person_weight",
        *COVERAGE_INPUTS,
        MEDICARE_PROXY,
        "is_medicaid_eligible",
        "medicaid_enrolled",
        "medicaid",
        DENOMINATOR,
    )
    assert "chip" not in calculated and "early_head_start" not in calculated
    metadata = {
        "mode": mode,
        "period": YEAR,
        "sample": dataset is not None,
        "dataset": str(dataset) if dataset is not None else None,
        "engine_version": engine_version,
        "engine_version_source": (
            "policyengine_us.__version__"
            if getattr(policyengine_us, "__version__", None)
            else "importlib.metadata (module has no __version__ attribute)"
        ),
        "data_bundle": bundle.get("certified_data_build_id"),
        "bundle_id": bundle.get("bundle_id"),
        "policyengine_bundle": bundle,
        "computed_at": datetime.now(timezone.utc).isoformat(),
        "started_at": started,
        "people": n_people,
        "released_dataset_frame_bytes": released_dataset_bytes,
        "eligibility_execution": eligibility_execution,
        "materialized_medicaid_category_pathways": materialized_pathways,
        "calculated_variables": list(calculated),
        "coverage_inputs": list(COVERAGE_INPUTS),
        "medicare_handling": (
            "medicare_enrolled is the modeled under-65 Medicare proxy; all other "
            "coverage inputs are reported at interview"
        ),
        "reported_uninsured_definition": (
            "none of coverage_inputs and not medicare_enrolled; age<65 is "
            "applied during moment aggregation"
        ),
        "modeled_uninsured_definition": (
            "reported_uninsured and not medicaid_enrolled"
        ),
        "takeup_definition_period": str(variables[TAKEUP].definition_period),
        "takeup_forced_true": mode == "reform",
        "baseline_eligibility_preserved": eligibility_preserved,
        "baseline_denominator_preserved": denominator_preserved,
        "denominator_note": (
            "The baseline Medicaid state-allocation denominator is supplied in "
            "the reform process to reproduce the engine's baseline-branch cost "
            "semantics without holding two simulations in memory."
            if denominator_preserved
            else "Baseline engine value extracted for the reform process."
        ),
        "variables": {name: variable_metadata(sim, name) for name in calculated},
    }
    # Publish the CSV and its metadata sidecar together at the end, via
    # temp-and-rename, so no earlier failure can leave a fresh CSV beside a
    # stale certified sidecar. (A hard crash between the two renames is the
    # remaining narrow window.)
    meta_tmp = Path(f"{output}.meta.json.tmp")
    meta_tmp.write_text(json.dumps(metadata, indent=2) + "\n")
    os.replace(csv_tmp, output)
    os.replace(meta_tmp, Path(f"{output}.meta.json"))
    log(f"wrote {len(frame)} person rows to {output}")
    print(
        json.dumps(
            {key: metadata[key] for key in metadata if key != "variables"}, indent=2
        )
    )
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("baseline", "reform"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dataset", type=Path)
    parser.add_argument("--baseline-extract", type=Path)
    args = parser.parse_args()
    run(args.mode, args.output, args.dataset, args.baseline_extract)


if __name__ == "__main__":
    main()
