"""PE-UK counterparts to the HMRC ready reckoner (mode 2, #60).

The reckoner sibling of the OBR costings lane: HMRC's *direct effects of
illustrative tax changes* (June 2025 edition) are one-parameter reform
deltas against HMRC's indexed baseline, already ingested as external
claims by sources/hmrc-personal-tax/adapter.py. This pipeline computes
the PolicyEngine-UK static delta for each expressible measure in
data/uk/hmrc_reckoner_reforms.json on the certified populace-uk bundle.

Binding contract (same as pipeline/compute_uk_counterparts.py):
  - policyengine.py managed_microsimulation() on the certified
    populace-uk bundle, under the machine-wide sim lock:
    ``simlock -- .venv-pe/bin/python pipeline/compute_uk_reckoner.py``
  - One baseline sim per policy year, reused across measures; one reform
    sim per (measure, year). Reform parameter values are BASELINE VALUE
    PLUS DELTA read from the live parameter tree at each year — the
    registry stores deltas (absolute or relative), never absolute
    schedules, because the reckoner's own construction is
    "baseline + illustrative change".
  - Registry rows whose parameter paths fail to resolve on the engine
    are demoted to ``pe_gap`` rows: a delta is never applied to a
    guessed parameter. paths_verified: false rows MUST resolve in
    --dry-run before any sim (see the registry's
    parameter_path_verification note).
  - Emits per-run JSON artifacts (one per measure x year) and staged
    rows under the campaign ingest contract
    (results/uk/staged/reckoner.jsonl: external_claim_match descriptor
    exactly as the external rows carry it — source hmrc-personal-tax,
    program, subgroup = verbatim HMRC label — plus engine_version, full
    bundle id, status, construction, run_id, annotations).

Sign orientation: HMRC publishes magnitudes with direction in the
English label (sign_convention magnitude_with_direction_in_label; see
the adapter docstring). Staged rows therefore carry the SIGNED PE delta
(reform - baseline revenue, positive = gain to the Exchequer) plus the
registry's change_direction/section_direction annotations, and the
downstream comparison orients the external magnitude from those fields —
this pipeline never flips the external value.

Basis axis: reckoner rows for the income-tax rates are post-behavioural
(HMRC nets large behavioural offsets at the additional rate); PE deltas
are static. Every staged row carries basis: static and the comparison
inherits benchmark_class different_model. No score-like summary.

Modes:
  --dry-run   validate the registry (schema, slug rule, join against
              data/externals/hmrc-personal-tax.json) and, if
              policyengine-uk is importable, resolve every non-null
              parameter path against the live tree. No sims, no output.
  (default)   full compute; requires the managed environment.

Staging and reconciliation. Rows stage through the CAMPAIGN contract in
its claim_id-direct form (results/uk/staged/reckoner.jsonl), because the
campaign ingester has no normalizer for a `reckoner` family and DB claims
are uk_hmrc / revenue_change / FY-END integers — not the adapter-side
hmrc-personal-tax / revenue_effect / string-FY descriptor. Each
(measure, year) resolves to exactly ONE ingested claim or raises.

Before anything is emitted the run RECONCILES against the merged
campaign's 14 resolved reckoner results: those claims are the anchor
set, this lane emits nothing for them, and the reconciliation refuses to
run if any of the 14 is unreachable. Three of them (savings allowance,
dividend allowance, savings starting-rate limit) carry exact executed
parameter paths this registry cannot express, so a competing row would
not merely shadow them by latest-result selection — it would regress
them to pe_gap. The manifest (results/uk/reckoner/manifest.json) records
retained vs new plus a sha256 over every artifact and the staged file.

Baseline honesty. The run executes CURRENT LAW; the claim keys HMRC's
indexed baseline. Both keys are stamped on the staged row and the
artifact so the guard can VERIFY they differ, and every successful row
is status `constructed` — `ok` is not a valid ComparisonStatus.

Engine pin. The registry pins policyengine-uk 2.89.2 and the run refuses
any other version, on both the import and the managed sim's own reported
version. The earlier dry-run passed under whatever ambient engine was
installed (2.75.3) while the registry prose referenced 2.89.2, so
resolving every path proved nothing about the engine the run would use.

HONESTY: this script has never been executed against a managed
policyengine.py environment — no certified populace-uk bundle exists on
the authoring machine. Everything below the engine boundary (registry
schema, join, delta arithmetic, slug rule, staged-row shape) is covered
by tests/test_reckoner_registry.py; the engine boundary itself is
unverified until the first real run, and the dry-run path-resolution
gate exists precisely so that first run cannot silently compute against
a wrong parameter.
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "data" / "uk" / "hmrc_reckoner_reforms.json"
EXTERNALS = ROOT / "data" / "externals" / "hmrc-personal-tax.json"
STAGED_OUT = ROOT / "results" / "uk" / "staged" / "reckoner.jsonl"
ARTIFACT_DIR = ROOT / "results" / "uk" / "reckoner"

# Reckoner forecast window: 2026-27 to 2028-29 -> PE calendar-year proxies.
YEARS = (2026, 2027, 2028)

t0 = time.time()


def log(msg):
    print(f"[{time.time() - t0:7.1f}s] {msg}", flush=True)


def slug(label):
    """Label slug for measure keys (reckoner_202506__<program>__<slug>).

    The program prefix is mandatory: HMRC prints identical change labels
    under different tax heads (VAT and IPT both carry "Change standard
    rate by 1 percentage point"), and a label-only key would join one
    reform world to two programs — the defect class the #48 review
    caught in the harvest ingest."""
    s = label.lower()
    s = re.sub(r"[£%]", "", s)
    s = re.sub(r"[^a-z0-9]+", "_", s).strip("_")
    return s[:60].rstrip("_")


def load_registry(path=REGISTRY):
    return json.loads(Path(path).read_text())


def validate_registry(registry, externals_path=EXTERNALS):
    """Schema + join validation; raises with every defect listed.

    Checkable without the engine: measure_key uniqueness and slug rule,
    computability vocabulary, expressible => non-null delta dict with
    finite numeric deltas and a delta_kind, null-delta rows carry a
    note, and every (program, hmrc_label) joins an external
    revenue_effect claim verbatim — the registry may never advertise a
    measure the external side does not carry.
    """
    errors = []
    ext = json.loads(Path(externals_path).read_text())
    ext_rows = [r for r in ext if r["metric"] == "revenue_effect"]
    ext_keys = {(r["program"], r["subgroup"]) for r in ext_rows}
    # YEAR-AWARE: the external side carries one claim per measure per
    # forecast year, and the validator used to check only that SOME claim
    # joined — so a missing or duplicated FY passed silently and the lane
    # would have staged a row with nothing to attach to.
    ext_years = {}
    for r in ext_rows:
        ext_years.setdefault((r["program"], r["subgroup"]), []).append(r["period"])
    seen_keys = set()
    for m in registry["measures"]:
        k = m["measure_key"]
        if k in seen_keys:
            errors.append(f"duplicate measure_key {k}")
        seen_keys.add(k)
        if k != f"reckoner_202506__{m['program']}__{slug(m['hmrc_label'])}":
            errors.append(f"{k}: violates the slug rule for {m['hmrc_label']!r}")
        if m["computability"] not in ("expressible", "partial", "not_expressible"):
            errors.append(f"{k}: bad computability {m['computability']!r}")
        if (m["program"], m["hmrc_label"]) not in ext_keys:
            errors.append(f"{k}: no external revenue_effect claim joins it")
        else:
            periods = ext_years[(m["program"], m["hmrc_label"])]
            want = {f"{y}-{str(y + 1)[2:]}" for y in YEARS}
            got = set(periods)
            if len(periods) != len(got):
                errors.append(f"{k}: external side has duplicate FY claims {periods}")
            if not want <= got:
                errors.append(
                    f"{k}: external side is missing FY claims {sorted(want - got)}"
                )
        deltas = m["pe_reform_delta"]
        if m["computability"] == "expressible" and not deltas:
            errors.append(f"{k}: expressible but pe_reform_delta is null")
        if m["computability"] == "not_expressible" and deltas:
            errors.append(f"{k}: not_expressible yet carries a reform delta")
        if deltas:
            if m["delta_kind"] not in ("absolute", "relative"):
                errors.append(f"{k}: delta_kind {m['delta_kind']!r}")
            for path, v in deltas.items():
                if not isinstance(v, (int, float)) or v != v or v == 0:
                    errors.append(f"{k}: non-finite/zero delta at {path}")
                if m["delta_kind"] == "relative" and abs(v) > 0.5:
                    errors.append(f"{k}: implausible relative delta {v} at {path}")
        if not deltas and m["computability"] != "expressible" and not m.get("note"):
            errors.append(f"{k}: null delta without an explanatory note")
        # A partial measure must never carry a delta: applying only the
        # legs whose paths are identified computes a DIFFERENT reform
        # from the one the label states, and it is what made the runtime
        # produce 27 ok / 48 gap against a declared 24 / 51.
        if m["computability"] == "partial" and deltas:
            errors.append(
                f"{k}: partial (missing leg) but carries a delta — a partial "
                "multi-leg reform is a different reform; emit a cited gap"
            )
        if deltas and not m.get("pe_head_variable"):
            errors.append(f"{k}: carries a delta but names no pe_head_variable")
        if m["computability"] == "not_expressible" and not m.get("action_link"):
            errors.append(f"{k}: not_expressible without an action_link (gate #9)")
    # The declared triage must equal what the runtime will actually do.
    triage = registry.get("computability_triage") or {}
    carrying = sum(1 for m in registry["measures"] if m["pe_reform_delta"])
    if triage.get("carrying_a_delta") != carrying:
        errors.append(
            f"declared carrying_a_delta {triage.get('carrying_a_delta')} != "
            f"{carrying} measures that actually carry one"
        )
    if triage.get("expressible") != carrying:
        errors.append(
            f"declared expressible {triage.get('expressible')} != {carrying} "
            "measures carrying a delta — the runtime computes the deltas, so "
            "the two are the same number or the triage is prose"
        )
    if errors:
        raise ValueError(
            f"registry invalid ({len(errors)} defects):\n  " + "\n  ".join(errors)
        )
    return len(registry["measures"])


def resolve_paths_or_gap(measure, parameters):
    """Split a measure's delta paths into (resolved, missing) on the live
    engine parameter tree. Bracket syntax path[i].field follows the OBR
    registry convention. Any missing path demotes the WHOLE measure to
    pe_gap — a partial application of a multi-leg delta is a different
    reform than the one the label states."""
    resolved, missing = {}, []
    for path in measure["pe_reform_delta"] or {}:
        node = parameters
        try:
            for part in re.split(r"\.(?![^\[]*\])", path):
                mbr = re.fullmatch(r"(.+)\[(\d+)\]", part)
                if mbr:
                    node = getattr(node, mbr.group(1)).brackets[int(mbr.group(2))]
                else:
                    node = getattr(node, part)
            resolved[path] = node
        except AttributeError:
            missing.append(path)
    return resolved, missing


def reform_values(measure, resolved, year):
    """Absolute reform value per path: live baseline value(year) + delta
    (absolute) or * (1 + delta) (relative). Reads the engine's own
    baseline so the delta is applied to what the certified world
    actually uses, mirroring HMRC's baseline-plus-change construction."""
    out = {}
    for path, node in resolved.items():
        # Baseline read at a single mid-year instant while the reform
        # spans the full calendar year: identical for flat-year
        # parameters (every current registry path), but a relative delta
        # on a parameter that steps mid-year would scale the 06-01 value
        # only — revisit if such a path enters the registry.
        base = float(node(f"{year}-06-01"))
        delta = measure["pe_reform_delta"][path]
        if measure["delta_kind"] == "relative":
            out[path] = base * (1.0 + delta)
        else:
            out[path] = base + delta
    return out


def fy_label(year):
    """PE calendar year Y proxies HMRC financial year Y-(Y+1)."""
    return f"{year}-{str(year + 1)[2:]}"


def annotations_for(measure, year, pe_value, external_value=None):
    """Annotations as the ingest contract wants them: a LIST OF STRINGS.

    The earlier mapping shape would not have survived the campaign
    ingester (``annotations=row.get("annotations", [])`` into
    ``PEResult.annotations``, a list), and it dropped the registry's
    free-text note entirely. The |PE|/|HMRC| magnitude ratio is the
    established annotation on this family — the merged 14 rows all carry
    it — and it is what makes a magnitude-with-direction-in-label
    comparison readable at all.
    """
    out = [
        "PE CY static accrual vs HMRC projected FY direct effects "
        "(first-year cash vs fuller-year; TIE/behavioural in the HMRC "
        "reckoner per their methodology notes); |magnitude| ratios",
        f"external sign convention: magnitude_with_direction_in_label "
        f"(change_direction {measure['change_direction']}, section_direction "
        f"{measure['section_direction']})",
        f"CY {year} proxies FY {fy_label(year)}",
        "basis: static (PE) vs post-behavioural (HMRC reckoner)",
    ]
    if measure.get("note"):
        out.append(f"registry note: {measure['note']}")
    if measure.get("action_link"):
        out.append(f"action: {measure['action_link']}")
    if pe_value is not None and external_value:
        ratio = abs(pe_value) / abs(external_value)
        out.append(
            f"FY {fy_label(year)} external value {external_value} "
            f"(|PE|/|HMRC| ratio {ratio})"
        )
    return out


def staged_row(
    measure,
    year,
    pe_delta_gbp,
    status,
    run_id,
    engine_version,
    bundle,
    claim_id,
    computed_at,
    construction,
    external_value=None,
):
    """One row in the CAMPAIGN staging contract (ingest_campaign).

    The earlier shape could not be ingested at all: it named
    ``hmrc-personal-tax`` / ``revenue_effect`` / a string FY where DB
    claims are ``uk_hmrc`` / ``revenue_change`` / FY-END integers with
    exact conditions, it had no ``computed_at`` or ``data_bundle``, its
    annotations were a mapping, and the campaign ingester has no
    normalizer for family ``reckoner``. So this stages through the ONE
    form that never needs a family normalizer — claim_id-direct, exactly
    as produce_campaign_uk resolves the merged 14.
    """
    return {
        "external_claim_match": {"claim_id": claim_id},
        "measure_key": measure["measure_key"],
        "pe_value": pe_delta_gbp,
        # `constructed`, not `ok`: PE executes CURRENT LAW while the claim
        # keys HMRC's indexed baseline, so the two worlds differ and the
        # comparison is a construction. `ok` is not even a valid
        # ComparisonStatus. The merged campaign rows model this exactly.
        "status": status,
        "pe_construction": construction,
        "run_id": run_id,
        "engine_version": engine_version,
        "data_bundle": bundle,
        "computed_at": computed_at,
        # The world the run ACTUALLY executed. The claim keys
        # hmrc_indexed_baseline_spring_2025; stamping the executed world
        # is what lets the guard verify they differ rather than assume.
        "baseline_key": "current_law",
        "annotations": annotations_for(measure, year, pe_delta_gbp, external_value),
    }


# The merged campaign's resolved reckoner staging: the anchor set this
# lane must not disturb. 14 rows, already attached to ingested claims on
# main, three of them (savings allowance, dividend allowance, savings
# starting-rate limit) with EXACT executed parameter paths this
# registry cannot express — so a competing reckoner row would not merely
# shadow them via latest-result selection, it would REGRESS them to
# pe_gap. Superseding staged campaign results is the #32-class doctrine
# violation; the reconciliation below makes the retained/new split
# explicit and testable rather than an ordering accident.
ANCHOR_STAGING = (
    ROOT / "sources" / "campaign-20260802" / "uk_resolved" / "hmrc_reckoner_t2.jsonl"
)


def anchor_claim_ids(path=ANCHOR_STAGING):
    """claim_ids the merged campaign already answers."""
    if not Path(path).exists():
        return set()
    return {
        json.loads(line)["external_claim_match"]["claim_id"]
        for line in Path(path).read_text().splitlines()
        if line.strip()
    }


def reconcile(resolved_claims, anchors=None):
    """Split every (measure_key, year) cell into retained vs new.

    `resolved_claims` maps (measure_key, year) -> claim_id. A cell whose
    claim already carries a merged campaign result is RETAINED: this lane
    emits nothing for it. Everything else is NEW and this lane owns it.
    The manifest is returned (and written beside the staging) so the
    disposition is a checked artifact, not an assumption about which
    ingest happens to run last.
    """
    anchors = anchor_claim_ids() if anchors is None else anchors
    retained, new = [], []
    for (measure_key, year), claim_id in sorted(resolved_claims.items()):
        entry = {"measure_key": measure_key, "year": year, "claim_id": claim_id}
        (retained if claim_id in anchors else new).append(entry)
    covered = {e["claim_id"] for e in retained}
    missing = sorted(anchors - covered)
    manifest = {
        "anchor_claims": len(anchors),
        "retained": retained,
        "new": new,
        "anchor_claims_not_reachable_from_this_registry": missing,
    }
    if len(covered) != len(anchors):
        raise ValueError(
            f"reconciliation would not preserve the merged campaign's "
            f"{len(anchors)} reckoner results: {len(missing)} of them are not "
            f"reachable from this registry ({missing[:5]}). The anchor set is "
            "preserved or the lane does not ship — superseding staged "
            "campaign results is the #32-class doctrine violation."
        )
    return manifest


def resolve_claim_id(db, measure, year):
    """The ONE ingested claim this (measure, year) answers, or raise.

    DB claims are ``uk_hmrc`` / ``revenue_change`` / FY-END integer
    periods with exact conditions — not the adapter-side
    ``hmrc-personal-tax`` / ``revenue_effect`` / string-FY the earlier
    staging named, which could not have matched anything. Resolution is
    exactly-one-match; 0 or 2+ raises, exactly as produce_campaign_uk
    resolves the merged 14.
    """
    rows = db.conn.execute(
        "SELECT claim_id FROM external_scores"
        " WHERE source = 'uk_hmrc' AND metric = 'revenue_change'"
        "   AND period = ?"
        "   AND json_extract(conditions, '$.fy') = ?"
        "   AND json_extract(conditions, '$.program') = ?"
        "   AND json_extract(conditions, '$.option') = ?",
        (year + 1, fy_label(year), measure["program"], measure["hmrc_label"]),
    ).fetchall()
    if len(rows) != 1:
        raise ValueError(
            f"{measure['measure_key']} FY{fy_label(year)}: {len(rows)} ingested "
            "uk_hmrc claims match — resolution is exactly-one-match, never a "
            "descriptor that happens to hit something"
        )
    return rows[0][0]


_EXTERNALS_CACHE = {}


def external_value_for(measure, year, externals_path=EXTERNALS):
    """The HMRC published value for this measure and year, for the
    |PE|/|HMRC| ratio annotation."""
    key = str(externals_path)
    if key not in _EXTERNALS_CACHE:
        _EXTERNALS_CACHE[key] = json.loads(Path(externals_path).read_text())
    for r in _EXTERNALS_CACHE[key]:
        if (
            r["metric"] == "revenue_effect"
            and r["program"] == measure["program"]
            and r["subgroup"] == measure["hmrc_label"]
            and r["period"] == fy_label(year)
        ):
            return r["value"]
    return None


def write_manifest(manifest, staged, artifacts, run_id, computed_at):
    """The run's own manifest: what was retained, what is new, and a
    sha256 over every artifact and the staged file, so a re-run is
    checkable rather than merely repeatable."""
    import hashlib

    def digest(path):
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()

    payload = {
        "run_id": run_id,
        "computed_at": computed_at,
        "staged_rows": len(staged),
        "constructed": sum(1 for r in staged if r["status"] == "constructed"),
        "pe_gap": sum(1 for r in staged if r["status"] == "pe_gap"),
        "reconciliation": manifest,
        "artifacts": {Path(p).name: digest(p) for p in sorted(map(str, artifacts))},
        "staged_sha256": digest(STAGED_OUT),
    }
    (ARTIFACT_DIR / "manifest.json").write_text(json.dumps(payload, indent=1) + "\n")
    return payload


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--registry", default=REGISTRY, type=Path)
    args = ap.parse_args(argv)

    registry = load_registry(args.registry)
    n = validate_registry(registry)
    log(f"registry valid: {n} measures")

    pin = registry["engine_pin"]["policyengine_uk"]
    try:
        import policyengine_uk  # type: ignore

        installed = getattr(policyengine_uk, "__version__", None)
        if installed != pin:
            # The earlier dry-run passed under whatever ambient version
            # happened to be installed (2.75.3) while the registry prose
            # referenced 2.89.2 — so resolving every path proved nothing
            # about the engine the real run would use.
            raise SystemExit(
                f"policyengine-uk {installed} is installed but this registry "
                f"is pinned to {pin}. Path resolution against a different "
                "engine proves nothing about the run; install the pin or "
                "re-verify and move the pin deliberately."
            )
        system = policyengine_uk.CountryTaxBenefitSystem()
        parameters = system.parameters
        engine = True
    except ImportError:
        parameters = None
        engine = False

    if engine:
        gaps = []
        for m in registry["measures"]:
            if not m["pe_reform_delta"]:
                continue
            _, missing = resolve_paths_or_gap(m, parameters)
            if missing:
                gaps.append((m["measure_key"], missing))
        for k, missing in gaps:
            log(f"  UNRESOLVED {k}: {missing}")
        if args.dry_run and gaps:
            raise SystemExit(
                f"{len(gaps)} measures have unresolvable parameter paths; "
                "fix the registry before computing (a delta is never applied "
                "to a guessed parameter)."
            )
    else:
        log("policyengine-uk not importable: path resolution deferred to the run")

    if args.dry_run:
        log("dry run complete: no sims, no output")
        return

    # Full compute: managed sims on the certified bundle. UNVERIFIED
    # against an installed policyengine.py — mirrors the documented
    # binding surface (see module docstring and compute_uk_counterparts).
    import datetime

    import policyengine as pe  # type: ignore

    from scorecard_db.db import ScorecardDB

    db = ScorecardDB(ROOT / "data" / "scorecard.db")
    resolved_claims = {}
    for m in registry["measures"]:
        for year in YEARS:
            resolved_claims[(m["measure_key"], year)] = resolve_claim_id(db, m, year)
    manifest = reconcile(resolved_claims)
    log(
        f"reconciliation: {len(manifest['retained'])} retained (already "
        f"answered by the merged campaign), {len(manifest['new'])} new"
    )
    retained_claims = {e["claim_id"] for e in manifest["retained"]}

    run_id = "reckoner-mode2"
    computed_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    STAGED_OUT.parent.mkdir(parents=True, exist_ok=True)
    staged = []
    artifacts = []
    for year in YEARS:
        base_sim = pe.uk.managed_microsimulation()
        bundle = str(getattr(base_sim, "policyengine_bundle", None))
        engine_version = getattr(base_sim, "engine_version", None)
        if engine_version != pin:
            raise SystemExit(
                f"the managed baseline sim reports engine {engine_version!r}, "
                f"not the pinned {pin!r}"
            )
        base_rev = {}
        for m in registry["measures"]:
            claim_id = resolved_claims[(m["measure_key"], year)]
            if claim_id in retained_claims:
                # The merged campaign already answers this claim with an
                # EXACT executed path. Emitting here would shadow it via
                # latest-result selection, or regress it to pe_gap.
                continue
            external_value = external_value_for(m, year)
            head_var = m.get("pe_head_variable")
            if (
                m["computability"] != "expressible"
                or not m["pe_reform_delta"]
                or head_var is None
            ):
                staged.append(
                    staged_row(
                        m,
                        year,
                        None,
                        "pe_gap",
                        run_id,
                        engine_version,
                        bundle,
                        claim_id,
                        computed_at,
                        f"pe_gap:{m['computability']}",
                        external_value,
                    )
                )
                continue
            resolved, missing = resolve_paths_or_gap(
                m, base_sim.tax_benefit_system.parameters
            )
            if missing:
                staged.append(
                    staged_row(
                        m,
                        year,
                        None,
                        "pe_gap",
                        run_id,
                        engine_version,
                        bundle,
                        claim_id,
                        computed_at,
                        f"pe_gap:unresolved_paths {sorted(missing)}",
                        external_value,
                    )
                )
                continue
            values = reform_values(m, resolved, year)
            if head_var not in base_rev:
                base_rev[head_var] = float(base_sim.calculate(head_var, year).sum())
            reform = {p: {f"{year}-01-01.{year}-12-31": v} for p, v in values.items()}
            sim = pe.uk.managed_microsimulation(reform=reform)
            reform_rev = float(sim.calculate(head_var, year).sum())
            # positive = gain to the Exchequer; child benefit is spending,
            # so its Exchequer gain is the negative of the spending change
            delta = reform_rev - base_rev[head_var]
            if m["program"] == "child_benefit":
                delta = -delta
            construction = (
                " | ".join(
                    f"{path}: {float(node(f'{year}-06-01'))} -> {values[path]}"
                    for path, node in sorted(resolved.items())
                )
                + f" | heads {head_var}"
            )
            artifact = {
                "measure_key": m["measure_key"],
                "year": year,
                "run_id": run_id,
                "claim_id": claim_id,
                "reform": reform,
                "head_variable": head_var,
                "baseline_value": base_rev[head_var],
                "reform_value": reform_rev,
                "pe_delta_gbp": delta,
                "bundle": bundle,
                "engine_version": engine_version,
                # The world the RUN executed, stamped on the artifact as
                # well as the staged row: the claim keys HMRC's indexed
                # baseline and the run executes current law, so the guard
                # must be able to verify the difference rather than assume
                # it.
                "baseline_key": "current_law",
                "claim_baseline_key": registry["external_baseline_key"],
                "computed_at": computed_at,
            }
            path = ARTIFACT_DIR / f"{m['measure_key']}_{year}.json"
            path.write_text(json.dumps(artifact, indent=1) + "\n")
            artifacts.append(path)
            staged.append(
                staged_row(
                    m,
                    year,
                    delta,
                    "constructed",
                    run_id,
                    engine_version,
                    bundle,
                    claim_id,
                    computed_at,
                    construction,
                    external_value,
                )
            )
            del sim
        del base_sim
        log(f"year {year} done ({len(staged)} staged rows so far)")
    db.close()

    with open(STAGED_OUT, "w") as f:
        for row in staged:
            f.write(json.dumps(row) + "\n")
    write_manifest(manifest, staged, artifacts, run_id, computed_at)
    log(f"wrote {len(staged)} staged rows -> {STAGED_OUT}")


if __name__ == "__main__":
    main(sys.argv[1:])
