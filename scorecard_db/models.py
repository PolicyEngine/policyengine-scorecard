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
    POVERTY_COUNT = "poverty_count"
    BENEFIT_COST = "benefit_cost"
    REVENUE_CHANGE = "revenue_change"
    CASELOAD = "caseload"
    ENROLLMENT = "enrollment"
    # 2026-08-02 harvest extensions — recurring proposed_* metrics
    # (COLLATION worklist item 1). Distribution-table family: the value's
    # income concept (after-tax vs after-tax-and-transfer) rides in
    # conditions["income_concept"]; mean-vs-median in conditions["statistic"]
    # (absent = mean).
    PCT_CHANGE_AFTER_TAX_INCOME = "pct_change_after_tax_income"
    AVG_TAX_CHANGE_USD = "avg_tax_change_usd"
    AVG_CHANGE_AFTER_TAX_INCOME_USD = "avg_change_after_tax_income_usd"
    SHARE_WITH_TAX_CUT = "share_with_tax_cut"
    PRIMARY_DEFICIT_CHANGE = "primary_deficit_change"
    # Reserved for the JCX-45-25 tax-expenditure report (downloaded but
    # unstaged — needs a coordinate-aware parser; no rows yet).
    TAX_EXPENDITURE = "tax_expenditure"
    # CBO baseline-detail families (single-source but PE-comparable):
    # individual-income-tax return walk (conditions: tax, concept)…
    INCOME_AGGREGATE = "income_aggregate"
    DEDUCTION_AGGREGATE = "deduction_aggregate"
    TAX_LIABILITY = "tax_liability"
    RETURN_COUNT = "return_count"
    TAX_CREDITS_APPLIED = "tax_credits_applied"
    # …and program benefit statistics (conditions: program, per).
    AVERAGE_MONTHLY_BENEFIT = "average_monthly_benefit"
    MAXIMUM_MONTHLY_BENEFIT = "maximum_monthly_benefit"
    AVERAGE_WEEKLY_BENEFIT = "average_weekly_benefit"
    FIRST_PAYMENT_COUNT = "first_payment_count"


class UnitConcept(str, Enum):
    PERSONS = "persons"
    ADULTS_18PLUS = "adults_18plus"
    CHILDREN_0THR4 = "children_0thr4"
    CHILDREN_UNDER_6 = "children_under_6"
    CHILDREN_UNDER_18 = "children_under_18"
    FAMILIES = "families"
    HOUSEHOLDS = "households"
    TAX_UNITS = "tax_units"
    SPM_UNITS = "spm_units"
    USD = "usd"
    # Per-unit dollar statistics (averages/medians of tax change or
    # income change) — distinct from USD aggregates so queries cannot
    # accidentally sum averages, and split by denominator population
    # (TPC publishes per tax unit; PWBM per household).
    USD_PER_TAX_UNIT = "usd_per_tax_unit"
    USD_PER_HOUSEHOLD = "usd_per_household"
    SHARE = "share"
    # Values on the 0–100 scale (share × 100). Adapters normalize every
    # pct_change_after_tax_income / share_with_tax_cut row to PERCENT;
    # SHARE stays the fraction convention for rates (poverty, take-up).
    PERCENT = "percent"


# Standardized conditions vocabulary (COLLATION worklist item 4).
# Conditions stay open-vocabulary by design; these are the keys adapters
# MUST use when the concept applies, so cross-source queries join cleanly.
# income_group      verbatim source group label ("Lowest Quintile", "p99_99.9")
# income_axis       the axis definition ("expanded_cash_income_percentile",
#                   "market_income_percentile", "agi_expanded_income")
# income_concept    "after_tax_income" | "after_tax_and_transfer_income"
# scoring           "conventional" | "dynamic" | "static" | source-stated
#                   variants (e.g. "with_import_demand_response")
# baseline_policy   normalized slug mirroring ReformRef.baseline["policy"];
#                   only present when the baseline is not current law
# option            source option label within an options table
# statistic         "median" when the value is a median (absent = mean)
# window_kind       "total" | "annual_average" on period-range claims
# month             "YYYY-MM" for monthly series
# data_vintage      dataset base when it is not the obvious current one
STANDARD_CONDITIONS = frozenset(
    {
        "geography",
        "program",
        "subgroup",
        "income_group",
        "income_axis",
        "income_concept",
        "scoring",
        "baseline_policy",
        "option",
        "statistic",
        "window_kind",
        "month",
        "data_vintage",
    }
)


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
    "policy_ref" | "axiom" (reserved). For policyengine frameworks,
    ``reform`` is the parametric reform dict (period-keyed values) and
    ``baseline`` an optional non-current-law baseline reform dict.

    ``policy_ref`` names an external policy world that is not (yet)
    encoded as an executable PolicyEngine reform: ``reform`` is a
    descriptor dict whose required ``policy`` key is a stable slug for the
    scored world (a bill, bill version, or option), plus free detail keys
    (law, version, jcx, option, …). ``baseline`` is an optional descriptor
    of the same shape naming a non-current-law baseline world
    (e.g. {"policy": "tcja_extension"}); absent means current law.
    Baseline variants are load-bearing (COLLATION worklist item 3): they
    live here, never only in conditions — conditions["baseline_policy"]
    mirrors ``baseline["policy"]`` for queryability.
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
        "policy_ref",
        "axiom",
    )

    def __post_init__(self):
        if self.framework not in self.VALID_FRAMEWORKS:
            raise ValueError(f"unknown reform framework: {self.framework}")
        if self.framework == "baseline" and (self.reform or self.rulespec_ref):
            raise ValueError("baseline reform carries no reform payload")
        if self.framework.startswith("policyengine") and not self.reform:
            raise ValueError(f"{self.framework} reform requires a reform dict")
        if self.framework == "policy_ref":
            if self.rulespec_ref:
                raise ValueError("policy_ref carries no rulespec_ref")
            for name, desc in (("reform", self.reform),
                               ("baseline", self.baseline)):
                if name == "reform" and desc is None:
                    raise ValueError(
                        "policy_ref requires a reform descriptor dict"
                    )
                if desc is not None and not (
                    isinstance(desc, dict)
                    and isinstance(desc.get("policy"), str)
                    and desc["policy"]
                ):
                    raise ValueError(
                        f"policy_ref {name} descriptor needs a 'policy' slug"
                    )

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
    # Multi-year window claims (10-year budget totals, decade averages —
    # COLLATION worklist item 2). Both set or neither; convention:
    # period == period_end (the window's last year), so single-year sort
    # order stays meaningful. conditions["window_kind"] says whether the
    # value is the window "total" or an "annual_average".
    period_start: Optional[int] = None
    period_end: Optional[int] = None

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
        if (self.period_start is None) != (self.period_end is None):
            raise ValueError("period_start and period_end come together")
        if self.period_start is not None:
            if self.period_start >= self.period_end:
                raise ValueError("period_start must precede period_end")
            if self.period != self.period_end:
                raise ValueError(
                    "window claims set period == period_end "
                    f"(got period={self.period}, end={self.period_end})"
                )

    def claim_id(self) -> str:
        """Stable id over (source, reform, metric, unit, period, basis,
        conditions) — invariant to condition ordering and to value.
        period_start/period_end enter the hash only when set, so
        pre-window claim ids are unchanged."""
        key = {
            "source": self.source,
            "reform_key": self.reform.key(),
            "metric": self.metric.value,
            "unit_concept": self.unit_concept.value,
            "period": self.period,
            "time_basis": self.time_basis.value,
            "conditions": self.conditions,
        }
        if self.period_start is not None:
            key["period_start"] = self.period_start
            key["period_end"] = self.period_end
        return hashlib.sha256(_canonical(key).encode()).hexdigest()[:20]


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
