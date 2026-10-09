"""Describe one OBR fiscal-event replay and summarize completed replays.

The comparison preserves the registry's source-row universe, including rows
without a counterpart. Signed ratio bins reuse the mode-2 convention. An axis
tag identifies a limitation; it does not quantify an explanation of a gap.
Artifacts, source identity, head sums and reversal orientation are verified
before rendering. No engine import or simulation is needed.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import sys
from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from pipeline.build_uk_event_registry import _sum as source_gbp_sum
from pipeline.compare_uk_obr_costings import atomic_write_bytes, ratio_and_bin

AXES_PATH = ROOT / "data" / "uk" / "obr_divergence_axes.json"
CSV_FIELDS = [
    "event_slug",
    "source_row_id",
    "measure_key",
    "title",
    "classification",
    "measure_type",
    "fy",
    "year",
    "tax_head",
    "source_table",
    "source_column",
    "obr_value_gbp",
    "obr_value_gbp_decimal",
    "pe_value_gbp",
    "gap_gbp",
    "pe_to_obr_ratio",
    "ratio_bin",
    "status",
    "reason",
    "construction_note",
    "missing_legs",
    "head_variables",
    "artifact",
    "artifact_sha256",
    "axes",
    "decomposition_status",
    "valued_components",
    "unsized_axes",
    "residual_gbp",
    "residual_label",
    "explained_share",
    "explained_share_withheld",
    "diagnosis",
]
DEFAULT_AXES = (
    "population_vintage",
    "behavioural_adjustment",
    "baseline_vintage",
    "cy_proxies_fy",
    "head_scope",
)
GRID_FIELDS = (
    "computed_measure_years",
    "full_event_grid_size",
    "full_event_complete",
    "missing_measure_years",
)


class EventComparisonError(ValueError):
    """A source row or artifact cannot support the reported counterpart."""


def _json(path: Path) -> dict:
    result = json.loads(path.read_bytes())
    if not isinstance(result, dict):
        raise EventComparisonError(f"{path}: expected JSON object")
    return result


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    for number, line in enumerate(path.read_text().splitlines(), 1):
        if line.strip():
            row = json.loads(line)
            if not isinstance(row, dict):
                raise EventComparisonError(f"{path}:{number}: expected JSON object")
            rows.append(row)
    return rows


def _finite(value: Any, context: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise EventComparisonError(f"{context}: expected a number")
    if not math.isfinite(value):
        raise EventComparisonError(f"{context}: expected a finite number")
    return float(value)


def _same(left: float, right: float, context: str) -> None:
    # Aggregate subtraction and a sum of independently subtracted heads have
    # normal floating-point roundoff. This bound is accounting, not a model
    # comparison tolerance.
    if not math.isclose(left, right, abs_tol=0.01, rel_tol=1e-12):
        raise EventComparisonError(f"{context}: {left} differs from {right}")


def _decimal(value: Any, context: str) -> Decimal:
    if not isinstance(value, str):
        raise EventComparisonError(
            f"{context}: exact source amount must be a decimal string"
        )
    try:
        result = Decimal(value)
    except InvalidOperation as exc:
        raise EventComparisonError(f"{context}: invalid decimal amount") from exc
    if not result.is_finite():
        raise EventComparisonError(f"{context}: decimal amount must be finite")
    return result


def validate_artifact(artifact: dict, context: str) -> None:
    effects = artifact.get("head_effects")
    if not isinstance(effects, dict) or not effects:
        raise EventComparisonError(f"{context}: missing head_effects")
    values = {k: _finite(v, f"{context}/{k}") for k, v in effects.items()}
    channels = artifact.get("head_channels")
    if not isinstance(channels, dict) or set(channels) != set(effects):
        raise EventComparisonError(f"{context}: missing raw head channels")
    try:
        for variable, effect in values.items():
            if channels[variable] not in ("tax", "spending"):
                raise EventComparisonError(
                    f"{context}/{variable}: invalid fiscal channel"
                )
            before = _finite(artifact["totals"]["baseline"]["heads"][variable], context)
            after = _finite(artifact["totals"]["reform"]["heads"][variable], context)
            expected = (after - before) * (1 if channels[variable] == "tax" else -1)
            _same(effect, expected, f"{context}/{variable}: raw aggregate delta")
    except KeyError as exc:
        raise EventComparisonError(f"{context}: missing raw fiscal aggregates") from exc
    total = _finite(artifact.get("measure_total_gbp"), f"{context}/measure total")
    _same(sum(values.values()), total, f"{context}: head effects sum")
    literal = artifact.get("literal_reform_minus_baseline")
    if not isinstance(literal, dict) or set(literal) != set(effects):
        raise EventComparisonError(f"{context}: missing literal world deltas")
    reversal = artifact.get("construction") == "reversal_on_certified_world"
    for variable, effect in values.items():
        delta = _finite(literal[variable], f"{context}/literal/{variable}")
        _same(
            effect,
            -delta if reversal else delta,
            f"{context}/{variable}: reversal orientation",
        )
    if reversal:
        reversal_delta = artifact.get("literal_reversal_minus_certified_gbp")
        if isinstance(reversal_delta, dict):
            for variable, delta in literal.items():
                _same(
                    _finite(reversal_delta.get(variable), context),
                    delta,
                    f"{context}/{variable}: retained reversal delta",
                )
        elif reversal_delta is not None:
            _same(
                _finite(reversal_delta, context),
                sum(literal.values()),
                f"{context}: retained reversal total",
            )


def _axes(measure: dict, staged: dict) -> list[str]:
    # The event forecast and the certified 2023 calibrated population differ
    # for every row, including rows awaiting computation. The other four are
    # the declared axes of this construction, not claims of sized effects.
    axes = set(DEFAULT_AXES)
    for value in (measure.get("axes", []), staged.get("axes", [])):
        axes.update(value if isinstance(value, list) else value.keys())
    if (
        staged.get(
            "computability", measure.get("classification", measure.get("computability"))
        )
        == "partial"
    ):
        axes.add("construction_scope")
    known = set(_json(AXES_PATH)["_schema"]["axes"])
    if axes - known:
        raise EventComparisonError(
            f"unregistered divergence axes: {sorted(axes - known)}"
        )
    return sorted(axes)


def describe_decomposition(
    gap: float | None, axes: list[str], components: list[dict]
) -> dict:
    """Preserve an evidence-backed decomposition, never infer one from tags.

    Event replay currently leaves vintage and behavioural terms unsized.
    A complete future decomposition must size every relevant axis, state
    provenance, avoid overlapping terms and have no component masking the
    observed gap before an explained share can be quoted.
    """
    valued = []
    names = set()
    for component in components:
        name = component.get("name")
        if not isinstance(name, str) or not name or name in names:
            raise EventComparisonError(
                "valued components require unique nonempty names"
            )
        names.add(name)
        if component.get("axis") not in axes:
            raise EventComparisonError("valued component has an untagged axis")
        if component.get("status") not in ("computed", "sized", "derived"):
            raise EventComparisonError(
                "valued component must be computed, sized or derived"
            )
        if not component.get("provenance"):
            raise EventComparisonError("valued component requires provenance")
        if component["status"] in ("computed", "derived") and not component.get(
            "derivation"
        ):
            raise EventComparisonError("computed/derived component requires derivation")
        if component["status"] == "sized" and component.get("derivation"):
            raise EventComparisonError(
                "a derived component cannot present as a quoted value"
            )
        value = _finite(component.get("value_gbp"), "component")
        valued.append(
            {
                **component,
                "value_gbp": value,
                "direction": (
                    "explains_gap" if gap and value * gap >= 0 else "masks_gap"
                ),
            }
        )
    sized_axes = {c["axis"] for c in valued}
    unsized = sorted(set(axes) - sized_axes)
    residual = None if gap is None else gap - sum(c["value_gbp"] for c in valued)
    masking = any(c["direction"] == "masks_gap" for c in valued)
    names = {c.get("name") for c in valued}
    overlap = any(set(c.get("overlaps", [])) & names for c in valued)
    result = {
        "decomposition_status": "not_available"
        if gap is None
        else "partial"
        if unsized
        else "complete",
        "valued_components": valued,
        "unsized_axes": unsized,
        "residual_gbp": residual,
        "residual_label": "residual_plus_unsized" if unsized else "residual",
        "explained_share": None,
    }
    if gap is None:
        reason = "no computed counterpart"
    elif unsized:
        reason = "unsized axes: " + ", ".join(unsized)
    elif masking:
        reason = "a valued component masks the observed gap"
    elif overlap:
        reason = "valued components overlap"
    elif not gap:
        reason = "zero observed gap"
    else:
        share = 1 - residual / gap
        if 0 <= share <= 1:
            result["explained_share"] = share
            reason = ""
        else:
            reason = "computed share outside [0, 1]"
    result["explained_share_withheld"] = reason
    return result


def build_comparison_rows(
    registry: dict, staged_rows: list[dict], *, artifact_root: Path = ROOT
) -> list[dict]:
    inventory = {}
    for measure in registry["measures"]:
        for source in measure["source_rows"]:
            key = source["source_row_id"]
            if key in inventory:
                raise EventComparisonError(f"duplicate registry source row: {key}")
            inventory[key] = (measure, source)
    staged = {}
    for row in staged_rows:
        key = row["source_row_id"]
        if key in staged:
            raise EventComparisonError(f"duplicate staged source row: {key}")
        staged[key] = row
    if set(staged) != set(inventory):
        raise EventComparisonError(
            f"source-row accounting differs: missing={sorted(set(inventory) - set(staged))}; "
            f"extra={sorted(set(staged) - set(inventory))}"
        )
    artifacts = {}
    out = []
    for key, (measure, source) in inventory.items():
        row = staged[key]
        for field in ("measure_key", "fy", "tax_head"):
            expected = (
                measure["measure_key"] if field == "measure_key" else source.get(field)
            )
            if row.get(field) != expected:
                raise EventComparisonError(
                    f"{key}: staged {field} differs from registry"
                )
        obr = _finite(source["value_gbp"], f"{key}/OBR")
        source_decimal = source.get("value_gbp_decimal", str(source["value_gbp"]))
        exact_source = _decimal(source_decimal, f"{key}/source")
        staged_decimal = row.get("external_value_gbp_decimal")
        if staged_decimal is None and "value_gbp_decimal" not in source:
            staged_decimal = str(row.get("external_value_gbp"))
        if _decimal(staged_decimal, f"{key}/staged") != exact_source:
            raise EventComparisonError(f"{key}: exact source £ accounting differs")
        staged_number = _finite(row.get("external_value_gbp"), f"{key}/staged OBR")
        if staged_number != obr or obr != float(exact_source):
            raise EventComparisonError(
                f"{key}: numerical source amount differs from decimal commitment"
            )
        pe = row.get("pe_value")
        variables = row.get("head_variables", [])
        reference = row.get("artifact_path")
        digest = row.get("artifact_sha256")
        if pe is not None:
            pe = _finite(pe, f"{key}/PE")
            if not reference or not digest:
                raise EventComparisonError(f"{key}: computed row has no artifact hash")
            if Path(reference).is_absolute():
                raise EventComparisonError(f"{key}: artifact path must be relative")
            path = (artifact_root / reference).resolve()
            try:
                path.relative_to(artifact_root.resolve())
            except ValueError as exc:
                raise EventComparisonError(f"{key}: artifact escapes root") from exc
            if reference not in artifacts:
                payload = path.read_bytes()
                if hashlib.sha256(payload).hexdigest() != digest:
                    raise EventComparisonError(f"{key}: artifact SHA-256 differs")
                artifact = json.loads(payload)
                validate_artifact(artifact, reference)
                artifacts[reference] = (artifact, digest)
            artifact, saved_digest = artifacts[reference]
            if digest != saved_digest:
                raise EventComparisonError(f"{key}: conflicting artifact SHA-256")
            year = int(source["fy"][:4])
            if (
                artifact.get("measure_key") != measure["measure_key"]
                or artifact.get("year") != year
            ):
                raise EventComparisonError(f"{key}: artifact measure/year differs")
            if not variables or len(variables) != len(set(variables)):
                raise EventComparisonError(
                    f"{key}: head variables must be nonempty and unique"
                )
            definitions = measure.get("heads", [])
            if source.get("pe_variables"):
                expected_variables = source["pe_variables"]
            elif definitions:
                normalize = lambda v: " ".join(
                    str(v).casefold().replace("_", " ").split()
                )
                matches = [
                    h
                    for h in definitions
                    if normalize(h["obr_head"]) == normalize(source["tax_head"])
                ]
                if len(matches) != 1:
                    raise EventComparisonError(
                        f"{key}: no unique registry head mapping"
                    )
                expected_variables = matches[0].get(
                    "pe_variables", matches[0].get("head_variables")
                )
            else:
                expected_variables = variables
            if variables != expected_variables:
                raise EventComparisonError(
                    f"{key}: staged variables differ from registry head mapping"
                )
            try:
                value = sum(artifact["head_effects"][v] for v in variables)
            except KeyError as exc:
                raise EventComparisonError(f"{key}: unmapped artifact head") from exc
            _same(pe, value, f"{key}: staged counterpart versus artifact heads")
        ratio, bin_name = ratio_and_bin(obr, pe)
        axes = _axes(measure, row)
        gap = None if pe is None else pe - obr
        components = [
            c
            for c in row.get("divergence_components", [])
            if c.get("fy", source["fy"]) == source["fy"]
        ]
        classification = source.get(
            "classification",
            measure.get("classification", measure.get("computability")),
        )
        reason = row.get("reason") or ""
        if not reason and classification == "partial":
            reason = "; ".join(measure.get("missing_legs", []))
        record = {
            "event_slug": registry["event_slug"],
            "source_row_id": key,
            "measure_key": measure["measure_key"],
            "title": measure["title"],
            "classification": classification,
            "measure_type": measure.get(
                "measure_type", measure.get("program", "unspecified")
            ),
            "fy": source["fy"],
            "year": int(source["fy"][:4]),
            "tax_head": source.get("tax_head"),
            "source_table": source.get("source_table"),
            "source_column": source.get("source_column"),
            "obr_value_gbp": obr,
            "obr_value_gbp_decimal": source_decimal,
            "pe_value_gbp": pe,
            "gap_gbp": gap,
            "pe_to_obr_ratio": ratio,
            "ratio_bin": bin_name,
            "status": row.get("status"),
            "reason": reason,
            "construction_note": measure.get("note", ""),
            "missing_legs": measure.get("missing_legs", []),
            "head_variables": variables,
            "artifact": reference,
            "artifact_sha256": digest,
            "axes": axes,
            "diagnosis": row.get("diagnosis", {}),
            **describe_decomposition(gap, axes, components),
        }
        out.append(record)
    return sorted(
        out,
        key=lambda r: (
            r["measure_key"],
            r["fy"],
            str(r["tax_head"]),
            r["source_row_id"],
        ),
    )


def _cell(value: Any) -> Any:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        if isinstance(value, (dict, list))
        else ""
        if value is None
        else value
    )


def render_csv(rows: list[dict]) -> str:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=CSV_FIELDS, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({field: _cell(row.get(field)) for field in CSV_FIELDS})
    return stream.getvalue()


def _md(value: Any) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", " ")


def _billions(value: float | None) -> str:
    return "—" if value is None else f"{value / 1e9:,.3f}"


def profile(rows: list[dict], field: str) -> list[tuple[str, dict[str, int]]]:
    groups = defaultdict(Counter)
    for row in rows:
        groups[str(row.get(field) or "unspecified")][row["ratio_bin"]] += 1
    return [
        (key, dict(sorted(counts.items()))) for key, counts in sorted(groups.items())
    ]


def render_markdown(
    registry: dict, rows: list[dict], replay_grid: dict | None = None
) -> str:
    computed = [r for r in rows if r["pe_value_gbp"] is not None]
    lines = [
        f"# {registry.get('event_name', registry['event_slug'])}: descriptive replay",
        "",
        (
            "Positive GBP means a gain to the Exchequer. PolicyEngine is the pinned "
            "certified 2023 population uprated to calendar year Y, with government "
            "policy parameters annualized from the engine's 30 April snapshot. "
            "These calendar population inputs proxy OBR FY Y–(Y+1). OBR's announcement forecast and behavioural "
            "costings remain distinct from this construction."
        ),
        "",
        (
            f"Every source row remains visible: {len(rows)} rows, {len(computed)} with "
            "computed counterparts. Source rows are counted once; no comparison subtotal "
            "is treated as a separately published OBR claim."
        ),
        "",
    ]
    if replay_grid and not replay_grid.get("full_event_complete"):
        lines += [
            (
                f"Numerical replay grid incomplete: {replay_grid.get('computed_measure_years', 0)} "
                f"of {replay_grid.get('full_event_grid_size', 'unspecified')} executable "
                "measure-year pairs have artifacts. Rows without counterparts remain visible; "
                "this report does not establish a completed event replay."
            ),
            "",
        ]
    lines += [
        "## Accounting",
        "",
        "| Classification | Measures | Source rows | Net OBR £bn | Absolute OBR £bn |",
        "|---|---:|---:|---:|---:|",
    ]
    for classification in (
        "expressible",
        "partial",
        "not_expressible",
        "out_of_household_scope",
    ):
        selected = [r for r in rows if r["classification"] == classification]
        account = registry.get("accounting", {}).get("by_class", {}).get(classification)
        measure_count = (
            account["measures"]
            if account
            else sum(
                measure.get("classification", measure.get("computability"))
                == classification
                for measure in registry["measures"]
            )
        )
        exact_values = [
            {"value_gbp_decimal": row["obr_value_gbp_decimal"]} for row in selected
        ]
        lines.append(
            f"| {classification} | {measure_count} | {len(selected)} | "
            f"{Decimal(source_gbp_sum(exact_values)) / Decimal(10**9):,.3f} | "
            f"{Decimal(source_gbp_sum(exact_values, absolute=True)) / Decimal(10**9):,.3f} |"
        )
    lines += [
        "",
        (
            "Net and absolute £ sum source-row values across the costing years; "
            "they are accounting amounts, not a single-year event total. Measure counts "
            "use each measure's registry class; source-row classes may differ for non-household heads."
        ),
        "",
        "## Agreement profile",
        "",
        "The bins describe PE/OBR on each source head and year. They do not define a quality gate.",
        "",
    ]
    for field, label in (
        (("tax_head", "Tax head"), ("measure_type", "Measure type")) if computed else ()
    ):
        lines += [f"| {label} | Source-row ratio bins |", "|---|---|"]
        lines += [
            f"| {_md(key)} | {_md(', '.join(f'{k}: {v}' for k, v in counts.items()))} |"
            for key, counts in profile(rows, field)
        ]
        lines.append("")
    gap_mass = sum(abs(r["gap_gbp"]) for r in computed)
    explained = [r for r in computed if r["explained_share"] is not None]
    lines += [
        "## Divergence axes and explained share",
        "",
        (
            "Every row tags population_vintage: OBR used the forecast at its fiscal "
            "event, whereas this bundle uses one 2023 population calibrated to later "
            "targets. The other declared axes are behavioural_adjustment (static versus "
            "behavioural), baseline_vintage (certified versus announcement baseline), "
            "cy_proxies_fy and head_scope. Partial constructions also tag construction_scope."
        ),
        "",
        (
            "The replay retains pinned incidence rules: employer_ni.employee_incidence=1 "
            "changes wages holding employer cost fixed, so its Income Tax effect is not "
            "a fixed-wage static costing. The OBR database reports direct measure effects "
            "and excludes separately reported indirect macroeconomic effects. Scope and "
            "incidence therefore require head_scope/construction_scope notes; neither "
            "a raw head gap nor the static label sizes a behavioural explanation."
        ),
        "",
        (
            f"Tagged coverage: {len(computed)} computed rows and "
            f"£{gap_mass / 1e9:,.3f}bn of absolute raw gap have named axes. "
            "Tagged coverage does not size their effects."
        ),
        "",
        (
            f"Explained share: available on {len(explained)} computed rows. "
            "For other rows it is withheld because relevant axes remain unsized. "
            "A tagged limitation cannot claim a percentage of the gap. Residuals are "
            "therefore labelled residual_plus_unsized, not model error."
        ),
        "",
        "## Source rows",
        "",
        "| Measure | FY | Head | Class | OBR £bn | PE £bn | PE/OBR | Bin | Status / reason |",
        "|---|---|---|---|---:|---:|---:|---|---|",
    ]
    for row in rows:
        ratio = (
            "—" if row["pe_to_obr_ratio"] is None else f"{row['pe_to_obr_ratio']:.3f}"
        )
        lines.append(
            "| "
            + " | ".join(
                [
                    _md(row["title"]),
                    row["fy"],
                    _md(row["tax_head"]),
                    row["classification"],
                    _billions(row["obr_value_gbp"]),
                    _billions(row["pe_value_gbp"]),
                    ratio,
                    row["ratio_bin"],
                    _md(f"{row['status']}: {row['reason']}"),
                ]
            )
            + " |"
        )
    caveats = [
        measure
        for measure in registry["measures"]
        if measure.get("note")
        and measure.get("classification", measure.get("computability"))
        in ("expressible", "partial")
    ]
    if caveats:
        lines += ["", "## Construction caveats", ""]
        for measure in caveats:
            lines.append(f"* `{measure['measure_key']}`: {measure['note']}")
    return "\n".join(lines) + "\n"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _relative_receipt(path: Path, artifact_root: Path) -> str:
    try:
        return str(path.resolve().relative_to(artifact_root.resolve()))
    except ValueError as exc:
        raise EventComparisonError("comparison input escapes artifact root") from exc


def _receipt_path(reference: Any, artifact_root: Path) -> Path:
    if not isinstance(reference, str) or Path(reference).is_absolute():
        raise EventComparisonError("receipt path must be relative to artifact root")
    result = (artifact_root / reference).resolve()
    _relative_receipt(result, artifact_root)
    return result


def _verify_staging(
    registry_path: Path, staged_path: Path, *, artifact_root: Path
) -> tuple[dict, list[dict], Path]:
    registry = _json(registry_path)
    manifest_path = staged_path.parent / "STAGING_MANIFEST.json"
    if not manifest_path.exists():
        raise EventComparisonError("comparison requires STAGING_MANIFEST.json")
    manifest = _json(manifest_path)
    if manifest.get("registry_sha256") != _sha256(registry_path):
        raise EventComparisonError("registry SHA-256 differs from staging manifest")
    if manifest.get("staged_sha256") != _sha256(staged_path):
        raise EventComparisonError("staged SHA-256 differs from staging manifest")
    rows = build_comparison_rows(
        registry, load_jsonl(staged_path), artifact_root=artifact_root
    )
    if manifest.get("staged_rows") != len(rows):
        raise EventComparisonError("staging manifest row count differs")
    total = Decimal(
        source_gbp_sum(
            {"value_gbp_decimal": row["obr_value_gbp_decimal"]} for row in rows
        )
    )
    exact_required = any(
        "value_gbp_decimal" in source
        for measure in registry["measures"]
        for source in measure["source_rows"]
    )
    for field in ("source_value_gbp_decimal", "staged_value_gbp_decimal"):
        if (exact_required or field in manifest) and _decimal(
            manifest.get(field), f"staging manifest/{field}"
        ) != total:
            raise EventComparisonError("staging manifest exact £ total differs")
    accounting = registry.get("accounting", {})
    if (
        "net_gbp_in_decimal" in accounting
        and _decimal(accounting["net_gbp_in_decimal"], "registry/net GBP") != total
    ):
        raise EventComparisonError("registry exact £ total differs")
    return registry, rows, manifest_path


def write_comparison(
    event: str,
    *,
    registry_path: Path | None = None,
    staged_path: Path | None = None,
    output_dir: Path | None = None,
    artifact_root: Path = ROOT,
) -> list[dict]:
    registry_path = (
        registry_path
        or artifact_root / "data" / "uk" / "events" / f"{event}_measures.json"
    )
    output_dir = output_dir or artifact_root / "results" / "uk" / "events" / event
    staged_path = staged_path or output_dir / "STAGED.jsonl"
    registry, rows, staging_manifest_path = _verify_staging(
        registry_path, staged_path, artifact_root=artifact_root
    )
    if registry.get("event_slug") != event:
        raise EventComparisonError("registry event differs from --event")
    output_dir.mkdir(parents=True, exist_ok=True)
    staging_manifest = _json(staging_manifest_path)
    replay_grid = {
        field: staging_manifest[field]
        for field in GRID_FIELDS
        if field in staging_manifest
    }
    payloads = {
        "COMPARISON.csv": render_csv(rows),
        "COMPARISON.md": render_markdown(registry, rows, replay_grid),
        "COMPARISON.json": json.dumps(rows, indent=1, sort_keys=True, allow_nan=False)
        + "\n",
    }
    for filename, payload in payloads.items():
        atomic_write_bytes(output_dir / filename, payload.encode())
    provenance = {
        "event_slug": event,
        "registry_path": _relative_receipt(registry_path, artifact_root),
        "registry_sha256": _sha256(registry_path),
        "staged_path": _relative_receipt(staged_path, artifact_root),
        "staged_sha256": _sha256(staged_path),
        "staging_manifest_path": _relative_receipt(
            staging_manifest_path, artifact_root
        ),
        "staging_manifest_sha256": _sha256(staging_manifest_path),
        "axes_sha256": _sha256(AXES_PATH),
        "source_rows": len(rows),
        "replay_grid": replay_grid,
        "outputs_sha256": {
            name: hashlib.sha256(payload.encode()).hexdigest()
            for name, payload in payloads.items()
        },
    }
    atomic_write_bytes(
        output_dir / "COMPARISON_PROVENANCE.json",
        (json.dumps(provenance, indent=1, sort_keys=True) + "\n").encode(),
    )
    return rows


def render_summary(
    events: dict[str, list[dict]],
    diagnostics: list[dict] | None = None,
    registries: dict[str, dict] | None = None,
    replay_grids: dict[str, dict] | None = None,
) -> str:
    rows = [row for event_rows in events.values() for row in event_rows]
    computed = [r for r in rows if r["pe_value_gbp"] is not None]
    registries = registries or {}
    replay_grids = replay_grids or {}
    lines = [
        "# Recent OBR fiscal-event replays",
        "",
        (
            "The inventories use the pinned populace-uk-2023 bundle definition with "
            "policyengine-uk 2.89.2. A seeded registry does not establish a completed "
            "numerical replay. Available comparisons use one source head and fiscal "
            "year per row."
        ),
        "",
        (
            f"Numerical comparison outputs available: {sum(any(r['pe_value_gbp'] is not None for r in event_rows) for event_rows in events.values())}. "
            f"Registry inventories available: {len(registries)}."
        ),
        "",
        "| Event | Replay state | Measures | Source rows | Computed rows | Computed FYs |",
        "|---|---|---:|---:|---:|---|",
    ]
    for event in sorted(set(events) | set(registries)):
        event_rows = events.get(event, [])
        registry = registries.get(event)
        years = sorted({r["fy"] for r in event_rows if r["pe_value_gbp"] is not None})
        computed_count = sum(r["pe_value_gbp"] is not None for r in event_rows)
        source_count = (
            registry["accounting"]["rows_in"] if registry else len(event_rows)
        )
        measure_count = (
            len(registry["measures"])
            if registry
            else len({r["measure_key"] for r in event_rows})
        )
        state = (
            "Numerical comparison available"
            if computed_count
            else "Registry seeded; numerical replay incomplete"
        )
        replay_grid = replay_grids.get(event)
        if computed_count and replay_grid:
            state = (
                "Numerical replay complete"
                if replay_grid.get("full_event_complete")
                else (
                    "Numerical comparison available; replay grid incomplete "
                    f"({replay_grid.get('computed_measure_years', 0)}/"
                    f"{replay_grid.get('full_event_grid_size', 'unspecified')})"
                )
            )
        label = f"[{event}]({event}/COMPARISON.md)" if event_rows else event
        lines.append(
            f"| {label} | {state} | {measure_count} | {source_count} | {computed_count} | {', '.join(years) or '—'} |"
        )
    if registries:
        lines += [
            "",
            "## Source inventory accounting",
            "",
            (
                "These amounts sum all source heads and costing years, including zero cells. "
                "They are inventory totals, not one-year event costings or numerical agreement statistics."
            ),
            "",
            "| Event / class | Measures | Source rows | Net OBR £bn | Absolute OBR £bn |",
            "|---|---:|---:|---:|---:|",
        ]
        for event, registry in sorted(registries.items()):
            for classification, account in registry["accounting"]["by_class"].items():
                lines.append(
                    f"| {event} / {classification} | {account['measures']} | {account['rows']} | "
                    f"{Decimal(account['net_gbp_decimal']) / Decimal(10**9):,.3f} | "
                    f"{Decimal(account['absolute_gbp_decimal']) / Decimal(10**9):,.3f} |"
                )
    lines += ["", "## Agreement profile", ""]
    if not computed:
        lines += [
            (
                "Unavailable: no completed numerical comparison rows have been published. "
                "Registry coverage does not supply a PE/OBR agreement profile."
            ),
            "",
        ]
    for field, label in (
        (("tax_head", "Tax head"), ("measure_type", "Measure type")) if computed else ()
    ):
        lines += [f"| {label} | Source-row ratio bins |", "|---|---|"]
        lines += [
            f"| {_md(key)} | {_md(', '.join(f'{k}: {v}' for k, v in counts.items()))} |"
            for key, counts in profile(rows, field)
        ]
        lines.append("")
    explained = [r for r in computed if r.get("explained_share") is not None]
    lines += [
        "## Named axes and explained share",
        "",
        (
            "population_vintage tags every row: the fiscal event's OBR forecast differs "
            "from the certified 2023 population and its later calibration targets. "
            "behavioural_adjustment, baseline_vintage, cy_proxies_fy and head_scope "
            "describe the other construction differences. construction_scope identifies "
            "partial measures. The pipeline does not adjust the population vintage."
        ),
        "",
        (
            "Pinned employer-NIC incidence assigns the wage adjustment fully to employees "
            "while holding employer cost fixed. OBR's direct per-head costings exclude "
            "separately reported macroeconomic indirect effects. This construction/head_scope "
            "difference is named, but its contribution to the raw gaps remains unsized."
        ),
        "",
        (
            f"Axis-tagged coverage: {len(computed)} computed rows, "
            f"£{sum(abs(r['gap_gbp']) for r in computed) / 1e9:,.3f}bn of absolute raw gap. "
            f"Explained share is available on {len(explained)} rows; relevant unsized axes "
            "withhold it on the rest. These are different quantities."
        )
        if computed
        else "National gaps and explained share are unavailable until numerical comparisons exist.",
        "",
        "## Largest unexplained divergences",
        "",
        (
            "The queue below is ranked by absolute residual_plus_unsized, after any "
            "evidence-backed sized terms. It names variables and a minimal run selection "
            "for investigation. A raw gap with unsized vintage or behavioural terms "
            "does not establish a PolicyEngine model issue. Multiple years of one "
            "measure share a potential mechanism, so the queue selects one row per measure."
        ),
        "",
        "| Event / measure | FY / head | Residual £bn | Variables | Evidence / diagnosis | Minimal replay |",
        "|---|---|---:|---|---|---|",
    ]
    seen = set()
    for row in sorted(computed, key=lambda r: -abs(r["residual_gbp"])):
        if row["measure_key"] in seen:
            continue
        seen.add(row["measure_key"])
        diagnostic = row.get("diagnosis") or {}
        evidence = diagnostic.get("evidence", "Open: relevant axes unsized")
        command = (
            f"PYTHONPATH=. .venv-replay/bin/python pipeline/compute_uk_event.py --event {row['event_slug']} "
            f"--measures {row['measure_key']} --years {row['year']} --workers 1 "
            f"--output-dir .venv-replay-checks/reproductions/{row['event_slug']}/{row['measure_key']}_{row['year']}"
        )
        lines.append(
            f"| {_md(row['event_slug'] + ' / ' + row['title'])} | "
            f"{row['fy']} / {_md(row['tax_head'])} | {_billions(row['residual_gbp'])} | "
            f"{_md(', '.join(row['head_variables']))} | {_md(evidence)} | `{command}` |"
        )
        if len(seen) == 10:
            break
    if not seen:
        lines.append("| No computed divergences | — | — | — | — | — |")
    diagnosed = [
        r for r in computed if (r.get("diagnosis") or {}).get("class") == "pe_gap"
    ]
    diagnostics = diagnostics or []
    active_events = set(events) | set(registries)
    relevant = [d for d in diagnostics if set(d.get("events", [])) & active_events]
    concrete = [d for d in relevant if d.get("class") == "pe_gap"]
    lines += [
        "",
        (
            f"Evidence-backed PolicyEngine issue candidates recorded: {len(concrete) + len({r['measure_key'] for r in diagnosed})}. "
            "No upstream issues were filed by this replay lane."
        ),
        "",
    ]
    if relevant:
        lines += [
            "## Measured model investigation candidates",
            "",
            (
                "These are engine observations reproduced separately from the national costing. "
                "Their national contribution remains unsized. The list contains only observed "
                "candidates; it is not padded to ten."
            ),
            "",
            "| Candidate | Class | Variables | Evidence | Minimal reproducer |",
            "|---|---|---|---|---|",
        ]
        for diagnostic in relevant:
            command = (
                "PYTHONPATH=. .venv-replay/bin/python pipeline/diagnose_uk_event_models.py "
                + diagnostic["reproducer"]
            )
            lines.append(
                f"| {_md(diagnostic['id'])} | {_md(diagnostic['class'])} | "
                f"{_md(', '.join(diagnostic['variables']))} | "
                f"{_md(diagnostic['evidence']['engine_file'])} (source SHA and measured values in MODEL_DIAGNOSTICS.json) | `{command}` |"
            )
        lines.append("")
    return "\n".join(lines)


def load_verified_comparison(path: Path, *, artifact_root: Path = ROOT) -> list[dict]:
    """Bind summary-only reads to current source, stage, axes and artifact bytes."""
    provenance_path = path.parent / "COMPARISON_PROVENANCE.json"
    if not provenance_path.exists():
        raise EventComparisonError("summary requires COMPARISON_PROVENANCE.json")
    provenance = _json(provenance_path)
    if provenance.get("event_slug") != path.parent.name:
        raise EventComparisonError("comparison provenance event differs")
    if provenance.get("axes_sha256") != _sha256(AXES_PATH):
        raise EventComparisonError("comparison axes SHA-256 is stale")
    outputs = provenance.get("outputs_sha256", {})
    if set(outputs) != {"COMPARISON.json", "COMPARISON.csv", "COMPARISON.md"}:
        raise EventComparisonError("comparison output receipt is incomplete")
    for name, digest in outputs.items():
        if _sha256(path.parent / name) != digest:
            raise EventComparisonError(f"comparison output SHA-256 differs: {name}")
    paths = {}
    for label in ("registry", "staged", "staging_manifest"):
        receipt = _receipt_path(provenance.get(f"{label}_path"), artifact_root)
        if _sha256(receipt) != provenance.get(f"{label}_sha256"):
            raise EventComparisonError(f"comparison {label} SHA-256 is stale")
        paths[label] = receipt
    registry, verified_rows, manifest_path = _verify_staging(
        paths["registry"], paths["staged"], artifact_root=artifact_root
    )
    if manifest_path != paths["staging_manifest"]:
        raise EventComparisonError("comparison staging manifest path differs")
    manifest = _json(manifest_path)
    grid = {field: manifest[field] for field in GRID_FIELDS if field in manifest}
    if provenance.get("replay_grid") != grid:
        raise EventComparisonError("comparison replay-grid receipt differs")
    if registry.get("event_slug") != path.parent.name:
        raise EventComparisonError("summary registry event differs")
    canonical_registry = (
        artifact_root / "data" / "uk" / "events" / f"{path.parent.name}_measures.json"
    )
    if (
        canonical_registry.exists()
        and _sha256(canonical_registry) != provenance["registry_sha256"]
    ):
        raise EventComparisonError("comparison differs from current event registry")
    rows = json.loads(path.read_text())
    if rows != verified_rows or provenance.get("source_rows") != len(rows):
        raise EventComparisonError("comparison rows differ from verified staging")
    return rows


def write_summary(events_root: Path, *, artifact_root: Path = ROOT) -> None:
    events = {
        path.parent.name: load_verified_comparison(path, artifact_root=artifact_root)
        for path in sorted(events_root.glob("*/COMPARISON.json"))
    }
    replay_grids = {
        path.parent.name: _json(path.parent / "COMPARISON_PROVENANCE.json")[
            "replay_grid"
        ]
        for path in sorted(events_root.glob("*/COMPARISON.json"))
    }
    diagnostic_path = events_root / "MODEL_DIAGNOSTICS.json"
    diagnostics = (
        json.loads(diagnostic_path.read_text()) if diagnostic_path.exists() else []
    )
    registries = {
        path.stem.removesuffix("_measures"): _json(path)
        for path in sorted(
            (artifact_root / "data" / "uk" / "events").glob("*_measures.json")
        )
    }
    events_root.mkdir(parents=True, exist_ok=True)
    atomic_write_bytes(
        events_root / "SUMMARY.md",
        render_summary(events, diagnostics, registries, replay_grids).encode(),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--event")
    parser.add_argument("--registry", type=Path)
    parser.add_argument("--staged", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--summary", action="store_true")
    parser.add_argument(
        "--events-root", type=Path, default=ROOT / "results" / "uk" / "events"
    )
    args = parser.parse_args(argv)
    if args.event:
        rows = write_comparison(
            args.event,
            registry_path=args.registry,
            staged_path=args.staged,
            output_dir=args.output_dir,
        )
        print(f"{args.event}: wrote {len(rows)} descriptive comparison rows")
    elif not args.summary:
        parser.error("--event or --summary is required")
    if args.summary:
        write_summary(args.events_root)
        print(f"wrote {args.events_root / 'SUMMARY.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
