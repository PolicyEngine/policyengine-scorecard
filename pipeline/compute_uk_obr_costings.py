#!/usr/bin/env python3
"""Compute static PE-UK counterparts to selected OBR policy costings.

The managed PolicyEngine baseline is the certified world served by
``policyengine.py``. Registry reforms are plain parameter dictionaries. Most
entries reverse a policy already present in that certified world; their staged
``pe_value`` deliberately remains the literal reform-minus-baseline delta, as
required by the lane contract. Artifacts retain both raw aggregates so the
construction can always be re-oriented downstream without rerunning a sim.

No managed microsimulation is constructed by ``--dry-run``. Normal execution
forces Hugging Face offline mode before importing PolicyEngine, so a missing
certified artifact fails instead of downloading a different world.
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


def configure_offline() -> None:
    """Make a cache miss fail rather than trigger a network request."""

    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ["HF_DATASETS_OFFLINE"] = "1"
    os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"


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
    hash_seconds = time.perf_counter() - started
    if actual_sha256 != expected_sha256:
        raise RuntimeError(
            "cached UK artifact SHA-256 differs from the certified release manifest"
        )
    return {
        "release_bundle": bundle,
        "dataset_uri": dataset_uri,
        "cached_file": cached_path.name,
        "sha256": actual_sha256,
        "hash_seconds": hash_seconds,
        "local_files_only": True,
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


def to_exchequer_gain(raw_aggregate_delta: float, channel: str) -> float:
    """Map an aggregate delta to OBR's positive-gain-to-Exchequer sign."""

    if channel == "tax":
        return raw_aggregate_delta
    if channel == "spending":
        return -raw_aggregate_delta
    raise ValueError(f"unknown channel {channel!r}")


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


def annotations_for(
    measure: dict[str, Any],
    head: dict[str, Any],
    year: int,
) -> list[str]:
    variables = " + ".join(head["pe_variables"])
    sign = "+Δtax" if head["channel"] == "tax" else "−Δspending"
    construction = (
        "Certified-world reversal, not the OBR announcement baseline; the staged "
        "delta remains literal reversal-minus-certified-baseline."
        if measure["construction"] == "reversal_on_certified_world"
        else "Forward parameter change from the certified baseline."
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
        pe_value = to_exchequer_gain(raw_delta, head["channel"])
        if not math.isfinite(pe_value):
            raise RuntimeError(
                f"{measure['measure_key']} {year} {head['obr_head']}: "
                "non-finite PE value"
            )
        matched_claim = (
            resolve_claim(claims, measure, head, year) if claims is not None else None
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
        (head["obr_head"], head["condition_key"]): head for head in artifact["heads"]
    }
    for head in measure["heads"]:
        result = artifact_heads[(head["obr_head"], head["condition_key"])]
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
        "--no-stage", action="store_true", help="Write artifacts but no JSONL"
    )
    parser.add_argument(
        "--pa-smoke-probe",
        action="store_true",
        help="Also run the non-OBR £12,570→£13,070 2026 diagnostic",
    )
    parser.add_argument("--run-id", default=f"campaign-{RUN_ID_DATE}-obr-costings")
    args = parser.parse_args(argv)

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
