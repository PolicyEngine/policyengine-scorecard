"""Canonical identities for qualification requests and replay receipts.

Release qualification (policyengine.py) sends a request; this repository
returns a receipt. Both sides address them by digest, so both must produce
the same bytes: RFC 8785 JSON Canonicalization Scheme (JCS), via the
``rfc8785`` package. JCS fixes what ``json.dumps(sort_keys=True)`` leaves to
the implementation: number serialisation (``1e-7``, not ``1e-07``;
``15000000000000000``, not ``1.5e+16``) and literal UTF-8 for non-ASCII
strings. See docs/uk_replay/QUALIFICATION_INTERFACE.md.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_DIR = ROOT / "docs" / "uk_replay" / "schemas"
REQUEST_SCHEMA_ID = "policyengine.uk-replay-qualification-request/v1"
RECEIPT_SCHEMA_ID = "policyengine.uk-replay-receipt/v1"
STATUS_SCHEMA_ID = "policyengine.uk-replay-status/v1"
SCHEMA_FILES = {
    REQUEST_SCHEMA_ID: "qualification_request.v1.json",
    RECEIPT_SCHEMA_ID: "replay_receipt.v1.json",
    STATUS_SCHEMA_ID: "replay_status.v1.json",
}


def jcs_bytes(value: Any) -> bytes:
    """RFC 8785 canonical UTF-8 bytes; the package refuses non-finite numbers."""
    import rfc8785

    return rfc8785.dumps(value)


def jcs_sha256(value: Any) -> str:
    return hashlib.sha256(jcs_bytes(value)).hexdigest()


def request_id(request: dict) -> str:
    """The request's own digest; it is never a field of the request."""
    if "request_id" in request:
        raise ValueError("request_id is derived from the request, not carried in it")
    return jcs_sha256(request)


def receipt_sha256(receipt: dict) -> str:
    """Digest of the receipt without its own receipt_sha256 field."""
    return jcs_sha256({k: v for k, v in receipt.items() if k != "receipt_sha256"})


def seal_receipt(receipt: dict) -> dict:
    sealed = {k: v for k, v in receipt.items() if k != "receipt_sha256"}
    sealed["receipt_sha256"] = receipt_sha256(sealed)
    return sealed


def load_schema(schema_id: str) -> dict:
    return json.loads((SCHEMA_DIR / SCHEMA_FILES[schema_id]).read_bytes())


def validate(document: dict, schema_id: str) -> None:
    """JSON Schema validation, then the digest identity a schema cannot express."""
    import jsonschema

    jsonschema.Draft202012Validator(
        load_schema(schema_id),
        format_checker=jsonschema.Draft202012Validator.FORMAT_CHECKER,
    ).validate(document)
    if schema_id == RECEIPT_SCHEMA_ID and (
        document["receipt_sha256"] != receipt_sha256(document)
    ):
        raise ValueError("receipt_sha256 does not match the receipt's canonical bytes")


def validate_request(request: dict) -> str:
    """Validate a request and return its request_id."""
    validate(request, REQUEST_SCHEMA_ID)
    return request_id(request)
