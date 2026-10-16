"""Metadata-selected, digest-bound changes beside the frozen event registries.

The annual dictionaries describe intended period values. An executor using
statutory reprocessing must submit a selected revision's annual windows on
the fiscal-year boundaries instead (6 April to 5 April), then read back the
processed values. Selection never depends on an engine version string.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Callable

from pipeline import compute_uk_ab2025 as worlds

REGISTRY = (
    Path(__file__).resolve().parent.parent
    / "data/uk/events/construction_revisions.json"
)
REVISIONS_PATH = REGISTRY


def scalar(value: Any) -> Any:
    """A JSON scalar, preserving the historical premises serialization."""
    if hasattr(value, "item"):
        value = value.item()
    if isinstance(value, float):
        if math.isnan(value):
            return None
        if math.isinf(value):
            return "inf" if value > 0 else "-inf"
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    return type(value).__name__


def window_value(reform: dict | None, path: str, date: str) -> tuple[bool, Any]:
    """The value an annual reform dictionary intends at a date, if any."""
    found, intended = False, None
    for window, value in ((reform or {}).get(path) or {}).items():
        start, stop = window.split(".")
        if start <= date <= stop:
            # The engine applies dictionary updates in insertion order.
            found, intended = True, scalar(worlds.NO_LIMIT if value is None else value)
    return found, intended


def intended_value(
    reform: dict | None,
    path: str,
    year: int,
    current_law: Callable[[str, str], Any],
) -> Any:
    """One shared intended-world rule for the premises and runtime check.

    ``reform`` is the annual-normalized construction. Its 1 January value
    overrides certified current law for period Y; an uncovered period keeps
    certified current law's already-processed fiscal-year value. This is
    intent, never evidence of what a simulation actually processed.
    """
    date = f"{year}-01-01"
    found, value = window_value(reform, path, date)
    return value if found else scalar(current_law(path, date))


def _registry() -> tuple[dict, str]:
    payload = REVISIONS_PATH.read_bytes()
    document = json.loads(payload)
    if document.get("schema_version") != 1:
        raise ValueError("unsupported construction revisions schema")
    return document["revisions"], hashlib.sha256(payload).hexdigest()


def select_revision(measure_key: str, metadata: Callable[[str], dict]) -> dict | None:
    """Select exactly when every named installed parameter carries the flag."""
    records, digest = _registry()
    revision = records.get(measure_key)
    if revision is None:
        return None
    condition = revision["condition"]
    if not all(
        metadata(path).get(condition["metadata_key"]) is condition["equals"]
        for path in condition["all_paths"]
    ):
        return None
    return {
        "revision_id": revision["revision_id"],
        "registry_sha256": digest,
        "activation_fy": revision["activation_fy"],
        "paths": list(condition["all_paths"]),
        "part_year_rule": revision["part_year_rule"],
    }


def get_revision(measure_key: str, evidence: dict) -> dict:
    """Validate recorded selection against the exact revision registry bytes."""
    records, digest = _registry()
    revision = records.get(measure_key)
    expected = (
        None
        if revision is None
        else {
            "revision_id": revision["revision_id"],
            "registry_sha256": digest,
            "activation_fy": revision["activation_fy"],
            "paths": list(revision["condition"]["all_paths"]),
            "part_year_rule": revision["part_year_rule"],
        }
    )
    if evidence != expected:
        raise ValueError(
            f"{measure_key}: construction revision evidence does not match registry"
        )
    return revision


def apply_selected_revision(
    measure_key: str, world: dict, evidence: dict | None
) -> dict:
    """Apply a verified selection, also usable by engine-free downstream tools."""
    if evidence is None:
        return world
    revision = get_revision(measure_key, evidence)
    revised = copy.deepcopy(world)
    for path, value in revision["baseline_values"].items():
        windows = revised["baseline_reform"][path]
        first = min(windows)
        _, stop = first.split(".")
        if windows[first] != value or stop < revision["baseline_start"]:
            raise ValueError(
                f"{measure_key}: frozen baseline no longer fits revision for {path}"
            )
        del windows[first]
        windows[f"{revision['baseline_start']}.{stop}"] = value
    revised["construction_revision"] = dict(evidence)
    return revised


def apply_revision(
    measure_key: str, world: dict, metadata: Callable[[str], dict]
) -> dict:
    return apply_selected_revision(
        measure_key, world, select_revision(measure_key, metadata)
    )
