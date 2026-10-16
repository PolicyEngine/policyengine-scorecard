"""Compare original-scorecard PMD cells without collapsing repeated identities.

The key is the workbook's exact event, title, head, table and fiscal year.
Some keys occur more than once. Within each key we match equal values first,
then pair the unmatched occurrences in workbook order as changed cells.
Edition metadata never participates in the cell key or the value comparison.
"""

from __future__ import annotations

import argparse
import gzip
import json
from collections import defaultdict, deque
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path

TABLE_HEADS = {
    "Tax Measures (Policy measures database)": "tax_head",
    "Spending Measures (Policy measures database)": "spending_head",
}
CellKey = tuple[str, str, str, str, str]


def cell_key(row: dict) -> CellKey:
    """Return the exact semantic key; preserve punctuation and empty heads."""
    conditions = row["conditions"]
    table = row["source_table"]
    key = (
        conditions["fiscal_event"],
        row["reform_hint"],
        conditions[TABLE_HEADS[table]],
        table,
        conditions["fy"],
    )
    if not all(isinstance(value, str) for value in key):
        raise ValueError("PMD cell key components must be strings")
    return key


def _value(row: dict) -> Decimal:
    try:
        value = Decimal(str(row["value_raw"]))
    except (InvalidOperation, KeyError) as error:
        raise ValueError("PMD cell has no numeric verbatim value") from error
    if not value.is_finite():
        raise ValueError("PMD cell has a non-finite verbatim value")
    return value


@dataclass(frozen=True)
class CellMatch:
    previous_line: int | None
    current_line: int | None
    previous: dict | None
    current: dict | None

    @property
    def key(self) -> CellKey:
        return cell_key(self.current if self.current is not None else self.previous)


@dataclass
class EditionDiff:
    identical: list[CellMatch]
    changed: list[CellMatch]
    new: list[CellMatch]
    removed: list[CellMatch]

    def accounting(self) -> dict:
        """Counts are a disjoint, exhaustive partition of both editions."""
        groups = {
            "identical": self.identical,
            "changed": self.changed,
            "new": self.new,
            "removed": self.removed,
        }
        totals = {name: len(matches) for name, matches in groups.items()}
        previous = [
            match.previous_line
            for matches in groups.values()
            for match in matches
            if match.previous_line is not None
        ]
        current = [
            match.current_line
            for matches in groups.values()
            for match in matches
            if match.current_line is not None
        ]
        if len(previous) != len(set(previous)) or len(current) != len(set(current)):
            raise ValueError("PMD edition diff repeats a source occurrence")
        by_event = defaultdict(lambda: dict.fromkeys(groups, 0))
        for name, matches in groups.items():
            for match in matches:
                by_event[match.key[0]][name] += 1
        november_cells, march_cells = len(previous), len(current)
        if (
            totals["identical"] + totals["changed"] + totals["removed"]
            != november_cells
            or totals["identical"] + totals["changed"] + totals["new"] != march_cells
        ):
            raise ValueError("PMD edition diff accounting is not exhaustive")
        return {
            "november_cells": november_cells,
            "march_cells": march_cells,
            "totals": totals,
            "by_event": dict(sorted(by_event.items())),
        }

    def report(self) -> dict:
        report = self.accounting()
        report["comparison"] = (
            "Exact event/title/head/table/FY keys; repeated keys matched by "
            "equal numeric GBP-million value first, then workbook occurrence order"
        )
        report["changed_cells"] = [
            {
                "key": list(match.key),
                "november_line": match.previous_line,
                "march_line": match.current_line,
                "november_value_raw": match.previous["value_raw"],
                "march_value_raw": match.current["value_raw"],
            }
            for match in self.changed
        ]
        report["removed_cells"] = [
            {
                "key": list(match.key),
                "november_line": match.previous_line,
                "november_value_raw": match.previous["value_raw"],
            }
            for match in self.removed
        ]
        return report


def compare_editions(previous: list[dict], current: list[dict]) -> EditionDiff:
    """Retain line numbers in the input JSONL files, including non-PMD rows."""
    old_groups, new_groups = defaultdict(list), defaultdict(list)
    for rows, groups in ((previous, old_groups), (current, new_groups)):
        for number, row in enumerate(rows, 1):
            if row.get("source_table") in TABLE_HEADS:
                groups[cell_key(row)].append((number, row))
    identical, changed, new, removed = [], [], [], []
    for key in dict.fromkeys((*old_groups, *new_groups)):
        old, fresh = old_groups[key], new_groups[key]
        by_value = defaultdict(deque)
        for number, row in old:
            by_value[_value(row)].append((number, row))
        matched_old, unmatched_new = set(), []
        for number, row in fresh:
            matches = by_value[_value(row)]
            if matches:
                old_number, old_row = matches.popleft()
                matched_old.add(old_number)
                identical.append(CellMatch(old_number, number, old_row, row))
            else:
                unmatched_new.append((number, row))
        unmatched_old = [(n, row) for n, row in old if n not in matched_old]
        paired = min(len(unmatched_old), len(unmatched_new))
        for (old_number, old_row), (number, row) in zip(
            unmatched_old[:paired], unmatched_new[:paired], strict=True
        ):
            changed.append(CellMatch(old_number, number, old_row, row))
        removed.extend(
            CellMatch(number, None, row, None) for number, row in unmatched_old[paired:]
        )
        new.extend(
            CellMatch(None, number, None, row) for number, row in unmatched_new[paired:]
        )
    for matches in (identical, changed, new):
        matches.sort(key=lambda match: match.current_line)
    removed.sort(key=lambda match: match.previous_line)
    result = EditionDiff(identical, changed, new, removed)
    accounting = result.accounting()
    if accounting["november_cells"] != sum(map(len, old_groups.values())) or accounting[
        "march_cells"
    ] != sum(map(len, new_groups.values())):
        raise ValueError("PMD edition diff lost source cells")
    return result


def load_staged(path: Path) -> list[dict]:
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("previous", type=Path)
    parser.add_argument("current", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    report = compare_editions(
        load_staged(args.previous), load_staged(args.current)
    ).report()
    payload = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.write_text(payload)
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
