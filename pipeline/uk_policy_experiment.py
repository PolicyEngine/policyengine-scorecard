"""Policy experiments: past UK fiscal-event measures on the modern population.

These runs are not replays and not PolicyEngine's costing of any past event
(docs/uk_replay/POLICY_EXPERIMENTS.md). Each experiment expresses one measure
from an event's source-accounting registry as a parameter change on modern
law, runs it on an experiment population, and screens the result against the
OBR's costing for crashes, inert constructions, sign errors and implausible
magnitudes.

    python3 -m pipeline.uk_policy_experiment plan --event autumn_statement_2022
    python -m pipeline.uk_policy_experiment run --event autumn_statement_2022 \\
        --dataset-file PATH --output-dir DIR          # engine; Modal runs this
    python3 -m pipeline.uk_policy_experiment findings --event autumn_statement_2022

``plan`` and ``findings`` are engine-free. ``run`` needs the population's
exact environment and reuses the replay's managed simulation path
(compute_uk_event.run_sim): the dataset's SHA-256 before and after every
simulation, its year set, and every touched parameter read back from the
simulation's own processed tree.
"""

from __future__ import annotations

import argparse
import gc
import json
import math
import os
import re
import sys
import time
import traceback
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC_DIR = ROOT / "data" / "uk" / "experiments"
POPULATIONS_PATH = SPEC_DIR / "populations.json"
DIAGNOSES_PATH = SPEC_DIR / "diagnoses.json"
OBR_BASES_PATH = SPEC_DIR / "obr_head_forecasts.json"
RESULT_ROOT = "results/uk/experiments"
RUNTIME_ROOT = ROOT / ".venv-replay-checks" / "experiments-runtime"
# Where replays live. An experiment never writes under these.
REPLAY_ROOTS = ("results/uk/events", "results/uk/replays")

SPEC_KIND = "uk_modern_population_policy_experiments"
ARTIFACT_KIND = "uk_modern_population_policy_experiment_result"
POPULATIONS_KIND = "uk_experiment_populations"
POPULATION_STATUS = "experiment_population"
LABEL = "modern_population_sensitivity"
LABEL_TEXT = (
    "Policy experiment on the modern population: not a replay or a costing of {event}."
)
# Experiment constructions -> the replay's orientation rule
# (compute_uk_obr_costings.orient_exchequer_effect).
CONSTRUCTIONS = {
    "reversal_on_modern_law": "reversal_on_certified_world",
    "forward_on_modern_law": "forward_from_baseline",
}
MAGNITUDE_CHECKS = ("scaled", "sign_only")
DIAGNOSIS_STATUSES = (
    "expected",
    "construction_corrected",
    "model_bug",
    "data_issue",
    "engine_route",
    "under_investigation",
)
EXPERIMENT_ID = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")
POPULATION_ID = re.compile(r"^exp-[A-Za-z0-9][A-Za-z0-9_.+-]*$")
EVENT = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")
FY = re.compile(r"^(\d{4})-(\d{2})$")

# Classification thresholds, GBP (docs/uk_replay/POLICY_EXPERIMENTS.md).
MOVE_FLOOR = 1e6  # a summed effect below this did not move
SIGN_MIN_OBR = 20e6
SIGN_MIN_PE = 5e6
SIGN_MIN_PE_SHARE = 0.10
MAGNITUDE_MIN_EXPECTED = 100e6
MAGNITUDE_MIN_MAPPED_SHARE = 0.5
OBR_ZERO = 1e6
OBR_ZERO_PE_MOVES = 100e6
BAND_CHECK = 3.0
BAND_INVESTIGATE = 10.0
MIRROR_TOLERANCE = 1e-9  # relative; the worlds are the same simulations

SEVERITY = {
    "crash": "investigate",
    "reform_not_applied": "investigate",
    "construction_noop": "note",
    "sign_mismatch": "investigate",
    "magnitude_outside_10x": "investigate",
    "magnitude_outside_3x": "check",
    "obr_zero_pe_moves": "note",
    "mirror_mismatch": "investigate",
}


class ExperimentError(ValueError):
    """A spec, population or output that breaks the experiment contract."""


def canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(value, indent=1, sort_keys=True, allow_nan=False) + "\n"
    ).encode()


def sha256_bytes(payload: bytes) -> str:
    import hashlib

    return hashlib.sha256(payload).hexdigest()


def fy_label(year: int) -> str:
    return f"{year}-{(year + 1) % 100:02d}"


def fy_start(label: str) -> int:
    match = FY.fullmatch(label) if isinstance(label, str) else None
    if not match or int(match[2]) != (int(match[1]) + 1) % 100:
        raise ExperimentError(f"invalid fiscal-year label: {label!r}")
    return int(match[1])


def label_text(event_name: str) -> str:
    return LABEL_TEXT.format(event=event_name)


# --- paths --------------------------------------------------------------------


def spec_path(event: str) -> Path:
    if not EVENT.fullmatch(event or ""):
        raise ExperimentError("event must be a lowercase underscore-separated slug")
    return SPEC_DIR / f"{event}.json"


def output_root(population_id: str, *, root: Path = ROOT) -> Path:
    if not POPULATION_ID.fullmatch(population_id or ""):
        raise ExperimentError(f"not an experiment population id: {population_id!r}")
    return root / RESULT_ROOT / population_id


def contained_output_dir(
    population_id: str, event: str, requested: Path | None = None, *, root: Path = ROOT
) -> Path:
    """The event's output directory, or a requested one that resolves inside
    results/uk/experiments/<population>/<event>/ or outside the repository
    (a scratch or Modal work directory). Never inside a replay root."""
    canonical = (output_root(population_id, root=root) / event).resolve()
    if not EVENT.fullmatch(event or ""):
        raise ExperimentError("event must be a lowercase underscore-separated slug")
    chosen = (requested or canonical).resolve()
    repository = root.resolve()
    for replay in REPLAY_ROOTS:
        if chosen.is_relative_to((repository / replay).resolve()):
            raise ExperimentError(f"{chosen} is inside the replay root {replay}")
    checks = (repository / ".venv-replay-checks").resolve()
    if (
        chosen.is_relative_to(repository)
        and not chosen.is_relative_to(canonical)
        and not chosen.is_relative_to(checks)
    ):
        raise ExperimentError(
            f"{chosen} is inside the repository but outside {canonical}"
        )
    return chosen


# --- populations -------------------------------------------------------------


def load_populations(path: Path = POPULATIONS_PATH) -> dict:
    document = json.loads(path.read_bytes())
    if document.get("schema_version") != 1 or document.get("kind") != POPULATIONS_KIND:
        raise ExperimentError(f"{path}: not an experiment population document")
    records = document.get("populations")
    if not isinstance(records, list) or not records:
        raise ExperimentError(f"{path}: lists no populations")
    ids = [record.get("population_id") for record in records]
    if len(ids) != len(set(ids)):
        raise ExperimentError(f"{path}: repeats a population_id")
    if document.get("default_population") not in ids:
        raise ExperimentError(f"{path}: default_population is not listed")
    return document


def get_population(
    population_id: str | None = None, *, path: Path = POPULATIONS_PATH
) -> dict:
    document = load_populations(path)
    wanted = population_id or document["default_population"]
    for record in document["populations"]:
        if record["population_id"] == wanted:
            validate_population(record)
            return record
    raise ExperimentError(f"no experiment population {wanted!r}")


def validate_population(record: dict, *, root: Path = ROOT) -> None:
    """Engine-free: the record is an experiment population, never a variant."""
    problems = []

    def need(condition: bool, message: str) -> None:
        if not condition:
            problems.append(message)

    population_id = record.get("population_id", "")
    need(bool(POPULATION_ID.fullmatch(population_id)), "population_id must start exp-")
    need(
        record.get("status") == POPULATION_STATUS, f"status must be {POPULATION_STATUS}"
    )
    need(record.get("label") == LABEL, f"label must be {LABEL}")
    need(
        record.get("result_root") == f"{RESULT_ROOT}/{population_id}",
        f"result_root must be {RESULT_ROOT}/{population_id}",
    )
    identity = record.get("identity") or {}
    dataset = identity.get("dataset") or {}
    bundle = identity.get("release_bundle") or {}
    packages = identity.get("packages") or {}
    need(
        set(packages) == {"policyengine", "policyengine-uk", "policyengine-core"},
        "identity.packages must name the three packages",
    )
    for name, package in sorted(packages.items()):
        need(
            bool(
                re.fullmatch(r"[0-9a-f]{64}", str((package or {}).get("record_sha256")))
            ),
            f"{name}: record_sha256 (probe the population first)",
        )
    for field in ("repo_id", "repo_type", "revision", "path", "sha256", "size_bytes"):
        need(field in dataset, f"identity.dataset.{field}")
    need(
        bundle.get("certified_data_artifact_sha256") == dataset.get("sha256"),
        "the release bundle names another dataset",
    )
    need(
        bundle.get("model_version")
        == (packages.get("policyengine-uk") or {}).get("version"),
        "the release bundle names another model version",
    )
    need(
        bundle.get("policyengine_version")
        == (packages.get("policyengine") or {}).get("version"),
        "the release bundle names another policyengine version",
    )
    need(identity.get("materialization") == "policyengine_data_dir", "materialization")
    years = record.get("data_years")
    need(
        isinstance(years, list)
        and bool(years)
        and all(isinstance(y, int) and not isinstance(y, bool) for y in years)
        and years == list(range(years[0], years[-1] + 1)),
        "data_years must be consecutive calendar years",
    )
    requirements = record.get("requirements") or {}
    requirements_path = root / str(requirements.get("path", ""))
    if not requirements.get("path") or not requirements_path.is_file():
        problems.append("requirements file is missing")
    else:
        need(
            sha256_bytes(requirements_path.read_bytes()) == requirements.get("sha256"),
            "requirements sha256 differs",
        )
        need(
            identity.get("requirements_sha256") == requirements.get("sha256"),
            "the identity binds another requirements file",
        )
    if problems:
        raise ExperimentError(f"{population_id}: " + "; ".join(problems))


def variant_view(record: dict) -> dict:
    """The fields the replay's environment checks read, under the population's
    own id. In memory only: never written, never added to the variant index."""
    return {
        "variant_id": record["population_id"],
        "identity": record["identity"],
        "requirements": record["requirements"],
        "data_years": record["data_years"],
    }


# --- specs ---------------------------------------------------------------------


INVENTORY_PATH = "data/uk/events/inventory.jsonl"


def load_registry(spec: dict, *, root: Path = ROOT) -> tuple[dict, str]:
    """The event's OBR rows: its registry, or for an event with none, its
    rows of the inventory (#158) in the registry's shape."""
    registry = spec["registry"]
    path = root / registry["path"]
    payload = path.read_bytes()
    digest = sha256_bytes(payload)
    if digest != registry["sha256"]:
        raise ExperimentError(
            f"{registry['path']}: sha256 {digest}, the spec binds {registry['sha256']}"
        )
    if registry.get("kind") == "inventory":
        if registry["path"] != INVENTORY_PATH:
            raise ExperimentError(f"an inventory source must be {INVENTORY_PATH}")
        return inventory_registry(payload, spec["event_slug"]), digest
    return json.loads(payload), digest


def inventory_registry(payload: bytes, event: str) -> dict:
    """Group an event's inventory rows (one per measure and head) into
    measures with one source row per head and fiscal year. GBP millions
    become GBP exactly, through the value's decimal string."""
    measures: dict[str, dict] = {}
    name = None
    fys: set[str] = set()
    for line in payload.decode().splitlines():
        row = json.loads(line)
        if row["event_key"] != event:
            continue
        name = row["event"]
        measure = measures.setdefault(
            row["measure_key"],
            {
                "measure_key": row["measure_key"],
                "title": row["measure"],
                "fiscal_event": row["event"],
                "source_rows": [],
            },
        )
        for fy, value in sorted(row["costing_gbp_m"].items()):
            fys.add(fy)
            measure["source_rows"].append(
                {
                    "source_row_id": f"{row['row_id']}:{fy}",
                    "fy": fy,
                    "tax_head": row["head"],
                    "value_gbp_decimal": str(Decimal(repr(value)) * 1_000_000),
                    "inventory_class": row["class"],
                }
            )
    if not measures:
        raise ExperimentError(f"{event}: no rows in the inventory")
    return {
        "event_slug": event,
        "event_name": name,
        "calendar_years": sorted(fy_start(fy) for fy in fys),
        "source": "inventory",
        "measures": list(measures.values()),
    }


def load_spec(event: str, *, root: Path = ROOT) -> dict:
    path = root / spec_path(event).relative_to(ROOT)
    return json.loads(path.read_bytes())


def load_bases(path: Path = OBR_BASES_PATH) -> dict:
    document = json.loads(path.read_bytes())
    if document.get("kind") != "obr_head_forecasts":
        raise ExperimentError(f"{path}: not the OBR head forecasts")
    return document


def measure_heads(measure: dict) -> set[str]:
    return {row["tax_head"] for row in measure["source_rows"]}


def validate_spec(spec: dict, registry: dict, bases: dict) -> None:
    """Engine-free consistency of one event's experiments."""
    from pipeline import compute_uk_event as event_runner

    event = spec.get("event_slug")
    problems = []

    def need(condition: bool, message: str) -> None:
        if not condition:
            problems.append(message)

    need(spec.get("schema_version") == 1, "schema_version must be 1")
    need(spec.get("kind") == SPEC_KIND, f"kind must be {SPEC_KIND}")
    need(spec.get("label") == LABEL, f"label must be {LABEL}")
    need(registry.get("event_slug") == event, "the registry is another event's")
    need(
        spec.get("label_text") == label_text(registry.get("event_name", "")),
        "label_text must be the standard sentence for this event",
    )
    need(
        spec.get("obr_forecast_vintage") in bases["vintages"],
        "obr_forecast_vintage is not a vintage of the forecasts database",
    )
    measures = {m["measure_key"]: m for m in registry["measures"]}
    experiments = spec.get("experiments")
    need(isinstance(experiments, list) and bool(experiments), "no experiments")
    seen = set()
    for experiment in experiments or []:
        eid = experiment.get("experiment_id", "")
        where = f"{eid}: "
        need(bool(EXPERIMENT_ID.fullmatch(eid)), where + "experiment_id")
        need(eid not in seen, where + "repeated experiment_id")
        seen.add(eid)
        measure = measures.get(experiment.get("measure_key"))
        if measure is None:
            problems.append(where + "measure_key is not in the registry")
            continue
        need(
            experiment.get("construction") in CONSTRUCTIONS,
            where + f"construction must be one of {sorted(CONSTRUCTIONS)}",
        )
        reform = experiment.get("reform")
        if not isinstance(reform, dict) or not reform:
            problems.append(where + "reform must be a nonempty dict")
        else:
            try:
                event_runner.annual_reform(reform)
            except (TypeError, ValueError) as exc:
                problems.append(where + str(exc))
        heads = experiment.get("heads") or []
        need(bool(heads), where + "no heads")
        variables: list[str] = []
        mapped: list[str] = []
        source_heads = measure_heads(measure)
        for head in heads:
            need(head.get("channel") in ("tax", "spending"), where + "head channel")
            obr_heads = head.get("obr_heads") or []
            need(bool(obr_heads), where + "a head group maps no OBR head")
            for name in obr_heads:
                need(
                    name in source_heads,
                    where + f"OBR head {name!r} has no source row in this measure",
                )
            mapped += obr_heads
            group = head.get("pe_variables") or []
            need(bool(group), where + "a head group has no variables")
            variables += group
            sheet = head.get("base_sheet")
            need(
                sheet is None or sheet in bases["sheets"],
                where + f"base_sheet {sheet!r} is not a forecasts database sheet",
            )
            need(
                isinstance(head.get("pe_base_comparable", False), bool),
                where + "pe_base_comparable must be a boolean",
            )
            need(
                not head.get("pe_base_comparable") or sheet is not None,
                where + "a comparable base needs a base_sheet",
            )
        need(
            len(variables) == len(set(variables)), where + "a variable is in two heads"
        )
        need(len(mapped) == len(set(mapped)), where + "an OBR head is in two groups")
        check = experiment.get("magnitude_check")
        need(check in MAGNITUDE_CHECKS, where + "magnitude_check")
        need(
            check == "scaled" or bool(experiment.get("magnitude_reason")),
            where + "a sign_only check needs magnitude_reason",
        )
        need(bool(experiment.get("note")), where + "note")
        need(bool(experiment.get("sources")), where + "sources")
        limit = experiment.get("years")
        need(
            limit is None
            or (
                isinstance(limit, list)
                and bool(limit)
                and all(isinstance(y, int) and not isinstance(y, bool) for y in limit)
                and limit == sorted(set(limit))
            ),
            where + "years must be a sorted list of calendar years",
        )
        mirror = experiment.get("mirror_of")
        need(
            mirror is None
            or (
                isinstance(mirror, str)
                and re.fullmatch(r"[a-z0-9_]+:[a-z0-9_]+", mirror) is not None
            ),
            where + "mirror_of must be '<event>:<experiment_id>'",
        )
    if problems:
        raise ExperimentError(f"{event}: " + "; ".join(problems))


def experiment_years(registry: dict, population: dict) -> list[int]:
    """Years both the event's costing window and the population cover."""
    data = set(population["data_years"])
    return sorted(year for year in registry["calendar_years"] if year in data)


def plan(
    spec: dict, registry: dict, population: dict, *, years=None, selected=None
) -> dict:
    available = experiment_years(registry, population)
    chosen = sorted(set(years or available))
    if set(chosen) - set(available):
        raise ExperimentError(
            f"years {sorted(set(chosen) - set(available))} are outside "
            f"{available}, the event window on this population"
        )
    ids = [e["experiment_id"] for e in spec["experiments"]]
    chosen_ids = selected or ids
    if set(chosen_ids) - set(ids):
        raise ExperimentError(
            f"unknown experiments {sorted(set(chosen_ids) - set(ids))}"
        )
    return {
        "kind": "uk_policy_experiment_plan",
        "label": LABEL,
        "is_replay": False,
        "event": spec["event_slug"],
        "population_id": population["population_id"],
        "years": chosen,
        "event_years_outside_population": sorted(
            set(registry["calendar_years"]) - set(population["data_years"])
        ),
        "experiments": [i for i in ids if i in chosen_ids],
        "grid": [
            {"experiment_id": e["experiment_id"], "year": y}
            for e in spec["experiments"]
            if e["experiment_id"] in chosen_ids
            for y in chosen
            if e.get("years") is None or y in e["years"]
        ],
    }


# --- the OBR side ----------------------------------------------------------------


def obr_values(measure: dict, fy: str, mapped_heads: list[str]) -> dict:
    """The registry's rows for one fiscal year, split by whether a head group
    maps them. Decimal throughout: mapped + unmapped = the FY's rows."""
    mapped = Decimal(0)
    unmapped = Decimal(0)
    by_head: dict[str, Decimal] = {}
    for row in measure["source_rows"]:
        if row["fy"] != fy:
            continue
        value = Decimal(row["value_gbp_decimal"])
        by_head[row["tax_head"]] = by_head.get(row["tax_head"], Decimal(0)) + value
        if row["tax_head"] in mapped_heads:
            mapped += value
        else:
            unmapped += value
    return {
        "mapped_gbp": float(mapped),
        "unmapped_gbp": float(unmapped),
        "by_head_gbp": {head: float(value) for head, value in sorted(by_head.items())},
        "mapped_decimal": str(mapped),
        "unmapped_decimal": str(unmapped),
    }


def forecast(bases: dict, sheet: str | None, vintage: str, fy: str) -> float | None:
    if sheet is None:
        return None
    cell = (bases["forecasts"].get(sheet, {}).get(vintage) or {}).get(fy)
    return None if cell is None else cell["value_gbp_bn"] * 1e9


def newest_forecast(
    bases: dict, sheet: str | None, fy: str
) -> tuple[str, float] | None:
    if sheet is None:
        return None
    for vintage in reversed(bases["vintages"]):
        value = forecast(bases, sheet, vintage, fy)
        if value is not None:
            return vintage, value
    return None


def group_scale(
    head: dict, *, pe_base: float | None, bases: dict, vintage: str, fy: str
) -> dict:
    """The factor that carries one head group's OBR costing to the modern
    population (docs/uk_replay/POLICY_EXPERIMENTS.md, Scaling)."""
    sheet = head.get("base_sheet")
    event_base = forecast(bases, sheet, vintage, fy)
    if event_base is None or event_base <= 0:
        return {"basis": "unscaled", "factor": 1.0, "base_sheet": sheet}
    if head.get("pe_base_comparable") and pe_base is not None and pe_base > 0:
        return {
            "basis": "pe_base_over_obr_event_forecast",
            "factor": pe_base / event_base,
            "base_sheet": sheet,
            "obr_event_forecast_gbp": event_base,
            "pe_base_gbp": pe_base,
        }
    newest = newest_forecast(bases, sheet, fy)
    if newest is None:
        return {"basis": "unscaled", "factor": 1.0, "base_sheet": sheet}
    return {
        "basis": "obr_newest_over_obr_event_forecast",
        "factor": newest[1] / event_base,
        "base_sheet": sheet,
        "obr_event_forecast_gbp": event_base,
        "obr_newest_forecast_gbp": newest[1],
        "obr_newest_vintage": newest[0],
    }


# --- artifacts -----------------------------------------------------------------


def orient(raw: float, channel: str, construction: str) -> tuple[float, float]:
    """(literal alternate - modern in Exchequer terms, announced effect)."""
    from pipeline import compute_uk_obr_costings as fiscal

    return fiscal.orient_exchequer_effect(raw, channel, CONSTRUCTIONS[construction])


def head_effects(experiment: dict, modern: dict, alternate: dict) -> dict:
    """Announced-orientation effects per head group and in total."""
    groups = []
    for head in experiment["heads"]:
        raw = sum(alternate[v] - modern[v] for v in head["pe_variables"])
        literal, announced = orient(raw, head["channel"], experiment["construction"])
        if not math.isfinite(announced):
            raise ExperimentError(f"{experiment['experiment_id']}: non-finite effect")
        groups.append(
            {
                "obr_heads": head["obr_heads"],
                "pe_variables": head["pe_variables"],
                "channel": head["channel"],
                "literal_alternate_minus_modern_gbp": literal,
                "effect_gbp": announced,
                "modern_gbp": sum(modern[v] for v in head["pe_variables"]),
                "alternate_gbp": sum(alternate[v] for v in head["pe_variables"]),
            }
        )
    # math.fsum: exact, so the total is the same whatever order the groups take.
    return {"groups": groups, "effect_gbp": math.fsum(g["effect_gbp"] for g in groups)}


def touched_paths(experiment: dict) -> list[str]:
    return sorted(experiment["reform"])


def intended_alternate(experiment: dict, year: int, modern_values: dict) -> dict:
    from pipeline import compute_uk_event as event_runner
    from pipeline import uk_construction_revisions as revisions

    reform = event_runner.annual_reform(experiment["reform"])
    return {
        path: revisions.intended_value(
            reform, path, year, lambda p, d: modern_values[p]
        )
        for path in touched_paths(experiment)
    }


def parameter_record(experiment, year, modern_values, alternate_values) -> dict:
    """Intent against the processed values of both worlds, path by path."""
    from pipeline import compute_uk_event as event_runner

    intended = intended_alternate(experiment, year, modern_values)
    rows = {}
    for path in touched_paths(experiment):
        rows[path] = {
            "modern_processed": modern_values.get(path),
            "alternate_intended": intended[path],
            "alternate_processed": None
            if alternate_values is None
            else alternate_values.get(path),
            "changes_modern_law": not event_runner.processed_values_match(
                intended[path], modern_values.get(path)
            ),
            "reached_simulation": None
            if alternate_values is None
            else event_runner.processed_values_match(
                intended[path], alternate_values.get(path)
            ),
        }
    return rows


def base_artifact(
    spec: dict, registry: dict, population: dict, experiment: dict, year: int
) -> dict:
    return {
        "schema_version": 1,
        "kind": ARTIFACT_KIND,
        "label": LABEL,
        "label_text": spec["label_text"],
        "is_replay": False,
        "event": spec["event_slug"],
        "event_name": registry["event_name"],
        "experiment_id": experiment["experiment_id"],
        "measure_key": experiment["measure_key"],
        "construction": experiment["construction"],
        "reform": experiment["reform"],
        "year": year,
        "fy": fy_label(year),
        "population_id": population["population_id"],
        "dataset_sha256": population["identity"]["dataset"]["sha256"],
        "sign_convention": "positive_gain_to_exchequer",
    }


def build_result(
    spec, registry, population, experiment, year, *, modern, alternate, registry_sha256
) -> dict:
    """Numerical facts only: identical inputs give identical bytes."""
    artifact = base_artifact(spec, registry, population, experiment, year)
    artifact["registry_sha256"] = registry_sha256
    parameters = parameter_record(
        experiment,
        year,
        modern["processed_parameter_values"],
        alternate["processed_parameter_values"] if alternate else None,
    )
    artifact["parameters"] = parameters
    if alternate is None:
        return artifact
    effects = head_effects(
        experiment, modern["aggregates_gbp"], alternate["aggregates_gbp"]
    )
    artifact.update(
        {
            "status": "computed",
            "head_groups": effects["groups"],
            "effect_gbp": effects["effect_gbp"],
            "engine_version": alternate["policyengine_bundle"].get("model_version"),
            "policyengine_version": alternate["policyengine_bundle"].get(
                "policyengine_version"
            ),
            "data_build_id": alternate["policyengine_bundle"].get(
                "certified_data_build_id"
            ),
            "dataset_sha256_before": alternate["dataset_sha256_before"],
            "dataset_sha256_after": alternate["dataset_sha256_after"],
        }
    )
    return artifact


def crash_result(
    spec, registry, population, experiment, year, *, modern, error, registry_sha256
) -> dict:
    """A simulation that raised: the type and the first message line only."""
    artifact = base_artifact(spec, registry, population, experiment, year)
    message = str(error).strip().splitlines()[0] if str(error).strip() else ""
    frames = traceback.extract_tb(error.__traceback__)
    engine_frames = [
        f"{Path(frame.filename).name}:{frame.lineno} {frame.name}"
        for frame in frames
        if "policyengine" in frame.filename
    ]
    artifact.update(
        {
            "registry_sha256": registry_sha256,
            "status": "crashed",
            "error_type": type(error).__name__,
            "error_message": message[:500],
            "error_frames": engine_frames[-6:],
            "parameters": parameter_record(
                experiment, year, modern["processed_parameter_values"], None
            ),
        }
    )
    return artifact


# --- classification ------------------------------------------------------------


def classify(
    artifact: dict,
    *,
    obr: dict,
    scales: list[dict],
    magnitude_check: str,
) -> dict:
    """Pure: an experiment-year's anomaly codes from its artifact, its OBR rows
    and its group scales (one per head group, in the experiment's order)."""
    codes: list[str] = []
    if artifact.get("status") == "crashed":
        return {"codes": ["crash"], "ratio_raw": None, "ratio_scaled": None}
    parameters = artifact["parameters"].values()
    if any(row["reached_simulation"] is False for row in parameters):
        codes.append("reform_not_applied")
    changes = any(row["changes_modern_law"] for row in parameters)
    pe = artifact["effect_gbp"]
    mapped = obr["mapped_gbp"]
    expected = sum(
        group["obr_mapped_gbp"] * scale["factor"]
        for group, scale in zip(obr["groups"], scales)
    )
    ratio_raw = pe / mapped if abs(mapped) >= OBR_ZERO else None
    ratio_scaled = pe / expected if abs(expected) >= OBR_ZERO else None
    out = {
        "ratio_raw": ratio_raw,
        "ratio_scaled": ratio_scaled,
        "expected_gbp": expected,
    }
    if not changes:
        codes.append("construction_noop")
        out["codes"] = codes
        return out
    if abs(pe) < MOVE_FLOOR:
        codes.append("inert")
        out["codes"] = codes
        out["inert_severity"] = (
            "investigate" if abs(mapped) >= SIGN_MIN_OBR else "check"
        )
        return out
    if abs(mapped) < OBR_ZERO:
        if abs(pe) >= OBR_ZERO_PE_MOVES:
            codes.append("obr_zero_pe_moves")
        out["codes"] = codes
        return out
    if (
        abs(mapped) >= SIGN_MIN_OBR
        and pe * mapped < 0
        and abs(pe) >= max(SIGN_MIN_PE, SIGN_MIN_PE_SHARE * abs(mapped))
    ):
        codes.append("sign_mismatch")
    total_abs = abs(obr["mapped_gbp"]) + abs(obr["unmapped_gbp"])
    mapped_share = abs(obr["mapped_gbp"]) / total_abs if total_abs else 0.0
    out["mapped_share"] = mapped_share
    if (
        magnitude_check == "scaled"
        and "sign_mismatch" not in codes
        and abs(expected) >= MAGNITUDE_MIN_EXPECTED
        and mapped_share >= MAGNITUDE_MIN_MAPPED_SHARE
        and ratio_scaled is not None
    ):
        size = abs(ratio_scaled)
        if ratio_scaled < 0:
            pass  # opposite sign below the sign floors: not a magnitude question
        elif size > BAND_INVESTIGATE or size < 1 / BAND_INVESTIGATE:
            codes.append("magnitude_outside_10x")
        elif size > BAND_CHECK or size < 1 / BAND_CHECK:
            codes.append("magnitude_outside_3x")
    out["codes"] = codes
    return out


def severity(code: str, classification: dict) -> str:
    if code == "inert":
        return classification.get("inert_severity", "investigate")
    return SEVERITY[code]


# --- engine runs -----------------------------------------------------------------


def experiment_preflight(population: dict, *, dataset_source: Path | None) -> dict:
    """Mirror compute_uk_event.variant_preflight for an experiment population."""
    from pipeline import compute_uk_ab2025 as worlds
    from pipeline import compute_uk_event as event_runner
    from pipeline import compute_uk_obr_costings as fiscal
    from pipeline import uk_replay_variants as variants

    view = variant_view(population)
    installed = variants.verify_installed(view)
    variants.isolate_certification_environment()
    fiscal.configure_offline()
    worlds.configure_offline()
    runtime_root = (RUNTIME_ROOT / population["population_id"]).resolve()
    dataset = variants.materialize_dataset(view, runtime_root, source=dataset_source)
    os.chdir(runtime_root)
    variants.isolate_bytecode(runtime_root)
    import policyengine as pe

    event_runner.import_engine()
    release_bundle = dict(pe.uk.uk_latest.release_bundle)
    variants.verify_release_bundle(view, release_bundle)
    return event_runner.variant_pre(
        view, release_bundle=release_bundle, dataset=dataset, installed=installed
    )


def read_check(experiments: list[dict], year: int, world: str) -> list[dict]:
    """A parameter readback request for every touched path (values ignored)."""
    return [
        {
            "event": "policy_experiment",
            "measure_key": e["experiment_id"],
            "year": year,
            "world": world,
            "intended_values": {path: None for path in touched_paths(e)},
        }
        for e in experiments
    ]


def run_year(
    spec, registry, population, experiments, year, pre, *, registry_sha256, output_dir
) -> list[dict]:
    """Modern law once, then each experiment's alternate world."""
    from pipeline import compute_uk_event as event_runner

    variables = sorted(
        {v for e in experiments for head in e["heads"] for v in head["pe_variables"]}
    )
    started = time.perf_counter()
    print(f"[{year}] modern law ({len(variables)} variables)", flush=True)
    modern = event_runner.run_sim(
        year,
        variables,
        None,
        {**pre, "parameter_checks": read_check(experiments, year, "modern_law")},
    )
    timings = [
        {"world": "modern_law", "year": year, "seconds": time.perf_counter() - started}
    ]
    written = []
    for experiment in experiments:
        started = time.perf_counter()
        own = sorted({v for head in experiment["heads"] for v in head["pe_variables"]})
        try:
            alternate = event_runner.run_sim(
                year,
                own,
                experiment["reform"],
                {
                    **pre,
                    "parameter_checks": read_check([experiment], year, "alternate"),
                },
            )
        except Exception as error:  # noqa: BLE001 - a crash is a finding
            artifact = crash_result(
                spec,
                registry,
                population,
                experiment,
                year,
                modern=modern,
                error=error,
                registry_sha256=registry_sha256,
            )
            print(
                f"[{year}] {experiment['experiment_id']}: CRASH {artifact['error_type']}",
                flush=True,
            )
        else:
            artifact = build_result(
                spec,
                registry,
                population,
                experiment,
                year,
                modern=modern,
                alternate=alternate,
                registry_sha256=registry_sha256,
            )
            print(
                f"[{year}] {experiment['experiment_id']}: "
                f"{artifact['effect_gbp'] / 1e9:+.3f}bn",
                flush=True,
            )
        alternate = None
        gc.collect()
        path = output_dir / f"{experiment['experiment_id']}_{year}.json"
        path.write_bytes(canonical_bytes(artifact))
        written.append(
            {"path": path.name, "sha256": sha256_bytes(canonical_bytes(artifact))}
        )
        timings.append(
            {
                "experiment_id": experiment["experiment_id"],
                "year": year,
                "seconds": time.perf_counter() - started,
            }
        )
    baseline_record = {
        "kind": "uk_policy_experiment_modern_law",
        "label": LABEL,
        "is_replay": False,
        "event": spec["event_slug"],
        "year": year,
        "population_id": population["population_id"],
        "aggregates_gbp": {v: modern["aggregates_gbp"][v] for v in variables},
        "engine_version": modern["policyengine_bundle"].get("model_version"),
        "data_build_id": modern["policyengine_bundle"].get("certified_data_build_id"),
        "dataset_sha256": modern["dataset_sha256_after"],
    }
    path = output_dir / f"MODERN_LAW_{year}.json"
    path.write_bytes(canonical_bytes(baseline_record))
    written.append(
        {"path": path.name, "sha256": sha256_bytes(canonical_bytes(baseline_record))}
    )
    (output_dir / f"RUN_LOG_{year}.json").write_bytes(
        canonical_bytes({"timings": timings})
    )
    return written


def run(args) -> int:
    from pipeline import compute_uk_ab2025 as worlds
    from pipeline import compute_uk_obr_costings as fiscal

    fiscal.configure_offline()
    worlds.configure_offline()
    population = get_population(args.population)
    spec = load_spec(args.event)
    registry, registry_sha256 = load_registry(spec)
    bases = load_bases()
    validate_spec(spec, registry, bases)
    planned = plan(
        spec, registry, population, years=args.years, selected=args.experiments
    )
    output_dir = contained_output_dir(
        population["population_id"], args.event, args.output_dir
    )
    dataset_file = args.dataset_file.resolve() if args.dataset_file else None
    pre = experiment_preflight(population, dataset_source=dataset_file)
    output_dir.mkdir(parents=True, exist_ok=True)
    chosen = [
        e for e in spec["experiments"] if e["experiment_id"] in planned["experiments"]
    ]
    files = []
    for year in planned["years"]:
        cells = {c["experiment_id"] for c in planned["grid"] if c["year"] == year}
        if not cells:
            continue
        files += run_year(
            spec,
            registry,
            population,
            [e for e in chosen if e["experiment_id"] in cells],
            year,
            pre,
            registry_sha256=registry_sha256,
            output_dir=output_dir,
        )
    manifest = {
        **planned,
        "kind": "uk_policy_experiment_manifest",
        "label_text": spec["label_text"],
        "spec_sha256": sha256_bytes(spec_path(args.event).read_bytes()),
        "registry_sha256": registry_sha256,
        "population_identity": population["identity"],
        "files": sorted(files, key=lambda row: row["path"]),
    }
    (output_dir / "EXPERIMENT_MANIFEST.json").write_bytes(canonical_bytes(manifest))
    print(f"wrote {len(files)} files to {output_dir}", flush=True)
    return 0


# --- findings ----------------------------------------------------------------------


def load_diagnoses(path: Path = DIAGNOSES_PATH) -> list[dict]:
    if not path.exists():
        return []
    document = json.loads(path.read_bytes())
    rows = document.get("diagnoses", [])
    for row in rows:
        if row.get("status") not in DIAGNOSIS_STATUSES:
            raise ExperimentError(f"diagnosis status {row.get('status')!r}")
        if row.get("code") not in (*SEVERITY, "inert"):
            raise ExperimentError(f"diagnosis code {row.get('code')!r}")
    return rows


def diagnosis_for(diagnoses: list[dict], event: str, eid: str, year: int, code: str):
    for row in diagnoses:
        if (
            row.get("event") == event
            and row.get("experiment_id") == eid
            and row.get("code") == code
            and (row.get("years") is None or year in row["years"])
        ):
            return row
    return None


def obr_for(experiment: dict, measure: dict, year: int) -> dict:
    fy = fy_label(year)
    mapped_heads = [h for head in experiment["heads"] for h in head["obr_heads"]]
    values = obr_values(measure, fy, mapped_heads)
    values["groups"] = [
        {
            "obr_heads": head["obr_heads"],
            "obr_mapped_gbp": float(
                sum(
                    (
                        Decimal(row["value_gbp_decimal"])
                        for row in measure["source_rows"]
                        if row["fy"] == fy and row["tax_head"] in head["obr_heads"]
                    ),
                    Decimal(0),
                )
            ),
        }
        for head in experiment["heads"]
    ]
    return values


def evaluate(
    artifact: dict,
    experiment: dict,
    measure: dict,
    bases: dict,
    vintage: str,
    modern: dict | None,
) -> dict:
    """One experiment-year: OBR values, scales, ratios and anomaly codes."""
    year = artifact["year"]
    obr = obr_for(experiment, measure, year)
    scales = []
    for head in experiment["heads"]:
        pe_base = None
        if modern is not None and head.get("pe_base_comparable"):
            sign = 1.0 if head["channel"] == "tax" else -1.0
            pe_base = abs(
                sign * sum(modern["aggregates_gbp"][v] for v in head["pe_variables"])
            )
        scales.append(
            group_scale(
                head, pe_base=pe_base, bases=bases, vintage=vintage, fy=fy_label(year)
            )
        )
    result = classify(
        artifact, obr=obr, scales=scales, magnitude_check=experiment["magnitude_check"]
    )
    return {"obr": obr, "scales": scales, **result}


def findings(
    event: str, population_id: str | None = None, *, root: Path = ROOT
) -> dict:
    """Engine-free: classify a completed run's artifacts and join diagnoses."""
    population = get_population(population_id)
    spec = load_spec(event, root=root)
    registry, registry_sha256 = load_registry(spec, root=root)
    bases = load_bases()
    validate_spec(spec, registry, bases)
    directory = contained_output_dir(population["population_id"], event, root=root)
    manifest = json.loads((directory / "EXPERIMENT_MANIFEST.json").read_bytes())
    if manifest.get("registry_sha256") != registry_sha256:
        raise ExperimentError("the run used another registry")
    for row in manifest["files"]:
        if sha256_bytes((directory / row["path"]).read_bytes()) != row["sha256"]:
            raise ExperimentError(f"{row['path']}: bytes differ from the manifest")
    measures = {m["measure_key"]: m for m in registry["measures"]}
    diagnoses = load_diagnoses()
    experiments = {e["experiment_id"]: e for e in spec["experiments"]}
    rows = []
    for cell in manifest["grid"]:
        eid, year = cell["experiment_id"], cell["year"]
        experiment = experiments[eid]
        artifact = json.loads((directory / f"{eid}_{year}.json").read_bytes())
        modern_path = directory / f"MODERN_LAW_{year}.json"
        modern = json.loads(modern_path.read_bytes()) if modern_path.exists() else None
        evaluated = evaluate(
            artifact,
            experiment,
            measures[experiment["measure_key"]],
            bases,
            spec["obr_forecast_vintage"],
            modern,
        )
        anomalies = []
        for code in evaluated["codes"]:
            found = diagnosis_for(diagnoses, event, eid, year, code)
            anomalies.append(
                {
                    "code": code,
                    "severity": severity(code, evaluated),
                    "diagnosis": found,
                }
            )
        rows.append(
            {
                "experiment_id": eid,
                "measure_key": experiment["measure_key"],
                "title": measures[experiment["measure_key"]]["title"],
                "year": year,
                "fy": fy_label(year),
                "status": artifact.get("status"),
                "effect_gbp": artifact.get("effect_gbp"),
                "error_type": artifact.get("error_type"),
                "error_message": artifact.get("error_message"),
                "obr_mapped_gbp": evaluated["obr"]["mapped_gbp"],
                "obr_unmapped_gbp": evaluated["obr"]["unmapped_gbp"],
                "expected_gbp": evaluated.get("expected_gbp"),
                "ratio_raw": evaluated.get("ratio_raw"),
                "ratio_scaled": evaluated.get("ratio_scaled"),
                "scales": evaluated["scales"],
                "magnitude_check": experiment["magnitude_check"],
                "anomalies": anomalies,
            }
        )
    return {
        "schema_version": 1,
        "kind": "uk_policy_experiment_findings",
        "label": LABEL,
        "label_text": spec["label_text"],
        "is_replay": False,
        "event": event,
        "population_id": population["population_id"],
        "obr_forecast_vintage": spec["obr_forecast_vintage"],
        "registry_sha256": registry_sha256,
        "rows": rows,
    }


def mirror_findings(all_findings: list[dict], specs: dict[str, dict]) -> list[dict]:
    """Experiments declared as mirrors must return exact negatives."""
    effects = {
        (f["event"], row["experiment_id"], row["year"]): row.get("effect_gbp")
        for f in all_findings
        for row in f["rows"]
    }
    out = []
    for event, spec in specs.items():
        for experiment in spec["experiments"]:
            mirror = experiment.get("mirror_of")
            if not mirror:
                continue
            other_event, other_id = mirror.split(":")
            for (e, eid, year), value in effects.items():
                if e != event or eid != experiment["experiment_id"]:
                    continue
                other = effects.get((other_event, other_id, year))
                if value is None or other is None:
                    continue
                scale = max(abs(value), abs(other), 1.0)
                out.append(
                    {
                        "pair": [f"{event}:{eid}", mirror],
                        "year": year,
                        "effects_gbp": [value, other],
                        "agrees": abs(value + other) <= MIRROR_TOLERANCE * scale,
                    }
                )
    return out


def money(value: float | None) -> str:
    if value is None:
        return ""
    return f"{value / 1e9:+,.3f}"


def render_findings(document: dict) -> str:
    lines = [
        f"# Policy experiments: {document['event']}",
        "",
        f"**{document['label_text']}**",
        "",
        (
            f"Population `{document['population_id']}`. OBR costings are the "
            f"registry's source rows; scaling uses the {document['obr_forecast_vintage']} "
            "forecast (docs/uk_replay/POLICY_EXPERIMENTS.md). £bn, positive = gain "
            "to the Exchequer."
        ),
        "",
        "| Experiment | FY | PE | OBR mapped | OBR × scale | Scaled ratio | Anomalies |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for row in document["rows"]:
        anomalies = ", ".join(
            f"{a['code']} ({a['severity']}"
            + (f"; {a['diagnosis']['status']}" if a["diagnosis"] else "; undiagnosed")
            + ")"
            for a in row["anomalies"]
        )
        effect = (
            money(row["effect_gbp"])
            if row["status"] == "computed"
            else f"crash: {row['error_type']}"
        )
        ratio = "" if row["ratio_scaled"] is None else f"{row['ratio_scaled']:.2f}"
        lines.append(
            f"| `{row['experiment_id']}` | {row['fy']} | {effect} | "
            f"{money(row['obr_mapped_gbp'])} | {money(row['expected_gbp'])} | {ratio} | {anomalies} |"
        )
    return "\n".join(lines) + "\n"


def write_findings(event: str, population_id: str | None = None) -> Path:
    document = findings(event, population_id)
    directory = contained_output_dir(document["population_id"], event)
    (directory / "FINDINGS.json").write_bytes(canonical_bytes(document))
    (directory / "FINDINGS.md").write_text(render_findings(document))
    return directory


# --- CLI ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("plan", "run", "findings"):
        command = commands.add_parser(name)
        command.add_argument("--event", required=True)
        command.add_argument("--population")
        if name != "findings":
            command.add_argument("--years", nargs="*", type=int)
            command.add_argument("--experiments", nargs="*")
        if name == "run":
            command.add_argument("--dataset-file", type=Path)
            command.add_argument("--output-dir", type=Path)
    args = parser.parse_args(argv)
    if args.command == "plan":
        population = get_population(args.population)
        spec = load_spec(args.event)
        registry, _ = load_registry(spec)
        validate_spec(spec, registry, load_bases())
        print(
            json.dumps(
                plan(
                    spec,
                    registry,
                    population,
                    years=args.years,
                    selected=args.experiments,
                ),
                indent=1,
            )
        )
        return 0
    if args.command == "run":
        return run(args)
    directory = write_findings(args.event, args.population)
    print(f"wrote {directory / 'FINDINGS.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
