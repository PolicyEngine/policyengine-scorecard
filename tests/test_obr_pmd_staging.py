"""PMD workbook staging and edition comparisons use source cells, not counts."""

from __future__ import annotations

import copy
import gzip
import hashlib
import io
import json
import zipfile
from pathlib import Path

import pytest
from hypothesis import given, settings, strategies as st

from scorecard_db import obr_pmd_diff as diff
from scorecard_db import stage_obr_pmd as staging


def row(value=1, *, title="Measure", event="Autumn Budget 2025", fy="2026-27"):
    return {
        "source_table": "Tax Measures (Policy measures database)",
        "reform_hint": title,
        "value_raw": value,
        "value": float(value) * 1e6,
        "conditions": {
            "fiscal_event": event,
            "tax_head": "Income tax",
            "fy": fy,
        },
    }


def test_diff_preserves_duplicate_occurrences_and_matches_values_before_order():
    previous = [row(1), row(2), row(2), row(4), row(9, title="Removed")]
    current = [row(2), row(3), row(2), row(8, title="New")]
    result = diff.compare_editions(previous, current)
    assert result.accounting() == {
        "november_cells": 5,
        "march_cells": 4,
        "totals": {"identical": 2, "changed": 1, "new": 1, "removed": 2},
        "by_event": {
            "Autumn Budget 2025": {
                "identical": 2,
                "changed": 1,
                "new": 1,
                "removed": 2,
            }
        },
    }
    assert [(m.previous_line, m.current_line) for m in result.identical] == [
        (2, 1),
        (3, 3),
    ]
    assert [(m.previous_line, m.current_line) for m in result.changed] == [(1, 2)]
    assert [m.previous_line for m in result.removed] == [4, 5]
    assert [m.current_line for m in result.new] == [4]


def test_numeric_values_ignore_edition_but_every_key_component_is_exact():
    previous = row(1)
    current = row("1.0000")
    current["conditions"]["edition"] = "March 2026"
    current["publication"] = {"edition": "March 2026"}
    result = diff.compare_editions([previous], [current])
    assert len(result.identical) == 1
    assert not result.changed and not result.new and not result.removed
    for field, location in (
        ("reform_hint", None),
        ("fiscal_event", "conditions"),
        ("tax_head", "conditions"),
        ("fy", "conditions"),
    ):
        changed = copy.deepcopy(current)
        target = changed if location is None else changed[location]
        target[field] += " "
        assert diff.cell_key(changed) != diff.cell_key(current)
    spending = copy.deepcopy(current)
    spending["source_table"] = "Spending Measures (Policy measures database)"
    spending["conditions"]["spending_head"] = spending["conditions"].pop("tax_head")
    assert diff.cell_key(spending) != diff.cell_key(current)


@given(
    st.lists(st.tuples(st.integers(-10, 10), st.text(max_size=8)), max_size=30),
    st.lists(st.tuples(st.integers(-10, 10), st.text(max_size=8)), max_size=30),
)
@settings(max_examples=100, deadline=None)
def test_edition_diff_accounting_partitions_every_source_occurrence(old, fresh):
    previous = [row(value, title=title) for value, title in old]
    current = [row(value, title=title) for value, title in fresh]
    result = diff.compare_editions(previous, current)
    accounting = result.accounting()
    totals = accounting["totals"]
    assert totals["identical"] + totals["changed"] + totals["removed"] == len(old)
    assert totals["identical"] + totals["changed"] + totals["new"] == len(fresh)
    for match in result.identical:
        assert diff.cell_key(match.previous) == diff.cell_key(match.current)
        assert match.previous["value_raw"] == match.current["value_raw"]
    assert previous == [row(value, title=title) for value, title in old]
    assert current == [row(value, title=title) for value, title in fresh]


@given(st.tuples(*(st.text(max_size=100) for _ in range(4))))
@settings(max_examples=100, deadline=None)
def test_cell_key_is_exact_injective_and_independent_of_metadata(parts):
    event, title, head, fy = parts
    original = row(title=title, event=event, fy=fy)
    original["conditions"]["tax_head"] = head
    assert diff.cell_key(original) == (
        event,
        title,
        head,
        "Tax Measures (Policy measures database)",
        fy,
    )
    reordered = dict(reversed(list(original.items())))
    reordered["conditions"] = dict(reversed(list(original["conditions"].items())))
    reordered["conditions"]["edition"] = "March 2026"
    reordered["value_raw"] = 987
    reordered["publication"] = {"receipt_sha256": "a" * 64}
    assert diff.cell_key(original) == diff.cell_key(reordered)
    altered = copy.deepcopy(original)
    altered["reform_hint"] += "\x00"
    assert diff.cell_key(original) != diff.cell_key(altered)


def test_diff_ignores_other_harvest_blocks_but_preserves_physical_line_numbers():
    rows = [{"source_table": "Unrelated table"}, row()]
    result = diff.compare_editions(rows, rows)
    assert len(result.identical) == 1
    assert result.identical[0].previous_line == result.identical[0].current_line == 2


def test_frozen_november_cells_are_all_identical_across_metadata_only_restage():
    root = Path(__file__).resolve().parents[1]
    previous = diff.load_staged(
        root / "sources/harvest-uk-2026-08-02/uk_obr/claims_staged.jsonl.gz"
    )
    current = copy.deepcopy(previous)
    for record in current:
        if record["source_table"] in diff.TABLE_HEADS:
            record["conditions"]["edition"] = "March 2026"
            record["publication"]["edition"] = "March 2026"
    result = diff.compare_editions(previous, current)
    assert result.accounting()["totals"] == {
        "identical": 24304,
        "changed": 0,
        "new": 0,
        "removed": 0,
    }
    # The input source records remain untouched, so callers can retain every
    # original claim and publication instead of re-ingesting identical cells.
    assert "edition" not in previous[0]["conditions"]


def test_committed_edition_diff_is_reproducible_and_accounts_for_both_editions():
    root = Path(__file__).resolve().parents[1]
    harvest = root / "sources/obr-pmd-march-2026"
    previous = diff.load_staged(
        root / "sources/harvest-uk-2026-08-02/uk_obr/claims_staged.jsonl.gz"
    )
    current = diff.load_staged(harvest / "claims_staged.jsonl.gz")
    result = diff.compare_editions(previous, current)
    assert result.report() == json.loads((harvest / "edition_diff.json").read_text())
    counts = result.accounting()
    assert counts["totals"] == {
        "identical": 24302,
        "changed": 0,
        "new": 246,
        "removed": 2,
    }
    assert counts["november_cells"] == 24304
    assert counts["march_cells"] == 24548
    totals = counts["totals"]
    assert totals["identical"] + totals["changed"] + totals["removed"] == 24304
    assert totals["identical"] + totals["changed"] + totals["new"] == 24548
    assert {match.key[0] for match in result.new} == {"Spring Forecast 2026"}


def fixture_workbook() -> bytes:
    """Small OOXML fixture with original, extended, zero and formula cells."""
    namespace = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"

    def sheet(event, *, spending=False):
        head = "PSCE in RDEL" if spending else "Income tax"
        title = "Spending policy" if spending else "Tax policy"
        value = "-2.5" if spending else "1.25"
        return f'''<worksheet xmlns="{namespace}"><sheetData>
<row r="3"><c r="E3" t="inlineStr"><is><t>2026-27</t></is></c><c r="F3" t="inlineStr"><is><t>2027-28</t></is></c><c r="G3" t="inlineStr"><is><t>2028-29</t></is></c></row>
<row r="4"><c r="B4" t="inlineStr"><is><t>{event}</t></is></c><c r="C4" t="inlineStr"><is><t>{title}</t></is></c><c r="D4" t="inlineStr"><is><t>{head}</t></is></c><c r="E4"><v>{value}</v></c><c r="F4" s="2"><v>0</v></c><c r="G4" s="1"><v>3</v></c></row>
<row r="5"><c r="B5" t="inlineStr"><is><t>{event}</t></is></c><c r="C5" t="s"><v>0</v></c><c r="D5" t="inlineStr"><is><t>{head}</t></is></c><c r="E5"><f>SUM(E4)</f><v>999</v></c><c r="F5" t="s"><v>1</v></c></row>
</sheetData></worksheet>'''

    files = {
        "xl/workbook.xml": f'''<workbook xmlns="{namespace}" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Notes" sheetId="1" r:id="rId1"/><sheet name="Tax Measures" sheetId="2" r:id="rId2"/><sheet name="Spending Measures" sheetId="3" r:id="rId3"/></sheets></workbook>''',
        "xl/_rels/workbook.xml.rels": """<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Target="worksheets/sheet1.xml"/><Relationship Id="rId2" Target="worksheets/sheet2.xml"/><Relationship Id="rId3" Target="/xl/worksheets/sheet3.xml"/></Relationships>""",
        "xl/styles.xml": f'''<styleSheet xmlns="{namespace}"><fills><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="solid"><fgColor rgb="FFE1E9EE"/></patternFill></fill><fill><patternFill patternType="darkGrid"><fgColor rgb="FFE1E9EE"/></patternFill></fill></fills><cellXfs><xf fillId="0"/><xf fillId="1"/><xf fillId="2"/></cellXfs></styleSheet>''',
        "xl/sharedStrings.xml": f'''<sst xmlns="{namespace}"><si><r><t>Shared </t></r><r><t>title</t></r></si><si><t>1.20</t></si></sst>''',
        "xl/worksheets/sheet1.xml": f'<worksheet xmlns="{namespace}"><sheetData/></worksheet>',
        "xl/worksheets/sheet2.xml": sheet("Autumn Budget 2025"),
        "xl/worksheets/sheet3.xml": sheet("Spring Forecast 2026", spending=True),
        "docProps/core.xml": """<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dcterms="http://purl.org/dc/terms/"><dcterms:created>2026-03-20T00:00:00Z</dcterms:created><dcterms:modified>2026-03-25T12:00:00Z</dcterms:modified></cp:coreProperties>""",
    }
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for filename, content in files.items():
            archive.writestr(zipfile.ZipInfo(filename, (2026, 3, 25, 0, 0, 0)), content)
    return buffer.getvalue()


def fixture_receipt(payload: bytes) -> dict:
    from data.uk.events.collect_vintage_locks import workbook_metadata
    from scorecard_db.collect_obr_pmd import CAPTURES, ORIGINAL_URL, build_receipt

    sheets, properties = workbook_metadata(payload)
    captures = []
    for stamp in CAPTURES:
        url = f"https://web.archive.org/web/{stamp}id_/{ORIGINAL_URL}"
        captures.append(
            {
                "role": "policy_measures",
                "original_url": ORIGINAL_URL,
                "archive_capture_url": url,
                "archive_timestamp": stamp,
                "edition": "march_2026",
                "status": "obtained",
                "retrieved_at": "2026-10-15T12:00:00+00:00",
                "byte_size": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
                "media_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "sheet_names": sheets,
                "workbook_properties": properties,
                "original_last_modified": None,
                "failure_reason": None,
                "attempts": [
                    {
                        "url": url,
                        "retrieved_at": "2026-10-15T12:00:00+00:00",
                        "http_status": 200,
                        "error": None,
                    }
                ],
            }
        )
    return build_receipt(captures)


def test_staging_reproduces_locked_fixture_and_original_harvest_conventions(tmp_path):
    payload = fixture_workbook()
    receipt = fixture_receipt(payload)
    workbook = tmp_path / "locked.workbook"
    workbook.write_bytes(payload)
    rows, accounting = staging.stage_workbook(workbook, receipt)
    repeated, repeated_accounting = staging.stage_workbook(workbook, receipt)
    assert staging.staged_bytes(rows) == staging.staged_bytes(repeated)
    assert accounting == repeated_accounting
    assert accounting["staged_original_cells"] == 6
    assert accounting["skipped_extended_cells"] == 2
    assert accounting["tax_measure_rows"] == accounting["spending_measure_rows"] == 2
    assert accounting["tax_cells"] == accounting["spending_cells"] == 3
    assert accounting["by_event"]["Spring Forecast 2026"]["measures"] == 2
    assert accounting["by_event"]["Spring Forecast 2026"]["staged_original_cells"] == 3
    assert [record["value_raw"] for record in rows] == [
        1.25,
        0.0,
        "1.20",
        -2.5,
        0.0,
        "1.20",
    ]
    assert [record["value"] for record in rows] == [1.25e6, 0, 1.2e6, -2.5e6, 0, 1.2e6]
    assert all(record["metric"] == "revenue_change" for record in rows[:3])
    for record in rows[3:]:
        assert record["proposed_metric"] == "exchequer_impact"
        assert record["conditions"]["impact_channel"] == "spending_measure"
    for record in rows:
        assert record["period"] == int(record["conditions"]["fy"][:4])
        assert record["time_basis"] == "fiscal_year"
        assert record["conditions"]["costing_phase"] == "original_scorecard"
        assert record["conditions"]["sign_convention"] == "positive_gain_to_exchequer"
        assert record["conditions"]["edition"] == "March 2026"
        assert record["publication"]["receipt_sha256"] == receipt["receipt_sha256"]
        assert record["publication"]["sha256"] == receipt["sha256"]
        assert record["publication"]["edition"] == "March 2026"
    assert rows[0]["publication"]["workbook_cell"] == "E4"
    assert rows[2]["reform_hint"] == "Shared title"
    first, second = tmp_path / "first", tmp_path / "second"
    staging.write_harvest(first, rows, accounting, receipt)
    staging.write_harvest(second, repeated, repeated_accounting, receipt)
    assert {p.name: p.read_bytes() for p in first.iterdir()} == {
        p.name: p.read_bytes() for p in second.iterdir()
    }
    assert gzip.decompress(
        (first / "claims_staged.jsonl.gz").read_bytes()
    ) == staging.staged_bytes(rows)
    manifest = json.loads((first / "manifest.jsonl").read_text())
    assert manifest["sha256"] == receipt["sha256"]
    assert manifest["wayback_snapshot"] == receipt["archive_capture_url"]
    assert not list(first.glob("*.xlsx"))


def test_staging_refuses_workbook_drift_and_wrong_edition(tmp_path):
    payload = fixture_workbook()
    receipt = fixture_receipt(payload)
    workbook = tmp_path / "locked.workbook"
    workbook.write_bytes(payload + b"changed")
    with pytest.raises(ValueError, match="bytes do not match"):
        staging.stage_workbook(workbook, receipt)
    workbook.write_bytes(payload)
    with pytest.raises(ValueError, match="edition does not match"):
        staging.stage_workbook(workbook, receipt, edition="November 2025")
