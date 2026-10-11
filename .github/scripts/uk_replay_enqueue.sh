#!/usr/bin/env bash
# Enqueue each request file given as an argument on the replay-state branch
# (idempotent), then commit and push, rebasing over concurrent writers.
set -euo pipefail
CONTROL=(uv run --with rfc8785==0.1.4 --with jsonschema python)
now=$(date -u +%Y-%m-%dT%H:%M:%SZ)
for request in "$@"; do
  "${CONTROL[@]}" -m pipeline.uk_replay_queue enqueue --state state \
    --request "$request" --run-url "$RUN_URL" --now "$now"
done
git -C state add -A
if git -C state diff --cached --quiet; then
  echo "nothing new to queue"
  exit 0
fi
git -C state commit -qm "Queue $# request(s)"
for _ in 1 2 3 4 5; do
  if git -C state push -q origin "HEAD:$STATE_BRANCH"; then
    exit 0
  fi
  git -C state pull -q --rebase origin "$STATE_BRANCH"
done
echo "could not push the state branch after five attempts" >&2
exit 1
