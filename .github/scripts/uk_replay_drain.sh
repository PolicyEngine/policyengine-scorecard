#!/usr/bin/env bash
# Drain the UK replay qualification queue (see .github/workflows/uk-replay.yml).
#
# For each pending request, oldest first: mark it running, run it end to end
# (pipeline/uk_replay_qualify.py run-request), commit the receipt and results
# to the state branch, then write the terminal STATUS.json naming the
# receipt's digest and that commit. Stops when the queue is empty or the time
# budget is spent; the next scheduled run continues.
set -euo pipefail
# shellcheck source=.github/scripts/uk_replay_state.sh
source "$(dirname "${BASH_SOURCE[0]}")/uk_replay_state.sh"

STATE=state
CONTROL=(uv run --with rfc8785==0.1.4 --with jsonschema --with huggingface_hub python)
BUDGET_SECONDS=$((300 * 60))
started=$(date +%s)

now() { date -u +%Y-%m-%dT%H:%M:%SZ; }

push_state() {
  push_replay_state "$STATE" "$1"
}

while :; do
  if replay_git ls-remote --exit-code --heads origin "$STATE_BRANCH" >/dev/null; then
    if ! replay_git -C "$STATE" pull -q --rebase origin "$STATE_BRANCH"; then
      git -C "$STATE" rebase --abort
      exit 1
    fi
  fi
  request_id=$("${CONTROL[@]}" -m pipeline.uk_replay_queue pending --state "$STATE" --now "$(now)" | head -n 1)
  if [ -z "$request_id" ]; then
    echo "queue empty"
    break
  fi
  if [ $(( $(date +%s) - started )) -gt "$BUDGET_SECONDS" ]; then
    echo "time budget spent; the next scheduled run continues"
    break
  fi
  echo "::group::request $request_id"
  "${CONTROL[@]}" -m pipeline.uk_replay_queue set-status --state "$STATE" \
    --request-id "$request_id" --status running --run-url "$RUN_URL" --now "$(now)"
  push_state "Run $request_id"

  work="$RUNNER_TEMP/requests/$request_id"
  outcome=$("${CONTROL[@]}" -m pipeline.uk_replay_qualify run-request \
    --request "$STATE/requests/$request_id/REQUEST.json" \
    --state-dir "$STATE" --work "$work" --runner "$REPLAY_RUNNER" | tail -n 1)
  status=${outcome%% *}
  receipt_sha256=${outcome##* }
  push_state "Receipt for $request_id: $status"
  receipt_commit=$REPLAY_STATE_COMMIT

  "${CONTROL[@]}" -m pipeline.uk_replay_queue set-status --state "$STATE" \
    --request-id "$request_id" --status "$status" --run-url "$RUN_URL" --now "$(now)" \
    --receipt-sha256 "$receipt_sha256" --receipt-commit "$receipt_commit"
  push_state "Status for $request_id: $status"
  rm -rf "$work"
  echo "::endgroup::"
done
