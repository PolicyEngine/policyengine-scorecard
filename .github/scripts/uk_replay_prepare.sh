#!/usr/bin/env bash
# Select one request. Exhausted stale attempts receive a committed failure first.
set -euo pipefail
# shellcheck source=.github/scripts/uk_replay_state.sh
source .github/scripts/uk_replay_state.sh
if ! git ls-remote --exit-code --heads origin "$STATE_BRANCH" >/dev/null; then
  echo "queue empty: no state branch"
  echo "request_id=" >> "$GITHUB_OUTPUT"
  exit 0
fi
checkout_state
mkdir -p input
while :; do
  "${CONTROL[@]}" -m pipeline.uk_replay_queue pending --state "$STATE" --now "$(now)" > "$RUNNER_TEMP/pending.txt"
  IFS= read -r request_id < "$RUNNER_TEMP/pending.txt" || true
  if [ -z "$request_id" ]; then
    echo "queue empty"
    echo "request_id=" >> "$GITHUB_OUTPUT"
    exit 0
  fi
  attempts=$("${CONTROL[@]}" -m pipeline.uk_replay_queue attempts --state "$STATE" --request-id "$request_id")
  if [ "$attempts" -ge 3 ]; then
    receipt_sha256=$("${CONTROL[@]}" -m pipeline.uk_replay_queue failure-receipt \
      --state "$STATE" --request-id "$request_id" --code attempt_limit_exceeded \
      --detail "The request exhausted three running attempts without a terminal receipt")
    push_state "Receipt for $request_id: attempts exhausted"
    receipt_commit=$(git -C "$STATE" rev-parse HEAD)
    "${CONTROL[@]}" -m pipeline.uk_replay_queue set-status --state "$STATE" \
      --request-id "$request_id" --status failed --run-url "$RUN_URL" --now "$(now)" \
      --receipt-sha256 "$receipt_sha256" --receipt-commit "$receipt_commit"
    push_state "Status for $request_id: attempts exhausted"
    continue
  fi
  "${CONTROL[@]}" -m pipeline.uk_replay_queue set-status --state "$STATE" \
    --request-id "$request_id" --status running --run-url "$RUN_URL" --now "$(now)"
  push_state "Run $request_id"
  cp "$STATE/requests/$request_id/REQUEST.json" input/REQUEST.json
  echo "request_id=$request_id" >> "$GITHUB_OUTPUT"
  break
done
