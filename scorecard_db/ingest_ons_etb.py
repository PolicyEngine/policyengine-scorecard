"""Ingest the ONS effects-of-taxes-and-benefits population (#90).

The distributional-incidence lane HM Treasury could not be: #68 emits
zero value claims because HMT publishes its decile impacts as unlabeled
chart bars. ONS publishes observations, so this lane carries numbers.

2,640 claims, one per (income concept x quintile group x statistic x
period). The harvest side (sources/ons-etb/adapter.py) explains the two
decisions that shape the population — the mixed calendar/financial time
dimension, and the dropped deflated half whose price base is published
nowhere.

Same contract as ingest_uk_externals (scorecard_db/README.md): fail
loudly on any unmapped metric, unknown identity value or unhandled
adapter field; values arrive in raw units and are NEVER re-derived here;
calibration_relationship is decided in relationships.py.

What this lane deliberately does NOT claim: that PolicyEngine can answer
all of it. `final` income includes benefits in kind — health, education,
housing subsidy — which PE-UK has no counterpart for, and `post_tax`
needs an indirect-tax total PE-UK exposes only as separate heads. Those
are coverage facts about the counterpart side, recorded on the claims as
`pe_expressibility` so a later compute lane reads them off the row
instead of rediscovering them.

    PYTHONPATH=. python -m scorecard_db.ingest_ons_etb data/scorecard.db
"""

from __future__ import annotations

import json
from pathlib import Path

from .db import LANE_SQL, SCORES_SQL, ScorecardDB
from .harvest import REPO, finish, require_fields
from .models import ExternalScore, Metric, TimeBasis, UnitConcept
from .relationships import uk_relationship
from .uk_aliases import canon

EXTERNALS = REPO / "data" / "externals"

ADAPTER_SOURCE = "ons-etb"
SOURCE = "ons_etb"
LANE_ID = "ons-etb"
LANE_UPDATED = "2026-08-24"
# The UK family's shared top-level feed literal (sync_lane_feed contract).
FEED_UPDATED = "2026-08-19"
LANE_FEED_META = {
    "source": "ONS",
    "area": "effects of taxes and benefits on household income",
    "mode": 1,
    "country": "UK",
}

PUBLICATION = {
    "title": (
        "ONS Effects of Taxes and Benefits on Household Income "
        "(dataset tax-benefits-statistics, edition time-series, version 3)"
    ),
    "url": "https://static.ons.gov.uk/datasets/tax-benefits-statistics-time-series-v3.csv",
    "date": "2022-09-09",
    "country": "UK",
}

# The ranking axis, recorded once. The dataset labels its dimension only
# "Quintile"; that the ranking is by equivalised disposable income on the
# modified-OECD scale comes from the ETB Quality and Methodology
# Information (stable across editions), cited in source.json.
INCOME_AXIS = "equivalised_disposable_income_quintile"

# How far PolicyEngine-UK can follow each income concept. Recorded on the
# CLAIM so a counterpart lane reads it off the row rather than
# rediscovering it — and so a `final`-income divergence can never be
# reported as an engine defect when it is a coverage gap.
EXPRESSIBILITY = {
    "original": "expressible",
    "gross": "expressible",
    "disposable": "expressible",
    # PE-UK has vat and the individual duties but no single indirect-tax
    # aggregate, so a counterpart must sum the heads explicitly.
    "post_tax": "partial",
    # Benefits in kind (health, education, housing subsidy, travel
    # subsidies, school meals) have no PE-UK counterpart at all.
    "final": "not_expressible",
}
NOT_EXPRESSIBLE_ACTION = (
    "https://github.com/PolicyEngine/policyengine-scorecard/issues/90"
)

_KNOWN_FIELDS = frozenset(
    {
        "country",
        "dataset_version",
        "fy",
        "geography",
        "income_concept",
        "metric",
        "period",
        "program",
        "quantile",
        "source",
        "source_column",
        "statistic",
        "status",
        "time_basis",
        "unit_concept",
        "value",
    }
)

_METRICS = {"income_statistic": (Metric.INCOME_STATISTIC, UnitConcept.GBP, "gbp")}
_TIME_BASES = {"annual": TimeBasis.ANNUAL, "fiscal_year": TimeBasis.FISCAL_YEAR}


def _load() -> list[dict]:
    path = EXTERNALS / f"{ADAPTER_SOURCE}.json"
    if not path.exists():
        raise FileNotFoundError(
            f"{path} missing — run sources/ons-etb/adapter.py first"
        )
    rows = json.loads(path.read_text())
    for row in rows:
        require_fields(row, _KNOWN_FIELDS, SOURCE)
        if row["source"] != ADAPTER_SOURCE:
            raise ValueError(f"{SOURCE}: row source {row['source']!r} is wrong")
        if row["country"] != "UK":
            raise ValueError(f"{SOURCE}: row country {row['country']!r} is not 'UK'")
    return rows


def stage() -> tuple[list[ExternalScore], dict]:
    scores: list[ExternalScore] = []
    counts: dict[str, dict[str, int]] = {}
    for row in _load():
        metric, unit, value_kind = _METRICS[row["metric"]]
        staged_unit = canon(SOURCE, "unit", row["unit_concept"])
        if staged_unit != "gbp_nominal":
            raise ValueError(f"{SOURCE}: unexpected unit {staged_unit!r}")
        concept = canon(SOURCE, "income_concept", row["income_concept"])
        cond = {
            "country": "UK",
            "geography": canon(SOURCE, "geography", row["geography"]),
            "program": canon(SOURCE, "program", row["program"]),
            "income_concept": concept,
            "income_axis": INCOME_AXIS,
            "quantile": canon(SOURCE, "quantile", row["quantile"]),
            # How far PE-UK can follow this concept, on the claim itself.
            "pe_expressibility": EXPRESSIBILITY[concept],
        }
        statistic = canon(SOURCE, "statistic", row["statistic"])
        # repo convention (models.py): absent means mean
        if statistic != "mean":
            cond["statistic"] = statistic
        if row["fy"] is not None:
            cond["fy"] = row["fy"]
        if EXPRESSIBILITY[concept] == "not_expressible":
            # Descriptive gate #9: a coverage gap is a finding only if it
            # is citable.
            cond["action_link"] = NOT_EXPRESSIBLE_ACTION
        basis = _TIME_BASES[row["time_basis"]]
        scores.append(
            ExternalScore(
                source=SOURCE,
                metric=metric,
                unit_concept=unit,
                period=int(row["period"]),
                time_basis=basis,
                value=float(row["value"]),
                conditions=cond,
                calibration_relationship=uk_relationship(SOURCE, metric)[0],
                source_model="ons_etb",
                source_column=row["source_column"],
                publication=PUBLICATION,
                value_kind=value_kind,
                status=row["status"],
            )
        )
        # keyed as a tuple, never a joined string: "post_tax" would split
        # back into "post" and quietly break the accounting
        counts.setdefault(concept, {}).setdefault(basis.value, 0)
        counts[concept][basis.value] += 1
    return finish(scores, SOURCE), counts


# Exact accounting for the committed adapter output. 2,640 = 5 income
# concepts x 6 quintile groups x 2 statistics x 44 periods, of which 17
# are calendar years (1977-1993) and 27 financial years (1994-95 on).
_EXPECTED_TOTAL = 2640
_EXPECTED_PER_CONCEPT = 528


def ingest(db_path: Path) -> dict:
    scores, counts = stage()
    if len(scores) != _EXPECTED_TOTAL:
        raise ValueError(
            f"claim accounting drifted: {len(scores)} != {_EXPECTED_TOTAL}"
        )
    by_concept = {c: sum(v.values()) for c, v in counts.items()}
    for concept, n in by_concept.items():
        if n != _EXPECTED_PER_CONCEPT:
            raise ValueError(
                f"income concept {concept!r} has {n} claims, not "
                f"{_EXPECTED_PER_CONCEPT} — the published grid is square"
            )

    db = ScorecardDB(db_path)
    rows = [ScorecardDB.score_row(s) for s in scores]

    from .baselines import register_baselines_txn
    from .ingest_harvest import sync_lane_feed

    with db.conn:
        db.conn.execute("DELETE FROM external_scores WHERE source = ?", (SOURCE,))
        db.conn.executemany(SCORES_SQL, rows)
        register_baselines_txn(db)
        detail = (
            f"{len(rows)} claims across 5 income concepts "
            f"(1 not_expressible in PE-UK: benefits in kind)"
        )
        db.conn.execute(LANE_SQL, (LANE_ID, "ingested", detail, LANE_UPDATED))
    sync_lane_feed(
        db,
        REPO / "data" / "lanes.json",
        FEED_UPDATED,
        lanes={LANE_ID: LANE_FEED_META},
    )
    db.close()
    return {"claims": len(rows), "by_concept": dict(sorted(by_concept.items()))}


if __name__ == "__main__":
    import sys

    out = Path(sys.argv[1] if len(sys.argv) > 1 else "data/scorecard.db")
    print(json.dumps(ingest(out), indent=1))
