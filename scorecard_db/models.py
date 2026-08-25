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
   validation comparisons; agreement on consumed targets is a tautology.
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
    # UK externals ingest (#33). Levels, not changes: taxpayer counts are
    # individuals with positive liability (not returns — the UK has no
    # joint filing), unclaimed amounts are the DWP take-up publication's
    # entitled-non-recipient aggregates, and the income-distribution
    # family carries UKMOD's Gini/quantile statistics.
    TAXPAYER_COUNT = "taxpayer_count"
    AVERAGE_TAX_RATE = "average_tax_rate"
    AVERAGE_TAX_AMOUNT = "average_tax_amount"
    UNCLAIMED_BENEFIT_AMOUNT = "unclaimed_benefit_amount"
    GINI = "gini"
    INCOME_STATISTIC = "income_statistic"
    INCOME_SHARE = "income_share"
    # UK UC-deductions harvest (#39/#21). cash_requirement_change is a
    # PSNCR effect — a cash measure, deliberately distinct from
    # revenue_change (PSNB): the FRR has no PSNB impact and the boundary
    # must be unconfusable. gainer_count / average_annual_gain are the
    # distributional-impact vocabulary of UK fiscal-event documents.
    CASH_REQUIREMENT_CHANGE = "cash_requirement_change"
    GAINER_COUNT = "gainer_count"
    AVERAGE_ANNUAL_GAIN = "average_annual_gain"


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
    # UK externals ingest (#33): GBP mirrors USD (raw pounds, never
    # billions); BENEFIT_UNITS is the DWP family concept (single adult or
    # couple plus dependents) matching PE UK's benunit entity; CHILDREN is
    # the generic dependent-child concept (child benefit covers children
    # up to 19 in approved education, so no age-bounded member fits).
    GBP = "gbp"
    # Belgium JRC country-report ingest: EUR is the aggregate currency
    # concept, mirroring USD/GBP. Source EUR millions are normalized to
    # raw euros before persistence.
    EUR = "eur"
    BENEFIT_UNITS = "benefit_units"
    CHILDREN = "children"
    # Per-period GBP amounts and index statistics are their own unit
    # concepts (adjudication blocker: a weekly amount labeled bare GBP and
    # a Gini labeled SHARE both misstate what the number is).
    GBP_PER_WEEK = "gbp_per_week"
    GBP_PER_MONTH = "gbp_per_month"
    INDEX_0_1 = "index_0_1"
    # Per-household GBP statistic (the UK mirror of USD_PER_HOUSEHOLD,
    # same rule: averages must never be summable as aggregates). The
    # FRR family's £420 average annual gain is per household per year.
    GBP_PER_HOUSEHOLD = "gbp_per_household"


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
#
# UK additions (2026-08-02 UK harvest; COLLATION UK worklist items 2-3):
# fy                normalized fiscal-year label "2026-27" (Apr–Mar). The
#                   integer period is the FY END year — the convention of
#                   every LIVE claim in the DB (ingest_reform_validation:
#                   "period is the ending year"; e.g. a FY2027-28 fiscal
#                   note keys 2028). Archived harvest NOTES staged some
#                   sources by START year, so any ingest built from those
#                   selectors (e.g. #52's deductions) must translate at
#                   staging time, never inherit the archive's keys.
#                   PE-UK's engine time_period uses the START year; that is
#                   RESULT-side provenance (engine_time_period), recorded at
#                   attach with the one-year offset asserted — never a claim
#                   identity.
# basis             source's own designation: "outturn" | "forecast" |
#                   "projected" | "provisional" | "unstated". Admin outturn
#                   rows never reach external_scores (ledger routing rule).
# income_concept    UK distribution rows: "BHC" | "AHC" (load-bearing on
#                   every HBAI-family statistic), alongside the US values.
# equivalisation    e.g. "modified_oecd" — load-bearing with income_concept.
# poverty_measure   "relative" | "absolute" (+ poverty_line, e.g.
#                   "60pct_median"; poverty_line_anchor for absolute lines)
# fiscal_event      "autumn_budget_2024" | "budget_2025" | … — the event a
#                   costing/measure belongs to
# measure           verbatim measure title on scored fiscal-event lines
#                   (mirrors the policy_ref slug, which hashes this title)
# series            UKMOD validation-block column: "ukmod" |
#                   "official_estimate" | "input_data" | "hbai"
# edition           publication edition when two editions of the same
#                   statistic are staged (HBAI FYE2025 vs admin-linked)
# bound             "lower" | "central" | "upper" on estimate ranges
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
        # Cross-model epistemics (ruling 2026-08-02): every new benchmark
        # names its class explicitly; Belgium's JRC model claims use
        # different_model, while the routed statistical rows carry
        # administrative_fact in Ledger staging.
        "benchmark_class",
        # Source/report semantics used by the Belgium country-report lane.
        "series",
        "policy_system_year",
        "reference_year",
        "assessment_level",
        "population_scope",
        "tax_scope",
        "contribution_payer",
        "benefit_scope",
        "source_scale",
        # Belgium model-claim universe pins (sol review of #82): the modeled
        # EUROMOD universe is EU-SILC private households (Table 3.1, p. 97)
        # from database BE_2022_c1 (SILC 2022 collection, income reference
        # year 2021) — never presented as an unqualified national frame.
        "population_frame",
        "input_database",
        # simulation_year: the uprating target year of a non-simulated
        # survey-input Ledger fact (Belgium bun row) — deliberately distinct
        # from reference_year (statistical outturns) and policy_system_year
        # (executed model output).
        "simulation_year",
        # UK externals ingest (#33)
        # country          "UK" on every UK claim (absent = US)
        # fy               UK financial-year label ("2026-27") alongside the
        #                  integer period (= the FY end year)
        # housing_costs    "bhc" | "ahc" on HBAI-concept poverty claims
        # poverty_line     "relative" | "absolute" (HBAI) or the percent-of-
        #                  median threshold ("50" | "60" | "70", UKMOD)
        # basis            "caseload" | "expenditure" on take-up rates;
        #                  "outturn" | "forecast" on OBR baseline lines
        # welfare_cap      "in_welfare_cap" | "outside_welfare_cap"
        # quantile         "q1".."q5" on distribution statistics
        # per              period unit of per-unit money statistics ("week",
        #                  "month" — CBO's benefit statistics precedent)
        # component        sub-quantity of a metric ("unclaimed" on DWP
        #                  amount statistics)
        # aggregate_level  OBR roll-up marker: "component" (leaf) |
        #                  "subtotal" | "total" — without it sibling
        #                  benefit_cost rows double-count when summed
        # parent           program slug of the aggregate an OBR row rolls
        #                  into (absent on the top-level total)
        # equivalisation   income-equivalisation scale on distribution
        #                  statistics: "modified_oecd" (BHC) |
        #                  "modified_oecd_companion_ahc" (AHC) — load-
        #                  bearing beside housing_costs
        # poverty_line_anchor  which FIXED median an absolute low-income
        #                  line uses: "fye_2011" | "fye_2025" |
        #                  "mixed_fye2011_fye2025" (a multi-year window
        #                  straddling the FYE-2025 re-anchor)
        # fiscal_measure   which fiscal aggregate a change claim moves:
        #                  "psncr" on the FRR family (a cash-requirement
        #                  effect, deliberately NOT PSNB — PQ UIN 3751)
        "measure",
        "fiscal_measure",
        "country",
        "fy",
        "housing_costs",
        "poverty_line",
        "poverty_line_anchor",
        "equivalisation",
        "basis",
        "welfare_cap",
        "quantile",
        "per",
        "component",
        "aggregate_level",
        "parent",
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


class BenchmarkClass(str, Enum):
    """Epistemic relationship between the benchmark and our model.

    This travels in claim conditions (and on routed Ledger facts) rather
    than becoming a second metric/status system.
    """

    ADMINISTRATIVE_FACT = "administrative_fact"
    SAME_ASSUMPTIONS = "same_assumptions"
    DIFFERENT_MODEL = "different_model"


class ComparisonStatus(str, Enum):
    COMPARABLE = "comparable"
    CONSTRUCTED = "constructed"
    CONCEPT_MISMATCH = "concept_mismatch"
    PE_GAP = "pe_gap"
    NOT_COMPUTED = "not_computed"


class DiagnosisClass(str, Enum):
    """Adjudication classes under the descriptive register (issue #9,
    Max 2026-08-02): the Scorecard is descriptive by default. PE_GAP and
    EXTERNAL_ISSUE are normative and therefore GATED — they require a
    citable known issue in action_link (a GitHub issue, published erratum,
    internal contradiction, or tracked correction); divergence alone never
    qualifies. METHODOLOGICAL_DIFFERENCE is strictly descriptive: the
    models differ because of documented choices on both sides, stated,
    sourced, and left there — no convergence or defended-departure
    framing in either direction."""

    PE_GAP = "pe_gap"
    EXTERNAL_ISSUE = "external_issue"
    CONCEPT_MISMATCH = "concept_mismatch"
    METHODOLOGICAL_DIFFERENCE = "methodological_difference"
    VINTAGE = "vintage"
    UNDIAGNOSED = "undiagnosed"


# Diagnosis classes that may only be assigned with a citable known issue.
GATED_DIAGNOSIS_CLASSES = frozenset(
    {DiagnosisClass.PE_GAP, DiagnosisClass.EXTERNAL_ISSUE}
)


def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


# The null baseline descriptor: current law at the source's scoring date.
CURRENT_LAW_DESCRIPTOR = {"policy": "current_law"}


def baseline_key(descriptor: dict) -> str:
    """Stable key over a baseline descriptor dict (issue #13). The same
    descriptor shape ReformRef.baseline carries; {"policy": "current_law"}
    keys the null baseline."""
    if not isinstance(descriptor, dict):
        raise ValueError(f"baseline descriptor must be a dict: {descriptor!r}")
    policy = descriptor.get("policy")
    if not (isinstance(policy, str) and policy.strip()):
        raise ValueError(
            f"baseline descriptor needs a nonempty string 'policy' slug: {descriptor!r}"
        )
    return hashlib.sha256(_canonical(descriptor).encode()).hexdigest()[:16]


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
            for name, desc in (("reform", self.reform), ("baseline", self.baseline)):
                if name == "reform" and desc is None:
                    raise ValueError("policy_ref requires a reform descriptor dict")
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

    def baseline_descriptor(self) -> dict:
        """The baseline world this reform is scored against, as a
        descriptor dict. Absent baseline means current law — the JCT /
        HMT-costing convention: scored against the law in force at
        publication (the announcement vintage rides in conditions such as
        fiscal_event / data_vintage, not in the baseline world)."""
        return self.baseline if self.baseline is not None else CURRENT_LAW_DESCRIPTOR

    def baseline_key(self) -> str:
        """First-class baseline identity (issue #13): a stable hash of the
        baseline descriptor, FK into the baselines registry. Additive
        projection only — claim_id/key() hashing is unchanged."""
        return baseline_key(self.baseline_descriptor())

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
    calibration_relationship: CalibrationRelationship = CalibrationRelationship.HELD_OUT
    source_model: Optional[str] = None  # attis, trim3, dynasim, taxcalc…
    ledger_fact: Optional[str] = None  # validation_comparator fact id
    source_column: Optional[str] = None  # the source's own name for it
    publication: dict = field(default_factory=dict)  # {title,url,date,vintage}
    value_kind: str = "count"  # count | share | percent | index | usd | gbp | eur
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
    """PolicyEngine's computation for a claim (history preserved per run).

    baseline_key records the baseline world the run ACTUALLY executed
    (issue #13 point 5) — e.g. the two-child-limit runs execute a
    pre_ab2025 reinstated counterfactual as their baseline, not current
    law. None on legacy rows only; new ingests must pass it, and the
    comparisons view refuses to render plain agreement when it differs
    from the claim's baseline."""

    claim_id: str
    computed_value: Optional[float]
    status: ComparisonStatus
    engine_version: str
    data_bundle: str  # certified data build id
    pe_construction: str = ""  # machine-readable recipe
    run_id: str = ""
    computed_at: str = ""  # ISO timestamp, caller-supplied
    annotations: list = field(default_factory=list)
    baseline_key: Optional[str] = None  # baseline actually executed

    def __post_init__(self):
        self.status = ComparisonStatus(self.status)
        if self.computed_value is None and self.status in (
            ComparisonStatus.COMPARABLE,
            ComparisonStatus.CONSTRUCTED,
        ):
            raise ValueError(f"{self.status.value} result requires a value")
