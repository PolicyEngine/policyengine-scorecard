"""Aggregate Medicaid baseline/reform extracts into scorecard staging files."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

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


def load_meta(path: Path) -> dict:
    return json.loads(Path(f"{path}.meta.json").read_text())


def weighted_count(frame: pd.DataFrame, mask: np.ndarray) -> float:
    return float(frame.loc[mask, "person_weight"].sum())


def weighted_dollars(frame: pd.DataFrame, mask: np.ndarray | None = None) -> float:
    if mask is None:
        mask = np.ones(len(frame), dtype=bool)
    selected = frame.loc[mask]
    return float((selected["person_weight"] * selected["medicaid"]).sum())


def aggregate(
    baseline_path: Path,
    reform_path: Path,
    diagnostics_dir: Path,
    counterpart_path: Path,
    campaign_path: Path,
    full: bool,
) -> dict:
    baseline = pd.read_csv(baseline_path)
    reform = pd.read_csv(reform_path)
    baseline_meta = load_meta(baseline_path)
    reform_meta = load_meta(reform_path)
    if len(baseline) != len(reform):
        raise ValueError("baseline and reform row counts differ")
    if not np.array_equal(baseline["person_id"], reform["person_id"]):
        raise ValueError("baseline and reform people differ")
    if not np.array_equal(baseline["state"], reform["state"]):
        raise ValueError("baseline and reform states differ")
    if not np.allclose(baseline["person_weight"], reform["person_weight"]):
        raise ValueError("baseline and reform weights differ")
    if not np.array_equal(
        baseline["is_medicaid_eligible"], reform["is_medicaid_eligible"]
    ):
        raise ValueError("eligibility changed under the take-up input")
    if not np.array_equal(baseline["reported_uninsured"], reform["reported_uninsured"]):
        raise ValueError("reported coverage changed under the take-up input")
    if not np.allclose(baseline[DENOMINATOR], reform[DENOMINATOR], equal_nan=True):
        raise ValueError("reform did not retain the baseline Medicaid denominator")
    eligible = baseline["is_medicaid_eligible"].to_numpy(dtype=bool)
    enrolled = baseline["medicaid_enrolled"].to_numpy(dtype=bool)
    reform_enrolled = reform["medicaid_enrolled"].to_numpy(dtype=bool)
    if not np.array_equal(reform_enrolled, eligible):
        raise AssertionError("reform enrollment is not identical to eligibility")
    if np.any(enrolled & ~reform_enrolled):
        raise AssertionError("the reform removes baseline enrollees")
    marginal = reform_enrolled & ~enrolled
    reported = baseline["reported_uninsured"].to_numpy(dtype=bool)
    modeled = baseline["modeled_uninsured"].to_numpy(dtype=bool)
    under65 = baseline["age"].to_numpy() < 65
    child = baseline["age"].to_numpy() < 19
    adult = under65 & ~child
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

    national_eligible = weighted_count(baseline, eligible)
    national_enrolled = weighted_count(baseline, enrolled)
    national_delta = weighted_count(baseline, marginal)
    identity_gap = national_delta - (national_eligible - national_enrolled)
    if abs(identity_gap) > 1e-6 * max(national_delta, 1):
        raise AssertionError(f"enrollment identity gap {identity_gap}")
    if full:
        anchors = {
            "eligible": (national_eligible, 77_300_000),
            "enrolled": (national_enrolled, 72_300_000),
        }
        for name, (actual, expected) in anchors.items():
            relative_error = abs(actual / expected - 1)
            if relative_error > 0.02:
                raise SystemExit(
                    f"STOP: {name} anchor {actual:,.0f} differs from "
                    f"{expected:,.0f} by {relative_error:.2%}"
                )

    common = {
        "engine_version": engine_version,
        "data_bundle": data_bundle,
        "bundle_id": bundle_id,
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
            np.ones(len(baseline), dtype=bool)
            if geography == "US"
            else baseline["state"].to_numpy() == geography
        )
        for coverage_variant, variant, uninsured in variants:
            universe = geo_mask & under65 & uninsured
            numerator_mask = universe & eligible
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
        "expansion_states": under65
        & baseline["state"].isin(expansion_states).to_numpy(),
    }
    for coverage_variant, variant, uninsured in variants:
        for subgroup, subgroup_mask in subgroup_masks.items():
            mask = subgroup_mask & uninsured & eligible
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
    for geography in geographies:
        geo_mask = (
            np.ones(len(baseline), dtype=bool)
            if geography == "US"
            else baseline["state"].to_numpy() == geography
        )
        base_eligible = weighted_count(baseline, geo_mask & eligible)
        base_enrolled = weighted_count(baseline, geo_mask & enrolled)
        reform_enrollment = weighted_count(baseline, geo_mask & reform_enrolled)
        delta_enrollment = weighted_count(baseline, geo_mask & marginal)
        baseline_spending = weighted_dollars(baseline, geo_mask)
        reform_spending = weighted_dollars(reform, geo_mask)
        delta_spending = reform_spending - baseline_spending
        bridge_reported = weighted_count(baseline, geo_mask & marginal & reported)
        bridge_other = weighted_count(baseline, geo_mask & marginal & ~reported)
        if abs(delta_enrollment - bridge_reported - bridge_other) > 1e-6 * max(
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
    pd.DataFrame(moment_diagnostics).to_csv(
        diagnostics_dir / "kff_medicaid_moments_2024.csv", index=False
    )
    pd.DataFrame(takeup_rows).to_csv(
        diagnostics_dir / "kff_medicaid_takeup_2024.csv", index=False
    )
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
    counterpart_path.write_text(json.dumps(counterpart_payload, indent=1) + "\n")
    campaign_path.parent.mkdir(parents=True, exist_ok=True)
    campaign_path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in campaign_rows)
    )
    summary = {
        "sample": not full,
        "people": len(baseline),
        "engine_version": engine_version,
        "data_bundle": data_bundle,
        "bundle_id": bundle_id,
        "eligible": national_eligible,
        "enrolled": national_enrolled,
        "delta_enrollment": national_delta,
        "identity_gap": identity_gap,
        "baseline_medicaid_usd": weighted_dollars(baseline),
        "reform_medicaid_usd": weighted_dollars(reform),
        "delta_medicaid_usd": weighted_dollars(reform) - weighted_dollars(baseline),
        "bridge_reported_uninsured": weighted_count(baseline, marginal & reported),
        "bridge_other_coverage": weighted_count(baseline, marginal & ~reported),
        "counterpart_rows": len(counterpart_rows),
        "campaign_rows": len(campaign_rows),
    }
    print(json.dumps(summary, indent=2))
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
