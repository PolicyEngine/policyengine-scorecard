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
# A run binds its revisions to the SHA-256 of the file holding them, so a file
# stays frozen once a sealed namespace records it. New revisions go in the next
# file, and every sealed namespace keeps validating.
ENACTED_REVISIONS_PATH = REGISTRY.with_name("construction_revisions_enacted.json")


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


def _registry(measure_key: str) -> tuple[dict | None, str | None]:
    """A measure's revision and the SHA-256 of the file holding it."""
    for path in (REVISIONS_PATH, ENACTED_REVISIONS_PATH):
        payload = path.read_bytes()
        document = json.loads(payload)
        if document.get("schema_version") != 1:
            raise ValueError("unsupported construction revisions schema")
        if measure_key in document["revisions"]:
            digest = hashlib.sha256(payload).hexdigest()
            return document["revisions"][measure_key], digest
    return None, None


def _evidence(revision: dict, digest: str) -> dict:
    """What a run records. ``paths`` are those the executor moves to fiscal years."""
    routed = revision.get("reform_route_paths", revision["condition"].get("all_paths"))
    return {
        "revision_id": revision["revision_id"],
        "registry_sha256": digest,
        "activation_fy": revision["activation_fy"],
        "paths": list(routed),
        "part_year_rule": revision["part_year_rule"],
    }


def _condition_holds(
    condition: dict,
    metadata: Callable[[str], dict],
    current_law: Callable[[str, str], Any] | None,
) -> bool:
    if "values" in condition:
        if current_law is None:
            raise ValueError("this revision selects on current-law values")
        return all(
            scalar(current_law(path, condition["date"])) == value
            for path, value in condition["values"].items()
        )
    expected = condition["equals"]
    found = (
        metadata(path).get(condition["metadata_key"]) for path in condition["all_paths"]
    )
    if isinstance(expected, str):
        return all(value == expected for value in found)
    return all(value is expected for value in found)


def select_revision(
    measure_key: str,
    metadata: Callable[[str], dict],
    current_law: Callable[[str, str], Any] | None = None,
) -> dict | None:
    """Select exactly when the installed engine meets the revision's condition.

    A condition names either a metadata value on every listed parameter or
    the current-law value of every listed parameter at one annual lookup.
    """
    revision, digest = _registry(measure_key)
    if revision is None:
        return None
    if not _condition_holds(revision["condition"], metadata, current_law):
        return None
    return _evidence(revision, digest)


def get_revision(measure_key: str, evidence: dict) -> dict:
    """Validate recorded selection against the exact revision registry bytes."""
    revision, digest = _registry(measure_key)
    expected = None if revision is None else _evidence(revision, digest)
    if evidence != expected:
        raise ValueError(
            f"{measure_key}: construction revision evidence does not match registry"
        )
    return revision


def _reverse_enacted_delta(measure_key: str, world: dict, revision: dict) -> dict:
    """Current law holds a forward delta already: reverse it to prior law.

    The delta's own windows stay, so the effect starts at the same annual
    lookup, and the certified world becomes the reform world.
    """
    prior = revision["prior_law_values"]
    enacted = revision["condition"]["values"]
    delta = world["reform_reform"] or {}
    if (
        world["baseline_reform"]
        or set(delta) != set(prior)
        or set(delta) != set(enacted)
        or any(
            value != enacted[path]
            for path, windows in delta.items()
            for value in windows.values()
        )
    ):
        raise ValueError(f"{measure_key}: frozen delta no longer fits revision")
    return {
        **world,
        "construction": "reversal_on_certified_world",
        "baseline_reform": {
            path: {window: prior[path] for window in windows}
            for path, windows in delta.items()
        },
        "reform_reform": None,
    }


def apply_selected_revision(
    measure_key: str, world: dict, evidence: dict | None
) -> dict:
    """Apply a verified selection, also usable by engine-free downstream tools."""
    if evidence is None:
        return world
    revision = get_revision(measure_key, evidence)
    revised = copy.deepcopy(world)
    if "prior_law_values" in revision:
        revised = _reverse_enacted_delta(measure_key, revised, revision)
    for path, value in revision.get("baseline_values", {}).items():
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
    measure_key: str,
    world: dict,
    metadata: Callable[[str], dict],
    current_law: Callable[[str, str], Any] | None = None,
) -> dict:
    return apply_selected_revision(
        measure_key, world, select_revision(measure_key, metadata, current_law)
    )
