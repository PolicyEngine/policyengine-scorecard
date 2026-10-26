"""The £100,000 childcare limit costings (lane uk-childcare-100k): CenTax's
Table 4.2 and the Centre for British Progress appendix are exactly what the
adapters derive from the vendored PDFs; the QC catches broken tables; the
certified-pair artifact ran on exactly its variant's pairing and moves only
the childcare heads, in England; every result's status is one stated
annotation; every certified run and the published dashboard figure stay in
the history; and a reform estimate is never a calibration target."""

import ast
import copy
import datetime as dt
import hashlib
import importlib.util
import json
import shutil
import sqlite3
import subprocess
from collections import Counter
from itertools import product
from pathlib import Path

import pytest
from hypothesis import given
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
    # a unique module name: several lanes ship an adapter.py
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
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


@given(st.integers(min_value=-99_999, max_value=99_999))
def test_money_cells_round_trip(value):
    a = _module("centax_childcare_adapter_r", CENTAX_SRC / "adapter.py")
    cell = f"{'+' if value >= 0 else '-'}{abs(value):,}m"
    assert a._gbp_m(cell) == value


# --- the certified-pair artifact ---------------------------------------------


def test_artifact_ran_on_the_certified_bundle_without_behaviour(artifact):
    assert artifact["data_bundle"] == CERTIFIED["revision"]
    assert artifact["dataset"]["sha256"] == CERTIFIED["sha256"]
    assert artifact["engine_version"] == "2.89.2"
    assert artifact["behavioural_response"] == "none (static)"
    for world in (*artifact["worlds"].values(), *artifact["diagnostics"].values()):
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


def test_removing_the_limit_costs_money_and_switches_universal_hours_off(artifact):
    for year in artifact["worlds"]["free_hours"]["years"]:
        assert lane.counterpart(artifact, lane.CENTAX, int(year)) < 0
        assert _d(artifact, "free_hours", year, "extended_childcare_entitlement") > 0
        assert _d(artifact, "free_hours", year, "universal_childcare_entitlement") < 0


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
        lane.measured_notes(bad, lane.CENTAX, int(year), "fy", {})


def test_artifact_records_the_inputs_and_metadata_it_read(artifact):
    compute = _module(
        "compute_uk_childcare_100k", REPO / "pipeline" / "compute_uk_childcare_100k.py"
    )
    assert set(artifact["variable_metadata"]) == set(compute.METADATA)
    for group in ("worlds", "diagnostics"):
        for world in artifact[group].values():
            assert set(world["dataset_inputs"]) == set(compute.DATASET_INPUTS)
            for block in world["years"].values():
                assert set(block["take_up"]) == set(compute.TAKE_UP)
                assert all(0 <= x <= 1 for x in block["take_up"].values())


_COMPS = (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)
_SCOPES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef, *_COMPS)


def _binds(node, name: str) -> bool:
    """Does this node bind `name` in the scope it sits in?"""
    if isinstance(node, ast.Name):
        return node.id == name and isinstance(node.ctx, ast.Store | ast.Del)
    if isinstance(node, ast.arg):
        return node.arg == name
    if isinstance(node, ast.alias):
        return (node.asname or node.name).split(".")[0] == name
    if isinstance(node, ast.Global | ast.Nonlocal):
        return name in node.names
    if isinstance(node, ast.ExceptHandler | ast.MatchAs | ast.MatchStar):
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


def _calculated(path: Path, compute) -> set[str]:
    """Every name the source passes to sim.calculate, read as Python scopes
    read it. A name must be a literal, or bound exactly once on the way out
    from the call: by the plain target of a loop or comprehension around the
    call, over a tuple display or a module tuple; or nowhere, a module
    string constant. Any other binding (an assignment, a second loop, a
    rebinding generator, an argument, a tuple target) fails, so an unread
    name cannot pass unnoticed."""
    tree = ast.parse(path.read_text())
    parents = {
        child: node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)
    }

    def scopes(node):
        while node in parents:
            node = parents[node]
            if isinstance(node, _SCOPES):
                yield node

    def module_value(name: ast.Name):
        for scope in scopes(name):
            if _stores(scope, name.id):
                raise AssertionError(
                    f"{name.id!r} is rebound before line {name.lineno}"
                )
        found = _stores(tree, name.id)
        if len(found) != 1 or not isinstance(
            parents[found[0]], ast.Assign | ast.AnnAssign
        ):
            raise AssertionError(
                f"{name.id!r} is not one plain module assignment ({len(found)} bindings)"
            )
        return getattr(compute, name.id)

    def values(expr) -> list:
        if isinstance(expr, ast.Constant):
            return [expr.value]
        if isinstance(expr, ast.Name):
            value = module_value(expr)
            assert isinstance(value, tuple), expr.id
            return list(value)
        if isinstance(expr, ast.Tuple | ast.List):
            out = []
            for e in expr.elts:
                if isinstance(e, ast.Starred):
                    out += values(e.value)
                elif isinstance(e, ast.Name):
                    value = module_value(e)
                    assert isinstance(value, str), e.id
                    out.append(value)
                else:
                    out += values(e)
            return out
        raise AssertionError(f"unresolved loop iterable {ast.dump(expr)}")

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
                raise AssertionError(
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
            raise AssertionError(
                f"{name.id!r} at line {name.lineno} is bound by "
                f"{type(target).__name__}, not a loop over known names"
            )
        value = module_value(name)
        assert isinstance(value, str), name.id
        return [value]

    calculated = set()
    for node in ast.walk(tree):
        if not (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "calculate"
        ):
            continue
        arg = node.args[0]
        if isinstance(arg, ast.Constant):
            calculated.add(arg.value)
        elif isinstance(arg, ast.Name):
            calculated |= set(resolve(arg))
        else:
            raise TypeError(f"unresolved calculate argument {ast.dump(arg)}")
    return calculated


def test_every_variable_the_run_calculates_has_its_metadata_recorded():
    """The pe_meta contract, read off the source: each sim.calculate name
    is in METADATA, with each loop variable read in its own scope."""
    path = REPO / "pipeline" / "compute_uk_childcare_100k.py"
    compute = _module("compute_uk_childcare_100k_src", path)
    calculated = _calculated(path, compute)
    # both reused loop names resolve to their own tuples
    assert set(compute.SUMMED) | set(compute.TAKE_UP) <= calculated
    assert {
        "is_child",
        "is_child_receiving_extended_childcare",
        "country",
    } <= calculated
    assert calculated <= set(compute.METADATA)


def test_the_metadata_scan_catches_a_summed_variable_left_out():
    """The mutation the review of #207 ran: drop the two SUMMED-only
    variables from METADATA and the contract must fail."""
    path = REPO / "pipeline" / "compute_uk_childcare_100k.py"
    compute = _module("compute_uk_childcare_100k_src_mut", path)
    pruned = set(compute.METADATA) - {"gov_spending", "gov_tax"}
    assert not _calculated(path, compute) <= pruned


_UNREAD = '"employment_income"'


@pytest.mark.parametrize(
    "anchor, mutant",
    [
        # the round-3 review's two mutants: a rebinding generator, and an
        # assignment inside the loop
        (
            "for v in SUMMED}",
            f"for v in SUMMED for v in ({_UNREAD},)}}",
        ),
        (
            "    for v in HEADS:\n",
            f"    for v in HEADS:\n        v = {_UNREAD}\n",
        ),
        # a module tuple shadowed in the function that reads it
        (
            '    """Weighted sums and counts for one world and year (microdf weights)."""\n',
            (
                '    """Weighted sums and counts for one world and year (microdf weights)."""\n'
                f"    SUMMED = ({_UNREAD},)\n"
            ),
        ),
        # a module constant bound twice
        (
            'HOURS_USAGE = "maximum_extended_childcare_hours_usage"\n',
            (
                'HOURS_USAGE = "maximum_extended_childcare_hours_usage"\n'
                f"HOURS_USAGE = {_UNREAD}\n"
            ),
        ),
        # a loop the scan cannot read
        ("for v in SUMMED}", "for v, _ in zip(SUMMED, SUMMED)}"),
    ],
)
def test_the_metadata_scan_refuses_a_rebound_name(tmp_path, anchor, mutant):
    """Each mutant calculates a name the scan cannot vouch for; the scan
    must fail rather than read the name's old binding."""
    path = REPO / "pipeline" / "compute_uk_childcare_100k.py"
    compute = _module("compute_uk_childcare_100k_src_rebind", path)
    source = path.read_text()
    assert source.count(anchor) == 1, anchor
    mutated = tmp_path / "compute_uk_childcare_100k.py"
    mutated.write_text(source.replace(anchor, mutant))
    with pytest.raises((AssertionError, TypeError)):
        _calculated(mutated, compute)


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
    assert runs["earlier-certified-run"] == runs[latest["run_id"]] == 22
    # ingest's tally scales with the runs, so a second artifact builds
    drops = lane.stage()[1]
    diag = lane.diagnoses(scores, history)
    want = lane.expected(scores, history)
    assert lane.accounting(scores, out, diag, drops, history) == want
    assert want["results"] == 2 * 22 + 4
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


def test_notes_reach_only_the_pairs_they_were_checked_on(artifact, tmp_path):
    vid = _wide_certified()["variant_id"]
    other = _on_pair(artifact, _wide_certified(), run_id="other")
    notes = _verified_for(vid, except_ids={"pe-universal-switch-off"})
    _write(tmp_path, artifact, other)
    scores, _, artifacts = lane.stage(notes, results_dir=tmp_path)
    out = lane.results(scores, _in_repo(artifacts), notes)
    runs = {
        run: [r for r in out if r.run_id == run]
        for run in (artifact["run_id"], "other")
    }
    switch_off = next(
        a["text"] for a in notes["construction"] if a["id"] == "pe-universal-switch-off"
    )
    draw = notes["pairs"][VARIANTS["default_variant"]]["hours_draw"]
    assert len(runs["other"]) == len(runs[artifact["run_id"]]) == 22
    for r in runs["other"]:
        assert switch_off not in r.annotations
        assert not any(draw in t for t in r.annotations)
    for r in runs[artifact["run_id"]]:
        assert switch_off in r.annotations
        assert any(draw in t for t in r.annotations)
    # the newest pair states no diagnosis, so none is drawn from the old one
    assert lane.diagnoses(scores, _in_repo(artifacts), notes) == []
    # and the behavioural legs say why from the newest pair
    legs = [s for s in scores if s.conditions.get("component") == "intensive_margin"]
    assert legs and all(
        "STATED FOR THE TEST" in s.publication["pe_missing"] for s in legs
    )


def test_tally_and_pe_missing_follow_each_runs_computed_years(artifact, tmp_path):
    """Coverage, not dataset support: a run that holds 2031 among its data
    years but computes only the default years leaves CBP's 2031-32 claims
    without a value and says so; one that computes 2031 answers them. The
    tally follows, and no claim id moves across the three histories."""
    wide = _wide_certified()
    notes = _verified_for(wide["variant_id"])
    histories = {"alone": lane.stage(notes)}
    for name, with_2031 in (("default_years", False), ("with_2031", True)):
        (tmp_path / name).mkdir()
        other = _on_pair(artifact, wide, run_id="other", with_2031=with_2031)
        _write(tmp_path / name, artifact, other)
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


def test_a_newer_run_that_skips_a_year_leaves_that_years_diagnosis(artifact, tmp_path):
    """The round-3 review's case: a newer run on a verified pair that
    computes only 2031 takes no claim's latest result in the years it skips,
    so the diagnoses of those years stay with the run that computed them."""
    wide = _wide_certified()
    notes = _verified_for(wide["variant_id"])
    other = _on_pair(artifact, wide, run_id="other", with_2031=True)
    for world in other["worlds"].values():
        world["years"] = {y: b for y, b in world["years"].items() if y == "2031"}
    _write(tmp_path, artifact, other)
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


def test_a_note_on_the_engine_or_a_run_names_its_pairs(tmp_path):
    spec = json.loads(lane.CONSTRUCTION.read_text())
    spec["annotations"][0].pop("variants")
    path = tmp_path / "construction_annotations.json"
    path.write_text(json.dumps(spec))
    with pytest.raises(ValueError, match="variants"):
        lane._spec(path)
    for kind in (lane.CENTAX, lane.CBP, "construction"):
        for a in lane.load_notes()[kind]:
            if "variants" in a:
                assert a["variants"] == [VARIANTS["default_variant"]], a["id"]


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
    assert len(computed) == 22
    assert {r["data_bundle"] for r in computed} == {CERTIFIED["revision"]}
    assert {r["engine_version"] for r in computed} == {"2.89.2"}
    lanes = _rows("SELECT * FROM lanes WHERE lane = ?", lane.LANE_ID)
    assert [r["stage"] for r in lanes] == ["computed"]
    # the note counts claims on the latest run, not results across the history
    assert lanes[0]["detail"].startswith("22 of 36 claims computed")


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


def test_central_static_rows_carry_the_hours_draw_diagnosis():
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
        "https://github.com/PolicyEngine/microcosm/issues/1126"
    }
    assert "15.3 of 30 weekly hours" in rows[0]["diagnosis_rationale"]


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
    unknown; the central static rows carry both results, the published
    figure first and the certified run as the latest."""
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
        assert [x["engine_version"] for x in r["results"]] == ["2.102.3", "2.89.2"]
        assert r["latest"]["data_bundle"] == CERTIFIED["revision"]
        assert r["latest"]["status_effective"] == "comparable"
        assert r["results"][0]["status_effective"] == "constructed"
    unscored = [r for r in rows if not r["results"]]
    assert len(unscored) == 14  # 12 CenTax margins + CBP's two 2031-32 cells
    assert all(r["conditions"].get("pe_missing") for r in unscored)
