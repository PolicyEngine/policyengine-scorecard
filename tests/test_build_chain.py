"""The build chain cannot lose a step in a merge (review of #137).

`scorecard_db/build_db.py` is one ordered list that many branches add to
at the same anchor, so it conflicts on nearly every UK merge, and three
times the conflict has cut through the middle of a step tuple. A careless
resolution either breaks the syntax (loud) or drops a step (silent: a
database missing a whole lane while every test stays green, because the
tests that would notice came with the dropped ingest). So the file is
parsed, the chain is read out of the AST and pinned by name and order,
and the chain is RUN and its summary compared with the pin.
"""

import ast
from pathlib import Path

from scorecard_db import build_db

BUILD_DB = Path(build_db.__file__)

# The chain as committed, in order. A branch that adds a step adds it here
# too, deliberately; a merge that drops one fails here instead of shipping
# a shorter database.
STEPS = (
    "urban",
    "harvest",
    "reform_validation",
    "platform",
    "solo",
    "diagnoses",
    "campaign_us",
    "harvest_lane_stages",
    "uk_externals",
    "uk_deductions",
    "dwp_pensions",
    "lpc_minimum_wage",
    "hmt_distributional",
    "obr_divergence",
    "uk_reform_validation",
    "uk_thinktanks",
    "ons_etb",
    "uk_policy_effects",
    "uk_ab2025",
    "produce_uk",
    "campaign_uk",
    "uk_ab2025_verdicts",
    "nz_budget_scores",
    "be_pit_reform",
    "be_jrc",
)


def _chain_from_source() -> list[str]:
    tree = ast.parse(BUILD_DB.read_text(), filename=str(BUILD_DB))
    build = next(
        n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "build"
    )
    for node in ast.walk(build):
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "steps" for t in node.targets
        ):
            names = []
            for elt in node.value.elts:
                assert isinstance(elt, ast.Tuple) and len(elt.elts) == 2, ast.dump(elt)
                name, fn = elt.elts
                assert isinstance(name, ast.Constant) and isinstance(name.value, str)
                assert isinstance(fn, ast.Lambda), ast.dump(elt)
                names.append(name.value)
            return names
    raise AssertionError("build() has no `steps = [...]` list")


def test_the_file_parses_and_the_chain_is_the_pinned_one():
    chain = _chain_from_source()
    assert len(chain) == len(set(chain)), "a step name repeats"
    missing = [s for s in STEPS if s not in chain]
    assert not missing, f"steps dropped from build_db.py: {missing}"
    assert chain == list(STEPS), "the chain and the pin differ in members or order"


def test_the_chain_runs_every_step(tmp_path):
    """Not just present in the source: executed, in order, on a fresh
    file. A step whose tuple survived the merge but whose lambda no longer
    runs its ingest is caught by _assert_every_imported_ingest_runs; a
    step that vanished is caught here."""
    summary = build_db.build(tmp_path / "chain.db")
    assert list(summary["steps"]) == list(STEPS)
    assert all(step in summary["steps"] for step in STEPS)
