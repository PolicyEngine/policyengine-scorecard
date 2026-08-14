"""Registry-consistency tests for the UK compute pipeline (#40).

The pipeline itself needs the policyengine.py-managed environment and
the certified populace-uk bundle; these tests pin what is checkable
anywhere — the declarative registries are internally consistent, the
candidate lists hold no cross-concept fallbacks, argv parsing takes the
year from index 1, the population denominator never emits an unweighted
count as "ok", and the module imports without the engine installed.
"""

import ast
import inspect

import pytest

from pipeline import compute_uk_counterparts as uk
from pipeline.compute_uk_counterparts import (
    BENEFIT_LINES,
    CANDIDATES,
    FULLPART_OVERRIDES,
    emit,
    emit_population_denominator,
    meta,
    parse_year,
    pe_gap,
    rows,
    weighted_population,
)


def _module_level_imports():
    """Top-level import names only — nested ones (policyengine) don't count."""
    names = []
    for node in ast.parse(inspect.getsource(uk)).body:
        if isinstance(node, ast.Import):
            names += [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.append(node.module)
    return names


def test_module_imports_without_engine():
    # the policyengine import lives inside build_sim(), so the registry
    # is inspectable (and testable) on unmanaged machines
    assert CANDIDATES and BENEFIT_LINES and FULLPART_OVERRIDES
    assert "policyengine" not in {m.split(".")[0] for m in _module_level_imports()}


def test_benefit_lines_reference_known_concepts():
    for program, concept, entity, geo in BENEFIT_LINES:
        assert concept in CANDIDATES, f"{program}: unknown concept {concept}"
        assert entity in ("person", "benunit", "household")
        assert geo in ("UK", "GB", "NI")


def test_candidate_lists_are_nonempty_and_unique():
    for concept, names in CANDIDATES.items():
        assert names, f"{concept}: empty candidate list"
        assert len(names) == len(set(names)), f"{concept}: duplicate candidates"


# --- no cross-concept fallbacks -------------------------------------------


def test_housing_cost_concepts_never_fall_back_across_measures():
    """BHC and AHC are different HBAI measures, and a housing-cost-agnostic
    in_poverty is neither. A fallback across them emits a wrong-concept
    value under status "ok"."""
    for suffix in ("bhc", "ahc"):
        concept = f"in_relative_poverty_{suffix}"
        other = "ahc" if suffix == "bhc" else "bhc"
        for name in CANDIDATES[concept]:
            assert name.lower().endswith(suffix), (
                f"{concept}: candidate {name} is not a {suffix.upper()} measure"
            )
            assert other not in name.lower(), f"{concept}: {name} crosses to {other}"


def test_no_generic_poverty_fallback_anywhere():
    for concept, names in CANDIDATES.items():
        assert "in_poverty" not in names, (
            f"{concept}: generic in_poverty is not a synonym of any specific "
            "poverty concept"
        )


def test_boolean_concepts_list_no_amount_variables():
    """A GBP amount is not a synonym for a boolean status flag: e.g.
    higher_rate_earned_income_tax is pounds charged at the higher rate,
    not "is a higher-rate taxpayer"."""
    boolean_prefixes = ("is_", "in_", "pays_", "would_", "takes_up_")
    for concept in ("pays_higher_rate", "is_child", "is_SP_age"):
        for name in CANDIDATES[concept]:
            assert name.lower().startswith(boolean_prefixes), (
                f"{concept}: candidate {name} does not read as a boolean flag; "
                "an amount variable is a different concept"
            )


# --- argv parsing ----------------------------------------------------------


def test_parse_year_takes_argv_index_1():
    assert parse_year(["compute_uk_counterparts.py", "2026"]) == 2026
    assert parse_year(["compute_uk_counterparts.py"]) == 2025
    assert parse_year(["compute_uk_counterparts.py"], default=2030) == 2030


def test_parse_year_ignores_no_argument_silently_only_when_absent():
    with pytest.raises(ValueError):
        parse_year(["compute_uk_counterparts.py", "not-a-year"])


def test_main_reads_the_year_from_index_1_not_2():
    src = inspect.getsource(uk)
    assert "sys.argv[2]" not in src, "year must come from argv[1]; there is no argv[2]"
    assert "parse_year(sys.argv)" in inspect.getsource(uk.main)


# --- poverty denominator ---------------------------------------------------


class _FakeMicroSeries:
    """Stand-in for a weighted microdf MicroSeries."""

    def __init__(self, weights, weighted_count):
        self.weights = weights
        self._weighted_count = weighted_count

    def count(self):
        return self._weighted_count


def test_weighted_population_returns_weighted_count():
    assert weighted_population(_FakeMicroSeries([1, 2], 67_000_000.0)) == 67_000_000.0


@pytest.mark.parametrize(
    "unweighted",
    [
        [0, 1, 1],  # plain list
        _FakeMicroSeries(None, 100_000),  # MicroSeries-shaped but unweighted
    ],
)
def test_weighted_population_refuses_unweighted_objects(unweighted):
    assert weighted_population(unweighted) is None


class _UnweightedPandasLike:
    """Like a pandas Series: answers count() with an unweighted record count
    and has no weights. The old code emitted this ~10^5 number as a
    poverty-rate denominator with status "ok"."""

    def count(self):
        return 100_000


def test_population_denominator_never_emits_unweighted_count_as_ok():
    before = len(rows)
    gaps_before = len(meta["unresolved"])
    out = emit_population_denominator("baseline", "ahc", _UnweightedPandasLike())
    assert out is None
    row = rows[before]
    assert row["status"] == "pe_gap" and row["value"] is None
    assert row["metric"] == "population_ahc"
    assert not any(r["value"] == 100_000.0 for r in rows[before:])
    del rows[before:]
    del meta["unresolved"][gaps_before:]


def test_population_denominator_emits_weighted_count_as_ok():
    before = len(rows)
    out = emit_population_denominator(
        "baseline", "bhc", _FakeMicroSeries([1.0], 67_000_000.0)
    )
    assert out == 67_000_000.0
    assert rows[before]["status"] == "ok"
    assert rows[before]["value"] == 67_000_000.0
    del rows[before:]


# --- fullpart verification -------------------------------------------------


def _row(run, program, metric, value, status="ok"):
    return {
        "run": run,
        "country": "UK",
        "program": program,
        "metric": metric,
        "subgroup": "total",
        "geography": "GB",
        "value": value,
        "status": status,
    }


def test_identical_fullpart_is_a_hard_failure():
    base = [_row("baseline", "pension_credit", "recipient_count", 1_320_000.0)]
    same = [_row("fullpart", "pension_credit", "recipient_count", 1_320_000.0)]
    with pytest.raises(RuntimeError, match="byte-identical"):
        uk.assert_fullpart_moved(base, same)


def test_nothing_comparable_is_a_hard_failure():
    base = [_row("baseline", "pension_credit", "recipient_count", None, "pe_gap")]
    full = [_row("fullpart", "pension_credit", "recipient_count", None, "pe_gap")]
    with pytest.raises(RuntimeError, match="nothing verifies"):
        uk.assert_fullpart_moved(base, full)


def test_moved_fullpart_passes_and_is_logged_in_meta():
    base = [_row("baseline", "pension_credit", "recipient_count", 1_320_000.0)]
    full = [_row("fullpart", "pension_credit", "recipient_count", 2_100_000.0)]
    uk.assert_fullpart_moved(base, full)
    assert meta["fullpart_moved"] == {"compared": 1, "moved": 1}


# --- period handling -------------------------------------------------------


class _Var:
    def __init__(self, definition_period):
        self.definition_period = definition_period


@pytest.mark.parametrize(
    "period,expected_len,label",
    [("month", 12, "12 months"), ("year", 1, "year"), ("eternity", 1, "eternity")],
)
def test_periods_follow_the_variables_definition_period(period, expected_len, label):
    periods, got_label = uk.periods_for(_Var(period), 2026)
    assert len(periods) == expected_len and got_label == label
    if period == "month":
        assert periods[0] == "2026-01" and periods[-1] == "2026-12"


def test_emit_and_pe_gap_row_shape():
    before = len(rows)
    emit("baseline", "pension_credit", "recipient_count", "total", "GB", 1_320_000)
    pe_gap("baseline", "x", "m", "total", "UK", "some_concept")
    ok_row, gap_row = rows[before], rows[before + 1]
    assert ok_row["country"] == "UK" and ok_row["status"] == "ok"
    assert ok_row["value"] == 1_320_000.0
    assert gap_row["status"] == "pe_gap" and gap_row["value"] is None
    assert meta["unresolved"][-1]["concept"] == "some_concept"
    del rows[before:]
    meta["unresolved"].pop()
