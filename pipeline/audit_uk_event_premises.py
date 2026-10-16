"""Record whether each frozen event construction's premises hold on an engine.

The five event registries freeze constructions authored against
policyengine-uk 2.89.2. Some rely on that engine's current law or parameter
processing: a forward delta assumes its lever is absent from current law, a
reversal assumes the measure is present, derived counterfactuals were
computed from 2.89.2's parameter values, and the notes assume every
government parameter is sampled at 30 April. A rerun on another engine runs
the same frozen dictionaries against a different current law. This audit
records, per engine, what the intended worlds hold at each annual lookup and
whether each premise still holds, so the release diff can show where the
experiment itself moved. It changes no construction; a failed premise is a
revision candidate (docs/uk_replay/CONSTRUCTION_REVISIONS.md).

Parameter tree only: no dataset, no simulation.

    PYTHONPATH=. python -m pipeline.audit_uk_event_premises --all \\
        --expect-engine 2.125.1 \\
        --output results/uk/replays/<variant_id>/CONSTRUCTION_PREMISES.json
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.metadata
import inspect
import json
import sys
import textwrap
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline import build_uk_event_registry as builder  # noqa: E402
from pipeline import compute_uk_ab2025 as worlds  # noqa: E402
from pipeline import compute_uk_event as compute  # noqa: E402
from pipeline import uk_construction_revisions as revisions  # noqa: E402

EVENTS_DIR = ROOT / "data" / "uk" / "events"
EVENTS = tuple(builder.EVENTS)
CHECKS = (
    "forward_delta_changes_current_law",
    "reversal_differs_from_current_law",
    "authored_construction_reproduces",
    "annual_value_matches_30_april_sample",
)
FORWARD = ("forward_delta_on_certified_world",)
REVERSAL = ("reversal_on_certified_world",)
AUTO_REVISION = object()


# Public historical names remain available to callers; runtime uses the same
# implementation without importing this audit (which itself imports compute).
scalar = revisions.scalar
window_value = revisions.window_value


def converter_metadata_keys(source: str) -> frozenset[str]:
    """Find literal keys actually read from parameter metadata in converter code.

    Docstrings and unrelated string constants do not establish support. Both
    ``param.metadata.get(key)`` (including ``metadata or {}``) and
    ``param.metadata[key]`` count as reads.
    """
    keys = set()
    for node in ast.walk(ast.parse(textwrap.dedent(source))):
        receiver = key = None
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "get"
            and node.args
        ):
            receiver, key = node.func.value, node.args[0]
        elif isinstance(node, ast.Subscript):
            receiver, key = node.value, node.slice
        if (
            isinstance(key, ast.Constant)
            and isinstance(key.value, str)
            and any(
                isinstance(part, ast.Attribute) and part.attr == "metadata"
                for part in ast.walk(receiver)
            )
        ):
            keys.add(key.value)
    return frozenset(keys)


class EngineView:
    """The installed engine's parameters, as the replay sees them.

    ``current_law`` reads the processed tree that simulations use.
    ``raw_30_april`` reads ``parameters.baseline``: the clone each engine's
    ``process_parameters`` adds as a child of the tree before uprating and
    backdating run over the whole tree, and which only the fiscal-year
    conversion of ``.gov`` skips (2.89.2 policyengine_uk/tax_benefit_system.py:
    102-108; 2.125.1:109-115). It is the uprated, backdated value on 30 April
    before fiscal-year conversion. ``annualisation``
    reports whether the engine's ``convert_to_fiscal_year_parameters`` reads
    the ``fiscal_year_blend``/``preserve_calendar_dates`` metadata at all.
    Those reads are in 2.125.1 policyengine_uk/utils/parameters.py:106-108;
    2.89.2's converter samples 30 April at utils/parameters.py:39-45.
    """

    def __init__(self, system=None):
        import policyengine_uk
        from policyengine_uk.utils import parameters as parameter_utils

        self.system = system or policyengine_uk.CountryTaxBenefitSystem()
        source = inspect.getsource(parameter_utils.convert_to_fiscal_year_parameters)
        metadata_keys = converter_metadata_keys(source)
        self.reads_blend = "fiscal_year_blend" in metadata_keys
        self.reads_calendar = "preserve_calendar_dates" in metadata_keys
        self.resolve = builder.engine_resolver(self.system)

    def _node(self, tree, path: str):
        try:
            return worlds._resolve_parameter(tree, path)
        except (AttributeError, IndexError):
            return None

    def current_law(self, path: str, date: str) -> Any:
        node = self._node(self.system.parameters, path)
        return None if node is None else scalar(node(date))

    def raw_30_april(self, path: str, year: int) -> Any:
        node = self._node(self.system.parameters.baseline, path)
        return None if node is None else scalar(node(f"{year}-04-30"))

    def metadata(self, path: str) -> dict:
        node = self._node(self.system.parameters, path)
        return dict(getattr(node, "metadata", None) or {})

    def annualisation(self, path: str) -> dict:
        metadata = self.metadata(path)
        return {
            "fiscal_year_blend": bool(metadata.get("fiscal_year_blend"))
            if self.reads_blend
            else None,
            "preserve_calendar_dates": bool(metadata.get("preserve_calendar_dates"))
            if self.reads_calendar
            else None,
        }


def _check(holds: bool | None, detail: str, **extra) -> dict:
    return {"holds": holds, "detail": detail, **extra}


def authored_differences(event: str, measure: dict, resolve: Callable) -> dict:
    """Re-author the measure's construction with this engine's parameters."""
    try:
        authored = builder.authored_construction(event, measure["title"], resolve)
    except Exception as exc:  # noqa: BLE001 - a construction that cannot be authored here
        return _check(
            None, f"the builder cannot author this construction here: {exc!r}"
        )
    if authored is None:
        return _check(None, "no authored construction for this title")
    differences = {}
    for field in ("pe_baseline_modifier", "pe_reform_delta"):
        frozen, fresh = measure.get(field), authored.get(field)
        if (frozen or None) != (fresh or None):
            differences[field] = {"frozen": frozen, "authored_here": fresh}
    if differences:
        return _check(
            False,
            "re-authoring with this engine's parameters gives other values than the "
            "frozen registry",
            differences=differences,
        )
    return _check(
        True, "re-authoring with this engine's parameters reproduces the registry"
    )


def audit_measure(
    event: str,
    measure: dict,
    world: dict,
    years: list[int],
    engine: EngineView,
    *,
    revision_selection: dict | None | object = AUTO_REVISION,
) -> dict:
    if revision_selection is AUTO_REVISION:
        world = revisions.apply_revision(
            measure["measure_key"],
            world,
            engine.metadata if hasattr(engine, "metadata") else engine.annualisation,
        )
    else:
        if revision_selection is not None:
            selected_here = revisions.select_revision(
                measure["measure_key"],
                engine.metadata
                if hasattr(engine, "metadata")
                else engine.annualisation,
            )
            if selected_here != revision_selection:
                raise ValueError(
                    f"{measure['measure_key']}: recorded construction revision "
                    "does not match installed parameter metadata or revision registry"
                )
        world = revisions.apply_selected_revision(
            measure["measure_key"], world, revision_selection
        )
    baseline = compute.annual_reform(world["baseline_reform"]) or {}
    reform = compute.annual_reform(world["reform_reform"]) or {}
    paths = sorted(set(baseline) | set(reform))
    commences = measure.get("commences_fy")
    first = int(commences[:4]) if commences else years[0]
    ends = measure.get("effect_ends_fy")
    last = int(ends[:4]) if ends else years[-1]
    year_records = {}
    for year in years:
        date = f"{year}-01-01"
        records = {}
        for path in paths:
            current = engine.current_law(path, date)
            records[path] = {
                "current_law": current,
                "baseline_world": revisions.intended_value(
                    baseline, path, year, engine.current_law
                ),
                "reform_world": revisions.intended_value(
                    reform, path, year, engine.current_law
                ),
                "raw_30_april": engine.raw_30_april(path, year),
                **engine.annualisation(path),
            }
        year_records[str(year)] = {"in_force": first <= year <= last, "paths": records}
    in_force = [r for r in year_records.values() if r["in_force"]]
    construction = world["construction"]
    checks = {}
    if construction in FORWARD:
        moved = any(
            p["reform_world"] != p["current_law"]
            for r in in_force
            for p in r["paths"].values()
        )
        checks["forward_delta_changes_current_law"] = _check(
            moved,
            "the forward delta changes current law in an in-force year"
            if moved
            else "the forward delta equals current law in every in-force year: inert",
        )
    else:
        checks["forward_delta_changes_current_law"] = _check(
            None, "not a forward delta"
        )
    if construction in REVERSAL:
        moved = any(
            p["baseline_world"] != p["current_law"]
            for r in in_force
            for p in r["paths"].values()
        )
        checks["reversal_differs_from_current_law"] = _check(
            moved,
            "the reversal differs from current law in an in-force year"
            if moved
            else "the reversal equals current law in every in-force year: inert",
        )
    else:
        checks["reversal_differs_from_current_law"] = _check(None, "not a reversal")
    checks["authored_construction_reproduces"] = authored_differences(
        event, measure, engine.resolve
    )
    # Retain the historical serialized key to preserve legacy receipt bytes.
    # It checks metadata on in-force touched paths, not numeric value equality;
    # equal annual/raw values can still carry either annualisation flag.
    if not engine.reads_blend and not engine.reads_calendar:
        checks["annual_value_matches_30_april_sample"] = _check(
            True, "this engine samples every government parameter at 30 April"
        )
    else:
        other = sorted(
            {
                path
                for r in in_force
                for path, p in r["paths"].items()
                if p["fiscal_year_blend"] or p["preserve_calendar_dates"]
            }
        )
        checks["annual_value_matches_30_april_sample"] = (
            _check(
                False,
                "these paths are annualised another way (day-weighted fiscal-year "
                "blend or statutory calendar dates): " + ", ".join(other),
            )
            if other
            else _check(True, "every touched path is sampled at 30 April")
        )
    result = {"construction": construction, "checks": checks, "years": year_records}
    if world.get("construction_revision"):
        result["construction_revision"] = world["construction_revision"]
    return result


def audit_event(
    event: str,
    registry: dict,
    registry_sha256: str,
    engine: EngineView,
    *,
    revision_selections: dict | None = None,
) -> dict:
    index = {measure["measure_key"]: measure for measure in registry["measures"]}
    years = sorted(registry["calendar_years"])
    planned = worlds.computable(index, years=years)
    if revision_selections is not None:
        unknown = set(revision_selections) - set(planned)
        if unknown:
            raise ValueError(
                f"{event}: recorded revisions name unknown measures: {sorted(unknown)}"
            )
    return {
        "registry_sha256": registry_sha256,
        "measures": {
            key: audit_measure(
                event,
                index[key],
                world,
                years,
                engine,
                revision_selection=(
                    AUTO_REVISION
                    if revision_selections is None
                    else revision_selections.get(key)
                ),
            )
            for key, world in sorted(planned.items())
            if "alias_of" not in world
        },
    }


def audit(
    events: list[str],
    engine: EngineView,
    *,
    events_dir: Path = EVENTS_DIR,
    namespace: Path | None = None,
) -> dict:
    """Audit fresh intent, or the exact constructions a namespace recorded.

    A namespace's event manifests bind which revisions actually ran. A
    historical manifest without that field executed the frozen registry;
    auditing it must not retrospectively select newly authored revisions.
    """
    out = {}
    selected = False
    processed_check = False
    for event in events:
        payload = (events_dir / f"{event}_measures.json").read_bytes()
        # A namespace records execution, including old sparse namespaces
        # whose retained premises have no event manifests beside them.
        # Missing selection evidence means the frozen construction ran.
        selection = {} if namespace is not None else None
        if namespace is not None:
            manifest_path = namespace / event / "RUN_MANIFEST.json"
            if manifest_path.is_file():
                manifest = json.loads(manifest_path.read_bytes())
                selection = manifest.get("construction_revisions", {})
                if not isinstance(selection, dict):
                    raise ValueError(
                        f"{event}: invalid recorded construction revisions"
                    )
                processed_check = processed_check or bool(
                    manifest.get("processed_value_check")
                )
        selected = selected or bool(selection)
        out[event] = audit_event(
            event,
            json.loads(payload),
            hashlib.sha256(payload).hexdigest(),
            engine,
            revision_selections=selection,
        )
    return {
        "schema_version": 1,
        "engine": {
            "policyengine": _version("policyengine"),
            "policyengine_uk": _version("policyengine-uk"),
            "policyengine_core": _version("policyengine-core"),
        },
        "description": (
            "Intended-world values at each annual lookup (1 January), computed "
            "by the shared runtime intended-value rule. Current law is already "
            "fiscal-year processed; construction windows override that annual "
            "value. These are not simulation readbacks: measure-year artifacts "
            "record each world's actual processed values and refuse a mismatch. "
            "Selected metadata-based construction revisions are digest-bound."
            if (namespace is None and (engine.reads_blend or engine.reads_calendar))
            or selected
            or processed_check
            else "Executed-world values at each annual lookup (1 January) and premise "
            "checks for the frozen event constructions on this engine. A failed "
            "check is a construction revision candidate, not a model verdict."
        ),
        "events": out,
    }


def _version(name: str) -> str | None:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, indent=1, sort_keys=True, allow_nan=False) + "\n"
    ).encode()


def namespace_events(root: Path) -> list[str]:
    """The events a namespace's premises cover (uk_replay_variants.namespace_events)."""
    from pipeline import uk_replay_variants as variants

    return variants.namespace_events(root)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--events", nargs="+", choices=EVENTS)
    selection.add_argument("--all", action="store_true")
    selection.add_argument(
        "--namespace",
        type=Path,
        help="cover the events this namespace holds results for (every event if none)",
    )
    parser.add_argument("--expect-engine", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    installed = _version("policyengine-uk")
    if installed != args.expect_engine:
        parser.error(
            f"policyengine-uk {installed} installed; expected {args.expect_engine}"
        )
    payload = canonical_bytes(
        audit(
            list(EVENTS)
            if args.all
            else namespace_events(args.namespace)
            if args.namespace
            else args.events,
            EngineView(),
            namespace=args.namespace,
        )
    )
    if args.check:
        if not args.output.is_file() or args.output.read_bytes() != payload:
            print(f"{args.output} differs from a fresh audit")
            return 1
        print(f"{args.output} matches a fresh audit")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(payload)
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
