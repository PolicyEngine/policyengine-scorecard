"""Describe how the event replay moved between two certified releases.

Compares two complete replay namespaces (the legacy ``results/uk/events`` or
a variant's ``results/uk/replays/<variant_id>``) after re-verifying each
side's staging, comparison and artifact receipts. Every flag is an
investigation prompt, not a verdict: nothing here passes or fails a model.
The PE/OBR ratio bins are reported unchanged, as transitions.

    PYTHONPATH=. python -m pipeline.diff_uk_event_runs \\
        --base results/uk/events \\
        --head results/uk/replays/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0

Flags (docs/uk_replay/RELEASE_REPLAY.md, "Release differences"):

* numerical: both sides numeric and the move exceeds
  max(£1m, 1% of the larger magnitude);
* structural: a sign reversal or zero crossing, a changed artifact schema or
  construction orientation;
* coverage: a counterpart, artifact or source row on one side only, in a
  year both sides support, or every source row of an event replayed on one
  side only;
* mapping: changed head variables, channels, definitions or registry digest;
* support: a year supported on one side only (never also coverage);
* inertness: an inert in-force construction on one side only;
* construction: changed executed reform dictionaries or premise checks, or
  premise records for a measure on one side only. A changed current-law value
  of a touched parameter is context, not a flag.

Each side is refused before anything is written when its receipts do not
verify, when its events differ from its NAMESPACE_MANIFEST.json (listed but
not loaded, or loaded but not listed), or when its CONSTRUCTION_PREMISES.json
names another engine or another registry than the run.

Invariants: each side uses its receipt-bound registry and staging manifest;
every inventory artifact is revalidated, and the run's identity, support and
grid reconcile with regenerated staging rows and tallies. Identical sides
have no flags. Swapping sides preserves flag sets and mirrors values. Every
source row on either side appears once at source_row level. For an event on
both sides, coverage requires shared year support; an event on one side only
flags every one of its source rows as coverage. Rows incapable of
counterparts never get support flags. Every flagged record belongs to exactly
one measure-year packet, including support records. Input ordering cannot
change output bytes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import shlex
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline import compare_uk_event as compare  # noqa: E402
from pipeline import stage_uk_event as stage  # noqa: E402
from pipeline.compare_uk_obr_costings import atomic_write_bytes  # noqa: E402

NUMERICAL_FLOOR_GBP = 1_000_000.0
NUMERICAL_RELATIVE = 0.01
# Accounting roundoff on national aggregates, not a materiality bound.
ZERO_GBP = 0.5
FLAGS = (
    "numerical",
    "structural",
    "coverage",
    "mapping",
    "support",
    "inertness",
    "construction",
)
PACKET_FLAGS = frozenset(FLAGS)
COMPUTABLE_CLASSES = ("expressible", "partial")
LEVELS = ("source_row", "measure_year", "head")
DIFF_ROOT = ROOT / "results" / "uk" / "replays" / "diffs"
VARIANTS_PATH = ROOT / "data" / "uk" / "replay_variants.json"
URL = re.compile(r"https?://[^\s\"'<>)\]]+")
PACKET_PENDING = "to be completed by the investigating lane"


class DiffError(ValueError):
    """A side cannot be compared: its receipts do not verify."""


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, indent=1, sort_keys=True, allow_nan=False) + "\n"
    ).encode()


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def numerical_threshold(base: float, head: float) -> float:
    return max(NUMERICAL_FLOOR_GBP, NUMERICAL_RELATIVE * max(abs(base), abs(head)))


def numerically_moved(base: float, head: float) -> bool:
    return abs(head - base) > numerical_threshold(base, head)


def is_zero(value: float) -> bool:
    return abs(value) <= ZERO_GBP


def sign_details(base: float, head: float) -> list[dict]:
    if not (math.isfinite(base) and math.isfinite(head)):
        return [{"flag": "structural", "code": "non_finite"}]
    if is_zero(base) != is_zero(head):
        return [{"flag": "structural", "code": "zero_crossing"}]
    if not is_zero(base) and (base > 0) != (head > 0):
        return [{"flag": "structural", "code": "sign_reversal"}]
    return []


def numeric_details(base: float, head: float) -> list[dict]:
    details = sign_details(base, head)
    if numerically_moved(base, head):
        details.append(
            {
                "flag": "numerical",
                "code": "move_above_threshold",
                "threshold_gbp": numerical_threshold(base, head),
            }
        )
    return details


# --- loading one side -----------------------------------------------------------


def _json(path: Path) -> Any:
    return json.loads(path.read_bytes())


def side_identity(manifest: dict) -> dict:
    variant_id = manifest.get("variant_id") or (
        f"pe{manifest['policyengine_version']}_uk{manifest['engine_version']}"
        f"_{manifest['data_bundle']}"
    )
    return {
        "variant_id": variant_id,
        "policyengine_version": manifest["policyengine_version"],
        "policyengine_uk_version": manifest["engine_version"],
        "policyengine_core_version": manifest["policyengine_core_version"],
        "data_bundle": manifest["data_bundle"],
        "certified_dataset_sha256": manifest["certified_dataset_sha256"],
    }


def resolve_root(value: str, *, artifact_root: Path = ROOT) -> Path:
    """A namespace path, or a variant id from data/uk/replay_variants.json."""
    path = Path(value)
    if path.is_dir():
        return path.resolve()
    variants = artifact_root / "data" / "uk" / "replay_variants.json"
    if variants.exists():
        for record in _json(variants)["variants"]:
            if record["variant_id"] == value:
                return (artifact_root / record["result_root"]).resolve()
    raise DiffError(f"{value!r} is neither a replay namespace nor a variant id")


def _revalidate_run(
    event_dir: Path,
    manifest: dict,
    provenance: dict,
    *,
    artifact_root: Path,
    variants_path: Path | None = None,
) -> tuple[dict, dict, dict, Path]:
    """Reconcile unbound run metadata with the receipt-bound staging inputs."""
    registry_path = compare._receipt_path(provenance["registry_path"], artifact_root)
    registry = _json(registry_path)
    registry_years = sorted(registry["calendar_years"])
    if (
        "registry_path" in manifest
        and compare._receipt_path(manifest["registry_path"], artifact_root)
        != registry_path
    ):
        raise DiffError("run manifest registry path differs from verified snapshot")
    if manifest.get("variant_id") is not None:
        data_years = manifest["data_years"]
        if (
            not isinstance(data_years, list)
            or not data_years
            or any(type(year) is not int for year in data_years)
            or data_years != sorted(set(data_years))
        ):
            raise DiffError("run manifest data years must be nonempty and ordered")
        supported, unsupported = stage.compute.variants.supported_years(
            manifest, registry_years
        )
        if (
            manifest["supported_years"] != supported
            or manifest["unsupported_years"] != unsupported
        ):
            raise DiffError("run manifest year support differs from its data years")
    elif manifest.get(
        "supported_years", registry_years
    ) != registry_years or manifest.get("unsupported_years", []):
        raise DiffError("legacy run manifest year support differs from registry")

    # stage_event resolves inventory references against compute.ROOT. Absolute
    # paths let it validate a separate artifact root without changing globals;
    # restore receipt-relative paths before comparing its rows with STAGED.
    inventory = {
        str(compare._receipt_path(relative, artifact_root)): relative
        for relative in manifest["artifacts"]
    }
    if len(inventory) != len(manifest["artifacts"]):
        raise DiffError("run manifest repeats an artifact path")
    staging_manifest = dict(manifest)
    staging_manifest["artifacts"] = {
        absolute: manifest["artifacts"][relative]
        for absolute, relative in inventory.items()
    }
    rows, tally = stage.stage_event(
        registry,
        staging_manifest,
        artifact_dir=event_dir,
        registry_sha256=provenance["registry_sha256"],
        variants_path=variants_path or stage.variants.VARIANTS_PATH,
    )
    pairs = set()
    for absolute in inventory:
        artifact = _json(Path(absolute))
        pairs.add((artifact["measure_key"], artifact["year"]))
    planned = stage.compute.worlds.computable(
        {measure["measure_key"]: measure for measure in registry["measures"]},
        years=registry_years,
    )
    full_pairs = {
        (key, year)
        for key, world in planned.items()
        if "alias_of" not in world
        for year in registry_years
    }
    supported_pairs = {
        pair
        for pair in full_pairs
        if pair[1] in manifest.get("supported_years", registry_years)
    }
    for field, expected in (
        ("artifact_grid", pairs),
        ("full_event_grid", full_pairs),
        ("full_supported_grid", supported_pairs),
    ):
        if field in manifest and manifest[field] != stage.compute.grid_rows(expected):
            raise DiffError(f"run manifest {field} differs from verified grid")
    for field, expected in (
        ("years", sorted({year for _, year in pairs})),
        ("measures", sorted({key for key, _ in pairs})),
        ("full_event_complete", full_pairs <= pairs),
        ("full_supported_grid_complete", supported_pairs <= pairs),
    ):
        if field in manifest and manifest[field] != expected:
            raise DiffError(f"run manifest {field} differs from verified inventory")
    for row in rows:
        if row.get("artifact_path"):
            row["artifact_path"] = inventory[row["artifact_path"]]
    staged_path = compare._receipt_path(provenance["staged_path"], artifact_root)
    if rows != compare.load_jsonl(staged_path):
        raise DiffError("run manifest staging rows differ from verified staging")
    staging_path = compare._receipt_path(
        provenance["staging_manifest_path"], artifact_root
    )
    staging = _json(staging_path)
    if staging.get("variant_id") != manifest.get("variant_id"):
        raise DiffError("run manifest variant differs from verified staging")
    if staging.get("event") != event_dir.name or any(
        staging.get(field) != value for field, value in tally.items()
    ):
        raise DiffError("run manifest staging tally differs from verified staging")
    if staging.get("inert_measure_years", []) != tally.get("inert_measure_years", []):
        raise DiffError("verified staging inertness differs from run artifacts")

    artifacts = {}
    for absolute, relative in sorted(inventory.items()):
        payload = Path(absolute).read_bytes()
        digest = manifest["artifacts"][relative]
        if sha256_bytes(payload) != digest:
            raise DiffError(f"{relative}: artifact bytes differ from RUN_MANIFEST")
        artifact = json.loads(payload)
        compare.validate_artifact(artifact, relative)
        for field in (
            "policyengine_version",
            "engine_version",
            "policyengine_core_version",
            "data_bundle",
        ):
            if artifact.get(field) != manifest[field]:
                raise DiffError(f"{relative}: {field} differs from run manifest")
        for field in ("variant_id", "variant_identity_sha256"):
            if artifact.get(field) != manifest.get(field):
                raise DiffError(f"{relative}: {field} differs from run manifest")
        for field in ("dataset_sha256_before", "dataset_sha256_after"):
            if artifact.get(field) != manifest["certified_dataset_sha256"]:
                raise DiffError(f"{relative}: {field} differs from certified digest")
        artifacts[(artifact["measure_key"], artifact["year"])] = {
            "path": relative,
            "sha256": digest,
            "artifact": artifact,
        }
    return registry, staging, artifacts, staging_path


def _verify_namespace_events(root: Path, events: dict) -> None:
    """A sealed namespace lists its files: every event it lists must load,
    and every event that loads must be listed."""
    manifest_path = root / "NAMESPACE_MANIFEST.json"
    if not manifest_path.exists():
        return
    listed = {
        Path(relative).parts[0]
        for relative in _json(manifest_path).get("files", {})
        if Path(relative).name == "RUN_MANIFEST.json" and len(Path(relative).parts) == 2
    }
    if listed != set(events):
        raise DiffError(
            f"{root}: events on disk {sorted(events)} differ from "
            f"NAMESPACE_MANIFEST.json {sorted(listed)}"
        )


def _verify_premises(premises: dict, identity: dict, events: dict, path: Path):
    """Construction premises must come from this side's engine and the
    registries its events verified against."""
    engine = premises.get("engine") or {}
    if (
        engine.get("policyengine_uk") != identity["policyengine_uk_version"]
        or engine.get("policyengine") != identity["policyengine_version"]
        or engine.get("policyengine_core") != identity["policyengine_core_version"]
    ):
        raise DiffError(f"{path}: premises come from another engine: {engine}")
    for event, record in (premises.get("events") or {}).items():
        if (
            event in events
            and record.get("registry_sha256") != events[event]["registry_sha256"]
        ):
            raise DiffError(
                f"{path}: {event} premises name another registry than the run"
            )


def load_side(
    root: Path, *, artifact_root: Path = ROOT, variants_path: Path | None = None
) -> dict:
    """Every event of a namespace, re-verified through its receipts.

    A variant run's manifest is checked against its record in
    ``variants_path`` (default data/uk/replay_variants.json); a qualification
    run passes its work file, which also holds the candidate's record."""
    root = root.resolve()
    artifact_root = artifact_root.resolve()
    events = {}
    identities = set()
    for event_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        manifest_path = event_dir / "RUN_MANIFEST.json"
        if not manifest_path.exists():
            continue
        event = event_dir.name
        try:
            manifest = _json(manifest_path)
            if manifest.get("event") != event:
                raise DiffError(f"{manifest_path}: event differs from its directory")
            provenance_path = event_dir / "COMPARISON_PROVENANCE.json"
            provenance = _json(provenance_path)
            registry_path = compare._receipt_path(
                provenance["registry_path"], artifact_root
            )
            rows = compare.load_verified_comparison(
                event_dir / "COMPARISON.json",
                artifact_root=artifact_root,
                registry_path=registry_path,
            )
            registry, staging, artifacts, staging_path = _revalidate_run(
                event_dir,
                manifest,
                provenance,
                artifact_root=artifact_root,
                variants_path=variants_path,
            )
            identity = side_identity(manifest)
        except (ValueError, KeyError, TypeError, OSError) as exc:
            raise DiffError(f"{event_dir}: comparison does not verify: {exc}") from exc
        registry_years = sorted(registry["calendar_years"])
        supported = manifest.get("supported_years", registry_years)
        identities.add(json.dumps(identity, sort_keys=True))
        events[event] = {
            "manifest": manifest,
            "rows": {row["source_row_id"]: row for row in rows},
            "artifacts": artifacts,
            "registry": registry,
            "registry_path": provenance["registry_path"],
            "registry_sha256": provenance["registry_sha256"],
            "registry_years": registry_years,
            "supported_years": sorted(supported),
            "inert_pairs": {
                (row["measure_key"], row["year"])
                for row in staging.get("inert_measure_years", [])
            },
            "inputs": {
                "run_manifest_sha256": sha256_bytes(manifest_path.read_bytes()),
                "staging_manifest_sha256": sha256_bytes(staging_path.read_bytes()),
                "comparison_provenance_sha256": sha256_bytes(
                    provenance_path.read_bytes()
                ),
            },
            "grid": staging_grid(manifest, staging),
        }
    if not events:
        raise DiffError(f"{root}: no replayed events")
    if len(identities) != 1:
        raise DiffError(f"{root}: events were produced by different executions")
    identity = json.loads(next(iter(identities)))
    _verify_namespace_events(root, events)
    premises_path = root / "CONSTRUCTION_PREMISES.json"
    premises = _json(premises_path) if premises_path.exists() else None
    if premises is not None:
        _verify_premises(premises, identity, events, premises_path)
    return {
        "root": root,
        "artifact_root": artifact_root,
        "identity": json.loads(identities.pop()),
        "events": events,
        "premises": premises,
        "premises_sha256": sha256_bytes(premises_path.read_bytes())
        if premises is not None
        else None,
    }


def staging_grid(manifest: dict, staging: dict) -> dict | None:
    """An event's grid from a variant run's verified staging tally (stage_uk_event:
    the run's supported years come from its RUN_MANIFEST.json, as staging
    does not record them). None for a legacy-layout run, whose staging has no
    variant grid fields: no gap is ever inferred for it.

    missing_measure_years is the full event grid without an artifact, so it
    includes the unsupported pairs; a supported-grid gap is a missing pair
    that is not unsupported."""
    if staging.get("variant_id") is None:
        return None
    return {
        "supported_years": sorted(manifest["supported_years"]),
        "full_supported_grid_complete": bool(staging["full_supported_grid_complete"]),
        "inert_measure_years": staging.get("inert_measure_years", []),
        "missing_measure_years": staging["missing_measure_years"],
        "unsupported_measure_years": staging["unsupported_measure_years"],
    }


# --- comparing ------------------------------------------------------------------


def _record(event, level, key, measure_key, year, base, head, details, context):
    flags = sorted({detail["flag"] for detail in details}, key=FLAGS.index)
    delta = None if base is None or head is None else head - base
    return {
        "event": event,
        "level": level,
        "key": key,
        "measure_key": measure_key,
        "year": year,
        "base_gbp": base,
        "head_gbp": head,
        "delta_gbp": delta,
        "threshold_gbp": None if delta is None else numerical_threshold(base, head),
        "flags": flags,
        "details": sorted(details, key=lambda d: (FLAGS.index(d["flag"]), d["code"])),
        "context": context,
    }


def _support(event: str, year: int, base: dict | None, head: dict | None) -> list:
    on_base = base is not None and year in base["supported_years"]
    on_head = head is not None and year in head["supported_years"]
    if base is not None and head is not None and on_base != on_head:
        return [
            {
                "flag": "support",
                "code": "supported_on_base_only"
                if on_base
                else "supported_on_head_only",
            }
        ]
    return []


def compare_source_rows(event: str, base: dict | None, head: dict | None) -> list:
    out = []
    ids = set(base["rows"] if base else ()) | set(head["rows"] if head else ())
    # A whole event replayed on one side only: every source row lost (or
    # gained) its counterpart, whatever the years.
    one_sided = (base is None) != (head is None)
    for source_row_id in sorted(ids):
        b = base["rows"].get(source_row_id) if base else None
        h = head["rows"].get(source_row_id) if head else None
        row = b or h
        year = row["year"]
        # Only a row that could carry a counterpart is affected by support;
        # outside-scope and not-expressible rows have none in any year.
        computable = any(
            r is not None and r.get("classification") in COMPUTABLE_CLASSES
            for r in (b, h)
        )
        details = _support(event, year, base, head) if computable else []
        bv = b["pe_value_gbp"] if b else None
        hv = h["pe_value_gbp"] if h else None
        supported_both = all(
            side is not None and year in side["supported_years"]
            for side in (base, head)
        )
        if not details and supported_both:
            if b is None or h is None:
                details.append(
                    {
                        "flag": "coverage",
                        "code": "source_row_on_base_only"
                        if h is None
                        else "source_row_on_head_only",
                    }
                )
            else:
                inert = {
                    side: r.get("status") == "inert_construction"
                    for side, r in (("base", b), ("head", h))
                }
                if inert["base"] != inert["head"]:
                    details.append(
                        {
                            "flag": "inertness",
                            "code": "inert_on_base_only"
                            if inert["base"]
                            else "inert_on_head_only",
                        }
                    )
                elif (bv is None) != (hv is None):
                    details.append(
                        {
                            "flag": "coverage",
                            "code": "counterpart_on_base_only"
                            if hv is None
                            else "counterpart_on_head_only",
                        }
                    )
                if bv is not None and hv is not None:
                    details += numeric_details(bv, hv)
                    if b["head_variables"] != h["head_variables"]:
                        details.append(
                            {
                                "flag": "mapping",
                                "code": "head_variables_changed",
                                "base": b["head_variables"],
                                "head": h["head_variables"],
                            }
                        )
        if one_sided:
            details = [
                {
                    "flag": "coverage",
                    "code": "event_on_base_only"
                    if head is None
                    else "event_on_head_only",
                }
            ]
        out.append(
            _record(
                event,
                "source_row",
                source_row_id,
                row["measure_key"],
                year,
                bv,
                hv,
                details,
                {
                    "fy": row["fy"],
                    "tax_head": row.get("tax_head"),
                    "obr_value_gbp": row["obr_value_gbp"],
                    "status": {
                        "base": b.get("status") if b else None,
                        "head": h.get("status") if h else None,
                    },
                    "ratio_bin": {
                        "base": b.get("ratio_bin") if b else None,
                        "head": h.get("ratio_bin") if h else None,
                    },
                },
            )
        )
    return out


def _premise_details(event, measure_key, year, base_premises, head_premises):
    """Construction flags from premise records; current-law moves are context."""

    def measure(premises):
        return (
            ((premises or {}).get("events", {}).get(event, {}))
            .get("measures", {})
            .get(measure_key)
        )

    b, h = measure(base_premises), measure(head_premises)
    details, context = [], {}
    if b is None and h is None:
        return details, context
    if b is None or h is None:
        # The other side's checks (a failed one included) cannot be compared.
        details.append(
            {
                "flag": "construction",
                "code": "premises_on_base_only"
                if h is None
                else "premises_on_head_only",
            }
        )
        return details, context
    for name in sorted(set(b.get("checks", {})) | set(h.get("checks", {}))):
        before = (b.get("checks", {}).get(name) or {}).get("holds")
        after = (h.get("checks", {}).get(name) or {}).get("holds")
        if before != after:
            details.append(
                {
                    "flag": "construction",
                    "code": "premise_check_changed",
                    "check": name,
                    "base": before,
                    "head": after,
                }
            )
    by = (b.get("years", {}) or {}).get(str(year), {}).get("paths", {})
    hy = (h.get("years", {}) or {}).get(str(year), {}).get("paths", {})
    moved = {}
    for path in sorted(set(by) | set(hy)):
        bp, hp = by.get(path, {}), hy.get(path, {})
        for world in ("baseline_world", "reform_world"):
            # A world that is current law on both sides moved with current
            # law (context below); only an executed override is construction.
            overrides = any(
                side.get(world) != side.get("current_law") for side in (bp, hp)
            )
            if overrides and bp.get(world) != hp.get(world):
                details.append(
                    {
                        "flag": "construction",
                        "code": f"{world}_value_changed",
                        "path": path,
                        "base": bp.get(world),
                        "head": hp.get(world),
                    }
                )
        if bp.get("current_law") != hp.get("current_law"):
            moved[path] = {"base": bp.get("current_law"), "head": hp.get("current_law")}
    if moved:
        context["current_law_changed"] = moved
    return details, context


def compare_artifacts(
    event: str, base: dict | None, head: dict | None, premises
) -> list:
    out = []
    pairs = set(base["artifacts"] if base else ()) | set(
        head["artifacts"] if head else ()
    )
    for measure_key, year in sorted(pairs):
        b = (
            (base["artifacts"].get((measure_key, year)) or {}).get("artifact")
            if base
            else None
        )
        h = (
            (head["artifacts"].get((measure_key, year)) or {}).get("artifact")
            if head
            else None
        )
        details = _support(event, year, base, head)
        context = {}
        bv = b["measure_total_gbp"] if b else None
        hv = h["measure_total_gbp"] if h else None
        head_records = []
        supported_both = all(
            side is not None and year in side["supported_years"]
            for side in (base, head)
        )
        if not details and supported_both:
            if b is None or h is None:
                details.append(
                    {
                        "flag": "coverage",
                        "code": "artifact_on_base_only"
                        if h is None
                        else "artifact_on_head_only",
                    }
                )
            else:
                details += numeric_details(bv, hv)
                if b.get("schema_version") != h.get("schema_version"):
                    details.append(
                        {"flag": "structural", "code": "artifact_schema_changed"}
                    )
                if b["construction"] != h["construction"]:
                    details.append(
                        {
                            "flag": "structural",
                            "code": "construction_orientation_changed",
                            "base": b["construction"],
                            "head": h["construction"],
                        }
                    )
                for field in ("head_channels", "head_definitions"):
                    if b.get(field) != h.get(field):
                        details.append({"flag": "mapping", "code": f"{field}_changed"})
                for world in ("baseline_world", "reform_world"):
                    if b[world].get("reform_dict") != h[world].get("reform_dict"):
                        details.append(
                            {
                                "flag": "construction",
                                "code": f"{world}_reform_dict_changed",
                            }
                        )
                inert = (
                    (measure_key, year) in base["inert_pairs"],
                    (measure_key, year) in head["inert_pairs"],
                )
                if inert[0] != inert[1]:
                    details.append(
                        {
                            "flag": "inertness",
                            "code": "inert_on_base_only"
                            if inert[0]
                            else "inert_on_head_only",
                        }
                    )
                extra, context = _premise_details(
                    event, measure_key, year, premises[0], premises[1]
                )
                details += extra
                for variable in sorted(set(b["head_effects"]) | set(h["head_effects"])):
                    hb = b["head_effects"].get(variable)
                    hh = h["head_effects"].get(variable)
                    variable_details = (
                        numeric_details(hb, hh)
                        if hb is not None and hh is not None
                        else [{"flag": "mapping", "code": "head_on_one_side_only"}]
                    )
                    head_records.append(
                        _record(
                            event,
                            "head",
                            variable,
                            measure_key,
                            year,
                            hb,
                            hh,
                            variable_details,
                            {
                                "channel": {
                                    "base": b["head_channels"].get(variable),
                                    "head": h["head_channels"].get(variable),
                                }
                            },
                        )
                    )
        out.append(
            _record(
                event,
                "measure_year",
                "total",
                measure_key,
                year,
                bv,
                hv,
                details,
                context,
            )
        )
        out += head_records
    return out


def bin_transitions(event_records: list[dict]) -> dict:
    table = defaultdict(lambda: defaultdict(int))
    for record in event_records:
        if record["level"] != "source_row":
            continue
        bins = record["context"]["ratio_bin"]
        if bins["base"] is not None and bins["head"] is not None:
            table[bins["base"]][bins["head"]] += 1
    return {base: dict(sorted(heads.items())) for base, heads in sorted(table.items())}


def flag_counts(records: list[dict]) -> dict:
    return {flag: sum(flag in r["flags"] for r in records) for flag in FLAGS}


def diff_sides(base: dict, head: dict) -> dict:
    records = []
    events = {}
    premises = (base["premises"], head["premises"])
    for event in sorted(set(base["events"]) | set(head["events"])):
        b = base["events"].get(event)
        h = head["events"].get(event)
        event_records = compare_source_rows(event, b, h) + compare_artifacts(
            event, b, h, premises
        )
        registry_changed = bool(
            b and h and b["registry_sha256"] != h["registry_sha256"]
        )
        if registry_changed:
            for record in event_records:
                record["details"].append(
                    {
                        "flag": "mapping",
                        "code": "registry_sha256_changed",
                        "base": b["registry_sha256"],
                        "head": h["registry_sha256"],
                    }
                )
                record["details"].sort(
                    key=lambda detail: (FLAGS.index(detail["flag"]), detail["code"])
                )
                record["flags"] = sorted(
                    set(record["flags"]) | {"mapping"}, key=FLAGS.index
                )
        records += event_records
        events[event] = {
            "present": {"base": b is not None, "head": h is not None},
            "registry_changed": registry_changed,
            "supported_years": {
                "base": b["supported_years"] if b else None,
                "head": h["supported_years"] if h else None,
            },
            "flag_counts": flag_counts(event_records),
            "bin_transitions": bin_transitions(event_records),
        }
    records.sort(
        key=lambda r: (
            r["event"],
            r["measure_key"],
            r["year"],
            LEVELS.index(r["level"]),
            r["key"],
        )
    )
    identity_changes = {
        field: {"base": base["identity"][field], "head": head["identity"][field]}
        for field in sorted(base["identity"])
        if base["identity"][field] != head["identity"][field]
    }

    def side_header(side):
        return {
            "identity": side["identity"],
            "root": str(side["root"].relative_to(ROOT))
            if side["root"].is_relative_to(ROOT)
            else str(side["root"]),
            "inputs": {
                event: data["inputs"] for event, data in sorted(side["events"].items())
            },
            "premises_sha256": side["premises_sha256"],
            # Each event's grid as this side's own verified staging recorded
            # it; the replay receipt carries the base side's as base_events.
            "grids": {
                event: data["grid"]
                for event, data in sorted(side["events"].items())
                if data.get("grid") is not None
            },
        }

    return {
        "schema_version": 1,
        "description": (
            "Movements of the event replay between two certified releases. "
            "Flags are investigation prompts, not verdicts; ratio bins are "
            "descriptive."
        ),
        "base": side_header(base),
        "head": side_header(head),
        "identity_changes": identity_changes,
        "thresholds": {
            "numerical_floor_gbp": NUMERICAL_FLOOR_GBP,
            "numerical_relative": NUMERICAL_RELATIVE,
            "zero_gbp": ZERO_GBP,
        },
        "flag_counts": flag_counts(records),
        "events": events,
        "rows": records,
    }


# --- packets ----------------------------------------------------------------------


def _cited_sources(measure: dict | None) -> list[str]:
    if measure is None:
        return []
    return sorted(set(URL.findall(json.dumps(measure, ensure_ascii=False))))


def _reproduce(side: dict, event: str, measure_key: str, year: int) -> str:
    data = side["events"].get(event)
    if data is None:
        return "# This event is absent from this namespace."
    variant = side["identity"]["variant_id"]
    # Receipt-relative, like every other path in the command: it runs from
    # the repository root on any checkout, and packet bytes do not depend on
    # the machine that rendered them.
    registry = data["registry_path"]
    arguments = [
        "python",
        "pipeline/compute_uk_event.py",
        "--event",
        event,
        "--variant",
        variant,
        "--registry",
        registry,
        "--measures",
        measure_key,
        "--years",
        str(year),
        "--workers",
        "1",
        "--output-dir",
        f".venv-replay-checks/reproductions/{variant}/{event}/{measure_key}_{year}",
    ]
    return "PYTHONPATH=. " + shlex.join(arguments)


def build_packets(diff: dict, base: dict, head: dict) -> dict[str, dict]:
    groups = defaultdict(list)
    for record in diff["rows"]:
        if PACKET_FLAGS & set(record["flags"]):
            groups[(record["event"], record["measure_key"], record["year"])].append(
                record
            )
    packets = {}
    for (event, measure_key, year), records in sorted(groups.items()):
        sides = {"base": base["events"].get(event), "head": head["events"].get(event)}
        measures = {
            side: next(
                (
                    measure
                    for measure in (data or {}).get("registry", {}).get("measures", [])
                    if measure["measure_key"] == measure_key
                ),
                None,
            )
            for side, data in sides.items()
        }
        measure = measures["head"] or measures["base"]
        all_records = [
            r
            for r in diff["rows"]
            if (r["event"], r["measure_key"], r["year"]) == (event, measure_key, year)
        ]
        source_cells = []
        for side, side_measure in measures.items():
            for source in (side_measure or {}).get("source_rows", []):
                if int(source["fy"][:4]) != year:
                    continue
                row = next(
                    (
                        r
                        for r in all_records
                        if r["level"] == "source_row"
                        and r["key"] == source["source_row_id"]
                    ),
                    None,
                )
                source_cells.append(
                    {
                        "side": side,
                        "source_row_id": source["source_row_id"],
                        "source_row_number": source.get("source_row_number"),
                        "source_table": source.get("source_table"),
                        "source_column": source.get("source_column"),
                        "fy": source["fy"],
                        "tax_head": source.get("tax_head"),
                        "obr_value_gbp": source["value_gbp"],
                        "base_gbp": row["base_gbp"] if row else None,
                        "head_gbp": row["head_gbp"] if row else None,
                        "flags": row["flags"] if row else [],
                    }
                )

        def artifact_ref(side):
            entry = (side or {}).get("artifacts", {}).get((measure_key, year))
            if entry is None:
                return None
            artifact = entry["artifact"]
            return {
                "path": entry["path"],
                "sha256": entry["sha256"],
                "construction": artifact["construction"],
                "baseline_reform_dict": artifact["baseline_world"].get("reform_dict"),
                "reform_reform_dict": artifact["reform_world"].get("reform_dict"),
            }

        def premises_for(side_premises):
            measure_premises = (
                ((side_premises or {}).get("events", {}).get(event, {}))
                .get("measures", {})
                .get(measure_key)
            )
            if measure_premises is None:
                return None
            return {
                "checks": measure_premises.get("checks"),
                "year": measure_premises.get("years", {}).get(str(year)),
            }

        name = f"{event}__{measure_key.removeprefix(event + '__')}__{year}"
        packets[name] = {
            "packet_schema": 1,
            "event": event,
            "measure_key": measure_key,
            "title": (measure or {}).get("title"),
            "measures": measures,
            "year": year,
            "fy": f"{year}-{str(year + 1)[-2:]}",
            "flags": sorted({f for r in records for f in r["flags"]}, key=FLAGS.index),
            "identities": {"base": base["identity"], "head": head["identity"]},
            "registry_sha256": {
                side: (data or {}).get("registry_sha256")
                for side, data in sides.items()
            },
            "artifacts": {side: artifact_ref(data) for side, data in sides.items()},
            "records": all_records,
            "source_cells": source_cells,
            "premises": {
                "base": premises_for(base["premises"]),
                "head": premises_for(head["premises"]),
            },
            "reproduce": {
                side: _reproduce(data, event, measure_key, year)
                for side, data in (("base", base), ("head", head))
            },
            "cited_sources": [
                {"side": side, "url": url}
                for side, side_measure in measures.items()
                for url in _cited_sources(side_measure)
            ],
            "minimal_case": {"status": PACKET_PENDING},
            "statutory_evidence": {"status": PACKET_PENDING},
            "filing": (
                "This pipeline files no issues. The coordinating session reviews "
                "the packet and decides whether to file upstream."
            ),
        }
    return packets


# --- rendering ----------------------------------------------------------------------


def _gbp(value: float | None) -> str:
    return "—" if value is None else f"{value / 1e6:,.1f}"


def render_packet_markdown(name: str, packet: dict) -> str:
    lines = [
        f"# Investigation packet: {packet['event']} / {packet['measure_key']} / CY{packet['year']}",
        "",
        packet["filing"],
        "",
        f"* Title: {packet['title']}",
        f"* Flags: {', '.join(packet['flags'])}",
        f"* Base: `{packet['identities']['base']['variant_id']}`",
        f"* Head: `{packet['identities']['head']['variant_id']}`",
        "",
        "## Movements (£m, positive = gain to the Exchequer)",
        "",
        "| Level | Key | Base | Head | Change | Flags | Details |",
        "|---|---|---:|---:|---:|---|---|",
    ]
    for record in packet["records"]:
        detail = "; ".join(
            d["code"]
            + (f" ({d['check']})" if "check" in d else "")
            + (f" {d['path']}" if "path" in d else "")
            for d in record["details"]
        )
        lines.append(
            f"| {record['level']} | {compare._md(record['key'])} | {_gbp(record['base_gbp'])} | "
            f"{_gbp(record['head_gbp'])} | {_gbp(record['delta_gbp'])} | "
            f"{', '.join(record['flags']) or '—'} | {compare._md(detail) or '—'} |"
        )
    lines += [
        "",
        "## OBR source cells",
        "",
        "| Side | Source row | Table / column | FY | Head | OBR £m | Base £m | Head £m |",
        "|---|---|---|---|---|---:|---:|---:|",
    ]
    for cell in packet["source_cells"]:
        lines.append(
            f"| {cell['side']} | {cell['source_row_id']} (row {cell['source_row_number']}) | "
            f"{compare._md(cell['source_table'])} / {compare._md(cell['source_column'])} | "
            f"{cell['fy']} | {compare._md(cell['tax_head'])} | {_gbp(cell['obr_value_gbp'])} | "
            f"{_gbp(cell['base_gbp'])} | {_gbp(cell['head_gbp'])} |"
        )
    lines += ["", "## Executed worlds", ""]
    for side in ("base", "head"):
        ref = packet["artifacts"][side]
        lines.append(
            f"* {side}: "
            + (
                "no artifact"
                if ref is None
                else f"`{ref['path']}` (sha256 `{ref['sha256']}`), {ref['construction']}; "
                f"baseline dict `{json.dumps(ref['baseline_reform_dict'], sort_keys=True)}`; "
                f"reform dict `{json.dumps(ref['reform_reform_dict'], sort_keys=True)}`"
            )
        )
    lines += ["", "## Reproduce", ""]
    for side, command in packet["reproduce"].items():
        lines += [f"{side}:", "", "```bash", command, "```", ""]
    lines += ["## Sources the registry cites", ""]
    lines += [
        f"* {source['side']}: {source['url']}" for source in packet["cited_sources"]
    ] or ["* none recorded"]
    lines += [
        "",
        "## Minimal case",
        "",
        PACKET_PENDING.capitalize() + ".",
        "",
        "## Statutory evidence",
        "",
        PACKET_PENDING.capitalize() + ".",
        "",
    ]
    return "\n".join(lines)


def premises_note(diff: dict) -> str:
    """Which construction premises the construction flags rest on."""
    digests = {side: diff[side]["premises_sha256"] for side in ("base", "head")}
    if not any(digests.values()):
        return (
            "Neither side has construction premises: premise checks were not "
            "compared, and construction flags come from executed reform "
            "dictionaries only."
        )
    if all(digests.values()):
        return (
            f"Construction premises compared: base `{digests['base']}`, "
            f"head `{digests['head']}`."
        )
    present = "base" if digests["base"] else "head"
    return (
        f"Construction premises on the {present} side only "
        f"(`{digests[present]}`): measure-years compared on both sides that "
        f"they cover carry `premises_on_{present}_only` construction flags, and "
        "no premise check was compared."
    )


def render_markdown(diff: dict, packet_names: list[str], max_rows: int) -> str:
    base, head = diff["base"]["identity"], diff["head"]["identity"]
    lines = [
        f"# Release diff: `{base['variant_id']}` → `{head['variant_id']}`",
        "",
        diff["description"],
        "",
        (
            "A numerical flag means the move exceeds max(£1m, 1% of the larger "
            "magnitude). Structural, coverage, mapping, support, inertness and "
            "construction flags are raised regardless of size. A year supported on "
            "one side only is a support flag, not coverage."
        ),
        "",
        "## Executions",
        "",
        "| Field | Base | Head |",
        "|---|---|---|",
    ]
    for field in sorted(base):
        lines.append(f"| {field} | `{base[field]}` | `{head[field]}` |")
    lines += ["", premises_note(diff)]
    lines += [
        "",
        "## Flags by event",
        "",
        "| Event | Supported years (base → head) | " + " | ".join(FLAGS) + " |",
        "|---|---|" + "---:|" * len(FLAGS),
    ]
    for event, data in diff["events"].items():
        years = data["supported_years"]

        def span(values):
            return "absent" if not values else f"{values[0]}–{values[-1]}"

        lines.append(
            f"| {event} | {span(years['base'])} → {span(years['head'])} | "
            + " | ".join(str(data["flag_counts"][flag]) for flag in FLAGS)
            + " |"
        )
    lines.append(
        "| **all** | | "
        + " | ".join(str(diff["flag_counts"][flag]) for flag in FLAGS)
        + " |"
    )
    flagged = [r for r in diff["rows"] if r["flags"] and r["flags"] != ["support"]]
    flagged.sort(
        key=lambda r: (
            -(abs(r["delta_gbp"]) if r["delta_gbp"] is not None else math.inf),
            r["event"],
            r["measure_key"],
            r["year"],
            LEVELS.index(r["level"]),
            r["key"],
        )
    )
    shown = flagged[:max_rows]
    lines += [
        "",
        "## Flagged movements",
        "",
        f"Showing {len(shown)} of {len(flagged)} rows with a flag other than support, "
        "rows without a numerical change first, then by absolute change. £m, "
        "positive = gain to the Exchequer.",
        "",
        "| Event | Measure | CY | Level | Key | Base | Head | Change | Flags |",
        "|---|---|---:|---|---|---:|---:|---:|---|",
    ]
    for r in shown:
        lines.append(
            f"| {r['event']} | {r['measure_key'].removeprefix(r['event'] + '__')} | {r['year']} | "
            f"{r['level']} | {compare._md(r['key'])} | {_gbp(r['base_gbp'])} | {_gbp(r['head_gbp'])} | "
            f"{_gbp(r['delta_gbp'])} | {', '.join(r['flags'])} |"
        )
    support_only = [r for r in diff["rows"] if r["flags"] == ["support"]]
    by_year = defaultdict(int)
    for r in support_only:
        by_year[(r["event"], r["year"], r["level"])] += 1
    lines += [
        "",
        "## Years supported on one side only",
        "",
        "Each has a packet; the population of one release cannot supply the year.",
        "",
        "| Event | CY | Level | Rows |",
        "|---|---:|---|---:|",
    ]
    lines += [
        f"| {event} | {year} | {level} | {count} |"
        for (event, year, level), count in sorted(by_year.items())
    ] or ["| none | | | |"]
    lines += ["", "## PE/OBR ratio-bin transitions (source rows on both sides)", ""]
    for event, data in diff["events"].items():
        lines += [
            f"### {event}",
            "",
            "| Base bin | Head bin | Rows |",
            "|---|---|---:|",
        ]
        lines += [
            f"| {b} | {h} | {n} |"
            for b, heads in data["bin_transitions"].items()
            for h, n in heads.items()
        ] or ["| — | — | 0 |"]
        lines.append("")
    lines += ["## Investigation packets", ""]
    lines += [f"* [{name}](packets/{name}.md)" for name in packet_names] or ["* none"]
    return "\n".join(lines) + "\n"


def render(base: dict, head: dict, *, max_rows: int = 200) -> dict[str, bytes]:
    diff = diff_sides(base, head)
    packets = build_packets(diff, base, head)
    diff["packets"] = sorted(packets)
    files = {
        "DIFF.json": canonical_bytes(diff),
        "DIFF.md": render_markdown(diff, sorted(packets), max_rows).encode(),
    }
    for name, packet in packets.items():
        files[f"packets/{name}.json"] = canonical_bytes(packet)
        files[f"packets/{name}.md"] = render_packet_markdown(name, packet).encode()
    return files


def write(files: dict[str, bytes], output_dir: Path) -> None:
    stale = (
        {p for p in (output_dir / "packets").glob("*") if p.is_file()}
        if (output_dir / "packets").is_dir()
        else set()
    )
    for relative, payload in sorted(files.items()):
        path = output_dir / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        atomic_write_bytes(path, payload)
        stale.discard(path)
    for path in stale:
        path.unlink()


def check(files: dict[str, bytes], output_dir: Path) -> list[str]:
    """Paths whose bytes on disk differ from a fresh render (CI's no-drift gate)."""
    drift = []
    for relative, payload in sorted(files.items()):
        path = output_dir / relative
        if not path.is_file() or path.read_bytes() != payload:
            drift.append(relative)
    packets = output_dir / "packets"
    if packets.is_dir():
        for path in sorted(packets.iterdir()):
            if f"packets/{path.name}" not in files:
                drift.append(f"packets/{path.name}")
    return drift


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--base", required=True, help="namespace path or variant id")
    parser.add_argument("--head", required=True, help="namespace path or variant id")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument(
        "--variants-file",
        type=Path,
        help="variant records the runs' manifests are checked against "
        "(default data/uk/replay_variants.json)",
    )
    parser.add_argument("--max-rows", type=int, default=200)
    parser.add_argument(
        "--check",
        action="store_true",
        help="compare a fresh render with the files on disk",
    )
    args = parser.parse_args(argv)
    variants_path = args.variants_file.resolve() if args.variants_file else None
    base = load_side(resolve_root(args.base), variants_path=variants_path)
    head = load_side(resolve_root(args.head), variants_path=variants_path)
    output_dir = args.output_dir or (
        DIFF_ROOT
        / f"{base['identity']['variant_id']}__{head['identity']['variant_id']}"
    )
    files = render(base, head, max_rows=args.max_rows)
    if args.check:
        drift = check(files, output_dir)
        if drift:
            print("release diff differs from a fresh render:", *drift, sep="\n  ")
            return 1
        print(f"{output_dir}: {len(files)} files match a fresh render")
        return 0
    write(files, output_dir)
    counts = json.loads(files["DIFF.json"])["flag_counts"]
    print(f"wrote {len(files)} files to {output_dir}; flags: {counts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
