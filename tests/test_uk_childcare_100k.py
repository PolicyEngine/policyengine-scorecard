"""The £100,000 childcare limit costings (lane uk-childcare-100k): CenTax's
Table 4.2 and the Centre for British Progress appendix are exactly what the
adapters derive from the vendored PDFs; the QC catches broken tables; the
certified-pair artifact ran on exactly its variant's pairing and moves only
the childcare heads, in England; every result's status is one stated
annotation; every certified run and the published dashboard figure stay in
the history; and a reform estimate is never a calibration target."""

import ast
import builtins
import copy
import datetime as dt
import hashlib
import importlib.util
import json
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from collections import Counter
from itertools import product
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
from hypothesis import example, given, settings
from hypothesis import strategies as st

from scorecard_db import ingest_uk_childcare_100k as lane
from scorecard_db.models import STANDARD_CONDITIONS
from scorecard_db.models import CalibrationRelationship as CR
from scorecard_db.relationships import uk_relationship

REPO = Path(__file__).resolve().parent.parent
CENTAX_SRC = REPO / "sources" / "centax-childcare-100k"
CBP_SRC = REPO / "sources" / "cbp-rates-and-wrongs"
DB = REPO / "data" / "scorecard.db"
CERTIFIED = json.loads((REPO / "data" / "uk" / "certified_bundle.json").read_text())
VARIANTS = json.loads((REPO / "data" / "uk" / "replay_variants.json").read_text())

# Table 4.2 as printed (printed page 41), read from the PDF on 2026-10-21:
# (scenario, year) -> (bunching before, after, static, intensive, extensive, net), £m
TABLE_4_2 = {
    ("central", 2028): (13_360, 3_850, -800, 150, 120, -520),
    ("central", 2030): (16_280, 4_300, -980, 210, 130, -640),
    ("high_cost", 2028): (9_710, 3_850, -820, 100, 120, -610),
    ("high_cost", 2030): (10_860, 4_300, -1_010, 120, 120, -770),
    ("low_cost", 2028): (58_510, 3_850, -580, 630, 90, 140),
    ("low_cost", 2030): (67_650, 4_300, -700, 770, 90, 160),
}
# CBP technical appendix, "Abolish Cliff" rows, £bn as printed
CBP_ABOLISH = {
    "endogenous_pension_exogenous_labour": (0.070, 0.077, 0.091, 0.132, 0.147, 0.172),
    "endogenous_labour_no_pension": (0.330, 0.349, 0.399, 0.427, 0.462, 0.507),
}


def _module(name: str, path: Path):
    # a unique module name: several lanes ship an adapter.py; registered as
    # an import registers it, so sys.modules[__name__] reads as in a real run
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def centax():
    return _module("centax_childcare_adapter", CENTAX_SRC / "adapter.py")


@pytest.fixture(scope="module")
def cbp():
    return _module("cbp_rates_and_wrongs_adapter", CBP_SRC / "adapter.py")


@pytest.fixture(scope="module")
def artifact():
    return lane.load_artifact()[0]


def _pair(art: dict) -> dict:
    """The verified_pairs entry of the artifact's pair."""
    return lane.verified_pair(lane.load_notes(), art)


# every committed certified-pair artifact, oldest first
_ARTIFACTS = lane.load_artifacts()
_ARTIFACT_IDS = [a["variant_id"] for a, _ in _ARTIFACTS]
# the 19 June pair's run, which predates the artifact's record of each
# child's own cap on funded hours
JUNE = "pe5.0.2_uk2.89.2_populace-uk-2023-dd68c73-4aa4b14-20260619T023711Z"
# the pair policyengine.py 6.11.0 certifies, policyengine-scorecard#228's run
PAIR_6110 = (
    "pair-pe6.11.0_uk2.132.6_microcosm-uk-2024-25-national-20261019T083323Z-6cba5d71"
)


@pytest.fixture
def june():
    return next(a for a, _ in _ARTIFACTS if a["variant_id"] == JUNE)


@pytest.fixture
def pair_6110():
    return next(a for a, _ in _ARTIFACTS if a["variant_id"] == PAIR_6110)


# --- the vendored sources ---------------------------------------------------


@pytest.mark.parametrize("src", [CENTAX_SRC, CBP_SRC])
def test_raw_files_match_their_recorded_hashes(src):
    recorded = json.loads((src / "source.json").read_text())["raw_sha256"]
    assert set(recorded) == {p.name for p in (src / "raw").iterdir()}
    for name, digest in recorded.items():
        assert hashlib.sha256((src / "raw" / name).read_bytes()).hexdigest() == digest


@pytest.mark.skipif(shutil.which("pdftotext") is None, reason="needs poppler")
@pytest.mark.parametrize("src", [CENTAX_SRC, CBP_SRC])
def test_page_extract_is_a_faithful_extract_of_the_pdf(src):
    """Every page of the extract re-extracts from the PDF byte for byte, so
    a number in the extract is a number in the publication."""
    spec = json.loads((src / "source.json").read_text())
    pdf = next(p for p in (src / "raw").iterdir() if p.suffix == ".pdf")
    text = (src / "raw" / "pages_layout.txt").read_text()
    chunks = text.split("=== PDF page ")[1:]
    assert [int(c.split(" ", 1)[0].split("=")[0]) for c in chunks] == spec[
        "pages_extracted"
    ]["pdf_pages"]
    for chunk in chunks:
        header, body = chunk.split("===\n", 1)
        page = int(header.split()[0])
        fresh = subprocess.run(
            ["pdftotext", "-layout", "-f", str(page), "-l", str(page), str(pdf), "-"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        assert body == fresh, f"{src.name} PDF page {page}"


def test_centax_extract_is_the_adapters_output_and_the_published_table(centax):
    rows = centax.tidy(centax.parse_table_4_2(centax.pages()[42]))
    assert rows == json.loads(
        (REPO / "data/externals/centax-childcare-100k.json").read_text()
    )
    assert len(rows) == centax.EXPECTED_ROWS == 36
    columns = (*centax.COUNTS, *centax.MONEY)
    for (scenario, year), printed in TABLE_4_2.items():
        got = {
            r["column"]: r["value"]
            for r in rows
            if (r["variant"], r["period"]) == (scenario, year)
        }
        want = {
            c: v * (1_000_000 if c in centax.MONEY else 1)
            for c, v in zip(columns, printed)
        }
        assert got == want, (scenario, year)
    assert {r["fy"] for r in rows if r["period"] == 2028} == {"2027-28"}
    assert {r["fy"] for r in rows if r["period"] == 2030} == {"2029-30"}


def test_centax_run_passes_every_qc(centax):
    assert len(centax.run()) == 36


def test_centax_qc_catches_a_component_that_no_longer_adds_up(centax):
    table = centax.parse_table_4_2(centax.pages()[42])
    table[("central", 2028)]["static_cost"] -= 30
    with pytest.raises(ValueError, match="components miss net"):
        centax.check_sums(table)


def test_centax_qc_catches_table_4_3_disagreeing(centax):
    pages = centax.pages()
    table = centax.parse_table_4_2(pages[42])
    table[("central", 2030)]["net_fiscal_cost"] = -650
    with pytest.raises(ValueError, match="Table 4.3"):
        centax.check_table_4_3(table, pages[45])


def test_centax_qc_catches_prose_disagreeing(centax):
    pages = centax.pages()
    table = centax.parse_table_4_2(pages[42])
    table[("central", 2030)]["intensive_margin"] = 200
    with pytest.raises(ValueError, match="prose"):
        centax.check_prose(table, pages[42] + pages[43])


def test_centax_qc_catches_a_shifted_row(centax):
    text = centax.pages()[42].replace("13,360", "13,360       9", 1)
    with pytest.raises(ValueError):
        centax.parse_table_4_2(text)


def test_cbp_extract_is_the_adapters_output_and_the_published_tables(cbp):
    rows = cbp.run()
    assert rows == json.loads(
        (REPO / "data/externals/cbp-rates-and-wrongs.json").read_text()
    )
    assert len(rows) == cbp.EXPECTED_ROWS == 72
    for model, printed in CBP_ABOLISH.items():
        got = [
            r["value"]
            for r in rows
            if (r["variant"], r["policy"]) == (model, "abolish_cliff")
        ]
        assert got == [round(v * 1e9) for v in printed]
    assert [r["fy"] for r in rows[:6]] == [
        "2026-27",
        "2027-28",
        "2028-29",
        "2029-30",
        "2030-31",
        "2031-32",
    ]
    assert [r["period"] for r in rows[:6]] == [2027, 2028, 2029, 2030, 2031, 2032]


def test_cbp_qc_catches_a_column_shift(cbp):
    pages = cbp.pages()
    table = cbp.parse_table("2", pages[8])
    table["taper_1pct"][3] = ("0.100", 0.100)
    with pytest.raises(ValueError, match="not rising"):
        cbp.check_order("2", table)


# --- properties of the adapters' arithmetic ----------------------------------


@settings(deadline=None)
@given(
    st.lists(
        st.floats(min_value=-2_000, max_value=2_000, allow_nan=False),
        min_size=3,
        max_size=3,
    )
)
def test_rounding_tolerance_covers_any_three_components(parts):
    """Invariant behind QC 4: if net is the exact sum of three components and
    each of the four figures is rounded to the nearest £10m, the rounded
    components miss the rounded net by at most SUM_TOLERANCE_GBP_M."""
    a = _module("centax_childcare_adapter_p", CENTAX_SRC / "adapter.py")
    step = a.ROUNDING_GBP_M

    def rnd(x):
        return step * round(x / step)

    net = sum(parts)
    assert abs(sum(rnd(p) for p in parts) - rnd(net)) <= a.SUM_TOLERANCE_GBP_M


@settings(deadline=None)
@given(st.integers(min_value=-99_999, max_value=99_999))
def test_money_cells_round_trip(value):
    a = _module("centax_childcare_adapter_r", CENTAX_SRC / "adapter.py")
    cell = f"{'+' if value >= 0 else '-'}{abs(value):,}m"
    assert a._gbp_m(cell) == value


# --- the certified-pair artifact ---------------------------------------------


@pytest.mark.parametrize("variant, engine", [(JUNE, "2.89.2"), (PAIR_6110, "2.132.6")])
def test_artifact_ran_on_its_certified_pair_without_behaviour(variant, engine):
    art = next(a for a, _ in _ARTIFACTS if a["variant_id"] == variant)
    dataset = lane.run_records()[variant]["identity"]["dataset"]
    assert art["data_bundle"] == dataset["revision"]
    assert art["dataset"]["sha256"] == dataset["sha256"]
    assert art["engine_version"] == engine
    assert art["behavioural_response"] == "none (static)"
    for world in (*art["worlds"].values(), *art["diagnostics"].values()):
        assert world["dataset_sha256_before"] == world["dataset_sha256_after"]


def test_each_world_removes_exactly_its_limits(artifact):
    hours = "gov.dfe.extended_childcare_entitlement.income.limit"
    tfc = "gov.hmrc.tax_free_childcare.income.income_limit"
    for year, block in artifact["worlds"]["baseline"]["years"].items():
        assert block["limits_executed"] == {hours: 100_000.0, tfc: 100_000.0}, year
    for year, block in artifact["worlds"]["free_hours"]["years"].items():
        assert block["limits_executed"] == {hours: 1e100, tfc: 100_000.0}, year
    for year, block in artifact["worlds"]["free_hours_and_tfc"]["years"].items():
        assert block["limits_executed"] == {hours: 1e100, tfc: 1e100}, year


def _d(art, world, year, var, group="worlds", base="baseline", sums="sums_gbp"):
    years = art[group]
    return (
        years[world]["years"][year][sums][var] - years[base]["years"][year][sums][var]
    )


def test_reforms_move_only_the_childcare_heads(artifact):
    heads = (*lane.FREE_HOURS, lane.TFC)
    for world in ("free_hours", "free_hours_and_tfc"):
        for year in artifact["worlds"][world]["years"]:
            moved = sum(_d(artifact, world, year, v) for v in heads)
            assert abs(_d(artifact, world, year, "gov_spending") - moved) < 1e6
            assert abs(_d(artifact, world, year, "gov_tax")) < 1e6
    # removing the 30-hours limit leaves Tax-Free Childcare alone
    for year in artifact["worlds"]["free_hours"]["years"]:
        assert abs(_d(artifact, "free_hours", year, lane.TFC)) < 1e6


def test_free_hours_leg_is_the_same_in_both_worlds(artifact):
    """Differential: the TFC limit does not touch the free hours, so the two
    reform worlds agree on every free-hours head."""
    for year in artifact["years"]:
        for v in lane.FREE_HOURS:
            a = artifact["worlds"]["free_hours"]["years"][str(year)]["sums_gbp"][v]
            b = artifact["worlds"]["free_hours_and_tfc"]["years"][str(year)][
                "sums_gbp"
            ][v]
            assert a == pytest.approx(b, rel=1e-12, abs=1.0), (year, v)


def test_removing_the_limit_costs_money_and_switches_universal_hours_off(june):
    for year in june["worlds"]["free_hours"]["years"]:
        assert lane.counterpart(june, lane.CENTAX, int(year)) < 0
        assert _d(june, "free_hours", year, "extended_childcare_entitlement") > 0
        assert _d(june, "free_hours", year, "universal_childcare_entitlement") < 0


def test_removing_the_limit_keeps_universal_and_targeted_hours(pair_6110):
    """The pe-universal-hours-kept note: the reform never lowers universal or
    targeted hours on 2.132.6, raises universal spending in every year and
    leaves targeted spending where it was."""
    for year in pair_6110["worlds"]["free_hours"]["years"]:
        assert lane.counterpart(pair_6110, lane.CENTAX, int(year)) < 0
        for head, moved in (
            ("extended_childcare_entitlement", True),
            ("universal_childcare_entitlement", True),
            ("targeted_childcare_entitlement", False),
        ):
            change = _d(pair_6110, "free_hours", year, head)
            assert change > 0 if moved else change == 0, (year, head)


def test_full_use_diagnostic_took_effect_and_costs_more(artifact):
    diag = artifact["diagnostics"]
    for world in diag.values():
        assert world["input_override"]["value"] == 30.0
        for mean in world["input_override"]["post_set_weighted_mean"].values():
            assert mean == pytest.approx(30.0)
        # set before anything that reads it was calculated ...
        overridden = world["input_override"]["dependents_calculated_before_override"]
        assert overridden and not any(overridden.values())
    # ... so it reached the entitlement: full use funds more extended hours
    for year in diag["baseline__full_use_hours"]["years"]:
        full = diag["baseline__full_use_hours"]["years"][year]["sums_gbp"]
        drawn = artifact["worlds"]["baseline"]["years"][year]["sums_gbp"]
        ext = "extended_childcare_entitlement"
        assert full[ext] > drawn[ext]
    for year in diag["baseline__full_use_hours"]["years"]:
        full = sum(
            diag["free_hours__full_use_hours"]["years"][year]["sums_gbp"][v]
            - diag["baseline__full_use_hours"]["years"][year]["sums_gbp"][v]
            for v in lane.FREE_HOURS
        )
        assert full > -lane.counterpart(artifact, lane.CENTAX, int(year))


def test_no_child_under_one_receives_extended_hours(artifact):
    """The pe-under-ones construction note states both facts for every world
    and year; the artifact must keep them true."""
    for group in ("worlds", "diagnostics"):
        for world in artifact[group].values():
            for block in world["years"].values():
                assert block["counts"]["children_under_one_receiving_extended"] == 0
                assert block["counts"]["people_with_fractional_age"] == 0
                assert block["counts"]["children_under_one"] > 0


def test_counterparts_count_england_only(artifact):
    """Both offers are England's: each counterpart is minus the change in
    the heads for people in English households, no free-hours head moves
    outside England, and England's Tax-Free Childcare is part of the UK's."""
    for world, source in (
        ("free_hours", lane.CENTAX),
        ("free_hours_and_tfc", lane.CBP),
    ):
        for year in artifact["worlds"][world]["years"]:
            eng = {
                v: _d(artifact, world, year, v, sums=lane.ENGLAND)
                for v in (*lane.FREE_HOURS, lane.TFC)
            }
            assert lane.counterpart(artifact, source, int(year)) == pytest.approx(
                -sum(eng[v] for v in lane.VARIABLES[source]), abs=1.0
            )
            for v in lane.FREE_HOURS:
                assert abs(_d(artifact, world, year, v) - eng[v]) < 1e6, (year, v)
            block = artifact["worlds"][world]["years"][year]
            assert (
                0 <= block["sums_gbp_england"][lane.TFC] <= block["sums_gbp"][lane.TFC]
            )


def test_free_hours_moving_outside_england_is_refused(artifact):
    bad = copy.deepcopy(artifact)
    year = next(iter(bad["worlds"]["free_hours"]["years"]))
    sums = bad["worlds"]["free_hours"]["years"][year]["sums_gbp"]
    # a UK-wide move with no English counterpart, kept inside gov_spending
    sums["extended_childcare_entitlement"] += 5e6
    sums["gov_spending"] += 5e6
    with pytest.raises(ValueError, match="outside England"):
        lane.measured_notes(bad, lane.CENTAX, int(year), "fy", _pair(bad))


@pytest.mark.parametrize("pair", _ARTIFACTS, ids=_ARTIFACT_IDS)
def test_artifact_records_the_inputs_and_metadata_it_read(pair):
    """Every committed run records the compute script's inputs, but a run
    from before the child hours input was recorded lacks only that one, and
    its pair's verified_pairs entry then states it from the dataset."""
    artifact, _ = pair
    compute = _module(
        "compute_uk_childcare_100k", REPO / "pipeline" / "compute_uk_childcare_100k.py"
    )
    assert set(artifact["variable_metadata"]) == set(compute.METADATA)
    for group in ("worlds", "diagnostics"):
        for world in artifact[group].values():
            recorded = set(world["dataset_inputs"])
            if compute.CHILD_HOURS not in recorded:
                assert _pair(artifact)["child_hours_input"]
                recorded.add(compute.CHILD_HOURS)
            assert recorded == set(compute.DATASET_INPUTS)
            for block in world["years"].values():
                assert set(block["take_up"]) == set(compute.TAKE_UP)
                assert all(0 <= x <= 1 for x in block["take_up"].values())


class Unvouched(AssertionError):
    """The metadata contract cannot vouch for a name the source calculates."""


_COMPS = (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)
_SCOPES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef, *_COMPS)
# Forms that bind a name out of a scope scan's sight (an assignment
# expression in a comprehension or a default binds the enclosing function;
# global and nonlocal reach other scopes; match patterns bind bare strings),
# or reach calculate other than by a direct call. The compute script uses
# none, so the scan refuses each wherever it appears.
_HIDDEN = (ast.NamedExpr, ast.Global, ast.Nonlocal, ast.Match)
_DYNAMIC = frozenset(
    {
        "eval",
        "exec",
        "compile",
        "globals",
        "locals",
        "vars",
        "__import__",
        "setattr",
        "delattr",
        "attrgetter",
        "methodcaller",
        "__builtins__",
    }
)


# Vetted functions that walk to whatever attribute a dotted path names:
# compute_uk_ab2025._resolve_parameter is getattr in a loop, so the scan
# holds each call to a direct call whose path it resolves, as it resolves a
# calculate name, to parameter paths that never name calculate.
_GETTERS = frozenset({"_resolve_parameter"})
_PARAMETER_PATH = re.compile(r"gov(\.[a-z][a-z0-9_]*(\[\d+\])?)+")

# What the compute script reaches numpy, the engine and the standard library
# through: each import, builtin name and attribute name it uses (getattr's
# literal names included). Each was read for a route to calculate other than
# a direct .calculate(...) call. The one such route is a getter in _GETTERS,
# held to parameter paths; so with the forms refused here every calculate
# the script's own code makes is a direct call the scan resolves. A name not
# listed is refused until it is read and added.
_VETTED_IMPORTS = frozenset(
    {
        ("", "argparse", None),
        ("", "datetime", "dt"),
        ("", "gc", None),
        ("", "inspect", None),
        ("", "json", None),
        ("", "numpy", "np"),
        ("", "string", None),
        ("", "sys", None),
        ("", "time", None),
        ("__future__", "annotations", None),
        ("pathlib", "Path", None),
        ("pipeline", "compute_uk_ab2025", "ab"),
        ("pipeline", "compute_uk_event", "event"),
        ("pipeline", "compute_uk_obr_costings", "fiscal"),
        ("pipeline", "modal_uk_event", None),
        ("pipeline", "uk_certified_pairs", "pairs"),
        ("pipeline", "uk_replay_variants", "variants"),
    }
)
_VETTED_NAMES = frozenset(
    {
        "SystemExit",
        "__doc__",
        "__file__",
        "__name__",
        "any",
        "bool",
        "dict",
        "float",
        "getattr",
        "int",
        "isinstance",
        "len",
        "list",
        "print",
        "set",
        "sorted",
        "str",
        "tuple",
        "type",
    }
)
_VETTED_ATTRIBUTES = frozenset(
    {
        "ArgumentParser",
        "HF_COMMIT",
        "NO_LIMIT",
        "PACKAGES",
        "_resolve_parameter",
        "abs",
        "add_argument",
        "allclose",
        "array_equal",
        "asarray",
        "ascii_lowercase",
        "ascii_uppercase",
        "assert_managed_bundle",
        "build_sim",
        "calculate",
        "check_variant_environment",
        "collect",
        "count",
        "data_bundle_id",
        "dataset",
        "dataset_file",
        "datetime",
        "default_value",
        "defined_for",
        "definition_period",
        "diagnostic_years",
        "documentation",
        "dumps",
        "entity",
        "exit",
        "full",
        "get",
        "get_holder",
        "get_known_periods",
        "get_record",
        "getsourcefile",
        "insert",
        "is_legacy",
        "isoformat",
        "items",
        "key",
        "label",
        "maketrans",
        "map_result",
        "mkdir",
        "ndarray",
        "now",
        "output_dir",
        "parameters",
        "parent",
        "parse_args",
        "path",
        "perf_counter",
        "policyengine_bundle",
        "pop",
        "populations",
        "preflight",
        "reform_dict",
        "relative_to",
        "relative_to_root",
        "resolve",
        "round",
        "run_id",
        "set_input",
        "split",
        "sum",
        "tax_benefit_system",
        "timezone",
        "translate",
        "unique",
        "unit",
        "utc",
        "values",
        "variables",
        "variant",
        "verify_import_origins",
        "verify_runtime_dataset_sha256",
        "weights",
        "write_text",
        "years",
    }
)


def _used(tree) -> tuple[frozenset, frozenset, frozenset]:
    """(imports, builtin and dunder names, attribute names) a module uses;
    an import is (module with any leading dots, name, alias)."""
    imports, names, attributes = set(), set(), set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports |= {("", a.name, a.asname) for a in node.names}
        elif isinstance(node, ast.ImportFrom):
            module = "." * node.level + (node.module or "")
            imports |= {(module, a.name, a.asname) for a in node.names}
        elif isinstance(node, ast.Name) and (
            hasattr(builtins, node.id) or node.id.startswith("__")
        ):
            names.add(node.id)
        elif isinstance(node, ast.Attribute):
            attributes.add(node.attr)
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "getattr"
            and len(node.args) > 1
            and isinstance(node.args[1], ast.Constant)
        ):
            attributes.add(node.args[1].value)
    return frozenset(imports), frozenset(names), frozenset(attributes)


def _binds(node, name: str) -> bool:
    """Does this node bind `name` in the scope it sits in?"""
    if isinstance(node, ast.Name):
        return node.id == name and isinstance(node.ctx, ast.Store | ast.Del)
    if isinstance(node, ast.arg):
        return node.arg == name
    if isinstance(node, ast.alias):
        return (node.asname or node.name).split(".")[0] == name
    if isinstance(node, ast.ExceptHandler):
        return node.name == name
    if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
        return node.name == name
    return False


def _stores(scope, name: str) -> list:
    """Every binding of `name` in this scope, not in scopes nested in it."""
    out = []

    def visit(node):
        for child in ast.iter_child_nodes(node):
            if _binds(child, name):
                out.append(child)
            if not isinstance(child, _SCOPES):
                visit(child)

    if isinstance(scope, ast.FunctionDef | ast.AsyncFunctionDef | ast.Lambda):
        out += [a for a in ast.walk(scope.args) if _binds(a, name)]
    visit(scope)
    return out


def _refuse_hidden(tree, parents) -> None:
    """Raise on any form in _HIDDEN or _DYNAMIC, on 'calculate' or a getter
    in _GETTERS named as a string or reached other than by a direct call, on
    getattr without a literal attribute name, and on an attribute write that
    rebinds a module constant of another object (sys.modules[__name__].X)."""
    constants = {
        t.id
        for node in tree.body
        if isinstance(node, ast.Assign | ast.AnnAssign)
        for t in (node.targets if isinstance(node, ast.Assign) else [node.target])
        if isinstance(t, ast.Name)
    }
    for node in ast.walk(tree):
        line = getattr(node, "lineno", "?")
        parent = parents.get(node)
        called = isinstance(parent, ast.Call) and parent.func is node
        if isinstance(node, _HIDDEN):
            raise Unvouched(f"line {line}: {type(node).__name__} binds out of sight")
        if isinstance(node, ast.Name) and node.id in _DYNAMIC:
            raise Unvouched(f"line {line}: {node.id} can bind or call by name")
        if isinstance(node, ast.Constant) and node.value in {"calculate", *_GETTERS}:
            raise Unvouched(f"line {line}: {node.value!r} named by a string")
        if isinstance(node, ast.Name) and node.id == "getattr":
            attr = parent.args[1] if called and len(parent.args) > 1 else None
            if not (isinstance(attr, ast.Constant) and isinstance(attr.value, str)):
                raise Unvouched(f"line {line}: getattr without a literal name")
        if isinstance(node, ast.Attribute):
            if node.attr in {"calculate", *_GETTERS} and not called:
                raise Unvouched(f"line {line}: {node.attr} used but not called")
            if node.attr == "__dict__":
                raise Unvouched(f"line {line}: a namespace read as a dict")
            if isinstance(node.ctx, ast.Store | ast.Del) and node.attr in constants:
                raise Unvouched(f"line {line}: an attribute write rebinds {node.attr}")


def _refuse_unvetted(tree) -> None:
    """Raise on any import, builtin name or attribute name not vetted."""
    vetted = (_VETTED_IMPORTS, _VETTED_NAMES, _VETTED_ATTRIBUTES)
    for kind, used, known in zip(("import", "name", "attribute"), _used(tree), vetted):
        if used - known:
            raise Unvouched(f"unvetted {kind}s {sorted(used - known, key=str)}")


def _refuse_classes(tree, parents) -> None:
    """Raise on a class the script defines, by a class statement or by
    type() with more than one argument. The script defines none. A method
    of such a class (resolve, __fspath__, __hash__, __float__, ...) is the
    script's code that library or engine code can call implicitly, inside
    a stub, an array conversion or a lookup, where the stand-in run does
    not follow."""
    for node in ast.walk(tree):
        line = getattr(node, "lineno", "?")
        if isinstance(node, ast.ClassDef):
            raise Unvouched(f"line {line}: class {node.name} could carry a callback")
        if isinstance(node, ast.Name) and node.id == "type":
            call = parents.get(node)
            if not (
                isinstance(call, ast.Call)
                and call.func is node
                and len(call.args) == 1
                and not call.keywords
                and not isinstance(call.args[0], ast.Starred)
            ):
                raise Unvouched(f"line {line}: type() other than on one object")


def _calculated(path: Path, compute) -> set[str]:
    """Every name the source passes to sim.calculate, read as Python scopes
    read it. A name must be a literal, or bound exactly once on the way out
    from the call: by the plain target of a loop or comprehension around the
    call, over a tuple display or a module tuple; or nowhere, a module
    string constant. Any other binding (an assignment, a second loop, a
    rebinding generator, an argument, a tuple target) raises, and so does
    any form _refuse_hidden lists, so a name cannot change unnoticed by a
    route this scan reads past. Each call of a getter in _GETTERS must have
    a path resolved the same way, to parameter paths only; then any name not
    vetted raises, so no route other than a direct call reaches calculate,
    and so does any class (_refuse_classes), so no method the script defines
    is called back unread. The stand-in run backs it up (_observed)."""
    tree = ast.parse(path.read_text())
    parents = {
        child: node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)
    }
    _refuse_hidden(tree, parents)

    def scopes(node):
        while node in parents:
            node = parents[node]
            if isinstance(node, _SCOPES):
                yield node

    def module_value(name: ast.Name):
        for scope in scopes(name):
            if _stores(scope, name.id):
                raise Unvouched(f"{name.id!r} is rebound before line {name.lineno}")
        found = _stores(tree, name.id)
        if len(found) != 1 or not isinstance(
            parents[found[0]], ast.Assign | ast.AnnAssign
        ):
            raise Unvouched(
                f"{name.id!r} is not one plain module assignment ({len(found)} bindings)"
            )
        return getattr(compute, name.id)

    def values(expr) -> list:
        if isinstance(expr, ast.Constant):
            return [expr.value]
        if isinstance(expr, ast.Name):
            value = module_value(expr)
            if not isinstance(value, tuple):
                raise Unvouched(f"{expr.id!r} is not a module tuple")
            return list(value)
        if isinstance(expr, ast.Tuple | ast.List):
            out = []
            for e in expr.elts:
                if isinstance(e, ast.Starred):
                    out += values(e.value)
                elif isinstance(e, ast.Name):
                    value = module_value(e)
                    if not isinstance(value, str):
                        raise Unvouched(f"{e.id!r} is not a module string")
                    out.append(value)
                else:
                    out += values(e)
            return out
        raise Unvouched(f"unresolved loop iterable {ast.dump(expr)}")

    def inside(node, block) -> bool:
        while node in parents:
            if any(node is b for b in block):
                return True
            node = parents[node]
        return False

    def resolve(name: ast.Name) -> list:
        for scope in scopes(name):
            found = _stores(scope, name.id)
            if not found:
                continue
            if len(found) > 1:
                raise Unvouched(
                    f"{name.id!r} is bound {len(found)} times around line {name.lineno}"
                )
            target = parents[found[0]]
            comprehension = (
                isinstance(scope, _COMPS)
                and isinstance(target, ast.comprehension)
                and target.target is found[0]
            )
            loop = (
                isinstance(target, ast.For)
                and target.target is found[0]
                and inside(name, target.body)
            )
            if comprehension or loop:
                return values(target.iter)
            raise Unvouched(
                f"{name.id!r} at line {name.lineno} is bound by "
                f"{type(target).__name__}, not a loop over known names"
            )
        value = module_value(name)
        if not isinstance(value, str):
            raise Unvouched(f"{name.id!r} is not a module string")
        return [value]

    calculated = set()
    for node in ast.walk(tree):
        if not (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "calculate"
        ):
            continue
        if node.keywords or not node.args or isinstance(node.args[0], ast.Starred):
            raise Unvouched(f"line {node.lineno}: calculate not called (name, period)")
        arg = node.args[0]
        if isinstance(arg, ast.Constant):
            calculated.add(arg.value)
        elif isinstance(arg, ast.Name):
            calculated |= set(resolve(arg))
        else:
            raise Unvouched(f"unresolved calculate argument {ast.dump(arg)}")
    for node in ast.walk(tree):
        if not (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr in _GETTERS
        ):
            continue
        if (
            node.keywords
            or len(node.args) != 2
            or isinstance(node.args[1], ast.Starred)
        ):
            raise Unvouched(
                f"line {node.lineno}: {node.func.attr} not called (node, path)"
            )
        arg = node.args[1]
        if isinstance(arg, ast.Constant):
            paths = [arg.value]
        elif isinstance(arg, ast.Name):
            paths = resolve(arg)
        else:
            raise Unvouched(
                f"line {node.lineno}: unresolved getter path {ast.dump(arg)}"
            )
        for p in paths:
            if not (isinstance(p, str) and _PARAMETER_PATH.fullmatch(p)) or (
                "calculate" in p.split(".")
            ):
                raise Unvouched(f"line {node.lineno}: {p!r} is not a parameter path")
    _refuse_unvetted(tree)
    _refuse_classes(tree, parents)
    return calculated


_PLAIN = (str, int, float, bool, type(None), type(Path()))


def _plain(*values) -> None:
    """Refuse any value whose type is not exactly one of _PLAIN, or a dict,
    list or tuple of them. A stub drops what it is passed, so an object the
    script defines could carry a callback that the real function would make
    (resolve, __fspath__, __eq__, ...) and the stand-in run would not see."""
    for v in values:
        if type(v) is dict:
            _plain(*v.keys(), *v.values())
        elif type(v) in (list, tuple):
            _plain(*v)
        elif type(v) not in _PLAIN:
            raise Unvouched(f"a stub was passed a {type(v).__name__}")


def _array(values) -> None:
    """Refuse anything but a plain ndarray of numbers, bools or strings: the
    engine converts an input array (astype(float)), which calls each member
    of an object array."""
    if type(values) is not np.ndarray:
        raise Unvouched(f"a stub was passed a {type(values).__name__}, not an array")
    if values.dtype.hasobject:
        raise Unvouched(f"a stub was passed an array of {values.dtype}")


def _stub(result):
    """A function outside the script that returns `result` and refuses any
    argument that is not plain (_plain)."""

    def call(*args, **kwargs):
        _plain(*args, *kwargs.values())
        return result

    return call


class _Series:
    def __init__(self, values):
        self.values = np.asarray(values)
        self.weights = np.ones(len(self.values))

    def sum(self):
        return float((self.values * self.weights).sum())


class _Parameter:
    """A parameter node: reading a child names it, and calling it on a date
    gives the reform's value there (start.stop, both days in) or £100,000."""

    def __init__(self, reform, path=""):
        self._reform, self._path = reform, path

    def __getattr__(self, part):
        return _Parameter(self._reform, f"{self._path}.{part}".lstrip("."))

    def __call__(self, date):
        _plain(date)
        for period, value in self._reform.get(self._path, {}).items():
            start, stop = period.split(".")
            if start <= date <= stop:
                return float(value)
        return 100_000.0


class _Variable:
    def __init__(self, name):
        self.label = name
        self.entity = SimpleNamespace(key="person")
        self.definition_period = "year"
        self.unit = self.documentation = self.defined_for = None
        self.default_value = 0.0


class _Variables(dict):
    def __missing__(self, name):
        return _Variable(name)


class _StandIn:
    """Stands in for each simulation the compute script builds, with no
    engine and no data, and records each (name, period) passed to
    calculate. It offers only what the script reads; reading anything else
    raises, so no other engine route goes unseen, and each method refuses an
    argument that is not plain (_plain) or an array. The hours input is
    drawn below 30 until set_input sets it, so the ordinary and full-use
    worlds each take their own branch, and every household but one is in
    England."""

    DRAWN = (12.0, 20.0, 25.0)

    def __init__(self, run, reform, years, source):
        self._run, self._inputs = run, {}
        self.dataset = SimpleNamespace(years=list(years))
        self.populations = {"benunit": SimpleNamespace(count=len(self.DRAWN))}
        self.policyengine_bundle = {"runtime_dataset_source": str(source)}
        self.tax_benefit_system = SimpleNamespace(
            parameters=_Parameter(reform or {}), variables=_Variables()
        )

    def __getattr__(self, name):
        raise Unvouched(f"the run read sim.{name}, which the stand-in does not offer")

    def calculate(self, variable, period):
        _plain(variable, period)
        self._run.calls.append((variable, int(period)))
        if variable == "country":
            return _Series(["ENGLAND", "WALES", "ENGLAND"])
        if variable == lane.HOURS_USAGE_INPUT:
            key = (variable, int(period))
            self._run.hours.append(
                (int(period), "set" if key in self._inputs else "drawn")
            )
            return _Series(self._inputs.get(key, self.DRAWN))
        if (variable, int(period)) in self._inputs:
            return _Series(self._inputs[variable, int(period)])
        return _Series([1000.0, 0.0, 500.0])

    def map_result(self, values, *entities, **how):
        _array(values)
        _plain(*entities, *how.values())
        return values

    def get_holder(self, variable):
        _plain(variable)
        return SimpleNamespace(get_known_periods=list)

    def set_input(self, variable, period, values):
        _plain(variable, period)
        _array(values)
        self._inputs[variable, int(period)] = values


def _observed(compute, monkeypatch) -> SimpleNamespace:
    """The compute script's main() run end to end on stand-in simulations:
    every world in every default year, and both full-use worlds. Only what
    lies outside the script and needs the engine, the data or the variant
    registry is stubbed: the variant record and preflight, the dataset hash,
    the bundle checks, the import-origin check and the simulation it builds
    (ab.build_sim). Each stub refuses an argument that is not plain, and the
    path helper (fiscal.relative_to_root) runs as it is. Returns each
    (name, period) passed to calculate, each read of the hours input (drawn
    or set) and each world's reform; the artifact written must record
    metadata for exactly METADATA."""
    run = SimpleNamespace(calls=[], hours=[], reforms=[])
    years = list(range(2023, 2031))
    out = Path(tempfile.mkdtemp(prefix="childcare-stand-in-")).resolve()
    source = out / "dataset.h5"
    sha = "0" * 64
    variant = {
        "variant_id": "stand-in",
        "data_years": years,
        "identity": {
            "dataset": {"revision": "stand-in", "sha256": sha, "repo_id": "stand-in"}
        },
        "identity_sha256": sha,
    }
    pre = {
        "installed": {
            "packages": {
                p: {"version": "0", "record_sha256": sha}
                for p in compute.variants.PACKAGES
            },
            "python": "stand-in",
            "packaged_bundle_manifest_sha256": sha,
        },
        "runtime_dataset_source": str(source),
        "sha256": sha,
        "release_bundle": {},
        "data_years": years,
    }

    def build(reform):
        _plain(reform)
        run.reforms.append(reform)
        return _StandIn(run, reform, years, source)

    monkeypatch.setattr(compute, "ROOT", out)
    monkeypatch.setattr(compute.pairs, "get_record", _stub(variant))
    monkeypatch.setattr(compute.variants, "is_legacy", _stub(False))
    monkeypatch.setattr(compute.variants, "verify_import_origins", _stub(None))
    monkeypatch.setattr(compute.pairs, "preflight", _stub(pre))
    monkeypatch.setattr(compute.fiscal, "data_bundle_id", _stub("stand-in"))
    monkeypatch.setattr(compute.fiscal, "verify_runtime_dataset_sha256", _stub(sha))
    monkeypatch.setattr(compute.fiscal, "assert_managed_bundle", _stub(None))
    monkeypatch.setattr(compute.ab, "build_sim", build)
    try:
        assert compute.main(["--output-dir", str(out)]) == 0
        written = json.loads((out / "stand-in.json").read_text())
    finally:
        shutil.rmtree(out)
    assert set(written["variable_metadata"]) == set(compute.METADATA)
    return run


def _contract(path: Path, name: str, monkeypatch) -> set[str]:
    """The pe_meta contract on one source file: the scan resolves every
    calculate argument, the stand-in run of main() sees exactly those
    names, and METADATA lists them all."""
    compute = _module(name, path)
    scanned = _calculated(path, compute)
    seen = {v for v, _ in _observed(compute, monkeypatch).calls}
    if seen != scanned:
        raise Unvouched(f"the run and the scan differ on {sorted(seen ^ scanned)}")
    if not scanned <= set(compute.METADATA):
        raise Unvouched(f"no metadata for {sorted(scanned - set(compute.METADATA))}")
    return scanned


def test_every_variable_the_run_calculates_has_its_metadata_recorded(monkeypatch):
    """The pe_meta contract, read off the source and observed on a
    recording simulation: each sim.calculate name is in METADATA, with each
    loop variable read in its own scope."""
    path = REPO / "pipeline" / "compute_uk_childcare_100k.py"
    compute = _module("compute_uk_childcare_100k_src", path)
    calculated = _contract(path, "compute_uk_childcare_100k_contract", monkeypatch)
    assert calculated == _calculated(path, compute)
    # both reused loop names resolve to their own tuples
    assert set(compute.SUMMED) | set(compute.TAKE_UP) <= calculated
    assert {
        "is_child",
        "is_child_receiving_extended_childcare",
        "country",
    } <= calculated
    assert calculated <= set(compute.METADATA)
    # each vetted name is one the script uses, so the lists are its own
    assert _used(ast.parse(path.read_text())) == (
        _VETTED_IMPORTS,
        _VETTED_NAMES,
        _VETTED_ATTRIBUTES,
    )


def test_the_stand_in_run_reaches_every_world_year_and_hours_branch(monkeypatch):
    """main() builds the three worlds and the two full-use worlds, the
    calculations run in every default year, and the hours input is read
    drawn in the ordinary worlds and set to 30 in the full-use ones."""
    path = REPO / "pipeline" / "compute_uk_childcare_100k.py"
    compute = _module("compute_uk_childcare_100k_reach", path)
    run = _observed(compute, monkeypatch)
    main = compute.worlds(compute.YEARS)
    diag = compute.worlds(compute.DIAGNOSTIC_YEARS)
    assert run.reforms == [*main.values(), diag["baseline"], diag["free_hours"]]
    assert {p for _, p in run.calls} == set(compute.YEARS)
    assert {p for p, how in run.hours if how == "drawn"} == set(compute.YEARS)
    assert {p for p, how in run.hours if how == "set"} == set(compute.DIAGNOSTIC_YEARS)


def test_the_metadata_scan_catches_a_summed_variable_left_out():
    """The mutation the review of #207 ran: drop the two SUMMED-only
    variables from METADATA and the contract must fail."""
    path = REPO / "pipeline" / "compute_uk_childcare_100k.py"
    compute = _module("compute_uk_childcare_100k_src_mut", path)
    pruned = set(compute.METADATA) - {"gov_spending", "gov_tax"}
    assert not _calculated(path, compute) <= pruned


def test_the_stand_in_run_sees_what_the_scan_cannot(monkeypatch):
    """A rebinding no source form shows (here a module constant changed at
    run time) reaches the stand-in run, which the contract then refuses."""
    path = REPO / "pipeline" / "compute_uk_childcare_100k.py"
    compute = _module("compute_uk_childcare_100k_runtime", path)
    scanned = _calculated(path, compute)
    monkeypatch.setattr(compute, "HOURS_USAGE", "employment_income")
    seen = {v for v, _ in _observed(compute, monkeypatch).calls}
    assert "employment_income" in seen
    assert seen != scanned


_UNREAD = '"employment_income"'
_YEAR_DOC = (
    '    """Weighted sums and counts for one world and year (microdf weights)."""\n'
)
_HEADS_LOOP = "    for v in HEADS:\n"
_LIMITS_BODY = "    params = sim.tax_benefit_system.parameters\n"
_BUILT = '"cal" + "culate"'
_IN_2029 = "    if year == 2029:\n"
# the round-5 review's thirteen survivors: calculate reached through a name
# the scan did not vet, in a helper the old recording run replaced, in a
# year it did not run (2029) or on the drawn-hours branch it never took
_SURVIVORS = {
    "import_alias_in_helper": (
        _LIMITS_BODY,
        (
            "    from builtins import getattr as lookup\n"
            f"    lookup(sim, {_BUILT})({_UNREAD}, year)\n{_LIMITS_BODY}"
        ),
    ),
    "getattribute_in_helper": (
        _LIMITS_BODY,
        f"    sim.__getattribute__({_BUILT})({_UNREAD}, year)\n{_LIMITS_BODY}",
    ),
    "class_body_in_2029": (
        _YEAR_DOC,
        (
            f"{_YEAR_DOC}{_IN_2029}        class ReadExtra:\n"
            f"            extra = sim.__getattribute__({_BUILT})({_UNREAD}, year)\n"
        ),
    ),
    "decorator_in_2029": (
        _YEAR_DOC,
        (
            f"{_YEAR_DOC}    def decorate(f):\n    {_IN_2029}"
            f"            sim.__getattribute__({_BUILT})({_UNREAD}, year)\n"
            "        return f\n    @decorate\n    def unused():\n        pass\n"
        ),
    ),
    "dict_of_functions_in_2029": (
        _YEAR_DOC,
        (
            f"{_YEAR_DOC}{_IN_2029}"
            f'        calls = {{"read": sim.__getattribute__({_BUILT})}}\n'
            f'        calls["read"]({_UNREAD}, year)\n'
        ),
    ),
    "exec_alias_in_2029": (
        _YEAR_DOC,
        (
            f"{_YEAR_DOC}    from builtins import exec as run_code\n{_IN_2029}"
            '        run_code("sim.cal" + "culate(\'employment_income\', year)")\n'
        ),
    ),
    "getattr_alias_in_2029": (
        _YEAR_DOC,
        (
            f"{_YEAR_DOC}    from builtins import getattr as lookup\n{_IN_2029}"
            f"        lookup(sim, {_BUILT})({_UNREAD}, year)\n"
        ),
    ),
    "getattribute_in_2029": (
        _YEAR_DOC,
        f"{_YEAR_DOC}{_IN_2029}        sim.__getattribute__({_BUILT})({_UNREAD}, year)\n",
    ),
    "drawn_hours_branch": (
        _YEAR_DOC,
        (
            f"{_YEAR_DOC}    if (sim.calculate(HOURS_USAGE, year).values < 30).any():\n"
            f"        sim.__getattribute__({_BUILT})({_UNREAD}, year)\n"
        ),
    ),
    "importlib_in_2029": (
        _YEAR_DOC,
        (
            f"{_YEAR_DOC}    import importlib as loader\n{_IN_2029}"
            '        loader.import_module("builtins").getattr(sim, '
            f"{_BUILT})({_UNREAD}, year)\n"
        ),
    ),
    "operator_alias_in_2029": (
        _YEAR_DOC,
        (
            f"{_YEAR_DOC}    import operator as op\n{_IN_2029}"
            f"        op.methodcaller({_BUILT}, {_UNREAD}, year)(sim)\n"
        ),
    ),
    "operator_from_alias_in_2029": (
        _YEAR_DOC,
        (
            f"{_YEAR_DOC}    from operator import methodcaller as invoke\n{_IN_2029}"
            f"        invoke({_BUILT}, {_UNREAD}, year)(sim)\n"
        ),
    ),
    "partial_in_2029": (
        _YEAR_DOC,
        (
            f"{_YEAR_DOC}    from functools import partial\n{_IN_2029}"
            f"        partial(sim.__getattribute__({_BUILT}), {_UNREAD})(year)\n"
        ),
    ),
}
_CALLBACK = f"            ab._resolve_parameter(sim, {_BUILT})({_UNREAD}, year)\n"
# the round-6 review's survivor, a callback the old run's path-helper stub
# dropped, and the getter routes to calculate it used: a vetted walker on a
# built, a literal or an aliased path
_ROUND_6 = {
    "callback_through_path_helper": (
        _YEAR_DOC,
        (
            f"{_YEAR_DOC}    class ChildcarePath:\n        def resolve(self):\n"
            f"{_CALLBACK}            return ROOT\n"
            "    fiscal.relative_to_root(ChildcarePath())\n"
        ),
    ),
    "getter_built_path": (
        _YEAR_DOC,
        f"{_YEAR_DOC}    ab._resolve_parameter(sim, {_BUILT})({_UNREAD}, year)\n",
    ),
    "getter_literal_path": (
        _YEAR_DOC,
        (
            f"{_YEAR_DOC}    ab._resolve_parameter(sim, "
            f'"calculate.__call__")({_UNREAD}, year)\n'
        ),
    ),
    "getter_alias": (
        _YEAR_DOC,
        (
            f"{_YEAR_DOC}    walk = ab._resolve_parameter\n"
            f'    walk(sim, "calculate.__call__")({_UNREAD}, year)\n'
        ),
    ),
    # the same callback handed to an engine method (a holder lookup hashes
    # its name) and to a function the run stubs
    "callback_through_engine_method": (
        _YEAR_DOC,
        (
            f"{_YEAR_DOC}    class Name(str):\n        def __hash__(self):\n"
            f"{_CALLBACK}            return 0\n"
            '    sim.get_holder(Name("age"))\n'
        ),
    ),
    "callback_through_stub": (
        _YEAR_DOC,
        (
            f"{_YEAR_DOC}    class Dataset:\n        def __fspath__(self):\n"
            f"{_CALLBACK}            return str(ROOT)\n"
            "    fiscal.verify_runtime_dataset_sha256("
            'Dataset(), "0" * 64, phase="year")\n'
        ),
    ),
}
_INPUT = '"employment_income_behavioral_response"'
# the round-7 review's survivor: the getter read by a literal getattr, from
# the __float__ of objects in an array the engine converts; the getter read
# by a string alone; and classes the class rule alone refuses, by a class
# statement and by type(), whose callbacks are direct calls
_ROUND_7 = {
    "object_array_callback": (
        _YEAR_DOC,
        (
            f"{_YEAR_DOC}    class ChildcareValue:\n        def __float__(self):\n"
            f'            getattr(ab, "_resolve_parameter")(sim, {_BUILT})'
            f"({_UNREAD}, year)\n            return 1.0\n"
            f"    sim.set_input(\n        {_INPUT},\n        year,\n"
            "        np.asarray("
            '[ChildcareValue()] * len(sim.calculate("age", year).values)),\n    )\n'
        ),
    ),
    "getter_named_by_string": (
        _YEAR_DOC,
        (
            f'{_YEAR_DOC}    getattr(ab, "_resolve_parameter")(sim, {_BUILT})'
            f"({_UNREAD}, year)\n"
        ),
    ),
    "class_calls_back": (
        _YEAR_DOC,
        (
            f"{_YEAR_DOC}    class Reader:\n        def __float__(self):\n"
            f"            return float(sim.calculate({_UNREAD}, year).sum())\n"
            f"    sim.set_input({_INPUT}, year, np.asarray([Reader()] * 3))\n"
        ),
    ),
    "class_by_type": (
        _YEAR_DOC,
        (
            f'{_YEAR_DOC}    Reader = type("Reader", (), {{"__float__": lambda _: '
            f"float(sim.calculate({_UNREAD}, year).sum())}})\n"
            f"    sim.set_input({_INPUT}, year, np.asarray([Reader()] * 3))\n"
        ),
    ),
}
# anchor -> mutant: each calculates a name the metadata does not list, by a
# route the contract must refuse
_MUTANTS = {
    # the round-3 review's two: a rebinding generator, and an assignment
    # inside the loop
    "rebinding_generator": (
        "for v in SUMMED}",
        f"for v in SUMMED for v in ({_UNREAD},)}}",
    ),
    "assignment_in_loop": (_HEADS_LOOP, f"{_HEADS_LOOP}        v = {_UNREAD}\n"),
    "shadowed_module_tuple": (_YEAR_DOC, f"{_YEAR_DOC}    SUMMED = ({_UNREAD},)\n"),
    "module_constant_bound_twice": (
        'HOURS_USAGE = "maximum_extended_childcare_hours_usage"\n',
        (
            'HOURS_USAGE = "maximum_extended_childcare_hours_usage"\n'
            f"HOURS_USAGE = {_UNREAD}\n"
        ),
    ),
    "tuple_target": ("for v in SUMMED}", "for v, _ in zip(SUMMED, SUMMED)}"),
    # the round-4 review's eight survivors and its mapping capture
    "getattr_call": (
        _YEAR_DOC,
        f'{_YEAR_DOC}    getattr(sim, "calculate")({_UNREAD}, year)\n',
    ),
    "alias_call": (
        _YEAR_DOC,
        f"{_YEAR_DOC}    calculate = sim.calculate\n    calculate({_UNREAD}, year)\n",
    ),
    "walrus_in_comprehension": (
        _YEAR_DOC,
        f"{_YEAR_DOC}    [(HOURS_USAGE := {_UNREAD}) for _ in (0,)]\n",
    ),
    "walrus_in_generator": (
        _YEAR_DOC,
        f"{_YEAR_DOC}    tuple((HOURS_USAGE := {_UNREAD}) for _ in (0,))\n",
    ),
    "nested_nonlocal": (
        _HEADS_LOOP,
        (
            f"{_HEADS_LOOP}        def rebind():\n            nonlocal v\n"
            f"            v = {_UNREAD}\n        rebind()\n"
        ),
    ),
    "nested_global": (
        _YEAR_DOC,
        (
            f"{_YEAR_DOC}    def rebind():\n        global HOURS_USAGE\n"
            f"        HOURS_USAGE = {_UNREAD}\n    rebind()\n"
        ),
    ),
    "default_walrus": (
        _YEAR_DOC,
        f"{_YEAR_DOC}    def _unused(arg=(HOURS_USAGE := {_UNREAD})):\n        pass\n",
    ),
    "default_getattr": (
        _YEAR_DOC,
        (
            f'{_YEAR_DOC}    def _unused(arg=getattr(sim, "calculate")({_UNREAD}, year)):\n'
            "        pass\n"
        ),
    ),
    "match_mapping_rest": (
        _HEADS_LOOP,
        f"{_HEADS_LOOP}        match {{}}:\n            case {{**v}}:\n                pass\n",
    ),
    # and a module constant rebound through the module object
    "module_attribute_write": (
        _YEAR_DOC,
        f"{_YEAR_DOC}    sys.modules[__name__].HOURS_USAGE = {_UNREAD}\n",
    ),
    **_SURVIVORS,
    **_ROUND_6,
    **_ROUND_7,
}
# What the stand-in run alone makes of each mutant (the scan refuses them
# all): it sees an unlisted name, or it does not, or a stub refuses the
# object a mutant passes it, or the mutant crashes before an artifact.
_RUN_ALONE = {
    # calculates only listed names
    "tuple_target": "listed",
    # METADATA is built from the rebound name, so the run lists it
    "module_constant_bound_twice": "listed",
    # TypeError (an unhashable dict) before the run writes an artifact
    "match_mapping_rest": "crash",
    "callback_through_engine_method": "refused",
    "callback_through_stub": "refused",
    # set_input refuses an object array
    "object_array_callback": "refused",
    "class_calls_back": "refused",
    "class_by_type": "refused",
}


def _mutant(tmp_path, anchor, mutant) -> Path:
    path = REPO / "pipeline" / "compute_uk_childcare_100k.py"
    source = path.read_text()
    assert source.count(anchor) == 1, anchor
    mutated = tmp_path / "compute_uk_childcare_100k.py"
    mutated.write_text(source.replace(anchor, mutant))
    return mutated


@pytest.mark.parametrize("anchor, mutant", _MUTANTS.values(), ids=list(_MUTANTS))
def test_the_metadata_contract_refuses_a_hidden_name(
    tmp_path, monkeypatch, anchor, mutant
):
    """Each mutant calculates a name the metadata does not list; the
    contract must refuse it rather than read the name's old binding."""
    mutated = _mutant(tmp_path, anchor, mutant)
    with pytest.raises(Unvouched):
        _contract(mutated, f"compute_mutant_{tmp_path.name}", monkeypatch)


@pytest.mark.parametrize("anchor, mutant", _MUTANTS.values(), ids=list(_MUTANTS))
def test_the_scan_alone_refuses_each_hidden_name(tmp_path, anchor, mutant):
    """The two layers each hold: with no run, the scan refuses every mutant."""
    mutated = _mutant(tmp_path, anchor, mutant)
    compute = _module(f"compute_scan_{tmp_path.name}", mutated)
    with pytest.raises(Unvouched):
        _calculated(mutated, compute)


def _alone(compute, monkeypatch) -> str:
    try:
        seen = {v for v, _ in _observed(compute, monkeypatch).calls}
    except Unvouched:
        return "refused"
    except TypeError:
        return "crash"
    return "unlisted" if seen - set(compute.METADATA) else "listed"


@pytest.mark.parametrize("name", list(_MUTANTS))
def test_what_the_stand_in_run_alone_makes_of_each_mutant(tmp_path, monkeypatch, name):
    """With the scan set aside, the stand-in run of main() reaches the
    calculation of every mutant but those in _RUN_ALONE: the helper each
    round-5 survivor hides in runs, and so do 2029, the drawn-hours branch
    and the path helper the round-6 callback goes through."""
    mutated = _mutant(tmp_path, *_MUTANTS[name])
    compute = _module(f"compute_alone_{tmp_path.name}", mutated)
    assert _alone(compute, monkeypatch) == _RUN_ALONE.get(name, "unlisted")


def test_a_stub_refuses_any_argument_the_script_could_define():
    """Each stub, and each stand-in method, refuses any argument whose type
    the script could have defined; plain values, paths and arrays pass."""
    _stub(None)(Path("x"), {"a": [1, 2.0, None]}, phase="p")
    _array(np.zeros(2))

    class Text(str):
        pass

    for value in (Text("x"), SimpleNamespace(), np.int64(1), [object()], {1: Text()}):
        with pytest.raises(Unvouched):
            _stub(None)(value)
    for values in (
        [1.0],
        np.asarray([object()]),
        np.zeros(2, dtype=[("a", object)]),
    ):
        with pytest.raises(Unvouched):
            _array(values)


def test_default_run_ids_differ_across_variants_and_runs():
    compute = _module(
        "compute_uk_childcare_100k_run_id",
        REPO / "pipeline" / "compute_uk_childcare_100k.py",
    )
    t = dt.datetime(2026, 10, 25, 20, 13, 47, tzinfo=dt.timezone.utc)
    ids = {
        compute.default_run_id(VARIANTS["default_variant"], t),
        compute.default_run_id(_wide_certified()["variant_id"], t),
        compute.default_run_id(
            VARIANTS["default_variant"], t + dt.timedelta(seconds=1)
        ),
    }
    assert len(ids) == 3


# --- the artifact's identity and history (synthetic: no engine, no run) --------


def _record(variant_id=None):
    vid = variant_id or VARIANTS["default_variant"]
    return copy.deepcopy(
        next(v for v in VARIANTS["variants"] if v["variant_id"] == vid)
    )


def _synthetic(variant, *, run_id="run", computed_at="2026-10-25T00:00:00+00:00"):
    identity = copy.deepcopy(variant["identity"])
    sha = identity["dataset"]["sha256"]
    world = {
        "dataset_sha256_before": sha,
        "dataset_sha256_after": sha,
        "runtime_dataset_source": "data/uk/policyengine-local/populace.h5",
        "dataset_years": list(variant["data_years"]),
        "years": {},
    }
    return {
        "schema_version": lane.SCHEMA_VERSION,
        "run_id": run_id,
        "computed_at": computed_at,
        "variant_id": variant["variant_id"],
        "variant_identity_sha256": variant["identity_sha256"],
        "packages": {
            name: {"version": pkg["version"], "record_sha256": pkg["record_sha256"]}
            for name, pkg in identity["packages"].items()
        },
        "engine_version": identity["packages"]["policyengine-uk"]["version"],
        "python": identity["python"],
        "packaged_bundle_manifest_sha256": identity["packaged_bundle_manifest_sha256"],
        "release_bundle": identity["release_bundle"],
        "data_bundle": identity["dataset"]["revision"],
        "dataset": {"revision": identity["dataset"]["revision"], "sha256": sha},
        "behavioural_response": "none (static)",
        "worlds": {"baseline": world},
        "diagnostics": {"baseline__full_use_hours": copy.deepcopy(world)},
    }


def _path(art):
    return Path(f"{art['variant_id']}.json")


def _other_certified():
    return next(
        v["variant_id"]
        for v in VARIANTS["variants"]
        if v["status"] == "certified" and v["variant_id"] != VARIANTS["default_variant"]
    )


@pytest.mark.parametrize("variant_id", [None, "other"])
def test_check_artifact_accepts_exactly_its_variants_pairing(variant_id):
    variant = _record(_other_certified() if variant_id else None)
    art = _synthetic(variant)
    lane.check_artifact(art, _path(art), variant)


_ZERO = "0" * 64
MUTATIONS = {
    "schema": lambda a: a.update(schema_version=1),
    "wrapper version": lambda a: a["packages"]["policyengine"].update(version="9.9.9"),
    "core RECORD": lambda a: a["packages"]["policyengine-core"].update(
        record_sha256=_ZERO
    ),
    "engine": lambda a: a.update(engine_version="0.0.1"),
    "python": lambda a: a.update(python="3.99"),
    "packaged manifest": lambda a: a.update(packaged_bundle_manifest_sha256=_ZERO),
    "release bundle": lambda a: a["release_bundle"].update(bundle_id="uk-other"),
    "variant identity": lambda a: a.update(variant_identity_sha256=_ZERO),
    "dataset": lambda a: a["dataset"].update(sha256=_ZERO),
    "data bundle": lambda a: a.update(data_bundle="another-build"),
    "runtime source": lambda a: a["worlds"]["baseline"].pop("runtime_dataset_source"),
    "digest after": lambda a: a["diagnostics"]["baseline__full_use_hours"].update(
        dataset_sha256_after=_ZERO
    ),
    "data years": lambda a: a["worlds"]["baseline"]["dataset_years"].pop(),
    "behaviour": lambda a: a.update(behavioural_response="dynamic"),
}


@pytest.mark.parametrize("what", sorted(MUTATIONS))
def test_check_artifact_refuses_any_other_pairing(what):
    variant = _record()
    art = _synthetic(variant)
    MUTATIONS[what](art)
    with pytest.raises(ValueError):
        lane.check_artifact(art, _path(art), variant)


def test_an_artifact_must_sit_under_its_own_variant_id():
    variant = _record()
    art = _synthetic(variant)
    with pytest.raises(ValueError):
        lane.check_artifact(art, Path(f"{_other_certified()}.json"), variant)


def _write(directory, *arts):
    for art in arts:
        (directory / _path(art)).write_text(json.dumps(art))
    # the construction notes live beside the artifacts and are not one
    shutil.copy(lane.CONSTRUCTION, directory / lane.CONSTRUCTION.name)


def test_every_certified_artifact_stays_and_the_newest_is_latest(tmp_path):
    older = _synthetic(
        _record(_other_certified()),
        run_id="older",
        computed_at="2026-10-22T00:00:00+00:00",
    )
    newer = _synthetic(_record(), run_id="newer")
    _write(tmp_path, newer, older)
    got = lane.load_artifacts(tmp_path)
    assert [a["run_id"] for a, _ in got] == ["older", "newer"]


def test_artifacts_must_have_distinct_runs_and_certified_variants(tmp_path):
    a = _synthetic(_record(_other_certified()), run_id="same")
    b = _synthetic(_record(), run_id="same")
    _write(tmp_path, a, b)
    with pytest.raises(ValueError, match="run_id"):
        lane.load_artifacts(tmp_path)
    index = copy.deepcopy(VARIANTS)
    for v in index["variants"]:
        if v["variant_id"] == a["variant_id"]:
            v["status"] = "retired"
    (tmp_path / "variants.json").write_text(json.dumps(index))
    b["run_id"] = "other"
    _write(tmp_path, b)
    with pytest.raises(ValueError, match="no certified variant"):
        lane.load_artifacts(tmp_path, tmp_path / "variants.json")


@pytest.mark.parametrize(
    "run_id, when, match",
    [
        ("a", "2026-10-25T00:00:00+00:00", "share a computed_at"),
        ("a", "2026-10-25T01:00:00+01:00", "not a UTC time"),
        # the same instant as b, and a time before it that sorts after it,
        # each in a UTC spelling isoformat() does not write
        ("a", "2026-10-25T00:00:00.000000+00:00", "not a UTC time"),
        ("a", "2026-10-24T23:59:59Z", "not a UTC time"),
        ("platform-grid-a", "2026-10-24T00:00:00+00:00", "reserved prefix"),
        # the view's LIKE ignores ASCII case
        ("Platform-grid-a", "2026-10-24T00:00:00+00:00", "reserved prefix"),
        ("PLATFORM-GRID-a", "2026-10-24T00:00:00+00:00", "reserved prefix"),
    ],
)
def test_each_claims_newest_run_is_unambiguous(tmp_path, run_id, when, match):
    """Each claim's latest is its newest covering run, here and in the
    database, which orders computed_at as text and prefers platform-grid
    runs within a bundle; so two runs at one time, a time not in isoformat's
    UTC form and a platform-grid run id are refused."""
    a = _synthetic(_record(_other_certified()), run_id=run_id, computed_at=when)
    b = _synthetic(_record(), run_id="b")
    _write(tmp_path, a, b)
    with pytest.raises(ValueError, match=match):
        lane.load_artifacts(tmp_path)


@settings(deadline=None)
@given(
    st.datetimes(timezones=st.just(dt.timezone.utc)),
    st.datetimes(timezones=st.just(dt.timezone.utc)),
)
def test_canonical_utc_strings_sort_as_the_times_do(a, b):
    """The premise of ordering runs by their computed_at strings: in the
    form _utc accepts, string order is time order and equal strings are
    equal times."""
    sa, sb = a.isoformat(), b.isoformat()
    lane._utc(sa, "a")
    lane._utc(sb, "b")
    assert (sa < sb) == (a < b)
    assert (sa == sb) == (a == b)


def test_every_stage_checks_the_run_history(artifact):
    """Called directly, results, diagnoses and expected refuse the histories
    load_artifacts refuses, so no path reads a tie or a duplicate run id."""
    scores, _, artifacts = lane.stage()
    path = artifacts[-1][1]
    twin = copy.deepcopy(artifact)
    twin["run_id"] = "twin"
    same_run = copy.deepcopy(artifact)
    same_run["computed_at"] = "2026-10-25T23:00:00+00:00"
    spelled = copy.deepcopy(artifact)
    spelled["computed_at"] = artifact["computed_at"].replace("+00:00", "Z")
    reserved = copy.deepcopy(artifact)
    reserved["run_id"] = "platform-grid-childcare"
    mixed = copy.deepcopy(artifact)
    mixed["run_id"] = "Platform-Grid-childcare"
    for history, match in (
        ([(artifact, path), (twin, path)], "share a computed_at"),
        ([(artifact, path), (same_run, path)], "share a run_id"),
        ([(spelled, path)], "not a UTC time"),
        ([(reserved, path)], "reserved prefix"),
        ([(mixed, path)], "reserved prefix"),
    ):
        for stage in (lane.results, lane.diagnoses, lane.expected):
            with pytest.raises(ValueError, match=match):
                stage(scores, history)
        if len(history) == 1:
            with pytest.raises(ValueError, match=match):
                lane.certified_result(scores[0], lane.load_notes(), *history[0])


@pytest.mark.parametrize(
    "run_id", ["platform-grid-childcare", "Platform-grid-childcare", "PLATFORM-GRID-x"]
)
def test_the_compute_script_refuses_a_reserved_run_id(run_id):
    compute = _module(
        "compute_uk_childcare_100k_reserved",
        REPO / "pipeline" / "compute_uk_childcare_100k.py",
    )
    assert compute.RESERVED_RUN_PREFIX == lane.RESERVED_RUN_PREFIX
    with pytest.raises(SystemExit, match="may not start with"):
        compute.main(["--run-id", run_id])


def _view_prefers(conn, run_id: str) -> bool:
    """The comparisons view's own platform-grid test, evaluated by SQLite."""
    sql = (REPO / "scorecard_db" / "db.py").read_text()
    (test,) = set(re.findall(r"p\.run_id LIKE '[^']*'", sql))
    like = test.removeprefix("p.run_id ")
    return bool(conn.execute(f"SELECT ? {like}", (run_id,)).fetchone()[0])


_CASED = st.lists(st.booleans(), min_size=14, max_size=14).map(
    lambda up: "".join(
        c.upper() if u else c for c, u in zip(lane.RESERVED_RUN_PREFIX, up)
    )
)


@settings(deadline=None)
@given(
    st.one_of(
        st.text(),
        st.tuples(_CASED, st.text()).map("".join),
        st.tuples(st.text(max_size=2), _CASED, st.text()).map("".join),
    )
)
@example("Platform-grid-childcare")
@example("platform-grİd-x")  # dotted capital I: SQLite folds ASCII only
@example("platform-grid")
def test_reserved_run_ids_are_those_the_database_view_prefers(run_id):
    """Differential: ingest's and the compute script's reserved test agree
    with SQLite evaluating the comparisons view's LIKE on every run id."""
    compute = _module(
        "compute_uk_childcare_100k_prefix",
        REPO / "pipeline" / "compute_uk_childcare_100k.py",
    )
    conn = sqlite3.connect(":memory:")
    try:
        want = _view_prefers(conn, run_id)
    finally:
        conn.close()
    assert lane.reserved_run_id(run_id) == want
    assert compute.reserved_run_id(run_id) == want


def test_the_published_run_may_not_take_the_reserved_prefix(tmp_path, monkeypatch):
    pe = tmp_path / "pe"
    pe.mkdir()
    pub = json.loads((lane.CENTAX_DIR / "pe" / "published_dashboard.json").read_text())
    lane._published()
    pub["run_id"] = "Platform-grid-dashboard"
    (pe / "published_dashboard.json").write_text(json.dumps(pub))
    monkeypatch.setattr(lane, "CENTAX_DIR", tmp_path)
    with pytest.raises(ValueError, match="reserved prefix"):
        lane._published()


def test_results_keep_an_earlier_certified_run_beside_the_latest(artifact):
    """History across variants: an earlier certified run attaches to every
    claim the latest does, and the published figure is older than both."""
    scores, _, artifacts = lane.stage()
    latest, path = artifacts[-1]
    earlier = copy.deepcopy(latest)
    earlier["run_id"] = "earlier-certified-run"
    earlier["computed_at"] = "2026-10-20T00:00:00+00:00"
    history = [(earlier, path), (latest, path)]
    out = lane.results(scores, history)
    runs = Counter(r.run_id for r in out)
    assert runs["earlier-certified-run"] == runs[latest["run_id"]] == 24
    # ingest's tally scales with the runs, so a second artifact builds
    drops = lane.stage()[1]
    diag = lane.diagnoses(scores, history)
    want = lane.expected(scores, history)
    assert lane.accounting(scores, out, diag, drops, history) == want
    assert want["results"] == 2 * 24 + 4
    one = lane.results(scores, artifacts)
    assert lane.accounting(
        scores, one, lane.diagnoses(scores, artifacts), drops, artifacts
    ) == lane.expected(scores, artifacts)
    # the published figure must stay older than every certified run
    earlier["computed_at"] = "2026-10-01T00:00:00+00:00"
    with pytest.raises(ValueError, match="older than every certified run"):
        lane.results(scores, [(earlier, path), (latest, path)])


def _wide_certified():
    """A registered certified variant other than the default whose data
    years reach 2031, the engine year of CBP's last claims (2031-32)."""
    return next(
        v
        for v in VARIANTS["variants"]
        if v["status"] == "certified"
        and v["variant_id"] != VARIANTS["default_variant"]
        and 2031 in v["data_years"]
    )


def _on_pair(art, variant, *, run_id, with_2031=False):
    """The committed run's numbers relabelled as a run on `variant` (its
    identity from the record, as _synthetic builds it), to exercise ingest's
    control flow only: they claim nothing about that engine's costs."""
    out = copy.deepcopy(art)
    label = _synthetic(variant, run_id=run_id, computed_at="2026-10-26T00:00:00+00:00")
    out.update({k: v for k, v in label.items() if k not in ("worlds", "diagnostics")})
    sha = variant["identity"]["dataset"]["sha256"]
    for group in ("worlds", "diagnostics"):
        for world in out[group].values():
            world.update(
                dataset_sha256_before=sha,
                dataset_sha256_after=sha,
                dataset_years=list(variant["data_years"]),
            )
            # as a run since the record began: no dataset values for it
            world["dataset_inputs"].setdefault(lane.CHILD_HOURS_INPUT, [])
            if with_2031 and group == "worlds":
                world["years"]["2031"] = copy.deepcopy(world["years"]["2030"])
    return out


def _in_repo(artifacts):
    # a result's construction names its artifact's path in the repo
    return [(a, lane.RESULTS_DIR / p.name) for a, p in artifacts]


def _verified_for(variant_id, *, except_ids=()):
    """The lane's notes with `variant_id` added as a checked pair to every
    pair-scoped note but `except_ids`, and a pair entry stating no diagnosis."""
    notes = copy.deepcopy(lane.load_notes())
    for kind in (lane.CENTAX, lane.CBP, "construction"):
        for a in notes[kind]:
            if "variants" in a and a["id"] not in except_ids:
                a["variants"].append(variant_id)
    notes["pairs"][variant_id] = {
        "static_because": "STATED FOR THE TEST",
        "hours_draw": None,
        "diagnosis": None,
    }
    return notes


def test_an_artifact_on_an_unverified_pair_is_refused(artifact, tmp_path):
    """The registered 2.130.1 pairs differ from 2.89.2 in mechanisms these
    notes state (the review of #207 read the pinned wheel), so ingest
    refuses a pair no note was checked on rather than give it 2.89.2's."""
    other = _on_pair(artifact, _wide_certified(), run_id="other")
    _write(tmp_path, artifact, other)
    with pytest.raises(ValueError, match="no note in this lane was verified"):
        lane.stage(results_dir=tmp_path)
    scores, _, artifacts = lane.stage()
    with pytest.raises(ValueError, match="no note in this lane was verified"):
        lane.results(scores, [*artifacts, (other, lane.RESULTS_DIR / _path(other))])
    with pytest.raises(ValueError, match="no note in this lane was verified"):
        lane.diagnoses(scores, [*artifacts, (other, lane.RESULTS_DIR / _path(other))])
    with pytest.raises(ValueError, match="no note in this lane was verified"):
        lane.expected(scores, [*artifacts, (other, lane.RESULTS_DIR / _path(other))])
    # refused even when the unverified run computes no claim's year
    idle = copy.deepcopy(other)
    for world in idle["worlds"].values():
        world["years"] = {}
    with pytest.raises(ValueError, match="no note in this lane was verified"):
        lane.results(scores, [*artifacts, (idle, lane.RESULTS_DIR / _path(idle))])


def test_notes_reach_only_the_pairs_they_were_checked_on(june, tmp_path):
    vid = _wide_certified()["variant_id"]
    other = _on_pair(june, _wide_certified(), run_id="other")
    notes = _verified_for(vid, except_ids={"pe-universal-switch-off"})
    _write(tmp_path, june, other)
    scores, _, artifacts = lane.stage(notes, results_dir=tmp_path)
    out = lane.results(scores, _in_repo(artifacts), notes)
    runs = {
        run: [r for r in out if r.run_id == run] for run in (june["run_id"], "other")
    }
    switch_off = next(
        a["text"] for a in notes["construction"] if a["id"] == "pe-universal-switch-off"
    )
    draw = notes["pairs"][VARIANTS["default_variant"]]["hours_draw"]
    assert len(runs["other"]) == len(runs[june["run_id"]]) == 22
    for r in runs["other"]:
        assert switch_off not in r.annotations
        assert not any(draw in t for t in r.annotations)
    for r in runs[june["run_id"]]:
        assert switch_off in r.annotations
        assert any(draw in t for t in r.annotations)
    # the newest pair states no diagnosis, so none is drawn from the old one
    assert lane.diagnoses(scores, _in_repo(artifacts), notes) == []
    # and the behavioural legs say why from the newest pair
    legs = [s for s in scores if s.conditions.get("component") == "intensive_margin"]
    assert legs and all(
        "STATED FOR THE TEST" in s.publication["pe_missing"] for s in legs
    )


def test_tally_and_pe_missing_follow_each_runs_computed_years(june, tmp_path):
    """Coverage, not dataset support: a run that holds 2031 among its data
    years but computes only the default years leaves CBP's 2031-32 claims
    without a value and says so; one that computes 2031 answers them. The
    tally follows, and no claim id moves across the three histories."""
    wide = _wide_certified()
    notes = _verified_for(wide["variant_id"])
    (tmp_path / "alone").mkdir()
    _write(tmp_path / "alone", june)
    histories = {"alone": lane.stage(notes, results_dir=tmp_path / "alone")}
    for name, with_2031 in (("default_years", False), ("with_2031", True)):
        (tmp_path / name).mkdir()
        other = _on_pair(june, wide, run_id="other", with_2031=with_2031)
        _write(tmp_path / name, june, other)
        histories[name] = lane.stage(notes, results_dir=tmp_path / name)
    ids = {k: [s.claim_id() for s in h[0]] for k, h in histories.items()}
    assert ids["alone"] == ids["default_years"] == ids["with_2031"]

    def last(name):
        return [
            s for s in histories[name][0] if s.source == lane.CBP and s.period == 2032
        ]

    assert len(last("alone")) == 2
    assert all(
        "outside the data years" in s.publication["pe_missing"] for s in last("alone")
    )
    for s in last("default_years"):
        assert (
            "no certified run in this lane computed it" in s.publication["pe_missing"]
        )
        assert wide["variant_id"] in s.publication["pe_missing"]
    assert all("pe_missing" not in s.publication for s in last("with_2031"))
    for name, certified in (("alone", 22), ("default_years", 44), ("with_2031", 46)):
        scores, drops, arts = histories[name]
        out = lane.results(scores, _in_repo(arts), notes)
        diag = lane.diagnoses(scores, _in_repo(arts), notes)
        got = lane.accounting(scores, out, diag, drops, arts)
        assert got == lane.expected(scores, arts, notes)
        assert got["results_by_kind"] == {
            "certified": certified,
            "published_dashboard": 4,
        }


def test_a_newer_run_that_skips_a_year_leaves_that_years_diagnosis(june, tmp_path):
    """The round-3 review's case: a newer run on a verified pair that
    computes only 2031 takes no claim's latest result in the years it skips,
    so the diagnoses of those years stay with the run that computed them."""
    wide = _wide_certified()
    notes = _verified_for(wide["variant_id"])
    other = _on_pair(june, wide, run_id="other", with_2031=True)
    for world in other["worlds"].values():
        world["years"] = {y: b for y, b in world["years"].items() if y == "2031"}
    _write(tmp_path, june, other)
    scores, drops, arts = lane.stage(notes, results_dir=tmp_path)
    arts = _in_repo(arts)
    out = lane.results(scores, arts, notes)
    diag = lane.diagnoses(scores, arts, notes)
    default = notes["pairs"][VARIANTS["default_variant"]]["diagnosis"]
    assert len(diag) == 2 and all(default in str(row) for row in diag)
    got = lane.accounting(scores, out, diag, drops, arts)
    assert got == lane.expected(scores, arts, notes)
    assert got["results_by_kind"] == {"certified": 24, "published_dashboard": 4}
    assert got["diagnoses"] == 2


_BASE_FULL = "baseline__full_use_hours"
_REFORM_FULL = "free_hours__full_use_hours"
_LIMIT_30H = "gov.dfe.extended_childcare_entitlement.income.limit"


def _override(a, world):
    return a["diagnostics"][world]["input_override"]


def _block(a, world, year="2027"):
    return a["diagnostics"][world]["years"][year]


def _periods(period, value=None):
    """Set the reform world's reform to one period (at the artifact's own
    sentinel unless a value is given)."""

    def change(a):
        d = a["diagnostics"][_REFORM_FULL]
        d["reform_dict"] = {
            k: {period: a["limit_sentinel"] if value is None else value}
            for k in d["reform_dict"]
        }

    return change


def _both(change):
    def apply(a):
        for world in (_BASE_FULL, _REFORM_FULL):
            change(a["diagnostics"][world])

    return apply


def _false_sentinel(a):
    a["limit_sentinel"] = 100_000
    _periods("2026-01-01.2035-12-31", 100_000)(a)


def _receiving_none(a):
    _block(a, _BASE_FULL)["hours_usage"]["mean_benunits_receiving_extended"] = None


# what the record must show before any text claims full use, each broken
_NOT_FULL_USE = {
    "value": lambda a: _override(a, _REFORM_FULL).update(value=17.0),
    "variable": lambda a: _override(a, _BASE_FULL).update(
        variable="childcare_expenses"
    ),
    "year not set": lambda a: _override(a, _REFORM_FULL).update(set_for_years=[2029]),
    "set after a dependent": lambda a: _override(a, _BASE_FULL)[
        "dependents_calculated_before_override"
    ].update(extended_childcare_entitlement=["2027"]),
    "read back": lambda a: _override(a, _REFORM_FULL)["post_set_weighted_mean"].update(
        {"2027": 17.0}
    ),
    "mean": lambda a: _block(a, _BASE_FULL)["hours_usage"].update(
        mean_benunits_receiving_extended=17.0
    ),
    "no override": lambda a: a["diagnostics"][_REFORM_FULL].pop("input_override"),
    "one world": lambda a: a["diagnostics"][_BASE_FULL]["years"].pop("2027"),
    "other reform": lambda a: a["diagnostics"][_REFORM_FULL].update(reform_dict={}),
    "reform not in force": _periods("2028-01-01.2035-12-31"),
    # the round-5 review's: holders, periods, sentinel and executed limits
    "an unrelated holder checked": _both(
        lambda d: d["input_override"].update(
            dependents_calculated_before_override={"unrelated": []}
        )
    ),
    "a reading holder unchecked": _both(
        lambda d: d["input_override"]["dependents_calculated_before_override"].pop(
            "extended_childcare_entitlement"
        )
    ),
    "no reform periods": lambda a: a["diagnostics"][_REFORM_FULL].update(
        reform_dict={k: {} for k in a["diagnostics"][_REFORM_FULL]["reform_dict"]}
    ),
    "reform starts after 30 April": _periods("2027-05-01.2035-12-31"),
    "reform stops before 30 April": _periods("2026-01-01.2027-04-29"),
    "invalid reform dates": _periods("2027-99-99.2035-99-99"),
    "reversed reform dates": _periods("2027-12-31.2027-01-01"),
    "overlapping periods disagree": lambda a: a["diagnostics"][_REFORM_FULL].update(
        reform_dict={
            k: {"2026-01-01.2035-12-31": 1e100, "2027-01-01.2027-12-31": 200_000}
            for k in a["diagnostics"][_REFORM_FULL]["reform_dict"]
        }
    ),
    "a false sentinel": _false_sentinel,
    "another sentinel named": lambda a: a.update(limit_sentinel=1e99),
    "an executed limit the main world did not run": lambda a: _block(a, _REFORM_FULL)[
        "limits_executed"
    ].update({_LIMIT_30H: 100_000}),
    "no executed limits": _both(lambda d: d["years"]["2027"].pop("limits_executed")),
    "no receiving mean with recipients": _receiving_none,
    # each child's own cap must be at its default of 30 too
    "child hours from the dataset": _both(
        lambda d: d["dataset_inputs"].update({lane.CHILD_HOURS_INPUT: ["2027"]})
    ),
}


def test_the_full_use_cost_rests_on_the_recorded_override(artifact):
    """The committed run's record shows full use in both diagnostic years;
    the cost is the reform world's free hours minus the baseline's."""
    for year in (2027, 2029):
        d = artifact["diagnostics"]
        want = sum(
            d[_REFORM_FULL]["years"][str(year)]["sums_gbp"][v]
            - d[_BASE_FULL]["years"][str(year)]["sums_gbp"][v]
            for v in lane.FREE_HOURS
        )
        assert lane.full_use_cost(artifact, year, _pair(artifact)) == want > 0
    assert lane.full_use_cost(artifact, 2026, _pair(artifact)) is None


@pytest.mark.parametrize("what", sorted(_NOT_FULL_USE))
def test_no_text_claims_full_use_the_record_does_not_show(artifact, what):
    """A note or diagnosis says every family is at the full 30 hours only
    when both full-use worlds record the override, set before any holder
    that reads it and read back at 30, on the main world's reform in force
    on 30 April of the year, with the main world's executed limits."""
    bad = copy.deepcopy(artifact)
    _NOT_FULL_USE[what](bad)
    with pytest.raises(ValueError, match="full use|beside the other"):
        lane.full_use_cost(bad, 2027, _pair(bad))
    with pytest.raises(ValueError, match="full use|beside the other"):
        lane.measured_notes(bad, lane.CENTAX, 2027, "fy", _pair(bad))
    scores, _, artifacts = lane.stage()
    with pytest.raises(ValueError, match="full use|beside the other"):
        lane.diagnoses(scores, [(bad, artifacts[-1][1])])


def _zero_recipients(a):
    for world in (_BASE_FULL, _REFORM_FULL):
        block = _block(a, world)
        block["hours_usage"]["mean_benunits_receiving_extended"] = None
        block["counts"]["benunits_receiving_extended"] = 0
        block["records"]["benunits_receiving_extended"] = 0


def _per_year_windows(a):
    from pipeline import compute_uk_ab2025 as ab

    d = a["diagnostics"][_REFORM_FULL]
    d["reform_dict"], _ = ab.reform_dict(
        {k: {"2027": None, "2029": None} for k in d["reform_dict"]}, years=[2027, 2029]
    )


# records the compute script can write that show full use, each kept
_TRUE_FULL_USE = {
    "per-year windows from reform_dict": _per_year_windows,
    "a one-day window on 30 April": _periods("2027-04-30.2027-04-30"),
    "overlapping periods that agree": lambda a: a["diagnostics"][_REFORM_FULL].update(
        reform_dict={
            k: {"2026-01-01.2035-12-31": 1e100, "2027-01-01.2027-12-31": 1e100}
            for k in a["diagnostics"][_REFORM_FULL]["reform_dict"]
        }
    ),
    "no benefit unit receiving": _zero_recipients,
    "child hours recorded as the default": _both(
        lambda d: d["dataset_inputs"].update({lane.CHILD_HOURS_INPUT: []})
    ),
}


CHILD_KEY = lane.CHILD_HOURS_INPUT


def test_full_use_needs_the_child_hours_shown_by_the_run_or_the_pair(june):
    """A run that predates the record of the child hours input shows full
    use only through its pair's verified statement; a run that records the
    input needs no such statement."""
    pair = _pair(june)
    assert CHILD_KEY not in june["diagnostics"][_BASE_FULL]["dataset_inputs"]
    silent = {k: v for k, v in pair.items() if k != "child_hours_input"}
    with pytest.raises(ValueError, match="child hours"):
        lane.full_use_cost(june, 2027, silent)
    recorded = copy.deepcopy(june)
    _both(lambda d: d["dataset_inputs"].update({CHILD_KEY: []}))(recorded)
    assert lane.full_use_cost(recorded, 2027, silent) == lane.full_use_cost(
        june, 2027, pair
    )


@pytest.mark.parametrize("periods, says", [([], "default of 30"), (["2027"], "own")])
def test_the_notes_state_the_child_hours_input_a_run_recorded(june, periods, says):
    """The take-up and usage note names the child hours input only when
    the run recorded it, and says where its value came from."""
    old = lane.measured_notes(june, lane.CBP, 2027, "fy", _pair(june))
    assert not any(CHILD_KEY in n for n in old)
    recorded = copy.deepcopy(june)
    recorded["worlds"]["baseline"]["dataset_inputs"][CHILD_KEY] = periods
    notes = lane.measured_notes(recorded, lane.CBP, 2027, "fy", _pair(recorded))
    (line,) = [n for n in notes if CHILD_KEY in n]
    assert f"{CHILD_KEY}, each child's own cap, is the" in line
    assert says in line and line.endswith(".")
    assert [n for n in notes if CHILD_KEY not in n] == [
        n for n in old if "Take-up and usage" not in n
    ]


class _Weightless(_StandIn):
    """A stand-in whose benefit units weigh nothing in total."""

    def calculate(self, variable, period):
        series = super().calculate(variable, period)
        if variable == "extended_childcare_entitlement":
            series.weights = np.zeros_like(series.values, dtype=float)
        return series


def test_a_population_with_no_benefit_unit_weight_is_refused():
    """The round-8 review's boundary: every share and mean year_block
    writes divides by the benefit units' total weight, so a world where it
    is zero stops the run instead of writing nan."""
    compute = _module(
        "compute_uk_childcare_100k_weightless",
        REPO / "pipeline" / "compute_uk_childcare_100k.py",
    )
    sim = _Weightless(SimpleNamespace(calls=[], hours=[]), None, [2027], Path("w.h5"))
    with pytest.raises(SystemExit, match="benefit-unit weights sum to 0"):
        compute.year_block(sim, 2027)


@pytest.mark.parametrize("what", sorted(_TRUE_FULL_USE))
def test_the_full_use_cost_keeps_every_true_record_shape(artifact, what):
    """The check refuses only what the record does not show: a reform
    window each year, a window that covers just the parameter date,
    overlapping periods that set one value, and no benefit unit receiving
    the offer (year_block then writes no receiving mean) all show full use."""
    good = copy.deepcopy(artifact)
    _TRUE_FULL_USE[what](good)
    assert lane.full_use_cost(good, 2027, _pair(good)) == lane.full_use_cost(
        artifact, 2027, _pair(artifact)
    )


def _current_law(a, year=2027):
    return a["worlds"]["baseline"]["years"][str(year)]


def test_no_family_receiving_under_current_law_is_stated_not_formatted(artifact):
    """The round-6 review's robustness case. year_block itself, on a
    stand-in where no benefit unit gets the extended hours, writes no
    receiving mean and no receiving records; ingest then says so in the
    note and the diagnosis instead of formatting a mean it does not have."""
    compute = _module(
        "compute_uk_childcare_100k_no_recipients",
        REPO / "pipeline" / "compute_uk_childcare_100k.py",
    )
    run = SimpleNamespace(calls=[], hours=[], reforms=[])
    sim = _StandIn(run, None, [2027], Path("stand-in.h5"))
    for v in (
        "extended_childcare_entitlement",
        "is_child_receiving_extended_childcare",
    ):
        sim.set_input(v, 2027, np.zeros(len(_StandIn.DRAWN)))
    made = compute.year_block(sim, 2027)
    assert made["hours_usage"]["mean_benunits_receiving_extended"] is None
    assert made["records"]["benunits_receiving_extended"] == 0
    assert made["counts"]["benunits_receiving_extended"] == 0
    none = copy.deepcopy(artifact)
    for key in ("hours_usage", "counts", "records"):
        _current_law(none)[key] = made[key]
    assert lane.receiving_hours(none, 2027) is None
    stated = "no family receives the extended hours under current law in 2027-28"
    notes = lane.measured_notes(none, lane.CENTAX, 2027, "2027-28", _pair(none))
    assert sum(stated in n for n in notes) == 1
    assert not any("weekly hours under current law" in n for n in notes)
    scores, _, artifacts = lane.stage()
    rows = lane.diagnoses(scores, [(none, artifacts[-1][1])])
    assert sum("no family receives the extended hours" in str(r) for r in rows) == 1
    assert sum("weighted mean of" in str(r) for r in rows) == len(rows) - 1


class _UnweightedReceivers(_StandIn):
    """A stand-in whose benefit units given the extended hours all carry
    zero weight, while one that is not given them carries weight."""

    def calculate(self, variable, period):
        series = super().calculate(variable, period)
        if variable == "extended_childcare_entitlement":
            series.weights = np.where(series.values > 0, 0.0, 1.0)
        return series


def test_receiving_records_with_no_receiving_weight_are_stated_not_nan(artifact):
    """The round-7 review's producer boundary. Records that receive the
    offer but weigh nothing in total give year_block no mean (None, not
    0/0 = nan), and ingest, keyed on the weighted count, says no family
    receives the offer."""
    compute = _module(
        "compute_uk_childcare_100k_unweighted_receivers",
        REPO / "pipeline" / "compute_uk_childcare_100k.py",
    )
    sim = _UnweightedReceivers(
        SimpleNamespace(calls=[], hours=[]), None, [2027], Path("stand-in.h5")
    )
    made = compute.year_block(sim, 2027)
    assert made["records"]["benunits_receiving_extended"] == 2
    assert made["counts"]["benunits_receiving_extended"] == 0
    assert made["hours_usage"]["mean_benunits_receiving_extended"] is None
    none = copy.deepcopy(artifact)
    for key in ("hours_usage", "counts", "records"):
        _current_law(none)[key] = made[key]
    assert lane.receiving_hours(none, 2027) is None
    notes = lane.measured_notes(none, lane.CENTAX, 2027, "2027-28", _pair(none))
    stated = "no family receives the extended hours under current law in 2027-28"
    assert sum(stated in n for n in notes) == 1
    assert not any("nan" in n for n in notes)


@pytest.mark.parametrize(
    "mean, weight",
    [
        (None, "kept"),
        (15.3, 0),
        (float("nan"), "kept"),
        (float("inf"), "kept"),
        (15.3, float("nan")),
        (None, float("nan")),
        (15.3, "missing"),
        (None, "missing"),
        (15.3, -1.0),
        ("15.3", "kept"),
        (True, "kept"),
        (15.3, True),
    ],
    ids=str,
)
def test_a_receiving_mean_must_agree_with_the_receiving_weight(artifact, mean, weight):
    """year_block writes no mean exactly when no weight receives the offer,
    so ingest refuses a mean without receiving weight, receiving weight
    without a mean, and any mean or weight that is not a finite number."""
    bad = copy.deepcopy(artifact)
    block = _current_law(bad)
    block["hours_usage"]["mean_benunits_receiving_extended"] = mean
    if weight == "missing":
        del block["counts"]["benunits_receiving_extended"]
    elif weight != "kept":
        block["counts"]["benunits_receiving_extended"] = weight
    with pytest.raises(ValueError, match="receiving-hours mean"):
        lane.receiving_hours(bad, 2027)
    with pytest.raises(ValueError, match="receiving-hours mean"):
        lane.measured_notes(bad, lane.CENTAX, 2027, "fy", _pair(bad))


def test_the_full_use_check_reads_the_compute_scripts_own_constants(
    artifact, monkeypatch
):
    """Differential: the sentinel, limits, hours and the holders checked
    before the override are the compute script's, and the holders are read
    off a stand-in run of set_full_use itself."""
    from pipeline import compute_uk_ab2025 as ab

    compute = _module(
        "compute_uk_childcare_100k_constants",
        REPO / "pipeline" / "compute_uk_childcare_100k.py",
    )
    assert lane.NO_LIMIT == ab.NO_LIMIT == artifact["limit_sentinel"]
    assert lane.LIMITS == compute.LIMITS
    assert (lane.HOURS_USAGE_INPUT, lane.FULL_USE_HOURS) == (
        compute.HOURS_USAGE,
        compute.FULL_USE_HOURS,
    )
    sim = _StandIn(SimpleNamespace(calls=[], hours=[]), None, [2027], "x")
    checked = compute.set_full_use(sim, [2027])["dependents_calculated_before_override"]
    assert sorted(checked) == sorted(lane.FULL_USE_DEPENDENTS)


def _ingest_isolated(tmp_path, monkeypatch, notes, staged) -> sqlite3.Connection:
    """The lane's real ingest into an empty database, with this history and
    these notes, and its lane feed written beside it, not into data/."""
    from scorecard_db import ingest_harvest

    scores, drops, artifacts = staged
    monkeypatch.setattr(lane, "stage", lambda n=None: (scores, drops, artifacts))
    monkeypatch.setattr(lane, "load_notes", lambda: notes)
    feed = tmp_path / "lanes.json"
    shutil.copy(REPO / "data" / "lanes.json", feed)
    sync = ingest_harvest.sync_lane_feed
    monkeypatch.setattr(
        ingest_harvest,
        "sync_lane_feed",
        lambda db, path, updated, **kw: sync(db, feed, updated, **kw),
    )
    db = tmp_path / "lane.db"
    lane.ingest(db)
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    return conn


def test_the_database_shows_each_claims_newest_covering_run(
    june, tmp_path, monkeypatch
):
    """Differential: on a history of three runs, two of them on pairs that
    share a data bundle and the newest computing only 2027, the comparisons
    view's latest result for each claim is the run _covering picks, and
    the diagnosis on it is that run's pair's."""
    default = VARIANTS["default_variant"]
    shared = Counter(
        v["identity"]["dataset"]["revision"]
        for v in VARIANTS["variants"]
        if v["status"] == "certified" and v["variant_id"] != default
    )
    bundle = next(b for b, n in shared.items() if n >= 2)
    v1, v2 = [
        v
        for v in VARIANTS["variants"]
        if v["status"] == "certified"
        and v["variant_id"] != default
        and v["identity"]["dataset"]["revision"] == bundle
    ][:2]
    notes = _verified_for(v1["variant_id"])
    for kind in (lane.CENTAX, lane.CBP, "construction"):
        for a in notes[kind]:
            if "variants" in a:
                a["variants"].append(v2["variant_id"])
    notes["pairs"][v1["variant_id"]].update(
        diagnosis="FIRST SHARED-BUNDLE PAIR", diagnosis_url="https://example.test/gap"
    )
    notes["pairs"][v2["variant_id"]] = {
        **notes["pairs"][v1["variant_id"]],
        "diagnosis": "SECOND SHARED-BUNDLE PAIR",
    }
    older = _on_pair(june, v1, run_id="shared-older")
    newer = _on_pair(june, v2, run_id="shared-newer")
    newer["computed_at"] = "2026-10-27T00:00:00+00:00"
    for world in newer["worlds"].values():
        world["years"] = {"2027": world["years"]["2027"]}
    (tmp_path / "in").mkdir()
    _write(tmp_path / "in", june, older, newer)
    scores, drops, arts = lane.stage(notes, results_dir=tmp_path / "in")
    arts = _in_repo(arts)
    conn = _ingest_isolated(tmp_path, monkeypatch, notes, (scores, drops, arts))
    shown = {
        row["claim_id"]: row
        for row in conn.execute(
            "SELECT c.claim_id, r.run_id, c.diagnosis_rationale FROM comparisons c "
            "JOIN pe_results r ON r.claim_id = c.claim_id "
            "AND r.computed_at = c.computed_at"
        )
    }
    picked = Counter()
    for s in scores:
        run = lane._covering(s, arts)
        attached = not (
            s.source == lane.CENTAX
            and s.conditions["component"] not in lane.CENTAX_ATTACHED
        )
        if run is None or not attached:
            assert s.claim_id() not in shown or shown[s.claim_id()]["run_id"] not in {
                a["run_id"] for a, _ in arts
            }
            continue
        row = shown[s.claim_id()]
        assert row["run_id"] == run["run_id"], s.claim_id()
        picked[run["run_id"]] += 1
        pair = notes["pairs"][run["variant_id"]]
        if lane._diagnosed(s, run, pair):
            assert pair["diagnosis"] in row["diagnosis_rationale"]
        else:
            assert row["diagnosis_rationale"] is None
    # the newest run is latest only in the year it computed
    assert set(picked) == {"shared-older", "shared-newer"}
    diagnosed = [
        r["diagnosis_rationale"] for r in shown.values() if r["diagnosis_rationale"]
    ]
    assert len(diagnosed) == 2
    for marker in ("FIRST SHARED-BUNDLE PAIR", "SECOND SHARED-BUNDLE PAIR"):
        assert sum(marker in t for t in diagnosed) == 1


def test_a_note_on_the_engine_or_a_run_names_its_pairs(tmp_path):
    spec = json.loads(lane.CONSTRUCTION.read_text())
    spec["annotations"][0].pop("variants")
    path = tmp_path / "construction_annotations.json"
    path.write_text(json.dumps(spec))
    with pytest.raises(ValueError, match="variants"):
        lane._spec(path)
    # #228's pass: each engine- or run-based note names the pairs it holds on,
    # and the two that failed at 2.132.6 hand over to their replacements
    only = {
        "pe-universal-switch-off": [JUNE],
        "cbp-full-utilisation": [JUNE],
        "pe-universal-hours-kept": [PAIR_6110],
        "cbp-full-utilisation-child-caps": [PAIR_6110],
        "centax-live-accounts-above-limit": [PAIR_6110],
    }
    for kind in (lane.CENTAX, lane.CBP, "construction"):
        for a in lane.load_notes()[kind]:
            if "variants" in a:
                assert a["variants"] == only.get(a["id"], [JUNE, PAIR_6110]), a["id"]


@settings(deadline=None)
@given(value=st.integers(-(10**10), 10**10), printed=st.text(min_size=1, max_size=12))
def test_claim_ids_ignore_the_value_its_printed_form_and_pe_coverage(value, printed):
    """A corrected extraction (value or formatting) keeps every claim id, and
    so does any reason PolicyEngine has no value (it depends on the runs), so
    links and history stay attached."""
    centax = json.loads(
        (REPO / "data/externals/centax-childcare-100k.json").read_text()
    )
    cbp = json.loads((REPO / "data/externals/cbp-rates-and-wrongs.json").read_text())
    edit = {"value": value, "value_verbatim": printed}
    for build, rows in (
        (lane._centax_claim, [r for r in centax if r["metric"] == "revenue_change"]),
        (lane._cbp_claim, [r for r in cbp if r["policy"] == "abolish_cliff"]),
    ):
        row = rows[0]
        assert build({**row, **edit}, printed).claim_id() == build(row).claim_id()


def test_adapter_rows_carry_the_tidy_core():
    for adapter_id, source in (
        ("centax-childcare-100k", lane.CENTAX),
        ("cbp-rates-and-wrongs", lane.CBP),
    ):
        rows = json.loads((REPO / f"data/externals/{adapter_id}.json").read_text())
        for r in rows:
            assert lane._CORE_FIELDS <= set(r)
            assert (r["geography"], r["program"], r["subgroup"]) == (
                "England",
                lane.PROGRAMS[source],
                None,
            )


# --- claims, statuses, annotations -------------------------------------------


def test_claims_drops_relationships_and_conditions():
    scores, drops, _ = lane.stage()
    assert Counter(s.source for s in scores) == {lane.CENTAX: 24, lane.CBP: 12}
    assert drops == {"cbp_taper_rows": 60, "centax_bunching_counts": 12}
    for s in scores:
        assert s.calibration_relationship == CR.HELD_OUT
        assert s.reform.framework == "policy_ref"
        assert set(s.conditions) <= STANDARD_CONDITIONS
        assert s.publication["publish_without_result"] is True
        assert s.conditions["measure_key"] == lane.MEASURES[s.source]
        # the printed value is provenance, outside the claim id
        assert "value_verbatim" not in s.conditions
        assert s.publication["value_verbatim"]
        # why a claim has no value depends on the runs, so it is outside the id
        assert "pe_missing" not in s.conditions
    assert uk_relationship(lane.CBP, None)[0] == CR.HELD_OUT
    assert len({s.claim_id() for s in scores}) == len(scores)


def _all_facets(source):
    if source == lane.CENTAX:
        return [
            {"component": c, "scenario": sc, "period": p}
            for c, sc, p in product(
                lane.CENTAX_ATTACHED, ("central", "high_cost", "low_cost"), (2028, 2030)
            )
        ]
    return [
        {"model": m, "period": p} for m, p in product(CBP_ABOLISH, range(2027, 2032))
    ]


def test_every_attached_result_has_exactly_one_stated_status():
    """Exhaustive over the attached facets: no result's status is a
    default, and the statuses are the ones the lane promises."""
    scores, _, _ = lane.stage()
    specs = {
        lane.CENTAX: lane._spec(CENTAX_SRC / "annotations.json"),
        lane.CBP: lane._spec(CBP_SRC / "annotations.json"),
    }
    seen = Counter()
    for s in scores:
        if (
            s.source == lane.CENTAX
            and s.conditions["component"] not in lane.CENTAX_ATTACHED
        ):
            continue
        kinds = ["certified"]
        if s.source == lane.CENTAX and s.conditions["scenario"] == "central":
            kinds.append("published_dashboard")
        for kind in kinds:
            variant = VARIANTS["default_variant"] if kind == "certified" else None
            _, status = lane.match_annotations(s, kind, specs[s.source], variant)
            key = (s.source, s.conditions.get("component"), kind)
            seen[(key, status.value)] += 1
    assert seen == {
        ((lane.CENTAX, "static_cost", "certified"), "comparable"): 6,
        ((lane.CENTAX, "net_fiscal_cost", "certified"), "concept_mismatch"): 6,
        ((lane.CENTAX, "static_cost", "published_dashboard"), "constructed"): 2,
        (
            (lane.CENTAX, "net_fiscal_cost", "published_dashboard"),
            "concept_mismatch",
        ): 2,
        ((lane.CBP, None, "certified"), "concept_mismatch"): 12,
    }


def test_every_annotation_has_a_basis_and_cites_files_that_exist():
    for path in (
        CENTAX_SRC / "annotations.json",
        CBP_SRC / "annotations.json",
        REPO / "results/uk/childcare_100k/construction_annotations.json",
    ):
        for a in lane._spec(path):
            assert a["basis"]
            for token in a["basis"].replace(";", " ").split():
                if token.startswith(("raw/", "pe/")):
                    assert (path.parent / token.rstrip(",")).exists(), (a["id"], token)
                if token.startswith("sources/"):
                    assert (REPO / token.rstrip(",")).exists(), (a["id"], token)


# --- the built database --------------------------------------------------------


def _rows(sql, *args):
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    out = conn.execute(sql, args).fetchall()
    conn.close()
    return out


def test_built_db_lane_counts_and_latest_result_is_the_certified_run():
    rows = _rows(
        "SELECT * FROM comparisons WHERE json_extract(publication, '$.registry') = ?",
        lane.REGISTRY_MARK,
    )
    assert len(rows) == 36
    computed = [r for r in rows if r["pe_value"] is not None]
    assert len(computed) == 24
    newest = lane.run_records()[PAIR_6110]["identity"]["dataset"]["revision"]
    assert {r["data_bundle"] for r in computed} == {newest}
    assert {r["engine_version"] for r in computed} == {"2.132.6"}
    lanes = _rows("SELECT * FROM lanes WHERE lane = ?", lane.LANE_ID)
    assert [r["stage"] for r in lanes] == ["computed"]
    # the note counts claims on the latest run, not results across the history
    assert lanes[0]["detail"].startswith("24 of 36 claims computed")


def test_published_dashboard_miss_stays_in_the_history():
    rows = _rows(
        "SELECT s.period, json_extract(s.conditions, '$.component') AS comp,"
        " r.computed_value, r.status, r.engine_version, r.data_bundle, r.computed_at"
        " FROM pe_results r JOIN external_scores s USING (claim_id)"
        " WHERE s.source = 'centax' AND r.run_id = 'uk-childcare-100k-dashboard-1b57118'"
        " ORDER BY s.period, comp"
    )
    got = {(r["period"], r["comp"]): (r["computed_value"], r["status"]) for r in rows}
    assert got == {
        (2028, "net_fiscal_cost"): (-434_000_000.0, "concept_mismatch"),
        (2028, "static_cost"): (-434_000_000.0, "constructed"),
        (2030, "net_fiscal_cost"): (-505_000_000.0, "concept_mismatch"),
        (2030, "static_cost"): (-505_000_000.0, "constructed"),
    }
    assert {r["engine_version"] for r in rows} == {"2.102.3"}
    assert {r["data_bundle"] for r in rows} == {
        "microcosm-uk-2024-25-national-20261002T230158Z-5c6b3f68"
    }
    # history, not the latest: the lane's certified run is newer
    certified = _rows(
        "SELECT MIN(computed_at) AS t FROM pe_results WHERE run_id = ?",
        lane.load_artifact()[0]["run_id"],
    )[0]["t"]
    assert max(r["computed_at"] for r in rows) < certified


def test_the_published_row_says_when_it_was_live_and_what_followed():
    """policyengine.org served the figure from 12 to 21 October 2026; what
    the dashboard has served since is stated on the row, never a value."""
    pub = lane._published()
    assert (pub["live"]["from"], pub["live"]["until"]) == ("2026-10-12", "2026-10-21")
    assert pub["after"]["attached"] is False
    scores, _, artifacts = lane.stage()
    published = [
        r for r in lane.results(scores, artifacts) if r.run_id == pub["run_id"]
    ]
    assert len(published) == 4
    for r in published:
        year = str(next(s for s in scores if s.claim_id() == r.claim_id).period - 1)
        after = f"£{pub['after']['thirty_hours_gbp_bn'][year]:.3f}bn in this year"
        assert any(after in t for t in r.annotations)
        assert any("from 2026-10-12 to 2026-10-21" in t for t in r.annotations)
    after_m = sorted(
        {-round(v * 1e3) for v in pub["after"]["thirty_hours_gbp_bn"].values()}
    )
    marks = ",".join("?" * len(after_m))
    assert not _rows(
        "SELECT 1 FROM pe_results r JOIN external_scores s USING (claim_id)"
        f" WHERE s.source = 'centax' AND ROUND(r.computed_value / 1e6) IN ({marks})",
        *after_m,
    )


def test_central_static_rows_carry_the_latest_pairs_diagnosis():
    rows = _rows(
        "SELECT period, diagnosis_class, action_link, diagnosis_rationale"
        " FROM comparisons WHERE source = 'centax'"
        " AND json_extract(conditions, '$.component') = 'static_cost'"
        " AND diagnosis_class IS NOT NULL ORDER BY period"
    )
    assert [(r["period"], r["diagnosis_class"]) for r in rows] == [
        (2028, "pe_gap"),
        (2030, "pe_gap"),
    ]
    assert {r["action_link"] for r in rows} == {
        "https://github.com/PolicyEngine/microcosm/pull/1338"
    }
    assert "28.3 of 30 weekly hours" in rows[0]["diagnosis_rationale"]
    assert "26% above CenTax's" in rows[0]["diagnosis_rationale"]
    assert "25% above CenTax's" in rows[1]["diagnosis_rationale"]


def test_the_diagnosis_and_readme_state_the_runs_own_split(pair_6110):
    """Differential: the figures the pair's diagnosis and the README give in
    prose equal the run's, including the universal change's share of the excess
    over CenTax."""
    text = _pair(pair_6110)["diagnosis"]
    readme = (CENTAX_SRC / "README.md").read_text()
    centax = {2027: 0.80, 2029: 0.98}
    extended, universal, share = {}, {}, {}
    for year, cost in centax.items():
        y = str(year)
        extended[year] = (
            _d(pair_6110, "free_hours", y, "extended_childcare_entitlement") / 1e9
        )
        universal[year] = (
            _d(pair_6110, "free_hours", y, "universal_childcare_entitlement") / 1e9
        )
        total = -lane.counterpart(pair_6110, lane.CENTAX, year) / 1e9
        assert total == pytest.approx(extended[year] + universal[year], abs=1e-6)
        share[year] = universal[year] / (total - cost) * 100
        assert f"{total:.3f}" in readme
    assert (
        f"£{universal[2027]:.3f}bn in 2027-28 and £{universal[2029]:.3f}bn in 2029-30"
        in text
    )
    assert f"£{extended[2027]:.3f}bn and £{extended[2029]:.3f}bn" in text
    assert (
        f"{share[2027]:.0f}% of the excess over CenTax in 2027-28 and "
        f"{share[2029]:.0f}% in 2029-30" in text
    )
    assert (
        f"{share[2027]:.0f}% of the excess in 2027-28 and {share[2029]:.0f}%" in readme
    )
    assert (
        f"{(extended[2027] / centax[2027] - 1) * 100:.0f}% and "
        f"{(extended[2029] / centax[2029] - 1) * 100:.0f}% above" in text
    )
    for year in centax:
        for figure in (extended[year], universal[year]):
            assert f"{figure:.3f}" in readme
        full = lane.full_use_cost(pair_6110, year, _pair(pair_6110))
        assert f"£{full / 1e9:.3f}bn" in readme


def test_no_reform_estimate_is_a_calibration_target():
    """The 2026-08-02 rulings: another model's reform estimate is never a
    calibration target. never_calibrate() is keyed on metric (the poverty
    family), so this checks the rule on the built DB for every source:
    a claim that scores any world other than the baseline (a policy_ref
    reform, a PolicyEngine reform or an input-override counterfactual) is
    held out, never consumed_as_target or seed_source."""
    rows = _rows(
        "SELECT source, calibration_relationship, COUNT(*) AS n FROM external_scores"
        " WHERE json_extract(reform_json, '$.framework') != 'baseline'"
        " AND calibration_relationship != 'held_out'"
        " GROUP BY source, calibration_relationship"
    )
    assert [tuple(r) for r in rows] == []
    lane_rows = _rows(
        "SELECT DISTINCT json_extract(reform_json, '$.framework') AS fw,"
        " calibration_relationship AS cr FROM external_scores"
        " WHERE json_extract(publication, '$.registry') = ?",
        lane.REGISTRY_MARK,
    )
    assert [tuple(r) for r in lane_rows] == [("policy_ref", "held_out")]


def test_exported_feed_rows_state_the_lane_signs_and_history():
    """The deployed feed is what a reader sees: CenTax rows point the same
    way as PolicyEngine's; CBP states no sign rule, so its rows are
    unknown; the central static rows carry every result, the published
    figure first and the newest certified run as the latest."""
    feed = json.loads((REPO / "data" / "populations.json").read_text())
    rows = [
        r
        for r in feed["rows"]
        if r["conditions"].get("measure_key") in set(lane.MEASURES.values())
    ]
    assert len(rows) == 36
    got = Counter(
        (r["source"], r["sign_relative_to_pe"], r["sign_basis"]) for r in rows
    )
    assert got == {
        (lane.CENTAX, "same", "stated:exchequer:same"): 24,
        (lane.CBP, "unknown", "no_stated_convention"): 12,
    }
    central = [
        r
        for r in rows
        if r["conditions"].get("scenario") == "central"
        and r["conditions"].get("component") == "static_cost"
    ]
    assert len(central) == 2
    for r in central:
        assert [x["engine_version"] for x in r["results"]] == [
            "2.102.3",
            "2.89.2",
            "2.132.6",
        ]
        assert (
            r["latest"]["data_bundle"]
            == lane.run_records()[PAIR_6110]["identity"]["dataset"]["revision"]
        )
        assert r["latest"]["status_effective"] == "comparable"
        assert r["results"][0]["status_effective"] == "constructed"
    unscored = [r for r in rows if not r["results"]]
    # the 12 CenTax margins; #228's run computes CBP's two 2031-32 cells
    assert len(unscored) == 12
    assert {r["source"] for r in unscored} == {lane.CENTAX}
    assert all(r["conditions"].get("pe_missing") for r in unscored)
