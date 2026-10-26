"""Ingest the £100,000 childcare limit costings and their PolicyEngine
counterparts (lane uk-childcare-100k).

Two external scores of removing the £100,000 adjusted-net-income limit on
the working-parent childcare offers in England:

    sources/centax-childcare-100k   CenTax, "Removing the childcare
        cliff-edge" (September 2026), Table 4.2: the free hours only, on
        HMRC administrative data; static cost, two behavioural margins and
        the net cost, for three scenarios in 2027-28 and 2029-30
    sources/cbp-rates-and-wrongs    Centre for British Progress, "Rates and
        wrongs" technical appendix (25 March 2026), Tables 2-3: the free
        hours and Tax-Free Childcare on a synthetic population; net of
        behaviour only, two behavioural models, 2026-27 to 2031-32

Inputs: the adapters' tidy rows (data/externals/<id>.json, QC'd there),
each source's annotations.json, every certified-pair artifact
results/uk/childcare_100k/<variant>.json (pipeline/compute_uk_childcare_100k.py),
each checked against its own record in data/uk/replay_variants.json, with
their construction_annotations.json, and the published dashboard figure in
sources/centax-childcare-100k/pe/published_dashboard.json.

Claims: 24 CenTax money cells and 12 CBP "Abolish Cliff" cells, all
revenue_change in pounds, the value as published; the printed form of each
value is publication provenance, outside the claim id. Tallied drops (still in
data/externals): CenTax's 12 bunching counts (a behavioural-model count of
parents with no registered metric; minting one waits for a counterpart)
and CBP's 60 taper cells (a per-child taper replacing the cliff, which no
PolicyEngine construction in this lane executes).

Results:
  - certified pair (the default replay variant, data/uk/certified_bundle.json):
    CenTax static rows (6) are `comparable`, CenTax net rows (6) and CBP
    rows (10) `concept_mismatch`; the status comes from the source's
    annotations.json, and exactly one status-setting annotation must match.
    Both offers are England's, so each counterpart sums the childcare heads
    for people in English households (the engine applies Tax-Free
    Childcare UK-wide).
  - earlier certified pairs: an artifact for another certified variant stays
    in results/uk/childcare_100k/ beside a newer one, and its run stays in
    the history; each claim's latest is the newest run that computed its
    year. A note
    whose basis is the engine or a run names the pairs it was checked on
    (`variants`) and attaches only to their results; an artifact whose pair
    has no verified_pairs entry in construction_annotations.json is refused.
  - published dashboard history (4): PolicyEngine's published 30-hours cost
    (£0.434bn in 2027-28, £0.505bn in 2029-30; on policyengine.org from
    12 to 21 October 2026, then taken down while the dashboard's costing
    is revised; what the dashboard has served since is recorded on the
    row, not attached) on the CenTax central
    static and net rows, the comparison the dashboard itself drew:
    `constructed` (static; the dashboard's local corrections) and
    `concept_mismatch` (net). It is older than the certified run, so the
    comparisons view and the app's latest point at the certified run and
    the published miss stays in the history beside it.
CenTax's behavioural margins (12) and CBP's 2031-32 cells (2) carry no
result; they are published without one and say why in ``pe_missing``, read
off the runs that exist (the years each computed). It rides in publication,
outside the claim id, so a new run never changes a claim's id; the feed
shows it as conditions.pe_missing.

Diagnosis: the CenTax central static rows carry a pe_gap diagnosis linked
to microcosm#1126 (the hours-usage draw), with the evidence measured on the
claim's latest run and the history that run's pair's verified_pairs entry
states.

calibration_relationship comes from relationships.uk_relationship: held out
for both sources. Each is a reform estimate, and no calibration target is a
reform-world quantity (tests/test_uk_childcare_100k.py checks the built DB).

    PYTHONPATH=. python -m scorecard_db.ingest_uk_childcare_100k data/scorecard.db
"""

from __future__ import annotations

import datetime as dt
import json
from collections import Counter
from pathlib import Path

from .db import DIAGNOSES_SQL, LANE_SQL, RESULTS_SQL, SCORES_SQL, ScorecardDB
from .harvest import REPO, finish, policy_ref, require_fields
from .models import (
    BASELINE,
    STANDARD_CONDITIONS,
    ComparisonStatus,
    DiagnosisClass,
    ExternalScore,
    Metric,
    PEResult,
    TimeBasis,
    UnitConcept,
)
from .relationships import uk_relationship

EXTERNALS = REPO / "data" / "externals"
CENTAX_DIR = REPO / "sources" / "centax-childcare-100k"
CBP_DIR = REPO / "sources" / "cbp-rates-and-wrongs"
RESULTS_DIR = REPO / "results" / "uk" / "childcare_100k"
VARIANTS = REPO / "data" / "uk" / "replay_variants.json"
CERTIFIED = REPO / "data" / "uk" / "certified_bundle.json"
CONSTRUCTION = RESULTS_DIR / "construction_annotations.json"
# The artifact schema this ingest reads (pipeline/compute_uk_childcare_100k.py).
SCHEMA_VERSION = 2

CENTAX = "centax"
CBP = "centre_for_british_progress"
SOURCES = (CENTAX, CBP)
SOURCE_MODELS = {
    # the spelling the Autumn Budget 2025 harvest already uses for CenTax
    CENTAX: "hmrc_administrative_microdata",
    CBP: "cbp_synthetic_microsimulation",
}
MEASURES = {
    CENTAX: "uk_free_childcare_hours_100k_limit_removed",
    CBP: "uk_free_childcare_hours_and_tfc_100k_limit_removed",
}
PROGRAMS = {
    CENTAX: "free_childcare_hours",
    CBP: "free_childcare_hours_and_tax_free_childcare",
}
# which certified-pair world answers which source
WORLDS = {CENTAX: "free_hours", CBP: "free_hours_and_tfc"}
FREE_HOURS = (
    "extended_childcare_entitlement",
    "universal_childcare_entitlement",
    "targeted_childcare_entitlement",
)
TFC = "tax_free_childcare"
VARIABLES = {CENTAX: list(FREE_HOURS), CBP: [*FREE_HOURS, TFC]}
HOURS_USAGE_INPUT = "maximum_extended_childcare_hours_usage"
# the extended offer's weekly hours: the full-use diagnostic sets every
# family's usage to them
FULL_USE_HOURS = 30.0
FULL_USE = {
    "baseline": "baseline__full_use_hours",
    "free_hours": "free_hours__full_use_hours",
}
# Within a data bundle the comparisons view prefers these runs (db.py: the
# canonical Urban grid), so a run of this lane may not take the prefix: its
# latest result must be its newest run.
RESERVED_RUN_PREFIX = "platform-grid-"
# the artifact's sums for people in English households
ENGLAND = "sums_gbp_england"

LANE_ID = "uk-childcare-100k"
LANE_UPDATED = "2026-10-25"
# The UK family's shared top-level feed literal (sync_lane_feed's contract).
FEED_UPDATED = "2026-08-19"
LANE_FEED_META = {
    "source": "CenTax + Centre for British Progress",
    "area": "£100,000 childcare limit (30 funded hours, Tax-Free Childcare)",
    "mode": 2,
    "country": "UK",
}
REGISTRY_MARK = "uk_childcare_100k"

CENTAX_PUBLICATION = {
    "title": "Removing the childcare cliff-edge: impacts and cost of reform",
    "authors": "Advani, Flew, Pepin-Hall and Summers",
    "publisher": "CenTax",
    "url": "https://centax.org.uk/wp-content/uploads/2026/09/AdvaniFlewPepin-HallSummers2026_Removing-the-childcare-cliff-edge.pdf",
    "date": "2026-09",
    "table": "4.2",
    "printed_page": "41",
    "vintage": "as published September 2026 (fetched 2026-10-21)",
}
CBP_PUBLICATION = {
    "title": "Technical Appendix: underlying modelling and analysis for each of the policies in the Rates and Wrongs paper",
    "publisher": "Centre for British Progress",
    "url": "https://britishprogress.org/api/media/file/rates_and_wrongs_technical_appendix.pdf",
    "date": "2026-03-25",
    "vintage": "as published 25 March 2026 (fetched 2026-10-21)",
}

CENTAX_MONEY = (
    "static_cost",
    "intensive_margin",
    "extensive_margin",
    "net_fiscal_cost",
)
CENTAX_ATTACHED = ("static_cost", "net_fiscal_cost")
CENTAX_SIGN = (
    "positive = gain to the Exchequer (published: 'negative = cost to the Exchequer')"
)
SCORING = {
    "static_cost": "static",
    "net_fiscal_cost": "post_behavioural",
}
# A basis citing either of these rests on the engine or a run, so its note
# names the certified pairs it was checked on (`variants`).
_RUN_BASIS = ("policyengine_uk ", "results/uk/childcare_100k/")

# the tidy-row core (docs/ARCHITECTURE.md), then each adapter's facets
_CORE_FIELDS = frozenset(
    {
        "source",
        "program",
        "metric",
        "subgroup",
        "variant",
        "geography",
        "unit_concept",
        "period",
        "value",
        "status",
        "source_column",
    }
)
_CENTAX_FIELDS = _CORE_FIELDS | {
    "column",
    "country",
    "fy",
    "printed_page",
    "table",
    "tax_year_label",
    "value_verbatim",
}
_CBP_FIELDS = _CORE_FIELDS | {
    "assumptions",
    "country",
    "fy",
    "pdf_page",
    "policy",
    "table",
    "value_verbatim",
}
_DROPS = {
    "centax_bunching_counts": (
        "CenTax's Table 4.2 bunching counts (parents holding income at "
        "£100,000, before and after removal) are outputs of its behavioural "
        "model with no registered metric here; minting one waits for a "
        "counterpart or a second source. The rows stay in data/externals."
    ),
    "cbp_taper_rows": (
        "CBP's 1%-5% rows replace the cliff with a per-child opt-in taper "
        "(section 1.3.6), a reform no PolicyEngine construction in this lane "
        "executes. The rows stay in data/externals."
    ),
}


def _load(adapter_id: str, known: frozenset, source: str) -> list[dict]:
    path = EXTERNALS / f"{adapter_id}.json"
    if not path.exists():
        raise FileNotFoundError(
            f"{path} missing — run python sources/{adapter_id}/adapter.py"
        )
    rows = json.loads(path.read_text())
    for row in rows:
        require_fields(row, known, source)
        missing = _CORE_FIELDS - set(row)
        if missing:
            raise ValueError(f"{source}: rows lack the tidy core {sorted(missing)}")
        identity = (row["source"], row["country"], row["geography"], row["program"])
        if identity != (adapter_id, "UK", "England", PROGRAMS[source]):
            raise ValueError(f"{source}: unexpected row identity {row}")
    return rows


def _check_conditions(cond: dict) -> dict:
    unknown = set(cond) - STANDARD_CONDITIONS
    if unknown:
        raise ValueError(f"conditions outside STANDARD_CONDITIONS: {sorted(unknown)}")
    return cond


def _revenue_row(row: dict, source: str) -> dict:
    if row["metric"] != Metric.REVENUE_CHANGE.value or row["subgroup"] is not None:
        raise ValueError(f"{source}: not a whole-population revenue row {row}")
    return row


def _centax_claim(row: dict, pe_missing: str | None = None) -> ExternalScore:
    _revenue_row(row, CENTAX)
    component = row["column"]
    cond = {
        "country": "UK",
        "geography": "England",
        "fy": row["fy"],
        "program": PROGRAMS[CENTAX],
        "measure_key": MEASURES[CENTAX],
        "component": component,
        "scenario": row["variant"],
        "benchmark_class": "different_model",
        "data_scope": "hmrc_administrative",
        "sign_convention": CENTAX_SIGN,
    }
    if component in SCORING:
        cond["scoring_method"] = SCORING[component]
    relationship, _ = uk_relationship(CENTAX, Metric.REVENUE_CHANGE)
    return ExternalScore(
        source=CENTAX,
        source_model=SOURCE_MODELS[CENTAX],
        metric=Metric.REVENUE_CHANGE,
        unit_concept=UnitConcept.GBP,
        period=int(row["period"]),
        time_basis=TimeBasis.FISCAL_YEAR,
        value=float(row["value"]),
        conditions=_check_conditions(cond),
        reform=policy_ref(MEASURES[CENTAX]),
        calibration_relationship=relationship,
        source_column=row["source_column"],
        publication=_without_result(
            {
                **CENTAX_PUBLICATION,
                "value_verbatim": row["value_verbatim"],
                "registry": REGISTRY_MARK,
                "publish_without_result": True,
            },
            pe_missing,
        ),
        value_kind="gbp",
        status=row["status"],
    )


def _without_result(publication: dict, pe_missing: str | None) -> dict:
    # Why a claim has no PolicyEngine value depends on which certified runs
    # exist (the years they computed, the pair's engine), so the reason rides
    # in publication, outside the claim id; export_populations shows it as
    # conditions.pe_missing, where every other lane's reason sits.
    if pe_missing is not None:
        publication["pe_missing"] = pe_missing
    return publication


def _cbp_claim(row: dict, pe_missing: str | None = None) -> ExternalScore:
    _revenue_row(row, CBP)
    cond = {
        "country": "UK",
        "geography": "England",
        "fy": row["fy"],
        "program": PROGRAMS[CBP],
        "measure_key": MEASURES[CBP],
        "scoring_method": "post_behavioural",
        "behavioral_response": row["variant"],
        "benchmark_class": "different_model",
        "data_scope": "synthetic_ons_births_spi_2022_23",
        # no sign_convention: the appendix states none, so the exporter's
        # signs.classify reads "no_stated_convention" (unknown); CenTax's
        # reading of the sign is in the cbp-sign-unstated annotation
    }
    relationship, _ = uk_relationship(CBP, Metric.REVENUE_CHANGE)
    return ExternalScore(
        source=CBP,
        source_model=SOURCE_MODELS[CBP],
        metric=Metric.REVENUE_CHANGE,
        unit_concept=UnitConcept.GBP,
        period=int(row["period"]),
        time_basis=TimeBasis.FISCAL_YEAR,
        value=float(row["value"]),
        conditions=_check_conditions(cond),
        reform=policy_ref(MEASURES[CBP]),
        calibration_relationship=relationship,
        source_column=row["source_column"],
        publication=_without_result(
            {
                **CBP_PUBLICATION,
                "table": row["table"],
                "pdf_page": str(row["pdf_page"]),
                "assumptions": row["assumptions"],
                "value_verbatim": row["value_verbatim"],
                "registry": REGISTRY_MARK,
                "publish_without_result": True,
            },
            pe_missing,
        ),
        value_kind="gbp",
        status=row["status"],
    )


def check_artifact(art: dict, path: Path, variant: dict) -> None:
    """The artifact ran on exactly its variant's certified pairing: the
    installed wheels, Python and packaged manifest the run verified, the
    runtime release bundle, the dataset each world read, and its years."""
    vid = variant["variant_id"]
    identity = variant["identity"]
    dataset = identity["dataset"]
    if art.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(
            f"{path.name}: schema_version {art.get('schema_version')} != "
            f"{SCHEMA_VERSION}; rerun pipeline/compute_uk_childcare_100k.py"
        )
    if (art["variant_id"], path.stem) != (vid, vid):
        raise ValueError(f"{path.name}: artifact variant {art['variant_id']} != {vid}")
    packages = {
        name: {f: pkg[f] for f in ("version", "record_sha256")}
        for name, pkg in identity["packages"].items()
    }
    got = {
        "variant_identity_sha256": art["variant_identity_sha256"],
        "packages": art["packages"],
        "engine_version": art["engine_version"],
        "python": art["python"],
        "packaged_bundle_manifest_sha256": art["packaged_bundle_manifest_sha256"],
        "release_bundle": art["release_bundle"],
        "dataset": (
            art["data_bundle"],
            art["dataset"]["revision"],
            art["dataset"]["sha256"],
        ),
    }
    want = {
        "variant_identity_sha256": variant["identity_sha256"],
        "packages": packages,
        "engine_version": packages["policyengine-uk"]["version"],
        "python": identity["python"],
        "packaged_bundle_manifest_sha256": identity["packaged_bundle_manifest_sha256"],
        "release_bundle": identity["release_bundle"],
        "dataset": (dataset["revision"], dataset["revision"], dataset["sha256"]),
    }
    wrong = sorted(k for k in want if got[k] != want[k])
    if wrong:
        raise ValueError(f"{path.name}: not {vid}'s certified pairing: {wrong}")
    if variant["layout"] == "legacy_events":
        cert = json.loads(CERTIFIED.read_text())
        if (dataset["revision"], dataset["sha256"]) != (
            cert["revision"],
            cert["sha256"],
        ):
            raise ValueError(f"{path.name}: data bundle is not the certified bundle")
    for name, world in (*art["worlds"].items(), *art["diagnostics"].items()):
        if not (
            world["dataset_sha256_before"]
            == world["dataset_sha256_after"]
            == dataset["sha256"]
        ):
            raise ValueError(
                f"{path.name} {name}: dataset digest is not the certified one"
            )
        if not world.get("runtime_dataset_source"):
            raise ValueError(f"{path.name} {name}: no runtime dataset source recorded")
        if world["dataset_years"] != variant["data_years"]:
            raise ValueError(f"{path.name} {name}: dataset years are not the variant's")
    if art["behavioural_response"] != "none (static)":
        raise ValueError(f"{path.name}: artifact is not a static run")


def load_artifacts(
    results_dir: Path = RESULTS_DIR, variants_path: Path = VARIANTS
) -> list[tuple[dict, Path]]:
    """Every certified-pair artifact, each checked against its own certified
    variant record, oldest first. Each claim's latest result is the newest
    run that computed its year, so run ids and UTC computed_at times must be
    distinct."""
    index = json.loads(variants_path.read_text())
    records = {v["variant_id"]: v for v in index["variants"]}
    out = []
    for path in sorted(results_dir.glob("*.json")):
        if path.name == CONSTRUCTION.name:
            continue
        art = json.loads(path.read_text())
        variant = records.get(art.get("variant_id"))
        if variant is None or variant["status"] != "certified":
            raise ValueError(f"{path.name}: names no certified variant")
        check_artifact(art, path, variant)
        out.append((art, path))
    out.sort(key=lambda a: a[0]["computed_at"])
    if not out:
        raise FileNotFoundError(
            f"no artifact in {results_dir}; run pipeline/compute_uk_childcare_100k.py"
        )
    check_history(out)
    return out


def _utc(stamp: str, where: str) -> None:
    """A UTC time in the one form datetime.isoformat() writes for it, so
    string order is time order (the database orders computed_at as text,
    and '+' sorts before the '.' of a fraction) and two strings differ only
    when the times do."""
    when = dt.datetime.fromisoformat(stamp)
    if when.utcoffset() != dt.timedelta(0) or when.isoformat() != stamp:
        raise ValueError(
            f"{where}: {stamp!r} is not a UTC time as datetime.isoformat() writes it"
        )


def check_history(artifacts: list[tuple[dict, Path]]) -> None:
    """The run history each stage reads: distinct run ids outside the
    reserved prefix, and distinct canonical UTC computed_at times, so each
    claim's newest run, here and in the database, is one run."""
    if not artifacts:
        raise ValueError("no certified artifact")
    for art, path in artifacts:
        if art["run_id"].startswith(RESERVED_RUN_PREFIX):
            raise ValueError(
                f"{path.name}: run_id {art['run_id']!r} takes the reserved prefix "
                f"{RESERVED_RUN_PREFIX!r}"
            )
        _utc(art["computed_at"], f"{path.name} computed_at")
    if len({a["run_id"] for a, _ in artifacts}) != len(artifacts):
        raise ValueError("two artifacts share a run_id")
    if len({a["computed_at"] for a, _ in artifacts}) != len(artifacts):
        raise ValueError("two artifacts share a computed_at")


def load_artifact() -> tuple[dict, Path]:
    """The newest certified artifact."""
    return load_artifacts()[-1]


def _pe_missing(
    source: str,
    component: str | None,
    period: int,
    fy: str,
    artifacts: list[tuple[dict, Path]],
    notes: dict,
) -> str | None:
    """Why a claim has no certified PolicyEngine value, read off the runs
    that exist (the years each computed, not the years its dataset holds),
    or None when one of them computed it."""
    if source == CENTAX and component not in CENTAX_ATTACHED:
        # the pair of the newest run that computed this year, as for a result
        runs = [a for a, _ in artifacts]
        covering = [
            a for a in runs if str(period - 1) in a["worlds"][WORLDS[CENTAX]]["years"]
        ]
        newest = max(covering or runs, key=lambda a: a["computed_at"])
        return (
            "behavioural leg: this lane's PolicyEngine counterparts are static "
            f"runs ({verified_pair(notes, newest)['static_because']})"
        )
    year = period - 1
    if any(str(year) in a["worlds"][WORLDS[source]]["years"] for a, _ in artifacts):
        return None
    holding = sorted(
        a["variant_id"]
        for a, _ in artifacts
        if year in a["worlds"]["baseline"]["dataset_years"]
    )
    if holding:
        return (
            f"fiscal year {fy}: no certified run in this lane computed it, though it is "
            f"among the data years of {', '.join(holding)} (rerun "
            f"pipeline/compute_uk_childcare_100k.py --variant <id> with {year} in --years)"
        )
    spans = "; ".join(
        f"{a['variant_id']} {ys[0]}-{ys[-1]}"
        for a, _ in artifacts
        for ys in [a["worlds"]["baseline"]["dataset_years"]]
    )
    return (
        f"fiscal year {fy} is outside the data years of every certified pair this "
        f"lane has run ({spans}; data/uk/replay_variants.json)"
    )


def stage(
    notes: dict | None = None,
    results_dir: Path = RESULTS_DIR,
    variants_path: Path = VARIANTS,
) -> tuple[list[ExternalScore], dict, list[tuple[dict, Path]]]:
    """(claims, drop tally, every certified artifact oldest first). Each
    artifact's pair must be a verified one; no claim id depends on which
    runs exist."""
    notes = notes or load_notes()
    artifacts = load_artifacts(results_dir, variants_path)
    for art, _ in artifacts:
        verified_pair(notes, art)
    scores: list[ExternalScore] = []
    drops: Counter = Counter()
    for row in _load("centax-childcare-100k", _CENTAX_FIELDS, CENTAX):
        if row["column"] in CENTAX_MONEY:
            missing = _pe_missing(
                CENTAX, row["column"], int(row["period"]), row["fy"], artifacts, notes
            )
            scores.append(_centax_claim(row, missing))
        else:
            drops["centax_bunching_counts"] += 1
    for row in _load("cbp-rates-and-wrongs", _CBP_FIELDS, CBP):
        if row["policy"] == "abolish_cliff":
            missing = _pe_missing(
                CBP, None, int(row["period"]), row["fy"], artifacts, notes
            )
            scores.append(_cbp_claim(row, missing))
        else:
            drops["cbp_taper_rows"] += 1
    return finish(scores, LANE_ID), dict(sorted(drops.items())), artifacts


# --- annotations -------------------------------------------------------------


def _spec(path: Path) -> list[dict]:
    spec = json.loads(path.read_text())
    for a in spec["annotations"]:
        if not a.get("basis"):
            raise ValueError(f"annotation {a['id']} has no basis")
        # a note resting on the engine or a run holds only where it was checked
        if any(m in a["basis"] for m in _RUN_BASIS) != bool(a.get("variants")):
            raise ValueError(
                f"annotation {a['id']}: a note whose basis is the engine or a run "
                "names the certified pairs it was checked on in `variants`, and "
                "only such a note does"
            )
    return spec["annotations"]


def load_notes() -> dict:
    """Every annotation in the lane, and what was verified about each pair:
    each source's annotations.json, the construction notes, and their
    verified_pairs (results/uk/childcare_100k/construction_annotations.json)."""
    notes = {
        CENTAX: _spec(CENTAX_DIR / "annotations.json"),
        CBP: _spec(CBP_DIR / "annotations.json"),
        "construction": _spec(CONSTRUCTION),
        "pairs": json.loads(CONSTRUCTION.read_text())["verified_pairs"],
    }
    named = {
        v
        for kind in (CENTAX, CBP, "construction")
        for a in notes[kind]
        for v in a.get("variants", [])
    }
    if named - set(notes["pairs"]):
        raise ValueError(
            f"annotations name pairs with no verified_pairs entry: "
            f"{sorted(named - set(notes['pairs']))}"
        )
    return notes


def verified_pair(notes: dict, art: dict) -> dict:
    """The pair's verified statements. An artifact for any other pair is
    refused rather than given notes that were checked on another engine."""
    pair = notes["pairs"].get(art["variant_id"])
    if pair is None:
        raise ValueError(
            f"{art['variant_id']}: no note in this lane was verified on this pair. "
            "Read each note whose basis is the engine or a run at this pair's pin, "
            "add the variant to the variants of those that hold, write new notes "
            "where they don't, and add its verified_pairs entry to "
            f"{CONSTRUCTION.relative_to(REPO)}"
        )
    return pair


def _scoped(spec: list[dict], variant: str | None) -> list[dict]:
    """The notes that hold for a result: report-only notes always, and a
    note resting on the engine or a run only on a pair it was checked on
    (never on the published figure, which is no certified pair)."""
    return [a for a in spec if "variants" not in a or variant in a["variants"]]


_MATCHERS = {
    CENTAX: {"components", "scenarios", "periods", "results"},
    CBP: {"models", "periods", "results"},
}


def _facets(score: ExternalScore) -> dict:
    c = score.conditions
    if score.source == CENTAX:
        return {
            "components": c["component"],
            "scenarios": c["scenario"],
            "periods": score.period,
        }
    return {"models": c["behavioral_response"], "periods": score.period}


def match_annotations(
    score: ExternalScore,
    result_kind: str,
    spec: list[dict],
    variant: str | None = None,
) -> tuple[list[str], ComparisonStatus]:
    """(texts, status) for one result on `variant`'s pair (None for the
    published figure); exactly one status-setting annotation must match, so
    a status is always a stated decision."""
    facets = {**_facets(score), "results": result_kind}
    texts, statuses = [], []
    for a in _scoped(spec, variant):
        match = a["applies_to"]
        if set(match) != _MATCHERS[score.source]:
            raise ValueError(f"annotation {a['id']}: matcher keys {sorted(match)}")
        if any(v is not None and facets[k] not in v for k, v in match.items()):
            continue
        texts.append(a["text"])
        if "status" in a:
            statuses.append((a["id"], a["status"]))
    if len(statuses) != 1:
        raise ValueError(
            f"{score.source} {score.conditions.get('component', '')} {score.period} "
            f"{result_kind}: status-setting annotations {statuses} (want exactly one)"
        )
    return texts, ComparisonStatus(statuses[0][1])


# --- results -----------------------------------------------------------------


def _bn(x: float) -> str:
    return f"£{x / 1e9:+.3f}bn"


def _delta(
    art: dict, world: str, year: int, variable: str, sums: str = "sums_gbp"
) -> float:
    ref = art["worlds"][world]["years"][str(year)][sums][variable]
    base = art["worlds"]["baseline"]["years"][str(year)][sums][variable]
    return ref - base


def counterpart(art: dict, source: str, year: int) -> float:
    """PolicyEngine's static revenue_change, oriented to the Exchequer
    (negative = cost): minus the change in the counted spending for people
    in English households."""
    return -sum(
        _delta(art, WORLDS[source], year, v, ENGLAND) for v in VARIABLES[source]
    )


def measured_notes(art: dict, source: str, year: int, fy: str, pair: dict) -> list[str]:
    world = WORLDS[source]
    w = art["worlds"][world]["years"][str(year)]
    b = art["worlds"]["baseline"]["years"][str(year)]
    d = {
        v: _delta(art, world, year, v)
        for v in (*FREE_HOURS, TFC, "gov_spending", "gov_tax")
    }
    eng = {v: _delta(art, world, year, v, ENGLAND) for v in (*FREE_HOURS, TFC)}
    # Nothing outside the four childcare heads may move (£1m tolerance on
    # sums of order £1e11), and the free-hours-only world leaves
    # Tax-Free Childcare where it was; the annotations say both.
    heads = sum(d[v] for v in (*FREE_HOURS, TFC))
    if abs(d["gov_spending"] - heads) > 1e6 or abs(d["gov_tax"]) > 1e6:
        raise ValueError(
            f"{source} {year}: the reform moved spending or tax outside the childcare heads"
        )
    if source == CENTAX and abs(d[TFC]) > 1e6:
        raise ValueError(
            f"{year}: removing the 30-hours limit moved Tax-Free Childcare"
        )
    # The engine tests country == ENGLAND for all three free-hours offers,
    # so none may move outside England; only Tax-Free Childcare can.
    outside = {v: d[v] - eng[v] for v in FREE_HOURS}
    if any(abs(x) > 1e6 for x in outside.values()):
        raise ValueError(f"{source} {year}: free hours moved outside England {outside}")
    # an input counts as the dataset's own only in a year the dataset holds it
    supplied = {
        v: str(year) in periods
        for v, periods in art["worlds"]["baseline"]["dataset_inputs"].items()
    }
    take_up = b["take_up"]
    notes = [
        (
            f"Measured on the certified pair, {fy} (engine period {year}, the start "
            f"year, for claim period {year + 1}), people in English households: "
            f"extended hours {_bn(eng['extended_childcare_entitlement'])}, universal "
            f"{_bn(eng['universal_childcare_entitlement'])}, targeted "
            f"{_bn(eng['targeted_childcare_entitlement'])}, Tax-Free Childcare "
            f"{_bn(eng[TFC])} (reform minus current law). UK-wide, gov_spending "
            f"moves {_bn(d['gov_spending'])} and gov_tax {_bn(d['gov_tax'])}; "
            f"Tax-Free Childcare outside England moves {_bn(d[TFC] - eng[TFC])}, "
            "left out because both offers are England's."
        ),
        (
            "Families receiving the extended hours: "
            f"{b['counts']['benunits_receiving_extended'] / 1e6:.2f}m under current "
            f"law, {w['counts']['benunits_receiving_extended'] / 1e6:.2f}m with the "
            "limit removed."
        ),
        " ".join(
            filter(
                None,
                (
                    (
                        "Hours-usage draw: the families receiving the extended hours "
                        "use a weighted mean of "
                        f"{b['hours_usage']['mean_benunits_receiving_extended']:.1f}"
                        f" of {FULL_USE_HOURS:g} weekly hours under current law "
                        "(maximum_extended_childcare_hours_usage)."
                    ),
                    pair.get("hours_draw"),
                ),
            )
        ),
        (
            "Take-up and usage the run read: the weighted share of benefit units "
            "whose take-up input is true under current law is "
            + ", ".join(
                f"{v} {take_up[v]:.3f}"
                + ("" if supplied.get(v) else " (engine default; not in the dataset)")
                for v in sorted(take_up)
            )
            + f"; {HOURS_USAGE_INPUT} is "
            + (
                "the dataset's own input."
                if supplied.get(HOURS_USAGE_INPUT)
                else "the engine's default (not in the dataset for this year)."
            )
        ),
        "Executed limits on 30 April {y}: 30 hours {a:g}, Tax-Free Childcare {t:g} (1e+100 is the "
        "repo's no-limit sentinel, compute_uk_ab2025.NO_LIMIT).".format(
            y=year,
            a=w["limits_executed"][
                "gov.dfe.extended_childcare_entitlement.income.limit"
            ],
            t=w["limits_executed"]["gov.hmrc.tax_free_childcare.income.income_limit"],
        ),
    ]
    full = full_use_cost(art, year) if source == CENTAX else None
    if full is not None:
        notes.append(
            f"Diagnostic, not attached: with every family at the full {FULL_USE_HOURS:g} hours (the "
            f"input set to {FULL_USE_HOURS:g} in both worlds before any calculation) the same reform "
            f"costs £{full / 1e9:.3f}bn in {fy} on this pair."
        )
    return notes


def _full(x) -> bool:
    return x is not None and abs(x - FULL_USE_HOURS) < 1e-6


def _covers(period: str, year: int) -> bool:
    start, end = period.split(".")
    return int(start[:4]) <= year <= int(end[:4])


def full_use_cost(art: dict, year: int) -> float | None:
    """The reform's free-hours cost with every family at the full 30 hours,
    from the run's two full-use worlds, or None when it ran none for this
    year. Each world must record the override the text states: the hours
    input set to 30 in this year before any of its dependents was
    calculated, read back at 30, on the main world's reform (the same
    limits at the no-limit sentinel, in force this year). Anything else
    raises, so no note or diagnosis claims full use without the evidence."""
    diag, y = art["diagnostics"], str(year)
    held = {w: y in diag.get(name, {}).get("years", {}) for w, name in FULL_USE.items()}
    if not any(held.values()):
        return None
    for world, name in FULL_USE.items():
        if not held[world]:
            raise ValueError(
                f"{art['run_id']} {year}: no {name} world beside the other"
            )
        d, main = diag[name], art["worlds"][world]["reform_dict"]
        o = d.get("input_override") or {}
        deps = o.get("dependents_calculated_before_override")
        hours = d["years"][y]["hours_usage"]
        reform = d["reform_dict"]
        same_reform = (reform is None and main is None) or (
            reform is not None
            and main is not None
            and sorted(reform) == sorted(main)
            and all(
                v == art["limit_sentinel"] and _covers(period, year)
                for periods in reform.values()
                for period, v in periods.items()
            )
        )
        evidence = {
            "variable": o.get("variable") == HOURS_USAGE_INPUT,
            "value": o.get("value") == FULL_USE_HOURS,
            "year set": year in o.get("set_for_years", []),
            "set first": isinstance(deps, dict)
            and bool(deps)
            and not any(deps.values()),
            "read back": _full(o.get("post_set_weighted_mean", {}).get(y)),
            "mean, all": _full(hours.get("mean_all_benunits")),
            "mean, receiving": _full(hours.get("mean_benunits_receiving_extended")),
            "reform": same_reform,
        }
        if not all(evidence.values()):
            wrong = sorted(k for k, ok in evidence.items() if not ok)
            raise ValueError(
                f"{art['run_id']} {name} {year}: the record does not show full use: {wrong}"
            )
    return sum(
        diag[FULL_USE["free_hours"]]["years"][y]["sums_gbp"][v]
        - diag[FULL_USE["baseline"]]["years"][y]["sums_gbp"][v]
        for v in FREE_HOURS
    )


def _construction(art: dict, path: Path, source: str, year: int) -> str:
    world = WORLDS[source]
    limits = sorted(art["worlds"][world]["reform_dict"])
    return (
        f"static: the certified world with {', '.join(limits)} set to "
        f"{art['limit_sentinel']:g} minus the certified world as served, engine period {year} "
        f"(FY {year}-{(year + 1) % 100:02d}); minus the change in "
        f"{' + '.join(VARIABLES[source])} for people in English households (microdf "
        f"weights); artifact {path.relative_to(REPO)}"
    )


def published_result(
    score: ExternalScore, spec: list[dict], pub: dict
) -> PEResult | None:
    """The published figure, on the central rows: the comparison the
    dashboard itself drew (its benchmark text names CenTax's central
    static and net costs)."""
    if score.conditions["scenario"] != "central":
        return None
    year = score.period - 1
    value = pub["values_gbp_bn"]["thirty_hours"].get(str(year))
    if value is None:
        return None
    texts, status = match_annotations(score, "published_dashboard", spec)
    after = pub["after"]
    return PEResult(
        claim_id=score.claim_id(),
        computed_value=-value * 1e9,
        status=status,
        engine_version=pub["engine"]["policyengine_uk"],
        data_bundle=pub["dataset"]["release"],
        pe_construction=(
            f"published: the 30-hours leg of PolicyEngine's dashboard ({pub['page']}), "
            f"{pub['values_gbp_bn']['field']}, year {year} (FY {year}-{(year + 1) % 100:02d}); "
            f"{pub['repo']}@{pub['commit'][:7]} {pub['results_file']} (sha256 "
            f"{pub['results_file_sha256'][:12]}); policyengine {pub['engine']['policyengine']}, "
            f"dataset passed unmanaged ({pub['dataset']['management']})"
        ),
        run_id=pub["run_id"],
        computed_at=pub["generated_at"],
        annotations=[
            *texts,
            f"Published figure: £{value:.3f}bn. {pub['corrections']}",
            f"{pub['hours_draw']}.",
            (
                f"On {pub['live']['on']} from {pub['live']['from']} to "
                f"{pub['live']['until']}: {pub['live']['until_basis']}."
            ),
            (
                f"Since then {after['pr']} merged ({after['merged']}): the dashboard's "
                f"own deployment, {after['served_at']}, serves "
                f"£{after['thirty_hours_gbp_bn'][str(year)]:.3f}bn in this year from "
                f"{pub['repo']}@{after['commit'][:7]} on {after['release']} with "
                f"policyengine-uk {after['engine']['policyengine_uk']}. Not attached: "
                f"{after['why_not_attached']}"
            ),
        ],
        baseline_key=BASELINE.baseline_key(),
        policyengine_variables=list(FREE_HOURS),
    )


def certified_result(
    s: ExternalScore, notes: dict, art: dict, path: Path
) -> PEResult | None:
    check_history([(art, path)])
    pair = verified_pair(notes, art)
    year = s.period - 1
    if str(year) not in art["worlds"][WORLDS[s.source]]["years"]:
        return None
    vid = art["variant_id"]
    texts, status = match_annotations(s, "certified", notes[s.source], vid)
    construction = [a["text"] for a in _scoped(notes["construction"], vid)]
    return PEResult(
        claim_id=s.claim_id(),
        computed_value=counterpart(art, s.source, year),
        status=status,
        engine_version=art["engine_version"],
        data_bundle=art["data_bundle"],
        pe_construction=_construction(art, path, s.source, year),
        run_id=art["run_id"],
        computed_at=art["computed_at"],
        annotations=[
            *texts,
            *construction,
            *measured_notes(art, s.source, year, s.conditions["fy"], pair),
        ],
        baseline_key=BASELINE.baseline_key(),
        policyengine_variables=VARIABLES[s.source],
    )


def _published() -> dict:
    path = CENTAX_DIR / "pe" / "published_dashboard.json"
    pub = json.loads(path.read_text())
    _utc(pub["generated_at"], f"{path.name} generated_at")
    if pub["run_id"].startswith(RESERVED_RUN_PREFIX):
        raise ValueError(f"{path.name}: run_id takes the reserved prefix")
    return pub


def results(
    scores: list[ExternalScore],
    artifacts: list[tuple[dict, Path]],
    notes: dict | None = None,
) -> list[PEResult]:
    """Every certified artifact's run on each attached claim, each with the
    notes verified on its own pair, and the published dashboard figure on
    CenTax's central rows, older than all."""
    notes = notes or load_notes()
    check_history(artifacts)
    for art, _ in artifacts:
        verified_pair(notes, art)
    pub = _published()
    oldest = min(art["computed_at"] for art, _ in artifacts)
    out = []
    for s in scores:
        if s.source == CENTAX and s.conditions["component"] not in CENTAX_ATTACHED:
            continue
        for art, path in artifacts:
            r = certified_result(s, notes, art, path)
            if r is not None:
                out.append(r)
        if s.source == CENTAX:
            hist = published_result(s, notes[CENTAX], pub)
            if hist is not None:
                if hist.computed_at >= oldest:
                    raise ValueError(
                        "the published figure must be older than every certified run"
                    )
                out.append(hist)
    return out


def _covering(s: ExternalScore, artifacts: list[tuple[dict, Path]]) -> dict | None:
    """The newest certified run that computed this claim's year: its latest
    certified result, so the run its diagnosis must come from."""
    year = str(s.period - 1)
    runs = [
        art for art, _ in artifacts if year in art["worlds"][WORLDS[s.source]]["years"]
    ]
    return max(runs, key=lambda a: a["computed_at"]) if runs else None


def _diagnosed(s: ExternalScore, art: dict | None, pair: dict | None) -> bool:
    """A CenTax central static row whose latest certified result comes from
    a run on a pair whose verified_pairs entry states a diagnosis."""
    c = s.conditions
    return (
        art is not None
        and pair.get("diagnosis") is not None
        and (s.source, c.get("component"), c.get("scenario"))
        == (CENTAX, "static_cost", "central")
    )


def diagnoses(
    scores: list[ExternalScore],
    artifacts: list[tuple[dict, Path]],
    notes: dict | None = None,
) -> list[tuple]:
    """pe_gap on the CenTax central static rows, linked to microcosm#1126,
    each as the pair of its own latest certified result states it: the
    measured lead from that run, then the pair's verified diagnosis (none for
    a pair that states none). A newer run that skips a claim's year leaves
    that claim's diagnosis with the run that computed it."""
    notes = notes or load_notes()
    check_history(artifacts)
    pairs = {art["run_id"]: verified_pair(notes, art) for art, _ in artifacts}
    rows = []
    for s in scores:
        art = _covering(s, artifacts)
        pair = pairs[art["run_id"]] if art is not None else None
        if not _diagnosed(s, art, pair):
            continue
        c = s.conditions
        year = s.period - 1
        pe = counterpart(art, CENTAX, year)
        hours = art["worlds"]["baseline"]["years"][str(year)]["hours_usage"][
            "mean_benunits_receiving_extended"
        ]
        full = full_use_cost(art, year)
        if full is None:
            raise ValueError(
                f"{art['variant_id']}: the diagnosis needs the full-use diagnostic for "
                f"{year}; rerun with it in --diagnostic-years"
            )
        rationale = (
            f"PolicyEngine's static cost on the certified pair is £{-pe / 1e9:.3f}bn in {c['fy']}, "
            f"{abs(pe / s.value - 1) * 100:.0f}% {'below' if pe > s.value else 'above'} CenTax's "
            f"£{-s.value / 1e9:.2f}bn. Our side first: on this pair the families receiving the "
            f"extended hours use a weighted mean of {hours:.1f} of {FULL_USE_HOURS:g} weekly hours "
            f"(measured), and with every family at the full {FULL_USE_HOURS:g} hours the same "
            f"reform costs £{full / 1e9:.3f}bn "
            f"(diagnostic run). {pair['diagnosis']}"
        )
        rows.append(
            ScorecardDB.diagnosis_row(
                s.claim_id(),
                DiagnosisClass.PE_GAP.value,
                rationale,
                "https://github.com/PolicyEngine/microcosm/issues/1126",
            )
        )
    return rows


def expected(
    scores: list[ExternalScore],
    artifacts: list[tuple[dict, Path]],
    notes: dict | None = None,
) -> dict:
    """The tally the claims, each run's computed years and the published
    file imply, derived without the annotations: a certified run attaches
    to each CenTax static or net row and each CBP row whose year it
    computed; CenTax's static rows are comparable and every net figure a
    concept_mismatch; the published figure attaches to the central static
    (constructed) and net (concept_mismatch) rows in its years."""
    notes = notes or load_notes()
    check_history(artifacts)
    pairs = {art["run_id"]: verified_pair(notes, art) for art, _ in artifacts}
    published_years = _published()["values_gbp_bn"]["thirty_hours"]
    kinds: Counter = Counter()
    statuses: Counter = Counter()
    for s in scores:
        component = s.conditions.get("component")
        if s.source == CENTAX and component not in CENTAX_ATTACHED:
            continue
        year = str(s.period - 1)
        static = component == "static_cost"
        for art, _ in artifacts:
            if year in art["worlds"][WORLDS[s.source]]["years"]:
                kinds["certified"] += 1
                statuses["comparable" if static else "concept_mismatch"] += 1
        if (
            s.source == CENTAX
            and s.conditions["scenario"] == "central"
            and year in published_years
        ):
            kinds["published_dashboard"] += 1
            statuses["constructed" if static else "concept_mismatch"] += 1
    return {
        "claims": 36,
        "claims_by_source": {CENTAX: 24, CBP: 12},
        "results": sum(kinds.values()),
        "results_by_kind": dict(kinds),
        "statuses": dict(statuses),
        "diagnoses": sum(
            _diagnosed(s, art, pairs[art["run_id"]] if art else None)
            for s in scores
            for art in [_covering(s, artifacts)]
        ),
        "drops": {"cbp_taper_rows": 60, "centax_bunching_counts": 12},
    }


def accounting(scores, pe, diag, drops, artifacts) -> dict:
    certified = {art["run_id"] for art, _ in artifacts}
    return {
        "claims": len(scores),
        "claims_by_source": dict(Counter(s.source for s in scores)),
        "results": len(pe),
        "results_by_kind": dict(
            Counter(
                "certified" if r.run_id in certified else "published_dashboard"
                for r in pe
            )
        ),
        "statuses": dict(Counter(r.status.value for r in pe)),
        "diagnoses": len(diag),
        "drops": drops,
    }


def ingest(db_path: Path) -> dict:
    notes = load_notes()
    scores, drops, artifacts = stage(notes)
    art = artifacts[-1][0]
    pe = results(scores, artifacts, notes)
    diag = diagnoses(scores, artifacts, notes)
    counts = accounting(scores, pe, diag, drops, artifacts)
    want = expected(scores, artifacts, notes)
    if counts != want:
        raise ValueError(f"claim accounting drifted: {counts} != {want}")
    db = ScorecardDB(db_path)

    from .baselines import register_baselines_txn
    from .ingest_harvest import sync_lane_feed

    with db.conn:
        old = [
            r[0]
            for r in db.conn.execute(
                "SELECT claim_id FROM external_scores "
                "WHERE json_extract(publication, '$.registry') = ?",
                (REGISTRY_MARK,),
            )
        ]
        for table in ("diagnoses", "pe_results", "external_scores"):
            db.conn.executemany(
                f"DELETE FROM {table} WHERE claim_id = ?", [(c,) for c in old]
            )
        db.conn.executemany(SCORES_SQL, [ScorecardDB.score_row(s) for s in scores])
        db.conn.executemany(RESULTS_SQL, [ScorecardDB.result_row(r) for r in pe])
        db.conn.executemany(DIAGNOSES_SQL, diag)
        register_baselines_txn(db)
        runs = {a["run_id"] for a, _ in artifacts}
        computed = {r.claim_id for r in pe if r.run_id in runs}
        pairs = (
            "the certified pair"
            if len(artifacts) == 1
            else f"{len(artifacts)} certified pairs, the newest"
        )
        detail = (
            f"{len(computed)} of {len(scores)} claims computed on {pairs} "
            f"({art['data_bundle']}, policyengine-uk {art['engine_version']}) — "
            "CenTax Table 4.2 (24 cells: static cost comparable, net cost concept_mismatch) and CBP's "
            "technical appendix (12 abolition cells, concept_mismatch); PolicyEngine's published "
            "dashboard figure kept as history"
            + ("; pe_gap on the central static rows (microcosm#1126)" if diag else "")
        )
        db.conn.execute(LANE_SQL, (LANE_ID, "computed", detail, LANE_UPDATED))
    sync_lane_feed(
        db,
        REPO / "data" / "lanes.json",
        FEED_UPDATED,
        lanes={LANE_ID: LANE_FEED_META},
    )
    db.close()
    return counts


if __name__ == "__main__":
    import sys

    out = Path(sys.argv[1] if len(sys.argv) > 1 else "data/scorecard.db")
    print(json.dumps(ingest(out), indent=1))
