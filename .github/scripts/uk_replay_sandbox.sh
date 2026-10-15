#!/usr/bin/env bash
# Candidate code runs as an unprivileged account, never as the runner user.
#
# The runner user has passwordless sudo, owns this job's workspace and its
# command files ($GITHUB_ENV, $GITHUB_PATH), and owns the runner processes
# that hold the job's secrets and the Actions runtime token. The candidate
# account has no sudoers entry, no supplementary groups (so no docker
# socket), no cron or at jobs, a private copy of the repository and the
# verified request inputs, and an environment built from nothing (env -i).
# It cannot write the runner user's files or read another user's process
# memory or environment; `setup` checks the first of these as the account
# itself and fails the job otherwise. Its processes are killed in `collect`,
# and only a copy of its output/, streamed out by the account itself, comes
# back, to be checked by the runner's own guard.
#
#   uk_replay_sandbox.sh setup     # after the dataset fetch, before any candidate code
#   uk_replay_sandbox.sh run       # the drain, as the candidate account
#   uk_replay_sandbox.sh collect   # kill its processes, copy output/ back
set -euo pipefail
CANDIDATE=replay-candidate
CANDIDATE_HOME=/home/$CANDIDATE
COPY=$CANDIDATE_HOME/scorecard

as_candidate() {
  sudo -n -u "$CANDIDATE" env -i HOME="$CANDIDATE_HOME" PATH=/usr/bin:/bin "$@"
}

case "${1:?usage: uk_replay_sandbox.sh setup|run|collect}" in
  setup)
    sudo useradd --create-home --shell /bin/bash "$CANDIDATE"
    # No scheduled jobs that could outlive `collect`.
    for deny in /etc/cron.deny /etc/at.deny; do
      echo "$CANDIDATE" | sudo tee -a "$deny" > /dev/null
    done
    sudo chmod 700 "$CANDIDATE_HOME"
    # Its own uv, whatever the permissions of the runner's tool cache.
    sudo install -d -o "$CANDIDATE" -g "$CANDIDATE" "$CANDIDATE_HOME/bin"
    sudo install -o "$CANDIDATE" -g "$CANDIDATE" -m 0755 "$(command -v uv)" "$CANDIDATE_HOME/bin/uv"
    # The repository with its history (the corpus runs in a worktree of
    # HEAD) and input/: the request, the verified dataset, the fetch result.
    sudo cp -a "$GITHUB_WORKSPACE/." "$COPY"
    sudo rm -rf "$COPY/output"
    sudo chown -R "$CANDIDATE:$CANDIDATE" "$COPY"
    # Check the account as itself: no sudo, no group beyond its own, and no
    # write access to the workspace, the runner's command files or docker.
    if as_candidate sudo -n true 2> /dev/null; then
      echo "::error::$CANDIDATE can use sudo"
      exit 1
    fi
    if [ "$(as_candidate id -G)" != "$(as_candidate id -g)" ]; then
      echo "::error::$CANDIDATE has supplementary groups: $(as_candidate id -Gn)"
      exit 1
    fi
    for target in "$GITHUB_WORKSPACE" "$(dirname "$GITHUB_ENV")" "$GITHUB_ENV" /var/run/docker.sock; do
      if [ -e "$target" ] && as_candidate test -w "$target"; then
        echo "::error::$CANDIDATE can write $target"
        exit 1
      fi
    done
    echo "$CANDIDATE: no sudo, no supplementary groups, no write access to the runner's files"
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
    # The account streams its own output/ out (tar keeps links as links and
    # special files as special files, which the guard refuses); nothing runs
    # as root inside its home. The runner user unpacks it as itself.
    if as_candidate test -d "$COPY/output"; then
      mkdir output
      as_candidate tar -C "$COPY/output" -cf - . | tar -C output --no-same-owner --no-same-permissions -xf -
      # Kill anything the stream itself might have started.
      sudo pkill -KILL -u "$CANDIDATE" || true
    fi
    ;;
  *)
    echo "usage: uk_replay_sandbox.sh setup|run|collect" >&2
    exit 2
    ;;
esac
