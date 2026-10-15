#!/usr/bin/env bash
# Enqueue each request file given as an argument on the replay-state branch
# (idempotent), then commit and push, rebasing over concurrent writers.
set -euo pipefail
# shellcheck source=.github/scripts/uk_replay_state.sh
source "$(dirname "${BASH_SOURCE[0]}")/uk_replay_state.sh"
CONTROL=(uv run --with rfc8785==0.1.4 --with jsonschema python)
now=$(date -u +%Y-%m-%dT%H:%M:%SZ)
for request in "$@"; do
  "${CONTROL[@]}" -m pipeline.uk_replay_queue enqueue --state state \
    --request "$request" --run-url "$RUN_URL" --now "$now"
done
push_replay_state state "Queue $# request(s)"
