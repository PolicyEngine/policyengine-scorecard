"""Pre-publish comparables: every PolicyEngine analysis is searched against
every external producer before it is published (Max, 2026-10-21; docs/COMPARABLES.md).

One directory per analysis, ``sources/analysis-<country>-<slug>/``:

    analysis.json         the analysis: its registry entry on policyengine.org,
                          scope, search terms, the policy worlds it scores and
                          the PolicyEngine estimates it publishes, each pinned
                          to the results file it was read from (SHA-256)
    search_log.json       every search: date, kind, who ran it, and one entry
                          per producer in data/comparables/producers.json
                          (found / none_found / not_applicable, the queries run
                          and the pages checked)
    manifest.jsonl        one line per primary publication, hashed
    claims_staged.jsonl   every comparable found, staged under the harvest
                          rules (sources/harvest-uk-ab2025-2026-09-24/README.md):
                          verbatim value, registered metric and unit or a
                          proposal, named baseline, attribution,
                          benchmark_class; plus the PolicyEngine estimate it is
                          compared with, or why there is none
    annotations.json      the cause of every gap over the threshold
                          (data/comparables/policy.json), each citing a basis

The validator below is the gate: a directory that fails it fails CI, so
everything on main is a complete record. ``build_index`` writes
data/comparables/index.json, which policyengine-app-v2's CI reads to check
that every research entry published after its cutover names a complete
record here. Nothing in this module reads the network.

    PYTHONPATH=. python -m scorecard_db.comparables check
    PYTHONPATH=. python -m scorecard_db.comparables index [--check]
    PYTHONPATH=. python -m scorecard_db.comparables scaffold --country uk \\
        --kind app --slug childcare-100k-threshold
    PYTHONPATH=. python -m scorecard_db.comparables record \\
        analysis-uk-childcare-100k-threshold
    PYTHONPATH=. python -m scorecard_db.comparables due \\
        --apps apps.json --posts posts.json --today 2026-10-26
    PYTHONPATH=. python -m scorecard_db.comparables report \\
        analysis-uk-childcare-100k-threshold --since 2026-10-21
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from . import signs
from .models import ComparisonStatus, Metric, TimeBasis, UnitConcept

REPO = Path(__file__).resolve().parent.parent
SOURCES = REPO / "sources"
COMPARABLES = REPO / "data" / "comparables"
POLICY_PATH = COMPARABLES / "policy.json"
PRODUCERS_PATH = COMPARABLES / "producers.json"
INDEX_PATH = COMPARABLES / "index.json"
REPO_URL = "https://github.com/PolicyEngine/policyengine-scorecard"

ANALYSIS_SCHEMA = "comparables/analysis/1"
SEARCH_SCHEMA = "comparables/search/1"
INDEX_SCHEMA = "comparables/index/1"
DIR_PREFIX = "analysis-"

SEARCH_KINDS = ("prepublish", "backfill", "reharvest")
# found_not_staged: a comparable exists but its primary cannot be read (harvest
# rule 8: a figure whose primary could not be read is never a claim); the note
# says what it is and where it was seen.
RESULTS = ("found", "none_found", "found_not_staged", "not_applicable")
VALUE_KINDS = (
    "point",
    "central",
    "range_low",
    "range_high",
    "approx_chart_reading",
    "cumulative",
)
ATTRIBUTIONS = ("own", "restated", "same_assumptions")
BENCHMARK_CLASSES = ("different_model", "administrative_fact", "same_assumptions")
PARSE_CONFIDENCE = ("high", "medium", "low")
BASIS_KINDS = ("issue", "document", "engine_metadata", "diagnostic")
# An annotation's status is the comparison status its claims carry. "pending"
# is the one extra: a comparable a post-publication re-harvest found, whose
# gap is still being explained on its tracking issue.
ANNOTATION_STATUSES = (
    ComparisonStatus.COMPARABLE.value,
    ComparisonStatus.CONSTRUCTED.value,
    ComparisonStatus.CONCEPT_MISMATCH.value,
    ComparisonStatus.PE_GAP.value,
    "pending",
)
BASELINE_WORLD = "baseline"
# Searches that may find a producer not on the list; the claim then names
# that producer's own slug.
OPEN_FINDERS = ("open_search", "academic")

_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_DATETIME = re.compile(
    r"^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}(:\d{2})?(\.\d+)?(Z|[+-]\d{2}:\d{2})?)?$"
)
_SLUG = re.compile(r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$")
_KEY = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")
_REGISTRY_SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_COMMIT = re.compile(r"^[0-9a-f]{40}$")
_REPO = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
_GITHUB_ISSUE = re.compile(
    r"^https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/(issues|pull)/\d+(#.*)?$"
)
_GITHUB_PINNED = re.compile(
    r"^https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/(blob|tree)/[0-9a-f]{40}/\S+$"
)
_URL = re.compile(r"^https?://\S+$")

# Harvest rule 1: ``value`` is ``value_raw`` normalised to the unit, with the
# conversion named. Only these conversions are checked mechanically; a new one
# is added here deliberately, never improvised in a staged row.
NORMALIZATIONS = {
    "as printed": 1.0,
    "percent as printed": 1.0,
    "fraction x 100 -> percent": 100.0,
    "percent / 100 -> fraction": 0.01,
    "thousands x 1e3": 1e3,
    "millions x 1e6": 1e6,
    "billions x 1e9": 1e9,
    "GBP k x 1e3 -> GBP": 1e3,
    "GBP m x 1e6 -> GBP": 1e6,
    "GBP bn x 1e9 -> GBP": 1e9,
    "USD k x 1e3 -> USD": 1e3,
    "USD m x 1e6 -> USD": 1e6,
    "USD bn x 1e9 -> USD": 1e9,
    "USD tn x 1e12 -> USD": 1e12,
}

_NUMBER = re.compile(r"\d+(?:,\d{3})*(?:\.\d+)?|\.\d+")
_MINUS = ("-", "−", "–")


def parse_printed(value_raw: str) -> float:
    """The number a printed string carries, without its unit or scale.

    "£0.80bn" -> 0.8, "-800m" -> -800, "13,360" -> 13360, "(0.4)" -> -0.4,
    "−£1.2 billion" -> -1.2, "2.1 per cent" -> 2.1. Exactly one number must
    appear; a string with two ("£1.2bn to £1.5bn") is two claims (range_low,
    range_high), never one.
    """
    if not isinstance(value_raw, str) or not value_raw.strip():
        raise ValueError(f"value_raw must be a nonempty string: {value_raw!r}")
    text = value_raw.strip()
    numbers = _NUMBER.findall(text)
    if len(numbers) != 1:
        raise ValueError(
            f"value_raw {value_raw!r} carries {len(numbers)} numbers; stage one "
            "number per claim (a range is two claims)"
        )
    magnitude = float(numbers[0].replace(",", ""))
    before = text[: text.index(numbers[0])]
    negative = any(m in before for m in _MINUS) or (
        text.startswith("(") and text.rstrip().endswith(")")
    )
    if "minus" in before.lower():
        negative = True
    return -magnitude if negative else magnitude


def check_value(row: dict, where: str, signed: bool = False) -> list[str]:
    """Harvest rule 1 for one row: the value parses back from what was printed.

    A staged claim is never re-signed (its sign convention travels in
    conditions). A PolicyEngine estimate is stated in PolicyEngine's own
    orientation for its metric (signs.ORIENTATION), so ``signed`` rows may
    carry ``sign: -1`` with a ``sign_basis`` when the results file prints the
    quantity the other way round (a cost as a positive number)."""
    errors = []
    sign = row.get("sign", 1)
    if signed:
        if sign not in (1, -1):
            return [f"{where}: sign must be 1 or -1"]
        if sign == -1 and not _nonempty_str(row.get("sign_basis"), 10):
            errors.append(f"{where}: sign -1 needs sign_basis saying why")
    elif "sign" in row:
        return [f"{where}: a staged claim is never re-signed (harvest rule 1)"]
    normalization = row.get("normalization")
    if normalization not in NORMALIZATIONS:
        return [
            (
                f"{where}: normalization {normalization!r} is not registered "
                f"(scorecard_db/comparables.py NORMALIZATIONS: {sorted(NORMALIZATIONS)})"
            )
        ]
    value = row.get("value")
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return [f"{where}: value must be a number, got {value!r}"]
    if not math.isfinite(value):
        return [f"{where}: value must be finite, got {value!r}"]
    try:
        parsed = parse_printed(row.get("value_raw"))
    except ValueError as exc:
        return [f"{where}: {exc}"]
    expected = sign * parsed * NORMALIZATIONS[normalization]
    if not math.isclose(value, expected, rel_tol=1e-9, abs_tol=1e-9):
        errors.append(
            f"{where}: value {value!r} is not value_raw {row.get('value_raw')!r} "
            f"under {normalization!r}{' with sign -1' if sign == -1 else ''} "
            f"(expected {expected!r})"
        )
    return errors


# --- the gap -----------------------------------------------------------------


def orientation(claim: dict, country: str) -> tuple[str, str]:
    """How the published value points relative to PolicyEngine's value for the
    metric: scorecard_db/signs.py decides it from the stated sign convention,
    never from comparing the two signs."""
    return signs.classify(
        {
            "metric": claim.get("metric"),
            "conditions": claim.get("conditions") or {},
            "country": country,
            "source": claim.get("source"),
        }
    )


def relative_gap(pe_value: float, external_value: float, relation: str) -> float | None:
    """PolicyEngine / external - 1, with the external value in PolicyEngine's
    orientation. None when no rule orients the external value.

    A zero external value gives 0 when PolicyEngine is also zero and +inf
    otherwise, so a nonzero estimate against a published zero is always over
    any threshold. Opposite signs give a gap below -1."""
    if relation == signs.SAME:
        pe, ext = pe_value, external_value
    elif relation == signs.OPPOSITE:
        pe, ext = pe_value, -external_value
    elif relation == signs.MAGNITUDE:
        pe, ext = abs(pe_value), abs(external_value)
    else:
        return None
    if ext == 0:
        return 0.0 if pe == 0 else math.inf
    return pe / ext - 1.0


def over_threshold(gap: float | None, threshold: float) -> bool:
    return gap is not None and abs(gap) > threshold


# --- loading -----------------------------------------------------------------


def load_policy(path: Path = POLICY_PATH) -> dict:
    policy = json.loads(path.read_text())
    threshold = policy.get("gap_threshold")
    if not (isinstance(threshold, (int, float)) and 0 < threshold < 10):
        raise ValueError(
            f"{path}: gap_threshold must be a positive number: {threshold!r}"
        )
    return policy


def load_producers(path: Path = PRODUCERS_PATH) -> dict:
    data = json.loads(path.read_text())
    for country, producers in data["countries"].items():
        slugs = [p["slug"] for p in producers]
        if len(slugs) != len(set(slugs)):
            raise ValueError(f"{path}: duplicate producer slugs for {country}")
        for p in producers:
            applies = p["applies_to"]
            if applies != "all" and not set(applies) <= set(data["scopes"][country]):
                raise ValueError(
                    f"{path}: {p['slug']} applies_to unknown scope {applies}"
                )
            if not _DATE.match(p["added"]):
                raise ValueError(f"{path}: {p['slug']} added must be YYYY-MM-DD")
    return data


def required_producers(producers: dict, country: str, on: str) -> list[dict]:
    """Every producer a search on date ``on`` must log, in list order."""
    return [p for p in producers["countries"][country] if p["added"] <= on]


def applies(producer: dict, scope: str) -> bool:
    return producer["applies_to"] == "all" or scope in producer["applies_to"]


def producer_for_source(producers: dict, country: str, source: str) -> str | None:
    """The producer slug a claim's ``source`` belongs to, or None when the
    source is not on the list (allowed only for open_search/academic finds)."""
    for p in producers["countries"][country]:
        if source == p["slug"] or source in p.get("aliases", []):
            return p["slug"]
        pattern = p.get("alias_pattern")
        if pattern and re.match(pattern, source):
            return p["slug"]
    return None


def _read_jsonl(path: Path) -> list[dict]:
    rows = []
    for n, line in enumerate(path.read_text().splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{n}: {exc}") from exc
    return rows


@dataclass
class AnalysisRecord:
    directory: Path
    analysis: dict
    search_log: dict
    manifest: list[dict]
    claims: list[dict]
    annotations: list[dict]
    load_errors: list[str] = field(default_factory=list)

    @property
    def name(self) -> str:
        return self.directory.name


FILES = (
    "analysis.json",
    "search_log.json",
    "manifest.jsonl",
    "claims_staged.jsonl",
    "annotations.json",
)


def load_analysis(directory: Path) -> AnalysisRecord:
    errors: list[str] = []
    parts: dict = {}
    for name in FILES:
        path = directory / name
        if not path.exists():
            errors.append(f"{directory.name}: missing {name}")
            continue
        try:
            parts[name] = (
                _read_jsonl(path)
                if name.endswith(".jsonl")
                else json.loads(path.read_text())
            )
        except (ValueError, json.JSONDecodeError) as exc:
            errors.append(f"{directory.name}: {name} does not parse: {exc}")
    return AnalysisRecord(
        directory=directory,
        analysis=parts.get("analysis.json") or {},
        search_log=parts.get("search_log.json") or {},
        manifest=parts.get("manifest.jsonl") or [],
        claims=parts.get("claims_staged.jsonl") or [],
        annotations=parts.get("annotations.json") or [],
        load_errors=errors,
    )


def analysis_dirs(root: Path = SOURCES) -> list[Path]:
    return sorted(
        p for p in root.iterdir() if p.is_dir() and p.name.startswith(DIR_PREFIX)
    )


# --- validation --------------------------------------------------------------


def _registered(enum, value) -> bool:
    return value in {m.value for m in enum}


def _string_map(value) -> bool:
    return isinstance(value, dict) and all(
        isinstance(k, str) and isinstance(v, str) for k, v in value.items()
    )


def _nonempty_str(value, minimum: int = 1) -> bool:
    return isinstance(value, str) and len(value.strip()) >= minimum


def _baseline_labels() -> set[str]:
    from .baselines import BASELINES

    return {label for _, label, *_ in BASELINES}


def _check_basis(basis: dict, where: str) -> list[str]:
    kind, ref = basis.get("kind"), basis.get("ref")
    if kind not in BASIS_KINDS:
        return [f"{where}: basis kind {kind!r} not in {BASIS_KINDS}"]
    if not _nonempty_str(ref):
        return [f"{where}: basis ref is empty"]
    if kind == "issue":
        if not _GITHUB_ISSUE.match(ref):
            return [f"{where}: an issue basis is a GitHub issue or pull URL: {ref!r}"]
        return []
    if kind == "engine_metadata":
        if _GITHUB_PINNED.match(ref) or (REPO / ref.split("#")[0]).exists():
            return []
        return [
            (
                f"{where}: engine metadata is a file pinned to a commit "
                f"(github.com/<org>/<repo>/blob/<40-hex>/<path>) or a path in this repo: {ref!r}"
            )
        ]
    # document / diagnostic: a URL, or a path in this repository that exists
    if _URL.match(ref):
        return []
    if (REPO / ref.split("#")[0]).exists():
        return []
    return [f"{where}: {kind} basis {ref!r} is neither a URL nor a path in this repo"]


def validate(
    record: AnalysisRecord,
    producers: dict | None = None,
    policy: dict | None = None,
) -> list[str]:
    """Every reason this directory is not a complete comparables record."""
    producers = producers or load_producers()
    policy = policy or load_policy()
    errors = list(record.load_errors)
    if errors:
        return errors
    name = record.name
    a = record.analysis

    # analysis.json -----------------------------------------------------------
    if a.get("schema") != ANALYSIS_SCHEMA:
        errors.append(f"{name}: analysis.json schema must be {ANALYSIS_SCHEMA!r}")
    country = a.get("country")
    if country not in producers["countries"]:
        errors.append(f"{name}: country {country!r} has no producer list")
        return errors
    registry = a.get("registry") or {}
    kind, slug = registry.get("kind"), registry.get("slug")
    if kind not in ("app", "post"):
        errors.append(f"{name}: registry.kind must be 'app' or 'post'")
    if not (isinstance(slug, str) and _REGISTRY_SLUG.match(slug)):
        errors.append(f"{name}: registry.slug {slug!r} is not a policyengine.org slug")
    if registry.get("country_id") != country.lower():
        errors.append(f"{name}: registry.country_id must be {country.lower()!r}")
    expected_dir = f"{DIR_PREFIX}{country.lower()}-{slug}"
    if name != expected_dir:
        errors.append(f"{name}: directory must be named {expected_dir!r}")
    if a.get("id") != f"{country.lower()}/{slug}":
        errors.append(f"{name}: id must be {country.lower()}/{slug}")
    if not (isinstance(a.get("url"), str) and a["url"].startswith("https://")):
        errors.append(f"{name}: url must be the analysis's https URL")
    if not _nonempty_str(a.get("title")):
        errors.append(f"{name}: title is empty")
    scope = a.get("scope")
    if scope not in producers["scopes"][country]:
        errors.append(f"{name}: scope {scope!r} not in {producers['scopes'][country]}")
    if not _nonempty_str(a.get("subject"), 10):
        errors.append(f"{name}: subject must say what the analysis estimates")
    terms = a.get("search_terms")
    if not (isinstance(terms, list) and terms and all(_nonempty_str(t) for t in terms)):
        errors.append(f"{name}: search_terms must be a nonempty list of strings")
    owner = a.get("owner") or {}
    if not (
        isinstance(owner.get("author"), str) and _REGISTRY_SLUG.match(owner["author"])
    ):
        errors.append(f"{name}: owner.author must be the app-v2 authors.json key")
    published = a.get("published")
    if published is not None and not (
        isinstance(published, str) and _DATE.match(published)
    ):
        errors.append(f"{name}: published must be YYYY-MM-DD or null")
    worlds = a.get("worlds")
    if not isinstance(worlds, dict):
        errors.append(f"{name}: worlds must map a world key to its policy slug")
        worlds = {}
    for wkey, world in worlds.items():
        if wkey == BASELINE_WORLD or not _KEY.match(wkey):
            errors.append(f"{name}: world key {wkey!r} is reserved or malformed")
        if not (isinstance(world, dict) and _SLUG.match(str(world.get("policy", "")))):
            errors.append(f"{name}: world {wkey!r} needs a policy slug")
        if not _nonempty_str((world or {}).get("description"), 10):
            errors.append(f"{name}: world {wkey!r} needs a description")
    world_keys = set(worlds) | {BASELINE_WORLD}

    estimates: dict[str, dict] = {}
    for i, e in enumerate(a.get("pe_estimates") or []):
        where = f"{name}: pe_estimates[{i}]"
        key = e.get("key")
        if not (isinstance(key, str) and _KEY.match(key)) or key in estimates:
            errors.append(f"{where}: key {key!r} missing, malformed or repeated")
            continue
        estimates[key] = e
        where = f"{name}: estimate {key}"
        if not _nonempty_str(e.get("label")):
            errors.append(f"{where}: label is empty")
        if e.get("world") not in world_keys:
            errors.append(f"{where}: world {e.get('world')!r} is not defined")
        if not _registered(Metric, e.get("metric")):
            errors.append(f"{where}: metric {e.get('metric')!r} is not registered")
        if not _registered(UnitConcept, e.get("unit_concept")):
            errors.append(
                f"{where}: unit_concept {e.get('unit_concept')!r} is not registered"
            )
        if not _registered(TimeBasis, e.get("time_basis")):
            errors.append(
                f"{where}: time_basis {e.get('time_basis')!r} is not registered"
            )
        if not isinstance(e.get("period"), int) or isinstance(e.get("period"), bool):
            errors.append(f"{where}: period must be an integer year")
        if not _string_map(e.get("conditions", {})):
            errors.append(f"{where}: conditions must map strings to strings")
        errors.extend(check_value(e, where, signed=True))
        prov = e.get("provenance") or {}
        if not (isinstance(prov.get("repo"), str) and _REPO.match(prov["repo"])):
            errors.append(f"{where}: provenance.repo must be <org>/<repo>")
        if not (isinstance(prov.get("commit"), str) and _COMMIT.match(prov["commit"])):
            errors.append(f"{where}: provenance.commit must be a 40-hex commit")
        if not (isinstance(prov.get("sha256"), str) and _SHA256.match(prov["sha256"])):
            errors.append(
                f"{where}: provenance.sha256 must be the results file's SHA-256"
            )
        for f in ("path", "field", "dataset"):
            if not _nonempty_str(prov.get(f)):
                errors.append(f"{where}: provenance.{f} is empty")
        if not (
            isinstance(prov.get("computed_at"), str)
            and _DATETIME.match(prov["computed_at"])
        ):
            errors.append(
                f"{where}: provenance.computed_at must be an ISO date or time"
            )
        engine = prov.get("engine")
        if not (_string_map(engine) and engine):
            errors.append(
                f"{where}: provenance.engine must map package names to versions"
            )
    if not estimates:
        errors.append(
            f"{name}: pe_estimates is empty; an analysis that publishes no estimate "
            "is declared no_estimate in the registry, not recorded here"
        )

    # manifest ----------------------------------------------------------------
    manifest: dict[str, dict] = {}
    for i, m in enumerate(record.manifest):
        where = f"{name}: manifest.jsonl line {i + 1}"
        if not (isinstance(m.get("sha256"), str) and _SHA256.match(m["sha256"])):
            errors.append(f"{where}: sha256 must be 64 hex")
            continue
        if not (isinstance(m.get("url"), str) and _URL.match(m["url"])):
            errors.append(f"{where}: url is not a URL")
        for f in ("title", "publisher", "retrieved", "access"):
            if not _nonempty_str(m.get(f)):
                errors.append(f"{where}: {f} is empty")
        if m["sha256"] in manifest:
            errors.append(f"{where}: sha256 repeated")
        manifest[m["sha256"]] = m

    # search_log ----------------------------------------------------------------
    log = record.search_log
    if log.get("schema") != SEARCH_SCHEMA:
        errors.append(f"{name}: search_log.json schema must be {SEARCH_SCHEMA!r}")
    searches = log.get("searches") or []
    if not searches:
        errors.append(f"{name}: search_log has no searches")
    claim_found: dict[str, tuple[str, str, str]] = {}  # key -> (date, kind, producer)
    previous_date = ""
    for i, s in enumerate(searches):
        where = f"{name}: search {i + 1}"
        date, skind = s.get("date"), s.get("kind")
        if not (isinstance(date, str) and _DATE.match(date)):
            errors.append(f"{where}: date must be YYYY-MM-DD")
            continue
        if date < previous_date:
            errors.append(f"{where}: searches must be in date order")
        previous_date = date
        if skind not in SEARCH_KINDS:
            errors.append(f"{where}: kind {skind!r} not in {SEARCH_KINDS}")
        if i == 0 and skind == "reharvest":
            errors.append(
                f"{where}: the first search is a prepublish or backfill search"
            )
        if not _nonempty_str(s.get("by")):
            errors.append(f"{where}: by must name the session or Subfleet job")
        entries = s.get("producers") or []
        logged = [p.get("producer") for p in entries]
        required = required_producers(producers, country, date)
        required_slugs = [p["slug"] for p in required]
        missing = [p for p in required_slugs if p not in logged]
        unknown = [p for p in logged if p not in required_slugs]
        if missing:
            errors.append(f"{where}: producers not searched: {missing}")
        if unknown:
            errors.append(
                f"{where}: producers not on the {country} list on {date}: {unknown}"
            )
        if len(logged) != len(set(logged)):
            errors.append(f"{where}: a producer is logged twice")
        by_slug = {p["slug"]: p for p in required}
        for entry in entries:
            slug_ = entry.get("producer")
            pwhere = f"{where} {slug_}"
            result = entry.get("result")
            claims = entry.get("claims") or []
            queries = entry.get("queries") or []
            checked = entry.get("checked") or []
            if result not in RESULTS:
                errors.append(f"{pwhere}: result {result!r} not in {RESULTS}")
                continue
            if not all(_nonempty_str(q) for q in queries):
                errors.append(f"{pwhere}: queries must be strings")
            if not all(isinstance(u, str) and _URL.match(u) for u in checked):
                errors.append(f"{pwhere}: checked must be URLs")
            producer = by_slug.get(slug_)
            if result == "not_applicable":
                if producer is not None and applies(producer, scope):
                    errors.append(
                        f"{pwhere}: not_applicable, but this producer applies to "
                        f"{scope!r} analyses; search it"
                    )
                if claims:
                    errors.append(f"{pwhere}: not_applicable with claims")
                continue
            if not (queries or checked):
                errors.append(
                    f"{pwhere}: {result} with no query run and no page checked"
                )
            if result == "none_found" and claims:
                errors.append(f"{pwhere}: none_found with claims")
            if result == "found_not_staged":
                if claims:
                    errors.append(f"{pwhere}: found_not_staged with claims")
                if not checked:
                    errors.append(
                        f"{pwhere}: found_not_staged lists the pages it was seen on"
                    )
                if not _nonempty_str(entry.get("note"), 20):
                    errors.append(
                        f"{pwhere}: found_not_staged says what was found and why it is not staged"
                    )
            if result == "found" and not claims:
                errors.append(f"{pwhere}: found with no claims")
            for key in claims:
                if key in claim_found:
                    errors.append(
                        f"{pwhere}: claim {key} already found by an earlier search"
                    )
                claim_found[key] = (date, skind, slug_)

    # claims ----------------------------------------------------------------------
    labels = _baseline_labels()
    claims_by_key: dict[str, dict] = {}
    for i, c in enumerate(record.claims):
        key = c.get("key")
        where = f"{name}: claim {key or i + 1}"
        if not (isinstance(key, str) and _KEY.match(key)) or key in claims_by_key:
            errors.append(f"{where}: key missing, malformed or repeated")
            continue
        claims_by_key[key] = c
        found = claim_found.get(key)
        if found is None:
            errors.append(f"{where}: no search entry lists this claim")
        else:
            if c.get("found_on") != found[0]:
                errors.append(
                    f"{where}: found_on must be {found[0]}, the search that found it"
                )
            if c.get("found_by") != found[2]:
                errors.append(
                    f"{where}: found_by must be {found[2]}, the producer logged"
                )
        source = c.get("source")
        found_by = c.get("found_by")
        if not (isinstance(source, str) and _SLUG.match(source)):
            errors.append(f"{where}: source must be a producer slug")
        elif source == "open_search":
            errors.append(
                f"{where}: source names the producer that published it, not open_search"
            )
        elif found_by not in OPEN_FINDERS:
            # a listed producer's own search finds only that producer's claims
            belongs = producer_for_source(producers, country, source)
            if belongs != found_by:
                errors.append(
                    f"{where}: source {source!r} is not {found_by}'s; a claim from "
                    "another producer is logged under that producer, or under "
                    "open_search when the producer is not on the list"
                )
        metric = c.get("metric")
        if metric is None:
            if not _nonempty_str(c.get("proposed_metric")):
                errors.append(f"{where}: metric null needs proposed_metric")
        elif not _registered(Metric, metric):
            errors.append(
                f"{where}: metric {metric!r} is not registered; use proposed_metric"
            )
        unit = c.get("unit_concept")
        if unit is None:
            if not _nonempty_str(c.get("proposed_unit")):
                errors.append(f"{where}: unit_concept null needs proposed_unit")
        elif not _registered(UnitConcept, unit):
            errors.append(
                f"{where}: unit_concept {unit!r} is not registered; use proposed_unit"
            )
        if c.get("value_kind") not in VALUE_KINDS:
            errors.append(
                f"{where}: value_kind {c.get('value_kind')!r} not in {VALUE_KINDS}"
            )
        if c.get("value_kind") == "approx_chart_reading":
            if not _nonempty_str(c.get("note"), 10):
                errors.append(f"{where}: a chart reading says how it was read in note")
        else:
            errors.extend(check_value(c, where))
            quote = re.sub(r"[\s,]", "", str(c.get("quote", "")))
            raw_digits = "".join(_NUMBER.findall(str(c.get("value_raw", "")))).replace(
                ",", ""
            )
            if raw_digits and raw_digits not in quote:
                errors.append(
                    f"{where}: quote does not contain the printed value {c.get('value_raw')!r}"
                )
        if not isinstance(c.get("period"), int) or isinstance(c.get("period"), bool):
            errors.append(f"{where}: period must be an integer year (FY end year)")
        if not _registered(TimeBasis, c.get("time_basis")):
            errors.append(
                f"{where}: time_basis {c.get('time_basis')!r} is not registered"
            )
        if not _string_map(c.get("conditions")):
            errors.append(f"{where}: conditions must map strings to strings")
        world = c.get("world")
        if world not in world_keys:
            errors.append(f"{where}: world {world!r} is not defined in analysis.json")
        if world != BASELINE_WORLD and not _nonempty_str(c.get("reform_hint")):
            errors.append(
                f"{where}: reform_hint must quote the producer's own words for the world"
            )
        if c.get("attribution") not in ATTRIBUTIONS:
            errors.append(
                f"{where}: attribution {c.get('attribution')!r} not in {ATTRIBUTIONS}"
            )
        bclass = c.get("benchmark_class")
        if bclass not in BENCHMARK_CLASSES:
            errors.append(
                f"{where}: benchmark_class {bclass!r} not in {BENCHMARK_CLASSES}"
            )
        if (c.get("attribution") == "same_assumptions") != (
            bclass == "same_assumptions"
        ):
            errors.append(
                f"{where}: same_assumptions attribution and benchmark_class go together"
            )
        if bclass == "administrative_fact" and world == BASELINE_WORLD:
            errors.append(
                f"{where}: an administrative level is calibration material; stage it "
                "under a producer-level source, where relationships.py assigns it"
            )
        baseline = c.get("baseline_policy")
        if baseline is not None and baseline not in labels:
            errors.append(
                f"{where}: baseline_policy {baseline!r} is not registered in "
                "scorecard_db/baselines.py (harvest rule 7: register it first)"
            )
        if "proposed_baseline" in c:
            errors.append(
                f"{where}: register the baseline before staging (harvest rule 7)"
            )
        pub = c.get("publication") or {}
        for f in ("title", "url", "date", "publisher", "locator", "access"):
            if not _nonempty_str(pub.get(f)):
                errors.append(f"{where}: publication.{f} is empty")
        sha = pub.get("primary_sha256")
        if sha not in manifest:
            errors.append(
                f"{where}: publication.primary_sha256 is not in manifest.jsonl"
            )
        elif manifest[sha].get("url") != pub.get("url"):
            errors.append(f"{where}: publication.url differs from its manifest line")
        for f in ("source_table", "source_column", "quote"):
            if not _nonempty_str(c.get(f)):
                errors.append(f"{where}: {f} is empty")
        if c.get("parse_confidence") not in PARSE_CONFIDENCE:
            errors.append(f"{where}: parse_confidence not in {PARSE_CONFIDENCE}")
        if c.get("status") != "ok":
            errors.append(f"{where}: status must be 'ok'")
        compare = c.get("compare_to")
        if compare is None:
            if not _nonempty_str(c.get("pe_missing"), 10):
                errors.append(f"{where}: not compared, so pe_missing must say why")
            continue
        if c.get("pe_missing") is not None:
            errors.append(f"{where}: compared, so pe_missing must be absent")
        est = estimates.get((compare or {}).get("pe_estimate"))
        if est is None:
            errors.append(f"{where}: compare_to names no PolicyEngine estimate")
            continue
        if c.get("attribution") != "own":
            errors.append(
                f"{where}: only a producer's own estimate is compared ({c.get('attribution')})"
            )
        if c.get("world") != est.get("world"):
            across = (compare or {}).get("across_worlds")
            if not isinstance(across, dict):
                errors.append(
                    f"{where}: world {c.get('world')!r} differs from {est['key']}'s "
                    f"{est.get('world')!r}; compare across worlds only with "
                    "compare_to.across_worlds giving the reason and its basis"
                )
            else:
                if not _nonempty_str(across.get("reason"), 20):
                    errors.append(
                        f"{where}: across_worlds.reason must say why the quantities match"
                    )
                bases = across.get("basis")
                if not (isinstance(bases, list) and bases):
                    errors.append(f"{where}: across_worlds.basis must cite a source")
                else:
                    for b in bases:
                        errors.extend(
                            _check_basis(b if isinstance(b, dict) else {}, where)
                        )
        for f in ("metric", "unit_concept", "period", "time_basis"):
            if c.get(f) != est.get(f):
                errors.append(
                    f"{where}: {f} {c.get(f)!r} differs from {est['key']}'s {est.get(f)!r}; "
                    "a different quantity is not compared (pe_missing says so)"
                )
        relation, basis = orientation(c, country)
        if relation == signs.UNKNOWN:
            errors.append(
                f"{where}: the sign convention does not orient the value ({basis}); "
                "state it in conditions.sign_convention in words signs.py reads"
            )

    for key in claim_found:
        if key not in claims_by_key:
            errors.append(f"{name}: search lists claim {key}, which is not staged")

    # annotations -------------------------------------------------------------------
    annotated: dict[str, dict] = {}
    ids = set()
    for i, n in enumerate(record.annotations):
        nid = n.get("id")
        where = f"{name}: annotation {nid or i + 1}"
        if not (isinstance(nid, str) and _SLUG.match(nid)) or nid in ids:
            errors.append(f"{where}: id missing, malformed or repeated")
            continue
        ids.add(nid)
        status = n.get("status")
        if status not in ANNOTATION_STATUSES:
            errors.append(f"{where}: status {status!r} not in {ANNOTATION_STATUSES}")
        if not _nonempty_str(n.get("cause"), 20):
            errors.append(f"{where}: cause must state the cause (20+ characters)")
        bases = n.get("basis")
        if not (isinstance(bases, list) and bases):
            errors.append(
                f"{where}: basis must cite at least one source (no fabricated mechanisms)"
            )
        else:
            for b in bases:
                errors.extend(_check_basis(b if isinstance(b, dict) else {}, where))
        if not isinstance(n.get("explains_gap"), bool):
            errors.append(f"{where}: explains_gap must be true or false")
        if status == "pending":
            if n.get("explains_gap"):
                errors.append(
                    f"{where}: a pending annotation does not explain the gap yet"
                )
            if not (
                isinstance(n.get("tracking_issue"), str)
                and _GITHUB_ISSUE.match(n["tracking_issue"])
            ):
                errors.append(
                    f"{where}: pending needs the tracking_issue opened for the owner"
                )
        keys = n.get("claims")
        if not (isinstance(keys, list) and keys):
            errors.append(f"{where}: claims must list the claim keys it covers")
            continue
        for key in keys:
            if key not in claims_by_key:
                errors.append(f"{where}: claim {key} is not staged")
            elif key in annotated:
                errors.append(
                    f"{where}: claim {key} already has a status from {annotated[key]['id']}"
                )
            else:
                annotated[key] = n
                if (
                    status == "pending"
                    and claim_found.get(key, ("", ""))[1] != "reharvest"
                ):
                    errors.append(
                        f"{where}: {key} was found before publication; its gap is "
                        "explained before the analysis is recorded, not left pending"
                    )

    # the gate ------------------------------------------------------------------------
    if errors:
        return errors
    for row in evaluate(record, policy):
        if not row["over"]:
            continue
        note = annotated.get(row["key"])
        if note is None:
            errors.append(
                f"{name}: claim {row['key']} is {row['gap']:+.1%} from {row['estimate']} "
                f"(threshold {policy['gap_threshold']:.0%}) and no annotation explains it"
            )
        elif note["status"] != "pending" and not note.get("explains_gap"):
            errors.append(
                f"{name}: claim {row['key']} is over the threshold; its annotation "
                f"{note['id']} must explain the gap (explains_gap: true)"
            )
    return errors


def evaluate(record: AnalysisRecord, policy: dict | None = None) -> list[dict]:
    """One row per staged claim: the comparison and its gap. Assumes a valid
    record (``validate`` returns no errors)."""
    policy = policy or load_policy()
    threshold = policy["gap_threshold"]
    country = record.analysis["country"]
    estimates = {e["key"]: e for e in record.analysis["pe_estimates"]}
    annotated = {}
    for n in record.annotations:
        for key in n["claims"]:
            annotated[key] = n
    rows = []
    for c in record.claims:
        note = annotated.get(c["key"])
        row = {
            "key": c["key"],
            "source": c["source"],
            "found_on": c["found_on"],
            "estimate": None,
            "relation": None,
            "gap": None,
            "over": False,
            "status": note["status"] if note else None,
            "annotation": note["id"] if note else None,
            "explains_gap": bool(note and note.get("explains_gap")),
            "tracking_issue": (note or {}).get("tracking_issue"),
        }
        compare = c.get("compare_to")
        if compare:
            est = estimates[compare["pe_estimate"]]
            relation, _ = orientation(c, country)
            gap = relative_gap(est["value"], c["value"], relation)
            # a comparison across two policy worlds is a documented
            # construction, never plainly comparable
            default = (
                ComparisonStatus.CONSTRUCTED.value
                if c["world"] != est["world"]
                else ComparisonStatus.COMPARABLE.value
            )
            row.update(
                estimate=est["key"],
                relation=relation,
                gap=gap,
                over=over_threshold(gap, threshold),
                status=row["status"] or default,
            )
        rows.append(row)
    return rows


# --- the index ------------------------------------------------------------------


def _search_summary(search: dict) -> dict:
    by_result: dict[str, list[str]] = {r: [] for r in RESULTS}
    for p in search["producers"]:
        by_result[p["result"]].append(p["producer"])
    searched = sorted(
        p["producer"] for p in search["producers"] if p["result"] != "not_applicable"
    )
    return {
        "date": search["date"],
        "kind": search["kind"],
        "producers_searched": searched,
        "producers_with_finds": sorted(by_result["found"]),
        "found_not_staged": sorted(by_result["found_not_staged"]),
        "not_applicable": sorted(by_result["not_applicable"]),
        "found": sum(len(p.get("claims") or []) for p in search["producers"]),
    }


def _round(x: float | None) -> float | None:
    if x is None:
        return None
    if math.isinf(x):
        return None
    return round(x, 4)


def index_entry(record: AnalysisRecord, policy: dict) -> dict:
    a = record.analysis
    rows = evaluate(record, policy)
    compared = [r for r in rows if r["estimate"]]
    gaps = [abs(r["gap"]) for r in compared if r["gap"] is not None]
    over = [r for r in compared if r["over"]]
    return {
        "id": a["id"],
        "kind": a["registry"]["kind"],
        "country_id": a["registry"]["country_id"],
        "slug": a["registry"]["slug"],
        "title": a["title"],
        "url": a["url"],
        "owner": a["owner"]["author"],
        "published": a.get("published"),
        "searches": [_search_summary(s) for s in record.search_log["searches"]],
        "claims": len(rows),
        "compared": len(compared),
        "over_threshold": len(over),
        "explained": sum(1 for r in over if r["explains_gap"]),
        "pending": sum(1 for r in rows if r["status"] == "pending"),
        "unbounded_gaps": sum(1 for g in gaps if math.isinf(g)),
        "max_abs_gap": _round(
            max((g for g in gaps if not math.isinf(g)), default=None)
        ),
        "tracking_issues": sorted(
            {r["tracking_issue"] for r in rows if r["tracking_issue"]}
        ),
        "search_log": f"{REPO_URL}/blob/main/sources/{record.name}/search_log.json",
    }


def build_index(
    root: Path = SOURCES, producers: dict | None = None, policy: dict | None = None
) -> dict:
    """The published index. Raises if any analysis directory is incomplete:
    the index lists only complete records, so a listing is the proof."""
    producers = producers or load_producers()
    policy = policy or load_policy()
    analyses = {}
    problems = []
    for directory in analysis_dirs(root):
        record = load_analysis(directory)
        errors = validate(record, producers, policy)
        if errors:
            problems.extend(errors)
            continue
        analyses[directory.name] = index_entry(record, policy)
    if problems:
        raise ValueError("incomplete comparables records:\n  " + "\n  ".join(problems))
    return {
        "_what": (
            "Every PolicyEngine analysis whose comparables search is recorded in "
            "this repository, keyed by its sources/ directory. Generated by "
            "`python -m scorecard_db.comparables index` from the directories "
            "themselves; policyengine-app-v2 reads it to check a research entry's "
            "comparables record. A listing means the record passed the gate."
        ),
        "schema": INDEX_SCHEMA,
        "gap_threshold": policy["gap_threshold"],
        "analyses": analyses,
    }


def render_index(index: dict) -> str:
    return json.dumps(index, indent=1, sort_keys=False, ensure_ascii=False) + "\n"


# --- the app-v2 record ------------------------------------------------------------


def app_record(record: AnalysisRecord, search_date: str | None = None) -> dict:
    """The ``comparables`` block for the analysis's apps.json / posts.json entry."""
    searches = [
        s
        for s in record.search_log["searches"]
        if s["kind"] in ("prepublish", "backfill")
    ]
    if search_date:
        searches = [s for s in searches if s["date"] == search_date]
    if not searches:
        raise ValueError(
            f"{record.name}: no prepublish or backfill search on {search_date}"
        )
    summary = _search_summary(searches[-1])
    return {
        "status": "reviewed",
        "scorecardSource": record.name,
        "searchDate": summary["date"],
        "searchKind": summary["kind"],
        "producersSearched": summary["producers_searched"],
        "found": summary["found"],
        "searchLog": f"{REPO_URL}/blob/main/sources/{record.name}/search_log.json",
    }


# --- scaffolding -----------------------------------------------------------------


def scaffold(
    country: str, kind: str, slug: str, today: str, root: Path = SOURCES
) -> Path:
    """A skeleton directory for a new search, with every producer to log."""
    producers = load_producers()
    country = country.upper()
    directory = root / f"{DIR_PREFIX}{country.lower()}-{slug}"
    if directory.exists():
        raise SystemExit(
            f"{directory} exists; add a search to its search_log.json instead"
        )
    directory.mkdir(parents=True)
    analysis = {
        "schema": ANALYSIS_SCHEMA,
        "id": f"{country.lower()}/{slug}",
        "country": country,
        "registry": {"kind": kind, "slug": slug, "country_id": country.lower()},
        "title": "",
        "url": f"https://policyengine.org/{country.lower()}/{'research/' if kind == 'post' else ''}{slug}",
        "published": None,
        "owner": {"author": ""},
        "scope": "",
        "subject": "",
        "search_terms": [],
        "worlds": {},
        "pe_estimates": [],
    }
    log = {
        "schema": SEARCH_SCHEMA,
        "searches": [
            {
                "date": today,
                "kind": "prepublish",
                "by": "",
                "producers": [
                    {
                        "producer": p["slug"],
                        "result": "",
                        "queries": [],
                        "checked": [],
                        "claims": [],
                        "note": "",
                    }
                    for p in required_producers(producers, country, today)
                ],
            }
        ],
    }
    (directory / "analysis.json").write_text(
        json.dumps(analysis, indent=1, ensure_ascii=False) + "\n"
    )
    (directory / "search_log.json").write_text(
        json.dumps(log, indent=1, ensure_ascii=False) + "\n"
    )
    (directory / "manifest.jsonl").write_text("")
    (directory / "claims_staged.jsonl").write_text("")
    (directory / "annotations.json").write_text("[]\n")
    return directory


# --- re-harvest support ----------------------------------------------------------


def _post_slug(filename: str) -> str:
    # website/src/data/posts/postTransformers.ts
    return filename.rsplit(".", 1)[0].lower().replace("_", "-")


def research_entries(apps: list[dict], posts: list[dict]) -> list[dict]:
    """policyengine.org research entries with a date, as {kind, country_id,
    slug, date, title, authors, tags}. A post can carry several country tags;
    it is listed once per country it is tagged with."""
    out = []
    for app in apps:
        if not app.get("displayWithResearch") or not app.get("date"):
            continue
        out.append(
            {
                "kind": "app",
                "country_id": app["countryId"],
                "slug": app["slug"],
                "date": app["date"][:10],
                "title": app.get("title", ""),
                "authors": app.get("authors", []),
                "tags": app.get("tags", []),
                "comparables": app.get("comparables"),
            }
        )
    for post in posts:
        for country_id in [
            t for t in post.get("tags", []) if t in ("uk", "us", "ca", "ng", "il")
        ]:
            out.append(
                {
                    "kind": "post",
                    "country_id": country_id,
                    "slug": _post_slug(post["filename"]),
                    "date": post["date"][:10],
                    "title": post.get("title", ""),
                    "authors": post.get("authors", []),
                    "tags": post.get("tags", []),
                    "comparables": post.get("comparables"),
                }
            )
    return out


def due(
    apps: list[dict],
    posts: list[dict],
    today: str,
    window_days: int,
    root: Path = SOURCES,
) -> list[dict]:
    """Research entries published within the re-harvest window that publish an
    estimate (a policy tag, or a reviewed comparables record), with the
    directory that holds (or will hold) their record."""
    start = (dt.date.fromisoformat(today) - dt.timedelta(days=window_days)).isoformat()
    rows = []
    for e in research_entries(apps, posts):
        if not (start <= e["date"] <= today):
            continue
        record = e.get("comparables") or {}
        if record.get("status") == "no_estimate":
            continue
        if "policy" not in e["tags"] and record.get("status") != "reviewed":
            continue
        name = f"{DIR_PREFIX}{e['country_id']}-{e['slug']}"
        rows.append(
            {
                **{k: v for k, v in e.items() if k != "comparables"},
                "source": name,
                "recorded": (root / name).is_dir(),
            }
        )
    return sorted(rows, key=lambda r: (r["date"], r["source"]))


def report(record: AnalysisRecord, since: str, policy: dict | None = None) -> dict:
    """New comparables found on or after ``since`` and every gap over the
    threshold among them: the text of a re-harvest's issue for the owner."""
    rows = [r for r in evaluate(record, policy) if r["found_on"] >= since]
    return {
        "source": record.name,
        "since": since,
        "new_claims": [r["key"] for r in rows],
        "over_threshold": [
            {
                k: r[k]
                for k in (
                    "key",
                    "source",
                    "estimate",
                    "gap",
                    "status",
                    "annotation",
                    "tracking_issue",
                )
            }
            for r in rows
            if r["over"]
        ],
    }


# --- CLI ------------------------------------------------------------------------------


def _today() -> str:
    return dt.datetime.now(dt.timezone.utc).date().isoformat()


def _main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="python -m scorecard_db.comparables")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_check = sub.add_parser("check", help="validate analysis directories")
    p_check.add_argument(
        "dirs", nargs="*", help="directories (default: every sources/analysis-*)"
    )
    p_index = sub.add_parser("index", help="write data/comparables/index.json")
    p_index.add_argument(
        "--check", action="store_true", help="fail if the committed index is stale"
    )
    p_scaffold = sub.add_parser("scaffold", help="start a record for a new analysis")
    p_scaffold.add_argument("--country", required=True)
    p_scaffold.add_argument("--kind", required=True, choices=("app", "post"))
    p_scaffold.add_argument("--slug", required=True)
    p_scaffold.add_argument("--today", default=_today())
    p_record = sub.add_parser("record", help="print the app-v2 comparables block")
    p_record.add_argument("source")
    p_record.add_argument("--search-date")
    p_due = sub.add_parser("due", help="analyses due for re-harvest")
    p_due.add_argument("--apps", required=True)
    p_due.add_argument("--posts", required=True)
    p_due.add_argument("--today", default=_today())
    p_report = sub.add_parser("report", help="comparables found since a date")
    p_report.add_argument("source")
    p_report.add_argument("--since", required=True)
    args = parser.parse_args(argv)

    if args.cmd == "check":
        dirs = [Path(d) for d in args.dirs] or analysis_dirs()
        producers, policy = load_producers(), load_policy()
        failed = 0
        for d in dirs:
            errors = validate(load_analysis(d.resolve()), producers, policy)
            if errors:
                failed += 1
                print(f"FAIL {d.name}")
                for e in errors:
                    print(f"  {e}")
            else:
                print(f"ok   {d.name}")
        return 1 if failed else 0
    if args.cmd == "index":
        text = render_index(build_index())
        if args.check:
            if not INDEX_PATH.exists() or INDEX_PATH.read_text() != text:
                print(
                    f"{INDEX_PATH} is stale: run python -m scorecard_db.comparables index"
                )
                return 1
            print(f"{INDEX_PATH} is current")
            return 0
        INDEX_PATH.write_text(text)
        print(f"wrote {INDEX_PATH}")
        return 0
    if args.cmd == "scaffold":
        print(scaffold(args.country, args.kind, args.slug, args.today))
        return 0
    if args.cmd == "record":
        record = load_analysis(SOURCES / args.source)
        errors = validate(record)
        if errors:
            print("\n".join(errors), file=sys.stderr)
            return 1
        print(
            json.dumps(
                app_record(record, args.search_date), indent=2, ensure_ascii=False
            )
        )
        return 0
    if args.cmd == "due":
        apps = json.loads(Path(args.apps).read_text())
        posts = json.loads(Path(args.posts).read_text())
        window = load_policy()["reharvest_window_days"]
        print(
            json.dumps(
                due(apps, posts, args.today, window), indent=1, ensure_ascii=False
            )
        )
        return 0
    if args.cmd == "report":
        record = load_analysis(SOURCES / args.source)
        errors = validate(record)
        if errors:
            print("\n".join(errors), file=sys.stderr)
            return 1
        print(
            json.dumps(
                report(record, args.since), indent=1, ensure_ascii=False, default=str
            )
        )
        return 0
    return 2


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
