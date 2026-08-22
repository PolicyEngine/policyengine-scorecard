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
   two null-side scope buckets, or ``unclassified``; every other outcome
   exists only as an ADJUDICATION of an ``unclassified`` row, with a
   traceable writeup — misses stay visible until someone explains them.
4. **The seam is enforced, not conventional.** ``CaseResult`` RECOMPUTES
   ``classify()`` and compares: a stored classification either equals what
   the classifier says, or it is an adjudication of a row the classifier
   left ``unclassified`` and carries a writeup. Nothing can persist
   ``100`` vs ``100`` as ``pe_gap``, a boolean ``1`` vs ``0`` as a
   tolerance match, or a numeric mismatch as ``policy_scope_mismatch``
   without an explanation — the failure modes the round-2 probes found.
   Tolerances come from :data:`DEFAULT_TOLERANCES` alone; a caller cannot
   hand in a wider one.
5. **Identities are closed at the edges too.** Regions, focus variables,
   battery schema paths and baseline worlds route through registries; NaN
   and infinity are not numbers a case may carry, and a boolean-class
   comparison may only hold 0 or 1.

Not yet here: the case/result TABLE, writer, exporter and build_db step.
Mode-3 rows therefore do not persist to the DB in this PR, and the
epistemic wiring that rides on those columns (calibration_relationship,
run/bundle pins, connector revision, citable adjudication links) lands
with them. That design has repo-wide surface and is being paired on
rather than decided unilaterally here; SCHEMA.md records the open shape.
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


# Classifications the automatic classifier may emit.
CLASSIFIER_EMITTED = frozenset(
    {
        DiffClassification.MATCH_EXACT,
        DiffClassification.MATCH_WITHIN_TOLERANCE,
        DiffClassification.PE_GAP,
        DiffClassification.POLICY_SCOPE_MISMATCH,
        DiffClassification.UNCLASSIFIED,
    }
)

# Outcomes a human may adjudicate an ``unclassified`` row INTO, each
# requiring a traceable writeup in ``annotations``. Note that pe_gap and
# policy_scope_mismatch appear both here and in CLASSIFIER_EMITTED: the
# classifier emits them for a NULL side, where they are mechanical, and a
# human may also assign them to a numeric-vs-numeric difference, where
# they are a judgement and need explaining. The round-2 finding was that
# only oracle_difference and rounding demanded a writeup, so a
# numeric-vs-numeric row could be labelled pe_gap silently.
ADJUDICATABLE = frozenset(
    {
        DiffClassification.ORACLE_DIFFERENCE,
        DiffClassification.ROUNDING,
        DiffClassification.PE_GAP,
        DiffClassification.POLICY_SCOPE_MISMATCH,
    }
)

# Back-compatible alias for the adjudicated-only pair.
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
    {"people", "benefit_units", "region", "tenure", "rent", "council_tax", "brma"}
)

# Regions are a CLOSED registry per country, not free text: region routes
# devolved policy and location-dependent amounts, so `region="MARS"` must
# not reach a connector that will silently fall back to a default rate.
VALID_REGIONS = {
    # UK ITL-1
    "UK": frozenset(
        {
            "NORTH_EAST",
            "NORTH_WEST",
            "YORKSHIRE",
            "EAST_MIDLANDS",
            "WEST_MIDLANDS",
            "EAST_OF_ENGLAND",
            "LONDON",
            "SOUTH_EAST",
            "SOUTH_WEST",
            "WALES",
            "SCOTLAND",
            "NORTHERN_IRELAND",
        }
    ),
    # US state codes (+ DC), for the taxsim-cases lane
    "US": frozenset(
        "AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA "
        "MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX "
        "UT VT VA WA WV WI WY".split()
    ),
}

# Broad Rental Market Areas the private-rent cases may pin. A UK
# private-rent case MUST name one: LHA rates are set per BRMA, not per
# ITL-1 region, so "Yorkshire" does not fix a world — the round-2 finding
# that the rent clears the cap only in "most" Yorkshire BRMAs means the
# two engines were not guaranteed the same LHA rate. Extending the list
# is deliberate, and each entry names the region it sits in so a case
# cannot pin a BRMA outside its own region.
BRMA_REGION = {
    "Leeds": "YORKSHIRE",
    "Sheffield": "YORKSHIRE",
    "Inner London": "LONDON",
    "Outer London": "LONDON",
    "Manchester": "NORTH_WEST",
    "Nottingham": "EAST_MIDLANDS",
    "Birmingham": "WEST_MIDLANDS",
    "Southampton": "SOUTH_EAST",
}

# expected_focus is claim-shaped: it names the output variables a case is
# curated to exercise, and a connector maps each to both engines. An
# invented name would silently produce no comparison at all, so the
# vocabulary is closed per country.
FOCUS_VARIABLES = {
    "UK": frozenset(
        {
            "universal_credit",
            "child_benefit",
            "pension_credit",
            "carers_allowance",
            "benefit_cap",
            "income_tax",
            "national_insurance",
            "scottish_child_payment",
            "council_tax_reduction",
            "housing_benefit",
        }
    ),
    "US": frozenset(
        {
            "federal_income_tax",
            "state_income_tax",
            "payroll_tax",
            "eitc",
            "ctc",
            "snap",
        }
    ),
}

# Battery `schema` values: the contract document a battery declares
# itself against. An arbitrary path let a battery claim a schema nobody
# wrote.
VALID_BATTERY_SCHEMAS = frozenset({"sources/ukmod-cases/SCHEMA.md"})


def _finite(value) -> bool:
    """NaN and infinity are not amounts a case or a comparison may carry:
    NaN silently defeats every comparison operator below, and an infinite
    rent produces an infinite entitlement rather than an error."""
    return value == value and value not in (float("inf"), float("-inf"))


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
        if isinstance(v, bool) or not isinstance(v, (int, float)) or not _finite(v):
            raise ValueError(f"person {person_id!r} {key} must be a finite number >= 0")
        if v < 0:
            raise ValueError(f"person {person_id!r} {key} must be a number >= 0")
    for key in PERSON_BOOL_KEYS & set(person):
        if not isinstance(person[key], bool):
            raise ValueError(f"person {person_id!r} {key} must be a boolean")


def _validate_household(household: dict, country: str) -> None:
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
            isinstance(v, bool)
            or not isinstance(v, (int, float))
            or not _finite(v)
            or v < 0
        ):
            raise ValueError(f"household.{key} must be a finite number >= 0")
    if household.get("rent", 0) and tenure in ("owned_outright", "owned_mortgage"):
        raise ValueError("owner-occupier households carry no rent")
    region = household.get("region")
    if region is not None and region not in VALID_REGIONS[country]:
        raise ValueError(
            f"unregistered {country} region {region!r} — region routes "
            "devolved policy and location-dependent amounts, so it is a "
            "closed registry (VALID_REGIONS), never free text"
        )
    brma = household.get("brma")
    if country == "UK" and tenure == "rented_private":
        if brma is None:
            raise ValueError(
                "a UK private-rent case must pin a BRMA: LHA rates are set "
                "per Broad Rental Market Area, not per ITL-1 region, so a "
                "region alone does not fix the world both engines run"
            )
        if brma not in BRMA_REGION:
            raise ValueError(f"unregistered BRMA: {brma!r}")
        if region is not None and BRMA_REGION[brma] != region:
            raise ValueError(f"BRMA {brma!r} sits in {BRMA_REGION[brma]}, not {region}")
    elif brma is not None:
        raise ValueError("brma is recorded only on UK private-rent cases")


def _validate_baseline(descriptor) -> None:
    """A case may only name a baseline world the registry describes.

    Registration is what makes a counterfactual auditable: an unnamed
    world is exactly the "which law did this run?" ambiguity mode 3
    exists to remove. Imported lazily — baselines.py reaches the DB
    layer, and this module must stay importable on its own.
    """
    if descriptor is None:
        return
    if not isinstance(descriptor, dict) or not descriptor.get("policy"):
        raise ValueError(
            f"case baseline must be a descriptor with a policy key: {descriptor!r}"
        )
    from .baselines import BASELINES
    from .models import baseline_key

    known = {baseline_key(d) for d, *_ in BASELINES}
    if baseline_key(descriptor) not in known:
        raise ValueError(
            f"unregistered baseline world {descriptor!r} — register it in "
            "scorecard_db/baselines.py before a case may be evaluated in it"
        )


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
    # The policy world the case is evaluated in. None = current law.
    # A descriptor of the same shape ReformRef.baseline carries, and it
    # must already be REGISTERED in baselines.py — this is how a case
    # pins a same-year counterfactual (e.g. {"policy": "pre_ab2025"},
    # the two-child limit reinstated) instead of leaning on a
    # year-on-year delta that moves ages, rates and policy year at once.
    baseline: Optional[dict] = None

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
        unknown_focus = sorted(set(self.expected_focus) - FOCUS_VARIABLES[self.country])
        if unknown_focus:
            raise ValueError(
                f"unregistered {self.country} focus variables: {unknown_focus} — "
                "a name no connector maps produces no comparison at all"
            )
        if len(set(self.expected_focus)) != len(self.expected_focus):
            raise ValueError("expected_focus must not repeat a variable")
        _validate_baseline(self.baseline)
        _validate_household(self.household, self.country)


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
    # REQUIRED, not optional: the validator re-runs classify() against it,
    # so a row without a variable class cannot be checked at all. (It was
    # Optional, and the shipped valid-row test omitted it.)
    variable_class: VariableClass
    abs_diff: Optional[float] = None
    tolerance: Optional[float] = None
    annotations: list = field(default_factory=list)
    # REQUIRED: an omitted version used to default to the current one,
    # which is precisely the silent reinterpretation the field exists to
    # prevent. `None` raises rather than assuming 1.
    schema_version: Optional[int] = None

    def __post_init__(self):
        self.oracle = Oracle(self.oracle)
        self.classification = DiffClassification(self.classification)
        self.variable_class = VariableClass(self.variable_class)
        if self.schema_version is None:
            raise ValueError(
                "schema_version is required — an omitted version silently "
                f"reinterprets a stored row; write {SCHEMA_VERSION} "
                "explicitly"
            )
        if self.schema_version != SCHEMA_VERSION:
            raise ValueError(
                f"schema_version {self.schema_version!r} is not the current "
                f"contract version {SCHEMA_VERSION}; migrate explicitly"
            )
        if not self.case_id or not self.variable:
            raise ValueError("case_id and variable are required")
        if not str(self.engine_version).strip() or not str(self.oracle_version).strip():
            raise ValueError(
                "engine_version and oracle_version are required — a blank "
                "version makes a stored comparison unreproducible"
            )
        for name in ("pe_value", "oracle_value"):
            v = getattr(self, name)
            if v is None:
                continue
            if isinstance(v, bool) or not isinstance(v, (int, float)) or not _finite(v):
                raise ValueError(f"{name} must be a finite number or None, got {v!r}")
            if self.variable_class is VariableClass.BOOLEAN and v not in (0, 1):
                raise ValueError(
                    f"boolean-class {name} must be 0 or 1, got {v!r} — a "
                    "boolean comparison carrying 7 is not a boolean"
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
        # THE SEAM. Recompute rather than trust the caller: the factory
        # was a convention, and round-2 probes persisted 100-vs-100 as
        # pe_gap, a numeric mismatch as policy_scope_mismatch, and a
        # boolean 1-vs-0 as a tolerance match with a caller-supplied
        # tolerance of 100. A stored classification is valid only if it
        # is what the classifier says, or an explained adjudication of a
        # row the classifier left unclassified.
        computed = classify(self.pe_value, self.oracle_value, self.variable_class)
        if self.classification != computed:
            if computed != DiffClassification.UNCLASSIFIED:
                raise ValueError(
                    f"classification {self.classification.value!r} contradicts "
                    f"the classifier, which says {computed.value!r} for "
                    f"pe={self.pe_value!r} oracle={self.oracle_value!r} "
                    f"({self.variable_class.value}). Only an `unclassified` "
                    "row may be adjudicated."
                )
            if self.classification not in ADJUDICATABLE:
                raise ValueError(
                    f"{self.classification.value!r} is not an outcome an "
                    f"unclassified row may be adjudicated into "
                    f"({sorted(c.value for c in ADJUDICATABLE)})"
                )
            if not self.annotations:
                raise ValueError(
                    f"{self.classification.value} is an adjudicated outcome "
                    "and requires a writeup in annotations (SCHEMA.md)"
                )
        # Tolerance comes from the registry, never from the caller: a
        # hand-passed tolerance is how a boolean mismatch became a match.
        if self.classification == DiffClassification.MATCH_WITHIN_TOLERANCE:
            registered = float(DEFAULT_TOLERANCES[self.variable_class])
            if abs(float(self.tolerance) - registered) > 1e-12:
                raise ValueError(
                    f"tolerance {self.tolerance!r} is not the registered "
                    f"tolerance for {self.variable_class.value} "
                    f"({registered}) — tolerances are a registry decision, "
                    "never a per-row argument"
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
        annotations: Optional[list] = None,
        classification: Optional[DiffClassification] = None,
    ) -> "CaseResult":
        """The one wiring path from ``classify`` to a stored row.

        Derives abs_diff, threads the registered tolerance (only onto
        match_within_tolerance rows, per the field contract), and
        persists the variable class.

        ``annotations`` is accepted here because some lanes REQUIRE one —
        the calculator oracles (#64) must carry an archive annotation, so
        a factory that could not take annotations made every calculator
        call raise. ``classification`` is accepted only to record an
        adjudication of a row the classifier leaves unclassified; the
        constructor re-checks it either way.
        """
        variable_class = VariableClass(variable_class)
        computed = classify(pe_value, oracle_value, variable_class)
        both = pe_value is not None and oracle_value is not None
        abs_diff = abs(float(pe_value) - float(oracle_value)) if both else None
        tolerance = (
            float(DEFAULT_TOLERANCES[variable_class])
            if computed == DiffClassification.MATCH_WITHIN_TOLERANCE
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
            classification=computed if classification is None else classification,
            abs_diff=abs_diff,
            tolerance=tolerance,
            variable_class=variable_class,
            annotations=list(annotations or []),
            schema_version=SCHEMA_VERSION,
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
        "baseline",
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
    if raw.get("schema") not in VALID_BATTERY_SCHEMAS:
        raise ValueError(
            f"battery schema {raw.get('schema')!r} is not a contract this "
            f"repo defines ({sorted(VALID_BATTERY_SCHEMAS)})"
        )
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
