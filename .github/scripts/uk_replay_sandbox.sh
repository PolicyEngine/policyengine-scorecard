#!/usr/bin/env bash
# Candidate code runs as an unprivileged account, never as the runner user.
#
# The runner user has passwordless sudo, owns this job's workspace and its
# command files ($GITHUB_ENV, $GITHUB_PATH), and owns the runner processes
# that hold the job's secrets and the Actions runtime token. The candidate
# account has none of these: no sudoers entry, a private copy of the
# repository and the verified request inputs, an environment built from
# nothing (env -i), and no read access to another user's process memory or
# environment. Nothing it starts survives `collect`, and only a copy of its
# output/ comes back, to be checked by the runner's own guard.
#
#   uk_replay_sandbox.sh setup     # after the dataset fetch, before any candidate code
#   uk_replay_sandbox.sh run       # the drain, as the candidate account
#   uk_replay_sandbox.sh collect   # kill its processes, copy output/ back
set -euo pipefail
CANDIDATE=replay-candidate
CANDIDATE_HOME=/home/$CANDIDATE
COPY=$CANDIDATE_HOME/scorecard

case "${1:?usage: uk_replay_sandbox.sh setup|run|collect}" in
  setup)
    sudo useradd --create-home --shell /bin/bash "$CANDIDATE"
    if ! sudo -l -U "$CANDIDATE" | grep -q "not allowed to run sudo"; then
      echo "::error::$CANDIDATE can use sudo"
      exit 1
    fi
    sudo chmod 700 "$CANDIDATE_HOME"
    # Its own uv, whatever the permissions of the runner's tool cache.
    sudo install -d -o "$CANDIDATE" -g "$CANDIDATE" "$CANDIDATE_HOME/bin"
    sudo install -o "$CANDIDATE" -g "$CANDIDATE" -m 0755 "$(command -v uv)" "$CANDIDATE_HOME/bin/uv"
    # The repository with its history (the corpus runs in a worktree of
    # HEAD) and input/: the request, the verified dataset, the fetch result.
    sudo cp -a "$GITHUB_WORKSPACE/." "$COPY"
    sudo rm -rf "$COPY/output"
    sudo chown -R "$CANDIDATE:$CANDIDATE" "$COPY"
    ;;
  run)
    status=0
    sudo -n -u "$CANDIDATE" env -i \
      HOME="$CANDIDATE_HOME" USER="$CANDIDATE" LANG=C.UTF-8 \
      PATH="$CANDIDATE_HOME/bin:/usr/local/bin:/usr/bin:/bin" \
      PYTHONPATH=. RUNNER_TEMP="$CANDIDATE_HOME/tmp" \
      REQUEST_ID="${REQUEST_ID:?}" REPLAY_RUNNER="${REPLAY_RUNNER:?}" \
      bash -c 'mkdir -p "$RUNNER_TEMP" && cd "$HOME/scorecard" && exec bash .github/scripts/uk_replay_drain.sh' \
      || status=$?
    # The drain records its own exit; the recorder handles a missing outcome.
    echo "candidate drain exited $status"
    ;;
  collect)
    # Nothing the candidate started outlives this step.
    sudo pkill -KILL -u "$CANDIDATE" || true
    for _ in $(seq 30); do
      pgrep -u "$CANDIDATE" > /dev/null || break
      sleep 1
    done
    if pgrep -u "$CANDIDATE" > /dev/null; then
      echo "::error::$CANDIDATE processes survive"
      exit 1
    fi
    rm -rf output
    if sudo test -d "$COPY/output"; then
      # -R copies links as links and special files as special files, which
      # the guard then refuses; --no-preserve drops the candidate's modes.
      sudo cp -R --no-preserve=all "$COPY/output" output
      sudo chown -R "$(id -u):$(id -g)" output
    fi
    ;;
  *)
    echo "usage: uk_replay_sandbox.sh setup|run|collect" >&2
    exit 2
    ;;
esac
