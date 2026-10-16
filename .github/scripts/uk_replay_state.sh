#!/usr/bin/env bash
# Shared state-branch operations. Source from the control scripts only.
set -euo pipefail

STATE=${STATE:-state}
# Used by the scripts that source this file.
# shellcheck disable=SC2034
CONTROL=(uv run --with rfc8785==0.1.4 --with jsonschema python)

now() { date -u +%Y-%m-%dT%H:%M:%SZ; }

checkout_state() {
  if git ls-remote --exit-code --heads origin "$STATE_BRANCH" >/dev/null; then
    git fetch -q origin "$STATE_BRANCH"
    git worktree add -q "$STATE" "origin/$STATE_BRANCH"
    git -C "$STATE" switch -q -C "$STATE_BRANCH"
  else
    git worktree add -q --orphan -b "$STATE_BRANCH" "$STATE"
  fi
  git -C "$STATE" config user.name "github-actions[bot]"
  git -C "$STATE" config user.email "41898282+github-actions[bot]@users.noreply.github.com"
}

push_state() {
  git -C "$STATE" add -A
  if ! git -C "$STATE" diff --cached --quiet; then
    git -C "$STATE" commit -qm "$1"
  fi
  for attempt in 1 2 3 4 5; do
    if git -C "$STATE" push -q origin "HEAD:$STATE_BRANCH"; then
      return 0
    fi
    if ! git -C "$STATE" pull -q --rebase origin "$STATE_BRANCH"; then
      git -C "$STATE" rebase --abort
      echo "state rebase conflicted; refusing to publish conflicting results" >&2
      return 1
    fi
    sleep "$attempt"
  done
  echo "could not push the state branch after five attempts" >&2
  return 1
}
