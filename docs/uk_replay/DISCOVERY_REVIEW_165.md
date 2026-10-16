# Discovery security review #165

Review response for the rebuilt discovery merged with main at `b7791b471749`.
The certified floor on this base is
`pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1`.

## Changes and tests

Implementation locations below are repository-relative `file:line` references.
Test names are in `tests/test_uk_replay_discover.py` unless prefixed with
`workflow:` (`tests/test_uk_replay_discovery_workflow.py`) or
`scripts:` (`tests/test_uk_replay_discovery_scripts.py`).

| Item | Change / implementation | Test pin |
| --- | --- | --- |
| B1: publisher gate | `pipeline/uk_replay_discover.py:112` reads static provenance and requires exact case-sensitive publisher fields; `:342` checks before wheel reading or request construction. Missing/wrong/unreadable complete provenance is a permanent skip; transient HTTP failures retry. | `test_a_release_becomes_a_valid_released_bundle_request`; `test_wrong_publisher_is_permanently_refused_before_bundle_building`; `test_missing_or_unreadable_provenance_has_response_digest`; `test_missing_provenance_http_response_is_permanent_evidence`; `test_transient_provenance_failure_is_retried_instead_of_recorded` |
| B1: evidence | `pipeline/uk_replay_discover.py:343` records `requested_by.pypi_provenance_sha256`; `:131` logs it; `:151` records permanent-skip evidence as `policyengine_provenance`. | `test_a_release_becomes_a_valid_released_bundle_request`; `test_missing_or_unreadable_provenance_has_response_digest` |
| B1: documentation | `docs/uk_replay/RELEASE_REPLAY.md:554`, `:569`, `:660`; `docs/uk_replay/QUALIFICATION_INTERFACE.md:68`, `:188` specify the trust boundary and digest location. | Same provenance behavior tests; documentation diff reviewed. |
| B2: schema | `.github/scripts/uk_replay_discovery_guard.py:57` retains full vendored schema validation before any write. A digest-named request with PyPI source/version but extra field or `data.repo_id: "a/../b"` is refused without push. | workflow: `test_enqueue_schema_validation_refuses_a_digest_named_complete_request` |
| B2: any status | `pipeline/uk_replay_discover.py:173`; `.github/scripts/uk_replay_discovery_guard.py:85` count `queued`, `running`, `complete`, `failed`, `rejected`. | `test_existing_qualification_in_any_status_sets_the_floor`; workflow: `test_enqueue_does_not_duplicate_a_release_already_in_the_queue` |
| B2: upload gate | `.github/workflows/uk-replay.yml:127` names the output guard `guard`; `:130` requires its success before upload. | workflow: `test_discovery_holds_the_token_only_in_an_empty_manual_drain` |
| 1: grace | `pipeline/uk_replay_discover.py:57`, `:340` require wheel age at least six hours; tested logic receives explicit `now`; only CLI reads the clock (`:559`). | `test_wheel_upload_grace_period_boundary` |
| 2: floor | `pipeline/uk_replay_discover.py:236` uses the maximum certified/requested version, including terminal requests. Superseded 6.4.2/6.4.3 are not backfilled after requested or certified 6.5.0. Old 6.4.1-floor fixtures now use the 6.5.0 base. | `test_candidates_are_sorted_strictly_above_the_floor`; `test_existing_qualification_in_any_status_sets_the_floor`; `test_642_and_643_are_not_backfilled_after_650` |
| 3: timeout | `.github/workflows/uk-replay.yml:142` sets `discover_enqueue` to ten minutes. | workflow: `test_discovery_and_enqueue_are_separate_and_failure_cannot_block_the_drain` |
| 4: size caps | `pipeline/uk_replay_discover.py:84`, `:269`, `:291`, `:325` bound streaming wheel/PyPI JSON reads to 64 MiB/1 MiB, local data-manifest reads to 1 MiB, and manifest/METADATA ZIP members to 1 MiB and compression ratio 100 before decompression; wheel hashing streams. | `test_response_caps_stop_reading_after_limit`; `test_wheel_entries_are_checked_before_decompression`; `test_large_artifact_refusal_does_not_stop_the_drain` |
| 5: dependencies | `.github/scripts/uk_replay_discover.sh:28` and `uk_replay_discover_enqueue.sh:10` deliberately retain existing unpinned `jsonschema`/`packaging`, per the agreed scope. | workflow: `test_token_and_write_jobs_never_install_or_execute_a_release`; no dependency pinning change. |
| 6: symlinks | `.github/scripts/uk_replay_discover.sh:21`, `:36` skip links in both copy loops. | scripts: `test_snapshot_and_handoff_skip_symlinks` |
| 7: defaults | `pipeline/uk_replay_discover.py:313` cites the inspected 6.5.0 wheel's `policyengine/provenance/manifest.py:30–31`; omitted `repo_type`/`release_manifest_path` default to `model`/`release_manifest.json`. Wheel was read with `zipfile`, never installed/imported. | `test_release_manifest_runtime_defaults_and_bounded_read` |
| 8: logging | `pipeline/uk_replay_discover.py:492`, `:508`, `:529` use `repr(exc)` via `!r`, escaping embedded newlines before workflow-command markers. | `test_discovery_logs_untrusted_exception_text_on_one_line` |
| 9: skip schema | `.github/scripts/uk_replay_discovery_guard.py:29` caps reason at 2,000 characters; `pipeline/uk_replay_discover.py:518` truncates produced reasons to match. | workflow: `test_enqueue_rejects_invalid_skip_metadata_before_any_request_write[long_reason]`; `test_permanent_skip_reason_stays_within_public_schema_limit` |
| 10: mutant tests | Existing filename/digest (`.github/scripts/uk_replay_discovery_guard.py:63`), 3-request/30-skip (`:80`), prerelease (`:75`, `pipeline/uk_replay_discover.py:246`), skip filename (`:72`), transient skip (`pipeline/uk_replay_discover.py:509`) and wheel digest (`:299`) checks now have direct regression cases. | workflow: `test_enqueue_refuses_metadata_with_the_wrong_filename`, `test_enqueue_refuses_batches_above_each_per_run_bound`, `test_enqueue_refuses_a_prerelease_above_the_certified_floor`; `test_prerelease_above_current_floor_is_not_discovered`; `test_transient_skip_with_evidence_is_never_persisted`; `test_fetch_streams_and_checks_the_actual_wheel_digest`; `test_default_three_request_and_thirty_attempt_bounds` |

The vendored request schema is unchanged. Its existing
[`requested_by.additionalProperties: true`](schemas/qualification_request.v1.json)
extension point carries the provenance digest in the public request and its JCS
identity, rather than adding a field to closed source/candidate objects.
Optional pinning of dataset/release-manifest repositories was not added; the
mandatory exact publisher gate is the release-origin check requested here.
A response stopped at its size cap remains retryable: no complete-response
SHA-256 exists to justify a permanent skip. The Hugging Face downloader remains
unchanged; its downloaded manifest is capped when read locally.

## Live read-only evidence

Read on 16 October 2026:
[6.5.0 wheel provenance](https://pypi.org/integrity/policyengine/6.5.0/policyengine-6.5.0-py3-none-any.whl/provenance),
abridged to the publisher fields actually checked:

```json
{
  "version": 1,
  "attestation_bundles": [{
    "publisher": {
      "environment": "pypi",
      "kind": "GitHub",
      "repository": "PolicyEngine/policyengine.py",
      "workflow": "push.yaml"
    }
  }]
}
```

SHA-256 of the raw, unabridged response:
`292fe22daee197510ffb42ea7e60f9e4fccbde062299726e2cfbdcde0e05d37a`.
The wheel matched the SHA-256 in the
[6.5.0 release JSON](https://pypi.org/pypi/policyengine/6.5.0/json):
`312a04f7ceb7058aa803d012ed836a8fdd0ed4885dea46112f5c205a42193856`.
Reading that wheel with `zipfile` showed manifest/METADATA sizes 14,712/52,820
bytes and compression ratios 4.68/3.13, within the new bounds. The
[whole-package JSON](https://pypi.org/pypi/policyengine/json) was 286,049 bytes,
within the 1 MiB JSON cap. No downloaded release code was installed or imported.

## Validation

Initial guard/workflow/script baseline: **37 passed in 151.98s**, after the
repository conftest built its derived database. The saved live 6.5.0 provenance
and verified wheel also passed the new control-code provenance/ZIP readers
offline, without installing or importing release code.

The required targeted command uses the shared venv, workspace-local `TMPDIR`,
no bytecode/cache provider and at most four workers:

```sh
mkdir -p .task-tmp/pytest
PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 TMPDIR="$PWD/.task-tmp/pytest" \
  /Users/maxghenis/PolicyEngine/policyengine-scorecard/.claude/worktrees/suspicious-wright-b02e85/.venv-tests/bin/python \
  -m pytest -q -n 4 -p no:cacheprovider \
  tests/test_uk_replay_discover.py tests/test_uk_replay_discovery_workflow.py \
  tests/test_uk_replay_discovery_scripts.py tests/test_uk_replay_queue.py \
  tests/test_uk_replay_qualify.py tests/test_ci_gates.py
UV_CACHE_DIR="$PWD/.task-tmp/uv-cache" UV_TOOL_DIR="$PWD/.task-tmp/uv-tools" \
  UV_TOOL_BIN_DIR="$PWD/.task-tmp/uv-bin" TMPDIR="$PWD/.task-tmp" \
  uvx ruff format --check be nz scorecard_db tests pipeline
shellcheck -x .github/scripts/uk_replay_discover*.sh
actionlint .github/workflows/uk-replay.yml
```

| Check | Result |
| --- | --- |
| Required six-file targeted suite | **227 passed in 180.04s** |
| Ruff format check | **192 files already formatted** |
| ShellCheck | **Passed** |
| Actionlint | **Passed** |
| Temporary-directory cleanup | **All test TMPDIRs and task scratch removed** |
| Incremental bundle verification | **Passed; final bundle includes the report commit** |

## Mutation checks

**39 mutations run: 38 killed, one equivalent survivor.** Each ran alone with
the shared venv, four workers and a focused regression selector. Sources were
restored in `finally`; all eight source/test files match their passing-baseline
SHA-256 values afterward. No unexplained survivor or invalid mutation remains.

| Mutation | Result |
| --- | --- |
| `guard-schema-validation`: Guard schema validation replaced with JCS digest only | Killed |
| `guard-terminal-dedupe`: Guard counts only queued/running requests | Killed |
| `guard-request-filename`: Guard request filename/digest check removed | Killed |
| `guard-skip-filename`: Guard skip filename/version check removed | Killed |
| `guard-request-cap`: Guard three-request bound removed | Killed |
| `guard-skip-cap`: Guard thirty-skip bound removed | Killed |
| `guard-prerelease`: Guard prerelease/development release check removed | Killed |
| `guard-skip-reason-cap`: Skip reason maxLength removed | Killed |
| `upload-always`: Upload uses always() and metadata alone | Killed |
| `enqueue-timeout`: Enqueue timeout removed | Killed |
| `snapshot-symlink`: Snapshot copy follows symlinks | Killed |
| `handoff-symlink`: Metadata handoff copy follows symlinks | Killed |
| `discover-terminal-dedupe`: Discovery counts only queued/running requests | Killed |
| `discover-requested-floor`: Requested versions omitted from discovery floor | Killed |
| `discover-prerelease`: Discovery prerelease filter removed | Killed |
| `discover-transient-evidence-permanent`: Evidence-bearing transient skip persisted permanently | Killed |
| `discover-wheel-digest`: Wheel SHA-256 comparison removed from real fetch | Killed |
| `discover-publisher-check`: Exact publisher comparison bypassed | Killed |
| `discover-missing-attestation`: Nonempty attestation requirement removed | Killed |
| `discover-provenance-gate-removed`: Pre-build provenance call bypassed with zero digest | Killed |
| `discover-publisher-kind`: Trusted kind GitHub changed to GitLab | Killed |
| `discover-publisher-repository`: Trusted repository PolicyEngine changed to Policyengine | Killed |
| `discover-publisher-workflow`: Trusted workflow push.yaml changed to push.yml | Killed |
| `discover-publisher-environment`: Trusted environment pypi changed to release | Killed |
| `discover-provenance-digest-omitted`: Provenance digest omitted from requested_by | Killed |
| `discover-transient-http-permanent`: Transient provenance HTTP failures made permanent | Killed |
| `discover-missing-provenance-retry`: Missing provenance HTTP response made retryable | Killed |
| `discover-grace-off`: Six-hour grace check removed | Killed |
| `discover-grace-exclusive`: Exactly six-hour-old release refused (less-than changed to less-or-equal) | Killed |
| `discover-response-cap`: Stream overflow refusal removed | Killed |
| `discover-zip-size`: ZIP uncompressed size check removed | Killed |
| `discover-zip-ratio`: ZIP compression ratio check effectively removed | Killed |
| `discover-log-command`: Exception logging uses str instead of repr | Killed |
| `discover-request-cap`: Discovery request bound removed | Killed |
| `discover-attempt-cap`: Discovery attempt bound removed | Killed |
| `discover-reason-cap`: Generated permanent-skip reason truncation removed | Killed |
| `discover-manifest-default`: release_manifest_path default removed | Killed |
| `discover-repo-type-default`: repo_type default removed | Killed |
| `equivalent-floor-inclusive`: Discovery floor comparison changed from > to >= | Equivalent |

The `>=` survivor is equivalent: `floor` is itself a member of the union of
certified and requested versions, and that same union is already included in
`seen`. Equality is therefore rejected by `version not in seen` under either
comparison, including normalized version aliases. Its focused floor/status
tests all pass (13 tests with this mutation); the invariant is unchanged.

## Verification limits

Private release-manifest access and token-scoped behavior were not exercised
against live services; tests replace network responses and private inputs.
Hosted Actions execution, hosted-runner sandbox behavior and actual remote
queue writes were not exercised. Workflow assertions and local-git integration
tests cover the edited boundary; they do not substitute for a hosted run.
All pytest runs used the one shared venv and at most four workers; the whole
suite was not run.

## Commits and handoff

- `d1ca568`: metadata handoff, write guard and workflow regression cases.
- `9d6f31f`: trusted-publisher provenance, bounded discovery and receiver docs.

Shared Git metadata denied ref writes. Commits are on `w6/replay-discovery` in
workspace-local `.git-discovery`. The incremental bundle
`w6-discovery-fix-165.bundle` requires base `b7791b471749`; verify it with
`git bundle verify w6-discovery-fix-165.bundle`. Only workspace-local test
remotes were used.
