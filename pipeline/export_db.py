"""Export the Scorecard database into the app's static JSON feeds.

scorecard.db is the source of truth — claims × latest PE result × diagnoses,
via the `comparisons` view. This renders it into:

  data/export/index.json          sources index + the four home tiles (#9)
  data/export/sources/<id>.json   one slice per source: meta, facets,
                                  publication pool, unified rows

and copies them into app/public/data/ next to lanes.json / exhibits.json.
Any source ingested into the DB later (e.g. UK adapters, issue #3) appears
automatically: unknown source ids get registry-fallback metadata derived
from the DB itself.

Two Urban-only presentation extras are joined from the platform pipeline
output by reconstructing claim ids with scorecard_db.ingest_platform._probe
(the same validated mapping used at ingest): 2026 projections, which stay
app-layer by design (a 2023 claim describes one period), and the batch-1
divergence diagnoses in data/diagnoses_rows.json. Valueless statuses
(pe_gap / not_computed) are NOT joined here — run
`python3 scorecard_db/ingest_platform.py data/scorecard.db
--backfill-valueless` (module form: `python3 -m scorecard_db.ingest_platform
… `) once so the DB itself carries a status for every unsuppressed claim.

Register rules (issue #9 latest comments, binding): descriptive throughout.
Tolerance bands are descriptive distance bins. Consumed-target / seed rows
are labeled and excluded from every aggregate agreement figure. A diagnosis
is presented normatively (pe_gap / external_issue) only when action_link
cites a known issue; the export emits `normative` per diagnosis and the app
gates issue-class chips on it.
"""

from __future__ import annotations

import json
import random
import shutil
import sqlite3
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scorecard_db.ingest_platform import _probe  # noqa: E402
from scorecard_db.models import Metric  # noqa: E402
from scorecard_db.relationships import effective_relationship  # noqa: E402

DATA = ROOT / "data"
OUT = DATA / "export"
APP_DATA = ROOT / "app" / "public" / "data"

RANDOM_STRAND_SEED = 20260802
RANDOM_STRAND_N = 200

# ---------------------------------------------------------------------------
# Source registry: display metadata per source id. Everything stated here is
# grounded in sources/ (source.json, harvest NOTES.md/COLLATION.md) or the
# publication rows themselves. Unknown ids fall back to DB-derived entries so
# new ingests (UK lanes) surface without touching this file.
# ---------------------------------------------------------------------------


def _urban_meta() -> dict:
    s = json.loads(
        (ROOT / "sources" / "urban-sotsn" / "source.json").read_text()
    )
    return {
        "name": s["name"],
        "org": s["organization"],
        "model": s["model"]["name"],
        "method": s["model"]["method"],
        "url": s["url"],
        "fetched": s["fetched"],
        "period": s["period"],
        "diagnosis_upstream": s.get("diagnosis_upstream"),
    }


HARVEST = "sources/harvest-2026-08-02"
SOURCE_META: dict[str, dict] = {
    "urban_sotsn": _urban_meta(),
    "jct": {
        "name": "Joint Committee on Taxation",
        "org": "US Congress",
        "model": "JCT conventional revenue estimates",
        "method": "Per-provision conventional revenue tables (JCX series), "
        "fiscal years 2025–2034. Rows passed column-count validation and a "
        "horizontal checksum (years sum to the printed span total); net "
        "totals matched published figures.",
        "url": "https://www.jct.gov/",
        "fetched": "2026-08-02",
        "harvest_dir": f"{HARVEST}/jct",
    },
    "cbo": {
        "name": "Congressional Budget Office",
        "org": "US Congress",
        "model": "CBO baseline projections and cost estimates",
        "method": "February-2026 outlook baseline detail (program outlays, "
        "participation, benefit statistics, and a 330-row individual income "
        "tax return walk) plus cost-estimate claims. 317 rows were "
        "pre-verified at staging against policyengine-us calibration "
        "parameters and labeled consumed_as_target.",
        "url": "https://www.cbo.gov/",
        "fetched": "2026-08-02",
        "harvest_dir": f"{HARVEST}/cbo",
    },
    "tpc": {
        "name": "Urban-Brookings Tax Policy Center",
        "org": "Urban Institute / Brookings Institution",
        "model": "TPC microsimulation model",
        "method": "T-series distribution and revenue tables (Senate-OBBBA "
        "block, CTC option sets, American Family Act, tariffs). Values "
        "verbatim from published XLS, including TPC's unrounded twins.",
        "url": "https://www.taxpolicycenter.org/",
        "fetched": "2026-08-02",
        "harvest_dir": f"{HARVEST}/tpc",
    },
    "tax_foundation": {
        "name": "Tax Foundation",
        "org": "Tax Foundation",
        "model": "Taxes and Growth model",
        "method": "OBBBA and TCJA-permanence revenue estimates "
        "(conventional and dynamic, never mixed) plus the July-2026 tariff "
        "tracker. Calendar-vs-fiscal basis is unstated on some tables and "
        "flagged per row.",
        "url": "https://taxfoundation.org/",
        "fetched": "2026-08-02",
        "harvest_dir": f"{HARVEST}/tax_foundation",
    },
    "pwbm": {
        "name": "Penn Wharton Budget Model",
        "org": "University of Pennsylvania",
        "model": "PWBM dynamic OLG + microsimulation",
        "method": "OBBBA (signed and House variants), Social Security "
        "benefit-tax elimination, KYPA/WATCA, and TCJA-extension-baseline "
        "option sets. Distribution rows measure after-tax-and-transfer "
        "income; some tables score against a TCJA-extension baseline "
        "(labeled per row).",
        "url": "https://budgetmodel.wharton.upenn.edu/",
        "fetched": "2026-08-02",
        "harvest_dir": f"{HARVEST}/pwbm",
    },
    "budget_lab": {
        "name": "The Budget Lab at Yale",
        "org": "Yale University",
        "model": "Budget Lab tax microsimulation",
        "method": "Reconciliation distributional workbook (including the "
        "transfer-side complement), 16-scenario CTC options under two "
        "baselines, provision-level House-vs-Senate distributions, "
        "KYPA/WATCA, capital-gains indexing.",
        "url": "https://budgetlab.yale.edu/",
        "fetched": "2026-08-02",
        "harvest_dir": f"{HARVEST}/budget_lab",
    },
    "cpsp": {
        "name": "Columbia Center on Poverty and Social Policy",
        "org": "Columbia University",
        "model": "CPSP SPM poverty model",
        "method": "Monthly SPM series 2024-01–2025-12 (the project ended "
        "December 2025), CTC counterfactuals for 2023/2024 at stated 100% "
        "take-up, state refundable-CTC designs, and SNAP TFP-revocation "
        "state tables on a pooled 2015–19 TRIM3 base (vintage flagged per "
        "row).",
        "url": "https://www.povertycenter.columbia.edu/",
        "fetched": "2026-08-02",
        "harvest_dir": f"{HARVEST}/cpsp",
    },
}

RELATIONSHIP_SOURCE_NOTES = {
    "cbo": {
        "consumed_as_target": (
            "Rows labeled consumed_as_target were pre-verified at staging "
            "against policyengine-us calibration parameters "
            "(parameters/calibration/gov/cbo): PolicyEngine consumes these "
            "series, so agreement there is calibration, not validation."
        ),
    },
}


def fallback_meta(source: str, rows: list[sqlite3.Row]) -> dict:
    """DB-derived registry entry for a source id we have no card for yet."""
    models = sorted({r["source_model"] for r in rows if r["source_model"]})
    pubs = [json.loads(r["publication"]) for r in rows[:200]]
    urls = [p.get("page_url") or p.get("url") for p in pubs]
    url = next((u for u in urls if u), None)
    return {
        "name": source.replace("_", " "),
        "org": None,
        "model": ", ".join(models) or None,
        "method": None,
        "url": url,
        "fetched": None,
        "auto": True,
    }


# ---------------------------------------------------------------------------
# Agreement bins — the same descriptive rule the app renders (format.ts):
# share-valued metrics compare in percentage points (2.5pp / 10pp), counts
# and dollars by ratio (10% / 30%). Bins, never pass/fail.
# ---------------------------------------------------------------------------


def bin_of(unit: str, metric: str, ext: float | None,
           pe: float | None) -> str | None:
    if ext is None or pe is None:
        return None
    if unit == "share" or "rate" in metric:
        pp = abs(pe - ext) * 100
        return "close" if pp < 2.5 else "moderate" if pp < 10 else "far"
    if ext == 0:
        return None
    r = abs(pe / ext - 1)
    return "close" if r < 0.1 else "moderate" if r < 0.3 else "far"


# ---------------------------------------------------------------------------
# Urban extras joined by reconstructed claim id (validated mapping — the
# ingest fails loudly on drift, so a silent mismatch here would have failed
# there first). 2026 values stay app-layer by design; diagnoses join only to
# variant-free rows exactly as build_comparison attached them.
# ---------------------------------------------------------------------------


def urban_extras() -> tuple[dict, dict, int]:
    comp = json.loads((DATA / "comparison.json").read_text())
    diagnoses = {
        (d["program"], d["metric"], d["geography"], d["subgroup"]): d
        for d in json.loads((DATA / "diagnoses_rows.json").read_text())
    }
    v26, diag = {}, {}
    for row in comp["rows"]:
        probe = _probe(row)
        if probe is None:
            continue
        cid = probe.claim_id()
        if row.get("pe_value_2026") is not None:
            v26[cid] = row["pe_value_2026"]
        d = diagnoses.get(
            (row["program"], row["metric"], row["geography"],
             row["subgroup"])
        )
        if d and not row["variant"]:
            diag[cid] = d
    return v26, diag, len(comp["rows"])


NORMATIVE_CLASSES = {"pe_gap", "external_issue"}


def diagnosis_payload(cls: str, title: str | None = None,
                      confidence: str | None = None,
                      fix_type: str | None = None,
                      rationale: str | None = None,
                      action_link: str | None = None) -> dict:
    cls = "external_issue" if cls == "external_model_issue" else cls
    out = {
        "class": cls,
        # Register gate: verdict language only where a known issue is cited.
        "normative": bool(cls in NORMATIVE_CLASSES and action_link),
    }
    for k, v in (
        ("title", title), ("confidence", confidence),
        ("fix_type", fix_type), ("rationale", rationale),
        ("action_link", action_link),
    ):
        if v:
            out[k] = v
    return out


# ---------------------------------------------------------------------------
# Row assembly
# ---------------------------------------------------------------------------

# Publication keys that vary per row (verbatim values, workbook cells) —
# these move onto the row as `provenance` so the rest of the publication
# dict pools cleanly (JCT would otherwise carry ~6,400 near-identical pubs).
ROW_PUB_KEYS = ("value_verbatim", "value_unrounded", "cell")

# Condition keys hoisted onto the row itself; the emitted conditions dict
# carries only the remainder (the app reassembles the full mapping for
# display, no information lost).
HOISTED_CONDITIONS = ("geography", "program", "subgroup")

VARIANT_SUFFIXES = ("_with_SSF", "_no_SSF")
POVERTY_METRICS = {
    "poverty_rate", "poverty_rate_change", "poverty_count_change",
    "poverty_count",
}


def split_subgroup(sub: str | None) -> tuple[str, str | None]:
    if not sub:
        return "total", None
    for suf in VARIANT_SUFFIXES:
        if sub.endswith(suf):
            return sub[: -len(suf)] or "total", suf[1:]
    return sub, None


def reform_fields(reform_json: str) -> tuple[str | None, str | None]:
    """(policy, baseline) slugs for a claim's reform reference."""
    ref = json.loads(reform_json)
    fw = ref.get("framework")
    policy = None
    if fw == "policy_ref":
        policy = (ref.get("reform") or {}).get("policy")
    elif fw and fw.startswith("policyengine") and fw.endswith("_inputs"):
        policy = "full_participation"
    elif fw and fw.startswith("policyengine"):
        policy = "pe_parametric_reform"
    baseline = ((ref.get("baseline") or {}) or {}).get("policy")
    return policy, baseline


def build_row(r: sqlite3.Row, pub_ix: int, v26: dict, diag: dict) -> dict:
    conditions = json.loads(r["conditions"])
    subgroup, variant = split_subgroup(conditions.get("subgroup"))
    program = r["program"] or None
    if (
        r["source"] == "urban_sotsn"
        and program is None
        and r["metric"] in POVERTY_METRICS
    ):
        program = "spm_poverty"
    policy, baseline = reform_fields(r["reform_json"])
    suppressed = r["status"] == "suppressed"
    status = r["pe_status"]
    if status is None and not suppressed:
        # No PE attempt recorded. Dynamic-scoring claims are out of model
        # (PolicyEngine is static — issue #9 doctrine); the rest are backlog.
        status = (
            "pe_gap" if conditions.get("scoring") == "dynamic"
            else "not_computed"
        )
    row = {
        "id": r["claim_id"],
        "metric": r["metric"],
        "unit": r["unit_concept"],
        "period": r["period"],
        "time_basis": r["time_basis"],
        "geography": r["geography"],
        "value_kind": r["value_kind"],
        "relationship": r["calibration_relationship"],
        "pub": pub_ix,
        "status": "suppressed" if suppressed else status,
    }
    extra = {
        k: v for k, v in conditions.items() if k not in HOISTED_CONDITIONS
    }
    if extra:
        row["conditions"] = extra
    if r["period_start"] is not None:
        row["period_start"] = r["period_start"]
        row["period_end"] = r["period_end"]
    if not suppressed:
        row["value"] = r["value"]
    for k, v in (
        ("program", program), ("subgroup", subgroup if r["source"] ==
         "urban_sotsn" or conditions.get("subgroup") else None),
        ("variant", variant), ("policy", policy), ("baseline", baseline),
        ("source_column", r["source_column"]),
    ):
        if v:
            row[k] = v
    if r["pe_value"] is not None:
        pe = {"value": r["pe_value"]}
        if r["pe_construction"]:
            pe["construction"] = r["pe_construction"]
        row["pe"] = pe
        if r["delta"] is not None:
            row["delta"] = r["delta"]
        if r["ratio"] is not None:
            row["ratio"] = r["ratio"]
    if r["claim_id"] in v26:
        row["pe_2026"] = v26[r["claim_id"]]
    d = None
    if r["diagnosis_class"]:
        d = diagnosis_payload(
            r["diagnosis_class"], rationale=r["diagnosis_rationale"],
            action_link=r["action_link"],
        )
    elif r["claim_id"] in diag:
        j = diag[r["claim_id"]]
        d = diagnosis_payload(
            j["classification"], title=j["title"],
            confidence=j["confidence"], fix_type=j["fix_type"],
        )
    if d:
        row["diagnosis"] = d
    ann = json.loads(r["annotations"]) if r["annotations"] else []
    if ann:
        row["annotations"] = ann
    return row


def facet(counter: Counter, limit: int = 60) -> list[dict]:
    return [
        {"value": v, "n": n} for v, n in counter.most_common(limit)
        if v is not None
    ]


# Scalar keys eligible for slice-level defaulting: when one value covers
# ≥60% of rows it moves to `row_defaults` and matching rows omit the key
# (the app reads row[k] ?? row_defaults[k]). Pure compression — absence of
# a non-defaulted key keeps meaning absence.
DEFAULTABLE_KEYS = (
    "metric", "unit", "period", "time_basis", "value_kind",
    "relationship", "status", "pub", "program", "subgroup",
)


def compact_rows(out_rows: list[dict]) -> tuple[dict, list[list[str]]]:
    """Apply row_defaults + intern annotation id arrays. Mutates rows."""
    defaults = {}
    n = len(out_rows)
    for key in DEFAULTABLE_KEYS:
        counts = Counter(
            row[key] for row in out_rows if key in row
        )
        if not counts:
            continue
        value, hits = counts.most_common(1)[0]
        if hits >= 0.6 * n:
            defaults[key] = value
            for row in out_rows:
                if row.get(key) == value:
                    del row[key]
    sets: dict[tuple, int] = {}
    ann_sets: list[list[str]] = []
    for row in out_rows:
        ann = row.get("annotations")
        if ann is None:
            continue
        key = tuple(ann)
        if key not in sets:
            sets[key] = len(ann_sets)
            ann_sets.append(list(key))
        row["annotations"] = sets[key]
    return defaults, ann_sets


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    conn = sqlite3.connect(DATA / "scorecard.db")
    conn.row_factory = sqlite3.Row
    all_rows = conn.execute(
        "SELECT c.*, r.annotations FROM comparisons c"
        " LEFT JOIN pe_results r ON r.id = ("
        "   SELECT id FROM pe_results WHERE claim_id = c.claim_id"
        "   ORDER BY computed_at DESC, id DESC LIMIT 1)"
        " ORDER BY c.source, c.claim_id"
    ).fetchall()
    v26, diag, n_comp = urban_extras()
    print(f"{len(all_rows)} claims; urban extras over {n_comp} platform "
          f"rows: {len(v26)} 2026 values, {len(diag)} diagnoses")

    by_source: dict[str, list[sqlite3.Row]] = defaultdict(list)
    for r in all_rows:
        by_source[r["source"]].append(r)

    pe_meta = json.loads((DATA / "pe" / "pe_meta.json").read_text())
    bundle = json.loads((DATA / "comparison.json").read_text())["pe_bundle"]
    annotations_catalog = {
        a["id"]: a
        for a in json.loads(
            (ROOT / "sources" / "urban-sotsn" / "annotations.json")
            .read_text()
        )["annotations"]
    }

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "sources").mkdir(exist_ok=True)
    built = str(date.today())

    index_sources = []
    total_bins = Counter()
    total_status = Counter()
    material = explained = held_out_both = 0
    excluded = Counter()

    for source, rows in sorted(
        by_source.items(), key=lambda kv: -len(kv[1])
    ):
        meta = SOURCE_META.get(source) or fallback_meta(source, rows)
        pubs, pub_ix = [], {}
        out_rows = []
        facets: dict[str, Counter] = defaultdict(Counter)
        bins = Counter()
        status_counts = Counter()
        rel_counts = Counter()
        src_material = src_explained = src_both = 0
        rel_notes: dict[str, str] = dict(
            RELATIONSHIP_SOURCE_NOTES.get(source, {})
        )
        for r in rows:
            pub = json.loads(r["publication"])
            prov = {k: pub.pop(k) for k in ROW_PUB_KEYS if k in pub}
            pub_key = json.dumps(pub, sort_keys=True)
            if pub_key not in pub_ix:
                pub_ix[pub_key] = len(pubs)
                pubs.append(pub)
            row = build_row(r, pub_ix[pub_key], v26, diag)
            if prov:
                row["provenance"] = prov
            out_rows.append(row)
            status_counts[row["status"]] += 1
            rel_counts[row["relationship"]] += 1
            for key in ("program", "metric", "geography", "period",
                        "policy", "baseline", "subgroup"):
                if row.get(key) is not None:
                    facets[key][row[key]] += 1
            scoring = (row.get("conditions") or {}).get("scoring")
            if scoring:
                facets["scoring"][scoring] += 1
            if source == "urban_sotsn":
                prog = row.get("program") or ""
                key = f"{prog}|{row['metric']}"
                if key not in rel_notes:
                    try:
                        _, basis = effective_relationship(
                            prog if prog != "spm_poverty" else "base",
                            Metric(row["metric"]),
                        )
                        if basis:
                            rel_notes[key] = basis
                    except ValueError:
                        pass
            ext, pe = row.get("value"), (row.get("pe") or {}).get("value")
            b = bin_of(row["unit"], row["metric"], ext, pe)
            if pe is not None and ext is not None:
                if row["relationship"] == "held_out":
                    src_both += 1
                    if b:
                        bins[b] += 1
                    if b in ("moderate", "far"):
                        src_material += 1
                        if "diagnosis" in row:
                            src_explained += 1
                else:
                    excluded[row["relationship"]] += 1

        row_defaults, ann_sets = compact_rows(out_rows)
        slice_doc = {
            "built": built,
            "id": source,
            "meta": meta,
            "row_defaults": row_defaults,
            "annotation_sets": ann_sets,
            "summary": {
                "claims": len(rows),
                "ok": len(rows) - status_counts["suppressed"],
                "suppressed": status_counts["suppressed"],
                "by_status": dict(status_counts),
                "relationships": dict(rel_counts),
                "agreement_bins": dict(bins),
                "held_out_compared": src_both,
                "material_divergences": src_material,
                "explained": src_explained,
                "period_min": min(r["period"] for r in rows),
                "period_max": max(r["period"] for r in rows),
                "models": sorted(
                    {r["source_model"] for r in rows if r["source_model"]}
                ),
            },
            "relationship_notes": rel_notes,
            "facets": {k: facet(c) for k, c in facets.items()},
            "pubs": pubs,
            "rows": out_rows,
        }
        if source == "urban_sotsn":
            slice_doc["annotations"] = annotations_catalog
            slice_doc["pe_runs"] = pe_meta.get("runs", {})
            slice_doc["pe_provenance"] = {
                "engine_version": bundle.get("model_version"),
                "data_bundle": bundle.get("certified_data_build_id"),
                "runtime_dataset": bundle.get("runtime_dataset"),
                "period": "annual 2024",
            }
        path = OUT / "sources" / f"{source}.json"
        path.write_text(json.dumps(slice_doc, separators=(",", ":")))
        print(f"  {source}: {len(rows)} rows, {len(pubs)} pubs, "
              f"{path.stat().st_size / 1e6:.1f} MB")

        total_bins.update(bins)
        total_status.update(status_counts)
        material += src_material
        explained += src_explained
        held_out_both += src_both
        idx = {
            "id": source,
            "name": meta["name"],
            "org": meta.get("org"),
            "model": meta.get("model"),
            "url": meta.get("url"),
            "fetched": meta.get("fetched"),
            "auto": meta.get("auto", False),
            **{k: slice_doc["summary"][k] for k in (
                "claims", "ok", "suppressed", "by_status", "relationships",
                "agreement_bins", "held_out_compared",
                "material_divergences", "explained", "period_min",
                "period_max", "models",
            )},
            "computed": sum(
                1 for row in out_rows if row.get("pe") is not None
            ),
            "metrics_top": facet(facets["metric"], 4),
            "n_policies": len(facets["policy"]),
            "n_baselines": len(facets["baseline"]),
            "n_geographies": len(facets["geography"]),
        }
        index_sources.append(idx)

    # ---- tiles ------------------------------------------------------------
    ok_claims = [r for r in all_rows if r["status"] == "ok"]
    computed = sum(1 for r in all_rows if r["pe_value"] is not None)
    rng = random.Random(RANDOM_STRAND_SEED)
    sample = rng.sample(sorted(r["claim_id"] for r in ok_claims),
                        min(RANDOM_STRAND_N, len(ok_claims)))
    sample_set = set(sample)
    strand_status = Counter()
    strand_source = Counter()
    strand_rel = Counter()
    row_by_id = {}
    for source, rows in by_source.items():
        for r in rows:
            if r["claim_id"] in sample_set:
                row_by_id[r["claim_id"]] = r
    for cid in sample:
        r = row_by_id[cid]
        conditions = json.loads(r["conditions"])
        st = r["pe_status"]
        if st is None:
            st = ("pe_gap" if conditions.get("scoring") == "dynamic"
                  else "not_computed")
        strand_status[st] += 1
        strand_source[r["source"]] += 1
        strand_rel[r["calibration_relationship"]] += 1

    n_diagnoses = sum(
        1 for r in all_rows if r["diagnosis_class"]
    ) + len(diag)

    # Flat list of every published explanation for the app's
    # "how the models differ" view (small: one entry per diagnosis).
    explanations = []
    diag_by_cid = dict(diag)
    for source, rows in by_source.items():
        for r in rows:
            entry = None
            if r["diagnosis_class"]:
                entry = diagnosis_payload(
                    r["diagnosis_class"],
                    rationale=r["diagnosis_rationale"],
                    action_link=r["action_link"],
                )
            elif r["claim_id"] in diag_by_cid:
                j = diag_by_cid[r["claim_id"]]
                entry = diagnosis_payload(
                    j["classification"], title=j["title"],
                    confidence=j["confidence"], fix_type=j["fix_type"],
                )
            if entry:
                conditions = json.loads(r["conditions"])
                explanations.append(
                    {
                        "source": source,
                        "claim_id": r["claim_id"],
                        "program": r["program"] or None,
                        "metric": r["metric"],
                        "geography": r["geography"],
                        "subgroup": conditions.get("subgroup"),
                        "period": r["period"],
                        **entry,
                    }
                )

    index_doc = {
        "built": built,
        "pe_bundle": {
            k: bundle.get(k)
            for k in (
                "model_package", "model_version", "runtime_dataset",
                "certified_data_build_id", "data_package", "data_version",
            )
        },
        "catalog": {
            "sources": len(by_source),
            "claims": len(all_rows),
            "ok": len(ok_claims),
            "suppressed": len(all_rows) - len(ok_claims),
            "computed": computed,
            "by_status": dict(total_status),
        },
        "tiles": {
            "coverage": {
                "ok": len(ok_claims),
                "computed": computed,
                "sources": len(by_source),
            },
            "agreement": {
                "held_out_compared": held_out_both,
                "bins": dict(total_bins),
                "excluded_labeled": dict(excluded),
            },
            "explained": {
                "material": material,
                "explained": explained,
                "explanations_published": n_diagnoses,
            },
            "random_strand": {
                "seed": RANDOM_STRAND_SEED,
                "drawn": len(sample),
                "by_status": dict(strand_status),
                "by_source": dict(strand_source),
                "by_relationship": dict(strand_rel),
            },
        },
        "sources": index_sources,
        "explanations": explanations,
    }
    (OUT / "index.json").write_text(json.dumps(index_doc, indent=1))
    print(f"index.json: {len(index_sources)} sources")
    print("tiles:", json.dumps(index_doc["tiles"], indent=1))

    # ---- copy into the app ------------------------------------------------
    APP_DATA.mkdir(parents=True, exist_ok=True)
    (APP_DATA / "sources").mkdir(exist_ok=True)
    shutil.copy(OUT / "index.json", APP_DATA / "index.json")
    for f in (OUT / "sources").glob("*.json"):
        shutil.copy(f, APP_DATA / "sources" / f.name)
    for name in ("lanes.json", "exhibits.json"):
        if (DATA / name).exists():
            shutil.copy(DATA / name, APP_DATA / name)
    stale = APP_DATA / "comparison.json"
    if stale.exists():
        stale.unlink()
    print(f"copied feeds -> {APP_DATA}")


if __name__ == "__main__":
    main()
