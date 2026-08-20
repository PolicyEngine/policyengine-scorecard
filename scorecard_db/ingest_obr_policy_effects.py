"""Ingest OBR's published policy-effect claims into the scorecard DB (#55).

The external side of the Macro entry point, harvested by
sources/obr-policy-effects/adapter.py into
data/externals/obr-policy-effects.json: what OBR says fiscal policy DOES
to the economy — package effects on real GDP and CPI, per-measure
supply-side impacts on potential output, and the direct/indirect split of
the decisions' effect on borrowing. These are the claims the Macro
members (OBR emulator, OG-UK, PE-UK LSR) answer in step 3; nothing here
computes a counterpart.

Same contract as ingest_uk_externals (scorecard_db/README.md): FAIL
LOUDLY on any unmapped metric, unknown identity value or unhandled
adapter field; values arrive in raw units from the adapter and are NEVER
re-derived here; calibration_relationship is decided in relationships.py
(uk_relationship), never inline.

Four claim families, one source id (``obr_policy_effects``):

    gdp_level_effect             151  per cent of real GDP, by channel or
                                      expenditure component, per FY
    cpi_inflation_effect          36  per cent, by measure, per FY
    supply_side_impact            19  per cent of potential output, one
                                      per measure (briefing paper No.10)
    decisions_effect_on_borrowing 60  GBP, March 2026 Table B.1 nested

Reform worlds. Every row is a policy EFFECT, so each carries a
``policy_ref`` reform naming the world scored — the fiscal event's
package for the package families, the individual measure for the
supply-side family. The baseline stays the null ``current_law``: OBR
scores an announcement against the law in force at its own scoring date,
which is exactly the convention baselines.py documents (announcement
vintage is a condition — ``fiscal_event`` — not a distinct baseline
world), so this module registers no new baseline.

Hierarchy. Table B.1's nested rows carry the adapter's
``aggregate_level``/``parent`` guard into conditions, the same way the
OBR welfare lines do: without them a consumer summing
decisions_effect_on_borrowing by FY would double-count
(total_effect + direct_effects + their components).

Period. The three chart families publish a financial-year path and land
on the FY end year. The briefing paper's supply-side table publishes ONE
number per measure, whose year the table states in words, not digits:
"Supply-side impact is the impact on potential output in the fifth year
of our forecast." That note is carried verbatim in
conditions["horizon_note"], with ``horizon`` naming it symbolically; the
period is _BP10_HORIZON_FY, the fifth year of the November 2025 forecast
the briefing paper accompanies. That mapping is the one interpretive
decision in this module — it is stated here, pinned by a test, and can
be re-keyed in one place if a reviewer reads the horizon differently.

Usage:
    PYTHONPATH=. python -m scorecard_db.ingest_obr_policy_effects data/scorecard.db
"""

from __future__ import annotations

import json
from pathlib import Path

from .db import LANE_SQL, SCORES_SQL, ScorecardDB
from .harvest import REPO, finish, policy_ref, require_fields
from .models import ExternalScore, Metric, TimeBasis, UnitConcept
from .relationships import uk_relationship
from .uk_aliases import canon

EXTERNALS = REPO / "data" / "externals"

# The adapter's file-level slug vs the DB source id (underscored, like
# every other source in external_scores).
ADAPTER_SOURCE = "obr-policy-effects"
SOURCE = "obr_policy_effects"
LANE_ID = "obr-policy-effects"
# This lane's own transition date.
LANE_UPDATED = "2026-08-20"
# The feed's TOP-LEVEL stamp is whatever the last sync_lane_feed caller
# passes, and the UK ingest family pins it to one constant
# (ingest_uk_externals, ingest_uk_deductions). It must stay that
# constant here too: the build ends on this step, the suite ends on
# whichever UK ingest test runs last, and data/lanes.json is committed —
# all three have to agree or the no-drift gate fails.
FEED_UPDATED = "2026-08-19"

PUBLICATIONS = {
    "chart_data": {
        "title": "OBR Economic and fiscal outlook: policy-effect chart data (Nov 2023, Mar 2024, Oct 2024, Nov 2025)",
        "url": "https://obr.uk/publications/",
        "date": "2025-11-26",
    },
    "annex_b": {
        "title": "OBR Economic and fiscal outlook March 2026, Annex B Table B.1: effect of Government decisions on borrowing",
        "url": "https://obr.uk/efo/economic-and-fiscal-outlook-march-2026/",
        "date": "2026-03-16",
    },
    "briefing_paper_10": {
        "title": "OBR Briefing paper No.10: accounting for the supply-side effects of policy measures, Table 2.1",
        "url": "https://obr.uk/docs/dlm_uploads/Briefing_paper_No.10_Accounting_for_the_supply-side_effects_of_policy_measures_charts_and_tables.xlsx",
        "date": "2025-11-26",
    },
}

# Briefing paper No.10 (November 2025) T2.1 note, verbatim: "Supply-side
# impact is the impact on potential output in the fifth year of our
# forecast." The paper accompanies the November 2025 EFO, whose forecast
# runs 2025-26 (the current year) through 2030-31 — five forecast years,
# the fifth being 2030-31. The table names no digit, so the mapping is
# recorded here rather than inferred at each call site.
_BP10_HORIZON_NOTE = (
    "Supply-side impact is the impact on potential output in the fifth "
    "year of our forecast."
)
_BP10_HORIZON_FY = "2030-31"
_BP10_HORIZON_PERIOD = 2031

# metric -> (Metric, UnitConcept, value_kind, publication key)
_METRICS = {
    "gdp_level_effect": (
        Metric.GDP_LEVEL_EFFECT,
        UnitConcept.PERCENT,
        "percent",
        "chart_data",
    ),
    "cpi_inflation_effect": (
        Metric.CPI_INFLATION_EFFECT,
        UnitConcept.PERCENT,
        "percent",
        "chart_data",
    ),
    "supply_side_impact": (
        Metric.SUPPLY_SIDE_IMPACT,
        UnitConcept.PERCENT,
        "percent",
        "briefing_paper_10",
    ),
    "decisions_effect_on_borrowing": (
        Metric.DECISIONS_EFFECT_ON_BORROWING,
        UnitConcept.GBP,
        "gbp",
        "annex_b",
    ),
}

# Every top-level field the adapter emits. Unknown fields raise (the
# harvest require_fields contract): a new adapter column is handled here
# DELIBERATELY or not at all.
_KNOWN_FIELDS = frozenset(
    {
        "aggregate_level",
        "basis",
        "country",
        "description",
        "fiscal_event",
        "geography",
        "metric",
        "parent",
        "period",
        "program",
        "scope",
        "sign_convention",
        "source",
        "source_column",
        "status",
        "subgroup",
        "unit_concept",
        "value",
        "variant",
    }
)

# Closed vocabularies for the free-text-shaped condition axes: an
# unrecognised value is a re-shuffled or re-labelled publication, which
# must fail rather than mint a claim under a new identity.
_EVENTS = frozenset(
    {
        "spring_budget_2023",
        "autumn_statement_2023",
        "spring_budget_2024",
        "autumn_budget_2024",
        "spring_statement_2025",
        "autumn_budget_2025",
        "march_2026_efo",
    }
)
_BASES = frozenset({"post_behavioural", "supply_side"})

# (fiscal_event, published sheet) -> how that chart decomposes the effect.
# This axis is IDENTITY-BEARING, not provenance: the October 2024
# workbook prints the AB2024 package twice — chart 2.A splits it by
# expenditure component, chart 2.B by measure/channel — so both publish a
# 'total' and both publish 'demand_multipliers'. Without the
# decomposition the two totals collide on one claim_id (they agree to
# ~1e-14, being the same series rendered twice) and the two
# demand_multipliers rows claim to be one quantity when they are not.
# The sheet id alone will not do: C2.A is by-channel in the Nov 2023 and
# Mar 2024 workbooks and by-expenditure-component in Oct 2024.
_DECOMPOSITIONS = {
    ("autumn_statement_2023", "C2.A"): "channel",
    ("spring_budget_2024", "C2.A"): "channel",
    ("autumn_budget_2024", "C2.A"): "expenditure_component",
    ("autumn_budget_2024", "C2.B"): "channel",
    ("autumn_budget_2025", "C3.3"): "expenditure_component",
    ("autumn_budget_2025", "C3.4"): "measure",
    ("spring_budget_2023", "T2.1"): "supply_side_channel",
    ("autumn_statement_2023", "T2.1"): "supply_side_channel",
    ("spring_budget_2024", "T2.1"): "supply_side_channel",
    ("autumn_budget_2024", "T2.1"): "supply_side_channel",
    ("spring_statement_2025", "T2.1"): "supply_side_channel",
    ("march_2026_efo", "TB.1"): "fiscal_aggregate",
}
_SCOPES = frozenset({"package", "measure"})
_AGGREGATE_LEVELS = frozenset({"component", "subtotal", "total"})
_MEASURE_TYPES = frozenset({"del", "tax", "welfare", "regulation"})
_SIGN_CONVENTIONS = frozenset({"as_published_positive_increases"})


def _load() -> list[dict]:
    path = EXTERNALS / f"{ADAPTER_SOURCE}.json"
    if not path.exists():
        raise FileNotFoundError(
            f"{path} missing — run sources/obr-policy-effects/adapter.py first"
        )
    rows = json.loads(path.read_text())
    for row in rows:
        require_fields(row, _KNOWN_FIELDS, SOURCE)
        if row["source"] != ADAPTER_SOURCE:
            raise ValueError(
                f"{SOURCE}: row source {row['source']!r} is not {ADAPTER_SOURCE!r}"
            )
        if row["country"] != "UK":
            raise ValueError(f"{SOURCE}: row country {row['country']!r} is not 'UK'")
    return rows


def _closed(value, allowed, axis):
    if value not in allowed:
        raise ValueError(
            f"{SOURCE}: unregistered {axis} {value!r} — add it deliberately, "
            "never pass it through"
        )
    return value


def _fy(label: str) -> tuple[int, str]:
    """'2023-24' -> (2024, '2023-24'). Financial years as published.

    fullmatch, and the suffix must be the start year + 1: '2029-99' is
    malformed, never year 2030 (the ingest_uk_externals gate)."""
    import re

    m = re.fullmatch(r"(\d{4})-(\d{2})", label)
    if not m:
        raise ValueError(f"unparseable OBR financial-year label: {label!r}")
    start = int(m.group(1))
    if (start + 1) % 100 != int(m.group(2)):
        raise ValueError(
            f"OBR financial-year label {label!r}: suffix is not start year + 1"
        )
    return start + 1, f"{start}-{m.group(2)}"


def _decomposition(row: dict) -> str:
    """How the row's published chart splits the effect (see
    _DECOMPOSITIONS). The sheet comes from the adapter's verbatim
    'SHEET:series' source_column; an unregistered (event, sheet) pair
    raises rather than minting claims under an unknown decomposition."""
    sheet = row["source_column"].split(":", 1)[0]
    key = (row["fiscal_event"], sheet)
    if key not in _DECOMPOSITIONS:
        raise ValueError(
            f"{SOURCE}: unregistered (fiscal_event, sheet) {key} — map its "
            "decomposition in _DECOMPOSITIONS deliberately"
        )
    return _DECOMPOSITIONS[key]


def _reform(row: dict):
    """The policy world the row scores.

    Package families score the fiscal event's whole announced package;
    the supply-side family scores one measure inside an event. The two
    never share a slug, and a measure's slug carries its event — the
    same measure re-scored at a later event is a different world.
    """
    event = row["fiscal_event"]
    if row["scope"] == "package":
        return policy_ref(f"obr_{event}_package")
    return policy_ref(f"obr_{event}_{row['program']}")


def stage() -> tuple[list[ExternalScore], dict]:
    """Stage every row; nothing touches the DB here."""
    scores: list[ExternalScore] = []
    counts: dict[str, int] = {}
    for row in _load():
        canon(SOURCE, "unit", row["unit_concept"])
        metric, unit, value_kind, pub_key = _METRICS[row["metric"]]
        cond = {
            "country": "UK",
            "geography": canon(SOURCE, "geography", row["geography"]),
            "program": canon(SOURCE, "program", row["program"]),
            "fiscal_event": _closed(row["fiscal_event"], _EVENTS, "fiscal_event"),
            "basis": _closed(row["basis"], _BASES, "basis"),
            "scope": _closed(row["scope"], _SCOPES, "scope"),
            # the roll-up guard: without it the nested Table B.1 rows read
            # as siblings and any consumer summing by FY double-counts
            "aggregate_level": _closed(
                row["aggregate_level"], _AGGREGATE_LEVELS, "aggregate_level"
            ),
            "decomposition": _decomposition(row),
        }
        if row["parent"] is not None:
            cond["parent"] = canon(SOURCE, "program", row["parent"])
        if row["subgroup"] != "total":
            cond["subgroup"] = canon(SOURCE, "subgroup", row["subgroup"])
        if row["variant"] is not None:
            cond["measure_type"] = _closed(
                row["variant"], _MEASURE_TYPES, "measure_type"
            )
        if row.get("sign_convention") is not None:
            cond["sign_convention"] = _closed(
                row["sign_convention"], _SIGN_CONVENTIONS, "sign_convention"
            )
        if row["period"] == "forecast_horizon":
            if row["metric"] != "supply_side_impact":
                raise ValueError(
                    f"{SOURCE}: period 'forecast_horizon' on {row['metric']!r} — "
                    "only the briefing-paper supply-side table publishes a "
                    "horizon-terminal number"
                )
            period, fy = _BP10_HORIZON_PERIOD, _BP10_HORIZON_FY
            cond["horizon"] = "fifth_year_of_forecast"
            cond["horizon_note"] = _BP10_HORIZON_NOTE
        else:
            period, fy = _fy(row["period"])
        cond["fy"] = fy
        scores.append(
            ExternalScore(
                source=SOURCE,
                metric=metric,
                unit_concept=unit,
                period=period,
                time_basis=TimeBasis.FISCAL_YEAR,
                value=row["value"],
                conditions=cond,
                reform=_reform(row),
                calibration_relationship=uk_relationship(
                    SOURCE, metric, program=cond["program"], kind=row["basis"]
                )[0],
                source_model="obr_efo",
                source_column=row["source_column"],
                publication=PUBLICATIONS[pub_key],
                value_kind=value_kind,
                status=row["status"],
            )
        )
        counts[row["metric"]] = counts.get(row["metric"], 0) + 1
    return finish(scores, SOURCE), counts


# Exact accounting for the committed adapter output. A drifted
# regeneration must fail HERE, never grow or shrink the catalog silently.
_EXPECTED = {
    "gdp_level_effect": 151,
    "cpi_inflation_effect": 36,
    "supply_side_impact": 19,
    "decisions_effect_on_borrowing": 60,
}


def ingest(db_path: Path) -> dict:
    """Stage and validate first; then ONE transaction replaces this
    source wholesale and runs the baseline-registration gate inside it,
    exactly as ingest_uk_externals does. The lane-feed mirror is
    rewritten after the commit (idempotent, keyed by lane id)."""
    scores, counts = stage()
    if counts != _EXPECTED:
        raise ValueError(f"claim accounting drifted: {counts} != {_EXPECTED}")
    db = ScorecardDB(db_path)
    rows = [ScorecardDB.score_row(s) for s in scores]
    from .baselines import register_baselines_txn
    from .ingest_harvest import sync_lane_feed

    with db.conn:
        db.conn.execute("DELETE FROM external_scores WHERE source = ?", (SOURCE,))
        db.conn.executemany(SCORES_SQL, rows)
        register_baselines_txn(db)
        db.conn.execute(
            LANE_SQL,
            (LANE_ID, "ingested", f"{len(rows)} claims", LANE_UPDATED),
        )
    sync_lane_feed(
        db,
        REPO / "data" / "lanes.json",
        FEED_UPDATED,
        lanes={
            LANE_ID: {
                "source": "OBR",
                "area": "published economic effects of policy",
                "mode": 2,
                "country": "UK",
            }
        },
    )
    db.close()
    return {"claims": len(rows), "by_metric": dict(sorted(counts.items()))}


if __name__ == "__main__":
    import sys

    out = Path(sys.argv[1] if len(sys.argv) > 1 else "data/scorecard.db")
    print(json.dumps(ingest(out), indent=1))
