#!/usr/bin/env bash
# The write job runs trusted control code only, and validates the entire
# public metadata artifact before touching replay-state. Discovery failure
# never prevents the workflow's prepare job from draining existing requests.
set -euo pipefail
# shellcheck source=.github/scripts/uk_replay_state.sh
source .github/scripts/uk_replay_state.sh
DISCOVERY_DIR=${DISCOVERY_DIR:-discovery}
CONTROL=(uv run --with rfc8785==0.1.4 --with jsonschema --with packaging python)
python3 -I .github/scripts/uk_replay_output_guard.py "$DISCOVERY_DIR"
"${CONTROL[@]}" .github/scripts/uk_replay_discovery_guard.py validate "$DISCOVERY_DIR"
checkout_state

for attempt in 1 2 3 4 5; do
  # Recheck against the latest queue on each retry, including requests that
  # arrived from W4 after the discovery snapshot, irrespective of status.
  "${CONTROL[@]}" .github/scripts/uk_replay_discovery_guard.py enqueue \
    "$DISCOVERY_DIR" --state "$STATE" --run-url "$RUN_URL" --now "$(now)"
  git -C "$STATE" add -A
  if ! git -C "$STATE" diff --cached --quiet; then
    git -C "$STATE" commit -qm 'Queue discovered policyengine releases'
  fi
  if git -C "$STATE" push -q origin "HEAD:$STATE_BRANCH"; then
    exit 0
  fi
  # Always replay against the current branch, even when a rebase could
  # succeed: two different requests can name the same wrapper version.
  git -C "$STATE" fetch -q origin "$STATE_BRANCH"
  git -C "$STATE" reset --hard "origin/$STATE_BRANCH"
  git -C "$STATE" clean -fd
  echo 'discovery enqueue raced; rechecking the current state branch'
  sleep "$attempt"
done
echo 'could not enqueue discovered requests after five attempts' >&2
exit 1
