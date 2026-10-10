"""Stage one descriptive counterpart (or a gap receipt) per event source row.

There is no database mutation. The registry is the row inventory, the compute
manifest commits its hash and each artifact's hash, and the output preserves
that inventory exactly. Positive values always mean gain to the Exchequer.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter
from pathlib import Path

from pipeline import compute_uk_event as compute
from pipeline import compute_uk_obr_costings as fiscal
from pipeline import stage_uk_ab2025 as ab_stage
from pipeline import uk_bundle as bundles

AXES = [
    "behavioural_adjustment",
    "baseline_vintage",
    "cy_proxies_fy",
    "head_scope",
    "population_vintage",
]

# Existing frozen registries predate an explicit annual_activation_fy field.
# These specific, documented constructions intentionally omit an earlier
# partial fiscal year. A late date alone must never excuse an inert lever:
# that would hide the original FY2023 Annual Allowance execution defect.
DOCUMENTED_ANNUAL_ACTIVATIONS = {
    "autumn_budget_2024__capital_gains_main_rates_and_reliefs": "2025-26",
    "autumn_budget_2024__sdlt_additional_dwelling_surcharge_2pp": "2025-26",
    "autumn_budget_2024__private_school_vat_20pct": "2025-26",
    "autumn_statement_2023__class_1_employee_nics_main_rate_cut_2p": "2024-25",
}


def _head_key(value: str) -> str:
    return " ".join(str(value).casefold().replace("_", " ").split())


def mapped_variables(source: dict, measure: dict) -> list[str]:
    """Match the literal OBR head to one registered head mapping."""
    explicit = source.get("pe_variables")
    if explicit:
        if len(explicit) != len(set(explicit)):
            raise ValueError("source head mapping repeats a variable")
        return list(explicit)
    candidates = [
        head
        for head in compute.head_definitions(measure)
        if _head_key(head["obr_head"]) == _head_key(source.get("tax_head", ""))
    ]
    if len(candidates) != 1:
        raise ValueError(
            f"source head {source.get('tax_head')!r} has {len(candidates)} registered mappings"
        )
    return candidates[0]["pe_variables"]


def validate_artifact(
    artifact: dict,
    measure: dict,
    year: int,
    registry_sha256: str,
    certified_digest: str,
) -> None:
    if (
        artifact.get("measure_key"),
        artifact.get("year"),
        artifact.get("registry_sha256"),
    ) != (measure["measure_key"], year, registry_sha256):
        raise ValueError("artifact identity differs from registry and manifest")
    if artifact.get("certified_dataset_sha256") != certified_digest:
        raise ValueError("artifact certified digest differs from compute manifest")
    channels = compute.variable_channels(measure)
    if artifact.get("head_channels") != channels or set(
        artifact["head_effects"]
    ) != set(channels):
        raise ValueError("artifact fiscal heads differ from registry")
    for variable, channel in channels.items():
        b = artifact["totals"]["baseline"]["heads"][variable]
        r = artifact["totals"]["reform"]["heads"][variable]
        effect = (r - b) * (1 if channel == "tax" else -1)
        if artifact["head_effects"][variable] != effect:
            raise ValueError(f"{variable}: staged effect differs from raw aggregates")
        literal = artifact["literal_reform_minus_baseline"][variable]
        expected = (
            -literal
            if artifact["construction"] == "reversal_on_certified_world"
            else literal
        )
        if effect != expected:
            raise ValueError(f"{variable}: literal reversal orientation differs")
    if artifact["measure_total_gbp"] != sum(artifact["head_effects"].values()):
        raise ValueError("per-measure head effects do not sum to the measure total")


def stage_event(
    registry: dict,
    manifest: dict | None,
    *,
    artifact_dir: Path,
    registry_sha256: str,
    bundle: str | None = None,
    bundle_root: Path = bundles.ROOT,
) -> tuple[list[dict], dict]:
    """Engine-free staging; missing measures and unsupported FYs stay visible."""
    selected = bundle or bundles.DEFAULT_BUNDLE
    verify_bundle = (
        bundle is not None or "bundle" in registry or "bundle_key" in registry
    )
    if verify_bundle:
        bundles.validate_registry_bundle(registry, selected, root=bundle_root)
    artifacts = {}
    paths = {}
    if manifest is not None:
        if verify_bundle:
            bundles.validate_runtime_bundle(manifest, selected, root=bundle_root)
        event = registry.get("event_slug", registry.get("event"))
        if event is not None and manifest.get("event", event) != event:
            raise ValueError("compute manifest event differs from registry")
        if manifest["registry_sha256"] != registry_sha256:
            raise ValueError("registry bytes changed after compute")
        for relative, digest in manifest["artifacts"].items():
            path = compute.ROOT / relative
            if not path.resolve().is_relative_to(artifact_dir.resolve()):
                raise ValueError(
                    "manifest artifact is outside this event's artifact directory"
                )
            payload = path.read_bytes()
            if fiscal.hashlib.sha256(payload).hexdigest() != digest:
                raise ValueError(
                    f"artifact bytes differ from compute manifest: {relative}"
                )
            artifact = json.loads(payload)
            key = (artifact["measure_key"], artifact["year"])
            if key in artifacts:
                raise ValueError(f"duplicate artifact identity: {key}")
            artifacts[key] = artifact
            paths[key] = (relative, digest)
    index = {measure["measure_key"]: measure for measure in registry["measures"]}
    for (key, year), artifact in artifacts.items():
        if verify_bundle:
            bundles.validate_runtime_bundle(artifact, selected, root=bundle_root)
            start, end = bundles.bundle_window(selected, root=bundle_root)
            if not start <= year <= end:
                raise ValueError("artifact year is outside selected bundle window")
        if key not in index:
            raise ValueError("manifest contains a measure outside the registry")
        event = registry.get("event_slug", registry.get("event"))
        if event is not None and artifact.get("event") != event:
            raise ValueError("artifact event differs from registry")
        validate_artifact(
            artifact,
            index[key],
            year,
            registry_sha256,
            manifest["certified_dataset_sha256"],
        )
    planned = compute.worlds.computable(index, years=registry["calendar_years"])
    full_pairs = {
        (key, year)
        for key, world in planned.items()
        if "alias_of" not in world
        for year in registry["calendar_years"]
    }
    computed_pairs = set(artifacts)
    if computed_pairs - full_pairs:
        raise ValueError(
            "committed artifact is outside the event's executable measure/year grid"
        )
    inert_pairs = set()
    for pair, artifact in artifacts.items():
        key, year = pair
        if not ab_stage.identical_worlds(artifact):
            continue
        commencement = index[key].get("commences_fy")
        if commencement and year < int(commencement[:4]):
            continue
        # Only a declared intentional annual activation can excuse an
        # identical in-force year. Inferring intent from a later start date
        # would hide a wrongly dated construction, such as the original AA.
        world = planned[key]
        first_years = [
            int(window[:4])
            for field in ("baseline_reform", "reform_reform")
            for windows in (compute.annual_reform(world[field]) or {}).values()
            for window in windows
        ]
        activation_fy = index[key].get("annual_activation_fy") or (
            DOCUMENTED_ANNUAL_ACTIVATIONS.get(key)
        )
        if activation_fy is not None:
            try:
                activation_year = int(activation_fy[:4])
            except (TypeError, ValueError) as exc:
                raise ValueError(f"{key}: invalid annual_activation_fy") from exc
            if (
                activation_fy != fiscal.fy_label(activation_year)
                or not first_years
                or activation_year != min(first_years)
            ):
                raise ValueError(
                    f"{key}: annual_activation_fy differs from the authored annual reform start"
                )
            if year < activation_year:
                continue
        inert_pairs.add(pair)
    if manifest is not None:

        def declared_pairs(field):
            rows = manifest[field]
            pairs = {(row["measure_key"], row["year"]) for row in rows}
            if len(pairs) != len(rows):
                raise ValueError(f"compute manifest repeats a pair in {field}")
            return pairs

        if "artifact_grid" in manifest:
            if declared_pairs("artifact_grid") != computed_pairs:
                raise ValueError(
                    "compute manifest grid differs from committed artifacts"
                )
            if declared_pairs("requested_grid") - computed_pairs:
                raise ValueError(
                    "compute manifest is missing requested measure/year artifacts"
                )
            if declared_pairs("full_event_grid") != full_pairs:
                raise ValueError(
                    "compute manifest full grid differs from the event registry"
                )
            if manifest["full_event_complete"] != (full_pairs <= computed_pairs):
                raise ValueError(
                    "compute manifest full-event completeness is inaccurate"
                )
        elif "measures" in manifest and "years" in manifest:
            requested = {
                (key, year)
                for key in manifest["measures"]
                for year in manifest["years"]
            }
            if requested != computed_pairs:
                raise ValueError(
                    "compute manifest is missing requested measure/year artifacts"
                )
    rows = []
    seen = set()
    mapped_heads = {}
    for measure in registry["measures"]:
        key = measure["measure_key"]
        for source in measure["source_rows"]:
            explicit = source.get("pe_variables") or []
            if len(explicit) != len(set(explicit)):
                raise ValueError("source head mapping repeats a variable")
            classification = source.get("classification", measure["computability"])
            identity = source["source_row_id"]
            if identity in seen:
                raise ValueError(f"source row classified more than once: {identity}")
            seen.add(identity)
            fy = source["fy"]
            year = int(fy[:4])
            axes = list(
                dict.fromkeys(
                    AXES
                    + measure.get("divergence_axes", [])
                    + source.get("divergence_axes", [])
                )
            )
            row = {
                "source_row_id": identity,
                "source_row_number": source.get("source_row_number"),
                "measure_key": key,
                "title": measure["title"],
                "event": registry.get("event", registry.get("event_slug")),
                "fy": fy,
                "year": year,
                "metric": source["metric"],
                "tax_head": source.get("tax_head"),
                "head_kind": source.get("head_kind"),
                "external_value_gbp": source["value_gbp"],
                "external_value_gbp_decimal": source.get(
                    "value_gbp_decimal", str(source["value_gbp"])
                ),
                "computability": classification,
                "construction": measure.get("construction"),
                "head_variables": [],
                "head_effects": {},
                "measure_total_gbp": None,
                "pe_value": None,
                "axes": axes,
                "status": "not_computed",
                "reason": None,
                "sign_convention": "positive_gain_to_exchequer",
                "partial_missing": measure.get("partial_missing")
                or measure.get("missing_legs")
                or measure.get("pe_gap"),
                "source_table": source.get("source_table"),
                "source_column": source.get("source_column"),
                "annotations": [
                    "OBR uses the forecast available at announcement; PE uses a single certified 2023 population with later calibration and uprating targets.",
                    "PE calendar-year totals proxy fiscal-year totals; PE is static and its certified policy world differs from the announcement baseline.",
                ],
            }
            if selected != bundles.DEFAULT_BUNDLE:
                row["annotations"][0] = (
                    f"OBR uses the forecast available at announcement; PE uses a single certified {bundles.bundle_window(selected, root=bundle_root)[0]} population with later calibration and uprating targets."
                )
            artifact_key = (key, year)
            artifact = artifacts.get(artifact_key)
            if (
                selected != bundles.DEFAULT_BUNDLE
                and not bundles.bundle_window(selected, root=bundle_root)[0]
                <= year
                <= bundles.bundle_window(selected, root=bundle_root)[1]
            ):
                row["status"] = "outside_bundle_window"
                row["reason"] = (
                    "FY start outside the selected certified bundle's supported calendar-year window"
                )
            elif classification == "out_of_household_scope":
                row["reason"] = (
                    source.get("scope_reason")
                    or source.get("classification_reason")
                    or source.get("pe_gap")
                    or measure.get("scope_reason")
                    or measure.get("pe_gap")
                    or classification
                )
            elif classification == "not_expressible":
                row["reason"] = (
                    source.get("pe_gap")
                    or source.get("scope_reason")
                    or measure.get("pe_gap")
                    or measure.get("scope_reason")
                    or classification
                )
            elif year not in registry["calendar_years"]:
                row["reason"] = (
                    "FY start outside this event's documented certified-bundle support"
                )
            elif artifact is None:
                row["reason"] = (
                    "no numerical artifact for this measure and calendar year"
                )
            else:
                try:
                    variables = mapped_variables(source, measure)
                except ValueError as exc:
                    row["reason"] = str(exc)
                else:
                    if any(
                        variable not in artifact["head_effects"]
                        for variable in variables
                    ):
                        raise ValueError(
                            "source mapping names a variable absent from the artifact"
                        )
                    if ab_stage.identical_worlds(artifact):
                        note, gap = ab_stage.identical_year_verdict(
                            fy, measure.get("commences_fy")
                        )
                        if gap:
                            row["reason"] = gap
                            if artifact_key in inert_pairs:
                                row["status"] = "inert_construction"
                                row["reason"] = (
                                    f"inert construction: reform and baseline worlds identical in FY {fy} "
                                    "while the measure is in force; numerical replay is blocked"
                                )
                        elif note:
                            row["annotations"].append(note)
                    if row["reason"] is None:
                        for variable in variables:
                            mapping = (key, year, variable)
                            if mapping in mapped_heads:
                                raise ValueError(
                                    f"{key} {year}: {variable} mapped to multiple source rows "
                                    f"({mapped_heads[mapping]}, {identity}); an explicit component allocation is required"
                                )
                            mapped_heads[mapping] = identity
                        row["head_variables"] = variables
                        row["head_effects"] = {
                            v: artifact["head_effects"][v] for v in variables
                        }
                        row["measure_total_gbp"] = artifact["measure_total_gbp"]
                        row["pe_value"] = sum(row["head_effects"].values())
                        if not math.isfinite(row["pe_value"]):
                            raise ValueError("staged counterpart is not finite")
                        row["literal_reform_minus_baseline"] = {
                            v: artifact["literal_reform_minus_baseline"][v]
                            for v in variables
                        }
                        row["status"] = "constructed"
                        row["artifact_path"], row["artifact_sha256"] = paths[
                            artifact_key
                        ]
                        row["engine_version"] = artifact["engine_version"]
                        row["data_bundle"] = artifact["data_bundle"]
            rows.append(row)
    rows.sort(key=lambda row: str(row["source_row_id"]))
    counts = Counter(row["status"] for row in rows)
    source_total = compute.registry_builder._sum(
        {"value_gbp_decimal": source.get("value_gbp_decimal", str(source["value_gbp"]))}
        for measure in registry["measures"]
        for source in measure["source_rows"]
    )
    staged_total = compute.registry_builder._sum(
        {"value_gbp_decimal": row["external_value_gbp_decimal"]} for row in rows
    )
    tally = {
        "source_rows": len(seen),
        "staged_rows": len(rows),
        "by_status": dict(sorted(counts.items())),
        "source_value_gbp": sum(row["external_value_gbp"] for row in rows),
        "source_value_gbp_decimal": source_total,
        "staged_value_gbp_decimal": staged_total,
        "computed_measure_years": len(computed_pairs),
        "full_event_grid_size": len(full_pairs),
        "full_event_complete": full_pairs <= computed_pairs and not inert_pairs,
        "missing_measure_years": compute.grid_rows(full_pairs - computed_pairs),
        "registry_sha256": registry_sha256,
    }
    if selected != bundles.DEFAULT_BUNDLE:
        tally.update(bundles.bundle_identity(selected, root=bundle_root))
    if inert_pairs:
        tally["inert_measure_years"] = compute.grid_rows(inert_pairs)
    if tally["source_rows"] != tally["staged_rows"]:
        raise ValueError(
            "staging inventory does not preserve the source-row accounting identity"
        )
    if source_total != staged_total:
        raise ValueError("staging does not preserve the exact source GBP total")
    return rows, tally


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--event", required=True)
    ap.add_argument("--bundle", default=bundles.DEFAULT_BUNDLE)
    ap.add_argument("--registry", type=Path)
    ap.add_argument("--artifact-dir", type=Path)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args(argv)
    default_registry = bundles.registry_path(args.event, args.bundle)
    default_artifacts = bundles.event_output_dir(args.event, args.bundle)
    registry_path = args.registry or default_registry
    artifact_dir = args.artifact_dir or default_artifacts
    bundles.validate_bundle_path(registry_path, args.bundle, kind="registry")
    bundles.validate_bundle_path(artifact_dir, args.bundle, kind="results")
    payload = registry_path.read_bytes()
    registry_sha256 = fiscal.hashlib.sha256(payload).hexdigest()
    manifest_path = artifact_dir / "RUN_MANIFEST.json"
    manifest = (
        json.loads(manifest_path.read_bytes()) if manifest_path.exists() else None
    )
    registry = json.loads(payload)
    compute.validate_event_identity(registry, args.event, args.bundle)
    compute.registry_builder.validate_registry(registry)
    rows, tally = stage_event(
        registry,
        manifest,
        artifact_dir=artifact_dir,
        registry_sha256=registry_sha256,
        bundle=args.bundle,
    )
    compute.verify_registry_identity(registry_path, registry_sha256)
    output = args.output or artifact_dir / "STAGED.jsonl"
    bundles.validate_bundle_path(output, args.bundle, kind="results")
    output.parent.mkdir(parents=True, exist_ok=True)
    staged_payload = b"".join(
        (json.dumps(row, sort_keys=True, allow_nan=False) + "\n").encode()
        for row in rows
    )
    fiscal.atomic_write_bytes(output, staged_payload)
    fiscal.atomic_write_bytes(
        artifact_dir / "STAGING_MANIFEST.json",
        compute.canonical_bytes(
            {
                **tally,
                "event": args.event,
                "staged_path": fiscal.relative_to_root(output),
                "staged_sha256": fiscal.hashlib.sha256(staged_payload).hexdigest(),
            }
        ),
    )
    print(json.dumps(tally, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
