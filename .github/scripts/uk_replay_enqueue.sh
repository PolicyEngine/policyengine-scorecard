#!/usr/bin/env bash
# Concurrent enqueues reapply the idempotent operation after a rebase conflict.
set -euo pipefail
# shellcheck source=.github/scripts/uk_replay_state.sh
source .github/scripts/uk_replay_state.sh
checkout_state

for attempt in 1 2 3 4 5; do
  "${CONTROL[@]}" -m pipeline.uk_replay_queue enqueue --state "$STATE" \
    --request "$REQUEST_FILE" --run-url "$RUN_URL" --now "$(now)" \
    | tee "$RUNNER_TEMP/enqueued.txt"
  git -C "$STATE" add -A
  if ! git -C "$STATE" diff --cached --quiet; then
    git -C "$STATE" commit -qm "Queue $(cut -d' ' -f1 "$RUNNER_TEMP/enqueued.txt")"
  fi
  if git -C "$STATE" push -q origin "HEAD:$STATE_BRANCH"; then
    exit 0
  fi
  if ! git -C "$STATE" pull -q --rebase origin "$STATE_BRANCH"; then
    git -C "$STATE" rebase --abort
    git -C "$STATE" fetch -q origin "$STATE_BRANCH"
    git -C "$STATE" reset --hard "origin/$STATE_BRANCH"
    git -C "$STATE" clean -fd
    echo "enqueue conflicted; reapplying the request to the current state branch"
  fi
  sleep "$attempt"
done
echo "could not enqueue and push the request after five attempts" >&2
exit 1
