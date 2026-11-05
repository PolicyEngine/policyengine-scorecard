"""A registry's name search must not depend on the engine's variable order.

policyengine-core adds variables in glob order, which differs by filesystem,
so build_ab2025_registry.py --check fails wherever that order differs unless
the search text reads the same for every ordering of the variable list.
"""

from hypothesis import given
from hypothesis import strategies as st

from pipeline.name_search import name_search

NAMES = st.lists(
    st.text(alphabet="abc_", min_size=1, max_size=6), min_size=0, max_size=30
)


@given(
    variables=NAMES.flatmap(lambda vs: st.tuples(st.just(vs), st.permutations(vs))),
    parameters=NAMES,
    pattern=st.sampled_from(["a", "b", "c", "_", "a|b", "^a", "c$"]),
)
def test_name_search_reads_the_same_for_any_variable_order(
    variables, parameters, pattern
):
    original, permuted = variables
    assert name_search(pattern, parameters, original, "2.89.2") == name_search(
        pattern, parameters, permuted, "2.89.2"
    )


def test_name_search_lists_the_first_six_variables_in_sorted_order():
    text = name_search("x", [], ["x9", "x1", "x8", "x2", "x7", "x3", "x6"], "2.89.2")
    assert "Variables: 7 ['x1', 'x2', 'x3', 'x6', 'x7', 'x8']." in text
