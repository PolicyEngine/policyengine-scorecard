"""Compare two certified replay bundles, retaining every OBR source row.

This is an engine-free descriptive comparison. Attribution is read exclusively
from the checked-in attribution file; engine versions and changed values never
supply a driver automatically. Numerical sizing requires a hash-bound computed
artifact. No event simulation is performed here.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
from collections import Counter
from decimal import Decimal
from pathlib import Path

from pipeline import compare_uk_event as event_comparison
from pipeline import uk_bundle as bundles
from pipeline.compare_uk_obr_costings import atomic_write_bytes, ratio_and_bin

ROOT = event_comparison.ROOT
DRIVERS = frozenset(
    {
        "hicbc_opt_out",
        "annual_allowance_pe_uk_2237",
        "sdlt_pe_uk_2238",
        "uc_uplifts_pe_uk_2239",
        "nics_freeze",
        "data_release",
        "construction_change",
        "window_change",
        "other_engine_change",
        "unattributed",
    }
)
# Executed schedules and mappings, not prose or engine metadata. Package
# components are recursively included, so changing a component changes its
# parent's construction digest too.
CONSTRUCTION_FIELDS = (
    "construction",
    "pe_baseline_modifier",
    "pe_reform_delta",
    "package_of",
    "heads",
    "head_variables",
    "commences_fy",
    "annual_activation_fy",
    "effect_ends_fy",
)
CSV_FIELDS = (
    "event",
    "source_row_id",
    "measure_key",
    "title",
    "fy",
    "tax_head",
    "obr_million_gbp",
    "pe_base_million_gbp",
    "pe_new_million_gbp",
    "change_million_gbp",
    "base_ratio_bin",
    "new_ratio_bin",
    "status",
    "base_status",
    "new_status",
    "base_construction_sha256",
    "new_construction_sha256",
    "base_classification",
    "new_classification",
    "head_certified_aggregate_new_to_base_ratio",
    "measure_new_to_base_ratio",
    "head_effect_new_to_base_ratio",
    "attribution",
    "explained_share",
    "explained_share_withheld",
)


class EngineComparisonError(ValueError):
    """Two replay receipts or their attribution cannot support a comparison."""


def canonical_bytes(value) -> bytes:
    return (
        json.dumps(value, sort_keys=True, indent=1, allow_nan=False) + "\n"
    ).encode()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def construction_digest(
    measure: dict, index: dict[str, dict] | None = None, trail: tuple[str, ...] = ()
) -> str:
    """Hash the authored construction and source-head mappings canonically."""
    key = measure["measure_key"]
    if key in trail:
        raise EngineComparisonError("cyclic package construction")
    payload = {
        field: measure[field] for field in CONSTRUCTION_FIELDS if field in measure
    }
    payload["source_head_mappings"] = sorted(
        [
            {field: source.get(field) for field in ("source_row_id", "pe_variables")}
            for source in measure["source_rows"]
        ],
        key=lambda row: row["source_row_id"],
    )
    if index is not None:
        components = measure.get("package_of", [])
        construction = str(measure.get("construction", ""))
        if construction.startswith("same_lever_as_"):
            components = [construction.removeprefix("same_lever_as_")]
        payload["component_constructions"] = {
            component: construction_digest(index[component], index, (*trail, key))
            for component in sorted(components)
        }
    return hashlib.sha256(canonical_bytes(payload)).hexdigest()


def _inventory(registry: dict) -> dict[str, tuple[dict, dict]]:
    out = {}
    measure_keys = set()
    for measure in registry["measures"]:
        if measure["measure_key"] in measure_keys:
            raise EngineComparisonError("duplicate registry measure key")
        measure_keys.add(measure["measure_key"])
        for source in measure["source_rows"]:
            identity = source["source_row_id"]
            if identity in out:
                raise EngineComparisonError("duplicate registry source row")
            out[identity] = (measure, source)
    return out


def _comparison_index(rows: list[dict]) -> dict[str, dict]:
    out = {row["source_row_id"]: row for row in rows}
    if len(out) != len(rows):
        raise EngineComparisonError("duplicate comparison source row")
    return out


def _ratio(new, base):
    return None if new is None or base is None or base == 0 else new / base


def _aggregate(row: dict, artifacts: dict[str, dict], field: str):
    if row.get("pe_value_gbp") is None:
        return None
    artifact = artifacts[row["artifact"]]
    if field == "measure_total_gbp":
        return artifact[field]
    values = artifact.get(field)
    if not isinstance(values, dict):
        raise EngineComparisonError(f"computed artifact missing {field}")
    try:
        return sum(values[variable] for variable in row["head_variables"])
    except KeyError as exc:
        raise EngineComparisonError(
            f"computed artifact missing certified head: {exc}"
        ) from exc


def _entry_index(attribution: dict) -> dict[tuple[str, str, str | None], list[dict]]:
    if attribution.get("schema_version") != 1:
        raise EngineComparisonError("unsupported attribution schema_version")
    entries = attribution.get("entries")
    if not isinstance(entries, list):
        raise EngineComparisonError(
            "attribution requires entries, including explicit unattributed entries"
        )
    out = {}
    for entry in entries:
        key = (entry.get("event"), entry.get("measure_key"), entry.get("fy"))
        if not all(isinstance(v, str) and v for v in key[:2]) or key in out:
            raise EngineComparisonError(
                "attribution has invalid or duplicate event/measure/FY entry"
            )
        if key[2] is not None and not isinstance(key[2], str):
            raise EngineComparisonError("attribution FY must be a string")
        drivers = entry.get("drivers")
        if not isinstance(drivers, list) or not drivers:
            raise EngineComparisonError("attribution entry requires named drivers")
        names = [driver.get("driver") for driver in drivers]
        if len(names) != len(set(names)) or set(names) - DRIVERS:
            raise EngineComparisonError(
                "attribution uses duplicate or unknown driver vocabulary"
            )
        if "unattributed" in names and len(names) != 1:
            raise EngineComparisonError(
                "explicit unattributed cannot be combined with attributed drivers"
            )
        out[key] = drivers
    return out


def _verified_bundle(reference: str, verified: dict[str, str]) -> str:
    """Sized evidence must be an executed artifact from a verified run manifest."""
    if reference not in verified:
        raise EngineComparisonError(
            "sized evidence must be an artifact listed in a verified run manifest"
        )
    return verified[reference]


def validate_attribution(
    attribution: dict,
    *,
    artifact_root: Path = ROOT,
    input_hashes: dict[str, str] | None = None,
    verified_artifacts: dict[str, str] | None = None,
) -> dict:
    """Validate all entries, even entries not used by a changed row.

    ``verified_artifacts`` maps each artifact path (relative to the root) from
    a verified run manifest to its bundle. Without it, no driver can be sized.
    """
    verified = verified_artifacts or {}
    out = _entry_index(attribution)
    for (event, measure_key, fy), drivers in out.items():
        sized_terms = set()
        # Each head is sized by at most one driver per entry, whatever kind of
        # proof it cites. A computed artifact and a paired run that ends at it
        # (or a total and one of its heads) would otherwise count one
        # contribution twice.
        sized_heads: set[str] = set()
        for driver in drivers:
            evidence = driver.get("evidence")
            if not isinstance(evidence, list) or not evidence:
                raise EngineComparisonError("every driver requires evidence")
            for item in evidence:
                if (
                    not isinstance(item, dict)
                    or item.get("kind")
                    not in (
                        "pr",
                        "issue",
                        "changelog",
                        "diagnostic",
                        "paired_run",
                        "unattributed",
                    )
                    or not isinstance(item.get("reference"), str)
                    or not item["reference"].strip()
                ):
                    raise EngineComparisonError(
                        "driver evidence must name a PR, issue, changelog, diagnostic or paired-run artifact"
                    )
                if (
                    item["kind"] == "unattributed"
                    and driver["driver"] != "unattributed"
                ):
                    raise EngineComparisonError(
                        "unattributed evidence cannot support a named mechanism"
                    )
            if type(driver.get("sized")) is not bool:
                raise EngineComparisonError("driver requires boolean sized")
            if not driver["sized"]:
                if "value_gbp" in driver or "artifact" in driver:
                    raise EngineComparisonError(
                        "unsized driver cannot carry a numerical size"
                    )
                continue
            if driver["driver"] == "unattributed":
                raise EngineComparisonError("unattributed driver cannot be sized")
            if fy is None:
                raise EngineComparisonError(
                    "a sized attribution requires an explicit source FY"
                )
            proof = driver.get("artifact")
            if not isinstance(proof, dict):
                raise EngineComparisonError("sized driver requires a computed artifact")
            reference = proof.get("path")
            if not isinstance(reference, str) or Path(reference).is_absolute():
                raise EngineComparisonError("sized artifact path must be relative")
            path = (artifact_root / reference).resolve()
            if not path.is_relative_to(artifact_root.resolve()):
                raise EngineComparisonError("sized artifact escapes root")
            if not path.is_file():
                raise EngineComparisonError("sized computed artifact does not exist")
            if sha256(path) != proof.get("sha256"):
                raise EngineComparisonError("sized artifact SHA-256 differs")
            computed = json.loads(path.read_bytes())
            if "head_effects" in computed:
                bundles.validate_runtime_bundle(
                    computed,
                    _verified_bundle(reference, verified),
                    root=artifact_root,
                )
                event_comparison.validate_artifact(computed, reference)
                if (
                    computed.get("event"),
                    computed.get("measure_key"),
                    computed.get("year"),
                ) != (event, measure_key, int(fy[:4])):
                    raise EngineComparisonError(
                        "sized artifact event/measure/FY differs from attribution"
                    )
                allowed = proof.get("value_path", [])
                if not (
                    allowed == ["measure_total_gbp"]
                    or len(allowed) == 2
                    and allowed[0] == "head_effects"
                ):
                    raise EngineComparisonError(
                        "sized artifact value must be a computed GBP effect"
                    )
                term = ("computed", proof["sha256"], tuple(allowed))
                heads = (
                    {allowed[1]}
                    if allowed[0] == "head_effects"
                    else set(computed["head_effects"])
                )
            elif (
                computed.get("artifact_type") == "paired_run"
                and computed.get("status") == "computed"
            ):
                allowed = proof.get("value_path", [])
                if allowed != ["effect_gbp"]:
                    raise EngineComparisonError(
                        "paired-run size must reference computed effect_gbp"
                    )
                endpoints = {}
                paired_heads = set()
                for side in ("base", "new"):
                    receipt = computed.get(side + "_artifact")
                    if not isinstance(receipt, dict):
                        raise EngineComparisonError(
                            "paired-run sizing artifact lacks executed-world commitments"
                        )
                    endpoint_reference = receipt.get("path")
                    if (
                        not isinstance(endpoint_reference, str)
                        or Path(endpoint_reference).is_absolute()
                    ):
                        raise EngineComparisonError(
                            "paired-run endpoint path must be relative"
                        )
                    endpoint_path = (artifact_root / endpoint_reference).resolve()
                    if not endpoint_path.is_relative_to(artifact_root.resolve()):
                        raise EngineComparisonError("paired-run endpoint escapes root")
                    if not endpoint_path.is_file():
                        raise EngineComparisonError(
                            "paired-run computed endpoint does not exist"
                        )
                    if sha256(endpoint_path) != receipt.get("sha256"):
                        raise EngineComparisonError(
                            "paired-run endpoint SHA-256 differs"
                        )
                    endpoint = json.loads(endpoint_path.read_bytes())
                    event_comparison.validate_artifact(endpoint, endpoint_reference)
                    if (
                        endpoint.get("event"),
                        endpoint.get("measure_key"),
                        endpoint.get("year"),
                    ) != (event, measure_key, int(fy[:4])):
                        raise EngineComparisonError(
                            "paired-run endpoint event/measure/FY differs from attribution"
                        )
                    endpoint_bundle = computed.get(side + "_bundle")
                    if not isinstance(endpoint_bundle, str):
                        raise EngineComparisonError(
                            "paired-run endpoint requires bundle identity"
                        )
                    if (
                        _verified_bundle(
                            str(endpoint_path.relative_to(artifact_root.resolve())),
                            verified,
                        )
                        != endpoint_bundle
                    ):
                        raise EngineComparisonError(
                            "paired-run endpoint belongs to another verified bundle"
                        )
                    bundles.validate_runtime_bundle(
                        endpoint, endpoint_bundle, root=artifact_root
                    )
                    variables = computed.get("head_variables")
                    if variables is None:
                        paired_heads.update(endpoint["head_effects"])
                        endpoints[side] = endpoint["measure_total_gbp"]
                    elif (
                        isinstance(variables, list)
                        and variables
                        and len(variables) == len(set(variables))
                    ):
                        paired_heads.update(variables)
                        try:
                            endpoints[side] = sum(
                                endpoint["head_effects"][variable]
                                for variable in variables
                            )
                        except KeyError as exc:
                            raise EngineComparisonError(
                                "paired-run endpoint lacks sized heads"
                            ) from exc
                    else:
                        raise EngineComparisonError(
                            "paired-run head variables must be unique and nonempty"
                        )
                    if input_hashes is not None:
                        input_hashes[endpoint_reference] = receipt["sha256"]
                if computed.get("effect_gbp") != endpoints["new"] - endpoints["base"]:
                    raise EngineComparisonError(
                        "paired-run size differs from computed endpoint change"
                    )
                term = (
                    "paired_run",
                    computed["base_artifact"]["sha256"],
                    computed["new_artifact"]["sha256"],
                    tuple(sorted(paired_heads)),
                )
                heads = set(paired_heads)
            else:
                raise EngineComparisonError(
                    "sized evidence is not a computed national artifact"
                )
            value = computed
            try:
                for part in allowed:
                    value = value[part]
            except (KeyError, TypeError) as exc:
                raise EngineComparisonError(
                    "sized artifact value path does not exist"
                ) from exc
            quoted = driver.get("value_gbp")
            if (
                isinstance(quoted, bool)
                or not isinstance(quoted, (int, float))
                or not math.isfinite(quoted)
                or quoted != value
            ):
                raise EngineComparisonError(
                    "sized driver value differs from computed artifact"
                )
            if term in sized_terms:
                raise EngineComparisonError(
                    "sized drivers repeat the same computed term"
                )
            sized_terms.add(term)
            if sized_heads & heads:
                raise EngineComparisonError(
                    "sized drivers overlap on the same measured heads"
                )
            sized_heads |= heads
            if input_hashes is not None:
                input_hashes[reference] = proof["sha256"]
    return out


def _sized_head_scope(driver: dict, artifact_root: Path) -> set[str]:
    """Read measured head scope, never allocate a package size across heads."""
    proof = driver["artifact"]
    value_path = proof["value_path"]
    if value_path[:1] == ["head_effects"]:
        return {value_path[1]}
    artifact = json.loads((artifact_root / proof["path"]).read_bytes())
    if value_path == ["measure_total_gbp"]:
        return set(artifact["head_effects"])
    if artifact.get("head_variables") is not None:
        return set(artifact["head_variables"])
    return {
        variable
        for side in ("base", "new")
        for variable in json.loads(
            (artifact_root / artifact[side + "_artifact"]["path"]).read_bytes()
        )["head_effects"]
    }


def build_engine_rows(
    base_registry: dict,
    new_registry: dict,
    base_rows: list[dict],
    new_rows: list[dict],
    attribution: dict,
    *,
    base_artifacts: dict[str, dict],
    new_artifacts: dict[str, dict],
    artifact_root: Path = ROOT,
    input_hashes: dict | None = None,
    verified_artifacts: dict[str, str] | None = None,
) -> list[dict]:
    """Join the exact source universe; neither gaps nor zero rows are dropped."""
    left, right = _inventory(base_registry), _inventory(new_registry)
    base, new = _comparison_index(base_rows), _comparison_index(new_rows)
    if set(left) != set(right) or set(base) != set(left) or set(new) != set(left):
        raise EngineComparisonError(
            "source-row multiset differs across bundle registries/comparisons"
        )
    event = base_registry["event_slug"]
    if new_registry["event_slug"] != event or base_registry.get(
        "source"
    ) != new_registry.get("source"):
        raise EngineComparisonError(
            "OBR source snapshot or event differs between bundles"
        )
    base_measures = {m["measure_key"]: m for m in base_registry["measures"]}
    new_measures = {m["measure_key"]: m for m in new_registry["measures"]}
    drivers = validate_attribution(
        attribution,
        artifact_root=artifact_root,
        input_hashes=input_hashes,
        verified_artifacts=verified_artifacts,
    )
    rows = []
    for identity in sorted(left):
        old_measure, old_source = left[identity]
        new_measure, new_source = right[identity]
        for field in (
            "fy",
            "tax_head",
            "metric",
            "source_table",
            "source_column",
            "value_gbp_decimal",
            "value_gbp",
        ):
            if old_source.get(field) != new_source.get(field):
                raise EngineComparisonError(
                    f"{identity}: OBR source {field} differs between bundles"
                )
        if old_measure["measure_key"] != new_measure["measure_key"]:
            raise EngineComparisonError("source row moved to another measure")
        before, after = base[identity], new[identity]
        old, latest = before["pe_value_gbp"], after["pe_value_gbp"]
        old_digest = construction_digest(old_measure, base_measures)
        new_digest = construction_digest(new_measure, new_measures)
        status = (
            "construction_changed"
            if old_digest != new_digest
            else "computed_in_both"
            if old is not None and latest is not None
            else "base_only"
            if old is not None
            else "new_only"
            if latest is not None
            else "uncomputed_in_both"
        )
        change = None if old is None or latest is None else latest - old
        changed = (
            old != latest
            or old_digest != new_digest
            or before.get("status") != after.get("status")
            or before.get("classification") != after.get("classification")
        )
        key = (event, old_measure["measure_key"], old_source["fy"])
        assigned = drivers.get(key, drivers.get((*key[:2], None), []))
        if changed and not assigned:
            raise EngineComparisonError(
                f"changed row requires explicit attribution or unattributed: {key}"
            )
        unsized = any(not driver["sized"] for driver in assigned)
        row_variables = set(before.get("head_variables", [])) & set(
            after.get("head_variables", [])
        )
        unmatched_sizing = any(
            driver["sized"]
            and not _sized_head_scope(driver, artifact_root) <= row_variables
            for driver in assigned
        )
        share = None
        reason = (
            "unsized drivers"
            if unsized
            else "measure sizing does not isolate this source head"
            if unmatched_sizing
            else "no computed change"
            if change is None
            else "zero computed change"
            if not change
            else "no sized drivers"
            if not assigned
            else ""
        )
        if not reason:
            values = [driver["value_gbp"] for driver in assigned]
            if any(value * change < 0 for value in values):
                reason = "a sized driver masks the observed change"
            elif not 0 <= sum(values) / change <= 1:
                reason = "computed share outside [0, 1]"
            else:
                share = sum(values) / change
        obr = old_source["value_gbp"]
        rows.append(
            {
                "event": event,
                "source_row_id": identity,
                "measure_key": old_measure["measure_key"],
                "title": old_measure["title"],
                "fy": old_source["fy"],
                "tax_head": old_source.get("tax_head"),
                "obr_million_gbp": obr / 1e6,
                "pe_base_million_gbp": None if old is None else old / 1e6,
                "pe_new_million_gbp": None if latest is None else latest / 1e6,
                "change_million_gbp": None if change is None else change / 1e6,
                "base_ratio_bin": ratio_and_bin(obr, old)[1],
                "new_ratio_bin": ratio_and_bin(obr, latest)[1],
                "status": status,
                "base_status": before.get("status"),
                "new_status": after.get("status"),
                "base_construction_sha256": old_digest,
                "new_construction_sha256": new_digest,
                "base_classification": before.get("classification"),
                "new_classification": after.get("classification"),
                "head_certified_aggregate_new_to_base_ratio": _ratio(
                    _aggregate(after, new_artifacts, "certified_aggregates_gbp"),
                    _aggregate(before, base_artifacts, "certified_aggregates_gbp"),
                ),
                "measure_new_to_base_ratio": _ratio(
                    _aggregate(after, new_artifacts, "measure_total_gbp"),
                    _aggregate(before, base_artifacts, "measure_total_gbp"),
                ),
                "head_effect_new_to_base_ratio": _ratio(latest, old),
                "attribution": assigned,
                "explained_share": share,
                "explained_share_withheld": reason,
            }
        )

    # Source £ accounting is exact; constructions and classes can change while
    # this same row inventory and its net/absolute amount remain fixed.
    def account(inventory):
        amounts = [
            Decimal(str(source.get("value_gbp_decimal", source["value_gbp"])))
            for _, source in inventory.values()
        ]
        return sum(amounts), sum(map(abs, amounts))

    if account(left) != account(right):
        raise EngineComparisonError("net or absolute OBR GBP differs across bundles")
    return sorted(
        rows,
        key=lambda row: (
            row["event"],
            row["measure_key"],
            row["fy"],
            str(row["tax_head"]),
            row["source_row_id"],
        ),
    )


def render_csv(rows: list[dict]) -> str:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=CSV_FIELDS, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow(
            {
                key: json.dumps(row[key], sort_keys=True, separators=(",", ":"))
                if isinstance(row[key], (dict, list))
                else ""
                if row[key] is None
                else row[key]
                for key in CSV_FIELDS
            }
        )
    return stream.getvalue()


def render_markdown(base: str, new: str, rows: list[dict]) -> str:
    number = lambda value: "—" if value is None else f"{value:,.3f}"
    md = event_comparison._md
    counts = Counter(row["status"] for row in rows)
    lines = [
        "# UK replay engine comparison",
        "",
        f"Base: `{base}`. New: `{new}`.",
        "",
        (
            "Amounts are £m, positive for gain to the Exchequer. Ratios and bins are descriptive. "
            "The certified head aggregate ratio shows how the fiscal base moved alongside the measure ratio. "
            "A changed construction is listed separately from a change on the same construction. "
            "Attribution comes only from the authored evidence file; unsized drivers withhold explained share."
        ),
        "",
        ", ".join(f"{key}: {value}" for key, value in sorted(counts.items())) + ".",
        "",
        "| Event / measure | FY / head | OBR £m | PE base £m | PE new £m | Change £m | Base bin | New bin | Status | Head base ratio | Measure ratio | Attribution |",
        "|---|---|---:|---:|---:|---:|---|---|---|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    md(row["event"] + " / " + row["title"]),
                    md(row["fy"] + " / " + str(row["tax_head"])),
                    *(
                        number(row[field])
                        for field in (
                            "obr_million_gbp",
                            "pe_base_million_gbp",
                            "pe_new_million_gbp",
                            "change_million_gbp",
                        )
                    ),
                    row["base_ratio_bin"],
                    row["new_ratio_bin"],
                    row["status"],
                    number(row["head_certified_aggregate_new_to_base_ratio"]),
                    number(row["measure_new_to_base_ratio"]),
                    md(
                        ", ".join(
                            driver["driver"]
                            + (" (sized)" if driver["sized"] else " (unsized)")
                            for driver in row["attribution"]
                        )
                        or "unchanged"
                    ),
                ]
            )
            + " |"
        )
    return "\n".join(lines) + "\n"


def _path_at_root(path: Path, root: Path) -> Path:
    return root / path.relative_to(ROOT)


def _verify_run_receipts(
    directory: Path,
    registry_path: Path,
    registry: dict,
    bundle: str,
    root: Path,
    commit,
    verified: dict[str, str] | None = None,
) -> None:
    """Bind the numerical manifest and each per-year progress receipt."""
    from pipeline import stage_uk_event as staging

    manifest_path = directory / "RUN_MANIFEST.json"
    commit(manifest_path)
    manifest = json.loads(manifest_path.read_bytes())
    bundles.validate_runtime_bundle(manifest, bundle, root=root)
    if manifest.get("registry_sha256") != sha256(registry_path):
        raise EngineComparisonError("compute manifest registry SHA-256 differs")
    years = set()
    for reference, digest in manifest["artifacts"].items():
        path = event_comparison._receipt_path(reference, root)
        if not path.is_relative_to(directory.resolve()) or sha256(path) != digest:
            raise EngineComparisonError(
                "compute manifest artifact path or SHA-256 differs"
            )
        commit(path)
        if verified is not None:
            verified[str(path.resolve().relative_to(root.resolve()))] = bundle
        years.add(json.loads(path.read_bytes())["year"])
    for year in sorted(years):
        progress_path = directory / f"RUN_PROGRESS_{year}.json"
        commit(progress_path)
        progress = json.loads(progress_path.read_bytes())
        bundles.validate_runtime_bundle(progress, bundle, root=root)
        expected = {
            reference: digest
            for reference, digest in manifest["artifacts"].items()
            if json.loads((root / reference).read_bytes())["year"] == year
        }
        if (
            progress.get("artifacts") != expected
            or progress.get("year") != year
            or progress.get("event") != registry["event_slug"]
            or progress.get("registry_sha256") != sha256(registry_path)
        ):
            raise EngineComparisonError(
                "per-year progress receipt differs from final numerical manifest"
            )
    # Stage's original path resolver uses compute.ROOT; supplying a separate
    # bundle_root keeps pin trust explicit for copied comparison test roots.
    original_root = staging.compute.ROOT
    try:
        staging.compute.ROOT = root
        staged_rows, tally = staging.stage_event(
            registry,
            manifest,
            artifact_dir=directory,
            registry_sha256=sha256(registry_path),
            bundle=bundle,
            bundle_root=root,
        )
    finally:
        staging.compute.ROOT = original_root
    if staged_rows != event_comparison.load_jsonl(directory / "STAGED.jsonl"):
        raise EngineComparisonError(
            "staged rows differ from verified numerical manifest"
        )
    stage_receipt = json.loads((directory / "STAGING_MANIFEST.json").read_bytes())
    if any(stage_receipt.get(field) != value for field, value in tally.items()):
        raise EngineComparisonError(
            "staging tally differs from verified numerical manifest"
        )
    modal = directory / "MODAL_RECEIPT.json"
    if modal.exists():
        commit(modal)
        # The Modal wrapper records the bundle identity in its request.
        bundles.validate_bundle_identity(
            json.loads(modal.read_bytes())["request"], bundle, root=root
        )


def validate_output_dir(output_dir: Path, artifact_root: Path) -> None:
    """Allow the shared comparison directory or a path outside both trees.

    A directory inside the registry tree, an event's results or any bundle's
    namespace is refused, so a comparison can't overwrite their files.
    """
    resolved = Path(output_dir).resolve()
    if resolved == (artifact_root / "results/uk/events").resolve():
        return
    for tree in bundles.PROTECTED_TREES.values():
        if resolved.is_relative_to((artifact_root / tree).resolve()):
            raise EngineComparisonError(
                "engine comparison output would enter a protected registry or "
                "bundle namespace"
            )


def write_engine_comparison(
    base: str,
    new: str,
    *,
    attribution_path: Path | None = None,
    output_dir: Path | None = None,
    artifact_root: Path = ROOT,
) -> list[dict]:
    """Verify both comparison receipt chains and bind every used input hash."""
    output_dir = output_dir or artifact_root / "results/uk/events"
    validate_output_dir(output_dir, artifact_root)
    bundles.load_bundle(base, root=artifact_root)
    bundles.load_bundle(new, root=artifact_root)
    attribution_path = (
        attribution_path
        or artifact_root / "data/uk/events/engine_attribution" / f"{base}__{new}.json"
    )
    attribution = json.loads(attribution_path.read_bytes())
    if attribution.get("base") != base or attribution.get("new") != new:
        raise EngineComparisonError(
            "attribution bundle pair differs from requested comparison"
        )
    inputs = {}

    def commit(path):
        reference = str(path.resolve().relative_to(artifact_root.resolve()))
        digest = sha256(path)
        if reference in inputs and inputs[reference] != digest:
            raise EngineComparisonError("input changed during engine comparison")
        inputs[reference] = digest
        return reference

    commit(attribution_path)
    for key in (base, new):
        commit(bundles.bundle_pin_path(key, root=artifact_root))
        pin = bundles.load_bundle(key, root=artifact_root)
        for label in ("requirements_freeze", "offline_audit"):
            commit(artifact_root / pin[label])
    commit(bundles.bundle_index_path(root=artifact_root))
    commit(_path_at_root(event_comparison.AXES_PATH, artifact_root))
    roots = {key: bundles.results_root(key, root=artifact_root) for key in (base, new)}
    event_sets = {
        key: {p.parent.name for p in root.glob("*/COMPARISON.json")}
        for key, root in roots.items()
    }
    registry_events = {
        key: {
            path.stem.removesuffix("_measures")
            for path in bundles.registry_path(
                "event", key, root=artifact_root
            ).parent.glob("*_measures.json")
        }
        for key in (base, new)
    }
    if (
        not event_sets[base]
        or event_sets[base] != event_sets[new]
        or registry_events[base] != registry_events[new]
        or event_sets[base] != registry_events[base]
    ):
        raise EngineComparisonError(
            "both bundles require comparisons for every event in the same nonempty registry inventory"
        )
    # Verify every bundle's receipt chain first, so sized attribution for any
    # event can only cite artifacts from a verified run manifest.
    verified_artifacts: dict[str, str] = {}
    loaded = {}
    for event in sorted(event_sets[base]):
        registries, comparisons, artifacts = {}, {}, {}
        for key in (base, new):
            directory = roots[key] / event
            path = directory / "COMPARISON.json"
            comparisons[key] = event_comparison.load_verified_comparison(
                path, artifact_root=artifact_root, bundle=key
            )
            for name in (
                "COMPARISON.json",
                "COMPARISON.md",
                "COMPARISON.csv",
                "COMPARISON_PROVENANCE.json",
            ):
                commit(directory / name)
            provenance = json.loads(
                (directory / "COMPARISON_PROVENANCE.json").read_bytes()
            )
            for label in ("registry", "staged", "staging_manifest"):
                commit(artifact_root / provenance[label + "_path"])
            registry_path = artifact_root / provenance["registry_path"]
            registries[key] = json.loads(registry_path.read_bytes())
            _verify_run_receipts(
                directory,
                registry_path,
                registries[key],
                key,
                artifact_root,
                commit,
                verified_artifacts,
            )
            source = registries[key].get("source", {})
            if source.get("claims_path"):
                source_path = artifact_root / source["claims_path"]
                if sha256(source_path) != source.get("claims_gzip_sha256"):
                    raise EngineComparisonError(
                        "OBR snapshot compressed SHA-256 differs"
                    )
                commit(source_path)
            artifacts[key] = {}
            for row in comparisons[key]:
                if row["pe_value_gbp"] is not None:
                    artifact_path = artifact_root / row["artifact"]
                    commit(artifact_path)
                    artifacts[key][row["artifact"]] = json.loads(
                        artifact_path.read_bytes()
                    )
        loaded[event] = (registries, comparisons, artifacts)
    rows = []
    for event, (registries, comparisons, artifacts) in loaded.items():
        rows.extend(
            build_engine_rows(
                registries[base],
                registries[new],
                comparisons[base],
                comparisons[new],
                attribution,
                base_artifacts=artifacts[base],
                new_artifacts=artifacts[new],
                artifact_root=artifact_root,
                input_hashes=inputs,
                verified_artifacts=verified_artifacts,
            )
        )
    payloads = {
        "ENGINE_COMPARISON.json": canonical_bytes(rows),
        "ENGINE_COMPARISON.csv": render_csv(rows).encode(),
        "ENGINE_COMPARISON.md": render_markdown(base, new, rows).encode(),
    }
    # Catch concurrent changes before any output write.
    for reference, digest in inputs.items():
        if sha256(artifact_root / reference) != digest:
            raise EngineComparisonError("input changed during engine comparison")
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, payload in payloads.items():
        atomic_write_bytes(output_dir / name, payload)
    provenance = {
        "schema_version": 1,
        "base": base,
        "new": new,
        "source_rows": len(rows),
        "inputs_sha256": dict(sorted(inputs.items())),
        "outputs_sha256": {
            name: hashlib.sha256(payload).hexdigest()
            for name, payload in sorted(payloads.items())
        },
    }
    atomic_write_bytes(
        output_dir / "ENGINE_COMPARISON_PROVENANCE.json", canonical_bytes(provenance)
    )
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True)
    parser.add_argument("--new", required=True)
    parser.add_argument("--attribution", type=Path)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args(argv)
    rows = write_engine_comparison(
        args.base,
        args.new,
        attribution_path=args.attribution,
        output_dir=args.output_dir,
    )
    print(f"wrote {len(rows)} descriptive engine-comparison source rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
