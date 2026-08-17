#!/usr/bin/env python3
"""Compute static PE-UK counterparts to selected OBR policy costings.

The managed PolicyEngine baseline is the certified world served by
``policyengine.py``. Registry reforms are plain parameter dictionaries. Most
entries reverse a policy already present in that certified world. Artifacts
retain both raw aggregates and the literal reversal delta, while ``pe_value``
is oriented to the announced measure so it is directly comparable with OBR.

No managed microsimulation is constructed by ``--dry-run`` or ``--restage``.
Normal execution forces Hugging Face offline mode before importing
PolicyEngine, so a missing certified artifact fails instead of downloading a
different world.
"""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
import math
import os
import re
import sys
import threading
import time
from collections import Counter
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any, Iterable

import yaml

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REGISTRY = ROOT / "data" / "uk" / "obr_measure_reforms.yaml"
DEFAULT_CLAIMS = Path.home() / "scorecard-harvest" / "uk_obr" / "claims_staged.jsonl"
DEFAULT_OUTPUT_DIR = ROOT / "results" / "uk" / "obr_costings"
DEFAULT_STAGED_OUTPUT = ROOT / "results" / "uk" / "staged" / "obr_costings.jsonl"
LOCAL_DATA_MIRROR_ROOT = ROOT / "data" / "uk" / "policyengine-local"
YEAR_MIN = 2024
YEAR_MAX = 2030
COMPUTABILITY = {"expressible", "partial", "not_expressible"}
CONSTRUCTIONS = {"reversal_on_certified_world", "forward_from_baseline"}
STAGED_STATUSES = {"comparable", "constructed", "concept_mismatch", "not_computed"}
REQUIRED_MEASURE_FIELDS = {
    "measure_key",
    "fiscal_event",
    "obr_description",
    "source_table",
    "external_metric",
    "pe_reform",
    "start_fy",
    "computability",
    "notes",
    "construction",
    "heads",
    "unmapped_obr_heads",
}
DATE_RANGE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})\.(\d{4})-(\d{2})-(\d{2})$")
MEASURE_KEY = re.compile(r"^[a-z0-9][a-z0-9_]*$")
NI_HEAD_VARIABLES = [
    "ni_class_1_employee",
    "ni_class_1_employer",
    "ni_class_4",
]
RUN_ID_DATE = datetime.now().astimezone().strftime("%Y%m%d")


class RegistryError(ValueError):
    """The registry or one of its engine/source references is invalid."""


class ClaimMatchError(ValueError):
    """A registry measure/head did not resolve to exactly one source row."""


class ArtifactRestageError(ValueError):
    """An existing run artifact cannot be safely restaged from raw aggregates."""


def configure_offline() -> None:
    """Make a cache miss fail rather than trigger a network request."""

    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ["HF_DATASETS_OFFLINE"] = "1"
    os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
    os.environ["POLICYENGINE_UK_DATA_REPO"] = str(LOCAL_DATA_MIRROR_ROOT)


def package_version(name: str) -> str:
    try:
        return version(name)
    except PackageNotFoundError:
        return "unavailable"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def fy_label(year: int) -> str:
    return f"{year}-{str(year + 1)[-2:]}"


def load_registry(path: Path = DEFAULT_REGISTRY) -> dict[str, Any]:
    spec = yaml.safe_load(path.read_text())
    if not isinstance(spec, dict) or not isinstance(spec.get("measures"), list):
        raise RegistryError(f"{path}: expected a mapping with a measures list")
    return spec


def load_claims(path: Path = DEFAULT_CLAIMS) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text().splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_number}: {exc}") from exc
        rows.append(row)
    return rows


def claim_metric(claim: dict[str, Any]) -> str | None:
    """Adopt PMD spending's proposed metric without mutating the harvest."""

    return claim.get("metric") or claim.get("proposed_metric")


def head_source_table(measure: dict[str, Any], head: dict[str, Any]) -> str:
    return head.get("source_table", measure["source_table"])


def head_external_metric(measure: dict[str, Any], head: dict[str, Any]) -> str:
    return head.get("external_metric", measure["external_metric"])


def _source_candidates(
    claims: Iterable[dict[str, Any]],
    measure: dict[str, Any],
    year: int,
    *,
    head: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    table = head_source_table(measure, head) if head else None
    metric = head_external_metric(measure, head) if head else None
    hits: list[dict[str, Any]] = []
    for claim in claims:
        if claim.get("source") != "obr":
            continue
        if claim.get("period") != year:
            continue
        if claim.get("reform_hint") != measure["obr_description"]:
            continue
        if table is not None and claim.get("source_table") != table:
            continue
        if metric is not None and claim_metric(claim) != metric:
            continue
        if claim.get("source_table") != "3.17: 3.17":
            if (
                claim.get("conditions", {}).get("fiscal_event")
                != measure["fiscal_event"]
            ):
                continue
        if head is not None and head.get("condition_key") is not None:
            if (
                claim.get("conditions", {}).get(head["condition_key"])
                != head["obr_head"]
            ):
                continue
        hits.append(claim)
    return hits


def resolve_claim(
    claims: Iterable[dict[str, Any]],
    measure: dict[str, Any],
    head: dict[str, Any],
    year: int,
) -> dict[str, Any] | None:
    """Resolve a mapped head, returning None only outside its source window."""

    hits = _source_candidates(claims, measure, year, head=head)
    if len(hits) == 1:
        return hits[0]
    if len(hits) > 1:
        raise ClaimMatchError(
            f"{measure['measure_key']} {year} {head['obr_head']}: "
            f"{len(hits)} source matches; expected exactly one"
        )
    any_measure_rows = _source_candidates(claims, measure, year)
    if any_measure_rows:
        raise ClaimMatchError(
            f"{measure['measure_key']} {year} {head['obr_head']}: "
            "measure exists in source window but mapped head has zero matches"
        )
    return None


def external_claim_match(claim: dict[str, Any]) -> dict[str, Any]:
    """Descriptor uses the exact harvested conditions, never a subset."""

    return {
        "source": claim["source"],
        "metric": claim_metric(claim),
        "period": claim["period"],
        "conditions": claim["conditions"],
    }


def source_claim_snapshot(claim: dict[str, Any]) -> dict[str, Any]:
    """Freeze the source identity and normalized value used by an artifact."""

    metric_field = "metric" if claim.get("metric") is not None else "proposed_metric"
    return {
        "source": claim["source"],
        "source_table": claim["source_table"],
        "reform_hint": claim["reform_hint"],
        "metric": claim_metric(claim),
        "source_metric_field": metric_field,
        "period": claim["period"],
        "conditions": claim["conditions"],
        "value_gbp": claim["value"],
        "value_raw": claim.get("value_raw"),
        "normalization": claim.get("normalization"),
        "unit": claim.get("proposed_unit"),
        "time_basis": claim.get("time_basis"),
    }


def _validate_date_range(value: str, context: str) -> None:
    match = DATE_RANGE.match(value)
    if match is None:
        raise RegistryError(f"{context}: invalid date range {value!r}")
    start = tuple(int(x) for x in match.groups()[:3])
    end = tuple(int(x) for x in match.groups()[3:])
    if start > end:
        raise RegistryError(f"{context}: reversed date range {value!r}")


def validate_registry(
    spec: dict[str, Any],
    *,
    tax_benefit_system: Any | None = None,
    claims: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Validate schema, engine paths/variables, and optional source identities."""

    measures = spec["measures"]
    keys: set[str] = set()
    counts: Counter[str] = Counter()
    source_head_years = 0
    for index, measure in enumerate(measures):
        context = f"measures[{index}]"
        if not isinstance(measure, dict):
            raise RegistryError(f"{context}: expected mapping")
        missing = REQUIRED_MEASURE_FIELDS - set(measure)
        if missing:
            raise RegistryError(f"{context}: missing fields {sorted(missing)}")
        key = measure["measure_key"]
        if not isinstance(key, str) or MEASURE_KEY.fullmatch(key) is None:
            raise RegistryError(
                f"{context}: measure_key must be lowercase filesystem-safe text"
            )
        if key in keys:
            raise RegistryError(f"duplicate measure_key {key!r}")
        keys.add(key)
        if measure["computability"] not in COMPUTABILITY:
            raise RegistryError(f"{key}: invalid computability")
        if measure["construction"] not in CONSTRUCTIONS:
            raise RegistryError(f"{key}: invalid construction")
        if not isinstance(measure["start_fy"], int):
            raise RegistryError(f"{key}: start_fy must be an integer")
        if not isinstance(measure["notes"], str) or not measure["notes"].strip():
            raise RegistryError(f"{key}: notes must be non-empty")
        if not isinstance(measure["heads"], list):
            raise RegistryError(f"{key}: heads must be a list")
        if not isinstance(measure["unmapped_obr_heads"], list):
            raise RegistryError(f"{key}: unmapped_obr_heads must be a list")
        reform = measure["pe_reform"]
        if measure["computability"] == "not_expressible":
            if reform is not None:
                raise RegistryError(f"{key}: not_expressible requires pe_reform: null")
        elif not isinstance(reform, dict) or not reform:
            raise RegistryError(f"{key}: runnable entry needs a non-empty pe_reform")
        if reform:
            for path, schedule in reform.items():
                if (
                    not isinstance(path, str)
                    or not isinstance(schedule, dict)
                    or not schedule
                ):
                    raise RegistryError(f"{key}: invalid reform schedule for {path!r}")
                for period, value in schedule.items():
                    _validate_date_range(str(period), f"{key} {path}")
                    if not isinstance(value, (bool, int, float)):
                        raise RegistryError(
                            f"{key} {path}: unsupported parameter value {value!r}"
                        )
                    if not isinstance(value, bool) and not math.isfinite(float(value)):
                        raise RegistryError(
                            f"{key} {path}: reform values must be finite"
                        )
                if tax_benefit_system is not None:
                    try:
                        tax_benefit_system.parameters.get_child(path)
                    except Exception as exc:
                        raise RegistryError(
                            f"{key}: unresolved parameter {path!r}: {exc}"
                        ) from exc
        head_identities: set[tuple[str, str | None, str]] = set()
        for head_index, head in enumerate(measure["heads"]):
            hctx = f"{key} heads[{head_index}]"
            if not isinstance(head, dict):
                raise RegistryError(f"{hctx}: expected mapping")
            required = {"obr_head", "condition_key", "pe_variables", "channel"}
            if required - set(head):
                raise RegistryError(f"{hctx}: missing {sorted(required - set(head))}")
            if head["condition_key"] not in (None, "tax_head", "spending_head"):
                raise RegistryError(f"{hctx}: invalid condition_key")
            if head["channel"] not in ("tax", "spending"):
                raise RegistryError(f"{hctx}: invalid channel")
            if not isinstance(head["obr_head"], str) or not head["obr_head"]:
                raise RegistryError(f"{hctx}: obr_head must be non-empty text")
            identity = (
                head["obr_head"],
                head["condition_key"],
                head_source_table(measure, head),
            )
            if identity in head_identities:
                raise RegistryError(f"{hctx}: duplicate head identity {identity}")
            head_identities.add(identity)
            variables = head["pe_variables"]
            if not isinstance(variables, list) or not variables:
                raise RegistryError(f"{hctx}: pe_variables must be non-empty")
            if head["obr_head"] == "NICs" and variables != NI_HEAD_VARIABLES:
                raise RegistryError(
                    f"{hctx}: NICs must be exactly {NI_HEAD_VARIABLES}, got {variables}"
                )
            if tax_benefit_system is not None:
                missing_variables = [
                    v for v in variables if v not in tax_benefit_system.variables
                ]
                if missing_variables:
                    raise RegistryError(
                        f"{hctx}: unknown PE variables {missing_variables}"
                    )
            if claims is not None:
                years_with_rows = 0
                for year in range(YEAR_MIN, YEAR_MAX + 1):
                    hit = resolve_claim(claims, measure, head, year)
                    if hit is not None:
                        years_with_rows += 1
                if years_with_rows == 0:
                    raise RegistryError(
                        f"{hctx}: no source rows in {YEAR_MIN}-{YEAR_MAX}"
                    )
                source_head_years += years_with_rows
        if claims is not None and not measure["heads"]:
            source_years = sum(
                bool(_source_candidates(claims, measure, year))
                for year in range(YEAR_MIN, YEAR_MAX + 1)
            )
            if source_years == 0:
                raise RegistryError(f"{key}: no source rows in {YEAR_MIN}-{YEAR_MAX}")
        counts[measure["computability"]] += 1
    return {
        "measures": len(measures),
        "computability": dict(sorted(counts.items())),
        "source_head_years": source_head_years,
    }


def parse_tokens(values: list[str] | None) -> list[str]:
    out: list[str] = []
    for value in values or []:
        out.extend(token.strip() for token in value.split(",") if token.strip())
    return out


def select_measures(
    measures: list[dict[str, Any]],
    requested: list[str] | None,
    limit: int | None,
) -> list[dict[str, Any]]:
    requested_keys = parse_tokens(requested)
    if len(set(requested_keys)) != len(requested_keys):
        raise RegistryError("duplicate --measures keys")
    by_key = {measure["measure_key"]: measure for measure in measures}
    if requested_keys:
        unknown = [key for key in requested_keys if key not in by_key]
        if unknown:
            raise RegistryError(f"unknown --measures keys: {unknown}")
        selected = [by_key[key] for key in requested_keys]
    else:
        # A full run preserves null-reform registry entries as not_computed
        # staged rows. They never construct simulations.
        selected = list(measures)
    if limit is not None:
        if limit < 1:
            raise RegistryError("--limit must be positive")
        selected = selected[:limit]
    return selected


def select_years(requested: list[str] | None) -> list[int]:
    tokens = parse_tokens(requested)
    years = (
        [int(token) for token in tokens]
        if tokens
        else list(range(YEAR_MIN, YEAR_MAX + 1))
    )
    invalid = [year for year in years if not YEAR_MIN <= year <= YEAR_MAX]
    if invalid:
        raise RegistryError(f"years outside {YEAR_MIN}-{YEAR_MAX}: {invalid}")
    if len(set(years)) != len(years):
        raise RegistryError("duplicate --years values")
    return sorted(years)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ensure_writable_local_mirror(
    cached_path: Path, relative_artifact_path: str, expected_sha256: str
) -> tuple[Path, bool]:
    """Copy certified bytes into the workspace for PyTables' read/write open."""

    mirror_path = (
        LOCAL_DATA_MIRROR_ROOT
        / "policyengine_uk_data"
        / "storage"
        / relative_artifact_path
    )
    created = False
    if not mirror_path.exists():
        mirror_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = mirror_path.with_name(mirror_path.name + ".tmp")
        if temporary.exists():
            temporary.unlink()
        try:
            with cached_path.open("rb") as source, temporary.open("wb") as target:
                for chunk in iter(lambda: source.read(8 * 1024 * 1024), b""):
                    target.write(chunk)
            if sha256_file(temporary) != expected_sha256:
                raise RuntimeError("workspace mirror copy failed SHA-256 verification")
            temporary.replace(mirror_path)
            created = True
        finally:
            if temporary.exists():
                temporary.unlink()
    if sha256_file(mirror_path) != expected_sha256:
        raise RuntimeError(
            "workspace UK data mirror differs from the certified artifact; "
            "refusing to overwrite it"
        )
    try:
        with mirror_path.open("r+b"):
            pass
    except OSError as exc:
        raise RuntimeError(
            f"workspace UK data mirror is not writable: {mirror_path}"
        ) from exc
    return mirror_path, created


def preflight_certified_dataset() -> dict[str, Any]:
    """Prove that the bundled dataset is cached and matches its manifest hash."""

    configure_offline()
    import policyengine as pe
    from huggingface_hub import hf_hub_download
    from policyengine.provenance.dataset_sources import parse_hf_uri

    bundle = dict(pe.uk.uk_latest.release_bundle)
    dataset_uri = bundle.get("default_dataset_uri")
    expected_sha256 = bundle.get("certified_data_artifact_sha256")
    if not isinstance(dataset_uri, str) or not dataset_uri.startswith("hf://"):
        raise RuntimeError(
            f"certified UK dataset is not a supported HF artifact: {dataset_uri!r}"
        )
    if not isinstance(expected_sha256, str) or not expected_sha256:
        raise RuntimeError("certified UK release has no artifact SHA-256")
    reference = parse_hf_uri(dataset_uri)
    try:
        cached_path = Path(
            hf_hub_download(
                repo_id=reference.repo_id,
                repo_type="dataset",
                filename=reference.path,
                revision=reference.version,
                local_files_only=True,
            )
        )
    except Exception as exc:
        raise RuntimeError(
            "certified UK artifact is not cached; refusing any network fallback"
        ) from exc
    started = time.perf_counter()
    actual_sha256 = sha256_file(cached_path)
    if actual_sha256 != expected_sha256:
        raise RuntimeError(
            "cached UK artifact SHA-256 differs from the certified release manifest"
        )
    mirror_path, mirror_created = ensure_writable_local_mirror(
        cached_path, reference.path, expected_sha256
    )
    hash_seconds = time.perf_counter() - started
    return {
        "release_bundle": bundle,
        "dataset_uri": dataset_uri,
        "cached_file": cached_path.name,
        "sha256": actual_sha256,
        "hash_seconds": hash_seconds,
        "local_files_only": True,
        "managed_local_mirror": relative_to_root(mirror_path),
        "managed_local_mirror_created": mirror_created,
    }


def current_rss_bytes() -> tuple[int, str]:
    try:
        import psutil

        return psutil.Process(os.getpid()).memory_info().rss, "psutil_process_rss"
    except (ImportError, OSError):
        import resource

        rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        # macOS reports bytes; Linux reports KiB.
        if sys.platform != "darwin":
            rss *= 1024
        return int(rss), "resource_process_lifetime_peak"


class PeakRSSSampler:
    """Sample whole-process RSS while one managed sim is alive."""

    def __init__(self, interval_seconds: float = 0.1):
        self.interval_seconds = interval_seconds
        self.stop_event = threading.Event()
        self.thread: threading.Thread | None = None
        self.start_rss_bytes = 0
        self.peak_rss_bytes = 0
        self.end_rss_bytes = 0
        self.method = ""

    def _sample(self) -> None:
        while not self.stop_event.wait(self.interval_seconds):
            rss, _ = current_rss_bytes()
            self.peak_rss_bytes = max(self.peak_rss_bytes, rss)

    def __enter__(self) -> "PeakRSSSampler":
        self.start_rss_bytes, self.method = current_rss_bytes()
        self.peak_rss_bytes = self.start_rss_bytes
        self.thread = threading.Thread(target=self._sample, daemon=True)
        self.thread.start()
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.stop_event.set()
        if self.thread is not None:
            self.thread.join(timeout=2)
        self.end_rss_bytes, _ = current_rss_bytes()
        self.peak_rss_bytes = max(self.peak_rss_bytes, self.end_rss_bytes)

    def as_dict(self) -> dict[str, Any]:
        return {
            "rss_method": self.method,
            "start_rss_bytes": self.start_rss_bytes,
            "peak_rss_bytes": self.peak_rss_bytes,
            "end_rss_bytes": self.end_rss_bytes,
        }


def variable_metadata(
    tax_benefit_system: Any, variables: Iterable[str]
) -> dict[str, Any]:
    metadata: dict[str, Any] = {}
    for name in variables:
        variable = tax_benefit_system.variables[name]
        metadata[name] = {
            "label": getattr(variable, "label", None),
            "entity": variable.entity.key,
            "definition_period": str(getattr(variable, "definition_period", None)),
            "unit": str(getattr(variable, "unit", None)),
        }
    return metadata


def run_managed_simulation(
    *,
    year: int,
    variables: list[str],
    reform: dict[str, Any] | None,
) -> dict[str, Any]:
    """Run, aggregate, delete, and collect exactly one managed sim."""

    configure_offline()
    import policyengine as pe

    started = time.perf_counter()
    sim = None
    try:
        with PeakRSSSampler() as memory:
            sim = (
                pe.uk.managed_microsimulation()
                if reform is None
                else pe.uk.managed_microsimulation(reform=reform)
            )
            bundle = dict(getattr(sim, "policyengine_bundle", {}) or {})
            if not bundle.get("certified_data_build_id"):
                raise RuntimeError(
                    "managed sim did not expose a certified data build id"
                )
            missing = [
                name
                for name in variables
                if name not in sim.tax_benefit_system.variables
            ]
            if missing:
                raise RuntimeError(f"managed sim lacks variables: {missing}")
            aggregates: dict[str, float] = {}
            for name in variables:
                calculated = sim.calculate(name, str(year))
                aggregate = float(calculated.sum())
                del calculated
                if not math.isfinite(aggregate):
                    raise RuntimeError(f"{name} {year}: non-finite aggregate")
                aggregates[name] = aggregate
            metadata = variable_metadata(sim.tax_benefit_system, variables)
            wall_seconds = time.perf_counter() - started
    except BaseException:
        sim = None
        gc.collect()
        raise
    sim = None
    cleanup_started = time.perf_counter()
    gc.collect()
    cleanup_seconds = time.perf_counter() - cleanup_started
    rss_after_gc, rss_method = current_rss_bytes()
    performance = {
        "wall_seconds": wall_seconds,
        **memory.as_dict(),
        "cleanup_seconds": cleanup_seconds,
        "rss_after_gc_bytes": rss_after_gc,
        "rss_after_gc_method": rss_method,
    }
    return {
        "aggregates_gbp": aggregates,
        "variable_metadata": metadata,
        "policyengine_bundle": bundle,
        "performance": performance,
    }


def assert_managed_bundle(
    runtime_bundle: dict[str, Any], release_bundle: dict[str, Any]
) -> None:
    """Require every certified release identity field in the managed run."""

    differences = {
        key: {"release": value, "runtime": runtime_bundle.get(key)}
        for key, value in release_bundle.items()
        if runtime_bundle.get(key) != value
    }
    if differences:
        raise RuntimeError(f"managed run differs from release bundle: {differences}")


def data_bundle_id(policyengine_bundle: dict[str, Any]) -> str:
    value = policyengine_bundle.get("certified_data_build_id")
    if not isinstance(value, str) or not value:
        raise RuntimeError("policyengine_bundle.certified_data_build_id is missing")
    return value


def reform_minus_baseline(
    baseline: dict[str, float], reform: dict[str, float], variables: Iterable[str]
) -> float:
    return sum(reform[name] - baseline[name] for name in variables)


def orient_exchequer_effect(
    raw_reform_minus_baseline: float,
    channel: str,
    construction: str,
) -> tuple[float, float]:
    """Return ``(literal_delta, pe_value)`` in exchequer-gain sign.

    Let ``G = +(reform - baseline)`` for tax and
    ``G = -(reform - baseline)`` for spending. The staging identity is
    ``pe_value = -G`` for ``reversal_on_certified_world`` (the announced
    measure is the reversal's undoing), and ``pe_value = +G`` for
    ``forward_from_baseline``.
    """

    if channel == "tax":
        literal_delta = raw_reform_minus_baseline
    elif channel == "spending":
        literal_delta = -raw_reform_minus_baseline
    else:
        raise ValueError(f"unknown channel {channel!r}")
    if construction == "reversal_on_certified_world":
        return literal_delta, -literal_delta
    if construction == "forward_from_baseline":
        return literal_delta, literal_delta
    raise ValueError(f"unknown construction {construction!r}")


def artifact_path(output_dir: Path, measure_key: str, year: int) -> Path:
    return output_dir / f"{measure_key}_{year}.json"


def relative_to_root(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT.resolve()))
    except ValueError:
        return str(path.resolve())


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(text)
    temporary.replace(path)


def write_json(path: Path, value: Any) -> None:
    atomic_write_text(
        path, json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"
    )


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    text = "".join(
        json.dumps(row, sort_keys=True, allow_nan=False) + "\n" for row in rows
    )
    atomic_write_text(path, text)


def load_json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise ArtifactRestageError(f"cannot read {label} {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ArtifactRestageError(f"{label} {path}: expected a JSON object")
    return value


def resolve_recorded_path(reference: str, root: Path = ROOT) -> Path:
    if not isinstance(reference, str) or not reference:
        raise ArtifactRestageError("recorded path must be non-empty text")
    path = Path(reference)
    return path if path.is_absolute() else root / path


def measure_head_identity(
    measure: dict[str, Any], head: dict[str, Any]
) -> tuple[str, str | None, str, str]:
    return (
        head["obr_head"],
        head["condition_key"],
        head_source_table(measure, head),
        head_external_metric(measure, head),
    )


def artifact_head_identity(head: dict[str, Any]) -> tuple[Any, ...]:
    return (
        head.get("obr_head"),
        head.get("condition_key"),
        head.get("source_table"),
        head.get("external_metric"),
    )


def rederive_artifact_orientation(
    artifact: dict[str, Any],
    measure: dict[str, Any],
    *,
    path: Path,
) -> dict[str, Any]:
    """Validate and rederive one artifact from its persisted raw aggregates."""

    expected_identity = {
        "measure_key": measure["measure_key"],
        "fiscal_event": measure["fiscal_event"],
        "obr_description": measure["obr_description"],
        "source_table": measure["source_table"],
        "construction": measure["construction"],
        "computability": measure["computability"],
        "reform": measure["pe_reform"],
        "benchmark_class": "different_model",
    }
    differences = {
        key: {"artifact": artifact.get(key), "registry": expected}
        for key, expected in expected_identity.items()
        if artifact.get(key) != expected
    }
    if differences:
        raise ArtifactRestageError(
            f"{path}: artifact/registry identity differs: {differences}"
        )
    if artifact.get("schema_version") != 1:
        raise ArtifactRestageError(
            f"{path}: unsupported artifact schema {artifact.get('schema_version')!r}"
        )
    year = artifact.get("year")
    if not isinstance(year, int) or not YEAR_MIN <= year <= YEAR_MAX:
        raise ArtifactRestageError(f"{path}: invalid artifact year {year!r}")
    raw_aggregates = artifact.get("raw_aggregates")
    if not isinstance(raw_aggregates, dict):
        raise ArtifactRestageError(f"{path}: raw_aggregates must be a mapping")
    baseline = raw_aggregates.get("baseline_gbp")
    reform = raw_aggregates.get("reform_gbp")
    if not isinstance(baseline, dict) or not isinstance(reform, dict):
        raise ArtifactRestageError(
            f"{path}: raw baseline/reform aggregates must be mappings"
        )

    artifact_heads = artifact.get("heads")
    if not isinstance(artifact_heads, list) or not all(
        isinstance(head, dict) for head in artifact_heads
    ):
        raise ArtifactRestageError(f"{path}: heads must be a list of mappings")
    by_identity: dict[tuple[Any, ...], dict[str, Any]] = {}
    for result in artifact_heads:
        identity = artifact_head_identity(result)
        if identity in by_identity:
            raise ArtifactRestageError(f"{path}: duplicate artifact head {identity}")
        by_identity[identity] = result
    expected_identities = {
        measure_head_identity(measure, head) for head in measure["heads"]
    }
    if set(by_identity) != expected_identities:
        raise ArtifactRestageError(
            f"{path}: artifact and registry head identities differ"
        )

    for head in measure["heads"]:
        identity = measure_head_identity(measure, head)
        result = by_identity[identity]
        variables = head["pe_variables"]
        if result.get("pe_variables") != variables:
            raise ArtifactRestageError(
                f"{path}: {head['obr_head']} PE variables differ from registry"
            )
        if result.get("channel") != head["channel"]:
            raise ArtifactRestageError(
                f"{path}: {head['obr_head']} channel differs from registry"
            )
        try:
            baseline_head = {name: baseline[name] for name in variables}
            reform_head = {name: reform[name] for name in variables}
        except KeyError as exc:
            raise ArtifactRestageError(
                f"{path}: missing raw aggregate {exc.args[0]!r}"
            ) from exc
        if result.get("baseline_aggregates_gbp") != baseline_head:
            raise ArtifactRestageError(
                f"{path}: {head['obr_head']} baseline aggregates differ"
            )
        if result.get("reform_aggregates_gbp") != reform_head:
            raise ArtifactRestageError(
                f"{path}: {head['obr_head']} reform aggregates differ"
            )
        raw_delta = reform_minus_baseline(baseline, reform, variables)
        if result.get("raw_reform_minus_baseline_gbp") != raw_delta:
            raise ArtifactRestageError(
                f"{path}: {head['obr_head']} raw delta does not reconcile"
            )
        literal_delta, pe_value = orient_exchequer_effect(
            raw_delta, head["channel"], measure["construction"]
        )
        delta_field = (
            "reversal_delta_exchequer_gain"
            if measure["construction"] == "reversal_on_certified_world"
            else "forward_delta_exchequer_gain"
        )
        other_delta_field = (
            "forward_delta_exchequer_gain"
            if delta_field == "reversal_delta_exchequer_gain"
            else "reversal_delta_exchequer_gain"
        )
        if other_delta_field in result:
            raise ArtifactRestageError(
                f"{path}: {head['obr_head']} has the wrong construction delta field"
            )
        if delta_field in result:
            if (
                result[delta_field] != literal_delta
                or result.get("pe_value") != pe_value
            ):
                raise ArtifactRestageError(
                    f"{path}: {head['obr_head']} oriented values do not reconcile"
                )
        elif result.get("pe_value") != literal_delta:
            raise ArtifactRestageError(
                f"{path}: {head['obr_head']} legacy PE value is not the literal delta"
            )
        result[delta_field] = literal_delta
        result["pe_value"] = pe_value
    return artifact


def annotations_for(
    measure: dict[str, Any],
    head: dict[str, Any],
    year: int,
) -> list[str]:
    variables = " + ".join(head["pe_variables"])
    sign = "+Δtax" if head["channel"] == "tax" else "−Δspending"
    construction = (
        "Reversal leg on the certified world, re-oriented to the announced "
        "measure: measure Δ = −(reversal − baseline)."
        if measure["construction"] == "reversal_on_certified_world"
        else (
            "Forward leg from the certified baseline: "
            "measure Δ = +(reform − baseline)."
        )
    )
    notes = [
        "PE-UK static microsimulation; the OBR published costing is behavioural-adjusted.",
        construction,
        f"PE calendar year {year} proxies OBR FY {fy_label(year)}.",
        f"Head mapping: {head['obr_head']} = {variables}; positive gain to the Exchequer = {sign}.",
    ]
    if measure["computability"] == "partial":
        notes.append(
            "Partial construction: "
            + measure["notes"]
            + (
                " Unmapped OBR heads: "
                + ", ".join(measure.get("unmapped_obr_heads", []))
                + "."
                if measure.get("unmapped_obr_heads")
                else ""
            )
        )
    return notes


def build_artifact(
    *,
    measure: dict[str, Any],
    year: int,
    baseline: dict[str, Any],
    reform: dict[str, Any],
    output_path: Path,
    computed_at: str,
    run_id: str,
    claims: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    baseline_bundle = baseline["policyengine_bundle"]
    reform_bundle = reform["policyengine_bundle"]
    if baseline_bundle != reform_bundle:
        raise RuntimeError(
            f"{measure['measure_key']} {year}: baseline/reform bundles differ"
        )

    heads: list[dict[str, Any]] = []
    for head in measure["heads"]:
        variables = head["pe_variables"]
        raw_delta = reform_minus_baseline(
            baseline["aggregates_gbp"], reform["aggregates_gbp"], variables
        )
        literal_delta, pe_value = orient_exchequer_effect(
            raw_delta, head["channel"], measure["construction"]
        )
        if not math.isfinite(literal_delta) or not math.isfinite(pe_value):
            raise RuntimeError(
                f"{measure['measure_key']} {year} {head['obr_head']}: "
                "non-finite PE value"
            )
        matched_claim = (
            resolve_claim(claims, measure, head, year) if claims is not None else None
        )
        construction_delta_field = (
            "reversal_delta_exchequer_gain"
            if measure["construction"] == "reversal_on_certified_world"
            else "forward_delta_exchequer_gain"
        )
        heads.append(
            {
                "obr_head": head["obr_head"],
                "condition_key": head["condition_key"],
                "source_table": head_source_table(measure, head),
                "external_metric": head_external_metric(measure, head),
                "channel": head["channel"],
                "pe_variables": variables,
                "baseline_aggregates_gbp": {
                    name: baseline["aggregates_gbp"][name] for name in variables
                },
                "reform_aggregates_gbp": {
                    name: reform["aggregates_gbp"][name] for name in variables
                },
                "raw_reform_minus_baseline_gbp": raw_delta,
                construction_delta_field: literal_delta,
                "pe_value": pe_value,
                "sign_convention": "positive_gain_to_exchequer",
                "external_claim": (
                    source_claim_snapshot(matched_claim)
                    if matched_claim is not None
                    else None
                ),
            }
        )
    return {
        "schema_version": 1,
        "measure_key": measure["measure_key"],
        "fiscal_event": measure["fiscal_event"],
        "obr_description": measure["obr_description"],
        "source_table": measure["source_table"],
        "year": year,
        "fy": fy_label(year),
        "calendar_year_proxy": f"PE calendar year {year} proxies FY {fy_label(year)}.",
        "engine_version": package_version("policyengine-uk"),
        "policyengine_version": package_version("policyengine"),
        "data_bundle": data_bundle_id(baseline_bundle),
        "policyengine_bundles": {
            "baseline": baseline_bundle,
            "reform": reform_bundle,
        },
        "reform": measure["pe_reform"],
        "construction": measure["construction"],
        "computability": measure["computability"],
        "benchmark_class": "different_model",
        "run_id": run_id,
        "raw_aggregates": {
            "baseline_gbp": baseline["aggregates_gbp"],
            "reform_gbp": reform["aggregates_gbp"],
        },
        "variable_metadata": baseline["variable_metadata"],
        "heads": heads,
        "performance": {
            "baseline": baseline["performance"],
            "reform": reform["performance"],
        },
        "computed_at": computed_at,
        "artifact": relative_to_root(output_path),
        "notes": measure["notes"],
    }


def stage_artifact_rows(
    artifact: dict[str, Any],
    measure: dict[str, Any],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    artifact_heads = {
        artifact_head_identity(head): head for head in artifact["heads"]
    }
    for head in measure["heads"]:
        result = artifact_heads[measure_head_identity(measure, head)]
        claim = result["external_claim"]
        if claim is None:
            continue
        artifact_ref = artifact["artifact"]
        row = {
            "measure_key": measure["measure_key"],
            "obr_description": measure["obr_description"],
            "source_table": result["source_table"],
            "benchmark_class": "different_model",
            "row_kind": "total" if head["condition_key"] is None else "head",
            "engine_version": artifact["engine_version"],
            "data_bundle": artifact["data_bundle"],
            "pe_value": result["pe_value"],
            "status": "constructed",
            "pe_construction": (
                f"{measure['construction']} with plain parameter dictionary; "
                f"raw aggregates in {artifact_ref}"
            ),
            "computed_at": artifact["computed_at"],
            "run_id": artifact["run_id"],
            "artifact": artifact_ref,
            "annotations": annotations_for(measure, head, artifact["year"]),
            "external_claim_match": external_claim_match(claim),
        }
        if row["status"] not in STAGED_STATUSES:
            raise RuntimeError(f"unexpected staged status {row['status']}")
        rows.append(row)
    return rows


def stage_not_computed_rows(
    *,
    measure: dict[str, Any],
    years: list[int],
    claims: list[dict[str, Any]],
    run_id: str,
    computed_at: str,
    release_bundle: dict[str, Any],
) -> list[dict[str, Any]]:
    """Keep explicitly selected null-reform measures visible."""

    rows: list[dict[str, Any]] = []
    for year in years:
        # The harvested scorecard window, not direct-policy start_fy, controls
        # visibility. Pre-effective zero and anticipatory OBR rows are evidence.
        hits = _source_candidates(claims, measure, year)
        for claim in hits:
            condition = claim["conditions"]
            head = (
                condition.get("tax_head") or condition.get("spending_head") or "Total"
            )
            rows.append(
                {
                    "measure_key": measure["measure_key"],
                    "obr_description": measure["obr_description"],
                    "source_table": claim["source_table"],
                    "benchmark_class": "different_model",
                    "row_kind": "total" if head == "Total" else "head",
                    "engine_version": package_version("policyengine-uk"),
                    "data_bundle": data_bundle_id(release_bundle),
                    "pe_value": None,
                    "status": "not_computed",
                    "pe_construction": measure["notes"],
                    "computed_at": computed_at,
                    "run_id": run_id,
                    "annotations": [
                        "No PE value: this registry entry is not expressible as a supported plain parameter reform.",
                        "PE-UK would be static; the OBR published costing is behavioural-adjusted.",
                        (
                            "Registry construction is a certified-world reversal, not the OBR announcement baseline."
                            if measure["construction"] == "reversal_on_certified_world"
                            else "Registry construction would be a forward change from the certified baseline."
                        ),
                        f"PE calendar year {year} would proxy OBR FY {fy_label(year)}.",
                        f"Head mapping unavailable for {head}; no aggregate is substituted.",
                    ],
                    "external_claim_match": external_claim_match(claim),
                }
            )
    return rows


PA_SMOKE_MEASURE = {
    "measure_key": "diagnostic__personal_allowance_plus_500",
    "fiscal_event": "Engine-path diagnostic",
    "obr_description": "Personal allowance £12,570 to £13,070 diagnostic",
    "source_table": "Not an OBR claim",
    "external_metric": "revenue_change",
    "start_fy": 2026,
    "computability": "expressible",
    "construction": "forward_from_baseline",
    "pe_reform": {
        "gov.hmrc.income_tax.allowances.personal_allowance.amount": {
            "2026-01-01.2026-12-31": 13070
        }
    },
    "heads": [
        {
            "obr_head": "Income tax",
            "condition_key": None,
            "pe_variables": ["income_tax"],
            "channel": "tax",
        }
    ],
    "unmapped_obr_heads": [],
    "notes": (
        "Requested smoke diagnostic only: a £500 PA increase in calendar 2026. "
        "It is not staged as an OBR comparison and is not the full Table 3.19 counterfactual."
    ),
}


def restage_existing_run(
    *,
    manifest_path: Path,
    output_dir: Path,
    artifact_root: Path = ROOT,
) -> dict[str, Any]:
    """Restage a manifest inventory using artifacts only; construct no sim."""

    manifest = load_json_object(manifest_path, "run manifest")
    if manifest.get("schema_version") != 1:
        raise ArtifactRestageError(
            f"{manifest_path}: unsupported manifest schema "
            f"{manifest.get('schema_version')!r}"
        )
    run_id = manifest.get("run_id")
    if not isinstance(run_id, str) or not run_id:
        raise ArtifactRestageError(f"{manifest_path}: run_id must be non-empty text")
    references = manifest.get("artifacts")
    if not isinstance(references, list) or not references or not all(
        isinstance(reference, str) and reference for reference in references
    ):
        raise ArtifactRestageError(
            f"{manifest_path}: artifacts must be a non-empty list of paths"
        )
    if len(set(references)) != len(references):
        raise ArtifactRestageError(f"{manifest_path}: duplicate artifact paths")
    resolved_references = [
        resolve_recorded_path(reference, artifact_root).resolve()
        for reference in references
    ]
    if len(set(resolved_references)) != len(resolved_references):
        raise ArtifactRestageError(
            f"{manifest_path}: artifact paths resolve to duplicate files"
        )

    registry_path = resolve_recorded_path(manifest.get("registry"), artifact_root)
    claims_path = resolve_recorded_path(manifest.get("claims"), artifact_root)
    staged_path = resolve_recorded_path(
        manifest.get("staged_output"), artifact_root
    )
    spec = load_registry(registry_path)
    claims = load_claims(claims_path)
    validate_registry(spec, claims=claims)
    registry = {measure["measure_key"]: measure for measure in spec["measures"]}

    replacements: list[tuple[Path, dict[str, Any]]] = []
    staged_rows: list[dict[str, Any]] = []
    regular_measure_keys: set[str] = set()
    diagnostic_artifacts = 0
    for reference in references:
        path = resolve_recorded_path(reference, artifact_root)
        artifact = load_json_object(path, "run artifact")
        self_reference = artifact.get("artifact")
        self_path = resolve_recorded_path(self_reference, artifact_root)
        if self_path.resolve() != path.resolve():
            raise ArtifactRestageError(
                f"{path}: self-reference {self_reference!r} points elsewhere"
            )
        if artifact.get("run_id") != run_id:
            raise ArtifactRestageError(f"{path}: run_id differs from manifest")
        key = artifact.get("measure_key")
        diagnostic_only = artifact.get("diagnostic_only")
        if diagnostic_only is True:
            if key != PA_SMOKE_MEASURE["measure_key"]:
                raise ArtifactRestageError(
                    f"{path}: unsupported diagnostic measure {key!r}"
                )
            measure = PA_SMOKE_MEASURE
            diagnostic_artifacts += 1
        elif diagnostic_only is False:
            if key not in registry:
                raise ArtifactRestageError(
                    f"{path}: measure_key {key!r} is absent from registry"
                )
            measure = registry[key]
            regular_measure_keys.add(key)
        else:
            raise ArtifactRestageError(
                f"{path}: diagnostic_only must be an explicit boolean"
            )
        refreshed = rederive_artifact_orientation(artifact, measure, path=path)
        replacements.append((path, refreshed))
        if not diagnostic_only:
            staged_rows.extend(stage_artifact_rows(refreshed, measure))

    selected = manifest.get("selected_measures")
    if (
        not isinstance(selected, list)
        or not all(isinstance(key, str) for key in selected)
        or len(set(selected)) != len(selected)
        or set(selected) != regular_measure_keys
    ):
        raise ArtifactRestageError(
            f"{manifest_path}: selected measures differ from artifact inventory"
        )
    expected_staged_rows = manifest.get("staged_rows")
    if expected_staged_rows != len(staged_rows):
        raise ArtifactRestageError(
            f"{manifest_path}: artifact-only restage produced {len(staged_rows)} "
            f"rows; manifest records {expected_staged_rows!r}"
        )

    for path, artifact in replacements:
        write_json(path, artifact)
    write_jsonl(staged_path, staged_rows)

    if __package__:
        from pipeline import compare_uk_obr_costings as comparison
    else:
        import compare_uk_obr_costings as comparison

    comparison_rows = comparison.write_comparison_outputs(
        registry_path=registry_path,
        claims_path=claims_path,
        staged_path=staged_path,
        output_dir=output_dir,
        artifact_root=artifact_root,
    )
    return {
        "artifacts": len(replacements),
        "diagnostic_artifacts": diagnostic_artifacts,
        "staged_rows": len(staged_rows),
        "comparison_rows": len(comparison_rows),
        "staged_output": staged_path,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--claims", type=Path, default=DEFAULT_CLAIMS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--staged-output", type=Path, default=DEFAULT_STAGED_OUTPUT)
    parser.add_argument("--measures", nargs="*", help="Exact keys; commas accepted")
    parser.add_argument(
        "--years", nargs="*", help="Calendar proxy years; commas accepted"
    )
    parser.add_argument("--limit", type=int, help="Maximum selected measures")
    parser.add_argument(
        "--dry-run", action="store_true", help="Validate only; construct no sim"
    )
    parser.add_argument(
        "--restage",
        action="store_true",
        help="Rebuild artifacts, staging, and comparison from the run manifest",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        help="Existing run manifest (default: OUTPUT_DIR/RUN_MANIFEST.json)",
    )
    parser.add_argument(
        "--artifact-root",
        type=Path,
        default=ROOT,
        help="Base for paths recorded relative to the repository root",
    )
    parser.add_argument(
        "--no-stage", action="store_true", help="Write artifacts but no JSONL"
    )
    parser.add_argument(
        "--pa-smoke-probe",
        action="store_true",
        help="Also run the non-OBR £12,570→£13,070 2026 diagnostic",
    )
    parser.add_argument("--run-id", default=f"campaign-{RUN_ID_DATE}-obr-costings")
    args = parser.parse_args(argv)

    if args.restage:
        incompatible = [
            flag
            for flag, enabled in (
                ("--measures", args.measures is not None),
                ("--years", args.years is not None),
                ("--limit", args.limit is not None),
                ("--dry-run", args.dry_run),
                ("--no-stage", args.no_stage),
                ("--pa-smoke-probe", args.pa_smoke_probe),
            )
            if enabled
        ]
        if incompatible:
            parser.error(
                "--restage cannot be combined with " + ", ".join(incompatible)
            )
        manifest_path = args.manifest or args.output_dir / "RUN_MANIFEST.json"
        summary = restage_existing_run(
            manifest_path=manifest_path,
            output_dir=args.output_dir,
            artifact_root=args.artifact_root,
        )
        print(
            f"restaged {summary['artifacts']} existing artifacts "
            f"({summary['diagnostic_artifacts']} diagnostic), "
            f"{summary['staged_rows']} staged rows, and "
            f"{summary['comparison_rows']} comparison rows; "
            "managed simulations constructed: 0",
            flush=True,
        )
        return 0

    configure_offline()
    spec = load_registry(args.registry)
    claims = load_claims(args.claims)
    try:
        from policyengine_uk import CountryTaxBenefitSystem
    except ImportError as exc:
        raise SystemExit(f"policyengine-uk is required: {exc}") from exc
    tax_benefit_system = CountryTaxBenefitSystem()
    validation = validate_registry(
        spec, tax_benefit_system=tax_benefit_system, claims=claims
    )
    selected = select_measures(spec["measures"], args.measures, args.limit)
    years = select_years(args.years)
    print(
        json.dumps(
            {
                "validation": validation,
                "selected_measures": [m["measure_key"] for m in selected],
                "years": years,
                "offline": {
                    key: os.environ.get(key)
                    for key in (
                        "HF_HUB_OFFLINE",
                        "TRANSFORMERS_OFFLINE",
                        "HF_DATASETS_OFFLINE",
                    )
                },
            },
            indent=2,
        ),
        flush=True,
    )
    if args.dry_run:
        print("dry-run complete: no managed microsimulation constructed", flush=True)
        return 0

    cache_preflight = preflight_certified_dataset()
    release_bundle = cache_preflight["release_bundle"]
    print(
        "certified cache preflight: "
        f"{data_bundle_id(release_bundle)}; SHA-256 verified in "
        f"{cache_preflight['hash_seconds']:.1f}s",
        flush=True,
    )
    staged_rows: list[dict[str, Any]] = []
    manifest: dict[str, Any] = {
        "schema_version": 1,
        "run_id": args.run_id,
        "started_at": utc_now(),
        "registry": relative_to_root(args.registry),
        "claims": str(args.claims.resolve()),
        "years": years,
        "selected_measures": [m["measure_key"] for m in selected],
        "pa_smoke_probe": args.pa_smoke_probe,
        "certified_cache_preflight": cache_preflight,
        "artifacts": [],
        "baseline_by_year": {},
        "skipped": [],
    }

    for measure in selected:
        if measure["pe_reform"] is None:
            staged_rows.extend(
                stage_not_computed_rows(
                    measure=measure,
                    years=years,
                    claims=claims,
                    run_id=args.run_id,
                    computed_at=utc_now(),
                    release_bundle=release_bundle,
                )
            )

    for year in years:
        active: list[dict[str, Any]] = []
        for measure in selected:
            if measure["pe_reform"] is None:
                continue
            # Reform schedules can start after this year; PE then returns a
            # zero delta. Keep that counterpart when the OBR has a source row.
            mapped_claims = [
                resolve_claim(claims, measure, head, year) for head in measure["heads"]
            ]
            if any(claim is not None for claim in mapped_claims):
                active.append(measure)
            else:
                manifest["skipped"].append(
                    {
                        "measure_key": measure["measure_key"],
                        "year": year,
                        "reason": "outside harvested OBR window",
                    }
                )
        include_probe = args.pa_smoke_probe and year == 2026
        if not active and not include_probe:
            continue
        variables = sorted(
            {
                variable
                for measure in active + ([PA_SMOKE_MEASURE] if include_probe else [])
                for head in measure["heads"]
                for variable in head["pe_variables"]
            }
        )
        print(f"[{year}] baseline: {', '.join(variables)}", flush=True)
        baseline = run_managed_simulation(year=year, variables=variables, reform=None)
        assert_managed_bundle(baseline["policyengine_bundle"], release_bundle)
        manifest["baseline_by_year"][str(year)] = {
            "data_bundle": data_bundle_id(baseline["policyengine_bundle"]),
            "aggregates_gbp": baseline["aggregates_gbp"],
            "performance": baseline["performance"],
        }
        print(
            f"[{year}] baseline done in {baseline['performance']['wall_seconds']:.1f}s; "
            f"peak RSS {baseline['performance']['peak_rss_bytes'] / 2**30:.2f} GiB",
            flush=True,
        )

        work = active + ([PA_SMOKE_MEASURE] if include_probe else [])
        for measure in work:
            measure_variables = sorted(
                {
                    variable
                    for head in measure["heads"]
                    for variable in head["pe_variables"]
                }
            )
            print(f"[{year}] reform {measure['measure_key']}", flush=True)
            reform = run_managed_simulation(
                year=year,
                variables=measure_variables,
                reform=measure["pe_reform"],
            )
            assert_managed_bundle(reform["policyengine_bundle"], release_bundle)
            # The baseline was aggregated over a superset; narrow it only in
            # the artifact so each run records exactly what its values use.
            narrowed_baseline = {
                **baseline,
                "aggregates_gbp": {
                    name: baseline["aggregates_gbp"][name] for name in measure_variables
                },
                "variable_metadata": {
                    name: baseline["variable_metadata"][name]
                    for name in measure_variables
                },
            }
            out_path = artifact_path(args.output_dir, measure["measure_key"], year)
            computed_at = utc_now()
            artifact = build_artifact(
                measure=measure,
                year=year,
                baseline=narrowed_baseline,
                reform=reform,
                output_path=out_path,
                computed_at=computed_at,
                run_id=args.run_id,
                claims=None if measure is PA_SMOKE_MEASURE else claims,
            )
            artifact["diagnostic_only"] = measure is PA_SMOKE_MEASURE
            write_json(out_path, artifact)
            manifest["artifacts"].append(relative_to_root(out_path))
            values = ", ".join(
                f"{head['obr_head']}={head['pe_value'] / 1e9:+.3f}bn"
                for head in artifact["heads"]
            )
            print(
                f"[{year}] {measure['measure_key']} done in "
                f"{reform['performance']['wall_seconds']:.1f}s; "
                f"peak RSS {reform['performance']['peak_rss_bytes'] / 2**30:.2f} GiB; "
                f"{values}",
                flush=True,
            )
            if measure is not PA_SMOKE_MEASURE:
                staged_rows.extend(stage_artifact_rows(artifact, measure))
            del reform, artifact, narrowed_baseline
            gc.collect()
        del baseline
        gc.collect()

    if not args.no_stage:
        write_jsonl(args.staged_output, staged_rows)
        manifest["staged_output"] = relative_to_root(args.staged_output)
        manifest["staged_rows"] = len(staged_rows)
    manifest["completed_at"] = utc_now()
    write_json(args.output_dir / "RUN_MANIFEST.json", manifest)
    print(
        f"wrote {len(manifest['artifacts'])} artifacts"
        + (f" and {len(staged_rows)} staged rows" if not args.no_stage else ""),
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
