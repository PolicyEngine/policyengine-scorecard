"""The AB2026 harvest contract checker (#230), tested on rows built to break it.

tests/test_uk_ab2026_harvest.py holds every staged family to
pipeline/ab2026_harvest_contract.py. These tests hold the checker itself to
the README: each rule, broken on an otherwise valid row, gives a problem, and
the period and quote-length rules hold for every input.
"""

import copy
import gzip
import io
import json
import shutil
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from pipeline.ab2026_harvest_contract import (
    OGL,
    enums,
    family_problems,
    read_rows,
    registry_keys,
    row_problems,
)

ROOT = Path(__file__).resolve().parent.parent
FAMILY = ROOT / "sources" / "harvest-uk-ab2026-2026-10-29" / "uk_hmt_tables"
KEYS, EARLIER = registry_keys()
METRICS, UNITS = enums()
BASE = next(
    r
    for r in read_rows(FAMILY)
    if r["measure_key"] and "recosting_of" not in r["conditions"]
)
REGISTERED = BASE["measure_key"]


def problems(row):
    return row_problems(row, KEYS, EARLIER, METRICS, UNITS)


def mutated(**changes):
    """BASE with dotted-path changes; a value of ... deletes the field."""
    row = copy.deepcopy(BASE)
    for path, value in changes.items():
        *parents, leaf = path.split("__")
        target = row
        for p in parents:
            target = target[p]
        if value is ...:
            del target[leaf]
        else:
            target[leaf] = value
    return row


def test_a_staged_row_has_no_problems():
    assert problems(BASE) == []


@pytest.mark.parametrize(
    ("changes", "expected"),
    [
        ({"quote": ...}, "missing fields"),
        ({"invented": "x"}, "unknown fields"),
        ({"attribution": "guess"}, "attribution"),
        ({"status": "draft"}, "status is not ok"),
        ({"value": "1"}, "value is not a number"),
        ({"value": True}, "value is not a number"),
        ({"proposed_metric": "x"}, "exactly one of metric"),
        ({"metric": "not_a_metric"}, "is not a Metric"),
        ({"conditions__fiscal_event": "autumn_budget_2025"}, "fiscal_event"),
        ({"conditions__geography": 1}, "is not a string"),
        ({"conditions__fy": "2026/27"}, "is not YYYY-YY"),
        ({"period": 2026}, "is not the end year"),
        ({"time_basis": "annual"}, "time_basis fiscal_year"),
        ({"measure_key": "ab2026__not_a_measure"}, "is not in data/uk"),
        (
            {"conditions__proposed_measure_key": "ab2026__package_x"},
            "carries no proposed_measure_key",
        ),
        (
            {"measure_key": None, "conditions__proposed_measure_key": "package_x"},
            "is not ab2026",
        ),
        (
            {"measure_key": None, "conditions__proposed_measure_key": REGISTERED},
            "is registered",
        ),
        (
            {"conditions__recosting_of": "autumn_budget_2025"},
            "is not a autumn_budget_2025 key",
        ),
        ({"conditions__row_type": "measure_component"}, "rule 9"),
        (
            {
                "measure_key": None,
                "conditions__row_type": "measure_component",
                "conditions__component": "Scotland",
            },
            "rule 9",
        ),
        ({"value_raw": "-2,625"}, "quote does not contain value_raw"),
        ({"publication__primary_sha256": "abc"}, "is not a sha256"),
        ({"publication__date": "28 October 2026"}, "is not YYYY-MM-DD"),
        ({"publication__url": ""}, "publication.url is empty"),
        ({"attribution": "same_assumptions"}, "PolicyEngine-computed"),
    ],
)
def test_each_rule_broken_on_a_valid_row_is_a_problem(changes, expected):
    found = problems(mutated(**changes))
    assert any(expected in p for p in found), found


def test_a_component_with_its_measure_or_a_proposed_key_is_valid():
    """README rule 9: a part of one measure keeps that measure's key; a part
    of a measure with no Table 6.1 line keeps that measure's proposed key."""
    keyed = mutated(
        conditions__row_type="measure_component", conditions__component="Wales"
    )
    proposed = mutated(
        measure_key=None,
        conditions__row_type="measure_component",
        conditions__component="Capital AME",
        conditions__proposed_measure_key="ab2026__package_fiscally_neutral_x",
    )
    assert problems(keyed) == []
    assert problems(proposed) == []


@settings(max_examples=200, deadline=None)
@given(start=st.integers(1945, 2073), offset=st.integers(-3, 3))
def test_an_fy_row_is_valid_only_at_the_fy_end_year(start, offset):
    fy = f"{start}-{(start + 1) % 100:02d}"
    row = mutated(conditions__fy=fy, period=start + 1 + offset)
    end_year_problem = any("is not the end year" in p for p in problems(row))
    assert end_year_problem == (offset != 0)


@settings(max_examples=200, deadline=None)
@given(
    words=st.integers(1, 40),
    source=st.sampled_from(["ifs", "resolution_foundation", *sorted(OGL)]),
)
def test_only_ogl_quotes_may_run_to_15_words(words, source):
    """README rule 6: under 15 words outside the Open Government Licence."""
    row = mutated(source=source, quote=" ".join(["-2625"] * words))
    long_quote = any("15 or more words" in p for p in problems(row))
    assert long_quote == (source not in OGL and words >= 15)


def _family_with_a_proposed_key(tmp_path, notes_extra):
    fam = tmp_path / "uk_test_family"
    shutil.copytree(FAMILY, fam)
    rows = read_rows(fam)
    i = rows.index(BASE)
    rows[i]["measure_key"] = None
    rows[i]["conditions"]["proposed_measure_key"] = "ab2026__package_test_scope"
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb", mtime=0, filename="") as gz:
        for r in rows:
            gz.write((json.dumps(r, sort_keys=True) + "\n").encode())
    (fam / "claims_staged.jsonl.gz").write_bytes(buf.getvalue())
    with (fam / "NOTES.md").open("a") as fh:
        fh.write(notes_extra)
    return fam


def test_a_family_scopes_every_proposed_key_it_uses_in_its_notes(tmp_path):
    unscoped = _family_with_a_proposed_key(tmp_path / "a", "")
    scoped = _family_with_a_proposed_key(
        tmp_path / "b", "\n- `ab2026__package_test_scope`: Table 6.1 line 1.\n"
    )
    assert family_problems(unscoped) == [
        "NOTES.md does not give the scope of ab2026__package_test_scope"
    ]
    assert family_problems(scoped) == []
