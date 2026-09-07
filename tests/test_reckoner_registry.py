"""Registry-consistency tests for the HMRC ready reckoner lane (#60).

The compute stage needs the managed policyengine.py environment; these
tests pin what is checkable anywhere — the registry validates against
its own schema, every measure joins an external claim verbatim, the
slug rule holds, the delta arithmetic is exact, the module imports
engine-free, and --dry-run completes without the engine.
"""

import ast
import builtins
import importlib.metadata
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


def _staged(measure, **kw):
    base = dict(
        year=2026,
        pe_delta_gbp=1.23e9,
        status="constructed",
        run_id="reckoner-mode2",
        engine_version="2.89.2",
        bundle="bundle-x",
        claim_id="4170013e721c13e0ddc1",
        computed_at="2026-08-17T00:00:00+00:00",
        construction="p: 1 -> 2 | heads income_tax",
        external_value=1.2e9,
    )
    base.update(kw)
    return rk.staged_row(measure, **base)


def test_staged_rows_use_the_campaign_contract():
    """The earlier shape could not be ingested at all: it named
    hmrc-personal-tax / revenue_effect / a string FY where DB claims are
    uk_hmrc / revenue_change / FY-END integers, had no computed_at or
    data_bundle, and the campaign ingester has no normalizer for family
    `reckoner`. claim_id-direct never needs one."""
    m = next(x for x in REGISTRY["measures"] if x["computability"] == "expressible")
    row = _staged(m)
    assert set(row["external_claim_match"]) == {"claim_id"}
    assert row["data_bundle"] == "bundle-x"
    assert row["computed_at"].startswith("2026-")
    assert row["run_id"] and row["pe_construction"]
    # `ok` is not even a valid ComparisonStatus
    from scorecard_db.models import ComparisonStatus

    assert ComparisonStatus(row["status"]) is ComparisonStatus.CONSTRUCTED


def test_staged_rows_stamp_the_executed_world():
    """PE executes current law; the claim keys HMRC's indexed baseline.
    Both are stamped so the guard can verify they differ."""
    m = next(x for x in REGISTRY["measures"] if x["computability"] == "expressible")
    assert _staged(m)["baseline_key"] == "current_law"
    assert REGISTRY["external_baseline_key"] == "hmrc_indexed_baseline_spring_2025"
    assert REGISTRY["executed_baseline_key"] == "current_law"


def test_annotations_are_strings_and_carry_the_magnitude_ratio():
    """The ingest contract is string[], the earlier shape was a mapping,
    and it dropped the registry note entirely. The |PE|/|HMRC| ratio is
    the established annotation on this family."""
    m = next(
        x
        for x in REGISTRY["measures"]
        if x["computability"] == "not_expressible" and x.get("note")
    )
    row = _staged(m, pe_delta_gbp=None, status="pe_gap")
    assert isinstance(row["annotations"], list)
    assert all(isinstance(a, str) for a in row["annotations"])
    assert any(a.startswith("registry note: ") for a in row["annotations"])
    assert any(
        "action: https://github.com/PolicyEngine/" in a for a in row["annotations"]
    )
    expressible = next(
        x for x in REGISTRY["measures"] if x["computability"] == "expressible"
    )
    ratios = [
        a for a in _staged(expressible)["annotations"] if "|PE|/|HMRC| ratio" in a
    ]
    assert len(ratios) == 1
    assert "magnitude_with_direction_in_label" in " ".join(
        _staged(expressible)["annotations"]
    )


def test_dry_run_completes_without_engine(capsys, monkeypatch):
    """The engine-free path, tested engine-FREE.

    This test used to rely on policyengine-uk simply not being
    installed. That made it ambient-dependent: with the engine present
    it took the engine branch instead, and once the installed engine
    drifted from the registry pin it failed on a guard it was never
    meant to exercise. CI never installs the engine, so CI stayed green
    while a developer machine that had it went red — the green tick
    meaning less than it looked, which is the thing #95 is about.

    Import is now blocked explicitly, so the test covers what it says.
    """
    real_import = builtins.__import__

    def no_engine(name, *args, **kwargs):
        if name == "policyengine_uk":
            raise ImportError("policyengine_uk blocked for this test")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", no_engine)
    rk.main(["--dry-run"])
    out = capsys.readouterr().out
    assert "dry run complete" in out
    assert "no sims" in out
    assert "path resolution deferred" in out


def test_the_pin_guard_refuses_a_mismatched_engine(monkeypatch):
    """The other half, which nothing covered: with an engine present
    whose version is NOT the pin, the run must refuse. A registry that
    resolved paths against a different engine proves nothing about the
    run it is pinning."""
    pytest.importorskip("policyengine_uk")
    monkeypatch.setattr(
        importlib.metadata, "version", lambda _name: "0.0.0-not-the-pin"
    )
    with pytest.raises(SystemExit, match="is pinned to"):
        rk.main(["--dry-run"])


def test_the_registry_pin_is_the_certified_engine():
    """Moving this is a deliberate re-certification, not a convenience.
    It is asserted here so a bump has to touch a test that says so."""
    assert REGISTRY["engine_pin"]["policyengine_uk"] == "2.89.2"


# --- the six review findings ------------------------------------------------


def test_the_merged_fourteen_are_the_anchor_set():
    """Wired in as it stood, all 14 FY2026-27 claim keys overlapped the
    campaign attaches on main: 11 would shadow them via latest-result
    selection and 3 — savings allowance, dividend allowance, savings
    starting-rate limit — would REGRESS to pe_gap despite exact executed
    paths already on main. Superseding staged campaign results is the
    #32-class doctrine violation."""
    anchors = rk.anchor_claim_ids()
    assert len(anchors) == 14
    resolved = {(f"m{i}", 2026): cid for i, cid in enumerate(sorted(anchors))}
    resolved[("a_new_measure", 2027)] = "not-an-anchor"
    manifest = rk.reconcile(resolved)
    assert len(manifest["retained"]) == 14
    assert len(manifest["new"]) == 1
    assert manifest["anchor_claims_not_reachable_from_this_registry"] == []


def test_reconciliation_refuses_to_drop_an_anchor():
    anchors = rk.anchor_claim_ids()
    partial = {(f"m{i}", 2026): cid for i, cid in enumerate(sorted(anchors)) if i > 0}
    with pytest.raises(ValueError, match="would not preserve"):
        rk.reconcile(partial)


def test_retained_claims_are_never_re_emitted():
    src = inspect.getsource(rk.main)
    assert "retained_claims" in src
    # the guard is a skip, not an overwrite
    assert "if claim_id in retained_claims:" in src
    assert "continue" in src.split("if claim_id in retained_claims:")[1][:400]


def test_declared_triage_equals_what_the_runtime_will_compute():
    """Three acknowledged partial, missing-leg reforms carried deltas and
    passed the compute gate: 27 ok / 48 gap against a declared 24 / 51."""
    triage = REGISTRY["computability_triage"]
    carrying = sum(1 for m in REGISTRY["measures"] if m["pe_reform_delta"])
    assert carrying == triage["carrying_a_delta"] == triage["expressible"] == 24
    assert triage["partial"] + triage["not_expressible"] == 51
    for m in REGISTRY["measures"]:
        if m["computability"] == "partial":
            assert not m["pe_reform_delta"], m["measure_key"]


def test_validate_rejects_a_partial_carrying_a_delta():
    bad = json.loads(json.dumps(REGISTRY))
    m = next(x for x in bad["measures"] if x["computability"] == "partial")
    m["pe_reform_delta"] = {"a.b": 0.01}
    m["delta_kind"] = "absolute"
    with pytest.raises(ValueError, match="partial .*but carries a delta"):
        rk.validate_registry(bad)


def test_employer_nics_read_their_own_head():
    """Both employer-NIC measures summed through `national_insurance`,
    where the committed campaign artifacts establish `ni_employer`."""
    employer = [
        m
        for m in REGISTRY["measures"]
        if m["program"] == "national_insurance"
        and m["pe_reform_delta"]
        and "employer" in m["hmrc_label"].lower()
    ]
    assert len(employer) == 2
    for m in employer:
        assert m["pe_head_variable"] == "ni_employer"
    # ...and every other delta-carrying measure names a head too
    for m in REGISTRY["measures"]:
        if m["pe_reform_delta"]:
            assert m["pe_head_variable"], m["measure_key"]


def test_the_validator_is_year_aware():
    """It checked only that SOME external claim joined, so a missing or
    duplicated FY passed."""
    bad = json.loads(json.dumps(REGISTRY))
    ext = json.loads(json.dumps(EXTERNALS))
    m = next(x for x in bad["measures"] if x["computability"] == "expressible")
    kept = [
        r
        for r in ext
        if not (
            r.get("metric") == "revenue_effect"
            and r.get("program") == m["program"]
            and r.get("subgroup") == m["hmrc_label"]
            and r.get("period") == "2027-28"
        )
    ]
    p = ROOT / "tests" / "_tmp_reckoner_externals.json"
    p.write_text(json.dumps(kept))
    try:
        with pytest.raises(ValueError, match="missing FY claims"):
            rk.validate_registry(bad, externals_path=p)
    finally:
        p.unlink()


def test_every_not_expressible_row_is_citable():
    """Descriptive gate #9: all 29 non-expressible rows carried no action
    link at all."""
    for m in REGISTRY["measures"]:
        if m["computability"] == "not_expressible":
            assert m["action_link"].startswith("https://github.com/PolicyEngine/")


def test_the_engine_pin_is_enforced_not_narrated():
    """The dry-run passed under whatever ambient policyengine-uk was
    installed (2.75.3) while the registry prose referenced 2.89.2, so
    resolving every path proved nothing about the run's engine."""
    assert REGISTRY["engine_pin"]["policyengine_uk"] == "2.89.2"
    src = inspect.getsource(rk.main)
    assert 'registry["engine_pin"]["policyengine_uk"]' in src
    assert "is installed but this registry" in src
    # and the managed sim's own reported version is checked too
    assert "the managed baseline sim reports engine" in src


def test_the_run_writes_a_checkable_manifest():
    src = inspect.getsource(rk.write_manifest)
    assert "sha256" in src and "reconciliation" in src
    assert "staged_sha256" in src
