#!/usr/bin/env bash
# Check out the replay-state branch at ./state (create it, orphaned, if it
# does not exist yet) for the UK replay workflow's jobs.
set -euo pipefail
if git ls-remote --exit-code --heads origin "$STATE_BRANCH" >/dev/null; then
  git fetch -q origin "$STATE_BRANCH"
  git worktree add -q state "origin/$STATE_BRANCH"
  git -C state switch -q -C "$STATE_BRANCH"
else
  git worktree add -q --orphan -b "$STATE_BRANCH" state
fi
git -C state config user.name "github-actions[bot]"
git -C state config user.email "41898282+github-actions[bot]@users.noreply.github.com"
