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
  same receiver handles it and records the variant and sealed namespace for
  each successfully replayed dispatched release; there is no separate handler.
  Missed-dispatch discovery constructs the same `released_bundle` request
  from published artifacts and uses this queue and receiver.

## Transport

* W4 sends `repository_dispatch` to `PolicyEngine/policyengine-scorecard`
  with `event_type: "uk-replay-qualification-request"` and
  `client_payload: {"request": <request>}`. W4 alone edits the policyengine.py
  dispatcher and its GitHub App token scope; scorecard needs
  `contents: read` on policyengine.py (public) and nothing else from W4.
* The receiver writes incoming requests to the persistent queue on the
  `replay-state` branch, then dispatches a drain run. Incoming runs have
  distinct concurrency groups; the discovery/prepare/run/record drain sequence
  shares `uk-replay-drain`. GitHub's default concurrency queue can replace an older
  pending run, so requests remain in the persistent queue until handled.
  ([GitHub concurrency documentation](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency))
  Every 3 hours a schedule-only `tick` job dispatches an empty
  `workflow_dispatch` drain, without receiving the dataset token. Only an
  empty-request `workflow_dispatch` runs `discover` → `discover_enqueue` →
  `prepare`; incoming requests enqueue directly, and the workflow has no
  pull-request trigger. Discovery failures do not block `prepare` from
  draining requests already queued.
* The read-only `discover` job checks out without persisted credentials. It
  considers stable, non-yanked PyPI wrapper releases whose wheel upload is at
  least six hours old, oldest first. A version must be strictly newer than
  both the newest certified variant (currently 6.5.0) and the newest wrapper
  version named by any recorded request, regardless of kind or status
  (`queued`, `running`, `complete`, `failed` or `rejected`). A requested or
  certified 6.5.0 suppresses 6.4.2 and 6.4.3 as well as 6.5.0; superseded
  patch releases are not backfilled. Discovery builds at most three requests
  from at most 30 release attempts per drain.
  Before building a request it reads the wheel's static PyPI integrity JSON
  and requires an attestation bundle whose publisher fields match exactly:
  `kind: "GitHub"`, `repository: "PolicyEngine/policyengine.py"`,
  `workflow: "push.yaml"`, and `environment: "pypi"` (the
  [checked 6.5.0 provenance response](https://pypi.org/integrity/policyengine/6.5.0/policyengine-6.5.0-py3-none-any.whl/provenance)).
  Missing attestations, another publisher and unreadable provenance responses
  become permanent skips with the response's SHA-256 as evidence; transient
  HTTP failures are retried. A response stopped at the size cap is retryable
  because no complete-response digest was obtained. The provenance response's
  SHA-256 enters accepted requests as `requested_by.pypi_provenance_sha256`
  and is also logged.
  The job reads downloaded wheels as ZIP/JSON data and runs no provenance,
  release or candidate code. Streaming responses are capped at 64 MiB for
  wheels and 1 MiB for PyPI JSON; manifest and METADATA ZIP members are capped at
  1 MiB each and a compression ratio of 100 before decompression. Its single
  token-holding step uses the read-only org
  secret `PE_UK_PRIVATE_HF_READ_TOKEN` only to read the private release
  manifest, whose SHA-256 and dataset size enter the request. No dataset is
  downloaded during discovery.
  `expected_release_bundle` is computed statically from the packaged manifest;
  `RELEASE_REPLAY.md` cites the reviewed 6.4.1/6.5.0 wheel source and the exact
  W4 fixtures. The normal runtime bundle comparison remains mandatory.
* Public discovered requests and permanent skip evidence pass the receiver's
  output guard before upload and again in `discover_enqueue`. That separate
  job has `contents: write`, no dataset token, and runs only trusted control
  code. It validates every discovered request against the vendored request
  schema before enqueueing any, and refetches `replay-state` to deduplicate
  versions again on every write attempt. This covers a W4 request that
  arrived before that attempt. A later dispatch can still create a distinct
  request after discovery has pushed; the six-hour grace period reduces that
  overlap. Immutable artifact contradictions can be
  recorded with their digest evidence as permanent skips; transient failures
  are retried on later drains.
* State for request `<request_id>` lives at
  `replay-state:requests/<request_id>/`:
  `REQUEST.json` (the received request re-serialised as sorted, indented JSON;
  `request_id` remains the JCS digest of the received request), `STATUS.json`
  (`queued` → `running` → `complete` | `rejected` | `failed`, with a
  history of timestamps and Actions run URLs), and on completion
  `REPLAY_RECEIPT.json`. The receipt is committed first; a terminal
  `STATUS.json` is written in a later commit and names `receipt_sha256` and
  `receipt_commit`, so one contents read binds the status to the receipt
  bytes.
* Dataset fetching and candidate execution are separate steps of the run
  job, which has `contents: read` and no persisted checkout credential. The
  fetch step runs first, before any candidate code is installed, and is the
  only step in that job holding the read-only dataset token (the organisation
  secret `PE_UK_PRIVATE_HF_READ_TOKEN`, only in `workflow_dispatch` and
  `repository_dispatch` runs). It verifies the file, which then goes to
  `run-request` as `--dataset-file`. Candidate code runs as an unprivileged
  account with no sudo, its own copy of the repository and inputs, and an
  empty starting environment. Scorecard is public: the dataset never leaves
  the runner, no job uses a cache, the control job hands over only the
  request, and the run's output must pass an allowlist (parsable `.json`,
  `.jsonl`, `.csv`, `.md` and `.txt` files under size caps) before it is
  uploaded and again before it is committed. RELEASE_REPLAY.md states what
  this protects and what it does not; in particular, a receipt is produced
  beside the candidate, so requests are for PolicyEngine's own releases
  only. Automatic discovery additionally requires the exact trusted-publisher
  provenance above; a PyPI upload alone does not authorize it. The qualifier
  writes a structured result
  file with `status` and `receipt_sha256`, while logs remain visible in
  Actions. A separate recording job has `contents: write` and `actions: write`,
  validates the uploaded receipt, records it before terminal status and
  dispatches another drain run while requests remain pending.
  `workflow_dispatch` can trigger a run using `GITHUB_TOKEN`.
  ([GitHub workflow-trigger documentation](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow))
* W4 polls `GET /repos/PolicyEngine/policyengine-scorecard/contents/requests/<request_id>/STATUS.json?ref=replay-state`
  (the repository is public). A receipt is addressed by the request's own
  digest, so W4 needs no callback and no scorecard token.
* Duplicate requests (same `request_id`) are idempotent: an existing
  terminal status is returned, never rerun. A failed request can be retried
  only by a new request (a different `attempt`).
* A running request becomes stale after 7 hours. The receiver permits at
  most three `running` entries in its history; the next stale attempt records
  a minimal `failed` receipt with `attempt_limit_exceeded`, followed by a
  terminal status naming that receipt and its pushed commit.

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

* `request_id` is not a field: it is the SHA-256 of the received request's
  JCS bytes, independent of the formatting used to store `REQUEST.json`.
  Both sides test against the golden fixture.
* `requested_by` names the requesting repository and commit;
  `workflow_run_id` is optional (a manual request made outside Actions has
  none), and additional provenance fields such as `run_attempt`
  are accepted. Discovery uses this existing extension point for
  `pypi_provenance_sha256`, the SHA-256 of the wheel's PyPI provenance response,
  without changing the vendored schema. It is included in the request's JCS
  digest and public discovery metadata. Permanent skip metadata uses
  `evidence_sha256.policyengine_provenance`. Every other object is closed.
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
| `artifact_hash_mismatch` | A requested wheel is missing from PyPI, or a downloaded wheel, the installed packaged manifest or the dataset bytes differ from the request. |
| `release_bundle_mismatch` | `pe.uk.uk_latest.release_bundle` under packaged certification differs from `expected_release_bundle`. |
| `incompatible_pair` | The packaged certification does not name the candidate model version, or the dataset is not the bundle's certified artifact. |
| `data_access_failed` | The dataset could not be fetched with the receiver's credential. |
| `no_supported_years` | No event year falls in the dataset's supported years. |

A rejected request has no numerical results; its receipt says why.
`variant_id`, `variant_identity_sha256`, `execution`, `corpus` and `diff`
are null, and `integrity.status` is `not_run`, even if a record was known
before the rejection.

Every corpus replay runs in a fresh detached checkout of the same commit
under its work directory. The candidate's copied namespace and diff are
removed before running, no committed results are resumed, and the runner
checkout supplies the read-only diff base. With `latest_certified`, an exact
certified pair is compared with its own committed namespace, which also
checks determinism. Sealing happens in the fresh checkout, and the request's
previous `results/` directory is replaced before copying the sealed output.
`INSTALL.json` records whether installation used exact certified requirements,
certified constraints or a fallback to free resolution; the receipt binds
that file through the namespace manifest.

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
  "corpus_version": "uk-fiscal-event-replay/2",
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
    "inert_measure_years": [],
    "missing_measure_years": [],
    "unsupported_measure_years": []
   }
  }
 },
 "integrity": {
  "status": "complete",
  "failures": []
 },
 "diff": {
  "base_variant_id": "pe6.2.6_uk2.125.1_policyengine-uk-data-1.58.0",
  "base_events": {
   "autumn_budget_2024": {
    "staging_manifest_sha256": "…",
    "run_manifest_sha256": "…",
    "supported_years": [2024, 2025, 2026, 2027, 2028, 2029],
    "full_supported_grid_complete": true,
    "inert_measure_years": [],
    "missing_measure_years": [],
    "unsupported_measure_years": []
   }
  },
  "diff_sha256": "…",
  "flag_counts": {"numerical": 0, "structural": 0, "coverage": 0, "mapping": 0, "support": 0, "inertness": 0, "construction": 0},
  "flagged_rows": [ {"event": "…", "measure_key": "…", "year": 2026, "level": "head", "key": "income_tax", "flags": ["numerical"], "base_gbp": 0.0, "head_gbp": 0.0} ]
 },
 "results": {
  "repository": "PolicyEngine/policyengine-scorecard",
  "ref": "replay-state",
  "path": "requests/<request_id>/results/",
  "manifest_sha256": "<64-hex SHA-256 of NAMESPACE_MANIFEST.json>"
 },
 "receipt_sha256": "<64-hex of the canonical receipt without this field>"
}
```

`corpus_version` names the event set the run replayed.
`uk-fiscal-event-replay/1` is the five events from Spring Budget 2023 to
Spring Statement 2025; `uk-fiscal-event-replay/2` adds Autumn Budget 2025.
In a diff against a base replayed under an earlier version, an added event
has `present.base` false and its rows carry no base values.

A complete receipt requires `variant_identity_sha256` and
`results.manifest_sha256`. A failed receipt has `corpus: null` when no event
produced outputs. If receipt building, sealing or result copying crashes,
the receiver writes a minimal schema-valid failed receipt with
`receipt_step_failed` and the error's first line. Missing or invalid uploaded
run output is recorded as `run_artifact_failed`. The terminal status still
names the receipt digest and the commit that was pushed before it.

An in-force measure-year whose declared heads come out identical in the two
worlds is inert. If the run's `CONSTRUCTION_PREMISES.json` gives any
parameter different 1 January values in the two worlds that year, the
intended change did not show in the declared heads: the construction did not
reach the engine, it does not bind on this population, or it moves only
variables outside those heads. The receipt then
records an integrity failure `construction_inert` (with `event`,
`measure_key`, `year`, and the parameter and both worlds' values in
`detail`), and its status is `failed`. Equal premises values do not prove a
pair should be inert (a freeze can carry earlier years' rates forward), so
such a pair leaves the grid incomplete and is listed in
`inert_measure_years`. Whether either blocks promotion is W4's qualification
policy.

A world whose processed parameter value differs from its intended value
records an integrity failure `processed_value_mismatch` (with `event`,
`measure_key`, `year`, and `world`, `path`, `intended` and `processed` as
JSON in `detail`), and the status is `failed`. The one exception is a
mismatch in an announcement world (`baseline_world` or `reform_world`, never
`certified_current_law`) in a year before the measure commences, when the two
worlds come out identical; the measure-year's artifact lists it under
`processed_value_notes` instead.
`RELEASE_REPLAY.md` gives the rule.

### Division of judgement

How flags arise, so a gate built on them sees the intended events:

* A year unsupported on one side raises `support` on that year's rows, not
  `coverage`. A lost counterpart is `coverage` only where both sides support
  the year.
* `construction` means the executed reform dictionaries differ or a premise
  check changed its result. A change in the current-law value of a parameter
  the construction touches is recorded as context in the row's details, not
  as a flag, because it is what a model release is expected to change.
* For a candidate, the default base is the newest certified variant with
  committed results; an exact certified pair uses its own committed run.
  The first certified-variant run diffs against the legacy populace variant,
  where the data family itself changes.

* `integrity.status` is `complete`, `incomplete` or `failed`. `failed` means
  a crash, a non-finite aggregate, an identity mismatch after the run started,
  an accounting identity broken in staging, a `construction_inert`
  measure-year, or a `processed_value_mismatch`. These are structural failures; W4 blocks promotion on
  them.
* Each corpus event also carries staging's own `missing_measure_years`
  (pairs in the full event grid without an artifact, so including the
  unsupported ones) and `unsupported_measure_years` (pairs in years outside
  the variant's data years); a gap on the supported grid is a missing pair
  that is not unsupported. A legacy-layout candidate's staging records only
  `missing_measure_years`. Receipts issued before these fields were added
  lack them.
* `diff.base_events` is the base side's own record of each event's grid, in
  the same fields with the same meanings, beside the base's staging and run
  manifest digests. The release diff records it in `DIFF.json` (`base.grids`)
  while it verifies the base's staging, taking `supported_years` from the
  base's `RUN_MANIFEST.json` (staging does not record them); the receipt
  copies it from there, so `diff_sha256` binds it and nothing is re-read.
  This matters when a certified pair requalifies: its base and candidate
  share one result root. `inert_measure_years` is always present. An event
  has no entry when the base is a legacy-layout run or did not replay it, so
  a base gap is reported only from the base's own verified staging, never
  inferred.
  Whether a candidate gap matching a base gap blocks promotion is W4's
  policy.
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
   Hugging Face token variables and `NO_PROXY`/`no_proxy` removed, and the
   HTTP(S) proxy variables pointed at a closed local port, exactly as
   `uk_replay_variants.isolate_certification_environment` does. (Amended 11
   October and confirmed by W4 the same day, implemented in
   policyengine.py#574: removing the tokens alone forces the packaged
   certification only for a private data repository; policyengine.py fetches
   the release manifest with `requests`, which ignores `HF_HUB_OFFLINE`, so a
   public one would still answer.)
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
