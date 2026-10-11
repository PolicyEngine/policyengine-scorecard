# Qualification request and replay receipt (v1, proposed)

Status: proposal from W6 (policyengine-scorecard) to W4 (policyengine.py
qualification), 11 October 2026, for agreement by 15 October. JSON Schemas:
[`schemas/qualification_request.v1.json`](schemas/qualification_request.v1.json)
and [`schemas/replay_receipt.v1.json`](schemas/replay_receipt.v1.json).

Two flows use the same receiver:

* **Pre-promotion qualification.** W4's certify workflow, holding a candidate
  model/data pair it has not yet promoted, sends an immutable request. W6
  validates the candidate's identity and compatibility, reruns the supported
  event corpus, diffs it against the latest certified variant, and returns an
  artifact-bound receipt that qualification consumes.
* **Post-promotion consumer dispatch.** After a policyengine.py release, the
  existing dispatcher notifies consumers. Scorecard treats a released bundle
  it has not replayed as a request with `kind: "released_bundle"`, so it
  ends up with a certified variant and a sealed namespace.

## Transport

* W4 sends `repository_dispatch` to `PolicyEngine/policyengine-scorecard`
  with `event_type: "uk-replay-qualification-request"` and
  `client_payload: {"request": <request>}`. W4 alone edits the policyengine.py
  dispatcher and its GitHub App token scope; scorecard needs
  `contents: read` on policyengine.py (public) and nothing else from W4.
* GitHub keeps at most one pending run per concurrency group and cancels
  older pending runs, so the receiver's first step writes the request to the
  persistent queue on the `replay-state` branch before anything else. A
  scheduled catch-up (every 3 hours) drains the queue and discovers
  policyengine.py releases that were never dispatched.
* State for request `<request_id>` lives at
  `replay-state:requests/<request_id>/`:
  `REQUEST.json` (the bytes received), `STATUS.json`
  (`queued` → `running` → `complete` | `rejected` | `failed`, with
  timestamps and the Actions run URL), and on completion
  `REPLAY_RECEIPT.json`.
* W4 polls `GET /repos/PolicyEngine/policyengine-scorecard/contents/requests/<request_id>/STATUS.json?ref=replay-state`
  (the repository is public). A receipt is addressed by the request's own
  digest, so W4 needs no callback and no scorecard token.
* Duplicate requests (same `request_id`) are idempotent: an existing
  terminal status is returned, never rerun. A failed request can be retried
  only by a new request (a different `attempt`).

## Request

```json
{
 "schema": "policyengine.uk-replay-qualification-request/v1",
 "kind": "candidate" ,
 "attempt": 1,
 "candidate": {
  "policyengine": {
   "version": "6.2.7",
   "source": {"git": {"repository": "PolicyEngine/policyengine.py", "commit": "<40-hex>"}},
   "packaged_bundle_manifest_sha256": "<64-hex>"
  },
  "policyengine_uk": {"version": "2.126.8", "wheel_sha256": "<64-hex>"},
  "policyengine_core": {"version": "3.33.0", "wheel_sha256": "<64-hex>"},
  "data": {
   "build_id": "policyengine-uk-data-1.58.0",
   "dataset": "enhanced_frs_2024_25",
   "repo_id": "policyengine/policyengine-uk-data-private",
   "repo_type": "model",
   "revision": "1.58.0",
   "path": "enhanced_frs_2024_25.h5",
   "sha256": "<64-hex>",
   "size_bytes": 128369110,
   "release_manifest_sha256": "<64-hex>"
  },
  "expected_release_bundle": { "...": "the exact pe.uk.uk_latest.release_bundle under packaged certification" }
 },
 "compare_to": "latest_certified",
 "requested_by": {
  "repository": "PolicyEngine/policyengine.py",
  "workflow_run_id": 1234567890,
  "commit": "<40-hex>"
 }
}
```

* `request_id` is not a field: it is the SHA-256 of the canonical request
  JSON (sorted keys, no whitespace, UTF-8). Both sides compute it the same
  way; `tests/fixtures/` holds a shared golden example.
* The wrapper is identified by `version` plus either a PyPI wheel
  (`{"pypi": {"wheel_sha256": …}}`) or, for an unreleased candidate whose
  regenerated manifest is not on PyPI yet, a public git commit. Scorecard
  installs exactly that, then checks the installed packaged manifest's SHA-256.
* Model and core are PyPI wheels pinned by SHA-256.
* `kind` is `candidate` or `released_bundle`.
* `compare_to` is `latest_certified` (default) or a `variant_id`.

## What scorecard validates before running

The candidate becomes a `candidate` variant record (RELEASE_REPLAY.md). It is
**rejected**, with a code, when:

| Code | Condition |
|---|---|
| `schema_invalid` | The request fails the v1 schema. |
| `artifact_hash_mismatch` | A downloaded wheel, the installed packaged manifest or the dataset bytes differ from the request. |
| `release_bundle_mismatch` | `pe.uk.uk_latest.release_bundle` under packaged certification differs from `expected_release_bundle`. |
| `incompatible_pair` | The packaged certification does not name the candidate model version, or the dataset is not the bundle's certified artifact. |
| `data_access_failed` | The dataset could not be fetched with the receiver's credential. |
| `no_supported_years` | No event year falls in the dataset's supported years. |

A rejected request has no numerical results; its receipt says why.

## Receipt

```json
{
 "schema": "policyengine.uk-replay-receipt/v1",
 "request_id": "<64-hex>",
 "status": "complete",
 "rejection": null,
 "variant_id": "pe6.2.7_uk2.126.8_policyengine-uk-data-1.58.0",
 "variant_identity_sha256": "<64-hex>",
 "execution": {
  "packages": {"policyengine": {"version": "6.2.7", "record_sha256": "…"}, "...": "..."},
  "packaged_bundle_manifest_sha256": "…",
  "release_bundle": {"...": "..."},
  "dataset_sha256": "…",
  "requirements_sha256": "…",
  "python": "3.12.13",
  "platform": "Linux-…",
  "runner": "github-actions ubuntu-latest" 
 },
 "corpus": {
  "corpus_version": "uk-fiscal-event-replay/1",
  "events": {
   "autumn_budget_2024": {
    "registry_sha256": "…",
    "supported_years": [2024, 2025, 2026, 2027, 2028, 2029],
    "unsupported_years": [],
    "run_manifest_sha256": "…",
    "staging_manifest_sha256": "…",
    "comparison_provenance_sha256": "…",
    "artifacts": 30,
    "full_supported_grid_complete": true,
    "inert_measure_years": []
   }
  }
 },
 "integrity": {
  "status": "complete",
  "failures": []
 },
 "diff": {
  "base_variant_id": "pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0",
  "diff_sha256": "…",
  "flag_counts": {"numerical": 0, "structural": 0, "coverage": 0, "mapping": 0, "support": 0, "inertness": 0, "construction": 0},
  "flagged_rows": [ {"event": "…", "measure_key": "…", "year": 2026, "level": "head", "key": "income_tax", "flags": ["numerical"], "base_gbp": 0.0, "head_gbp": 0.0} ]
 },
 "results": {
  "repository": "PolicyEngine/policyengine-scorecard",
  "ref": "replay-state",
  "commit": "<40-hex>",
  "path": "requests/<request_id>/results/"
 },
 "receipt_sha256": "<64-hex of the canonical receipt without this field>"
}
```

### Division of judgement

* `integrity.status` is `complete`, `incomplete` or `failed`. `failed` means
  a crash, a non-finite aggregate, an identity mismatch after the run started,
  or an accounting identity broken in staging. These are structural failures
  in the PLAN's sense; W4 blocks promotion on them.
* `diff.flag_counts` and `flagged_rows` describe movements against the base
  variant. They carry no verdict. Whether an unexplained material move blocks
  promotion, and who reviews it, is W4's qualification policy under d1344.
* Unsupported years are listed per event and are never counted as failures.

## Open points for W4

1. Does the candidate wrapper arrive as a git commit (as proposed) or as a
   wheel artifact? Scorecard can consume either; a wheel needs a URL it can
   read without a token.
2. Receipt delivery: polling `replay-state` (proposed) or an additional
   callback dispatch to policyengine.py.
3. Expected turnaround: not yet measured for a full sweep. One probe on
   6.2.6/2.125.1/1.58.0 loaded the baseline and computed five annual
   aggregates in 10.6s at 2.3GB peak, so a five-event sweep should take
   minutes rather than hours on a 16GB runner; the first full run will
   replace this estimate. The queue serialises runs, so a backlog adds wait.
4. The receipt schema versioning rule: additive fields keep `v1`; renamed or
   removed fields bump to `v2`.
