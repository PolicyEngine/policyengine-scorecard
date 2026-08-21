"""OBR welfare baseline (EFO March 2026 Table 4.9): hierarchy invariants.

Table 4.9 is nested — 'DWP social security' is the SUM of the rows under
its 'of which:' marker, and 'Other DWP in welfare cap' is the sum of a
further ten. The adapter originally emitted all 31 programs flat, which
made parents and children indistinguishable siblings: adding up the
in-cap non-total rows for 2025-26 gave £319.85bn against a published cap
total of £169.13bn, a 1.89x double-count.

These tests pin the hierarchy that prevents that. The load-bearing one is
test_components_only_sum_to_published_total: it is the assertion that
fails loudly on a flat emission.

Tolerances: components carry full float64 precision, so a parent whose
components are all published reconciles to exactly 0.0; PARENT_TOL of £1
sits ~4 orders above float noise and ~8 orders below the smallest
published component (£0.093bn). Where a parent has suppressed ('*')
components no exact check is possible — '*' only says |x| < £0.1bn — so
those are bounded by n_suppressed * £0.1bn instead.
"""

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
EXTERNAL = ROOT / "data" / "externals" / "obr-welfare.json"

pytestmark = pytest.mark.skipif(
    not EXTERNAL.exists(), reason="no committed obr-welfare.json"
)

PARENT_TOL = 1.0  # £1
SUPPRESSED_BOUND = 0.1e9  # '*' means |x| < £0.1bn
TOTAL_ROWS = 259  # 37 label rows x 7 financial years
SECTIONS = ("in_welfare_cap", "outside_welfare_cap")


def load():
    return json.loads(EXTERNAL.read_text())


def periods(rows):
    return sorted({r["period"] for r in rows})


def children_of(rows, aggregate):
    """Rows naming `aggregate` as parent in the same section and year."""
    return [
        r
        for r in rows
        if r["parent"] == aggregate["program"]
        and r["variant"] == aggregate["variant"]
        and r["period"] == aggregate["period"]
    ]


def assert_sums_to(children, parent, label):
    known = [c for c in children if c["status"] != "suppressed"]
    n_suppressed = len(children) - len(known)
    got = sum(c["value"] for c in known)
    want = parent["value"]
    assert want is not None, f"{label}: parent value suppressed"
    tol = PARENT_TOL if n_suppressed == 0 else n_suppressed * SUPPRESSED_BOUND
    assert abs(got - want) < tol, (
        f"{label}: {len(children)} components sum to {got:,.2f} but the published "
        f"parent is {want:,.2f} (residual {got - want:+,.2f}, tolerance {tol:,.2f})"
    )


def test_row_count_and_new_fields_present():
    rows = load()
    assert len(rows) == TOTAL_ROWS
    assert all("aggregate_level" in r and "parent" in r for r in rows)
    assert {r["aggregate_level"] for r in rows} == {"component", "subtotal", "total"}
    assert len(periods(rows)) == 7


def test_hierarchy_is_actually_nested():
    """The defect was a flat emission; assert the nesting exists at all."""
    rows = load()
    levels = {}
    for r in rows:
        levels[r["aggregate_level"]] = levels.get(r["aggregate_level"], 0) + 1
    # 3 aggregates (DWP social security in both sections, Other DWP in cap)
    # and 3 totals, over 7 years; the remaining 31 programs are leaves.
    assert levels == {"component": 217, "subtotal": 21, "total": 21}
    # the two aggregates the flat emission turned into siblings
    dwp = [r for r in rows if r["program"] == "dwp_social_security"]
    assert dwp and all(r["aggregate_level"] == "subtotal" for r in dwp)
    other_in_cap = [
        r
        for r in rows
        if r["program"] == "other_dwp" and r["variant"] == "in_welfare_cap"
    ]
    assert other_in_cap and all(
        r["aggregate_level"] == "subtotal" and r["parent"] == "dwp_social_security"
        for r in other_in_cap
    )


def test_every_component_has_a_resolvable_parent():
    rows = load()
    aggregates = {
        (r["program"], r["variant"], r["period"])
        for r in rows
        if r["aggregate_level"] in ("subtotal", "total")
    }
    for r in rows:
        if r["aggregate_level"] == "total":
            assert r["parent"] is None
            continue
        assert r["parent"] is not None, f"{r['program']} has no parent"
        key = (r["parent"], r["variant"], r["period"])
        assert key in aggregates, (
            f"{r['program']}/{r['variant']}/{r['period']} names parent "
            f"{r['parent']!r}, which is not an aggregate in that section"
        )


def test_components_sum_to_their_parent_every_year():
    """Sensitive to a dropped, renamed, or misparented row — unlike the
    published cap + outside = total identity, which is not."""
    rows = load()
    aggregates = [r for r in rows if r["aggregate_level"] in ("subtotal", "total")]
    checked = 0
    for agg in aggregates:
        if agg["variant"] is None:
            continue  # grand total: covered by the section identity below
        kids = children_of(rows, agg)
        assert kids, f"aggregate {agg['program']}/{agg['variant']} has no components"
        assert_sums_to(kids, agg, f"{agg['program']}[{agg['variant']}] {agg['period']}")
        checked += 1
    # 3 subtotals + 2 section totals, over 7 years
    assert checked == 35


def test_dwp_social_security_reconciles_exactly():
    """Both DWP sections have no suppressed components, so the sum must be
    exact to float64 — the strongest check the source supports."""
    rows = load()
    for variant in SECTIONS:
        for period in periods(rows):
            parent = next(
                r
                for r in rows
                if r["program"] == "dwp_social_security"
                and r["variant"] == variant
                and r["period"] == period
            )
            kids = children_of(rows, parent)
            assert all(c["status"] == "ok" for c in kids)
            got = sum(c["value"] for c in kids)
            assert abs(got - parent["value"]) < PARENT_TOL


def test_components_only_sum_to_published_total():
    """THE regression: with the flat emission, summing the non-total rows
    of the in-cap section for 2025-26 gave £319.85bn against a published
    £169.13bn. Leaves-only must land on the published total instead."""
    rows = load()
    for variant in SECTIONS:
        for period in periods(rows):
            leaves = [
                r
                for r in rows
                if r["variant"] == variant
                and r["period"] == period
                and r["aggregate_level"] == "component"
            ]
            total = next(
                r
                for r in rows
                if r["program"] == "total_welfare"
                and r["variant"] == variant
                and r["period"] == period
            )
            assert_sums_to(leaves, total, f"leaves-only {variant} {period}")


def test_flat_sum_of_all_program_rows_double_counts():
    """Pin the failure mode itself, so the hierarchy cannot be quietly
    dropped again: ignoring aggregate_level overstates the 2025-26 cap
    total by ~1.9x, and that is exactly what the field exists to prevent."""
    rows = load()
    naive = sum(
        r["value"]
        for r in rows
        if r["variant"] == "in_welfare_cap"
        and r["period"] == "2025-26"
        and r["program"] != "total_welfare"
        and r["status"] == "ok"
    )
    published = next(
        r["value"]
        for r in rows
        if r["program"] == "total_welfare"
        and r["variant"] == "in_welfare_cap"
        and r["period"] == "2025-26"
    )
    assert naive / published > 1.8  # ~1.89x, the double-count
    # ...and filtering to components alone removes it
    corrected = sum(
        r["value"]
        for r in rows
        if r["variant"] == "in_welfare_cap"
        and r["period"] == "2025-26"
        and r["aggregate_level"] == "component"
        and r["status"] == "ok"
    )
    assert abs(corrected - published) < 5 * SUPPRESSED_BOUND


def test_published_totals_identity_still_holds():
    rows = load()
    for period in periods(rows):
        by_variant = {
            r["variant"]: r["value"]
            for r in rows
            if r["program"] == "total_welfare" and r["period"] == period
        }
        assert (
            abs(
                by_variant["in_welfare_cap"]
                + by_variant["outside_welfare_cap"]
                - by_variant[None]
            )
            < 1e6
        )
