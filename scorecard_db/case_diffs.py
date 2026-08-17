"""Mode-3 case-diff models: record-level comparisons against household
oracles (UKMOD/EUROMOD via the JRC connector, NBER TAXSIM).

One schema for every mode-3 lane (#5, #41) — the contract lives at
sources/ukmod-cases/SCHEMA.md and is deliberately engine-agnostic: the
``country`` field on a case and the ``oracle`` field on a result are what
keep ``ukmod-cases`` and ``taxsim-cases`` on a single schema instead of two.

Design, same doctrine as :mod:`scorecard_db.models`:

1. **Closed vocabularies fail loudly.** Oracles, diff classifications,
   variable classes, household/person input keys — all closed sets; unknown
   values raise instead of passing through.
2. **Cases are inputs only.** A ``CaseSpec`` never embeds expected output
   values; both sides of every comparison come from engine runs, so the
   battery cannot smuggle in hand-computed truth.
3. **The classifier never flatters.** ``classify`` emits match buckets, the
   two null-side scope buckets, or ``unclassified``; ``oracle_difference``
   and ``rounding`` exist only as adjudicated outcomes with a traceable
   writeup — misses stay visible until someone explains them.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


class Oracle(str, Enum):
    UKMOD = "ukmod"
    TAXSIM = "taxsim"


class VariableClass(str, Enum):
    CURRENCY = "currency"
    BOOLEAN = "boolean"


class DiffClassification(str, Enum):
    MATCH_EXACT = "match_exact"
    MATCH_WITHIN_TOLERANCE = "match_within_tolerance"
    PE_GAP = "pe_gap"
    ORACLE_DIFFERENCE = "oracle_difference"
    POLICY_SCOPE_MISMATCH = "policy_scope_mismatch"
    ROUNDING = "rounding"
    UNCLASSIFIED = "unclassified"


# Classifications the automatic classifier may emit; the rest
# (oracle_difference, rounding, and pe_gap/policy_scope_mismatch on
# numeric-vs-numeric rows) require adjudication with a writeup.
CLASSIFIER_EMITTED = frozenset(
    {
        DiffClassification.MATCH_EXACT,
        DiffClassification.MATCH_WITHIN_TOLERANCE,
        DiffClassification.PE_GAP,
        DiffClassification.POLICY_SCOPE_MISMATCH,
        DiffClassification.UNCLASSIFIED,
    }
)

# Adjudicated-only outcomes: a row may carry one of these only with a
# traceable writeup in ``annotations`` (SCHEMA.md — "misses stay visible
# until someone explains them").
ADJUDICATED_ONLY = frozenset(
    {
        DiffClassification.ORACLE_DIFFERENCE,
        DiffClassification.ROUNDING,
    }
)

# Currency tolerance: benefit rules are stated weekly to the penny and
# comparisons are annual, so 52 x GBP/USD 0.01. Booleans agree or they
# don't. Wider slack is never a tolerance bump — a documented oracle
# rounding rule adjudicates to ROUNDING instead (SCHEMA.md).
DEFAULT_TOLERANCES: dict[VariableClass, float] = {
    VariableClass.CURRENCY: 0.52,
    VariableClass.BOOLEAN: 0.0,
}

VALID_COUNTRIES = frozenset({"UK", "US"})

VALID_TENURES = frozenset(
    {"owned_outright", "owned_mortgage", "rented_social", "rented_private"}
)

# The engine-agnostic household input vocabulary (SCHEMA.md). Each mode-3
# connector owns the mapping to its engines' variables; the battery speaks
# only these keys. Extending the vocabulary means extending these sets AND
# documenting the key in SCHEMA.md.
PERSON_NUMERIC_KEYS = frozenset(
    {
        "employment_income",
        "self_employment_income",
        "pension_income",
        "state_pension",
        "savings_income",
        "capital",
        "employee_pension_contributions",
        "hours_worked_per_week",
    }
)
PERSON_BOOL_KEYS = frozenset(
    {"salary_sacrifice", "is_disabled", "is_carer", "gainfully_self_employed"}
)
PERSON_KEYS = (
    frozenset({"age", "date_of_birth"}) | PERSON_NUMERIC_KEYS | PERSON_BOOL_KEYS
)

HOUSEHOLD_KEYS = frozenset(
    {"people", "benefit_units", "region", "tenure", "rent", "council_tax"}
)


def _validate_person(person_id: str, person: dict) -> None:
    if not isinstance(person, dict):
        raise ValueError(f"person {person_id!r} must be a mapping")
    unknown = set(person) - PERSON_KEYS
    if unknown:
        raise ValueError(f"person {person_id!r} has unknown keys: {sorted(unknown)}")
    age = person.get("age")
    if not isinstance(age, int) or isinstance(age, bool) or age < 0:
        raise ValueError(f"person {person_id!r} needs an integer age >= 0")
    dob = person.get("date_of_birth")
    if dob is not None and not (
        isinstance(dob, str) and len(dob) == 10 and dob[4] == "-" and dob[7] == "-"
    ):
        raise ValueError(f"person {person_id!r} date_of_birth must be YYYY-MM-DD")
    for key in PERSON_NUMERIC_KEYS & set(person):
        v = person[key]
        if isinstance(v, bool) or not isinstance(v, (int, float)) or v < 0:
            raise ValueError(f"person {person_id!r} {key} must be a number >= 0")
    for key in PERSON_BOOL_KEYS & set(person):
        if not isinstance(person[key], bool):
            raise ValueError(f"person {person_id!r} {key} must be a boolean")


def _validate_household(household: dict) -> None:
    if not isinstance(household, dict):
        raise ValueError("household must be a mapping")
    unknown = set(household) - HOUSEHOLD_KEYS
    if unknown:
        raise ValueError(f"household has unknown keys: {sorted(unknown)}")
    people = household.get("people")
    if not isinstance(people, dict) or not people:
        raise ValueError("household.people must be a non-empty mapping")
    for person_id, person in people.items():
        _validate_person(person_id, person)
    units = household.get("benefit_units")
    if not isinstance(units, list) or not units:
        raise ValueError("household.benefit_units must be a non-empty list")
    assigned: list[str] = []
    for unit in units:
        if not isinstance(unit, dict) or set(unit) != {"adults", "children"}:
            raise ValueError("each benefit unit needs exactly adults + children lists")
        for role in ("adults", "children"):
            members = unit[role]
            if not isinstance(members, list) or not all(
                isinstance(m, str) and m for m in members
            ):
                raise ValueError(
                    f"benefit unit {role} must be a list of person ids, got {members!r}"
                )
        if not unit["adults"]:
            raise ValueError("each benefit unit needs at least one adult")
        assigned.extend(unit["adults"])
        assigned.extend(unit["children"])
    if sorted(assigned) != sorted(people):
        raise ValueError(
            "benefit units must assign every person exactly once "
            f"(people={sorted(people)}, assigned={sorted(assigned)})"
        )
    tenure = household.get("tenure")
    if tenure is not None and tenure not in VALID_TENURES:
        raise ValueError(f"unknown tenure: {tenure!r}")
    for key in ("rent", "council_tax"):
        v = household.get(key)
        if v is not None and (
            isinstance(v, bool) or not isinstance(v, (int, float)) or v < 0
        ):
            raise ValueError(f"household.{key} must be a number >= 0")
    if household.get("rent", 0) and tenure in ("owned_outright", "owned_mortgage"):
        raise ValueError("owner-occupier households carry no rent")


@dataclass
class CaseSpec:
    """One curated hypothetical household: inputs + expected focus only."""

    case_id: str
    description: str
    policy_year: int
    country: str
    household: dict
    expected_focus: list
    rationale: str = ""

    def __post_init__(self):
        if not self.case_id or not isinstance(self.case_id, str):
            raise ValueError("case_id must be a non-empty string")
        if self.country not in VALID_COUNTRIES:
            raise ValueError(f"unknown country: {self.country!r}")
        if not self.case_id.startswith(self.country.lower() + "-"):
            raise ValueError(
                f"case_id {self.case_id!r} must be prefixed '{self.country.lower()}-'"
            )
        if (
            not isinstance(self.policy_year, int)
            or not 1990 <= self.policy_year <= 2100
        ):
            raise ValueError(f"implausible policy_year: {self.policy_year!r}")
        if (
            not isinstance(self.expected_focus, list)
            or not self.expected_focus
            or not all(isinstance(v, str) and v for v in self.expected_focus)
        ):
            raise ValueError("expected_focus must be a non-empty list of variables")
        _validate_household(self.household)


@dataclass
class CaseResult:
    """PE vs oracle for one case x output variable x run (history kept)."""

    case_id: str
    variable: str
    pe_value: Optional[float]
    oracle_value: Optional[float]
    oracle: Oracle
    engine_version: str
    oracle_version: str
    computed_at: str  # ISO timestamp, caller-supplied
    classification: DiffClassification
    abs_diff: Optional[float] = None
    tolerance: Optional[float] = None
    annotations: list = field(default_factory=list)

    def __post_init__(self):
        self.oracle = Oracle(self.oracle)
        self.classification = DiffClassification(self.classification)
        if not self.case_id or not self.variable:
            raise ValueError("case_id and variable are required")
        if not isinstance(self.annotations, list) or not all(
            isinstance(a, str) and a.strip() for a in self.annotations
        ):
            raise ValueError("annotations must be a list of non-empty strings")
        both_numeric = self.pe_value is not None and self.oracle_value is not None
        if both_numeric:
            expected = abs(self.pe_value - self.oracle_value)
            if self.abs_diff is None or abs(self.abs_diff - expected) > 1e-9:
                raise ValueError(
                    f"abs_diff must equal |pe_value - oracle_value| "
                    f"(got {self.abs_diff}, expected {expected})"
                )
        elif self.abs_diff is not None:
            raise ValueError("abs_diff requires both values")
        if self.pe_value is None and self.classification != DiffClassification.PE_GAP:
            raise ValueError("null pe_value requires classification=pe_gap")
        if (
            self.oracle_value is None
            and self.pe_value is not None
            and self.classification != DiffClassification.POLICY_SCOPE_MISMATCH
        ):
            raise ValueError(
                "null oracle_value requires classification=policy_scope_mismatch"
            )
        if self.classification == DiffClassification.MATCH_EXACT and (
            not both_numeric or self.abs_diff != 0.0
        ):
            raise ValueError("match_exact requires identical numeric values")
        if self.classification == DiffClassification.MATCH_WITHIN_TOLERANCE:
            if (
                isinstance(self.tolerance, bool)
                or not isinstance(self.tolerance, (int, float))
                or self.tolerance <= 0
            ):
                raise ValueError(
                    "match_within_tolerance requires the numeric tolerance "
                    "the row was judged against (tolerance > 0)"
                )
            if not both_numeric or not 0 < self.abs_diff <= self.tolerance:
                raise ValueError(
                    "match_within_tolerance requires 0 < abs_diff <= tolerance "
                    f"(abs_diff={self.abs_diff}, tolerance={self.tolerance})"
                )
        elif self.tolerance is not None:
            raise ValueError(
                "tolerance is recorded only on match_within_tolerance rows"
            )
        if self.classification in ADJUDICATED_ONLY and not self.annotations:
            raise ValueError(
                f"{self.classification.value} is an adjudicated outcome and "
                "requires a writeup in annotations (SCHEMA.md)"
            )


def classify(
    pe_value: Optional[float],
    oracle_value: Optional[float],
    variable_class: VariableClass,
    tolerance_table: dict = DEFAULT_TOLERANCES,
) -> DiffClassification:
    """Automatic first-pass classification of one (pe, oracle) pair.

    Emits only ``CLASSIFIER_EMITTED`` buckets: null sides map to the scope
    buckets, exact/tolerance matches to the match buckets, and everything
    above tolerance to ``unclassified`` — the adjudication queue, never a
    silently flattering default.
    """
    variable_class = VariableClass(variable_class)
    if pe_value is None:
        return DiffClassification.PE_GAP
    if oracle_value is None:
        return DiffClassification.POLICY_SCOPE_MISMATCH
    if variable_class not in tolerance_table:
        raise ValueError(f"no tolerance for variable class {variable_class.value!r}")
    diff = abs(float(pe_value) - float(oracle_value))
    if diff == 0.0:
        return DiffClassification.MATCH_EXACT
    if diff <= tolerance_table[variable_class]:
        return DiffClassification.MATCH_WITHIN_TOLERANCE
    return DiffClassification.UNCLASSIFIED


BATTERY_KEYS = frozenset({"schema", "description", "cases"})
CASE_KEYS = frozenset(
    {
        "case_id",
        "description",
        "policy_year",
        "country",
        "household",
        "expected_focus",
        "rationale",
    }
)


def load_battery(path) -> list[CaseSpec]:
    """Load and validate a case battery file; every defect raises."""
    raw = json.loads(Path(path).read_text())
    if not isinstance(raw, dict):
        raise ValueError("battery must be a JSON object")
    unknown = set(raw) - BATTERY_KEYS
    if unknown:
        raise ValueError(f"battery has unknown keys: {sorted(unknown)}")
    if not isinstance(raw.get("cases"), list) or not raw["cases"]:
        raise ValueError("battery.cases must be a non-empty list")
    cases = []
    for entry in raw["cases"]:
        if not isinstance(entry, dict):
            raise ValueError("each case must be a JSON object")
        unknown = set(entry) - CASE_KEYS
        if unknown:
            raise ValueError(
                f"case {entry.get('case_id')!r} has unknown keys: {sorted(unknown)}"
            )
        cases.append(CaseSpec(**entry))
    ids = [c.case_id for c in cases]
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    if dupes:
        raise ValueError(f"duplicate case_ids: {dupes}")
    return cases
