"""Scorecard database models.

Design decisions (Max, 2026-08-01):

1. **Every claim is keyed off a reform reference.** ``reform`` describes the
   policy world an external score is about: ``baseline`` (current law) for
   level validation, a PolicyEngine parametric reform for score validation,
   and — reserved — an Axiom rulespec reference. This unifies mode 1
   (population statistics) and mode 2 (reform scores) in one table: a level
   is just a score of the null reform.

2. **Populace-targets-DB shape.** Each row = a provenance reference (the
   ``ledger_fact`` column — a Ledger ``validation_comparator`` fact id once
   cataloged; publication metadata inline until then) + a small enum'd core
   (metric, unit_concept, period) + a ``conditions`` mapping carrying every
   subset criterion (geography, program, subgroup axes, methodological
   variant). Conditions are open-vocabulary by design; metrics and unit
   concepts are closed vocabularies that adapters must fail loudly against.

3. **calibration_relationship is mandatory** — ``consumed_as_target`` /
   ``seed_source`` / ``held_out``. Only held_out rows may be published as
   validation wins; agreement on consumed targets is a tautology.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class Metric(str, Enum):
    ELIGIBLE_COUNT = "eligible_count"
    ELIGIBILITY_RATE = "eligibility_rate"
    PARTICIPANT_COUNT = "participant_count"
    PARTICIPATION_RATE = "participation_rate"
    PARTICIPATION_GAP_COUNT = "participation_gap_count"
    POVERTY_RATE = "poverty_rate"
    POVERTY_RATE_CHANGE = "poverty_rate_change"
    POVERTY_COUNT_CHANGE = "poverty_count_change"
    BENEFIT_COST = "benefit_cost"
    REVENUE_CHANGE = "revenue_change"
    CASELOAD = "caseload"
    ENROLLMENT = "enrollment"


class UnitConcept(str, Enum):
    PERSONS = "persons"
    ADULTS_18PLUS = "adults_18plus"
    CHILDREN_0THR4 = "children_0thr4"
    CHILDREN_UNDER_18 = "children_under_18"
    FAMILIES = "families"
    HOUSEHOLDS = "households"
    TAX_UNITS = "tax_units"
    SPM_UNITS = "spm_units"
    USD = "usd"
    SHARE = "share"


class TimeBasis(str, Enum):
    ANNUAL = "annual"
    AVERAGE_MONTH = "average_month"
    POINT_IN_TIME = "point_in_time"
    FISCAL_YEAR = "fiscal_year"


class CalibrationRelationship(str, Enum):
    CONSUMED_AS_TARGET = "consumed_as_target"
    SEED_SOURCE = "seed_source"
    HELD_OUT = "held_out"


class ComparisonStatus(str, Enum):
    COMPARABLE = "comparable"
    CONSTRUCTED = "constructed"
    CONCEPT_MISMATCH = "concept_mismatch"
    PE_GAP = "pe_gap"
    NOT_COMPUTED = "not_computed"


class DiagnosisClass(str, Enum):
    PE_GAP = "pe_gap"
    EXTERNAL_ISSUE = "external_issue"
    CONCEPT_MISMATCH = "concept_mismatch"
    VINTAGE = "vintage"
    UNDIAGNOSED = "undiagnosed"


def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


@dataclass(frozen=True)
class ReformRef:
    """The policy world a claim scores.

    framework: "baseline" | "policyengine_us" | "policyengine_uk" |
    "axiom" (reserved). For policyengine frameworks, ``reform`` is the
    parametric reform dict (period-keyed values) and ``baseline`` an
    optional non-current-law baseline reform dict.
    """

    framework: str = "baseline"
    reform: Optional[dict] = None
    baseline: Optional[dict] = None
    rulespec_ref: Optional[str] = None  # axiom, reserved

    # policyengine_us/_uk: executable parametric reform dicts (parameter
    # path -> period-keyed values). policyengine_us_inputs/_uk_inputs:
    # counterfactuals defined by INPUT-VARIABLE overrides (e.g. forcing
    # take-up flags), which are not expressible as parameter paths — the
    # dict is a descriptor {variable: value}, executed by the pipeline's
    # set_input machinery, not by a Reform class.
    VALID_FRAMEWORKS = (
        "baseline",
        "policyengine_us",
        "policyengine_uk",
        "policyengine_us_inputs",
        "policyengine_uk_inputs",
        "axiom",
    )

    def __post_init__(self):
        if self.framework not in self.VALID_FRAMEWORKS:
            raise ValueError(f"unknown reform framework: {self.framework}")
        if self.framework == "baseline" and (self.reform or self.rulespec_ref):
            raise ValueError("baseline reform carries no reform payload")
        if self.framework.startswith("policyengine") and not self.reform:
            raise ValueError(f"{self.framework} reform requires a reform dict")

    def key(self) -> str:
        return hashlib.sha256(
            _canonical(
                {
                    "framework": self.framework,
                    "reform": self.reform,
                    "baseline": self.baseline,
                    "rulespec_ref": self.rulespec_ref,
                }
            ).encode()
        ).hexdigest()[:16]

    def to_json(self) -> str:
        return _canonical(
            {
                "framework": self.framework,
                "reform": self.reform,
                "baseline": self.baseline,
                "rulespec_ref": self.rulespec_ref,
            }
        )

    @classmethod
    def from_json(cls, s: str) -> "ReformRef":
        return cls(**json.loads(s))


BASELINE = ReformRef()


@dataclass
class ExternalScore:
    """One claim by an external model, populace-target-style."""

    source: str  # publisher slug: urban_sotsn, cbo, jct, tpc, cpsp, ca_lao…
    metric: Metric
    unit_concept: UnitConcept
    period: int  # calendar/fiscal year the claim describes
    time_basis: TimeBasis
    value: Optional[float]  # None => suppressed
    conditions: dict = field(default_factory=dict)
    reform: ReformRef = field(default_factory=ReformRef)
    calibration_relationship: CalibrationRelationship = (
        CalibrationRelationship.HELD_OUT
    )
    source_model: Optional[str] = None  # attis, trim3, dynasim, taxcalc…
    ledger_fact: Optional[str] = None  # validation_comparator fact id
    source_column: Optional[str] = None  # the source's own name for it
    publication: dict = field(default_factory=dict)  # {title,url,date,vintage}
    value_kind: str = "count"  # count | share | usd
    status: str = "ok"  # ok | suppressed

    def __post_init__(self):
        self.metric = Metric(self.metric)
        self.unit_concept = UnitConcept(self.unit_concept)
        self.time_basis = TimeBasis(self.time_basis)
        self.calibration_relationship = CalibrationRelationship(
            self.calibration_relationship
        )
        self.reform = (
            self.reform
            if isinstance(self.reform, ReformRef)
            else ReformRef(**self.reform)
        )
        if self.value is None and self.status != "suppressed":
            raise ValueError("null value requires status='suppressed'")
        for k, v in self.conditions.items():
            if not isinstance(k, str) or not isinstance(v, str):
                raise ValueError("conditions must be str->str")

    def claim_id(self) -> str:
        """Stable id over (source, reform, metric, unit, period, basis,
        conditions) — invariant to condition ordering and to value."""
        return hashlib.sha256(
            _canonical(
                {
                    "source": self.source,
                    "reform_key": self.reform.key(),
                    "metric": self.metric.value,
                    "unit_concept": self.unit_concept.value,
                    "period": self.period,
                    "time_basis": self.time_basis.value,
                    "conditions": self.conditions,
                }
            ).encode()
        ).hexdigest()[:20]


@dataclass
class PEResult:
    """PolicyEngine's computation for a claim (history preserved per run)."""

    claim_id: str
    computed_value: Optional[float]
    status: ComparisonStatus
    engine_version: str
    data_bundle: str  # certified data build id
    pe_construction: str = ""  # machine-readable recipe
    run_id: str = ""
    computed_at: str = ""  # ISO timestamp, caller-supplied
    annotations: list = field(default_factory=list)

    def __post_init__(self):
        self.status = ComparisonStatus(self.status)
        if self.computed_value is None and self.status in (
            ComparisonStatus.COMPARABLE,
            ComparisonStatus.CONSTRUCTED,
        ):
            raise ValueError(f"{self.status.value} result requires a value")
