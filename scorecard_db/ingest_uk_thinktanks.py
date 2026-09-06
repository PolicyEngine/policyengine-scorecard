"""Ingest the two harvested UK think-tank families (#86).

The 2026-08-02 UK sweep staged seven families and only five were ever
ingested (#48's uk_hmrc, uk_dwp, uk_hmt, uk_obr, uk_ukmod_jrf). Two sat
unused with their NOTES.md and manifests beside them:

    sources/harvest-uk-2026-08-02/uk_ifs                    268 rows
    sources/harvest-uk-2026-08-02/uk_resolution_foundation   71 rows

The repo already REFERENCED both while carrying neither —
``baselines.py`` registers ``ifs_2cl_fp_removal_rolled_out`` for an IFS
Green-Budget options world, and ``produce_campaign_uk`` declines four
archived campaign rows because Resolution Foundation is "a long-tail
source (held)". This module is that ingest.

Both are INDEPENDENT models, which is the benchmark class the scorecard
exists for: no pe-uk-data target and no policyengine-uk parameter is
fitted to either (relationships.py carries the evidence, read at the
certified pin), so their rows are held_out and a divergence is a finding
rather than a tautology.

Two honesty problems the staging carries, and how each is handled:

1. **145 of the 339 rows have a null ``metric``** — they carry a
   harvest-side ``proposed_metric`` instead. A proposal is not a
   decision, so DISPOSITIONS below turns every one of them into either a
   registered Metric or a tallied drop with a reason. Nothing is
   inferred at runtime: an unregistered proposal RAISES. The 145 could
   have shrunk silently to zero and nobody would have seen it, which is
   what the exact accounting at the bottom of this module prevents.

2. **8 Resolution Foundation rows are not Resolution Foundation
   claims.** They carry an ``attribution`` naming HM Treasury, a UK
   Parliament impact assessment, or "Government estimate cited by RF",
   and two say so outright in their note ("not an RF model output").
   Staging them under ``resolution_foundation`` would attribute a
   government figure to a think tank and let a PE-vs-RF divergence read
   as disagreement with RF when RF never modelled it. They are dropped
   here; re-publishing them correctly means staging them under their
   ORIGINATOR, which is its own harvest decision, not this one.

Same contract as ingest_uk_externals (scorecard_db/README.md): fail
loudly on any unmapped metric, unknown identity value or unhandled
staged field; values arrive in raw units and are NEVER re-derived here;
calibration_relationship is decided in relationships.py.

Usage:
    PYTHONPATH=. python -m scorecard_db.ingest_uk_thinktanks data/scorecard.db
"""

from __future__ import annotations

import gzip
import json
from pathlib import Path

from .db import LANE_SQL, SCORES_SQL, ScorecardDB
from .harvest import REPO, finish, policy_ref, with_baseline_condition
from .models import ExternalScore, Metric, ReformRef, TimeBasis, UnitConcept
from .relationships import uk_relationship
from .uk_aliases import canon

HARVEST = REPO / "sources" / "harvest-uk-2026-08-02"

# harvest family dir -> (DB source id, display name)
FAMILIES = {
    "uk_ifs": "ifs",
    "uk_resolution_foundation": "resolution_foundation",
}

LANE_ID = "uk-thinktanks"
LANE_UPDATED = "2026-08-24"
# The UK family's shared top-level feed literal (sync_lane_feed's
# contract: every caller in a build passes the same one).
FEED_UPDATED = "2026-08-19"
LANE_FEED_META = {
    "source": "IFS + Resolution Foundation",
    "area": "independent UK tax-benefit modelling",
    "mode": 2,
    "country": "UK",
}

# --- the disposition table --------------------------------------------------
# Every metric name the staging can present — its own `metric` or, where
# that is null, its `proposed_metric` — maps to exactly one of:
#
#   a Metric        ingest it under that registered metric
#   a DROP reason   do not ingest, and TALLY it with the reason
#
# An unlisted name raises. A proposal is a suggestion from the harvest;
# this table is where it becomes a decision.
DISPOSITIONS: dict[str, Metric] = {
    # already-registered metrics, carried straight through
    "poverty_rate": Metric.POVERTY_RATE,
    "poverty_rate_change": Metric.POVERTY_RATE_CHANGE,
    "poverty_count": Metric.POVERTY_COUNT,
    "poverty_count_change": Metric.POVERTY_COUNT_CHANGE,
    "revenue_change": Metric.REVENUE_CHANGE,
    # proposals adopted onto existing metrics
    #   both count families made better off by a reform; the IFS row's
    #   own sign_convention says "count of families gaining"
    "families_affected_count": Metric.GAINER_COUNT,
    "benefiting_family_count": Metric.GAINER_COUNT,
    "avg_gain_per_benefiting_family": Metric.AVERAGE_ANNUAL_GAIN,
    #   an exchequer cost is a revenue change; the published sign
    #   convention rides in conditions and the value is NOT re-signed here
    "reform_fiscal_cost": Metric.REVENUE_CHANGE,
    # proposals adopted onto the new sibling metrics (see models.py)
    "avg_change_household_net_income": Metric.AVERAGE_HOUSEHOLD_INCOME_CHANGE,
    "avg_income_change": Metric.AVERAGE_HOUSEHOLD_INCOME_CHANGE,
    "benefit_spending_change": Metric.BENEFIT_COST_CHANGE,
    "taxpayer_count_change": Metric.TAXPAYER_COUNT_CHANGE,
    "share_gaining": Metric.SHARE_GAINING,
    "share_losing": Metric.SHARE_LOSING,
    "share_of_spending_to_group": Metric.SPENDING_SHARE,
    "benefit_uprating_pct": Metric.BENEFIT_UPRATING_RATE,
    "real_income_growth_pct": Metric.REAL_INCOME_GROWTH,
    #   the same quantity expressed per annum: a window_kind condition,
    #   not a different metric
    "real_income_growth_pct_pa": Metric.REAL_INCOME_GROWTH,
    "real_value_change_pct": Metric.REAL_INCOME_GROWTH,
}

DROPS: dict[str, str] = {
    "cost_per_child_lifted_out_of_poverty": (
        "A RATIO of two other published quantities (programme cost divided "
        "by the poverty-count change). PolicyEngine could only 'answer' it "
        "by dividing two of its own numbers, which would make agreement "
        "mechanical rather than evidential — and the two inputs are already "
        "staged as claims in their own right."
    ),
    "benefit_rate_gap_weekly": (
        "A gap between two published statutory rates, i.e. derived from two "
        "quantities neither of which is staged here. Stage the rates and "
        "let the gap be a downstream derivation."
    ),
    "inflation_rate_gap_pp": (
        "A gap between two published rates, derived; same rule as "
        "benefit_rate_gap_weekly."
    ),
    "benefit_rate_weekly": (
        "A statutory weekly benefit RATE, which has no sibling metric in "
        "this repo (average_weekly_benefit is an average of actual "
        "receipts, a different quantity). One row does not justify minting "
        "a metric; deferred deliberately rather than mapped to a "
        "near-neighbour."
    ),
    "avg_gain_per_unit": (
        "The denominator population is unstated in the staging ('per "
        "unit'), so the number cannot be given an identity. A per-unit "
        "statistic whose unit is unknown is not a claim."
    ),
}

# Rows whose `attribution` names a third party are that party's claims,
# not the publisher's (see the module docstring).
THIRD_PARTY_DROP = (
    "Re-published third-party figure: the staged row carries an "
    "`attribution` naming its true originator (HM Treasury, a UK "
    "Parliament impact assessment, or a Government estimate cited by the "
    "publisher). Staging it under the publisher would attribute a "
    "government number to a think tank, and a PE divergence against it "
    "would read as disagreement with a model that never produced it. "
    "Re-publishing it correctly means staging it under its originator, "
    "which is a separate harvest decision."
)

_ADOPTED = frozenset(DISPOSITIONS)
_DROPPED = frozenset(DROPS)
assert not (_ADOPTED & _DROPPED), "a metric is adopted or dropped, never both"

# Adapter unit label -> DB unit concept. Closed: an unregistered unit
# raises rather than landing a number under a unit nobody chose.
UNITS = {
    "gbp": UnitConcept.GBP,
    "gbp_per_year": UnitConcept.GBP,
    "share": UnitConcept.SHARE,
    "percent": UnitConcept.PERCENT,
    "percentage_points": UnitConcept.PERCENT,
    "persons": UnitConcept.PERSONS,
    "families": UnitConcept.FAMILIES,
    "children_under_18": UnitConcept.CHILDREN_UNDER_18,
}

TIME_BASES = {
    "annual": TimeBasis.ANNUAL,
    "fiscal_year": TimeBasis.FISCAL_YEAR,
    "point_in_time": TimeBasis.POINT_IN_TIME,
    "average_month": TimeBasis.AVERAGE_MONTH,
}


# Staged fields this module understands. An unknown field raises: a new
# harvest column is handled here DELIBERATELY or not at all.
_KNOWN_FIELDS = frozenset(
    {
        "attribution",
        "calibration_relationship",
        "conditions",
        "geography_note",
        "local_artifact",
        "metric",
        "normalization",
        "note",
        "parse_confidence",
        "period",
        "proposed_metric",
        "proposed_unit",
        "publication",
        "reform_hint",
        "sign_convention",
        "source",
        "source_column",
        "source_model",
        "source_table",
        "status",
        "time_basis",
        "unit_concept",
        "value",
        "value_kind",
        # the publication's own rendering ("£2.4 billion", "560,000
        # families"), kept as provenance beside the parsed number
        "value_raw",
    }
)

# Condition keys whose values are closed identities (uk_aliases); every
# other staged condition is descriptive provenance and travels verbatim.
_CANONICALISED = {"geography", "program", "income_group", "benefit"}


def _load(family: str) -> list[dict]:
    path = HARVEST / family / "claims_staged.jsonl.gz"
    if not path.exists():
        raise FileNotFoundError(f"{path} missing — the harvest family is not vendored")
    rows = []
    for line in gzip.open(path, "rt"):
        row = json.loads(line)
        unknown = sorted(set(row) - _KNOWN_FIELDS)
        if unknown:
            raise ValueError(
                f"{family}: unhandled staged fields {unknown} — handle them "
                "deliberately or not at all"
            )
        rows.append(row)
    return rows


def _metric_name(row: dict) -> str:
    """The name this row presents: its own metric, else its PROPOSAL.

    A proposal is a suggestion from the harvest, never a decision — it
    only reaches a claim through DISPOSITIONS.
    """
    name = row.get("metric") or row.get("proposed_metric")
    if not name:
        raise ValueError(
            f"staged row carries neither metric nor proposed_metric: "
            f"{row.get('source_column')!r}"
        )
    return name


def _reform(row: dict, source: str) -> ReformRef:
    """The world the row scores.

    A row with a reform_hint is a REFORM score and names the world; a row
    without one is a level or a projection of the current world.
    """
    hint = row.get("reform_hint")
    if not hint:
        return ReformRef()
    baseline = None
    conditions = row.get("conditions") or {}
    # The IFS Green-Budget options are scored against a registered
    # non-current-law world (baselines.py), which the staging names in
    # its own conditions rather than in the hint.
    if conditions.get("counterfactual", "").startswith("current tax-benefit system"):
        baseline = {"policy": "ifs_2cl_fp_removal_rolled_out"}
    return policy_ref(f"{source}:{hint[:120]}", baseline=baseline)


def stage() -> tuple[list[ExternalScore], dict]:
    """Stage every ingestible row; nothing touches the DB here.

    Returns (scores, accounting) where accounting reconciles EVERY staged
    row: read = ingested + dropped, by reason.
    """
    scores: list[ExternalScore] = []
    acct = {
        "read": 0,
        "ingested": 0,
        "dropped": 0,
        "by_family": {},
        "drops": {},
    }
    for family, source in FAMILIES.items():
        rows = _load(family)
        acct["read"] += len(rows)
        fam_stats = {"read": len(rows), "ingested": 0, "dropped": 0}
        for row in rows:
            if row["source"] != source:
                raise ValueError(
                    f"{family}: row source {row['source']!r} is not {source!r}"
                )
            name = _metric_name(row)
            # A third-party figure is its originator's claim, not this
            # publisher's — checked BEFORE the metric disposition, so an
            # otherwise-ingestible metric cannot smuggle one in.
            if row.get("attribution"):
                _drop(acct, fam_stats, "third_party_attribution", THIRD_PARTY_DROP)
                continue
            if name in DROPS:
                _drop(acct, fam_stats, name, DROPS[name])
                continue
            if name not in DISPOSITIONS:
                raise ValueError(
                    f"{family}: metric {name!r} has no disposition — decide it "
                    "in DISPOSITIONS or DROPS deliberately; a proposal is not "
                    "a decision"
                )
            scores.append(_score(row, source, DISPOSITIONS[name]))
            fam_stats["ingested"] += 1
            acct["ingested"] += 1
        acct["by_family"][source] = fam_stats
    acct["dropped"] = acct["read"] - acct["ingested"]
    if acct["ingested"] + acct["dropped"] != acct["read"]:  # pragma: no cover
        raise ValueError("accounting does not close")
    return finish(scores, "uk_thinktanks"), acct


def _drop(acct: dict, fam_stats: dict, reason_key: str, reason: str) -> None:
    entry = acct["drops"].setdefault(reason_key, {"rows": 0, "reason": reason})
    entry["rows"] += 1
    fam_stats["dropped"] += 1


def _score(row: dict, source: str, metric: Metric) -> ExternalScore:
    unit_label = row.get("unit_concept") or row.get("proposed_unit")
    if unit_label is None:
        raise ValueError(
            f"{source}: {metric.value} row carries no unit — a number without "
            f"a unit is not a claim ({row.get('source_column')!r})"
        )
    canon(source, "unit", unit_label)
    if unit_label not in UNITS:
        raise ValueError(f"{source}: unregistered unit {unit_label!r}")
    unit = UNITS[unit_label]

    staged_conditions = dict(row.get("conditions") or {})
    cond: dict[str, str] = {"country": "UK"}
    for key, value in staged_conditions.items():
        if key in _CANONICALISED:
            cond[key] = canon(source, key, value)
            if cond[key] != value:
                # the publication's own wording survives as provenance
                cond[f"{key}_verbatim"] = value
        else:
            cond[key] = value
    if row.get("geography_note"):
        cond["geography_note"] = row["geography_note"]
    if row.get("sign_convention"):
        cond["sign_convention"] = row["sign_convention"]
    if row.get("value_raw") is not None:
        # Some families stage the raw rendering as a number rather than a
        # string ("207" vs "£2.4 billion"); conditions are str->str.
        cond["value_verbatim"] = str(row["value_raw"])
    # "per annum" is a window shape, not a different quantity
    if row.get("proposed_metric") in ("real_income_growth_pct_pa",):
        cond["window_kind"] = "annual_average"

    basis = TIME_BASES.get(row.get("time_basis"))
    if basis is None:
        raise ValueError(f"{source}: unregistered time_basis {row.get('time_basis')!r}")

    reform = _reform(row, source)
    with_baseline_condition(cond, reform)
    return ExternalScore(
        source=source,
        metric=metric,
        unit_concept=unit,
        period=int(row["period"]),
        time_basis=basis,
        value=float(row["value"]),
        conditions=cond,
        reform=reform,
        calibration_relationship=uk_relationship(source, metric)[0],
        source_model=row.get("source_model") or source,
        source_column=row.get("source_column") or "",
        publication=row.get("publication") or {},
        value_kind=row.get("value_kind") or unit.value,
        status="ok",
    )


# Exact accounting for the committed harvest. A drifted re-stage must
# fail HERE, never grow or shrink the catalog silently — and in
# particular the 145 proposal-only rows must never quietly become zero.
_EXPECTED = {
    "read": 339,
    "ingested": 314,
    "dropped": 25,
    "drops": {
        "cost_per_child_lifted_out_of_poverty": 12,
        "third_party_attribution": 8,
        "benefit_rate_gap_weekly": 2,
        "avg_gain_per_unit": 1,
        "benefit_rate_weekly": 1,
        "inflation_rate_gap_pp": 1,
    },
}


def check_accounting(acct: dict) -> None:
    got = {
        "read": acct["read"],
        "ingested": acct["ingested"],
        "dropped": acct["dropped"],
        "drops": {k: v["rows"] for k, v in acct["drops"].items()},
    }
    if got != _EXPECTED:
        raise ValueError(f"claim accounting drifted: {got} != {_EXPECTED}")


def ingest(db_path: Path) -> dict:
    """Stage and validate first; then ONE transaction replaces both
    sources wholesale and runs the baseline-registration gate inside it,
    exactly as ingest_uk_externals does."""
    scores, acct = stage()
    check_accounting(acct)
    db = ScorecardDB(db_path)
    rows = [ScorecardDB.score_row(s) for s in scores]

    from .baselines import register_baselines_txn
    from .ingest_harvest import sync_lane_feed

    with db.conn:
        for source in FAMILIES.values():
            db.conn.execute("DELETE FROM external_scores WHERE source = ?", (source,))
        db.conn.executemany(SCORES_SQL, rows)
        register_baselines_txn(db)
        detail = (
            f"{acct['ingested']} claims from {len(FAMILIES)} independent "
            f"models ({acct['read']} staged rows = {acct['ingested']} ingested "
            f"+ {acct['dropped']} tallied drops)"
        )
        db.conn.execute(LANE_SQL, (LANE_ID, "ingested", detail, LANE_UPDATED))
    sync_lane_feed(
        db,
        REPO / "data" / "lanes.json",
        FEED_UPDATED,
        lanes={LANE_ID: LANE_FEED_META},
    )
    db.close()
    return {
        "claims": len(rows),
        **{k: v for k, v in acct.items() if k != "drops"},
        "drops": {k: v["rows"] for k, v in acct["drops"].items()},
    }


if __name__ == "__main__":
    import sys

    out = Path(sys.argv[1] if len(sys.argv) > 1 else "data/scorecard.db")
    print(json.dumps(ingest(out), indent=1))
