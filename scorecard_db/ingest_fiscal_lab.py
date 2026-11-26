"""Ingest Fiscal Lab's Memo Bill Scores (released 2026-11-24).

Fiscal Lab on Capitol Hill scored 110 bills and proposals from the
Cost-of-Living Healthcare Working Group memo: each one's effect on federal
deficits over FY2027-2036, against current law (CBO's February 2026
baseline), with a low and a high case on 69 of them. Every figure is staged:
110 central claims and 138 range claims, 248 in all, including the bills
PolicyEngine can run little or none of.

Nothing from Fiscal Lab is committed raw. Its Terms of Use allow links and
short excerpts with attribution, so sources/fiscal-lab-memo-scores/adapter.py
reads the fetched page (hash-checked against source.json, git-ignored) and
writes only per-bill identifiers and titles, model and effect labels, the
CSV's printed values (plus H.R. 4849's superseded values from the November 21
build), a link to the bill's dashboard page and its congress.gov link, to
data/externals/fiscal-lab-memo-scores.json. This module reads that extract,
never the page.

pe_status.json states, per bill, what a PolicyEngine counterpart would be:
``not_computed`` where policyengine-us could plausibly run most of it (no
result row; the feed shows the synthetic not_computed), ``pe_gap`` where the
household model has no lever for the provisions that carry the score, or for
only a minority of it (a result row with no value). No PolicyEngine number
is recorded. The pe_gap rows carry no diagnosis: a gated pe_gap diagnosis
needs a citable known issue (issue #9), and none is filed.

Usage:
    PYTHONPATH=. python -m scorecard_db.ingest_fiscal_lab data/scorecard.db
"""

from __future__ import annotations

import hashlib
import json
import re
from decimal import Decimal
from pathlib import Path

from .baselines import register_baselines_txn
from .db import LANE_SQL, RESULTS_SQL, SCORES_SQL, ScorecardDB
from .harvest import REPO, finish, policy_ref
from .ingest_harvest import sync_lane_feed
from .models import (
    BenchmarkClass,
    CalibrationRelationship,
    ComparisonStatus,
    ExternalScore,
    Metric,
    PEResult,
    TimeBasis,
    UnitConcept,
)

SOURCE_DIR = REPO / "sources" / "fiscal-lab-memo-scores"
SOURCE_PATH = SOURCE_DIR / "source.json"
PE_STATUS_PATH = SOURCE_DIR / "pe_status.json"
EXTRACT_PATH = REPO / "data" / "externals" / "fiscal-lab-memo-scores.json"

EXTRACT_SHA256 = "3a68893d09c82ceb26c1edf7b7c96088588d3c6b337f124f23955d1185b75d7b"
PE_STATUS_SHA256 = "f4c49dbbe26bf0ca5882322b68122e142e464a84b3a8540bc3e6b2d5f837be45"

SOURCE = "fiscal_lab"
REGISTRY_MARK = "fiscal_lab_memo_scores"
LANE_ID = "fiscal-lab-memo-scores"
UPDATED = "2026-11-26"
RELEASED = "2026-11-24"
SOURCE_PIN = "dashboard_20261125"
WINDOW = "FY2027-2036"
PERIOD_START, PERIOD_END = 2027, 2036

ENGINE_PIN = "2.2.2"  # policyengine-us source the statuses were judged against
STATUS_RUN_ID = "fiscal-lab-pe-status-2026-11-26"
STATUS_COMPUTED_AT = "2026-11-26T00:00:00+00:00"
# The feed labels a result's release from its bundle id; "no run" reads as
# what it is (the annotations say the status is judged against the source).
NO_RUN_BUNDLE = "no run"

N_BILLS = 110
N_RANGES = 69
N_CLAIMS = N_BILLS + 2 * N_RANGES

# The two bills PolicyEngine/fiscal-lab-comparison is replicating: whatever
# pe_status.json says of the rest, these stay not_computed until its results
# pass review, and they cover only the named provisions.
COMPARISON_REPO = "https://github.com/PolicyEngine/fiscal-lab-comparison"
COMPARISON_BILLS = {"H_R_4849", "H_R_1428"}

SIGN_CONVENTION = "positive = cost (adds to federal deficits)"
FISCAL_MEASURE = "deficit_effect_direct_spending_and_revenues"

_TOP_FIELDS = {
    "schema_version",
    "registry",
    "source_pin",
    "source_sha256",
    "build",
    "unit",
    "bills",
}
_UNIT = "billions of dollars, as the page's CSV prints them"
_ROW_FIELDS = (
    "slug",
    "bill",
    "kind",
    "congress",
    "version",
    "title",
    "models",
    "window",
    "central",
    "low",
    "high",
    "effect",
    "url",
    "bill_url",
)
_SUPERSEDED_FIELDS = {"build", "central", "low", "high", "changelog_id"}
# The one bill Fiscal Lab revised after the release; its released values
# ride along as `superseded`.
SUPERSEDED_SLUGS = {"H_R_4849"}
_OPTIONAL_ROW_FIELDS = {"superseded", "range_rounded"}
# Slug prefix -> the bill label Fiscal Lab prints, and the row's kind.
_LABELS = {"H_R": "H.R.", "S": "S.", "H_J_Res": "H.J.Res."}
_KIND_OF_PREFIX = {
    "H_R": "bill",
    "S": "bill",
    "H_J_Res": "resolution",
    "Concept": "proposal",
}
_KINDS = {"bill", "resolution", "proposal"}
_VERSIONS = {"introduced", "memo_description"}
_EFFECTS = {
    1: "adds to deficits",
    -1: "reduces deficits",
    0: "no significant effect",
}
_VALUE = re.compile(r"^-?\d+\.\d{3}$")
_SLUG = re.compile(r"^(?:H_R|H_J_Res|S)_\d+$|^Concept_[A-Za-z0-9_]+$")
_PAGE = (
    "https://fiscallab.org/score/healthcare-working-group-memo-scores/dashboard.html#"
)
# congress.gov bill pages, or bill text for an earlier Congress's bill
_BILL_URL = re.compile(
    r"^https://www\.congress\.gov/(?:bill/(\d+)(?:st|nd|rd|th)-congress/"
    r"(?:house-bill|senate-bill|house-joint-resolution)/\d+$"
    r"|(\d+)/bills/[a-z]+\d+/)"
)

_STATUS_TOP = {
    "schema_version",
    "registry",
    "engine",
    "judged",
    "method",
    "statuses",
    "bills",
}
_ENTRY_FIELDS = {"status", "scope", "gap_class", "reason", "pe_paths"}
# not_computed: PolicyEngine's levers carry all or most of the score;
# pe_gap: they carry a minority of it (partial) or none of it.
_SCOPES = {"not_computed": {"full", "partial"}, "pe_gap": {"partial", "none"}}
_GAP_CLASS = re.compile(r"^[a-z][a-z0-9_]*$")
# Reasons are PolicyEngine's side in our words: no Fiscal Lab dollar figure
# (its component lines are not committed). Program names that look like
# figures ("340B", "H-1B", "H-2A") are blanked before the check.
_PROGRAM_NAMES = re.compile(r"\b340B\b|\bH-[12][ABC]?\b", re.IGNORECASE)
_DOLLARS = re.compile(
    r"\$|\b(?:million|billion|trillion|dollars?|USD)\b"
    r"|\b\d[\d,]*(?:\.\d+)?\s?(?:bn|mn|[BM])\b",
    re.IGNORECASE,
)


def _quotes_dollars(text: str) -> bool:
    return bool(_DOLLARS.search(_PROGRAM_NAMES.sub(" ", text)))


_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _require_hash(path: Path, expected: str, label: str) -> None:
    actual = _sha256(path)
    if actual != expected:
        raise ValueError(f"Fiscal Lab {label} SHA-256 drifted: {actual} != {expected}")


def _sign(text: str) -> int:
    value = Decimal(text)
    return (value > 0) - (value < 0)


def load_source(path: Path = SOURCE_PATH) -> dict:
    """source.json: every raw file is recorded by hash and none is stored."""
    source = json.loads(path.read_text())
    raw = {r["id"]: r for r in source["raw"]}
    if len(raw) != len(source["raw"]):
        raise ValueError("Fiscal Lab source.json: duplicate raw ids")
    if any(r["stored_in_repo"] is not False for r in raw.values()):
        raise ValueError("Fiscal Lab raw files must all be stored_in_repo false")
    if SOURCE_PIN not in raw or not re.fullmatch(
        r"[0-9a-f]{64}", raw[SOURCE_PIN]["sha256"]
    ):
        raise ValueError(f"Fiscal Lab source.json: no hash for {SOURCE_PIN}")
    return source


def _nonempty(value) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_extract(payload: dict, source: dict) -> None:
    """The extract's shape and census, and its tie to source.json: the page
    hash and build it was rebuilt from must be the ones source.json pins."""
    if set(payload) != _TOP_FIELDS:
        raise ValueError(f"Fiscal Lab extract top level drifted: {sorted(payload)}")
    if payload["schema_version"] != 1 or payload["registry"] != REGISTRY_MARK:
        raise ValueError("Fiscal Lab extract schema version or registry drifted")
    if payload["source_pin"] != SOURCE_PIN:
        raise ValueError(f"Fiscal Lab extract pin drifted: {payload['source_pin']}")
    page = {r["id"]: r for r in source["raw"]}[SOURCE_PIN]
    if payload["source_sha256"] != page["sha256"] or payload["build"] != page.get(
        "build"
    ):
        raise ValueError("Fiscal Lab extract and source.json pin different pages")
    if payload["unit"] != _UNIT:
        raise ValueError(f"Fiscal Lab extract unit drifted: {payload['unit']!r}")
    rows = payload["bills"]
    if len(rows) != N_BILLS:
        raise ValueError(f"Fiscal Lab census: {len(rows)} bills, expected {N_BILLS}")
    slugs = [r.get("slug") for r in rows]
    if len(set(slugs)) != len(slugs):
        raise ValueError("Fiscal Lab extract: duplicate slugs")
    ranges = 0
    for row in rows:
        slug = row.get("slug")
        extra = set(row) - set(_ROW_FIELDS)
        if (
            tuple(k for k in row if k in _ROW_FIELDS) != _ROW_FIELDS
            or extra - _OPTIONAL_ROW_FIELDS
        ):
            raise ValueError(f"Fiscal Lab row schema drifted: {slug}")
        if not isinstance(slug, str) or not _SLUG.match(slug):
            raise ValueError(f"Fiscal Lab slug malformed: {slug!r}")
        if row["kind"] not in _KINDS or row["version"] not in _VERSIONS:
            raise ValueError(f"{slug}: unknown kind or version")
        if (row["kind"] == "proposal") != (row["bill"] is None):
            raise ValueError(f"{slug}: a proposal, and only a proposal, has no bill")
        prefix = "Concept" if slug.startswith("Concept_") else slug.rsplit("_", 1)[0]
        if row["kind"] != _KIND_OF_PREFIX[prefix]:
            raise ValueError(f"{slug}: kind {row['kind']!r} does not fit the slug")
        if row["bill"] is not None:
            prefix, number = slug.rsplit("_", 1)
            if row["bill"] != f"{_LABELS.get(prefix)} {number}":
                raise ValueError(f"{slug}: bill label {row['bill']!r} is not its slug")
        if not _nonempty(row["title"]):
            raise ValueError(f"{slug}: no title")
        if row["congress"] is None and row["version"] != "memo_description":
            raise ValueError(f"{slug}: an introduced bill needs its Congress")
        if row["window"] != WINDOW:
            raise ValueError(f"{slug}: window {row['window']!r}")
        if row["url"] != _PAGE + slug:
            raise ValueError(f"{slug}: link is not the bill's dashboard page")
        if row["bill_url"] is not None:
            m = _BILL_URL.match(row["bill_url"])
            if not m or (m.group(1) or m.group(2)) != row["congress"]:
                raise ValueError(f"{slug}: congress.gov link and Congress disagree")
        if row["congress"] is not None and not re.fullmatch(r"\d{3}", row["congress"]):
            raise ValueError(f"{slug}: Congress {row['congress']!r}")
        if (
            not isinstance(row["models"], list)
            or not row["models"]
            or not all(_nonempty(m) for m in row["models"])
        ):
            raise ValueError(f"{slug}: no model label")
        if (row["low"] is None) != (row["high"] is None):
            raise ValueError(f"{slug}: a range needs both ends")
        values = [row["central"]] + (
            [] if row["low"] is None else [row["low"], row["high"]]
        )
        if not all(isinstance(v, str) and _VALUE.match(v) for v in values):
            raise ValueError(f"{slug}: values must print as the CSV's 3 decimals")
        if row["low"] is not None:
            ranges += 1
            if (
                not Decimal(row["low"])
                <= Decimal(row["central"])
                <= Decimal(row["high"])
            ):
                raise ValueError(f"{slug}: the range does not bracket the central case")
        if row["effect"] != _EFFECTS[_sign(row["central"])]:
            raise ValueError(f"{slug}: effect {row['effect']!r} disagrees with sign")
        if "range_rounded" in row and (
            row["range_rounded"] is not True or row["low"] is None
        ):
            raise ValueError(f"{slug}: range_rounded is true and needs a range")
        if ("superseded" in row) != (slug in SUPERSEDED_SLUGS):
            raise ValueError(f"{slug}: only {sorted(SUPERSEDED_SLUGS)} is superseded")
        if "superseded" in row:
            sup = row["superseded"]
            if set(sup) != _SUPERSEDED_FIELDS or (sup["low"] is None) != (
                row["low"] is None
            ):
                raise ValueError(f"{slug}: superseded record drifted")
            old = [sup["central"]] + (
                [] if sup["low"] is None else [sup["low"], sup["high"]]
            )
            if not all(isinstance(v, str) and _VALUE.match(v) for v in old):
                raise ValueError(f"{slug}: superseded values must print as 3 decimals")
            if sup["low"] is not None and not (
                Decimal(sup["low"]) <= Decimal(sup["central"]) <= Decimal(sup["high"])
            ):
                raise ValueError(f"{slug}: the superseded range does not bracket")
            if not _nonempty(sup["build"]) or not _nonempty(sup["changelog_id"]):
                raise ValueError(f"{slug}: superseded build or changelog id missing")
    if ranges != N_RANGES:
        raise ValueError(f"Fiscal Lab census: {ranges} ranges, expected {N_RANGES}")


def load_extract(
    path: Path = EXTRACT_PATH, *, verify_sha: bool = True, source: dict | None = None
) -> dict:
    if verify_sha:
        _require_hash(path, EXTRACT_SHA256, "extract")
    payload = json.loads(path.read_text())
    validate_extract(payload, source or load_source())
    return payload


def validate_pe_status(status: dict, slugs: set[str]) -> None:
    if set(status) != _STATUS_TOP:
        raise ValueError(f"Fiscal Lab pe_status top level drifted: {sorted(status)}")
    if status["schema_version"] != 1 or status["registry"] != REGISTRY_MARK:
        raise ValueError("Fiscal Lab pe_status schema version or registry drifted")
    if status["engine"] != f"policyengine-us {ENGINE_PIN}":
        raise ValueError(f"Fiscal Lab pe_status engine drifted: {status['engine']}")
    if status["judged"] != STATUS_COMPUTED_AT[:10] or not _DATE.match(status["judged"]):
        raise ValueError(f"Fiscal Lab pe_status judged {status['judged']!r}")
    if not _nonempty(status["method"]) or set(status["statuses"]) != set(_SCOPES):
        raise ValueError("Fiscal Lab pe_status method or status legend drifted")
    if not all(_nonempty(v) for v in status["statuses"].values()):
        raise ValueError("Fiscal Lab pe_status status legend has an empty entry")
    bills = status["bills"]
    if set(bills) != slugs:
        raise ValueError(
            "Fiscal Lab pe_status census drifted: "
            f"missing={sorted(slugs - set(bills))}, extra={sorted(set(bills) - slugs)}"
        )
    for slug, entry in bills.items():
        if set(entry) - {"counterpart"} != _ENTRY_FIELDS:
            raise ValueError(f"{slug}: pe_status fields drifted: {sorted(entry)}")
        if entry["status"] not in _SCOPES:
            raise ValueError(f"{slug}: pe status {entry['status']!r}")
        if entry["scope"] not in _SCOPES[entry["status"]]:
            raise ValueError(f"{slug}: scope {entry['scope']!r} for {entry['status']}")
        if not _GAP_CLASS.match(entry["gap_class"]):
            raise ValueError(f"{slug}: gap_class {entry['gap_class']!r}")
        if (entry["gap_class"] == "none") != (entry["scope"] == "full"):
            raise ValueError(f"{slug}: only a full scope has no gap class")
        if not _nonempty(entry["reason"]) or _quotes_dollars(entry["reason"]):
            raise ValueError(f"{slug}: reason empty or quotes a dollar figure")
        if not isinstance(entry["pe_paths"], list) or not all(
            isinstance(p, str) and p.startswith("policyengine_us/")
            for p in entry["pe_paths"]
        ):
            raise ValueError(f"{slug}: pe_paths must be policyengine_us paths")
        if entry["status"] == "not_computed" and not entry["pe_paths"]:
            raise ValueError(f"{slug}: not_computed must name the levers it would use")
        if slug in COMPARISON_BILLS:
            if entry["status"] != "not_computed" or COMPARISON_REPO not in entry.get(
                "counterpart", ""
            ):
                raise ValueError(
                    f"{slug}: stays not_computed, pointing at {COMPARISON_REPO}"
                )
        elif "counterpart" in entry:
            raise ValueError(f"{slug}: only the comparison bills name a counterpart")


def load_pe_status(
    slugs: set[str], path: Path = PE_STATUS_PATH, *, verify_sha: bool = True
) -> dict:
    if verify_sha:
        _require_hash(path, PE_STATUS_SHA256, "pe_status")
    status = json.loads(path.read_text())
    validate_pe_status(status, slugs)
    return status


def policy_slug(slug: str) -> str:
    """H_R_4849 -> federal.hr4849; Concept_Medicare_for_Kids ->
    federal.concept.medicare_for_kids (memo proposals have no bill)."""
    if slug.startswith("Concept_"):
        return "federal.concept." + slug[len("Concept_") :].lower()
    return "federal." + slug.replace("_", "").lower()


def _reform(row: dict):
    detail = {"version": row["version"]}
    if row["congress"] is not None:
        detail["congress"] = row["congress"]
    return policy_ref(policy_slug(row["slug"]), **detail)


def _usd(text: str) -> float:
    return float(Decimal(text) * 1_000_000_000)


def _publication(
    row: dict, scenario: str, entry: dict, payload: dict, source: dict
) -> dict:
    name = row["title"] if row["bill"] is None else f"{row['bill']}: {row['title']}"
    publication = {
        "registry": REGISTRY_MARK,
        "publish_without_result": True,
        "publisher": source["organization"],
        "title": "Memo Bill Scores",
        "name": name,
        "kind": row["kind"],
        "date": RELEASED,
        "build": payload["build"],
        "url": row["url"],
        "bill_url": row["bill_url"],
        "window": WINDOW,
        "scenario": scenario,
        "value_verbatim": f"{row[scenario]} ($ billions)",
        "effect": row["effect"],
        "models": list(row["models"]),
        "scope_note": (
            "Ten-year total of direct spending and revenues; interest and "
            "spending subject to appropriation are shown separately and are "
            "not part of the figure."
        ),
        "source_pin": SOURCE_PIN,
        "source_sha256": {r["id"]: r for r in source["raw"]}[SOURCE_PIN]["sha256"],
        "pe_status": entry["status"],
        "pe_scope": entry["scope"],
    }
    if entry["status"] == "pe_gap":
        publication["pe_missing"] = entry["reason"]
    if "counterpart" in entry:
        publication["pe_counterpart"] = entry["counterpart"]
    if scenario != "central" and row.get("range_rounded"):
        publication["range_rounded"] = True
        publication["range_note"] = (
            "Fiscal Lab's CSV and headline range round this case to $0.1 "
            "billion. The total row of the bill's score table carries it to "
            "three decimals in the page's embedded data; the page's table "
            "prints one decimal."
        )
    if "superseded" in row:
        sup = row["superseded"]
        publication["superseded"] = {
            "build": sup["build"],
            "value_verbatim": f"{sup[scenario]} ($ billions)",
            "changelog_id": sup["changelog_id"],
        }
    return publication


def stage_scores(
    payload: dict | None = None,
    status: dict | None = None,
    source: dict | None = None,
) -> list[ExternalScore]:
    source = source or load_source()
    payload = payload if payload is not None else load_extract(source=source)
    validate_extract(payload, source)
    slugs = {r["slug"] for r in payload["bills"]}
    status = status if status is not None else load_pe_status(slugs)
    validate_pe_status(status, slugs)
    scores = []
    for row in payload["bills"]:
        entry = status["bills"][row["slug"]]
        scenarios = ["central"] + ([] if row["low"] is None else ["low", "high"])
        for scenario in scenarios:
            scores.append(
                ExternalScore(
                    source=SOURCE,
                    source_model="Fiscal Lab: " + "; ".join(row["models"]),
                    source_column=(
                        f"{WINDOW} total, {scenario} case: {row[scenario]} ($bn"
                        + (
                            ", rounded by Fiscal Lab to $0.1bn)"
                            if scenario != "central" and row.get("range_rounded")
                            else ")"
                        )
                    ),
                    publication=_publication(row, scenario, entry, payload, source),
                    metric=Metric.PRIMARY_DEFICIT_CHANGE,
                    unit_concept=UnitConcept.USD,
                    period=PERIOD_END,
                    time_basis=TimeBasis.FISCAL_YEAR,
                    value=_usd(row[scenario]),
                    value_kind="usd",
                    conditions={
                        "geography": "US",
                        "window_kind": "total",
                        "scenario": scenario,
                        "benchmark_class": BenchmarkClass.DIFFERENT_MODEL.value,
                        "sign_convention": SIGN_CONVENTION,
                        "fiscal_measure": FISCAL_MEASURE,
                        "data_vintage": "cbo_baseline_2026_02",
                    },
                    reform=_reform(row),
                    calibration_relationship=CalibrationRelationship.HELD_OUT,
                    period_start=PERIOD_START,
                    period_end=PERIOD_END,
                )
            )
    if len(scores) != N_CLAIMS:
        raise ValueError(f"Fiscal Lab census: {len(scores)} claims, not {N_CLAIMS}")
    return finish(scores, REGISTRY_MARK)


def gap_rows(db: ScorecardDB, scores: list[ExternalScore], status: dict) -> list[tuple]:
    """One valueless pe_gap result per claim on a bill whose score the
    household model cannot carry (none or only a minority of it);
    not_computed bills get none."""
    baseline = {
        r["claim_id"]: r["baseline_key"]
        for r in db.conn.execute(
            "SELECT claim_id, baseline_key FROM external_scores "
            "WHERE json_extract(publication, '$.registry') = ?",
            (REGISTRY_MARK,),
        )
    }
    rows = []
    for score in scores:
        slug = score.publication["url"].rsplit("#", 1)[1]
        entry = status["bills"][slug]
        if entry["status"] != "pe_gap":
            continue
        rows.append(
            ScorecardDB.result_row(
                PEResult(
                    claim_id=score.claim_id(),
                    computed_value=None,
                    status=ComparisonStatus.PE_GAP,
                    engine_version=ENGINE_PIN,
                    data_bundle=NO_RUN_BUNDLE,
                    pe_construction=f"pe_gap:{entry['gap_class']}:{slug}",
                    run_id=STATUS_RUN_ID,
                    computed_at=STATUS_COMPUTED_AT,
                    annotations=[
                        entry["reason"],
                        (
                            "no run executed: the status is judged against the "
                            f"policyengine-us {ENGINE_PIN} source"
                        ),
                    ],
                    baseline_key=baseline[score.claim_id()],
                    policyengine_variables=[],
                )
            )
        )
    return rows


_PROTECTED_STAGES = {"diagnosing", "published", "regressed"}


def _write_lane(db: ScorecardDB, status: dict, n_claims: int) -> tuple[str, int]:
    """Set the lane from each claim's latest result, ordered as the feed
    orders them (computed_at, then id), following the NZ Treasury ingest:
    a later stage (diagnosing, published, regressed) is never rolled back; a
    claim whose latest result comes from another run and is not
    not_computed counts as computed; losing every one after computed is a
    regression. This module's own pe_gap rows never count, and where one is
    the latest row the feed shows it, so the lane does not count that claim
    either."""
    state = db.conn.execute(
        "SELECT COUNT(*) AS n, MAX(substr(r.computed_at, 1, 10)) AS latest "
        "FROM external_scores s JOIN pe_results r ON r.id = ("
        "SELECT id FROM pe_results WHERE claim_id = s.claim_id "
        "ORDER BY computed_at DESC, id DESC LIMIT 1) "
        "WHERE json_extract(s.publication, '$.registry') = ? "
        "AND r.run_id IS NOT ? AND r.status != 'not_computed'",
        (REGISTRY_MARK, STATUS_RUN_ID),
    ).fetchone()
    computed = state["n"]
    gaps = sum(1 for e in status["bills"].values() if e["status"] == "pe_gap")
    base = (
        f"{n_claims} claims on {N_BILLS} bills (FY2027-2036 totals, "
        f"{N_RANGES} with low-high ranges)"
    )
    outside = f"{gaps} mostly or wholly outside the household model (pe_gap)"
    current = db.conn.execute(
        "SELECT stage FROM lanes WHERE lane = ?", (LANE_ID,)
    ).fetchone()
    if current is not None and current["stage"] in _PROTECTED_STAGES:
        return current["stage"], computed
    if computed:
        detail = f"{computed} of {n_claims} claims computed — {base}; {outside}"
        db.conn.execute(
            LANE_SQL, (LANE_ID, "computed", detail, state["latest"] or UPDATED)
        )
        return "computed", computed
    if current is not None and current["stage"] == "computed":
        detail = f"0 of {n_claims} claims retain results — {base}; {outside}"
        db.conn.execute(LANE_SQL, (LANE_ID, "regressed", detail, UPDATED))
        return "regressed", computed
    detail = f"{base}; none computed: {N_BILLS - gaps} bills not computed, {outside}"
    db.conn.execute(LANE_SQL, (LANE_ID, "ingested", detail, UPDATED))
    return "ingested", computed


def ingest(db_path: Path) -> dict:
    """Validate, replace this registry, then mirror the lane.

    Claims that left the census go with their results and diagnoses. On the
    claims that remain, only this module's own pe_gap rows (STATUS_RUN_ID)
    are replaced, so a counterpart attached later by another step survives a
    rerun."""
    source = load_source()
    payload = load_extract(source=source)
    status = load_pe_status({r["slug"] for r in payload["bills"]})
    scores = stage_scores(payload, status, source)
    new_ids = {s.claim_id() for s in scores}
    db = ScorecardDB(db_path)
    try:
        with db.conn:
            old = {
                r[0]
                for r in db.conn.execute(
                    "SELECT claim_id FROM external_scores "
                    "WHERE json_extract(publication, '$.registry') = ?",
                    (REGISTRY_MARK,),
                )
            }
            stale = sorted(old - new_ids)
            if stale:
                marks = ",".join("?" for _ in stale)
                for table in ("diagnoses", "pe_results", "external_scores"):
                    db.conn.execute(
                        f"DELETE FROM {table} WHERE claim_id IN ({marks})", stale
                    )
            kept = sorted(old & new_ids)
            if kept:
                marks = ",".join("?" for _ in kept)
                db.conn.execute(
                    f"DELETE FROM pe_results WHERE run_id = ? "
                    f"AND claim_id IN ({marks})",
                    [STATUS_RUN_ID, *kept],
                )
            db.conn.executemany(SCORES_SQL, [ScorecardDB.score_row(s) for s in scores])
            register_baselines_txn(db)
            results = gap_rows(db, scores, status)
            db.conn.executemany(RESULTS_SQL, results)
            lane_stage, computed_claims = _write_lane(db, status, len(scores))
        lanes_synced = sync_lane_feed(
            db,
            REPO / "data" / "lanes.json",
            UPDATED,
            lanes={
                LANE_ID: {
                    "source": "Fiscal Lab",
                    "area": "health bill scores (Healthcare Working Group memo)",
                    "mode": 2,
                    "country": "US",
                }
            },
        )
        coverage = db.coverage()
    finally:
        db.close()
    return {
        "claims": len(scores),
        "pe_gap_results": len(results),
        "computed_claims": computed_claims,
        "lane": LANE_ID,
        "lane_stage": lane_stage,
        "lanes_synced": lanes_synced,
        "coverage": coverage,
    }


if __name__ == "__main__":
    import sys

    output = Path(sys.argv[1] if len(sys.argv) > 1 else "data/scorecard.db")
    print(json.dumps(ingest(output), indent=1))
