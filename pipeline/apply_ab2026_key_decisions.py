"""Give each staged AB2026 row its registered key, and write KEY_DECISIONS.md.

Tranche 1 staged 973 rows with `measure_key: null` and a proposed key in
`conditions.proposed_measure_key` (harvest README rule 2). Tranche 2
registers each proposed key, or folds it into a registered key
(pipeline/ab2026_key_decisions.py). AB2025's rows carry their registry key in
`measure_key`, and the contract checker rejects a registered key left in
`proposed_measure_key`, so this script moves each row's key into
`measure_key` and drops the condition. It changes nothing else in a row, and
it writes each claims file as the stagers do: sorted keys, UTF-8, gzip level 9
with no name or time in the header.

Every registered key is new to the registry and we fold none, so the rows a
decision covers are exactly the rows that now carry its key. `render`
rebuilds KEY_DECISIONS.md from the rewritten claims, and the tests check it.

Usage:
    python pipeline/apply_ab2026_key_decisions.py           # rewrite and write
    python pipeline/apply_ab2026_key_decisions.py --check   # check only

After a rewrite, re-pin COUNTS.json with pipeline/harvest_counts.py and
regenerate PROPOSED_KEYS.md with pipeline/ab2026_proposed_keys.py.
"""

import gzip
import io
import json
import sys
from collections import defaultdict
from pathlib import Path

try:
    from pipeline import ab2026_key_decisions as D
except ModuleNotFoundError:  # direct script invocation without PYTHONPATH
    import ab2026_key_decisions as D

REPO = Path(__file__).resolve().parent.parent
HARVEST = REPO / "sources/harvest-uk-ab2026-2026-10-29"
REGISTRY = REPO / "data/uk/ab2026_measures.json"
OUT = HARVEST / "KEY_DECISIONS.md"


def families(harvest=HARVEST):
    return sorted(
        p.name for p in harvest.iterdir() if (p / "claims_staged.jsonl.gz").exists()
    )


def read(path):
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def write(path, rows):
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb", mtime=0, filename="") as gz:
        for r in rows:
            gz.write(
                (json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n").encode()
            )
    path.write_bytes(buf.getvalue())


def rekey(row):
    """The row with its proposed key moved into measure_key (or unchanged)."""
    pk = (row.get("conditions") or {}).get("proposed_measure_key")
    if not pk:
        return row
    if pk not in D.DECISIONS:
        raise ValueError(f"{pk} has no decision in pipeline/ab2026_key_decisions.py")
    out = dict(row)
    out["conditions"] = {
        k: v for k, v in row["conditions"].items() if k != "proposed_measure_key"
    }
    out["measure_key"] = D.registered_key(pk)
    return out


def apply(harvest=HARVEST):
    changed = {}
    for fam in families(harvest):
        path = harvest / fam / "claims_staged.jsonl.gz"
        rows = read(path)
        new = [rekey(r) for r in rows]
        n = sum(a is not b for a, b in zip(rows, new))
        if n:
            write(path, new)
            changed[fam] = n
    return changed


def _ranges(idx):
    out, start, prev = [], None, None
    for i in idx:
        if start is None:
            start = prev = i
        elif i == prev + 1:
            prev = i
        else:
            out.append((start, prev))
            start = prev = i
    if start is not None:
        out.append((start, prev))
    return ", ".join(str(a) if a == b else f"{a}–{b}" for a, b in out)


def _why(d):
    v = d["verdict"]
    kind = v[0]
    if kind == "legs":
        return "We register it as a package of the registry measures its scope lists."
    if kind == "receipts":
        return "We register it as the receipts of the Table 6.1 lines its scope lists; no registered package holds them."
    if kind == "words":
        return f"Its producer gives the scope in words: {v[1]}."
    if kind in ("scope", "scope_why"):
        return "No registered key has its scope; the engine can't express it, and it falls outside the household model."
    if kind == "gap":
        return "No registered key has its scope; the engine can't express it yet (a policyengine-uk development item)."
    if kind == "delta":
        return "No registered key has its scope, and the engine expresses it as a delta on current law."
    if kind == "partial":
        return (
            "No registered key has its scope, and the engine expresses only part of it."
        )
    raise ValueError(kind)


def render(harvest=HARVEST):
    """KEY_DECISIONS.md from the decisions and the rows that carry each key."""
    reg = {m["measure_key"]: m for m in json.loads(REGISTRY.read_text())["measures"]}
    rows_of = defaultdict(lambda: defaultdict(list))
    for fam in families(harvest):
        for i, r in enumerate(read(harvest / fam / "claims_staged.jsonl.gz")):
            rows_of[r["measure_key"]][fam].append(i)
    kinds = defaultdict(int)
    for d in D.DECISIONS.values():
        kinds[d["kind"]] += 1
    total = sum(d["rows"] for d in D.DECISIONS.values())
    out = [
        "# Key decisions for the AB2026 harvest (#230)",
        "",
        "Generated by `pipeline/apply_ab2026_key_decisions.py` from `pipeline/ab2026_key_decisions.py` and the staged families; don't edit by hand.",
        "",
        f"The families proposed {len(D.DECISIONS)} keys ({kinds['measure']} measures, {kinds['package']} packages and {kinds['option']} options) on {total} staged rows (README rule 2). "
        f"We register {len(D.DECISIONS) - len(D.FOLDED)} of them in `data/uk/ab2026_measures.json` and fold {len(D.FOLDED)}. "
        "Two producers' packages share a key only if their scopes match line for line (rule 3), and no proposed scope matches a registered key, or another proposed key, that way. "
        f"We register {len(D.RENAMED)} key under a new name and keep the proposed name in the entry's `proposed_as`. Each row carries its key in `measure_key`, as AB2025's rows do.",
        "",
        "Each row below gives the key, what we did, the registry verdict, why, and the rows it covers by family and row number (from 0, in `claims_staged.jsonl.gz`). "
        "The scope comes from the families' NOTES.md, and the registry entry's `source_note` repeats it.",
        "",
        "| proposed key | decision | registered key | verdict | why | rows |",
        "|---|---|---|---|---|---|",
    ]
    for pk, d in sorted(D.DECISIONS.items()):
        key = D.registered_key(pk)
        if pk in D.FOLDED:
            decision, why = "folded", D.FOLDED[pk][1]
        elif pk in D.RENAMED:
            decision, why = "registered, renamed", _why(d)
        else:
            decision, why = "registered", _why(d)
        m = reg.get(key)
        verdict = m["computability"] if m else "MISSING"
        cover = "; ".join(
            f"{fam} {_ranges(idx)}" for fam, idx in sorted(rows_of[key].items())
        )
        n = sum(len(v) for v in rows_of[key].values())
        out.append(
            f"| `{pk}` | {decision} | `{key}` | {verdict} | {why} Scope: {d['scope'].replace('|', '/')} | {n}: {cover} |"
        )
    return "\n".join(out) + "\n"


def problems(harvest=HARVEST):
    reg = {m["measure_key"] for m in json.loads(REGISTRY.read_text())["measures"]}
    out = []
    for fam in families(harvest):
        for i, r in enumerate(read(harvest / fam / "claims_staged.jsonl.gz")):
            if (r.get("conditions") or {}).get("proposed_measure_key"):
                out.append(f"{fam} row {i} still carries a proposed key")
    counted = defaultdict(int)
    for fam in families(harvest):
        for r in read(harvest / fam / "claims_staged.jsonl.gz"):
            counted[r["measure_key"]] += 1
    for pk, d in D.DECISIONS.items():
        key = D.registered_key(pk)
        if key not in reg:
            out.append(f"{key} is not in the registry")
        if pk not in D.FOLDED and counted[key] != d["rows"]:
            out.append(f"{key}: {counted[key]} rows, the decision records {d['rows']}")
    if OUT.read_text() != render(harvest):
        out.append("KEY_DECISIONS.md is stale")
    return out


def main(argv):
    if "--check" not in argv:
        print(json.dumps(apply(), indent=1))
        OUT.write_text(render())
    bad = problems()
    print("\n".join(bad) if bad else "ok")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
