"""Join external baseline moments to PolicyEngine counterparts.

The join key is ``(program, metric, subgroup, geography, period)``.  Variant
is a construct axis rather than part of the key:

* ``comparable``: the selected external and PE rows share a variant;
* ``concept_mismatch``: a same-period PE row exists under another variant;
* ``not_computed``: no PE value exists for the external row's period; and
* ``suppressed``: the external source withheld the value.

Every external row remains in the output.  A row may also name a
``reference_period``.  That dated PE value is attached as context without
changing the status or period of the external claim.

Output: ``app/public/data/moments.json``.
"""

from __future__ import annotations

import json
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXTERNALS = ROOT / "data" / "externals"
SOURCES = (
    "yale-tariff-tracker",
    "tpc-tariffs",
    "kff-remaining-uninsured",
)
COUNTERPART_FILES = {
    "tariff": ROOT / "data" / "pe" / "tariff_counterparts.json",
    "kff_medicaid": ROOT / "data" / "pe" / "kff_medicaid_counterparts.json",
}

JOIN_FIELDS = ("program", "metric", "subgroup", "geography", "period")
PROVENANCE_FIELDS = (
    "engine_version",
    "data_bundle",
    "bundle_id",
    "computed_at",
)


def load_annotations(sources: tuple[str, ...] = SOURCES) -> list[dict]:
    entries = []
    for source in sources:
        path = ROOT / "sources" / source / "annotations.json"
        entries.extend(json.loads(path.read_text()))
    return entries


def load_counterpart_payloads() -> dict[str, dict]:
    """Load available declared counterpart files.

    A missing file means those rows have not been computed yet; it is not a
    reason to discard their external claims.  Once a counterpart file is
    staged, the same builder attaches it without another wiring change.
    """
    return {
        name: json.loads(path.read_text())
        for name, path in COUNTERPART_FILES.items()
        if path.exists()
    }


def join_key(row: dict, period: str | None = None) -> tuple:
    return tuple(
        period if field == "period" and period is not None else row[field]
        for field in JOIN_FIELDS
    )


def index_counterparts(rows: list[dict]) -> dict[tuple, list[dict]]:
    """Index all variants without silently overwriting alternatives."""
    indexed = defaultdict(list)
    identities = defaultdict(set)
    for row in rows:
        key = join_key(row)
        identity = (row.get("variant"), row.get("coverage_variant"))
        if identity in identities[key]:
            raise ValueError(f"duplicate PE counterpart {key!r} {identity!r}")
        identities[key].add(identity)
        indexed[key].append(row)
    return dict(indexed)


def _select_counterpart(
    external: dict, candidates: list[dict]
) -> tuple[dict | None, list[dict]]:
    """Choose the primary construct and return every other variant.

    Exact full-variant matches take priority.  KFF's source and PE variant
    names deliberately differ because their eligibility constructs differ,
    so ``coverage_variant`` selects the closest reported-uninsured PE row.
    """
    if not candidates:
        return None, []

    exact = [row for row in candidates if row.get("variant") == external.get("variant")]
    if len(exact) > 1:
        raise ValueError(f"ambiguous exact PE variant for {join_key(external)!r}")
    if exact:
        primary = exact[0]
    else:
        coverage_variant = external.get("coverage_variant")
        coverage_matches = [
            row
            for row in candidates
            if coverage_variant is not None
            and row.get("coverage_variant") == coverage_variant
        ]
        if len(coverage_matches) > 1:
            raise ValueError(
                f"ambiguous PE coverage variant for {join_key(external)!r}"
            )
        if coverage_matches:
            primary = coverage_matches[0]
        elif len(candidates) == 1:
            primary = candidates[0]
        else:
            raise ValueError(f"no primary PE variant for {join_key(external)!r}")

    alternatives = [row for row in candidates if row is not primary]
    alternatives.sort(
        key=lambda row: (row.get("coverage_variant") or "", row.get("variant") or "")
    )
    return primary, alternatives


def _annotation_applies(annotation: dict, row: dict) -> bool:
    for field, expected in annotation.get("applies", {}).items():
        if expected is None:
            continue
        actual = row.get(field)
        if isinstance(expected, list):
            if actual not in expected:
                return False
        elif actual != expected:
            return False
    return True


def annotation_ids_for(annotations: list[dict], row: dict) -> list[str]:
    return [
        annotation["id"]
        for annotation in annotations
        if _annotation_applies(annotation, row)
    ]


def _copy_counterpart(row: dict | None) -> dict | None:
    return None if row is None else dict(row)


def join_external_row(
    external: dict,
    counterparts: dict[tuple, list[dict]],
    annotations: list[dict],
    claim_class: str = "baseline_moment",
) -> dict:
    """Join one external claim while preserving its source metadata."""
    external_status = external.get("status", "ok")
    external_value = external.get("value")
    candidates = counterparts.get(join_key(external), [])

    if external_status == "suppressed":
        status = "suppressed"
        primary = None
        alternatives = []
    else:
        primary, alternatives = _select_counterpart(external, candidates)
        if primary is None or primary.get("value") is None:
            status = "not_computed"
        elif primary.get("variant") == external.get("variant"):
            status = "comparable"
        else:
            status = "concept_mismatch"

    reference = None
    reference_alternatives = []
    reference_period = external.get("reference_period")
    if external_status != "suppressed" and reference_period is not None:
        reference, reference_alternatives = _select_counterpart(
            external,
            counterparts.get(join_key(external, period=reference_period), []),
        )

    pe_value = primary.get("value") if primary is not None else None
    delta = (
        pe_value - external_value
        if pe_value is not None and external_value is not None
        else None
    )
    row = dict(external)
    row.pop("value", None)
    row["external_status"] = external_status
    row["external_value"] = external_value
    row["claim_class"] = claim_class
    row["pe_value"] = pe_value
    row["pe_variant"] = primary.get("variant") if primary is not None else None
    row["pe_counterpart"] = _copy_counterpart(primary)
    row["pe_alternatives"] = [_copy_counterpart(item) for item in alternatives]
    row["pe_reference"] = _copy_counterpart(reference)
    row["pe_reference_alternatives"] = [
        _copy_counterpart(item) for item in reference_alternatives
    ]
    row["delta"] = delta
    row["status"] = status
    row["annotation_ids"] = annotation_ids_for(annotations, row)

    provenance_row = primary or reference
    if provenance_row is not None:
        for field in PROVENANCE_FIELDS:
            if field in provenance_row:
                row[field] = provenance_row[field]
    return row


def build_payload(
    external_rows: dict[str, list[dict]],
    source_meta: dict[str, dict],
    counterpart_payloads: dict[str, dict],
    annotations: list[dict],
    built: str | None = None,
) -> dict:
    pe_rows = [
        row
        for payload in counterpart_payloads.values()
        for row in payload.get("rows", [])
    ]
    counterpart_index = index_counterparts(pe_rows)
    rows = []
    for source in SOURCES:
        meta = source_meta[source]
        rows.extend(
            join_external_row(
                external,
                counterpart_index,
                annotations,
                claim_class=meta.get("claim_class", "baseline_moment"),
            )
            for external in external_rows[source]
        )

    statuses = {}
    for row in rows:
        statuses[row["status"]] = statuses.get(row["status"], 0) + 1
    return {
        "built": built or date.today().isoformat(),
        "claim_class": "baseline_moment",
        "pe_provenance": {
            name: payload.get("provenance", {})
            for name, payload in counterpart_payloads.items()
        },
        "source_meta": source_meta,
        "sources": SOURCES,
        "summary": {"rows": len(rows), "by_status": statuses},
        "annotations": annotations,
        "rows": rows,
    }


def main() -> None:
    external_rows = {
        source: json.loads((EXTERNALS / f"{source}.json").read_text())
        for source in SOURCES
    }
    source_meta = {
        source: json.loads((ROOT / "sources" / source / "source.json").read_text())
        for source in SOURCES
    }
    payload = build_payload(
        external_rows,
        source_meta,
        load_counterpart_payloads(),
        load_annotations(),
    )
    out = ROOT / "app" / "public" / "data" / "moments.json"
    out.write_text(json.dumps(payload, indent=1) + "\n")
    print(f"{out}: {payload['summary']['rows']} rows {payload['summary']['by_status']}")


if __name__ == "__main__":
    main()
