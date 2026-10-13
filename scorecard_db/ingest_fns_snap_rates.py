"""Ingest the FNS state SNAP participation rates and their PE counterparts (#2).

The first US mode-1 source after Urban (lane fns-snap-rates). FNS
(Mathematica, February 2025) publishes per State and fiscal year the share
of people eligible under FEDERAL rules who participate in an average month,
and the eligible count behind it. Inputs:

    data/externals/fns-snap-rates.json  the adapter's tidy rows (QC'd there)
    sources/fns-snap-rates/pe/<bundle>.json  the PE counterparts
        (pipeline/campaign_us/fns_snap_rates.py: federal-rules world,
        average month of CY2024, toggle-verified)
    sources/fns-snap-rates/annotations.json  concept deltas, each with a basis

Claims: participation_rate and eligible_count for the 50 States, DC and the
nation, FY 2020 and FY 2022 (208). PE results attach to the FY 2022 claims
only; FY 2020 covers five pre-pandemic months and is an underestimate by
the report's own account, so it stays registered without a counterpart.

Deliberate drops, tallied (all still in data/externals for diagnosis):
    - standard_error and uncapped_implied variants (the claim is the
      central published estimate; the cap rides as an annotation)
    - administrative cells: participant_count (FNS program operations),
      federal_rules_eligible_share (SNAP QC) and their product — the
      numerator's inputs, not modeled claims (the 2026-08-02 boundary rule)
    - benchmark_adjustment_factor (a method constant)
    - FNS regions (no PE counterpart registered for the region map)

calibration_relationship comes from relationships.effective_relationship:
the rate is consumed_as_target (its numerator class, FNS average-month
caseloads, is a calibration target) and the eligible count is held_out
(no eligibility targets) — the eligible count is this lane's out-of-sample
signal.

    PYTHONPATH=. python -m scorecard_db.ingest_fns_snap_rates data/scorecard.db
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

from .db import LANE_SQL, RESULTS_SQL, SCORES_SQL, ScorecardDB
from .harvest import REPO, finish, require_fields
from .models import (
    BASELINE,
    ComparisonStatus,
    ExternalScore,
    Metric,
    PEResult,
    TimeBasis,
    UnitConcept,
)
from .relationships import effective_relationship

EXTERNALS = REPO / "data" / "externals"
SOURCE_DIR = REPO / "sources" / "fns-snap-rates"
ADAPTER_SOURCE = "fns-snap-rates"
SOURCE = "fns_snap_rates"
SOURCE_MODEL = "mathematica_snap_shrinkage"
PE_BUNDLE = "us-6.2.1"
COMPUTED_PERIOD = 2022  # the fiscal year PE results attach to

LANE_ID = "fns-snap-rates"
LANE_UPDATED = "2026-10-06"
FEED_UPDATED = "2026-10-06"
LANE_FEED_META = {
    "source": "FNS",
    "area": "official SNAP state participation rates",
    "mode": 1,
    "country": "US",
}

PUBLICATION = {
    "title": (
        "Empirical Bayes Shrinkage Estimates of State SNAP Participation "
        "Rates: Fiscal Year 2020 and Fiscal Year 2022"
    ),
    "url": "https://www.fns.usda.gov/research/snap/state-participation-rates/2022",
    "date": "2025-02",
    "vintage": "FY 2022 (latest edition as fetched 2026-10-06)",
}

_KNOWN_FIELDS = frozenset(
    {
        "country",
        "geography",
        "metric",
        "period",
        "program",
        "source",
        "source_column",
        "status",
        "subgroup",
        "unit_concept",
        "value",
        "variant",
    }
)

# adapter metric -> (Metric, UnitConcept, value_kind, staged PE field)
_CLAIM_METRICS = {
    "participation_rate": (
        Metric.PARTICIPATION_RATE,
        UnitConcept.SHARE,
        "share",
        "participation_rate",
    ),
    "eligible_count": (
        Metric.ELIGIBLE_COUNT,
        UnitConcept.PERSONS,
        "count",
        "eligible_persons",
    ),
}
_ADMIN_METRICS = frozenset(
    {
        "participant_count",
        "federal_rules_eligible_share",
        "federal_rules_eligible_participant_count",
    }
)
_DROPPED_VARIANTS = frozenset({"standard_error", "uncapped_implied"})
_PERIODS = {"FY 2020": 2020, "FY 2022": 2022}


def _load() -> list[dict]:
    path = EXTERNALS / f"{ADAPTER_SOURCE}.json"
    if not path.exists():
        raise FileNotFoundError(
            f"{path} missing — run sources/fns-snap-rates/adapter.py first"
        )
    rows = json.loads(path.read_text())
    for row in rows:
        require_fields(row, _KNOWN_FIELDS, SOURCE)
        if row["source"] != ADAPTER_SOURCE or row["country"] != "US":
            raise ValueError(f"{SOURCE}: foreign row {row['source_column']!r}")
        if row["program"] != "snap" or row["subgroup"] != "total":
            raise ValueError(f"{SOURCE}: unexpected row {row['source_column']!r}")
    return rows


_NAMES = {
    "participation_rate": "SNAP participation rate",
    "eligible_count": "People eligible for SNAP",
}


def _place(row: dict) -> str:
    """The State name as the table prints it ('Table A.17: New York, FY
    2022' -> 'New York'); national rows read 'United States'."""
    if row["geography"] == "US":
        return "United States"
    m = re.fullmatch(r"Table A\.1[78]: (.+), FY \d{4}", row["source_column"])
    if m is None:
        raise ValueError(f"{SOURCE}: no State name in {row['source_column']!r}")
    return m.group(1)


def _claim(row: dict) -> ExternalScore:
    metric, unit, value_kind, _ = _CLAIM_METRICS[row["metric"]]
    value = float(row["value"])
    if value_kind == "share" and not 0.0 < value <= 1.0:
        raise ValueError(f"{SOURCE}: rate {value} is not a share ({row})")
    conditions = {"geography": row["geography"], "program": "snap"}
    if value_kind == "share":
        conditions["rate_unit"] = row["unit_concept"]
    return ExternalScore(
        source=SOURCE,
        source_model=SOURCE_MODEL,
        metric=metric,
        unit_concept=unit,
        period=_PERIODS[row["period"]],
        time_basis=TimeBasis.AVERAGE_MONTH,
        value=value,
        conditions={**conditions, "year_basis": "federal_fiscal_year"},
        calibration_relationship=effective_relationship("snap", metric)[0],
        source_column=row["source_column"],
        publication={
            **PUBLICATION,
            "name": f"{_NAMES[row['metric']]}, {_place(row)}",
            "window": f"{row['period']}, average month",
        },
        value_kind=value_kind,
        status=row["status"],
    )


def stage() -> tuple[list[ExternalScore], dict, dict]:
    """(claims, drop tally, uncapped implied rate per (geography, period))."""
    scores: list[ExternalScore] = []
    drops: Counter = Counter()
    uncapped: dict[tuple[str, int], float] = {}
    for row in _load():
        if row["variant"] == "uncapped_implied":
            uncapped[(row["geography"], _PERIODS[row["period"]])] = row["value"]
        if row["variant"] in _DROPPED_VARIANTS:
            drops[f"variant:{row['variant']}"] += 1
            continue
        if row["variant"] is not None:
            raise ValueError(f"{SOURCE}: unknown variant {row['variant']!r}")
        if row["metric"] in _ADMIN_METRICS:
            drops[f"admin:{row['metric']}"] += 1
            continue
        if row["metric"] == "benchmark_adjustment_factor":
            drops["method_constant"] += 1
            continue
        if row["metric"] not in _CLAIM_METRICS:
            raise ValueError(f"{SOURCE}: unmapped metric {row['metric']!r}")
        if row["geography"].startswith("fns_region:"):
            drops["fns_region"] += 1
            continue
        scores.append(_claim(row))
    return finish(scores, SOURCE), dict(sorted(drops.items())), uncapped


def _annotations(metric: str, saturated: bool, grain: str) -> list[str]:
    """Annotation texts for one result. ``saturated`` limits a note to
    geographies where the measured take-up flag share is 1; the
    person-grain note gets the measured counts (``grain``) appended."""
    spec = json.loads((SOURCE_DIR / "annotations.json").read_text())
    out = []
    for a in spec["annotations"]:
        if not a.get("basis"):
            raise ValueError(f"annotation {a['id']} has no basis")
        match = a["applies_to"]
        if set(match) - {"program", "metrics", "saturated"}:
            raise ValueError(f"annotation {a['id']}: unknown matcher {match}")
        metrics = match.get("metrics")
        if metrics is not None and metric not in metrics:
            continue
        if match.get("saturated") and not saturated:
            continue
        out.append(
            f"{a['text']} {grain}" if a["id"] == "fns-person-grain" else a["text"]
        )
    return out


def _grain_note(staged: dict, period: int) -> str:
    """The measured person-grain gap: PE people in participating SPM units
    as served (BBCE included) vs FNS participants (Table A.1)."""
    fns_participants = next(
        r["value"]
        for r in _load()
        if r["metric"] == "participant_count"
        and r["geography"] == "US"
        and _PERIODS[r["period"]] == period
    )
    pe_people = staged["geographies"]["US"]["baseline_participants"]
    return (
        f"Measured: as served, PolicyEngine has {pe_people / 1e6:.1f} million "
        f"people in participating SPM units in an average {staged['period']} "
        f"month; FNS counts {fns_participants / 1e6:.1f} million participants "
        f"in FY {period} (Table A.1)."
    )


def results(scores: list[ExternalScore], uncapped: dict) -> list[PEResult]:
    staged = json.loads((SOURCE_DIR / "pe" / f"{PE_BUNDLE}.json").read_text())
    prov = staged["provenance"]
    if prov["bundle_id"] != PE_BUNDLE:
        raise ValueError(f"staged PE file is {prov['bundle_id']}, want {PE_BUNDLE}")
    geos = staged["geographies"]
    grain = _grain_note(staged, COMPUTED_PERIOD)
    # A capped cell is a State rate of exactly 100%; both of its claims
    # (rate and eligible count) carry the cap. Exhibit A.3 prints the
    # uncapped value for all but the secondary caps (adapter.SECONDARY_CAPS).
    capped = {
        (s.conditions["geography"], s.period)
        for s in scores
        if s.metric == Metric.PARTICIPATION_RATE
        and s.conditions["geography"] != "US"
        and s.value == 1.0
    }
    out = []
    for s in scores:
        if s.period != COMPUTED_PERIOD:
            continue
        geo = s.conditions["geography"]
        field = _CLAIM_METRICS[
            "participation_rate"
            if s.metric == Metric.PARTICIPATION_RATE
            else "eligible_count"
        ][3]
        value = float(geos[geo][field])
        # every federally eligible person's unit carries the take-up flag
        saturated = geos[geo]["takeup_flag_share"] >= 1 - 1e-9
        notes = _annotations(s.metric.value, saturated, grain)
        if (geo, s.period) in capped:
            cap = uncapped.get((geo, s.period))
            notes.append(
                f"This State is capped: FNS's implied FY {s.period} rate before "
                f"the cap was {cap:.1%} (Exhibit A.3)."
                if cap is not None
                else "This State is capped at 100%. The report prints no "
                "uncapped value for it: the cap's own redistribution raised "
                "it over 100% after Exhibit A.3 was drawn (report ch. II.D)."
            )
        out.append(
            PEResult(
                claim_id=s.claim_id(),
                computed_value=value,
                status=ComparisonStatus.CONSTRUCTED,
                engine_version=prov["engine_version"],
                data_bundle=prov["data_bundle"],
                pe_construction=staged["pe_construction"],
                run_id=staged["run_id"],
                computed_at=staged["computed_at"],
                annotations=notes,
                baseline_key=BASELINE.baseline_key(),
                policyengine_variables=staged["policyengine_variables"],
            )
        )
    return out


_EXPECTED = {"claims": 208, "results": 104}


def ingest(db_path: Path) -> dict:
    scores, drops, uncapped = stage()
    pe = results(scores, uncapped)
    counts = {"claims": len(scores), "results": len(pe)}
    if counts != _EXPECTED:
        raise ValueError(f"claim accounting drifted: {counts} != {_EXPECTED}")
    db = ScorecardDB(db_path)

    from .baselines import register_baselines_txn
    from .ingest_harvest import sync_lane_feed

    with db.conn:
        db.conn.execute(
            "DELETE FROM pe_results WHERE claim_id IN "
            "(SELECT claim_id FROM external_scores WHERE source = ?)",
            (SOURCE,),
        )
        db.conn.execute("DELETE FROM external_scores WHERE source = ?", (SOURCE,))
        db.conn.executemany(SCORES_SQL, [ScorecardDB.score_row(s) for s in scores])
        db.conn.executemany(RESULTS_SQL, [ScorecardDB.result_row(r) for r in pe])
        register_baselines_txn(db)
        detail = (
            f"{len(pe)} of {len(scores)} claims computed — FY 2020 and FY 2022 "
            "State, DC and national rates and eligible counts (federal rules, "
            "average month; Mathematica shrinkage); FY 2022 compared with PE "
            "CY2024 on us-6.2.1 in a BBCE-off world; adapter QC recomputes "
            "every rate from its published parts"
        )
        db.conn.execute(LANE_SQL, (LANE_ID, "computed", detail, LANE_UPDATED))
    sync_lane_feed(
        db,
        REPO / "data" / "lanes.json",
        FEED_UPDATED,
        lanes={LANE_ID: LANE_FEED_META},
    )
    db.close()
    return {**counts, "drops": drops}


if __name__ == "__main__":
    import sys

    out = Path(sys.argv[1] if len(sys.argv) > 1 else "data/scorecard.db")
    print(json.dumps(ingest(out), indent=1))
