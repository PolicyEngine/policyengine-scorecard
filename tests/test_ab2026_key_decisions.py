"""Tranche 2 of #230: every key tranche 1 proposed is registered or folded.

pipeline/ab2026_key_decisions.py records a decision for each of the 86
proposed keys, pipeline/build_ab2026_registry.py registers them, and
pipeline/apply_ab2026_key_decisions.py moves each staged row's key into
measure_key, as AB2025's rows carry theirs. These tests check that the three
agree: no row still proposes a key, every decision's key sits in the
registry, each decision covers the rows tranche 1 counted, and
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


def test_tranche_one_proposed_86_keys_on_973_rows():
    kinds = [d["kind"] for d in D.DECISIONS.values()]
    assert (kinds.count("measure"), kinds.count("package"), kinds.count("option")) == (
        15,
        58,
        13,
    )
    assert sum(d["rows"] for d in D.DECISIONS.values()) == 973


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
