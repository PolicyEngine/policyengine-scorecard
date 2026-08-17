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
from datetime import date
from enum import Enum
from pathlib import Path
from typing import Optional

# Contract version for the battery file and result rows. Bump on any
# breaking change to the vocabularies or row shape so stored artifacts
# can be migrated explicitly instead of silently reinterpreted.
SCHEMA_VERSION = 1


class Oracle(str, Enum):
    UKMOD = "ukmod"
    TAXSIM = "taxsim"
    # Official-calculator oracles (#63): gov.uk estimators and production
    # benefit calculators, read manually or via terms-compliant access.
    GOVUK_INCOME_TAX_ESTIMATOR = "govuk_income_tax_estimator"
    GOVUK_HICBC_CALCULATOR = "govuk_hicbc_calculator"
    POLICY_IN_PRACTICE_BOC = "policy_in_practice_boc"
    ENTITLEDTO = "entitledto"
    TURN2US = "turn2us"


# Calculator oracles are live services with no release versioning, so a
# result's oracle_version must carry the READING DATE (YYYY-MM-DD) and the
# reading itself must be archived (screenshot / saved page) per SCHEMA.md.
# Model oracles (UKMOD, TAXSIM) keep their release-string versioning.
CALCULATOR_ORACLES = frozenset(
    {
        Oracle.GOVUK_INCOME_TAX_ESTIMATOR,
        Oracle.GOVUK_HICBC_CALCULATOR,
        Oracle.POLICY_IN_PRACTICE_BOC,
        Oracle.ENTITLEDTO,
        Oracle.TURN2US,
    }
)


def _contains_iso_date(s: str) -> bool:
    for i in range(len(s) - 9):
        chunk = s[i : i + 10]
        if (
            chunk[4] == "-"
            and chunk[7] == "-"
            and chunk[:4].isdigit()
            and chunk[5:7].isdigit()
            and chunk[8:10].isdigit()
        ):
            return True
    return False


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
    if dob is not None:
        # a real calendar date, not just the YYYY-MM-DD shape
        # ("2026-13-40" must fail)
        try:
            if not (isinstance(dob, str) and len(dob) == 10):
                raise ValueError
            date.fromisoformat(dob)
        except ValueError:
            raise ValueError(
                f"person {person_id!r} date_of_birth must be a real "
                f"YYYY-MM-DD date, got {dob!r}"
            ) from None
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
    # Which tolerance rule applied — persisted so a stored row can be
    # re-classified/audited without inferring the class from the
    # free-text variable name.
    variable_class: Optional[VariableClass] = None
    annotations: list = field(default_factory=list)
    schema_version: int = SCHEMA_VERSION

    def __post_init__(self):
        self.oracle = Oracle(self.oracle)
        self.classification = DiffClassification(self.classification)
        if self.variable_class is not None:
            self.variable_class = VariableClass(self.variable_class)
        if self.schema_version != SCHEMA_VERSION:
            raise ValueError(
                f"schema_version {self.schema_version!r} is not the current "
                f"contract version {SCHEMA_VERSION}; migrate explicitly"
            )
        if not self.case_id or not self.variable:
            raise ValueError("case_id and variable are required")
        if not isinstance(self.oracle_version, str) or not self.oracle_version.strip():
            raise ValueError("oracle_version is required (release string or date)")
        if self.oracle in CALCULATOR_ORACLES and not _contains_iso_date(
            self.oracle_version
        ):
            raise ValueError(
                f"{self.oracle.value} is a live calculator: oracle_version must "
                "carry the reading date (YYYY-MM-DD), and the reading must be "
                "archived per SCHEMA.md"
            )
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

    @classmethod
    def from_classification(
        cls,
        *,
        case_id: str,
        variable: str,
        pe_value: Optional[float],
        oracle_value: Optional[float],
        variable_class: VariableClass,
        oracle: Oracle,
        engine_version: str,
        oracle_version: str,
        computed_at: str,
        tolerance_table: dict = DEFAULT_TOLERANCES,
    ) -> "CaseResult":
        """The one wiring path from ``classify`` to a stored row.

        Derives abs_diff, threads the exact tolerance ``classify`` judged
        against (only onto match_within_tolerance rows, per the field
        contract), and persists the variable class — so no caller ever
        re-derives the tolerance by hand and passes the wrong one.
        """
        variable_class = VariableClass(variable_class)
        classification = classify(
            pe_value, oracle_value, variable_class, tolerance_table
        )
        both = pe_value is not None and oracle_value is not None
        abs_diff = abs(float(pe_value) - float(oracle_value)) if both else None
        tolerance = (
            float(tolerance_table[variable_class])
            if classification == DiffClassification.MATCH_WITHIN_TOLERANCE
            else None
        )
        return cls(
            case_id=case_id,
            variable=variable,
            pe_value=pe_value,
            oracle_value=oracle_value,
            oracle=oracle,
            engine_version=engine_version,
            oracle_version=oracle_version,
            computed_at=computed_at,
            classification=classification,
            abs_diff=abs_diff,
            tolerance=tolerance,
            variable_class=variable_class,
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


BATTERY_KEYS = frozenset({"schema", "schema_version", "description", "cases"})
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
    if raw.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(
            f"battery schema_version must be {SCHEMA_VERSION}, "
            f"got {raw.get('schema_version')!r}"
        )
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


CALCULATOR_SET_KEYS = frozenset({"schema", "description", "entries"})
CALCULATOR_ENTRY_KEYS = frozenset({"case_id", "oracles", "notes"})


def load_calculator_set(path, battery_cases) -> list[dict]:
    """Load the calculator starter set (#63); every defect raises.

    Each entry names a battery case and the >= 2 calculator oracles it is
    to be entered into — a work list for manual readings, never results.
    """
    raw = json.loads(Path(path).read_text())
    if not isinstance(raw, dict):
        raise ValueError("calculator set must be a JSON object")
    unknown = set(raw) - CALCULATOR_SET_KEYS
    if unknown:
        raise ValueError(f"calculator set has unknown keys: {sorted(unknown)}")
    entries = raw.get("entries")
    if not isinstance(entries, list) or not entries:
        raise ValueError("calculator set entries must be a non-empty list")
    known_ids = {c.case_id for c in battery_cases}
    seen: list[str] = []
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) - CALCULATOR_ENTRY_KEYS:
            raise ValueError(f"bad calculator entry keys: {entry!r}")
        case_id = entry.get("case_id")
        if case_id not in known_ids:
            raise ValueError(f"calculator entry references unknown case {case_id!r}")
        oracles = entry.get("oracles")
        if not isinstance(oracles, list) or len(oracles) < 2:
            raise ValueError(
                f"case {case_id!r} needs >= 2 calculator oracles (adjudication "
                "is the point of the lane)"
            )
        for o in oracles:
            if Oracle(o) not in CALCULATOR_ORACLES:
                raise ValueError(f"case {case_id!r}: {o!r} is not a calculator oracle")
        if len(set(oracles)) != len(oracles):
            raise ValueError(f"case {case_id!r} lists a duplicate oracle")
        if not isinstance(entry.get("notes"), str) or not entry["notes"].strip():
            raise ValueError(f"case {case_id!r} needs non-empty notes")
        seen.append(case_id)
    dupes = sorted({i for i in seen if seen.count(i) > 1})
    if dupes:
        raise ValueError(f"duplicate calculator entries: {dupes}")
    return entries
