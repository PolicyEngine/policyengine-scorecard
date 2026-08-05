"""Ingest the Columbia CPSP staged claims (2026-08-02 harvest).

Monthly SPM series 2024-01→2025-12 (the project ended Dec 2025 — no 2026
monthlies will ever exist; Oct 2025 blank from the shutdown CPS), annual
historical/anchored rates, the CTC counterfactual briefs (2023 + 2024),
the state refundable-CTC design brief, and the SNAP TFP-revocation
all-state tables (TRIM3-pooled 2015-19 base, data_vintage-flagged).

Counterfactual worlds ride policy_ref reforms. The CTC scenario worlds
(No-CTC / TCJA / OBBBA / AFA) are modeled at explicit 100% take-up with
no behavioral response (per the briefs; harvest NOTES), so the modeled
CTC worlds carry take_up="full" — including "TCJA CTC (current policy)",
which is NOT the observed current-law world. Change rows compare two
modeled worlds: reform = the scenario, ReformRef.baseline = the
comparison world (current law/policy -> None).

calibration_relationship review (COLLATION item 5): CPSP annual SPM
levels ≈ published Census SPM. Verified 2026-08-02 against
policyengine-us/parameters/calibration/: the census/ tree carries
population totals only — no SPM or poverty targets anywhere in the
calibration surface — so held_out stands for the annual series.

The 2024 historical brief carries a CPSP ERRATUM (key findings say 16.6%
where body Fig.3 and the arithmetic give 11.4%; 11.4 staged). ingest()
seeds the external_issue diagnosis on that claim.
"""

from __future__ import annotations

import json
from pathlib import Path

from .db import ScorecardDB
from .harvest import (
    finish,
    load_staged,
    normalize_geography,
    policy_ref,
    require_fields,
    with_baseline_condition,
)
from .models import (
    BASELINE,
    ExternalScore,
    Metric,
    ReformRef,
    TimeBasis,
    UnitConcept,
)

_STATE_DESIGNS = {
    "California",
    "Colorado",
    "Illinois",
    "Maine",
    "Maryland",
    "Massachusetts",
    "Minnesota",
    "New Jersey",
    "New Mexico",
    "New York",
    "Oregon",
    "Vermont",
    "Washington DC",
}

# Modeled CTC counterfactual worlds (100% take-up, no behavior).
_TCJA_CTC = {"policy": "tcja_ctc", "take_up": "full"}
_AFA_CTC = {"policy": "afa_ctc", "take_up": "full"}
_OBBBA_CTC = {"policy": "obbba_ctc", "take_up": "full"}
_NO_CTC = {"policy": "no_ctc"}


def _scenario_world(scenario: str) -> tuple[dict | None, dict]:
    """policy_scenario -> (reform descriptor or None for current law,
    extra conditions)."""
    if scenario in (
        "With All Taxes & Transfers",
        "observed (all taxes and transfers)",
        "current policy (2021 TFP adjustment in place)",
        "baseline (no refundable state CTC)",
    ):
        return None, {}
    if scenario in ("Pre-Tax/Transfer", "pre-tax/transfer"):
        return None, {"income_concept": "pre_tax_transfer"}
    if scenario == "Without COVID Relief":
        return {"policy": "no_covid_relief"}, {}
    if scenario == "Revoke 2021 Thrifty Food Plan adjustment to SNAP":
        return {"policy": "snap_tfp_2021_revoked"}, {}
    if scenario == "No CTC":
        return _NO_CTC, {}
    if scenario in ("TCJA CTC", "2023 TCJA CTC (current policy)"):
        return _TCJA_CTC, {}
    if scenario in ("AFA CTC", "2023 AFA CTC"):
        return _AFA_CTC, {}
    if scenario == "OBBBA CTC":
        return _OBBBA_CTC, {}
    if scenario.endswith(" Design"):
        state = scenario[: -len(" Design")]
        if state not in _STATE_DESIGNS:
            raise ValueError(f"cpsp: unknown state design {scenario!r}")
        return {
            "policy": "state_refundable_ctc_design",
            "option": state,
        }, {}
    raise ValueError(f"cpsp: unmapped policy_scenario {scenario!r}")


def _comparison_world(scenario: str) -> dict | None:
    """comparison_scenario -> ReformRef.baseline descriptor."""
    if scenario in ("current policy", "baseline (no refundable state CTC)"):
        return None  # current law
    if scenario == "No CTC":
        return _NO_CTC
    if scenario in ("TCJA CTC", "2023 TCJA CTC (current policy)"):
        return _TCJA_CTC
    raise ValueError(f"cpsp: unmapped comparison_scenario {scenario!r}")


METRICS = {
    "poverty_rate": Metric.POVERTY_RATE,
    "poverty_rate_change": Metric.POVERTY_RATE_CHANGE,
    "poverty_count": Metric.POVERTY_COUNT,
    "poverty_count_change": Metric.POVERTY_COUNT_CHANGE,
}

_KNOWN_FIELDS = frozenset(
    {
        "source",
        "metric",
        "proposed_metric",
        "unit_concept",
        "proposed_unit_concept",
        "period",
        "time_basis",
        "value",
        "conditions",
        "reform",
        "calibration_relationship",
        "source_model",
        "source_column",
        "publication",
        "value_kind",
        "status",
    }
)
_KNOWN_CONDITIONS = frozenset(
    {
        "geography",
        "subgroup",
        "policy_scenario",
        "comparison_scenario",
        "change_type",
        "month",
        "data_vintage",
        "poverty_threshold",
        "measure_variant",
        "caveat",
    }
)

ERRATUM_RATIONALE = (
    "CPSP's 2024 historical brief states 16.6% in its key findings where "
    "body Figure 3 and the underlying arithmetic give 11.4% "
    "(anchored-2022 SPM, all persons, 2024); the harvest staged 11.4 and "
    "flagged the inconsistency (sources/harvest-2026-08-02/cpsp/NOTES.md)."
)


def stage_scores() -> list[ExternalScore]:
    scores = []
    for row in load_staged("cpsp"):
        require_fields(row, _KNOWN_FIELDS, "cpsp")
        staged_conds = dict(row["conditions"])
        unknown = set(staged_conds) - _KNOWN_CONDITIONS
        if unknown:
            raise ValueError(f"cpsp: unmapped conditions {sorted(unknown)}")
        if row["reform"] != {"framework": "baseline"}:
            raise ValueError(f"cpsp: unexpected staged reform {row['reform']}")
        if row["calibration_relationship"] != "held_out":
            raise ValueError("cpsp: unexpected calibration relationship")

        metric = METRICS[row.get("metric") or row["proposed_metric"]]
        if metric in (Metric.POVERTY_RATE, Metric.POVERTY_RATE_CHANGE):
            unit = UnitConcept.SHARE
        else:
            unit = UnitConcept(row.get("unit_concept") or row["proposed_unit_concept"])

        reform_desc, extra = _scenario_world(staged_conds.pop("policy_scenario"))
        comparison = staged_conds.pop("comparison_scenario", None)
        is_change = metric in (
            Metric.POVERTY_RATE_CHANGE,
            Metric.POVERTY_COUNT_CHANGE,
        )
        if is_change != (comparison is not None):
            raise ValueError(
                "cpsp: change metrics and comparison_scenario must pair "
                f"({metric.value}, {comparison!r})"
            )
        if comparison is not None:
            if reform_desc is None:
                raise ValueError("cpsp: change row scored on current law")
            reform = ReformRef(
                framework="policy_ref",
                reform=reform_desc,
                baseline=_comparison_world(comparison),
            )
        elif reform_desc is not None:
            reform = policy_ref(
                **{k if k != "policy" else "policy": v for k, v in reform_desc.items()}
            )
        else:
            reform = BASELINE

        conditions = {
            "geography": normalize_geography(staged_conds.pop("geography")),
            **extra,
        }
        subgroup = staged_conds.pop("subgroup")
        if subgroup != "all":
            conditions["subgroup"] = subgroup
        for key in (
            "change_type",
            "month",
            "data_vintage",
            "poverty_threshold",
            "measure_variant",
        ):
            if key in staged_conds:
                conditions[key] = staged_conds.pop(key)
        with_baseline_condition(conditions, reform)

        publication = dict(row["publication"])
        if "caveat" in staged_conds:
            publication["caveat"] = staged_conds.pop("caveat")
        if staged_conds:
            raise ValueError(f"cpsp: unconsumed {sorted(staged_conds)}")

        scores.append(
            ExternalScore(
                source="cpsp",
                source_model=row["source_model"],
                metric=metric,
                unit_concept=unit,
                period=row["period"],
                time_basis=TimeBasis(row["time_basis"]),
                value=row["value"],
                conditions=conditions,
                reform=reform,
                source_column=row["source_column"],
                publication=publication,
                value_kind=row["value_kind"],
                status=row["status"],
            )
        )
    return finish(scores, "cpsp")


def erratum_claim(scores: list[ExternalScore]) -> ExternalScore:
    hits = [
        s
        for s in scores
        if s.metric is Metric.POVERTY_RATE
        and s.period == 2024
        and s.conditions.get("measure_variant") == "anchored_2022_spm"
        and s.reform is BASELINE
        and "month" not in s.conditions
        and "subgroup" not in s.conditions
    ]
    if len(hits) != 1:
        raise ValueError(f"cpsp: erratum claim not unique: {len(hits)}")
    return hits[0]


def ingest(db_path: Path) -> dict:
    scores = stage_scores()
    db = ScorecardDB(db_path)
    n = db.upsert_scores(scores)
    db.diagnose(
        erratum_claim(scores).claim_id(),
        "external_issue",
        ERRATUM_RATIONALE,
    )
    db.set_lane(
        "cpsp-poverty",
        "ingested",
        f"{n} claims: monthly SPM 2024-01→2025-12 (final series — project "
        "ended Dec 2025), CTC counterfactuals 2023/2024 at 100% take-up, "
        "state refundable-CTC designs, SNAP TFP-revocation state tables "
        "(TRIM3 2015-19 base); annual-SPM≈Census reviewed → held_out (no "
        "poverty targets in pe-us calibration); 16.6-vs-11.4 erratum "
        "diagnosed external_issue",
        "2026-08-02",
    )
    db.close()
    return {"scores": n}


if __name__ == "__main__":
    import sys

    out = Path(sys.argv[1] if len(sys.argv) > 1 else "data/scorecard.db")
    print(json.dumps(ingest(out), indent=1))
