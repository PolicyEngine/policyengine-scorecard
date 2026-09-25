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
supply-side family — AND the baseline world it is scored against.

That baseline is NOT the null ``current_law``. OBR measures a package as
a deviation from that EFO round's PRE-MEASURES forecast, which is a
distinct named world per round (and fixes the economic determinants the
effect is read off); Briefing paper No.10 chapter 2 further scores
tax/welfare measures against a legislated-parameter counterfactual but
DEL and regulatory measures against the pre-existing activity/spending
baseline; and March 2026 Table B.1 states its own counterfactual in its
title — the November 2025 Budget forecast. The adapter emits each row's
world and counterfactual kind with a locator; this module turns them
into ``ReformRef.baseline`` descriptors, mirrors them into
``conditions["baseline_policy"]``, and every one of them is registered in
baselines.py. Defaulting these to ``current_law`` would have let a PE
result computed against current law read as comparable.

Hierarchy. Table B.1's nested rows carry the adapter's
``aggregate_level``/``parent`` guard into conditions, the same way the
OBR welfare lines do: without them a consumer summing
decisions_effect_on_borrowing by FY would double-count
(total_effect + direct_effects + their components).

Period. The three chart families publish a financial-year path and land
on the FY end year. The briefing paper's supply-side table publishes ONE
number per measure, whose year the table states in words, not digits:
"Supply-side impact is the impact on potential output in the fifth year
of our forecast." Crucially that is each measure's OWN scoring round's
forecast, not the November 2025 one the paper is published with:
Briefing paper No.10 re-states scorings made at five earlier fiscal
events, and an AS2023 measure's impact is its effect in the fifth year of
the November 2023 forecast (2028-29), not of the November 2025 forecast.
Period is claim identity, so all 19 rows keyed to one shared 2030-31
would have been 19 wrong claims. _BP10_HORIZON resolves the symbol per
event (the round's own forecast horizon = its current FY + 5, the
convention every EFO follows); ``horizon`` names the symbol and
``horizon_note`` carries the publication's words verbatim.

Usage:
    PYTHONPATH=. python -m scorecard_db.ingest_obr_policy_effects data/scorecard.db
"""

from __future__ import annotations

import json
from pathlib import Path

from .db import LANE_SQL, SCORES_SQL, ScorecardDB
from .harvest import REPO, finish, policy_ref, require_fields, with_baseline_condition
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

# Publication provenance, keyed by the VENDORED ARTIFACT each row names.
# Publication is per fiscal event: one generic obr.uk/publications/ URL
# stamped with the newest round's date misdated every earlier round's
# claims, and the March 2026 rows carried the Wayback CAPTURE date
# (2026-03-16) instead of the publication date (2026-03-03). Dates are
# the OBR release dates; the captures are recorded in
# sources/obr-policy-effects/raw/README.md and are not publication dates.
PUBLICATIONS = {
    "efo_november2023_chapter2.xlsx": {
        "title": (
            "OBR Economic and fiscal outlook – November 2023, Chapter 2 "
            "charts and tables (Chart 2.A: real GDP impacts of the Autumn "
            "Statement 2023 package)"
        ),
        "url": (
            "https://obr.uk/docs/dlm_uploads/"
            "Chapter_2_charts_and_tables_November_2023.xlsx"
        ),
        "date": "2023-11-22",
    },
    "efo_march2024_chapter2.xlsx": {
        "title": (
            "OBR Economic and fiscal outlook – March 2024, Chapter 2 "
            "charts and tables (Chart 2.A: impact of policy measures on "
            "real GDP)"
        ),
        "url": (
            "https://obr.uk/docs/dlm_uploads/"
            "Chapter_2_charts_and_tables_March_2024.xlsx"
        ),
        "date": "2024-03-06",
    },
    "efo_october2024_chapter2.xlsx": {
        "title": (
            "OBR Economic and fiscal outlook – October 2024, Chapter 2 "
            "charts and tables (Charts 2.A and 2.B: policy impacts on real "
            "GDP, by component and by measure)"
        ),
        "url": (
            "https://obr.uk/docs/dlm_uploads/"
            "Chapter_2_charts_and_tables_October_2024.xlsx"
        ),
        "date": "2024-10-30",
    },
    "efo_november2025_chapter3.xlsx": {
        "title": (
            "OBR Economic and fiscal outlook – November 2025, Chapter 3 "
            "charts and tables (Charts 3.3 and 3.4: policy impacts on real "
            "GDP and on CPI inflation)"
        ),
        "url": (
            "https://obr.uk/docs/dlm_uploads/"
            "Chapter_3_charts_and_tables_November_2025.xlsx"
        ),
        "date": "2025-11-26",
    },
    "efo_march2026_annex_tables.xlsx": {
        "title": (
            "OBR Economic and fiscal outlook – March 2026, Annex B Table "
            "B.1: total effect of Government decisions on borrowing"
        ),
        "url": (
            "https://obr.uk/docs/d055fbf02d5b3g6jq8l2/"
            "efo-march-2026-charts-and-tables-annex-tables.xlsx"
        ),
        "date": "2026-03-03",
    },
    "obr_briefing_paper_10_supply_side.xlsx": {
        "title": (
            "OBR Briefing paper No.10: accounting for the supply-side "
            "effects of policy measures, Table 2.1"
        ),
        "url": (
            "https://obr.uk/docs/dlm_uploads/Briefing_paper_No.10_Accounting_"
            "for_the_supply-side_effects_of_policy_measures_charts_and_"
            "tables.xlsx"
        ),
        "date": "2025-11-26",
    },
}

# Briefing paper No.10 (November 2025) T2.1 note, verbatim: "Supply-side
# impact is the impact on potential output in the fifth year of our
# forecast." The paper RE-STATES scorings made at five earlier fiscal
# events, so "our forecast" is each measure's own scoring round — not the
# November 2025 round the paper accompanies. Every EFO forecast runs the
# current financial year plus five, so the fifth forecast year of a round
# held in FY Y is FY Y+5:
#
#   March 2023      scored in FY2022-23 -> 2027-28
#   November 2023   scored in FY2023-24 -> 2028-29
#   March 2024      scored in FY2023-24 -> 2028-29
#   October 2024    scored in FY2024-25 -> 2029-30
#   March 2025      scored in FY2024-25 -> 2029-30
#
# Period is claim identity: keying all 19 rows to 2030-31 (the November
# 2025 round's horizon) made 19 claims about years OBR never scored them
# for. The mapping is stated here, pinned by tests, and re-keyable in one
# place if a reviewer reads a horizon differently.
_BP10_HORIZON_NOTE = (
    "Supply-side impact is the impact on potential output in the fifth "
    "year of our forecast."
)
_BP10_HORIZON = {
    "spring_budget_2023": ("2027-28", 2028),
    "autumn_statement_2023": ("2028-29", 2029),
    "spring_budget_2024": ("2028-29", 2029),
    "autumn_budget_2024": ("2029-30", 2030),
    "spring_statement_2025": ("2029-30", 2030),
}

# metric -> (Metric, adapter unit expected, UnitConcept, value_kind).
# VALIDATE-THEN-MAP (the #52 pattern): the adapter's staged unit label is
# checked against the one this metric must carry and RAISES on drift.
# Previously the staged label was canon-checked and then DISCARDED, so a
# GDP row mislabeled 'gbp_nominal' would have been stored as a percent.
_METRICS = {
    "gdp_level_effect": (
        Metric.GDP_LEVEL_EFFECT,
        "percent_of_real_gdp",
        UnitConcept.PERCENT_OF_REAL_GDP,
        "percent",
    ),
    "cpi_inflation_effect": (
        Metric.CPI_INFLATION_EFFECT,
        "percentage_points",
        UnitConcept.PERCENTAGE_POINTS,
        "percent",
    ),
    "supply_side_impact": (
        Metric.SUPPLY_SIDE_IMPACT,
        "percent_of_potential_gdp",
        UnitConcept.PERCENT_OF_POTENTIAL_GDP,
        "percent",
    ),
    "decisions_effect_on_borrowing": (
        Metric.DECISIONS_EFFECT_ON_BORROWING,
        "gbp_nominal",
        UnitConcept.GBP,
        "gbp",
    ),
}

# Every top-level field the adapter emits. Unknown fields raise (the
# harvest require_fields contract): a new adapter column is handled here
# DELIBERATELY or not at all.
_KNOWN_FIELDS = frozenset(
    {
        "aggregate_level",
        "artifact",
        "baseline",
        "baseline_counterfactual",
        "baseline_locator",
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
        "scoring_method",
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
# `basis` is the repo-wide forecast|outturn axis and every row here is a
# forecast quantity. HOW the effect was scored is a different question
# and gets its own axis — a scoring method was squatting on `basis`.
_BASES = frozenset({"forecast"})
_SCORING_METHODS = frozenset({"post_behavioural", "supply_side"})

# The baseline worlds these claims are scored against, closed. Every one
# is registered in baselines.py, and the registration gate runs inside
# the same transaction as the claims — an unregistered world rolls the
# whole replacement back.
# fiscal_event -> the ONE baseline world its rows may key. A row whose
# event and baseline disagree is exactly the failure this fixes: the
# registration gate passes while the claims name the wrong world.
_EVENT_BASELINE = {
    "spring_budget_2023": "obr_pre_measures_spring_budget_2023",
    "autumn_statement_2023": "obr_pre_measures_autumn_statement_2023",
    "spring_budget_2024": "obr_pre_measures_spring_budget_2024",
    "autumn_budget_2024": "obr_pre_measures_autumn_budget_2024",
    "spring_statement_2025": "obr_pre_measures_spring_statement_2025",
    "autumn_budget_2025": "obr_pre_measures_autumn_budget_2025",
    "march_2026_efo": "obr_november_2025_budget_forecast",
}
_BASELINE_POLICIES = frozenset(_EVENT_BASELINE.values())
_COUNTERFACTUALS = frozenset({"policy_parameters", "del_activity", "regulatory"})

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


def _baseline_descriptor(row: dict) -> dict:
    """The world this row is scored AGAINST, from the adapter's own
    per-row declaration — never a default.

    OBR measures a package as a deviation from its round's pre-measures
    forecast, and Briefing paper No.10 scores DEL and regulatory measures
    against the pre-existing activity baseline rather than a legislated
    parameter, so the counterfactual KIND is part of the world's
    identity. Both values are closed; the locator travels with the claim
    as provenance.
    """
    policy = _closed(row["baseline"], _BASELINE_POLICIES, "baseline policy")
    expected = _EVENT_BASELINE[_closed(row["fiscal_event"], _EVENTS, "fiscal_event")]
    if policy != expected:
        raise ValueError(
            f"{SOURCE}: {row['fiscal_event']} rows are scored against "
            f"{expected!r}, not {policy!r} — each round has its own "
            "pre-measures world and they are not interchangeable"
        )
    kind = _closed(
        row["baseline_counterfactual"], _COUNTERFACTUALS, "baseline counterfactual"
    )
    if not str(row.get("baseline_locator", "")).strip():
        raise ValueError(
            f"{SOURCE}: baseline {policy!r} carries no locator — a registered "
            "world without a citable reading is not provenance"
        )
    return {"policy": policy, "counterfactual": kind}


def _reform(row: dict):
    """The policy world the row scores.

    Package families score the fiscal event's whole announced package;
    the supply-side family scores one measure inside an event. The two
    never share a slug, and a measure's slug carries its event — the
    same measure re-scored at a later event is a different world.
    """
    event = row["fiscal_event"]
    baseline = _baseline_descriptor(row)
    if row["scope"] == "package":
        return policy_ref(f"obr_{event}_package", baseline=baseline)
    return policy_ref(f"obr_{event}_{row['program']}", baseline=baseline)


def stage() -> tuple[list[ExternalScore], dict]:
    """Stage every row; nothing touches the DB here."""
    scores: list[ExternalScore] = []
    counts: dict[str, int] = {}
    for row in _load():
        staged_unit = canon(SOURCE, "unit", row["unit_concept"])
        metric, expected_unit, unit, value_kind = _METRICS[row["metric"]]
        # validate-THEN-map: the staged label must be the one this metric
        # carries, or the row is a mislabeled quantity and must not land
        if staged_unit != expected_unit:
            raise ValueError(
                f"{SOURCE}: {row['metric']} staged unit {staged_unit!r} != "
                f"{expected_unit!r} — the adapter's unit label and the metric's "
                "unit concept disagree; fix the label, never map past it"
            )
        cond = {
            "country": "UK",
            "geography": canon(SOURCE, "geography", row["geography"]),
            "program": canon(SOURCE, "program", row["program"]),
            "fiscal_event": _closed(row["fiscal_event"], _EVENTS, "fiscal_event"),
            "basis": _closed(row["basis"], _BASES, "basis"),
            "scoring_method": _closed(
                row["scoring_method"], _SCORING_METHODS, "scoring_method"
            ),
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
            if row["fiscal_event"] not in _BP10_HORIZON:
                raise ValueError(
                    f"{SOURCE}: no forecast horizon registered for scoring "
                    f"event {row['fiscal_event']!r} — a horizon-terminal "
                    "number needs its own round's fifth forecast year, not "
                    "another round's"
                )
            fy, period = _BP10_HORIZON[row["fiscal_event"]]
            cond["horizon"] = "fifth_year_of_scoring_round_forecast"
            cond["horizon_note"] = _BP10_HORIZON_NOTE
        else:
            period, fy = _fy(row["period"])
        cond["fy"] = fy
        reform = _reform(row)
        with_baseline_condition(cond, reform)
        if row["artifact"] not in PUBLICATIONS:
            raise ValueError(
                f"{SOURCE}: no publication registered for artifact "
                f"{row['artifact']!r} — publication provenance is per "
                "artifact, never one generic stamp"
            )
        scores.append(
            ExternalScore(
                source=SOURCE,
                metric=metric,
                unit_concept=unit,
                period=period,
                time_basis=TimeBasis.FISCAL_YEAR,
                value=row["value"],
                conditions=cond,
                reform=reform,
                calibration_relationship=uk_relationship(
                    SOURCE, metric, program=cond["program"], kind=row["scoring_method"]
                )[0],
                source_model="obr_efo",
                source_column=row["source_column"],
                publication=PUBLICATIONS[row["artifact"]],
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
