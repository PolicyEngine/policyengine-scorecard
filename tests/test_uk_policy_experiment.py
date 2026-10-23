"""Policy experiments on the modern population (docs/uk_replay/POLICY_EXPERIMENTS.md).

Engine-free: the specs, the population records, the OBR side, the
classification and the separation from replays. The invariants are the ones
the design states; Hypothesis checks them for every input it draws.
"""

from __future__ import annotations

import copy
import json
import math
from decimal import Decimal
from pathlib import Path

import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st

from pipeline import modal_uk_experiment as modal_experiment
from pipeline import uk_experiment_obr_bases as obr_bases
from pipeline import uk_experiment_specs as specs_builder
from pipeline import uk_policy_experiment as ex

ROOT = Path(__file__).resolve().parent.parent
EVENTS = sorted(
    path.stem
    for path in ex.SPEC_DIR.glob("*.json")
    if path.stem not in ("populations", "diagnoses", "obr_head_forecasts")
)


def spec_and_registry(event):
    spec = ex.load_spec(event)
    registry, _ = ex.load_registry(spec)
    return spec, registry


# --- specs --------------------------------------------------------------------


def test_specs_are_the_builders_output():
    built = specs_builder.build()
    assert sorted(built) == sorted(f"{event}.json" for event in EVENTS)
    for name, payload in built.items():
        assert (ex.SPEC_DIR / name).read_bytes() == payload, name


@pytest.mark.parametrize("event", EVENTS)
def test_every_spec_validates_against_its_bound_registry(event):
    spec, registry = spec_and_registry(event)
    ex.validate_spec(spec, registry, ex.load_bases())
    assert spec["label"] == ex.LABEL
    assert spec["label_text"] == ex.label_text(registry["event_name"])
    assert "not a replay" in spec["label_text"]


def test_a_spec_never_edits_or_replaces_its_registry():
    for event in EVENTS:
        _, registry = spec_and_registry(event)
        # Historical registries keep refusing replays.
        from pipeline import compute_uk_event

        if registry.get("execution"):
            with pytest.raises(ValueError):
                compute_uk_event.refuse_unexecutable(registry, event)
        assert not (ex.SPEC_DIR / f"{event}.json").name.endswith("_measures.json")


@pytest.mark.parametrize(
    "mutation, message",
    [
        (
            lambda e: e.update(construction="reversal_on_certified_world"),
            "construction",
        ),
        (lambda e: e.update(magnitude_check="sign_only"), "magnitude_reason"),
        (lambda e: e["heads"][0].update(obr_heads=["Not a head"]), "no source row"),
        (
            lambda e: e.update(reform={"gov.x": {"2024-04-06.2024-12-31": 1.0}}),
            "1 January",
        ),
        (lambda e: e.update(mirror_of="no colon"), "mirror_of"),
        (lambda e: e.update(sources=[]), "sources"),
        (
            lambda e: e["assumes_modern"].pop(min(e["assumes_modern"])),
            "no current law stated",
        ),
        (
            lambda e: e.update(set_outright={min(e["assumes_modern"]): "why"}),
            "both assumed and set outright",
        ),
        (
            lambda e: e.update(set_outright={min(e["reform"]): " "}),
            "set_outright must map paths to reasons",
        ),
        (
            lambda e: e.update(set_outright={"gov.not.set": "why"}),
            "does not set",
        ),
    ],
)
def test_validate_spec_refuses_a_broken_experiment(mutation, message):
    spec, registry = spec_and_registry("autumn_statement_2022")
    broken = copy.deepcopy(spec)
    mutation(broken["experiments"][0])
    with pytest.raises(ex.ExperimentError, match=message):
        ex.validate_spec(broken, registry, ex.load_bases())


def test_validate_spec_refuses_another_label():
    spec, registry = spec_and_registry("autumn_statement_2022")
    for field, value in (
        ("label", "replay"),
        ("kind", "replay"),
        ("label_text", "A replay."),
    ):
        broken = {**spec, field: value}
        with pytest.raises(ex.ExperimentError):
            ex.validate_spec(broken, registry, ex.load_bases())


def test_mirrors_name_each_other_with_the_same_reform_and_opposite_constructions():
    experiments = {
        f"{event}:{e['experiment_id']}": e
        for event in EVENTS
        for e in ex.load_spec(event)["experiments"]
    }
    mirrored = {k: e for k, e in experiments.items() if e.get("mirror_of")}
    assert mirrored
    for key, experiment in mirrored.items():
        other = experiments[experiment["mirror_of"]]
        assert other.get("mirror_of") == key
        assert other["reform"] == experiment["reform"]
        assert {other["construction"], experiment["construction"]} == set(
            ex.CONSTRUCTIONS
        )


# --- the OBR side ---------------------------------------------------------------


@pytest.mark.parametrize("event", EVENTS)
def test_mapped_and_unmapped_obr_values_conserve_the_fiscal_year(event):
    spec, registry = spec_and_registry(event)
    measures = {m["measure_key"]: m for m in registry["measures"]}
    for experiment in spec["experiments"]:
        measure = measures[experiment["measure_key"]]
        mapped = [h for head in experiment["heads"] for h in head["obr_heads"]]
        for fy in sorted({row["fy"] for row in measure["source_rows"]}):
            values = ex.obr_values(measure, fy, mapped)
            total = sum(
                (
                    Decimal(r["value_gbp_decimal"])
                    for r in measure["source_rows"]
                    if r["fy"] == fy
                ),
                Decimal(0),
            )
            assert (
                Decimal(values["mapped_decimal"]) + Decimal(values["unmapped_decimal"])
                == total
            )
            groups = ex.obr_for(experiment, measure, fy)["groups"]
            assert math.isclose(
                sum(g["obr_mapped_gbp"] for g in groups),
                values["mapped_gbp"],
                abs_tol=1e-3,
            )


def test_obr_head_forecasts_cover_each_event_vintage_and_only_forecasts():
    bases = ex.load_bases()
    assert (
        bases["source"]["march_2025"]["sha256"]
        == obr_bases.SOURCES["march_2025"]["sha256"]
    )
    for event in EVENTS:
        vintage = ex.load_spec(event)["obr_forecast_vintage"]
        assert bases["forecasts"]["IT"][vintage], vintage
    cells = set()
    for sheet, vintages in bases["forecasts"].items():
        assert sheet in bases["sheets"]
        for vintage, values in vintages.items():
            assert obr_bases.VINTAGE.match(vintage)
            for fy, cell in values.items():
                assert obr_bases.FY.match(fy)
                assert math.isfinite(cell["value_gbp_bn"])
                assert cell["cell"].startswith(f"{sheet}!")
                assert cell["cell"] not in cells
                cells.add(cell["cell"])
    # The locked edition names these vintages for the three events.
    locks = ROOT / "data" / "uk" / "events" / "vintage_locks"
    for path in locks.glob("*.json"):
        lock = json.loads(path.read_bytes())
        hofd = next(s for s in lock["sources"] if s["role"] == "hofd_row")
        assert hofd["sha256"] == obr_bases.SOURCES["march_2025"]["sha256"]


def test_obr_head_forecasts_rebuild_identically_when_the_editions_are_present():
    downloads = obr_bases.DOWNLOADS
    if not all((downloads / s["file"]).exists() for s in obr_bases.SOURCES.values()):
        pytest.skip(
            "the forecasts database editions are not in this checkout's harvest"
        )
    pytest.importorskip("openpyxl")
    assert (
        obr_bases.canonical_bytes(obr_bases.build(downloads))
        == ex.OBR_BASES_PATH.read_bytes()
    )


@given(
    obr=st.floats(-5e10, 5e10, allow_nan=False),
    pe_base=st.one_of(st.none(), st.floats(1e8, 1e12)),
)
def test_group_scale_is_positive_and_names_its_basis(obr, pe_base):
    bases = ex.load_bases()
    for comparable in (True, False):
        head = {"base_sheet": "IT", "pe_base_comparable": comparable}
        scale = ex.group_scale(
            head, pe_base=pe_base, bases=bases, vintage="November 2022", fy="2024-25"
        )
        assert scale["factor"] > 0
        if comparable and pe_base is not None:
            assert scale["basis"] == "pe_base_over_obr_event_forecast"
            assert math.isclose(
                scale["factor"] * scale["obr_event_forecast_gbp"], pe_base
            )
        else:
            assert scale["basis"] == "obr_newest_over_obr_event_forecast"
    unscaled = ex.group_scale(
        {"base_sheet": None},
        pe_base=pe_base,
        bases=bases,
        vintage="November 2022",
        fy="2024-25",
    )
    assert unscaled == {"basis": "unscaled", "factor": 1.0, "base_sheet": None}


# --- orientation and head sums ---------------------------------------------------


@given(
    raw=st.floats(-1e12, 1e12, allow_nan=False),
    channel=st.sampled_from(["tax", "spending"]),
)
def test_reversal_and_forward_constructions_are_exact_negatives(raw, channel):
    _, reversal = ex.orient(raw, channel, "reversal_on_modern_law")
    _, forward = ex.orient(raw, channel, "forward_on_modern_law")
    assert reversal == -forward
    _, tax = ex.orient(raw, "tax", "forward_on_modern_law")
    _, spending = ex.orient(raw, "spending", "forward_on_modern_law")
    assert tax == -spending


@given(
    values=st.lists(
        st.tuples(st.floats(0, 1e11), st.floats(0, 1e11)), min_size=4, max_size=4
    ),
    construction=st.sampled_from(sorted(ex.CONSTRUCTIONS)),
)
def test_an_experiments_total_is_the_sum_of_its_head_groups(values, construction):
    names = ["a", "b", "c", "d"]
    experiment = {
        "experiment_id": "x",
        "construction": construction,
        "heads": [
            {"obr_heads": ["A"], "pe_variables": ["a", "b"], "channel": "tax"},
            {"obr_heads": ["B"], "pe_variables": ["c"], "channel": "spending"},
            {"obr_heads": ["C"], "pe_variables": ["d"], "channel": "tax"},
        ],
    }
    modern = {n: v[0] for n, v in zip(names, values)}
    alternate = {n: v[1] for n, v in zip(names, values)}
    effects = ex.head_effects(experiment, modern, alternate)
    assert effects["effect_gbp"] == math.fsum(
        g["effect_gbp"] for g in effects["groups"]
    )
    swapped = {
        **experiment,
        "construction": next(c for c in ex.CONSTRUCTIONS if c != construction),
    }
    assert (
        ex.head_effects(swapped, modern, alternate)["effect_gbp"]
        == -effects["effect_gbp"]
    )


# --- classification ---------------------------------------------------------------


def artifact(effect, *, changes=True, reached=True, status="computed"):
    return {
        "status": status,
        "effect_gbp": effect,
        "parameters": {
            "gov.x": {"changes_modern_law": changes, "reached_simulation": reached}
        },
    }


def obr(mapped, unmapped=0.0, groups=None):
    return {
        "mapped_gbp": mapped,
        "unmapped_gbp": unmapped,
        "groups": groups if groups is not None else [{"obr_mapped_gbp": mapped}],
    }


ONE = [{"factor": 1.0, "basis": "unscaled"}]
money = st.floats(-1e11, 1e11, allow_nan=False, allow_infinity=False)


@given(
    pe=money,
    mapped=money,
    unmapped=money,
    factor=st.floats(0.2, 5.0),
    check=st.sampled_from(ex.MAGNITUDE_CHECKS),
)
def test_classify_is_pure_and_codes_have_severities(
    pe, mapped, unmapped, factor, check
):
    scales = [{"factor": factor}]
    first = ex.classify(
        artifact(pe), obr=obr(mapped, unmapped), scales=scales, magnitude_check=check
    )
    second = ex.classify(
        artifact(pe), obr=obr(mapped, unmapped), scales=scales, magnitude_check=check
    )
    assert first == second
    for code in first["codes"]:
        assert ex.severity(code, first) in ("investigate", "check", "note")


@given(pe=money, mapped=money, unmapped=money, factor=st.floats(0.2, 5.0))
def test_negating_both_sides_leaves_the_codes_unchanged(pe, mapped, unmapped, factor):
    scales = [{"factor": factor}]
    one = ex.classify(
        artifact(pe), obr=obr(mapped, unmapped), scales=scales, magnitude_check="scaled"
    )
    two = ex.classify(
        artifact(-pe),
        obr=obr(-mapped, -unmapped),
        scales=scales,
        magnitude_check="scaled",
    )
    assert one["codes"] == two["codes"]


@given(
    pe=st.floats(1e9, 1e11),
    mapped=st.floats(1e9, 1e11),
    sign=st.sampled_from([1, -1]),
    k=st.floats(1.0, 50.0),
)
def test_scaling_both_sides_above_the_floors_leaves_the_codes_unchanged(
    pe, mapped, sign, k
):
    one = ex.classify(
        artifact(sign * pe), obr=obr(mapped), scales=ONE, magnitude_check="scaled"
    )
    two = ex.classify(
        artifact(sign * pe * k),
        obr=obr(mapped * k),
        scales=ONE,
        magnitude_check="scaled",
    )
    assert one["codes"] == two["codes"]


@given(
    ratio=st.floats(1e-4, 1e4),
    further=st.floats(1.0, 100.0),
    mapped=st.floats(1e9, 1e10),
)
def test_a_ratio_further_from_one_than_a_flagged_one_is_flagged(ratio, further, mapped):
    def codes(r):
        return set(
            ex.classify(
                artifact(r * mapped),
                obr=obr(mapped),
                scales=ONE,
                magnitude_check="scaled",
            )["codes"]
        )

    assume(r_ok := abs(math.log(ratio)) > 1e-9)
    beyond = ratio * further if ratio > 1 else ratio / further
    assume(r_ok and mapped * min(ratio, beyond) >= ex.MOVE_FLOOR)
    flagged = codes(ratio) & {"magnitude_outside_3x", "magnitude_outside_10x"}
    if flagged:
        assert codes(beyond) & {"magnitude_outside_3x", "magnitude_outside_10x"}
    if "magnitude_outside_10x" in flagged:
        assert "magnitude_outside_10x" in codes(beyond)


@given(pe=money, mapped=money)
def test_crash_inert_and_noop_exclude_sign_and_magnitude_codes(pe, mapped):
    crashed = ex.classify(
        artifact(pe, status="crashed"),
        obr=obr(mapped),
        scales=ONE,
        magnitude_check="scaled",
    )
    assert crashed["codes"] == ["crash"]
    noop = ex.classify(
        artifact(pe, changes=False),
        obr=obr(mapped),
        scales=ONE,
        magnitude_check="scaled",
    )
    assert noop["codes"] == ["construction_noop"]
    small = ex.classify(
        artifact(ex.MOVE_FLOOR / 2),
        obr=obr(mapped),
        scales=ONE,
        magnitude_check="scaled",
    )
    assert small["codes"] == ["inert"]
    assert small["inert_severity"] == (
        "investigate" if abs(mapped) >= ex.SIGN_MIN_OBR else "check"
    )


def test_classify_examples():
    def codes(pe, mapped, unmapped=0.0, **kwargs):
        return ex.classify(
            artifact(pe, **kwargs),
            obr=obr(mapped, unmapped),
            scales=ONE,
            magnitude_check="scaled",
        )["codes"]

    assert codes(1e9, 1e9) == []
    assert codes(-1e9, 1e9) == ["sign_mismatch"]
    assert codes(4e9, 1e9) == ["magnitude_outside_3x"]
    assert codes(11e9, 1e9) == ["magnitude_outside_10x"]
    assert codes(0.05e9, 1e9) == ["magnitude_outside_10x"]
    assert codes(4e9, 1e9, unmapped=3e9) == []  # mapped heads hold under half
    assert codes(2e8, 0.0) == ["obr_zero_pe_moves"]
    assert codes(1e9, 1e9, reached=False) == ["reform_not_applied"]
    assert codes(-3e6, 1e9) == []  # opposite sign below the sign floors
    sign_only = ex.classify(
        artifact(40e9), obr=obr(1e9), scales=ONE, magnitude_check="sign_only"
    )
    assert sign_only["codes"] == []


# --- separation from replays -------------------------------------------------------


paths = st.lists(
    st.sampled_from(
        [
            "results",
            "uk",
            "events",
            "replays",
            "Results",
            "UK",
            "Events",
            "REPLAYS",
            "experiments",
            "..",
            "x",
            "exp-a",
            "autumn_statement_2022",
            ".venv-replay-checks",
        ]
    ),
    min_size=0,
    max_size=6,
)


@given(parts=paths, where=st.sampled_from(["root", "cased", "elsewhere"]))
@settings(max_examples=300)
def test_no_output_directory_resolves_into_a_replay_root(
    parts, where, tmp_path_factory
):
    root = tmp_path_factory.mktemp("repo")
    base = {
        "root": root,
        "cased": root.parent / root.name.upper(),
        "elsewhere": Path("/elsewhere"),
    }[where]
    requested = base.joinpath(*parts)
    try:
        chosen = ex.contained_output_dir(
            "exp-a", "autumn_statement_2022", requested, root=root
        )
    except ex.ExperimentError:
        return
    for replay in ex.REPLAY_ROOTS:
        assert not chosen.is_relative_to((root / replay).resolve())
        segments = tuple(part.casefold() for part in Path(replay).parts)
        folded = tuple(part.casefold() for part in chosen.parts)
        assert all(
            folded[i : i + len(segments)] != segments for i in range(len(folded))
        )
    if ex._within_casefolded(chosen, root.resolve()):
        assert chosen.is_relative_to(
            (root / ex.RESULT_ROOT / "exp-a" / "autumn_statement_2022").resolve()
        ) or chosen.is_relative_to((root / ".venv-replay-checks").resolve())


def test_every_value_a_construction_sets_states_its_current_law():
    """For every planned year, each reform path is assumed or set outright,
    so an engine whose current law differs is flagged on any population."""
    from pipeline import uk_construction_revisions as revisions

    for event in EVENTS:
        spec, registry = spec_and_registry(event)
        for experiment in spec["experiments"]:
            assumed = experiment.get("assumes_modern") or {}
            outright = experiment.get("set_outright") or {}
            for path in experiment["reform"]:
                if path in outright:
                    continue
                for year in ex.planned_years(experiment, registry):
                    date = f"{year}-01-01"
                    if revisions.window_value(experiment["reform"], path, date)[0]:
                        assert revisions.window_value(assumed, path, date)[0], (
                            experiment["experiment_id"],
                            path,
                            year,
                        )


def test_the_grid_is_the_planned_years_the_data_covers():
    population = {"data_years": [2024, 2025]}
    registry = {"calendar_years": [2023, 2024, 2025, 2026]}
    assert ex.planned_years({}, registry) == [2023, 2024, 2025, 2026]
    assert ex.experiment_grid_years({}, registry, population) == [2024, 2025]
    limited = {"years": [2025, 2026]}
    assert ex.experiment_grid_years(limited, registry, population) == [2025]
    carried = {"carried_from_fy": "2019-20", "years": [2026, 2024]}
    assert ex.planned_years(carried, registry) == [2024, 2026]
    assert ex.experiment_grid_years(carried, registry, population) == [2024]


def test_a_cased_spelling_of_the_checkout_is_still_the_repository(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    cased = root.parent / "REPO" / "data" / "uk" / "events" / "x"
    with pytest.raises(ex.ExperimentError, match="inside the repository"):
        ex.contained_output_dir("exp-a", "autumn_statement_2022", cased, root=root)


def test_two_brackets_of_one_scale_may_not_share_a_threshold():
    # A zero-width band is not empty: policyengine adds the rates of brackets
    # that share a threshold (a £1m additional dwelling taxed at 13% above
    # £250,000 instead of 8%).
    spec, registry = spec_and_registry("autumn_statement_2022")
    broken = copy.deepcopy(spec)
    experiment = next(
        e
        for e in broken["experiments"]
        if e["experiment_id"] == "as2022_sdlt_end_growth_plan_relief"
    )
    scale = "gov.hmrc.stamp_duty.residential.purchase.additional.rate"
    window = "2025-01-01.2035-12-31"
    experiment["reform"][f"{scale}[1].threshold"] = {window: 250_000.0}
    experiment["reform"][f"{scale}[2].threshold"] = {window: 250_000.0}
    experiment["assumes_modern"][f"{scale}[1].threshold"] = {window: 125_000.0}
    experiment["assumes_modern"][f"{scale}[2].threshold"] = {window: 250_000.0}
    with pytest.raises(ex.ExperimentError, match="share the threshold"):
        ex.validate_spec(broken, registry, ex.load_bases())


def test_a_crash_keeps_modern_law_differs():
    crashed = {"status": "crashed"}
    codes = ex.classify(
        crashed,
        obr=obr(1e9),
        scales=ONE,
        magnitude_check="scaled",
        assumption_failures=[{"path": "gov.a"}],
    )["codes"]
    assert codes == ["crash", "modern_law_differs"]
    assert ex.classify(crashed, obr=obr(1e9), scales=ONE, magnitude_check="scaled")[
        "codes"
    ] == ["crash"]


def test_another_checkouts_replay_root_is_refused_too(tmp_path):
    root = tmp_path / "repo"
    for replay in ex.REPLAY_ROOTS:
        for spelling in (replay, replay.upper(), replay.title()):
            elsewhere = tmp_path / "other-checkout" / spelling / "x"
            with pytest.raises(ex.ExperimentError, match="inside a replay root"):
                ex.contained_output_dir(
                    "exp-a", "autumn_statement_2022", elsewhere, root=root
                )


def test_the_canonical_output_directory_is_the_experiment_namespace():
    chosen = ex.contained_output_dir("exp-a", "autumn_statement_2022")
    assert (
        chosen
        == (ROOT / "results/uk/experiments/exp-a/autumn_statement_2022").resolve()
    )
    with pytest.raises(ex.ExperimentError):
        ex.contained_output_dir("pe6.9.0_uk2.130.1_x", "autumn_statement_2022")


def test_no_population_is_a_replay_variant():
    variants = json.loads((ROOT / "data/uk/replay_variants.json").read_bytes())
    variant_ids = {v["variant_id"] for v in variants["variants"]}
    document = ex.load_populations()
    for record in document["populations"]:
        assert record["population_id"].startswith("exp-")
        assert record["population_id"] not in variant_ids
        assert record["status"] == ex.POPULATION_STATUS
        assert record["status"] not in ("certified", "candidate", "retired")
        assert record["result_root"] == f"{ex.RESULT_ROOT}/{record['population_id']}"


def test_a_population_must_bind_installed_digests_before_it_runs():
    record = copy.deepcopy(ex.load_populations()["populations"][0])
    for package in record["identity"]["packages"].values():
        package["record_sha256"] = "pending_probe"
    with pytest.raises(ex.ExperimentError, match="probe"):
        ex.validate_population(record)
    for package in record["identity"]["packages"].values():
        package["record_sha256"] = "0" * 64
    ex.validate_population(record)
    record["status"] = "certified"
    with pytest.raises(ex.ExperimentError, match="status"):
        ex.validate_population(record)


def test_replay_readers_never_read_the_experiment_namespace():
    """The database build, the replay namespace scan and the results-PR
    builder name only replay roots; nothing but the experiment modules and
    their tests names results/uk/experiments or data/uk/experiments."""
    allowed = {
        "pipeline/uk_policy_experiment.py",
        "pipeline/modal_uk_experiment.py",
        "pipeline/uk_experiment_specs.py",
        "pipeline/uk_experiment_obr_bases.py",
        "tests/test_uk_policy_experiment.py",
    }
    for folder in ("pipeline", "scorecard_db", "tests", ".github"):
        for path in (ROOT / folder).rglob("*"):
            if not path.is_file() or path.suffix not in (".py", ".yml", ".yaml", ".sh"):
                continue
            relative = str(path.relative_to(ROOT))
            text = path.read_text(errors="ignore")
            if "uk/experiments" in text or "uk_policy_experiment" in text:
                assert relative in allowed, relative
    from pipeline import uk_replay_variants

    assert uk_replay_variants.REPLAY_RESULT_ROOT == "results/uk/replays"
    assert not ex.RESULT_ROOT.startswith(uk_replay_variants.REPLAY_RESULT_ROOT)


def test_every_artifact_carries_the_label(tmp_path):
    spec, registry = spec_and_registry("autumn_statement_2022")
    population = ex.load_populations()["populations"][0]
    experiment = spec["experiments"][0]
    modern = {"processed_parameter_values": {p: 0.0 for p in experiment["reform"]}}
    try:
        raise RuntimeError("boom\nsecond line")
    except RuntimeError as error:
        crashed = ex.crash_result(
            spec,
            registry,
            population,
            experiment,
            2024,
            modern=modern,
            error=error,
            registry_sha256="0" * 64,
        )
    assert crashed["error_message"] == "boom"
    for artifact_ in (
        crashed,
        ex.base_artifact(spec, registry, population, experiment, 2024),
    ):
        assert artifact_["label"] == ex.LABEL
        assert artifact_["is_replay"] is False
        assert artifact_["kind"] == ex.ARTIFACT_KIND
        assert "not a replay" in artifact_["label_text"]


# --- runs and findings -----------------------------------------------------------


def test_plan_runs_only_years_the_population_and_the_event_share():
    spec, registry = spec_and_registry("autumn_statement_2022")
    population = {"population_id": "exp-a", "data_years": list(range(2024, 2031))}
    planned = ex.plan(spec, registry, population)
    assert planned["years"] == [2024, 2025, 2026, 2027]
    assert planned["event_years_outside_population"] == [2022, 2023]
    assert planned["is_replay"] is False
    assert len(planned["grid"]) == 4 * len(spec["experiments"])
    with pytest.raises(ex.ExperimentError):
        ex.plan(spec, registry, population, years=[2023])


def test_mirror_findings_compare_only_shared_head_groups():
    specs = {event: ex.load_spec(event) for event in EVENTS}
    rows = []
    for event, spec in specs.items():
        sign = {"forward_on_modern_law": 1.0, "reversal_on_modern_law": -1.0}
        rows.append(
            {
                "event": event,
                "rows": [
                    {
                        "experiment_id": e["experiment_id"],
                        "year": 2024,
                        "group_effects_gbp": {
                            "+".join(h["pe_variables"]): sign[e["construction"]]
                            * (1e9 + 1e6 * i)
                            for i, h in enumerate(e["heads"])
                        },
                    }
                    for e in spec["experiments"]
                ],
            }
        )
    checks = ex.mirror_findings(rows, specs)
    assert checks and all(check["agrees"] for check in checks)
    # A group only one mirror maps (AS2022's Universal Credit) is not compared.
    assert not any(
        c["pe_variables"] == "universal_credit" and "hscl" in c["pair"][0]
        for c in checks
    )
    hscl = next(
        row
        for document in rows
        if document["event"] == "autumn_budget_2021"
        for row in document["rows"]
        if row["experiment_id"] == "ab2021_hscl_nics_plus_1_25pp"
    )
    key = next(iter(hscl["group_effects_gbp"]))
    hscl["group_effects_gbp"][key] *= 1.001
    assert not all(check["agrees"] for check in ex.mirror_findings(rows, specs))


def test_parameter_record_says_whether_a_construction_changes_modern_law():
    experiment = {
        "reform": {
            "gov.a": {"2024-01-01.2024-12-31": 2.0},
            "gov.b": {"2025-01-01.2030-12-31": 3.0},
        }
    }
    record = ex.parameter_record(
        experiment, 2024, {"gov.a": 1.0, "gov.b": 3.0}, {"gov.a": 2.0, "gov.b": 3.0}
    )
    assert (
        record["gov.a"]["changes_modern_law"] and record["gov.a"]["reached_simulation"]
    )
    assert not record["gov.b"]["changes_modern_law"]  # 2024 keeps modern law
    missed = ex.parameter_record(
        experiment, 2024, {"gov.a": 1.0, "gov.b": 3.0}, {"gov.a": 1.0, "gov.b": 3.0}
    )
    assert missed["gov.a"]["reached_simulation"] is False


def test_modal_request_refuses_a_replay_variant_and_downloads_stay_ignored():
    with pytest.raises(ValueError):
        modal_experiment.request_spec(
            "autumn_statement_2022",
            "pe6.9.0_uk2.130.1_x",
            years=[],
            experiments=[],
            probe=False,
        )
    request = modal_experiment.request_spec(
        "autumn_statement_2022", "exp-a", years=[2024], experiments=[], probe=False
    )
    assert request["is_replay"] is False and request["label"] == ex.LABEL
    payload = {"request": request, "inputs": {"files": []}}
    target = modal_experiment.download_dir(modal_experiment.DOWNLOAD_ROOT, payload)
    assert target.resolve().is_relative_to((ROOT / ".venv-replay-checks").resolve())
    other = {"request": request, "inputs": {"files": [{"path": "x", "sha256": "0"}]}}
    assert (
        modal_experiment.download_dir(modal_experiment.DOWNLOAD_ROOT, other) != target
    )
    with pytest.raises(ValueError):
        modal_experiment.download_dir("results/uk/replays", payload)


def test_the_modal_allowlist_names_files_that_exist():
    population = ex.load_populations()["populations"][0]
    for event in EVENTS:
        for relative in modal_experiment.repository_files(event, population):
            assert (ROOT / relative).is_file(), relative


def test_a_carried_forward_experiment_runs_its_named_years_against_its_named_fy():
    spec, registry = spec_and_registry("autumn_statement_2022")
    population = {"population_id": "exp-a", "data_years": list(range(2024, 2033))}
    experiment = copy.deepcopy(spec["experiments"][1])
    experiment.update(
        years=[2028, 2029], carried_from_fy="2027-28", carry_reason="steady state"
    )
    # The current law it assumes, stated for the years it now runs.
    for windows in experiment["assumes_modern"].values():
        windows["2028-01-01.2029-12-31"] = list(windows.values())[-1]
    carried = {**spec, "experiments": [experiment]}
    ex.validate_spec(carried, registry, ex.load_bases())
    planned = ex.plan(carried, registry, population)
    assert planned["years"] == [2028, 2029]
    assert ex.comparison_fy(experiment, registry, 2028) == "2027-28"
    assert ex.comparison_fy(experiment, registry, 2026) == "2026-27"
    bad = copy.deepcopy(experiment)
    bad["carried_from_fy"] = "2031-32"
    with pytest.raises(ex.ExperimentError, match="carried_from_fy"):
        ex.validate_spec({**spec, "experiments": [bad]}, registry, ex.load_bases())


def test_group_scale_reads_the_event_forecast_at_the_costing_year_and_newest_at_the_run_year():
    bases = ex.load_bases()
    head = {"base_sheet": "IT", "pe_base_comparable": False}
    scale = ex.group_scale(
        head,
        pe_base=None,
        bases=bases,
        vintage="November 2022",
        fy="2027-28",
        modern_fy="2029-30",
    )
    assert scale["obr_event_forecast_gbp"] == ex.forecast(
        bases, "IT", "November 2022", "2027-28"
    )
    assert (
        scale["obr_newest_forecast_gbp"]
        == ex.newest_forecast(bases, "IT", "2029-30")[1]
    )


def test_a_leg_without_an_obr_head_counts_toward_the_total_but_not_the_expectation():
    spec, registry = spec_and_registry("autumn_2010")
    experiment = spec["experiments"][0]
    assert [h["obr_heads"] for h in experiment["heads"]] == [
        ["Social security benefits"],
        [],
    ]
    broken = copy.deepcopy(spec)
    for head in broken["experiments"][0]["heads"]:
        head["obr_heads"] = []
    with pytest.raises(ex.ExperimentError, match="no head group maps an OBR head"):
        ex.validate_spec(broken, registry, ex.load_bases())
    measure = {m["measure_key"]: m for m in registry["measures"]}[
        experiment["measure_key"]
    ]
    obr = ex.obr_for(experiment, measure, "2015-16")
    assert obr["groups"][1]["obr_mapped_gbp"] == 0.0
    assert obr["mapped_gbp"] == obr["groups"][0]["obr_mapped_gbp"]


def test_offsetting_mapped_heads_still_count_as_mapped():
    obr_ = {
        "mapped_gbp": 185e6,
        "unmapped_gbp": 340e6,
        "by_head_gbp": {
            "NICs": 475e6,
            "Income tax": -290e6,
            "Corporation tax (onshore)": 340e6,
        },
        "groups": [
            {"obr_heads": ["NICs"], "obr_mapped_gbp": 475e6},
            {"obr_heads": ["Income tax"], "obr_mapped_gbp": -290e6},
        ],
    }
    assert math.isclose(ex.mapped_head_share(obr_), 765 / 1105)
    result = ex.classify(
        artifact(680e6),
        obr=obr_,
        scales=[{"factor": 1.0}, {"factor": 1.0}],
        magnitude_check="scaled",
    )
    assert result["codes"] == ["magnitude_outside_3x"]


@given(
    value=st.floats(1.0, 1e6), factor=st.floats(0.5, 2.0), year=st.integers(2024, 2032)
)
def test_a_scaled_path_runs_at_its_modern_value_times_its_factor(value, factor, year):
    experiment = {
        "experiment_id": "x",
        "reform": {"gov.a": {"2024-01-01.2035-12-31": 1.0}},
        "scale": {"gov.b": factor},
    }
    run = ex.executed(experiment, year, {"gov.a": 0.0, "gov.b": value})
    assert run["reform"]["gov.b"] == {f"{year}-01-01.{year}-12-31": value * factor}
    assert run["reform"]["gov.a"] == experiment["reform"]["gov.a"]
    record = ex.parameter_record(
        run,
        year,
        {"gov.a": 0.0, "gov.b": value},
        {"gov.a": 1.0, "gov.b": value * factor},
    )
    assert record["gov.b"]["reached_simulation"] and record["gov.b"][
        "changes_modern_law"
    ] == (factor != 1.0)
    assert ex.touched_paths(experiment) == ["gov.a", "gov.b"]
    with pytest.raises(ex.ExperimentError):
        ex.executed(experiment, year, {"gov.a": 0.0})


def test_an_engine_whose_current_law_differs_from_the_assumed_one_is_flagged():
    experiment = {
        "reform": {"gov.a": {"2025-01-01.2035-12-31": 0.02}},
        "assumes_modern": {"gov.a": {"2025-01-01.2035-12-31": 0.05}},
    }
    stale = {"year": 2025, "parameters": {"gov.a": {"modern_processed": 0.03}}}
    current = {"year": 2025, "parameters": {"gov.a": {"modern_processed": 0.05}}}
    assert ex.modern_assumption_failures(experiment, stale) == [
        {"path": "gov.a", "assumed": 0.05, "modern_processed": 0.03}
    ]
    assert ex.modern_assumption_failures(experiment, current) == []
    earlier = {"year": 2024, "parameters": {"gov.a": {"modern_processed": 0.03}}}
    assert (
        ex.modern_assumption_failures(experiment, earlier) == []
    )  # no assumption that year
    codes = ex.classify(
        artifact(1e9),
        obr=obr(1e9),
        scales=ONE,
        magnitude_check="scaled",
        assumption_failures=[{"path": "gov.a"}],
    )["codes"]
    assert codes == ["modern_law_differs"]
    assert ex.severity("modern_law_differs", {}) == "investigate"


def test_assumes_modern_may_only_name_touched_paths():
    spec, registry = spec_and_registry("autumn_2015")
    broken = copy.deepcopy(spec)
    broken["experiments"][0]["assumes_modern"] = {
        "gov.not.touched": {"2025-01-01.2035-12-31": 1.0}
    }
    with pytest.raises(ex.ExperimentError, match="untouched"):
        ex.validate_spec(broken, registry, ex.load_bases())


def committed_runs():
    root = ROOT / ex.RESULT_ROOT
    return sorted(
        (population.name, event.name)
        for population in root.glob("exp-*")
        for event in population.iterdir()
        if (event / "EXPERIMENT_MANIFEST.json").exists()
    )


@pytest.mark.parametrize("population, event", committed_runs())
def test_committed_findings_regenerate_byte_for_byte(population, event):
    directory = ROOT / ex.RESULT_ROOT / population / event
    document = ex.findings(event, population)
    assert ex.canonical_bytes(document) == (directory / "FINDINGS.json").read_bytes()
    assert ex.render_findings(document) == (directory / "FINDINGS.md").read_text()


@pytest.mark.parametrize("population", sorted({p for p, _ in committed_runs()}))
def test_committed_summaries_regenerate_byte_for_byte(population):
    root = ROOT / ex.RESULT_ROOT / population
    document = ex.summary(population)
    assert ex.canonical_bytes(document) == (root / "SUMMARY.json").read_bytes()
    assert ex.render_summary(document) == (root / "SUMMARY.md").read_text()


def test_engines_disagree_on_current_law_only_where_the_construction_says_so():
    """Where a model swap and its certified pair (the same data) differ on the
    current law of a parameter the construction sets that year, the
    construction either states the law it assumes (assumes_modern) or sets the
    parameter outright. Scaled paths follow each engine's own law by design."""
    from pipeline import uk_construction_revisions as revisions

    records = ex.load_populations()["populations"]
    checked = 0
    for swap in (r for r in records if r.get("pairing") == "model_swap"):
        pair = next(
            r
            for r in records
            if r.get("pairing") == "certified_pair"
            and r["identity"]["dataset"]["sha256"]
            == swap["identity"]["dataset"]["sha256"]
        )
        mine = ROOT / ex.RESULT_ROOT / swap["population_id"]
        theirs = ROOT / ex.RESULT_ROOT / pair["population_id"]
        for manifest in sorted(mine.glob("*/EXPERIMENT_MANIFEST.json")):
            event = manifest.parent.name
            if not (theirs / event / "EXPERIMENT_MANIFEST.json").exists():
                continue
            spec = json.loads(ex.spec_path(event).read_bytes())
            for experiment in spec["experiments"]:
                eid = experiment["experiment_id"]
                assumed = set(experiment.get("assumes_modern") or {})
                for year in range(2024, 2036):
                    name = f"{eid}_{year}.json"
                    if not (theirs / event / name).exists():
                        continue
                    a = json.loads((theirs / event / name).read_bytes())
                    b = json.loads((manifest.parent / name).read_bytes())
                    for path, record in a.get("parameters", {}).items():
                        found, _ = revisions.window_value(
                            experiment["reform"], path, f"{year}-01-01"
                        )
                        if not found:
                            continue
                        checked += 1
                        if (
                            record["modern_processed"]
                            == b["parameters"][path]["modern_processed"]
                        ):
                            continue
                        outright = experiment.get("set_outright") or {}
                        assert path in assumed or path in outright, (
                            event,
                            eid,
                            year,
                            path,
                        )
    assert checked


def test_findings_refuse_a_run_on_another_spec(tmp_path, monkeypatch):
    population, event = committed_runs()[0]
    source = ROOT / ex.RESULT_ROOT / population / event
    fake_root = tmp_path / "repo"
    target = fake_root / ex.RESULT_ROOT / population / event
    target.mkdir(parents=True)
    for path in source.glob("*.json"):
        (target / path.name).write_bytes(path.read_bytes())
    spec_target = fake_root / ex.spec_path(event).relative_to(ROOT)
    spec_target.parent.mkdir(parents=True)
    spec = json.loads(ex.spec_path(event).read_bytes())
    spec["experiments"][0]["note"] += " (edited)"
    spec_target.write_bytes(ex.canonical_bytes(spec))
    registry = fake_root / spec["registry"]["path"]
    registry.parent.mkdir(parents=True, exist_ok=True)
    registry.write_bytes((ROOT / spec["registry"]["path"]).read_bytes())
    with pytest.raises(ex.ExperimentError, match="another spec"):
        ex.findings(event, population, root=fake_root)


def test_adopt_copies_nothing_when_downloads_disagree(tmp_path, monkeypatch):
    def download(name, spec_sha):
        directory = tmp_path / name
        directory.mkdir()
        artifact_bytes = b"{}\n"
        (directory / "x_2024.json").write_bytes(artifact_bytes)
        manifest = {
            "registry_sha256": "r",
            "spec_sha256": spec_sha,
            "population_identity": {},
            "grid": [{"experiment_id": "x", "year": 2024}],
            "files": [
                {"path": "x_2024.json", "sha256": ex.sha256_bytes(artifact_bytes)}
            ],
        }
        (directory / "EXPERIMENT_MANIFEST.json").write_bytes(
            ex.canonical_bytes(manifest)
        )
        receipt = {
            "request": {"event": "autumn_2015", "population_id": "exp-a"},
            "files": {
                name_: ex.sha256_bytes((directory / name_).read_bytes())
                for name_ in ("x_2024.json", "EXPERIMENT_MANIFEST.json")
            },
        }
        (directory / "MODAL_RECEIPT.json").write_bytes(ex.canonical_bytes(receipt))
        return directory

    destination = tmp_path / "out"
    monkeypatch.setattr(
        ex, "contained_output_dir", lambda population, event: destination
    )
    with pytest.raises(ValueError, match="disagree"):
        modal_experiment.adopt(
            [download("a", "one"), download("b", "two")], "autumn_2015", "exp-a"
        )
    assert not destination.exists() or not any(destination.iterdir())
