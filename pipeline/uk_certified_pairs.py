"""Certified pairs a lane runs on outside the replay variant index.

A certified pair is a policyengine.py release's certified bundle: the
wrapper, the model package and the data build its packaged bundle manifest
certifies together. data/uk/certified_pairs.json records each one in the
replay variant's identity shape (pipeline/uk_replay_variants.py), under the
id ``pair-<variant slug>``, so a lane's computation can apply the replay
variant's checks to it before the release-replay pipeline qualifies the
pair (docs/uk_replay/RELEASE_REPLAY.md).

No event replay runs on a certified pair: it is not in
data/uk/replay_variants.json, it has no result root or layout, and nothing
here writes either file. A variant the pipeline later qualifies for the same
pair has its own id and identity (its own requirements file), so the pair
record stays: it is the identity the lane's runs on it were checked
against. Experiment populations (docs/uk_replay/POLICY_EXPERIMENTS.md) stay
separate: their results are never ingested.

    from pipeline import uk_certified_pairs as pairs
    record = pairs.get_record("pair-pe6.11.0_uk2.132.6_...")   # or a variant id
    pre = pairs.preflight(record, dataset_source=None)
"""

from __future__ import annotations

import json
from pathlib import Path

from pipeline import uk_replay_variants as variants

ROOT = variants.ROOT
PAIRS_PATH = ROOT / "data" / "uk" / "certified_pairs.json"
KIND = "uk_certified_pairs"
STATUS = "certified_pair"
PREFIX = "pair-"
# What a pair record holds; a variant's status, layout and result root are
# not among them.
FIELDS = frozenset(
    {
        "certification",
        "data_years",
        "data_years_evidence",
        "executor",
        "identity",
        "identity_sha256",
        "note",
        "pair_id",
        "requirements",
        "status",
    }
)


def load_pairs(path: Path = PAIRS_PATH) -> dict:
    document = json.loads(path.read_bytes())
    if document.get("schema_version") != 1 or document.get("kind") != KIND:
        raise variants.VariantError(
            f"{path.name}: schema_version must be 1 and kind {KIND}"
        )
    pairs = document.get("pairs")
    if not isinstance(pairs, list):
        raise variants.VariantError(f"{path.name}: pairs must be a list")
    ids = [pair.get("pair_id") for pair in pairs]
    if len(ids) != len(set(ids)):
        raise variants.VariantError(f"{path.name} repeats a pair_id")
    return document


def validate_pair(record: dict, *, root: Path = ROOT) -> None:
    """Engine-free: the record is one certified pairing (the replay variant's
    identity checks) and a certified pair, not a replay variant."""
    pair_id = record.get("pair_id")
    extra = sorted(set(record) - FIELDS)
    missing = sorted(FIELDS - set(record))
    if extra or missing:
        raise variants.VariantError(
            f"{pair_id}: a certified pair holds exactly {sorted(FIELDS)}; "
            f"extra {extra}, missing {missing}"
        )
    if record["status"] != STATUS:
        raise variants.VariantError(f"{pair_id}: status must be {STATUS}")
    if not str(pair_id).startswith(PREFIX):
        raise variants.VariantError(f"{pair_id}: a pair_id starts {PREFIX}")
    variants.validate_identity(record, pair_id.removeprefix(PREFIX), root=root)


def view(record: dict) -> dict:
    """The fields the variant checks and the lane read, under the pair's own
    id. In memory only: never written, never added to the variant index."""
    return {
        "variant_id": record["pair_id"],
        "certified_pair": True,
        "certification": record["certification"],
        "data_years": record["data_years"],
        "executor": record["executor"],
        "identity": record["identity"],
        "identity_sha256": record["identity_sha256"],
        "requirements": record["requirements"],
        "status": record["status"],
    }


def is_pair(record: dict) -> bool:
    return record.get("certified_pair") is True


def get_record(
    record_id: str | None = None,
    *,
    variants_path: Path = variants.VARIANTS_PATH,
    pairs_path: Path = PAIRS_PATH,
    root: Path = ROOT,
) -> dict:
    """A certified pair's view (an id starting pair-), else a certified
    replay variant (None: the variant file's default), each validated."""
    if record_id is None or not record_id.startswith(PREFIX):
        return variants.get_variant(record_id, path=variants_path, root=root)
    for record in load_pairs(pairs_path)["pairs"]:
        if record["pair_id"] == record_id:
            validate_pair(record, root=root)
            return view(record)
    raise variants.VariantError(f"no certified pair {record_id!r}")


def preflight(record: dict, *, dataset_source: Path | None = None) -> dict:
    """The event runner's preflight for a non-legacy record: a replay
    variant's as it is (compute_uk_event.variant_preflight); for a certified
    pair, the pair checks, then the same installed-environment verification
    and materialised-dataset path."""
    from pipeline import compute_uk_event as event

    if not is_pair(record):
        return event.variant_preflight(record, dataset_source=dataset_source)
    record_id = record.get("variant_id")
    if record.get("status") != STATUS:
        raise variants.VariantError(f"{record_id}: not a certified pair")
    if not isinstance(record_id, str) or not record_id.startswith(PREFIX):
        raise variants.VariantError(f"{record_id}: a pair's id starts {PREFIX}")
    variants.validate_identity(record, record_id.removeprefix(PREFIX))
    installed = variants.verify_installed(record)
    return event.materialized_preflight(
        record, installed, dataset_source=dataset_source
    )
