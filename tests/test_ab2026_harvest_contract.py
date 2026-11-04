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
        ({"conditions__fy": "2026/27"}, "is not one fiscal year YYYY-YY"),
        ({"conditions__fy": "2026-29"}, "is not one fiscal year YYYY-YY"),
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
        # review A H-1: a component is a part (rule 9)
        ({"conditions__component": "Receipts: VAT"}, "a component row has row_type"),
        (
            {"conditions__component": " ", "conditions__row_type": "measure_component"},
            "names its component and measure",
        ),
        # review A H-2: value against value_raw
        ({"value": float("nan")}, "value is not finite"),
        ({"value": float("inf")}, "value is not finite"),
        ({"value": -2625}, "at a stated scale"),
        ({"value": 2625000000}, "opposite sign"),
        # review A H-6
        (
            {"metric": ..., "proposed_metric": "affected_share"},
            "is a registered Metric",
        ),
        ({"conditions__recosting_of": "autumn_budget_2025"}, "row_type recosting"),
        ({"conditions__fy": ...}, "conditions.fy or conditions.horizon"),
        ({"conditions__geography": "England for count; UK funding"}, "is not a code"),
        ({"attribution": "restated", "note": ""}, "names whose figure"),
        (
            {"measure_key": None, "conditions__proposed_measure_key": "ab2026___x"},
            "is not ab2026",
        ),
        (
            {
                "measure_key": None,
                "conditions__proposed_measure_key": "ab2026__package_",
            },
            "is not ab2026",
        ),
        (
            {
                "measure_key": None,
                "conditions__proposed_measure_key": "ab2026__package",
            },
            "is not ab2026",
        ),
        ({"measure_key": ["ab2026__x"]}, "measure_key is not a string"),
        ({"publication": None}, "publication is not an object"),
        ({"value_raw": None}, "value_raw is empty"),
    ],
)
def test_each_rule_broken_on_a_valid_row_is_a_problem(changes, expected):
    found = problems(mutated(**changes))
    assert any(expected in p for p in found), found


def test_value_raw_scale_words_set_the_scale():
    """review A H-2: "£15 billion" is 1.5e10, never 1.5e7; "N in M" is N/M."""
    bn = mutated(value_raw="£15 billion", quote="£15 billion", value=1.5e10)
    wrong = mutated(value_raw="£15 billion", quote="£15 billion", value=1.5e7)
    share = mutated(
        value_raw="1 in 4", quote="1 in 4", value=0.25, normalization="N in M -> N/M"
    )
    worded = mutated(
        value_raw="£2bn",
        quote="cut of £2bn",
        value=-2e9,
        normalization="£bn x 1e9; sign from the wording (cut)",
    )
    assert problems(bn) == []
    assert any("at a stated scale" in p for p in problems(wrong))
    assert problems(share) == []
    assert problems(worded) == []


def test_malformed_rows_are_reported_not_raised():
    """review A H-6(h)."""
    for row in (
        mutated(conditions=["fy"]),
        mutated(publication=None),
        mutated(measure_key=["x"]),
        mutated(quote=None),
        "not a row",
    ):
        assert problems(row), row


def test_rule_4_holds_whatever_the_title_case():
    row = mutated(
        publication__title="Budget 2026: IMPACT ON HOUSEHOLDS",
        value_kind="approx_chart_reading",
    )
    assert any("rule 4" in p for p in problems(row))


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


def _write(fam, rows):
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb", mtime=0, filename="") as gz:
        for r in rows:
            gz.write((json.dumps(r, sort_keys=True) + "\n").encode())
    (fam / "claims_staged.jsonl.gz").write_bytes(buf.getvalue())


def _family_with_a_proposed_key(
    tmp_path, notes_extra, key="ab2026__package_test_scope"
):
    fam = tmp_path / "uk_test_family"
    shutil.copytree(FAMILY, fam)
    rows = read_rows(fam)
    i = rows.index(BASE)
    rows[i]["measure_key"] = None
    rows[i]["conditions"]["proposed_measure_key"] = key
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


def test_a_scope_for_a_longer_key_does_not_scope_its_prefix(tmp_path):
    """review A H-6(g): NOTES scopes a key as a whole token."""
    fam = _family_with_a_proposed_key(
        tmp_path,
        "\n- `ab2026__package_test_scope_wider`: Table 6.1 lines 1-2.\n",
        key="ab2026__package_test_scope",
    )
    assert family_problems(fam) == [
        "NOTES.md does not give the scope of ab2026__package_test_scope"
    ]


def _family_with_copies(tmp_path, n, factor=1.0):
    fam = tmp_path / "uk_test_family"
    shutil.copytree(FAMILY, fam)
    rows = read_rows(fam)
    i = rows.index(BASE)
    extra = copy.deepcopy(BASE)
    extra["value"] = BASE["value"] * factor
    rows[i + 1 : i + 1] = [copy.deepcopy(extra) for _ in range(n)]
    _write(fam, rows)
    return fam


def test_three_printings_of_one_claim_are_a_problem(tmp_path):
    """review A H-3: the AB2025 ingest merges two rows that share a claim
    identity and raises on three (red book rows 179, 191 and 200)."""
    assert family_problems(_family_with_copies(tmp_path / "a", 1)) == []
    triple = family_problems(_family_with_copies(tmp_path / "b", 2))
    assert len(triple) == 1 and "more than 2" in triple[0], triple


def test_a_pair_that_disagrees_is_a_problem(tmp_path):
    # a value off by 1% (value_raw unchanged) is also a value_raw mismatch
    found = family_problems(_family_with_copies(tmp_path, 1, factor=1.01))
    assert any("differ by over 0.5%" in p for p in found), found


def _family(tmp_path):
    fam = tmp_path / "uk_test_family"
    shutil.copytree(FAMILY, fam)
    return fam


def _rewrite_manifest(fam, edit):
    lines = [
        json.loads(x) for x in (fam / "manifest.jsonl").read_text().splitlines() if x
    ]
    lines = edit(lines)
    (fam / "manifest.jsonl").write_text("".join(json.dumps(m) + "\n" for m in lines))


@pytest.mark.parametrize(
    ("edit", "expected"),
    [
        (lambda m: [{**m[0], "sha256": "abc"}, *m[1:]], "sha256 is not a sha256"),
        (lambda m: [{**m[0], "retrieved": ""}, *m[1:]], "needs url, title"),
        (lambda m: [*m, m[0]], "lists a primary twice"),
        (lambda m: m[1:], "primary_sha256 is not in manifest.jsonl"),
    ],
)
def test_each_manifest_rule_broken_is_a_problem(tmp_path, edit, expected):
    """review A H-7: the manifest checks, reached by a test."""
    fam = _family(tmp_path)
    _rewrite_manifest(fam, edit)
    found = family_problems(fam)
    assert any(expected in p for p in found), found[:5]


def test_a_family_missing_a_file_is_a_problem(tmp_path):
    fam = _family(tmp_path)
    (fam / "NOTES.md").unlink()
    assert family_problems(fam) == ["uk_test_family: missing ['NOTES.md']"]
