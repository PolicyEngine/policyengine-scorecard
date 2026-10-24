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

import json
import math
import shutil
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from pipeline import export_uk_events_dashboard as export
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
    for measure in document["measures"]:
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
    "ratio_bin",
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


@pytest.mark.parametrize("variant_id,event,document", ALL, ids=lambda v: str(v)[:40])
def test_the_document_has_a_closed_aggregate_shape(variant_id, event, document):
    assert set(document) == {
        "schema",
        "semantics",
        "sign_convention",
        "event",
        "variant",
        "years",
        "accounting",
        "measures",
    }
    assert document["schema"] == export.SCHEMA
    for measure in document["measures"]:
        assert set(measure) == MEASURE_KEYS
        for row in measure["obr_rows"]:
            assert set(row) == ROW_KEYS
        if measure["construction"]:
            assert set(measure["construction"]) == CONSTRUCTION_KEYS
        for year in measure["years"]:
            assert set(year) == YEAR_KEYS
            # National aggregates: one number per fiscal head.
            assert all(
                isinstance(v, float | int) for v in year["head_effects"].values()
            )
            for world in year["processed_parameter_values"].values():
                for value in world.values():
                    assert set(value) == {"intended", "processed"}
                    assert all(isinstance(v, SCALARS + (list,)) for v in value.values())


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
    ):
        shutil.copy2(source / name, target / name)
    shutil.copytree(source / event, target / event)
    run = json.loads((source / event / "RUN_MANIFEST.json").read_text())
    registry = tmp_path / run["registry_path"]
    registry.parent.mkdir(parents=True)
    shutil.copy2(ROOT / run["registry_path"], registry)
    return record, target


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


@given(decimals)
def test_decimal_text_round_trips_without_an_exponent(value):
    text = export.decimal_text(value)
    assert Decimal(text) == value
    assert "E" not in text.upper() and text != "-0"


@given(st.lists(decimals.map(abs), min_size=1, max_size=40))
def test_shares_of_a_partition_sum_to_exactly_one(parts):
    with export.exact():
        whole = sum(parts, Decimal(0))
    shares = [export.share_text(p, whole) for p in parts]
    if whole == 0:
        assert shares == [None] * len(parts)
    else:
        assert sum(Fraction(s) for s in shares) == 1


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


@given(reforms.filter(bool))
def test_a_year_that_disagrees_is_refused(reform):
    path, ws = next(iter(reform.items()))
    window, value = next(iter(ws.items()))
    other = {path: {window: value + 1}}
    with pytest.raises(export.ExportError, match="years disagree"):
        export.union_reforms([reform, other], "t")


# --- the accounting against an independent implementation ---------------------


def reference_accounting(measures: list[dict]) -> dict:
    """The registry's recorded accounting, computed with Fractions."""
    by_class = {
        c: {"rows": 0, "net": Fraction(0), "abs": Fraction(0), "measures": 0}
        for c in export.CLASSES
    }
    for measure in measures:
        by_class[measure["classification"]]["measures"] += 1
        for row in measure["source_rows"]:
            account = by_class[row["classification"]]
            value = Fraction(Decimal(row["value_gbp_decimal"]))
            account["rows"] += 1
            account["net"] += value
            account["abs"] += abs(value)

    def text(f: Fraction) -> str:
        return str(Decimal(f.numerator) / Decimal(f.denominator)) if f else "0"

    # Fractions of finite decimals divide exactly at this precision.
    with export.exact():
        return {
            "amount_basis": "test",
            "sign_convention": "positive means a gain to the Exchequer",
            "rows_in": sum(a["rows"] for a in by_class.values()),
            "net_gbp_in_decimal": text(
                sum((a["net"] for a in by_class.values()), Fraction(0))
            ),
            "absolute_gbp_in_decimal": text(
                sum((a["abs"] for a in by_class.values()), Fraction(0))
            ),
            "by_class": {
                c: {
                    "rows": a["rows"],
                    "net_gbp_decimal": text(a["net"]),
                    "absolute_gbp_decimal": text(a["abs"]),
                    "measures": a["measures"],
                }
                for c, a in by_class.items()
            },
        }


measure_strategy = st.builds(
    lambda classification, gap_kind, values: {
        "classification": classification,
        "gap_kind": gap_kind if classification == "not_expressible" else None,
        "source_rows": [
            {"classification": classification, "value_gbp_decimal": str(v)}
            for v in values
        ],
    },
    st.sampled_from(export.CLASSES),
    st.sampled_from(export.GAP_KINDS),
    st.lists(decimals, max_size=8),
)


@settings(max_examples=200)
@given(st.lists(measure_strategy, min_size=1, max_size=12))
def test_accounting_agrees_with_a_fraction_reference(measures):
    registry = {
        "event_slug": "generated",
        "measures": measures,
        "accounting": reference_accounting(measures),
    }
    result = export.accounting(registry)
    for c in export.CLASSES:
        recorded = registry["accounting"]["by_class"][c]
        assert Decimal(result["by_class"][c]["net_gbp_decimal"]) == Decimal(
            recorded["net_gbp_decimal"]
        )
        assert result["by_class"][c]["rows"] == recorded["rows"]
    assert result["totals"]["rows"] == registry["accounting"]["rows_in"]
    shares = [result["by_class"][c]["share_of_absolute"] for c in export.CLASSES]
    if any(shares):
        assert sum(Fraction(s) for s in shares) == 1


@given(
    st.lists(measure_strategy, min_size=1, max_size=6), st.sampled_from(export.CLASSES)
)
def test_accounting_that_differs_from_the_registry_is_refused(measures, victim):
    recorded = reference_accounting(measures)
    # Exact, or a large net would round the perturbation away.
    with export.exact():
        recorded["by_class"][victim]["net_gbp_decimal"] = str(
            Decimal(recorded["by_class"][victim]["net_gbp_decimal"]) + Decimal("1e-20")
        )
    registry = {"event_slug": "generated", "measures": measures, "accounting": recorded}
    with pytest.raises(export.ExportError, match="accounting differs"):
        export.accounting(registry)
