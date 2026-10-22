"""Export DB-backed populations for the app -> data/populations.json.

The Urban SotSN population reaches the app through the file-based
pipeline/build_comparison.py export (data/comparison.json). Everything
else lives only in scorecard.db: the reform-validation registry (issue
#20, its 205 minted claims plus the 36 harvested JCX-35-25 provision
claims its OBBBA results attach to), the US campaign attaches, and —
since the campaign-UK producer — the 14 uk_hmrc reckoner claims with
campaign results; Belgium's honest concept-mismatch Axiom attachments
to JRC EUROMOD-BE claims; and New Zealand's official budget scores. This
module exports every non-Urban claim with a result plus claims that explicitly
opt in through publication.publish_without_result. That narrow gate
lets newly registered official scores appear before their first model run
without flooding the app with the entire uncomputed harvest. Available results
carry the dimension the Urban export doesn't have: the full per-release result
history (one row per certified release, engine pins and OBBBA scoring mode in
the construction), plus the Belgian PIT-reform scorekeeper rows, so
cross-release drift is visible.

The comprehensive historical PMD lane is exported as compact fiscal-event
files in populations-pmd/, indexed by event_archives in the main feed. Every
score contributes to the summary before its detail is loaded. Existing
costings-slice rows stay in the main feed. A shard factors only fields identical
across its rows, so expanding common fields and conditions restores them
without dropping values, zero cells, statuses or provenance shown by this feed.

Doctrine (issues #1/#9): descriptive only. Recorded result statuses and
calibration relationships are exported verbatim; a no-result claim receives
only a synthetic latest status of not_computed, never a fabricated history
entry. Ratios are raw pe/external with no pass/fail anywhere.
concept_mismatch results carry their construction so the app can label, never
grade.

Every row also carries the published value's sign against PolicyEngine's
(issue #198, scorecard_db/signs.py): sign_relative_to_pe (same | opposite |
magnitude | unknown), the sign_basis rule that decided it, and
external_value_pe_sign, the published value in that orientation (null for
magnitude and unknown). The free-text conditions.sign_convention stays as
the record.

A UK row whose conditions.measure_key names a measure in a committed UK
registry also carries that measure's ``measure`` block (issue #209): its
programme, the model variables it heads, and the PolicyEngine parameter
paths its construction sets, so a
report that changes one of those parameters can find the row. The block is
the registry's, verbatim; it is null for every other row.

Also refreshes data/lanes.json via ingest_harvest.sync_lane_feed so the
populace-reform-validation lane appears in mission control.

Usage:
    PYTHONPATH=. python -m scorecard_db.export_populations data/scorecard.db
"""

from __future__ import annotations

import json
from collections import defaultdict
from datetime import date
from hashlib import sha256
from pathlib import Path

from . import signs
from .db import CURRENT_LAW_KEY, ScorecardDB
from .ingest_harvest import sync_lane_feed

REPO = Path(__file__).resolve().parent.parent
URBAN_SOURCE = "urban_sotsn"
PMD_REGISTRY = "obr_pmd_all_events"
PMD_REGISTRIES = frozenset({PMD_REGISTRY, "obr_pmd_march2026"})
PMD_DIRECTORY = "populations-pmd"
# The AB2025 registry is the one the AB2025 and OBR costings ingests join
# through, so it decides its own keys. The replay registries under
# data/uk/events/ restate many AB2025 keys with their own programme list;
# they answer only the keys the AB2025 registry does not define.
UK_MEASURE_REGISTRIES = (
    REPO / "data" / "uk" / "ab2025_measures.json",
    REPO / "data" / "uk" / "budget_2026_measures.json",
)
UK_EVENT_REGISTRIES = REPO / "data" / "uk" / "events"


def uk_measures() -> dict[str, dict]:
    """Every committed UK measure by key: its programme, computability, the
    model variables it heads, and the sorted parameter paths of its reform
    delta and baseline modifier."""
    measures: dict[str, dict] = {}
    owner: dict[str, Path] = {}

    def add(path: Path, primary: bool) -> None:
        for m in json.loads(path.read_text())["measures"]:
            key = m["measure_key"]
            if key in owner:
                if not primary and owner[key] in UK_MEASURE_REGISTRIES:
                    continue
                raise ValueError(
                    f"UK measure {key!r} is defined in both {owner[key].name}"
                    f" and {path.name}"
                )
            owner[key] = path
            measures[key] = {
                "key": key,
                "program": m.get("program"),
                "computability": m.get("computability"),
                "head_variables": list(m.get("head_variables") or []),
                "parameter_paths": sorted(
                    set(m.get("pe_reform_delta") or {})
                    | set(m.get("pe_baseline_modifier") or {})
                ),
            }

    for path in UK_MEASURE_REGISTRIES:
        add(path, primary=True)
    for path in sorted(UK_EVENT_REGISTRIES.glob("*_measures.json")):
        add(path, primary=False)
    return measures


def _compact_rows(rows: list[dict]) -> dict:
    """Factor only identical fields; decoding restores each row exactly."""
    common = {
        key: value
        for key, value in rows[0].items()
        if key != "conditions" and all(row[key] == value for row in rows)
    }
    conditions = {
        key: value
        for key, value in rows[0]["conditions"].items()
        if all(
            key in row["conditions"] and row["conditions"][key] == value for row in rows
        )
    }
    return {
        "common": common,
        "common_conditions": conditions,
        "rows": [
            {
                **{key: value for key, value in row.items() if key not in common},
                "conditions": {
                    key: value
                    for key, value in row["conditions"].items()
                    if key not in conditions
                },
            }
            for row in rows
        ],
    }


def _counts(rows: list[dict]) -> dict:
    """A recorded gap result is distinct from a PolicyEngine value."""
    return {
        "claims": len(rows),
        "with_result": sum(bool(row["results"]) for row in rows),
        "with_value": sum(row["latest"]["value"] is not None for row in rows),
        "without_result": sum(not row["results"] for row in rows),
        "multi_release_claims": sum(len(row["results"]) > 1 for row in rows),
    }


_RELEASE_TOKEN = (
    "l0-refit",
    "buildi",
    "buildj",
    "buildo",
    "buildp",
    "spm-20260915",
    "f0af251",
    "microcosm_be_v02",
    "microcosm_be_v05h",
    "parameter-tree",
)


def release_label(bundle: str) -> str:
    """Short human label for a data-bundle id ("buildo", "l0-refit")."""
    for token in _RELEASE_TOKEN:
        if token in bundle:
            return token
    return bundle.rsplit("-", 1)[0][-12:]


def _effective_status(status: str, result_bk: str | None, claim_bk: str | None) -> str:
    """Mirror of the comparisons-view #13 guard, applied per result so
    the exported feed can never publish plain agreement across baseline
    worlds (or over unverifiable legacy provenance)."""
    if status != "comparable" or claim_bk is None:
        return status
    if result_bk is not None and result_bk != claim_bk:
        return "constructed"
    if result_bk is None and claim_bk != CURRENT_LAW_KEY:
        return "baseline_unvalidated"
    return status


def _ratio(pe: float | None, external: float | None) -> float | None:
    if pe is None or external is None or external == 0:
        return None
    return pe / external


def export(
    db_path: Path,
    out_path: Path | None = None,
    lanes_path: Path | None = None,
    built: str | None = None,
) -> dict:
    out_path = out_path or REPO / "data" / "populations.json"
    db = ScorecardDB(db_path)
    claims = db.conn.execute(
        """SELECT s.*, d.diagnosis_class, d.rationale, d.action_link
           FROM external_scores s
           LEFT JOIN diagnoses d USING (claim_id)
           WHERE s.source != ?
             AND (EXISTS (SELECT 1 FROM pe_results r
                          WHERE r.claim_id = s.claim_id)
                  OR json_extract(s.publication,
                                  '$.publish_without_result') = 1)
           ORDER BY s.source, s.metric, s.period, s.source_column,
                    s.claim_id""",
        (URBAN_SOURCE,),
    ).fetchall()

    labels = {
        r["baseline_key"]: r["label"]
        for r in db.conn.execute("SELECT baseline_key, label FROM baselines")
    }
    measures = uk_measures()
    rows = []
    by_source: dict[str, int] = {}
    by_status: dict[str, int] = {}
    by_sign: dict[str, int] = {}
    multi_release = 0
    archive_events: dict[str, tuple[str, str]] = {}
    for c in claims:
        results = [
            {
                "value": r["computed_value"],
                "status": r["status"],
                "engine_version": r["engine_version"],
                "data_bundle": r["data_bundle"],
                "release": release_label(r["data_bundle"]),
                "construction": r["pe_construction"],
                "policyengine_variables": json.loads(r["policyengine_variables"]),
                "computed_at": r["computed_at"],
                "annotations": json.loads(r["annotations"]),
                "baseline": labels.get(r["baseline_key"]),
                "status_effective": _effective_status(
                    r["status"], r["baseline_key"], c["baseline_key"]
                ),
            }
            for r in db.conn.execute(
                """SELECT computed_value, status, engine_version,
                          data_bundle, pe_construction, computed_at,
                          annotations, baseline_key, policyengine_variables
                   FROM pe_results WHERE claim_id = ?
                   ORDER BY computed_at, id""",
                (c["claim_id"],),
            )
        ]
        latest = (
            results[-1]
            if results
            else {
                "value": None,
                "status": "not_computed",
                "engine_version": "",
                "data_bundle": "",
                "release": "",
                "construction": "",
                "policyengine_variables": [],
                "computed_at": "",
                "annotations": [],
                "baseline": None,
                "status_effective": "not_computed",
            }
        )
        publication = json.loads(c["publication"])
        reform = json.loads(c["reform_json"])
        conditions = json.loads(c["conditions"])
        if publication.get("registry") in PMD_REGISTRIES:
            event = conditions["fiscal_event"]
            archive_events[c["claim_id"]] = (
                event,
                publication.get("fiscal_event_name", event),
            )
        # Harvest OBBBA claims carry no per-claim name — the provision
        # label in conditions is their identity; the publication title is
        # the whole JCX document.
        # PMD cells carry their measure in conditions; the source column
        # identifies the fiscal year, and the title names the whole workbook.
        name = (
            publication.get("name")
            or conditions.get("provision")
            or (conditions.get("measure") if c["source"] == "obr_pmd" else None)
            or publication.get("title")
            or ""
        )
        if len({r["data_bundle"] for r in results}) > 1:
            multi_release += 1
        by_source[c["source"]] = by_source.get(c["source"], 0) + 1
        eff = latest["status_effective"]
        by_status[eff] = by_status.get(eff, 0) + 1
        # issue #198: the published value's sign against PolicyEngine's
        relation, sign_basis = signs.classify(
            {
                "metric": c["metric"],
                "conditions": conditions,
                "latest": latest,
                "country": conditions.get("country", "US"),
                "source": c["source"],
            }
        )
        by_sign[relation] = by_sign.get(relation, 0) + 1
        rows.append(
            {
                "claim_id": c["claim_id"],
                "source": c["source"],
                # the model instance the claim belongs to (issue #42):
                # non-US claims carry conditions["country"]; its absence IS
                # the US claim-side convention, mirrored by the app's
                # countryOf() default — emit it explicitly so the feed never
                # relies on the default for non-US rows
                "country": conditions.get("country", "US"),
                "source_column": c["source_column"],
                "name": name,
                "window": publication.get("window") or "",
                "publication_title": publication.get("title") or "",
                "url": publication.get("url") or "",
                "metric": c["metric"],
                "unit_concept": c["unit_concept"],
                "value_kind": c["value_kind"],
                "period": c["period"],
                "time_basis": c["time_basis"],
                "period_start": c["period_start"],
                "period_end": c["period_end"],
                "geography": c["geography"],
                "program": c["program"],
                "conditions": conditions,
                "measure": (
                    measures.get(conditions.get("measure_key"))
                    if conditions.get("country") == "UK"
                    else None
                ),
                "reform_framework": reform.get("framework"),
                "reform_key": c["reform_key"],
                "external_value": c["value"],
                "sign_relative_to_pe": relation,
                "sign_basis": sign_basis,
                "external_value_pe_sign": signs.external_value_pe_sign(
                    c["value"], relation
                ),
                "calibration_relationship": c["calibration_relationship"],
                "claim_baseline": labels.get(c["baseline_key"]),
                "latest": {
                    **latest,
                    "ratio": _ratio(latest["value"], c["value"]),
                    "delta": (
                        latest["value"] - c["value"]
                        if latest["value"] is not None and c["value"] is not None
                        else None
                    ),
                },
                "results": results,
                "diagnosis": (
                    {
                        "class": c["diagnosis_class"],
                        "rationale": c["rationale"],
                        "action_link": c["action_link"],
                    }
                    if c["diagnosis_class"]
                    else None
                ),
            }
        )

    # The historical PMD is comprehensive, including thousands of scores with
    # no result. Keep every score reachable without adding them all to the
    # initial browser request: load one fiscal event on demand. Existing
    # costings-slice rows retain their place in the main feed.
    archived: dict[str, list[dict]] = defaultdict(list)
    main_rows = []
    countries: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        countries[row["country"]].append(row)
        if row["claim_id"] in archive_events:
            archived[archive_events[row["claim_id"]][0]].append(row)
        else:
            main_rows.append(row)
    archives = []
    directory = out_path.parent / PMD_DIRECTORY
    if archived:
        directory.mkdir(exist_ok=True)
    emitted = set()
    for event, event_rows in sorted(archived.items()):
        filename = sha256(event.encode()).hexdigest()[:16] + ".json"
        emitted.add(filename)
        (directory / filename).write_text(
            json.dumps(_compact_rows(event_rows), separators=(",", ":")) + "\n"
        )
        event_status: dict[str, int] = defaultdict(int)
        event_classes: dict[str, int] = defaultdict(int)
        for row in event_rows:
            event_status[row["latest"]["status_effective"]] += 1
            event_classes[row["conditions"].get("benchmark_class", "")] += 1
        archives.append(
            {
                "source": "obr_pmd",
                "country": "UK",
                "fiscal_event": event,
                "label": archive_events[event_rows[0]["claim_id"]][1],
                "path": f"data/{PMD_DIRECTORY}/{filename}",
                **_counts(event_rows),
                "by_latest_status": dict(sorted(event_status.items())),
                "by_benchmark_class": dict(sorted(event_classes.items())),
            }
        )
    # Remove only exporter-owned shards which no longer occur in the DB.
    if directory.exists():
        for stale in directory.glob("*.json"):
            if stale.name not in emitted:
                stale.unlink()

    payload = {
        "built": built or date.today().isoformat(),
        "note": (
            "Non-Urban populations exported from scorecard.db: the populace"
            " reform-validation registry (issue #20) plus the compute"
            " campaign's attached comparisons (US: TPC/CPSP/PWBM/CBO/JCT;"
            " UK: the HMRC ready-reckoner family and the complete OBR Policy"
            " measures database, including historical HM Treasury scores;"
            " BE: JRC EUROMOD-BE claims"
            " with demo-grade Axiom concept-mismatch attachments and the"
            " 2026 PIT-reform scorekeeper claims; NZ: official budget"
            " scores). Claims explicitly opted into pre-result display remain"
            " in the feed with latest status not_computed and empty history."
            " Recorded result statuses and calibration relationships are"
            " verbatim; nothing here is a pass/fail grade."
        ),
        "summary": {
            "claims": len(rows),
            "multi_release_claims": multi_release,
            "by_source": dict(sorted(by_source.items())),
            "by_latest_status": dict(sorted(by_status.items())),
            "by_sign_relative_to_pe": dict(sorted(by_sign.items())),
            "by_country": {
                country: _counts(country_rows)
                for country, country_rows in sorted(countries.items())
            },
        },
        "event_archives": archives,
        "rows": main_rows,
    }
    out_path.write_text(json.dumps(payload, indent=1) + "\n")

    n_lanes = 0
    if lanes_path is not None:
        n_lanes = sync_lane_feed(
            db,
            lanes_path,
            payload["built"],
            lanes={
                "populace-reform-validation": {
                    "source": "Populace releases",
                    "area": "reform-validation registry (per-release)",
                    "mode": 2,
                    "country": "US",
                },
                # The UK lane reaches mission control too. The ingest
                # writes it to SQLite either way — as ingested rows or as
                # an explicit "awaiting artifact" row — but the feed only
                # listed the US lane, so both the tracked-feed count and
                # the UK page silently lost it.
                "populace-uk-reform-validation": {
                    "source": "Populace releases",
                    "area": "reform-validation registry (per-release)",
                    "mode": 2,
                    "country": "UK",
                },
            },
        )
    db.close()
    return {
        "rows": len(rows),
        "initial_rows": len(main_rows),
        "event_archives": len(archives),
        "multi_release_claims": multi_release,
        "lanes_synced": n_lanes,
        "out": str(out_path),
    }


if __name__ == "__main__":
    import sys

    db = Path(sys.argv[1] if len(sys.argv) > 1 else "data/scorecard.db")
    print(json.dumps(export(db, lanes_path=REPO / "data" / "lanes.json"), indent=1))
