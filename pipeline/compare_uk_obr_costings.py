#!/usr/bin/env python3
"""Write descriptive OBR/PE-UK costing counterparts from staged results.

The harvested OBR descriptor carries the verbatim measure description and
source table needed to resolve every row exactly once. Every staged PE value is
then checked against the frozen source-claim snapshot and PE value in its saved
run artifact.

The output retains source head rows.  For PMD measures with at least two mapped
heads, it also shows a comparison-only sum of those mapped heads.  That sum is
never represented as, or attached to, an external TOTAL claim.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

import yaml

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REGISTRY = ROOT / "data" / "uk" / "obr_measure_reforms.yaml"
DEFAULT_CLAIMS = Path.home() / "scorecard-harvest" / "uk_obr" / "claims_staged.jsonl"
DEFAULT_STAGED = ROOT / "results" / "uk" / "staged" / "obr_costings.jsonl"
DEFAULT_OUTPUT_DIR = ROOT / "results" / "uk" / "obr_costings"
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


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text().splitlines(), 1):
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


def load_registry(path: Path) -> dict[str, dict[str, Any]]:
    spec = yaml.safe_load(path.read_text())
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


def _artifact_file(reference: str, artifact_root: Path) -> Path:
    path = Path(reference)
    return path if path.is_absolute() else artifact_root / path


def _snapshot_identity(snapshot: dict[str, Any]) -> tuple[Any, ...]:
    return (
        snapshot.get("source"),
        snapshot.get("source_table"),
        snapshot.get("reform_hint"),
        snapshot.get("metric"),
        snapshot.get("period"),
        _canonical(snapshot.get("conditions")),
    )


def _claim_identity(claim: dict[str, Any]) -> tuple[Any, ...]:
    return (
        claim.get("source"),
        claim.get("source_table"),
        claim.get("reform_hint"),
        claim_metric(claim),
        claim.get("period"),
        _canonical(claim.get("conditions")),
    )


def validate_artifact_trace(
    staged_row: dict[str, Any], claim: dict[str, Any], artifact_root: Path = ROOT
) -> dict[str, Any] | None:
    """Validate a PE value and frozen claim against its referenced run artifact."""

    pe_value = staged_row["pe_value"]
    if pe_value is None:
        if staged_row.get("artifact") is not None:
            raise ComparisonError(
                f"{staged_row['measure_key']}: null PE value unexpectedly names an artifact"
            )
        return None
    if not _is_number(pe_value) or not math.isfinite(pe_value):
        raise ComparisonError(f"{staged_row['measure_key']}: invalid staged PE value")
    reference = staged_row.get("artifact")
    if not isinstance(reference, str) or not reference:
        raise ComparisonError(
            f"{staged_row['measure_key']}: every PE value must name a run artifact"
        )
    path = _artifact_file(reference, artifact_root)
    try:
        artifact = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise ComparisonError(f"cannot read artifact {path}: {exc}") from exc
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
            f"{path}: staged/artifact identity differs: {differences}"
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
            f"{path}: {len(hits)} artifact heads match the frozen OBR claim; expected one"
        )
    head = hits[0]
    snapshot = head["external_claim"]
    if snapshot.get("value_gbp") != claim["value"]:
        raise ComparisonError(f"{path}: frozen and harvested OBR values differ")
    if snapshot.get("unit") != "gbp":
        raise ComparisonError(f"{path}: frozen OBR value is not normalized to gbp")
    if head.get("pe_value") != pe_value:
        raise ComparisonError(f"{path}: staged and artifact PE values differ")
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
    override = measure.get("computability_overrides", {}).get(year)
    return (
        override["computability"]
        if isinstance(override, dict)
        else measure["computability"]
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
    artifact_root: Path = ROOT,
) -> list[dict[str, Any]]:
    """Resolve, trace, and assemble head and mapped-head-total rows."""

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
        artifact_head = validate_artifact_trace(staged_row, claim, artifact_root)
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
        "| Measure | FY | Head / scope | OBR (£bn) | PE (£bn) | PE / OBR | Ratio bin | Status | Annotations |",
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
            "- Same-sign numeric bins: below 0.5; 0.5–0.8; 0.8–1.25; 1.25–2; at least 2.",
            "- `pe_zero`, `obr_zero`, `both_zero`, and `not_available` describe zero or absent values directly.",
            "",
        ]
    )
    return "\n".join(lines)


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(text)
    temporary.replace(path)


def write_comparison_outputs(
    *,
    registry_path: Path = DEFAULT_REGISTRY,
    claims_path: Path = DEFAULT_CLAIMS,
    staged_path: Path = DEFAULT_STAGED,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    artifact_root: Path = ROOT,
) -> list[dict[str, Any]]:
    """Validate inputs and write both deterministic comparison renderings."""

    if not staged_path.exists():
        raise ComparisonError(f"staged results do not exist: {staged_path}")
    staged_rows = load_jsonl(staged_path)
    if not staged_rows:
        raise ComparisonError(f"staged results are empty: {staged_path}")
    rows = build_comparison_rows(
        staged_rows,
        load_jsonl(claims_path),
        load_registry(registry_path),
        artifact_root=artifact_root,
    )
    atomic_write_text(output_dir / "COMPARISON.csv", render_csv(rows))
    atomic_write_text(output_dir / "COMPARISON.md", render_markdown(rows))
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--claims", type=Path, default=DEFAULT_CLAIMS)
    parser.add_argument("--staged", type=Path, default=DEFAULT_STAGED)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--artifact-root",
        type=Path,
        default=ROOT,
        help="Base for artifact paths stored relative to the repository root",
    )
    args = parser.parse_args(argv)

    rows = write_comparison_outputs(
        registry_path=args.registry,
        claims_path=args.claims,
        staged_path=args.staged,
        output_dir=args.output_dir,
        artifact_root=args.artifact_root,
    )
    csv_path = args.output_dir / "COMPARISON.csv"
    markdown_path = args.output_dir / "COMPARISON.md"
    totals = sum(row["row_kind"] == "mapped_head_total" for row in rows)
    print(
        f"wrote {len(rows)} descriptive rows ({totals} mapped-head totals) to "
        f"{csv_path} and {markdown_path}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
