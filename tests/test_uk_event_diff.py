"""The release diff: flags describe movements; nothing passes or fails.

Synthetic namespaces go through the real artifact, staging and comparison
writers, so the diff reads them through the same verified loaders it uses on
real replays. The committed legacy namespace is diffed against itself.
"""

import copy
import hashlib
import json
import random
import shlex
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
    remove_measure=False,
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
        "measures": [] if remove_measure else [m],
    }
    registry_path = (
        tmp_path / "data" / "uk" / "events" / f"{EVENT}_{name}_measures.json"
    )
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_path.write_bytes(compute.canonical_bytes(registry))
    registry_sha = hashlib.sha256(registry_path.read_bytes()).hexdigest()
    # Keep the current registry as well as each run's receipt-bound snapshot.
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
    for year in () if remove_measure else supported:
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
        artifact.update(
            policyengine_version="6.2.6" if variant else "5.0.2",
            engine_version="2.125.1" if variant else "2.89.2",
            policyengine_core_version="3.33.0" if variant else "3.27.1",
        )
        path = event_dir / f"{KEY}_{year}.json"
        path.write_bytes(compute.canonical_bytes(artifact))
        artifacts[str(path.relative_to(tmp_path))] = hashlib.sha256(
            path.read_bytes()
        ).hexdigest()
    manifest = {
        "event": EVENT,
        "registry_path": str(registry_path.relative_to(tmp_path)),
        "registry_sha256": registry_sha,
        "certified_dataset_sha256": "a" * 64,
        "artifacts": artifacts,
        "policyengine_version": "6.2.6" if variant else "5.0.2",
        "engine_version": "2.125.1" if variant else "2.89.2",
        "policyengine_core_version": "3.33.0" if variant else "3.27.1",
        "data_bundle": "build",
    }
    pairs = (
        set()
        if remove_measure
        else {(KEY, year) for year in supported if year not in skip}
    )
    full_pairs = set() if remove_measure else {(KEY, year) for year in (2024, 2025)}
    manifest.update(
        artifact_grid=compute.grid_rows(pairs),
        requested_grid=compute.grid_rows(pairs),
        full_event_grid=compute.grid_rows(full_pairs),
        full_event_complete=full_pairs <= pairs,
        years=sorted({year for _, year in pairs}),
        measures=sorted({key for key, _ in pairs}),
    )
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
            full_supported_grid=[]
            if remove_measure
            else [{"measure_key": KEY, "year": y} for y in supported],
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
        registry_path=registry_path,
        staged_path=event_dir / "STAGED.jsonl",
        output_dir=event_dir,
        artifact_root=tmp_path,
    )
    return diff.load_side(root, artifact_root=tmp_path)


def synthetic_record(manifest, registry, *, variants_path):
    """Stand-in for staging's variant lookup. These sides use synthetic
    variants (several share an id with different data years), so no one
    variants document can hold them; staging's checks of a manifest against
    its record are tested in test_uk_replay_variants.py."""
    if manifest is None or manifest.get("variant_id") is None:
        return None
    return {
        "variant_id": manifest["variant_id"],
        "layout": "replay_namespace",
        "identity_sha256": manifest["variant_identity_sha256"],
        "data_years": manifest["data_years"],
        "identity": {
            "dataset": {
                "path": "synthetic.h5",
                "repo_id": "synthetic/data",
                "revision": manifest["data_bundle"],
                "sha256": manifest["certified_dataset_sha256"],
            },
            "release_bundle": {"certified_data_build_id": manifest["data_bundle"]},
        },
    }


@pytest.fixture
def ns(tmp_path, monkeypatch):
    monkeypatch.setattr(compute, "ROOT", tmp_path)
    monkeypatch.setattr(stage, "manifest_variant", synthetic_record)

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

    def record_for(head_premises):
        head["premises"] = head_premises
        return next(
            r
            for r in diff.diff_sides(base, head)["rows"]
            if r["level"] == "measure_year" and r["year"] == 2024
        )

    def changed(**values):
        out = copy.deepcopy(premise)
        out["events"][EVENT]["measures"][KEY]["years"]["2024"]["paths"][
            "gov.tax.rate"
        ].update(values)
        return out

    # The reform world of a reversal is current law: when current law moves,
    # that world moves with it, which is context and not a construction change.
    record = record_for(changed(current_law=0.35, reform_world=0.35))
    assert record["flags"] == []
    assert record["context"]["current_law_changed"] == {
        "gov.tax.rate": {"base": 0.3, "head": 0.35}
    }
    # An executed override that changes (a re-derived counterfactual) is.
    record = record_for(changed(baseline_world=0.25))
    assert record["flags"] == ["construction"]
    assert [d["code"] for d in record["details"]] == ["baseline_world_value_changed"]
    # So is an override on one side that the other side no longer applies.
    record = record_for(changed(baseline_world=0.3))
    assert record["flags"] == ["construction"]
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


def test_packets_cover_flagged_moves_including_support_only_rows(ns):
    a = ns("a")
    b = ns(
        "b",
        supported=(2025,),
        variant="pe6_uk2_build",
        effects={2025: {"income_tax": 300e6, "universal_credit": -33e6}},
    )
    files = diff.render(a, b)
    names = sorted(p for p in files if p.startswith("packets/") and p.endswith(".json"))
    assert names == [
        f"packets/{EVENT}__tax_and_benefit__2024.json",
        f"packets/{EVENT}__tax_and_benefit__2025.json",
    ]
    support_packet = json.loads(files[names[0]])
    assert support_packet["flags"] == ["support"]
    packet = json.loads(files[names[1]])
    assert packet["flags"] == ["numerical"]
    assert [c["source_row_id"] for c in packet["source_cells"]] == [
        "tax_2025",
        "benefit_2025",
        "corporation_2025",
        "tax_2025",
        "benefit_2025",
        "corporation_2025",
    ]
    assert [c["side"] for c in packet["source_cells"]] == ["base"] * 3 + ["head"] * 3
    assert "--variant pe6_uk2_build" in packet["reproduce"]["head"]
    assert "--variant pe5.0.2_uk2.89.2_build" in packet["reproduce"]["base"]
    assert packet["cited_sources"] == [
        {"side": "base", "url": "https://www.gov.uk/example"},
        {"side": "head", "url": "https://www.gov.uk/example"},
    ]
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


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("certified_dataset_sha256", "b" * 64),
        ("supported_years", []),
        ("unsupported_years", []),
        ("data_years", [2024, 2025]),
        ("data_years", []),
        ("full_supported_grid", []),
        ("registry_sha256", "b" * 64),
        ("engine_version", "forged"),
        ("variant_identity_sha256", "b" * 64),
        ("artifact_grid", []),
        ("requested_grid", [{"measure_key": KEY, "year": 2024}]),
        ("full_event_grid", []),
        ("years", []),
        ("measures", []),
        ("full_event_complete", True),
        ("full_supported_grid_complete", False),
    ],
)
def test_run_manifest_must_reconcile_with_verified_receipts(ns, tmp_path, field, value):
    ns("a", supported=(2025,), variant="pe6_uk2_build")
    path = tmp_path / "ns" / "a" / EVENT / "RUN_MANIFEST.json"
    manifest = json.loads(path.read_bytes())
    manifest[field] = value
    path.write_bytes(compute.canonical_bytes(manifest))
    with pytest.raises(diff.DiffError):
        diff.load_side(path.parent.parent, artifact_root=tmp_path)


@pytest.mark.parametrize(
    "corruption", ["raw_delta", "dataset_sha256_before", "dataset_sha256_after"]
)
def test_unreferenced_artifact_is_revalidated(ns, tmp_path, corruption):
    ns("a", identical=(2024,))
    event_dir = tmp_path / "ns" / "a" / EVENT
    artifact_path = event_dir / f"{KEY}_2024.json"
    artifact = json.loads(artifact_path.read_bytes())
    if corruption == "raw_delta":
        artifact["head_effects"]["income_tax"] = 2e9
        artifact["measure_total_gbp"] = 2e9
    else:
        artifact[corruption] = "b" * 64
    artifact_path.write_bytes(compute.canonical_bytes(artifact))
    manifest_path = event_dir / "RUN_MANIFEST.json"
    manifest = json.loads(manifest_path.read_bytes())
    manifest["artifacts"][str(artifact_path.relative_to(tmp_path))] = hashlib.sha256(
        artifact_path.read_bytes()
    ).hexdigest()
    manifest_path.write_bytes(compute.canonical_bytes(manifest))
    with pytest.raises(diff.DiffError):
        diff.load_side(event_dir.parent, artifact_root=tmp_path)


def test_variant_identity_cannot_be_removed_from_run_manifest(ns, tmp_path):
    ns("a", variant="pe6_uk2_build")
    path = tmp_path / "ns" / "a" / EVENT / "RUN_MANIFEST.json"
    manifest = json.loads(path.read_bytes())
    for field in (
        "variant_id",
        "variant_identity_sha256",
        "data_years",
        "supported_years",
        "unsupported_years",
        "full_supported_grid",
        "full_supported_grid_complete",
    ):
        del manifest[field]
    path.write_bytes(compute.canonical_bytes(manifest))
    with pytest.raises(diff.DiffError):
        diff.load_side(path.parent.parent, artifact_root=tmp_path)


def test_unreferenced_artifact_cannot_be_removed_from_inventory(ns, tmp_path):
    ns("a", identical=(2024,))
    event_dir = tmp_path / "ns" / "a" / EVENT
    manifest_path = event_dir / "RUN_MANIFEST.json"
    manifest = json.loads(manifest_path.read_bytes())
    del manifest["artifacts"][f"ns/a/{EVENT}/{KEY}_2024.json"]
    manifest_path.write_bytes(compute.canonical_bytes(manifest))
    with pytest.raises(diff.DiffError):
        diff.load_side(event_dir.parent, artifact_root=tmp_path)


def test_both_historical_registries_load_after_both_runs_are_built(ns, tmp_path):
    ns("base")
    ns("head", modifier=0.3)
    base = diff.load_side(tmp_path / "ns" / "base", artifact_root=tmp_path)
    head = diff.load_side(tmp_path / "ns" / "head", artifact_root=tmp_path)
    assert (
        base["events"][EVENT]["registry_sha256"]
        != head["events"][EVENT]["registry_sha256"]
    )
    # Existing summary callers still require the current registry.
    with pytest.raises(compare.EventComparisonError, match="current event registry"):
        compare.load_verified_comparison(
            tmp_path / "ns" / "base" / EVENT / "COMPARISON.json",
            artifact_root=tmp_path,
        )


@pytest.mark.parametrize("field", ["by_status", "computed_measure_years"])
def test_verified_staging_tally_must_reconcile_with_run(ns, tmp_path, field):
    ns("a")
    event_dir = tmp_path / "ns" / "a" / EVENT
    staging_path = event_dir / "STAGING_MANIFEST.json"
    staging = json.loads(staging_path.read_bytes())
    staging[field] = {} if field == "by_status" else 0
    staging_path.write_bytes(compute.canonical_bytes(staging))
    provenance_path = event_dir / "COMPARISON_PROVENANCE.json"
    provenance = json.loads(provenance_path.read_bytes())
    provenance["staging_manifest_sha256"] = hashlib.sha256(
        staging_path.read_bytes()
    ).hexdigest()
    if field in provenance["replay_grid"]:
        provenance["replay_grid"][field] = staging[field]
    provenance_path.write_bytes(compute.canonical_bytes(provenance))
    with pytest.raises(diff.DiffError):
        diff.load_side(event_dir.parent, artifact_root=tmp_path)


def test_inertness_uses_provenance_bound_staging_manifest(ns, tmp_path):
    original = ns("a")
    event_dir = tmp_path / "ns" / "a" / EVENT
    relocated = tmp_path / "receipts" / EVENT
    relocated.mkdir(parents=True)
    for name in ("STAGED.jsonl", "STAGING_MANIFEST.json"):
        (relocated / name).write_bytes((event_dir / name).read_bytes())
    provenance_path = event_dir / "COMPARISON_PROVENANCE.json"
    provenance = json.loads(provenance_path.read_bytes())
    provenance["staged_path"] = str((relocated / "STAGED.jsonl").relative_to(tmp_path))
    provenance["staging_manifest_path"] = str(
        (relocated / "STAGING_MANIFEST.json").relative_to(tmp_path)
    )
    provenance_path.write_bytes(compute.canonical_bytes(provenance))
    local_manifest = event_dir / "STAGING_MANIFEST.json"
    staging = json.loads(local_manifest.read_bytes())
    staging["inert_measure_years"] = [{"measure_key": KEY, "year": 2025}]
    local_manifest.write_bytes(compute.canonical_bytes(staging))
    reloaded = diff.load_side(event_dir.parent, artifact_root=tmp_path)
    assert not reloaded["events"][EVENT]["inert_pairs"]
    assert not any(row["flags"] for row in diff.diff_sides(original, reloaded)["rows"])


def test_registry_digest_alone_flags_each_affected_record(ns):
    base = ns("registry_base")
    head = copy.deepcopy(base)
    head_event = head["events"][EVENT]
    head_event["registry"]["measures"][0]["title"] += " (revised registry note)"
    head_event["registry_sha256"] = hashlib.sha256(
        compute.canonical_bytes(head_event["registry"])
    ).hexdigest()

    result = diff.diff_sides(base, head)
    assert result["events"][EVENT]["registry_changed"]
    assert {record["level"] for record in result["rows"]} == set(diff.LEVELS)
    for record in result["rows"]:
        assert record["flags"] == ["mapping"]
        assert record["details"] == [
            {
                "flag": "mapping",
                "code": "registry_sha256_changed",
                "base": base["events"][EVENT]["registry_sha256"],
                "head": head_event["registry_sha256"],
            }
        ]


@pytest.mark.parametrize(
    "classification", ["out_of_household_scope", "not_expressible"]
)
@pytest.mark.parametrize("head_supported", [(2025,), (2024, 2025)])
def test_missing_noncomputable_row_requires_shared_year_support(
    ns, classification, head_supported
):
    base = ns("coverage_base", supported=(2025,), variant="pe6_uk2_build")
    head = ns("coverage_head", supported=head_supported, variant="pe6_uk2_build")
    base_event = base["events"][EVENT]
    head_event = head["events"][EVENT]
    base_event["rows"]["corporation_2024"]["classification"] = classification
    del head_event["rows"]["corporation_2024"]

    record = next(
        row
        for row in diff.compare_source_rows(EVENT, base_event, head_event)
        if row["key"] == "corporation_2024"
    )
    assert record["flags"] == []


def test_missing_noncomputable_row_has_coverage_when_both_support_the_year(ns):
    base = ns("shared_base")
    head = ns("shared_head")
    del head["events"][EVENT]["rows"]["corporation_2024"]
    record = next(
        row
        for row in diff.compare_source_rows(
            EVENT, base["events"][EVENT], head["events"][EVENT]
        )
        if row["key"] == "corporation_2024"
    )
    assert record["flags"] == ["coverage"]


def test_an_event_replayed_on_one_side_only_is_coverage(ns):
    # Review of 8700d29, B: a head that lost an event (or never ran it) must
    # not diff clean; every source row of that event is coverage.
    base = ns("missing_event_base")["events"][EVENT]
    for b, h, code in (
        (base, None, "event_on_base_only"),
        (None, base, "event_on_head_only"),
    ):
        records = diff.compare_source_rows(EVENT, b, h)
        assert records
        assert all(record["flags"] == ["coverage"] for record in records)
        assert {d["code"] for r in records for d in r["details"]} == {code}


def test_a_sealed_namespace_must_load_every_event_it_lists(ns, tmp_path):
    ns("listed")
    root = tmp_path / "ns" / "listed"
    manifest = {"schema_version": 1, "files": {f"{EVENT}/RUN_MANIFEST.json": "0" * 64}}
    (root / "NAMESPACE_MANIFEST.json").write_text(json.dumps(manifest))
    diff.load_side(root, artifact_root=tmp_path)
    manifest["files"]["another_event/RUN_MANIFEST.json"] = "0" * 64
    (root / "NAMESPACE_MANIFEST.json").write_text(json.dumps(manifest))
    with pytest.raises(diff.DiffError, match="differ from NAMESPACE_MANIFEST"):
        diff.load_side(root, artifact_root=tmp_path)


def premises_for(side_name, tmp_path, *, engine, registry_sha256):
    root = tmp_path / "ns" / side_name
    document = {
        "schema_version": 1,
        "engine": engine,
        "events": {EVENT: {"registry_sha256": registry_sha256, "measures": {}}},
    }
    (root / "CONSTRUCTION_PREMISES.json").write_text(json.dumps(document))
    return root


def test_premises_must_come_from_the_sides_engine_and_registry(ns, tmp_path):
    # Review of 8700d29, D: a premises file from another engine, or naming
    # another registry, must not drive construction flags.
    side = ns("premised", variant="pe6_uk2_build")
    registry = side["events"][EVENT]["registry_sha256"]
    own = {
        "policyengine": "6.2.6",
        "policyengine_core": "3.33.0",
        "policyengine_uk": "2.125.1",
    }
    root = premises_for("premised", tmp_path, engine=own, registry_sha256=registry)
    assert diff.load_side(root, artifact_root=tmp_path)["premises"] is not None
    premises_for(
        "premised",
        tmp_path,
        engine={**own, "policyengine_uk": "2.89.2"},
        registry_sha256=registry,
    )
    with pytest.raises(diff.DiffError, match="another engine"):
        diff.load_side(root, artifact_root=tmp_path)
    premises_for("premised", tmp_path, engine=own, registry_sha256="f" * 64)
    with pytest.raises(diff.DiffError, match="another registry"):
        diff.load_side(root, artifact_root=tmp_path)


def test_premises_on_one_side_only_flag_construction():
    record = {"checks": {"annual_value_matches_30_april_sample": {"holds": False}}}
    premises = {"events": {EVENT: {"measures": {KEY: record}}}}
    details, _ = diff._premise_details(EVENT, KEY, 2024, premises, None)
    assert [d["code"] for d in details] == ["premises_on_base_only"]
    details, _ = diff._premise_details(EVENT, KEY, 2024, None, premises)
    assert [d["code"] for d in details] == ["premises_on_head_only"]
    assert diff._premise_details(EVENT, KEY, 2024, None, None) == ([], {})


@st.composite
def replay_sides(draw):
    """Small sides for the pure diff's order, symmetry and membership properties."""
    supported = sorted(draw(st.sets(st.sampled_from([2024, 2025]), min_size=1)))
    included = draw(
        st.sets(
            st.sampled_from(
                [
                    f"{prefix}_{year}"
                    for year in (2024, 2025)
                    for prefix in ("tax", "benefit", "corporation")
                ]
            )
        )
    )
    gains = {
        year: {
            variable: float(draw(st.integers(-200, 200)) * 1_000_000)
            for variable in ("income_tax", "universal_credit")
        }
        for year in (2024, 2025)
    }
    m = measure()
    m["source_rows"] = [
        source for source in m["source_rows"] if source["source_row_id"] in included
    ]
    registry = {"calendar_years": [2024, 2025], "measures": [m]}
    registry_sha256 = hashlib.sha256(compute.canonical_bytes(registry)).hexdigest()
    rows = {}
    for source in m["source_rows"]:
        source_id = source["source_row_id"]
        year = int(source["fy"][:4])
        noncomputable = source.get("classification") == "out_of_household_scope"
        variable = (
            "income_tax" if source["tax_head"] == "Income tax" else "universal_credit"
        )
        value = (
            None if noncomputable or year not in supported else gains[year][variable]
        )
        rows[source_id] = {
            "measure_key": KEY,
            "year": year,
            "fy": source["fy"],
            "tax_head": source["tax_head"],
            "classification": source.get("classification", "partial"),
            "pe_value_gbp": value,
            "obr_value_gbp": source["value_gbp"],
            "head_variables": [] if noncomputable else [variable],
            "status": "out_of_household_scope" if noncomputable else "computed",
            "ratio_bin": None if value is None else "synthetic_bin",
        }
    artifacts = {
        (KEY, year): {
            "path": f"synthetic/{KEY}_{year}.json",
            "sha256": "a" * 64,
            "artifact": {
                "schema_version": 3,
                "measure_total_gbp": sum(gains[year].values()),
                "head_effects": gains[year],
                "head_channels": {"income_tax": "tax", "universal_credit": "spending"},
                "head_definitions": {},
                "construction": "reversal_on_certified_world",
                "baseline_world": {"reform_dict": {"gov.tax.rate": 0.2}},
                "reform_world": {"reform_dict": None},
            },
        }
        for year in supported
    }
    identity = {
        "variant_id": "synthetic_variant",
        "policyengine_version": "6",
        "policyengine_uk_version": "2",
        "policyengine_core_version": "3",
        "data_bundle": "synthetic_build",
        "certified_dataset_sha256": "a" * 64,
    }
    return {
        "root": Path("/tmp/synthetic"),
        "artifact_root": Path("/tmp"),
        "identity": identity,
        "premises": None,
        "premises_sha256": None,
        "events": {
            EVENT: {
                "rows": rows,
                "artifacts": artifacts,
                "registry": registry,
                "registry_sha256": registry_sha256,
                "registry_path": "registry.json",
                "registry_years": [2024, 2025],
                "supported_years": supported,
                "inert_pairs": set(),
                "inputs": {},
            }
        },
    }


def record_key(record):
    return (
        record["event"],
        record["measure_key"],
        record["year"],
        record["level"],
        record["key"],
    )


@settings(max_examples=100, deadline=None)
@given(replay_sides())
def test_identical_sides_have_no_flags(side):
    result = diff.diff_sides(side, copy.deepcopy(side))
    assert not any(record["flags"] for record in result["rows"])


@settings(max_examples=100, deadline=None)
@given(replay_sides(), replay_sides())
def test_swapping_sides_preserves_flags_and_mirrors_values(base, head):
    forward = {record_key(row): row for row in diff.diff_sides(base, head)["rows"]}
    backward = {record_key(row): row for row in diff.diff_sides(head, base)["rows"]}
    assert forward.keys() == backward.keys()
    for key, row in forward.items():
        reverse = backward[key]
        assert row["flags"] == reverse["flags"]
        assert row["base_gbp"] == reverse["head_gbp"]
        assert row["head_gbp"] == reverse["base_gbp"]
        assert row["delta_gbp"] == (
            None if reverse["delta_gbp"] is None else -reverse["delta_gbp"]
        )


@settings(max_examples=100, deadline=None)
@given(replay_sides(), replay_sides())
def test_every_source_row_on_either_side_has_one_source_record(base, head):
    result = diff.diff_sides(base, head)
    expected = set(base["events"][EVENT]["rows"]) | set(head["events"][EVENT]["rows"])
    source_keys = [row["key"] for row in result["rows"] if row["level"] == "source_row"]
    assert set(source_keys) == expected
    assert len(source_keys) == len(expected)


@settings(max_examples=100, deadline=None)
@given(replay_sides(), replay_sides())
def test_every_flagged_record_belongs_to_exactly_one_packet(base, head):
    result = diff.diff_sides(base, head)
    packets = diff.build_packets(result, base, head)
    for record in result["rows"]:
        if record["flags"]:
            assert (
                sum(
                    record_key(candidate) == record_key(record)
                    for packet in packets.values()
                    for candidate in packet["records"]
                )
                == 1
            )


@settings(max_examples=100, deadline=None)
@given(replay_sides(), replay_sides())
def test_coverage_flags_require_shared_year_support(base, head):
    for record in diff.diff_sides(base, head)["rows"]:
        if "coverage" in record["flags"]:
            assert all(
                record["year"] in side["events"][record["event"]]["supported_years"]
                for side in (base, head)
            )


@settings(max_examples=100, deadline=None)
@given(replay_sides(), replay_sides())
def test_rows_without_counterparts_never_have_support_flags(base, head):
    for record in diff.compare_source_rows(
        EVENT, base["events"][EVENT], head["events"][EVENT]
    ):
        if record["key"].startswith("corporation_"):
            assert "support" not in record["flags"]


finite = st.floats(min_value=-1e13, max_value=1e13, allow_nan=False)


@settings(max_examples=500, deadline=None)
@given(finite, finite)
def test_threshold_is_symmetric_and_strict(base, head):
    assert diff.numerically_moved(base, head) == diff.numerically_moved(head, base)
    threshold = diff.numerical_threshold(base, head)
    assert threshold >= diff.NUMERICAL_FLOOR_GBP
    assert diff.numerically_moved(base, head) == (abs(head - base) > threshold)


@settings(max_examples=300, deadline=None)
# Whole pounds: below 2**53 their sums are exact, so "a move of exactly the
# floor" is exactly the floor (with arbitrary floats, m + floor - m can round
# above it).
@given(st.integers(min_value=0, max_value=10**12).map(float))
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


def test_removed_measure_packet_retains_base_source_evidence(ns):
    base = ns("base")
    head = ns("head", remove_measure=True)
    packets = diff.build_packets(diff.diff_sides(base, head), base, head)
    packet = packets[f"{EVENT}__tax_and_benefit__2024"]
    assert "coverage" in packet["flags"]
    assert packet["title"] == measure()["title"]
    assert packet["measures"]["base"] == measure()
    assert packet["measures"]["head"] is None
    assert [
        (cell["side"], cell["source_row_id"]) for cell in packet["source_cells"]
    ] == [
        ("base", "tax_2024"),
        ("base", "benefit_2024"),
        ("base", "corporation_2024"),
    ]
    assert packet["cited_sources"] == [
        {"side": "base", "url": "https://www.gov.uk/example"}
    ]
    markdown = diff.render_packet_markdown("removed", packet)
    assert "| base | tax_2024" in markdown
    assert "* base: https://www.gov.uk/example" in markdown


def test_packets_keep_each_sides_changed_cells_and_citations(ns):
    base = ns("base")
    head = ns(
        "head",
        effects={
            2024: {"income_tax": 300e6, "universal_credit": -30e6},
            2025: {"income_tax": 110e6, "universal_credit": -33e6},
        },
    )
    head_measure = head["events"][EVENT]["registry"]["measures"][0]
    head_measure["title"] = "Updated announcement: https://www.gov.uk/updated"
    head_measure["source_rows"][0]["value_gbp"] = 125
    head_measure["source_rows"][0]["source_column"] = "Updated column"
    packets = diff.build_packets(diff.diff_sides(base, head), base, head)
    packet = packets[f"{EVENT}__tax_and_benefit__2024"]
    tax_cells = [c for c in packet["source_cells"] if c["source_row_id"] == "tax_2024"]
    assert [(c["side"], c["obr_value_gbp"], c["source_column"]) for c in tax_cells] == [
        ("base", 100, "C"),
        ("head", 125, "Updated column"),
    ]
    assert packet["cited_sources"] == [
        {"side": "base", "url": "https://www.gov.uk/example"},
        {"side": "head", "url": "https://www.gov.uk/updated"},
    ]


def test_reproduction_uses_each_verified_registry_and_variant(ns, tmp_path):
    base = ns("base")
    head = ns("head", modifier=0.25, variant="pe6_uk2_build")
    packet = diff.build_packets(diff.diff_sides(base, head), base, head)[
        f"{EVENT}__tax_and_benefit__2024"
    ]
    for label, side in (("base", base), ("head", head)):
        argv = shlex.split(packet["reproduce"][label])
        registry_path = Path(argv[argv.index("--registry") + 1])
        # Receipt-relative (review of 8700d29, C): runs from any checkout's
        # root, and packet bytes do not depend on the rendering machine.
        assert not registry_path.is_absolute()
        assert str(registry_path) == side["events"][EVENT]["registry_path"]
        assert (
            hashlib.sha256((tmp_path / registry_path).read_bytes()).hexdigest()
            == side["events"][EVENT]["registry_sha256"]
        )
        assert argv[argv.index("--variant") + 1] == side["identity"]["variant_id"]
    assert packet["reproduce"]["base"] != packet["reproduce"]["head"]


def test_committed_reproduction_command_is_accepted_by_compute_cli(
    monkeypatch, tmp_path
):
    side = diff.load_side(diff.ROOT / "results" / "uk" / "events")
    event = "autumn_budget_2024"
    key, year = next(iter(side["events"][event]["artifacts"]))
    argv = shlex.split(diff._reproduce(side, event, key, year))[3:]
    argv[argv.index("--output-dir") + 1] = str(tmp_path / "reproduction")

    def unavailable_engine():
        raise ImportError("This regression checks the engine-free plan only")

    monkeypatch.setattr(compute.worlds, "engine_resolver", unavailable_engine)
    assert compute.main(argv + ["--dry-run"]) == 0


def test_the_variants_file_reaches_staging(ns, tmp_path, monkeypatch):
    # A qualification run diffs a candidate whose record is only in its work
    # variants file; the diff must check each manifest against that file.
    ns("base", variant="pe6_uk2_build")
    seen = []
    real = stage.stage_event

    def spy(*args, **kwargs):
        seen.append(kwargs.get("variants_path"))
        return real(*args, **kwargs)

    monkeypatch.setattr(stage, "stage_event", spy)
    work = tmp_path / "work-variants.json"
    diff.load_side(tmp_path / "ns" / "base", artifact_root=tmp_path, variants_path=work)
    assert seen == [work]
    seen.clear()
    diff.load_side(tmp_path / "ns" / "base", artifact_root=tmp_path)
    assert seen == [stage.variants.VARIANTS_PATH]
