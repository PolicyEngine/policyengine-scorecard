"""Registry-consistency tests for the HMRC ready reckoner lane (#60).

The compute stage needs the managed policyengine.py environment; these
tests pin what is checkable anywhere — the registry validates against
its own schema, every measure joins an external claim verbatim, the
slug rule holds, the delta arithmetic is exact, the module imports
engine-free, and --dry-run completes without the engine.
"""

import ast
import inspect
import json
from pathlib import Path

import pytest

from pipeline import compute_uk_reckoner as rk

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = json.loads((ROOT / "data" / "uk" / "hmrc_reckoner_reforms.json").read_text())
EXTERNALS = json.loads(
    (ROOT / "data" / "externals" / "hmrc-personal-tax.json").read_text()
)
RECKONER_CLAIMS = [r for r in EXTERNALS if r["metric"] == "revenue_effect"]


def test_module_imports_without_engine():
    names = []
    for node in ast.parse(inspect.getsource(rk)).body:
        if isinstance(node, ast.Import):
            names += [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.append(node.module)
    tops = {m.split(".")[0] for m in names}
    assert "policyengine" not in tops and "policyengine_uk" not in tops


def test_registry_validates():
    assert rk.validate_registry(REGISTRY) == len(REGISTRY["measures"])


def test_every_external_reckoner_label_is_triaged():
    """The registry covers the WHOLE external population: every
    (program, label) the adapter emits has a computability verdict —
    coverage gaps are labelled, never silent."""
    ext = {(r["program"], r["subgroup"]) for r in RECKONER_CLAIMS}
    reg = {(m["program"], m["hmrc_label"]) for m in REGISTRY["measures"]}
    assert reg == ext


def test_expressible_measures_carry_full_delta_specs():
    for m in REGISTRY["measures"]:
        if m["computability"] == "expressible":
            assert m["pe_reform_delta"], m["measure_key"]
            assert m["delta_kind"] in ("absolute", "relative")


def test_rate_deltas_are_fractions_not_percentage_points():
    """A 1p/1pp change is 0.01 as an engine fraction; a delta of 1.0 on
    a .rate path would be a 100-point change emitted under a 1p label."""
    for m in REGISTRY["measures"]:
        for path, v in (m["pe_reform_delta"] or {}).items():
            if path.endswith(".rate") or (
                ".rates." in path and path.endswith(("main", "additional", "employer"))
            ):
                assert abs(v) <= 0.05, f"{m['measure_key']}: {path} delta {v}"


def test_directioned_labels_carry_signed_deltas():
    """'Decrease ... (cost)'/'(yield)' labels state the direction; the
    delta's sign must match it (increase => positive delta on the
    parameter, decrease => negative)."""
    for m in REGISTRY["measures"]:
        deltas = m["pe_reform_delta"]
        if not deltas or m["change_direction"] == "unsigned":
            continue
        sign = 1 if m["change_direction"] == "increase" else -1
        for path, v in deltas.items():
            assert v * sign > 0, (
                f"{m['measure_key']}: {path} delta {v} contradicts {m['change_direction']}"
            )


def test_slug_rule_matches_measure_keys():
    for m in REGISTRY["measures"]:
        assert (
            m["measure_key"]
            == f"reckoner_202506__{m['program']}__{rk.slug(m['hmrc_label'])}"
        )


def test_validate_rejects_unjoined_measures():
    bad = json.loads(json.dumps(REGISTRY))
    bad["measures"][0]["hmrc_label"] = "A label HMRC never printed"
    with pytest.raises(ValueError, match="no external revenue_effect claim"):
        rk.validate_registry(bad)


def test_validate_rejects_expressible_without_delta():
    bad = json.loads(json.dumps(REGISTRY))
    m = next(x for x in bad["measures"] if x["computability"] == "expressible")
    m["pe_reform_delta"] = None
    with pytest.raises(ValueError, match="expressible but pe_reform_delta is null"):
        rk.validate_registry(bad)


def test_reform_values_arithmetic():
    class Node:
        def __init__(self, v):
            self.v = v

        def __call__(self, _):
            return self.v

    m_abs = {"pe_reform_delta": {"a.b": 100}, "delta_kind": "absolute"}
    assert rk.reform_values(m_abs, {"a.b": Node(12570)}, 2026) == {"a.b": 12670}
    m_rel = {"pe_reform_delta": {"a.b": -0.10}, "delta_kind": "relative"}
    assert rk.reform_values(m_rel, {"a.b": Node(50270)}, 2026) == {
        "a.b": pytest.approx(45243.0)
    }


def test_staged_row_carries_the_verbatim_join_and_sign_annotations():
    m = next(x for x in REGISTRY["measures"] if x["computability"] == "expressible")
    row = rk.staged_row(m, 2026, 1.23e9, "ok", "runid", "2.89.2", "bundle-x")
    assert row["external_claim_match"]["subgroup"] == m["hmrc_label"]
    assert row["external_claim_match"]["period"] == "2026-27"
    assert row["basis"] == "static"
    assert (
        row["annotations"]["sign_convention_external"]
        == "magnitude_with_direction_in_label"
    )


def test_dry_run_completes_without_engine(capsys):
    rk.main(["--dry-run"])
    out = capsys.readouterr().out
    assert "dry run complete" in out
    assert "no sims" in out
