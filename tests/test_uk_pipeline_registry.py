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
    HMRC_BAND_CUTS,
    PENSION_AGE_HB_LINE,
    TAKEUP_COMPONENT_PROGRAMS,
    TAKEUP_VALIDATED_PROGRAMS,
    emit,
    emit_population_denominator,
    meta,
    parse_year,
    pe_gap,
    restricted_mask,
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
    for program, concept, entity, geo in BENEFIT_LINES + [PENSION_AGE_HB_LINE]:
        assert concept in CANDIDATES, f"{program}: unknown concept {concept}"
        assert entity in ("person", "benunit", "household")
        assert geo in ("UK", "GB", "NI")


def test_entity_levels_match_the_engine():
    """ESA/JSA are benefit-unit variables and winter fuel is
    household-level; mapping them lower projects awards onto every
    member and overcounts recipients."""
    levels = {program: entity for program, _, entity, _ in BENEFIT_LINES}
    assert levels["esa_income"] == "benunit"
    assert levels["jsa"] == "benunit"
    assert levels["winter_fuel_allowance"] == "household"


def test_fullpart_overrides_use_the_engine_takeup_vocabulary():
    """The engine's take-up inputs are would_claim_* plus the global
    claims_all_entitled_benefits switch (the set the compute campaign's
    fulltakeup runs used successfully) — not guessed takes_up_* names,
    which would make the first managed run die on its own abort."""
    assert set(FULLPART_OVERRIDES) == {
        "would_claim_pc",
        "would_claim_housing_benefit",
        "would_claim_uc",
        "would_claim_child_benefit",
        "claims_all_entitled_benefits",
    }
    assert all(v is True for v in FULLPART_OVERRIDES.values())


def test_hmrc_band_cuts_match_external_subgroup_vocabulary():
    """sources/hmrc-personal-tax/adapter.py emits taxpayer_count under
    basic_rate/higher_rate/additional_rate; the PE side must cut on the
    same ids, each through a declared boolean band concept."""
    assert [s for s, _ in HMRC_BAND_CUTS] == [
        "basic_rate",
        "higher_rate",
        "additional_rate",
    ]
    for _, concept in HMRC_BAND_CUTS:
        assert concept in CANDIDATES


def test_takeup_validated_programs_are_emitted_programs():
    emitted = {program for program, _, _, _ in BENEFIT_LINES} | {PENSION_AGE_HB_LINE[0]}
    for program in TAKEUP_VALIDATED_PROGRAMS + TAKEUP_COMPONENT_PROGRAMS:
        assert program in emitted, f"{program}: validated but never emitted"


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
    for concept in (
        "pays_basic_rate",
        "pays_higher_rate",
        "pays_additional_rate",
        "is_child",
        "is_SP_age",
    ):
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


def test_build_sim_has_no_half_wired_year_param():
    """build_sim reads the module-global YEAR like every sim.calculate;
    a year parameter that callers never pass is a silent divergence
    trap, so it must not exist."""
    assert list(inspect.signature(uk.build_sim).parameters) == ["fullpart"]


def test_fullpart_override_is_an_ndarray_not_a_list():
    """set_input on some core versions expects an ndarray; a Python
    list may coerce oddly or fail silently (US parity: np.ones)."""
    src = inspect.getsource(uk.build_sim)
    assert "[value] * n" not in src
    assert "np.full(n, value, dtype=bool)" in src


# --- poverty denominator ---------------------------------------------------


def _fake_microseries(weighted_count):
    """Type-identity stand-in for microdf.generic.MicroSeries.

    The module identifies a MicroSeries by TYPE (name + defining
    module), never by reading its weight array — microdf itself is not
    installed in CI, so the fallback identity path is what these tests
    exercise."""
    cls = type("MicroSeries", (), {"count": lambda self: weighted_count})
    cls.__module__ = "microdf.generic"
    return cls()


def test_weighted_population_returns_weighted_count():
    assert weighted_population(_fake_microseries(67_000_000.0)) == 67_000_000.0


def _impostor_microseries():
    """Right class name, wrong module: not a microdf type."""
    cls = type("MicroSeries", (), {"count": lambda self: 100_000})
    cls.__module__ = "pandas.core.series"
    return cls()


@pytest.mark.parametrize(
    "unweighted",
    [
        [0, 1, 1],  # plain list
        _impostor_microseries(),  # MicroSeries-named but not microdf's
    ],
)
def test_weighted_population_refuses_non_microseries_objects(unweighted):
    assert weighted_population(unweighted) is None


def test_weighted_population_never_touches_weight_arrays():
    """The module contract forbids touching weight arrays; the check is
    type identity + MicroSeries.count() (the weighted count), never a
    .weights read. Checked on the AST so docstrings don't count."""
    src = inspect.getsource(uk.weighted_population) + inspect.getsource(
        uk._is_microseries
    )
    accessed = {
        node.attr
        for node in ast.walk(ast.parse(src))
        if isinstance(node, ast.Attribute)
    }
    assert "weights" not in accessed


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
        "baseline", "bhc", _fake_microseries(67_000_000.0)
    )
    assert out == 67_000_000.0
    assert rows[before]["status"] == "ok"
    assert rows[before]["value"] == 67_000_000.0
    assert rows[before]["subgroup"] == "total"
    del rows[before:]


def test_population_denominator_carries_its_subgroup():
    """Each numerator cut gets a matching denominator row: the subgroup
    lands on the denominator so a children's rate divides by children."""
    before = len(rows)
    emit_population_denominator(
        "baseline", "ahc", _fake_microseries(12_000_000.0), "children"
    )
    assert rows[before]["subgroup"] == "children"
    assert rows[before]["metric"] == "population_ahc"
    del rows[before:]


# --- geography restriction refusal -----------------------------------------


def test_restricted_mask_refuses_unanchored_restrictions():
    """A GB/NI line whose entity has no country anchor must go pe_gap —
    an unrestricted total is never emitted under a restricted label."""
    masks = {"person": {"UK": [True], "GB": [True], "NI": [False]}}
    _, honoured = restricted_mask(masks, "benunit", "GB")
    assert not honoured
    _, honoured = restricted_mask(masks, "person", "GB")
    assert honoured


def test_restricted_mask_treats_uk_as_unrestricted():
    _, honoured = restricted_mask({}, "household", "UK")
    assert honoured


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
    with pytest.raises(RuntimeError, match="pension_credit"):
        uk.assert_fullpart_moved(base, same)


def test_nothing_comparable_is_a_hard_failure():
    base = [_row("baseline", "pension_credit", "recipient_count", None, "pe_gap")]
    full = [_row("fullpart", "pension_credit", "recipient_count", None, "pe_gap")]
    with pytest.raises(RuntimeError, match="nothing verifies"):
        uk.assert_fullpart_moved(base, full)


def test_one_benefit_moving_does_not_bless_another():
    """The silent-100%-take-up failure class: UC moved but PC did not.
    A global any-value-moved check passes this; the per-benefit contract
    must fail it, naming the stuck benefit."""
    base = [
        _row("baseline", "universal_credit", "recipient_count", 5_000_000.0),
        _row("baseline", "pension_credit", "recipient_count", 1_320_000.0),
    ]
    full = [
        _row("fullpart", "universal_credit", "recipient_count", 6_400_000.0),
        _row("fullpart", "pension_credit", "recipient_count", 1_320_000.0),
    ]
    with pytest.raises(RuntimeError, match="pension_credit"):
        uk.assert_fullpart_moved(base, full)


def test_stuck_component_warns_but_does_not_fail():
    """savings_credit is closed to new claims: a forced-on PC can move
    the aggregate while the component stays put — warn-only."""
    base = [
        _row("baseline", "pension_credit", "recipient_count", 1_320_000.0),
        _row("baseline", "savings_credit", "recipient_count", 120_000.0),
        _row("baseline", "universal_credit", "recipient_count", 5_000_000.0),
        _row("baseline", "housing_benefit", "recipient_count", 2_000_000.0),
        _row("baseline", "child_benefit", "recipient_count", 7_000_000.0),
        _row("baseline", "housing_benefit_pensioners", "recipient_count", 1_100_000.0),
    ]
    full = [
        _row("fullpart", "pension_credit", "recipient_count", 2_100_000.0),
        _row("fullpart", "savings_credit", "recipient_count", 120_000.0),
        _row("fullpart", "universal_credit", "recipient_count", 6_400_000.0),
        _row("fullpart", "housing_benefit", "recipient_count", 2_600_000.0),
        _row("fullpart", "child_benefit", "recipient_count", 7_300_000.0),
        _row("fullpart", "housing_benefit_pensioners", "recipient_count", 1_400_000.0),
    ]
    uk.assert_fullpart_moved(base, full)
    assert meta["fullpart_moved"]["by_program"]["savings_credit"] == {
        "compared": 1,
        "moved": 0,
    }


def test_moved_fullpart_passes_and_is_logged_per_program():
    base = [_row("baseline", "pension_credit", "recipient_count", 1_320_000.0)]
    full = [_row("fullpart", "pension_credit", "recipient_count", 2_100_000.0)]
    uk.assert_fullpart_moved(base, full)
    assert meta["fullpart_moved"]["compared"] == 1
    assert meta["fullpart_moved"]["moved"] == 1
    assert meta["fullpart_moved"]["by_program"]["pension_credit"] == {
        "compared": 1,
        "moved": 1,
    }


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
