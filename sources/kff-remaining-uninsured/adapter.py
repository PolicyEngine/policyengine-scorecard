"""Adapt KFF eligibility-among-the-uninsured estimates to moments rows.

The state indicator contributes the rendered table's first percentage
column only.  The source labels that column ``Medicaid/Other Public``;
``source_column`` preserves that wording because the KFF CSV headers still
need an offline re-check.  Percentages stay on KFF's published 0--100 scale.

The flagship brief contributes five national 2022-vintage claims.  Those
rows remain on their own period so the moments join reports ``not_computed``
against the single-period 2024 certified artifact and can show the 2024 PE
value as a dated reference instead.

KFF uses ``NSD`` for statistically suppressed cells.  A suppressed selected
cell is emitted with ``value=None``, ``status=suppressed``, and an explicit
``suppression_flag``; it is never dropped.  There happen to be no NSD values
in the selected first column of the staged table.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent.parent / "data" / "externals" / "kff-remaining-uninsured.json"

SOURCE = "kff-remaining-uninsured"
PROGRAM = "medicaid"
STATE_VARIANT = "kff_reported_uninsured_magi_medicaid_chip_2025_rules"
BRIEF_VARIANT = "kff_reported_uninsured_magi_medicaid_chip_2023_rules"
STATE_SOURCE_COLUMN = "Medicaid/Other Public (%)"

STATE_CODES = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "District of Columbia": "DC",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
}

STATE_LINE = re.compile(r"^([^:]+):\s*(.+)$")


def parse_percent(raw: str) -> tuple[float | None, str, str | None]:
    """Return value, row status, and suppression flag for one KFF cell."""
    token = raw.strip()
    if token == "NSD":
        return None, "suppressed", "NSD"
    if not token.endswith("%"):
        raise ValueError(f"expected a percentage or NSD, got {token!r}")
    return float(token.removesuffix("%")), "ok", None


def _base_row() -> dict:
    return {
        "source": SOURCE,
        "program": PROGRAM,
        "benchmark_class": "different_model",
        "calibration_relationship": "held_out",
        "coverage_variant": "reported_uninsured",
    }


def state_rows(raw_path: Path | None = None) -> list[dict]:
    raw_path = raw_path or HERE / "raw" / "state_indicator_2024acs_2025levels.md"
    rows = []
    seen = set()
    for line in raw_path.read_text().splitlines():
        match = STATE_LINE.match(line)
        if match is None:
            continue
        name, rendered = match.groups()
        if name == "United States":
            geography = "US"
        elif name in STATE_CODES:
            geography = STATE_CODES[name]
        else:
            continue
        first_cell = rendered.split("|")[0].strip()
        value, status, suppression_flag = parse_percent(first_cell)
        rows.append(
            {
                **_base_row(),
                "metric": "eligible_share_among_uninsured",
                "subgroup": "total",
                "variant": STATE_VARIANT,
                "geography": geography,
                "unit_concept": "percent",
                "period": "2024",
                "value": value,
                "value_kind": "share",
                "status": status,
                "suppression_flag": suppression_flag,
                "source_column": STATE_SOURCE_COLUMN,
                "publication_population": "state_indicator",
                "data_vintage": "2024 ACS",
                "rules_vintage": "2025 eligibility levels",
            }
        )
        seen.add(geography)
    expected = {"US", *STATE_CODES.values()}
    if seen != expected:
        raise ValueError(
            "state table geography mismatch: "
            f"missing={sorted(expected - seen)}, extra={sorted(seen - expected)}"
        )
    return rows


def brief_rows() -> list[dict]:
    claims = (
        ("eligible_uninsured_count", "total", "persons", 6_400_000, "count"),
        ("eligible_uninsured_count", "adults", "persons", 4_200_000, "count"),
        ("eligible_uninsured_count", "children", "persons", 2_200_000, "count"),
        (
            "eligible_uninsured_count",
            "expansion_states",
            "persons",
            5_200_000,
            "count",
        ),
        ("eligible_share_among_uninsured", "total", "percent", 25.0, "share"),
    )
    return [
        {
            **_base_row(),
            "metric": metric,
            "subgroup": subgroup,
            "variant": BRIEF_VARIANT,
            "geography": "US",
            "unit_concept": unit,
            "period": "2022",
            "value": value,
            "value_kind": value_kind,
            "status": "ok",
            "suppression_flag": None,
            "source_column": "flagship brief headline",
            "publication_population": "flagship_brief",
            "data_vintage": "2022 ACS",
            "rules_vintage": "2023 eligibility levels",
            "reference_period": "2024",
        }
        for metric, subgroup, unit, value, value_kind in claims
    ]


def main() -> None:
    rows = state_rows() + brief_rows()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rows, indent=1) + "\n")
    suppressed = sum(row["status"] == "suppressed" for row in rows)
    print(f"{OUT}: {len(rows)} rows ({suppressed} suppressed)")


if __name__ == "__main__":
    main()
