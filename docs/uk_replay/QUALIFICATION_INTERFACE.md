# Qualification request and replay receipt (v1)

Status: proposed by W6 (policyengine-scorecard) to W4 (policyengine.py
qualification) on 11 October 2026 and accepted in principle by W4 the same
day, with the amendments folded in below (RFC 8785 canonicalisation, the
receipt digest and commit in `STATUS.json`, extra `requested_by` fields, and
the post-release flow). JSON Schemas:
[`schemas/qualification_request.v1.json`](schemas/qualification_request.v1.json),
[`schemas/replay_receipt.v1.json`](schemas/replay_receipt.v1.json) and
[`schemas/replay_status.v1.json`](schemas/replay_status.v1.json).
Implementation: `pipeline/uk_replay_interface.py`. Golden fixtures with
pinned digests: `tests/fixtures/uk_replay/` (`DIGESTS.json`, and the exact
JCS bytes in `*.jcs`).

## Canonical bytes

Both sides compute digests over **RFC 8785 (JCS)** bytes, using the
`rfc8785` package (0.1.4 here). `json.dumps(sort_keys=True)` is not
equivalent: it writes `1e-07` where JCS writes `1e-7`, `1.5e+16` where JCS
writes `15000000000000000`, and escapes non-ASCII characters that JCS
writes as UTF-8. Integers must lie within ±(2^53 − 1); the package refuses
larger ones. The golden request carries these probes in
`requested_by.jcs_probe` and a non-ASCII `requested_by.note`.

Two flows use the same receiver:

* **Pre-promotion qualification.** W4's certify workflow, holding a candidate
  model/data pair it has not yet promoted, sends an immutable request. W6
  validates the candidate's identity and compatibility, reruns the supported
  event corpus, diffs it against the latest certified variant, and returns an
  artifact-bound receipt that qualification consumes.
* **Post-promotion consumer dispatch.** After a policyengine.py release,
  W4's NotifyConsumers sends the same event with `kind: "released_bundle"`,
  the policyengine PyPI wheel SHA-256 and the packaged manifest SHA-256. The
  same receiver handles it, so scorecard ends up with a certified variant
  and a sealed namespace for every release; there is no separate handler.

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
  (`queued` → `running` → `complete` | `rejected` | `failed`, with a
  history of timestamps and Actions run URLs), and on completion
  `REPLAY_RECEIPT.json`. The receipt is committed first; a terminal
  `STATUS.json` is written in a later commit and names `receipt_sha256` and
  `receipt_commit`, so one contents read binds the status to the receipt
  bytes.
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

* `request_id` is not a field: it is the SHA-256 of the request's JCS
  bytes. Both sides test against the golden fixture.
* `requested_by` names the requesting repository and commit;
  `workflow_run_id` is optional (a scorecard catch-up run started outside
  Actions has none), and additional provenance fields such as `run_attempt`
  are accepted. Every other object is closed.
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

How flags arise, so a gate built on them sees the intended events:

* A year unsupported on one side raises `support` on that year's rows, not
  `coverage`. A lost counterpart is `coverage` only where both sides support
  the year.
* `construction` means the executed reform dictionaries differ or a premise
  check changed its result. A change in the current-law value of a parameter
  the construction touches is recorded as context in the row's details, not
  as a flag, because it is what a model release is expected to change.
* For a candidate, the base is the latest certified variant, normally on the
  same data build; the first certified-variant run diffs against the legacy
  populace variant, where the data family itself changes.

* `integrity.status` is `complete`, `incomplete` or `failed`. `failed` means
  a crash, a non-finite aggregate, an identity mismatch after the run started,
  or an accounting identity broken in staging. These are structural failures
  in the PLAN's sense; W4 blocks promotion on them.
* `diff.flag_counts` and `flagged_rows` describe movements against the base
  variant. They carry no verdict. Whether an unexplained material move blocks
  promotion, and who reviews it, is W4's qualification policy under d1344.
* Unsupported years are listed per event and are never counted as failures.

## Agreed points

1. The candidate wrapper is a git commit on a policyengine.py
   `candidate/uk/<model>-<data>` branch whose packaged manifest, pins,
   `uv.lock` and TRO certify the pair; that commit becomes the promotion PR
   head, so the replayed bytes are the promoted bytes.
2. Receipt delivery is by polling `replay-state`; no callback.
3. W4's qualification receipt records `request_id`, `receipt_sha256` and
   `receipt_commit`; nothing of this receipt nests inside W4's execution
   receipt.
4. W4 computes `expected_release_bundle` in a subprocess with the three
   Hugging Face token variables removed.
5. W4's proposed gate on these fields (pending d1344): `rejected`, `failed`,
   integrity `failed` or `incomplete`, and structural, coverage, mapping,
   inertness or construction flags fail the replay gate; numerical and
   support flags go to review; `no_supported_years` fails; unsupported years
   alone never fail.

## Open points

1. Expected turnaround: not yet measured for a full sweep. One probe on
   6.2.6/2.125.1/1.58.0 loaded the baseline and computed five annual
   aggregates in 10.6s at 2.3GB peak, so a five-event sweep should take
   minutes rather than hours on a 16GB runner; the first full run will
   replace this estimate. The queue serialises runs, so a backlog adds wait.
2. The receipt schema versioning rule: additive optional fields keep `v1`;
   renamed or removed fields bump to `v2`.
