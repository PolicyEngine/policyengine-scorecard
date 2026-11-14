"""Tranche 2 of #230: every key tranche 1 proposed is registered or folded.

pipeline/ab2026_key_decisions.py records a decision for each of the 86
proposed keys, pipeline/build_ab2026_registry.py registers them, and
pipeline/apply_ab2026_key_decisions.py moves each staged row's key into
measure_key, where AB2025's rows name theirs. These tests check that the three
agree: no row still proposes a key, the registry lists every decision's
key, each decision covers the rows tranche 1 counted, and
KEY_DECISIONS.md is what the script renders.
"""

import json
from pathlib import Path

from pipeline import ab2026_key_decisions as D
from pipeline import ab2026_measure_keys as K
from pipeline.apply_ab2026_key_decisions import HARVEST, problems, read, rekey, render

ROOT = Path(__file__).resolve().parent.parent
REG = {
    m["measure_key"]: m
    for m in json.loads((ROOT / "data/uk/ab2026_measures.json").read_text())["measures"]
}


def test_the_rewrite_leaves_nothing_to_do():
    assert problems() == []


def test_key_decisions_md_is_rendered_from_the_rows():
    assert (HARVEST / "KEY_DECISIONS.md").read_text() == render()


def test_registered_86_keys_cover_980_rows():
    kinds = [d["kind"] for d in D.DECISIONS.values()]
    assert (kinds.count("measure"), kinds.count("package"), kinds.count("option")) == (
        15,
        58,
        13,
    )
    assert sum(d["rows"] for d in D.DECISIONS.values()) == 980


def test_each_registered_key_carries_its_kind_and_producers():
    for pk, d in D.DECISIONS.items():
        m = REG[D.registered_key(pk)]
        assert m["producers"] == list(d["producers"]), pk
        want = "option_costed_by_others" if d["kind"] == "option" else "announced"
        assert m["reported_status"] == want, pk
        assert m.get("proposed_as", m["measure_key"]) == pk, pk
        assert d["scope"] in m["source_note"], pk


def test_a_package_of_legs_names_exactly_its_lines():
    for pk, d in D.DECISIONS.items():
        if d["verdict"][0] != "legs":
            continue
        want = [K.key(x) if isinstance(x, int) else x for x in d["legs"]]
        assert REG[D.registered_key(pk)]["package_of"] == want, pk


def test_no_two_registered_packages_share_a_list_of_legs():
    """Rule 3: one scope, one key. Two packages with the same legs would be
    one scope under two keys, and we should have folded one into the other."""
    seen = {}
    for k, m in REG.items():
        legs = m.get("package_of") or m.get("receipts_of")
        if not isinstance(legs, list):
            continue
        sig = (m.get("construction"), tuple(sorted(legs)))
        assert sig not in seen, (k, seen.get(sig))
        seen[sig] = k


def test_rekey_moves_the_key_and_changes_nothing_else():
    row = {
        "measure_key": None,
        "value": 1.0,
        "conditions": {"proposed_measure_key": next(iter(D.RENAMED)), "fy": "2026-27"},
    }
    out = rekey(row)
    assert out["measure_key"] == next(iter(D.RENAMED.values()))
    assert out["conditions"] == {"fy": "2026-27"}
    assert {k: v for k, v in out.items() if k not in ("measure_key", "conditions")} == {
        "value": 1.0
    }
    keyed = {"measure_key": "ab2026__x", "conditions": {}}
    assert rekey(keyed) is keyed


def test_no_staged_row_names_a_key_outside_the_registry():
    earlier = {"autumn_budget_2025", "autumn_budget_2024", "spring_budget_2024"}
    for fam in sorted(p.name for p in HARVEST.iterdir() if p.is_dir()):
        path = HARVEST / fam / "claims_staged.jsonl.gz"
        if not path.exists():
            continue
        for r in read(path):
            k = r["measure_key"]
            if k is None or r["conditions"].get("recosting_of") in earlier:
                continue
            assert k in REG, (fam, k)


def _scope_lines(scope):
    """The Table 6.1 lines a scope names first, from the NOTES wording."""
    import re

    m = re.search(r"Table 6\.1 lines ((?:\d+(?:, | and )?)+)", scope)
    return [int(x) for x in re.findall(r"\d+", m.group(1))] if m else []


def test_a_package_of_legs_takes_the_lines_its_scope_names():
    """The legs table and the registry come from one authored list; the
    scope's own words give the lines independently."""
    for pk, d in D.DECISIONS.items():
        if d["verdict"][0] != "legs":
            continue
        lines = [x for x in d["legs"] if isinstance(x, int)]
        assert lines == _scope_lines(d["scope"]), pk
        reg_lines = [
            REG[k]["table_61_line"]
            for k in REG[D.registered_key(pk)]["package_of"]
            if "table_61_line" in REG[k]
        ]
        assert reg_lines == lines, pk


def test_a_producer_scope_is_its_producers_words_once():
    """A producer scope keeps its words as a string, never a list a reader
    could take for keys, and no two entries share the words."""
    seen = {}
    for k, m in REG.items():
        if m.get("construction") != "producer_scope":
            continue
        assert isinstance(m["package_of"], str) and m["package_of"].strip(), k
        assert m["package_of"] not in seen, (k, seen.get(m["package_of"]))
        seen[m["package_of"]] = k


def test_every_list_of_legs_names_registered_keys():
    for k, m in REG.items():
        for field in ("package_of", "receipts_of"):
            legs = m.get(field)
            if isinstance(legs, list):
                assert legs and set(legs) <= set(REG), (k, field)
