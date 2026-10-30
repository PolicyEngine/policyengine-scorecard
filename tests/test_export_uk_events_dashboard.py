"""The dashboard export of certified UK event replays
(pipeline/export_uk_events_dashboard.py).

Invariants, for every committed export:

- it regenerates byte for byte from the sealed namespace and the registries;
- every registry measure appears once, computed exactly when the registry
  computes it and the seal holds its artifacts, one per supported year;
- a reversal undoes the measure in its baseline world and runs current law
  as its reform world; a forward delta does the opposite;
- each year's total is the sum of its declared heads' effects;
- the classes partition the source rows, so their absolute shares sum to
  exactly one; the computed rows are a subset of the computable classes';
- the document has a closed shape: no field beyond the schema's.

Properties of the helpers are checked over generated inputs, and the
accounting against an independent Fraction implementation. Tampered copies of
a sealed namespace are refused.
"""

import csv
import io
import json
import math
import re
import shutil
from decimal import Decimal
from fractions import Fraction
from importlib import metadata
from pathlib import Path
from types import SimpleNamespace

import pytest
from hypothesis import HealthCheck, example, given, settings
from hypothesis import strategies as st

from pipeline import export_uk_events_dashboard as export
from pipeline import uk_replay_interface as interface
from pipeline import uk_replay_variants as variants

ROOT = Path(__file__).resolve().parent.parent
EXPORTED = sorted(p.name for p in export.EXPORT_ROOT.iterdir() if p.is_dir())
# The variant the dashboard's first import reads.
FIRST = "pe6.9.0_uk2.130.1_policyengine-uk-data-1.58.1"
EVENT = "spring_statement_2025"


def documents(variant_id: str) -> dict[str, dict]:
    folder = export.EXPORT_ROOT / variant_id
    return {
        p.stem: json.loads(p.read_text())
        for p in sorted(folder.glob("*.json"))
        if p.name != export.EXPORT_MANIFEST
    }


ALL = [
    (variant_id, event, document)
    for variant_id in EXPORTED
    for event, document in documents(variant_id).items()
]


def registry_of(document: dict) -> dict:
    return json.loads((ROOT / document["event"]["registry_path"]).read_text())


def test_the_first_import_variant_is_exported():
    assert FIRST in EXPORTED


def test_recorded_scenario_capability_matches_the_installed_engine():
    # Engine-free CI skips this. Each replay-engine leg instead checks the
    # table's entry on its variant's engine (--check-scenario-capability in
    # ci.yml), which, unlike this test, passes an unrecorded engine whose
    # variant has no committed export
    try:
        version = metadata.version("policyengine-uk")
    except metadata.PackageNotFoundError:
        pytest.skip("policyengine-uk is not installed in this engine-free environment")
    assert version in export.SCENARIO_DATED_REFORMS, (
        f"Verify and record Scenario.dated_reforms for policyengine-uk {version}"
    )
    assert export.scenario_capability_problems() == []


def installed(monkeypatch, version: str | None, dated_reforms: bool = True) -> None:
    """Stand in for an installed engine of ``version``; None installs none."""

    def read(name: str) -> str:
        if version is None:
            raise metadata.PackageNotFoundError(name)
        return version

    monkeypatch.setattr(
        export,
        "metadata",
        SimpleNamespace(
            version=read, PackageNotFoundError=metadata.PackageNotFoundError
        ),
    )
    monkeypatch.setattr(
        export, "installed_scenario_dated_reforms", lambda: dated_reforms
    )


def exports_nothing(monkeypatch) -> None:
    def refuse(*args, **kwargs):
        raise AssertionError("the capability check exported")

    monkeypatch.setattr(export, "write_export", refuse)


def legacy_record() -> dict:
    document = variants.load_document()
    return next(v for v in document["variants"] if variants.is_legacy(v))


def test_the_capability_check_passes_a_recorded_engine_that_agrees(monkeypatch, capsys):
    installed(monkeypatch, "2.130.1", True)
    exports_nothing(monkeypatch)
    assert export.scenario_capability_problems(variants.get_variant(FIRST)) == []
    assert export.main(["--check-scenario-capability", "--variant", FIRST]) == 0
    assert "dated_reforms=True, as recorded" in capsys.readouterr().out


def test_the_capability_check_refuses_a_recorded_engine_that_disagrees(
    monkeypatch, capsys
):
    installed(monkeypatch, "2.130.1", False)
    exports_nothing(monkeypatch)
    (problem,) = export.scenario_capability_problems()
    assert "records dated_reforms=True" in problem and "gives False" in problem
    assert export.main(["--check-scenario-capability", "--variant", FIRST]) == 1
    assert "gives False" in capsys.readouterr().err


def test_the_capability_check_refuses_an_unrecorded_engine_only_for_an_exported_variant(
    monkeypatch, capsys
):
    legacy = legacy_record()
    installed(monkeypatch, legacy["identity"]["packages"]["policyengine-uk"]["version"])
    exports_nothing(monkeypatch)
    assert not (export.EXPORT_ROOT / legacy["variant_id"]).exists()
    assert export.scenario_capability_problems(legacy) == []
    check = ["--check-scenario-capability", "--variant", legacy["variant_id"]]
    assert export.main(check) == 0
    assert "is not recorded; the export refuses it" in capsys.readouterr().out
    monkeypatch.delitem(export.SCENARIO_DATED_REFORMS, "2.130.1")
    installed(monkeypatch, "2.130.1")
    assert export.scenario_capability_problems() == []
    (problem,) = export.scenario_capability_problems(variants.get_variant(FIRST))
    assert "has a committed export" in problem
    assert export.main(["--check-scenario-capability", "--variant", FIRST]) == 1


def test_the_capability_check_refuses_another_variants_engine_and_no_engine(
    monkeypatch, capsys
):
    exports_nothing(monkeypatch)
    installed(monkeypatch, "2.125.1")
    (problem,) = export.scenario_capability_problems(variants.get_variant(FIRST))
    assert "runs policyengine-uk 2.130.1, but 2.125.1 is installed" in problem
    installed(monkeypatch, None)
    assert export.scenario_capability_problems() == ["policyengine-uk is not installed"]
    assert export.main(["--check-scenario-capability", "--variant", FIRST]) == 1
    assert "not installed" in capsys.readouterr().err


def test_the_capability_check_defaults_to_the_newest_certified_variant(monkeypatch):
    seen = []
    monkeypatch.setattr(
        export, "scenario_capability_problems", lambda record: seen.append(record) or []
    )
    installed(monkeypatch, "2.130.1")
    exports_nothing(monkeypatch)
    assert export.main(["--check-scenario-capability"]) == 0
    assert seen == [export.default_variant(variants.load_document())]


def test_the_capability_check_asks_the_replays_own_route(monkeypatch):
    calls = []

    def route(reform, revision):
        calls.append((reform, revision))
        return routed(reform)

    monkeypatch.setattr(export.replay, "revision_reform_route", route)
    for routed, expected in [
        (lambda reform: reform, False),
        (
            lambda reform: {path: {"2024-04-06.2036-04-05": 0.1} for path in reform},
            True,
        ),
    ]:
        assert export.installed_scenario_dated_reforms() is expected
    assert (
        calls
        == [(export.CAPABILITY_PROBE, {"paths": list(export.CAPABILITY_PROBE)})] * 2
    )


def test_every_replay_engine_leg_runs_the_capability_check():
    import yaml

    steps = yaml.safe_load((ROOT / ".github/workflows/ci.yml").read_text())["jobs"][
        "replay-engine"
    ]["steps"]
    command = (
        ".venv-variant/bin/python -m pipeline.export_uk_events_dashboard "
        '--check-scenario-capability --variant "$VARIANT"'
    )
    (check,) = [s for s in steps if s.get("run", "").strip() == command]
    # No condition, continue-on-error, env or shell override can weaken it
    assert set(check) == {"name", "run"}
    names = [s.get("name") for s in steps]
    assert names.index("The installed environment is exactly the variant's") < (
        steps.index(check)
    )


@pytest.mark.parametrize("variant_id", EXPORTED)
def test_committed_export_regenerates_byte_for_byte(variant_id, tmp_path):
    out = export.write_export(variants.get_variant(variant_id), output_root=tmp_path)
    committed = export.EXPORT_ROOT / variant_id
    assert sorted(p.name for p in out.iterdir()) == sorted(
        p.name for p in committed.iterdir()
    )
    for path in out.iterdir():
        assert path.read_bytes() == (committed / path.name).read_bytes(), path.name


@pytest.mark.parametrize("variant_id", EXPORTED)
def test_manifest_names_every_file_by_digest(variant_id):
    folder = export.EXPORT_ROOT / variant_id
    manifest = json.loads((folder / export.EXPORT_MANIFEST).read_text())
    assert manifest["variant_id"] == variant_id
    files = {
        p.name: export.sha256_bytes(p.read_bytes())
        for p in folder.glob("*.json")
        if p.name != export.EXPORT_MANIFEST
    }
    assert manifest["files"] == files
    record = variants.get_variant(variant_id)
    receipt = variants.namespace_root(record) / variants.RECEIPT_NAME
    assert manifest["receipt_sha256"] == export.sha256_bytes(receipt.read_bytes())


@pytest.mark.parametrize("variant_id,event,document", ALL, ids=lambda v: str(v)[:40])
def test_every_registry_measure_once_computed_when_the_registry_computes_it(
    variant_id, event, document
):
    registry = registry_of(document)
    assert document["event"]["slug"] == event
    assert document["variant"]["variant_id"] == variant_id
    keys = [m["measure_key"] for m in document["measures"]]
    assert keys == sorted(m["measure_key"] for m in registry["measures"])
    supported = document["years"]["supported"]
    index = {m["measure_key"]: m for m in registry["measures"]}
    planned = export.worlds.computable(index, years=supported)
    namespace = export.Namespace(variants.get_variant(variant_id))
    run = namespace.json(f"{event}/RUN_MANIFEST.json")
    artifact_years: dict[str, list[int]] = {}
    for path in run["artifacts"]:
        artifact = namespace.json(
            Path(path).relative_to(namespace.path.relative_to(ROOT)).as_posix()
        )
        artifact_years.setdefault(artifact["measure_key"], []).append(artifact["year"])
    for measure in document["measures"]:
        key = measure["measure_key"]
        expected = measure["classification"] in export.COMPUTABLE and key in planned
        years = sorted(artifact_years.get(key, []))
        assert years == (supported if expected else [])
        assert measure["computed"] == (expected and bool(supported))
        if measure["computed"]:
            assert measure["classification"] in export.COMPUTABLE
            assert [y["year"] for y in measure["years"]] == supported
            assert all(
                y["fy"] == f"{y['year']}-{str(y['year'] + 1)[2:]}"
                for y in measure["years"]
            )
        else:
            assert measure["construction"] is None and measure["years"] == []
            assert measure["reason"]
        if measure["classification"] == "not_expressible":
            assert measure["gap_kind"] in export.GAP_KINDS
        else:
            assert measure["gap_kind"] is None


@pytest.mark.parametrize("variant_id,event,document", ALL, ids=lambda v: str(v)[:40])
def test_constructions_have_the_declared_direction_and_totals_sum_their_heads(
    variant_id, event, document
):
    for measure in (m for m in document["measures"] if m["computed"]):
        construction = measure["construction"]
        baseline = construction["baseline_world"]["submitted_reform"]
        reform = construction["reform_world"]["submitted_reform"]
        if construction["kind"] == "reversal_on_certified_world":
            assert baseline and reform is None
            assert (
                construction["reform_world"]["entry_point"] == "certified_current_law"
            )
        elif construction["kind"] == "forward_delta_on_certified_world":
            assert baseline is None and reform
            assert (
                construction["baseline_world"]["entry_point"] == "certified_current_law"
            )
        else:
            pytest.fail(f"{measure['measure_key']}: unexpected {construction['kind']}")
        heads = {v for h in construction["head_definitions"] for v in h["pe_variables"]}
        for year in measure["years"]:
            assert set(year["head_effects"]) <= heads
            assert year["measure_total_gbp"] == pytest.approx(
                math.fsum(year["head_effects"].values()), rel=1e-12, abs=1e-6
            )


@pytest.mark.parametrize("variant_id,event,document", ALL, ids=lambda v: str(v)[:40])
def test_classes_partition_the_source_rows(variant_id, event, document):
    accounting = document["accounting"]
    classes = accounting["by_class"]
    assert sum(Fraction(c["share_of_absolute"]) for c in classes.values()) == 1
    assert sum(Fraction(c["share_of_measures"]) for c in classes.values()) == 1
    totals = accounting["totals"]
    assert sum(c["rows"] for c in classes.values()) == totals["rows"]
    assert sum(c["measures"] for c in classes.values()) == totals["measures"]
    with export.exact():
        net = sum((Decimal(c["net_gbp_decimal"]) for c in classes.values()), Decimal(0))
        computable_absolute = sum(
            (Decimal(classes[c]["absolute_gbp_decimal"]) for c in export.COMPUTABLE),
            Decimal(0),
        )
    assert net == Decimal(totals["net_gbp_decimal"])
    rows = [r for m in document["measures"] for r in m["obr_rows"]]
    assert len(rows) == totals["rows"]
    assert len({r["source_row_id"] for r in rows}) == len(rows)
    computed = accounting["computed"]
    by_status = computed["by_status"]
    assert sum(s["rows"] for s in by_status.values()) == totals["rows"]
    assert sum(Fraction(s["share_of_absolute"]) for s in by_status.values()) == 1
    assert computed["rows"] == by_status.get(export.CONSTRUCTED, {"rows": 0})["rows"]
    assert Decimal(computed["absolute_gbp_decimal"]) <= computable_absolute
    for row in rows:
        if row["status"] == export.CONSTRUCTED:
            assert row["classification"] in export.COMPUTABLE
            assert row["replay_pe_value_gbp"] is not None


MEASURE_KEYS = {
    "measure_key",
    "title",
    "measure_type",
    "classification",
    "gap_kind",
    "reason",
    "missing_legs",
    "construction_note",
    "obr_rows",
    "computed",
    "construction",
    "years",
}
ROW_KEYS = {
    "source_row_id",
    "fy",
    "year",
    "tax_head",
    "obr_value_gbp_decimal",
    "classification",
    "status",
    "reason",
    "replay_pe_value_gbp",
    "replay_gap_gbp",
    "replay_pe_to_obr_ratio",
    "replay_ratio_bin",
}
YEAR_KEYS = {
    "year",
    "fy",
    "measure_total_gbp",
    "head_effects",
    "processed_parameter_values",
    "artifact",
    "artifact_sha256",
}
CONSTRUCTION_KEYS = {
    "kind",
    "components",
    "baseline_world",
    "reform_world",
    "construction_revision",
    "sentinels",
    "executor_route",
    "head_definitions",
}
SCALARS = (bool, int, float, str, type(None))


def assert_closed_shape(value, shape):
    if isinstance(shape, tuple) and shape[0] is None:
        if value is None:
            return
        shape = shape[1]
    if isinstance(shape, dict):
        assert isinstance(value, dict)
        assert set(value) == set(shape)
        for key, child in shape.items():
            assert_closed_shape(value[key], child)
    elif isinstance(shape, list):
        assert isinstance(value, list)
        for item in value:
            assert_closed_shape(item, shape[0])
    elif isinstance(shape, tuple) and isinstance(shape[0], frozenset | re.Pattern):
        assert isinstance(value, dict)
        keys, child = shape
        for key, item in value.items():
            assert key in keys if isinstance(keys, frozenset) else keys.fullmatch(key)
            assert_closed_shape(item, child)
    elif shape is SCALARS and isinstance(value, list):
        for item in value:
            assert_closed_shape(item, SCALARS)
    else:
        assert isinstance(value, shape)


def document_shape(document):
    registry = registry_of(document)
    worlds = export.worlds.computable(
        {m["measure_key"]: m for m in registry["measures"]},
        years=document["years"]["supported"],
    )
    paths = frozenset(
        path
        for world in worlds.values()
        for field in ("baseline_reform", "reform_reform")
        for path in world[field] or {}
    )
    heads = frozenset(
        variable
        for measure in registry["measures"]
        for head in export.replay.head_definitions(measure)
        for variable in head["pe_variables"]
    )
    reform = (
        None,
        (paths, (re.compile(r"\d{4}-\d{2}-\d{2}\.\d{4}-\d{2}-\d{2}"), SCALARS)),
    )
    world = {"entry_point": str, "submitted_reform": reform}
    account = {
        "measures": int,
        "rows": int,
        "net_gbp_decimal": str,
        "absolute_gbp_decimal": str,
        "share_of_absolute": (str, type(None)),
        "share_of_measures": (str, type(None)),
    }
    construction = {key: SCALARS for key in CONSTRUCTION_KEYS}
    construction.update(
        components=[str],
        baseline_world=world,
        reform_world=world,
        construction_revision=(
            None,
            {
                "revision_id": str,
                "registry_sha256": str,
                "activation_fy": str,
                "part_year_rule": str,
                "paths": [str],
            },
        ),
        sentinels=[str],
        head_definitions=[{"channel": str, "obr_head": str, "pe_variables": [str]}],
    )
    year = {key: SCALARS for key in YEAR_KEYS}
    year.update(
        head_effects=(heads, (float, int)),
        processed_parameter_values={
            name: (paths, {"intended": SCALARS, "processed": SCALARS})
            for name in ("baseline_world", "reform_world")
        },
    )
    measure = {key: SCALARS for key in MEASURE_KEYS}
    measure.update(
        missing_legs=[str],
        obr_rows=[{key: SCALARS for key in ROW_KEYS}],
        construction=(None, construction),
        years=[year],
    )
    return {
        "schema": str,
        "semantics": str,
        "sign_convention": str,
        "event": dict.fromkeys(
            ("slug", "name", "registry_path", "registry_sha256"), str
        ),
        "variant": {
            **dict.fromkeys(
                (
                    "variant_id",
                    "variant_identity_sha256",
                    "receipt_sha256",
                    "namespace_manifest_sha256",
                    "run_manifest_sha256",
                    "comparison_sha256",
                ),
                str,
            ),
            "packages": dict.fromkeys(
                variants.get_variant(document["variant"]["variant_id"])["identity"][
                    "packages"
                ],
                str,
            ),
            "dataset": dict.fromkeys(("repo_id", "path", "revision", "sha256"), str),
            "data_years": [int],
        },
        "years": {
            "requested": [int],
            "supported": [int],
            "unsupported": [{"reason": str, "year": int}],
        },
        "accounting": {
            "amount_basis": str,
            "sign_convention": str,
            "by_class": dict.fromkeys(export.CLASSES, account),
            "not_expressible_by_gap_kind": dict.fromkeys(export.GAP_KINDS, account),
            "totals": {
                "measures": int,
                "rows": int,
                "net_gbp_decimal": str,
                "absolute_gbp_decimal": str,
            },
            "computed": {
                "measures": int,
                "rows": int,
                "absolute_gbp_decimal": str,
                "share_of_absolute": (str, type(None)),
                "share_of_measures": (str, type(None)),
                "by_status": (
                    frozenset(
                        ("constructed", "not_computed", "unsupported_on_variant")
                    ),
                    {
                        "rows": int,
                        "absolute_gbp_decimal": str,
                        "share_of_absolute": (str, type(None)),
                    },
                ),
            },
        },
        "measures": [measure],
    }


@pytest.mark.parametrize("variant_id,event,document", ALL, ids=lambda v: str(v)[:40])
def test_the_document_has_a_closed_aggregate_shape(variant_id, event, document):
    assert document["schema"] == export.SCHEMA
    assert_closed_shape(document, document_shape(document))


def test_unknown_event_fields_are_refused_by_the_closed_schema():
    document = documents(FIRST)[EVENT]
    shape = document_shape(document)
    document["event"]["extra_unrecognised_field"] = 123
    with pytest.raises(AssertionError):
        assert_closed_shape(document, shape)


def test_the_uc_health_measure_names_its_executor_route():
    document = documents(FIRST)[EVENT]
    routes = {
        m["measure_key"]: m["construction"]["executor_route"]
        for m in document["measures"]
        if m["computed"]
    }
    assert routes == {
        "spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut": "uc_health_element_refresh",
        "spring_statement_2025__uc_standard_allowance_above_inflation": None,
    }


# --- refusals on tampered copies ------------------------------------------------


def sealed_copy(tmp_path: Path, event: str = EVENT) -> tuple[dict, Path]:
    """A minimal copy of FIRST's sealed namespace holding one event."""
    record = variants.get_variant(FIRST)
    source = variants.namespace_root(record)
    target = variants.namespace_root(record, root=tmp_path)
    target.mkdir(parents=True)
    for name in (
        variants.RECEIPT_NAME,
        "NAMESPACE_MANIFEST.json",
        variants.CORPUS_NAME,
        "CONSTRUCTION_PREMISES.json",
    ):
        shutil.copy2(source / name, target / name)
    shutil.copytree(source / event, target / event)
    run = json.loads((source / event / "RUN_MANIFEST.json").read_text())
    registry = tmp_path / run["registry_path"]
    registry.parent.mkdir(parents=True)
    shutil.copy2(ROOT / run["registry_path"], registry)
    requirements = tmp_path / record["requirements"]["path"]
    requirements.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / record["requirements"]["path"], requirements)
    return record, target


def reseal_namespace(target: Path, event: str) -> None:
    """Reseal edited fixture files so semantic checks see valid digests."""
    run_path = target / event / "RUN_MANIFEST.json"
    run = json.loads(run_path.read_bytes())
    changed_artifacts = {}
    artifact_names = {Path(path).name for path in run["artifacts"]}
    for path in run["artifacts"]:
        artifact = target / event / Path(path).name
        old_digest = run["artifacts"][path]
        new_digest = export.sha256_bytes(artifact.read_bytes())
        run["artifacts"][path] = new_digest
        if new_digest != old_digest:
            changed_artifacts[old_digest] = new_digest
    run_path.write_bytes(export.canonical_json(run))
    # Staging, comparisons, and progress records also carry artifact digests.
    # Preserve their formatting while refreshing every pointer to an edited file.
    for path in (target / event).iterdir():
        if path.name in artifact_names or path == run_path:
            continue
        if path.suffix not in (".json", ".jsonl", ".csv", ".md"):
            continue
        content = path.read_bytes()
        for old_digest, new_digest in changed_artifacts.items():
            content = content.replace(old_digest.encode(), new_digest.encode())
        path.write_bytes(content)
    staged_digest = export.sha256_bytes((target / event / "STAGED.jsonl").read_bytes())
    staging_path = target / event / "STAGING_MANIFEST.json"
    staging = json.loads(staging_path.read_bytes())
    staging["staged_sha256"] = staged_digest
    staging_path.write_bytes(export.canonical_json(staging))
    staging_digest = export.sha256_bytes(staging_path.read_bytes())
    run_digest = export.sha256_bytes(run_path.read_bytes())
    provenance_path = target / event / "COMPARISON_PROVENANCE.json"
    provenance = json.loads(provenance_path.read_bytes())
    provenance["run_manifest_sha256"] = run_digest
    provenance["staged_sha256"] = staged_digest
    provenance["staging_manifest_sha256"] = staging_digest
    for name in provenance["outputs_sha256"]:
        provenance["outputs_sha256"][name] = export.sha256_bytes(
            (target / event / name).read_bytes()
        )
    provenance_path.write_bytes(export.canonical_json(provenance))
    provenance_digest = export.sha256_bytes(provenance_path.read_bytes())
    manifest_path = target / "NAMESPACE_MANIFEST.json"
    manifest = json.loads(manifest_path.read_bytes())
    for relative in manifest["files"]:
        path = target / relative
        if path.is_file():
            manifest["files"][relative] = export.sha256_bytes(path.read_bytes())
    manifest_path.write_bytes(export.canonical_json(manifest))
    receipt_path = target / variants.RECEIPT_NAME
    receipt = json.loads(receipt_path.read_bytes())
    receipt["results"]["manifest_sha256"] = export.sha256_bytes(
        manifest_path.read_bytes()
    )
    event_receipt = receipt["corpus"]["events"][event]
    event_receipt["run_manifest_sha256"] = run_digest
    event_receipt["staging_manifest_sha256"] = staging_digest
    event_receipt["comparison_provenance_sha256"] = provenance_digest
    receipt_path.write_bytes(export.canonical_json(interface.seal_receipt(receipt)))


def assert_namespace_fully_resealed(target: Path, event: str) -> None:
    receipt = json.loads((target / variants.RECEIPT_NAME).read_bytes())
    interface.validate(receipt, interface.RECEIPT_SCHEMA_ID)
    manifest_path = target / "NAMESPACE_MANIFEST.json"
    assert receipt["results"]["manifest_sha256"] == export.sha256_bytes(
        manifest_path.read_bytes()
    )
    manifest = json.loads(manifest_path.read_bytes())
    for relative, digest in manifest["files"].items():
        path = target / relative
        if path.is_file():
            assert digest == export.sha256_bytes(path.read_bytes()), relative
    run_path = target / event / "RUN_MANIFEST.json"
    run = json.loads(run_path.read_bytes())
    for path, digest in run["artifacts"].items():
        assert digest == export.sha256_bytes(
            (target / event / Path(path).name).read_bytes()
        ), path
    staged_path = target / event / "STAGED.jsonl"
    staged = [json.loads(line) for line in staged_path.read_bytes().splitlines()]
    comparisons = json.loads((target / event / "COMPARISON.json").read_bytes())
    comparison_csv = list(csv.DictReader((target / event / "COMPARISON.csv").open()))
    for rows, field in (
        (staged, "artifact_path"),
        (comparisons, "artifact"),
        (comparison_csv, "artifact"),
    ):
        for row in rows:
            if row.get(field):
                assert row["artifact_sha256"] == run["artifacts"][row[field]]
    staging_path = target / event / "STAGING_MANIFEST.json"
    staging = json.loads(staging_path.read_bytes())
    assert staging["staged_sha256"] == export.sha256_bytes(staged_path.read_bytes())
    provenance_path = target / event / "COMPARISON_PROVENANCE.json"
    provenance = json.loads(provenance_path.read_bytes())
    assert provenance["run_manifest_sha256"] == export.sha256_bytes(
        run_path.read_bytes()
    )
    assert provenance["staged_sha256"] == staging["staged_sha256"]
    assert provenance["staging_manifest_sha256"] == export.sha256_bytes(
        staging_path.read_bytes()
    )
    for name, digest in provenance["outputs_sha256"].items():
        assert digest == export.sha256_bytes((target / event / name).read_bytes())
    event_receipt = receipt["corpus"]["events"][event]
    assert event_receipt["run_manifest_sha256"] == provenance["run_manifest_sha256"]
    assert (
        event_receipt["staging_manifest_sha256"]
        == provenance["staging_manifest_sha256"]
    )
    assert event_receipt["comparison_provenance_sha256"] == export.sha256_bytes(
        provenance_path.read_bytes()
    )


def test_an_identity_path_changed_without_its_digest_is_refused(tmp_path):
    record, _ = sealed_copy(tmp_path)
    record["identity"]["dataset"]["path"] = "unsealed.h5"
    with pytest.raises(export.ExportError, match="identity_sha256 differs"):
        export.Namespace(record, root=tmp_path)


def test_unsealed_data_years_are_refused(tmp_path):
    record, _ = sealed_copy(tmp_path)
    record["data_years"] = record["data_years"][:-1]
    with pytest.raises(export.ExportError, match="data years differ"):
        export.write_export(
            record, [EVENT], root=tmp_path, output_root=tmp_path / "out"
        )


def test_a_missing_sealed_event_cannot_disappear_from_the_default_export(tmp_path):
    record = variants.get_variant(FIRST)
    source = variants.namespace_root(record)
    target = variants.namespace_root(record, root=tmp_path)
    shutil.copytree(source, target)
    requirements = tmp_path / record["requirements"]["path"]
    requirements.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / record["requirements"]["path"], requirements)
    for event in json.loads((source / variants.CORPUS_NAME).read_bytes())["events"]:
        run = json.loads((source / event / "RUN_MANIFEST.json").read_bytes())
        registry = tmp_path / run["registry_path"]
        registry.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / run["registry_path"], registry)
    (target / EVENT / "RUN_MANIFEST.json").unlink()
    with pytest.raises(
        export.ExportError, match="RUN_MANIFEST.json: sealed file is missing"
    ):
        export.write_export(record, root=tmp_path, output_root=tmp_path / "out")


def test_an_incomplete_integrity_receipt_is_refused(tmp_path):
    record, target = sealed_copy(tmp_path)
    path = target / variants.RECEIPT_NAME
    receipt = json.loads(path.read_bytes())
    assert receipt["status"] == "complete"
    receipt["integrity"]["status"] = "incomplete"
    path.write_bytes(export.canonical_json(receipt))
    with pytest.raises(export.ExportError, match="not a complete seal"):
        export.Namespace(record, root=tmp_path)


@pytest.mark.parametrize(
    "malformation", ["missing_year", "duplicate_year", "missing_measure"]
)
def test_resealed_incomplete_or_duplicate_artifact_years_are_refused(
    tmp_path, malformation
):
    record, target = sealed_copy(tmp_path)
    run_path = target / EVENT / "RUN_MANIFEST.json"
    run = json.loads(run_path.read_bytes())
    first, second = sorted(run["artifacts"])[:2]
    if malformation == "duplicate_year":
        path = tmp_path / second
        artifact = json.loads(path.read_bytes())
        artifact["year"] = json.loads((tmp_path / first).read_bytes())["year"]
        path.write_bytes(export.canonical_json(artifact))
        message = "duplicate artifact measure/year"
    else:
        key = json.loads((tmp_path / first).read_bytes())["measure_key"]
        for path in list(run["artifacts"]):
            if path == first or (
                malformation == "missing_measure"
                and json.loads((tmp_path / path).read_bytes())["measure_key"] == key
            ):
                del run["artifacts"][path]
        message = "expected supported-year grid"
    run_path.write_bytes(export.canonical_json(run))
    reseal_namespace(target, EVENT)
    with pytest.raises(export.ExportError, match=message):
        export.write_export(
            record, [EVENT], root=tmp_path, output_root=tmp_path / "out"
        )


def test_a_noncomputed_measure_cannot_own_constructed_obr_rows(tmp_path):
    record, target = sealed_copy(tmp_path)
    path = target / EVENT / "COMPARISON.csv"
    reader = csv.DictReader(io.StringIO(path.read_text()))
    rows = list(reader)
    next(row for row in rows if row["status"] != export.CONSTRUCTED)["status"] = (
        export.CONSTRUCTED
    )
    with path.open("w") as stream:
        writer = csv.DictWriter(stream, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    reseal_namespace(target, EVENT)
    with pytest.raises(
        export.ExportError, match="noncomputed measure owns constructed"
    ):
        export.write_export(
            record, [EVENT], root=tmp_path, output_root=tmp_path / "out"
        )


def test_a_sealed_copy_exports_the_committed_bytes(tmp_path):
    record, _ = sealed_copy(tmp_path)
    out = export.write_export(
        record, [EVENT], root=tmp_path, output_root=tmp_path / "out"
    )
    committed = export.EXPORT_ROOT / FIRST / f"{EVENT}.json"
    assert (out / f"{EVENT}.json").read_bytes() == committed.read_bytes()


def flip_last_byte(path: Path) -> None:
    data = bytearray(path.read_bytes())
    data[-2] = ord(" ") if data[-2] != ord(" ") else ord("\t")
    path.write_bytes(bytes(data))


@pytest.mark.parametrize(
    "victim,message",
    [
        ("artifact", "does not match its sealed digest"),
        ("COMPARISON.csv", "does not match its sealed digest"),
        ("NAMESPACE_MANIFEST.json", "is not the sealed one"),
        ("registry", "is not the registry this replay ran"),
    ],
)
def test_a_tampered_input_is_refused(tmp_path, victim, message):
    record, target = sealed_copy(tmp_path)
    run = json.loads((target / EVENT / "RUN_MANIFEST.json").read_text())
    path = {
        "artifact": tmp_path / min(run["artifacts"]),
        "COMPARISON.csv": target / EVENT / "COMPARISON.csv",
        "NAMESPACE_MANIFEST.json": target / "NAMESPACE_MANIFEST.json",
        "registry": tmp_path / run["registry_path"],
    }[victim]
    flip_last_byte(path)
    with pytest.raises(export.ExportError, match=message):
        export.write_export(
            record, [EVENT], root=tmp_path, output_root=tmp_path / "out"
        )


@pytest.mark.parametrize(
    "change", ["rates", "window", "evidence", "artifact_evidence", "missing_year_world"]
)
def test_a_revision_allows_only_its_recorded_window_change(tmp_path, change):
    event = "autumn_budget_2024"
    key = "autumn_budget_2024__capital_gains_main_rates_and_reliefs"
    record, target = sealed_copy(tmp_path, event)
    run_path = target / event / "RUN_MANIFEST.json"
    run = json.loads(run_path.read_text())
    if change == "evidence":
        run["construction_revisions"][key]["registry_sha256"] = "0" * 64
        run_path.write_bytes(export.canonical_json(run))
    else:
        for artifact_path in (target / event).glob(f"{key}_*.json"):
            artifact = json.loads(artifact_path.read_text())
            if change == "artifact_evidence":
                artifact["construction_revision"]["revision_id"] = "unrecorded_revision"
            else:
                windows = artifact["parameter_reform_routes"]["baseline_world"][
                    "submitted_reform"
                ]["gov.hmrc.cgt.basic_rate"]
                if change == "rates":
                    assert set(windows.values()) == {0.1}
                    for window in windows:
                        windows[window] = 0.99
                elif change == "window":
                    first = min(windows)
                    windows["2023-04-06.2036-04-05"] = windows.pop(first)
                else:
                    del artifact["parameter_reform_routes"]["baseline_world"][
                        "submitted_reform"
                    ]["gov.hmrc.cgt.basic_rate"]
            artifact_path.write_bytes(export.canonical_json(artifact))
            if change == "missing_year_world":
                break
    reseal_namespace(target, event)
    message = (
        "revision" if change in ("evidence", "artifact_evidence") else "construction"
    )
    with pytest.raises(export.ExportError, match=message):
        export.write_export(
            record, [event], root=tmp_path, output_root=tmp_path / "out"
        )


@pytest.mark.parametrize("change", ["annual_windows", "current_law_entry_point"])
def test_a_revision_must_use_its_engines_recorded_execution_route(tmp_path, change):
    """The reviewer's accepted fixtures retain valid digests and revision evidence."""
    event = "autumn_budget_2024"
    key = "autumn_budget_2024__capital_gains_main_rates_and_reliefs"
    record, target = sealed_copy(tmp_path, event)
    paths = sorted((target / event).glob(f"{key}_*.json"))
    assert len(paths) == 6
    for path in paths:
        artifact = json.loads(path.read_bytes())
        assert artifact["engine_version"] == "2.130.1"
        route = artifact["parameter_reform_routes"]["baseline_world"]
        assert route["entry_point"] == "construction_reform"
        for windows in route["submitted_reform"].values():
            assert set(windows) == {"2024-04-06.2036-04-05"}
        if change == "annual_windows":
            route["submitted_reform"] = {
                parameter: {"2024-01-01.2035-12-31": next(iter(windows.values()))}
                for parameter, windows in route["submitted_reform"].items()
            }
        else:
            route["entry_point"] = "certified_current_law"
        path.write_bytes(export.canonical_json(artifact))
    reseal_namespace(target, event)
    assert_namespace_fully_resealed(target, event)
    with pytest.raises(
        export.ExportError,
        match="construction" if change == "annual_windows" else "entry point",
    ):
        export.write_export(
            record, [event], root=tmp_path, output_root=tmp_path / "out"
        )


@pytest.mark.parametrize(
    "event,key",
    [
        (
            EVENT,
            "spring_statement_2025__uc_health_element_freeze_and_new_claimant_cut",
        ),
        (EVENT, "spring_statement_2025__uc_standard_allowance_above_inflation"),
        ("autumn_budget_2024", "autumn_budget_2024__private_school_vat_20pct"),
    ],
)
@pytest.mark.parametrize("world", ["baseline_world", "reform_world"])
@pytest.mark.parametrize("alternative", [0, 1])
def test_unrevised_worlds_must_name_the_entry_point_their_reform_uses(
    tmp_path, event, key, world, alternative
):
    record, target = sealed_copy(tmp_path, event)
    points = {
        "built_simulation_scenario",
        "construction_reform",
        "certified_current_law",
    }
    paths = sorted((target / event).glob(f"{key}_*.json"))
    assert paths
    for path in paths:
        artifact = json.loads(path.read_bytes())
        assert artifact.get("construction_revision") is None
        route = artifact["parameter_reform_routes"][world]
        route["entry_point"] = sorted(points - {route["entry_point"]})[alternative]
        path.write_bytes(export.canonical_json(artifact))
    # All years agree on the wrong entry point; agreement alone must not pass.
    reseal_namespace(target, event)
    with pytest.raises(export.ExportError, match="entry point"):
        export.write_export(
            record, [event], root=tmp_path, output_root=tmp_path / "out"
        )


@pytest.mark.parametrize("source", ["premises", "run", "artifact"])
def test_resealed_engine_versions_must_agree_with_the_certified_identity(
    tmp_path, source
):
    record, target = sealed_copy(tmp_path)
    run_path = target / EVENT / "RUN_MANIFEST.json"
    run = json.loads(run_path.read_bytes())
    path = {
        "premises": target / "CONSTRUCTION_PREMISES.json",
        "run": run_path,
        "artifact": tmp_path / min(run["artifacts"]),
    }[source]
    document = json.loads(path.read_bytes())
    engine = document["engine"] if source == "premises" else document
    field = "policyengine_uk" if source == "premises" else "engine_version"
    assert engine[field] == "2.130.1"
    engine[field] = "999.0.0"
    path.write_bytes(export.canonical_json(document))
    reseal_namespace(target, EVENT)
    with pytest.raises(export.ExportError, match="engine"):
        export.write_export(
            record, [EVENT], root=tmp_path, output_root=tmp_path / "out"
        )


def test_an_engine_without_verified_scenario_capability_is_refused(monkeypatch):
    record = variants.get_variant(FIRST)
    version = record["identity"]["packages"]["policyengine-uk"]["version"]
    monkeypatch.delitem(export.SCENARIO_DATED_REFORMS, version)
    with pytest.raises(export.ExportError, match="unverified Scenario route"):
        export.Namespace(record)


def test_legacy_and_uncertified_variants_are_refused():
    document = variants.load_document()
    legacy = next(v for v in document["variants"] if variants.is_legacy(v))
    with pytest.raises(export.ExportError, match="legacy"):
        export.Namespace(legacy)
    candidate = dict(variants.get_variant(FIRST), status="candidate")
    with pytest.raises(export.ExportError, match="not certified"):
        export.Namespace(candidate)


def test_the_default_variant_is_the_newest_certified_namespace():
    document = variants.load_document()
    newest = [v for v in document["variants"] if v["status"] == "certified"][-1]
    assert export.default_variant(document)["variant_id"] == newest["variant_id"]


# --- properties of the helpers ---------------------------------------------------

decimals = st.decimals(
    min_value=Decimal("-1e15"), max_value=Decimal("1e15"), places=17, allow_nan=False
)
correctness = settings(deadline=None, suppress_health_check=[HealthCheck.too_slow])


@correctness
@given(decimals)
def test_decimal_text_round_trips_without_an_exponent(value):
    text = export.decimal_text(value)
    assert Decimal(text) == value
    assert "E" not in text.upper() and text != "-0"


@correctness
@given(st.lists(decimals.map(abs), min_size=1, max_size=40))
def test_shares_of_a_partition_sum_to_exactly_one(parts):
    with export.exact():
        whole = sum(parts, Decimal(0))
    shares = [export.share_text(p, whole) for p in parts]
    if whole == 0:
        assert shares == [None] * len(parts)
    else:
        assert sum(Fraction(s) for s in shares) == 1


@correctness
@given(st.lists(decimals, max_size=200))
def test_exact_sums_never_round(values):
    with export.exact():
        total = sum(values, Decimal(0))
    assert Fraction(total) == sum((Fraction(v) for v in values), Fraction(0))


windows = st.sampled_from(
    [f"{y}-01-01.{y}-12-31" for y in range(2024, 2031)] + ["2024-01-01.2035-12-31"]
)
reforms = st.dictionaries(
    st.sampled_from(["gov.a", "gov.b.c", "gov.d"]),
    st.dictionaries(windows, st.integers(0, 3), min_size=1, max_size=3),
    max_size=3,
)


@correctness
@given(st.lists(reforms, min_size=1, max_size=5), st.randoms())
def test_union_of_consistent_years_is_order_free(per_year, random):
    merged: dict = {}
    consistent = []
    for reform in per_year:
        if all(
            merged.get(path, {}).get(window, value) == value
            for path, ws in reform.items()
            for window, value in ws.items()
        ):
            for path, ws in reform.items():
                merged.setdefault(path, {}).update(ws)
            consistent.append(reform)
    shuffled = list(consistent)
    random.shuffle(shuffled)
    expected = (
        {p: dict(sorted(w.items())) for p, w in sorted(merged.items())}
        if consistent
        else None
    )
    assert export.union_reforms(consistent, "t") == expected
    assert export.union_reforms(shuffled + [None], "t") == expected


@correctness
@given(reforms.filter(bool))
def test_a_year_that_disagrees_is_refused(reform):
    path, ws = next(iter(reform.items()))
    window, value = next(iter(ws.items()))
    other = {path: {window: value + 1}}
    with pytest.raises(export.ExportError, match="years disagree"):
        export.union_reforms([reform, other], "t")


# --- the accounting against an independent implementation ---------------------


def reference_accounting(measures: list[dict]) -> tuple[dict, dict]:
    """The recorded and exported accounts, computed independently with Fractions."""

    def empty() -> dict:
        return {"rows": 0, "net": Fraction(0), "abs": Fraction(0), "measures": 0}

    by_class = {c: empty() for c in export.CLASSES}
    gaps = {k: empty() for k in export.GAP_KINDS}
    by_fy = {}
    for measure in measures:
        classification = measure["classification"]
        by_class[classification]["measures"] += 1
        if classification == "not_expressible":
            gaps[measure["gap_kind"]]["measures"] += 1
        for row in measure["source_rows"]:
            row_class = row.get("classification", classification)
            accounts = [by_class[row_class], by_fy.setdefault(row["fy"], empty())]
            if row_class == "not_expressible":
                accounts.append(gaps[row.get("gap_kind", measure.get("gap_kind"))])
            value = Fraction(row["value_gbp_decimal"])
            for account in accounts:
                account["rows"] += 1
                account["net"] += value
                account["abs"] += abs(value)
    rows = sum(a["rows"] for a in by_class.values())
    net = sum((a["net"] for a in by_class.values()), Fraction(0))
    absolute = sum((a["abs"] for a in by_class.values()), Fraction(0))

    def text(f: Fraction) -> str:
        value = format(Decimal(f.numerator) / Decimal(f.denominator), "f")
        return value.rstrip("0").rstrip(".") if "." in value else value

    def balance(count: int, net: Fraction, absolute: Fraction) -> dict:
        return {
            "rows_in": count,
            "rows_classified": count,
            "net_gbp_in_decimal": text(net),
            "net_gbp_classified_decimal": text(net),
            "absolute_gbp_in_decimal": text(absolute),
            "absolute_gbp_classified_decimal": text(absolute),
        }

    def share(part: Fraction | int, whole: Fraction | int) -> str | None:
        if whole == 0:
            return None
        value = Fraction(part) / Fraction(whole)
        return f"{value.numerator}/{value.denominator}"

    def render(account: dict) -> dict:
        return {
            "rows": account["rows"],
            "measures": account["measures"],
            "net_gbp_decimal": text(account["net"]),
            "absolute_gbp_decimal": text(account["abs"]),
            "share_of_absolute": share(account["abs"], absolute),
            "share_of_measures": share(account["measures"], len(measures)),
        }

    # Fractions of finite decimals divide exactly at this precision.
    with export.exact():
        labels = {
            "amount_basis": "test",
            "sign_convention": "positive means a gain to the Exchequer",
        }
        recorded = {
            **labels,
            **balance(rows, net, absolute),
            "by_class": {
                c: {
                    "rows": a["rows"],
                    "net_gbp_decimal": text(a["net"]),
                    "absolute_gbp_decimal": text(a["abs"]),
                    "measures": a["measures"],
                }
                for c, a in by_class.items()
            },
            "by_fy": {
                fy: balance(a["rows"], a["net"], a["abs"]) for fy, a in by_fy.items()
            },
        }
        expected = {
            **labels,
            "by_class": {c: render(a) for c, a in by_class.items()},
            "not_expressible_by_gap_kind": {k: render(a) for k, a in gaps.items()},
            "totals": {
                "measures": len(measures),
                "rows": rows,
                "net_gbp_decimal": text(net),
                "absolute_gbp_decimal": text(absolute),
            },
        }
        return recorded, expected


row_strategy = st.builds(
    lambda classification, gap_kind, value, fy: {
        "classification": classification,
        "gap_kind": gap_kind if classification == "not_expressible" else None,
        "value_gbp_decimal": str(value),
        "fy": fy,
    },
    st.sampled_from(export.CLASSES),
    st.sampled_from(export.GAP_KINDS),
    decimals,
    st.sampled_from(["2024-25", "2025-26", "2026-27"]),
)
measure_strategy = st.builds(
    lambda classification, gap_kind, rows: {
        "classification": classification,
        "gap_kind": gap_kind if classification == "not_expressible" else None,
        "source_rows": rows,
    },
    st.sampled_from(export.CLASSES),
    st.sampled_from(export.GAP_KINDS),
    st.lists(row_strategy, max_size=8),
)


@settings(correctness, max_examples=200)
@example(
    [
        {
            "classification": "not_expressible",
            "gap_kind": "construction_pending",
            "source_rows": [
                {
                    "classification": "not_expressible",
                    "gap_kind": "model_or_data_gap",
                    "value_gbp_decimal": "-1.25",
                    "fy": "2024-25",
                },
                {
                    "classification": "expressible",
                    "value_gbp_decimal": "2",
                    "fy": "2025-26",
                },
            ],
        }
    ]
)
@given(st.lists(measure_strategy, min_size=1, max_size=12))
def test_accounting_agrees_with_a_fraction_reference(measures):
    recorded, expected = reference_accounting(measures)
    registry = {
        "event_slug": "generated",
        "measures": measures,
        "accounting": recorded,
    }
    assert export.accounting(registry) == expected


@correctness
@given(
    st.lists(measure_strategy, min_size=1, max_size=6), st.sampled_from(export.CLASSES)
)
def test_accounting_that_differs_from_the_registry_is_refused(measures, victim):
    recorded, _ = reference_accounting(measures)
    # Exact, or a large net would round the perturbation away.
    with export.exact():
        recorded["by_class"][victim]["net_gbp_decimal"] = str(
            Decimal(recorded["by_class"][victim]["net_gbp_decimal"]) + Decimal("1e-20")
        )
    registry = {"event_slug": "generated", "measures": measures, "accounting": recorded}
    with pytest.raises(export.ExportError, match="accounting differs"):
        export.accounting(registry)


@pytest.mark.parametrize(
    "field",
    [
        "rows_classified",
        "net_gbp_classified_decimal",
        "absolute_gbp_classified_decimal",
        "by_fy.rows_in",
        "by_fy.rows_classified",
        "by_fy.net_gbp_in_decimal",
        "by_fy.net_gbp_classified_decimal",
        "by_fy.absolute_gbp_in_decimal",
        "by_fy.absolute_gbp_classified_decimal",
    ],
)
def test_recorded_accounting_totals_and_fiscal_years_are_verified(field):
    registry = registry_of(documents(FIRST)[EVENT])
    account = registry["accounting"]
    if field.startswith("by_fy."):
        account = next(iter(account["by_fy"].values()))
        field = field.removeprefix("by_fy.")
    if field.startswith("rows_"):
        account[field] += 1
    else:
        with export.exact():
            account[field] = str(Decimal(account[field]) + Decimal("1e-20"))
    with pytest.raises(export.ExportError, match="accounting .*differ"):
        export.accounting(registry)


@pytest.mark.parametrize("change", ["missing", "extra"])
def test_recorded_accounting_fiscal_years_must_match_the_rows(change):
    registry = registry_of(documents(FIRST)[EVENT])
    by_fy = registry["accounting"]["by_fy"]
    year = next(iter(by_fy))
    if change == "missing":
        del by_fy[year]
    else:
        by_fy["2099-00"] = dict(by_fy[year])
    with pytest.raises(export.ExportError, match="fiscal-year accounting differs"):
        export.accounting(registry)
