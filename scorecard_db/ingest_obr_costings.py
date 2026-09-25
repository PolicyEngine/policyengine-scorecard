"""Ingest the OBR-certified measure costings the mode-2 lane scores (#54, #56).

The external side of PR #56's lane: the 621-row slice of the OBR Policy
Measures Database (November 2025 vintage; 552 rows) and the EFO March 2026
Table 3.17 re-estimates (69 rows) that `data/uk/obr_measure_reforms.yaml`
scores, vendored at `sources/harvest-20260802/uk_obr/obr_costings_claims.jsonl`
and derived from the repository's own harvest by
`pipeline/select_obr_costings_claims.py` (exact tally, `--check`).

Gate round 1 on #56 asked for four things this module supplies:
  * a registered ingestor in the build chain, one transaction, exact
    accounting, lane row, feed sync, idempotent (finding 2);
  * a closed identity — every condition key in STANDARD_CONDITIONS,
    `exchequer_impact` carried as REVENUE_CHANGE with the fiscal measure
    named, and claims keyed to the FY END year (finding 4);
  * the relationship derived from relationships.py, never copied (5);
  * announcement-time baselines: every row names the registered world
    OBR scored it against — that round's pre-measures forecast for PMD
    rows, the indexed-thresholds counterfactual for the March 2026
    re-estimates — so the #13 guard can compare it with the world PE
    executed (finding 1, claim side; the result side is the staging
    resolver, produce_obr_costings).

Two producer slugs, one registry mark. PMD rows are HM Treasury's
scorecard as certified by the OBR (`obr_pmd`); Table 3.17 rows are the
OBR's own forecast tables (`obr_efo`, the slug the AB2025 EFO tables
already use). Deletion is by the registry mark, never by slug: `obr_efo`
also carries the #136 rows.

Retrieval by measure: an Autumn Budget 2025 measure carries the #136
registry key (`conditions.measure_key = ab2025__…`, joined through the
registry's `obr_pmd_measure_key`) so the OBR leg sits beside HM
Treasury's, the IFS's and RF's on one reform key per baseline world;
every row also carries `obr_measure_key`, the YAML registry's own key.
"""

from __future__ import annotations

import json
from pathlib import Path

from .baselines import BASELINES
from .db import LANE_SQL, SCORES_SQL, ScorecardDB
from .harvest import REPO, finish, policy_ref, require_fields, with_baseline_condition
from .models import (
    BASELINE,
    ExternalScore,
    Metric,
    TimeBasis,
    UnitConcept,
    baseline_key,
)
from .relationships import uk_relationship

SLICE = REPO / "sources" / "harvest-20260802" / "uk_obr" / "obr_costings_claims.jsonl"
INDEX = REPO / "sources" / "harvest-20260802" / "uk_obr" / "obr_costings_measures.json"
AB2025_REGISTRY = REPO / "data" / "uk" / "ab2025_measures.json"

REGISTRY_MARK = "obr_costings"
FAMILY = "uk_obr_costings"
SOURCE_PMD = "obr_pmd"
SOURCE_EFO = "obr_efo"
LANE_ID = "uk-obr-costings"
LANE_UPDATED = "2026-09-25"
# The UK family's shared top-level feed literal (sync_lane_feed's contract).
FEED_UPDATED = "2026-08-19"
LANE = {
    LANE_ID: {
        "source": "OBR Policy Measures Database and EFO March 2026 Table 3.17",
        "area": "OBR-certified costings of the measures data/uk/obr_measure_reforms.yaml scores (#56)",
        "mode": 2,
        "country": "UK",
    }
}

PMD_TABLES = frozenset(
    {
        "Tax Measures (Policy measures database)",
        "Spending Measures (Policy measures database)",
    }
)
EFO_317 = "3.17: 3.17"
# Verbatim PMD event names -> the closed slugs the OBR policy-effects
# ingest already uses (retrieval by event joins across the two).
EVENTS = {
    "Autumn Statement 2023": "autumn_statement_2023",
    "Spring Budget 2024": "spring_budget_2024",
    "Autumn Budget 2024": "autumn_budget_2024",
    "Autumn Budget 2025": "autumn_budget_2025",
}
EFO_EVENT = "march_2026_efo"
# The world OBR scores a round's measures against: that round's
# pre-measures forecast, legislated-parameter counterfactual (registered
# by #81). The March 2026 re-estimates are measured against the
# indexed-thresholds counterfactual (registered by #67).
EVENT_BASELINE = {
    slug: {"policy": f"obr_pre_measures_{slug}", "counterfactual": "policy_parameters"}
    for slug in EVENTS.values()
}
EFO_BASELINE = {"policy": "obr_announcement_baseline_efo_march_2026"}
METRICS = {
    "revenue_change": Metric.REVENUE_CHANGE,
    "exchequer_impact": Metric.REVENUE_CHANGE,
}
ACTION_LINK_LANE = "https://github.com/PolicyEngine/policyengine-scorecard/issues/54"

_KNOWN_FIELDS = frozenset(
    {
        "calibration_relationship",
        "conditions",
        "metric",
        "normalization",
        "period",
        "proposed_metric",
        "proposed_unit",
        "publication",
        "reform_hint",
        "source",
        "source_column",
        "source_model",
        "source_table",
        "status",
        "time_basis",
        "value",
        "value_raw",
    }
)
_KNOWN_CONDITIONS = frozenset(
    {
        "geography",
        "fy",
        "fiscal_event",
        "tax_head",
        "spending_head",
        "impact_channel",
        "basis",
        "costing_phase",
        "sign_convention",
        "line_item",
        "note",
    }
)
EXPECTED = {
    "read": 621,
    "ingested": 621,
    "by_source": {SOURCE_PMD: 552, SOURCE_EFO: 69},
}

_BASELINE_BY_LABEL: dict[str, dict] = {label: desc for desc, label, *_ in BASELINES}
_REGISTERED_KEYS = frozenset(baseline_key(desc) for desc, *_ in BASELINES)
_CURRENT_LAW_KEY = BASELINE.baseline_key()


def measures() -> dict[str, dict]:
    return {m["measure_key"]: m for m in json.loads(INDEX.read_text())["measures"]}


def _ab2025_join() -> dict[str, dict]:
    """obr_pmd_measure_key -> the #136 registry measure."""
    reg = json.loads(AB2025_REGISTRY.read_text())["measures"]
    return {m["obr_pmd_measure_key"]: m for m in reg if m.get("obr_pmd_measure_key")}


def load_rows() -> list[dict]:
    return [json.loads(line) for line in SLICE.read_text().splitlines() if line.strip()]


def measure_for(row: dict, index: dict[str, dict]) -> dict:
    """The registry measure a slice row belongs to, by the selector's rule."""
    table = row.get("source_table")
    event = (row.get("conditions") or {}).get("fiscal_event")
    for m in index.values():
        if row.get("reform_hint") != m["obr_description"]:
            continue
        if table == EFO_317 and m["source_table"] == EFO_317:
            return m
        if table in PMD_TABLES and event == m["fiscal_event"]:
            return m
    raise ValueError(
        f"{REGISTRY_MARK}: no registry measure for {row.get('reform_hint')!r} "
        f"({table}, {event}) — the slice and the registry drifted"
    )


def executed_world_key(measure_key: str, index: dict[str, dict] | None = None) -> str:
    """The registered world PE EXECUTES for a measure's result (the
    result-side half of finding 1).

    A reversal on the certified world executes the pre-measure world:
    the #136 `pre_ab2025__*` worlds for the Autumn Budget 2025 measures,
    the `pre_<key>` worlds registered here for the earlier events, and
    the indexed-thresholds counterfactual for the PA/HRT re-estimate. A
    forward delta, or a measure with no reform, executes current law.
    """
    index = index or measures()
    m = index[measure_key]
    if m["construction"] != "reversal_on_certified_world" or not m["has_pe_reform"]:
        return _CURRENT_LAW_KEY
    if measure_key == "efo_march_2026__pa_and_hrt_freezes":
        return baseline_key(EFO_BASELINE)
    if measure_key.startswith("autumn_budget_2025__"):
        ab = _ab2025_join()[measure_key]
        slug = ab["measure_key"].removeprefix("ab2025__")
        label = f"pre_ab2025__{slug}"
        if label not in _BASELINE_BY_LABEL:
            if slug != "uc_child_element_remove_two_child_limit":
                raise ValueError(
                    f"{measure_key}: no registered pre-Budget world {label!r}"
                )
            label = "pre_ab2025"
        return baseline_key(_BASELINE_BY_LABEL[label])
    label = f"pre_{measure_key}"
    if label not in _BASELINE_BY_LABEL:
        raise ValueError(f"{measure_key}: executed world {label!r} is not registered")
    return baseline_key(_BASELINE_BY_LABEL[label])


def _score(
    row: dict, index: dict[str, dict], ab_join: dict[str, dict]
) -> ExternalScore:
    require_fields(row, _KNOWN_FIELDS, REGISTRY_MARK)
    if row.get("source") != "obr":
        raise ValueError(f"{REGISTRY_MARK}: slice row source {row.get('source')!r}")
    m = measure_for(row, index)
    table = row["source_table"]
    source = SOURCE_EFO if table == EFO_317 else SOURCE_PMD

    staged = dict(row.get("conditions") or {})
    unknown = set(staged) - _KNOWN_CONDITIONS
    if unknown:
        raise ValueError(
            f"{REGISTRY_MARK}: unregistered condition keys {sorted(unknown)}"
        )
    cond: dict = {"country": "UK"}
    cond.update(staged)
    if source == SOURCE_EFO:
        if "fiscal_event" in staged:
            raise ValueError(
                f"{REGISTRY_MARK}: a Table 3.17 row carries a fiscal_event"
            )
        cond["fiscal_event"] = EFO_EVENT
        baseline = EFO_BASELINE
    else:
        slug = EVENTS.get(staged.get("fiscal_event"))
        if slug is None:
            raise ValueError(
                f"{REGISTRY_MARK}: unregistered fiscal_event {staged.get('fiscal_event')!r}"
            )
        cond["fiscal_event"] = slug
        baseline = EVENT_BASELINE[slug]
    if baseline_key(baseline) not in _REGISTERED_KEYS:
        raise ValueError(
            f"{REGISTRY_MARK}: baseline {baseline!r} is not a registered world"
        )

    # claims key the FY END year (#48/#52); the slice carries the start year
    fy = cond["fy"]
    start = int(fy[:4])
    if int(row["period"]) != start or fy != f"{start}-{(start + 1) % 100:02d}":
        raise ValueError(
            f"{REGISTRY_MARK}: period {row['period']} does not open fy {fy!r}"
        )
    period = start + 1

    name = row.get("metric") or row.get("proposed_metric")
    if name not in METRICS:
        raise ValueError(f"{REGISTRY_MARK}: unregistered metric {name!r}")
    metric = METRICS[name]
    if name == "exchequer_impact":
        cond["fiscal_measure"] = "exchequer_impact"
    if row.get("proposed_unit", "gbp") != "gbp":
        raise ValueError(f"{REGISTRY_MARK}: unit {row.get('proposed_unit')!r}")
    if row.get("time_basis") != "fiscal_year":
        raise ValueError(f"{REGISTRY_MARK}: time_basis {row.get('time_basis')!r}")

    cond["value_verbatim"] = str(row["value_raw"])
    cond["benchmark_class"] = "different_model"
    cond["obr_measure_key"] = m["measure_key"]
    ab = ab_join.get(m["measure_key"])
    if ab is not None:
        cond["measure_key"] = ab["measure_key"]
        cond["pe_expressibility"] = ab["computability"]
        gap = ab.get("missing") or ab.get("why")
        if gap:
            cond["pe_missing"] = gap
        if ab.get("action_link"):
            cond["action_link"] = ab["action_link"]
    else:
        cond["measure_key"] = m["measure_key"]
        cond["pe_expressibility"] = m["computability"]
        if m["computability"] == "not_expressible":
            cond["pe_missing"] = m["notes"]
            cond["action_link"] = ACTION_LINK_LANE
    reform = policy_ref(cond["measure_key"], baseline=baseline)
    with_baseline_condition(cond, reform)

    pub = dict(row.get("publication") or {})
    pub.update(
        {
            "registry": REGISTRY_MARK,
            "family": FAMILY,
            "table": table,
            "publish_without_result": True,
        }
    )
    return ExternalScore(
        source=source,
        metric=metric,
        unit_concept=UnitConcept.GBP,
        period=period,
        time_basis=TimeBasis.FISCAL_YEAR,
        value=float(row["value"]),
        conditions=cond,
        reform=reform,
        calibration_relationship=uk_relationship(source, metric, kind="forecast")[0],
        source_model=row["source_model"],
        source_column=row.get("source_column") or "",
        publication=pub,
        value_kind=UnitConcept.GBP.value,
        status="ok",
    )


def stage() -> tuple[list[ExternalScore], dict]:
    index = measures()
    ab_join = _ab2025_join()
    rows = load_rows()
    scores = [_score(r, index, ab_join) for r in rows]
    by_source: dict[str, int] = {}
    for s in scores:
        by_source[s.source] = by_source.get(s.source, 0) + 1
    acct = {"read": len(rows), "ingested": len(scores), "by_source": by_source}
    if acct != EXPECTED:
        raise ValueError(
            f"{REGISTRY_MARK}: accounting drifted: {acct} != {EXPECTED} — "
            "re-derive the slice (pipeline/select_obr_costings_claims.py) and "
            "re-pin deliberately"
        )
    return finish(scores, REGISTRY_MARK), acct


def claim_ids() -> dict[str, str]:
    """descriptor JSON (source, metric, period, source_table, reform_hint,
    conditions — the exact form the compute pipeline stages) -> claim_id."""
    index = measures()
    ab_join = _ab2025_join()
    out: dict[str, str] = {}
    for row in load_rows():
        desc = json.dumps(
            {
                "source": row["source"],
                "metric": row.get("metric") or row.get("proposed_metric"),
                "period": row["period"],
                "source_table": row["source_table"],
                "reform_hint": row["reform_hint"],
                "conditions": row["conditions"],
            },
            sort_keys=True,
        )
        if desc in out:
            raise ValueError(
                f"{REGISTRY_MARK}: two slice rows share a descriptor: {desc}"
            )
        out[desc] = _score(row, index, ab_join).claim_id()
    return out


def ingest(db_path: Path) -> dict:
    scores, acct = stage()
    db = ScorecardDB(db_path)
    rows = [ScorecardDB.score_row(s) for s in scores]

    from .baselines import register_baselines_txn
    from .ingest_harvest import sync_lane_feed

    with db.conn:
        db.conn.execute(
            "DELETE FROM external_scores WHERE json_extract(publication, '$.registry') = ?",
            (REGISTRY_MARK,),
        )
        db.conn.executemany(SCORES_SQL, rows)
        register_baselines_txn(db)
        detail = (
            f"{acct['ingested']} claims ({acct['by_source'][SOURCE_PMD]} Policy "
            f"Measures Database rows + {acct['by_source'][SOURCE_EFO]} EFO March 2026 "
            f"Table 3.17 rows; {acct['read']} slice rows = {acct['ingested']} ingested)"
        )
        db.conn.execute(LANE_SQL, (LANE_ID, "ingested", detail, LANE_UPDATED))
    sync_lane_feed(db, REPO / "data" / "lanes.json", FEED_UPDATED, lanes=LANE)
    db.close()
    return {"claims": len(rows), **acct}


if __name__ == "__main__":
    import sys

    print(
        json.dumps(
            ingest(Path(sys.argv[1] if len(sys.argv) > 1 else "data/scorecard.db")),
            indent=1,
        )
    )
