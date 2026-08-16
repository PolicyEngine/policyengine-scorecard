"""The DWP take-up extract's shape contract: the committed tidy file must
match the adapter's pinned expectations, and the FYE-2021 suppression
annotation must match the data (modeled estimates suppressed;
administrative cells published)."""

import json
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "sources" / "dwp-takeup"


def _adapter():
    sys.path.insert(0, str(SRC))
    try:
        import adapter
    finally:
        sys.path.pop(0)
    return adapter


def test_committed_extract_matches_contract():
    a = _adapter()
    rows = json.loads((REPO / "data" / "externals" / "dwp-takeup.json").read_text())
    assert len(rows) == a.EXPECTED_TOTAL_ROWS
    sheets = {r["source_column"].split(":")[0] for r in rows}
    assert sheets == a.EXPECTED_SHEETS


def test_fye_2021_suppression_shape():
    rows = json.loads((REPO / "data" / "externals" / "dwp-takeup.json").read_text())
    by_status = Counter(r["status"] for r in rows if r["period"] == "FYE 2021")
    # Administrative cells are published; only modeled estimates are
    # suppressed (annotations.json methodology-breaks).
    assert by_status["ok"] == 42
    assert by_status["suppressed"] == 196
    ok_metrics = {
        r["metric"] for r in rows if r["period"] == "FYE 2021" and r["status"] == "ok"
    }
    assert ok_metrics == {
        "recipients_count",
        "total_amount_claimed",
        "mean_weekly_amount_claimed",
    }
