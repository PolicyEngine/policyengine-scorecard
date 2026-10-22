#!/usr/bin/env bash
# Candidate code runs as an unprivileged account inside a systemd sandbox,
# never as the runner user.
#
# The runner user has passwordless sudo, owns this job's workspace and its
# command files ($GITHUB_ENV, $GITHUB_PATH), and owns the runner processes
# that hold the job's secrets and the Actions runtime token. Later steps run
# as that user and search its PATH, which on the hosted image includes
# world-writable directories under /opt. So a separate account is not
# enough: the candidate runs as a transient systemd service (systemd-run
# --uid) in which the whole filesystem is read-only except the account's
# home (ProtectSystem=strict), the runner's home is inaccessible, /tmp is
# private, setuid programs such as sudo cannot gain privileges, and other
# users' processes are invisible. /dev/shm and /dev/mqueue stay shared with
# the host (systemd binds them under PrivateDevices), so Python
# multiprocessing works; nothing later in the job runs from them. The
# account itself has no sudoers entry, no supplementary group (so no docker
# socket) and no cron or at jobs. `setup` checks all of this from inside the
# same sandbox and fails the job otherwise. When the service's main process
# ends, systemd kills everything left in it; `collect` then makes sure no
# process of the account survives, and only a copy of its output/, streamed
# out by the account, comes back to be checked by the runner's own guard.
#
# The real replay (uk-replay-determinism.yml) runs a certified variant's
# engine the same way. `install` builds the variant's environment in the
# copy, with the network and without the dataset. `replay` hands the dataset
# in and replays one measure-year offline: no network interface but
# loopback, and nothing under /run, where D-Bus, systemd-resolved and other
# host services listen, so nothing in the sandbox can send the dataset out
# over the network. Both print the variant's output with the runner's
# workflow commands stopped, so it can neither set a step output nor raise
# an annotation.
#
#   uk_replay_sandbox.sh setup     # after the dataset fetch, before any candidate code
#   uk_replay_sandbox.sh run       # the drain, in the sandbox
#   uk_replay_sandbox.sh install   # the real replay's environment, in the sandbox
#   uk_replay_sandbox.sh replay    # the real replay's measure-year, in the sandbox, offline
#   uk_replay_sandbox.sh collect   # make sure nothing survives, copy output/ back
set -euo pipefail
CANDIDATE=replay-candidate
CANDIDATE_HOME=/home/$CANDIDATE
COPY=$CANDIDATE_HOME/scorecard

# Run a command as the candidate in the sandbox, with an environment built
# from nothing but the arguments given before the command (VAR=value ...).
# A first argument --offline also leaves it no network but loopback and no
# /run. (${a[@]+"${a[@]}"} is an empty array under set -u in bash 3.2 too.)
in_sandbox() {
  local offline=() settings=()
  if [ "${1:-}" = --offline ]; then
    offline=(-p PrivateNetwork=yes -p InaccessiblePaths=-/run)
    shift
  fi
  while [ "$#" -gt 0 ] && [[ "$1" == *=* ]]; do
    settings+=(--setenv "$1")
    shift
  done
  sudo systemd-run --quiet --collect --pipe --wait \
    --uid="$CANDIDATE" --gid="$CANDIDATE" \
    --working-directory="$CANDIDATE_HOME" \
    --setenv HOME="$CANDIDATE_HOME" --setenv USER="$CANDIDATE" \
    --setenv LANG=C.UTF-8 \
    --setenv PATH="$CANDIDATE_HOME/bin:/usr/local/bin:/usr/bin:/bin" \
    ${settings[@]+"${settings[@]}"} \
    -p ProtectSystem=strict \
    -p ReadWritePaths="$CANDIDATE_HOME" \
    -p InaccessiblePaths=-/home/runner \
    -p PrivateTmp=yes \
    -p PrivateDevices=yes \
    -p NoNewPrivileges=yes \
    -p RestrictSUIDSGID=yes \
    -p ProtectProc=invisible \
    -p ProtectKernelTunables=yes \
    -p ProtectKernelModules=yes \
    -p ProtectKernelLogs=yes \
    -p ProtectClock=yes \
    -p ProtectControlGroups=yes \
    -p RestrictNamespaces=yes \
    -p LockPersonality=yes \
    -p CapabilityBoundingSet= \
    ${offline[@]+"${offline[@]}"} \
    "$@"
}

# The account, outside the sandbox, for streaming files in and out.
as_candidate() {
  sudo -n -u "$CANDIDATE" env -i HOME="$CANDIDATE_HOME" PATH=/usr/bin:/bin "$@"
}

# Make sure nothing of the account runs anywhere.
stop_candidate() {
  sudo pkill -KILL -u "$CANDIDATE" || true
  for _ in $(seq 30); do
    pgrep -u "$CANDIDATE" > /dev/null || break
    sleep 1
  done
  if pgrep -u "$CANDIDATE" > /dev/null; then
    echo "::error::$CANDIDATE processes survive"
    exit 1
  fi
}

# Run a command whose output the variant writes, with the runner's workflow
# commands stopped until a token the variant never sees.
untrusted_output() {
  local token status=0
  token=$(od -An -N16 -tx1 /dev/urandom | tr -d ' \n')
  echo "::stop-commands::$token"
  "$@" || status=$?
  printf '\n::%s::\n' "$token"
  return "$status"
}

case "${1:?usage: uk_replay_sandbox.sh setup|run|install|replay|collect}" in
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
    # Check, from inside the sandbox: no sudo, no group beyond its own, and
    # nothing writable that a later step as the runner user could read or
    # execute: every directory on the runner's PATH and its parents, the
    # tool cache, /opt, /usr, /etc, the workspace and command files, docker.
    if in_sandbox sudo -n true > /dev/null 2>&1; then
      echo "::error::$CANDIDATE can use sudo in the sandbox"
      exit 1
    fi
    groups=$(in_sandbox id -G)
    if [ "$groups" != "$(in_sandbox id -g)" ]; then
      echo "::error::$CANDIDATE has supplementary groups: $groups"
      exit 1
    fi
    targets=("$GITHUB_WORKSPACE" "$(dirname "$GITHUB_ENV")" "$GITHUB_ENV"
      /var/run/docker.sock /opt /usr /usr/share /usr/local /etc /home/runner
      "${RUNNER_TOOL_CACHE:-/opt/hostedtoolcache}")
    IFS=: read -r -a path_entries <<< "$PATH"
    for entry in "${path_entries[@]}"; do
      while [ -n "$entry" ] && [ "$entry" != / ]; do
        targets+=("$entry")
        entry=$(dirname "$entry")
      done
    done
    # shellcheck disable=SC2016 # expanded by the sandboxed shell
    writable=$(in_sandbox /bin/sh -c \
      'for t in "$@"; do if [ -e "$t" ] && [ -w "$t" ]; then echo "$t"; fi; done' \
      sh "${targets[@]}")
    if [ -n "$writable" ]; then
      echo "::error::$CANDIDATE can write, in the sandbox: $(echo "$writable" | sort -u | tr '\n' ' ')"
      exit 1
    fi
    # Offline, the network namespace's only interface is loopback, and /run
    # cannot be opened.
    interfaces=$(in_sandbox --offline /bin/sh -c 'tail -n +3 /proc/self/net/dev | cut -d: -f1 | tr -d " "')
    if [ "$interfaces" != lo ]; then
      echo "::error::$CANDIDATE has network interfaces offline: $(echo "$interfaces" | tr '\n' ' ')"
      exit 1
    fi
    if in_sandbox --offline ls /run > /dev/null 2>&1; then
      echo "::error::$CANDIDATE can open /run offline"
      exit 1
    fi
    echo "$CANDIDATE: no sudo, no supplementary groups, nothing writable outside its home (${#targets[@]} paths checked); offline, only loopback and no /run"
    ;;
  run)
    status=0
    # shellcheck disable=SC2016 # expanded by the sandboxed shell
    in_sandbox PYTHONPATH=. RUNNER_TEMP="$CANDIDATE_HOME/tmp" \
      REQUEST_ID="${REQUEST_ID:?}" REPLAY_RUNNER="${REPLAY_RUNNER:?}" \
      /bin/bash -c 'mkdir -p "$RUNNER_TEMP" && cd "$HOME/scorecard" && exec bash .github/scripts/uk_replay_drain.sh' \
      || status=$?
    # The drain records its own exit; the recorder handles a missing outcome.
    echo "candidate drain exited $status"
    ;;
  install)
    # shellcheck disable=SC2016 # expanded by the sandboxed shell
    untrusted_output in_sandbox REQUIREMENTS="${REQUIREMENTS:?}" \
      /bin/bash -c 'cd "$HOME/scorecard" && exec bash .github/scripts/uk_replay_determinism.sh install'
    ;;
  replay)
    : "${DATASET_FILE:?}" "${VARIANT:?}" "${REPLAY_EVENT:?}" "${REPLAY_MEASURE:?}" "${REPLAY_YEAR:?}"
    # The dataset enters a home in which nothing of the account runs, and
    # the account itself streams it in: nothing runs as root inside its home.
    stop_candidate
    as_candidate mkdir -p "$COPY/input"
    as_candidate dd of="$COPY/input/dataset.h5" bs=1M status=none < "$DATASET_FILE"
    # shellcheck disable=SC2016 # expanded by the sandboxed shell
    untrusted_output in_sandbox --offline PYTHONPATH=. RUNNER_TEMP="$CANDIDATE_HOME/tmp" \
      VARIANT="$VARIANT" REPLAY_EVENT="$REPLAY_EVENT" \
      REPLAY_MEASURE="$REPLAY_MEASURE" REPLAY_YEAR="$REPLAY_YEAR" \
      /bin/bash -c 'mkdir -p "$RUNNER_TEMP" && cd "$HOME/scorecard" && exec bash .github/scripts/uk_replay_determinism.sh replay'
    ;;
  collect)
    # systemd killed what was left in the service; make sure nothing of the
    # account runs anywhere.
    stop_candidate
    rm -rf output
    # The account streams its own output/ out (tar keeps links as links and
    # special files as special files, which the guard refuses); nothing runs
    # as root inside its home. The runner user unpacks it as itself.
    if as_candidate test -d "$COPY/output"; then
      mkdir output
      as_candidate tar -C "$COPY/output" -cf - . | tar -C output --no-same-owner --no-same-permissions -xf -
      sudo pkill -KILL -u "$CANDIDATE" || true
    fi
    ;;
  *)
    echo "usage: uk_replay_sandbox.sh setup|run|install|replay|collect" >&2
    exit 2
    ;;
esac
