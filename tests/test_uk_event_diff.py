"""The release diff: flags describe movements; nothing passes or fails.

Synthetic namespaces go through the real artifact, staging and comparison
writers, so the diff reads them through the same verified loaders it uses on
real replays. The committed legacy namespace is diffed against itself.
"""

import copy
import hashlib
import json
import random
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from pipeline import compare_uk_event as compare
from pipeline import compute_uk_ab2025 as ab
from pipeline import compute_uk_event as compute
from pipeline import diff_uk_event_runs as diff
from pipeline import stage_uk_event as stage

EVENT = "test_event"
KEY = f"{EVENT}__tax_and_benefit"


def measure(modifier=0.2, heads=None):
    rows = []
    for year in (2024, 2025):
        fy = f"{year}-{str(year + 1)[-2:]}"
        rows += [
            {
                "source_row_id": f"tax_{year}",
                "source_row_number": year,
                "fy": fy,
                "metric": "revenue_change",
                "tax_head": "Income tax",
                "value_gbp": 100,
                "source_table": "T",
                "source_column": "C",
            },
            {
                "source_row_id": f"benefit_{year}",
                "source_row_number": year + 1,
                "fy": fy,
                "metric": "exchequer_impact",
                "tax_head": "Welfare inside cap",
                "value_gbp": -30,
                "source_table": "T",
                "source_column": "D",
            },
            {
                "source_row_id": f"corporation_{year}",
                "source_row_number": year + 2,
                "fy": fy,
                "metric": "revenue_change",
                "tax_head": "Corporation tax",
                "value_gbp": 4,
                "classification": "out_of_household_scope",
                "source_table": "T",
                "source_column": "E",
            },
        ]
    heads = heads or [
        {"obr_head": "Income tax", "pe_variables": ["income_tax"], "channel": "tax"},
        {
            "obr_head": "Welfare inside cap",
            "pe_variables": ["universal_credit"],
            "channel": "spending",
        },
    ]
    return {
        "measure_key": KEY,
        "title": "An announcement, see https://www.gov.uk/example",
        "computability": "partial",
        "classification": "partial",
        "construction": "reversal_on_certified_world",
        "commences_fy": "2024-25",
        "pe_baseline_modifier": {"gov.tax.rate": modifier},
        "head_variables": sorted({v for h in heads for v in h["pe_variables"]}),
        "heads": heads,
        "source_rows": rows,
    }


def simulation(values):
    return {
        "aggregates_gbp": {k: float(v) for k, v in values.items()},
        "variable_metadata": {k: {"entity": "person"} for k in values},
        "policyengine_bundle": {
            "model_version": "x",
            "certified_data_build_id": "build",
        },
        "dataset_sha256_before": "a" * 64,
        "dataset_sha256_after": "a" * 64,
        "performance": {},
    }


def make_namespace(
    tmp_path,
    name,
    *,
    effects=None,
    supported=(2024, 2025),
    variant=None,
    modifier=0.2,
    heads=None,
    skip=(),
    identical=(),
):
    """A complete namespace for one event; effects maps year -> {variable: gain}."""
    effects = effects or {
        2024: {"income_tax": 100e6, "universal_credit": -30e6},
        2025: {"income_tax": 110e6, "universal_credit": -33e6},
    }
    m = measure(modifier, heads)
    registry = {
        "event_slug": EVENT,
        "event": EVENT,
        "calendar_years": [2024, 2025],
        "measures": [m],
    }
    registry_path = (
        tmp_path / "data" / "uk" / "events" / f"{EVENT}_{name}_measures.json"
    )
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_path.write_bytes(compute.canonical_bytes(registry))
    registry_sha = hashlib.sha256(registry_path.read_bytes()).hexdigest()
    # The comparison loader binds to the canonical registry path.
    canonical = tmp_path / "data" / "uk" / "events" / f"{EVENT}_measures.json"
    canonical.write_bytes(registry_path.read_bytes())
    root = tmp_path / "ns" / name
    event_dir = root / EVENT
    event_dir.mkdir(parents=True)
    channels = compute.variable_channels(m)
    world = ab.worlds_for(m, {KEY: m}, years=[2024, 2025])
    variant_fields = (
        {"variant_id": variant, "variant_identity_sha256": "e" * 64} if variant else {}
    )
    artifacts = {}
    for year in supported:
        if year in skip:
            continue
        gains = effects[year]
        certified = {v: 1000e6 for v in channels}
        reversed_world = {
            v: certified[v] + (gains[v] if channels[v] == "tax" else -gains[v])
            for v in channels
        }
        if year in identical:
            reversed_world = dict(certified)
        artifact = compute.build_artifact(
            measure=m,
            world=world,
            year=year,
            baseline=simulation(reversed_world),
            reform=simulation(certified),
            certified=simulation(certified),
            registry_sha256=registry_sha,
            event=EVENT,
            variant_fields=variant_fields,
        )
        path = event_dir / f"{KEY}_{year}.json"
        path.write_bytes(compute.canonical_bytes(artifact))
        artifacts[str(path.relative_to(tmp_path))] = hashlib.sha256(
            path.read_bytes()
        ).hexdigest()
    manifest = {
        "event": EVENT,
        "registry_sha256": registry_sha,
        "certified_dataset_sha256": "a" * 64,
        "artifacts": artifacts,
        "policyengine_version": "6.2.6" if variant else "5.0.2",
        "engine_version": "2.125.1" if variant else "2.89.2",
        "policyengine_core_version": "3.33.0" if variant else "3.27.1",
        "data_bundle": "build",
    }
    if variant:
        manifest.update(
            variant_fields,
            data_years=list(range(min(supported), 2031)),
            supported_years=list(supported),
            unsupported_years=[
                {"year": y, "reason": "before_data_year"}
                for y in (2024, 2025)
                if y not in supported
            ],
            full_supported_grid=[{"measure_key": KEY, "year": y} for y in supported],
            full_supported_grid_complete=not skip,
        )
    (event_dir / "RUN_MANIFEST.json").write_bytes(compute.canonical_bytes(manifest))
    rows, tally = stage.stage_event(
        registry, manifest, artifact_dir=event_dir, registry_sha256=registry_sha
    )
    staged = b"".join((json.dumps(r, sort_keys=True) + "\n").encode() for r in rows)
    (event_dir / "STAGED.jsonl").write_bytes(staged)
    (event_dir / "STAGING_MANIFEST.json").write_bytes(
        compute.canonical_bytes(
            {
                **tally,
                "event": EVENT,
                "staged_path": f"ns/{name}/{EVENT}/STAGED.jsonl",
                "staged_sha256": hashlib.sha256(staged).hexdigest(),
            }
        )
    )
    compare.write_comparison(
        EVENT,
        registry_path=canonical,
        staged_path=event_dir / "STAGED.jsonl",
        output_dir=event_dir,
        artifact_root=tmp_path,
    )
    return diff.load_side(root, artifact_root=tmp_path)


@pytest.fixture
def ns(tmp_path, monkeypatch):
    monkeypatch.setattr(compute, "ROOT", tmp_path)

    def build(name, **kwargs):
        return make_namespace(tmp_path, name, **kwargs)

    return build


def flags_by_key(result):
    return {
        (r["level"], r["key"], r["measure_key"], r["year"]): r["flags"]
        for r in result["rows"]
    }


def test_committed_legacy_namespace_has_no_flags_against_itself(tmp_path):
    side = diff.load_side(diff.ROOT / "results" / "uk" / "events")
    result = diff.diff_sides(side, side)
    assert set(result["events"]) == {
        "autumn_budget_2024",
        "autumn_statement_2023",
        "spring_budget_2024",
        "spring_statement_2025",
        "spring_budget_2023",
    }
    assert not any(r["flags"] for r in result["rows"])
    assert result["identity_changes"] == {}
    files = diff.render(side, side)
    diff.write(files, tmp_path / "out")
    assert diff.check(files, tmp_path / "out") == []
    with open(tmp_path / "out" / "DIFF.json", "ab") as handle:
        handle.write(b" ")
    assert diff.check(files, tmp_path / "out") == ["DIFF.json"]


def test_identity_change_alone_raises_no_row_flags(ns):
    result = diff.diff_sides(ns("a"), ns("b", variant="pe6.2.6_uk2.125.1_build"))
    assert not any(r["flags"] for r in result["rows"])
    assert result["identity_changes"]["variant_id"]["head"] == "pe6.2.6_uk2.125.1_build"
    assert result["identity_changes"]["policyengine_uk_version"] == {
        "base": "2.89.2",
        "head": "2.125.1",
    }


def test_numerical_flag_only_strictly_above_the_threshold(ns):
    base = ns("a")
    within = ns(
        "b",
        effects={
            2024: {"income_tax": 100e6 + 1e6, "universal_credit": -30e6},
            2025: {"income_tax": 110e6, "universal_credit": -33e6},
        },
    )
    above = ns(
        "c",
        effects={
            2024: {"income_tax": 100e6 + 1.5e6, "universal_credit": -30e6},
            2025: {"income_tax": 110e6, "universal_credit": -33e6},
        },
    )
    assert not any(r["flags"] for r in diff.diff_sides(base, within)["rows"])
    flagged = flags_by_key(diff.diff_sides(base, above))
    assert flagged[("head", "income_tax", KEY, 2024)] == ["numerical"]
    assert flagged[("measure_year", "total", KEY, 2024)] == ["numerical"]
    assert flagged[("source_row", "tax_2024", KEY, 2024)] == ["numerical"]
    assert flagged[("head", "universal_credit", KEY, 2024)] == []


def test_sign_reversal_and_zero_crossing_are_structural_regardless_of_size(ns):
    base = ns(
        "a",
        effects={
            2024: {"income_tax": 0.2, "universal_credit": -30e6},
            2025: {"income_tax": 0.4, "universal_credit": -33e6},
        },
    )
    head = ns(
        "b",
        effects={
            2024: {"income_tax": 0.9, "universal_credit": -30e6},
            2025: {"income_tax": -0.6, "universal_credit": -33e6},
        },
    )
    flagged = flags_by_key(diff.diff_sides(base, head))
    assert flagged[("head", "income_tax", KEY, 2024)] == ["structural"]
    assert flagged[("head", "income_tax", KEY, 2025)] == ["structural"]
    codes = {
        (r["year"], d["code"])
        for r in diff.diff_sides(base, head)["rows"]
        if r["level"] == "head" and r["key"] == "income_tax"
        for d in r["details"]
    }
    assert codes == {(2024, "zero_crossing"), (2025, "zero_crossing")}
    flipped = ns(
        "c",
        effects={
            2024: {"income_tax": -5.0, "universal_credit": -30e6},
            2025: {"income_tax": 0.4, "universal_credit": -33e6},
        },
    )
    base5 = ns(
        "d",
        effects={
            2024: {"income_tax": 5.0, "universal_credit": -30e6},
            2025: {"income_tax": 0.4, "universal_credit": -33e6},
        },
    )
    rows = diff.diff_sides(base5, flipped)["rows"]
    assert any(d["code"] == "sign_reversal" for r in rows for d in r["details"])


def test_unsupported_year_is_support_never_coverage(ns):
    result = diff.diff_sides(
        ns("a"), ns("b", supported=(2025,), variant="pe6_uk2_build")
    )
    for record in result["rows"]:
        if record["key"].startswith("corporation_"):
            # Outside household scope in every year: support cannot move it.
            assert record["flags"] == []
        elif record["year"] == 2024:
            assert record["flags"] == ["support"], record
        else:
            assert record["flags"] == []
    assert result["flag_counts"]["coverage"] == 0
    assert result["flag_counts"]["support"] > 0


def test_missing_artifact_in_a_supported_year_is_coverage(ns):
    result = diff.diff_sides(ns("a"), ns("b", skip=(2025,), variant="pe6_uk2_build"))
    flagged = flags_by_key(result)
    assert flagged[("measure_year", "total", KEY, 2025)] == ["coverage"]
    assert flagged[("source_row", "tax_2025", KEY, 2025)] == ["coverage"]


def test_newly_inert_construction_is_flagged(ns):
    result = diff.diff_sides(ns("a"), ns("b", identical=(2025,)))
    flagged = flags_by_key(result)
    assert "inertness" in flagged[("measure_year", "total", KEY, 2025)]
    assert "inertness" in flagged[("source_row", "tax_2025", KEY, 2025)]


def test_changed_construction_and_mapping_are_flagged(ns):
    changed = flags_by_key(diff.diff_sides(ns("a"), ns("b", modifier=0.25)))
    assert "construction" in changed[("measure_year", "total", KEY, 2024)]
    heads = [
        {
            "obr_head": "Income tax",
            "pe_variables": ["income_tax", "national_insurance"],
            "channel": "tax",
        },
        {
            "obr_head": "Welfare inside cap",
            "pe_variables": ["universal_credit"],
            "channel": "spending",
        },
    ]
    effects = {
        y: {"income_tax": 100e6, "national_insurance": 0.0, "universal_credit": -30e6}
        for y in (2024, 2025)
    }
    remapped = flags_by_key(
        diff.diff_sides(ns("c"), ns("d", heads=heads, effects=effects))
    )
    assert "mapping" in remapped[("measure_year", "total", KEY, 2024)]
    assert remapped[("head", "national_insurance", KEY, 2024)] == ["mapping"]
    assert "mapping" in remapped[("source_row", "tax_2024", KEY, 2024)]


def test_premise_changes_flag_construction_and_current_law_is_context(ns):
    base, head = ns("a"), ns("b")
    premise = {
        "events": {
            EVENT: {
                "measures": {
                    KEY: {
                        "checks": {
                            "reversal_differs_from_current_law": {"holds": True}
                        },
                        "years": {
                            "2024": {
                                "paths": {
                                    "gov.tax.rate": {
                                        "current_law": 0.3,
                                        "baseline_world": 0.2,
                                        "reform_world": 0.3,
                                    }
                                }
                            }
                        },
                    }
                }
            }
        }
    }
    base["premises"] = premise
    moved = copy.deepcopy(premise)
    moved["events"][EVENT]["measures"][KEY]["years"]["2024"]["paths"][
        "gov.tax.rate"
    ].update(current_law=0.35, reform_world=0.35)
    head["premises"] = moved
    record = next(
        r
        for r in diff.diff_sides(base, head)["rows"]
        if r["level"] == "measure_year" and r["year"] == 2024
    )
    assert record["flags"] == ["construction"]
    assert [d["code"] for d in record["details"]] == ["reform_world_value_changed"]
    assert record["context"]["current_law_changed"] == {
        "gov.tax.rate": {"base": 0.3, "head": 0.35}
    }
    only_current_law = copy.deepcopy(premise)
    only_current_law["events"][EVENT]["measures"][KEY]["years"]["2024"]["paths"][
        "gov.tax.rate"
    ]["current_law"] = 0.4
    head["premises"] = only_current_law
    record = next(
        r
        for r in diff.diff_sides(base, head)["rows"]
        if r["level"] == "measure_year" and r["year"] == 2024
    )
    assert record["flags"] == []
    assert "current_law_changed" in record["context"]
    flipped = copy.deepcopy(premise)
    flipped["events"][EVENT]["measures"][KEY]["checks"][
        "reversal_differs_from_current_law"
    ]["holds"] = False
    head["premises"] = flipped
    assert any(
        d["code"] == "premise_check_changed"
        for r in diff.diff_sides(base, head)["rows"]
        for d in r["details"]
    )


def test_swapping_sides_swaps_values_and_keeps_flags(ns):
    a = ns("a")
    b = ns(
        "b",
        effects={
            2024: {"income_tax": -40e6, "universal_credit": -30e6},
            2025: {"income_tax": 0.0, "universal_credit": -60e6},
        },
        variant="pe6_uk2_build",
    )
    forward = {
        (r["level"], r["key"], r["year"]): r for r in diff.diff_sides(a, b)["rows"]
    }
    backward = {
        (r["level"], r["key"], r["year"]): r for r in diff.diff_sides(b, a)["rows"]
    }
    assert forward.keys() == backward.keys()
    for key, record in forward.items():
        other = backward[key]
        assert record["flags"] == other["flags"]
        assert (record["base_gbp"], record["head_gbp"]) == (
            other["head_gbp"],
            other["base_gbp"],
        )
        if record["delta_gbp"] is not None:
            assert record["delta_gbp"] == -other["delta_gbp"]


def test_measure_year_change_equals_the_sum_of_head_changes(ns):
    a = ns("a")
    b = ns(
        "b",
        effects={
            2024: {"income_tax": 123.456e6, "universal_credit": -7.25e6},
            2025: {"income_tax": 1e9, "universal_credit": -2e9},
        },
    )
    rows = diff.diff_sides(a, b)["rows"]
    for year in (2024, 2025):
        total = next(
            r for r in rows if r["level"] == "measure_year" and r["year"] == year
        )
        heads = [r for r in rows if r["level"] == "head" and r["year"] == year]
        assert total["delta_gbp"] == pytest.approx(
            sum(h["delta_gbp"] for h in heads), abs=1e-3
        )


def test_output_bytes_do_not_depend_on_input_order(ns):
    a = ns("a")
    b = ns(
        "b",
        effects={
            2024: {"income_tax": 50e6, "universal_credit": -30e6},
            2025: {"income_tax": 0.0, "universal_credit": -3e6},
        },
    )
    first = diff.render(a, b)
    for seed in range(5):
        rng = random.Random(seed)
        shuffled = copy.copy(b)
        shuffled["events"] = {}
        for event, data in b["events"].items():
            data = dict(data)
            items = list(data["rows"].items())
            rng.shuffle(items)
            data["rows"] = dict(items)
            artifacts = list(data["artifacts"].items())
            rng.shuffle(artifacts)
            data["artifacts"] = dict(artifacts)
            shuffled["events"][event] = data
        assert diff.render(a, shuffled) == first


def test_packets_cover_flagged_moves_but_not_support_only_rows(ns):
    a = ns("a")
    b = ns(
        "b",
        supported=(2025,),
        variant="pe6_uk2_build",
        effects={2025: {"income_tax": 300e6, "universal_credit": -33e6}},
    )
    files = diff.render(a, b)
    names = sorted(p for p in files if p.startswith("packets/") and p.endswith(".json"))
    assert names == [f"packets/{EVENT}__tax_and_benefit__2025.json"]
    packet = json.loads(files[names[0]])
    assert packet["flags"] == ["numerical"]
    assert [c["source_row_id"] for c in packet["source_cells"]] == [
        "tax_2025",
        "benefit_2025",
        "corporation_2025",
    ]
    assert "--variant pe6_uk2_build" in packet["reproduce"]["head"]
    assert "--variant pe5.0.2_uk2.89.2_build" in packet["reproduce"]["base"]
    assert packet["cited_sources"] == ["https://www.gov.uk/example"]
    assert packet["minimal_case"]["status"] == diff.PACKET_PENDING
    assert "files no issues" in packet["filing"]
    markdown = files["DIFF.md"].decode()
    assert "Years supported on one side only" in markdown
    assert f"| {EVENT} | 2024 | source_row | 2 |" in markdown


def test_unverifiable_side_is_refused(ns, tmp_path):
    ns("a")
    staged = tmp_path / "ns" / "a" / EVENT / "STAGED.jsonl"
    staged.write_bytes(staged.read_bytes() + b"\n")
    with pytest.raises(diff.DiffError, match="does not verify"):
        diff.load_side(tmp_path / "ns" / "a", artifact_root=tmp_path)


finite = st.floats(min_value=-1e13, max_value=1e13, allow_nan=False)


@settings(max_examples=500, deadline=None)
@given(finite, finite)
def test_threshold_is_symmetric_and_strict(base, head):
    assert diff.numerically_moved(base, head) == diff.numerically_moved(head, base)
    threshold = diff.numerical_threshold(base, head)
    assert threshold >= diff.NUMERICAL_FLOOR_GBP
    assert diff.numerically_moved(base, head) == (abs(head - base) > threshold)


@settings(max_examples=300, deadline=None)
@given(st.floats(min_value=0, max_value=1e12, allow_nan=False))
def test_no_flag_at_the_threshold_one_just_above(magnitude):
    threshold = diff.numerical_threshold(magnitude, magnitude)
    assert not diff.numerically_moved(magnitude, magnitude)
    # A move of exactly the floor never flags while the floor dominates.
    if magnitude < 99e6:
        assert not diff.numerically_moved(
            magnitude, magnitude + diff.NUMERICAL_FLOOR_GBP
        )
        assert diff.numerically_moved(
            magnitude, magnitude + 1.000001 * diff.NUMERICAL_FLOOR_GBP
        )
    assert threshold == max(diff.NUMERICAL_FLOOR_GBP, 0.01 * magnitude)


@settings(max_examples=300, deadline=None)
@given(finite, finite)
def test_sign_details_are_symmetric(base, head):
    assert [d["code"] for d in diff.sign_details(base, head)] == [
        d["code"] for d in diff.sign_details(head, base)
    ]
