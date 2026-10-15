#!/usr/bin/env bash
# Check out the replay-state branch at ./state (create it, orphaned, if it
# does not exist yet) for the UK replay workflow's jobs.
set -euo pipefail

# Checkout never persists credentials. Keep authentication in this shell,
# unexported, and expose it only to individual Git operations. In particular,
# the qualification subprocess and the release code it runs cannot inherit it.
REPLAY_PUSH_AUTH=""
if [ -n "${PUSH_TOKEN:-}" ]; then
  REPLAY_PUSH_AUTH=$(printf 'x-access-token:%s' "$PUSH_TOKEN" | base64 | tr -d '\n')
fi
export -n REPLAY_PUSH_AUTH
unset PUSH_TOKEN GITHUB_TOKEN

replay_git() {
  if [ -n "$REPLAY_PUSH_AUTH" ]; then
    GIT_CONFIG_COUNT=1 \
      GIT_CONFIG_KEY_0=http.https://github.com/.extraheader \
      GIT_CONFIG_VALUE_0="AUTHORIZATION: basic $REPLAY_PUSH_AUTH" git "$@"
  else
    git "$@"
  fi
}

push_replay_state() {
  local state=$1 message=$2 local_commit remote_commit
  git -C "$state" add -A
  if ! git -C "$state" diff --cached --quiet; then
    git -C "$state" commit -qm "$message"
  fi
  if ! git -C "$state" rev-parse --verify HEAD >/dev/null 2>&1; then
    echo "no state commits to push"
    return 0
  fi
  # Even if nothing changed, verify that HEAD is on the remote before callers
  # use its digest as the receipt commit (a retry may already have the files).
  for _ in 1 2 3 4 5; do
    local_commit=$(git -C "$state" rev-parse HEAD)
    if replay_git -C "$state" push -q origin "HEAD:$STATE_BRANCH"; then
      remote_commit=$(replay_git -C "$state" ls-remote --exit-code --heads origin \
        "refs/heads/$STATE_BRANCH" | awk 'NR == 1 {print $1}') || return 1
      if [ "$remote_commit" = "$local_commit" ]; then
        # shellcheck disable=SC2034 # Consumed by the script sourcing this helper.
        REPLAY_STATE_COMMIT=$local_commit
        return 0
      fi
      echo "the remote state branch differs from the pushed commit; retrying" >&2
    fi
    if ! replay_git -C "$state" pull -q --rebase origin "$STATE_BRANCH"; then
      # A conflicted rebase leaves HEAD at an intermediate commit. Never push
      # that commit or let a receipt name it; restore the pre-rebase state.
      if ! git -C "$state" rebase --abort; then
        echo "could not abort the failed state-branch rebase" >&2
      fi
      echo "could not rebase the state branch; push stopped" >&2
      return 1
    fi
  done
  echo "could not push and verify the state branch after five attempts" >&2
  return 1
}

if [[ "${BASH_SOURCE[0]}" = "$0" ]]; then
  if replay_git ls-remote --exit-code --heads origin "$STATE_BRANCH" >/dev/null; then
    replay_git fetch -q origin "$STATE_BRANCH"
    git worktree add -q state "origin/$STATE_BRANCH"
    git -C state switch -q -C "$STATE_BRANCH"
  else
    git worktree add -q --orphan -b "$STATE_BRANCH" state
  fi
  git -C state config user.name "github-actions[bot]"
  git -C state config user.email "41898282+github-actions[bot]@users.noreply.github.com"
fi
