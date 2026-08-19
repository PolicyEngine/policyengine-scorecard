"""Aggregate Medicaid baseline/reform extracts into scorecard staging files.

Standard-library only, like the other pipeline modules: CI runs the test
suite without pandas, so extracts are read as typed columns and masks are
plain boolean lists.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import math
from datetime import datetime, timezone
from pathlib import Path

YEAR = 2024
RUN_ID = "campaign-2026-08-18-kff-medicaid"
DENOMINATOR = "medicaid_slcsp_state_denominator"
NON_EXPANSION_2024 = {"AL", "FL", "GA", "KS", "MS", "SC", "TN", "TX", "WI", "WY"}
REPORTED_VARIANT = "pe_reported_uninsured_all_medicaid_pathways_2024_rules"
MODELED_VARIANT = "pe_modeled_uninsured_all_medicaid_pathways_2024_rules"
REFORM_REF = {
    "framework": "policyengine_us_inputs",
    "reform": {"takes_up_medicaid_if_eligible": True},
}
BOOL_COLUMNS = (
    "is_medicaid_eligible",
    "medicaid_enrolled",
    "reported_uninsured",
    "modeled_uninsured",
)
FINITE_FLOAT_COLUMNS = ("age", "person_weight", "medicaid")
NAN_ALLOWED_FLOAT_COLUMNS = (DENOMINATOR,)
CERTIFIED_PROVENANCE = {
    "engine_version": "1.764.6",
    "bundle_id": "us-5.0.2",
    "data_bundle": "populace-us-2024-buildp-sparse-rmloss100-cae8640-20260728T011454Z",
}


def load_meta(path: Path) -> dict:
    return json.loads(Path(f"{path}.meta.json").read_text())


def require_certified_provenance(
    engine_version: str, bundle_id: str, data_bundle: str
) -> None:
    """Hard-pin full-file provenance to the certified triple.

    Self-reported sidecar provenance is not trusted on the full path: a
    wrong-but-self-consistent triple must fail. Update CERTIFIED_PROVENANCE
    deliberately when re-running on a newer certified bundle.
    """
    actual = {
        "engine_version": engine_version,
        "bundle_id": bundle_id,
        "data_bundle": data_bundle,
    }
    if actual != CERTIFIED_PROVENANCE:
        raise ValueError(
            f"full-file provenance {actual} does not match the certified pin "
            f"{CERTIFIED_PROVENANCE}"
        )


def _parse_bool(text: str) -> bool:
    if text in ("True", "true", "1"):
        return True
    if text in ("False", "false", "0"):
        return False
    raise ValueError(f"not a boolean: {text!r}")


def _parse_lenient_float(text: str) -> float:
    return math.nan if text == "" else float(text)


def _parse_finite_float(text: str, column: str) -> float:
    if text == "":
        raise ValueError(f"blank value in required numeric column {column}")
    value = float(text)
    if not math.isfinite(value):
        raise ValueError(f"non-finite value {text!r} in column {column}")
    return value


def load_extract(path: Path) -> dict[str, list]:
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []
        columns: dict[str, list] = {name: [] for name in fieldnames}
        for row in reader:
            for name in fieldnames:
                columns[name].append(row[name])
    for name in BOOL_COLUMNS:
        columns[name] = [_parse_bool(text) for text in columns[name]]
    for name in FINITE_FLOAT_COLUMNS:
        columns[name] = [_parse_finite_float(text, name) for text in columns[name]]
    for name in NAN_ALLOWED_FLOAT_COLUMNS:
        columns[name] = [_parse_lenient_float(text) for text in columns[name]]
    return columns


def _close(actual: float, expected: float) -> bool:
    if math.isnan(actual) and math.isnan(expected):
        return True
    return abs(actual - expected) <= 1e-8 + 1e-5 * abs(expected)


def _and(*masks: list[bool]) -> list[bool]:
    return [all(values) for values in zip(*masks)]


def _not(mask: list[bool]) -> list[bool]:
    return [not value for value in mask]


def weighted_count(columns: dict[str, list], mask: list[bool]) -> float:
    return float(
        sum(
            weight
            for weight, selected in zip(columns["person_weight"], mask)
            if selected
        )
    )


def weighted_dollars(columns: dict[str, list], mask: list[bool] | None = None) -> float:
    if mask is None:
        mask = [True] * len(columns["person_weight"])
    return float(
        sum(
            weight * dollars
            for weight, dollars, selected in zip(
                columns["person_weight"], columns["medicaid"], mask
            )
            if selected
        )
    )


def aggregate(
    baseline_path: Path,
    reform_path: Path,
    diagnostics_dir: Path,
    counterpart_path: Path,
    campaign_path: Path,
    full: bool,
) -> dict:
    baseline = load_extract(baseline_path)
    reform = load_extract(reform_path)
    baseline_meta = load_meta(baseline_path)
    reform_meta = load_meta(reform_path)
    people = len(baseline["person_weight"])
    if people != len(reform["person_weight"]):
        raise ValueError("baseline and reform row counts differ")
    if baseline["person_id"] != reform["person_id"]:
        raise ValueError("baseline and reform people differ")
    if baseline["state"] != reform["state"]:
        raise ValueError("baseline and reform states differ")
    if not all(map(_close, baseline["person_weight"], reform["person_weight"])):
        raise ValueError("baseline and reform weights differ")
    if baseline["is_medicaid_eligible"] != reform["is_medicaid_eligible"]:
        raise ValueError("eligibility changed under the take-up input")
    if baseline["reported_uninsured"] != reform["reported_uninsured"]:
        raise ValueError("reported coverage changed under the take-up input")
    if not all(map(_close, baseline[DENOMINATOR], reform[DENOMINATOR])):
        raise ValueError("reform did not retain the baseline Medicaid denominator")
    eligible = baseline["is_medicaid_eligible"]
    enrolled = baseline["medicaid_enrolled"]
    reform_enrolled = reform["medicaid_enrolled"]
    if reform_enrolled != eligible:
        raise AssertionError("reform enrollment is not identical to eligibility")
    if any(_and(enrolled, _not(reform_enrolled))):
        raise AssertionError("the reform removes baseline enrollees")
    marginal = _and(reform_enrolled, _not(enrolled))
    reported = baseline["reported_uninsured"]
    modeled = baseline["modeled_uninsured"]
    under65 = [age < 65 for age in baseline["age"]]
    child = [age < 19 for age in baseline["age"]]
    adult = _and(under65, _not(child))
    states = sorted(set(baseline["state"]))
    geographies = ["US", *states]
    expansion_states = set(states) - NON_EXPANSION_2024
    computed_at = datetime.now(timezone.utc).isoformat()

    engine_version = baseline_meta["engine_version"]
    data_bundle = baseline_meta["data_bundle"]
    bundle_id = baseline_meta["bundle_id"]
    if (engine_version, data_bundle, bundle_id) != (
        reform_meta["engine_version"],
        reform_meta["data_bundle"],
        reform_meta["bundle_id"],
    ):
        raise ValueError("baseline and reform provenance differs")
    for label, metadata in (("baseline", baseline_meta), ("reform", reform_meta)):
        bundle = metadata.get("policyengine_bundle")
        if not isinstance(bundle, dict):
            raise ValueError(f"{label} policyengine_bundle is missing")
        top_level = (
            metadata["engine_version"],
            metadata["data_bundle"],
            metadata["bundle_id"],
        )
        nested = (
            bundle.get("model_version"),
            bundle.get("certified_data_build_id"),
            bundle.get("bundle_id"),
        )
        if nested != top_level:
            raise ValueError(f"{label} policyengine_bundle identifiers differ")
    baseline_sample = baseline_meta.get("sample")
    reform_sample = reform_meta.get("sample")
    if not isinstance(baseline_sample, bool) or not isinstance(reform_sample, bool):
        raise ValueError("baseline and reform sample provenance must be boolean")
    if baseline_sample != reform_sample:
        raise ValueError("baseline and reform sample provenance differs")
    if full and baseline_sample:
        raise ValueError("--full cannot be used with validation-sample extracts")
    if not full and not baseline_sample:
        raise ValueError("full-file extracts require --full and its anchor gates")
    if full:
        require_certified_provenance(engine_version, bundle_id, data_bundle)

    national_eligible = weighted_count(baseline, eligible)
    national_enrolled = weighted_count(baseline, enrolled)
    national_delta = weighted_count(baseline, marginal)
    identity_gap = national_delta - (national_eligible - national_enrolled)
    if not abs(identity_gap) <= 1e-6 * max(national_delta, 1):
        raise AssertionError(f"enrollment identity gap {identity_gap}")
    if full:
        anchors = {
            "eligible": (national_eligible, 77_300_000),
            "enrolled": (national_enrolled, 72_300_000),
        }
        for name, (actual, expected) in anchors.items():
            relative_error = abs(actual / expected - 1)
            if not relative_error <= 0.02:
                raise SystemExit(
                    f"STOP: {name} anchor {actual:,.0f} differs from "
                    f"{expected:,.0f} by {relative_error:.2%}"
                )

    common = {
        "engine_version": engine_version,
        "data_bundle": data_bundle,
        "bundle_id": bundle_id,
        "sample": baseline_sample,
        "computed_at": computed_at,
        "benchmark_class": "different_model",
        "calibration_relationship": "held_out",
        "rules_vintage": "PolicyEngine 2024 law",
        "coverage_inputs": baseline_meta["coverage_inputs"],
        "medicare_handling": baseline_meta["medicare_handling"],
    }
    moment_diagnostics = []
    counterpart_rows = []
    variants = (
        ("reported_uninsured", REPORTED_VARIANT, reported),
        ("modeled_uninsured", MODELED_VARIANT, modeled),
    )
    for geography in geographies:
        geo_mask = (
            [True] * people
            if geography == "US"
            else [state == geography for state in baseline["state"]]
        )
        for coverage_variant, variant, uninsured in variants:
            universe = _and(geo_mask, under65, uninsured)
            numerator_mask = _and(universe, eligible)
            denominator = weighted_count(baseline, universe)
            numerator = weighted_count(baseline, numerator_mask)
            share = 100 * numerator / denominator if denominator else None
            moment_diagnostics.append(
                {
                    "geography": geography,
                    "coverage_variant": coverage_variant,
                    "uninsured_count": denominator,
                    "eligible_uninsured_count": numerator,
                    "eligible_share_percent": share,
                    "age_universe": "age_under_65",
                    "engine_version": engine_version,
                    "data_bundle": data_bundle,
                    "bundle_id": bundle_id,
                    "sample": baseline_sample,
                    "rules_vintage": "PolicyEngine 2024 law",
                    "computed_at": computed_at,
                }
            )
            for metric, unit, value in (
                ("eligible_share_among_uninsured", "percent", share),
                ("eligible_uninsured_count", "persons", numerator),
            ):
                counterpart_rows.append(
                    {
                        "source": "pe",
                        "program": "medicaid",
                        "metric": metric,
                        "subgroup": "total",
                        "variant": variant,
                        "coverage_variant": coverage_variant,
                        "geography": geography,
                        "unit_concept": unit,
                        "period": "2024",
                        "value": value,
                        "numerator": numerator,
                        "denominator": denominator,
                        "age_universe": "age_under_65",
                        **common,
                    }
                )

    subgroup_masks = {
        "adults": adult,
        "children": child,
        "expansion_states": _and(
            under65,
            [state in expansion_states for state in baseline["state"]],
        ),
    }
    for coverage_variant, variant, uninsured in variants:
        for subgroup, subgroup_mask in subgroup_masks.items():
            mask = _and(subgroup_mask, uninsured, eligible)
            value = weighted_count(baseline, mask)
            counterpart_rows.append(
                {
                    "source": "pe",
                    "program": "medicaid",
                    "metric": "eligible_uninsured_count",
                    "subgroup": subgroup,
                    "variant": variant,
                    "coverage_variant": coverage_variant,
                    "geography": "US",
                    "unit_concept": "persons",
                    "period": "2024",
                    "value": value,
                    "numerator": value,
                    "denominator": None,
                    "age_universe": (
                        "age_19_to_64"
                        if subgroup == "adults"
                        else "age_under_19"
                        if subgroup == "children"
                        else "age_under_65_in_2024_expansion_states"
                    ),
                    "expansion_classification": (
                        "2024 expansion set; non-expansion AL FL GA KS MS SC TN TX WI WY"
                        if subgroup == "expansion_states"
                        else None
                    ),
                    **common,
                }
            )

    takeup_rows = []
    campaign_rows = []
    denominator_note = (
        "Reform Medicaid spending holds the baseline state-allocation denominator "
        "fixed, matching policyengine-us's baseline-branch reform semantics."
    )
    run_scope_note = (
        "This is a deterministic validation-sample result and is not publishable."
        if baseline_sample
        else "This is a full-file computation on the certified Build P artifact."
    )
    kff_bridge_note = (
        "The reform and bridge cover all ages and every PolicyEngine Medicaid "
        "eligibility pathway. KFF covers nonelderly people under MAGI Medicaid "
        "and CHIP, so KFF is narrower by age and Medicaid pathway but includes "
        "a child CHIP pathway absent from this PolicyEngine construction."
    )
    calibration_fill_note = (
        "Baseline anchor-and-fill Medicaid enrollees are not marginal under the "
        "reform even when they report no coverage at interview; KFF retains such "
        "reported-uninsured survey underreporters, so marginal_reported_uninsured "
        "is narrower than KFF's eligible-and-reported-uninsured construct."
    )
    rules_note = (
        "PolicyEngine applies 2024 law to 2024 Populace. KFF applies 2025 levels "
        "to the 2024 state indicator and 2023 levels to the 2022 flagship brief."
    )
    for geography in geographies:
        geo_mask = (
            [True] * people
            if geography == "US"
            else [state == geography for state in baseline["state"]]
        )
        base_eligible = weighted_count(baseline, _and(geo_mask, eligible))
        base_enrolled = weighted_count(baseline, _and(geo_mask, enrolled))
        reform_enrollment = weighted_count(baseline, _and(geo_mask, reform_enrolled))
        delta_enrollment = weighted_count(baseline, _and(geo_mask, marginal))
        baseline_spending = weighted_dollars(baseline, geo_mask)
        reform_spending = weighted_dollars(reform, geo_mask)
        delta_spending = reform_spending - baseline_spending
        bridge_reported = weighted_count(baseline, _and(geo_mask, marginal, reported))
        bridge_other = weighted_count(
            baseline, _and(geo_mask, marginal, _not(reported))
        )
        if not abs(delta_enrollment - bridge_reported - bridge_other) <= 1e-6 * max(
            delta_enrollment, 1
        ):
            raise AssertionError(f"bridge identity differs in {geography}")
        takeup_rows.append(
            {
                "geography": geography,
                "baseline_eligible": base_eligible,
                "baseline_enrolled": base_enrolled,
                "baseline_medicaid_usd": baseline_spending,
                "reform_enrolled": reform_enrollment,
                "reform_medicaid_usd": reform_spending,
                "delta_enrollment": delta_enrollment,
                "delta_medicaid_usd": delta_spending,
                "marginal_reported_uninsured": bridge_reported,
                "marginal_other_coverage": bridge_other,
                "enrollment_identity_gap": delta_enrollment
                - (base_eligible - base_enrolled),
                "bridge_identity_gap": delta_enrollment
                - bridge_reported
                - bridge_other,
                "engine_version": engine_version,
                "data_bundle": data_bundle,
                "bundle_id": bundle_id,
                "sample": baseline_sample,
                "computed_at": computed_at,
                "cost_construction": denominator_note,
            }
        )
        result_specs = (
            (
                "total",
                "enrollment",
                "persons",
                "point_in_time",
                reform_enrollment,
                base_enrolled,
                delta_enrollment,
            ),
            (
                "total_spending",
                "benefit_cost",
                "usd",
                "annual",
                reform_spending,
                baseline_spending,
                delta_spending,
            ),
            (
                "marginal_reported_uninsured",
                "enrollment",
                "persons",
                "point_in_time",
                bridge_reported,
                0.0,
                bridge_reported,
            ),
            (
                "marginal_other_coverage",
                "enrollment",
                "persons",
                "point_in_time",
                bridge_other,
                0.0,
                bridge_other,
            ),
        )
        for (
            component,
            metric,
            unit,
            time_basis,
            value,
            baseline_value,
            delta,
        ) in result_specs:
            annotations = [
                "Take-up is forced with the annual takes_up_medicaid_if_eligible input.",
                "Enrollment is point-in-time; Medicaid spending is annual.",
                denominator_note,
                run_scope_note,
                kff_bridge_note,
                calibration_fill_note,
                rules_note,
                (
                    "reported_uninsured means none of the nine reported coverage flags "
                    "and not modeled medicare_enrolled; other coverage is its complement"
                ),
            ]
            campaign_rows.append(
                {
                    "engine_version": engine_version,
                    "data_bundle": data_bundle,
                    "bundle_id": bundle_id,
                    "sample": baseline_sample,
                    "policyengine_bundle": reform_meta["policyengine_bundle"],
                    "pe_value": value,
                    "baseline_value": baseline_value,
                    "delta": delta,
                    "status": "constructed",
                    "benchmark_class": "different_model",
                    "calibration_relationship": "held_out",
                    "pe_construction": (
                        f"2024 {component}; one managed reform simulation; annual "
                        "Medicaid take-up input True; baseline allocation denominator retained"
                    ),
                    "computed_at": reform_meta["computed_at"],
                    "run_id": RUN_ID,
                    "annotations": annotations,
                    "reform_ref": REFORM_REF,
                    "exhibit_context": {
                        "geography": geography,
                        "program": "medicaid",
                        "component": component,
                    },
                    "exhibit_meta": {
                        "metric": metric,
                        "unit_concept": unit,
                        "period": YEAR,
                        "time_basis": time_basis,
                        "note": "Medicaid take-up increased to 100%",
                    },
                }
            )

    diagnostics_dir.mkdir(parents=True, exist_ok=True)
    for filename, rows in (
        ("kff_medicaid_moments_2024.csv", moment_diagnostics),
        ("kff_medicaid_takeup_2024.csv", takeup_rows),
    ):
        with (diagnostics_dir / filename).open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    counterpart_path.parent.mkdir(parents=True, exist_ok=True)
    counterpart_payload = {
        "provenance": {
            **common,
            "policyengine_bundle": baseline_meta["policyengine_bundle"],
            "baseline_computed_at": baseline_meta["computed_at"],
            "reform_computed_at": reform_meta["computed_at"],
            "expansion_classification": (
                "2024 expansion set; non-expansion AL FL GA KS MS SC TN TX WI WY"
            ),
            "adult_child_split": "children age under 19; adults age 19 to 64",
        },
        "rows": counterpart_rows,
    }
    counterpart_path.write_text(
        json.dumps(counterpart_payload, indent=1, allow_nan=False) + "\n"
    )
    campaign_path.parent.mkdir(parents=True, exist_ok=True)
    campaign_path.write_text(
        "".join(
            json.dumps(row, sort_keys=True, allow_nan=False) + "\n"
            for row in campaign_rows
        )
    )
    baseline_dollars = weighted_dollars(baseline)
    reform_dollars = weighted_dollars(reform)
    summary = {
        "sample": baseline_sample,
        "people": people,
        "engine_version": engine_version,
        "data_bundle": data_bundle,
        "bundle_id": bundle_id,
        "eligible": national_eligible,
        "enrolled": national_enrolled,
        "delta_enrollment": national_delta,
        "identity_gap": identity_gap,
        "baseline_medicaid_usd": baseline_dollars,
        "reform_medicaid_usd": reform_dollars,
        "delta_medicaid_usd": reform_dollars - baseline_dollars,
        "bridge_reported_uninsured": weighted_count(baseline, _and(marginal, reported)),
        "bridge_other_coverage": weighted_count(
            baseline, _and(marginal, _not(reported))
        ),
        "counterpart_rows": len(counterpart_rows),
        "campaign_rows": len(campaign_rows),
    }
    print(json.dumps(summary, indent=2, allow_nan=False))
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--reform", type=Path, required=True)
    parser.add_argument("--diagnostics-dir", type=Path, required=True)
    parser.add_argument("--counterparts", type=Path, required=True)
    parser.add_argument("--campaign", type=Path, required=True)
    parser.add_argument("--full", action="store_true")
    args = parser.parse_args()
    aggregate(
        args.baseline,
        args.reform,
        args.diagnostics_dir,
        args.counterparts,
        args.campaign,
        args.full,
    )


if __name__ == "__main__":
    main()
