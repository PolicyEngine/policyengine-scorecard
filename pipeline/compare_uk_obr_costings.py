#!/usr/bin/env python3
"""Write descriptive OBR/PE-UK costing counterparts from staged results.

The harvested OBR descriptor carries the verbatim measure description and
source table needed to resolve every row exactly once. Every staged PE value is
then checked against the frozen source-claim snapshot and a PE value recomputed
from the raw aggregates in its saved run artifact. The standalone command
accepts only a run manifest: it SHA-verifies the registry, claims slice, and
complete artifact inventory plus staged JSONL before parsing any of them.

The output retains source head rows.  For PMD measures with at least two mapped
heads, it also shows a comparison-only sum of those mapped heads.  That sum is
never represented as, or attached to, an external TOTAL claim.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import re
import stat
import tempfile
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping

import yaml

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REGISTRY = ROOT / "data" / "uk" / "obr_measure_reforms.yaml"
DEFAULT_CLAIMS = (
    ROOT / "sources" / "harvest-20260802" / "uk_obr" / "obr_costings_claims.jsonl"
)
DEFAULT_STAGED = ROOT / "results" / "uk" / "staged" / "obr_costings.jsonl"
DEFAULT_OUTPUT_DIR = ROOT / "results" / "uk" / "obr_costings"
DEFAULT_MANIFEST = DEFAULT_OUTPUT_DIR / "RUN_MANIFEST.json"
PMD_TABLES = {
    "Tax Measures (Policy measures database)",
    "Spending Measures (Policy measures database)",
}
REQUIRED_STAGED_FIELDS = {
    "measure_key",
    "obr_description",
    "source_table",
    "benchmark_class",
    "row_kind",
    "engine_version",
    "data_bundle",
    "pe_value",
    "status",
    "pe_construction",
    "computed_at",
    "run_id",
    "annotations",
    "external_claim_match",
    "source_model",
    "basis",
    "behavioural_adjustment",
}
CSV_FIELDS = [
    "measure_key",
    "obr_description",
    "fiscal_event",
    "year",
    "fy",
    "head",
    "row_kind",
    "obr_value_gbp",
    "pe_value_gbp",
    "pe_to_obr_ratio",
    "ratio_bin",
    "status",
    "benchmark_class",
    "source_table",
    "external_metric",
    "source_model",
    "basis",
    "behavioural_adjustment",
    "construction",
    "artifact",
    "annotations",
]


class ComparisonError(ValueError):
    """A staged row cannot be tied unambiguously to its source or artifact."""


def _read_bytes(path: Path, label: str) -> bytes:
    try:
        return path.read_bytes()
    except OSError as exc:
        raise ComparisonError(f"cannot read {label} {path}: {exc}") from exc


def _parse_json_object(
    payload: bytes,
    *,
    path: Path,
    label: str,
) -> dict[str, Any]:
    try:
        value = json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ComparisonError(f"cannot parse {label} {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ComparisonError(f"{label} {path}: expected a JSON object")
    return value


def _parse_jsonl(payload: bytes, *, path: Path) -> list[dict[str, Any]]:
    try:
        lines = payload.decode("utf-8").splitlines()
    except UnicodeDecodeError as exc:
        raise ComparisonError(f"cannot parse JSONL {path}: {exc}") from exc
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ComparisonError(f"{path}:{line_number}: {exc}") from exc
        if not isinstance(row, dict):
            raise ComparisonError(f"{path}:{line_number}: expected a JSON object")
        rows.append(row)
    return rows


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return _parse_jsonl(_read_bytes(path, "JSONL"), path=path)


def _parse_registry(
    payload: bytes,
    *,
    path: Path,
) -> dict[str, dict[str, Any]]:
    try:
        spec = yaml.safe_load(payload)
    except yaml.YAMLError as exc:
        raise ComparisonError(f"cannot parse registry {path}: {exc}") from exc
    if not isinstance(spec, dict) or not isinstance(spec.get("measures"), list):
        raise ComparisonError(f"{path}: expected a mapping with a measures list")
    measures: dict[str, dict[str, Any]] = {}
    for index, measure in enumerate(spec["measures"]):
        if not isinstance(measure, dict) or not isinstance(
            measure.get("measure_key"), str
        ):
            raise ComparisonError(f"{path}: measures[{index}] has no measure_key")
        key = measure["measure_key"]
        if key in measures:
            raise ComparisonError(f"{path}: duplicate measure_key {key!r}")
        measures[key] = measure
    return measures


def load_registry(path: Path) -> dict[str, dict[str, Any]]:
    return _parse_registry(_read_bytes(path, "registry"), path=path)


def _resolve_recorded_path(
    reference: Any,
    *,
    artifact_root: Path,
    role: str,
) -> Path:
    if not isinstance(reference, str) or not reference:
        raise ComparisonError(f"{role} must be a non-empty recorded path")
    relative = Path(reference)
    if relative.is_absolute():
        raise ComparisonError(f"{role} must be relative to the artifact root")
    root = artifact_root.resolve()
    path = (root / relative).resolve()
    try:
        canonical = path.relative_to(root).as_posix()
    except ValueError as exc:
        raise ComparisonError(
            f"{role} {reference!r} escapes artifact root {root}"
        ) from exc
    if reference != canonical:
        raise ComparisonError(
            f"{role} must be canonical; recorded {reference!r}, canonical {canonical!r}"
        )
    return path


def _validate_sha256(value: Any, *, field: str, manifest_path: Path) -> str:
    if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
        raise ComparisonError(f"{manifest_path}: {field} must be a lowercase SHA-256")
    return value


def validate_comparison_path_plan(
    *,
    manifest: Mapping[str, Any],
    manifest_path: Path,
    artifact_root: Path,
    output_dir: Path,
) -> None:
    """Reject input aliases and comparison outputs that overwrite run inputs."""

    artifact_root = artifact_root.resolve()
    manifest_path = manifest_path.resolve()
    artifact_dir = manifest_path.parent
    file_roles = [
        ("manifest", manifest_path),
        (
            "registry",
            _resolve_recorded_path(
                manifest.get("registry"),
                artifact_root=artifact_root,
                role="registry",
            ),
        ),
        (
            "claims",
            _resolve_recorded_path(
                manifest.get("claims"),
                artifact_root=artifact_root,
                role="claims",
            ),
        ),
        (
            "staged_output",
            _resolve_recorded_path(
                manifest.get("staged_output"),
                artifact_root=artifact_root,
                role="staged_output",
            ),
        ),
    ]
    references = manifest.get("artifacts")
    if not isinstance(references, list):
        raise ComparisonError(f"{manifest_path}: artifacts must be a list")
    for index, reference in enumerate(references):
        path = _resolve_recorded_path(
            reference,
            artifact_root=artifact_root,
            role=f"artifact {index}",
        )
        try:
            path.relative_to(artifact_dir)
        except ValueError as exc:
            raise ComparisonError(
                f"artifact {reference!r} escapes manifest directory {artifact_dir}"
            ) from exc
        file_roles.append((f"artifact {index}", path))

    output_dir = output_dir.resolve()
    file_roles.extend(
        [
            ("comparison CSV", output_dir / "COMPARISON.csv"),
            ("comparison Markdown", output_dir / "COMPARISON.md"),
        ]
    )
    seen_paths: dict[Path, str] = {}
    seen_normalized: dict[str, tuple[str, Path]] = {}
    seen_inodes: dict[tuple[int, int], tuple[str, Path]] = {}
    for role, path in file_roles:
        previous_role = seen_paths.get(path)
        if previous_role is not None:
            raise ComparisonError(
                f"path collision: {previous_role} and {role} resolve to {path}"
            )
        seen_paths[path] = role
        normalized = unicodedata.normalize("NFC", str(path)).casefold()
        previous_normalized = seen_normalized.get(normalized)
        if previous_normalized is not None:
            previous_role, previous_path = previous_normalized
            raise ComparisonError(
                f"path collision: {previous_role} {previous_path} and "
                f"{role} {path} have the same normalized path"
            )
        seen_normalized[normalized] = (role, path)
        try:
            result = path.stat()
        except OSError:
            continue
        inode = (result.st_dev, result.st_ino)
        previous_inode = seen_inodes.get(inode)
        if previous_inode is not None:
            previous_role, previous_path = previous_inode
            raise ComparisonError(
                f"path collision: {previous_role} {previous_path} and "
                f"{role} {path} identify the same file"
            )
        seen_inodes[inode] = (role, path)


def _verify_payload(
    payload: bytes,
    *,
    path: Path,
    expected_sha256: str,
    role: str,
) -> None:
    actual_sha256 = hashlib.sha256(payload).hexdigest()
    if actual_sha256 != expected_sha256:
        raise ComparisonError(
            f"{path}: {role} SHA-256 differs from RUN_MANIFEST; "
            f"expected {expected_sha256}; actual {actual_sha256}"
        )


def load_verified_comparison_inputs(
    *,
    manifest_path: Path,
    artifact_root: Path = ROOT,
) -> tuple[
    dict[str, Any],
    list[dict[str, Any]],
    list[dict[str, Any]],
    dict[str, dict[str, Any]],
    dict[str, dict[str, Any]],
]:
    """SHA-gate all manifest inputs, then parse each retained payload once."""

    artifact_root = artifact_root.resolve()
    manifest_path = manifest_path.resolve()
    try:
        manifest_path.relative_to(artifact_root)
    except ValueError as exc:
        raise ComparisonError(
            f"manifest {manifest_path} escapes artifact root {artifact_root}"
        ) from exc
    manifest = _parse_json_object(
        _read_bytes(manifest_path, "run manifest"),
        path=manifest_path,
        label="run manifest",
    )
    if manifest.get("schema_version") != 1:
        raise ComparisonError(
            f"{manifest_path}: unsupported manifest schema "
            f"{manifest.get('schema_version')!r}"
        )
    if manifest.get("staged") is not True:
        raise ComparisonError(
            f"{manifest_path}: comparison requires a manifest with staged=true"
        )

    registry_path = _resolve_recorded_path(
        manifest.get("registry"),
        artifact_root=artifact_root,
        role="registry",
    )
    claims_path = _resolve_recorded_path(
        manifest.get("claims"),
        artifact_root=artifact_root,
        role="claims",
    )
    staged_path = _resolve_recorded_path(
        manifest.get("staged_output"),
        artifact_root=artifact_root,
        role="staged_output",
    )
    registry_sha256 = _validate_sha256(
        manifest.get("registry_sha256"),
        field="registry_sha256",
        manifest_path=manifest_path,
    )
    claims_sha256 = _validate_sha256(
        manifest.get("claims_sha256"),
        field="claims_sha256",
        manifest_path=manifest_path,
    )
    staged_sha256 = _validate_sha256(
        manifest.get("staged_sha256"),
        field="staged_sha256",
        manifest_path=manifest_path,
    )
    references = manifest.get("artifacts")
    if (
        not isinstance(references, list)
        or not all(isinstance(reference, str) for reference in references)
        or len(references) != len(set(references))
    ):
        raise ComparisonError(
            f"{manifest_path}: artifacts must be unique recorded paths"
        )
    artifact_paths = {
        reference: _resolve_recorded_path(
            reference,
            artifact_root=artifact_root,
            role=f"artifact {index}",
        )
        for index, reference in enumerate(references)
    }
    recorded_artifact_sha256 = manifest.get("artifact_sha256")
    if not isinstance(recorded_artifact_sha256, dict):
        raise ComparisonError(
            f"{manifest_path}: artifact_sha256 must be a path-to-SHA mapping"
        )
    if set(recorded_artifact_sha256) != set(references):
        missing = sorted(set(references) - set(recorded_artifact_sha256))
        extra = sorted(set(recorded_artifact_sha256) - set(references))
        raise ComparisonError(
            f"{manifest_path}: artifact_sha256 inventory differs; "
            f"missing {missing}; extra {extra}"
        )
    artifact_digests = {
        reference: _validate_sha256(
            recorded_artifact_sha256[reference],
            field=f"artifact_sha256[{reference!r}]",
            manifest_path=manifest_path,
        )
        for reference in references
    }

    registry_payload = _read_bytes(registry_path, "registry")
    claims_payload = _read_bytes(claims_path, "claims slice")
    staged_payload = _read_bytes(staged_path, "staged results")
    artifact_payloads = {
        reference: _read_bytes(path, "run artifact")
        for reference, path in artifact_paths.items()
    }
    _verify_payload(
        registry_payload,
        path=registry_path,
        expected_sha256=registry_sha256,
        role="registry",
    )
    _verify_payload(
        claims_payload,
        path=claims_path,
        expected_sha256=claims_sha256,
        role="claims slice",
    )
    _verify_payload(
        staged_payload,
        path=staged_path,
        expected_sha256=staged_sha256,
        role="staged results",
    )
    for reference in references:
        _verify_payload(
            artifact_payloads[reference],
            path=artifact_paths[reference],
            expected_sha256=artifact_digests[reference],
            role="artifact",
        )

    registry = _parse_registry(registry_payload, path=registry_path)
    claims = _parse_jsonl(claims_payload, path=claims_path)
    artifacts = {
        reference: _parse_json_object(
            artifact_payloads[reference],
            path=artifact_paths[reference],
            label="run artifact",
        )
        for reference in references
    }
    run_id = manifest.get("run_id")
    if not isinstance(run_id, str) or not run_id:
        raise ComparisonError(f"{manifest_path}: run_id must be non-empty text")
    for reference, artifact in artifacts.items():
        if artifact.get("run_id") != run_id:
            raise ComparisonError(f"{reference}: run_id differs from RUN_MANIFEST")
    staged_rows = _parse_jsonl(staged_payload, path=staged_path)
    if not staged_rows:
        raise ComparisonError(f"staged results are empty: {staged_path}")
    staged_count = manifest.get("staged_rows")
    if (
        isinstance(staged_count, bool)
        or not isinstance(staged_count, int)
        or staged_count != len(staged_rows)
    ):
        raise ComparisonError(
            f"{manifest_path}: staged_rows records {staged_count!r}; "
            f"loaded {len(staged_rows)}"
        )
    return manifest, staged_rows, claims, registry, artifacts


def claim_metric(claim: dict[str, Any]) -> str | None:
    """Return the staged metric name without mutating PMD spending rows."""

    return claim.get("metric") or claim.get("proposed_metric")


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def resolve_external_claim(
    staged_row: dict[str, Any], claims: Iterable[dict[str, Any]]
) -> dict[str, Any]:
    """Resolve one source row using only the staged match descriptor."""

    missing = REQUIRED_STAGED_FIELDS - set(staged_row)
    if missing:
        raise ComparisonError(
            f"staged row is missing required fields: {sorted(missing)}"
        )
    if staged_row["benchmark_class"] != "different_model":
        raise ComparisonError(
            f"{staged_row['measure_key']}: expected benchmark_class=different_model"
        )
    match = staged_row["external_claim_match"]
    if not isinstance(match, dict):
        raise ComparisonError(
            f"{staged_row['measure_key']}: external_claim_match must be a mapping"
        )
    expected_match_fields = {
        "source",
        "metric",
        "period",
        "source_table",
        "reform_hint",
        "conditions",
    }
    if set(match) != expected_match_fields:
        raise ComparisonError(
            f"{staged_row['measure_key']}: external_claim_match fields are "
            f"{sorted(match)}; expected {sorted(expected_match_fields)}"
        )
    conditions_key = _canonical(match["conditions"])
    hits = [
        claim
        for claim in claims
        if claim.get("source") == match["source"]
        and claim_metric(claim) == match["metric"]
        and claim.get("period") == match["period"]
        and claim.get("source_table") == match["source_table"]
        and claim.get("reform_hint") == match["reform_hint"]
        and _canonical(claim.get("conditions")) == conditions_key
    ]
    if len(hits) != 1:
        raise ComparisonError(
            f"{staged_row['measure_key']} {match['period']}: {len(hits)} OBR rows "
            "match external_claim_match; expected one"
        )
    claim = hits[0]
    expected_source_facts = {
        "source_model": claim.get("source_model"),
        "basis": claim.get("conditions", {}).get("basis"),
        "behavioural_adjustment": "unstated in harvest",
    }
    staged_source_facts = {key: staged_row.get(key) for key in expected_source_facts}
    if staged_source_facts != expected_source_facts:
        raise ComparisonError(
            f"{staged_row['measure_key']} {match['period']}: staged source facts "
            "differ from the matched harvest row"
        )
    if claim.get("proposed_unit") != "gbp":
        raise ComparisonError(
            f"{staged_row['measure_key']} {match['period']}: expected normalized gbp"
        )
    if not _is_number(claim.get("value")) or not math.isfinite(claim["value"]):
        raise ComparisonError(
            f"{staged_row['measure_key']} {match['period']}: invalid OBR value"
        )
    return claim


def _head_name(head: Mapping[str, Any]) -> str:
    value = head.get("obr_head")
    return value if isinstance(value, str) and value else "<unnamed head>"


def _finite_number(value: Any, *, context: str) -> float | int:
    if not _is_number(value) or not math.isfinite(value):
        raise ComparisonError(f"{context}: expected a finite number")
    return value


def recompute_artifact_head_pe_value(
    artifact: Mapping[str, Any],
    head: Mapping[str, Any],
    *,
    reference: str,
) -> float:
    """Recompute one head solely from top-level raw aggregates and signs."""

    name = _head_name(head)
    raw_aggregates = artifact.get("raw_aggregates")
    if not isinstance(raw_aggregates, dict):
        raise ComparisonError(f"{reference}: {name}: raw_aggregates is not a mapping")
    baseline = raw_aggregates.get("baseline_gbp")
    reform = raw_aggregates.get("reform_gbp")
    if not isinstance(baseline, dict) or not isinstance(reform, dict):
        raise ComparisonError(
            f"{reference}: {name}: raw baseline/reform aggregates are not mappings"
        )
    variables = head.get("pe_variables")
    if (
        not isinstance(variables, list)
        or not variables
        or not all(isinstance(variable, str) and variable for variable in variables)
    ):
        raise ComparisonError(f"{reference}: {name}: invalid pe_variables")
    try:
        raw_delta = sum(
            _finite_number(
                reform[variable],
                context=f"{reference}: {name}: reform {variable}",
            )
            - _finite_number(
                baseline[variable],
                context=f"{reference}: {name}: baseline {variable}",
            )
            for variable in variables
        )
    except KeyError as exc:
        raise ComparisonError(
            f"{reference}: {name}: missing raw aggregate {exc.args[0]!r}"
        ) from exc

    channel = head.get("channel")
    if channel == "tax":
        exchequer_delta = raw_delta
    elif channel == "spending":
        exchequer_delta = -raw_delta
    else:
        raise ComparisonError(f"{reference}: {name}: invalid channel {channel!r}")
    construction = artifact.get("construction")
    if construction == "reversal_on_certified_world":
        return -exchequer_delta
    if construction == "forward_from_baseline":
        return exchequer_delta
    raise ComparisonError(f"{reference}: {name}: invalid construction {construction!r}")


def _expected_registry_head(
    measure: Mapping[str, Any],
    artifact_head: Mapping[str, Any],
    *,
    reference: str,
) -> Mapping[str, Any]:
    heads = measure.get("heads")
    if not isinstance(heads, list):
        raise ComparisonError(f"{reference}: registry heads are not a list")
    hits = [
        head
        for head in heads
        if isinstance(head, dict)
        and head.get("obr_head") == artifact_head.get("obr_head")
        and head.get("condition_key") == artifact_head.get("condition_key")
        and head.get("source_table", measure.get("source_table"))
        == artifact_head.get("source_table")
        and head.get("external_metric", measure.get("external_metric"))
        == artifact_head.get("external_metric")
    ]
    if len(hits) != 1:
        raise ComparisonError(
            f"{reference}: {_head_name(artifact_head)}: {len(hits)} registry "
            "heads match; expected one"
        )
    return hits[0]


def validate_artifact_heads(
    artifacts_by_reference: Mapping[str, dict[str, Any]],
    registry: Mapping[str, dict[str, Any]],
) -> None:
    """Validate every inventory head before any comparison output is rendered."""

    for reference, artifact in artifacts_by_reference.items():
        if artifact.get("artifact") != reference:
            raise ComparisonError(
                f"{reference}: artifact self-reference differs from inventory"
            )
        heads = artifact.get("heads")
        if not isinstance(heads, list) or not all(
            isinstance(head, dict) for head in heads
        ):
            raise ComparisonError(f"{reference}: heads must be a list of mappings")
        diagnostic_only = artifact.get("diagnostic_only")
        measure = None
        if diagnostic_only is False:
            key = artifact.get("measure_key")
            measure = registry.get(key) if isinstance(key, str) else None
            if measure is None:
                raise ComparisonError(
                    f"{reference}: measure_key {key!r} is absent from registry"
                )
            if artifact.get("construction") != measure.get("construction"):
                raise ComparisonError(
                    f"{reference}: construction differs from registry"
                )
        elif diagnostic_only is not True:
            raise ComparisonError(
                f"{reference}: diagnostic_only must be an explicit boolean"
            )

        for head in heads:
            name = _head_name(head)
            if measure is not None:
                expected = _expected_registry_head(
                    measure,
                    head,
                    reference=reference,
                )
                for field in ("pe_variables", "channel"):
                    if head.get(field) != expected.get(field):
                        raise ComparisonError(
                            f"{reference}: {name}: {field} differs from registry"
                        )
            recomputed = recompute_artifact_head_pe_value(
                artifact,
                head,
                reference=reference,
            )
            stored = head.get("pe_value")
            if stored != recomputed:
                raise ComparisonError(
                    f"{reference}: {name}: stored pe_value {stored!r} differs "
                    f"from recomputed pe_value {recomputed!r}"
                )


def _staged_snapshot_identity(staged_row: Mapping[str, Any]) -> tuple[Any, ...] | None:
    match = staged_row.get("external_claim_match")
    if not isinstance(match, dict):
        return None
    return (
        match.get("source"),
        match.get("source_table"),
        match.get("reform_hint"),
        staged_row.get("source_model"),
        match.get("metric"),
        match.get("period"),
        _canonical(match.get("conditions")),
    )


def validate_staged_artifact_completeness(
    staged_rows: Iterable[dict[str, Any]],
    artifacts_by_reference: Mapping[str, dict[str, Any]],
) -> None:
    """Require one staged row per source-backed non-diagnostic artifact head."""

    expected: Counter[tuple[str, tuple[Any, ...]]] = Counter()
    for reference, artifact in artifacts_by_reference.items():
        if artifact.get("diagnostic_only") is True:
            continue
        for head in artifact["heads"]:
            snapshot = head.get("external_claim")
            if isinstance(snapshot, dict):
                expected[(reference, _snapshot_identity(snapshot))] += 1

    actual: Counter[tuple[str, tuple[Any, ...]]] = Counter()
    for staged_row in staged_rows:
        if staged_row.get("pe_value") is None:
            continue
        reference = staged_row.get("artifact")
        identity = _staged_snapshot_identity(staged_row)
        if isinstance(reference, str) and identity is not None:
            actual[(reference, identity)] += 1

    if actual != expected:
        missing = sum((expected - actual).values())
        extra = sum((actual - expected).values())
        raise ComparisonError(
            "staged/artifact head inventory differs: "
            f"{missing} missing staged rows; {extra} extra staged rows"
        )


def _snapshot_identity(snapshot: dict[str, Any]) -> tuple[Any, ...]:
    return (
        snapshot.get("source"),
        snapshot.get("source_table"),
        snapshot.get("reform_hint"),
        snapshot.get("source_model"),
        snapshot.get("metric"),
        snapshot.get("period"),
        _canonical(snapshot.get("conditions")),
    )


def _claim_identity(claim: dict[str, Any]) -> tuple[Any, ...]:
    return (
        claim.get("source"),
        claim.get("source_table"),
        claim.get("reform_hint"),
        claim.get("source_model"),
        claim_metric(claim),
        claim.get("period"),
        _canonical(claim.get("conditions")),
    )


def validate_artifact_trace(
    staged_row: dict[str, Any],
    claim: dict[str, Any],
    artifacts_by_reference: Mapping[str, dict[str, Any]],
) -> dict[str, Any] | None:
    """Validate a staged PE value against its retained run artifact object."""

    pe_value = staged_row["pe_value"]
    if pe_value is None:
        if staged_row.get("artifact") is not None:
            raise ComparisonError(
                f"{staged_row['measure_key']}: null PE value unexpectedly "
                "names an artifact"
            )
        return None
    if not _is_number(pe_value) or not math.isfinite(pe_value):
        raise ComparisonError(f"{staged_row['measure_key']}: invalid staged PE value")
    reference = staged_row.get("artifact")
    if not isinstance(reference, str) or not reference:
        raise ComparisonError(
            f"{staged_row['measure_key']}: every PE value must name a run artifact"
        )
    artifact = artifacts_by_reference.get(reference)
    if artifact is None:
        raise ComparisonError(
            f"{staged_row['measure_key']}: artifact {reference!r} is absent "
            "from the verified manifest inventory"
        )
    match = staged_row["external_claim_match"]
    expected = {
        "measure_key": staged_row["measure_key"],
        "obr_description": staged_row["obr_description"],
        "year": match["period"],
        "engine_version": staged_row["engine_version"],
        "data_bundle": staged_row["data_bundle"],
        "run_id": staged_row["run_id"],
        "benchmark_class": staged_row["benchmark_class"],
    }
    differences = {
        key: {"staged": value, "artifact": artifact.get(key)}
        for key, value in expected.items()
        if artifact.get(key) != value
    }
    if differences:
        raise ComparisonError(
            f"{reference}: staged/artifact identity differs: {differences}"
        )

    claim_identity = _claim_identity(claim)
    hits = [
        head
        for head in artifact.get("heads", [])
        if isinstance(head, dict)
        and isinstance(head.get("external_claim"), dict)
        and _snapshot_identity(head["external_claim"]) == claim_identity
    ]
    if len(hits) != 1:
        raise ComparisonError(
            f"{reference}: external_claim_match differs from verified artifact "
            f"heads: {len(hits)} artifact heads match the frozen OBR claim; "
            "expected one"
        )
    head = hits[0]
    snapshot = head["external_claim"]
    if snapshot.get("value_gbp") != claim["value"]:
        raise ComparisonError(f"{reference}: frozen and harvested OBR values differ")
    if snapshot.get("unit") != "gbp":
        raise ComparisonError(f"{reference}: frozen OBR value is not normalized to gbp")
    recomputed = recompute_artifact_head_pe_value(
        artifact,
        head,
        reference=reference,
    )
    if head.get("pe_value") != recomputed or pe_value != recomputed:
        raise ComparisonError(
            f"{reference}: {_head_name(head)}: staged pe_value {pe_value!r} and "
            f"stored pe_value {head.get('pe_value')!r} must equal recomputed "
            f"pe_value {recomputed!r}"
        )
    return head


def ratio_and_bin(
    obr_value: float | None, pe_value: float | None
) -> tuple[float | None, str]:
    """Return PE/OBR and a descriptive signed-ratio bin."""

    if obr_value is None or pe_value is None:
        return None, "not_available"
    if not math.isfinite(obr_value) or not math.isfinite(pe_value):
        raise ComparisonError("ratio inputs must be finite")
    if obr_value == 0 and pe_value == 0:
        return None, "both_zero"
    if obr_value == 0:
        return None, "obr_zero"
    ratio = pe_value / obr_value
    if pe_value == 0:
        return ratio, "pe_zero"
    if ratio < 0:
        return ratio, "opposite_sign"
    if ratio < 0.5:
        return ratio, "same_sign_ratio_below_0.5"
    if ratio < 0.8:
        return ratio, "same_sign_ratio_0.5_to_0.8"
    if ratio < 1.25:
        return ratio, "same_sign_ratio_0.8_to_1.25"
    if ratio < 2:
        return ratio, "same_sign_ratio_1.25_to_2"
    return ratio, "same_sign_ratio_at_least_2"


def _head_label(staged_row: dict[str, Any], claim: dict[str, Any]) -> str:
    if staged_row["row_kind"] == "total":
        return "Total"
    conditions = claim["conditions"]
    return (
        conditions.get("tax_head")
        or conditions.get("spending_head")
        or "Unspecified head"
    )


def _axis_annotation(staged_row: dict[str, Any], head: str) -> str:
    if staged_row["row_kind"] == "total":
        head_axis = "published Table 3.17 measure total vs mapped PE aggregate"
    else:
        head_axis = f"single mapped source head ({head})"
    return (
        "Comparison scope: benchmark_class=different_model; "
        f"head_scope={head_axis}; remaining_difference=unexplained."
    )


def _deduplicate_annotations(annotations: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for annotation in annotations:
        if annotation not in seen:
            output.append(annotation)
            seen.add(annotation)
    return output


def _effective_computability(measure: dict[str, Any], year: int) -> str:
    overrides = measure.get("computability_overrides", {})
    override = overrides.get(year, overrides.get(str(year)))
    return (
        override["computability"]
        if isinstance(override, dict)
        else measure["computability"]
    )


def _effective_computability_details(
    measure: Mapping[str, Any], year: int
) -> tuple[Any, Any]:
    overrides = measure.get("computability_overrides", {})
    override = (
        overrides.get(year, overrides.get(str(year)))
        if isinstance(overrides, dict)
        else None
    )
    if isinstance(override, dict):
        return override.get("computability"), override.get("note")
    return measure.get("computability"), None


def _claim_descriptor(claim: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "source": claim.get("source"),
        "metric": claim_metric(dict(claim)),
        "period": claim.get("period"),
        "source_table": claim.get("source_table"),
        "reform_hint": claim.get("reform_hint"),
        "conditions": claim.get("conditions"),
    }


def _source_facts_annotation(claim: Mapping[str, Any]) -> str:
    return (
        "OBR source facts: "
        f"source_model={claim.get('source_model')}; "
        f"basis={claim.get('conditions', {}).get('basis')}; "
        "behavioural_adjustment=unstated in harvest."
    )


def _constructed_annotations(
    *,
    measure: Mapping[str, Any],
    artifact: Mapping[str, Any],
    artifact_head: Mapping[str, Any],
    claim: Mapping[str, Any],
) -> list[str]:
    year = artifact.get("year")
    variables = " + ".join(artifact_head["pe_variables"])
    sign = "+Δtax" if artifact_head.get("channel") == "tax" else "−Δspending"
    construction = (
        "PE: static microsimulation on the certified world; reversal re-oriented "
        "to the announced measure; "
        f"PE calendar year {year} proxies FY "
        f"{year}-{str(year + 1)[-2:]}. "
        "measure Δ = −(reversal − baseline)."
        if artifact.get("construction") == "reversal_on_certified_world"
        else (
            "PE: static microsimulation on the certified world; forward change "
            f"from the certified baseline; PE calendar year {year} proxies FY "
            f"{year}-{str(year + 1)[-2:]}. "
            "measure Δ = +(reform − baseline)."
        )
    )
    annotations = [
        _source_facts_annotation(claim),
        construction,
        (
            f"Head mapping: {artifact_head.get('obr_head')} = {variables}; "
            f"positive gain to the Exchequer = {sign}."
        ),
    ]
    computability, override_note = _effective_computability_details(measure, year)
    if computability == "partial":
        override_annotation = (
            f" Per-year computability override: {override_note}."
            if override_note is not None
            else ""
        )
        unmapped = measure.get("unmapped_obr_heads", [])
        annotations.append(
            "Partial construction: "
            + str(measure.get("notes"))
            + (" Unmapped OBR heads: " + ", ".join(unmapped) + "." if unmapped else "")
            + override_annotation
        )
    return annotations


def _not_computed_annotations(
    *,
    measure: Mapping[str, Any],
    claim: Mapping[str, Any],
) -> list[str]:
    year = claim.get("period")
    conditions = claim.get("conditions", {})
    head = conditions.get("tax_head") or conditions.get("spending_head") or "Total"
    no_simulation = (
        "PE: no microsimulation constructed; the registry construction is a "
        "reversal on the certified world."
        if measure.get("construction") == "reversal_on_certified_world"
        else (
            "PE: no microsimulation constructed; the registry construction is a "
            "forward change from the certified baseline."
        )
    )
    return [
        _source_facts_annotation(claim),
        (
            "No PE value: this registry entry is not expressible as a supported "
            "plain parameter reform."
        ),
        no_simulation,
        f"PE calendar year {year} would proxy OBR FY {year}-{str(year + 1)[-2:]}.",
        f"Head mapping unavailable for {head}; no aggregate is substituted.",
    ]


def validate_staged_descriptive_fields(
    staged_row: Mapping[str, Any],
    claim: Mapping[str, Any],
    measure: Mapping[str, Any],
    artifact_head: Mapping[str, Any] | None,
    artifacts_by_reference: Mapping[str, dict[str, Any]],
) -> None:
    """Re-derive output-driving staged text from verified claims and artifacts."""

    if artifact_head is None:
        conditions = claim.get("conditions", {})
        head = conditions.get("tax_head") or conditions.get("spending_head") or "Total"
        expected = {
            "row_kind": "total" if head == "Total" else "head",
            "status": "not_computed",
            "source_table": claim.get("source_table"),
            "annotations": _not_computed_annotations(measure=measure, claim=claim),
            "external_claim_match": _claim_descriptor(claim),
        }
    else:
        reference = staged_row.get("artifact")
        artifact = artifacts_by_reference.get(reference)
        if artifact is None:
            raise ComparisonError(
                f"{staged_row.get('measure_key')}: verified artifact {reference!r} "
                "is unavailable for staged-field validation"
            )
        expected = {
            "row_kind": (
                "total" if artifact_head.get("condition_key") is None else "head"
            ),
            "status": "constructed",
            "source_table": artifact_head.get("source_table"),
            "annotations": _constructed_annotations(
                measure=measure,
                artifact=artifact,
                artifact_head=artifact_head,
                claim=claim,
            ),
            "external_claim_match": _claim_descriptor(claim),
        }
    differences = [
        field for field, value in expected.items() if staged_row.get(field) != value
    ]
    if differences:
        raise ComparisonError(
            f"{staged_row.get('measure_key')} {claim.get('period')}: staged fields "
            "differ from verified artifact/claim inputs: "
            + ", ".join(differences)
        )


def build_head_row(
    staged_row: dict[str, Any],
    claim: dict[str, Any],
    measure: dict[str, Any],
    artifact_head: dict[str, Any] | None,
) -> dict[str, Any]:
    pe_value = staged_row["pe_value"]
    obr_value = float(claim["value"])
    ratio, ratio_bin = ratio_and_bin(obr_value, pe_value)
    head = _head_label(staged_row, claim)
    annotations = _deduplicate_annotations(
        [
            *staged_row["annotations"],
            _axis_annotation(staged_row, head),
        ]
    )
    if artifact_head is not None and staged_row["row_kind"] == "total":
        annotations.append(
            "Table 3.17 is retained as a measure-total row; its PE head mapping is "
            + " + ".join(artifact_head.get("pe_variables", []))
            + "."
        )
    return {
        "measure_key": staged_row["measure_key"],
        "obr_description": staged_row["obr_description"],
        "fiscal_event": measure["fiscal_event"],
        "year": claim["period"],
        "fy": claim["conditions"].get(
            "fy", f"{claim['period']}-{str(claim['period'] + 1)[-2:]}"
        ),
        "head": head,
        "row_kind": staged_row["row_kind"],
        "obr_value_gbp": obr_value,
        "pe_value_gbp": pe_value,
        "pe_to_obr_ratio": ratio,
        "ratio_bin": ratio_bin,
        "status": staged_row["status"],
        "benchmark_class": staged_row["benchmark_class"],
        "source_table": staged_row["source_table"],
        "external_metric": staged_row["external_claim_match"]["metric"],
        "source_model": claim["source_model"],
        "basis": claim["conditions"]["basis"],
        "behavioural_adjustment": "unstated in harvest",
        "construction": measure["construction"],
        "artifact": staged_row.get("artifact", ""),
        "annotations": annotations,
    }


def derive_mapped_head_totals(
    head_rows: list[dict[str, Any]], registry: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    """Sum two or more mapped PMD heads without inventing a TOTAL claim."""

    groups: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
    for row in head_rows:
        if row["row_kind"] == "head" and row["source_table"] in PMD_TABLES:
            groups[(row["measure_key"], row["year"])].append(row)

    totals: list[dict[str, Any]] = []
    for (measure_key, year), rows in groups.items():
        if len(rows) < 2 or any(row["pe_value_gbp"] is None for row in rows):
            continue
        measure = registry[measure_key]
        heads = [row["head"] for row in rows]
        obr_value = math.fsum(row["obr_value_gbp"] for row in rows)
        pe_value = math.fsum(row["pe_value_gbp"] for row in rows)
        ratio, ratio_bin = ratio_and_bin(obr_value, pe_value)
        source_tables = sorted({row["source_table"] for row in rows})
        metrics = sorted({row["external_metric"] for row in rows})
        source_models = {row["source_model"] for row in rows}
        bases = {row["basis"] for row in rows}
        behavioural_adjustments = {row["behavioural_adjustment"] for row in rows}
        if (
            len(source_models) != 1
            or len(bases) != 1
            or behavioural_adjustments != {"unstated in harvest"}
        ):
            raise ComparisonError(
                f"{measure_key} {year}: mapped heads have inconsistent source facts"
            )
        source_model = next(iter(source_models))
        basis = next(iter(bases))
        annotations = [
            "Derived mapped-head total for this comparison only: sums "
            + ", ".join(heads)
            + "; it is not attached to an external TOTAL claim.",
            (
                "OBR source facts represented by the mapped heads: "
                f"source_model={source_model}; basis={basis}; "
                "behavioural_adjustment=unstated in harvest."
            ),
            (
                "PE: static microsimulation on the certified world; reversal "
                "re-oriented to the announced measure; "
                f"PE calendar year {year} proxies FY {rows[0]['fy']}. "
                "measure Δ = −(reversal − baseline)."
                if measure["construction"] == "reversal_on_certified_world"
                else (
                    "PE: static microsimulation on the certified world; forward "
                    "change from the certified baseline; "
                    f"PE calendar year {year} proxies FY {rows[0]['fy']}. "
                    "measure Δ = +(reform − baseline)."
                )
            ),
            (
                "Comparison scope: benchmark_class=different_model; "
                "head_scope=mapped PMD heads only; "
                "remaining_difference=unexplained."
            ),
            "Registry construction: " + measure["notes"],
        ]
        unmapped = measure.get("unmapped_obr_heads", [])
        if unmapped or _effective_computability(measure, year) == "partial":
            detail = (
                " Unmapped OBR heads: " + ", ".join(unmapped) + "." if unmapped else ""
            )
            annotations.append(
                "Partial scope: this is not an all-head measure total." + detail
            )
        totals.append(
            {
                "measure_key": measure_key,
                "obr_description": rows[0]["obr_description"],
                "fiscal_event": rows[0]["fiscal_event"],
                "year": year,
                "fy": rows[0]["fy"],
                "head": "Mapped-head total",
                "row_kind": "mapped_head_total",
                "obr_value_gbp": obr_value,
                "pe_value_gbp": pe_value,
                "pe_to_obr_ratio": ratio,
                "ratio_bin": ratio_bin,
                "status": rows[0]["status"],
                "benchmark_class": "different_model",
                "source_table": " + ".join(source_tables),
                "external_metric": " + ".join(metrics),
                "source_model": source_model,
                "basis": basis,
                "behavioural_adjustment": "unstated in harvest",
                "construction": measure["construction"],
                "artifact": " + ".join(
                    sorted({row["artifact"] for row in rows if row["artifact"]})
                ),
                "annotations": annotations,
            }
        )
    return totals


def build_comparison_rows(
    staged_rows: list[dict[str, Any]],
    claims: list[dict[str, Any]],
    registry: dict[str, dict[str, Any]],
    *,
    artifacts_by_reference: Mapping[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Resolve, trace, and assemble head and mapped-head-total rows."""

    validate_artifact_heads(artifacts_by_reference, registry)
    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, str, int, str]] = set()
    for staged_row in staged_rows:
        key = staged_row.get("measure_key")
        if key not in registry:
            raise ComparisonError(f"staged measure_key {key!r} is not in the registry")
        measure = registry[key]
        if staged_row.get("obr_description") != measure.get("obr_description"):
            raise ComparisonError(f"{key}: staged and registry descriptions differ")
        if not isinstance(staged_row.get("annotations"), list) or not all(
            isinstance(item, str) for item in staged_row["annotations"]
        ):
            raise ComparisonError(f"{key}: annotations must be a list of strings")
        claim = resolve_external_claim(staged_row, claims)
        artifact_head = validate_artifact_trace(
            staged_row,
            claim,
            artifacts_by_reference,
        )
        validate_staged_descriptive_fields(
            staged_row,
            claim,
            measure,
            artifact_head,
            artifacts_by_reference,
        )
        identity = (
            key,
            staged_row["source_table"],
            claim["period"],
            _canonical(staged_row["external_claim_match"]["conditions"]),
        )
        if identity in seen:
            raise ComparisonError(f"duplicate staged comparison identity: {identity}")
        seen.add(identity)
        rows.append(build_head_row(staged_row, claim, measure, artifact_head))
    validate_staged_artifact_completeness(staged_rows, artifacts_by_reference)
    rows.extend(derive_mapped_head_totals(rows, registry))
    row_kind_order = {"head": 0, "total": 0, "mapped_head_total": 1}
    return sorted(
        rows,
        key=lambda row: (
            row["measure_key"],
            row["year"],
            row_kind_order.get(row["row_kind"], 9),
            row["head"],
        ),
    )


def _csv_value(value: Any) -> Any:
    if value is None:
        return ""
    if isinstance(value, list):
        return " | ".join(value)
    return value


def render_csv(rows: list[dict[str, Any]]) -> str:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=CSV_FIELDS, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({field: _csv_value(row.get(field)) for field in CSV_FIELDS})
    return output.getvalue()


def _markdown_escape(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def _format_gbp_billions(value: float | None) -> str:
    return "—" if value is None else f"{value / 1e9:+.3f}"


def _format_ratio(value: float | None) -> str:
    return "—" if value is None else f"{value:.3f}"


def render_markdown(rows: list[dict[str, Any]]) -> str:
    lines = [
        "# OBR and PE-UK static costing counterparts",
        "",
        (
            "Values are GBP billions under the harvested OBR "
            "`positive_gain_to_exchequer` orientation. `PE / OBR` uses the "
            "announced-measure orientation: certified-world reversal legs are "
            "sign-flipped, while forward changes retain their sign. "
            "`benchmark_class` is `different_model`."
        ),
        "",
        (
            "Source head rows are preserved. `Mapped-head total` rows are "
            "comparison-only sums of two or more staged PMD heads, not external "
            "TOTAL claims; annotations identify partial scope and leave the "
            "remaining difference unexplained."
        ),
        "",
        (
            "| Measure | FY | Head / scope | OBR (£bn) | PE (£bn) | PE / OBR "
            "| Ratio bin | Status | Annotations |"
        ),
        "|---|---:|---|---:|---:|---:|---|---|---|",
    ]
    for row in rows:
        annotations = " ".join(row["annotations"])
        values = [
            f"{row['obr_description']} (`{row['measure_key']}`)",
            row["fy"],
            row["head"],
            _format_gbp_billions(row["obr_value_gbp"]),
            _format_gbp_billions(row["pe_value_gbp"]),
            _format_ratio(row["pe_to_obr_ratio"]),
            row["ratio_bin"],
            row["status"],
            annotations,
        ]
        lines.append(
            "| " + " | ".join(_markdown_escape(value) for value in values) + " |"
        )
    lines.extend(
        [
            "",
            "Ratio-bin boundaries",
            "",
            "- `opposite_sign`: the signed PE/OBR ratio is negative.",
            (
                "- Same-sign numeric bins: below 0.5; 0.5–0.8; 0.8–1.25; "
                "1.25–2; at least 2."
            ),
            (
                "- `pe_zero`, `obr_zero`, `both_zero`, and `not_available` "
                "describe zero or absent values directly."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    destination_mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else 0o644
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as destination:
            temporary = Path(destination.name)
            destination.write(text)
        assert temporary is not None
        temporary.chmod(destination_mode)
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def write_comparison_outputs_from_rows(
    *,
    staged_rows: list[dict[str, Any]],
    claims: list[dict[str, Any]],
    registry: dict[str, dict[str, Any]],
    artifacts_by_reference: Mapping[str, dict[str, Any]],
    output_dir: Path = DEFAULT_OUTPUT_DIR,
) -> list[dict[str, Any]]:
    """Write deterministic outputs from already-validated in-memory inputs."""

    if not staged_rows:
        raise ComparisonError("staged results are empty")
    rows = build_comparison_rows(
        staged_rows,
        claims,
        registry,
        artifacts_by_reference=artifacts_by_reference,
    )
    atomic_write_text(output_dir / "COMPARISON.csv", render_csv(rows))
    atomic_write_text(output_dir / "COMPARISON.md", render_markdown(rows))
    return rows


def write_comparison_outputs(
    *,
    manifest_path: Path,
    output_dir: Path | None = None,
    artifact_root: Path = ROOT,
) -> list[dict[str, Any]]:
    """Load one manifest-bound run and write deterministic comparison outputs."""

    manifest, staged_rows, claims, registry, artifacts = (
        load_verified_comparison_inputs(
            manifest_path=manifest_path,
            artifact_root=artifact_root,
        )
    )
    resolved_output_dir = output_dir or manifest_path.resolve().parent
    validate_comparison_path_plan(
        manifest=manifest,
        manifest_path=manifest_path,
        artifact_root=artifact_root,
        output_dir=resolved_output_dir,
    )
    return write_comparison_outputs_from_rows(
        staged_rows=staged_rows,
        claims=claims,
        registry=registry,
        artifacts_by_reference=artifacts,
        output_dir=resolved_output_dir,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        type=Path,
        required=True,
        help=(
            "Required RUN_MANIFEST; supplies the SHA-bound registry, claims, "
            "staged results, and complete artifact inventory"
        ),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Comparison destination (default: RUN_MANIFEST directory)",
    )
    parser.add_argument(
        "--artifact-root",
        type=Path,
        default=ROOT,
        help="Base for artifact paths stored relative to the repository root",
    )
    args = parser.parse_args(argv)

    rows = write_comparison_outputs(
        manifest_path=args.manifest,
        output_dir=args.output_dir,
        artifact_root=args.artifact_root,
    )
    output_dir = args.output_dir or args.manifest.resolve().parent
    csv_path = output_dir / "COMPARISON.csv"
    markdown_path = output_dir / "COMPARISON.md"
    totals = sum(row["row_kind"] == "mapped_head_total" for row in rows)
    print(
        f"wrote {len(rows)} descriptive rows ({totals} mapped-head totals) to "
        f"{csv_path} and {markdown_path}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
