"""Construction premises: what each frozen world holds on an engine.

A stub engine view stands in for policyengine-uk, so the checks run without
the engine. Installed-engine tests regenerate that engine's committed
premises and compare processed annual CGT rates with raw 30 April values.
"""

import importlib.util
import json
import random
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from pipeline import audit_uk_event_premises as premises
from pipeline import compute_uk_ab2025 as worlds

ROOT = Path(__file__).resolve().parent.parent


class StubEngine:
    def __init__(self, law, *, blend=(), reads_blend=True, authored=None):
        self.law = law  # path -> value (constant) or {year: value}
        self.blend = set(blend)
        self.reads_blend = reads_blend
        self.reads_calendar = reads_blend
        self.authored = authored

    def current_law(self, path, date):
        value = self.law.get(path)
        value = value.get(int(date[:4])) if isinstance(value, dict) else value
        return premises.scalar(value)

    def raw_30_april(self, path, year):
        return self.current_law(path, f"{year}-04-30")

    def annualisation(self, path):
        return {
            "fiscal_year_blend": (path in self.blend) if self.reads_blend else None,
            "preserve_calendar_dates": False if self.reads_calendar else None,
        }

    def resolve(self, path, date):
        return self.current_law(path, date)


def measure(construction, *, modifier=None, delta=None, commences="2024-25"):
    m = {
        "measure_key": "event__m",
        "title": "Untitled measure",
        "computability": "partial",
        "construction": construction,
        "commences_fy": commences,
        "heads": [],
    }
    if modifier is not None:
        m["pe_baseline_modifier"] = modifier
    if delta is not None:
        m["pe_reform_delta"] = delta
    return m


def run(m, engine, years=(2023, 2024, 2025)):
    world = worlds.worlds_for(m, {m["measure_key"]: m}, years=list(years))
    return premises.audit_measure("event", m, world, list(years), engine)


def test_forward_delta_equal_to_current_law_is_inert():
    m = measure(
        "forward_delta_on_certified_world", delta={"gov.vat": {"2024-01-01": 0.2}}
    )
    moving = run(m, StubEngine({"gov.vat": 0}))
    assert moving["checks"]["forward_delta_changes_current_law"]["holds"] is True
    assert moving["years"]["2024"]["paths"]["gov.vat"] == {
        "current_law": 0,
        "baseline_world": 0,
        "reform_world": 0.2,
        "raw_30_april": 0,
        "fiscal_year_blend": False,
        "preserve_calendar_dates": False,
    }
    inert = run(m, StubEngine({"gov.vat": 0.2}))
    assert inert["checks"]["forward_delta_changes_current_law"]["holds"] is False
    assert inert["checks"]["reversal_differs_from_current_law"]["holds"] is None


def test_reversal_identical_to_current_law_is_inert():
    m = measure(
        "reversal_on_certified_world", modifier={"gov.rate": {"2024-01-01": 0.1}}
    )
    assert (
        run(m, StubEngine({"gov.rate": 0.18}))["checks"][
            "reversal_differs_from_current_law"
        ]["holds"]
        is True
    )
    assert (
        run(m, StubEngine({"gov.rate": 0.1}))["checks"][
            "reversal_differs_from_current_law"
        ]["holds"]
        is False
    )


def test_only_in_force_years_count_for_inertness():
    # Current law equals the reversal only before commencement: not inert.
    m = measure(
        "reversal_on_certified_world",
        modifier={"gov.rate": {"2023-01-01": 0.1}},
        commences="2025-26",
    )
    law = {"gov.rate": {2023: 0.1, 2024: 0.1, 2025: 0.18}}
    result = run(m, StubEngine(law))
    assert [result["years"][y]["in_force"] for y in ("2023", "2024", "2025")] == [
        False,
        False,
        True,
    ]
    assert result["checks"]["reversal_differs_from_current_law"]["holds"] is True
    law = {"gov.rate": {2023: 0.18, 2024: 0.18, 2025: 0.1}}
    assert (
        run(m, StubEngine(law))["checks"]["reversal_differs_from_current_law"]["holds"]
        is False
    )


def test_blended_annualisation_is_reported_only_where_the_engine_blends():
    m = measure(
        "reversal_on_certified_world", modifier={"gov.cgt": {"2024-10-30": 0.1}}
    )
    blended = run(m, StubEngine({"gov.cgt": 0.1346}, blend={"gov.cgt"}))
    check = blended["checks"]["annual_value_matches_30_april_sample"]
    assert check["holds"] is False and "gov.cgt" in check["detail"]
    sampled = run(m, StubEngine({"gov.cgt": 0.1}, reads_blend=False))
    assert sampled["checks"]["annual_value_matches_30_april_sample"]["holds"] is True
    assert sampled["years"]["2025"]["paths"]["gov.cgt"]["fiscal_year_blend"] is None


def test_historical_annualisation_check_names_metadata_not_value_equality():
    m = measure(
        "reversal_on_certified_world", modifier={"gov.cgt": {"2024-01-01": 0.1}}
    )
    result = run(m, StubEngine({"gov.cgt": 0.1}, blend={"gov.cgt"}))
    path = result["years"]["2024"]["paths"]["gov.cgt"]
    assert path["current_law"] == path["raw_30_april"]
    assert result["checks"]["annual_value_matches_30_april_sample"]["holds"] is False


@pytest.mark.parametrize(
    "body,expected",
    [
        ('"""fiscal_year_blend and preserve_calendar_dates"""', frozenset()),
        ('name = "fiscal_year_blend"', frozenset()),
        ('other.get("fiscal_year_blend")', frozenset()),
        (
            '(param.metadata or {}).get("fiscal_year_blend", False)',
            frozenset({"fiscal_year_blend"}),
        ),
        (
            'param.metadata["preserve_calendar_dates"]',
            frozenset({"preserve_calendar_dates"}),
        ),
    ],
)
def test_converter_support_requires_executable_metadata_reads(body, expected):
    source = f"def converter(param):\n    {body}\n"
    assert premises.converter_metadata_keys(source) == expected


def test_october_dates_execute_from_the_next_january():
    m = measure(
        "reversal_on_certified_world", modifier={"gov.cgt": {"2024-10-30": 0.1}}
    )
    result = run(m, StubEngine({"gov.cgt": 0.18}))
    assert result["years"]["2024"]["paths"]["gov.cgt"]["baseline_world"] == 0.18
    assert result["years"]["2025"]["paths"]["gov.cgt"]["baseline_world"] == 0.1


def test_authored_drift_is_caught(monkeypatch):
    m = measure(
        "reversal_on_certified_world",
        modifier={"gov.cap": {"2024": 646.35, "2025": round(646.35 * 1030 / 951, 2)}},
    )

    def authored(event, title, resolve):
        return {
            "pe_baseline_modifier": {
                "gov.cap": {
                    str(y): round(646.35 * resolve("gov.cap", f"{y}-04-06") / 951, 2)
                    for y in (2024, 2025)
                }
            }
        }

    monkeypatch.setattr(premises.builder, "authored_construction", authored)
    same = run(m, StubEngine({"gov.cap": {2024: 951, 2025: 1030.0}}))
    assert same["checks"]["authored_construction_reproduces"]["holds"] is True
    drifted = run(m, StubEngine({"gov.cap": {2024: 951, 2025: 1071.09}}))
    check = drifted["checks"]["authored_construction_reproduces"]
    assert check["holds"] is False
    assert check["differences"]["pe_baseline_modifier"]["authored_here"]["gov.cap"][
        "2025"
    ] == round(646.35 * 1071.09 / 951, 2)
    monkeypatch.setattr(premises.builder, "authored_construction", lambda *a: None)
    assert (
        run(m, StubEngine({"gov.cap": 951}))["checks"][
            "authored_construction_reproduces"
        ]["holds"]
        is None
    )

    def broken(event, title, resolve):
        raise TypeError("unsupported operand")

    monkeypatch.setattr(premises.builder, "authored_construction", broken)
    assert (
        run(m, StubEngine({"gov.cap": None}))["checks"][
            "authored_construction_reproduces"
        ]["holds"]
        is None
    )


@settings(max_examples=100, deadline=None)
@given(
    st.floats(allow_nan=True, allow_infinity=True),
    st.integers(min_value=0, max_value=2**31),
)
def test_scalars_serialise_without_nan_or_infinity(value, seed):
    out = premises.scalar(value)
    json.dumps(out, allow_nan=False)
    m = measure(
        "forward_delta_on_certified_world", delta={"gov.x": {"2024-01-01": 1.0}}
    )
    payload = premises.canonical_bytes(
        {"m": run(m, StubEngine({"gov.x": value})), "seed": seed}
    )
    assert b"NaN" not in payload and b"Infinity" not in payload


@settings(max_examples=50, deadline=None)
@given(st.integers(min_value=0, max_value=2**31))
def test_output_is_independent_of_dictionary_order(seed):
    rng = random.Random(seed)
    paths = [f"gov.p{i}" for i in range(5)]
    modifier = {p: {"2024-01-01": float(i)} for i, p in enumerate(paths)}
    shuffled = list(modifier.items())
    rng.shuffle(shuffled)
    law = {p: 10.0 for p in paths}
    a = run(measure("reversal_on_certified_world", modifier=modifier), StubEngine(law))
    b = run(
        measure("reversal_on_certified_world", modifier=dict(shuffled)),
        StubEngine(law),
    )
    assert premises.canonical_bytes(a) == premises.canonical_bytes(b)


def committed_engine():
    if importlib.util.find_spec("policyengine_uk") is None:
        return None
    from importlib.metadata import version

    return version("policyengine-uk")


@pytest.fixture(scope="module")
def installed_engine_view():
    if committed_engine() is None:
        pytest.skip(
            "policyengine-uk is not installed; committed premises and CGT values "
            "are checked in .venv-candidate and .venv-replay"
        )
    # These parameter-only checks do not mutate the tree; share the expensive
    # engine load between the committed audit and the direct value comparison.
    return premises.EngineView()


@pytest.mark.parametrize(
    "engine,path",
    [
        (
            "2.125.1",
            "results/uk/replays/pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0/CONSTRUCTION_PREMISES.json",
        ),
        ("2.89.2", "results/uk/events/CONSTRUCTION_PREMISES.json"),
    ],
)
def test_committed_premises_regenerate(engine, path, installed_engine_view):
    installed = committed_engine()
    if installed is None:
        pytest.skip(
            "policyengine-uk is not installed; committed premises regenerate in "
            ".venv-candidate and .venv-replay"
        )
    if installed != engine:
        pytest.skip(
            f"installed policyengine-uk {installed}; this committed file belongs "
            f"to {engine} (checked in its pinned environment)"
        )
    payload = premises.canonical_bytes(
        premises.audit(list(premises.EVENTS), installed_engine_view)
    )
    assert payload == (ROOT / path).read_bytes()


def test_installed_cgt_annual_values_against_raw_30_april(installed_engine_view):
    installed = committed_engine()
    if installed not in ("2.89.2", "2.125.1"):
        pytest.skip(
            "CGT value comparison needs policyengine-uk 2.89.2 or 2.125.1; "
            "run in .venv-replay or .venv-candidate"
        )
    engine = installed_engine_view
    for name, old, new in (
        ("basic_rate", 0.10, 0.18),
        ("higher_rate", 0.20, 0.24),
        ("additional_rate", 0.20, 0.24),
    ):
        path = f"gov.hmrc.cgt.{name}"
        raw = engine.raw_30_april(path, 2024)
        annual = engine.current_law(path, "2024-01-01")
        assert raw == old
        expected = old * 207 / 365 + new * 158 / 365 if installed == "2.125.1" else old
        assert annual == pytest.approx(expected, abs=1e-10)
        assert engine.reads_blend is (installed == "2.125.1")
